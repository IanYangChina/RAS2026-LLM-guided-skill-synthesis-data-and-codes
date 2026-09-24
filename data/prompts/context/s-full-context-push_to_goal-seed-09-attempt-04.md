## Search State

- **Seed**: 9
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | time_limit | 9 | 0.2511 | 0.47 | ❌ rejected |
| 3 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | time_limit | 8 | -0.3184 | 0.00 | ❌ rejected |
| 2 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | time_limit | 5 | 0.2607 | 0.54 | ✅ accepted |
| 1 | rotate → pull → push → descend → descend → grasp | arc_cartesian | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | impedance_control | impedance_control | position_control | admittance_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | contact_detected | grasp_success | 5 | -0.3700 | 0.00 | ❌ rejected |
| 0 | rotate → pull → push → descend → descend → grasp | arc_cartesian | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | impedance_control | impedance_control | position_control | admittance_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | contact_detected | grasp_success | 5 | -0.3700 | 0.00 | ✅ accepted |

**Proposal policy**: task_score is 0.47 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.251) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
subtasks:
- id: push_progress
  target_entity: object
  metric: goal_progress
phases:
- id: approach_behind
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
    - 0.025
    offset_along_axis:
      distance: 0.1
      axis: task_goal_direction
      mode: replace_offset_projection
      sign: negative
    tolerance: 0.01
  parameters:
    speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: contact_guard
    when: during_phase
    predicate: contact_detected
    threshold: 0.0
    on_failure: abort
- id: contact_make
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.05
      axis: task_goal_direction
      mode: replace_offset_projection
      sign: positive
    tolerance: 0.01
  parameters:
    force_threshold:
      type: scalar
      range:
      - 1.0
      - 10.0
      default: 3.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
  guards:
  - id: pre_force
    when: before_phase
    predicate: force_below
    threshold: 15.0
    on_failure: abort
- id: push_to_goal
  type: push
  generator: linear_cartesian
  control: admittance_control
  termination: time_limit
  target:
    source: yaml
    anchor: task_goal
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
  parameters:
    max_time:
      type: scalar
      range:
      - 2.0
      - 10.0
      default: 5.0
      binds_to:
      - path: duration.max_time
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
    stroke_distance:
      type: scalar
      range:
      - 0.08
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
  guards:
  - id: force_limit_guard
    when: during_phase
    predicate: force_below
    threshold: 20.0
    on_failure: abort
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.01
    - 0.01
    - 0.0
  subtask_id: push_progress

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_behind** (`approach`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.0, 0.025], offset_along_axis={axis=task_goal_direction, distance=0.1, mode=replace_offset_projection, sign=negative}, tolerance=0.01
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=contact_guard, when=during_phase, predicate=contact_detected, on_failure=abort, threshold=0.0
- **contact_make** (`contact`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.05, mode=replace_offset_projection, sign=positive}, tolerance=0.01
  - parameter_bindings:
    - force_threshold: status=consumed; consumers=termination.force_threshold (replace)
  - guards:
    - id=pre_force, when=before_phase, predicate=force_below, on_failure=abort, threshold=15.0
- **push_to_goal** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.15, mode=replace_offset_projection, sign=positive}, tolerance=0.02
  - parameter_bindings:
    - max_time: status=consumed; consumers=duration.max_time (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
    - stroke_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
  - guards:
    - id=force_limit_guard, when=during_phase, predicate=force_below, on_failure=abort, threshold=20.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.01, 0.01, 0.0]

## Design Metrics

- **Composite score**: 0.251
- **task_score** (E): 0.473
- **fitness_score**: 0.453  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.278
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.480

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_behind | 1.00 | 1.00 | 0.2921 |
| contact_make | 0.67 | 1.00 | 0.0451 |
| push_to_goal | 0.67 | 1.00 | 0.0797 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_behind | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.535, 0.073, 0.031) | (0.518, -0.020, 0.025)→(0.518, -0.020, 0.025) | 0.139→0.139 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_make | contact | 0.67 / force_exceeded | (0.535, 0.073, 0.031)→(0.521, 0.033, 0.025) | (0.518, -0.020, 0.025)→(0.518, -0.020, 0.025) | 0.139→0.139 | 1.00 / 4.667 | 12.696 | 0.245 |
| push_to_goal | push | 0.67 / time_limit | (0.521, 0.033, 0.025)→(0.490, -0.041, 0.022) | (0.518, -0.020, 0.025)→(0.496, -0.077, 0.025) | 0.139→0.077 | 1.00 / 4.667 | 12.362 | 20.527 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.874
- lateral_force_integral: None
- approach_alignment: 0.642
- goal_progress: 0.873
- terminal_score: 0.873
- phase_score: 0.753
- phase_breakdown.push_progress_score: 0.873
- phase_breakdown.approach_contact_score: 0.473

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.801
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.873
- **Median Q (composite search score)**: -0.011
- **K-run variance**: 0.1627
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.413


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.04082,"average_solve_count":98.0,"average_success_count":98.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_offset":0.15038,"approach_behind.speed":0.17109,"contact_make.contact_distance":0.05854,"contact_make.force_threshold":2.67565,"contact_make.speed":0.05198,"push_to_goal.force_limit_guard_threshold":16.04332,"push_to_goal.max_time":5.03908,"push_to_goal.speed":0.03957,"push_to_goal.stroke_distance":0.21857},"optimized_scores":{"best_composite_score":-0.01087,"best_fitness_score":0.46913,"best_task_score":0.53348},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":520.0,"contact_point_centroid":[0.53971,-0.03395,0.03403],"force_p95":11.47014,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.22832,"mean_force":3.63521,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.53275,-0.02214,0.01726]},{"body_a":"world","body_b":"push_box","contact_count":2599.0,"contact_point_centroid":[0.54038,-0.04201,-2e-05],"force_p95":5.37913,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.18838,"mean_force":1.09401,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.54517,0.01425,0.01713]},{"body_a":"push_box","body_b":"link7","contact_count":139.0,"contact_point_centroid":[0.55665,-0.04381,0.05018],"force_p95":8.96227,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.33027,"mean_force":2.70757,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.53011,-0.03012,0.01739]},{"body_a":"world","body_b":"push_box","contact_count":3900.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.54304,0.05583,0.16177]},{"body_a":"world","body_b":"push_box","contact_count":2536.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_make","phase_type":"contact","tcp_position_centroid":[0.57351,0.08427,0.02233]}],"total_contact_groups":5},"final_pose_error":0.31455,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52376,-0.09313,0.02493],"final_tcp_position":[0.52152,-0.05608,0.01774],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":15.22832,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":975.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3900.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach_contact","tcp_end":[0.58713,0.11102,0.02825],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.14316,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":634.0,"n_steps_budget":720.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"contact_make","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2536.0,"raw_peak_contact_force":0.24525,"subtask_id":"approach_contact","tcp_end":[0.56415,0.05896,0.02208],"tcp_start":[0.58713,0.11102,0.02825],"tcp_to_object_dist_end":0.08686,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52376,-0.09313,0.02493],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.06163,"object_to_goal_dist_start":0.13211,"object_z_max":0.02534,"peak_contact_force":1.29103,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3258.0,"raw_peak_contact_force":15.22832,"subtask_id":"push_progress","tcp_end":[0.52152,-0.05608,0.01774],"tcp_start":[0.56415,0.05896,0.02208],"tcp_to_object_dist_end":0.03781,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.73786,"average_solve_count":103.0,"average_success_count":103.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_offset":0.08893,"approach_behind.speed":0.18334,"contact_make.contact_distance":0.07524,"contact_make.force_threshold":1.46588,"contact_make.speed":0.03018,"push_to_goal.force_limit_guard_threshold":23.37827,"push_to_goal.max_time":5.79605,"push_to_goal.speed":0.0395,"push_to_goal.stroke_distance":0.23638},"optimized_scores":{"best_composite_score":0.82091,"best_fitness_score":0.80091,"best_task_score":0.8729},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":855.0,"contact_point_centroid":[0.53241,-0.06104,0.01955],"force_p95":11.99286,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.55422,"mean_force":3.78965,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.53349,-0.04916,0.01875]},{"body_a":"world","body_b":"push_box","contact_count":2046.0,"contact_point_centroid":[0.52936,-0.08882,-4e-05],"force_p95":4.91163,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.11054,"mean_force":1.83692,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.53434,-0.0474,0.01883]},{"body_a":"world","body_b":"push_box","contact_count":3492.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.54156,0.02145,0.1635]},{"body_a":"world","body_b":"push_box","contact_count":3376.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_make","phase_type":"contact","tcp_position_centroid":[0.57002,0.02112,0.02395]}],"total_contact_groups":4},"final_pose_error":0.28715,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50826,-0.13609,0.02489],"final_tcp_position":[0.51098,-0.09934,0.01893],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55472,-0.03508,0.025]},"peak_contact_force":20.55422,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":873.0,"n_steps_budget":1000.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.025],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3492.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach_contact","tcp_end":[0.5847,0.04297,0.02984],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08374,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":844.0,"n_steps_budget":1000.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.02499,"peak_contact_force":17.96992,"phase_name":"contact_make","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3376.0,"raw_peak_contact_force":0.24525,"subtask_id":"approach_contact","tcp_end":[0.5606,0.00188,0.0238],"tcp_start":[0.5847,0.04297,0.02984],"tcp_to_object_dist_end":0.03744,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50826,-0.13609,0.02489],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.01618,"object_to_goal_dist_start":0.12728,"object_z_max":0.02519,"peak_contact_force":9.99366,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2901.0,"raw_peak_contact_force":20.55422,"subtask_id":"push_progress","tcp_end":[0.51098,-0.09934,0.01893],"tcp_start":[0.5606,0.00188,0.0238],"tcp_to_object_dist_end":0.03733,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.18966,"average_solve_count":58.0,"average_success_count":58.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_offset":0.07339,"approach_behind.speed":0.15801,"contact_make.contact_distance":0.04563,"contact_make.force_threshold":7.44777,"contact_make.speed":0.05162,"push_to_goal.force_limit_guard_threshold":23.07603,"push_to_goal.max_time":5.92803,"push_to_goal.speed":0.07863,"push_to_goal.stroke_distance":0.14716},"optimized_scores":{"best_composite_score":-0.05683,"best_fitness_score":0.08984,"best_task_score":0.0128},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":31.0,"contact_point_centroid":[0.44445,0.02359,0.03814],"force_p95":17.80229,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":25.79985,"mean_force":9.25642,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.43828,0.0353,0.0293]},{"body_a":"push_box","body_b":"link7","contact_count":17.0,"contact_point_centroid":[0.47995,0.0221,0.04979],"force_p95":20.04086,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.76203,"mean_force":14.25785,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.43815,0.03454,0.02889]},{"body_a":"world","body_b":"push_box","contact_count":99.0,"contact_point_centroid":[0.45628,0.0011,-6e-05],"force_p95":10.86254,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.48263,"mean_force":5.25423,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.43828,0.03525,0.02928]},{"body_a":"world","body_b":"push_box","contact_count":3212.0,"contact_point_centroid":[0.45543,-9e-05,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.46634,0.03293,0.16646]},{"body_a":"world","body_b":"push_box","contact_count":1492.0,"contact_point_centroid":[0.45543,-9e-05,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_make","phase_type":"contact","tcp_position_centroid":[0.43473,0.0513,0.03064]}],"total_contact_groups":5},"final_pose_error":0.34112,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.45581,-0.00206,0.02481],"final_tcp_position":[0.43815,0.03387,0.02861],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45543,-9e-05,0.025]},"peak_contact_force":25.79985,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":803.0,"n_steps_budget":1000.0,"object_pos_end":[0.45543,-9e-05,0.02499],"object_pos_start":[0.45543,-9e-05,0.025],"object_to_goal_dist_end":0.1564,"object_to_goal_dist_start":0.1564,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3212.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach_contact","tcp_end":[0.43384,0.06639,0.03412],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07049,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":373.0,"n_steps_budget":600.0,"object_pos_end":[0.45543,-9e-05,0.02499],"object_pos_start":[0.45543,-9e-05,0.02499],"object_to_goal_dist_end":0.1564,"object_to_goal_dist_start":0.1564,"object_z_max":0.02499,"peak_contact_force":19.87154,"phase_name":"contact_make","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1492.0,"raw_peak_contact_force":0.24525,"subtask_id":"approach_contact","tcp_end":[0.43857,0.03688,0.03017],"tcp_start":[0.43384,0.06639,0.03412],"tcp_to_object_dist_end":0.04096,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":6.0,"n_steps":33.0,"n_steps_budget":1000.0,"object_pos_end":[0.45581,-0.00206,0.02481],"object_pos_start":[0.45543,-9e-05,0.02499],"object_to_goal_dist_end":0.1544,"object_to_goal_dist_start":0.1564,"object_z_max":0.02511,"peak_contact_force":25.79985,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":147.0,"raw_peak_contact_force":25.79985,"subtask_id":"push_progress","tcp_end":[0.43815,0.03387,0.02861],"tcp_start":[0.43857,0.03688,0.03017],"tcp_to_object_dist_end":0.04022,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```