import "./globals.css";
import type { Metadata, Viewport } from "next";
import { SiteHeader } from "@/components/SiteHeader";

export const metadata: Metadata = {
  title: "Thermomix Master — HelloFresh × Cookidoo",
  description: "Sexy Rezept-Browser für HelloFresh-Kreationen als native-quality Cookidoo Eigene Rezepte.",
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="de">
      <body className="min-h-screen bg-cream-50 text-charcoal-800">
        <SiteHeader />
        <main className="max-w-7xl mx-auto px-4 sm:px-6 py-6 sm:py-8">{children}</main>
        <footer className="border-t border-charcoal-100 mt-16 py-8 text-center text-sm text-charcoal-500">
          <div className="max-w-7xl mx-auto px-4 sm:px-6">
            Thermomix Master · <a href="https://github.com/meintechblog/cookidoo-master" className="hover:text-hero-700">Open Source</a> · MIT
          </div>
        </footer>
      </body>
    </html>
  );
}
