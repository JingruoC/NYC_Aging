import Link from "next/link";

export default function HomePage() {
  return (
    <div className="grid" style={{ gap: 20 }}>
      <section className="hero">
        <div className="hero-grid">
          <div>
            <div className="eyebrow">Standalone prototype</div>
            <h2>Build a full day menu from approved recipes, faster.</h2>
            <p>
              This MVP helps NYC Aging staff search recipes, assemble menus, see nutrition totals, and get
              rule-based recommendations from historical patterns. No generative AI is used.
            </p>
            <div className="hero-actions">
              <Link className="button" href="/menus/new">Start building a menu</Link>
              <Link className="ghost-button" href="/recipes">Browse recipes</Link>
              <Link className="ghost-button" href="/analytics">View analytics</Link>
            </div>
          </div>
          <div className="metric-card">
            <h4>What it does</h4>
            <div className="status-stack">
              <div className="status-row"><span>Autocomplete from approved recipes</span><span className="pill brand">On</span></div>
              <div className="status-row"><span>Nutrition pass / warning / fail</span><span className="pill good">On</span></div>
              <div className="status-row"><span>Historical menu similarity</span><span className="pill brand">On</span></div>
              <div className="status-row"><span>Revision suggestions</span><span className="pill warn">Rule-based</span></div>
            </div>
          </div>
        </div>
      </section>

      <section className="grid cols-3">
        <div className="section">
          <h3>1. Search and pick recipes</h3>
          <p className="muted">Autocomplete and browse from a seeded catalog of 40 realistic recipes.</p>
        </div>
        <div className="section">
          <h3>2. Analyze nutrition</h3>
          <p className="muted">Totals update as recipes are added so staff can see warnings early.</p>
        </div>
        <div className="section">
          <h3>3. Get suggestions</h3>
          <p className="muted">The app recommends complementary recipes, revisions, and similar historical menus.</p>
        </div>
      </section>
    </div>
  );
}

