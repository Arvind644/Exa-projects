# AI Newsletter Generator with Exa Websets

Generate professional AI newsletters using Exa's Websets API for curated, enriched content.

## 🎯 Overview

This tool automatically creates professional newsletters by:
- 🔍 **Searching** for recent articles using Exa Websets API
- 📊 **Curating** content with intelligent criteria filtering  
- 🧠 **Enriching** articles with summaries, key details, and impact analysis
- 📰 **Formatting** into a professional newsletter layout
- 💾 **Saving** both formatted content and raw data locally

## ✨ Features

- **Websets Integration**: Uses Exa's powerful websets for intelligent content curation
- **Smart Enrichments**: Automatically generates summaries, extracts key details, and analyzes industry impact
- **Professional Formatting**: Creates beautifully formatted newsletters with headers, sections, and source citations
- **Customizable Topics**: Generate newsletters on any topic (AI, startups, crypto, etc.)
- **Dual Output**: Saves both human-readable newsletter and machine-readable JSON data
- **Real-time Monitoring**: Shows webset creation and enrichment progress
- **Fallback Handling**: Graceful handling when API calls fail

## 🚀 Quick Start

### 1. Prerequisites

```bash
# Install required packages
pip install python-dotenv requests

# Get your Exa API key from https://exa.ai
```

### 2. Environment Setup

Create a `.env` file:

```env
# Required
EXA_API_KEY=your_exa_api_key_here

# Optional
NEWSLETTER_TOPIC=AI and Technology
```

### 3. Run the Generator

```bash
# Generate with default topic
python ai_news_websets.py

# Generate with custom topic
python ai_news_websets.py --topic "AI startups"

# Other topic examples
python ai_news_websets.py --topic "Machine Learning"
python ai_news_websets.py --topic "Cryptocurrency"
python ai_news_websets.py --topic "Robotics"
```


### Newsletter Format
```
╔══════════════════════════════════════════════════════════════╗
║                    🤖 AI NEWSLETTER                          ║
║                        July 01, 2025                         ║
╚══════════════════════════════════════════════════════════════╝

📰 DAILY AI STARTUPS BRIEFING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Welcome to your AI-powered daily newsletter! Here are today's key developments from our curated webset analysis:

🔸 STORY #1: $1.3B funding round led by Microsoft and NVIDIA; total funding reaches $1.525B
   ──────────────────────────────────────────────────
   🔗 Source: https://siliconcanals.com/inflection-ai-gets-1-1b
   📰 Summary: Inflection AI raised $1.3B to develop personal AI assistant Pi...
   💡 Key Details: Microsoft, NVIDIA, Reid Hoffman invested; building 22,000 H100 GPU cluster
   🎯 Industry Impact: Represents significant investment in consumer-focused AI products...

📊 CONTENT SOURCE
────────────────────────────────────────────────────────────
🔗 Webset ID: webset_01jz31hkx7ssevyvx2hnqps4hk
🌐 View full webset: https://websets.exa.ai/webset_01jz31hkx7ssevyvx2hnqps4hk
📊 Articles analyzed: 3
```

## 🔧 Configuration Options

### Command Line Arguments

| Argument | Description | Example |
|----------|-------------|---------|
| `--topic` | Custom newsletter topic | `--topic "Quantum Computing"` |
| `--help` | Show help message | `--help` |

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `EXA_API_KEY` | ✅ Yes | - | Your Exa API key |
| `NEWSLETTER_TOPIC` | ❌ No | "AI and Technology" | Default newsletter topic |

## 📁 Output Files

Each run generates two files:

### 1. Newsletter Content (`newsletter_websets_YYYYMMDD_HHMMSS.txt`)
- Formatted newsletter ready for sharing
- Professional layout with headers and sections
- Source citations and webset links
- Statistics and metadata

### 2. Raw Data (`webset_data_YYYYMMDD_HHMMSS.json`)
- Complete webset response data
- Article metadata and enrichments
- Evaluation criteria results
- Useful for analysis and debugging

## 🎛️ How It Works

### 1. Webset Creation
```python
# Creates enriched webset with search criteria
payload = {
    "search": {
        "query": "latest AI startups news developments announcements 2025-07",
        "criteria": [
            "Recent article about AI startups developments or breakthroughs",
            "Article from credible tech or business publication",
            "Article contains specific details about companies, products, or research",
            "Article published within the last week"
        ],
        "entity": {"type": "article"},
        "count": 5
    },
    "enrichments": [
        {
            "title": "Article Summary",
            "description": "Provide a 2-3 sentence summary of the main points and key takeaways",
            "format": "text"
        },
        {
            "title": "Key Details", 
            "description": "Extract company names, product names, key figures, and important dates mentioned",
            "format": "text"
        },
        {
            "title": "Industry Impact",
            "description": "Analyze the significance and potential impact of this news on the industry", 
            "format": "text"
        }
    ]
}
```

### 2. Content Processing
- Waits for enrichments to complete (up to 2 minutes)
- Extracts article summaries, key details, and impact analysis
- Formats content with professional newsletter layout
- Adds source citations and webset transparency links

### 3. Output Generation
- Saves formatted newsletter as `.txt` file
- Saves raw webset data as `.json` file
- Provides webset URL for manual review

## 🔍 Search Criteria

The tool uses intelligent criteria to filter articles:

1. **Relevance**: Recent articles about specified topic developments
2. **Authority**: Articles from credible tech/business publications  
3. **Detail**: Articles with specific company, product, or research details
4. **Recency**: Articles published within the last week

## 🎯 Enrichment Types

Each article gets enriched with:

1. **Article Summary**: 2-3 sentence overview of main points
2. **Key Details**: Extracted companies, products, figures, dates
3. **Industry Impact**: Analysis of significance and potential impact

## 🚨 Error Handling

- **API Failures**: Graceful fallback to sample content
- **No Results**: Informative messages and suggested next steps
- **Timeout Handling**: Reasonable wait times with progress updates
- **Network Issues**: Retry logic with exponential backoff

## 🎨 Customization

### Change Default Topic
```bash
# Method 1: Environment variable
export NEWSLETTER_TOPIC="Quantum Computing"
python ai_news_websets.py

# Method 2: Command line
python ai_news_websets.py --topic "Blockchain"
```

### Modify Search Criteria
Edit the `criteria` list in `generate_newsletter_content_with_websets()`:

```python
criteria = [
    "Your custom criterion 1",
    "Your custom criterion 2", 
    "Your custom criterion 3"
]
```

### Adjust Enrichments
Modify the `enrichments` list to change analysis types:

```python
enrichments = [
    {
        "title": "Custom Analysis",
        "description": "Your custom enrichment description",
        "format": "text"
    }
]
```

## 📊 Performance

- **Webset Creation**: ~5-10 seconds
- **Enrichment Processing**: ~60-120 seconds
- **Content Formatting**: ~1-2 seconds
- **Total Runtime**: ~90-150 seconds

## 🔗 Related Links

- [Exa Websets Documentation](https://docs.exa.ai/reference/websets-api)
- [Exa API Keys](https://exa.ai)
- [Websets Dashboard](https://websets.exa.ai)

## 🆘 Troubleshooting

### Common Issues

**"Missing required environment variable: EXA_API_KEY"**
- Ensure `.env` file exists with `EXA_API_KEY=your_key`
- Check API key is valid at https://exa.ai

**"No items retrieved, using fallback content"**
- Topic may be too specific or recent
- Try broader topics like "AI" or "Technology"
- Check if articles exist for your timeframe

**Enrichments taking too long**
- Normal processing time is 1-2 minutes
- Some topics may take longer to enrich
- Script will timeout after 2 minutes and use available data

**NetworkError or ConnectionError**
- Check internet connection
- Verify Exa API is accessible
- Try again in a few minutes

### Debug Mode
Add debug prints by modifying the script:

```python
print(f"Debug: Query = {query}")
print(f"Debug: Criteria = {criteria}")
print(f"Debug: Response = {response.json()}")
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with different topics
5. Submit a pull request

## 📄 License

This project is part of the Exa AI examples and follows the same licensing terms.

---

**💡 Pro Tip**: Visit the webset URL provided in the output to see the full interactive webset with all articles and enrichments! 