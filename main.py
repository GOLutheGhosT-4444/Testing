import os
import requests
from datetime import datetime, timedelta
import dateutil.parser
import google.generativeai as genai
import json

# Keys from GitHub Secrets (env vars)
NEWS_API_KEY = os.getenv('NEWSAPI_KEY')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GITHUB_TOKEN = os.getenv('REPO_TOKEN')  # For pushing back to repo

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def fetch_news():
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    url = f'https://newsapi.org/v2/everything?q=india&from={yesterday}&sortBy=publishedAt&apiKey={NEWS_API_KEY}'
    response = requests.get(url)
    articles = response.json().get('articles', [])
    return [a for a in articles if 'publishedAt' in a][:20]  # Top 20 recent

def filter_with_gemini(news_items):
    filtered = []
    prompt = """
    Filter this news for Bank PO, SSC CGL, UPSC CSE students only. 
    Keep ONLY relevant parts: Economy/Banking, Polity/Govt schemes, Environment/Science, International Relations, Social Issues.
    Remove ALL irrelevant: Sports, Entertainment, Local crime (unless national impact), Celebrity news.
    Output ONLY: Title: [short relevant title]
    Summary: [1-2 sentences exam points]
    Relevance: [Bank/SSC/UPSC tag]
    
    News: {news}
    """
    
    for item in news_items:
        full_text = f"Title: {item['title']}
Description: {item['description']}"
        try:
            response = model.generate_content(prompt.format(news=full_text))
            if response.text.strip():  # If relevant output
                filtered.append(response.text.strip())
        except:
            pass
    return filtered

def save_to_github(content):
    # Commit to daily.txt in repo root
    url = f"https://api.github.com/repos/{os.getenv('GITHUB_REPOSITORY')}/contents/daily.txt"
    # First, get current file (or create)
    # Use GitHub API to update - simplified, add full PUT logic if needed
    with open('daily.txt', 'w') as f:
        f.write(f"Filtered Current Affairs - {datetime.now().strftime('%Y-%m-%d')}

")
        f.write('

'.join(content))
    # In Actions, git add/commit/push will handle

if __name__ == "__main__":
    news = fetch_news()
    filtered_news = filter_with_gemini(news)
    save_to_github(filtered_news)
    print("Filtered news saved to daily.txt")