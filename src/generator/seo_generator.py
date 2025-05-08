import os
import re
from typing import Dict, List, Optional

import openai
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class SEOGenerator:
    def __init__(self, youtube_api_key: Optional[str] = None, openai_api_key: Optional[str] = None):
        self.youtube_api_key = youtube_api_key or os.getenv("YOUTUBE_API_KEY")
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        
        if self.youtube_api_key:
            self.youtube = build("youtube", "v3", developerKey=self.youtube_api_key)
        
        if self.openai_api_key:
            openai.api_key = self.openai_api_key

    async def generate_seo_content(
        self,
        keyword: str,
        video_data: Dict,
        use_gpt: bool = False
    ) -> Dict:
        """Generate SEO-optimized content for YouTube videos."""
        # Generate title variations
        titles = await self._generate_titles(keyword, video_data, use_gpt)
        
        # Generate description
        description = await self._generate_description(keyword, video_data, use_gpt)
        
        # Generate tags
        tags = await self._generate_tags(keyword, video_data)
        
        # Generate hashtags
        hashtags = await self._generate_hashtags(keyword, video_data)
        
        # Generate SEO score
        seo_score = await self._calculate_seo_score(titles[0], description, tags, hashtags)

        return {
            "titles": titles,
            "description": description,
            "tags": tags,
            "hashtags": hashtags,
            "seo_score": seo_score,
            "optimization_tips": await self._generate_optimization_tips(
                titles[0], description, tags, hashtags
            )
        }

    async def _generate_titles(
        self,
        keyword: str,
        video_data: Dict,
        use_gpt: bool
    ) -> List[str]:
        """Generate SEO-optimized title variations."""
        if use_gpt and self.openai_api_key:
            return await self._generate_titles_with_gpt(keyword, video_data)
        
        # Get trending titles for the keyword
        trending_titles = await self._get_trending_titles(keyword)
        
        # Generate title variations
        titles = []
        
        # Pattern 1: Question format
        titles.append(f"How to {keyword} - Complete Guide")
        
        # Pattern 2: Number format
        titles.append(f"10 Best {keyword} Tips and Tricks")
        
        # Pattern 3: Ultimate guide format
        titles.append(f"The Ultimate {keyword} Guide")
        
        # Pattern 4: Trending format
        if trending_titles:
            titles.append(trending_titles[0])
        
        # Pattern 5: Problem-solution format
        titles.append(f"{keyword} - Everything You Need to Know")
        
        return titles

    async def _generate_description(
        self,
        keyword: str,
        video_data: Dict,
        use_gpt: bool
    ) -> str:
        """Generate SEO-optimized description."""
        if use_gpt and self.openai_api_key:
            return await self._generate_description_with_gpt(keyword, video_data)
        
        # Get trending descriptions
        trending_descriptions = await self._get_trending_descriptions(keyword)
        
        # Create description template
        description = f"""In this video, we'll explore everything about {keyword}. 

🔍 What you'll learn:
• Key concepts and fundamentals
• Best practices and tips
• Common mistakes to avoid
• Advanced techniques

📚 Resources:
• Links to related content
• Tools and software mentioned
• Additional learning materials

⏰ Timestamps:
00:00 - Introduction
02:00 - Main content
05:00 - Tips and tricks
08:00 - Conclusion

#YouTubeSEO #{keyword.replace(' ', '')} #ContentCreation

Subscribe for more content about {keyword} and related topics!"""
        
        return description

    async def _generate_tags(self, keyword: str, video_data: Dict) -> List[str]:
        """Generate relevant tags for the video."""
        # Get trending tags
        trending_tags = await self._get_trending_tags(keyword)
        
        # Generate base tags
        base_tags = [
            keyword,
            keyword.replace(" ", ""),
            f"how to {keyword}",
            f"{keyword} tutorial",
            f"{keyword} guide",
            f"learn {keyword}",
            f"{keyword} tips",
            f"{keyword} tricks"
        ]
        
        # Add trending tags
        if trending_tags:
            base_tags.extend(trending_tags[:10])
        
        # Add related tags from video data
        if video_data.get("tags"):
            base_tags.extend(video_data["tags"][:5])
        
        # Remove duplicates and limit to 15 tags
        return list(dict.fromkeys(base_tags))[:15]

    async def _generate_hashtags(self, keyword: str, video_data: Dict) -> List[str]:
        """Generate relevant hashtags for the video."""
        # Get trending hashtags
        trending_hashtags = await self._get_trending_hashtags(keyword)
        
        # Generate base hashtags
        base_hashtags = [
            f"#{keyword.replace(' ', '')}",
            f"#{keyword.replace(' ', '')}Tutorial",
            f"#{keyword.replace(' ', '')}Tips",
            f"#{keyword.replace(' ', '')}Guide",
            f"#Learn{keyword.replace(' ', '')}"
        ]
        
        # Add trending hashtags
        if trending_hashtags:
            base_hashtags.extend(trending_hashtags[:5])
        
        # Remove duplicates and limit to 10 hashtags
        return list(dict.fromkeys(base_hashtags))[:10]

    async def _calculate_seo_score(
        self,
        title: str,
        description: str,
        tags: List[str],
        hashtags: List[str]
    ) -> Dict:
        """Calculate SEO score for the generated content."""
        score = 0
        max_score = 100
        
        # Title score (30 points)
        title_score = 0
        if len(title) >= 30 and len(title) <= 60:
            title_score += 15
        if "#" in title:
            title_score += 5
        if "?" in title:
            title_score += 5
        if any(num in title for num in "0123456789"):
            title_score += 5
        score += title_score
        
        # Description score (30 points)
        desc_score = 0
        if len(description) >= 200:
            desc_score += 10
        if "⏰" in description:
            desc_score += 5
        if "🔍" in description:
            desc_score += 5
        if "📚" in description:
            desc_score += 5
        if "Subscribe" in description:
            desc_score += 5
        score += desc_score
        
        # Tags score (20 points)
        tags_score = min(len(tags) * 2, 20)
        score += tags_score
        
        # Hashtags score (20 points)
        hashtags_score = min(len(hashtags) * 2, 20)
        score += hashtags_score
        
        return {
            "total_score": score,
            "max_score": max_score,
            "title_score": title_score,
            "description_score": desc_score,
            "tags_score": tags_score,
            "hashtags_score": hashtags_score
        }

    async def _generate_optimization_tips(
        self,
        title: str,
        description: str,
        tags: List[str],
        hashtags: List[str]
    ) -> List[str]:
        """Generate optimization tips based on the content."""
        tips = []
        
        # Title tips
        if len(title) < 30:
            tips.append("Consider making the title longer (30-60 characters)")
        elif len(title) > 60:
            tips.append("Consider making the title shorter (30-60 characters)")
        
        # Description tips
        if len(description) < 200:
            tips.append("Add more content to the description (minimum 200 characters)")
        if "⏰" not in description:
            tips.append("Add timestamps to the description")
        if "Subscribe" not in description:
            tips.append("Add a call-to-action to subscribe")
        
        # Tags tips
        if len(tags) < 10:
            tips.append("Add more tags (aim for 10-15 tags)")
        
        # Hashtags tips
        if len(hashtags) < 5:
            tips.append("Add more hashtags (aim for 5-10 hashtags)")
        
        return tips

    async def _get_trending_titles(self, keyword: str) -> List[str]:
        """Get trending titles for the keyword."""
        if not self.youtube_api_key:
            return []
        
        try:
            request = self.youtube.search().list(
                part="snippet",
                q=keyword,
                type="video",
                maxResults=5,
                order="viewCount"
            )
            response = request.execute()
            
            return [item["snippet"]["title"] for item in response["items"]]
        except HttpError:
            return []

    async def _get_trending_descriptions(self, keyword: str) -> List[str]:
        """Get trending descriptions for the keyword."""
        if not self.youtube_api_key:
            return []
        
        try:
            request = self.youtube.search().list(
                part="snippet",
                q=keyword,
                type="video",
                maxResults=5,
                order="viewCount"
            )
            response = request.execute()
            
            return [item["snippet"]["description"] for item in response["items"]]
        except HttpError:
            return []

    async def _get_trending_tags(self, keyword: str) -> List[str]:
        """Get trending tags for the keyword."""
        if not self.youtube_api_key:
            return []
        
        try:
            request = self.youtube.search().list(
                part="snippet",
                q=keyword,
                type="video",
                maxResults=5,
                order="viewCount"
            )
            response = request.execute()
            
            video_ids = [item["id"]["videoId"] for item in response["items"]]
            
            request = self.youtube.videos().list(
                part="snippet",
                id=",".join(video_ids)
            )
            response = request.execute()
            
            tags = []
            for item in response["items"]:
                if "tags" in item["snippet"]:
                    tags.extend(item["snippet"]["tags"])
            
            return list(dict.fromkeys(tags))
        except HttpError:
            return []

    async def _get_trending_hashtags(self, keyword: str) -> List[str]:
        """Get trending hashtags for the keyword."""
        if not self.youtube_api_key:
            return []
        
        try:
            request = self.youtube.search().list(
                part="snippet",
                q=f"#{keyword.replace(' ', '')}",
                type="video",
                maxResults=5,
                order="viewCount"
            )
            response = request.execute()
            
            hashtags = []
            for item in response["items"]:
                description = item["snippet"]["description"]
                hashtags.extend(re.findall(r"#\w+", description))
            
            return list(dict.fromkeys(hashtags))
        except HttpError:
            return []

    async def _generate_titles_with_gpt(self, keyword: str, video_data: Dict) -> List[str]:
        """Generate titles using GPT-3."""
        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a YouTube SEO expert. Generate 5 engaging and SEO-optimized titles for a video about the given keyword."},
                    {"role": "user", "content": f"Generate 5 YouTube titles for a video about: {keyword}"}
                ],
                max_tokens=150,
                temperature=0.7
            )
            
            titles = response.choices[0].message.content.split("\n")
            titles = [title.strip() for title in titles if title.strip()]
            return titles[:5]
        except Exception:
            return await self._generate_titles(keyword, video_data, use_gpt=False)

    async def _generate_description_with_gpt(self, keyword: str, video_data: Dict) -> str:
        """Generate description using GPT-3."""
        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a YouTube SEO expert. Generate an engaging and SEO-optimized description for a video about the given keyword."},
                    {"role": "user", "content": f"Generate a YouTube description for a video about: {keyword}"}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content
        except Exception:
            return await self._generate_description(keyword, video_data, use_gpt=False) 