## Search State

- **Seed**: 0
- **Iteration**: 1 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 0 | insert → approach → push → retract → lift → insert | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | linear_cartesian | impedance_motion | impedance_control | force_threshold_switch | impedance_control | position_control | position_control | admittance_control | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 5 | -0.0851 | 0.60 | ✅ accepted |

**Proposal policy**: task_score is 0.60 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `271e316106eeefadf1968368496c98b5aba16bca2ae9da2edeb84f157a6c113e`
- Frozen object start: [0.5109569349857164, -0.018417062898890377, 0.08]
- Frozen task target: [0.5109569349857164, -0.018417062898890377, 0.025]
- Frozen socket pose: [0.5, 0.0, 0.3] (static fixture for this episode)
- Goal object position: (0.5, 0.0, 0.3)
- Object initial pose: (0.5109569349857164, -0.018417062898890377, 0.08)
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 40.0 N
- Channel axis: `(0.0, 0.0, -1.0)` — use `impedance_control` to absorb lateral wall forces
- Robot initial TCP position: (0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **insertion depth ratio (axial progress into hole)**

## Scene Entities

robot:
  model: panda_peg
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]
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
  frozen_task_target: [0.511, -0.0184, 0.08]
  frozen_socket_position: [0.511, -0.0184, 0.025]
  socket_state: static_frozen
  frozen_object_starts: {'peg': [0.5109569349857164, -0.018417062898890377, 0.08]}
  frozen_targets: {'socket_entry': [0.5109569349857164, -0.018417062898890377, 0.025]}
  frozen_fixtures: {'peg_socket': [0.5, 0.0, 0.3]}
  insertion_axis: [0, 0, -1]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  hole_depth_m: 0.05
  force_scale_n: 5
  realized_scene_sha256: 271e316106eeefadf1968368496c98b5aba16bca2ae9da2edeb84f157a6c113e

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
| `object` | offset from object initial position (0.5109569349857164, -0.018417062898890377, 0.08) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5, 0.0, 0.3) | final destination targets |
| `fixture` | offset from fixture pose (0.5, 0.0, 0.3) | approach/contact targets near fixture |

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

## Current Skill (Q=-0.085) — your mutation base

```yaml
skill: peg_insert
phases:
- id: insert_1
  type: insert
  generator: linear_cartesian
  control: impedance_control
  termination: force_exceeded
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: force_threshold_switch
  termination: pose_tolerance
- id: push_1
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: pose_tolerance
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.02
      - 0.2
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: retract_1
  type: retract
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.2
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: lift_1
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: insert_2
  type: insert
  generator: impedance_motion
  control: admittance_control
  termination: force_exceeded

```

## Design Metrics

- **Composite score**: -0.085
- **task_score** (E): 0.596
- **fitness_score**: 0.285  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.370

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| insert_1 | 0.00 | 0.00 | 0.0832 |
| approach_1 | 1.00 | 0.00 | 0.1135 |
| push_1 | 0.00 | 0.00 | 0.3272 |
| retract_1 | 0.00 | 0.00 | 0.1229 |
| lift_1 | 1.00 | 0.00 | 0.1553 |
| insert_2 | 0.00 | 0.00 | 0.0839 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| insert_1 | insert | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.502, -0.000, 0.384) | (0.504, -0.000, 0.340)→(0.501, -0.000, 0.424) | 0.260→0.344 | 0.00 / 0.000 | 0.000 | 0.000 |
| approach_1 | approach | 1.00 / step_budget | (0.502, -0.000, 0.384)→(0.501, 0.000, 0.497) | (0.501, -0.000, 0.424)→(0.490, 0.000, 0.536) | 0.344→0.456 | 0.00 / 0.000 | 0.000 | 0.000 |
| push_1 | push | 0.00 / step_budget | (0.501, 0.000, 0.497)→(0.497, -0.000, 0.170) | (0.490, 0.000, 0.536)→(0.508, -0.000, 0.208) | 0.456→0.129 | 0.00 / 0.000 | 0.000 | 0.000 |
| retract_1 | retract | 0.00 / step_budget | (0.497, -0.000, 0.170)→(0.500, 0.025, 0.290) | (0.508, -0.000, 0.208)→(0.505, 0.025, 0.330) | 0.129→0.251 | 0.00 / 0.000 | 0.000 | 0.000 |
| lift_1 | lift | 1.00 / step_budget | (0.500, 0.025, 0.290)→(0.357, 0.001, 0.343) | (0.505, 0.025, 0.330)→(0.369, 0.002, 0.382) | 0.251→0.329 | 0.00 / 0.000 | 0.000 | 0.000 |
| insert_2 | insert | 0.00 / step_budget | (0.357, 0.001, 0.343)→(0.367, 0.002, 0.427) | (0.369, 0.002, 0.382)→(0.371, 0.002, 0.466) | 0.329→0.407 | 0.00 / 0.000 | 0.000 | 0.000 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.596
- alignment_error: None
- force_efficiency: 1.000
- terminal_score: 0.596
- phase_score: 0.078
- phase_breakdown.align_score: 0.000
- phase_breakdown.approach_score: 0.238
- phase_breakdown.contact_score: 0.000
- phase_breakdown.insert_score: 0.061

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.285
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.596
- **Median Q (composite search score)**: -0.085
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.348


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `193ea3a1ce1ed79056963f057d25ec25a24d300f4824e32f67c8dd96cb6cee27`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `a8b82e05e54fe244d72795229d8ab0587efc7638aafbc9b6be7ad9630911a897`; realized-scene SHA-256: `271e316106eeefadf1968368496c98b5aba16bca2ae9da2edeb84f157a6c113e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51096,-0.01842,0.08]},{"name":"task_object","value":[0.51096,-0.01842,0.08]},{"name":"fixture","value":[0.50397,-0.0,0.34031]},{"name":"target","value":[0.50397,-0.0,0.34031]},{"name":"socket","value":[0.50397,-0.0,0.34031]},{"name":"goal","value":[0.50397,-0.0,0.34031]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.50397,-0.0,0.34031]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.51096,-0.01842,0.08]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.51096,-0.01842,0.025]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.91038,"average_solve_count":212.0,"average_success_count":212.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift_1.speed":0.08501,"push_1.push_distance":0.16039,"push_1.push_speed":0.09988,"retract_1.retract_height":0.14805,"retract_1.speed":0.07477},"optimized_scores":{"best_composite_score":-0.08513,"best_fitness_score":0.28487,"best_task_score":0.59573},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[],"total_contact_groups":0},"final_pose_error":0.01013,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.51096,-0.01842,0.025],"final_tcp_position":[0.36703,0.00173,0.42661],"realised_fixture_position":[0.51096,-0.01842,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.51096,-0.01842,0.08]},"peak_contact_force":0.0,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":571.0,"n_steps_budget":600.0,"object_pos_end":[0.50084,-0.0,0.42361],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.34361,"object_to_goal_dist_start":0.26034,"object_z_max":0.42348,"peak_contact_force":0.0,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.50234,-1e-05,0.38364],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":693.0,"n_steps_budget":780.0,"object_pos_end":[0.49048,2e-05,0.5358],"object_pos_start":[0.50084,-0.0,0.42361],"object_to_goal_dist_end":0.45589,"object_to_goal_dist_start":0.34361,"object_z_max":0.53567,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.50054,0.0,0.49708],"tcp_start":[0.50234,-1e-05,0.38364],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5077,-2e-05,0.20846],"object_pos_start":[0.49048,2e-05,0.5358],"object_to_goal_dist_end":0.12869,"object_to_goal_dist_start":0.45589,"object_z_max":0.53586,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49707,-5e-05,0.1699],"tcp_start":[0.50054,0.0,0.49708],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50452,0.02606,0.33098],"object_pos_start":[0.5077,-2e-05,0.20846],"object_to_goal_dist_end":0.25237,"object_to_goal_dist_start":0.12869,"object_z_max":0.33084,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49996,0.02596,0.29124],"tcp_start":[0.49707,-5e-05,0.1699],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":708.0,"n_steps_budget":1000.0,"object_pos_end":[0.36894,0.00177,0.38156],"object_pos_start":[0.50452,0.02606,0.33098],"object_to_goal_dist_end":0.32881,"object_to_goal_dist_start":0.25237,"object_z_max":0.38149,"peak_contact_force":0.0,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.35715,0.00148,0.34333],"tcp_start":[0.49996,0.02596,0.29124],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.37147,0.00202,0.46636],"object_pos_start":[0.36894,0.00177,0.38156],"object_to_goal_dist_end":0.40719,"object_to_goal_dist_start":0.32881,"object_z_max":0.46624,"peak_contact_force":0.0,"phase_name":"insert_2","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.36703,0.00173,0.42661],"tcp_start":[0.35715,0.00148,0.34333],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `8b3071e2f56806ea19629fc8ca21c92088a0ed2e080a3c941a59355284793364`; realized-scene SHA-256: `8f814a9d9dd9825bee110b06b2d985dbb0aa82505ba300f6022b2e21e7c15f67`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50095,0.03604,0.08]},{"name":"task_object","value":[0.50095,0.03604,0.08]},{"name":"fixture","value":[0.50397,-0.0,0.34031]},{"name":"target","value":[0.50397,-0.0,0.34031]},{"name":"socket","value":[0.50397,-0.0,0.34031]},{"name":"goal","value":[0.50397,-0.0,0.34031]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.50397,-0.0,0.34031]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50095,0.03604,0.08]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.50095,0.03604,0.025]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.67686,"average_solve_count":229.0,"average_success_count":229.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift_1.speed":0.05672,"push_1.push_distance":0.04928,"push_1.push_speed":0.09939,"retract_1.retract_height":0.10136,"retract_1.speed":0.08885},"optimized_scores":{"best_composite_score":-0.08495,"best_fitness_score":0.28505,"best_task_score":0.59574},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[],"total_contact_groups":0},"final_pose_error":0.01013,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.50095,0.03604,0.025],"final_tcp_position":[0.36779,0.00186,0.42779],"realised_fixture_position":[0.50095,0.03604,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.50095,0.03604,0.08]},"peak_contact_force":0.0,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":571.0,"n_steps_budget":600.0,"object_pos_end":[0.50084,-0.0,0.42361],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.34361,"object_to_goal_dist_start":0.26034,"object_z_max":0.42348,"peak_contact_force":0.0,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.50234,-1e-05,0.38364],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":693.0,"n_steps_budget":780.0,"object_pos_end":[0.49048,2e-05,0.5358],"object_pos_start":[0.50084,-0.0,0.42361],"object_to_goal_dist_end":0.45589,"object_to_goal_dist_start":0.34361,"object_z_max":0.53567,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.50054,0.0,0.49708],"tcp_start":[0.50234,-1e-05,0.38364],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5077,-2e-05,0.20846],"object_pos_start":[0.49048,2e-05,0.5358],"object_to_goal_dist_end":0.12869,"object_to_goal_dist_start":0.45589,"object_z_max":0.53586,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49707,-5e-05,0.1699],"tcp_start":[0.50054,0.0,0.49708],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5042,0.02561,0.3542],"object_pos_start":[0.5077,-2e-05,0.20846],"object_to_goal_dist_end":0.27542,"object_to_goal_dist_start":0.12869,"object_z_max":0.35402,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.50111,0.02554,0.31432],"tcp_start":[0.49707,-5e-05,0.1699],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":711.0,"n_steps_budget":1000.0,"object_pos_end":[0.36967,0.0019,0.38275],"object_pos_start":[0.5042,0.02561,0.3542],"object_to_goal_dist_end":0.32962,"object_to_goal_dist_start":0.27542,"object_z_max":0.3827,"peak_contact_force":0.0,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.35814,0.00161,0.34445],"tcp_start":[0.50111,0.02554,0.31432],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.37196,0.00215,0.46757],"object_pos_start":[0.36967,0.0019,0.38275],"object_to_goal_dist_end":0.40818,"object_to_goal_dist_start":0.32962,"object_z_max":0.46745,"peak_contact_force":0.0,"phase_name":"insert_2","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.36779,0.00186,0.42779],"tcp_start":[0.35814,0.00161,0.34445],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `9052c43e0ec79f8dbaeeb446a29f2f8fb71a40595590f857e4c93b1d7e78cc51`; realized-scene SHA-256: `4c08395e36e43245f6092dd2e3719288cb8e1800970c3a851b5dc162486241ee`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48093,-0.01612,0.08]},{"name":"task_object","value":[0.48093,-0.01612,0.08]},{"name":"fixture","value":[0.50397,-0.0,0.34031]},{"name":"target","value":[0.50397,-0.0,0.34031]},{"name":"socket","value":[0.50397,-0.0,0.34031]},{"name":"goal","value":[0.50397,-0.0,0.34031]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.50397,-0.0,0.34031]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.48093,-0.01612,0.08]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.48093,-0.01612,0.025]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.46667,"average_solve_count":255.0,"average_success_count":255.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift_1.speed":0.0501,"push_1.push_distance":0.09944,"push_1.push_speed":0.09971,"retract_1.retract_height":0.14065,"retract_1.speed":0.01746},"optimized_scores":{"best_composite_score":-0.08529,"best_fitness_score":0.28471,"best_task_score":0.5957},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[],"total_contact_groups":0},"final_pose_error":0.01012,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48093,-0.01612,0.025],"final_tcp_position":[0.36633,0.0015,0.42546],"realised_fixture_position":[0.48093,-0.01612,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48093,-0.01612,0.08]},"peak_contact_force":0.0,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":571.0,"n_steps_budget":600.0,"object_pos_end":[0.50084,-0.0,0.42361],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.34361,"object_to_goal_dist_start":0.26034,"object_z_max":0.42348,"peak_contact_force":0.0,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.50234,-1e-05,0.38364],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":693.0,"n_steps_budget":780.0,"object_pos_end":[0.49048,2e-05,0.5358],"object_pos_start":[0.50084,-0.0,0.42361],"object_to_goal_dist_end":0.45589,"object_to_goal_dist_start":0.34361,"object_z_max":0.53567,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.50054,0.0,0.49708],"tcp_start":[0.50234,-1e-05,0.38364],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5077,-2e-05,0.20846],"object_pos_start":[0.49048,2e-05,0.5358],"object_to_goal_dist_end":0.12869,"object_to_goal_dist_start":0.45589,"object_z_max":0.53586,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49707,-5e-05,0.1699],"tcp_start":[0.50054,0.0,0.49708],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50479,0.02464,0.3041],"object_pos_start":[0.5077,-2e-05,0.20846],"object_to_goal_dist_end":0.2255,"object_to_goal_dist_start":0.12869,"object_z_max":0.30399,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49864,0.02451,0.26458],"tcp_start":[0.49707,-5e-05,0.1699],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":889.0,"n_steps_budget":1000.0,"object_pos_end":[0.36826,0.00153,0.3804],"object_pos_start":[0.50479,0.02464,0.3041],"object_to_goal_dist_end":0.32802,"object_to_goal_dist_start":0.2255,"object_z_max":0.38031,"peak_contact_force":0.0,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.3562,0.00126,0.34226],"tcp_start":[0.49864,0.02451,0.26458],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.37104,0.00178,0.46518],"object_pos_start":[0.36826,0.00153,0.3804],"object_to_goal_dist_end":0.4062,"object_to_goal_dist_start":0.32802,"object_z_max":0.46506,"peak_contact_force":0.0,"phase_name":"insert_2","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.36633,0.0015,0.42546],"tcp_start":[0.3562,0.00126,0.34226],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```