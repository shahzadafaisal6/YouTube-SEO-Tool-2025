import os
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl

from .extractor.youtube_extractor import YouTubeExtractor
from .analyzer.content_analyzer import ContentAnalyzer
from .generator.seo_generator import SEOGenerator
from .research.keyword_researcher import KeywordResearcher

app = FastAPI(
    title="YouTube SEO Tool",
    description="A unified tool for YouTube SEO optimization and analysis",
    version="1.0.0"
)

class AnalysisRequest(BaseModel):
    url: Optional[HttpUrl] = None
    keyword: Optional[str] = None
    use_gpt: bool = False

class AnalysisResponse(BaseModel):
    video_data: dict
    seo_suggestions: dict
    keyword_analysis: dict
    sentiment_analysis: dict
    timestamp: str

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_content(request: AnalysisRequest):
    try:
        # Check if we have at least one of URL or keyword
        if not request.url and not request.keyword:
            raise HTTPException(
                status_code=400, 
                detail="Please provide either a YouTube URL or a keyword for analysis"
            )
            
        # Initialize components
        extractor = YouTubeExtractor()
        analyzer = ContentAnalyzer()
        generator = SEOGenerator()
        researcher = KeywordResearcher()

        # Extract video data if URL is provided
        video_data = {}
        if request.url:
            try:
                video_data = await extractor.extract_video_data(str(request.url))
                # Check if there was an error in the video data
                if "error" in video_data:
                    raise HTTPException(
                        status_code=500,
                        detail=f"YouTube API error: {video_data['error']}"
                    )
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))
            except Exception as e:
                print(f"[ERROR] Video extraction failed: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to extract video data: {str(e)}"
                )

        # Perform keyword research
        keyword = request.keyword or video_data.get("title", "")
        try:
            keyword_analysis = await researcher.analyze_keyword(keyword)
        except Exception as e:
            print(f"[ERROR] Keyword research failed: {str(e)}")
            keyword_analysis = {"error": f"Keyword research failed: {str(e)}"}

        # Generate SEO suggestions
        try:
            seo_suggestions = await generator.generate_seo_content(
                keyword=keyword,
                video_data=video_data,
                use_gpt=request.use_gpt
            )
        except Exception as e:
            print(f"[ERROR] SEO generation failed: {str(e)}")
            seo_suggestions = {"error": f"SEO generation failed: {str(e)}"}

        # Analyze content and sentiment
        try:
            sentiment_analysis = await analyzer.analyze_content(
                video_data=video_data,
                keyword=keyword
            )
        except Exception as e:
            print(f"[ERROR] Sentiment analysis failed: {str(e)}")
            sentiment_analysis = {"error": f"Sentiment analysis failed: {str(e)}"}

        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results = {
            "video_data": video_data,
            "seo_suggestions": seo_suggestions,
            "keyword_analysis": keyword_analysis,
            "sentiment_analysis": sentiment_analysis,
            "timestamp": timestamp
        }

        # Save to results directory
        os.makedirs("results", exist_ok=True)
        with open(f"results/analysis_{timestamp}.json", "w") as f:
            import json
            json.dump(results, f, indent=2)

        return results

    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Unexpected error in analyze_content: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"An unexpected error occurred: {str(e)}"
        )

@app.get("/")
async def root():
    return {
        "message": "Welcome to YouTube SEO Tool",
        "endpoints": {
            "/analyze": "POST - Analyze YouTube content and generate SEO suggestions",
            "/docs": "GET - API documentation"
        }
    } 