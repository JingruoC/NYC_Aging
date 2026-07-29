"use client";

import { RecipeCatalog } from "../../components/RecipeCatalog";

export default function RecipesPage() {
  return (
    <div className="grid" style={{ gap: 18 }}>
      <section className="hero">
        <div className="hero-grid">
          <div>
            <div className="eyebrow">Recipe library</div>
            <h2>Browse all approved recipes with tags and nutrition at a glance.</h2>
            <p>
              Use the gallery to preview meal types, categories, and tags. The most relevant recipes rise to the top
              based on historical menu patterns.
            </p>
          </div>
          <div className="metric-card">
            <h4>How to use it</h4>
            <div className="status-stack">
              <div className="status-row"><span>Search by tag or category</span><span className="pill brand">Live</span></div>
              <div className="status-row"><span>See all recipe previews</span><span className="pill good">Visible</span></div>
              <div className="status-row"><span>Recommended items first</span><span className="pill warn">Ranked</span></div>
            </div>
          </div>
        </div>
      </section>
      <RecipeCatalog selectedRecipeIds={[]} />
    </div>
  );
}
