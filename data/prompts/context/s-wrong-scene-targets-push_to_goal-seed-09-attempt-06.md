## Search State

- **Seed**: 9
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 5 | 0.1881 | 0.41 | ✅ accepted |
| 5 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 8 | -0.1901 | 0.00 | ❌ rejected |
| 4 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 7 | 0.0007 | 0.00 | ❌ rejected |
| 3 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 5 | 0.1783 | 0.40 | ✅ accepted |
| 2 | rotate → pull → push → descend → descend → grasp | arc_cartesian | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | impedance_control | impedance_control | position_control | admittance_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | contact_detected | grasp_success | 5 | -0.3700 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.41 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen object start: [0.5, -0.15, 0.025]
- Frozen task target: [0.5, 0.0, 0.3]
- Goal object position: (0.5, 0.0, 0.3)
- Object initial pose: (0.5, -0.15, 0.025)
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.8
- Force limit: 25.0 N
- Robot initial TCP position: (0.5444299044764102, -0.025581934909493356, 0.025)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **object displacement ratio toward goal_object_position**

## Scene Entities

robot:
  model: panda_pusher
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5444299044764102, -0.025581934909493356, 0.025]
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
  frozen_task_target: [0.5, 0.0, 0.3]
  frozen_object_starts: {'push_box': [0.5, -0.15, 0.025]}
  frozen_targets: {'task_goal': [0.5, 0.0, 0.3]}
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

## Current Skill (Q=0.188) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: approach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.3
- id: push_to_goal
  metric: goal_progress
  weight: 0.7
phases:
- id: approach
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
    - 0.0
    - 0.15
    offset_along_axis:
      distance: 0.0
      axis: task_goal_direction
      mode: replace_offset_projection
      sign: negative
    orientation:
      mode: none
  parameters:
    approach_offset_z:
      type: scalar
      range:
      - 0.08
      - 0.2
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_object
- id: descend
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: push_box
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: none
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
- id: push
  type: push
  generator: linear_cartesian
  control: admittance_control
  termination: time_limit
  target:
    source: yaml
    anchor: task_goal
    entity: goal_marker
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.2
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
    orientation:
      mode: none
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.2
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: push_to_goal
- id: retract
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: push_box
    offset:
    - 0.0
    - 0.0
    - 0.2
    orientation:
      mode: none

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach** (`approach`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.0, 0.15], offset_along_axis={axis=task_goal_direction, distance=0.0, mode=replace_offset_projection, sign=negative}
  - orientation: mode=none
  - parameter_bindings:
    - approach_offset_z: status=consumed; consumers=target.offset.z (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend** (`descend`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.0, 0.0]
  - orientation: mode=none
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **push** (`push`)
  - target: source=yaml, anchor=task_goal, entity=goal_marker, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.2, mode=add_to_offset, sign=positive}
  - orientation: mode=none
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.0]
- **retract** (`retract`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.0, 0.2]
  - orientation: mode=none
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.188
- **task_score** (E): 0.415
- **fitness_score**: 0.498  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.310

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach | 1.00 | 1.00 | 0.1317 |
| descend | 1.00 | 1.00 | 0.1317 |
| push | 1.00 | 1.00 | 0.2864 |
| retract | 0.00 | 1.00 | 0.1645 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.514, -0.018, 0.178) | (0.518, -0.020, 0.025)→(0.518, -0.020, 0.025) | 0.139→0.139 | 1.00 / 4.000 | 0.245 | 0.245 |
| descend | descend | 1.00 / step_budget | (0.514, -0.018, 0.178)→(0.528, -0.020, 0.047) | (0.518, -0.020, 0.025)→(0.522, -0.020, 0.024) | 0.139→0.139 | 1.00 / 5.000 | 252.559 | 277.380 |
| push | push | 1.00 / time_limit | (0.528, -0.020, 0.047)→(0.463, -0.284, 0.025) | (0.522, -0.020, 0.024)→(0.524, -0.075, 0.025) | 0.139→0.082 | 1.00 / 4.000 | 0.245 | 157.035 |
| retract | retract | 0.00 / step_budget | (0.463, -0.284, 0.025)→(0.493, -0.167, 0.131) | (0.524, -0.075, 0.025)→(0.524, -0.075, 0.025) | 0.082→0.082 | 1.00 / 4.000 | 0.245 | 0.245 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.478
- lateral_force_integral: None
- approach_alignment: 0.856
- goal_progress: 0.467
- terminal_score: 0.467
- phase_score: 0.575
- phase_breakdown.push_to_goal_score: 0.473
- phase_breakdown.approach_object_score: 0.815

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.532
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.467
- **Median Q (composite search score)**: 0.180
- **K-run variance**: 0.0006
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.365


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
{"anchors":[{"name":"object","value":[0.5,-0.15,0.025]},{"name":"goal","value":[0.54443,-0.02558,0.025]}],"axes":[{"name":"push_direction","value":[-0.04443,-0.12442,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.54443,-0.02558,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.44144,"average_solve_count":111.0,"average_success_count":111.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_offset_z":0.145,"approach.approach_speed":0.15694,"descend.descend_speed":0.19024,"push.push_distance":0.26039,"push.push_speed":0.17083},"optimized_scores":{"best_composite_score":0.18019,"best_fitness_score":0.49019,"best_task_score":0.40676},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":79.0,"contact_point_centroid":[0.55638,-0.0252,0.04705],"force_p95":265.28347,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":271.77634,"mean_force":216.78298,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.54498,-0.02533,0.04915]},{"body_a":"attachment","body_b":"push_box","contact_count":322.0,"contact_point_centroid":[0.55221,-0.05187,0.04799],"force_p95":141.7346,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":144.7315,"mean_force":101.95739,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.54343,-0.05757,0.04942]},{"body_a":"world","body_b":"push_box","contact_count":1673.0,"contact_point_centroid":[0.54485,-0.02564,-8e-05],"force_p95":104.09787,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":138.96048,"mean_force":10.53964,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.53847,-0.02428,0.10331]},{"body_a":"world","body_b":"push_box","contact_count":3291.0,"contact_point_centroid":[0.53568,-0.07129,-0.00012],"force_p95":73.74596,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":87.05869,"mean_force":10.28365,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49575,-0.16088,0.03657]},{"body_a":"world","body_b":"push_box","contact_count":1668.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.51753,-0.0113,0.23829]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.53259,-0.07872,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.46972,-0.21614,0.08089]}],"total_contact_groups":6},"final_pose_error":0.12581,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53259,-0.07872,0.02499],"final_tcp_position":[0.49408,-0.16014,0.13715],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":271.77634,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":417.0,"n_steps_budget":600.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1668.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach_object","tcp_end":[0.53736,-0.02318,0.17655],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.15175,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":422.0,"n_steps_budget":600.0,"object_pos_end":[0.54819,-0.02579,0.02377],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.13324,"object_to_goal_dist_start":0.13211,"object_z_max":0.02499,"peak_contact_force":246.35246,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1752.0,"raw_peak_contact_force":271.77634,"tcp_end":[0.55216,-0.02574,0.04692],"tcp_start":[0.53736,-0.02318,0.17655],"tcp_to_object_dist_end":0.02349,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53259,-0.07872,0.02499],"object_pos_start":[0.54819,-0.02579,0.02377],"object_to_goal_dist_end":0.07837,"object_to_goal_dist_start":0.13324,"object_z_max":0.03526,"peak_contact_force":0.24525,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3613.0,"raw_peak_contact_force":144.7315,"subtask_id":"push_to_goal","tcp_end":[0.44858,-0.27447,0.02837],"tcp_start":[0.55216,-0.02574,0.04692],"tcp_to_object_dist_end":0.21304,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53259,-0.07872,0.02499],"object_pos_start":[0.53259,-0.07872,0.02499],"object_to_goal_dist_end":0.07837,"object_to_goal_dist_start":0.07837,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.49408,-0.16014,0.13715],"tcp_start":[0.44858,-0.27447,0.02837],"tcp_to_object_dist_end":0.14385,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `e094d2c5a71c8b89ef1fa30d7ce553b9c4ed64cd3fbca90620c3ede94e719cec`; realized-scene SHA-256: `d6f67641a3df0efca2ae6de2763dea57e4736e336d1ca3e6fe373ea0745d2d85`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5,-0.15,0.025]},{"name":"goal","value":[0.55472,-0.03508,0.025]}],"axes":[{"name":"push_direction","value":[-0.05472,-0.11492,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.55472,-0.03508,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.44643,"average_solve_count":112.0,"average_success_count":112.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_offset_z":0.15058,"approach.approach_speed":0.17374,"descend.descend_speed":0.16028,"push.push_distance":0.2348,"push.push_speed":0.19998},"optimized_scores":{"best_composite_score":0.22216,"best_fitness_score":0.53216,"best_task_score":0.46716},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":81.0,"contact_point_centroid":[0.56673,-0.03451,0.04711],"force_p95":255.69871,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":264.33392,"mean_force":211.29721,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.55524,-0.03474,0.04898]},{"body_a":"attachment","body_b":"push_box","contact_count":306.0,"contact_point_centroid":[0.55813,-0.06278,0.04848],"force_p95":144.15414,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":145.6844,"mean_force":100.94217,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.54914,-0.0688,0.04927]},{"body_a":"world","body_b":"push_box","contact_count":1728.0,"contact_point_centroid":[0.55514,-0.03513,-8e-05],"force_p95":102.01805,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":135.9259,"mean_force":10.20658,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.54839,-0.03334,0.10509]},{"body_a":"world","body_b":"push_box","contact_count":3323.0,"contact_point_centroid":[0.54097,-0.08587,-0.00011],"force_p95":71.95974,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":113.13067,"mean_force":9.60232,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.48072,-0.18667,0.03444]},{"body_a":"world","body_b":"push_box","contact_count":1732.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.52234,-0.01566,0.24007]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.53729,-0.09335,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.44159,-0.25526,0.07214]}],"total_contact_groups":6},"final_pose_error":0.1598,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53729,-0.09335,0.02499],"final_tcp_position":[0.47375,-0.1989,0.12321],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55472,-0.03508,0.025]},"peak_contact_force":264.33392,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":433.0,"n_steps_budget":600.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.025],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1732.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach_object","tcp_end":[0.54695,-0.03191,0.1809],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.15613,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":436.0,"n_steps_budget":630.0,"object_pos_end":[0.55844,-0.03534,0.02376],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.1287,"object_to_goal_dist_start":0.12728,"object_z_max":0.02499,"peak_contact_force":241.79106,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1809.0,"raw_peak_contact_force":264.33392,"tcp_end":[0.56245,-0.03529,0.04675],"tcp_start":[0.54695,-0.03191,0.1809],"tcp_to_object_dist_end":0.02334,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53729,-0.09335,0.02499],"object_pos_start":[0.55844,-0.03534,0.02376],"object_to_goal_dist_end":0.06782,"object_to_goal_dist_start":0.1287,"object_z_max":0.03503,"peak_contact_force":0.24525,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3629.0,"raw_peak_contact_force":145.6844,"subtask_id":"push_to_goal","tcp_end":[0.41243,-0.3141,0.0248],"tcp_start":[0.56245,-0.03529,0.04675],"tcp_to_object_dist_end":0.25361,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53729,-0.09335,0.02499],"object_pos_start":[0.53729,-0.09335,0.02499],"object_to_goal_dist_end":0.06782,"object_to_goal_dist_start":0.06782,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.47375,-0.1989,0.12321],"tcp_start":[0.41243,-0.3141,0.0248],"tcp_to_object_dist_end":0.15756,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `0fd7d18e656259f06515eb57b82afa0c0febd9395a43c1a5f926ddaec3767c64`; realized-scene SHA-256: `5de0d8cc5a3c16249bcf1097af6edba15dfacc79d06e3eed726605dcb01257b0`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5,-0.15,0.025]},{"name":"goal","value":[0.45543,-9e-05,0.025]}],"axes":[{"name":"push_direction","value":[0.04457,-0.14991,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.45543,-9e-05,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.2562,"average_solve_count":121.0,"average_success_count":121.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_offset_z":0.1423,"approach.approach_speed":0.21892,"descend.descend_speed":0.10861,"push.push_distance":0.15337,"push.push_speed":0.17232},"optimized_scores":{"best_composite_score":0.16192,"best_fitness_score":0.47192,"best_task_score":0.36985},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":121.0,"contact_point_centroid":[0.4701,-0.00013,0.04625],"force_p95":287.39734,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":296.02959,"mean_force":248.53236,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.45966,-0.00017,0.05011]},{"body_a":"attachment","body_b":"push_box","contact_count":309.0,"contact_point_centroid":[0.48871,-0.02661,0.04574],"force_p95":172.11653,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":180.68874,"mean_force":103.77059,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.48069,-0.03216,0.0487]},{"body_a":"world","body_b":"push_box","contact_count":3071.0,"contact_point_centroid":[0.49919,-0.04554,-0.00013],"force_p95":110.95933,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":149.61611,"mean_force":10.78673,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.5024,-0.15206,0.03275]},{"body_a":"world","body_b":"push_box","contact_count":2052.0,"contact_point_centroid":[0.45573,-9e-05,-0.00013],"force_p95":129.34158,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":147.01418,"mean_force":14.97841,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.45517,-0.00016,0.10069]},{"body_a":"world","body_b":"push_box","contact_count":1480.0,"contact_point_centroid":[0.45543,-9e-05,-1e-05],"force_p95":0.24531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.47867,-6e-05,0.23921]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.50169,-0.05146,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.51698,-0.20151,0.07531]}],"total_contact_groups":6},"final_pose_error":0.12938,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50169,-0.05146,0.02499],"final_tcp_position":[0.50979,-0.14178,0.13271],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45543,-9e-05,0.025]},"peak_contact_force":296.02959,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":370.0,"n_steps_budget":600.0,"object_pos_end":[0.45543,-9e-05,0.02499],"object_pos_start":[0.45543,-9e-05,0.025],"object_to_goal_dist_end":0.1564,"object_to_goal_dist_start":0.1564,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1480.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach_object","tcp_end":[0.45732,-0.00012,0.17695],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.15197,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":513.0,"n_steps_budget":870.0,"object_pos_end":[0.45939,-9e-05,0.02362],"object_pos_start":[0.45543,-9e-05,0.02499],"object_to_goal_dist_end":0.15532,"object_to_goal_dist_start":0.1564,"object_z_max":0.02499,"peak_contact_force":269.53421,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2173.0,"raw_peak_contact_force":296.02959,"tcp_end":[0.46805,-0.00018,0.04798],"tcp_start":[0.45732,-0.00012,0.17695],"tcp_to_object_dist_end":0.02585,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50169,-0.05146,0.02499],"object_pos_start":[0.45939,-9e-05,0.02362],"object_to_goal_dist_end":0.09856,"object_to_goal_dist_start":0.15532,"object_z_max":0.03526,"peak_contact_force":0.24525,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3380.0,"raw_peak_contact_force":180.68874,"subtask_id":"push_to_goal","tcp_end":[0.52825,-0.26392,0.02228],"tcp_start":[0.46805,-0.00018,0.04798],"tcp_to_object_dist_end":0.21413,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50169,-0.05146,0.02499],"object_pos_start":[0.50169,-0.05146,0.02499],"object_to_goal_dist_end":0.09856,"object_to_goal_dist_start":0.09856,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.50979,-0.14178,0.13271],"tcp_start":[0.52825,-0.26392,0.02228],"tcp_to_object_dist_end":0.14081,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```