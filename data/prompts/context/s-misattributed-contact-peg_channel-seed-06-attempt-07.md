## Search State

- **Seed**: 6
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.4227 | 0.75 | ❌ rejected |
| 6 | approach → descend → contact → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.3315 | 0.80 | ❌ rejected |
| 5 | approach → descend → contact → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | pose_tolerance | 10 | 0.5023 | 0.81 | ❌ rejected |
| 4 | approach → descend → contact → push → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | pose_tolerance | 11 | 0.4475 | 0.77 | ❌ rejected |
| 3 | approach → descend → contact → push → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | pose_tolerance | 9 | 0.5222 | 0.76 | ❌ rejected |

**Proposal policy**: task_score is 0.75 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.423) — your mutation base

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

- **Composite score**: 0.423
- **task_score** (E): 0.752
- **fitness_score**: 0.729  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.133
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.440

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1672 |
| descend_1 | 1.00 | 1.00 | 0.1167 |
| contact_1 | 0.67 | 1.00 | 0.0074 |
| push_1 | 0.67 | 1.00 | 0.0916 |
| retract_1 | 1.00 | 1.00 | 0.0605 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.497, 0.134, 0.148) | (0.500, 0.099, 0.040)→(0.501, 0.100, 0.034) | 0.180→0.180 | 1.00 / 1.000 | 0.495 | 4.854 |
| descend_1 | descend | 1.00 / step_budget | (0.497, 0.134, 0.148)→(0.497, 0.129, 0.032) | (0.501, 0.100, 0.034)→(0.501, 0.099, 0.035) | 0.180→0.179 | 1.00 / 2.000 | 3.668 | 5.316 |
| contact_1 | contact | 0.67 / force_exceeded | (0.497, 0.129, 0.032)→(0.496, 0.122, 0.030) | (0.501, 0.099, 0.035)→(0.501, 0.092, 0.035) | 0.179→0.172 | 1.00 / 2.667 | 23.290 | 30.506 |
| push_1 | push | 0.67 / step_budget | (0.495, 0.088, 0.029)→(0.493, -0.004, 0.026) | (0.501, 0.092, 0.035)→(0.503, -0.031, 0.036) | 0.172→0.050 | 1.00 / 1.000 | 0.537 | 112.011 |
| retract_1 | retract | 1.00 / step_budget | (0.493, -0.004, 0.026)→(0.490, -0.004, 0.087) | (0.503, -0.031, 0.036)→(0.502, -0.035, 0.034) | 0.050→0.046 | 1.00 / 1.000 | 0.541 | 2.127 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.881
- alignment_error: None
- force_efficiency: 0.707
- terminal_score: 0.881
- phase_score: 0.774
- phase_breakdown.reach_pre_contact_score: 0.821
- phase_breakdown.reach_contact_score: 0.536
- phase_breakdown.reach_goal_score: 0.919

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.817
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.900
- **Median Q (composite search score)**: 0.533
- **K-run variance**: 0.0355
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.325


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.9375,"average_solve_count":320.0,"average_success_count":320.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.04098,"contact_1.force_threshold":2.45673,"contact_1.speed":0.01142,"descend_1.speed":0.03128,"push_1.push_distance":0.15587,"push_1.push_speed":0.03004,"retract_1.speed":0.04552},"optimized_scores":{"best_composite_score":0.57714,"best_fitness_score":0.81714,"best_task_score":0.88127},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":180.0,"contact_point_centroid":[0.49932,-0.01083,0.00971],"force_p95":8.99939,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.64375,"mean_force":2.39653,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49533,0.02871,0.02695]},{"body_a":"attachment","body_b":"peg","contact_count":279.0,"contact_point_centroid":[0.49804,0.01695,0.04126],"force_p95":4.59565,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.43549,"mean_force":1.18634,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49529,0.02861,0.0269]},{"body_a":"peg","body_b":"channel_base_body","contact_count":682.0,"contact_point_centroid":[0.50299,0.06626,0.0094],"force_p95":0.55071,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.39363,"mean_force":0.58801,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49808,0.10033,0.08729]},{"body_a":"attachment","body_b":"peg","contact_count":16.0,"contact_point_centroid":[0.50262,0.08528,0.0592],"force_p95":3.88981,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.01555,"mean_force":2.14306,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49889,0.09737,0.03589]},{"body_a":"peg","body_b":"channel_base_body","contact_count":7.0,"contact_point_centroid":[0.50804,0.05002,0.00979],"force_p95":2.56396,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.471,"mean_force":0.86358,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49874,0.09707,0.03123]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50266,0.08486,0.05656],"force_p95":3.16288,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.16288,"mean_force":3.16288,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49851,0.09699,0.03095]},{"body_a":"peg","body_b":"channel_base_body","contact_count":199.0,"contact_point_centroid":[0.49723,-0.07556,0.00956],"force_p95":0.59637,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.97113,"mean_force":0.55251,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49209,-0.04022,0.0556]},{"body_a":"attachment","body_b":"peg","contact_count":9.0,"contact_point_centroid":[0.49617,-0.05234,0.0487],"force_p95":1.73331,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.65096,"mean_force":0.38855,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49334,-0.0404,0.03488]},{"body_a":"peg","body_b":"channel_base_body","contact_count":615.0,"contact_point_centroid":[0.50308,0.0675,0.00934],"force_p95":0.5551,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.56063,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49905,0.15129,0.22068]}],"total_contact_groups":9},"final_pose_error":0.01972,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49858,-0.07354,0.03486],"final_tcp_position":[0.49165,-0.03992,0.08682],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":14.64375,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":631.0,"n_steps_budget":1000.0,"object_pos_end":[0.50308,0.06743,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.45849,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":698.0,"raw_peak_contact_force":4.39363,"subtask_id":"reach_pre_contact","tcp_end":[0.49984,0.10412,0.14654],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11861,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":682.0,"n_steps_budget":1000.0,"object_pos_end":[0.50316,0.06697,0.03481],"object_pos_start":[0.50308,0.06743,0.0338],"object_to_goal_dist_end":0.1471,"object_to_goal_dist_start":0.14759,"object_z_max":0.03478,"peak_contact_force":3.471,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8.0,"raw_peak_contact_force":3.471,"subtask_id":"reach_contact","tcp_end":[0.49898,0.09715,0.03153],"tcp_start":[0.49984,0.10412,0.14654],"tcp_to_object_dist_end":0.03064,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":7.0,"n_steps_budget":1000.0,"object_pos_end":[0.50306,0.06709,0.03478],"object_pos_start":[0.50316,0.06697,0.03481],"object_to_goal_dist_end":0.14721,"object_to_goal_dist_start":0.1471,"object_z_max":0.03484,"peak_contact_force":5.92059,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":459.0,"raw_peak_contact_force":14.64375,"subtask_id":"reach_contact","tcp_end":[0.49844,0.09695,0.03086],"tcp_start":[0.49898,0.09715,0.03153],"tcp_to_object_dist_end":0.03047,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":362.0,"n_steps_budget":1000.0,"object_pos_end":[0.49631,-0.06947,0.03563],"object_pos_start":[0.50306,0.06709,0.03478],"object_to_goal_dist_end":0.01198,"object_to_goal_dist_start":0.14721,"object_z_max":0.038,"peak_contact_force":0.53527,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":208.0,"raw_peak_contact_force":2.97113,"subtask_id":"reach_goal","tcp_end":[0.49482,-0.04012,0.02628],"tcp_start":[0.49844,0.09695,0.03086],"tcp_to_object_dist_end":0.03084,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":202.0,"n_steps_budget":1000.0,"object_pos_end":[0.49858,-0.07354,0.03486],"object_pos_start":[0.49631,-0.06947,0.03563],"object_to_goal_dist_end":0.00837,"object_to_goal_dist_start":0.01198,"object_z_max":0.03591,"peak_contact_force":0.54539,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":615.0,"raw_peak_contact_force":2.06903,"tcp_end":[0.49165,-0.03992,0.08682],"tcp_start":[0.49482,-0.04012,0.02628],"tcp_to_object_dist_end":0.06227,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.69132,"average_solve_count":311.0,"average_success_count":311.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.06485,"contact_1.force_threshold":5.70924,"contact_1.speed":0.01343,"descend_1.speed":0.02781,"push_1.push_distance":0.15645,"push_1.push_speed":0.01965,"retract_1.speed":0.04084},"optimized_scores":{"best_composite_score":0.53334,"best_fitness_score":0.77334,"best_task_score":0.90045},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_left_wall","contact_count":237.0,"contact_point_centroid":[0.52526,0.04038,0.03583],"force_p95":23.41371,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":32.45882,"mean_force":4.91549,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49558,0.06851,0.0267]},{"body_a":"attachment","body_b":"peg","contact_count":291.0,"contact_point_centroid":[0.5018,0.06179,0.04401],"force_p95":23.2274,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":32.36072,"mean_force":5.94703,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49586,0.07312,0.02706]},{"body_a":"peg","body_b":"channel_base_body","contact_count":131.0,"contact_point_centroid":[0.50572,0.03454,0.00986],"force_p95":19.48133,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.19039,"mean_force":6.52465,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4961,0.0785,0.02734]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":104.0,"contact_point_centroid":[0.52511,-0.03217,0.04711],"force_p95":0.67571,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.32875,"mean_force":0.36973,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49313,0.00285,0.04931]},{"body_a":"attachment","body_b":"peg","contact_count":4.0,"contact_point_centroid":[0.50376,-0.00876,0.06162],"force_p95":13.8662,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.30974,"mean_force":4.0823,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4955,0.00292,0.02653]},{"body_a":"peg","body_b":"channel_base_body","contact_count":10.0,"contact_point_centroid":[0.49363,0.09663,0.00967],"force_p95":5.54801,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.47721,"mean_force":1.7083,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49964,0.1409,0.03166]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.50224,0.12886,0.04436],"force_p95":6.1144,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.30873,"mean_force":4.43944,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49963,0.14088,0.03164]},{"body_a":"peg","body_b":"channel_base_body","contact_count":669.0,"contact_point_centroid":[0.50382,0.10909,0.00944],"force_p95":0.93942,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.19594,"mean_force":0.61587,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50178,0.143,0.08862]},{"body_a":"attachment","body_b":"peg","contact_count":39.0,"contact_point_centroid":[0.50302,0.12938,0.05781],"force_p95":3.71941,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.86742,"mean_force":1.56019,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5003,0.1414,0.04283]},{"body_a":"peg","body_b":"channel_base_body","contact_count":502.0,"contact_point_centroid":[0.50358,0.11164,0.00937],"force_p95":0.61239,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.55949,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50234,0.17198,0.22084]},{"body_a":"peg","body_b":"channel_base_body","contact_count":195.0,"contact_point_centroid":[0.50345,-0.0331,0.00946],"force_p95":0.92574,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.32382,"mean_force":0.57759,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49277,0.00297,0.05644]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4998,0.19933,0.299]}],"total_contact_groups":12},"final_pose_error":0.01988,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50691,-0.0323,0.03383],"final_tcp_position":[0.4924,0.00322,0.08696],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":32.45882,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":524.0,"n_steps_budget":1000.0,"object_pos_end":[0.5037,0.1118,0.03391],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19193,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.53305,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":708.0,"raw_peak_contact_force":6.19594,"subtask_id":"reach_pre_contact","tcp_end":[0.50618,0.14573,0.14816],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11921,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":669.0,"n_steps_budget":1000.0,"object_pos_end":[0.50355,0.11106,0.03457],"object_pos_start":[0.5037,0.1118,0.03391],"object_to_goal_dist_end":0.19117,"object_to_goal_dist_start":0.19193,"object_z_max":0.03466,"peak_contact_force":6.47721,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":13.0,"raw_peak_contact_force":6.47721,"subtask_id":"reach_contact","tcp_end":[0.5,0.14106,0.03213],"tcp_start":[0.50618,0.14573,0.14816],"tcp_to_object_dist_end":0.03031,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":10.0,"n_steps_budget":1000.0,"object_pos_end":[0.50344,0.11079,0.03478],"object_pos_start":[0.50355,0.11106,0.03457],"object_to_goal_dist_end":0.19089,"object_to_goal_dist_start":0.19117,"object_z_max":0.03475,"peak_contact_force":19.53154,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":659.0,"raw_peak_contact_force":32.45882,"subtask_id":"reach_contact","tcp_end":[0.49923,0.1406,0.03116],"tcp_start":[0.5,0.14106,0.03213],"tcp_to_object_dist_end":0.03032,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":372.0,"n_steps_budget":1000.0,"object_pos_end":[0.50655,-0.02519,0.03637],"object_pos_start":[0.50344,0.11079,0.03478],"object_to_goal_dist_end":0.05532,"object_to_goal_dist_start":0.19089,"object_z_max":0.03806,"peak_contact_force":0.54738,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":303.0,"raw_peak_contact_force":16.32875,"subtask_id":"reach_goal","tcp_end":[0.49557,0.00327,0.02659],"tcp_start":[0.49923,0.1406,0.03116],"tcp_to_object_dist_end":0.03204,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":203.0,"n_steps_budget":1000.0,"object_pos_end":[0.50691,-0.0323,0.03383],"object_pos_start":[0.50655,-0.02519,0.03637],"object_to_goal_dist_end":0.0486,"object_to_goal_dist_start":0.05532,"object_z_max":0.03637,"peak_contact_force":0.55901,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":518.0,"raw_peak_contact_force":2.06328,"tcp_end":[0.4924,0.00322,0.08696],"tcp_start":[0.49557,0.00327,0.02659],"tcp_to_object_dist_end":0.06554,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.62179,"average_solve_count":312.0,"average_success_count":312.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.04895,"contact_1.force_threshold":6.04135,"contact_1.speed":0.00946,"descend_1.speed":0.03815,"push_1.push_distance":0.14566,"push_1.push_speed":0.01784,"retract_1.speed":0.05531},"optimized_scores":{"best_composite_score":0.1575,"best_fitness_score":0.5975,"best_task_score":0.47486},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":62.0,"contact_point_centroid":[0.47498,0.02556,0.04361],"force_p95":242.38654,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":316.73173,"mean_force":152.19113,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4868,0.02558,0.0416]},{"body_a":"peg","body_b":"channel_base_body","contact_count":294.0,"contact_point_centroid":[0.50984,0.03384,0.00992],"force_p95":36.15851,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":44.41664,"mean_force":28.37413,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48814,0.07366,0.02576]},{"body_a":"attachment","body_b":"peg","contact_count":302.0,"contact_point_centroid":[0.49564,0.06477,0.03475],"force_p95":37.05646,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.07704,"mean_force":19.06105,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48817,0.07469,0.02579]},{"body_a":"peg","body_b":"link7","contact_count":271.0,"contact_point_centroid":[0.51944,0.05383,0.06162],"force_p95":26.47955,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":36.36496,"mean_force":22.83401,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48804,0.06903,0.02564]},{"body_a":"peg","body_b":"link7","contact_count":11.0,"contact_point_centroid":[0.52006,0.01185,0.06121],"force_p95":23.1804,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.75443,"mean_force":10.96301,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48723,0.02583,0.02562]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":76.0,"contact_point_centroid":[0.52501,0.01345,0.06],"force_p95":22.30872,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.69517,"mean_force":19.70936,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48783,0.03935,0.0255]},{"body_a":"peg","body_b":"channel_base_body","contact_count":186.0,"contact_point_centroid":[0.50398,-0.00761,0.00971],"force_p95":0.82683,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.74001,"mean_force":0.96342,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48628,0.02566,0.0557]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":2.0,"contact_point_centroid":[0.525,0.00063,0.06],"force_p95":13.46946,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.17838,"mean_force":7.08919,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48757,0.02608,0.02537]},{"body_a":"attachment","body_b":"peg","contact_count":42.0,"contact_point_centroid":[0.49487,0.01519,0.05398],"force_p95":10.85385,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.98114,"mean_force":1.88156,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4869,0.02565,0.03909]},{"body_a":"peg","body_b":"channel_base_body","contact_count":961.0,"contact_point_centroid":[0.49549,0.08973,0.00997],"force_p95":2.47799,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.00076,"mean_force":1.15765,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48945,0.13651,0.02774]},{"body_a":"attachment","body_b":"peg","contact_count":965.0,"contact_point_centroid":[0.49259,0.12446,0.03523],"force_p95":2.11714,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.63427,"mean_force":0.86627,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48942,0.13629,0.0277]},{"body_a":"peg","body_b":"channel_base_body","contact_count":752.0,"contact_point_centroid":[0.49603,0.11738,0.00948],"force_p95":0.60375,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.97176,"mean_force":0.58447,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48675,0.1501,0.08764]},{"body_a":"attachment","body_b":"peg","contact_count":31.0,"contact_point_centroid":[0.49486,0.13666,0.05885],"force_p95":3.30236,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.62063,"mean_force":1.39708,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49095,0.14869,0.0376]},{"body_a":"peg","body_b":"channel_base_body","contact_count":493.0,"contact_point_centroid":[0.4963,0.11932,0.00939],"force_p95":0.61965,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.55788,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49129,0.17538,0.22119]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49947,0.19909,0.29799]}],"total_contact_groups":15},"final_pose_error":0.01978,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50014,-5e-05,0.03431],"final_tcp_position":[0.4849,0.0259,0.08579],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":316.73173,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":518.0,"n_steps_budget":1000.0,"object_pos_end":[0.49601,0.11943,0.03392],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19956,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.49288,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":783.0,"raw_peak_contact_force":3.97176,"subtask_id":"reach_pre_contact","tcp_end":[0.48451,0.15253,0.14919],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12048,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":752.0,"n_steps_budget":1000.0,"object_pos_end":[0.49597,0.11853,0.03458],"object_pos_start":[0.49601,0.11943,0.03392],"object_to_goal_dist_end":0.19865,"object_to_goal_dist_start":0.19956,"object_z_max":0.03458,"peak_contact_force":1.05652,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1926.0,"raw_peak_contact_force":6.00076,"subtask_id":"reach_contact","tcp_end":[0.49152,0.14852,0.03091],"tcp_start":[0.48451,0.15253,0.14919],"tcp_to_object_dist_end":0.03054,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49738,0.09916,0.0355],"object_pos_start":[0.49597,0.11853,0.03458],"object_to_goal_dist_end":0.17924,"object_to_goal_dist_start":0.19865,"object_z_max":0.03557,"peak_contact_force":44.41664,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":943.0,"raw_peak_contact_force":44.41664,"subtask_id":"reach_contact","tcp_end":[0.49044,0.12859,0.0285],"tcp_start":[0.49152,0.14852,0.03091],"tcp_to_object_dist_end":0.03103,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":318.0,"n_steps_budget":1000.0,"object_pos_end":[0.50632,0.00306,0.03609],"object_pos_start":[0.49738,0.09916,0.0355],"object_to_goal_dist_end":0.08339,"object_to_goal_dist_start":0.17924,"object_z_max":0.03698,"peak_contact_force":0.5269,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":303.0,"raw_peak_contact_force":316.73173,"subtask_id":"reach_goal","tcp_end":[0.48758,0.02614,0.02539],"tcp_start":[0.48759,0.02632,0.0254],"tcp_to_object_dist_end":0.0316,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":194.0,"n_steps_budget":900.0,"object_pos_end":[0.50014,-5e-05,0.03431],"object_pos_start":[0.50633,0.0028,0.03608],"object_to_goal_dist_end":0.08015,"object_to_goal_dist_start":0.08314,"object_z_max":0.03704,"peak_contact_force":0.51735,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":517.0,"raw_peak_contact_force":2.24822,"tcp_end":[0.4849,0.0259,0.08579],"tcp_start":[0.48758,0.02614,0.02539],"tcp_to_object_dist_end":0.05964,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```