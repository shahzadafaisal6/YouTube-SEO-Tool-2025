import argparse
import asyncio
import json
import os
from datetime import datetime
from typing import Optional

from dotenv import load_dotenv

from extractor.youtube_extractor import YouTubeExtractor
from analyzer.content_analyzer import ContentAnalyzer
from generator.seo_generator import SEOGenerator
from research.keyword_researcher import KeywordResearcher

# Load environment variables
load_dotenv()

async def analyze_content(url: Optional[str], keyword: str, use_gpt: bool = False):
    """Analyze YouTube content and generate SEO suggestions."""
    try:
        # Initialize components
        extractor = YouTubeExtractor()
        analyzer = ContentAnalyzer()
        generator = SEOGenerator()
        researcher = KeywordResearcher()

        # Extract video data if URL is provided
        video_data = {}
        if url:
            print(f"Extracting data from video: {url}")
            video_data = await extractor.extract_video_data(url)

        # Perform keyword research
        print(f"Analyzing keyword: {keyword}")
        keyword_analysis = await researcher.analyze_keyword(keyword)

        # Generate SEO suggestions
        print("Generating SEO suggestions...")
        seo_suggestions = await generator.generate_seo_content(
            keyword=keyword,
            video_data=video_data,
            use_gpt=use_gpt
        )

        # Analyze content and sentiment
        print("Analyzing content and sentiment...")
        sentiment_analysis = await analyzer.analyze_content(
            video_data=video_data,
            keyword=keyword
        )

        # Prepare results
        results = {
            "video_data": video_data,
            "seo_suggestions": seo_suggestions,
            "keyword_analysis": keyword_analysis,
            "sentiment_analysis": sentiment_analysis,
            "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S")
        }

        # Save results
        os.makedirs("results", exist_ok=True)
        output_file = f"results/analysis_{results['timestamp']}.json"
        with open(output_file, "w") as f:
            json.dump(results, f, indent=2)

        print(f"\nAnalysis complete! Results saved to: {output_file}")
        
        # Print summary
        print("\nSummary:")
        print("-" * 50)
        
        if video_data:
            print(f"Video Title: {video_data.get('title', 'N/A')}")
            print(f"Channel: {video_data.get('channel_title', 'N/A')}")
            print(f"Views: {video_data.get('view_count', 'N/A')}")
            print(f"Likes: {video_data.get('like_count', 'N/A')}")
            print(f"Comments: {video_data.get('comment_count', 'N/A')}")
        
        print("\nSEO Score:", seo_suggestions["seo_score"]["total_score"])
        print("\nTop Title Suggestions:")
        for i, title in enumerate(seo_suggestions["titles"][:3], 1):
            print(f"{i}. {title}")
        
        print("\nCompetition Level:", keyword_analysis["competition_metrics"]["overall_competition"])
        print("\nTop Keyword Suggestions:")
        for i, suggestion in enumerate(keyword_analysis["suggestions"][:3], 1):
            print(f"{i}. {suggestion['keyword']}")

    except Exception as e:
        print(f"Error: {str(e)}")
        raise

def main():
    parser = argparse.ArgumentParser(description="YouTube SEO Tool")
    parser.add_argument("--url", help="YouTube video URL to analyze")
    parser.add_argument("--keyword", required=True, help="Target keyword for analysis")
    parser.add_argument("--use-gpt", action="store_true", help="Use GPT-3 for content generation")
    
    args = parser.parse_args()
    
    # Run the analysis
    asyncio.run(analyze_content(args.url, args.keyword, args.use_gpt))

if __name__ == "__main__":
    main() 