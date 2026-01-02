"""
Quick test script to verify News API key and check available data
Run: python test_api.py
"""
import httpx
import json

NEWS_API_KEY = "f0e24f9a61104e8d909a2ebf9269c6b8"
BASE_URL = "https://newsapi.org/v2"

async def test_news_api():
    print("Testing News API...\n")
    
    # Test 1: Top Headlines
    print("1. Testing Top Headlines (General):")
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/top-headlines",
            params={"apiKey": NEWS_API_KEY, "country": "us", "pageSize": 5}
        )
        data = response.json()
        print(f"Status: {data.get('status')}")
        print(f"Total Results: {data.get('totalResults')}")
        if data.get('articles'):
            print(f"Sample Article: {data['articles'][0]['title']}\n")
    
    # Test 2: Categories
    categories = ["business", "entertainment", "general", "health", "science", "sports", "technology"]
    print("2. Testing Categories:")
    for category in categories:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}/top-headlines",
                params={"apiKey": NEWS_API_KEY, "country": "us", "category": category, "pageSize": 1}
            )
            data = response.json()
            count = data.get('totalResults', 0)
            print(f"   {category.capitalize()}: {count} articles available")
    
    # Test 3: Search
    print("\n3. Testing Search:")
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/everything",
            params={"apiKey": NEWS_API_KEY, "q": "technology", "pageSize": 3}
        )
        data = response.json()
        print(f"Search 'technology': {data.get('totalResults')} results")
        if data.get('articles'):
            article = data['articles'][0]
            print(f"\nSample Article Structure:")
            print(f"  - source: {article.get('source')}")
            print(f"  - author: {article.get('author')}")
            print(f"  - title: {article.get('title')}")
            print(f"  - description: {article.get('description')[:100]}...")
            print(f"  - url: {article.get('url')}")
            print(f"  - urlToImage: {article.get('urlToImage')}")
            print(f"  - publishedAt: {article.get('publishedAt')}")
            print(f"  - content: {article.get('content')[:100] if article.get('content') else 'None'}...")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_news_api())
