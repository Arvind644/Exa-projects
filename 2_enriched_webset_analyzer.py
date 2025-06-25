#!/usr/bin/env python3
"""
PROJECT 2: Enriched Webset Analyzer (Video Demo Version)
Difficulty: ⭐⭐ (Intermediate)

Minimal example demonstrating enrichments and data analysis.
Perfect for YouTube video demonstration.

Requirements: pip install requests python-dotenv pandas
Set EXA_API_KEY in environment variables
"""

import os
import time
import requests
from dotenv import load_dotenv

# Load environment
load_dotenv()

class EnrichedWebsets:
    def __init__(self):
        self.api_key = os.getenv('EXA_API_KEY')
        if not self.api_key:
            raise ValueError("EXA_API_KEY required")
        
        self.headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key
        }
    
    def create_enriched_webset(self, query, criteria, enrichments, count=5):
        """Create webset with criteria and enrichments"""
        payload = {
            "search": {
                "query": query,
                "criteria": [{"description": c} for c in criteria],
                "entity": {"type": "article"},
                "count": count
            },
            "enrichments": enrichments
        }
        
        response = requests.post("https://api.exa.ai/websets/v0/websets", 
                               headers=self.headers, json=payload)
        response.raise_for_status()
        return response.json()
    
    def get_webset_status(self, webset_id):
        """Get webset status and details"""
        response = requests.get(f"https://api.exa.ai/websets/v0/websets/{webset_id}", 
                              headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def get_basic_items(self, webset_id):
        """Get basic items (even while enrichments are processing)"""
        try:
            response = requests.get(f"https://api.exa.ai/websets/v0/websets/{webset_id}/items", 
                                  headers=self.headers)
            response.raise_for_status()
            return response.json().get('data', [])
        except:
            return []
    
    def check_enrichment_results(self, webset_id):
        """Check if any enrichments are ready and display them"""
        # Try multiple times to get items as they might be processing
        items = []
        for attempt in range(3):
            items = self.get_basic_items(webset_id)
            if items:
                break
            if attempt < 2:
                print(f"   ⏳ Attempt {attempt + 1}: Waiting for search results...")
                time.sleep(2)
        
        if not items:
            print("   📝 No items ready yet - searches are still starting up")
            return False
        
        print(f"   📊 Found {len(items)} items from search!")
        print("   🎯 Here's what we discovered:")
        
        # Show all basic results first
        for i, item in enumerate(items, 1):
            props = item.get('properties', {})
            title = props.get('description', 'No title')
            url = props.get('url', 'No URL')
            
            print(f"\n   {i}. 📰 {title}")
            print(f"      🔗 {url}")
            
            # Check if any metadata is available
            if 'publishedDate' in props:
                print(f"      📅 Published: {props['publishedDate']}")
            if 'author' in props:
                print(f"      ✍️ Author: {props['author']}")
        
        # Now check enrichments
        print(f"\n   🔬 Checking enrichment status...")
        enriched_count = 0
        
        for i, item in enumerate(items, 1):
            enrichments = item.get('enrichments', [])
            if enrichments:
                has_any_enrichment = False
                for enrichment in enrichments:
                    status = enrichment.get('status', 'unknown')
                    enrich_id = enrichment.get('enrichmentId', 'unknown')
                    
                    if status == 'completed':
                        if not has_any_enrichment:
                            print(f"\n   ✨ Item {i} enrichments:")
                            has_any_enrichment = True
                        
                        enriched_count += 1
                        result = enrichment.get('result', [''])
                        result_text = result[0] if result else 'No result'
                        print(f"      ✅ {enrich_id}: {result_text[:100]}...")
                    elif status in ['running', 'pending']:
                        if not has_any_enrichment:
                            print(f"\n   ⏳ Item {i} enrichments processing...")
                            has_any_enrichment = True
        
        if enriched_count == 0:
            print("   🔄 Enrichments are still processing - run again in a few minutes!")
        else:
            print(f"   🎉 Found {enriched_count} completed enrichments!")
        
        return len(items) > 0

def analyze_startups():
    """Analyze startup funding with enrichments"""
    client = EnrichedWebsets()
    
    query = "AI startup funding rounds announced in 2024"
    
    criteria = [
        "Article about AI startup raising funding",
        "Article mentions funding amount and investors",
        "Article from credible tech or business publication"
    ]
    
    enrichments = [
        {
            "title": "Company Details",
            "description": "Extract company name, funding amount, and what they do",
            "format": "text"
        },
        {
            "title": "Key Investors",
            "description": "Extract lead investor and other participants",
            "format": "text"
        }
    ]
    
    # Create webset
    webset = client.create_enriched_webset(query, criteria, enrichments, count=5)
    webset_id = webset['id']
    
    print(f"🔗 View enriched webset: https://websets.exa.ai/{webset_id}")

def main():
    analyze_startups()

if __name__ == "__main__":
    main() 