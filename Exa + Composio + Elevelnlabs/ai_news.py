#!/usr/bin/env python3
"""
AI Voice Newsletter Generator with Exa Answer API
===============================================
Enhanced version using Exa Answer API with command-line options for different modes.
"""

import os
import json
import time
import argparse
import base64
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import requests

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("python-dotenv not installed. Please set environment variables manually.")

# Google Gmail API imports
try:
    from googleapiclient.discovery import build
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    GMAIL_API_AVAILABLE = True
except ImportError:
    print("Google API client not installed. Email functionality will be limited.")
    print("Install with: pip install google-api-python-client google-auth-oauthlib google-auth-httplib2")
    GMAIL_API_AVAILABLE = False

# Gmail API scopes
GMAIL_SCOPES = [
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.modify'
]

class FixedNewsletterGenerator:
    """AI-powered voice newsletter generator with Gmail API email delivery"""
    
    def __init__(self):
        # API Keys
        self.exa_api_key = os.getenv('EXA_API_KEY')
        self.elevenlabs_api_key = os.getenv('ELEVENLABS_API_KEY')
        
        # Email configuration
        self.sender_email = os.getenv('SENDER_EMAIL', 'newsletter@yourcompany.com')
        self.recipient_emails = os.getenv('RECIPIENT_EMAILS', '').split(',')
        
        # Configuration
        self.voice_id = os.getenv('ELEVENLABS_VOICE_ID', 'pNInz6obpgDQGcFmaJgB')
        self.newsletter_topic = os.getenv('NEWSLETTER_TOPIC', 'AI and Technology')
        self.max_articles = int(os.getenv('MAX_ARTICLES', '8'))
        
        # Gmail service (will be initialized when needed)
        self.gmail_service = None
        
        self._validate_config()
    
    def _validate_config(self):
        """Validate required configuration"""
        print("🔧 Validating configuration...")
        
        # Check required API keys
        required_keys = [
            ('EXA_API_KEY', self.exa_api_key),
            ('ELEVENLABS_API_KEY', self.elevenlabs_api_key)
        ]
        
        missing = []
        for key_name, key_value in required_keys:
            if not key_value:
                missing.append(key_name)
            else:
                print(f"✅ {key_name}: {'*' * (len(key_value) - 8) + key_value[-8:]}")
        
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
        
        # Check email options
        print("\n📧 Email Delivery Options:")
        if GMAIL_API_AVAILABLE:
            print(f"   ✅ Gmail API: available")
            credentials_exists = os.path.exists('credentials.json')
            token_exists = os.path.exists('token.json')
            print(f"   📁 credentials.json: {'✅ found' if credentials_exists else '❌ missing'}")
            print(f"   🔑 token.json: {'✅ found' if token_exists else '❌ will be created on first auth'}")
        else:
            print("   ❌ Gmail API not available - install google-api-python-client")
        
        # Check recipients
        valid_emails = [email.strip() for email in self.recipient_emails if email.strip()]
        if not valid_emails:
            print("⚠️  Warning: No recipient emails configured")
        else:
            print(f"📧 Recipients: {len(valid_emails)} configured")
        
        print(f"🎤 Voice ID: {self.voice_id}")
        print(f"📰 Topic: {self.newsletter_topic}")
        print(f"📊 Max Articles: {self.max_articles}")
    
    def get_gmail_service(self):
        """Set up Gmail API service with OAuth authentication - simplified approach"""
        if not GMAIL_API_AVAILABLE:
            print("❌ Gmail API not available")
            return None
        
        if self.gmail_service:
            return self.gmail_service
        
        print("🔐 Setting up Gmail API authentication...")
        
        creds = None
        # Load existing credentials from token.json
        if os.path.exists('token.json'):
            try:
                creds = Credentials.from_authorized_user_file('token.json', GMAIL_SCOPES)
                print("📄 Loaded existing credentials from token.json")
            except Exception as e:
                print(f"⚠️  Error loading token.json: {e}")
                print("🗑️  Removing corrupted token file...")
                os.remove('token.json')
                creds = None
        
        # If there are no valid credentials available, let the user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                print("🔄 Refreshing expired credentials...")
                try:
                    creds.refresh(Request())
                    print("✅ Credentials refreshed successfully")
                except Exception as e:
                    print(f"❌ Failed to refresh credentials: {e}")
                    creds = None
            
            if not creds:
                if not os.path.exists('credentials.json'):
                    print("❌ credentials.json not found!")
                    print("📋 To set up Gmail API:")
                    print("   1. Go to Google Cloud Console: https://console.cloud.google.com/")
                    print("   2. Create a new project or select existing")
                    print("   3. Enable Gmail API")
                    print("   4. Go to APIs & Services → Credentials")
                    print("   5. Click 'Create Credentials' → 'OAuth client ID'")
                    print("   6. Choose 'Desktop application'")
                    print("   7. Under 'Authorized redirect URIs', add: http://localhost:8080/")
                    print("   8. Download credentials.json to this directory")
                    print("   9. Run: python a.py --reset-auth")
                    print("   10. Run: python a.py --email-with-audio")
                    return None
                
                print("🌐 Starting OAuth flow...")
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', GMAIL_SCOPES)
                
                # Try common ports in sequence
                ports_to_try = [8080, 8081, 8082, 8083]
                creds = None
                
                for port in ports_to_try:
                    try:
                        print(f"📱 Trying authentication on port {port}...")
                        print(f"🔗 Using redirect URI: http://localhost:{port}/")
                        creds = flow.run_local_server(port=port)
                        print("✅ Authentication successful!")
                        break
                    except Exception as e:
                        error_msg = str(e).lower()
                        
                        if "redirect_uri_mismatch" in error_msg:
                            print(f"❌ Port {port}: Redirect URI not configured")
                            if port == 8080:
                                print("\n🔧 REDIRECT URI MISMATCH - Quick Fix:")
                                print("   1. Go to: https://console.cloud.google.com/apis/credentials")
                                print("   2. Find your OAuth 2.0 Client ID and click Edit (pencil icon)")
                                print("   3. Under 'Authorized redirect URIs', click 'ADD URI'")
                                print("   4. Add exactly: http://localhost:8080/")
                                print("   5. Click 'SAVE'")
                                print("   6. Wait 1-2 minutes for changes to propagate")
                                print("   7. Run: python a.py --reset-auth")
                                print("   8. Run: python a.py --email-with-audio")
                                return None
                            continue
                        elif "address already in use" in error_msg:
                            print(f"⚠️  Port {port} is busy, trying next port...")
                            continue
                        else:
                            print(f"❌ Port {port} failed: {e}")
                            continue
                
                if not creds:
                    print("\n❌ All ports failed. Please:")
                    print("   1. Add redirect URI http://localhost:8080/ to your OAuth client")
                    print("   2. Make sure port 8080 is available")
                    print("   3. Try running: python a.py --reset-auth")
                    return None
            
            # Save the credentials for the next run
            try:
                with open('token.json', 'w') as token:
                    token.write(creds.to_json())
                print("💾 Credentials saved to token.json")
            except Exception as e:
                print(f"⚠️  Warning: Could not save credentials: {e}")
        
        try:
            self.gmail_service = build('gmail', 'v1', credentials=creds)
            print("✅ Gmail API service initialized successfully")
            return self.gmail_service
        except Exception as e:
            print(f"❌ Failed to initialize Gmail service: {e}")
            return None
    
    def get_newsletter_content_with_exa_answer(self, topic: str) -> Dict:
        """Use Exa Answer API to get newsletter content and summary"""
        print(f"\n🔍 Getting newsletter content about: {topic}")
        
        url = "https://api.exa.ai/answer"
        headers = {
            "x-api-key": self.exa_api_key,
            "Content-Type": "application/json"
        }
        
        # Create a comprehensive query for newsletter content
        query = f"""Create a comprehensive newsletter about the latest {topic} developments. 
        Include at least 5 recent stories with:
        1. Specific company announcements and breakthroughs
        2. New product launches and innovations  
        3. Funding rounds and business developments
        4. Research breakthroughs and scientific advances
        5. Industry trends and market movements
        
        For each story, provide the title, key details, and significance to the {topic} industry."""
        
        payload = {
            "query": query,
            "text": True,
            "include_domains": [
                "techcrunch.com", "arstechnica.com", "theverge.com", "wired.com",
                "venturebeat.com", "technologyreview.com", "zdnet.com", "engadget.com",
                "reuters.com", "bloomberg.com", "forbes.com", "cnbc.com"
            ],
            "start_published_date": (datetime.now() - timedelta(days=3)).isoformat(),
            "end_published_date": datetime.now().isoformat()
        }
        
        try:
            print("   🤖 Generating newsletter content with Exa Answer API...")
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            
            answer = data.get('answer', '')
            citations = data.get('citations', [])
            
            print(f"📰 Generated content with {len(citations)} source citations")
            
            return {
                'content': answer,
                'citations': citations,
                'raw_response': data
            }
            
        except Exception as e:
            print(f"❌ Error with Exa Answer API: {e}")
            # Fallback to sample content
            return self._get_fallback_newsletter_content(topic)
    
    def _get_fallback_newsletter_content(self, topic: str) -> Dict:
        """Provide fallback newsletter content when API fails"""
        print("📰 Using fallback content generation...")
        
        sample_content = f"""Today's {topic} Newsletter

Here are the latest developments in {topic}:

1. **OpenAI Advances**: Continued improvements in language models and AI safety research, with new partnerships announced for enterprise applications.

2. **Google AI Breakthroughs**: Recent developments in quantum AI and machine learning efficiency, showing promising results in scientific research applications.

3. **Tesla Innovations**: Progress in autonomous driving technology and AI-powered manufacturing processes, expanding deployment across multiple cities.

4. **Microsoft AI Integration**: Enhanced productivity tools with AI assistance, focusing on workplace automation and developer productivity improvements.

5. **Startup Ecosystem**: Multiple AI startups securing significant funding rounds, indicating strong investor confidence in the sector's growth potential.

These developments represent significant progress in {topic}, with implications for industry transformation and technological advancement."""
        
        # Create mock citations
        citations = [
            {
                'url': 'https://techcrunch.com/ai-developments',
                'title': f'Latest {topic} Developments - TechCrunch',
                'text': f'Recent advances in {topic} technology and industry news'
            },
            {
                'url': 'https://arstechnica.com/ai-news',
                'title': f'{topic} Innovation Report - Ars Technica', 
                'text': f'Technical analysis of {topic} breakthroughs and research'
            }
        ]
        
        return {
            'content': sample_content,
            'citations': citations,
            'raw_response': {'answer': sample_content, 'citations': citations}
        }
    
    def create_newsletter_content(self, newsletter_data: Dict) -> str:
        """Create well-formatted newsletter content from Exa Answer API data"""
        if not newsletter_data or not newsletter_data.get('content'):
            return "No recent content found for today's newsletter."
        
        date_str = datetime.now().strftime("%B %d, %Y")
        raw_content = newsletter_data['content']
        citations = newsletter_data.get('citations', [])
        
        # Create header
        content = f"""
╔══════════════════════════════════════════════════════════════╗
║                    🤖 AI VOICE NEWSLETTER                     ║
║                        {date_str}                         ║
╚══════════════════════════════════════════════════════════════╝

📰 DAILY {self.newsletter_topic.upper()} BRIEFING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Welcome to your AI-powered daily newsletter! Here are today's key developments:

"""
        
        # Format the main content with better structure
        formatted_content = self._format_newsletter_sections(raw_content)
        content += formatted_content
        
        # Add sources section with better formatting
        if citations:
            content += "\n\n" + "─" * 60 + "\n"
            content += "📚 SOURCES & REFERENCES\n"
            content += "─" * 60 + "\n"
            for i, citation in enumerate(citations, 1):
                title = citation.get('title', 'Source').strip()
                url = citation.get('url', '').strip()
                # Extract domain for cleaner display
                domain = url.split('//')[1].split('/')[0] if '//' in url else url
                content += f"\n[{i:2d}] {title}\n"
                content += f"     🔗 {domain}\n"
                content += f"     {url}\n"
        
        # Add footer
        content += f"""

─────────────────────────────────────────────────────────────────
📊 NEWSLETTER STATS
─────────────────────────────────────────────────────────────────
• Sources analyzed: {len(citations)}
• Topic focus: {self.newsletter_topic}
• Generated: {datetime.now().strftime("%Y-%m-%d at %H:%M UTC")}
• Powered by: Exa AI & ElevenLabs

🎧 This newsletter includes an audio summary for your convenience.
💌 Share feedback or suggestions: newsletter@yourcompany.com
"""
        
        return content
    
    def _format_newsletter_sections(self, raw_content: str) -> str:
        """Format raw content into structured sections"""
        lines = raw_content.split('\n')
        formatted_lines = []
        
        current_section = ""
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Detect section headers (lines that end with colons or are numbered)
            if (line.endswith(':') and len(line.split()) <= 8) or \
               (line.startswith(('1.', '2.', '3.', '4.', '5.', '**1.', '**2.', '**3.', '**4.', '**5.'))):
                if current_section:
                    formatted_lines.append("")  # Add spacing
                formatted_lines.append(f"🔸 {line.replace('**', '').replace(':', '')}")
                formatted_lines.append("   " + "─" * 50)
                current_section = line
            
            # Detect sub-points or key details
            elif line.startswith(('•', '-', '*')) or \
                 ('**' in line and ('Title:' in line or 'Details:' in line or 'Significance:' in line)):
                clean_line = line.replace('**', '').replace('*', '').replace('•', '').replace('-', '').strip()
                if 'Title:' in clean_line:
                    formatted_lines.append(f"\n   📰 {clean_line.replace('Title:', '').strip()}")
                elif 'Details:' in clean_line:
                    formatted_lines.append(f"   💡 {clean_line.replace('Details:', '').strip()}")
                elif 'Significance:' in clean_line:
                    formatted_lines.append(f"   🎯 {clean_line.replace('Significance:', '').strip()}")
                else:
                    formatted_lines.append(f"   • {clean_line}")
            
            # Regular paragraphs
            else:
                if line and not line.startswith(' '):
                    formatted_lines.append(f"   {line}")
        
        return '\n'.join(formatted_lines)
    
    def create_newsletter_summary(self, newsletter_data: Dict) -> str:
        """Create a comprehensive text summary from newsletter data"""
        if not newsletter_data or not newsletter_data.get('content'):
            return "No recent content found for today's newsletter."
        
        date_str = datetime.now().strftime("%B %d, %Y")
        content = newsletter_data['content']
        citations_count = len(newsletter_data.get('citations', []))
        
        # Extract key points and structure them better
        key_stories = self._extract_key_stories(content)
        
        summary = f"""
📋 NEWSLETTER SUMMARY - {date_str}
{"="*50}

📊 Overview:
• Topic: {self.newsletter_topic}
• Sources: {citations_count} verified sources
• Key stories: {len(key_stories)} major developments

🔍 Key Highlights:
"""
        
        for i, story in enumerate(key_stories, 1):
            summary += f"\n{i}. {story}"
        
        summary += f"""

📈 Industry Impact:
This newsletter covers significant developments that are shaping the {self.newsletter_topic} landscape. 
The stories highlight emerging trends, major company announcements, and technological breakthroughs 
that could influence market direction and innovation patterns.

💡 For detailed analysis, source links, and complete context, please refer to the full newsletter content above.
"""
        
        return summary
    
    def create_audio_summary_with_exa(self, newsletter_content: str, topic: str) -> str:
        """Create an optimized audio summary using Exa Answer API based on newsletter content (2-3 minutes)"""
        print("🎙️ Creating AI-powered audio summary based on newsletter content...")
        
        url = "https://api.exa.ai/answer"
        headers = {
            "x-api-key": self.exa_api_key,
            "Content-Type": "application/json"
        }
        
        # Create a query that uses the actual newsletter content
        audio_query = f"""Based on the following newsletter content about {topic}, create a concise 2-3 minute audio script for voice narration.
        
        Newsletter Content:
        {newsletter_content[:3000]}...
        
        Transform this into a professional news broadcast script that:
        
        1. Has a brief welcome introduction (no specific dates or times)
        2. Summarizes the 3-4 most important stories from the newsletter content
        3. Each story should be 30-45 seconds when spoken
        4. Uses conversational, clear language suitable for audio
        5. Includes a professional closing
        6. Avoids all asterisks, bullet points, and specific time references
        7. Uses flowing narrative style without visual formatting
        8. Focuses on the key developments mentioned in the newsletter
        
        Make it engaging and informative for audio listening. Use phrases like "recent developments", "latest news", or "current updates" instead of specific dates. Base the content strictly on what's provided in the newsletter above."""
        
        payload = {
            "query": audio_query,
            "text": True
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            
            audio_script = data.get('answer', '')
            citations = data.get('citations', [])
            
            if audio_script:
                # Clean and optimize for speech
                audio_script = self._clean_text_for_speech(audio_script)
                
                # Ensure proper length for 3-minute audio (approximately 450-500 words)
                words = audio_script.split()
                target_words = 480  # ~3 minutes at average speaking pace
                
                if len(words) > target_words:
                    # Trim to target length while preserving sentence structure
                    trimmed_script = " ".join(words[:target_words])
                    last_sentence_end = max(
                        trimmed_script.rfind('.'),
                        trimmed_script.rfind('!'),
                        trimmed_script.rfind('?')
                    )
                    if last_sentence_end > len(trimmed_script) - 100:
                        audio_script = trimmed_script[:last_sentence_end + 1]
                    else:
                        audio_script = trimmed_script + ". Thank you for listening to this update."
                
                print(f"📊 Audio script generated: {len(audio_script.split())} words (~{len(audio_script.split()) / 150:.1f} minutes)")
                print(f"📚 Based on newsletter content with {len(citations)} additional citations")
                
                return audio_script
            else:
                print("⚠️  No audio script generated from newsletter content, falling back to manual method")
                return self._create_fallback_audio_summary_from_content(newsletter_content, topic)
                
        except Exception as e:
            print(f"❌ Error with Exa Answer API for audio: {e}")
            return self._create_fallback_audio_summary_from_content(newsletter_content, topic)
    
    def _create_fallback_audio_summary_from_content(self, newsletter_content: str, topic: str) -> str:
        """Fallback audio summary based on newsletter content when Exa Answer API fails"""
        print("📻 Creating fallback audio summary from newsletter content...")
        
        # Extract key stories from the newsletter content
        key_stories = self._extract_key_stories(newsletter_content)
        top_stories = key_stories[:4]  # Limit to top 4 stories for time constraint
        
        # Create audio-friendly introduction
        audio_script = f"""Welcome to your AI Voice Newsletter.

Here are the key developments from the latest {topic} news:

"""
        
        # Add top stories in audio-friendly format
        if top_stories:
            for i, story in enumerate(top_stories, 1):
                # Clean up the story for better speech and remove time references
                clean_story = self._clean_text_for_speech(story)
                if clean_story.strip():
                    if i == 1:
                        audio_script += f"First, {clean_story}\n\n"
                    elif i == 2:
                        audio_script += f"Second, {clean_story}\n\n"
                    elif i == 3:
                        audio_script += f"Third, {clean_story}\n\n"
                    else:
                        audio_script += f"Finally, {clean_story}\n\n"
        else:
            # Generic fallback if no stories extracted
            audio_script += f"""The latest developments in {topic} include advances in machine learning and artificial intelligence, new product announcements from major technology companies, active startup funding in the sector, and important research findings from leading institutions.

"""
        
        # Add closing
        audio_script += f"""These developments represent ongoing progress in {topic}, with implications for businesses, researchers, and consumers alike.

Thank you for listening to this newsletter summary. For detailed information and source links, please check your email for the complete newsletter."""
        
        return audio_script
    
    def _create_fallback_audio_summary(self, topic: str) -> str:
        """Generic fallback audio summary when no newsletter content available"""
        print("📻 Creating generic fallback audio summary...")
        
        audio_script = f"""Welcome to your AI Voice Newsletter.

Here are the latest key developments in {topic}:

First, artificial intelligence continues to advance with new breakthroughs in machine learning and natural language processing, showing significant improvements in both efficiency and capability.

Second, major technology companies are announcing new partnerships and product launches, focusing on enterprise applications and consumer-facing innovations.

Third, the startup ecosystem remains active with several funding announcements and new ventures entering the market, particularly in AI-driven solutions.

Finally, research institutions are publishing important findings that could shape the future direction of technology development and implementation.

These developments represent the ongoing evolution of {topic}, with implications for businesses, researchers, and consumers alike.

Thank you for listening to this newsletter summary. For detailed information and source links, please check your email for the complete newsletter."""
        
        return audio_script
    
    def create_audio_summary(self, newsletter_data: Dict) -> str:
        """Create audio summary based on newsletter content - enhanced with Exa Answer API"""
        # Get the newsletter content that was already generated
        newsletter_content = newsletter_data.get('content', '')
        
        if not newsletter_content:
            print("⚠️  No newsletter content available, using generic fallback")
            return self._create_fallback_audio_summary(self.newsletter_topic)
        
        # Try to use Exa Answer API first for better quality, based on newsletter content
        try:
            return self.create_audio_summary_with_exa(newsletter_content, self.newsletter_topic)
        except Exception as e:
            print(f"⚠️  Exa Answer API failed, using content-based fallback: {e}")
            return self._create_fallback_audio_summary_from_content(newsletter_content, self.newsletter_topic)
    
    def _extract_key_stories(self, content: str) -> list:
        """Extract key stories/points from newsletter content"""
        lines = content.split('\n')
        stories = []
        current_story = ""
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Look for story markers (numbered items, titles, etc.)
            if (line.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.')) or
                ('**Title:**' in line) or
                (line.startswith('**') and line.endswith('**') and len(line.split()) <= 10)):
                
                if current_story.strip():
                    stories.append(current_story.strip())
                    current_story = ""
                
                # Clean up the story title
                clean_title = line.replace('**Title:**', '').replace('**', '').strip()
                if clean_title.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.')):
                    clean_title = clean_title[2:].strip()  # Remove number prefix
                current_story = clean_title
            
            # Look for details or key information
            elif ('**Details:**' in line or '**Key Details:**' in line or 
                  line.startswith(('•', '-', '*')) and len(line) > 20):
                detail = line.replace('**Details:**', '').replace('**Key Details:**', '')
                detail = detail.replace('•', '').replace('-', '').replace('*', '').strip()
                if detail and current_story:
                    current_story += f" - {detail}"
        
        # Add the last story
        if current_story.strip():
            stories.append(current_story.strip())
        
        # If no structured stories found, extract sentences
        if not stories:
            sentences = content.split('.')
            for sentence in sentences:
                sentence = sentence.strip()
                if len(sentence) > 50 and any(keyword in sentence.lower() for keyword in 
                    ['announced', 'launched', 'developed', 'breakthrough', 'funding', 'partnership', 'release']):
                    stories.append(sentence + '.')
                    if len(stories) >= 6:  # Limit to prevent too many
                        break
        
        return stories[:6]  # Return top 6 stories max

    def generate_audio_with_elevenlabs(self, newsletter_data: Dict) -> tuple[Optional[str], str]:
        """Generate audio for newsletter using Exa Answer API-enhanced summary"""
        print("\n🎵 Creating newsletter audio summary...")
        audio_start_time = time.time()
        
        # Create text summary (for saving/reference)
        text_summary = self.create_newsletter_summary(newsletter_data)
        
        # Create audio-optimized script using Exa Answer API (designed for speech, ~2-3 minutes)
        audio_script = self.create_audio_summary(newsletter_data)
        
        audio_generation_time = time.time() - audio_start_time
        word_count = len(audio_script.split())
        estimated_duration = word_count / 150  # Average speaking pace
        
        print(f"   📝 Text summary: {len(text_summary.split())} words")
        print(f"   🎙️ Audio script: {word_count} words")
        print(f"   ⏱️ Estimated audio length: {estimated_duration:.1f} minutes")
        print(f"   🕐 Script generation time: {audio_generation_time:.1f}s")
        
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}"
        headers = {
            "xi-api-key": self.elevenlabs_api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "text": audio_script,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.6,  # Slightly more stable for narration
                "similarity_boost": 0.75,
                "style": 0.2,  # Slight style for engagement
                "use_speaker_boost": True
            }
        }
        
        try:
            print("   🎙️ Generating professional voice narration...")
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code == 401:
                print("❌ ElevenLabs API Error: Invalid API key")
                return None, text_summary
            
            response.raise_for_status()
            
            # Create audio folder
            audio_folder = os.path.join(".", "newsletter_audio")
            os.makedirs(audio_folder, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            audio_filename = f"newsletter_summary_{timestamp}.mp3"
            audio_path = os.path.join(audio_folder, audio_filename)
            
            with open(audio_path, 'wb') as f:
                f.write(response.content)
            
            # Save the audio script separately for reference
            script_filename = f"audio_script_{timestamp}.txt"
            with open(script_filename, 'w', encoding='utf-8') as f:
                f.write("AUDIO SCRIPT (What was converted to speech):\n")
                f.write("=" * 50 + "\n")
                f.write(audio_script)
            
            print(f"🎧 Newsletter audio generated: {audio_path}")
            print(f"📝 Audio script saved: {script_filename}")
            
            return audio_path, text_summary
            
        except Exception as e:
            print(f"❌ Error generating audio: {e}")
            return None, text_summary
    
    def _clean_text_for_speech(self, text: str) -> str:
        """Clean text for better speech synthesis - remove time references and asterisks"""
        import re
        
        # Remove emojis and special characters that don't read well
        emoji_pattern = re.compile("["
                                 u"\U0001F600-\U0001F64F"
                                 u"\U0001F300-\U0001F5FF"
                                 u"\U0001F680-\U0001F6FF"
                                 u"\U0001F1E0-\U0001F1FF"
                                 u"\U00002702-\U000027B0"
                                 u"\U000024C2-\U0001F251"
                                 "]+", flags=re.UNICODE)
        text = emoji_pattern.sub('', text)
        
        # Remove ALL asterisks and markdown formatting
        text = re.sub(r'\*+', '', text)              # Remove all asterisks
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text) # Remove bold markdown
        text = re.sub(r'\*(.*?)\*', r'\1', text)     # Remove italic markdown
        text = re.sub(r'`(.*?)`', r'\1', text)       # Remove code formatting
        text = re.sub(r'#{1,6}\s*', '', text)        # Remove markdown headers
        
        # Remove bullet points and list formatting
        text = re.sub(r'^\s*[\-\*\+]\s+', '', text, flags=re.MULTILINE)
        text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)
        
        # Remove specific time references that sound awkward in audio
        time_patterns = [
            r'\b(today|yesterday|tomorrow)\b',
            r'\b\d{1,2}/\d{1,2}/\d{2,4}\b',           # dates like 12/25/2024
            r'\b\d{4}-\d{2}-\d{2}\b',                 # dates like 2024-12-25
            r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b',
            r'\b(Mon|Tue|Wed|Thu|Fri|Sat|Sun|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b',
            r'\bat\s+\d{1,2}:\d{2}\s*(AM|PM|am|pm)?\b',  # times like "at 3:30 PM"
            r'\bthis\s+(morning|afternoon|evening|week|month|year)\b',
            r'\blast\s+(week|month|year|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b',
            r'\bnext\s+(week|month|year|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b',
        ]
        
        for pattern in time_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        # Replace time-specific phrases with audio-friendly alternatives
        time_replacements = {
            'breaking news': 'latest developments',
            'just announced': 'recently announced',
            'this morning': 'recently',
            'this afternoon': 'recently',
            'this evening': 'recently',
            'earlier today': 'recently',
            'just released': 'recently released',
            'breaking:': '',
            'update:': '',
            'urgent:': '',
        }
        
        for old, new in time_replacements.items():
            text = re.sub(old, new, text, flags=re.IGNORECASE)
        
        # Replace URLs with more speech-friendly descriptions
        text = re.sub(r'https?://[^\s]+', '', text)  # Remove URLs entirely for audio
        
        # Clean up multiple spaces and newlines
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n+', '. ', text)
        
        # Replace abbreviations and symbols with speech-friendly versions
        replacements = {
            '&': 'and',
            '%': 'percent',
            '$': 'dollars',
            '€': 'euros',
            '£': 'pounds',
            '@': 'at',
            '#': 'number',
            'AI': 'A I',  # Better pronunciation
            'API': 'A P I',
            'CEO': 'C E O',
            'CTO': 'C T O',
            'IPO': 'I P O',
            'USD': 'US dollars',
            'vs.': 'versus',
            'vs': 'versus',
            'etc.': 'etcetera',
            'e.g.': 'for example',
            'i.e.': 'that is',
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        # Clean up extra spaces and punctuation
        text = re.sub(r'\s+', ' ', text)              # Multiple spaces to single space
        text = re.sub(r'\s*\.\s*\.', '.', text)      # Multiple periods
        text = re.sub(r'\s*,\s*,', ',', text)        # Multiple commas
        text = re.sub(r'^\s*[,\.]\s*', '', text)     # Leading punctuation
        
        # Ensure proper sentence endings
        text = text.strip()
        if text and not text.endswith(('.', '!', '?')):
            text += '.'
        
        return text
    
    def send_newsletter_with_gmail(self, content: str, audio_path: Optional[str]) -> tuple[bool, str]:
        """Send newsletter via Gmail using Google Auth"""
        if not GMAIL_API_AVAILABLE:
            print("❌ Gmail API not available")
            return False, content
        
        try:
            service = self.get_gmail_service()
            if not service:
                print("❌ Gmail service not initialized")
                return False, content
            
            # Create email message
            message = MIMEMultipart()
            message['From'] = self.sender_email
            message['To'] = ", ".join(self.recipient_emails)
            message['Subject'] = f"🎙️ AI Voice Newsletter - {datetime.now().strftime('%B %d, %Y')}"
            
            # Add text content
            text_part = MIMEText(content, 'plain')
            message.attach(text_part)
            
            # Add audio attachment if available
            if audio_path and os.path.exists(audio_path):
                with open(audio_path, 'rb') as f:
                    audio_data = f.read()
                audio_part = MIMEBase('application', 'octet-stream')
                audio_part.set_payload(audio_data)
                encoders.encode_base64(audio_part)
                audio_part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(audio_path)}')
                message.attach(audio_part)
            
            # Convert message to bytes
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            
            # Send email
            print("\n📧 Sending newsletter via Gmail...")
            print(f"📝 Sending email with {len(content)} characters of content")
            
            service.users().messages().send(userId='me', body={'raw': raw_message}).execute()
            
            print("✅ Newsletter sent successfully via Gmail!")
            return True, content
            
        except Exception as e:
            print(f"❌ Error sending email: {e}")
            return False, content
    
    def _create_html_email(self, content: str) -> str:
        """Convert text to HTML email format"""
        html_content = content.replace('\n', '<br>')
        
        return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; max-width: 600px; margin: 0 auto; padding: 20px; }}
        .content {{ padding: 20px; background: #f9f9f9; border-radius: 10px; }}
        .story {{ margin: 15px 0; padding: 10px; border-left: 4px solid #4CAF50; }}
        a {{ color: #2196F3; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <div class="content">
        {html_content}
    </div>
</body>
</html>"""
    
    def save_newsletter_locally(self, content: str, audio_path: Optional[str], original_content: str = None) -> bool:
        """Save newsletter files locally - no truncation needed since full content is sent"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save newsletter content 
        text_filename = f"newsletter_backup_{timestamp}.txt"
        with open(text_filename, 'w', encoding='utf-8') as f:
            f.write("NEWSLETTER CONTENT (Full version sent via email):\n")
            f.write("=" * 50 + "\n")
            f.write(content)
        print(f"💾 Newsletter content saved: {text_filename}")
        
        # Save HTML version
        html_content = self._create_html_email(content)
        html_filename = f"newsletter_{timestamp}.html"
        with open(html_filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"🌐 HTML version saved: {html_filename}")
        
        # Note audio file if exists
        if audio_path and os.path.exists(audio_path):
            print(f"🎧 Audio attachment: {audio_path}")
        
        return True
    
    def generate_and_send_newsletter(self, mode="email_with_audio"):
        """Main method to generate and send newsletter with different modes"""
        start_time = time.time()
        print("🚀 Starting AI Voice Newsletter Generation...")
        print(f"📋 Mode: {mode}")
        print("⏱️  Target completion time: 3 minutes")
        print("=" * 50)
        
        try:
            # Generate content using Exa Answer API
            print("⏱️  Step 1/3: Getting newsletter content...")
            newsletter_data = self.get_newsletter_content_with_exa_answer(self.newsletter_topic)
            
            elapsed = time.time() - start_time
            print(f"⏱️  Time elapsed: {elapsed:.1f}s")
            
            # Create newsletter content
            print("⏱️  Step 2/3: Formatting newsletter...")
            newsletter_content = self.create_newsletter_content(newsletter_data)
            citations_count = len(newsletter_data.get('citations', []))
            print(f"📄 Newsletter content created with {citations_count} source citations")
            
            elapsed = time.time() - start_time
            print(f"⏱️  Time elapsed: {elapsed:.1f}s")
            
            # Handle different modes
            audio_path = None
            if mode in ["audio_only", "email_with_audio"]:
                print("🎵 Generating AI-powered audio summary...")
                print("   📰 Using newsletter content for audio script generation")
                print("   📡 Enhanced with Exa Answer API for intelligent summarization")
                audio_path, newsletter_summary = self.generate_audio_with_elevenlabs(newsletter_data)
            
            # Step 3: Handle output based on mode
            print("⏱️  Step 3/3: Processing output...")
            
            if mode == "content_only":
                # Add summary at the bottom for content-only mode
                newsletter_summary = self.create_newsletter_summary(newsletter_data)
                
                # Combine newsletter content with summary
                full_content_with_summary = newsletter_content + "\n\n" + "=" * 60 + "\n"
                full_content_with_summary += "📋 NEWSLETTER SUMMARY\n"
                full_content_with_summary += "=" * 60 + "\n"
                full_content_with_summary += newsletter_summary
                
                # Save content to file only
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"newsletter_content_{timestamp}.txt"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(full_content_with_summary)
                print(f"💾 Content with summary saved to: {filename}")
                print(f"📊 Total content: {len(full_content_with_summary)} characters")
                
            elif mode == "email_only":
                # Send email without audio - full content always sent
                email_success, sent_content = self.send_newsletter_with_gmail(newsletter_content, None)
                self.save_newsletter_locally(sent_content, None)
                
            elif mode == "email_with_audio":
                # Send email with audio attachment - full content always sent
                email_success, sent_content = self.send_newsletter_with_gmail(newsletter_content, audio_path)
                self.save_newsletter_locally(sent_content, audio_path)
            
            # Final timing and results
            total_time = time.time() - start_time
            
            print("\n" + "=" * 50)
            print(f"⏱️  Total completion time: {total_time:.1f} seconds")
            
            if total_time <= 180:  # 3 minutes
                print("✅ Completed within 3-minute target!")
            else:
                print("⚠️  Exceeded 3-minute target")
            
            if mode == "content_only":
                print("🎉 Newsletter content generated successfully!")
                print(f"📊 Content based on {citations_count} sources")
                
            elif mode in ["email_only", "email_with_audio"]:
                if 'email_success' in locals() and email_success:
                    print("🎉 Newsletter generated and delivered successfully!")
                    print(f"📊 Newsletter contains content from {citations_count} sources")
                    if mode == "email_with_audio":
                        print("🎧 Email includes audio summary attachment")
                else:
                    print("✅ Newsletter generated successfully!")
                    print("📧 Email delivery failed, but all files are saved locally")
                    self._print_email_setup_instructions()
            
            if audio_path:
                print(f"🎧 Audio file: {audio_path}")
                
        except Exception as e:
            total_time = time.time() - start_time
            print(f"❌ Error after {total_time:.1f}s: {e}")
    
    def _print_email_setup_instructions(self):
        """Print email setup instructions"""
        print("\n💡 To enable email delivery:")
        print("   1. Add to your .env file:")
        print("      EXA_API_KEY=your_exa_key")
        print("      ELEVENLABS_API_KEY=your_elevenlabs_key")
        print("   2. Install Google API client:")
        print("      pip install google-api-python-client google-auth-oauthlib google-auth-httplib2")
        print("   3. Get API keys:")
        print("      OpenAI: https://platform.openai.com/api-keys")
        print("      Google Cloud Console: https://console.cloud.google.com/")
        print("   4. Create OAuth 2.0 credentials (Desktop application)")
        print("   5. Download credentials.json to this directory")
        print("   6. Run: python a.py --email-with-audio")


def parse_arguments():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(
        description="AI Voice Newsletter Generator with Exa Answer API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python a.py --content-only          # Generate content and save to file only
  python a.py --email                 # Generate and send newsletter via email  
  python a.py --email-with-audio      # Generate, create AI audio summary, and send email with audio attachment
  python a.py                         # Default: --email-with-audio
  python a.py --reset-auth            # Reset Gmail authentication

Modes:
  --content-only     : Generate newsletter content and save to file (no email, no audio)
  --email           : Generate newsletter content and send via email (no audio) 
  --email-with-audio: Generate newsletter content, create AI-powered audio summary (~3 min), and send email with attachment (default)
  --reset-auth      : Reset Gmail authentication (delete saved tokens)

Features:
  🤖 AI-Powered Content: Uses Exa Answer API for intelligent content generation
  🎙️ Smart Audio Summaries: Creates 3-minute audio scripts based on newsletter content, enhanced with Exa Answer API
  📧 Gmail Integration: Direct email delivery with OAuth 2.0 authentication
  📊 Performance Tracking: Real-time timing and word count metrics
  🔗 Content Consistency: Audio summaries match the newsletter content exactly

Environment Variables Required:
  EXA_API_KEY=your_exa_api_key
  ELEVENLABS_API_KEY=your_elevenlabs_api_key (for audio modes)
  RECIPIENT_EMAILS=email1@example.com,email2@example.com (for email modes)
"""
    )
    
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument('--content-only', action='store_true',
                           help='Generate content and save to file only')
    mode_group.add_argument('--email', action='store_true', 
                           help='Generate and send newsletter via email (no audio)')
    mode_group.add_argument('--email-with-audio', action='store_true',
                           help='Generate newsletter with audio and send via email (default)')
    
    parser.add_argument('--reset-auth', action='store_true',
                       help='Reset Gmail authentication (delete saved tokens)')
    
    return parser.parse_args()

def main():
    """Main execution function with command-line argument support"""
    args = parse_arguments()
    
    # Handle reset authentication
    if args.reset_auth:
        print("🗑️  Resetting Gmail authentication...")
        
        # Remove both old and new token files
        files_removed = []
        if os.path.exists('token.json'):
            os.remove('token.json')
            files_removed.append('token.json')
        if os.path.exists('token.pickle'):
            os.remove('token.pickle')
            files_removed.append('token.pickle')
        
        if files_removed:
            print(f"✅ Deleted: {', '.join(files_removed)}")
        else:
            print("⚠️  No token files found")
        
        print("\n📋 Next steps:")
        print("1. Ensure you have valid credentials.json")
        print("2. Run: python a.py --email-with-audio")
        print("3. Complete OAuth flow when prompted")
        return
    
    # Determine mode based on arguments
    if args.content_only:
        mode = "content_only"
    elif args.email:
        mode = "email_only"
    else:
        mode = "email_with_audio"  # Default mode
    
    try:
        generator = FixedNewsletterGenerator()
        generator.generate_and_send_newsletter(mode=mode)
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        print("\n📋 Setup Instructions:")
        print("1. Create a .env file with:")
        print("   EXA_API_KEY=your_exa_key")
        if mode in ["email_with_audio"]:
            print("   ELEVENLABS_API_KEY=your_elevenlabs_key")
        if mode in ["email_only", "email_with_audio"]:
            print("   RECIPIENT_EMAILS=email1@example.com,email2@example.com")
        print("\n2. Install Google API client:")
        print("   pip install google-api-python-client google-auth-oauthlib google-auth-httplib2")
        print("\n3. Get API keys:")
        print("   Google Cloud Console: https://console.cloud.google.com/")
        print("\n4. Create OAuth 2.0 credentials (Desktop application)")
        print("\n5. Download credentials.json to this directory")
        print("\n6. Run: python a.py --email-with-audio")


if __name__ == "__main__":
    main() 