## Search State

- **Seed**: 5
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.2857 | 0.47 | ✅ accepted |
| 2 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.0451 | 0.00 | ❌ rejected |
| 1 | approach → approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 9 | -0.2084 | 0.00 | ❌ rejected |
| 0 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.1666 | 0.22 | ✅ accepted |

**Proposal policy**: task_score is 0.47 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.286) — your mutation base

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

- **Composite score**: 0.286
- **task_score** (E): 0.473
- **fitness_score**: 0.596  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.310

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above | 1.00 | 1.00 | 0.1958 |
| descend_to_peg | 1.00 | 0.67 | 0.0759 |
| push_channel | 0.00 | 1.00 | 0.0001 |
| retract_home | 1.00 | 1.00 | 0.2986 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.508, 0.132, 0.118) | (0.512, 0.095, 0.040)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 1.000 | 0.530 | 2.488 |
| descend_to_peg | descend | 1.00 / step_budget | (0.508, 0.132, 0.118)→(0.508, 0.114, 0.044) | (0.504, 0.095, 0.034)→(0.504, 0.071, 0.039) | 0.175→0.152 | 0.67 / 1.333 | 37.683 | 177.028 |
| push_channel | push | 0.00 / guard_failure | (0.506, 0.014, 0.041)→(0.506, 0.014, 0.041) | (0.504, 0.071, 0.039)→(0.502, -0.015, 0.032) | 0.152→0.070 | 1.00 / 2.667 | 61.975 | 81.957 |
| retract_home | retract | 1.00 / step_budget | (0.506, 0.014, 0.041)→(0.499, 0.185, 0.276) | (0.502, -0.015, 0.032)→(0.504, -0.015, 0.031) | 0.070→0.071 | 1.00 / 1.000 | 0.550 | 61.216 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.928
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.928
- phase_score: 0.865
- phase_breakdown.approach_peg_score: 0.673
- phase_breakdown.push_to_goal_score: 0.963
- phase_breakdown.descend_peg_score: 0.909

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.890
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.928
- **Median Q (composite search score)**: 0.360
- **K-run variance**: 0.0763
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.314


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.94906,"average_solve_count":373.0,"average_success_count":373.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.speed":0.06965,"descend_to_peg.descend_speed":0.02331,"push_channel.insert_depth":0.181,"push_channel.push_speed":0.02954,"retract_home.speed":0.03956},"optimized_scores":{"best_composite_score":0.36025,"best_fitness_score":0.67025,"best_task_score":0.4751},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":366.0,"contact_point_centroid":[0.51059,0.10764,0.00889],"force_p95":151.73212,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":162.36046,"mean_force":52.18294,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.5116,0.13009,0.07257]},{"body_a":"attachment","body_b":"peg","contact_count":154.0,"contact_point_centroid":[0.51821,0.11647,0.05415],"force_p95":156.00684,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":161.90093,"mean_force":122.95501,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.51074,0.12522,0.05305]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52505,0.11998,0.05999],"force_p95":126.2719,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":156.68752,"mean_force":57.1712,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.51283,0.1247,0.05053]},{"body_a":"peg","body_b":"channel_base_body","contact_count":7.0,"contact_point_centroid":[0.51112,-0.10029,0.02782],"force_p95":45.58168,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":48.94263,"mean_force":30.39351,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.5047,-0.03743,0.03787]},{"body_a":"attachment","body_b":"peg","contact_count":364.0,"contact_point_centroid":[0.50289,0.02192,0.03815],"force_p95":10.70374,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":48.82922,"mean_force":2.5955,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50478,0.03362,0.03796]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":121.0,"contact_point_centroid":[0.47479,0.00356,0.03334],"force_p95":18.33653,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":28.01812,"mean_force":9.84897,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50551,0.06366,0.03894]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":62.0,"contact_point_centroid":[0.5256,0.08468,0.04349],"force_p95":18.38769,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":24.35102,"mean_force":14.01329,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50627,0.1149,0.03994]},{"body_a":"peg","body_b":"channel_base_body","contact_count":356.0,"contact_point_centroid":[0.49632,-0.01461,0.00981],"force_p95":4.9726,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.2524,"mean_force":1.66405,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50475,0.02953,0.03792]},{"body_a":"peg","body_b":"channel_base_body","contact_count":85.0,"contact_point_centroid":[0.51505,-0.10011,0.02529],"force_p95":2.35004,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.05396,"mean_force":0.44527,"phase_index":3.0,"phase_name":"retract_home","phase_type":"retract","tcp_position_centroid":[0.50143,-0.0054,0.07047]},{"body_a":"attachment","body_b":"peg","contact_count":9.0,"contact_point_centroid":[0.50332,-0.04976,0.0421],"force_p95":6.22624,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.6971,"mean_force":1.35915,"phase_index":3.0,"phase_name":"retract_home","phase_type":"retract","tcp_position_centroid":[0.50428,-0.03809,0.03771]},{"body_a":"peg","body_b":"channel_base_body","contact_count":994.0,"contact_point_centroid":[0.50323,-0.07278,0.00816],"force_p95":0.72613,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.84401,"mean_force":0.64596,"phase_index":3.0,"phase_name":"retract_home","phase_type":"retract","tcp_position_centroid":[0.49985,0.07313,0.15608]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":12.0,"contact_point_centroid":[0.52501,-0.04997,0.02468],"force_p95":7.50164,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.55015,"mean_force":3.15926,"phase_index":3.0,"phase_name":"retract_home","phase_type":"retract","tcp_position_centroid":[0.50001,0.04761,0.12774]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52501,0.10406,0.05711],"force_p95":6.22786,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.5026,"mean_force":3.36443,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50978,0.12544,0.05387]},{"body_a":"peg","body_b":"channel_base_body","contact_count":352.0,"contact_point_centroid":[0.50558,0.10467,0.00936],"force_p95":0.59057,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.57846,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.50913,0.16914,0.20354]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":9.0,"contact_point_centroid":[0.47497,-0.09621,0.02681],"force_p95":3.08595,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.12855,"mean_force":0.93889,"phase_index":3.0,"phase_name":"retract_home","phase_type":"retract","tcp_position_centroid":[0.50284,-0.0341,0.04089]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":9.0,"contact_point_centroid":[0.47443,0.05986,0.05277],"force_p95":2.1655,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.3392,"mean_force":1.14733,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50904,0.12351,0.04391]}],"total_contact_groups":17},"final_pose_error":0.03231,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50452,-0.07262,0.02421],"final_tcp_position":[0.49855,0.18062,0.27419],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":162.36046,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":379.0,"n_steps_budget":1000.0,"object_pos_end":[0.50591,0.10456,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18476,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.54908,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":384.0,"raw_peak_contact_force":3.33087,"subtask_id":"approach_peg","tcp_end":[0.51872,0.14133,0.11783],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09258,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":380.0,"n_steps_budget":1000.0,"object_pos_end":[0.49886,0.07273,0.04252],"object_pos_start":[0.50591,0.10456,0.03384],"object_to_goal_dist_end":0.15276,"object_to_goal_dist_start":0.18476,"object_z_max":0.04286,"peak_contact_force":0.38986,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":577.0,"raw_peak_contact_force":162.36046,"subtask_id":"descend_peg","tcp_end":[0.50838,0.12307,0.04255],"tcp_start":[0.51872,0.14133,0.11783],"tcp_to_object_dist_end":0.05123,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":578.0,"n_steps_budget":1000.0,"object_pos_end":[0.49702,-0.0735,0.02833],"object_pos_start":[0.49886,0.07273,0.04252],"object_to_goal_dist_end":0.01369,"object_to_goal_dist_start":0.15276,"object_z_max":0.04252,"peak_contact_force":17.03435,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":910.0,"raw_peak_contact_force":48.94263,"subtask_id":"push_to_goal","tcp_end":[0.50464,-0.0381,0.0378],"tcp_start":[0.50468,-0.03801,0.03784],"tcp_to_object_dist_end":0.03743,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50452,-0.07262,0.02421],"object_pos_start":[0.49691,-0.07375,0.02839],"object_to_goal_dist_end":0.01801,"object_to_goal_dist_start":0.01354,"object_z_max":0.02839,"peak_contact_force":0.56481,"phase_name":"retract_home","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1109.0,"raw_peak_contact_force":9.05396,"tcp_end":[0.49855,0.18062,0.27419],"tcp_start":[0.50464,-0.0381,0.0378],"tcp_to_object_dist_end":0.35589,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.92042,"average_solve_count":377.0,"average_success_count":377.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.speed":0.06733,"descend_to_peg.descend_speed":0.02016,"push_channel.insert_depth":0.17342,"push_channel.push_speed":0.02863,"retract_home.speed":0.06273},"optimized_scores":{"best_composite_score":0.58044,"best_fitness_score":0.89044,"best_task_score":0.92797},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":360.0,"contact_point_centroid":[0.50734,0.07025,0.00897],"force_p95":153.94043,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":157.4982,"mean_force":44.63932,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50044,0.09541,0.07431]},{"body_a":"attachment","body_b":"peg","contact_count":132.0,"contact_point_centroid":[0.51246,0.0815,0.05439],"force_p95":155.68229,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":157.00456,"mean_force":120.35352,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50374,0.0891,0.05355]},{"body_a":"attachment","body_b":"peg","contact_count":110.0,"contact_point_centroid":[0.50198,-0.03556,0.03864],"force_p95":27.99553,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":43.35742,"mean_force":5.76799,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50052,-0.0238,0.03845]},{"body_a":"peg","body_b":"channel_base_body","contact_count":12.0,"contact_point_centroid":[0.49838,-0.10042,0.06074],"force_p95":33.6221,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":35.47761,"mean_force":23.72788,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.5005,-0.05194,0.03839]},{"body_a":"peg","body_b":"channel_base_body","contact_count":399.0,"contact_point_centroid":[0.50393,-0.0368,0.0095],"force_p95":10.08473,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.64467,"mean_force":1.77762,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50073,0.01943,0.03872]},{"body_a":"peg","body_b":"channel_base_body","contact_count":28.0,"contact_point_centroid":[0.50225,-0.10019,0.05165],"force_p95":12.0916,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.77881,"mean_force":1.87959,"phase_index":3.0,"phase_name":"retract_home","phase_type":"retract","tcp_position_centroid":[0.49869,-0.04376,0.04583]},{"body_a":"attachment","body_b":"peg","contact_count":11.0,"contact_point_centroid":[0.50038,-0.06459,0.04145],"force_p95":14.30412,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.11583,"mean_force":5.17875,"phase_index":3.0,"phase_name":"retract_home","phase_type":"retract","tcp_position_centroid":[0.5,-0.05282,0.0383]},{"body_a":"peg","body_b":"channel_base_body","contact_count":989.0,"contact_point_centroid":[0.50153,-0.08111,0.00942],"force_p95":0.59234,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.52437,"mean_force":0.58159,"phase_index":3.0,"phase_name":"retract_home","phase_type":"retract","tcp_position_centroid":[0.49764,0.06608,0.15722]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":47.0,"contact_point_centroid":[0.52523,-0.04406,0.034],"force_p95":3.99495,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.3983,"mean_force":0.85692,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50052,-0.01504,0.03847]},{"body_a":"peg","body_b":"channel_base_body","contact_count":391.0,"contact_point_centroid":[0.50312,0.06749,0.00932],"force_p95":0.60085,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.56865,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.49929,0.15305,0.20548]}],"total_contact_groups":10},"final_pose_error":0.03278,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50185,-0.08101,0.03393],"final_tcp_position":[0.49824,0.17962,0.27439],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":157.4982,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":407.0,"n_steps_budget":1000.0,"object_pos_end":[0.50305,0.06742,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14758,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54909,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":391.0,"raw_peak_contact_force":2.06903,"subtask_id":"approach_peg","tcp_end":[0.49988,0.10779,0.11659],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09216,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":373.0,"n_steps_budget":1000.0,"object_pos_end":[0.50495,0.03009,0.0433],"object_pos_start":[0.50305,0.06742,0.0338],"object_to_goal_dist_end":0.11025,"object_to_goal_dist_start":0.14758,"object_z_max":0.0434,"peak_contact_force":0.0,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":492.0,"raw_peak_contact_force":157.4982,"subtask_id":"descend_peg","tcp_end":[0.50422,0.08591,0.04309],"tcp_start":[0.49988,0.10779,0.11659],"tcp_to_object_dist_end":0.05583,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":511.0,"n_steps_budget":1000.0,"object_pos_end":[0.50156,-0.08219,0.03699],"object_pos_start":[0.50495,0.03009,0.0433],"object_to_goal_dist_end":0.00403,"object_to_goal_dist_start":0.11025,"object_z_max":0.0433,"peak_contact_force":15.31784,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":568.0,"raw_peak_contact_force":43.35742,"subtask_id":"push_to_goal","tcp_end":[0.50045,-0.05304,0.03829],"tcp_start":[0.50048,-0.05296,0.03833],"tcp_to_object_dist_end":0.0292,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50185,-0.08101,0.03393],"object_pos_start":[0.50148,-0.08236,0.03702],"object_to_goal_dist_end":0.00642,"object_to_goal_dist_start":0.00408,"object_z_max":0.03758,"peak_contact_force":0.54424,"phase_name":"retract_home","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1028.0,"raw_peak_contact_force":15.77881,"tcp_end":[0.49824,0.17962,0.27439],"tcp_start":[0.50045,-0.05304,0.03829],"tcp_to_object_dist_end":0.35463,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.08658,"average_solve_count":231.0,"average_success_count":231.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.speed":0.06411,"descend_to_peg.descend_speed":0.04421,"push_channel.insert_depth":0.18578,"push_channel.push_speed":0.03392,"retract_home.speed":0.04175},"optimized_scores":{"best_composite_score":-0.08362,"best_fitness_score":0.22638,"best_task_score":0.01535},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":394.0,"contact_point_centroid":[0.51056,0.11559,0.00864],"force_p95":203.60621,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":211.22576,"mean_force":75.55099,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50499,0.13694,0.07016]},{"body_a":"attachment","body_b":"peg","contact_count":197.0,"contact_point_centroid":[0.51597,0.12549,0.05274],"force_p95":201.20316,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":211.20946,"mean_force":149.70193,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50729,0.13322,0.05124]},{"body_a":"peg","body_b":"channel_base_body","contact_count":808.0,"contact_point_centroid":[0.50612,0.10995,0.00934],"force_p95":0.73206,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":158.81587,"mean_force":2.28978,"phase_index":3.0,"phase_name":"retract_home","phase_type":"retract","tcp_position_centroid":[0.50429,0.1645,0.16405]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.52201,0.11969,0.00705],"force_p95":152.70662,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":153.57196,"mean_force":141.77046,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51269,0.13307,0.04715]},{"body_a":"attachment","body_b":"peg","contact_count":43.0,"contact_point_centroid":[0.51967,0.12545,0.05395],"force_p95":124.0469,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":147.00986,"mean_force":32.2423,"phase_index":3.0,"phase_name":"retract_home","phase_type":"retract","tcp_position_centroid":[0.51234,0.13465,0.05268]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.52021,0.12417,0.05003],"force_p95":141.65251,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":142.00801,"mean_force":135.52249,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51269,0.13307,0.04715]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":13.0,"contact_point_centroid":[0.52527,0.11196,0.03434],"force_p95":15.55164,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.41119,"mean_force":3.51994,"phase_index":3.0,"phase_name":"retract_home","phase_type":"retract","tcp_position_centroid":[0.51294,0.13341,0.04813]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.52543,0.11412,0.05494],"force_p95":20.27393,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.54839,"mean_force":10.11738,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51269,0.13307,0.04715]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":66.0,"contact_point_centroid":[0.52524,0.11377,0.05116],"force_p95":12.34529,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.9053,"mean_force":4.40512,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.51091,0.13306,0.048]},{"body_a":"peg","body_b":"channel_base_body","contact_count":350.0,"contact_point_centroid":[0.50339,0.11169,0.00935],"force_p95":0.62727,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.56699,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.50251,0.1728,0.20502]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.49987,0.19932,0.29869]}],"total_contact_groups":11},"final_pose_error":0.01979,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50621,0.10932,0.03382],"final_tcp_position":[0.49895,0.19557,0.28074],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":211.22576,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":372.0,"n_steps_budget":1000.0,"object_pos_end":[0.50374,0.11175,0.03385],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19189,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.49189,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":366.0,"raw_peak_contact_force":2.06328,"subtask_id":"approach_peg","tcp_end":[0.50602,0.14767,0.11822],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09173,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":394.0,"n_steps_budget":1000.0,"object_pos_end":[0.50775,0.11145,0.03016],"object_pos_start":[0.50374,0.11175,0.03385],"object_to_goal_dist_end":0.19186,"object_to_goal_dist_start":0.19189,"object_z_max":0.0341,"peak_contact_force":112.65974,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":657.0,"raw_peak_contact_force":211.22576,"subtask_id":"descend_peg","tcp_end":[0.51263,0.13307,0.04713],"tcp_start":[0.50602,0.14767,0.11822],"tcp_to_object_dist_end":0.02791,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50774,0.11145,0.03016],"object_pos_start":[0.50775,0.11145,0.03016],"object_to_goal_dist_end":0.19186,"object_to_goal_dist_start":0.19186,"object_z_max":0.03018,"peak_contact_force":153.57196,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":9.0,"raw_peak_contact_force":153.57196,"subtask_id":"push_to_goal","tcp_end":[0.51279,0.13311,0.04723],"tcp_start":[0.51273,0.13309,0.04717],"tcp_to_object_dist_end":0.02804,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":808.0,"n_steps_budget":1000.0,"object_pos_end":[0.50621,0.10932,0.03382],"object_pos_start":[0.50772,0.11147,0.03021],"object_to_goal_dist_end":0.18952,"object_to_goal_dist_start":0.19187,"object_z_max":0.03521,"peak_contact_force":0.53953,"phase_name":"retract_home","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":864.0,"raw_peak_contact_force":158.81587,"tcp_end":[0.49895,0.19557,0.28074],"tcp_start":[0.51279,0.13311,0.04723],"tcp_to_object_dist_end":0.26165,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```