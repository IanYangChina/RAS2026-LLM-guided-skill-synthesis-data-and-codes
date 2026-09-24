## Search State

- **Seed**: 6
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.2483 | 0.84 | ❌ rejected |
| 10 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.4602 | 0.90 | ✅ accepted |
| 9 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.4457 | 0.70 | ❌ rejected |
| 8 | approach → descend → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.1348 | 0.02 | ❌ rejected |
| 7 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.4227 | 0.75 | ❌ rejected |

**Proposal policy**: task_score is 0.84 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.248) — your mutation base

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

- **Composite score**: 0.248
- **task_score** (E): 0.843
- **fitness_score**: 0.688  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.440

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 0.00 | 1.00 | 0.1173 |
| descend_1 | 1.00 | 1.00 | 0.1268 |
| contact_1 | 0.33 | 1.00 | 0.0305 |
| push_1 | 0.00 | 1.00 | 0.1218 |
| retract_1 | 1.00 | 1.00 | 0.0505 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 0.00 / step_budget | (0.500, 0.200, 0.300)→(0.501, 0.154, 0.193) | (0.500, 0.099, 0.040)→(0.501, 0.099, 0.034) | 0.180→0.180 | 1.00 / 1.000 | 0.532 | 0.602 |
| descend_1 | descend | 1.00 / step_budget | (0.501, 0.154, 0.193)→(0.499, 0.135, 0.068) | (0.501, 0.099, 0.034)→(0.501, 0.099, 0.034) | 0.180→0.180 | 1.00 / 2.000 | 1.677 | 2.551 |
| contact_1 | contact | 0.33 / step_budget | (0.499, 0.135, 0.068)→(0.496, 0.117, 0.044) | (0.501, 0.099, 0.034)→(0.502, 0.088, 0.035) | 0.180→0.168 | 1.00 / 2.000 | 4.979 | 91.267 |
| push_1 | push | 0.00 / step_budget | (0.496, 0.117, 0.044)→(0.495, -0.005, 0.040) | (0.502, 0.088, 0.035)→(0.505, -0.033, 0.039) | 0.168→0.050 | 1.00 / 1.333 | 0.602 | 13.033 |
| retract_1 | retract | 1.00 / step_budget | (0.495, -0.005, 0.040)→(0.493, -0.005, 0.090) | (0.505, -0.033, 0.039)→(0.504, -0.063, 0.032) | 0.050→0.021 | 1.00 / 1.000 | 0.539 | 2.127 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.926
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.926
- phase_score: 0.676
- phase_breakdown.reach_pre_contact_score: 0.308
- phase_breakdown.reach_contact_score: 0.680
- phase_breakdown.reach_goal_score: 0.948

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.776
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.989
- **Median Q (composite search score)**: 0.302
- **K-run variance**: 0.0102
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.350


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.77835,"average_solve_count":388.0,"average_success_count":388.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.06487,"contact_1.force_threshold":4.73801,"contact_1.speed":0.01463,"descend_1.speed":0.01538,"push_1.push_distance":0.19408,"push_1.push_speed":0.0274,"retract_1.speed":0.03679},"optimized_scores":{"best_composite_score":0.33561,"best_fitness_score":0.77561,"best_task_score":0.92572},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":89.0,"contact_point_centroid":[0.50108,0.03426,0.04073],"force_p95":73.31593,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":93.3272,"mean_force":19.23083,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49727,0.04535,0.04055]},{"body_a":"peg","body_b":"channel_base_body","contact_count":61.0,"contact_point_centroid":[0.50477,0.00096,0.00986],"force_p95":71.65658,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":74.70748,"mean_force":25.31145,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49742,0.04183,0.04063]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":62.0,"contact_point_centroid":[0.52513,0.00455,0.03436],"force_p95":34.716,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":42.72111,"mean_force":9.14176,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49717,0.03214,0.04003]},{"body_a":"peg","body_b":"channel_base_body","contact_count":31.0,"contact_point_centroid":[0.50381,-0.10104,0.05298],"force_p95":21.83788,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":25.02546,"mean_force":3.56066,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49629,-0.05351,0.0414]},{"body_a":"peg","body_b":"channel_base_body","contact_count":112.0,"contact_point_centroid":[0.50553,-0.08432,0.0094],"force_p95":2.80812,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.25849,"mean_force":1.09585,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49555,-0.05163,0.06077]},{"body_a":"attachment","body_b":"peg","contact_count":12.0,"contact_point_centroid":[0.5009,-0.06511,0.05904],"force_p95":12.98703,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.97479,"mean_force":4.46758,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49552,-0.05346,0.04512]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50472,0.05248,0.00977],"force_p95":2.37819,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.64217,"mean_force":1.39351,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.4981,0.09443,0.0516]},{"body_a":"attachment","body_b":"peg","contact_count":636.0,"contact_point_centroid":[0.50072,0.07947,0.052],"force_p95":2.10581,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.20076,"mean_force":1.51168,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49824,0.09132,0.04852]},{"body_a":"peg","body_b":"channel_base_body","contact_count":97.0,"contact_point_centroid":[0.50279,0.0674,0.00914],"force_p95":1.20473,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.63541,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50183,0.1655,0.24289]},{"body_a":"peg","body_b":"channel_base_body","contact_count":156.0,"contact_point_centroid":[0.5032,0.06768,0.00938],"force_p95":0.55491,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.56003,"mean_force":0.54658,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50162,0.11985,0.13348]}],"total_contact_groups":10},"final_pose_error":0.0298,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50568,-0.08065,0.03379],"final_tcp_position":[0.49527,-0.04979,0.0892],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":93.3272,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":113.0,"n_steps_budget":1000.0,"object_pos_end":[0.50305,0.0675,0.03379],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14766,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.53861,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":156.0,"raw_peak_contact_force":0.56003,"subtask_id":"reach_pre_contact","tcp_end":[0.50318,0.13132,0.18824],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.16712,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":156.0,"n_steps_budget":1000.0,"object_pos_end":[0.50309,0.06745,0.0338],"object_pos_start":[0.50305,0.0675,0.03379],"object_to_goal_dist_end":0.14761,"object_to_goal_dist_start":0.14766,"object_z_max":0.0338,"peak_contact_force":2.17792,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1636.0,"raw_peak_contact_force":2.64217,"subtask_id":"reach_contact","tcp_end":[0.5014,0.10623,0.06758],"tcp_start":[0.50318,0.13132,0.18824],"tcp_to_object_dist_end":0.05145,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50386,0.05666,0.03544],"object_pos_start":[0.50309,0.06745,0.0338],"object_to_goal_dist_end":0.13679,"object_to_goal_dist_start":0.14761,"object_z_max":0.03553,"peak_contact_force":2.29893,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":212.0,"raw_peak_contact_force":93.3272,"subtask_id":"reach_contact","tcp_end":[0.49844,0.08592,0.04309],"tcp_start":[0.5014,0.10623,0.06758],"tcp_to_object_dist_end":0.03073,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":144.0,"n_steps_budget":1000.0,"object_pos_end":[0.50349,-0.08186,0.0341],"object_pos_start":[0.50386,0.05666,0.03544],"object_to_goal_dist_end":0.0071,"object_to_goal_dist_start":0.13679,"object_z_max":0.04135,"peak_contact_force":0.5315,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":155.0,"raw_peak_contact_force":25.02546,"subtask_id":"reach_goal","tcp_end":[0.4979,-0.04936,0.03888],"tcp_start":[0.49844,0.08592,0.04309],"tcp_to_object_dist_end":0.03333,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":112.0,"n_steps_budget":1000.0,"object_pos_end":[0.50568,-0.08065,0.03379],"object_pos_start":[0.50349,-0.08186,0.0341],"object_to_goal_dist_end":0.00844,"object_to_goal_dist_start":0.0071,"object_z_max":0.03503,"peak_contact_force":0.54135,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":97.0,"raw_peak_contact_force":2.06903,"tcp_end":[0.49527,-0.04979,0.0892],"tcp_start":[0.4979,-0.04936,0.03888],"tcp_to_object_dist_end":0.06427,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.76238,"average_solve_count":404.0,"average_success_count":404.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.03801,"contact_1.force_threshold":4.14945,"contact_1.speed":0.0138,"descend_1.speed":0.02617,"push_1.push_distance":0.18478,"push_1.push_speed":0.02581,"retract_1.speed":0.05762},"optimized_scores":{"best_composite_score":0.30222,"best_fitness_score":0.74222,"best_task_score":0.98919},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":96.0,"contact_point_centroid":[0.50207,0.06898,0.04741],"force_p95":43.80153,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":94.22365,"mean_force":9.44636,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49819,0.08038,0.0396]},{"body_a":"peg","body_b":"channel_base_body","contact_count":44.0,"contact_point_centroid":[0.50681,0.03836,0.00967],"force_p95":68.92956,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":87.04168,"mean_force":19.31232,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49846,0.08213,0.0399]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":63.0,"contact_point_centroid":[0.52527,0.04895,0.03089],"force_p95":19.13679,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":25.90703,"mean_force":3.92655,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49797,0.07709,0.03925]},{"body_a":"peg","body_b":"channel_base_body","contact_count":74.0,"contact_point_centroid":[0.49588,-0.07587,0.00936],"force_p95":2.02995,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.51342,"mean_force":0.75344,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49656,-0.0003,0.06937]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50574,0.09055,0.0099],"force_p95":2.29934,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.43643,"mean_force":1.64846,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49942,0.13542,0.05101]},{"body_a":"attachment","body_b":"peg","contact_count":854.0,"contact_point_centroid":[0.50169,0.12236,0.05278],"force_p95":1.9407,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.07235,"mean_force":1.46557,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49944,0.13422,0.04976]},{"body_a":"peg","body_b":"channel_base_body","contact_count":86.0,"contact_point_centroid":[0.50294,0.1118,0.00916],"force_p95":1.18746,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.63988,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50346,0.18208,0.24793]},{"body_a":"peg","body_b":"channel_base_body","contact_count":17.0,"contact_point_centroid":[0.49806,-0.10055,0.05688],"force_p95":1.34406,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.51267,"mean_force":0.40149,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4967,-0.00107,0.05879]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":22.0,"contact_point_centroid":[0.52542,-0.04919,0.04658],"force_p95":0.66025,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.80802,"mean_force":0.28665,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49765,-0.00217,0.04601]},{"body_a":"peg","body_b":"channel_base_body","contact_count":159.0,"contact_point_centroid":[0.50376,0.11169,0.0094],"force_p95":0.60643,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63867,"mean_force":0.54448,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50442,0.15566,0.13646]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49976,0.19934,0.29906]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50236,-0.01028,0.05518],"force_p95":0.0,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49886,0.0016,0.03828]}],"total_contact_groups":12},"final_pose_error":0.02965,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50479,-0.06929,0.03674],"final_tcp_position":[0.49638,0.00081,0.08874],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":94.22365,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":108.0,"n_steps_budget":1000.0,"object_pos_end":[0.50379,0.11175,0.03378],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19189,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.56149,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":159.0,"raw_peak_contact_force":0.63867,"subtask_id":"reach_pre_contact","tcp_end":[0.50721,0.16342,0.19541],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.16972,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":159.0,"n_steps_budget":1000.0,"object_pos_end":[0.50372,0.11175,0.03384],"object_pos_start":[0.50379,0.11175,0.03378],"object_to_goal_dist_end":0.19188,"object_to_goal_dist_start":0.19189,"object_z_max":0.03386,"peak_contact_force":1.49001,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1854.0,"raw_peak_contact_force":2.43643,"subtask_id":"reach_contact","tcp_end":[0.50297,0.1468,0.06763],"tcp_start":[0.50721,0.16342,0.19541],"tcp_to_object_dist_end":0.0487,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50462,0.0982,0.03535],"object_pos_start":[0.50372,0.11175,0.03384],"object_to_goal_dist_end":0.17832,"object_to_goal_dist_start":0.19188,"object_z_max":0.0355,"peak_contact_force":0.61068,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":203.0,"raw_peak_contact_force":94.22365,"subtask_id":"reach_contact","tcp_end":[0.49954,0.12764,0.04247],"tcp_start":[0.50297,0.1468,0.06763],"tcp_to_object_dist_end":0.03071,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":136.0,"n_steps_budget":1000.0,"object_pos_end":[0.50507,-0.02787,0.04521],"object_pos_start":[0.50462,0.0982,0.03535],"object_to_goal_dist_end":0.05263,"object_to_goal_dist_start":0.17832,"object_z_max":0.04488,"peak_contact_force":0.64419,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":114.0,"raw_peak_contact_force":3.51342,"subtask_id":"reach_goal","tcp_end":[0.49886,0.0016,0.03828],"tcp_start":[0.49954,0.12764,0.04247],"tcp_to_object_dist_end":0.0309,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":107.0,"n_steps_budget":870.0,"object_pos_end":[0.50479,-0.06929,0.03674],"object_pos_start":[0.50507,-0.02787,0.04521],"object_to_goal_dist_end":0.01218,"object_to_goal_dist_start":0.05263,"object_z_max":0.04645,"peak_contact_force":0.57526,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":102.0,"raw_peak_contact_force":2.06328,"tcp_end":[0.49638,0.00081,0.08874],"tcp_start":[0.49886,0.0016,0.03828],"tcp_to_object_dist_end":0.08768,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.5958,"average_solve_count":381.0,"average_success_count":381.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.06001,"contact_1.force_threshold":3.37777,"contact_1.speed":0.01177,"descend_1.speed":0.01997,"push_1.push_distance":0.16361,"push_1.push_speed":0.02215,"retract_1.speed":0.04296},"optimized_scores":{"best_composite_score":0.10697,"best_fitness_score":0.54697,"best_task_score":0.61381},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":73.0,"contact_point_centroid":[0.49518,0.09223,0.0448],"force_p95":52.08338,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":86.25125,"mean_force":14.68589,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48931,0.10251,0.0432]},{"body_a":"peg","body_b":"channel_base_body","contact_count":48.0,"contact_point_centroid":[0.50392,0.06255,0.00994],"force_p95":54.10394,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":56.96945,"mean_force":18.51534,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48961,0.10344,0.04353]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":64.0,"contact_point_centroid":[0.52545,0.04995,0.03934],"force_p95":31.48185,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":54.30273,"mean_force":7.70995,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48916,0.0742,0.04218]},{"body_a":"attachment","body_b":"peg","contact_count":4.0,"contact_point_centroid":[0.49697,0.02267,0.04035],"force_p95":9.10836,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.56099,"mean_force":2.9069,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48962,0.0319,0.04158]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":12.0,"contact_point_centroid":[0.52526,0.00486,0.03758],"force_p95":4.95232,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.44458,"mean_force":1.34405,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48937,0.02972,0.04171]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49926,0.09965,0.00989],"force_p95":2.06965,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.57553,"mean_force":1.43934,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49047,0.14367,0.05324]},{"body_a":"peg","body_b":"channel_base_body","contact_count":89.0,"contact_point_centroid":[0.50224,-0.01741,0.00977],"force_p95":1.83341,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.55207,"mean_force":0.6504,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48764,0.03069,0.06522]},{"body_a":"peg","body_b":"channel_base_body","contact_count":72.0,"contact_point_centroid":[0.49706,0.11907,0.00924],"force_p95":1.29434,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.64827,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49622,0.18241,0.24182]},{"body_a":"attachment","body_b":"peg","contact_count":827.0,"contact_point_centroid":[0.49336,0.13076,0.055],"force_p95":1.70043,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.1426,"mean_force":1.24913,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49055,0.14253,0.05202]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":4.0,"contact_point_centroid":[0.47493,-0.04727,0.04365],"force_p95":1.61604,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.6849,"mean_force":1.21939,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48731,0.03182,0.07574]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49958,0.19867,0.29634]},{"body_a":"peg","body_b":"channel_base_body","contact_count":160.0,"contact_point_centroid":[0.49611,0.11914,0.0094],"force_p95":0.59914,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60856,"mean_force":0.5442,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49217,0.16118,0.13709]}],"total_contact_groups":12},"final_pose_error":0.02971,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50069,-0.03916,0.02481],"final_tcp_position":[0.48723,0.03248,0.09204],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":86.25125,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":97.0,"n_steps_budget":1000.0,"object_pos_end":[0.49604,0.11905,0.03384],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19918,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.49711,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":160.0,"raw_peak_contact_force":0.60856,"subtask_id":"reach_pre_contact","tcp_end":[0.4927,0.16801,0.19569],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.16912,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":160.0,"n_steps_budget":1000.0,"object_pos_end":[0.49605,0.11902,0.03383],"object_pos_start":[0.49604,0.11905,0.03384],"object_to_goal_dist_end":0.19915,"object_to_goal_dist_start":0.19918,"object_z_max":0.03384,"peak_contact_force":1.36217,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1827.0,"raw_peak_contact_force":2.57553,"subtask_id":"reach_contact","tcp_end":[0.49354,0.15343,0.0682],"tcp_start":[0.4927,0.16801,0.19569],"tcp_to_object_dist_end":0.04871,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49723,0.10813,0.03548],"object_pos_start":[0.49605,0.11902,0.03383],"object_to_goal_dist_end":0.18821,"object_to_goal_dist_start":0.19915,"object_z_max":0.03556,"peak_contact_force":12.02872,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":185.0,"raw_peak_contact_force":86.25125,"subtask_id":"reach_contact","tcp_end":[0.49091,0.13716,0.04586],"tcp_start":[0.49354,0.15343,0.0682],"tcp_to_object_dist_end":0.03147,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":124.0,"n_steps_budget":1000.0,"object_pos_end":[0.50761,0.0099,0.03898],"object_pos_start":[0.49723,0.10813,0.03548],"object_to_goal_dist_end":0.09023,"object_to_goal_dist_start":0.18821,"object_z_max":0.0403,"peak_contact_force":0.62966,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":109.0,"raw_peak_contact_force":10.56099,"subtask_id":"reach_goal","tcp_end":[0.48961,0.03335,0.04164],"tcp_start":[0.49091,0.13716,0.04586],"tcp_to_object_dist_end":0.02968,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":109.0,"n_steps_budget":1000.0,"object_pos_end":[0.50069,-0.03916,0.02481],"object_pos_start":[0.50761,0.0099,0.03898],"object_to_goal_dist_end":0.04358,"object_to_goal_dist_start":0.09023,"object_z_max":0.04078,"peak_contact_force":0.49959,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":96.0,"raw_peak_contact_force":2.24822,"tcp_end":[0.48723,0.03248,0.09204],"tcp_start":[0.48961,0.03335,0.04164],"tcp_to_object_dist_end":0.09916,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```