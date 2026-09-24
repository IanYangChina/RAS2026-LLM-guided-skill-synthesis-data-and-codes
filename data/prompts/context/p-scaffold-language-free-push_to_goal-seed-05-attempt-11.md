## Search State

- **Seed**: 5
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → contact → push → retract | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4762 | 0.76 | ❌ rejected |
| 10 | approach → contact → push → retract | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4729 | 0.75 | ❌ rejected |
| 9 | approach → contact → push → retract | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.1492 | 0.31 | ❌ rejected |
| 8 | approach → contact → push → retract | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4711 | 0.75 | ❌ rejected |
| 7 | approach → contact → push → retract | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4632 | 0.73 | ❌ rejected |

**Proposal policy**: task_score is 0.76 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `b2a76c5d1121259d09d3db2c62740fd8fe93dd873d8f379ba1928ff319a7d266`
- Frozen object start: [0.5366003508494456, 0.03695289476837925, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.5366003508494456, 0.03695289476837925, 0.025)
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
  frozen_object_start: [0.5366, 0.037, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.5366003508494456, 0.03695289476837925, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [-0.0366, -0.187, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: b2a76c5d1121259d09d3db2c62740fd8fe93dd873d8f379ba1928ff319a7d266

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.763, which indicates the subtask decomposition is already effective.
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
| `object` | offset from object initial position (0.5366003508494456, 0.03695289476837925, 0.025) | approach/contact targets near object start |
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

## Current Skill (Q=0.476) — your mutation base

```yaml
skill: push_to_goal
phases:
- id: approach_1
  type: approach
  generator: arc_cartesian
  control: force_threshold_switch
  termination: pose_tolerance
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
  generator: impedance_motion
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
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.2

```

## Design Metrics

- **Composite score**: 0.476
- **task_score** (E): 0.756
- **fitness_score**: 0.686  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.210

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2855 |
| contact_1 | 1.00 | 1.00 | 0.0538 |
| push_1 | 1.00 | 1.00 | 0.1269 |
| retract_1 | 0.00 | 1.00 | 0.1655 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.514, 0.101, 0.036) | (0.519, 0.022, 0.025)→(0.519, 0.022, 0.025) | 0.173→0.173 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / step_budget | (0.514, 0.101, 0.036)→(0.514, 0.050, 0.020) | (0.519, 0.022, 0.025)→(0.521, 0.013, 0.025) | 0.173→0.165 | 1.00 / 3.333 | 3.688 | 9.002 |
| push_1 | push | 1.00 / step_budget | (0.514, 0.050, 0.020)→(0.500, -0.076, 0.023) | (0.521, 0.013, 0.025)→(0.511, -0.110, 0.027) | 0.165→0.047 | 1.00 / 3.000 | 40.499 | 85.496 |
| retract_1 | retract | 0.00 / step_budget | (0.500, -0.076, 0.023)→(0.496, 0.069, 0.101) | (0.511, -0.110, 0.027)→(0.508, -0.110, 0.025) | 0.047→0.046 | 1.00 / 4.000 | 0.245 | 28.558 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.426
- goal_progress: 0.945
- terminal_score: 0.945
- phase_score: 0.848
- phase_breakdown.approach_score: 0.820
- phase_breakdown.push_score: 0.845
- phase_breakdown.contact_score: 0.871

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.887
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.945
- **Median Q (composite search score)**: 0.391
- **K-run variance**: 0.0203
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Parameters at upper bound**: push_1.push_depth
- **Final σ (mean)**: 0.341


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `7ff7a4e3a1b03e3d7ba3d0b298d1ee8847b5344eb55f2aa0aaf582e7a98ab8ac`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `028a6956ebe09ab7c7952341570355f52da12e46fb22d3462091c70c024324ff`; realized-scene SHA-256: `b2a76c5d1121259d09d3db2c62740fd8fe93dd873d8f379ba1928ff319a7d266`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5366,0.03695,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.0366,-0.18695,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5366,0.03695,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.70482,"average_solve_count":166.0,"average_success_count":166.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.speed":0.03116,"push_1.push_depth":0.1,"retract_1.retract_height":0.09542},"optimized_scores":{"best_composite_score":0.36057,"best_fitness_score":0.57057,"best_task_score":0.61916},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":799.0,"contact_point_centroid":[0.55021,-0.01152,0.05471],"force_p95":116.40067,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":134.02415,"mean_force":77.95872,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51828,0.0038,0.0237]},{"body_a":"attachment","body_b":"push_box","contact_count":801.0,"contact_point_centroid":[0.537,-0.00475,0.05211],"force_p95":101.60244,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":112.92001,"mean_force":56.43784,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51832,0.00395,0.02369]},{"body_a":"world","body_b":"push_box","contact_count":1536.0,"contact_point_centroid":[0.54444,-0.04756,-0.00032],"force_p95":80.68338,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":98.18356,"mean_force":52.41583,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.518,0.00206,0.02392]},{"body_a":"push_box","body_b":"link7","contact_count":45.0,"contact_point_centroid":[0.54937,-0.06116,0.05587],"force_p95":78.2352,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":82.85752,"mean_force":38.37846,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50685,-0.05255,0.03033]},{"body_a":"attachment","body_b":"push_box","contact_count":67.0,"contact_point_centroid":[0.52761,-0.0549,0.05851],"force_p95":58.85623,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":63.69569,"mean_force":20.12298,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50599,-0.04885,0.03153]},{"body_a":"world","body_b":"push_box","contact_count":3679.0,"contact_point_centroid":[0.52587,-0.08204,-3e-05],"force_p95":0.25475,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":57.2105,"mean_force":0.50092,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50101,0.02376,0.07115]},{"body_a":"attachment","body_b":"push_box","contact_count":208.0,"contact_point_centroid":[0.53795,0.05708,0.03818],"force_p95":6.32877,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.18062,"mean_force":2.48668,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.5313,0.06904,0.02109]},{"body_a":"world","body_b":"push_box","contact_count":3487.0,"contact_point_centroid":[0.53691,0.03467,-1e-05],"force_p95":1.81171,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.54878,"mean_force":0.40082,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52895,0.09065,0.02594]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51292,0.07216,0.17685]}],"total_contact_groups":9},"final_pose_error":0.07264,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52532,-0.08201,0.02499],"final_tcp_position":[0.49875,0.0895,0.10982],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":134.02415,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.53035,0.11538,0.03637],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07949,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":988.0,"n_steps_budget":1000.0,"object_pos_end":[0.53989,0.02704,0.02503],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.18148,"object_to_goal_dist_start":0.1905,"object_z_max":0.02509,"peak_contact_force":4.22911,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3695.0,"raw_peak_contact_force":7.18062,"tcp_end":[0.53191,0.06392,0.02001],"tcp_start":[0.53035,0.11538,0.03637],"tcp_to_object_dist_end":0.03807,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":807.0,"n_steps_budget":900.0,"object_pos_end":[0.5342,-0.08424,0.03125],"object_pos_start":[0.53989,0.02704,0.02503],"object_to_goal_dist_end":0.07438,"object_to_goal_dist_start":0.18148,"object_z_max":0.03128,"peak_contact_force":115.58596,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3136.0,"raw_peak_contact_force":134.02415,"tcp_end":[0.50778,-0.05586,0.02911],"tcp_start":[0.53191,0.06392,0.02001],"tcp_to_object_dist_end":0.03884,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52532,-0.08201,0.02499],"object_pos_start":[0.5342,-0.08424,0.03125],"object_to_goal_dist_end":0.07255,"object_to_goal_dist_start":0.07438,"object_z_max":0.03501,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3791.0,"raw_peak_contact_force":82.85752,"tcp_end":[0.49875,0.0895,0.10982],"tcp_start":[0.50778,-0.05586,0.02911],"tcp_to_object_dist_end":0.19318,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1c6409cc6d884b90ecc3937d36e5ea87cc4ef513b6f301a9da66b4e84390f805`; realized-scene SHA-256: `5f9daa62d5a7a2b8a7116f2dfbb5f9857bb0d5d4b297d304a4e76a9a270e7ec7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50458,-0.01881,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.00458,-0.13119,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.50458,-0.01881,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.71795,"average_solve_count":156.0,"average_success_count":156.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.speed":0.03741,"push_1.push_depth":0.09974,"retract_1.retract_height":0.19213},"optimized_scores":{"best_composite_score":0.6769,"best_fitness_score":0.8869,"best_task_score":0.94524},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1128.0,"contact_point_centroid":[0.50677,-0.1084,-0.00011],"force_p95":56.6629,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":74.76942,"mean_force":17.63879,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49752,-0.05772,0.01952]},{"body_a":"push_box","body_b":"link7","contact_count":421.0,"contact_point_centroid":[0.52527,-0.0472,0.05198],"force_p95":42.45146,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":54.7956,"mean_force":28.21151,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49877,-0.02508,0.01974]},{"body_a":"attachment","body_b":"push_box","contact_count":728.0,"contact_point_centroid":[0.50955,-0.06489,0.04065],"force_p95":44.94435,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":54.15812,"mean_force":18.2982,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49764,-0.05345,0.01949]},{"body_a":"attachment","body_b":"push_box","contact_count":155.0,"contact_point_centroid":[0.50737,0.00196,0.03669],"force_p95":7.25954,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.38855,"mean_force":3.1073,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49973,0.01382,0.02132]},{"body_a":"world","body_b":"push_box","contact_count":3047.0,"contact_point_centroid":[0.50492,-0.02076,-1e-05],"force_p95":1.76698,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.39551,"mean_force":0.40954,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49816,0.03694,0.02522]},{"body_a":"world","body_b":"push_box","contact_count":3966.0,"contact_point_centroid":[0.4992,-0.15717,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.90867,"mean_force":0.24771,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49334,-0.04178,0.05272]},{"body_a":"attachment","body_b":"push_box","contact_count":2.0,"contact_point_centroid":[0.49621,-0.1317,0.01981],"force_p95":0.51406,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.52682,"mean_force":0.39928,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49599,-0.11973,0.01987]},{"body_a":"world","body_b":"push_box","contact_count":3580.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4992,0.04658,0.17199]}],"total_contact_groups":8},"final_pose_error":0.13306,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49911,-0.15713,0.02499],"final_tcp_position":[0.49455,0.03217,0.08843],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":74.76942,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":895.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3580.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.50029,0.06252,0.03384],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08192,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":850.0,"n_steps_budget":960.0,"object_pos_end":[0.50686,-0.02771,0.02498],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.12249,"object_to_goal_dist_start":0.13127,"object_z_max":0.02515,"peak_contact_force":0.00036,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3202.0,"raw_peak_contact_force":9.38855,"tcp_end":[0.50011,0.00908,0.02058],"tcp_start":[0.50029,0.06252,0.03384],"tcp_to_object_dist_end":0.03766,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":775.0,"n_steps_budget":870.0,"object_pos_end":[0.49916,-0.15657,0.02506],"object_pos_start":[0.50686,-0.02771,0.02498],"object_to_goal_dist_end":0.00663,"object_to_goal_dist_start":0.12249,"object_z_max":0.02777,"peak_contact_force":2.01734,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2277.0,"raw_peak_contact_force":74.76942,"tcp_end":[0.496,-0.11968,0.01988],"tcp_start":[0.50011,0.00908,0.02058],"tcp_to_object_dist_end":0.03739,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49911,-0.15713,0.02499],"object_pos_start":[0.49916,-0.15657,0.02506],"object_to_goal_dist_end":0.00719,"object_to_goal_dist_start":0.00663,"object_z_max":0.02507,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3968.0,"raw_peak_contact_force":0.90867,"tcp_end":[0.49455,0.03217,0.08843],"tcp_start":[0.496,-0.11968,0.01988],"tcp_to_object_dist_end":0.19971,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `f52ec1899e2888770a8b6b3ae605718303ef4b10e72cfd7d20ce53303721b2b0`; realized-scene SHA-256: `c8d09cd43835becf8e5eb4413394fad8627e4bf404e9e7726e9f380b60e09752`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51501,0.04767,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.01501,-0.19767,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.51501,0.04767,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.75974,"average_solve_count":154.0,"average_success_count":154.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.speed":0.04517,"push_1.push_depth":0.09977,"retract_1.retract_height":0.12873},"optimized_scores":{"best_composite_score":0.39114,"best_fitness_score":0.60114,"best_task_score":0.70225},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1040.0,"contact_point_centroid":[0.507,-0.03537,-9e-05],"force_p95":26.66481,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":47.69497,"mean_force":6.86825,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50224,0.01393,0.01862]},{"body_a":"push_box","body_b":"link7","contact_count":207.0,"contact_point_centroid":[0.5319,0.02406,0.0511],"force_p95":33.83704,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":46.74893,"mean_force":13.9468,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50558,0.04689,0.01855]},{"body_a":"attachment","body_b":"push_box","contact_count":574.0,"contact_point_centroid":[0.5115,-0.00399,0.0374],"force_p95":26.07131,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":34.45417,"mean_force":8.38275,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50167,0.0076,0.01873]},{"body_a":"attachment","body_b":"push_box","contact_count":130.0,"contact_point_centroid":[0.51587,0.06843,0.03446],"force_p95":8.7613,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.43736,"mean_force":3.88577,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50999,0.08026,0.02166]},{"body_a":"world","body_b":"push_box","contact_count":2463.0,"contact_point_centroid":[0.51509,0.04587,-1e-05],"force_p95":2.29834,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.688,"mean_force":0.45655,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50828,0.10153,0.02666]},{"body_a":"world","body_b":"push_box","contact_count":3984.0,"contact_point_centroid":[0.50058,-0.09099,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.90657,"mean_force":0.24705,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49392,0.01807,0.061]},{"body_a":"attachment","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.5114,-0.06496,0.05006],"force_p95":1.03189,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.03211,"mean_force":1.00959,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49635,-0.05316,0.0199]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50358,0.07681,0.17794]}],"total_contact_groups":8},"final_pose_error":0.078,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50064,-0.09098,0.02499],"final_tcp_position":[0.49534,0.08659,0.10481],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":47.69497,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.51015,0.12542,0.03668],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07878,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":685.0,"n_steps_budget":780.0,"object_pos_end":[0.51729,0.03889,0.02489],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.18968,"object_to_goal_dist_start":0.19823,"object_z_max":0.02512,"peak_contact_force":6.83483,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2593.0,"raw_peak_contact_force":10.43736,"tcp_end":[0.51045,0.07562,0.02066],"tcp_start":[0.51015,0.12542,0.03668],"tcp_to_object_dist_end":0.0376,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":702.0,"n_steps_budget":870.0,"object_pos_end":[0.50062,-0.09001,0.02505],"object_pos_start":[0.51729,0.03889,0.02489],"object_to_goal_dist_end":0.05999,"object_to_goal_dist_start":0.18968,"object_z_max":0.02679,"peak_contact_force":3.89501,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1821.0,"raw_peak_contact_force":47.69497,"tcp_end":[0.49639,-0.05306,0.01993],"tcp_start":[0.51045,0.07562,0.02066],"tcp_to_object_dist_end":0.03754,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50064,-0.09098,0.02499],"object_pos_start":[0.50062,-0.09001,0.02505],"object_to_goal_dist_end":0.05902,"object_to_goal_dist_start":0.05999,"object_z_max":0.02505,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3987.0,"raw_peak_contact_force":1.90657,"tcp_end":[0.49534,0.08659,0.10481],"tcp_start":[0.49639,-0.05306,0.01993],"tcp_to_object_dist_end":0.19476,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```