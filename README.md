# NewsPodcast

An automated news podcast generator that scrapes news articles from various sources and converts them into audio podcast episodes using AI-powered text-to-speech.

## Features

- **Multi-Source News Scraping**: Automatically fetches articles from:
  - Editorials (Indian Express)
  - Expert Explanations
  - Law Explanations
  - Global News
  - Opinions & Columns
  
- **Paywall Bypass**: Extracts full article content using external APIs to bypass paywalls

- **AI-Powered Compilation**: Uses GPT-4o-mini to compile articles into structured podcast transcripts with chapters

- **Text-to-Speech**: Converts transcripts to high-quality audio using x-ai/grok-voice-tts-1.0 via OpenRouter

- **Audio Processing**: Combines multiple audio segments into complete podcast episodes using pydub

## Installation

### Prerequisites

- Python 3.12 or higher
- uv (recommended) or pip

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd NewsPodcast
```

2. Install dependencies:
```bash
uv sync
# or with pip
pip install -r requirements.txt
```

3. Install Playwright browser:
```bash
playwright install chromium-headless-shell
```

## Configuration

Create a `config.yaml` file in the project root:

```yaml
openrouter_api_key: "your-openrouter-api-key"
```

Or use environment variables in `.env`:
```bash
OPENROUTER_API_KEY=your-openrouter-api-key
```

## Usage

Run the main script:

```bash
python main.py
```

The workflow:
1. Scrapes news articles from multiple sources in parallel
2. Extracts full article content (bypassing paywalls)
3. Compiles articles into podcast transcripts using AI
4. Generates audio files for each chapter
5. Combines segments into complete podcast episodes
6. Saves final audio files to the `audio/` directory

## Project Structure

```
NewsPodcast/
├── main.py                 # Main entry point and orchestration
├── config.yaml             # Configuration file (API keys)
├── .env                    # Environment variables
├── agents/                 # AI agents for processing
│   ├── podcast_audio.py    # Text-to-speech generation
│   ├── text_compiler.py    # Transcript compilation using AI
│   └── prompts.py          # AI prompts
├── tools/                  # News scraping modules
│   ├── editorials.py       # Editorial scraper
│   ├── experts_explain.py  # Expert explanations scraper
│   ├── law_explain.py      # Law explanations scraper
│   ├── global_explain.py   # Global news scraper
│   └── opinions_columns.py # Opinions & columns scraper
├── audio/                  # Generated podcast audio files
└── pyproject.toml          # Project dependencies
```

## Dependencies

- beautifulsoup4>=4.14.3
- lxml>=6.1.1
- openai>=2.37.0
- playwright>=1.60.0
- pydantic>=2.13.4
- pydub>=0.25.1
- python-dotenv>=1.2.2
- pyyaml>=6.0.3
- requests>=2.34.2
- tqdm>=4.67.3

## API Requirements

- **OpenRouter API Key**: Required for both text compilation (GPT-4o-mini) and text-to-speech (x-ai/grok-voice-tts-1.0)

Get your API key at: https://openrouter.ai/
