## Search State

- **Seed**: 9
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → descend → push → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | impedance_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 9 | 0.1608 | 0.62 | ❌ rejected |
| 1 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.2930 | 0.72 | ✅ accepted |
| 0 | rotate → pull → push → descend → descend → grasp | arc_cartesian | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | impedance_control | impedance_control | position_control | admittance_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | contact_detected | grasp_success | 5 | -0.3700 | 0.00 | ✅ accepted |

**Proposal policy**: task_score is 0.62 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.2
- id: push_to_goal
  target_entity: object
  metric: goal_progress
  weight: 0.8
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: push_box
    offset:
    - 0.0
    - 0.1
    - 0.1
    tolerance: 0.02
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_lateral:
      type: scalar
      range:
      - -0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset.y
        mode: add
- id: descend_contact
  type: descend
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    entity: push_box
    offset:
    - 0.0
    - 0.1
    - 0.025
    tolerance: 0.005
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 1.0
      - 10.0
      default: 3.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    descend_approach_y:
      type: scalar
      range:
      - -0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset.y
        mode: replace
- id: push_forward
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: push_box
    offset:
    - 0.0
    - 0.1
    - 0.025
    offset_along_axis:
      distance: 0.15
      axis: task_goal_direction
      mode: replace_offset_projection
      sign: positive
    tolerance: 0.02
  parameters:
    push_speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
    push_stroke:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.1, 0.1], tolerance=0.02
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - approach_lateral: status=consumed; consumers=target.offset.y (add)
- **descend_contact** (`descend`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.1, 0.025], tolerance=0.005
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - descend_approach_y: status=consumed; consumers=target.offset.y (replace)
- **push_forward** (`push`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.1, 0.025], offset_along_axis={axis=task_goal_direction, distance=0.15, mode=replace_offset_projection, sign=positive}, tolerance=0.02
  - parameter_bindings:
    - push_speed: status=consumed; consumers=generator.speed (replace)
    - push_stroke: status=consumed; consumers=target.offset_along_axis.distance (replace)

## Design Metrics

- **Composite score**: 0.161
- **task_score** (E): 0.620
- **fitness_score**: 0.449  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.222
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.510

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2256 |
| descend_contact | 0.67 | 1.00 | 0.1478 |
| push_forward | 1.00 | 1.00 | 0.1158 |
| push_final | 1.00 | 1.00 | 0.0618 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.513, 0.141, 0.133) | (0.518, -0.020, 0.025)→(0.518, -0.020, 0.025) | 0.139→0.139 | 1.00 / 4.667 | 50595.773 | 0.245 |
| descend_contact | descend | 0.67 / force_exceeded | (0.513, 0.141, 0.133)→(0.513, 0.019, 0.052) | (0.518, -0.020, 0.025)→(0.518, -0.020, 0.025) | 0.139→0.139 | 1.00 / 3.000 | 39.916 | 72.063 |
| push_forward | push | 1.00 / time_limit | (0.513, 0.019, 0.052)→(0.502, -0.083, 0.049) | (0.518, -0.020, 0.025)→(0.511, -0.060, 0.031) | 0.139→0.093 | 1.00 / 3.667 | 0.469 | 75.219 |
| push_final | push | 1.00 / step_budget | (0.502, -0.083, 0.049)→(0.496, -0.143, 0.041) | (0.511, -0.060, 0.031)→(0.508, -0.100, 0.025) | 0.093→0.053 | 1.00 / 4.000 | 0.245 | 0.245 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.670
- lateral_force_integral: None
- approach_alignment: 0.715
- goal_progress: 0.639
- terminal_score: 0.639
- phase_score: 0.416
- phase_breakdown.reach_object_score: 0.000
- phase_breakdown.push_to_goal_score: 0.520

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.505
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.639
- **Median Q (composite search score)**: 0.301
- **K-run variance**: 0.0476
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.297


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.6391,"average_solve_count":133.0,"average_success_count":133.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.11386,"approach_1.approach_lateral":0.05859,"descend_contact.contact_force_threshold":5.74144,"descend_contact.descend_approach_y":0.02592,"push_final.final_push_speed":0.11579,"push_final.final_push_z":0.01866,"push_forward.push_speed":0.02001,"push_forward.push_stroke":0.23044,"push_forward.push_time":4.15697},"optimized_scores":{"best_composite_score":0.30113,"best_fitness_score":0.47779,"best_task_score":0.595},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":335.0,"contact_point_centroid":[0.51853,-0.08081,0.04868],"force_p95":108.79538,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":117.2358,"mean_force":77.61821,"phase_index":3.0,"phase_name":"push_final","phase_type":"push","tcp_position_centroid":[0.50979,-0.08701,0.05088]},{"body_a":"world","body_b":"push_box","contact_count":805.0,"contact_point_centroid":[0.53483,-0.08255,-0.0004],"force_p95":92.38906,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":94.87059,"mean_force":32.83195,"phase_index":3.0,"phase_name":"push_final","phase_type":"push","tcp_position_centroid":[0.50738,-0.09607,0.04867]},{"body_a":"attachment","body_b":"push_box","contact_count":1000.0,"contact_point_centroid":[0.53616,-0.02379,0.04889],"force_p95":76.58658,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":77.62495,"mean_force":69.56111,"phase_index":2.0,"phase_name":"push_forward","phase_type":"push","tcp_position_centroid":[0.52593,-0.02153,0.05232]},{"body_a":"world","body_b":"push_box","contact_count":3793.0,"contact_point_centroid":[0.53884,-0.03928,-0.00023],"force_p95":44.44939,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":63.27689,"mean_force":18.6505,"phase_index":2.0,"phase_name":"push_forward","phase_type":"push","tcp_position_centroid":[0.52633,-0.02049,0.05231]},{"body_a":"world","body_b":"push_box","contact_count":1624.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5175,0.0579,0.22531]},{"body_a":"world","body_b":"push_box","contact_count":3584.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.53678,0.06424,0.09921]}],"total_contact_groups":6},"final_pose_error":0.00993,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52825,-0.10456,0.02465],"final_tcp_position":[0.49712,-0.14145,0.0395],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":75893.53664,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":406.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":75893.53664,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3584.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.53702,0.11838,0.15025],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.19098,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":896.0,"n_steps_budget":990.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.02499,"peak_contact_force":77.2287,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4793.0,"raw_peak_contact_force":77.62495,"tcp_end":[0.53962,0.00934,0.05217],"tcp_start":[0.53702,0.11838,0.15025],"tcp_to_object_dist_end":0.04451,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53578,-0.04924,0.02469],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.10692,"object_to_goal_dist_start":0.13211,"object_z_max":0.02512,"peak_contact_force":0.31245,"phase_name":"push_forward","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1140.0,"raw_peak_contact_force":117.2358,"tcp_end":[0.51203,-0.05602,0.05266],"tcp_start":[0.53962,0.00934,0.05217],"tcp_to_object_dist_end":0.03731,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":427.0,"n_steps_budget":600.0,"object_pos_end":[0.52825,-0.10456,0.02465],"object_pos_start":[0.53578,-0.04924,0.02469],"object_to_goal_dist_end":0.05351,"object_to_goal_dist_start":0.10692,"object_z_max":0.03514,"peak_contact_force":0.24525,"phase_name":"push_final","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1624.0,"raw_peak_contact_force":0.24534,"subtask_id":"push_to_goal","tcp_end":[0.49712,-0.14145,0.0395],"tcp_start":[0.51203,-0.05602,0.05266],"tcp_to_object_dist_end":0.05051,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.6791,"average_solve_count":134.0,"average_success_count":134.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.07518,"approach_1.approach_lateral":0.06111,"descend_contact.contact_force_threshold":5.86803,"descend_contact.descend_approach_y":-0.00577,"push_final.final_push_speed":0.04517,"push_final.final_push_z":0.01078,"push_forward.push_speed":0.19258,"push_forward.push_stroke":0.08016,"push_forward.push_time":2.14648},"optimized_scores":{"best_composite_score":0.32853,"best_fitness_score":0.50519,"best_task_score":0.63915},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":376.0,"contact_point_centroid":[0.52055,-0.07574,-0.00027],"force_p95":64.49127,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":106.78359,"mean_force":23.06033,"phase_index":3.0,"phase_name":"push_final","phase_type":"push","tcp_position_centroid":[0.48921,-0.11214,0.0409]},{"body_a":"attachment","body_b":"push_box","contact_count":206.0,"contact_point_centroid":[0.49459,-0.09906,0.03912],"force_p95":77.23374,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":106.27691,"mean_force":20.51567,"phase_index":3.0,"phase_name":"push_final","phase_type":"push","tcp_position_centroid":[0.48819,-0.10733,0.04208]},{"body_a":"attachment","body_b":"push_box","contact_count":542.0,"contact_point_centroid":[0.53122,-0.04548,0.04906],"force_p95":99.82626,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":102.18055,"mean_force":74.92681,"phase_index":2.0,"phase_name":"push_forward","phase_type":"push","tcp_position_centroid":[0.52028,-0.04667,0.05291]},{"body_a":"world","body_b":"push_box","contact_count":1077.0,"contact_point_centroid":[0.5247,-0.04991,-0.00035],"force_p95":90.5144,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":96.23983,"mean_force":38.25335,"phase_index":2.0,"phase_name":"push_forward","phase_type":"push","tcp_position_centroid":[0.52318,-0.04367,0.0529]},{"body_a":"push_box","body_b":"link7","contact_count":218.0,"contact_point_centroid":[0.52705,-0.09347,0.0684],"force_p95":31.20625,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":32.47942,"mean_force":19.20483,"phase_index":3.0,"phase_name":"push_final","phase_type":"push","tcp_position_centroid":[0.49,-0.11632,0.03981]},{"body_a":"world","body_b":"push_box","contact_count":1832.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52214,0.05551,0.20717]},{"body_a":"world","body_b":"push_box","contact_count":3508.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.54613,0.04843,0.08124]}],"total_contact_groups":7},"final_pose_error":0.00996,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50495,-0.10436,0.02652],"final_tcp_position":[0.49453,-0.14239,0.03241],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55472,-0.03508,0.025]},"peak_contact_force":75893.53664,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":458.0,"n_steps_budget":1000.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.025],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.025,"peak_contact_force":75893.53664,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3508.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.54648,0.11345,0.11336],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.17303,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":877.0,"n_steps_budget":1000.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.02499,"peak_contact_force":42.02948,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1619.0,"raw_peak_contact_force":102.18055,"tcp_end":[0.54926,-0.01747,0.05378],"tcp_start":[0.54648,0.11345,0.11336],"tcp_to_object_dist_end":0.03418,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.51364,-0.05571,0.03363],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.09566,"object_to_goal_dist_start":0.12728,"object_z_max":0.03359,"peak_contact_force":0.84957,"phase_name":"push_forward","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":800.0,"raw_peak_contact_force":106.78359,"tcp_end":[0.48559,-0.08353,0.04963],"tcp_start":[0.54926,-0.01747,0.05378],"tcp_to_object_dist_end":0.04262,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":327.0,"n_steps_budget":960.0,"object_pos_end":[0.50495,-0.10436,0.02652],"object_pos_start":[0.51364,-0.05571,0.03363],"object_to_goal_dist_end":0.04593,"object_to_goal_dist_start":0.09566,"object_z_max":0.03856,"peak_contact_force":0.24525,"phase_name":"push_final","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1832.0,"raw_peak_contact_force":0.24534,"subtask_id":"push_to_goal","tcp_end":[0.49453,-0.14239,0.03241],"tcp_start":[0.48559,-0.08353,0.04963],"tcp_to_object_dist_end":0.03987,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.78621,"average_solve_count":145.0,"average_success_count":145.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.10025,"approach_1.approach_lateral":0.10991,"descend_contact.contact_force_threshold":7.59771,"descend_contact.descend_approach_y":0.06066,"push_final.final_push_speed":0.08608,"push_final.final_push_z":0.03397,"push_forward.push_speed":0.11608,"push_forward.push_stroke":0.29588,"push_forward.push_time":4.33378},"optimized_scores":{"best_composite_score":-0.1474,"best_fitness_score":0.3626,"best_task_score":0.62467},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1953.0,"contact_point_centroid":[0.45912,-0.04118,-7e-05],"force_p95":32.41994,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":36.382,"mean_force":6.837,"phase_index":2.0,"phase_name":"push_forward","phase_type":"push","tcp_position_centroid":[0.47288,-0.00519,0.04594]},{"body_a":"attachment","body_b":"push_box","contact_count":659.0,"contact_point_centroid":[0.47851,-0.04044,0.04837],"force_p95":34.54922,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":35.22556,"mean_force":18.96947,"phase_index":2.0,"phase_name":"push_forward","phase_type":"push","tcp_position_centroid":[0.48306,-0.03401,0.04598]},{"body_a":"world","body_b":"push_box","contact_count":662.0,"contact_point_centroid":[0.48974,-0.08482,-5e-05],"force_p95":0.82466,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.63816,"mean_force":0.37766,"phase_index":3.0,"phase_name":"push_final","phase_type":"push","tcp_position_centroid":[0.50005,-0.13099,0.04794]},{"body_a":"attachment","body_b":"push_box","contact_count":39.0,"contact_point_centroid":[0.49436,-0.11725,0.04897],"force_p95":1.28999,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.60598,"mean_force":0.68559,"phase_index":3.0,"phase_name":"push_final","phase_type":"push","tcp_position_centroid":[0.50063,-0.12692,0.04623]},{"body_a":"world","body_b":"push_box","contact_count":2152.0,"contact_point_centroid":[0.45543,-9e-05,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47765,0.09505,0.21654]},{"body_a":"world","body_b":"push_box","contact_count":3728.0,"contact_point_centroid":[0.45543,-9e-05,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.45254,0.12897,0.09019]}],"total_contact_groups":6},"final_pose_error":0.00995,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49142,-0.09193,0.02499],"final_tcp_position":[0.49706,-0.14369,0.05185],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45543,-9e-05,0.025]},"peak_contact_force":36.382,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":538.0,"n_steps_budget":1000.0,"object_pos_end":[0.45543,-9e-05,0.02499],"object_pos_start":[0.45543,-9e-05,0.025],"object_to_goal_dist_end":0.1564,"object_to_goal_dist_start":0.1564,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3728.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.4563,0.19215,0.13442],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.2212,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":932.0,"n_steps_budget":990.0,"object_pos_end":[0.45543,-9e-05,0.02499],"object_pos_start":[0.45543,-9e-05,0.02499],"object_to_goal_dist_end":0.1564,"object_to_goal_dist_start":0.1564,"object_z_max":0.02499,"peak_contact_force":0.48971,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2612.0,"raw_peak_contact_force":36.382,"tcp_end":[0.45161,0.06545,0.04929],"tcp_start":[0.4563,0.19215,0.13442],"tcp_to_object_dist_end":0.07,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48255,-0.07601,0.03532],"object_pos_start":[0.45543,-9e-05,0.02499],"object_to_goal_dist_end":0.07672,"object_to_goal_dist_start":0.1564,"object_z_max":0.03533,"peak_contact_force":0.24525,"phase_name":"push_forward","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":701.0,"raw_peak_contact_force":1.63816,"tcp_end":[0.50759,-0.11035,0.04472],"tcp_start":[0.45161,0.06545,0.04929],"tcp_to_object_dist_end":0.04353,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":256.0,"n_steps_budget":600.0,"object_pos_end":[0.49142,-0.09193,0.02499],"object_pos_start":[0.48255,-0.07601,0.03532],"object_to_goal_dist_end":0.0587,"object_to_goal_dist_start":0.07672,"object_z_max":0.03532,"peak_contact_force":0.24525,"phase_name":"push_final","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2152.0,"raw_peak_contact_force":0.24534,"subtask_id":"push_to_goal","tcp_end":[0.49706,-0.14369,0.05185],"tcp_start":[0.50759,-0.11035,0.04472],"tcp_to_object_dist_end":0.05859,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```