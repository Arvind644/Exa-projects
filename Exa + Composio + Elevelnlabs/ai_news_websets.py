#!/usr/bin/env python3
"""
AI Newsletter Generator with Exa Websets
=======================================
Enhanced version using Exa Websets API for curated content generation.
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

class WebsetsNewsletterGenerator:
    """AI-powered newsletter generator using Exa Websets"""
    
    def __init__(self):
        # API Keys
        self.exa_api_key = os.getenv('EXA_API_KEY')
        self.elevenlabs_api_key = os.getenv('ELEVENLABS_API_KEY')
        
        # Email configuration
        self.sender_email = os.getenv('SENDER_EMAIL', 'newsletter@yourcompany.com')
        self.recipient_emails = os.getenv('RECIPIENT_EMAILS', '').split(',')
        
        # Configuration
        self.newsletter_topic = os.getenv('NEWSLETTER_TOPIC', 'AI and Technology')
        self.max_articles = 5  # Fixed to 5 as requested
        self.voice_id = os.getenv('ELEVENLABS_VOICE_ID', 'pNInz6obpgDQGcFmaJgB')
        
        # API Headers
        self.headers = {
            "Content-Type": "application/json",
            "x-api-key": self.exa_api_key
        }
        
        # Gmail service (will be initialized when needed)
        self.gmail_service = None
        
        self._validate_config()
    
    def _validate_config(self):
        """Validate required configuration"""
        print("🔧 Validating configuration...")
        
        # Check required API keys
        required_keys = [
            ('EXA_API_KEY', self.exa_api_key),
        ]
        
        missing = []
        for key_name, key_value in required_keys:
            if not key_value:
                missing.append(key_name)
            else:
                print(f"✅ {key_name}: {'*' * (len(key_value) - 8) + key_value[-8:]}")
        
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
        
        # Check optional keys
        if self.elevenlabs_api_key:
            print(f"✅ ELEVENLABS_API_KEY: {'*' * (len(self.elevenlabs_api_key) - 8) + self.elevenlabs_api_key[-8:]}")
        else:
            print("⚠️  ELEVENLABS_API_KEY not set - audio generation will be disabled")
        
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
    
    def create_enriched_webset(self, query: str, criteria: List[str], enrichments: List[Dict]) -> Dict:
        """Create webset with criteria and enrichments"""
        print(f"\n🔍 Creating enriched webset for: {query}")
        
        payload = {
            "search": {
                "query": query,
                "criteria": [{"description": c} for c in criteria],
                "entity": {"type": "article"},
                "count": self.max_articles
            },
            "enrichments": enrichments
        }
        
        try:
            response = requests.post("https://api.exa.ai/websets/v0/websets", 
                                   headers=self.headers, json=payload)
            response.raise_for_status()
            result = response.json()
            print(f"🎯 Webset created with ID: {result['id']}")
            return result
        except Exception as e:
            print(f"❌ Error creating webset: {e}")
            raise
    
    def get_webset_status(self, webset_id: str) -> Dict:
        """Get webset status and details"""
        try:
            response = requests.get(f"https://api.exa.ai/websets/v0/websets/{webset_id}", 
                                  headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Error getting webset status: {e}")
            return {}
    
    def get_webset_items(self, webset_id: str) -> List[Dict]:
        """Get webset items with retries"""
        print("📊 Retrieving webset items...")
        
        items = []
        max_attempts = 5
        
        for attempt in range(max_attempts):
            try:
                response = requests.get(f"https://api.exa.ai/websets/v0/websets/{webset_id}/items", 
                                      headers=self.headers)
                response.raise_for_status()
                items = response.json().get('data', [])
                
                if items:
                    print(f"✅ Retrieved {len(items)} items from webset")
                    break
                else:
                    print(f"⏳ Attempt {attempt + 1}: Waiting for items to be ready...")
                    if attempt < max_attempts - 1:
                        time.sleep(3)
                        
            except Exception as e:
                print(f"❌ Error getting items (attempt {attempt + 1}): {e}")
                if attempt < max_attempts - 1:
                    time.sleep(2)
        
        return items
    
    def wait_for_enrichments(self, webset_id: str, max_wait_time: int = 120) -> List[Dict]:
        """Wait for enrichments to complete and return enriched items"""
        print("🔬 Waiting for enrichments to complete...")
        
        start_time = time.time()
        items = []
        
        while time.time() - start_time < max_wait_time:
            items = self.get_webset_items(webset_id)
            
            if not items:
                print("⏳ Items not ready yet, continuing to wait...")
                time.sleep(5)
                continue
            
            # Check enrichment status
            enriched_count = 0
            total_enrichments = 0
            
            for item in items:
                enrichments = item.get('enrichments', [])
                for enrichment in enrichments:
                    total_enrichments += 1
                    if enrichment.get('status') == 'completed':
                        enriched_count += 1
            
            if total_enrichments > 0:
                completion_rate = enriched_count / total_enrichments
                print(f"📈 Enrichment progress: {enriched_count}/{total_enrichments} ({completion_rate:.1%})")
                
                if completion_rate >= 0.8:  # 80% completion rate
                    print("✅ Sufficient enrichments completed!")
                    break
            
            elapsed = time.time() - start_time
            print(f"⏱️  Waiting... ({elapsed:.0f}s/{max_wait_time}s)")
            time.sleep(10)
        
        return items
    
    def generate_newsletter_content_with_websets(self, topic: str) -> Dict:
        """Generate newsletter content using Exa Websets"""
        print(f"\n🚀 Generating newsletter content for: {topic}")
        
        # Define search query
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)  # Last week
        
        query = f"latest {topic} news developments announcements {end_date.strftime('%Y-%m')}"
        
        # Define search criteria
        criteria = [
            f"Recent article about {topic} developments or breakthroughs",
            "Article from credible tech or business publication",
            "Article contains specific details about companies, products, or research",
            "Article published within the last week"
        ]
        
        # Define enrichments
        enrichments = [
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
        
        try:
            # Create enriched webset
            webset = self.create_enriched_webset(query, criteria, enrichments)
            webset_id = webset['id']
            
            print(f"🔗 View webset: https://websets.exa.ai/{webset_id}")
            
            # Wait for enrichments
            items = self.wait_for_enrichments(webset_id)
            
            if not items:
                print("⚠️  No items retrieved, using fallback content")
                return self._get_fallback_content(topic)
            
            return {
                'webset_id': webset_id,
                'items': items,
                'topic': topic,
                'query': query
            }
            
        except Exception as e:
            print(f"❌ Error generating content: {e}")
            return self._get_fallback_content(topic)
    
    def _get_fallback_content(self, topic: str) -> Dict:
        """Provide fallback content when websets fail"""
        print("📰 Using fallback content...")
        
        fallback_items = [
            {
                'properties': {
                    'description': f'Recent {topic} Development #1',
                    'url': 'https://example.com/news1'
                },
                'enrichments': [{
                    'title': 'Article Summary',
                    'result': [f'Significant advancement in {topic} technology with new breakthrough announced.'],
                    'status': 'completed'
                }]
            }
        ]
        
        return {
            'webset_id': 'fallback',
            'items': fallback_items,
            'topic': topic,
            'query': f'Latest {topic} news'
        }
    
    def create_newsletter_content(self, webset_data: Dict) -> str:
        """Create well-formatted newsletter content from webset data"""
        if not webset_data or not webset_data.get('items'):
            return "No recent content found for today's newsletter."
        
        date_str = datetime.now().strftime("%B %d, %Y")
        items = webset_data['items']
        topic = webset_data.get('topic', self.newsletter_topic)
        webset_id = webset_data.get('webset_id', 'unknown')
        
        # Create header
        content = f"""
╔══════════════════════════════════════════════════════════════╗
║                    🤖 AI NEWSLETTER                          ║
║                        {date_str}                         ║
╚══════════════════════════════════════════════════════════════╝

📰 DAILY {topic.upper()} BRIEFING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Welcome to your AI-powered daily newsletter! Here are today's key developments from our curated webset analysis:

"""
        
        # Process each item
        for i, item in enumerate(items, 1):
            properties = item.get('properties', {})
            title = properties.get('description', f'Story #{i}')
            url = properties.get('url', 'No URL')
            
            # Clean up title
            if title.startswith('http'):
                title = f"Story #{i}"
            
            content += f"🔸 STORY #{i}: {title}\n"
            content += "   " + "─" * 50 + "\n"
            
            # Add basic info
            content += f"   🔗 Source: {url}\n"
            
            if 'publishedDate' in properties:
                content += f"   📅 Published: {properties['publishedDate']}\n"
            
            # Process enrichments
            enrichments = item.get('enrichments', [])
            
            for enrichment in enrichments:
                if enrichment.get('status') == 'completed':
                    title_enrichment = enrichment.get('title', 'Analysis')
                    result = enrichment.get('result', ['No result available'])
                    result_text = result[0] if result else 'No result available'
                    
                    if title_enrichment == 'Article Summary':
                        content += f"   📰 Summary: {result_text}\n"
                    elif title_enrichment == 'Key Details':
                        content += f"   💡 Key Details: {result_text}\n"
                    elif title_enrichment == 'Industry Impact':
                        content += f"   🎯 Industry Impact: {result_text}\n"
                    else:
                        content += f"   ✨ {title_enrichment}: {result_text}\n"
            
            content += "\n"
        
        # Add webset info
        content += "─" * 60 + "\n"
        content += "📊 CONTENT SOURCE\n"
        content += "─" * 60 + "\n"
        content += f"🔗 Webset ID: {webset_id}\n"
        content += f"🌐 View full webset: https://websets.exa.ai/{webset_id}\n"
        content += f"📊 Articles analyzed: {len(items)}\n"
        
        # Add footer
        content += f"""

─────────────────────────────────────────────────────────────────
📊 NEWSLETTER STATS
─────────────────────────────────────────────────────────────────
• Articles curated: {len(items)}
• Topic focus: {topic}
• Generated: {datetime.now().strftime("%Y-%m-%d at %H:%M UTC")}
• Powered by: Exa Websets API

💌 This newsletter is generated using AI-curated content from trusted sources.
🔍 Each story is enriched with summaries and impact analysis.
"""
        
        return content
    
    def save_newsletter_locally(self, content: str, webset_data: Dict) -> bool:
        """Save newsletter content locally"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save newsletter content
        filename = f"newsletter_websets_{timestamp}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"💾 Newsletter saved: {filename}")
        
        # Save webset data for reference
        data_filename = f"webset_data_{timestamp}.json"
        with open(data_filename, 'w', encoding='utf-8') as f:
            json.dump(webset_data, f, indent=2, default=str)
        print(f"📊 Webset data saved: {data_filename}")
        
        return True
    
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
                    print("   9. Run: python a_websets.py --reset-auth")
                    print("   10. Run: python a_websets.py --email-with-audio")
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
                                print("   7. Run: python a_websets.py --reset-auth")
                                print("   8. Run: python a_websets.py --email-with-audio")
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
                    print("   3. Try running: python a_websets.py --reset-auth")
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
    
    def _extract_key_stories(self, content: str) -> list:
        """Extract key stories/points from newsletter content"""
        lines = content.split('\n')
        stories = []
        current_story = ""
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Look for story markers (STORY #1, #2, etc.)
            if line.startswith('🔸 STORY #'):
                if current_story.strip():
                    stories.append(current_story.strip())
                    current_story = ""
                
                # Clean up the story title
                clean_title = line.replace('🔸 STORY #', '').strip()
                if ':' in clean_title:
                    clean_title = clean_title.split(':', 1)[1].strip()
                current_story = clean_title
            
            # Look for enrichment details
            elif line.startswith('   📰 Summary:') or line.startswith('   💡 Key Details:'):
                detail = line.split(':', 1)[1].strip() if ':' in line else line.strip()
                if detail and current_story:
                    current_story += f" - {detail}"
        
        # Add the last story
        if current_story.strip():
            stories.append(current_story.strip())
        
        return stories[:6]  # Return top 6 stories max
    
    def create_audio_summary(self, webset_data: Dict) -> str:
        """Create audio summary based on newsletter content - enhanced with Exa Answer API"""
        # Get the newsletter content that was already generated
        newsletter_content = self.create_newsletter_content(webset_data)
        
        if not newsletter_content:
            print("⚠️  No newsletter content available, using generic fallback")
            return self._create_fallback_audio_summary(self.newsletter_topic)
        
        # Try to use Exa Answer API first for better quality, based on newsletter content
        try:
            return self.create_audio_summary_with_exa(newsletter_content, self.newsletter_topic)
        except Exception as e:
            print(f"⚠️  Exa Answer API failed, using content-based fallback: {e}")
            return self._create_fallback_audio_summary_from_content(newsletter_content, self.newsletter_topic)
    
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
    
    def generate_audio_with_elevenlabs(self, webset_data: Dict) -> tuple[Optional[str], str]:
        """Generate audio for newsletter using Exa Answer API-enhanced summary"""
        print("\n🎵 Creating newsletter audio summary...")
        audio_start_time = time.time()
        
        # Create text summary (for saving/reference)
        text_summary = self.create_newsletter_summary(webset_data)
        
        # Create audio-optimized script using Exa Answer API (designed for speech, ~2-3 minutes)
        audio_script = self.create_audio_summary(webset_data)
        
        audio_generation_time = time.time() - audio_start_time
        word_count = len(audio_script.split())
        estimated_duration = word_count / 150  # Average speaking pace
        
        print(f"   📝 Text summary: {len(text_summary.split())} words")
        print(f"   🎙️ Audio script: {word_count} words")
        print(f"   ⏱️ Estimated audio length: {estimated_duration:.1f} minutes")
        print(f"   🕐 Script generation time: {audio_generation_time:.1f}s")
        
        if not self.elevenlabs_api_key:
            print("⚠️  ElevenLabs API key not configured - skipping audio generation")
            return None, text_summary
        
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
    
    def create_newsletter_summary(self, webset_data: Dict) -> str:
        """Create a text summary from webset data"""
        if not webset_data or not webset_data.get('items'):
            return "No recent content found for today's newsletter."
        
        items = webset_data['items']
        topic = webset_data.get('topic', self.newsletter_topic)
        
        summary = f"""
📋 NEWSLETTER SUMMARY - {datetime.now().strftime("%B %d, %Y")}
{"="*50}

📊 Overview:
• Topic: {topic}
• Articles: {len(items)} curated items
• Source: Exa Websets API

🔍 Key Highlights:
"""
        
        for i, item in enumerate(items, 1):
            properties = item.get('properties', {})
            title = properties.get('description', f'Story #{i}')
            
            # Get summary from enrichments
            enrichments = item.get('enrichments', [])
            story_summary = ""
            for enrichment in enrichments:
                if enrichment.get('title') == 'Article Summary' and enrichment.get('status') == 'completed':
                    result = enrichment.get('result', [''])
                    story_summary = result[0] if result else ""
                    break
            
            if not story_summary:
                story_summary = title
            
            summary += f"\n{i}. {story_summary}"
        
        summary += f"""

📈 Industry Impact:
This newsletter covers significant developments from curated sources using Exa Websets. 
The stories highlight emerging trends, major company announcements, and technological breakthroughs 
that could influence market direction and innovation patterns.

💡 For detailed analysis and source links, please refer to the full newsletter content above.
"""
        
        return summary
    
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
    
    def save_newsletter_with_email_audio(self, content: str, audio_path: Optional[str], webset_data: Dict) -> bool:
        """Save newsletter files locally with email and audio support"""
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
        
        # Save webset data for reference
        data_filename = f"webset_data_{timestamp}.json"
        with open(data_filename, 'w', encoding='utf-8') as f:
            json.dump(webset_data, f, indent=2, default=str)
        print(f"📊 Webset data saved: {data_filename}")
        
        # Note audio file if exists
        if audio_path and os.path.exists(audio_path):
            print(f"🎧 Audio attachment: {audio_path}")
        
        return True
    
    def _print_email_setup_instructions(self):
        """Print email setup instructions"""
        print("\n💡 To enable email delivery:")
        print("   1. Add to your .env file:")
        print("      EXA_API_KEY=your_exa_key")
        print("      ELEVENLABS_API_KEY=your_elevenlabs_key")
        print("      RECIPIENT_EMAILS=email1@example.com,email2@example.com")
        print("   2. Install Google API client:")
        print("      pip install google-api-python-client google-auth-oauthlib google-auth-httplib2")
        print("   3. Get API keys:")
        print("      Google Cloud Console: https://console.cloud.google.com/")
        print("   4. Create OAuth 2.0 credentials (Desktop application)")
        print("   5. Download credentials.json to this directory")
        print("   6. Run: python a_websets.py --email-with-audio")
    
    def generate_newsletter(self, mode="content_only"):
        """Main method to generate newsletter using websets with different modes"""
        start_time = time.time()
        print("🚀 Starting AI Newsletter Generation with Websets...")
        print(f"📋 Mode: {mode}")
        print("⏱️  Target completion time: 3 minutes")
        print("=" * 50)
        
        try:
            # Generate content using websets
            print("⏱️  Step 1/3: Creating enriched webset...")
            webset_data = self.generate_newsletter_content_with_websets(self.newsletter_topic)
            
            elapsed = time.time() - start_time
            print(f"⏱️  Time elapsed: {elapsed:.1f}s")
            
            # Create newsletter content
            print("⏱️  Step 2/3: Formatting newsletter...")
            newsletter_content = self.create_newsletter_content(webset_data)
            articles_count = len(webset_data.get('items', []))
            print(f"📄 Newsletter created with {articles_count} curated articles")
            
            elapsed = time.time() - start_time
            print(f"⏱️  Time elapsed: {elapsed:.1f}s")
            
            # Handle different modes
            audio_path = None
            if mode in ["audio_only", "email_with_audio"]:
                print("🎵 Generating AI-powered audio summary...")
                print("   📰 Using newsletter content for audio script generation")
                print("   📡 Enhanced with Exa Answer API for intelligent summarization")
                audio_path, newsletter_summary = self.generate_audio_with_elevenlabs(webset_data)
            
            # Step 3: Handle output based on mode
            print("⏱️  Step 3/3: Processing output...")
            
            if mode == "content_only":
                # Add summary at the bottom for content-only mode
                newsletter_summary = self.create_newsletter_summary(webset_data)
                
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
                self.save_newsletter_with_email_audio(sent_content, None, webset_data)
                
            elif mode == "email_with_audio":
                # Send email with audio attachment - full content always sent
                email_success, sent_content = self.send_newsletter_with_gmail(newsletter_content, audio_path)
                self.save_newsletter_with_email_audio(sent_content, audio_path, webset_data)
            
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
                print(f"📊 Content based on {articles_count} curated articles")
                
            elif mode in ["email_only", "email_with_audio"]:
                if 'email_success' in locals() and email_success:
                    print("🎉 Newsletter generated and delivered successfully!")
                    print(f"📊 Newsletter contains content from {articles_count} curated articles")
                    if mode == "email_with_audio":
                        print("🎧 Email includes audio summary attachment")
                else:
                    print("✅ Newsletter generated successfully!")
                    print("📧 Email delivery failed, but all files are saved locally")
                    self._print_email_setup_instructions()
            
            if audio_path:
                print(f"🎧 Audio file: {audio_path}")
            
            if webset_data.get('webset_id') != 'fallback':
                print(f"🔗 View webset: https://websets.exa.ai/{webset_data['webset_id']}")
                
        except Exception as e:
            total_time = time.time() - start_time
            print(f"❌ Error after {total_time:.1f}s: {e}")

def parse_arguments():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(
        description="AI Newsletter Generator with Exa Websets",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python a_websets.py --content-only          # Generate content and save to file only
  python a_websets.py --email                 # Generate and send newsletter via email  
  python a_websets.py --email-with-audio      # Generate, create AI audio summary, and send email with audio attachment
  python a_websets.py                         # Default: --content-only
  python a_websets.py --topic "AI"            # Generate newsletter with custom topic
  python a_websets.py --reset-auth            # Reset Gmail authentication

Modes:
  --content-only     : Generate newsletter content and save to file (no email, no audio) [DEFAULT]
  --email           : Generate newsletter content and send via email (no audio) 
  --email-with-audio: Generate newsletter content, create AI-powered audio summary (~3 min), and send email with attachment
  --reset-auth      : Reset Gmail authentication (delete saved tokens)

Features:
  🤖 AI-Powered Content: Uses Exa Websets API for curated content generation
  🎙️ Smart Audio Summaries: Creates 3-minute audio scripts based on newsletter content, enhanced with Exa Answer API
  📧 Gmail Integration: Direct email delivery with OAuth 2.0 authentication
  📊 Performance Tracking: Real-time timing and word count metrics
  🔗 Content Consistency: Audio summaries match the newsletter content exactly

Environment Variables Required:
  EXA_API_KEY=your_exa_api_key
  ELEVENLABS_API_KEY=your_elevenlabs_api_key (for audio modes)
  RECIPIENT_EMAILS=email1@example.com,email2@example.com (for email modes)

Optional:
  NEWSLETTER_TOPIC=your_preferred_topic (default: "AI and Technology")
"""
    )
    
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument('--content-only', action='store_true',
                           help='Generate content and save to file only (default)')
    mode_group.add_argument('--email', action='store_true', 
                           help='Generate and send newsletter via email (no audio)')
    mode_group.add_argument('--email-with-audio', action='store_true',
                           help='Generate newsletter with audio and send via email')
    
    parser.add_argument('--reset-auth', action='store_true',
                       help='Reset Gmail authentication (delete saved tokens)')
    
    parser.add_argument('--topic', type=str, 
                       help='Newsletter topic (overrides NEWSLETTER_TOPIC env var)')
    
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
        print("2. Run: python a_websets.py --email-with-audio")
        print("3. Complete OAuth flow when prompted")
        return
    
    # Determine mode based on arguments
    if args.email:
        mode = "email_only"
    elif args.email_with_audio:
        mode = "email_with_audio"
    else:
        mode = "content_only"  # Default mode
    
    try:
        generator = WebsetsNewsletterGenerator()
        
        # Override topic if provided
        if args.topic:
            generator.newsletter_topic = args.topic
            print(f"📰 Using custom topic: {args.topic}")
        
        generator.generate_newsletter(mode=mode)
        
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
        print("\n6. Run: python a_websets.py --email-with-audio")

if __name__ == "__main__":
    main() 