# Exa + Perplexity News Analysis Integration

Two powerful Python projects that combine **Exa AI** search capabilities with **Perplexity AI** analysis to create intelligent news monitoring and analysis tools.

## 🚀 Projects Overview

### 1. Webset News Analyzer (`1_webset_news_analyzer.py`)
**Advanced news collection and analysis using Exa Websets**

- ⭐ **Complexity**: Intermediate
- 📄 **Lines of Code**: ~360
- 🔧 **Features**:
  - Creates persistent websets for ongoing news monitoring
  - Monitors webset completion with real-time progress updates
  - Enriches articles with metadata and analysis
  - Generates comprehensive markdown reports
  - Supports multiple news domains (TechCrunch, Reuters, Bloomberg, etc.)

### 2. Simple News Analyzer (`exa_perplexity_news.py`)
**Quick news search and analysis in minimal code**

- ⭐ **Complexity**: Beginner
- 📄 **Lines of Code**: ~114
- 🔧 **Features**:
  - Instant news search using Exa's neural search
  - Fast Perplexity AI analysis
  - Markdown report generation
  - Perfect for quick news insights
  - Interactive topic selection

## 🛠️ Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Environment Variables
Create a `.env` file in this directory:
```env
EXA_API_KEY=your_exa_api_key_here
PERPLEXITY_API_KEY=your_perplexity_api_key_here
```

### 3. Get API Keys
- **Exa API**: [https://dashboard.exa.ai](https://dashboard.exa.ai)
- **Perplexity API**: [https://www.perplexity.ai/settings/api](https://www.perplexity.ai/settings/api)

## 🎯 Usage

### Quick News Analysis (Recommended for beginners)
```bash
python exa_perplexity_news.py
```
- Enter a topic when prompted
- Get instant results with AI analysis
- Perfect for YouTube demos and quick insights

### Advanced Webset Analysis
```bash
python 1_webset_news_analyzer.py
```
- More comprehensive news collection
- Real-time monitoring of webset creation
- Detailed progress tracking
- Rich metadata extraction

## 📊 Example Output

Both projects generate markdown reports like this:

```markdown
# News Analysis: AI Developments

**Generated:** 2024-12-26 15:30:45

## 📰 Articles Found

### 1. OpenAI Releases GPT-5 with Breakthrough Capabilities
**URL:** https://techcrunch.com/...

Revolutionary advancement in AI reasoning and multimodal understanding...

## 🤖 AI Analysis

**Key Trends:**
- Rapid advancement in large language models
- Increased focus on reasoning capabilities
- Growing enterprise adoption

**Future Implications:**
- Potential disruption in software development
- Enhanced automation across industries
- New regulatory challenges emerging
```

## 🔄 Project Comparison

| Feature | Simple Analyzer | Webset Analyzer |
|---------|----------------|-----------------|
| **Setup Time** | 30 seconds | 2-5 minutes |
| **Search Method** | Direct API call | Persistent webset |
| **Monitoring** | None | Real-time progress |
| **Best For** | Quick demos | Ongoing research |
| **Code Length** | ~114 lines | ~360 lines |

## 🎥 YouTube Demo Script

### For `exa_perplexity_news.py` (3-minute demo):
1. **Show the code** (30s) - Highlight simplicity
2. **Run the program** (60s) - Enter "AI startups" as topic
3. **Review results** (60s) - Show found articles
4. **AI analysis** (30s) - Highlight insights generated

### For `1_webset_news_analyzer.py` (5-minute demo):
1. **Explain websets concept** (60s)
2. **Show webset creation** (90s)
3. **Monitor progress** (90s) - Real-time updates
4. **Review comprehensive results** (60s)

## 🚀 Advanced Use Cases

### Business Intelligence
```python
# Monitor competitor news
python exa_perplexity_news.py
# Topic: "Tesla competitors electric vehicles"
```

### Market Research
```python
# Track industry trends
python 1_webset_news_analyzer.py
# Modify topic in main(): "fintech funding 2024"
```

### Content Creation
```python
# Research for articles/videos
python exa_perplexity_news.py
# Topic: "blockchain applications healthcare"
```

## 🔧 Customization

### Modify News Sources
Edit the `includeDomains` array:
```python
"includeDomains": [
    "techcrunch.com", 
    "reuters.com", 
    "bloomberg.com",
    "your-custom-domain.com"  # Add your sources
]
```

### Adjust Analysis Depth
Modify the Perplexity prompt:
```python
prompt = f"""
Analyze these articles and focus on:
1. Financial implications
2. Technology trends
3. Competitive landscape
{news_text}
"""
```

## 📚 Learning Path

1. **Start with**: `exa_perplexity_news.py` - Learn basic concepts
2. **Understand**: API integration patterns
3. **Progress to**: `1_webset_news_analyzer.py` - Explore advanced features
4. **Experiment**: Modify topics, sources, and analysis prompts
5. **Build**: Your own custom news analysis tools

## 🐛 Troubleshooting

### Common Issues
- **API Key Error**: Check your `.env` file format
- **No Results**: Try broader search terms
- **Timeout**: Websets may take 2-5 minutes to complete
- **Rate Limits**: Exa free tier has daily limits

### Debug Mode
Add `print()` statements to see API responses:
```python
print(f"API Response: {response.json()}")
```

## 🎯 Next Steps

1. **Combine with other APIs**: Add sentiment analysis, stock data
2. **Create dashboards**: Use Flask/Streamlit for web interfaces
3. **Schedule automation**: Run daily/hourly news analysis
4. **Export formats**: Add PDF, JSON, CSV output options

## 📄 License

MIT License - Feel free to modify and distribute

---

**Perfect for**: Content creators, researchers, developers learning AI APIs, business intelligence, market research

**Keywords**: Exa AI, Perplexity AI, news analysis, websets, Python automation, AI integration 