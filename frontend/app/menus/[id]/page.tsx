import Link from "next/link";
import { SITE_URL } from "../../../lib/api";

export const dynamic = "force-dynamic";

async function getMenu(menuId: string) {
  const res = await fetch(new URL(`/api/menus/${menuId}`, SITE_URL).toString(), { cache: "no-store" });
  if (!res.ok) throw new Error("Menu not found");
  return res.json();
}

const MEAL_SLOTS = ["breakfast", "lunch", "dinner"] as const;

function formatDate(value: string) {
  return new Date(`${value}T00:00:00`).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
  });
}

export default async function MenuDetailPage({ params }: { params: { id: string } }) {
  const { id } = params;
  const data = await getMenu(id);
  const menu = data.menu;
  const analysis = data.analysis;
  const dayCount = menu.days_per_week ?? 5;
  const startDate = menu.start_date ?? menu.service_date;
  const calendarDays = Array.from({ length: dayCount }, (_, index) => {
    const date = new Date(`${startDate}T00:00:00`);
    date.setDate(date.getDate() + index);
    return date;
  });

  const schedule = calendarDays.map((_, dayIndex) =>
    MEAL_SLOTS.reduce<Record<(typeof MEAL_SLOTS)[number], any | null>>((acc, mealSlot) => {
      acc[mealSlot] = menu.items.find((item: any) => item.day_index === dayIndex && item.meal_slot === mealSlot) ?? null;
      return acc;
    }, { breakfast: null, lunch: null, dinner: null }),
  );

  return (
    <div className="grid" style={{ gap: 18 }}>
      <section className="hero">
        <div className="hero-grid">
          <div>
            <div className="eyebrow">Saved weekly menu</div>
            <h2>{menu.name}</h2>
            <p>
              Week {menu.cycle_week} · {formatDate(startDate)} to {formatDate(menu.end_date ?? startDate)}
            </p>
          </div>
          <div className="metric-card">
            <h4>Overall status</h4>
            <div className="metric-value" style={{ fontSize: 28 }}>
              {analysis.overall_status}
            </div>
          </div>
        </div>
      </section>

      <section className="section">
        <h3>Weekly calendar</h3>
        <div className="calendar-grid" style={{ gridTemplateColumns: `110px repeat(${dayCount}, minmax(0, 1fr))` }}>
          <div className="calendar-corner" />
          {calendarDays.map((date, dayIndex) => (
            <div key={dayIndex} className="calendar-day-header">
              <div className="day-label">{date.toLocaleDateString("en-US", { weekday: "short" })}</div>
              <div className="date-label">{formatDate(date.toISOString().slice(0, 10))}</div>
            </div>
          ))}

          {MEAL_SLOTS.map((mealSlot) => (
            <div key={mealSlot} className="meal-row">
              <div className="meal-label">{mealSlot}</div>
              {schedule.map((daySlots, dayIndex) => {
                const item = daySlots[mealSlot];
                return (
                  <div key={`${mealSlot}-${dayIndex}`} className={`calendar-cell ${item ? "filled" : ""}`}>
                    {item ? (
                      <div className="scheduled-card">
                        <strong>{item.recipe.recipe_name}</strong>
                        <div className="muted small">
                          {item.recipe.category} · {item.recipe.calories} kcal
                        </div>
                      </div>
                    ) : (
                      <div className="calendar-placeholder">No recipe assigned</div>
                    )}
                  </div>
                );
              })}
            </div>
          ))}
        </div>
      </section>

      <div className="columns two">
        <section className="section">
          <h3>Nutrition analysis</h3>
          <div className="status-stack">
            {analysis.statuses.map((status: any) => (
              <div key={status.nutrient_key} className="status-row">
                <div>
                  <strong>{status.nutrient_key}</strong>
                  <div className="muted small">{status.message}</div>
                </div>
                <div>
                  {status.total} {status.unit}
                </div>
              </div>
            ))}
          </div>
        </section>

        <section className="section">
          <h3>Recommendations</h3>
          <div className="list">
            <div className="card" style={{ padding: 16 }}>
              <h4>Autocomplete</h4>
              {data.autocomplete.map((item: any) => (
                <div key={item.recipe.recipe_id} className="muted small">
                  {item.recipe.recipe_name}
                </div>
              ))}
            </div>
            <div className="card" style={{ padding: 16 }}>
              <h4>Similar menus</h4>
              {data.similar_menus.map((item: any) => (
                <div key={item.id} className="muted small">
                  {item.name} ({Math.round(item.similarity * 100)}%)
                </div>
              ))}
            </div>
            <div className="card" style={{ padding: 16 }}>
              <h4>Revisions</h4>
              {Object.entries(data.revisions.suggestions).map(([key, items]: any) => (
                <div key={key} style={{ marginBottom: 12 }}>
                  <strong>{key}</strong>
                  <div className="muted small">{items.length} suggestions</div>
                </div>
              ))}
            </div>
          </div>
        </section>
      </div>

      <Link className="ghost-button" href="/menus/new">
        Back to builder
      </Link>
    </div>
  );
}
