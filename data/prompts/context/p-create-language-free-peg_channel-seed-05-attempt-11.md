## Search State

- **Seed**: 5
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.4383 | 0.72 | ❌ rejected |
| 10 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 9 | 0.1376 | 0.19 | ❌ rejected |
| 9 | approach → descend → push → push → retract → retract | linear_cartesian | linear_cartesian | impedance_motion | impedance_motion | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | impedance_control | position_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 9 | -0.3722 | 0.05 | ❌ rejected |
| 8 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.4605 | 0.76 | ✅ accepted |
| 7 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.0210 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.72 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.761, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.438) — your mutation base

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

- **Composite score**: 0.438
- **task_score** (E): 0.717
- **fitness_score**: 0.748  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.310

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above | 1.00 | 1.00 | 0.1959 |
| descend_to_peg | 1.00 | 0.67 | 0.0754 |
| push_channel | 0.67 | 1.00 | 0.1505 |
| retract_home | 1.00 | 1.00 | 0.3206 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.508, 0.132, 0.117) | (0.512, 0.095, 0.040)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 1.000 | 0.534 | 2.488 |
| descend_to_peg | descend | 1.00 / step_budget | (0.508, 0.132, 0.117)→(0.506, 0.119, 0.044) | (0.504, 0.095, 0.034)→(0.506, 0.076, 0.036) | 0.175→0.157 | 0.67 / 1.333 | 66.299 | 149.644 |
| push_channel | push | 0.67 / step_budget | (0.506, 0.119, 0.044)→(0.503, -0.031, 0.039) | (0.506, 0.076, 0.036)→(0.499, -0.056, 0.027) | 0.157→0.033 | 1.00 / 2.667 | 20.267 | 129.826 |
| retract_home | retract | 1.00 / step_budget | (0.503, -0.031, 0.039)→(0.498, 0.183, 0.277) | (0.499, -0.056, 0.027)→(0.503, -0.052, 0.024) | 0.033→0.036 | 1.00 / 1.000 | 0.626 | 58.058 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.869
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.869
- phase_score: 0.827
- phase_breakdown.approach_peg_score: 0.676
- phase_breakdown.push_to_goal_score: 0.886
- phase_breakdown.descend_peg_score: 0.904

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.844
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.869
- **Median Q (composite search score)**: 0.404
- **K-run variance**: 0.0047
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.252


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.82382,"average_solve_count":403.0,"average_success_count":403.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.speed":0.07269,"descend_to_peg.descend_speed":0.01238,"push_channel.insert_depth":0.18112,"push_channel.push_speed":0.0342,"retract_home.speed":0.0556},"optimized_scores":{"best_composite_score":0.37679,"best_fitness_score":0.68679,"best_task_score":0.52081},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":278.0,"contact_point_centroid":[0.50782,0.10541,0.00926],"force_p95":117.1266,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":130.4088,"mean_force":19.96988,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.51131,0.1339,0.07988]},{"body_a":"attachment","body_b":"peg","contact_count":57.0,"contact_point_centroid":[0.5148,0.11981,0.05607],"force_p95":127.5094,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":129.90511,"mean_force":94.91893,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50841,0.12936,0.05568]},{"body_a":"attachment","body_b":"peg","contact_count":15.0,"contact_point_centroid":[0.50158,-0.0512,0.03917],"force_p95":40.87506,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":59.62626,"mean_force":10.41828,"phase_index":3.0,"phase_name":"retract_home","phase_type":"retract","tcp_position_centroid":[0.50244,-0.03977,0.03912]},{"body_a":"attachment","body_b":"peg","contact_count":357.0,"contact_point_centroid":[0.50198,0.01101,0.04035],"force_p95":31.08117,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":59.0512,"mean_force":4.46002,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50284,0.02282,0.03874]},{"body_a":"peg","body_b":"channel_base_body","contact_count":22.0,"contact_point_centroid":[0.51073,-0.10064,0.02913],"force_p95":57.57462,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":58.04872,"mean_force":43.51265,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50286,-0.03878,0.03874]},{"body_a":"peg","body_b":"channel_base_body","contact_count":21.0,"contact_point_centroid":[0.50881,-0.10054,0.03551],"force_p95":32.28185,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":57.80087,"mean_force":7.34513,"phase_index":3.0,"phase_name":"retract_home","phase_type":"retract","tcp_position_centroid":[0.5022,-0.03913,0.03961]},{"body_a":"peg","body_b":"channel_base_body","contact_count":994.0,"contact_point_centroid":[0.50312,-0.07432,0.00812],"force_p95":0.72552,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.40994,"mean_force":0.70007,"phase_index":3.0,"phase_name":"retract_home","phase_type":"retract","tcp_position_centroid":[0.49896,0.07205,0.15673]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":57.0,"contact_point_centroid":[0.47492,-0.06011,0.02797],"force_p95":7.96531,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.4665,"mean_force":3.73997,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50282,-0.00154,0.03874]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":13.0,"contact_point_centroid":[0.525,-0.04938,0.02423],"force_p95":8.9131,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.92786,"mean_force":3.59098,"phase_index":3.0,"phase_name":"retract_home","phase_type":"retract","tcp_position_centroid":[0.49862,0.11783,0.20632]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":7.0,"contact_point_centroid":[0.5251,0.01619,0.02803],"force_p95":6.60103,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.32658,"mean_force":2.12509,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50287,0.07743,0.03872]},{"body_a":"peg","body_b":"channel_base_body","contact_count":481.0,"contact_point_centroid":[0.50002,0.00196,0.00941],"force_p95":5.81329,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.48005,"mean_force":1.55313,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50306,0.04477,0.03901]},{"body_a":"peg","body_b":"channel_base_body","contact_count":350.0,"contact_point_centroid":[0.50551,0.10475,0.00936],"force_p95":0.5922,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.57864,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.50913,0.16906,0.20331]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.50024,0.19828,0.29501]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":8.0,"contact_point_centroid":[0.47498,-0.09827,0.02799],"force_p95":0.72355,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.80914,"mean_force":0.35031,"phase_index":3.0,"phase_name":"retract_home","phase_type":"retract","tcp_position_centroid":[0.50186,-0.03758,0.04083]}],"total_contact_groups":14},"final_pose_error":0.03248,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50635,-0.07339,0.02423],"final_tcp_position":[0.49842,0.18036,0.27417],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":130.4088,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":377.0,"n_steps_budget":1000.0,"object_pos_end":[0.50598,0.1046,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.1848,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.53829,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":382.0,"raw_peak_contact_force":3.33087,"subtask_id":"approach_peg","tcp_end":[0.51874,0.14127,0.11765],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09237,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":292.0,"n_steps_budget":1000.0,"object_pos_end":[0.50486,0.07416,0.03858],"object_pos_start":[0.50598,0.1046,0.03384],"object_to_goal_dist_end":0.15424,"object_to_goal_dist_start":0.1848,"object_z_max":0.04097,"peak_contact_force":0.0,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":335.0,"raw_peak_contact_force":130.4088,"subtask_id":"descend_peg","tcp_end":[0.50651,0.12698,0.0434],"tcp_start":[0.51874,0.14127,0.11765],"tcp_to_object_dist_end":0.05307,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":603.0,"n_steps_budget":1000.0,"object_pos_end":[0.4957,-0.07504,0.02832],"object_pos_start":[0.50486,0.07416,0.03858],"object_to_goal_dist_end":0.0134,"object_to_goal_dist_start":0.15424,"object_z_max":0.03858,"peak_contact_force":59.0512,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":924.0,"raw_peak_contact_force":59.0512,"subtask_id":"push_to_goal","tcp_end":[0.50293,-0.04038,0.03876],"tcp_start":[0.50651,0.12698,0.0434],"tcp_to_object_dist_end":0.03691,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50635,-0.07339,0.02423],"object_pos_start":[0.4957,-0.07504,0.02832],"object_to_goal_dist_end":0.01824,"object_to_goal_dist_start":0.0134,"object_z_max":0.02878,"peak_contact_force":0.63155,"phase_name":"retract_home","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1051.0,"raw_peak_contact_force":59.62626,"tcp_end":[0.49842,0.18036,0.27417],"tcp_start":[0.50293,-0.04038,0.03876],"tcp_to_object_dist_end":0.35626,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.24534,"average_solve_count":322.0,"average_success_count":322.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.speed":0.08979,"descend_to_peg.descend_speed":0.03432,"push_channel.insert_depth":0.19792,"push_channel.push_speed":0.03461,"retract_home.speed":0.0453},"optimized_scores":{"best_composite_score":0.5336,"best_fitness_score":0.8436,"best_task_score":0.86887},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":790.0,"contact_point_centroid":[0.49847,-0.04006,0.04448],"force_p95":157.69313,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":162.15461,"mean_force":85.99347,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49678,-0.02967,0.03765]},{"body_a":"peg","body_b":"channel_base_body","contact_count":545.0,"contact_point_centroid":[0.49699,-0.10244,0.04248],"force_p95":158.81028,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":160.74098,"mean_force":122.69044,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49705,-0.04738,0.03743]},{"body_a":"peg","body_b":"channel_base_body","contact_count":268.0,"contact_point_centroid":[0.50427,0.06611,0.00938],"force_p95":99.60686,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":118.09988,"mean_force":9.47793,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.49871,0.09899,0.07937]},{"body_a":"attachment","body_b":"peg","contact_count":31.0,"contact_point_centroid":[0.50635,0.08452,0.05719],"force_p95":111.69387,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":117.54597,"mean_force":77.48463,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.49956,0.09375,0.0571]},{"body_a":"peg","body_b":"channel_base_body","contact_count":50.0,"contact_point_centroid":[0.49512,-0.10219,0.03959],"force_p95":99.12906,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":103.45489,"mean_force":40.76081,"phase_index":3.0,"phase_name":"retract_home","phase_type":"retract","tcp_position_centroid":[0.49681,-0.04401,0.04075]},{"body_a":"attachment","body_b":"peg","contact_count":42.0,"contact_point_centroid":[0.49811,-0.0557,0.03949],"force_p95":65.52495,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":69.47658,"mean_force":24.64577,"phase_index":3.0,"phase_name":"retract_home","phase_type":"retract","tcp_position_centroid":[0.49698,-0.04512,0.03987]},{"body_a":"peg","body_b":"channel_base_body","contact_count":990.0,"contact_point_centroid":[0.50249,-0.07248,0.00815],"force_p95":0.78265,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":42.92902,"mean_force":1.52519,"phase_index":3.0,"phase_name":"retract_home","phase_type":"retract","tcp_position_centroid":[0.49654,0.06761,0.15667]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.52536,-0.10072,0.026],"force_p95":40.6582,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":42.294,"mean_force":23.06389,"phase_index":3.0,"phase_name":"retract_home","phase_type":"retract","tcp_position_centroid":[0.49698,-0.04369,0.04155]},{"body_a":"peg","body_b":"channel_base_body","contact_count":837.0,"contact_point_centroid":[0.5048,-0.06719,0.00966],"force_p95":10.47367,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":28.49509,"mean_force":3.2431,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49684,-0.01551,0.03784]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":91.0,"contact_point_centroid":[0.52505,-0.04983,0.02784],"force_p95":10.00163,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.87833,"mean_force":3.61793,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49618,0.0092,0.03813]},{"body_a":"peg","body_b":"channel_base_body","contact_count":382.0,"contact_point_centroid":[0.50312,0.06748,0.00932],"force_p95":0.61538,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.56917,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.49948,0.15295,0.20527]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.52501,0.03144,0.05884],"force_p95":0.94512,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.94512,"mean_force":0.94512,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50002,0.09113,0.04602]}],"total_contact_groups":12},"final_pose_error":0.03296,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49826,-0.07156,0.02415],"final_tcp_position":[0.49807,0.17964,0.27416],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":162.15461,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":398.0,"n_steps_budget":1000.0,"object_pos_end":[0.50305,0.06742,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14758,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54666,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":382.0,"raw_peak_contact_force":2.06903,"subtask_id":"approach_peg","tcp_end":[0.50008,0.10768,0.1164],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09194,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":275.0,"n_steps_budget":1000.0,"object_pos_end":[0.50552,0.0407,0.03944],"object_pos_start":[0.50305,0.06742,0.0338],"object_to_goal_dist_end":0.12082,"object_to_goal_dist_start":0.14758,"object_z_max":0.04089,"peak_contact_force":0.48689,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":300.0,"raw_peak_contact_force":118.09988,"subtask_id":"descend_peg","tcp_end":[0.49985,0.09026,0.04266],"tcp_start":[0.50008,0.10768,0.1164],"tcp_to_object_dist_end":0.04999,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50624,-0.08122,0.02776],"object_pos_start":[0.50552,0.0407,0.03944],"object_to_goal_dist_end":0.01379,"object_to_goal_dist_start":0.12082,"object_z_max":0.03944,"peak_contact_force":1.11669,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2263.0,"raw_peak_contact_force":162.15461,"subtask_id":"push_to_goal","tcp_end":[0.49834,-0.05051,0.03701],"tcp_start":[0.49985,0.09026,0.04266],"tcp_to_object_dist_end":0.03303,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49826,-0.07156,0.02415],"object_pos_start":[0.50624,-0.08122,0.02776],"object_to_goal_dist_end":0.01804,"object_to_goal_dist_start":0.01379,"object_z_max":0.0308,"peak_contact_force":0.64359,"phase_name":"retract_home","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1119.0,"raw_peak_contact_force":103.45489,"tcp_end":[0.49807,0.17964,0.27416],"tcp_start":[0.49834,-0.05051,0.03701],"tcp_to_object_dist_end":0.3544,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.10658,"average_solve_count":319.0,"average_success_count":319.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.speed":0.05912,"descend_to_peg.descend_speed":0.03364,"push_channel.insert_depth":0.17024,"push_channel.push_speed":0.02621,"retract_home.speed":0.08128},"optimized_scores":{"best_composite_score":0.40437,"best_fitness_score":0.71437,"best_task_score":0.76238},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":426.0,"contact_point_centroid":[0.50902,0.11577,0.00844],"force_p95":193.32111,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":200.42436,"mean_force":77.4923,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50496,0.14023,0.06811]},{"body_a":"attachment","body_b":"peg","contact_count":228.0,"contact_point_centroid":[0.51321,0.12917,0.05152],"force_p95":197.06369,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":199.85306,"mean_force":143.8747,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.5069,0.13856,0.04985]},{"body_a":"peg","body_b":"channel_base_body","contact_count":944.0,"contact_point_centroid":[0.50523,0.0756,0.00846],"force_p95":154.34486,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":168.27314,"mean_force":93.69917,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51154,0.09298,0.04769]},{"body_a":"attachment","body_b":"peg","contact_count":958.0,"contact_point_centroid":[0.51086,0.08506,0.04935],"force_p95":153.87865,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":166.58045,"mean_force":96.51072,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51153,0.09476,0.04768]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":463.0,"contact_point_centroid":[0.52504,0.11584,0.06],"force_p95":120.70498,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":152.56524,"mean_force":84.64097,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51276,0.11857,0.05065]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":426.0,"contact_point_centroid":[0.47424,0.03701,0.03597],"force_p95":51.24318,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":59.7488,"mean_force":23.65697,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50966,0.05574,0.04378]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":92.0,"contact_point_centroid":[0.52514,0.11463,0.05128],"force_p95":16.73773,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.4879,"mean_force":11.60801,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51308,0.13567,0.04878]},{"body_a":"peg","body_b":"channel_base_body","contact_count":922.0,"contact_point_centroid":[0.50565,-0.01053,0.00813],"force_p95":1.35221,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.09182,"mean_force":0.97255,"phase_index":3.0,"phase_name":"retract_home","phase_type":"retract","tcp_position_centroid":[0.50179,0.09465,0.1619]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":79.0,"contact_point_centroid":[0.52505,-0.00532,0.0251],"force_p95":9.93785,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.70188,"mean_force":4.58356,"phase_index":3.0,"phase_name":"retract_home","phase_type":"retract","tcp_position_centroid":[0.50267,0.06725,0.12682]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":35.0,"contact_point_centroid":[0.52505,0.11771,0.04472],"force_p95":6.62882,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.59589,"mean_force":1.20987,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.51004,0.14025,0.04561]},{"body_a":"peg","body_b":"channel_base_body","contact_count":356.0,"contact_point_centroid":[0.50355,0.11171,0.00935],"force_p95":0.62709,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.56676,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.50247,0.17285,0.20521]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.49987,0.19934,0.29876]}],"total_contact_groups":12},"final_pose_error":0.01999,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50525,-0.0102,0.02423],"final_tcp_position":[0.49852,0.18994,0.28279],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":200.42436,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":378.0,"n_steps_budget":1000.0,"object_pos_end":[0.50372,0.11175,0.0338],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19189,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.51789,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":372.0,"raw_peak_contact_force":2.06328,"subtask_id":"approach_peg","tcp_end":[0.50607,0.14773,0.11839],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09196,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":426.0,"n_steps_budget":1000.0,"object_pos_end":[0.507,0.11416,0.0301],"object_pos_start":[0.50372,0.11175,0.0338],"object_to_goal_dist_end":0.19453,"object_to_goal_dist_start":0.19189,"object_z_max":0.03397,"peak_contact_force":198.40929,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":689.0,"raw_peak_contact_force":200.42436,"subtask_id":"descend_peg","tcp_end":[0.51031,0.14057,0.04503],"tcp_start":[0.50607,0.14773,0.11839],"tcp_to_object_dist_end":0.03052,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49434,-0.0105,0.02531],"object_pos_start":[0.507,0.11416,0.0301],"object_to_goal_dist_end":0.07126,"object_to_goal_dist_start":0.19453,"object_z_max":0.04015,"peak_contact_force":0.63273,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2883.0,"raw_peak_contact_force":168.27314,"subtask_id":"push_to_goal","tcp_end":[0.50849,-0.00269,0.04201],"tcp_start":[0.51031,0.14057,0.04503],"tcp_to_object_dist_end":0.02325,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":922.0,"n_steps_budget":1000.0,"object_pos_end":[0.50525,-0.0102,0.02423],"object_pos_start":[0.49434,-0.0105,0.02531],"object_to_goal_dist_end":0.07175,"object_to_goal_dist_start":0.07126,"object_z_max":0.02601,"peak_contact_force":0.6027,"phase_name":"retract_home","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1001.0,"raw_peak_contact_force":11.09182,"tcp_end":[0.49852,0.18994,0.28279],"tcp_start":[0.50849,-0.00269,0.04201],"tcp_to_object_dist_end":0.32704,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```