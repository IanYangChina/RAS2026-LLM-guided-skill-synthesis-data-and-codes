## Search State

- **Seed**: 5
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 10 | -0.4192 | 0.00 | ❌ rejected |
| 12 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | -0.0626 | 0.00 | ❌ rejected |
| 11 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 10 | 0.0019 | 0.30 | ✅ accepted |
| 10 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 10 | 0.0085 | 0.29 | ✅ accepted |
| 9 | approach → descend → push → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 14 | -0.3522 | 0.10 | ❌ rejected |

**Proposal policy**: task_score is 0.00 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.419) — your mutation base

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

- **Composite score**: -0.419
- **task_score** (E): 0.000
- **fitness_score**: 0.141  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.560

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above | 1.00 | 1.00 | 0.1517 |
| align_contact | 0.00 | 1.00 | 0.0869 |
| push_channel | 1.00 | 1.00 | 0.1509 |
| retract_away | 1.00 | 1.00 | 0.2744 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.508, 0.152, 0.158) | (0.512, 0.095, 0.040)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 1.000 | 0.529 | 2.488 |
| align_contact | contact | 0.00 / step_budget | (0.508, 0.152, 0.158)→(0.501, 0.122, 0.077) | (0.504, 0.095, 0.034)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 1.000 | 0.550 | 0.592 |
| push_channel | push | 1.00 / time_limit | (0.501, 0.122, 0.077)→(0.497, -0.029, 0.072) | (0.504, 0.095, 0.034)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 1.000 | 0.540 | 0.590 |
| retract_away | retract | 1.00 / step_budget | (0.497, -0.029, 0.072)→(0.500, 0.167, 0.263) | (0.504, 0.095, 0.034)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 1.000 | 0.544 | 0.584 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.000
- alignment_error: None
- force_efficiency: 0.959
- terminal_score: 0.000
- phase_score: 0.264
- phase_breakdown.push_to_goal_score: 0.001
- phase_breakdown.reach_peg_side_score: 0.878

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.158
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.001
- **Median Q (composite search score)**: -0.415
- **K-run variance**: 0.0003
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.276


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.67232,"average_solve_count":177.0,"average_success_count":177.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_contact.contact_force_threshold":4.1569,"align_contact.contact_speed":0.03373,"approach_above.approach_speed":0.069,"approach_above.approach_tol":0.02648,"push_channel.push_distance":0.20296,"push_channel.push_duration":18.73727,"push_channel.push_force_limit":45.65077,"push_channel.push_speed":0.07222,"retract_away.retract_speed":0.17163,"retract_away.retract_tol":0.06843},"optimized_scores":{"best_composite_score":-0.44157,"best_fitness_score":0.11843,"best_task_score":0.00025},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":270.0,"contact_point_centroid":[0.50527,0.10475,0.00935],"force_p95":0.61208,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.58826,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.50903,0.17885,0.2237]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.50026,0.1985,0.29507]},{"body_a":"peg","body_b":"channel_base_body","contact_count":414.0,"contact_point_centroid":[0.50585,0.10457,0.00939],"force_p95":0.57547,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57941,"mean_force":0.54626,"phase_index":1.0,"phase_name":"align_contact","phase_type":"contact","tcp_position_centroid":[0.50987,0.14611,0.11639]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.5059,0.10462,0.00939],"force_p95":0.57569,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57597,"mean_force":0.54635,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49998,0.07307,0.07284]},{"body_a":"peg","body_b":"channel_base_body","contact_count":255.0,"contact_point_centroid":[0.50616,0.10467,0.00939],"force_p95":0.57565,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57567,"mean_force":0.54633,"phase_index":3.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.49906,0.09066,0.16254]}],"total_contact_groups":5},"final_pose_error":0.04973,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50586,0.10456,0.03384],"final_tcp_position":[0.50011,0.17083,0.25972],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":3.33087,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":297.0,"n_steps_budget":1000.0,"object_pos_end":[0.506,0.10467,0.03383],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18487,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.55356,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":302.0,"raw_peak_contact_force":3.33087,"subtask_id":"reach_peg_side","tcp_end":[0.51828,0.16033,0.1577],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13635,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":414.0,"n_steps_budget":1000.0,"object_pos_end":[0.50593,0.10472,0.03383],"object_pos_start":[0.506,0.10467,0.03383],"object_to_goal_dist_end":0.18492,"object_to_goal_dist_start":0.18487,"object_z_max":0.03384,"peak_contact_force":0.52988,"phase_name":"align_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":414.0,"raw_peak_contact_force":0.57941,"subtask_id":"reach_peg_side","tcp_end":[0.5036,0.13198,0.07753],"tcp_start":[0.51828,0.16033,0.1577],"tcp_to_object_dist_end":0.05155,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50588,0.10471,0.03384],"object_pos_start":[0.50593,0.10472,0.03383],"object_to_goal_dist_end":0.18491,"object_to_goal_dist_start":0.18492,"object_z_max":0.03384,"peak_contact_force":0.54255,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.57597,"subtask_id":"push_to_goal","tcp_end":[0.4998,0.01404,0.07272],"tcp_start":[0.5036,0.13198,0.07753],"tcp_to_object_dist_end":0.09885,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":255.0,"n_steps_budget":1000.0,"object_pos_end":[0.50586,0.10456,0.03384],"object_pos_start":[0.50588,0.10471,0.03384],"object_to_goal_dist_end":0.18475,"object_to_goal_dist_start":0.18491,"object_z_max":0.03384,"peak_contact_force":0.55164,"phase_name":"retract_away","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":255.0,"raw_peak_contact_force":0.57567,"subtask_id":"push_to_goal","tcp_end":[0.50011,0.17083,0.25972],"tcp_start":[0.4998,0.01404,0.07272],"tcp_to_object_dist_end":0.23548,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.91946,"average_solve_count":149.0,"average_success_count":149.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_contact.contact_force_threshold":9.90754,"align_contact.contact_speed":0.0863,"approach_above.approach_speed":0.13192,"approach_above.approach_tol":0.02777,"push_channel.push_distance":0.23015,"push_channel.push_duration":16.69276,"push_channel.push_force_limit":48.67933,"push_channel.push_speed":0.09902,"retract_away.retract_speed":0.11671,"retract_away.retract_tol":0.03227},"optimized_scores":{"best_composite_score":-0.40164,"best_fitness_score":0.15836,"best_task_score":0.00026},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":288.0,"contact_point_centroid":[0.50298,0.06753,0.0093],"force_p95":0.69918,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.57653,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.49949,0.16305,0.22549]},{"body_a":"peg","body_b":"channel_base_body","contact_count":448.0,"contact_point_centroid":[0.50309,0.06736,0.00938],"force_p95":0.55081,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5555,"mean_force":0.54664,"phase_index":1.0,"phase_name":"align_contact","phase_type":"contact","tcp_position_centroid":[0.49832,0.11095,0.11412]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50304,0.06746,0.00938],"force_p95":0.55057,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55081,"mean_force":0.54665,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49542,0.0147,0.07109]},{"body_a":"peg","body_b":"channel_base_body","contact_count":320.0,"contact_point_centroid":[0.50319,0.06754,0.00938],"force_p95":0.55056,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5506,"mean_force":0.54665,"phase_index":3.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.49655,0.04719,0.16465]}],"total_contact_groups":4},"final_pose_error":0.04973,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50304,0.06742,0.0338],"final_tcp_position":[0.49946,0.16478,0.26489],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":2.06903,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":304.0,"n_steps_budget":870.0,"object_pos_end":[0.50309,0.06748,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14764,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54693,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":288.0,"raw_peak_contact_force":2.06903,"subtask_id":"reach_peg_side","tcp_end":[0.50007,0.1279,0.15661],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13691,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":448.0,"n_steps_budget":660.0,"object_pos_end":[0.50301,0.06748,0.0338],"object_pos_start":[0.50309,0.06748,0.0338],"object_to_goal_dist_end":0.14764,"object_to_goal_dist_start":0.14764,"object_z_max":0.0338,"peak_contact_force":0.54538,"phase_name":"align_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":448.0,"raw_peak_contact_force":0.5555,"subtask_id":"reach_peg_side","tcp_end":[0.49905,0.09469,0.07568],"tcp_start":[0.50007,0.1279,0.15661],"tcp_to_object_dist_end":0.0501,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50303,0.0675,0.0338],"object_pos_start":[0.50301,0.06748,0.0338],"object_to_goal_dist_end":0.14766,"object_to_goal_dist_start":0.14764,"object_z_max":0.0338,"peak_contact_force":0.54566,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.55081,"subtask_id":"push_to_goal","tcp_end":[0.49526,-0.06636,0.07083],"tcp_start":[0.49905,0.09469,0.07568],"tcp_to_object_dist_end":0.13911,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":320.0,"n_steps_budget":1000.0,"object_pos_end":[0.50304,0.06742,0.0338],"object_pos_start":[0.50303,0.0675,0.0338],"object_to_goal_dist_end":0.14758,"object_to_goal_dist_start":0.14766,"object_z_max":0.0338,"peak_contact_force":0.54778,"phase_name":"retract_away","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":320.0,"raw_peak_contact_force":0.5506,"subtask_id":"push_to_goal","tcp_end":[0.49946,0.16478,0.26489],"tcp_start":[0.49526,-0.06636,0.07083],"tcp_to_object_dist_end":0.25079,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.1145,"average_solve_count":131.0,"average_success_count":131.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_contact.contact_force_threshold":7.35986,"align_contact.contact_speed":0.06514,"approach_above.approach_speed":0.12349,"approach_above.approach_tol":0.0262,"push_channel.push_distance":0.18112,"push_channel.push_duration":19.17179,"push_channel.push_force_limit":41.54746,"push_channel.push_speed":0.1202,"retract_away.retract_speed":0.16006,"retract_away.retract_tol":0.05823},"optimized_scores":{"best_composite_score":-0.41453,"best_fitness_score":0.14547,"best_task_score":0.00063},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":251.0,"contact_point_centroid":[0.50354,0.11153,0.00934],"force_p95":0.73726,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.575,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.50262,0.18231,0.22496]},{"body_a":"peg","body_b":"channel_base_body","contact_count":911.0,"contact_point_centroid":[0.50367,0.11168,0.00941],"force_p95":0.60032,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64253,"mean_force":0.54409,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49669,0.05328,0.07222]},{"body_a":"peg","body_b":"channel_base_body","contact_count":425.0,"contact_point_centroid":[0.5036,0.11179,0.00939],"force_p95":0.60685,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64068,"mean_force":0.546,"phase_index":1.0,"phase_name":"align_contact","phase_type":"contact","tcp_position_centroid":[0.50193,0.15241,0.11624]},{"body_a":"peg","body_b":"channel_base_body","contact_count":287.0,"contact_point_centroid":[0.50367,0.11158,0.00941],"force_p95":0.59746,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.6251,"mean_force":0.54361,"phase_index":3.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.49727,0.06419,0.16417]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.4999,0.19932,0.29817]}],"total_contact_groups":5},"final_pose_error":0.04986,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50372,0.11167,0.03384],"final_tcp_position":[0.49971,0.16668,0.26291],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":2.06328,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":273.0,"n_steps_budget":840.0,"object_pos_end":[0.50374,0.11175,0.0339],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19188,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.48744,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":267.0,"raw_peak_contact_force":2.06328,"subtask_id":"reach_peg_side","tcp_end":[0.506,0.16661,0.15876],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13639,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":425.0,"n_steps_budget":870.0,"object_pos_end":[0.50366,0.11177,0.03379],"object_pos_start":[0.50374,0.11175,0.0339],"object_to_goal_dist_end":0.1919,"object_to_goal_dist_start":0.19188,"object_z_max":0.0339,"peak_contact_force":0.57458,"phase_name":"align_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":425.0,"raw_peak_contact_force":0.64068,"subtask_id":"reach_peg_side","tcp_end":[0.50025,0.13859,0.07683],"tcp_start":[0.506,0.16661,0.15876],"tcp_to_object_dist_end":0.05082,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":911.0,"n_steps_budget":960.0,"object_pos_end":[0.50372,0.11168,0.03379],"object_pos_start":[0.50366,0.11177,0.03379],"object_to_goal_dist_end":0.19182,"object_to_goal_dist_start":0.1919,"object_z_max":0.03394,"peak_contact_force":0.53166,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":911.0,"raw_peak_contact_force":0.64253,"subtask_id":"push_to_goal","tcp_end":[0.49649,-0.03463,0.07204],"tcp_start":[0.50025,0.13859,0.07683],"tcp_to_object_dist_end":0.1514,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":287.0,"n_steps_budget":1000.0,"object_pos_end":[0.50372,0.11167,0.03384],"object_pos_start":[0.50372,0.11168,0.03379],"object_to_goal_dist_end":0.1918,"object_to_goal_dist_start":0.19182,"object_z_max":0.03403,"peak_contact_force":0.53211,"phase_name":"retract_away","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":287.0,"raw_peak_contact_force":0.6251,"subtask_id":"push_to_goal","tcp_end":[0.49971,0.16668,0.26291],"tcp_start":[0.49649,-0.03463,0.07204],"tcp_to_object_dist_end":0.23561,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```