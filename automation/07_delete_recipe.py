"""Delete a Cookidoo "Eigenes Rezept" — safely, by recipe ID, with a title guard.

Why this exists: not every recipe belongs in the catalog. If a HelloFresh dish turns
out to be a pure pan/handwork recipe (no real Thermomix operation), converting it
produces a confusing recipe — see PLAYBOOK.md "0. Pre-Check (GATE)". This is the
clean way to remove such a recipe again.

Usage:
    python3 automation/07_delete_recipe.py <RECIPE_ID> --expect "<title substring>" --yes

Safety:
    * RECIPE_ID is required as an explicit arg (no silent fallback to current_recipe.txt).
    * --expect "<substr>" : fetches the recipe first and aborts unless its name contains
      <substr> (case-insensitive). Strongly recommended so you never delete the wrong one.
    * --yes : without it, the script only previews (GET + would-delete), never deletes.
    * After DELETE it re-fetches and confirms the resource is gone (non-200).

The same-origin fetch runs inside the logged-in persistent profile, so auth/CSRF are
handled by the browser context (same mechanism as 06_publish.py's PATCH).
"""
import os
import sys
import pathlib
from playwright.sync_api import sync_playwright

USER_DATA = str(pathlib.Path.home() / "thermomix-automation/profile")
BASE = "https://cookidoo.de/created-recipes/de-DE"


def main():
    args = sys.argv[1:]
    if not args or args[0].startswith("-"):
        sys.exit("Usage: python3 automation/07_delete_recipe.py <RECIPE_ID> "
                 "--expect \"<title substring>\" --yes")
    recipe_id = args[0]
    do_delete = "--yes" in args
    expect = None
    if "--expect" in args:
        i = args.index("--expect")
        if i + 1 < len(args):
            expect = args[i + 1]

    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            USER_DATA, headless=os.environ.get("THERMOMIX_HEADLESS", "0") == "1",
            viewport={"width": 1400, "height": 900}, locale="de-DE",
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.goto(f"{BASE}/{recipe_id}", wait_until="domcontentloaded", timeout=60000)
        try:
            page.locator("#onetrust-accept-btn-handler").first.click(timeout=2000)
        except Exception:
            pass
        page.wait_for_timeout(2000)

        # 1) Fetch the recipe to read its name (title guard).
        got = page.evaluate(f"""async () => {{
            const r = await fetch('{BASE}/{recipe_id}', {{
                headers: {{'Accept': 'application/json'}}
            }});
            let name = null;
            try {{ const j = await r.clone().json(); name = (j.recipeContent && j.recipeContent.name) || j.name || j.title || null; }} catch (e) {{}}
            return {{status: r.status, name, body: (await r.text()).slice(0, 600)}};
        }}""")
        print(f"GET {recipe_id} → status {got['status']}, name={got['name']!r}")
        if got["status"] != 200:
            print("Recipe not reachable (maybe already deleted). Body:", got["body"])
            ctx.close()
            return

        if expect:
            name = (got["name"] or "")
            if expect.lower() not in name.lower():
                ctx.close()
                sys.exit(f"ABORT: --expect {expect!r} not found in recipe name {name!r}. "
                         f"Refusing to delete the wrong recipe.")
            print(f"Title guard OK: {expect!r} ⊂ {name!r}")
        else:
            print("WARNING: no --expect guard given.")

        if not do_delete:
            print("Preview only (no --yes). Would DELETE this recipe. Re-run with --yes to delete.")
            ctx.close()
            return

        # 2) Delete.
        res = page.evaluate(f"""async () => {{
            const r = await fetch('{BASE}/{recipe_id}', {{
                method: 'DELETE',
                headers: {{'Accept': 'application/json'}}
            }});
            return {{status: r.status, body: (await r.text()).slice(0, 600)}};
        }}""")
        print(f"DELETE status: {res['status']}")
        if res["status"] not in (200, 202, 204):
            print("Response body:", res["body"])

        # 3) Verify it is gone.
        page.wait_for_timeout(1500)
        check = page.evaluate(f"""async () => {{
            const r = await fetch('{BASE}/{recipe_id}', {{headers: {{'Accept': 'application/json'}}}});
            return r.status;
        }}""")
        print(f"Verify GET after delete → status {check} ({'gone ✅' if check != 200 else 'STILL PRESENT ⚠️'})")
        ctx.close()


if __name__ == "__main__":
    main()
