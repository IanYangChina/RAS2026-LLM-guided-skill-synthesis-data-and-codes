## Search State

- **Seed**: 7
- **Iteration**: 11 / 15

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
- Frozen realised-scene SHA-256: `c8d09cd43835becf8e5eb4413394fad8627e4bf404e9e7726e9f380b60e09752`
- Frozen object start: [0.51501145599256, 0.047665656116349056, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.51501145599256, 0.047665656116349056, 0.025)
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
  frozen_object_start: [0.515, 0.0477, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.51501145599256, 0.047665656116349056, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [-0.015, -0.1977, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: c8d09cd43835becf8e5eb4413394fad8627e4bf404e9e7726e9f380b60e09752

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.822, which indicates the subtask decomposition is already effective.
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
| `object` | offset from object initial position (0.51501145599256, 0.047665656116349056, 0.025) | approach/contact targets near object start |
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

## Current Skill (Q=0.560) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
subtasks:
- id: reach_contact
  anchor: object
  offset:
  - 0.0
  - 0.03
  - 0.0
  weight: 0.3
- id: reach_goal
  target_entity: object
  weight: 0.7
phases:
- id: approach_hover
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.03
    - 0.08
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
- id: descend_to_contact
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.03
    - 0.0
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_contact
- id: push_to_goal
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.01
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    push_speed:
      type: scalar
      range:
      - 0.02
      - 0.06
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_hover** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.03, 0.08], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_contact** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.03, 0.0], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **push_to_goal** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.01], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.560
- **task_score** (E): 0.764
- **fitness_score**: 0.740  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.180

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_hover | 1.00 | 1.00 | 0.2002 |
| descend_to_contact | 1.00 | 1.00 | 0.0820 |
| push_to_goal | 1.00 | 0.67 | 0.1926 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_hover | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.509, 0.053, 0.112) | (0.513, 0.027, 0.025)→(0.513, 0.027, 0.025) | 0.180→0.180 | 1.00 / 4.000 | 0.245 | 0.245 |
| descend_to_contact | descend | 1.00 / step_budget | (0.509, 0.053, 0.112)→(0.518, 0.059, 0.031) | (0.513, 0.027, 0.025)→(0.514, 0.019, 0.025) | 0.180→0.172 | 1.00 / 2.000 | 0.687 | 218.880 |
| push_to_goal | push | 1.00 / step_budget | (0.518, 0.059, 0.031)→(0.498, -0.131, 0.030) | (0.514, 0.019, 0.025)→(0.465, -0.138, 0.025) | 0.172→0.045 | 0.67 / 1.667 | 0.082 | 45.427 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.704
- goal_progress: 0.863
- terminal_score: 0.863
- phase_score: 0.746
- phase_breakdown.reach_contact_score: 0.907
- phase_breakdown.reach_goal_score: 0.677

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.793
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.863
- **Median Q (composite search score)**: 0.550
- **K-run variance**: 0.0016
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.263


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `75e2389a1a667086aa2b9c0de482ff37adf5571150b90a83772692baadf8b52e`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `154c216c563de6b8ee153943e5b668ca6d0c7dfd9253696b060f91a67dca06ec`; realized-scene SHA-256: `c8d09cd43835becf8e5eb4413394fad8627e4bf404e9e7726e9f380b60e09752`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51501,0.04767,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.01501,-0.19767,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.51501,0.04767,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.76398,"average_solve_count":322.0,"average_success_count":322.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_hover.approach_speed":0.03492,"descend_to_contact.descend_speed":0.0208,"push_to_goal.push_speed":0.04043},"optimized_scores":{"best_composite_score":0.55011,"best_fitness_score":0.73011,"best_task_score":0.75886},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":586.0,"contact_point_centroid":[0.53101,0.07279,0.04628],"force_p95":203.86337,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":215.93797,"mean_force":159.08539,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.52186,0.07917,0.04635]},{"body_a":"world","body_b":"push_box","contact_count":2826.0,"contact_point_centroid":[0.51638,0.05656,-0.00035],"force_p95":164.2953,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":192.95432,"mean_force":33.35943,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.51462,0.07607,0.06526]},{"body_a":"attachment","body_b":"push_box","contact_count":301.0,"contact_point_centroid":[0.50578,-0.03049,0.02976],"force_p95":28.55123,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":51.01008,"mean_force":5.24988,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.5093,-0.01928,0.02918]},{"body_a":"world","body_b":"push_box","contact_count":790.0,"contact_point_centroid":[0.48506,-0.05977,-0.00013],"force_p95":10.03398,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.9414,"mean_force":2.46107,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50857,-0.02795,0.02941]},{"body_a":"world","body_b":"push_box","contact_count":2932.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_hover","phase_type":"approach","tcp_position_centroid":[0.50435,0.03564,0.20571]}],"total_contact_groups":5},"final_pose_error":0.01988,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.45344,-0.13919,0.02561],"final_tcp_position":[0.49834,-0.13083,0.03003],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":215.93797,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":733.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_hover","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2932.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.51073,0.07233,0.11223],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.09076,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51484,0.04062,0.0247],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.19119,"object_to_goal_dist_start":0.19823,"object_z_max":0.02772,"peak_contact_force":0.36914,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3412.0,"raw_peak_contact_force":215.93797,"subtask_id":"reach_contact","tcp_end":[0.52244,0.08061,0.03258],"tcp_start":[0.51073,0.07233,0.11223],"tcp_to_object_dist_end":0.04146,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":561.0,"n_steps_budget":1000.0,"object_pos_end":[0.45344,-0.13919,0.02561],"object_pos_start":[0.51484,0.04062,0.0247],"object_to_goal_dist_end":0.0478,"object_to_goal_dist_start":0.19119,"object_z_max":0.02627,"peak_contact_force":0.0,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1091.0,"raw_peak_contact_force":51.01008,"subtask_id":"reach_goal","tcp_end":[0.49834,-0.13083,0.03003],"tcp_start":[0.52244,0.08061,0.03258],"tcp_to_object_dist_end":0.04588,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `4d55d9375783bea830660bf0a13dfc76a97a0d4f5645e7ebcc1ef7143776d0b7`; realized-scene SHA-256: `f3b8ea82cefd9504be10e2d47c49094a836a703404c06bdee3b01a27a59bf7be`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47924,0.05847,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.02076,-0.20847,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.47924,0.05847,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.85959,"average_solve_count":292.0,"average_success_count":292.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_hover.approach_speed":0.04243,"descend_to_contact.descend_speed":0.02585,"push_to_goal.push_speed":0.03365},"optimized_scores":{"best_composite_score":0.51694,"best_fitness_score":0.69694,"best_task_score":0.66896},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":467.0,"contact_point_centroid":[0.49591,0.0835,0.04613],"force_p95":213.30167,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":228.33506,"mean_force":166.32381,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.4865,0.08965,0.04614]},{"body_a":"world","body_b":"push_box","contact_count":2573.0,"contact_point_centroid":[0.48028,0.06644,-0.00032],"force_p95":177.15383,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":217.12228,"mean_force":30.55956,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.47942,0.08615,0.06736]},{"body_a":"attachment","body_b":"push_box","contact_count":250.0,"contact_point_centroid":[0.48493,-0.00104,0.02917],"force_p95":30.44162,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":36.43028,"mean_force":5.70047,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.48775,0.01041,0.02872]},{"body_a":"world","body_b":"push_box","contact_count":1164.0,"contact_point_centroid":[0.46221,-0.06163,-0.00014],"force_p95":9.14185,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.71545,"mean_force":1.58917,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.4907,-0.04226,0.0293]},{"body_a":"world","body_b":"push_box","contact_count":2924.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_hover","phase_type":"approach","tcp_position_centroid":[0.48786,0.04071,0.20576]}],"total_contact_groups":5},"final_pose_error":0.02,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.4459,-0.1066,0.02499],"final_tcp_position":[0.49539,-0.13123,0.02988],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":228.33506,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":731.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_hover","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2924.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.47732,0.08251,0.11257],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.09084,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":885.0,"n_steps_budget":1000.0,"object_pos_end":[0.48264,0.04997,0.02511],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.20073,"object_to_goal_dist_start":0.2095,"object_z_max":0.02625,"peak_contact_force":1.2405,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3040.0,"raw_peak_contact_force":228.33506,"subtask_id":"reach_contact","tcp_end":[0.48644,0.09037,0.03163],"tcp_start":[0.47732,0.08251,0.11257],"tcp_to_object_dist_end":0.04109,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":599.0,"n_steps_budget":1000.0,"object_pos_end":[0.4459,-0.1066,0.02499],"object_pos_start":[0.48264,0.04997,0.02511],"object_to_goal_dist_end":0.06935,"object_to_goal_dist_start":0.20073,"object_z_max":0.02629,"peak_contact_force":0.24524,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1414.0,"raw_peak_contact_force":36.43028,"subtask_id":"reach_goal","tcp_end":[0.49539,-0.13123,0.02988],"tcp_start":[0.48644,0.09037,0.03163],"tcp_to_object_dist_end":0.05549,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `0a9238470f4497c7aa88b149b7cee960f9853513db10bf496723f5ea1d3a6043`; realized-scene SHA-256: `2cf7387f3e8baf02f18930263090d6f78777bdbc147b7fa30c178332e76b547b`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.54443,-0.02558,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.04443,-0.12442,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.54443,-0.02558,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.70861,"average_solve_count":302.0,"average_success_count":302.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_hover.approach_speed":0.0364,"descend_to_contact.descend_speed":0.02235,"push_to_goal.push_speed":0.02975},"optimized_scores":{"best_composite_score":0.61267,"best_fitness_score":0.79267,"best_task_score":0.86302},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":477.0,"contact_point_centroid":[0.55915,-0.0006,0.04662],"force_p95":198.82698,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":212.36701,"mean_force":150.00035,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.54927,0.00557,0.04695]},{"body_a":"world","body_b":"push_box","contact_count":2881.0,"contact_point_centroid":[0.54806,-0.02162,-0.00027],"force_p95":139.21244,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":190.91214,"mean_force":25.20886,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.54237,0.00475,0.06461]},{"body_a":"attachment","body_b":"push_box","contact_count":267.0,"contact_point_centroid":[0.52173,-0.07301,0.03033],"force_p95":37.07281,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":48.84172,"mean_force":7.47339,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.52266,-0.06121,0.02748]},{"body_a":"world","body_b":"push_box","contact_count":509.0,"contact_point_centroid":[0.51903,-0.09667,-0.00015],"force_p95":14.79477,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":24.70665,"mean_force":4.34631,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.52404,-0.05724,0.02759]},{"body_a":"world","body_b":"push_box","contact_count":2776.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_hover","phase_type":"approach","tcp_position_centroid":[0.51775,0.00197,0.20632]}],"total_contact_groups":5},"final_pose_error":0.0198,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49584,-0.16761,0.02513],"final_tcp_position":[0.5017,-0.13106,0.02948],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":212.36701,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":694.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_hover","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2776.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.53801,0.00403,0.11261],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.09271,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":904.0,"n_steps_budget":1000.0,"object_pos_end":[0.5434,-0.03393,0.02522],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.12392,"object_to_goal_dist_start":0.13211,"object_z_max":0.02922,"peak_contact_force":0.45125,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3358.0,"raw_peak_contact_force":212.36701,"subtask_id":"reach_contact","tcp_end":[0.54579,0.00511,0.02963],"tcp_start":[0.53801,0.00403,0.11261],"tcp_to_object_dist_end":0.03936,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":385.0,"n_steps_budget":1000.0,"object_pos_end":[0.49584,-0.16761,0.02513],"object_pos_start":[0.5434,-0.03393,0.02522],"object_to_goal_dist_end":0.0181,"object_to_goal_dist_start":0.12392,"object_z_max":0.02628,"peak_contact_force":0.0,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":776.0,"raw_peak_contact_force":48.84172,"subtask_id":"reach_goal","tcp_end":[0.5017,-0.13106,0.02948],"tcp_start":[0.54579,0.00511,0.02963],"tcp_to_object_dist_end":0.03727,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```