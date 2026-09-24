## Search State

- **Seed**: 1
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → descend → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | time_limit | pose_tolerance | 14 | -0.4785 | 0.11 | ❌ rejected |
| 5 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 11 | -0.1871 | 0.34 | ✅ accepted |
| 4 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 10 | -0.1244 | 0.23 | ❌ rejected |
| 3 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 11 | -0.4914 | 0.00 | ❌ rejected |
| 2 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 11 | -0.2299 | 0.15 | ❌ rejected |

**Proposal policy**: task_score is 0.11 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `9fd07833843a6ee28e14c5e2ce05f86547005983f45e63c41c77b8dac2024c0a`
- Frozen object start: [0.5009457299760205, 0.11603709570607482, 0.04]
- Frozen task target: [0.5009457299760205, -0.04396290429392519, 0.04]
- Goal object position: (0.5009457299760205, -0.04396290429392519, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5009457299760205, 0.11603709570607482, 0.04)
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
  frozen_object_start: [0.5009, 0.116, 0.04]
  frozen_task_target: [0.5009, -0.044, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5009457299760205, 0.11603709570607482, 0.04]}
  frozen_targets: {'channel_exit': [0.5009457299760205, -0.04396290429392519, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: 9fd07833843a6ee28e14c5e2ce05f86547005983f45e63c41c77b8dac2024c0a

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
| `object` | offset from object initial position (0.5009457299760205, 0.11603709570607482, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5009457299760205, -0.04396290429392519, 0.04) | final destination targets |
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

## Current Skill (Q=-0.478) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: reach_pre_contact
  anchor: object
  offset:
  - 0.0
  - 0.05
  - 0.1
  weight: 0.3
- id: push_channel
  metric: goal_progress
  weight: 0.7
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.05
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.3
      binds_to:
      - path: generator.speed
        mode: replace
    approach_y_offset:
      type: scalar
      range:
      - 0.03
      - 0.07
      default: 0.05
      binds_to:
      - path: target.offset.y
        mode: replace
  subtask_id: reach_pre_contact
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    descend_force_threshold:
      type: scalar
      range:
      - 5.0
      - 30.0
      default: 15.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    descend_speed:
      type: scalar
      range:
      - 0.05
      - 0.25
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
    descend_z_offset:
      type: scalar
      range:
      - -0.01
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_pre_contact
- id: push_1
  type: push
  generator: impedance_motion
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
      distance: 0.18
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.12
      - 0.25
      default: 0.18
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_max_time:
      type: scalar
      range:
      - 2.0
      - 8.0
      default: 5.0
      binds_to:
      - path: duration.max_time
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
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
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.01
  subtask_id: push_channel
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
    - 0.15
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.1
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    retract_speed:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.3
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: push_channel

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.05, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - approach_y_offset: status=consumed; consumers=target.offset.y (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - descend_z_offset: status=consumed; consumers=target.offset.z (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.18, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_max_time: status=consumed; consumers=duration.max_time (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_guard, when=during_phase, predicate=force_below, on_failure=retry, threshold=35.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.01]
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.15], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_height: status=consumed; consumers=target.offset.z (replace)
    - retract_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: -0.478
- **task_score** (E): 0.114
- **fitness_score**: 0.112  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.790

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1842 |
| descend_1 | 1.00 | 1.00 | 0.1092 |
| align_1 | 1.00 | 1.00 | 0.0307 |
| push_1 | 0.00 | 1.00 | 0.0002 |
| retract_1 | 1.00 | 1.00 | 0.1791 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.478, 0.143, 0.128) | (0.483, 0.080, 0.040)→(0.497, 0.080, 0.034) | 0.161→0.160 | 1.00 / 1.000 | 0.530 | 2.857 |
| descend_1 | descend | 1.00 / force_exceeded | (0.478, 0.143, 0.128)→(0.483, 0.059, 0.060) | (0.497, 0.080, 0.034)→(0.497, 0.079, 0.034) | 0.160→0.160 | 1.00 / 2.000 | 26.955 | 26.955 |
| align_1 | align | 1.00 / step_budget | (0.483, 0.059, 0.060)→(0.494, 0.034, 0.047) | (0.497, 0.079, 0.034)→(0.503, 0.072, 0.037) | 0.160→0.152 | 1.00 / 1.667 | 61.770 | 393.299 |
| push_1 | push | 0.00 / guard_failure | (0.493, 0.031, 0.045)→(0.493, 0.030, 0.045) | (0.503, 0.072, 0.037)→(0.501, 0.075, 0.038) | 0.152→0.155 | 1.00 / 2.000 | 42.637 | 58.007 |
| retract_1 | retract | 1.00 / step_budget | (0.493, 0.030, 0.045)→(0.491, 0.030, 0.224) | (0.501, 0.074, 0.038)→(0.498, 0.057, 0.028) | 0.154→0.138 | 1.00 / 1.000 | 0.580 | 140.985 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.216
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.216
- phase_score: 0.120
- phase_breakdown.push_channel_score: 0.120
- phase_breakdown.reach_pre_contact_score: 0.122

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.159
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.216
- **Median Q (composite search score)**: -0.449
- **K-run variance**: 0.0030
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.299


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `a904e23429ae963dd2788b3e8d0575d9ce341e1daddfe013fbb1224c3e0c850e`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `6bee39a4c127c6d39ee1365e3969a50bb09484f7e2580b1a3dc4d8c4ae20213b`; realized-scene SHA-256: `9fd07833843a6ee28e14c5e2ce05f86547005983f45e63c41c77b8dac2024c0a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50095,0.11604,0.04]},{"name":"goal","value":[0.50095,-0.04396,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.50095,0.11604,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.50095,-0.04396,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.05195,"average_solve_count":77.0,"average_success_count":77.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.15465,"approach_1.approach_height":0.06282,"approach_1.approach_speed":0.30663,"approach_1.approach_x_offset":0.00353,"approach_1.approach_y_offset":0.04865,"descend_1.descend_force_threshold":17.23088,"descend_1.descend_speed":0.16613,"descend_1.descend_x_offset":-0.0123,"push_1.force_guard_threshold":34.37843,"push_1.push_distance":0.1802,"push_1.push_max_time":6.38265,"push_1.push_speed":0.07839,"retract_1.retract_height":0.21662,"retract_1.retract_speed":0.29016},"optimized_scores":{"best_composite_score":-0.43144,"best_fitness_score":0.15856,"best_task_score":0.21597},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":88.0,"contact_point_centroid":[0.507,0.09985,0.00863],"force_p95":151.25877,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":156.13798,"mean_force":124.5645,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49517,0.08639,0.05417]},{"body_a":"attachment","body_b":"peg","contact_count":88.0,"contact_point_centroid":[0.50152,0.09473,0.05516],"force_p95":150.74648,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":155.70714,"mean_force":123.97449,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49517,0.08639,0.05417]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.50616,0.10416,0.00851],"force_p95":64.13688,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":65.08987,"mean_force":55.61012,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50074,0.07024,0.04705]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.50265,0.0807,0.04882],"force_p95":63.95406,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":64.88842,"mean_force":55.34491,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50074,0.07024,0.04705]},{"body_a":"peg","body_b":"channel_base_body","contact_count":550.0,"contact_point_centroid":[0.50095,0.09238,0.00886],"force_p95":1.26616,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":63.37059,"mean_force":1.46314,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49812,0.06915,0.14013]},{"body_a":"attachment","body_b":"peg","contact_count":31.0,"contact_point_centroid":[0.5023,0.0795,0.04921],"force_p95":35.83952,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":63.23305,"mean_force":15.43793,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49972,0.06858,0.04853]},{"body_a":"peg","body_b":"channel_base_body","contact_count":366.0,"contact_point_centroid":[0.50083,0.11593,0.00944],"force_p95":0.61409,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":28.19908,"mean_force":0.75852,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49443,0.1335,0.08506]},{"body_a":"attachment","body_b":"peg","contact_count":6.0,"contact_point_centroid":[0.50189,0.0987,0.05875],"force_p95":23.68672,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":27.56207,"mean_force":13.22648,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49003,0.09915,0.06032]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":4.0,"contact_point_centroid":[0.52501,0.0935,0.05836],"force_p95":17.36713,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.43543,"mean_force":16.74964,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50027,0.07336,0.04869]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":12.0,"contact_point_centroid":[0.52509,0.10187,0.02413],"force_p95":5.56513,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.85679,"mean_force":2.00602,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49785,0.06924,0.1463]},{"body_a":"peg","body_b":"channel_base_body","contact_count":484.0,"contact_point_centroid":[0.50085,0.116,0.00937],"force_p95":0.62382,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.56061,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49984,0.18243,0.20277]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":33.0,"contact_point_centroid":[0.47489,0.09302,0.05626],"force_p95":0.49339,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.98728,"mean_force":0.14775,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49756,0.06908,0.08193]}],"total_contact_groups":12},"final_pose_error":0.01924,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50154,0.08148,0.02413],"final_tcp_position":[0.49869,0.06934,0.24427],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":156.13798,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":500.0,"n_steps_budget":600.0,"object_pos_end":[0.50095,0.11614,0.03393],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19623,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.49617,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":484.0,"raw_peak_contact_force":1.92055,"subtask_id":"reach_pre_contact","tcp_end":[0.50102,0.16616,0.11195],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09268,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":366.0,"n_steps_budget":600.0,"object_pos_end":[0.50092,0.11598,0.0339],"object_pos_start":[0.50095,0.11614,0.03393],"object_to_goal_dist_end":0.19607,"object_to_goal_dist_start":0.19623,"object_z_max":0.03401,"peak_contact_force":28.19908,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":372.0,"raw_peak_contact_force":28.19908,"subtask_id":"reach_pre_contact","tcp_end":[0.49,0.09852,0.05995],"tcp_start":[0.50102,0.16616,0.11195],"tcp_to_object_dist_end":0.0332,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":88.0,"n_steps_budget":600.0,"object_pos_end":[0.50632,0.10453,0.03772],"object_pos_start":[0.50092,0.11598,0.0339],"object_to_goal_dist_end":0.18465,"object_to_goal_dist_start":0.19607,"object_z_max":0.03763,"peak_contact_force":96.61751,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":180.0,"raw_peak_contact_force":156.13798,"subtask_id":"push_channel","tcp_end":[0.50078,0.07057,0.04722],"tcp_start":[0.49,0.09852,0.05995],"tcp_to_object_dist_end":0.03569,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50619,0.10437,0.03782],"object_pos_start":[0.50632,0.10453,0.03772],"object_to_goal_dist_end":0.18448,"object_to_goal_dist_start":0.18465,"object_z_max":0.03792,"peak_contact_force":65.08987,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":6.0,"raw_peak_contact_force":65.08987,"subtask_id":"push_channel","tcp_end":[0.50063,0.06968,0.0468],"tcp_start":[0.5007,0.06993,0.04691],"tcp_to_object_dist_end":0.03626,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":557.0,"n_steps_budget":600.0,"object_pos_end":[0.50154,0.08148,0.02413],"object_pos_start":[0.5059,0.10422,0.03802],"object_to_goal_dist_end":0.16227,"object_to_goal_dist_start":0.18432,"object_z_max":0.04075,"peak_contact_force":0.5603,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":626.0,"raw_peak_contact_force":63.37059,"subtask_id":"push_channel","tcp_end":[0.49869,0.06934,0.24427],"tcp_start":[0.50063,0.06968,0.0468],"tcp_to_object_dist_end":0.2205,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `8416ac3bebb4dbec2abbf751596843a33db171fd8d70765023f3b940d846bd0c`; realized-scene SHA-256: `2a92d231da5879af7af8916eb4c7dff00148227e84220c4d9643d9841dc77ee7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48093,0.06388,0.04]},{"name":"goal","value":[0.48093,-0.09612,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48093,0.06388,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48093,-0.09612,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.1625,"average_solve_count":80.0,"average_success_count":80.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.13207,"approach_1.approach_height":0.08494,"approach_1.approach_speed":0.26202,"approach_1.approach_x_offset":-0.00211,"approach_1.approach_y_offset":0.06874,"descend_1.descend_force_threshold":29.8743,"descend_1.descend_speed":0.16141,"descend_1.descend_x_offset":-0.00958,"push_1.force_guard_threshold":33.11917,"push_1.push_distance":0.21514,"push_1.push_max_time":8.01006,"push_1.push_speed":0.046,"retract_1.retract_height":0.21414,"retract_1.retract_speed":0.31447},"optimized_scores":{"best_composite_score":-0.44888,"best_fitness_score":0.14112,"best_task_score":0.12721},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":37.0,"contact_point_centroid":[0.47499,0.03233,0.05993],"force_p95":492.87141,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":507.03229,"mean_force":376.53837,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.4833,0.04015,0.05874]},{"body_a":"peg","body_b":"channel_base_body","contact_count":109.0,"contact_point_centroid":[0.50207,0.04773,0.00899],"force_p95":140.30927,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":147.38169,"mean_force":91.741,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.48651,0.03437,0.056]},{"body_a":"attachment","body_b":"peg","contact_count":109.0,"contact_point_centroid":[0.49329,0.0429,0.05649],"force_p95":139.94213,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":146.97233,"mean_force":91.26001,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.48651,0.03437,0.056]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.49508,0.02786,0.04898],"force_p95":65.76686,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":66.25866,"mean_force":55.1634,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49284,0.01735,0.04745]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.50135,0.05196,0.0087],"force_p95":65.70281,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":66.18077,"mean_force":55.34894,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49284,0.01735,0.04745]},{"body_a":"peg","body_b":"channel_base_body","contact_count":549.0,"contact_point_centroid":[0.4986,0.03776,0.00879],"force_p95":1.31891,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":59.60078,"mean_force":1.30576,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49004,0.01657,0.13977]},{"body_a":"attachment","body_b":"peg","contact_count":29.0,"contact_point_centroid":[0.4943,0.02685,0.04912],"force_p95":30.73335,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":59.44328,"mean_force":13.10009,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49146,0.01594,0.04854]},{"body_a":"peg","body_b":"channel_base_body","contact_count":464.0,"contact_point_centroid":[0.49499,0.0637,0.0094],"force_p95":0.55064,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":30.49885,"mean_force":0.80125,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47723,0.09219,0.09662]},{"body_a":"attachment","body_b":"peg","contact_count":5.0,"contact_point_centroid":[0.4913,0.0456,0.05868],"force_p95":29.3598,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.9289,"mean_force":23.65731,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.4795,0.04429,0.0603]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":15.0,"contact_point_centroid":[0.52512,0.05019,0.0247],"force_p95":6.77712,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.30234,"mean_force":1.62913,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48987,0.01668,0.13843]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":36.0,"contact_point_centroid":[0.47488,0.03496,0.05257],"force_p95":1.25194,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.65083,"mean_force":0.38675,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48982,0.01641,0.0865]},{"body_a":"peg","body_b":"channel_base_body","contact_count":445.0,"contact_point_centroid":[0.49544,0.06401,0.00936],"force_p95":0.5969,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.56462,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48768,0.1669,0.21184]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4992,0.19834,0.29611]}],"total_contact_groups":13},"final_pose_error":0.01889,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49673,0.02894,0.02415],"final_tcp_position":[0.49061,0.01669,0.2425],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":507.03229,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":472.0,"n_steps_budget":600.0,"object_pos_end":[0.49494,0.06376,0.03394],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14398,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.55009,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":473.0,"raw_peak_contact_force":2.44546,"subtask_id":"reach_pre_contact","tcp_end":[0.47756,0.13691,0.1337],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12493,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":464.0,"n_steps_budget":660.0,"object_pos_end":[0.49508,0.06332,0.03418],"object_pos_start":[0.49494,0.06376,0.03394],"object_to_goal_dist_end":0.14352,"object_to_goal_dist_start":0.14398,"object_z_max":0.03413,"peak_contact_force":30.49885,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":469.0,"raw_peak_contact_force":30.49885,"subtask_id":"reach_pre_contact","tcp_end":[0.47958,0.04374,0.05996],"tcp_start":[0.47756,0.13691,0.1337],"tcp_to_object_dist_end":0.03589,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":109.0,"n_steps_budget":600.0,"object_pos_end":[0.50146,0.05199,0.03812],"object_pos_start":[0.49508,0.06332,0.03418],"object_to_goal_dist_end":0.13201,"object_to_goal_dist_start":0.14352,"object_z_max":0.03804,"peak_contact_force":88.23008,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":255.0,"raw_peak_contact_force":507.03229,"subtask_id":"push_channel","tcp_end":[0.49301,0.01767,0.04765],"tcp_start":[0.47958,0.04374,0.05996],"tcp_to_object_dist_end":0.0366,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50129,0.05183,0.03821],"object_pos_start":[0.50146,0.05199,0.03812],"object_to_goal_dist_end":0.13185,"object_to_goal_dist_start":0.13201,"object_z_max":0.03829,"peak_contact_force":61.40116,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":6.0,"raw_peak_contact_force":66.25866,"subtask_id":"push_channel","tcp_end":[0.49257,0.01681,0.04715],"tcp_start":[0.49268,0.01705,0.04727],"tcp_to_object_dist_end":0.03718,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":557.0,"n_steps_budget":600.0,"object_pos_end":[0.49673,0.02894,0.02415],"object_pos_start":[0.50106,0.0517,0.03838],"object_to_goal_dist_end":0.11014,"object_to_goal_dist_start":0.13172,"object_z_max":0.04075,"peak_contact_force":0.64491,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":629.0,"raw_peak_contact_force":59.60078,"subtask_id":"push_channel","tcp_end":[0.49061,0.01669,0.2425],"tcp_start":[0.49257,0.01681,0.04715],"tcp_to_object_dist_end":0.21878,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `0188121de1b8142d5ff7a7406b62c43adf6da5520b986a997e46ef53b7d11bf9`; realized-scene SHA-256: `990d03f436076caee02f5d9d8b3b9b0b3759564b7644084e4eac46818881d834`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.46685,0.05894,0.04]},{"name":"goal","value":[0.46685,-0.10106,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.46685,0.05894,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.46685,-0.10106,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.16471,"average_solve_count":85.0,"average_success_count":85.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.19008,"approach_1.approach_height":0.09119,"approach_1.approach_speed":0.34563,"approach_1.approach_x_offset":-0.0105,"approach_1.approach_y_offset":0.06206,"descend_1.descend_force_threshold":16.47744,"descend_1.descend_speed":0.15781,"descend_1.descend_x_offset":-1e-05,"push_1.force_guard_threshold":35.67884,"push_1.push_distance":0.1736,"push_1.push_max_time":7.96609,"push_1.push_speed":0.10157,"retract_1.retract_height":0.15953,"retract_1.retract_speed":0.4458},"optimized_scores":{"best_composite_score":-0.55513,"best_fitness_score":0.03487,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.47498,0.02398,0.05988],"force_p95":489.60626,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":516.7258,"mean_force":402.30493,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.48335,0.0317,0.05862]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":58.0,"contact_point_centroid":[0.47496,0.00471,0.05088],"force_p95":298.04855,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":299.98308,"mean_force":179.5598,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48679,0.00473,0.04907]},{"body_a":"peg","body_b":"channel_base_body","contact_count":98.0,"contact_point_centroid":[0.50365,0.04388,0.00924],"force_p95":127.12509,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":139.76693,"mean_force":53.65057,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.48566,0.02728,0.05595]},{"body_a":"attachment","body_b":"peg","contact_count":81.0,"contact_point_centroid":[0.49235,0.03803,0.05768],"force_p95":126.83537,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":139.34551,"mean_force":64.3675,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.48486,0.02944,0.0575]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":10.0,"contact_point_centroid":[0.47499,0.00589,0.04404],"force_p95":38.68376,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":42.6717,"mean_force":26.42316,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48685,0.00591,0.04223]},{"body_a":"peg","body_b":"channel_base_body","contact_count":495.0,"contact_point_centroid":[0.49398,0.05895,0.00939],"force_p95":0.55039,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.16731,"mean_force":0.58972,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.46665,0.08266,0.09999]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.49047,0.04107,0.05882],"force_p95":21.46665,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.46665,"mean_force":21.46665,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47985,0.03571,0.06033]},{"body_a":"peg","body_b":"channel_base_body","contact_count":449.0,"contact_point_centroid":[0.4945,0.05889,0.00935],"force_p95":0.59162,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.57879,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47683,0.16111,0.21437]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49829,0.19759,0.29485]},{"body_a":"peg","body_b":"channel_base_body","contact_count":541.0,"contact_point_centroid":[0.49853,0.06096,0.00953],"force_p95":0.63963,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.19838,"mean_force":0.53891,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48453,0.00488,0.11174]},{"body_a":"peg","body_b":"channel_base_body","contact_count":67.0,"contact_point_centroid":[0.49866,0.0749,0.0096],"force_p95":0.75127,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.82461,"mean_force":0.54113,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4876,0.00935,0.04311]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":19.0,"contact_point_centroid":[0.47465,0.07488,0.05996],"force_p95":0.61674,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.74432,"mean_force":0.17428,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48699,0.0073,0.04244]}],"total_contact_groups":12},"final_pose_error":0.01518,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49716,0.06184,0.03498],"final_tcp_position":[0.48428,0.00494,0.1867],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":516.7258,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":478.0,"n_steps_budget":600.0,"object_pos_end":[0.49419,0.05905,0.03386],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.1393,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54364,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":484.0,"raw_peak_contact_force":4.20518,"subtask_id":"reach_pre_contact","tcp_end":[0.45688,0.12615,0.13956],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13064,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":495.0,"n_steps_budget":690.0,"object_pos_end":[0.49427,0.05881,0.03394],"object_pos_start":[0.49419,0.05905,0.03386],"object_to_goal_dist_end":0.13906,"object_to_goal_dist_start":0.1393,"object_z_max":0.03392,"peak_contact_force":22.16731,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":496.0,"raw_peak_contact_force":22.16731,"subtask_id":"reach_pre_contact","tcp_end":[0.47989,0.03555,0.0602],"tcp_start":[0.45688,0.12615,0.13956],"tcp_to_object_dist_end":0.03792,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":98.0,"n_steps_budget":600.0,"object_pos_end":[0.50159,0.05898,0.03651],"object_pos_start":[0.49427,0.05881,0.03394],"object_to_goal_dist_end":0.13903,"object_to_goal_dist_start":0.13906,"object_z_max":0.037,"peak_contact_force":0.46193,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":214.0,"raw_peak_contact_force":516.7258,"subtask_id":"push_channel","tcp_end":[0.48956,0.01426,0.0455],"tcp_start":[0.47989,0.03555,0.0602],"tcp_to_object_dist_end":0.04717,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":67.0,"n_steps_budget":1000.0,"object_pos_end":[0.49628,0.06734,0.03832],"object_pos_start":[0.50159,0.05898,0.03651],"object_to_goal_dist_end":0.14739,"object_to_goal_dist_start":0.13903,"object_z_max":0.03872,"peak_contact_force":1.42026,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":96.0,"raw_peak_contact_force":42.6717,"subtask_id":"push_channel","tcp_end":[0.48684,0.00499,0.04212],"tcp_start":[0.48687,0.00507,0.04216],"tcp_to_object_dist_end":0.06317,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.49716,0.06184,0.03498],"object_pos_start":[0.49651,0.06702,0.03818],"object_to_goal_dist_end":0.14196,"object_to_goal_dist_start":0.14707,"object_z_max":0.03818,"peak_contact_force":0.53584,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":599.0,"raw_peak_contact_force":299.98308,"subtask_id":"push_channel","tcp_end":[0.48428,0.00494,0.1867],"tcp_start":[0.48684,0.00499,0.04212],"tcp_to_object_dist_end":0.16255,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```