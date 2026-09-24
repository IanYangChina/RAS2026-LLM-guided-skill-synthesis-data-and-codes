## Search State

- **Seed**: 6
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | impedance_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.6472 | 0.80 | ❌ rejected |
| 12 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | impedance_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.7492 | 0.91 | ✅ accepted |
| 11 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | impedance_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.7339 | 0.88 | ✅ accepted |
| 10 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | -0.0131 | 0.38 | ❌ rejected |
| 9 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 2 | 0.1442 | 0.23 | ❌ rejected |

**Proposal policy**: task_score is 0.80 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.909, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.647) — your mutation base

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
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
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
    - 0.02
    - 0.0
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
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
    anchor: current_tcp
    offset:
    - 0.0
    - -0.02
    - 0.0
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: channel_axis
      tolerance: 0.1
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 3.0
      - 10.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
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
      default: 0.14
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
    threshold: 200.0
    on_failure: retry
  retries:
    max_attempts: 1
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
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.02, 0.0], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **contact_1** (`contact`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, -0.02, 0.0]
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.16, mode=add_to_offset, sign=positive}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - insertion_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_safety, when=during_phase, predicate=force_below, on_failure=retry, threshold=200.0
  - retries: max_attempts=1, strategy=reduce_speed
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.647
- **task_score** (E): 0.796
- **fitness_score**: 0.837  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.390

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1345 |
| descend_1 | 1.00 | 1.00 | 0.1458 |
| contact_1 | 1.00 | 1.00 | 0.0014 |
| push_1 | 0.67 | 1.00 | 0.1117 |
| retract_1 | 1.00 | 1.00 | 0.0805 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.497, 0.180, 0.169) | (0.500, 0.099, 0.040)→(0.501, 0.100, 0.034) | 0.180→0.180 | 1.00 / 1.000 | 0.569 | 2.127 |
| descend_1 | descend | 1.00 / step_budget | (0.497, 0.180, 0.169)→(0.497, 0.122, 0.036) | (0.501, 0.100, 0.034)→(0.504, 0.093, 0.035) | 0.180→0.173 | 1.00 / 1.667 | 2.601 | 9.489 |
| contact_1 | contact | 1.00 / force_exceeded | (0.497, 0.122, 0.036)→(0.498, 0.121, 0.035) | (0.504, 0.093, 0.035)→(0.504, 0.092, 0.035) | 0.173→0.172 | 1.00 / 2.000 | 28.097 | 34.134 |
| push_1 | push | 0.67 / step_budget | (0.497, 0.073, 0.033)→(0.494, -0.038, 0.030) | (0.504, 0.092, 0.035)→(0.507, -0.065, 0.036) | 0.172→0.019 | 1.00 / 2.333 | 5.610 | 15.273 |
| retract_1 | retract | 1.00 / step_budget | (0.494, -0.038, 0.030)→(0.491, -0.038, 0.111) | (0.507, -0.065, 0.036)→(0.507, -0.065, 0.034) | 0.019→0.021 | 1.00 / 1.000 | 0.541 | 97.340 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.933
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.933
- phase_score: 0.908
- phase_breakdown.reach_contact_score: 0.823
- phase_breakdown.goal_progress_score: 0.945

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.918
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.727
- **K-run variance**: 0.0129
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.302


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.00784,"average_solve_count":255.0,"average_success_count":255.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.065,"contact_1.contact_force_threshold":5.28881,"descend_1.descend_speed":0.03878,"push_1.force_limit":16.15256,"push_1.insertion_depth":0.17301,"push_1.push_speed":0.01594},"optimized_scores":{"best_composite_score":0.72831,"best_fitness_score":0.91831,"best_task_score":0.93343},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50247,0.07815,0.04854],"force_p95":65.40469,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":65.40469,"mean_force":65.40469,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49916,0.09009,0.03538]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.50566,0.04318,0.00995],"force_p95":64.38418,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":64.38418,"mean_force":64.38418,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49916,0.09009,0.03538]},{"body_a":"attachment","body_b":"peg","contact_count":25.0,"contact_point_centroid":[0.50079,-0.06469,0.05243],"force_p95":19.05497,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.29545,"mean_force":6.29869,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49397,-0.0534,0.03345]},{"body_a":"peg","body_b":"channel_base_body","contact_count":56.0,"contact_point_centroid":[0.50722,-0.1002,0.03909],"force_p95":17.34859,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.68616,"mean_force":4.6503,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49339,-0.05326,0.03805]},{"body_a":"peg","body_b":"channel_base_body","contact_count":10.0,"contact_point_centroid":[0.50672,-0.10014,0.06028],"force_p95":16.61036,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.698,"mean_force":12.70303,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49555,-0.05297,0.03056]},{"body_a":"attachment","body_b":"peg","contact_count":731.0,"contact_point_centroid":[0.50123,0.0018,0.04119],"force_p95":8.8596,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.61963,"mean_force":3.08409,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49569,0.01313,0.03077]},{"body_a":"peg","body_b":"channel_base_body","contact_count":882.0,"contact_point_centroid":[0.50335,0.06477,0.00944],"force_p95":7.38399,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.90949,"mean_force":1.08745,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49818,0.12,0.09901]},{"body_a":"peg","body_b":"channel_base_body","contact_count":471.0,"contact_point_centroid":[0.50687,-0.02556,0.00994],"force_p95":7.81026,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.82854,"mean_force":4.31263,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49581,0.01879,0.03091]},{"body_a":"attachment","body_b":"peg","contact_count":69.0,"contact_point_centroid":[0.50152,0.08156,0.04943],"force_p95":9.28014,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.6293,"mean_force":7.1704,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49899,0.09347,0.04275]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":569.0,"contact_point_centroid":[0.52509,-0.01097,0.02687],"force_p95":4.93963,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.13252,"mean_force":1.37404,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49564,0.01657,0.03072]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":71.0,"contact_point_centroid":[0.52528,-0.08201,0.02687],"force_p95":8.48868,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.08991,"mean_force":1.61545,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4927,-0.05316,0.04733]},{"body_a":"peg","body_b":"channel_base_body","contact_count":436.0,"contact_point_centroid":[0.50311,0.06748,0.00933],"force_p95":0.56949,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.56638,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49921,0.17533,0.2321]},{"body_a":"peg","body_b":"channel_base_body","contact_count":215.0,"contact_point_centroid":[0.50537,-0.08049,0.00955],"force_p95":0.56343,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57784,"mean_force":0.5051,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49236,-0.0532,0.07446]}],"total_contact_groups":13},"final_pose_error":0.01982,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50694,-0.08189,0.03378],"final_tcp_position":[0.49239,-0.05325,0.11088],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":65.40469,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":452.0,"n_steps_budget":1000.0,"object_pos_end":[0.50305,0.06742,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14758,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54758,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":436.0,"raw_peak_contact_force":2.06903,"subtask_id":"reach_contact","tcp_end":[0.49992,0.15163,0.16837],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15878,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":888.0,"n_steps_budget":1000.0,"object_pos_end":[0.50446,0.06059,0.03529],"object_pos_start":[0.50305,0.06742,0.0338],"object_to_goal_dist_end":0.14074,"object_to_goal_dist_start":0.14758,"object_z_max":0.03546,"peak_contact_force":7.14783,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":951.0,"raw_peak_contact_force":9.90949,"subtask_id":"reach_contact","tcp_end":[0.49916,0.09009,0.03538],"tcp_start":[0.49992,0.15163,0.16837],"tcp_to_object_dist_end":0.02998,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.50462,0.06032,0.03535],"object_pos_start":[0.50446,0.06059,0.03529],"object_to_goal_dist_end":0.14047,"object_to_goal_dist_start":0.14074,"object_z_max":0.03529,"peak_contact_force":65.40469,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":65.40469,"subtask_id":"reach_contact","tcp_end":[0.49942,0.08984,0.03517],"tcp_start":[0.49916,0.09009,0.03538],"tcp_to_object_dist_end":0.02998,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":905.0,"n_steps_budget":1000.0,"object_pos_end":[0.5066,-0.08149,0.03617],"object_pos_start":[0.50462,0.06032,0.03535],"object_to_goal_dist_end":0.00778,"object_to_goal_dist_start":0.14047,"object_z_max":0.03652,"peak_contact_force":4.7853,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1781.0,"raw_peak_contact_force":16.698,"subtask_id":"goal_progress","tcp_end":[0.49546,-0.05353,0.03046],"tcp_start":[0.4955,-0.05347,0.03051],"tcp_to_object_dist_end":0.03064,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":245.0,"n_steps_budget":630.0,"object_pos_end":[0.50694,-0.08189,0.03378],"object_pos_start":[0.50649,-0.08169,0.03611],"object_to_goal_dist_end":0.00951,"object_to_goal_dist_start":0.00775,"object_z_max":0.03706,"peak_contact_force":0.54656,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":367.0,"raw_peak_contact_force":19.29545,"tcp_end":[0.49239,-0.05325,0.11088],"tcp_start":[0.49546,-0.05353,0.03046],"tcp_to_object_dist_end":0.08352,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.05396,"average_solve_count":278.0,"average_success_count":278.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.05162,"contact_1.contact_force_threshold":5.79262,"descend_1.descend_speed":0.03601,"push_1.force_limit":19.93519,"push_1.insertion_depth":0.18652,"push_1.push_speed":0.01666},"optimized_scores":{"best_composite_score":0.72684,"best_fitness_score":0.91684,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.50389,0.122,0.04404],"force_p95":32.75722,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":34.12629,"mean_force":20.43563,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50054,0.13363,0.03566]},{"body_a":"peg","body_b":"channel_base_body","contact_count":2.0,"contact_point_centroid":[0.51446,0.08949,0.00987],"force_p95":28.25006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":29.70985,"mean_force":15.11197,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50016,0.13402,0.036]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.5253,0.10431,0.0437],"force_p95":26.65143,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":29.196,"mean_force":11.01386,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50037,0.13381,0.03582]},{"body_a":"attachment","body_b":"peg","contact_count":775.0,"contact_point_centroid":[0.50251,0.02929,0.04139],"force_p95":8.10546,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.96781,"mean_force":2.79421,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49775,0.04077,0.03038]},{"body_a":"peg","body_b":"channel_base_body","contact_count":787.0,"contact_point_centroid":[0.50392,0.10919,0.00944],"force_p95":0.76145,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.63148,"mean_force":0.8799,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50185,0.16263,0.10099]},{"body_a":"attachment","body_b":"peg","contact_count":50.0,"contact_point_centroid":[0.50259,0.12623,0.05054],"force_p95":11.01701,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.39667,"mean_force":5.50852,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50027,0.13811,0.04512]},{"body_a":"peg","body_b":"channel_base_body","contact_count":513.0,"contact_point_centroid":[0.50632,0.00115,0.00994],"force_p95":8.44324,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.72078,"mean_force":4.35672,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49791,0.04663,0.03047]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":598.0,"contact_point_centroid":[0.52508,0.01452,0.02499],"force_p95":3.17484,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.1472,"mean_force":0.95849,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49788,0.04326,0.03047]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":11.0,"contact_point_centroid":[0.52504,-0.06526,0.06],"force_p95":2.96523,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.67323,"mean_force":0.58352,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49687,-0.03572,0.03204]},{"body_a":"attachment","body_b":"peg","contact_count":21.0,"contact_point_centroid":[0.5019,-0.04704,0.06023],"force_p95":2.22766,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.459,"mean_force":0.57096,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49543,-0.03562,0.04133]},{"body_a":"peg","body_b":"channel_base_body","contact_count":413.0,"contact_point_centroid":[0.50357,0.11167,0.00935],"force_p95":0.61747,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.56429,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50236,0.19524,0.23164]},{"body_a":"peg","body_b":"channel_base_body","contact_count":243.0,"contact_point_centroid":[0.50716,-0.06789,0.00955],"force_p95":0.57893,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.67129,"mean_force":0.52519,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49484,-0.0354,0.06971]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4998,0.19957,0.29904]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.52514,0.10421,0.06],"force_p95":0.32716,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.3377,"mean_force":0.24097,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50005,0.1343,0.03641]}],"total_contact_groups":14},"final_pose_error":0.01978,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50674,-0.06359,0.03385],"final_tcp_position":[0.49462,-0.0353,0.11083],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":34.12629,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":435.0,"n_steps_budget":1000.0,"object_pos_end":[0.50372,0.11181,0.03385],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19195,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.54579,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":429.0,"raw_peak_contact_force":2.06328,"subtask_id":"reach_contact","tcp_end":[0.50622,0.19154,0.16905],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15698,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":799.0,"n_steps_budget":1000.0,"object_pos_end":[0.50712,0.10489,0.03539],"object_pos_start":[0.50372,0.11181,0.03385],"object_to_goal_dist_end":0.18508,"object_to_goal_dist_start":0.19195,"object_z_max":0.03568,"peak_contact_force":0.5625,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":840.0,"raw_peak_contact_force":11.63148,"subtask_id":"reach_contact","tcp_end":[0.50003,0.13417,0.03613],"tcp_start":[0.50622,0.19154,0.16905],"tcp_to_object_dist_end":0.03014,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":600.0,"object_pos_end":[0.50716,0.10364,0.03585],"object_pos_start":[0.50712,0.10489,0.03539],"object_to_goal_dist_end":0.18382,"object_to_goal_dist_start":0.18508,"object_z_max":0.03572,"peak_contact_force":6.74497,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":7.0,"raw_peak_contact_force":34.12629,"subtask_id":"reach_contact","tcp_end":[0.50154,0.13265,0.03494],"tcp_start":[0.50003,0.13417,0.03613],"tcp_to_object_dist_end":0.02957,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50709,-0.06422,0.03568],"object_pos_start":[0.50716,0.10364,0.03585],"object_to_goal_dist_end":0.01783,"object_to_goal_dist_start":0.18382,"object_z_max":0.03888,"peak_contact_force":2.43897,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1886.0,"raw_peak_contact_force":11.96781,"subtask_id":"goal_progress","tcp_end":[0.49769,-0.03546,0.03037],"tcp_start":[0.50154,0.13265,0.03494],"tcp_to_object_dist_end":0.03072,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":244.0,"n_steps_budget":630.0,"object_pos_end":[0.50674,-0.06359,0.03385],"object_pos_start":[0.50709,-0.06422,0.03568],"object_to_goal_dist_end":0.01878,"object_to_goal_dist_start":0.01783,"object_z_max":0.03568,"peak_contact_force":0.54726,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":275.0,"raw_peak_contact_force":3.67323,"tcp_end":[0.49462,-0.0353,0.11083],"tcp_start":[0.49769,-0.03546,0.03037],"tcp_to_object_dist_end":0.0829,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.06028,"average_solve_count":282.0,"average_success_count":282.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.0457,"contact_1.contact_force_threshold":7.62736,"descend_1.descend_speed":0.03788,"push_1.force_limit":21.16843,"push_1.insertion_depth":0.18259,"push_1.push_speed":0.02038},"optimized_scores":{"best_composite_score":0.48658,"best_fitness_score":0.67658,"best_task_score":0.45338},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":29.0,"contact_point_centroid":[0.47499,-0.0263,0.04844],"force_p95":241.60138,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":269.05159,"mean_force":116.00134,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48682,-0.0263,0.04649]},{"body_a":"attachment","body_b":"peg","contact_count":26.0,"contact_point_centroid":[0.49629,-0.03598,0.05761],"force_p95":0.60571,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.16895,"mean_force":0.98291,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4871,-0.02633,0.04452]},{"body_a":"attachment","body_b":"peg","contact_count":770.0,"contact_point_centroid":[0.49654,0.04186,0.03676],"force_p95":13.33131,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.15334,"mean_force":5.24004,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48878,0.05152,0.03055]},{"body_a":"peg","body_b":"channel_base_body","contact_count":241.0,"contact_point_centroid":[0.50639,-0.05472,0.00965],"force_p95":0.61401,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.4257,"mean_force":0.56688,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48629,-0.02623,0.06963]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":806.0,"contact_point_centroid":[0.52518,0.02267,0.03009],"force_p95":7.86817,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.09502,"mean_force":3.14551,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48864,0.04617,0.03044]},{"body_a":"peg","body_b":"channel_base_body","contact_count":602.0,"contact_point_centroid":[0.50629,0.01608,0.0099],"force_p95":10.20026,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.58158,"mean_force":4.84897,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48883,0.05594,0.03059]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":93.0,"contact_point_centroid":[0.52504,-0.0488,0.04568],"force_p95":0.36556,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.88808,"mean_force":0.22575,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48663,-0.0263,0.05789]},{"body_a":"peg","body_b":"channel_base_body","contact_count":870.0,"contact_point_centroid":[0.49651,0.11681,0.00949],"force_p95":0.65017,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.92719,"mean_force":0.67159,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48703,0.16917,0.10073]},{"body_a":"attachment","body_b":"peg","contact_count":48.0,"contact_point_centroid":[0.49503,0.13271,0.05423],"force_p95":5.61283,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.75162,"mean_force":2.61261,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49112,0.14443,0.04321]},{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.49668,0.1292,0.05796],"force_p95":2.8503,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.87196,"mean_force":2.65545,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49182,0.141,0.03539]},{"body_a":"peg","body_b":"channel_base_body","contact_count":400.0,"contact_point_centroid":[0.49635,0.11919,0.00941],"force_p95":0.63379,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.55993,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49156,0.19849,0.23165]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49947,0.19954,0.29796]}],"total_contact_groups":12},"final_pose_error":0.01986,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50698,-0.04807,0.03377],"final_tcp_position":[0.48568,-0.02618,0.11081],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":269.05159,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":425.0,"n_steps_budget":1000.0,"object_pos_end":[0.49601,0.11935,0.03392],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19948,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.61245,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":424.0,"raw_peak_contact_force":2.24822,"subtask_id":"reach_contact","tcp_end":[0.48495,0.19798,0.16975],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15733,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":885.0,"n_steps_budget":1000.0,"object_pos_end":[0.49915,0.11211,0.03574],"object_pos_start":[0.49601,0.11935,0.03392],"object_to_goal_dist_end":0.19216,"object_to_goal_dist_start":0.19948,"object_z_max":0.03575,"peak_contact_force":0.09137,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":918.0,"raw_peak_contact_force":6.92719,"subtask_id":"reach_contact","tcp_end":[0.49168,0.14114,0.03552],"tcp_start":[0.48495,0.19798,0.16975],"tcp_to_object_dist_end":0.02997,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":2.0,"n_steps_budget":600.0,"object_pos_end":[0.49927,0.11145,0.03521],"object_pos_start":[0.49915,0.11211,0.03574],"object_to_goal_dist_end":0.19151,"object_to_goal_dist_start":0.19216,"object_z_max":0.03574,"peak_contact_force":12.14193,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":2.87196,"subtask_id":"reach_contact","tcp_end":[0.49251,0.14037,0.03489],"tcp_start":[0.49168,0.14114,0.03552],"tcp_to_object_dist_end":0.02971,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50709,-0.05057,0.03677],"object_pos_start":[0.49927,0.11145,0.03521],"object_to_goal_dist_end":0.03044,"object_to_goal_dist_start":0.19151,"object_z_max":0.03728,"peak_contact_force":9.60441,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2178.0,"raw_peak_contact_force":17.15334,"subtask_id":"goal_progress","tcp_end":[0.48865,-0.02631,0.03044],"tcp_start":[0.49251,0.14037,0.03489],"tcp_to_object_dist_end":0.03112,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":241.0,"n_steps_budget":660.0,"object_pos_end":[0.50698,-0.04807,0.03377],"object_pos_start":[0.50709,-0.05057,0.03677],"object_to_goal_dist_end":0.03327,"object_to_goal_dist_start":0.03044,"object_z_max":0.0369,"peak_contact_force":0.52847,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":389.0,"raw_peak_contact_force":269.05159,"tcp_end":[0.48568,-0.02618,0.11081],"tcp_start":[0.48865,-0.02631,0.03044],"tcp_to_object_dist_end":0.08287,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```