from flask import Flask, request, jsonify, render_template
import json
import os

app = Flask(__name__)


# ========== Load Index & Mapping ==========
def load_index(filepath="index.txt"):
    index = {}
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split("\t")
            if len(parts) == 2:
                word, urls = parts
                index[word] = urls.split(",")
    return index


def load_mapping(filepath="mapping.json"):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


print("Loading index...")
index = load_index()
mapping = load_mapping()
print(f"Index loaded — {len(index)} words")

# ========== Cache ==========
cache = {}


# ========== Helper Functions ==========
def get_snippet(url, keywords):
    filename = None
    for fname, furl in mapping.items():
        if furl == url:
            filename = fname
            break
    if not filename:
        return ""
    filepath = os.path.join("crawled_pages", filename)
    if not os.path.exists(filepath):
        return ""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()
        text_lower = text.lower()
        for keyword in keywords:
            pos = text_lower.find(keyword.lower())
            if pos != -1:
                start = max(0, pos - 100)
                end = min(len(text), pos + 200)
                return text[start:end].strip()
    except:
        pass
    return ""


def count_occurrences(url, keywords):
    filename = None
    for fname, furl in mapping.items():
        if furl == url:
            filename = fname
            break
    if not filename:
        return 0
    filepath = os.path.join("crawled_pages", filename)
    if not os.path.exists(filepath):
        return 0
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read().lower()
        count = 0
        for keyword in keywords:
            count += text.count(keyword.lower())
        return count
    except:
        return 0


# ========== Routes ==========
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/search")
def search():
    query = request.args.get("q", "").strip().lower()
    if not query:
        return render_template("results.html", results=[], query="")

    # Check cache
    if query in cache:
        print(f"Cache hit: {query}")
        return render_template("results.html", results=cache[query], query=query)

    keywords = query.split()

    if len(keywords) == 1:
        urls = index.get(keywords[0], [])
    else:
        sets = [set(index.get(kw, [])) for kw in keywords]
        urls = list(sets[0].intersection(*sets[1:]))

    results = []
    for url in urls[:20]:
        snippet = get_snippet(url, keywords)
        count = count_occurrences(url, keywords)
        results.append({"url": url, "snippet": snippet, "count": count})

    # Sort by count
    results.sort(key=lambda x: x["count"], reverse=True)

    # Save to cache
    cache[query] = results

    return render_template("results.html", results=results, query=query)


@app.route("/open")
def open_url():
    url = request.args.get("url", "")
    query = request.args.get("q", "")
    return render_template("preview.html", url=url, query=query)


@app.route("/get_content")
def get_content():
    url = request.args.get("url", "")
    filename = None
    for fname, furl in mapping.items():
        if furl == url:
            filename = fname
            break
    if not filename:
        return jsonify({"text": "Content not found."})
    filepath = os.path.join("crawled_pages", filename)
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()
        return jsonify({"text": text})
    except:
        return jsonify({"text": "Could not load content."})


# ========== Run ==========
if __name__ == "__main__":
    app.run(debug=True, port=5000)
