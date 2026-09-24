## Search State

- **Seed**: 9
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | contact_detected | time_limit | 5 | -0.1432 | 0.00 | ❌ rejected |
| 0 | rotate → pull → push → descend → descend → grasp | arc_cartesian | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | impedance_control | impedance_control | position_control | admittance_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | contact_detected | grasp_success | 5 | -0.2578 | 0.06 | ✅ accepted |

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

## Current Skill (Q=-0.143) — your mutation base

```yaml
skill: peg_channel
skill_type: arm_gripper
phases:
- id: rotate_1
  type: rotate
  generator: arc_cartesian
  control: impedance_control
  termination: time_limit
- id: pull_1
  type: pull
  generator: arc_cartesian
  control: impedance_control
  termination: time_limit
  parameters:
    pull_distance:
      type: scalar
      range:
      - 0.02
      - 0.2
- id: push_1
  type: push
  generator: impedance_motion
  control: position_control
  termination: time_limit
  parameters:
    push_depth:
      type: scalar
      range:
      - 0.01
      - 0.1
    push_distance:
      type: scalar
      range:
      - 0.02
      - 0.2
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
- id: descend_2
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: contact_detected
- id: grasp_1
  type: grasp
  control: position_control
  termination: grasp_success
  end_effector_action: force_grasp
  parameters:
    grip_force:
      type: scalar
      range:
      - 5.0
      - 30.0

```

## Design Metrics

- **Composite score**: -0.143
- **task_score** (E): 0.001
- **fitness_score**: 0.137  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.280

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 1.00 | 0.2480 |
| contact_peg | 1.00 | 1.00 | 0.0149 |
| push_through_channel | 0.00 | 1.00 | 0.0056 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.508, 0.111, 0.071) | (0.512, 0.067, 0.040)→(0.502, 0.067, 0.034) | 0.150→0.147 | 1.00 / 1.667 | 114.847 | 127.949 |
| contact_peg | contact | 1.00 / step_budget | (0.508, 0.111, 0.071)→(0.509, 0.104, 0.064) | (0.502, 0.067, 0.034)→(0.502, 0.066, 0.034) | 0.147→0.147 | 1.00 / 1.667 | 205.488 | 401.925 |
| push_through_channel | push | 0.00 / guard_failure | (0.509, 0.104, 0.064)→(0.508, 0.099, 0.062) | (0.502, 0.066, 0.034)→(0.502, 0.066, 0.034) | 0.147→0.146 | 1.00 / 2.333 | 179.029 | 149.883 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.008
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.003
- phase_score: 0.240
- phase_breakdown.approach_score: 0.521
- phase_breakdown.contact_score: 0.557
- phase_breakdown.push_score: 0.040

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.145
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.003
- **Median Q (composite search score)**: -0.141
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.291


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.33636,"average_solve_count":110.0,"average_success_count":110.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.09422,"contact_peg.contact_speed":0.02266,"push_through_channel.push_depth":0.15641,"push_through_channel.push_speed":0.0312,"push_through_channel.push_time":8.31367},"optimized_scores":{"best_composite_score":-0.13484,"best_fitness_score":0.14516,"best_task_score":0.00313},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":979.0,"contact_point_centroid":[0.52501,0.12,0.05996],"force_p95":255.10515,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":260.4925,"mean_force":193.5871,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.52235,0.10552,0.07212]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":30.0,"contact_point_centroid":[0.52502,0.11999,0.05961],"force_p95":181.73697,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":189.42242,"mean_force":170.77677,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.52447,0.10803,0.07138]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":51.0,"contact_point_centroid":[0.525,0.11996,0.02866],"force_p95":32.73415,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":40.34941,"mean_force":28.44236,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50917,0.07976,0.05408]},{"body_a":"world","body_b":"link7","contact_count":25.0,"contact_point_centroid":[0.51181,0.1428,-0.0],"force_p95":19.7205,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":20.16842,"mean_force":14.05363,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50914,0.08079,0.05427]},{"body_a":"peg","body_b":"channel_base_body","contact_count":237.0,"contact_point_centroid":[0.50564,0.0608,0.00947],"force_p95":1.19366,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.92318,"mean_force":0.69927,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50965,0.08429,0.05528]},{"body_a":"attachment","body_b":"peg","contact_count":34.0,"contact_point_centroid":[0.50591,0.08021,0.04272],"force_p95":4.55539,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.55819,"mean_force":1.26753,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50914,0.08026,0.05421]},{"body_a":"peg","body_b":"channel_base_body","contact_count":812.0,"contact_point_centroid":[0.50584,0.06295,0.00937],"force_p95":0.55616,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.56323,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50876,0.15676,0.17815]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50343,0.2202,0.28849]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50601,0.06301,0.00938],"force_p95":0.55192,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55532,"mean_force":0.54652,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.52222,0.10537,0.07203]}],"total_contact_groups":9},"final_pose_error":0.15461,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50591,0.06167,0.03387],"final_tcp_position":[0.50921,0.07974,0.05396],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":260.4925,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":840.0,"n_steps_budget":1000.0,"object_pos_end":[0.50593,0.06297,0.0338],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14323,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":164.91689,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":876.0,"raw_peak_contact_force":189.42242,"subtask_id":"approach","tcp_end":[0.52458,0.10811,0.07178],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.06187,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50597,0.06289,0.03384],"object_pos_start":[0.50593,0.06297,0.0338],"object_to_goal_dist_end":0.14315,"object_to_goal_dist_start":0.14323,"object_z_max":0.03384,"peak_contact_force":0.54733,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1979.0,"raw_peak_contact_force":260.4925,"subtask_id":"contact","tcp_end":[0.51274,0.09422,0.06102],"tcp_start":[0.52458,0.10811,0.07178],"tcp_to_object_dist_end":0.04203,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":237.0,"n_steps_budget":1000.0,"object_pos_end":[0.50591,0.06167,0.03387],"object_pos_start":[0.50597,0.06289,0.03384],"object_to_goal_dist_end":0.14193,"object_to_goal_dist_start":0.14315,"object_z_max":0.03467,"peak_contact_force":40.34941,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":347.0,"raw_peak_contact_force":40.34941,"subtask_id":"push","tcp_end":[0.50921,0.07974,0.05396],"tcp_start":[0.51274,0.09422,0.06102],"tcp_to_object_dist_end":0.02722,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.98462,"average_solve_count":65.0,"average_success_count":65.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.18824,"contact_peg.contact_speed":0.0323,"push_through_channel.push_depth":0.12975,"push_through_channel.push_speed":0.03013,"push_through_channel.push_time":8.47201},"optimized_scores":{"best_composite_score":-0.15339,"best_fitness_score":0.12661,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":904.0,"contact_point_centroid":[0.52987,0.12,0.05994],"force_p95":266.40528,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":269.02377,"mean_force":215.01256,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.53091,0.10012,0.07295]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.52927,0.12,0.05994],"force_p95":216.7741,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":216.7741,"mean_force":216.7741,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.53169,0.09722,0.07387]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":19.0,"contact_point_centroid":[0.5313,0.11999,0.05934],"force_p95":190.26002,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":190.65307,"mean_force":176.99018,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.53127,0.10228,0.07083]},{"body_a":"peg","body_b":"channel_base_body","contact_count":677.0,"contact_point_centroid":[0.5059,0.0566,0.00936],"force_p95":0.60057,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.57004,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.51204,0.1523,0.17198]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50274,0.22212,0.28585]},{"body_a":"peg","body_b":"channel_base_body","contact_count":904.0,"contact_point_centroid":[0.50617,0.05661,0.00938],"force_p95":0.55015,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55093,"mean_force":0.54674,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.53091,0.10012,0.07295]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.49115,0.04673,0.00938],"force_p95":0.54553,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54553,"mean_force":0.54553,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.53169,0.09722,0.07387]}],"total_contact_groups":7},"final_pose_error":0.15776,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50611,0.05662,0.03378],"final_tcp_position":[0.53174,0.09728,0.07382],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":269.02377,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":706.0,"n_steps_budget":900.0,"object_pos_end":[0.50613,0.05663,0.03378],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.13691,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":179.06876,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":733.0,"raw_peak_contact_force":190.65307,"subtask_id":"approach","tcp_end":[0.53148,0.10219,0.07101],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.06407,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":904.0,"n_steps_budget":1000.0,"object_pos_end":[0.50611,0.0566,0.03378],"object_pos_start":[0.50613,0.05663,0.03378],"object_to_goal_dist_end":0.13688,"object_to_goal_dist_start":0.13691,"object_z_max":0.03378,"peak_contact_force":260.41861,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1808.0,"raw_peak_contact_force":269.02377,"subtask_id":"contact","tcp_end":[0.53169,0.09722,0.07387],"tcp_start":[0.53148,0.10219,0.07101],"tcp_to_object_dist_end":0.06254,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50611,0.05662,0.03378],"object_pos_start":[0.50611,0.0566,0.03378],"object_to_goal_dist_end":0.1369,"object_to_goal_dist_start":0.13688,"object_z_max":0.03378,"peak_contact_force":216.7741,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2.0,"raw_peak_contact_force":216.7741,"subtask_id":"push","tcp_end":[0.53174,0.09728,0.07382],"tcp_start":[0.53169,0.09722,0.07387],"tcp_to_object_dist_end":0.06255,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.76056,"average_solve_count":71.0,"average_success_count":71.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.10464,"contact_peg.contact_speed":0.0666,"push_through_channel.push_depth":0.16694,"push_through_channel.push_speed":0.03437,"push_through_channel.push_time":12.96935},"optimized_scores":{"best_composite_score":-0.14128,"best_fitness_score":0.13872,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link7","contact_count":305.0,"contact_point_centroid":[0.48035,0.18115,-0.00013],"force_p95":574.33474,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":676.25962,"mean_force":367.88935,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.47871,0.12026,0.05529]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":280.0,"contact_point_centroid":[0.46854,0.11993,0.0507],"force_p95":440.76055,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":557.83426,"mean_force":160.35471,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.47625,0.12008,0.05671]},{"body_a":"world","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.48494,0.17893,-0.0002],"force_p95":192.52451,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":192.52451,"mean_force":192.52451,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.48253,0.12067,0.05788]},{"body_a":"peg","body_b":"channel_base_body","contact_count":732.0,"contact_point_centroid":[0.494,0.07994,0.00937],"force_p95":0.58409,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.77147,"mean_force":0.564,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.48162,0.16543,0.17956]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46907,0.07994,0.03235],"force_p95":1.18295,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.95027,"mean_force":0.45938,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50291,0.22105,0.28777]},{"body_a":"peg","body_b":"channel_base_body","contact_count":497.0,"contact_point_centroid":[0.49382,0.07995,0.00938],"force_p95":0.59208,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.6283,"mean_force":0.54662,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.47618,0.12028,0.05704]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.50722,0.06818,0.00938],"force_p95":0.54989,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54989,"mean_force":0.54989,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.48253,0.12067,0.05788]}],"total_contact_groups":7},"final_pose_error":0.18949,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49384,0.07996,0.03379],"final_tcp_position":[0.48251,0.12059,0.05801],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.47029,0.07994,0.04]},"peak_contact_force":676.25962,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":760.0,"n_steps_budget":1000.0,"object_pos_end":[0.49384,0.07996,0.03377],"object_pos_start":[0.47029,0.07994,0.04],"object_to_goal_dist_end":0.1602,"object_to_goal_dist_start":0.16268,"object_z_max":0.04001,"peak_contact_force":0.55657,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":767.0,"raw_peak_contact_force":3.77147,"subtask_id":"approach","tcp_end":[0.46921,0.12286,0.06932],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.06092,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":497.0,"n_steps_budget":600.0,"object_pos_end":[0.49383,0.07994,0.03379],"object_pos_start":[0.49384,0.07996,0.03377],"object_to_goal_dist_end":0.16018,"object_to_goal_dist_start":0.1602,"object_z_max":0.03379,"peak_contact_force":355.49879,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1082.0,"raw_peak_contact_force":676.25962,"subtask_id":"contact","tcp_end":[0.48253,0.12067,0.05788],"tcp_start":[0.46921,0.12286,0.06932],"tcp_to_object_dist_end":0.04866,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.49384,0.07996,0.03379],"object_pos_start":[0.49383,0.07994,0.03379],"object_to_goal_dist_end":0.1602,"object_to_goal_dist_start":0.16018,"object_z_max":0.03379,"peak_contact_force":279.96309,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2.0,"raw_peak_contact_force":192.52451,"subtask_id":"push","tcp_end":[0.48251,0.12059,0.05801],"tcp_start":[0.48253,0.12067,0.05788],"tcp_to_object_dist_end":0.04864,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```