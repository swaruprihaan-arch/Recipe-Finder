import json, urllib.request, string, time

BASE = "https://www.themealdb.com/api/json/v1/1"

def get(url):
    with urllib.request.urlopen(url, timeout=20) as r:
        return json.load(r)

all_meals = {}
for letter in string.ascii_lowercase:
    try:
        data = get(f"{BASE}/search.php?f={letter}")
    except Exception as e:
        print("fail", letter, e)
        continue
    meals = data.get("meals") or []
    for m in meals:
        all_meals[m["idMeal"]] = m
    print(letter, len(meals), "total so far", len(all_meals))
    time.sleep(0.1)

with open("real_meals.json", "w") as f:
    json.dump(list(all_meals.values()), f)

print("TOTAL REAL MEALS:", len(all_meals))
