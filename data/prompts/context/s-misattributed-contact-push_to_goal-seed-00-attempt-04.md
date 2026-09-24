## Search State

- **Seed**: 0
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.0128 | 0.39 | ❌ rejected |
| 3 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | -0.4169 | 0.00 | ❌ rejected |
| 2 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.3196 | 0.39 | ❌ rejected |
| 1 | insert → approach → push → retract → lift → insert | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | linear_cartesian | impedance_motion | impedance_control | force_threshold_switch | impedance_control | position_control | position_control | admittance_control | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 5 | 0.2365 | 0.82 | ✅ accepted |
| 0 | insert → approach → push → retract → lift → insert | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | linear_cartesian | impedance_motion | impedance_control | force_threshold_switch | impedance_control | position_control | position_control | admittance_control | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 5 | 0.2322 | 0.80 | ✅ accepted |

**Proposal policy**: task_score is 0.39 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.013) — your mutation base

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

- **Composite score**: 0.013
- **task_score** (E): 0.387
- **fitness_score**: 0.473  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.460

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1808 |
| descend_1 | 1.00 | 1.00 | 0.0810 |
| push_1 | 0.33 | 1.00 | 0.1517 |
| retract_1 | 1.00 | 1.00 | 0.0802 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.493, 0.001, 0.124) | (0.496, 0.001, 0.025)→(0.496, 0.001, 0.025) | 0.152→0.152 | 1.00 / 4.000 | 239.005 | 246.141 |
| descend_1 | descend | 1.00 / step_budget | (0.493, 0.001, 0.124)→(0.509, 0.019, 0.047) | (0.496, 0.001, 0.025)→(0.501, 0.002, 0.024) | 0.152→0.154 | 1.00 / 4.000 | 0.245 | 170.965 |
| push_1 | push | 0.33 / step_budget | (0.509, 0.019, 0.047)→(0.501, -0.129, 0.027) | (0.501, 0.002, 0.024)→(0.516, -0.057, 0.025) | 0.154→0.096 | 1.00 / 4.000 | 0.245 | 0.245 |
| retract_1 | retract | 1.00 / step_budget | (0.501, -0.129, 0.027)→(0.497, -0.129, 0.107) | (0.516, -0.057, 0.025)→(0.516, -0.057, 0.025) | 0.096→0.096 | 1.00 / 4.000 | 0.245 | 0.245 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.457
- lateral_force_integral: None
- approach_alignment: 0.825
- goal_progress: 0.456
- terminal_score: 0.456
- phase_score: 0.565
- phase_breakdown.pre_push_score: 0.534
- phase_breakdown.reach_above_score: 0.859
- phase_breakdown.push_object_score: 0.465

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.521
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.456
- **Median Q (composite search score)**: 0.032
- **K-run variance**: 0.0024
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.368


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.23438,"average_solve_count":192.0,"average_success_count":192.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.09726,"approach_1.approach_speed":0.04662,"descend_1.descend_lateral_offset":0.01602,"descend_1.descend_speed":0.05823,"push_1.push_distance":0.24766,"push_1.push_speed":0.07793,"retract_1.retract_height":0.13871,"retract_1.retract_speed":0.06504},"optimized_scores":{"best_composite_score":0.06121,"best_fitness_score":0.52121,"best_task_score":0.45627},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":276.0,"contact_point_centroid":[0.534,-0.01521,0.04664],"force_p95":238.16107,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":239.18817,"mean_force":186.37836,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52286,-0.01428,0.04938]},{"body_a":"world","body_b":"push_box","contact_count":2678.0,"contact_point_centroid":[0.51954,-0.02518,-0.00019],"force_p95":128.37173,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":179.52637,"mean_force":19.51262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51447,-0.0188,0.07779]},{"body_a":"attachment","body_b":"push_box","contact_count":764.0,"contact_point_centroid":[0.5379,-0.05421,0.04585],"force_p95":150.36324,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":153.41606,"mean_force":117.49263,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5282,-0.05796,0.04774]},{"body_a":"world","body_b":"push_box","contact_count":2475.0,"contact_point_centroid":[0.52021,-0.05838,-0.00039],"force_p95":135.55933,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":147.06137,"mean_force":36.80687,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52129,-0.07833,0.04319]},{"body_a":"world","body_b":"push_box","contact_count":2396.0,"contact_point_centroid":[0.51644,-0.02763,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5049,-0.01242,0.21578]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.50712,-0.08324,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49795,-0.14067,0.08417]}],"total_contact_groups":6},"final_pose_error":0.03181,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50712,-0.08324,0.02499],"final_tcp_position":[0.49816,-0.14068,0.13796],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51644,-0.02763,0.025]},"peak_contact_force":239.18817,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":599.0,"n_steps_budget":1000.0,"object_pos_end":[0.51644,-0.02763,0.02499],"object_pos_start":[0.51644,-0.02763,0.025],"object_to_goal_dist_end":0.12347,"object_to_goal_dist_start":0.12347,"object_z_max":0.025,"peak_contact_force":231.23418,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2954.0,"raw_peak_contact_force":239.18817,"subtask_id":"reach_above","tcp_end":[0.51188,-0.02546,0.13069],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.10582,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":735.0,"n_steps_budget":1000.0,"object_pos_end":[0.52167,-0.02644,0.02431],"object_pos_start":[0.51644,-0.02763,0.02499],"object_to_goal_dist_end":0.12545,"object_to_goal_dist_start":0.12347,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3239.0,"raw_peak_contact_force":153.41606,"subtask_id":"pre_push","tcp_end":[0.53297,-0.01228,0.04675],"tcp_start":[0.51188,-0.02546,0.13069],"tcp_to_object_dist_end":0.02883,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50712,-0.08324,0.02499],"object_pos_start":[0.52167,-0.02644,0.02431],"object_to_goal_dist_end":0.06714,"object_to_goal_dist_start":0.12545,"object_z_max":0.03544,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"subtask_id":"push_object","tcp_end":[0.50152,-0.14142,0.03087],"tcp_start":[0.53297,-0.01228,0.04675],"tcp_to_object_dist_end":0.05874,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50712,-0.08324,0.02499],"object_pos_start":[0.50712,-0.08324,0.02499],"object_to_goal_dist_end":0.06714,"object_to_goal_dist_start":0.06714,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2396.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.49816,-0.14068,0.13796],"tcp_start":[0.50152,-0.14142,0.03087],"tcp_to_object_dist_end":0.12705,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.28108,"average_solve_count":185.0,"average_success_count":185.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.09058,"approach_1.approach_speed":0.05588,"descend_1.descend_lateral_offset":0.01934,"descend_1.descend_speed":0.07846,"push_1.push_distance":0.18278,"push_1.push_speed":0.09675,"retract_1.retract_height":0.10943,"retract_1.retract_speed":0.04061},"optimized_scores":{"best_composite_score":-0.05462,"best_fitness_score":0.40538,"best_task_score":0.28723},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":221.0,"contact_point_centroid":[0.5165,0.06818,0.04661],"force_p95":247.20873,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":251.3738,"mean_force":192.99944,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5055,0.06898,0.04968]},{"body_a":"world","body_b":"push_box","contact_count":2263.0,"contact_point_centroid":[0.50427,0.05654,-0.00018],"force_p95":140.20313,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":205.93729,"mean_force":19.16223,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49868,0.06059,0.07637]},{"body_a":"world","body_b":"push_box","contact_count":2140.0,"contact_point_centroid":[0.53847,0.01807,-0.00049],"force_p95":164.56851,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":175.21999,"mean_force":44.60195,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51043,-0.01183,0.03846]},{"body_a":"attachment","body_b":"push_box","contact_count":602.0,"contact_point_centroid":[0.52882,0.03443,0.04559],"force_p95":170.53299,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":173.89899,"mean_force":143.91006,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51849,0.03177,0.04838]},{"body_a":"push_box","body_b":"link7","contact_count":212.0,"contact_point_centroid":[0.55398,-0.00639,0.06703],"force_p95":60.90994,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":64.7014,"mean_force":35.35405,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50632,-0.03824,0.03327]},{"body_a":"world","body_b":"push_box","contact_count":2548.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49812,0.0244,0.21207]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.54444,-0.01151,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49577,-0.08415,0.06935]}],"total_contact_groups":7},"final_pose_error":0.019,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.54444,-0.01151,0.02499],"final_tcp_position":[0.49593,-0.08414,0.11515],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50142,0.05406,0.025]},"peak_contact_force":251.3738,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":637.0,"n_steps_budget":1000.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.025],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.025,"peak_contact_force":238.71962,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2484.0,"raw_peak_contact_force":251.3738,"subtask_id":"reach_above","tcp_end":[0.49799,0.04986,0.12385],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.09901,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":618.0,"n_steps_budget":810.0,"object_pos_end":[0.50644,0.05673,0.02428],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.20683,"object_to_goal_dist_start":0.20406,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2954.0,"raw_peak_contact_force":175.21999,"subtask_id":"pre_push","tcp_end":[0.51533,0.07368,0.04679],"tcp_start":[0.49799,0.04986,0.12385],"tcp_to_object_dist_end":0.02955,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54444,-0.01151,0.02499],"object_pos_start":[0.50644,0.05673,0.02428],"object_to_goal_dist_end":0.14545,"object_to_goal_dist_start":0.20683,"object_z_max":0.03536,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"subtask_id":"push_object","tcp_end":[0.49947,-0.08456,0.02437],"tcp_start":[0.51533,0.07368,0.04679],"tcp_to_object_dist_end":0.08579,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54444,-0.01151,0.02499],"object_pos_start":[0.54444,-0.01151,0.02499],"object_to_goal_dist_end":0.14545,"object_to_goal_dist_start":0.14545,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2548.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.49593,-0.08414,0.11515],"tcp_start":[0.49947,-0.08456,0.02437],"tcp_to_object_dist_end":0.12553,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.63057,"average_solve_count":314.0,"average_success_count":314.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.08346,"approach_1.approach_speed":0.01438,"descend_1.descend_lateral_offset":0.02155,"descend_1.descend_speed":0.01267,"push_1.push_distance":0.19689,"push_1.push_speed":0.09954,"retract_1.retract_height":0.05153,"retract_1.retract_speed":0.02173},"optimized_scores":{"best_composite_score":0.03192,"best_fitness_score":0.49192,"best_task_score":0.4174},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":586.0,"contact_point_centroid":[0.48443,-0.00785,0.04661],"force_p95":247.29277,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":247.8602,"mean_force":187.1883,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47387,-0.00712,0.0505]},{"body_a":"attachment","body_b":"push_box","contact_count":646.0,"contact_point_centroid":[0.50055,-0.04579,0.04553],"force_p95":163.98753,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":184.25778,"mean_force":125.12034,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49388,-0.05126,0.04742]},{"body_a":"world","body_b":"push_box","contact_count":3489.0,"contact_point_centroid":[0.4759,-0.02056,-0.00032],"force_p95":131.42927,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":171.71127,"mean_force":31.73238,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.46989,-0.01165,0.06744]},{"body_a":"world","body_b":"push_box","contact_count":2440.0,"contact_point_centroid":[0.49651,-0.05787,-0.00034],"force_p95":121.06439,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":132.87682,"mean_force":33.62524,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49518,-0.09346,0.0381]},{"body_a":"world","body_b":"push_box","contact_count":2512.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48456,-0.01089,0.20965]},{"body_a":"world","body_b":"push_box","contact_count":2352.0,"contact_point_centroid":[0.4974,-0.07487,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49719,-0.16151,0.04678]}],"total_contact_groups":6},"final_pose_error":0.00996,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.4974,-0.07487,0.02499],"final_tcp_position":[0.49705,-0.16142,0.06819],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":247.8602,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":628.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":247.06022,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4075.0,"raw_peak_contact_force":247.8602,"subtask_id":"reach_above","tcp_end":[0.47019,-0.02235,0.11803],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.09307,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47435,-0.02363,0.02409],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12895,"object_to_goal_dist_start":0.12903,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3086.0,"raw_peak_contact_force":184.25778,"subtask_id":"pre_push","tcp_end":[0.47992,-0.00467,0.048],"tcp_start":[0.47019,-0.02235,0.11803],"tcp_to_object_dist_end":0.03102,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4974,-0.07487,0.02499],"object_pos_start":[0.47435,-0.02363,0.02409],"object_to_goal_dist_end":0.07517,"object_to_goal_dist_start":0.12895,"object_z_max":0.036,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2352.0,"raw_peak_contact_force":0.24525,"subtask_id":"push_object","tcp_end":[0.50092,-0.16239,0.02579],"tcp_start":[0.47992,-0.00467,0.048],"tcp_to_object_dist_end":0.08759,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":588.0,"n_steps_budget":1000.0,"object_pos_end":[0.4974,-0.07487,0.02499],"object_pos_start":[0.4974,-0.07487,0.02499],"object_to_goal_dist_end":0.07517,"object_to_goal_dist_start":0.07517,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2512.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.49705,-0.16142,0.06819],"tcp_start":[0.50092,-0.16239,0.02579],"tcp_to_object_dist_end":0.09673,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```