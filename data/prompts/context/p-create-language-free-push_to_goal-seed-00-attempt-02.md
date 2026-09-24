## Search State

- **Seed**: 0
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 2 | 0.2139 | 0.38 | ✅ accepted |
| 1 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | -0.2350 | 0.00 | ❌ rejected |
| 0 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 2 | 0.2121 | 0.38 | ✅ accepted |

**Proposal policy**: task_score is 0.38 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `79fe20ee7316d80bc617c84166fccacf882b4f96b2faf4b155be83e4f318b183`
- Frozen object start: [0.5164354024785746, -0.027625594348335558, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.5164354024785746, -0.027625594348335558, 0.025)
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
  frozen_object_start: [0.5164, -0.0276, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.5164354024785746, -0.027625594348335558, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [-0.0164, -0.1224, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: 79fe20ee7316d80bc617c84166fccacf882b4f96b2faf4b155be83e4f318b183

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
| `object` | offset from object initial position (0.5164354024785746, -0.027625594348335558, 0.025) | approach/contact targets near object start |
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

## Current Skill (Q=0.214) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
subtasks:
- id: pre_contact
  anchor: object
  offset:
  - 0.0
  - 0.025
  - 0.1
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
    entity: push_box
    offset:
    - 0.0
    - 0.025
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: pre_contact
- id: descend_1
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
    - 0.025
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  subtask_id: pre_contact
- id: push_1
  type: push
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.15
      axis: world_y
      mode: add_to_offset
      sign: negative
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: push_to_goal
- id: retract_1
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
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.025, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.025, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none
- **push_1** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_y, distance=0.15, mode=add_to_offset, sign=negative}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_speed: status=consumed; consumers=generator.speed (replace)
- **retract_1** (`retract`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.214
- **task_score** (E): 0.384
- **fitness_score**: 0.374  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.160

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1333 |
| descend_1 | 1.00 | 1.00 | 0.1498 |
| push_1 | 1.00 | 1.00 | 0.1366 |
| retract_1 | 1.00 | 1.00 | 0.0915 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.494, 0.023, 0.192) | (0.496, 0.001, 0.025)→(0.496, 0.001, 0.025) | 0.152→0.152 | 1.00 / 4.000 | 0.245 | 0.245 |
| descend_1 | descend | 1.00 / step_budget | (0.494, 0.023, 0.192)→(0.507, 0.027, 0.044) | (0.496, 0.001, 0.025)→(0.500, 0.002, 0.024) | 0.152→0.153 | 1.00 / 4.000 | 250.458 | 254.808 |
| push_1 | push | 1.00 / step_budget | (0.507, 0.027, 0.044)→(0.504, -0.109, 0.039) | (0.500, 0.002, 0.024)→(0.511, -0.064, 0.028) | 0.153→0.088 | 1.00 / 3.333 | 0.327 | 162.719 |
| retract_1 | retract | 1.00 / step_budget | (0.504, -0.109, 0.039)→(0.507, -0.066, 0.118) | (0.511, -0.064, 0.028)→(0.512, -0.057, 0.025) | 0.088→0.095 | 1.00 / 4.000 | 0.245 | 2.884 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.580
- lateral_force_integral: None
- approach_alignment: 0.732
- goal_progress: 0.568
- terminal_score: 0.568
- phase_score: 0.459
- phase_breakdown.pre_contact_score: 0.194
- phase_breakdown.push_to_goal_score: 0.572

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.502
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.568
- **Median Q (composite search score)**: 0.162
- **K-run variance**: 0.0083
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 11.0
- **Final σ (mean)**: 0.356


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `1efc9b29f7d131941a1bd842274a029ca5b2a2ff6a8656033ab118e32e2fae7d`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `6150c547b3cd2920ed4582689733d59ef61d18dc295ccd2a0d2317d1cf4e7764`; realized-scene SHA-256: `79fe20ee7316d80bc617c84166fccacf882b4f96b2faf4b155be83e4f318b183`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51644,-0.02763,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.01644,-0.12237,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.51644,-0.02763,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.89344,"average_solve_count":122.0,"average_success_count":122.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.06547,"push_1.push_speed":0.08502},"optimized_scores":{"best_composite_score":0.34227,"best_fitness_score":0.50227,"best_task_score":0.56783},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":132.0,"contact_point_centroid":[0.53058,-0.00549,0.04615],"force_p95":245.36298,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":246.17087,"mean_force":206.02968,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51953,-0.00167,0.04638]},{"body_a":"world","body_b":"push_box","contact_count":1010.0,"contact_point_centroid":[0.52023,-0.02463,-0.00025],"force_p95":187.4138,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":210.18405,"mean_force":27.3729,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51414,-0.00222,0.06426]},{"body_a":"attachment","body_b":"push_box","contact_count":785.0,"contact_point_centroid":[0.54216,-0.05122,0.04717],"force_p95":130.81135,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":155.57337,"mean_force":105.01155,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53232,-0.05522,0.04753]},{"body_a":"world","body_b":"push_box","contact_count":1662.0,"contact_point_centroid":[0.53482,-0.05736,-0.00052],"force_p95":111.65377,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":120.78208,"mean_force":50.24339,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53104,-0.06383,0.04614]},{"body_a":"world","body_b":"push_box","contact_count":2051.0,"contact_point_centroid":[0.51668,-0.09793,-2e-05],"force_p95":0.37526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.6889,"mean_force":0.25885,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51707,-0.12115,0.07648]},{"body_a":"attachment","body_b":"push_box","contact_count":35.0,"contact_point_centroid":[0.51972,-0.12273,0.0504],"force_p95":0.59068,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.46608,"mean_force":0.48757,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51925,-0.13466,0.05036]},{"body_a":"world","body_b":"push_box","contact_count":2560.0,"contact_point_centroid":[0.51644,-0.02763,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50502,-0.00124,0.19958]}],"total_contact_groups":7},"final_pose_error":0.01156,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51662,-0.09929,0.02499],"final_tcp_position":[0.5139,-0.10161,0.11403],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51644,-0.02763,0.025]},"peak_contact_force":246.17087,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":640.0,"n_steps_budget":1000.0,"object_pos_end":[0.51644,-0.02763,0.02499],"object_pos_start":[0.51644,-0.02763,0.025],"object_to_goal_dist_end":0.12347,"object_to_goal_dist_start":0.12347,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2560.0,"raw_peak_contact_force":0.24534,"subtask_id":"pre_contact","tcp_end":[0.51197,-0.00251,0.09915],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07843,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":285.0,"n_steps_budget":600.0,"object_pos_end":[0.52078,-0.02679,0.02429],"object_pos_start":[0.51644,-0.02763,0.02499],"object_to_goal_dist_end":0.12495,"object_to_goal_dist_start":0.12347,"object_z_max":0.02499,"peak_contact_force":241.06544,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1142.0,"raw_peak_contact_force":246.17087,"subtask_id":"pre_contact","tcp_end":[0.52795,-0.00123,0.04378],"tcp_start":[0.51197,-0.00251,0.09915],"tcp_to_object_dist_end":0.03293,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":899.0,"n_steps_budget":1000.0,"object_pos_end":[0.51684,-0.09925,0.02496],"object_pos_start":[0.52078,-0.02679,0.02429],"object_to_goal_dist_end":0.05348,"object_to_goal_dist_start":0.12495,"object_z_max":0.03631,"peak_contact_force":0.24549,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2447.0,"raw_peak_contact_force":155.57337,"subtask_id":"push_to_goal","tcp_end":[0.52399,-0.1438,0.03845],"tcp_start":[0.52795,-0.00123,0.04378],"tcp_to_object_dist_end":0.04709,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.51662,-0.09929,0.02499],"object_pos_start":[0.51684,-0.09925,0.02496],"object_to_goal_dist_end":0.05336,"object_to_goal_dist_start":0.05348,"object_z_max":0.02654,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2086.0,"raw_peak_contact_force":3.6889,"tcp_end":[0.5139,-0.10161,0.11403],"tcp_start":[0.52399,-0.1438,0.03845],"tcp_to_object_dist_end":0.08911,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `88c86884172a74f1f27b08fda534b767baf4d8d60d3fd4d782dec9555f4aae87`; realized-scene SHA-256: `258b33ff0697721ed1ba4810cf28d81707440dffd73b12c632f307c6591915c0`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50142,0.05406,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.00142,-0.20406,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.50142,0.05406,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.90769,"average_solve_count":130.0,"average_success_count":130.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.28121,"push_1.push_speed":0.09931},"optimized_scores":{"best_composite_score":0.16191,"best_fitness_score":0.32191,"best_task_score":0.34734},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":106.0,"contact_point_centroid":[0.51533,0.07598,0.04631],"force_p95":251.7982,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":252.14099,"mean_force":205.34612,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50428,0.07965,0.04665]},{"body_a":"world","body_b":"push_box","contact_count":3431.0,"contact_point_centroid":[0.50228,0.05481,-6e-05],"force_p95":24.74658,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":222.35083,"mean_force":6.63042,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49827,0.07473,0.16385]},{"body_a":"attachment","body_b":"push_box","contact_count":688.0,"contact_point_centroid":[0.52522,0.03114,0.04727],"force_p95":135.45699,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":158.76458,"mean_force":107.28101,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51545,0.02724,0.04762]},{"body_a":"world","body_b":"push_box","contact_count":1674.0,"contact_point_centroid":[0.51218,0.02443,-0.00047],"force_p95":116.1412,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":120.53775,"mean_force":44.69459,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51452,0.0232,0.04664]},{"body_a":"world","body_b":"push_box","contact_count":2054.0,"contact_point_centroid":[0.50037,-0.01585,-2e-05],"force_p95":0.37069,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.53921,"mean_force":0.25876,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50078,-0.03884,0.07716]},{"body_a":"attachment","body_b":"push_box","contact_count":28.0,"contact_point_centroid":[0.50416,-0.04072,0.0507],"force_p95":0.75579,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.19656,"mean_force":0.49702,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50312,-0.0526,0.0505]},{"body_a":"world","body_b":"push_box","contact_count":1504.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.24531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49885,0.0362,0.29891]}],"total_contact_groups":7},"final_pose_error":0.01114,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50009,-0.01682,0.02499],"final_tcp_position":[0.49759,-0.01955,0.11446],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50142,0.05406,0.025]},"peak_contact_force":252.14099,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":376.0,"n_steps_budget":600.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.025],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1504.0,"raw_peak_contact_force":0.24534,"subtask_id":"pre_contact","tcp_end":[0.49932,0.07115,0.30066],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.27621,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":884.0,"n_steps_budget":1000.0,"object_pos_end":[0.50526,0.05569,0.02429],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.20576,"object_to_goal_dist_start":0.20406,"object_z_max":0.02499,"peak_contact_force":246.94267,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3537.0,"raw_peak_contact_force":252.14099,"subtask_id":"pre_contact","tcp_end":[0.51147,0.08139,0.04376],"tcp_start":[0.49932,0.07115,0.30066],"tcp_to_object_dist_end":0.03284,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":792.0,"n_steps_budget":960.0,"object_pos_end":[0.50045,-0.01674,0.02485],"object_pos_start":[0.50526,0.05569,0.02429],"object_to_goal_dist_end":0.13326,"object_to_goal_dist_start":0.20576,"object_z_max":0.03619,"peak_contact_force":0.24762,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2362.0,"raw_peak_contact_force":158.76458,"subtask_id":"push_to_goal","tcp_end":[0.50772,-0.06071,0.03908],"tcp_start":[0.51147,0.08139,0.04376],"tcp_to_object_dist_end":0.04679,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.50009,-0.01682,0.02499],"object_pos_start":[0.50045,-0.01674,0.02485],"object_to_goal_dist_end":0.13318,"object_to_goal_dist_start":0.13326,"object_z_max":0.02628,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2082.0,"raw_peak_contact_force":2.53921,"tcp_end":[0.49759,-0.01955,0.11446],"tcp_start":[0.50772,-0.06071,0.03908],"tcp_to_object_dist_end":0.08955,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `a3cdbd735282928b0caf1de02aaaeed7f0a3d0a10908989412c558d20f3517fa`; realized-scene SHA-256: `8c36a5f9300ba3a57ccc09620ec8ba0a5276276ed83fb4303679e150911bfa14`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47139,-0.02418,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.02861,-0.12582,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.47139,-0.02418,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.67692,"average_solve_count":130.0,"average_success_count":130.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.14238,"push_1.push_speed":0.06123},"optimized_scores":{"best_composite_score":0.13737,"best_fitness_score":0.29737,"best_task_score":0.23812},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":105.0,"contact_point_centroid":[0.48586,-0.00208,0.04611],"force_p95":266.07833,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":266.1136,"mean_force":217.42283,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47484,0.00168,0.04633]},{"body_a":"world","body_b":"push_box","contact_count":1949.0,"contact_point_centroid":[0.47287,-0.02294,-0.00011],"force_p95":65.41566,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":226.24499,"mean_force":12.04166,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.46982,0.00086,0.10356]},{"body_a":"attachment","body_b":"push_box","contact_count":946.0,"contact_point_centroid":[0.49783,-0.04409,0.04706],"force_p95":138.61707,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":173.81813,"mean_force":114.13107,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48779,-0.0481,0.04738]},{"body_a":"world","body_b":"push_box","contact_count":1830.0,"contact_point_centroid":[0.49847,-0.04529,-0.00061],"force_p95":110.08905,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":130.27257,"mean_force":59.72985,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48737,-0.04812,0.04699]},{"body_a":"world","body_b":"push_box","contact_count":2342.0,"contact_point_centroid":[0.52021,-0.05495,-5e-05],"force_p95":0.45866,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.42485,"mean_force":0.26968,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49479,-0.09729,0.08414]},{"body_a":"world","body_b":"push_box","contact_count":1536.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4856,0.00033,0.23929]}],"total_contact_groups":6},"final_pose_error":0.01209,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52047,-0.05385,0.02499],"final_tcp_position":[0.51021,-0.07696,0.12451],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":266.1136,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":384.0,"n_steps_budget":870.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1536.0,"raw_peak_contact_force":0.24534,"subtask_id":"pre_contact","tcp_end":[0.47169,0.0007,0.17712],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.15416,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":513.0,"n_steps_budget":960.0,"object_pos_end":[0.4753,-0.02318,0.02427],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.1292,"object_to_goal_dist_start":0.12903,"object_z_max":0.02499,"peak_contact_force":263.36468,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2054.0,"raw_peak_contact_force":266.1136,"subtask_id":"pre_contact","tcp_end":[0.48256,0.00226,0.0432],"tcp_start":[0.47169,0.0007,0.17712],"tcp_to_object_dist_end":0.03253,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51561,-0.07461,0.03506],"object_pos_start":[0.4753,-0.02318,0.02427],"object_to_goal_dist_end":0.07764,"object_to_goal_dist_start":0.1292,"object_z_max":0.03511,"peak_contact_force":0.48652,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2776.0,"raw_peak_contact_force":173.81813,"subtask_id":"push_to_goal","tcp_end":[0.47979,-0.12238,0.03966],"tcp_start":[0.48256,0.00226,0.0432],"tcp_to_object_dist_end":0.05989,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":636.0,"n_steps_budget":720.0,"object_pos_end":[0.52047,-0.05385,0.02499],"object_pos_start":[0.51561,-0.07461,0.03506],"object_to_goal_dist_end":0.09831,"object_to_goal_dist_start":0.07764,"object_z_max":0.03506,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2342.0,"raw_peak_contact_force":2.42485,"tcp_end":[0.51021,-0.07696,0.12451],"tcp_start":[0.47979,-0.12238,0.03966],"tcp_to_object_dist_end":0.10268,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```