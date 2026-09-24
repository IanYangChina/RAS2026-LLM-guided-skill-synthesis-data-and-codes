## Search State

- **Seed**: 5
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → contact → push → retract | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4729 | 0.75 | ❌ rejected |
| 9 | approach → contact → push → retract | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.1492 | 0.31 | ❌ rejected |
| 8 | approach → contact → push → retract | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4711 | 0.75 | ❌ rejected |
| 7 | approach → contact → push → retract | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4632 | 0.73 | ❌ rejected |
| 6 | approach → contact → push → retract | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.1477 | 0.00 | ❌ rejected |

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

## Current Skill (Q=0.473) — your mutation base

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

- **Composite score**: 0.473
- **task_score** (E): 0.752
- **fitness_score**: 0.683  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.210

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2855 |
| contact_1 | 1.00 | 1.00 | 0.0538 |
| push_1 | 1.00 | 1.00 | 0.1257 |
| retract_1 | 0.00 | 1.00 | 0.1658 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.514, 0.101, 0.036) | (0.519, 0.022, 0.025)→(0.519, 0.022, 0.025) | 0.173→0.173 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / step_budget | (0.514, 0.101, 0.036)→(0.514, 0.049, 0.020) | (0.519, 0.022, 0.025)→(0.521, 0.013, 0.025) | 0.173→0.164 | 1.00 / 2.667 | 2.174 | 9.022 |
| push_1 | push | 1.00 / step_budget | (0.514, 0.049, 0.020)→(0.501, -0.075, 0.024) | (0.521, 0.013, 0.025)→(0.512, -0.110, 0.028) | 0.164→0.047 | 1.00 / 3.000 | 49.254 | 93.463 |
| retract_1 | retract | 0.00 / step_budget | (0.501, -0.075, 0.024)→(0.496, 0.071, 0.102) | (0.512, -0.110, 0.028)→(0.509, -0.108, 0.025) | 0.047→0.047 | 1.00 / 4.000 | 0.245 | 45.561 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.425
- goal_progress: 0.955
- terminal_score: 0.955
- phase_score: 0.843
- phase_breakdown.approach_score: 0.820
- phase_breakdown.push_score: 0.836
- phase_breakdown.contact_score: 0.870

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.888
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.955
- **Median Q (composite search score)**: 0.380
- **K-run variance**: 0.0211
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.285


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.73125,"average_solve_count":160.0,"average_success_count":160.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.speed":0.03715,"push_1.push_depth":0.09972,"retract_1.retract_height":0.06207},"optimized_scores":{"best_composite_score":0.36123,"best_fitness_score":0.57123,"best_task_score":0.6232},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":796.0,"contact_point_centroid":[0.54964,-0.01174,0.05468],"force_p95":114.83434,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":133.63294,"mean_force":75.59887,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51801,0.00399,0.02357]},{"body_a":"attachment","body_b":"push_box","contact_count":799.0,"contact_point_centroid":[0.53672,-0.00456,0.0521],"force_p95":100.81493,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":106.81499,"mean_force":55.21315,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51808,0.00424,0.02356]},{"body_a":"world","body_b":"push_box","contact_count":1511.0,"contact_point_centroid":[0.54416,-0.04782,-0.00031],"force_p95":78.22015,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":95.46153,"mean_force":51.47705,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51765,0.00175,0.02384]},{"body_a":"push_box","body_b":"link7","contact_count":44.0,"contact_point_centroid":[0.5493,-0.06182,0.05578],"force_p95":79.2895,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":93.48183,"mean_force":37.99057,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50682,-0.05214,0.03027]},{"body_a":"world","body_b":"push_box","contact_count":3694.0,"contact_point_centroid":[0.52547,-0.08266,-3e-05],"force_p95":0.24784,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":81.23783,"mean_force":0.487,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.501,0.0238,0.07098]},{"body_a":"attachment","body_b":"push_box","contact_count":61.0,"contact_point_centroid":[0.52865,-0.05516,0.05943],"force_p95":60.57067,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":79.54073,"mean_force":22.07354,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50612,-0.04923,0.03119]},{"body_a":"attachment","body_b":"push_box","contact_count":162.0,"contact_point_centroid":[0.53792,0.0574,0.03815],"force_p95":6.73281,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.60136,"mean_force":2.77549,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53127,0.06934,0.02116]},{"body_a":"world","body_b":"push_box","contact_count":2906.0,"contact_point_centroid":[0.53689,0.03479,-1e-05],"force_p95":1.78946,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.39139,"mean_force":0.40773,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52894,0.09108,0.02608]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51292,0.07216,0.17685]}],"total_contact_groups":9},"final_pose_error":0.07253,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.5249,-0.08268,0.02499],"final_tcp_position":[0.49874,0.08964,0.1098],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":133.63294,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.53035,0.11538,0.03637],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07949,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":823.0,"n_steps_budget":930.0,"object_pos_end":[0.53929,0.02761,0.02502],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.1819,"object_to_goal_dist_start":0.1905,"object_z_max":0.02512,"peak_contact_force":1.02004,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3068.0,"raw_peak_contact_force":8.60136,"tcp_end":[0.53188,0.06442,0.02013],"tcp_start":[0.53035,0.11538,0.03637],"tcp_to_object_dist_end":0.03787,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":806.0,"n_steps_budget":900.0,"object_pos_end":[0.53347,-0.08437,0.03134],"object_pos_start":[0.53929,0.02761,0.02502],"object_to_goal_dist_end":0.07394,"object_to_goal_dist_start":0.1819,"object_z_max":0.03138,"peak_contact_force":112.48685,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3106.0,"raw_peak_contact_force":133.63294,"tcp_end":[0.50775,-0.0554,0.02907],"tcp_start":[0.53188,0.06442,0.02013],"tcp_to_object_dist_end":0.03881,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5249,-0.08268,0.02499],"object_pos_start":[0.53347,-0.08437,0.03134],"object_to_goal_dist_end":0.07178,"object_to_goal_dist_start":0.07394,"object_z_max":0.03478,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3799.0,"raw_peak_contact_force":93.48183,"tcp_end":[0.49874,0.08964,0.1098],"tcp_start":[0.50775,-0.0554,0.02907],"tcp_to_object_dist_end":0.19383,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.72258,"average_solve_count":155.0,"average_success_count":155.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.speed":0.03868,"push_1.push_depth":0.09888,"retract_1.retract_height":0.05253},"optimized_scores":{"best_composite_score":0.67797,"best_fitness_score":0.88797,"best_task_score":0.95516},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1076.0,"contact_point_centroid":[0.51022,-0.10869,-0.00012],"force_p95":58.04179,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":68.4053,"mean_force":24.5425,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49828,-0.05167,0.02003]},{"body_a":"push_box","body_b":"link7","contact_count":536.0,"contact_point_centroid":[0.52489,-0.0543,0.05271],"force_p95":45.5499,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":54.16616,"mean_force":31.93879,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49895,-0.03382,0.02015]},{"body_a":"attachment","body_b":"push_box","contact_count":738.0,"contact_point_centroid":[0.51307,-0.0626,0.04588],"force_p95":45.48946,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":53.12643,"mean_force":23.51695,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49824,-0.05136,0.01999]},{"body_a":"push_box","body_b":"link7","contact_count":26.0,"contact_point_centroid":[0.52515,-0.13866,0.0501],"force_p95":7.61421,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.89701,"mean_force":4.26536,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49383,-0.11309,0.02036]},{"body_a":"world","body_b":"push_box","contact_count":3898.0,"contact_point_centroid":[0.50086,-0.15543,-2e-05],"force_p95":0.24723,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.56896,"mean_force":0.28085,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49325,-0.0401,0.05323]},{"body_a":"attachment","body_b":"push_box","contact_count":147.0,"contact_point_centroid":[0.5067,0.00186,0.03528],"force_p95":7.44943,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.43239,"mean_force":3.28261,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49974,0.01373,0.02131]},{"body_a":"world","body_b":"push_box","contact_count":2965.0,"contact_point_centroid":[0.50465,-0.02057,-1e-05],"force_p95":1.67818,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.1286,"mean_force":0.41279,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49816,0.03696,0.02523]},{"body_a":"world","body_b":"push_box","contact_count":3580.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4992,0.04658,0.17199]},{"body_a":"attachment","body_b":"push_box","contact_count":2.0,"contact_point_centroid":[0.51025,-0.13092,0.05021],"force_p95":0.02991,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.03149,"mean_force":0.01574,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49585,-0.11904,0.01979]}],"total_contact_groups":9},"final_pose_error":0.13281,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50094,-0.15581,0.02499],"final_tcp_position":[0.49449,0.03247,0.08839],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":68.4053,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":895.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3580.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.50029,0.06252,0.03384],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08192,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":823.0,"n_steps_budget":930.0,"object_pos_end":[0.50643,-0.0276,0.02507],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.12257,"object_to_goal_dist_start":0.13127,"object_z_max":0.02514,"peak_contact_force":4.82094,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3112.0,"raw_peak_contact_force":9.43239,"tcp_end":[0.50013,0.00923,0.02063],"tcp_start":[0.50029,0.06252,0.03384],"tcp_to_object_dist_end":0.03762,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":780.0,"n_steps_budget":870.0,"object_pos_end":[0.50051,-0.15592,0.02519],"object_pos_start":[0.50643,-0.0276,0.02507],"object_to_goal_dist_end":0.00595,"object_to_goal_dist_start":0.12257,"object_z_max":0.02794,"peak_contact_force":0.14259,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2350.0,"raw_peak_contact_force":68.4053,"tcp_end":[0.49587,-0.11899,0.0198],"tcp_start":[0.50013,0.00923,0.02063],"tcp_to_object_dist_end":0.03761,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50094,-0.15581,0.02499],"object_pos_start":[0.50051,-0.15592,0.02519],"object_to_goal_dist_end":0.00589,"object_to_goal_dist_start":0.00595,"object_z_max":0.02651,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3926.0,"raw_peak_contact_force":17.89701,"tcp_end":[0.49449,0.03247,0.08839],"tcp_start":[0.49587,-0.11899,0.0198],"tcp_to_object_dist_end":0.19878,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.7205,"average_solve_count":161.0,"average_success_count":161.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.speed":0.03456,"push_1.push_depth":0.09862,"retract_1.retract_height":0.17779},"optimized_scores":{"best_composite_score":0.37961,"best_fitness_score":0.58961,"best_task_score":0.67903},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1294.0,"contact_point_centroid":[0.5212,-0.04327,-0.00015],"force_p95":58.32205,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":78.35009,"mean_force":32.31149,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50452,0.01214,0.02132]},{"body_a":"push_box","body_b":"link7","contact_count":764.0,"contact_point_centroid":[0.53081,-0.00706,0.05394],"force_p95":55.22133,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":65.40225,"mean_force":38.39637,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50445,0.01215,0.02125]},{"body_a":"attachment","body_b":"push_box","contact_count":769.0,"contact_point_centroid":[0.52175,0.00216,0.0493],"force_p95":55.35004,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":59.35934,"mean_force":36.2399,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50449,0.01256,0.02124]},{"body_a":"push_box","body_b":"link7","contact_count":7.0,"contact_point_centroid":[0.52377,-0.07607,0.05454],"force_p95":25.2232,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":25.30474,"mean_force":14.04433,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49845,-0.05086,0.02184]},{"body_a":"attachment","body_b":"push_box","contact_count":28.0,"contact_point_centroid":[0.51647,-0.05925,0.05272],"force_p95":18.74884,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.76519,"mean_force":3.23223,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49745,-0.04838,0.02241]},{"body_a":"world","body_b":"push_box","contact_count":3897.0,"contact_point_centroid":[0.50056,-0.08682,-2e-05],"force_p95":0.24565,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.60922,"mean_force":0.26563,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49535,0.02251,0.06407]},{"body_a":"attachment","body_b":"push_box","contact_count":179.0,"contact_point_centroid":[0.51679,0.06801,0.03626],"force_p95":7.91967,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.03374,"mean_force":3.20535,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.51002,0.07984,0.02157]},{"body_a":"world","body_b":"push_box","contact_count":3089.0,"contact_point_centroid":[0.51515,0.04551,-1e-05],"force_p95":2.05176,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.77511,"mean_force":0.4374,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50827,0.10093,0.02646]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50358,0.07681,0.17794]}],"total_contact_groups":9},"final_pose_error":0.07366,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50045,-0.08637,0.02499],"final_tcp_position":[0.49606,0.09016,0.10723],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":78.35009,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.51015,0.12542,0.03668],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07878,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":870.0,"n_steps_budget":990.0,"object_pos_end":[0.51682,0.03808,0.02514],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.18883,"object_to_goal_dist_start":0.19823,"object_z_max":0.02518,"peak_contact_force":0.68081,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3268.0,"raw_peak_contact_force":9.03374,"tcp_end":[0.51049,0.07485,0.02047],"tcp_start":[0.51015,0.12542,0.03668],"tcp_to_object_dist_end":0.0376,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":777.0,"n_steps_budget":870.0,"object_pos_end":[0.50236,-0.08928,0.02856],"object_pos_start":[0.51682,0.03808,0.02514],"object_to_goal_dist_end":0.06087,"object_to_goal_dist_start":0.18883,"object_z_max":0.02896,"peak_contact_force":35.13328,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2827.0,"raw_peak_contact_force":78.35009,"tcp_end":[0.4986,-0.05082,0.02186],"tcp_start":[0.51049,0.07485,0.02047],"tcp_to_object_dist_end":0.03922,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50045,-0.08637,0.02499],"object_pos_start":[0.50236,-0.08928,0.02856],"object_to_goal_dist_end":0.06363,"object_to_goal_dist_start":0.06087,"object_z_max":0.0286,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3932.0,"raw_peak_contact_force":25.30474,"tcp_end":[0.49606,0.09016,0.10723],"tcp_start":[0.4986,-0.05082,0.02186],"tcp_to_object_dist_end":0.1948,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```