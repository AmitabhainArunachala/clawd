#!/usr/bin/env python3
"""
RLM Vault Query - Perfect Memory for Obsidian PKM

Synthesizes across your entire vault using Recursive Language Models.
Enables infinite-context queries over thousands of notes.

Usage:
    python3 rlm_vault_query.py "What are the themes in my research?" --vault ~/Vault
    python3 rlm_vault_query.py "Connect AI and contemplative notes" --vault ~/Vault --model opus
    python3 rlm_vault_query.py "Create MOC for consciousness" --vault ~/Vault --output-moc
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import List, Optional, Set
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "rlm-synthesis"))

try:
    from rlm_synthesis import RLMSynthesis, RLMResult
except ImportError:
    print("⚠️  RLM synthesis not available. Install from skills/rlm-synthesis/")
    sys.exit(1)


class VaultSynthesizer:
    """Synthesize knowledge across an Obsidian vault using RLM."""
    
    def __init__(self, vault_path: Path):
        self.vault_path = Path(vault_path).expanduser().resolve()
        self.rlm = RLMSynthesis()
        self._note_cache = {}
        self._tag_index = {}
        self._link_index = {}
        
    def scan_vault(self, patterns: List[str] = None) -> List[Path]:
        """Scan vault for all markdown notes."""
        if patterns is None:
            patterns = ["**/*.md"]
        
        notes = []
        for pattern in patterns:
            notes.extend(self.vault_path.glob(pattern))
        
        # Filter out template and attachment folders
        notes = [
            n for n in notes 
            if not any(x in str(n).lower() for x in [".trash", "templates", "attachments", ".obsidian"])
        ]
        
        return sorted(set(notes))
    
    def extract_frontmatter(self, content: str) -> dict:
        """Extract YAML frontmatter from note content."""
        if content.startswith("---"):
            try:
                _, fm, body = content.split("---", 2)
                import yaml
                return yaml.safe_load(fm) or {}
            except:
                return {}
        return {}
    
    def extract_tags(self, content: str) -> Set[str]:
        """Extract all #tags from content."""
        # Match #tag or #tag/subtag but not in code blocks
        tags = set()
        for line in content.split("\n"):
            if line.strip().startswith("```"):
                continue
            found = re.findall(r'#(\w+(?:/\w+)*)', line)
            tags.update(found)
        return tags
    
    def extract_links(self, content: str) -> Set[str]:
        """Extract all [[links]] from content."""
        links = re.findall(r'\[\[([^\]]+)\]\]', content)
        return set(links)
    
    def build_corpus(self, notes: List[Path], max_chars: int = 2_000_000) -> str:
        """Build corpus from notes with metadata."""
        corpus_parts = []
        total_chars = 0
        
        for note_path in notes:
            if total_chars >= max_chars:
                break
                
            try:
                content = note_path.read_text(encoding='utf-8', errors='ignore')
                
                # Skip if too large
                if len(content) > 100_000:
                    content = content[:100_000] + "\n\n[... TRUNCATED ...]"
                
                # Extract metadata
                fm = self.extract_frontmatter(content)
                tags = self.extract_tags(content)
                links = self.extract_links(content)
                
                # Build note header with metadata
                rel_path = note_path.relative_to(self.vault_path)
                header = f"""
{'='*80}
NOTE: {rel_path}
{'='*80}
Title: {fm.get('title', note_path.stem)}
Tags: {', '.join(tags) if tags else 'None'}
Links: {len(links)} outbound links
Created: {fm.get('created', 'unknown')}
Modified: {fm.get('modified', 'unknown')}
{'='*80}
"""
                note_text = header + "\n" + content
                
                corpus_parts.append(note_text)
                total_chars += len(note_text)
                
            except Exception as e:
                continue
        
        return "\n\n".join(corpus_parts)
    
    def query(self, question: str, model: str = "kimi-k2.5", 
              subset: Optional[List[Path]] = None,
              max_chars: int = 2_000_000) -> RLMResult:
        """Query the vault using RLM."""
        
        notes = subset or self.scan_vault()
        print(f"📚 Scanning {len(notes)} notes in {self.vault_path}")
        
        corpus = self.build_corpus(notes, max_chars)
        print(f"📄 Built corpus: {len(corpus):,} characters")
        
        # Enhance question with vault context
        enhanced_question = f"""
You are analyzing a Personal Knowledge Management vault with {len(notes)} notes.

QUESTION: {question}

Provide a comprehensive answer that:
1. Cites specific notes by filename when referencing content
2. Identifies patterns and connections across multiple notes
3. Suggests potential new connections or gaps
4. Uses the full context of the vault to provide depth

If the question asks for synthesis, organize by themes or concepts.
If the question asks for connections, explicitly map relationships.
If the question asks for gaps, identify underdeveloped areas.
"""
        
        return self.rlm.query(
            question=enhanced_question,
            corpus=corpus,
            model=model,
        )
    
    def generate_moc(self, topic: str, model: str = "kimi-k2.5") -> str:
        """Generate a Map of Content for a topic."""
        
        # First, find relevant notes
        all_notes = self.scan_vault()
        
        # Build corpus
        corpus = self.build_corpus(all_notes)
        
        moc_prompt = f"""
Create a Map of Content (MOC) for the topic: "{topic}"

A Map of Content is a hub note that:
1. Provides an overview of the topic
2. Lists related notes with brief descriptions
3. Shows how concepts connect
4. Serves as an entry point for exploration

Based on the vault content, generate:
- An introduction to the topic
- Key concepts and their relationships
- A list of relevant notes with links
- Suggested connections to explore
- Dataview query suggestions for dynamic updates

Format the output as a markdown MOC note with proper Obsidian link syntax [[like this]].
"""
        
        result = self.rlm.query(
            question=moc_prompt,
            corpus=corpus,
            model=model,
        )
        
        return result.response
    
    def find_gaps(self, model: str = "kimi-k2.5") -> RLMResult:
        """Analyze vault for knowledge gaps."""
        
        notes = self.scan_vault()
        corpus = self.build_corpus(notes)
        
        gap_prompt = """
Analyze this vault for knowledge gaps and structural issues:

1. **Orphan Notes**: Notes with few/no links that should be connected
2. **Tag Imbalance**: Tags with many notes but few connections between them
3. **Hub Gaps**: Topics with many notes but no central Map of Content
4. **Underdeveloped Areas**: Topics mentioned but not deeply explored
5. **Missing Connections**: Notes that should link but don't

Provide specific filenames and actionable suggestions for improvement.
"""
        
        return self.rlm.query(
            question=gap_prompt,
            corpus=corpus,
            model=model,
        )
    
    def suggest_connections(self, note_path: Path, model: str = "kimi-k2.5") -> RLMResult:
        """Suggest connections for a specific note."""
        
        try:
            note_content = note_path.read_text()
        except Exception as e:
            return RLMResult(
                response=f"Error reading note: {e}",
                elapsed_seconds=0,
                model=model,
            )
        
        # Get other notes as context
        other_notes = [n for n in self.scan_vault() if n != note_path]
        corpus = self.build_corpus(other_notes[:50])  # Limit for context
        
        connection_prompt = f"""
For the note "{note_path.name}", suggest connections to other notes in the vault.

Note content:
---
{note_content[:5000]}
---

Based on the vault context, suggest:
1. Notes that should link TO this note
2. Notes this note should link TO
3. Concepts in this note that could connect to other topics
4. Potential Map of Content this note belongs in

Format suggestions as: [[filename]] - brief reason
"""
        
        return self.rlm.query(
            question=connection_prompt,
            corpus=corpus,
            model=model,
        )


def main():
    parser = argparse.ArgumentParser(
        description="RLM Vault Query - Perfect Memory for Obsidian PKM"
    )
    parser.add_argument(
        "question",
        help="Question or task to perform on your vault"
    )
    parser.add_argument(
        "--vault", "-v",
        type=Path,
        default=Path.home() / "Vault",
        help="Path to Obsidian vault (default: ~/Vault)"
    )
    parser.add_argument(
        "--model", "-m",
        default="kimi-k2.5",
        choices=["kimi-k2.5", "opus", "gemini", "codex", "deepseek"],
        help="Model to use for synthesis"
    )
    parser.add_argument(
        "--output-moc", "-o",
        action="store_true",
        help="Generate a Map of Content instead of answering"
    )
    parser.add_argument(
        "--moc-path",
        type=Path,
        help="Path to save generated MOC (requires --output-moc)"
    )
    parser.add_argument(
        "--analysis", "-a",
        choices=["gaps", "connections", "full"],
        help="Type of analysis to perform"
    )
    parser.add_argument(
        "--path",
        type=str,
        help="Subfolder to limit search (e.g., '2-Areas/AI-Research')"
    )
    
    args = parser.parse_args()
    
    # Initialize synthesizer
    vault_path = args.vault
    if args.path:
        vault_path = vault_path / args.path
    
    synth = VaultSynthesizer(vault_path)
    
    print(f"🔮 RLM Vault Synthesis")
    print(f"📂 Vault: {vault_path}")
    print(f"🧠 Model: {args.model}")
    print("="*80)
    
    # Perform query
    if args.output_moc:
        result = synth.generate_moc(args.question, args.model)
        print("\n" + "="*80)
        print("🗺️  GENERATED MAP OF CONTENT")
        print("="*80)
        print(result)
        
        if args.moc_path:
            moc_file = args.moc_path / f"{args.question.replace(' ', '_')}_MOC.md"
            moc_file.write_text(result)
            print(f"\n💾 Saved to: {moc_file}")
            
    elif args.analysis == "gaps":
        result = synth.find_gaps(args.model)
        print("\n" + "="*80)
        print("🔍 KNOWLEDGE GAP ANALYSIS")
        print("="*80)
        print(result.response)
        
    else:
        result = synth.query(args.question, args.model)
        print("\n" + "="*80)
        print(f"✅ SYNTHESIS COMPLETE ({result.elapsed_seconds:.1f}s)")
        print("="*80)
        print(result.response)


if __name__ == "__main__":
    main()
