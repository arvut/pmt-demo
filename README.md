# P&M CFO Treuhand — Demo-Landingpage

Landingpage-Entwurf (DE) für P&M CFO Treuhand AG, Zürich.
Live: **https://pmt.arvut.ch**

Design-Referenz: qontrarian.com (Monochrom-Minimalismus, Montserrat + Inconsolata, Creme/Ink).

## Struktur

- `index.src.html` — **DE-Master (Quelle der Wahrheit).** Hier Design und Inhalt bearbeiten.
- `de/` — generierte Sprachversion (NICHT von Hand bearbeiten, wird überschrieben).
- `index.html` — Root-Weiterleitung auf `de/`.
- `assets/` — Logo, Fotos, Schriften (lokal, self-contained; relativ `../assets/`).
- `build.py` — erzeugt `de/` + Redirect aus dem Master.

## Bearbeiten & neu bauen

1. Design/Text am DE-Master `index.src.html` ändern.
2. `python3 build.py` ausführen.
3. Commit + Push.

Weitere Sprachen (FR/IT/EN + verstecktes RU): Schlüsselschema und Build-Muster wie
im Repo `arvut/tbo-demo` — Textextrakt liegt als `pmt_landing_text_DE_SOURCE.md` vor,
Übersetzungen werden nach demselben Schema integriert.
