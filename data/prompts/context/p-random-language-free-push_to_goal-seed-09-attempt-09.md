## Search State

- **Seed**: 9
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | contact_detected | time_limit | 6 | 0.4352 | 0.89 | ❌ rejected |
| 8 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | contact_detected | time_limit | 6 | 0.4405 | 0.90 | ✅ accepted |
| 7 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | contact_detected | time_limit | 6 | 0.4259 | 0.89 | ✅ accepted |
| 6 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 10 | -0.3922 | 0.00 | ❌ rejected |
| 5 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | pose_tolerance | 5 | -0.1334 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.89 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.902, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.435) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
subtasks:
- id: pre_contact
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.3
- id: at_goal
  target_entity: object
  metric: goal_progress
  weight: 0.7
phases:
- id: approach_side
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.1
    offset_along_axis:
      distance: 0.05
      axis: task_goal_direction
      mode: add_to_offset
      sign: negative
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
    lateral_offset:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.05
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
  subtask_id: pre_contact
- id: descend_to_side
  type: descend
  generator: linear_cartesian
  control: impedance_control
  termination: contact_detected
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.02
    offset_along_axis:
      distance: 0.05
      axis: task_goal_direction
      mode: add_to_offset
      sign: negative
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    lateral_offset:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.05
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
  subtask_id: pre_contact
- id: push_to_goal
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: time_limit
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.15
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.05
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: push_force_limit
    when: during_phase
    predicate: force_below
    threshold: 25.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: reduce_speed
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: at_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_side** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.1], offset_along_axis={axis=task_goal_direction, distance=0.05, mode=add_to_offset, sign=negative}
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - lateral_offset: status=consumed; consumers=target.offset_along_axis.distance (replace)
- **descend_to_side** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.02], offset_along_axis={axis=task_goal_direction, distance=0.05, mode=add_to_offset, sign=negative}
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - lateral_offset: status=consumed; consumers=target.offset_along_axis.distance (replace)
- **push_to_goal** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.15, mode=add_to_offset, sign=positive}
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=push_force_limit, when=during_phase, predicate=force_below, on_failure=retry, threshold=25.0
  - retries: max_attempts=2, strategy=reduce_speed, offset=[0.0, 0.0, 0.0]

## Design Metrics

- **Composite score**: 0.435
- **task_score** (E): 0.894
- **fitness_score**: 0.765  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.330

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_side | 1.00 | 1.00 | 0.1841 |
| descend_to_side | 1.00 | 1.00 | 0.0855 |
| push_to_goal | 1.00 | 1.00 | 0.1266 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_side | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.523, 0.032, 0.131) | (0.518, -0.020, 0.025)→(0.518, -0.020, 0.025) | 0.139→0.139 | 1.00 / 4.000 | 0.245 | 0.245 |
| descend_to_side | descend | 1.00 / step_budget | (0.523, 0.032, 0.131)→(0.521, 0.016, 0.048) | (0.518, -0.020, 0.025)→(0.518, -0.021, 0.025) | 0.139→0.138 | 1.00 / 4.000 | 16.108 | 63.786 |
| push_to_goal | push | 1.00 / time_limit | (0.521, 0.016, 0.048)→(0.495, -0.102, 0.043) | (0.518, -0.021, 0.025)→(0.496, -0.135, 0.027) | 0.138→0.016 | 1.00 / 2.667 | 4.241 | 21.892 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.677
- goal_progress: 0.989
- terminal_score: 0.989
- phase_score: 0.745
- phase_breakdown.at_goal_score: 0.989
- phase_breakdown.pre_contact_score: 0.177

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.843
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.989
- **Median Q (composite search score)**: 0.491
- **K-run variance**: 0.0089
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.264


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.68,"average_solve_count":100.0,"average_success_count":100.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_side.approach_speed":0.17015,"approach_side.lateral_offset":0.05175,"descend_to_side.descend_speed":0.0392,"descend_to_side.lateral_offset":0.03485,"push_to_goal.push_distance":0.13498,"push_to_goal.push_speed":0.09315},"optimized_scores":{"best_composite_score":0.49057,"best_fitness_score":0.82057,"best_task_score":0.96045},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":43.0,"contact_point_centroid":[0.55793,-0.00088,0.04898],"force_p95":92.4491,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":101.25172,"mean_force":70.42101,"phase_index":1.0,"phase_name":"descend_to_side","phase_type":"descend","tcp_position_centroid":[0.55285,0.0094,0.05016]},{"body_a":"world","body_b":"push_box","contact_count":1890.0,"contact_point_centroid":[0.54495,-0.0251,-2e-05],"force_p95":8.4114,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":81.08245,"mean_force":1.86192,"phase_index":1.0,"phase_name":"descend_to_side","phase_type":"descend","tcp_position_centroid":[0.55164,0.0149,0.0871]},{"body_a":"attachment","body_b":"push_box","contact_count":560.0,"contact_point_centroid":[0.52718,-0.06078,0.04446],"force_p95":16.13661,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.73825,"mean_force":6.49343,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.52875,-0.049,0.04381]},{"body_a":"world","body_b":"push_box","contact_count":1476.0,"contact_point_centroid":[0.52081,-0.0908,-7e-05],"force_p95":8.54053,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.48077,"mean_force":2.8332,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.52988,-0.04605,0.04387]},{"body_a":"world","body_b":"push_box","contact_count":2200.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_side","phase_type":"approach","tcp_position_centroid":[0.52596,0.01052,0.21533]}],"total_contact_groups":5},"final_pose_error":0.00869,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49686,-0.14583,0.0248],"final_tcp_position":[0.50629,-0.11023,0.04391],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":101.25172,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":550.0,"n_steps_budget":720.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_side","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2200.0,"raw_peak_contact_force":0.24534,"subtask_id":"pre_contact","tcp_end":[0.55426,0.02138,0.13118],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.11653,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":482.0,"n_steps_budget":1000.0,"object_pos_end":[0.54495,-0.02636,0.02466],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.13156,"object_to_goal_dist_start":0.13211,"object_z_max":0.02499,"peak_contact_force":32.52768,"phase_name":"descend_to_side","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1933.0,"raw_peak_contact_force":101.25172,"subtask_id":"pre_contact","tcp_end":[0.55424,0.00986,0.04869],"tcp_start":[0.55426,0.02138,0.13118],"tcp_to_object_dist_end":0.04444,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":842.0,"n_steps_budget":900.0,"object_pos_end":[0.49686,-0.14583,0.0248],"object_pos_start":[0.54495,-0.02636,0.02466],"object_to_goal_dist_end":0.00523,"object_to_goal_dist_start":0.13156,"object_z_max":0.02575,"peak_contact_force":3.19553,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2036.0,"raw_peak_contact_force":20.73825,"subtask_id":"at_goal","tcp_end":[0.50629,-0.11023,0.04391],"tcp_start":[0.55424,0.00986,0.04869],"tcp_to_object_dist_end":0.04148,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.61682,"average_solve_count":107.0,"average_success_count":107.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_side.approach_speed":0.09644,"approach_side.lateral_offset":0.06606,"descend_to_side.descend_speed":0.05619,"descend_to_side.lateral_offset":0.03607,"push_to_goal.push_distance":0.13442,"push_to_goal.push_speed":0.08825},"optimized_scores":{"best_composite_score":0.51259,"best_fitness_score":0.84259,"best_task_score":0.9887},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":25.0,"contact_point_centroid":[0.5684,-0.01073,0.04909],"force_p95":61.31449,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":73.12003,"mean_force":31.59788,"phase_index":1.0,"phase_name":"descend_to_side","phase_type":"descend","tcp_position_centroid":[0.56683,0.00081,0.04941]},{"body_a":"world","body_b":"push_box","contact_count":1757.0,"contact_point_centroid":[0.5547,-0.03537,-1e-05],"force_p95":0.26573,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":45.81323,"mean_force":0.69774,"phase_index":1.0,"phase_name":"descend_to_side","phase_type":"descend","tcp_position_centroid":[0.56912,0.01153,0.08672]},{"body_a":"attachment","body_b":"push_box","contact_count":658.0,"contact_point_centroid":[0.53415,-0.06836,0.04239],"force_p95":15.8012,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.16322,"mean_force":6.06086,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.53526,-0.0565,0.04192]},{"body_a":"world","body_b":"push_box","contact_count":1718.0,"contact_point_centroid":[0.52854,-0.0983,-8e-05],"force_p95":7.49749,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.52198,"mean_force":2.65378,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.53615,-0.05478,0.04199]},{"body_a":"world","body_b":"push_box","contact_count":2668.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_side","phase_type":"approach","tcp_position_centroid":[0.53606,0.0113,0.21399]}],"total_contact_groups":5},"final_pose_error":0.00822,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50119,-0.1508,0.02514],"final_tcp_position":[0.50728,-0.11435,0.04204],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55472,-0.03508,0.025]},"peak_contact_force":73.12003,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":667.0,"n_steps_budget":1000.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.025],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_side","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2668.0,"raw_peak_contact_force":0.24534,"subtask_id":"pre_contact","tcp_end":[0.5746,0.02285,0.12961],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.12123,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":446.0,"n_steps_budget":990.0,"object_pos_end":[0.5547,-0.03621,0.02494],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.12625,"object_to_goal_dist_start":0.12728,"object_z_max":0.02502,"peak_contact_force":15.36005,"phase_name":"descend_to_side","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1782.0,"raw_peak_contact_force":73.12003,"subtask_id":"pre_contact","tcp_end":[0.56693,0.00051,0.04708],"tcp_start":[0.5746,0.02285,0.12961],"tcp_to_object_dist_end":0.04459,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":902.0,"n_steps_budget":960.0,"object_pos_end":[0.50119,-0.1508,0.02514],"object_pos_start":[0.5547,-0.03621,0.02494],"object_to_goal_dist_end":0.00144,"object_to_goal_dist_start":0.12625,"object_z_max":0.02559,"peak_contact_force":0.7368,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2376.0,"raw_peak_contact_force":20.16322,"subtask_id":"at_goal","tcp_end":[0.50728,-0.11435,0.04204],"tcp_start":[0.56693,0.00051,0.04708],"tcp_to_object_dist_end":0.04063,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.76,"average_solve_count":100.0,"average_success_count":100.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_side.approach_speed":0.11761,"approach_side.lateral_offset":0.05879,"descend_to_side.descend_speed":0.06462,"descend_to_side.lateral_offset":0.03717,"push_to_goal.push_distance":0.14132,"push_to_goal.push_speed":0.07636},"optimized_scores":{"best_composite_score":0.3023,"best_fitness_score":0.6323,"best_task_score":0.73265},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":818.0,"contact_point_centroid":[0.4617,-0.03295,0.04846],"force_p95":16.4731,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.77494,"mean_force":6.78215,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.45471,-0.0217,0.04378]},{"body_a":"attachment","body_b":"push_box","contact_count":9.0,"contact_point_centroid":[0.44086,0.02478,0.04929],"force_p95":16.73015,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.98573,"mean_force":13.4214,"phase_index":1.0,"phase_name":"descend_to_side","phase_type":"descend","tcp_position_centroid":[0.44066,0.03677,0.04916]},{"body_a":"world","body_b":"push_box","contact_count":1367.0,"contact_point_centroid":[0.47689,-0.06851,-6e-05],"force_p95":10.5306,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.31683,"mean_force":4.57295,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.4536,-0.0177,0.04389]},{"body_a":"world","body_b":"push_box","contact_count":2173.0,"contact_point_centroid":[0.45542,-0.00017,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.17675,"mean_force":0.30027,"phase_index":1.0,"phase_name":"descend_to_side","phase_type":"descend","tcp_position_centroid":[0.43903,0.04407,0.08925]},{"body_a":"world","body_b":"push_box","contact_count":2248.0,"contact_point_centroid":[0.45543,-9e-05,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_side","phase_type":"approach","tcp_position_centroid":[0.46982,0.02535,0.21699]}],"total_contact_groups":5},"final_pose_error":0.02135,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49129,-0.10947,0.03041],"final_tcp_position":[0.47197,-0.0801,0.0432],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45543,-9e-05,0.025]},"peak_contact_force":24.77494,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":562.0,"n_steps_budget":1000.0,"object_pos_end":[0.45543,-9e-05,0.02499],"object_pos_start":[0.45543,-9e-05,0.025],"object_to_goal_dist_end":0.1564,"object_to_goal_dist_start":0.1564,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_side","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2248.0,"raw_peak_contact_force":0.24534,"subtask_id":"pre_contact","tcp_end":[0.44004,0.05187,0.13363],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.1214,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":545.0,"n_steps_budget":870.0,"object_pos_end":[0.45531,-0.00035,0.02499],"object_pos_start":[0.45543,-9e-05,0.02499],"object_to_goal_dist_end":0.15618,"object_to_goal_dist_start":0.1564,"object_z_max":0.025,"peak_contact_force":0.43572,"phase_name":"descend_to_side","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2182.0,"raw_peak_contact_force":16.98573,"subtask_id":"pre_contact","tcp_end":[0.44073,0.03656,0.04764],"tcp_start":[0.44004,0.05187,0.13363],"tcp_to_object_dist_end":0.0457,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49129,-0.10947,0.03041],"object_pos_start":[0.45531,-0.00035,0.02499],"object_to_goal_dist_end":0.04181,"object_to_goal_dist_start":0.15618,"object_z_max":0.03053,"peak_contact_force":8.78997,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2185.0,"raw_peak_contact_force":24.77494,"subtask_id":"at_goal","tcp_end":[0.47197,-0.0801,0.0432],"tcp_start":[0.44073,0.03656,0.04764],"tcp_to_object_dist_end":0.03741,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```