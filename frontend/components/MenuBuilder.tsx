"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { apiFetch } from "../lib/api";
import { NutritionPanel } from "./NutritionPanel";
import { RecipeCatalog } from "./RecipeCatalog";
import type { Recipe } from "./RecipeSearch";
import { StatusPill } from "./StatusPill";

type MealSlot = "breakfast" | "lunch" | "dinner";
type CycleWeek = 1 | 2 | 3 | 4;
type DaysPerWeek = 5 | 7;

type Analysis = {
  totals: Record<string, number>;
  statuses: { nutrient_key: string; total: number; unit: string; status: "pass" | "warning" | "fail"; message: string }[];
  overall_status: "pass" | "warning" | "fail";
  selected_recipes: Recipe[];
};

type RecommendationItem = {
  recipe: Recipe;
  score: number;
  reasons: string[];
};

type CellAssignment = Recipe | null;
type WeekSchedule = Record<number, Record<MealSlot, CellAssignment>>;

const MEAL_SLOTS: MealSlot[] = ["breakfast", "lunch", "dinner"];
const WEEK_DAYS: Record<DaysPerWeek, string[]> = {
  5: ["Mon", "Tue", "Wed", "Thu", "Fri"],
  7: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
};

function parseDate(value: string) {
  return new Date(`${value}T00:00:00`);
}

function formatDate(value: Date) {
  return value.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
  });
}

function formatWeekday(value: Date) {
  return value.toLocaleDateString("en-US", {
    weekday: "short",
  });
}

function addDays(value: Date, amount: number) {
  const next = new Date(value);
  next.setDate(next.getDate() + amount);
  return next;
}

function blankWeek(daysPerWeek: DaysPerWeek): WeekSchedule {
  return Array.from({ length: daysPerWeek }).reduce<WeekSchedule>((acc, _, dayIndex) => {
    acc[dayIndex] = {
      breakfast: null,
      lunch: null,
      dinner: null,
    };
    return acc;
  }, {});
}

function buildItems(schedule: WeekSchedule) {
  const items: { recipe_id: number; position: number; day_index: number; meal_slot: MealSlot }[] = [];
  let position = 1;
  Object.entries(schedule).forEach(([dayIndex, slots]) => {
    MEAL_SLOTS.forEach((mealSlot) => {
      const recipe = slots[mealSlot];
      if (!recipe) return;
      items.push({
        recipe_id: recipe.recipe_id,
        position,
        day_index: Number(dayIndex),
        meal_slot: mealSlot,
      });
      position += 1;
    });
  });
  return items;
}

function flattenSelectedIds(schedule: WeekSchedule) {
  const ids = new Set<number>();
  Object.values(schedule).forEach((slots) => {
    MEAL_SLOTS.forEach((mealSlot) => {
      const recipe = slots[mealSlot];
      if (recipe) ids.add(recipe.recipe_id);
    });
  });
  return Array.from(ids);
}

function sameMealSlot(recipe: Recipe, mealSlot: MealSlot) {
  if (mealSlot === "breakfast") return recipe.meal_type === "breakfast";
  if (mealSlot === "lunch") return recipe.meal_type === "lunch";
  return recipe.meal_type === "dinner" || recipe.meal_type === "snack";
}

function emptyDaySchedule(): Record<MealSlot, CellAssignment> {
  return { breakfast: null, lunch: null, dinner: null };
}

export function MenuBuilder() {
  const router = useRouter();
  const [menuName, setMenuName] = useState("Weekly Menu");
  const [startDate, setStartDate] = useState(new Date().toISOString().slice(0, 10));
  const [daysPerWeek, setDaysPerWeek] = useState<DaysPerWeek>(5);
  const [cycleWeek, setCycleWeek] = useState<CycleWeek>(1);
  const [schedulesByCycle, setSchedulesByCycle] = useState<Record<CycleWeek, WeekSchedule>>({
    1: blankWeek(5),
    2: blankWeek(5),
    3: blankWeek(5),
    4: blankWeek(5),
  });
  const [activeCell, setActiveCell] = useState<{ dayIndex: number; mealSlot: MealSlot } | null>(null);
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [autocomplete, setAutocomplete] = useState<RecommendationItem[]>([]);
  const [revisions, setRevisions] = useState<Record<string, RecommendationItem[]>>({});
  const [similarMenus, setSimilarMenus] = useState<any[]>([]);
  const [saving, setSaving] = useState(false);

  const activeSchedule = schedulesByCycle[cycleWeek];
  const selectedIds = useMemo(() => flattenSelectedIds(activeSchedule), [activeSchedule]);
  const placedRecipeIds = useMemo(() => buildItems(activeSchedule).map((item) => item.recipe_id), [activeSchedule]);
  const placedCount = placedRecipeIds.length;
  const scheduleDates = useMemo(() => {
    const base = parseDate(startDate);
    return Array.from({ length: daysPerWeek }, (_, index) => addDays(base, index));
  }, [startDate, daysPerWeek]);

  const endDate = useMemo(() => {
    const finalDate = addDays(parseDate(startDate), daysPerWeek - 1);
    return finalDate.toISOString().slice(0, 10);
  }, [startDate, daysPerWeek]);

  useEffect(() => {
    setSchedulesByCycle({
      1: blankWeek(daysPerWeek),
      2: blankWeek(daysPerWeek),
      3: blankWeek(daysPerWeek),
      4: blankWeek(daysPerWeek),
    });
    setActiveCell(null);
  }, [daysPerWeek]);

  useEffect(() => {
    if (!selectedIds.length) {
      setAnalysis(null);
      setAutocomplete([]);
      setRevisions({});
      setSimilarMenus([]);
      return;
    }

    const run = async () => {
      const [analysisData, autoData, revisionData, similarData] = await Promise.all([
        apiFetch<Analysis>("/menus/analyze", {
          method: "POST",
          body: JSON.stringify({ recipe_ids: placedRecipeIds }),
        }),
        apiFetch<{ items: RecommendationItem[] }>("/recommendations/autocomplete", {
          method: "POST",
          body: JSON.stringify({ selected_recipe_ids: selectedIds, limit: 8 }),
        }),
        apiFetch<{ suggestions: Record<string, RecommendationItem[]> }>("/recommendations/revisions", {
          method: "POST",
          body: JSON.stringify({ selected_recipe_ids: selectedIds, limit: 8 }),
        }),
        apiFetch<{ items: any[] }>("/recommendations/similar-menus", {
          method: "POST",
          body: JSON.stringify({ selected_recipe_ids: selectedIds, limit: 5 }),
        }),
      ]);
      setAnalysis(analysisData);
      setAutocomplete(autoData.items ?? []);
      setRevisions(revisionData.suggestions ?? {});
      setSimilarMenus(similarData.items ?? []);
    };

    void run().catch((error) => {
      console.error(error);
    });
  }, [placedRecipeIds, selectedIds]);

  const updateCell = (dayIndex: number, mealSlot: MealSlot, recipe: Recipe | null) => {
    setSchedulesByCycle((current) => ({
      ...current,
      [cycleWeek]: {
        ...current[cycleWeek],
        [dayIndex]: {
          ...(current[cycleWeek][dayIndex] ?? emptyDaySchedule()),
          [mealSlot]: recipe,
        },
      },
    }));
  };

  const assignRecipe = (recipe: Recipe) => {
    if (activeCell) {
      const activeMealSlot = activeCell.mealSlot;
      if (!sameMealSlot(recipe, activeMealSlot)) {
        // Fall back to the first compatible empty cell instead of doing nothing.
      } else {
        updateCell(activeCell.dayIndex, activeMealSlot, recipe);
        return;
      }
    }

    const matchingDay = scheduleDates.findIndex((_, dayIndex) =>
      MEAL_SLOTS.some((mealSlot) => sameMealSlot(recipe, mealSlot) && !activeSchedule[dayIndex][mealSlot]),
    );

    if (matchingDay >= 0) {
      const mealSlot = MEAL_SLOTS.find((slot) => sameMealSlot(recipe, slot) && !activeSchedule[matchingDay][slot]);
      if (mealSlot) {
        updateCell(matchingDay, mealSlot, recipe);
      }
    }
  };

  const clearCycle = () => {
    setSchedulesByCycle((current) => ({
      ...current,
      [cycleWeek]: blankWeek(daysPerWeek),
    }));
    setActiveCell(null);
  };

  const saveMenu = async () => {
    setSaving(true);
    try {
      const items = buildItems(activeSchedule);
      const created = await apiFetch<{ id: number }>("/menus", {
        method: "POST",
        body: JSON.stringify({
          name: menuName,
          start_date: startDate,
          end_date: endDate,
          days_per_week: daysPerWeek,
          cycle_week: cycleWeek,
          items,
        }),
      });
      router.push(`/menus/${created.id}`);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="grid" style={{ gap: 18 }}>
      <section className="section">
        <div className="planner-toolbar">
          <div className="grid" style={{ gap: 12 }}>
            <label>
              <div className="small muted">Menu name</div>
              <input className="input" value={menuName} onChange={(event) => setMenuName(event.target.value)} />
            </label>
            <div className="range-chip">
              <strong>{formatDate(parseDate(startDate))}</strong>
              <span className="muted small">to</span>
              <strong>{formatDate(parseDate(endDate))}</strong>
            </div>
          </div>
          <div className="grid" style={{ gap: 12 }}>
            <label>
              <div className="small muted">Start date</div>
              <input className="input" type="date" value={startDate} onChange={(event) => setStartDate(event.target.value)} />
            </label>
            <div className="toggle-row">
              <button className={daysPerWeek === 5 ? "button" : "ghost-button"} onClick={() => setDaysPerWeek(5)}>
                5-day workweek
              </button>
              <button className={daysPerWeek === 7 ? "button" : "ghost-button"} onClick={() => setDaysPerWeek(7)}>
                7-day week
              </button>
            </div>
          </div>
          <div className="grid" style={{ gap: 12 }}>
            <div className="week-switcher">
              {[1, 2, 3, 4].map((week) => (
                <button
                  key={week}
                  className={cycleWeek === week ? "button" : "ghost-button"}
                  onClick={() => setCycleWeek(week as CycleWeek)}
                >
                  Week {week}
                </button>
              ))}
            </div>
            <div className="hero-actions">
              <StatusPill status="brand" label={`${selectedIds.length} recipes placed`} />
              <StatusPill status="brand" label={`${placedCount} menu items`} />
              <StatusPill status={analysis?.overall_status ?? "brand"} label={`Overall: ${analysis?.overall_status ?? "pending"}`} />
              <button className="button" disabled={!selectedIds.length || saving} onClick={saveMenu}>
                {saving ? "Saving..." : "Save week"}
              </button>
              <button className="ghost-button" onClick={clearCycle}>
                Clear week
              </button>
            </div>
          </div>
        </div>
      </section>

      <div className="columns planner-layout">
        <section className="section calendar-panel">
          <div className="section-header">
            <div>
              <h3 style={{ marginBottom: 6 }}>Weekly menu calendar</h3>
              <p className="muted" style={{ margin: 0 }}>
                Drag recipes into breakfast, lunch, and dinner. Click a cell to make it active, then click a recipe card to place it.
              </p>
            </div>
          </div>

          <div className="calendar-grid" style={{ gridTemplateColumns: `110px repeat(${daysPerWeek}, minmax(0, 1fr))` }}>
            <div className="calendar-corner" />
            {scheduleDates.map((date, dayIndex) => (
              <div key={dayIndex} className="calendar-day-header">
                <div className="day-label">{WEEK_DAYS[daysPerWeek][dayIndex]}</div>
                <div className="date-label">{formatDate(date)}</div>
              </div>
            ))}

            {MEAL_SLOTS.map((mealSlot) => (
              <div key={mealSlot} className="meal-row">
              <div className="meal-label">{mealSlot}</div>
                {scheduleDates.map((_, dayIndex) => {
                  const daySchedule = activeSchedule[dayIndex] ?? emptyDaySchedule();
                  const assigned = daySchedule[mealSlot];
                  const isActive = activeCell?.dayIndex === dayIndex && activeCell?.mealSlot === mealSlot;
                  return (
                    <div
                      key={`${dayIndex}-${mealSlot}`}
                      className={`calendar-cell ${isActive ? "active" : ""} ${assigned ? "filled" : ""}`}
                      onDragOver={(event) => event.preventDefault()}
                      onDrop={(event) => {
                        event.preventDefault();
                        let recipe: Recipe | null = null;
                        const rawRecipe = event.dataTransfer.getData("application/json");
                        try {
                          recipe = rawRecipe ? (JSON.parse(rawRecipe) as Recipe) : null;
                        } catch {
                          recipe = null;
                        }
                        if (!recipe) return;
                        if (!sameMealSlot(recipe, mealSlot)) return;
                        updateCell(dayIndex, mealSlot, recipe);
                      }}
                      onClick={() => setActiveCell({ dayIndex, mealSlot })}
                    >
                      {assigned ? (
                        <div className="scheduled-card">
                          <strong>{assigned.recipe_name}</strong>
                          <div className="muted small">{assigned.category}</div>
                          <button
                            className="ghost-button tiny-button"
                            onClick={(event) => {
                              event.stopPropagation();
                              updateCell(dayIndex, mealSlot, null);
                            }}
                          >
                            Remove
                          </button>
                        </div>
                      ) : (
                        <div className="calendar-placeholder">Drop a {mealSlot} recipe here</div>
                      )}
                    </div>
                  );
                })}
              </div>
            ))}
          </div>
        </section>

        <div className="grid planner-sidebar" style={{ gap: 18 }}>
          <RecipeCatalog
            selectedRecipeIds={selectedIds}
            onAddRecipe={assignRecipe}
            onDragRecipe={(recipe, event) => {
              event.dataTransfer.setData("application/json", JSON.stringify(recipe));
              event.dataTransfer.setData("text/plain", String(recipe.recipe_id));
              event.dataTransfer.effectAllowed = "copy";
            }}
          />

          {analysis ? (
            <NutritionPanel totals={analysis.totals} statuses={analysis.statuses} overallStatus={analysis.overall_status} />
          ) : null}

          <section className="section">
            <h3>Revision suggestions</h3>
            <div className="grid" style={{ gap: 12 }}>
              {Object.entries(revisions).map(([key, items]) => (
                <div key={key} className="card" style={{ padding: 16 }}>
                  <h4 style={{ marginBottom: 10 }}>{key.toUpperCase()}</h4>
                  <div className="list">
                    {items.map((item) => (
                      <div key={item.recipe.recipe_id} className="recipe-chip">
                        <div>
                          <strong>{item.recipe.recipe_name}</strong>
                          <div className="muted small">
                            {item.recipe.sodium_mg} mg sodium · {item.recipe.protein_g} g protein · {item.recipe.fiber_g} g fiber
                          </div>
                          <div className="meta">
                            {item.reasons.map((reason) => (
                              <span key={reason} className="pill warn">
                                {reason}
                              </span>
                            ))}
                          </div>
                        </div>
                        <button className="button" onClick={() => assignRecipe(item.recipe)}>
                          Add
                        </button>
                      </div>
                    ))}
                    {!items?.length ? <div className="empty-state">No revision suggestion needed.</div> : null}
                  </div>
                </div>
              ))}
              {!Object.keys(revisions).length ? <div className="empty-state">Nutrition warnings will unlock revision suggestions.</div> : null}
            </div>
          </section>

          <section className="section">
            <h3>Similar historical menus</h3>
            <div className="list">
              {similarMenus.map((menu) => (
                <div key={menu.id} className="recipe-chip">
                  <div>
                    <strong>{menu.name}</strong>
                    <div className="muted small">
                      {menu.service_date} · similarity {Math.round(menu.similarity * 100)}%
                    </div>
                    <div className="meta">
                      <StatusPill status={menu.passes_nutrition ? "pass" : "warning"} label={menu.passes_nutrition ? "passed" : "failed"} />
                    </div>
                  </div>
                </div>
              ))}
              {!similarMenus.length ? <div className="empty-state">Historical matches appear once recipes are placed.</div> : null}
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}
