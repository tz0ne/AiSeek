# AISeek Demo - Improved for Render with Logo
# Deploy: git push to Render with requirements.txt + Procfile

import re
from collections import defaultdict
import math
from flask import Flask, request, render_template_string
import random
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AISeek")

# Simulated index
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
    10: {"url": "x.com/10", "content": "Latest AI breakthroughs trending in the news"}
}

# Simulated X crawler
def simulate_x_crawler():
    x_base = len(index) + 1
    for i in range(40):
        post_id = x_base + i
        content = random.choice([
            f"AISeek’s crushing it—Google’s {random.choice(['done', 'toast', 'shaking'])} in latest news",
            f"Python + AI = {random.choice(['future', 'win', 'gold'])}—news buzzing now",
            f"Search without {random.choice(['ads', 'SEO', 'crap'])}—AISeek delivers fresh news",
            f"AI breakthroughs: {random.choice(['real-time', 'mind-blowing', 'next-level'])} in today’s news"
        ])
        index[post_id] = {
            "url": f"x.com/p{post_id}",
            "content": content,
            "timestamp": f"2025-02-22 {random.randint(10, 23)}:{random.randint(0, 59):02d}"
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

# Simple synonym map
SYNONYMS = {
    "news": ["info", "updates", "trending"],
    "ai": ["artificial", "intelligence"],
    "search": ["find", "lookup"]
}

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
        score += 0.3
    if len(doc_words) > 5:  # Quality
        score += 0.2
    if "ai" in doc_words or "search" in doc_words:
        score += 0.5
    return score

# Search function (returns top 3)
def aiseek_search(query):
    logger.info(f"Searching: {query}")
    query_words = re.findall(r'\w+', query.lower())
    expanded_words = expand_query(query_words)
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
             f"Matches {expanded_words}, scored {score:.2f}",
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
        .results { text-align: left; margin-top: 20px; }
        .result { background: white; padding: 15px; margin-bottom: 10px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,.1); }
        .result h3 { font-size: 18px; margin: 0 0 5px; color: #ff4500; }
        .result p { font-size: 14px; color: #333; margin: 5px 0; }
        .result a { color: #00b7ff; text-decoration: none; }
        .result a:hover { text-decoration: underline; }
        @media (max-width: 600px) { 
            .search-input { width: 60%; } 
            .logo img { max-width: 150px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo"><img src="{{ url_for('static', filename='aiseek_logo.png') }}" alt="AISeek Search!"></div>
        <form method="POST" class="search-box">
            <input type="text" name="query" class="search-input" placeholder="Search the AI way..." value="{{ query or '' }}" autofocus>
            <button type="submit" class="search-button">Seek</button>
        </form>
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
simulate_x_crawler()
build_index()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    logger.info(f"Starting AISeek on port {port}")
    app.run(debug=False, host="0.0.0.0", port=port)