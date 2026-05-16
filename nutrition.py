import re

NUTRITION_DB: dict[str, list[float]] = {

    "куриное филе":       [113, 23.6, 1.9, 0.0],
    "курица":             [113, 23.6, 1.9, 0.0],
    "говядина":           [187, 18.9, 12.4, 0.0],
    "свинина":            [259, 16.0, 21.5, 0.0],
    "индейка":            [84,  19.2, 0.7,  0.0],
    "фарш куриный":       [143, 17.0, 8.0,  0.0],


    "лосось":             [206, 20.0, 13.4, 0.0],
    "тунец":              [96,  21.5, 1.0,  0.0],
    "треска":             [69,  16.0, 0.6,  0.0],
    "горбуша":            [142, 20.5, 6.5,  0.0],
    "креветки":           [95,  18.9, 2.2,  0.0],


    "яйцо":               [157, 12.7, 11.5, 0.7],
    "яйца":               [157, 12.7, 11.5, 0.7],
    "творог 5%":          [121, 17.2, 5.0,  1.8],
    "творог":             [121, 17.2, 5.0,  1.8],
    "молоко":             [52,  2.8,  3.2,  4.7],
    "кефир":              [56,  2.8,  3.2,  4.1],
    "сметана 15%":        [158, 2.6,  15.0, 3.0],
    "сыр":                [340, 26.0, 26.5, 0.0],
    "йогурт":             [68,  5.0,  3.2,  3.5],


    "гречка":             [343, 12.6, 3.3,  68.0],
    "рис бурый":          [337, 7.4,  2.7,  72.0],
    "рис":                [344, 6.7,  0.7,  79.0],
    "овсянка":            [352, 12.3, 6.1,  61.0],
    "геркулес":           [352, 12.3, 6.1,  61.0],
    "перловка":           [324, 9.3,  1.1,  73.7],
    "макароны":           [337, 10.4, 1.1,  74.2],


    "чечевица":           [295, 21.6, 1.1,  48.0],
    "нут":                [364, 19.0, 6.0,  61.0],
    "фасоль":             [298, 21.0, 2.0,  52.7],


    "брокколи":           [34,  2.8,  0.4,  6.6],
    "помидор":            [20,  0.6,  0.2,  4.2],
    "помидоры":           [20,  0.6,  0.2,  4.2],
    "огурец":             [15,  0.8,  0.1,  3.0],
    "морковь":            [35,  1.3,  0.1,  8.0],
    "картофель":          [80,  2.0,  0.4,  18.1],
    "болгарский перец":   [27,  1.3,  0.1,  5.7],
    "перец":              [27,  1.3,  0.1,  5.7],
    "кабачок":            [24,  0.6,  0.3,  4.6],
    "капуста":            [28,  1.8,  0.1,  4.7],
    "шпинат":             [23,  2.9,  0.4,  3.6],
    "лук":                [41,  1.4,  0.0,  10.4],
    "чеснок":             [149, 6.5,  0.5,  33.1],
    "свёкла":             [48,  1.5,  0.1,  11.8],


    "яблоко":             [47,  0.4,  0.4,  11.8],
    "банан":              [96,  1.5,  0.2,  21.8],
    "апельсин":           [43,  0.9,  0.2,  8.1],
    "груша":              [47,  0.4,  0.3,  10.9],


    "оливковое масло":    [884, 0.0,  99.8, 0.0],
    "подсолнечное масло": [884, 0.0,  99.9, 0.0],
    "сливочное масло":    [748, 0.5,  82.5, 0.8],


    "грецкий орех":       [654, 15.2, 65.2, 7.0],
    "миндаль":            [575, 21.2, 49.9, 13.0],
    "арахис":             [567, 25.8, 49.2, 16.1],


    "мёд":                [304, 0.8,  0.0,  80.3],
    "сахар":              [387, 0.0,  0.0,  99.7],
}


def calculate_kbju(ingredients_with_grams: dict[str, float]) -> dict:

    totals = {"calories": 0.0, "proteins": 0.0, "fats": 0.0, "carbs": 0.0}
    found  = {}
    missing = []

    for ingredient, grams in ingredients_with_grams.items():
        key = ingredient.lower().strip()

        data = NUTRITION_DB.get(key)
        if data is None:
            for db_key in NUTRITION_DB:
                if db_key in key or key in db_key:
                    data = NUTRITION_DB[db_key]
                    break

        if data:
            factor = grams / 100
            totals["calories"] += data[0] * factor
            totals["proteins"] += data[1] * factor
            totals["fats"]     += data[2] * factor
            totals["carbs"]    += data[3] * factor
            found[ingredient]  = grams
        else:
            missing.append(ingredient)

    result = {k: round(v) for k, v in totals.items()}
    result["found"]   = found
    result["missing"] = missing
    return result


def parse_ingredients_from_recipe(recipe_text: str) -> dict[str, float]:

    pattern = re.compile(
        r'([а-яёА-ЯЁa-zA-Z][а-яёА-ЯЁa-zA-Z\s%]+?)\s*[—–-]?\s*(\d+)\s*г(?:р(?:амм)?)?',
        re.IGNORECASE
    )
    result = {}
    for match in pattern.finditer(recipe_text):
        name  = match.group(1).strip().lower()
        grams = float(match.group(2))
        if 5 <= grams <= 2000:
            result[name] = grams
    return result


def check_allergens(ingredients: list[str], allergies: str) -> list[str]:

    if not allergies:
        return []
    allergen_list = [a.strip().lower() for a in allergies.split(",")]
    found = []
    for ingredient in ingredients:
        ing_lower = ingredient.lower()
        for allergen in allergen_list:
            if allergen and (allergen in ing_lower or ing_lower in allergen):
                found.append(ingredient)
    return found