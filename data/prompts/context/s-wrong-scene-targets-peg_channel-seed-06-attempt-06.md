## Search State

- **Seed**: 6
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | 6 | 0.0663 | 0.40 | ✅ accepted |
| 5 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | 6 | 0.0693 | 0.38 | ❌ rejected |
| 4 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | 6 | 0.0620 | 0.39 | ✅ accepted |
| 3 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | 6 | 0.0626 | 0.39 | ✅ accepted |
| 2 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 4 | 0.4345 | 0.29 | ✅ accepted |

**Proposal policy**: task_score is 0.40 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.066) — your mutation base

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

- **Composite score**: 0.066
- **task_score** (E): 0.402
- **fitness_score**: 0.396  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.330

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 1.00 | 0.1927 |
| contact_peg | 1.00 | 1.00 | 0.0718 |
| push_through_channel | 1.00 | 1.00 | 0.0706 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.498, 0.139, 0.118) | (0.500, 0.099, 0.040)→(0.501, 0.099, 0.034) | 0.180→0.180 | 1.00 / 1.000 | 0.527 | 2.127 |
| contact_peg | contact | 1.00 / step_budget | (0.498, 0.139, 0.118)→(0.499, 0.125, 0.048) | (0.501, 0.099, 0.034)→(0.503, 0.095, 0.034) | 0.180→0.175 | 1.00 / 1.667 | 90.476 | 136.006 |
| push_through_channel | push | 1.00 / time_limit | (0.499, 0.125, 0.048)→(0.498, 0.054, 0.046) | (0.503, 0.095, 0.034)→(0.501, 0.033, 0.028) | 0.175→0.114 | 1.00 / 2.000 | 34.975 | 81.206 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.597
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.597
- phase_score: 0.533
- phase_breakdown.insert_peg_score: 0.593
- phase_breakdown.reach_peg_score: 0.393

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.559
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.597
- **Median Q (composite search score)**: 0.045
- **K-run variance**: 0.0156
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.314


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.0678,"average_solve_count":177.0,"average_success_count":177.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.03502,"approach_peg.approach_tolerance":0.02597,"contact_peg.contact_tolerance":0.01144,"push_through_channel.push_distance":0.18095,"push_through_channel.push_speed":0.04957,"push_through_channel.push_time":2.44277},"optimized_scores":{"best_composite_score":0.22864,"best_fitness_score":0.55864,"best_task_score":0.59664},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":207.0,"contact_point_centroid":[0.50387,0.0645,0.00942],"force_p95":8.68347,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":90.56489,"mean_force":3.59989,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.4987,0.10052,0.07752]},{"body_a":"attachment","body_b":"peg","contact_count":13.0,"contact_point_centroid":[0.50349,0.08465,0.05812],"force_p95":86.01322,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":90.23611,"mean_force":49.09403,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49882,0.09512,0.05796]},{"body_a":"peg","body_b":"channel_base_body","contact_count":990.0,"contact_point_centroid":[0.50181,0.00732,0.009],"force_p95":3.36353,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.57528,"mean_force":1.09805,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49545,0.0488,0.03948]},{"body_a":"attachment","body_b":"peg","contact_count":422.0,"contact_point_centroid":[0.49812,0.02259,0.04455],"force_p95":6.2776,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.4319,"mean_force":1.55195,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.4953,0.0344,0.03934]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":133.0,"contact_point_centroid":[0.52501,-0.02617,0.02742],"force_p95":4.1127,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.85091,"mean_force":2.0028,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49535,0.03147,0.0394]},{"body_a":"peg","body_b":"channel_base_body","contact_count":329.0,"contact_point_centroid":[0.50312,0.06743,0.00931],"force_p95":0.6474,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.5728,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49961,0.15454,0.20399]}],"total_contact_groups":6},"final_pose_error":0.09865,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50188,-0.028,0.02626],"final_tcp_position":[0.4953,0.00864,0.03936],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":90.56489,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":345.0,"n_steps_budget":1000.0,"object_pos_end":[0.50303,0.06743,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54175,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":329.0,"raw_peak_contact_force":2.06903,"subtask_id":"reach_peg","tcp_end":[0.50018,0.11005,0.11225],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08932,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":208.0,"n_steps_budget":600.0,"object_pos_end":[0.50531,0.05225,0.04068],"object_pos_start":[0.50303,0.06743,0.0338],"object_to_goal_dist_end":0.13236,"object_to_goal_dist_start":0.14759,"object_z_max":0.04066,"peak_contact_force":0.49601,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":220.0,"raw_peak_contact_force":90.56489,"subtask_id":"reach_peg","tcp_end":[0.49917,0.09113,0.04391],"tcp_start":[0.50018,0.11005,0.11225],"tcp_to_object_dist_end":0.03949,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50188,-0.028,0.02626],"object_pos_start":[0.50531,0.05225,0.04068],"object_to_goal_dist_end":0.05382,"object_to_goal_dist_start":0.13236,"object_z_max":0.0408,"peak_contact_force":6.64131,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1545.0,"raw_peak_contact_force":9.57528,"subtask_id":"insert_peg","tcp_end":[0.4953,0.00864,0.03936],"tcp_start":[0.49917,0.09113,0.04391],"tcp_to_object_dist_end":0.03947,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.9708,"average_solve_count":137.0,"average_success_count":137.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.06006,"approach_peg.approach_tolerance":0.04011,"contact_peg.contact_tolerance":0.01668,"push_through_channel.push_distance":0.14156,"push_through_channel.push_speed":0.02332,"push_through_channel.push_time":2.78131},"optimized_scores":{"best_composite_score":0.04514,"best_fitness_score":0.37514,"best_task_score":0.39715},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":191.0,"contact_point_centroid":[0.50603,0.11367,0.00916],"force_p95":169.24216,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":181.52045,"mean_force":33.33709,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50337,0.14352,0.08395]},{"body_a":"attachment","body_b":"peg","contact_count":45.0,"contact_point_centroid":[0.51165,0.12917,0.05447],"force_p95":177.97857,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":180.99737,"mean_force":139.2429,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50343,0.13763,0.05374]},{"body_a":"peg","body_b":"channel_base_body","contact_count":986.0,"contact_point_centroid":[0.50755,0.08361,0.00832],"force_p95":115.44165,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":128.65091,"mean_force":53.10274,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50578,0.11501,0.04885]},{"body_a":"attachment","body_b":"peg","contact_count":488.0,"contact_point_centroid":[0.5157,0.11878,0.05409],"force_p95":119.54139,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":128.11708,"mean_force":106.04239,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.5092,0.12844,0.05284]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":22.0,"contact_point_centroid":[0.47486,0.0731,0.03575],"force_p95":7.62233,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.4179,"mean_force":1.47463,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50374,0.10892,0.0464]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":23.0,"contact_point_centroid":[0.52502,0.02755,0.02731],"force_p95":7.38082,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.81334,"mean_force":3.19447,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50202,0.09588,0.04452]},{"body_a":"peg","body_b":"channel_base_body","contact_count":183.0,"contact_point_centroid":[0.50329,0.11165,0.00929],"force_p95":0.84923,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.58923,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50353,0.17539,0.20915]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49992,0.19934,0.29865]}],"total_contact_groups":8},"final_pose_error":0.09497,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50499,0.04818,0.02456],"final_tcp_position":[0.50179,0.09128,0.04429],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":181.52045,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":205.0,"n_steps_budget":1000.0,"object_pos_end":[0.50369,0.11174,0.03386],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19188,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.51637,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":199.0,"raw_peak_contact_force":2.06328,"subtask_id":"reach_peg","tcp_end":[0.50673,0.1531,0.12822],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.10307,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":191.0,"n_steps_budget":630.0,"object_pos_end":[0.50524,0.11181,0.03128],"object_pos_start":[0.50369,0.11174,0.03386],"object_to_goal_dist_end":0.19208,"object_to_goal_dist_start":0.19188,"object_z_max":0.03386,"peak_contact_force":178.60226,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":236.0,"raw_peak_contact_force":181.52045,"subtask_id":"reach_peg","tcp_end":[0.50565,0.13807,0.0491],"tcp_start":[0.50673,0.1531,0.12822],"tcp_to_object_dist_end":0.03174,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50499,0.04818,0.02456],"object_pos_start":[0.50524,0.11181,0.03128],"object_to_goal_dist_end":0.12921,"object_to_goal_dist_start":0.19208,"object_z_max":0.04067,"peak_contact_force":2.21253,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1519.0,"raw_peak_contact_force":128.65091,"subtask_id":"insert_peg","tcp_end":[0.50179,0.09128,0.04429],"tcp_start":[0.50565,0.13807,0.0491],"tcp_to_object_dist_end":0.0475,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.59649,"average_solve_count":114.0,"average_success_count":114.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.07796,"approach_peg.approach_tolerance":0.02603,"contact_peg.contact_tolerance":0.01928,"push_through_channel.push_distance":0.10852,"push_through_channel.push_speed":0.0496,"push_through_channel.push_time":1.87822},"optimized_scores":{"best_composite_score":-0.07491,"best_fitness_score":0.25509,"best_task_score":0.21163},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":136.0,"contact_point_centroid":[0.49755,0.11919,0.00938],"force_p95":128.63681,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":135.93178,"mean_force":17.99966,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.4875,0.14897,0.08233]},{"body_a":"attachment","body_b":"peg","contact_count":23.0,"contact_point_centroid":[0.50019,0.13759,0.05572],"force_p95":133.48455,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":135.38837,"mean_force":103.34484,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49049,0.14437,0.05594]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50414,0.09681,0.00811],"force_p95":103.38648,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":105.39248,"mean_force":89.67332,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49423,0.10475,0.05404]},{"body_a":"attachment","body_b":"peg","contact_count":1000.0,"contact_point_centroid":[0.50532,0.10275,0.0543],"force_p95":102.90785,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":104.86957,"mean_force":89.17005,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49423,0.10475,0.05404]},{"body_a":"peg","body_b":"channel_base_body","contact_count":275.0,"contact_point_centroid":[0.49639,0.11907,0.00943],"force_p95":0.64928,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.56514,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49232,0.17632,0.20147]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49963,0.19887,0.29621]}],"total_contact_groups":6},"final_pose_error":0.02722,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49496,0.07802,0.03351],"final_tcp_position":[0.49567,0.06302,0.05516],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":135.93178,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":300.0,"n_steps_budget":1000.0,"object_pos_end":[0.49603,0.11906,0.034],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19919,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.52156,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":299.0,"raw_peak_contact_force":2.24822,"subtask_id":"reach_peg","tcp_end":[0.48588,0.15531,0.1148],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08914,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":136.0,"n_steps_budget":600.0,"object_pos_end":[0.49723,0.11967,0.03148],"object_pos_start":[0.49603,0.11906,0.034],"object_to_goal_dist_end":0.19987,"object_to_goal_dist_start":0.19919,"object_z_max":0.03402,"peak_contact_force":92.33007,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":159.0,"raw_peak_contact_force":135.93178,"subtask_id":"reach_peg","tcp_end":[0.49198,0.14477,0.05194],"tcp_start":[0.48588,0.15531,0.1148],"tcp_to_object_dist_end":0.03281,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49496,0.07802,0.03351],"object_pos_start":[0.49723,0.11967,0.03148],"object_to_goal_dist_end":0.15824,"object_to_goal_dist_start":0.19987,"object_z_max":0.0335,"peak_contact_force":96.0713,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2000.0,"raw_peak_contact_force":105.39248,"subtask_id":"insert_peg","tcp_end":[0.49567,0.06302,0.05516],"tcp_start":[0.49198,0.14477,0.05194],"tcp_to_object_dist_end":0.02635,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```