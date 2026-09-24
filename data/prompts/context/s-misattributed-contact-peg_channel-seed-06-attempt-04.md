## Search State

- **Seed**: 6
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → descend → contact → push → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | pose_tolerance | 11 | 0.4475 | 0.77 | ❌ rejected |
| 3 | approach → descend → contact → push → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | pose_tolerance | 9 | 0.5222 | 0.76 | ❌ rejected |
| 2 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.5658 | 0.83 | ✅ accepted |
| 1 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | -0.0775 | 0.00 | ✅ accepted |
| 0 | align → lift → push → approach → approach → descend → grasp | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | force_threshold_switch | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | -0.0805 | 0.00 | ✅ accepted |

**Proposal policy**: task_score is 0.77 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.447) — your mutation base

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

- **Composite score**: 0.447
- **task_score** (E): 0.774
- **fitness_score**: 0.762  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.356
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.670

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1672 |
| descend_1 | 1.00 | 1.00 | 0.1167 |
| contact_1 | 1.00 | 1.00 | 0.0020 |
| lateral_adjust | 1.00 | 1.00 | 0.0001 |
| push_1 | 0.67 | 1.00 | 0.1597 |
| retract_1 | 1.00 | 1.00 | 0.0604 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.497, 0.134, 0.148) | (0.500, 0.099, 0.040)→(0.501, 0.099, 0.034) | 0.180→0.180 | 1.00 / 1.000 | 0.485 | 4.982 |
| descend_1 | descend | 1.00 / step_budget | (0.497, 0.134, 0.148)→(0.497, 0.129, 0.031) | (0.501, 0.099, 0.034)→(0.501, 0.099, 0.035) | 0.180→0.179 | 1.00 / 2.000 | 6.159 | 6.214 |
| contact_1 | contact | 1.00 / force_exceeded | (0.497, 0.129, 0.031)→(0.496, 0.128, 0.030) | (0.501, 0.099, 0.035)→(0.501, 0.098, 0.035) | 0.179→0.178 | 1.00 / 2.000 | 9.882 | 9.882 |
| lateral_adjust | push | 1.00 / force_exceeded | (0.496, 0.128, 0.030)→(0.496, 0.128, 0.030) | (0.501, 0.098, 0.035)→(0.501, 0.098, 0.035) | 0.178→0.178 | 1.00 / 2.667 | 47.047 | 67.160 |
| push_1 | push | 0.67 / step_budget | (0.496, 0.128, 0.030)→(0.492, -0.032, 0.026) | (0.501, 0.098, 0.035)→(0.505, -0.058, 0.036) | 0.178→0.025 | 1.00 / 1.000 | 0.554 | 158.799 |
| retract_1 | retract | 1.00 / step_budget | (0.491, -0.022, 0.026)→(0.488, -0.022, 0.086) | (0.504, -0.047, 0.036)→(0.503, -0.053, 0.035) | 0.033→0.028 | 1.00 / 1.000 | 0.555 | 2.127 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.915
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.915
- phase_score: 0.784
- phase_breakdown.reach_pre_contact_score: 0.820
- phase_breakdown.reach_contact_score: 0.538
- phase_breakdown.reach_goal_score: 0.943

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.837
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.915
- **Median Q (composite search score)**: 0.438
- **K-run variance**: 0.0088
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.314


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.78596,"average_solve_count":285.0,"average_success_count":285.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.05081,"contact_1.force_threshold":6.52689,"contact_1.speed":0.01234,"descend_1.speed":0.03084,"lateral_adjust.lat_distance":0.01812,"lateral_adjust.lat_force_threshold":8.77561,"lateral_adjust.lat_speed":0.01948,"push_1.push_distance":0.16792,"push_1.push_force_threshold":57.40809,"push_1.push_speed":0.02357,"retract_1.speed":0.05273},"optimized_scores":{"best_composite_score":0.56679,"best_fitness_score":0.83679,"best_task_score":0.91539},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_base_body","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54895,-0.1,0.06499],"force_p95":84.64118,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":84.64118,"mean_force":84.64118,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49438,-0.0511,0.02581]},{"body_a":"attachment","body_b":"peg","contact_count":294.0,"contact_point_centroid":[0.50103,0.01193,0.04293],"force_p95":30.40855,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":45.76074,"mean_force":6.9082,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49486,0.02322,0.02642]},{"body_a":"peg","body_b":"channel_base_body","contact_count":186.0,"contact_point_centroid":[0.50583,-0.01674,0.00979],"force_p95":28.84315,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":35.19997,"mean_force":10.70536,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49493,0.02657,0.02651]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":209.0,"contact_point_centroid":[0.52516,-0.01948,0.03079],"force_p95":17.48384,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":24.07507,"mean_force":3.95367,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49459,0.00814,0.02607]},{"body_a":"peg","body_b":"link7","contact_count":83.0,"contact_point_centroid":[0.52123,-0.00289,0.06244],"force_p95":22.44552,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.15943,"mean_force":5.29518,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49456,0.01715,0.02603]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.50268,0.04932,0.00969],"force_p95":11.15884,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.15884,"mean_force":11.15884,"phase_index":3.0,"phase_name":"lateral_adjust","phase_type":"push","tcp_position_centroid":[0.49805,0.09658,0.0304]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50146,0.08455,0.04602],"force_p95":10.90389,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.90389,"mean_force":10.90389,"phase_index":3.0,"phase_name":"lateral_adjust","phase_type":"push","tcp_position_centroid":[0.49805,0.09658,0.0304]},{"body_a":"peg","body_b":"channel_base_body","contact_count":13.0,"contact_point_centroid":[0.50465,0.05006,0.00964],"force_p95":7.31552,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.27151,"mean_force":2.5004,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49851,0.09699,0.03094]},{"body_a":"attachment","body_b":"peg","contact_count":6.0,"contact_point_centroid":[0.50244,0.08487,0.05443],"force_p95":7.59127,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.99947,"mean_force":4.5141,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49848,0.09697,0.03091]},{"body_a":"peg","body_b":"channel_base_body","contact_count":682.0,"contact_point_centroid":[0.5031,0.06664,0.00939],"force_p95":0.55068,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.41186,"mean_force":0.56747,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49807,0.10037,0.0873]},{"body_a":"attachment","body_b":"peg","contact_count":14.0,"contact_point_centroid":[0.50256,0.08531,0.05842],"force_p95":3.34688,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.96614,"mean_force":1.32811,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49889,0.09741,0.03554]},{"body_a":"peg","body_b":"channel_base_body","contact_count":612.0,"contact_point_centroid":[0.50301,0.06746,0.00934],"force_p95":0.55511,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.56071,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49906,0.15119,0.22052]}],"total_contact_groups":12},"final_pose_error":0.02081,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50763,-0.079,0.03653],"final_tcp_position":[0.4944,-0.05141,0.02584],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":84.64118,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":628.0,"n_steps_budget":1000.0,"object_pos_end":[0.50306,0.0675,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14766,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.44805,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":696.0,"raw_peak_contact_force":5.41186,"subtask_id":"reach_pre_contact","tcp_end":[0.49984,0.10414,0.14657],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11862,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":682.0,"n_steps_budget":1000.0,"object_pos_end":[0.50293,0.06718,0.03445],"object_pos_start":[0.50306,0.0675,0.0338],"object_to_goal_dist_end":0.14731,"object_to_goal_dist_start":0.14766,"object_z_max":0.03447,"peak_contact_force":8.27151,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":19.0,"raw_peak_contact_force":8.27151,"subtask_id":"reach_contact","tcp_end":[0.49896,0.09719,0.0315],"tcp_start":[0.49984,0.10414,0.14657],"tcp_to_object_dist_end":0.03041,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":13.0,"n_steps_budget":1000.0,"object_pos_end":[0.50303,0.06684,0.03471],"object_pos_start":[0.50293,0.06718,0.03445],"object_to_goal_dist_end":0.14697,"object_to_goal_dist_start":0.14731,"object_z_max":0.03466,"peak_contact_force":11.15884,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":11.15884,"subtask_id":"reach_contact","tcp_end":[0.49805,0.09658,0.0304],"tcp_start":[0.49896,0.09719,0.0315],"tcp_to_object_dist_end":0.03046,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.50305,0.06678,0.03476],"object_pos_start":[0.50303,0.06684,0.03471],"object_to_goal_dist_end":0.14691,"object_to_goal_dist_start":0.14697,"object_z_max":0.03471,"peak_contact_force":84.64118,"phase_name":"lateral_adjust","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":773.0,"raw_peak_contact_force":84.64118,"subtask_id":"reach_contact","tcp_end":[0.498,0.09651,0.03033],"tcp_start":[0.49805,0.09658,0.0304],"tcp_to_object_dist_end":0.03048,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":405.0,"n_steps_budget":1000.0,"object_pos_end":[0.50763,-0.079,0.03653],"object_pos_start":[0.50305,0.06678,0.03476],"object_to_goal_dist_end":0.00844,"object_to_goal_dist_start":0.14691,"object_z_max":0.03692,"peak_contact_force":0.55063,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":612.0,"raw_peak_contact_force":2.06903,"subtask_id":"reach_goal","tcp_end":[0.4944,-0.05141,0.02584],"tcp_start":[0.498,0.09651,0.03033],"tcp_to_object_dist_end":0.03241,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.91007,"average_solve_count":278.0,"average_success_count":278.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.0588,"contact_1.force_threshold":4.29604,"contact_1.speed":0.01154,"descend_1.speed":0.03725,"lateral_adjust.lat_distance":0.03104,"lateral_adjust.lat_force_threshold":9.52864,"lateral_adjust.lat_speed":0.02145,"push_1.push_distance":0.16782,"push_1.push_force_threshold":60.59174,"push_1.push_speed":0.03421,"retract_1.speed":0.04183},"optimized_scores":{"best_composite_score":0.43816,"best_fitness_score":0.77483,"best_task_score":0.86116},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.52983,0.06857,0.06],"force_p95":58.52062,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":58.69748,"mean_force":56.92886,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49368,0.06192,0.02527]},{"body_a":"attachment","body_b":"peg","contact_count":394.0,"contact_point_centroid":[0.5022,0.0557,0.05224],"force_p95":37.51821,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":45.44115,"mean_force":19.25609,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49461,0.06695,0.02604]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":338.0,"contact_point_centroid":[0.52541,0.04559,0.04866],"force_p95":31.75425,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":33.96296,"mean_force":19.53562,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49443,0.07389,0.0259]},{"body_a":"peg","body_b":"channel_base_body","contact_count":163.0,"contact_point_centroid":[0.50787,0.01705,0.00974],"force_p95":27.99135,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":33.8022,"mean_force":12.65651,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49481,0.05925,0.02623]},{"body_a":"peg","body_b":"link7","contact_count":49.0,"contact_point_centroid":[0.52242,0.03061,0.0619],"force_p95":27.38741,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":32.98624,"mean_force":9.89097,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49419,0.04914,0.02569]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.50655,0.09328,0.00979],"force_p95":10.74954,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.74954,"mean_force":10.74954,"phase_index":3.0,"phase_name":"lateral_adjust","phase_type":"push","tcp_position_centroid":[0.49898,0.14027,0.03074]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.5025,0.12834,0.04774],"force_p95":10.56344,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.56344,"mean_force":10.56344,"phase_index":3.0,"phase_name":"lateral_adjust","phase_type":"push","tcp_position_centroid":[0.49898,0.14027,0.03074]},{"body_a":"peg","body_b":"channel_base_body","contact_count":14.0,"contact_point_centroid":[0.49615,0.09648,0.00964],"force_p95":4.07406,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.02114,"mean_force":1.44416,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49949,0.14077,0.03136]},{"body_a":"attachment","body_b":"peg","contact_count":5.0,"contact_point_centroid":[0.50206,0.12875,0.04274],"force_p95":4.39893,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.69327,"mean_force":2.9458,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49943,0.14072,0.03128]},{"body_a":"peg","body_b":"channel_base_body","contact_count":640.0,"contact_point_centroid":[0.50373,0.10898,0.00946],"force_p95":0.89924,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.22228,"mean_force":0.62437,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50181,0.143,0.08856]},{"body_a":"attachment","body_b":"peg","contact_count":36.0,"contact_point_centroid":[0.50305,0.12937,0.05788],"force_p95":3.70186,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.89949,"mean_force":1.78932,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50031,0.14139,0.04271]},{"body_a":"peg","body_b":"channel_base_body","contact_count":516.0,"contact_point_centroid":[0.50357,0.11164,0.00938],"force_p95":0.61711,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.55868,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50228,0.17202,0.22096]},{"body_a":"peg","body_b":"channel_base_body","contact_count":196.0,"contact_point_centroid":[0.50171,-0.04524,0.00953],"force_p95":0.79573,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.10876,"mean_force":0.55478,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49231,-0.00895,0.05557]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49976,0.19934,0.29908]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":4.0,"contact_point_centroid":[0.52503,-0.04553,0.05917],"force_p95":0.1847,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19203,"mean_force":0.12664,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49286,-0.0093,0.0352]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.49864,-0.02064,0.04141],"force_p95":0.0,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49508,-0.00869,0.02601]}],"total_contact_groups":16},"final_pose_error":0.01997,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50255,-0.04399,0.03482],"final_tcp_position":[0.4919,-0.00867,0.08629],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":58.69748,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":538.0,"n_steps_budget":1000.0,"object_pos_end":[0.50371,0.11178,0.03385],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19192,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.53233,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":676.0,"raw_peak_contact_force":4.22228,"subtask_id":"reach_pre_contact","tcp_end":[0.50619,0.14574,0.14819],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.1193,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":640.0,"n_steps_budget":1000.0,"object_pos_end":[0.50347,0.11104,0.03453],"object_pos_start":[0.50371,0.11178,0.03385],"object_to_goal_dist_end":0.19115,"object_to_goal_dist_start":0.19192,"object_z_max":0.03483,"peak_contact_force":5.02114,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":19.0,"raw_peak_contact_force":5.02114,"subtask_id":"reach_contact","tcp_end":[0.50001,0.14104,0.032],"tcp_start":[0.50619,0.14574,0.14819],"tcp_to_object_dist_end":0.03031,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":14.0,"n_steps_budget":1000.0,"object_pos_end":[0.50385,0.11069,0.03485],"object_pos_start":[0.50347,0.11104,0.03453],"object_to_goal_dist_end":0.1908,"object_to_goal_dist_start":0.19115,"object_z_max":0.03478,"peak_contact_force":10.74954,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":10.74954,"subtask_id":"reach_contact","tcp_end":[0.49898,0.14027,0.03074],"tcp_start":[0.50001,0.14104,0.032],"tcp_to_object_dist_end":0.03026,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":900.0,"object_pos_end":[0.50391,0.11062,0.03492],"object_pos_start":[0.50385,0.11069,0.03485],"object_to_goal_dist_end":0.19072,"object_to_goal_dist_start":0.1908,"object_z_max":0.03485,"peak_contact_force":0.1019,"phase_name":"lateral_adjust","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":946.0,"raw_peak_contact_force":58.69748,"subtask_id":"reach_contact","tcp_end":[0.49893,0.1402,0.03067],"tcp_start":[0.49898,0.14027,0.03074],"tcp_to_object_dist_end":0.0303,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":432.0,"n_steps_budget":1000.0,"object_pos_end":[0.50052,-0.0384,0.03682],"object_pos_start":[0.50391,0.11062,0.03492],"object_to_goal_dist_end":0.04173,"object_to_goal_dist_start":0.19072,"object_z_max":0.03758,"peak_contact_force":0.5594,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":201.0,"raw_peak_contact_force":1.10876,"subtask_id":"reach_goal","tcp_end":[0.49508,-0.00869,0.02601],"tcp_start":[0.49893,0.1402,0.03067],"tcp_to_object_dist_end":0.03208,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":202.0,"n_steps_budget":1000.0,"object_pos_end":[0.50255,-0.04399,0.03482],"object_pos_start":[0.50052,-0.0384,0.03682],"object_to_goal_dist_end":0.03647,"object_to_goal_dist_start":0.04173,"object_z_max":0.03682,"peak_contact_force":0.5432,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":532.0,"raw_peak_contact_force":2.06328,"tcp_end":[0.4919,-0.00867,0.08629],"tcp_start":[0.49508,-0.00869,0.02601],"tcp_to_object_dist_end":0.06332,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.86111,"average_solve_count":324.0,"average_success_count":324.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.05514,"contact_1.force_threshold":4.94039,"contact_1.speed":0.00528,"descend_1.speed":0.03508,"lateral_adjust.lat_distance":0.01918,"lateral_adjust.lat_force_threshold":7.32403,"lateral_adjust.lat_speed":0.01844,"push_1.push_distance":0.20133,"push_1.push_force_threshold":63.80632,"push_1.push_speed":0.02416,"retract_1.speed":0.03306},"optimized_scores":{"best_composite_score":0.33746,"best_fitness_score":0.67413,"best_task_score":0.54506},"replay_outcomes":[{"contacts":{"omitted_contact_groups":2,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":74.0,"contact_point_centroid":[0.47498,-0.03504,0.04223],"force_p95":276.56543,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":316.48936,"mean_force":185.36817,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4868,-0.03503,0.04031]},{"body_a":"attachment","body_b":"peg","contact_count":545.0,"contact_point_centroid":[0.49571,0.03625,0.03887],"force_p95":55.2215,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":58.14152,"mean_force":27.7641,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48745,0.04589,0.02602]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":5.0,"contact_point_centroid":[0.475,-0.02629,0.02745],"force_p95":48.41083,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":48.70175,"mean_force":46.78901,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48684,-0.02629,0.02553]},{"body_a":"peg","body_b":"channel_base_body","contact_count":529.0,"contact_point_centroid":[0.50815,0.00454,0.00986],"force_p95":44.36081,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":46.16542,"mean_force":32.10066,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48742,0.04367,0.02598]},{"body_a":"peg","body_b":"channel_base_body","contact_count":181.0,"contact_point_centroid":[0.5034,-0.06583,0.00953],"force_p95":3.25154,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":43.48457,"mean_force":1.22756,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48603,-0.03487,0.05674]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":246.0,"contact_point_centroid":[0.52513,-0.02686,0.06],"force_p95":36.55479,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":42.95986,"mean_force":27.08767,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48705,-0.00222,0.02571]},{"body_a":"attachment","body_b":"peg","contact_count":28.0,"contact_point_centroid":[0.49616,-0.04502,0.04907],"force_p95":34.26584,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":35.8771,"mean_force":9.86356,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48681,-0.03549,0.02949]},{"body_a":"peg","body_b":"link7","contact_count":15.0,"contact_point_centroid":[0.52103,-0.04812,0.06139],"force_p95":31.61119,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":35.54781,"mean_force":10.80226,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4868,-0.03568,0.0258]},{"body_a":"peg","body_b":"link7","contact_count":508.0,"contact_point_centroid":[0.51932,0.02421,0.06193],"force_p95":31.83259,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":33.28181,"mean_force":23.88173,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48735,0.03876,0.0259]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52516,-0.05985,0.06],"force_p95":27.61365,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":32.54022,"mean_force":12.24564,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48684,-0.03563,0.02621]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.49272,0.10039,0.00989],"force_p95":7.73744,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.73744,"mean_force":7.73744,"phase_index":3.0,"phase_name":"lateral_adjust","phase_type":"push","tcp_position_centroid":[0.49002,0.14697,0.02909]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.49363,0.13509,0.04198],"force_p95":7.44572,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.44572,"mean_force":7.44572,"phase_index":3.0,"phase_name":"lateral_adjust","phase_type":"push","tcp_position_centroid":[0.49002,0.14697,0.02909]},{"body_a":"peg","body_b":"channel_base_body","contact_count":24.0,"contact_point_centroid":[0.49548,0.10136,0.00984],"force_p95":5.05709,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.34982,"mean_force":1.82968,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.4907,0.14772,0.02991]},{"body_a":"peg","body_b":"channel_base_body","contact_count":751.0,"contact_point_centroid":[0.49634,0.11621,0.00951],"force_p95":0.91093,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.31223,"mean_force":0.63942,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.4867,0.14987,0.08756]},{"body_a":"attachment","body_b":"peg","contact_count":10.0,"contact_point_centroid":[0.49479,0.13566,0.0515],"force_p95":4.95065,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.99834,"mean_force":3.43625,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49062,0.14766,0.02981]},{"body_a":"attachment","body_b":"peg","contact_count":42.0,"contact_point_centroid":[0.4945,0.13645,0.05955],"force_p95":3.92597,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.89788,"mean_force":2.17371,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49064,0.14843,0.0408]}],"total_contact_groups":18},"final_pose_error":0.01972,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5033,-0.06203,0.0342],"final_tcp_position":[0.48426,-0.03495,0.08593],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":316.48936,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":517.0,"n_steps_budget":1000.0,"object_pos_end":[0.49599,0.119,0.03395],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19914,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.47489,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":793.0,"raw_peak_contact_force":5.31223,"subtask_id":"reach_pre_contact","tcp_end":[0.48444,0.15246,0.14899],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12036,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":751.0,"n_steps_budget":1000.0,"object_pos_end":[0.49607,0.11818,0.03489],"object_pos_start":[0.49599,0.119,0.03395],"object_to_goal_dist_end":0.19829,"object_to_goal_dist_start":0.19914,"object_z_max":0.03499,"peak_contact_force":5.18408,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":34.0,"raw_peak_contact_force":5.34982,"subtask_id":"reach_contact","tcp_end":[0.49151,0.14815,0.03094],"tcp_start":[0.48444,0.15246,0.14899],"tcp_to_object_dist_end":0.03057,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":24.0,"n_steps_budget":1000.0,"object_pos_end":[0.49607,0.11745,0.0352],"object_pos_start":[0.49607,0.11818,0.03489],"object_to_goal_dist_end":0.19754,"object_to_goal_dist_start":0.19829,"object_z_max":0.03518,"peak_contact_force":7.73744,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":7.73744,"subtask_id":"reach_contact","tcp_end":[0.49002,0.14697,0.02909],"tcp_start":[0.49151,0.14815,0.03094],"tcp_to_object_dist_end":0.03075,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":660.0,"object_pos_end":[0.49604,0.11739,0.03523],"object_pos_start":[0.49607,0.11745,0.0352],"object_to_goal_dist_end":0.19749,"object_to_goal_dist_start":0.19754,"object_z_max":0.0352,"peak_contact_force":56.39698,"phase_name":"lateral_adjust","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1833.0,"raw_peak_contact_force":58.14152,"subtask_id":"reach_contact","tcp_end":[0.48998,0.14691,0.02903],"tcp_start":[0.49002,0.14697,0.02909],"tcp_to_object_dist_end":0.03077,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":574.0,"n_steps_budget":1000.0,"object_pos_end":[0.50692,-0.05648,0.03613],"object_pos_start":[0.49604,0.11739,0.03523],"object_to_goal_dist_end":0.02483,"object_to_goal_dist_start":0.19749,"object_z_max":0.0371,"peak_contact_force":0.54778,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":314.0,"raw_peak_contact_force":316.48936,"subtask_id":"reach_goal","tcp_end":[0.48685,-0.03522,0.02548],"tcp_start":[0.48998,0.14691,0.02903],"tcp_to_object_dist_end":0.03112,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":199.0,"n_steps_budget":1000.0,"object_pos_end":[0.5033,-0.06203,0.0342],"object_pos_start":[0.50692,-0.05648,0.03613],"object_to_goal_dist_end":0.01916,"object_to_goal_dist_start":0.02483,"object_z_max":0.03701,"peak_contact_force":0.57251,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":516.0,"raw_peak_contact_force":2.24822,"tcp_end":[0.48426,-0.03495,0.08593],"tcp_start":[0.48685,-0.03522,0.02548],"tcp_to_object_dist_end":0.06141,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```