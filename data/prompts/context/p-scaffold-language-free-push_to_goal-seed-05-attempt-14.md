## Search State

- **Seed**: 5
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → contact → push → retract | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4724 | 0.75 | ❌ rejected |
| 13 | approach → contact → push → retract | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4719 | 0.75 | ❌ rejected |
| 12 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 4 | -0.2080 | 0.00 | ❌ rejected |
| 11 | approach → contact → push → retract | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4762 | 0.76 | ❌ rejected |
| 10 | approach → contact → push → retract | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4729 | 0.75 | ❌ rejected |

**Proposal policy**: task_score is 0.75 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.472) — your mutation base

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

- **Composite score**: 0.472
- **task_score** (E): 0.752
- **fitness_score**: 0.682  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.210

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2855 |
| contact_1 | 1.00 | 1.00 | 0.0535 |
| push_1 | 1.00 | 1.00 | 0.1258 |
| retract_1 | 0.00 | 1.00 | 0.1656 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.514, 0.101, 0.036) | (0.519, 0.022, 0.025)→(0.519, 0.022, 0.025) | 0.173→0.173 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / step_budget | (0.514, 0.101, 0.036)→(0.514, 0.050, 0.020) | (0.519, 0.022, 0.025)→(0.521, 0.013, 0.025) | 0.173→0.165 | 1.00 / 3.333 | 0.890 | 10.927 |
| push_1 | push | 1.00 / step_budget | (0.514, 0.050, 0.020)→(0.501, -0.075, 0.024) | (0.521, 0.013, 0.025)→(0.512, -0.110, 0.029) | 0.165→0.047 | 1.00 / 3.333 | 51.037 | 96.280 |
| retract_1 | retract | 0.00 / step_budget | (0.501, -0.075, 0.024)→(0.497, 0.071, 0.102) | (0.512, -0.110, 0.029)→(0.509, -0.109, 0.025) | 0.047→0.047 | 1.00 / 4.000 | 0.245 | 42.179 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.424
- goal_progress: 0.950
- terminal_score: 0.950
- phase_score: 0.844
- phase_breakdown.approach_score: 0.820
- phase_breakdown.push_score: 0.838
- phase_breakdown.contact_score: 0.871

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.887
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.950
- **Median Q (composite search score)**: 0.380
- **K-run variance**: 0.0209
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.560


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.75159,"average_solve_count":157.0,"average_success_count":157.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.speed":0.04202,"push_1.push_depth":0.09985,"retract_1.retract_height":0.12521},"optimized_scores":{"best_composite_score":0.36068,"best_fitness_score":0.57068,"best_task_score":0.62301},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":786.0,"contact_point_centroid":[0.5489,-0.01147,0.05509],"force_p95":113.76901,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":131.93587,"mean_force":76.41566,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51788,0.00368,0.02371]},{"body_a":"attachment","body_b":"push_box","contact_count":793.0,"contact_point_centroid":[0.53673,-0.00456,0.05241],"force_p95":98.41626,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":104.76436,"mean_force":57.31762,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.518,0.00422,0.02368]},{"body_a":"world","body_b":"push_box","contact_count":1561.0,"contact_point_centroid":[0.54257,-0.04606,-0.00029],"force_p95":78.3627,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":93.26508,"mean_force":50.09342,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51798,0.00393,0.02373]},{"body_a":"push_box","body_b":"link7","contact_count":44.0,"contact_point_centroid":[0.54905,-0.06198,0.05584],"force_p95":79.3548,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":88.74515,"mean_force":38.01286,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50678,-0.05198,0.03023]},{"body_a":"world","body_b":"push_box","contact_count":3693.0,"contact_point_centroid":[0.52526,-0.08259,-3e-05],"force_p95":0.25042,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":85.54455,"mean_force":0.48278,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50097,0.02392,0.07096]},{"body_a":"attachment","body_b":"push_box","contact_count":63.0,"contact_point_centroid":[0.52835,-0.05494,0.05973],"force_p95":60.89049,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":81.39023,"mean_force":21.57824,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50601,-0.04876,0.03125]},{"body_a":"attachment","body_b":"push_box","contact_count":142.0,"contact_point_centroid":[0.53849,0.05741,0.03964],"force_p95":8.54685,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.9316,"mean_force":3.39941,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.5313,0.06935,0.02118]},{"body_a":"world","body_b":"push_box","contact_count":2668.0,"contact_point_centroid":[0.5368,0.0349,-1e-05],"force_p95":1.90099,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.36492,"mean_force":0.43443,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52891,0.09157,0.02621]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51292,0.07216,0.17685]}],"total_contact_groups":9},"final_pose_error":0.0725,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52473,-0.08257,0.02499],"final_tcp_position":[0.49873,0.08969,0.10979],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":131.93587,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.53035,0.11538,0.03637],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07949,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":750.0,"n_steps_budget":840.0,"object_pos_end":[0.53908,0.02799,0.02508],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.18223,"object_to_goal_dist_start":0.1905,"object_z_max":0.0251,"peak_contact_force":1.63931,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2810.0,"raw_peak_contact_force":10.9316,"tcp_end":[0.53187,0.06478,0.02023],"tcp_start":[0.53035,0.11538,0.03637],"tcp_to_object_dist_end":0.0378,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":805.0,"n_steps_budget":900.0,"object_pos_end":[0.53326,-0.08446,0.03127],"object_pos_start":[0.53908,0.02799,0.02508],"object_to_goal_dist_end":0.07377,"object_to_goal_dist_start":0.18223,"object_z_max":0.03136,"peak_contact_force":106.28099,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3140.0,"raw_peak_contact_force":131.93587,"tcp_end":[0.5077,-0.05521,0.02903],"tcp_start":[0.53187,0.06478,0.02023],"tcp_to_object_dist_end":0.03891,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52473,-0.08257,0.02499],"object_pos_start":[0.53326,-0.08446,0.03127],"object_to_goal_dist_end":0.07182,"object_to_goal_dist_start":0.07377,"object_z_max":0.03468,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3800.0,"raw_peak_contact_force":88.74515,"tcp_end":[0.49873,0.08969,0.10979],"tcp_start":[0.5077,-0.05521,0.02903],"tcp_to_object_dist_end":0.19376,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.71795,"average_solve_count":156.0,"average_success_count":156.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.speed":0.03811,"push_1.push_depth":0.09897,"retract_1.retract_height":0.17958},"optimized_scores":{"best_composite_score":0.67653,"best_fitness_score":0.88653,"best_task_score":0.94982},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1059.0,"contact_point_centroid":[0.51177,-0.10615,-0.00014],"force_p95":61.79184,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":75.27572,"mean_force":25.60065,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49834,-0.05026,0.02004]},{"body_a":"push_box","body_b":"link7","contact_count":591.0,"contact_point_centroid":[0.52496,-0.06138,0.05251],"force_p95":47.44262,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":64.60039,"mean_force":29.2565,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49872,-0.04102,0.02012]},{"body_a":"attachment","body_b":"push_box","contact_count":735.0,"contact_point_centroid":[0.51358,-0.06315,0.04677],"force_p95":48.44747,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":56.35817,"mean_force":23.73612,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49824,-0.05195,0.01999]},{"body_a":"world","body_b":"push_box","contact_count":3965.0,"contact_point_centroid":[0.49965,-0.15664,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.68395,"mean_force":0.25065,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49356,-0.04085,0.05298]},{"body_a":"push_box","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.52526,-0.14138,0.05109],"force_p95":8.47535,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.46787,"mean_force":3.62323,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49625,-0.1187,0.02011]},{"body_a":"attachment","body_b":"push_box","contact_count":155.0,"contact_point_centroid":[0.50737,0.00196,0.03669],"force_p95":7.25954,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.38855,"mean_force":3.1073,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49973,0.01382,0.02132]},{"body_a":"world","body_b":"push_box","contact_count":3047.0,"contact_point_centroid":[0.50492,-0.02076,-1e-05],"force_p95":1.76698,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.39551,"mean_force":0.40954,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49816,0.03694,0.02522]},{"body_a":"attachment","body_b":"push_box","contact_count":7.0,"contact_point_centroid":[0.51207,-0.13042,0.05156],"force_p95":2.56517,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.65987,"mean_force":1.05953,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49612,-0.11865,0.02009]},{"body_a":"world","body_b":"push_box","contact_count":3580.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4992,0.04658,0.17199]}],"total_contact_groups":9},"final_pose_error":0.1324,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49961,-0.15658,0.02499],"final_tcp_position":[0.49469,0.03281,0.08862],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":75.27572,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":895.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3580.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.50029,0.06252,0.03384],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08192,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":850.0,"n_steps_budget":960.0,"object_pos_end":[0.50686,-0.02771,0.02498],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.12249,"object_to_goal_dist_start":0.13127,"object_z_max":0.02515,"peak_contact_force":0.00036,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3202.0,"raw_peak_contact_force":9.38855,"tcp_end":[0.50011,0.00908,0.02058],"tcp_start":[0.50029,0.06252,0.03384],"tcp_to_object_dist_end":0.03766,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":779.0,"n_steps_budget":870.0,"object_pos_end":[0.5012,-0.15547,0.0261],"object_pos_start":[0.50686,-0.02771,0.02498],"object_to_goal_dist_end":0.0057,"object_to_goal_dist_start":0.12249,"object_z_max":0.0282,"peak_contact_force":14.3407,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2385.0,"raw_peak_contact_force":75.27572,"tcp_end":[0.49632,-0.11862,0.02014],"tcp_start":[0.50011,0.00908,0.02058],"tcp_to_object_dist_end":0.03765,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49961,-0.15658,0.02499],"object_pos_start":[0.5012,-0.15547,0.0261],"object_to_goal_dist_end":0.00659,"object_to_goal_dist_start":0.0057,"object_z_max":0.0261,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3976.0,"raw_peak_contact_force":10.68395,"tcp_end":[0.49469,0.03281,0.08862],"tcp_start":[0.49632,-0.11862,0.02014],"tcp_to_object_dist_end":0.19985,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.76471,"average_solve_count":153.0,"average_success_count":153.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.speed":0.04578,"push_1.push_depth":0.09954,"retract_1.retract_height":0.16559},"optimized_scores":{"best_composite_score":0.38,"best_fitness_score":0.59,"best_task_score":0.68173},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1296.0,"contact_point_centroid":[0.52329,-0.04114,-0.00015],"force_p95":60.5086,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":81.62901,"mean_force":34.73846,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50478,0.01294,0.02167]},{"body_a":"push_box","body_b":"link7","contact_count":768.0,"contact_point_centroid":[0.53154,-0.0057,0.05405],"force_p95":56.87841,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":66.04584,"mean_force":42.1718,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50466,0.01299,0.02155]},{"body_a":"attachment","body_b":"push_box","contact_count":776.0,"contact_point_centroid":[0.52206,0.00335,0.04933],"force_p95":59.06481,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":61.89667,"mean_force":38.49954,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50472,0.01364,0.02154]},{"body_a":"world","body_b":"push_box","contact_count":3899.0,"contact_point_centroid":[0.50208,-0.08737,-2e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.10918,"mean_force":0.26218,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49545,0.02214,0.064]},{"body_a":"push_box","body_b":"link7","contact_count":6.0,"contact_point_centroid":[0.52492,-0.07765,0.05417],"force_p95":22.5633,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.65225,"mean_force":14.65141,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49859,-0.05103,0.022]},{"body_a":"attachment","body_b":"push_box","contact_count":26.0,"contact_point_centroid":[0.51712,-0.05998,0.05336],"force_p95":13.01396,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.13466,"mean_force":3.26656,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49767,-0.04921,0.02232]},{"body_a":"attachment","body_b":"push_box","contact_count":120.0,"contact_point_centroid":[0.51656,0.06849,0.03614],"force_p95":7.48044,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.46167,"mean_force":2.9432,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50996,0.08033,0.02166]},{"body_a":"world","body_b":"push_box","contact_count":2352.0,"contact_point_centroid":[0.5152,0.04612,-1e-05],"force_p95":1.65642,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.77995,"mean_force":0.40194,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50825,0.10195,0.02677]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50358,0.07681,0.17794]}],"total_contact_groups":9},"final_pose_error":0.07401,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50194,-0.08694,0.02499],"final_tcp_position":[0.49611,0.08983,0.10709],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":81.62901,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.51015,0.12542,0.03668],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07878,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":660.0,"n_steps_budget":750.0,"object_pos_end":[0.51706,0.03872,0.02494],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.18949,"object_to_goal_dist_start":0.19823,"object_z_max":0.02511,"peak_contact_force":1.02954,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2472.0,"raw_peak_contact_force":12.46167,"tcp_end":[0.51039,0.07559,0.02061],"tcp_start":[0.51015,0.12542,0.03668],"tcp_to_object_dist_end":0.03772,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":778.0,"n_steps_budget":870.0,"object_pos_end":[0.50288,-0.08957,0.02882],"object_pos_start":[0.51706,0.03872,0.02494],"object_to_goal_dist_end":0.06062,"object_to_goal_dist_start":0.18949,"object_z_max":0.02922,"peak_contact_force":32.48978,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2840.0,"raw_peak_contact_force":81.62901,"tcp_end":[0.49876,-0.0509,0.02206],"tcp_start":[0.51039,0.07559,0.02061],"tcp_to_object_dist_end":0.03947,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50194,-0.08694,0.02499],"object_pos_start":[0.50288,-0.08957,0.02882],"object_to_goal_dist_end":0.06309,"object_to_goal_dist_start":0.06062,"object_z_max":0.02882,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3931.0,"raw_peak_contact_force":27.10918,"tcp_end":[0.49611,0.08983,0.10709],"tcp_start":[0.49876,-0.0509,0.02206],"tcp_to_object_dist_end":0.19499,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```