## Search State

- **Seed**: 5
- **Iteration**: 6 / 15

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

## Current Skill (Q=-0.120) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: reach_above_peg
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.12
  weight: 0.2
- id: contact_peg
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.02
  weight: 0.3
- id: push_through_channel
  target_entity: object
  metric: goal_progress
  weight: 0.5
phases:
- id: approach_1
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
    - 0.0
    - 0.12
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: add
  subtask_id: reach_above_peg
- id: descend_1
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
    - 0.0
    - 0.02
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: add
  subtask_id: contact_peg
- id: push_1
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: time_limit
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.16
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
    orientation:
      mode: keep_current
  parameters:
    max_time:
      type: scalar
      range:
      - 5.0
      - 15.0
      default: 10.0
      binds_to:
      - path: duration.max_time
        mode: replace
    push_distance:
      type: scalar
      range:
      - 0.1
      - 0.2
      default: 0.16
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    speed:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: add
  guards:
  - id: force_guard
    when: during_phase
    predicate: force_below
    threshold: 40.0
    on_failure: abort
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.005
    - 0.0
    - 0.0
  subtask_id: push_through_channel

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.0, 0.12], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (add)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.0, 0.02], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (add)
- **push_1** (`push`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.16, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - max_time: status=consumed; consumers=duration.max_time (replace)
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - speed: status=consumed; consumers=generator.speed (add)
  - guards:
    - id=force_guard, when=during_phase, predicate=force_below, on_failure=abort, threshold=40.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.005, 0.0, 0.0]

## Design Metrics

- **Composite score**: -0.120
- **task_score** (E): 0.118
- **fitness_score**: 0.190  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.310

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1572 |
| descend_1 | 1.00 | 1.00 | 0.1271 |
| align_1 | 1.00 | 1.00 | 0.0228 |
| push_1 | 0.00 | 1.00 | 0.0000 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.508, 0.108, 0.174) | (0.512, 0.095, 0.040)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 1.000 | 0.539 | 2.488 |
| descend_1 | descend | 1.00 / step_budget | (0.508, 0.108, 0.174)→(0.510, 0.097, 0.047) | (0.504, 0.095, 0.034)→(0.507, 0.094, 0.028) | 0.175→0.175 | 1.00 / 3.000 | 204.432 | 210.736 |
| align_1 | align | 1.00 / step_budget | (0.510, 0.097, 0.047)→(0.516, 0.113, 0.059) | (0.507, 0.094, 0.028)→(0.497, 0.083, 0.032) | 0.175→0.163 | 1.00 / 4.333 | 345.674 | 719.321 |
| push_1 | push | 0.00 / guard_failure | (0.516, 0.113, 0.059)→(0.516, 0.113, 0.059) | (0.497, 0.083, 0.032)→(0.497, 0.083, 0.032) | 0.163→0.163 | 1.00 / 4.000 | 44.135 | 79.703 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.347
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.347
- phase_score: 0.247
- phase_breakdown.contact_peg_score: 0.585
- phase_breakdown.push_through_channel_score: 0.000
- phase_breakdown.reach_above_peg_score: 0.672

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.287
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.347
- **Median Q (composite search score)**: -0.157
- **K-run variance**: 0.0048
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.261


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.86154,"average_solve_count":65.0,"average_success_count":65.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.speed":0.05891,"approach_1.speed":0.11687,"descend_1.speed":0.06974,"push_1.push_threshold":32.87147,"push_1.speed":0.05063},"optimized_scores":{"best_composite_score":-0.15689,"best_fitness_score":0.15311,"best_task_score":0.00673},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":61.0,"contact_point_centroid":[0.5252,0.10995,0.05996],"force_p95":566.88358,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":616.18542,"mean_force":279.73899,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.51302,0.10874,0.05795]},{"body_a":"world","body_b":"link6","contact_count":201.0,"contact_point_centroid":[0.51626,0.29728,-7e-05],"force_p95":407.18576,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":467.93465,"mean_force":310.79803,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.51078,0.1134,0.06222]},{"body_a":"attachment","body_b":"peg","contact_count":413.0,"contact_point_centroid":[0.50936,0.11395,0.05396],"force_p95":204.91741,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":306.59167,"mean_force":114.60307,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.51124,0.11162,0.06186]},{"body_a":"world","body_b":"link7","contact_count":58.0,"contact_point_centroid":[0.5109,0.17279,-0.00017],"force_p95":167.36261,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":276.60271,"mean_force":130.07053,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.51229,0.11547,0.05891]},{"body_a":"peg","body_b":"channel_base_body","contact_count":426.0,"contact_point_centroid":[0.50017,0.108,0.0077],"force_p95":204.74047,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":250.56844,"mean_force":107.29863,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.51128,0.1117,0.06177]},{"body_a":"attachment","body_b":"peg","contact_count":75.0,"contact_point_centroid":[0.51989,0.10595,0.05416],"force_p95":198.98421,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":204.73209,"mean_force":142.61085,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50802,0.10665,0.05361]},{"body_a":"peg","body_b":"channel_base_body","contact_count":408.0,"contact_point_centroid":[0.50863,0.10492,0.00916],"force_p95":186.37229,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":202.95582,"mean_force":26.63249,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51065,0.11086,0.10545]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":27.0,"contact_point_centroid":[0.52548,0.10451,0.05151],"force_p95":7.38976,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":153.14344,"mean_force":7.9181,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.51217,0.10472,0.05059]},{"body_a":"world","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.51929,0.30064,-2e-05],"force_p95":92.97715,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":93.87598,"mean_force":79.70517,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51199,0.11582,0.05932]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":268.0,"contact_point_centroid":[0.47376,0.10486,0.02941],"force_p95":43.46088,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":85.02496,"mean_force":25.90044,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.51043,0.11255,0.06237]},{"body_a":"world","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.51096,0.17301,-3e-05],"force_p95":59.67415,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":61.8348,"mean_force":34.02102,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51199,0.11582,0.05932]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":49.0,"contact_point_centroid":[0.52513,0.10458,0.04978],"force_p95":32.92485,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":48.53995,"mean_force":11.64639,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50913,0.10667,0.05159]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":3.0,"contact_point_centroid":[0.4744,0.1003,0.05228],"force_p95":16.83325,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.64929,"mean_force":6.50366,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51199,0.11582,0.05932]},{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.50024,0.11616,0.05689],"force_p95":17.06981,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.93777,"mean_force":9.25816,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51198,0.11581,0.05931]},{"body_a":"peg","body_b":"channel_base_body","contact_count":249.0,"contact_point_centroid":[0.50545,0.10462,0.00935],"force_p95":0.63274,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.59176,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50952,0.15571,0.23146]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50051,0.19653,0.29457]}],"total_contact_groups":17},"final_pose_error":0.19716,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.4919,0.10038,0.03496],"final_tcp_position":[0.51203,0.11585,0.05933],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":6276.61512,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":276.0,"n_steps_budget":600.0,"object_pos_end":[0.50588,0.10457,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18477,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.55425,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":281.0,"raw_peak_contact_force":3.33087,"subtask_id":"reach_above_peg","tcp_end":[0.51871,0.11732,0.17432],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14164,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":408.0,"n_steps_budget":660.0,"object_pos_end":[0.50751,0.10459,0.02913],"object_pos_start":[0.50588,0.10457,0.03384],"object_to_goal_dist_end":0.18506,"object_to_goal_dist_start":0.18477,"object_z_max":0.03384,"peak_contact_force":196.23327,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":532.0,"raw_peak_contact_force":204.73209,"subtask_id":"contact_peg","tcp_end":[0.51134,0.10676,0.04853],"tcp_start":[0.51871,0.11732,0.17432],"tcp_to_object_dist_end":0.01989,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":426.0,"n_steps_budget":600.0,"object_pos_end":[0.49179,0.10042,0.03493],"object_pos_start":[0.50751,0.10459,0.02913],"object_to_goal_dist_end":0.18068,"object_to_goal_dist_start":0.18506,"object_z_max":0.03492,"peak_contact_force":386.35918,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1454.0,"raw_peak_contact_force":616.18542,"subtask_id":"contact_peg","tcp_end":[0.51196,0.11581,0.05931],"tcp_start":[0.51134,0.10676,0.04853],"tcp_to_object_dist_end":0.03519,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.49183,0.1004,0.03494],"object_pos_start":[0.49179,0.10042,0.03493],"object_to_goal_dist_end":0.18066,"object_to_goal_dist_start":0.18068,"object_z_max":0.03495,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":14.0,"raw_peak_contact_force":93.87598,"subtask_id":"push_through_channel","tcp_end":[0.51203,0.11585,0.05933],"tcp_start":[0.51201,0.11583,0.05932],"tcp_to_object_dist_end":0.03523,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.69231,"average_solve_count":91.0,"average_success_count":91.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.speed":0.08718,"approach_1.speed":0.05689,"descend_1.speed":0.04419,"push_1.push_threshold":26.62681,"push_1.speed":0.03966},"optimized_scores":{"best_composite_score":-0.02311,"best_fitness_score":0.28689,"best_task_score":0.34659},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":150.0,"contact_point_centroid":[0.52528,0.09287,0.05993],"force_p95":488.6317,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":828.09205,"mean_force":254.71324,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.51461,0.07642,0.06378]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":78.0,"contact_point_centroid":[0.53446,0.11995,0.04827],"force_p95":410.69644,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":442.85382,"mean_force":234.42687,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.51535,0.08129,0.06859]},{"body_a":"attachment","body_b":"peg","contact_count":192.0,"contact_point_centroid":[0.51432,0.08016,0.05382],"force_p95":241.88086,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":403.49308,"mean_force":141.42207,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.51358,0.07634,0.06197]},{"body_a":"peg","body_b":"channel_base_body","contact_count":433.0,"contact_point_centroid":[0.50165,0.05098,0.00838],"force_p95":227.72334,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":326.04205,"mean_force":62.07466,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.51086,0.08081,0.06126]},{"body_a":"world","body_b":"link7","contact_count":216.0,"contact_point_centroid":[0.50816,0.14298,-0.0002],"force_p95":270.3641,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":318.52348,"mean_force":226.8347,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.5071,0.08535,0.05851]},{"body_a":"world","body_b":"link6","contact_count":89.0,"contact_point_centroid":[0.51703,0.27052,-3e-05],"force_p95":287.29507,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":301.93606,"mean_force":217.93286,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50575,0.08586,0.0592]},{"body_a":"peg","body_b":"channel_base_body","contact_count":468.0,"contact_point_centroid":[0.50654,0.06762,0.00898],"force_p95":177.07848,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":212.24391,"mean_force":33.95893,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49987,0.07506,0.10134]},{"body_a":"attachment","body_b":"peg","contact_count":109.0,"contact_point_centroid":[0.51575,0.06897,0.053],"force_p95":207.35954,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":211.58211,"mean_force":143.29439,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50388,0.06981,0.05227]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":18.0,"contact_point_centroid":[0.52541,0.06562,0.04992],"force_p95":168.03225,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":182.53429,"mean_force":43.84258,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.51287,0.06619,0.04698]},{"body_a":"world","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.5058,0.14319,-5e-05],"force_p95":51.55409,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":51.56194,"mean_force":51.09967,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50548,0.08595,0.05924]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52503,0.06681,0.05298],"force_p95":47.26467,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":48.75514,"mean_force":25.03238,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50815,0.06941,0.04749]},{"body_a":"world","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.51751,0.27055,-2e-05],"force_p95":44.19144,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":44.19585,"mean_force":43.889,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50548,0.08595,0.05924]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":123.0,"contact_point_centroid":[0.47482,0.05714,0.02008],"force_p95":33.41559,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":36.32457,"mean_force":12.16757,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.51359,0.08226,0.06555]},{"body_a":"peg","body_b":"channel_base_body","contact_count":326.0,"contact_point_centroid":[0.50304,0.06755,0.00931],"force_p95":0.65223,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.57303,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49959,0.14022,0.23318]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.49944,0.03703,0.00805],"force_p95":0.67496,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.68313,"mean_force":0.60569,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50548,0.08595,0.05924]}],"total_contact_groups":15},"final_pose_error":0.16715,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49952,0.01201,0.02414],"final_tcp_position":[0.50548,0.08595,0.05925],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":828.09205,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":342.0,"n_steps_budget":1000.0,"object_pos_end":[0.50309,0.06745,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14761,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54685,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":326.0,"raw_peak_contact_force":2.06903,"subtask_id":"reach_above_peg","tcp_end":[0.50032,0.08301,0.17208],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13918,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":468.0,"n_steps_budget":990.0,"object_pos_end":[0.50702,0.06678,0.02751],"object_pos_start":[0.50309,0.06745,0.0338],"object_to_goal_dist_end":0.14748,"object_to_goal_dist_start":0.14761,"object_z_max":0.0338,"peak_contact_force":201.82889,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":593.0,"raw_peak_contact_force":212.24391,"subtask_id":"contact_peg","tcp_end":[0.50892,0.06935,0.04667],"tcp_start":[0.50032,0.08301,0.17208],"tcp_to_object_dist_end":0.01943,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":455.0,"n_steps_budget":600.0,"object_pos_end":[0.49939,0.01206,0.02414],"object_pos_start":[0.50702,0.06678,0.02751],"object_to_goal_dist_end":0.09342,"object_to_goal_dist_start":0.14748,"object_z_max":0.04106,"peak_contact_force":272.31419,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1299.0,"raw_peak_contact_force":828.09205,"subtask_id":"contact_peg","tcp_end":[0.50548,0.08595,0.05924],"tcp_start":[0.50892,0.06935,0.04667],"tcp_to_object_dist_end":0.08203,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.49943,0.01207,0.02414],"object_pos_start":[0.49939,0.01206,0.02414],"object_to_goal_dist_end":0.09343,"object_to_goal_dist_start":0.09342,"object_z_max":0.02414,"peak_contact_force":50.25365,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":9.0,"raw_peak_contact_force":51.56194,"subtask_id":"push_through_channel","tcp_end":[0.50548,0.08595,0.05925],"tcp_start":[0.50548,0.08595,0.05924],"tcp_to_object_dist_end":0.08202,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.875,"average_solve_count":80.0,"average_success_count":80.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.speed":0.03822,"approach_1.speed":0.088,"descend_1.speed":0.03961,"push_1.push_threshold":31.62179,"push_1.speed":0.07641},"optimized_scores":{"best_composite_score":-0.17929,"best_fitness_score":0.13071,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":2,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":44.0,"contact_point_centroid":[0.52557,0.11395,0.0599],"force_p95":643.31768,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":713.68433,"mean_force":317.57497,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.5131,0.11256,0.05465]},{"body_a":"world","body_b":"link6","contact_count":185.0,"contact_point_centroid":[0.50729,0.32027,-5e-05],"force_p95":398.95185,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":484.75419,"mean_force":310.30607,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.53034,0.13672,0.05918]},{"body_a":"attachment","body_b":"peg","contact_count":454.0,"contact_point_centroid":[0.52227,0.13296,0.04989],"force_p95":277.98891,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":362.4787,"mean_force":108.77315,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.52545,0.1318,0.05804]},{"body_a":"world","body_b":"link7","contact_count":252.0,"contact_point_centroid":[0.52441,0.19347,-8e-05],"force_p95":174.05828,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":312.00166,"mean_force":143.04395,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.53052,0.13639,0.05895]},{"body_a":"peg","body_b":"channel_base_body","contact_count":455.0,"contact_point_centroid":[0.50658,0.11916,0.00854],"force_p95":240.71784,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":292.46919,"mean_force":99.97354,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.52542,0.13174,0.05805]},{"body_a":"peg","body_b":"channel_base_body","contact_count":476.0,"contact_point_centroid":[0.50746,0.1119,0.00903],"force_p95":201.77723,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":215.23236,"mean_force":36.47668,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50333,0.11737,0.10171]},{"body_a":"attachment","body_b":"peg","contact_count":115.0,"contact_point_centroid":[0.51748,0.11298,0.05314],"force_p95":208.22655,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":214.12578,"mean_force":148.67209,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50561,0.11377,0.05224]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":30.0,"contact_point_centroid":[0.52575,0.11205,0.05051],"force_p95":147.22732,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":164.82103,"mean_force":21.50238,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.51279,0.11094,0.04987]},{"body_a":"world","body_b":"link6","contact_count":2.0,"contact_point_centroid":[0.50951,0.32159,-0.0],"force_p95":91.65963,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":93.67237,"mean_force":73.54493,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53042,0.13776,0.05921]},{"body_a":"world","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.52045,0.19417,-4e-05],"force_p95":79.56338,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":82.15168,"mean_force":53.14953,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53042,0.13777,0.05921]},{"body_a":"peg","body_b":"world","contact_count":66.0,"contact_point_centroid":[0.50003,0.12955,-0.0006],"force_p95":51.7298,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":52.26427,"mean_force":33.67406,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.51769,0.13148,0.05636]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":274.0,"contact_point_centroid":[0.47458,0.11981,0.02812],"force_p95":35.03209,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":36.18514,"mean_force":23.71213,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.53055,0.13628,0.05885]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":31.0,"contact_point_centroid":[0.52523,0.11183,0.04951],"force_p95":21.82123,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":34.34956,"mean_force":8.61968,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50929,0.11396,0.04817]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.52326,0.13627,0.05017],"force_p95":23.50272,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":26.05382,"mean_force":9.03346,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53042,0.13777,0.05921]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":3.0,"contact_point_centroid":[0.47477,0.11985,0.02885],"force_p95":21.92406,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":24.22697,"mean_force":8.85885,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53042,0.13777,0.05921]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.49901,0.11988,0.0098],"force_p95":3.56313,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.77648,"mean_force":2.33821,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53042,0.13777,0.05921]}],"total_contact_groups":18},"final_pose_error":0.22075,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5,0.13547,0.03612],"final_tcp_position":[0.53043,0.1378,0.05924],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":6288.99662,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":265.0,"n_steps_budget":600.0,"object_pos_end":[0.50371,0.11184,0.03389],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19197,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.51579,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":259.0,"raw_peak_contact_force":2.06328,"subtask_id":"reach_above_peg","tcp_end":[0.50635,0.12377,0.17502],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14167,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":476.0,"n_steps_budget":1000.0,"object_pos_end":[0.50756,0.11183,0.02839],"object_pos_start":[0.50371,0.11184,0.03389],"object_to_goal_dist_end":0.19233,"object_to_goal_dist_start":0.19197,"object_z_max":0.03404,"peak_contact_force":215.23236,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":622.0,"raw_peak_contact_force":215.23236,"subtask_id":"contact_peg","tcp_end":[0.51046,0.11405,0.04715],"tcp_start":[0.50635,0.12377,0.17502],"tcp_to_object_dist_end":0.01911,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":455.0,"n_steps_budget":600.0,"object_pos_end":[0.50002,0.13541,0.03611],"object_pos_start":[0.50756,0.11183,0.02839],"object_to_goal_dist_end":0.21545,"object_to_goal_dist_start":0.19233,"object_z_max":0.03679,"peak_contact_force":378.34729,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1760.0,"raw_peak_contact_force":713.68433,"subtask_id":"contact_peg","tcp_end":[0.5304,0.13776,0.05921],"tcp_start":[0.51046,0.11405,0.04715],"tcp_to_object_dist_end":0.03824,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":3.0,"n_steps_budget":900.0,"object_pos_end":[0.50002,0.13543,0.03611],"object_pos_start":[0.50002,0.13541,0.03611],"object_to_goal_dist_end":0.21546,"object_to_goal_dist_start":0.21545,"object_z_max":0.03611,"peak_contact_force":82.15168,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":14.0,"raw_peak_contact_force":93.67237,"subtask_id":"push_through_channel","tcp_end":[0.53043,0.1378,0.05924],"tcp_start":[0.53043,0.13778,0.05923],"tcp_to_object_dist_end":0.03828,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```