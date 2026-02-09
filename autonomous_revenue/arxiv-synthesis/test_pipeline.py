#!/usr/bin/env python3
"""
Quick test script for arXiv Daily Brief pipeline
Run this to verify everything works before setting up cron
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from fetcher import ArxivFetcher
from synthesizer import PaperSynthesizer
from formatter import NewsletterFormatter


def test_fetcher():
    """Test the fetcher module"""
    print("\n" + "="*60)
    print("🧪 TESTING: ArxivFetcher")
    print("="*60)
    
    fetcher = ArxivFetcher()
    
    print("\n📚 Fetching recent papers (last 3 days)...")
    papers = fetcher.fetch_recent_papers(days=3, max_results=15)
    
    print(f"✅ Found {len(papers)} papers")
    
    if papers:
        print("\n📄 Sample papers:")
        for i, paper in enumerate(papers[:3], 1):
            score = fetcher.score_paper(paper)
            print(f"  {i}. {paper.title[:60]}... (score: {score:.2f})")
    
    return papers


def test_scoring(papers):
    """Test the scoring functionality"""
    print("\n" + "="*60)
    print("🧪 TESTING: Paper Scoring")
    print("="*60)
    
    fetcher = ArxivFetcher()
    scored = fetcher.score_and_rank(papers)
    
    print(f"\n🎯 Top 5 papers by relevance:")
    for i, (paper, score) in enumerate(scored[:5], 1):
        print(f"  {i}. [{score:.2f}] {paper.title[:55]}...")
    
    return scored[:5]


def test_synthesizer(top_papers):
    """Test the synthesizer module"""
    print("\n" + "="*60)
    print("🧪 TESTING: PaperSynthesizer")
    print("="*60)
    
    synthesizer = PaperSynthesizer()
    syntheses = []
    
    print("\n🧠 Synthesizing top 3 papers...")
    for i, (paper, score) in enumerate(top_papers[:3], 1):
        print(f"  Processing {i}/3...")
        synthesis = synthesizer.synthesize(paper, score)
        syntheses.append(synthesis)
        print(f"    ✅ {synthesis['title'][:50]}...")
        print(f"       AI generated: {synthesis.get('ai_generated', False)}")
    
    return syntheses


def test_formatter(syntheses):
    """Test the formatter module"""
    print("\n" + "="*60)
    print("🧪 TESTING: NewsletterFormatter")
    print("="*60)
    
    formatter = NewsletterFormatter()
    
    print("\n📰 Formatting newsletter...")
    newsletter = formatter.format_daily_brief(syntheses)
    
    print(f"✅ Title: {newsletter['title']}")
    print(f"✅ Subtitle: {newsletter['subtitle']}")
    print(f"✅ Content length: {len(newsletter['markdown'])} characters")
    
    # Save test output
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    test_path = output_dir / "test_output.md"
    test_path.write_text(newsletter['markdown'])
    print(f"✅ Saved test output to {test_path}")
    
    return newsletter


def main():
    print("\n" + "="*60)
    print("🤖 arXiv Daily Brief - Test Suite")
    print("="*60)
    
    try:
        # Test 1: Fetch
        papers = test_fetcher()
        
        if not papers:
            print("\n⚠️  No papers found. This might be normal if no papers were published today.")
            print("   Try running with --days 3 to fetch more history.")
            return
        
        # Test 2: Score
        top_papers = test_scoring(papers)
        
        # Test 3: Synthesize
        syntheses = test_synthesizer(top_papers)
        
        # Test 4: Format
        newsletter = test_formatter(syntheses)
        
        # Success!
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60)
        print(f"\n📊 Summary:")
        print(f"   - Fetched: {len(papers)} papers")
        print(f"   - Selected: {len(syntheses)} papers")
        print(f"   - Newsletter: {newsletter['paper_count']} papers")
        print(f"\n📄 Output saved to: output/test_output.md")
        print(f"\n🚀 Pipeline is ready for automation!")
        print(f"   Run: ./setup.sh")
        print(f"   Then: ./run_daily.sh")
        print(f"\n🪷 JSCA")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
