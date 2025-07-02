# AI Voice Newsletter Generator with Exa Websets

Generate professional AI newsletters with intelligent audio summaries using Exa's Websets API for curated content and Gmail delivery.

## 🎯 Overview

This advanced tool automatically creates professional newsletters with voice summaries by:
- 🔍 **Searching** for recent articles using Exa Websets API with intelligent criteria
- 📊 **Curating** content with enrichments (summaries, key details, impact analysis)
- 🎙️ **Creating** 3-minute AI-powered audio summaries using Exa Answer API
- 📧 **Delivering** via Gmail with OAuth 2.0 authentication
- 🎧 **Attaching** professional voice narration using ElevenLabs TTS
- 💾 **Saving** all content locally with comprehensive backups

## ✨ Key Features

### 🤖 AI-Powered Content Generation
- **Websets Integration**: Uses Exa's powerful websets for intelligent content curation
- **Smart Enrichments**: Automatically generates summaries, extracts key details, and analyzes industry impact
- **Professional Formatting**: Creates beautifully formatted newsletters with headers, sections, and source citations
- **Customizable Topics**: Generate newsletters on any topic (AI, startups, crypto, etc.)

### 🎙️ Intelligent Audio Summaries
- **3-Minute Target**: Optimized for ~480 words (perfect listening duration)
- **Exa Answer API**: Enhanced summarization using AI for broadcast-quality scripts
- **Content Consistency**: Audio summaries based on actual newsletter content
- **Speech Optimization**: Text cleaning removes asterisks, time references, improves pronunciation
- **Professional Narration**: ElevenLabs TTS with optimized voice settings

### 📧 Gmail Integration
- **OAuth 2.0 Authentication**: Secure Google authentication with automatic token management
- **Direct Email Delivery**: Send newsletters directly from Gmail API
- **Audio Attachments**: Include MP3 audio summaries in email
- **HTML Formatting**: Professional email layout with proper MIME encoding
- **Multi-recipient Support**: Send to multiple recipients simultaneously

### 🚀 Command Line Interface
- **Multiple Modes**: Content-only, email-only, email-with-audio
- **Authentication Management**: Reset and refresh OAuth tokens
- **Performance Tracking**: Real-time timing and progress indicators
- **Flexible Topics**: Override default topics via command line
- **Comprehensive Logging**: Detailed status updates and error handling

## 🚀 Quick Start

### 1. Prerequisites

```bash
# Install required packages
pip install python-dotenv requests google-api-python-client google-auth-oauthlib google-auth-httplib2

# Get your API keys
# Exa API: https://exa.ai
# ElevenLabs API: https://elevenlabs.io (for audio)
```

### 2. Environment Setup

Create a `.env` file:

```env
# Required for all modes
EXA_API_KEY=your_exa_api_key_here

# Required for audio features
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
ELEVENLABS_VOICE_ID=pNInz6obpgDQGcFmaJgB

# Required for email delivery
RECIPIENT_EMAILS=email1@example.com,email2@example.com
SENDER_EMAIL=your-gmail@gmail.com

# Optional
NEWSLETTER_TOPIC=AI and Technology
```

### 3. Gmail OAuth Setup

1. **Google Cloud Console Setup**:
   ```
   1. Go to: https://console.cloud.google.com/
   2. Create a new project or select existing
   3. Enable Gmail API
   4. Go to APIs & Services → Credentials
   5. Click 'Create Credentials' → 'OAuth client ID'
   6. Choose 'Desktop application'
   7. Under 'Authorized redirect URIs', add: http://localhost:8080/
   8. Download credentials.json to this directory
   ```

2. **First-time Authentication**:
   ```bash
   python ai_news_websets.py --email-with-audio
   # Follow OAuth flow in browser
   # Credentials saved to token.json automatically
   ```

### 4. Run the Generator

```bash
# Generate content only (default)
python ai_news_websets.py --content-only

# Generate and send via email (no audio)
python ai_news_websets.py --email

# Generate with audio summary and send via email (full experience)
python ai_news_websets.py --email-with-audio

# Custom topic examples
python ai_news_websets.py --email-with-audio --topic "Machine Learning"
python ai_news_websets.py --email --topic "Cryptocurrency"
python ai_news_websets.py --content-only --topic "Robotics"

# Reset authentication
python ai_news_websets.py --reset-auth
```

## 📧 Usage Modes

| Mode | Content | Audio | Email | Use Case |
|------|---------|--------|-------|-----------|
| `--content-only` | ✅ | ❌ | ❌ | Local file generation only |
| `--email` | ✅ | ❌ | ✅ | Email newsletter without audio |
| `--email-with-audio` | ✅ | ✅ | ✅ | Full experience with voice summary |

### Default Behavior
- **Default mode**: `--content-only` (safest option)
- **Target completion**: Under 3 minutes total
- **Audio duration**: ~3 minutes (480 words optimized for speech)
- **Email format**: HTML with proper MIME encoding

## 🎙️ Audio Features

### Intelligent Script Generation
```python
# Uses Exa Answer API for enhanced summarization
audio_query = f"""Based on the following newsletter content about {topic}, 
create a concise 2-3 minute audio script for voice narration that:

1. Has a brief welcome introduction (no specific dates or times)
2. Summarizes the 3-4 most important stories from the newsletter content
3. Each story should be 30-45 seconds when spoken
4. Uses conversational, clear language suitable for audio
5. Includes a professional closing
6. Focuses on the key developments mentioned in the newsletter
"""
```

### Speech Optimization
- **Remove visual elements**: Asterisks, bullet points, markdown formatting
- **Time reference cleaning**: Remove "today", "yesterday", specific dates
- **Pronunciation improvements**: "AI" → "A I", "CEO" → "C E O"
- **Audio-friendly replacements**: "breaking news" → "latest developments"
- **URL removal**: Links stripped for audio clarity

### Professional Voice Settings
```python
voice_settings = {
    "stability": 0.6,        # Stable narration
    "similarity_boost": 0.75, # Clear voice reproduction  
    "style": 0.2,            # Slight engagement
    "use_speaker_boost": True # Enhanced clarity
}
```

## 🔧 Configuration Options

### Command Line Arguments

| Argument | Description | Example |
|----------|-------------|---------|
| `--content-only` | Generate content and save to file only (default) | `--content-only` |
| `--email` | Generate and send newsletter via email (no audio) | `--email` |
| `--email-with-audio` | Generate newsletter with audio and send via email | `--email-with-audio` |
| `--topic` | Custom newsletter topic | `--topic "Quantum Computing"` |
| `--reset-auth` | Reset Gmail authentication | `--reset-auth` |
| `--help` | Show help message | `--help` |

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `EXA_API_KEY` | ✅ Yes | - | Your Exa API key |
| `ELEVENLABS_API_KEY` | 🎧 Audio modes | - | ElevenLabs API key for voice generation |
| `RECIPIENT_EMAILS` | 📧 Email modes | - | Comma-separated email addresses |
| `SENDER_EMAIL` | 📧 Email modes | `newsletter@yourcompany.com` | Sender email address |
| `NEWSLETTER_TOPIC` | ❌ No | "AI and Technology" | Default newsletter topic |
| `ELEVENLABS_VOICE_ID` | 🎧 Audio modes | `pNInz6obpgDQGcFmaJgB` | ElevenLabs voice ID |

## 📁 Output Files

Each run generates multiple files based on mode:

### Content-Only Mode
- `newsletter_content_YYYYMMDD_HHMMSS.txt` - Newsletter with summary
- `webset_data_YYYYMMDD_HHMMSS.json` - Raw webset data

### Email Modes  
- `newsletter_backup_YYYYMMDD_HHMMSS.txt` - Full newsletter content
- `newsletter_YYYYMMDD_HHMMSS.html` - HTML email version
- `webset_data_YYYYMMDD_HHMMSS.json` - Raw webset data

### Audio Modes (Additional)
- `newsletter_audio/newsletter_summary_YYYYMMDD_HHMMSS.mp3` - Audio file
- `audio_script_YYYYMMDD_HHMMSS.txt` - Text used for audio generation

## 🎛️ How It Works

### 1. Webset Creation with Enrichments
```python
payload = {
    "search": {
        "query": "latest AI and Technology news developments announcements 2025-01",
        "criteria": [
            "Recent article about AI and Technology developments or breakthroughs",
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

### 2. Audio Script Enhancement
```python
# Uses Exa Answer API for intelligent summarization
def create_audio_summary_with_exa(self, newsletter_content: str, topic: str) -> str:
    # Creates audio script based on actual newsletter content
    # Enhanced by Exa Answer API for professional broadcast quality
    # Optimized for 3-minute duration (~480 words)
```

### 3. Gmail OAuth Authentication
```python
def get_gmail_service(self):
    # OAuth 2.0 flow with automatic token management
    # Supports port cycling (8080, 8081, 8082, 8083)
    # Saves credentials to token.json for reuse
```

### 4. Email Delivery with Attachments
```python
def send_newsletter_with_gmail(self, content: str, audio_path: Optional[str]):
    # Sends HTML-formatted email via Gmail API
    # Includes MP3 audio attachment if available
    # Supports multiple recipients
```

## 📊 Performance Metrics

- **Target Total Time**: Under 3 minutes
- **Webset Creation**: ~10-15 seconds
- **Enrichment Processing**: ~60-120 seconds  
- **Audio Generation**: ~15-30 seconds
- **Email Delivery**: ~5-10 seconds

### Real-time Progress Tracking
```
🚀 Starting AI Newsletter Generation with Websets...
📋 Mode: email_with_audio
⏱️  Target completion time: 3 minutes
==================================================
⏱️  Step 1/3: Creating enriched webset...
🎯 Webset created with ID: webset_01jz31hkx7ssevyvx2hnqps4hk
⏱️  Time elapsed: 12.3s
⏱️  Step 2/3: Formatting newsletter...
📄 Newsletter created with 5 curated articles
⏱️  Time elapsed: 89.7s
🎵 Generating AI-powered audio summary...
   📰 Using newsletter content for audio script generation
   📡 Enhanced with Exa Answer API for intelligent summarization
   🎙️ Audio script: 467 words (~3.1 minutes)
📧 Sending newsletter via Gmail...
✅ Newsletter sent successfully via Gmail!
⏱️  Total completion time: 157.4 seconds
🎉 Newsletter generated and delivered successfully!
```

## 🚨 Error Handling & Troubleshooting

### Gmail Authentication Issues

**"Error 400: redirect_uri_mismatch"**
```bash
# Solution: Add redirect URI to OAuth client
1. Go to: https://console.cloud.google.com/apis/credentials
2. Find your OAuth 2.0 Client ID and click Edit
3. Under 'Authorized redirect URIs', click 'ADD URI'  
4. Add exactly: http://localhost:8080/
5. Click 'SAVE' and wait 1-2 minutes
6. Run: python ai_news_websets.py --reset-auth
7. Run: python ai_news_websets.py --email-with-audio
```

**"Error 401: deleted_client"**
```bash
# OAuth client was deleted/disabled
1. Recreate OAuth client in Google Cloud Console
2. Download new credentials.json
3. Run: python ai_news_websets.py --reset-auth
```

### API Issues

**"Missing required environment variable: EXA_API_KEY"**
- Ensure `.env` file exists with `EXA_API_KEY=your_key`
- Check API key is valid at https://exa.ai

**"ElevenLabs API Error: Invalid API key"**
- Verify `ELEVENLABS_API_KEY` in `.env` file
- Check quota and billing at https://elevenlabs.io

**"No items retrieved, using fallback content"**
- Topic may be too specific or recent
- Try broader topics like "AI" or "Technology"  
- Check if articles exist for your timeframe

### Audio Generation Issues

**"Audio generation skipped"**
- Ensure `ELEVENLABS_API_KEY` is configured
- Check ElevenLabs account has available characters
- Verify `ELEVENLABS_VOICE_ID` is valid

**"Exa Answer API failed for audio"**
- Falls back to content-based audio summary
- Audio still generated, just less enhanced
- Check Exa API quota and limits

## 🎨 Customization

### Change Default Settings
```bash
# Override topic
python ai_news_websets.py --topic "Quantum Computing" --email-with-audio

# Use different voice
export ELEVENLABS_VOICE_ID=your_preferred_voice_id
```

### Modify Search Criteria
Edit the `criteria` list in `generate_newsletter_content_with_websets()`:
```python
criteria = [
    "Recent article about your_topic developments or breakthroughs",
    "Article from credible tech or business publication",
    "Article contains specific details about companies, products, or research", 
    "Article published within the last week"
]
```

### Customize Audio Settings
Modify voice settings in `generate_audio_with_elevenlabs()`:
```python
voice_settings = {
    "stability": 0.6,        # 0.0 to 1.0
    "similarity_boost": 0.75, # 0.0 to 1.0
    "style": 0.2,            # 0.0 to 1.0
    "use_speaker_boost": True
}
```

### Adjust Audio Length
Change target duration in `create_audio_summary_with_exa()`:
```python
target_words = 480  # ~3 minutes at 150 words/minute
# Adjust based on desired duration
```

## 🔗 API Documentation

- [Exa Websets API](https://docs.exa.ai/reference/websets-api)
- [Exa Answer API](https://docs.exa.ai/reference/answer-api)
- [Gmail API](https://developers.google.com/gmail/api)
- [ElevenLabs TTS API](https://docs.elevenlabs.io/api-reference)

## 📊 Comparison: Voice Newsletter vs Websets Newsletter

| Feature | Voice Newsletter (`ai_news.py`) | Websets Newsletter (`ai_news_websets.py`) |
|---------|--------------------------------|-------------------------------------------|
| **Content Source** | Exa Answer API | Exa Websets API |
| **Content Type** | AI-generated summaries | Curated articles with enrichments |
| **Audio Generation** | ✅ Exa Answer + ElevenLabs | ✅ Exa Answer + ElevenLabs |
| **Gmail Integration** | ✅ OAuth 2.0 | ✅ OAuth 2.0 |
| **Content Curation** | AI-generated content | Human-curated with AI enrichment |
| **Article Sources** | AI synthesis | Real article URLs and sources |
| **Enrichments** | ❌ | ✅ Summaries, details, impact analysis |
| **Webset Transparency** | ❌ | ✅ View full webset online |
| **Content Consistency** | AI-generated stories | Real articles with verified sources |

**Choose Voice Newsletter for**: Rapid AI-generated content and summaries
**Choose Websets Newsletter for**: Curated real articles with transparent sources

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Test with different topics and modes
4. Ensure Gmail authentication works
5. Test audio generation
6. Submit a pull request

## 📄 License

This project is part of the Exa AI examples and follows the same licensing terms.

---

**💡 Pro Tips**: 
- Visit the webset URL in the output to see the full interactive webset!
- Use `--reset-auth` if Gmail authentication fails
- Test with `--content-only` first before setting up email delivery
- Audio files are saved locally even when email delivery fails 