#!/usr/bin/env python3
"""
RLM Note Suggester - AI-Powered Connection Discovery

Suggests links and connections for notes using RLM synthesis.

Usage:
    python3 rlm_note_suggester.py --note "~/Vault/Note.md" --vault ~/Vault
    python3 rlm_note_suggester.py --unlinked-only --vault ~/Vault
    python3 rlm_note_suggester.py --interactive --vault ~/Vault
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Set

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "rlm-synthesis"))

try:
    from rlm_vault_query import VaultSynthesizer
except ImportError:
    print("⚠️  rlm_vault_query required. Ensure skills/rlm-synthesis is available.")
    sys.exit(1)


def find_unlinked_notes(vault_path: Path, min_links: int = 1) -> List[Path]:
    """Find notes with fewer than min_links outbound links."""
    import re
    
    synth = VaultSynthesizer(vault_path)
    all_notes = synth.scan_vault()
    
    unlinked = []
    for note in all_notes:
        content = note.read_text(errors='ignore')
        links = re.findall(r'\[\[([^\]]+)\]\]', content)
        if len(links) < min_links:
            unlinked.append((note, len(links)))
    
    return [n for n, _ in sorted(unlinked, key=lambda x: x[1])]


def interactive_mode(vault_path: Path):
    """Interactive connection suggestion mode."""
    synth = VaultSynthesizer(vault_path)
    
    print("🤖 RLM Note Suggester - Interactive Mode")
    print(f"📂 Vault: {vault_path}")
    print("\nCommands:")
    print("  suggest <note>  - Get connection suggestions for a note")
    print("  unlinked        - List notes with few connections")
    print("  orphans         - List notes with no backlinks")
    print("  quit            - Exit")
    print("-" * 60)
    
    while True:
        try:
            cmd = input("\n> ").strip()
            
            if cmd == "quit":
                break
            elif cmd == "unlinked":
                notes = find_unlinked_notes(vault_path, min_links=2)
                print(f"\n📝 Notes with < 2 outbound links:")
                for i, note in enumerate(notes[:20], 1):
                    print(f"  {i}. {note.name}")
                    
            elif cmd.startswith("suggest "):
                note_name = cmd[8:].strip()
                note_path = vault_path / note_name
                if not note_path.exists():
                    # Try to find it
                    matches = list(vault_path.glob(f"**/{note_name}*"))
                    if matches:
                        note_path = matches[0]
                    else:
                        print(f"❌ Note not found: {note_name}")
                        continue
                
                print(f"\n🔍 Analyzing {note_path.name}...")
                result = synth.suggest_connections(note_path)
                print("\n" + "="*60)
                print(result.response)
                
            else:
                print("Unknown command. Try: suggest, unlinked, orphans, quit")
                
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break


def batch_process(vault_path: Path, output: Path = None):
    """Batch process all unlinked notes."""
    synth = VaultSynthesizer(vault_path)
    unlinked = find_unlinked_notes(vault_path, min_links=1)
    
    print(f"🔍 Found {len(unlinked)} notes with few connections")
    
    suggestions = []
    for i, note in enumerate(unlinked[:10], 1):  # Limit to 10 for demo
        print(f"\n[{i}/10] Processing {note.name}...")
        result = synth.suggest_connections(note)
        suggestions.append({
            "note": str(note.relative_to(vault_path)),
            "suggestions": result.response,
        })
    
    if output:
        output.write_text(json.dumps(suggestions, indent=2))
        print(f"\n💾 Saved suggestions to {output}")
    else:
        print("\n" + "="*60)
        print("SUGGESTIONS:")
        print("="*60)
        for s in suggestions:
            print(f"\n📄 {s['note']}")
            print(s['suggestions'])


def main():
    parser = argparse.ArgumentParser(
        description="RLM Note Suggester - AI-Powered Connection Discovery"
    )
    parser.add_argument(
        "--vault", "-v",
        type=Path,
        required=True,
        help="Path to Obsidian vault"
    )
    parser.add_argument(
        "--note", "-n",
        type=Path,
        help="Specific note to analyze"
    )
    parser.add_argument(
        "--unlinked-only", "-u",
        action="store_true",
        help="Process only notes with few connections"
    )
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Interactive mode"
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        help="Output file for batch results (JSON)"
    )
    parser.add_argument(
        "--model", "-m",
        default="kimi-k2.5",
        help="Model to use"
    )
    
    args = parser.parse_args()
    
    if args.interactive:
        interactive_mode(args.vault)
    elif args.note:
        synth = VaultSynthesizer(args.vault)
        result = synth.suggest_connections(args.note, args.model)
        print(result.response)
    elif args.unlinked_only:
        batch_process(args.vault, args.output)
    else:
        print("Specify --note, --unlinked-only, or --interactive")


if __name__ == "__main__":
    main()
