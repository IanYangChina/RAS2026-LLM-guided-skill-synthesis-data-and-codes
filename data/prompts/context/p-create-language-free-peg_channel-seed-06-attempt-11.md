## Search State

- **Seed**: 6
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | impedance_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.7339 | 0.88 | ✅ accepted |
| 10 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | -0.0131 | 0.38 | ❌ rejected |
| 9 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 2 | 0.1442 | 0.23 | ❌ rejected |
| 8 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | -0.0227 | 0.00 | ❌ rejected |
| 7 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 2 | 0.6305 | 0.84 | ✅ accepted |

**Proposal policy**: task_score is 0.88 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.884, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.734) — your mutation base

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

- **Composite score**: 0.734
- **task_score** (E): 0.884
- **fitness_score**: 0.874  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.340

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1345 |
| descend_1 | 1.00 | 1.00 | 0.1459 |
| contact_1 | 1.00 | 1.00 | 0.0032 |
| push_1 | 1.00 | 0.67 | 0.1550 |
| retract_1 | 1.00 | 1.00 | 0.0805 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.497, 0.180, 0.169) | (0.500, 0.099, 0.040)→(0.501, 0.099, 0.034) | 0.180→0.180 | 1.00 / 1.000 | 0.553 | 2.127 |
| descend_1 | descend | 1.00 / step_budget | (0.497, 0.180, 0.169)→(0.497, 0.122, 0.036) | (0.501, 0.099, 0.034)→(0.503, 0.092, 0.035) | 0.180→0.172 | 1.00 / 1.333 | 1.391 | 12.181 |
| contact_1 | contact | 1.00 / force_exceeded | (0.497, 0.122, 0.036)→(0.499, 0.120, 0.034) | (0.503, 0.092, 0.035)→(0.503, 0.090, 0.036) | 0.172→0.170 | 1.00 / 2.000 | 23.842 | 39.842 |
| push_1 | push | 1.00 / step_budget | (0.499, 0.120, 0.034)→(0.495, -0.035, 0.030) | (0.503, 0.090, 0.036)→(0.505, -0.067, 0.037) | 0.170→0.016 | 0.67 / 2.000 | 8.285 | 20.278 |
| retract_1 | retract | 1.00 / step_budget | (0.495, -0.035, 0.030)→(0.492, -0.035, 0.110) | (0.505, -0.067, 0.037)→(0.502, -0.073, 0.033) | 0.016→0.012 | 1.00 / 2.000 | 1.064 | 17.332 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 1.000
- alignment_error: None
- force_efficiency: 0.324
- terminal_score: 1.000
- phase_score: 0.869
- phase_breakdown.reach_contact_score: 0.767
- phase_breakdown.goal_progress_score: 0.912

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.921
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.776
- **K-run variance**: 0.0040
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.391


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.15859,"average_solve_count":227.0,"average_success_count":227.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.06964,"contact_1.contact_force_threshold":7.89002,"descend_1.descend_speed":0.04034,"push_1.insertion_depth":0.14456,"push_1.push_speed":0.03633},"optimized_scores":{"best_composite_score":0.77559,"best_fitness_score":0.91559,"best_task_score":0.93415},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.50358,0.07682,0.04463],"force_p95":45.85809,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":47.68258,"mean_force":29.4377,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50029,0.08856,0.03458]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.51573,0.04667,0.00977],"force_p95":46.63047,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":46.63047,"mean_force":46.63047,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49907,0.08984,0.03539]},{"body_a":"attachment","body_b":"peg","contact_count":807.0,"contact_point_centroid":[0.50094,-0.00181,0.02894],"force_p95":20.49213,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":25.63212,"mean_force":9.06411,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49937,0.00988,0.02891]},{"body_a":"peg","body_b":"channel_base_body","contact_count":107.0,"contact_point_centroid":[0.49668,-0.10031,0.05756],"force_p95":24.993,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":25.2794,"mean_force":15.74606,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49917,-0.04265,0.02863]},{"body_a":"peg","body_b":"channel_base_body","contact_count":801.0,"contact_point_centroid":[0.49702,-0.02704,0.00997],"force_p95":12.76716,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.53119,"mean_force":10.46468,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49949,0.01468,0.02885]},{"body_a":"peg","body_b":"link7","contact_count":776.0,"contact_point_centroid":[0.50249,-0.01822,0.07064],"force_p95":9.10527,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.17028,"mean_force":3.46494,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49939,0.01461,0.02891]},{"body_a":"peg","body_b":"channel_base_body","contact_count":868.0,"contact_point_centroid":[0.50347,0.06543,0.00941],"force_p95":0.63,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.17163,"mean_force":0.676,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49823,0.12043,0.09993]},{"body_a":"attachment","body_b":"peg","contact_count":42.0,"contact_point_centroid":[0.50244,0.08144,0.05383],"force_p95":7.17584,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.90463,"mean_force":2.88766,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49896,0.09327,0.04266]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":2.0,"contact_point_centroid":[0.52542,0.05852,0.0123],"force_p95":6.6321,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.94382,"mean_force":3.82656,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50102,0.08779,0.03406]},{"body_a":"peg","body_b":"channel_base_body","contact_count":435.0,"contact_point_centroid":[0.50308,0.06751,0.00933],"force_p95":0.56966,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.56642,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49922,0.1753,0.23201]},{"body_a":"peg","body_b":"channel_base_body","contact_count":245.0,"contact_point_centroid":[0.50063,-0.07862,0.0095],"force_p95":0.60434,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.34684,"mean_force":0.52658,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49592,-0.05063,0.06781]},{"body_a":"peg","body_b":"channel_base_body","contact_count":153.0,"contact_point_centroid":[0.50112,-0.10011,0.03661],"force_p95":0.54757,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.98059,"mean_force":0.1834,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4961,-0.05069,0.05839]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":9.0,"contact_point_centroid":[0.52521,0.05093,0.04406],"force_p95":0.7302,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.7953,"mean_force":0.42326,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50395,0.08408,0.03066]}],"total_contact_groups":13},"final_pose_error":0.01971,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5011,-0.082,0.03385],"final_tcp_position":[0.49571,-0.05052,0.10885],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":47.68258,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":451.0,"n_steps_budget":1000.0,"object_pos_end":[0.50308,0.06743,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54626,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":435.0,"raw_peak_contact_force":2.06903,"subtask_id":"reach_contact","tcp_end":[0.50002,0.15166,0.16844],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15885,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":883.0,"n_steps_budget":1000.0,"object_pos_end":[0.50601,0.06072,0.03517],"object_pos_start":[0.50308,0.06743,0.0338],"object_to_goal_dist_end":0.14093,"object_to_goal_dist_start":0.14759,"object_z_max":0.03579,"peak_contact_force":2.75938,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":910.0,"raw_peak_contact_force":9.17163,"subtask_id":"reach_contact","tcp_end":[0.49907,0.08984,0.03539],"tcp_start":[0.50002,0.15166,0.16844],"tcp_to_object_dist_end":0.02994,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":5.0,"n_steps_budget":600.0,"object_pos_end":[0.50677,0.05677,0.03656],"object_pos_start":[0.50601,0.06072,0.03517],"object_to_goal_dist_end":0.13698,"object_to_goal_dist_start":0.14093,"object_z_max":0.03651,"peak_contact_force":11.19283,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":5.0,"raw_peak_contact_force":47.68258,"subtask_id":"reach_contact","tcp_end":[0.50273,0.08603,0.03309],"tcp_start":[0.49907,0.08984,0.03539],"tcp_to_object_dist_end":0.02973,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":892.0,"n_steps_budget":1000.0,"object_pos_end":[0.5013,-0.08156,0.03525],"object_pos_start":[0.50677,0.05677,0.03656],"object_to_goal_dist_end":0.00517,"object_to_goal_dist_start":0.13698,"object_z_max":0.0405,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2500.0,"raw_peak_contact_force":25.63212,"subtask_id":"goal_progress","tcp_end":[0.49881,-0.05075,0.02831],"tcp_start":[0.50273,0.08603,0.03309],"tcp_to_object_dist_end":0.03168,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":246.0,"n_steps_budget":630.0,"object_pos_end":[0.5011,-0.082,0.03385],"object_pos_start":[0.5013,-0.08156,0.03525],"object_to_goal_dist_end":0.00656,"object_to_goal_dist_start":0.00517,"object_z_max":0.03525,"peak_contact_force":2.27257,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":398.0,"raw_peak_contact_force":1.34684,"tcp_end":[0.49571,-0.05052,0.10885],"tcp_start":[0.49881,-0.05075,0.02831],"tcp_to_object_dist_end":0.08152,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.25238,"average_solve_count":210.0,"average_success_count":210.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.08068,"contact_1.contact_force_threshold":5.96704,"descend_1.descend_speed":0.04887,"push_1.insertion_depth":0.19034,"push_1.push_speed":0.04135},"optimized_scores":{"best_composite_score":0.78114,"best_fitness_score":0.92114,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50218,0.12203,0.0389],"force_p95":33.81168,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":33.81168,"mean_force":33.81168,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50029,0.13386,0.03587]},{"body_a":"peg","body_b":"channel_base_body","contact_count":2.0,"contact_point_centroid":[0.49808,0.08825,0.00949],"force_p95":31.29581,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":32.90737,"mean_force":16.79179,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50016,0.13401,0.036]},{"body_a":"attachment","body_b":"peg","contact_count":48.0,"contact_point_centroid":[0.50302,0.12574,0.05202],"force_p95":11.24502,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.24587,"mean_force":4.4986,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50026,0.13759,0.04398]},{"body_a":"peg","body_b":"channel_base_body","contact_count":244.0,"contact_point_centroid":[0.50699,-0.06921,0.00953],"force_p95":0.57802,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.36813,"mean_force":0.58136,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49412,-0.03733,0.07016]},{"body_a":"attachment","body_b":"peg","contact_count":20.0,"contact_point_centroid":[0.50159,-0.04906,0.05887],"force_p95":4.86318,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.96094,"mean_force":1.3852,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.495,-0.03757,0.0396]},{"body_a":"peg","body_b":"channel_base_body","contact_count":773.0,"contact_point_centroid":[0.50421,0.10934,0.00946],"force_p95":0.66301,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.48602,"mean_force":0.78804,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50193,0.16279,0.10136]},{"body_a":"attachment","body_b":"peg","contact_count":692.0,"contact_point_centroid":[0.50014,0.02507,0.03873],"force_p95":8.28422,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.0369,"mean_force":2.34009,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49709,0.03665,0.031]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":9.0,"contact_point_centroid":[0.52512,0.10653,0.05963],"force_p95":7.93447,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.65591,"mean_force":2.64486,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5002,0.13632,0.04112]},{"body_a":"peg","body_b":"channel_base_body","contact_count":611.0,"contact_point_centroid":[0.50169,0.011,0.0098],"force_p95":8.00359,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.6295,"mean_force":2.87371,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49721,0.05232,0.03108]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":361.0,"contact_point_centroid":[0.52509,-0.02188,0.02669],"force_p95":3.80741,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.96813,"mean_force":1.18736,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49698,0.00621,0.03095]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":8.0,"contact_point_centroid":[0.52508,-0.06634,0.05988],"force_p95":4.66942,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.67124,"mean_force":1.21209,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49484,-0.03761,0.03904]},{"body_a":"peg","body_b":"channel_base_body","contact_count":386.0,"contact_point_centroid":[0.50342,0.11164,0.00936],"force_p95":0.62323,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.56428,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50248,0.19526,0.2315]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":131.0,"contact_point_centroid":[0.47487,0.07423,0.03195],"force_p95":1.19093,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.73262,"mean_force":0.44217,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49725,0.1041,0.03099]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49986,0.19958,0.29893]}],"total_contact_groups":14},"final_pose_error":0.01973,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50658,-0.06554,0.03379],"final_tcp_position":[0.4939,-0.03722,0.11141],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":33.81168,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":408.0,"n_steps_budget":1000.0,"object_pos_end":[0.50376,0.1118,0.03382],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19193,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.51474,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":402.0,"raw_peak_contact_force":2.06328,"subtask_id":"reach_contact","tcp_end":[0.50631,0.19157,0.16911],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15708,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":789.0,"n_steps_budget":1000.0,"object_pos_end":[0.50448,0.10433,0.03441],"object_pos_start":[0.50376,0.1118,0.03382],"object_to_goal_dist_end":0.18447,"object_to_goal_dist_start":0.19193,"object_z_max":0.03618,"peak_contact_force":0.66883,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":830.0,"raw_peak_contact_force":17.24587,"subtask_id":"reach_contact","tcp_end":[0.50003,0.13416,0.03614],"tcp_start":[0.50631,0.19157,0.16911],"tcp_to_object_dist_end":0.0302,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":2.0,"n_steps_budget":600.0,"object_pos_end":[0.50429,0.10399,0.03458],"object_pos_start":[0.50448,0.10433,0.03441],"object_to_goal_dist_end":0.18412,"object_to_goal_dist_start":0.18447,"object_z_max":0.03441,"peak_contact_force":33.81168,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3.0,"raw_peak_contact_force":33.81168,"subtask_id":"reach_contact","tcp_end":[0.50083,0.13337,0.0355],"tcp_start":[0.50003,0.13416,0.03614],"tcp_to_object_dist_end":0.02959,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50681,-0.06604,0.03533],"object_pos_start":[0.50429,0.10399,0.03458],"object_to_goal_dist_end":0.01622,"object_to_goal_dist_start":0.18412,"object_z_max":0.03716,"peak_contact_force":1.42061,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1795.0,"raw_peak_contact_force":10.0369,"subtask_id":"goal_progress","tcp_end":[0.49696,-0.0374,0.0309],"tcp_start":[0.50083,0.13337,0.0355],"tcp_to_object_dist_end":0.0306,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":244.0,"n_steps_budget":630.0,"object_pos_end":[0.50658,-0.06554,0.03379],"object_pos_start":[0.50681,-0.06604,0.03533],"object_to_goal_dist_end":0.01706,"object_to_goal_dist_start":0.01622,"object_z_max":0.03533,"peak_contact_force":0.54405,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":272.0,"raw_peak_contact_force":13.36813,"tcp_end":[0.4939,-0.03722,0.11141],"tcp_start":[0.49696,-0.0374,0.0309],"tcp_to_object_dist_end":0.08359,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.06452,"average_solve_count":248.0,"average_success_count":248.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.04701,"contact_1.contact_force_threshold":5.55793,"descend_1.descend_speed":0.04773,"push_1.insertion_depth":0.17089,"push_1.push_speed":0.03435},"optimized_scores":{"best_composite_score":0.64487,"best_fitness_score":0.78487,"best_task_score":0.71775},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.49528,0.12858,0.04507],"force_p95":36.31071,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":38.03169,"mean_force":20.82194,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49223,0.14044,0.03516]},{"body_a":"peg","body_b":"channel_base_body","contact_count":227.0,"contact_point_centroid":[0.5027,-0.05106,0.00995],"force_p95":0.61421,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":37.2813,"mean_force":0.71187,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48741,-0.01764,0.06985]},{"body_a":"peg","body_b":"channel_base_body","contact_count":2.0,"contact_point_centroid":[0.48917,0.09614,0.00992],"force_p95":34.68451,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":36.47428,"mean_force":18.57661,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49181,0.14081,0.03546]},{"body_a":"attachment","body_b":"peg","contact_count":8.0,"contact_point_centroid":[0.49751,-0.02653,0.02995],"force_p95":20.35179,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.85581,"mean_force":4.31689,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48978,-0.01781,0.03099]},{"body_a":"attachment","body_b":"peg","contact_count":955.0,"contact_point_centroid":[0.49539,0.04456,0.03055],"force_p95":15.35066,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":25.16519,"mean_force":13.85489,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49043,0.05504,0.03107]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50356,0.02057,0.00981],"force_p95":21.57414,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.62219,"mean_force":19.24236,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4905,0.05863,0.03109]},{"body_a":"peg","body_b":"link7","contact_count":7.0,"contact_point_centroid":[0.50745,-0.05479,0.07079],"force_p95":12.61305,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.37119,"mean_force":3.51722,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48986,-0.0178,0.03092]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":33.0,"contact_point_centroid":[0.52505,-0.0364,0.02121],"force_p95":11.72179,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.77838,"mean_force":10.57186,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49028,-0.01546,0.03091]},{"body_a":"peg","body_b":"link7","contact_count":959.0,"contact_point_centroid":[0.50653,0.02248,0.07039],"force_p95":9.02314,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.10568,"mean_force":8.37596,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49042,0.05534,0.03106]},{"body_a":"peg","body_b":"channel_base_body","contact_count":865.0,"contact_point_centroid":[0.49664,0.11666,0.00948],"force_p95":0.7907,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.12699,"mean_force":0.77244,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48703,0.16897,0.10055]},{"body_a":"attachment","body_b":"peg","contact_count":52.0,"contact_point_centroid":[0.49416,0.13306,0.05236],"force_p95":9.2612,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.84418,"mean_force":4.09352,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49101,0.14485,0.04469]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":6.0,"contact_point_centroid":[0.52506,-0.0386,0.0213],"force_p95":7.98128,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.67276,"mean_force":3.34697,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48994,-0.01778,0.03087]},{"body_a":"peg","body_b":"channel_base_body","contact_count":400.0,"contact_point_centroid":[0.49634,0.11899,0.00941],"force_p95":0.62078,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.55998,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49156,0.19849,0.23163]},{"body_a":"peg","body_b":"channel_base_body","contact_count":115.0,"contact_point_centroid":[0.50596,-0.10011,0.02572],"force_p95":0.86517,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.48908,"mean_force":0.35486,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48703,-0.01757,0.08937]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":95.0,"contact_point_centroid":[0.47495,-0.08982,0.0372],"force_p95":0.62709,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.88945,"mean_force":0.23419,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48706,-0.01757,0.0885]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49947,0.19954,0.29796]}],"total_contact_groups":16},"final_pose_error":0.01983,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49779,-0.07126,0.03139],"final_tcp_position":[0.48715,-0.01756,0.11124],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":38.03169,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":425.0,"n_steps_budget":1000.0,"object_pos_end":[0.49598,0.11906,0.03393],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19919,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.59907,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":424.0,"raw_peak_contact_force":2.24822,"subtask_id":"reach_contact","tcp_end":[0.48495,0.19798,0.16969],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15742,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":879.0,"n_steps_budget":1000.0,"object_pos_end":[0.49754,0.11126,0.03539],"object_pos_start":[0.49598,0.11906,0.03393],"object_to_goal_dist_end":0.19133,"object_to_goal_dist_start":0.19919,"object_z_max":0.03577,"peak_contact_force":0.74361,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":917.0,"raw_peak_contact_force":10.12699,"subtask_id":"reach_contact","tcp_end":[0.49167,0.14095,0.03559],"tcp_start":[0.48495,0.19798,0.16969],"tcp_to_object_dist_end":0.03026,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":600.0,"object_pos_end":[0.498,0.11001,0.0354],"object_pos_start":[0.49754,0.11126,0.03539],"object_to_goal_dist_end":0.19008,"object_to_goal_dist_start":0.19133,"object_z_max":0.03547,"peak_contact_force":26.52159,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":4.0,"raw_peak_contact_force":38.03169,"subtask_id":"reach_contact","tcp_end":[0.49334,0.13953,0.0345],"tcp_start":[0.49167,0.14095,0.03559],"tcp_to_object_dist_end":0.02989,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50594,-0.05314,0.04025],"object_pos_start":[0.498,0.11001,0.0354],"object_to_goal_dist_end":0.02751,"object_to_goal_dist_start":0.19008,"object_z_max":0.04043,"peak_contact_force":23.43361,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2947.0,"raw_peak_contact_force":25.16519,"subtask_id":"goal_progress","tcp_end":[0.49016,-0.01763,0.03083],"tcp_start":[0.49334,0.13953,0.0345],"tcp_to_object_dist_end":0.03998,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":241.0,"n_steps_budget":630.0,"object_pos_end":[0.49779,-0.07126,0.03139],"object_pos_start":[0.50594,-0.05314,0.04025],"object_to_goal_dist_end":0.01246,"object_to_goal_dist_start":0.02751,"object_z_max":0.04057,"peak_contact_force":0.37498,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":458.0,"raw_peak_contact_force":37.2813,"tcp_end":[0.48715,-0.01756,0.11124],"tcp_start":[0.49016,-0.01763,0.03083],"tcp_to_object_dist_end":0.09681,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```