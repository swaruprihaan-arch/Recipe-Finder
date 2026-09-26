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

DISH_NOUNS = ["Stew", "Curry", "Bake", "Skillet", "Casserole", "Platter", "Roast", "Bowl", "Delight", "Special"]
COLOR_CYCLE = ["#f4a261", "#e76f51", "#2a9d8f", "#588157", "#e07a5f", "#f2cc8f", "#81b29a", "#a3b18a", "#bc6c25", "#dda15e"]

def slugify(s):
    return re.sub(r"[^a-z0-9]+", "", s.lower())

def make_svg_thumb(area, emoji, color):
    import base64
    label = area if len(area) <= 18 else area[:16] + "…"
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="400" height="400">'
           f'<rect width="400" height="400" fill="{color}"/>'
           f'<text x="200" y="180" font-size="120" text-anchor="middle" dominant-baseline="middle">{emoji}</text>'
           f'<text x="200" y="300" font-size="26" font-family="sans-serif" font-weight="700" fill="white" text-anchor="middle">{label}</text>'
           f'</svg>')
    encoded = base64.b64encode(svg.encode("utf-8")).decode("ascii")
    return f"data:image/svg+xml;base64,{encoded}"

def build_synthetic(area, template, idx):
    category_key, category_label, ingredients = template
    dish_noun = DISH_NOUNS[idx % len(DISH_NOUNS)]
    name = f"{area} Style {category_label} {dish_noun}"
    meal_id = f"c{slugify(area)}-{slugify(category_key)}-{idx}"
    color = COLOR_CYCLE[idx % len(COLOR_CYCLE)]
    thumb = make_svg_thumb(area, "🍲", color)

    instructions = (
        f"[Community-style recipe] This is a generated {category_label.lower()} dish inspired by {area} cuisine, "
        f"created to fill a gap where no sourced recipe was available. It is NOT an authentic dish pulled from a "
        f"recipe database — treat it as a customizable starting template.\n\n"
        f"step 1\nPrepare all ingredients: chop the vegetables, mince the garlic, and measure out the spices.\n\n"
        f"step 2\nHeat the oil in a large pan over medium heat. Add the onion and garlic (if using) and cook until "
        f"softened, about 4-5 minutes.\n\n"
        f"step 3\nAdd the main ingredient ({ingredients[0][0].lower()}) and cook until browned or lightly cooked, "
        f"stirring occasionally.\n\n"
        f"step 4\nStir in the remaining ingredients along with the local spice blend. Reduce heat, cover, and simmer "
        f"until everything is cooked through and flavors have combined, about 20-30 minutes.\n\n"
        f"step 5\nTaste and adjust seasoning with salt as needed. Serve warm, garnished with fresh herbs if available."
    )

    meal = {
        "idMeal": meal_id, "strMeal": name, "strCategory": category_label, "strArea": area,
        "strMealThumb": thumb, "strInstructions": instructions, "strTags": "Community,Generated",
        "isVariant": True, "isSynthetic": True, "variantLabel": "Community",
    }
    for i, (ing_name, measure) in enumerate(ingredients, start=1):
        meal[f"strIngredient{i}"] = ing_name
        meal[f"strMeasure{i}"] = measure
    return meal

new_synthetic = []
for area in AREAS:
    for i in range(10):
        template = CATEGORY_TEMPLATES[i % len(CATEGORY_TEMPLATES)]
        new_synthetic.append(build_synthetic(area, template, i))

with open("community_recipes.json", "w") as f:
    json.dump(new_synthetic, f)

print("Community recipes generated:", len(new_synthetic))
