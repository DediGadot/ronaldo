#!/usr/bin/env python3
"""
Manual test script to scrape Schmiedmann without Scrapy to test basic access
"""

import requests
import time
from bs4 import BeautifulSoup
import random

def test_schmiedmann_access():
    """Test basic access to Schmiedmann BMW parts pages"""
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    # Test URLs that we know have products
    test_urls = [
        "https://www.schmiedmann.com/en/bmw-f10/spare-parts-engine-and-driveline-mc12-catn-ol",
        "https://www.schmiedmann.com/en/bmw-E28/spare-parts-engine-and-driveline-mc12-catn-ol",
    ]
    
    session = requests.Session()
    session.headers.update(headers)
    
    for url in test_urls:
        print(f"\n🔍 Testing: {url}")
        
        try:
            # Add delay between requests
            time.sleep(random.uniform(3, 6))
            
            response = session.get(url, timeout=30)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for product containers
                products = soup.find_all('div', class_='product-inner')
                print(f"Found {len(products)} products with .product-inner")
                
                # Try alternative selectors
                if not products:
                    products = soup.find_all('div', class_='product-card')
                    print(f"Found {len(products)} products with .product-card")
                
                if not products:
                    products = soup.find_all('div', class_='product-item')  
                    print(f"Found {len(products)} products with .product-item")
                
                # Look for any div with "product" in class name
                if not products:
                    products = soup.find_all('div', class_=lambda x: x and 'product' in x.lower())
                    print(f"Found {len(products)} products with 'product' in class name")
                
                if products:
                    print("✅ Found products! Sample product:")
                    sample = products[0]
                    print(f"HTML: {str(sample)[:200]}...")
                    
                    # Look for title
                    title = sample.find(text=True, recursive=True)
                    if title:
                        print(f"Sample title: {title.strip()[:50]}")
                else:
                    print("❌ No products found")
                    
                    # Check if blocked
                    page_text = soup.get_text().lower()
                    if any(word in page_text for word in ['blocked', 'access denied', 'forbidden']):
                        print("🚫 Page appears to be blocked")
                    else:
                        print("📄 Page loaded but no products found")
                        # Print first 500 chars of page
                        print(f"Page content sample: {soup.get_text()[:500]}")
                        
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_schmiedmann_access()