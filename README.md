# YouTube SEO Tool

A comprehensive Python-based YouTube SEO tool that helps content creators optimize their videos for better visibility and engagement. This tool combines video analysis, keyword research, content analysis, and SEO suggestion generation.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.68.0-009688.svg)](https://fastapi.tiangolo.com/)

## 🚀 Features

- **Video Analysis**
  - Extract video metadata, tags, and comments
  - Analyze video performance metrics
  - Calculate engagement rates and ratios

- **Content Analysis**
  - Sentiment analysis of video content and comments
  - Content clustering and pattern detection
  - Trend analysis and keyword density calculation

- **SEO Generation**
  - Generate SEO-optimized titles and descriptions
  - Create relevant tags and hashtags
  - Calculate SEO scores and provide optimization tips
  - Optional GPT-3.5 integration for enhanced content generation

- **Keyword Research**
  - Analyze keyword competition on YouTube and web
  - Generate keyword suggestions and long-tail variations
  - Calculate competition metrics and search volume estimates

## 🛠️ Installation

### Option 1: Docker (Recommended)

1. Clone the repository:
```bash
git clone https://github.com/your-github-username/YouTube-SEO-Tool-Python-based.git
cd YouTube-SEO-Tool-Python-based
```

2. Create a `.env` file from the template:
```bash
cp .env.template .env
```

3. Edit the `.env` file with your API keys:
```
YOUTUBE_API_KEY=your_youtube_api_key
OPENAI_API_KEY=your_openai_api_key  # Optional
```

4. Build and run the Docker container:
```bash
docker build -t youtube-seo-tool .
docker run -p 8000:8000 --env-file .env youtube-seo-tool
```

### Option 2: Manual Installation

1. Clone the repository:
```bash
git clone https://github.com/your-github-username/YouTube-SEO-Tool-Python-based.git
cd YouTube-SEO-Tool-Python-based
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.template .env
# Edit the .env file with your API keys
```

5. Install NLTK data:
```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('vader_lexicon'); nltk.download('punkt_tab'); nltk.download('averaged_perceptron_tagger'); nltk.download('maxent_ne_chunker'); nltk.download('words'); nltk.download('tagsets')"
```

## 📊 Usage

### Web Interface

1. Start the FastAPI server:
```bash
# If installed manually
uvicorn src.main:app --host 0.0.0.0 --port 8000

# If using Docker
# The server automatically starts
```

2. Open your browser and navigate to:
```
http://localhost:8000
```

3. Use the interactive API documentation at:
```
http://localhost:8000/docs
```

### Command Line Interface

The tool also provides a CLI interface:

```bash
# Analyze a YouTube video
python src/cli.py --url "https://www.youtube.com/watch?v=example" --keyword "ai tools"

# Analyze a keyword
python src/cli.py --keyword "python programming"

# Use GPT-3.5 for content generation
python src/cli.py --keyword "machine learning" --use-gpt
```

## 🔌 API Endpoints

- `POST /analyze`: Analyze YouTube content and generate SEO suggestions
  - Parameters:
    - `url` (optional): YouTube video URL
    - `keyword` (optional): Target keyword
    - `use_gpt` (optional): Use GPT-3.5 for content generation

## 📁 Project Structure

```
YouTube-SEO-Tool-Python-based/
├── src/
│   ├── extractor/       # YouTube data extraction
│   ├── analyzer/        # Content analysis
│   ├── generator/       # SEO content generation
│   ├── research/        # Keyword research
│   ├── main.py          # FastAPI app
│   └── cli.py           # Command-line interface
├── results/             # Analysis results storage
├── requirements.txt     # Python dependencies
├── Dockerfile           # Docker configuration
├── .env.template        # Environment variables template
└── README.md            # Documentation
```

## 🔍 Getting YouTube API Key

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable the YouTube Data API v3
4. Create credentials (API Key)
5. Add restrictions to the API key as needed

## 🧰 Dependencies

- Python 3.8+
- FastAPI
- Google API Python Client
- OpenAI API (optional)
- NLTK
- scikit-learn
- BeautifulSoup4
- aiohttp
- numpy

## 🤝 Contributing

Contributions are welcome! Here's how you can contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

This project was inspired by various YouTube SEO tools and integrates concepts from multiple open-source projects. 