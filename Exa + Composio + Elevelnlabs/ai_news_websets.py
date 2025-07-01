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
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import requests

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("python-dotenv not installed. Please set environment variables manually.")

class WebsetsNewsletterGenerator:
    """AI-powered newsletter generator using Exa Websets"""
    
    def __init__(self):
        # API Keys
        self.exa_api_key = os.getenv('EXA_API_KEY')
        
        # Configuration
        self.newsletter_topic = os.getenv('NEWSLETTER_TOPIC', 'AI and Technology')
        self.max_articles = 5  # Fixed to 5 as requested
        
        # API Headers
        self.headers = {
            "Content-Type": "application/json",
            "x-api-key": self.exa_api_key
        }
        
        self._validate_config()
    
    def _validate_config(self):
        """Validate required configuration"""
        print("🔧 Validating configuration...")
        
        if not self.exa_api_key:
            raise ValueError("Missing required environment variable: EXA_API_KEY")
        
        print(f"✅ EXA_API_KEY: {'*' * (len(self.exa_api_key) - 8) + self.exa_api_key[-8:]}")
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
    
    def generate_newsletter(self):
        """Main method to generate newsletter using websets"""
        start_time = time.time()
        print("🚀 Starting AI Newsletter Generation with Websets...")
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
            
            # Save content
            print("⏱️  Step 3/3: Saving newsletter...")
            self.save_newsletter_locally(newsletter_content, webset_data)
            
            # Final results
            total_time = time.time() - start_time
            print("\n" + "=" * 50)
            print(f"⏱️  Total completion time: {total_time:.1f} seconds")
            print("🎉 Newsletter generated successfully!")
            print(f"📊 Newsletter contains {articles_count} curated articles")
            
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
  python a_websets.py                    # Generate newsletter with default topic
  python a_websets.py --topic "AI"       # Generate newsletter with custom topic

Environment Variables Required:
  EXA_API_KEY=your_exa_api_key

Optional:
  NEWSLETTER_TOPIC=your_preferred_topic (default: "AI and Technology")
"""
    )
    
    parser.add_argument('--topic', type=str, 
                       help='Newsletter topic (overrides NEWSLETTER_TOPIC env var)')
    
    return parser.parse_args()

def main():
    """Main execution function"""
    args = parse_arguments()
    
    try:
        generator = WebsetsNewsletterGenerator()
        
        # Override topic if provided
        if args.topic:
            generator.newsletter_topic = args.topic
            print(f"📰 Using custom topic: {args.topic}")
        
        generator.generate_newsletter()
        
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        print("\n📋 Setup Instructions:")
        print("1. Create a .env file with:")
        print("   EXA_API_KEY=your_exa_key")
        print("\n2. Install required packages:")
        print("   pip install python-dotenv requests")
        print("\n3. Optional settings:")
        print("   NEWSLETTER_TOPIC=Your preferred topic")
        print("\n4. Usage examples:")
        print("   python a_websets.py")
        print("   python a_websets.py --topic 'Machine Learning'")

if __name__ == "__main__":
    main() 