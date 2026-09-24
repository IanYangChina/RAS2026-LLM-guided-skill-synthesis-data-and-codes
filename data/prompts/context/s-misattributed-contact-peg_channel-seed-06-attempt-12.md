## Search State

- **Seed**: 6
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → align → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 9 | 0.2298 | 0.73 | ❌ rejected |
| 11 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.2483 | 0.84 | ❌ rejected |
| 10 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.4602 | 0.90 | ✅ accepted |
| 9 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.4457 | 0.70 | ❌ rejected |
| 8 | approach → descend → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.1348 | 0.02 | ❌ rejected |

**Proposal policy**: task_score is 0.73 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.230) — your mutation base

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

- **Composite score**: 0.230
- **task_score** (E): 0.730
- **fitness_score**: 0.678  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.122
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.570

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1470 |
| descend_1 | 1.00 | 1.00 | 0.1187 |
| align_1 | 1.00 | 1.00 | 0.0057 |
| contact_1 | 0.67 | 1.00 | 0.0198 |
| push_1 | 0.33 | 1.00 | 0.1215 |
| retract_1 | 1.00 | 1.00 | 0.0604 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.498, 0.142, 0.166) | (0.500, 0.099, 0.040)→(0.501, 0.099, 0.034) | 0.180→0.180 | 1.00 / 1.000 | 0.526 | 0.618 |
| descend_1 | descend | 1.00 / step_budget | (0.498, 0.142, 0.166)→(0.497, 0.131, 0.048) | (0.501, 0.099, 0.034)→(0.501, 0.099, 0.034) | 0.180→0.180 | 1.00 / 1.333 | 0.523 | 1.492 |
| align_1 | align | 1.00 / step_budget | (0.497, 0.131, 0.048)→(0.498, 0.130, 0.044) | (0.501, 0.099, 0.034)→(0.501, 0.099, 0.034) | 0.180→0.179 | 1.00 / 2.333 | 3.250 | 5.884 |
| contact_1 | contact | 0.67 / step_budget | (0.498, 0.130, 0.044)→(0.496, 0.113, 0.035) | (0.501, 0.099, 0.034)→(0.502, 0.083, 0.035) | 0.179→0.164 | 1.00 / 2.667 | 40.069 | 40.556 |
| push_1 | push | 0.33 / guard_failure | (0.496, 0.113, 0.035)→(0.493, -0.009, 0.030) | (0.502, 0.083, 0.035)→(0.505, -0.037, 0.037) | 0.164→0.046 | 1.00 / 1.000 | 0.596 | 26.624 |
| retract_1 | retract | 1.00 / step_budget | (0.496, 0.009, 0.037)→(0.493, 0.009, 0.097) | (0.507, -0.020, 0.038)→(0.506, -0.032, 0.034) | 0.061→0.049 | 1.00 / 1.000 | 0.511 | 2.127 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.897
- alignment_error: None
- force_efficiency: 0.245
- terminal_score: 0.897
- phase_score: 0.601
- phase_breakdown.reach_pre_contact_score: 0.553
- phase_breakdown.reach_contact_score: 0.542
- phase_breakdown.reach_goal_score: 0.681

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.834
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.931
- **Median Q (composite search score)**: 0.264
- **K-run variance**: 0.0078
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.274


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.63782,"average_solve_count":312.0,"average_success_count":312.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_align_x":-0.00719,"align_1.speed":0.00953,"approach_1.speed":0.05909,"contact_1.force_threshold":6.00095,"contact_1.speed":0.01115,"descend_1.speed":0.03981,"push_1.push_distance":0.17048,"push_1.push_speed":0.02986,"retract_1.speed":0.04893},"optimized_scores":{"best_composite_score":0.26446,"best_fitness_score":0.83446,"best_task_score":0.93126},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.50731,-0.10035,0.06029],"force_p95":39.78979,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":40.80627,"mean_force":28.50111,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49381,-0.05308,0.02791]},{"body_a":"attachment","body_b":"peg","contact_count":207.0,"contact_point_centroid":[0.50055,0.00549,0.04045],"force_p95":16.18144,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":38.69964,"mean_force":3.24513,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49438,0.01646,0.0289]},{"body_a":"peg","body_b":"channel_base_body","contact_count":68.0,"contact_point_centroid":[0.50687,-0.02656,0.00993],"force_p95":19.45775,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":26.25598,"mean_force":6.93859,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49456,0.0171,0.02915]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":136.0,"contact_point_centroid":[0.52512,-0.00371,0.0234],"force_p95":8.84484,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.28659,"mean_force":2.0165,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49453,0.02314,0.02915]},{"body_a":"peg","body_b":"channel_base_body","contact_count":972.0,"contact_point_centroid":[0.50749,0.04154,0.00995],"force_p95":2.48384,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.85541,"mean_force":1.62143,"phase_index":3.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.4953,0.08551,0.03595]},{"body_a":"attachment","body_b":"peg","contact_count":930.0,"contact_point_centroid":[0.5005,0.07328,0.0433],"force_p95":2.59705,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.52247,"mean_force":1.55504,"phase_index":3.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49534,0.08466,0.03549]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":355.0,"contact_point_centroid":[0.52508,0.05169,0.03304],"force_p95":1.8074,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.5242,"mean_force":1.16991,"phase_index":3.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49633,0.07966,0.03361]},{"body_a":"peg","body_b":"channel_base_body","contact_count":221.0,"contact_point_centroid":[0.50306,0.06735,0.00927],"force_p95":0.8045,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.58558,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50001,0.15677,0.22931]},{"body_a":"peg","body_b":"channel_base_body","contact_count":240.0,"contact_point_centroid":[0.50303,0.06767,0.00938],"force_p95":0.5525,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55954,"mean_force":0.54664,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49923,0.10761,0.10691]},{"body_a":"peg","body_b":"channel_base_body","contact_count":21.0,"contact_point_centroid":[0.50445,0.06578,0.00938],"force_p95":0.55014,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55036,"mean_force":0.54663,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49768,0.09953,0.04597]}],"total_contact_groups":10},"final_pose_error":0.04007,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50744,-0.08154,0.03693],"final_tcp_position":[0.49376,-0.05416,0.02787],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":40.80627,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":237.0,"n_steps_budget":1000.0,"object_pos_end":[0.50301,0.06746,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14763,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54349,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":240.0,"raw_peak_contact_force":0.55954,"subtask_id":"reach_pre_contact","tcp_end":[0.50065,0.11523,0.16366],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13839,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":240.0,"n_steps_budget":1000.0,"object_pos_end":[0.50309,0.06745,0.0338],"object_pos_start":[0.50301,0.06746,0.0338],"object_to_goal_dist_end":0.14762,"object_to_goal_dist_start":0.14763,"object_z_max":0.0338,"peak_contact_force":0.54648,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":21.0,"raw_peak_contact_force":0.55036,"subtask_id":"reach_contact","tcp_end":[0.4994,0.09998,0.04809],"tcp_start":[0.50065,0.11523,0.16366],"tcp_to_object_dist_end":0.03571,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":21.0,"n_steps_budget":600.0,"object_pos_end":[0.50302,0.06743,0.0338],"object_pos_start":[0.50309,0.06745,0.0338],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14762,"object_z_max":0.0338,"peak_contact_force":2.51842,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":2257.0,"raw_peak_contact_force":4.85541,"subtask_id":"reach_contact","tcp_end":[0.49614,0.09934,0.04512],"tcp_start":[0.4994,0.09998,0.04809],"tcp_to_object_dist_end":0.03455,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50712,0.04833,0.03591],"object_pos_start":[0.50302,0.06743,0.0338],"object_to_goal_dist_end":0.12859,"object_to_goal_dist_start":0.14759,"object_z_max":0.03605,"peak_contact_force":40.80627,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":414.0,"raw_peak_contact_force":40.80627,"subtask_id":"reach_contact","tcp_end":[0.49695,0.07664,0.03249],"tcp_start":[0.49614,0.09934,0.04512],"tcp_to_object_dist_end":0.03028,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":238.0,"n_steps_budget":1000.0,"object_pos_end":[0.50744,-0.08154,0.03693],"object_pos_start":[0.50712,0.04833,0.03591],"object_to_goal_dist_end":0.0082,"object_to_goal_dist_start":0.12859,"object_z_max":0.0376,"peak_contact_force":0.53889,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":221.0,"raw_peak_contact_force":2.06903,"subtask_id":"reach_goal","tcp_end":[0.49376,-0.05416,0.02787],"tcp_start":[0.49695,0.07664,0.03249],"tcp_to_object_dist_end":0.03192,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.66763,"average_solve_count":346.0,"average_success_count":346.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_align_x":0.00448,"align_1.speed":0.01247,"approach_1.speed":0.05795,"contact_1.force_threshold":4.6647,"contact_1.speed":0.01412,"descend_1.speed":0.0179,"push_1.push_distance":0.16017,"push_1.push_speed":0.0381,"retract_1.speed":0.03269},"optimized_scores":{"best_composite_score":0.3163,"best_fitness_score":0.71963,"best_task_score":0.89716},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":160.0,"contact_point_centroid":[0.50169,0.07216,0.0466],"force_p95":32.29018,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.74785,"mean_force":7.6647,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49691,0.08339,0.03816]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":153.0,"contact_point_centroid":[0.52523,0.04866,0.03063],"force_p95":32.13795,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":36.28799,"mean_force":5.45873,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49656,0.07618,0.03766]},{"body_a":"peg","body_b":"channel_base_body","contact_count":66.0,"contact_point_centroid":[0.50465,0.03668,0.00986],"force_p95":25.79714,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":31.49573,"mean_force":8.52696,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49701,0.08116,0.03826]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.52514,-0.02971,0.05203],"force_p95":1.60118,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":26.62435,"mean_force":1.05838,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49433,0.00878,0.05692]},{"body_a":"attachment","body_b":"peg","contact_count":8.0,"contact_point_centroid":[0.50333,-0.00268,0.06174],"force_p95":18.78677,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":26.39529,"mean_force":3.8815,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49619,0.00848,0.03708]},{"body_a":"peg","body_b":"channel_base_body","contact_count":19.0,"contact_point_centroid":[0.50481,0.09702,0.00956],"force_p95":5.32078,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.41768,"mean_force":1.37886,"phase_index":3.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50013,0.14132,0.04285]},{"body_a":"attachment","body_b":"peg","contact_count":6.0,"contact_point_centroid":[0.50295,0.12943,0.05652],"force_p95":5.08246,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.13954,"mean_force":2.97189,"phase_index":3.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50022,0.14141,0.04299]},{"body_a":"peg","body_b":"channel_base_body","contact_count":185.0,"contact_point_centroid":[0.50345,0.11181,0.00929],"force_p95":0.84291,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.5884,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50299,0.17511,0.22921]},{"body_a":"peg","body_b":"channel_base_body","contact_count":281.0,"contact_point_centroid":[0.50357,0.10943,0.00945],"force_p95":0.61403,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.03349,"mean_force":0.55477,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49964,0.14182,0.04408]},{"body_a":"attachment","body_b":"peg","contact_count":78.0,"contact_point_centroid":[0.50297,0.12973,0.05902],"force_p95":0.33318,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.57071,"mean_force":0.14286,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.5,0.14173,0.04363]},{"body_a":"peg","body_b":"channel_base_body","contact_count":194.0,"contact_point_centroid":[0.50521,-0.03445,0.00945],"force_p95":0.96954,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.54953,"mean_force":0.56219,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49359,0.00899,0.0673]},{"body_a":"peg","body_b":"channel_base_body","contact_count":248.0,"contact_point_centroid":[0.50378,0.11162,0.00941],"force_p95":0.59327,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62874,"mean_force":0.54351,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50282,0.14769,0.1096]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49988,0.19925,0.29871]}],"total_contact_groups":13},"final_pose_error":0.01997,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50637,-0.03177,0.03412],"final_tcp_position":[0.4933,0.00935,0.09749],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":37.74785,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":207.0,"n_steps_budget":1000.0,"object_pos_end":[0.50371,0.11175,0.03396],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19188,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.52322,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":248.0,"raw_peak_contact_force":0.62874,"subtask_id":"reach_pre_contact","tcp_end":[0.5062,0.15279,0.1672],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13944,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":248.0,"n_steps_budget":1000.0,"object_pos_end":[0.50372,0.11172,0.03379],"object_pos_start":[0.50371,0.11175,0.03396],"object_to_goal_dist_end":0.19186,"object_to_goal_dist_start":0.19188,"object_z_max":0.03399,"peak_contact_force":0.52498,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":359.0,"raw_peak_contact_force":2.03349,"subtask_id":"reach_contact","tcp_end":[0.50095,0.14279,0.04857],"tcp_start":[0.5062,0.15279,0.1672],"tcp_to_object_dist_end":0.03451,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":281.0,"n_steps_budget":600.0,"object_pos_end":[0.50373,0.11172,0.03409],"object_pos_start":[0.50372,0.11172,0.03379],"object_to_goal_dist_end":0.19185,"object_to_goal_dist_start":0.19186,"object_z_max":0.03421,"peak_contact_force":5.41768,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":25.0,"raw_peak_contact_force":5.41768,"subtask_id":"reach_contact","tcp_end":[0.50056,0.14172,0.04356],"tcp_start":[0.50095,0.14279,0.04857],"tcp_to_object_dist_end":0.03162,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":19.0,"n_steps_budget":1000.0,"object_pos_end":[0.50402,0.11106,0.03482],"object_pos_start":[0.50373,0.11172,0.03409],"object_to_goal_dist_end":0.19118,"object_to_goal_dist_start":0.19185,"object_z_max":0.03475,"peak_contact_force":36.28799,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":379.0,"raw_peak_contact_force":37.74785,"subtask_id":"reach_contact","tcp_end":[0.49958,0.14047,0.04182],"tcp_start":[0.50056,0.14172,0.04356],"tcp_to_object_dist_end":0.03056,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":232.0,"n_steps_budget":1000.0,"object_pos_end":[0.50724,-0.01954,0.03849],"object_pos_start":[0.50402,0.11106,0.03482],"object_to_goal_dist_end":0.06091,"object_to_goal_dist_start":0.19118,"object_z_max":0.0385,"peak_contact_force":0.59632,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":239.0,"raw_peak_contact_force":26.62435,"subtask_id":"reach_goal","tcp_end":[0.49644,0.00947,0.03721],"tcp_start":[0.49958,0.14047,0.04182],"tcp_to_object_dist_end":0.03098,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":206.0,"n_steps_budget":1000.0,"object_pos_end":[0.50637,-0.03177,0.03412],"object_pos_start":[0.50724,-0.01954,0.03849],"object_to_goal_dist_end":0.04901,"object_to_goal_dist_start":0.06091,"object_z_max":0.03849,"peak_contact_force":0.48325,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":201.0,"raw_peak_contact_force":2.06328,"tcp_end":[0.4933,0.00935,0.09749],"tcp_start":[0.49644,0.00947,0.03721],"tcp_to_object_dist_end":0.07667,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.81343,"average_solve_count":268.0,"average_success_count":268.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_align_x":0.0107,"align_1.speed":0.00991,"approach_1.speed":0.09168,"contact_1.force_threshold":6.51656,"contact_1.speed":0.01264,"descend_1.speed":0.03116,"push_1.push_distance":0.13824,"push_1.push_speed":0.04037,"retract_1.speed":0.05038},"optimized_scores":{"best_composite_score":0.10856,"best_fitness_score":0.47856,"best_task_score":0.36182},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":82.0,"contact_point_centroid":[0.49313,0.03462,0.00971],"force_p95":10.01793,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":43.11318,"mean_force":3.65799,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49005,0.07151,0.0271]},{"body_a":"attachment","body_b":"peg","contact_count":155.0,"contact_point_centroid":[0.49446,0.06262,0.05138],"force_p95":8.91176,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":35.35877,"mean_force":2.19351,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48997,0.07406,0.02699]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":19.0,"contact_point_centroid":[0.47482,0.03966,0.03742],"force_p95":35.10384,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":35.23411,"mean_force":7.02574,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48965,0.06952,0.02646]},{"body_a":"peg","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.51164,0.02504,0.06317],"force_p95":20.52484,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.75454,"mean_force":11.49223,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48951,0.05001,0.02626]},{"body_a":"peg","body_b":"channel_base_body","contact_count":993.0,"contact_point_centroid":[0.49424,0.09199,0.00978],"force_p95":1.89774,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.37756,"mean_force":1.01614,"phase_index":3.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.4928,0.13122,0.03354]},{"body_a":"attachment","body_b":"peg","contact_count":717.0,"contact_point_centroid":[0.4938,0.11802,0.03879],"force_p95":1.64437,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.95406,"mean_force":0.88718,"phase_index":3.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49271,0.13,0.03311]},{"body_a":"peg","body_b":"channel_base_body","contact_count":169.0,"contact_point_centroid":[0.49671,0.11902,0.00937],"force_p95":0.76354,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.58634,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49311,0.17763,0.22776]},{"body_a":"peg","body_b":"channel_base_body","contact_count":487.0,"contact_point_centroid":[0.49671,0.11252,0.00964],"force_p95":1.05404,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.89158,"mean_force":0.5896,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.4932,0.14871,0.04345]},{"body_a":"attachment","body_b":"peg","contact_count":243.0,"contact_point_centroid":[0.49537,0.13671,0.05739],"force_p95":0.85163,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.46365,"mean_force":0.24974,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49268,0.14869,0.04336]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49958,0.19851,0.2958]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":120.0,"contact_point_centroid":[0.47497,0.10529,0.02815],"force_p95":0.47662,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.66523,"mean_force":0.2257,"phase_index":3.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49285,0.13528,0.03464]},{"body_a":"peg","body_b":"channel_base_body","contact_count":250.0,"contact_point_centroid":[0.4959,0.11914,0.00948],"force_p95":0.60671,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.66434,"mean_force":0.53708,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48849,0.1541,0.10914]}],"total_contact_groups":12},"final_pose_error":0.03629,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49911,-0.01092,0.03613],"final_tcp_position":[0.48932,0.01856,0.02592],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":43.11318,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":194.0,"n_steps_budget":1000.0,"object_pos_end":[0.49603,0.11903,0.03397],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19916,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.51206,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":250.0,"raw_peak_contact_force":0.66434,"subtask_id":"reach_pre_contact","tcp_end":[0.48748,0.15874,0.16802],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14006,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":250.0,"n_steps_budget":1000.0,"object_pos_end":[0.49603,0.11926,0.03397],"object_pos_start":[0.49603,0.11903,0.03397],"object_to_goal_dist_end":0.19939,"object_to_goal_dist_start":0.19916,"object_z_max":0.03417,"peak_contact_force":0.49873,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":730.0,"raw_peak_contact_force":1.89158,"subtask_id":"reach_contact","tcp_end":[0.49144,0.14976,0.04807],"tcp_start":[0.48748,0.15874,0.16802],"tcp_to_object_dist_end":0.03391,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":487.0,"n_steps_budget":690.0,"object_pos_end":[0.49607,0.1186,0.03403],"object_pos_start":[0.49603,0.11926,0.03397],"object_to_goal_dist_end":0.19872,"object_to_goal_dist_start":0.19939,"object_z_max":0.03486,"peak_contact_force":1.81281,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1830.0,"raw_peak_contact_force":7.37756,"subtask_id":"reach_contact","tcp_end":[0.49704,0.14864,0.04309],"tcp_start":[0.49144,0.14976,0.04807],"tcp_to_object_dist_end":0.0314,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49469,0.09101,0.03508],"object_pos_start":[0.49607,0.1186,0.03403],"object_to_goal_dist_end":0.17116,"object_to_goal_dist_start":0.19872,"object_z_max":0.0352,"peak_contact_force":43.11318,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":260.0,"raw_peak_contact_force":43.11318,"subtask_id":"reach_contact","tcp_end":[0.49228,0.12089,0.03025],"tcp_start":[0.49704,0.14864,0.04309],"tcp_to_object_dist_end":0.03037,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":181.0,"n_steps_budget":1000.0,"object_pos_end":[0.49911,-0.01092,0.03613],"object_pos_start":[0.49469,0.09101,0.03508],"object_to_goal_dist_end":0.06919,"object_to_goal_dist_start":0.17116,"object_z_max":0.03844,"peak_contact_force":0.51115,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":193.0,"raw_peak_contact_force":2.24822,"subtask_id":"reach_goal","tcp_end":[0.48932,0.01856,0.02592],"tcp_start":[0.49228,0.12089,0.03025],"tcp_to_object_dist_end":0.0327,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```