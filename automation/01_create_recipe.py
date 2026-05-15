"""Create a new Cookidoo Eigenes Rezept and fill in ingredients + plain-text steps.

EDIT THE THREE CONSTANTS at the top, then run.

After completion, the new recipe ID is stored in ~/cookidoo-automation/current_recipe.txt
for the rest of the pipeline (02_upload_image.py, 03_add_tips.py, 04_set_times.py,
05_annotate_chips.py).

CRITICAL CONSISTENCY RULES (learned from the first recipe iteration):
1. Each ingredient must appear at most 1x per step. The AI annotator marks the second
   occurrence as 'overuse' and the rendered chips look duplicated/messy.
   Bad:  '...unter kaltem Wasser spülen. 1200 g Wasser ...'   → 2x Wasser in same step
   Good: '...kurz abspülen. 1200 g Wasser ...'                → 1x Wasser
2. Avoid compound names that contain another ingredient as substring within the same step.
   Bad:  '50 g Sriracha-Sauce zu Sriracha-Mayo verrühren'     → 'Sriracha' matched twice
   Good: '50 g Sriracha-Sauce mit Mayo verrühren'             → 1x Sriracha-Sauce
3. Don't list a generic Salz amount AND a catch-all 'Salz, Pfeffer, Zucker, Öl nach Bedarf'
   in the ingredient list — pick one.

NATIVE-STYLE INSIGHTS (learned from deep-research of 12 Vorwerk recipes for Bowls/Currys):
- Native recipes for 14-17 ingredients have a MEDIAN of 5 steps (range 4-7), not 8.
- Group preparation + parallel tasks into a single 'In der Zwischenzeit ...' step.
- Use native verbs: 'einwiegen', 'mithilfe des Spatels herausnehmen', 'aufsetzen',
  'absetzen', 'einhängen', 'auf 4 Bowls verteilen', '... servieren'.
- Ingredient lines: shorter is better. '1 Limette, gewachst' (not '1 Limette, gewachst,
  in 6 Spalten geschnitten' — the verb belongs in the step text).
- Specify exact amounts ('2 TL Salz', '25 g Öl', '1-2 Prisen Pfeffer', '1 Prise Zucker')
  instead of a catch-all 'nach Bedarf' line — native recipes always do the former.
"""
import pathlib
from playwright.sync_api import sync_playwright

# === EDIT THESE ===
RECIPE_NAME = "Sweet-Chili-Bowl mit glasierter Aubergine (HelloFresh #33)"

INGREDIENTS = [
    "300 g Basmatireis",
    "2 Auberginen",
    "200 g Buschbohnen",
    "2 Gurken",
    "2 Frühlingszwiebeln",
    "1 rote Chilischote, frisch",
    "100 g Teriyakisoße",
    "20 ml Sesamöl",
    "16 ml Sriracha-Sauce",
    "100 g Sweet-Chili-Soße",
    "1 Limette, gewachst",
    "50 g vegane Mayonnaise",
    "1200 g Wasser",
    "2 TL Salz",
    "25 g Öl",
    "1-2 Prisen Pfeffer",
    "1 Prise Zucker",
]

# 5 native-style steps (median for 14-17-ingredient native recipes).
# Cooking commands embedded as plain text in the format the AI annotator recognizes:
#   "18 Min./Varoma/Stufe 1"  or  "6 Min./100 °C/Linkslauf/Stufe 1"
# Script 05_annotate_chips.py converts them to interactive chips.
#
# Per-step uniqueness + cross-step adjacent endings already validated.
STEPS = [
    # 1 — Vorbereitung (Limette, Aubergine, Buschbohnen, Ofen)
    "Limette in 6 Spalten schneiden. Aubergine längs vierteln und in ca. 2 cm Stücke schneiden, in einer großen Schüssel mit der Hälfte der Teriyakisoße, Saft von 2 Limettenspalten, 1 TL Salz und 2 EL Öl marinieren und auf einem mit Backpapier belegten Backblech verteilen. Enden der Buschbohnen entfernen und dritteln, in den Varoma-Behälter geben und verschließen. Backofen auf 220 °C Ober-/Unterhitze (200 °C Umluft) vorheizen.",
    # 2 — Reis dampfgaren + Aubergine backen
    "Gareinsatz einhängen, Basmatireis einwiegen und kurz abspülen. Gareinsatz einsetzen. 1200 g Wasser, 1,5 TL Salz und 5 g Öl in den Mixtopf geben, Varoma aufsetzen und 18 Min./Varoma/Stufe 1 dampfgaren. Aubergine in den vorgeheizten Ofen geben und 15–20 Min. backen, bis sie innen weich und außen schön gebräunt ist.",
    # 3 — Toppings + Gurkensalat (parallel zum Dampfgaren)
    "In der Zwischenzeit Chili (Achtung: scharf!) und Frühlingszwiebeln in feine Ringe schneiden. In einer kleinen Schüssel 50 g vegane Mayonnaise, 16 g Sriracha-Sauce und Saft von 2 Limettenspalten verrühren. In einer zweiten Schüssel 100 g Sweet-Chili-Soße mit dem Saft von 4 weiteren Spalten vermengen. Gurke in dünne Scheiben (2 mm) hobeln und in der Marinade-Schüssel aus Schritt 1 mit 2 EL aus der zweiten Schüssel, Saft von 2 Limettenspalten und 1 Prise Zucker marinieren. Beide Soßen und Gurkensalat mit Salz und Pfeffer abschmecken.",
    # 4 — Bohnen vollenden + Reis fertig
    "Varoma absetzen. Gareinsatz mithilfe des Spatels herausnehmen und abgedeckt 6 Min. ruhen lassen. Mixtopf leeren. 20 g Öl, Buschbohnen aus dem Varoma und je 1 Prise Salz und Pfeffer in den Mixtopf geben und 6 Min./100 °C/Linkslauf/Stufe 1 dünsten. Reis mit einer Gabel auflockern und 20 ml Sesamöl unterheben.",
    # 5 — Anrichten
    "Reis und Buschbohnen auf 4 Bowls verteilen. Aubergine nach der Garzeit mit der restlichen Teriyakisoße vermengen und obenauf geben. Gurkensalat daneben anrichten, mit Frühlingszwiebelringen, Chili (Achtung: scharf!) und den Dips garnieren und servieren.",
]
# === END EDIT ===

USER_DATA = str(pathlib.Path.home() / "cookidoo-automation/profile")
STATE_FILE = pathlib.Path.home() / "cookidoo-automation/current_recipe.txt"


def click_first_visible(page, selector):
    for el in page.locator(selector).all():
        try:
            if el.is_visible():
                el.click(); return True
        except Exception:
            pass
    return False


def main():
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            USER_DATA, headless=False,
            viewport={"width": 1500, "height": 950}, locale="de-DE",
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.goto("https://cookidoo.de/created-recipes/de-DE", wait_until="domcontentloaded", timeout=60000)
        try: page.locator("#onetrust-accept-btn-handler").first.click(timeout=2000)
        except Exception: pass
        page.wait_for_timeout(2000)

        # Open create-modal
        page.locator("button:has-text('Rezept erstellen')").first.click()
        page.wait_for_timeout(1200)

        # Fill recipe name and confirm via the modal's "Erstellen" button (exact match)
        page.fill("#recipe-title", RECIPE_NAME)
        page.wait_for_timeout(400)
        for b in page.locator("button:has-text('Erstellen')").all():
            try:
                if b.is_visible() and b.inner_text().strip() == "Erstellen":
                    b.click(); break
            except Exception: pass

        page.wait_for_load_state("networkidle", timeout=30000)
        page.wait_for_timeout(2000)
        recipe_id = page.url.rstrip("/").split("/")[-2]
        print(f"Created recipe: {recipe_id}")
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        STATE_FILE.write_text(recipe_id)

        page.goto(f"https://cookidoo.de/created-recipes/de-DE/{recipe_id}/edit/ingredients-and-preparation-steps?active=steps",
                  wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(2000)

        for sel in ["#add-ingredients", "button:has-text('Erste Zutat hinzufügen')"]:
            if click_first_visible(page, sel): break
        page.wait_for_timeout(500)

        print(f"Adding {len(INGREDIENTS)} ingredients...")
        for i, ing in enumerate(INGREDIENTS):
            print(f"  [{i+1}/{len(INGREDIENTS)}] {ing}")
            page.wait_for_selector("cr-manage-ingredients cr-text-field[contenteditable='true']", timeout=10000)
            fields = page.locator("cr-manage-ingredients cr-text-field[contenteditable='true']")
            target = None
            for j in range(fields.count()-1, -1, -1):
                try:
                    if fields.nth(j).is_visible(): target = fields.nth(j); break
                except Exception: pass
            if not target: continue
            target.click(); page.wait_for_timeout(150)
            page.keyboard.type(ing, delay=2); page.wait_for_timeout(100)
            page.keyboard.press("Enter"); page.wait_for_timeout(250)

        for sel in ["#add-steps", "button:has-text('Ersten Rezeptschritt hinzufügen')"]:
            if click_first_visible(page, sel): break
        page.wait_for_timeout(500)

        print(f"\nAdding {len(STEPS)} steps...")
        for i, step in enumerate(STEPS):
            print(f"  [{i+1}/{len(STEPS)}] {step[:60]}...")
            page.wait_for_selector("cr-manage-steps cr-text-field[contenteditable='true']", timeout=10000)
            fields = page.locator("cr-manage-steps cr-text-field[contenteditable='true']")
            target = None
            for j in range(fields.count()-1, -1, -1):
                try:
                    if fields.nth(j).is_visible(): target = fields.nth(j); break
                except Exception: pass
            if not target: continue
            target.click(); page.wait_for_timeout(150)
            page.keyboard.type(step, delay=1); page.wait_for_timeout(150)
            page.keyboard.press("Enter"); page.wait_for_timeout(300)

        page.wait_for_timeout(800)
        for a in page.locator("a:has-text('Bestätigen')").all():
            try:
                if a.is_visible(): a.click(); break
            except Exception: pass
        page.wait_for_load_state("networkidle", timeout=20000)
        page.wait_for_timeout(2000)
        print(f"\nDone. Recipe URL: https://cookidoo.de/created-recipes/de-DE/{recipe_id}")
        ctx.close()


if __name__ == "__main__":
    main()
