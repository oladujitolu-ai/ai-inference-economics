# Sources: AI inference economics data

Everything here was read on **2026-10-06**. Each number in the three CSVs comes from a page or official data feed that was opened that day. Nothing was estimated. A field is left blank when the source does not state the value.

Derived values (each one is a simple division):
- `gpu_rental.csv` `usd_per_gpu_hour` = `usd_per_hour_per_unit / gpus_per_unit`. For Lambda the page gives a per-GPU price, so `usd_per_hour_per_unit` = 8 x that price.
- `throughput_benchmarks.csv` `throughput_tokens_per_sec_per_gpu` = total / `num_gpus`.
- `params_billion` for open models is taken from the model name (for example "70B" or "397B-A17B" gives total parameters) or from the host page (Groq states 120B for gpt-oss-120b). It is left blank when neither states it (DeepSeek V4/V3.1/R1, Kimi K3, Llama 4 Maverick, Mixtral).

## api_prices.csv: API list prices (USD per 1M tokens, standard tier)

| URL | What was taken | Notes |
|---|---|---|
| https://developers.openai.com/api/docs/pricing (Markdown copy at `.../pricing.md`) | Standard-tier short-context input/output for gpt-6-astra, gpt-6.1-sol, gpt-6-luna, gpt-5.5, gpt-5.4-mini; long-context prices go in notes | Short context means 272K input tokens or fewer. Regional/data-residency endpoints cost 10% more. GPT-5.6 Sol is on promotional pricing until at least 21 Nov 2026 and is not used here. |
| https://platform.claude.com/docs/en/about-claude/pricing (docs.claude.com redirects here) | Base input/output for Claude Fable 5.1, Opus 5.5, Sonnet 5.5, Haiku 4.5 | Claude 4.7 and later use a tokenizer that produces about 30% more tokens for the same text, so per-token prices do not compare directly with other vendors. `inference_geo: "us"` costs 1.1x. Mythos is invitation-only and is excluded. |
| https://ai.google.dev/gemini-api/docs/pricing (Markdown copy at `.../pricing.md.txt`) | Paid-tier Standard input/output for Gemini 3.1 Pro Preview, 3.8 Flash, 3.5 Flash, 3.5 Flash-Lite | Gemini 3.8 Flash's $0.75/$3.75 ends on 2026-12-31 and becomes $1.50/$7.50 on 2027-01-01. 3.1 Pro is priced for prompts of 200k tokens or fewer; above that it is $4/$18. Output prices include thinking tokens. |
| https://www.together.ai/pricing | Serverless input/output prices for open models. Also the GPU Clusters H100/H200/B200 per-GPU-hour prices used in gpu_rental | The rendered page was checked: the "Batch API price" toggle is off by default, so these are standard prices. Kimi K3 is marked PROMO. |
| https://docs.fireworks.ai/serverless/pricing (linked from fireworks.ai/pricing) | Standard serverless prices for gpt-oss-120b, DeepSeek V4.1 Flash, Kimi K3; size-based tier prices (4B-16B: $0.20; >16B dense: $0.90) | The size-based tiers cover any model "not listed individually". The page does not confirm that Llama 3.1 8B or 3.3 70B are deployed serverless right now. US-region variants cost 1.5x. |
| https://deepinfra.com/pricing | Input/output prices for Llama 3.1 8B / 3.3 70B Turbo, Qwen, DeepSeek, Kimi, Gemma. Also the dedicated H100 price used in gpu_rental | The page does not say how "Turbo" variants are quantized. Priority tier is 1.5x and Flex is 0.8x; the standard tier is used here. |
| https://console.groq.com/docs/models (groq.com/pricing redirects to the homepage, which shows no prices) | gpt-oss-120b $0.15/$0.60, gpt-oss-20b $0.075/$0.30; Llama 3.1 8B and 3.3 70B are listed as "Contact Sales" | The Llama rows are kept with blank prices. |
| https://aws.amazon.com/bedrock/pricing/ | Llama 3.1 8B, Llama 3.3 70B, gpt-oss-120b/20b, Qwen3 235B A22B, DeepSeek-V3.1, Gemma 4 31B | The page loads its prices through JavaScript from AWS's own feed, `https://b0.p.awsstatic.com/pricing/2.0/meteredUnitMaps/bedrock/USD/current/bedrock.json` (published 2026-10-03). Values are per-1K x 1000 for the us-east-1/us-east-2/us-west-2 entries. The method was checked visually: Llama 3.3 70B shows $0.72/$0.72 on the rendered page (US East (Ohio)), and the feed matches the page's static Sydney table (for example gpt-oss-120b $0.1545 = $0.15 x 1.03). Qwen3 235B and DeepSeek-V3.1 are not in us-east-1, so their values come from Oregon/Ohio. |

## gpu_rental.csv: GPU rental list prices

| URL | What was taken | Notes |
|---|---|---|
| https://aws.amazon.com/ec2/pricing/on-demand/ via the feed `https://b0.p.awsstatic.com/pricing/2.0/meteredUnitMaps/ec2/USD/current/ec2-ondemand-without-sec-sel/US%20East%20(N.%20Virginia)/Linux/index.json` (also checked for Ohio and Oregon) | Linux on-demand $/hr: p5.48xlarge $55.04, p5.4xlarge $6.88, p5en.48xlarge $63.296, p6-b200.48xlarge $113.9328 | Same price in all three US regions. The feed is dated 2026-09-25. |
| https://aws.amazon.com/ec2/instance-types/p5/ and https://aws.amazon.com/ec2/instance-types/p6/ | GPU counts: p5.48xlarge = 8 H100, p5.4xlarge = 1 H100, p5en.48xlarge = 8 H200, p6-b200.48xlarge = 8 B200 | |
| https://cloud.google.com/products/compute/pricing/accelerator-optimized (the old /compute/gpus-pricing and /compute/vm-instance-pricing URLs redirect toward it) | Prices for a3-highgpu-8g, a3-megagpu-8g, a3-ultragpu-8g; spot price for a3-highgpu-8g | Read from the rendered table cells in us-central1 (Iowa). Prices bundle vCPU, RAM and local SSD. a4-highgpu-8g (B200) shows N/A for on-demand, so it is excluded. |
| https://prices.azure.com/api/retail/prices (Azure Retail Prices API, public and official), filter `armRegionName eq 'eastus'` | Standard_ND96isr_H100_v5: Linux pay-as-you-go $98.32/hr, spot $18.169536/hr | The Azure pricing web page itself is rendered by JavaScript. 1-year and 3-year reservation prices are also in the API but are not used here. |
| https://learn.microsoft.com/en-us/azure/virtual-machines/sizes/gpu-accelerated/ndh100v5-series | ND96isr_H100_v5 has 8x H100 80GB | |
| https://lambda.ai/pricing | Per-GPU-hour prices for 8x/4x/2x/1x H100 SXM and B200 instances, plus 1-Click Cluster prices | Prices exclude sales tax/VAT. |
| https://www.coreweave.com/pricing | 8-GPU instance $/hr: HGX H100 $49.24 (spot $19.71), HGX H200 $50.44, HGX B200 $68.80 | The page has two tables whose H200/B200 spot prices differ slightly; both appear in notes. |
| https://www.runpod.io/pricing | Pods per-GPU $/hr from HTML `data-secure` / `data-community` attributes: H100 SXM $3.49/$2.69, H100 PCIe $2.89/$1.99, H200 $4.59/$3.59, B200 $6.79/$5.98 | Secure Cloud is the page default and is used. Community Cloud prices are in notes. |
| https://www.together.ai/pricing | GPU Clusters per-GPU-hour: H100 $3.99 on-demand / $1.99 preemptible / $3.19 reserved (91-180 days); H200 $5.99; B200 $8.19 | |
| https://deepinfra.com/pricing | Dedicated H100 $2.20/GPU-hour | This is managed model serving, not a bare VM. |
| https://fireworks.ai/pricing | On-demand deployment H100 $8.00/hr | Managed serving, not a bare VM. Region-restricted deployments cost 1.5x. |

## throughput_benchmarks.csv: aggregate serving throughput

| URL | What was taken | Notes |
|---|---|---|
| https://nvidia.github.io/TensorRT-LLM/performance/perf-overview.html | "Total Output Throughput (tokens/sec)" at maximum offline load: Llama 3.1 8B FP8 (H100 and H200, TP1), Llama 3.3 70B FP8 (H100 and H200, TP2), Llama 3.3 70B FP4 (B200, TP1), Llama 3.1 405B FP8 (H100, TP8), Llama 4 Maverick FP8 (H100 and H200, TP8). Request counts per ISL/OSL come from the page | Docs version 1.1.0rc5, page last updated 2025-09-15, data from TRT-LLM v0.21. Requests are synthetic and fixed-length. The figures are totals across the TP group; per-GPU figures are computed. NVIDIA says the numbers are reference points, not peak. Tables were parsed from the HTML cells so that empty cells are not shifted. |
| https://raw.githubusercontent.com/mlcommons/inference_results_v5.1/main/summary_results.json | MLPerf Inference v5.1 closed, available systems: Cisco 16xH100 llama2-70b Offline/Server and llama3.1-405b Offline; RedHat 1xH100 (vLLM) llama3.1-8b Offline/Server; Dell 8xH200 llama2-70b Offline/Server/Interactive; HPE 8xH200 llama3.1-8b Offline and mixtral-8x7b Offline | Each row's results folder is linked in its notes. |
| https://raw.githubusercontent.com/mlcommons/inference_results_v6.0/main/summary_results.json | RedHat 8xH200 (LLM-D) gpt-oss-120b Offline 28,680 tok/s | |
| https://raw.githubusercontent.com/mlcommons/inference_results_v6.1/main/summary.csv | CoreWeave 8xB200 llama2-70b-99.9, deepseek-r1, gpt-oss-120b Offline | The v6.1 repo was created 2026-09-14. It has no H100 LLM results. |
| https://github.com/mlcommons/inference_policies/blob/master/inference_rules.adoc | Datasets, sample counts, reference output tokens per sample (llama2-70b 294.45; 405B 684.68; Mixtral 144.84), max_new_tokens, Server/Interactive TTFT/TPOT limits | This is the current master. The limits may have been tweaked between rounds. |
| https://github.com/mlcommons/inference/blob/master/language/llama2-70b/README.md | Shows that the token count LoadGen uses is the output-token count each response reports | This supports reading MLPerf "Tokens/s" as output tokens/sec. |
| https://lmsys.org/blog/2025-05-05-large-scale-ep/ | SGLang DeepSeek-V3 on H100: decode 22,282 tok/s per 8-GPU node (9 decode nodes, EP72, batch 256, 2,000-token KV); headline 52.3k input + 22.3k output tok/s per node on 12 nodes | Prefill was measured on separate nodes and assumed unlimited, so the per-GPU decode figure leaves out the prefill GPUs. The page does not state precision. |
| https://mlcommons.org/benchmarks/inference-datacenter/ | Opened for metric definitions. It has none and points to inference_rules.adoc | No data taken. |

## Caveats

1. **Prices vary by region and tier.** AWS/Bedrock figures are US regions, GCP is us-central1 and Azure is East US. Fireworks charges 1.5x for US-region or region-restricted use. OpenAI, Anthropic and Bedrock regional endpoints cost 10% more. Several prices are promotional or due to change (Gemini 3.8 Flash until 2026-12-31; Together Kimi K3 PROMO; OpenAI GPT-5.6 Sol promo, which is excluded).
2. **GPU "units" are not the same product.** Hyperscaler prices (AWS, GCP, Azure) bundle CPUs, RAM, local NVMe and InfiniBand in an 8-GPU node. Lambda, RunPod and Together price per GPU. DeepInfra and Fireworks GPU-hours are managed serving deployments, not bare VMs. Some rows are H100 PCIe/NVL rather than SXM, and the `gpu` column shows which.
3. **Benchmarks depend heavily on sequence length and precision.** TRT-LLM 8B on one H100 ranges from 26,401 tok/s (128 in / 128 out) to 1,341 tok/s (20,000 in / 2,000 out). The TRT-LLM and MLPerf rows use FP8 on Hopper and FP4 on Blackwell. Hosts' "Turbo"/FP8 variants may be quantized differently. TRT-LLM uses synthetic fixed-length random tokens, while MLPerf uses real datasets with variable lengths.
4. **Offline throughput is a ceiling.** TRT-LLM and MLPerf Offline runs have no latency limit. MLPerf Server/Interactive rows show the drop under latency limits; for example Dell 8xH200 llama2-70b gives 35,317 Offline, 33,244 Server and 21,916 Interactive. MLPerf models are Llama 2 70B and Llama 3.1 8B, while hosts serve Llama 3.3 70B / 3.1 8B. These share an architecture but have different tokenizers and context lengths.
5. **Per-token prices are not fully comparable across vendors.** Tokenizers differ (Anthropic notes about 30% more tokens on Claude 4.7+), and Google and OpenAI bill reasoning ("thinking") tokens as output.

## Not found or left blank

- Groq per-token prices for Llama 3.1 8B and Llama 3.3 70B ("Contact Sales").
- Public serverless prices for Llama 3.x on Fireworks as named models. Only the size-based tier is published.
- A single-node 8xH100 MLPerf v5.1/v6.x result for llama2-70b or llama3.1-8b with TensorRT. The only H100 LLM results are Cisco's 2- and 4-node systems and RedHat's 1-GPU vLLM run. There are also no H100 results for DeepSeek-R1 or gpt-oss-120b in v6.0/v6.1, so the H100 MoE coverage is the SGLang DeepSeek-V3 blog and TRT-LLM Llama 4 Maverick.
- NVIDIA NIM benchmarking tables: the old docs URL returns 404.
- Total parameter counts for DeepSeek V4/V3.1/R1, Kimi K3, Llama 4 Maverick and Mixtral 8x7B were not on any page opened.
- GCP B200 (a4-highgpu-8g) on-demand price (N/A on page), Azure H200 on-demand (no East US H200 SKU returned by the API), and CoreWeave/Lambda reserved prices ("contact sales").

## Small and long-tail GPU clouds (gpu_rental_small.csv)

All pages and APIs were opened on 2026-10-06. Prices are USD per hour excl. tax unless noted. `usd_per_gpu_hour` = unit price / `gpus_per_unit`. The `segment` column is "marketplace" (aggregated or peer supply) or "small GPU cloud". On-demand is the main row for each provider. Reserved, spot and interruptible rows are included only where the page clearly lists them. Raw API snapshots (Vast.ai, Shadeform, Vultr) were saved to the session scratchpad, not to this folder.

| URL | What was taken | Caveats (region, term, what is bundled) |
|---|---|---|
| https://console.vast.ai/api/v0/bundles/ | Live public search API, one query per gpu_name ("H100 SXM", "H100 PCIE", "H100 NVL", "H200", "B200"), filtered to rentable=true, rented=false, type=on-demand. Per-GPU price = dph_total / num_gpus, deduped to the lowest offer per machine. Recorded the **lowest** and **median** across machines (two rows per GPU). | A live snapshot taken around 21:00 ET; it changes minute to minute. Supply was thin: 8 H100 SXM machines, 5 PCIe, 6 NVL, 4 H200, 9 B200. Hosts are worldwide and a mix of verified and unverified. dph_total includes the default-disk storage charge; bandwidth is extra. The offer-level (non-deduped) median is in the notes. H200 NVL is a separate gpu_name and was left out. |
| https://api.shadeform.ai/v1/instances/types | Public API (no key). hourly_price in cents / num_gpus. Lowest and median per-GPU price across the underlying clouds (deduped to the lowest config per cloud) for H100 SXM, H100 PCIe/NVL, H200 and B200. | These are Shadeform's list prices and can differ from each cloud's own page (e.g. Nebius H100 $3.87-3.98 on Shadeform vs $4.50 on nebius.com). Very few configs showed available=true. The underlying clouds include Lambda, which is already in gpu_rental.csv. |
| https://www.tensordock.com/ | Homepage "H100 SXM5 From $2.25/hr". | A marketing "from" price, not a live listing. tensordock.com/pricing returns 404, the public v2 locations API returned an empty list and live listings need a login. |
| https://www.hyperstack.cloud/gpu-pricing | On-demand per-GPU prices: H100 SXM $3.20, H100 PCIe $2.50, H100 PCIe NVLink $2.60, H200 SXM $3.99, B200 $6.00. Reservation "starting from" prices: H100 SXM $2.72, H200 $2.79, B200 $5.10. Spot: H100 PCIe $2.00. | Billed per minute. No region on the table. The reservation term is not stated. Per-GPU vCPU/RAM is listed. |
| https://www.voltagepark.com/pricing | FAQ: one H100 for 1 hour "starting at $1.99 without a contract". | The on-demand card itself says "Contact for pricing". HGX H100 with InfiniBand, no minimum term. The page says Voltage Park has merged with Lightning AI. The Shadeform API shows the same $1.99. |
| https://www.crusoe.ai/cloud/pricing | On-demand $/GPU-hr: H100 HGX $3.90, H200 HGX $4.29. | B200 and spot are "Contact sales". Managed-inference dedicated endpoint prices (H100 $5.50, H200 $6.00, B200 $9.65 per hour) were not recorded because they are not VMs. |
| https://nebius.com/prices | Column "GPU-hour (Effective October 1, 2026)": H100 $4.50, H200 $5.40, B200 $8.50. Preemptible "from" prices: H100/H200 $0.79, B200 $0.99. | The page still shows the older "On-demand, GPU-hour" column (H100 $3.85, H200 $4.50, B200 $7.15). Because today is after 1 Oct, the newer column was used. Spot prices are floors. Commitments save up to 35%. No region given. |
| https://verda.com/pricing | GPU instances, on-demand (1x) and spot: H100 SXM5 $3.81 / $1.91, H200 SXM5 $4.97 / $2.49, B200 SXM6 $7.20 / $3.60. | Formerly DataCrunch (datacrunch.io redirects here). USD view. CPU/RAM bundled per GPU. Reserved is a custom quote with a 1-month minimum. Serverless-container prices were not recorded. |
| https://jarvislabs.ai/pricing | On-demand per-GPU, billed per minute: H100 SXM $3.49, H200 SXM $4.59. | The page lists India regions. Spot and term discounts load by script, so they were not recorded. |
| https://www.digitalocean.com/pricing/gpu-droplets | On-demand $/GPU/hr: H100 $4.41, H200 $4.47. 12-month reserved: H100 $3.26, H200 $3.40. | 1 or 8 GPUs per Droplet. Boot disk, 5 TiB scratch NVMe and 15,000 GiB transfer are bundled. "New pricing is effective as of August 1, 2026." The only NVIDIA spot item is B300, which was not recorded. |
| https://www.paperspace.com/pricing | H100 on-demand $5.95/hr (footnote: "special promo price"). $2.24/hr for a 3-year commitment. | The $2.24 headline needs a 3-year term. Shadeform lists Paperspace H100 at $5.99. Paperspace is part of DigitalOcean. |
| https://massedcompute.com/home/pricing/ | On-demand: H100 SXM5 8x $25.12 (1x $3.14), H100 80GB 1x $2.73, H100 NVL 1x $3.11, H200 NVL 1x $3.62, B200 SXM6 8x $43.46. | Redirects to vm.massedcompute.com/pricing. No contracts and no bandwidth charges. vCPU, RAM and storage are bundled. The form factor of the plain "H100 (80GB)" is not stated; Shadeform labels it PCIe. The H200 is NVL (PCIe), not SXM. |
| https://www.thundercompute.com/pricing | H100 SXM $3.20/hr per GPU. | 4 vCPU are included and extra vCPU is $0.04/hr. Disk is 100-500 GB. Sandboxes at $2.95/GPU-hr were not recorded. The page also shows other clouds' prices, which were **not** used. |
| https://www.ovhcloud.com/en/public-cloud/prices/ | GPU instances, hourly excl. VAT: h100-380 (1x H100) $2.99, h200-1920 (8x H200) $49.56. | The location shown is France (Gravelines). Monthly billing is cheaper ($2,070/mo for 1x H100). The H100 form factor is not stated. The AI Training h100-1-gpu ($3.39) was not recorded because it is a managed service. |
| https://www.scaleway.com/en/pricing/gpu/ | Embedded price data, zone fr-par-2: H100-SXM-8-80G EUR 25.3308/hr, H100-1-80G (PCIe) EUR 2.8665/hr. | Prices are in EUR before tax and were converted at the ECB reference rate of 1.1269 USD/EUR for 2026-10-06 (https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml). Billed per minute. PAR-1 shows "not available". No H200 or B200 instances are listed (only B300). |
| https://api.vultr.com/v2/plans-metal (and https://api.vultr.com/v2/plans) | 8x H100 hourly_cost $23.92 and preemptible $18.40. 8x B200 $68.00 and preemptible $25.60. | www.vultr.com/pricing/ returned HTTP 403. **The API shows deploy_ondemand=false and an empty locations list**, so these list prices are not currently orderable. The H100 form factor is not stated. |
| https://www.denvr.com/pricing | 8x H100 SXM node at $2.45/GPU-hr. | Billed per minute on demand, or reserved (up to 20% off). H200 is "Reserved only" and B200 has no price. denvrdata.com redirects here. |
| https://www.civo.com/pricing | H100 SXM 1x on-demand $2.99 and 12-month $2.69. H200 SXM 1x on-demand $3.49. 8x B200 12-month $35.92. | Data transfer is free and vCPU/RAM/NVMe are bundled. B200 on-demand and 6-month are N/A. Other terms (6/24/36-month) are in the notes. |
| https://gcore.com/pricing/ai | Virtual GPU ("pay only while powered on"): 1x H100 EUR 2.82/hr, 8x H100 EUR 18.91/hr. | Prices are in EUR excl. VAT, converted at ECB 1.1269. The form factor is not stated. The bare-metal 8xH100 SXM price (EUR 21.82/hr) was not recorded because the page's pricing-model toggle runs in script and its term is unclear. "Everywhere Inference" (managed) was not recorded. |
| https://www.latitude.sh/pricing | Metal GPU g3.h100.small (1x H100 80GB), hourly "Starting At" $1.68. | Bare metal. The price varies by location. 20 TB free egress. The form factor is not stated; Shadeform labels it PCIe. |
| https://www.koyeb.com/pricing | Serverless GPU, Standard tab: H100 $2.50, H200 $3.00, B200 $5.50 per hour (1x). | Billed per second with scale-to-zero. vCPU/RAM/disk are bundled. There is also an "Eco" tab, which was not recorded. The form factor is not stated. |
| https://northflank.com/pricing | H100 80GB $2.74/hr. | GPU only: CPU and memory are billed on top. The form factor is not stated. |
| https://modal.com/pricing | Per-second GPU prices x 3600: H100 SXM5 $3.9492, H200 SXM $4.5396, B200 $6.2496. | Serverless, GPU only; CPU and memory are billed separately. You pay only for running time. |

### Opened but no usable price

- SF Compute (https://sfcompute.com/pricing) redirects to a login. The homepage shows only an illustrative resale calculator, not a price list.
- Fluidstack (https://www.fluidstack.io/pricing) returns 404. The homepage has no price list.
- Genesis Cloud (https://www.genesiscloud.com/pricing) failed with HTTP 522 / TLS error.
- CUDO Compute (https://www.cudocompute.com/pricing) shows H100/H200/B200 as "Quote on request".
- Prime Intellect, Hyperbolic, Novita and Nscale pricing URLs returned 404, 403 or no GPU prices.
- Three pages were not used because they show only "from" prices with an unclear term: GMI Cloud (https://www.gmicloud.ai/pricing; H100 "from $2.00", H200 "from $2.60", B200 "from $4.00"), Taiga Cloud / Northern Data (https://northerndata.de/taiga-cloud-ai-pricing; H100 SXM "from $2.60") and Seeweb (H100 config shown with ambiguous GPU count).

### Caveats for this file

1. **Units differ.** Some prices are per GPU on a multi-GPU node (Hyperstack SXM, Denvr, Vultr, Scaleway SXM). Some are single-GPU VMs (Civo, Verda, Koyeb), and some are serverless GPU-only rates that add CPU/RAM on top (Modal, Northflank). What is bundled is in each row's notes.
2. **"From" and "starting at" prices are floors.** These are Voltage Park, TensorDock, Latitude.sh, Hyperstack reserved and Nebius spot.
3. **Form factors.** Rows say SXM, PCIe or NVL when the page states it. "Form factor not stated" means the page did not say.
4. **Marketplace prices are snapshots.** Vast.ai and Shadeform prices move continuously, and most Shadeform configs were shown as unavailable.
5. **EUR rows.** Scaleway and Gcore were converted at a single ECB rate. The original EUR price is in the notes.
6. **Not deployable.** Vultr's on-demand list prices are not orderable at present (deploy_ondemand=false).
