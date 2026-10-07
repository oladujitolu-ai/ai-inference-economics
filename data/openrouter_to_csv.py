# -*- coding: utf-8 -*-
"""Turns the OpenRouter per-model endpoint lists (public API, retrieved 2026-10-06) into openrouter_prices.csv:
one row per provider offer, with the provider's segment. Prices are what each provider charges through OpenRouter."""
import csv, glob, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
SEG = {
    # large clouds / hyperscalers selling inference
    "Amazon Bedrock": "hyperscaler / big cloud", "Google": "hyperscaler / big cloud", "Cloudflare": "hyperscaler / big cloud",
    "CoreWeave": "hyperscaler / big cloud", "DigitalOcean": "hyperscaler / big cloud",
    # custom-chip companies
    "Groq": "custom chips", "SambaNova": "custom chips", "Cerebras": "custom chips",
    # the established independent inference hosts
    "Together": "major independent host", "Fireworks": "major independent host", "DeepInfra": "major independent host", "BaseTen": "major independent host",
}
MODELS = {"meta-llama_llama-3.1-8b-instruct": ("Llama 3.1 8B", "meta-llama/llama-3.1-8b-instruct"),
          "meta-llama_llama-3.3-70b-instruct": ("Llama 3.3 70B", "meta-llama/llama-3.3-70b-instruct"),
          "openai_gpt-oss-120b": ("gpt-oss-120b", "openai/gpt-oss-120b")}
rows, seen = [], set()
for p in sorted(glob.glob(os.path.join(HERE, "openrouter_*.json"))):
    key = os.path.basename(p)[len("openrouter_"):-5]
    model, slug = MODELS[key]
    for e in json.load(open(p, encoding="utf-8"))["data"]["endpoints"]:
        pr = e.get("pricing", {})
        i, o = round(float(pr.get("prompt", 0)) * 1e6, 4), round(float(pr.get("completion", 0)) * 1e6, 4)
        prov = e.get("provider_name")
        k = (model, prov, i, o, e.get("quantization"))
        if k in seen:          # OpenRouter lists some providers twice (two regions / endpoints at the same price)
            continue
        seen.add(k)
        rows.append({"model": model, "provider": prov, "segment": SEG.get(prov, "long-tail independent host"),
                     "quantization": e.get("quantization") or "", "input_usd_per_1m_tokens": i, "output_usd_per_1m_tokens": o,
                     "context_length": e.get("context_length"), "source_url": "https://openrouter.ai/api/v1/models/%s/endpoints" % slug,
                     "retrieved_date": "2026-10-06"})
with open(os.path.join(HERE, "openrouter_prices.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
print(len(rows), "rows")
for r in rows:
    print(r["model"], "|", r["provider"], "|", r["segment"], "|", r["input_usd_per_1m_tokens"], "/", r["output_usd_per_1m_tokens"], "|", r["quantization"])
