## Search State

- **Seed**: 6
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → descend → contact → push → retract → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | force_threshold_switch | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.5933 | 0.68 | ❌ rejected |
| 4 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 2 | 0.5922 | 0.78 | ❌ rejected |
| 3 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | impedance_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.1566 | 0.32 | ❌ rejected |
| 2 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.5883 | 0.66 | ❌ rejected |
| 1 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 2 | 0.6156 | 0.82 | ✅ accepted |

**Proposal policy**: task_score is 0.68 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `07dc0764c781629358e2f97446117d9c410d14c078397be91277b4276116a1de`
- Frozen object start: [0.5030531481177555, 0.06746166958506708, 0.04]
- Frozen task target: [0.5030531481177555, -0.09253833041493292, 0.04]
- Goal object position: (0.5030531481177555, -0.09253833041493292, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5030531481177555, 0.06746166958506708, 0.04)
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
  frozen_object_start: [0.5031, 0.0675, 0.04]
  frozen_task_target: [0.5031, -0.0925, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5030531481177555, 0.06746166958506708, 0.04]}
  frozen_targets: {'channel_exit': [0.5030531481177555, -0.09253833041493292, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: 07dc0764c781629358e2f97446117d9c410d14c078397be91277b4276116a1de

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.822, which indicates the subtask decomposition is already effective.
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
| `object` | offset from object initial position (0.5030531481177555, 0.06746166958506708, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5030531481177555, -0.09253833041493292, 0.04) | final destination targets |
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

## Current Skill (Q=0.593) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: reach_contact
  anchor: object
  offset:
  - 0.0
  - 0.03
  - 0.0
  weight: 0.3
- id: goal_progress
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
    entity: peg
    offset:
    - 0.0
    - 0.08
    - 0.12
    tolerance: 0.01
    orientation:
      mode: keep_current
  subtask_id: reach_contact
- id: descend_1
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
    - 0.04
    - 0.0
    tolerance: 0.008
    orientation:
      mode: keep_current
  subtask_id: reach_contact
- id: push_1
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
      distance: 0.16
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    insertion_depth:
      type: scalar
      range:
      - 0.1
      - 0.2
      default: 0.16
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
  guards:
  - id: force_safety
    when: during_phase
    predicate: force_below
    threshold: 50.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: reduce_speed
  subtask_id: goal_progress
- id: retract_1
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

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.08, 0.12], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.04, 0.0], tolerance=0.008
  - orientation: mode=keep_current
  - parameter_bindings: none
- **push_1** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.16, mode=add_to_offset, sign=positive}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - insertion_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_safety, when=during_phase, predicate=force_below, on_failure=retry, threshold=50.0
  - retries: max_attempts=2, strategy=reduce_speed
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.593
- **task_score** (E): 0.676
- **fitness_score**: 0.697  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.167
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.270

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1346 |
| descend_1 | 1.00 | 1.00 | 0.1396 |
| seat_1 | 1.00 | 1.00 | 0.0024 |
| push_1 | 0.33 | 1.00 | 0.0565 |
| retract_y | 1.00 | 1.00 | 0.0121 |
| retract_z | 1.00 | 1.00 | 0.0805 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.497, 0.180, 0.169) | (0.500, 0.099, 0.040)→(0.501, 0.099, 0.034) | 0.180→0.180 | 1.00 / 1.000 | 0.518 | 2.127 |
| descend_1 | descend | 1.00 / step_budget | (0.497, 0.180, 0.169)→(0.497, 0.128, 0.040) | (0.501, 0.099, 0.034)→(0.501, 0.098, 0.035) | 0.180→0.178 | 1.00 / 1.667 | 7.323 | 12.368 |
| seat_1 | contact | 1.00 / force_exceeded | (0.497, 0.128, 0.040)→(0.496, 0.127, 0.038) | (0.501, 0.098, 0.035)→(0.500, 0.097, 0.035) | 0.178→0.177 | 1.00 / 2.000 | 13.645 | 6.970 |
| push_1 | push | 0.33 / guard_failure | (0.493, 0.068, 0.035)→(0.492, 0.012, 0.034) | (0.500, 0.097, 0.035)→(0.504, -0.015, 0.036) | 0.177→0.068 | 1.00 / 2.333 | 17.193 | 29.931 |
| retract_y | retract | 1.00 / step_budget | (0.492, 0.012, 0.034)→(0.489, 0.023, 0.030) | (0.504, -0.015, 0.036)→(0.504, -0.015, 0.034) | 0.068→0.069 | 1.00 / 1.333 | 0.374 | 23.954 |
| retract_z | retract | 1.00 / step_budget | (0.489, 0.023, 0.030)→(0.486, 0.023, 0.111) | (0.504, -0.015, 0.034)→(0.503, -0.015, 0.034) | 0.069→0.069 | 1.00 / 1.000 | 0.561 | 0.663 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.933
- alignment_error: None
- force_efficiency: 0.210
- terminal_score: 0.933
- phase_score: 0.928
- phase_breakdown.reach_contact_score: 0.875
- phase_breakdown.goal_progress_score: 0.952

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.930
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.808
- **K-run variance**: 0.1007
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.203


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `080f370e6b427cbdf66706e7036a0e474f3967ccfc94f129756881a980a10a27`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `1f3f20d8b9dd2cb87de5d9f0723b4addbc88cdcf096cd2177633d23c0fa32881`; realized-scene SHA-256: `07dc0764c781629358e2f97446117d9c410d14c078397be91277b4276116a1de`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50305,0.06746,0.04]},{"name":"goal","value":[0.50305,-0.09254,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.50305,0.06746,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.50305,-0.09254,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.2,"average_solve_count":215.0,"average_success_count":215.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"push_1.insertion_depth":0.18586,"push_1.push_speed":0.02174,"seat_1.seat_force_threshold":9.68013},"optimized_scores":{"best_composite_score":0.8269,"best_fitness_score":0.93024,"best_task_score":0.93284},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":800.0,"contact_point_centroid":[0.49981,0.00215,0.04046],"force_p95":12.14645,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":39.51365,"mean_force":4.3216,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49381,0.01309,0.03329]},{"body_a":"peg","body_b":"channel_base_body","contact_count":28.0,"contact_point_centroid":[0.50675,-0.10035,0.06031],"force_p95":34.61153,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":37.18423,"mean_force":26.17343,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4936,-0.05455,0.03297]},{"body_a":"attachment","body_b":"peg","contact_count":21.0,"contact_point_centroid":[0.5014,-0.06588,0.06147],"force_p95":17.01942,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.14772,"mean_force":4.4317,"phase_index":4.0,"phase_name":"retract_y","phase_type":"retract","tcp_position_centroid":[0.49293,-0.05458,0.03212]},{"body_a":"peg","body_b":"channel_base_body","contact_count":483.0,"contact_point_centroid":[0.50665,-0.02317,0.00994],"force_p95":9.66814,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.7249,"mean_force":5.2042,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49392,0.02005,0.03341]},{"body_a":"peg","body_b":"channel_base_body","contact_count":31.0,"contact_point_centroid":[0.50528,-0.10026,0.06003],"force_p95":12.02329,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.7764,"mean_force":2.31023,"phase_index":4.0,"phase_name":"retract_y","phase_type":"retract","tcp_position_centroid":[0.49231,-0.0522,0.0314]},{"body_a":"peg","body_b":"channel_base_body","contact_count":17.0,"contact_point_centroid":[0.5069,0.04923,0.00979],"force_p95":4.94898,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.96821,"mean_force":1.33231,"phase_index":2.0,"phase_name":"seat_1","phase_type":"contact","tcp_position_centroid":[0.49829,0.0957,0.03855]},{"body_a":"attachment","body_b":"peg","contact_count":6.0,"contact_point_centroid":[0.50023,0.0833,0.04367],"force_p95":8.91226,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.82562,"mean_force":2.86631,"phase_index":2.0,"phase_name":"seat_1","phase_type":"contact","tcp_position_centroid":[0.49789,0.09509,0.03809]},{"body_a":"peg","body_b":"channel_base_body","contact_count":517.0,"contact_point_centroid":[0.50295,0.0672,0.00938],"force_p95":0.55072,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.57323,"mean_force":0.59321,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49839,0.12408,0.1029]},{"body_a":"attachment","body_b":"peg","contact_count":5.0,"contact_point_centroid":[0.50158,0.08507,0.05233],"force_p95":10.10762,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.40703,"mean_force":5.06568,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49899,0.09706,0.04108]},{"body_a":"peg","body_b":"channel_base_body","contact_count":66.0,"contact_point_centroid":[0.50917,-0.08212,0.00971],"force_p95":7.5113,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.25835,"mean_force":1.34421,"phase_index":4.0,"phase_name":"retract_y","phase_type":"retract","tcp_position_centroid":[0.49183,-0.05053,0.03085]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":612.0,"contact_point_centroid":[0.52509,-0.00804,0.02618],"force_p95":5.14826,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.27148,"mean_force":1.86734,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49373,0.01826,0.03319]},{"body_a":"peg","body_b":"channel_base_body","contact_count":412.0,"contact_point_centroid":[0.50304,0.0674,0.00933],"force_p95":0.57772,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.56752,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49926,0.17525,0.23185]},{"body_a":"peg","body_b":"channel_base_body","contact_count":243.0,"contact_point_centroid":[0.50348,-0.08156,0.00939],"force_p95":0.63285,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.78652,"mean_force":0.54695,"phase_index":5.0,"phase_name":"retract_z","phase_type":"retract","tcp_position_centroid":[0.48778,-0.04402,0.06865]}],"total_contact_groups":13},"final_pose_error":0.0197,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5037,-0.08179,0.03384],"final_tcp_position":[0.48757,-0.04412,0.10998],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":39.51365,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":428.0,"n_steps_budget":930.0,"object_pos_end":[0.50302,0.06748,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14764,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54513,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":412.0,"raw_peak_contact_force":2.06903,"subtask_id":"reach_contact","tcp_end":[0.50001,0.15159,0.16827],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15864,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":517.0,"n_steps_budget":930.0,"object_pos_end":[0.50281,0.06667,0.03431],"object_pos_start":[0.50302,0.06748,0.0338],"object_to_goal_dist_end":0.14681,"object_to_goal_dist_start":0.14764,"object_z_max":0.03418,"peak_contact_force":10.57323,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":522.0,"raw_peak_contact_force":10.57323,"subtask_id":"reach_contact","tcp_end":[0.49898,0.09634,0.03944],"tcp_start":[0.50001,0.15159,0.16827],"tcp_to_object_dist_end":0.03035,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.50234,0.06543,0.03537],"object_pos_start":[0.50281,0.06667,0.03431],"object_to_goal_dist_end":0.14552,"object_to_goal_dist_start":0.14681,"object_z_max":0.03544,"peak_contact_force":14.49664,"phase_name":"seat_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":23.0,"raw_peak_contact_force":10.96821,"subtask_id":"reach_contact","tcp_end":[0.4975,0.09455,0.03762],"tcp_start":[0.49898,0.09634,0.03944],"tcp_to_object_dist_end":0.02961,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":931.0,"n_steps_budget":1000.0,"object_pos_end":[0.50548,-0.08212,0.03612],"object_pos_start":[0.50234,0.06543,0.03537],"object_to_goal_dist_end":0.00704,"object_to_goal_dist_start":0.14552,"object_z_max":0.0366,"peak_contact_force":21.42441,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1923.0,"raw_peak_contact_force":39.51365,"subtask_id":"goal_progress","tcp_end":[0.49351,-0.05544,0.03281],"tcp_start":[0.49353,-0.05544,0.03285],"tcp_to_object_dist_end":0.02943,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":66.0,"n_steps_budget":600.0,"object_pos_end":[0.50403,-0.08185,0.03425],"object_pos_start":[0.5054,-0.0822,0.03608],"object_to_goal_dist_end":0.00726,"object_to_goal_dist_start":0.00703,"object_z_max":0.03608,"peak_contact_force":0.01041,"phase_name":"retract_y","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":118.0,"raw_peak_contact_force":17.14772,"tcp_end":[0.49061,-0.04435,0.02944],"tcp_start":[0.49351,-0.05544,0.03281],"tcp_to_object_dist_end":0.04012,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":243.0,"n_steps_budget":630.0,"object_pos_end":[0.5037,-0.08179,0.03384],"object_pos_start":[0.50403,-0.08185,0.03425],"object_to_goal_dist_end":0.00741,"object_to_goal_dist_start":0.00726,"object_z_max":0.03425,"peak_contact_force":0.55327,"phase_name":"retract_z","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":243.0,"raw_peak_contact_force":0.78652,"tcp_end":[0.48757,-0.04412,0.10998],"tcp_start":[0.49061,-0.04435,0.02944],"tcp_to_object_dist_end":0.08647,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `625c03a21403c0f6267b643060335ee3d751a26340ace08db5429afcee4c5ccf`; realized-scene SHA-256: `d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51001,0.11178,0.04]},{"name":"goal","value":[0.51001,-0.04822,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.51001,0.11178,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.51001,-0.04822,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.20909,"average_solve_count":220.0,"average_success_count":220.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"push_1.insertion_depth":0.1925,"push_1.push_speed":0.01451,"seat_1.seat_force_threshold":6.75735},"optimized_scores":{"best_composite_score":0.80827,"best_fitness_score":0.9116,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":489.0,"contact_point_centroid":[0.50354,0.1112,0.00941],"force_p95":0.60396,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.17485,"mean_force":0.62768,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50218,0.16607,0.10373]},{"body_a":"attachment","body_b":"peg","contact_count":5.0,"contact_point_centroid":[0.50215,0.12904,0.04796],"force_p95":11.76079,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.81337,"mean_force":8.45061,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50021,0.14097,0.04161]},{"body_a":"attachment","body_b":"peg","contact_count":819.0,"contact_point_centroid":[0.50081,0.03693,0.04128],"force_p95":8.89446,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.33736,"mean_force":2.72143,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49557,0.04815,0.03442]},{"body_a":"peg","body_b":"channel_base_body","contact_count":502.0,"contact_point_centroid":[0.50655,0.01046,0.00992],"force_p95":8.30926,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.47054,"mean_force":4.48144,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49573,0.05438,0.03461]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":577.0,"contact_point_centroid":[0.52507,0.01926,0.02376],"force_p95":4.13155,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.838,"mean_force":1.24335,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49553,0.04635,0.03438]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.50284,0.09302,0.00987],"force_p95":5.23165,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.23165,"mean_force":5.23165,"phase_index":2.0,"phase_name":"seat_1","phase_type":"contact","tcp_position_centroid":[0.50014,0.14032,0.03999]},{"body_a":"attachment","body_b":"peg","contact_count":9.0,"contact_point_centroid":[0.503,0.12816,0.05967],"force_p95":3.17259,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.21669,"mean_force":0.65033,"phase_index":2.0,"phase_name":"seat_1","phase_type":"contact","tcp_position_centroid":[0.49975,0.14001,0.03943]},{"body_a":"peg","body_b":"channel_base_body","contact_count":379.0,"contact_point_centroid":[0.50355,0.11171,0.00936],"force_p95":0.62508,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.56511,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50247,0.19523,0.23127]},{"body_a":"peg","body_b":"channel_base_body","contact_count":70.0,"contact_point_centroid":[0.50631,-0.05926,0.0096],"force_p95":0.78565,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.64814,"mean_force":0.57391,"phase_index":4.0,"phase_name":"retract_y","phase_type":"retract","tcp_position_centroid":[0.49366,-0.02485,0.03224]},{"body_a":"attachment","body_b":"peg","contact_count":9.0,"contact_point_centroid":[0.50158,-0.03981,0.05422],"force_p95":0.65669,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.90653,"mean_force":0.15706,"phase_index":4.0,"phase_name":"retract_y","phase_type":"retract","tcp_position_centroid":[0.49459,-0.02832,0.03331]},{"body_a":"peg","body_b":"channel_base_body","contact_count":242.0,"contact_point_centroid":[0.50679,-0.05706,0.00939],"force_p95":0.58218,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62666,"mean_force":0.54636,"phase_index":5.0,"phase_name":"retract_z","phase_type":"retract","tcp_position_centroid":[0.48966,-0.01826,0.06993]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49988,0.19958,0.29877]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":7.0,"contact_point_centroid":[0.52502,-0.05662,0.05203],"force_p95":0.34735,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.46874,"mean_force":0.08632,"phase_index":4.0,"phase_name":"retract_y","phase_type":"retract","tcp_position_centroid":[0.49323,-0.02251,0.03173]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.52501,-0.05699,0.05876],"force_p95":0.0,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":5.0,"phase_name":"retract_z","phase_type":"retract","tcp_position_centroid":[0.49248,-0.01845,0.03086]}],"total_contact_groups":14},"final_pose_error":0.01996,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50668,-0.05701,0.03377],"final_tcp_position":[0.48944,-0.01837,0.11113],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":12.17485,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":401.0,"n_steps_budget":900.0,"object_pos_end":[0.50371,0.11182,0.03382],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19196,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.53999,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":395.0,"raw_peak_contact_force":2.06328,"subtask_id":"reach_contact","tcp_end":[0.50626,0.19154,0.16903],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15697,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":489.0,"n_steps_budget":930.0,"object_pos_end":[0.50353,0.11081,0.03488],"object_pos_start":[0.50371,0.11182,0.03382],"object_to_goal_dist_end":0.19091,"object_to_goal_dist_start":0.19196,"object_z_max":0.03472,"peak_contact_force":10.9891,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":494.0,"raw_peak_contact_force":12.17485,"subtask_id":"reach_contact","tcp_end":[0.50014,0.14032,0.03999],"tcp_start":[0.50626,0.19154,0.16903],"tcp_to_object_dist_end":0.03014,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":9.0,"n_steps_budget":600.0,"object_pos_end":[0.50334,0.1093,0.03524],"object_pos_start":[0.50353,0.11081,0.03488],"object_to_goal_dist_end":0.18939,"object_to_goal_dist_start":0.19091,"object_z_max":0.03543,"peak_contact_force":7.3286,"phase_name":"seat_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":10.0,"raw_peak_contact_force":5.23165,"subtask_id":"reach_contact","tcp_end":[0.49931,0.13958,0.03889],"tcp_start":[0.50014,0.14032,0.03999],"tcp_to_object_dist_end":0.03076,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50697,-0.05752,0.03611],"object_pos_start":[0.50334,0.1093,0.03524],"object_to_goal_dist_end":0.02386,"object_to_goal_dist_start":0.18939,"object_z_max":0.03698,"peak_contact_force":0.29863,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1898.0,"raw_peak_contact_force":11.33736,"subtask_id":"goal_progress","tcp_end":[0.49549,-0.0297,0.03436],"tcp_start":[0.49931,0.13958,0.03889],"tcp_to_object_dist_end":0.03014,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":72.0,"n_steps_budget":600.0,"object_pos_end":[0.50686,-0.057,0.03388],"object_pos_start":[0.50697,-0.05752,0.03611],"object_to_goal_dist_end":0.02477,"object_to_goal_dist_start":0.02386,"object_z_max":0.03611,"peak_contact_force":0.55939,"phase_name":"retract_y","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":86.0,"raw_peak_contact_force":1.64814,"tcp_end":[0.49248,-0.01845,0.03086],"tcp_start":[0.49549,-0.0297,0.03436],"tcp_to_object_dist_end":0.04125,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":242.0,"n_steps_budget":630.0,"object_pos_end":[0.50668,-0.05701,0.03377],"object_pos_start":[0.50686,-0.057,0.03388],"object_to_goal_dist_end":0.02473,"object_to_goal_dist_start":0.02477,"object_z_max":0.03388,"peak_contact_force":0.58116,"phase_name":"retract_z","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":243.0,"raw_peak_contact_force":0.62666,"tcp_end":[0.48944,-0.01837,0.11113],"tcp_start":[0.49248,-0.01845,0.03086],"tcp_to_object_dist_end":0.08818,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `abe38b4b57ac37a91047e57d04e408cb1fd05583a47670bcb186dc9505a3f021`; realized-scene SHA-256: `c5fb87552d009c7e1ef813cadc54d289d6d9c896c1dd51a37fa468bf6305165e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48616,0.11898,0.04]},{"name":"goal","value":[0.48616,-0.04102,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48616,0.11898,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48616,-0.04102,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.31579,"average_solve_count":133.0,"average_success_count":133.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"push_1.insertion_depth":0.16982,"push_1.push_speed":0.03242,"seat_1.seat_force_threshold":15.17207},"optimized_scores":{"best_composite_score":0.14462,"best_fitness_score":0.24795,"best_task_score":0.09617},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":22.0,"contact_point_centroid":[0.47499,0.12,0.03515],"force_p95":51.29498,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":53.0665,"mean_force":35.12768,"phase_index":4.0,"phase_name":"retract_y","phase_type":"retract","tcp_position_centroid":[0.48667,0.12179,0.03325]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":5.0,"contact_point_centroid":[0.47499,0.12,0.03582],"force_p95":37.12419,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":38.94128,"mean_force":28.53208,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48672,0.12155,0.03392]},{"body_a":"peg","body_b":"channel_base_body","contact_count":517.0,"contact_point_centroid":[0.49607,0.11845,0.00945],"force_p95":0.61582,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.35701,"mean_force":0.67607,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48707,0.1726,0.10381]},{"body_a":"attachment","body_b":"peg","contact_count":8.0,"contact_point_centroid":[0.49397,0.13613,0.05081],"force_p95":13.88542,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.03973,"mean_force":9.12882,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49131,0.14803,0.04191]},{"body_a":"peg","body_b":"channel_base_body","contact_count":82.0,"contact_point_centroid":[0.50096,0.09114,0.00985],"force_p95":10.80652,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.82602,"mean_force":3.12334,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48774,0.13374,0.03523]},{"body_a":"attachment","body_b":"peg","contact_count":69.0,"contact_point_centroid":[0.49182,0.12259,0.03994],"force_p95":10.81417,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.436,"mean_force":3.1416,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48787,0.13397,0.03538]},{"body_a":"peg","body_b":"channel_base_body","contact_count":14.0,"contact_point_centroid":[0.496,0.09992,0.00997],"force_p95":1.96327,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.70909,"mean_force":0.73685,"phase_index":2.0,"phase_name":"seat_1","phase_type":"contact","tcp_position_centroid":[0.49086,0.14666,0.03902]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.49232,0.13416,0.03801],"force_p95":4.0194,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.4262,"mean_force":1.69852,"phase_index":2.0,"phase_name":"seat_1","phase_type":"contact","tcp_position_centroid":[0.49029,0.14587,0.03834]},{"body_a":"peg","body_b":"channel_base_body","contact_count":366.0,"contact_point_centroid":[0.49639,0.11912,0.00944],"force_p95":0.62218,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.55843,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49157,0.1985,0.2312]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49947,0.19956,0.2975]},{"body_a":"peg","body_b":"channel_base_body","contact_count":86.0,"contact_point_centroid":[0.50017,0.09009,0.00967],"force_p95":0.64017,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.72372,"mean_force":0.53209,"phase_index":4.0,"phase_name":"retract_y","phase_type":"retract","tcp_position_centroid":[0.48563,0.12574,0.03192]},{"body_a":"peg","body_b":"channel_base_body","contact_count":245.0,"contact_point_centroid":[0.49991,0.09496,0.00939],"force_p95":0.55491,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57532,"mean_force":0.54657,"phase_index":5.0,"phase_name":"retract_z","phase_type":"retract","tcp_position_centroid":[0.48125,0.13178,0.06948]},{"body_a":"attachment","body_b":"peg","contact_count":22.0,"contact_point_centroid":[0.49453,0.11101,0.05985],"force_p95":0.27504,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27828,"mean_force":0.16049,"phase_index":4.0,"phase_name":"retract_y","phase_type":"retract","tcp_position_centroid":[0.48656,0.12237,0.03291]}],"total_contact_groups":13},"final_pose_error":0.0197,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49979,0.0953,0.03384],"final_tcp_position":[0.48107,0.13162,0.11079],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":119.94908,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":391.0,"n_steps_budget":900.0,"object_pos_end":[0.49602,0.11907,0.03413],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.1992,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.46818,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":390.0,"raw_peak_contact_force":2.24822,"subtask_id":"reach_contact","tcp_end":[0.48497,0.19798,0.16969],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15724,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":517.0,"n_steps_budget":930.0,"object_pos_end":[0.49583,0.1175,0.03517],"object_pos_start":[0.49602,0.11907,0.03413],"object_to_goal_dist_end":0.19761,"object_to_goal_dist_start":0.1992,"object_z_max":0.03504,"peak_contact_force":0.40596,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":525.0,"raw_peak_contact_force":14.35701,"subtask_id":"reach_contact","tcp_end":[0.49146,0.14727,0.03985],"tcp_start":[0.48497,0.19798,0.16969],"tcp_to_object_dist_end":0.03044,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":17.0,"n_steps_budget":600.0,"object_pos_end":[0.49534,0.11655,0.03557],"object_pos_start":[0.49583,0.1175,0.03517],"object_to_goal_dist_end":0.19666,"object_to_goal_dist_start":0.19761,"object_z_max":0.0357,"peak_contact_force":19.1092,"phase_name":"seat_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":17.0,"raw_peak_contact_force":4.70909,"subtask_id":"reach_contact","tcp_end":[0.49018,0.14566,0.0382],"tcp_start":[0.49146,0.14727,0.03985],"tcp_to_object_dist_end":0.02968,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":128.0,"n_steps_budget":1000.0,"object_pos_end":[0.4998,0.09401,0.03632],"object_pos_start":[0.49534,0.11655,0.03557],"object_to_goal_dist_end":0.17405,"object_to_goal_dist_start":0.19666,"object_z_max":0.03691,"peak_contact_force":29.85583,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":156.0,"raw_peak_contact_force":38.94128,"subtask_id":"goal_progress","tcp_end":[0.48678,0.12119,0.03391],"tcp_start":[0.48675,0.12128,0.03392],"tcp_to_object_dist_end":0.03023,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":86.0,"n_steps_budget":600.0,"object_pos_end":[0.49969,0.09518,0.03386],"object_pos_start":[0.49985,0.09374,0.03618],"object_to_goal_dist_end":0.17528,"object_to_goal_dist_start":0.17379,"object_z_max":0.03618,"peak_contact_force":0.5527,"phase_name":"retract_y","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":130.0,"raw_peak_contact_force":53.0665,"tcp_end":[0.48405,0.13242,0.03025],"tcp_start":[0.48678,0.12119,0.03391],"tcp_to_object_dist_end":0.04055,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":245.0,"n_steps_budget":630.0,"object_pos_end":[0.49979,0.0953,0.03384],"object_pos_start":[0.49969,0.09518,0.03386],"object_to_goal_dist_end":0.1754,"object_to_goal_dist_start":0.17528,"object_z_max":0.03386,"peak_contact_force":0.54846,"phase_name":"retract_z","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":245.0,"raw_peak_contact_force":0.57532,"tcp_end":[0.48107,0.13162,0.11079],"tcp_start":[0.48405,0.13242,0.03025],"tcp_to_object_dist_end":0.08713,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```