## Search State

- **Seed**: 0
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.2595 | 0.00 | ❌ rejected |
| 5 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | -0.1678 | 0.00 | ❌ rejected |
| 4 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.2843 | 0.00 | ❌ rejected |
| 3 | insert → approach → push → retract → lift → insert | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | linear_cartesian | impedance_motion | impedance_control | force_threshold_switch | impedance_control | position_control | position_control | admittance_control | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 5 | 0.2384 | 0.80 | ❌ rejected |
| 2 | insert → approach → push → retract → lift → insert | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | linear_cartesian | impedance_motion | impedance_control | force_threshold_switch | impedance_control | position_control | position_control | admittance_control | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 5 | 0.2392 | 0.81 | ❌ rejected |

**Proposal policy**: task_score is 0.00 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.819, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=-0.260) — your mutation base

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

- **Composite score**: -0.260
- **task_score** (E): 0.005
- **fitness_score**: 0.100  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach | 1.00 | 1.00 | 0.1714 |
| descend | 1.00 | 1.00 | 0.0877 |
| push | 0.00 | 1.00 | 0.0001 |
| retract | 1.00 | 1.00 | 0.1884 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.494, 0.001, 0.134) | (0.496, 0.001, 0.025)→(0.496, 0.001, 0.025) | 0.152→0.152 | 1.00 / 4.000 | 0.245 | 0.245 |
| descend | descend | 1.00 / step_budget | (0.494, 0.001, 0.134)→(0.509, 0.001, 0.048) | (0.496, 0.001, 0.025)→(0.501, 0.001, 0.024) | 0.152→0.152 | 1.00 / 5.000 | 250.995 | 275.603 |
| push | push | 0.00 / guard_failure | (0.509, 0.001, 0.048)→(0.509, 0.001, 0.048) | (0.501, 0.001, 0.024)→(0.501, 0.001, 0.024) | 0.152→0.152 | 1.00 / 5.000 | 141.324 | 141.324 |
| retract | retract | 1.00 / step_budget | (0.509, 0.001, 0.048)→(0.499, -0.132, 0.178) | (0.501, 0.001, 0.024)→(0.500, 0.000, 0.025) | 0.152→0.152 | 1.00 / 4.000 | 0.245 | 147.675 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.044
- lateral_force_integral: None
- approach_alignment: 0.862
- goal_progress: 0.008
- terminal_score: 0.008
- phase_score: 0.164
- phase_breakdown.push_to_goal_score: 0.000
- phase_breakdown.reach_object_score: 0.545

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.101
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.008
- **Median Q (composite search score)**: -0.259
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.350


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.10465,"average_solve_count":86.0,"average_success_count":86.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.12998,"descend.descend_speed":0.08747,"push.push_distance":0.18136,"push.push_speed":0.06717,"retract.arc_height":0.09473,"retract.retract_speed":0.13517},"optimized_scores":{"best_composite_score":-0.25852,"best_fitness_score":0.10148,"best_task_score":0.00822},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":136.0,"contact_point_centroid":[0.53118,-0.02745,0.04653],"force_p95":258.0189,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":263.38243,"mean_force":224.6132,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.52001,-0.02747,0.04907]},{"body_a":"attachment","body_b":"push_box","contact_count":31.0,"contact_point_centroid":[0.54014,-0.02697,0.0488],"force_p95":74.07609,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":140.62626,"mean_force":18.18613,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.52905,-0.0255,0.05175]},{"body_a":"attachment","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.54006,-0.02803,0.04544],"force_p95":134.26489,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":135.2389,"mean_force":123.01684,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.52875,-0.02807,0.04732]},{"body_a":"world","body_b":"push_box","contact_count":1541.0,"contact_point_centroid":[0.51716,-0.02782,-0.00018],"force_p95":118.97211,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":133.57194,"mean_force":20.17601,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.51372,-0.02657,0.07851]},{"body_a":"world","body_b":"push_box","contact_count":2255.0,"contact_point_centroid":[0.52166,-0.02883,-4e-05],"force_p95":0.32958,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":72.44621,"mean_force":0.50666,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.52285,-0.04194,0.14118]},{"body_a":"world","body_b":"push_box","contact_count":12.0,"contact_point_centroid":[0.51972,-0.02789,-0.00061],"force_p95":66.31272,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":67.61567,"mean_force":31.05784,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.52875,-0.02807,0.04732]},{"body_a":"world","body_b":"push_box","contact_count":2104.0,"contact_point_centroid":[0.51644,-0.02763,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.50503,-0.01242,0.21706]}],"total_contact_groups":7},"final_pose_error":0.01971,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52155,-0.02945,0.02499],"final_tcp_position":[0.50206,-0.13087,0.17925],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51644,-0.02763,0.025]},"peak_contact_force":263.38243,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":526.0,"n_steps_budget":870.0,"object_pos_end":[0.51644,-0.02763,0.02499],"object_pos_start":[0.51644,-0.02763,0.025],"object_to_goal_dist_end":0.12347,"object_to_goal_dist_start":0.12347,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2104.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.5119,-0.02543,0.13345],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.10858,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":388.0,"n_steps_budget":780.0,"object_pos_end":[0.52089,-0.02792,0.02375],"object_pos_start":[0.51644,-0.02763,0.02499],"object_to_goal_dist_end":0.12386,"object_to_goal_dist_start":0.12347,"object_z_max":0.02499,"peak_contact_force":242.40416,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1677.0,"raw_peak_contact_force":263.38243,"subtask_id":"reach_object","tcp_end":[0.52868,-0.02806,0.04728],"tcp_start":[0.5119,-0.02543,0.13345],"tcp_to_object_dist_end":0.02479,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.52089,-0.02792,0.02376],"object_pos_start":[0.52089,-0.02792,0.02375],"object_to_goal_dist_end":0.12386,"object_to_goal_dist_start":0.12386,"object_z_max":0.02377,"peak_contact_force":135.2389,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":15.0,"raw_peak_contact_force":135.2389,"subtask_id":"push_to_goal","tcp_end":[0.52889,-0.02808,0.04743],"tcp_start":[0.52882,-0.02807,0.04736],"tcp_to_object_dist_end":0.02499,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":589.0,"n_steps_budget":840.0,"object_pos_end":[0.52155,-0.02945,0.02499],"object_pos_start":[0.52086,-0.02792,0.02378],"object_to_goal_dist_end":0.12246,"object_to_goal_dist_start":0.12386,"object_z_max":0.02694,"peak_contact_force":0.24525,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2286.0,"raw_peak_contact_force":140.62626,"tcp_end":[0.50206,-0.13087,0.17925],"tcp_start":[0.52889,-0.02808,0.04743],"tcp_to_object_dist_end":0.18564,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.39175,"average_solve_count":97.0,"average_success_count":97.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.14707,"descend.descend_speed":0.09992,"push.push_distance":0.12099,"push.push_speed":0.0562,"retract.arc_height":0.12403,"retract.retract_speed":0.11077},"optimized_scores":{"best_composite_score":-0.26113,"best_fitness_score":0.09887,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":125.0,"contact_point_centroid":[0.51574,0.05356,0.04652],"force_p95":266.00364,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":273.33235,"mean_force":230.36942,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.50472,0.05339,0.04939]},{"body_a":"attachment","body_b":"push_box","contact_count":26.0,"contact_point_centroid":[0.52421,0.05544,0.0478],"force_p95":74.77172,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":144.96382,"mean_force":19.32734,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.51313,0.05586,0.05098]},{"body_a":"world","body_b":"push_box","contact_count":1487.0,"contact_point_centroid":[0.50215,0.05436,-0.00017],"force_p95":121.97502,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":140.19921,"mean_force":19.71661,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.49902,0.05165,0.07946]},{"body_a":"attachment","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.52447,0.05462,0.04534],"force_p95":136.51396,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":137.62775,"mean_force":124.35804,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.5133,0.05455,0.04751]},{"body_a":"world","body_b":"push_box","contact_count":3278.0,"contact_point_centroid":[0.50493,0.05471,-2e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":72.66369,"mean_force":0.40184,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.50778,0.00622,0.16644]},{"body_a":"world","body_b":"push_box","contact_count":12.0,"contact_point_centroid":[0.50467,0.05456,-0.00062],"force_p95":65.10794,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":65.40259,"mean_force":31.3719,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.5133,0.05455,0.04751]},{"body_a":"world","body_b":"push_box","contact_count":2088.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49825,0.02429,0.2168]}],"total_contact_groups":7},"final_pose_error":0.01963,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50483,0.05442,0.02499],"final_tcp_position":[0.49876,-0.13367,0.18582],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50142,0.05406,0.025]},"peak_contact_force":273.33235,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":522.0,"n_steps_budget":780.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.025],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2088.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.49809,0.04965,0.13333],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.10848,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":375.0,"n_steps_budget":690.0,"object_pos_end":[0.50587,0.0546,0.02372],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.20469,"object_to_goal_dist_start":0.20406,"object_z_max":0.02499,"peak_contact_force":249.65323,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1612.0,"raw_peak_contact_force":273.33235,"subtask_id":"reach_object","tcp_end":[0.51322,0.05454,0.04747],"tcp_start":[0.49809,0.04965,0.13333],"tcp_to_object_dist_end":0.02486,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50586,0.0546,0.02372],"object_pos_start":[0.50587,0.0546,0.02372],"object_to_goal_dist_end":0.20469,"object_to_goal_dist_start":0.20469,"object_z_max":0.02373,"peak_contact_force":137.62775,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":15.0,"raw_peak_contact_force":137.62775,"subtask_id":"push_to_goal","tcp_end":[0.51345,0.05457,0.04762],"tcp_start":[0.51338,0.05456,0.04755],"tcp_to_object_dist_end":0.02507,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":832.0,"n_steps_budget":1000.0,"object_pos_end":[0.50483,0.05442,0.02499],"object_pos_start":[0.50583,0.0546,0.02375],"object_to_goal_dist_end":0.20447,"object_to_goal_dist_start":0.20469,"object_z_max":0.02555,"peak_contact_force":0.24525,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3304.0,"raw_peak_contact_force":144.96382,"tcp_end":[0.49876,-0.13367,0.18582],"tcp_start":[0.51345,0.05457,0.04762],"tcp_to_object_dist_end":0.24755,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.04762,"average_solve_count":84.0,"average_success_count":84.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.15989,"descend.descend_speed":0.09918,"push.push_distance":0.21647,"push.push_speed":0.01353,"retract.arc_height":0.19487,"retract.retract_speed":0.11414},"optimized_scores":{"best_composite_score":-0.25899,"best_fitness_score":0.10101,"best_task_score":0.00595},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":131.0,"contact_point_centroid":[0.48628,-0.02414,0.04627],"force_p95":279.27775,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":290.09473,"mean_force":242.53182,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.47563,-0.02403,0.04976]},{"body_a":"attachment","body_b":"push_box","contact_count":23.0,"contact_point_centroid":[0.49485,-0.0248,0.04721],"force_p95":81.47144,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":157.43612,"mean_force":17.96506,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.48411,-0.02468,0.05111]},{"body_a":"attachment","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.49516,-0.02465,0.04505],"force_p95":150.13138,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":151.10388,"mean_force":136.14528,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.48433,-0.0246,0.04785]},{"body_a":"world","body_b":"push_box","contact_count":1534.0,"contact_point_centroid":[0.47212,-0.02448,-0.00019],"force_p95":128.25163,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":144.46999,"mean_force":21.05664,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.47048,-0.0232,0.08027]},{"body_a":"world","body_b":"push_box","contact_count":1992.0,"contact_point_centroid":[0.47397,-0.02441,-2e-05],"force_p95":0.24538,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":81.17367,"mean_force":0.45102,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.48642,-0.06126,0.12121]},{"body_a":"world","body_b":"push_box","contact_count":12.0,"contact_point_centroid":[0.47436,-0.02441,-0.00065],"force_p95":74.57581,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":76.21168,"mean_force":34.345,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.48433,-0.0246,0.04785]},{"body_a":"world","body_b":"push_box","contact_count":1908.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.48489,-0.0108,0.21788]}],"total_contact_groups":7},"final_pose_error":0.0197,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.47396,-0.02441,0.02499],"final_tcp_position":[0.49523,-0.13204,0.16845],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":290.09473,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":477.0,"n_steps_budget":720.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1908.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.47061,-0.02218,0.13466],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.1097,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":388.0,"n_steps_budget":720.0,"object_pos_end":[0.47563,-0.02444,0.02365],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12791,"object_to_goal_dist_start":0.12903,"object_z_max":0.02499,"peak_contact_force":260.92698,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1665.0,"raw_peak_contact_force":290.09473,"subtask_id":"reach_object","tcp_end":[0.48426,-0.0246,0.04782],"tcp_start":[0.47061,-0.02218,0.13466],"tcp_to_object_dist_end":0.02566,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.47563,-0.02444,0.02366],"object_pos_start":[0.47563,-0.02444,0.02365],"object_to_goal_dist_end":0.12791,"object_to_goal_dist_start":0.12791,"object_z_max":0.02367,"peak_contact_force":151.10388,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":15.0,"raw_peak_contact_force":151.10388,"subtask_id":"push_to_goal","tcp_end":[0.48447,-0.02461,0.04796],"tcp_start":[0.4844,-0.02461,0.0479],"tcp_to_object_dist_end":0.02586,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":498.0,"n_steps_budget":990.0,"object_pos_end":[0.47396,-0.02441,0.02499],"object_pos_start":[0.47561,-0.02445,0.02369],"object_to_goal_dist_end":0.12826,"object_to_goal_dist_start":0.12791,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2015.0,"raw_peak_contact_force":157.43612,"tcp_end":[0.49523,-0.13204,0.16845],"tcp_start":[0.48447,-0.02461,0.04796],"tcp_to_object_dist_end":0.1806,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```