## Search State

- **Seed**: 5
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9 | -0.2422 | 0.22 | ✅ accepted |
| 6 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | pose_tolerance | time_limit | pose_tolerance | 9 | -0.2436 | 0.22 | ✅ accepted |
| 5 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | pose_tolerance | time_limit | pose_tolerance | 8 | -0.1804 | 0.19 | ✅ accepted |
| 4 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | pose_tolerance | time_limit | pose_tolerance | 6 | -0.1141 | 0.14 | ✅ accepted |
| 3 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 2 | -0.0183 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.22 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.242) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: reach_approach
  anchor: object
  offset:
  - 0.0
  - 0.03
  - 0.0
  weight: 0.3
- id: push_to_goal
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
    entity: peg
    offset:
    - 0.0
    - 0.03
    - 0.0
    tolerance: 0.02
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: channel_axis
      tolerance: 0.1
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
    approach_tol:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.005
    - 0.0
  subtask_id: reach_approach
- id: descend_to_peg
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
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
    descend_tol:
      type: scalar
      range:
      - 0.005
      - 0.03
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: reach_approach
- id: push_channel
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
      distance: 0.2
      axis: channel_axis
      mode: replace_offset_projection
      sign: positive
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.15
      - 0.3
      default: 0.2
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_duration:
      type: scalar
      range:
      - 5.0
      - 20.0
      default: 12.0
      binds_to:
      - path: duration.max_time
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: push_to_goal
- id: retract_away
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
    tolerance: 0.05
    orientation:
      mode: none
  parameters:
    retract_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
    retract_tol:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: push_to_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_behind** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.03, 0.0], tolerance=0.02
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - approach_tol: status=consumed; consumers=termination.pose_tolerance (replace)
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.005, 0.0]
- **descend_to_peg** (`descend`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - descend_tol: status=consumed; consumers=termination.pose_tolerance (replace)
- **push_channel** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.2, mode=replace_offset_projection, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_duration: status=consumed; consumers=duration.max_time (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
- **retract_away** (`retract`)
  - target: source=yaml, anchor=world, offset=[0.5, 0.2, 0.3], tolerance=0.05
  - orientation: mode=none
  - parameter_bindings:
    - retract_speed: status=consumed; consumers=generator.speed (replace)
    - retract_tol: status=consumed; consumers=termination.pose_tolerance (replace)

## Design Metrics

- **Composite score**: -0.242
- **task_score** (E): 0.224
- **fitness_score**: 0.268  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.510

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_behind | 1.00 | 1.00 | 0.2524 |
| descend_to_peg | 1.00 | 1.00 | 0.0096 |
| push_channel | 1.00 | 1.00 | 0.0384 |
| retract_away | 1.00 | 1.00 | 0.2259 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_behind | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.509, 0.130, 0.059) | (0.512, 0.095, 0.040)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 1.000 | 0.534 | 2.488 |
| descend_to_peg | descend | 1.00 / step_budget | (0.509, 0.130, 0.059)→(0.509, 0.123, 0.053) | (0.504, 0.095, 0.034)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 2.000 | 320.112 | 332.843 |
| push_channel | push | 1.00 / time_limit | (0.509, 0.123, 0.053)→(0.512, 0.086, 0.050) | (0.504, 0.095, 0.034)→(0.504, 0.054, 0.038) | 0.175→0.134 | 1.00 / 2.333 | 317.576 | 458.644 |
| retract_away | retract | 1.00 / step_budget | (0.512, 0.086, 0.050)→(0.502, 0.182, 0.254) | (0.504, 0.054, 0.038)→(0.503, 0.039, 0.027) | 0.134→0.120 | 1.00 / 1.000 | 0.516 | 268.468 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.487
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.363
- phase_score: 0.353
- phase_breakdown.push_to_goal_score: 0.178
- phase_breakdown.reach_approach_score: 0.762

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.357
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.363
- **Median Q (composite search score)**: -0.239
- **K-run variance**: 0.0056
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.245


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.78866,"average_solve_count":194.0,"average_success_count":194.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.07817,"approach_behind.approach_tol":0.03748,"descend_to_peg.descend_speed":0.09115,"descend_to_peg.descend_tol":0.0173,"push_channel.push_distance":0.23739,"push_channel.push_duration":13.32276,"push_channel.push_speed":0.06448,"retract_away.retract_speed":0.08334,"retract_away.retract_tol":0.03551},"optimized_scores":{"best_composite_score":-0.23875,"best_fitness_score":0.27125,"best_task_score":0.20946},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link7","contact_count":221.0,"contact_point_centroid":[0.47495,0.11992,0.05603],"force_p95":532.07516,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":617.20492,"mean_force":384.80218,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51317,0.07952,0.04992]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":770.0,"contact_point_centroid":[0.52503,0.10641,0.05443],"force_p95":319.90527,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":464.29539,"mean_force":199.77209,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51404,0.10564,0.05078]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":6.0,"contact_point_centroid":[0.47494,0.1199,0.06],"force_p95":425.69903,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":455.79993,"mean_force":219.67798,"phase_index":3.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.51307,0.08027,0.0493]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.52504,0.08128,0.04932],"force_p95":318.33911,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":322.66755,"mean_force":218.16155,"phase_index":3.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.51314,0.0802,0.04928]},{"body_a":"world","body_b":"link7","contact_count":225.0,"contact_point_centroid":[0.50928,0.18067,-2e-05],"force_p95":261.56554,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":309.91922,"mean_force":112.60882,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51497,0.11764,0.05127]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":80.0,"contact_point_centroid":[0.52501,0.11993,0.06],"force_p95":255.10356,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":296.70261,"mean_force":122.07563,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51312,0.07919,0.0503]},{"body_a":"world","body_b":"link7","contact_count":364.0,"contact_point_centroid":[0.51473,0.19579,-8e-05],"force_p95":240.46574,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":264.5185,"mean_force":210.20907,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.5161,0.13285,0.05294]},{"body_a":"attachment","body_b":"peg","contact_count":702.0,"contact_point_centroid":[0.50678,0.10679,0.05278],"force_p95":3.24765,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":97.40981,"mean_force":1.43488,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.5141,0.10743,0.05086]},{"body_a":"peg","body_b":"channel_base_body","contact_count":975.0,"contact_point_centroid":[0.50489,0.07972,0.00987],"force_p95":2.28097,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":73.56885,"mean_force":1.40322,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.5143,0.10939,0.05093]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":45.0,"contact_point_centroid":[0.52508,0.0994,0.02727],"force_p95":27.5587,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":57.47968,"mean_force":4.34292,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51433,0.11738,0.05095]},{"body_a":"peg","body_b":"channel_base_body","contact_count":498.0,"contact_point_centroid":[0.50563,0.10458,0.00937],"force_p95":0.57754,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.56906,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50395,0.17603,0.17617]},{"body_a":"peg","body_b":"channel_base_body","contact_count":249.0,"contact_point_centroid":[0.50422,0.03549,0.00824],"force_p95":0.95904,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.74276,"mean_force":0.61749,"phase_index":3.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.50715,0.12983,0.15004]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50397,0.21875,0.28998]},{"body_a":"peg","body_b":"channel_base_body","contact_count":381.0,"contact_point_centroid":[0.50575,0.10472,0.00939],"force_p95":0.57566,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57647,"mean_force":0.54627,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.51618,0.13306,0.0531]}],"total_contact_groups":14},"final_pose_error":0.04928,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50398,0.03217,0.02409],"final_tcp_position":[0.50238,0.18068,0.25473],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":617.20492,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":525.0,"n_steps_budget":1000.0,"object_pos_end":[0.50583,0.10463,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18483,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.54994,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":530.0,"raw_peak_contact_force":3.33087,"subtask_id":"reach_approach","tcp_end":[0.51939,0.13909,0.0587],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.0446,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":381.0,"n_steps_budget":600.0,"object_pos_end":[0.50593,0.10472,0.03383],"object_pos_start":[0.50583,0.10463,0.03384],"object_to_goal_dist_end":0.18492,"object_to_goal_dist_start":0.18483,"object_z_max":0.03384,"peak_contact_force":240.40926,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":745.0,"raw_peak_contact_force":264.5185,"subtask_id":"reach_approach","tcp_end":[0.51598,0.13058,0.05199],"tcp_start":[0.51939,0.13909,0.0587],"tcp_to_object_dist_end":0.03316,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50508,0.05022,0.03969],"object_pos_start":[0.50593,0.10472,0.03383],"object_to_goal_dist_end":0.13032,"object_to_goal_dist_start":0.18492,"object_z_max":0.04079,"peak_contact_force":530.04699,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3018.0,"raw_peak_contact_force":617.20492,"subtask_id":"push_to_goal","tcp_end":[0.51321,0.08019,0.04929],"tcp_start":[0.51598,0.13058,0.05199],"tcp_to_object_dist_end":0.0325,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":257.0,"n_steps_budget":1000.0,"object_pos_end":[0.50398,0.03217,0.02409],"object_pos_start":[0.50508,0.05022,0.03969],"object_to_goal_dist_end":0.11336,"object_to_goal_dist_start":0.13032,"object_z_max":0.03969,"peak_contact_force":0.49887,"phase_name":"retract_away","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":258.0,"raw_peak_contact_force":455.79993,"subtask_id":"push_to_goal","tcp_end":[0.50238,0.18068,0.25473],"tcp_start":[0.51321,0.08019,0.04929],"tcp_to_object_dist_end":0.27432,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.84459,"average_solve_count":148.0,"average_success_count":148.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.12513,"approach_behind.approach_tol":0.02162,"descend_to_peg.descend_speed":0.06194,"descend_to_peg.descend_tol":0.01134,"push_channel.push_distance":0.2195,"push_channel.push_duration":11.68964,"push_channel.push_speed":0.1252,"retract_away.retract_speed":0.11779,"retract_away.retract_tol":0.05694},"optimized_scores":{"best_composite_score":-0.33535,"best_fitness_score":0.17465,"best_task_score":0.09899},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link7","contact_count":390.0,"contact_point_centroid":[0.50219,0.16231,-9e-05],"force_p95":370.66135,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":382.24695,"mean_force":326.84651,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50089,0.10035,0.0542]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":833.0,"contact_point_centroid":[0.47075,0.11988,0.05983],"force_p95":232.5857,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":361.564,"mean_force":220.42799,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50814,0.08748,0.05176]},{"body_a":"world","body_b":"link7","contact_count":145.0,"contact_point_centroid":[0.50416,0.15548,-2e-05],"force_p95":132.66906,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":252.03612,"mean_force":98.2169,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50355,0.0932,0.05398]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.46926,0.11993,0.06],"force_p95":125.49187,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":129.6606,"mean_force":73.45902,"phase_index":3.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.51191,0.09442,0.05156]},{"body_a":"peg","body_b":"channel_base_body","contact_count":979.0,"contact_point_centroid":[0.50502,0.05386,0.00942],"force_p95":0.64709,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.73795,"mean_force":0.61976,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50745,0.0886,0.05209]},{"body_a":"attachment","body_b":"peg","contact_count":27.0,"contact_point_centroid":[0.50312,0.08283,0.05281],"force_p95":17.32169,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.47919,"mean_force":2.70859,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50359,0.08267,0.05379]},{"body_a":"peg","body_b":"channel_base_body","contact_count":486.0,"contact_point_centroid":[0.503,0.06746,0.00933],"force_p95":0.55991,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.56435,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.49492,0.15994,0.17222]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":48.0,"contact_point_centroid":[0.52527,0.05225,0.04451],"force_p95":0.58109,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.93731,"mean_force":0.24798,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50451,0.08154,0.05338]},{"body_a":"peg","body_b":"channel_base_body","contact_count":241.0,"contact_point_centroid":[0.5061,0.05166,0.00939],"force_p95":0.55245,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55964,"mean_force":0.54651,"phase_index":3.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.5066,0.13704,0.14864]},{"body_a":"peg","body_b":"channel_base_body","contact_count":405.0,"contact_point_centroid":[0.50306,0.06745,0.00938],"force_p95":0.5506,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55098,"mean_force":0.54665,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50083,0.10047,0.05427]}],"total_contact_groups":10},"final_pose_error":0.04915,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50587,0.05162,0.0338],"final_tcp_position":[0.50226,0.18282,0.254],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":382.24695,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":502.0,"n_steps_budget":1000.0,"object_pos_end":[0.50307,0.0675,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14766,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.55031,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":486.0,"raw_peak_contact_force":2.06903,"subtask_id":"reach_approach","tcp_end":[0.50008,0.10495,0.05786],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.04461,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":405.0,"n_steps_budget":600.0,"object_pos_end":[0.50306,0.0675,0.0338],"object_pos_start":[0.50307,0.0675,0.0338],"object_to_goal_dist_end":0.14766,"object_to_goal_dist_start":0.14766,"object_z_max":0.0338,"peak_contact_force":369.61343,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":795.0,"raw_peak_contact_force":382.24695,"subtask_id":"reach_approach","tcp_end":[0.50345,0.09911,0.05427],"tcp_start":[0.50008,0.10495,0.05786],"tcp_to_object_dist_end":0.03766,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50595,0.05151,0.03387],"object_pos_start":[0.50306,0.0675,0.0338],"object_to_goal_dist_end":0.13179,"object_to_goal_dist_start":0.14766,"object_z_max":0.03793,"peak_contact_force":200.43729,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2032.0,"raw_peak_contact_force":361.564,"subtask_id":"push_to_goal","tcp_end":[0.51198,0.09438,0.05158],"tcp_start":[0.50345,0.09911,0.05427],"tcp_to_object_dist_end":0.04678,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":241.0,"n_steps_budget":1000.0,"object_pos_end":[0.50587,0.05162,0.0338],"object_pos_start":[0.50595,0.05151,0.03387],"object_to_goal_dist_end":0.1319,"object_to_goal_dist_start":0.13179,"object_z_max":0.03387,"peak_contact_force":0.54676,"phase_name":"retract_away","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":245.0,"raw_peak_contact_force":129.6606,"subtask_id":"push_to_goal","tcp_end":[0.50226,0.18282,0.254],"tcp_start":[0.51198,0.09438,0.05158],"tcp_to_object_dist_end":0.25635,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.95683,"average_solve_count":139.0,"average_success_count":139.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.10381,"approach_behind.approach_tol":0.02382,"descend_to_peg.descend_speed":0.12773,"descend_to_peg.descend_tol":0.01231,"push_channel.push_distance":0.24513,"push_channel.push_duration":12.61942,"push_channel.push_speed":0.06935,"retract_away.retract_speed":0.19669,"retract_away.retract_tol":0.06101},"optimized_scores":{"best_composite_score":-0.15263,"best_fitness_score":0.35737,"best_task_score":0.36321},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link7","contact_count":423.0,"contact_point_centroid":[0.47497,0.11992,0.05517],"force_p95":222.65599,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":397.16229,"mean_force":200.43608,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.5087,0.08216,0.0507]},{"body_a":"world","body_b":"link7","contact_count":360.0,"contact_point_centroid":[0.5068,0.20232,-0.0001],"force_p95":350.73291,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":351.76351,"mean_force":288.79719,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50527,0.13985,0.05359]},{"body_a":"world","body_b":"link7","contact_count":475.0,"contact_point_centroid":[0.50711,0.17767,-2e-05],"force_p95":103.77252,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":311.61636,"mean_force":93.94114,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50623,0.11397,0.05232]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.47498,0.11996,0.06],"force_p95":215.93968,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":219.94459,"mean_force":135.75632,"phase_index":3.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.51143,0.08392,0.04892]},{"body_a":"attachment","body_b":"peg","contact_count":665.0,"contact_point_centroid":[0.50174,0.09214,0.04211],"force_p95":28.99566,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":42.64124,"mean_force":5.33896,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50715,0.09191,0.0517]},{"body_a":"peg","body_b":"channel_base_body","contact_count":986.0,"contact_point_centroid":[0.50099,0.07731,0.00981],"force_p95":25.69717,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":42.60643,"mean_force":4.04478,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50729,0.09971,0.05162]},{"body_a":"peg","body_b":"channel_base_body","contact_count":233.0,"contact_point_centroid":[0.49963,0.04495,0.00895],"force_p95":1.02908,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.44993,"mean_force":0.61617,"phase_index":3.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.50624,0.13145,0.1482]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":9.0,"contact_point_centroid":[0.47496,0.05397,0.02393],"force_p95":5.27839,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.34202,"mean_force":1.46072,"phase_index":3.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.50497,0.1494,0.18635]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":14.0,"contact_point_centroid":[0.47474,0.10211,0.05858],"force_p95":2.03621,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.17706,"mean_force":0.64728,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50602,0.12123,0.05224]},{"body_a":"peg","body_b":"channel_base_body","contact_count":471.0,"contact_point_centroid":[0.50368,0.11169,0.00937],"force_p95":0.61915,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.56099,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.49782,0.17936,0.17428]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":9.0,"contact_point_centroid":[0.525,0.04125,0.05421],"force_p95":0.57716,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63852,"mean_force":0.28455,"phase_index":3.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.50868,0.09957,0.08054]},{"body_a":"peg","body_b":"channel_base_body","contact_count":379.0,"contact_point_centroid":[0.50346,0.1117,0.00939],"force_p95":0.59962,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63193,"mean_force":0.5455,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50526,0.14006,0.05374]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50377,0.20563,0.29957]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":29.0,"contact_point_centroid":[0.52501,0.04974,0.05747],"force_p95":0.18621,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19514,"mean_force":0.06961,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51034,0.08307,0.04957]}],"total_contact_groups":14},"final_pose_error":0.04918,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49913,0.03381,0.02409],"final_tcp_position":[0.5023,0.18142,0.25452],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":397.16229,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":493.0,"n_steps_budget":1000.0,"object_pos_end":[0.50369,0.11177,0.03382],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.1919,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.50122,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":487.0,"raw_peak_contact_force":2.06328,"subtask_id":"reach_approach","tcp_end":[0.50639,0.14561,0.05924],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.04241,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":379.0,"n_steps_budget":600.0,"object_pos_end":[0.50374,0.11177,0.03383],"object_pos_start":[0.50369,0.11177,0.03382],"object_to_goal_dist_end":0.19191,"object_to_goal_dist_start":0.1919,"object_z_max":0.03385,"peak_contact_force":350.31264,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":739.0,"raw_peak_contact_force":351.76351,"subtask_id":"reach_approach","tcp_end":[0.50665,0.13818,0.05266],"tcp_start":[0.50639,0.14561,0.05924],"tcp_to_object_dist_end":0.03256,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50179,0.05985,0.04073],"object_pos_start":[0.50374,0.11177,0.03383],"object_to_goal_dist_end":0.13986,"object_to_goal_dist_start":0.19191,"object_z_max":0.04077,"peak_contact_force":222.24327,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2592.0,"raw_peak_contact_force":397.16229,"subtask_id":"push_to_goal","tcp_end":[0.51149,0.08387,0.04893],"tcp_start":[0.50665,0.13818,0.05266],"tcp_to_object_dist_end":0.02717,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":240.0,"n_steps_budget":900.0,"object_pos_end":[0.49913,0.03381,0.02409],"object_pos_start":[0.50179,0.05985,0.04073],"object_to_goal_dist_end":0.11492,"object_to_goal_dist_start":0.13986,"object_z_max":0.04073,"peak_contact_force":0.50109,"phase_name":"retract_away","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":255.0,"raw_peak_contact_force":219.94459,"subtask_id":"push_to_goal","tcp_end":[0.5023,0.18142,0.25452],"tcp_start":[0.51149,0.08387,0.04893],"tcp_to_object_dist_end":0.27367,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```