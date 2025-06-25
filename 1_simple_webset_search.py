#!/usr/bin/env python3
"""
PROJECT 1: Simple Webset Search (Video Demo Version)
Difficulty: ⭐ (Beginner)

Minimal example demonstrating basic Websets API usage.
Perfect for YouTube video demonstration.

Requirements: pip install requests python-dotenv
Set EXA_API_KEY in environment variables
"""

import os
import requests
import time
from dotenv import load_dotenv

# Load environment
load_dotenv()

class SimpleWebsets:
    def __init__(self):
        self.api_key = os.getenv('EXA_API_KEY')
        if not self.api_key:
            raise ValueError("EXA_API_KEY required")
        
        self.headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key
        }
    
    def create_webset(self, query, count=5):
        """Create a webset with search query"""
        payload = {
            "search": {
                "query": query,
                "count": count
            }
        }
        
        response = requests.post("https://api.exa.ai/websets/v0/websets", 
                               headers=self.headers, json=payload)
        response.raise_for_status()
        return response.json()
    
    def get_webset_status(self, webset_id):
        """Check webset status"""
        response = requests.get(f"https://api.exa.ai/websets/v0/websets/{webset_id}", 
                              headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def get_items(self, webset_id):
        """Get items from webset"""
        response = requests.get(f"https://api.exa.ai/websets/v0/websets/{webset_id}/items", 
                              headers=self.headers)
        response.raise_for_status()
        return response.json().get('data', [])
    
    def wait_for_completion(self, webset_id):
        """Wait for webset to complete"""
        for _ in range(40):  # Max 2 minutes
            webset = self.get_webset_status(webset_id)
            status = webset.get('status', 'unknown')
            
            print(f"Status: {status}")
            
            if status == 'idle':
                return True
            
            time.sleep(3)
        
        return False

def main():
    print("🔍 Simple Websets Demo")
    print("=" * 30)
    
    # Initialize client
    client = SimpleWebsets()
    
    # Search query
    query = "Latest AI breakthroughs 2024"
    print(f"Query: {query}")
    
    # Create webset
    print("\n🔨 Creating webset...")
    webset = client.create_webset(query, count=10)
    webset_id = webset['id']
    print(f"✅ Created: {webset_id}")
    
    # Check initial status
    print("\n📊 Webset Details:")
    status_info = client.get_webset_status(webset_id)
    print(f"   Status: {status_info.get('status', 'unknown')}")
    print(f"   Created: {status_info.get('created_at', 'N/A')}")
    
    print("\n🎯 Webset created successfully!")
    print("💡 You can now:")
    print("   • View it in the Exa Websets UI")
    print("   • Wait for it to complete processing")
    print("   • Add enrichments or monitors")
    print("   • Retrieve results when ready")
    
    print(f"\n🔗 Direct link: https://websets.exa.ai/{webset_id}")

if __name__ == "__main__":
    main() 