## Search State

- **Seed**: 2
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 3 | 0.1791 | 0.19 | ❌ rejected |
| 8 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 3 | -0.0566 | 0.00 | ❌ rejected |
| 7 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 3 | 0.0613 | 0.00 | ❌ rejected |
| 6 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 3 | 0.2327 | 0.07 | ❌ rejected |
| 5 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.1767 | 0.15 | ❌ rejected |

**Proposal policy**: task_score is 0.19 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `2a92d231da5879af7af8916eb4c7dff00148227e84220c4d9643d9841dc77ee7`
- Frozen object start: [0.48092897073994534, 0.06387929147312987, 0.04]
- Frozen task target: [0.48092897073994534, -0.09612070852687013, 0.04]
- Goal object position: (0.48092897073994534, -0.09612070852687013, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.48092897073994534, 0.06387929147312987, 0.04)
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
  frozen_object_start: [0.4809, 0.0639, 0.04]
  frozen_task_target: [0.4809, -0.0961, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.48092897073994534, 0.06387929147312987, 0.04]}
  frozen_targets: {'channel_exit': [0.48092897073994534, -0.09612070852687013, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: 2a92d231da5879af7af8916eb4c7dff00148227e84220c4d9643d9841dc77ee7

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
| `object` | offset from object initial position (0.48092897073994534, 0.06387929147312987, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.48092897073994534, -0.09612070852687013, 0.04) | final destination targets |
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

## Current Skill (Q=0.179) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: reach_contact
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.05
  weight: 0.3
- id: complete_push
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
    - 0.03
    - 0.08
    tolerance: 0.02
    orientation:
      mode: keep_current
  subtask_id: reach_contact
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.03
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    contact_force:
      type: scalar
      range:
      - 1.0
      - 15.0
      default: 3.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
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
      distance: 0.18
      axis: world_y
      mode: add_to_offset
      sign: negative
    tolerance: 0.01
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - -1.0
      align_with: world_z
      tolerance: 0.1
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.12
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
    threshold: 40.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.002
    - 0.0
    - 0.0
  subtask_id: complete_push
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
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.03, 0.08], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings: none
- **contact_1** (`contact`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.03, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_y, distance=0.18, mode=add_to_offset, sign=negative}, tolerance=0.01
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_guard, when=during_phase, predicate=force_below, on_failure=retry, threshold=40.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.002, 0.0, 0.0]
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.179
- **task_score** (E): 0.194
- **fitness_score**: 0.306  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.083
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.210

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1899 |
| contact_1 | 0.33 | 1.00 | 0.0937 |
| push_1 | 0.67 | 1.00 | 0.1067 |
| retract_1 | 1.00 | 1.00 | 0.0890 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.492, 0.109, 0.136) | (0.494, 0.068, 0.040)→(0.498, 0.068, 0.034) | 0.151→0.148 | 1.00 / 1.000 | 0.546 | 3.659 |
| contact_1 | contact | 0.33 / step_budget | (0.492, 0.109, 0.136)→(0.493, 0.099, 0.044) | (0.498, 0.068, 0.034)→(0.498, 0.068, 0.034) | 0.148→0.148 | 1.00 / 1.667 | 19.728 | 19.822 |
| push_1 | push | 0.67 / step_budget | (0.493, 0.099, 0.044)→(0.490, -0.008, 0.041) | (0.498, 0.068, 0.034)→(0.499, -0.035, 0.035) | 0.148→0.053 | 1.00 / 2.333 | 13.851 | 111.927 |
| retract_1 | retract | 1.00 / step_budget | (0.490, -0.008, 0.041)→(0.487, -0.008, 0.130) | (0.498, -0.035, 0.035)→(0.502, -0.029, 0.034) | 0.053→0.055 | 1.00 / 1.000 | 0.550 | 267.467 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.896
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.319
- phase_score: 0.492
- phase_breakdown.reach_contact_score: 0.285
- phase_breakdown.complete_push_score: 0.581

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.423
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.319
- **Median Q (composite search score)**: 0.202
- **K-run variance**: 0.0016
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.3
- **Final σ (mean)**: 0.183


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `6269840a353345700ffa70ea476a3ad730b138bf2ec3c52304c054f0e194e023`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `a2936262b79fcd5a49fda15d77b54223f43c58bfee2e71dc505f8a2f79369706`; realized-scene SHA-256: `2a92d231da5879af7af8916eb4c7dff00148227e84220c4d9643d9841dc77ee7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48093,0.06388,0.04]},{"name":"goal","value":[0.48093,-0.09612,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48093,0.06388,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48093,-0.09612,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.09804,"average_solve_count":204.0,"average_success_count":204.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force":7.02266,"push_1.push_distance":0.16302,"push_1.push_speed":0.02707},"optimized_scores":{"best_composite_score":0.21309,"best_fitness_score":0.42309,"best_task_score":0.31947},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":146.0,"contact_point_centroid":[0.47498,-0.05662,0.04537],"force_p95":311.21423,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":344.25153,"mean_force":180.36321,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48696,-0.05663,0.04521]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":245.0,"contact_point_centroid":[0.475,0.00052,0.03178],"force_p95":31.49602,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":37.9436,"mean_force":22.40693,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.487,0.00052,0.03165]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":26.0,"contact_point_centroid":[0.52519,-0.07979,0.05421],"force_p95":23.80601,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":24.84299,"mean_force":7.33826,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48697,-0.05762,0.03281]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":781.0,"contact_point_centroid":[0.52526,-0.02394,0.03877],"force_p95":14.17534,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.144,"mean_force":4.0519,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.487,-0.00225,0.03167]},{"body_a":"attachment","body_b":"peg","contact_count":804.0,"contact_point_centroid":[0.49491,-0.00125,0.04615],"force_p95":14.99347,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.12786,"mean_force":4.73769,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48704,0.00767,0.03168]},{"body_a":"attachment","body_b":"peg","contact_count":47.0,"contact_point_centroid":[0.49514,-0.06619,0.06008],"force_p95":18.02742,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.71823,"mean_force":3.66907,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48698,-0.05713,0.03637]},{"body_a":"peg","body_b":"channel_base_body","contact_count":568.0,"contact_point_centroid":[0.50825,-0.02065,0.00988],"force_p95":7.76577,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.51812,"mean_force":2.6937,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4871,0.01722,0.03175]},{"body_a":"peg","body_b":"channel_base_body","contact_count":541.0,"contact_point_centroid":[0.50798,-0.08116,0.00948],"force_p95":0.57112,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.98863,"mean_force":0.60908,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48512,-0.05699,0.07576]},{"body_a":"peg","body_b":"channel_base_body","contact_count":337.0,"contact_point_centroid":[0.49571,0.06376,0.00935],"force_p95":0.62945,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.57066,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48934,0.15027,0.21253]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49929,0.19757,0.29585]},{"body_a":"peg","body_b":"channel_base_body","contact_count":578.0,"contact_point_centroid":[0.49515,0.0638,0.0094],"force_p95":0.55077,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.864,"mean_force":0.54703,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48433,0.09938,0.08376]},{"body_a":"attachment","body_b":"peg","contact_count":6.0,"contact_point_centroid":[0.49419,0.08213,0.05884],"force_p95":0.48137,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.53422,"mean_force":0.25467,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49029,0.09419,0.03748]}],"total_contact_groups":12},"final_pose_error":0.01126,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50656,-0.07951,0.03378],"final_tcp_position":[0.48402,-0.05733,0.12068],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":344.25153,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":364.0,"n_steps_budget":1000.0,"object_pos_end":[0.49523,0.06399,0.03392],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.1442,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.54547,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":365.0,"raw_peak_contact_force":2.44546,"subtask_id":"reach_contact","tcp_end":[0.48065,0.10548,0.13615],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11128,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":578.0,"n_steps_budget":660.0,"object_pos_end":[0.49523,0.06396,0.0339],"object_pos_start":[0.49523,0.06399,0.03392],"object_to_goal_dist_end":0.14417,"object_to_goal_dist_start":0.1442,"object_z_max":0.034,"peak_contact_force":0.58779,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":584.0,"raw_peak_contact_force":0.864,"subtask_id":"reach_contact","tcp_end":[0.49044,0.09399,0.03582],"tcp_start":[0.48065,0.10548,0.13615],"tcp_to_object_dist_end":0.03047,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50759,-0.0793,0.03501],"object_pos_start":[0.49523,0.06396,0.0339],"object_to_goal_dist_end":0.00911,"object_to_goal_dist_start":0.14417,"object_z_max":0.03854,"peak_contact_force":11.89601,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2398.0,"raw_peak_contact_force":37.9436,"subtask_id":"complete_push","tcp_end":[0.487,-0.0577,0.03153],"tcp_start":[0.49044,0.09399,0.03582],"tcp_to_object_dist_end":0.03004,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":544.0,"n_steps_budget":630.0,"object_pos_end":[0.50656,-0.07951,0.03378],"object_pos_start":[0.50759,-0.0793,0.03501],"object_to_goal_dist_end":0.00905,"object_to_goal_dist_start":0.00911,"object_z_max":0.03518,"peak_contact_force":0.55204,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":760.0,"raw_peak_contact_force":344.25153,"tcp_end":[0.48402,-0.05733,0.12068],"tcp_start":[0.487,-0.0577,0.03153],"tcp_to_object_dist_end":0.09247,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `78f29ebb38dd2df9149fb0cd7c7c33d55e802bb94eee599b284bb0b197a04fb7`; realized-scene SHA-256: `990d03f436076caee02f5d9d8b3b9b0b3759564b7644084e4eac46818881d834`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.46685,0.05894,0.04]},{"name":"goal","value":[0.46685,-0.10106,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.46685,0.05894,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.46685,-0.10106,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.93023,"average_solve_count":86.0,"average_success_count":86.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force":8.67931,"push_1.push_distance":0.15504,"push_1.push_speed":0.03034},"optimized_scores":{"best_composite_score":0.12222,"best_fitness_score":0.08222,"best_task_score":0.00049},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":1.0,"contact_point_centroid":[0.475,0.0824,0.06],"force_p95":420.00556,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":420.00556,"mean_force":420.00556,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48309,0.09115,0.05887]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":2.0,"contact_point_centroid":[0.47499,0.08292,0.05996],"force_p95":265.31201,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":266.54672,"mean_force":254.19955,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48308,0.09162,0.05879]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":1.0,"contact_point_centroid":[0.475,0.0829,0.06],"force_p95":58.05142,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":58.05142,"mean_force":58.05142,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48304,0.0917,0.05887]},{"body_a":"peg","body_b":"channel_base_body","contact_count":343.0,"contact_point_centroid":[0.49451,0.05885,0.00933],"force_p95":0.61136,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.58884,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48273,0.14757,0.2119]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49868,0.19668,0.29435]},{"body_a":"peg","body_b":"channel_base_body","contact_count":474.0,"contact_point_centroid":[0.49421,0.05896,0.00939],"force_p95":0.55041,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55382,"mean_force":0.54615,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47434,0.09595,0.09575]},{"body_a":"peg","body_b":"channel_base_body","contact_count":543.0,"contact_point_centroid":[0.49391,0.05892,0.0094],"force_p95":0.55039,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55295,"mean_force":0.54567,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48017,0.09054,0.10277]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.4991,0.07554,0.00939],"force_p95":0.54805,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54847,"mean_force":0.54537,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48308,0.09158,0.05882]}],"total_contact_groups":8},"final_pose_error":0.01153,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49417,0.05871,0.03399],"final_tcp_position":[0.48013,0.09061,0.14774],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":420.00556,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":372.0,"n_steps_budget":1000.0,"object_pos_end":[0.49422,0.05896,0.03385],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13922,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54827,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":378.0,"raw_peak_contact_force":4.20518,"subtask_id":"reach_contact","tcp_end":[0.46814,0.10076,0.13574],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11318,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":474.0,"n_steps_budget":690.0,"object_pos_end":[0.49422,0.05909,0.0339],"object_pos_start":[0.49422,0.05896,0.03385],"object_to_goal_dist_end":0.13934,"object_to_goal_dist_start":0.13922,"object_z_max":0.0339,"peak_contact_force":58.05142,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":475.0,"raw_peak_contact_force":58.05142,"subtask_id":"reach_contact","tcp_end":[0.48307,0.09169,0.05877],"tcp_start":[0.46814,0.10076,0.13574],"tcp_to_object_dist_end":0.04249,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.49417,0.05912,0.0339],"object_pos_start":[0.49422,0.05909,0.0339],"object_to_goal_dist_end":0.13937,"object_to_goal_dist_start":0.13934,"object_z_max":0.0339,"peak_contact_force":1.4151,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":5.0,"raw_peak_contact_force":266.54672,"subtask_id":"complete_push","tcp_end":[0.48309,0.09115,0.05887],"tcp_start":[0.48308,0.09149,0.05889],"tcp_to_object_dist_end":0.0421,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.49417,0.05871,0.03399],"object_pos_start":[0.49406,0.05911,0.0339],"object_to_goal_dist_end":0.13896,"object_to_goal_dist_start":0.13937,"object_z_max":0.03399,"peak_contact_force":0.53863,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":544.0,"raw_peak_contact_force":420.00556,"tcp_end":[0.48013,0.09061,0.14774],"tcp_start":[0.48309,0.09115,0.05887],"tcp_to_object_dist_end":0.11897,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `ecba62e37d233197bb248f7fe6e722b45204af5e83240a6f27138a89bcccfe42`; realized-scene SHA-256: `5d75b33f12bcf5a2f8bdcc4693a93f63ce145f4d32d6acfe75032964e261854c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53544,0.08091,0.04]},{"name":"goal","value":[0.53544,-0.07909,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.53544,0.08091,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.53544,-0.07909,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.41176,"average_solve_count":187.0,"average_success_count":187.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force":7.59386,"push_1.push_distance":0.17783,"push_1.push_speed":0.03504},"optimized_scores":{"best_composite_score":0.20207,"best_fitness_score":0.41207,"best_task_score":0.26064},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":286.0,"contact_point_centroid":[0.49623,-0.06555,0.05564],"force_p95":30.71869,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":38.14363,"mean_force":21.69955,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49748,-0.05401,0.05535]},{"body_a":"peg","body_b":"channel_base_body","contact_count":297.0,"contact_point_centroid":[0.49309,-0.10066,0.06169],"force_p95":31.15346,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":33.31554,"mean_force":21.0036,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49747,-0.05406,0.05629]},{"body_a":"peg","body_b":"channel_base_body","contact_count":40.0,"contact_point_centroid":[0.49442,-0.10092,0.04129],"force_p95":30.80406,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":31.29123,"mean_force":21.70651,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50057,-0.0551,0.03383]},{"body_a":"attachment","body_b":"peg","contact_count":799.0,"contact_point_centroid":[0.49903,0.01038,0.042],"force_p95":11.69891,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":30.96829,"mean_force":2.40473,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5007,0.02202,0.034]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":89.0,"contact_point_centroid":[0.47493,-0.08231,0.05443],"force_p95":8.22675,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.05926,"mean_force":3.21387,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49757,-0.05434,0.04695]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":136.0,"contact_point_centroid":[0.47489,-0.01974,0.03692],"force_p95":11.52555,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.19436,"mean_force":2.95364,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5007,0.00893,0.03404]},{"body_a":"peg","body_b":"channel_base_body","contact_count":729.0,"contact_point_centroid":[0.49563,-0.01125,0.00987],"force_p95":3.85666,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.85354,"mean_force":1.47501,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50071,0.02424,0.03402]},{"body_a":"peg","body_b":"channel_base_body","contact_count":331.0,"contact_point_centroid":[0.50553,0.08094,0.00934],"force_p95":0.57191,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.59286,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51452,0.1579,0.21177]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5007,0.19715,0.29399]},{"body_a":"peg","body_b":"channel_base_body","contact_count":225.0,"contact_point_centroid":[0.50404,-0.06475,0.0093],"force_p95":1.31992,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.39479,"mean_force":0.62363,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49744,-0.05651,0.10381]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":25.0,"contact_point_centroid":[0.52531,-0.0626,0.05878],"force_p95":1.25993,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.60848,"mean_force":0.32481,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49739,-0.05639,0.09481]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":15.0,"contact_point_centroid":[0.5251,0.07715,0.03141],"force_p95":0.90745,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.02127,"mean_force":0.41484,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5021,0.1069,0.03587]},{"body_a":"peg","body_b":"channel_base_body","contact_count":415.0,"contact_point_centroid":[0.50602,0.08085,0.00938],"force_p95":0.55007,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55014,"mean_force":0.54677,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.51557,0.11553,0.08627]}],"total_contact_groups":13},"final_pose_error":0.01161,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50543,-0.06474,0.03414],"final_tcp_position":[0.49756,-0.05667,0.12262],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":38.14363,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":360.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.08087,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54453,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":367.0,"raw_peak_contact_force":4.32595,"subtask_id":"reach_contact","tcp_end":[0.52868,0.1206,0.13565],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11167,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":415.0,"n_steps_budget":660.0,"object_pos_end":[0.50597,0.08086,0.03378],"object_pos_start":[0.50599,0.08087,0.03378],"object_to_goal_dist_end":0.16109,"object_to_goal_dist_start":0.1611,"object_z_max":0.03378,"peak_contact_force":0.54611,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":415.0,"raw_peak_contact_force":0.55014,"subtask_id":"reach_contact","tcp_end":[0.50428,0.11094,0.03847],"tcp_start":[0.52868,0.1206,0.13565],"tcp_to_object_dist_end":0.0305,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49381,-0.0855,0.0352],"object_pos_start":[0.50597,0.08086,0.03378],"object_to_goal_dist_end":0.00957,"object_to_goal_dist_start":0.16109,"object_z_max":0.03736,"peak_contact_force":28.2411,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1719.0,"raw_peak_contact_force":31.29123,"subtask_id":"complete_push","tcp_end":[0.50065,-0.05703,0.03381],"tcp_start":[0.50428,0.11094,0.03847],"tcp_to_object_dist_end":0.02931,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":546.0,"n_steps_budget":630.0,"object_pos_end":[0.50543,-0.06474,0.03414],"object_pos_start":[0.49381,-0.0855,0.0352],"object_to_goal_dist_end":0.01723,"object_to_goal_dist_start":0.00957,"object_z_max":0.0579,"peak_contact_force":0.56027,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":922.0,"raw_peak_contact_force":38.14363,"tcp_end":[0.49756,-0.05667,0.12262],"tcp_start":[0.50065,-0.05703,0.03381],"tcp_to_object_dist_end":0.08919,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```