## Search State

- **Seed**: 3
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → push | linear_cartesian | linear_cartesian | position_control | admittance_control | pose_tolerance | time_limit | 6  | 0.4920 | 0.84 | ❌ rejected |
| 12 | approach → push | linear_cartesian | linear_cartesian | position_control | admittance_control | pose_tolerance | time_limit | 5  | -0.0903 | 0.00 | ❌ rejected |
| 11 | approach → push | linear_cartesian | linear_cartesian | position_control | admittance_control | pose_tolerance | pose_tolerance | 4  | 0.4927 | 0.85 | ❌ rejected |
| 10 | approach → push | linear_cartesian | linear_cartesian | position_control | admittance_control | pose_tolerance | time_limit | 5  | 0.5116 | 0.87 | ✅ accepted |
| 9 | approach → push | linear_cartesian | linear_cartesian | position_control | admittance_control | pose_tolerance | time_limit | 5  | -0.0804 | 0.14 | ❌ rejected |

**Proposal policy**: task_score is 0.14 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `35b7946dd60174c5d3e72b05c58367a0800836a817579e6ae5b810157d0560be`
- Frozen object start: [0.45027790005723495, -0.03158273920846803, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.45027790005723495, -0.03158273920846803, 0.025)
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
  frozen_object_start: [0.4503, -0.0316, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.45027790005723495, -0.03158273920846803, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [0.0497, -0.1184, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: 35b7946dd60174c5d3e72b05c58367a0800836a817579e6ae5b810157d0560be

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.871, which indicates the subtask decomposition is already effective.
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
| `object` | offset from object initial position (0.45027790005723495, -0.03158273920846803, 0.025) | approach/contact targets near object start |
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

## Current Skill (Q=-0.080) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
subtasks:
- id: pre_push
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.03
  weight: 0.3
- id: push_task
  target_entity: object
  metric: goal_progress
  weight: 0.7
phases:
- id: approach_to_push
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
    - 0.025
    offset_along_axis:
      distance: 0.06
      axis: task_goal_direction
      mode: add_to_offset
      sign: negative
    tolerance: 0.01
  parameters:
    approach_offset:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.06
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.5
      default: 0.3
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: pre_push
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
    - 0.025
    offset_along_axis:
      distance: 0.2
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
    tolerance: 0.01
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.1
      - 0.3
      default: 0.2
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_duration:
      type: scalar
      range:
      - 1.0
      - 5.0
      default: 3.0
      binds_to:
      - path: duration.max_time
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.2
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: push_task

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_to_push** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.025], offset_along_axis={axis=task_goal_direction, distance=0.06, mode=add_to_offset, sign=negative}, tolerance=0.01
  - parameter_bindings:
    - approach_offset: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **push_to_goal** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.025], offset_along_axis={axis=task_goal_direction, distance=0.2, mode=add_to_offset, sign=positive}, tolerance=0.01
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_duration: status=consumed; consumers=duration.max_time (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: -0.080
- **task_score** (E): 0.141
- **fitness_score**: 0.220  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.300

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_to_push | 1.00 | 1.00 | 0.2519 |
| push_to_goal | 0.00 | 1.00 | 0.0001 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_to_push | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.512, 0.030, 0.059) | (0.513, 0.002, 0.025)→(0.513, 0.002, 0.025) | 0.160→0.160 | 1.00 / 4.000 | 0.245 | 0.245 |
| push_to_goal | push | 0.00 / guard_failure | (0.499, -0.013, 0.054)→(0.499, -0.013, 0.054) | (0.513, 0.002, 0.025)→(0.513, -0.023, 0.028) | 0.160→0.135 | 1.00 / 3.000 | 21.055 | 39.648 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.253
- lateral_force_integral: None
- approach_alignment: 0.577
- goal_progress: 0.234
- terminal_score: 0.234
- phase_score: 0.371
- phase_breakdown.pre_push_score: 0.690
- phase_breakdown.push_task_score: 0.234

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.316
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.234
- **Median Q (composite search score)**: -0.079
- **K-run variance**: 0.0063
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.336


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `01fea9f27a58d64b0f9b0ff0cae1096a52b0da1ad311c77058a75ddb9aab77d2`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `c53c9bf1992485fcf877d50f4ee23d3483b4b9e63e5a19adda2461c26d89c46e`; realized-scene SHA-256: `35b7946dd60174c5d3e72b05c58367a0800836a817579e6ae5b810157d0560be`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45028,-0.03158,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.04972,-0.11842,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.45028,-0.03158,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.4186,"average_solve_count":43.0,"average_success_count":43.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_push.approach_offset":0.02017,"approach_to_push.approach_speed":0.1559,"push_to_goal.force_threshold":24.88794,"push_to_goal.push_distance":0.14649,"push_to_goal.push_duration":2.12193,"push_to_goal.push_speed":0.04769},"optimized_scores":{"best_composite_score":-0.17839,"best_fitness_score":0.12161,"best_task_score":0.00563},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":39.0,"contact_point_centroid":[0.45175,-0.01868,0.0499],"force_p95":22.59872,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.21196,"mean_force":14.23806,"phase_index":1.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.44164,-0.01859,0.05625]},{"body_a":"world","body_b":"push_box","contact_count":387.0,"contact_point_centroid":[0.45231,-0.03404,-1e-05],"force_p95":8.2315,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.36459,"mean_force":1.69193,"phase_index":1.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.44124,-0.01584,0.05718]},{"body_a":"world","body_b":"push_box","contact_count":2788.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_to_push","phase_type":"approach","tcp_position_centroid":[0.47059,-0.00605,0.17996]}],"total_contact_groups":3},"final_pose_error":0.28901,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.45063,-0.03222,0.02496],"final_tcp_position":[0.44214,-0.0198,0.05611],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":29.21196,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":697.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_to_push","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2788.0,"raw_peak_contact_force":0.24534,"subtask_id":"pre_push","tcp_end":[0.44202,-0.01227,0.05978],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.04064,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":106.0,"n_steps_budget":1000.0,"object_pos_end":[0.45064,-0.03221,0.02496],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12771,"object_to_goal_dist_start":0.12843,"object_z_max":0.02499,"peak_contact_force":22.47334,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":426.0,"raw_peak_contact_force":29.21196,"subtask_id":"push_task","tcp_end":[0.44214,-0.0198,0.05611],"tcp_start":[0.44214,-0.01976,0.05613],"tcp_to_object_dist_end":0.03459,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `234a0edc218dcf63b67654ddcfd8b0f12da84040687f62c4c4845001a50f549a`; realized-scene SHA-256: `721a00290a47301d7751e432f1a041db545f1b55cfdb74b1d642c32f5b25f702`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.55317,0.00136,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.05317,-0.15136,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.55317,0.00136,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.23256,"average_solve_count":43.0,"average_success_count":43.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_push.approach_offset":0.02032,"approach_to_push.approach_speed":0.28213,"push_to_goal.force_threshold":27.31416,"push_to_goal.push_distance":0.12278,"push_to_goal.push_duration":2.18692,"push_to_goal.push_speed":0.07995},"optimized_scores":{"best_composite_score":0.01627,"best_fitness_score":0.31627,"best_task_score":0.23444},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":310.0,"contact_point_centroid":[0.54325,-0.03186,0.05016],"force_p95":24.92881,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":50.73613,"mean_force":12.9068,"phase_index":1.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.53205,-0.03217,0.05423]},{"body_a":"world","body_b":"push_box","contact_count":1482.0,"contact_point_centroid":[0.55124,-0.01041,-4e-05],"force_p95":19.25884,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":31.15517,"mean_force":3.07275,"phase_index":1.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.54015,-0.00728,0.0551]},{"body_a":"world","body_b":"push_box","contact_count":2220.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_to_push","phase_type":"approach","tcp_position_centroid":[0.52454,0.00915,0.18291]}],"total_contact_groups":3},"final_pose_error":0.22549,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.55293,-0.03918,0.02533],"final_tcp_position":[0.52602,-0.05048,0.05398],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":50.73613,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":555.0,"n_steps_budget":600.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_to_push","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2220.0,"raw_peak_contact_force":0.24534,"subtask_id":"pre_push","tcp_end":[0.55232,0.01895,0.06093],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.04003,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":574.0,"n_steps_budget":1000.0,"object_pos_end":[0.55299,-0.03917,0.02535],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.12285,"object_to_goal_dist_start":0.16043,"object_z_max":0.02644,"peak_contact_force":1.69528,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1792.0,"raw_peak_contact_force":50.73613,"subtask_id":"push_task","tcp_end":[0.52602,-0.05048,0.05398],"tcp_start":[0.52606,-0.0504,0.054],"tcp_to_object_dist_end":0.04093,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `107d1233d3b0a09f0fa34aa18231b315c9a1d92237bb254399d486ed8004836a`; realized-scene SHA-256: `b2a76c5d1121259d09d3db2c62740fd8fe93dd873d8f379ba1928ff319a7d266`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5366,0.03695,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.0366,-0.18695,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5366,0.03695,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.92857,"average_solve_count":56.0,"average_success_count":56.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_push.approach_offset":0.05144,"approach_to_push.approach_speed":0.18767,"push_to_goal.force_threshold":29.18576,"push_to_goal.push_distance":0.05959,"push_to_goal.push_duration":1.85852,"push_to_goal.push_speed":0.03896},"optimized_scores":{"best_composite_score":-0.07893,"best_fitness_score":0.22107,"best_task_score":0.18213},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":538.0,"contact_point_centroid":[0.53346,0.04122,0.05016],"force_p95":26.4148,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":38.99553,"mean_force":15.33775,"phase_index":1.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.53142,0.05282,0.05087]},{"body_a":"world","body_b":"push_box","contact_count":1464.0,"contact_point_centroid":[0.53625,0.01271,-6e-05],"force_p95":14.37951,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.24661,"mean_force":5.99102,"phase_index":1.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.53289,0.05953,0.05131]},{"body_a":"world","body_b":"push_box","contact_count":3084.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_to_push","phase_type":"approach","tcp_position_centroid":[0.51928,0.04118,0.17692]}],"total_contact_groups":3},"final_pose_error":0.24338,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53491,0.00153,0.03467],"final_tcp_position":[0.52837,0.03161,0.0514],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":38.99553,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":771.0,"n_steps_budget":900.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_to_push","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3084.0,"raw_peak_contact_force":0.24534,"subtask_id":"pre_push","tcp_end":[0.5403,0.08274,0.056],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.05543,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":635.0,"n_steps_budget":1000.0,"object_pos_end":[0.53491,0.00158,0.03467],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.15584,"object_to_goal_dist_start":0.1905,"object_z_max":0.03467,"peak_contact_force":38.99553,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2002.0,"raw_peak_contact_force":38.99553,"subtask_id":"push_task","tcp_end":[0.52837,0.03161,0.0514],"tcp_start":[0.52838,0.03166,0.05141],"tcp_to_object_dist_end":0.035,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```