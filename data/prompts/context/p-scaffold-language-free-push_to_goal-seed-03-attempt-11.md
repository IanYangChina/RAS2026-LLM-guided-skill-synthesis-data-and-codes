## Search State

- **Seed**: 3
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4593 | 0.65 | ❌ rejected |
| 10 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4794 | 0.72 | ❌ rejected |
| 9 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4570 | 0.64 | ❌ rejected |
| 8 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4557 | 0.63 | ❌ rejected |
| 7 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 5 | 0.2069 | 0.41 | ❌ rejected |

**Proposal policy**: task_score is 0.65 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.459) — your mutation base

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

- **Composite score**: 0.459
- **task_score** (E): 0.646
- **fitness_score**: 0.669  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.210

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2843 |
| contact_1 | 1.00 | 1.00 | 0.0496 |
| push_1 | 1.00 | 1.00 | 0.1249 |
| retract_1 | 0.00 | 1.00 | 0.1662 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.509, 0.078, 0.032) | (0.513, 0.002, 0.025)→(0.513, 0.002, 0.025) | 0.160→0.160 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / step_budget | (0.509, 0.078, 0.032)→(0.509, 0.030, 0.020) | (0.513, 0.002, 0.025)→(0.516, -0.007, 0.025) | 0.160→0.151 | 1.00 / 2.667 | 4.947 | 9.846 |
| push_1 | push | 1.00 / step_budget | (0.509, 0.030, 0.020)→(0.504, -0.089, 0.026) | (0.516, -0.007, 0.025)→(0.511, -0.113, 0.029) | 0.151→0.057 | 1.00 / 4.000 | 83.875 | 109.686 |
| retract_1 | retract | 0.00 / step_budget | (0.504, -0.089, 0.026)→(0.497, 0.060, 0.099) | (0.511, -0.113, 0.029)→(0.506, -0.110, 0.025) | 0.057→0.057 | 1.00 / 4.000 | 0.245 | 58.903 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.858
- lateral_force_integral: None
- approach_alignment: 0.431
- goal_progress: 0.661
- terminal_score: 0.661
- phase_score: 0.846
- phase_breakdown.contact_score: 0.889
- phase_breakdown.approach_score: 0.821
- phase_breakdown.push_score: 0.829

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.772
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.661
- **Median Q (composite search score)**: 0.453
- **K-run variance**: 0.0066
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.254


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.25346,"average_solve_count":217.0,"average_success_count":217.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.04952,"contact_1.speed":0.0315,"push_1.push_depth":0.08722},"optimized_scores":{"best_composite_score":0.56172,"best_fitness_score":0.77172,"best_task_score":0.661},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1301.0,"contact_point_centroid":[0.45986,-0.11224,-9e-05],"force_p95":44.65631,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":58.90152,"mean_force":8.67577,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47366,-0.07366,0.01954]},{"body_a":"attachment","body_b":"push_box","contact_count":590.0,"contact_point_centroid":[0.47472,-0.06577,0.03551],"force_p95":31.43543,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":42.80743,"mean_force":13.05798,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46613,-0.05424,0.01973]},{"body_a":"push_box","body_b":"link7","contact_count":261.0,"contact_point_centroid":[0.48181,-0.0472,0.05063],"force_p95":29.24577,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":30.0965,"mean_force":20.71662,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.45413,-0.0224,0.0203]},{"body_a":"world","body_b":"push_box","contact_count":3317.0,"contact_point_centroid":[0.45101,-0.03297,-1e-05],"force_p95":2.37975,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.43497,"mean_force":0.54223,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.44571,0.02128,0.02617]},{"body_a":"attachment","body_b":"push_box","contact_count":186.0,"contact_point_centroid":[0.45423,-0.01104,0.03473],"force_p95":7.96686,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.89439,"mean_force":4.03408,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.44612,0.00086,0.02233]},{"body_a":"push_box","body_b":"link7","contact_count":49.0,"contact_point_centroid":[0.4771,-0.02012,0.04986],"force_p95":8.21082,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.96895,"mean_force":6.12079,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.44632,-0.0026,0.02177]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.48722,-0.13103,0.02269],"force_p95":6.1367,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.1367,"mean_force":6.1367,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49326,-0.12107,0.01984]},{"body_a":"world","body_b":"push_box","contact_count":3981.0,"contact_point_centroid":[0.45731,-0.14151,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44689,"mean_force":0.24726,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49137,-0.04396,0.05215]},{"body_a":"world","body_b":"push_box","contact_count":3708.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47371,0.02262,0.16664]}],"total_contact_groups":9},"final_pose_error":0.13599,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.4573,-0.14149,0.02499],"final_tcp_position":[0.4933,0.02946,0.08741],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":58.90152,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":927.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3708.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.44888,0.04565,0.03434],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07781,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":918.0,"n_steps_budget":1000.0,"object_pos_end":[0.45218,-0.04056,0.02513],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.11943,"object_to_goal_dist_start":0.12843,"object_z_max":0.02514,"peak_contact_force":9.0661,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3552.0,"raw_peak_contact_force":12.43497,"tcp_end":[0.44643,-0.00369,0.02163],"tcp_start":[0.44888,0.04565,0.03434],"tcp_to_object_dist_end":0.03748,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":783.0,"n_steps_budget":870.0,"object_pos_end":[0.45805,-0.14064,0.02492],"object_pos_start":[0.45218,-0.04056,0.02513],"object_to_goal_dist_end":0.04299,"object_to_goal_dist_start":0.11943,"object_z_max":0.03129,"peak_contact_force":16.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2152.0,"raw_peak_contact_force":58.90152,"tcp_end":[0.49326,-0.12099,0.01986],"tcp_start":[0.44643,-0.00369,0.02163],"tcp_to_object_dist_end":0.04064,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4573,-0.14149,0.02499],"object_pos_start":[0.45805,-0.14064,0.02492],"object_to_goal_dist_end":0.04354,"object_to_goal_dist_start":0.04299,"object_z_max":0.0251,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3982.0,"raw_peak_contact_force":6.1367,"tcp_end":[0.4933,0.02946,0.08741],"tcp_start":[0.49326,-0.12099,0.01986],"tcp_to_object_dist_end":0.18552,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.74457,"average_solve_count":184.0,"average_success_count":184.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.07183,"contact_1.speed":0.03204,"push_1.push_depth":0.09901},"optimized_scores":{"best_composite_score":0.4525,"best_fitness_score":0.6625,"best_task_score":0.65961},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":793.0,"contact_point_centroid":[0.56141,-0.04594,0.05429],"force_p95":121.18146,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":137.51052,"mean_force":81.03097,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52734,-0.03125,0.02378]},{"body_a":"world","body_b":"push_box","contact_count":1593.0,"contact_point_centroid":[0.55464,-0.07881,-0.00033],"force_p95":90.46621,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":103.40416,"mean_force":51.41063,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5275,-0.03085,0.02377]},{"body_a":"attachment","body_b":"push_box","contact_count":783.0,"contact_point_centroid":[0.54621,-0.04042,0.05433],"force_p95":85.23718,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":91.62649,"mean_force":53.28101,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52713,-0.03194,0.02387]},{"body_a":"world","body_b":"push_box","contact_count":3685.0,"contact_point_centroid":[0.53533,-0.10799,-3e-05],"force_p95":0.26714,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":82.55141,"mean_force":0.50443,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50285,-0.00764,0.06641]},{"body_a":"push_box","body_b":"link7","contact_count":51.0,"contact_point_centroid":[0.55009,-0.09647,0.05738],"force_p95":65.81138,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":75.15837,"mean_force":27.61775,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50898,-0.08649,0.03086]},{"body_a":"attachment","body_b":"push_box","contact_count":62.0,"contact_point_centroid":[0.53365,-0.08852,0.06177],"force_p95":45.24391,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":65.29134,"mean_force":16.89389,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50847,-0.08436,0.03134]},{"body_a":"attachment","body_b":"push_box","contact_count":196.0,"contact_point_centroid":[0.55372,0.02168,0.03715],"force_p95":5.89685,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.7134,"mean_force":2.58861,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54771,0.03365,0.02015]},{"body_a":"world","body_b":"push_box","contact_count":3174.0,"contact_point_centroid":[0.55343,-0.00105,-1e-05],"force_p95":1.97545,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.64431,"mean_force":0.41205,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54525,0.05418,0.02289]},{"body_a":"world","body_b":"push_box","contact_count":3924.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52231,0.03847,0.16435]}],"total_contact_groups":9},"final_pose_error":0.10195,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53476,-0.10789,0.02499],"final_tcp_position":[0.50014,0.06077,0.10068],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":137.51052,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":981.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3924.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.5466,0.07723,0.03105],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.0764,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":904.0,"n_steps_budget":1000.0,"object_pos_end":[0.55595,-0.00809,0.02521],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.15254,"object_to_goal_dist_start":0.16043,"object_z_max":0.02521,"peak_contact_force":0.70631,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3370.0,"raw_peak_contact_force":7.7134,"tcp_end":[0.54836,0.0287,0.01956],"tcp_start":[0.5466,0.07723,0.03105],"tcp_to_object_dist_end":0.03799,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":806.0,"n_steps_budget":900.0,"object_pos_end":[0.54092,-0.11601,0.03118],"object_pos_start":[0.55595,-0.00809,0.02521],"object_to_goal_dist_end":0.05355,"object_to_goal_dist_start":0.15254,"object_z_max":0.03119,"peak_contact_force":121.60453,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3169.0,"raw_peak_contact_force":137.51052,"tcp_end":[0.51017,-0.09064,0.02984],"tcp_start":[0.54836,0.0287,0.01956],"tcp_to_object_dist_end":0.03988,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53476,-0.10789,0.02499],"object_pos_start":[0.54092,-0.11601,0.03118],"object_to_goal_dist_end":0.05461,"object_to_goal_dist_start":0.05355,"object_z_max":0.03479,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3798.0,"raw_peak_contact_force":82.55141,"tcp_end":[0.50014,0.06077,0.10068],"tcp_start":[0.51017,-0.09064,0.02984],"tcp_to_object_dist_end":0.18808,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.75159,"average_solve_count":157.0,"average_success_count":157.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.09766,"contact_1.speed":0.03914,"push_1.push_depth":0.09973},"optimized_scores":{"best_composite_score":0.36379,"best_fitness_score":0.57379,"best_task_score":0.61679},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":806.0,"contact_point_centroid":[0.55093,-0.01042,0.05449],"force_p95":115.34663,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":132.64631,"mean_force":77.87245,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51845,0.00519,0.02373]},{"body_a":"attachment","body_b":"push_box","contact_count":807.0,"contact_point_centroid":[0.53728,-0.00343,0.05249],"force_p95":100.20491,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":105.36312,"mean_force":56.70337,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51848,0.00528,0.02372]},{"body_a":"world","body_b":"push_box","contact_count":1551.0,"contact_point_centroid":[0.54573,-0.04489,-0.00032],"force_p95":80.94846,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":95.79783,"mean_force":52.48986,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5182,0.00358,0.02393]},{"body_a":"push_box","body_b":"link7","contact_count":44.0,"contact_point_centroid":[0.55026,-0.06008,0.05576],"force_p95":77.81267,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":88.021,"mean_force":37.60476,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5071,-0.05201,0.03052]},{"body_a":"world","body_b":"push_box","contact_count":3686.0,"contact_point_centroid":[0.52657,-0.08177,-3e-05],"force_p95":0.24961,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":77.75121,"mean_force":0.4962,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50117,0.02401,0.07121]},{"body_a":"attachment","body_b":"push_box","contact_count":64.0,"contact_point_centroid":[0.52832,-0.05444,0.05889],"force_p95":53.25316,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":62.12381,"mean_force":20.15632,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50632,-0.04866,0.0316]},{"body_a":"attachment","body_b":"push_box","contact_count":154.0,"contact_point_centroid":[0.53841,0.05746,0.03877],"force_p95":7.69411,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.38899,"mean_force":2.99471,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53128,0.06941,0.02043]},{"body_a":"world","body_b":"push_box","contact_count":2500.0,"contact_point_centroid":[0.53665,0.03458,-1e-05],"force_p95":2.1351,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.15934,"mean_force":0.43749,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52923,0.0894,0.02309]},{"body_a":"world","body_b":"push_box","contact_count":3968.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51454,0.05561,0.16378]}],"total_contact_groups":9},"final_pose_error":0.07246,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52599,-0.08178,0.02499],"final_tcp_position":[0.49883,0.08967,0.10988],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":132.64631,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":992.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3968.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.53089,0.11128,0.03074],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07477,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":714.0,"n_steps_budget":810.0,"object_pos_end":[0.54003,0.02784,0.02498],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.18229,"object_to_goal_dist_start":0.1905,"object_z_max":0.02514,"peak_contact_force":5.0691,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2654.0,"raw_peak_contact_force":9.38899,"tcp_end":[0.53187,0.06463,0.0199],"tcp_start":[0.53089,0.11128,0.03074],"tcp_to_object_dist_end":0.03802,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":810.0,"n_steps_budget":900.0,"object_pos_end":[0.53502,-0.08326,0.0313],"object_pos_start":[0.54003,0.02784,0.02498],"object_to_goal_dist_end":0.07563,"object_to_goal_dist_start":0.18229,"object_z_max":0.03142,"peak_contact_force":114.02154,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3164.0,"raw_peak_contact_force":132.64631,"tcp_end":[0.50804,-0.05528,0.02933],"tcp_start":[0.53187,0.06463,0.0199],"tcp_to_object_dist_end":0.03892,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52599,-0.08178,0.02499],"object_pos_start":[0.53502,-0.08326,0.0313],"object_to_goal_dist_end":0.073,"object_to_goal_dist_start":0.07563,"object_z_max":0.03513,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3794.0,"raw_peak_contact_force":88.021,"tcp_end":[0.49883,0.08967,0.10988],"tcp_start":[0.50804,-0.05528,0.02933],"tcp_to_object_dist_end":0.19324,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```