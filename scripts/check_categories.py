import json

with open('src/data/restaurants/_index.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

cats = {}
for r in data['restaurants']:
    c = r.get('category', 'Other')
    cats[c] = cats.get(c, 0) + 1

for c, count in sorted(cats.items(), key=lambda x: x[1], reverse=True):
    print(f"  {c}: {count}")
