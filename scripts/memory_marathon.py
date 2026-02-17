#!/usr/bin/env python3
"""
Autonomous memory hardening marathon runner.

Runs repeated audit/enforcement cycles for a fixed duration, writes machine logs,
and self-authors a prioritized TODO file from the latest evidence.

Example:
  python3 scripts/memory_marathon.py --duration-hours 8 --interval-minutes 15
  python3 scripts/memory_marathon.py --run-once --apply-hygiene
"""

from __future__ import annotations

import argparse
import json
import re
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Sequence

try:
    from memory_control_plane import LEGACY_ROOT_DEFAULTS, MemoryControlPlane
except ModuleNotFoundError:
    from scripts.memory_control_plane import LEGACY_ROOT_DEFAULTS, MemoryControlPlane


DEFAULT_QUERIES = [
    "Moltbook harvest memory tiering poisoning defense",
    "DGC payload spec trust gradient",
    "SAB hardening smoke test imports pytest",
    "PRATYABHIJNA R_V measurement scope correction",
    "agent identity schema modular registration",
    "bridge DGC scores reputation graph",
]


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def utc_now_iso() -> str:
    return utc_now().isoformat()


def clamp_score(value: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, value))


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def read_queries(args_queries: Sequence[str], queries_file: Path | None) -> List[str]:
    out: List[str] = []
    for q in args_queries:
        q = q.strip()
        if q:
            out.append(q)
    if queries_file and queries_file.exists():
        for raw in queries_file.read_text(encoding="utf-8").splitlines():
            q = raw.strip()
            if not q or q.startswith("#"):
                continue
            out.append(q)
    if not out:
        out = list(DEFAULT_QUERIES)
    dedup: List[str] = []
    seen: set[str] = set()
    for q in out:
        if q in seen:
            continue
        dedup.append(q)
        seen.add(q)
    return dedup


def run_query_benchmark(
    mcp: MemoryControlPlane,
    queries: Sequence[str],
    limit: int,
) -> Dict[str, Any]:
    def _relaxed_fts_query(raw: str) -> str:
        tokens = re.findall(r"[A-Za-z0-9_]+", raw.lower())
        keep: List[str] = []
        seen: set[str] = set()
        for tok in tokens:
            if len(tok) < 3:
                continue
            if tok in seen:
                continue
            seen.add(tok)
            keep.append(tok)
        if not keep:
            return raw
        return " OR ".join(keep[:8])

    rows: List[Dict[str, Any]] = []
    success = 0
    for q in queries:
        try:
            query_used = q
            result = mcp.search(query=query_used, source="all", limit=limit)
            hits = len(result.get("results", []))
            if hits == 0:
                relaxed = _relaxed_fts_query(q)
                if relaxed != query_used:
                    query_used = relaxed
                    result = mcp.search(query=query_used, source="all", limit=limit)
                    hits = len(result.get("results", []))
            if hits > 0:
                success += 1
            rows.append(
                {
                    "query": q,
                    "query_used": query_used,
                    "hits": hits,
                    "top_path": result["results"][0]["path"] if hits else None,
                    "top_source": result["results"][0]["source"] if hits else None,
                    "error": None,
                }
            )
        except Exception as exc:  # defensive: keep marathon running
            rows.append(
                {
                    "query": q,
                    "query_used": q,
                    "hits": 0,
                    "top_path": None,
                    "top_source": None,
                    "error": str(exc),
                }
            )
    total = len(queries)
    recall_rate = round((success / total), 3) if total else 0.0
    return {
        "queries_total": total,
        "queries_with_hits": success,
        "recall_rate": recall_rate,
        "rows": rows,
    }


def compute_metrics(audit: Dict[str, Any], benchmark: Dict[str, Any]) -> Dict[str, Any]:
    cfg = audit.get("memory_config", {})
    db_health = audit.get("db_health", {})
    memory_files = audit.get("memory_files", {})
    state_files = audit.get("state_files", {})
    legacy = audit.get("legacy_p9", {})

    sources = set(cfg.get("memory_sources", []))
    sources_ok = ("memory" in sources) and ("sessions" in sources)
    session_ok = bool(cfg.get("session_memory_enabled", False))
    vec_ok = db_health.get("vec_status") == "ok"

    stale_state_count = sum(
        1 for row in state_files.get("files", []) if row.get("exists") and row.get("stale")
    )
    old_memory_count = len(memory_files.get("older_than_retention", []))
    legacy_p9_count = len(legacy.get("databases", []))
    recall_rate = float(benchmark.get("recall_rate", 0.0))

    base = 35.0
    base += 20.0 if sources_ok else 0.0
    base += 10.0 if session_ok else 0.0
    base += 10.0 if vec_ok else 0.0
    base += 30.0 * recall_rate
    base -= 12.0 * stale_state_count
    base -= 15.0 * legacy_p9_count
    base -= 2.0 * old_memory_count
    health_score = round(clamp_score(base), 2)

    status = "excellent"
    if health_score < 85:
        status = "good"
    if health_score < 70:
        status = "degraded"
    if health_score < 50:
        status = "critical"

    return {
        "health_score": health_score,
        "status": status,
        "sources_ok": sources_ok,
        "session_memory_ok": session_ok,
        "vec_ok": vec_ok,
        "stale_state_count": stale_state_count,
        "old_memory_count": old_memory_count,
        "legacy_p9_count": legacy_p9_count,
        "recall_rate": recall_rate,
        "queries_with_hits": int(benchmark.get("queries_with_hits", 0)),
        "queries_total": int(benchmark.get("queries_total", 0)),
    }


def generate_todos(
    audit: Dict[str, Any],
    benchmark: Dict[str, Any],
    metrics: Dict[str, Any],
) -> List[Dict[str, Any]]:
    todos: List[Dict[str, Any]] = []

    def add(priority: str, title: str, reason: str, action: str) -> None:
        todos.append(
            {
                "priority": priority,
                "title": title,
                "reason": reason,
                "action": action,
                "generated_at": utc_now_iso(),
            }
        )

    if not metrics.get("sources_ok", False):
        add(
            "P0",
            "Fix memory sources to canonical pair",
            "Expected sources are memory+sessions for one retrieval surface.",
            "Set agents.defaults.memorySearch.sources to [\"memory\", \"sessions\"].",
        )

    if not metrics.get("session_memory_ok", False):
        add(
            "P0",
            "Enable session memory indexing",
            "Cross-session recall is reduced when session indexing is off.",
            "Set agents.defaults.memorySearch.experimental.sessionMemory=true.",
        )

    if not metrics.get("vec_ok", False):
        add(
            "P1",
            "Restore vector acceleration",
            "BM25-only fallback is active; semantic ranking quality is lower.",
            "Install/load sqlite vec extension and verify chunks_vec query succeeds.",
        )

    if metrics.get("legacy_p9_count", 0) > 0:
        add(
            "P0",
            "Quarantine legacy P9 indexes",
            "Multiple memory indexes create split-brain retrieval and stale context.",
            "Run memory_control_plane quarantine-p9 --apply for legacy roots.",
        )

    if metrics.get("stale_state_count", 0) > 0:
        add(
            "P0",
            "Archive stale state snapshots",
            "Stale handoff state files can poison context in new sessions.",
            "Run memory_control_plane archive-state --stale-days 2 --apply.",
        )

    if metrics.get("old_memory_count", 0) > 0:
        add(
            "P1",
            "Archive old daily memory files",
            "Active memory dir includes documents older than retention policy.",
            "Run memory_control_plane gc --retention-days 30 --apply.",
        )

    if metrics.get("recall_rate", 0.0) < 0.75:
        miss_queries = [
            row["query"]
            for row in benchmark.get("rows", [])
            if int(row.get("hits", 0)) == 0
        ]
        add(
            "P0",
            "Improve retrieval recall benchmark",
            f"Recall rate is {metrics.get('recall_rate', 0.0):.3f}, below 0.75 target.",
            "Curate missed topics into MEMORY.md and last-7-day memory notes. Misses: "
            + "; ".join(miss_queries[:4]),
        )

    add(
        "P2",
        "Weekly memory economics sweep",
        "Memory quality drifts without value-based pruning.",
        "Score entries by reuse signal and archive low-value noise weekly.",
    )
    add(
        "P2",
        "Context poisoning audit",
        "Unverified state artifacts can silently distort prompts.",
        "Add signed provenance tags for ingest sources and reject unsigned digests.",
    )

    if not todos:
        add(
            "P2",
            "Maintain baseline",
            "No immediate issues detected in this cycle.",
            "Keep audit cadence and monitor health score drift.",
        )
    return todos


def render_todo_markdown(
    workspace: Path,
    run_id: str,
    cycle_index: int,
    metrics: Dict[str, Any],
    todos: Sequence[Dict[str, Any]],
) -> str:
    grouped: Dict[str, List[Dict[str, Any]]] = {"P0": [], "P1": [], "P2": []}
    for item in todos:
        grouped.setdefault(item["priority"], []).append(item)

    lines = [
        "# Memory Marathon TODO",
        "",
        f"- Generated: {utc_now_iso()}",
        f"- Workspace: `{workspace}`",
        f"- Run ID: `{run_id}`",
        f"- Cycle: `{cycle_index}`",
        f"- Health score: `{metrics['health_score']}` ({metrics['status']})",
        f"- Recall rate: `{metrics['queries_with_hits']}/{metrics['queries_total']} = {metrics['recall_rate']}`",
        "",
        "## Priority Tasks",
        "",
    ]

    for p in ("P0", "P1", "P2"):
        items = grouped.get(p, [])
        lines.append(f"### {p}")
        if not items:
            lines.append("- [ ] No open tasks in this priority.")
            lines.append("")
            continue
        for item in items:
            lines.append(f"- [ ] {item['title']}")
            lines.append(f"  - Reason: {item['reason']}")
            lines.append(f"  - Action: {item['action']}")
        lines.append("")
    return "\n".join(lines) + "\n"


def render_status_markdown(
    workspace: Path,
    run_id: str,
    cycle_index: int,
    metrics: Dict[str, Any],
    benchmark: Dict[str, Any],
    recent_cycles: Sequence[Dict[str, Any]],
) -> str:
    lines = [
        "# Memory Marathon Status",
        "",
        f"- Updated: {utc_now_iso()}",
        f"- Workspace: `{workspace}`",
        f"- Run ID: `{run_id}`",
        f"- Cycle: `{cycle_index}`",
        "",
        "## Current Metrics",
        "",
        f"- Health score: `{metrics['health_score']}` ({metrics['status']})",
        f"- Sources OK: `{metrics['sources_ok']}`",
        f"- Session memory OK: `{metrics['session_memory_ok']}`",
        f"- Vector path OK: `{metrics['vec_ok']}`",
        f"- Recall: `{metrics['queries_with_hits']}/{metrics['queries_total']}` ({metrics['recall_rate']})",
        f"- Stale state files: `{metrics['stale_state_count']}`",
        f"- Legacy P9 DBs: `{metrics['legacy_p9_count']}`",
        "",
        "## Query Benchmark",
        "",
    ]
    for row in benchmark.get("rows", []):
        status = "ok" if int(row.get("hits", 0)) > 0 else "miss"
        path = row.get("top_path") or "-"
        lines.append(f"- `{status}` `{row['query']}` -> hits={row['hits']} top={path}")

    lines.extend(["", "## Cycle History (Recent)", ""])
    for row in recent_cycles[-10:]:
        lines.append(
            "- "
            + f"{row['timestamp']} cycle={row['cycle']} "
            + f"score={row['health_score']} status={row['status']} "
            + f"recall={row['recall_rate']}"
        )
    lines.append("")
    return "\n".join(lines)


def render_phase_plan_markdown(
    workspace: Path,
    run_id: str,
    cycle_index: int,
    metrics: Dict[str, Any],
    benchmark: Dict[str, Any],
) -> str:
    recall_rate = metrics.get("recall_rate", 0.0)
    vec_ok = metrics.get("vec_ok", False)
    stale_count = metrics.get("stale_state_count", 0)
    p9_count = metrics.get("legacy_p9_count", 0)

    phase_rows = [
        (
            "Hour 1",
            "Baseline lock",
            "Audit canonical memory health and verify one index is dominant.",
            f"Score >= 85 or clear P0 list published (current: {metrics['health_score']}).",
        ),
        (
            "Hour 2",
            "Retrieval hardening",
            "Run benchmark queries, tighten query set, and recover misses.",
            f"Recall >= 0.75 (current: {recall_rate}).",
        ),
        (
            "Hour 3",
            "Split-brain elimination",
            "Quarantine parallel indexes and stale state artifacts.",
            f"Legacy P9 count == 0 (current: {p9_count}), stale snapshots == 0 (current: {stale_count}).",
        ),
        (
            "Hour 4",
            "Memory economics pass",
            "Rank notes by reuse signal and archive low-value noise.",
            "Noise archive candidate list generated and reviewed.",
        ),
        (
            "Hour 5",
            "Poisoning defense pass",
            "Mark trusted sources, flag unsigned/low-trust context paths.",
            "Source trust rubric emitted with top risk list.",
        ),
        (
            "Hour 6",
            "Namespace boundaries",
            "Verify project isolation and avoid cross-workspace bleed.",
            "Per-workspace audit snapshots generated.",
        ),
        (
            "Hour 7",
            "Stress + drift checks",
            "Run repeated cycles and ensure metrics stay stable.",
            "No critical status over 3 consecutive cycles.",
        ),
        (
            "Hour 8",
            "Handoff package",
            "Emit final status, TODOs, and cycle log pointers.",
            "Final summary links complete and reproducible.",
        ),
    ]

    lines = [
        "# Memory Marathon 8-Hour Plan",
        "",
        f"- Generated: {utc_now_iso()}",
        f"- Workspace: `{workspace}`",
        f"- Run ID: `{run_id}`",
        f"- Current cycle: `{cycle_index}`",
        "",
        "## Runtime Signals",
        "",
        f"- Health score: `{metrics['health_score']}` ({metrics['status']})",
        f"- Recall rate: `{benchmark['queries_with_hits']}/{benchmark['queries_total']} = {recall_rate}`",
        f"- Vector path OK: `{vec_ok}`",
        f"- Legacy P9 count: `{p9_count}`",
        f"- Stale state count: `{stale_count}`",
        "",
        "## Phase Ladder",
        "",
    ]

    for label, theme, work, exit_criteria in phase_rows:
        lines.append(f"### {label}: {theme}")
        lines.append(f"- Work: {work}")
        lines.append(f"- Exit criteria: {exit_criteria}")
        lines.append("")

    lines.extend(
        [
            "## Operator Checkpoints",
            "",
            "- Every cycle emits: JSON log, status markdown, TODO markdown.",
            "- Investigate if health score drops by 10+ points between cycles.",
            "- Investigate if recall rate drops below 0.5 for two cycles.",
            "",
        ]
    )
    return "\n".join(lines)


@dataclass
class CycleResult:
    cycle_index: int
    timestamp: str
    health_score: float
    status: str
    recall_rate: float
    log_path: Path


class MemoryMarathonRunner:
    def __init__(
        self,
        mcp: MemoryControlPlane,
        workspace: Path,
        run_id: str,
        logs_dir: Path,
        todo_file: Path,
        status_file: Path,
        plan_file: Path,
        benchmark_queries: Sequence[str],
        legacy_roots: Sequence[Path],
        retention_days: int,
        stale_days: int,
        benchmark_limit: int,
        apply_hygiene: bool,
    ) -> None:
        self.mcp = mcp
        self.workspace = workspace
        self.run_id = run_id
        self.logs_dir = logs_dir
        self.todo_file = todo_file
        self.status_file = status_file
        self.plan_file = plan_file
        self.benchmark_queries = list(benchmark_queries)
        self.legacy_roots = list(legacy_roots)
        self.retention_days = retention_days
        self.stale_days = stale_days
        self.benchmark_limit = benchmark_limit
        self.apply_hygiene = apply_hygiene
        self.summary_jsonl = self.logs_dir / "summary.jsonl"
        ensure_dir(self.logs_dir)

    def _load_recent_cycle_summaries(self) -> List[Dict[str, Any]]:
        if not self.summary_jsonl.exists():
            return []
        out: List[Dict[str, Any]] = []
        for raw in self.summary_jsonl.read_text(encoding="utf-8").splitlines():
            raw = raw.strip()
            if not raw:
                continue
            try:
                out.append(json.loads(raw))
            except json.JSONDecodeError:
                continue
        return out

    def run_cycle(self, cycle_index: int) -> CycleResult:
        cycle_timestamp = utc_now_iso()

        audit = self.mcp.audit(
            retention_days=self.retention_days,
            stale_days=self.stale_days,
            legacy_roots=self.legacy_roots,
        )
        gc_out = self.mcp.gc_memory(retention_days=self.retention_days, apply=self.apply_hygiene)
        state_out = self.mcp.archive_state_files(stale_days=self.stale_days, apply=self.apply_hygiene)
        p9_out = self.mcp.quarantine_p9(apply=self.apply_hygiene, legacy_roots=self.legacy_roots)

        benchmark = run_query_benchmark(
            mcp=self.mcp,
            queries=self.benchmark_queries,
            limit=self.benchmark_limit,
        )
        metrics = compute_metrics(audit=audit, benchmark=benchmark)
        todos = generate_todos(audit=audit, benchmark=benchmark, metrics=metrics)

        payload = {
            "run_id": self.run_id,
            "cycle_index": cycle_index,
            "timestamp": cycle_timestamp,
            "apply_hygiene": self.apply_hygiene,
            "retention_days": self.retention_days,
            "stale_days": self.stale_days,
            "audit": audit,
            "gc": gc_out,
            "archive_state": state_out,
            "quarantine_p9": p9_out,
            "benchmark": benchmark,
            "metrics": metrics,
            "todos": todos,
        }

        stamp = utc_now().strftime("%Y%m%dT%H%M%SZ")
        log_path = self.logs_dir / f"cycle_{cycle_index:03d}_{stamp}.json"
        log_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

        summary_row = {
            "timestamp": cycle_timestamp,
            "cycle": cycle_index,
            "health_score": metrics["health_score"],
            "status": metrics["status"],
            "recall_rate": metrics["recall_rate"],
            "legacy_p9_count": metrics["legacy_p9_count"],
            "stale_state_count": metrics["stale_state_count"],
        }
        with self.summary_jsonl.open("a", encoding="utf-8") as f:
            f.write(json.dumps(summary_row) + "\n")

        recent = self._load_recent_cycle_summaries()
        self.todo_file.write_text(
            render_todo_markdown(
                workspace=self.workspace,
                run_id=self.run_id,
                cycle_index=cycle_index,
                metrics=metrics,
                todos=todos,
            ),
            encoding="utf-8",
        )
        self.status_file.write_text(
            render_status_markdown(
                workspace=self.workspace,
                run_id=self.run_id,
                cycle_index=cycle_index,
                metrics=metrics,
                benchmark=benchmark,
                recent_cycles=recent,
            ),
            encoding="utf-8",
        )
        self.plan_file.write_text(
            render_phase_plan_markdown(
                workspace=self.workspace,
                run_id=self.run_id,
                cycle_index=cycle_index,
                metrics=metrics,
                benchmark=benchmark,
            ),
            encoding="utf-8",
        )

        return CycleResult(
            cycle_index=cycle_index,
            timestamp=cycle_timestamp,
            health_score=metrics["health_score"],
            status=metrics["status"],
            recall_rate=metrics["recall_rate"],
            log_path=log_path,
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run an autonomous memory hardening marathon.")
    parser.add_argument("--openclaw-home", default="~/.openclaw")
    parser.add_argument("--workspace", default=None)
    parser.add_argument("--duration-hours", type=float, default=8.0)
    parser.add_argument("--interval-minutes", type=float, default=15.0)
    parser.add_argument("--retention-days", type=int, default=30)
    parser.add_argument("--stale-days", type=int, default=2)
    parser.add_argument("--benchmark-limit", type=int, default=5)
    parser.add_argument("--query", action="append", default=[])
    parser.add_argument("--queries-file", default=None)
    parser.add_argument("--legacy-root", action="append", default=[])
    parser.add_argument("--apply-hygiene", action="store_true")
    parser.add_argument("--run-once", action="store_true")
    parser.add_argument("--run-id", default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    openclaw_home = Path(args.openclaw_home).expanduser()
    workspace_override = Path(args.workspace).expanduser() if args.workspace else None
    queries_file = Path(args.queries_file).expanduser() if args.queries_file else None

    mcp = MemoryControlPlane.from_args(
        openclaw_home=openclaw_home,
        workspace_override=workspace_override,
    )
    workspace = mcp.workspace

    benchmark_queries = read_queries(args_queries=args.query, queries_file=queries_file)

    legacy_roots: List[Path] = [Path(p).expanduser() for p in args.legacy_root]
    for root_name in LEGACY_ROOT_DEFAULTS:
        legacy_roots.append(Path.home() / root_name)

    run_id = args.run_id or utc_now().strftime("mem-marathon-%Y%m%dT%H%M%SZ")
    logs_dir = workspace / "logs" / "memory_marathon" / run_id
    todo_file = workspace / "MEMORY_MARATHON_TODO.md"
    status_file = workspace / "MEMORY_MARATHON_STATUS.md"
    plan_file = workspace / "MEMORY_MARATHON_PLAN.md"

    runner = MemoryMarathonRunner(
        mcp=mcp,
        workspace=workspace,
        run_id=run_id,
        logs_dir=logs_dir,
        todo_file=todo_file,
        status_file=status_file,
        plan_file=plan_file,
        benchmark_queries=benchmark_queries,
        legacy_roots=legacy_roots,
        retention_days=args.retention_days,
        stale_days=args.stale_days,
        benchmark_limit=args.benchmark_limit,
        apply_hygiene=args.apply_hygiene,
    )

    start = utc_now()
    deadline = start + timedelta(hours=float(args.duration_hours))
    cycle_index = 1

    while True:
        cycle_start = utc_now()
        result = runner.run_cycle(cycle_index=cycle_index)
        print(
            json.dumps(
                {
                    "run_id": run_id,
                    "cycle": result.cycle_index,
                    "timestamp": result.timestamp,
                    "health_score": result.health_score,
                    "status": result.status,
                    "recall_rate": result.recall_rate,
                    "log_path": str(result.log_path),
                }
            ),
            flush=True,
        )

        if args.run_once:
            break
        if utc_now() >= deadline:
            break

        cycle_index += 1
        next_wakeup = cycle_start + timedelta(minutes=float(args.interval_minutes))
        sleep_seconds = max(0.0, (next_wakeup - utc_now()).total_seconds())
        time.sleep(sleep_seconds)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
