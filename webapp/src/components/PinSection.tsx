"use client";

import { useState } from "react";
import { PinForm } from "./PinForm";

export function PinSection() {
  const [open, setOpen] = useState(false);

  return (
    <section className="mb-8 sm:mb-12">
      <div className="bg-gradient-to-br from-hero-600 to-hero-700 rounded-2xl sm:rounded-3xl text-white shadow-card overflow-hidden transition-all">
        <button
          type="button"
          onClick={() => setOpen(o => !o)}
          aria-expanded={open}
          className="w-full flex items-center justify-between gap-3 text-left px-5 sm:px-8 py-4 sm:py-5 hover:bg-white/5 transition"
        >
          <div className="flex items-center gap-3 min-w-0">
            <span className="text-2xl shrink-0" aria-hidden>📌</span>
            <div className="min-w-0">
              <h1 className="font-display text-xl sm:text-2xl md:text-3xl font-bold leading-tight truncate">
                HelloFresh-Rezept pinnen
              </h1>
              {!open && (
                <p className="text-hero-100 text-xs sm:text-sm truncate">
                  Tippen zum Aufklappen — URL pasten, Worker übernimmt den Rest.
                </p>
              )}
            </div>
          </div>
          <svg
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2.5"
            strokeLinecap="round"
            strokeLinejoin="round"
            className={"shrink-0 transition-transform duration-200 " + (open ? "rotate-180" : "")}
            aria-hidden
          >
            <polyline points="6 9 12 15 18 9" />
          </svg>
        </button>
        {open && (
          <div className="px-5 sm:px-8 pb-5 sm:pb-8 -mt-1">
            <p className="text-hero-100 mb-5 text-sm sm:text-base">
              Paste eine HelloFresh-URL — der Worker scrapet die Karte, adaptiert sie auf native
              Thermomix-Style mit Koch-Befehl-Chips und publisht sie auf Cookidoo.
            </p>
            <PinForm />
          </div>
        )}
      </div>
    </section>
  );
}
