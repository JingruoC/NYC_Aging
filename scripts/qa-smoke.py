#!/usr/bin/env python3
"""Repeatable API smoke checks for the running Simple Servings prototype."""

from __future__ import annotations

import json
import os
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


BASE_URL = os.environ.get("SIMPLE_SERVINGS_API", "http://127.0.0.1:8000").rstrip("/")


def request(path: str, payload: dict | None = None):
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    req = Request(
        f"{BASE_URL}{path}",
        data=body,
        headers={"Content-Type": "application/json"} if body else {},
        method="POST" if body else "GET",
    )
    with urlopen(req, timeout=20) as response:
        content_type = response.headers.get_content_type()
        content = response.read()
        parsed = json.loads(content) if content_type == "application/json" else content
        return response.status, content_type, parsed


def download(path: str):
    req = Request(f"{BASE_URL}{path}", method="GET")
    with urlopen(req, timeout=20) as response:
        return response.status, response.headers, response.read()


def check(condition: bool, label: str) -> None:
    if not condition:
        raise AssertionError(label)
    print(f"PASS  {label}")


def main() -> int:
    status, _, health = request("/health")
    check(status == 200 and health.get("status") == "ok", "backend health")

    _, _, recipes = request("/recipes")
    approved = [recipe for recipe in recipes if recipe["is_approved"]]
    check(len(recipes) >= 40 and len(approved) >= 30, "recipe catalog is seeded")
    check(
        any(any(str(line).lstrip()[:1].isdigit() for line in recipe.get("ingredients", [])) for recipe in approved),
        "seed recipes contain scalable quantities",
    )

    _, _, menus = request("/menus")
    reviewable = [menu for menu in menus if menu["status"] != "Draft"]
    check(len(reviewable) >= 4, "reviewable saved menus are seeded")
    check(all(menu["item_count"] >= 30 for menu in reviewable), "reviewable mock menus contain complete weekly records")

    _, _, sample_menus = request("/sample-menus")
    check(len(sample_menus) >= 20, "sample menu catalog is seeded")
    _, _, sample = request(f"/sample-menus/{sample_menus[0]['id']}")
    sample_days = {item["day_index"] for item in sample.get("items", [])}
    check(len(sample_days) == sample["days_per_week"], "sample menu spans every service day")

    _, _, updates = request("/home-updates")
    check(any(update.get("image_source") for update in updates), "home updates support pictures")
    check(any("\n\n" in update.get("content", "") for update in updates), "home updates support long-form content")

    _, _, categories = request("/recipe-home-categories")
    check(len(categories) >= 6 and all("is_visible" in category for category in categories), "recipe home categories are configurable")

    _, _, resources = request("/resources")
    check(
        isinstance(resources, list) and all(resource.get("last_updated") for resource in resources),
        "uploaded resource records include updated dates",
    )

    _, _, analysis = request("/menus/analyze", {"recipe_ids": [7, 10, 9, 11]})
    check("totals" in analysis and "statuses" in analysis, "nutrition analysis")

    _, _, autocomplete = request(
        "/recommendations/autocomplete",
        {"selected_recipe_ids": [7], "meal_type": "lunch", "limit": 5},
    )
    check(len(autocomplete) > 0, "rule-based autocomplete recommendations")
    _, _, revisions = request("/recommendations/revisions", {"selected_recipe_ids": [21, 10, 12, 30]})
    check(isinstance(revisions, dict), "rule-based revision recommendations")
    _, _, similar = request(
        "/recommendations/similar-menus",
        {"selected_recipe_ids": [7, 10, 9, 11], "limit": 5},
    )
    check(len(similar) > 0, "historical menu similarity")

    _, _, attachments = request("/recipes/43/attachments")
    check(any(item["file_kind"] == "product_label" for item in attachments), "recipe review attachment metadata")
    attachment = next(item for item in attachments if item["file_kind"] == "product_label")
    status, headers, content = download(f"/recipes/43/attachments/{attachment['id']}?download=false")
    check(
        status == 200
        and headers.get_content_type() == "application/pdf"
        and headers.get("Content-Disposition", "").startswith("inline")
        and len(content) > 100,
        "recipe review attachment opens inline",
    )
    status, headers, content = download(f"/recipes/43/attachments/{attachment['id']}?download=true")
    check(
        status == 200
        and headers.get("Content-Disposition", "").startswith("attachment")
        and len(content) > 100,
        "recipe review attachment downloads",
    )
    status, content_type, workbook = request("/recipes/43/export/submission.xlsx")
    check(status == 200 and "spreadsheetml" in content_type and len(workbook) > 1000, "recipe submission Excel export")
    status, content_type, workbook = request("/recipes/43/export/nutrition.xlsx")
    check(status == 200 and "spreadsheetml" in content_type and len(workbook) > 1000, "nutrition analysis Excel export")

    _, _, menu_comments = request("/menus/1/comments")
    check(
        any(comment.get("target_type") == "recipe" for comment in menu_comments),
        "menu review supports linked comments",
    )
    _, _, recipe_comments = request("/recipes/43/comments")
    check(isinstance(recipe_comments, list), "recipe review comment history")

    print("\nAll API smoke checks passed.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, HTTPError, URLError, KeyError, ValueError) as exc:
        print(f"FAIL  {exc}", file=sys.stderr)
        raise SystemExit(1)
