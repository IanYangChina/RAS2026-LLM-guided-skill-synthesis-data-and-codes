## Search State

- **Seed**: 0
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | pose_tolerance | 4 | 0.6210 | 0.92 | ✅ accepted |
| 11 | insert → approach → push → retract → lift → insert | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | linear_cartesian | impedance_motion | impedance_control | force_threshold_switch | impedance_control | position_control | position_control | admittance_control | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 5 | 0.2391 | 0.83 | ✅ accepted |
| 10 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | -0.3390 | 0.00 | ❌ rejected |
| 9 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.0555 | 0.00 | ❌ rejected |
| 8 | insert → approach → push → retract → lift → insert | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | linear_cartesian | impedance_motion | impedance_control | force_threshold_switch | impedance_control | position_control | position_control | admittance_control | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 5 | 0.2405 | 0.81 | ✅ accepted |

**Proposal policy**: task_score is near-perfect (0.92). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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
- Frozen realised-scene SHA-256: `79fe20ee7316d80bc617c84166fccacf882b4f96b2faf4b155be83e4f318b183`
- Frozen object start: [0.5, -0.15, 0.025]
- Frozen task target: [0.5, 0.0, 0.3]
- Goal object position: (0.5, 0.0, 0.3)
- Object initial pose: (0.5, -0.15, 0.025)
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.8
- Force limit: 25.0 N
- Robot initial TCP position: (0.5164354024785746, -0.027625594348335558, 0.025)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **object displacement ratio toward goal_object_position**

## Scene Entities

robot:
  model: panda_pusher
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5164354024785746, -0.027625594348335558, 0.025]
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
  frozen_object_start: [0.5164, -0.0276, 0.025]
  frozen_task_target: [0.5, 0.0, 0.3]
  frozen_object_starts: {'push_box': [0.5, -0.15, 0.025]}
  frozen_targets: {'task_goal': [0.5, 0.0, 0.3]}
  push_direction: [-0.0164, -0.1224, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: 79fe20ee7316d80bc617c84166fccacf882b4f96b2faf4b155be83e4f318b183

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.919, which indicates the subtask decomposition is already effective.
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
| `object` | offset from object initial position (0.5, -0.15, 0.025) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5, 0.0, 0.3) | final destination targets |
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

## Current Skill (Q=0.621) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
subtasks:
- id: reach_object
  anchor: object
  weight: 0.3
- id: push_to_goal
  target_entity: object
  metric: goal_progress
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
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.08
      axis: task_goal_direction
      mode: replace_offset_projection
      sign: negative
    tolerance: 0.02
    orientation:
      mode: none
  parameters:
    approach_distance:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_object
- id: push_1
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.15
      axis: task_goal_direction
      mode: replace_offset_projection
      sign: positive
    tolerance: 0.02
    orientation:
      mode: none
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: push_to_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.08, mode=replace_offset_projection, sign=negative}, tolerance=0.02
  - orientation: mode=none
  - parameter_bindings:
    - approach_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.15, mode=replace_offset_projection, sign=positive}, tolerance=0.02
  - orientation: mode=none
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.621
- **task_score** (E): 0.919
- **fitness_score**: 0.821  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.200

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2659 |
| push_1 | 1.00 | 1.00 | 0.1568 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.492, 0.046, 0.044) | (0.496, 0.001, 0.025)→(0.496, 0.000, 0.025) | 0.152→0.152 | 1.00 / 3.333 | 0.164 | 82.181 |
| push_1 | push | 1.00 / step_budget | (0.492, 0.046, 0.044)→(0.497, -0.108, 0.022) | (0.496, 0.000, 0.025)→(0.505, -0.150, 0.026) | 0.152→0.011 | 1.00 / 1.667 | 1.027 | 71.902 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.963
- lateral_force_integral: None
- approach_alignment: 0.662
- goal_progress: 0.962
- terminal_score: 0.962
- phase_score: 0.769
- phase_breakdown.push_to_goal_score: 0.962
- phase_breakdown.reach_object_score: 0.318

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.846
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.962
- **Median Q (composite search score)**: 0.616
- **K-run variance**: 0.0004
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.455


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `1efc9b29f7d131941a1bd842274a029ca5b2a2ff6a8656033ab118e32e2fae7d`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `6150c547b3cd2920ed4582689733d59ef61d18dc295ccd2a0d2317d1cf4e7764`; realized-scene SHA-256: `79fe20ee7316d80bc617c84166fccacf882b4f96b2faf4b155be83e4f318b183`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5,-0.15,0.025]},{"name":"goal","value":[0.51644,-0.02763,0.025]}],"axes":[{"name":"push_direction","value":[-0.01644,-0.12237,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.51644,-0.02763,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.9763,"average_solve_count":211.0,"average_success_count":211.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_distance":0.03467,"approach_1.approach_speed":0.0339,"push_1.push_distance":0.09702,"push_1.push_speed":0.03017},"optimized_scores":{"best_composite_score":0.60051,"best_fitness_score":0.80051,"best_task_score":0.87971},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":22.0,"contact_point_centroid":[0.5214,-0.00308,0.04845],"force_p95":238.1713,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":246.05245,"mean_force":147.86541,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51645,0.00652,0.04974]},{"body_a":"world","body_b":"push_box","contact_count":2114.0,"contact_point_centroid":[0.51659,-0.02749,-1e-05],"force_p95":0.24533,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":176.82936,"mean_force":1.79463,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50696,0.00296,0.17377]},{"body_a":"attachment","body_b":"push_box","contact_count":205.0,"contact_point_centroid":[0.51446,-0.06188,0.04388],"force_p95":58.78179,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":77.57441,"mean_force":9.26774,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50826,-0.05025,0.03148]},{"body_a":"world","body_b":"push_box","contact_count":369.0,"contact_point_centroid":[0.51457,-0.09159,-0.00021],"force_p95":30.03539,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":50.42101,"mean_force":6.28333,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50916,-0.04321,0.03271]},{"body_a":"push_box","body_b":"link7","contact_count":12.0,"contact_point_centroid":[0.53893,-0.11563,0.05169],"force_p95":30.47402,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":31.59907,"mean_force":22.18937,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50263,-0.09872,0.02393]}],"total_contact_groups":5},"final_pose_error":0.01965,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51451,-0.14804,0.02751],"final_tcp_position":[0.50193,-0.10609,0.02292],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51644,-0.02763,0.025]},"peak_contact_force":246.05245,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":534.0,"n_steps_budget":1000.0,"object_pos_end":[0.51648,-0.02945,0.02483],"object_pos_start":[0.51644,-0.02763,0.025],"object_to_goal_dist_end":0.12167,"object_to_goal_dist_start":0.12347,"object_z_max":0.025,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2136.0,"raw_peak_contact_force":246.05245,"subtask_id":"reach_object","tcp_end":[0.51826,0.0078,0.04477],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.04229,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":311.0,"n_steps_budget":1000.0,"object_pos_end":[0.51451,-0.14804,0.02751],"object_pos_start":[0.51648,-0.02945,0.02483],"object_to_goal_dist_end":0.01485,"object_to_goal_dist_start":0.12167,"object_z_max":0.02849,"peak_contact_force":2.34207,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":586.0,"raw_peak_contact_force":77.57441,"subtask_id":"push_to_goal","tcp_end":[0.50193,-0.10609,0.02292],"tcp_start":[0.51826,0.0078,0.04477],"tcp_to_object_dist_end":0.04403,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `88c86884172a74f1f27b08fda534b767baf4d8d60d3fd4d782dec9555f4aae87`; realized-scene SHA-256: `258b33ff0697721ed1ba4810cf28d81707440dffd73b12c632f307c6591915c0`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5,-0.15,0.025]},{"name":"goal","value":[0.50142,0.05406,0.025]}],"axes":[{"name":"push_direction","value":[-0.00142,-0.20406,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.50142,0.05406,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.71127,"average_solve_count":142.0,"average_success_count":142.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_distance":0.06472,"approach_1.approach_speed":0.0863,"push_1.push_distance":0.16859,"push_1.push_speed":0.06407},"optimized_scores":{"best_composite_score":0.64605,"best_fitness_score":0.84605,"best_task_score":0.96187},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":285.0,"contact_point_centroid":[0.50423,-0.01244,0.04254],"force_p95":55.03145,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":63.83689,"mean_force":11.27307,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49571,-0.00106,0.0289]},{"body_a":"world","body_b":"push_box","contact_count":692.0,"contact_point_centroid":[0.50737,-0.02736,-0.00018],"force_p95":31.00517,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":57.96088,"mean_force":5.98239,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49576,0.02435,0.03126]},{"body_a":"push_box","body_b":"link7","contact_count":45.0,"contact_point_centroid":[0.5342,-0.02861,0.05452],"force_p95":49.3739,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":51.00522,"mean_force":14.80569,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49609,-0.01345,0.02817]},{"body_a":"world","body_b":"push_box","contact_count":2236.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49843,0.05334,0.17167]}],"total_contact_groups":4},"final_pose_error":0.01985,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49852,-0.14238,0.02552],"final_tcp_position":[0.49626,-0.09541,0.02142],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50142,0.05406,0.025]},"peak_contact_force":63.83689,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":559.0,"n_steps_budget":1000.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.025],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2236.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.4982,0.10872,0.04161],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.05722,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":529.0,"n_steps_budget":1000.0,"object_pos_end":[0.49852,-0.14238,0.02552],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.00778,"object_to_goal_dist_start":0.20406,"object_z_max":0.03056,"peak_contact_force":0.73849,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1022.0,"raw_peak_contact_force":63.83689,"subtask_id":"push_to_goal","tcp_end":[0.49626,-0.09541,0.02142],"tcp_start":[0.4982,0.10872,0.04161],"tcp_to_object_dist_end":0.0472,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `a3cdbd735282928b0caf1de02aaaeed7f0a3d0a10908989412c558d20f3517fa`; realized-scene SHA-256: `8c36a5f9300ba3a57ccc09620ec8ba0a5276276ed83fb4303679e150911bfa14`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5,-0.15,0.025]},{"name":"goal","value":[0.47139,-0.02418,0.025]}],"axes":[{"name":"push_direction","value":[0.02861,-0.12582,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.47139,-0.02418,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.07527,"average_solve_count":186.0,"average_success_count":186.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_distance":0.04835,"approach_1.approach_speed":0.08599,"push_1.push_distance":0.12023,"push_1.push_speed":0.02161},"optimized_scores":{"best_composite_score":0.61647,"best_fitness_score":0.81647,"best_task_score":0.91517},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":249.0,"contact_point_centroid":[0.48787,-0.06892,0.04978],"force_p95":60.26416,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":74.29354,"mean_force":20.0901,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47587,-0.05725,0.03092]},{"body_a":"world","body_b":"push_box","contact_count":604.0,"contact_point_centroid":[0.48944,-0.09328,-0.00011],"force_p95":35.99368,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":56.96378,"mean_force":10.02174,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47291,-0.04366,0.03291]},{"body_a":"push_box","body_b":"link7","contact_count":76.0,"contact_point_centroid":[0.52061,-0.10793,0.05322],"force_p95":30.27873,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.12852,"mean_force":11.49614,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48358,-0.08906,0.02703]},{"body_a":"world","body_b":"push_box","contact_count":2008.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4801,0.01016,0.17347]}],"total_contact_groups":4},"final_pose_error":0.01992,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50083,-0.16087,0.02595],"final_tcp_position":[0.49189,-0.12259,0.02294],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":74.29354,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":502.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2008.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.46068,0.02078,0.04444],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.05015,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":435.0,"n_steps_budget":1000.0,"object_pos_end":[0.50083,-0.16087,0.02595],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.01095,"object_to_goal_dist_start":0.12903,"object_z_max":0.02973,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":929.0,"raw_peak_contact_force":74.29354,"subtask_id":"push_to_goal","tcp_end":[0.49189,-0.12259,0.02294],"tcp_start":[0.46068,0.02078,0.04444],"tcp_to_object_dist_end":0.03943,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```