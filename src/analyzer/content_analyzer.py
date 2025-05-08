import re
from typing import Dict, List, Tuple

import nltk
import numpy as np
from nltk.sentiment import SentimentIntensityAnalyzer
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class ContentAnalyzer:
    def __init__(self):
        # Download required NLTK data
        try:
            nltk.data.find('vader_lexicon')
        except LookupError:
            nltk.download('vader_lexicon')
        
        try:
            nltk.data.find('punkt')
        except LookupError:
            nltk.download('punkt')
        
        try:
            nltk.data.find('averaged_perceptron_tagger')
        except LookupError:
            nltk.download('averaged_perceptron_tagger')
            
        try:
            nltk.data.find('maxent_ne_chunker')
        except LookupError:
            nltk.download('maxent_ne_chunker')
            
        try:
            nltk.data.find('words')
        except LookupError:
            nltk.download('words')
            
        try:
            nltk.data.find('tagsets')
        except LookupError:
            nltk.download('tagsets')
        
        self.sia = SentimentIntensityAnalyzer()
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )

    async def analyze_content(self, video_data: Dict, keyword: str) -> Dict:
        """Analyze video content and generate insights."""
        # Extract text content
        title = video_data.get("title", "")
        description = video_data.get("description", "")
        comments = [comment["text"] for comment in video_data.get("comments", [])]

        # Perform various analyses
        sentiment = await self._analyze_sentiment(title, description, comments)
        trend_analysis = await self._analyze_trends(title, description, keyword)
        clustering = await self._cluster_content(title, description, comments)
        keyword_analysis = await self._analyze_keywords(title, description, keyword)

        return {
            "sentiment_analysis": sentiment,
            "trend_analysis": trend_analysis,
            "content_clusters": clustering,
            "keyword_analysis": keyword_analysis
        }

    async def _analyze_sentiment(self, title: str, description: str, comments: List[str]) -> Dict:
        """Analyze sentiment of content and comments."""
        # Analyze title and description
        content_sentiment = self.sia.polarity_scores(f"{title} {description}")
        
        # Analyze comments
        comment_sentiments = [self.sia.polarity_scores(comment) for comment in comments]
        avg_comment_sentiment = {
            "compound": np.mean([s["compound"] for s in comment_sentiments]),
            "pos": np.mean([s["pos"] for s in comment_sentiments]),
            "neu": np.mean([s["neu"] for s in comment_sentiments]),
            "neg": np.mean([s["neg"] for s in comment_sentiments])
        }

        return {
            "content_sentiment": content_sentiment,
            "comment_sentiment": avg_comment_sentiment,
            "sentiment_distribution": {
                "positive": len([s for s in comment_sentiments if s["compound"] > 0.2]),
                "neutral": len([s for s in comment_sentiments if -0.2 <= s["compound"] <= 0.2]),
                "negative": len([s for s in comment_sentiments if s["compound"] < -0.2])
            }
        }

    async def _analyze_trends(self, title: str, description: str, keyword: str) -> Dict:
        """Analyze content trends and patterns."""
        # Combine all text
        text = f"{title} {description}"
        
        # Extract key phrases
        key_phrases = self._extract_key_phrases(text)
        
        # Calculate keyword density
        keyword_density = self._calculate_keyword_density(text, keyword)
        
        # Analyze content structure
        structure_analysis = self._analyze_content_structure(title, description)

        return {
            "key_phrases": key_phrases,
            "keyword_density": keyword_density,
            "content_structure": structure_analysis
        }

    async def _cluster_content(self, title: str, description: str, comments: List[str]) -> Dict:
        """Cluster content and comments to identify patterns."""
        # Prepare text for clustering
        texts = [title, description] + comments
        texts = [t for t in texts if t.strip()]  # Remove empty strings
        
        if not texts:
            return {"clusters": [], "cluster_keywords": []}

        # Vectorize text
        try:
            tfidf_matrix = self.vectorizer.fit_transform(texts)
            
            # Determine optimal number of clusters
            n_clusters = min(5, len(texts))
            
            # Perform clustering
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            clusters = kmeans.fit_predict(tfidf_matrix)
            
            # Get cluster keywords
            cluster_keywords = self._get_cluster_keywords(tfidf_matrix, clusters, self.vectorizer)
            
            return {
                "clusters": clusters.tolist(),
                "cluster_keywords": cluster_keywords
            }
        except Exception as e:
            return {"error": str(e), "clusters": [], "cluster_keywords": []}

    async def _analyze_keywords(self, title: str, description: str, target_keyword: str) -> Dict:
        """Analyze keyword usage and relevance."""
        # Combine text
        text = f"{title} {description}"
        
        # Extract all words
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Calculate word frequencies
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Calculate keyword metrics
        keyword_metrics = {
            "frequency": word_freq.get(target_keyword.lower(), 0),
            "density": self._calculate_keyword_density(text, target_keyword),
            "position": self._analyze_keyword_position(title, description, target_keyword)
        }
        
        # Find related keywords
        related_keywords = self._find_related_keywords(text, target_keyword)
        
        return {
            "keyword_metrics": keyword_metrics,
            "related_keywords": related_keywords
        }

    def _extract_key_phrases(self, text: str) -> List[str]:
        """Extract key phrases from text."""
        try:
            # Tokenize and tag parts of speech
            tokens = nltk.word_tokenize(text)
            tagged = nltk.pos_tag(tokens)
            
            # Extract noun phrases
            grammar = r"""
                NP: {<DT>?<JJ>*<NN.*>+}
                    {<NNP>+}
            """
            chunk_parser = nltk.RegexpParser(grammar)
            tree = chunk_parser.parse(tagged)
            
            # Extract phrases
            phrases = []
            for subtree in tree.subtrees(filter=lambda t: t.label() == 'NP'):
                phrase = ' '.join(word for word, tag in subtree.leaves())
                phrases.append(phrase)
            
            return phrases
        except Exception as e:
            print(f"[WARNING] Error extracting key phrases: {str(e)}")
            # Fallback to simple extraction
            return re.findall(r'\b\w+\s+\w+\b', text)[:10]

    def _calculate_keyword_density(self, text: str, keyword: str) -> float:
        """Calculate keyword density in text."""
        words = re.findall(r'\b\w+\b', text.lower())
        keyword_count = len(re.findall(r'\b' + re.escape(keyword.lower()) + r'\b', text.lower()))
        return keyword_count / len(words) if words else 0

    def _analyze_content_structure(self, title: str, description: str) -> Dict:
        """Analyze the structure of the content."""
        return {
            "title_length": len(title),
            "description_length": len(description),
            "has_emojis": bool(re.search(r'[\U0001F300-\U0001F9FF]', title + description)),
            "has_hashtags": bool(re.search(r'#\w+', title + description)),
            "has_links": bool(re.search(r'https?://\S+', description))
        }

    def _get_cluster_keywords(self, tfidf_matrix, clusters, vectorizer) -> List[List[str]]:
        """Extract keywords for each cluster."""
        cluster_keywords = []
        for i in range(max(clusters) + 1):
            # Get documents in this cluster
            cluster_docs = tfidf_matrix[clusters == i]
            
            # Get average TF-IDF scores for this cluster
            avg_scores = cluster_docs.mean(axis=0).A1
            
            # Get top keywords
            top_indices = avg_scores.argsort()[-5:][::-1]
            keywords = [vectorizer.get_feature_names_out()[idx] for idx in top_indices]
            cluster_keywords.append(keywords)
        
        return cluster_keywords

    def _analyze_keyword_position(self, title: str, description: str, keyword: str) -> Dict:
        """Analyze keyword position in title and description."""
        title_pos = title.lower().find(keyword.lower())
        desc_pos = description.lower().find(keyword.lower())
        
        return {
            "in_title": title_pos != -1,
            "title_position": title_pos if title_pos != -1 else None,
            "in_description": desc_pos != -1,
            "description_position": desc_pos if desc_pos != -1 else None
        }

    def _find_related_keywords(self, text: str, target_keyword: str) -> List[Tuple[str, float]]:
        """Find keywords related to the target keyword."""
        # Vectorize text
        tfidf_matrix = self.vectorizer.fit_transform([text])
        
        # Get feature names
        feature_names = self.vectorizer.get_feature_names_out()
        
        # Get target keyword index
        try:
            target_idx = list(feature_names).index(target_keyword.lower())
        except ValueError:
            return []
        
        # Calculate similarities
        similarities = cosine_similarity(tfidf_matrix[:, target_idx:target_idx+1], tfidf_matrix.T).flatten()
        
        # Get top related keywords
        top_indices = similarities.argsort()[-6:][::-1]  # Get top 5 + target keyword
        related_keywords = [(feature_names[idx], similarities[idx]) for idx in top_indices]
        
        # Remove target keyword from results
        related_keywords = [kw for kw in related_keywords if kw[0] != target_keyword.lower()]
        
        return related_keywords[:5]  # Return top 5 related keywords 