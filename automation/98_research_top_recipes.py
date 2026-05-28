"""Research helper: browse Cookidoo (logged-in profile) and dump the per-step
structure of popular native recipes, to refresh research/native-step-corpus.md.

Collects recipe links from a few popular/collection pages, visits up to N recipe
detail pages, and writes title + ordered step list (with char counts) to a
markdown file. Read-only — never edits anything.

Usage: THERMOMIX_HEADLESS=1 python3 automation/98_research_top_recipes.py [N]
"""
import os, re, sys, json, pathlib
from playwright.sync_api import sync_playwright

USER_DATA = str(pathlib.Path.home() / "thermomix-automation/profile")
OUT = pathlib.Path(__file__).resolve().parent.parent / "research" / "native-top-recipes-2026-05-29.md"
N = int(sys.argv[1]) if len(sys.argv) > 1 else 12

SEED_PAGES = [
    "https://cookidoo.de/foundation/de-DE",
    "https://cookidoo.de/search/de-DE?context=recipes&sort=relevance",
    "https://cookidoo.de/search/de-DE?context=recipes",
]
RECIPE_HREF = re.compile(r"/recipes/recipe/[a-z]{2}-[A-Z]{2}/r\d+")


def accept_cookies(page):
    try: page.locator("#onetrust-accept-btn-handler").first.click(timeout=2500)
    except Exception: pass


def collect_links(page):
    hrefs = page.eval_on_selector_all(
        "a[href]", "els => els.map(e => e.getAttribute('href'))")
    out = []
    for h in hrefs or []:
        if h and RECIPE_HREF.search(h):
            full = h if h.startswith("http") else "https://cookidoo.de" + h
            out.append(full.split("?")[0])
    return out


def dump_recipe(page, url):
    page.goto(url, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(1800)
    try:
        title = page.locator("h1").first.inner_text(timeout=4000).strip()
    except Exception:
        title = "(kein Titel)"
    steps = []
    for sel in ["ol.recipe-content__ordered-list > li",
                ".recipe-content__ordered-list > li",
                "ol[class*='ordered-list'] > li",
                "[class*='preparation'] li"]:
        loc = page.locator(sel)
        n = loc.count()
        if n:
            for i in range(n):
                try:
                    txt = re.sub(r"\s+", " ", loc.nth(i).inner_text()).strip()
                    if txt:
                        steps.append(txt)
                except Exception:
                    pass
            if steps:
                break
    rid = re.search(r"/(r\d+)", url)
    return {"title": title, "id": rid.group(1) if rid else url, "url": url, "steps": steps}


def main():
    results, seen = [], set()
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            USER_DATA, headless=os.environ.get("THERMOMIX_HEADLESS", "0") == "1",
            viewport={"width": 1400, "height": 1000}, locale="de-DE")
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        links = []
        for sp in SEED_PAGES:
            try:
                page.goto(sp, wait_until="domcontentloaded", timeout=60000)
                accept_cookies(page)
                page.wait_for_timeout(2500)
                for _ in range(4):
                    page.mouse.wheel(0, 4000); page.wait_for_timeout(900)
                found = collect_links(page)
                print(f"{sp} → {len(found)} recipe links")
                for f in found:
                    if f not in seen:
                        seen.add(f); links.append(f)
            except Exception as e:
                print(f"seed fail {sp}: {e}")
            if len(links) >= N * 2:
                break
        print(f"Total unique candidate links: {len(links)}; visiting up to {N}")
        for url in links:
            if len(results) >= N:
                break
            try:
                r = dump_recipe(page, url)
                if len(r["steps"]) >= 2:
                    results.append(r)
                    print(f"  ✓ {r['id']}: {len(r['steps'])} steps — {r['title'][:50]}")
                else:
                    print(f"  – {r['id']}: no steps (gated?) — skip")
            except Exception as e:
                print(f"  ! {url}: {e}")
        ctx.close()

    lines = ["# Native Top-Recipes — fresh dump 2026-05-29",
             "",
             "> Read-only Cookidoo (logged-in) dump via 98_research_top_recipes.py.",
             f"> {len(results)} recipes, per-step char counts for the playbook refresh.",
             ""]
    for r in results:
        lines.append(f"## {r['title']} (`{r['id']}`)")
        lines.append(f"<{r['url']}>")
        lens = [len(s) for s in r["steps"]]
        med = sorted(lens)[len(lens)//2] if lens else 0
        lines.append(f"_{len(r['steps'])} steps · median {med}c · max {max(lens) if lens else 0}c_")
        lines.append("")
        for i, s in enumerate(r["steps"], 1):
            lines.append(f"{i}. ({len(s)}c) {s}")
        lines.append("")
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nWrote {OUT} ({len(results)} recipes)")
    # also emit a compact JSON for downstream analysis
    OUT.with_suffix(".json").write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
