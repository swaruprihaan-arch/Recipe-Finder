import json, urllib.request, urllib.parse, time

HEADERS = {"User-Agent": "RecipeFinderApp/1.0 (local dev tool; contact: local-dev@example.com)"}

def commons_search(query, limit=40, retries=4):
    params = {
        "action": "query", "format": "json", "prop": "imageinfo",
        "generator": "search", "gsrsearch": query, "gsrlimit": limit,
        "gsrnamespace": 6, "iiprop": "url",
    }
    url = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(params)
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=20) as r:
                data = json.load(r)
            pages = data.get("query", {}).get("pages", {})
            urls = []
            for p in pages.values():
                infos = p.get("imageinfo") or []
                if infos:
                    u = infos[0]["url"]
                    base = u.split("?")[0]
                    if base.lower().endswith((".jpg", ".jpeg", ".png")):
                        urls.append(u)
            return urls
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(5 * (attempt + 1))
                continue
            raise
    return []

QUERIES = {
    "Chicken": ["roast chicken dish food"],
    "Beef": ["beef stew dish food", "beef steak plate food", "braised beef dish"],
    "Seafood": ["grilled fish seafood dish food", "shrimp dish food plate", "salmon fillet dish plate"],
    "Vegetarian": ["vegetarian vegetable dish food", "vegetable curry plate food", "salad bowl vegetables food"],
    "Dessert": ["dessert cake pastry food"],
    "Breakfast": ["breakfast plate food"],
    "Side Dish": ["rice side dish food"],
    "Starter": ["appetizer salad starter food", "bruschetta appetizer plate", "spring rolls appetizer plate", "dip appetizer plate food", "hummus appetizer plate food", "cheese platter appetizer", "stuffed appetizer plate food"],
    "Soup": ["soup bowl food"],
    "Bread": ["fresh baked bread food"],
}

pools = {}
for label, queries in QUERIES.items():
    all_urls = set()
    for q in queries:
        urls = commons_search(q, limit=40)
        all_urls.update(urls)
        time.sleep(1.5)
    pools[label] = list(all_urls)
    print(label, "->", len(pools[label]), "images")

with open("images/category_image_pools.json", "w") as f:
    json.dump(pools, f)

print("DONE. total images:", sum(len(v) for v in pools.values()))
