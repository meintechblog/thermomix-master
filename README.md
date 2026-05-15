# Cookidoo Master

**Aus beliebigen Rezepten (HelloFresh-Karte, Kochbuch, Webseite) native-quality Cookidoo „Eigene Rezepte" machen — mit interaktiven Koch-Befehl-Chips, die der Thermomix automatisch abspielt.**

---

## Warum dieses Repo existiert

HelloFresh schickt jede Woche eine Box mit grandiosen Rezept-Kreationen. Auf manchen Karten steht hinten klein: **„Thermomix-Variante"**. Das klingt erst mal toll — aber in der Praxis ist diese „Variante" nichts weiter als der gleiche Fließtext mit ein paar zusätzlichen Hinweisen wie _„Wasser dazu, kochen"_. Es gibt:

- ❌ keine geführte Bedienung
- ❌ keine Chips für Zeit/Temperatur/Stufe
- ❌ keinen Start aus Cookidoo
- ❌ keine Verknüpfung mit dem Gerät

Wer eine echte Thermomix-Bedienung will, muss die Karte selbst am Display abtippen — Zutat für Zutat, Schritt für Schritt, jeden Koch-Befehl per Hand auswählen. Das ist genau das, was der Thermomix _eigentlich_ überflüssig machen sollte.

**Dieses Repo schließt die Lücke.** Es konvertiert beliebige Rezepte vollautomatisch in **native-quality Cookidoo-Eigene-Rezepte** — mit allem was ein originales Vorwerk-Rezept hat: strukturierte Zutaten, schrittweise Anleitung im Thermomix-Wording (`einwiegen`, `einhängen`, `aufsetzen`, `dampfgaren`) und vor allem **interaktive Koch-Befehl-Chips**, die der Thermomix beim Antippen direkt ausführt (`18 Min./Varoma/Stufe 1`, `6 Min./100 °C/Linkslauf/Stufe 1`).

## Die technische Entdeckung

Cookidoo hat eine **undokumentierte AI-Annotate-API** unter `POST /created-recipes/de-DE/annotate/steps`. Sie nimmt Plain-Text-Schritte entgegen und liefert eine strukturierte Token-Liste zurück: jede Zutaten-Mention wird zur `INGREDIENT`-Annotation, jeder Koch-Befehl zur `TTS`-Annotation. Wer diese API direkt anspricht (statt durch das versteckte 5-7-Klick-Modal pro Befehl zu navigieren), bekommt für seine Eigenen Rezepte **die gleiche Guided-Cooking-Erfahrung wie bei nativen Vorwerk-Rezepten**.

Komplettes Reverse-Engineering — DOM, Custom-Elements, Bundle-Strings, Save-Quirks — siehe [LEARNINGS.md](LEARNINGS.md).

## Status

✅ **Voll funktional + erstes Rezept öffentlich auf Cookidoo:**

- Rezept: [Sweet-Chili-Bowl mit glasierter Aubergine](recipes/sweet-chili-bowl/) — **5 native Steps**, **17 strukturierte Zutaten**, **2 interaktive Koch-Befehl-Chips**, alle Zutaten-Mentions als Chips verlinkt, Tipps + Quellen-Narrativ
- **Live auf Cookidoo (öffentlich, ohne Login einsehbar):** https://cookidoo.de/created-recipes/public/recipes/de-DE/01KRNNR72NTN1C0PTD67PA8W7D
- **Original HelloFresh-Karte:** https://www.hellofresh.de/recipes/sweet-chili-bowl-mit-glasierter-aubergine-thermomix-695b7cae2a2e2effad1837dd

### Beweis: native-quality Chips im Rezept

![Step 2 mit Varoma-Chip](docs/assets/zoom-step2-varoma-chip.png)

![Step 4 mit Linkslauf-Chip](docs/assets/zoom-step4-linkslauf-chip.png)

> _`18 Min./Varoma/Stufe 1` und `6 Min./100 °C/Linkslauf/Stufe 1` sind keine Plain-Text-Strings — der Thermomix erkennt sie als ausführbare Koch-Befehle und führt sie beim Antippen direkt aus._

## Quick Start

Voraussetzungen einmalig:

```bash
brew install python3
pip3 install playwright
playwright install chromium

git clone https://github.com/meintechblog/cookidoo-master.git
cd cookidoo-master
python3 automation/00_setup_profile.py
# Im Browser bei cookidoo.de einloggen, Cookie-Banner akzeptieren, Fenster schließen.
# Login persistiert in ~/cookidoo-automation/profile/ — danach nie wieder nötig.
```

Pro neuem Rezept:

```bash
# 1. Quellmaterial bereitlegen (eigenes Foto + slug-Verzeichnis)
mkdir -p recipes/{slug}
cp ~/eigenes-foto.jpg recipes/{slug}/hero.jpg

# 2. INGREDIENTS + STEPS in automation/01_create_recipe.py editieren
#    (Faustregel: 5 Steps bei 14-17 Zutaten — siehe PLAYBOOK.md Regel 8)

# 3. Pipeline durchlaufen (~2 Min. End-to-End):
python3 automation/01_create_recipe.py     # Anlage + Zutaten + Plain-Text-Steps
python3 automation/02_upload_image.py recipes/{slug}/hero.jpg   # Hero-Bild
python3 automation/03_add_tips.py          # Tipps (em-dash-Bullets + Quellen)
python3 automation/04_set_times.py         # Arbeitszeit + Gesamtzeit
python3 automation/05_annotate_chips.py    # 🪄 AI-Annotate → echte Chips
# Optional, nur mit EIGENEM Foto:
python3 automation/06_publish.py           # workStatus PUBLIC + Sharing-URL
```

Details + die 9 nicht-offensichtlichen Qualitätsregeln (per-step Uniqueness, Compound-Namen, Native-Verb-Vokabular, ...): siehe [PLAYBOOK.md](PLAYBOOK.md).

## Repo Layout

```
cookidoo-master/
├── README.md             ← du bist hier — Why + Quick Start
├── PLAYBOOK.md           ← Schritt-für-Schritt pro neuem Rezept + die 9 Qualitätsregeln
├── LEARNINGS.md          ← Reverse-Engineering: APIs, DOM, Custom-Elements, Edge-Cases
├── automation/           ← 7 Pipeline-Scripts (00_setup_profile → 06_publish) + 1 Helper (99_replace_steps_helper)
├── research/             ← Deep-Research aus 12 nativen Vorwerk-Rezepten (Step-Median, Verben)
├── recipes/              ← Pro Rezept: Quellfoto, Markdown, Cookidoo-Link, Tipps-Narrativ
│   └── sweet-chili-bowl/ ← Das canonical example
└── docs/assets/          ← Screenshots fürs README
```

## Lizenz & Disclaimer

- **Code**: MIT
- **Rezeptbilder & -inhalte**: Original-Copyright bei HelloFresh / dem jeweiligen Rechteinhaber. Dieses Repo zeigt nur den technischen Workflow. Wer ein Rezept via diesem Toolset auf Cookidoo veröffentlichen will, muss **eigene Rechte am Bild haben** oder ein eigenes Foto verwenden. Die `06_publish.py`-Stage verlangt explizit den Toggle `isImageOwnedByUser: true` — das ist eine rechtliche Selbstzusicherung.
- Cookidoo® und Thermomix® sind eingetragene Marken der Vorwerk International AG & Co. KmG. Dieses Projekt ist **nicht** mit Vorwerk verbunden und nicht offiziell unterstützt.
- Die `/created-recipes/de-DE/annotate/steps`-API ist undokumentiert und kann sich jederzeit ändern. Use at your own risk.

## Mitmachen

Issues und PRs willkommen. Besonders gefragt:
- **Weitere Rezepte** als `recipes/{slug}/` mit eigenem Foto + Cookidoo-Link
- **Andere Lokale** (`en-US`, `fr-FR`, etc.) — die Annotate-API existiert per-Locale, die Verb-Vokabulare unterscheiden sich
- **Edge-Cases im Annotate-API** — bisher getestet: Bowls, Currys, Pfannen. Backrezepte (Mode-Glyphs für „Teig kneten"), Suppen (lange Garzeiten), Smoothies (kein TTS) stehen aus
