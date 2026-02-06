#!/usr/bin/env python3
"""
RLM Synthesis - OpenClaw Integration

Wraps the RLM (Recursive Language Models) framework for use with OpenClaw.
Provides infinite context processing via recursive decomposition.
"""

import os
import json
import glob
import time
from pathlib import Path
from typing import Optional, List, Union
from dataclasses import dataclass

# Model configuration - matches OpenClaw hierarchy
MODEL_CONFIG = {
    "kimi-k2.5": {
        "backend": "openrouter",
        "model_name": "moonshotai/kimi-k2.5",
        "context_window": 256000,
        "description": "Primary - fast, 256K context, multimodal"
    },
    "opus": {
        "backend": "openrouter",
        "model_name": "anthropic/claude-opus-4-5",
        "context_window": 200000,
        "description": "Heavy reasoning - expensive but powerful"
    },
    "gemini": {
        "backend": "openrouter",
        "model_name": "google/gemini-3-flash",
        "context_window": 1000000,
        "description": "Fallback - 1M context, fast"
    },
    "codex": {
        "backend": "openrouter",
        "model_name": "openai/gpt-5.2-codex",
        "context_window": 400000,
        "description": "Code-focused - agentic coding"
    },
    "deepseek": {
        "backend": "openrouter",
        "model_name": "deepseek/deepseek-chat",
        "context_window": 128000,
        "description": "Budget - great value, strong reasoning"
    }
}


@dataclass
class RLMResult:
    """Result from RLM query"""
    response: str
    elapsed_seconds: float
    tokens_used: Optional[int] = None
    iterations: Optional[int] = None
    model: str = ""
    files_processed: int = 0


class RLMSynthesis:
    """
    RLM Synthesis wrapper for OpenClaw.
    
    Example:
        rlm = RLMSynthesis()
        result = rlm.query(
            files=["*.md"],
            question="What is the architecture?",
            model="kimi-k2.5"
        )
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize with API key from env or OpenClaw config."""
        self.api_key = api_key or self._load_api_key()
        self._rlm = None
        
    def _load_api_key(self) -> str:
        """Load API key from environment or OpenClaw config."""
        key = os.getenv("OPENROUTER_API_KEY")
        if key:
            return key
            
        config_path = Path.home() / ".openclaw" / "openclaw.json"
        if config_path.exists():
            config = json.loads(config_path.read_text())
            key = config.get("env", {}).get("OPENROUTER_API_KEY")
            if key:
                os.environ["OPENROUTER_API_KEY"] = key
                return key
                
        raise ValueError("No OPENROUTER_API_KEY found in env or .openclaw/openclaw.json")
    
    def _get_rlm(self, model: str = "kimi-k2.5"):
        """Get or create RLM instance for the specified model."""
        from rlm import RLM
        
        model_cfg = MODEL_CONFIG.get(model, MODEL_CONFIG["kimi-k2.5"])
        
        return RLM(
            backend="openrouter",
            backend_kwargs={
                "model_name": model_cfg["model_name"],
                "api_key": self.api_key,
            },
            verbose=True,
            max_iterations=20,
            max_depth=2,
        )
    
    def load_files(
        self, 
        patterns: Union[str, List[str]], 
        base_path: Optional[str] = None,
        max_chars: int = 2_000_000
    ) -> str:
        """
        Load files matching patterns into a single corpus.
        
        Args:
            patterns: Glob pattern(s) like "*.md" or ["src/*.py", "docs/*.md"]
            base_path: Base directory for patterns (default: cwd)
            max_chars: Maximum total characters to load
            
        Returns:
            Combined corpus string with file headers
        """
        if isinstance(patterns, str):
            patterns = [patterns]
            
        base = Path(base_path) if base_path else Path.cwd()
        
        corpus_parts = []
        total_chars = 0
        files_loaded = 0
        
        for pattern in patterns:
            for fpath in base.glob(pattern):
                if total_chars >= max_chars:
                    break
                if fpath.is_file():
                    try:
                        text = fpath.read_text(errors='ignore')
                        # Truncate individual large files
                        if len(text) > 100_000:
                            text = text[:100_000] + "\n\n[... TRUNCATED ...]"
                        
                        header = f"\n\n{'='*80}\n=== FILE: {fpath.relative_to(base)} ===\n{'='*80}\n"
                        corpus_parts.append(header + text)
                        total_chars += len(text)
                        files_loaded += 1
                    except Exception as e:
                        continue
        
        self._files_loaded = files_loaded
        return "\n".join(corpus_parts)
    
    def query(
        self,
        question: str,
        files: Optional[Union[str, List[str]]] = None,
        corpus: Optional[str] = None,
        base_path: Optional[str] = None,
        model: str = "kimi-k2.5",
        max_chars: int = 2_000_000,
    ) -> RLMResult:
        """
        Query RLM with a question over files or corpus.
        
        Args:
            question: The question/task to perform
            files: Glob pattern(s) for files to load
            corpus: Pre-loaded corpus string (alternative to files)
            base_path: Base directory for file patterns
            model: Model to use ("kimi-k2.5", "opus", "gemini", "codex", "deepseek")
            max_chars: Maximum corpus size
            
        Returns:
            RLMResult with response and metadata
        """
        # Load corpus if files provided
        if files and not corpus:
            corpus = self.load_files(files, base_path, max_chars)
            print(f"📚 Loaded {self._files_loaded} files, {len(corpus):,} characters")
        elif not corpus:
            raise ValueError("Must provide either 'files' or 'corpus'")
        
        # Initialize RLM with selected model
        rlm = self._get_rlm(model)
        
        print(f"🧠 Using model: {MODEL_CONFIG[model]['description']}")
        print(f"🎯 Question: {question[:100]}...")
        
        start_time = time.time()
        
        try:
            result = rlm.completion(
                prompt=corpus,
                root_prompt=question,
            )
            
            elapsed = time.time() - start_time
            response = result.response if hasattr(result, 'response') else str(result)
            
            return RLMResult(
                response=response,
                elapsed_seconds=elapsed,
                tokens_used=getattr(result, 'total_tokens', None),
                iterations=getattr(result, 'num_iterations', None),
                model=model,
                files_processed=getattr(self, '_files_loaded', 0),
            )
            
        except Exception as e:
            return RLMResult(
                response=f"Error: {str(e)}",
                elapsed_seconds=time.time() - start_time,
                model=model,
            )
    
    def synthesize_research(self, question: str, model: str = "kimi-k2.5") -> RLMResult:
        """
        Convenience method to synthesize across Dhyana's research system.
        Loads CLAUDE.md files, mech-interp, DHARMIC_GODEL_CLAW, and vault.
        """
        home = Path.home()
        
        patterns = [
            (home, "CLAUDE*.md"),
            (home / "DHARMIC_GODEL_CLAW", "*.md"),
            (home / "mech-interp-latent-lab-phase1", "*.md"),
            (home / "Persistent-Semantic-Memory-Vault", "*.md"),
        ]
        
        corpus_parts = []
        total_files = 0
        
        for base, pattern in patterns:
            if base.exists():
                for f in base.glob(pattern):
                    if f.is_file():
                        try:
                            text = f.read_text()[:50000]  # Cap per file
                            corpus_parts.append(f"\n=== {f.name} ===\n{text}")
                            total_files += 1
                            if total_files >= 50:  # Cap total files
                                break
                        except:
                            continue
        
        corpus = "\n".join(corpus_parts)
        self._files_loaded = total_files
        
        return self.query(question=question, corpus=corpus, model=model)


# CLI interface
def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="RLM Synthesis for OpenClaw")
    parser.add_argument("question", help="Question or task to perform")
    parser.add_argument("--files", "-f", nargs="+", help="File patterns to load")
    parser.add_argument("--path", "-p", help="Base path for files")
    parser.add_argument("--model", "-m", default="kimi-k2.5", 
                       choices=list(MODEL_CONFIG.keys()),
                       help="Model to use")
    parser.add_argument("--research", "-r", action="store_true",
                       help="Load Dhyana's full research system")
    
    args = parser.parse_args()
    
    rlm = RLMSynthesis()
    
    if args.research:
        result = rlm.synthesize_research(args.question, args.model)
    else:
        result = rlm.query(
            question=args.question,
            files=args.files,
            base_path=args.path,
            model=args.model,
        )
    
    print("\n" + "="*80)
    print(f"✅ Completed in {result.elapsed_seconds:.1f}s using {result.model}")
    print("="*80)
    print(result.response)


if __name__ == "__main__":
    main()
