# -*- coding: utf-8 -*-
"""build_site.py - writes README.md and index.html (GitHub Pages) from outputs/results.json, so every number on the
page is the model's number. Run after model.py (refresh.py runs both)."""
import json, os, statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
R = json.load(open(os.path.join(HERE, "outputs", "results.json"), encoding="utf-8"))
C = {c["case"]: c for c in R["cases"]}
c8, c70, cB, cM = C["Llama 3.1 8B"], C["Llama 3.3 70B"], C["Llama 3.3 70B on next-gen B200"], C["gpt-oss-120b (MoE)"]
U = int(R["base_utilisation"] * 100)
MK, SEGS = R.get("market_offers", []), R.get("segment_summary", [])
GPU = R["gpu"]
SM, GC, HS = "Small-cloud / marketplace median", "GPU-cloud median", "Hyperscaler median"


def host(case, name):
    return next(h for h in case["hosts"] if h["host"] == name)


def rng(case, hosts, key):
    v = [host(case, h)[key] * 100 for h in hosts]
    return "%.0f-%.0f%%" % (min(v), max(v))


def seg(model, segment):
    return next((s for s in SEGS if s["model"] == model and s["segment"] == segment), None)


MAIN = ["Together AI", "Fireworks AI", "Amazon Bedrock"]
cost = lambda c, t=GC: c["tiers"][t]["cost_per_1m_output"]
gph = lambda c, t: c["tiers"][t]["usd_per_gpu_hour"]
closed = R["closed_model_prices"]
cin = [x["input"] for x in closed]; cout = [x["output"] for x in closed]

# long tail on Llama 3.3 70B: costed on small-cloud H100, then on small-cloud B200
lt70 = [x for x in MK if x["model"] == "Llama 3.3 70B" and x["segment"] == "long-tail independent host"]
b200_cost_req = cost(cB, SM) * 1000 / 1e6
lt70_b200 = [1 - b200_cost_req / ((1000 * x["input_price"] + 1000 * x["output_price"]) / 1e6) for x in lt70]
oss = [x for x in MK if x["model"] == "gpt-oss-120b"]
providers = sorted({x["provider"] for x in MK})

F = {
 "U": U, "c8": "$%.2f" % cost(c8), "c70": "$%.2f" % cost(c70), "ratio": "%.0f" % (cost(c70) / cost(c8)),
 "h100_sm": "$%.2f" % GPU["H100"]["small_cloud_median"], "n_sm": len(GPU["H100"]["small_clouds"]),
 "h100_gc": "$%.2f" % GPU["H100"]["gpu_cloud_median"], "h100_hs": "$%.2f" % GPU["H100"]["hyperscaler_median"],
 "c70_hs": "$%.2f" % cost(c70, HS), "gm8": rng(c8, MAIN, "gross_margin"), "gm70": rng(c70, MAIN, "gross_margin"),
 "be70": rng(c70, MAIN, "breakeven_util"), "b200_gph": "$%.2f" % gph(cB, GC), "cB": "$%.2f" % cost(cB),
 "b200_drop": "%.0f%%" % (100 * (1 - cost(cB) / cost(c70))), "gmB": rng(cB, MAIN, "gross_margin"),
 "di70": "%.0f%%" % (100 * host(c70, "DeepInfra")["breakeven_util"]),
 "cM": "$%.2f" % cost(cM), "gmM": "%.0f%%" % (100 * host(cM, "Together AI")["gross_margin"]),
 "cin": "$%.2f-$%.0f" % (min(cin), max(cin)), "cout": "$%.2f-$%.0f" % (min(cout), max(cout)), "spread": "%.0f" % (max(cout) / min(cout)),
 "n_prov": len(providers), "n_off": len(MK),
 "lt70_med": "$%.2f" % seg("Llama 3.3 70B", "long-tail independent host")["median_output_price"],
 "big70_med": "$%.2f" % seg("Llama 3.3 70B", "hyperscaler / big cloud")["median_output_price"],
 "lt70_n": len(lt70), "lt70_b200": "%.0f-%.0f%%" % (100 * min(lt70_b200), 100 * max(lt70_b200)),
 "oss_n": len(oss), "oss_min": "$%.2f" % min(x["output_price"] for x in oss), "oss_max": "$%.2f" % max(x["output_price"] for x in oss),
 "oss_x": "%.1f" % (max(x["output_price"] for x in oss) / min(x["output_price"] for x in oss)),
 "oss_lt_med": "$%.2f" % seg("gpt-oss-120b", "long-tail independent host")["median_output_price"],
 "oss_chip_med": "$%.2f" % seg("gpt-oss-120b", "custom chips")["median_output_price"],
}

FINDINGS = [
 ("Model size drives cost.", "On a rented H100 at the GPU-cloud median rate (%(h100_gc)s an hour) and %(U)s%% utilisation, serving costs about %(c8)s per million output tokens for Llama 3.1 8B and %(c70)s for Llama 3.3 70B: roughly %(ratio)sx more for the larger model." % F),
 ("Where you rent matters as much as what you serve.", "The same H100 rents for a median %(h100_sm)s an hour across %(n_sm)s small GPU clouds and marketplaces, %(h100_gc)s at the larger GPU clouds and %(h100_hs)s on demand at AWS, Google Cloud and Azure. At the hyperscaler rate the 70B model costs %(c70_hs)s per million output tokens, above every host's list price, so nobody selling at these prices is renting hyperscaler capacity on demand." % F),
 ("At list prices the economics work, if you fill the GPUs.", "A host renting GPU-cloud H100s at %(U)s%% utilisation would earn implied compute gross margins of %(gm8)s on Llama 3.1 8B and %(gm70)s on Llama 3.3 70B at Together AI, Fireworks AI and Amazon Bedrock list prices. Break-even utilisation for 70B is only %(be70)s, so the risk is idle capacity, not price." % F),
 ("The long tail competes below big-host prices, and only new hardware makes that pay.", "Across %(n_prov)s providers and %(n_off)s offers on OpenRouter, smaller independent hosts price Llama 3.3 70B at a median %(lt70_med)s per million output tokens, against %(big70_med)s at the big clouds. At those prices all %(lt70_n)s long-tail offers are below cost on rented H100s, even at small-cloud rates; on B200-class GPUs the same prices earn %(lt70_b200)s. For small players, hardware generation is the business model." % F),
 ("Next-generation hardware resets the cost curve.", "On a B200 running FP4, 70B serving falls to %(cB)s per million output tokens, %(b200_drop)s cheaper than on H100, even though the B200 rents for more (%(b200_gph)s an hour). Implied margins at the big hosts' prices rise to %(gmB)s." % F),
 ("Open models have a price range, not a price.", "gpt-oss-120b has %(oss_n)s offers ranging from %(oss_min)s to %(oss_max)s per million output tokens, a %(oss_x)sx spread. The big hosts cluster at $0.60, the long tail undercuts them (median %(oss_lt_med)s), and custom-chip providers charge the most (median %(oss_chip_med)s), likely a premium for speed." % F),
 ("Some prices sit below rented-GPU cost.", "DeepInfra's Llama 3.3 70B Turbo price would need %(di70)s utilisation of rented H100s to break even, which is impossible. That points to owned or contracted capacity, more aggressive optimisation (the Turbo variants are not defined on the pricing page), or market-share pricing." % F),
 ("Closed models price on value, not cost.", "Published prices for OpenAI, Anthropic and Google models span %(cin)s per million input tokens and %(cout)s per million output tokens, a %(spread)sx spread at the output price." % F),
]

ROWS = []
for c in (c8, c70, cB, cM):
    for h in c["hosts"]:
        ROWS.append((c["case"], h["host"], h["host_model"], "$%.3f / $%.3f" % (h["input_price"], h["output_price"]),
                     "%.0f%%" % (100 * h["gross_margin"]), "%.0f%%" % (100 * h["breakeven_util"])))
SEGROWS = [(s["model"], s["segment"], str(s["offers"]), "$%.2f" % s["median_output_price"],
            "$%.2f-$%.2f" % (s["min_output_price"], s["max_output_price"]), "%.0f%%" % (100 * s["median_gross_margin"]),
            str(s["offers_below_cost"])) for s in SEGS]

AUTOMATION = ("The project updates itself. One command (`python refresh.py`) pulls live per-provider prices from OpenRouter's public API, "
              "saves a dated snapshot, logs every price change against the previous run, then re-runs the model and rebuilds the Excel file, "
              "charts, this README and the web page. A GitHub Actions workflow runs it every Monday, so the numbers here stay current without "
              "manual work. Sources without a public feed (NVIDIA benchmark tables and some GPU price pages) stay as dated, cited inputs.")

LIMITS = [
 "Compute only: the margins exclude staff, networking, storage, idle reserve capacity and sales costs, so true operating margins are lower.",
 "Throughput is NVIDIA TensorRT-LLM / MLPerf offline maximum-load output throughput, a ceiling. The utilisation assumption (base %(U)s%%, tested 30-90%%) stands in for latency targets and uneven demand." % F,
 "GPU prices are on-demand list prices on 6 Oct 2026 (US regions where stated; two European clouds converted at the ECB rate). Hosts often pay less through reserved or owned capacity, so real margins can be higher than shown. Marketplace prices are live snapshots (median listing, never the lowest).",
 "The margins show what a host renting GPUs at list price would earn at each host's price. They are not any company's reported margins: Groq, SambaNova and Cerebras run their own chips, and several hosts may own hardware.",
 "OpenRouter prices are what each provider charges through OpenRouter, which can differ from its direct price. Providers are grouped into segments by judgement (see data/openrouter_to_csv.py).",
 "Fireworks lists Llama-class models under size-based tiers ($0.20 for 4-16B, $0.90 for dense models above 16B), used as its price for those models. gpt-oss-120b's benchmark does not state input/output lengths, so it is compared on output price only, which understates the margin.",
]

LEDE = ("A fully sourced, self-updating model of LLM inference unit economics. It combines GPU rental prices from %d providers (hyperscalers, GPU clouds, "
        "small clouds and marketplaces), published serving benchmarks and API list prices from big and small hosts, then works out the cost to "
        "serve a request, each host's implied gross margin and the GPU utilisation needed to break even." % (
            len({g[0] for g in R["gpu"]["H100"]["gpu_clouds"] + R["gpu"]["H100"]["hyperscalers"] + R["gpu"]["H100"]["small_clouds"]})))

README = ["# AI inference economics: what it costs to serve an open LLM, and what hosts earn", "",
          "**Tolu Oladuji** | October 2026 | [LinkedIn](https://www.linkedin.com/in/oladuji-tolulope/) | [Web version](https://oladujitolu-ai.github.io/ai-inference-economics/)", "",
          LEDE + " Every input is public and cited; see [`data/SOURCES.md`](data/SOURCES.md).", "", "## Key findings", ""]
README += ["%d. **%s** %s" % (i, t, b) for i, (t, b) in enumerate(FINDINGS, 1)]
README += ["", "![Implied gross margin by host](outputs/gross_margin_by_host.svg)", "", "![Llama 3.3 70B cost per 1M tokens](outputs/cost_per_1m_tokens_70b.svg)", "",
           "## The whole market: big and small providers", "", "Every offer on OpenRouter for the same three models, costed on small-cloud / marketplace GPUs (the cheapest realistic rented capacity) at %d%% utilisation." % U, "",
           "| Model | Segment | Offers | Median $/1M out | Range | Median implied margin | Offers below cost |", "|---|---|---|---|---|---|---|"]
README += ["| %s |" % " | ".join(r) for r in SEGROWS]
README += ["", "## Implied margins at the major hosts' list prices", "", "GPU-cloud median rate, %d%% utilisation. Requests of 1,000 input + 1,000 output tokens, except gpt-oss-120b (output only)." % U, "",
           "| Model | Host | Host's model | List price $/1M (in / out) | Implied gross margin | Break-even utilisation |", "|---|---|---|---|---|---|"]
README += ["| %s |" % " | ".join(r) for r in ROWS]
README += ["", "## How it stays current", "", AUTOMATION, "", "## Method", "",
           "- **Serving cost per request** = GPU $/hour / (output tokens per second per GPU x 3,600 x utilisation) x output tokens",
           "- **List price per request** = input tokens x input price + output tokens x output price",
           "- **Implied gross margin** = 1 - serving cost / list price; **break-even utilisation** = utilisation at which cost equals price",
           "- **GPU price tiers:** small GPU clouds and marketplaces, larger GPU clouds (Lambda, CoreWeave, RunPod, Together AI) and hyperscalers (AWS, Google Cloud, Azure), on-demand, one quote per provider.",
           "", "## Limitations", ""] + ["- " + l for l in LIMITS] + [
           "", "## Run it", "", "```", "pip install openpyxl", "python refresh.py     # fetch live prices, rebuild everything", "python model.py       # or just re-run the model on the saved data", "```", "",
           "## Repository", "", "- `data/`: input tables, live-price snapshots, price-change log and `SOURCES.md`",
           "- `refresh.py`: the weekly refresh pipeline; `.github/workflows/refresh.yml`: the schedule",
           "- `model.py`: the model; `build_site.py`: builds this README and the web page from the results",
           "- `outputs/`: Excel model, results and charts", "", "Preview-card photo: data center via [Unsplash](https://unsplash.com/s/photos/server-room?license=free) (Unsplash License).", ""]
open(os.path.join(HERE, "README.md"), "w", encoding="utf-8", newline="\n").write("\n".join(README))

svg1 = open(os.path.join(HERE, "outputs", "gross_margin_by_host.svg"), encoding="utf-8").read()
svg2 = open(os.path.join(HERE, "outputs", "cost_per_1m_tokens_70b.svg"), encoding="utf-8").read()
cards = "".join("<li><h3>%s</h3> <p>%s</p></li>" % (t, b) for t, b in FINDINGS)
trow = lambda rows: "".join("<tr>%s</tr>" % "".join("<td>%s</td>" % x for x in r) for r in rows)
lim = "".join("<li>%s</li>" % l for l in LIMITS)
HTML = open(os.path.join(HERE, "site_template.html"), encoding="utf-8").read()
for k, v in {"{{LEDE}}": LEDE, "{{CARDS}}": cards, "{{SVG1}}": svg1, "{{SVG2}}": svg2, "{{SEGROWS}}": trow(SEGROWS), "{{ROWS}}": trow(ROWS),
             "{{LIM}}": lim, "{{AUTOMATION}}": AUTOMATION.replace("`python refresh.py`", "<code>python refresh.py</code>"),
             "{{K1}}": F["c70"], "{{K2}}": F["h100_sm"] + " vs " + F["h100_hs"], "{{K3}}": F["gm70"], "{{K4}}": F["oss_x"] + "x", "{{U}}": str(U)}.items():
    HTML = HTML.replace(k, v)
open(os.path.join(HERE, "index.html"), "w", encoding="utf-8", newline="\n").write(HTML)
json.dump(F, open(os.path.join(HERE, "outputs", "headline_numbers.json"), "w", encoding="utf-8"), indent=1)
print("README.md and index.html written")
for t, b in FINDINGS:
    print("-", t, b)
