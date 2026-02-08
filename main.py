import os
import requests
from datetime import datetime, timedelta

NEWS_API_KEY = os.getenv('NEWSAPI_KEY')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

def fetch_news():
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    url = f'https://newsapi.org/v2/everything?q=india&from={yesterday}&sortBy=publishedAt&apiKey={NEWS_API_KEY}'
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        articles = data.get('articles', [])
        print(f"Found {len(articles)} articles")
        return articles[:10]
    except:
        return []

def simple_filter(news_items):
    relevant_keywords = ['bank', 'rbi', 'economy', 'budget', 'govt', 'scheme', 'polity', 'upsc', 'ssc']
    filtered = []
    for item in news_items:
        title = item.get('title', '').lower()
        if any(word in title for word in relevant_keywords):
            filtered.append(f"Title: {item.get('title', '')}
Summary: {item.get('description', '')}")
    return filtered

def save_file(content):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
    with open('daily.txt', 'w') as f:
        f.write(f"UPSC/SSC/Bank News - {timestamp}
{'='*50}

")
        for i, item in enumerate(content, 1):
            f.write(f"{i}. {item}

")
    print(f"Saved {len(content)} items!")

if __name__ == "__main__":
    print("Starting...")
    if not NEWS_API_KEY:
        print("ERROR: NEWSAPI_KEY missing!")
        exit(1)
    
    news = fetch_news()
    filtered = simple_filter(news)
    save_file(filtered)
    print("DONE!")