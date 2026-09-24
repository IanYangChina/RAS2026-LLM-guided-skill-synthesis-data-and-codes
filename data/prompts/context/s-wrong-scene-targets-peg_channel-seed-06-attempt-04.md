## Search State

- **Seed**: 6
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | 6 | 0.0620 | 0.39 | ✅ accepted |
| 3 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | 6 | 0.0626 | 0.39 | ✅ accepted |
| 2 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 4 | 0.4345 | 0.29 | ✅ accepted |
| 1 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 4 | 0.2031 | 0.00 | ✅ accepted |
| 0 | align → lift → push → approach → approach → descend → grasp | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | force_threshold_switch | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | -0.0805 | 0.00 | ✅ accepted |

**Proposal policy**: task_score is 0.39 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.062) — your mutation base

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

- **Composite score**: 0.062
- **task_score** (E): 0.390
- **fitness_score**: 0.392  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.330

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 1.00 | 0.1927 |
| contact_peg | 1.00 | 1.00 | 0.0722 |
| push_through_channel | 1.00 | 1.00 | 0.0722 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.498, 0.140, 0.118) | (0.500, 0.099, 0.040)→(0.501, 0.099, 0.034) | 0.180→0.180 | 1.00 / 1.000 | 0.553 | 2.127 |
| contact_peg | contact | 1.00 / step_budget | (0.498, 0.140, 0.118)→(0.500, 0.125, 0.048) | (0.501, 0.099, 0.034)→(0.503, 0.098, 0.033) | 0.180→0.178 | 1.00 / 1.667 | 96.190 | 129.009 |
| push_through_channel | push | 1.00 / time_limit | (0.500, 0.125, 0.048)→(0.499, 0.053, 0.046) | (0.503, 0.098, 0.033)→(0.503, 0.034, 0.032) | 0.178→0.115 | 1.00 / 2.000 | 46.467 | 98.611 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.570
- alignment_error: None
- force_efficiency: 0.009
- terminal_score: 0.570
- phase_score: 0.540
- phase_breakdown.insert_peg_score: 0.599
- phase_breakdown.reach_peg_score: 0.402

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.552
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.570
- **Median Q (composite search score)**: 0.039
- **K-run variance**: 0.0150
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Parameters at upper bound**: push_through_channel.push_speed
- **Final σ (mean)**: 0.358


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.09272,"average_solve_count":151.0,"average_success_count":151.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.05107,"approach_peg.approach_tolerance":0.03951,"contact_peg.contact_tolerance":0.01285,"push_through_channel.push_distance":0.09957,"push_through_channel.push_speed":0.05,"push_through_channel.push_time":4.23757},"optimized_scores":{"best_composite_score":0.22194,"best_fitness_score":0.55194,"best_task_score":0.56973},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":218.0,"contact_point_centroid":[0.50371,0.06461,0.00942],"force_p95":0.55555,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":49.57063,"mean_force":1.05638,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49915,0.1039,0.08371]},{"body_a":"attachment","body_b":"peg","contact_count":5.0,"contact_point_centroid":[0.50194,0.08489,0.05872],"force_p95":47.72378,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":49.26542,"mean_force":23.16543,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49903,0.09617,0.05859]},{"body_a":"attachment","body_b":"peg","contact_count":992.0,"contact_point_centroid":[0.50068,0.03938,0.04037],"force_p95":34.09279,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.73494,"mean_force":14.38746,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49579,0.04994,0.04103]},{"body_a":"peg","body_b":"channel_base_body","contact_count":995.0,"contact_point_centroid":[0.50519,0.01707,0.00985],"force_p95":30.6477,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":36.09384,"mean_force":13.23262,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49581,0.05008,0.04105]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":458.0,"contact_point_centroid":[0.52513,0.00614,0.02866],"force_p95":13.89458,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.16906,"mean_force":8.60975,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49582,0.02858,0.04119]},{"body_a":"peg","body_b":"channel_base_body","contact_count":212.0,"contact_point_centroid":[0.50304,0.06733,0.00927],"force_p95":0.83869,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.58722,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.5005,0.15774,0.21037]}],"total_contact_groups":6},"final_pose_error":0.01867,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50754,-0.0237,0.03822],"final_tcp_position":[0.49625,0.01051,0.04175],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":49.57063,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":228.0,"n_steps_budget":1000.0,"object_pos_end":[0.50302,0.06748,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14764,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54147,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":212.0,"raw_peak_contact_force":2.06903,"subtask_id":"reach_peg","tcp_end":[0.50114,0.11626,0.12467],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.10315,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":218.0,"n_steps_budget":630.0,"object_pos_end":[0.50402,0.06174,0.03805],"object_pos_start":[0.50302,0.06748,0.0338],"object_to_goal_dist_end":0.14181,"object_to_goal_dist_start":0.14764,"object_z_max":0.03807,"peak_contact_force":0.44056,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":223.0,"raw_peak_contact_force":49.57063,"subtask_id":"reach_peg","tcp_end":[0.49917,0.09191,0.04495],"tcp_start":[0.50114,0.11626,0.12467],"tcp_to_object_dist_end":0.03133,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50754,-0.0237,0.03822],"object_pos_start":[0.50402,0.06174,0.03805],"object_to_goal_dist_end":0.05684,"object_to_goal_dist_start":0.14181,"object_z_max":0.04061,"peak_contact_force":40.47194,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2445.0,"raw_peak_contact_force":40.73494,"subtask_id":"insert_peg","tcp_end":[0.49625,0.01051,0.04175],"tcp_start":[0.49917,0.09191,0.04495],"tcp_to_object_dist_end":0.03619,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.01935,"average_solve_count":155.0,"average_success_count":155.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.04633,"approach_peg.approach_tolerance":0.03005,"contact_peg.contact_tolerance":0.01124,"push_through_channel.push_distance":0.15219,"push_through_channel.push_speed":0.02983,"push_through_channel.push_time":3.16324},"optimized_scores":{"best_composite_score":0.0393,"best_fitness_score":0.3693,"best_task_score":0.39128},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":259.0,"contact_point_centroid":[0.50742,0.11444,0.00894],"force_p95":186.01815,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":195.74694,"mean_force":50.32655,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50358,0.14169,0.07518]},{"body_a":"attachment","body_b":"peg","contact_count":94.0,"contact_point_centroid":[0.5121,0.12921,0.0532],"force_p95":190.26577,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":195.21449,"mean_force":137.21735,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50462,0.13809,0.05207]},{"body_a":"peg","body_b":"channel_base_body","contact_count":983.0,"contact_point_centroid":[0.50805,0.08233,0.00819],"force_p95":130.56085,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":147.10979,"mean_force":57.29352,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50817,0.1137,0.04676]},{"body_a":"attachment","body_b":"peg","contact_count":487.0,"contact_point_centroid":[0.51704,0.11738,0.05268],"force_p95":134.85875,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":146.67493,"mean_force":114.55464,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.51173,0.12768,0.05105]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":130.0,"contact_point_centroid":[0.52501,0.12,0.06],"force_p95":55.76334,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":77.59603,"mean_force":27.50993,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.5126,0.12304,0.05201]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":172.0,"contact_point_centroid":[0.5251,0.1069,0.05165],"force_p95":6.99382,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.21173,"mean_force":3.40818,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.51133,0.13274,0.05081]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47482,0.07555,0.03436],"force_p95":8.08111,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.2756,"mean_force":1.55361,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.5062,0.10952,0.04443]},{"body_a":"peg","body_b":"channel_base_body","contact_count":254.0,"contact_point_centroid":[0.50335,0.11167,0.00932],"force_p95":0.72907,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.57611,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50292,0.17409,0.20489]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49981,0.19938,0.2989]}],"total_contact_groups":9},"final_pose_error":0.09928,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50492,0.0489,0.02561],"final_tcp_position":[0.5041,0.08606,0.04189],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":195.74694,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":276.0,"n_steps_budget":1000.0,"object_pos_end":[0.50374,0.11182,0.03388],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19196,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.52027,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":270.0,"raw_peak_contact_force":2.06328,"subtask_id":"reach_peg","tcp_end":[0.5063,0.15014,0.11799],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09246,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":259.0,"n_steps_budget":600.0,"object_pos_end":[0.50636,0.11249,0.03092],"object_pos_start":[0.50374,0.11182,0.03388],"object_to_goal_dist_end":0.19281,"object_to_goal_dist_start":0.19196,"object_z_max":0.03398,"peak_contact_force":195.74694,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":353.0,"raw_peak_contact_force":195.74694,"subtask_id":"reach_peg","tcp_end":[0.50799,0.13916,0.04671],"tcp_start":[0.5063,0.15014,0.11799],"tcp_to_object_dist_end":0.03104,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50492,0.0489,0.02561],"object_pos_start":[0.50636,0.11249,0.03092],"object_to_goal_dist_end":0.1298,"object_to_goal_dist_start":0.19281,"object_z_max":0.04112,"peak_contact_force":0.49632,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1796.0,"raw_peak_contact_force":147.10979,"subtask_id":"insert_peg","tcp_end":[0.5041,0.08606,0.04189],"tcp_start":[0.50799,0.13916,0.04671],"tcp_to_object_dist_end":0.04057,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.0678,"average_solve_count":177.0,"average_success_count":177.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.02459,"approach_peg.approach_tolerance":0.02233,"contact_peg.contact_tolerance":0.01917,"push_through_channel.push_distance":0.2363,"push_through_channel.push_speed":0.04949,"push_through_channel.push_time":3.48833},"optimized_scores":{"best_composite_score":-0.07517,"best_fitness_score":0.25483,"best_task_score":0.2085},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":133.0,"contact_point_centroid":[0.49771,0.11903,0.00935],"force_p95":130.74265,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":141.71056,"mean_force":20.54316,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.48723,0.14851,0.08059]},{"body_a":"attachment","body_b":"peg","contact_count":25.0,"contact_point_centroid":[0.49994,0.13741,0.05567],"force_p95":135.60744,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":140.88004,"mean_force":106.5056,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49036,0.14432,0.05579]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50447,0.09669,0.00804],"force_p95":105.49941,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":107.98831,"mean_force":91.17933,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49438,0.10484,0.05384]},{"body_a":"attachment","body_b":"peg","contact_count":1000.0,"contact_point_centroid":[0.50545,0.10262,0.05412],"force_p95":104.96935,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":107.47397,"mean_force":90.67319,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49438,0.10484,0.05384]},{"body_a":"peg","body_b":"channel_base_body","contact_count":333.0,"contact_point_centroid":[0.49646,0.11907,0.00938],"force_p95":0.62319,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.5647,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49193,0.17624,0.20139]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49951,0.19911,0.29753]}],"total_contact_groups":6},"final_pose_error":0.15489,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49564,0.07725,0.03325],"final_tcp_position":[0.49586,0.06329,0.05501],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":141.71056,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":358.0,"n_steps_budget":1000.0,"object_pos_end":[0.496,0.11897,0.03402],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.1991,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.59709,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":357.0,"raw_peak_contact_force":2.24822,"subtask_id":"reach_peg","tcp_end":[0.48534,0.15448,0.11158],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08597,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":133.0,"n_steps_budget":600.0,"object_pos_end":[0.49727,0.11958,0.03146],"object_pos_start":[0.496,0.11897,0.03402],"object_to_goal_dist_end":0.19978,"object_to_goal_dist_start":0.1991,"object_z_max":0.03402,"peak_contact_force":92.38334,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":158.0,"raw_peak_contact_force":141.71056,"subtask_id":"reach_peg","tcp_end":[0.49203,0.14479,0.05163],"tcp_start":[0.48534,0.15448,0.11158],"tcp_to_object_dist_end":0.03271,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49564,0.07725,0.03325],"object_pos_start":[0.49727,0.11958,0.03146],"object_to_goal_dist_end":0.15745,"object_to_goal_dist_start":0.19978,"object_z_max":0.03324,"peak_contact_force":98.43383,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2000.0,"raw_peak_contact_force":107.98831,"subtask_id":"insert_peg","tcp_end":[0.49586,0.06329,0.05501],"tcp_start":[0.49203,0.14479,0.05163],"tcp_to_object_dist_end":0.02585,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```