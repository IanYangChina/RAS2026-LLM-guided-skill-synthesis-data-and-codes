## Search State

- **Seed**: 9
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 11 | 0.1988 | 0.25 | ❌ rejected |
| 11 | approach → descend → contact → align → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | position_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 11 | -0.1731 | 0.03 | ❌ rejected |
| 10 | approach → descend → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 9 | -0.0973 | 0.06 | ❌ rejected |
| 9 | approach → descend → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 9 | 0.3200 | 0.56 | ✅ accepted |
| 8 | approach → descend → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 10 | -0.0222 | 0.32 | ❌ rejected |

**Proposal policy**: task_score is 0.25 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `a0d7ea14565b0a67e86de15fa43f3773b761884db645527685cd53e0fd95aeb9`
- Frozen object start: [0.5296199363176067, 0.06294537672700443, 0.04]
- Frozen task target: [0.5296199363176067, -0.09705462327299558, 0.04]
- Goal object position: (0.5296199363176067, -0.09705462327299558, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5296199363176067, 0.06294537672700443, 0.04)
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
  frozen_object_start: [0.5296, 0.0629, 0.04]
  frozen_task_target: [0.5296, -0.0971, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5296199363176067, 0.06294537672700443, 0.04]}
  frozen_targets: {'channel_exit': [0.5296199363176067, -0.09705462327299558, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: a0d7ea14565b0a67e86de15fa43f3773b761884db645527685cd53e0fd95aeb9

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
| `object` | offset from object initial position (0.5296199363176067, 0.06294537672700443, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5296199363176067, -0.09705462327299558, 0.04) | final destination targets |
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

## Current Skill (Q=0.199) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: reach_peg
  anchor: object
  offset:
  - 0.0
  - 0.05
  - 0.16
  weight: 0.2
- id: align_to_peg
  anchor: object
  offset:
  - 0.0
  - 0.02
  - 0.0
  weight: 0.3
- id: push_through
  target_entity: object
  metric: goal_progress
  weight: 0.5
phases:
- id: approach_prep
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
    - 0.16
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.12
      - 0.2
      default: 0.16
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_peg
- id: descend_to_peg_height
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.05
    - 0.0
    tolerance: 0.015
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: align_to_peg
- id: lateral_contact
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.02
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 1.0
      - 8.0
      default: 3.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    contact_speed:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
    contact_x_offset:
      type: scalar
      range:
      - -0.03
      - 0.03
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: replace
  guards:
  - id: force_high
    when: during_phase
    predicate: force_below
    threshold: 60.0
    on_failure: continue
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.005
    - 0.0
  subtask_id: align_to_peg
- id: push_channel
  type: push
  generator: linear_cartesian
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
      distance: 0.22
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
      - 0.18
      - 0.26
      default: 0.22
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_lateral_offset:
      type: scalar
      range:
      - -0.03
      - 0.03
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: push_through

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_prep** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.05, 0.16], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_peg_height** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.05, 0.0], tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **lateral_contact** (`contact`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.02, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - contact_speed: status=consumed; consumers=generator.speed (replace)
    - contact_x_offset: status=consumed; consumers=target.offset.x (replace)
  - guards:
    - id=force_high, when=during_phase, predicate=force_below, on_failure=continue, threshold=60.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.005, 0.0]
- **push_channel** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.22, mode=add_to_offset, sign=positive}, tolerance=0.03
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_lateral_offset: status=consumed; consumers=target.offset.x (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.0]

## Design Metrics

- **Composite score**: 0.199
- **task_score** (E): 0.255
- **fitness_score**: 0.526  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.283
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.610

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_prep | 1.00 | 1.00 | 0.1178 |
| descend_to_peg_height | 1.00 | 1.00 | 0.1528 |
| contact_peg | 1.00 | 1.00 | 0.0285 |
| push_channel | 0.67 | 1.00 | 0.1171 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_prep | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.508, 0.130, 0.209) | (0.512, 0.067, 0.040)→(0.502, 0.067, 0.034) | 0.150→0.147 | 1.00 / 1.000 | 0.563 | 4.034 |
| descend_to_peg_height | descend | 1.00 / step_budget | (0.508, 0.130, 0.209)→(0.499, 0.117, 0.058) | (0.502, 0.067, 0.034)→(0.502, 0.067, 0.034) | 0.147→0.147 | 1.00 / 1.000 | 0.554 | 0.594 |
| contact_peg | contact | 1.00 / force_exceeded | (0.499, 0.117, 0.058)→(0.505, 0.094, 0.043) | (0.502, 0.067, 0.034)→(0.502, 0.065, 0.034) | 0.147→0.145 | 1.00 / 2.333 | 13.109 | 5.880 |
| push_channel | push | 0.67 / time_limit | (0.505, 0.094, 0.043)→(0.500, -0.022, 0.047) | (0.502, 0.065, 0.034)→(0.504, -0.051, 0.037) | 0.145→0.030 | 1.00 / 2.667 | 26.552 | 30.929 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.805
- alignment_error: None
- force_efficiency: 0.392
- terminal_score: 0.332
- phase_score: 0.747
- phase_breakdown.push_through_score: 0.884
- phase_breakdown.align_to_peg_score: 0.622
- phase_breakdown.reach_peg_score: 0.594

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.581
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.332
- **Median Q (composite search score)**: 0.173
- **K-run variance**: 0.0061
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Parameters at upper bound**: push_channel.push_speed
- **Final σ (mean)**: 0.355


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `bf8103833c1e96f48e87b3ce39b3b3bf17e268470bd7b5c037546fb78b5150b8`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `98954a34ee744fa939070f7dadee8a411de43cdcfeddcf3b4bfc5c3a4c536020`; realized-scene SHA-256: `a0d7ea14565b0a67e86de15fa43f3773b761884db645527685cd53e0fd95aeb9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.52962,0.06295,0.04]},{"name":"goal","value":[0.52962,-0.09705,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.52962,0.06295,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.52962,-0.09705,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.38889,"average_solve_count":144.0,"average_success_count":144.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_prep.approach_height":0.16948,"approach_prep.approach_speed":0.10905,"contact_peg.contact_force_threshold":5.55264,"contact_peg.contact_speed":0.05082,"contact_peg.contact_x_offset":0.01091,"descend_to_peg_height.descend_speed":0.05398,"push_channel.push_distance":0.22003,"push_channel.push_lateral_offset":-0.00792,"push_channel.push_max_time":4.79957,"push_channel.push_speed":0.08,"push_channel.push_z_offset":0.01023},"optimized_scores":{"best_composite_score":0.30467,"best_fitness_score":0.58134,"best_task_score":0.33248},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":843.0,"contact_point_centroid":[0.50505,0.00955,0.04323],"force_p95":26.04509,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":30.40554,"mean_force":9.68257,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50291,0.02117,0.04294]},{"body_a":"peg","body_b":"channel_base_body","contact_count":827.0,"contact_point_centroid":[0.50639,-0.01466,0.00985],"force_p95":26.18616,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":28.71229,"mean_force":10.12825,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50303,0.02297,0.0429]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":299.0,"contact_point_centroid":[0.52503,0.00498,0.02803],"force_p95":6.51764,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.28141,"mean_force":2.40769,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50322,0.03206,0.04227]},{"body_a":"peg","body_b":"channel_base_body","contact_count":350.0,"contact_point_centroid":[0.50603,0.06292,0.00938],"force_p95":0.55275,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.67961,"mean_force":0.56518,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50535,0.1023,0.04891]},{"body_a":"attachment","body_b":"peg","contact_count":5.0,"contact_point_centroid":[0.50763,0.08086,0.04398],"force_p95":4.4706,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.2531,"mean_force":1.39694,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50869,0.09279,0.04385]},{"body_a":"peg","body_b":"channel_base_body","contact_count":195.0,"contact_point_centroid":[0.50513,0.06296,0.00931],"force_p95":0.75948,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.61588,"phase_index":0.0,"phase_name":"approach_prep","phase_type":"approach","tcp_position_centroid":[0.51168,0.16051,0.25519]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_prep","phase_type":"approach","tcp_position_centroid":[0.50085,0.19609,0.29539]},{"body_a":"peg","body_b":"channel_base_body","contact_count":398.0,"contact_point_centroid":[0.50607,0.06292,0.00938],"force_p95":0.55177,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55664,"mean_force":0.54659,"phase_index":1.0,"phase_name":"descend_to_peg_height","phase_type":"descend","tcp_position_centroid":[0.51281,0.12068,0.13983]}],"total_contact_groups":8},"final_pose_error":0.09181,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50693,-0.06587,0.03464],"final_tcp_position":[0.50205,-0.03601,0.04686],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":30.40554,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":223.0,"n_steps_budget":750.0,"object_pos_end":[0.50599,0.06304,0.0338],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.1433,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.53905,"phase_name":"approach_prep","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":229.0,"raw_peak_contact_force":3.88411,"subtask_id":"reach_peg","tcp_end":[0.52237,0.12775,0.22021],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.198,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":398.0,"n_steps_budget":1000.0,"object_pos_end":[0.50593,0.06301,0.0338],"object_pos_start":[0.50599,0.06304,0.0338],"object_to_goal_dist_end":0.14326,"object_to_goal_dist_start":0.1433,"object_z_max":0.03381,"peak_contact_force":0.5473,"phase_name":"descend_to_peg_height","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":398.0,"raw_peak_contact_force":0.55664,"subtask_id":"align_to_peg","tcp_end":[0.50441,0.1139,0.05852],"tcp_start":[0.52237,0.12775,0.22021],"tcp_to_object_dist_end":0.0566,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":350.0,"n_steps_budget":600.0,"object_pos_end":[0.5059,0.06275,0.03389],"object_pos_start":[0.50593,0.06301,0.0338],"object_to_goal_dist_end":0.143,"object_to_goal_dist_start":0.14326,"object_z_max":0.03385,"peak_contact_force":5.67961,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":355.0,"raw_peak_contact_force":5.67961,"subtask_id":"align_to_peg","tcp_end":[0.50883,0.09249,0.0437],"tcp_start":[0.50441,0.1139,0.05852],"tcp_to_object_dist_end":0.03145,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50693,-0.06587,0.03464],"object_pos_start":[0.5059,0.06275,0.03389],"object_to_goal_dist_end":0.01662,"object_to_goal_dist_start":0.143,"object_z_max":0.04038,"peak_contact_force":20.997,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1969.0,"raw_peak_contact_force":30.40554,"subtask_id":"push_through","tcp_end":[0.50205,-0.03601,0.04686],"tcp_start":[0.50883,0.09249,0.0437],"tcp_to_object_dist_end":0.03263,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `cae0d95026bac46aa2e5d95cffd531753a79751757c4f25fa56c1ec6e19c2175`; realized-scene SHA-256: `11c1f773d01ee1d435c5ecc0d1531095d6f84a2c0ab26c3ff2560d4c62fcd41a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53648,0.05661,0.04]},{"name":"goal","value":[0.53648,-0.10339,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.53648,0.05661,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.53648,-0.10339,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.37363,"average_solve_count":182.0,"average_success_count":182.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_prep.approach_height":0.15365,"approach_prep.approach_speed":0.19313,"contact_peg.contact_force_threshold":8.17908,"contact_peg.contact_speed":0.05049,"contact_peg.contact_x_offset":0.00272,"descend_to_peg_height.descend_speed":0.03091,"push_channel.push_distance":0.22093,"push_channel.push_lateral_offset":0.01007,"push_channel.push_max_time":2.32016,"push_channel.push_speed":0.07882,"push_channel.push_z_offset":0.01694},"optimized_scores":{"best_composite_score":0.11846,"best_fitness_score":0.54664,"best_task_score":0.23555},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":827.0,"contact_point_centroid":[0.50573,0.00056,0.04446],"force_p95":18.90569,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":47.92009,"mean_force":7.741,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50414,0.01237,0.04265]},{"body_a":"peg","body_b":"channel_base_body","contact_count":29.0,"contact_point_centroid":[0.50698,-0.10041,0.04294],"force_p95":32.89554,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":37.14271,"mean_force":26.35274,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50735,-0.04154,0.04751]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":574.0,"contact_point_centroid":[0.52506,-0.00419,0.03188],"force_p95":6.33545,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":25.71028,"mean_force":2.17033,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50349,0.02624,0.04154]},{"body_a":"peg","body_b":"channel_base_body","contact_count":779.0,"contact_point_centroid":[0.50629,-0.02697,0.00989],"force_p95":16.16131,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.4881,"mean_force":7.24396,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50416,0.01308,0.04265]},{"body_a":"peg","body_b":"channel_base_body","contact_count":409.0,"contact_point_centroid":[0.50606,0.0522,0.00949],"force_p95":4.60475,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.17485,"mean_force":1.27595,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50347,0.09318,0.04746]},{"body_a":"attachment","body_b":"peg","contact_count":91.0,"contact_point_centroid":[0.50526,0.07212,0.04442],"force_p95":5.70469,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.89535,"mean_force":3.47893,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50417,0.08404,0.04274]},{"body_a":"peg","body_b":"channel_base_body","contact_count":214.0,"contact_point_centroid":[0.50542,0.05669,0.00932],"force_p95":0.71661,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.62091,"phase_index":0.0,"phase_name":"approach_prep","phase_type":"approach","tcp_position_centroid":[0.51501,0.15683,0.24703]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"approach_prep","phase_type":"approach","tcp_position_centroid":[0.50123,0.19555,0.2943]},{"body_a":"peg","body_b":"channel_base_body","contact_count":365.0,"contact_point_centroid":[0.50613,0.05663,0.00938],"force_p95":0.60278,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63933,"mean_force":0.5464,"phase_index":1.0,"phase_name":"descend_to_peg_height","phase_type":"descend","tcp_position_centroid":[0.51653,0.11409,0.13255]}],"total_contact_groups":9},"final_pose_error":0.09763,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.507,-0.07048,0.03948],"final_tcp_position":[0.50752,-0.04251,0.04771],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":47.92009,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":243.0,"n_steps_budget":600.0,"object_pos_end":[0.50615,0.05658,0.03377],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.13686,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":0.60057,"phase_name":"approach_prep","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":251.0,"raw_peak_contact_force":4.44541,"subtask_id":"reach_peg","tcp_end":[0.52851,0.12082,0.20511],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.18435,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":365.0,"n_steps_budget":1000.0,"object_pos_end":[0.50616,0.05663,0.03379],"object_pos_start":[0.50615,0.05658,0.03377],"object_to_goal_dist_end":0.13691,"object_to_goal_dist_start":0.13686,"object_z_max":0.03381,"peak_contact_force":0.54499,"phase_name":"descend_to_peg_height","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":365.0,"raw_peak_contact_force":0.63933,"subtask_id":"align_to_peg","tcp_end":[0.50544,0.10756,0.05837],"tcp_start":[0.52851,0.12082,0.20511],"tcp_to_object_dist_end":0.05656,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":414.0,"n_steps_budget":600.0,"object_pos_end":[0.50698,0.05189,0.03526],"object_pos_start":[0.50616,0.05663,0.03379],"object_to_goal_dist_end":0.13216,"object_to_goal_dist_start":0.13691,"object_z_max":0.03531,"peak_contact_force":27.8615,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":500.0,"raw_peak_contact_force":6.17485,"subtask_id":"align_to_peg","tcp_end":[0.50447,0.08165,0.0416],"tcp_start":[0.50544,0.10756,0.05837],"tcp_to_object_dist_end":0.03053,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":995.0,"n_steps_budget":1000.0,"object_pos_end":[0.507,-0.07048,0.03948],"object_pos_start":[0.50698,0.05189,0.03526],"object_to_goal_dist_end":0.01183,"object_to_goal_dist_start":0.13216,"object_z_max":0.04043,"peak_contact_force":47.92009,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2209.0,"raw_peak_contact_force":47.92009,"subtask_id":"push_through","tcp_end":[0.50752,-0.04251,0.04771],"tcp_start":[0.50447,0.08165,0.0416],"tcp_to_object_dist_end":0.02916,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `fd7ada9a67242f1adcdb6e23860d1223cdc8a17daf859e94e1687ff0564d9575`; realized-scene SHA-256: `8df62a5afc1e0110114ab6e06b493b5783d0c746729f7f7f1f2cb046babeda91`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47029,0.07994,0.04]},{"name":"goal","value":[0.47029,-0.08006,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.47029,0.07994,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.47029,-0.08006,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.17881,"average_solve_count":151.0,"average_success_count":151.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_prep.approach_height":0.14666,"approach_prep.approach_speed":0.14147,"contact_peg.contact_force_threshold":5.716,"contact_peg.contact_speed":0.05038,"contact_peg.contact_x_offset":0.01804,"descend_to_peg_height.descend_speed":0.04175,"push_channel.push_distance":0.23625,"push_channel.push_lateral_offset":-0.01545,"push_channel.push_max_time":2.85365,"push_channel.push_speed":0.06074,"push_channel.push_z_offset":0.01899},"optimized_scores":{"best_composite_score":0.17336,"best_fitness_score":0.45003,"best_task_score":0.19648},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":916.0,"contact_point_centroid":[0.49637,0.02183,0.00987],"force_p95":12.07698,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.46284,"mean_force":5.20911,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49359,0.05853,0.04332]},{"body_a":"attachment","body_b":"peg","contact_count":818.0,"contact_point_centroid":[0.49526,0.04217,0.0436],"force_p95":11.74101,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.18836,"mean_force":5.37704,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49326,0.05372,0.04371]},{"body_a":"peg","body_b":"channel_base_body","contact_count":372.0,"contact_point_centroid":[0.49385,0.07987,0.00938],"force_p95":0.5538,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.78447,"mean_force":0.56343,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49298,0.11919,0.04845]},{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.49772,0.09747,0.04378],"force_p95":5.23915,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.44587,"mean_force":3.37862,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50026,0.10916,0.04341]},{"body_a":"peg","body_b":"channel_base_body","contact_count":190.0,"contact_point_centroid":[0.49461,0.07985,0.00934],"force_p95":0.72464,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.77147,"mean_force":0.61371,"phase_index":0.0,"phase_name":"approach_prep","phase_type":"approach","tcp_position_centroid":[0.48542,0.16825,0.2456]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46907,0.07994,0.03235],"force_p95":1.18295,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.95027,"mean_force":0.45938,"phase_index":0.0,"phase_name":"approach_prep","phase_type":"approach","tcp_position_centroid":[0.49823,0.19648,0.29403]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":81.0,"contact_point_centroid":[0.47489,0.0636,0.03115],"force_p95":0.84407,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.62632,"mean_force":0.33238,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49554,0.09351,0.03976]},{"body_a":"peg","body_b":"channel_base_body","contact_count":387.0,"contact_point_centroid":[0.49382,0.07997,0.00938],"force_p95":0.5724,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.58533,"mean_force":0.54658,"phase_index":1.0,"phase_name":"descend_to_peg_height","phase_type":"descend","tcp_position_centroid":[0.47992,0.136,0.13032]}],"total_contact_groups":8},"final_pose_error":0.13947,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.498,-0.01792,0.03705],"final_tcp_position":[0.49094,0.01139,0.0477],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.47029,0.07994,0.04]},"peak_contact_force":14.46284,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":218.0,"n_steps_budget":630.0,"object_pos_end":[0.49384,0.07994,0.03378],"object_pos_start":[0.47029,0.07994,0.04],"object_to_goal_dist_end":0.16018,"object_to_goal_dist_start":0.16268,"object_z_max":0.04001,"peak_contact_force":0.54975,"phase_name":"approach_prep","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":225.0,"raw_peak_contact_force":3.77147,"subtask_id":"reach_peg","tcp_end":[0.4738,0.14186,0.20233],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.18068,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":387.0,"n_steps_budget":1000.0,"object_pos_end":[0.49383,0.07994,0.03378],"object_pos_start":[0.49384,0.07994,0.03378],"object_to_goal_dist_end":0.16018,"object_to_goal_dist_start":0.16018,"object_z_max":0.03379,"peak_contact_force":0.56865,"phase_name":"descend_to_peg_height","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":387.0,"raw_peak_contact_force":0.58533,"subtask_id":"align_to_peg","tcp_end":[0.48824,0.13046,0.05742],"tcp_start":[0.4738,0.14186,0.20233],"tcp_to_object_dist_end":0.05606,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":372.0,"n_steps_budget":600.0,"object_pos_end":[0.49379,0.07988,0.03382],"object_pos_start":[0.49383,0.07994,0.03378],"object_to_goal_dist_end":0.16012,"object_to_goal_dist_start":0.16018,"object_z_max":0.03379,"peak_contact_force":5.78447,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":374.0,"raw_peak_contact_force":5.78447,"subtask_id":"align_to_peg","tcp_end":[0.50033,0.10907,0.04337],"tcp_start":[0.48824,0.13046,0.05742],"tcp_to_object_dist_end":0.0314,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.498,-0.01792,0.03705],"object_pos_start":[0.49379,0.07988,0.03382],"object_to_goal_dist_end":0.06218,"object_to_goal_dist_start":0.16012,"object_z_max":0.04053,"peak_contact_force":10.73789,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1815.0,"raw_peak_contact_force":14.46284,"subtask_id":"push_through","tcp_end":[0.49094,0.01139,0.0477],"tcp_start":[0.50033,0.10907,0.04337],"tcp_to_object_dist_end":0.03197,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```