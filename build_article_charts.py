# -*- coding: utf-8 -*-
"""build_article_charts.py - the five article charts (HTML -> PNG at 2x via headless Chrome), all numbers from
outputs/results.json. Run after model.py.

Style (7 Oct 2026 redesign): plain white chart, the cover's type (Inter Tight headlines, Inter labels, JetBrains Mono
for figures and the source line), one amber accent for the point of each chart, greys for everything else, thin rules,
no rounded cards. Drawn at 900px wide with large type so the labels stay readable on a phone."""
import json, os, subprocess, shutil, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "outputs", "charts")
os.makedirs(OUT, exist_ok=True)
R = json.load(open(os.path.join(HERE, "outputs", "results.json"), encoding="utf-8"))
C = {c["case"]: c for c in R["cases"]}
c8, c70, cB = C["Llama 3.1 8B"], C["Llama 3.3 70B"], C["Llama 3.3 70B on next-gen B200"]
CHROME = os.environ.get("CHROME") or shutil.which("google-chrome") or shutil.which("chromium") or shutil.which("chromium-browser") \
    or r"C:\Program Files\Google\Chrome\Application\chrome.exe"   # Windows locally, google-chrome on the GitHub runner
PROFILE = tempfile.mkdtemp(prefix="chart-render-")

W = 900
INK, BODY, MUTED, RULE, GRID = "#111111", "#3D3D3D", "#767676", "#111111", "#E6E6E6"
AMBER, DARK, MID, LIGHT = "#C98A2B", "#2E2E2E", "#8C8C8C", "#C9C9C9"

HEAD = """<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Inter+Tight:wght@600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@500;600&display=swap" rel="stylesheet">
<style>html,body{margin:0}
body{width:%dpx;height:%dpx;background:#fff;color:%s;font-family:Inter,'Segoe UI',Arial,sans-serif;-webkit-font-smoothing:antialiased;box-sizing:border-box;padding:40px 44px 0;position:relative;font-variant-numeric:tabular-nums}
.top{border-top:3px solid %s;padding-top:22px}
h1{font-family:'Inter Tight',Inter,sans-serif;font-weight:700;font-size:40px;line-height:1.08;letter-spacing:-.02em;margin:0 0 10px;color:%s}
.sub{font-size:21px;line-height:1.35;color:%s;margin:0 0 30px;max-width:780px}
.mono{font-family:'JetBrains Mono',ui-monospace,monospace}
.src{position:absolute;left:44px;right:44px;bottom:24px;font-family:'JetBrains Mono',monospace;font-size:14px;color:%s;border-top:1px solid %s;padding-top:12px}
.lab{font-size:21px;color:%s}
</style></head><body><div class="top">"""

SRC = "*1M tokens = roughly 750,000 words. Sources: public chip and AI prices, NVIDIA, MLPerf."


def page(h, body, src=SRC):
    return HEAD % (W, h, INK, RULE, INK, BODY, MUTED, GRID, BODY) + body + '</div><div class="src">%s</div></body></html>' % src


def render(name, html, h):
    p = os.path.join(OUT, name + ".html")
    open(p, "w", encoding="utf-8").write(html)
    png = os.path.join(OUT, name + ".png")
    subprocess.run([CHROME, "--headless=new", "--no-sandbox", "--user-data-dir=" + PROFILE, "--disable-gpu", "--hide-scrollbars",
                    "--force-device-scale-factor=2", "--virtual-time-budget=8000", "--window-size=%d,%d" % (W, h), "--screenshot=" + png,
                    ("file:///" + p.replace("\\", "/").lstrip("/")).replace(" ", "%20")], capture_output=True)
    print("rendered", png)


def hbar(pct, color, label="", h=34):
    """One horizontal bar, value printed just past the end of the bar."""
    txt = ('<span class="mono" style="position:absolute;left:calc(%.1f%% + 10px);top:50%%;transform:translateY(-50%%);font-size:20px;font-weight:600;color:%s">%s</span>'
           % (pct, INK, label)) if label else ""
    return ('<div style="position:relative;height:%dpx"><div style="position:absolute;left:0;top:0;bottom:0;width:%.1f%%;background:%s"></div>%s</div>'
            % (h, pct, color, txt))


# 1. Same GPU, three prices --------------------------------------------------------------------------------------
g = R["gpu"]["H100"]
tiers = [("Small clouds and marketplaces", g["small_cloud_median"], c70["tiers"]["Small-cloud / marketplace median"]["cost_per_1m_output"], MID),
         ("Larger GPU clouds", g["gpu_cloud_median"], c70["tiers"]["GPU-cloud median"]["cost_per_1m_output"], MID),
         ("AWS, Google Cloud, Microsoft Azure", g["hyperscaler_median"], c70["tiers"]["Hyperscaler median"]["cost_per_1m_output"], AMBER)]
mx = max(t[1] for t in tiers) * 1.18
head = ('<div style="display:grid;grid-template-columns:1fr 210px;gap:24px;font-size:16px;font-weight:600;color:%s;margin-bottom:4px">'
        '<div>Rent per hour (typical price)</div><div style="text-align:right">Cost per 1M tokens*</div></div>' % MUTED)
rows = "".join("""<div style="display:grid;grid-template-columns:1fr 210px;gap:24px;align-items:end;padding:14px 0;border-bottom:1px solid %s">
<div><div class="lab" style="margin-bottom:8px;font-weight:500;color:%s">%s</div>%s</div>
<div class="mono" style="text-align:right;font-size:30px;font-weight:600;color:%s;line-height:34px">$%.2f</div></div>""" % (
    GRID, INK, n, hbar(100 * v / mx, col, "$%.2f" % v), AMBER if col == AMBER else INK, c) for n, v, c, col in tiers)
render("01-same-gpu-three-prices", page(620, """<h1>Same chip, three very different prices</h1>
<p class="sub">What it costs to rent NVIDIA's H100 chip for an hour, and what that does to the cost of an AI answer</p>%s%s""" % (head, rows)), 620)

# 2. Margins at list price ---------------------------------------------------------------------------------------
hosts = ["Together AI", "Fireworks AI", "Amazon Bedrock"]
def host(case, h): return next(x for x in case["hosts"] if x["host"] == h)
legend = ('<div style="display:flex;gap:28px;font-size:18px;color:%s;margin-bottom:18px">'
          '<span style="display:inline-flex;align-items:center;gap:8px"><i style="width:14px;height:14px;background:%s;display:inline-block"></i>Small model (Llama 3.1 8B)</span>'
          '<span style="display:inline-flex;align-items:center;gap:8px"><i style="width:14px;height:14px;background:%s;display:inline-block"></i>Bigger model (Llama 3.3 70B)</span></div>' % (BODY, LIGHT, AMBER))
bars = ""
for hname in hosts:
    a, b = host(c8, hname)["gross_margin"] * 100, host(c70, hname)["gross_margin"] * 100
    bars += """<div style="display:grid;grid-template-columns:190px 1fr;gap:18px;align-items:center;padding:12px 0;border-bottom:1px solid %s">
<div class="lab" style="font-weight:500;color:%s">%s</div><div style="display:flex;flex-direction:column;gap:6px">%s%s</div></div>""" % (
        GRID, INK, hname, hbar(a, LIGHT, "%.0f%%" % a, 26), hbar(b, AMBER, "%.0f%%" % b, 26))
be = [host(c70, h)["breakeven_util"] * 100 for h in hosts]
render("02-margins-at-list-price", page(620, """<h1>Keep the chips busy and the business works</h1>
<p class="sub">Share of every dollar a company keeps after paying for the chips, at its public price, with the chips busy 60%% of the time</p>%s
<div style="display:grid;grid-template-columns:1fr 200px;gap:34px">
<div>%s</div>
<div style="border-left:3px solid %s;padding-left:18px;align-self:start"><div class="mono" style="font-size:40px;font-weight:600;line-height:1;color:%s">%.0f&ndash;%.0f%%</div>
<div style="font-size:18px;line-height:1.35;color:%s;margin-top:10px">how busy the chips must be just to break even on the bigger model</div></div></div>""" % (
    legend, bars, AMBER, INK, min(be), max(be), BODY)), 620)

# 3. One model, 21 prices ----------------------------------------------------------------------------------------
SEGCOL = {"hyperscaler / big cloud": DARK, "custom chips": AMBER, "major independent host": MID, "long-tail independent host": LIGHT}
SEGLAB = {"hyperscaler / big cloud": "Big clouds", "custom chips": "Custom-chip companies", "major independent host": "Larger independent companies", "long-tail independent host": "Smaller companies"}
oss = sorted([x for x in R["market_offers"] if x["model"] == "gpt-oss-120b"], key=lambda x: x["output_price"])
lo, hi = 0.0, 1.0
dots, placed = "", []
for x in oss:
    left = 100 * (x["output_price"] - lo) / (hi - lo)
    lvl = 0                                         # exact x; a dot moves up a level only when it would touch another
    while any(l == lvl and abs(px - x["output_price"]) < 0.031 for px, l in placed):
        lvl += 1
    placed.append((x["output_price"], lvl))
    dots += '<div style="position:absolute;left:calc(%.2f%% - 11px);bottom:%dpx;width:22px;height:22px;border-radius:50%%;background:%s;box-shadow:0 0 0 2px #fff"></div>' % (
        left, 6 + lvl * 26, SEGCOL[x["segment"]])
ticks = "".join('<div style="position:absolute;left:%d%%;top:0;bottom:0;border-left:1px solid %s"></div><div class="mono" style="position:absolute;left:%d%%;bottom:-32px;transform:translateX(-50%%);font-size:16px;color:%s">$%.2f</div>' % (
    t, GRID, t, MUTED, t / 100) for t in (0, 25, 50, 75, 100))
legend = "".join('<span style="display:inline-flex;align-items:center;gap:8px;font-size:18px;color:%s"><i style="width:14px;height:14px;border-radius:50%%;background:%s;display:inline-block"></i>%s</span>' % (BODY, SEGCOL[k], SEGLAB[k]) for k in SEGCOL)
mn, mxp = oss[0]["output_price"], oss[-1]["output_price"]
render("03-one-model-21-prices", page(640, """<h1>Same model, %d different prices</h1>
<p class="sub">What each company charges per 1M tokens* for gpt-oss-120b, a free-to-use OpenAI model. The most expensive is <b style="color:%s">%.1f times</b> the cheapest.</p>
<div style="display:flex;flex-wrap:wrap;gap:10px 26px;margin-bottom:26px">%s</div>
<div style="position:relative;height:230px;margin:0 14px 0;border-bottom:1px solid %s">%s%s</div>""" % (
    len(oss), INK, mxp / mn, legend, INK, ticks, dots)), 640)

# 4. Newer chips, cheaper tokens ---------------------------------------------------------------------------------
h1c, b2c = c70["tiers"]["GPU-cloud median"], cB["tiers"]["GPU-cloud median"]
drop = 100 * (1 - b2c["cost_per_1m_output"] / h1c["cost_per_1m_output"])
def group(title, rows, mxv):
    out = '<div style="padding:16px 0;border-bottom:1px solid %s"><div class="lab" style="font-weight:600;color:%s;margin-bottom:12px">%s</div>' % (GRID, INK, title)
    for name, v, col in rows:
        out += '<div style="display:grid;grid-template-columns:200px 1fr;gap:16px;align-items:center;margin-bottom:8px"><div style="font-size:19px;color:%s">%s</div>%s</div>' % (
            BODY, name, hbar(100 * v / mxv, col, "$%.2f" % v, 30))
    return out + "</div>"
render("04-newer-chips-cheaper-tokens", page(600, """<h1>A pricier chip, %.0f%% cheaper tokens</h1>
<p class="sub">NVIDIA's newer B200 costs more to rent, but it works so much faster that each answer costs less</p>%s%s""" % (
    drop,
    group("Rent per hour", [("NVIDIA H100", h1c["usd_per_gpu_hour"], LIGHT), ("NVIDIA B200", b2c["usd_per_gpu_hour"], LIGHT)], b2c["usd_per_gpu_hour"] * 1.2),
    group("Cost per 1M tokens* (Llama 3.3 70B)", [("NVIDIA H100", h1c["cost_per_1m_output"], DARK), ("NVIDIA B200", b2c["cost_per_1m_output"], AMBER)], h1c["cost_per_1m_output"] * 1.2))), 600)

# 5. How the tracker updates itself ------------------------------------------------------------------------------
steps = [("Monday", "The run starts on its own"), ("Fetch", "Live prices pulled from a public data feed"),
         ("Snapshot", "A dated copy of every price is saved"), ("Compare", "Every price change against last week is logged"),
         ("Rebuild", "Model, Excel file, charts and web page")]
cells = "".join("""<div style="border-top:3px solid %s;padding-top:14px"><div class="mono" style="font-size:18px;font-weight:600;color:%s">%02d</div>
<div style="font-family:'Inter Tight',Inter,sans-serif;font-size:23px;font-weight:700;margin:6px 0 6px;color:%s">%s</div><div style="font-size:17px;line-height:1.35;color:%s">%s</div></div>""" % (
    AMBER if i == 0 else INK, AMBER if i == 0 else MUTED, i + 1, INK, a, BODY, b) for i, (a, b) in enumerate(steps))
render("05-how-it-updates-itself", page(480, """<h1>It updates itself every Monday</h1>
<p class="sub">Nobody has to touch it: it fetches new prices, keeps a dated record and rebuilds everything on its own</p>
<div style="display:grid;grid-template-columns:repeat(5,1fr);gap:18px">%s</div>""" % cells,
    "github.com/oladujitolu-ai/ai-inference-economics"), 480)
