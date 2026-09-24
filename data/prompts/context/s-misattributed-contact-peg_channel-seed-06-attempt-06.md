## Search State

- **Seed**: 6
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → descend → contact → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.3315 | 0.80 | ❌ rejected |
| 5 | approach → descend → contact → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | pose_tolerance | 10 | 0.5023 | 0.81 | ❌ rejected |
| 4 | approach → descend → contact → push → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | pose_tolerance | 11 | 0.4475 | 0.77 | ❌ rejected |
| 3 | approach → descend → contact → push → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | pose_tolerance | 9 | 0.5222 | 0.76 | ❌ rejected |
| 2 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.5658 | 0.83 | ✅ accepted |

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

## Current Skill (Q=0.331) — your mutation base

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

- **Composite score**: 0.331
- **task_score** (E): 0.801
- **fitness_score**: 0.790  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.111
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.570

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1673 |
| descend_1 | 1.00 | 1.00 | 0.1167 |
| contact_1 | 0.67 | 1.00 | 0.0188 |
| align_1 | 1.00 | 1.00 | 0.0272 |
| push_1 | 0.00 | 1.00 | 0.0002 |
| retract_1 | 1.00 | 1.00 | 0.0605 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.497, 0.134, 0.148) | (0.500, 0.099, 0.040)→(0.501, 0.099, 0.034) | 0.180→0.180 | 1.00 / 1.333 | 0.637 | 5.613 |
| descend_1 | descend | 1.00 / step_budget | (0.497, 0.134, 0.148)→(0.497, 0.129, 0.031) | (0.501, 0.099, 0.034)→(0.501, 0.099, 0.035) | 0.180→0.179 | 1.00 / 2.000 | 1309.270 | 5.334 |
| contact_1 | contact | 0.67 / force_exceeded | (0.497, 0.129, 0.031)→(0.496, 0.111, 0.029) | (0.501, 0.099, 0.035)→(0.505, 0.082, 0.036) | 0.179→0.162 | 1.00 / 2.667 | 1.800 | 7.117 |
| align_1 | align | 1.00 / step_budget | (0.496, 0.111, 0.029)→(0.497, 0.083, 0.030) | (0.505, 0.082, 0.036)→(0.507, 0.055, 0.036) | 0.162→0.135 | 1.00 / 2.333 | 38.304 | 63.033 |
| push_1 | push | 0.00 / guard_failure | (0.493, -0.035, 0.026)→(0.493, -0.035, 0.026) | (0.507, 0.055, 0.036)→(0.507, -0.062, 0.036) | 0.135→0.021 | 1.00 / 1.000 | 0.548 | 114.214 |
| retract_1 | retract | 1.00 / step_budget | (0.493, -0.035, 0.026)→(0.490, -0.035, 0.087) | (0.507, -0.063, 0.036)→(0.506, -0.066, 0.034) | 0.021→0.020 | 1.00 / 1.000 | 0.579 | 2.127 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.913
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.913
- phase_score: 0.854
- phase_breakdown.reach_pre_contact_score: 0.822
- phase_breakdown.reach_contact_score: 0.807
- phase_breakdown.reach_goal_score: 0.913

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.878
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.465
- **K-run variance**: 0.0382
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.243


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.53107,"average_solve_count":354.0,"average_success_count":354.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset":0.00016,"align_1.speed":0.02573,"approach_1.speed":0.06703,"contact_1.force_threshold":5.49593,"contact_1.speed":0.00673,"descend_1.speed":0.02075,"push_1.push_distance":0.14464,"push_1.push_speed":0.00671,"retract_1.speed":0.06132},"optimized_scores":{"best_composite_score":0.4743,"best_fitness_score":0.87763,"best_task_score":0.91327},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_base_body","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.55403,-0.1,0.06499],"force_p95":72.03355,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":73.11128,"mean_force":62.03595,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4952,-0.04413,0.02572]},{"body_a":"channel_base_body","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.55373,-0.1,0.06499],"force_p95":67.3785,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":68.73636,"mean_force":54.35316,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49525,-0.04467,0.02575]},{"body_a":"peg","body_b":"channel_base_body","contact_count":125.0,"contact_point_centroid":[0.50731,-0.032,0.00993],"force_p95":21.28423,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.94796,"mean_force":11.13589,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49579,0.01286,0.02652]},{"body_a":"attachment","body_b":"peg","contact_count":261.0,"contact_point_centroid":[0.50189,0.00025,0.04269],"force_p95":16.39421,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.41522,"mean_force":4.72781,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49565,0.01163,0.02636]},{"body_a":"peg","body_b":"link7","contact_count":109.0,"contact_point_centroid":[0.52206,-0.02945,0.06185],"force_p95":17.42457,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.70499,"mean_force":3.41924,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49521,-0.00911,0.02578]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":178.0,"contact_point_centroid":[0.52513,-0.00857,0.02843],"force_p95":11.3659,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.15113,"mean_force":2.4117,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49586,0.01951,0.02664]},{"body_a":"peg","body_b":"channel_base_body","contact_count":520.0,"contact_point_centroid":[0.50415,0.03502,0.00998],"force_p95":4.59549,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.84123,"mean_force":2.1591,"phase_index":3.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49656,0.08086,0.02811]},{"body_a":"attachment","body_b":"peg","contact_count":562.0,"contact_point_centroid":[0.50114,0.0689,0.03836],"force_p95":4.17519,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.52315,"mean_force":1.79666,"phase_index":3.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49658,0.08055,0.02812]},{"body_a":"peg","body_b":"channel_base_body","contact_count":728.0,"contact_point_centroid":[0.50302,0.06646,0.00939],"force_p95":0.55073,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.45573,"mean_force":0.57929,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49801,0.10031,0.08724]},{"body_a":"peg","body_b":"channel_base_body","contact_count":26.0,"contact_point_centroid":[0.50321,0.05037,0.00976],"force_p95":5.2778,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.37605,"mean_force":2.30224,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49801,0.09665,0.03042]},{"body_a":"attachment","body_b":"peg","contact_count":14.0,"contact_point_centroid":[0.50161,0.08439,0.04941],"force_p95":5.05138,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.10872,"mean_force":3.59361,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49774,0.09641,0.03009]},{"body_a":"attachment","body_b":"peg","contact_count":20.0,"contact_point_centroid":[0.50253,0.08526,0.0586],"force_p95":4.01992,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.0938,"mean_force":1.4552,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49883,0.09736,0.03592]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":230.0,"contact_point_centroid":[0.52504,0.04406,0.03145],"force_p95":1.59649,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.60238,"mean_force":0.78712,"phase_index":3.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49779,0.07271,0.02926]},{"body_a":"peg","body_b":"channel_base_body","contact_count":590.0,"contact_point_centroid":[0.5031,0.06744,0.00934],"force_p95":0.55521,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.56123,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49904,0.15117,0.22048]},{"body_a":"peg","body_b":"channel_base_body","contact_count":198.0,"contact_point_centroid":[0.50564,-0.0799,0.00941],"force_p95":0.7928,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.6864,"mean_force":0.57698,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4926,-0.04449,0.05506]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.52506,-0.07854,0.05898],"force_p95":0.3871,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54705,"mean_force":0.12317,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49287,-0.04457,0.04508]}],"total_contact_groups":16},"final_pose_error":0.01987,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50678,-0.07866,0.03383],"final_tcp_position":[0.49206,-0.04431,0.08612],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":73.11128,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":606.0,"n_steps_budget":1000.0,"object_pos_end":[0.50302,0.06743,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.46936,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":748.0,"raw_peak_contact_force":5.45573,"subtask_id":"reach_pre_contact","tcp_end":[0.49981,0.10409,0.14648],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11854,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":728.0,"n_steps_budget":1000.0,"object_pos_end":[0.50314,0.06708,0.03448],"object_pos_start":[0.50302,0.06743,0.0338],"object_to_goal_dist_end":0.14722,"object_to_goal_dist_start":0.14759,"object_z_max":0.03444,"peak_contact_force":6.36566,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":40.0,"raw_peak_contact_force":5.37605,"subtask_id":"reach_contact","tcp_end":[0.49892,0.09713,0.03153],"tcp_start":[0.49981,0.10409,0.14648],"tcp_to_object_dist_end":0.03049,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":27.0,"n_steps_budget":1000.0,"object_pos_end":[0.503,0.06613,0.03531],"object_pos_start":[0.50314,0.06708,0.03448],"object_to_goal_dist_end":0.14624,"object_to_goal_dist_start":0.14722,"object_z_max":0.03531,"peak_contact_force":2.07153,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1312.0,"raw_peak_contact_force":7.84123,"subtask_id":"reach_contact","tcp_end":[0.49729,0.09575,0.02953],"tcp_start":[0.49892,0.09713,0.03153],"tcp_to_object_dist_end":0.03071,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":606.0,"n_steps_budget":750.0,"object_pos_end":[0.50705,0.0389,0.03579],"object_pos_start":[0.503,0.06613,0.03531],"object_to_goal_dist_end":0.11918,"object_to_goal_dist_start":0.14624,"object_z_max":0.03596,"peak_contact_force":50.66254,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":676.0,"raw_peak_contact_force":73.11128,"subtask_id":"reach_contact","tcp_end":[0.49872,0.06797,0.03018],"tcp_start":[0.49729,0.09575,0.02953],"tcp_to_object_dist_end":0.03076,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":315.0,"n_steps_budget":1000.0,"object_pos_end":[0.50681,-0.07347,0.03583],"object_pos_start":[0.50705,0.0389,0.03579],"object_to_goal_dist_end":0.01031,"object_to_goal_dist_start":0.11918,"object_z_max":0.03681,"peak_contact_force":0.55371,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":238.0,"raw_peak_contact_force":68.73636,"subtask_id":"reach_goal","tcp_end":[0.49524,-0.04454,0.02573],"tcp_start":[0.49522,-0.04438,0.02573],"tcp_to_object_dist_end":0.03276,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":199.0,"n_steps_budget":840.0,"object_pos_end":[0.50678,-0.07866,0.03383],"object_pos_start":[0.50676,-0.07475,0.03542],"object_to_goal_dist_end":0.00927,"object_to_goal_dist_start":0.00971,"object_z_max":0.03542,"peak_contact_force":0.54748,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":590.0,"raw_peak_contact_force":2.06903,"tcp_end":[0.49206,-0.04431,0.08612],"tcp_start":[0.49524,-0.04454,0.02573],"tcp_to_object_dist_end":0.06427,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.73961,"average_solve_count":361.0,"average_success_count":361.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset":-0.00348,"align_1.speed":0.02701,"approach_1.speed":0.06339,"contact_1.force_threshold":6.90813,"contact_1.speed":0.01454,"descend_1.speed":0.02462,"push_1.push_distance":0.17981,"push_1.push_speed":0.02867,"retract_1.speed":0.04149},"optimized_scores":{"best_composite_score":0.46505,"best_fitness_score":0.86839,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":3,"reported_contact_groups":[{"body_a":"channel_base_body","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.55449,-0.1,0.06499],"force_p95":74.7856,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":75.71414,"mean_force":63.5724,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49565,-0.04444,0.02592]},{"body_a":"channel_base_body","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.55419,-0.1,0.06499],"force_p95":67.26515,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":68.89881,"mean_force":57.60337,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49571,-0.045,0.02595]},{"body_a":"attachment","body_b":"peg","contact_count":248.0,"contact_point_centroid":[0.50233,0.01217,0.04383],"force_p95":19.14204,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.21151,"mean_force":5.04737,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49616,0.02361,0.02663]},{"body_a":"peg","body_b":"channel_base_body","contact_count":134.0,"contact_point_centroid":[0.50696,-0.02624,0.00988],"force_p95":18.83841,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.38988,"mean_force":8.79748,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49613,0.01901,0.0266]},{"body_a":"peg","body_b":"link7","contact_count":43.0,"contact_point_centroid":[0.52235,-0.02996,0.06204],"force_p95":18.11938,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.94475,"mean_force":2.64247,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49565,-0.00935,0.02597]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":212.0,"contact_point_centroid":[0.52513,-0.00415,0.02754],"force_p95":10.39508,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.86666,"mean_force":1.89747,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49614,0.02411,0.02661]},{"body_a":"attachment","body_b":"peg","contact_count":523.0,"contact_point_centroid":[0.50265,0.08653,0.03915],"force_p95":3.9859,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.95236,"mean_force":1.83401,"phase_index":3.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49784,0.09814,0.0283]},{"body_a":"peg","body_b":"channel_base_body","contact_count":477.0,"contact_point_centroid":[0.50644,0.05259,0.00998],"force_p95":4.47137,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.77989,"mean_force":2.1551,"phase_index":3.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49783,0.09836,0.02827]},{"body_a":"peg","body_b":"channel_base_body","contact_count":669.0,"contact_point_centroid":[0.50383,0.10888,0.00944],"force_p95":1.06784,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.38986,"mean_force":0.65832,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50177,0.14297,0.08854]},{"body_a":"attachment","body_b":"peg","contact_count":43.0,"contact_point_centroid":[0.50295,0.12936,0.05756],"force_p95":5.88322,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.08278,"mean_force":2.10265,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50029,0.14138,0.0433]},{"body_a":"peg","body_b":"channel_base_body","contact_count":931.0,"contact_point_centroid":[0.50326,0.07849,0.00996],"force_p95":2.21799,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.54548,"mean_force":1.42621,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49814,0.12512,0.02879]},{"body_a":"attachment","body_b":"peg","contact_count":949.0,"contact_point_centroid":[0.50133,0.11291,0.03724],"force_p95":1.89119,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.32713,"mean_force":1.09438,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49813,0.12475,0.02875]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":409.0,"contact_point_centroid":[0.52503,0.06842,0.02497],"force_p95":1.3761,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.73159,"mean_force":0.70092,"phase_index":3.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49786,0.09688,0.02837]},{"body_a":"peg","body_b":"channel_base_body","contact_count":502.0,"contact_point_centroid":[0.5036,0.11165,0.00937],"force_p95":0.61643,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.55963,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50232,0.17197,0.2208]},{"body_a":"peg","body_b":"channel_base_body","contact_count":198.0,"contact_point_centroid":[0.50596,-0.08088,0.00939],"force_p95":0.7895,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.48264,"mean_force":0.56406,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49298,-0.04482,0.05559]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":5.0,"contact_point_centroid":[0.52519,-0.07527,0.01097],"force_p95":0.58129,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.59211,"mean_force":0.49617,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49571,-0.0451,0.02598]}],"total_contact_groups":19},"final_pose_error":0.01974,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50633,-0.07976,0.03388],"final_tcp_position":[0.4925,-0.04463,0.08646],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":3920.34915,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":524.0,"n_steps_budget":1000.0,"object_pos_end":[0.50368,0.11175,0.03383],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19188,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.02547,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":712.0,"raw_peak_contact_force":6.38986,"subtask_id":"reach_pre_contact","tcp_end":[0.50618,0.14571,0.14811],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11924,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":669.0,"n_steps_budget":1000.0,"object_pos_end":[0.50379,0.11108,0.0347],"object_pos_start":[0.50368,0.11175,0.03383],"object_to_goal_dist_end":0.19119,"object_to_goal_dist_start":0.19188,"object_z_max":0.03468,"peak_contact_force":3920.34915,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1884.0,"raw_peak_contact_force":5.54548,"subtask_id":"reach_contact","tcp_end":[0.49999,0.14104,0.03209],"tcp_start":[0.50618,0.14571,0.14811],"tcp_to_object_dist_end":0.03031,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":991.0,"n_steps_budget":1000.0,"object_pos_end":[0.50699,0.08394,0.03566],"object_pos_start":[0.50379,0.11108,0.0347],"object_to_goal_dist_end":0.16415,"object_to_goal_dist_start":0.19119,"object_z_max":0.03567,"peak_contact_force":1.5921,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1409.0,"raw_peak_contact_force":6.95236,"subtask_id":"reach_contact","tcp_end":[0.49946,0.11321,0.02962],"tcp_start":[0.49999,0.14104,0.03209],"tcp_to_object_dist_end":0.03082,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":581.0,"n_steps_budget":720.0,"object_pos_end":[0.50696,0.05637,0.03555],"object_pos_start":[0.50699,0.08394,0.03566],"object_to_goal_dist_end":0.13662,"object_to_goal_dist_start":0.16415,"object_z_max":0.03586,"peak_contact_force":48.57431,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":640.0,"raw_peak_contact_force":75.71414,"subtask_id":"reach_contact","tcp_end":[0.49923,0.0856,0.03046],"tcp_start":[0.49946,0.11321,0.02962],"tcp_to_object_dist_end":0.03066,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":352.0,"n_steps_budget":1000.0,"object_pos_end":[0.50735,-0.07324,0.03638],"object_pos_start":[0.50696,0.05637,0.03555],"object_to_goal_dist_end":0.01062,"object_to_goal_dist_start":0.13662,"object_z_max":0.03685,"peak_contact_force":0.54394,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":217.0,"raw_peak_contact_force":68.89881,"subtask_id":"reach_goal","tcp_end":[0.49569,-0.04487,0.02594],"tcp_start":[0.49567,-0.0447,0.02593],"tcp_to_object_dist_end":0.03241,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":203.0,"n_steps_budget":1000.0,"object_pos_end":[0.50633,-0.07976,0.03388],"object_pos_start":[0.50736,-0.0743,0.03617],"object_to_goal_dist_end":0.00881,"object_to_goal_dist_start":0.01007,"object_z_max":0.03617,"peak_contact_force":0.5889,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":518.0,"raw_peak_contact_force":2.06328,"tcp_end":[0.4925,-0.04463,0.08646],"tcp_start":[0.49569,-0.04487,0.02594],"tcp_to_object_dist_end":0.06473,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.5618,"average_solve_count":356.0,"average_success_count":356.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset":-0.00734,"align_1.speed":0.03971,"approach_1.speed":0.05269,"contact_1.force_threshold":6.69337,"contact_1.speed":0.01311,"descend_1.speed":0.02962,"push_1.push_distance":0.13577,"push_1.push_speed":0.01679,"retract_1.speed":0.06201},"optimized_scores":{"best_composite_score":0.05505,"best_fitness_score":0.62505,"best_task_score":0.48857},"replay_outcomes":[{"contacts":{"omitted_contact_groups":3,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":37.0,"contact_point_centroid":[0.47499,-0.01513,0.0468],"force_p95":202.24928,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":205.00744,"mean_force":116.40592,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48677,-0.01512,0.04457]},{"body_a":"attachment","body_b":"peg","contact_count":351.0,"contact_point_centroid":[0.49827,0.02655,0.04402],"force_p95":39.10323,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.27366,"mean_force":26.53099,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4893,0.03646,0.02731]},{"body_a":"peg","body_b":"channel_base_body","contact_count":320.0,"contact_point_centroid":[0.50733,-0.00669,0.00994],"force_p95":28.49632,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":34.05416,"mean_force":23.98663,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48922,0.03292,0.02724]},{"body_a":"peg","body_b":"link7","contact_count":304.0,"contact_point_centroid":[0.52086,0.01306,0.06242],"force_p95":18.37173,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":25.97589,"mean_force":14.89581,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48905,0.02846,0.02705]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":315.0,"contact_point_centroid":[0.52508,0.00748,0.05175],"force_p95":24.77704,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":25.71288,"mean_force":17.84179,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48927,0.03336,0.02731]},{"body_a":"peg","body_b":"link7","contact_count":9.0,"contact_point_centroid":[0.52068,-0.03027,0.06199],"force_p95":20.36922,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.63251,"mean_force":8.52492,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48832,-0.01531,0.02678]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":15.0,"contact_point_centroid":[0.52506,-0.04002,0.06],"force_p95":10.64767,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.13802,"mean_force":2.11397,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48716,-0.01511,0.04154]},{"body_a":"attachment","body_b":"peg","contact_count":46.0,"contact_point_centroid":[0.49689,-0.02522,0.06014],"force_p95":9.1064,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.01356,"mean_force":1.55616,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48716,-0.01516,0.04149]},{"body_a":"peg","body_b":"channel_base_body","contact_count":190.0,"contact_point_centroid":[0.50908,-0.04694,0.00978],"force_p95":0.67783,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.13408,"mean_force":0.81724,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48655,-0.01509,0.05616]},{"body_a":"attachment","body_b":"peg","contact_count":420.0,"contact_point_centroid":[0.49817,0.09825,0.03856],"force_p95":4.94922,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.55831,"mean_force":2.54462,"phase_index":3.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49045,0.10858,0.02841]},{"body_a":"peg","body_b":"channel_base_body","contact_count":391.0,"contact_point_centroid":[0.50757,0.06785,0.00996],"force_p95":4.0558,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.97629,"mean_force":2.46211,"phase_index":3.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49041,0.10922,0.02836]},{"body_a":"peg","body_b":"channel_base_body","contact_count":946.0,"contact_point_centroid":[0.49986,0.08864,0.00997],"force_p95":2.21046,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.08052,"mean_force":1.27995,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48989,0.13346,0.02807]},{"body_a":"peg","body_b":"channel_base_body","contact_count":781.0,"contact_point_centroid":[0.4963,0.11633,0.00951],"force_p95":0.90618,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.99287,"mean_force":0.62657,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48672,0.14986,0.08734]},{"body_a":"attachment","body_b":"peg","contact_count":952.0,"contact_point_centroid":[0.49518,0.1218,0.03676],"force_p95":1.8584,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.85496,"mean_force":0.96191,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48988,0.13313,0.02804]},{"body_a":"attachment","body_b":"peg","contact_count":53.0,"contact_point_centroid":[0.49417,0.13655,0.05883],"force_p95":4.01358,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.66244,"mean_force":1.59624,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49049,0.14849,0.04266]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":389.0,"contact_point_centroid":[0.52506,0.08123,0.03502],"force_p95":3.44957,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.62576,"mean_force":1.52764,"phase_index":3.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49055,0.10694,0.02854]}],"total_contact_groups":19},"final_pose_error":0.01984,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50512,-0.0381,0.0338],"final_tcp_position":[0.48576,-0.01504,0.08707],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":205.00744,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":517.0,"n_steps_budget":1000.0,"object_pos_end":[0.49603,0.11903,0.03382],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19917,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":1.41609,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":834.0,"raw_peak_contact_force":4.99287,"subtask_id":"reach_pre_contact","tcp_end":[0.48445,0.15245,0.14894],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12043,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":781.0,"n_steps_budget":1000.0,"object_pos_end":[0.49602,0.11828,0.03477],"object_pos_start":[0.49603,0.11903,0.03382],"object_to_goal_dist_end":0.19839,"object_to_goal_dist_start":0.19917,"object_z_max":0.03493,"peak_contact_force":1.09462,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1898.0,"raw_peak_contact_force":5.08052,"subtask_id":"reach_contact","tcp_end":[0.49154,0.14817,0.03071],"tcp_start":[0.48445,0.15245,0.14894],"tcp_to_object_dist_end":0.03049,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50424,0.0951,0.03607],"object_pos_start":[0.49602,0.11828,0.03477],"object_to_goal_dist_end":0.1752,"object_to_goal_dist_start":0.19839,"object_z_max":0.03617,"peak_contact_force":1.73662,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1260.0,"raw_peak_contact_force":6.55831,"subtask_id":"reach_contact","tcp_end":[0.49132,0.12271,0.02933],"tcp_start":[0.49154,0.14817,0.03071],"tcp_to_object_dist_end":0.03122,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":484.0,"n_steps_budget":600.0,"object_pos_end":[0.50706,0.06996,0.03648],"object_pos_start":[0.50424,0.0951,0.03607],"object_to_goal_dist_end":0.15017,"object_to_goal_dist_start":0.1752,"object_z_max":0.03687,"peak_contact_force":15.67658,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1290.0,"raw_peak_contact_force":40.27366,"subtask_id":"reach_contact","tcp_end":[0.49249,0.09672,0.03085],"tcp_start":[0.49132,0.12271,0.02933],"tcp_to_object_dist_end":0.03098,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":370.0,"n_steps_budget":1000.0,"object_pos_end":[0.50707,-0.03824,0.0365],"object_pos_start":[0.50706,0.06996,0.03648],"object_to_goal_dist_end":0.0425,"object_to_goal_dist_start":0.15017,"object_z_max":0.0372,"peak_contact_force":0.54606,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":297.0,"raw_peak_contact_force":205.00744,"subtask_id":"reach_goal","tcp_end":[0.48868,-0.01511,0.02669],"tcp_start":[0.4887,-0.01499,0.02673],"tcp_to_object_dist_end":0.03113,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":193.0,"n_steps_budget":810.0,"object_pos_end":[0.50512,-0.0381,0.0338],"object_pos_start":[0.50704,-0.03868,0.03645],"object_to_goal_dist_end":0.04266,"object_to_goal_dist_start":0.04207,"object_z_max":0.03669,"peak_contact_force":0.60059,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":516.0,"raw_peak_contact_force":2.24822,"tcp_end":[0.48576,-0.01504,0.08707],"tcp_start":[0.48868,-0.01511,0.02669],"tcp_to_object_dist_end":0.06119,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```