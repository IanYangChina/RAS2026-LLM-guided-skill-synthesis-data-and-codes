## Search State

- **Seed**: 3
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 4 | -0.1426 | 0.01 | ❌ rejected |
| 0 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4526 | 0.63 | ✅ accepted |

**Proposal policy**: task_score is 0.01 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.143) — your mutation base

```yaml
skill: push_to_goal
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: contact_detected
  parameters:
    speed:
      type: scalar
      range:
      - 0.005
      - 0.05
- id: push_1
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  parameters:
    push_depth:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance

```

## Design Metrics

- **Composite score**: -0.143
- **task_score** (E): 0.006
- **fitness_score**: 0.117  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.260

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2232 |
| contact_1 | 1.00 | 1.00 | 0.0410 |
| push_1 | 0.00 | 1.00 | 0.0001 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.509, 0.002, 0.083) | (0.513, 0.002, 0.025)→(0.513, 0.002, 0.025) | 0.160→0.160 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / step_budget | (0.509, 0.002, 0.083)→(0.529, 0.002, 0.047) | (0.513, 0.002, 0.025)→(0.518, 0.002, 0.024) | 0.160→0.160 | 1.00 / 4.667 | 235.539 | 245.738 |
| push_1 | push | 0.00 / guard_failure | (0.529, 0.002, 0.047)→(0.529, 0.002, 0.047) | (0.518, 0.002, 0.024)→(0.518, 0.002, 0.024) | 0.160→0.160 | 1.00 / 4.667 | 116.967 | 116.967 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.038
- lateral_force_integral: None
- approach_alignment: 0.534
- goal_progress: 0.017
- terminal_score: 0.017
- phase_score: 0.217
- phase_breakdown.goal_reach_score: 0.083
- phase_breakdown.pre_contact_score: 0.530

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.137
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.017
- **Median Q (composite search score)**: -0.149
- **K-run variance**: 0.0002
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.373


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.95556,"average_solve_count":135.0,"average_success_count":135.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.04345,"contact_1.speed":0.04985,"push_1.speed":0.06169,"retract_1.speed":0.07218},"optimized_scores":{"best_composite_score":-0.12287,"best_fitness_score":0.13713,"best_task_score":0.01693},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":324.0,"contact_point_centroid":[0.46738,-0.03159,0.0463],"force_p95":268.69391,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":273.05932,"mean_force":220.23984,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.45698,-0.03137,0.05032]},{"body_a":"world","body_b":"push_box","contact_count":1946.0,"contact_point_centroid":[0.45181,-0.03205,-0.00037],"force_p95":126.90173,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":137.17988,"mean_force":36.98572,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.45346,-0.03084,0.0572]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.47782,-0.0326,0.0449],"force_p95":128.80471,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":128.80471,"mean_force":128.80471,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4672,-0.03241,0.04813]},{"body_a":"world","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.4619,-0.04039,-0.00086],"force_p95":60.76377,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":61.12934,"mean_force":43.32826,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4672,-0.03241,0.04813]},{"body_a":"world","body_b":"push_box","contact_count":2984.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47443,-0.01452,0.19249]}],"total_contact_groups":5},"final_pose_error":0.12424,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.45492,-0.03207,0.0237],"final_tcp_position":[0.46725,-0.03241,0.04815],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":273.05932,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":746.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2984.0,"raw_peak_contact_force":0.24534,"subtask_id":"pre_contact","tcp_end":[0.44987,-0.02952,0.08474],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.05979,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":493.0,"n_steps_budget":750.0,"object_pos_end":[0.45492,-0.03207,0.02369],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12626,"object_to_goal_dist_start":0.12843,"object_z_max":0.02499,"peak_contact_force":257.46581,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2270.0,"raw_peak_contact_force":273.05932,"subtask_id":"pre_contact","tcp_end":[0.4672,-0.03241,0.04813],"tcp_start":[0.44987,-0.02952,0.08474],"tcp_to_object_dist_end":0.02735,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.45492,-0.03207,0.0237],"object_pos_start":[0.45492,-0.03207,0.02369],"object_to_goal_dist_end":0.12626,"object_to_goal_dist_start":0.12626,"object_z_max":0.02369,"peak_contact_force":128.80471,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4.0,"raw_peak_contact_force":128.80471,"subtask_id":"goal_reach","tcp_end":[0.46725,-0.03241,0.04815],"tcp_start":[0.4672,-0.03241,0.04813],"tcp_to_object_dist_end":0.02739,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.61364,"average_solve_count":88.0,"average_success_count":88.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.07718,"contact_1.speed":0.04983,"push_1.speed":0.0332,"retract_1.speed":0.05064},"optimized_scores":{"best_composite_score":-0.14926,"best_fitness_score":0.11074,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":319.0,"contact_point_centroid":[0.56828,0.00125,0.04709],"force_p95":228.39587,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":229.26318,"mean_force":178.20307,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.55679,0.0012,0.04901]},{"body_a":"world","body_b":"push_box","contact_count":1916.0,"contact_point_centroid":[0.55483,0.00137,-0.0003],"force_p95":106.26938,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":113.22204,"mean_force":29.99957,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.55275,0.00118,0.05503]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.57887,0.00127,0.04577],"force_p95":109.66536,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":109.66536,"mean_force":109.66536,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.56725,0.00125,0.04681]},{"body_a":"world","body_b":"push_box","contact_count":4.0,"contact_point_centroid":[0.55753,0.00138,-0.00058],"force_p95":48.11924,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":48.5479,"mean_force":27.72724,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.56725,0.00125,0.04681]},{"body_a":"world","body_b":"push_box","contact_count":3020.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52195,0.00058,0.19096]}],"total_contact_groups":5},"final_pose_error":0.16698,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.55851,0.00138,0.02382],"final_tcp_position":[0.5673,0.00125,0.04684],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":229.26318,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":755.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3020.0,"raw_peak_contact_force":0.24534,"subtask_id":"pre_contact","tcp_end":[0.5463,0.00118,0.08225],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.05767,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":479.0,"n_steps_budget":750.0,"object_pos_end":[0.55851,0.00138,0.02381],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.1623,"object_to_goal_dist_start":0.16043,"object_z_max":0.02499,"peak_contact_force":222.2834,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2235.0,"raw_peak_contact_force":229.26318,"subtask_id":"pre_contact","tcp_end":[0.56725,0.00125,0.04681],"tcp_start":[0.5463,0.00118,0.08225],"tcp_to_object_dist_end":0.02461,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.55851,0.00138,0.02382],"object_pos_start":[0.55851,0.00138,0.02381],"object_to_goal_dist_end":0.1623,"object_to_goal_dist_start":0.1623,"object_z_max":0.02381,"peak_contact_force":109.66536,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":5.0,"raw_peak_contact_force":109.66536,"subtask_id":"goal_reach","tcp_end":[0.5673,0.00125,0.04684],"tcp_start":[0.56725,0.00125,0.04681],"tcp_to_object_dist_end":0.02464,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.95522,"average_solve_count":134.0,"average_success_count":134.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.0437,"contact_1.speed":0.04942,"push_1.speed":0.06065,"retract_1.speed":0.12999},"optimized_scores":{"best_composite_score":-0.15569,"best_fitness_score":0.10431,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":320.0,"contact_point_centroid":[0.55209,0.03632,0.04698],"force_p95":232.99134,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":234.89227,"mean_force":184.26674,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54073,0.03636,0.04924]},{"body_a":"world","body_b":"push_box","contact_count":1924.0,"contact_point_centroid":[0.5382,0.03714,-0.00031],"force_p95":109.10618,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":116.02098,"mean_force":30.97796,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53679,0.03583,0.05537]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.56262,0.03728,0.04566],"force_p95":112.43116,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":112.43116,"mean_force":112.43116,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.55112,0.03743,0.04707]},{"body_a":"world","body_b":"push_box","contact_count":4.0,"contact_point_centroid":[0.54082,0.03747,-0.00059],"force_p95":50.19883,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":50.69545,"mean_force":28.42407,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.55112,0.03743,0.04707]},{"body_a":"world","body_b":"push_box","contact_count":3184.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51421,0.017,0.19121]}],"total_contact_groups":5},"final_pose_error":0.19555,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.54184,0.03748,0.0238],"final_tcp_position":[0.55117,0.03744,0.0471],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":234.89227,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":796.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3184.0,"raw_peak_contact_force":0.24534,"subtask_id":"pre_contact","tcp_end":[0.53071,0.03451,0.0827],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.05806,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":481.0,"n_steps_budget":750.0,"object_pos_end":[0.54184,0.03748,0.02379],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.19209,"object_to_goal_dist_start":0.1905,"object_z_max":0.02499,"peak_contact_force":226.86814,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2244.0,"raw_peak_contact_force":234.89227,"subtask_id":"pre_contact","tcp_end":[0.55112,0.03743,0.04707],"tcp_start":[0.53071,0.03451,0.0827],"tcp_to_object_dist_end":0.02506,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.54184,0.03748,0.0238],"object_pos_start":[0.54184,0.03748,0.02379],"object_to_goal_dist_end":0.19209,"object_to_goal_dist_start":0.19209,"object_z_max":0.02379,"peak_contact_force":112.43116,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":5.0,"raw_peak_contact_force":112.43116,"subtask_id":"goal_reach","tcp_end":[0.55117,0.03744,0.0471],"tcp_start":[0.55112,0.03743,0.04707],"tcp_to_object_dist_end":0.0251,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```