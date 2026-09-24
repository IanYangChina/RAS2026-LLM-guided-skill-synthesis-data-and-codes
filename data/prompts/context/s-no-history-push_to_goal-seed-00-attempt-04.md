## Search State

- **Seed**: 0
- **Iteration**: 5 / 15

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
- Frozen object start: [0.5164354024785746, -0.027625594348335558, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.5164354024785746, -0.027625594348335558, 0.025)
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
  frozen_object_start: [0.5164, -0.0276, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.5164354024785746, -0.027625594348335558, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [-0.0164, -0.1224, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: 79fe20ee7316d80bc617c84166fccacf882b4f96b2faf4b155be83e4f318b183

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.815, which indicates the subtask decomposition is already effective.
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
| `object` | offset from object initial position (0.5164354024785746, -0.027625594348335558, 0.025) | approach/contact targets near object start |
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

## Current Skill (Q=0.236) — your mutation base

```yaml
skill: push_to_goal
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

- **Composite score**: 0.236
- **task_score** (E): 0.815
- **fitness_score**: 0.606  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.370

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| insert_1 | 0.00 | 1.00 | 0.1849 |
| approach_1 | 1.00 | 1.00 | 0.1925 |
| push_1 | 0.67 | 1.00 | 0.1652 |
| retract_1 | 0.00 | 1.00 | 0.1223 |
| lift_1 | 0.00 | 1.00 | 0.1448 |
| insert_2 | 0.00 | 1.00 | 0.1668 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| insert_1 | insert | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.497, -0.086, 0.137) | (0.496, 0.001, 0.025)→(0.496, 0.001, 0.025) | 0.152→0.152 | 1.00 / 4.000 | 0.245 | 0.245 |
| approach_1 | approach | 1.00 / step_budget | (0.497, -0.086, 0.137)→(0.494, 0.071, 0.030) | (0.496, 0.001, 0.025)→(0.497, 0.010, 0.028) | 0.152→0.161 | 1.00 / 4.000 | 13.603 | 60.704 |
| push_1 | push | 0.67 / step_budget | (0.494, 0.071, 0.030)→(0.496, -0.093, 0.023) | (0.497, 0.010, 0.028)→(0.494, -0.131, 0.029) | 0.161→0.031 | 1.00 / 3.333 | 24.802 | 53.997 |
| retract_1 | retract | 0.00 / step_budget | (0.496, -0.093, 0.023)→(0.494, 0.002, 0.098) | (0.494, -0.131, 0.029)→(0.494, -0.126, 0.025) | 0.031→0.034 | 1.00 / 4.000 | 0.245 | 22.558 |
| lift_1 | lift | 0.00 / step_budget | (0.494, 0.002, 0.098)→(0.427, -0.065, 0.207) | (0.494, -0.126, 0.025)→(0.494, -0.126, 0.025) | 0.034→0.034 | 1.00 / 4.000 | 0.245 | 0.245 |
| insert_2 | insert | 0.00 / step_budget | (0.427, -0.065, 0.207)→(0.479, -0.129, 0.063) | (0.494, -0.126, 0.025)→(0.494, -0.126, 0.025) | 0.034→0.034 | 1.00 / 4.000 | 0.245 | 0.245 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.744
- goal_progress: 0.917
- terminal_score: 0.917
- phase_score: 0.632
- phase_breakdown.contact_score: 0.000
- phase_breakdown.approach_score: 0.820
- phase_breakdown.push_score: 0.937

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.746
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.951
- **Median Q (composite search score)**: 0.329
- **K-run variance**: 0.0273
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.458


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
{"anchors":[{"name":"object","value":[0.51644,-0.02763,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.01644,-0.12237,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.51644,-0.02763,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.53585,"average_solve_count":265.0,"average_success_count":265.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift_1.speed":0.04131,"push_1.push_distance":0.11075,"push_1.push_speed":0.08168,"retract_1.retract_height":0.14614,"retract_1.speed":0.04076},"optimized_scores":{"best_composite_score":0.37619,"best_fitness_score":0.74619,"best_task_score":0.91708},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1830.0,"contact_point_centroid":[0.51336,-0.08067,-6e-05],"force_p95":30.00774,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":55.71597,"mean_force":6.78937,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50333,-0.02693,0.02162]},{"body_a":"attachment","body_b":"push_box","contact_count":698.0,"contact_point_centroid":[0.5131,-0.07734,0.04466],"force_p95":34.6757,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":46.88843,"mean_force":11.65697,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50079,-0.06563,0.02105]},{"body_a":"push_box","body_b":"link7","contact_count":463.0,"contact_point_centroid":[0.53056,-0.08731,0.05192],"force_p95":26.86667,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":38.38077,"mean_force":12.73261,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50092,-0.06813,0.02126]},{"body_a":"push_box","body_b":"link7","contact_count":13.0,"contact_point_centroid":[0.52571,-0.15033,0.0539],"force_p95":34.46008,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":35.93893,"mean_force":17.48222,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49852,-0.12498,0.02195]},{"body_a":"attachment","body_b":"push_box","contact_count":39.0,"contact_point_centroid":[0.51688,-0.13365,0.05482],"force_p95":25.09886,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":26.11398,"mean_force":4.9467,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49747,-0.12272,0.02289]},{"body_a":"world","body_b":"push_box","contact_count":3869.0,"contact_point_centroid":[0.50242,-0.16063,-1e-05],"force_p95":0.2454,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.12708,"mean_force":0.27647,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49526,-0.07772,0.05886]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.51644,-0.02763,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49729,-0.0436,0.21555]},{"body_a":"world","body_b":"push_box","contact_count":2704.0,"contact_point_centroid":[0.51644,-0.02763,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50252,-0.02032,0.07916]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.50223,-0.15999,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4599,-0.0572,0.1463]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.50223,-0.15999,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":5.0,"phase_name":"insert_2","phase_type":"insert","tcp_position_centroid":[0.45335,-0.10953,0.12881]}],"total_contact_groups":10},"final_pose_error":0.0378,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50223,-0.15999,0.02499],"final_tcp_position":[0.48204,-0.13621,0.05526],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51644,-0.02763,0.025]},"peak_contact_force":55.71597,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51644,-0.02763,0.02499],"object_pos_start":[0.51644,-0.02763,0.025],"object_to_goal_dist_end":0.12347,"object_to_goal_dist_start":0.12347,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.4966,-0.08596,0.13695],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.12779,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":676.0,"n_steps_budget":1000.0,"object_pos_end":[0.51644,-0.02763,0.02499],"object_pos_start":[0.51644,-0.02763,0.02499],"object_to_goal_dist_end":0.12347,"object_to_goal_dist_start":0.12347,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2704.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.51104,0.04412,0.02621],"tcp_start":[0.4966,-0.08596,0.13695],"tcp_to_object_dist_end":0.07196,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50425,-0.16276,0.0283],"object_pos_start":[0.51644,-0.02763,0.02499],"object_to_goal_dist_end":0.01384,"object_to_goal_dist_start":0.12347,"object_z_max":0.02837,"peak_contact_force":46.47935,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2991.0,"raw_peak_contact_force":55.71597,"tcp_end":[0.49892,-0.12511,0.02191],"tcp_start":[0.51104,0.04412,0.02621],"tcp_to_object_dist_end":0.03855,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50223,-0.15999,0.02499],"object_pos_start":[0.50425,-0.16276,0.0283],"object_to_goal_dist_end":0.01024,"object_to_goal_dist_start":0.01384,"object_z_max":0.02831,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3921.0,"raw_peak_contact_force":35.93893,"tcp_end":[0.49559,-0.03065,0.09255],"tcp_start":[0.49892,-0.12511,0.02191],"tcp_to_object_dist_end":0.14607,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50223,-0.15999,0.02499],"object_pos_start":[0.50223,-0.15999,0.02499],"object_to_goal_dist_end":0.01024,"object_to_goal_dist_start":0.01024,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.4277,-0.08379,0.20408],"tcp_start":[0.49559,-0.03065,0.09255],"tcp_to_object_dist_end":0.20842,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50223,-0.15999,0.02499],"object_pos_start":[0.50223,-0.15999,0.02499],"object_to_goal_dist_end":0.01024,"object_to_goal_dist_start":0.01024,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"insert_2","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.48204,-0.13621,0.05526],"tcp_start":[0.4277,-0.08379,0.20408],"tcp_to_object_dist_end":0.04347,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `88c86884172a74f1f27b08fda534b767baf4d8d60d3fd4d782dec9555f4aae87`; realized-scene SHA-256: `258b33ff0697721ed1ba4810cf28d81707440dffd73b12c632f307c6591915c0`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50142,0.05406,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.00142,-0.20406,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.50142,0.05406,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.52158,"average_solve_count":278.0,"average_success_count":278.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift_1.speed":0.04858,"push_1.push_distance":0.16642,"push_1.push_speed":0.09961,"retract_1.retract_height":0.11297,"retract_1.speed":0.02042},"optimized_scores":{"best_composite_score":0.00432,"best_fitness_score":0.37432,"best_task_score":0.57757},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":286.0,"contact_point_centroid":[0.51033,0.08541,0.04646],"force_p95":154.66051,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":181.6215,"mean_force":112.54583,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50235,0.09183,0.04903]},{"body_a":"world","body_b":"push_box","contact_count":3422.0,"contact_point_centroid":[0.50174,0.05825,-9e-05],"force_p95":81.58625,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":164.76933,"mean_force":9.73416,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49612,0.00715,0.08615]},{"body_a":"attachment","body_b":"push_box","contact_count":994.0,"contact_point_centroid":[0.50385,0.03324,0.03071],"force_p95":76.13189,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":81.22073,"mean_force":55.83146,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50187,0.04449,0.03129]},{"body_a":"world","body_b":"push_box","contact_count":1925.0,"contact_point_centroid":[0.49634,-0.00255,-0.00017],"force_p95":60.8895,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":76.72962,"mean_force":41.66019,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5019,0.04685,0.03144]},{"body_a":"push_box","body_b":"link7","contact_count":1000.0,"contact_point_centroid":[0.52172,0.00997,0.06792],"force_p95":33.48592,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":53.8641,"mean_force":31.17874,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50186,0.04495,0.0313]},{"body_a":"push_box","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.52838,0.09012,0.06853],"force_p95":39.95326,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.31824,"mean_force":36.49581,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50206,0.12188,0.0353]},{"body_a":"push_box","body_b":"link7","contact_count":20.0,"contact_point_centroid":[0.50851,-0.07622,0.06701],"force_p95":27.84187,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":30.82368,"mean_force":7.98242,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49907,-0.04018,0.02529]},{"body_a":"world","body_b":"push_box","contact_count":3711.0,"contact_point_centroid":[0.48397,-0.0666,-1e-05],"force_p95":0.3698,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":25.9121,"mean_force":0.30586,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49588,-0.00034,0.06556]},{"body_a":"attachment","body_b":"push_box","contact_count":67.0,"contact_point_centroid":[0.49538,-0.04641,0.03071],"force_p95":2.34055,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.99193,"mean_force":0.75988,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49703,-0.0347,0.0299]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49729,-0.0436,0.21555]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.48448,-0.06521,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46153,-0.00248,0.14928]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.48448,-0.06521,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":5.0,"phase_name":"insert_2","phase_type":"insert","tcp_position_centroid":[0.45305,-0.08219,0.13351]}],"total_contact_groups":12},"final_pose_error":0.05309,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.48448,-0.06521,0.02499],"final_tcp_position":[0.47876,-0.12242,0.06509],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50142,0.05406,0.025]},"peak_contact_force":181.6215,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.025],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.4966,-0.08596,0.13695],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.17934,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50341,0.08175,0.03419],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.23196,"object_to_goal_dist_start":0.20406,"object_z_max":0.03486,"peak_contact_force":40.31824,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3711.0,"raw_peak_contact_force":181.6215,"tcp_end":[0.50193,0.12221,0.03486],"tcp_start":[0.4966,-0.08596,0.13695],"tcp_to_object_dist_end":0.04049,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48235,-0.07956,0.03342],"object_pos_start":[0.50341,0.08175,0.03419],"object_to_goal_dist_end":0.0731,"object_to_goal_dist_start":0.23196,"object_z_max":0.03421,"peak_contact_force":26.29291,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3919.0,"raw_peak_contact_force":81.22073,"tcp_end":[0.49963,-0.0403,0.025],"tcp_start":[0.50193,0.12221,0.03486],"tcp_to_object_dist_end":0.04371,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48448,-0.06521,0.02499],"object_pos_start":[0.48235,-0.07956,0.03342],"object_to_goal_dist_end":0.0862,"object_to_goal_dist_start":0.0731,"object_z_max":0.03373,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3798.0,"raw_peak_contact_force":30.82368,"tcp_end":[0.49615,0.03837,0.09898],"tcp_start":[0.49963,-0.0403,0.025],"tcp_to_object_dist_end":0.12782,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48448,-0.06521,0.02499],"object_pos_start":[0.48448,-0.06521,0.02499],"object_to_goal_dist_end":0.0862,"object_to_goal_dist_start":0.0862,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.43028,-0.04299,0.20373],"tcp_start":[0.49615,0.03837,0.09898],"tcp_to_object_dist_end":0.18809,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48448,-0.06521,0.02499],"object_pos_start":[0.48448,-0.06521,0.02499],"object_to_goal_dist_end":0.0862,"object_to_goal_dist_start":0.0862,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"insert_2","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.47876,-0.12242,0.06509],"tcp_start":[0.43028,-0.04299,0.20373],"tcp_to_object_dist_end":0.0701,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `a3cdbd735282928b0caf1de02aaaeed7f0a3d0a10908989412c558d20f3517fa`; realized-scene SHA-256: `8c36a5f9300ba3a57ccc09620ec8ba0a5276276ed83fb4303679e150911bfa14`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47139,-0.02418,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.02861,-0.12582,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.47139,-0.02418,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.70385,"average_solve_count":260.0,"average_success_count":260.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift_1.speed":0.0228,"push_1.push_distance":0.13955,"push_1.push_speed":0.07184,"retract_1.retract_height":0.13656,"retract_1.speed":0.08088},"optimized_scores":{"best_composite_score":0.3289,"best_fitness_score":0.6989,"best_task_score":0.95053},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":717.0,"contact_point_centroid":[0.48562,-0.06426,0.03335],"force_p95":16.58199,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":25.05527,"mean_force":4.39657,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47961,-0.05224,0.02176]},{"body_a":"world","body_b":"push_box","contact_count":2043.0,"contact_point_centroid":[0.47877,-0.07112,-4e-05],"force_p95":7.36744,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.90143,"mean_force":1.88024,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4755,-0.02251,0.02254]},{"body_a":"push_box","body_b":"link7","contact_count":49.0,"contact_point_centroid":[0.51533,-0.0949,0.05021],"force_p95":11.8379,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.29932,"mean_force":2.6303,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48386,-0.08076,0.02132]},{"body_a":"world","body_b":"push_box","contact_count":3989.0,"contact_point_centroid":[0.49446,-0.1531,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.91158,"mean_force":0.24611,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48751,-0.06009,0.06425]},{"body_a":"attachment","body_b":"push_box","contact_count":2.0,"contact_point_centroid":[0.48867,-0.12708,0.02072],"force_p95":0.87976,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.8881,"mean_force":0.80467,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48891,-0.11511,0.0207]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49729,-0.0436,0.21555]},{"body_a":"world","body_b":"push_box","contact_count":2520.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48142,-0.0196,0.08025]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.49443,-0.15311,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4549,-0.03555,0.15665]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.49443,-0.15311,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":5.0,"phase_name":"insert_2","phase_type":"insert","tcp_position_centroid":[0.44855,-0.09879,0.13956]}],"total_contact_groups":9},"final_pose_error":0.05269,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49443,-0.15311,0.02499],"final_tcp_position":[0.47697,-0.12904,0.0675],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":25.05527,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.4966,-0.08596,0.13695],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.13033,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":630.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2520.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.46892,0.04665,0.02746],"tcp_start":[0.4966,-0.08596,0.13695],"tcp_to_object_dist_end":0.07092,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49449,-0.15211,0.02501],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.0059,"object_to_goal_dist_start":0.12903,"object_z_max":0.02542,"peak_contact_force":1.63516,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2809.0,"raw_peak_contact_force":25.05527,"tcp_end":[0.48892,-0.11506,0.02071],"tcp_start":[0.46892,0.04665,0.02746],"tcp_to_object_dist_end":0.03772,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49443,-0.15311,0.02499],"object_pos_start":[0.49449,-0.15211,0.02501],"object_to_goal_dist_end":0.00638,"object_to_goal_dist_start":0.0059,"object_z_max":0.02502,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3991.0,"raw_peak_contact_force":0.91158,"tcp_end":[0.49009,-0.00145,0.1039],"tcp_start":[0.48892,-0.11506,0.02071],"tcp_to_object_dist_end":0.17102,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49443,-0.15311,0.02499],"object_pos_start":[0.49443,-0.15311,0.02499],"object_to_goal_dist_end":0.00638,"object_to_goal_dist_start":0.00638,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.42307,-0.06948,0.21329],"tcp_start":[0.49009,-0.00145,0.1039],"tcp_to_object_dist_end":0.21805,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49443,-0.15311,0.02499],"object_pos_start":[0.49443,-0.15311,0.02499],"object_to_goal_dist_end":0.00638,"object_to_goal_dist_start":0.00638,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"insert_2","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.47697,-0.12904,0.0675],"tcp_start":[0.42307,-0.06948,0.21329],"tcp_to_object_dist_end":0.05188,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```