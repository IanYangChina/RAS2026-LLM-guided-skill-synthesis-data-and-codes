## Search State

- **Seed**: 5
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 10 | 0.0085 | 0.29 | ✅ accepted |
| 9 | approach → descend → push → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 14 | -0.3522 | 0.10 | ❌ rejected |
| 8 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 10 | -0.0775 | 0.24 | ✅ accepted |
| 7 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9 | -0.2422 | 0.22 | ✅ accepted |
| 6 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | pose_tolerance | time_limit | pose_tolerance | 9 | -0.2436 | 0.22 | ✅ accepted |

**Proposal policy**: task_score is 0.29 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.008) — your mutation base

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
      - 10.0
      - 25.0
      default: 15.0
      binds_to:
      - path: duration.max_time
        mode: replace
    push_force_limit:
      type: scalar
      range:
      - 40.0
      - 50.0
      default: 45.0
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
    threshold: 45.0
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.01
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
    - id=push_force_guard, when=during_phase, predicate=force_below, on_failure=retry, threshold=45.0
  - retries: max_attempts=1, strategy=offset_target, offset=[0.01, 0.0, 0.0]
- **retract_away** (`retract`)
  - target: source=yaml, anchor=world, offset=[0.5, 0.2, 0.3], tolerance=0.05
  - orientation: mode=none
  - parameter_bindings:
    - retract_speed: status=consumed; consumers=generator.speed (replace)
    - retract_tol: status=consumed; consumers=termination.pose_tolerance (replace)

## Design Metrics

- **Composite score**: 0.008
- **task_score** (E): 0.287
- **fitness_score**: 0.235  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.560

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_behind | 1.00 | 1.00 | 0.1771 |
| descend_to_peg | 1.00 | 1.00 | 0.0845 |
| push_channel | 1.00 | 0.67 | 0.0823 |
| retract_away | 1.00 | 1.00 | 0.2559 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_behind | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.508, 0.133, 0.137) | (0.512, 0.095, 0.040)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 1.000 | 0.556 | 2.488 |
| descend_to_peg | descend | 1.00 / force_exceeded | (0.508, 0.133, 0.137)→(0.501, 0.099, 0.060) | (0.504, 0.095, 0.034)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 2.000 | 23.560 | 23.560 |
| push_channel | push | 1.00 / time_limit | (0.501, 0.099, 0.060)→(0.497, 0.017, 0.056) | (0.504, 0.095, 0.034)→(0.499, 0.059, 0.041) | 0.175→0.139 | 0.67 / 0.667 | 0.327 | 45.656 |
| retract_away | retract | 1.00 / step_budget | (0.497, 0.017, 0.056)→(0.500, 0.172, 0.259) | (0.499, 0.059, 0.041)→(0.501, 0.034, 0.024) | 0.139→0.115 | 1.00 / 1.000 | 0.584 | 4.028 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.385
- alignment_error: None
- force_efficiency: 0.072
- terminal_score: 0.385
- phase_score: 0.239
- phase_breakdown.push_to_goal_score: 0.224
- phase_breakdown.reach_approach_score: 0.274

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.297
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.385
- **Median Q (composite search score)**: 0.030
- **K-run variance**: 0.0038
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.317


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.76562,"average_solve_count":128.0,"average_success_count":128.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.1194,"approach_behind.approach_tol":0.02173,"descend_to_peg.descend_force_threshold":10.16361,"descend_to_peg.descend_speed":0.08822,"push_channel.push_distance":0.20958,"push_channel.push_duration":14.77453,"push_channel.push_force_limit":46.59061,"push_channel.push_speed":0.0358,"retract_away.retract_speed":0.27049,"retract_away.retract_tol":0.05631},"optimized_scores":{"best_composite_score":-0.0753,"best_fitness_score":0.15137,"best_task_score":0.11936},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50912,0.07625,0.00954],"force_p95":43.88767,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":45.39626,"mean_force":30.30202,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50257,0.06862,0.05841]},{"body_a":"attachment","body_b":"peg","contact_count":837.0,"contact_point_centroid":[0.51192,0.08077,0.05816],"force_p95":43.45599,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":44.93843,"mean_force":35.6277,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.503,0.07549,0.05889]},{"body_a":"peg","body_b":"channel_base_body","contact_count":381.0,"contact_point_centroid":[0.50589,0.10479,0.00939],"force_p95":0.57555,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":29.58195,"mean_force":0.62256,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.51026,0.12556,0.09776]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51581,0.10921,0.0588],"force_p95":29.03821,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.03821,"mean_force":29.03821,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50396,0.10915,0.06065]},{"body_a":"peg","body_b":"channel_base_body","contact_count":318.0,"contact_point_centroid":[0.50537,0.10455,0.00936],"force_p95":0.60043,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.58191,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50814,0.17216,0.21532]},{"body_a":"peg","body_b":"channel_base_body","contact_count":242.0,"contact_point_centroid":[0.49838,0.05342,0.00874],"force_p95":0.97802,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.48319,"mean_force":0.58989,"phase_index":3.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.49946,0.10037,0.15456]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.4996,0.19974,0.29468]},{"body_a":"attachment","body_b":"peg","contact_count":4.0,"contact_point_centroid":[0.49969,0.05014,0.06648],"force_p95":1.24788,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.28915,"mean_force":0.943,"phase_index":3.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.4974,0.03853,0.0668]}],"total_contact_groups":8},"final_pose_error":0.04964,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49669,0.04518,0.02455],"final_tcp_position":[0.50053,0.17341,0.25809],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":45.39626,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":345.0,"n_steps_budget":1000.0,"object_pos_end":[0.50585,0.1047,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.1849,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.54226,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":350.0,"raw_peak_contact_force":3.33087,"subtask_id":"reach_approach","tcp_end":[0.51873,0.14209,0.13757],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11102,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":381.0,"n_steps_budget":660.0,"object_pos_end":[0.50601,0.10468,0.03384],"object_pos_start":[0.50585,0.1047,0.03384],"object_to_goal_dist_end":0.18488,"object_to_goal_dist_start":0.1849,"object_z_max":0.03384,"peak_contact_force":29.58195,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":382.0,"raw_peak_contact_force":29.58195,"subtask_id":"reach_approach","tcp_end":[0.50397,0.10907,0.06046],"tcp_start":[0.51873,0.14209,0.13757],"tcp_to_object_dist_end":0.02706,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50054,0.06613,0.04035],"object_pos_start":[0.50601,0.10468,0.03384],"object_to_goal_dist_end":0.14613,"object_to_goal_dist_start":0.18488,"object_z_max":0.04078,"peak_contact_force":0.0,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1837.0,"raw_peak_contact_force":45.39626,"subtask_id":"push_to_goal","tcp_end":[0.5002,0.02847,0.05583],"tcp_start":[0.50397,0.10907,0.06046],"tcp_to_object_dist_end":0.04072,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":249.0,"n_steps_budget":720.0,"object_pos_end":[0.49669,0.04518,0.02455],"object_pos_start":[0.50054,0.06613,0.04035],"object_to_goal_dist_end":0.12617,"object_to_goal_dist_start":0.14613,"object_z_max":0.04035,"peak_contact_force":0.56304,"phase_name":"retract_away","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":246.0,"raw_peak_contact_force":2.48319,"subtask_id":"push_to_goal","tcp_end":[0.50053,0.17341,0.25809],"tcp_start":[0.5002,0.02847,0.05583],"tcp_to_object_dist_end":0.26646,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.73333,"average_solve_count":180.0,"average_success_count":180.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.07812,"approach_behind.approach_tol":0.01635,"descend_to_peg.descend_force_threshold":2.94627,"descend_to_peg.descend_speed":0.07129,"push_channel.push_distance":0.2503,"push_channel.push_duration":17.30191,"push_channel.push_force_limit":49.85642,"push_channel.push_speed":0.03068,"retract_away.retract_speed":0.11708,"retract_away.retract_tol":0.03466},"optimized_scores":{"best_composite_score":0.0707,"best_fitness_score":0.29737,"best_task_score":0.38531},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50538,0.03809,0.00949],"force_p95":44.91044,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":46.41156,"mean_force":31.75949,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.4977,0.03216,0.05844]},{"body_a":"attachment","body_b":"peg","contact_count":864.0,"contact_point_centroid":[0.50738,0.04281,0.05806],"force_p95":44.46318,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":45.96551,"mean_force":36.20046,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49807,0.03803,0.05883]},{"body_a":"peg","body_b":"channel_base_body","contact_count":467.0,"contact_point_centroid":[0.50306,0.0675,0.00938],"force_p95":0.55059,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.98749,"mean_force":0.59684,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.49817,0.09031,0.09625]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51083,0.07291,0.05872],"force_p95":23.4842,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.4842,"mean_force":23.4842,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.49897,0.07263,0.06051]},{"body_a":"peg","body_b":"channel_base_body","contact_count":283.0,"contact_point_centroid":[0.49886,0.01986,0.00907],"force_p95":0.84625,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.67757,"mean_force":0.56682,"phase_index":3.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.49662,0.07812,0.15489]},{"body_a":"peg","body_b":"channel_base_body","contact_count":374.0,"contact_point_centroid":[0.50312,0.06744,0.00932],"force_p95":0.61822,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.56964,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.49846,0.15727,0.21821]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":4.0,"contact_point_centroid":[0.47498,0.00835,0.05443],"force_p95":0.47452,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.48726,"mean_force":0.37457,"phase_index":3.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.49599,0.05668,0.12962]}],"total_contact_groups":7},"final_pose_error":0.04969,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50353,0.00581,0.02418],"final_tcp_position":[0.4995,0.16972,0.2606],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":46.41156,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":390.0,"n_steps_budget":1000.0,"object_pos_end":[0.50302,0.06743,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54714,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":374.0,"raw_peak_contact_force":2.06903,"subtask_id":"reach_approach","tcp_end":[0.49996,0.10873,0.13611],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11038,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":467.0,"n_steps_budget":810.0,"object_pos_end":[0.50307,0.06741,0.0338],"object_pos_start":[0.50302,0.06743,0.0338],"object_to_goal_dist_end":0.14757,"object_to_goal_dist_start":0.14759,"object_z_max":0.0338,"peak_contact_force":23.98749,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":468.0,"raw_peak_contact_force":23.98749,"subtask_id":"reach_approach","tcp_end":[0.49898,0.07256,0.06036],"tcp_start":[0.49996,0.10873,0.13611],"tcp_to_object_dist_end":0.02736,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49822,0.03248,0.04078],"object_pos_start":[0.50307,0.06741,0.0338],"object_to_goal_dist_end":0.1125,"object_to_goal_dist_start":0.14757,"object_z_max":0.04078,"peak_contact_force":0.49046,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1864.0,"raw_peak_contact_force":46.41156,"subtask_id":"push_to_goal","tcp_end":[0.49526,-0.00996,0.05583],"tcp_start":[0.49898,0.07256,0.06036],"tcp_to_object_dist_end":0.04513,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":291.0,"n_steps_budget":1000.0,"object_pos_end":[0.50353,0.00581,0.02418],"object_pos_start":[0.49822,0.03248,0.04078],"object_to_goal_dist_end":0.08733,"object_to_goal_dist_start":0.1125,"object_z_max":0.04078,"peak_contact_force":0.5693,"phase_name":"retract_away","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":287.0,"raw_peak_contact_force":2.67757,"subtask_id":"push_to_goal","tcp_end":[0.4995,0.16972,0.2606],"tcp_start":[0.49526,-0.00996,0.05583],"tcp_to_object_dist_end":0.28771,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.70345,"average_solve_count":145.0,"average_success_count":145.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.1336,"approach_behind.approach_tol":0.03214,"descend_to_peg.descend_force_threshold":10.15676,"descend_to_peg.descend_speed":0.05358,"push_channel.push_distance":0.25086,"push_channel.push_duration":17.16395,"push_channel.push_force_limit":48.30107,"push_channel.push_speed":0.03157,"retract_away.retract_speed":0.16404,"retract_away.retract_tol":0.03003},"optimized_scores":{"best_composite_score":0.02998,"best_fitness_score":0.25665,"best_task_score":0.35578},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50604,0.08311,0.00955],"force_p95":44.0255,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":45.16021,"mean_force":29.78183,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49906,0.07481,0.05839]},{"body_a":"attachment","body_b":"peg","contact_count":816.0,"contact_point_centroid":[0.50865,0.08795,0.05818],"force_p95":43.57859,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":44.73645,"mean_force":35.90636,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49955,0.08284,0.05892]},{"body_a":"peg","body_b":"channel_base_body","contact_count":457.0,"contact_point_centroid":[0.50375,0.11172,0.0094],"force_p95":0.595,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.11029,"mean_force":0.58069,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50211,0.13202,0.09768]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51234,0.11627,0.05881],"force_p95":16.63388,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.63388,"mean_force":16.63388,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50048,0.11605,0.06061]},{"body_a":"peg","body_b":"channel_base_body","contact_count":250.0,"contact_point_centroid":[0.5002,0.06216,0.00893],"force_p95":0.94567,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.92213,"mean_force":0.62838,"phase_index":3.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.49742,0.10227,0.15396]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":8.0,"contact_point_centroid":[0.52504,0.07462,0.02463],"force_p95":6.68532,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.68628,"mean_force":1.94909,"phase_index":3.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.49911,0.15144,0.22517]},{"body_a":"peg","body_b":"channel_base_body","contact_count":306.0,"contact_point_centroid":[0.50346,0.11166,0.00933],"force_p95":0.67342,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.57117,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50195,0.17537,0.21607]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":3.0,"contact_point_centroid":[0.47498,0.04813,0.05053],"force_p95":0.7855,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.79933,"mean_force":0.66888,"phase_index":3.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.4965,0.07416,0.11285]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.49972,0.19974,0.29817]}],"total_contact_groups":9},"final_pose_error":0.04973,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.504,0.0519,0.02457],"final_tcp_position":[0.49977,0.17383,0.25772],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":45.16021,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":328.0,"n_steps_budget":900.0,"object_pos_end":[0.5038,0.11182,0.03381],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19195,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.57985,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":322.0,"raw_peak_contact_force":2.06328,"subtask_id":"reach_approach","tcp_end":[0.5063,0.14846,0.13823],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11068,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":457.0,"n_steps_budget":1000.0,"object_pos_end":[0.5037,0.11179,0.03385],"object_pos_start":[0.5038,0.11182,0.03381],"object_to_goal_dist_end":0.19192,"object_to_goal_dist_start":0.19195,"object_z_max":0.03389,"peak_contact_force":17.11029,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":458.0,"raw_peak_contact_force":17.11029,"subtask_id":"reach_approach","tcp_end":[0.50049,0.11598,0.06045],"tcp_start":[0.5063,0.14846,0.13823],"tcp_to_object_dist_end":0.02712,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49847,0.07756,0.04076],"object_pos_start":[0.5037,0.11179,0.03385],"object_to_goal_dist_end":0.15757,"object_to_goal_dist_start":0.19192,"object_z_max":0.04078,"peak_contact_force":0.48992,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1816.0,"raw_peak_contact_force":45.16021,"subtask_id":"push_to_goal","tcp_end":[0.49675,0.03273,0.05588],"tcp_start":[0.50049,0.11598,0.06045],"tcp_to_object_dist_end":0.04734,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":257.0,"n_steps_budget":1000.0,"object_pos_end":[0.504,0.0519,0.02457],"object_pos_start":[0.49847,0.07756,0.04076],"object_to_goal_dist_end":0.13286,"object_to_goal_dist_start":0.15757,"object_z_max":0.04076,"peak_contact_force":0.62098,"phase_name":"retract_away","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":261.0,"raw_peak_contact_force":6.92213,"subtask_id":"push_to_goal","tcp_end":[0.49977,0.17383,0.25772],"tcp_start":[0.49675,0.03273,0.05588],"tcp_to_object_dist_end":0.26313,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```