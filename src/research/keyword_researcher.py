import os
import re
from typing import Dict, List, Optional

import aiohttp
import numpy as np
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class KeywordResearcher:
    def __init__(self, youtube_api_key: Optional[str] = None):
        self.youtube_api_key = youtube_api_key or os.getenv("YOUTUBE_API_KEY")
        if self.youtube_api_key:
            self.youtube = build("youtube", "v3", developerKey=self.youtube_api_key)

    async def analyze_keyword(self, keyword: str) -> Dict:
        """Analyze a keyword for YouTube SEO."""
        # Get YouTube search data
        youtube_data = await self._get_youtube_data(keyword)
        
        # Get web search data
        web_data = await self._get_web_data(keyword)
        
        # Calculate competition metrics
        competition_metrics = await self._calculate_competition_metrics(youtube_data, web_data)
        
        # Generate keyword suggestions
        suggestions = await self._generate_keyword_suggestions(keyword, youtube_data, web_data)
        
        return {
            "keyword": keyword,
            "youtube_metrics": youtube_data,
            "web_metrics": web_data,
            "competition_metrics": competition_metrics,
            "suggestions": suggestions
        }

    async def _get_youtube_data(self, keyword: str) -> Dict:
        """Get YouTube-specific metrics for the keyword."""
        if not self.youtube_api_key:
            return {
                "total_videos": 0,
                "avg_views": 0,
                "avg_likes": 0,
                "avg_comments": 0,
                "top_channels": []
            }
        
        try:
            # Get search results
            request = self.youtube.search().list(
                part="snippet",
                q=keyword,
                type="video",
                maxResults=50,
                order="viewCount"
            )
            response = request.execute()
            
            if not response["items"]:
                return {
                    "total_videos": 0,
                    "avg_views": 0,
                    "avg_likes": 0,
                    "avg_comments": 0,
                    "top_channels": []
                }
            
            # Get video IDs
            video_ids = [item["id"]["videoId"] for item in response["items"]]
            
            # Get video statistics
            request = self.youtube.videos().list(
                part="statistics",
                id=",".join(video_ids)
            )
            stats_response = request.execute()
            
            # Calculate metrics
            views = []
            likes = []
            comments = []
            channels = {}
            
            for item in stats_response.get("items", []):
                try:
                    if "statistics" not in item:
                        continue
                        
                    stats = item["statistics"]
                    views.append(int(stats.get("viewCount", 0)))
                    likes.append(int(stats.get("likeCount", 0)))
                    comments.append(int(stats.get("commentCount", 0)))
                    
                    # Get channel info - safely access from search results instead
                    # since snippet might not be in stats response
                    channel_id = ""
                    for search_item in response.get("items", []):
                        if search_item.get("id", {}).get("videoId") == item.get("id"):
                            if "snippet" in search_item and "channelId" in search_item["snippet"]:
                                channel_id = search_item["snippet"]["channelId"]
                                break
                    
                    if channel_id:
                        if channel_id not in channels:
                            channels[channel_id] = 1
                        else:
                            channels[channel_id] += 1
                except Exception as e:
                    print(f"[ERROR] Error processing video stats: {str(e)}")
                    continue
            
            # Get top channels
            top_channels = sorted(channels.items(), key=lambda x: x[1], reverse=True)[:5]
            
            # Safe calculation with error handling
            return {
                "total_videos": len(response.get("items", [])),
                "avg_views": int(np.mean(views)) if views else 0,
                "avg_likes": int(np.mean(likes)) if likes else 0,
                "avg_comments": int(np.mean(comments)) if comments else 0,
                "top_channels": top_channels
            }
        except HttpError:
            return {
                "total_videos": 0,
                "avg_views": 0,
                "avg_likes": 0,
                "avg_comments": 0,
                "top_channels": []
            }

    async def _get_web_data(self, keyword: str) -> Dict:
        """Get web search data for the keyword."""
        async with aiohttp.ClientSession() as session:
            # Search Google
            google_url = f"https://www.google.com/search?q={keyword}"
            async with session.get(google_url) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, "html.parser")
                    
                    # Extract search results
                    search_results = soup.find_all("div", class_="g")
                    
                    # Extract related searches
                    related_searches = soup.find_all("div", class_="BNeawe")
                    
                    return {
                        "total_results": len(search_results),
                        "related_searches": [s.text for s in related_searches[:5]],
                        "search_volume": self._estimate_search_volume(len(search_results))
                    }
                else:
                    return {
                        "total_results": 0,
                        "related_searches": [],
                        "search_volume": "Low"
                    }

    async def _calculate_competition_metrics(
        self,
        youtube_data: Dict,
        web_data: Dict
    ) -> Dict:
        """Calculate competition metrics for the keyword."""
        # Calculate YouTube competition score
        youtube_score = 0
        if youtube_data["total_videos"] > 0:
            youtube_score = min(
                (youtube_data["avg_views"] * youtube_data["total_videos"]) / 1000000,
                100
            )
        
        # Calculate web competition score
        web_score = 0
        if web_data["total_results"] > 0:
            web_score = min(web_data["total_results"] / 100, 100)
        
        # Calculate overall competition score
        overall_score = (youtube_score + web_score) / 2
        
        return {
            "youtube_competition": self._get_competition_level(youtube_score),
            "web_competition": self._get_competition_level(web_score),
            "overall_competition": self._get_competition_level(overall_score),
            "youtube_score": youtube_score,
            "web_score": web_score,
            "overall_score": overall_score
        }

    async def _generate_keyword_suggestions(
        self,
        keyword: str,
        youtube_data: Dict,
        web_data: Dict
    ) -> List[Dict]:
        """Generate keyword suggestions based on the analysis."""
        suggestions = []
        
        # Add related searches from web data
        for related in web_data.get("related_searches", []):
            suggestions.append({
                "keyword": related,
                "type": "related_search",
                "competition": "Unknown"
            })
        
        # Generate long-tail variations
        long_tail = [
            f"how to {keyword}",
            f"best {keyword}",
            f"{keyword} tutorial",
            f"{keyword} guide",
            f"learn {keyword}",
            f"{keyword} tips",
            f"{keyword} tricks",
            f"{keyword} for beginners",
            f"advanced {keyword}",
            f"{keyword} examples"
        ]
        
        for lt in long_tail:
            suggestions.append({
                "keyword": lt,
                "type": "long_tail",
                "competition": "Unknown"
            })
        
        return suggestions

    def _estimate_search_volume(self, result_count: int) -> str:
        """Estimate search volume based on result count."""
        if result_count > 1000000:
            return "Very High"
        elif result_count > 100000:
            return "High"
        elif result_count > 10000:
            return "Medium"
        elif result_count > 1000:
            return "Low"
        else:
            return "Very Low"

    def _get_competition_level(self, score: float) -> str:
        """Get competition level based on score."""
        if score >= 80:
            return "Very High"
        elif score >= 60:
            return "High"
        elif score >= 40:
            return "Medium"
        elif score >= 20:
            return "Low"
        else:
            return "Very Low" 