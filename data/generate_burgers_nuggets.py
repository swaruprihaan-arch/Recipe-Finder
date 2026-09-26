import json, urllib.parse, hashlib
from collections import defaultdict

real = json.load(open("real_meals.json"))
by_cat = defaultdict(list)
for m in real:
    cat = m.get("strCategory") or "Miscellaneous"
    thumb = m.get("strMealThumb")
    if thumb:
        by_cat[cat].append(thumb)

burger_pool = by_cat.get("Beef") or by_cat.get("Miscellaneous") or [u for urls in by_cat.values() for u in urls]
chicken_pool = by_cat.get("Chicken") or [u for urls in by_cat.values() for u in urls]

def pick_image(pool, meal_id):
    h = int(hashlib.md5(meal_id.encode("utf-8")).hexdigest(), 16)
    return pool[h % len(pool)]

PROTEINS = ["Beef", "Chicken", "Turkey", "Lamb", "Black Bean (Vegetarian)", "Portobello Mushroom (Vegetarian)", "Salmon", "Pork", "Bison", "Falafel (Vegan)"]
TOPPINGS = [
    ["Cheddar Cheese", "Lettuce", "Tomato", "Red Onion", "Pickles"],
    ["Bacon", "BBQ Sauce", "Onion Rings", "Cheddar Cheese"],
    ["Blue Cheese", "Caramelized Onion", "Arugula"],
    ["Avocado", "Pepper Jack Cheese", "Chipotle Mayo", "Jalapeños"],
    ["Swiss Cheese", "Mushrooms", "Garlic Aioli"],
    ["Fried Egg", "Bacon", "Cheddar Cheese", "Hash Brown"],
    ["Feta Cheese", "Tzatziki", "Cucumber", "Red Onion"],
    ["Teriyaki Glaze", "Grilled Pineapple", "Provolone"],
    ["Mac and Cheese", "Bacon", "BBQ Sauce"],
    ["Kimchi", "Gochujang Mayo", "Sesame Seeds"],
]
STYLES = ["Classic", "Smash", "Double", "Deluxe", "Gourmet", "Spicy", "Smoky BBQ", "Loaded", "Juicy Lucy (Stuffed)", "Open-Face"]

burgers = []
for i in range(100):
    protein = PROTEINS[i % len(PROTEINS)]
    toppings = TOPPINGS[i % len(TOPPINGS)]
    style = STYLES[(i * 3 + 1) % len(STYLES)]
    meal_id = f"burger-{i}"
    name = f"{style} {protein} Burger"

    ingredients = [
        (f"{protein} Patty", "1 (180g)"),
        ("Burger Bun", "1"),
    ] + [(t, "to taste") for t in toppings] + [
        ("Salt", "1/2 tsp"),
        ("Black Pepper", "1/4 tsp"),
        ("Vegetable Oil", "1 tbsp"),
    ]

    instructions = (
        f"[Bulk-generated burger recipe] A {style.lower()} {protein.lower()} burger topped with "
        f"{', '.join(toppings).lower()}. This is an auto-generated recipe template, not sourced from a "
        f"recipe database.\n\n"
        f"step 1\nSeason the {protein.lower()} patty with salt and pepper.\n\n"
        f"step 2\nHeat oil in a skillet or grill over medium-high heat. Cook the patty 3-5 minutes per side "
        f"until done to your preference (or fully cooked through for poultry/pork).\n\n"
        f"step 3\nToast the bun lightly. Layer with {', '.join(toppings).lower()}.\n\n"
        f"step 4\nPlace the cooked patty on the bun, add the top bun, and serve immediately."
    )

    pool = chicken_pool if protein == "Chicken" else burger_pool
    thumb = pick_image(pool, meal_id)

    meal = {
        "idMeal": meal_id,
        "strMeal": name,
        "strCategory": "Burger",
        "strArea": "American",
        "strMealThumb": thumb,
        "strInstructions": instructions,
        "strTags": f"Burger,{style},{protein}",
        "isVariant": True,
        "isSynthetic": True,
        "variantLabel": "Burger",
    }
    for idx, (ing_name, measure) in enumerate(ingredients[:20], start=1):
        meal[f"strIngredient{idx}"] = ing_name
        meal[f"strMeasure{idx}"] = measure

    q = urllib.parse.quote_plus(f"{name} recipe")
    meal["strYoutube"] = f"https://www.youtube.com/results?search_query={q}"
    meal["strYoutubeIsSearch"] = True
    meal["strSource"] = f"https://www.google.com/search?q={q}"
    meal["strSourceIsSearch"] = True

    burgers.append(meal)

# --- Nuggets ---
NUGGET_STYLES = ["Classic Breaded", "Spicy Buffalo", "Honey Mustard Glazed", "Panko-Crusted", "Parmesan-Crusted",
                 "Sweet Chili", "Cornflake-Crusted", "Garlic Parmesan", "BBQ Glazed", "Popcorn-Style"]
NUGGET_PROTEINS = ["Chicken", "Chicken", "Chicken", "Chicken", "Chicken", "Chicken", "Chicken", "Chicken",
                    "Chicken", "Cauliflower (Vegetarian)"]

nuggets = []
for i in range(10):
    style = NUGGET_STYLES[i]
    protein = NUGGET_PROTEINS[i]
    meal_id = f"nugget-{i}"
    name = f"{style} {protein} Nuggets"

    ingredients = [
        (f"{protein} Breast, cubed" if protein == "Chicken" else "Cauliflower Florets", "500g"),
        ("Breadcrumbs", "1 cup"),
        ("Flour", "1/2 cup"),
        ("Eggs", "2 beaten"),
        ("Salt", "1 tsp"),
        ("Black Pepper", "1/2 tsp"),
        ("Paprika", "1 tsp"),
        ("Vegetable Oil", "for frying"),
    ]

    instructions = (
        f"[Bulk-generated nugget recipe] {style} {protein.lower()} nuggets, breaded and fried until golden. "
        f"This is an auto-generated recipe template, not sourced from a recipe database.\n\n"
        f"step 1\nCut the {protein.lower()} into bite-sized pieces (or break cauliflower into florets).\n\n"
        f"step 2\nSet up a breading station: flour, beaten eggs, and breadcrumbs mixed with salt, pepper, and paprika.\n\n"
        f"step 3\nDredge each piece in flour, then egg, then breadcrumbs, pressing to coat evenly.\n\n"
        f"step 4\nFry in hot oil (180C) for 4-6 minutes until golden and cooked through, or bake at 200C for "
        f"18-20 minutes, flipping halfway.\n\n"
        f"step 5\nDrain on paper towels and serve with your favorite dipping sauce."
    )

    thumb = pick_image(chicken_pool, meal_id)

    meal = {
        "idMeal": meal_id,
        "strMeal": name,
        "strCategory": "Nuggets",
        "strArea": "American",
        "strMealThumb": thumb,
        "strInstructions": instructions,
        "strTags": f"Nuggets,{style},{protein}",
        "isVariant": True,
        "isSynthetic": True,
        "variantLabel": "Nuggets",
    }
    for idx, (ing_name, measure) in enumerate(ingredients[:20], start=1):
        meal[f"strIngredient{idx}"] = ing_name
        meal[f"strMeasure{idx}"] = measure

    q = urllib.parse.quote_plus(f"{name} recipe")
    meal["strYoutube"] = f"https://www.youtube.com/results?search_query={q}"
    meal["strYoutubeIsSearch"] = True
    meal["strSource"] = f"https://www.google.com/search?q={q}"
    meal["strSourceIsSearch"] = True

    nuggets.append(meal)

with open("burger_nugget_recipes.json", "w") as f:
    json.dump(burgers + nuggets, f)

print("Burgers:", len(burgers))
print("Nuggets:", len(nuggets))
