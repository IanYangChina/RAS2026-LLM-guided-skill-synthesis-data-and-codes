## Search State

- **Seed**: 6
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.5822 | 0.96 | ✅ accepted |
| 13 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | 0.0974 | 0.36 | ❌ rejected |
| 12 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | 0.1530 | 0.32 | ❌ rejected |
| 11 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.1977 | 0.36 | ❌ rejected |
| 10 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 5 | -0.2659 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is near-perfect (0.96). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.958, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.582) — your mutation base

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

- **Composite score**: 0.582
- **task_score** (E): 0.958
- **fitness_score**: 0.862  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.280

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_object | 1.00 | 0.2678 |
| push_to_goal | 1.00 | 0.2130 |
| retract_after_push | 1.00 | 0.0857 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.499, 0.067, 0.044) | (0.500, 0.029, 0.025)→(0.500, 0.028, 0.025) | 0.180→0.179 |
| push_to_goal | push | 1.00 / step_budget | (0.499, 0.067, 0.044)→(0.495, -0.145, 0.022) | (0.500, 0.028, 0.025)→(0.504, -0.145, 0.027) | 0.179→0.008 |
| retract_after_push | retract | 1.00 / step_budget | (0.495, -0.145, 0.022)→(0.492, -0.144, 0.108) | (0.504, -0.145, 0.027)→(0.503, -0.145, 0.025) | 0.008→0.008 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.989
- approach_alignment: 0.773
- goal_progress: 0.988
- terminal_score: 0.988
- phase_score: 0.810
- phase_breakdown.push_complete_score: 0.973

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.881
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.988
- **Median Q (composite search score)**: 0.595
- **K-run variance**: 0.0005
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.381


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.68217,"average_solve_count":129.0,"average_success_count":129.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.lateral_offset_y":0.00661,"approach_object.speed":0.10875,"push_to_goal.push_distance":0.10878,"push_to_goal.push_speed":0.06217,"retract_after_push.retract_height":0.13072},"optimized_scores":{"best_composite_score":0.59545,"best_fitness_score":0.87545,"best_task_score":0.97418},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":16.0,"contact_point_centroid":[0.50576,0.0057,0.04917],"force_p95":213.86853,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":243.23217,"mean_force":121.2197,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50228,0.01616,0.05004]},{"body_a":"world","body_b":"push_box","contact_count":1978.0,"contact_point_centroid":[0.50463,-0.01887,-1e-05],"force_p95":0.24533,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":140.54018,"mean_force":1.22932,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50019,0.00789,0.17312]},{"body_a":"attachment","body_b":"push_box","contact_count":229.0,"contact_point_centroid":[0.50139,-0.06445,0.03671],"force_p95":36.85082,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":58.3952,"mean_force":6.15863,"phase_index":1.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.49851,-0.05258,0.03067]},{"body_a":"world","body_b":"push_box","contact_count":397.0,"contact_point_centroid":[0.50071,-0.09407,-7e-05],"force_p95":17.70124,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":25.95773,"mean_force":4.03183,"phase_index":1.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.49874,-0.04815,0.03148]},{"body_a":"world","body_b":"push_box","contact_count":1310.0,"contact_point_centroid":[0.49639,-0.14901,-3e-05],"force_p95":0.48276,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.39517,"mean_force":0.26447,"phase_index":2.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.49414,-0.10923,0.07978]},{"body_a":"attachment","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.49682,-0.1218,0.02274],"force_p95":2.03257,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.05103,"mean_force":1.65394,"phase_index":2.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.49735,-0.10987,0.02252]}],"total_contact_groups":6},"final_pose_error":0.02,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49677,-0.14898,0.02499],"final_tcp_position":[0.4943,-0.1091,0.13355],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"phases":[{"n_steps":496.0,"n_steps_budget":1000.0,"object_pos_end":[0.50488,-0.02029,0.02504],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.12981,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"pre_contact","tcp_end":[0.50321,0.01768,0.04484],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.04285,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":334.0,"n_steps_budget":1000.0,"object_pos_end":[0.49811,-0.14663,0.02447],"object_pos_start":[0.50488,-0.02029,0.02504],"object_to_goal_dist_end":0.0039,"object_to_goal_dist_start":0.12981,"object_z_max":0.02618,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_complete","tcp_end":[0.49744,-0.10964,0.02257],"tcp_start":[0.50321,0.01768,0.04484],"tcp_to_object_dist_end":0.03704,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":346.0,"n_steps_budget":840.0,"object_pos_end":[0.49677,-0.14898,0.02499],"object_pos_start":[0.49811,-0.14663,0.02447],"object_to_goal_dist_end":0.00339,"object_to_goal_dist_start":0.0039,"object_z_max":0.02549,"phase_name":"retract_after_push","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.4943,-0.1091,0.13355],"tcp_start":[0.49744,-0.10964,0.02257],"tcp_to_object_dist_end":0.11568,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.32727,"average_solve_count":220.0,"average_success_count":220.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.lateral_offset_y":0.01582,"approach_object.speed":0.07463,"push_to_goal.push_distance":0.28208,"push_to_goal.push_speed":0.02454,"retract_after_push.retract_height":0.05134},"optimized_scores":{"best_composite_score":0.54996,"best_fitness_score":0.82996,"best_task_score":0.91328},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":14.0,"contact_point_centroid":[0.51636,0.0726,0.04917],"force_p95":170.85042,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":197.06886,"mean_force":106.64863,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51241,0.083,0.05027]},{"body_a":"push_box","body_b":"link7","contact_count":581.0,"contact_point_centroid":[0.54058,-0.08834,0.05917],"force_p95":122.29243,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":138.96218,"mean_force":63.70803,"phase_index":1.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50212,-0.09644,0.03169]},{"body_a":"world","body_b":"push_box","contact_count":1250.0,"contact_point_centroid":[0.54219,-0.07633,-0.0003],"force_p95":107.44661,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":137.01735,"mean_force":41.38706,"phase_index":1.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50381,-0.05409,0.03317]},{"body_a":"world","body_b":"push_box","contact_count":2167.0,"contact_point_centroid":[0.51503,0.04767,-1e-05],"force_p95":0.24532,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":118.04112,"mean_force":0.94035,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50533,0.04147,0.17309]},{"body_a":"attachment","body_b":"push_box","contact_count":671.0,"contact_point_centroid":[0.52237,-0.0525,0.05428],"force_p95":68.56143,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":83.61433,"mean_force":38.22061,"phase_index":1.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50421,-0.04878,0.03357]},{"body_a":"world","body_b":"push_box","contact_count":408.0,"contact_point_centroid":[0.51205,-0.13612,-0.00015],"force_p95":0.65889,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.31479,"mean_force":0.31362,"phase_index":2.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.48936,-0.21429,0.03856]}],"total_contact_groups":6},"final_pose_error":0.01975,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51247,-0.13817,0.02499],"final_tcp_position":[0.48884,-0.21375,0.05401],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"phases":[{"n_steps":547.0,"n_steps_budget":1000.0,"object_pos_end":[0.51486,0.04685,0.02483],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19741,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"pre_contact","tcp_end":[0.51343,0.08628,0.04303],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.04345,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":884.0,"n_steps_budget":1000.0,"object_pos_end":[0.51232,-0.14148,0.02668],"object_pos_start":[0.51486,0.04685,0.02483],"object_to_goal_dist_end":0.01507,"object_to_goal_dist_start":0.19741,"object_z_max":0.03676,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_complete","tcp_end":[0.49224,-0.21478,0.02209],"tcp_start":[0.51343,0.08628,0.04303],"tcp_to_object_dist_end":0.07614,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":116.0,"n_steps_budget":600.0,"object_pos_end":[0.51247,-0.13817,0.02499],"object_pos_start":[0.51232,-0.14148,0.02668],"object_to_goal_dist_end":0.01719,"object_to_goal_dist_start":0.01507,"object_z_max":0.02668,"phase_name":"retract_after_push","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.48884,-0.21375,0.05401],"tcp_start":[0.49224,-0.21478,0.02209],"tcp_to_object_dist_end":0.08434,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.38571,"average_solve_count":210.0,"average_success_count":210.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.lateral_offset_y":0.01271,"approach_object.speed":0.09683,"push_to_goal.push_distance":0.1879,"push_to_goal.push_speed":0.0368,"retract_after_push.retract_height":0.13364},"optimized_scores":{"best_composite_score":0.60113,"best_fitness_score":0.88113,"best_task_score":0.98763},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":41.0,"contact_point_centroid":[0.48533,0.08475,0.04733],"force_p95":268.01168,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":270.16146,"mean_force":180.60559,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.47805,0.09194,0.04939]},{"body_a":"world","body_b":"push_box","contact_count":2143.0,"contact_point_centroid":[0.47936,0.05927,-3e-05],"force_p95":0.24534,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":223.7589,"mean_force":3.71404,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48708,0.0452,0.17259]},{"body_a":"attachment","body_b":"push_box","contact_count":370.0,"contact_point_centroid":[0.49403,-0.02648,0.04461],"force_p95":59.64444,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":69.22081,"mean_force":16.34493,"phase_index":1.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.48564,-0.01486,0.03034]},{"body_a":"world","body_b":"push_box","contact_count":710.0,"contact_point_centroid":[0.49253,-0.05074,-0.00018],"force_p95":38.26809,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":69.19433,"mean_force":10.04607,"phase_index":1.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.48458,-0.00138,0.03161]},{"body_a":"push_box","body_b":"link7","contact_count":52.0,"contact_point_centroid":[0.52581,-0.12175,0.05198],"force_p95":33.14021,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":35.09381,"mean_force":17.05735,"phase_index":1.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.49284,-0.09897,0.02309]},{"body_a":"push_box","body_b":"link7","contact_count":6.0,"contact_point_centroid":[0.52596,-0.13508,0.05254],"force_p95":25.71237,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":30.61505,"mean_force":8.66064,"phase_index":2.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.49422,-0.10966,0.02282]},{"body_a":"attachment","body_b":"push_box","contact_count":23.0,"contact_point_centroid":[0.50891,-0.12058,0.05337],"force_p95":8.53261,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":25.03538,"mean_force":2.52893,"phase_index":2.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.49273,-0.10955,0.02942]},{"body_a":"world","body_b":"push_box","contact_count":1258.0,"contact_point_centroid":[0.49909,-0.14933,-3e-05],"force_p95":0.40968,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.83607,"mean_force":0.29066,"phase_index":2.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.49114,-0.10884,0.08446]}],"total_contact_groups":8},"final_pose_error":0.01988,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49856,-0.14785,0.02499],"final_tcp_position":[0.49136,-0.10877,0.13675],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"phases":[{"n_steps":553.0,"n_steps_budget":1000.0,"object_pos_end":[0.48005,0.05828,0.02411],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.20924,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"pre_contact","tcp_end":[0.4799,0.0961,0.04401],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.04273,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":570.0,"n_steps_budget":1000.0,"object_pos_end":[0.50205,-0.1466,0.02904],"object_pos_start":[0.48005,0.05828,0.02411],"object_to_goal_dist_end":0.00567,"object_to_goal_dist_start":0.20924,"object_z_max":0.029,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_complete","tcp_end":[0.49444,-0.10929,0.02274],"tcp_start":[0.4799,0.0961,0.04401],"tcp_to_object_dist_end":0.03859,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":351.0,"n_steps_budget":840.0,"object_pos_end":[0.49856,-0.14785,0.02499],"object_pos_start":[0.50205,-0.1466,0.02904],"object_to_goal_dist_end":0.00259,"object_to_goal_dist_start":0.00567,"object_z_max":0.02904,"phase_name":"retract_after_push","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.49136,-0.10877,0.13675],"tcp_start":[0.49444,-0.10929,0.02274],"tcp_to_object_dist_end":0.11861,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```