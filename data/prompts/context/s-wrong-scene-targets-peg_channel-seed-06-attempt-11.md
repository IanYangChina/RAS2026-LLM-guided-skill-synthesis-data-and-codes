## Search State

- **Seed**: 6
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → contact → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 8 | 0.0697 | 0.01 | ❌ rejected |
| 10 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | 6 | 0.0654 | 0.40 | ❌ rejected |
| 9 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 8 | 0.1046 | 0.02 | ❌ rejected |
| 8 | approach → contact → approach → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | time_limit | 9 | -0.1762 | 0.00 | ❌ rejected |
| 7 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 6 | 0.1774 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.01 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `07dc0764c781629358e2f97446117d9c410d14c078397be91277b4276116a1de`
- Frozen object start: [0.5030531481177555, -0.09253833041493292, 0.04]
- Frozen task target: [0.5, 0.2, 0.3]
- Goal object position: (0.5, 0.2, 0.3)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5030531481177555, -0.09253833041493292, 0.04)
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.5
- Force limit: 40.0 N
- Peg body: `peg`
- Channel axis: `(0.0, -1.0, 0.0)` — use `impedance_control` to absorb lateral wall forces
- Robot initial TCP position: (0.5030531481177555, 0.06746166958506708, 0.04)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **insertion depth × lateral alignment (axial progress penalised by wall deviation)**

## Scene Entities

robot:
  model: panda_pusher
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5030531481177555, 0.06746166958506708, 0.04]
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
  frozen_object_start: [0.5031, 0.0675, 0.04]
  frozen_task_target: [0.5031, -0.0925, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5030531481177555, -0.09253833041493292, 0.04]}
  frozen_targets: {'channel_exit': [0.5, 0.2, 0.3]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: 07dc0764c781629358e2f97446117d9c410d14c078397be91277b4276116a1de

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
| `object` | offset from object initial position (0.5030531481177555, -0.09253833041493292, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5, 0.2, 0.3) | final destination targets |
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

## Current Skill (Q=0.070) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: reach_peg
  anchor: object
  offset:
  - 0.0
  - 0.03
  - 0.05
  weight: 0.3
- id: insert_peg
  anchor: fixture
  metric: goal_progress
  offset:
  - 0.0
  - -0.16
  - 0.0
  weight: 0.7
phases:
- id: approach_peg
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
    - 0.05
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    approach_tolerance:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: reach_peg
- id: contact_peg
  type: contact
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.02
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    contact_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.02
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: reach_peg
- id: push_through_channel
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
      mode: add_to_offset
      sign: positive
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.08
      - 0.25
      default: 0.2
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
    push_time:
      type: scalar
      range:
      - 1.0
      - 5.0
      default: 3.0
      binds_to:
      - path: duration.max_time
        mode: replace
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.01
    - 0.005
    - 0.0
  subtask_id: insert_peg

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_peg** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.03, 0.05]
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - approach_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **contact_peg** (`contact`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.02, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **push_through_channel** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.2, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
    - push_time: status=consumed; consumers=duration.max_time (replace)
  - retries: max_attempts=2, strategy=offset_target, offset=[0.01, 0.005, 0.0]

## Design Metrics

- **Composite score**: 0.070
- **task_score** (E): 0.005
- **fitness_score**: 0.111  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.389
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.430

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 1.00 | 0.1964 |
| contact_peg | 1.00 | 1.00 | 0.0655 |
| push_through_channel | 0.33 | 1.00 | 0.0255 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.498, 0.106, 0.133) | (0.500, 0.099, 0.040)→(0.501, 0.100, 0.034) | 0.180→0.180 | 1.00 / 1.000 | 0.538 | 2.127 |
| contact_peg | contact | 1.00 / force_exceeded | (0.498, 0.106, 0.133)→(0.495, 0.111, 0.068) | (0.501, 0.100, 0.034)→(0.501, 0.104, 0.033) | 0.180→0.184 | 1.00 / 2.000 | 11.893 | 11.015 |
| push_through_channel | push | 0.33 / guard_failure | (0.494, 0.109, 0.068)→(0.493, 0.084, 0.066) | (0.501, 0.104, 0.033)→(0.517, 0.112, 0.027) | 0.184→0.194 | 1.00 / 1.667 | 32.946 | 35.402 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.000
- alignment_error: None
- force_efficiency: 0.935
- terminal_score: 0.000
- phase_score: 0.265
- phase_breakdown.insert_peg_score: 0.000
- phase_breakdown.reach_peg_score: 0.883

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.159
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.009
- **Median Q (composite search score)**: -0.009
- **K-run variance**: 0.0127
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Parameters at lower bound**: push_through_channel.push_time
- **Final σ (mean)**: 0.380


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `080f370e6b427cbdf66706e7036a0e474f3967ccfc94f129756881a980a10a27`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `1f3f20d8b9dd2cb87de5d9f0723b4addbc88cdcf096cd2177633d23c0fa32881`; realized-scene SHA-256: `07dc0764c781629358e2f97446117d9c410d14c078397be91277b4276116a1de`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50305,-0.09254,0.04]},{"name":"goal","value":[0.54,0.0,0.035]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.50305,0.06746,0.04]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.50305,-0.09254,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.54,0.0,0.035]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.72727,"average_solve_count":88.0,"average_success_count":88.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.07405,"approach_peg.approach_tolerance":0.01696,"approach_peg.arc_height":0.08497,"contact_peg.contact_force":6.39851,"push_through_channel.push_distance":0.16699,"push_through_channel.push_force_limit":39.3957,"push_through_channel.push_speed":0.0104,"push_through_channel.push_time":4.80387},"optimized_scores":{"best_composite_score":-0.00876,"best_fitness_score":0.08791,"best_task_score":0.00871},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":44.0,"contact_point_centroid":[0.50329,0.05782,0.00941],"force_p95":39.60533,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":49.7082,"mean_force":32.57143,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49793,0.06943,0.05959]},{"body_a":"attachment","body_b":"peg","contact_count":44.0,"contact_point_centroid":[0.50978,0.06884,0.05834],"force_p95":39.10976,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":49.22797,"mean_force":32.11196,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49793,0.06943,0.05959]},{"body_a":"peg","body_b":"channel_base_body","contact_count":388.0,"contact_point_centroid":[0.50301,0.06744,0.00938],"force_p95":0.55059,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.52441,"mean_force":0.58009,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49831,0.064,0.09537]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51034,0.07003,0.0588],"force_p95":13.04496,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.04496,"mean_force":13.04496,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49848,0.07064,0.06054]},{"body_a":"peg","body_b":"channel_base_body","contact_count":645.0,"contact_point_centroid":[0.50308,0.06742,0.00935],"force_p95":0.55496,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.55998,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50053,0.09516,0.24908]}],"total_contact_groups":5},"final_pose_error":0.16423,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5024,0.06607,0.0336],"final_tcp_position":[0.49761,0.0679,0.0591],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":49.7082,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":661.0,"n_steps_budget":1000.0,"object_pos_end":[0.50301,0.06745,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14761,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54615,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":645.0,"raw_peak_contact_force":2.06903,"subtask_id":"reach_peg","tcp_end":[0.50053,0.05758,0.13348],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.1002,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":388.0,"n_steps_budget":660.0,"object_pos_end":[0.503,0.06748,0.0338],"object_pos_start":[0.50301,0.06745,0.0338],"object_to_goal_dist_end":0.14764,"object_to_goal_dist_start":0.14761,"object_z_max":0.0338,"peak_contact_force":13.52441,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":389.0,"raw_peak_contact_force":13.52441,"subtask_id":"reach_peg","tcp_end":[0.49849,0.07067,0.0604],"tcp_start":[0.50053,0.05758,0.13348],"tcp_to_object_dist_end":0.02717,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":44.0,"n_steps_budget":1000.0,"object_pos_end":[0.5024,0.06613,0.03362],"object_pos_start":[0.503,0.06748,0.0338],"object_to_goal_dist_end":0.14629,"object_to_goal_dist_start":0.14764,"object_z_max":0.034,"peak_contact_force":47.59799,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":88.0,"raw_peak_contact_force":49.7082,"subtask_id":"insert_peg","tcp_end":[0.49761,0.0679,0.0591],"tcp_start":[0.49762,0.06793,0.05912],"tcp_to_object_dist_end":0.02598,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `625c03a21403c0f6267b643060335ee3d751a26340ace08db5429afcee4c5ccf`; realized-scene SHA-256: `d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51001,-0.04822,0.04]},{"name":"goal","value":[0.54,0.0,0.035]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.51001,0.11178,0.04]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.51001,-0.04822,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.54,0.0,0.035]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.08411,"average_solve_count":107.0,"average_success_count":107.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.05142,"approach_peg.approach_tolerance":0.02936,"approach_peg.arc_height":0.05299,"contact_peg.contact_force":4.66908,"push_through_channel.push_distance":0.26132,"push_through_channel.push_force_limit":39.66785,"push_through_channel.push_speed":0.04082,"push_through_channel.push_time":2.00002},"optimized_scores":{"best_composite_score":-0.0109,"best_fitness_score":0.08576,"best_task_score":0.00725},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":34.0,"contact_point_centroid":[0.50624,0.10044,0.00939],"force_p95":43.80764,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":53.6428,"mean_force":32.68134,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50084,0.11471,0.05966]},{"body_a":"attachment","body_b":"peg","contact_count":34.0,"contact_point_centroid":[0.51271,0.11451,0.05837],"force_p95":43.35609,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":53.15379,"mean_force":32.22173,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50084,0.11471,0.05966]},{"body_a":"peg","body_b":"channel_base_body","contact_count":424.0,"contact_point_centroid":[0.50357,0.1117,0.00941],"force_p95":0.59186,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.91002,"mean_force":0.5871,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50396,0.10921,0.10188]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51328,0.11535,0.05883],"force_p95":18.38404,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.38404,"mean_force":18.38404,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50142,0.11571,0.06056]},{"body_a":"peg","body_b":"channel_base_body","contact_count":282.0,"contact_point_centroid":[0.50358,0.11168,0.00933],"force_p95":0.6897,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.57319,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50664,0.12931,0.23417]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49969,0.1984,0.29948]}],"total_contact_groups":6},"final_pose_error":0.25904,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50325,0.11051,0.03378],"final_tcp_position":[0.50057,0.11345,0.05925],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":53.6428,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":304.0,"n_steps_budget":1000.0,"object_pos_end":[0.5037,0.11175,0.03379],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19189,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.54776,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":298.0,"raw_peak_contact_force":2.06328,"subtask_id":"reach_peg","tcp_end":[0.50899,0.10314,0.14738],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11404,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":424.0,"n_steps_budget":750.0,"object_pos_end":[0.50375,0.11173,0.03387],"object_pos_start":[0.5037,0.11175,0.03379],"object_to_goal_dist_end":0.19187,"object_to_goal_dist_start":0.19189,"object_z_max":0.03393,"peak_contact_force":18.91002,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":425.0,"raw_peak_contact_force":18.91002,"subtask_id":"reach_peg","tcp_end":[0.50141,0.11574,0.06041],"tcp_start":[0.50899,0.10314,0.14738],"tcp_to_object_dist_end":0.02695,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":34.0,"n_steps_budget":1000.0,"object_pos_end":[0.50323,0.11058,0.03379],"object_pos_start":[0.50375,0.11173,0.03387],"object_to_goal_dist_end":0.19071,"object_to_goal_dist_start":0.19187,"object_z_max":0.0339,"peak_contact_force":50.60382,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":68.0,"raw_peak_contact_force":53.6428,"subtask_id":"insert_peg","tcp_end":[0.50057,0.11345,0.05925],"tcp_start":[0.50058,0.1135,0.05927],"tcp_to_object_dist_end":0.02576,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `abe38b4b57ac37a91047e57d04e408cb1fd05583a47670bcb186dc9505a3f021`; realized-scene SHA-256: `c5fb87552d009c7e1ef813cadc54d289d6d9c896c1dd51a37fa468bf6305165e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48616,-0.04102,0.04]},{"name":"goal","value":[0.54,0.0,0.035]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.48616,0.11898,0.04]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48616,-0.04102,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.54,0.0,0.035]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.01205,"average_solve_count":166.0,"average_success_count":166.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.03077,"approach_peg.approach_tolerance":0.03883,"approach_peg.arc_height":0.10476,"contact_peg.contact_force":2.29895,"push_through_channel.push_distance":0.18614,"push_through_channel.push_force_limit":35.24937,"push_through_channel.push_speed":0.04432,"push_through_channel.push_time":2.72769},"optimized_scores":{"best_composite_score":0.22888,"best_fitness_score":0.15888,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"world","contact_count":991.0,"contact_point_centroid":[0.51266,0.15855,-0.00192],"force_p95":0.72594,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.85436,"mean_force":0.61077,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.48149,0.10739,0.07992]},{"body_a":"peg","body_b":"channel_base_body","contact_count":268.0,"contact_point_centroid":[0.49642,0.11909,0.00941],"force_p95":0.64715,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.56833,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49098,0.22003,0.19226]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49979,0.20187,0.29791]},{"body_a":"peg","body_b":"channel_base_body","contact_count":172.0,"contact_point_centroid":[0.49592,0.11993,0.00946],"force_p95":0.57781,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.61173,"mean_force":0.52774,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.48403,0.15154,0.09989]},{"body_a":"peg","body_b":"channel_base_body","contact_count":6.0,"contact_point_centroid":[0.51376,0.11985,0.00979],"force_p95":0.0,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.48466,0.14683,0.08394]}],"total_contact_groups":5},"final_pose_error":0.11009,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.54559,0.15834,0.01408],"final_tcp_position":[0.48134,0.0708,0.07984],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":3.24574,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":293.0,"n_steps_budget":1000.0,"object_pos_end":[0.49601,0.11946,0.03396],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19959,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.51981,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":292.0,"raw_peak_contact_force":2.24822,"subtask_id":"reach_peg","tcp_end":[0.48422,0.15747,0.11668],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09179,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":172.0,"n_steps_budget":600.0,"object_pos_end":[0.49605,0.13279,0.03059],"object_pos_start":[0.49601,0.11946,0.03396],"object_to_goal_dist_end":0.21303,"object_to_goal_dist_start":0.19959,"object_z_max":0.03406,"peak_contact_force":3.24574,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":172.0,"raw_peak_contact_force":0.61173,"subtask_id":"reach_peg","tcp_end":[0.48484,0.14699,0.08423],"tcp_start":[0.48422,0.15747,0.11668],"tcp_to_object_dist_end":0.05661,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54559,0.15834,0.01408],"object_pos_start":[0.49605,0.13279,0.03059],"object_to_goal_dist_end":0.24404,"object_to_goal_dist_start":0.21303,"object_z_max":0.03059,"peak_contact_force":0.63714,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":997.0,"raw_peak_contact_force":2.85436,"subtask_id":"insert_peg","tcp_end":[0.48134,0.0708,0.07984],"tcp_start":[0.48484,0.14699,0.08423],"tcp_to_object_dist_end":0.12695,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```