import os
import requests
from datetime import datetime, timedelta
import google.generativeai as genai

NEWS_API_KEY = os.getenv('NEWSAPI_KEY')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

def get_gemini_model():
    """API se available models list karke first model return karega"""
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        models = genai.list_models()
        for model in models:
            if 'generateContent' in model.supported_generation_methods:
                print(f"Using model: {model.name}")
                return genai.GenerativeModel(model.name)
        return None
    except Exception as e:
        print(f"Model detection error: {e}")
        return None

def fetch_news():
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    url = f'https://newsapi.org/v2/everything?q=india&from={yesterday}&sortBy=publishedAt&apiKey={NEWS_API_KEY}'
    response = requests.get(url)
    articles = response.json().get('articles', [])
    return [a for a in articles if 'publishedAt' in a][:10]

def filter_with_gemini(model, news_items):
    filtered = []
    prompt = """Filter this news ONLY for Bank/SSC/UPSC students. 
Keep Economy, Polity, Environment, IR, Govt schemes. Remove Sports/Entertainment. 
Output format:
Title: [title]
Summary: [1 sentence exam point]
Tag: [Bank/SSC/UPSC]

News: {news}"""
    
    for item in news_items:
        full_text = f"Title: {item.get('title', '')}
Desc: {item.get('description', '')}"
        try:
            response = model.generate_content(prompt.format(news=full_text))
            if "Title:" in response.text:
                filtered.append(response.text.strip())
        except:
            continue
    return filtered

def save_filtered_news(content):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
    with open('daily.txt', 'w', encoding='utf-8') as f:
        f.write(f"UPSC/SSC/Bank News - {timestamp}
{'='*50}

")
        for item in content:
            f.write(item + "

")
    print(f"Saved {len(content)} filtered news items")

if __name__ == "__main__":
    if not all([NEWS_API_KEY, GEMINI_API_KEY]):
        print("ERROR: API keys missing! Check GitHub Secrets.")
        exit(1)
    
    print("Detecting Gemini model...")
    model = get_gemini_model()
    if not model:
        print("ERROR: No Gemini model available!")
        exit(1)
    
    print("Fetching news...")
    news = fetch_news()
    print(f"Found {len(news)} articles")
    
    print("Filtering with Gemini AI...")
    filtered = filter_with_gemini(model, news)
    
    print("Saving to daily.txt...")
    save_filtered_news(filtered)
    print("Done!")