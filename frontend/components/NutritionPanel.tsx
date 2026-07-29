"use client";

import { StatusPill } from "./StatusPill";

type StatusRow = {
  nutrient_key: string;
  total: number;
  unit: string;
  status: "pass" | "warning" | "fail";
  message: string;
};

export function NutritionPanel({
  totals,
  statuses,
  overallStatus,
}: {
  totals?: Record<string, number>;
  statuses?: StatusRow[];
  overallStatus?: "pass" | "warning" | "fail";
}) {
  return (
    <div className="section">
      <h3>Nutrition analysis</h3>
      <div className="meta">
        <StatusPill status={overallStatus ?? "brand"} label={`Overall: ${overallStatus ?? "pending"}`} />
      </div>
      <div className="grid cols-3" style={{ marginTop: 14 }}>
        {totals &&
          Object.entries(totals).map(([key, value]) => (
            <div key={key} className="metric-card">
              <h4>{key.replaceAll("_", " ")}</h4>
              <div className="metric-value">{value}</div>
            </div>
          ))}
      </div>
      <div className="status-stack" style={{ marginTop: 16 }}>
        {statuses?.map((row) => (
          <div key={row.nutrient_key} className="status-row">
            <div>
              <strong>{row.nutrient_key.replaceAll("_", " ")}</strong>
              <div className="muted small">{row.message}</div>
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
              <span className="small">{row.total} {row.unit}</span>
              <StatusPill status={row.status} label={row.status} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

