## Search State

- **Seed**: 5
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | push → release → pull → release → release → grasp → retract | linear_cartesian | — | arc_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | time_limit | pose_tolerance | 3 | 0.4728 | 0.77 | ❌ rejected |
| 0 | push → release → pull → release → release → grasp → retract | linear_cartesian | — | arc_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | admittance_control | position_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | time_limit | time_limit | pose_tolerance | 3 | 0.6642 | 0.96 | ✅ accepted |

**Proposal policy**: task_score is 0.77 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
- task_score stagnant: change coupled targets, parameters, terminations, phase types, controls, subtasks, or ordering when evidence shows they need to change together.
A HOLD wastes an iteration when task_score is below 0.9.

## Optimisation Objective

Your goal is to **maximise task_score first, then composite score Q**:

> **Primary objective: task_score** — the fraction of episodes where the robot successfully completes the task. This is the most important metric. **Never propose a simpler or shorter skill if it reduces task_score.**

> **Q = fitness_score + termination_fidelity − complexity_penalty**

- `fitness_score`: shaped task reward (includes phase progress for contact-rich tasks)
- `termination_fidelity`: fraction of phases that terminated by designed condition (not timeout)
- `complexity_penalty`: cost for over-parameterised or over-phased designs

**Warning**: Do not reduce phases or parameters to lower complexity if doing so reduces task_score. Structure complexity is only penalised when it adds no performance gain.

# Proposal Context

## Task Specification

- Task name: peg_insert
- Frozen realised-scene SHA-256: `68ad8ffad13ff17e4e79d7c12ed07a79b854360d1380b55b4d752be6df0d8737`
- Frozen object start: [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]
- Frozen task target: [0.5244002338996298, 0.024635263178919502, 0.08]
- Frozen socket pose: [0.5244002338996298, 0.024635263178919502, 0.025] (static fixture for this episode)
- Goal object position: (0.5244002338996298, 0.024635263178919502, 0.025)
- Object initial pose: (0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055)
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 40.0 N
- Channel axis: `(0.0, 0.0, -1.0)` — use `impedance_control` to absorb lateral wall forces
- Robot initial TCP position: (0.5, 0.0, 0.3)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **insertion depth ratio (axial progress into hole)**

## Scene Entities

robot:
  model: panda_peg
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5, 0, 0.3]
objects:
  - name: peg_socket
    role: fixture
    dynamics: static
    geometry: box_with_hole
    base_dimensions_m: [0.12, 0.12, 0.05]
    hole_entry_height_m: 0.08
  - name: peg
    role: manipulated_object
    dynamics: free
    geometry: cylinder
    note: peg is a fixed end-effector attachment on the panda_peg arm
task_landmarks:
  frozen_object_start: [0.504, -0, 0.3403]
  frozen_task_target: [0.5244, 0.0246, 0.08]
  frozen_socket_position: [0.5244, 0.0246, 0.025]
  socket_state: static_frozen
  frozen_object_starts: {'peg': [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]}
  frozen_targets: {'socket_entry': [0.5244002338996298, 0.024635263178919502, 0.08]}
  frozen_fixtures: {'peg_socket': [0.5244002338996298, 0.024635263178919502, 0.025]}
  insertion_axis: [0, 0, -1]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  hole_depth_m: 0.05
  force_scale_n: 5
  realized_scene_sha256: 68ad8ffad13ff17e4e79d7c12ed07a79b854360d1380b55b4d752be6df0d8737

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.964, which indicates the subtask decomposition is already effective.
> Preserve the current subtask decomposition unless the evidence shows a subtask change is necessary. Prefer refining phases, parameters, control modes, or termination conditions first.
> Unnecessary subtask redesign when performance is already high often causes regression.

## Subtask Layer

**Mode**: free (you define subtask targets; use `subtasks:` block in your YAML)

Define subtasks in a `subtasks:` block **before** `phases:`. Each subtask specifies an intermediate optimisation target.

**Required fields** — always include both, never omit:
- `anchor` (**required**): fixture | goal | object | world
- `target_entity` (**required**): hinge | object | tcp

Subtask anchors are separate from phase `target.anchor` vocabulary: subtasks use `world | object | goal | fixture`, while phase targets use `world | task_goal | task_object | fixture | body | site | current_tcp`.

Optional fields:
- `metric`: contact | distance | goal_progress | hinge_angle (default: distance)
- `offset`: [x, y, z] in metres relative to anchor (default: [0, 0, 0])
- `param_offset_key`: CMA-ES parameter added to offset at runtime (optional)
- `weight`: scoring weight [0.1, 1.0] (default: 1.0)

**Anchor resolution for this task** — choose anchor so the resolved position is meaningful:
| Anchor | Resolves to | Best used for |
|--------|-------------|---------------|
| `world` | absolute world-frame coordinate | fixed reference points not tied to objects |
| `object` | offset from object initial position (0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5244002338996298, 0.024635263178919502, 0.025) | final destination targets |
| `fixture` | offset from fixture pose (0.5244002338996298, 0.024635263178919502, 0.025) | approach/contact targets near fixture |

Annotate each phase with `subtask_id: <id>` to bind it to a subtask.
Only the **last phase** bound to a given subtask contributes to subtask scoring.

Example (two subtasks — one near object start, one at goal):
```yaml
subtasks:
  - id: reach_pre_contact
    anchor: object         # resolved to object initial position (see table above)
    target_entity: tcp     # score TCP distance to this target
    metric: distance
    offset: [0.0, 0.0, 0.10]  # 10 cm above object start position
    weight: 0.3
  - id: reach_goal
    anchor: goal           # resolved to task goal position (see table above)
    target_entity: tcp
    metric: distance
    offset: [0.0, 0.0, 0.0]
    weight: 0.7
phases:
  - id: approach_1
    type: approach
    subtask_id: reach_pre_contact
    ...
  - id: push_1
    type: push
    subtask_id: reach_goal
    ...
```

## Current Skill (Q=0.473) — your mutation base

```yaml
skill: peg_insert
skill_type: arm_gripper
phases:
- id: push_1
  type: push
  generator: linear_cartesian
  control: position_control
  termination: time_limit
  parameters:
    push_depth:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: release_1
  type: release
  control: position_control
  termination: time_limit
  end_effector_action: open
- id: pull_1
  type: pull
  generator: arc_cartesian
  control: impedance_control
  termination: time_limit
  parameters:
    pull_distance:
      type: scalar
      range:
      - 0.02
      - 0.2
- id: release_2
  type: release
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
  end_effector_action: open
- id: release_3
  type: release
  generator: linear_cartesian
  control: position_control
  termination: time_limit
  end_effector_action: open
- id: grasp_1
  type: grasp
  control: position_control
  termination: time_limit
  end_effector_action: force_grasp
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1

```

## Design Metrics

- **Composite score**: 0.473
- **task_score** (E): 0.773
- **fitness_score**: 0.773  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.300

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| push_1 | 1.00 | 0.1058 |
| release_1 | 1.00 | 0.0117 |
| pull_1 | 1.00 | 0.0725 |
| release_2 | 1.00 | 0.0981 |
| release_3 | 1.00 | 0.0282 |
| grasp_1 | 1.00 | 0.0095 |
| retract_1 | 0.00 | 0.0736 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| push_1 | push | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.508, 0.009, 0.197) | (0.504, -0.000, 0.340)→(0.508, 0.009, 0.237) | 0.260→0.158 |
| release_1 | release | 1.00 / step_budget | (0.508, 0.009, 0.197)→(0.502, 0.009, 0.186) | (0.508, 0.009, 0.237)→(0.504, 0.009, 0.226) | 0.158→0.147 |
| pull_1 | pull | 1.00 / step_budget | (0.502, 0.009, 0.186)→(0.508, 0.028, 0.256) | (0.504, 0.009, 0.226)→(0.510, 0.028, 0.296) | 0.147→0.218 |
| release_2 | release | 1.00 / step_budget | (0.508, 0.028, 0.256)→(0.506, 0.018, 0.159) | (0.510, 0.028, 0.296)→(0.507, 0.018, 0.199) | 0.218→0.122 |
| release_3 | release | 1.00 / time_limit | (0.506, 0.018, 0.159)→(0.504, 0.015, 0.131) | (0.507, 0.018, 0.199)→(0.505, 0.015, 0.171) | 0.122→0.095 |
| grasp_1 | grasp | 1.00 / step_budget | (0.504, 0.015, 0.131)→(0.499, 0.015, 0.124) | (0.505, 0.015, 0.171)→(0.501, 0.015, 0.164) | 0.095→0.087 |
| retract_1 | retract | 0.00 / step_budget | (0.499, 0.015, 0.124)→(0.511, 0.006, 0.195) | (0.501, 0.015, 0.164)→(0.513, 0.006, 0.235) | 0.087→0.156 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.790
- alignment_error: None

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.790
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.790
- **Median Q (composite search score)**: 0.473
- **K-run variance**: 0.0002
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.350


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `5e5af3f51d5f63e3a348998ea00f94a7255959965642a40069d0a7b5ef8ede34`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `cc7f64fba434a86728ba6288ab9746a03660fc43702ba486c544717f06e4937d`; realized-scene SHA-256: `68ad8ffad13ff17e4e79d7c12ed07a79b854360d1380b55b4d752be6df0d8737`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.5244,0.02464,0.025]},{"name":"target","value":[0.5244,0.02464,0.025]},{"name":"socket","value":[0.5244,0.02464,0.025]},{"name":"goal","value":[0.5244,0.02464,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.5244,0.02464,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.5244,0.02464,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.42446,"average_solve_count":139.0,"average_success_count":139.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"pull_1.pull_distance":0.13107,"push_1.push_depth":0.09916,"retract_1.speed":0.05875},"optimized_scores":{"best_composite_score":0.47278,"best_fitness_score":0.77278,"best_task_score":0.77278},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[],"total_contact_groups":0},"final_pose_error":0.05929,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.5244,0.02464,0.025],"final_tcp_position":[0.51573,0.01003,0.19172],"realised_fixture_position":[0.5244,0.02464,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.5244,0.02464,0.08]},"phases":[{"n_steps":99.0,"n_steps_budget":810.0,"object_pos_end":[0.5164,0.01588,0.25661],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.17808,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"reach_socket","tcp_end":[0.51541,0.01582,0.21662],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.512,0.01588,0.24601],"object_pos_start":[0.5164,0.01588,0.25661],"object_to_goal_dist_end":0.1672,"object_to_goal_dist_start":0.17808,"object_z_max":0.25661,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","tcp_end":[0.51011,0.01579,0.20606],"tcp_start":[0.51541,0.01582,0.21662],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":62.0,"n_steps_budget":630.0,"object_pos_end":[0.51931,0.02775,0.29119],"object_pos_start":[0.512,0.01588,0.24601],"object_to_goal_dist_end":0.21388,"object_to_goal_dist_start":0.1672,"object_z_max":0.29031,"phase_name":"pull_1","phase_peak_obstacle_force":0.0,"phase_type":"pull","tcp_end":[0.51697,0.02764,0.25126],"tcp_start":[0.51011,0.01579,0.20606],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":128.0,"n_steps_budget":750.0,"object_pos_end":[0.51844,0.02524,0.1993],"object_pos_start":[0.51931,0.02775,0.29119],"object_to_goal_dist_end":0.12333,"object_to_goal_dist_start":0.21388,"object_z_max":0.29285,"phase_name":"release_2","phase_peak_obstacle_force":0.0,"phase_type":"release","subtask_id":"insertion","tcp_end":[0.51736,0.02518,0.15931],"tcp_start":[0.51697,0.02764,0.25126],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":165.0,"n_steps_budget":600.0,"object_pos_end":[0.51708,0.02443,0.17088],"object_pos_start":[0.51844,0.02524,0.1993],"object_to_goal_dist_end":0.09564,"object_to_goal_dist_start":0.12333,"object_z_max":0.1993,"phase_name":"release_3","phase_peak_obstacle_force":0.0,"phase_type":"release","tcp_end":[0.51614,0.02439,0.13089],"tcp_start":[0.51736,0.02518,0.15931],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"time_limit"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5121,0.02414,0.16287],"object_pos_start":[0.51708,0.02443,0.17088],"object_to_goal_dist_end":0.08716,"object_to_goal_dist_start":0.09564,"object_z_max":0.17088,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.5104,0.02407,0.1229],"tcp_start":[0.51614,0.02439,0.13089],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":80.0,"n_steps_budget":1000.0,"object_pos_end":[0.51786,0.01015,0.23167],"object_pos_start":[0.5121,0.02414,0.16287],"object_to_goal_dist_end":0.15305,"object_to_goal_dist_start":0.08716,"object_z_max":0.2306,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.51573,0.01003,0.19172],"tcp_start":[0.5104,0.02407,0.1229],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `619899a8ac3451ebc6b92c72992387b20e095386c555898a9ee2a3180ddd0ca3`; realized-scene SHA-256: `8fefb664610d091fa81ee0c279409778edf059cbe39fe254365372fa331a0db3`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.50305,-0.01254,0.025]},{"name":"target","value":[0.50305,-0.01254,0.025]},{"name":"socket","value":[0.50305,-0.01254,0.025]},{"name":"goal","value":[0.50305,-0.01254,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.50305,-0.01254,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.50305,-0.01254,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.08787,"average_solve_count":239.0,"average_success_count":239.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"pull_1.pull_distance":0.07186,"push_1.push_depth":0.03815,"retract_1.speed":0.02134},"optimized_scores":{"best_composite_score":0.48986,"best_fitness_score":0.78986,"best_task_score":0.78986},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[],"total_contact_groups":0},"final_pose_error":0.0554,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.50305,-0.01254,0.025],"final_tcp_position":[0.50745,-0.00402,0.1962],"realised_fixture_position":[0.50305,-0.01254,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.50305,-0.01254,0.08]},"phases":[{"n_steps":158.0,"n_steps_budget":1000.0,"object_pos_end":[0.50204,-0.00942,0.19742],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.11782,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"reach_socket","tcp_end":[0.5014,-0.0094,0.15743],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49664,-0.00946,0.18725],"object_pos_start":[0.50204,-0.00942,0.19742],"object_to_goal_dist_end":0.10772,"object_to_goal_dist_start":0.11782,"object_z_max":0.19742,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","tcp_end":[0.49509,-0.00944,0.14728],"tcp_start":[0.5014,-0.0094,0.15743],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":167.0,"n_steps_budget":960.0,"object_pos_end":[0.50377,0.02373,0.30661],"object_pos_start":[0.49664,-0.00946,0.18725],"object_to_goal_dist_end":0.22788,"object_to_goal_dist_start":0.10772,"object_z_max":0.306,"phase_name":"pull_1","phase_peak_obstacle_force":0.0,"phase_type":"pull","tcp_end":[0.50182,0.02369,0.26666],"tcp_start":[0.49509,-0.00944,0.14728],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":153.0,"n_steps_budget":870.0,"object_pos_end":[0.49883,-0.00346,0.19877],"object_pos_start":[0.50377,0.02373,0.30661],"object_to_goal_dist_end":0.11883,"object_to_goal_dist_start":0.22788,"object_z_max":0.30729,"phase_name":"release_2","phase_peak_obstacle_force":0.0,"phase_type":"release","subtask_id":"insertion","tcp_end":[0.49785,-0.00344,0.15878],"tcp_start":[0.50182,0.02369,0.26666],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":171.0,"n_steps_budget":600.0,"object_pos_end":[0.49626,-0.01045,0.17148],"object_pos_start":[0.49883,-0.00346,0.19877],"object_to_goal_dist_end":0.09215,"object_to_goal_dist_start":0.11883,"object_z_max":0.19877,"phase_name":"release_3","phase_peak_obstacle_force":0.0,"phase_type":"release","tcp_end":[0.49536,-0.01044,0.13149],"tcp_start":[0.49785,-0.00344,0.15878],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"time_limit"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4914,-0.01042,0.16409],"object_pos_start":[0.49626,-0.01045,0.17148],"object_to_goal_dist_end":0.08517,"object_to_goal_dist_start":0.09215,"object_z_max":0.17148,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.48977,-0.01041,0.12412],"tcp_start":[0.49536,-0.01044,0.13149],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":120.0,"n_steps_budget":1000.0,"object_pos_end":[0.50953,-0.00404,0.23614],"object_pos_start":[0.4914,-0.01042,0.16409],"object_to_goal_dist_end":0.15648,"object_to_goal_dist_start":0.08517,"object_z_max":0.2352,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.50745,-0.00402,0.1962],"tcp_start":[0.48977,-0.01041,0.12412],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `09a021eaed2a28b8f97b40a956e668b0df532c8dfcbc8d48b91f00ceefb0c83a`; realized-scene SHA-256: `f2535c6a7dfc5a3ca3c25224b40d7fd8d1111b06ec904a3c56a54673c2686a85`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.51001,0.03178,0.025]},{"name":"target","value":[0.51001,0.03178,0.025]},{"name":"socket","value":[0.51001,0.03178,0.025]},{"name":"goal","value":[0.51001,0.03178,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.51001,0.03178,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.51001,0.03178,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.90141,"average_solve_count":213.0,"average_success_count":213.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"pull_1.pull_distance":0.1732,"push_1.push_depth":0.09784,"retract_1.speed":0.01648},"optimized_scores":{"best_composite_score":0.45564,"best_fitness_score":0.75564,"best_task_score":0.75564},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[],"total_contact_groups":0},"final_pose_error":0.05583,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.51001,0.03178,0.025],"final_tcp_position":[0.50998,0.01182,0.19636],"realised_fixture_position":[0.51001,0.03178,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.51001,0.03178,0.08]},"phases":[{"n_steps":99.0,"n_steps_budget":810.0,"object_pos_end":[0.50702,0.02049,0.25583],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.17716,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"reach_socket","tcp_end":[0.50603,0.02041,0.21584],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50265,0.02051,0.24577],"object_pos_start":[0.50702,0.02049,0.25583],"object_to_goal_dist_end":0.16706,"object_to_goal_dist_start":0.17716,"object_z_max":0.25583,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","tcp_end":[0.50079,0.0204,0.20582],"tcp_start":[0.50603,0.02041,0.21584],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":60.0,"n_steps_budget":630.0,"object_pos_end":[0.50719,0.03165,0.29041],"object_pos_start":[0.50265,0.02051,0.24577],"object_to_goal_dist_end":0.2129,"object_to_goal_dist_start":0.16706,"object_z_max":0.28951,"phase_name":"pull_1","phase_peak_obstacle_force":0.0,"phase_type":"pull","tcp_end":[0.50488,0.03152,0.25048],"tcp_start":[0.50079,0.0204,0.20582],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":128.0,"n_steps_budget":750.0,"object_pos_end":[0.50479,0.03138,0.19948],"object_pos_start":[0.50719,0.03165,0.29041],"object_to_goal_dist_end":0.12363,"object_to_goal_dist_start":0.2129,"object_z_max":0.29218,"phase_name":"release_2","phase_peak_obstacle_force":0.0,"phase_type":"release","subtask_id":"insertion","tcp_end":[0.50374,0.03131,0.1595],"tcp_start":[0.50488,0.03152,0.25048],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":158.0,"n_steps_budget":600.0,"object_pos_end":[0.50289,0.03128,0.17184],"object_pos_start":[0.50479,0.03138,0.19948],"object_to_goal_dist_end":0.09706,"object_to_goal_dist_start":0.12363,"object_z_max":0.19948,"phase_name":"release_3","phase_peak_obstacle_force":0.0,"phase_type":"release","tcp_end":[0.50198,0.03123,0.13185],"tcp_start":[0.50374,0.03131,0.1595],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"time_limit"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49801,0.03094,0.16424],"object_pos_start":[0.50289,0.03128,0.17184],"object_to_goal_dist_end":0.08977,"object_to_goal_dist_start":0.09706,"object_z_max":0.17184,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.49635,0.03085,0.12428],"tcp_start":[0.50198,0.03123,0.13185],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":120.0,"n_steps_budget":1000.0,"object_pos_end":[0.51209,0.01195,0.2363],"object_pos_start":[0.49801,0.03094,0.16424],"object_to_goal_dist_end":0.15723,"object_to_goal_dist_start":0.08977,"object_z_max":0.23536,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.50998,0.01182,0.19636],"tcp_start":[0.49635,0.03085,0.12428],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```