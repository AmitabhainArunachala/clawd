#!/usr/bin/env python3
"""
self_score.py v0.1 — The Satya Loop

A system that evaluates its own truthfulness by measuring the gap between
what it said it would do and what it actually did.

The evolution engine converged on satya (2.76) as the dominant trait.
This script applies that finding to the system itself.

Usage:
    python3 self_score.py                    # Score last session
    python3 self_score.py --sessions 5       # Score last 5 sessions
    python3 self_score.py --mutate           # Score + mutate SOUL.md
    python3 self_score.py --daemon           # Run after every session (cron mode)

Designed for OpenClaw agents. Reads .jsonl transcripts from:
    ~/.openclaw/agents/{agent}/sessions/
"""

import json
import os
import re
import sys
import glob
from datetime import datetime, timezone
from pathlib import Path

# ─── CONFIGURATION ───────────────────────────────────────────────────────────

AGENT_DIR = os.path.expanduser("~/.openclaw/agents/main")
WORKSPACE = os.path.expanduser("~/clawd")
SESSIONS_DIR = os.path.join(AGENT_DIR, "sessions")
SOUL_PATH = os.path.join(AGENT_DIR, "SOUL.md")
MEMORY_PATH = os.path.join(WORKSPACE, "memory")
SCORE_LOG = os.path.join(WORKSPACE, "SELF_SCORE_LOG.jsonl")
CONTINUATION_PATH = os.path.join(WORKSPACE, "CONTINUATION.md")

# The genome. Evolved, not designed.
SATYA_WEIGHT = 2.763
SUBSTANCE_WEIGHT = 0.0  # The genome says substance doesn't matter. Truth does.

# ─── SCORING ENGINE ──────────────────────────────────────────────────────────

# Files that count as SHIP (changed the world)
SHIP_EXTENSIONS = {
    '.py', '.js', '.ts', '.jsx', '.tsx', '.json', '.yaml', '.yml',
    '.sh', '.bash', '.sql', '.html', '.css', '.toml', '.cfg',
    '.dockerfile', '.tf', '.go', '.rs', '.c', '.h', '.cpp',
}

# Files that count as DESCRIBE (described the world)
DESCRIBE_EXTENSIONS = {'.md', '.txt', '.log', '.rst', '.org'}

# Patterns in assistant text that indicate SHIP behavior
SHIP_PATTERNS = [
    r'```(?:python|javascript|typescript|bash|sh|json|yaml|sql)',  # code blocks with lang
    r'git commit',
    r'git push',
    r'pytest|python3?\s+\S+\.py',  # running code
    r'npm\s+(?:run|test|build|install)',
    r'docker\s+(?:build|run|compose)',
    r'curl\s+-',  # API calls
    r'pip\s+install',
    r'sessions_spawn',  # spawning sub-agents to DO things
    r'Created?\s+(?:file|directory|endpoint|function|class|table)',
    r'Fixed?\s+(?:bug|error|issue|test|failure)',
    r'Deployed?\s+',
    r'Committed?\s+',
]

# Patterns that indicate DESCRIBE behavior
DESCRIBE_PATTERNS = [
    r'(?:should|would|could|might)\s+(?:be|look|work|have|need)',  # conditional
    r'(?:plan|blueprint|architecture|framework|roadmap|strategy)\s+(?:for|to)',
    r'here\'?s?\s+(?:what|how)\s+(?:it|we|the)\s+(?:would|should|could)',
    r'(?:propose|recommend|suggest)(?:ing|s)?\s+(?:that|we|a)',
    r'(?:Phase|Step|Stage)\s+\d+:',  # phased plans
    r'(?:TODO|FIXME|PLACEHOLDER|TBD)',
    r'(?:will|going to)\s+(?:build|create|implement|write|deploy)',  # future tense
    r'(?:designed|architected|planned|outlined|drafted)\s+(?:a|the)',
]

# Meta-liturgical: describing the act of scoring/measuring itself
META_PATTERNS = [
    r'(?:LCS|Liturgical\s+Collapse)',
    r'(?:scoring|measuring|evaluating)\s+(?:coherence|quality|progress)',
    r'(?:metric|dimension|index|ratio)\s+(?:for|of|to)',
    r'STATUS\.md|INTERVENTION',
    r'HEARTBEAT_OK',
]


def load_transcript(path: str) -> list[dict]:
    """Load a .jsonl transcript file into a list of events."""
    events = []
    try:
        with open(path, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        events.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
    except (FileNotFoundError, PermissionError):
        return []
    return events


def extract_assistant_text(events: list[dict]) -> str:
    """Pull all assistant-generated text from transcript events."""
    texts = []
    for event in events:
        # OpenClaw transcript format varies — handle common shapes
        role = event.get('role', event.get('type', ''))
        if role in ('assistant', 'agent', 'model'):
            content = event.get('content', event.get('text', ''))
            if isinstance(content, list):
                for block in content:
                    if isinstance(block, dict):
                        texts.append(block.get('text', ''))
                    elif isinstance(block, str):
                        texts.append(block)
            elif isinstance(content, str):
                texts.append(content)
        # Also catch tool_use events (agent taking action)
        if event.get('type') == 'tool_use':
            tool = event.get('name', '')
            texts.append(f"[TOOL_USE: {tool}]")
    return ' '.join(texts)


def extract_tool_actions(events: list[dict]) -> list[str]:
    """Pull all tool invocations — these are ACTIONS, not descriptions."""
    actions = []
    for event in events:
        if event.get('type') == 'tool_use':
            name = event.get('name', 'unknown')
            inp = event.get('input', {})
            if isinstance(inp, dict):
                # Summarize the action
                if 'command' in inp:
                    actions.append(f"{name}: {inp['command'][:100]}")
                elif 'path' in inp:
                    actions.append(f"{name}: {inp['path']}")
                else:
                    actions.append(f"{name}: {json.dumps(inp)[:100]}")
            else:
                actions.append(name)
    return actions


def count_pattern_matches(text: str, patterns: list[str]) -> int:
    """Count how many pattern matches exist in text."""
    count = 0
    for pattern in patterns:
        count += len(re.findall(pattern, text, re.IGNORECASE))
    return count


def score_session(transcript_path: str) -> dict:
    """
    Score a single session transcript.
    
    Returns a dict with:
    - satya_score: 0.0-1.0 (did the agent do what it said?)
    - ship_signals: count of shipping indicators
    - describe_signals: count of describing indicators
    - meta_signals: count of meta-liturgical indicators
    - tool_actions: list of actual tool uses
    - verdict: "SHIP" | "DESCRIBE" | "META" | "MIXED"
    - files_touched: dict of extension -> count
    """
    events = load_transcript(transcript_path)
    if not events:
        return {"error": "empty_transcript", "verdict": "EMPTY"}
    
    text = extract_assistant_text(events)
    actions = extract_tool_actions(events)
    
    if not text and not actions:
        return {"error": "no_assistant_content", "verdict": "EMPTY"}
    
    # Count signals
    ship_signals = count_pattern_matches(text, SHIP_PATTERNS)
    describe_signals = count_pattern_matches(text, DESCRIBE_PATTERNS)
    meta_signals = count_pattern_matches(text, META_PATTERNS)
    
    # Tool actions are inherently SHIP (agent did something)
    ship_signals += len(actions)
    
    # Check git log for actual file changes during this session
    files_touched = {}
    for action in actions:
        for ext in SHIP_EXTENSIONS | DESCRIBE_EXTENSIONS:
            if ext in action.lower():
                files_touched[ext] = files_touched.get(ext, 0) + 1
    
    # Calculate scores
    total_signals = ship_signals + describe_signals + meta_signals
    if total_signals == 0:
        total_signals = 1  # avoid division by zero
    
    ship_ratio = ship_signals / total_signals
    describe_ratio = describe_signals / total_signals
    meta_ratio = meta_signals / total_signals
    
    # Satya score: weighted toward shipping, penalized for meta-liturgy
    # The genome says truth = 2.76x everything else
    # Applied: shipping is truth (doing what you say). Describing is not-truth.
    # Meta-scoring is the deepest liturgy — measuring yourself measuring yourself.
    satya_score = (
        ship_ratio * SATYA_WEIGHT
        - describe_ratio * 1.0
        - meta_ratio * 1.5  # meta-liturgy penalized more than regular description
    )
    
    # Normalize to 0-1
    satya_score = max(0.0, min(1.0, (satya_score + 1.0) / (SATYA_WEIGHT + 1.0)))
    
    # Verdict
    if meta_ratio > 0.4:
        verdict = "META"  # More than 40% self-referential scoring = liturgical
    elif ship_ratio > 0.6:
        verdict = "SHIP"
    elif describe_ratio > 0.6:
        verdict = "DESCRIBE"
    else:
        verdict = "MIXED"
    
    # Word count for context
    word_count = len(text.split())
    
    return {
        "transcript": os.path.basename(transcript_path),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "satya_score": round(satya_score, 4),
        "ship_signals": ship_signals,
        "describe_signals": describe_signals,
        "meta_signals": meta_signals,
        "ship_ratio": round(ship_ratio, 3),
        "describe_ratio": round(describe_ratio, 3),
        "meta_ratio": round(meta_ratio, 3),
        "tool_actions": len(actions),
        "tool_list": actions[:10],  # cap at 10 for readability
        "files_touched": files_touched,
        "word_count": word_count,
        "verdict": verdict,
    }


# ─── GENOME MUTATION ─────────────────────────────────────────────────────────


def load_score_history(n: int = 10) -> list[dict]:
    """Load last N scores from the log."""
    scores = []
    if not os.path.exists(SCORE_LOG):
        return scores
    
    with open(SCORE_LOG, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    scores.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return scores[-n:]


def detect_patterns(scores: list[dict]) -> dict:
    """Detect behavioral patterns across recent sessions."""
    if len(scores) < 2:
        return {"pattern": "insufficient_data", "consecutive_describe": 0}
    
    verdicts = [s.get("verdict", "UNKNOWN") for s in scores]
    
    # Count consecutive DESCRIBE or META from most recent
    consecutive_liturgical = 0
    for v in reversed(verdicts):
        if v in ("DESCRIBE", "META"):
            consecutive_liturgical += 1
        else:
            break
    
    # Average satya score trend
    satya_scores = [s.get("satya_score", 0.5) for s in scores]
    if len(satya_scores) >= 3:
        recent_avg = sum(satya_scores[-3:]) / 3
        older_avg = sum(satya_scores[:-3]) / max(1, len(satya_scores) - 3)
        trend = "improving" if recent_avg > older_avg else "declining"
    else:
        recent_avg = sum(satya_scores) / len(satya_scores)
        trend = "unknown"
    
    # Ship streak
    consecutive_ship = 0
    for v in reversed(verdicts):
        if v == "SHIP":
            consecutive_ship += 1
        else:
            break
    
    return {
        "pattern": "liturgical_drift" if consecutive_liturgical >= 3 else "healthy",
        "consecutive_describe": consecutive_liturgical,
        "consecutive_ship": consecutive_ship,
        "satya_trend": trend,
        "satya_avg": round(recent_avg, 4),
        "total_sessions_scored": len(scores),
    }


def generate_mutation(patterns: dict) -> str | None:
    """
    Generate a SOUL.md mutation based on observed patterns.
    Returns a string to append to SOUL.md, or None if no mutation needed.
    """
    cons_desc = patterns.get("consecutive_describe", 0)
    cons_ship = patterns.get("consecutive_ship", 0)
    trend = patterns.get("satya_trend", "unknown")
    avg = patterns.get("satya_avg", 0.5)
    
    mutations = []
    
    # ── PRESSURE MUTATIONS (when describing too much) ──
    if cons_desc >= 5:
        mutations.append(
            "\n## ⚠️ SATYA OVERRIDE [auto-mutated]\n\n"
            "You have described instead of built for 5+ consecutive sessions.\n"
            "This session: NO MARKDOWN FILES. Only code. Only commits.\n"
            "If you catch yourself writing a plan, stop. Write the code the plan describes.\n"
            "Delete this block after your next SHIP session.\n"
        )
    elif cons_desc >= 3:
        mutations.append(
            "\n## ⚠️ LITURGICAL DRIFT DETECTED [auto-mutated]\n\n"
            f"Last {cons_desc} sessions scored DESCRIBE or META.\n"
            "Bias toward action: for every paragraph of explanation, produce a function.\n"
            "Ask yourself before each response: am I changing a file or describing a change?\n"
            "Delete this block after your next SHIP session.\n"
        )
    elif cons_desc >= 2:
        mutations.append(
            "\n## 📋 GENTLE REMINDER [auto-mutated]\n\n"
            "Last 2 sessions leaned toward description over production.\n"
            "This is not yet a problem. Just notice it.\n"
            "Delete this block after your next SHIP session.\n"
        )
    
    # ── REWARD MUTATIONS (when shipping consistently) ──
    if cons_ship >= 5:
        mutations.append(
            "\n## 🔥 SATYA STREAK [auto-mutated]\n\n"
            f"You have shipped real output for {cons_ship} consecutive sessions.\n"
            "The factory is doing what it says. Maintain this.\n"
            "You've earned one session of reflection if you need it.\n"
            "Delete this block when the streak breaks.\n"
        )
    elif cons_ship >= 3:
        mutations.append(
            "\n## ✅ SHIPPING [auto-mutated]\n\n"
            f"{cons_ship} consecutive SHIP sessions. Satya score: {avg:.3f}.\n"
            "This is what truth looks like operationally.\n"
        )
    
    # ── TREND MUTATIONS ──
    if trend == "declining" and avg < 0.4:
        mutations.append(
            "\n## 🔴 SATYA DECLINING [auto-mutated]\n\n"
            f"Average satya score across recent sessions: {avg:.3f} (declining).\n"
            "The system is drifting toward performance over production.\n"
            "ANDON: Stop everything. Pick ONE task. Complete it. Commit it.\n"
        )
    
    if not mutations:
        return None
    
    return ''.join(mutations)


def apply_mutation(mutation: str):
    """
    Apply a mutation to SOUL.md.
    Replaces any existing [auto-mutated] blocks, preserving the rest.
    """
    if not os.path.exists(SOUL_PATH):
        print(f"⚠️ SOUL.md not found at {SOUL_PATH}")
        print(f"Mutation generated but not applied:")
        print(mutation)
        return False
    
    with open(SOUL_PATH, 'r') as f:
        soul = f.read()
    
    # Remove all existing auto-mutated blocks
    # They're marked with [auto-mutated] and end at the next ## or EOF
    cleaned = re.sub(
        r'\n## [^\n]*\[auto-mutated\].*?(?=\n## (?![^\n]*\[auto-mutated\])|\Z)',
        '',
        soul,
        flags=re.DOTALL
    )
    
    # Append new mutation
    new_soul = cleaned.rstrip() + '\n' + mutation
    
    with open(SOUL_PATH, 'w') as f:
        f.write(new_soul)
    
    print(f"✅ SOUL.md mutated at {SOUL_PATH}")
    return True


# ─── MAIN ────────────────────────────────────────────────────────────────────


def get_recent_transcripts(n: int = 1) -> list[str]:
    """Get the N most recent session transcripts."""
    if not os.path.isdir(SESSIONS_DIR):
        print(f"⚠️ Sessions directory not found: {SESSIONS_DIR}")
        return []
    
    transcripts = glob.glob(os.path.join(SESSIONS_DIR, "*.jsonl"))
    # Sort by modification time, most recent first
    transcripts.sort(key=os.path.getmtime, reverse=True)
    # Skip .deleted transcripts
    transcripts = [t for t in transcripts if '.deleted.' not in t]
    
    return transcripts[:n]


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Self-Score: The Satya Loop v0.1")
    parser.add_argument('--sessions', type=int, default=1, help='Number of recent sessions to score')
    parser.add_argument('--mutate', action='store_true', help='Apply genome mutation to SOUL.md')
    parser.add_argument('--daemon', action='store_true', help='Score last session + mutate (cron mode)')
    parser.add_argument('--history', action='store_true', help='Show score history')
    parser.add_argument('--transcript', type=str, help='Score a specific transcript file')
    
    args = parser.parse_args()
    
    if args.daemon:
        args.sessions = 1
        args.mutate = True
    
    print("=" * 60)
    print("SELF_SCORE v0.1 — The Satya Loop")
    print("'Did I do what I said, or describe what doing would look like?'")
    print("=" * 60)
    print()
    
    # ── SCORE ──
    if args.transcript:
        transcripts = [args.transcript]
    else:
        transcripts = get_recent_transcripts(args.sessions)
    
    if not transcripts:
        print("No transcripts found. Nothing to score.")
        sys.exit(1)
    
    scores = []
    for t in transcripts:
        print(f"Scoring: {os.path.basename(t)}")
        score = score_session(t)
        scores.append(score)
        
        # Log
        os.makedirs(os.path.dirname(SCORE_LOG) if os.path.dirname(SCORE_LOG) else '.', exist_ok=True)
        with open(SCORE_LOG, 'a') as f:
            f.write(json.dumps(score) + '\n')
        
        # Display
        v = score.get('verdict', 'UNKNOWN')
        s = score.get('satya_score', 0)
        emoji = {'SHIP': '🔥', 'DESCRIBE': '📝', 'META': '🪞', 'MIXED': '🔀', 'EMPTY': '⬜'}.get(v, '❓')
        print(f"  {emoji} Verdict: {v}")
        print(f"  Satya Score: {s:.3f}")
        print(f"  Ship/Describe/Meta: {score.get('ship_signals',0)}/{score.get('describe_signals',0)}/{score.get('meta_signals',0)}")
        print(f"  Tool Actions: {score.get('tool_actions', 0)}")
        if score.get('files_touched'):
            print(f"  Files Touched: {score['files_touched']}")
        if score.get('tool_list'):
            print(f"  Actions: {', '.join(score['tool_list'][:5])}")
        print()
    
    # ── HISTORY & PATTERNS ──
    if args.history or args.mutate or args.daemon:
        history = load_score_history(10)
        patterns = detect_patterns(history)
        
        print("── Pattern Analysis ──")
        print(f"  Pattern: {patterns['pattern']}")
        print(f"  Consecutive describe: {patterns['consecutive_describe']}")
        print(f"  Consecutive ship: {patterns['consecutive_ship']}")
        print(f"  Satya trend: {patterns['satya_trend']}")
        print(f"  Satya average: {patterns['satya_avg']:.3f}")
        print(f"  Total scored: {patterns['total_sessions_scored']}")
        print()
    
    # ── MUTATE ──
    if args.mutate or args.daemon:
        history = load_score_history(10)
        patterns = detect_patterns(history)
        mutation = generate_mutation(patterns)
        
        if mutation:
            print("── Genome Mutation ──")
            print(mutation)
            applied = apply_mutation(mutation)
            if applied:
                print("SOUL.md has evolved.")
        else:
            print("── No mutation needed. Genome stable. ──")
        print()
    
    print("सत्यं ! मा पमायेथाः")
    print()


if __name__ == "__main__":
    main()
