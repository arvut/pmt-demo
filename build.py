#!/usr/bin/env python3
# pmt-demo multilang build (Muster: arvut/tbo-demo):
#   index.src.html (DE-Master, Design Natalia) + Übersetzungen .md → de/ fr/ it/ en/ ru/ + Root-Redirect.
# RU wird gebaut, ist aber im Umschalter versteckt (Reserve).
# Ohne Übersetzungsdatei (~/Downloads/pmt_landing_translations_EN_FR_IT_RU.md): DE-only Build, kein Switcher.
# ⚠️ Master und Build-Output sind getrennte Dateien — index.src.html wird NIE überschrieben.
import re, os

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC  = os.path.join(ROOT, 'index.src.html')
TRANS = os.path.expanduser('~/Downloads/pmt_landing_translations_EN_FR_IT_RU.md')
DE_SOURCE = os.path.expanduser('~/Downloads/pmt_landing_text_DE_SOURCE.md')
LANGS = ['de', 'fr', 'it', 'en', 'ru']
VISIBLE = ['de', 'fr', 'it', 'en']            # RU versteckt
DEFLANG = 'de'
OWN = ['pmt']  # имена самого лендинга: их комментарий называть вправе

# Общий гейт «внутренние заметки не уезжают клиенту» — GoToMarket/_shared/landing_guard.py.
# Копии нет: модуль ищется вверх по дереву. Нет модуля = сборка падает, а не выкладывается без гейта.
def _load_guard():
    import importlib.util
    d = os.path.dirname(os.path.abspath(__file__))
    while True:
        p = os.path.join(d, "_shared", "landing_guard.py")
        if os.path.isfile(p):
            spec = importlib.util.spec_from_file_location("landing_guard", p)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return mod
        parent = os.path.dirname(d)
        if parent == d:
            raise SystemExit("!! не найден _shared/landing_guard.py — сборка без гейта запрещена")
        d = parent


guard = _load_guard()

MULTILANG = os.path.exists(TRANS)

# ---- parse key-schema .md → {sec.key: text} ----
def parse_md(path, with_lang=False):
    out = {}; lang = None; sec = None
    for line in open(path, encoding='utf-8'):
        if with_lang:
            m = re.match(r'^#\s*=*\s*(EN|FR|IT|RU)\s*=*\s*$', line.rstrip())
            if m: lang = m.group(1); out.setdefault(lang, {}); continue
        if line.startswith('## '):
            ms = re.match(r'^## \[(\w+)\]', line)
            sec = ms.group(1) if ms else None   # «## NICHT übersetzen» etc. → kein Abschnitt
            continue
        mk = re.match(r'^- (\w+):\s?(.*)$', line.rstrip('\n'))
        if mk and sec:
            tgt = out[lang] if with_lang else out
            if with_lang and lang is None: continue
            tgt[f'{sec}.{mk.group(1)}'] = mk.group(2)
    return out

# ---- Kanon: Leitsatz wörtlich aus der Übersetzungsdatei; span.inv auf die CFO-Phrase ----
# (Kanon-Fassung liegt in T[L]['leitsatz.zitat'] — Strategy liefert sie wörtlich; hier nur Markup.)
CFO_PHRASE = {'en': 'fractional CFO', 'fr': 'directeur financier externe',
              'it': 'CFO esterno',   'ru': 'внешний финансовый директор'}

def leitsatz_html(T, L, lang):
    t = T[L]['leitsatz.zitat']
    ph = CFO_PHRASE[lang]
    if ph not in t:
        print(f'  ⚠️ [{lang}] CFO-Phrase «{ph}» nicht im Leitsatz — span fehlt!')
        return t
    return t.replace(ph, f'<span class="inv">{ph}</span>', 1)

def markup_map(T, L, lang):
    def b_chf(txt, chf):
        return re.sub(re.escape(chf), f'<b style="color:var(--ink);">{chf}</b>', txt, count=1)
    return {
      # vergleich h2 (<br>)
      'Ihre Zahlen nur einmal im Jahr?<br>Das gehört der Vergangenheit an.': T[L]['vergleich.h2'],
      # col1_li2 (<b>&nbsp;</b>)
      "Vollkosten pro Mitarbeitenden — ab <b style=\"color:var(--ink);\">CHF&nbsp;110'000</b> pro Jahr":
        re.sub(r"CHF 110'000", "<b style=\"color:var(--ink);\">CHF&nbsp;110'000</b>", T[L]['vergleich.col1_li2']),
      # leitsatz (Kanon seit 08.07: «— und nicht nur für kleine Unternehmen»; span.inv)
      'Der klassische Treuhänder ist der geteilte Buchhalter der KMU. Der Treuhänder im Arvut-Netzwerk ist zusätzlich ihr <span class="inv">externer CFO</span> — und nicht nur für kleine Unternehmen.':
        leitsatz_html(T, L, lang),
      # preise lead (<b>CHF 110'000</b>)
      "Eine eigene Buchhaltung ist nicht nur der Lohn. Mit Sozialabgaben und Arbeitsplatz kostet ein Buchhalter in Zürich über <b style=\"color:var(--ink);\">CHF 110'000</b> pro Jahr, ein Team mehrere Hunderttausend. Mit P&M erhalten Sie mehr — und zahlen deutlich weniger.":
        b_chf(T[L]['preise.lead'], "CHF 110'000"),
      # preise fussnote (<b>pilot</b> + <a>link</a>)
      "Der genaue Preis wird nach einer kurzen Analyse festgelegt — er hängt vom Buchungsvolumen und der Anzahl Gesellschaften ab. Der Einstieg ist über eine dreimonatige Pilotphase zu <b style=\"color:var(--ink);\">CHF 1'000 pro Mandat</b> möglich (bei Fortsetzung anrechenbar). <a href=\"#kontakt\" class=\"link-u\">Offerte anfordern</a>.":
        fussnote_html(T, L),
      # banner h2 (<br>)
      'Konzentrieren Sie sich auf Ihr Geschäft.<br>Die Zahlen sind unsere Sache.': T[L]['banner.h2'],
      # team footer (<b>lead:</b> rest)
      '<b style="color:var(--ink);">Kurze Wege, klare Antworten:</b> Besprechungen in Zürich — persönlich oder online, auf Deutsch und Englisch.':
        team_footer_html(T, L),
      # footer tech desc (<br>)
      'Automatisierung und Buchhaltungsplattform.<br>Daten in der Schweiz gehostet.': T[L]['footer.tech_beschreibung'],
    }

def fussnote_html(T, L):
    t = T[L]['preise.fussnote']
    cta = T[L]['header.cta_header']
    t = re.sub(r"(CHF 1'000 [^.(]+?)( \()", r'<b style="color:var(--ink);">\1</b>\2', t, count=1)
    t = re.sub(r'\s*\[[^\]]*\]\s*\.?\s*$', '', t).rstrip('. ').rstrip()
    return f'{t}. <a href="#kontakt" class="link-u">{cta}</a>.'

def team_footer_html(T, L):
    t = T[L]['team.footer']
    m = re.match(r'^([^:]+:)\s*(.*)$', t)
    if m: return f'<b style="color:var(--ink);">{m.group(1)}</b> {m.group(2)}'
    return t

MARKUP_KEYS = {'vergleich.h2','vergleich.col1_li2','leitsatz.zitat','preise.lead','preise.fussnote',
 'banner.h2','team.footer','footer.tech_beschreibung','meta.title','meta.meta_description'}

SWITCH_CSS = ('.lang-switch{display:flex;align-items:center;gap:10px;margin-left:6px;}'
  '.lang-switch a.lang{font-family:\'Inconsolata\',monospace;font-size:12px;font-weight:700;'
  'letter-spacing:.1em;text-transform:uppercase;color:var(--muted);}'
  '.lang-switch a.lang:hover{color:var(--ink);}'
  '.lang-switch a.lang.on{color:var(--ink);border-bottom:2px solid var(--ink);}\n</style>')
HEADER_CTA_DE = '    <a href="#kontakt" class="btn btn-out" style="padding:11px 22px;font-size:.82rem;">Offerte anfordern</a>'

def build_lang(lang, T, DE):
    src = open(SRC, encoding='utf-8').read()
    L = lang.upper()
    src = src.replace('src="assets/', 'src="../assets/')
    src = src.replace("@import url('assets/", "@import url('../assets/")

    if MULTILANG:
        src = src.replace('\n</style>', '\n' + SWITCH_CSS, 1)
        links = ''.join(f'<a href="../{lc}/" class="lang{" on" if lc==lang else ""}">{lc.upper()}</a>' for lc in VISIBLE)
        cta = 'Offerte anfordern' if lang == 'de' else T[L]['header.cta_header']
        src = src.replace(HEADER_CTA_DE,
          f'    <span class="lang-switch">{links}</span>\n'
          f'    <a href="#kontakt" class="btn btn-out" style="padding:11px 22px;font-size:.82rem;">{cta}</a>', 1)

    if lang == 'de':
        return finalize(src, 'de')

    for de_frag, tgt in markup_map(T, L, lang).items():
        if de_frag not in src:
            print(f'  ⚠️ [{lang}] markup fragment NOT found: {de_frag[:55]}...')
        src = src.replace(de_frag, tgt)

    src = src.replace('P&M CFO Treuhand — Ihr externer CFO und Buchhaltung in Echtzeit, Zürich', T[L]['meta.title'])
    src = src.replace(DE['meta.meta_description'], T[L]['meta.meta_description'])

    # NICHT übersetzen: Paketnamen maskieren — Kollisionsschutz vor kurzen Keys («Partner» → Finance Partner).
    # Maske auch auf Such-Key und Übersetzung anwenden, sonst matchen Keys mit Paketnamen nicht mehr.
    PROTECT = ['Real-Time Books', 'Finance Partner', 'Virtual CFO']
    def mask(t):
        for i, p in enumerate(PROTECT): t = t.replace(p, f'\x00P{i}\x00')
        return t
    src = mask(src)
    items = [(k, mask(DE[k]), mask(T[L].get(k))) for k in DE
             if k not in MARKUP_KEYS and DE[k] and T[L].get(k) and not DE[k].startswith('[')]
    items.sort(key=lambda x: len(x[1]), reverse=True)
    for k, de_t, tg in items:
        if de_t == tg: continue
        if de_t in src: src = src.replace(de_t, tg)
        elif f'>{de_t}<' in src: src = src.replace(f'>{de_t}<', f'>{tg}<')
        elif f'>{de_t}</a>' in src: src = src.replace(f'>{de_t}</a>', f'>{tg}</a>')
        elif tg in src: pass   # bereits durch gleichlautenden Key ersetzt (z.B. CTA ×3)
        else: print(f'  ⚠️ [{lang}] clean text not found: {k} = {de_t[:45]}')
    for i, p in enumerate(PROTECT): src = src.replace(f'\x00P{i}\x00', p)
    return finalize(src, lang)

def finalize(src, lang):
    return re.sub(r'<html lang="de">', f'<html lang="{lang}">', src, count=1)

def tag_count(s):
    return {t: len(re.findall(f'<{t}\\b', s)) for t in ['a','section','svg','img','h1','h2','h3','form','input']}

# ---- build ----
T = parse_md(TRANS, with_lang=True) if MULTILANG else {}
DE = parse_md(DE_SOURCE) if os.path.exists(DE_SOURCE) else {}
langs = LANGS if MULTILANG else ['de']
built = {lang: build_lang(lang, T, DE) for lang in langs}

if MULTILANG:
    base = tag_count(built['de'])
    print('Tag parity (vs DE):')
    for lang in langs:
        c = tag_count(built[lang])
        print(f'  {lang}: {"✓" if c == base else "✗ " + str({k: (base[k], c[k]) for k in base if base[k] != c[k]})}')

for lang in langs:
    d = os.path.join(ROOT, lang); os.makedirs(d, exist_ok=True)
    page = guard.strip_internal_comments(built[lang])   # заметки остаются в index.src.html
    if lang in VISIBLE:                                 # /ru/ — скрытая версия, кириллица там штатна
        guard.assert_no_internal_notes(page, lang)
        guard.assert_no_foreign_partner(page, lang, own=OWN)
    open(os.path.join(d, 'index.html'), 'w', encoding='utf-8').write(page)

redirect = ('<!doctype html><html lang="de"><head><meta charset="utf-8">'
  '<meta name="robots" content="noindex,nofollow">'
  f'<link rel="canonical" href="{DEFLANG}/"><meta http-equiv="refresh" content="0; url={DEFLANG}/">'
  f'<script>location.replace("{DEFLANG}/"+location.hash)</script>'
  '<title>P&M CFO Treuhand AG</title></head>'
  '<style>@media(max-width:900px){section,header,footer,main{overflow-x:clip}}'
  '@media(max-width:560px){*{min-width:0}body{overflow-wrap:break-word;hyphens:auto}'
  'h1,h2{hyphens:manual}.g2{grid-template-columns:minmax(0,1fr)!important}.wrap{flex-wrap:wrap}'
  'header .wrap{height:auto!important;min-height:0}nav,.menu{flex-wrap:wrap}}</style>'
  f'<body style="font-family:sans-serif;padding:2rem">Weiter zu <a href="{DEFLANG}/">P&M CFO Treuhand</a>…</body></html>')
redirect = guard.guard(redirect, 'index.html (Root-Redirect)', own=OWN)
open(os.path.join(ROOT, 'index.html'), 'w', encoding='utf-8').write(redirect)

print(f'✓ Build: {" ".join(langs)}/ + Root-Redirect → /{DEFLANG}/' + ('' if MULTILANG else '  (DE-only: Übersetzungsdatei fehlt)'))
