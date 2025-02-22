# AISeek Demo - Enhanced for Render with X API Prep (tweepy Fallback)
# Deploy: git push to Render with requirements.txt + Procfile

import re
from collections import defaultdict
import math
from flask import Flask, request, render_template_string, jsonify
import random
import os
import logging
import time
from functools import lru_cache

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AISeek")

try:
    import tweepy
except ImportError:
    logger.warning("tweepy not found—using mock X crawler only")
    tweepy = None

# Simulated index (10 static entries)
index = {
    1: {"url": "sci.org/1", "content": "AI transforms science with reasoning models"},
    2: {"url": "dev.net/2", "content": "Python beats Java for quick coding projects"},
    3: {"url": "edu.org/3", "content": "Learn AI with Python in 10 steps"},
    4: {"url": "tech.io/4", "content": "Google’s search is ad-heavy and slow"},
    5: {"url": "sci.org/5", "content": "Reasoning AI outsmarts keyword search"},
    6: {"url": "dev.net/6", "content": "Code smarter with AI tools"},
    7: {"url": "edu.org/7", "content": "Python and AI are the future of learning"},
    8: {"url": "tech.io/8", "content": "Ditch ads, embrace clean search"},
    9: {"url": "x.com/9", "content": "AISeek hype is real—new search king?"},
    10: {"url": "x.com/10", "content": "Latest AI breakthroughs trending in breaking news"}
}

# X API crawler using full auth (mocked if tweepy missing)
def x_crawler(api_key="dn3vr5sbsavMUYs9c6D3n712z", api_secret="AGHr2BnRDsal8Lais049XoDhiqSs3skZMs7u1FvpZHOlO46DZG", access_token="1453079771416518658-HFs0XFIwXCWcgcOwxxePnYV8TxyLka", access_token_secret="ALo0OvJj4LgFT4k4hPOhIg4v5Xv8GFLuAzI4Ke2WpIyWR", bearer_token="AAAAAAAAAAAAAAAAAAAAJDuzQEAAAAAaylsACwHhhGF%2BnW0gnSOXE%2BTdZw%3D5KnkixInU3af29mEEbzywv7SjZhtFTdCNk4GKtkRLCC4alyeFc"):
    if tweepy is None:
        logger.warning("tweepy not available—using mock crawler")
        simulate_x_crawler()
        return

    try:
        # Authenticate with OAuth 1.0a (full auth)
        if api_key and api_secret and access_token and access_token_secret:
            auth = tweepy.OAuthHandler(api_key, api_secret)
            auth.set_access_token(access_token, access_token_secret)
            api = tweepy.API(auth, wait_on_rate_limit=True)
        # Fallback to Bearer Token (simpler, read-only)
        elif bearer_token:
            client = tweepy.Client(bearer_token=bearer_token)
        else:
            raise ValueError("No valid X API credentials provided")

        # Pull recent tweets (e.g., #AI, #news, #breaking)
        query = "#AI OR #news OR #breaking OR #search -filter:retweets"
        if bearer_token:
            tweets = client.search_recent_tweets(query=query, max_results=50, tweet_fields=["created_at"])
        else:
            tweets = api.search_tweets(q=query, count=50, lang="en", tweet_mode="extended")

        x_base = len(index) + 1
        for i, tweet in enumerate(tweets.data if bearer_token else tweets):
            if tweet is not None:
                post_id = x_base + i
                content = tweet.text if bearer_token else (tweet.full_text if hasattr(tweet, "full_text") else tweet.text)
                index[post_id] = {
                    "url": f"x.com/{tweet.id}",
                    "content": content,
                    "timestamp": (tweet.created_at.strftime("%Y-%m-%d %H:%M:%S") if bearer_token 
                                else tweet.created_at.strftime("%Y-%m-%d %H:%M:%S"))
                }
        logger.info(f"Fetched {len(tweets.data if bearer_token else tweets)} tweets from X")
    except Exception as e:
        logger.error(f"X API error: {e}")
        # Fallback to mock if API fails
        simulate_x_crawler()

# Mock X crawler (fallback)
def simulate_x_crawler():
    x_base = len(index) + 1
    for i in range(50):
        post_id = x_base + i
        content = random.choice([
            f"AISeek’s crushing it—Google’s {random.choice(['done', 'toast', 'shaking'])} in latest breaking news {time.time()}",
            f"Python + AI = {random.choice(['future', 'win', 'gold'])}—news buzzing with breaking updates {time.time()}",
            f"Search without {random.choice(['ads', 'SEO', 'crap'])}—AISeek delivers fresh breaking news {time.time()}",
            f"AI breakthroughs: {random.choice(['real-time', 'mind-blowing', 'next-level'])} in today’s breaking news {time.time()}"
        ])
        index[post_id] = {
            "url": f"x.com/p{post_id}",
            "content": content,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        }

# Inverted index
inverted_index = defaultdict(list)

def build_index():
    for doc_id, doc in index.items():
        words = re.findall(r'\w+', doc["content"].lower())
        word_count = defaultdict(int)
        for word in words:
            word_count[word] += 1
        for word, count in word_count.items():
            inverted_index[word].append((doc_id, count))

# Expanded synonym map
SYNONYMS = {
    "news": ["info", "updates", "trending", "latest", "breaking"],
    "ai": ["artificial", "intelligence"],
    "search": ["find", "lookup", "seek"],
    "breaking": ["urgent", "hot", "fresh"]
}

@lru_cache(maxsize=100)  # Cache for performance
def expand_query(query_words):
    expanded = set(query_words)
    for word in query_words:
        for key, synonyms in SYNONYMS.items():
            if word == key or word in synonyms:
                expanded.update(synonyms)
                expanded.add(key)
    return list(expanded)

# Scoring
def score_document(query_words, doc_id):
    score = 0
    doc_words = re.findall(r'\w+', index[doc_id]["content"].lower())
    total_docs = len(index)
    
    for word in query_words:
        if word in inverted_index:
            for did, freq in inverted_index[word]:
                if did == doc_id:
                    tf = freq / len(doc_words)
                    idf = math.log(total_docs / len(inverted_index[word]))
                    score += tf * idf
    
    if doc_id > 10:  # X posts
        score += 0.3  # Recency
    if len(doc_words) > 5:  # Quality
        score += 0.2
    if any(kw in doc_words for kw in ["ai", "search", "news", "breaking"]):
        score += 0.5
    return score

# Search function (returns top 3)
def aiseek_search(query):
    logger.info(f"Searching: {query}")
    query_words = re.findall(r'\w+', query.lower())
    expanded_words = expand_query(tuple(query_words))  # Cached
    matching_docs = set()
    
    for word in expanded_words:
        if word in inverted_index:
            for doc_id, _ in inverted_index[word]:
                matching_docs.add(doc_id)
    
    results = []
    for doc_id in matching_docs:
        score = score_document(expanded_words, doc_id)
        results.append((score, doc_id))
    results.sort(reverse=True)
    
    if not results:
        return [("No results found!", None, None)]
    
    top_results = results[:3]  # Top 3
    return [(index[doc_id]["content"], 
             f"Matches {expanded_words}, scored {score:.2f} (recency + quality boosted)",
             index[doc_id]["url"]) for score, doc_id in top_results]

# Flask app
app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>AISeek Search!</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; text-align: center; }
        .logo { margin: 20px 0; }
        .logo img { max-width: 200px; height: auto; }
        .search-box { display: flex; justify-content: center; margin: 20px 0; }
        .search-input { width: 70%; max-width: 500px; padding: 12px; font-size: 16px; border: 1px solid #dfe1e5; border-radius: 24px 0 0 24px; box-shadow: 0 1px 6px rgba(32,33,36,.28); }
        .search-button { padding: 12px 20px; font-size: 16px; background: #ff4500; color: white; border: none; border-radius: 0 24px 24px 0; cursor: pointer; }
        .search-button:hover { background: #e03e00; }
        .loading { display: none; position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); font-size: 20px; color: #ff4500; }
        .results { text-align: left; margin-top: 20px; }
        .result { background: white; padding: 15px; margin-bottom: 10px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,.1); }
        .result h3 { font-size: 18px; margin: 0 0 5px; color: #ff4500; }
        .result p { font-size: 14px; color: #333; margin: 5px 0; }
        .result a { color: #00b7ff; text-decoration: none; }
        .result a:hover { text-decoration: underline; }
        .footer { margin-top: 20px; font-size: 12px; color: #666; }
        @media (max-width: 600px) { 
            .search-input { width: 60%; } 
            .logo img { max-width: 150px; }
        }
    </style>
    <script>
        document.addEventListener('submit', function(e) {
            var loading = document.querySelector('.loading');
            loading.style.display = 'block';
            setTimeout(function() { loading.style.display = 'none'; }, 2000); // Hide after 2s
        });
    </script>
</head>
<body>
    <div class="container">
        <div class="logo"><img src="{{ url_for('static', filename='aiseek_logo.png') }}" alt="AISeek Search!"></div>
        <form method="POST" class="search-box">
            <input type="text" name="query" class="search-input" placeholder="Search the AI way..." value="{{ query or '' }}" autofocus>
            <button type="submit" class="search-button">Seek</button>
        </form>
        <div class="loading">Seeking...</div>
        {% if results %}
            <div class="results">
                {% for result, why, source in results %}
                    <div class="result">
                        <h3>{{ result }}</h3>
                        <p>{{ why }}</p>
                        <p><a href="{{ source }}" target="_blank">{{ source }}</a></p>
                    </div>
                {% endfor %}
            </div>
        {% endif %}
        <div class="footer">Powered by xAI | No ads, just answers</div>
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def home():
    results = []
    query = None
    if request.method == "POST":
        query = request.form["query"]
        results = aiseek_search(query)
    return render_template_string(HTML_TEMPLATE, results=results, query=query)

@app.route("/health")
def health():
    logger.info("Health check hit")
    return "OK", 200

# Serve static files for logo
@app.route('/static/<path:filename>')
def serve_static(filename):
    return app.send_static_file(filename)

# Build index
x_crawler("", "", "1453079771416518658-HFs0XFIwXCWcgcOwxxePnYV8TxyLka", "ALo0OvJj4LgFT4k4hPOhIg4v5Xv8GFLuAzI4Ke2WpIyWR", "AAAAAAAAAAAAAAAAAAAAJDuzQEAAAAAaylsACwHhhGF%2BnW0gnSOXE%2BTdZw%3D5KnkixInU3af29mEEbzywv7SjZhtFTdCNk4GKtkRLCC4alyeFc")  # Use your full creds here
build_index()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    logger.info(f"Starting AISeek on port {port}")
    app.run(debug=False, host="0.0.0.0", port=port)