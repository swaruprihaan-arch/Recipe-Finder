import json, re

with open("real_meals.json") as f:
    real_meals = json.load(f)

def repl_rules(pairs):
    return [(re.compile(re.escape(a), re.IGNORECASE), b) for a, b in pairs]

TEMPLATES = [
    {"key": "vegan", "label": "Vegan", "rules": repl_rules([
        ("chicken breast", "Tofu"), ("chicken thigh", "Tofu"), ("chicken", "Tofu"),
        ("ground beef", "Plant-Based Mince"), ("beef", "Seitan"),
        ("pork", "Jackfruit"), ("turkey", "Tempeh"),
        ("bacon", "Smoked Coconut Bacon"), ("shrimp", "King Oyster Mushroom"),
        ("prawn", "King Oyster Mushroom"), ("fish", "Marinated Tofu"),
        ("salmon", "Marinated Carrot Lox"), ("lamb", "Mushroom & Walnut Mince"),
        ("egg", "Flax Egg"), ("butter", "Vegan Butter"),
        ("milk", "Oat Milk"), ("cream", "Coconut Cream"),
        ("cheese", "Vegan Cheese"), ("honey", "Maple Syrup"),
        ("yogurt", "Coconut Yogurt"), ("mayonnaise", "Vegan Mayonnaise"),
    ]), "add_ingredients": [("Nutritional Yeast", "1 tbsp")],
       "note": "Vegan adaptation: all animal products have been swapped for plant-based alternatives."},
    {"key": "vegetarian", "label": "Vegetarian", "rules": repl_rules([
        ("chicken breast", "Paneer"), ("chicken thigh", "Paneer"), ("chicken", "Paneer"),
        ("ground beef", "Lentil Mince"), ("beef", "Halloumi"),
        ("pork", "Mushroom"), ("turkey", "Paneer"),
        ("bacon", "Smoked Tempeh"), ("shrimp", "Baby Corn"),
        ("prawn", "Baby Corn"), ("fish", "Halloumi"),
        ("salmon", "Grilled Halloumi"), ("lamb", "Portobello Mushroom"),
    ]), "add_ingredients": [("Extra Vegetable Stock", "1 cup")],
       "note": "Vegetarian adaptation: meat and seafood have been replaced with hearty plant-based proteins."},
    {"key": "spicy", "label": "Extra Spicy", "rules": [],
       "add_ingredients": [("Fresh Red Chilli", "2 chopped"), ("Cayenne Pepper", "1 tsp"), ("Chilli Flakes", "1 tbsp")],
       "note": "Spicy twist: extra chillies and heat have been added throughout for a fiery kick."},
    {"key": "mild", "label": "Mild & Kid-Friendly", "rules": repl_rules([
        ("chilli powder", "Sweet Paprika"), ("cayenne", "Sweet Paprika"),
        ("hot sauce", "Ketchup"), ("jalapeno", "Bell Pepper"),
        ("red chilli", "Bell Pepper"), ("green chilli", "Bell Pepper"),
    ]), "add_ingredients": [],
       "note": "Mild version: spice levels have been toned down to make this dish kid-friendly."},
    {"key": "gluten_free", "label": "Gluten-Free", "rules": repl_rules([
        ("plain flour", "Gluten-Free Flour"), ("all-purpose flour", "Gluten-Free Flour"),
        ("flour", "Gluten-Free Flour"), ("pasta", "Gluten-Free Pasta"),
        ("spaghetti", "Gluten-Free Spaghetti"), ("breadcrumbs", "Gluten-Free Breadcrumbs"),
        ("soy sauce", "Tamari"), ("bread", "Gluten-Free Bread"),
        ("noodles", "Rice Noodles"),
    ]), "add_ingredients": [],
       "note": "Gluten-free adaptation: wheat-based ingredients have been swapped for gluten-free alternatives."},
    {"key": "low_carb", "label": "Low-Carb", "rules": repl_rules([
        ("rice", "Cauliflower Rice"), ("pasta", "Zucchini Noodles"),
        ("spaghetti", "Zucchini Noodles"), ("potato", "Turnip"),
        ("bread", "Lettuce Wrap"), ("noodles", "Shirataki Noodles"),
        ("sugar", "Stevia"),
    ]), "add_ingredients": [],
       "note": "Low-carb adaptation: starchy ingredients have been swapped for lighter, low-carb options."},
    {"key": "extra_cheesy", "label": "Extra Cheesy", "rules": [],
       "add_ingredients": [("Extra Cheddar Cheese", "100g grated"), ("Mozzarella", "50g")],
       "note": "Extra cheesy twist: loaded with additional melted cheese."},
    {"key": "smoky_bbq", "label": "Smoky BBQ", "rules": [],
       "add_ingredients": [("BBQ Sauce", "3 tbsp"), ("Smoked Paprika", "1 tsp")],
       "note": "Smoky BBQ twist: finished with barbecue sauce and smoked paprika for a charred, smoky flavor."},
    {"key": "mediterranean", "label": "Mediterranean Style", "rules": [],
       "add_ingredients": [("Feta Cheese", "80g crumbled"), ("Kalamata Olives", "10"), ("Dried Oregano", "1 tsp")],
       "note": "Mediterranean twist: finished with feta, olives, and oregano."},
    {"key": "air_fryer", "label": "Air Fryer Method", "rules": [], "add_ingredients": [],
       "note": "Air fryer method: instead of the original cooking method, cook at 200C in the air fryer, shaking halfway, until golden and cooked through (roughly two-thirds of the original time)."},
    {"key": "high_protein", "label": "High-Protein", "rules": [],
       "add_ingredients": [("Extra Chicken Breast", "150g diced"), ("Cooked Quinoa", "1 cup")],
       "note": "High-protein twist: extra lean protein and quinoa added to boost the protein content."},
    {"key": "one_pot", "label": "One-Pot Version", "rules": [], "add_ingredients": [],
       "note": "One-pot method: combine all ingredients into a single large pot or pan, and cook together in stages to minimize cleanup, following the same order of steps as the original recipe."},
]

def get_ingredients(meal):
    items = []
    for i in range(1, 21):
        name = (meal.get(f"strIngredient{i}") or "").strip()
        measure = (meal.get(f"strMeasure{i}") or "").strip()
        if name:
            items.append((name, measure))
    return items

def apply_template(meal, template):
    new_meal = dict(meal)
    base_id = meal["idMeal"]
    new_id = f"v{base_id}-{template['key']}"
    new_meal["idMeal"] = new_id
    new_meal["isVariant"] = True
    new_meal["variantLabel"] = template["label"]
    new_meal["strMeal"] = f"{meal['strMeal']} ({template['label']})"

    ingredients = get_ingredients(meal)
    new_ingredients = []
    for name, measure in ingredients:
        new_name = name
        for pattern, repl in template["rules"]:
            if pattern.search(new_name):
                new_name = pattern.sub(repl, new_name)
                break
        new_ingredients.append((new_name, measure))

    for name, measure in template["add_ingredients"]:
        new_ingredients.append((name, measure))

    for i in range(1, 21):
        new_meal.pop(f"strIngredient{i}", None)
        new_meal.pop(f"strMeasure{i}", None)
    for i, (name, measure) in enumerate(new_ingredients[:20], start=1):
        new_meal[f"strIngredient{i}"] = name
        new_meal[f"strMeasure{i}"] = measure

    original_instructions = meal.get("strInstructions", "")
    new_meal["strInstructions"] = f"[{template['label']} variant] {template['note']}\n\n{original_instructions}"

    existing_tags = (meal.get("strTags") or "").strip()
    tag_list = [t for t in existing_tags.split(",") if t] if existing_tags else []
    tag_list.append(template["label"])
    new_meal["strTags"] = ",".join(tag_list)

    return new_meal

variants = []
num_templates = len(TEMPLATES)
target_total = 1000
base_count = len(real_meals)

for idx, meal in enumerate(real_meals):
    t1 = TEMPLATES[idx % num_templates]
    variants.append(apply_template(meal, t1))

extra_needed = target_total - len(variants)
for idx in range(extra_needed):
    meal = real_meals[idx % base_count]
    t_first_index = idx % num_templates
    t2_index = (t_first_index + 1 + (idx // base_count)) % num_templates
    t2 = TEMPLATES[t2_index]
    variants.append(apply_template(meal, t2))

with open("variant_meals_ingredient.json", "w") as f:
    json.dump(variants, f)

print("REAL MEALS:", len(real_meals))
print("INGREDIENT VARIANTS GENERATED:", len(variants))
