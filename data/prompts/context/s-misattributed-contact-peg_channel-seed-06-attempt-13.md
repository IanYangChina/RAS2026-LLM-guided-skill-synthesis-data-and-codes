## Search State

- **Seed**: 6
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.3174 | 0.73 | ❌ rejected |
| 12 | approach → descend → align → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 9 | 0.2298 | 0.73 | ❌ rejected |
| 11 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.2483 | 0.84 | ❌ rejected |
| 10 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.4602 | 0.90 | ✅ accepted |
| 9 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.4457 | 0.70 | ❌ rejected |

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

## Current Skill (Q=0.317) — your mutation base

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

- **Composite score**: 0.317
- **task_score** (E): 0.728
- **fitness_score**: 0.691  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.067
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.440

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1469 |
| descend_1 | 1.00 | 1.00 | 0.1190 |
| contact_1 | 0.67 | 1.00 | 0.0232 |
| push_1 | 0.33 | 1.00 | 0.0467 |
| retract_1 | 1.00 | 1.00 | 0.0605 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.498, 0.142, 0.166) | (0.500, 0.099, 0.040)→(0.501, 0.099, 0.034) | 0.180→0.180 | 1.00 / 1.000 | 0.559 | 0.618 |
| descend_1 | descend | 1.00 / step_budget | (0.498, 0.142, 0.166)→(0.497, 0.131, 0.048) | (0.501, 0.099, 0.034)→(0.501, 0.099, 0.034) | 0.180→0.180 | 1.00 / 2.000 | 2.801 | 5.164 |
| contact_1 | contact | 0.67 / step_budget | (0.497, 0.131, 0.048)→(0.496, 0.112, 0.036) | (0.501, 0.099, 0.034)→(0.505, 0.083, 0.035) | 0.180→0.163 | 1.00 / 3.333 | 36.473 | 45.220 |
| push_1 | push | 0.33 / guard_failure | (0.494, 0.038, 0.033)→(0.492, -0.009, 0.031) | (0.505, 0.083, 0.035)→(0.507, -0.035, 0.036) | 0.163→0.049 | 1.00 / 1.000 | 0.552 | 123.287 |
| retract_1 | retract | 1.00 / step_budget | (0.492, -0.009, 0.031)→(0.489, -0.009, 0.092) | (0.507, -0.035, 0.036)→(0.504, -0.033, 0.034) | 0.049→0.049 | 1.00 / 1.000 | 0.510 | 2.127 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.847
- alignment_error: None
- force_efficiency: 0.328
- terminal_score: 0.847
- phase_score: 0.614
- phase_breakdown.reach_pre_contact_score: 0.555
- phase_breakdown.reach_contact_score: 0.536
- phase_breakdown.reach_goal_score: 0.718

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.832
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.913
- **Median Q (composite search score)**: 0.392
- **K-run variance**: 0.0261
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.308


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.63492,"average_solve_count":378.0,"average_success_count":378.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.0455,"contact_1.force_threshold":4.9008,"contact_1.speed":0.01394,"descend_1.speed":0.02364,"push_1.push_distance":0.16963,"push_1.push_speed":0.02478,"retract_1.speed":0.06437},"optimized_scores":{"best_composite_score":0.39201,"best_fitness_score":0.83201,"best_task_score":0.91276},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":276.0,"contact_point_centroid":[0.50169,-0.00388,0.04589],"force_p95":24.57397,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":51.95946,"mean_force":7.26746,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49509,0.00744,0.0282]},{"body_a":"peg","body_b":"channel_base_body","contact_count":9.0,"contact_point_centroid":[0.50693,-0.10062,0.05967],"force_p95":40.70668,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":41.22814,"mean_force":29.14059,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49457,-0.05372,0.02748]},{"body_a":"attachment","body_b":"peg","contact_count":73.0,"contact_point_centroid":[0.49852,-0.06521,0.04943],"force_p95":27.32505,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":30.94316,"mean_force":11.35306,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49201,-0.05438,0.03985]},{"body_a":"peg","body_b":"channel_base_body","contact_count":77.0,"contact_point_centroid":[0.5064,-0.10029,0.06083],"force_p95":27.12245,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":30.39043,"mean_force":9.89492,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49201,-0.05433,0.03866]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":253.0,"contact_point_centroid":[0.52526,-0.01932,0.02976],"force_p95":20.83063,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":24.64494,"mean_force":4.34879,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49503,0.00826,0.02813]},{"body_a":"peg","body_b":"channel_base_body","contact_count":124.0,"contact_point_centroid":[0.5064,-0.03151,0.00989],"force_p95":18.7143,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.93059,"mean_force":8.44247,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4953,0.01287,0.02846]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":35.0,"contact_point_centroid":[0.52512,-0.08227,0.05999],"force_p95":9.09979,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.22657,"mean_force":4.57176,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49161,-0.05398,0.03819]},{"body_a":"peg","body_b":"channel_base_body","contact_count":131.0,"contact_point_centroid":[0.50542,-0.08465,0.00965],"force_p95":0.9912,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.69898,"mean_force":0.66968,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49123,-0.05446,0.06627]},{"body_a":"peg","body_b":"channel_base_body","contact_count":985.0,"contact_point_centroid":[0.50548,0.0394,0.00995],"force_p95":2.8104,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.85175,"mean_force":1.85297,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49733,0.08477,0.037]},{"body_a":"attachment","body_b":"peg","contact_count":951.0,"contact_point_centroid":[0.501,0.07239,0.04258],"force_p95":2.50204,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.58668,"mean_force":1.5599,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49732,0.08408,0.03661]},{"body_a":"peg","body_b":"channel_base_body","contact_count":223.0,"contact_point_centroid":[0.50292,0.06742,0.00928],"force_p95":0.80253,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.58519,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49997,0.1571,0.22982]},{"body_a":"peg","body_b":"channel_base_body","contact_count":248.0,"contact_point_centroid":[0.50323,0.06759,0.00938],"force_p95":0.55241,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55954,"mean_force":0.54667,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49917,0.10777,0.10769]}],"total_contact_groups":12},"final_pose_error":0.01984,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50249,-0.07858,0.03444],"final_tcp_position":[0.49125,-0.05467,0.08778],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":51.95946,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":239.0,"n_steps_budget":1000.0,"object_pos_end":[0.50306,0.0675,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14766,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.5457,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":248.0,"raw_peak_contact_force":0.55954,"subtask_id":"reach_pre_contact","tcp_end":[0.50064,0.11531,0.16379],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13853,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":248.0,"n_steps_budget":1000.0,"object_pos_end":[0.50308,0.06743,0.0338],"object_pos_start":[0.50306,0.0675,0.0338],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14766,"object_z_max":0.0338,"peak_contact_force":1.5356,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1936.0,"raw_peak_contact_force":4.85175,"subtask_id":"reach_contact","tcp_end":[0.49942,0.09999,0.04791],"tcp_start":[0.50064,0.11531,0.16379],"tcp_to_object_dist_end":0.03568,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50681,0.04514,0.03572],"object_pos_start":[0.50308,0.06743,0.0338],"object_to_goal_dist_end":0.1254,"object_to_goal_dist_start":0.14759,"object_z_max":0.03573,"peak_contact_force":47.94865,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":662.0,"raw_peak_contact_force":51.95946,"subtask_id":"reach_contact","tcp_end":[0.49836,0.07408,0.03221],"tcp_start":[0.49942,0.09999,0.04791],"tcp_to_object_dist_end":0.03035,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":358.0,"n_steps_budget":1000.0,"object_pos_end":[0.50693,-0.08221,0.03598],"object_pos_start":[0.50681,0.04514,0.03572],"object_to_goal_dist_end":0.00831,"object_to_goal_dist_start":0.1254,"object_z_max":0.03713,"peak_contact_force":0.53958,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":316.0,"raw_peak_contact_force":30.94316,"subtask_id":"reach_goal","tcp_end":[0.49447,-0.05502,0.02736],"tcp_start":[0.49451,-0.05487,0.0274],"tcp_to_object_dist_end":0.03113,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":199.0,"n_steps_budget":780.0,"object_pos_end":[0.50249,-0.07858,0.03444],"object_pos_start":[0.50688,-0.08235,0.03596],"object_to_goal_dist_end":0.00626,"object_to_goal_dist_start":0.00832,"object_z_max":0.03879,"peak_contact_force":0.54422,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":223.0,"raw_peak_contact_force":2.06903,"tcp_end":[0.49125,-0.05467,0.08778],"tcp_start":[0.49447,-0.05502,0.02736],"tcp_to_object_dist_end":0.05953,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.68519,"average_solve_count":324.0,"average_success_count":324.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.06521,"contact_1.force_threshold":3.09239,"contact_1.speed":0.02123,"descend_1.speed":0.0271,"push_1.push_distance":0.15879,"push_1.push_speed":0.01542,"retract_1.speed":0.0434},"optimized_scores":{"best_composite_score":0.46731,"best_fitness_score":0.70731,"best_task_score":0.84679},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":281.0,"contact_point_centroid":[0.50066,0.05885,0.04579],"force_p95":27.03415,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":33.58364,"mean_force":8.97336,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49543,0.06984,0.04009]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":260.0,"contact_point_centroid":[0.52526,0.03882,0.03287],"force_p95":23.83507,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.56619,"mean_force":5.65383,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49529,0.0656,0.03993]},{"body_a":"peg","body_b":"channel_base_body","contact_count":151.0,"contact_point_centroid":[0.50625,0.03392,0.00985],"force_p95":23.10658,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":26.52247,"mean_force":11.29508,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49568,0.07651,0.04043]},{"body_a":"attachment","body_b":"peg","contact_count":30.0,"contact_point_centroid":[0.49952,-0.0105,0.05715],"force_p95":6.02977,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.08127,"mean_force":2.26551,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49322,0.00033,0.05022]},{"body_a":"peg","body_b":"channel_base_body","contact_count":201.0,"contact_point_centroid":[0.50715,-0.0314,0.00967],"force_p95":0.94829,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.98615,"mean_force":0.6556,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49251,0.00052,0.06882]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":30.0,"contact_point_centroid":[0.52507,-0.02571,0.05179],"force_p95":7.38189,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.7716,"mean_force":1.88103,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49302,0.00041,0.0545]},{"body_a":"peg","body_b":"channel_base_body","contact_count":24.0,"contact_point_centroid":[0.5064,0.10434,0.00938],"force_p95":4.417,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.2899,"mean_force":1.00566,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49944,0.14177,0.04565]},{"body_a":"attachment","body_b":"peg","contact_count":4.0,"contact_point_centroid":[0.5022,0.12937,0.05837],"force_p95":4.73037,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.78924,"mean_force":3.02656,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49902,0.14131,0.04492]},{"body_a":"peg","body_b":"channel_base_body","contact_count":183.0,"contact_point_centroid":[0.50338,0.11148,0.00929],"force_p95":0.84923,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.58876,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50298,0.175,0.22893]},{"body_a":"peg","body_b":"channel_base_body","contact_count":247.0,"contact_point_centroid":[0.50362,0.11182,0.00942],"force_p95":0.60181,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62886,"mean_force":0.54349,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50272,0.14763,0.10901]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49994,0.19922,0.29859]}],"total_contact_groups":11},"final_pose_error":0.01971,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50656,-0.02371,0.03394],"final_tcp_position":[0.49206,0.00074,0.10025],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":33.58364,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":205.0,"n_steps_budget":1000.0,"object_pos_end":[0.50372,0.1118,0.03386],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19194,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.56017,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":247.0,"raw_peak_contact_force":0.62886,"subtask_id":"reach_pre_contact","tcp_end":[0.50602,0.15272,0.16704],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13934,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":247.0,"n_steps_budget":1000.0,"object_pos_end":[0.50368,0.11177,0.03376],"object_pos_start":[0.50372,0.1118,0.03386],"object_to_goal_dist_end":0.19191,"object_to_goal_dist_start":0.19194,"object_z_max":0.03398,"peak_contact_force":4.69829,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":28.0,"raw_peak_contact_force":5.2899,"subtask_id":"reach_contact","tcp_end":[0.5009,0.1428,0.0482],"tcp_start":[0.50602,0.15272,0.16704],"tcp_to_object_dist_end":0.03433,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":24.0,"n_steps_budget":1000.0,"object_pos_end":[0.50385,0.11124,0.03437],"object_pos_start":[0.50368,0.11177,0.03376],"object_to_goal_dist_end":0.19137,"object_to_goal_dist_start":0.19191,"object_z_max":0.0343,"peak_contact_force":19.31055,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":692.0,"raw_peak_contact_force":33.58364,"subtask_id":"reach_contact","tcp_end":[0.49877,0.14054,0.04425],"tcp_start":[0.5009,0.1428,0.0482],"tcp_to_object_dist_end":0.03133,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":382.0,"n_steps_budget":1000.0,"object_pos_end":[0.5069,-0.02648,0.03672],"object_pos_start":[0.50385,0.11124,0.03437],"object_to_goal_dist_end":0.05406,"object_to_goal_dist_start":0.19137,"object_z_max":0.03838,"peak_contact_force":0.54831,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":261.0,"raw_peak_contact_force":24.08127,"subtask_id":"reach_goal","tcp_end":[0.49516,0.00079,0.03972],"tcp_start":[0.49877,0.14054,0.04425],"tcp_to_object_dist_end":0.02984,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":204.0,"n_steps_budget":1000.0,"object_pos_end":[0.50656,-0.02371,0.03394],"object_pos_start":[0.5069,-0.02648,0.03672],"object_to_goal_dist_end":0.05699,"object_to_goal_dist_start":0.05406,"object_z_max":0.03701,"peak_contact_force":0.48181,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":199.0,"raw_peak_contact_force":2.06328,"tcp_end":[0.49206,0.00074,0.10025],"tcp_start":[0.49516,0.00079,0.03972],"tcp_to_object_dist_end":0.07215,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.68852,"average_solve_count":305.0,"average_success_count":305.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.05604,"contact_1.force_threshold":5.57561,"contact_1.speed":0.02022,"descend_1.speed":0.03731,"push_1.push_distance":0.14463,"push_1.push_speed":0.02252,"retract_1.speed":0.04518},"optimized_scores":{"best_composite_score":0.0929,"best_fitness_score":0.5329,"best_task_score":0.42417},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":56.0,"contact_point_centroid":[0.47499,0.02653,0.04466],"force_p95":232.58968,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":314.83685,"mean_force":150.19929,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48679,0.02655,0.04261]},{"body_a":"attachment","body_b":"peg","contact_count":313.0,"contact_point_centroid":[0.49808,0.05985,0.04891],"force_p95":48.86196,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":50.11627,"mean_force":40.02448,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48821,0.06939,0.0267]},{"body_a":"peg","body_b":"channel_base_body","contact_count":316.0,"contact_point_centroid":[0.50787,0.03164,0.00984],"force_p95":34.92483,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":42.15926,"mean_force":29.2251,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48824,0.06986,0.02672]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":310.0,"contact_point_centroid":[0.52521,0.0435,0.05711],"force_p95":32.25533,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":37.25698,"mean_force":26.74626,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48814,0.06863,0.02662]},{"body_a":"peg","body_b":"link7","contact_count":286.0,"contact_point_centroid":[0.52104,0.05145,0.06213],"force_p95":26.65752,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":34.73107,"mean_force":21.40225,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.488,0.06518,0.02653]},{"body_a":"peg","body_b":"link7","contact_count":11.0,"contact_point_centroid":[0.52076,0.01329,0.06184],"force_p95":23.71233,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.8837,"mean_force":12.09504,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48743,0.02681,0.02642]},{"body_a":"peg","body_b":"channel_base_body","contact_count":188.0,"contact_point_centroid":[0.5074,-0.00599,0.00976],"force_p95":0.99866,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.85126,"mean_force":0.99865,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48629,0.02663,0.05628]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":5.0,"contact_point_centroid":[0.52518,0.00219,0.06],"force_p95":16.73197,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.51286,"mean_force":4.42426,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48769,0.02691,0.02625]},{"body_a":"attachment","body_b":"peg","contact_count":48.0,"contact_point_centroid":[0.49553,0.01659,0.05479],"force_p95":11.13035,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.25299,"mean_force":1.84232,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48693,0.02661,0.04025]},{"body_a":"peg","body_b":"channel_base_body","contact_count":804.0,"contact_point_centroid":[0.50172,0.08866,0.00995],"force_p95":3.37918,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.349,"mean_force":2.35665,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49014,0.13316,0.03616]},{"body_a":"attachment","body_b":"peg","contact_count":788.0,"contact_point_centroid":[0.49539,0.12105,0.04499],"force_p95":3.02019,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.01211,"mean_force":2.03109,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49018,0.13245,0.03576]},{"body_a":"peg","body_b":"channel_base_body","contact_count":177.0,"contact_point_centroid":[0.49673,0.11898,0.00934],"force_p95":0.74205,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.58644,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49301,0.17789,0.22868]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49951,0.19875,0.2967]},{"body_a":"peg","body_b":"channel_base_body","contact_count":249.0,"contact_point_centroid":[0.49593,0.11925,0.00945],"force_p95":0.60255,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.66506,"mean_force":0.53983,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48846,0.15409,0.10894]}],"total_contact_groups":14},"final_pose_error":0.01994,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50182,0.0033,0.0342],"final_tcp_position":[0.485,0.02683,0.08655],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":314.83685,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":202.0,"n_steps_budget":1000.0,"object_pos_end":[0.49602,0.11899,0.03391],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19913,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.56975,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":249.0,"raw_peak_contact_force":0.66506,"subtask_id":"reach_pre_contact","tcp_end":[0.48738,0.15878,0.1682],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14033,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":249.0,"n_steps_budget":1000.0,"object_pos_end":[0.49605,0.11923,0.03389],"object_pos_start":[0.49602,0.11899,0.03391],"object_to_goal_dist_end":0.19936,"object_to_goal_dist_start":0.19913,"object_z_max":0.03403,"peak_contact_force":2.16889,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1592.0,"raw_peak_contact_force":5.349,"subtask_id":"reach_contact","tcp_end":[0.49142,0.14973,0.04798],"tcp_start":[0.48738,0.15878,0.1682],"tcp_to_object_dist_end":0.03392,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":839.0,"n_steps_budget":1000.0,"object_pos_end":[0.5041,0.09267,0.03585],"object_pos_start":[0.49605,0.11923,0.03389],"object_to_goal_dist_end":0.17277,"object_to_goal_dist_start":0.19936,"object_z_max":0.03599,"peak_contact_force":42.15926,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1225.0,"raw_peak_contact_force":50.11627,"subtask_id":"reach_contact","tcp_end":[0.49188,0.12048,0.03013],"tcp_start":[0.49142,0.14973,0.04798],"tcp_to_object_dist_end":0.03091,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":338.0,"n_steps_budget":1000.0,"object_pos_end":[0.50723,0.00514,0.03634],"object_pos_start":[0.5041,0.09267,0.03585],"object_to_goal_dist_end":0.08552,"object_to_goal_dist_start":0.17277,"object_z_max":0.03706,"peak_contact_force":0.56812,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":308.0,"raw_peak_contact_force":314.83685,"subtask_id":"reach_goal","tcp_end":[0.48776,0.02707,0.0263],"tcp_start":[0.48777,0.02723,0.02632],"tcp_to_object_dist_end":0.031,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":196.0,"n_steps_budget":1000.0,"object_pos_end":[0.50182,0.0033,0.0342],"object_pos_start":[0.50723,0.0049,0.03633],"object_to_goal_dist_end":0.08353,"object_to_goal_dist_start":0.08528,"object_z_max":0.03713,"peak_contact_force":0.50445,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":201.0,"raw_peak_contact_force":2.24822,"tcp_end":[0.485,0.02683,0.08655],"tcp_start":[0.48776,0.02707,0.0263],"tcp_to_object_dist_end":0.05981,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```