## Search State

- **Seed**: 9
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → descend → push → push → retract | linear_cartesian | linear_cartesian | impedance_motion | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.3488 | 0.67 | ✅ accepted |
| 5 | approach → descend → push → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 5 | -0.0177 | 0.47 | ❌ rejected |
| 4 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 3 | -0.1632 | 0.00 | ❌ rejected |
| 3 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.0217 | 0.00 | ❌ rejected |
| 2 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.3449 | 0.62 | ✅ accepted |

**Proposal policy**: task_score is 0.67 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.349) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
subtasks:
- id: reach_contact
  anchor: object
  offset:
  - 0.0
  - 0.05
  - 0.0
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
    - 0.05
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current
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
    speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_contact
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.05
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  subtask_id: reach_contact
- id: contact_1
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    contact_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_contact
- id: push_1
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - -0.01
    - 0.0
  subtask_id: push_to_goal
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.05, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.05, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none
- **contact_1** (`push`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_speed: status=consumed; consumers=generator.speed (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, -0.01, 0.0]
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.349
- **task_score** (E): 0.674
- **fitness_score**: 0.639  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.290

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1302 |
| descend_1 | 1.00 | 1.00 | 0.1478 |
| contact_1 | 1.00 | 1.00 | 0.0318 |
| push_1 | 1.00 | 1.00 | 0.1366 |
| retract_1 | 1.00 | 1.00 | 0.0884 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.514, 0.027, 0.181) | (0.518, -0.020, 0.025)→(0.518, -0.020, 0.025) | 0.139→0.139 | 1.00 / 4.000 | 0.245 | 0.245 |
| descend_1 | descend | 1.00 / step_budget | (0.514, 0.027, 0.181)→(0.514, 0.029, 0.034) | (0.518, -0.020, 0.025)→(0.518, -0.020, 0.025) | 0.139→0.139 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | push | 1.00 / step_budget | (0.514, 0.029, 0.034)→(0.513, -0.001, 0.024) | (0.518, -0.020, 0.025)→(0.519, -0.038, 0.025) | 0.139→0.123 | 1.00 / 3.000 | 6.674 | 46.187 |
| push_1 | push | 1.00 / step_budget | (0.513, -0.001, 0.024)→(0.500, -0.131, 0.021) | (0.519, -0.038, 0.025)→(0.532, -0.149, 0.028) | 0.123→0.041 | 1.00 / 2.667 | 33.043 | 53.664 |
| retract_1 | retract | 1.00 / step_budget | (0.500, -0.131, 0.021)→(0.496, -0.131, 0.110) | (0.532, -0.149, 0.028)→(0.534, -0.149, 0.025) | 0.041→0.043 | 1.00 / 4.000 | 0.245 | 40.975 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.764
- goal_progress: 0.870
- terminal_score: 0.870
- phase_score: 0.767
- phase_breakdown.reach_contact_score: 0.541
- phase_breakdown.push_to_goal_score: 0.864

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.808
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.870
- **Median Q (composite search score)**: 0.378
- **K-run variance**: 0.0229
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.280


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.8853,"average_solve_count":279.0,"average_success_count":279.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.17063,"approach_1.speed":0.02726,"contact_1.contact_speed":0.03332,"push_1.push_speed":0.0296},"optimized_scores":{"best_composite_score":0.3777,"best_fitness_score":0.6677,"best_task_score":0.72259},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":262.0,"contact_point_centroid":[0.54776,-0.0994,0.05457],"force_p95":49.86703,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":65.50838,"mean_force":27.10906,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51346,-0.09091,0.02112]},{"body_a":"world","body_b":"push_box","contact_count":518.0,"contact_point_centroid":[0.55219,-0.12475,-0.0001],"force_p95":52.87674,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":59.15762,"mean_force":23.96811,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51684,-0.07902,0.02112]},{"body_a":"attachment","body_b":"push_box","contact_count":330.0,"contact_point_centroid":[0.53134,-0.08449,0.04902],"force_p95":50.6737,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":55.30465,"mean_force":21.91172,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51757,-0.07631,0.02107]},{"body_a":"push_box","body_b":"link7","contact_count":8.0,"contact_point_centroid":[0.54169,-0.13179,0.05513],"force_p95":32.17884,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":41.58951,"mean_force":8.04643,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50308,-0.13091,0.0226]},{"body_a":"world","body_b":"push_box","contact_count":1926.0,"contact_point_centroid":[0.53761,-0.15887,-2e-05],"force_p95":0.55438,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":38.95587,"mean_force":0.30091,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49991,-0.12984,0.07049]},{"body_a":"attachment","body_b":"push_box","contact_count":35.0,"contact_point_centroid":[0.54233,-0.00708,0.04135],"force_p95":36.15769,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":38.92776,"mean_force":5.41884,"phase_index":2.0,"phase_name":"contact_1","phase_type":"push","tcp_position_centroid":[0.53864,0.00452,0.02608]},{"body_a":"world","body_b":"push_box","contact_count":240.0,"contact_point_centroid":[0.54611,-0.02844,-3e-05],"force_p95":4.95844,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.6193,"mean_force":1.07029,"phase_index":2.0,"phase_name":"contact_1","phase_type":"push","tcp_position_centroid":[0.53866,0.01415,0.02903]},{"body_a":"attachment","body_b":"push_box","contact_count":50.0,"contact_point_centroid":[0.51936,-0.1325,0.05523],"force_p95":4.04245,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.2681,"mean_force":1.21044,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50109,-0.1304,0.02915]},{"body_a":"world","body_b":"push_box","contact_count":1720.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51705,0.01048,0.2507]},{"body_a":"world","body_b":"push_box","contact_count":2068.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53722,0.02271,0.11712]}],"total_contact_groups":10},"final_pose_error":0.01222,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53566,-0.15847,0.02499],"final_tcp_position":[0.50011,-0.12983,0.11079],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":65.50838,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":430.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1720.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_contact","tcp_end":[0.53689,0.02163,0.2015],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.18287,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":517.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2068.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_contact","tcp_end":[0.5397,0.02393,0.03352],"tcp_start":[0.53689,0.02163,0.2015],"tcp_to_object_dist_end":0.05046,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":89.0,"n_steps_budget":960.0,"object_pos_end":[0.54415,-0.04302,0.02459],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.11573,"object_to_goal_dist_start":0.13211,"object_z_max":0.02553,"peak_contact_force":16.0,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":275.0,"raw_peak_contact_force":38.92776,"subtask_id":"reach_contact","tcp_end":[0.53921,-0.00644,0.02356],"tcp_start":[0.5397,0.02393,0.03352],"tcp_to_object_dist_end":0.03693,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":385.0,"n_steps_budget":1000.0,"object_pos_end":[0.53717,-0.1559,0.02945],"object_pos_start":[0.54415,-0.04302,0.02459],"object_to_goal_dist_end":0.0379,"object_to_goal_dist_start":0.11573,"object_z_max":0.02966,"peak_contact_force":47.29007,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1110.0,"raw_peak_contact_force":65.50838,"subtask_id":"push_to_goal","tcp_end":[0.50349,-0.13057,0.02251],"tcp_start":[0.53921,-0.00644,0.02356],"tcp_to_object_dist_end":0.04271,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":544.0,"n_steps_budget":630.0,"object_pos_end":[0.53566,-0.15847,0.02499],"object_pos_start":[0.53717,-0.1559,0.02945],"object_to_goal_dist_end":0.03665,"object_to_goal_dist_start":0.0379,"object_z_max":0.02987,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1984.0,"raw_peak_contact_force":41.58951,"tcp_end":[0.50011,-0.12983,0.11079],"tcp_start":[0.50349,-0.13057,0.02251],"tcp_to_object_dist_end":0.09719,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.18182,"average_solve_count":209.0,"average_success_count":209.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.11981,"approach_1.speed":0.04208,"contact_1.contact_speed":0.02206,"push_1.push_speed":0.0884},"optimized_scores":{"best_composite_score":0.15047,"best_fitness_score":0.44047,"best_task_score":0.42956},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":7.0,"contact_point_centroid":[0.53821,-0.11499,0.05485],"force_p95":60.66007,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":79.83855,"mean_force":14.37666,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50377,-0.13129,0.02145]},{"body_a":"world","body_b":"push_box","contact_count":2050.0,"contact_point_centroid":[0.56451,-0.11798,-4e-05],"force_p95":0.3224,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":63.99614,"mean_force":0.32294,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50056,-0.13016,0.067]},{"body_a":"push_box","body_b":"link7","contact_count":83.0,"contact_point_centroid":[0.5503,-0.0965,0.05298],"force_p95":51.5396,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":52.80982,"mean_force":34.72612,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51361,-0.10371,0.02015]},{"body_a":"world","body_b":"push_box","contact_count":494.0,"contact_point_centroid":[0.55845,-0.1112,-0.00012],"force_p95":31.38196,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":40.79099,"mean_force":8.44643,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52156,-0.08204,0.01973]},{"body_a":"attachment","body_b":"push_box","contact_count":145.0,"contact_point_centroid":[0.53903,-0.08187,0.04942],"force_p95":27.2711,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":39.02083,"mean_force":8.70936,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52532,-0.07278,0.02002]},{"body_a":"attachment","body_b":"push_box","contact_count":39.0,"contact_point_centroid":[0.55229,-0.01848,0.0405],"force_p95":35.14447,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":38.88578,"mean_force":4.91122,"phase_index":2.0,"phase_name":"contact_1","phase_type":"push","tcp_position_centroid":[0.54869,-0.00685,0.02533]},{"body_a":"attachment","body_b":"push_box","contact_count":6.0,"contact_point_centroid":[0.52186,-0.13435,0.04775],"force_p95":17.96254,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.85342,"mean_force":4.10231,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50373,-0.13132,0.02147]},{"body_a":"world","body_b":"push_box","contact_count":247.0,"contact_point_centroid":[0.55567,-0.03809,-1e-05],"force_p95":6.44384,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.68658,"mean_force":1.05169,"phase_index":2.0,"phase_name":"contact_1","phase_type":"push","tcp_position_centroid":[0.54853,0.00611,0.02917]},{"body_a":"world","body_b":"push_box","contact_count":2356.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52234,0.00668,0.22535]},{"body_a":"world","body_b":"push_box","contact_count":1448.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.54735,0.01405,0.09214]}],"total_contact_groups":10},"final_pose_error":0.01224,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.5649,-0.11745,0.02499],"final_tcp_position":[0.50071,-0.13012,0.10957],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55472,-0.03508,0.025]},"peak_contact_force":79.83855,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":589.0,"n_steps_budget":1000.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.025],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2356.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_contact","tcp_end":[0.54732,0.01363,0.15121],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.1355,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":362.0,"n_steps_budget":810.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1448.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_contact","tcp_end":[0.54971,0.01457,0.03356],"tcp_start":[0.54732,0.01363,0.15121],"tcp_to_object_dist_end":0.05063,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":96.0,"n_steps_budget":1000.0,"object_pos_end":[0.55704,-0.0529,0.02485],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.11262,"object_to_goal_dist_start":0.12728,"object_z_max":0.02544,"peak_contact_force":2.0,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":286.0,"raw_peak_contact_force":38.88578,"subtask_id":"reach_contact","tcp_end":[0.54925,-0.01624,0.02319],"tcp_start":[0.54971,0.01457,0.03356],"tcp_to_object_dist_end":0.03751,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":303.0,"n_steps_budget":1000.0,"object_pos_end":[0.56035,-0.12336,0.03047],"object_pos_start":[0.55704,-0.0529,0.02485],"object_to_goal_dist_end":0.06619,"object_to_goal_dist_start":0.11262,"object_z_max":0.03041,"peak_contact_force":51.67938,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":722.0,"raw_peak_contact_force":52.80982,"subtask_id":"push_to_goal","tcp_end":[0.50412,-0.13086,0.02131],"tcp_start":[0.54925,-0.01624,0.02319],"tcp_to_object_dist_end":0.05746,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.5649,-0.11745,0.02499],"object_pos_start":[0.56035,-0.12336,0.03047],"object_to_goal_dist_end":0.07261,"object_to_goal_dist_start":0.06619,"object_z_max":0.0309,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2063.0,"raw_peak_contact_force":79.83855,"tcp_end":[0.50071,-0.13012,0.10957],"tcp_start":[0.50412,-0.13086,0.02131],"tcp_to_object_dist_end":0.10693,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.315,"average_solve_count":200.0,"average_success_count":200.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.15867,"approach_1.speed":0.06794,"contact_1.contact_speed":0.03507,"push_1.push_speed":0.04896},"optimized_scores":{"best_composite_score":0.51809,"best_fitness_score":0.80809,"best_task_score":0.86989},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":35.0,"contact_point_centroid":[0.45341,0.01745,0.03732],"force_p95":47.01611,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":60.74836,"mean_force":8.69005,"phase_index":2.0,"phase_name":"contact_1","phase_type":"push","tcp_position_centroid":[0.4511,0.02912,0.02763]},{"body_a":"attachment","body_b":"push_box","contact_count":355.0,"contact_point_centroid":[0.47462,-0.07144,0.03509],"force_p95":29.12902,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":42.67254,"mean_force":4.33389,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4712,-0.05964,0.02138]},{"body_a":"world","body_b":"push_box","contact_count":225.0,"contact_point_centroid":[0.45601,-0.0026,-3e-05],"force_p95":10.0225,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":25.41979,"mean_force":1.61443,"phase_index":2.0,"phase_name":"contact_1","phase_type":"push","tcp_position_centroid":[0.45112,0.04,0.03057]},{"body_a":"world","body_b":"push_box","contact_count":469.0,"contact_point_centroid":[0.47736,-0.10323,-6e-05],"force_p95":16.05626,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.55401,"mean_force":3.76772,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46952,-0.05333,0.0216]},{"body_a":"world","body_b":"push_box","contact_count":2140.0,"contact_point_centroid":[0.50017,-0.17069,-1e-05],"force_p95":0.24538,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.49585,"mean_force":0.25116,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48856,-0.13189,0.06452]},{"body_a":"attachment","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.49487,-0.14466,0.03034],"force_p95":0.88645,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.89044,"mean_force":0.58033,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49193,-0.13277,0.02033]},{"body_a":"world","body_b":"push_box","contact_count":1640.0,"contact_point_centroid":[0.45543,-9e-05,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47864,0.02147,0.24611]},{"body_a":"world","body_b":"push_box","contact_count":2084.0,"contact_point_centroid":[0.45543,-9e-05,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45381,0.0467,0.11254]}],"total_contact_groups":8},"final_pose_error":0.01202,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50014,-0.17035,0.02499],"final_tcp_position":[0.48866,-0.13183,0.10884],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45543,-9e-05,0.025]},"peak_contact_force":60.74836,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":410.0,"n_steps_budget":1000.0,"object_pos_end":[0.45543,-9e-05,0.02499],"object_pos_start":[0.45543,-9e-05,0.025],"object_to_goal_dist_end":0.1564,"object_to_goal_dist_start":0.1564,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1640.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_contact","tcp_end":[0.45748,0.04452,0.19161],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.1725,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":521.0,"n_steps_budget":1000.0,"object_pos_end":[0.45543,-9e-05,0.02499],"object_pos_start":[0.45543,-9e-05,0.02499],"object_to_goal_dist_end":0.1564,"object_to_goal_dist_start":0.1564,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2084.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_contact","tcp_end":[0.45211,0.04909,0.03417],"tcp_start":[0.45748,0.04452,0.19161],"tcp_to_object_dist_end":0.05014,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":85.0,"n_steps_budget":900.0,"object_pos_end":[0.45716,-0.01709,0.02514],"object_pos_start":[0.45543,-9e-05,0.02499],"object_to_goal_dist_end":0.13964,"object_to_goal_dist_start":0.1564,"object_z_max":0.02547,"peak_contact_force":2.02298,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":260.0,"raw_peak_contact_force":60.74836,"subtask_id":"reach_contact","tcp_end":[0.45143,0.01944,0.02543],"tcp_start":[0.45211,0.04909,0.03417],"tcp_to_object_dist_end":0.03699,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":445.0,"n_steps_budget":1000.0,"object_pos_end":[0.49974,-0.16902,0.02543],"object_pos_start":[0.45716,-0.01709,0.02514],"object_to_goal_dist_end":0.01902,"object_to_goal_dist_start":0.13964,"object_z_max":0.02568,"peak_contact_force":0.15945,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":824.0,"raw_peak_contact_force":42.67254,"subtask_id":"push_to_goal","tcp_end":[0.49201,-0.1326,0.02035],"tcp_start":[0.45143,0.01944,0.02543],"tcp_to_object_dist_end":0.03757,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":545.0,"n_steps_budget":630.0,"object_pos_end":[0.50014,-0.17035,0.02499],"object_pos_start":[0.49974,-0.16902,0.02543],"object_to_goal_dist_end":0.02035,"object_to_goal_dist_start":0.01902,"object_z_max":0.02544,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2143.0,"raw_peak_contact_force":1.49585,"tcp_end":[0.48866,-0.13183,0.10884],"tcp_start":[0.49201,-0.1326,0.02035],"tcp_to_object_dist_end":0.09298,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```