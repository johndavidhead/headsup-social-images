"""Render Head's Up social images from the John David Head design system.

Reads tokens.json + components/bundle.css from the design system folder and
drafts.json from this folder. Writes 1080x1350 PNGs: a 6-slide carousel and a
single card per post.

usage: python3 render_ds.py DS_PROJECT_DIR OUT_DIR [POST_JSON SLUG]
  DS_PROJECT_DIR  folder holding tokens.json, components/bundle.css, fonts/
  POST_JSON       one post object (topic, source_name, carousel, single_image,
                  optional scribble). Without it, renders every post in drafts.json.
  SLUG            file prefix, e.g. 2026-10-13-ai
Prints each file with its size; any OVERFLOW means a line of copy is too long.
"""
import json, html, os, sys, re
from playwright.sync_api import sync_playwright

BASE = os.path.dirname(os.path.abspath(__file__))
DS = sys.argv[1] if len(sys.argv) > 1 else os.path.join(BASE, 'ds')
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(BASE, 'images-ds')
CAVEAT = os.path.join(BASE, 'fonts', 'caveat-latin-600-normal.woff2')
W, H = 1080, 1350
e = html.escape


def token_css():
    t = json.load(open(os.path.join(DS, 'tokens.json')))
    flat = {}
    themed = {}
    for tok in t['color']['tokens']:
        (themed if isinstance(tok['value'], dict) else flat)[tok['name']] = tok['value']
    for sec in ('spacing', 'radius', 'stroke', 'shadow'):
        for tok in t[sec]['tokens']:
            flat[tok['name']] = tok['value']
    res = lambda v: re.sub(r'\{([a-z0-9-]+)\}', lambda m: f'var(--{m.group(1)})', v)
    root = ''.join(f'--{k}:{res(v)};' for k, v in flat.items())
    for k, v in t['type']['families'].items():
        root += f'--font-{k}:{v};'
    themes = ''
    for th in ('cream', 'navy'):
        sel = ':root,[data-theme="cream"]' if th == 'cream' else '[data-theme="navy"]'
        themes += sel + '{' + ''.join(f'--{k}:{res(v[th])};' for k, v in themed.items()) + '}'
    styles = ''
    for g in t['type']['groups']:
        for s in g['styles']:
            fam = s.get('family', g.get('family', 'serif'))
            css = f'font-family:var(--font-{fam});font-size:{s["fontSize"]};line-height:{s.get("lineHeight", 1.2)};font-weight:{s.get("fontWeight", 400)};'
            if 'letterSpacing' in s: css += f'letter-spacing:{s["letterSpacing"]};'
            if 'fontStyle' in s: css += f'font-style:{s["fontStyle"]};'
            if 'textTransform' in s: css += f'text-transform:{s["textTransform"]};'
            styles += f'.{s["name"]}{{{css}}}'
    fonts = ''
    for f in t['type']['fonts']:
        fonts += (f"@font-face{{font-family:'{f['family']}';src:url('file://{os.path.join(DS, f['file'])}');"
                  f"font-weight:{f['weight']};font-style:{f['style']};}}")
    fonts += f"@font-face{{font-family:'Caveat';src:url('file://{CAVEAT}');font-weight:600;}}"
    return fonts + ':root{' + root + '}' + themes + styles


def bundle_css():
    css = open(os.path.join(DS, 'components', 'bundle.css')).read()
    return re.sub(r'@import url\("[^"]*"\);', '', css)  # fonts are local; Inter is installed


CSS = None
EXTRA = """
html,body{margin:0;padding:0}
.hu-canvas{transform:none}
.hu-canvas .wm{margin-bottom:36px}
.hu-canvas .wm .hu-wordmark{font-size:72px;letter-spacing:-1.5px}
.hu-canvas .wm .src{margin-top:8px}
.hu-canvas .hu-headline{margin-top:36px}
.hu-canvas .body{color:var(--fg-body);margin-top:40px}
.hu-canvas .by{font-family:var(--font-sans);font-weight:700;font-size:24px;letter-spacing:4px;color:var(--fg-brand)}
.hu-canvas .hu-footer .cta{font-size:26px;line-height:1.35}
.hu-canvas .hu-footer .hu-wordmark{font-size:46px}
.hu-canvas .hu-footer .hu-sub{font-size:16px}
/* whimsical mood */
.hu-canvas.whim{padding:100px 108px}
.whim .hu-corners{position:absolute;inset:36px;pointer-events:none}
.whim .hu-corners i{border-color:var(--fg-brand)}
.whim.center .hu-tag{justify-content:center}
.whim.center .hu-tag .t{letter-spacing:10px}
.whim.center .hu-headline{text-align:center}
.whim.center .wm{text-align:center}
.whim .scrib{text-align:center;margin-top:56px}
.whim .hu-scribble{font-size:54px;padding:0 8px 4px}
"""


def page(inner, theme='cream', cls=''):
    return (f'<!doctype html><html data-theme="{theme}"><head><meta charset="utf-8"><style>{CSS}{EXTRA}</style></head>'
            f'<body><div class="hu-canvas {cls}" data-theme="{theme}">{inner}</div></body></html>')


META_L = 'Head&rsquo;s Up &middot; John&rsquo;s take on AI &amp; Quantum'


def meta(counter=''):
    return f'<div class="hu-meta"><div class="l">{META_L}</div><div class="r">{e(counter)}</div></div>'


def tag(t):
    return f'<div class="hu-tag"><div class="bar"></div><div class="t">{e(t)}</div></div>'


def wordmark_block():
    return ('<div class="wm"><div class="hu-wordmark">Head&rsquo;s Up<span class="dot">.</span></div>'
            '<div class="src">One story a day, by John Head</div></div>')


def cover_size(h):
    return 'display-cover' if len(h) <= 55 else 'display-cover" style="font-size:88px'


def slide_size(h):
    return 'display-slide' if len(h) <= 45 else 'display-slide" style="font-size:62px'


def corners(whim):
    return '<div class="hu-corners"><i></i><i></i><i></i><i></i></div>' if whim else ''


def build(post, slug, scribble=None):
    whim = post['topic'].lower() == 'weekend'
    src = e(post['source_name'])
    slides = post['carousel']
    n = len(slides)
    out = []
    for s in slides:
        i = s['slide']
        c = f'{i} / {n}'
        if i == 1:
            sc = f'<div class="scrib"><span class="hu-scribble">{e(scribble)}</span></div>' if (whim and scribble) else ''
            inner = (corners(whim) + meta(c) + tag(s['tag'] or post['topic'].upper()) +
                     f'<h1 class="hu-headline {cover_size(s["headline"])}">{e(s["headline"])}</h1>' + sc +
                     '<div class="grow"></div>' + wordmark_block() +
                     f'<div class="hu-footer"><div class="src">{src}</div><div class="swipe">SWIPE &rarr;</div></div>')
            h = page(inner, cls='whim center' if whim else '')
        elif s['role'].lower() == 'my take':
            inner = (meta(c) + tag('My take') +
                     f'<h2 class="hu-headline {slide_size(s["headline"])}">{e(s["headline"])}</h2>'
                     f'<div class="slide-body body">{e(s["body"])}</div><div class="grow"></div>'
                     '<div class="hu-footer"><div class="src">John Head</div><div class="swipe">SWIPE &rarr;</div></div>')
            h = page(inner, theme='navy')
        elif i == n:
            inner = (corners(whim) + meta(c) + tag('Your turn') +
                     f'<h2 class="hu-headline {slide_size(s["headline"])}">{e(s["headline"])}</h2>'
                     '<div class="slide-body body">Follow Head&rsquo;s Up for one story a day.</div><div class="grow"></div>'
                     '<div class="hu-footer"><div><div class="hu-wordmark">Head&rsquo;s Up<span class="dot">.</span></div>'
                     '<div class="hu-sub">John Head &middot; AI &amp; Quantum</div></div>'
                     '<div class="cta">Subscribe on LinkedIn.<br><b>linkedin.com/in/johndhead</b></div></div>')
            h = page(inner, cls='whim' if whim else '')
        else:
            inner = (corners(whim) + meta(c) + tag(s['role']) +
                     f'<h2 class="hu-headline {slide_size(s["headline"])}">{e(s["headline"])}</h2>'
                     f'<div class="slide-body body">{e(s["body"])}</div><div class="grow"></div>'
                     f'<div class="num">{i}</div>'
                     f'<div class="hu-footer"><div class="src">{src}</div><div class="swipe">SWIPE &rarr;</div></div>')
            h = page(inner, cls='whim' if whim else '')
        out.append((f'{slug}-carousel-{i}.png', h))
    si = post['single_image']
    sc = f'<div class="scrib"><span class="hu-scribble">{e(scribble)}</span></div>' if (whim and scribble) else ''
    inner = (corners(whim) + meta() + tag(si['tag']) +
             f'<h1 class="hu-headline {cover_size(si["headline"])}">{e(si["headline"])}</h1>' + sc +
             '<div class="grow"></div>' + wordmark_block() +
             f'<div class="hu-footer"><div class="src">{e(si["sub"])}</div><div class="by">JOHN HEAD</div></div>')
    out.append((f'{slug}-single.png', page(inner, cls='whim center' if whim else '')))
    return out


if __name__ == '__main__':
    CSS = token_css() + bundle_css()
    os.makedirs(OUT, exist_ok=True)
    jobs = []
    if len(sys.argv) > 4:
        post = json.load(open(sys.argv[3]))
        jobs += build(post, sys.argv[4], scribble=post.get('scribble'))
    else:
        d = json.load(open(os.path.join(BASE, 'drafts.json')))
        for post, slug in zip(d['posts'], ['ai', 'quantum', 'saturday']):
            jobs += build(post, slug, scribble=post.get('scribble'))
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={'width': W, 'height': H})
        for name, h in jobs:
            hp = os.path.join(OUT, name.replace('.png', '.html'))
            open(hp, 'w').write(h)
            pg.goto('file://' + hp)
            pg.wait_for_timeout(200)
            over = pg.evaluate('(()=>{const c=document.querySelector(".hu-canvas");return c.scrollHeight>c.clientHeight||c.scrollWidth>c.clientWidth})()')
            pg.screenshot(path=os.path.join(OUT, name), clip={'x': 0, 'y': 0, 'width': W, 'height': H})
            kb = os.path.getsize(os.path.join(OUT, name)) // 1024
            print(name, f'{kb}KB', 'OVERFLOW' if over else '')
        b.close()
