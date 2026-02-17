from __future__ import annotations

from pathlib import Path

from scripts.memory_marathon import compute_metrics, generate_todos, read_queries


def _sample_audit(
    *,
    memory_sources: list[str] | None = None,
    session_memory_enabled: bool = True,
    vec_ok: bool = True,
    stale_state_count: int = 0,
    old_memory_count: int = 0,
    legacy_p9_count: int = 0,
) -> dict:
    return {
        "memory_config": {
            "memory_sources": memory_sources if memory_sources is not None else ["memory", "sessions"],
            "session_memory_enabled": session_memory_enabled,
        },
        "db_health": {
            "vec_status": "ok" if vec_ok else "unavailable: no such module: vec0",
        },
        "memory_files": {
            "older_than_retention": [{"path": f"memory/old_{i}.md"} for i in range(old_memory_count)],
        },
        "state_files": {
            "files": (
                [{"exists": True, "stale": True, "name": f"stale_{i}.md"} for i in range(stale_state_count)]
                + [{"exists": False, "name": "WAKE.md"}]
            ),
        },
        "legacy_p9": {
            "databases": [{"path": f"/tmp/p9_{i}.db"} for i in range(legacy_p9_count)],
        },
    }


def _sample_benchmark(*, total: int, with_hits: int) -> dict:
    rows = []
    for i in range(total):
        hits = 1 if i < with_hits else 0
        rows.append(
            {
                "query": f"q{i}",
                "hits": hits,
                "top_path": "memory/test.md" if hits else None,
                "top_source": "memory" if hits else None,
                "error": None,
            }
        )
    recall_rate = (with_hits / total) if total else 0.0
    return {
        "queries_total": total,
        "queries_with_hits": with_hits,
        "recall_rate": round(recall_rate, 3),
        "rows": rows,
    }


def test_compute_metrics_healthy() -> None:
    audit = _sample_audit()
    benchmark = _sample_benchmark(total=4, with_hits=4)
    metrics = compute_metrics(audit=audit, benchmark=benchmark)

    assert metrics["status"] in {"good", "excellent"}
    assert metrics["health_score"] >= 90
    assert metrics["sources_ok"] is True
    assert metrics["session_memory_ok"] is True
    assert metrics["vec_ok"] is True
    assert metrics["legacy_p9_count"] == 0
    assert metrics["stale_state_count"] == 0


def test_compute_metrics_degraded_with_split_brain_and_stale_state() -> None:
    audit = _sample_audit(
        vec_ok=False,
        stale_state_count=2,
        legacy_p9_count=1,
        old_memory_count=3,
    )
    benchmark = _sample_benchmark(total=4, with_hits=1)
    metrics = compute_metrics(audit=audit, benchmark=benchmark)

    assert metrics["status"] in {"critical", "degraded", "good"}
    assert metrics["health_score"] < 80
    assert metrics["legacy_p9_count"] == 1
    assert metrics["stale_state_count"] == 2
    assert metrics["vec_ok"] is False
    assert metrics["recall_rate"] == 0.25


def test_generate_todos_prioritizes_recall_and_split_brain() -> None:
    audit = _sample_audit(vec_ok=False, stale_state_count=1, legacy_p9_count=1)
    benchmark = _sample_benchmark(total=3, with_hits=1)
    metrics = compute_metrics(audit=audit, benchmark=benchmark)
    todos = generate_todos(audit=audit, benchmark=benchmark, metrics=metrics)

    titles = {t["title"] for t in todos}
    assert "Quarantine legacy P9 indexes" in titles
    assert "Archive stale state snapshots" in titles
    assert "Improve retrieval recall benchmark" in titles
    assert "Restore vector acceleration" in titles

    p0_titles = {t["title"] for t in todos if t["priority"] == "P0"}
    assert "Quarantine legacy P9 indexes" in p0_titles
    assert "Archive stale state snapshots" in p0_titles


def test_read_queries_deduplicates_and_ignores_comments(tmp_path: Path) -> None:
    qfile = tmp_path / "queries.txt"
    qfile.write_text(
        "\n".join(
            [
                "# comment",
                "alpha query",
                "",
                "beta query",
                "alpha query",
            ]
        ),
        encoding="utf-8",
    )
    result = read_queries(args_queries=["beta query", "gamma query"], queries_file=qfile)
    assert result == ["beta query", "gamma query", "alpha query"]
