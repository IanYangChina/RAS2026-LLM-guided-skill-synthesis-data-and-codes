## Search State

- **Seed**: 5
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.3589 | 0.80 | ❌ rejected |
| 7 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.5102 | 0.81 | ❌ rejected |
| 6 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 7 | 0.1186 | 0.34 | ❌ rejected |
| 5 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.4067 | 0.80 | ❌ rejected |
| 4 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.4627 | 0.82 | ✅ accepted |

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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.821, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.359) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: pre_push_approach
  anchor: object
  offset:
  - 0.0
  - 0.08
  - 0.0
  weight: 0.3
- id: push_channel
  target_entity: object
  metric: goal_progress
  weight: 0.7
phases:
- id: approach_behind_high
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
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: pre_push_approach
- id: descend_to_lateral
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
    - 0.08
    - 0.0
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.04
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: pre_push_approach
- id: push_along_channel
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.16
      axis: channel_axis
      mode: replace_offset_projection
      sign: positive
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    force_limit:
      type: scalar
      range:
      - 30.0
      - 50.0
      default: 40.0
      binds_to:
      - path: guards.force_safe.threshold
        mode: replace
    lateral_nudge:
      type: scalar
      range:
      - 0.0
      - 0.02
      default: 0.005
      binds_to:
      - path: retry.offset.x
        mode: replace
    push_distance:
      type: scalar
      range:
      - 0.14
      - 0.25
      default: 0.18
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.03
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: force_safe
    when: during_phase
    predicate: force_below
    threshold: 40.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.005
    - 0.0
    - 0.0
  subtask_id: push_channel
- id: retract_upward
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: peg
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.05
    orientation:
      mode: keep_current
  parameters:
    retract_speed:
      type: scalar
      range:
      - 0.03
      - 0.1
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_behind_high** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.08, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_lateral** (`descend`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.08, 0.0], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **push_along_channel** (`push`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.16, mode=replace_offset_projection, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - force_limit: status=consumed; consumers=guards.force_safe.threshold (replace)
    - lateral_nudge: status=consumed; consumers=retry.offset.x (replace)
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_safe, when=during_phase, predicate=force_below, on_failure=retry, threshold=40.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.005, 0.0, 0.0]
- **retract_upward** (`retract`)
  - target: source=yaml, anchor=task_goal, entity=peg, offset=[0.0, 0.0, 0.1], tolerance=0.05
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.359
- **task_score** (E): 0.798
- **fitness_score**: 0.869  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.510

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_behind_high | 1.00 | 1.00 | 0.1575 |
| descend_to_lateral | 1.00 | 1.00 | 0.1120 |
| push_along_channel | 0.00 | 1.00 | 0.0002 |
| retract_upward | 1.00 | 1.00 | 0.0647 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_behind_high | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.525, 0.176, 0.148) | (0.512, 0.095, 0.040)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 1.000 | 0.539 | 2.488 |
| descend_to_lateral | descend | 1.00 / step_budget | (0.525, 0.176, 0.148)→(0.505, 0.173, 0.038) | (0.504, 0.095, 0.034)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 1.000 | 0.557 | 0.588 |
| push_along_channel | push | 0.00 / guard_failure | (0.501, -0.053, 0.030)→(0.501, -0.054, 0.030) | (0.504, 0.095, 0.034)→(0.506, -0.083, 0.036) | 0.175→0.008 | 1.00 / 3.000 | 1.465 | 38.266 |
| retract_upward | retract | 1.00 / step_budget | (0.501, -0.054, 0.030)→(0.498, -0.064, 0.093) | (0.506, -0.083, 0.036)→(0.505, -0.075, 0.070) | 0.008→0.031 | 1.00 / 1.000 | 0.155 | 103.032 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 1.000
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 1.000
- phase_score: 0.934
- phase_breakdown.pre_push_approach_score: 0.889
- phase_breakdown.push_channel_score: 0.953

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.960
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.419
- **K-run variance**: 0.0117
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.312


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.95765,"average_solve_count":307.0,"average_success_count":307.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind_high.approach_lateral_offset":0.00498,"approach_behind_high.approach_speed":0.03551,"descend_to_lateral.descend_lateral_offset":0.00046,"descend_to_lateral.descend_speed":0.02899,"push_along_channel.force_limit":36.88655,"push_along_channel.lateral_nudge":0.01012,"push_along_channel.push_distance":0.19135,"push_along_channel.push_speed":0.05111,"retract_upward.retract_speed":0.08639},"optimized_scores":{"best_composite_score":0.207,"best_fitness_score":0.717,"best_task_score":0.49159},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":87.0,"contact_point_centroid":[0.50092,-0.06695,0.05764],"force_p95":101.50393,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":103.0605,"mean_force":62.78264,"phase_index":3.0,"phase_name":"retract_upward","phase_type":"retract","tcp_position_centroid":[0.49754,-0.056,0.05447]},{"body_a":"peg","body_b":"channel_base_body","contact_count":91.0,"contact_point_centroid":[0.50616,-0.1009,0.06024],"force_p95":101.28413,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":102.9102,"mean_force":60.35697,"phase_index":3.0,"phase_name":"retract_upward","phase_type":"retract","tcp_position_centroid":[0.49755,-0.05632,0.05609]},{"body_a":"peg","body_b":"channel_base_body","contact_count":6.0,"contact_point_centroid":[0.50645,-0.10032,0.06009],"force_p95":39.11103,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":39.18534,"mean_force":25.35326,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50195,-0.05272,0.0296]},{"body_a":"attachment","body_b":"peg","contact_count":358.0,"contact_point_centroid":[0.5047,0.02562,0.04567],"force_p95":24.45244,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":39.11966,"mean_force":5.45492,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50128,0.03739,0.03091]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":218.0,"contact_point_centroid":[0.52516,-0.01547,0.03502],"force_p95":24.78445,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":26.50272,"mean_force":5.13614,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50135,0.01409,0.03054]},{"body_a":"peg","body_b":"channel_base_body","contact_count":306.0,"contact_point_centroid":[0.50516,0.04471,0.00965],"force_p95":13.39526,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":24.64985,"mean_force":3.1449,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50143,0.09264,0.03234]},{"body_a":"peg","body_b":"channel_base_body","contact_count":4.0,"contact_point_centroid":[0.49492,-0.09661,0.00997],"force_p95":14.13832,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.18094,"mean_force":13.38626,"phase_index":3.0,"phase_name":"retract_upward","phase_type":"retract","tcp_position_centroid":[0.50051,-0.05414,0.03021]},{"body_a":"peg","body_b":"channel_base_body","contact_count":503.0,"contact_point_centroid":[0.50554,0.10467,0.00937],"force_p95":0.57751,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.56884,"phase_index":0.0,"phase_name":"approach_behind_high","phase_type":"approach","tcp_position_centroid":[0.51135,0.19179,0.22047]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":3.0,"contact_point_centroid":[0.47496,-0.07233,0.03909],"force_p95":2.34292,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.36606,"mean_force":2.19807,"phase_index":3.0,"phase_name":"retract_upward","phase_type":"retract","tcp_position_centroid":[0.49663,-0.05671,0.07008]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_behind_high","phase_type":"approach","tcp_position_centroid":[0.49994,0.19934,0.29696]},{"body_a":"peg","body_b":"channel_base_body","contact_count":554.0,"contact_point_centroid":[0.50598,0.10456,0.00939],"force_p95":0.5757,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57647,"mean_force":0.54633,"phase_index":1.0,"phase_name":"descend_to_lateral","phase_type":"descend","tcp_position_centroid":[0.51291,0.18364,0.09208]}],"total_contact_groups":11},"final_pose_error":0.04927,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5052,-0.07492,0.07028],"final_tcp_position":[0.49767,-0.06404,0.09344],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":103.0605,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":530.0,"n_steps_budget":1000.0,"object_pos_end":[0.50597,0.10471,0.03383],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18491,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.57517,"phase_name":"approach_behind_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":535.0,"raw_peak_contact_force":3.33087,"subtask_id":"pre_push_approach","tcp_end":[0.52389,0.18486,0.14806],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14068,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":554.0,"n_steps_budget":1000.0,"object_pos_end":[0.50582,0.10463,0.03384],"object_pos_start":[0.50597,0.10471,0.03383],"object_to_goal_dist_end":0.18482,"object_to_goal_dist_start":0.18491,"object_z_max":0.03384,"peak_contact_force":0.55011,"phase_name":"descend_to_lateral","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":554.0,"raw_peak_contact_force":0.57647,"subtask_id":"pre_push_approach","tcp_end":[0.50403,0.18335,0.0379],"tcp_start":[0.52389,0.18486,0.14806],"tcp_to_object_dist_end":0.07885,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":612.0,"n_steps_budget":1000.0,"object_pos_end":[0.50649,-0.08268,0.03542],"object_pos_start":[0.50582,0.10463,0.03384],"object_to_goal_dist_end":0.00838,"object_to_goal_dist_start":0.18482,"object_z_max":0.03776,"peak_contact_force":0.14288,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":888.0,"raw_peak_contact_force":39.18534,"subtask_id":"push_channel","tcp_end":[0.50187,-0.05358,0.02949],"tcp_start":[0.50192,-0.05343,0.02955],"tcp_to_object_dist_end":0.03006,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":91.0,"n_steps_budget":840.0,"object_pos_end":[0.5052,-0.07492,0.07028],"object_pos_start":[0.50637,-0.08314,0.03539],"object_to_goal_dist_end":0.03114,"object_to_goal_dist_start":0.00847,"object_z_max":0.06983,"peak_contact_force":0.15355,"phase_name":"retract_upward","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":185.0,"raw_peak_contact_force":103.0605,"tcp_end":[0.49767,-0.06404,0.09344],"tcp_start":[0.50187,-0.05358,0.02949],"tcp_to_object_dist_end":0.02667,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.67127,"average_solve_count":362.0,"average_success_count":362.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind_high.approach_lateral_offset":0.03903,"approach_behind_high.approach_speed":0.0202,"descend_to_lateral.descend_lateral_offset":0.00582,"descend_to_lateral.descend_speed":0.02096,"push_along_channel.force_limit":31.33216,"push_along_channel.lateral_nudge":0.0119,"push_along_channel.push_distance":0.18331,"push_along_channel.push_speed":0.04793,"retract_upward.retract_speed":0.06714},"optimized_scores":{"best_composite_score":0.41945,"best_fitness_score":0.92945,"best_task_score":0.90259},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":87.0,"contact_point_centroid":[0.49896,-0.06643,0.0559],"force_p95":101.33574,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":102.48621,"mean_force":64.14391,"phase_index":3.0,"phase_name":"retract_upward","phase_type":"retract","tcp_position_centroid":[0.49715,-0.05524,0.05465]},{"body_a":"peg","body_b":"channel_base_body","contact_count":91.0,"contact_point_centroid":[0.50038,-0.10078,0.06397],"force_p95":101.1562,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":102.37458,"mean_force":61.37209,"phase_index":3.0,"phase_name":"retract_upward","phase_type":"retract","tcp_position_centroid":[0.49718,-0.05557,0.05626]},{"body_a":"attachment","body_b":"peg","contact_count":256.0,"contact_point_centroid":[0.50414,0.01116,0.0413],"force_p95":13.1448,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":36.35535,"mean_force":2.57721,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50171,0.02273,0.03153]},{"body_a":"peg","body_b":"channel_base_body","contact_count":294.0,"contact_point_centroid":[0.50409,0.01874,0.00949],"force_p95":8.6969,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":30.36983,"mean_force":2.10015,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.5029,0.06643,0.0329]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.50024,-0.10042,0.06075],"force_p95":27.50714,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.73113,"mean_force":18.65946,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50047,-0.05255,0.03021]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":116.0,"contact_point_centroid":[0.52514,0.0181,0.02887],"force_p95":16.76102,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.94501,"mean_force":2.14609,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50209,0.04788,0.03193]},{"body_a":"peg","body_b":"channel_base_body","contact_count":8.0,"contact_point_centroid":[0.48902,-0.08662,0.00976],"force_p95":8.8687,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.34257,"mean_force":5.59204,"phase_index":3.0,"phase_name":"retract_upward","phase_type":"retract","tcp_position_centroid":[0.50004,-0.05331,0.03012]},{"body_a":"peg","body_b":"channel_base_body","contact_count":578.0,"contact_point_centroid":[0.50305,0.0675,0.00934],"force_p95":0.5553,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.56153,"phase_index":0.0,"phase_name":"approach_behind_high","phase_type":"approach","tcp_position_centroid":[0.51706,0.17477,0.2211]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":3.0,"contact_point_centroid":[0.47496,-0.07197,0.03618],"force_p95":1.51124,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.55315,"mean_force":1.26117,"phase_index":3.0,"phase_name":"retract_upward","phase_type":"retract","tcp_position_centroid":[0.49647,-0.05553,0.06771]},{"body_a":"peg","body_b":"channel_base_body","contact_count":546.0,"contact_point_centroid":[0.50303,0.06737,0.00938],"force_p95":0.55059,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55089,"mean_force":0.54664,"phase_index":1.0,"phase_name":"descend_to_lateral","phase_type":"descend","tcp_position_centroid":[0.52068,0.14829,0.0921]}],"total_contact_groups":10},"final_pose_error":0.04944,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50133,-0.07695,0.07149],"final_tcp_position":[0.49788,-0.06345,0.09346],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":102.48621,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":594.0,"n_steps_budget":1000.0,"object_pos_end":[0.50309,0.06745,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14762,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54397,"phase_name":"approach_behind_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":578.0,"raw_peak_contact_force":2.06903,"subtask_id":"pre_push_approach","tcp_end":[0.53573,0.15065,0.1468],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14407,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":546.0,"n_steps_budget":1000.0,"object_pos_end":[0.50303,0.0675,0.0338],"object_pos_start":[0.50309,0.06745,0.0338],"object_to_goal_dist_end":0.14766,"object_to_goal_dist_start":0.14762,"object_z_max":0.0338,"peak_contact_force":0.54563,"phase_name":"descend_to_lateral","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":546.0,"raw_peak_contact_force":0.55089,"subtask_id":"pre_push_approach","tcp_end":[0.50735,0.14662,0.0384],"tcp_start":[0.53573,0.15065,0.1468],"tcp_to_object_dist_end":0.07937,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":512.0,"n_steps_budget":1000.0,"object_pos_end":[0.50348,-0.08224,0.03643],"object_pos_start":[0.50303,0.0675,0.0338],"object_to_goal_dist_end":0.00547,"object_to_goal_dist_start":0.14766,"object_z_max":0.03943,"peak_contact_force":2.98467,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":669.0,"raw_peak_contact_force":36.35535,"subtask_id":"push_channel","tcp_end":[0.50042,-0.05302,0.03015],"tcp_start":[0.50046,-0.05283,0.03019],"tcp_to_object_dist_end":0.03004,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":91.0,"n_steps_budget":1000.0,"object_pos_end":[0.50133,-0.07695,0.07149],"object_pos_start":[0.50352,-0.08282,0.03639],"object_to_goal_dist_end":0.03166,"object_to_goal_dist_start":0.00578,"object_z_max":0.07108,"peak_contact_force":0.16186,"phase_name":"retract_upward","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":189.0,"raw_peak_contact_force":102.48621,"tcp_end":[0.49788,-0.06345,0.09346],"tcp_start":[0.50042,-0.05302,0.03015],"tcp_to_object_dist_end":0.02602,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.00704,"average_solve_count":284.0,"average_success_count":284.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind_high.approach_lateral_offset":0.00907,"approach_behind_high.approach_speed":0.04658,"descend_to_lateral.descend_lateral_offset":0.00478,"descend_to_lateral.descend_speed":0.03019,"push_along_channel.force_limit":37.31578,"push_along_channel.lateral_nudge":0.0048,"push_along_channel.push_distance":0.19002,"push_along_channel.push_speed":0.05276,"retract_upward.retract_speed":0.07382},"optimized_scores":{"best_composite_score":0.45021,"best_fitness_score":0.96021,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":83.0,"contact_point_centroid":[0.5012,-0.06719,0.05909],"force_p95":102.15026,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":103.54793,"mean_force":62.94541,"phase_index":3.0,"phase_name":"retract_upward","phase_type":"retract","tcp_position_centroid":[0.49659,-0.05657,0.05479]},{"body_a":"peg","body_b":"channel_base_body","contact_count":90.0,"contact_point_centroid":[0.50809,-0.10103,0.06051],"force_p95":101.77241,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":103.25763,"mean_force":58.91748,"phase_index":3.0,"phase_name":"retract_upward","phase_type":"retract","tcp_position_centroid":[0.49667,-0.05692,0.05622]},{"body_a":"peg","body_b":"channel_base_body","contact_count":9.0,"contact_point_centroid":[0.50666,-0.10052,0.04936],"force_p95":31.51692,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":39.2561,"mean_force":11.137,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50015,-0.05262,0.0294]},{"body_a":"attachment","body_b":"peg","contact_count":325.0,"contact_point_centroid":[0.50333,0.02971,0.03848],"force_p95":7.06499,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":38.71512,"mean_force":1.97968,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50074,0.04132,0.03061]},{"body_a":"peg","body_b":"channel_base_body","contact_count":14.0,"contact_point_centroid":[0.50092,-0.08836,0.00981],"force_p95":19.09485,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.25359,"mean_force":8.55658,"phase_index":3.0,"phase_name":"retract_upward","phase_type":"retract","tcp_position_centroid":[0.49915,-0.05465,0.02991]},{"body_a":"peg","body_b":"channel_base_body","contact_count":354.0,"contact_point_centroid":[0.50463,0.04199,0.00965],"force_p95":5.89429,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.87739,"mean_force":1.93863,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50137,0.0882,0.03167]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":18.0,"contact_point_centroid":[0.52506,-0.08409,0.04054],"force_p95":15.65693,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.22515,"mean_force":5.95733,"phase_index":3.0,"phase_name":"retract_upward","phase_type":"retract","tcp_position_centroid":[0.49758,-0.05522,0.04396]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":121.0,"contact_point_centroid":[0.52526,-0.01467,0.03825],"force_p95":3.20422,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.02081,"mean_force":0.99582,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50059,0.01527,0.0303]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":4.0,"contact_point_centroid":[0.47481,-0.07253,0.03974],"force_p95":4.09798,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.14947,"mean_force":3.44801,"phase_index":3.0,"phase_name":"retract_upward","phase_type":"retract","tcp_position_centroid":[0.49584,-0.05736,0.07037]},{"body_a":"peg","body_b":"channel_base_body","contact_count":489.0,"contact_point_centroid":[0.50361,0.11165,0.00937],"force_p95":0.61228,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.56003,"phase_index":0.0,"phase_name":"approach_behind_high","phase_type":"approach","tcp_position_centroid":[0.5065,0.19515,0.2214]},{"body_a":"peg","body_b":"channel_base_body","contact_count":594.0,"contact_point_centroid":[0.50368,0.1117,0.0094],"force_p95":0.60995,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63527,"mean_force":0.54458,"phase_index":1.0,"phase_name":"descend_to_lateral","phase_type":"descend","tcp_position_centroid":[0.50855,0.19036,0.09163]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_behind_high","phase_type":"approach","tcp_position_centroid":[0.49983,0.19958,0.2991]}],"total_contact_groups":12},"final_pose_error":0.04935,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50705,-0.07338,0.06939],"final_tcp_position":[0.49719,-0.06445,0.09324],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":103.54793,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":511.0,"n_steps_budget":1000.0,"object_pos_end":[0.50372,0.11175,0.03384],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19189,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.49901,"phase_name":"approach_behind_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":505.0,"raw_peak_contact_force":2.06328,"subtask_id":"pre_push_approach","tcp_end":[0.51445,0.19139,0.14877],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14024,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":594.0,"n_steps_budget":1000.0,"object_pos_end":[0.50369,0.11171,0.03383],"object_pos_start":[0.50372,0.11175,0.03384],"object_to_goal_dist_end":0.19185,"object_to_goal_dist_start":0.19189,"object_z_max":0.034,"peak_contact_force":0.57581,"phase_name":"descend_to_lateral","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":594.0,"raw_peak_contact_force":0.63527,"subtask_id":"pre_push_approach","tcp_end":[0.50509,0.1903,0.03718],"tcp_start":[0.51445,0.19139,0.14877],"tcp_to_object_dist_end":0.07867,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":621.0,"n_steps_budget":1000.0,"object_pos_end":[0.50698,-0.08353,0.03537],"object_pos_start":[0.50369,0.11171,0.03383],"object_to_goal_dist_end":0.00909,"object_to_goal_dist_start":0.19185,"object_z_max":0.03805,"peak_contact_force":1.26647,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":809.0,"raw_peak_contact_force":39.2561,"subtask_id":"push_channel","tcp_end":[0.50005,-0.05415,0.02929],"tcp_start":[0.50009,-0.05396,0.02933],"tcp_to_object_dist_end":0.03079,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":90.0,"n_steps_budget":960.0,"object_pos_end":[0.50705,-0.07338,0.06939],"object_pos_start":[0.5071,-0.08395,0.03498],"object_to_goal_dist_end":0.03094,"object_to_goal_dist_start":0.00955,"object_z_max":0.06892,"peak_contact_force":0.14852,"phase_name":"retract_upward","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":209.0,"raw_peak_contact_force":103.54793,"tcp_end":[0.49719,-0.06445,0.09324],"tcp_start":[0.50005,-0.05415,0.02929],"tcp_to_object_dist_end":0.02731,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```