## Search State

- **Seed**: 3
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | time_limit | 9 | 0.6335 | 0.94 | ✅ accepted |
| 6 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | time_limit | 8 | 0.4540 | 0.45 | ✅ accepted |
| 5 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | time_limit | 8 | -0.3432 | 0.00 | ❌ rejected |
| 4 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | time_limit | 9 | -0.3000 | 0.00 | ❌ rejected |
| 3 | contact → push | linear_cartesian | linear_cartesian | force_threshold_switch | admittance_control | force_exceeded | time_limit | 6 | -0.1197 | 0.00 | ✅ accepted |

**Proposal policy**: task_score is near-perfect (0.94). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.935, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.634) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
subtasks:
- id: make_contact
  anchor: object
  target_entity: object
  metric: contact
  weight: 0.3
- id: push_to_goal
  target_entity: object
  metric: goal_progress
  weight: 0.7
phases:
- id: approach_behind
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
    - 0.06
    offset_along_axis:
      distance: 0.15
      axis: task_goal_direction
      mode: replace_offset_projection
      sign: negative
    orientation:
      mode: none
  parameters:
    approach_distance:
      type: scalar
      range:
      - 0.05
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    approach_height:
      type: scalar
      range:
      - 0.03
      - 0.08
      default: 0.06
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
- id: make_contact
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.05
      axis: task_goal_direction
      mode: replace_offset_projection
      sign: positive
    orientation:
      mode: none
  parameters:
    contact_distance:
      type: scalar
      range:
      - 0.03
      - 0.1
      default: 0.05
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    contact_force_threshold:
      type: scalar
      range:
      - 2.0
      - 10.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    contact_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: no_contact_guard
    when: during_phase
    predicate: contact_detected
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - -0.01
  subtask_id: make_contact
- id: push_to_goal
  type: push
  generator: linear_cartesian
  control: admittance_control
  termination: time_limit
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.35
      axis: task_goal_direction
      mode: replace_offset_projection
      sign: positive
    orientation:
      mode: none
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.15
      - 0.5
      default: 0.35
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.02
      - 0.25
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
    push_time:
      type: scalar
      range:
      - 3.0
      - 15.0
      default: 8.0
      binds_to:
      - path: duration.max_time
        mode: replace
  guards:
  - id: contact_guard
    when: during_phase
    predicate: contact_detected
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: push_to_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_behind** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.06], offset_along_axis={axis=task_goal_direction, distance=0.15, mode=replace_offset_projection, sign=negative}
  - orientation: mode=none
  - parameter_bindings:
    - approach_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **make_contact** (`contact`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.05, mode=replace_offset_projection, sign=positive}
  - orientation: mode=none
  - parameter_bindings:
    - contact_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - contact_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=no_contact_guard, when=during_phase, predicate=contact_detected, on_failure=retry
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, -0.01]
- **push_to_goal** (`push`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.35, mode=replace_offset_projection, sign=positive}
  - orientation: mode=none
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
    - push_time: status=consumed; consumers=duration.max_time (replace)
  - guards:
    - id=contact_guard, when=during_phase, predicate=contact_detected, on_failure=retry
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.0]

## Design Metrics

- **Composite score**: 0.634
- **task_score** (E): 0.935
- **fitness_score**: 0.947  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.167
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.480

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_behind | 1.00 | 0.2779 |
| make_contact | 0.33 | 0.0751 |
| push_to_goal | 1.00 | 0.2493 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_behind | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.503, 0.124, 0.071) | (0.513, 0.002, 0.025)→(0.513, 0.002, 0.025) | 0.160→0.160 |
| make_contact | contact | 0.33 / step_budget | (0.503, 0.124, 0.071)→(0.501, 0.058, 0.048) | (0.513, 0.002, 0.025)→(0.513, 0.002, 0.025) | 0.160→0.160 |
| push_to_goal | push | 1.00 / time_limit | (0.501, 0.058, 0.048)→(0.481, -0.179, 0.026) | (0.513, 0.002, 0.025)→(0.507, -0.150, 0.025) | 0.160→0.010 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.955
- approach_alignment: 0.814
- goal_progress: 0.952
- terminal_score: 0.952
- phase_score: 0.967
- phase_breakdown.push_to_goal_score: 0.952

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.969
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.962
- **Median Q (composite search score)**: 0.489
- **K-run variance**: 0.0608
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.303


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.68548,"average_solve_count":124.0,"average_success_count":124.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_distance":0.2051,"approach_behind.approach_height":0.03127,"approach_behind.approach_speed":0.12235,"make_contact.contact_distance":0.03036,"make_contact.contact_force_threshold":4.28582,"make_contact.contact_speed":0.06068,"push_to_goal.push_distance":0.1818,"push_to_goal.push_speed":0.12255,"push_to_goal.push_time":9.18762},"optimized_scores":{"best_composite_score":0.48884,"best_fitness_score":0.96884,"best_task_score":0.962},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":445.0,"contact_point_centroid":[0.46684,-0.06589,0.04976],"force_p95":27.49898,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":52.25842,"mean_force":10.5641,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.45388,-0.05408,0.03098]},{"body_a":"world","body_b":"push_box","contact_count":2358.0,"contact_point_centroid":[0.46437,-0.06646,-4e-05],"force_p95":11.09186,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":31.58928,"mean_force":2.35091,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.43442,-0.00947,0.03461]},{"body_a":"push_box","body_b":"link7","contact_count":31.0,"contact_point_centroid":[0.50598,-0.08422,0.0508],"force_p95":14.2075,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.13733,"mean_force":2.5141,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.46211,-0.0727,0.02956]},{"body_a":"world","body_b":"push_box","contact_count":3972.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.43532,0.07526,0.17939]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"make_contact","phase_type":"contact","tcp_position_centroid":[0.38851,0.10468,0.0514]}],"total_contact_groups":5},"final_pose_error":0.0899,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49893,-0.15476,0.02485],"final_tcp_position":[0.48204,-0.11803,0.02598],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"phases":[{"n_steps":993.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","tcp_end":[0.3728,0.15021,0.06265],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.20117,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.02499,"phase_name":"make_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","subtask_id":"make_contact","tcp_end":[0.40751,0.05946,0.04294],"tcp_start":[0.3728,0.15021,0.06265],"tcp_to_object_dist_end":0.10218,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49893,-0.15476,0.02485],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.00488,"object_to_goal_dist_start":0.12843,"object_z_max":0.02588,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_to_goal","tcp_end":[0.48204,-0.11803,0.02598],"tcp_start":[0.40751,0.05946,0.04294],"tcp_to_object_dist_end":0.04044,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.89286,"average_solve_count":112.0,"average_success_count":112.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_distance":0.14389,"approach_behind.approach_height":0.06453,"approach_behind.approach_speed":0.14226,"make_contact.contact_distance":0.06223,"make_contact.contact_force_threshold":5.56181,"make_contact.contact_speed":0.05996,"push_to_goal.push_distance":0.32088,"push_to_goal.push_speed":0.15477,"push_to_goal.push_time":10.70175},"optimized_scores":{"best_composite_score":0.43098,"best_fitness_score":0.91098,"best_task_score":0.89144},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1539.0,"contact_point_centroid":[0.54776,-0.10274,-0.00013],"force_p95":37.86573,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":58.08394,"mean_force":9.1283,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.51667,-0.07947,0.03889]},{"body_a":"attachment","body_b":"push_box","contact_count":689.0,"contact_point_centroid":[0.53289,-0.08116,0.05557],"force_p95":26.04223,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":51.3754,"mean_force":10.21132,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.51828,-0.07425,0.03915]},{"body_a":"push_box","body_b":"link7","contact_count":272.0,"contact_point_centroid":[0.53748,-0.11625,0.06186],"force_p95":40.11648,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":46.65991,"mean_force":25.97419,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.49909,-0.13354,0.03487]},{"body_a":"world","body_b":"push_box","contact_count":3872.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.54627,0.06628,0.19252]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"make_contact","phase_type":"contact","tcp_position_centroid":[0.5745,0.08495,0.06872]}],"total_contact_groups":5},"final_pose_error":0.11319,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51713,-0.15315,0.02489],"final_tcp_position":[0.47848,-0.19279,0.02886],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"phases":[{"n_steps":968.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","tcp_end":[0.59312,0.13107,0.09068],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.15078,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.02499,"phase_name":"make_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","subtask_id":"make_contact","tcp_end":[0.55975,0.04026,0.05311],"tcp_start":[0.59312,0.13107,0.09068],"tcp_to_object_dist_end":0.04846,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51713,-0.15315,0.02489],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.01742,"object_to_goal_dist_start":0.16043,"object_z_max":0.03326,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_to_goal","tcp_end":[0.47848,-0.19279,0.02886],"tcp_start":[0.55975,0.04026,0.05311],"tcp_to_object_dist_end":0.0555,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.11538,"average_solve_count":78.0,"average_success_count":78.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_distance":0.06094,"approach_behind.approach_height":0.03003,"approach_behind.approach_speed":0.14093,"make_contact.contact_distance":0.0419,"make_contact.contact_force_threshold":6.98961,"make_contact.contact_speed":0.05699,"push_to_goal.push_distance":0.28488,"push_to_goal.push_speed":0.24075,"push_to_goal.push_time":4.75942},"optimized_scores":{"best_composite_score":0.98078,"best_fitness_score":0.96078,"best_task_score":0.95217},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1019.0,"contact_point_centroid":[0.54611,-0.09037,-0.00024],"force_p95":79.9065,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":135.90463,"mean_force":30.20479,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50946,-0.06857,0.03505]},{"body_a":"push_box","body_b":"link7","contact_count":387.0,"contact_point_centroid":[0.53855,-0.10862,0.05969],"force_p95":94.59525,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":124.17935,"mean_force":54.80022,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50107,-0.12429,0.0319]},{"body_a":"attachment","body_b":"push_box","contact_count":503.0,"contact_point_centroid":[0.52871,-0.0571,0.05607],"force_p95":52.90408,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":68.68498,"mean_force":26.06461,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.51232,-0.05204,0.03638]},{"body_a":"world","body_b":"push_box","contact_count":3392.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.52009,0.0456,0.17918]},{"body_a":"world","body_b":"push_box","contact_count":756.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"make_contact","phase_type":"contact","tcp_position_centroid":[0.53762,0.08254,0.05303]}],"total_contact_groups":5},"final_pose_error":0.01639,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50441,-0.14203,0.02531],"final_tcp_position":[0.48132,-0.22658,0.02166],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"phases":[{"n_steps":848.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","tcp_end":[0.54208,0.09162,0.06062],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.06548,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":189.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.02499,"phase_name":"make_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","subtask_id":"make_contact","tcp_end":[0.5355,0.07389,0.04869],"tcp_start":[0.54208,0.09162,0.06062],"tcp_to_object_dist_end":0.0439,"terminated_normally":true,"termination_reason":"force_exceeded"},{"n_steps":811.0,"n_steps_budget":840.0,"object_pos_end":[0.50441,-0.14203,0.02531],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.00911,"object_to_goal_dist_start":0.1905,"object_z_max":0.0383,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_to_goal","tcp_end":[0.48132,-0.22658,0.02166],"tcp_start":[0.5355,0.07389,0.04869],"tcp_to_object_dist_end":0.08772,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```