## Search State

- **Seed**: 5
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → descend → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 7 | -0.0113 | 0.03 | ❌ rejected |
| 3 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.2857 | 0.47 | ✅ accepted |
| 2 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.0451 | 0.00 | ❌ rejected |
| 1 | approach → approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 9 | -0.2084 | 0.00 | ❌ rejected |
| 0 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.1666 | 0.22 | ✅ accepted |

**Proposal policy**: task_score is 0.03 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.011) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: approach_peg
  anchor: object
  offset:
  - 0.0
  - 0.03
  - 0.06
  weight: 0.3
- id: descend_peg
  anchor: object
  offset:
  - 0.0
  - 0.015
  - 0.0
  weight: 0.2
- id: push_to_goal
  metric: goal_progress
  weight: 0.5
phases:
- id: approach_above
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
    - 0.06
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_peg
- id: descend_to_peg
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
    - 0.015
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: descend_peg
- id: push_channel
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
      distance: 0.18
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    tolerance: 0.015
    orientation:
      mode: keep_current
  parameters:
    insert_depth:
      type: scalar
      range:
      - 0.16
      - 0.2
      default: 0.18
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
  - id: force_guard
    when: during_phase
    predicate: force_below
    threshold: 35.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: reduce_speed
  subtask_id: push_to_goal
- id: retract_home
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
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_above** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.03, 0.06], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_peg** (`descend`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.015, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **push_channel** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.18, mode=add_to_offset, sign=positive}, tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - insert_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_guard, when=during_phase, predicate=force_below, on_failure=retry, threshold=35.0
  - retries: max_attempts=2, strategy=reduce_speed
- **retract_home** (`retract`)
  - target: source=yaml, anchor=world, offset=[0.5, 0.2, 0.3], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: -0.011
- **task_score** (E): 0.032
- **fitness_score**: 0.229  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.440

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above | 1.00 | 1.00 | 0.1958 |
| descend_to_contact | 1.00 | 1.00 | 0.0624 |
| align_lateral | 1.00 | 1.00 | 0.0177 |
| push_channel | 0.00 | 1.00 | 0.0000 |
| retract_home | 1.00 | 1.00 | 0.2515 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.508, 0.132, 0.117) | (0.512, 0.095, 0.040)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 1.000 | 0.540 | 2.488 |
| descend_to_contact | descend | 1.00 / force_exceeded | (0.508, 0.132, 0.117)→(0.501, 0.109, 0.060) | (0.504, 0.095, 0.034)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 2.000 | 20.017 | 20.017 |
| align_lateral | align | 1.00 / step_budget | (0.501, 0.109, 0.060)→(0.512, 0.101, 0.048) | (0.504, 0.095, 0.034)→(0.503, 0.089, 0.031) | 0.175→0.169 | 1.00 / 3.000 | 207.493 | 258.771 |
| push_channel | push | 0.00 / guard_failure | (0.512, 0.101, 0.049)→(0.512, 0.101, 0.049) | (0.503, 0.089, 0.031)→(0.503, 0.089, 0.031) | 0.169→0.169 | 1.00 / 3.000 | 177.299 | 177.299 |
| retract_home | retract | 1.00 / step_budget | (0.512, 0.101, 0.049)→(0.499, 0.194, 0.281) | (0.503, 0.089, 0.031)→(0.500, 0.088, 0.034) | 0.169→0.168 | 1.00 / 1.000 | 0.547 | 178.495 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.054
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.052
- phase_score: 0.378
- phase_breakdown.approach_peg_score: 0.675
- phase_breakdown.push_to_goal_score: 0.000
- phase_breakdown.descend_peg_score: 0.878

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.248
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.052
- **Median Q (composite search score)**: -0.009
- **K-run variance**: 0.0003
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.219


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.39286,"average_solve_count":196.0,"average_success_count":196.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_lateral.align_speed":0.03776,"approach_above.speed":0.07674,"descend_to_contact.contact_force":13.74967,"descend_to_contact.descend_speed":0.02763,"push_channel.insert_depth":0.19598,"push_channel.push_speed":0.02478,"retract_home.speed":0.08423},"optimized_scores":{"best_composite_score":-0.03265,"best_fitness_score":0.20735,"best_task_score":0.01407},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":154.0,"contact_point_centroid":[0.52508,0.11218,0.05999],"force_p95":243.88145,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":314.67045,"mean_force":195.3374,"phase_index":2.0,"phase_name":"align_lateral","phase_type":"align","tcp_position_centroid":[0.51177,0.11228,0.04969]},{"body_a":"peg","body_b":"channel_base_body","contact_count":301.0,"contact_point_centroid":[0.5205,0.10924,0.00791],"force_p95":183.68443,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":184.50228,"mean_force":152.32167,"phase_index":2.0,"phase_name":"align_lateral","phase_type":"align","tcp_position_centroid":[0.50989,0.11362,0.05168]},{"body_a":"attachment","body_b":"peg","contact_count":301.0,"contact_point_centroid":[0.52131,0.11071,0.05298],"force_p95":183.20628,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":184.01239,"mean_force":152.18512,"phase_index":2.0,"phase_name":"align_lateral","phase_type":"align","tcp_position_centroid":[0.50989,0.11362,0.05168]},{"body_a":"peg","body_b":"channel_base_body","contact_count":769.0,"contact_point_centroid":[0.50141,0.10006,0.0094],"force_p95":0.65321,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":172.73998,"mean_force":1.85552,"phase_index":4.0,"phase_name":"retract_home","phase_type":"retract","tcp_position_centroid":[0.50354,0.15369,0.16494]},{"body_a":"attachment","body_b":"peg","contact_count":42.0,"contact_point_centroid":[0.52004,0.1067,0.05546],"force_p95":89.16252,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":172.24758,"mean_force":24.09561,"phase_index":4.0,"phase_name":"retract_home","phase_type":"retract","tcp_position_centroid":[0.51073,0.11421,0.05465]},{"body_a":"peg","body_b":"channel_base_body","contact_count":4.0,"contact_point_centroid":[0.5188,0.10439,0.00756],"force_p95":171.08683,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":171.41636,"mean_force":166.31925,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51164,0.11228,0.04898]},{"body_a":"attachment","body_b":"peg","contact_count":4.0,"contact_point_centroid":[0.52129,0.10496,0.05141],"force_p95":170.58931,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":170.91983,"mean_force":165.81369,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51164,0.11228,0.04898]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":5.0,"contact_point_centroid":[0.52503,0.11226,0.06],"force_p95":72.15497,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":83.30086,"mean_force":22.17445,"phase_index":4.0,"phase_name":"retract_home","phase_type":"retract","tcp_position_centroid":[0.51162,0.11237,0.04914]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":4.0,"contact_point_centroid":[0.52505,0.11217,0.05999],"force_p95":80.42405,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":80.95121,"mean_force":73.06356,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51164,0.11228,0.04898]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":146.0,"contact_point_centroid":[0.52519,0.10258,0.05449],"force_p95":18.80119,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":32.99985,"mean_force":7.68384,"phase_index":2.0,"phase_name":"align_lateral","phase_type":"align","tcp_position_centroid":[0.50919,0.11402,0.05233]},{"body_a":"peg","body_b":"channel_base_body","contact_count":315.0,"contact_point_centroid":[0.50606,0.10464,0.00939],"force_p95":0.57557,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.56836,"mean_force":0.6162,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.51062,0.12996,0.08795]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51646,0.11815,0.05878],"force_p95":22.06308,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.06308,"mean_force":22.06308,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.50461,0.11867,0.06049]},{"body_a":"peg","body_b":"channel_base_body","contact_count":348.0,"contact_point_centroid":[0.50541,0.10472,0.00936],"force_p95":0.59383,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.57887,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.50921,0.16909,0.20336]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.50025,0.19826,0.29496]}],"total_contact_groups":14},"final_pose_error":0.01992,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50115,0.09903,0.03406],"final_tcp_position":[0.49879,0.19445,0.28091],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":314.67045,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":375.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.10468,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18488,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.54412,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":380.0,"raw_peak_contact_force":3.33087,"subtask_id":"approach_peg","tcp_end":[0.51871,0.14124,0.11755],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09224,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":315.0,"n_steps_budget":1000.0,"object_pos_end":[0.50597,0.10457,0.03384],"object_pos_start":[0.50599,0.10468,0.03384],"object_to_goal_dist_end":0.18477,"object_to_goal_dist_start":0.18488,"object_z_max":0.03384,"peak_contact_force":22.56836,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":316.0,"raw_peak_contact_force":22.56836,"subtask_id":"descend_peg","tcp_end":[0.50457,0.11861,0.06033],"tcp_start":[0.51871,0.14124,0.11755],"tcp_to_object_dist_end":0.03001,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":301.0,"n_steps_budget":600.0,"object_pos_end":[0.50364,0.09991,0.03152],"object_pos_start":[0.50597,0.10457,0.03384],"object_to_goal_dist_end":0.18015,"object_to_goal_dist_start":0.18477,"object_z_max":0.03384,"peak_contact_force":237.31015,"phase_name":"align_lateral","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":902.0,"raw_peak_contact_force":314.67045,"tcp_end":[0.51164,0.11226,0.04897],"tcp_start":[0.50457,0.11861,0.06033],"tcp_to_object_dist_end":0.02282,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":4.0,"n_steps_budget":1000.0,"object_pos_end":[0.5036,0.09991,0.03153],"object_pos_start":[0.50364,0.09991,0.03152],"object_to_goal_dist_end":0.18014,"object_to_goal_dist_start":0.18015,"object_z_max":0.03155,"peak_contact_force":171.41636,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":12.0,"raw_peak_contact_force":171.41636,"subtask_id":"push_to_goal","tcp_end":[0.51164,0.11233,0.04903],"tcp_start":[0.51164,0.1123,0.04901],"tcp_to_object_dist_end":0.02292,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":769.0,"n_steps_budget":1000.0,"object_pos_end":[0.50115,0.09903,0.03406],"object_pos_start":[0.50349,0.09991,0.03156],"object_to_goal_dist_end":0.17913,"object_to_goal_dist_start":0.18014,"object_z_max":0.0355,"peak_contact_force":0.54882,"phase_name":"retract_home","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":816.0,"raw_peak_contact_force":172.73998,"tcp_end":[0.49879,0.19445,0.28091],"tcp_start":[0.51164,0.11233,0.04903],"tcp_to_object_dist_end":0.26466,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.68,"average_solve_count":350.0,"average_success_count":350.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_lateral.align_speed":0.01542,"approach_above.speed":0.02724,"descend_to_contact.contact_force":8.178,"descend_to_contact.descend_speed":0.02023,"push_channel.insert_depth":0.18012,"push_channel.push_speed":0.02473,"retract_home.speed":0.0452},"optimized_scores":{"best_composite_score":0.00783,"best_fitness_score":0.24783,"best_task_score":0.05249},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":506.0,"contact_point_centroid":[0.51938,0.07103,0.05225],"force_p95":194.21882,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":197.13438,"mean_force":163.89719,"phase_index":2.0,"phase_name":"align_lateral","phase_type":"align","tcp_position_centroid":[0.5084,0.07456,0.05054]},{"body_a":"peg","body_b":"channel_base_body","contact_count":506.0,"contact_point_centroid":[0.51935,0.07023,0.00767],"force_p95":194.708,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":195.40838,"mean_force":164.54135,"phase_index":2.0,"phase_name":"align_lateral","phase_type":"align","tcp_position_centroid":[0.5084,0.07456,0.05054]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":207.0,"contact_point_centroid":[0.52503,0.07249,0.06],"force_p95":159.38059,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":184.52211,"mean_force":116.42302,"phase_index":2.0,"phase_name":"align_lateral","phase_type":"align","tcp_position_centroid":[0.51164,0.07263,0.04861]},{"body_a":"peg","body_b":"channel_base_body","contact_count":859.0,"contact_point_centroid":[0.49811,0.06058,0.00943],"force_p95":0.73617,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":184.20413,"mean_force":2.62887,"phase_index":4.0,"phase_name":"retract_home","phase_type":"retract","tcp_position_centroid":[0.50361,0.13348,0.16506]},{"body_a":"attachment","body_b":"peg","contact_count":50.0,"contact_point_centroid":[0.51805,0.06596,0.05527],"force_p95":133.80817,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":183.7036,"mean_force":35.95013,"phase_index":4.0,"phase_name":"retract_home","phase_type":"retract","tcp_position_centroid":[0.51097,0.07562,0.05405]},{"body_a":"peg","body_b":"channel_base_body","contact_count":4.0,"contact_point_centroid":[0.51628,0.06255,0.00741],"force_p95":182.7519,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":183.06034,"mean_force":177.51935,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51156,0.07259,0.04791]},{"body_a":"attachment","body_b":"peg","contact_count":4.0,"contact_point_centroid":[0.51882,0.06287,0.0509],"force_p95":182.24829,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":182.55728,"mean_force":177.01213,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51156,0.07259,0.04791]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":5.0,"contact_point_centroid":[0.52502,0.07252,0.06],"force_p95":86.04551,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":91.04303,"mean_force":50.2508,"phase_index":4.0,"phase_name":"retract_home","phase_type":"retract","tcp_position_centroid":[0.51155,0.07266,0.04804]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":4.0,"contact_point_centroid":[0.52503,0.07245,0.06],"force_p95":88.50608,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":88.98562,"mean_force":81.426,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51156,0.07259,0.04791]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":184.0,"contact_point_centroid":[0.5251,0.06284,0.05447],"force_p95":12.01894,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":31.92805,"mean_force":4.67143,"phase_index":2.0,"phase_name":"align_lateral","phase_type":"align","tcp_position_centroid":[0.50994,0.0734,0.04974]},{"body_a":"peg","body_b":"channel_base_body","contact_count":413.0,"contact_point_centroid":[0.50309,0.06744,0.00938],"force_p95":0.5506,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.0146,"mean_force":0.57684,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.49802,0.09477,0.08665]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51062,0.08193,0.05878],"force_p95":12.56983,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.56983,"mean_force":12.56983,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.49876,0.0824,0.06051]},{"body_a":"peg","body_b":"channel_base_body","contact_count":404.0,"contact_point_centroid":[0.503,0.06741,0.00932],"force_p95":0.5828,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.56794,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.49932,0.15328,0.20592]}],"total_contact_groups":13},"final_pose_error":0.01975,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49762,0.05888,0.03458],"final_tcp_position":[0.49884,0.19273,0.28168],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":197.13438,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":420.0,"n_steps_budget":1000.0,"object_pos_end":[0.50304,0.0675,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14766,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54516,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":404.0,"raw_peak_contact_force":2.06903,"subtask_id":"approach_peg","tcp_end":[0.49993,0.10773,0.11648],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09201,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":413.0,"n_steps_budget":1000.0,"object_pos_end":[0.50301,0.06747,0.0338],"object_pos_start":[0.50304,0.0675,0.0338],"object_to_goal_dist_end":0.14763,"object_to_goal_dist_start":0.14766,"object_z_max":0.0338,"peak_contact_force":13.0146,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":414.0,"raw_peak_contact_force":13.0146,"subtask_id":"descend_peg","tcp_end":[0.49877,0.08235,0.06039],"tcp_start":[0.49993,0.10773,0.11648],"tcp_to_object_dist_end":0.03077,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":506.0,"n_steps_budget":1000.0,"object_pos_end":[0.5011,0.06008,0.03147],"object_pos_start":[0.50301,0.06747,0.0338],"object_to_goal_dist_end":0.14034,"object_to_goal_dist_start":0.14763,"object_z_max":0.03392,"peak_contact_force":195.40838,"phase_name":"align_lateral","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1403.0,"raw_peak_contact_force":197.13438,"tcp_end":[0.51156,0.07258,0.0479],"tcp_start":[0.49877,0.08235,0.06039],"tcp_to_object_dist_end":0.02315,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":4.0,"n_steps_budget":1000.0,"object_pos_end":[0.50105,0.06007,0.03147],"object_pos_start":[0.5011,0.06008,0.03147],"object_to_goal_dist_end":0.14034,"object_to_goal_dist_start":0.14034,"object_z_max":0.03148,"peak_contact_force":183.06034,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":12.0,"raw_peak_contact_force":183.06034,"subtask_id":"push_to_goal","tcp_end":[0.51156,0.07262,0.04796],"tcp_start":[0.51156,0.07261,0.04794],"tcp_to_object_dist_end":0.02323,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":859.0,"n_steps_budget":1000.0,"object_pos_end":[0.49762,0.05888,0.03458],"object_pos_start":[0.50091,0.06007,0.03149],"object_to_goal_dist_end":0.13901,"object_to_goal_dist_start":0.14033,"object_z_max":0.03628,"peak_contact_force":0.53691,"phase_name":"retract_home","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":914.0,"raw_peak_contact_force":184.20413,"tcp_end":[0.49884,0.19273,0.28168],"tcp_start":[0.51156,0.07262,0.04796],"tcp_to_object_dist_end":0.28102,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.97925,"average_solve_count":241.0,"average_success_count":241.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_lateral.align_speed":0.02405,"approach_above.speed":0.05269,"descend_to_contact.contact_force":8.26806,"descend_to_contact.descend_speed":0.02571,"push_channel.insert_depth":0.16787,"push_channel.push_speed":0.03411,"retract_home.speed":0.06983},"optimized_scores":{"best_composite_score":-0.00898,"best_fitness_score":0.23102,"best_task_score":0.03021},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":133.0,"contact_point_centroid":[0.52508,0.11753,0.05999],"force_p95":186.26488,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":264.50752,"mean_force":138.69534,"phase_index":2.0,"phase_name":"align_lateral","phase_type":"align","tcp_position_centroid":[0.51178,0.11765,0.04911]},{"body_a":"peg","body_b":"channel_base_body","contact_count":370.0,"contact_point_centroid":[0.52001,0.1159,0.0078],"force_p95":188.63963,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":189.75934,"mean_force":157.95019,"phase_index":2.0,"phase_name":"align_lateral","phase_type":"align","tcp_position_centroid":[0.50834,0.11955,0.05124]},{"body_a":"attachment","body_b":"peg","contact_count":370.0,"contact_point_centroid":[0.51979,0.11678,0.05269],"force_p95":188.1505,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":189.26873,"mean_force":157.332,"phase_index":2.0,"phase_name":"align_lateral","phase_type":"align","tcp_position_centroid":[0.50834,0.11955,0.05124]},{"body_a":"peg","body_b":"channel_base_body","contact_count":782.0,"contact_point_centroid":[0.50196,0.10662,0.00935],"force_p95":0.65346,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":178.54009,"mean_force":2.10923,"phase_index":4.0,"phase_name":"retract_home","phase_type":"retract","tcp_position_centroid":[0.5036,0.15653,0.16489]},{"body_a":"attachment","body_b":"peg","contact_count":43.0,"contact_point_centroid":[0.5203,0.11215,0.05517],"force_p95":104.7841,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":178.04514,"mean_force":28.4962,"phase_index":4.0,"phase_name":"retract_home","phase_type":"retract","tcp_position_centroid":[0.5108,0.11945,0.0542]},{"body_a":"peg","body_b":"channel_base_body","contact_count":4.0,"contact_point_centroid":[0.51935,0.11025,0.00749],"force_p95":177.13709,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":177.42002,"mean_force":173.08976,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51167,0.11767,0.04861]},{"body_a":"attachment","body_b":"peg","contact_count":4.0,"contact_point_centroid":[0.52152,0.11062,0.05116],"force_p95":176.63783,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":176.92159,"mean_force":172.58192,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51167,0.11767,0.04861]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":4.0,"contact_point_centroid":[0.52503,0.11763,0.06],"force_p95":82.11429,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":88.04296,"mean_force":42.01669,"phase_index":4.0,"phase_name":"retract_home","phase_type":"retract","tcp_position_centroid":[0.51164,0.11775,0.0487]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":4.0,"contact_point_centroid":[0.52505,0.11755,0.05999],"force_p95":85.72161,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":86.14967,"mean_force":80.03644,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51167,0.11767,0.04861]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":135.0,"contact_point_centroid":[0.52516,0.10855,0.05512],"force_p95":19.60518,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.9132,"mean_force":4.64887,"phase_index":2.0,"phase_name":"align_lateral","phase_type":"align","tcp_position_centroid":[0.51011,0.1183,0.05004]},{"body_a":"peg","body_b":"channel_base_body","contact_count":348.0,"contact_point_centroid":[0.50377,0.11172,0.00941],"force_p95":0.59253,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":24.46791,"mean_force":0.61237,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.50202,0.13647,0.08806]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.5123,0.12502,0.05876],"force_p95":23.9367,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.9367,"mean_force":23.9367,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.50043,0.12551,0.06046]},{"body_a":"peg","body_b":"channel_base_body","contact_count":357.0,"contact_point_centroid":[0.50348,0.11163,0.00936],"force_p95":0.62843,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.56609,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.50251,0.17288,0.20529]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.49983,0.19935,0.29883]}],"total_contact_groups":14},"final_pose_error":0.01977,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50133,0.10597,0.03383],"final_tcp_position":[0.49881,0.19477,0.28097],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":264.50752,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":379.0,"n_steps_budget":1000.0,"object_pos_end":[0.50371,0.11181,0.0339],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19194,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.52944,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":373.0,"raw_peak_contact_force":2.06328,"subtask_id":"approach_peg","tcp_end":[0.50607,0.14774,0.11844],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.0919,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":348.0,"n_steps_budget":1000.0,"object_pos_end":[0.50374,0.11177,0.03383],"object_pos_start":[0.50371,0.11181,0.0339],"object_to_goal_dist_end":0.19191,"object_to_goal_dist_start":0.19194,"object_z_max":0.03397,"peak_contact_force":24.46791,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":349.0,"raw_peak_contact_force":24.46791,"subtask_id":"descend_peg","tcp_end":[0.50043,0.12545,0.06032],"tcp_start":[0.50607,0.14774,0.11844],"tcp_to_object_dist_end":0.03,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":370.0,"n_steps_budget":780.0,"object_pos_end":[0.50385,0.10631,0.03125],"object_pos_start":[0.50374,0.11177,0.03383],"object_to_goal_dist_end":0.18655,"object_to_goal_dist_start":0.19191,"object_z_max":0.03383,"peak_contact_force":189.75934,"phase_name":"align_lateral","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1008.0,"raw_peak_contact_force":264.50752,"tcp_end":[0.51168,0.11765,0.04859],"tcp_start":[0.50043,0.12545,0.06032],"tcp_to_object_dist_end":0.02215,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":4.0,"n_steps_budget":1000.0,"object_pos_end":[0.50381,0.1063,0.03126],"object_pos_start":[0.50385,0.10631,0.03125],"object_to_goal_dist_end":0.18655,"object_to_goal_dist_start":0.18655,"object_z_max":0.03128,"peak_contact_force":177.42002,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":12.0,"raw_peak_contact_force":177.42002,"subtask_id":"push_to_goal","tcp_end":[0.51166,0.11772,0.04865],"tcp_start":[0.51166,0.1177,0.04863],"tcp_to_object_dist_end":0.02223,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":782.0,"n_steps_budget":1000.0,"object_pos_end":[0.50133,0.10597,0.03383],"object_pos_start":[0.5037,0.10631,0.03129],"object_to_goal_dist_end":0.18608,"object_to_goal_dist_start":0.18655,"object_z_max":0.03489,"peak_contact_force":0.5559,"phase_name":"retract_home","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":829.0,"raw_peak_contact_force":178.54009,"tcp_end":[0.49881,0.19477,0.28097],"tcp_start":[0.51166,0.11772,0.04865],"tcp_to_object_dist_end":0.26262,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```