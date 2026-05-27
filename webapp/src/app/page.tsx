import Link from "next/link";
import { listRecipes } from "@/lib/recipes";
import { PinSection } from "@/components/PinSection";
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
      <PinSection />

      <div className="mb-3 flex justify-end">
        <Link href="/pinned" className="text-sm text-charcoal-600 hover:text-hero-700 transition">
          Queue ansehen →
        </Link>
      </div>

      <RecipeGrid recipes={recipes} />
    </div>
  );
}
