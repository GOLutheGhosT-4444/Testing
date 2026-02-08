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
        print(f"Found {len(articles)} news articles")
        return articles[:10]
    except Exception as e:
        print(f"News fetch error: {e}")
        return []

def filter_news_gemini(news_items):
    if not GEMINI_API_KEY:
        print("No Gemini key - saving raw news")
        return [f"Title: {a.get('title', '')}
Summary: {a.get('description', '')}" for a in news_items]
    
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        filtered = []
        for item in news_items[:6]:
            text = f"Title: {item.get('title', '')}
Desc: {item.get('description', '')}"
            prompt = f"""UPSC/SSC/Bank exam ke liye filter karo. sirf Economy/Polity/Environment rakho.
Output format:
Title: [title]
Key Points: [2 bullet points]
Category: [Bank/SSC/UPSC]

News: {text}"""
            
            try:
                response = model.generate_content(prompt)
                if response.text.strip():
                    filtered.append(response.text.strip())
            except:
                continue
        
        print(f"Filtered {len(filtered)} news items")
        return filtered
        
    except Exception as e:
        print(f"Gemini error: {e}")
        return [f"Raw: {a.get('title', '')}" for a in news_items]

def save_file(content):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
    with open('daily.txt', 'w', encoding='utf-8') as f:
        f.write(f"UPSC/SSC/Bank News - {timestamp}
{'='*50}

")
        for i, item in enumerate(content, 1):
            f.write(f"{i}. {item}
{'-'*40}

")
    print(f"SUCCESS: {len(content)} items saved!")

if __name__ == "__main__":
    print("Starting news filter...")
    
    if not NEWS_API_KEY:
        print("ERROR: NEWSAPI_KEY missing!")
        exit(1)
    
    news = fetch_news()
    filtered = filter_news_gemini(news)
    save_file(filtered)
    
    print("DONE! Check daily.txt")