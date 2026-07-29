"use client";

import { useEffect, useState } from "react";
import { apiFetch } from "../lib/api";

export type Recipe = {
  recipe_id: number;
  recipe_name: string;
  meal_type: string;
  category: string;
  calories: number;
  sodium_mg: number;
  protein_g: number;
  fiber_g: number;
  fat_g: number;
  tags: string[];
  is_approved: boolean;
};

export function RecipeSearch({
  onAdd,
}: {
  onAdd: (recipe: Recipe) => void;
}) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<Recipe[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const handle = setTimeout(() => {
      const run = async () => {
        setLoading(true);
        try {
          const data = await apiFetch<Recipe[]>(`/recipes/search?q=${encodeURIComponent(query)}`);
          setResults(data);
        } catch {
          setResults([]);
        } finally {
          setLoading(false);
        }
      };
      void run();
    }, 220);
    return () => clearTimeout(handle);
  }, [query]);

  return (
    <div className="section">
      <h3>Search recipes</h3>
      <input
        className="input"
        placeholder="Search approved recipes by name, tag, category, or meal type"
        value={query}
        onChange={(event) => setQuery(event.target.value)}
      />
      <div className="muted small" style={{ marginTop: 8 }}>{loading ? "Searching..." : `${results.length} results`}</div>
      <div className="list" style={{ marginTop: 14 }}>
        {results.map((recipe) => (
          <div key={recipe.recipe_id} className="recipe-chip">
            <div>
              <strong>{recipe.recipe_name}</strong>
              <div className="muted small">
                {recipe.meal_type} · {recipe.category} · {recipe.calories} kcal · {recipe.sodium_mg} mg sodium
              </div>
            </div>
            <button className="button" onClick={() => onAdd(recipe)}>Add</button>
          </div>
        ))}
        {!loading && results.length === 0 ? <div className="empty-state">No recipes found.</div> : null}
      </div>
    </div>
  );
}

