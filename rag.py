import json
import os
from typing import Optional

RECIPES_FILE = os.path.join("knowledge_base", "recipes.json")


def load_recipes() -> list[dict]:
    if not os.path.exists(RECIPES_FILE):
        return []
    with open(RECIPES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _ingredients_match(recipe_ing: str, user_ing: str) -> bool:

    ri = recipe_ing.strip().lower()
    ui = user_ing.strip().lower()


    if ri == ui:
        return True

    if len(ri) >= 4 and len(ui) >= 4:
        return ri in ui or ui in ri


    return ri == ui


def search_recipe(
    ingredients: list[str],
    profile: dict,
    meal_type: str,
    top_k: int = 3,
) -> Optional[dict]:

    recipes = load_recipes()
    if not recipes:
        return None

    user_ings  = [i.strip().lower() for i in ingredients]
    conditions = [c.lower() for c in profile.get("conditions", [])]
    allergies  = [a.strip().lower() for a in profile.get("allergies", "").split(",") if a.strip()]
    meal_clean = (meal_type
                  .replace("🌅 ", "").replace("☀️ ", "")
                  .replace("🌙 ", "").replace("🍎 ", "").lower())

    scored = []

    for recipe in recipes:


        recipe_ings = [i.strip().lower() for i in recipe.get("ingredients", [])]
        matches = sum(
            1 for ri in recipe_ings
            if any(_ingredients_match(ri, ui) for ui in user_ings)
        )
        if matches == 0:
            continue
        score = matches * 10


        meal_map = {
            "завтрак": "завтрак", "обед": "обед",
            "ужин": "ужин", "перекус": "перекус",
        }
        meal_key = next((v for k, v in meal_map.items() if k in meal_clean), None)
        if meal_key and meal_key in recipe.get("meal_types", []):
            score += 5


        recipe_tags = [t.lower() for t in recipe.get("tags", [])]
        for cond in conditions:
            cond_short = cond.split(" ")[0].lower()
            if any(cond_short in tag for tag in recipe_tags):
                score += 8


        recipe_forbidden = [f.lower() for f in recipe.get("forbidden", [])]
        has_allergen = any(
            any(_ingredients_match(allergen, f) for f in recipe_forbidden) or
            any(_ingredients_match(allergen, ri) for ri in recipe_ings)
            for allergen in allergies
        )
        if has_allergen:
            continue

        scored.append((score, recipe))

    if not scored:
        return None

    scored.sort(key=lambda x: x[0], reverse=True)
    best_score, best_recipe = scored[0]


    return best_recipe if best_score >= 10 else None


def format_rag_context(recipe: dict) -> str:
    return f"""
[НАЙДЕН РЕЦЕПТ В БАЗЕ ЗНАНИЙ]
Используй этот рецепт как основу, адаптируй под медицинский профиль пользователя:

Название: {recipe['name']}
Ингредиенты: {', '.join(recipe['ingredients'])}
Время: {recipe['time_minutes']} минут
КБЖУ: {recipe['kbju']['calories']} ккал | Б:{recipe['kbju']['proteins']}г | Ж:{recipe['kbju']['fats']}г | У:{recipe['kbju']['carbs']}г
Почему подходит: {recipe['why_suitable']}
Рецепт: {recipe['recipe']}

Адаптируй граммовку и дай рекомендации исходя из медицинского профиля.
"""
