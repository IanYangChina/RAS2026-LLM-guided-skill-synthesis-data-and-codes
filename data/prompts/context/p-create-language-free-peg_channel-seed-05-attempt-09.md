## Search State

- **Seed**: 5
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → descend → push → push → retract → retract | linear_cartesian | linear_cartesian | impedance_motion | impedance_motion | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | impedance_control | position_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 9 | -0.3722 | 0.05 | ❌ rejected |
| 8 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.4605 | 0.76 | ✅ accepted |
| 7 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.0210 | 0.00 | ❌ rejected |
| 6 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 9 | -0.0607 | 0.01 | ❌ rejected |
| 5 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.2843 | 0.48 | ✅ accepted |

**Proposal policy**: task_score is 0.05 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.372) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: approach_peg
  anchor: object
  offset:
  - 0.0
  - 0.03
  - 0.06
  weight: 0.3
- id: descend_peg
  anchor: object
  offset:
  - 0.0
  - 0.02
  - 0.0
  weight: 0.2
- id: push_to_goal
  metric: goal_progress
  weight: 0.5
phases:
- id: approach_above
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.03
    - 0.06
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_peg
- id: descend_to_peg
  type: descend
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.02
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: descend_peg
- id: push_channel
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.18
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    tolerance: 0.015
    orientation:
      mode: keep_current
  parameters:
    insert_depth:
      type: scalar
      range:
      - 0.16
      - 0.2
      default: 0.18
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: push_to_goal
- id: retract_home
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: world
    offset:
    - 0.5
    - 0.2
    - 0.3
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_above** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.03, 0.06], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_peg** (`descend`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.02, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **push_channel** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.18, mode=add_to_offset, sign=positive}, tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - insert_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
- **retract_home** (`retract`)
  - target: source=yaml, anchor=world, offset=[0.5, 0.2, 0.3], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: -0.372
- **task_score** (E): 0.055
- **fitness_score**: 0.198  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.570

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above | 1.00 | 1.00 | 0.1958 |
| descend_to_contact | 0.00 | 1.00 | 0.0584 |
| seat_push | 1.00 | 1.00 | 0.0207 |
| push_channel | 0.00 | 1.00 | 0.0001 |
| release_contact | 1.00 | 1.00 | 0.0117 |
| retract_home | 1.00 | 1.00 | 0.2319 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.508, 0.132, 0.118) | (0.512, 0.095, 0.040)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 1.000 | 0.536 | 2.488 |
| descend_to_contact | descend | 0.00 / step_budget | (0.508, 0.132, 0.118)→(0.501, 0.116, 0.062) | (0.504, 0.095, 0.034)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 1.000 | 0.556 | 0.588 |
| seat_push | push | 1.00 / step_budget | (0.501, 0.116, 0.062)→(0.499, 0.096, 0.060) | (0.504, 0.095, 0.034)→(0.504, 0.084, 0.034) | 0.175→0.165 | 1.00 / 2.000 | 33.403 | 35.816 |
| push_channel | push | 0.00 / guard_failure | (0.499, 0.096, 0.060)→(0.499, 0.096, 0.060) | (0.504, 0.084, 0.034)→(0.504, 0.084, 0.034) | 0.165→0.165 | 1.00 / 2.000 | 43.462 | 47.819 |
| release_contact | retract | 1.00 / step_budget | (0.499, 0.096, 0.060)→(0.496, 0.099, 0.070) | (0.504, 0.084, 0.034)→(0.504, 0.084, 0.034) | 0.164→0.164 | 1.00 / 1.000 | 0.550 | 43.251 |
| retract_home | retract | 1.00 / step_budget | (0.496, 0.099, 0.070)→(0.498, 0.193, 0.281) | (0.504, 0.084, 0.034)→(0.504, 0.084, 0.034) | 0.164→0.164 | 1.00 / 1.000 | 0.548 | 0.565 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.073
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.073
- phase_score: 0.312
- phase_breakdown.approach_peg_score: 0.671
- phase_breakdown.push_to_goal_score: 0.001
- phase_breakdown.descend_peg_score: 0.887

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.216
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.073
- **Median Q (composite search score)**: -0.366
- **K-run variance**: 0.0003
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.401


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.63953,"average_solve_count":344.0,"average_success_count":344.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.speed":0.04736,"descend_to_contact.contact_force_threshold":3.69917,"descend_to_contact.descend_speed":0.02084,"push_channel.insert_depth":0.18744,"push_channel.push_speed":0.02177,"release_contact.release_speed":0.028,"retract_home.speed":0.02835,"seat_push.seat_distance":0.02994,"seat_push.seat_speed":0.01256},"optimized_scores":{"best_composite_score":-0.39697,"best_fitness_score":0.17303,"best_task_score":0.02919},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.51966,0.09263,0.00967],"force_p95":38.58124,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":38.82448,"mean_force":37.12143,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50214,0.10557,0.06032]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.514,0.10523,0.05893],"force_p95":38.17559,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":38.42058,"mean_force":36.70834,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50214,0.10557,0.06032]},{"body_a":"peg","body_b":"channel_base_body","contact_count":133.0,"contact_point_centroid":[0.50217,0.09651,0.00951],"force_p95":18.91918,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":36.56733,"mean_force":2.41206,"phase_index":4.0,"phase_name":"release_contact","phase_type":"retract","tcp_position_centroid":[0.49987,0.10686,0.06534]},{"body_a":"attachment","body_b":"peg","contact_count":30.0,"contact_point_centroid":[0.5133,0.10482,0.05935],"force_p95":30.71403,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":36.12463,"mean_force":8.3611,"phase_index":4.0,"phase_name":"release_contact","phase_type":"retract","tcp_position_centroid":[0.50147,0.10543,0.06085]},{"body_a":"peg","body_b":"channel_base_body","contact_count":138.0,"contact_point_centroid":[0.51137,0.09049,0.00956],"force_p95":27.96436,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":28.47035,"mean_force":19.87512,"phase_index":2.0,"phase_name":"seat_push","phase_type":"push","tcp_position_centroid":[0.50237,0.11635,0.06063]},{"body_a":"attachment","body_b":"peg","contact_count":108.0,"contact_point_centroid":[0.51398,0.11354,0.05888],"force_p95":27.63865,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.03586,"mean_force":24.82017,"phase_index":2.0,"phase_name":"seat_push","phase_type":"push","tcp_position_centroid":[0.50214,0.11396,0.06033]},{"body_a":"peg","body_b":"channel_base_body","contact_count":364.0,"contact_point_centroid":[0.50557,0.10472,0.00936],"force_p95":0.58321,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.57739,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.50909,0.16923,0.20382]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.50007,0.19844,0.2956]},{"body_a":"peg","body_b":"channel_base_body","contact_count":285.0,"contact_point_centroid":[0.50584,0.10467,0.00939],"force_p95":0.57551,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57865,"mean_force":0.54635,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.51066,0.13375,0.08967]},{"body_a":"peg","body_b":"channel_base_body","contact_count":764.0,"contact_point_centroid":[0.50551,0.09525,0.00938],"force_p95":0.5528,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55904,"mean_force":0.54661,"phase_index":5.0,"phase_name":"retract_home","phase_type":"retract","tcp_position_centroid":[0.49696,0.15134,0.17537]}],"total_contact_groups":10},"final_pose_error":0.01982,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50548,0.09527,0.03379],"final_tcp_position":[0.49817,0.19391,0.28123],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":38.82448,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":391.0,"n_steps_budget":1000.0,"object_pos_end":[0.50596,0.10458,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18478,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.54011,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":396.0,"raw_peak_contact_force":3.33087,"subtask_id":"approach_peg","tcp_end":[0.51878,0.14124,0.11754],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09227,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":285.0,"n_steps_budget":1000.0,"object_pos_end":[0.50598,0.1046,0.03384],"object_pos_start":[0.50596,0.10458,0.03384],"object_to_goal_dist_end":0.1848,"object_to_goal_dist_start":0.18478,"object_z_max":0.03384,"peak_contact_force":0.53595,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":285.0,"raw_peak_contact_force":0.57865,"subtask_id":"descend_peg","tcp_end":[0.50431,0.12631,0.06312],"tcp_start":[0.51878,0.14124,0.11754],"tcp_to_object_dist_end":0.03649,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":138.0,"n_steps_budget":1000.0,"object_pos_end":[0.50574,0.09571,0.03438],"object_pos_start":[0.50598,0.1046,0.03384],"object_to_goal_dist_end":0.1759,"object_to_goal_dist_start":0.1848,"object_z_max":0.03438,"peak_contact_force":26.56117,"phase_name":"seat_push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":246.0,"raw_peak_contact_force":28.47035,"subtask_id":"push_to_goal","tcp_end":[0.50213,0.10566,0.06033],"tcp_start":[0.50431,0.12631,0.06312],"tcp_to_object_dist_end":0.02802,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50576,0.09563,0.03438],"object_pos_start":[0.50574,0.09571,0.03438],"object_to_goal_dist_end":0.17581,"object_to_goal_dist_start":0.1759,"object_z_max":0.03438,"peak_contact_force":36.39205,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":6.0,"raw_peak_contact_force":38.82448,"subtask_id":"push_to_goal","tcp_end":[0.50214,0.10542,0.06027],"tcp_start":[0.50214,0.10548,0.0603],"tcp_to_object_dist_end":0.02792,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":133.0,"n_steps_budget":600.0,"object_pos_end":[0.50553,0.09521,0.03384],"object_pos_start":[0.50579,0.09551,0.03434],"object_to_goal_dist_end":0.1754,"object_to_goal_dist_start":0.1757,"object_z_max":0.03507,"peak_contact_force":0.53509,"phase_name":"release_contact","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":163.0,"raw_peak_contact_force":36.56733,"tcp_end":[0.49877,0.10853,0.07111],"tcp_start":[0.50214,0.10542,0.06027],"tcp_to_object_dist_end":0.04015,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":764.0,"n_steps_budget":1000.0,"object_pos_end":[0.50548,0.09527,0.03379],"object_pos_start":[0.50553,0.09521,0.03384],"object_to_goal_dist_end":0.17546,"object_to_goal_dist_start":0.1754,"object_z_max":0.03384,"peak_contact_force":0.55119,"phase_name":"retract_home","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":764.0,"raw_peak_contact_force":0.55904,"tcp_end":[0.49817,0.19391,0.28123],"tcp_start":[0.49877,0.10853,0.07111],"tcp_to_object_dist_end":0.26647,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.5586,"average_solve_count":401.0,"average_success_count":401.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.speed":0.04149,"descend_to_contact.contact_force_threshold":5.53208,"descend_to_contact.descend_speed":0.0118,"push_channel.insert_depth":0.19771,"push_channel.push_speed":0.03134,"release_contact.release_speed":0.04724,"retract_home.speed":0.01462,"seat_push.seat_distance":0.02999,"seat_push.seat_speed":0.0148},"optimized_scores":{"best_composite_score":-0.35378,"best_fitness_score":0.21622,"best_task_score":0.07283},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.51652,0.06102,0.00918],"force_p95":56.29285,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":56.60249,"mean_force":53.32812,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49751,0.06885,0.05901]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.50936,0.0683,0.05779],"force_p95":55.81585,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":56.12667,"mean_force":52.84395,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49751,0.06885,0.05901]},{"body_a":"peg","body_b":"channel_base_body","contact_count":122.0,"contact_point_centroid":[0.49818,0.05877,0.00948],"force_p95":26.57667,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":49.43976,"mean_force":3.8398,"phase_index":4.0,"phase_name":"release_contact","phase_type":"retract","tcp_position_centroid":[0.49547,0.07025,0.06409]},{"body_a":"attachment","body_b":"peg","contact_count":38.0,"contact_point_centroid":[0.5086,0.06777,0.05881],"force_p95":42.5353,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":48.94721,"mean_force":10.66747,"phase_index":4.0,"phase_name":"release_contact","phase_type":"retract","tcp_position_centroid":[0.49681,0.06893,0.06017]},{"body_a":"peg","body_b":"channel_base_body","contact_count":143.0,"contact_point_centroid":[0.50718,0.05639,0.00925],"force_p95":42.08129,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":43.76032,"mean_force":32.93985,"phase_index":2.0,"phase_name":"seat_push","phase_type":"push","tcp_position_centroid":[0.49767,0.07976,0.05931]},{"body_a":"attachment","body_b":"peg","contact_count":138.0,"contact_point_centroid":[0.5093,0.07774,0.058],"force_p95":41.71474,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":43.3172,"mean_force":33.67134,"phase_index":2.0,"phase_name":"seat_push","phase_type":"push","tcp_position_centroid":[0.49764,0.07942,0.05926]},{"body_a":"peg","body_b":"channel_base_body","contact_count":402.0,"contact_point_centroid":[0.50309,0.06741,0.00932],"force_p95":0.58407,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.56805,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.49933,0.15327,0.20592]},{"body_a":"peg","body_b":"channel_base_body","contact_count":804.0,"contact_point_centroid":[0.50201,0.05596,0.00939],"force_p95":0.55289,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57614,"mean_force":0.54643,"phase_index":5.0,"phase_name":"retract_home","phase_type":"retract","tcp_position_centroid":[0.49461,0.13257,0.17525]},{"body_a":"peg","body_b":"channel_base_body","contact_count":378.0,"contact_point_centroid":[0.50306,0.06745,0.00938],"force_p95":0.55059,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55115,"mean_force":0.54664,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.49812,0.0984,0.0875]}],"total_contact_groups":9},"final_pose_error":0.01974,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50203,0.05581,0.03385],"final_tcp_position":[0.49794,0.19224,0.28197],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":56.60249,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":418.0,"n_steps_budget":1000.0,"object_pos_end":[0.50301,0.06745,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14761,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54659,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":402.0,"raw_peak_contact_force":2.06903,"subtask_id":"approach_peg","tcp_end":[0.49994,0.10786,0.11675],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09232,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":378.0,"n_steps_budget":1000.0,"object_pos_end":[0.50301,0.06745,0.0338],"object_pos_start":[0.50301,0.06745,0.0338],"object_to_goal_dist_end":0.14761,"object_to_goal_dist_start":0.14761,"object_z_max":0.0338,"peak_contact_force":0.54697,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":378.0,"raw_peak_contact_force":0.55115,"subtask_id":"descend_peg","tcp_end":[0.49894,0.08924,0.06098],"tcp_start":[0.49994,0.10786,0.11675],"tcp_to_object_dist_end":0.03507,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":143.0,"n_steps_budget":1000.0,"object_pos_end":[0.50248,0.05633,0.03338],"object_pos_start":[0.50301,0.06745,0.0338],"object_to_goal_dist_end":0.13651,"object_to_goal_dist_start":0.14761,"object_z_max":0.03386,"peak_contact_force":39.07629,"phase_name":"seat_push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":281.0,"raw_peak_contact_force":43.76032,"subtask_id":"push_to_goal","tcp_end":[0.4975,0.06894,0.05902],"tcp_start":[0.49894,0.08924,0.06098],"tcp_to_object_dist_end":0.029,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.5025,0.05625,0.03339],"object_pos_start":[0.50248,0.05633,0.03338],"object_to_goal_dist_end":0.13644,"object_to_goal_dist_start":0.13651,"object_z_max":0.03339,"peak_contact_force":49.8758,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":6.0,"raw_peak_contact_force":56.60249,"subtask_id":"push_to_goal","tcp_end":[0.49751,0.06871,0.05898],"tcp_start":[0.49751,0.06877,0.059],"tcp_to_object_dist_end":0.0289,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":122.0,"n_steps_budget":600.0,"object_pos_end":[0.50194,0.05587,0.03383],"object_pos_start":[0.50252,0.05616,0.0334],"object_to_goal_dist_end":0.13603,"object_to_goal_dist_start":0.13634,"object_z_max":0.03516,"peak_contact_force":0.5565,"phase_name":"release_contact","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":160.0,"raw_peak_contact_force":49.43976,"tcp_end":[0.49426,0.07196,0.06973],"tcp_start":[0.49751,0.06871,0.05898],"tcp_to_object_dist_end":0.04008,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":804.0,"n_steps_budget":1000.0,"object_pos_end":[0.50203,0.05581,0.03385],"object_pos_start":[0.50194,0.05587,0.03383],"object_to_goal_dist_end":0.13596,"object_to_goal_dist_start":0.13603,"object_z_max":0.03385,"peak_contact_force":0.54878,"phase_name":"retract_home","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":804.0,"raw_peak_contact_force":0.57614,"tcp_end":[0.49794,0.19224,0.28197],"tcp_start":[0.49426,0.07196,0.06973],"tcp_to_object_dist_end":0.28319,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.45628,"average_solve_count":366.0,"average_success_count":366.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.speed":0.07921,"descend_to_contact.contact_force_threshold":7.14321,"descend_to_contact.descend_speed":0.01466,"push_channel.insert_depth":0.17837,"push_channel.push_speed":0.03539,"release_contact.release_speed":0.03159,"retract_home.speed":0.0442,"seat_push.seat_distance":0.02988,"seat_push.seat_speed":0.00669},"optimized_scores":{"best_composite_score":-0.36589,"best_fitness_score":0.20411,"best_task_score":0.0622},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.51411,0.10224,0.00947],"force_p95":47.63899,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":48.03013,"mean_force":43.83683,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49844,0.11258,0.05979]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.51029,0.11221,0.05846],"force_p95":47.18531,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":47.57728,"mean_force":43.38742,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49844,0.11258,0.05979]},{"body_a":"peg","body_b":"channel_base_body","contact_count":130.0,"contact_point_centroid":[0.49937,0.10308,0.00951],"force_p95":21.80747,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":43.74445,"mean_force":2.9145,"phase_index":4.0,"phase_name":"release_contact","phase_type":"retract","tcp_position_centroid":[0.49626,0.11384,0.06484]},{"body_a":"attachment","body_b":"peg","contact_count":34.0,"contact_point_centroid":[0.50957,0.11178,0.05914],"force_p95":36.4163,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":43.27352,"mean_force":9.14794,"phase_index":4.0,"phase_name":"release_contact","phase_type":"retract","tcp_position_centroid":[0.49774,0.11252,0.0606]},{"body_a":"peg","body_b":"channel_base_body","contact_count":157.0,"contact_point_centroid":[0.50855,0.09946,0.00944],"force_p95":34.16082,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":35.21827,"mean_force":25.49021,"phase_index":2.0,"phase_name":"seat_push","phase_type":"push","tcp_position_centroid":[0.49861,0.12394,0.06002]},{"body_a":"attachment","body_b":"peg","contact_count":138.0,"contact_point_centroid":[0.51025,0.12179,0.05847],"force_p95":33.75265,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":34.79934,"mean_force":28.48945,"phase_index":2.0,"phase_name":"seat_push","phase_type":"push","tcp_position_centroid":[0.49846,0.12274,0.05985]},{"body_a":"peg","body_b":"channel_base_body","contact_count":343.0,"contact_point_centroid":[0.50364,0.11166,0.00935],"force_p95":0.62748,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.56769,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.50265,0.17279,0.20493]},{"body_a":"peg","body_b":"channel_base_body","contact_count":325.0,"contact_point_centroid":[0.50349,0.11178,0.00939],"force_p95":0.59769,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63473,"mean_force":0.5453,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.50199,0.14023,0.08924]},{"body_a":"peg","body_b":"channel_base_body","contact_count":757.0,"contact_point_centroid":[0.50316,0.10085,0.00939],"force_p95":0.55201,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55859,"mean_force":0.54658,"phase_index":5.0,"phase_name":"retract_home","phase_type":"retract","tcp_position_centroid":[0.49506,0.15496,0.17508]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.49995,0.1993,0.29854]}],"total_contact_groups":10},"final_pose_error":0.01973,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50315,0.10085,0.03378],"final_tcp_position":[0.49797,0.19432,0.28122],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":48.03013,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":365.0,"n_steps_budget":1000.0,"object_pos_end":[0.5037,0.11179,0.03381],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19193,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.52088,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":359.0,"raw_peak_contact_force":2.06328,"subtask_id":"approach_peg","tcp_end":[0.50603,0.14768,0.11826],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09179,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":325.0,"n_steps_budget":1000.0,"object_pos_end":[0.50377,0.11177,0.03378],"object_pos_start":[0.5037,0.11179,0.03381],"object_to_goal_dist_end":0.19191,"object_to_goal_dist_start":0.19193,"object_z_max":0.03388,"peak_contact_force":0.58562,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":325.0,"raw_peak_contact_force":0.63473,"subtask_id":"descend_peg","tcp_end":[0.50035,0.13307,0.06224],"tcp_start":[0.50603,0.14768,0.11826],"tcp_to_object_dist_end":0.03571,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":157.0,"n_steps_budget":1000.0,"object_pos_end":[0.50345,0.1013,0.03396],"object_pos_start":[0.50377,0.11177,0.03378],"object_to_goal_dist_end":0.18143,"object_to_goal_dist_start":0.19191,"object_z_max":0.03397,"peak_contact_force":34.57252,"phase_name":"seat_push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":295.0,"raw_peak_contact_force":35.21827,"subtask_id":"push_to_goal","tcp_end":[0.49843,0.11267,0.05981],"tcp_start":[0.50035,0.13307,0.06224],"tcp_to_object_dist_end":0.02868,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50348,0.10123,0.03396],"object_pos_start":[0.50345,0.1013,0.03396],"object_to_goal_dist_end":0.18136,"object_to_goal_dist_start":0.18143,"object_z_max":0.03396,"peak_contact_force":44.11874,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":6.0,"raw_peak_contact_force":48.03013,"subtask_id":"push_to_goal","tcp_end":[0.49844,0.11244,0.05976],"tcp_start":[0.49844,0.1125,0.05978],"tcp_to_object_dist_end":0.02858,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":130.0,"n_steps_budget":600.0,"object_pos_end":[0.50304,0.10083,0.03388],"object_pos_start":[0.50351,0.10114,0.03395],"object_to_goal_dist_end":0.18096,"object_to_goal_dist_start":0.18127,"object_z_max":0.03514,"peak_contact_force":0.55895,"phase_name":"release_contact","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":164.0,"raw_peak_contact_force":43.74445,"tcp_end":[0.49512,0.11548,0.07054],"tcp_start":[0.49844,0.11244,0.05976],"tcp_to_object_dist_end":0.04026,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":757.0,"n_steps_budget":1000.0,"object_pos_end":[0.50315,0.10085,0.03378],"object_pos_start":[0.50304,0.10083,0.03388],"object_to_goal_dist_end":0.18099,"object_to_goal_dist_start":0.18096,"object_z_max":0.03388,"peak_contact_force":0.54377,"phase_name":"retract_home","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":757.0,"raw_peak_contact_force":0.55859,"tcp_end":[0.49797,0.19432,0.28122],"tcp_start":[0.49512,0.11548,0.07054],"tcp_to_object_dist_end":0.26455,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```