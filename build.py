#!/usr/bin/env python3
"""Genera il sito statico bilingue (italiano in /, inglese in /en/).

Ogni calcolatore è un file in tools/ (italiano) o tools_en/ (inglese) che inizia con:
<!--
title: titolo della pagina (tag <title>)
h1: titolo visibile
desc: meta description
card: testo breve della scheda in home
icon: emoji
cat: Auto | Casa | Lavoro | Collezionismo | Utilità   (sempre in italiano, anche nei file inglesi)
updated: AAAA-MM-GG
order: numero (ordine nella categoria)
new: si (facoltativo)
alt: slug della pagina corrispondente nell'altra lingua (solo nei file di tools_en/)
-->
seguito dall'HTML del calcolatore e da un <script> facoltativo.
"""
import html, json, re, shutil
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent
SRC, OUT = ROOT / "src", ROOT / "public"
DOMAIN = "https://vuoisaperequantocosta.it"
GA_ID = "G-FKCYXWVBCF"
CAT_KEYS = ["Auto", "Casa", "Lavoro", "Collezionismo", "Utilità"]
CAT_SLUG = {"Auto": "auto", "Casa": "casa", "Lavoro": "lavoro", "Collezionismo": "collezionismo", "Utilità": "utilita"}

FLAG_IT = '<svg width="20" height="14" viewBox="0 0 3 2" aria-hidden="true"><rect width="1" height="2" fill="#009246"/><rect x="1" width="1" height="2" fill="#fff"/><rect x="2" width="1" height="2" fill="#ce2b37"/></svg>'
FLAG_GB = ('<svg width="20" height="14" viewBox="0 0 60 30" aria-hidden="true"><clipPath id="gbc"><path d="M0,0 v30 h60 v-30 z"/></clipPath><g clip-path="url(#gbc)">'
           '<path d="M0,0 v30 h60 v-30 z" fill="#012169"/><path d="M0,0 L60,30 M60,0 L0,30" stroke="#fff" stroke-width="6"/>'
           '<path d="M0,0 L60,30 M60,0 L0,30" stroke="#C8102E" stroke-width="3"/><path d="M30,0 v30 M0,15 h60" stroke="#fff" stroke-width="10"/>'
           '<path d="M30,0 v30 M0,15 h60" stroke="#C8102E" stroke-width="6"/></g></svg>')

L = {
 "it": dict(
    prefix="", tools_dir="tools", html_lang="it", in_lang="it-IT", site="Vuoi sapere quanto costa?",
    logo='Vuoi sapere <b>quanto costa?</b>',
    cats={"Auto": ("Auto", "Bollo, passaggio di proprietà, manutenzione, viaggi e valore dell'usato"),
          "Casa": ("Casa", "Mutuo, prestiti, IMU, bollette di luce e gas, internet"),
          "Lavoro": ("Lavoro", "Stipendio, tredicesima, TFR, IVA e assegno unico"),
          "Collezionismo": ("Collezionismo", "Quanto valgono videogiochi e carte"),
          "Utilità": ("Utilità", "Valore dell'usato e calcoli di tutti i giorni")},
    footer_p="Calcolatori gratuiti e senza registrazione per sapere in pochi secondi quanto costa davvero una spesa. I dati inseriti restano nel tuo browser.",
    footer_b="I risultati sono stime indicative e non sostituiscono il parere di un professionista.",
    privacy="Privacy e cookie", manage_ck="Gestisci cookie", new="Nuovo", home="Home",
    updated="Aggiornato il", related="Altri calcolatori",
    eyebrow="{n} calcolatori gratuiti · aggiornati al 2026",
    h1='Vuoi sapere <em>quanto costa?</em>',
    sub="Il valore di qualsiasi oggetto usato, il tuo stipendio netto, le bollette, il bollo, il mutuo e molto altro. Scoprilo in pochi secondi.",
    search_action="/quanto-vale/", search_ph="Cosa vuoi sapere quanto costa? es. iPhone 13, Fiat Panda, bollo…", search_btn="Cerca", search_aria="Cerca",
    search_note="Scrivi qualsiasi oggetto: ti mostriamo i prezzi dell'usato su Vinted, eBay e Subito, e il calcolatore giusto se c'è.",
    stats='<span><b>Gratis</b> e senza registrazione</span><span><b>Dati aggiornati</b> alle regole 2026</span><span><b>Privacy</b>: i calcoli restano sul tuo dispositivo</span>',
    why=[("⚡", "Risultato immediato", "Il calcolo si aggiorna mentre scrivi, senza pulsanti e senza attese."),
         ("📚", "Spiegato bene", "Ogni calcolatore spiega come si arriva al risultato, in parole semplici."),
         ("🔒", "Nessun dato salvato", "Non chiediamo email e non salviamo quello che inserisci.")],
    news_h="🔔 Ultimi aggiornamenti", news_file="news.json",
    home_title="Vuoi sapere quanto costa? Calcolatori gratuiti per le spese di tutti i giorni",
    home_desc="Calcolatori online gratuiti: stipendio netto 2026, tredicesima, bollo auto, IMU, rata del mutuo, bollette di luce e gas, valore dell'auto usata, IVA, TFR e altro.",
    ck_text='<b>Usiamo i cookie solo per statistiche anonime</b> sulle visite, con Google Analytics, se ci dai il consenso. I calcoli restano sempre sul tuo dispositivo.',
    ck_no="Rifiuta", ck_ok="Accetta",
    emb_sum="🧩 Aggiungi questo calcolatore al tuo sito o blog",
    emb_p="Copia questo codice e incollalo nella tua pagina: il calcolatore apparirà sul tuo sito, gratis e sempre aggiornato.",
    emb_btn="Copia il codice", emb_done="Codice copiato!", emb_credit="Calcolatore offerto da", emb_free="Calcolatore gratuito di",
    nf_title="Pagina non trovata", nf_p="La pagina che cerchi non esiste.", nf_btn="Torna ai calcolatori",
    switch_label="English version", months=["gennaio","febbraio","marzo","aprile","maggio","giugno","luglio","agosto","settembre","ottobre","novembre","dicembre"],
 ),
 "en": dict(
    prefix="/en", tools_dir="tools_en", html_lang="en", in_lang="en", site="Vuoi sapere quanto costa? – Cost calculators for Italy",
    logo='Vuoi sapere <b>quanto costa?</b>',
    cats={"Auto": ("Car", "Car tax, ownership transfer, servicing, fuel and used car value"),
          "Casa": ("Home", "Mortgage, loans, IMU property tax, energy bills and internet"),
          "Lavoro": ("Work", "Net salary, 13th-month pay, severance, VAT and child benefit"),
          "Collezionismo": ("Collectibles", "What your video games and trading cards are worth"),
          "Utilità": ("Tools", "Second-hand value and everyday calculations")},
    footer_p="Free calculators, no sign-up needed, to find out in seconds what things really cost in Italy. Everything you type stays in your browser.",
    footer_b="Results are estimates and do not replace advice from a professional.",
    privacy="Privacy and cookies", manage_ck="Cookie settings", new="New", home="Home",
    updated="Updated on", related="More calculators",
    eyebrow="{n} free calculators · updated for 2026",
    h1='How much does it <em>cost in Italy?</em>',
    sub="Your Italian net salary, car tax, property tax, energy bills, mortgage, the value of anything second-hand and more. In English, in seconds.",
    search_action="/en/what-is-it-worth/", search_ph="What do you want to price? e.g. iPhone 13, Fiat Panda, e-bike…", search_btn="Search", search_aria="Search",
    search_note="Type any item: we show you second-hand prices on Vinted, eBay and Subito, plus the right calculator if there is one.",
    stats='<span><b>Free</b>, no sign-up</span><span><b>Up to date</b> with 2026 Italian rules</span><span><b>Private</b>: calculations stay on your device</span>',
    why=[("⚡", "Instant results", "Results update as you type: no buttons, no waiting."),
         ("📚", "Clearly explained", "Every calculator explains Italian rules in plain English."),
         ("🔒", "No data stored", "We don't ask for your email and we don't save what you type.")],
    news_h="🔔 Latest updates", news_file="news_en.json",
    home_title="Cost calculators for Italy in English: salary, taxes, bills and more",
    home_desc="Free calculators in English for people living in Italy: Italian net salary 2026, 13th-month pay, car tax (bollo), IMU property tax, mortgage, energy bills, used car value and more.",
    ck_text='<b>We only use cookies for anonymous visit statistics</b>, with Google Analytics, if you agree. Your calculations always stay on your device.',
    ck_no="Decline", ck_ok="Accept",
    emb_sum="🧩 Add this calculator to your website or blog",
    emb_p="Copy this code and paste it into your page: the calculator will appear on your site, free and always up to date.",
    emb_btn="Copy the code", emb_done="Code copied!", emb_credit="Calculator by", emb_free="Free calculator by",
    nf_title="Page not found", nf_p="The page you are looking for does not exist.", nf_btn="Back to the calculators",
    switch_label="Versione italiana", months=["January","February","March","April","May","June","July","August","September","October","November","December"],
 ),
}

def fmtdate(iso, lang):
    y, m, d = (int(x) for x in iso.split("-"))
    mo = L[lang]["months"][m - 1]
    return f"{d} {mo} {y}" if lang == "it" else f"{d} {mo} {y}"
def strip_tags(x): return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", x))).strip()
def jsonld(obj): return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False).replace("</", "<\\/") + "</script>"
def catcls(c): return "c-" + CAT_SLUG[c]

def parse(p):
    raw = p.read_text(encoding="utf-8")
    m = re.match(r"\s*<!--(.*?)-->(.*)", raw, re.S)
    meta = {}
    for line in m.group(1).strip().splitlines():
        k, _, v = line.partition(":")
        meta[k.strip()] = v.strip()
    body = m.group(2)
    script = ""
    sm = re.search(r"<script>(.*)</script>\s*$", body, re.S)
    if sm:
        script, body = sm.group(1), body[:sm.start()]
    meta.update(slug=p.stem, body=body.strip(), script=script.strip(), order=int(meta.get("order", 50)))
    meta.setdefault("updated", date.today().isoformat())
    return meta

TOOLS = {lang: sorted((parse(p) for p in (ROOT / L[lang]["tools_dir"]).glob("*.html")), key=lambda t: (CAT_KEYS.index(t["cat"]), t["order"]))
         for lang in L}
# collegamenti tra le due lingue: it_slug -> en_slug
EN_OF = {t["alt"]: t["slug"] for t in TOOLS["en"] if t.get("alt")}
IT_OF = {v: k for k, v in EN_OF.items()}
COMMON_JS = (SRC / "common.js").read_text(encoding="utf-8")
SHARE_JS = (SRC / "share.js").read_text(encoding="utf-8")

def url_of(lang, slug=None):
    base = L[lang]["prefix"]
    return f"{base}/{slug}/" if slug else (base + "/" if base else "/")

def other(lang, slug):
    """(lingua, percorso) della pagina equivalente nell'altra lingua."""
    if lang == "it":
        return "en", url_of("en", EN_OF[slug]) if slug in EN_OF else url_of("en")
    return "it", url_of("it", IT_OF[slug]) if slug in IT_OF else url_of("it")

def consent(lang):
    S = L[lang]
    return f"""<div id="ck" class="ck" role="dialog" aria-live="polite" aria-label="Cookie" hidden>
<p>{S["ck_text"]} <a href="{url_of(lang, "privacy")}">{S["privacy"]}</a></p>
<div class="ck-b"><button type="button" class="btn" id="ck-no">{S["ck_no"]}</button><button type="button" class="btn btn-primary" id="ck-ok">{S["ck_ok"]}</button></div></div>
<script>(function(){{var K='vsqc-consent',GA='{GA_ID}';
function load(){{if(window.__ga)return;window.__ga=1;var s=document.createElement('script');s.async=1;s.src='https://www.googletagmanager.com/gtag/js?id='+GA;document.head.appendChild(s);
window.dataLayer=window.dataLayer||[];window.gtag=function(){{dataLayer.push(arguments)}};gtag('js',new Date());gtag('config',GA);}}
var c=null;try{{c=localStorage.getItem(K)}}catch(e){{}}
var b=document.getElementById('ck');function set(v){{try{{localStorage.setItem(K,v)}}catch(e){{}}b.hidden=true;if(v==='ok')load();}}
if(c==='ok')load();else if(c!=='no')b.hidden=false;
document.getElementById('ck-ok').onclick=function(){{set('ok')}};document.getElementById('ck-no').onclick=function(){{set('no')}};
document.addEventListener('click',function(e){{var t=e.target.closest('[data-ck]');if(t){{e.preventDefault();b.hidden=false;}}}});}})();</script>"""

def logo(lang):
    return f'<a class="logo" href="{url_of(lang)}"><span class="logo-mark">€?</span><span>{L[lang]["logo"]}</span></a>'

def switch(lang, slug):
    olang, opath = other(lang, slug)
    flag, code = (FLAG_GB, "EN") if olang == "en" else (FLAG_IT, "IT")
    return (f'<a class="lang-switch" href="{opath}" hreflang="{olang}" lang="{olang}" title="{L[lang]["switch_label"]}" '
            f'aria-label="{L[lang]["switch_label"]}">{flag}<span>{code}</span></a>')

def header(lang, slug=None, active=""):
    S = L[lang]
    nav = "".join(f'<a href="{url_of(lang)}#{CAT_SLUG[c]}"{" class=on" if c == active else ""}>{S["cats"][c][0]}</a>' for c in CAT_KEYS)
    return f'<header class="site-header"><div class="wrap">{logo(lang)}<div class="hdr-r"><nav class="main-nav">{nav}</nav>{switch(lang, slug)}</div></div></header>'

def footer(lang):
    S = L[lang]
    cols = []
    for c in CAT_KEYS[:3]:
        links = "".join(f'<a href="{url_of(lang, t["slug"])}">{html.escape(t["h1"])}</a>' for t in TOOLS[lang] if t["cat"] == c)
        cols.append(f"<div><h4>{S['cats'][c][0]}</h4>{links}</div>")
    return f'''<footer class="site-footer"><div class="wrap"><div class="cols">
<div>{logo(lang)}<p>{S["footer_p"]}</p></div>
{"".join(cols)}</div>
<div class="bottom">© 2026 VuoiSapereQuantoCosta.it · {S["footer_b"]} · <a href="{url_of(lang, "privacy")}" style="display:inline;color:#b7bec8">{S["privacy"]}</a> · <a href="#" data-ck style="display:inline;color:#b7bec8">{S["manage_ck"]}</a></div></div></footer>'''

def page(lang, title, desc, path, main, slug=None, active="", script="", head_extra="", alt_paths=None):
    S = L[lang]
    canon = DOMAIN + path
    js = f"<script>\n{COMMON_JS}\n{script}\n</script>" if script else ""
    hreflang = ""
    if alt_paths:
        hreflang = "".join(f'<link rel="alternate" hreflang="{lg}" href="{DOMAIN}{p}">' for lg, p in alt_paths.items())
        hreflang += f'<link rel="alternate" hreflang="x-default" href="{DOMAIN}{alt_paths.get("it", path)}">'
    return f'''<!DOCTYPE html>
<html lang="{S["html_lang"]}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{canon}">
{hreflang}
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{canon}">
<meta property="og:locale" content="{"it_IT" if lang == "it" else "en_GB"}">
<meta name="theme-color" content="#0e6b63">
<meta name="google-site-verification" content="kYwrCokb8RvZCkuNno2ew4Bu0Jja8ny4wfENO5Qc8x8">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'><rect width='64' height='64' rx='16' fill='%230e6b63'/><text x='32' y='43' font-size='30' text-anchor='middle' fill='white' font-family='Arial' font-weight='bold'>€?</text></svg>">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/style.css">
{head_extra}
</head>
<body>
{header(lang, slug, active)}
<main>
{main}
</main>
{footer(lang)}
{js}
{consent(lang)}
</body>
</html>
'''

def card(lang, t):
    S = L[lang]
    new = f'<span class="new">{S["new"]}</span>' if t.get("new") else ""
    return (f'<a class="card {catcls(t["cat"])}" href="{url_of(lang, t["slug"])}">'
            f'<span class="ic">{t["icon"]}</span><span><h3>{html.escape(t["h1"])}{new}</h3><p>{html.escape(t["card"])}</p></span></a>')

def news_box(lang):
    f = SRC / L[lang]["news_file"]
    news = json.loads(f.read_text(encoding="utf-8")) if f.exists() else []
    items = sorted(news, key=lambda n: n["date"], reverse=True)[:4]
    if not items: return ""
    li = "".join(f'<li><time datetime="{n["date"]}">{fmtdate(n["date"], lang)}</time><a href="{n["url"]}">{html.escape(n["text"])}</a></li>' for n in items)
    return f'<section class="news"><h2>{L[lang]["news_h"]}</h2><ul>{li}</ul></section>'

def home(lang):
    S, tools = L[lang], TOOLS[lang]
    blocks = []
    for c in CAT_KEYS:
        items = [t for t in tools if t["cat"] == c]
        if not items: continue
        name, sub = S["cats"][c]
        blocks.append(f'<section class="cat-block" id="{CAT_SLUG[c]}"><div class="cat-head"><h2>{name}</h2><span>{sub}</span></div>'
                      f'<div class="grid">{"".join(card(lang, t) for t in items)}</div></section>')
    chips = "".join(f'<a class="chip" href="#{CAT_SLUG[c]}">{S["cats"][c][0]}</a>' for c in CAT_KEYS)
    why = "".join(f'<div><span style="font-size:24px">{i}</span><h3>{h}</h3><p>{p}</p></div>' for i, h, p in S["why"])
    main = f'''<section class="hero"><div class="wrap">
<span class="eyebrow"><i></i> {S["eyebrow"].format(n=len(tools))}</span>
<h1>{S["h1"]}</h1>
<p class="sub">{S["sub"]}</p>
<form class="search" action="{S["search_action"]}" method="get" role="search"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>
<input id="q" name="q" type="search" placeholder="{S["search_ph"]}" autocomplete="off" aria-label="{S["search_aria"]}" required style="padding-right:118px">
<button class="btn btn-primary" type="submit" style="position:absolute;right:6px;top:6px;bottom:6px;font-size:16px;padding:0 20px">{S["search_btn"]}</button></form>
<p style="font-size:13.5px;color:var(--muted);margin:10px 0 0">{S["search_note"]}</p>
<div class="chips">{chips}</div>
<div class="stats">{S["stats"]}</div>
</div></section>
<div class="wrap">
{news_box(lang)}
{"".join(blocks)}
<section class="why">{why}</section>
</div>'''
    ld = jsonld({"@context": "https://schema.org", "@type": "WebSite", "name": "Vuoi sapere quanto costa?", "alternateName": "VuoiSapereQuantoCosta.it",
                 "url": DOMAIN + url_of(lang), "inLanguage": S["in_lang"],
                 "potentialAction": {"@type": "SearchAction", "target": DOMAIN + S["search_action"] + "?q={search_term_string}", "query-input": "required name=search_term_string"}})
    return page(lang, S["home_title"], S["home_desc"], url_of(lang), main, head_extra=ld, alt_paths={"it": "/", "en": "/en/"})

PRIVACY = {
"it": """<div class="wrap"><div class="tool-head"><div class="crumb"><a href="/">Home</a> › Privacy</div><h1>Privacy e cookie</h1>
<p class="lead">Come VuoiSapereQuantoCosta.it tratta i dati di chi visita il sito. Ultimo aggiornamento: novembre 2026.</p></div>
<article class="info">
<h2>Titolare del trattamento</h2><p>Marco, gestore di VuoiSapereQuantoCosta.it. Per qualsiasi richiesta sulla privacy puoi scrivere a <a href="mailto:gipmac95@gmail.com">gipmac95@gmail.com</a> (gipmac95@gmail.com).</p>
<h2>I dati che inserisci nei calcolatori</h2><p>Tutti i calcoli avvengono direttamente nel tuo browser. I numeri e le parole che scrivi nei calcolatori e nella ricerca non vengono inviati né salvati da noi.</p>
<h2>Cookie tecnici</h2><p>Salviamo nel tuo browser solo la tua scelta sui cookie, per non chiedertela a ogni visita. Non serve il consenso per questo dato.</p>
<h2>Statistiche (Google Analytics)</h2><p>Solo se clicchi "Accetta", usiamo Google Analytics 4, un servizio di Google Ireland Limited, per contare in forma aggregata le visite, le pagine viste, il tipo di dispositivo, la provenienza delle visite e i click verso altri siti. Servono a capire quali pagine sono utili e a migliorarle. Google può trattare i dati anche negli Stati Uniti, nell'ambito dell'EU-US Data Privacy Framework. Se rifiuti, Google Analytics non viene caricato. Puoi cambiare idea quando vuoi con il link "Gestisci cookie" in fondo a ogni pagina.</p>
<h2>Hosting</h2><p>Il sito è ospitato da Netlify, che per motivi tecnici e di sicurezza può registrare dati come l'indirizzo IP nei registri del server.</p>
<h2>Link ad altri siti</h2><p>Molte pagine contengono link a siti esterni (per esempio eBay, Vinted, Subito, ARERA, fornitori di luce, gas e internet). Quando li apri, valgono le regole sulla privacy di quei siti.</p>
<h2>I tuoi diritti</h2><p>Puoi chiedere l'accesso, la rettifica o la cancellazione dei tuoi dati, opporti al trattamento e proporre reclamo al Garante per la protezione dei dati personali (garanteprivacy.it).</p>
</article></div>""",
"en": """<div class="wrap"><div class="tool-head"><div class="crumb"><a href="/en/">Home</a> › Privacy</div><h1>Privacy and cookies</h1>
<p class="lead">How VuoiSapereQuantoCosta.it handles visitors' data. Last updated: November 2026.</p></div>
<article class="info">
<h2>Data controller</h2><p>Marco, who runs VuoiSapereQuantoCosta.it. For any privacy request you can write to <a href="mailto:gipmac95@gmail.com">gipmac95@gmail.com</a> (gipmac95@gmail.com).</p>
<h2>What you type into the calculators</h2><p>All calculations happen directly in your browser. The numbers and words you type into the calculators and the search box are not sent to us or stored by us.</p>
<h2>Technical cookies</h2><p>We only store your cookie choice in your browser, so we don't have to ask you again on every visit. No consent is needed for this.</p>
<h2>Statistics (Google Analytics)</h2><p>Only if you click "Accept", we use Google Analytics 4, a service of Google Ireland Limited, to count visits, page views, device type, traffic sources and clicks to other websites in aggregate form. This helps us understand which pages are useful and improve them. Google may also process data in the United States under the EU-US Data Privacy Framework. If you decline, Google Analytics is not loaded. You can change your mind at any time with the "Cookie settings" link at the bottom of every page.</p>
<h2>Hosting</h2><p>The site is hosted by Netlify, which may record data such as IP addresses in server logs for technical and security reasons.</p>
<h2>Links to other websites</h2><p>Many pages link to external websites (for example eBay, Vinted, Subito, ARERA, energy and internet providers). When you open them, those websites' privacy policies apply.</p>
<h2>Your rights</h2><p>You can request access to, correction or deletion of your data, object to processing and lodge a complaint with the Italian data protection authority, the Garante per la protezione dei dati personali (garanteprivacy.it).</p>
</article></div>"""}

def tool_page(lang, t):
    S, tools = L[lang], TOOLS[lang]
    related = [x for x in tools if x["cat"] == t["cat"] and x["slug"] != t["slug"]]
    related += [x for x in tools if x["cat"] != t["cat"]][: max(0, 4 - len(related))]
    catname = S["cats"][t["cat"]][0]
    main = f'''<div class="wrap">
<div class="tool-head"><div class="crumb"><a href="{url_of(lang)}">{S["home"]}</a> › <a href="{url_of(lang)}#{CAT_SLUG[t["cat"]]}">{catname}</a></div>
<h1><span class="ic">{t["icon"]}</span>{html.escape(t["h1"])}</h1>
<p class="lead">{t["desc"]}</p>
<p class="upd">🗓️ {S["updated"]} {fmtdate(t["updated"], lang)}</p></div>
{t["body"]}
{embed_box(lang, t)}
<section class="related"><h2>{S["related"]}</h2><div class="grid">{"".join(card(lang, x) for x in related[:4])}</div></section>
</div>'''
    path = url_of(lang, t["slug"])
    url = DOMAIN + path
    faq = re.findall(r"<h2>(.*?)</h2>\s*<p>(.*?)</p>", t["body"].split('<article class="info">')[-1], re.S) if '<article class="info">' in t["body"] else []
    graph = [
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": S["home"], "item": DOMAIN + url_of(lang)},
            {"@type": "ListItem", "position": 2, "name": catname, "item": f"{DOMAIN}{url_of(lang)}#{CAT_SLUG[t['cat']]}"},
            {"@type": "ListItem", "position": 3, "name": t["h1"], "item": url}]},
        {"@type": "WebApplication", "name": t["h1"], "url": url, "description": t["desc"], "applicationCategory": "FinanceApplication",
         "operatingSystem": "Any", "inLanguage": S["in_lang"], "dateModified": t["updated"], "isAccessibleForFree": True,
         "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EUR"}}]
    if faq:
        graph.append({"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": strip_tags(q),
                      "acceptedAnswer": {"@type": "Answer", "text": strip_tags(a)}} for q, a in faq]})
    ld = jsonld({"@context": "https://schema.org", "@graph": graph})
    alt = None
    if lang == "it" and t["slug"] in EN_OF: alt = {"it": path, "en": url_of("en", EN_OF[t["slug"]])}
    if lang == "en" and t["slug"] in IT_OF: alt = {"it": url_of("it", IT_OF[t["slug"]]), "en": path}
    return page(lang, t["title"], t["desc"], path, main, slug=t["slug"], active=t["cat"], script=t["script"] + "\n" + SHARE_JS, head_extra=ld, alt_paths=alt)

def embed_url(lang, slug): return f"{DOMAIN}{L[lang]['prefix']}/embed/{slug}/"

def embed_box(lang, t):
    S = L[lang]
    code = (f'<iframe data-vsqc src="{embed_url(lang, t["slug"])}" title="{html.escape(t["h1"])}" width="100%" height="900" loading="lazy" style="border:0;max-width:760px;display:block"></iframe>'
            f'<p style="font-size:13px;max-width:760px">{S["emb_credit"]} <a href="{DOMAIN}{url_of(lang, t["slug"])}">VuoiSapereQuantoCosta.it – {html.escape(t["h1"])}</a></p>'
            '<script>addEventListener("message",function(e){if(e.origin!=="' + DOMAIN + '"||!e.data||!e.data.vsqcH)return;document.querySelectorAll("iframe[data-vsqc]").forEach(function(f){if(f.contentWindow===e.source)f.style.height=e.data.vsqcH+"px"})})</script>')
    return f'''<details class="embed-box"><summary>{S["emb_sum"]}</summary>
<p>{S["emb_p"]}</p>
<textarea id="emb_code" readonly rows="4">{html.escape(code)}</textarea>
<button type="button" class="btn" onclick="var t=document.getElementById('emb_code');t.select();try{{navigator.clipboard.writeText(t.value).catch(function(){{}})}}catch(e){{}};this.textContent='{S["emb_done"]}'">{S["emb_btn"]}</button></details>'''

def embed_page(lang, t):
    S = L[lang]
    js = f"<script>\n{COMMON_JS}\n{t['script']}\n</script>"
    return f'''<!DOCTYPE html>
<html lang="{S["html_lang"]}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(t["h1"])} – Vuoi sapere quanto costa?</title><meta name="robots" content="noindex">
<link rel="canonical" href="{DOMAIN}{url_of(lang, t["slug"])}"><base target="_blank">
<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/style.css"></head>
<body class="embed"><div class="embed-wrap">
<div class="embed-head"><span class="ic">{t["icon"]}</span><b>{html.escape(t["h1"])}</b></div>
{t["body"]}
<p class="embed-credit">{S["emb_free"]} <a href="{DOMAIN}{url_of(lang, t["slug"])}">VuoiSapereQuantoCosta.it</a></p>
</div>{js}
<script>(function(){{function s(){{try{{parent.postMessage({{vsqcH:document.documentElement.scrollHeight}},"*")}}catch(e){{}}}}s();if(window.ResizeObserver)new ResizeObserver(s).observe(document.body);addEventListener("load",s)}})();</script>
</body></html>'''

def not_found(lang):
    S = L[lang]
    return page(lang, f'{S["nf_title"]} – Vuoi sapere quanto costa?', S["nf_title"], url_of(lang) + "404",
                f'<div class="wrap" style="padding:80px 20px;text-align:center"><h1>{S["nf_title"]}</h1><p>{S["nf_p"]}</p><p><a class="btn btn-primary" href="{url_of(lang)}">{S["nf_btn"]}</a></p></div>')

# ---------- scrittura ----------
if OUT.exists(): shutil.rmtree(OUT)
OUT.mkdir()
shutil.copy(SRC / "style.css", OUT / "style.css")
sitemap = []
for lang in L:
    base = OUT / L[lang]["prefix"].strip("/") if L[lang]["prefix"] else OUT
    base.mkdir(exist_ok=True)
    (base / "index.html").write_text(home(lang), encoding="utf-8")
    tools = TOOLS[lang]
    latest = max(t["updated"] for t in tools)
    sitemap.append((DOMAIN + url_of(lang), latest))
    for t in tools:
        d = base / t["slug"]; d.mkdir()
        (d / "index.html").write_text(tool_page(lang, t), encoding="utf-8")
        e = base / "embed" / t["slug"]; e.mkdir(parents=True)
        (e / "index.html").write_text(embed_page(lang, t), encoding="utf-8")
        sitemap.append((DOMAIN + url_of(lang, t["slug"]), t["updated"]))
    (base / "privacy").mkdir()
    (base / "privacy" / "index.html").write_text(page(lang, f'{L[lang]["privacy"]} – Vuoi sapere quanto costa?', L[lang]["privacy"], url_of(lang, "privacy"), PRIVACY[lang]), encoding="utf-8")
    (base / "404.html").write_text(not_found(lang), encoding="utf-8")
(OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {DOMAIN}/sitemap.xml\n")
(OUT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                                 + "".join(f"  <url><loc>{u}</loc><lastmod>{d}</lastmod></url>\n" for u, d in sitemap) + "</urlset>\n")
missing = [t["slug"] for t in TOOLS["it"] if t["slug"] not in EN_OF]
print(f"Generate {len(TOOLS['it'])} pagine IT e {len(TOOLS['en'])} pagine EN in {OUT}")
if missing: print("Senza versione inglese:", ", ".join(missing))
