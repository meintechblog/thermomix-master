"use client";

import { useState, useMemo } from "react";
import type { Recipe } from "@/lib/recipes";
import { RecipeCard } from "./RecipeCard";

function normalize(s: string): string {
  return s.toLowerCase()
    .replace(/ä/g, "a").replace(/ö/g, "o").replace(/ü/g, "u").replace(/ß/g, "ss")
    .normalize("NFD").replace(/[̀-ͯ]/g, "");
}

export function RecipeGrid({ recipes }: { recipes: Recipe[] }) {
  const [query, setQuery] = useState("");

  const filtered = useMemo(() => {
    if (!query.trim()) return recipes;
    const q = normalize(query.trim());
    return recipes.filter(r => {
      const hay = normalize([
        r.title,
        r.subtitle || "",
        r.slug,
        r.hfCardNumber ? `#${r.hfCardNumber}` : "",
        r.ingredients.join(" "),
        r.diet || "",
      ].join(" "));
      return hay.includes(q);
    });
  }, [recipes, query]);

  return (
    <section>
      <div className="flex items-baseline justify-between mb-6 gap-4 flex-wrap">
        <h2 className="font-display text-3xl font-bold text-charcoal-900">
          Unsere Kollektion{" "}
          <span className="text-charcoal-400 font-normal text-2xl">
            ({filtered.length}{filtered.length !== recipes.length ? ` / ${recipes.length}` : ""})
          </span>
        </h2>
        <div className="relative flex-1 min-w-[240px] max-w-md">
          <input
            type="search"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Rezept suchen — Name, Zutat, HF-#…"
            className="w-full pl-10 pr-9 py-2.5 rounded-full border border-charcoal-200 bg-white text-charcoal-800 placeholder-charcoal-400 focus:outline-none focus:ring-2 focus:ring-hero-500 focus:border-transparent transition"
            aria-label="Rezepte filtern"
          />
          <svg
            className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-charcoal-400 pointer-events-none"
            fill="none" stroke="currentColor" viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
              d="M21 21l-4.35-4.35M17 11a6 6 0 11-12 0 6 6 0 0112 0z" />
          </svg>
          {query && (
            <button
              type="button"
              onClick={() => setQuery("")}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-charcoal-400 hover:text-charcoal-700 text-lg leading-none"
              aria-label="Suche zurücksetzen"
            >
              ×
            </button>
          )}
        </div>
      </div>

      {filtered.length === 0 ? (
        <div className="text-center py-16 bg-white rounded-2xl border border-charcoal-100">
          <p className="text-charcoal-500">
            {recipes.length === 0
              ? "Noch keine Rezepte. Pinne oben eine HelloFresh-URL."
              : `Keine Rezepte für „${query}" gefunden.`}
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filtered.map(r => <RecipeCard key={r.slug} recipe={r} />)}
        </div>
      )}
    </section>
  );
}
