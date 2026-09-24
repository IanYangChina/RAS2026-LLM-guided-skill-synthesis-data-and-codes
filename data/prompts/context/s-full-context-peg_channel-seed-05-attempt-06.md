## Search State

- **Seed**: 5
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | pose_tolerance | time_limit | pose_tolerance | 9 | -0.2436 | 0.22 | ✅ accepted |
| 5 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | pose_tolerance | time_limit | pose_tolerance | 8 | -0.1804 | 0.19 | ✅ accepted |
| 4 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | pose_tolerance | time_limit | pose_tolerance | 6 | -0.1141 | 0.14 | ✅ accepted |
| 3 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 2 | -0.0183 | 0.00 | ❌ rejected |
| 2 | push → release → pull → release → release → grasp → retract | linear_cartesian | — | arc_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | admittance_control | position_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | time_limit | time_limit | pose_tolerance | 3 | -0.2993 | 0.00 | ✅ accepted |

**Proposal policy**: task_score is 0.22 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.244) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: reach_approach
  anchor: object
  offset:
  - 0.0
  - 0.03
  - 0.0
  weight: 0.3
- id: push_to_goal
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
    - 0.0
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
      - 15.0
      default: 10.0
      binds_to:
      - path: duration.max_time
        mode: replace
    push_force_guard_threshold:
      type: scalar
      range:
      - 5.0
      - 40.0
      default: 25.0
      binds_to:
      - path: guards.push_force_guard.threshold
        mode: replace
    push_retry_offset_y:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: retry.offset.y
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
    threshold: 25.0
    on_failure: retry
  retries:
    max_attempts: 3
    strategy: offset_target
    offset:
    - 0.0
    - 0.02
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
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: push_to_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_behind** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.03, 0.0], tolerance=0.02
  - orientation: mode=align_axis, axis=[1.0, 0.0, 0.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - approach_tol: status=consumed; consumers=termination.pose_tolerance (replace)
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.005, 0.0]
- **push_channel** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.2, mode=replace_offset_projection, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_duration: status=consumed; consumers=duration.max_time (replace)
    - push_force_guard_threshold: status=consumed; consumers=guards.push_force_guard.threshold (replace)
    - push_retry_offset_y: status=consumed; consumers=retry.offset.y (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=push_force_guard, when=during_phase, predicate=force_below, on_failure=retry, threshold=25.0
  - retries: max_attempts=3, strategy=offset_target, offset=[0.0, 0.02, 0.0]
- **retract_away** (`retract`)
  - target: source=yaml, anchor=world, offset=[0.5, 0.2, 0.3], tolerance=0.05
  - orientation: mode=none
  - parameter_bindings:
    - retract_speed: status=consumed; consumers=generator.speed (replace)
    - retract_tol: status=consumed; consumers=termination.pose_tolerance (replace)
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, 0.0]

## Design Metrics

- **Composite score**: -0.244
- **task_score** (E): 0.216
- **fitness_score**: 0.236  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.480

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_behind | 1.00 | 1.00 | 0.2527 |
| push_channel | 0.33 | 1.00 | 0.0241 |
| retract_away | 1.00 | 1.00 | 0.2222 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_behind | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.508, 0.130, 0.058) | (0.512, 0.095, 0.040)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 1.000 | 0.562 | 2.488 |
| push_channel | push | 0.33 / guard_failure | (0.506, 0.113, 0.055)→(0.505, 0.089, 0.053) | (0.504, 0.095, 0.034)→(0.505, 0.068, 0.034) | 0.175→0.148 | 1.00 / 2.333 | 23.346 | 42.652 |
| retract_away | retract | 1.00 / step_budget | (0.505, 0.089, 0.053)→(0.501, 0.181, 0.254) | (0.505, 0.068, 0.034)→(0.504, 0.060, 0.027) | 0.148→0.141 | 1.00 / 1.000 | 0.569 | 24.532 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.317
- alignment_error: None
- force_efficiency: 0.383
- terminal_score: 0.317
- phase_score: 0.339
- phase_breakdown.push_to_goal_score: 0.194
- phase_breakdown.reach_approach_score: 0.675

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.330
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.329
- **Median Q (composite search score)**: -0.224
- **K-run variance**: 0.0073
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.323


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.08,"average_solve_count":100.0,"average_success_count":100.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.09315,"approach_behind.approach_tol":0.03335,"push_channel.push_distance":0.20547,"push_channel.push_duration":6.38157,"push_channel.push_force_guard_threshold":25.80118,"push_channel.push_retry_offset_y":0.02182,"push_channel.push_speed":0.04002,"retract_away.retract_speed":0.18834,"retract_away.retract_tol":0.03521},"optimized_scores":{"best_composite_score":-0.35696,"best_fitness_score":0.12304,"best_task_score":0.00331},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":15.0,"contact_point_centroid":[0.52504,0.11996,0.05999],"force_p95":76.71352,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":92.24918,"mean_force":27.91324,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51526,0.12819,0.0532]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.52501,0.11999,0.06],"force_p95":49.69444,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":49.69444,"mean_force":49.69444,"phase_index":2.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.51513,0.1282,0.05317]},{"body_a":"peg","body_b":"channel_base_body","contact_count":219.0,"contact_point_centroid":[0.50474,0.10304,0.00949],"force_p95":0.7697,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.42153,"mean_force":0.59795,"phase_index":2.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.508,0.1564,0.14736]},{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.51087,0.11706,0.05386],"force_p95":9.9296,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.32988,"mean_force":6.32712,"phase_index":2.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.51511,0.12823,0.05315]},{"body_a":"peg","body_b":"channel_base_body","contact_count":159.0,"contact_point_centroid":[0.50256,0.09602,0.00961],"force_p95":3.72304,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.71081,"mean_force":1.20621,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51593,0.133,0.05391]},{"body_a":"attachment","body_b":"peg","contact_count":56.0,"contact_point_centroid":[0.51129,0.11865,0.05396],"force_p95":3.67465,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.39563,"mean_force":2.10473,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51536,0.12986,0.05327]},{"body_a":"peg","body_b":"channel_base_body","contact_count":460.0,"contact_point_centroid":[0.50557,0.10457,0.00937],"force_p95":0.57869,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.57094,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50875,0.16968,0.17441]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.49965,0.19976,0.29468]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":14.0,"contact_point_centroid":[0.52525,0.10525,0.059],"force_p95":0.28223,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.34454,"mean_force":0.07735,"phase_index":2.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.51043,0.13742,0.08221]}],"total_contact_groups":9},"final_pose_error":0.04987,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50552,0.10357,0.0339],"final_tcp_position":[0.50289,0.18699,0.25194],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":92.24918,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":487.0,"n_steps_budget":1000.0,"object_pos_end":[0.50583,0.10467,0.03383],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18486,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.54719,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":492.0,"raw_peak_contact_force":3.33087,"subtask_id":"reach_approach","tcp_end":[0.51895,0.13956,0.05813],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.0445,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":159.0,"n_steps_budget":1000.0,"object_pos_end":[0.50478,0.1017,0.03643],"object_pos_start":[0.50583,0.10467,0.03383],"object_to_goal_dist_end":0.1818,"object_to_goal_dist_start":0.18486,"object_z_max":0.03644,"peak_contact_force":53.18137,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":230.0,"raw_peak_contact_force":92.24918,"subtask_id":"push_to_goal","tcp_end":[0.51513,0.1282,0.05317],"tcp_start":[0.51517,0.12815,0.0532],"tcp_to_object_dist_end":0.03301,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":219.0,"n_steps_budget":870.0,"object_pos_end":[0.50552,0.10357,0.0339],"object_pos_start":[0.50474,0.10172,0.03643],"object_to_goal_dist_end":0.18376,"object_to_goal_dist_start":0.18182,"object_z_max":0.0366,"peak_contact_force":0.54454,"phase_name":"retract_away","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":236.0,"raw_peak_contact_force":49.69444,"subtask_id":"push_to_goal","tcp_end":[0.50289,0.18699,0.25194],"tcp_start":[0.51513,0.1282,0.05317],"tcp_to_object_dist_end":0.23347,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.22642,"average_solve_count":106.0,"average_success_count":106.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.10484,"approach_behind.approach_tol":0.00567,"push_channel.push_distance":0.2367,"push_channel.push_duration":8.83419,"push_channel.push_force_guard_threshold":16.0002,"push_channel.push_retry_offset_y":0.03623,"push_channel.push_speed":0.09393,"retract_away.retract_speed":0.16193,"retract_away.retract_tol":0.0528},"optimized_scores":{"best_composite_score":-0.15003,"best_fitness_score":0.32997,"best_task_score":0.3171},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":280.0,"contact_point_centroid":[0.50609,0.05155,0.00974],"force_p95":10.52374,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":30.84171,"mean_force":5.41147,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49664,0.08509,0.05362]},{"body_a":"attachment","body_b":"peg","contact_count":184.0,"contact_point_centroid":[0.50057,0.06728,0.05293],"force_p95":13.63334,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":30.57644,"mean_force":8.032,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49634,0.07836,0.05332]},{"body_a":"peg","body_b":"channel_base_body","contact_count":235.0,"contact_point_centroid":[0.50205,0.02387,0.00851],"force_p95":1.00111,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.10501,"mean_force":0.66182,"phase_index":2.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.49708,0.12054,0.15222]},{"body_a":"attachment","body_b":"peg","contact_count":4.0,"contact_point_centroid":[0.50126,0.05357,0.05263],"force_p95":11.57262,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.5395,"mean_force":3.51319,"phase_index":2.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.49623,0.06431,0.05331]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":25.0,"contact_point_centroid":[0.525,0.03363,0.05985],"force_p95":7.84107,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.48244,"mean_force":5.57585,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49634,0.06968,0.05337]},{"body_a":"peg","body_b":"channel_base_body","contact_count":494.0,"contact_point_centroid":[0.50301,0.06742,0.00933],"force_p95":0.55971,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.56406,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.49872,0.1539,0.17746]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":2.0,"contact_point_centroid":[0.52503,0.02623,0.05891],"force_p95":0.15382,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16192,"mean_force":0.08096,"phase_index":2.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.4963,0.06434,0.05331]}],"total_contact_groups":7},"final_pose_error":0.04989,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.499,0.01673,0.02412],"final_tcp_position":[0.49963,0.17766,0.25539],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":30.84171,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":510.0,"n_steps_budget":1000.0,"object_pos_end":[0.50304,0.0675,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14766,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.546,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":494.0,"raw_peak_contact_force":2.06903,"subtask_id":"reach_approach","tcp_end":[0.49976,0.10555,0.05757],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.04499,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":280.0,"n_steps_budget":1000.0,"object_pos_end":[0.50574,0.04192,0.04037],"object_pos_start":[0.50304,0.0675,0.0338],"object_to_goal_dist_end":0.12205,"object_to_goal_dist_start":0.14766,"object_z_max":0.04042,"peak_contact_force":16.33433,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":489.0,"raw_peak_contact_force":30.84171,"subtask_id":"push_to_goal","tcp_end":[0.49632,0.06437,0.05333],"tcp_start":[0.49634,0.06444,0.05337],"tcp_to_object_dist_end":0.02759,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":244.0,"n_steps_budget":1000.0,"object_pos_end":[0.499,0.01673,0.02412],"object_pos_start":[0.50579,0.04151,0.04032],"object_to_goal_dist_end":0.09803,"object_to_goal_dist_start":0.12165,"object_z_max":0.04032,"peak_contact_force":0.63084,"phase_name":"retract_away","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":241.0,"raw_peak_contact_force":14.10501,"subtask_id":"push_to_goal","tcp_end":[0.49963,0.17766,0.25539],"tcp_start":[0.49632,0.06437,0.05333],"tcp_to_object_dist_end":0.28176,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.19249,"average_solve_count":213.0,"average_success_count":213.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.05745,"approach_behind.approach_tol":0.01253,"push_channel.push_distance":0.25119,"push_channel.push_duration":5.54526,"push_channel.push_force_guard_threshold":7.33312,"push_channel.push_retry_offset_y":0.04113,"push_channel.push_speed":0.02833,"retract_away.retract_speed":0.06844,"retract_away.retract_tol":0.08696},"optimized_scores":{"best_composite_score":-0.22374,"best_fitness_score":0.25626,"best_task_score":0.32876},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":255.0,"contact_point_centroid":[0.50664,0.06003,0.0081],"force_p95":0.71079,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.79796,"mean_force":0.80806,"phase_index":2.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.50056,0.12469,0.14987]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":15.0,"contact_point_centroid":[0.525,0.03811,0.02441],"force_p95":9.24714,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.31085,"mean_force":3.81618,"phase_index":2.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.50055,0.11204,0.1249]},{"body_a":"peg","body_b":"channel_base_body","contact_count":994.0,"contact_point_centroid":[0.50429,0.08088,0.00933],"force_p95":4.17781,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.866,"mean_force":2.11393,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50239,0.10958,0.05403]},{"body_a":"attachment","body_b":"peg","contact_count":571.0,"contact_point_centroid":[0.50361,0.10726,0.05385],"force_p95":3.87757,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.40794,"mean_force":2.80003,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50238,0.11916,0.05398]},{"body_a":"peg","body_b":"channel_base_body","contact_count":476.0,"contact_point_centroid":[0.50352,0.1117,0.00936],"force_p95":0.61307,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.5613,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50207,0.17292,0.17568]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.49969,0.19972,0.29877]}],"total_contact_groups":6},"final_pose_error":0.04923,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5065,0.05918,0.02413],"final_tcp_position":[0.50033,0.17919,0.25539],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":9.79796,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":498.0,"n_steps_budget":1000.0,"object_pos_end":[0.50376,0.11178,0.03379],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19192,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.59137,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":492.0,"raw_peak_contact_force":2.06328,"subtask_id":"reach_approach","tcp_end":[0.50595,0.14611,0.05862],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.04242,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50586,0.06022,0.02414],"object_pos_start":[0.50376,0.11178,0.03379],"object_to_goal_dist_end":0.14124,"object_to_goal_dist_start":0.19192,"object_z_max":0.04062,"peak_contact_force":0.52114,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1565.0,"raw_peak_contact_force":4.866,"subtask_id":"push_to_goal","tcp_end":[0.50216,0.07436,0.05388],"tcp_start":[0.50595,0.14611,0.05862],"tcp_to_object_dist_end":0.03314,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":255.0,"n_steps_budget":1000.0,"object_pos_end":[0.5065,0.05918,0.02413],"object_pos_start":[0.50586,0.06022,0.02414],"object_to_goal_dist_end":0.14023,"object_to_goal_dist_start":0.14124,"object_z_max":0.0247,"peak_contact_force":0.53279,"phase_name":"retract_away","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":270.0,"raw_peak_contact_force":9.79796,"subtask_id":"push_to_goal","tcp_end":[0.50033,0.17919,0.25539],"tcp_start":[0.50216,0.07436,0.05388],"tcp_to_object_dist_end":0.26062,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```