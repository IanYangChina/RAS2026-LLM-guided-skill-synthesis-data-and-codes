## Search State

- **Seed**: 6
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → descend → contact → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | pose_tolerance | 10 | 0.5023 | 0.81 | ❌ rejected |
| 4 | approach → descend → contact → push → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | pose_tolerance | 11 | 0.4475 | 0.77 | ❌ rejected |
| 3 | approach → descend → contact → push → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | pose_tolerance | 9 | 0.5222 | 0.76 | ❌ rejected |
| 2 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.5658 | 0.83 | ✅ accepted |
| 1 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | -0.0775 | 0.00 | ✅ accepted |

**Proposal policy**: task_score is 0.81 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.827, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.502) — your mutation base

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
    tolerance: 0.01
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
    tolerance: 0.005
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
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    force_threshold:
      type: scalar
      range:
      - 2.0
      - 8.0
      default: 5.0
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
    tolerance: 0.02
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
  guards:
  - id: force_guard_push
    when: during_phase
    predicate: force_below
    threshold: 40.0
    on_failure: abort
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
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.03, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.03, -0.005], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **contact_1** (`contact`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.0, 0.0], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_guard, when=during_phase, predicate=force_below, on_failure=abort, threshold=40.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, -0.005, 0.0]
- **push_1** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.16, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_guard_push, when=during_phase, predicate=force_below, on_failure=abort, threshold=40.0
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.08], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.502
- **task_score** (E): 0.809
- **fitness_score**: 0.767  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.356
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.620

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1672 |
| descend_1 | 1.00 | 1.00 | 0.1167 |
| contact_1 | 1.00 | 1.00 | 0.0027 |
| align_1 | 1.00 | 1.00 | 0.0001 |
| push_1 | 0.67 | 1.00 | 0.1504 |
| retract_1 | 1.00 | 1.00 | 0.0605 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.497, 0.134, 0.148) | (0.500, 0.099, 0.040)→(0.501, 0.099, 0.034) | 0.180→0.180 | 1.00 / 1.333 | 0.692 | 5.185 |
| descend_1 | descend | 1.00 / step_budget | (0.497, 0.134, 0.148)→(0.497, 0.129, 0.032) | (0.501, 0.099, 0.034)→(0.501, 0.099, 0.035) | 0.180→0.179 | 1.00 / 2.000 | 6.414 | 5.525 |
| contact_1 | contact | 1.00 / force_exceeded | (0.497, 0.129, 0.032)→(0.496, 0.127, 0.030) | (0.501, 0.099, 0.035)→(0.501, 0.098, 0.035) | 0.179→0.178 | 1.00 / 2.000 | 8.659 | 8.659 |
| align_1 | align | 1.00 / force_exceeded | (0.496, 0.127, 0.030)→(0.496, 0.127, 0.030) | (0.501, 0.098, 0.035)→(0.501, 0.098, 0.035) | 0.178→0.178 | 1.00 / 2.333 | 11.128 | 42.249 |
| push_1 | push | 0.67 / step_budget | (0.496, 0.127, 0.030)→(0.492, -0.023, 0.026) | (0.501, 0.098, 0.035)→(0.507, -0.050, 0.036) | 0.178→0.033 | 1.00 / 1.000 | 0.538 | 144.763 |
| retract_1 | retract | 1.00 / step_budget | (0.491, -0.009, 0.026)→(0.489, -0.009, 0.086) | (0.507, -0.035, 0.037)→(0.504, -0.038, 0.034) | 0.046→0.043 | 1.00 / 1.000 | 0.535 | 2.127 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.925
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.925
- phase_score: 0.785
- phase_breakdown.reach_pre_contact_score: 0.821
- phase_breakdown.reach_contact_score: 0.539
- phase_breakdown.reach_goal_score: 0.943

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.842
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.555
- **K-run variance**: 0.0155
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.264


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.52632,"average_solve_count":323.0,"average_success_count":323.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_distance":0.01762,"align_1.lateral_force_threshold":6.09911,"align_1.lateral_speed":0.01318,"approach_1.speed":0.05038,"contact_1.force_threshold":4.61538,"contact_1.speed":0.0126,"descend_1.speed":0.02047,"push_1.push_distance":0.16958,"push_1.push_speed":0.02523,"retract_1.speed":0.03211},"optimized_scores":{"best_composite_score":0.62132,"best_fitness_score":0.84132,"best_task_score":0.92544},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_base_body","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54882,-0.1,0.06498],"force_p95":62.58925,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":62.58925,"mean_force":62.58925,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49435,-0.05115,0.02578]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":211.0,"contact_point_centroid":[0.52519,-0.00747,0.0326],"force_p95":33.35412,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":38.01884,"mean_force":6.37521,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49437,0.02001,0.02602]},{"body_a":"attachment","body_b":"peg","contact_count":347.0,"contact_point_centroid":[0.50096,0.01224,0.04205],"force_p95":30.79961,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.99009,"mean_force":5.94361,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49457,0.02343,0.02623]},{"body_a":"peg","body_b":"channel_base_body","contact_count":155.0,"contact_point_centroid":[0.50513,-0.01391,0.00991],"force_p95":21.0011,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":26.42744,"mean_force":8.30587,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49473,0.0297,0.02644]},{"body_a":"peg","body_b":"link7","contact_count":125.0,"contact_point_centroid":[0.52152,-0.01358,0.06214],"force_p95":11.65182,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.27353,"mean_force":2.44471,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49431,0.00595,0.02586]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.50737,0.04988,0.00973],"force_p95":9.95671,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.95671,"mean_force":9.95671,"phase_index":3.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49799,0.09646,0.03039]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50173,0.08451,0.04844],"force_p95":9.72154,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.72154,"mean_force":9.72154,"phase_index":3.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49799,0.09646,0.03039]},{"body_a":"peg","body_b":"channel_base_body","contact_count":732.0,"contact_point_centroid":[0.50305,0.06674,0.00939],"force_p95":0.55071,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.52806,"mean_force":0.56624,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49804,0.10035,0.08725]},{"body_a":"attachment","body_b":"peg","contact_count":16.0,"contact_point_centroid":[0.50256,0.08531,0.05839],"force_p95":3.19601,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.0832,"mean_force":1.17329,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49888,0.0974,0.03554]},{"body_a":"peg","body_b":"channel_base_body","contact_count":14.0,"contact_point_centroid":[0.50182,0.05146,0.00969],"force_p95":4.47891,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.69056,"mean_force":1.32257,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49848,0.09695,0.03097]},{"body_a":"attachment","body_b":"peg","contact_count":4.0,"contact_point_centroid":[0.50228,0.08475,0.0532],"force_p95":4.38626,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.42812,"mean_force":3.31517,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49832,0.09677,0.03079]},{"body_a":"peg","body_b":"channel_base_body","contact_count":612.0,"contact_point_centroid":[0.50301,0.06746,0.00934],"force_p95":0.55511,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.56071,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49906,0.15125,0.2206]}],"total_contact_groups":12},"final_pose_error":0.02247,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50681,-0.08061,0.03519],"final_tcp_position":[0.49436,-0.05147,0.02579],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":62.58925,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":628.0,"n_steps_budget":1000.0,"object_pos_end":[0.50306,0.0675,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14766,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":1.1012,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":748.0,"raw_peak_contact_force":5.52806,"subtask_id":"reach_pre_contact","tcp_end":[0.49984,0.1041,0.14651],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11856,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":732.0,"n_steps_budget":1000.0,"object_pos_end":[0.50278,0.06722,0.03454],"object_pos_start":[0.50306,0.0675,0.0338],"object_to_goal_dist_end":0.14735,"object_to_goal_dist_start":0.14766,"object_z_max":0.03455,"peak_contact_force":4.69056,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":18.0,"raw_peak_contact_force":4.69056,"subtask_id":"reach_contact","tcp_end":[0.49897,0.09719,0.03157],"tcp_start":[0.49984,0.1041,0.14651],"tcp_to_object_dist_end":0.03036,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":14.0,"n_steps_budget":1000.0,"object_pos_end":[0.50316,0.06692,0.03478],"object_pos_start":[0.50278,0.06722,0.03454],"object_to_goal_dist_end":0.14705,"object_to_goal_dist_start":0.14735,"object_z_max":0.03474,"peak_contact_force":9.95671,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":9.95671,"subtask_id":"reach_contact","tcp_end":[0.49799,0.09646,0.03039],"tcp_start":[0.49897,0.09719,0.03157],"tcp_to_object_dist_end":0.0303,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":840.0,"object_pos_end":[0.50308,0.0668,0.03484],"object_pos_start":[0.50316,0.06692,0.03478],"object_to_goal_dist_end":0.14692,"object_to_goal_dist_start":0.14705,"object_z_max":0.03478,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":839.0,"raw_peak_contact_force":62.58925,"subtask_id":"reach_contact","tcp_end":[0.49794,0.09639,0.03032],"tcp_start":[0.49799,0.09646,0.03039],"tcp_to_object_dist_end":0.03038,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":406.0,"n_steps_budget":1000.0,"object_pos_end":[0.50681,-0.08061,0.03519],"object_pos_start":[0.50308,0.0668,0.03484],"object_to_goal_dist_end":0.00836,"object_to_goal_dist_start":0.14692,"object_z_max":0.03728,"peak_contact_force":0.55063,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":612.0,"raw_peak_contact_force":2.06903,"subtask_id":"reach_goal","tcp_end":[0.49436,-0.05147,0.02579],"tcp_start":[0.49794,0.09639,0.03032],"tcp_to_object_dist_end":0.03305,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.76081,"average_solve_count":347.0,"average_success_count":347.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_distance":0.01737,"align_1.lateral_force_threshold":6.03876,"align_1.lateral_speed":0.01103,"approach_1.speed":0.04201,"contact_1.force_threshold":3.22042,"contact_1.speed":0.0086,"descend_1.speed":0.02326,"push_1.push_distance":0.18055,"push_1.push_speed":0.0179,"retract_1.speed":0.06171},"optimized_scores":{"best_composite_score":0.55528,"best_fitness_score":0.84194,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_left_wall","contact_count":249.0,"contact_point_centroid":[0.52526,0.01513,0.03431],"force_p95":26.40161,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":31.89021,"mean_force":6.81848,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49515,0.0429,0.02624]},{"body_a":"attachment","body_b":"peg","contact_count":322.0,"contact_point_centroid":[0.50156,0.05232,0.04369],"force_p95":26.18522,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":31.84672,"mean_force":7.32483,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49558,0.06367,0.02672]},{"body_a":"peg","body_b":"channel_base_body","contact_count":157.0,"contact_point_centroid":[0.50585,0.0202,0.00987],"force_p95":19.21394,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.10167,"mean_force":6.65344,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49579,0.06379,0.02696]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.5105,0.09449,0.00973],"force_p95":7.47099,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.47099,"mean_force":7.47099,"phase_index":3.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49913,0.14056,0.03105]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50273,0.12856,0.04945],"force_p95":7.28972,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.28972,"mean_force":7.28972,"phase_index":3.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49913,0.14056,0.03105]},{"body_a":"peg","body_b":"channel_base_body","contact_count":12.0,"contact_point_centroid":[0.49888,0.09556,0.00971],"force_p95":4.04072,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.3698,"mean_force":1.30121,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.4996,0.14086,0.03162]},{"body_a":"attachment","body_b":"peg","contact_count":4.0,"contact_point_centroid":[0.503,0.12883,0.05165],"force_p95":5.49312,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.1179,"mean_force":2.69821,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49964,0.14087,0.03166]},{"body_a":"peg","body_b":"channel_base_body","contact_count":675.0,"contact_point_centroid":[0.5037,0.10867,0.00948],"force_p95":0.81934,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.99918,"mean_force":0.6392,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50181,0.14302,0.08872]},{"body_a":"attachment","body_b":"peg","contact_count":37.0,"contact_point_centroid":[0.50313,0.12934,0.05894],"force_p95":3.96435,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.58752,"mean_force":2.17089,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50033,0.14138,0.04266]},{"body_a":"peg","body_b":"channel_base_body","contact_count":521.0,"contact_point_centroid":[0.5035,0.11165,0.00937],"force_p95":0.61771,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.55901,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5023,0.1721,0.22117]},{"body_a":"peg","body_b":"link7","contact_count":6.0,"contact_point_centroid":[0.52197,0.03741,0.06247],"force_p95":1.44801,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.51559,"mean_force":0.64961,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49505,0.05715,0.02617]},{"body_a":"peg","body_b":"channel_base_body","contact_count":188.0,"contact_point_centroid":[0.50592,-0.05468,0.00944],"force_p95":0.74607,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.30894,"mean_force":0.55495,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49262,-0.02126,0.05684]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":18.0,"contact_point_centroid":[0.5259,-0.05123,0.05987],"force_p95":0.48603,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55512,"mean_force":0.19844,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49458,-0.02189,0.02737]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49973,0.19936,0.29913]},{"body_a":"attachment","body_b":"peg","contact_count":6.0,"contact_point_centroid":[0.50237,-0.03286,0.04584],"force_p95":0.39002,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.43951,"mean_force":0.14788,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49524,-0.02159,0.02636]}],"total_contact_groups":15},"final_pose_error":0.01973,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50584,-0.0541,0.03393],"final_tcp_position":[0.49228,-0.02098,0.08692],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":31.89021,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":543.0,"n_steps_budget":1000.0,"object_pos_end":[0.50374,0.11176,0.03399],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19189,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.47992,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":712.0,"raw_peak_contact_force":4.99918,"subtask_id":"reach_pre_contact","tcp_end":[0.50621,0.1458,0.14833],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11933,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":675.0,"n_steps_budget":1000.0,"object_pos_end":[0.5036,0.11101,0.0346],"object_pos_start":[0.50374,0.11176,0.03399],"object_to_goal_dist_end":0.19112,"object_to_goal_dist_start":0.19189,"object_z_max":0.0349,"peak_contact_force":6.3698,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":16.0,"raw_peak_contact_force":6.3698,"subtask_id":"reach_contact","tcp_end":[0.50004,0.14103,0.03219],"tcp_start":[0.50621,0.1458,0.14833],"tcp_to_object_dist_end":0.03033,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":12.0,"n_steps_budget":1000.0,"object_pos_end":[0.50387,0.11083,0.03473],"object_pos_start":[0.5036,0.11101,0.0346],"object_to_goal_dist_end":0.19095,"object_to_goal_dist_start":0.19112,"object_z_max":0.03471,"peak_contact_force":7.47099,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":7.47099,"subtask_id":"reach_contact","tcp_end":[0.49913,0.14056,0.03105],"tcp_start":[0.50004,0.14103,0.03219],"tcp_to_object_dist_end":0.03032,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":990.0,"object_pos_end":[0.50385,0.11077,0.03476],"object_pos_start":[0.50387,0.11083,0.03473],"object_to_goal_dist_end":0.19088,"object_to_goal_dist_start":0.19095,"object_z_max":0.03473,"peak_contact_force":1.8691,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":734.0,"raw_peak_contact_force":31.89021,"subtask_id":"reach_contact","tcp_end":[0.49907,0.1405,0.03097],"tcp_start":[0.49913,0.14056,0.03105],"tcp_to_object_dist_end":0.03035,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":431.0,"n_steps_budget":1000.0,"object_pos_end":[0.5072,-0.04895,0.03674],"object_pos_start":[0.50385,0.11077,0.03476],"object_to_goal_dist_end":0.03204,"object_to_goal_dist_start":0.19088,"object_z_max":0.03678,"peak_contact_force":0.54174,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":212.0,"raw_peak_contact_force":1.30894,"subtask_id":"reach_goal","tcp_end":[0.49541,-0.02107,0.0264],"tcp_start":[0.49907,0.1405,0.03097],"tcp_to_object_dist_end":0.03199,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":197.0,"n_steps_budget":810.0,"object_pos_end":[0.50584,-0.0541,0.03393],"object_pos_start":[0.5072,-0.04895,0.03674],"object_to_goal_dist_end":0.02723,"object_to_goal_dist_start":0.03204,"object_z_max":0.03678,"peak_contact_force":0.51576,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":537.0,"raw_peak_contact_force":2.06328,"tcp_end":[0.49228,-0.02098,0.08692],"tcp_start":[0.49541,-0.02107,0.0264],"tcp_to_object_dist_end":0.06394,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.67405,"average_solve_count":316.0,"average_success_count":316.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_distance":0.01347,"align_1.lateral_force_threshold":7.01007,"align_1.lateral_speed":0.01589,"approach_1.speed":0.06617,"contact_1.force_threshold":6.73773,"contact_1.speed":0.01506,"descend_1.speed":0.02721,"push_1.push_distance":0.1609,"push_1.push_speed":0.0143,"retract_1.speed":0.03898},"optimized_scores":{"best_composite_score":0.33027,"best_fitness_score":0.61694,"best_task_score":0.50081},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":65.0,"contact_point_centroid":[0.47499,0.00289,0.04315],"force_p95":247.91242,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":288.21779,"mean_force":160.66263,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48681,0.00289,0.04121]},{"body_a":"peg","body_b":"channel_base_body","contact_count":193.0,"contact_point_centroid":[0.50557,-0.03036,0.00974],"force_p95":0.79723,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":37.73108,"mean_force":0.90008,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48626,0.00304,0.05476]},{"body_a":"peg","body_b":"channel_base_body","contact_count":384.0,"contact_point_centroid":[0.50853,0.03005,0.00996],"force_p95":31.38606,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":32.26793,"mean_force":27.02685,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48731,0.07057,0.02537]},{"body_a":"peg","body_b":"link7","contact_count":12.0,"contact_point_centroid":[0.5195,-0.01158,0.06128],"force_p95":19.64639,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.8072,"mean_force":6.88455,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48717,0.00276,0.02548]},{"body_a":"peg","body_b":"link7","contact_count":366.0,"contact_point_centroid":[0.51698,0.04909,0.06157],"force_p95":23.07088,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.84706,"mean_force":20.34846,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48722,0.06537,0.02525]},{"body_a":"attachment","body_b":"peg","contact_count":402.0,"contact_point_centroid":[0.49356,0.06172,0.02977],"force_p95":18.90497,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.66248,"mean_force":14.08721,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48731,0.07197,0.02538]},{"body_a":"attachment","body_b":"peg","contact_count":48.0,"contact_point_centroid":[0.49526,-0.00763,0.05595],"force_p95":4.37246,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.90961,"mean_force":1.12341,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4869,0.00289,0.03945]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.49967,0.09826,0.00997],"force_p95":8.54921,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.54921,"mean_force":8.54921,"phase_index":3.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.48956,0.14476,0.02821]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.49402,0.13292,0.04944],"force_p95":8.19325,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.19325,"mean_force":8.19325,"phase_index":3.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.48956,0.14476,0.02821]},{"body_a":"peg","body_b":"channel_base_body","contact_count":42.0,"contact_point_centroid":[0.49779,0.10163,0.00987],"force_p95":4.90919,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.51441,"mean_force":1.89734,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49039,0.14664,0.02932]},{"body_a":"attachment","body_b":"peg","contact_count":24.0,"contact_point_centroid":[0.49416,0.13456,0.0478],"force_p95":4.78002,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.21153,"mean_force":2.62663,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49034,0.14652,0.02925]},{"body_a":"peg","body_b":"channel_base_body","contact_count":793.0,"contact_point_centroid":[0.4961,0.11654,0.00951],"force_p95":0.854,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.02785,"mean_force":0.61757,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48676,0.14992,0.08749]},{"body_a":"attachment","body_b":"peg","contact_count":49.0,"contact_point_centroid":[0.49438,0.13655,0.0589],"force_p95":3.84648,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.50395,"mean_force":1.5842,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49067,0.14853,0.04131]},{"body_a":"peg","body_b":"channel_base_body","contact_count":477.0,"contact_point_centroid":[0.49629,0.11911,0.0094],"force_p95":0.60861,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.55819,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4913,0.17529,0.2209]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49948,0.19905,0.29781]}],"total_contact_groups":15},"final_pose_error":0.01992,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5024,-0.0216,0.03394],"final_tcp_position":[0.4848,0.00326,0.08563],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":288.21779,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":502.0,"n_steps_budget":1000.0,"object_pos_end":[0.49608,0.11912,0.03396],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19925,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.49388,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":842.0,"raw_peak_contact_force":5.02785,"subtask_id":"reach_pre_contact","tcp_end":[0.48451,0.15248,0.14902],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12036,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":793.0,"n_steps_budget":1000.0,"object_pos_end":[0.49625,0.1183,0.03476],"object_pos_start":[0.49608,0.11912,0.03396],"object_to_goal_dist_end":0.19841,"object_to_goal_dist_start":0.19925,"object_z_max":0.03477,"peak_contact_force":8.18135,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":66.0,"raw_peak_contact_force":5.51441,"subtask_id":"reach_contact","tcp_end":[0.49159,0.14824,0.03086],"tcp_start":[0.48451,0.15248,0.14902],"tcp_to_object_dist_end":0.03055,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":47.0,"n_steps_budget":1000.0,"object_pos_end":[0.49569,0.11538,0.03524],"object_pos_start":[0.49625,0.1183,0.03476],"object_to_goal_dist_end":0.19548,"object_to_goal_dist_start":0.19841,"object_z_max":0.03535,"peak_contact_force":8.54921,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":8.54921,"subtask_id":"reach_contact","tcp_end":[0.48956,0.14476,0.02821],"tcp_start":[0.49159,0.14824,0.03086],"tcp_to_object_dist_end":0.03083,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.4957,0.1153,0.03521],"object_pos_start":[0.49569,0.11538,0.03524],"object_to_goal_dist_end":0.1954,"object_to_goal_dist_start":0.19548,"object_z_max":0.03524,"peak_contact_force":31.5155,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1152.0,"raw_peak_contact_force":32.26793,"subtask_id":"reach_contact","tcp_end":[0.48953,0.14471,0.02816],"tcp_start":[0.48956,0.14476,0.02821],"tcp_to_object_dist_end":0.03087,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":418.0,"n_steps_budget":1000.0,"object_pos_end":[0.50583,-0.02092,0.03637],"object_pos_start":[0.4957,0.1153,0.03521],"object_to_goal_dist_end":0.05947,"object_to_goal_dist_start":0.1954,"object_z_max":0.03713,"peak_contact_force":0.53356,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":318.0,"raw_peak_contact_force":288.21779,"subtask_id":"reach_goal","tcp_end":[0.48751,0.00333,0.02537],"tcp_start":[0.48953,0.14471,0.02816],"tcp_to_object_dist_end":0.03232,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":198.0,"n_steps_budget":1000.0,"object_pos_end":[0.5024,-0.0216,0.03394],"object_pos_start":[0.50583,-0.02092,0.03637],"object_to_goal_dist_end":0.05877,"object_to_goal_dist_start":0.05947,"object_z_max":0.03637,"peak_contact_force":0.53792,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":501.0,"raw_peak_contact_force":2.24822,"tcp_end":[0.4848,0.00326,0.08563],"tcp_start":[0.48751,0.00333,0.02537],"tcp_to_object_dist_end":0.06,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```