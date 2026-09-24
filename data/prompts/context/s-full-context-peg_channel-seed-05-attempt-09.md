## Search State

- **Seed**: 5
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → descend → push → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 14 | -0.3522 | 0.10 | ❌ rejected |
| 8 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 10 | -0.0775 | 0.24 | ✅ accepted |
| 7 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9 | -0.2422 | 0.22 | ✅ accepted |
| 6 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | pose_tolerance | time_limit | pose_tolerance | 9 | -0.2436 | 0.22 | ✅ accepted |
| 5 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | pose_tolerance | time_limit | pose_tolerance | 8 | -0.1804 | 0.19 | ✅ accepted |

**Proposal policy**: task_score is 0.10 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e`
- Frozen object start: [0.5244002338996304, 0.1046352631789195, 0.04]
- Frozen task target: [0.5244002338996304, -0.05536473682108051, 0.04]
- Goal object position: (0.5244002338996304, -0.05536473682108051, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5244002338996304, 0.1046352631789195, 0.04)
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
  frozen_object_start: [0.5244, 0.1046, 0.04]
  frozen_task_target: [0.5244, -0.0554, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5244002338996304, 0.1046352631789195, 0.04]}
  frozen_targets: {'channel_exit': [0.5244002338996304, -0.05536473682108051, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e

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
| `object` | offset from object initial position (0.5244002338996304, 0.1046352631789195, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5244002338996304, -0.05536473682108051, 0.04) | final destination targets |
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

## Current Skill (Q=-0.352) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: reach_approach
  anchor: object
  offset:
  - 0.0
  - 0.03
  - 0.08
  weight: 0.3
- id: push_to_goal
  target_entity: object
  metric: goal_progress
  weight: 0.7
phases:
- id: approach_behind
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
    - 0.08
    tolerance: 0.02
    orientation:
      mode: align_axis
      axis:
      - 1.0
      - 0.0
      - 0.0
      align_with: channel_axis
      tolerance: 0.1
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
    approach_tol:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.005
    - 0.0
  subtask_id: reach_approach
- id: descend_to_peg
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.0
    - 0.02
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_force_threshold:
      type: scalar
      range:
      - 2.0
      - 15.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    descend_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_approach
- id: push_channel
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: time_limit
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.2
      axis: channel_axis
      mode: replace_offset_projection
      sign: positive
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.15
      - 0.3
      default: 0.2
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_duration:
      type: scalar
      range:
      - 5.0
      - 20.0
      default: 12.0
      binds_to:
      - path: duration.max_time
        mode: replace
    push_force_limit:
      type: scalar
      range:
      - 10.0
      - 50.0
      default: 30.0
      binds_to:
      - path: guards.push_force_guard.threshold
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: push_force_guard
    when: during_phase
    predicate: force_below
    threshold: 30.0
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.005
    - 0.0
    - 0.0
  subtask_id: push_to_goal
- id: retract_away
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: world
    offset:
    - 0.5
    - 0.2
    - 0.3
    tolerance: 0.05
    orientation:
      mode: none
  parameters:
    retract_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
    retract_tol:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: push_to_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_behind** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.03, 0.08], tolerance=0.02
  - orientation: mode=align_axis, axis=[1.0, 0.0, 0.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - approach_tol: status=consumed; consumers=termination.pose_tolerance (replace)
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.005, 0.0]
- **descend_to_peg** (`descend`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.0, 0.02], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **push_channel** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.2, mode=replace_offset_projection, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_duration: status=consumed; consumers=duration.max_time (replace)
    - push_force_limit: status=consumed; consumers=guards.push_force_guard.threshold (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=push_force_guard, when=during_phase, predicate=force_below, on_failure=retry, threshold=30.0
  - retries: max_attempts=1, strategy=offset_target, offset=[0.005, 0.0, 0.0]
- **retract_away** (`retract`)
  - target: source=yaml, anchor=world, offset=[0.5, 0.2, 0.3], tolerance=0.05
  - orientation: mode=none
  - parameter_bindings:
    - retract_speed: status=consumed; consumers=generator.speed (replace)
    - retract_tol: status=consumed; consumers=termination.pose_tolerance (replace)

## Design Metrics

- **Composite score**: -0.352
- **task_score** (E): 0.103
- **fitness_score**: 0.238  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.790

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_behind | 1.00 | 1.00 | 0.1519 |
| descend_to_peg | 1.00 | 1.00 | 0.1027 |
| push_channel_1 | 0.00 | 1.00 | 0.0001 |
| push_channel_2 | 0.33 | 1.00 | 0.0511 |
| retract_away | 1.00 | 1.00 | 0.2355 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_behind | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.508, 0.152, 0.158) | (0.512, 0.095, 0.040)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 1.000 | 0.555 | 2.488 |
| descend_to_peg | descend | 1.00 / force_exceeded | (0.508, 0.152, 0.158)→(0.502, 0.123, 0.059) | (0.504, 0.095, 0.034)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 2.000 | 25.589 | 25.589 |
| push_channel_1 | push | 0.00 / guard_failure | (0.501, 0.123, 0.059)→(0.501, 0.123, 0.059) | (0.504, 0.095, 0.034)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 2.000 | 16.874 | 31.308 |
| push_channel_2 | push | 0.33 / guard_failure | (0.501, 0.122, 0.059)→(0.500, 0.071, 0.057) | (0.504, 0.095, 0.034)→(0.501, 0.078, 0.031) | 0.175→0.159 | 1.00 / 1.667 | 19.475 | 25.842 |
| retract_away | retract | 1.00 / step_budget | (0.500, 0.071, 0.057)→(0.500, 0.181, 0.256) | (0.501, 0.078, 0.031)→(0.502, 0.078, 0.031) | 0.159→0.158 | 1.00 / 1.000 | 0.571 | 31.281 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.302
- alignment_error: None
- force_efficiency: 0.589
- terminal_score: 0.302
- phase_score: 0.333
- phase_breakdown.push_to_goal_score: 0.001
- phase_breakdown.contact_peg_score: 0.649
- phase_breakdown.reach_approach_score: 0.676

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.321
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.302
- **Median Q (composite search score)**: -0.390
- **K-run variance**: 0.0034
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.267


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `9b36d26f861d7a613dfb3d8c86d70470e42095a430c2befa4bd6e530468a8a7e`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `2af86d8f59685db6584febc0596b9044223ae39cea3120c112c665a54a1c4732`; realized-scene SHA-256: `ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5244,0.10464,0.04]},{"name":"goal","value":[0.5244,-0.05536,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.5244,0.10464,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.5244,-0.05536,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.24324,"average_solve_count":74.0,"average_success_count":74.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.15455,"approach_behind.approach_tol":0.02442,"descend_to_peg.descend_force_threshold":4.84148,"descend_to_peg.descend_speed":0.1267,"push_channel_1.push1_distance":0.09005,"push_channel_1.push1_force_limit":22.72716,"push_channel_1.push1_speed":0.05744,"push_channel_1.push1_tol":0.01265,"push_channel_2.push2_distance":0.13334,"push_channel_2.push2_force_limit":19.55493,"push_channel_2.push2_speed":0.06524,"push_channel_2.push2_tol":0.01194,"retract_away.retract_speed":0.24238,"retract_away.retract_tol":0.06291},"optimized_scores":{"best_composite_score":-0.39715,"best_fitness_score":0.19285,"best_task_score":0.00378},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":208.0,"contact_point_centroid":[0.50057,0.10418,0.00952],"force_p95":0.91242,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":49.92084,"mean_force":1.48378,"phase_index":4.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.50189,0.15871,0.15069]},{"body_a":"attachment","body_b":"peg","contact_count":12.0,"contact_point_centroid":[0.50894,0.12157,0.05893],"force_p95":45.95436,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":49.39219,"mean_force":16.49679,"phase_index":4.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.50371,0.13223,0.0592]},{"body_a":"peg","body_b":"channel_base_body","contact_count":7.0,"contact_point_centroid":[0.49468,0.10091,0.00931],"force_p95":35.33927,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":37.97092,"mean_force":19.67231,"phase_index":2.0,"phase_name":"push_channel_1","phase_type":"push","tcp_position_centroid":[0.50514,0.13235,0.05885]},{"body_a":"attachment","body_b":"peg","contact_count":7.0,"contact_point_centroid":[0.51058,0.12175,0.05844],"force_p95":35.08792,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.8347,"mean_force":19.22361,"phase_index":2.0,"phase_name":"push_channel_1","phase_type":"push","tcp_position_centroid":[0.50514,0.13235,0.05885]},{"body_a":"peg","body_b":"channel_base_body","contact_count":433.0,"contact_point_centroid":[0.50602,0.10473,0.00939],"force_p95":0.57553,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":32.40784,"mean_force":0.61999,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.51091,0.1463,0.10723]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51091,0.12198,0.05878],"force_p95":31.96798,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":31.96798,"mean_force":31.96798,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50547,0.13264,0.05953]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.48814,0.10077,0.00926],"force_p95":29.20143,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":29.27542,"mean_force":28.60465,"phase_index":3.0,"phase_name":"push_channel_2","phase_type":"push","tcp_position_centroid":[0.50485,0.13199,0.05841]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.51028,0.12143,0.05822],"force_p95":28.70951,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.78644,"mean_force":28.08679,"phase_index":3.0,"phase_name":"push_channel_2","phase_type":"push","tcp_position_centroid":[0.50485,0.13199,0.05841]},{"body_a":"peg","body_b":"channel_base_body","contact_count":255.0,"contact_point_centroid":[0.50515,0.10463,0.00935],"force_p95":0.62382,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.5906,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50827,0.18137,0.22438]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.49984,0.19989,0.29416]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":15.0,"contact_point_centroid":[0.52536,0.10405,0.05847],"force_p95":0.28332,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.33023,"mean_force":0.06838,"phase_index":4.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.50211,0.15007,0.11991]}],"total_contact_groups":11},"final_pose_error":0.04926,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50549,0.10342,0.0342],"final_tcp_position":[0.50117,0.18754,0.25236],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":49.92084,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":282.0,"n_steps_budget":690.0,"object_pos_end":[0.50594,0.10472,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18492,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.52964,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":287.0,"raw_peak_contact_force":3.33087,"subtask_id":"reach_approach","tcp_end":[0.51856,0.16037,0.15781],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13648,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":433.0,"n_steps_budget":660.0,"object_pos_end":[0.50599,0.10461,0.03383],"object_pos_start":[0.50594,0.10472,0.03384],"object_to_goal_dist_end":0.18481,"object_to_goal_dist_start":0.18492,"object_z_max":0.03384,"peak_contact_force":32.40784,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":434.0,"raw_peak_contact_force":32.40784,"subtask_id":"contact_peg","tcp_end":[0.50545,0.13258,0.0593],"tcp_start":[0.51856,0.16037,0.15781],"tcp_to_object_dist_end":0.03783,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":7.0,"n_steps_budget":990.0,"object_pos_end":[0.50553,0.10457,0.03378],"object_pos_start":[0.50599,0.10461,0.03383],"object_to_goal_dist_end":0.18475,"object_to_goal_dist_start":0.18481,"object_z_max":0.03383,"peak_contact_force":29.19876,"phase_name":"push_channel_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":14.0,"raw_peak_contact_force":37.97092,"subtask_id":"push_to_goal","tcp_end":[0.50487,0.13203,0.05847],"tcp_start":[0.5049,0.1321,0.05853],"tcp_to_object_dist_end":0.03694,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50546,0.10437,0.03373],"object_pos_start":[0.50547,0.10443,0.03374],"object_to_goal_dist_end":0.18456,"object_to_goal_dist_start":0.18461,"object_z_max":0.03374,"peak_contact_force":29.27542,"phase_name":"push_channel_2","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":6.0,"raw_peak_contact_force":29.27542,"subtask_id":"push_to_goal","tcp_end":[0.50481,0.13194,0.05831],"tcp_start":[0.50483,0.13196,0.05836],"tcp_to_object_dist_end":0.03694,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":209.0,"n_steps_budget":660.0,"object_pos_end":[0.50549,0.10342,0.0342],"object_pos_start":[0.50542,0.1043,0.03371],"object_to_goal_dist_end":0.1836,"object_to_goal_dist_start":0.18448,"object_z_max":0.0377,"peak_contact_force":0.54974,"phase_name":"retract_away","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":235.0,"raw_peak_contact_force":49.92084,"subtask_id":"push_to_goal","tcp_end":[0.50117,0.18754,0.25236],"tcp_start":[0.50481,0.13194,0.05831],"tcp_to_object_dist_end":0.23385,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `314cefd2153cfe84bc0d0d2dfbeb7f4daf8feaf5f2c7ce7d396802b52a157f39`; realized-scene SHA-256: `07dc0764c781629358e2f97446117d9c410d14c078397be91277b4276116a1de`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50305,0.06746,0.04]},{"name":"goal","value":[0.50305,-0.09254,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.50305,0.06746,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.50305,-0.09254,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.67453,"average_solve_count":212.0,"average_success_count":212.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.12405,"approach_behind.approach_tol":0.01342,"descend_to_peg.descend_force_threshold":6.50418,"descend_to_peg.descend_speed":0.07987,"push_channel_1.push1_distance":0.09176,"push_channel_1.push1_force_limit":16.44745,"push_channel_1.push1_speed":0.09315,"push_channel_1.push1_tol":0.01467,"push_channel_2.push2_distance":0.16096,"push_channel_2.push2_force_limit":23.17493,"push_channel_2.push2_speed":0.08238,"push_channel_2.push2_tol":0.0075,"retract_away.retract_speed":0.06632,"retract_away.retract_tol":0.04855},"optimized_scores":{"best_composite_score":-0.26925,"best_fitness_score":0.32075,"best_task_score":0.30245},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.4883,0.06103,0.00937],"force_p95":19.6655,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.57186,"mean_force":10.94482,"phase_index":2.0,"phase_name":"push_channel_1","phase_type":"push","tcp_position_centroid":[0.4986,0.09658,0.05898]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.5016,0.08516,0.05872],"force_p95":19.12843,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.03715,"mean_force":10.43625,"phase_index":2.0,"phase_name":"push_channel_1","phase_type":"push","tcp_position_centroid":[0.4986,0.09658,0.05898]},{"body_a":"attachment","body_b":"peg","contact_count":187.0,"contact_point_centroid":[0.50065,0.05874,0.05433],"force_p95":17.53079,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.8243,"mean_force":9.80032,"phase_index":3.0,"phase_name":"push_channel_2","phase_type":"push","tcp_position_centroid":[0.49544,0.06929,0.05507]},{"body_a":"peg","body_b":"channel_base_body","contact_count":524.0,"contact_point_centroid":[0.50306,0.0674,0.00938],"force_p95":0.55075,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.60912,"mean_force":0.57922,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.49819,0.11193,0.10603]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.5025,0.08534,0.05876],"force_p95":17.198,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.198,"mean_force":17.198,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.49867,0.09667,0.05926]},{"body_a":"peg","body_b":"channel_base_body","contact_count":795.0,"contact_point_centroid":[0.5013,0.02813,0.00862],"force_p95":11.8001,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.46366,"mean_force":2.57648,"phase_index":3.0,"phase_name":"push_channel_2","phase_type":"push","tcp_position_centroid":[0.49505,0.01836,0.05456]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":52.0,"contact_point_centroid":[0.52501,0.03319,0.05824],"force_p95":10.25016,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.8215,"mean_force":7.71028,"phase_index":3.0,"phase_name":"push_channel_2","phase_type":"push","tcp_position_centroid":[0.49529,0.06825,0.0549]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":5.0,"contact_point_centroid":[0.47499,0.04305,0.02422],"force_p95":6.75907,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.33871,"mean_force":1.98093,"phase_index":3.0,"phase_name":"push_channel_2","phase_type":"push","tcp_position_centroid":[0.49477,-0.04466,0.05418]},{"body_a":"peg","body_b":"channel_base_body","contact_count":309.0,"contact_point_centroid":[0.50312,0.06752,0.00931],"force_p95":0.67624,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.57447,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.49853,0.1668,0.22787]},{"body_a":"peg","body_b":"channel_base_body","contact_count":333.0,"contact_point_centroid":[0.49637,0.01911,0.00802],"force_p95":0.72553,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.72713,"mean_force":0.60599,"phase_index":4.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.49635,0.05189,0.15466]}],"total_contact_groups":10},"final_pose_error":0.04995,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49839,0.01907,0.0241],"final_tcp_position":[0.49945,0.1661,0.26332],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":20.57186,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":325.0,"n_steps_budget":930.0,"object_pos_end":[0.50307,0.06742,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14758,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54186,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":309.0,"raw_peak_contact_force":2.06903,"subtask_id":"reach_approach","tcp_end":[0.50021,0.12775,0.15642],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13669,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":524.0,"n_steps_budget":1000.0,"object_pos_end":[0.50303,0.06741,0.0338],"object_pos_start":[0.50307,0.06742,0.0338],"object_to_goal_dist_end":0.14757,"object_to_goal_dist_start":0.14758,"object_z_max":0.0338,"peak_contact_force":17.60912,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":525.0,"raw_peak_contact_force":17.60912,"subtask_id":"contact_peg","tcp_end":[0.49868,0.09662,0.05911],"tcp_start":[0.50021,0.12775,0.15642],"tcp_to_object_dist_end":0.0389,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":630.0,"object_pos_end":[0.50295,0.0674,0.03382],"object_pos_start":[0.50303,0.06741,0.0338],"object_to_goal_dist_end":0.14756,"object_to_goal_dist_start":0.14757,"object_z_max":0.03386,"peak_contact_force":0.75433,"phase_name":"push_channel_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":6.0,"raw_peak_contact_force":20.57186,"subtask_id":"push_to_goal","tcp_end":[0.49845,0.09652,0.05876],"tcp_start":[0.49853,0.09655,0.05887],"tcp_to_object_dist_end":0.0386,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":800.0,"n_steps_budget":1000.0,"object_pos_end":[0.49432,0.01902,0.02416],"object_pos_start":[0.50282,0.06736,0.03389],"object_to_goal_dist_end":0.10044,"object_to_goal_dist_start":0.14751,"object_z_max":0.04036,"peak_contact_force":0.72263,"phase_name":"push_channel_2","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1039.0,"raw_peak_contact_force":19.8243,"subtask_id":"push_to_goal","tcp_end":[0.49476,-0.0565,0.05416],"tcp_start":[0.49845,0.09652,0.05876],"tcp_to_object_dist_end":0.08126,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":333.0,"n_steps_budget":1000.0,"object_pos_end":[0.49839,0.01907,0.0241],"object_pos_start":[0.49432,0.01902,0.02416],"object_to_goal_dist_end":0.10035,"object_to_goal_dist_start":0.10044,"object_z_max":0.02417,"peak_contact_force":0.63683,"phase_name":"retract_away","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":333.0,"raw_peak_contact_force":0.72713,"subtask_id":"push_to_goal","tcp_end":[0.49945,0.1661,0.26332],"tcp_start":[0.49476,-0.0565,0.05416],"tcp_to_object_dist_end":0.28079,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `7acce370299b32aeef0e4239da3e97eae076cb9602edead185a6cf774ee0bc4e`; realized-scene SHA-256: `d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51001,0.11178,0.04]},{"name":"goal","value":[0.51001,-0.04822,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.51001,0.11178,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.51001,-0.04822,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.81308,"average_solve_count":107.0,"average_success_count":107.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.06753,"approach_behind.approach_tol":0.03725,"descend_to_peg.descend_force_threshold":4.11883,"descend_to_peg.descend_speed":0.10724,"push_channel_1.push1_distance":0.10811,"push_channel_1.push1_force_limit":20.5681,"push_channel_1.push1_speed":0.06649,"push_channel_1.push1_tol":0.01128,"push_channel_2.push2_distance":0.16973,"push_channel_2.push2_force_limit":23.70991,"push_channel_2.push2_speed":0.08731,"push_channel_2.push2_tol":0.0117,"retract_away.retract_speed":0.19531,"retract_away.retract_tol":0.07344},"optimized_scores":{"best_composite_score":-0.39015,"best_fitness_score":0.19985,"best_task_score":0.00343},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":209.0,"contact_point_centroid":[0.49967,0.11209,0.00953],"force_p95":0.97966,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":43.19399,"mean_force":1.29665,"phase_index":4.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.49916,0.16274,0.1506]},{"body_a":"attachment","body_b":"peg","contact_count":12.0,"contact_point_centroid":[0.50585,0.12927,0.05899],"force_p95":40.35253,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":42.6616,"mean_force":13.36377,"phase_index":4.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.49923,0.13913,0.05953]},{"body_a":"peg","body_b":"channel_base_body","contact_count":5.0,"contact_point_centroid":[0.49284,0.11655,0.00937],"force_p95":32.43796,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":35.38022,"mean_force":16.52029,"phase_index":2.0,"phase_name":"push_channel_1","phase_type":"push","tcp_position_centroid":[0.50048,0.13922,0.05922]},{"body_a":"attachment","body_b":"peg","contact_count":5.0,"contact_point_centroid":[0.50714,0.12935,0.05853],"force_p95":31.85267,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":34.77854,"mean_force":16.09462,"phase_index":2.0,"phase_name":"push_channel_1","phase_type":"push","tcp_position_centroid":[0.50048,0.13922,0.05922]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.48601,0.11511,0.00932],"force_p95":28.24778,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":28.42727,"mean_force":26.43527,"phase_index":3.0,"phase_name":"push_channel_2","phase_type":"push","tcp_position_centroid":[0.50022,0.13901,0.05883]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.50699,0.12925,0.05832],"force_p95":27.75909,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":27.94082,"mean_force":25.92587,"phase_index":3.0,"phase_name":"push_channel_2","phase_type":"push","tcp_position_centroid":[0.50022,0.13901,0.05883]},{"body_a":"peg","body_b":"channel_base_body","contact_count":470.0,"contact_point_centroid":[0.50359,0.11169,0.00942],"force_p95":0.58855,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":26.74933,"mean_force":0.59845,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50216,0.1527,0.10758]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50719,0.12939,0.05881],"force_p95":26.28138,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":26.28138,"mean_force":26.28138,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50066,0.1394,0.0597]},{"body_a":"peg","body_b":"channel_base_body","contact_count":270.0,"contact_point_centroid":[0.50354,0.11158,0.00934],"force_p95":0.70096,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.5733,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50195,0.18399,0.22598]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.49976,0.19975,0.29865]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.525,0.11174,0.05836],"force_p95":0.0,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":4.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.49888,0.15564,0.1225]}],"total_contact_groups":11},"final_pose_error":0.04966,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50334,0.11118,0.0339],"final_tcp_position":[0.50027,0.18856,0.25167],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":43.19399,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":292.0,"n_steps_budget":1000.0,"object_pos_end":[0.50368,0.11178,0.03382],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19192,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.59416,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":286.0,"raw_peak_contact_force":2.06328,"subtask_id":"reach_approach","tcp_end":[0.50602,0.1665,0.15852],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.1362,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":470.0,"n_steps_budget":780.0,"object_pos_end":[0.50374,0.11175,0.03389],"object_pos_start":[0.50368,0.11178,0.03382],"object_to_goal_dist_end":0.19188,"object_to_goal_dist_start":0.19192,"object_z_max":0.034,"peak_contact_force":26.74933,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":471.0,"raw_peak_contact_force":26.74933,"subtask_id":"contact_peg","tcp_end":[0.50065,0.13935,0.05949],"tcp_start":[0.50602,0.1665,0.15852],"tcp_to_object_dist_end":0.03778,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":5.0,"n_steps_budget":1000.0,"object_pos_end":[0.50349,0.11177,0.03386],"object_pos_start":[0.50374,0.11175,0.03389],"object_to_goal_dist_end":0.1919,"object_to_goal_dist_start":0.19188,"object_z_max":0.03389,"peak_contact_force":20.66893,"phase_name":"push_channel_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":10.0,"raw_peak_contact_force":35.38022,"subtask_id":"push_to_goal","tcp_end":[0.50026,0.13905,0.0589],"tcp_start":[0.50032,0.1391,0.05899],"tcp_to_object_dist_end":0.03717,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50341,0.1117,0.03382],"object_pos_start":[0.50343,0.11172,0.03383],"object_to_goal_dist_end":0.19183,"object_to_goal_dist_start":0.19185,"object_z_max":0.03383,"peak_contact_force":28.42727,"phase_name":"push_channel_2","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":6.0,"raw_peak_contact_force":28.42727,"subtask_id":"push_to_goal","tcp_end":[0.50015,0.13897,0.0587],"tcp_start":[0.50018,0.13898,0.05876],"tcp_to_object_dist_end":0.03706,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":210.0,"n_steps_budget":810.0,"object_pos_end":[0.50334,0.11118,0.0339],"object_pos_start":[0.50339,0.11167,0.03381],"object_to_goal_dist_end":0.19131,"object_to_goal_dist_start":0.1918,"object_z_max":0.03776,"peak_contact_force":0.52596,"phase_name":"retract_away","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":222.0,"raw_peak_contact_force":43.19399,"subtask_id":"push_to_goal","tcp_end":[0.50027,0.18856,0.25167],"tcp_start":[0.50015,0.13897,0.0587],"tcp_to_object_dist_end":0.23113,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```