## Search State

- **Seed**: 1
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → descend → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 3 | 0.3732 | 0.28 | ❌ rejected |
| 5 | approach → descend → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 3 | 0.2301 | 0.24 | ❌ rejected |
| 4 | approach → descend → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 3 | 0.0455 | 0.01 | ❌ rejected |
| 3 | approach → contact → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 3 | -0.1122 | 0.00 | ❌ rejected |
| 2 | approach → align → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 3 | 0.1558 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.28 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.373) — your mutation base

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

- **Composite score**: 0.373
- **task_score** (E): 0.284
- **fitness_score**: 0.500  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.083
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.210

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_high | 1.00 | 1.00 | 0.0946 |
| descend_to_peg | 1.00 | 1.00 | 0.2014 |
| contact_peg | 0.33 | 1.00 | 0.0091 |
| push_channel | 0.33 | 1.00 | 0.1813 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_high | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.482, 0.129, 0.243) | (0.483, 0.080, 0.040)→(0.497, 0.080, 0.034) | 0.161→0.160 | 1.00 / 1.000 | 0.550 | 2.857 |
| descend_to_peg | descend | 1.00 / step_budget | (0.482, 0.129, 0.243)→(0.499, 0.104, 0.044) | (0.497, 0.080, 0.034)→(0.498, 0.074, 0.033) | 0.160→0.154 | 1.00 / 2.333 | 40.128 | 194.700 |
| contact_peg | contact | 0.33 / step_budget | (0.499, 0.104, 0.044)→(0.496, 0.098, 0.038) | (0.498, 0.074, 0.033)→(0.504, 0.070, 0.035) | 0.154→0.150 | 1.00 / 1.667 | 35.821 | 38.979 |
| push_channel | push | 0.33 / step_budget | (0.496, 0.098, 0.038)→(0.494, -0.083, 0.034) | (0.504, 0.070, 0.035)→(0.506, -0.028, 0.033) | 0.150→0.054 | 1.00 / 3.333 | 262.028 | 448.073 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.489
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.489
- phase_score: 0.741
- phase_breakdown.approach_score: 0.016
- phase_breakdown.push_score: 0.952
- phase_breakdown.contact_score: 0.833

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.640
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.489
- **Median Q (composite search score)**: 0.257
- **K-run variance**: 0.0481
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.406


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.30636,"average_solve_count":173.0,"average_success_count":173.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_peg.contact_force":3.44931,"push_channel.push_distance":0.23944,"push_channel.push_speed":0.04482},"optimized_scores":{"best_composite_score":0.68026,"best_fitness_score":0.64026,"best_task_score":0.48924},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":672.0,"contact_point_centroid":[0.50212,0.1165,0.00922],"force_p95":140.55362,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":190.46596,"mean_force":17.4631,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.49744,0.14965,0.13832]},{"body_a":"attachment","body_b":"peg","contact_count":96.0,"contact_point_centroid":[0.50773,0.1323,0.05265],"force_p95":178.09266,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":189.61512,"mean_force":118.70204,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50033,0.1408,0.05188]},{"body_a":"peg","body_b":"channel_base_body","contact_count":676.0,"contact_point_centroid":[0.50839,0.06917,0.0081],"force_p95":157.1777,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":166.41502,"mean_force":81.18483,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50594,0.04523,0.04777]},{"body_a":"attachment","body_b":"peg","contact_count":443.0,"contact_point_centroid":[0.51618,0.08867,0.05266],"force_p95":158.88008,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":165.9461,"mean_force":123.16591,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50868,0.08612,0.05096]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.49236,0.11891,0.00653],"force_p95":105.92563,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":105.92563,"mean_force":105.92563,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50329,0.14289,0.04549]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50749,0.13256,0.0477],"force_p95":105.01502,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":105.01502,"mean_force":105.01502,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50329,0.14289,0.04549]},{"body_a":"peg","body_b":"world","contact_count":1.0,"contact_point_centroid":[0.50296,0.12795,-3e-05],"force_p95":22.06259,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.06259,"mean_force":22.06259,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50324,0.14285,0.04558]},{"body_a":"peg","body_b":"world","contact_count":5.0,"contact_point_centroid":[0.50306,0.12789,-3e-05],"force_p95":11.89511,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.34663,"mean_force":8.75912,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50335,0.14302,0.04547]},{"body_a":"peg","body_b":"channel_base_body","contact_count":196.0,"contact_point_centroid":[0.50088,0.11605,0.00931],"force_p95":0.86145,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.58544,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.49866,0.18107,0.27107]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":6.0,"contact_point_centroid":[0.47496,0.01324,0.0249],"force_p95":0.58675,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.6064,"mean_force":0.43639,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50133,-0.0065,0.04232]},{"body_a":"peg","body_b":"world","contact_count":1.0,"contact_point_centroid":[0.50306,0.12792,-5e-05],"force_p95":0.0,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50329,0.14289,0.04549]}],"total_contact_groups":11},"final_pose_error":0.01975,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50113,0.03776,0.02418],"final_tcp_position":[0.49983,-0.07765,0.04076],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":190.46596,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":212.0,"n_steps_budget":600.0,"object_pos_end":[0.50096,0.11599,0.03393],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19609,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.55818,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":196.0,"raw_peak_contact_force":1.92055,"subtask_id":"approach","tcp_end":[0.49853,0.16339,0.24598],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.21729,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":672.0,"n_steps_budget":1000.0,"object_pos_end":[0.50321,0.11822,0.02913],"object_pos_start":[0.50096,0.11599,0.03393],"object_to_goal_dist_end":0.19855,"object_to_goal_dist_start":0.19609,"object_z_max":0.03404,"peak_contact_force":118.278,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":769.0,"raw_peak_contact_force":190.46596,"tcp_end":[0.50329,0.14289,0.04549],"tcp_start":[0.49853,0.16339,0.24598],"tcp_to_object_dist_end":0.0296,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.50322,0.11825,0.02915],"object_pos_start":[0.50321,0.11822,0.02913],"object_to_goal_dist_end":0.19857,"object_to_goal_dist_start":0.19855,"object_z_max":0.02913,"peak_contact_force":105.92563,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3.0,"raw_peak_contact_force":105.92563,"subtask_id":"contact","tcp_end":[0.50333,0.14293,0.04546],"tcp_start":[0.50329,0.14289,0.04549],"tcp_to_object_dist_end":0.02958,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":684.0,"n_steps_budget":1000.0,"object_pos_end":[0.50113,0.03776,0.02418],"object_pos_start":[0.50322,0.11825,0.02915],"object_to_goal_dist_end":0.11882,"object_to_goal_dist_start":0.19857,"object_z_max":0.03964,"peak_contact_force":0.64536,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1130.0,"raw_peak_contact_force":166.41502,"tcp_end":[0.49983,-0.07765,0.04076],"tcp_start":[0.50333,0.14293,0.04546],"tcp_to_object_dist_end":0.1166,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.66013,"average_solve_count":153.0,"average_success_count":153.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_peg.contact_force":12.27706,"push_channel.push_distance":0.24841,"push_channel.push_speed":0.07561},"optimized_scores":{"best_composite_score":0.25715,"best_fitness_score":0.46715,"best_task_score":0.24761},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_base_body","contact_count":141.0,"contact_point_centroid":[0.49765,-0.10016,0.06499],"force_p95":645.90379,"geom_a":"pusher_tip","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":702.46393,"mean_force":333.5959,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49156,-0.08663,0.03069]},{"body_a":"channel_base_body","body_b":"link7","contact_count":560.0,"contact_point_centroid":[0.53086,-0.10001,0.06493],"force_p95":415.89003,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":598.63819,"mean_force":259.52023,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48899,-0.07866,0.02936]},{"body_a":"attachment","body_b":"peg","contact_count":886.0,"contact_point_centroid":[0.49972,-0.05908,0.05098],"force_p95":216.81376,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":250.74158,"mean_force":110.0249,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48887,-0.05483,0.02949]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":915.0,"contact_point_centroid":[0.52727,-0.06427,0.04533],"force_p95":206.46177,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":216.54153,"mean_force":86.55302,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48882,-0.05374,0.02945]},{"body_a":"peg","body_b":"channel_base_body","contact_count":696.0,"contact_point_centroid":[0.49645,0.06499,0.00924],"force_p95":158.44436,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":195.0992,"mean_force":17.20126,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.48571,0.09876,0.1361]},{"body_a":"attachment","body_b":"peg","contact_count":95.0,"contact_point_centroid":[0.50272,0.08003,0.05475],"force_p95":193.80776,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":194.6571,"mean_force":122.0305,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.4946,0.08781,0.0534]},{"body_a":"peg","body_b":"channel_base_body","contact_count":515.0,"contact_point_centroid":[0.51279,-0.10194,0.04901],"force_p95":113.07042,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":131.65279,"mean_force":77.15124,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48802,-0.074,0.02883]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":46.0,"contact_point_centroid":[0.47499,-0.06633,0.02955],"force_p95":89.68031,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":103.17554,"mean_force":42.03592,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48683,-0.06631,0.02769]},{"body_a":"peg","body_b":"channel_base_body","contact_count":678.0,"contact_point_centroid":[0.52007,-0.07402,0.00947],"force_p95":47.34212,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":91.98677,"mean_force":24.69104,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48873,-0.05987,0.02938]},{"body_a":"peg","body_b":"link7","contact_count":11.0,"contact_point_centroid":[0.52353,-0.0742,0.06664],"force_p95":11.4309,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.72726,"mean_force":5.75059,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.4917,-0.08635,0.03068]},{"body_a":"peg","body_b":"channel_base_body","contact_count":75.0,"contact_point_centroid":[0.50062,0.04242,0.00956],"force_p95":4.1537,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.51862,"mean_force":0.91843,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49428,0.0831,0.03879]},{"body_a":"attachment","body_b":"peg","contact_count":27.0,"contact_point_centroid":[0.49711,0.06895,0.03509],"force_p95":4.45836,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.00511,"mean_force":1.29566,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49284,0.08005,0.03573]},{"body_a":"peg","body_b":"channel_base_body","contact_count":340.0,"contact_point_centroid":[0.49578,0.06389,0.00935],"force_p95":0.62852,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.57044,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.48909,0.15416,0.26742]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":4.0,"contact_point_centroid":[0.4746,0.04989,0.05635],"force_p95":2.07954,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.13096,"mean_force":1.61832,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.4973,0.08676,0.04421]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.49898,0.19741,0.29793]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":7.0,"contact_point_centroid":[0.47459,0.04696,0.05759],"force_p95":0.76717,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.83866,"mean_force":0.328,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49652,0.08643,0.0429]}],"total_contact_groups":17},"final_pose_error":0.0844,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50853,-0.05875,0.03895],"final_tcp_position":[0.49197,-0.08599,0.03107],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":702.46393,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":367.0,"n_steps_budget":720.0,"object_pos_end":[0.49507,0.06405,0.03392],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14427,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.546,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":368.0,"raw_peak_contact_force":2.44546,"subtask_id":"approach","tcp_end":[0.4807,0.11359,0.24172],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.2141,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":696.0,"n_steps_budget":1000.0,"object_pos_end":[0.49479,0.05391,0.035],"object_pos_start":[0.49507,0.06405,0.03392],"object_to_goal_dist_end":0.13411,"object_to_goal_dist_start":0.14427,"object_z_max":0.03469,"peak_contact_force":1.118,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":795.0,"raw_peak_contact_force":195.0992,"tcp_end":[0.49698,0.0866,0.04347],"tcp_start":[0.4807,0.11359,0.24172],"tcp_to_object_dist_end":0.03383,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":93.0,"n_steps_budget":600.0,"object_pos_end":[0.50366,0.04868,0.03828],"object_pos_start":[0.49479,0.05391,0.035],"object_to_goal_dist_end":0.12874,"object_to_goal_dist_start":0.13411,"object_z_max":0.04001,"peak_contact_force":0.68853,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":114.0,"raw_peak_contact_force":5.51862,"subtask_id":"contact","tcp_end":[0.49219,0.07807,0.03408],"tcp_start":[0.49698,0.0866,0.04347],"tcp_to_object_dist_end":0.03183,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50853,-0.05875,0.03895],"object_pos_start":[0.50366,0.04868,0.03828],"object_to_goal_dist_end":0.02292,"object_to_goal_dist_start":0.12874,"object_z_max":0.03948,"peak_contact_force":418.19979,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3752.0,"raw_peak_contact_force":702.46393,"tcp_end":[0.49197,-0.08599,0.03107],"tcp_start":[0.49219,0.07807,0.03408],"tcp_to_object_dist_end":0.03283,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.66234,"average_solve_count":154.0,"average_success_count":154.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_peg.contact_force":18.53514,"push_channel.push_distance":0.24997,"push_channel.push_speed":0.07655},"optimized_scores":{"best_composite_score":0.18205,"best_fitness_score":0.39205,"best_task_score":0.11661},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_base_body","body_b":"link7","contact_count":560.0,"contact_point_centroid":[0.53121,-0.1,0.06494],"force_p95":373.17982,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":475.3402,"mean_force":247.01335,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48913,-0.07842,0.02923]},{"body_a":"attachment","body_b":"channel_base_body","contact_count":128.0,"contact_point_centroid":[0.49703,-0.1001,0.065],"force_p95":423.50349,"geom_a":"pusher_tip","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":467.26095,"mean_force":282.22177,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49105,-0.08644,0.03048]},{"body_a":"attachment","body_b":"peg","contact_count":916.0,"contact_point_centroid":[0.4998,-0.05921,0.05297],"force_p95":225.96218,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":240.88761,"mean_force":116.34236,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48874,-0.05439,0.02929]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":929.0,"contact_point_centroid":[0.52733,-0.06581,0.04804],"force_p95":216.52399,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":222.16357,"mean_force":92.4589,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48869,-0.05452,0.02924]},{"body_a":"peg","body_b":"channel_base_body","contact_count":716.0,"contact_point_centroid":[0.49545,0.06027,0.00924],"force_p95":161.20208,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":198.53606,"mean_force":17.40367,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.47877,0.09381,0.13608]},{"body_a":"attachment","body_b":"peg","contact_count":97.0,"contact_point_centroid":[0.5011,0.07531,0.05458],"force_p95":196.24946,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":198.05907,"mean_force":124.44305,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.49266,0.08273,0.05324]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":61.0,"contact_point_centroid":[0.47499,-0.06578,0.02953],"force_p95":120.17648,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":161.54988,"mean_force":61.85546,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48683,-0.06576,0.02769]},{"body_a":"peg","body_b":"channel_base_body","contact_count":559.0,"contact_point_centroid":[0.51293,-0.10184,0.04889],"force_p95":114.81269,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":143.68248,"mean_force":73.58082,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48837,-0.07411,0.02877]},{"body_a":"peg","body_b":"channel_base_body","contact_count":715.0,"contact_point_centroid":[0.51962,-0.0801,0.00952],"force_p95":47.51276,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":94.15195,"mean_force":25.15992,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48862,-0.06128,0.02911]},{"body_a":"peg","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.52117,-0.01056,0.06654],"force_p95":9.49915,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.9672,"mean_force":4.23395,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48991,-0.00185,0.0307]},{"body_a":"peg","body_b":"channel_base_body","contact_count":77.0,"contact_point_centroid":[0.50082,0.03772,0.00953],"force_p95":3.62271,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.49244,"mean_force":0.84994,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49332,0.07819,0.03877]},{"body_a":"attachment","body_b":"peg","contact_count":24.0,"contact_point_centroid":[0.49643,0.06416,0.03496],"force_p95":4.44319,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.94421,"mean_force":1.26089,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49211,0.07522,0.0356]},{"body_a":"peg","body_b":"channel_base_body","contact_count":363.0,"contact_point_centroid":[0.4946,0.05904,0.00934],"force_p95":0.60601,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.5865,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.48242,0.15162,0.26735]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.49837,0.19668,0.29731]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":4.0,"contact_point_centroid":[0.47473,0.04541,0.05648],"force_p95":1.88055,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.93193,"mean_force":1.44748,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.49613,0.08181,0.04438]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":6.0,"contact_point_centroid":[0.47473,0.04249,0.05768],"force_p95":0.67608,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.73146,"mean_force":0.32146,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49541,0.08151,0.04314]}],"total_contact_groups":16},"final_pose_error":0.09089,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50918,-0.06166,0.03693],"final_tcp_position":[0.49154,-0.08598,0.03061],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":475.3402,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":392.0,"n_steps_budget":780.0,"object_pos_end":[0.49404,0.05902,0.03385],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13929,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54503,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":398.0,"raw_peak_contact_force":4.20518,"subtask_id":"approach","tcp_end":[0.46801,0.10871,0.24164],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.21523,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":716.0,"n_steps_budget":1000.0,"object_pos_end":[0.4946,0.04929,0.03467],"object_pos_start":[0.49404,0.05902,0.03385],"object_to_goal_dist_end":0.12951,"object_to_goal_dist_start":0.13929,"object_z_max":0.03435,"peak_contact_force":0.98865,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":817.0,"raw_peak_contact_force":198.53606,"tcp_end":[0.49581,0.08165,0.04363],"tcp_start":[0.46801,0.10871,0.24164],"tcp_to_object_dist_end":0.0336,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":97.0,"n_steps_budget":600.0,"object_pos_end":[0.50382,0.04385,0.03788],"object_pos_start":[0.4946,0.04929,0.03467],"object_to_goal_dist_end":0.12393,"object_to_goal_dist_start":0.12951,"object_z_max":0.04019,"peak_contact_force":0.85011,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":107.0,"raw_peak_contact_force":5.49244,"subtask_id":"contact","tcp_end":[0.49158,0.07315,0.03376],"tcp_start":[0.49581,0.08165,0.04363],"tcp_to_object_dist_end":0.03202,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50918,-0.06166,0.03693],"object_pos_start":[0.50382,0.04385,0.03788],"object_to_goal_dist_end":0.02074,"object_to_goal_dist_start":0.12393,"object_z_max":0.03969,"peak_contact_force":367.23777,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3873.0,"raw_peak_contact_force":475.3402,"tcp_end":[0.49154,-0.08598,0.03061],"tcp_start":[0.49158,0.07315,0.03376],"tcp_to_object_dist_end":0.0307,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```