## Search State

- **Seed**: 9
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | 0.1613 | 0.32 | ❌ rejected |
| 10 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | force_threshold_switch | admittance_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 5 | 0.6844 | 0.80 | ❌ rejected |
| 9 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 11 | -0.2047 | 0.05 | ❌ rejected |
| 8 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 11 | 0.1400 | 0.45 | ❌ rejected |
| 7 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | 0.2588 | 0.60 | ❌ rejected |

**Proposal policy**: task_score is 0.32 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `2cf7387f3e8baf02f18930263090d6f78777bdbc147b7fa30c178332e76b547b`
- Frozen object start: [0.5444299044764102, -0.025581934909493356, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.5444299044764102, -0.025581934909493356, 0.025)
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
  frozen_object_start: [0.5444, -0.0256, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.5444299044764102, -0.025581934909493356, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [-0.0444, -0.1244, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: 2cf7387f3e8baf02f18930263090d6f78777bdbc147b7fa30c178332e76b547b

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.813, which indicates the subtask decomposition is already effective.
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
| `object` | offset from object initial position (0.5444299044764102, -0.025581934909493356, 0.025) | approach/contact targets near object start |
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

## Current Skill (Q=0.161) — your mutation base

```yaml
skill: push_to_goal
phases:
- id: approach_1
  type: approach
  generator: arc_cartesian
  control: force_threshold_switch
  termination: pose_tolerance
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.3
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: admittance_control
  termination: force_exceeded
  parameters:
    speed:
      type: scalar
      range:
      - 0.005
      - 0.05
- id: push_1
  type: push
  generator: linear_cartesian
  control: position_control
  termination: time_limit
  parameters:
    push_speed:
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
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1

```

## Design Metrics

- **Composite score**: 0.161
- **task_score** (E): 0.315
- **fitness_score**: 0.371  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.460

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1920 |
| contact_1 | 1.00 | 1.00 | 0.1031 |
| push_1 | 0.00 | 1.00 | 0.0559 |
| retract_1 | 1.00 | 1.00 | 0.1114 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.576, 0.037, 0.138) | (0.518, -0.020, 0.025)→(0.518, -0.020, 0.025) | 0.139→0.139 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / force_exceeded | (0.576, 0.037, 0.138)→(0.549, 0.015, 0.041) | (0.518, -0.020, 0.025)→(0.518, -0.020, 0.025) | 0.139→0.139 | 1.00 / 5.000 | 25308.749 | 0.245 |
| push_1 | push | 0.00 / guard_failure | (0.549, 0.015, 0.041)→(0.523, -0.034, 0.033) | (0.518, -0.020, 0.025)→(0.488, -0.052, 0.025) | 0.139→0.101 | 1.00 / 2.667 | 0.440 | 26.904 |
| retract_1 | retract | 1.00 / step_budget | (0.523, -0.034, 0.033)→(0.520, -0.034, 0.144) | (0.488, -0.052, 0.025)→(0.485, -0.055, 0.025) | 0.101→0.098 | 1.00 / 4.000 | 0.245 | 6.225 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.554
- lateral_force_integral: None
- approach_alignment: 0.631
- goal_progress: 0.453
- terminal_score: 0.453
- phase_score: 0.463
- phase_breakdown.reach_contact_score: 0.731
- phase_breakdown.reach_above_object_score: 0.675
- phase_breakdown.reach_goal_score: 0.217

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.459
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.470
- **Median Q (composite search score)**: 0.217
- **K-run variance**: 0.0105
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.344


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `327b95871eb659cd41b4cf66bc0b4dfb3b240662e8501854b46ee2b8b86a04c5`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `5ffd2bb280d1d50ec9ffd23c1ed75abf73d645c1d10372a9b5bb6e9fac6e0bf8`; realized-scene SHA-256: `2cf7387f3e8baf02f18930263090d6f78777bdbc147b7fa30c178332e76b547b`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.54443,-0.02558,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.04443,-0.12442,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.54443,-0.02558,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.04846,"average_solve_count":227.0,"average_success_count":227.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.1041,"approach_1.speed":0.06862,"contact_1.force_threshold":5.90217,"contact_1.speed":0.02822,"push_1.overshoot":0.04243,"push_1.push_speed":0.03944,"retract_1.retract_height":0.05479,"retract_1.speed":0.09025},"optimized_scores":{"best_composite_score":0.24907,"best_fitness_score":0.45907,"best_task_score":0.45316},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":80.0,"contact_point_centroid":[0.5456,-0.03271,0.03533],"force_p95":17.23122,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.22537,"mean_force":3.66073,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.55625,-0.02967,0.03288]},{"body_a":"world","body_b":"push_box","contact_count":239.0,"contact_point_centroid":[0.51235,-0.05977,-9e-05],"force_p95":6.17265,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.83589,"mean_force":1.68658,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5524,-0.03768,0.03192]},{"body_a":"attachment","body_b":"push_box","contact_count":20.0,"contact_point_centroid":[0.51804,-0.08046,0.04234],"force_p95":1.60637,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.27473,"mean_force":0.9248,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.52964,-0.08151,0.03956]},{"body_a":"world","body_b":"push_box","contact_count":374.0,"contact_point_centroid":[0.48657,-0.07715,-8e-05],"force_p95":0.56893,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.99672,"mean_force":0.32255,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.52939,-0.08135,0.0462]},{"body_a":"world","body_b":"push_box","contact_count":2276.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.58817,0.02306,0.25629]},{"body_a":"world","body_b":"push_box","contact_count":1768.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.592,0.01911,0.08783]}],"total_contact_groups":6},"final_pose_error":0.01974,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49346,-0.07805,0.02493],"final_tcp_position":[0.52876,-0.08062,0.06321],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":20.22537,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":569.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2276.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_above_object","tcp_end":[0.60906,0.02876,0.13732],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.14053,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":442.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.02499,"peak_contact_force":18.5846,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1768.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_contact","tcp_end":[0.57657,0.00883,0.03987],"tcp_start":[0.60906,0.02876,0.13732],"tcp_to_object_dist_end":0.04939,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":170.0,"n_steps_budget":1000.0,"object_pos_end":[0.49586,-0.07579,0.02505],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.07432,"object_to_goal_dist_start":0.13211,"object_z_max":0.026,"peak_contact_force":1.31754,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":319.0,"raw_peak_contact_force":20.22537,"subtask_id":"reach_goal","tcp_end":[0.53226,-0.08086,0.02784],"tcp_start":[0.57657,0.00883,0.03987],"tcp_to_object_dist_end":0.03685,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":127.0,"n_steps_budget":600.0,"object_pos_end":[0.49346,-0.07805,0.02493],"object_pos_start":[0.49586,-0.07579,0.02505],"object_to_goal_dist_end":0.07224,"object_to_goal_dist_start":0.07432,"object_z_max":0.02548,"peak_contact_force":0.24579,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":394.0,"raw_peak_contact_force":3.27473,"tcp_end":[0.52876,-0.08062,0.06321],"tcp_start":[0.53226,-0.08086,0.02784],"tcp_to_object_dist_end":0.05213,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `e094d2c5a71c8b89ef1fa30d7ce553b9c4ed64cd3fbca90620c3ede94e719cec`; realized-scene SHA-256: `d6f67641a3df0efca2ae6de2763dea57e4736e336d1ca3e6fe373ea0745d2d85`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.55472,-0.03508,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.05472,-0.11492,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.55472,-0.03508,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.80466,"average_solve_count":343.0,"average_success_count":343.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.12701,"approach_1.speed":0.04231,"contact_1.force_threshold":9.47639,"contact_1.speed":0.02107,"push_1.overshoot":0.05889,"push_1.push_speed":0.09742,"retract_1.retract_height":0.18288,"retract_1.speed":0.02697},"optimized_scores":{"best_composite_score":0.21707,"best_fitness_score":0.42707,"best_task_score":0.46976},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":37.0,"contact_point_centroid":[0.56311,-0.03219,0.03914],"force_p95":17.53674,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.86653,"mean_force":5.03914,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5715,-0.02414,0.03722]},{"body_a":"world","body_b":"push_box","contact_count":101.0,"contact_point_centroid":[0.52489,-0.06176,-5e-05],"force_p95":8.82997,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.22972,"mean_force":2.53326,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.56972,-0.02714,0.03674]},{"body_a":"world","body_b":"push_box","contact_count":2330.0,"contact_point_centroid":[0.51044,-0.08335,-2e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.36149,"mean_force":0.24919,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.55026,-0.05505,0.1137]},{"body_a":"attachment","body_b":"push_box","contact_count":4.0,"contact_point_centroid":[0.54217,-0.05902,0.0352],"force_p95":0.26878,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28983,"mean_force":0.10983,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.55331,-0.05574,0.0326]},{"body_a":"world","body_b":"push_box","contact_count":2224.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.58486,0.01223,0.25408]},{"body_a":"world","body_b":"push_box","contact_count":1772.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.60053,0.00842,0.09112]}],"total_contact_groups":6},"final_pose_error":0.01974,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51041,-0.08332,0.02499],"final_tcp_position":[0.55078,-0.0549,0.19604],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55472,-0.03508,0.025]},"peak_contact_force":75893.53664,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":556.0,"n_steps_budget":1000.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.025],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2224.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_above_object","tcp_end":[0.61594,0.0168,0.14097],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.14103,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":443.0,"n_steps_budget":1000.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.02499,"peak_contact_force":75893.53664,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1772.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_contact","tcp_end":[0.58686,-0.0006,0.04282],"tcp_start":[0.61594,0.0168,0.14097],"tcp_to_object_dist_end":0.05039,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":102.0,"n_steps_budget":1000.0,"object_pos_end":[0.51434,-0.07969,0.02498],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.07176,"object_to_goal_dist_start":0.12728,"object_z_max":0.02596,"peak_contact_force":0.00098,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":138.0,"raw_peak_contact_force":23.86653,"subtask_id":"reach_goal","tcp_end":[0.55352,-0.05509,0.03271],"tcp_start":[0.58686,-0.0006,0.04282],"tcp_to_object_dist_end":0.04691,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":592.0,"n_steps_budget":1000.0,"object_pos_end":[0.51041,-0.08332,0.02499],"object_pos_start":[0.51434,-0.07969,0.02498],"object_to_goal_dist_end":0.06749,"object_to_goal_dist_start":0.07176,"object_z_max":0.02544,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2334.0,"raw_peak_contact_force":1.36149,"tcp_end":[0.55078,-0.0549,0.19604],"tcp_start":[0.55352,-0.05509,0.03271],"tcp_to_object_dist_end":0.17803,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `0fd7d18e656259f06515eb57b82afa0c0febd9395a43c1a5f926ddaec3767c64`; realized-scene SHA-256: `5de0d8cc5a3c16249bcf1097af6edba15dfacc79d06e3eed726605dcb01257b0`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45543,-9e-05,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.04457,-0.14991,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.45543,-9e-05,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.41509,"average_solve_count":159.0,"average_success_count":159.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.10603,"approach_1.speed":0.07349,"contact_1.force_threshold":8.737,"contact_1.speed":0.04602,"push_1.overshoot":0.08312,"push_1.push_speed":0.06041,"retract_1.retract_height":0.15516,"retract_1.speed":0.06345},"optimized_scores":{"best_composite_score":0.01778,"best_fitness_score":0.22778,"best_task_score":0.02283},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":11.0,"contact_point_centroid":[0.48036,0.02442,0.04026],"force_p95":27.48162,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":36.62028,"mean_force":6.46518,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48422,0.03562,0.0394]},{"body_a":"world","body_b":"push_box","contact_count":19.0,"contact_point_centroid":[0.44873,0.00102,-3e-05],"force_p95":14.93792,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":24.20747,"mean_force":3.94395,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48426,0.03565,0.03946]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.48034,0.023,0.03967],"force_p95":14.03813,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.03813,"mean_force":14.03813,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48409,0.03429,0.03884]},{"body_a":"world","body_b":"push_box","contact_count":1647.0,"contact_point_centroid":[0.45206,-0.0053,-1e-05],"force_p95":0.24578,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.7922,"mean_force":0.26332,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48122,0.03394,0.10759]},{"body_a":"world","body_b":"push_box","contact_count":1920.0,"contact_point_centroid":[0.45543,-9e-05,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49997,0.06938,0.23491]},{"body_a":"world","body_b":"push_box","contact_count":2144.0,"contact_point_centroid":[0.45543,-9e-05,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49209,0.05148,0.08591]}],"total_contact_groups":6},"final_pose_error":0.01999,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.45184,-0.00496,0.02499],"final_tcp_position":[0.48137,0.03406,0.17419],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45543,-9e-05,0.025]},"peak_contact_force":36.62028,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":480.0,"n_steps_budget":1000.0,"object_pos_end":[0.45543,-9e-05,0.02499],"object_pos_start":[0.45543,-9e-05,0.025],"object_to_goal_dist_end":0.1564,"object_to_goal_dist_start":0.1564,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1920.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_above_object","tcp_end":[0.50205,0.06683,0.1343],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.13638,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":536.0,"n_steps_budget":1000.0,"object_pos_end":[0.45543,-9e-05,0.02499],"object_pos_start":[0.45543,-9e-05,0.02499],"object_to_goal_dist_end":0.1564,"object_to_goal_dist_start":0.1564,"object_z_max":0.02499,"peak_contact_force":14.12618,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2144.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_contact","tcp_end":[0.48456,0.03613,0.03992],"tcp_start":[0.50205,0.06683,0.1343],"tcp_to_object_dist_end":0.04882,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":11.0,"n_steps_budget":1000.0,"object_pos_end":[0.45472,-0.00119,0.02493],"object_pos_start":[0.45543,-9e-05,0.02499],"object_to_goal_dist_end":0.15555,"object_to_goal_dist_start":0.1564,"object_z_max":0.02508,"peak_contact_force":0.00075,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":30.0,"raw_peak_contact_force":36.62028,"subtask_id":"reach_goal","tcp_end":[0.48409,0.03429,0.03884],"tcp_start":[0.48456,0.03613,0.03992],"tcp_to_object_dist_end":0.04811,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":426.0,"n_steps_budget":1000.0,"object_pos_end":[0.45184,-0.00496,0.02499],"object_pos_start":[0.45472,-0.00119,0.02493],"object_to_goal_dist_end":0.15283,"object_to_goal_dist_start":0.15555,"object_z_max":0.02523,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1648.0,"raw_peak_contact_force":14.03813,"tcp_end":[0.48137,0.03406,0.17419],"tcp_start":[0.48409,0.03429,0.03884],"tcp_to_object_dist_end":0.15702,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```