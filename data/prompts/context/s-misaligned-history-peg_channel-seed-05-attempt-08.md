## Search State

- **Seed**: 5
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → descend → push → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | force_exceeded | pose_tolerance | 10  | 0.1461 | 0.22 | ❌ rejected |
| 7 | approach → descend → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 7  | -0.3118 | 0.00 | ❌ rejected |
| 6 | approach → descend → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 11  | 0.1447 | 0.22 | ✅ accepted |
| 5 | approach → descend → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 7  | -0.4496 | 0.05 | ❌ rejected |
| 4 | approach → descend → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 10  | -0.1272 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.00 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

- Task name: peg_channel
- Frozen realised-scene SHA-256: `ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e`
- Frozen object start: [0.5244002338996304, 0.1046352631789195, 0.04]
- Frozen task target: [0.5244002338996304, -0.05536473682108051, 0.04]
- Goal object position: (0.5244002338996304, -0.05536473682108051, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5244002338996304, 0.1046352631789195, 0.04)
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.5
- Force limit: 40.0 N
- Peg body: `peg`
- Channel axis: `(0.0, -1.0, 0.0)` — use `impedance_control` to absorb lateral wall forces
- Robot initial TCP position: (0.5, 0.2, 0.3)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **insertion depth × lateral alignment (axial progress penalised by wall deviation)**

## Scene Entities

robot:
  model: panda_pusher
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5, 0.2, 0.3]
objects:
  - name: peg
    role: manipulated_object
    dynamics: free
    geometry: cylinder
    radius_m: 0.018
    half_length_m: 0.025
  - name: channel_structure
    role: fixture
    dynamics: static
    geometry: two_parallel_walls
    inner_gap_m: 0.05
    wall_thickness_m: 0.03
    wall_height_m: 0.05
task_landmarks:
  frozen_object_start: [0.5244, 0.1046, 0.04]
  frozen_task_target: [0.5244, -0.0554, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5244002338996304, 0.1046352631789195, 0.04]}
  frozen_targets: {'channel_exit': [0.5244002338996304, -0.05536473682108051, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e

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
| `object` | offset from object initial position (0.5244002338996304, 0.1046352631789195, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5244002338996304, -0.05536473682108051, 0.04) | final destination targets |
| `fixture` | offset from fixture pose (0.54, 0.0, 0.035) | approach/contact targets near fixture |

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

## Current Skill (Q=-0.127) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: approach_peg
  anchor: object
  offset:
  - 0.0
  - 0.05
  - 0.015
  weight: 0.3
- id: push_to_goal
  target_entity: object
  metric: goal_progress
  weight: 0.7
phases:
- id: approach_1
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.05
    - 0.08
    tolerance: 0.01
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: channel_axis
      tolerance: 0.1
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.04
      - 0.12
      default: 0.08
      binds_to:
      - path: target.offset.z
        mode: replace
    arc_height:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.arc_height
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: approach_peg
- id: descend_to_contact
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.05
    - 0.015
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_height:
      type: scalar
      range:
      - 0.0
      - 0.04
      default: 0.015
      binds_to:
      - path: target.offset.z
        mode: replace
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.06
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: approach_peg
- id: push_along_channel
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: force_exceeded
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.16
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.1
      - 0.2
      default: 0.16
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_force_threshold:
      type: scalar
      range:
      - 30.0
      - 39.0
      default: 36.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: push_to_goal
- id: retract_tcp
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
  retries:
    max_attempts: 0
    strategy: repeat

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.05, 0.08], tolerance=0.01
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
  - retries: max_attempts=0, strategy=repeat
- **descend_to_contact** (`descend`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.05, 0.015], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_height: status=consumed; consumers=target.offset.z (replace)
    - descend_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat
- **push_along_channel** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.16, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat
- **retract_tcp** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings: none
  - retries: max_attempts=0, strategy=repeat

## Design Metrics

- **Composite score**: -0.127
- **task_score** (E): 0.000
- **fitness_score**: 0.129  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.590

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2038 |
| descend_to_contact | 0.67 | 1.00 | 0.0489 |
| lateral_align | 1.00 | 1.00 | 0.0080 |
| push_along_channel | 1.00 | 1.00 | 0.0001 |
| retract_tcp | 1.00 | 1.00 | 0.0804 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.510, 0.153, 0.103) | (0.512, 0.095, 0.040)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 1.000 | 0.541 | 2.488 |
| descend_to_contact | descend | 0.67 / force_exceeded | (0.510, 0.153, 0.103)→(0.504, 0.145, 0.056) | (0.504, 0.095, 0.034)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 1.667 | 59.143 | 59.143 |
| lateral_align | push | 1.00 / step_budget | (0.504, 0.145, 0.056)→(0.496, 0.144, 0.055) | (0.504, 0.095, 0.034)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 2.000 | 76.302 | 107.781 |
| push_along_channel | push | 1.00 / force_exceeded | (0.496, 0.144, 0.055)→(0.496, 0.144, 0.055) | (0.504, 0.095, 0.034)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 2.000 | 74.362 | 74.362 |
| retract_tcp | retract | 1.00 / step_budget | (0.496, 0.144, 0.055)→(0.494, 0.143, 0.136) | (0.504, 0.095, 0.034)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 1.000 | 0.533 | 133.957 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.000
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.000
- phase_score: 0.228
- phase_breakdown.approach_peg_score: 0.759
- phase_breakdown.push_to_goal_score: 0.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.137
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.000
- **Median Q (composite search score)**: -0.070
- **K-run variance**: 0.0087
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.345


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `9b36d26f861d7a613dfb3d8c86d70470e42095a430c2befa4bd6e530468a8a7e`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `2af86d8f59685db6584febc0596b9044223ae39cea3120c112c665a54a1c4732`; realized-scene SHA-256: `ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5244,0.10464,0.04]},{"name":"goal","value":[0.5244,-0.05536,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.5244,0.10464,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.5244,-0.05536,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.51887,"average_solve_count":106.0,"average_success_count":106.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.05684,"approach_1.arc_height":0.08687,"descend_to_contact.descend_force_threshold":6.96435,"descend_to_contact.descend_height":0.0001,"descend_to_contact.descend_speed":0.04818,"lateral_align.align_distance":0.01017,"lateral_align.align_speed":0.03803,"push_along_channel.push_distance":0.1486,"push_along_channel.push_force_threshold":34.98619,"push_along_channel.push_speed":0.01996},"optimized_scores":{"best_composite_score":-0.06967,"best_fitness_score":0.12033,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.51103,0.2181,-8e-05],"force_p95":110.79877,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":110.79877,"mean_force":110.79877,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.50986,0.1564,0.05453]},{"body_a":"world","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.5056,0.21611,-4e-05],"force_p95":94.63595,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":101.24739,"mean_force":62.82647,"phase_index":4.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.50413,0.15457,0.05477]},{"body_a":"world","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.50573,0.21612,-3e-05],"force_p95":90.58084,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":90.58084,"mean_force":90.58084,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50424,0.15457,0.05478]},{"body_a":"world","body_b":"link7","contact_count":116.0,"contact_point_centroid":[0.50857,0.21705,-7e-05],"force_p95":72.40583,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":78.89754,"mean_force":62.06639,"phase_index":2.0,"phase_name":"lateral_align","phase_type":"push","tcp_position_centroid":[0.5072,0.15543,0.05463]},{"body_a":"peg","body_b":"channel_base_body","contact_count":869.0,"contact_point_centroid":[0.50572,0.10468,0.00938],"force_p95":0.57571,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.55936,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50928,0.23258,0.17858]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50571,0.22032,0.29152]},{"body_a":"peg","body_b":"channel_base_body","contact_count":176.0,"contact_point_centroid":[0.5059,0.10424,0.00939],"force_p95":0.57572,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57577,"mean_force":0.54631,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.51556,0.1593,0.07361]},{"body_a":"peg","body_b":"channel_base_body","contact_count":124.0,"contact_point_centroid":[0.50602,0.10521,0.00939],"force_p95":0.57571,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57573,"mean_force":0.54627,"phase_index":2.0,"phase_name":"lateral_align","phase_type":"push","tcp_position_centroid":[0.50717,0.15542,0.05464]},{"body_a":"peg","body_b":"channel_base_body","contact_count":252.0,"contact_point_centroid":[0.50576,0.10439,0.00939],"force_p95":0.5757,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57571,"mean_force":0.54638,"phase_index":4.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.50212,0.15326,0.09427]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.5215,0.09567,0.00939],"force_p95":0.54213,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54213,"mean_force":0.54213,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50424,0.15457,0.05478]}],"total_contact_groups":10},"final_pose_error":0.01972,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50582,0.10466,0.03384],"final_tcp_position":[0.50194,0.15313,0.13522],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":110.79877,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":896.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.10464,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18484,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.54106,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":901.0,"raw_peak_contact_force":3.33087,"subtask_id":"approach_peg","tcp_end":[0.52152,0.16287,0.09196],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08373,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":176.0,"n_steps_budget":810.0,"object_pos_end":[0.50583,0.10466,0.03384],"object_pos_start":[0.50599,0.10464,0.03384],"object_to_goal_dist_end":0.18486,"object_to_goal_dist_start":0.18484,"object_z_max":0.03384,"peak_contact_force":110.79877,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":177.0,"raw_peak_contact_force":110.79877,"subtask_id":"approach_peg","tcp_end":[0.50981,0.15638,0.05435],"tcp_start":[0.52152,0.16287,0.09196],"tcp_to_object_dist_end":0.05578,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":124.0,"n_steps_budget":600.0,"object_pos_end":[0.50598,0.1046,0.03384],"object_pos_start":[0.50583,0.10466,0.03384],"object_to_goal_dist_end":0.1848,"object_to_goal_dist_start":0.18486,"object_z_max":0.03384,"peak_contact_force":51.15221,"phase_name":"lateral_align","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":240.0,"raw_peak_contact_force":78.89754,"subtask_id":"approach_peg","tcp_end":[0.50424,0.15457,0.05478],"tcp_start":[0.50981,0.15638,0.05435],"tcp_to_object_dist_end":0.05421,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50595,0.10457,0.03384],"object_pos_start":[0.50598,0.1046,0.03384],"object_to_goal_dist_end":0.18477,"object_to_goal_dist_start":0.1848,"object_z_max":0.03384,"peak_contact_force":90.58084,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2.0,"raw_peak_contact_force":90.58084,"subtask_id":"push_to_goal","tcp_end":[0.50419,0.15457,0.05476],"tcp_start":[0.50424,0.15457,0.05478],"tcp_to_object_dist_end":0.05423,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":252.0,"n_steps_budget":630.0,"object_pos_end":[0.50582,0.10466,0.03384],"object_pos_start":[0.50595,0.10457,0.03384],"object_to_goal_dist_end":0.18485,"object_to_goal_dist_start":0.18477,"object_z_max":0.03384,"peak_contact_force":0.54519,"phase_name":"retract_tcp","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":256.0,"raw_peak_contact_force":101.24739,"tcp_end":[0.50194,0.15313,0.13522],"tcp_start":[0.50419,0.15457,0.05476],"tcp_to_object_dist_end":0.11244,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `314cefd2153cfe84bc0d0d2dfbeb7f4daf8feaf5f2c7ce7d396802b52a157f39`; realized-scene SHA-256: `07dc0764c781629358e2f97446117d9c410d14c078397be91277b4276116a1de`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50305,0.06746,0.04]},{"name":"goal","value":[0.50305,-0.09254,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.50305,0.06746,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.50305,-0.09254,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.42857,"average_solve_count":126.0,"average_success_count":126.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.07193,"approach_1.arc_height":0.06586,"descend_to_contact.descend_force_threshold":7.63687,"descend_to_contact.descend_height":0.02133,"descend_to_contact.descend_speed":0.03452,"lateral_align.align_distance":0.03588,"lateral_align.align_speed":0.03198,"push_along_channel.push_distance":0.12152,"push_along_channel.push_force_threshold":37.25673,"push_along_channel.push_speed":0.01004},"optimized_scores":{"best_composite_score":-0.25858,"best_fitness_score":0.13142,"best_task_score":0.0002},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":22.0,"contact_point_centroid":[0.47497,0.12,0.05804],"force_p95":200.43984,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":203.30438,"mean_force":120.95915,"phase_index":4.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.48736,0.11735,0.05827]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":390.0,"contact_point_centroid":[0.47495,0.11996,0.05578],"force_p95":124.33986,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":145.45776,"mean_force":112.63539,"phase_index":2.0,"phase_name":"lateral_align","phase_type":"push","tcp_position_centroid":[0.48715,0.11622,0.05586]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":5.0,"contact_point_centroid":[0.47493,0.11999,0.05664],"force_p95":44.33043,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":46.2787,"mean_force":28.74948,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.48731,0.11705,0.05674]},{"body_a":"world","body_b":"link7","contact_count":20.0,"contact_point_centroid":[0.48931,0.17726,-1e-05],"force_p95":34.23636,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":35.66967,"mean_force":22.96006,"phase_index":2.0,"phase_name":"lateral_align","phase_type":"push","tcp_position_centroid":[0.48851,0.1157,0.05483]},{"body_a":"peg","body_b":"channel_base_body","contact_count":792.0,"contact_point_centroid":[0.50302,0.06746,0.00935],"force_p95":0.5534,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.55751,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49742,0.20011,0.1835]},{"body_a":"peg","body_b":"channel_base_body","contact_count":270.0,"contact_point_centroid":[0.50306,0.06746,0.00938],"force_p95":0.55058,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55079,"mean_force":0.54664,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.49909,0.12139,0.08308]},{"body_a":"peg","body_b":"channel_base_body","contact_count":484.0,"contact_point_centroid":[0.5031,0.0674,0.00938],"force_p95":0.55056,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55069,"mean_force":0.54664,"phase_index":2.0,"phase_name":"lateral_align","phase_type":"push","tcp_position_centroid":[0.48825,0.11619,0.05585]},{"body_a":"peg","body_b":"channel_base_body","contact_count":252.0,"contact_point_centroid":[0.50305,0.06745,0.00938],"force_p95":0.55055,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5506,"mean_force":0.54665,"phase_index":4.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.48566,0.11622,0.09431]},{"body_a":"peg","body_b":"channel_base_body","contact_count":5.0,"contact_point_centroid":[0.5066,0.07733,0.00938],"force_p95":0.54995,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55059,"mean_force":0.54654,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.48731,0.11705,0.05674]}],"total_contact_groups":9},"final_pose_error":0.01986,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50307,0.06743,0.0338],"final_tcp_position":[0.48516,0.11576,0.13692],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":203.30438,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":808.0,"n_steps_budget":1000.0,"object_pos_end":[0.50306,0.0675,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14766,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.55072,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":792.0,"raw_peak_contact_force":2.06903,"subtask_id":"approach_peg","tcp_end":[0.50043,0.12632,0.10817],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09486,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":270.0,"n_steps_budget":990.0,"object_pos_end":[0.50306,0.0675,0.0338],"object_pos_start":[0.50306,0.0675,0.0338],"object_to_goal_dist_end":0.14766,"object_to_goal_dist_start":0.14766,"object_z_max":0.0338,"peak_contact_force":0.55048,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":270.0,"raw_peak_contact_force":0.55079,"subtask_id":"approach_peg","tcp_end":[0.4995,0.11718,0.05849],"tcp_start":[0.50043,0.12632,0.10817],"tcp_to_object_dist_end":0.05559,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":484.0,"n_steps_budget":720.0,"object_pos_end":[0.50301,0.06748,0.0338],"object_pos_start":[0.50306,0.0675,0.0338],"object_to_goal_dist_end":0.14764,"object_to_goal_dist_start":0.14766,"object_z_max":0.0338,"peak_contact_force":118.72535,"phase_name":"lateral_align","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":894.0,"raw_peak_contact_force":145.45776,"subtask_id":"approach_peg","tcp_end":[0.48735,0.11707,0.0568],"tcp_start":[0.4995,0.11718,0.05849],"tcp_to_object_dist_end":0.05686,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":5.0,"n_steps_budget":1000.0,"object_pos_end":[0.50307,0.06743,0.0338],"object_pos_start":[0.50301,0.06748,0.0338],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14764,"object_z_max":0.0338,"peak_contact_force":46.2787,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":10.0,"raw_peak_contact_force":46.2787,"subtask_id":"push_to_goal","tcp_end":[0.48727,0.11698,0.05663],"tcp_start":[0.48735,0.11707,0.0568],"tcp_to_object_dist_end":0.05681,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":252.0,"n_steps_budget":630.0,"object_pos_end":[0.50307,0.06743,0.0338],"object_pos_start":[0.50307,0.06743,0.0338],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14759,"object_z_max":0.0338,"peak_contact_force":0.54556,"phase_name":"retract_tcp","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":274.0,"raw_peak_contact_force":203.30438,"tcp_end":[0.48516,0.11576,0.13692],"tcp_start":[0.48727,0.11698,0.05663],"tcp_to_object_dist_end":0.11529,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `7acce370299b32aeef0e4239da3e97eae076cb9602edead185a6cf774ee0bc4e`; realized-scene SHA-256: `d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51001,0.11178,0.04]},{"name":"goal","value":[0.51001,-0.04822,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.51001,0.11178,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.51001,-0.04822,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.68868,"average_solve_count":106.0,"average_success_count":106.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.07571,"approach_1.arc_height":0.09205,"descend_to_contact.descend_force_threshold":2.13948,"descend_to_contact.descend_height":0.00502,"descend_to_contact.descend_speed":0.05173,"lateral_align.align_distance":0.01005,"lateral_align.align_speed":0.04461,"push_along_channel.push_distance":0.13938,"push_along_channel.push_force_threshold":31.82941,"push_along_channel.push_speed":0.05703},"optimized_scores":{"best_composite_score":-0.0534,"best_fitness_score":0.1366,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link7","contact_count":115.0,"contact_point_centroid":[0.50062,0.22272,-5e-05],"force_p95":71.86845,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":98.98755,"mean_force":61.99421,"phase_index":2.0,"phase_name":"lateral_align","phase_type":"push","tcp_position_centroid":[0.49921,0.16111,0.05467]},{"body_a":"world","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.49772,0.2218,-3e-05],"force_p95":91.35454,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":97.3201,"mean_force":62.32203,"phase_index":4.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.49621,0.16027,0.05479]},{"body_a":"world","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.49782,0.22182,-4e-05],"force_p95":86.22532,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":86.22532,"mean_force":86.22532,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49629,0.16028,0.05478]},{"body_a":"world","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.50294,0.22383,-6e-05],"force_p95":66.07884,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":66.07884,"mean_force":66.07884,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.50175,0.16214,0.05458]},{"body_a":"peg","body_b":"channel_base_body","contact_count":573.0,"contact_point_centroid":[0.50357,0.11163,0.00939],"force_p95":0.61541,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.55627,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50342,0.23624,0.15553]},{"body_a":"peg","body_b":"channel_base_body","contact_count":250.0,"contact_point_centroid":[0.5036,0.11167,0.00939],"force_p95":0.59954,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64296,"mean_force":0.54491,"phase_index":4.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.49423,0.15894,0.09422]},{"body_a":"peg","body_b":"channel_base_body","contact_count":124.0,"contact_point_centroid":[0.50334,0.11171,0.00941],"force_p95":0.59548,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63475,"mean_force":0.54411,"phase_index":2.0,"phase_name":"lateral_align","phase_type":"push","tcp_position_centroid":[0.49921,0.1611,0.05468]},{"body_a":"peg","body_b":"channel_base_body","contact_count":271.0,"contact_point_centroid":[0.50374,0.11164,0.00939],"force_p95":0.59882,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63287,"mean_force":0.5455,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.50395,0.16549,0.08211]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.52085,0.11726,0.0094],"force_p95":0.55744,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55744,"mean_force":0.55744,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49629,0.16028,0.05478]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50425,0.2059,0.29996]}],"total_contact_groups":10},"final_pose_error":0.01985,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50373,0.11178,0.03384],"final_tcp_position":[0.49404,0.15881,0.1351],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":98.98755,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":595.0,"n_steps_budget":1000.0,"object_pos_end":[0.50372,0.11175,0.03391],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19188,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.53101,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":589.0,"raw_peak_contact_force":2.06328,"subtask_id":"approach_peg","tcp_end":[0.50756,0.16975,0.10982],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09561,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":271.0,"n_steps_budget":870.0,"object_pos_end":[0.5037,0.11174,0.03381],"object_pos_start":[0.50372,0.11175,0.03391],"object_to_goal_dist_end":0.19188,"object_to_goal_dist_start":0.19188,"object_z_max":0.03391,"peak_contact_force":66.07884,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":272.0,"raw_peak_contact_force":66.07884,"subtask_id":"approach_peg","tcp_end":[0.50174,0.16213,0.0544],"tcp_start":[0.50756,0.16975,0.10982],"tcp_to_object_dist_end":0.05446,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":124.0,"n_steps_budget":600.0,"object_pos_end":[0.50377,0.11176,0.03383],"object_pos_start":[0.5037,0.11174,0.03381],"object_to_goal_dist_end":0.19189,"object_to_goal_dist_start":0.19188,"object_z_max":0.03389,"peak_contact_force":59.02703,"phase_name":"lateral_align","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":239.0,"raw_peak_contact_force":98.98755,"subtask_id":"approach_peg","tcp_end":[0.49629,0.16028,0.05478],"tcp_start":[0.50174,0.16213,0.0544],"tcp_to_object_dist_end":0.05338,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50377,0.11175,0.03383],"object_pos_start":[0.50377,0.11176,0.03383],"object_to_goal_dist_end":0.19189,"object_to_goal_dist_start":0.19189,"object_z_max":0.03383,"peak_contact_force":86.22532,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2.0,"raw_peak_contact_force":86.22532,"subtask_id":"push_to_goal","tcp_end":[0.49626,0.16028,0.05477],"tcp_start":[0.49629,0.16028,0.05478],"tcp_to_object_dist_end":0.05338,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":250.0,"n_steps_budget":630.0,"object_pos_end":[0.50373,0.11178,0.03384],"object_pos_start":[0.50377,0.11175,0.03383],"object_to_goal_dist_end":0.19192,"object_to_goal_dist_start":0.19189,"object_z_max":0.03386,"peak_contact_force":0.50917,"phase_name":"retract_tcp","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":254.0,"raw_peak_contact_force":97.3201,"tcp_end":[0.49404,0.15881,0.1351],"tcp_start":[0.49626,0.16028,0.05477],"tcp_to_object_dist_end":0.11206,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```