# MiniGoogle 🔍
A Big Data Search Engine built with Hadoop MapReduce and Flask.

## Requirements
- Ubuntu
- Hadoop 3.x
- Python 3.x
- pip install requests beautifulsoup4 lxml flask

## How to Run

### Step 1 — Collect Data
python3 scraper.py

### Step 2 — Upload to HDFS
hdfs dfs -mkdir -p /search_engine/pages
hdfs dfs -put crawled_pages/* /search_engine/pages/
hdfs dfs -put mapping.json /search_engine/

### Step 3 — Run MapReduce
hadoop jar $HADOOP_HOME/share/hadoop/tools/lib/hadoop-streaming-*.jar \
  -input /search_engine/pages/* \
  -output /search_engine/index \
  -mapper "python3 mapper.py" \
  -reducer "python3 reducer.py" \
  -file mapper.py \
  -file reducer.py

### Step 4 — Download Index
hdfs dfs -get /search_engine/index/part-00000 index.txt

### Step 5 — Run Website
python3 app.py

### Step 6 — Open Browser
http://127.0.0.1:5000
