import { SITE_URL } from "../../lib/api";

export const dynamic = "force-dynamic";

async function getAnalytics() {
  const res = await fetch(new URL("/api/analytics", SITE_URL).toString(), { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to load analytics");
  return res.json();
}

export default async function AnalyticsPage() {
  const data = await getAnalytics();
  return (
    <div className="grid" style={{ gap: 18 }}>
      <section className="section">
        <h3>Recipe usage</h3>
        <table className="table">
          <thead>
            <tr><th>Recipe</th><th>Category</th><th>Usage</th></tr>
          </thead>
          <tbody>
            {data.top_recipes.map((row: any) => (
              <tr key={row.recipe_id}>
                <td>{row.recipe_name}</td>
                <td>{row.category}</td>
                <td>{row.count}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      <div className="columns two">
        <section className="section">
          <h3>Common pairings</h3>
          <table className="table">
            <thead>
              <tr><th>Recipe A</th><th>Recipe B</th><th>Count</th></tr>
            </thead>
            <tbody>
              {data.top_pairings.map((row: any, index: number) => (
                <tr key={`${row.recipe_a}-${row.recipe_b}-${index}`}>
                  <td>{row.recipe_a}</td>
                  <td>{row.recipe_b}</td>
                  <td>{row.count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>

        <section className="section">
          <h3>Recipe mix</h3>
          <div className="grid cols-2">
            <div className="metric-card">
              <h4>Categories</h4>
              {data.category_counts.map((row: any) => (
                <div key={row.category} className="status-row">
                  <span>{row.category}</span>
                  <strong>{row.count}</strong>
                </div>
              ))}
            </div>
            <div className="metric-card">
              <h4>Meal types</h4>
              {data.meal_type_counts.map((row: any) => (
                <div key={row.meal_type} className="status-row">
                  <span>{row.meal_type}</span>
                  <strong>{row.count}</strong>
                </div>
              ))}
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
