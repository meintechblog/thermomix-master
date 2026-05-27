import Link from "next/link";
import { listRecipes } from "@/lib/recipes";
import { PinForm } from "@/components/PinForm";
import { RecipeGrid } from "@/components/RecipeGrid";

export const dynamic = "force-dynamic";

export default function Home() {
  const recipes = listRecipes().sort((a, b) => {
    const an = a.hfCardNumber ? parseInt(a.hfCardNumber) : 9999;
    const bn = b.hfCardNumber ? parseInt(b.hfCardNumber) : 9999;
    return an - bn;
  });

  return (
    <div className="animate-fade-in">
      <section className="mb-12">
        <div className="bg-gradient-to-br from-hero-600 to-hero-700 rounded-3xl p-8 md:p-12 text-white shadow-card">
          <h1 className="font-display text-4xl md:text-5xl font-bold mb-3">
            HelloFresh-Rezept pinnen
          </h1>
          <p className="text-hero-100 mb-6 text-lg max-w-2xl">
            Paste eine HelloFresh-URL — der Worker scrapet die Karte, adaptiert sie auf native Thermomix-Style mit Koch-Befehl-Chips und publisht sie auf Cookidoo.
          </p>
          <PinForm />
        </div>
      </section>

      <div className="mb-3 flex justify-end">
        <Link href="/pinned" className="text-sm text-charcoal-600 hover:text-hero-700 transition">
          Queue ansehen →
        </Link>
      </div>

      <RecipeGrid recipes={recipes} />
    </div>
  );
}
