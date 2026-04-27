import sys

current_word = None
urls = set()

for line in sys.stdin:
    line = line.strip()
    parts = line.split("\t")

    if len(parts) != 2:
        continue

    word, url = parts

    if word == current_word:
        urls.add(url)
    else:
        if current_word:
            print(f"{current_word}\t{','.join(urls)}")
        current_word = word
        urls = {url}

# اطبع آخر كلمة
if current_word:
    print(f"{current_word}\t{','.join(urls)}")
