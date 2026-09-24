# Optional LLM calls

LLM-based creation and structural refinement are optional. Exact paper
reanalysis and archived replay do not require an API key.

## Authentication

Supply credentials only through the process environment or an external secret
manager. Never commit a key, place it in `.env.example`, pass it as a command-
line argument, or include it in a run log:

```bash
read -r -s DEEPSEEK_API_KEY
export DEEPSEEK_API_KEY
```

The paper preset uses the documented DeepSeek endpoint and model. A different
OpenAI-compatible service is a methodological variant and must be declared:

```bash
read -r OPENAI_COMPATIBLE_BASE_URL
export OPENAI_COMPATIBLE_BASE_URL
read -r OPENAI_COMPATIBLE_MODEL
export OPENAI_COMPATIBLE_MODEL
```

The model can also be supplied with the structural runner's `--model` option.
Do not print the environment or shell history when diagnosing a failed call.

## Proposal count and provider limits

The structural runner nominally requests one proposal per attempt. The paper
contract therefore requests up to 15 refinement proposals per LLM cell. Create
initialization uses `K_CREATION=3`: it makes three nominal creation requests per
Create-initialized cell. When structural LLM refinement is enabled, a Create
cell therefore has up to 18 nominal requests (3 creation + 15 refinement)
before retries, held proposals, or duplicate handling. Retries for invalid
output, transport errors, or rate limits are additional and must be recorded. Use one or two
concurrent workers while validating a setup, then stay below the provider's
current account limit. Do not launch all task/seed cells without an explicit
concurrency plan. Handle HTTP 429 responses with bounded exponential backoff,
and preserve the seed/cell identity when retrying.

## Cost estimate

Provider prices change. Use the provider's pricing page at the time of the
run and record its URL, model, cache mode, and peak/off-peak schedule with the
results. The current DeepSeek pricing page is:
<https://api-docs.deepseek.com/quick_start/pricing/>.

For any OpenAI-compatible provider, calculate an upper-bound estimate before
launching:

```text
cost = (input_tokens / 1,000,000) * input_price_per_million
      + (output_tokens / 1,000,000) * output_price_per_million
      + provider-specific image/cache/tool charges
```

Multiply the per-call estimate by the nominal proposal bound, including three
creation calls plus up to 15 refinement calls for each Create cell, and add
expected retries, held proposals, and duplicate handling. Use actual `usage` fields from completed
responses for the final bill. As a dated planning reference, the official
DeepSeek page currently lists separate cache-hit, cache-miss, peak, off-peak,
and output rates for its Flash model; do not copy those rates into a future
estimate without checking the live page. The legacy paper model name may be
accepted as a provider alias, so record the resolved model returned by the API.

## Cost and safety

Each live proposal may incur provider charges. The full protocol performs many
proposals across six tasks, ten seeds, and 15 structural attempts; estimate
provider cost before launching it. Use a one-task, one-seed, low-budget smoke
run first. `--dry-run` is the safe preflight and makes no network request.
Responses and prompts can contain sensitive context. Store generated outputs
locally until they have been inspected and scrubbed for secrets or personal
paths.

## Reproducibility

LLM responses are stochastic. Save the selected model, endpoint family,
temperature and seed settings, prompt-template identifier, timestamp, and
output hashes alongside a replication result. These metadata identify a
replication attempt; they do not make it byte-identical to a prior call.
