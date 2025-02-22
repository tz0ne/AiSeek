# AISeek Demo - Heroku-Ready with Eccentric UI
# Deploy: pip install flask gunicorn, create Procfile + requirements.txt, git push to Heroku

import re
from collections import defaultdict
import math
from flask import Flask, request, render_template_string
import random
import os

# Simulated index (50 entries: 10 static, 40 X-like posts)
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
    10: {"url": "x.com/10", "content": "Latest AI breakthroughs trending now"}
}

# Simulated X crawler (replace with real X API later)
def simulate_x_crawler():
    x_base = len(index) + 1
    for i in range(40):
        post_id = x_base + i
        content = random.choice([
            f"AISeek’s crushing it—Google’s {random.choice(['done', 'toast', 'shaking'])}",
            f"Python + AI = {random.choice(['future', 'win', 'gold'])}",
            f"Search without {random.choice(['ads', 'SEO', 'crap'])}—AISeek delivers",
            f"AI breakthroughs: {random.choice(['real-time', 'mind-blowing', 'next-level'])}"
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

# Scoring: TF-IDF + recency + quality
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

# Search function
def aiseek_search(query):
    query_words = re.findall(r'\w+', query.lower())
    matching_docs = set()
    
    for word in query_words:
        if word in inverted_index:
            for doc_id, _ in inverted_index[word]:
                matching_docs.add(doc_id)
    
    results = []
    for doc_id in matching_docs:
        score = score_document(query_words, doc_id)
        results.append((score, doc_id))
    results.sort(reverse=True)
    
    if not results:
        return "No results found!", None, None
    
    top_doc = results[0][1]
    return (
        index[top_doc]["content"],
        f"Matches {query_words}, scored {results[0][0]:.2f} (recency + quality boosted)",
        index[top_doc]["url"]
    )

# Flask app
app = Flask(__name__)

# Google-inspired UI with eccentric AISeek logo
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>AISeek Search!</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; }
        .container { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; }
        .logo { font-size: 48px; font-weight: bold; color: #ff4500; text-shadow: 2px 2px #00b7ff; margin-bottom: 20px; }
        .logo span { color: #00b7ff; }
        .search-box { width: 100%; max-width: 600px; display: flex; justify-content: center; }
        .search-input { width: 80%; padding: 12px; font-size: 16px; border: 1px solid #dfe1e5; border-radius: 24px 0 0 24px; box-shadow: none; outline: none; }
        .search-button { padding: 12px 20px; font-size: 16px; background-color: #ff4500; color: white; border: none; border-radius: 0 24px 24px 0; cursor: pointer; }
        .search-button:hover { background-color: #e03e00; }
        .result { max-width: 600px; margin-top: 20px; text-align: left; }
        .result h3 { font-size: 20px; margin: 10px 0; }
        .result p { font-size: 14px; color: #555; margin: 5px 0; }
        .result a { color: #ff4500; text-decoration: none; }
        .result a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">AISeek <span>Search!</span></div>
        <form method="POST" class="search-box">
            <input type="text" name="query" class="search-input" placeholder="Search the AI way..." value="{{ query or '' }}">
            <button type="submit" class="search-button">Seek</button>
        </form>
        {% if context.result %}
            <div class="result">
                <h3>{{ context.result }}</h3>
                <p>{{ context.why }}</p>
                <p><a href="{{ context.source }}" target="_blank">{{ context.source }}</a></p>
            </div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def home():
    context = {"result": None, "why": None, "source": None}
    query = None
    if request.method == "POST":
        query = request.form["query"]
        context["result"], context["why"], context["source"] = aiseek_search(query)
    return render_template_string(HTML_TEMPLATE, context=context, query=query)

# Build index
simulate_x_crawler()
build_index()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting AISeek demo... Access at http://localhost:{port} or your Heroku URL")
    app.run(debug=False, host="0.0.0.0", port=port)