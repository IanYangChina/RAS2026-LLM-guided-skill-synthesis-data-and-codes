## Search State

- **Seed**: 3
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4582 | 0.64 | ✅ accepted |
| 2 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | -0.0256 | 0.00 | ❌ rejected |
| 1 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 4 | -0.1426 | 0.01 | ❌ rejected |
| 0 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4526 | 0.63 | ✅ accepted |

**Proposal policy**: task_score is 0.64 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.458) — your mutation base

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

- **Composite score**: 0.458
- **task_score** (E): 0.642
- **fitness_score**: 0.668  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.210

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2842 |
| contact_1 | 1.00 | 1.00 | 0.0497 |
| push_1 | 1.00 | 1.00 | 0.1257 |
| retract_1 | 0.00 | 1.00 | 0.1666 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.509, 0.078, 0.032) | (0.513, 0.002, 0.025)→(0.513, 0.002, 0.025) | 0.160→0.160 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / step_budget | (0.509, 0.078, 0.032)→(0.509, 0.030, 0.020) | (0.513, 0.002, 0.025)→(0.516, -0.007, 0.025) | 0.160→0.151 | 1.00 / 2.667 | 3.507 | 8.811 |
| push_1 | push | 1.00 / step_budget | (0.509, 0.030, 0.020)→(0.504, -0.090, 0.026) | (0.516, -0.007, 0.025)→(0.511, -0.114, 0.029) | 0.151→0.057 | 1.00 / 3.333 | 79.483 | 109.313 |
| retract_1 | retract | 0.00 / step_budget | (0.504, -0.090, 0.026)→(0.497, 0.060, 0.099) | (0.511, -0.114, 0.029)→(0.506, -0.110, 0.025) | 0.057→0.058 | 1.00 / 4.000 | 0.245 | 58.671 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.879
- lateral_force_integral: None
- approach_alignment: 0.435
- goal_progress: 0.669
- terminal_score: 0.669
- phase_score: 0.852
- phase_breakdown.contact_score: 0.888
- phase_breakdown.approach_score: 0.820
- phase_breakdown.push_score: 0.844

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.779
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.669
- **Median Q (composite search score)**: 0.439
- **K-run variance**: 0.0070
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.354


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.24887,"average_solve_count":221.0,"average_success_count":221.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.02365,"contact_1.speed":0.03209,"push_1.push_depth":0.09096},"optimized_scores":{"best_composite_score":0.56901,"best_fitness_score":0.77901,"best_task_score":0.66878},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1305.0,"contact_point_centroid":[0.46034,-0.11421,-7e-05],"force_p95":42.98698,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":58.51339,"mean_force":8.02208,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47318,-0.07492,0.01945]},{"body_a":"attachment","body_b":"push_box","contact_count":622.0,"contact_point_centroid":[0.47387,-0.06915,0.0339],"force_p95":30.20314,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":41.61199,"mean_force":11.49084,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46663,-0.05766,0.01959]},{"body_a":"push_box","body_b":"link7","contact_count":246.0,"contact_point_centroid":[0.48111,-0.04688,0.05058],"force_p95":28.24304,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":34.37526,"mean_force":20.25104,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.45354,-0.02207,0.02019]},{"body_a":"world","body_b":"push_box","contact_count":3299.0,"contact_point_centroid":[0.45061,-0.03342,-1e-05],"force_p95":2.35302,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.9987,"mean_force":0.50123,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.44572,0.02139,0.02625]},{"body_a":"attachment","body_b":"push_box","contact_count":187.0,"contact_point_centroid":[0.45432,-0.01104,0.03488],"force_p95":7.68429,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.99108,"mean_force":3.86279,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.44611,0.00087,0.02234]},{"body_a":"push_box","body_b":"link7","contact_count":41.0,"contact_point_centroid":[0.47663,-0.02239,0.05001],"force_p95":4.24058,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.41157,"mean_force":3.44001,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.44629,-0.00286,0.0217]},{"body_a":"world","body_b":"push_box","contact_count":3987.0,"contact_point_centroid":[0.45785,-0.14421,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.87817,"mean_force":0.24588,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49138,-0.04678,0.05202]},{"body_a":"world","body_b":"push_box","contact_count":3712.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47374,0.02259,0.16679]}],"total_contact_groups":8},"final_pose_error":0.13758,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.45786,-0.14421,0.02499],"final_tcp_position":[0.4933,0.0277,0.08733],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":58.51339,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":928.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3712.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.4489,0.04564,0.03445],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07781,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":918.0,"n_steps_budget":1000.0,"object_pos_end":[0.45172,-0.04063,0.02504],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.11956,"object_to_goal_dist_start":0.12843,"object_z_max":0.02507,"peak_contact_force":7.3026,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3527.0,"raw_peak_contact_force":9.9987,"tcp_end":[0.44635,-0.0038,0.02155],"tcp_start":[0.4489,0.04564,0.03445],"tcp_to_object_dist_end":0.03738,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":783.0,"n_steps_budget":870.0,"object_pos_end":[0.45821,-0.14378,0.02502],"object_pos_start":[0.45172,-0.04063,0.02504],"object_to_goal_dist_end":0.04225,"object_to_goal_dist_start":0.11956,"object_z_max":0.03116,"peak_contact_force":1.50886,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2173.0,"raw_peak_contact_force":58.51339,"tcp_end":[0.49328,-0.12458,0.01986],"tcp_start":[0.44635,-0.0038,0.02155],"tcp_to_object_dist_end":0.04032,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45786,-0.14421,0.02499],"object_pos_start":[0.45821,-0.14378,0.02502],"object_to_goal_dist_end":0.04254,"object_to_goal_dist_start":0.04225,"object_z_max":0.02505,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3987.0,"raw_peak_contact_force":0.87817,"tcp_end":[0.4933,0.0277,0.08733],"tcp_start":[0.49328,-0.12458,0.01986],"tcp_to_object_dist_end":0.18627,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.73125,"average_solve_count":160.0,"average_success_count":160.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.09737,"contact_1.speed":0.03536,"push_1.push_depth":0.09881},"optimized_scores":{"best_composite_score":0.43896,"best_fitness_score":0.64896,"best_task_score":0.63192},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":805.0,"contact_point_centroid":[0.56265,-0.04458,0.05412],"force_p95":124.70819,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":140.38951,"mean_force":82.05577,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52777,-0.02994,0.0239]},{"body_a":"world","body_b":"push_box","contact_count":1591.0,"contact_point_centroid":[0.5571,-0.07738,-0.00035],"force_p95":92.97041,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":106.61112,"mean_force":53.10009,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52764,-0.03041,0.02397]},{"body_a":"attachment","body_b":"push_box","contact_count":805.0,"contact_point_centroid":[0.54676,-0.03838,0.05412],"force_p95":84.06513,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":87.18149,"mean_force":52.14428,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52778,-0.02992,0.0239]},{"body_a":"world","body_b":"push_box","contact_count":3679.0,"contact_point_centroid":[0.53629,-0.10328,-3e-05],"force_p95":0.30325,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":83.90651,"mean_force":0.52068,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50284,-0.00693,0.06657]},{"body_a":"push_box","body_b":"link7","contact_count":51.0,"contact_point_centroid":[0.55063,-0.09436,0.05724],"force_p95":65.96884,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":76.23362,"mean_force":28.5747,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50899,-0.08577,0.03095]},{"body_a":"attachment","body_b":"push_box","contact_count":67.0,"contact_point_centroid":[0.53322,-0.08751,0.06175],"force_p95":45.66985,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":69.51832,"mean_force":16.12849,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50836,-0.08306,0.03158]},{"body_a":"attachment","body_b":"push_box","contact_count":173.0,"contact_point_centroid":[0.55443,0.02178,0.03922],"force_p95":5.81042,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.81576,"mean_force":2.35122,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54768,0.03376,0.02018]},{"body_a":"world","body_b":"push_box","contact_count":2849.0,"contact_point_centroid":[0.55333,-0.00125,-1e-05],"force_p95":1.72633,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.77018,"mean_force":0.39793,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.5452,0.05467,0.02309]},{"body_a":"world","body_b":"push_box","contact_count":3820.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5223,0.03842,0.16453]}],"total_contact_groups":9},"final_pose_error":0.10154,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53578,-0.10302,0.02499],"final_tcp_position":[0.50013,0.06119,0.10078],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":140.38951,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":955.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3820.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.54657,0.07718,0.03124],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07637,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":822.0,"n_steps_budget":930.0,"object_pos_end":[0.556,-0.00795,0.02509],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.15269,"object_to_goal_dist_start":0.16043,"object_z_max":0.0252,"peak_contact_force":1.12075,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3022.0,"raw_peak_contact_force":7.81576,"tcp_end":[0.54831,0.02887,0.01957],"tcp_start":[0.54657,0.07718,0.03124],"tcp_to_object_dist_end":0.03802,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":811.0,"n_steps_budget":900.0,"object_pos_end":[0.54133,-0.11429,0.03119],"object_pos_start":[0.556,-0.00795,0.02509],"object_to_goal_dist_end":0.05497,"object_to_goal_dist_start":0.15269,"object_z_max":0.0312,"peak_contact_force":123.85518,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3201.0,"raw_peak_contact_force":140.38951,"tcp_end":[0.51017,-0.08994,0.02988],"tcp_start":[0.54831,0.02887,0.01957],"tcp_to_object_dist_end":0.03958,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53578,-0.10302,0.02499],"object_pos_start":[0.54133,-0.11429,0.03119],"object_to_goal_dist_end":0.05905,"object_to_goal_dist_start":0.05497,"object_z_max":0.03459,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3797.0,"raw_peak_contact_force":83.90651,"tcp_end":[0.50013,0.06119,0.10078],"tcp_start":[0.51017,-0.08994,0.02988],"tcp_to_object_dist_end":0.18434,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.74522,"average_solve_count":157.0,"average_success_count":157.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.09999,"contact_1.speed":0.03714,"push_1.push_depth":0.0994},"optimized_scores":{"best_composite_score":0.3667,"best_fitness_score":0.5767,"best_task_score":0.62398},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":807.0,"contact_point_centroid":[0.54963,-0.01071,0.05461],"force_p95":114.15481,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":129.03483,"mean_force":75.02228,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5182,0.00498,0.02343]},{"body_a":"attachment","body_b":"push_box","contact_count":803.0,"contact_point_centroid":[0.53664,-0.00417,0.05187],"force_p95":99.14015,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":107.24413,"mean_force":55.71769,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51814,0.0047,0.02345]},{"body_a":"world","body_b":"push_box","contact_count":1548.0,"contact_point_centroid":[0.54415,-0.04557,-0.00031],"force_p95":78.00652,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":95.99973,"mean_force":50.81887,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51795,0.00333,0.02364]},{"body_a":"push_box","body_b":"link7","contact_count":44.0,"contact_point_centroid":[0.54897,-0.06212,0.05581],"force_p95":83.2025,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":91.22689,"mean_force":38.78552,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50674,-0.05195,0.03018]},{"body_a":"world","body_b":"push_box","contact_count":3692.0,"contact_point_centroid":[0.52514,-0.08273,-3e-05],"force_p95":0.25384,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":84.08468,"mean_force":0.48467,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50091,0.02398,0.07092]},{"body_a":"attachment","body_b":"push_box","contact_count":63.0,"contact_point_centroid":[0.52825,-0.05497,0.05966],"force_p95":61.94683,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":81.65909,"mean_force":21.92598,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50596,-0.04872,0.03119]},{"body_a":"attachment","body_b":"push_box","contact_count":161.0,"contact_point_centroid":[0.53835,0.05735,0.03858],"force_p95":6.82028,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.61911,"mean_force":2.36352,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53127,0.0693,0.02039]},{"body_a":"world","body_b":"push_box","contact_count":2556.0,"contact_point_centroid":[0.53688,0.03446,-1e-05],"force_p95":1.62885,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.33559,"mean_force":0.40329,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52922,0.08948,0.02307]},{"body_a":"world","body_b":"push_box","contact_count":3964.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51453,0.05557,0.16387]}],"total_contact_groups":9},"final_pose_error":0.0725,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52461,-0.08273,0.02499],"final_tcp_position":[0.4987,0.0897,0.10977],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":129.03483,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":991.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3964.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.5309,0.1113,0.0307],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07478,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":739.0,"n_steps_budget":840.0,"object_pos_end":[0.53944,0.02754,0.02507],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.18186,"object_to_goal_dist_start":0.1905,"object_z_max":0.02514,"peak_contact_force":2.0968,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2717.0,"raw_peak_contact_force":8.61911,"tcp_end":[0.53185,0.06442,0.01984],"tcp_start":[0.5309,0.1113,0.0307],"tcp_to_object_dist_end":0.03802,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":810.0,"n_steps_budget":900.0,"object_pos_end":[0.53304,-0.08452,0.03128],"object_pos_start":[0.53944,0.02754,0.02507],"object_to_goal_dist_end":0.07362,"object_to_goal_dist_start":0.18186,"object_z_max":0.03131,"peak_contact_force":113.08527,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3158.0,"raw_peak_contact_force":129.03483,"tcp_end":[0.50761,-0.05516,0.02894],"tcp_start":[0.53185,0.06442,0.01984],"tcp_to_object_dist_end":0.03891,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52461,-0.08273,0.02499],"object_pos_start":[0.53304,-0.08452,0.03128],"object_to_goal_dist_end":0.07163,"object_to_goal_dist_start":0.07362,"object_z_max":0.03468,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3799.0,"raw_peak_contact_force":91.22689,"tcp_end":[0.4987,0.0897,0.10977],"tcp_start":[0.50761,-0.05516,0.02894],"tcp_to_object_dist_end":0.19389,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```