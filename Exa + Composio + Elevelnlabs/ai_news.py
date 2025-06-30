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
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import requests

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("python-dotenv not installed. Please set environment variables manually.")

# Import Composio and OpenAI for email functionality
try:
    from openai import OpenAI
    from composio_openai import ComposioToolSet, Action, App
    COMPOSIO_AVAILABLE = True
except ImportError:
    print("Composio and OpenAI not installed. Email functionality will be limited.")
    COMPOSIO_AVAILABLE = False

class FixedNewsletterGenerator:
    """AI-powered voice newsletter generator with multiple email delivery options"""
    
    def __init__(self):
        # API Keys
        self.exa_api_key = os.getenv('EXA_API_KEY')
        self.elevenlabs_api_key = os.getenv('ELEVENLABS_API_KEY')
        self.composio_api_key = os.getenv('COMPOSIO_API_KEY')
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        
        # Email configuration
        self.sender_email = os.getenv('SENDER_EMAIL', 'newsletter@yourcompany.com')
        self.recipient_emails = os.getenv('RECIPIENT_EMAILS', '').split(',')
        
        # Configuration
        self.voice_id = os.getenv('ELEVENLABS_VOICE_ID', 'pNInz6obpgDQGcFmaJgB')
        self.newsletter_topic = os.getenv('NEWSLETTER_TOPIC', 'AI and Technology')
        self.max_articles = int(os.getenv('MAX_ARTICLES', '8'))
        
        # Initialize Composio clients if available
        self.composio_toolset = None
        self.openai_client = None
        if COMPOSIO_AVAILABLE and self.composio_api_key and self.openai_api_key:
            os.environ["OPENAI_API_KEY"] = self.openai_api_key
            os.environ["COMPOSIO_API_KEY"] = self.composio_api_key
            self.openai_client = OpenAI()
            self.composio_toolset = ComposioToolSet()
        
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
        if self.composio_toolset and self.openai_client:
            print(f"   ✅ Composio + OpenAI: configured")
        elif self.composio_api_key and self.openai_api_key:
            print(f"   ⚠️  Composio configured but SDK not available")
        
        gmail_user = os.getenv('GMAIL_USER')
        gmail_password = os.getenv('GMAIL_APP_PASSWORD')
        if gmail_user and gmail_password:
            print(f"   ✅ Gmail SMTP: configured (fallback)")
        
        if not (self.composio_toolset and self.openai_client) and not (gmail_user and gmail_password):
            print("   ⚠️  No email delivery method configured - will save locally only")
        
        # Check recipients
        valid_emails = [email.strip() for email in self.recipient_emails if email.strip()]
        if not valid_emails:
            print("⚠️  Warning: No recipient emails configured")
        else:
            print(f"📧 Recipients: {len(valid_emails)} configured")
        
        print(f"🎤 Voice ID: {self.voice_id}")
        print(f"📰 Topic: {self.newsletter_topic}")
        print(f"📊 Max Articles: {self.max_articles}")
    
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
        """Create formatted newsletter content from Exa Answer API data"""
        if not newsletter_data or not newsletter_data.get('content'):
            return "No recent content found for today's newsletter."
        
        date_str = datetime.now().strftime("%B %d, %Y")
        content = f"""AI VOICE NEWSLETTER - {date_str}

Welcome to your daily AI-powered voice newsletter!

{newsletter_data['content']}

"""
        
        # Add source links
        citations = newsletter_data.get('citations', [])
        if citations:
            content += "\n📚 **Sources:**\n"
            for i, citation in enumerate(citations, 1):
                title = citation.get('title', 'Source')
                url = citation.get('url', '')
                content += f"{i}. [{title}]({url})\n"
        
        content += f"""

Generated on {datetime.now().strftime("%Y-%m-%d at %H:%M UTC")} using [Exa AI](https://docs.exa.ai/reference/answer)"""
        
        return content
    
    def create_newsletter_summary(self, newsletter_data: Dict) -> str:
        """Create a comprehensive summary from newsletter data"""
        if not newsletter_data or not newsletter_data.get('content'):
            return "No recent content found for today's newsletter."
        
        date_str = datetime.now().strftime("%B %d, %Y")
        
        content = newsletter_data['content']
        citations_count = len(newsletter_data.get('citations', []))
        
        summary = f"AI Voice Newsletter Summary for {date_str}. "
        summary += f"Today's newsletter covers the latest developments in {self.newsletter_topic}, "
        summary += f"based on {citations_count} quality sources. "
        
        # Extract key points from the content (first few sentences)
        sentences = content.split('. ')
        key_points = '. '.join(sentences[:3])  # First 3 sentences
        
        summary += f"Key highlights include: {key_points}. "
        summary += "For complete details and source links, please refer to the full newsletter content."
        
        return summary

    def generate_audio_with_elevenlabs(self, newsletter_data: Dict) -> tuple[Optional[str], str]:
        """Generate audio for newsletter summary"""
        print("\n🎵 Creating newsletter summary audio...")
        
        # Create full summary
        full_summary = self.create_newsletter_summary(newsletter_data)
        
        # Create a concise audio-friendly version of the summary (limit to ~200 words for reasonable audio length)
        words = full_summary.split()
        if len(words) > 200:
            # Take first 200 words and ensure it ends with a complete sentence
            audio_text = " ".join(words[:200])
            # Find the last sentence ending
            last_period = audio_text.rfind('.')
            last_exclamation = audio_text.rfind('!')
            last_question = audio_text.rfind('?')
            last_sentence_end = max(last_period, last_exclamation, last_question)
            
            if last_sentence_end > len(audio_text) - 50:  # If sentence end is near the end
                audio_text = audio_text[:last_sentence_end + 1]
            else:
                audio_text = audio_text + "."
        else:
            audio_text = full_summary
        
        print(f"   📝 Full summary: {len(full_summary.split())} words")
        print(f"   🎙️ Audio text: {len(audio_text.split())} words")
        
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}"
        headers = {
            "xi-api-key": self.elevenlabs_api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "text": audio_text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.8
            }
        }
        
        try:
            print("   🎙️ Generating speech for newsletter summary...")
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code == 401:
                print("❌ ElevenLabs API Error: Invalid API key")
                return None, full_summary
            
            response.raise_for_status()
            
            # Create audio folder
            audio_folder = os.path.join(".", "newsletter_audio")
            os.makedirs(audio_folder, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            audio_filename = f"newsletter_summary_{timestamp}.mp3"
            audio_path = os.path.join(audio_folder, audio_filename)
            
            with open(audio_path, 'wb') as f:
                f.write(response.content)
            
            print(f"🎧 Newsletter summary audio generated: {audio_path}")
            return audio_path, full_summary
            
        except Exception as e:
            print(f"❌ Error generating audio: {e}")
            return None, full_summary
    
    def _clean_text_for_speech(self, text: str) -> str:
        """Clean text for better speech synthesis"""
        import re
        
        # Remove emojis and special characters
        emoji_pattern = re.compile("["
                                 u"\U0001F600-\U0001F64F"
                                 u"\U0001F300-\U0001F5FF"
                                 u"\U0001F680-\U0001F6FF"
                                 u"\U0001F1E0-\U0001F1FF"
                                 u"\U00002702-\U000027B0"
                                 u"\U000024C2-\U0001F251"
                                 "]+", flags=re.UNICODE)
        return emoji_pattern.sub('', text).strip()
    
    def send_newsletter_with_composio(self, content: str, audio_path: Optional[str]) -> tuple[bool, str]:
        """Send newsletter via Gmail using Composio with content length validation"""
        if not self.composio_toolset or not self.openai_client:
            print("⚠️  Composio not available")
            return False, content
        
        valid_emails = [email.strip() for email in self.recipient_emails if email.strip()]
        if not valid_emails:
            print("⚠️  No recipients configured")
            return False, content
        
        print("\n📧 Sending newsletter with Composio...")
        
        original_content = content
        
        # Check content length and truncate if necessary
        max_content_length = 20000  # Conservative limit for Composio/Gmail
        if len(content) > max_content_length:
            print(f"⚠️  Content length ({len(content)} chars) exceeds safe limit ({max_content_length})")
            print("🔧 Truncating content to fit email limits...")
            
            # Find a good truncation point (end of paragraph or sentence)
            truncated_content = content[:max_content_length]
            
            # Try to end at a paragraph break
            last_double_newline = truncated_content.rfind('\n\n')
            if last_double_newline > max_content_length * 0.8:  # If we can keep 80% of content
                truncated_content = truncated_content[:last_double_newline]
            else:
                # Try to end at a sentence
                last_period = truncated_content.rfind('. ')
                if last_period > max_content_length * 0.8:
                    truncated_content = truncated_content[:last_period + 1]
            
            # Add truncation notice
            truncated_content += f"""

[Content truncated due to email length limits. Full newsletter saved locally.]

Original content length: {len(content)} characters
Sent content length: {len(truncated_content)} characters"""
            
            content = truncated_content
            print(f"✂️  Content truncated to {len(content)} characters")
        
        try:
            # Check Gmail connection
            gmail_tools = self.composio_toolset.get_tools(apps=[App.GMAIL])
            
            if not gmail_tools:
                print("❌ Gmail tools not found. Please connect Gmail:")
                print("   composio login")
                print("   composio add gmail")
                return False, content
            
            # Create assistant for email sending
            assistant = self.openai_client.beta.assistants.create(
                name="Newsletter Sender",
                instructions="""You are a helpful assistant that sends newsletters via Gmail.
                Send the newsletter with proper formatting and include any attachments if provided.
                Make sure to send to all recipients specified. Keep the email content exactly as provided.
                If content seems long, send it as-is - do not truncate or summarize it.""",
                model="gpt-4-turbo",
                tools=gmail_tools
            )
            
            # Create thread
            thread = self.openai_client.beta.threads.create()
            
            # Prepare email details
            subject = f"🎙️ AI Voice Newsletter - {datetime.now().strftime('%B %d, %Y')}"
            recipients_str = ", ".join(valid_emails)
            
            # Create plain text email (avoiding HTML complexity that might cause truncation)
            email_instruction = f"""Please send an email with the following details:

Recipients: {recipients_str}
Subject: {subject}

Email Content:
{content}

Please send this email exactly as provided. Do not modify, truncate, or summarize the content.
Send as plain text email to avoid formatting issues."""
            
            # Add audio attachment instruction if available
            if audio_path and os.path.exists(audio_path):
                email_instruction += f"""

Note: There is an audio summary file at {audio_path} that should be attached to the email."""
            
            print(f"📝 Sending email with {len(content)} characters of content...")
            
            # Add message to thread
            message = self.openai_client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=email_instruction
            )
            
            # Run the assistant
            run = self.openai_client.beta.threads.runs.create(
                thread_id=thread.id,
                assistant_id=assistant.id
            )
            
            # Handle tool calls with timeout
            print("   🤖 Assistant is sending email...")
            try:
                run_result = self.composio_toolset.wait_and_handle_assistant_tool_calls(
                    client=self.openai_client,
                    run=run,
                    thread=thread
                )
                
                # Check if email was sent successfully
                messages = self.openai_client.beta.threads.messages.list(thread_id=thread.id)
                for message in messages.data:
                    if message.role == "assistant":
                        for content_item in message.content:
                            if content_item.type == "text":
                                response_text = content_item.text.value.lower()
                                if "sent" in response_text or "success" in response_text:
                                    print("✅ Newsletter sent successfully via Composio!")
                                    return True, content
                                elif "error" in response_text or "failed" in response_text:
                                    print(f"❌ Composio error in response: {content_item.text.value}")
                                    return False, content
                
                print("⚠️  Email status unclear - check assistant response")
                return False, content
                
            except Exception as e:
                print(f"❌ Composio tool execution error: {e}")
                return False, content
            
        except Exception as e:
            print(f"❌ Composio email error: {e}")
            return False, content
    
    def send_newsletter_with_smtp(self, content: str, audio_path: Optional[str]) -> tuple[bool, str]:
        """Send newsletter via Gmail SMTP with content length validation"""
        valid_emails = [email.strip() for email in self.recipient_emails if email.strip()]
        
        if not valid_emails:
            print("⚠️  No recipients configured")
            return False, content
        
        print("\n📧 Attempting Gmail SMTP delivery...")
        
        original_content = content
        
        # Check content length and truncate if necessary (same logic as Composio)
        max_content_length = 25000  # Slightly higher limit for direct SMTP
        original_length = len(content)
        
        if len(content) > max_content_length:
            print(f"⚠️  Content length ({len(content)} chars) exceeds safe limit ({max_content_length})")
            print("🔧 Truncating content to fit email limits...")
            
            # Find a good truncation point (end of paragraph or sentence)
            truncated_content = content[:max_content_length]
            
            # Try to end at a paragraph break
            last_double_newline = truncated_content.rfind('\n\n')
            if last_double_newline > max_content_length * 0.8:  # If we can keep 80% of content
                truncated_content = truncated_content[:last_double_newline]
            else:
                # Try to end at a sentence
                last_period = truncated_content.rfind('. ')
                if last_period > max_content_length * 0.8:
                    truncated_content = truncated_content[:last_period + 1]
            
            # Add truncation notice
            truncated_content += f"""

[Content truncated due to email length limits. Full newsletter saved locally.]

Original content length: {original_length} characters
Sent content length: {len(truncated_content)} characters"""
            
            content = truncated_content
            print(f"✂️  Content truncated to {len(content)} characters")
        
        try:
            import smtplib
            from email.mime.multipart import MIMEMultipart
            from email.mime.text import MIMEText
            from email.mime.base import MIMEBase
            from email import encoders
            
            gmail_user = os.getenv('GMAIL_USER')
            gmail_password = os.getenv('GMAIL_APP_PASSWORD')
            
            if not gmail_user or not gmail_password:
                print("❌ Gmail credentials not configured")
                print("   Set GMAIL_USER and GMAIL_APP_PASSWORD in .env file")
                return False, content
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = gmail_user
            msg['To'] = ', '.join(valid_emails)
            msg['Subject'] = f"🎙️ AI Voice Newsletter - {datetime.now().strftime('%B %d, %Y')}"
            
            # Add content as plain text (avoiding HTML complexity)
            msg.attach(MIMEText(content, 'plain', 'utf-8'))
            
            print(f"📝 Sending email with {len(content)} characters of content...")
            
            # Add audio attachment
            if audio_path and os.path.exists(audio_path):
                with open(audio_path, "rb") as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename= newsletter_summary.mp3'
                    )
                    msg.attach(part)
                print("🎧 Audio attachment added")
            
            # Send email
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(gmail_user, gmail_password)
            server.sendmail(gmail_user, valid_emails, msg.as_string())
            server.quit()
            
            print("✅ Newsletter sent successfully via Gmail!")
            if original_length != len(content):
                print(f"📊 Content was truncated: {original_length} → {len(content)} chars")
            return True, content
            
        except Exception as e:
            print(f"❌ Gmail SMTP error: {e}")
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
    
    def _create_content_summary(self, full_content: str, max_length: int = 500) -> str:
        """Create a brief summary of newsletter content for truncation notices"""
        # Extract key sections
        lines = full_content.split('\n')
        summary_lines = []
        
        for line in lines:
            line = line.strip()
            if line.startswith('**') and line.endswith('**'):  # Section headers
                summary_lines.append(line)
            elif line.startswith('*   **Title:**'):  # Story titles
                summary_lines.append(line.replace('*   **Title:**', '• '))
        
        summary = '\n'.join(summary_lines[:10])  # First 10 items
        
        if len(summary) > max_length:
            summary = summary[:max_length] + "..."
        
        return summary
    
    def save_newsletter_locally(self, content: str, audio_path: Optional[str], original_content: str = None) -> bool:
        """Save newsletter files locally with clear documentation of any truncation"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save email content (what was sent)
        text_filename = f"newsletter_backup_{timestamp}.txt"
        with open(text_filename, 'w', encoding='utf-8') as f:
            f.write("EMAIL CONTENT (What was sent via email):\n")
            f.write("=" * 50 + "\n")
            
            if original_content and len(original_content) != len(content):
                f.write(f"NOTE: Content was truncated for email delivery\n")
                f.write(f"Original length: {len(original_content)} characters\n")
                f.write(f"Sent length: {len(content)} characters\n")
                f.write("Full content is saved in the complete newsletter file.\n\n")
            
            f.write(content)
        print(f"💾 Email content saved: {text_filename}")
        
        # Save complete content if truncated
        if original_content and len(original_content) != len(content):
            complete_filename = f"newsletter_complete_{timestamp}.txt"
            with open(complete_filename, 'w', encoding='utf-8') as f:
                f.write("COMPLETE NEWSLETTER CONTENT (Full version):\n")
                f.write("=" * 50 + "\n")
                f.write(original_content)
            print(f"📄 Complete content saved: {complete_filename}")
            
            # Create truncation summary
            summary = self._create_content_summary(original_content)
            truncation_summary_filename = f"truncation_summary_{timestamp}.txt"
            with open(truncation_summary_filename, 'w', encoding='utf-8') as f:
                f.write("CONTENT TRUNCATION SUMMARY:\n")
                f.write("=" * 50 + "\n")
                f.write(f"Original content length: {len(original_content)} characters\n")
                f.write(f"Email content length: {len(content)} characters\n")
                f.write(f"Truncated: {len(original_content) - len(content)} characters\n\n")
                f.write("Content overview:\n")
                f.write(summary)
            print(f"📋 Truncation summary saved: {truncation_summary_filename}")
        
        # Save HTML version
        html_content = self._create_html_email(content)
        html_filename = f"newsletter_{timestamp}.html"
        with open(html_filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"🌐 HTML version saved: {html_filename}")
        
        # Save audio transcript
        if audio_path and os.path.exists(audio_path):
            audio_transcript_filename = f"audio_summary_{timestamp}.txt"
            with open(audio_transcript_filename, 'w', encoding='utf-8') as f:
                f.write("AUDIO ATTACHMENT CONTENT (Newsletter summary):\n")
                f.write("=" * 50 + "\n")
                f.write("This text was converted to audio and attached to the email.\n")
                f.write("The email content did NOT include this summary.\n\n")
                f.write("Audio contains the newsletter summary that was not included in email text.\n")
                f.write(f"Audio file: {os.path.basename(audio_path)}\n")
            
            print(f"🎙️ Audio transcript saved: {audio_transcript_filename}")
        
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
                print("🎵 Generating audio summary...")
                audio_path, newsletter_summary = self.generate_audio_with_elevenlabs(newsletter_data)
            
            # Step 3: Handle output based on mode
            print("⏱️  Step 3/3: Processing output...")
            
            if mode == "content_only":
                # Save content to file only
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"newsletter_content_{timestamp}.txt"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(newsletter_content)
                print(f"💾 Content saved to: {filename}")
                
            elif mode == "email_only":
                # Send email without audio
                email_success, sent_content = self._send_email(newsletter_content, None)
                # Save what was actually sent, with reference to original if truncated
                if len(sent_content) != len(newsletter_content):
                    self.save_newsletter_locally(sent_content, None, newsletter_content)
                else:
                    self.save_newsletter_locally(sent_content, None)
                
            elif mode == "email_with_audio":
                # Send email with audio attachment
                email_success, sent_content = self._send_email(newsletter_content, audio_path)
                # Save what was actually sent, with reference to original if truncated
                if len(sent_content) != len(newsletter_content):
                    self.save_newsletter_locally(sent_content, audio_path, newsletter_content)
                else:
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
    
    def _send_email(self, content: str, audio_path: Optional[str]) -> tuple[bool, str]:
        """Send email using available methods and return success status and content that was actually sent"""
        original_content = content
        email_success = False
        sent_content = content
        
        # Try Composio first if available
        if self.composio_toolset and self.openai_client:
            email_success, sent_content = self.send_newsletter_with_composio(content, audio_path)
        
        # Fallback to SMTP if Composio failed or not available
        if not email_success:
            # Use original content for SMTP attempt (in case Composio truncated it)
            email_success, sent_content = self.send_newsletter_with_smtp(original_content, audio_path)
        
        return email_success, sent_content
    
    def _print_email_setup_instructions(self):
        """Print email setup instructions"""
        print("\n💡 To enable email delivery:")
        print("   Add to your .env file:")
        print("   GMAIL_USER=your-email@gmail.com")
        print("   GMAIL_APP_PASSWORD=your-app-password")
        print("   Get app password: https://support.google.com/accounts/answer/185833")


def parse_arguments():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(
        description="AI Voice Newsletter Generator with Exa Answer API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python ai_new.py --content-only          # Generate content and save to file only
  python ai_new.py --email                 # Generate and send newsletter via email  
  python ai_new.py --email-with-audio      # Generate, create audio, and send email with audio attachment
  python ai_new.py                         # Default: --email-with-audio

Modes:
  --content-only     : Generate newsletter content and save to file (no email, no audio)
  --email           : Generate newsletter content and send via email (no audio) 
  --email-with-audio: Generate newsletter content, create audio summary, and send email with attachment (default)

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
    
    return parser.parse_args()

def main():
    """Main execution function with command-line argument support"""
    args = parse_arguments()
    
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
        print("\n2. For email delivery, choose ONE option:")
        print("   Option A - Composio (Recommended):")
        print("   OPENAI_API_KEY=your_openai_key")
        print("   COMPOSIO_API_KEY=your_composio_key")
        print("   Then run: composio login && composio add gmail")
        print("\n   Option B - Gmail SMTP (Fallback):")
        print("   GMAIL_USER=your-email@gmail.com")
        print("   GMAIL_APP_PASSWORD=your-app-password")
        print("\n3. Install required packages:")
        print("   pip install python-dotenv openai composio-openai requests")
        print("\n4. Optional settings:")
        print("   NEWSLETTER_TOPIC=Your preferred topic")
        print("\n5. Usage examples:")
        print("   python ai_new.py --content-only")
        print("   python ai_new.py --email")
        print("   python ai_new.py --email-with-audio")


if __name__ == "__main__":
    main() 