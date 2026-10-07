# -*- coding: utf-8 -*-
"""build_article_charts.py - the five article charts (HTML -> PNG at 2x via headless Chrome), all numbers from
outputs/results.json. Run after model.py."""
import json, os, subprocess, statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "outputs", "charts")
os.makedirs(OUT, exist_ok=True)
R = json.load(open(os.path.join(HERE, "outputs", "results.json"), encoding="utf-8"))
C = {c["case"]: c for c in R["cases"]}
c8, c70, cB = C["Llama 3.1 8B"], C["Llama 3.3 70B"], C["Llama 3.3 70B on next-gen B200"]
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
INK, MUTED, BRONZE, SAGE, SLATE, STONE, LINE = "#191816", "#5E5A52", "#8A6F4E", "#5F7A68", "#7C8794", "#F2EFE9", "rgba(25,24,22,.14)"

HEAD = """<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<style>html,body{margin:0}body{width:1200px;height:%dpx;background:%s;color:%s;font-family:Inter,'Segoe UI',sans-serif;-webkit-font-smoothing:antialiased;box-sizing:border-box;padding:54px 72px}
.k{font-size:13px;font-weight:600;letter-spacing:.26em;text-transform:uppercase;color:%s;margin-bottom:14px}
h1{font-family:'Instrument Serif',Georgia,serif;font-weight:400;font-size:54px;line-height:1.02;letter-spacing:-.015em;margin:0 0 10px}
h1 i{color:#6E5A40}.sub{font-size:19px;color:%s;margin-bottom:34px}
.src{position:absolute;left:72px;bottom:30px;font-size:13px;color:#8C877D}
.num{font-family:'Instrument Serif',Georgia,serif}
</style></head><body>"""


def page(h, body):
    return HEAD % (h, STONE, INK, BRONZE, MUTED) + body + "</body></html>"


def render(name, html, h):
    p = os.path.join(OUT, name + ".html")
    open(p, "w", encoding="utf-8").write(html)
    png = os.path.join(OUT, name + ".png")
    subprocess.run([CHROME, "--headless", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=2",
                    "--virtual-time-budget=8000", "--window-size=1200,%d" % h, "--screenshot=" + png,
                    "file:///" + p.replace("\\", "/").replace(" ", "%20")], capture_output=True)
    print("rendered", png)


SRC = "Source: Tolu Oladuji's AI inference economics model, public prices and NVIDIA / MLPerf benchmarks, 6 Oct 2026."

# 1. Same GPU, three prices
g = R["gpu"]["H100"]
tiers = [("Small clouds &amp; marketplaces", g["small_cloud_median"], c70["tiers"]["Small-cloud / marketplace median"]["cost_per_1m_output"], SAGE),
         ("Larger GPU clouds", g["gpu_cloud_median"], c70["tiers"]["GPU-cloud median"]["cost_per_1m_output"], BRONZE),
         ("Hyperscalers on demand", g["hyperscaler_median"], c70["tiers"]["Hyperscaler median"]["cost_per_1m_output"], INK)]
mx = max(t[1] for t in tiers)
rows = "".join("""<div style="display:grid;grid-template-columns:300px 1fr 190px;align-items:center;gap:22px;margin-bottom:26px">
<div style="font-size:19px;font-weight:500">%s</div>
<div style="height:46px;background:rgba(25,24,22,.06)"><div style="height:100%%;width:%.1f%%;background:%s;display:flex;align-items:center;justify-content:flex-end;padding-right:14px;box-sizing:border-box;color:#fff;font-size:20px;font-weight:600">$%.2f/hr</div></div>
<div><span class="num" style="font-size:38px">$%.2f</span><div style="font-size:14px;color:%s">per 1M tokens, Llama 70B</div></div></div>""" % (n, 100 * v / mx, col, v, c, MUTED) for n, v, c, col in tiers)
render("01-same-gpu-three-prices", page(560, """<div class="k">Where you rent matters</div><h1>Same GPU, <i>three very different prices</i></h1>
<div class="sub">Median on-demand price of an NVIDIA H100, and what it does to the cost of serving Llama 3.3 70B (60%% utilisation)</div>%s
<div class="src">%s</div>""" % (rows, SRC)), 560)

# 2. Margins at list price
hosts = ["Together AI", "Fireworks AI", "Amazon Bedrock"]
def gm(case, h): return next(x for x in case["hosts"] if x["host"] == h)["gross_margin"] * 100
bars = ""
for label, case in (("Llama 3.1 8B", c8), ("Llama 3.3 70B", c70)):
    bars += '<div style="margin-bottom:22px"><div style="font-size:17px;font-weight:600;margin-bottom:10px">%s</div>' % label
    for h, col in zip(hosts, (INK, BRONZE, SAGE)):
        v = gm(case, h)
        bars += """<div style="display:grid;grid-template-columns:170px 1fr;align-items:center;gap:18px;margin-bottom:8px"><div style="font-size:16px;color:%s">%s</div>
<div style="height:30px;background:rgba(25,24,22,.06)"><div style="height:100%%;width:%.1f%%;background:%s;display:flex;align-items:center;justify-content:flex-end;padding-right:10px;box-sizing:border-box;color:#fff;font-size:15px;font-weight:600">%.0f%%</div></div></div>""" % (MUTED, h.replace("Amazon ", ""), v, col, v)
    bars += "</div>"
be = [next(x for x in c70["hosts"] if x["host"] == h)["breakeven_util"] * 100 for h in hosts]
render("02-margins-at-list-price", page(640, """<div class="k">If you fill the GPUs</div><h1>Healthy margins, <i>low break-even</i></h1>
<div class="sub">Implied compute gross margin at list price: H100s at the GPU-cloud median rate, 60%% busy</div><div style="width:760px">%s</div>
<div style="position:absolute;right:72px;top:250px;width:260px;border-left:1px solid %s;padding-left:24px"><div class="num" style="font-size:64px;line-height:1">%.0f&ndash;%.0f%%</div><div style="font-size:16px;color:%s;margin-top:8px">GPU utilisation needed to break even on Llama 3.3 70B</div></div>
<div class="src">%s</div>""" % (bars, LINE, min(be), max(be), MUTED, SRC)), 640)

# 3. One model, 21 prices
SEGCOL = {"hyperscaler / big cloud": INK, "custom chips": BRONZE, "major independent host": SLATE, "long-tail independent host": SAGE}
SEGLAB = {"hyperscaler / big cloud": "Big clouds", "custom chips": "Custom chips", "major independent host": "Major independent hosts", "long-tail independent host": "Smaller independent hosts"}
oss = sorted([x for x in R["market_offers"] if x["model"] == "gpt-oss-120b"], key=lambda x: x["output_price"])
lo, hi = 0.0, 1.0
dots = ""
stack = {}
for i, x in enumerate(oss):
    left = 100 * (x["output_price"] - lo) / (hi - lo)
    key = round(x["output_price"] / 0.02)          # offers within ~2 cents share a column and stack upward
    lvl = stack.get(key, 0); stack[key] = lvl + 1
    dots += '<div title="%s" style="position:absolute;left:calc(%.2f%% - 9px);top:%dpx;width:18px;height:18px;border-radius:50%%;background:%s;border:2px solid %s"></div>' % (
        x["provider"], left, 178 - lvl * 24, SEGCOL[x["segment"]], STONE)
ticks = "".join('<div style="position:absolute;left:%d%%;top:208px;transform:translateX(-50%%);font-size:15px;color:%s">$%.2f</div><div style="position:absolute;left:%d%%;top:0;height:200px;border-left:1px dashed %s"></div>' % (
    t, MUTED, t / 100, t, LINE) for t in (0, 25, 50, 75, 100))
legend = "".join('<span style="display:inline-flex;align-items:center;gap:8px;margin-right:26px;font-size:16px"><i style="width:14px;height:14px;border-radius:50%%;background:%s;display:inline-block"></i>%s</span>' % (SEGCOL[k], SEGLAB[k]) for k in SEGCOL)
mn, mxp = oss[0]["output_price"], oss[-1]["output_price"]
render("03-one-model-21-prices", page(600, """<div class="k">A price range, not a price</div><h1>One model, <i>%d prices</i></h1>
<div class="sub">gpt-oss-120b output price per 1M tokens, every provider offer on OpenRouter</div>
<div style="position:relative;height:236px;margin:20px 10px 30px">%s%s</div><div>%s</div>
<div style="position:absolute;right:72px;top:62px;text-align:right"><div class="num" style="font-size:64px;line-height:1">%.1f&times;</div><div style="font-size:16px;color:%s">spread, $%.2f to $%.2f</div></div>
<div class="src">%s</div>""" % (len(oss), ticks, dots, legend, mxp / mn, MUTED, mn, mxp, SRC)), 600)

# 4. Newer chips, cheaper tokens
h1c, b2c = c70["tiers"]["GPU-cloud median"], cB["tiers"]["GPU-cloud median"]
drop = 100 * (1 - b2c["cost_per_1m_output"] / h1c["cost_per_1m_output"])
def col(title, gph, cost, color):
    return """<div style="flex:1;border-top:4px solid %s;padding-top:22px"><div style="font-size:20px;font-weight:600">%s</div>
<div style="font-size:17px;color:%s;margin:6px 0 26px">rents for $%.2f an hour</div><div class="num" style="font-size:96px;line-height:1">$%.2f</div>
<div style="font-size:17px;color:%s;margin-top:8px">per 1M tokens to serve Llama 3.3 70B</div></div>""" % (color, title, MUTED, gph, cost, MUTED)
render("04-newer-chips-cheaper-tokens", page(540, """<div class="k">The hardware roadmap is a margin roadmap</div><h1>Pricier chip, <i>cheaper tokens</i></h1>
<div class="sub">The B200 costs more per hour, but serves so many more tokens that each token is %.0f%% cheaper</div>
<div style="display:flex;gap:64px;margin-top:10px">%s%s</div><div class="src">%s</div>""" % (
    drop, col("NVIDIA H100 (FP8)", h1c["usd_per_gpu_hour"], h1c["cost_per_1m_output"], BRONZE),
    col("NVIDIA B200 (FP4)", b2c["usd_per_gpu_hour"], b2c["cost_per_1m_output"], SAGE), SRC)), 540)

# 5. How the tracker updates itself
steps = [("Every Monday", "GitHub Actions starts the run"), ("Fetch", "Live prices from public data feeds"),
         ("Snapshot", "A dated copy of every price"), ("Compare", "Logs each price change vs last week"),
         ("Rebuild", "Model, Excel, charts and web page")]
boxes = ""
for i, (a, b) in enumerate(steps):
    boxes += """<div style="flex:1;background:#fff;border:1px solid %s;padding:22px 18px;min-height:150px;box-sizing:border-box">
<div class="num" style="font-size:40px;color:%s;line-height:1">%d</div><div style="font-size:19px;font-weight:600;margin:12px 0 6px">%s</div><div style="font-size:15px;color:%s;line-height:1.35">%s</div></div>""" % (LINE, BRONZE, i + 1, a, MUTED, b)
    if i < len(steps) - 1:
        boxes += '<div style="align-self:center;font-size:26px;color:%s">&rarr;</div>' % BRONZE
render("05-how-it-updates-itself", page(470, """<div class="k">Automation</div><h1>A tracker that <i>updates itself</i></h1>
<div class="sub">No manual steps: the whole pipeline runs on a schedule and leaves an audit trail</div>
<div style="display:flex;gap:12px">%s</div><div class="src">github.com/oladujitolu-ai/ai-inference-economics</div>""" % boxes), 470)
