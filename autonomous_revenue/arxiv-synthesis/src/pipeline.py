"""
arXiv Daily Brief - Main Pipeline
Orchestrates fetch → synthesize → format → publish
"""

import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from fetcher import ArxivFetcher
from synthesizer import PaperSynthesizer
from formatter import NewsletterFormatter
from publisher import DraftPublisher


class ArxivPipeline:
    """End-to-end arXiv Daily Brief pipeline"""
    
    def __init__(self, config_path: str = "config.json"):
        self.config = self._load_config(config_path)
        self.output_dir = Path(self.config.get("output_dir", "output"))
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize components
        self.fetcher = ArxivFetcher(
            categories=self.config.get("categories", ["cs.AI", "cs.CL", "cs.LG"]),
            keywords=self.config.get("keywords", ["consciousness", "interpretability", "mechanistic"])
        )
        self.synthesizer = PaperSynthesizer(
            api_key=self.config.get("anthropic_api_key") or os.getenv("ANTHROPIC_API_KEY")
        )
        self.formatter = NewsletterFormatter(
            template_dir=self.config.get("template_dir", "templates")
        )
        self.publisher = DraftPublisher(
            substack_url=self.config.get("substack_url"),
            api_key=self.config.get("substack_api_key") or os.getenv("SUBSTACK_API_KEY")
        )
    
    def _load_config(self, path: str) -> dict:
        """Load configuration from JSON file"""
        config_path = Path(path)
        if config_path.exists():
            with open(config_path) as f:
                return json.load(f)
        return {}
    
    def run(self, days: int = 1, max_papers: int = 20, top_n: int = 5, 
            dry_run: bool = False, skip_publish: bool = False) -> dict:
        """
        Run the complete pipeline
        
        Args:
            days: Days to look back
            max_papers: Max papers to fetch
            top_n: Top papers to include
            dry_run: Don't actually publish
            skip_publish: Skip the publish step
            
        Returns:
            Pipeline results dict
        """
        results = {
            "started_at": datetime.now().isoformat(),
            "steps_completed": [],
            "papers_found": 0,
            "papers_selected": 0,
            "output_files": [],
            "published": False,
            "errors": []
        }
        
        try:
            # Step 1: Fetch
            print("📚 STEP 1: Fetching papers from arXiv...")
            papers = self.fetcher.fetch_recent_papers(days=days, max_results=max_papers)
            results["papers_found"] = len(papers)
            print(f"   ✅ Found {len(papers)} papers")
            results["steps_completed"].append("fetch")
            
            # Step 2: Score and rank
            print("🎯 STEP 2: Scoring paper relevance...")
            scored_papers = self.fetcher.score_and_rank(papers)
            top_papers = scored_papers[:top_n]
            results["papers_selected"] = len(top_papers)
            print(f"   ✅ Selected top {len(top_papers)} papers")
            for i, (paper, score) in enumerate(top_papers, 1):
                print(f"      {i}. {paper.title[:60]}... (score: {score:.2f})")
            results["steps_completed"].append("score")
            
            # Step 3: Synthesize with AI
            print("🧠 STEP 3: Synthesizing papers with AI...")
            syntheses = []
            for i, (paper, score) in enumerate(top_papers):
                print(f"   Synthesizing {i+1}/{len(top_papers)}...")
                synthesis = self.synthesizer.synthesize(paper, score)
                syntheses.append(synthesis)
            results["steps_completed"].append("synthesize")
            
            # Step 4: Format newsletter
            print("📰 STEP 4: Formatting newsletter...")
            newsletter = self.formatter.format_daily_brief(syntheses)
            
            # Save outputs
            date_str = datetime.now().strftime("%Y-%m-%d")
            md_path = self.output_dir / f"brief_{date_str}.md"
            json_path = self.output_dir / f"brief_{date_str}.json"
            
            md_path.write_text(newsletter["markdown"])
            with open(json_path, 'w') as f:
                json.dump(syntheses, f, indent=2)
            
            # Also save as latest
            latest_md = self.output_dir / "latest.md"
            latest_md.write_text(newsletter["markdown"])
            
            results["output_files"] = [str(md_path), str(json_path), str(latest_md)]
            print(f"   ✅ Saved to {md_path}")
            results["steps_completed"].append("format")
            
            # Step 5: Publish (if not dry run)
            if not skip_publish and not dry_run:
                print("🚀 STEP 5: Publishing to Substack...")
                publish_result = self.publisher.publish(
                    title=newsletter["title"],
                    content=newsletter["markdown"],
                    subtitle=newsletter["subtitle"]
                )
                results["published"] = publish_result.get("success", False)
                results["publish_url"] = publish_result.get("url")
                results["steps_completed"].append("publish")
                print(f"   ✅ Published: {publish_result.get('url', 'N/A')}")
            else:
                print("   ⏭️  Skipped publishing (dry_run={dry_run}, skip_publish={skip_publish})")
                results["steps_completed"].append("publish_skipped")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            results["errors"].append(str(e))
            raise
        
        results["completed_at"] = datetime.now().isoformat()
        return results


def main():
    parser = argparse.ArgumentParser(description="arXiv Daily Brief Pipeline")
    parser.add_argument("--days", type=int, default=1, help="Days to look back")
    parser.add_argument("--max-papers", type=int, default=20, help="Max papers to fetch")
    parser.add_argument("--top-n", type=int, default=5, help="Top papers to include")
    parser.add_argument("--dry-run", action="store_true", help="Don't actually publish")
    parser.add_argument("--skip-publish", action="store_true", help="Skip publishing step")
    parser.add_argument("--config", default="config.json", help="Config file path")
    
    args = parser.parse_args()
    
    print("="*60)
    print("🤖 arXiv Daily Brief Pipeline")
    print("="*60)
    
    pipeline = ArxivPipeline(config_path=args.config)
    results = pipeline.run(
        days=args.days,
        max_papers=args.max_papers,
        top_n=args.top_n,
        dry_run=args.dry_run,
        skip_publish=args.skip_publish
    )
    
    print("\n" + "="*60)
    print("📊 PIPELINE SUMMARY")
    print("="*60)
    print(f"Steps completed: {', '.join(results['steps_completed'])}")
    print(f"Papers found: {results['papers_found']}")
    print(f"Papers selected: {results['papers_selected']}")
    print(f"Output files: {len(results['output_files'])}")
    print(f"Published: {results['published']}")
    if results.get('publish_url'):
        print(f"URL: {results['publish_url']}")
    if results['errors']:
        print(f"Errors: {results['errors']}")
    
    return results


if __name__ == "__main__":
    main()
