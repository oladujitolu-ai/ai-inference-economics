# -*- coding: utf-8 -*-
"""refresh.py - one command that keeps the project current.

    python refresh.py

  1. FETCH     live per-provider prices from OpenRouter's public API for every model in MODELS
  2. SNAPSHOT  saves the raw responses under data/snapshots/<date>/ (an audit trail of every run)
  3. CHANGES   compares each provider's price with the previous snapshot and appends any move to data/price_changes.csv
  4. REBUILD   regenerates data/openrouter_prices.csv, re-runs model.py, build_article_charts.py and build_site.py (Excel, charts, README, web page)
  5. LOG       appends a one-line summary to data/refresh_log.csv

Runs weekly on GitHub Actions (.github/workflows/refresh.yml) and can be run by hand at any time.
Sources without a public feed (NVIDIA benchmark tables, some GPU price pages) stay as dated, manually cited inputs.
Standard library only (plus openpyxl for the model).
"""
import csv, datetime as dt, json, os, shutil, subprocess, sys, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
MODELS = ["meta-llama/llama-3.1-8b-instruct", "meta-llama/llama-3.3-70b-instruct", "openai/gpt-oss-120b"]
TODAY = dt.date.today().isoformat()


def fetch(slug):
    req = urllib.request.Request("https://openrouter.ai/api/v1/models/%s/endpoints" % slug,
                                 headers={"User-Agent": "ai-inference-economics/1.0 (research project)"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


def offers(payload):
    out = {}
    for e in payload.get("data", {}).get("endpoints", []):
        pr = e.get("pricing", {})
        out[(e.get("provider_name"), e.get("quantization") or "")] = (round(float(pr.get("prompt", 0)) * 1e6, 4),
                                                                      round(float(pr.get("completion", 0)) * 1e6, 4))
    return out


def main():
    snap_dir = os.path.join(DATA, "snapshots", TODAY)
    os.makedirs(snap_dir, exist_ok=True)
    prev_dirs = sorted(d for d in os.listdir(os.path.join(DATA, "snapshots")) if d < TODAY)
    prev_dir = os.path.join(DATA, "snapshots", prev_dirs[-1]) if prev_dirs else None
    changes, n_offers, failed = [], 0, []
    for slug in MODELS:
        fname = "openrouter_%s.json" % slug.replace("/", "_")
        try:
            payload = fetch(slug)
        except Exception as e:  # keep the last good file; report the failure
            failed.append("%s (%s)" % (slug, e))
            continue
        json.dump(payload, open(os.path.join(snap_dir, fname), "w", encoding="utf-8"), indent=1)
        shutil.copy(os.path.join(snap_dir, fname), os.path.join(DATA, fname))
        now = offers(payload); n_offers += len(now)
        if prev_dir and os.path.exists(os.path.join(prev_dir, fname)):
            before = offers(json.load(open(os.path.join(prev_dir, fname), encoding="utf-8")))
            for k, (i, o) in now.items():
                if k not in before:
                    changes.append([TODAY, slug, k[0], k[1], "", "", i, o, "new offer"])
                elif before[k] != (i, o):
                    changes.append([TODAY, slug, k[0], k[1], before[k][0], before[k][1], i, o, "price change"])
            for k in before:
                if k not in now:
                    changes.append([TODAY, slug, k[0], k[1], before[k][0], before[k][1], "", "", "offer removed"])
    pc = os.path.join(DATA, "price_changes.csv")
    new_file = not os.path.exists(pc)
    with open(pc, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new_file:
            w.writerow(["date", "model", "provider", "quantization", "old_input", "old_output", "new_input", "new_output", "event"])
        w.writerows(changes)
    for script in (os.path.join(DATA, "openrouter_to_csv.py"), os.path.join(HERE, "model.py"), os.path.join(HERE, "build_article_charts.py"), os.path.join(HERE, "build_site.py")):
        subprocess.run([sys.executable, script], check=True, cwd=os.path.dirname(script), stdout=subprocess.DEVNULL)
    log = os.path.join(DATA, "refresh_log.csv")
    new_log = not os.path.exists(log)
    with open(log, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new_log:
            w.writerow(["date", "models", "offers_fetched", "price_events", "failed"])
        w.writerow([TODAY, len(MODELS), n_offers, len(changes), "; ".join(failed)])
    print("refresh %s: %d offers fetched, %d price events, %d failures" % (TODAY, n_offers, len(changes), len(failed)))
    for c in changes:
        print("  ", c)


if __name__ == "__main__":
    main()
