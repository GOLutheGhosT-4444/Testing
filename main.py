import os
import requests
from datetime import datetime, timedelta

NEWS_API_KEY = os.getenv('NEWSAPI_KEY')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

def fetch_news():
    """Last 24hr India news fetch karega"""
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    url = f'https://newsapi.org/v2/everything?q=india&from={yesterday}&sortBy=publishedAt&apiKey={NEWS_API_KEY}'
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        articles = data.get('articles', [])
        print(f"✅ Found {len(articles)} news articles")
        return articles[:15]  # Top 15
    except Exception as e:
        print(f"❌ News fetch error: {e}")
        return []

def filter_news_gemini(news_items):
    """Gemini se filter - SIMPLIFIED & STABLE"""
    if not GEMINI_API_KEY:
        print("⚠️ No Gemini key, saving raw news")
        return [f"Title: {a.get('title', '')}
Summary: {a.get('description', '')}" for a in news_items]
    
    import google.generativeai as genai
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        # FIXED: Direct stable model name (no list_models call)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        filtered = []
        prompt = """UPSC/SSC/Bank exam students ke liye ye news filter karo:
- RAKHO: Economy, Banking, Govt schemes, Polity, Environment, International
- HATADO: Sports, Bollywood, Local crime, Entertainment
Output ONLY:
**Title:** [short title]
**Key Points:** [2 exam bullet points]
**Category:** [Economy/Polity/Etc]

News: {news}"""

        for i, item in enumerate(news_items[:8]):  # Limit to 8 to avoid timeout
            text = f"Title: {item.get('title', '')}
Desc: {item.get('description', '')}"
            try:
                response = model.generate_content(prompt.format(news=text))
                if response.text.strip():
                    filtered.append(response.text.strip())
                    print(f"✅ Filtered news {i+1}")
            except Exception as e:
                print(f"⚠️ Skip news {i+1}: {e}")
                continue
        
        print(f"✅ Filtered {len(filtered)} relevant news")
        return filtered
        
    except Exception as e:
        print(f"❌ Gemini error, saving raw: {e}")
        return [f"Raw: {a.get('title', '')}" for a in news_items]

def save_daily_news(content):
    """daily.txt mein save karega"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M IST')
    with open('daily.txt', 'w', encoding='utf-8') as f:
        f.write(f"📢 UPSC/SSC/Bank Current Affairs
")
        f.write(f"Date: {timestamp}
")
        f.write("="*60 + "

")
        
        if content:
            for i, item in enumerate(content, 1):
                f.write(f"{i}. {item}
")
                f.write("-"*40 + "

")
        else:
            f.write("No news found today.
")
    
    print(f"✅ SUCCESS: Saved {len(content)} items to daily.txt")

if __name__ == "__main__":
    print("🚀 Starting UPSC News Filter...")
    
    if not NEWS_API_KEY:
        print("❌ ERROR: NEWSAPI_KEY missing in GitHub Secrets!")
        exit(1)
    
    # Step 1: Fetch news
    news = fetch_news()
    
    # Step 2: Filter (Gemini ya raw)
    filtered = filter_news_gemini(news)
    
    # Step 3: Save
    save_daily_news(filtered)
    
    print("🎉 ALL DONE! Check daily.txt")