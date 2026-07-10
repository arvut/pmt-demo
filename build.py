#!/usr/bin/env python3
# pmt-demo build: index.src.html (DE-Master) → de/ + Root-Redirect.
# DE-only Entwurfsphase. Mehrsprachig (fr/it/en + verstecktes ru) wird nach dem
# Übersetzungs-Schritt ergänzt — Muster: arvut/tbo-demo build.py (gleiches Schlüsselschema,
# Übersetzungs-.md von Arvut Strategy, Markup-Fragmente explizit im Build).
# ⚠️ Master und Build-Output sind getrennte Dateien — index.src.html wird NIE überschrieben.
import os, re

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC  = os.path.join(ROOT, 'index.src.html')
LANGS = ['de']            # + 'fr','it','en','ru' nach Übersetzung (ru versteckt)
DEFLANG = 'de'

def build_lang(lang):
    src = open(SRC, encoding='utf-8').read()
    # relative Assets für Sprach-Unterordner (funktioniert auf Domain-Root UND GitHub Pages)
    src = src.replace('src="assets/', 'src="../assets/')
    src = src.replace("@import url('assets/", "@import url('../assets/")
    src = re.sub(r'<html lang="de">', f'<html lang="{lang}">', src, count=1)
    return src

for lang in LANGS:
    d = os.path.join(ROOT, lang); os.makedirs(d, exist_ok=True)
    open(os.path.join(d, 'index.html'), 'w', encoding='utf-8').write(build_lang(lang))

redirect = ('<!doctype html><html lang="de"><head><meta charset="utf-8">'
  '<meta name="robots" content="noindex,nofollow">'
  f'<link rel="canonical" href="{DEFLANG}/"><meta http-equiv="refresh" content="0; url={DEFLANG}/">'
  f'<script>location.replace("{DEFLANG}/"+location.hash)</script>'
  '<title>P&M CFO Treuhand AG</title></head>'
  f'<body style="font-family:sans-serif;padding:2rem">Weiter zu <a href="{DEFLANG}/">P&M CFO Treuhand</a>…</body></html>')
open(os.path.join(ROOT, 'index.html'), 'w', encoding='utf-8').write(redirect)
print(f'✓ Build: {" ".join(LANGS)}/ + Root-Redirect → /{DEFLANG}/')
