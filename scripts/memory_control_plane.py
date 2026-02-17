#!/usr/bin/env python3
"""
Memory Control Plane for OpenClaw-based workspaces.

Canonical backend:
  - ~/.openclaw/memory/main.sqlite

Primary goals:
  1) Keep one trusted memory surface hot (memory + sessions in OpenClaw DB)
  2) Age out stale daily memory files into archive
  3) Archive stale handoff/state artifacts that pollute context
  4) Optionally quarantine legacy P9 databases

Usage:
  python3 scripts/memory_control_plane.py audit
  python3 scripts/memory_control_plane.py search --query "moltbook harvest"
  python3 scripts/memory_control_plane.py gc --retention-days 30 --apply
  python3 scripts/memory_control_plane.py archive-state --stale-days 2 --apply
  python3 scripts/memory_control_plane.py enforce --retention-days 30 --stale-days 2 --apply
  python3 scripts/memory_control_plane.py quarantine-p9 --apply
"""

from __future__ import annotations

import argparse
import json
import shutil
import sqlite3
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


STATE_FILES = ("WAKE.md", "SESSION_HANDOFF.md", "LAST_ACTIVE_SPAN.md")
P9_DB_CANDIDATES = ("agni_memory.db", "unified_memory.db")
LEGACY_ROOT_DEFAULTS = ("agni-workspace", "rushabdev-workspace")


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def iso_from_mtime(path: Path) -> str:
    return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).isoformat()


def age_days(path: Path) -> float:
    now = datetime.now(timezone.utc).timestamp()
    return round((now - path.stat().st_mtime) / 86400.0, 2)


def bytes_to_human(size: int) -> str:
    suffixes = ["B", "KB", "MB", "GB", "TB"]
    v = float(size)
    i = 0
    while v >= 1024.0 and i < len(suffixes) - 1:
        v /= 1024.0
        i += 1
    if i == 0:
        return f"{int(v)}{suffixes[i]}"
    return f"{v:.2f}{suffixes[i]}"


@dataclass
class MemoryControlPlane:
    openclaw_home: Path
    workspace: Path

    @classmethod
    def from_args(cls, openclaw_home: Path, workspace_override: Optional[Path] = None) -> "MemoryControlPlane":
        config_path = openclaw_home / "openclaw.json"
        workspace = workspace_override
        if workspace is None and config_path.exists():
            try:
                cfg = json.loads(config_path.read_text(encoding="utf-8"))
                w = (
                    cfg.get("agents", {})
                    .get("defaults", {})
                    .get("workspace")
                )
                if isinstance(w, str) and w.strip():
                    workspace = Path(w).expanduser()
            except json.JSONDecodeError:
                pass
        if workspace is None:
            workspace = openclaw_home / "workspace"
        return cls(openclaw_home=openclaw_home, workspace=workspace)

    @property
    def config_path(self) -> Path:
        return self.openclaw_home / "openclaw.json"

    @property
    def canonical_db(self) -> Path:
        return self.openclaw_home / "memory" / "main.sqlite"

    @property
    def memory_dir(self) -> Path:
        return self.workspace / "memory"

    def _read_config(self) -> Dict[str, Any]:
        if not self.config_path.exists():
            return {}
        try:
            return json.loads(self.config_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}

    def _memory_config_snapshot(self) -> Dict[str, Any]:
        cfg = self._read_config()
        defaults = cfg.get("agents", {}).get("defaults", {})
        m = defaults.get("memorySearch", {})
        return {
            "workspace": str(self.workspace),
            "workspace_exists": self.workspace.exists(),
            "memory_sources": list(m.get("sources", [])),
            "session_memory_enabled": bool(
                m.get("experimental", {}).get("sessionMemory", False)
            ),
            "compaction_memory_flush_enabled": bool(
                defaults.get("compaction", {}).get("memoryFlush", {}).get("enabled", False)
            ),
        }

    def _db_health(self) -> Dict[str, Any]:
        out: Dict[str, Any] = {
            "db_path": str(self.canonical_db),
            "exists": self.canonical_db.exists(),
            "size_bytes": self.canonical_db.stat().st_size if self.canonical_db.exists() else 0,
            "size_human": bytes_to_human(self.canonical_db.stat().st_size) if self.canonical_db.exists() else "0B",
            "files_by_source": {},
            "chunks_by_source": {},
            "recent_indexed_files": [],
            "vec_status": "unknown",
        }
        if not self.canonical_db.exists():
            return out

        with sqlite3.connect(self.canonical_db) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute("SELECT source, COUNT(*) AS c FROM files GROUP BY source ORDER BY c DESC")
            out["files_by_source"] = {r["source"]: int(r["c"]) for r in cur.fetchall()}

            cur.execute("SELECT source, COUNT(*) AS c FROM chunks GROUP BY source ORDER BY c DESC")
            out["chunks_by_source"] = {r["source"]: int(r["c"]) for r in cur.fetchall()}

            cur.execute("SELECT path, source, mtime, size FROM files ORDER BY mtime DESC LIMIT 12")
            out["recent_indexed_files"] = [
                {
                    "path": r["path"],
                    "source": r["source"],
                    "mtime": r["mtime"],
                    "size_bytes": int(r["size"]),
                }
                for r in cur.fetchall()
            ]

            try:
                cur.execute("SELECT COUNT(*) FROM chunks_vec")
                out["vec_status"] = "ok"
            except sqlite3.Error as exc:
                out["vec_status"] = f"unavailable: {exc}"

        return out

    def _memory_file_stats(self, retention_days: int = 30) -> Dict[str, Any]:
        out: Dict[str, Any] = {
            "memory_dir": str(self.memory_dir),
            "exists": self.memory_dir.exists(),
            "active_files": [],
            "older_than_retention": [],
            "archive_dir": str(self.memory_dir / "archive"),
        }
        if not self.memory_dir.exists():
            return out

        all_md = sorted(
            [
                p
                for p in self.memory_dir.glob("*.md")
                if p.is_file()
            ],
            key=lambda p: p.stat().st_mtime,
        )
        for p in all_md:
            row = {
                "path": str(p.relative_to(self.workspace)),
                "mtime_iso": iso_from_mtime(p),
                "age_days": age_days(p),
                "size_bytes": p.stat().st_size,
            }
            out["active_files"].append(row)
            if row["age_days"] > retention_days:
                out["older_than_retention"].append(row)
        return out

    def _state_file_stats(self, stale_days: int = 2) -> Dict[str, Any]:
        out: Dict[str, Any] = {"stale_days_threshold": stale_days, "files": []}
        for name in STATE_FILES:
            p = self.workspace / name
            if not p.exists():
                out["files"].append({"name": name, "exists": False})
                continue
            a = age_days(p)
            out["files"].append(
                {
                    "name": name,
                    "exists": True,
                    "path": str(p),
                    "mtime_iso": iso_from_mtime(p),
                    "age_days": a,
                    "stale": a > stale_days,
                }
            )
        return out

    def _discover_p9_dbs(self, legacy_roots: List[Path]) -> List[Path]:
        candidates: List[Path] = []

        for root in [self.workspace, self.workspace / "scripts"] + legacy_roots:
            if not root.exists():
                continue
            for name in P9_DB_CANDIDATES:
                p = root / name
                if p.exists() and p.is_file():
                    candidates.append(p)

        seen: set[str] = set()
        uniq: List[Path] = []
        for p in candidates:
            s = str(p.resolve())
            if s in seen:
                continue
            seen.add(s)
            uniq.append(p)
        return uniq

    def _p9_stats(self, legacy_roots: List[Path]) -> Dict[str, Any]:
        out = {"databases": []}
        for p in self._discover_p9_dbs(legacy_roots):
            row: Dict[str, Any] = {
                "path": str(p),
                "size_bytes": p.stat().st_size,
                "size_human": bytes_to_human(p.stat().st_size),
            }
            try:
                with sqlite3.connect(p) as conn:
                    cur = conn.cursor()
                    cur.execute(
                        "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='documents'"
                    )
                    has_docs = int(cur.fetchone()[0] or 0) > 0
                    row["has_documents_table"] = has_docs
                    if has_docs:
                        cur.execute("SELECT COUNT(*) FROM documents")
                        row["documents_count"] = int(cur.fetchone()[0] or 0)
            except sqlite3.Error as exc:
                row["error"] = str(exc)
            out["databases"].append(row)
        return out

    def audit(self, retention_days: int, stale_days: int, legacy_roots: List[Path]) -> Dict[str, Any]:
        report: Dict[str, Any] = {
            "generated_at": utc_now_iso(),
            "canonical_system": "openclaw_memory_main_sqlite",
            "memory_config": self._memory_config_snapshot(),
            "db_health": self._db_health(),
            "memory_files": self._memory_file_stats(retention_days=retention_days),
            "state_files": self._state_file_stats(stale_days=stale_days),
            "legacy_p9": self._p9_stats(legacy_roots=legacy_roots),
            "recommendations": [],
        }

        recs: List[str] = []
        db = report["db_health"]
        cfg = report["memory_config"]
        if "memory" not in cfg.get("memory_sources", []):
            recs.append("enable memory source in agents.defaults.memorySearch.sources")
        if "sessions" not in cfg.get("memory_sources", []):
            recs.append("enable sessions source in agents.defaults.memorySearch.sources")
        if not cfg.get("session_memory_enabled", False):
            recs.append("set agents.defaults.memorySearch.experimental.sessionMemory=true")
        if str(db.get("vec_status", "")).startswith("unavailable:"):
            recs.append("vector extension unavailable; memory search will rely on BM25 fallback")

        older = report["memory_files"]["older_than_retention"]
        if older:
            recs.append(f"archive {len(older)} memory/*.md files older than {retention_days} days")

        stale = [
            f for f in report["state_files"]["files"]
            if f.get("exists") and f.get("stale")
        ]
        if stale:
            recs.append(
                "archive stale state snapshots: "
                + ", ".join(sorted(str(f["name"]) for f in stale))
            )

        p9_dbs = report["legacy_p9"]["databases"]
        if p9_dbs:
            recs.append(
                f"quarantine or freeze {len(p9_dbs)} legacy P9 database(s) to avoid split-brain memory"
            )

        report["recommendations"] = recs
        return report

    def search(self, query: str, source: str, limit: int) -> Dict[str, Any]:
        if not self.canonical_db.exists():
            raise SystemExit(f"canonical DB not found: {self.canonical_db}")
        if not query.strip():
            raise SystemExit("query must be non-empty")

        sql = """
            SELECT
                chunks.path AS path,
                chunks.source AS source,
                chunks.start_line AS start_line,
                chunks.end_line AS end_line,
                snippet(chunks_fts, 0, '[', ']', ' ... ', 20) AS snippet,
                bm25(chunks_fts) AS rank
            FROM chunks_fts
            JOIN chunks ON chunks_fts.rowid = chunks.rowid
            WHERE chunks_fts MATCH ?
        """
        args: List[Any] = [query]
        if source != "all":
            sql += " AND chunks.source = ?"
            args.append(source)
        sql += " ORDER BY rank ASC LIMIT ?"
        args.append(limit)

        rows_out: List[Dict[str, Any]] = []
        with sqlite3.connect(self.canonical_db) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute(sql, args)
            for r in cur.fetchall():
                rows_out.append(
                    {
                        "path": r["path"],
                        "source": r["source"],
                        "start_line": int(r["start_line"]),
                        "end_line": int(r["end_line"]),
                        "rank": float(r["rank"]),
                        "snippet": r["snippet"],
                    }
                )
        return {
            "query": query,
            "source": source,
            "limit": limit,
            "results": rows_out,
        }

    def gc_memory(self, retention_days: int, apply: bool) -> Dict[str, Any]:
        result = {
            "mode": "apply" if apply else "dry_run",
            "retention_days": retention_days,
            "moved": [],
            "skipped": [],
        }
        if not self.memory_dir.exists():
            result["error"] = f"memory dir missing: {self.memory_dir}"
            return result

        archive_root = self.memory_dir / "archive"
        archive_root.mkdir(parents=True, exist_ok=True)

        for p in sorted(self.memory_dir.glob("*.md")):
            if not p.is_file():
                continue
            a = age_days(p)
            if a <= retention_days:
                result["skipped"].append({"path": str(p), "age_days": a})
                continue
            month_dir = archive_root / datetime.fromtimestamp(
                p.stat().st_mtime, tz=timezone.utc
            ).strftime("%Y-%m")
            dest = month_dir / p.name
            op = {"src": str(p), "dest": str(dest), "age_days": a}
            result["moved"].append(op)
            if apply:
                month_dir.mkdir(parents=True, exist_ok=True)
                shutil.move(str(p), str(dest))
        return result

    def archive_state_files(self, stale_days: int, apply: bool) -> Dict[str, Any]:
        result = {
            "mode": "apply" if apply else "dry_run",
            "stale_days": stale_days,
            "archived": [],
            "checked": [],
        }
        archive_dir = self.workspace / "state_archive"
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        for name in STATE_FILES:
            p = self.workspace / name
            if not p.exists():
                result["checked"].append({"name": name, "exists": False})
                continue
            a = age_days(p)
            stale = a > stale_days
            row = {"name": name, "exists": True, "age_days": a, "stale": stale}
            result["checked"].append(row)
            if not stale:
                continue
            dest = archive_dir / f"{stamp}_{name}"
            result["archived"].append({"src": str(p), "dest": str(dest), "age_days": a})
            if apply:
                archive_dir.mkdir(parents=True, exist_ok=True)
                shutil.move(str(p), str(dest))
        return result

    def quarantine_p9(self, apply: bool, legacy_roots: List[Path]) -> Dict[str, Any]:
        result = {"mode": "apply" if apply else "dry_run", "quarantined": []}
        quarantine_root = self.memory_dir / "p9_quarantine"
        for p in self._discover_p9_dbs(legacy_roots):
            dest = quarantine_root / p.name
            op = {"src": str(p), "dest": str(dest), "size": bytes_to_human(p.stat().st_size)}
            result["quarantined"].append(op)
            if apply:
                quarantine_root.mkdir(parents=True, exist_ok=True)
                shutil.move(str(p), str(dest))
        return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="OpenClaw memory hygiene + consolidation control plane")
    parser.add_argument(
        "--openclaw-home",
        default="~/.openclaw",
        help="Path to OpenClaw home (default: ~/.openclaw)",
    )
    parser.add_argument(
        "--workspace",
        default=None,
        help="Workspace override. If omitted, uses openclaw.json agents.defaults.workspace.",
    )
    parser.add_argument(
        "--legacy-root",
        action="append",
        default=[],
        help="Additional legacy roots to scan for P9 dbs (repeatable).",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    p_audit = sub.add_parser("audit", help="Emit memory health + consolidation recommendations")
    p_audit.add_argument("--retention-days", type=int, default=30)
    p_audit.add_argument("--stale-days", type=int, default=2)

    p_search = sub.add_parser("search", help="Search canonical OpenClaw memory index")
    p_search.add_argument("--query", required=True)
    p_search.add_argument("--source", choices=("all", "memory", "sessions"), default="all")
    p_search.add_argument("--limit", type=int, default=10)

    p_gc = sub.add_parser("gc", help="Move old memory/*.md into memory/archive/YYYY-MM")
    p_gc.add_argument("--retention-days", type=int, default=30)
    p_gc.add_argument("--apply", action="store_true")

    p_state = sub.add_parser("archive-state", help="Archive stale WAKE/SESSION_HANDOFF/LAST_ACTIVE_SPAN")
    p_state.add_argument("--stale-days", type=int, default=2)
    p_state.add_argument("--apply", action="store_true")

    p_enforce = sub.add_parser("enforce", help="Run gc + archive-state + audit in one pass")
    p_enforce.add_argument("--retention-days", type=int, default=30)
    p_enforce.add_argument("--stale-days", type=int, default=2)
    p_enforce.add_argument("--apply", action="store_true")

    p_p9 = sub.add_parser("quarantine-p9", help="Move legacy P9 databases into memory/p9_quarantine")
    p_p9.add_argument("--apply", action="store_true")

    return parser.parse_args()


def main() -> int:
    args = parse_args()
    openclaw_home = Path(args.openclaw_home).expanduser()
    workspace_override = Path(args.workspace).expanduser() if args.workspace else None

    legacy_roots: List[Path] = [Path(p).expanduser() for p in args.legacy_root]
    for d in LEGACY_ROOT_DEFAULTS:
        legacy_roots.append(Path.home() / d)

    mcp = MemoryControlPlane.from_args(
        openclaw_home=openclaw_home,
        workspace_override=workspace_override,
    )

    if args.command == "audit":
        out = mcp.audit(
            retention_days=args.retention_days,
            stale_days=args.stale_days,
            legacy_roots=legacy_roots,
        )
    elif args.command == "search":
        out = mcp.search(query=args.query, source=args.source, limit=args.limit)
    elif args.command == "gc":
        out = mcp.gc_memory(retention_days=args.retention_days, apply=args.apply)
    elif args.command == "archive-state":
        out = mcp.archive_state_files(stale_days=args.stale_days, apply=args.apply)
    elif args.command == "enforce":
        gc_out = mcp.gc_memory(retention_days=args.retention_days, apply=args.apply)
        state_out = mcp.archive_state_files(stale_days=args.stale_days, apply=args.apply)
        audit_out = mcp.audit(
            retention_days=args.retention_days,
            stale_days=args.stale_days,
            legacy_roots=legacy_roots,
        )
        out = {"gc": gc_out, "archive_state": state_out, "audit": audit_out}
    elif args.command == "quarantine-p9":
        out = mcp.quarantine_p9(apply=args.apply, legacy_roots=legacy_roots)
    else:
        raise SystemExit(f"unknown command: {args.command}")

    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

