from __future__ import annotations

from datetime import date, datetime, timedelta

from sqlalchemy import select

from .db import Base, engine, SessionLocal
from .models import HistoricalMenu, HistoricalMenuItem, Menu, MenuComment, MenuItem, NutrientThreshold, Recipe


RECIPES = [
    {"recipe_id": 1, "recipe_name": "Cinnamon Oatmeal with Apples", "meal_type": "breakfast", "category": "grain", "calories": 180, "sodium_mg": 120, "protein_g": 6, "fiber_g": 5, "fat_g": 3, "tags": ["whole grain", "vegetarian", "low sodium"], "is_approved": True},
    {"recipe_id": 2, "recipe_name": "Scrambled Eggs with Spinach", "meal_type": "breakfast", "category": "entree", "calories": 210, "sodium_mg": 330, "protein_g": 14, "fiber_g": 2, "fat_g": 14, "tags": ["high protein"], "is_approved": True},
    {"recipe_id": 3, "recipe_name": "Whole Wheat Toast", "meal_type": "breakfast", "category": "grain", "calories": 110, "sodium_mg": 170, "protein_g": 4, "fiber_g": 3, "fat_g": 1, "tags": ["whole grain"], "is_approved": True},
    {"recipe_id": 4, "recipe_name": "Low Fat Milk", "meal_type": "breakfast", "category": "milk", "calories": 90, "sodium_mg": 130, "protein_g": 8, "fiber_g": 0, "fat_g": 2, "tags": ["dairy"], "is_approved": True},
    {"recipe_id": 5, "recipe_name": "Turkey Sausage Patty", "meal_type": "breakfast", "category": "entree", "calories": 150, "sodium_mg": 420, "protein_g": 11, "fiber_g": 0, "fat_g": 11, "tags": ["protein"], "is_approved": True},
    {"recipe_id": 6, "recipe_name": "Blueberry Yogurt Parfait", "meal_type": "breakfast", "category": "fruit", "calories": 160, "sodium_mg": 85, "protein_g": 9, "fiber_g": 3, "fat_g": 3, "tags": ["dairy", "fruit"], "is_approved": True},
    {"recipe_id": 7, "recipe_name": "Chicken and Brown Rice Bowl", "meal_type": "lunch", "category": "entree", "calories": 340, "sodium_mg": 520, "protein_g": 24, "fiber_g": 4, "fat_g": 10, "tags": ["high protein"], "is_approved": True},
    {"recipe_id": 8, "recipe_name": "Roasted Sweet Potatoes", "meal_type": "lunch", "category": "vegetable", "calories": 120, "sodium_mg": 65, "protein_g": 2, "fiber_g": 4, "fat_g": 4, "tags": ["vegetarian", "low sodium"], "is_approved": True},
    {"recipe_id": 9, "recipe_name": "Steamed Broccoli", "meal_type": "lunch", "category": "vegetable", "calories": 55, "sodium_mg": 40, "protein_g": 4, "fiber_g": 4, "fat_g": 1, "tags": ["low sodium"], "is_approved": True},
    {"recipe_id": 10, "recipe_name": "Brown Rice Pilaf", "meal_type": "lunch", "category": "grain", "calories": 160, "sodium_mg": 140, "protein_g": 4, "fiber_g": 3, "fat_g": 3, "tags": ["whole grain"], "is_approved": True},
    {"recipe_id": 11, "recipe_name": "Apple Slices", "meal_type": "lunch", "category": "fruit", "calories": 60, "sodium_mg": 0, "protein_g": 0, "fiber_g": 3, "fat_g": 0, "tags": ["fresh fruit", "low sodium"], "is_approved": True},
    {"recipe_id": 12, "recipe_name": "Garden Salad with Italian Dressing", "meal_type": "lunch", "category": "vegetable", "calories": 80, "sodium_mg": 120, "protein_g": 2, "fiber_g": 2, "fat_g": 5, "tags": ["vegetarian"], "is_approved": True},
    {"recipe_id": 13, "recipe_name": "Baked Fish with Lemon", "meal_type": "dinner", "category": "entree", "calories": 280, "sodium_mg": 260, "protein_g": 27, "fiber_g": 0, "fat_g": 12, "tags": ["high protein", "low sodium"], "is_approved": True},
    {"recipe_id": 14, "recipe_name": "Mashed Potatoes", "meal_type": "dinner", "category": "side", "calories": 150, "sodium_mg": 180, "protein_g": 3, "fiber_g": 2, "fat_g": 5, "tags": ["comfort food"], "is_approved": True},
    {"recipe_id": 15, "recipe_name": "Green Beans Almondine", "meal_type": "dinner", "category": "vegetable", "calories": 95, "sodium_mg": 55, "protein_g": 3, "fiber_g": 4, "fat_g": 5, "tags": ["low sodium"], "is_approved": True},
    {"recipe_id": 16, "recipe_name": "Whole Wheat Dinner Roll", "meal_type": "dinner", "category": "grain", "calories": 120, "sodium_mg": 150, "protein_g": 4, "fiber_g": 2, "fat_g": 2, "tags": ["whole grain"], "is_approved": True},
    {"recipe_id": 17, "recipe_name": "Fresh Orange", "meal_type": "dinner", "category": "fruit", "calories": 70, "sodium_mg": 0, "protein_g": 1, "fiber_g": 3, "fat_g": 0, "tags": ["fresh fruit"], "is_approved": True},
    {"recipe_id": 18, "recipe_name": "Baked Chicken Thigh", "meal_type": "dinner", "category": "entree", "calories": 310, "sodium_mg": 430, "protein_g": 28, "fiber_g": 0, "fat_g": 18, "tags": ["protein"], "is_approved": True},
    {"recipe_id": 19, "recipe_name": "Turkey Meatloaf", "meal_type": "dinner", "category": "entree", "calories": 290, "sodium_mg": 500, "protein_g": 26, "fiber_g": 1, "fat_g": 15, "tags": ["high protein"], "is_approved": True},
    {"recipe_id": 20, "recipe_name": "Carrot Raisin Salad", "meal_type": "lunch", "category": "vegetable", "calories": 110, "sodium_mg": 95, "protein_g": 1, "fiber_g": 3, "fat_g": 4, "tags": ["sweet", "vegetarian"], "is_approved": True},
    {"recipe_id": 21, "recipe_name": "Chicken Noodle Soup", "meal_type": "lunch", "category": "entree", "calories": 220, "sodium_mg": 670, "protein_g": 16, "fiber_g": 2, "fat_g": 7, "tags": ["warm meal"], "is_approved": True},
    {"recipe_id": 22, "recipe_name": "Low Fat Cottage Cheese", "meal_type": "snack", "category": "milk", "calories": 100, "sodium_mg": 360, "protein_g": 13, "fiber_g": 0, "fat_g": 2, "tags": ["high protein"], "is_approved": True},
    {"recipe_id": 23, "recipe_name": "Whole Grain Crackers", "meal_type": "snack", "category": "grain", "calories": 130, "sodium_mg": 150, "protein_g": 3, "fiber_g": 4, "fat_g": 3, "tags": ["whole grain"], "is_approved": True},
    {"recipe_id": 24, "recipe_name": "Peanut Butter Banana Sandwich", "meal_type": "snack", "category": "entree", "calories": 230, "sodium_mg": 210, "protein_g": 8, "fiber_g": 4, "fat_g": 10, "tags": ["protein", "fruit"], "is_approved": True},
    {"recipe_id": 25, "recipe_name": "Stewed Pears", "meal_type": "snack", "category": "fruit", "calories": 85, "sodium_mg": 15, "protein_g": 1, "fiber_g": 3, "fat_g": 0, "tags": ["low sodium"], "is_approved": True},
    {"recipe_id": 26, "recipe_name": "Vegetable Chili", "meal_type": "dinner", "category": "entree", "calories": 260, "sodium_mg": 410, "protein_g": 15, "fiber_g": 9, "fat_g": 7, "tags": ["high fiber", "vegetarian"], "is_approved": True},
    {"recipe_id": 27, "recipe_name": "Cornbread Muffin", "meal_type": "dinner", "category": "grain", "calories": 170, "sodium_mg": 240, "protein_g": 3, "fiber_g": 2, "fat_g": 5, "tags": ["whole grain"], "is_approved": True},
    {"recipe_id": 28, "recipe_name": "Cauliflower Mash", "meal_type": "dinner", "category": "vegetable", "calories": 75, "sodium_mg": 50, "protein_g": 3, "fiber_g": 3, "fat_g": 2, "tags": ["low sodium", "vegetarian"], "is_approved": True},
    {"recipe_id": 29, "recipe_name": "Baked Apples with Cinnamon", "meal_type": "snack", "category": "fruit", "calories": 95, "sodium_mg": 20, "protein_g": 1, "fiber_g": 4, "fat_g": 1, "tags": ["dessert"], "is_approved": True},
    {"recipe_id": 30, "recipe_name": "Cheddar Cheese Slice", "meal_type": "snack", "category": "milk", "calories": 110, "sodium_mg": 180, "protein_g": 7, "fiber_g": 0, "fat_g": 9, "tags": ["dairy"], "is_approved": True},
    {"recipe_id": 31, "recipe_name": "Lentil Stew", "meal_type": "lunch", "category": "entree", "calories": 240, "sodium_mg": 290, "protein_g": 16, "fiber_g": 10, "fat_g": 4, "tags": ["high fiber", "vegetarian"], "is_approved": True},
    {"recipe_id": 32, "recipe_name": "Spinach Salad", "meal_type": "lunch", "category": "vegetable", "calories": 70, "sodium_mg": 45, "protein_g": 2, "fiber_g": 3, "fat_g": 4, "tags": ["low sodium"], "is_approved": True},
    {"recipe_id": 33, "recipe_name": "Turkey Sandwich on Wheat", "meal_type": "lunch", "category": "entree", "calories": 320, "sodium_mg": 560, "protein_g": 19, "fiber_g": 4, "fat_g": 8, "tags": ["whole grain"], "is_approved": True},
    {"recipe_id": 34, "recipe_name": "Mixed Berry Cup", "meal_type": "lunch", "category": "fruit", "calories": 65, "sodium_mg": 0, "protein_g": 1, "fiber_g": 4, "fat_g": 0, "tags": ["fresh fruit"], "is_approved": True},
    {"recipe_id": 35, "recipe_name": "Rice Pudding", "meal_type": "snack", "category": "grain", "calories": 140, "sodium_mg": 110, "protein_g": 4, "fiber_g": 1, "fat_g": 4, "tags": ["dessert"], "is_approved": True},
    {"recipe_id": 36, "recipe_name": "Grilled Tofu with Sesame", "meal_type": "dinner", "category": "entree", "calories": 220, "sodium_mg": 340, "protein_g": 18, "fiber_g": 2, "fat_g": 11, "tags": ["vegetarian", "high protein"], "is_approved": True},
    {"recipe_id": 37, "recipe_name": "Barley Pilaf", "meal_type": "dinner", "category": "grain", "calories": 155, "sodium_mg": 95, "protein_g": 4, "fiber_g": 5, "fat_g": 2, "tags": ["whole grain", "low sodium"], "is_approved": True},
    {"recipe_id": 38, "recipe_name": "Honey Glazed Carrots", "meal_type": "dinner", "category": "vegetable", "calories": 85, "sodium_mg": 75, "protein_g": 1, "fiber_g": 3, "fat_g": 2, "tags": ["vegetarian"], "is_approved": True},
    {"recipe_id": 39, "recipe_name": "Fruit Salad Cup", "meal_type": "snack", "category": "fruit", "calories": 75, "sodium_mg": 10, "protein_g": 1, "fiber_g": 3, "fat_g": 0, "tags": ["fresh fruit", "low sodium"], "is_approved": True},
    {"recipe_id": 40, "recipe_name": "Egg Salad Sandwich", "meal_type": "lunch", "category": "entree", "calories": 310, "sodium_mg": 530, "protein_g": 14, "fiber_g": 3, "fat_g": 18, "tags": ["protein"], "is_approved": True},
]


def _legacy_ingredients(row: dict) -> list[str]:
    name = row["recipe_name"].lower()
    category = row["category"]
    if "oatmeal" in name:
        return ["rolled oats", "apples", "cinnamon", "low fat milk", "brown sugar"]
    if "egg" in name:
        return ["eggs", "spinach", "whole wheat bread", "light mayonnaise", "black pepper"]
    if "milk" in name:
        return ["1% low fat milk"]
    if "yogurt" in name:
        return ["low fat yogurt", "blueberries", "whole grain granola"]
    if "rice" in name:
        return ["brown rice", "low sodium vegetable stock", "onion", "parsley"]
    if "tofu" in name:
        return ["firm tofu", "sesame seeds", "low sodium soy sauce", "scallions"]
    if "lentil" in name:
        return ["lentils", "carrots", "celery", "tomatoes", "low sodium broth"]
    if "chicken" in name:
        return ["chicken", "herbs", "garlic", "low sodium broth"]
    if "turkey" in name:
        return ["turkey", "whole wheat bread crumbs", "onion", "herbs"]
    if "fish" in name:
        return ["white fish", "lemon", "parsley", "olive oil"]
    if category == "fruit":
        return [row["recipe_name"].lower(), "fresh fruit"]
    if category == "vegetable":
        return [row["recipe_name"].lower(), "vegetables", "olive oil", "herbs"]
    if category == "grain":
        return [row["recipe_name"].lower(), "whole grain ingredient", "low sodium seasoning"]
    if category == "milk":
        return [row["recipe_name"].lower(), "dairy or calcium-fortified equivalent"]
    return [row["recipe_name"].lower(), "approved menu ingredient", "low sodium seasoning"]


def _legacy_claims(row: dict) -> list[str]:
    claims = set(row.get("tags", []))
    if row["sodium_mg"] <= 140:
        claims.add("low sodium")
    if row["protein_g"] >= 15:
        claims.add("high protein")
    if row["fiber_g"] >= 5:
        claims.add("high fiber")
    if row["category"] == "grain" and any("whole" in tag for tag in row.get("tags", [])):
        claims.add("whole grain")
    if row["category"] in {"fruit", "vegetable"}:
        claims.add("good source of vitamin c")
    if row["category"] == "milk":
        claims.add("good source of calcium")
    return sorted(claims)


def _vitamin_c(row: dict) -> float:
    if row["category"] == "fruit":
        return 35.0
    if row["category"] == "vegetable":
        return 28.0
    return 2.0


def _calcium(row: dict) -> float:
    if row["category"] == "milk":
        return 300.0
    if row["category"] == "vegetable":
        return 45.0
    return 15.0


for recipe in RECIPES:
    recipe.update(
        {
            "ingredients": _legacy_ingredients(recipe),
            "instructions": [
                "Review approved production record before service.",
                "Prepare according to approved Simple Servings recipe procedure.",
                "Hold and serve using the portion size listed for the menu.",
            ],
            "serving_size": "1 serving",
            "yield_servings": 50,
            "scale_note": "Use Scale to serving(s) in the recipe view to adjust production quantities.",
            "contributed_by": "NYC Aging Nutrition Unit",
            "created_on": date(2025, (recipe["recipe_id"] % 12) + 1, (recipe["recipe_id"] % 24) + 1),
            "is_public": True,
            "is_favorite": recipe["recipe_id"] in {1, 4, 7, 10, 11, 13, 31, 33, 34, 37},
            "is_dead": False,
            "nutrient_claims": _legacy_claims(recipe),
            "vitamin_c_mg": _vitamin_c(recipe),
            "calcium_mg": _calcium(recipe),
        }
    )

RECIPES.extend(
    [
        {
            "recipe_id": 41,
            "recipe_name": "Three Bean Vegetable Chili",
            "meal_type": "lunch",
            "category": "entree",
            "calories": 275,
            "sodium_mg": 410,
            "protein_g": 14,
            "fiber_g": 11,
            "fat_g": 6,
            "tags": ["pending review", "Full recipe with ingredients and directions", "plant-based", "high fiber", "entree"],
            "is_approved": False,
            "ingredients": ["low sodium kidney beans", "black beans", "pinto beans", "tomatoes", "onions", "bell peppers", "chili powder"],
            "instructions": ["Combine vegetables, beans, tomatoes, and seasoning.", "Simmer until vegetables are tender.", "Hold hot and serve one measured portion."],
            "serving_size": "1 cup",
            "yield_servings": 60,
            "scale_note": "\n".join(
                [
                    "Submission type: Full recipe with ingredients and directions",
                    "Contact Person: Astoria NSC",
                    "Preferred E-mail Address: menu.staff@astoriansc.example",
                    "Can be made public: Yes",
                    "Recipe source: A recipe created by our organization",
                    "Recipe file names: three-bean-vegetable-chili.pdf",
                    "Comments: Provider requests review for plant-based entree rotation.",
                ]
            ),
            "contributed_by": "Astoria NSC",
            "created_on": date(2026, 7, 18),
            "is_public": True,
            "is_favorite": False,
            "is_dead": False,
            "nutrient_claims": ["high fiber", "plant-based entree"],
            "vitamin_c_mg": 22,
            "calcium_mg": 75,
        },
        {
            "recipe_id": 42,
            "recipe_name": "Southwest Brown Rice Bowl",
            "meal_type": "lunch",
            "category": "grain",
            "calories": 365,
            "sodium_mg": 690,
            "protein_g": 12,
            "fiber_g": 7,
            "fat_g": 9,
            "tags": ["pending review", "Recipe nutrition analysis", "whole grain", "grain"],
            "is_approved": False,
            "ingredients": ["Vegetables per serving: corn 1/4 cup, peppers 1/4 cup", "Plant-based protein per serving: black beans 1/4 cup", "Fruit per serving: 0"],
            "instructions": ["Review the submitted recipe nutrition analysis panel."],
            "serving_size": "1 serving from analysis",
            "yield_servings": 48,
            "scale_note": "\n".join(
                [
                    "Submission type: Recipe nutrition analysis",
                    "Contact Person: ABSW OAC",
                    "Preferred E-mail Address: nutrition@abswoac.example",
                    "Can be made public: Yes",
                    "Recipe Yield: 48 servings",
                    "Number of Servings: 48",
                    "Nutrition Facts Panel file names: southwest-brown-rice-analysis.xlsx",
                    "Vegetables Per Serving: corn 1/4 cup, peppers 1/4 cup",
                    "Plant-Based Protein Per Serving: black beans 1/4 cup",
                    "Fruit Per Serving: 0",
                ]
            ),
            "contributed_by": "ABSW OAC",
            "created_on": date(2026, 7, 20),
            "is_public": True,
            "is_favorite": False,
            "is_dead": False,
            "nutrient_claims": ["whole grain", "good source of fiber"],
            "vitamin_c_mg": 18,
            "calcium_mg": 40,
        },
        {
            "recipe_id": 43,
            "recipe_name": "Reduced Sodium Turkey Patty",
            "meal_type": "breakfast",
            "category": "entree",
            "calories": 145,
            "sodium_mg": 360,
            "protein_g": 13,
            "fiber_g": 0,
            "fat_g": 8,
            "tags": ["pending review", "Pre-prepared product label", "protein", "breakfast"],
            "is_approved": False,
            "ingredients": ["Manufacturer: Metro Food Service", "Serving size: 1 patty", "Nutrition Facts panel files: reduced-sodium-turkey-patty-label.pdf"],
            "instructions": ["Review the pre-prepared product label and ingredient list."],
            "serving_size": "1 patty",
            "yield_servings": 1,
            "scale_note": "\n".join(
                [
                    "Submission type: Pre-prepared product label",
                    "Contact Person: Ridgewood OAC",
                    "Preferred E-mail Address: catering@ridgewoodoac.example",
                    "Can be made public: No",
                    "Manufacturer: Metro Food Service",
                    "Serving Size: 1 patty",
                    "Saturated Fat (g): 2.5",
                    "Trans Fat (g): 0",
                    "Cholesterol (mg): 35",
                    "Total Carbohydrate (g): 4",
                    "Total Sugars (g): 0",
                    "Added Sugars (g): 0",
                    "Vitamin D (mcg): 0",
                    "Iron (mg): 1.2",
                    "Potassium (mg): 180",
                    "Nutrition Facts Panel and Ingredient List file names: reduced-sodium-turkey-patty-label.pdf",
                ]
            ),
            "contributed_by": "Ridgewood OAC",
            "created_on": date(2026, 7, 21),
            "is_public": False,
            "is_favorite": False,
            "is_dead": False,
            "nutrient_claims": ["high protein"],
            "vitamin_c_mg": 0,
            "calcium_mg": 20,
        },
    ]
)


THRESHOLDS = [
    {"nutrient_key": "calories", "low_fail": 550, "low_warn": 650, "high_warn": 850, "high_fail": 950, "unit": "kcal"},
    {"nutrient_key": "sodium_mg", "low_fail": None, "low_warn": None, "high_warn": 1800, "high_fail": 2300, "unit": "mg"},
    {"nutrient_key": "protein_g", "low_fail": 20, "low_warn": 28, "high_warn": None, "high_fail": None, "unit": "g"},
    {"nutrient_key": "fiber_g", "low_fail": 7, "low_warn": 10, "high_warn": None, "high_fail": None, "unit": "g"},
    {"nutrient_key": "fat_g", "low_fail": None, "low_warn": None, "high_warn": 32, "high_fail": 40, "unit": "g"},
]


HISTORICAL_MENUS = [
    {"name": "Monday Breakfast A", "service_date": date(2026, 3, 2), "passes_nutrition": True, "items": [1, 3, 4, 6]},
    {"name": "Monday Lunch A", "service_date": date(2026, 3, 2), "passes_nutrition": True, "items": [7, 10, 9, 11]},
    {"name": "Tuesday Lunch A", "service_date": date(2026, 3, 3), "passes_nutrition": True, "items": [31, 37, 38, 34]},
    {"name": "Tuesday Dinner A", "service_date": date(2026, 3, 3), "passes_nutrition": True, "items": [13, 16, 15, 17]},
    {"name": "Wednesday Lunch A", "service_date": date(2026, 3, 4), "passes_nutrition": False, "items": [21, 10, 12, 30]},
    {"name": "Wednesday Snack A", "service_date": date(2026, 3, 4), "passes_nutrition": True, "items": [25, 23, 4]},
    {"name": "Thursday Breakfast A", "service_date": date(2026, 3, 5), "passes_nutrition": True, "items": [2, 3, 4, 11]},
    {"name": "Thursday Lunch A", "service_date": date(2026, 3, 5), "passes_nutrition": True, "items": [33, 32, 34]},
    {"name": "Friday Dinner A", "service_date": date(2026, 3, 6), "passes_nutrition": True, "items": [18, 37, 28, 17]},
    {"name": "Friday Lunch A", "service_date": date(2026, 3, 6), "passes_nutrition": False, "items": [40, 14, 30, 35]},
    {"name": "Monday Dinner B", "service_date": date(2026, 3, 9), "passes_nutrition": True, "items": [26, 37, 38, 39]},
    {"name": "Tuesday Breakfast B", "service_date": date(2026, 3, 10), "passes_nutrition": True, "items": [1, 6, 4]},
    {"name": "Tuesday Lunch B", "service_date": date(2026, 3, 10), "passes_nutrition": True, "items": [7, 8, 9, 11]},
    {"name": "Wednesday Dinner B", "service_date": date(2026, 3, 11), "passes_nutrition": False, "items": [19, 14, 27, 29]},
    {"name": "Thursday Lunch B", "service_date": date(2026, 3, 12), "passes_nutrition": True, "items": [31, 10, 32, 34]},
    {"name": "Thursday Snack B", "service_date": date(2026, 3, 12), "passes_nutrition": True, "items": [39, 23, 4]},
    {"name": "Friday Breakfast B", "service_date": date(2026, 3, 13), "passes_nutrition": True, "items": [2, 3, 6, 4]},
    {"name": "Friday Lunch B", "service_date": date(2026, 3, 13), "passes_nutrition": True, "items": [33, 12, 17]},
    {"name": "Monday Lunch C", "service_date": date(2026, 3, 16), "passes_nutrition": True, "items": [7, 10, 15, 11]},
    {"name": "Tuesday Dinner C", "service_date": date(2026, 3, 17), "passes_nutrition": True, "items": [36, 37, 28, 25]},
]

LEGACY_SAMPLE_NAMES = [
    "Sample 5-day Lunch Menu- Chinese 1",
    "Sample Breakfast- Cold",
    "Sample 7-day Lunch Menu- Polish 2",
    "Sample 7-day Lunch Menu- Russian 2",
    "Sample 7-day Lunch Menu- Vegetarian 1",
    "Sample 7-day Lunch Menu- Chinese 2",
    "Sample 7-day Lunch Menu- Kosher 1",
    "Sample 7-day Lunch Menu- Halal 2",
    "Sample 7-day Lunch Menu- Latin 1",
    "Sample 7-day Lunch Menu- Standard 1",
    "Sample 7-day Lunch Menu- Korean 1",
    "Sample 7-day Lunch Menu- Caribbean 1",
    "Sample 5-day Lunch Menu- Latin 2, Good For Chilled",
    "Sample 5-day Lunch Menu- Mediterranean 2",
    "Sample 5-day Lunch Menu- Cold",
    "Sample 5-day Lunch Menu- Standard 3",
    "NYC Aging Breakfast Hot Fiscal Year 2027",
    "NYC Aging Lunch Hot Fiscal Year 2027",
    "Gotham Catering Lunch Frozen Kosher Fiscal Year 2027",
    "Gotham Catering Lunch Frozen Vegetarian Fiscal Year 2027",
]

LEGACY_CONTRACTS = [
    "ABSW OAC",
    "Aging Through Arts Center (Encore at St Malachy's)",
    "Agudath Israel Brookdale Senior Center",
    "Agudath Israel Moriah Older Adult Luncheon Club",
    "Albany OAC",
    "Allen AME Community Senior Citizens Centers - Linden Blvd",
    "Allen AME Rockaway Blvd Senior Center",
    "ARC XVI Central Harlem Center",
    "Astoria NSC",
    "QUEENS COMM HOUSE HOME DELIVERED MEALS AT FOREST HILLS - QUEENS 3",
]


for index, menu in enumerate(HISTORICAL_MENUS, start=1):
    if index <= len(LEGACY_SAMPLE_NAMES):
        menu["name"] = LEGACY_SAMPLE_NAMES[index - 1]
    meal_name = menu["name"].lower()
    if "breakfast" in meal_name:
        meal_type = "Breakfast"
    elif "dinner" in meal_name:
        meal_type = "Dinner"
    elif "snack" in meal_name:
        meal_type = "Snack"
    else:
        meal_type = "Lunch"
    menu.update(
        {
            "program_type": "Home Delivered Meal" if "home delivered" in meal_name or "frozen" in meal_name else "Congregate",
            "meal_type": meal_type,
            "menu_coverage": f"{meal_type} only" if meal_type in {"Breakfast", "Lunch", "Dinner"} else "Lunch only",
            "diet_type": "Regular",
            "menu_duration_type": "Medically Tailored Meal - Very Low Sodium" if "very low sodium" in meal_name else "Regular",
            "meal_served_format": "Cold" if "cold" in meal_name else ("Frozen" if "frozen" in meal_name else "Hot"),
            "menu_tags": ["Vegetarian"] if "vegetarian" in meal_name else [],
            "cycle": "Spring/Summer" if index % 2 else "Fiscal Year",
            "days_per_week": 7 if "7-day" in meal_name else 5,
            "contracts": [LEGACY_CONTRACTS[(index - 1) % len(LEGACY_CONTRACTS)]],
            "sample_category": "Sample Menu" if index <= 12 else "Historical Menu",
        }
    )


LEGACY_RECIPE_FIELDS = [
    "ingredients",
    "instructions",
    "serving_size",
    "yield_servings",
    "scale_note",
    "contributed_by",
    "created_on",
    "is_public",
    "is_favorite",
    "is_dead",
    "nutrient_claims",
    "vitamin_c_mg",
    "calcium_mg",
]

SAVED_MENUS = [
    {
        "name": "ABSW OAC July Lunch Cycle - Week 1",
        "contract_name": "ABSW OAC",
        "program_type": "Congregate",
        "meal_type": "Lunch",
        "menu_coverage": "Lunch only",
        "diet_type": "Regular",
        "menu_format": "Weekly",
        "menu_duration_type": "Regular",
        "meal_served_format": "Hot",
        "menu_tags": [],
        "cycle": "Fiscal Year",
        "cycle_start_date": date(2026, 7, 1),
        "cycle_end_date": date(2027, 6, 30),
        "contracts": ["ABSW OAC"],
        "completed_weeks": [1],
        "submitted_programs": ["Congregate"],
        "status": "Submitted To NYC Aging",
        "status_date": date(2026, 7, 9),
        "submitted_to": "NYC Aging Nutrition Unit",
        "submitted_to_nyc_aging_on": date(2026, 7, 9),
        "nutrition_advisor": "NYC Aging Nutrition Unit",
        "created_by": "ABSW OAC",
        "service_date": date(2026, 7, 6),
        "start_date": date(2026, 7, 6),
        "end_date": date(2026, 7, 10),
        "days_per_week": 5,
        "cycle_week": 1,
        "notes": "Provider submitted Week 1 lunch cycle for review.",
        "returned_comments": None,
        "approval_notes": None,
        "is_favorite": True,
        "items": [7, 10, 9, 11, 31, 37, 38, 34, 33, 32, 10, 17, 13, 16, 15, 11, 26, 37, 28, 39],
        "comments": [
            {
                "created_at": datetime(2026, 7, 9, 10, 15),
                "action": "Submitted",
                "author": "ABSW OAC",
                "role": "Provider / Caterer",
                "body": "Submitted Week 1 lunch cycle with hot service format for NYC Aging review.",
                "visibility": "Admin and provider",
                "badge_class": "brand",
                "target_type": "menu",
                "target_label": "General menu summary",
                "review_status": "open",
            }
        ],
    },
    {
        "name": "ABSW OAC July Lunch Cycle - Week 2",
        "contract_name": "ABSW OAC",
        "program_type": "Congregate",
        "meal_type": "Lunch",
        "menu_coverage": "Lunch only",
        "diet_type": "Regular",
        "menu_format": "Weekly",
        "menu_duration_type": "Regular",
        "meal_served_format": "Hot",
        "menu_tags": [],
        "cycle": "Fiscal Year",
        "cycle_start_date": date(2026, 7, 1),
        "cycle_end_date": date(2027, 6, 30),
        "contracts": ["ABSW OAC"],
        "completed_weeks": [1, 2],
        "submitted_programs": ["Congregate"],
        "status": "Returned for correction (from NYC Aging)",
        "status_date": date(2026, 7, 11),
        "submitted_to": "ABSW OAC",
        "submitted_to_nyc_aging_on": date(2026, 7, 8),
        "nutrition_advisor": "Malek, Esther",
        "created_by": "ABSW OAC",
        "service_date": date(2026, 7, 13),
        "start_date": date(2026, 7, 13),
        "end_date": date(2026, 7, 17),
        "days_per_week": 5,
        "cycle_week": 2,
        "notes": "Returned to provider with sodium and component comments.",
        "returned_comments": "Please replace the high-sodium soup on Wednesday and confirm dairy or non-dairy equivalent for Friday.",
        "approval_notes": None,
        "is_favorite": False,
        "items": [21, 10, 12, 30, 7, 8, 9, 11, 40, 14, 32, 34, 31, 10, 20, 4, 33, 37, 15, 17],
        "comments": [
            {
                "created_at": datetime(2026, 7, 11, 9, 30),
                "action": "Returned correction",
                "author": "Malek, Esther",
                "role": "Admin / Department staff",
                "body": "Please replace the high-sodium soup on Wednesday and confirm dairy or non-dairy equivalent for Friday.",
                "visibility": "Admin and provider",
                "badge_class": "warn",
                "target_type": "component",
                "target_label": "Wednesday Lunch - Entrée",
                "day_index": 2,
                "meal_slot": "Lunch",
                "component_key": "entree",
                "review_status": "open",
            },
            {
                "created_at": datetime(2026, 7, 11, 9, 45),
                "action": "Internal note",
                "author": "NYC Aging Nutrition Unit",
                "role": "Admin / Department staff",
                "body": "Review sodium again after provider substitution. Wednesday lunch was the main concern.",
                "visibility": "Internal",
                "badge_class": "brand",
                "target_type": "nutrition",
                "target_label": "Sodium review",
                "nutrient_key": "sodium_mg",
                "review_status": "open",
            },
        ],
    },
    {
        "name": "ABSW OAC July Breakfast Cycle - Week 1",
        "contract_name": "ABSW OAC",
        "program_type": "Congregate",
        "meal_type": "Breakfast",
        "menu_coverage": "Breakfast only",
        "diet_type": "Regular",
        "menu_format": "Weekly",
        "menu_duration_type": "Regular",
        "meal_served_format": "Hot",
        "menu_tags": [],
        "cycle": "Fiscal Year",
        "cycle_start_date": date(2026, 7, 1),
        "cycle_end_date": date(2027, 6, 30),
        "contracts": ["ABSW OAC"],
        "completed_weeks": [1],
        "submitted_programs": ["Congregate"],
        "status": "Approved",
        "status_date": date(2026, 7, 10),
        "submitted_to": "ABSW OAC",
        "submitted_to_nyc_aging_on": date(2026, 7, 7),
        "nutrition_advisor": "NYC Aging Nutrition Unit",
        "created_by": "ABSW OAC",
        "service_date": date(2026, 7, 6),
        "start_date": date(2026, 7, 6),
        "end_date": date(2026, 7, 10),
        "days_per_week": 5,
        "cycle_week": 1,
        "notes": "Approved breakfast cycle.",
        "returned_comments": None,
        "approval_notes": "Approved for Week 1 breakfast service. Keep milk equivalent visible on printed menu.",
        "is_favorite": False,
        "items": [1, 6, 4, 2, 3, 4, 1, 11, 4, 5, 3, 6, 2, 6, 4],
        "comments": [
            {
                "created_at": datetime(2026, 7, 10, 14, 0),
                "action": "Approval note",
                "author": "NYC Aging Nutrition Unit",
                "role": "Admin / Department staff",
                "body": "Approved for Week 1 breakfast service. Keep milk equivalent visible on printed menu.",
                "visibility": "Admin and provider",
                "badge_class": "good",
                "target_type": "menu",
                "target_label": "General menu summary",
                "review_status": "resolved",
            }
        ],
    },
    {
        "name": "Astoria NSC August Lunch Cycle - Week 1",
        "contract_name": "Astoria NSC",
        "program_type": "Congregate",
        "meal_type": "Lunch",
        "menu_coverage": "Lunch only",
        "diet_type": "Regular",
        "menu_format": "Weekly",
        "menu_duration_type": "Regular",
        "meal_served_format": "Fresh Chilled",
        "menu_tags": [],
        "cycle": "Summer",
        "cycle_start_date": date(2026, 8, 1),
        "cycle_end_date": date(2026, 8, 31),
        "contracts": ["Astoria NSC"],
        "completed_weeks": [1],
        "submitted_programs": ["Congregate"],
        "status": "Contract(s) Reviewed Menu",
        "status_date": date(2026, 7, 12),
        "submitted_to": "NYC Aging Nutrition Unit",
        "submitted_to_nyc_aging_on": date(2026, 7, 12),
        "nutrition_advisor": "Regional Nutrition Advisor",
        "created_by": "Astoria NSC",
        "service_date": date(2026, 8, 3),
        "start_date": date(2026, 8, 3),
        "end_date": date(2026, 8, 7),
        "days_per_week": 5,
        "cycle_week": 1,
        "notes": "Contract reviewed and ready for NYC Aging review.",
        "returned_comments": None,
        "approval_notes": None,
        "is_favorite": False,
        "items": [31, 10, 32, 34, 7, 8, 9, 11, 33, 12, 17, 21, 10, 20, 4, 36, 37, 28, 39],
        "comments": [
            {
                "created_at": datetime(2026, 7, 12, 11, 20),
                "action": "Submitted",
                "author": "Astoria NSC",
                "role": "Provider / Caterer",
                "body": "Contract reviewed menu and submitted for NYC Aging review.",
                "visibility": "Admin and provider",
                "badge_class": "brand",
                "target_type": "menu",
                "target_label": "General menu summary",
                "review_status": "open",
            }
        ],
    },
]


def _component_for_recipe(recipe: Recipe | None, position: int) -> str:
    if recipe is None:
        return "entree" if position % 4 == 1 else "vegetable"
    return {
        "grain": "grains",
        "side": "vegetable",
        "milk": "dairy",
        "snack": "alternate",
    }.get(recipe.category, recipe.category)


def _slot_for_menu(menu: dict, component_key: str) -> str:
    meal_type = str(menu["meal_type"]).lower()
    return f"{meal_type}_{component_key}"


def seed_database() -> None:
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        if session.scalar(select(Recipe.recipe_id).limit(1)) is None:
            session.add_all([Recipe(**row) for row in RECIPES])
        else:
            for row in RECIPES:
                recipe = session.get(Recipe, row["recipe_id"])
                if recipe is None:
                    session.add(Recipe(**row))
                    continue
                for field in LEGACY_RECIPE_FIELDS:
                    value = getattr(recipe, field, None)
                    if field in {"is_favorite", "vitamin_c_mg", "calcium_mg"} or value in (None, [], ""):
                        setattr(recipe, field, row[field])
        if session.scalar(select(NutrientThreshold.id).limit(1)) is None:
            session.add_all([NutrientThreshold(**row) for row in THRESHOLDS])
        if session.scalar(select(HistoricalMenu.id).limit(1)) is None:
            for idx, menu in enumerate(HISTORICAL_MENUS, start=1):
                hist = HistoricalMenu(
                    name=menu["name"],
                    service_date=menu["service_date"],
                    program_type=menu["program_type"],
                    meal_type=menu["meal_type"],
                    menu_coverage=menu["menu_coverage"],
                    diet_type=menu["diet_type"],
                    menu_duration_type=menu["menu_duration_type"],
                    meal_served_format=menu["meal_served_format"],
                    menu_tags=menu["menu_tags"],
                    cycle=menu["cycle"],
                    days_per_week=menu["days_per_week"],
                    contracts=menu["contracts"],
                    sample_category=menu["sample_category"],
                    passes_nutrition=menu["passes_nutrition"],
                    notes="Seeded historical menu",
                )
                session.add(hist)
                session.flush()
                for position, recipe_id in enumerate(menu["items"], start=1):
                    recipe = session.get(Recipe, recipe_id)
                    component = recipe.category if recipe is not None else ("main" if position == 1 else "side")
                    session.add(
                        HistoricalMenuItem(
                            historical_menu_id=hist.id,
                            recipe_id=recipe_id,
                            position=position,
                            meal_slot=component,
                        )
                    )
        else:
            for index, row in enumerate(HISTORICAL_MENUS, start=1):
                hist = session.get(HistoricalMenu, index)
                if hist is None:
                    continue
                for field in ["program_type", "meal_type", "menu_coverage", "diet_type", "menu_duration_type", "meal_served_format", "menu_tags", "cycle", "days_per_week", "contracts", "sample_category"]:
                    value = getattr(hist, field, None)
                    if field == "days_per_week" or value in (None, [], ""):
                        setattr(hist, field, row[field])
        if session.scalar(select(Menu.id).limit(1)) is None:
            for menu_row in SAVED_MENUS:
                menu = Menu(
                    name=menu_row["name"],
                    contract_name=menu_row["contract_name"],
                    program_type=menu_row["program_type"],
                    meal_type=menu_row["meal_type"],
                    menu_coverage=menu_row["menu_coverage"],
                    diet_type=menu_row["diet_type"],
                    menu_format=menu_row["menu_format"],
                    menu_duration_type=menu_row["menu_duration_type"],
                    meal_served_format=menu_row["meal_served_format"],
                    menu_tags=menu_row["menu_tags"],
                    cycle=menu_row["cycle"],
                    cycle_start_date=menu_row["cycle_start_date"],
                    cycle_end_date=menu_row["cycle_end_date"],
                    contracts=menu_row["contracts"],
                    completed_weeks=menu_row["completed_weeks"],
                    submitted_programs=menu_row["submitted_programs"],
                    status=menu_row["status"],
                    status_date=menu_row["status_date"],
                    submitted_to=menu_row["submitted_to"],
                    submitted_to_nyc_aging_on=menu_row["submitted_to_nyc_aging_on"],
                    nutrition_advisor=menu_row["nutrition_advisor"],
                    created_by=menu_row["created_by"],
                    service_date=menu_row["service_date"],
                    start_date=menu_row["start_date"],
                    end_date=menu_row["end_date"],
                    days_per_week=menu_row["days_per_week"],
                    cycle_week=menu_row["cycle_week"],
                    notes=menu_row["notes"],
                    returned_comments=menu_row["returned_comments"],
                    approval_notes=menu_row["approval_notes"],
                    is_favorite=menu_row["is_favorite"],
                )
                session.add(menu)
                session.flush()
                for position, recipe_id in enumerate(menu_row["items"], start=1):
                    recipe = session.get(Recipe, recipe_id)
                    component_key = _component_for_recipe(recipe, position)
                    session.add(
                        MenuItem(
                            menu_id=menu.id,
                            recipe_id=recipe_id,
                            position=position,
                            day_index=(position - 1) // 4,
                            meal_slot=_slot_for_menu(menu_row, component_key),
                            component_key=component_key,
                            is_alternate=component_key == "alternate",
                            source_type="seed",
                        )
                    )
                for comment_row in menu_row["comments"]:
                    session.add(
                        MenuComment(
                            menu_id=menu.id,
                            created_at=comment_row["created_at"],
                            action=comment_row["action"],
                            author=comment_row["author"],
                            role=comment_row["role"],
                            body=comment_row["body"],
                            visibility=comment_row["visibility"],
                            badge_class=comment_row["badge_class"],
                            is_user_comment=True,
                            target_type=comment_row.get("target_type", "menu"),
                            target_label=comment_row.get("target_label", "General menu summary"),
                            day_index=comment_row.get("day_index"),
                            meal_slot=comment_row.get("meal_slot"),
                            component_key=comment_row.get("component_key"),
                            recipe_id=comment_row.get("recipe_id"),
                            nutrient_key=comment_row.get("nutrient_key"),
                            review_status=comment_row.get("review_status", "open"),
                        )
                    )
        elif session.scalar(select(MenuComment.id).limit(1)) is None:
            for menu_row in SAVED_MENUS:
                menu = session.scalar(select(Menu).where(Menu.name == menu_row["name"]))
                if menu is None:
                    continue
                for comment_row in menu_row["comments"]:
                    session.add(
                        MenuComment(
                            menu_id=menu.id,
                            created_at=comment_row["created_at"],
                            action=comment_row["action"],
                            author=comment_row["author"],
                            role=comment_row["role"],
                            body=comment_row["body"],
                            visibility=comment_row["visibility"],
                            badge_class=comment_row["badge_class"],
                            is_user_comment=True,
                            target_type=comment_row.get("target_type", "menu"),
                            target_label=comment_row.get("target_label", "General menu summary"),
                            day_index=comment_row.get("day_index"),
                            meal_slot=comment_row.get("meal_slot"),
                            component_key=comment_row.get("component_key"),
                            recipe_id=comment_row.get("recipe_id"),
                            nutrient_key=comment_row.get("nutrient_key"),
                            review_status=comment_row.get("review_status", "open"),
                        )
                    )
        else:
            for menu_row in SAVED_MENUS:
                menu = session.scalar(select(Menu).where(Menu.name == menu_row["name"]))
                if menu is None:
                    continue
                for comment_row in menu_row["comments"]:
                    existing_comment = session.scalar(
                        select(MenuComment).where(
                            MenuComment.menu_id == menu.id,
                            MenuComment.action == comment_row["action"],
                            MenuComment.body == comment_row["body"],
                        )
                    )
                    if existing_comment is None:
                        continue
                    existing_comment.target_type = comment_row.get("target_type", "menu")
                    existing_comment.target_label = comment_row.get("target_label", "General menu summary")
                    existing_comment.day_index = comment_row.get("day_index")
                    existing_comment.meal_slot = comment_row.get("meal_slot")
                    existing_comment.component_key = comment_row.get("component_key")
                    existing_comment.recipe_id = comment_row.get("recipe_id")
                    existing_comment.nutrient_key = comment_row.get("nutrient_key")
                    existing_comment.review_status = comment_row.get("review_status", "open")
        session.commit()
    finally:
        session.close()


if __name__ == "__main__":
    seed_database()
