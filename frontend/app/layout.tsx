import "./globals.css";
import Link from "next/link";
import type { ReactNode } from "react";

export const metadata = {
  title: "NYC Aging Menu Planner MVP",
  description: "Standalone menu planning recommendation prototype for NYC Aging",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="app-shell">
          <header className="topbar">
            <div>
              <div className="eyebrow">NYC Aging</div>
              <h1>Menu Planning Recommendation MVP</h1>
            </div>
            <nav className="nav">
              <Link href="/">Home</Link>
              <Link href="/menus/new">Build Menu</Link>
              <Link href="/recipes">Recipes</Link>
              <Link href="/analytics">Analytics</Link>
            </nav>
          </header>
          <main className="content">{children}</main>
        </div>
      </body>
    </html>
  );
}
