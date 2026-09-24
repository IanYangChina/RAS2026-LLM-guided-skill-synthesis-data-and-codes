## Search State

- **Seed**: 5
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → descend → insert | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | force_exceeded | 5 | 0.6955 | 0.89 | ❌ rejected |
| 4 | push → release → pull → release → release → grasp → retract | linear_cartesian | — | arc_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.5679 | 0.87 | ❌ rejected |
| 3 | push → release → pull → release → release → grasp → retract | linear_cartesian | — | arc_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | admittance_control | position_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | time_limit | time_limit | pose_tolerance | 3 | 0.6642 | 0.96 | ❌ rejected |
| 2 | push → release → pull → release → release → grasp → retract | linear_cartesian | — | arc_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | admittance_control | position_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | time_limit | time_limit | pose_tolerance | 3 | 0.6642 | 0.96 | ❌ rejected |
| 1 | push → release → pull → release → release → grasp → retract | linear_cartesian | — | arc_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | time_limit | pose_tolerance | 3 | 0.4728 | 0.77 | ❌ rejected |

**Proposal policy**: task_score is 0.89 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.695) — your mutation base

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

- **Composite score**: 0.695
- **task_score** (E): 0.889
- **fitness_score**: 0.642  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.280

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_above_entry | 1.00 | 0.1391 |
| descend_to_entry | 0.00 | 0.0809 |
| insert_into_hole | 1.00 | 0.0325 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_above_entry | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.508, 0.012, 0.163) | (0.504, -0.000, 0.340)→(0.513, 0.012, 0.203) | 0.260→0.126 |
| descend_to_entry | descend | 0.00 / step_budget | (0.508, 0.012, 0.163)→(0.508, 0.014, 0.083) | (0.513, 0.012, 0.203)→(0.513, 0.014, 0.122) | 0.126→0.051 |
| insert_into_hole | insert | 1.00 / force_exceeded | (0.508, 0.014, 0.083)→(0.507, 0.014, 0.050) | (0.513, 0.014, 0.122)→(0.507, 0.014, 0.090) | 0.051→0.027 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.943
- alignment_error: None
- terminal_score: 0.943
- phase_score: 0.639
- phase_breakdown.insertion_goal_score: 0.639

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.760
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.943
- **Median Q (composite search score)**: 0.645
- **K-run variance**: 0.0070
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.414


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.15385,"average_solve_count":52.0,"average_success_count":52.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_entry.approach_speed":0.49974,"approach_above_entry.pose_tol":0.02,"descend_to_entry.contact_force_threshold":6.60202,"insert_into_hole.insert_distance":0.05972,"insert_into_hole.insert_force_limit":29.89178},"optimized_scores":{"best_composite_score":0.64509,"best_fitness_score":0.59175,"best_task_score":0.86425},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[],"total_contact_groups":0},"final_pose_error":0.03063,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.5244,0.02464,0.025],"final_tcp_position":[0.51796,0.02407,0.05021],"realised_fixture_position":[0.5244,0.02464,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.5244,0.02464,0.08]},"phases":[{"n_steps":255.0,"n_steps_budget":600.0,"object_pos_end":[0.52273,0.02075,0.20331],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.12709,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"phase_name":"approach_above_entry","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"insertion_goal","tcp_end":[0.51815,0.02072,0.16358],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":423.0,"n_steps_budget":600.0,"object_pos_end":[0.52502,0.02411,0.12189],"object_pos_start":[0.52273,0.02075,0.20331],"object_to_goal_dist_end":0.05443,"object_to_goal_dist_start":0.12709,"object_z_max":0.20331,"phase_name":"descend_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"insertion_goal","tcp_end":[0.51996,0.02406,0.08221],"tcp_start":[0.51815,0.02072,0.16358],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":170.0,"n_steps_budget":600.0,"object_pos_end":[0.5186,0.0241,0.09021],"object_pos_start":[0.52502,0.02411,0.12189],"object_to_goal_dist_end":0.03211,"object_to_goal_dist_start":0.05443,"object_z_max":0.12189,"phase_name":"insert_into_hole","phase_peak_obstacle_force":0.0,"phase_type":"insert","subtask_id":"insertion_goal","tcp_end":[0.51796,0.02407,0.05021],"tcp_start":[0.51996,0.02406,0.08221],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.91803,"average_solve_count":61.0,"average_success_count":61.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_entry.approach_speed":0.15954,"approach_above_entry.pose_tol":0.01908,"descend_to_entry.contact_force_threshold":10.90123,"insert_into_hole.insert_distance":0.03302,"insert_into_hole.insert_force_limit":23.66996},"optimized_scores":{"best_composite_score":0.81363,"best_fitness_score":0.76029,"best_task_score":0.94268},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[],"total_contact_groups":0},"final_pose_error":0.00564,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.50305,-0.01254,0.025],"final_tcp_position":[0.49834,-0.01246,0.05008],"realised_fixture_position":[0.50305,-0.01254,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.50305,-0.01254,0.08]},"phases":[{"n_steps":258.0,"n_steps_budget":630.0,"object_pos_end":[0.50464,-0.01062,0.20339],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.12393,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"phase_name":"approach_above_entry","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"insertion_goal","tcp_end":[0.50006,-0.01061,0.16365],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":415.0,"n_steps_budget":600.0,"object_pos_end":[0.50403,-0.01235,0.12255],"object_pos_start":[0.50464,-0.01062,0.20339],"object_to_goal_dist_end":0.04449,"object_to_goal_dist_start":0.12393,"object_z_max":0.20339,"phase_name":"descend_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"insertion_goal","tcp_end":[0.49899,-0.01234,0.08287],"tcp_start":[0.50006,-0.01061,0.16365],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":204.0,"n_steps_budget":600.0,"object_pos_end":[0.49888,-0.01247,0.09008],"object_pos_start":[0.50403,-0.01235,0.12255],"object_to_goal_dist_end":0.01607,"object_to_goal_dist_start":0.04449,"object_z_max":0.12255,"phase_name":"insert_into_hole","phase_peak_obstacle_force":0.0,"phase_type":"insert","subtask_id":"insertion_goal","tcp_end":[0.49834,-0.01246,0.05008],"tcp_start":[0.49899,-0.01234,0.08287],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.8254,"average_solve_count":63.0,"average_success_count":63.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_entry.approach_speed":0.10828,"approach_above_entry.pose_tol":0.01953,"descend_to_entry.contact_force_threshold":4.92377,"insert_into_hole.insert_distance":0.05984,"insert_into_hole.insert_force_limit":13.73435},"optimized_scores":{"best_composite_score":0.62767,"best_fitness_score":0.57434,"best_task_score":0.85906},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[],"total_contact_groups":0},"final_pose_error":0.03057,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.51001,0.03178,0.025],"final_tcp_position":[0.50382,0.03109,0.05008],"realised_fixture_position":[0.51001,0.03178,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.51001,0.03178,0.08]},"phases":[{"n_steps":276.0,"n_steps_budget":930.0,"object_pos_end":[0.51043,0.02691,0.20278],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.12613,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"phase_name":"approach_above_entry","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"insertion_goal","tcp_end":[0.50584,0.02688,0.16304],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":417.0,"n_steps_budget":600.0,"object_pos_end":[0.51087,0.03113,0.12231],"object_pos_start":[0.51043,0.02691,0.20278],"object_to_goal_dist_end":0.05364,"object_to_goal_dist_start":0.12613,"object_z_max":0.20278,"phase_name":"descend_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"insertion_goal","tcp_end":[0.50582,0.03107,0.08263],"tcp_start":[0.50584,0.02688,0.16304],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":176.0,"n_steps_budget":600.0,"object_pos_end":[0.50443,0.03113,0.09007],"object_pos_start":[0.51087,0.03113,0.12231],"object_to_goal_dist_end":0.03301,"object_to_goal_dist_start":0.05364,"object_z_max":0.12231,"phase_name":"insert_into_hole","phase_peak_obstacle_force":0.0,"phase_type":"insert","subtask_id":"insertion_goal","tcp_end":[0.50382,0.03109,0.05008],"tcp_start":[0.50582,0.03107,0.08263],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":true}]}
```