## Search State

- **Seed**: 1
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → descend → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 3 | 0.2301 | 0.24 | ❌ rejected |
| 4 | approach → descend → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 3 | 0.0455 | 0.01 | ❌ rejected |
| 3 | approach → contact → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 3 | -0.1122 | 0.00 | ❌ rejected |
| 2 | approach → align → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 3 | 0.1558 | 0.00 | ❌ rejected |
| 1 | approach → contact → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 4 | 0.1088 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.24 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.230) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
phases:
- id: approach_1
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
    - 0.04
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  subtask_id: approach
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.02
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    contact_force:
      type: scalar
      range:
      - 1.0
      - 20.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
  subtask_id: contact
- id: push_1
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: world
    offset:
    - 0.5
    - -0.08
    - 0.04
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    push_depth:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: add
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: push

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.04, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none
- **contact_1** (`contact`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.02, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=world, offset=[0.5, -0.08, 0.04], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_depth: status=consumed; consumers=target.offset.y (add)
    - push_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.230
- **task_score** (E): 0.244
- **fitness_score**: 0.190  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.210

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_high | 1.00 | 1.00 | 0.0890 |
| descend_to_peg | 1.00 | 1.00 | 0.1822 |
| contact_peg | 1.00 | 1.00 | 0.0321 |
| push_channel | 0.00 | 1.00 | 0.0436 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_high | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.498, 0.126, 0.251) | (0.483, 0.080, 0.040)→(0.497, 0.080, 0.034) | 0.161→0.160 | 1.00 / 1.000 | 0.537 | 2.857 |
| descend_to_peg | descend | 1.00 / step_budget | (0.498, 0.126, 0.251)→(0.496, 0.116, 0.069) | (0.497, 0.080, 0.034)→(0.497, 0.080, 0.034) | 0.160→0.160 | 1.00 / 1.000 | 0.539 | 0.590 |
| contact_peg | contact | 1.00 / force_exceeded | (0.496, 0.116, 0.069)→(0.492, 0.098, 0.044) | (0.497, 0.080, 0.034)→(0.496, 0.077, 0.034) | 0.160→0.157 | 1.00 / 2.000 | 8.390 | 9.590 |
| push_channel | push | 0.00 / step_budget | (0.492, 0.098, 0.044)→(0.518, 0.081, 0.067) | (0.496, 0.077, 0.034)→(0.495, 0.003, 0.026) | 0.157→0.088 | 1.00 / 3.000 | 492.407 | 2293.022 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.631
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.370
- phase_score: 0.180
- phase_breakdown.approach_score: 0.014
- phase_breakdown.push_score: 0.037
- phase_breakdown.contact_score: 0.771

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.256
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.370
- **Median Q (composite search score)**: 0.241
- **K-run variance**: 0.0034
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.387


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.91071,"average_solve_count":112.0,"average_success_count":112.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_peg.contact_force":4.15187,"push_channel.push_depth":0.01937,"push_channel.push_speed":0.07653},"optimized_scores":{"best_composite_score":0.15395,"best_fitness_score":0.11395,"best_task_score":0.07564},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":561.0,"contact_point_centroid":[0.52521,0.08354,0.05995],"force_p95":407.56646,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":790.49019,"mean_force":385.79603,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.5136,0.08202,0.06148]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":830.0,"contact_point_centroid":[0.47492,0.11987,0.05999],"force_p95":545.90881,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":572.23617,"mean_force":409.32123,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51196,0.08014,0.06167]},{"body_a":"attachment","body_b":"peg","contact_count":978.0,"contact_point_centroid":[0.50969,0.0973,0.05305],"force_p95":226.31962,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":367.00149,"mean_force":152.95539,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51121,0.08339,0.06144]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50745,0.09667,0.00791],"force_p95":231.18231,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":328.43087,"mean_force":149.81518,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.5114,0.08405,0.06149]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":118.0,"contact_point_centroid":[0.525,0.11989,0.06],"force_p95":74.68809,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":111.8907,"mean_force":24.5645,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50831,0.07887,0.06216]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":761.0,"contact_point_centroid":[0.47476,0.10247,0.01032],"force_p95":44.5467,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":82.86926,"mean_force":10.53882,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51154,0.08178,0.06114]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":25.0,"contact_point_centroid":[0.52706,0.11295,0.05624],"force_p95":64.32001,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":68.14631,"mean_force":19.79621,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51648,0.11193,0.06014]},{"body_a":"peg","body_b":"link7","contact_count":624.0,"contact_point_centroid":[0.49319,0.11892,0.05703],"force_p95":6.29502,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":30.26799,"mean_force":3.49149,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51304,0.08028,0.06141]},{"body_a":"peg","body_b":"world","contact_count":22.0,"contact_point_centroid":[0.49497,0.09841,-0.00013],"force_p95":22.95654,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":24.10905,"mean_force":6.15045,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50341,0.1014,0.05678]},{"body_a":"peg","body_b":"channel_base_body","contact_count":53.0,"contact_point_centroid":[0.5004,0.11602,0.0094],"force_p95":0.61606,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.69157,"mean_force":0.81153,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49521,0.11679,0.06462]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50643,0.11783,0.05881],"force_p95":14.19248,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.19248,"mean_force":14.19248,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49458,0.11816,0.06063]},{"body_a":"peg","body_b":"channel_base_body","contact_count":304.0,"contact_point_centroid":[0.50105,0.11608,0.00933],"force_p95":0.68057,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.57147,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.49812,0.16138,0.27304]},{"body_a":"peg","body_b":"channel_base_body","contact_count":569.0,"contact_point_centroid":[0.50092,0.11595,0.00941],"force_p95":0.60397,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.66438,"mean_force":0.54328,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.49623,0.12055,0.15985]}],"total_contact_groups":13},"final_pose_error":0.14578,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49313,0.10211,0.03123],"final_tcp_position":[0.51359,0.08275,0.06251],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":790.49019,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":320.0,"n_steps_budget":630.0,"object_pos_end":[0.50097,0.11601,0.03382],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19611,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.51895,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":304.0,"raw_peak_contact_force":1.92055,"tcp_end":[0.49777,0.12555,0.25103],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.21744,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":569.0,"n_steps_budget":1000.0,"object_pos_end":[0.50092,0.11602,0.03382],"object_pos_start":[0.50097,0.11601,0.03382],"object_to_goal_dist_end":0.19612,"object_to_goal_dist_start":0.19611,"object_z_max":0.034,"peak_contact_force":0.52814,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":569.0,"raw_peak_contact_force":0.66438,"tcp_end":[0.49641,0.1159,0.06907],"tcp_start":[0.49777,0.12555,0.25103],"tcp_to_object_dist_end":0.03554,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":53.0,"n_steps_budget":600.0,"object_pos_end":[0.50092,0.11605,0.03383],"object_pos_start":[0.50092,0.11602,0.03382],"object_to_goal_dist_end":0.19615,"object_to_goal_dist_start":0.19612,"object_z_max":0.03386,"peak_contact_force":14.69157,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":54.0,"raw_peak_contact_force":14.69157,"subtask_id":"contact","tcp_end":[0.49457,0.11822,0.06049],"tcp_start":[0.49641,0.1159,0.06907],"tcp_to_object_dist_end":0.0275,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49313,0.10211,0.03123],"object_pos_start":[0.50092,0.11605,0.03383],"object_to_goal_dist_end":0.18245,"object_to_goal_dist_start":0.19615,"object_z_max":0.03535,"peak_contact_force":539.17251,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4919.0,"raw_peak_contact_force":790.49019,"subtask_id":"push","tcp_end":[0.51359,0.08275,0.06251],"tcp_start":[0.49457,0.11822,0.06049],"tcp_to_object_dist_end":0.04208,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.8087,"average_solve_count":115.0,"average_success_count":115.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_peg.contact_force":18.96855,"push_channel.push_depth":0.01022,"push_channel.push_speed":0.09778},"optimized_scores":{"best_composite_score":0.29561,"best_fitness_score":0.25561,"best_task_score":0.36964},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":742.0,"contact_point_centroid":[0.52562,0.11895,0.0599],"force_p95":451.82924,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2729.29238,"mean_force":364.10763,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.52195,0.0726,0.08034]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":17.0,"contact_point_centroid":[0.52579,0.07115,0.05986],"force_p95":2654.13602,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2713.3533,"mean_force":1189.74062,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50864,0.06405,0.02743]},{"body_a":"attachment","body_b":"peg","contact_count":9.0,"contact_point_centroid":[0.49679,0.06964,0.03909],"force_p95":25.72345,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":27.19272,"mean_force":11.89881,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49686,0.08084,0.03056]},{"body_a":"peg","body_b":"channel_base_body","contact_count":749.0,"contact_point_centroid":[0.5008,-0.01723,0.00816],"force_p95":0.89263,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.17686,"mean_force":0.74168,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.52181,0.07276,0.08047]},{"body_a":"peg","body_b":"channel_base_body","contact_count":306.0,"contact_point_centroid":[0.49511,0.06045,0.00948],"force_p95":2.57254,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.8035,"mean_force":0.76926,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49269,0.10145,0.05002]},{"body_a":"attachment","body_b":"peg","contact_count":37.0,"contact_point_centroid":[0.4932,0.07854,0.04546],"force_p95":5.92684,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.39143,"mean_force":2.11904,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49168,0.09048,0.03753]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":14.0,"contact_point_centroid":[0.52522,-0.02756,0.04046],"force_p95":3.34198,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.33598,"mean_force":1.19313,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50949,0.06902,0.05444]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":25.0,"contact_point_centroid":[0.47479,0.01153,0.03807],"force_p95":2.0688,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.57489,"mean_force":0.85326,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50714,0.069,0.04784]},{"body_a":"peg","body_b":"channel_base_body","contact_count":293.0,"contact_point_centroid":[0.49552,0.06387,0.00935],"force_p95":0.65171,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.5744,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.49808,0.16008,0.27216]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.49944,0.19743,0.298]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":48.0,"contact_point_centroid":[0.47478,0.05933,0.03699],"force_p95":0.75243,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.15738,"mean_force":0.27841,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49164,0.08933,0.03626]},{"body_a":"peg","body_b":"channel_base_body","contact_count":569.0,"contact_point_centroid":[0.49507,0.06384,0.0094],"force_p95":0.55023,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55295,"mean_force":0.54559,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.49623,0.12055,0.15985]}],"total_contact_groups":12},"final_pose_error":0.15436,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50018,-0.01888,0.02413],"final_tcp_position":[0.52837,0.0755,0.08378],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":2729.29238,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":320.0,"n_steps_budget":630.0,"object_pos_end":[0.49515,0.06371,0.03391],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14392,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.54524,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":321.0,"raw_peak_contact_force":2.44546,"tcp_end":[0.49777,0.12555,0.25103],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.22577,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":569.0,"n_steps_budget":1000.0,"object_pos_end":[0.49523,0.06365,0.034],"object_pos_start":[0.49515,0.06371,0.03391],"object_to_goal_dist_end":0.14385,"object_to_goal_dist_start":0.14392,"object_z_max":0.034,"peak_contact_force":0.54019,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":569.0,"raw_peak_contact_force":0.55295,"tcp_end":[0.49641,0.1159,0.06907],"tcp_start":[0.49777,0.12555,0.25103],"tcp_to_object_dist_end":0.06295,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":317.0,"n_steps_budget":600.0,"object_pos_end":[0.49333,0.0571,0.03468],"object_pos_start":[0.49523,0.06365,0.034],"object_to_goal_dist_end":0.13737,"object_to_goal_dist_start":0.14385,"object_z_max":0.0354,"peak_contact_force":3.20304,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":391.0,"raw_peak_contact_force":6.8035,"subtask_id":"contact","tcp_end":[0.49151,0.08696,0.03368],"tcp_start":[0.49641,0.1159,0.06907],"tcp_to_object_dist_end":0.02993,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":780.0,"n_steps_budget":1000.0,"object_pos_end":[0.50018,-0.01888,0.02413],"object_pos_start":[0.49333,0.0571,0.03468],"object_to_goal_dist_end":0.06315,"object_to_goal_dist_start":0.13737,"object_z_max":0.0422,"peak_contact_force":332.51296,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1556.0,"raw_peak_contact_force":2729.29238,"subtask_id":"push","tcp_end":[0.52837,0.0755,0.08378],"tcp_start":[0.49151,0.08696,0.03368],"tcp_to_object_dist_end":0.11516,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.66667,"average_solve_count":123.0,"average_success_count":123.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_peg.contact_force":2.69332,"push_channel.push_depth":-0.005,"push_channel.push_speed":0.06761},"optimized_scores":{"best_composite_score":0.24073,"best_fitness_score":0.20073,"best_task_score":0.28561},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":281.0,"contact_point_centroid":[0.52805,0.11772,0.0598],"force_p95":826.78409,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3359.28484,"mean_force":437.86328,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51113,0.07594,0.06033]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":765.0,"contact_point_centroid":[0.52514,0.08217,0.05558],"force_p95":544.53909,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2979.82509,"mean_force":439.6663,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51333,0.08068,0.05516]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":712.0,"contact_point_centroid":[0.47493,0.11988,0.05621],"force_p95":595.27288,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":617.1568,"mean_force":565.58658,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51328,0.08118,0.05523]},{"body_a":"peg","body_b":"channel_base_body","contact_count":939.0,"contact_point_centroid":[0.49437,-0.07094,0.00825],"force_p95":0.75675,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":68.5901,"mean_force":0.88611,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51268,0.08004,0.05729]},{"body_a":"attachment","body_b":"peg","contact_count":12.0,"contact_point_centroid":[0.4992,0.07031,0.05394],"force_p95":56.3209,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":67.27702,"mean_force":14.83375,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.4983,0.08036,0.03463]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":31.0,"contact_point_centroid":[0.47499,-0.05691,0.02431],"force_p95":9.18309,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.4491,"mean_force":3.41584,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51323,0.08087,0.05728]},{"body_a":"peg","body_b":"channel_base_body","contact_count":284.0,"contact_point_centroid":[0.49389,0.05867,0.00939],"force_p95":0.55077,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.27593,"mean_force":0.57,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49235,0.10184,0.0523]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.49374,0.077,0.05679],"force_p95":6.20412,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.88334,"mean_force":2.35142,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49085,0.08904,0.03954]},{"body_a":"peg","body_b":"channel_base_body","contact_count":291.0,"contact_point_centroid":[0.49474,0.059,0.00932],"force_p95":0.63923,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.59645,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.49807,0.15985,0.272]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.49935,0.19666,0.29729]},{"body_a":"peg","body_b":"channel_base_body","contact_count":12.0,"contact_point_centroid":[0.49574,-0.10009,0.0246],"force_p95":2.48735,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.75892,"mean_force":0.98216,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51134,0.07448,0.07343]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":14.0,"contact_point_centroid":[0.52552,-0.00916,0.03038],"force_p95":1.93971,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.05719,"mean_force":0.97661,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50542,0.06629,0.0329]},{"body_a":"peg","body_b":"channel_base_body","contact_count":569.0,"contact_point_centroid":[0.49408,0.05903,0.00939],"force_p95":0.55035,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55382,"mean_force":0.54614,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.49623,0.12055,0.15985]}],"total_contact_groups":13},"final_pose_error":0.17024,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49304,-0.0729,0.02413],"final_tcp_position":[0.51338,0.08415,0.0538],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":3359.28484,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":320.0,"n_steps_budget":630.0,"object_pos_end":[0.49408,0.05905,0.03385],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13931,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54744,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":326.0,"raw_peak_contact_force":4.20518,"tcp_end":[0.49777,0.12555,0.25103],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.22717,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":569.0,"n_steps_budget":1000.0,"object_pos_end":[0.49395,0.05897,0.03391],"object_pos_start":[0.49408,0.05905,0.03385],"object_to_goal_dist_end":0.13924,"object_to_goal_dist_start":0.13931,"object_z_max":0.03391,"peak_contact_force":0.54806,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":569.0,"raw_peak_contact_force":0.55382,"tcp_end":[0.49641,0.1159,0.06907],"tcp_start":[0.49777,0.12555,0.25103],"tcp_to_object_dist_end":0.06696,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":284.0,"n_steps_budget":600.0,"object_pos_end":[0.49421,0.05869,0.03398],"object_pos_start":[0.49395,0.05897,0.03391],"object_to_goal_dist_end":0.13894,"object_to_goal_dist_start":0.13924,"object_z_max":0.03395,"peak_contact_force":7.27593,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":287.0,"raw_peak_contact_force":7.27593,"subtask_id":"contact","tcp_end":[0.49079,0.08846,0.03899],"tcp_start":[0.49641,0.1159,0.06907],"tcp_to_object_dist_end":0.03039,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49304,-0.0729,0.02413],"object_pos_start":[0.49421,0.05869,0.03398],"object_to_goal_dist_end":0.01873,"object_to_goal_dist_start":0.13894,"object_z_max":0.04089,"peak_contact_force":605.53483,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2766.0,"raw_peak_contact_force":3359.28484,"subtask_id":"push","tcp_end":[0.51338,0.08415,0.0538],"tcp_start":[0.49079,0.08846,0.03899],"tcp_to_object_dist_end":0.16112,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```