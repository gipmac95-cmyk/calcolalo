#!/usr/bin/env python3
"""Genera il sito statico: home + una pagina per ogni calcolatore in tools/*.html.

Ogni file in tools/ inizia con un blocco di intestazione:
<!--
title: titolo della pagina (tag <title>)
h1: titolo visibile
desc: meta description
card: testo breve della scheda in home
icon: emoji
cat: Auto | Casa | Lavoro | Collezionismo | Utilità
order: numero (ordine nella categoria)
new: si (facoltativo)
-->
seguito dall'HTML del calcolatore e da un <script> facoltativo.
"""
import html, json, re, shutil
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent
SRC, TOOLS, OUT = ROOT / "src", ROOT / "tools", ROOT / "public"
DOMAIN = "https://vuoisaperequantocosta.it"
SITE = "Vuoi sapere quanto costa?"
GA_ID = "G-FKCYXWVBCF"
CATS = [("Auto", "Bollo, passaggio di proprietà, viaggi e valore dell'usato"),
        ("Casa", "Mutuo, bollette di luce e gas, internet"),
        ("Lavoro", "Stipendio, TFR e IVA"),
        ("Collezionismo", "Quanto valgono videogiochi e carte"),
        ("Utilità", "Valore dell'usato e calcoli di tutti i giorni")]
SLUGCAT = {"Utilità": "utilita"}


CONSENT = """<div id="ck" class="ck" role="dialog" aria-live="polite" aria-label="Cookie" hidden>
<p><b>Usiamo i cookie solo per statistiche anonime</b> sulle visite, con Google Analytics, se ci dai il consenso. I calcoli restano sempre sul tuo dispositivo. <a href="/privacy/">Privacy e cookie</a></p>
<div class="ck-b"><button type="button" class="btn" id="ck-no">Rifiuta</button><button type="button" class="btn btn-primary" id="ck-ok">Accetta</button></div></div>
<script>(function(){var K='vsqc-consent',GA='""" + GA_ID + """';
function load(){if(window.__ga)return;window.__ga=1;var s=document.createElement('script');s.async=1;s.src='https://www.googletagmanager.com/gtag/js?id='+GA;document.head.appendChild(s);
window.dataLayer=window.dataLayer||[];window.gtag=function(){dataLayer.push(arguments)};gtag('js',new Date());gtag('config',GA);}
var c=null;try{c=localStorage.getItem(K)}catch(e){}
var b=document.getElementById('ck');function set(v){try{localStorage.setItem(K,v)}catch(e){}b.hidden=true;if(v==='ok')load();}
if(c==='ok')load();else if(c!=='no')b.hidden=false;
document.getElementById('ck-ok').onclick=function(){set('ok')};document.getElementById('ck-no').onclick=function(){set('no')};
document.addEventListener('click',function(e){var t=e.target.closest('[data-ck]');if(t){e.preventDefault();b.hidden=false;}});})();</script>"""

MESI = ["gennaio","febbraio","marzo","aprile","maggio","giugno","luglio","agosto","settembre","ottobre","novembre","dicembre"]
def itdate(iso):
    y, m, d = (int(x) for x in iso.split("-"))
    return f"{d} {MESI[m-1]} {y}"
def catslug(c): return SLUGCAT.get(c, c.lower())
def strip_tags(x): return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", x))).strip()
def jsonld(obj): return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False).replace("</", "<\\/") + "</script>"

def catcls(c): return "c-" + SLUGCAT.get(c, c.lower())

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

tools = sorted((parse(p) for p in TOOLS.glob("*.html")), key=lambda t: (t["cat"], t["order"]))
COMMON_JS = (SRC / "common.js").read_text(encoding="utf-8")
SHARE_JS = (SRC / "share.js").read_text(encoding="utf-8")
NEWS = json.loads((SRC / "news.json").read_text(encoding="utf-8"))

def logo():
    return '<a class="logo" href="/"><span class="logo-mark">€?</span><span>Vuoi sapere <b>quanto costa?</b></span></a>'

def header(active=""):
    nav = "".join(f'<a href="/#{SLUGCAT.get(c, c.lower())}"{" class=on" if c == active else ""}>{c}</a>' for c, _ in CATS)
    return f'<header class="site-header"><div class="wrap">{logo()}<nav class="main-nav">{nav}</nav></div></header>'

def footer():
    cols = []
    for c, _ in CATS[:3]:
        links = "".join(f'<a href="/{t["slug"]}/">{html.escape(t["h1"])}</a>' for t in tools if t["cat"] == c)
        cols.append(f"<div><h4>{c}</h4>{links}</div>")
    return f'''<footer class="site-footer"><div class="wrap"><div class="cols">
<div>{logo()}<p>Calcolatori gratuiti e senza registrazione per sapere in pochi secondi quanto costa davvero una spesa. I dati inseriti restano nel tuo browser.</p></div>
{"".join(cols)}</div>
<div class="bottom">© 2026 VuoiSapereQuantoCosta.it · I risultati sono stime indicative e non sostituiscono il parere di un professionista. · <a href="/privacy/" style="display:inline;color:#b7bec8">Privacy e cookie</a> · <a href="#" data-ck style="display:inline;color:#b7bec8">Gestisci cookie</a></div></div></footer>'''

def page(title, desc, path, main, active="", script="", head_extra=""):
    canon = DOMAIN + path
    js = f"<script>\n{COMMON_JS}\n{script}\n</script>" if script else ""
    return f'''<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{canon}">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{canon}">
<meta name="theme-color" content="#0e6b63">
<meta name="google-site-verification" content="kYwrCokb8RvZCkuNno2ew4Bu0Jja8ny4wfENO5Qc8x8">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'><rect width='64' height='64' rx='16' fill='%230e6b63'/><text x='32' y='43' font-size='30' text-anchor='middle' fill='white' font-family='Arial' font-weight='bold'>€?</text></svg>">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/style.css">
{head_extra}
</head>
<body>
{header(active)}
<main>
{main}
</main>
{footer()}
{js}
{CONSENT}
</body>
</html>
'''

def card(t):
    new = '<span class="new">Nuovo</span>' if t.get("new") else ""
    return (f'<a class="card {catcls(t["cat"])}" href="/{t["slug"]}/" data-s="{html.escape((t["h1"] + " " + t["card"] + " " + t["cat"]).lower())}">'
            f'<span class="ic">{t["icon"]}</span><span><h3>{html.escape(t["h1"])}{new}</h3><p>{html.escape(t["card"])}</p></span></a>')

def home():
    blocks = []
    for c, sub in CATS:
        items = [t for t in tools if t["cat"] == c]
        if not items: continue
        blocks.append(f'<section class="cat-block" id="{SLUGCAT.get(c, c.lower())}"><div class="cat-head"><h2>{c}</h2><span>{sub}</span></div>'
                      f'<div class="grid">{"".join(card(t) for t in items)}</div></section>')
    chips = "".join(f'<a class="chip" href="#{SLUGCAT.get(c, c.lower())}">{c}</a>' for c, _ in CATS)
    main = f'''<section class="hero"><div class="wrap">
<span class="eyebrow"><i></i> {len(tools)} calcolatori gratuiti · aggiornati al 2026</span>
<h1>Vuoi sapere <em>quanto costa?</em></h1>
<p class="sub">Il valore di qualsiasi oggetto usato, il tuo stipendio netto, le bollette, il bollo, il mutuo e molto altro. Scoprilo in pochi secondi.</p>
<form class="search" action="/quanto-vale/" method="get" role="search"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>
<input id="q" name="q" type="search" placeholder="Cosa vuoi sapere quanto costa? es. iPhone 13, Fiat Panda, bollo…" autocomplete="off" aria-label="Cerca" required style="padding-right:118px">
<button class="btn btn-primary" type="submit" style="position:absolute;right:6px;top:6px;bottom:6px;font-size:16px;padding:0 20px">Cerca</button></form>
<p style="font-size:13.5px;color:var(--muted);margin:10px 0 0">Scrivi qualsiasi oggetto: ti mostriamo i prezzi dell'usato su Vinted, eBay e Subito, e il calcolatore giusto se c'è.</p>
<div class="chips">{chips}</div>
<div class="stats"><span><b>Gratis</b> e senza registrazione</span><span><b>Dati aggiornati</b> alle regole 2026</span><span><b>Privacy</b>: i calcoli restano sul tuo dispositivo</span></div>
</div></section>
<div class="wrap">
{news_box()}
{"".join(blocks)}
<p class="empty" id="empty">Nessun calcolatore trovato. Prova con un'altra parola.</p>
<section class="why">
<div><span style="font-size:24px">⚡</span><h3>Risultato immediato</h3><p>Il calcolo si aggiorna mentre scrivi, senza pulsanti e senza attese.</p></div>
<div><span style="font-size:24px">📚</span><h3>Spiegato bene</h3><p>Ogni calcolatore spiega come si arriva al risultato, in parole semplici.</p></div>
<div><span style="font-size:24px">🔒</span><h3>Nessun dato salvato</h3><p>Non chiediamo email e non salviamo quello che inserisci.</p></div>
</section>
</div>'''
    ld = jsonld({"@context": "https://schema.org", "@type": "WebSite", "name": "Vuoi sapere quanto costa?", "alternateName": "VuoiSapereQuantoCosta.it",
                 "url": DOMAIN + "/", "inLanguage": "it-IT",
                 "potentialAction": {"@type": "SearchAction", "target": DOMAIN + "/quanto-vale/?q={search_term_string}", "query-input": "required name=search_term_string"}})
    return page(f"{SITE} Calcolatori gratuiti per le spese di tutti i giorni",
                "Calcolatori online gratuiti: stipendio netto 2026, bollo auto, passaggio di proprietà, rata del mutuo, bollette di luce e gas, valore dell'auto usata, IVA, TFR e altro.",
                "/", main, head_extra=ld)

def news_box():
    items = sorted(NEWS, key=lambda n: n["date"], reverse=True)[:4]
    if not items: return ""
    li = "".join(f'<li><time datetime="{n["date"]}">{itdate(n["date"])}</time><a href="{n["url"]}">{html.escape(n["text"])}</a></li>' for n in items)
    return f'<section class="news"><h2>🔔 Ultimi aggiornamenti</h2><ul>{li}</ul></section>'


PRIVACY = """<div class="wrap"><div class="tool-head"><div class="crumb"><a href="/">Home</a> › Privacy</div><h1>Privacy e cookie</h1>
<p class="lead">Come VuoiSapereQuantoCosta.it tratta i dati di chi visita il sito. Ultimo aggiornamento: novembre 2026.</p></div>
<article class="info">
<h2>Titolare del trattamento</h2><p>Marco, gestore di VuoiSapereQuantoCosta.it. Per qualsiasi richiesta sulla privacy puoi scrivere a <a href="mailto:gipmac95@gmail.com">gipmac95@gmail.com</a> (gipmac95@gmail.com).</p>
<h2>I dati che inserisci nei calcolatori</h2><p>Tutti i calcoli avvengono direttamente nel tuo browser. I numeri e le parole che scrivi nei calcolatori e nella ricerca non vengono inviati né salvati da noi.</p>
<h2>Cookie tecnici</h2><p>Salviamo nel tuo browser solo la tua scelta sui cookie, per non chiedertela a ogni visita. Non serve il consenso per questo dato.</p>
<h2>Statistiche (Google Analytics)</h2><p>Solo se clicchi "Accetta", usiamo Google Analytics 4, un servizio di Google Ireland Limited, per contare in forma aggregata le visite, le pagine viste, il tipo di dispositivo, la provenienza delle visite e i click verso altri siti. Servono a capire quali pagine sono utili e a migliorarle. Google può trattare i dati anche negli Stati Uniti, nell'ambito dell'EU-US Data Privacy Framework. Se rifiuti, Google Analytics non viene caricato. Puoi cambiare idea quando vuoi con il link "Gestisci cookie" in fondo a ogni pagina.</p>
<h2>Hosting</h2><p>Il sito è ospitato da Netlify, che per motivi tecnici e di sicurezza può registrare dati come l'indirizzo IP nei registri del server.</p>
<h2>Link ad altri siti</h2><p>Molte pagine contengono link a siti esterni (per esempio eBay, Vinted, Subito, ARERA, fornitori di luce, gas e internet). Quando li apri, valgono le regole sulla privacy di quei siti.</p>
<h2>I tuoi diritti</h2><p>Puoi chiedere l'accesso, la rettifica o la cancellazione dei tuoi dati, opporti al trattamento e proporre reclamo al Garante per la protezione dei dati personali (garanteprivacy.it).</p>
</article></div>"""

def tool_page(t):
    related = [x for x in tools if x["cat"] == t["cat"] and x["slug"] != t["slug"]]
    related += [x for x in tools if x["cat"] != t["cat"]][: max(0, 4 - len(related))]
    main = f'''<div class="wrap">
<div class="tool-head"><div class="crumb"><a href="/">Home</a> › <a href="/#{SLUGCAT.get(t["cat"], t["cat"].lower())}">{t["cat"]}</a></div>
<h1><span class="ic">{t["icon"]}</span>{html.escape(t["h1"])}</h1>
<p class="lead">{t["desc"]}</p>
<p class="upd">🗓️ Aggiornato il {itdate(t["updated"])}</p></div>
{t["body"]}
{embed_box(t)}
<section class="related"><h2>Altri calcolatori</h2><div class="grid">{"".join(card(x) for x in related[:4])}</div></section>
</div>'''
    url = f"{DOMAIN}/{t['slug']}/"
    faq = re.findall(r"<h2>(.*?)</h2>\s*<p>(.*?)</p>", t["body"].split('<article class="info">')[-1], re.S) if '<article class="info">' in t["body"] else []
    graph = [
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": DOMAIN + "/"},
            {"@type": "ListItem", "position": 2, "name": t["cat"], "item": f"{DOMAIN}/#{catslug(t['cat'])}"},
            {"@type": "ListItem", "position": 3, "name": t["h1"], "item": url}]},
        {"@type": "WebApplication", "name": t["h1"], "url": url, "description": t["desc"], "applicationCategory": "FinanceApplication",
         "operatingSystem": "Any", "inLanguage": "it-IT", "dateModified": t["updated"], "isAccessibleForFree": True,
         "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EUR"}}]
    if faq:
        graph.append({"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": strip_tags(q),
                      "acceptedAnswer": {"@type": "Answer", "text": strip_tags(a)}} for q, a in faq]})
    ld = jsonld({"@context": "https://schema.org", "@graph": graph})
    return page(t["title"], t["desc"], f"/{t['slug']}/", main, active=t["cat"], script=t["script"] + "\n" + SHARE_JS, head_extra=ld)

def embed_box(t):
    code = (f'<iframe data-vsqc src="{DOMAIN}/embed/{t["slug"]}/" title="{html.escape(t["h1"])}" width="100%" height="900" loading="lazy" style="border:0;max-width:760px;display:block"></iframe>'
            f'<p style="font-size:13px;max-width:760px">Calcolatore offerto da <a href="{DOMAIN}/{t["slug"]}/">VuoiSapereQuantoCosta.it – {html.escape(t["h1"])}</a></p>'
            '<script>addEventListener("message",function(e){if(e.origin!=="' + DOMAIN + '"||!e.data||!e.data.vsqcH)return;document.querySelectorAll("iframe[data-vsqc]").forEach(function(f){if(f.contentWindow===e.source)f.style.height=e.data.vsqcH+"px"})})</script>')
    return f'''<details class="embed-box"><summary>🧩 Aggiungi questo calcolatore al tuo sito o blog</summary>
<p>Copia questo codice e incollalo nella tua pagina: il calcolatore apparirà sul tuo sito, gratis e sempre aggiornato.</p>
<textarea id="emb_code" readonly rows="4">{html.escape(code)}</textarea>
<button type="button" class="btn" onclick="var t=document.getElementById('emb_code');t.select();try{{navigator.clipboard.writeText(t.value).catch(function(){{}})}}catch(e){{}};this.textContent='Codice copiato!'">Copia il codice</button></details>'''

def embed_page(t):
    js = f"<script>\n{COMMON_JS}\n{t['script']}\n</script>"
    return f'''<!DOCTYPE html>
<html lang="it"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(t["h1"])} – {SITE}</title><meta name="robots" content="noindex">
<link rel="canonical" href="{DOMAIN}/{t["slug"]}/"><base target="_blank">
<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/style.css"></head>
<body class="embed"><div class="embed-wrap">
<div class="embed-head"><span class="ic">{t["icon"]}</span><b>{html.escape(t["h1"])}</b></div>
{t["body"]}
<p class="embed-credit">Calcolatore gratuito di <a href="{DOMAIN}/{t["slug"]}/">VuoiSapereQuantoCosta.it</a></p>
</div>{js}
<script>(function(){{function s(){{try{{parent.postMessage({{vsqcH:document.documentElement.scrollHeight}},"*")}}catch(e){{}}}}s();if(window.ResizeObserver)new ResizeObserver(s).observe(document.body);addEventListener("load",s)}})();</script>
</body></html>'''

if OUT.exists(): shutil.rmtree(OUT)
OUT.mkdir()
shutil.copy(SRC / "style.css", OUT / "style.css")
(OUT / "index.html").write_text(home(), encoding="utf-8")
for t in tools:
    d = OUT / t["slug"]; d.mkdir()
    (d / "index.html").write_text(tool_page(t), encoding="utf-8")
    e = OUT / "embed" / t["slug"]; e.mkdir(parents=True)
    (e / "index.html").write_text(embed_page(t), encoding="utf-8")
(OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {DOMAIN}/sitemap.xml\n")
latest = max(t["updated"] for t in tools)
urls = [(DOMAIN + "/", latest)] + [(f"{DOMAIN}/{t['slug']}/", t["updated"]) for t in tools]
(OUT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                                 + "".join(f"  <url><loc>{u}</loc><lastmod>{d}</lastmod></url>\n" for u, d in urls) + "</urlset>\n")
(OUT / "privacy").mkdir()
(OUT / "privacy" / "index.html").write_text(page("Privacy e cookie – " + SITE, "Informativa sulla privacy e sui cookie di VuoiSapereQuantoCosta.it", "/privacy/", PRIVACY), encoding="utf-8")
(OUT / "404.html").write_text(page("Pagina non trovata – " + SITE, "Pagina non trovata", "/404",
    '<div class="wrap" style="padding:80px 20px;text-align:center"><h1>Pagina non trovata</h1><p>La pagina che cerchi non esiste.</p><p><a class="btn btn-primary" href="/">Torna ai calcolatori</a></p></div>'), encoding="utf-8")
print(f"Generate {len(tools)} pagine di calcolatori in {OUT}")
