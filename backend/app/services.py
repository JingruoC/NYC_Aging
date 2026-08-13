from __future__ import annotations

from collections import Counter, defaultdict
from itertools import combinations
from math import sqrt
from typing import Iterable

import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import HistoricalMenu, HistoricalMenuItem, Menu, MenuItem, NutrientThreshold, Recipe, RecommendationLog


NUTRIENT_FIELDS = {
    "calories": "calories",
    "sodium_mg": "sodium_mg",
    "protein_g": "protein_g",
    "fiber_g": "fiber_g",
    "fat_g": "fat_g",
}


def _recipe_dict(recipe: Recipe) -> dict:
    return {
        "recipe_id": recipe.recipe_id,
        "recipe_name": recipe.recipe_name,
        "meal_type": recipe.meal_type,
        "category": recipe.category,
        "calories": recipe.calories,
        "sodium_mg": recipe.sodium_mg,
        "protein_g": recipe.protein_g,
        "fiber_g": recipe.fiber_g,
        "fat_g": recipe.fat_g,
        "tags": recipe.tags or [],
        "is_approved": recipe.is_approved,
        "ingredients": getattr(recipe, "ingredients", None) or [],
        "instructions": getattr(recipe, "instructions", None) or [],
        "serving_size": getattr(recipe, "serving_size", None),
        "yield_servings": getattr(recipe, "yield_servings", None) or 50,
        "scale_note": getattr(recipe, "scale_note", None),
        "contributed_by": getattr(recipe, "contributed_by", None),
        "created_on": getattr(recipe, "created_on", None),
        "is_public": bool(getattr(recipe, "is_public", True)),
        "is_favorite": bool(getattr(recipe, "is_favorite", False)),
        "is_dead": bool(getattr(recipe, "is_dead", False)),
        "nutrient_claims": getattr(recipe, "nutrient_claims", None) or [],
        "vitamin_c_mg": getattr(recipe, "vitamin_c_mg", None) or 0,
        "calcium_mg": getattr(recipe, "calcium_mg", None) or 0,
        "saturated_fat_g": getattr(recipe, "saturated_fat_g", None) or 0,
        "trans_fat_g": getattr(recipe, "trans_fat_g", None) or 0,
        "cholesterol_mg": getattr(recipe, "cholesterol_mg", None) or 0,
        "carbohydrates_g": getattr(recipe, "carbohydrates_g", None) or 0,
        "total_sugars_g": getattr(recipe, "total_sugars_g", None) or 0,
        "added_sugars_g": getattr(recipe, "added_sugars_g", None) or 0,
        "vitamin_d_mcg": getattr(recipe, "vitamin_d_mcg", None) or 0,
        "iron_mg": getattr(recipe, "iron_mg", None) or 0,
        "potassium_mg": getattr(recipe, "potassium_mg", None) or 0,
    }


def load_thresholds(db: Session) -> dict[str, NutrientThreshold]:
    rows = db.scalars(select(NutrientThreshold)).all()
    return {row.nutrient_key: row for row in rows}


def _format_number(value: float) -> str:
    return f"{value:.0f}" if float(value).is_integer() else f"{value:.1f}"


def _normalize_text(value: str) -> str:
    return value.replace("_", " ").lower()


def _processed_meat_keywords() -> tuple[str, ...]:
    return ("bacon", "ham", "sausage", "deli", "hot dog", "salami", "pepperoni", "turkey bacon")


def _is_processed_meat(recipe: Recipe) -> bool:
    haystack = " ".join(
        [
            recipe.recipe_name,
            recipe.category,
            " ".join(recipe.tags or []),
            " ".join(getattr(recipe, "ingredients", None) or []),
            " ".join(getattr(recipe, "nutrient_claims", None) or []),
        ]
    ).lower()
    return any(keyword in haystack for keyword in _processed_meat_keywords())


def _is_whole_grain(recipe: Recipe) -> bool:
    haystack = " ".join([recipe.recipe_name, recipe.category, " ".join(recipe.tags or []), " ".join(getattr(recipe, "nutrient_claims", None) or [])]).lower()
    return recipe.category == "grain" and ("whole grain" in haystack or "whole wheat" in haystack or "brown rice" in haystack or "barley" in haystack or "oat" in haystack)


def _is_plant_based_protein(recipe: Recipe) -> bool:
    haystack = " ".join(
        [
            recipe.recipe_name,
            recipe.category,
            " ".join(recipe.tags or []),
            " ".join(getattr(recipe, "ingredients", None) or []),
            " ".join(getattr(recipe, "nutrient_claims", None) or []),
        ]
    ).lower()
    return "vegetarian" in haystack or "plant-based" in haystack or any(keyword in haystack for keyword in ("lentil", "tofu", "bean", "chickpea", "edamame", "pea"))


def _is_dairy(recipe: Recipe) -> bool:
    haystack = " ".join([recipe.recipe_name, recipe.category, " ".join(recipe.tags or [])]).lower()
    return recipe.category == "milk" or any(keyword in haystack for keyword in ("milk", "yogurt", "cheese", "cottage"))


def _is_fruit_or_vegetable(recipe: Recipe) -> bool:
    return recipe.category in {"fruit", "vegetable"}


def _is_non_starchy_vegetable(recipe: Recipe) -> bool:
    return recipe.category == "vegetable"


def _meal_label(meal_slot: str) -> str:
    return meal_slot.title()


def _menu_item_records(recipe_rows: list[Recipe], menu_items: list[dict] | None = None) -> dict[str, list[Recipe]]:
    grouped: dict[str, list[Recipe]] = {"breakfast": [], "lunch": [], "dinner": []}
    if menu_items:
        lookup = {recipe.recipe_id: recipe for recipe in recipe_rows}
        for item in menu_items:
            recipe_id = item.get("recipe_id") if isinstance(item, dict) else getattr(item, "recipe_id", None)
            meal_slot = (item.get("meal_slot") if isinstance(item, dict) else getattr(item, "meal_slot", None)) or ""
            recipe = lookup.get(recipe_id)
            if recipe is None:
                continue
            slot = meal_slot.lower().split("_", 1)[0]
            if slot in grouped:
                grouped[slot].append(recipe)
        return grouped

    for recipe in recipe_rows:
        meal_type = recipe.meal_type.lower()
        if meal_type in grouped:
            grouped[meal_type].append(recipe)
    return grouped


def _make_requirement(
    rule_key: str,
    title: str,
    status: str,
    message: str,
    component_badges: list[str] | None = None,
    missing_component_badges: list[str] | None = None,
    details: list[str] | None = None,
    suggestions: list[dict] | None = None,
) -> dict:
    return {
        "rule_key": rule_key,
        "title": title,
        "status": status,
        "message": message,
        "component_badges": component_badges or [],
        "missing_component_badges": missing_component_badges or [],
        "details": details or [],
        "suggestions": suggestions or [],
    }


def _suggest_recipes(
    recipes: list[Recipe],
    *,
    meal_slots: set[str] | None = None,
    categories: set[str] | None = None,
    limit: int = 3,
    exclude_ids: set[int] | None = None,
    prefer_tags: tuple[str, ...] = (),
    requires_whole_grain: bool = False,
    requires_plant_based: bool = False,
    requires_dairy: bool = False,
    requires_fruit_or_veg: bool = False,
) -> list[dict]:
    exclude_ids = exclude_ids or set()
    scored: list[tuple[float, Recipe, list[str]]] = []
    for recipe in recipes:
        if recipe.recipe_id in exclude_ids:
            continue

        if meal_slots and recipe.meal_type.lower() not in meal_slots and recipe.meal_type.lower() != "snack":
            continue
        if categories and recipe.category not in categories:
            continue
        if requires_whole_grain and not _is_whole_grain(recipe):
            continue
        if requires_plant_based and not _is_plant_based_protein(recipe):
            continue
        if requires_dairy and not _is_dairy(recipe):
            continue
        if requires_fruit_or_veg and not _is_fruit_or_vegetable(recipe):
            continue

        score = 0.0
        reasons: list[str] = []
        if recipe.is_approved:
            score += 2.0
            reasons.append("Approved recipe")
        if recipe.tags:
            joined_tags = " ".join(recipe.tags).lower()
            for tag in prefer_tags:
                if tag in joined_tags:
                    score += 1.5
                    reasons.append(f"Matches {tag} guidance")
        if getattr(recipe, "nutrient_claims", None):
            joined_claims = " ".join(recipe.nutrient_claims).lower()
            for tag in prefer_tags:
                if tag in joined_claims:
                    score += 1.5
                    reasons.append(f"Matches {tag} nutrition claim")
        if requires_whole_grain and _is_whole_grain(recipe):
            score += 2.0
        if requires_plant_based and _is_plant_based_protein(recipe):
            score += 2.0
        if requires_dairy and _is_dairy(recipe):
            score += 2.0
        if requires_fruit_or_veg and _is_fruit_or_vegetable(recipe):
            score += 1.5
        if recipe.category in {"fruit", "vegetable"}:
            score += 0.5
        if recipe.category == "grain" and _is_whole_grain(recipe):
            score += 1.0
        if recipe.meal_type in {"breakfast", "lunch", "dinner"}:
            score += 0.5
        if not reasons:
            reasons.append("Fits the menu pattern")
        scored.append((score, recipe, reasons))

    scored.sort(key=lambda item: (-item[0], item[1].recipe_name))
    return [
        {
            "recipe": _recipe_dict(recipe),
            "score": round(score, 2),
            "reasons": reasons,
        }
        for score, recipe, reasons in scored[:limit]
    ]


def get_recipes(db: Session, only_approved: bool = False) -> list[dict]:
    stmt = select(Recipe).order_by(Recipe.recipe_name.asc())
    if only_approved:
        stmt = stmt.where(Recipe.is_approved.is_(True))
    return [_recipe_dict(recipe) for recipe in db.scalars(stmt).all()]


def search_recipes(db: Session, query: str) -> list[dict]:
    q = (query or "").strip().lower()
    if not q:
        return get_recipes(db, only_approved=False)

    recipes = db.scalars(select(Recipe).where(Recipe.is_approved.is_(True))).all()
    scored: list[tuple[float, Recipe]] = []
    for recipe in recipes:
        haystack = " ".join(
            [
                recipe.recipe_name,
                recipe.category,
                recipe.meal_type,
                " ".join(recipe.tags or []),
                " ".join(getattr(recipe, "ingredients", None) or []),
                " ".join(getattr(recipe, "instructions", None) or []),
                " ".join(getattr(recipe, "nutrient_claims", None) or []),
            ]
        ).lower()
        if q in haystack:
            score = 3.0 + haystack.count(q)
            scored.append((score, recipe))
        else:
            tokens = q.split()
            if all(token in haystack for token in tokens):
                score = 2.0 + sum(haystack.count(token) for token in tokens) / 10
                scored.append((score, recipe))
    scored.sort(key=lambda item: (-item[0], item[1].recipe_name))
    return [_recipe_dict(recipe) for _, recipe in scored[:20]]


def selected_recipes(db: Session, recipe_ids: list[int]) -> list[Recipe]:
    if not recipe_ids:
        return []
    rows = db.scalars(select(Recipe).where(Recipe.recipe_id.in_(recipe_ids))).all()
    by_id = {row.recipe_id: row for row in rows}
    return [by_id[rid] for rid in recipe_ids if rid in by_id]


def analyze_menu(
    db: Session,
    recipe_ids: list[int],
    thresholds: dict[str, NutrientThreshold] | None = None,
    menu_items: list[dict] | None = None,
) -> dict:
    all_recipe_rows = db.scalars(select(Recipe).where(Recipe.recipe_id.in_(set(recipe_ids)))).all()
    recipe_map = {recipe.recipe_id: recipe for recipe in all_recipe_rows}
    chosen = [recipe_map[recipe_id] for recipe_id in recipe_ids if recipe_id in recipe_map]
    grouped = _menu_item_records(chosen, menu_items)
    selected_ids = {recipe.recipe_id for recipe in chosen}

    planned_days: set[int] = set()
    meal_days: dict[str, set[int]] = {"breakfast": set(), "lunch": set(), "dinner": set()}
    for item in menu_items or []:
        day_index = item.get("day_index") if isinstance(item, dict) else getattr(item, "day_index", None)
        meal_slot = (item.get("meal_slot") if isinstance(item, dict) else getattr(item, "meal_slot", None)) or ""
        meal_key = meal_slot.lower().split("_", 1)[0]
        if day_index is None:
            continue
        planned_days.add(day_index)
        if meal_key in meal_days:
            meal_days[meal_key].add(day_index)

    service_day_count = max(len(planned_days), 1)
    planned_meal_count = max(sum(len(days) for days in meal_days.values()), 1)

    totals = {
        "calories": round(sum(r.calories for r in chosen) / planned_meal_count, 1),
        "sodium_mg": round(sum(r.sodium_mg for r in chosen) / planned_meal_count, 1),
        "protein_g": round(sum(r.protein_g for r in chosen) / planned_meal_count, 1),
        "fiber_g": round(sum(r.fiber_g for r in chosen) / planned_meal_count, 1),
        "fat_g": round(sum(r.fat_g for r in chosen) / planned_meal_count, 1),
    }
    threshold_map = thresholds or load_thresholds(db)
    statuses = []
    meal_requirements = []
    overall = "pass"

    def update_overall(status: str) -> None:
        nonlocal overall
        if status == "fail":
            overall = "fail"
        elif status == "warning" and overall == "pass":
            overall = "warning"

    for key, total in totals.items():
        threshold = threshold_map.get(key)
        if threshold is None:
            continue
        status = "pass"
        label = key.replace("_", " ").title()
        message = f"{label} is within target."
        if threshold.low_fail is not None and total < threshold.low_fail:
            status = "fail"
            diff = threshold.low_fail - total
            message = f"{label} is {_format_number(diff)} {threshold.unit} below the minimum target of {_format_number(threshold.low_fail)} {threshold.unit}."
        elif threshold.low_warn is not None and total < threshold.low_warn:
            status = "warning"
            diff = threshold.low_warn - total
            message = f"{label} is {_format_number(diff)} {threshold.unit} below the warning threshold of {_format_number(threshold.low_warn)} {threshold.unit}."
        if threshold.high_fail is not None and total > threshold.high_fail:
            status = "fail"
            diff = total - threshold.high_fail
            message = f"{label} is {_format_number(diff)} {threshold.unit} above the maximum target of {_format_number(threshold.high_fail)} {threshold.unit}."
        elif threshold.high_warn is not None and total > threshold.high_warn and status != "fail":
            status = "warning"
            diff = total - threshold.high_warn
            message = f"{label} is {_format_number(diff)} {threshold.unit} above the warning threshold of {_format_number(threshold.high_warn)} {threshold.unit}."

        update_overall(status)
        statuses.append(
            {
                "nutrient_key": key,
                "total": total,
                "unit": threshold.unit,
                "status": status,
                "message": message,
            }
        )

    all_approved = db.scalars(select(Recipe).where(Recipe.is_approved.is_(True))).all()
    approved_map = {recipe.recipe_id: recipe for recipe in all_approved}
    selected_approved = [approved_map[rid] for rid in selected_ids if rid in approved_map]
    total_days = service_day_count

    def collect_component_suggestions(
        meal_slot: str,
        categories: set[str],
        *,
        whole_grain: bool = False,
        plant_based: bool = False,
        dairy: bool = False,
        fruit_or_veg: bool = False,
        title: str = "",
    ) -> list[dict]:
        candidates = _suggest_recipes(
            all_approved,
            meal_slots={meal_slot},
            categories=categories,
            limit=3,
            exclude_ids=selected_ids,
            requires_whole_grain=whole_grain,
            requires_plant_based=plant_based,
            requires_dairy=dairy,
            requires_fruit_or_veg=fruit_or_veg,
        )
        for candidate in candidates:
            candidate["reasons"] = [title] + candidate["reasons"] if title else candidate["reasons"]
        return candidates

    def make_meal_requirement(
        rule_key: str,
        title: str,
        meal_slot: str,
        required_categories: set[str],
        *,
        component_badges: list[str] | None = None,
        must_have_dairy: bool = False,
        must_have_fruit_or_veg: bool = False,
        must_have_whole_grain: bool = False,
        must_have_plant_based: bool = False,
        include_processed_meat_check: bool = False,
    ) -> dict:
        items = grouped.get(meal_slot, [])
        details: list[str] = []
        suggestions: list[dict] = []
        missing_badges: list[str] = []
        status = "pass"
        meal_count = len(meal_days[meal_slot]) if menu_items else min(len(items), total_days)
        if meal_count < total_days:
            status = "warning"
            details.append(f"{_meal_label(meal_slot)} coverage is {meal_count} of {total_days} planned days.")
        else:
            details.append(f"{_meal_label(meal_slot)} coverage is complete for the current cycle.")

        has_required = any(recipe.category in required_categories for recipe in items)
        if required_categories and not has_required:
            status = "fail"
            details.append(f"Missing a {', '.join(sorted(required_categories))} option in {_meal_label(meal_slot).lower()}.")
            suggestions.extend(collect_component_suggestions(meal_slot, required_categories, title=f"Add a {', '.join(sorted(required_categories))} option"))
            missing_badges.extend(["entrée" if "entree" in required_categories else c for c in sorted(required_categories)])

        if must_have_dairy:
            has_dairy = any(_is_dairy(recipe) for recipe in items)
            if not has_dairy:
                status = "fail" if status != "warning" else status
                details.append(f"No dairy or non-dairy equivalent is present in {_meal_label(meal_slot).lower()}.")
                suggestions.extend(collect_component_suggestions(meal_slot, {"milk"}, dairy=True, title="Add a dairy or milk option"))
                missing_badges.append("dairy")

        if must_have_fruit_or_veg:
            has_fruit_veg = any(_is_fruit_or_vegetable(recipe) for recipe in items)
            if not has_fruit_veg:
                status = "fail" if status != "warning" else status
                details.append(f"No fruit or vegetable option is present in {_meal_label(meal_slot).lower()}.")
                suggestions.extend(collect_component_suggestions(meal_slot, {"fruit", "vegetable"}, fruit_or_veg=True, title="Add a fruit or vegetable option"))
                missing_badges.append("fruit/veg")

        if must_have_whole_grain:
            grain_items = [recipe for recipe in items if recipe.category == "grain"]
            whole_grain_count = sum(1 for recipe in grain_items if _is_whole_grain(recipe))
            if grain_items and whole_grain_count < max(1, (len(grain_items) + 1) // 2):
                status = "warning" if status == "pass" else status
                details.append(f"Only {whole_grain_count} of {len(grain_items)} grain items are whole grain.")
                suggestions.extend(collect_component_suggestions(meal_slot, {"grain"}, whole_grain=True, title="Use more whole grain recipes"))
                missing_badges.append("whole grain")

        if must_have_plant_based:
            plant_based_count = sum(1 for recipe in items if _is_plant_based_protein(recipe))
            if plant_based_count < 2:
                status = "warning" if status == "pass" else status
                details.append(f"Only {plant_based_count} plant-based protein servings are planned; target is at least 2 per week.")
                suggestions.extend(collect_component_suggestions(meal_slot, {"entree", "side", "grain"}, plant_based=True, title="Add a plant-based protein"))
                missing_badges.append("plant protein")

        if include_processed_meat_check:
            processed_items = [recipe for recipe in items if _is_processed_meat(recipe)]
            if processed_items:
                status = "fail"
                details.append(f"Processed meat is not allowed: {', '.join(recipe.recipe_name for recipe in processed_items)}.")
                missing_badges.append("processed meat")
                suggestions.extend(_suggest_recipes(
                    all_approved,
                    meal_slots={meal_slot},
                    categories={"entree", "grain", "vegetable", "fruit", "milk", "side"},
                    limit=3,
                    exclude_ids=selected_ids,
                    prefer_tags=("low sodium", "whole grain", "vegetarian"),
                ))

        if status == "pass" and not details:
            details.append(f"{_meal_label(meal_slot)} requirements are covered.")

        if suggestions:
            seen = set()
            deduped = []
            for item in suggestions:
                recipe_id = item["recipe"]["recipe_id"]
                if recipe_id in seen:
                    continue
                seen.add(recipe_id)
                deduped.append(item)
            suggestions = deduped[:3]

        update_overall(status)
        if missing_badges:
            seen_badges = set()
            ordered_missing = []
            for badge in missing_badges:
                if badge in seen_badges:
                    continue
                seen_badges.add(badge)
                ordered_missing.append(badge)
        else:
            ordered_missing = []

        return _make_requirement(
            rule_key,
            title,
            status,
            details[0] if details else f"{title} is covered.",
            component_badges,
            ordered_missing,
            details,
            suggestions,
        )

    if grouped["breakfast"]:
        meal_requirements.append(make_meal_requirement(
            "breakfast",
            "Breakfast balance",
            "breakfast",
            {"entree", "grain"},
            component_badges=["entrée", "fruit/veg", "dairy", "whole grain"],
            must_have_dairy=True,
            must_have_fruit_or_veg=True,
            must_have_whole_grain=True,
            include_processed_meat_check=True,
        ))
    if grouped["lunch"]:
        meal_requirements.append(make_meal_requirement(
            "lunch",
            "Lunch balance",
            "lunch",
            {"entree"},
            component_badges=["entrée", "fruit", "vegetable", "dairy", "whole grain", "plant protein"],
            must_have_dairy=True,
            must_have_fruit_or_veg=True,
            must_have_whole_grain=True,
            must_have_plant_based=True,
            include_processed_meat_check=True,
        ))
    if grouped["dinner"]:
        meal_requirements.append(make_meal_requirement(
            "dinner",
            "Dinner balance",
            "dinner",
            {"entree"},
            component_badges=["entrée", "fruit", "vegetable", "dairy", "whole grain", "plant protein"],
            must_have_dairy=True,
            must_have_fruit_or_veg=True,
            must_have_whole_grain=True,
            must_have_plant_based=True,
            include_processed_meat_check=True,
        ))

    grain_items = [recipe for recipe in selected_approved if recipe.category == "grain"]
    whole_grain_count = sum(1 for recipe in grain_items if _is_whole_grain(recipe))
    if grain_items:
        whole_grain_status = "pass"
        whole_grain_details = [f"{whole_grain_count} of {len(grain_items)} grain recipes are whole grain."]
        if whole_grain_count < max(1, (len(grain_items) + 1) // 2):
            whole_grain_status = "warning"
            whole_grain_details.append("At least half of all grains should be whole grain.")
        else:
            whole_grain_details.append("Whole grain balance is on target.")
        update_overall(whole_grain_status)
        meal_requirements.append(_make_requirement(
            "whole_grain_balance",
            "Whole grain balance",
            whole_grain_status,
            whole_grain_details[0],
            ["whole grain"],
            [],
            whole_grain_details,
            _suggest_recipes(
                all_approved,
                meal_slots={"breakfast", "lunch", "dinner"},
                categories={"grain"},
                limit=3,
                exclude_ids=selected_ids,
                requires_whole_grain=True,
                prefer_tags=("whole grain", "whole wheat", "barley", "brown rice"),
            ),
        ))

    processed_items = [recipe for recipe in selected_approved if _is_processed_meat(recipe)]
    processed_status = "pass" if not processed_items else "fail"
    processed_details = ["No processed meat items are present."]
    if processed_items:
        processed_details = [f"Processed meat is not allowed: {', '.join(recipe.recipe_name for recipe in processed_items)}."]
    update_overall(processed_status)
    meal_requirements.append(_make_requirement(
        "processed_meat",
        "Processed meat check",
        processed_status,
        processed_details[0],
        ["processed meat"],
        [],
        processed_details,
        _suggest_recipes(
            all_approved,
            meal_slots={"breakfast", "lunch", "dinner"},
            categories={"entree", "grain", "vegetable", "fruit", "milk", "side"},
            limit=3,
            exclude_ids=selected_ids,
            prefer_tags=("vegetarian", "low sodium", "whole grain"),
        ) if processed_items else [],
    ))

    return {
        "totals": totals,
        "statuses": statuses,
        "meal_requirements": meal_requirements,
        "overall_status": overall,
        "selected_recipes": [_recipe_dict(recipe) for recipe in chosen],
    }


def _historical_menu_recipe_sets(db: Session) -> list[tuple[HistoricalMenu, set[int], list[str]]]:
    menus = db.scalars(select(HistoricalMenu)).all()
    results = []
    for menu in menus:
        item_rows = db.scalars(
            select(HistoricalMenuItem.recipe_id).where(HistoricalMenuItem.historical_menu_id == menu.id)
        ).all()
        results.append((menu, set(item_rows), []))
    return results


def _historical_category_sets(db: Session) -> dict[int, set[str]]:
    recipe_rows = db.scalars(select(Recipe)).all()
    return {recipe.recipe_id: set((recipe.category, recipe.meal_type) + tuple(recipe.tags or [])) for recipe in recipe_rows}


def autocomplete_recommendations(db: Session, selected_ids: list[int], limit: int = 8) -> list[dict]:
    selected = selected_recipes(db, selected_ids)
    if not selected:
        approved = selected_recipes(db, [r.recipe_id for r in db.scalars(select(Recipe).where(Recipe.is_approved.is_(True))).all()])
        return [_recipe_dict(recipe) | {"score": 1.0, "reasons": ["Approved recipe"]} for recipe in approved[:limit]]

    selected_set = set(selected_ids)
    hist = _historical_menu_recipe_sets(db)
    all_recipes = db.scalars(select(Recipe).where(Recipe.is_approved.is_(True))).all()
    recipe_map = {recipe.recipe_id: recipe for recipe in all_recipes}

    co_occurrence = Counter()
    selected_support = Counter()
    for _, recipe_set, _ in hist:
        if selected_set.issubset(recipe_set):
            for rid in recipe_set - selected_set:
                co_occurrence[rid] += 2
        if recipe_set & selected_set:
            for rid in recipe_set:
                selected_support[rid] += 1

    selected_categories = Counter(recipe.category for recipe in selected)
    selected_meal_types = Counter(recipe.meal_type for recipe in selected)
    complementary_categories = {
        "entree": {"grain", "vegetable", "fruit", "milk", "side"},
        "grain": {"entree", "vegetable"},
        "vegetable": {"entree", "grain", "fruit"},
        "fruit": {"entree", "grain", "milk"},
        "milk": {"fruit", "grain", "entree"},
        "side": {"entree", "grain", "vegetable"},
    }

    scored: list[tuple[float, Recipe, list[str]]] = []
    for recipe in all_recipes:
        if recipe.recipe_id in selected_set:
            continue
        score = 0.0
        reasons = []
        if co_occurrence[recipe.recipe_id]:
            score += min(co_occurrence[recipe.recipe_id], 6)
            reasons.append("Frequently paired in historical menus")
        if selected_support[recipe.recipe_id]:
            score += 0.5
            reasons.append("Appears in similar menus")
        if recipe.meal_type in selected_meal_types:
            score += 1.0
            reasons.append(f"Matches selected {recipe.meal_type} items")
        if any(recipe.category in complementary_categories.get(cat, set()) for cat in selected_categories):
            score += 1.5
            reasons.append("Complements the current meal mix")
        if "low sodium" in " ".join(recipe.tags or []).lower():
            score += 0.4
        if recipe.category in {"vegetable", "fruit"}:
            score += 0.8
        scored.append((score, recipe, reasons))

    scored.sort(key=lambda item: (-item[0], item[1].recipe_name))
    output = []
    for score, recipe, reasons in scored[:limit]:
        if score <= 0:
            continue
        output.append({"recipe": _recipe_dict(recipe), "score": round(score, 2), "reasons": reasons or ["Approved recipe"]})
    return output


def revision_recommendations(db: Session, selected_ids: list[int], limit: int = 8) -> dict:
    analysis = analyze_menu(db, selected_ids)
    selected = selected_recipes(db, selected_ids)
    selected_categories = {recipe.category for recipe in selected}
    selected_meal_types = {recipe.meal_type for recipe in selected}
    approved = db.scalars(select(Recipe).where(Recipe.is_approved.is_(True))).all()

    suggestions: dict[str, list[dict]] = {"sodium": [], "protein": [], "fiber": []}

    sodium_status = next(item for item in analysis["statuses"] if item["nutrient_key"] == "sodium_mg")
    protein_status = next(item for item in analysis["statuses"] if item["nutrient_key"] == "protein_g")
    fiber_status = next(item for item in analysis["statuses"] if item["nutrient_key"] == "fiber_g")

    if sodium_status["status"] in {"warning", "fail"}:
        candidates = [r for r in approved if r.category in selected_categories and r.recipe_id not in selected_ids]
        candidates.sort(key=lambda r: (r.sodium_mg, -r.protein_g, -r.fiber_g))
        suggestions["sodium"] = [
            {
                "recipe": _recipe_dict(recipe),
                "score": round(max(0.1, 10 - recipe.sodium_mg / 150), 2),
                "reasons": ["Lower-sodium option in the same category"],
            }
            for recipe in candidates[:limit]
        ]

    if protein_status["status"] in {"warning", "fail"}:
        candidates = [r for r in approved if r.recipe_id not in selected_ids]
        candidates.sort(key=lambda r: (-r.protein_g, r.sodium_mg))
        suggestions["protein"] = [
            {
                "recipe": _recipe_dict(recipe),
                "score": round(recipe.protein_g / 2, 2),
                "reasons": ["Higher-protein approved recipe"],
            }
            for recipe in candidates[:limit]
        ]

    if fiber_status["status"] in {"warning", "fail"}:
        candidates = [r for r in approved if r.category in {"grain", "vegetable", "fruit"} and r.recipe_id not in selected_ids]
        candidates.sort(key=lambda r: (-r.fiber_g, r.sodium_mg))
        suggestions["fiber"] = [
            {
                "recipe": _recipe_dict(recipe),
                "score": round(recipe.fiber_g / 2, 2),
                "reasons": ["Higher-fiber grain, vegetable, or fruit"],
            }
            for recipe in candidates[:limit]
        ]

    for key in suggestions:
        suggestions[key] = suggestions[key][:limit]

    return {"analysis": analysis, "suggestions": suggestions}


def similar_menus(db: Session, selected_ids: list[int], limit: int = 5) -> list[dict]:
    selected = set(selected_ids)
    if not selected:
        return []

    selected_recipes_rows = selected_recipes(db, selected_ids)
    selected_categories = Counter(recipe.category for recipe in selected_recipes_rows)

    historical_menus = db.scalars(select(HistoricalMenu)).all()
    results = []
    for menu in historical_menus:
        recipe_ids = set(
            db.scalars(
                select(HistoricalMenuItem.recipe_id).where(HistoricalMenuItem.historical_menu_id == menu.id)
            ).all()
        )
        if not recipe_ids:
            continue
        jaccard = len(selected & recipe_ids) / len(selected | recipe_ids)
        if jaccard == 0:
            continue
        menu_recipe_rows = db.scalars(select(Recipe).where(Recipe.recipe_id.in_(recipe_ids))).all()
        menu_categories = Counter(recipe.category for recipe in menu_recipe_rows)
        cat_overlap = sum(min(selected_categories[c], menu_categories[c]) for c in selected_categories)
        score = round(jaccard * 0.7 + min(cat_overlap / max(len(selected), 1), 1.0) * 0.3, 4)
        results.append(
            {
                "id": menu.id,
                "name": menu.name,
                "service_date": menu.service_date,
                "passes_nutrition": menu.passes_nutrition,
                "similarity": score,
                "recipe_ids": sorted(recipe_ids),
                "notes": menu.notes,
            }
        )

    results.sort(key=lambda item: (-item["similarity"], not item["passes_nutrition"], item["name"]))
    passed = [item for item in results if item["passes_nutrition"]]
    failed = [item for item in results if not item["passes_nutrition"]]
    return (passed + failed)[:limit]


def analytics_summary(db: Session) -> dict:
    recipes = db.scalars(select(Recipe)).all()
    historical_menus = db.scalars(select(HistoricalMenu)).all()
    historical_items = db.scalars(select(HistoricalMenuItem)).all()
    item_rows = db.scalars(select(HistoricalMenuItem.recipe_id)).all()
    recipe_ids = [row for row in item_rows]

    recipe_lookup = {r.recipe_id: r for r in recipes}
    usage_counts = Counter(recipe_ids)
    top_recipes = [
        {
            "recipe_id": rid,
            "recipe_name": recipe_lookup[rid].recipe_name,
            "count": count,
            "category": recipe_lookup[rid].category,
        }
        for rid, count in usage_counts.most_common(10)
        if rid in recipe_lookup
    ]

    pair_counts = Counter()
    for menu in historical_menus:
        rids = [item.recipe_id for item in historical_items if item.historical_menu_id == menu.id]
        for left, right in combinations(sorted(set(rids)), 2):
            pair_counts[(left, right)] += 1
    top_pairings = [
        {
            "recipe_a": recipe_lookup[a].recipe_name,
            "recipe_b": recipe_lookup[b].recipe_name,
            "count": count,
        }
        for (a, b), count in pair_counts.most_common(10)
        if a in recipe_lookup and b in recipe_lookup
    ]

    category_counts = (
        pd.DataFrame([{"category": r.category} for r in recipes])
        .value_counts()
        .reset_index(name="count")
        .to_dict(orient="records")
    )
    meal_type_counts = (
        pd.DataFrame([{"meal_type": r.meal_type} for r in recipes])
        .value_counts()
        .reset_index(name="count")
        .to_dict(orient="records")
    )

    return {
        "top_recipes": top_recipes,
        "top_pairings": top_pairings,
        "category_counts": category_counts,
        "meal_type_counts": meal_type_counts,
    }


def log_recommendation(db: Session, endpoint: str, selected_recipe_ids: list[int], result_count: int, metadata: dict | None = None):
    db.add(
        RecommendationLog(
            endpoint=endpoint,
            selected_recipe_ids=selected_recipe_ids,
            result_count=result_count,
            details=metadata or {},
        )
    )
