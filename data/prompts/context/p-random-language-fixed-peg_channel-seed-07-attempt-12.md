## Search State

- **Seed**: 7
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.3796 | 0.74 | ✅ accepted |
| 11 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.3576 | 0.74 | ✅ accepted |
| 10 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.2720 | 0.02 | ❌ rejected |
| 9 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.0244 | 0.54 | ❌ rejected |
| 8 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.1262 | 0.54 | ✅ accepted |

**Proposal policy**: task_score is 0.74 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415`
- Frozen object start: [0.5100076373283734, 0.11177710407756605, 0.04]
- Frozen task target: [0.5100076373283734, -0.04822289592243395, 0.04]
- Goal object position: (0.5100076373283734, -0.04822289592243395, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5100076373283734, 0.11177710407756605, 0.04)
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
  frozen_object_start: [0.51, 0.1118, 0.04]
  frozen_task_target: [0.51, -0.0482, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5100076373283734, 0.11177710407756605, 0.04]}
  frozen_targets: {'channel_exit': [0.5100076373283734, -0.04822289592243395, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415

## Subtask Layer

**Mode**: fixed (subtask targets are defined by the task configuration)

Available subtask IDs for phase binding:
| Subtask ID | Anchor | Target offset (m) | Metric | CMA-ES offset param |
|---|---|---|---|---|
| approach | object | (0.00, 0.04, 0.00) | distance | — |
| contact | object | (0.00, 0.02, 0.00) | distance | — |
| push | world | (0.50, -0.08, 0.04) | distance | push_depth |

Annotate phases with `subtask_id: <id>` to bind them to a subtask target.
- A phase bound to a subtask receives a navigation waypoint computed from that subtask's anchor and offset.
- Only the **last phase** bound to a given subtask is used for subtask scoring.
- Phases without `subtask_id` are not scored against subtasks but still execute normally.

## Current Skill (Q=0.380) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
phases:
- id: approach_to_peg
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.04
    - 0.08
    tolerance: 0.01
    orientation:
      mode: none
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
  subtask_id: approach
- id: descend_behind_peg
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.03
    - 0.0
    tolerance: 0.005
    orientation:
      mode: none
  subtask_id: contact
- id: push_through_channel
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
      distance: 0.16
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.1
      - 0.2
      default: 0.16
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: push
- id: retract_from_channel
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.05
    tolerance: 0.01
    orientation:
      mode: none

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_to_peg** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.04, 0.08], tolerance=0.01
  - orientation: mode=none
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_behind_peg** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.03, 0.0], tolerance=0.005
  - orientation: mode=none
  - parameter_bindings: none
- **push_through_channel** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.16, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
- **retract_from_channel** (`retract`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.05], tolerance=0.01
  - orientation: mode=none
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.380
- **task_score** (E): 0.744
- **fitness_score**: 0.590  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.210

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_to_peg | 1.00 | 1.00 | 0.1839 |
| descend_behind_peg | 1.00 | 1.00 | 0.0915 |
| push_through_channel | 1.00 | 1.00 | 0.1684 |
| retract_from_channel | 1.00 | 1.00 | 0.0611 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_to_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.505, 0.141, 0.128) | (0.509, 0.098, 0.040)→(0.502, 0.098, 0.034) | 0.179→0.178 | 1.00 / 1.000 | 0.580 | 2.732 |
| descend_behind_peg | descend | 1.00 / step_budget | (0.505, 0.141, 0.128)→(0.498, 0.128, 0.038) | (0.502, 0.098, 0.034)→(0.502, 0.098, 0.034) | 0.178→0.178 | 1.00 / 1.333 | 110.262 | 134.175 |
| push_through_channel | push | 1.00 / step_budget | (0.498, 0.128, 0.038)→(0.498, -0.040, 0.038) | (0.502, 0.098, 0.034)→(0.502, -0.058, 0.034) | 0.178→0.026 | 1.00 / 4.000 | 156.564 | 206.491 |
| retract_from_channel | retract | 1.00 / step_budget | (0.498, -0.040, 0.038)→(0.496, -0.077, 0.081) | (0.502, -0.058, 0.034)→(0.502, -0.072, 0.024) | 0.026→0.019 | 1.00 / 1.000 | 0.611 | 67.164 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 1.000
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 1.000
- phase_score: 0.400
- phase_breakdown.approach_score: 0.170
- phase_breakdown.push_score: 0.361
- phase_breakdown.contact_score: 0.746

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.640
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.360
- **K-run variance**: 0.0013
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.350


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `474e87cb3f7f98c9c8d99c8760356b7c026b70b97898f68d5a6c39ba94bca956`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `a79e5fd8fc80d9ecadd30a274b12d8d7e7d0841df5ca68ae512c46dc86b114e6`; realized-scene SHA-256: `d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51001,0.11178,0.04]},{"name":"goal","value":[0.51001,-0.04822,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.51001,0.11178,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.51001,-0.04822,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.09964,"average_solve_count":281.0,"average_success_count":281.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_peg.speed":0.02754,"push_through_channel.push_distance":0.19916,"push_through_channel.push_speed":0.02825},"optimized_scores":{"best_composite_score":0.43004,"best_fitness_score":0.64004,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_base_body","body_b":"link7","contact_count":193.0,"contact_point_centroid":[0.56492,-0.10003,0.06493],"force_p95":268.45537,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":274.91367,"mean_force":243.96865,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49936,-0.02824,0.03664]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":359.0,"contact_point_centroid":[0.54318,0.05361,0.05999],"force_p95":111.49408,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":120.26912,"mean_force":95.60885,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49876,0.05154,0.03544]},{"body_a":"channel_base_body","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.56577,-0.10002,0.06496],"force_p95":59.35267,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":60.42026,"mean_force":47.24456,"phase_index":3.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.49953,-0.02918,0.03727]},{"body_a":"peg","body_b":"channel_base_body","contact_count":257.0,"contact_point_centroid":[0.5043,-0.10053,0.05315],"force_p95":41.74063,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":43.5483,"mean_force":28.98065,"phase_index":3.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.4961,-0.05454,0.0625]},{"body_a":"attachment","body_b":"peg","contact_count":382.0,"contact_point_centroid":[0.50078,-0.05989,0.05487],"force_p95":41.27468,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":43.42833,"mean_force":20.47185,"phase_index":3.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.49639,-0.0493,0.05653]},{"body_a":"peg","body_b":"channel_base_body","contact_count":571.0,"contact_point_centroid":[0.50216,-0.01291,0.00968],"force_p95":8.22109,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.02919,"mean_force":1.66852,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49897,0.02763,0.03587]},{"body_a":"attachment","body_b":"peg","contact_count":381.0,"contact_point_centroid":[0.501,0.00542,0.0366],"force_p95":10.26792,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.77138,"mean_force":1.96705,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49903,0.01713,0.03606]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":100.0,"contact_point_centroid":[0.47459,0.01006,0.03505],"force_p95":3.69355,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.27548,"mean_force":0.98692,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49887,0.04058,0.03549]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":111.0,"contact_point_centroid":[0.52521,0.04321,0.03271],"force_p95":6.70424,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.11313,"mean_force":1.32874,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49856,0.07331,0.03542]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":61.0,"contact_point_centroid":[0.5251,-0.08862,0.05999],"force_p95":8.06482,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.20318,"mean_force":6.6283,"phase_index":3.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.49673,-0.06181,0.07187]},{"body_a":"peg","body_b":"channel_base_body","contact_count":199.0,"contact_point_centroid":[0.50289,-0.07555,0.00936],"force_p95":3.22734,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.4417,"mean_force":1.12152,"phase_index":3.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.49666,-0.0462,0.05176]},{"body_a":"peg","body_b":"channel_base_body","contact_count":574.0,"contact_point_centroid":[0.50362,0.11172,0.00937],"force_p95":0.61146,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.55866,"phase_index":0.0,"phase_name":"approach_to_peg","phase_type":"approach","tcp_position_centroid":[0.5022,0.17656,0.21137]},{"body_a":"peg","body_b":"channel_base_body","contact_count":433.0,"contact_point_centroid":[0.50363,0.11173,0.0094],"force_p95":0.60376,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62497,"mean_force":0.54466,"phase_index":1.0,"phase_name":"descend_behind_peg","phase_type":"descend","tcp_position_centroid":[0.50166,0.14784,0.08139]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_to_peg","phase_type":"approach","tcp_position_centroid":[0.4997,0.19945,0.29923]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":22.0,"contact_point_centroid":[0.47482,-0.06538,0.02492],"force_p95":0.22326,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22432,"mean_force":0.0642,"phase_index":3.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.49569,-0.05095,0.05751]}],"total_contact_groups":15},"final_pose_error":0.01038,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50516,-0.06933,0.02252],"final_tcp_position":[0.49636,-0.07533,0.08147],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":274.91367,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":596.0,"n_steps_budget":1000.0,"object_pos_end":[0.50366,0.11175,0.03382],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19188,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.61159,"phase_name":"approach_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":590.0,"raw_peak_contact_force":2.06328,"subtask_id":"approach","tcp_end":[0.50603,0.1545,0.12849],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.1039,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":433.0,"n_steps_budget":630.0,"object_pos_end":[0.50371,0.11174,0.03383],"object_pos_start":[0.50366,0.11175,0.03382],"object_to_goal_dist_end":0.19187,"object_to_goal_dist_start":0.19188,"object_z_max":0.03399,"peak_contact_force":0.53349,"phase_name":"descend_behind_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":433.0,"raw_peak_contact_force":0.62497,"subtask_id":"contact","tcp_end":[0.49975,0.14174,0.03686],"tcp_start":[0.50603,0.1545,0.12849],"tcp_to_object_dist_end":0.03042,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":808.0,"n_steps_budget":1000.0,"object_pos_end":[0.50478,-0.05878,0.03658],"object_pos_start":[0.50371,0.11174,0.03383],"object_to_goal_dist_end":0.02202,"object_to_goal_dist_start":0.19187,"object_z_max":0.03939,"peak_contact_force":262.58202,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1715.0,"raw_peak_contact_force":274.91367,"subtask_id":"push","tcp_end":[0.49953,-0.02919,0.03724],"tcp_start":[0.49975,0.14174,0.03686],"tcp_to_object_dist_end":0.03006,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":497.0,"n_steps_budget":600.0,"object_pos_end":[0.50516,-0.06933,0.02252],"object_pos_start":[0.50478,-0.05878,0.03658],"object_to_goal_dist_end":0.02112,"object_to_goal_dist_start":0.02202,"object_z_max":0.04976,"peak_contact_force":0.6483,"phase_name":"retract_from_channel","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":926.0,"raw_peak_contact_force":60.42026,"tcp_end":[0.49636,-0.07533,0.08147],"tcp_start":[0.49953,-0.02919,0.03724],"tcp_to_object_dist_end":0.0599,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `3ca2e925d364d2c0fe81fb71ee31d40f947a20e349a0720e1c44a2dd2bc628da`; realized-scene SHA-256: `c5fb87552d009c7e1ef813cadc54d289d6d9c896c1dd51a37fa468bf6305165e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48616,0.11898,0.04]},{"name":"goal","value":[0.48616,-0.04102,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48616,0.11898,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48616,-0.04102,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.28095,"average_solve_count":210.0,"average_success_count":210.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_peg.speed":0.06285,"push_through_channel.push_distance":0.1984,"push_through_channel.push_speed":0.01104},"optimized_scores":{"best_composite_score":0.34843,"best_fitness_score":0.55843,"best_task_score":0.88521},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":745.0,"contact_point_centroid":[0.53628,0.05905,0.05999],"force_p95":131.6615,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":146.72257,"mean_force":116.90094,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49123,0.05755,0.03583]},{"body_a":"attachment","body_b":"peg","contact_count":834.0,"contact_point_centroid":[0.49837,0.03845,0.03506],"force_p95":69.60863,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":80.22353,"mean_force":30.76399,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49135,0.04742,0.0359]},{"body_a":"peg","body_b":"channel_base_body","contact_count":841.0,"contact_point_centroid":[0.50567,0.01786,0.00973],"force_p95":67.91499,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":72.94856,"mean_force":20.28901,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49128,0.05261,0.03585]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.53653,-0.00692,0.05997],"force_p95":66.90666,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":71.03796,"mean_force":48.29212,"phase_index":3.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.49225,-0.01118,0.0359]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":757.0,"contact_point_centroid":[0.5253,0.02014,0.02347],"force_p95":35.58582,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":42.67798,"mean_force":20.32644,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49142,0.04025,0.03595]},{"body_a":"peg","body_b":"link7","contact_count":420.0,"contact_point_centroid":[0.51636,0.00824,0.06933],"force_p95":20.1884,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":34.15575,"mean_force":8.19172,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49139,0.03769,0.03595]},{"body_a":"attachment","body_b":"peg","contact_count":126.0,"contact_point_centroid":[0.49882,-0.02749,0.03661],"force_p95":10.72905,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.20649,"mean_force":5.19765,"phase_index":3.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.4908,-0.01963,0.04007]},{"body_a":"peg","body_b":"channel_base_body","contact_count":495.0,"contact_point_centroid":[0.50033,-0.06715,0.00865],"force_p95":7.14991,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.16547,"mean_force":1.66758,"phase_index":3.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.4925,-0.04454,0.05806]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":77.0,"contact_point_centroid":[0.52503,-0.03559,0.02288],"force_p95":6.98497,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.51119,"mean_force":5.14627,"phase_index":3.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.49091,-0.01848,0.03941]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":8.0,"contact_point_centroid":[0.47498,-0.09927,0.02428],"force_p95":9.09303,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.23509,"mean_force":2.54481,"phase_index":3.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.49418,-0.06194,0.07123]},{"body_a":"peg","body_b":"channel_base_body","contact_count":530.0,"contact_point_centroid":[0.49604,0.11893,0.00945],"force_p95":0.60063,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.9619,"mean_force":0.55546,"phase_index":1.0,"phase_name":"descend_behind_peg","phase_type":"descend","tcp_position_centroid":[0.48638,0.15443,0.07965]},{"body_a":"attachment","body_b":"peg","contact_count":6.0,"contact_point_centroid":[0.49567,0.13692,0.04606],"force_p95":3.32861,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.75706,"mean_force":1.62433,"phase_index":1.0,"phase_name":"descend_behind_peg","phase_type":"descend","tcp_position_centroid":[0.491,0.1488,0.03638]},{"body_a":"peg","body_b":"channel_base_body","contact_count":529.0,"contact_point_centroid":[0.49621,0.11916,0.00943],"force_p95":0.61921,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.55452,"phase_index":0.0,"phase_name":"approach_to_peg","phase_type":"approach","tcp_position_centroid":[0.49112,0.17981,0.21117]},{"body_a":"peg","body_b":"channel_base_body","contact_count":22.0,"contact_point_centroid":[0.51737,-0.10031,0.03453],"force_p95":1.58349,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.21761,"mean_force":0.26327,"phase_index":3.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.491,-0.03402,0.04951]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_to_peg","phase_type":"approach","tcp_position_centroid":[0.49944,0.1992,0.29785]}],"total_contact_groups":15},"final_pose_error":0.01099,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.4936,-0.07474,0.02409],"final_tcp_position":[0.49574,-0.0748,0.08131],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":146.72257,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":554.0,"n_steps_budget":1000.0,"object_pos_end":[0.49601,0.11897,0.03388],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.1991,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.5777,"phase_name":"approach_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":553.0,"raw_peak_contact_force":2.24822,"subtask_id":"approach","tcp_end":[0.48414,0.16123,0.12936],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.10508,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":530.0,"n_steps_budget":630.0,"object_pos_end":[0.49607,0.11873,0.03396],"object_pos_start":[0.49601,0.11897,0.03388],"object_to_goal_dist_end":0.19886,"object_to_goal_dist_start":0.1991,"object_z_max":0.03408,"peak_contact_force":0.56831,"phase_name":"descend_behind_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":536.0,"raw_peak_contact_force":3.9619,"subtask_id":"contact","tcp_end":[0.4911,0.14863,0.03516],"tcp_start":[0.48414,0.16123,0.12936],"tcp_to_object_dist_end":0.03034,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50735,-0.04404,0.04042],"object_pos_start":[0.49607,0.11873,0.03396],"object_to_goal_dist_end":0.03671,"object_to_goal_dist_start":0.19886,"object_z_max":0.04132,"peak_contact_force":123.46435,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3597.0,"raw_peak_contact_force":146.72257,"subtask_id":"push","tcp_end":[0.49226,-0.01104,0.0359],"tcp_start":[0.4911,0.14863,0.03516],"tcp_to_object_dist_end":0.03657,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":511.0,"n_steps_budget":600.0,"object_pos_end":[0.4936,-0.07474,0.02409],"object_pos_start":[0.50735,-0.04404,0.04042],"object_to_goal_dist_end":0.01794,"object_to_goal_dist_start":0.03671,"object_z_max":0.04107,"peak_contact_force":0.63678,"phase_name":"retract_from_channel","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":732.0,"raw_peak_contact_force":71.03796,"tcp_end":[0.49574,-0.0748,0.08131],"tcp_start":[0.49226,-0.01104,0.0359],"tcp_to_object_dist_end":0.05726,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `f85f1938a541e3d507519c8f918b8ca98f1f9baf6ab2f6f3ba2c32478e079e47`; realized-scene SHA-256: `a0d7ea14565b0a67e86de15fa43f3773b761884db645527685cd53e0fd95aeb9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.52962,0.06295,0.04]},{"name":"goal","value":[0.52962,-0.09705,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.52962,0.06295,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.52962,-0.09705,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.18943,"average_solve_count":227.0,"average_success_count":227.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_peg.speed":0.06408,"push_through_channel.push_distance":0.19426,"push_through_channel.push_speed":0.02842},"optimized_scores":{"best_composite_score":0.36041,"best_fitness_score":0.57041,"best_task_score":0.34629},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":49.0,"contact_point_centroid":[0.52513,0.09493,0.05994],"force_p95":365.84569,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":397.93742,"mean_force":289.93386,"phase_index":1.0,"phase_name":"descend_behind_peg","phase_type":"descend","tcp_position_centroid":[0.50481,0.09487,0.04357]},{"body_a":"channel_base_body","body_b":"link7","contact_count":39.0,"contact_point_centroid":[0.55198,-0.1,0.06499],"force_p95":160.40954,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":197.838,"mean_force":91.279,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50223,-0.07533,0.0398]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":101.0,"contact_point_centroid":[0.52501,-0.02544,0.06],"force_p95":120.5664,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":174.73103,"mean_force":88.89587,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50293,-0.02553,0.04094]},{"body_a":"channel_base_body","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.55159,-0.1,0.06499],"force_p95":68.23929,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":70.03374,"mean_force":51.86134,"phase_index":3.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.50251,-0.07987,0.04019]},{"body_a":"peg","body_b":"channel_base_body","contact_count":471.0,"contact_point_centroid":[0.49605,-0.02642,0.00902],"force_p95":48.30719,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":57.25888,"mean_force":20.46763,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50215,-0.00653,0.04012]},{"body_a":"attachment","body_b":"peg","contact_count":399.0,"contact_point_centroid":[0.50167,-0.01269,0.04299],"force_p95":53.7667,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":55.40816,"mean_force":25.79982,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50217,-0.00541,0.04014]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":4.0,"contact_point_centroid":[0.52501,-0.07981,0.05999],"force_p95":29.78519,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":35.0414,"mean_force":8.76035,"phase_index":3.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.50251,-0.0799,0.0402]},{"body_a":"attachment","body_b":"peg","contact_count":36.0,"contact_point_centroid":[0.50022,-0.0682,0.04244],"force_p95":15.05639,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":33.65632,"mean_force":5.11494,"phase_index":3.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.50147,-0.07995,0.04178]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":46.0,"contact_point_centroid":[0.47481,-0.06971,0.0265],"force_p95":14.48631,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":30.07413,"mean_force":5.31242,"phase_index":3.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.50118,-0.07992,0.04232]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":279.0,"contact_point_centroid":[0.47488,-0.04488,0.02621],"force_p95":24.21535,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.20872,"mean_force":13.97184,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.5024,-0.03344,0.04028]},{"body_a":"peg","body_b":"channel_base_body","contact_count":425.0,"contact_point_centroid":[0.501,-0.07056,0.00841],"force_p95":8.69591,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.55901,"mean_force":1.92224,"phase_index":3.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.49781,-0.07955,0.06073]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":20.0,"contact_point_centroid":[0.52533,0.04053,0.01929],"force_p95":10.91921,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.07863,"mean_force":1.95168,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50143,0.07031,0.03962]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":81.0,"contact_point_centroid":[0.52505,-0.07317,0.02544],"force_p95":8.44547,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.72274,"mean_force":4.8851,"phase_index":3.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.49663,-0.07951,0.07514]},{"body_a":"peg","body_b":"channel_base_body","contact_count":646.0,"contact_point_centroid":[0.50573,0.063,0.00936],"force_p95":0.56054,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.56751,"phase_index":0.0,"phase_name":"approach_to_peg","phase_type":"approach","tcp_position_centroid":[0.51163,0.15265,0.20885]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_to_peg","phase_type":"approach","tcp_position_centroid":[0.49984,0.19824,0.29664]},{"body_a":"peg","body_b":"channel_base_body","contact_count":404.0,"contact_point_centroid":[0.50612,0.06298,0.00938],"force_p95":0.55153,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55424,"mean_force":0.54656,"phase_index":1.0,"phase_name":"descend_behind_peg","phase_type":"descend","tcp_position_centroid":[0.51277,0.10091,0.08013]}],"total_contact_groups":16},"final_pose_error":0.00994,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50694,-0.07119,0.02517],"final_tcp_position":[0.49643,-0.07954,0.08073],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":397.93742,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":674.0,"n_steps_budget":1000.0,"object_pos_end":[0.50602,0.06303,0.0338],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14329,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.55119,"phase_name":"approach_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":680.0,"raw_peak_contact_force":3.88411,"subtask_id":"approach","tcp_end":[0.52435,0.10858,0.12634],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.10476,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":404.0,"n_steps_budget":630.0,"object_pos_end":[0.50598,0.06294,0.03381],"object_pos_start":[0.50602,0.06303,0.0338],"object_to_goal_dist_end":0.1432,"object_to_goal_dist_start":0.14329,"object_z_max":0.03381,"peak_contact_force":329.68508,"phase_name":"descend_behind_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":453.0,"raw_peak_contact_force":397.93742,"subtask_id":"contact","tcp_end":[0.50433,0.09486,0.04327],"tcp_start":[0.52435,0.10858,0.12634],"tcp_to_object_dist_end":0.03334,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":541.0,"n_steps_budget":1000.0,"object_pos_end":[0.49276,-0.0709,0.02506],"object_pos_start":[0.50598,0.06294,0.03381],"object_to_goal_dist_end":0.01894,"object_to_goal_dist_start":0.1432,"object_z_max":0.04031,"peak_contact_force":83.64455,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1309.0,"raw_peak_contact_force":197.838,"subtask_id":"push","tcp_end":[0.5025,-0.0798,0.04018],"tcp_start":[0.50433,0.09486,0.04327],"tcp_to_object_dist_end":0.02007,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":425.0,"n_steps_budget":600.0,"object_pos_end":[0.50694,-0.07119,0.02517],"object_pos_start":[0.49276,-0.0709,0.02506],"object_to_goal_dist_end":0.01859,"object_to_goal_dist_start":0.01894,"object_z_max":0.02745,"peak_contact_force":0.54702,"phase_name":"retract_from_channel","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":595.0,"raw_peak_contact_force":70.03374,"tcp_end":[0.49643,-0.07954,0.08073],"tcp_start":[0.5025,-0.0798,0.04018],"tcp_to_object_dist_end":0.05716,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```