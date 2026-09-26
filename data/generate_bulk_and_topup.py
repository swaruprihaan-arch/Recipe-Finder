import json, re
from collections import Counter

AREAS = ["Afghan", "Albanian", "Algerian", "Andorran", "Angolan", "Antiguan, Barbudan", "Argentine", "Armenian", "Aruban", "Australian", "Austrian", "Azerbaijani", "Bahamian", "Bahraini", "Bangladeshi", "Barbadian", "Belarusian", "Belgian", "Belizean", "Beninese", "Bermudian", "Bhutanese", "Bolivian", "Bosnian, Herzegovinian", "Motswana", "Brazilian", "Bruneian", "Bulgarian", "Burkinabe", "Burundian", "Cambodian", "Cameroonian", "Canadian", "Cape Verdian", "Caymanian", "Central African", "Chadian", "Chilean", "Chinese", "Colombian", "Costa Rican", "Croatian", "Cuban", "Cypriot", "Czech", "Danish", "Djibouti", "Dominican", "Congolese", "Ecuadorean", "Egyptian", "Salvadoran", "Equatorial Guinean", "Eritrean", "Estonian", "Ethiopian", "Faroese", "Fijian", "Finnish", "French", "Gabonese", "Gambian", "Georgian", "German", "Ghanaian", "Gibraltar", "Greek", "Greenlandic", "Grenadian", "Guadeloupian", "Guamanian", "Guatemalan", "Channel Islander", "Guinean", "Guinea-Bissauan", "Guyanese", "Haitian", "Honduran", "Hong Konger", "Hungarian", "Icelander", "Indian", "Indonesian", "Iranian", "Iraqi", "Irish", "Israeli", "Italian", "Ivorian", "Jamaican", "Japanese", "Jordanian", "Kazakhstani", "Kenyan", "Kosovar", "Kuwaiti", "Kirghiz", "Laotian", "Latvian", "Lebanese", "Mosotho", "Liberian", "Libyan", "Liechtensteiner", "Lithuanian", "Luxembourger", "Malagasy", "Malawian", "Malaysian", "Maldivan", "Malian", "Maltese", "Mauritian", "Mexican", "Moldovan", "Mongolian", "Montenegrin", "Moroccan", "Mozambican", "Burmese", "Namibian", "Nepalese", "Dutch", "New Zealander", "Nicaraguan", "Nigerien", "Nigerian", "North Korean", "Macedonian", "Norwegian", "Omani", "Pakistani", "Palestinian", "Panamanian", "Papua New Guinean", "Paraguayan", "Peruvian", "Filipino", "Polish", "Portuguese", "Puerto Rican", "Qatari", "Romanian", "Russian", "Rwandan", "Saint Lucian", "Samoan", "Sammarinese", "Saudi Arabian", "Senegalese", "Serbian", "Seychellois", "Sierra Leonean", "Singaporean", "Slovak", "Slovene", "Solomon Islander", "Somali", "South African", "South Korean", "South Sudanese", "Spanish", "Sri Lankan", "Sudanese", "Surinamer", "Swedish", "Swiss", "Syrian", "Taiwanese", "Tadzhik", "Tanzanian", "Thai", "Togolese", "Tongan", "Trinidadian", "Tunisian", "Turkish", "Turkmen", "Tuvaluan", "Ugandan", "Ukrainian", "Emirati", "British", "American", "Uruguayan", "Uzbekistani", "Ni-Vanuatu", "Venezuelan", "Vietnamese", "Yemeni", "Zambian", "Zimbabwean", "Slovakia", "France", "Venezuela", "Argentina", "India", "United States", "Netherlands", "Norway"]
AREAS = sorted(set(AREAS))

CATEGORY_TEMPLATES = [
    ("Chicken", "Chicken", [("Chicken Thighs", "600g"), ("Onion", "1 diced"), ("Garlic", "3 cloves"), ("Local Spice Blend", "2 tbsp"), ("Vegetable Oil", "2 tbsp"), ("Salt", "1 tsp"), ("Stock", "300ml")]),
    ("Beef", "Beef", [("Beef Chunks", "600g"), ("Onion", "1 diced"), ("Garlic", "3 cloves"), ("Root Vegetables", "2 cups chopped"), ("Local Spice Blend", "2 tbsp"), ("Tomato Paste", "2 tbsp"), ("Stock", "400ml")]),
    ("Seafood", "Seafood", [("Firm White Fish", "500g"), ("Lime", "1"), ("Garlic", "2 cloves"), ("Fresh Herbs", "1 bunch chopped"), ("Vegetable Oil", "2 tbsp"), ("Local Spice Blend", "1 tbsp"), ("Salt", "1 tsp")]),
    ("Vegetarian", "Vegetarian", [("Mixed Vegetables", "500g chopped"), ("Chickpeas", "1 can drained"), ("Onion", "1 diced"), ("Garlic", "2 cloves"), ("Local Spice Blend", "2 tbsp"), ("Vegetable Oil", "2 tbsp"), ("Vegetable Stock", "300ml")]),
    ("Dessert", "Dessert", [("Flour", "2 cups"), ("Sugar", "1 cup"), ("Butter", "150g"), ("Eggs", "2"), ("Local Spice or Flavoring", "1 tsp"), ("Milk", "150ml")]),
    ("Breakfast", "Breakfast", [("Eggs", "3"), ("Flatbread or Local Bread", "2 pieces"), ("Tomatoes", "2 diced"), ("Onion", "1/2 diced"), ("Local Spice Blend", "1 tsp"), ("Vegetable Oil", "1 tbsp")]),
    ("Side", "Side Dish", [("Rice or Local Grain", "2 cups cooked"), ("Mixed Vegetables", "1 cup chopped"), ("Garlic", "2 cloves"), ("Vegetable Oil", "1 tbsp"), ("Local Spice Blend", "1 tsp"), ("Salt", "1/2 tsp")]),
    ("Starter", "Starter", [("Seasonal Vegetables", "300g"), ("Fresh Herbs", "1/2 bunch chopped"), ("Lemon or Lime", "1"), ("Olive or Vegetable Oil", "2 tbsp"), ("Local Spice Blend", "1 tsp"), ("Salt", "1/2 tsp")]),
    ("Soup", "Soup", [("Mixed Vegetables", "400g chopped"), ("Onion", "1 diced"), ("Garlic", "2 cloves"), ("Stock", "1 litre"), ("Local Spice Blend", "1 tbsp"), ("Fresh Herbs", "small handful")]),
    ("Bread", "Bread", [("Flour", "3 cups"), ("Yeast", "1 tsp"), ("Warm Water", "1 cup"), ("Salt", "1 tsp"), ("Olive or Vegetable Oil", "2 tbsp"), ("Local Spice or Seed Topping", "1 tbsp")]),
]

COOKING_METHODS = ["Grilled", "Baked", "Pan-Fried", "Steamed", "Slow-Cooked", "Stir-Fried", "Roasted", "Braised", "Poached", "Smoked", "Charcoal-Grilled"]
FLAVOR_PROFILES = ["Spicy", "Sweet & Savory", "Herb-Crusted", "Garlic Butter", "Citrus-Glazed", "Smoky", "Tangy", "Creamy", "Charred", "Umami-Rich", "Honey-Glazed"]
DISH_NOUNS = ["Stew", "Curry", "Bake", "Skillet", "Casserole", "Platter", "Roast", "Bowl", "Delight", "Special", "Medley", "Fusion Plate"]
COLOR_CYCLE = ["#f4a261", "#e76f51", "#2a9d8f", "#588157", "#e07a5f", "#f2cc8f", "#81b29a", "#a3b18a", "#bc6c25", "#dda15e"]

def slugify(s):
    return re.sub(r"[^a-z0-9]+", "", s.lower())

def make_svg_thumb(area, color):
    import base64
    label = area if len(area) <= 18 else area[:16] + "…"
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="400" height="400">'
           f'<rect width="400" height="400" fill="{color}"/>'
           f'<text x="200" y="200" font-size="90" text-anchor="middle" dominant-baseline="middle">🍲</text>'
           f'<text x="200" y="300" font-size="24" font-family="sans-serif" font-weight="700" fill="white" text-anchor="middle">{label}</text>'
           f'</svg>')
    encoded = base64.b64encode(svg.encode("utf-8")).decode("ascii")
    return f"data:image/svg+xml;base64,{encoded}"

def build_bulk_recipe(area, category_key, category_label, ingredients, method, flavor, noun, idx):
    meal_id = f"bulk-{slugify(area)}-{slugify(category_key)}-{idx}"
    name = f"{flavor} {method} {area} {category_label} {noun}"
    color = COLOR_CYCLE[idx % len(COLOR_CYCLE)]
    thumb = make_svg_thumb(area, color)
    instructions = (
        f"[Bulk-generated fusion recipe] This is an auto-generated {method.lower()}, {flavor.lower()} take on "
        f"{category_label.lower()} inspired by {area} cuisine. It is NOT an authentic dish pulled from a "
        f"recipe database — treat it as a customizable starting template rather than a sourced recipe.\n\n"
        f"step 1\nPrepare all ingredients: chop, measure, and season as listed.\n\n"
        f"step 2\nUsing the {method.lower()} method, cook the main ingredient ({ingredients[0][0].lower()}) "
        f"until done, adjusting time based on thickness/size.\n\n"
        f"step 3\nBuild the {flavor.lower()} flavor profile by incorporating the remaining ingredients and spice "
        f"blend at the appropriate stage of cooking.\n\n"
        f"step 4\nTaste and adjust seasoning. Serve warm, garnished with fresh herbs if available."
    )
    meal = {
        "idMeal": meal_id, "strMeal": name, "strCategory": category_label, "strArea": area,
        "strMealThumb": thumb, "strInstructions": instructions, "strTags": f"Bulk,{method},{flavor}",
        "isVariant": True, "isSynthetic": True, "isBulk": True, "variantLabel": "Fusion",
    }
    for i, (ing_name, measure) in enumerate(ingredients, start=1):
        meal[f"strIngredient{i}"] = ing_name
        meal[f"strMeasure{i}"] = measure
    return meal

TARGET_NEW = 20000
combos = [(area, cat) for area in AREAS for cat in CATEGORY_TEMPLATES]
per_combo = -(-TARGET_NEW // len(combos))

bulk_recipes = []
counter = 0
for area, (category_key, category_label, ingredients) in combos:
    for i in range(per_combo):
        if len(bulk_recipes) >= TARGET_NEW:
            break
        method = COOKING_METHODS[i % len(COOKING_METHODS)]
        flavor = FLAVOR_PROFILES[(i * 3 + 1) % len(FLAVOR_PROFILES)]
        noun = DISH_NOUNS[(i * 5 + 2) % len(DISH_NOUNS)]
        recipe = build_bulk_recipe(area, category_key, category_label, ingredients, method, flavor, noun, counter)
        bulk_recipes.append(recipe)
        counter += 1
    if len(bulk_recipes) >= TARGET_NEW:
        break

bulk_recipes = bulk_recipes[:TARGET_NEW]
with open("bulk_recipes.json", "w") as f:
    json.dump(bulk_recipes, f)
print("Bulk fusion recipes generated:", len(bulk_recipes))

# ---- top-up pass to guarantee >= 100 per country across everything ----
with open("real_meals.json") as f:
    real = json.load(f)
with open("variant_meals_ingredient.json") as f:
    ingredient_variants = json.load(f)
with open("community_recipes.json") as f:
    community = json.load(f)

allmeals = real + ingredient_variants + community + bulk_recipes
coverage = Counter(m.get("strArea") or "Unknown" for m in allmeals)

TARGET_MIN = 100
topup = []
for area in AREAS:
    have = coverage.get(area, 0)
    needed = TARGET_MIN - have
    idx = 0
    while needed > 0:
        cat_key, cat_label, ingredients = CATEGORY_TEMPLATES[idx % len(CATEGORY_TEMPLATES)]
        method = COOKING_METHODS[idx % len(COOKING_METHODS)]
        flavor = FLAVOR_PROFILES[(idx * 3 + 1) % len(FLAVOR_PROFILES)]
        noun = DISH_NOUNS[(idx * 5 + 2) % len(DISH_NOUNS)]
        recipe = build_bulk_recipe(area, cat_key, cat_label, ingredients, method, flavor, noun, 90000 + idx)
        recipe["idMeal"] = f"topup2-{slugify(area)}-{slugify(cat_key)}-{idx}"
        topup.append(recipe)
        idx += 1
        needed -= 1

with open("topup2_recipes.json", "w") as f:
    json.dump(topup, f)

print("Additional top-up recipes for 100+/country:", len(topup))
