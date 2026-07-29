"use client";

import { useEffect, useMemo, useState, type DragEvent } from "react";
import { apiFetch } from "../lib/api";
import type { Recipe } from "./RecipeSearch";
import { StatusPill } from "./StatusPill";

type AutocompleteItem = {
  recipe: Recipe;
  score: number;
  reasons: string[];
};

type AnalyticsTopRecipe = {
  recipe_id: number;
  recipe_name: string;
  count: number;
  category: string;
};

type AnalyticsResponse = {
  top_recipes: AnalyticsTopRecipe[];
};

const mealTypeOrder: Record<string, number> = {
  breakfast: 0,
  lunch: 1,
  dinner: 2,
  snack: 3,
};

function normalize(text: string) {
  return text.trim().toLowerCase();
}

function recipeMatches(recipe: Recipe, query: string) {
  if (!query) return true;
  const haystack = [
    recipe.recipe_name,
    recipe.meal_type,
    recipe.category,
    ...(recipe.tags ?? []),
  ]
    .join(" ")
    .toLowerCase();
  return query.split(/\s+/).every((part) => haystack.includes(part));
}

function recipeScore(recipe: Recipe, recommendations: AutocompleteItem[], popularIds: number[]) {
  const recommended = recommendations.find((item) => item.recipe.recipe_id === recipe.recipe_id);
  if (recommended) return 200 - recommended.score * 10;
  const popularRank = popularIds.indexOf(recipe.recipe_id);
  if (popularRank >= 0) return 100 + popularRank;
  return 500 + mealTypeOrder[recipe.meal_type] * 25 + recipe.recipe_name.localeCompare("");
}

function RecipeCard({
  recipe,
  compact = false,
  onAdd,
  onDragStart,
}: {
  recipe: Recipe;
  compact?: boolean;
  onAdd?: (recipe: Recipe) => void;
  onDragStart?: (recipe: Recipe, event: DragEvent<HTMLDivElement>) => void;
}) {
  return (
    <div
      className={`recipe-card ${compact ? "compact" : ""}`}
      draggable={Boolean(onDragStart)}
      onDragStart={(event) => onDragStart?.(recipe, event)}
    >
      <div className="recipe-card-head">
        <div>
          <strong>{recipe.recipe_name}</strong>
          <div className="muted small">
            {recipe.meal_type} · {recipe.category} · {recipe.calories} kcal
          </div>
        </div>
        {onAdd ? (
          <button className="button small-button" onClick={() => onAdd(recipe)}>
            Add
          </button>
        ) : null}
      </div>
      <div className="tag-list">
        {(recipe.tags ?? []).map((tag) => (
          <span key={tag} className="tag-chip">
            {tag}
          </span>
        ))}
      </div>
      {!compact ? (
        <div className="nutrition-strip">
          <span>{recipe.sodium_mg} mg sodium</span>
          <span>{recipe.protein_g} g protein</span>
          <span>{recipe.fiber_g} g fiber</span>
        </div>
      ) : null}
    </div>
  );
}

export function RecipeCatalog({
  selectedRecipeIds,
  onAddRecipe,
  onDragRecipe,
}: {
  selectedRecipeIds: number[];
  onAddRecipe?: (recipe: Recipe) => void;
  onDragRecipe?: (recipe: Recipe, event: DragEvent<HTMLDivElement>) => void;
}) {
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [query, setQuery] = useState("");
  const [recommendations, setRecommendations] = useState<AutocompleteItem[]>([]);
  const [popularRecipes, setPopularRecipes] = useState<AnalyticsTopRecipe[]>([]);

  useEffect(() => {
    const load = async () => {
      const [recipeData, analyticsData] = await Promise.all([
        apiFetch<Recipe[]>("/recipes?approved_only=true"),
        apiFetch<AnalyticsResponse>("/analytics"),
      ]);
      setRecipes(recipeData);
      setPopularRecipes(analyticsData.top_recipes ?? []);
    };
    void load().catch(() => {
      setRecipes([]);
      setPopularRecipes([]);
    });
  }, []);

  useEffect(() => {
    if (!selectedRecipeIds.length) {
      setRecommendations([]);
      return;
    }

    const load = async () => {
      const data = await apiFetch<{ items: AutocompleteItem[] }>("/recommendations/autocomplete", {
        method: "POST",
        body: JSON.stringify({ selected_recipe_ids: selectedRecipeIds, limit: 8 }),
      });
      setRecommendations(data.items ?? []);
    };
    void load().catch(() => setRecommendations([]));
  }, [selectedRecipeIds]);

  const filteredRecipes = useMemo(() => {
    const normalizedQuery = normalize(query);
    const popularIds = popularRecipes.map((item) => item.recipe_id);
    const recommendationIds = recommendations.map((item) => item.recipe.recipe_id);

    return [...recipes]
      .filter((recipe) => recipeMatches(recipe, normalizedQuery))
      .sort((a, b) => {
        const aRecommended = recommendationIds.indexOf(a.recipe_id);
        const bRecommended = recommendationIds.indexOf(b.recipe_id);
        if (aRecommended >= 0 || bRecommended >= 0) {
          if (aRecommended === -1) return 1;
          if (bRecommended === -1) return -1;
          return aRecommended - bRecommended;
        }
        const aPopular = popularIds.indexOf(a.recipe_id);
        const bPopular = popularIds.indexOf(b.recipe_id);
        if (aPopular >= 0 || bPopular >= 0) {
          if (aPopular === -1) return 1;
          if (bPopular === -1) return -1;
          return aPopular - bPopular;
        }
        return recipeScore(a, recommendations, popularIds) - recipeScore(b, recommendations, popularIds);
      });
  }, [query, recipes, popularRecipes, recommendations]);

  const popularMap = new Map(popularRecipes.map((item) => [item.recipe_id, item]));

  const topRecipes: Recipe[] = recommendations.length
    ? recommendations.slice(0, 6).map((item) => item.recipe)
    : popularRecipes
        .map((item) => recipes.find((recipe) => recipe.recipe_id === item.recipe_id))
        .filter((recipe): recipe is Recipe => Boolean(recipe))
        .slice(0, 6);

  return (
    <div className="section">
      <div className="planner-toolbar">
        <div>
          <h3 style={{ marginBottom: 6 }}>Recipe gallery</h3>
          <p className="muted" style={{ margin: 0 }}>
            Browse recipe previews, or use search to narrow the gallery. The most relevant items stay pinned at the top.
          </p>
        </div>
        <input
          className="input"
          placeholder="Search by recipe, category, meal type, or tag"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
        />
      </div>

      <div className="section-inner">
        <div className="section-header">
          <h4>Recommended first</h4>
          <StatusPill status="brand" label={selectedRecipeIds.length ? "Based on current menu" : "Popular recipes"} />
        </div>
        <div className="recipe-strip">
          {topRecipes.map((recipe) => {
            const recommendation = recommendations.find((item) => item.recipe.recipe_id === recipe.recipe_id);
            const popular = popularMap.get(recipe.recipe_id);
            return (
            <div key={recipe.recipe_id} className="recipe-strip-card">
                <RecipeCard recipe={recipe} compact onAdd={onAddRecipe} onDragStart={onDragRecipe} />
                <div className="muted small" style={{ marginTop: 8 }}>
                  {recommendation ? recommendation.reasons[0] : `Used ${popular?.count ?? 0} times in historical menus`}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      <div className="section-inner">
        <div className="section-header">
          <h4>All recipes</h4>
          <StatusPill status="brand" label={`${filteredRecipes.length} shown`} />
        </div>
        <div className="recipe-grid">
          {filteredRecipes.map((recipe) => (
            <RecipeCard key={recipe.recipe_id} recipe={recipe} onAdd={onAddRecipe} onDragStart={onDragRecipe} />
          ))}
        </div>
      </div>
    </div>
  );
}

export { RecipeCard };
