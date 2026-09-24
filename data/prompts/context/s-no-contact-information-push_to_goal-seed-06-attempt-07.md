## Search State

- **Seed**: 6
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.5644 | 0.95 | ✅ accepted |
| 6 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 5 | -0.2800 | 0.00 | ❌ rejected |
| 5 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.0722 | 0.54 | ❌ rejected |
| 4 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.0740 | 0.55 | ✅ accepted |
| 3 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.0116 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is near-perfect (0.95). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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
- Frozen realised-scene SHA-256: `5f9daa62d5a7a2b8a7116f2dfbb5f9857bb0d5d4b297d304a4e76a9a270e7ec7`
- Frozen object start: [0.5045797221766332, -0.01880749562239939, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.5045797221766332, -0.01880749562239939, 0.025)
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
  frozen_object_start: [0.5046, -0.0188, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.5045797221766332, -0.01880749562239939, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [-0.0046, -0.1312, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: 5f9daa62d5a7a2b8a7116f2dfbb5f9857bb0d5d4b297d304a4e76a9a270e7ec7

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.949, which indicates the subtask decomposition is already effective.
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
| `object` | offset from object initial position (0.5045797221766332, -0.01880749562239939, 0.025) | approach/contact targets near object start |
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

## Current Skill (Q=0.564) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: pre_contact
  anchor: object
  weight: 0.3
- id: push_complete
  target_entity: object
  metric: goal_progress
  weight: 0.7
phases:
- id: approach_object
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
    - 0.0
    offset_along_axis:
      distance: 0.03
      axis: task_goal_direction
      mode: add_to_offset
      sign: negative
    tolerance: 0.02
    orientation:
      mode: none
  parameters:
    lateral_offset_y:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: add
    speed:
      type: scalar
      range:
      - 0.03
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: pre_contact
- id: push_to_goal
  type: push
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: push_box
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.15
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
    orientation:
      mode: none
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: push_complete
- id: retract_after_push
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
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.03, mode=add_to_offset, sign=negative}, tolerance=0.02
  - orientation: mode=none
  - parameter_bindings:
    - lateral_offset_y: status=consumed; consumers=target.offset.y (add)
    - speed: status=consumed; consumers=generator.speed (replace)
- **push_to_goal** (`push`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.15, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=none
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
- **retract_after_push** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_height: status=consumed; consumers=target.offset.z (replace)

## Design Metrics

- **Composite score**: 0.564
- **task_score** (E): 0.949
- **fitness_score**: 0.844  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.280

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_object | 1.00 | 0.2689 |
| push_to_goal | 1.00 | 0.1781 |
| retract_after_push | 1.00 | 0.0542 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.497, 0.068, 0.043) | (0.500, 0.029, 0.025)→(0.500, 0.029, 0.025) | 0.180→0.179 |
| push_to_goal | push | 1.00 / step_budget | (0.497, 0.068, 0.043)→(0.497, -0.108, 0.023) | (0.500, 0.029, 0.025)→(0.507, -0.145, 0.026) | 0.179→0.012 |
| retract_after_push | retract | 1.00 / step_budget | (0.497, -0.108, 0.023)→(0.493, -0.107, 0.077) | (0.507, -0.145, 0.026)→(0.505, -0.146, 0.025) | 0.012→0.008 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.978
- approach_alignment: 0.709
- goal_progress: 0.978
- terminal_score: 0.978
- phase_score: 0.802
- phase_breakdown.push_complete_score: 0.965

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.872
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.978
- **Median Q (composite search score)**: 0.574
- **K-run variance**: 0.0008
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.356


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `acf3715aaa310bcc73047d49f01e71bc863ef036ae437b7dc851a0f6d3fe40ae`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `ec1d0331416d42e6883eeb3b72499fac99c0735b785eb70ece69dc94e8044fc3`; realized-scene SHA-256: `5f9daa62d5a7a2b8a7116f2dfbb5f9857bb0d5d4b297d304a4e76a9a270e7ec7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50458,-0.01881,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.00458,-0.13119,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.50458,-0.01881,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.44167,"average_solve_count":120.0,"average_success_count":120.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.lateral_offset_y":0.01094,"approach_object.speed":0.13945,"push_to_goal.push_distance":0.0992,"push_to_goal.push_speed":0.0481,"retract_after_push.retract_height":0.07782},"optimized_scores":{"best_composite_score":0.52711,"best_fitness_score":0.80711,"best_task_score":0.9062},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":348.0,"contact_point_centroid":[0.50845,-0.08342,-8e-05],"force_p95":18.63968,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":45.56086,"mean_force":3.83945,"phase_index":1.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.4982,-0.03445,0.03246]},{"body_a":"attachment","body_b":"push_box","contact_count":155.0,"contact_point_centroid":[0.50478,-0.05499,0.04425],"force_p95":33.52125,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":42.06288,"mean_force":6.51153,"phase_index":1.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.49784,-0.0431,0.03083]},{"body_a":"push_box","body_b":"link7","contact_count":14.0,"contact_point_centroid":[0.53472,-0.11063,0.05073],"force_p95":30.21314,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":31.55921,"mean_force":10.16669,"phase_index":1.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.49743,-0.09048,0.02379]},{"body_a":"world","body_b":"push_box","contact_count":723.0,"contact_point_centroid":[0.50681,-0.13997,-1e-05],"force_p95":0.27775,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.41238,"mean_force":0.26457,"phase_index":2.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.49455,-0.09833,0.05181]},{"body_a":"world","body_b":"push_box","contact_count":1944.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50021,0.00976,0.1734]}],"total_contact_groups":5},"final_pose_error":0.01976,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50724,-0.14004,0.02499],"final_tcp_position":[0.49412,-0.09797,0.08117],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"phases":[{"n_steps":486.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"pre_contact","tcp_end":[0.50162,0.01997,0.04423],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.04339,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":316.0,"n_steps_budget":1000.0,"object_pos_end":[0.50891,-0.1368,0.02513],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.01593,"object_to_goal_dist_start":0.13127,"object_z_max":0.02647,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_complete","tcp_end":[0.49765,-0.09845,0.02279],"tcp_start":[0.50162,0.01997,0.04423],"tcp_to_object_dist_end":0.04004,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":187.0,"n_steps_budget":600.0,"object_pos_end":[0.50724,-0.14004,0.02499],"object_pos_start":[0.50891,-0.1368,0.02513],"object_to_goal_dist_end":0.01231,"object_to_goal_dist_start":0.01593,"object_z_max":0.02513,"phase_name":"retract_after_push","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.49412,-0.09797,0.08117],"tcp_start":[0.49765,-0.09845,0.02279],"tcp_to_object_dist_end":0.07141,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `589e611c6c27578474525e3fd29be4fb5907d8bbd5d1ca44922bfd811e342c78`; realized-scene SHA-256: `c8d09cd43835becf8e5eb4413394fad8627e4bf404e9e7726e9f380b60e09752`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51501,0.04767,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.01501,-0.19767,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.51501,0.04767,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.47312,"average_solve_count":186.0,"average_success_count":186.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.lateral_offset_y":0.01875,"approach_object.speed":0.07609,"push_to_goal.push_distance":0.18753,"push_to_goal.push_speed":0.05252,"retract_after_push.retract_height":0.06868},"optimized_scores":{"best_composite_score":0.57396,"best_fitness_score":0.85396,"best_task_score":0.96406},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":401.0,"contact_point_centroid":[0.51586,-0.04173,0.04695],"force_p95":67.31199,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":82.13764,"mean_force":20.22056,"phase_index":1.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50323,-0.03103,0.02902]},{"body_a":"world","body_b":"push_box","contact_count":654.0,"contact_point_centroid":[0.52314,-0.06724,-0.00012],"force_p95":44.69091,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":72.05499,"mean_force":16.40716,"phase_index":1.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50419,-0.01467,0.0305]},{"body_a":"push_box","body_b":"link7","contact_count":10.0,"contact_point_centroid":[0.53267,-0.14529,0.05403],"force_p95":65.58387,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":68.53835,"mean_force":29.7588,"phase_index":2.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.50069,-0.12002,0.02403]},{"body_a":"push_box","body_b":"link7","contact_count":167.0,"contact_point_centroid":[0.53085,-0.09981,0.05601],"force_p95":57.23007,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":64.22384,"mean_force":22.89073,"phase_index":1.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50105,-0.08363,0.02523]},{"body_a":"attachment","body_b":"push_box","contact_count":49.0,"contact_point_centroid":[0.51233,-0.12948,0.05147],"force_p95":33.87031,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":43.86409,"mean_force":4.79323,"phase_index":2.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.49901,-0.11962,0.03613]},{"body_a":"world","body_b":"push_box","contact_count":375.0,"contact_point_centroid":[0.51306,-0.16528,-0.00012],"force_p95":1.05986,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":31.6406,"mean_force":0.82313,"phase_index":2.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.49809,-0.11927,0.05214]},{"body_a":"world","body_b":"push_box","contact_count":2184.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50534,0.04299,0.17237]}],"total_contact_groups":7},"final_pose_error":0.01978,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50696,-0.1515,0.02485],"final_tcp_position":[0.49758,-0.11903,0.07286],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"phases":[{"n_steps":546.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"pre_contact","tcp_end":[0.5123,0.08785,0.04236],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.04386,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":573.0,"n_steps_budget":1000.0,"object_pos_end":[0.51076,-0.15537,0.0285],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.01253,"object_to_goal_dist_start":0.19823,"object_z_max":0.03255,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_complete","tcp_end":[0.50102,-0.11963,0.02365],"tcp_start":[0.5123,0.08785,0.04236],"tcp_to_object_dist_end":0.03737,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":160.0,"n_steps_budget":600.0,"object_pos_end":[0.50696,-0.1515,0.02485],"object_pos_start":[0.51076,-0.15537,0.0285],"object_to_goal_dist_end":0.00712,"object_to_goal_dist_start":0.01253,"object_z_max":0.03037,"phase_name":"retract_after_push","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.49758,-0.11903,0.07286],"tcp_start":[0.50102,-0.11963,0.02365],"tcp_to_object_dist_end":0.05871,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `f2c9c63f0d9eca1b3ff8bf951759f6a3adee73f9f65e1cd3613c5e9d1203ebcc`; realized-scene SHA-256: `f3b8ea82cefd9504be10e2d47c49094a836a703404c06bdee3b01a27a59bf7be`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47924,0.05847,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.02076,-0.20847,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.47924,0.05847,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.67176,"average_solve_count":131.0,"average_success_count":131.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.lateral_offset_y":0.01702,"approach_object.speed":0.1395,"push_to_goal.push_distance":0.18363,"push_to_goal.push_speed":0.06886,"retract_after_push.retract_height":0.07417},"optimized_scores":{"best_composite_score":0.59223,"best_fitness_score":0.87223,"best_task_score":0.97819},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":15.0,"contact_point_centroid":[0.48029,0.08337,0.04919],"force_p95":131.55823,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":131.61047,"mean_force":105.8808,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.47615,0.09363,0.05073]},{"body_a":"world","body_b":"push_box","contact_count":2106.0,"contact_point_centroid":[0.47936,0.05858,-1e-05],"force_p95":0.24533,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":68.07181,"mean_force":1.00096,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48702,0.04727,0.17208]},{"body_a":"attachment","body_b":"push_box","contact_count":354.0,"contact_point_centroid":[0.48978,-0.0202,0.04204],"force_p95":42.8629,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":63.07271,"mean_force":9.35687,"phase_index":1.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.48288,-0.0085,0.03013]},{"body_a":"world","body_b":"push_box","contact_count":614.0,"contact_point_centroid":[0.49207,-0.04473,-0.0001],"force_p95":22.88377,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":33.99131,"mean_force":5.91466,"phase_index":1.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.48184,0.00424,0.03143]},{"body_a":"world","body_b":"push_box","contact_count":674.0,"contact_point_centroid":[0.49966,-0.14538,-2e-05],"force_p95":0.26102,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":29.85103,"mean_force":0.30044,"phase_index":2.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.4892,-0.10579,0.04855]},{"body_a":"push_box","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.52512,-0.12007,0.0502],"force_p95":26.64458,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.49884,"mean_force":10.3813,"phase_index":2.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.49185,-0.10649,0.0216]},{"body_a":"push_box","body_b":"link7","contact_count":17.0,"contact_point_centroid":[0.52402,-0.0987,0.0516],"force_p95":3.69311,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.26591,"mean_force":1.31779,"phase_index":1.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.4899,-0.08327,0.02356]},{"body_a":"attachment","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.49202,-0.11805,0.02162],"force_p95":1.19036,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.28392,"mean_force":0.54406,"phase_index":2.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.49207,-0.10614,0.02159]}],"total_contact_groups":8},"final_pose_error":0.01995,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49987,-0.14543,0.02499],"final_tcp_position":[0.48874,-0.1054,0.07616],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"phases":[{"n_steps":529.0,"n_steps_budget":1000.0,"object_pos_end":[0.47933,0.05791,0.02477],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.20893,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"pre_contact","tcp_end":[0.47601,0.09757,0.04315],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.04384,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":536.0,"n_steps_budget":1000.0,"object_pos_end":[0.50016,-0.14261,0.02513],"object_pos_start":[0.47933,0.05791,0.02477],"object_to_goal_dist_end":0.0074,"object_to_goal_dist_start":0.20893,"object_z_max":0.02724,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_complete","tcp_end":[0.49215,-0.1059,0.02163],"tcp_start":[0.47601,0.09757,0.04315],"tcp_to_object_dist_end":0.03773,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":173.0,"n_steps_budget":600.0,"object_pos_end":[0.49987,-0.14543,0.02499],"object_pos_start":[0.50016,-0.14261,0.02513],"object_to_goal_dist_end":0.00457,"object_to_goal_dist_start":0.0074,"object_z_max":0.02514,"phase_name":"retract_after_push","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.48874,-0.1054,0.07616],"tcp_start":[0.49215,-0.1059,0.02163],"tcp_to_object_dist_end":0.06591,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```