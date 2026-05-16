import json
import os
from datetime import datetime

PROFILE_FILE = "user_profile.json"
HISTORY_FILE = "recipe_history.json"




def save_profile(profile: dict) -> None:
    with open(PROFILE_FILE, "w", encoding="utf-8") as f:
        json.dump(profile, f, ensure_ascii=False, indent=2)


def load_profile() -> dict | None:
    if not os.path.exists(PROFILE_FILE):
        return None
    try:
        with open(PROFILE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def delete_profile() -> None:
    if os.path.exists(PROFILE_FILE):
        os.remove(PROFILE_FILE)



def save_recipe(meal_type: str, ingredients: str, recipe_text: str, kbju: dict) -> None:

    history = load_history()
    history.append({
        "date":        datetime.now().strftime("%d.%m.%Y %H:%M"),
        "meal_type":   meal_type,
        "ingredients": ingredients,
        "recipe":      recipe_text,
        "kbju":        kbju,
    })
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def load_history() -> list:
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def clear_history() -> None:
    if os.path.exists(HISTORY_FILE):
        os.remove(HISTORY_FILE)


def get_weekly_stats() -> dict:

    history = load_history()
    if not history:
        return {}

    totals = {"calories": 0, "proteins": 0, "fats": 0, "carbs": 0}
    count  = 0

    for entry in history[-21:]:
        kbju = entry.get("kbju", {})
        if kbju:
            totals["calories"] += kbju.get("calories", 0)
            totals["proteins"] += kbju.get("proteins", 0)
            totals["fats"]     += kbju.get("fats", 0)
            totals["carbs"]    += kbju.get("carbs", 0)
            count += 1

    if count == 0:
        return {}

    return {
        "totals":  totals,
        "count":   count,
        "average": {k: round(v / count) for k, v in totals.items()},
    }