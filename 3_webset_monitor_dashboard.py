#!/usr/bin/env python3
"""
PROJECT 3: Webset Monitor (Video Demo Version)
Difficulty: ⭐⭐⭐ (Advanced)

Minimal terminal-based monitoring example with no database.
Perfect for YouTube video demonstration.

Requirements: pip install requests python-dotenv
Set EXA_API_KEY in environment variables
"""

import os
import time
from datetime import datetime
from dotenv import load_dotenv
import requests

# Load environment
load_dotenv()

class SimpleMonitor:
    def __init__(self):
        self.api_key = os.getenv('EXA_API_KEY')
        if not self.api_key:
            raise ValueError("EXA_API_KEY required")
        
        self.headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key
        }
        
        self.seen_urls = set()
        self.total_found = 0
    
    def create_monitor(self, query):
        """Create a webset with monitor"""
        payload = {
            "search": {
                "query": query,
                "entity": {"type": "article"},
                "count": 5
            }
        }
        
        response = requests.post("https://api.exa.ai/websets/v0/websets", 
                               headers=self.headers, json=payload)
        response.raise_for_status()
        webset = response.json()
        webset_id = webset['id']
        
        # Create monitor with correct API structure
        monitor_payload = {
            "websetId": webset_id,
            "cadence": {
                "cron": "0 9 * * *",  # Daily at 9 AM UTC
                "timezone": "UTC"
            },
            "behavior": {
                "type": "search",
                "config": {
                    "query": query,
                    "entity": {"type": "article"},
                    "count": 5,
                    "behavior": "append"
                }
            }
        }
        
        response = requests.post("https://api.exa.ai/websets/v0/monitors", 
                               headers=self.headers, json=monitor_payload)
        response.raise_for_status()
        monitor = response.json()
        
        return webset_id, monitor['id']
    
    def check_for_new_items(self, webset_id):
        """Check for new items"""
        response = requests.get(f"https://api.exa.ai/websets/v0/websets/{webset_id}/items", 
                              headers=self.headers)
        if response.status_code != 200:
            return []
        
        items = response.json().get('data', [])
        new_items = []
        
        for item in items:
            url = item.get('properties', {}).get('url', '')
            if url and url not in self.seen_urls:
                self.seen_urls.add(url)
                new_items.append(item)
        
        return new_items
    
    def monitor_loop(self, webset_id):
        """Simple monitoring loop"""
        print(f"\n🔄 Starting monitor (checking every 30 seconds)")
        print("💡 Press Ctrl+C to stop\n")
        
        while True:
            try:
                new_items = self.check_for_new_items(webset_id)
                
                if new_items:
                    for item in new_items:
                        self.total_found += 1
                        title = item.get('properties', {}).get('description', 'No title')
                        url = item.get('properties', {}).get('url', '')
                        print(f"🆕 #{self.total_found}: {title[:60]}...")
                        print(f"    🔗 {url}")
                else:
                    print(f"⏰ {datetime.now().strftime('%H:%M:%S')} - No new items (Total: {self.total_found})")
                
                time.sleep(30)  # Check every 30 seconds
                
            except KeyboardInterrupt:
                print(f"\n🛑 Monitoring stopped. Found {self.total_found} total items.")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                time.sleep(10)

def main():
    print("🔍 Simple Webset Monitor")
    print("=" * 30)
    
    monitor = SimpleMonitor()
    
    # Create monitor
    query = "AI breakthrough news 2024"
    print(f"Query: {query}")
    print("\n🔨 Creating monitor...")
    
    webset_id, monitor_id = monitor.create_monitor(query)
    
    print(f"✅ Monitor created!")
    print(f"   Webset: {webset_id}")
    print(f"   Monitor: {monitor_id}")
    
    # Check initial items
    print("\n📊 Checking for initial items...")
    initial_items = monitor.check_for_new_items(webset_id)
    
    if initial_items:
        print(f"Found {len(initial_items)} initial items:")
        for i, item in enumerate(initial_items, 1):
            title = item.get('properties', {}).get('description', 'No title')
            print(f"  {i}. {title[:50]}...")
    
    # Start monitoring
    monitor.monitor_loop(webset_id)

if __name__ == "__main__":
    main() 