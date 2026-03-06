#!/usr/bin/env python3
"""
Wikipedia Scraper CLI Tool
Scrape Wikipedia articles and convert to AIM knowledge files
Created by @akulsaju - https://github.com/akulsaju

Usage:
    python scraper_cli.py <wikipedia_url> [--name ModelName] [--output path/to/file.aim]
    
Examples:
    python scraper_cli.py "https://en.wikipedia.org/wiki/Albert_Einstein"
    python scraper_cli.py "https://en.wikipedia.org/wiki/Python_(programming_language)" --name PythonKnowledge
    python scraper_cli.py "https://en.wikipedia.org/wiki/Machine_learning" --output ml_model.aim
"""

import sys
import argparse
import json
from pathlib import Path
from scraper import WebScraper


def main():
    parser = argparse.ArgumentParser(
        description='Scrape Wikipedia and convert to AIM knowledge files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scraper_cli.py "https://en.wikipedia.org/wiki/Albert_Einstein"
  python scraper_cli.py "https://en.wikipedia.org/wiki/Python_(programming_language)" --name PythonAI
  python scraper_cli.py "https://en.wikipedia.org/wiki/Artificial_intelligence" --output ai_knowledge.aim
        """
    )
    
    parser.add_argument('url', help='Wikipedia article URL to scrape')
    parser.add_argument('--name', '-n', help='Model name (default: article title)', default='')
    parser.add_argument('--output', '-o', help='Output file path (default: models/ directory)', default='')
    parser.add_argument('--print-sentences', '-p', action='store_true', help='Print extracted sentences')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show detailed progress')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🌐 Wikipedia Scraper for AIM Chat")
    print("=" * 60)
    print(f"📍 URL: {args.url}")
    print()
    
    try:
        # Validate URL
        if 'wikipedia.org' not in args.url.lower():
            print("⚠️  Warning: URL doesn't appear to be from Wikipedia")
            if args.verbose:
                print("   (Proceeding anyway...)")
        
        # Scrape the page
        print("🔄 Scraping Wikipedia page...")
        scraper = WebScraper()
        scraped_data = scraper.scrape_url(args.url)
        
        print(f"✅ Successfully scraped: {scraped_data['title']}")
        print(f"   📊 Paragraphs extracted: {scraped_data.get('paragraphs_extracted', 'unknown')}")
        print(f"   💾 Sentences extracted: {len(scraped_data['sentences'])}")
        print()
        
        if args.print_sentences:
            print("=" * 60)
            print("📝 Extracted Sentences:")
            print("=" * 60)
            for i, sentence in enumerate(scraped_data['sentences'][:30], 1):
                print(f"{i:2d}. {sentence}")
            if len(scraped_data['sentences']) > 30:
                print(f"... and {len(scraped_data['sentences']) - 30} more sentences")
            print()
        
        # Determine output path
        if args.output:
            output_path = args.output
            if not output_path.endswith('.aim'):
                output_path += '.aim'
        else:
            # Default to models directory
            models_dir = Path(__file__).parent.parent / 'models'
            models_dir.mkdir(exist_ok=True)
            
            model_name = args.name or scraped_data['title'].replace(' ', '_')
            model_name = model_name.replace('/', '_')[:50]
            output_path = models_dir / f"{model_name}.aim"
        
        # Ensure parent directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Save as .aim file
        print("💾 Saving as AIM model...")
        save_info = scraper.save_as_aim(scraped_data, str(output_path), args.name)
        
        print(f"✅ Model saved successfully!")
        print(f"   📦 Name: {save_info['name']}")
        print(f"   📊 Sentences: {save_info['sentences']}")
        print(f"   📁 Path: {Path(save_info['path']).absolute()}")
        print()
        
        print("=" * 60)
        print("🎉 Done! You can now load this model in AIM Chat")
        print("=" * 60)
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
