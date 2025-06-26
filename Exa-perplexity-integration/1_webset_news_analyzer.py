"""
Webset News Analyzer with Perplexity AI
========================================
Uses Exa Websets API directly to collect news articles, then Perplexity AI to analyze trends and generate insights.
Perfect for: Daily news analysis, trend identification, market intelligence
"""

import os
import time
import json
from datetime import datetime
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration
EXA_API_KEY = os.getenv('EXA_API_KEY', 'your_exa_api_key_here')
PERPLEXITY_API_KEY = os.getenv('PERPLEXITY_API_KEY', 'your_perplexity_api_key_here')
EXA_BASE_URL = "https://api.exa.ai"

def create_news_webset(topic="AI breakthroughs", max_results=10):
    """Create a webset to collect recent news on a specific topic"""
    
    print(f"🔍 Creating webset for: {topic}")
    
    headers = {
        'Content-Type': 'application/json',
        'x-api-key': EXA_API_KEY
    }
    
    # Create webset with news-focused search - correct API format
    payload = {
        "search": {
            "query": f"{topic} news recent developments",
            "count": max_results,
            "includeDomains": ["techcrunch.com", "reuters.com", "bloomberg.com", "cnn.com", "bbc.com"],
            "startPublishedDate": "2024-01-01"
        }
    }
    
    print(f"📤 Sending request to: {EXA_BASE_URL}/websets/v0/websets")
    print(f"📋 Payload: {json.dumps(payload, indent=2)}")
    
    response = requests.post(
        f"{EXA_BASE_URL}/websets/v0/websets",
        headers=headers,
        json=payload
    )
    
    print(f"📨 Response Status: {response.status_code}")
    print(f"📨 Response Body: {response.text}")
    
    if response.status_code != 201:
        raise Exception(f"Failed to create webset: {response.status_code} - {response.text}")
    
    webset_data = response.json()
    webset_id = webset_data['id']
    
    print(f"✅ Webset created successfully!")
    print(f"🆔 Webset ID: {webset_id}")
    print(f"🔗 Monitor webset at: https://dashboard.exa.ai/websets/{webset_id}")
    print(f"🔗 Or check status at: {EXA_BASE_URL}/websets/v0/websets/{webset_id}")
    
    return webset_id

def wait_for_webset_completion(webset_id, check_interval=30):
    """Wait for webset to complete with periodic status updates"""
    
    headers = {
        'Content-Type': 'application/json',
        'x-api-key': EXA_API_KEY
    }
    
    print(f"\n⏳ Waiting for webset {webset_id} to complete...")
    print(f"🔄 Checking status every {check_interval} seconds...")
    
    start_time = time.time()
    
    while True:
        try:
            status_response = requests.get(
                f"{EXA_BASE_URL}/websets/v0/websets/{webset_id}",
                headers=headers
            )
            
            if status_response.status_code != 200:
                print(f"❌ Failed to get webset status: {status_response.status_code}")
                print(f"Response: {status_response.text}")
                break
            
            status_data = status_response.json()
            elapsed_time = int(time.time() - start_time)
            
            print(f"📊 [{elapsed_time}s] Status: {status_data.get('status', 'unknown')}")
            
            # Show progress if available
            if 'searches' in status_data and status_data['searches']:
                search = status_data['searches'][0]
                if 'progress' in search:
                    progress = search['progress']
                    found = progress.get('found', 0)
                    completion = progress.get('completion', 0)
                    print(f"   📈 Progress: {completion}% - Found {found} items")
            
            if status_data.get('status') in ["completed", "idle"]:
                # Check if we have items or if progress is 100%
                has_items = False
                if 'searches' in status_data and status_data['searches']:
                    search = status_data['searches'][0]
                    if 'progress' in search:
                        progress = search['progress']
                        completion = progress.get('completion', 0)
                        found = progress.get('found', 0)
                        if completion >= 100 or found > 0:
                            has_items = True
                
                if has_items:
                    print(f"✅ Webset completed after {elapsed_time} seconds!")
                    
                    # Get webset items
                    print(f"📥 Fetching items from: {EXA_BASE_URL}/websets/v0/websets/{webset_id}/items")
                    items_response = requests.get(
                        f"{EXA_BASE_URL}/websets/v0/websets/{webset_id}/items",
                        headers=headers
                    )
                    
                    print(f"📥 Items Response Status: {items_response.status_code}")
                    print(f"📥 Items Response Body: {items_response.text[:500]}...")
                    
                    if items_response.status_code == 200:
                        items_data = items_response.json()
                        print(f"📋 Items data keys: {list(items_data.keys())}")
                        
                        # Try different possible keys for items
                        items = items_data.get('items', [])
                        if not items:
                            items = items_data.get('results', [])
                        if not items:
                            items = items_data.get('data', [])
                        
                        status_data['results'] = items
                        print(f"📰 Retrieved {len(status_data['results'])} articles")
                        
                                            # Debug: show first item structure if available
                    if items:
                        print(f"🔍 First item keys: {list(items[0].keys())}")
                        if 'properties' in items[0]:
                            props = items[0]['properties']
                            print(f"🔍 Properties keys: {list(props.keys())}")
                            print(f"🔍 Sample title: {props.get('title', props.get('url', 'N/A'))[:100]}...")
                            print(f"🔍 Sample description: {props.get('description', 'N/A')[:100]}...")
                            if 'properties' in items[0]:
                                props = items[0]['properties']
                                print(f"🔍 Properties keys: {list(props.keys())}")
                                print(f"🔍 Sample title: {props.get('title', props.get('url', 'N/A'))[:100]}...")
                                print(f"🔍 Sample description: {props.get('description', 'N/A')[:100]}...")
                    else:
                        print(f"⚠️ Warning: Could not retrieve items: {items_response.status_code}")
                        print(f"⚠️ Response: {items_response.text}")
                        status_data['results'] = []
                    
                    return status_data
                
            elif status_data.get('status') == "failed":
                print(f"❌ Webset creation failed after {elapsed_time} seconds")
                print(f"Error details: {status_data}")
                raise Exception("Webset creation failed")
            
            elif status_data.get('status') in ["idle", "running"]:
                # Continue waiting
                pass
            else:
                print(f"🤔 Unknown status: {status_data.get('status')}")
            
        except Exception as e:
            print(f"❌ Error checking status: {str(e)}")
            break
        
        time.sleep(check_interval)

def analyze_with_perplexity(news_items):
    """Use Perplexity AI to analyze news trends and generate insights"""
    
    # Prepare news summary for analysis - extract from properties field
    news_summary = "\n".join([
        f"- {item.get('properties', {}).get('title', item.get('properties', {}).get('url', 'No title'))}: {item.get('properties', {}).get('description', item.get('properties', {}).get('text', ''))[:200]}..." 
        for item in news_items[:8]  # Limit to avoid token limits
    ])
    
    prompt = f"""
    Analyze the following recent news articles and provide:
    1. Key trends and patterns
    2. Most significant developments
    3. Potential implications and predictions
    4. Market/industry impact assessment
    
    News Articles:
    {news_summary}
    
    Please provide a structured analysis with clear insights.
    """
    
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "llama-3.1-sonar-small-128k-online",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 1000
    }
    
    # Check if Perplexity API key is set
    if PERPLEXITY_API_KEY == 'your_perplexity_api_key_here' or not PERPLEXITY_API_KEY:
        return "⚠️ Perplexity AI analysis skipped - API key not configured. Set PERPLEXITY_API_KEY environment variable to enable AI analysis."
    
    print("🤖 Analyzing with Perplexity AI...")
    
    response = requests.post(
        "https://api.perplexity.ai/chat/completions",
        headers=headers,
        json=data
    )
    
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        return f"❌ Perplexity API Error: {response.status_code} - {response.text[:200]}..."

def generate_report(webset, analysis):
    """Generate a formatted report with findings"""
    
    results = webset.get('results', [])
    
    report = f"""
NEWS ANALYSIS REPORT
===================
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Webset: {webset.get('name', 'Unknown')}
Articles Analyzed: {len(results)}

SOURCES OVERVIEW:
"""
    
    for i, item in enumerate(results[:5], 1):
        properties = item.get('properties', {})
        title = properties.get('title', properties.get('url', 'No title'))
        url = properties.get('url', 'No URL')
        published_date = properties.get('publishedDate', 'Unknown date')
        report += f"{i}. {title}\n   URL: {url}\n   Published: {published_date}\n\n"
    
    report += f"\nAI ANALYSIS:\n{'='*50}\n{analysis}\n"
    
    return report

def main():
    """Main execution function with step-by-step approach"""
    try:
        print("🚀 EXA WEBSETS + PERPLEXITY NEWS ANALYZER")
        print("=" * 50)
        
        # Step 1: Get topic from user
        topic = input("Enter news topic to analyze (or press Enter for 'AI breakthroughs'): ").strip()
        if not topic:
            topic = "AI breakthroughs"
        
        print(f"\n🎯 Topic: {topic}")
        
        # Step 2: Create webset and show link
        print(f"\n📋 STEP 1: Creating Webset...")
        webset_id = create_news_webset(topic)
        
        # Step 3: Ask user if they want to wait or proceed manually
        print(f"\n🕐 STEP 2: Waiting for Completion...")
        user_choice = input("Choose option:\n1. Auto-wait with status updates (recommended)\n2. Manual - I'll check the dashboard myself\nEnter choice (1 or 2): ").strip()
        
        if user_choice == "2":
            print(f"\n🔗 Check your webset at: https://dashboard.exa.ai/websets/{webset_id}")
            input("Press Enter when the webset is completed and you're ready to analyze...")
            
            # Get the completed webset
            headers = {'x-api-key': EXA_API_KEY}
            status_response = requests.get(f"{EXA_BASE_URL}/websets/v0/websets/{webset_id}", headers=headers)
            
            if status_response.status_code == 200:
                webset = status_response.json()
                print(f"📥 Fetching items from: {EXA_BASE_URL}/websets/v0/websets/{webset_id}/items")
                items_response = requests.get(f"{EXA_BASE_URL}/websets/v0/websets/{webset_id}/items", headers=headers)
                print(f"📥 Items Response Status: {items_response.status_code}")
                print(f"📥 Items Response Body: {items_response.text[:500]}...")
                
                if items_response.status_code == 200:
                    items_data = items_response.json()
                    print(f"📋 Items data keys: {list(items_data.keys())}")
                    
                    # Try different possible keys for items
                    items = items_data.get('items', [])
                    if not items:
                        items = items_data.get('results', [])
                    if not items:
                        items = items_data.get('data', [])
                    
                    webset['results'] = items
                    print(f"📰 Retrieved {len(webset['results'])} articles")
                    
                    # Debug: show first item structure if available
                    if items:
                        print(f"🔍 First item keys: {list(items[0].keys())}")
                else:
                    print(f"⚠️ Warning: Could not retrieve items: {items_response.status_code}")
                    print(f"⚠️ Response: {items_response.text}")
                    webset['results'] = []
            else:
                raise Exception("Could not retrieve completed webset")
        else:
            # Auto-wait
            webset = wait_for_webset_completion(webset_id)
        
        # Step 4: Check results
        results = webset.get('results', [])
        if not results:
            print("❌ No articles found. The webset may still be processing or no results match your criteria.")
            print(f"🔗 Check the webset status at: https://dashboard.exa.ai/websets/{webset_id}")
            return
        
        print(f"\n📰 Found {len(results)} articles")
        
        # Step 5: Analyze with Perplexity
        print(f"\n🤖 STEP 3: Analyzing with Perplexity AI...")
        analysis = analyze_with_perplexity(results)
        
        # Step 6: Generate and display report
        print(f"\n📊 STEP 4: Generating Report...")
        report = generate_report(webset, analysis)
        
        # Display results
        print("\n" + "="*60)
        print(report)
        
        # Save to file
        filename = f"news_analysis_{topic.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n💾 Report saved to: {filename}")
        print(f"🔗 Webset ID for future reference: {webset_id}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 