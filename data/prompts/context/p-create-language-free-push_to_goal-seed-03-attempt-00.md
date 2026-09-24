## Search State

- **Seed**: 3
- **Iteration**: 1 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 0 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 0 | 0.4974 | 0.27 | ✅ accepted |

**Proposal policy**: task_score is 0.27 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

- Task name: push_to_goal
- Frozen realised-scene SHA-256: `35b7946dd60174c5d3e72b05c58367a0800836a817579e6ae5b810157d0560be`
- Frozen object start: [0.45027790005723495, -0.03158273920846803, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.45027790005723495, -0.03158273920846803, 0.025)
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.8
- Force limit: 25.0 N
- Robot initial TCP position: (0.5, 0.0, 0.3)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **object displacement ratio toward goal_object_position**

## Scene Entities

robot:
  model: panda_pusher
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5, 0, 0.3]
objects:
  - name: push_box
    role: manipulated_object
    dynamics: free
    geometry: box
    dimensions_m: [0.05, 0.05, 0.05]
    mass_kg: 0.1
  - name: goal_marker
    role: target_marker
    dynamics: static
    geometry: point
task_landmarks:
  frozen_object_start: [0.4503, -0.0316, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.45027790005723495, -0.03158273920846803, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [0.0497, -0.1184, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: 35b7946dd60174c5d3e72b05c58367a0800836a817579e6ae5b810157d0560be

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
| `object` | offset from object initial position (0.45027790005723495, -0.03158273920846803, 0.025) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5, -0.15, 0.025) | final destination targets |
| `fixture` | offset from fixture pose (if defined, else world) | targets near fixture |

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

## Current Skill (Q=0.497) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
subtasks:
- id: reach_pre_contact
  anchor: object
  offset:
  - 0.0
  - 0.03
  - 0.0
  weight: 0.3
- id: reach_goal
  weight: 0.7
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: push_box
    offset:
    - 0.0
    - 0.03
    - 0.0
    orientation:
      mode: keep_current
  subtask_id: reach_pre_contact
- id: push_1
  type: push
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: goal_marker
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
  subtask_id: reach_goal
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: world
    offset:
    - 0.5
    - -0.15
    - 0.3
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.03, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none
- **push_1** (`push`)
  - target: source=yaml, anchor=task_goal, entity=goal_marker, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none
- **retract_1** (`retract`)
  - target: source=yaml, anchor=world, offset=[0.5, -0.15, 0.3]
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.497
- **task_score** (E): 0.268
- **fitness_score**: 0.527  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.030

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2652 |
| push_1 | 1.00 | 1.00 | 0.1743 |
| retract_1 | 0.00 | 1.00 | 0.1638 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.524, 0.033, 0.043) | (0.513, 0.002, 0.025)→(0.518, 0.004, 0.024) | 0.160→0.162 | 1.00 / 4.000 | 242.680 | 251.137 |
| push_1 | push | 1.00 / step_budget | (0.524, 0.033, 0.043)→(0.499, -0.134, 0.021) | (0.518, 0.004, 0.024)→(0.507, -0.042, 0.025) | 0.162→0.115 | 1.00 / 4.000 | 0.245 | 185.942 |
| retract_1 | retract | 0.00 / step_budget | (0.499, -0.134, 0.021)→(0.497, -0.143, 0.185) | (0.507, -0.042, 0.025)→(0.507, -0.042, 0.025) | 0.115→0.115 | 1.00 / 4.000 | 0.245 | 0.245 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.128
- lateral_force_integral: None
- approach_alignment: 0.856
- goal_progress: 0.128
- terminal_score: 0.128
- phase_score: 0.765
- phase_breakdown.reach_goal_score: 0.819
- phase_breakdown.reach_pre_contact_score: 0.640

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.527
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.268
- **Median Q (composite search score)**: 0.497
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: no_parameters
- **Mean generations**: 0.0
- **Final σ (mean)**: 0.000


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `01fea9f27a58d64b0f9b0ff0cae1096a52b0da1ad311c77058a75ddb9aab77d2`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `c53c9bf1992485fcf877d50f4ee23d3483b4b9e63e5a19adda2461c26d89c46e`; realized-scene SHA-256: `35b7946dd60174c5d3e72b05c58367a0800836a817579e6ae5b810157d0560be`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45028,-0.03158,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.04972,-0.11842,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.45028,-0.03158,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.92969,"average_solve_count":128.0,"average_success_count":128.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{},"optimized_scores":{"best_composite_score":0.48029,"best_fitness_score":0.51029,"best_task_score":0.1281},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":102.0,"contact_point_centroid":[0.46735,-0.00657,0.04584],"force_p95":264.26061,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":267.15395,"mean_force":210.32211,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.45742,-0.0004,0.04577]},{"body_a":"world","body_b":"push_box","contact_count":3424.0,"contact_point_centroid":[0.45105,-0.03092,-6e-05],"force_p95":19.01504,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":241.42762,"mean_force":6.56312,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47389,-0.0007,0.16381]},{"body_a":"attachment","body_b":"push_box","contact_count":593.0,"contact_point_centroid":[0.47992,-0.04178,0.04597],"force_p95":200.17869,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":212.31919,"mean_force":168.29395,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48456,-0.0441,0.04364]},{"body_a":"world","body_b":"push_box","contact_count":2079.0,"contact_point_centroid":[0.46739,-0.04721,-0.00054],"force_p95":143.39019,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":175.1065,"mean_force":48.53327,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48737,-0.07866,0.03508]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.4558,-0.04711,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.493,-0.14412,0.10168]}],"total_contact_groups":5},"final_pose_error":0.11567,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.4558,-0.04711,0.02499],"final_tcp_position":[0.49498,-0.14635,0.18449],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":267.15395,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":881.0,"n_steps_budget":1000.0,"object_pos_end":[0.45375,-0.03075,0.02446],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.1279,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":257.25001,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3526.0,"raw_peak_contact_force":267.15395,"subtask_id":"reach_pre_contact","tcp_end":[0.46445,0.0001,0.04216],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.03715,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":861.0,"n_steps_budget":990.0,"object_pos_end":[0.4558,-0.04711,0.02499],"object_pos_start":[0.45375,-0.03075,0.02446],"object_to_goal_dist_end":0.11198,"object_to_goal_dist_start":0.1279,"object_z_max":0.03344,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2672.0,"raw_peak_contact_force":212.31919,"subtask_id":"reach_goal","tcp_end":[0.49457,-0.14269,0.02087],"tcp_start":[0.46445,0.0001,0.04216],"tcp_to_object_dist_end":0.10322,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4558,-0.04711,0.02499],"object_pos_start":[0.4558,-0.04711,0.02499],"object_to_goal_dist_end":0.11198,"object_to_goal_dist_start":0.11198,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.49498,-0.14635,0.18449],"tcp_start":[0.49457,-0.14269,0.02087],"tcp_to_object_dist_end":0.1919,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `234a0edc218dcf63b67654ddcfd8b0f12da84040687f62c4c4845001a50f549a`; realized-scene SHA-256: `721a00290a47301d7751e432f1a041db545f1b55cfdb74b1d642c32f5b25f702`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.55317,0.00136,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.05317,-0.15136,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.55317,0.00136,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.93333,"average_solve_count":135.0,"average_success_count":135.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{},"optimized_scores":{"best_composite_score":0.57785,"best_fitness_score":0.60785,"best_task_score":0.36094},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":114.0,"contact_point_centroid":[0.56302,0.02561,0.04649],"force_p95":241.61809,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":242.11397,"mean_force":198.13978,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.55216,0.02993,0.04675]},{"body_a":"world","body_b":"push_box","contact_count":3663.0,"contact_point_centroid":[0.55413,0.0021,-6e-05],"force_p95":35.39667,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":222.41396,"mean_force":6.47529,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52338,0.0151,0.16338]},{"body_a":"attachment","body_b":"push_box","contact_count":664.0,"contact_point_centroid":[0.5616,-0.01401,0.04695],"force_p95":168.40818,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":171.62243,"mean_force":137.94228,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.55175,-0.01747,0.04643]},{"body_a":"world","body_b":"push_box","contact_count":3088.0,"contact_point_centroid":[0.55052,-0.02848,-0.00032],"force_p95":94.93704,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":106.78871,"mean_force":30.04246,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53742,-0.04718,0.03873]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.54005,-0.05563,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49579,-0.14308,0.10158]}],"total_contact_groups":5},"final_pose_error":0.1157,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.54005,-0.05563,0.02499],"final_tcp_position":[0.49657,-0.14575,0.18443],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":242.11397,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":944.0,"n_steps_budget":1000.0,"object_pos_end":[0.55841,0.0031,0.02437],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16386,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":234.01491,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3777.0,"raw_peak_contact_force":242.11397,"subtask_id":"reach_pre_contact","tcp_end":[0.56137,0.03177,0.04409],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.03493,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":976.0,"n_steps_budget":1000.0,"object_pos_end":[0.54005,-0.05563,0.02499],"object_pos_start":[0.55841,0.0031,0.02437],"object_to_goal_dist_end":0.10252,"object_to_goal_dist_start":0.16386,"object_z_max":0.03541,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3752.0,"raw_peak_contact_force":171.62243,"subtask_id":"reach_goal","tcp_end":[0.49865,-0.14116,0.02081],"tcp_start":[0.56137,0.03177,0.04409],"tcp_to_object_dist_end":0.09511,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54005,-0.05563,0.02499],"object_pos_start":[0.54005,-0.05563,0.02499],"object_to_goal_dist_end":0.10252,"object_to_goal_dist_start":0.10252,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.49657,-0.14575,0.18443],"tcp_start":[0.49865,-0.14116,0.02081],"tcp_to_object_dist_end":0.18824,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `107d1233d3b0a09f0fa34aa18231b315c9a1d92237bb254399d486ed8004836a`; realized-scene SHA-256: `b2a76c5d1121259d09d3db2c62740fd8fe93dd873d8f379ba1928ff319a7d266`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5366,0.03695,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.0366,-0.18695,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5366,0.03695,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.93478,"average_solve_count":138.0,"average_success_count":138.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{},"optimized_scores":{"best_composite_score":0.43395,"best_fitness_score":0.46395,"best_task_score":0.31504},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":117.0,"contact_point_centroid":[0.54797,0.05843,0.04653],"force_p95":243.66701,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":244.1426,"mean_force":199.73891,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.53707,0.06262,0.04677]},{"body_a":"world","body_b":"push_box","contact_count":3717.0,"contact_point_centroid":[0.53755,0.03775,-6e-05],"force_p95":30.89448,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":220.07418,"mean_force":6.58941,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51547,0.03224,0.16321]},{"body_a":"attachment","body_b":"push_box","contact_count":652.0,"contact_point_centroid":[0.55092,0.01971,0.0468],"force_p95":171.23355,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":173.88436,"mean_force":135.90491,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.54112,0.01607,0.0463]},{"body_a":"world","body_b":"push_box","contact_count":3116.0,"contact_point_centroid":[0.53539,0.00383,-0.00033],"force_p95":113.46783,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":131.12629,"mean_force":28.85655,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52906,-0.02131,0.0383]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.52644,-0.02222,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49854,-0.12706,0.10328]}],"total_contact_groups":5},"final_pose_error":0.11519,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52644,-0.02222,0.02499],"final_tcp_position":[0.49814,-0.13663,0.18561],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":244.1426,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":958.0,"n_steps_budget":1000.0,"object_pos_end":[0.54154,0.03955,0.02432],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.19405,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":236.77565,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3834.0,"raw_peak_contact_force":244.1426,"subtask_id":"reach_pre_contact","tcp_end":[0.54572,0.06601,0.04406],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.03328,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52644,-0.02222,0.02499],"object_pos_start":[0.54154,0.03955,0.02432],"object_to_goal_dist_end":0.13049,"object_to_goal_dist_start":0.19405,"object_z_max":0.03557,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3768.0,"raw_peak_contact_force":173.88436,"subtask_id":"reach_goal","tcp_end":[0.50262,-0.11786,0.02278],"tcp_start":[0.54572,0.06601,0.04406],"tcp_to_object_dist_end":0.09858,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52644,-0.02222,0.02499],"object_pos_start":[0.52644,-0.02222,0.02499],"object_to_goal_dist_end":0.13049,"object_to_goal_dist_start":0.13049,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.49814,-0.13663,0.18561],"tcp_start":[0.50262,-0.11786,0.02278],"tcp_to_object_dist_end":0.19922,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```