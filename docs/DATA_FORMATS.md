# Data and output formats

`data/` is an immutable, checksum-protected input layer. Generated outputs
belong in `runs/`, `renders/`, or `reproduced_results/`.

## Coverage and identifiers

The release contains exactly 1,380 experimental cells:

- 900 primary cells: 15 automatic arms × 6 tasks × 10 seeds;
- 60 separately evaluated expert-reference cells; and
- 420 semantic cells: 7 conditions × 6 tasks × 10 seeds.

Cell IDs are stable and neutral: `p-…` (primary), `e-…` (expert), and `s-…`
(semantic). `catalog.csv` has one row per cell. Its `skill_path`,
`parameters_path`, and `scene_bank_path` form the replay identity consumed by
`render_skill.py`; `cell_record_path` and `run_log_path` locate the complete
normalized numeric record. Every scientific file is repository-relative and
hash-verifiable.

`skill_catalog.csv` catalogs every distributed YAML program. The role is one
of `selected_best`, `executed_expert`, `initial`, or `proposed`.
`evaluation_status` distinguishes evaluated programs from rejected, skipped,
or otherwise non-evaluated proposals. Proposed programs are intentionally not
marked render-addressable because no optimized parameter/result identity is
claimed for them.

## Result tables

`paper_results/main/primary_seed_scores.csv` is the 900-row primary source
table. `primary_task_summary.csv` contains the corresponding 90 arm/task rows.
The expert folder contains 60 seed results, paired comparisons, and gap
recovery inputs. The semantic folder contains the 360 intervention/control
pairs and the 42-row seven-condition task summary. `paper_crosswalk.csv` maps
paper labels to these files and their hashes.

Trajectory files contain cell-, task-, arm-, and method-level anytime and
incumbent-retention data. Case files contain the machine-readable structural
examples. `scripts/reproduce_paper_results.py --strict` recomputes task means,
sample standard deviations, 20,000-replicate seed-0 paired bootstraps, gap
recovery, and trajectory summaries, then checks full-precision values with an
absolute tolerance of `1e-12`.

The tolerance applies only to numerical verification. The categorical
`retained_best` trajectory field uses exact winner semantics: the selected and
terminal canonical scores must be exactly equal. The complete set of numeric
paper-result cells, with three- and four-decimal renderings, is recorded in
`paper_results/manuscript_expectations.json`; strict reproduction regenerates
and verifies this inventory.

## Skills, parameters, scenes, and logs

Skill programs are UTF-8 YAML accepted by `dsl.serialiser`. Parameter files are
JSON maps from fully qualified parameter names to their selected numeric
values. Scene files are ordered frozen configuration banks; scene index zero
is the default replay configuration. Cell JSON records preserve score fields,
source hashes, companion links, and replay paths.

Normalized run logs retain iteration-level scores, structural diffs, optimizer
outcomes, parameter maps, and proposal decisions. Archive histories and
proposal-attempt ledgers remain separate so search trajectories can be audited.
Realized language-model prompt contexts, response skill YAMLs, parse/acceptance
metadata, provider/model settings, token counts, and response hashes are
included. Authentication material, wall-clock timestamps, revision IDs, and
private paths are absent. The public realized-scene marker is
`skill-synthesis:realized-scene:v1`.

## Generation-zero companions

Ten remeasurements are first-class records under `companions/`, with a separate
catalog linking each to its primary cell. They document numerically equivalent
or corrected generation-zero evidence and never overwrite a primary run log.

## Intentional exclusions

The archive omits high-rate simulator traces, diagnostic render images and old
videos, per-attempt metric/CMA files duplicated in run logs, duplicate
checkpoints, caches, lock/completion sentinels, development metadata, Git
history, and credentials. These exclusions reduce redundant storage without
removing the numbers, skills, parameters, scenes, prompts, responses, or search
histories used by the paper. `provenance/normalization.json` records the policy;
`provenance/checksums.sha256` covers every other file in `data/`.
