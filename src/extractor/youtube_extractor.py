import os
import re
from typing import Dict, List, Optional

import requests
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class YouTubeExtractor:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("YOUTUBE_API_KEY")
        if self.api_key:
            self.youtube = build("youtube", "v3", developerKey=self.api_key)

    async def extract_video_data(self, url: str) -> Dict:
        """Extract video data from a YouTube URL."""
        video_id = self._extract_video_id(url)
        if not video_id:
            raise ValueError("Invalid YouTube URL")

        # Get basic video data
        video_data = await self._get_video_info(video_id)
        
        # Get additional metadata
        video_data.update({
            "tags": await self._extract_tags(video_id),
            "comments": await self._extract_comments(video_id),
            "engagement_metrics": await self._get_engagement_metrics(video_id)
        })

        return video_data

    def _extract_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from various YouTube URL formats."""
        patterns = [
            r"(?:v=|\/)([0-9A-Za-z_-]{11}).*",
            r"youtu\.be\/([0-9A-Za-z_-]{11})",
            r"youtube\.com\/embed\/([0-9A-Za-z_-]{11})"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    async def _get_video_info(self, video_id: str) -> Dict:
        """Get basic video information using YouTube Data API."""
        if not self.api_key:
            return await self._scrape_video_info(video_id)

        try:
            request = self.youtube.videos().list(
                part="snippet,statistics,contentDetails",
                id=video_id
            )
            response = request.execute()

            if not response["items"]:
                return await self._scrape_video_info(video_id)

            video = response["items"][0]
            # Debug: print the full video object if 'snippet' is missing
            if "snippet" not in video or "statistics" not in video or "contentDetails" not in video:
                print("[DEBUG] Unexpected YouTube API response:", response)
                return {"error": "YouTube API response missing expected fields. See server logs for details.", "raw_response": response}
            return {
                "title": video["snippet"]["title"],
                "description": video["snippet"]["description"],
                "channel_title": video["snippet"]["channelTitle"],
                "published_at": video["snippet"]["publishedAt"],
                "view_count": video["statistics"]["viewCount"],
                "like_count": video["statistics"].get("likeCount", 0),
                "comment_count": video["statistics"]["commentCount"],
                "duration": video["contentDetails"]["duration"]
            }
        except HttpError:
            return await self._scrape_video_info(video_id)

    async def _scrape_video_info(self, video_id: str) -> Dict:
        """Fallback method to scrape video information when API is not available."""
        url = f"https://www.youtube.com/watch?v={video_id}"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        return {
            "title": self._extract_title(soup),
            "description": self._extract_description(soup),
            "channel_title": self._extract_channel(soup),
            "published_at": self._extract_publish_date(soup),
            "view_count": self._extract_view_count(soup),
            "like_count": self._extract_like_count(soup),
            "comment_count": self._extract_comment_count(soup)
        }

    async def _extract_tags(self, video_id: str) -> List[str]:
        """Extract video tags."""
        if self.api_key:
            try:
                request = self.youtube.videos().list(
                    part="snippet",
                    id=video_id
                )
                response = request.execute()
                if response.get("items") and len(response["items"]) > 0:
                    # Make sure snippet exists before trying to access it
                    if "snippet" in response["items"][0]:
                        return response["items"][0]["snippet"].get("tags", [])
                    else:
                        print(f"[DEBUG] No snippet in tags response: {response}")
                        return []
                else:
                    print(f"[DEBUG] No items in tags response for video {video_id}")
                    return []
            except HttpError as e:
                print(f"[ERROR] YouTube API error in tag extraction: {str(e)}")
                return []
            except Exception as e:
                print(f"[ERROR] Unexpected error in tag extraction: {str(e)}")
                return []

        # Fallback to scraping
        url = f"https://www.youtube.com/watch?v={video_id}"
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, "html.parser")
            return self._extract_tags_from_soup(soup)
        except Exception as e:
            print(f"[ERROR] Failed to scrape tags: {str(e)}")
            return []

    async def _extract_comments(self, video_id: str, max_comments: int = 100) -> List[Dict]:
        """Extract video comments."""
        if not self.api_key:
            return []

        try:
            comments = []
            request = self.youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=min(max_comments, 100),
                textFormat="plainText"
            )

            while request and len(comments) < max_comments:
                response = request.execute()
                
                if "items" not in response:
                    print(f"[DEBUG] No items in comments response: {response}")
                    break
                    
                for item in response["items"]:
                    try:
                        if "snippet" not in item or "topLevelComment" not in item["snippet"]:
                            continue
                            
                        comment = item["snippet"]["topLevelComment"]["snippet"]
                        comments.append({
                            "author": comment.get("authorDisplayName", ""),
                            "text": comment.get("textDisplay", ""),
                            "like_count": comment.get("likeCount", 0),
                            "published_at": comment.get("publishedAt", "")
                        })
                    except KeyError as e:
                        print(f"[ERROR] KeyError in comment extraction: {str(e)}")
                        continue

                if len(comments) >= max_comments:
                    break

                request = self.youtube.commentThreads().list_next(request, response)

            return comments
        except HttpError as e:
            print(f"[ERROR] YouTube API error in comment extraction: {str(e)}")
            return []
        except Exception as e:
            print(f"[ERROR] Unexpected error in comment extraction: {str(e)}")
            return []

    async def _get_engagement_metrics(self, video_id: str) -> Dict:
        """Calculate engagement metrics."""
        video_info = await self._get_video_info(video_id)
        
        try:
            views = int(video_info["view_count"])
            likes = int(video_info["like_count"])
            comments = int(video_info["comment_count"])
            
            return {
                "engagement_rate": (likes + comments) / views if views > 0 else 0,
                "like_ratio": likes / views if views > 0 else 0,
                "comment_ratio": comments / views if views > 0 else 0
            }
        except (ValueError, KeyError):
            return {
                "engagement_rate": 0,
                "like_ratio": 0,
                "comment_ratio": 0
            }

    # Helper methods for scraping
    def _extract_title(self, soup: BeautifulSoup) -> str:
        title_tag = soup.find("meta", property="og:title")
        return title_tag["content"] if title_tag else ""

    def _extract_description(self, soup: BeautifulSoup) -> str:
        desc_tag = soup.find("meta", property="og:description")
        return desc_tag["content"] if desc_tag else ""

    def _extract_channel(self, soup: BeautifulSoup) -> str:
        channel_tag = soup.find("link", itemprop="name")
        return channel_tag["content"] if channel_tag else ""

    def _extract_publish_date(self, soup: BeautifulSoup) -> str:
        date_tag = soup.find("meta", itemprop="datePublished")
        return date_tag["content"] if date_tag else ""

    def _extract_view_count(self, soup: BeautifulSoup) -> str:
        view_tag = soup.find("meta", itemprop="interactionCount")
        return view_tag["content"] if view_tag else "0"

    def _extract_like_count(self, soup: BeautifulSoup) -> str:
        # Note: Like count is not directly available in the page source
        return "0"

    def _extract_comment_count(self, soup: BeautifulSoup) -> str:
        comment_tag = soup.find("meta", itemprop="commentCount")
        return comment_tag["content"] if comment_tag else "0"

    def _extract_tags_from_soup(self, soup: BeautifulSoup) -> List[str]:
        tags = []
        for tag in soup.find_all("meta", property="og:video:tag"):
            tags.append(tag["content"])
        return tags 