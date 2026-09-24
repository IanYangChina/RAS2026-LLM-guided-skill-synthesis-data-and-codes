## Search State

- **Seed**: 6
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.4602 | 0.90 | ✅ accepted |
| 9 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.4457 | 0.70 | ❌ rejected |
| 8 | approach → descend → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.1348 | 0.02 | ❌ rejected |
| 7 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.4227 | 0.75 | ❌ rejected |
| 6 | approach → descend → contact → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.3315 | 0.80 | ❌ rejected |

**Proposal policy**: task_score is near-perfect (0.90). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.901, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.460) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: reach_pre_contact
  anchor: object
  offset:
  - 0.0
  - 0.03
  - 0.1
  weight: 0.3
- id: reach_contact
  anchor: object
  weight: 0.3
- id: reach_goal
  metric: goal_progress
  weight: 0.4
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
    - 0.03
    - 0.1
    tolerance: 0.03
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
        mode: replace
  subtask_id: reach_pre_contact
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
    - 0.03
    - -0.005
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.025
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_contact
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
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
    force_threshold:
      type: scalar
      range:
      - 1.0
      - 5.0
      default: 3.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    speed:
      type: scalar
      range:
      - 0.005
      - 0.02
      default: 0.01
      binds_to:
      - path: generator.speed
        mode: replace
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
    - 0.0
    - -0.005
    - 0.0
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
    tolerance: 0.03
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.12
      - 0.2
      default: 0.16
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.005
      - 0.04
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_goal
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
    - 0.08
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.03, 0.1], tolerance=0.03
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.03, -0.005], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **contact_1** (`contact`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_guard, when=during_phase, predicate=force_below, on_failure=abort, threshold=40.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, -0.005, 0.0]
- **push_1** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.16, mode=add_to_offset, sign=positive}, tolerance=0.03
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.08], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.460
- **task_score** (E): 0.901
- **fitness_score**: 0.767  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.133
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.440

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1470 |
| descend_1 | 1.00 | 1.00 | 0.1189 |
| contact_1 | 0.67 | 1.00 | 0.0125 |
| push_1 | 1.00 | 1.00 | 0.1552 |
| retract_1 | 1.00 | 1.00 | 0.0606 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.498, 0.142, 0.166) | (0.500, 0.099, 0.040)→(0.501, 0.099, 0.034) | 0.180→0.180 | 1.00 / 1.000 | 0.551 | 0.615 |
| descend_1 | descend | 1.00 / step_budget | (0.498, 0.142, 0.166)→(0.497, 0.131, 0.048) | (0.501, 0.099, 0.034)→(0.501, 0.100, 0.034) | 0.180→0.180 | 1.00 / 2.000 | 4.848 | 5.946 |
| contact_1 | contact | 0.67 / force_exceeded | (0.497, 0.131, 0.048)→(0.495, 0.122, 0.041) | (0.501, 0.100, 0.034)→(0.502, 0.092, 0.035) | 0.180→0.172 | 1.00 / 3.000 | 75.303 | 129.228 |
| push_1 | push | 1.00 / step_budget | (0.495, 0.122, 0.041)→(0.493, -0.034, 0.036) | (0.502, 0.092, 0.035)→(0.509, -0.054, 0.033) | 0.172→0.034 | 1.00 / 1.000 | 0.465 | 161.155 |
| retract_1 | retract | 1.00 / step_budget | (0.493, -0.034, 0.036)→(0.490, -0.033, 0.097) | (0.509, -0.054, 0.033)→(0.501, -0.050, 0.038) | 0.034→0.034 | 1.00 / 1.000 | 0.535 | 2.127 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.986
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.986
- phase_score: 0.647
- phase_breakdown.reach_pre_contact_score: 0.552
- phase_breakdown.reach_contact_score: 0.538
- phase_breakdown.reach_goal_score: 0.800

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.808
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.986
- **Median Q (composite search score)**: 0.470
- **K-run variance**: 0.0052
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.373


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.69634,"average_solve_count":382.0,"average_success_count":382.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.05695,"contact_1.force_threshold":4.24416,"contact_1.speed":0.01238,"descend_1.speed":0.03115,"push_1.push_distance":0.17637,"push_1.push_speed":0.02247,"retract_1.speed":0.02732},"optimized_scores":{"best_composite_score":0.36761,"best_fitness_score":0.80761,"best_task_score":0.88068},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":419.0,"contact_point_centroid":[0.50286,-0.03652,0.05367],"force_p95":161.19579,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":171.46903,"mean_force":78.18884,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49528,-0.0262,0.02872]},{"body_a":"peg","body_b":"channel_base_body","contact_count":218.0,"contact_point_centroid":[0.50853,-0.10274,0.05629],"force_p95":154.62281,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":157.1723,"mean_force":127.51418,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49529,-0.06328,0.02816]},{"body_a":"peg","body_b":"channel_base_body","contact_count":261.0,"contact_point_centroid":[0.50859,-0.10115,0.06314],"force_p95":94.79915,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":138.15536,"mean_force":44.02108,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49172,-0.06006,0.05456]},{"body_a":"channel_base_body","body_b":"link7","contact_count":181.0,"contact_point_centroid":[0.54545,-0.1,0.06498],"force_p95":121.63344,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":137.54675,"mean_force":95.39008,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49545,-0.064,0.0282]},{"body_a":"attachment","body_b":"peg","contact_count":250.0,"contact_point_centroid":[0.49823,-0.06955,0.05839],"force_p95":71.73209,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":125.52557,"mean_force":44.00944,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4917,-0.05996,0.05323]},{"body_a":"channel_base_body","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.54633,-0.1,0.06499],"force_p95":120.02985,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":122.6042,"mean_force":92.65553,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49647,-0.06528,0.02851]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":394.0,"contact_point_centroid":[0.52559,-0.05876,0.0479],"force_p95":48.76665,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":82.99499,"mean_force":26.55179,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49518,-0.03294,0.02854]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":216.0,"contact_point_centroid":[0.52532,-0.08455,0.05922],"force_p95":32.12939,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":45.58533,"mean_force":16.43958,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49176,-0.05988,0.04988]},{"body_a":"peg","body_b":"channel_base_body","contact_count":284.0,"contact_point_centroid":[0.51417,-0.08094,0.00976],"force_p95":25.42663,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":41.98332,"mean_force":11.8011,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49536,-0.04222,0.02853]},{"body_a":"peg","body_b":"channel_base_body","contact_count":20.0,"contact_point_centroid":[0.51314,-0.10027,0.00973],"force_p95":20.82119,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.79805,"mean_force":14.79422,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49591,-0.06424,0.02896]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":34.0,"contact_point_centroid":[0.47496,-0.0795,0.03251],"force_p95":6.90387,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.07084,"mean_force":5.43784,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49052,-0.0595,0.06592]},{"body_a":"peg","body_b":"channel_base_body","contact_count":986.0,"contact_point_centroid":[0.50548,0.0404,0.00995],"force_p95":2.49374,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.68907,"mean_force":1.71791,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49721,0.08568,0.03751]},{"body_a":"attachment","body_b":"peg","contact_count":944.0,"contact_point_centroid":[0.50079,0.0733,0.04234],"force_p95":2.17765,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.11919,"mean_force":1.433,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.4972,0.08498,0.03711]},{"body_a":"peg","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.52298,-0.06472,0.06332],"force_p95":3.88796,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.01174,"mean_force":2.77395,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49378,-0.04672,0.02771]},{"body_a":"peg","body_b":"channel_base_body","contact_count":221.0,"contact_point_centroid":[0.50306,0.06735,0.00927],"force_p95":0.8045,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.58558,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50001,0.15677,0.2293]},{"body_a":"peg","body_b":"channel_base_body","contact_count":241.0,"contact_point_centroid":[0.5031,0.06766,0.00938],"force_p95":0.55247,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55954,"mean_force":0.54663,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.4992,0.10759,0.10711]}],"total_contact_groups":16},"final_pose_error":0.0199,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50406,-0.07345,0.05451],"final_tcp_position":[0.4925,-0.06315,0.08912],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":171.46903,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":237.0,"n_steps_budget":1000.0,"object_pos_end":[0.50301,0.06746,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14763,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54508,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":241.0,"raw_peak_contact_force":0.55954,"subtask_id":"reach_pre_contact","tcp_end":[0.50065,0.11513,0.1635],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.1382,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":241.0,"n_steps_budget":1000.0,"object_pos_end":[0.50308,0.06743,0.0338],"object_pos_start":[0.50301,0.06746,0.0338],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14763,"object_z_max":0.0338,"peak_contact_force":1.39494,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1930.0,"raw_peak_contact_force":4.68907,"subtask_id":"reach_contact","tcp_end":[0.4994,0.09996,0.0481],"tcp_start":[0.50065,0.11513,0.1635],"tcp_to_object_dist_end":0.03573,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50633,0.04713,0.03571],"object_pos_start":[0.50308,0.06743,0.0338],"object_to_goal_dist_end":0.12736,"object_to_goal_dist_start":0.14759,"object_z_max":0.03581,"peak_contact_force":164.14964,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1498.0,"raw_peak_contact_force":171.46903,"subtask_id":"reach_contact","tcp_end":[0.49813,0.07609,0.03314],"tcp_start":[0.4994,0.09996,0.0481],"tcp_to_object_dist_end":0.03021,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":460.0,"n_steps_budget":1000.0,"object_pos_end":[0.50898,-0.08867,0.03435],"object_pos_start":[0.50633,0.04713,0.03571],"object_to_goal_dist_end":0.0137,"object_to_goal_dist_start":0.12736,"object_z_max":0.03733,"peak_contact_force":0.21785,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":784.0,"raw_peak_contact_force":138.15536,"subtask_id":"reach_goal","tcp_end":[0.49646,-0.06532,0.0285],"tcp_start":[0.49813,0.07609,0.03314],"tcp_to_object_dist_end":0.02713,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":272.0,"n_steps_budget":1000.0,"object_pos_end":[0.50406,-0.07345,0.05451],"object_pos_start":[0.50898,-0.08867,0.03435],"object_to_goal_dist_end":0.01643,"object_to_goal_dist_start":0.0137,"object_z_max":0.05892,"peak_contact_force":0.53889,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":221.0,"raw_peak_contact_force":2.06903,"tcp_end":[0.4925,-0.06315,0.08912],"tcp_start":[0.49646,-0.06532,0.0285],"tcp_to_object_dist_end":0.03792,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.775,"average_solve_count":360.0,"average_success_count":360.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.0457,"contact_1.force_threshold":2.3088,"contact_1.speed":0.01667,"descend_1.speed":0.01747,"push_1.push_distance":0.18282,"push_1.push_speed":0.00519,"retract_1.speed":0.04927},"optimized_scores":{"best_composite_score":0.54279,"best_fitness_score":0.78279,"best_task_score":0.98645},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":170.0,"contact_point_centroid":[0.5009,0.05668,0.04549],"force_p95":50.71794,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":54.76027,"mean_force":11.0125,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49595,0.0677,0.04012]},{"body_a":"peg","body_b":"channel_base_body","contact_count":95.0,"contact_point_centroid":[0.50628,0.0298,0.00983],"force_p95":33.73788,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":38.72371,"mean_force":11.87781,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49614,0.07322,0.04041]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":206.0,"contact_point_centroid":[0.52523,0.03191,0.03205],"force_p95":34.31359,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":38.37878,"mean_force":5.50395,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49578,0.05882,0.03986]},{"body_a":"peg","body_b":"channel_base_body","contact_count":27.0,"contact_point_centroid":[0.50501,0.10545,0.0094],"force_p95":4.04878,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.19154,"mean_force":1.16301,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49939,0.14173,0.04543]},{"body_a":"attachment","body_b":"peg","contact_count":6.0,"contact_point_centroid":[0.50206,0.12928,0.05718],"force_p95":6.93229,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.9428,"mean_force":2.98527,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49898,0.14125,0.04472]},{"body_a":"peg","body_b":"channel_base_body","contact_count":197.0,"contact_point_centroid":[0.505,-0.04809,0.00948],"force_p95":0.90001,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.17984,"mean_force":0.57401,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49285,-0.01397,0.06883]},{"body_a":"peg","body_b":"channel_base_body","contact_count":187.0,"contact_point_centroid":[0.50326,0.11159,0.00929],"force_p95":0.83659,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.58805,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50293,0.1753,0.22974]},{"body_a":"peg","body_b":"channel_base_body","contact_count":249.0,"contact_point_centroid":[0.50379,0.11157,0.00944],"force_p95":0.59837,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63519,"mean_force":0.5417,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50282,0.14773,0.10944]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49981,0.19931,0.29893]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":9.0,"contact_point_centroid":[0.52505,-0.04356,0.05393],"force_p95":0.27325,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.37101,"mean_force":0.09241,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49326,-0.01409,0.05314]}],"total_contact_groups":10},"final_pose_error":0.01982,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50538,-0.04605,0.03393],"final_tcp_position":[0.49243,-0.01349,0.0998],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":54.76027,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":209.0,"n_steps_budget":1000.0,"object_pos_end":[0.50372,0.11184,0.03383],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19198,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.58631,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":249.0,"raw_peak_contact_force":0.63519,"subtask_id":"reach_pre_contact","tcp_end":[0.50619,0.15283,0.1673],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13965,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":249.0,"n_steps_budget":1000.0,"object_pos_end":[0.50376,0.11179,0.0338],"object_pos_start":[0.50372,0.11184,0.03383],"object_to_goal_dist_end":0.19192,"object_to_goal_dist_start":0.19198,"object_z_max":0.03405,"peak_contact_force":8.19154,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":33.0,"raw_peak_contact_force":8.19154,"subtask_id":"reach_contact","tcp_end":[0.50094,0.14285,0.04814],"tcp_start":[0.50619,0.15283,0.1673],"tcp_to_object_dist_end":0.03432,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":27.0,"n_steps_budget":1000.0,"object_pos_end":[0.50364,0.11106,0.03449],"object_pos_start":[0.50376,0.11179,0.0338],"object_to_goal_dist_end":0.19118,"object_to_goal_dist_start":0.19192,"object_z_max":0.03442,"peak_contact_force":0.38894,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":471.0,"raw_peak_contact_force":54.76027,"subtask_id":"reach_contact","tcp_end":[0.49872,0.14041,0.044],"tcp_start":[0.50094,0.14285,0.04814],"tcp_to_object_dist_end":0.03123,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":276.0,"n_steps_budget":1000.0,"object_pos_end":[0.50664,-0.04248,0.03738],"object_pos_start":[0.50364,0.11106,0.03449],"object_to_goal_dist_end":0.03819,"object_to_goal_dist_start":0.19118,"object_z_max":0.03863,"peak_contact_force":0.55035,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":206.0,"raw_peak_contact_force":2.17984,"subtask_id":"reach_goal","tcp_end":[0.49552,-0.01351,0.03938],"tcp_start":[0.49872,0.14041,0.044],"tcp_to_object_dist_end":0.0311,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":201.0,"n_steps_budget":1000.0,"object_pos_end":[0.50538,-0.04605,0.03393],"object_pos_start":[0.50664,-0.04248,0.03738],"object_to_goal_dist_end":0.0349,"object_to_goal_dist_start":0.03819,"object_z_max":0.03738,"peak_contact_force":0.54401,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":203.0,"raw_peak_contact_force":2.06328,"tcp_end":[0.49243,-0.01349,0.0998],"tcp_start":[0.49552,-0.01351,0.03938],"tcp_to_object_dist_end":0.07461,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.86446,"average_solve_count":332.0,"average_success_count":332.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.02683,"contact_1.force_threshold":2.76107,"contact_1.speed":0.01575,"descend_1.speed":0.04882,"push_1.push_distance":0.19977,"push_1.push_speed":0.0064,"retract_1.speed":0.0722},"optimized_scores":{"best_composite_score":0.47006,"best_fitness_score":0.71006,"best_task_score":0.8347},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":38.0,"contact_point_centroid":[0.47498,-0.02265,0.0502],"force_p95":334.57585,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":343.12967,"mean_force":205.44668,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4868,-0.02264,0.04828]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":86.0,"contact_point_centroid":[0.47499,0.0245,0.04311],"force_p95":151.14984,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":161.45358,"mean_force":104.45893,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48682,0.02451,0.04119]},{"body_a":"attachment","body_b":"peg","contact_count":244.0,"contact_point_centroid":[0.49635,0.04048,0.04841],"force_p95":94.3395,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":102.54579,"mean_force":42.9323,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48699,0.04712,0.04144]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":252.0,"contact_point_centroid":[0.52634,0.02267,0.03547],"force_p95":92.51929,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":101.91697,"mean_force":37.99266,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48687,0.039,0.0412]},{"body_a":"peg","body_b":"channel_base_body","contact_count":162.0,"contact_point_centroid":[0.5078,0.02131,0.00974],"force_p95":60.61713,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":65.45964,"mean_force":26.49276,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48711,0.04092,0.04169]},{"body_a":"attachment","body_b":"peg","contact_count":18.0,"contact_point_centroid":[0.49827,-0.02289,0.04081],"force_p95":52.0212,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":55.76294,"mean_force":26.45989,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48682,-0.02282,0.04227]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.52586,-0.02522,0.02745],"force_p95":54.10701,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":54.75299,"mean_force":16.12013,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48682,-0.0228,0.04503]},{"body_a":"peg","body_b":"channel_base_body","contact_count":190.0,"contact_point_centroid":[0.50051,-0.03154,0.00851],"force_p95":11.07019,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.45787,"mean_force":2.00713,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48545,-0.02211,0.07037]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":15.0,"contact_point_centroid":[0.47492,-0.02859,0.02444],"force_p95":9.90556,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.11354,"mean_force":2.33309,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48407,-0.0218,0.09371]},{"body_a":"peg","body_b":"channel_base_body","contact_count":16.0,"contact_point_centroid":[0.49811,0.11407,0.00946],"force_p95":1.83347,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.95662,"mean_force":0.86583,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49004,0.14905,0.04601]},{"body_a":"attachment","body_b":"peg","contact_count":7.0,"contact_point_centroid":[0.49356,0.13713,0.05883],"force_p95":3.29167,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.54707,"mean_force":0.81187,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48987,0.14903,0.0458]},{"body_a":"peg","body_b":"channel_base_body","contact_count":186.0,"contact_point_centroid":[0.49652,0.11905,0.00937],"force_p95":0.72627,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.58111,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49317,0.17858,0.23084]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49946,0.19909,0.29796]},{"body_a":"peg","body_b":"channel_base_body","contact_count":247.0,"contact_point_centroid":[0.49598,0.11904,0.00941],"force_p95":0.62055,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65172,"mean_force":0.54309,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48847,0.15405,0.10863]}],"total_contact_groups":14},"final_pose_error":0.0197,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49358,-0.03174,0.02484],"final_tcp_position":[0.48399,-0.02179,0.10187],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":343.12967,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":211.0,"n_steps_budget":1000.0,"object_pos_end":[0.49598,0.11899,0.034],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19912,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.52189,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":247.0,"raw_peak_contact_force":0.65172,"subtask_id":"reach_pre_contact","tcp_end":[0.48735,0.15875,0.16811],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14014,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":247.0,"n_steps_budget":1000.0,"object_pos_end":[0.49603,0.11929,0.03394],"object_pos_start":[0.49598,0.11899,0.034],"object_to_goal_dist_end":0.19942,"object_to_goal_dist_start":0.19912,"object_z_max":0.034,"peak_contact_force":4.95662,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":23.0,"raw_peak_contact_force":4.95662,"subtask_id":"reach_contact","tcp_end":[0.49138,0.14972,0.048],"tcp_start":[0.48735,0.15875,0.16811],"tcp_to_object_dist_end":0.03385,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":16.0,"n_steps_budget":1000.0,"object_pos_end":[0.49606,0.11879,0.0341],"object_pos_start":[0.49603,0.11929,0.03394],"object_to_goal_dist_end":0.19891,"object_to_goal_dist_start":0.19942,"object_z_max":0.03405,"peak_contact_force":61.36932,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":744.0,"raw_peak_contact_force":161.45358,"subtask_id":"reach_contact","tcp_end":[0.48939,0.14828,0.04484],"tcp_start":[0.49138,0.14972,0.048],"tcp_to_object_dist_end":0.03209,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":341.0,"n_steps_budget":1000.0,"object_pos_end":[0.50993,-0.03101,0.02785],"object_pos_start":[0.49606,0.11879,0.0341],"object_to_goal_dist_end":0.05144,"object_to_goal_dist_start":0.19891,"object_z_max":0.04317,"peak_contact_force":0.62691,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":298.0,"raw_peak_contact_force":343.12967,"subtask_id":"reach_goal","tcp_end":[0.48687,-0.02188,0.04136],"tcp_start":[0.48939,0.14828,0.04484],"tcp_to_object_dist_end":0.02825,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":190.0,"n_steps_budget":720.0,"object_pos_end":[0.49358,-0.03174,0.02484],"object_pos_start":[0.50993,-0.03101,0.02785],"object_to_goal_dist_end":0.05099,"object_to_goal_dist_start":0.05144,"object_z_max":0.02785,"peak_contact_force":0.52307,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":210.0,"raw_peak_contact_force":2.24822,"tcp_end":[0.48399,-0.02179,0.10187],"tcp_start":[0.48687,-0.02188,0.04136],"tcp_to_object_dist_end":0.07827,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```