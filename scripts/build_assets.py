#!/usr/bin/env python3
"""Generates the animated SVG panels used in README.md.

Run from the repo root:  python3 scripts/build_assets.py
Everything is plain SVG + CSS/SMIL animation, so GitHub renders it as-is.
Icon paths come from Simple Icons (CC0), stored in scripts/icons.json.
"""
import json
import math
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"
ICONS = json.loads((Path(__file__).parent / "icons.json").read_text())

MONO = "'JetBrains Mono','Fira Code','SFMono-Regular',ui-monospace,Menlo,Consolas,monospace"
SANS = "'Inter','Segoe UI','Helvetica Neue',Arial,sans-serif"

BG0, BG1 = "#06070d", "#0d1020"
CYAN, GO, VIOLET, PINK, LIME, AMBER = "#22d3ee", "#00ADD8", "#a78bfa", "#f472b6", "#34d399", "#fbbf24"
MUTED, TEXT = "#7c86a2", "#e6e9f5"
GLOWS = {"cyan": CYAN, "go": GO, "violet": VIOLET, "pink": PINK}

random.seed(42)


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def icon(name, x, y, size, color):
    s = size / 24
    return f'<path transform="translate({x} {y}) scale({s})" d="{ICONS[name]}" fill="{color}"/>'


def svg(w, h, body, style=""):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" fill="none">'
        f"<style>{style}</style>{body}</svg>"
    )


def frame_defs(w, h, rx=20):
    return f"""
  <clipPath id="frame"><rect width="{w}" height="{h}" rx="{rx}"/></clipPath>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="{BG1}"/><stop offset="1" stop-color="{BG0}"/>
  </linearGradient>
  <linearGradient id="edge" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="{CYAN}"/><stop offset=".5" stop-color="{VIOLET}"/><stop offset="1" stop-color="{PINK}"/>
  </linearGradient>
  <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
    <feGaussianBlur stdDeviation="6" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
""" + "".join(
        f'<radialGradient id="r{n}"><stop offset="0" stop-color="{c}"/><stop offset=".45" stop-color="{c}" stop-opacity=".45"/><stop offset="1" stop-color="{c}" stop-opacity="0"/></radialGradient>'
        for n, c in GLOWS.items()
    )


def frame_border(w, h, rx=20):
    return f'<rect x=".75" y=".75" width="{w-1.5}" height="{h-1.5}" rx="{rx}" stroke="url(#edge)" stroke-opacity=".55" stroke-width="1.5"/>'


def stars(w, h, n, ymax=None):
    out = []
    for i in range(n):
        x, y = random.uniform(0, w), random.uniform(0, ymax or h)
        r = random.choice([0.6, 0.8, 1, 1.3])
        out.append(f'<circle class="tw t{i%4}" cx="{x:.0f}" cy="{y:.0f}" r="{r}" fill="#fff"/>')
    return "".join(out)


STAR_CSS = """
.tw{animation:tw 4s ease-in-out infinite}
.t1{animation-duration:5.5s;animation-delay:-1s}.t2{animation-duration:3.2s;animation-delay:-2s}.t3{animation-duration:6.8s;animation-delay:-3s}
@keyframes tw{0%,100%{opacity:.15}50%{opacity:.9}}
"""


# ---------------------------------------------------------------- hero
def hero():
    W, H, HZ = 1200, 480, 330
    # perspective grid: vertical lines to the vanishing point, horizontal lines rushing toward the viewer
    vlines = "".join(
        f'<line x1="600" y1="{HZ}" x2="{600 + k*170}" y2="440" />' for k in range(-9, 10)
    )
    hlines = "".join(
        f'<line x1="0" x2="{W}" y1="{HZ}" y2="{HZ}">'
        f'<animate attributeName="y1" values="{HZ};440" dur="3.2s" begin="-{i*0.4:.1f}s" repeatCount="indefinite" calcMode="spline" keyTimes="0;1" keySplines=".55 0 1 .45"/>'
        f'<animate attributeName="y2" values="{HZ};440" dur="3.2s" begin="-{i*0.4:.1f}s" repeatCount="indefinite" calcMode="spline" keyTimes="0;1" keySplines=".55 0 1 .45"/>'
        f"</line>"
        for i in range(8)
    )

    # rotating role line with a char-by-char typewriter
    roles = ["Go backend engineer", "microservices & event-driven", "highload, but make it calm", "postgres · kafka · redis"]
    cw, fs, base_x, slot = 14.4, 24, 96, 4.0  # char width @24px mono
    total = slot * len(roles)
    times, widths = [], []
    for j, r in enumerate(roles):
        t0 = j * slot
        n = len(r)
        type_t = 1.6
        for c in range(n + 1):
            times.append(t0 + type_t * c / n)
            widths.append(c * cw)
        times.append(t0 + 3.0)
        widths.append(n * cw)
        for c in range(n, -1, -4):
            times.append(t0 + 3.0 + 0.6 * (n - c) / n)
            widths.append(c * cw)
        times.append(t0 + 3.65)
        widths.append(0)
    times.append(total)
    widths.append(0)
    kt = ";".join(f"{t/total:.4f}" for t in times)
    wv = ";".join(f"{w:.1f}" for w in widths)
    xv = ";".join(f"{base_x + w + 2:.1f}" for w in widths)
    role_texts = []
    for j, r in enumerate(roles):
        vis = ";".join(["0"] * j + ["1"] + ["0"] * (len(roles) - j - 1))
        kts = ";".join(f"{k/len(roles):.3f}" for k in range(len(roles)))
        role_texts.append(
            f'<text x="{base_x}" y="304" font-family="{MONO}" font-size="{fs}" fill="{CYAN}" opacity="0">{esc(r)}'
            f'<animate attributeName="opacity" values="{vis}" keyTimes="{kts}" dur="{total}s" calcMode="discrete" repeatCount="indefinite"/></text>'
        )

    # terminal window: a service booting up
    tx, ty, tw, th = 690, 64, 450, 236
    logs = [
        (f'<tspan fill="{LIME}">$</tspan> go run ./cmd/filipp', 0.4),
        (f'<tspan fill="{MUTED}">INF</tspan> config loaded <tspan fill="{MUTED}">env=</tspan><tspan fill="{AMBER}">prod</tspan>', 1.4),
        (f'<tspan fill="{MUTED}">INF</tspan> postgres pool ready <tspan fill="{MUTED}">conns=</tspan><tspan fill="{AMBER}">32</tspan>', 2.0),
        (f'<tspan fill="{MUTED}">INF</tspan> redis connected <tspan fill="{MUTED}">ping=</tspan><tspan fill="{AMBER}">0.3ms</tspan>', 2.6),
        (f'<tspan fill="{MUTED}">INF</tspan> kafka consumer joined <tspan fill="{MUTED}">group=</tspan><tspan fill="{AMBER}">readme</tspan>', 3.2),
        (f'<tspan fill="{MUTED}">INF</tspan> grpc listening <tspan fill="{MUTED}">addr=</tspan><tspan fill="{AMBER}">:9090</tspan>', 3.8),
        (f'<tspan fill="{LIME}">✓ ready</tspan> <tspan fill="{MUTED}">in</tspan> 42ms <tspan fill="{MUTED}">· p99</tspan> 7ms', 4.6),
    ]
    LOOP = 11
    log_svg = []
    for i, (txt, t) in enumerate(logs):
        a = t / LOOP
        log_svg.append(
            f'<text x="{tx+22}" y="{ty+70+i*23}" font-family="{MONO}" font-size="14" fill="{TEXT}" opacity="0">{txt}'
            f'<animate attributeName="opacity" values="0;0;1;1;0" keyTimes="0;{a:.3f};{a+0.01:.3f};.94;1" dur="{LOOP}s" repeatCount="indefinite"/></text>'
        )
    cursor_y = ty + 70 + len(logs) * 23

    ticker_items = ["Go", "PostgreSQL", "Apache Kafka", "Redis", "Docker", "gRPC", "Prometheus", "Grafana", "Linux", "GitLab CI", "Kubernetes", "RabbitMQ"]
    tick = "".join(
        f'<tspan fill="{TEXT}">{esc(t)}</tspan><tspan fill="{VIOLET}">   ✦   </tspan>' for t in ticker_items
    )
    tick_w = sum((len(t) + 7) * 9.6 for t in ticker_items)

    style = STAR_CSS + f"""
.glA{{animation:glA 6s steps(1) infinite}}.glB{{animation:glB 6s steps(1) infinite}}
@keyframes glA{{0%,88%,100%{{opacity:0;transform:none}}89%{{opacity:.8;transform:translate(-5px,2px)}}91%{{opacity:.8;transform:translate(4px,-2px)}}93%{{opacity:0}}96%{{opacity:.7;transform:translate(-3px,0)}}97%{{opacity:0}}}}
@keyframes glB{{0%,88%,100%{{opacity:0;transform:none}}89%{{opacity:.8;transform:translate(5px,-2px)}}91%{{opacity:.8;transform:translate(-4px,2px)}}93%{{opacity:0}}96%{{opacity:.7;transform:translate(3px,1px)}}97%{{opacity:0}}}}
.blob{{animation:blob 12s ease-in-out infinite alternate}}.blob2{{animation-duration:15s;animation-delay:-5s}}
@keyframes blob{{0%{{transform:translate(0,0) scale(1)}}100%{{transform:translate(60px,30px) scale(1.15)}}}}
.blink{{animation:blink 1s steps(1) infinite}}@keyframes blink{{50%{{opacity:0}}}}
.float{{animation:float 6s ease-in-out infinite}}@keyframes float{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-8px)}}}}
.tick{{animation:tick 40s linear infinite}}@keyframes tick{{to{{transform:translateX(-{tick_w:.0f}px)}}}}
.pulse{{animation:pulse 2s ease-in-out infinite}}@keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:.35}}}}
"""
    body = f"""<defs>{frame_defs(W, H)}
  <linearGradient id="name" x1="0" y1="0" x2="600" y2="0" gradientUnits="userSpaceOnUse" spreadMethod="reflect">
    <stop offset="0" stop-color="{CYAN}"/><stop offset=".45" stop-color="{VIOLET}"/><stop offset="1" stop-color="{PINK}"/>
    <animateTransform attributeName="gradientTransform" type="translate" values="0;600;0" dur="8s" repeatCount="indefinite"/>
  </linearGradient>
  <linearGradient id="gridfade" x1="0" y1="{HZ}" x2="0" y2="440" gradientUnits="userSpaceOnUse">
    <stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#fff" stop-opacity="1"/>
  </linearGradient>
  <mask id="gridmask"><rect y="{HZ}" width="{W}" height="{440-HZ}" fill="url(#gridfade)"/></mask>
  <linearGradient id="horizon" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="{CYAN}" stop-opacity="0"/><stop offset=".5" stop-color="{VIOLET}"/><stop offset="1" stop-color="{PINK}" stop-opacity="0"/>
  </linearGradient>
  <linearGradient id="term" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#151a30" stop-opacity=".92"/><stop offset="1" stop-color="#0a0d1a" stop-opacity=".92"/>
  </linearGradient>
</defs>
<g clip-path="url(#frame)">
  <rect width="{W}" height="{H}" fill="url(#bg)"/>
  <g opacity=".5">
    <circle class="blob" cx="220" cy="120" r="170" fill="url(#rviolet)"/>
    <circle class="blob blob2" cx="980" cy="260" r="160" fill="url(#rgo)"/>
    <circle class="blob" cx="640" cy="40" r="110" fill="url(#rpink)" opacity=".6"/>
  </g>
  {stars(W, H, 70, HZ)}
  <g mask="url(#gridmask)" stroke="{VIOLET}" stroke-opacity=".55" stroke-width="1">{vlines}{hlines}</g>
  <rect y="{HZ-1}" width="{W}" height="2" fill="url(#horizon)" filter="url(#glow)"/>

  <text x="96" y="108" font-family="{MONO}" font-size="16" fill="{MUTED}">// hello, world <tspan fill="{VIOLET}">→</tspan> immxrtalbeast</text>
  <text x="94" y="158" font-family="{SANS}" font-size="34" font-weight="500" fill="{TEXT}">Hi, I'm</text>
  <g font-family="{SANS}" font-size="112" font-weight="800" letter-spacing="-3">
    <text class="glA" x="90" y="255" fill="{CYAN}" opacity="0">Filipp</text>
    <text class="glB" x="90" y="255" fill="{PINK}" opacity="0">Filipp</text>
    <text x="90" y="255" fill="url(#name)" filter="url(#glow)">Filipp</text>
  </g>
  <text x="{base_x-26}" y="304" font-family="{MONO}" font-size="{fs}" fill="{VIOLET}">&gt;</text>
  <clipPath id="typeclip"><rect x="{base_x}" y="276" height="40" width="0">
    <animate attributeName="width" values="{wv}" keyTimes="{kt}" dur="{total}s" calcMode="discrete" repeatCount="indefinite"/></rect></clipPath>
  <g clip-path="url(#typeclip)">{''.join(role_texts)}</g>
  <rect x="{base_x+2}" y="282" width="12" height="28" fill="{CYAN}" class="blink">
    <animate attributeName="x" values="{xv}" keyTimes="{kt}" dur="{total}s" calcMode="discrete" repeatCount="indefinite"/></rect>

  <g class="float">
    <rect x="{tx}" y="{ty}" width="{tw}" height="{th}" rx="14" fill="url(#term)" stroke="url(#edge)" stroke-opacity=".7"/>
    <circle cx="{tx+22}" cy="{ty+22}" r="6" fill="#ff5f57"/><circle cx="{tx+42}" cy="{ty+22}" r="6" fill="#febc2e"/><circle cx="{tx+62}" cy="{ty+22}" r="6" fill="#28c840"/>
    <text x="{tx+tw/2}" y="{ty+27}" text-anchor="middle" font-family="{MONO}" font-size="13" fill="{MUTED}">filipp@prod: ~/services</text>
    <line x1="{tx}" x2="{tx+tw}" y1="{ty+42}" y2="{ty+42}" stroke="#ffffff" stroke-opacity=".07"/>
    {''.join(log_svg)}
    <rect x="{tx+22}" y="{cursor_y-14}" width="9" height="18" fill="{LIME}" class="blink"/>
    <circle class="pulse" cx="{tx+tw-26}" cy="{ty+22}" r="4" fill="{LIME}"/>
  </g>

  <rect y="440" width="{W}" height="40" fill="#05060b" fill-opacity=".85"/>
  <line x1="0" x2="{W}" y1="440" y2="440" stroke="url(#horizon)" stroke-opacity=".6"/>
  <g class="tick" font-family="{MONO}" font-size="14" letter-spacing="1">
    <text x="24" y="465" xml:space="preserve">{tick}{tick}{tick}</text>
  </g>
</g>
{frame_border(W, H)}"""
    return svg(W, H, body, style)


# ---------------------------------------------------------------- about (code editor)
def about():
    W, H = 1200, 470
    K, F, S, T, C, N = PINK, "#82aaff", "#c3e88d", "#ffcb6b", "#5c6a8a", TEXT  # keyword func string type comment plain

    def sp(s, c):
        return f'<tspan fill="{c}">{esc(s)}</tspan>'

    lines = [
        sp("package ", K) + sp("main", N),
        "",
        sp("// Filipp — backend engineer who likes boring, fast, observable systems", C),
        sp("type ", K) + sp("Filipp ", T) + sp("struct", K) + sp("{}", N),
        "",
        sp("func ", K) + sp("(Filipp) ", N) + sp("Stack", F) + sp("() []", N) + sp("string ", T) + sp("{", N),
        "    " + sp("return ", K) + sp("[]", N) + sp("string", T) + sp("{", N) + sp('"Go"', S) + sp(", ", N) + sp('"PostgreSQL"', S) + sp(", ", N) + sp('"Kafka"', S) + sp(", ", N) + sp('"Redis"', S) + sp(", ", N) + sp('"Docker"', S) + sp("}", N),
        sp("}", N),
        "",
        sp("func ", K) + sp("(Filipp) ", N) + sp("Into", F) + sp("() []", N) + sp("string ", T) + sp("{", N),
        "    " + sp("return ", K) + sp("[]", N) + sp("string", T) + sp("{", N) + sp('"microservices"', S) + sp(", ", N) + sp('"highload"', S) + sp(", ", N) + sp('"distributed systems"', S) + sp("}", N),
        sp("}", N),
        "",
        sp("func ", K) + sp("(Filipp) ", N) + sp("Learning", F) + sp("() <-", N) + sp("chan ", K) + sp("string ", T) + sp("{ ", N) + sp("// Kubernetes, RabbitMQ, gRPC ...", C),
        "",
        sp("func ", K) + sp("main", F) + sp("() { ", N) + sp("fmt", N) + sp(".", N) + sp("Println", F) + sp("(", N) + sp('"let\'s build something that scales"', S) + sp(") }", N),
    ]
    x0, y0, lh = 110, 104, 21.5
    LOOP = 14
    rows = []
    for i, ln in enumerate(lines):
        t = 0.3 + i * 0.28
        a = t / LOOP
        rows.append(f'<text x="44" y="{y0+i*lh}" text-anchor="end" font-family="{MONO}" font-size="13" fill="#3b4462" transform="translate(30 0)">{i+1}</text>')
        if ln:
            rows.append(
                f'<text x="{x0}" y="{y0+i*lh}" font-family="{MONO}" font-size="15" xml:space="preserve" opacity="0">{ln}'
                f'<animate attributeName="opacity" values="0;0;1;1;0" keyTimes="0;{a:.3f};{a+0.015:.3f};.95;1" dur="{LOOP}s" repeatCount="indefinite"/></text>'
            )
    hl_y = y0 + 15 * lh - 15

    # side panel: "runtime" cards
    px = 830
    cards = [
        ("ROLE", "Backend Developer", CYAN),
        ("LANGUAGE", "Go (mostly) · Python", GO),
        ("FOCUS", "Microservices · Highload", VIOLET),
        ("NOW LEARNING", "Kubernetes · RabbitMQ · gRPC", PINK),
    ]
    card_svg = []
    for i, (k, v, c) in enumerate(cards):
        y = 66 + i * 84
        card_svg.append(
            f'<g class="card" style="animation-delay:{i*0.15:.2f}s">'
            f'<rect x="{px}" y="{y}" width="330" height="70" rx="12" fill="#ffffff" fill-opacity=".03" stroke="{c}" stroke-opacity=".35"/>'
            f'<rect x="{px}" y="{y+14}" width="3" height="42" rx="1.5" fill="{c}"/>'
            f'<text x="{px+22}" y="{y+28}" font-family="{MONO}" font-size="11" letter-spacing="2" fill="{c}">{k}</text>'
            f'<text x="{px+22}" y="{y+52}" font-family="{SANS}" font-size="18" font-weight="600" fill="{TEXT}">{esc(v)}</text></g>'
        )

    style = f"""
.card{{animation:cardin 1s cubic-bezier(.2,.8,.2,1) both}}
@keyframes cardin{{from{{opacity:0;transform:translateX(30px)}}to{{opacity:1;transform:none}}}}
.scan{{animation:scan 7s linear infinite}}@keyframes scan{{from{{transform:translateY(-40px)}}to{{transform:translateY({H}px)}}}}
.blink{{animation:blink 1s steps(1) infinite}}@keyframes blink{{50%{{opacity:0}}}}
"""
    body = f"""<defs>{frame_defs(W, H)}
  <linearGradient id="scanG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{CYAN}" stop-opacity="0"/><stop offset="1" stop-color="{CYAN}" stop-opacity=".08"/></linearGradient>
</defs>
<g clip-path="url(#frame)">
  <rect width="{W}" height="{H}" fill="url(#bg)"/>
  <circle cx="1100" cy="60" r="200" fill="url(#rviolet)" opacity=".12"/>
  <rect width="{W}" height="44" fill="#0a0c18"/>
  <circle cx="24" cy="22" r="6" fill="#ff5f57"/><circle cx="44" cy="22" r="6" fill="#febc2e"/><circle cx="64" cy="22" r="6" fill="#28c840"/>
  <rect x="96" y="8" width="150" height="36" rx="8" fill="{BG1}"/>
  <path transform="translate(110 17) scale(.75)" d="{ICONS['go']}" fill="{GO}"/>
  <text x="140" y="31" font-family="{MONO}" font-size="13" fill="{TEXT}">filipp.go</text>
  <text x="262" y="31" font-family="{MONO}" font-size="13" fill="#3b4462" xml:space="preserve">about.md    stack.yaml</text>
  <text x="{W-24}" y="31" text-anchor="end" font-family="{MONO}" font-size="12" fill="{MUTED}">// about me</text>
  <rect x="0" y="{hl_y}" width="800" height="22" fill="{VIOLET}" fill-opacity=".08"/>
  {''.join(rows)}
  <line x1="800" x2="800" y1="44" y2="{H-30}" stroke="#ffffff" stroke-opacity=".06"/>
  {''.join(card_svg)}
  <rect class="scan" width="{W}" height="40" fill="url(#scanG)"/>
  <rect y="{H-30}" width="{W}" height="30" fill="#0a0c18"/>
  <rect y="{H-30}" width="160" height="30" fill="{VIOLET}" fill-opacity=".85"/>
  <text x="18" y="{H-10}" font-family="{MONO}" font-size="12" font-weight="700" fill="{BG0}">NORMAL</text>
  <text x="180" y="{H-10}" font-family="{MONO}" font-size="12" fill="{MUTED}" xml:space="preserve">main ⎇   go 1.23   utf-8   LF</text>
  <text x="{W-20}" y="{H-10}" text-anchor="end" font-family="{MONO}" font-size="12" fill="{LIME}" xml:space="preserve">● gopls ready   ✓ 0 problems</text>
</g>
{frame_border(W, H)}"""
    return svg(W, H, body, style)


# ---------------------------------------------------------------- tech stack
def stack():
    W = 1200
    groups = [
        ("core", [("go", "Go", GO), ("postgresql", "PostgreSQL", "#4f8fe0"), ("redis", "Redis", "#ff4438"), ("apachekafka", "Kafka", "#cdd3e6"), ("docker", "Docker", "#2496ED")]),
        ("ops & observability", [("linux", "Linux", "#FCC624"), ("prometheus", "Prometheus", "#E6522C"), ("grafana", "Grafana", "#F46800"), ("gitlab", "GitLab CI", "#FC6D26"), ("postman", "Postman", "#FF6C37")]),
        ("leveling up", [("kubernetes", "Kubernetes", "#4f8fe0"), ("rabbitmq", "RabbitMQ", "#FF6600"), (None, "gRPC", "#3fc2c9"), (None, "Sys Design", VIOLET)]),
    ]
    tw, th, gap, x0 = 206, 120, 18, 64
    y = 70
    tiles = []
    n = 0
    for gi, (gname, items) in enumerate(groups):
        learning = gi == 2
        tiles.append(f'<text x="{x0}" y="{y}" font-family="{MONO}" font-size="13" letter-spacing="3" fill="{MUTED}">{esc(gname.upper())}</text>')
        tiles.append(f'<line x1="{x0 + len(gname)*10.2 + 50}" x2="{W-x0}" y1="{y-4}" y2="{y-4}" stroke="#ffffff" stroke-opacity=".07"/>')
        y += 18
        tw = (W - 2 * x0 - gap * (len(items) - 1)) / len(items)
        for i, (ic, label, col) in enumerate(items):
            x = x0 + i * (tw + gap)
            d = n * 0.09
            border = f'stroke="{col}" stroke-opacity=".5" stroke-dasharray="6 6" class="dash"' if learning else f'stroke="{col}" stroke-opacity=".35"'
            glyph = (
                icon(ic, x + 24, y + 26, 40, col)
                if ic
                else f'<text x="{x+44}" y="{y+56}" text-anchor="middle" font-family="{MONO}" font-size="{18 if len(label) < 6 else 26}" font-weight="800" fill="{col}">{"{ }" if label == "Sys Design" else "rpc"}</text>'
            )
            prog = ""
            if learning:
                pw = [0.62, 0.45, 0.55, 0.5][i]
                prog = (
                    f'<rect x="{x+24}" y="{y+96}" width="{tw-48}" height="5" rx="2.5" fill="#ffffff" fill-opacity=".08"/>'
                    f'<rect x="{x+24}" y="{y+96}" width="0" height="5" rx="2.5" fill="{col}">'
                    f'<animate attributeName="width" values="0;{(tw-48)*pw:.0f};{(tw-48)*pw:.0f};0" keyTimes="0;.4;.9;1" dur="6s" begin="{d:.2f}s" repeatCount="indefinite"/></rect>'
                )
            sub = "learning" if learning else ["daily driver", "battle-tested", "in prod"][i % 3]
            tiles.append(
                f'<g class="tile" style="animation-delay:{d:.2f}s"><g class="hov" style="animation-delay:-{n*0.7:.1f}s">'
                f'<rect x="{x}" y="{y}" width="{tw}" height="{th}" rx="16" fill="{col}" fill-opacity=".05" {border}/>'
                f'<circle cx="{x+44}" cy="{y+46}" r="30" fill="{col}" opacity=".14" filter="url(#glow)"/>'
                f"{glyph}"
                f'<text x="{x+84}" y="{y+46}" font-family="{SANS}" font-size="19" font-weight="700" fill="{TEXT}">{esc(label)}</text>'
                f'<text x="{x+84}" y="{y+68}" font-family="{MONO}" font-size="12" fill="{col}" opacity=".85">{sub}</text>'
                f"{prog}</g></g>"
            )
            n += 1
        y += th + 46
    H = y - 20
    style = """
.tile{animation:pop .8s cubic-bezier(.2,1.4,.4,1) both}
@keyframes pop{from{opacity:0;transform:translateY(24px) scale(.96)}to{opacity:1;transform:none}}
.hov{animation:hov 6s ease-in-out infinite}
@keyframes hov{0%,100%{transform:translateY(0)}50%{transform:translateY(-4px)}}
.dash{animation:dash 1.2s linear infinite}@keyframes dash{to{stroke-dashoffset:-24}}
.beam{animation:beam 6s ease-in-out infinite}@keyframes beam{0%{transform:translateX(-400px)}100%{transform:translateX(1600px)}}
"""
    body = f"""<defs>{frame_defs(W, H)}
  <linearGradient id="beamG" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".05"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
</defs>
<g clip-path="url(#frame)">
  <rect width="{W}" height="{H}" fill="url(#bg)"/>
  <circle cx="150" cy="{H-60}" r="200" fill="url(#rgo)" opacity=".12"/>
  <circle cx="1050" cy="80" r="180" fill="url(#rpink)" opacity=".1"/>
  <text x="{W-64}" y="70" text-anchor="end" font-family="{MONO}" font-size="13" fill="{VIOLET}">$ go list -m all | grep filipp</text>
  {''.join(tiles)}
  <rect class="beam" x="0" y="0" width="300" height="{H}" fill="url(#beamG)" transform="skewX(-20)"/>
</g>
{frame_border(W, H)}"""
    return svg(W, H, body, style)


# ---------------------------------------------------------------- architecture
def arch():
    W, H = 1200, 560
    nodes = {
        "client": (110, 280, "client", "web · mobile", None, "#94a3b8"),
        "gw": (330, 280, "api-gateway", "rate-limit · auth", "go", GO),
        "auth": (580, 140, "auth-svc", "gRPC", "go", GO),
        "order": (580, 280, "order-svc", "gRPC", "go", GO),
        "notify": (580, 420, "notify-svc", "consumer", "go", GO),
        "kafka": (835, 280, "kafka", "orders.v1", "apachekafka", "#ffffff"),
        "pg": (1075, 140, "postgres", "primary", "postgresql", "#4f8fe0"),
        "redis": (1075, 420, "redis", "cache · sessions", "redis", "#ff4438"),
    }
    NW, NH = 176, 64

    def edge_pt(a, side):
        x, y = nodes[a][:2]
        hw, hh = (60, 110) if a == "kafka" else (NW / 2, NH / 2)
        return {"r": (x + hw, y), "l": (x - hw, y), "t": (x, y - hh), "b": (x, y + hh)}[side]

    def curve(p, q):
        mx = (p[0] + q[0]) / 2
        return f"M{p[0]:.0f} {p[1]:.0f} C{mx:.0f} {p[1]:.0f} {mx:.0f} {q[1]:.0f} {q[0]:.0f} {q[1]:.0f}"

    edges = [
        ("e1", curve(edge_pt("client", "r"), edge_pt("gw", "l")), CYAN, 1.6, "HTTP"),
        ("e2", curve(edge_pt("gw", "r"), edge_pt("auth", "l")), VIOLET, 2.2, ""),
        ("e3", curve(edge_pt("gw", "r"), edge_pt("order", "l")), VIOLET, 1.8, "gRPC"),
        ("e4", curve(edge_pt("gw", "r"), edge_pt("notify", "l")), VIOLET, 2.6, ""),
        ("e5", curve(edge_pt("order", "r"), edge_pt("kafka", "l")), AMBER, 1.5, "produce"),
        ("e6", f"M{edge_pt('kafka','b')[0]:.0f} {edge_pt('kafka','b')[1]:.0f} C835 420 760 420 {edge_pt('notify','r')[0]:.0f} 420", AMBER, 1.9, "consume"),
        ("e7", f"M{edge_pt('auth','r')[0]:.0f} 140 L{edge_pt('pg','l')[0]:.0f} 140", LIME, 2.4, "SQL"),
        ("e8", curve(edge_pt("kafka", "r"), edge_pt("pg", "l")), LIME, 2.0, ""),
        ("e9", f"M{edge_pt('notify','r')[0]:.0f} 440 L{edge_pt('redis','l')[0]:.0f} 440", PINK, 2.2, "cache"),
    ]
    edge_svg, pkt_svg, lbl_svg = [], [], []
    for i, (eid, d, col, dur, lbl) in enumerate(edges):
        edge_svg.append(f'<path id="{eid}" d="{d}" stroke="{col}" stroke-opacity=".22" stroke-width="2"/>')
        edge_svg.append(f'<path d="{d}" stroke="{col}" stroke-opacity=".7" stroke-width="1.5" stroke-dasharray="4 10" class="flow"/>')
        for k in range(2):
            b = -(dur * k / 2 + i * 0.37)
            pkt_svg.append(
                f'<g><circle r="9" fill="{col}" opacity=".25"/><circle r="4" fill="{col}" filter="url(#glow)"/>'
                f'<animateMotion dur="{dur}s" begin="{b:.2f}s" repeatCount="indefinite" rotate="auto"><mpath href="#{eid}"/></animateMotion></g>'
            )
    labels = {"e1": (220, 266), "e3": (458, 266), "e5": (713, 266), "e6": (735, 402), "e7": (830, 128), "e9": (830, 432)}
    for eid, (lx, ly) in labels.items():
        lbl = next(e[4] for e in edges if e[0] == eid)
        col = next(e[2] for e in edges if e[0] == eid)
        lbl_svg.append(f'<text x="{lx}" y="{ly}" text-anchor="middle" font-family="{MONO}" font-size="11" fill="{col}" opacity=".9">{lbl}</text>')

    node_svg = []
    for i, (key, (x, y, title, sub, ic, col)) in enumerate(nodes.items()):
        if key == "kafka":
            kx, ky, kw, kh = x - 60, y - 110, 120, 220
            parts = []
            for p in range(3):
                py = ky + 58 + p * 50
                parts.append(f'<rect x="{kx+14}" y="{py}" width="{kw-28}" height="34" rx="6" fill="#ffffff" fill-opacity=".04" stroke="#ffffff" stroke-opacity=".1"/>')
                parts.append(f'<text x="{kx+20}" y="{py-4}" font-family="{MONO}" font-size="9" fill="{MUTED}">p{p}</text>')
                for m in range(6):
                    parts.append(
                        f'<rect y="{py+9}" width="10" height="16" rx="2" fill="{AMBER}" opacity=".85">'
                        f'<animate attributeName="x" values="{kx+16};{kx+kw-26}" dur="{2.4+p*0.5:.1f}s" begin="-{m*(2.4+p*0.5)/6:.2f}s" repeatCount="indefinite"/>'
                        f'<animate attributeName="opacity" values="0;.9;.9;0" keyTimes="0;.1;.85;1" dur="{2.4+p*0.5:.1f}s" begin="-{m*(2.4+p*0.5)/6:.2f}s" repeatCount="indefinite"/></rect>'
                    )
            node_svg.append(
                f'<g class="node" style="animation-delay:{i*0.12:.2f}s">'
                f'<rect x="{kx}" y="{ky}" width="{kw}" height="{kh}" rx="16" fill="#0f1326" stroke="{AMBER}" stroke-opacity=".55"/>'
                f'{icon("apachekafka", kx+14, ky+14, 22, "#fff")}'
                f'<text x="{kx+44}" y="{ky+31}" font-family="{SANS}" font-size="15" font-weight="700" fill="{TEXT}">kafka</text>'
                f'<clipPath id="kclip"><rect x="{kx+14}" y="{ky+50}" width="{kw-28}" height="160"/></clipPath>'
                f'<g clip-path="url(#kclip)">{"".join(parts)}</g></g>'
            )
            continue
        nx, ny = x - NW / 2, y - NH / 2
        glyph = icon(ic, nx + 16, ny + 18, 28, col) if ic else f'<circle cx="{nx+30}" cy="{y}" r="9" stroke="{col}" stroke-width="2"/>'
        node_svg.append(
            f'<g class="node" style="animation-delay:{i*0.12:.2f}s">'
            f'<rect x="{nx}" y="{ny}" width="{NW}" height="{NH}" rx="14" fill="#0f1326" stroke="{col}" stroke-opacity=".5"/>'
            f'<rect class="halo" style="animation-delay:-{i*0.5:.1f}s" x="{nx}" y="{ny}" width="{NW}" height="{NH}" rx="14" stroke="{col}" stroke-width="2"/>'
            f"{glyph}"
            f'<text x="{nx+56}" y="{y-3}" font-family="{SANS}" font-size="15" font-weight="700" fill="{TEXT}">{title}</text>'
            f'<text x="{nx+56}" y="{y+15}" font-family="{MONO}" font-size="11" fill="{MUTED}">{sub}</text>'
            f'<circle class="pulse" style="animation-delay:-{i*0.3:.1f}s" cx="{nx+NW-14}" cy="{ny+14}" r="3.5" fill="{LIME}"/></g>'
        )

    # observability strip with a live-ish latency sparkline
    pts = []
    for k in range(60):
        v = 14 + 8 * math.sin(k / 4) + random.uniform(-5, 5) + (16 if k in (37, 38) else 0)
        pts.append((k * 6.4, 40 - v))
    spark = "M" + " L".join(f"{x:.0f} {y:.1f}" for x, y in pts)

    style = """
.flow{animation:flow 1s linear infinite}@keyframes flow{to{stroke-dashoffset:-14}}
.node{animation:nin .9s cubic-bezier(.2,1.3,.4,1) both}@keyframes nin{from{opacity:0;transform:scale(.9)}to{opacity:1;transform:none}}
.node{transform-box:fill-box;transform-origin:center}
.halo{animation:halo 3s ease-out infinite;transform-box:fill-box;transform-origin:center}
@keyframes halo{0%{opacity:.6;transform:scale(1)}100%{opacity:0;transform:scale(1.12,1.35)}}
.pulse{animation:pulse 1.6s ease-in-out infinite}@keyframes pulse{0%,100%{opacity:1}50%{opacity:.25}}
.spark{stroke-dasharray:900;animation:draw 6s linear infinite}@keyframes draw{from{stroke-dashoffset:900}to{stroke-dashoffset:0}}
"""
    body = f"""<defs>{frame_defs(W, H)}
  <pattern id="dots" width="24" height="24" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1" fill="#ffffff" fill-opacity=".06"/></pattern>
  <linearGradient id="sparkfill" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{LIME}" stop-opacity=".25"/><stop offset="1" stop-color="{LIME}" stop-opacity="0"/></linearGradient>
</defs>
<g clip-path="url(#frame)">
  <rect width="{W}" height="{H}" fill="url(#bg)"/>
  <rect width="{W}" height="{H}" fill="url(#dots)"/>
  <circle cx="600" cy="280" r="220" fill="url(#rviolet)" opacity=".1"/>
  <text x="40" y="52" font-family="{MONO}" font-size="13" fill="{VIOLET}">// what I build</text>
  <text x="40" y="82" font-family="{SANS}" font-size="24" font-weight="800" fill="{TEXT}">request lifecycle, end to end</text>
  <g font-family="{MONO}" font-size="12" fill="{MUTED}">
    <circle cx="{W-420}" cy="58" r="4" fill="{CYAN}"/><text x="{W-410}" y="62">http</text>
    <circle cx="{W-350}" cy="58" r="4" fill="{VIOLET}"/><text x="{W-340}" y="62">grpc</text>
    <circle cx="{W-280}" cy="58" r="4" fill="{AMBER}"/><text x="{W-270}" y="62">events</text>
    <circle cx="{W-196}" cy="58" r="4" fill="{LIME}"/><text x="{W-186}" y="62">sql</text>
    <circle cx="{W-134}" cy="58" r="4" fill="{PINK}"/><text x="{W-124}" y="62">cache</text>
  </g>
  {''.join(edge_svg)}
  {''.join(lbl_svg)}
  {''.join(pkt_svg)}
  {''.join(node_svg)}

  <g transform="translate(40 488)">
    <rect width="{W-80}" height="52" rx="12" fill="#ffffff" fill-opacity=".025" stroke="#ffffff" stroke-opacity=".07"/>
    {icon("prometheus", 18, 14, 24, "#E6522C")}
    {icon("grafana", 50, 14, 24, "#F46800")}
    <text x="88" y="31" font-family="{MONO}" font-size="13" fill="{TEXT}">observability <tspan fill="{MUTED}">· every hop is traced, measured and alerted</tspan></text>
    <g transform="translate({W-80-560} 6)">
      <path d="{spark} L378 40 L0 40 Z" fill="url(#sparkfill)"/>
      <path class="spark" d="{spark}" stroke="{LIME}" stroke-width="1.6"/>
    </g>
    <text x="{W-100}" y="22" text-anchor="end" font-family="{MONO}" font-size="11" fill="{MUTED}">p99 latency</text>
    <text x="{W-100}" y="40" text-anchor="end" font-family="{MONO}" font-size="15" font-weight="700" fill="{LIME}">7.2ms</text>
  </g>
</g>
{frame_border(W, H)}"""
    return svg(W, H, body, style)


# ---------------------------------------------------------------- section header
def header(name, title, sub, color):
    W, H = 1200, 76
    style = """.ln{stroke-dasharray:1200;animation:ln 2.4s cubic-bezier(.6,0,.2,1) both}@keyframes ln{from{stroke-dashoffset:1200}to{stroke-dashoffset:0}}
.dot{animation:dot 2s ease-in-out infinite}@keyframes dot{50%{opacity:.3}}"""
    tx = 50 + len(title) * 15
    body = f"""<defs><linearGradient id="hl" x1="44" y1="0" x2="{W}" y2="0" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="{color}"/><stop offset="1" stop-color="{color}" stop-opacity="0"/></linearGradient></defs>
  <circle class="dot" cx="18" cy="38" r="6" fill="{color}"/><circle cx="18" cy="38" r="12" stroke="{color}" stroke-opacity=".4"/>
  <text x="44" y="48" font-family="{SANS}" font-size="28" font-weight="800" fill="{color}">{esc(title)}</text>
  <text x="{tx+20}" y="47" font-family="{MONO}" font-size="14" fill="#8b93ad">{esc(sub)}</text>
  <path class="ln" d="M44 64 H{W}" stroke="url(#hl)" stroke-width="2"/>"""
    (OUT / f"h-{name}.svg").write_text(svg(W, H, body, style))


# ---------------------------------------------------------------- footer
def footer():
    W, H = 1200, 240

    def wave(amp, ph, y):
        pts = [f"{x} {y + amp*math.sin(x/120 + ph):.1f}" for x in range(0, 2401, 40)]
        return "M" + " L".join(pts) + f" L2400 {H} L0 {H} Z"

    style = """.w1{animation:wv 9s linear infinite}.w2{animation:wv 13s linear infinite reverse}.w3{animation:wv 7s linear infinite}
@keyframes wv{from{transform:translateX(0)}to{transform:translateX(-754px)}}
.blink{animation:blink 1s steps(1) infinite}@keyframes blink{50%{opacity:0}}"""
    body = f"""<defs>{frame_defs(W, H)}
  <linearGradient id="wg" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{CYAN}"/><stop offset=".5" stop-color="{VIOLET}"/><stop offset="1" stop-color="{PINK}"/></linearGradient>
</defs>
<g clip-path="url(#frame)">
  <rect width="{W}" height="{H}" fill="url(#bg)"/>
  {stars(W, H, 40, 150)}
  <path class="w1" d="{wave(10, 0, 168)}" fill="url(#wg)" opacity=".18"/>
  <path class="w2" d="{wave(14, 2, 182)}" fill="url(#wg)" opacity=".22"/>
  <path class="w3" d="{wave(8, 4, 198)}" fill="url(#wg)" opacity=".35"/>
  <text x="600" y="78" text-anchor="middle" font-family="{SANS}" font-size="38" font-weight="800" fill="{TEXT}">Let's build something that <tspan fill="url(#wg)">scales</tspan>.</text>
  <text x="600" y="118" text-anchor="middle" font-family="{MONO}" font-size="16" fill="{MUTED}">ping me on telegram <tspan fill="{CYAN}">@c0dys</tspan> — usually faster than p99<tspan class="blink" fill="{CYAN}">_</tspan></text>
</g>
{frame_border(W, H)}"""
    return svg(W, H, body, style + STAR_CSS)


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    (OUT / "hero.svg").write_text(hero())
    (OUT / "about.svg").write_text(about())
    (OUT / "stack.svg").write_text(stack())
    (OUT / "arch.svg").write_text(arch())
    (OUT / "footer.svg").write_text(footer())
    header("about", "About", "whoami --verbose", CYAN)
    header("stack", "Tech Stack", "tools I ship with", VIOLET)
    header("arch", "How I Build", "event-driven, observable, boring in prod", AMBER)
    header("stats", "Activity", "commits, streaks & coding time", LIME)
    print("ok:", sorted(p.name for p in OUT.glob("*.svg")))
