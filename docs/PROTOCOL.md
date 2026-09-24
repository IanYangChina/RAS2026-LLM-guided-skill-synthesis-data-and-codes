# Evaluation protocol

## Three reproducibility tiers

- **Exact paper reanalysis:** reads frozen CSV/JSON/YAML records only. It
  regenerates summaries and cross-reference tables without simulation or API
  access.
- **Executable replay:** compiles a supplied or catalogued skill, loads its
  saved parameter map and frozen scene bank, and executes or renders it. The
  selected scene index is explicit (the featured examples use index 0).
- **Stochastic protocol replication:** reruns CMA-ES or structural refinement
  from the declared seed and initialization. Physics, package, and LLM
  variation can change the result; a new LLM response is not an exact replay.

## Reported paper contract

The main study has six tasks and ten independent seeds (0--9) per cell.
Structural refinement uses `T=15` attempts. Every candidate requests a CMA-ES
budget of `B=200`; the three scene configurations allocate 198 scheduled
candidate evaluations as 66/66/66. Legitimate early stopping can reduce the
number actually consumed. Each candidate objective averages three simulator
episodes.

The main automatic comparison matrix contains 900 cells. An expert-reference
set contains 60 cells. The semantic-context study contains 420 cells. The
separately stored generation-zero companion measurements are not silently
merged into those counts.

The six task identifiers are `door_push`, `push_to_goal`, `peg_insert`,
`peg_channel`, `grasp_place`, and `obstacle_reach`.

## Approximate simulation work

The following are planning estimates, not performance guarantees. They depend
on CPU speed, MuJoCo scene complexity, rendering, process contention, and
whether a cached scene bank is reused:

| Run | Approximate work on the reference host |
|---|---|
| Quick smoke (`mock`, one seed, tiny budget) | seconds to a few minutes; no scientific physics |
| One physical task/seed with a small budget | minutes to tens of minutes; measure locally before scaling |
| One full task/seed (`B=200`, three basins, three episodes) | tens of minutes to hours; depends on early stopping and scene cost |
| Full paper protocol (all tasks, seeds, and structural attempts) | many hours to multiple days of CPU simulation, plus LLM latency and provider limits |

These estimates are deliberately approximate. Rendering adds work and disk
space. Start with one task and one seed, inspect CPU/RAM/disk use, and scale
only after a successful replay.

## Proposal and call bounds

A structural LLM cell requests at most one proposal per refinement attempt,
so the nominal bound is 15 refinement proposals per cell before retries. Create
initialization uses `K_CREATION=3`: it makes three nominal creation requests per
Create-initialized cell. If structural refinement is enabled, a Create cell
therefore has up to 18 nominal requests (3 creation + 15 refinement) before
retries, held proposals, or duplicate handling. Semantic runs use the same
15-attempt refinement bound per cell. Retries, malformed responses, provider
failures, held proposals, and duplicate handling can increase request count; the
runner should record actual request and retry counts. Non-LLM CMA-ES and Bandit/MAP-QD runs
make no provider calls.

The full main matrix has 900 cells, but not every arm is LLM-based. Compute
provider calls from the selected arms and cells rather than multiplying 900 by
15 blindly. The semantic study has 420 cells; its theoretical one-proposal
bound is 6,300 before retries if every cell uses LLM refinement.

## Protocol commands

Use `--paper-protocol` for the reported budget where supported. Begin with
`--dry-run`; it performs no physics or API call and prints/validates the
planned inputs. Use `--backend mock` only for software smoke tests. Record the
command, environment package versions, seed, backend, and output directory
with any new result.
