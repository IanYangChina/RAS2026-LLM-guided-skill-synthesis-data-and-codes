## Search State

- **Seed**: 4
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.2434 | 0.58 | ❌ rejected |
| 9 | approach → contact → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 7 | -0.2933 | 0.01 | ❌ rejected |
| 8 | approach → contact → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.1780 | 0.58 | ❌ rejected |
| 7 | approach → contact → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.3408 | 0.22 | ❌ rejected |
| 6 | approach → descend → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 4 | -0.0638 | 0.21 | ❌ rejected |

**Proposal policy**: task_score is 0.58 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `5d75b33f12bcf5a2f8bdcc4693a93f63ce145f4d32d6acfe75032964e261854c`
- Frozen object start: [0.5354444884457894, 0.08090620422514894, 0.04]
- Frozen task target: [0.5354444884457894, -0.07909379577485107, 0.04]
- Goal object position: (0.5354444884457894, -0.07909379577485107, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5354444884457894, 0.08090620422514894, 0.04)
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
  frozen_object_start: [0.5354, 0.0809, 0.04]
  frozen_task_target: [0.5354, -0.0791, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5354444884457894, 0.08090620422514894, 0.04]}
  frozen_targets: {'channel_exit': [0.5354444884457894, -0.07909379577485107, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: 5d75b33f12bcf5a2f8bdcc4693a93f63ce145f4d32d6acfe75032964e261854c

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

## Current Skill (Q=0.243) — your mutation base

```yaml
skill: peg_channel
skill_type: arm_gripper
phases:
- id: push_1
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: time_limit
  parameters:
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
- id: align_1
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    lateral_offset_x:
      type: scalar
      range:
      - -0.01
      - 0.01
    lateral_offset_y:
      type: scalar
      range:
      - -0.01
      - 0.01
- id: release_1
  type: release
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
  end_effector_action: open
- id: insert_1
  type: insert
  generator: impedance_motion
  control: impedance_control
  termination: force_exceeded
  parameters:
    insertion_depth:
      type: scalar
      range:
      - 0.01
      - 0.15
    insertion_force:
      type: scalar
      range:
      - 1.0
      - 20.0

```

## Design Metrics

- **Composite score**: 0.243
- **task_score** (E): 0.575
- **fitness_score**: 0.523  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.280

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 1.00 | 0.2240 |
| contact_peg | 1.00 | 1.00 | 0.0486 |
| push_peg | 0.33 | 1.00 | 0.0577 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.516, 0.090, 0.106) | (0.521, 0.084, 0.040)→(0.505, 0.084, 0.034) | 0.166→0.165 | 1.00 / 1.000 | 0.547 | 3.242 |
| contact_peg | contact | 1.00 / step_budget | (0.509, 0.095, 0.085)→(0.506, 0.102, 0.043) | (0.505, 0.084, 0.034)→(0.495, 0.074, 0.038) | 0.165→0.154 | 1.00 / 1.667 | 0.576 | 278.402 |
| push_peg | push | 0.33 / guard_failure | (0.502, 0.012, 0.038)→(0.497, -0.046, 0.036) | (0.497, 0.068, 0.037)→(0.505, -0.076, 0.033) | 0.148→0.011 | 1.00 / 3.333 | 15.312 | 27.833 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.938
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.938
- phase_score: 0.582
- phase_breakdown.contact_score: 0.904
- phase_breakdown.approach_score: 0.227
- phase_breakdown.push_score: 0.592

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.724
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.938
- **Median Q (composite search score)**: 0.232
- **K-run variance**: 0.0254
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.339


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `424e8a040c59c1e1e42822c1022320b6050001458f7b9b4937cb9238911ce80b`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `72d2436204c0f1ee3bbdbdfe3e5489661153a48f95d8f0dc3b73e6ce1e1e081b`; realized-scene SHA-256: `5d75b33f12bcf5a2f8bdcc4693a93f63ce145f4d32d6acfe75032964e261854c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53544,0.08091,0.04]},{"name":"goal","value":[0.53544,-0.07909,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.53544,0.08091,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.53544,-0.07909,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.82772,"average_solve_count":267.0,"average_success_count":267.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.04404,"contact_peg.contact_speed":0.02951,"push_peg.force_guard_threshold":24.52552,"push_peg.push_depth":0.11078,"push_peg.push_speed":0.03404},"optimized_scores":{"best_composite_score":0.05416,"best_fitness_score":0.33416,"best_task_score":0.24575},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":228.0,"contact_point_centroid":[0.52507,0.09836,0.05999],"force_p95":337.51765,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":422.66135,"mean_force":281.78426,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.51224,0.09843,0.05362]},{"body_a":"peg","body_b":"channel_base_body","contact_count":478.0,"contact_point_centroid":[0.50975,0.08173,0.00898],"force_p95":139.02222,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":142.61633,"mean_force":55.83991,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.5142,0.09538,0.06214]},{"body_a":"attachment","body_b":"peg","contact_count":237.0,"contact_point_centroid":[0.51869,0.089,0.05473],"force_p95":139.96827,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":142.13962,"mean_force":111.6331,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.51223,0.09841,0.05362]},{"body_a":"attachment","body_b":"peg","contact_count":511.0,"contact_point_centroid":[0.49916,0.00389,0.04564],"force_p95":10.52101,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":33.32011,"mean_force":2.76046,"phase_index":2.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.49605,0.01575,0.03704]},{"body_a":"peg","body_b":"channel_base_body","contact_count":11.0,"contact_point_centroid":[0.48949,-0.1003,0.02813],"force_p95":26.34938,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":29.90923,"mean_force":17.48424,"phase_index":2.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.4963,-0.03657,0.03577]},{"body_a":"peg","body_b":"channel_base_body","contact_count":691.0,"contact_point_centroid":[0.5024,-0.01635,0.00961],"force_p95":6.38535,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.61283,"mean_force":1.78608,"phase_index":2.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.49623,0.02535,0.03753]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":12.0,"contact_point_centroid":[0.4749,0.05732,0.02438],"force_p95":7.81271,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.13443,"mean_force":1.61021,"phase_index":2.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.4964,0.07546,0.03915]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":180.0,"contact_point_centroid":[0.52502,-0.04791,0.02786],"force_p95":6.26979,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.88853,"mean_force":2.73237,"phase_index":2.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.49605,0.01046,0.03689]},{"body_a":"peg","body_b":"channel_base_body","contact_count":785.0,"contact_point_centroid":[0.50577,0.08087,0.00936],"force_p95":0.55171,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.5662,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.51454,0.14143,0.19811]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49983,0.19811,0.29661]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":9.0,"contact_point_centroid":[0.47459,0.06475,0.0588],"force_p95":1.98353,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.1556,"mean_force":0.95123,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.51054,0.10042,0.04777]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":10.0,"contact_point_centroid":[0.52521,0.03544,0.05351],"force_p95":0.93045,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.01027,"mean_force":0.48829,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50244,0.09529,0.04247]}],"total_contact_groups":12},"final_pose_error":0.0269,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50312,-0.07323,0.02794],"final_tcp_position":[0.4963,-0.03717,0.03572],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":422.66135,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":814.0,"n_steps_budget":1000.0,"object_pos_end":[0.50597,0.0809,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16113,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54527,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":821.0,"raw_peak_contact_force":4.32595,"subtask_id":"approach","tcp_end":[0.53004,0.08695,0.10584],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07622,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":485.0,"n_steps_budget":1000.0,"object_pos_end":[0.49718,0.06536,0.04045],"object_pos_start":[0.50597,0.0809,0.03378],"object_to_goal_dist_end":0.14539,"object_to_goal_dist_start":0.16113,"object_z_max":0.04077,"peak_contact_force":0.41279,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":962.0,"raw_peak_contact_force":422.66135,"subtask_id":"contact","tcp_end":[0.49947,0.09185,0.04337],"tcp_start":[0.50847,0.10025,0.04327],"tcp_to_object_dist_end":0.02675,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":765.0,"n_steps_budget":1000.0,"object_pos_end":[0.50312,-0.07318,0.02794],"object_pos_start":[0.50194,0.04727,0.03778],"object_to_goal_dist_end":0.01421,"object_to_goal_dist_start":0.1273,"object_z_max":0.03778,"peak_contact_force":15.58131,"phase_name":"push_peg","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1405.0,"raw_peak_contact_force":33.32011,"subtask_id":"push","tcp_end":[0.4963,-0.03717,0.03572],"tcp_start":[0.49633,-0.03713,0.03575],"tcp_to_object_dist_end":0.03747,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `54762c1e743ba455eff3c9979c2b42f5642abe1893e28eae37dc231d7efcd4e4`; realized-scene SHA-256: `ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5244,0.10464,0.04]},{"name":"goal","value":[0.5244,-0.05536,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.5244,0.10464,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.5244,-0.05536,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.97101,"average_solve_count":276.0,"average_success_count":276.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.04069,"contact_peg.contact_speed":0.03252,"push_peg.force_guard_threshold":24.94007,"push_peg.push_depth":0.15778,"push_peg.push_speed":0.01976},"optimized_scores":{"best_composite_score":0.23204,"best_fitness_score":0.51204,"best_task_score":0.54171},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":418.0,"contact_point_centroid":[0.51228,0.11049,0.00859],"force_p95":192.6281,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":202.64595,"mean_force":86.76858,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.51272,0.11959,0.06389]},{"body_a":"attachment","body_b":"peg","contact_count":246.0,"contact_point_centroid":[0.51941,0.11562,0.05328],"force_p95":193.5319,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":202.20728,"mean_force":147.65836,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.51221,0.12368,0.05138]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":144.0,"contact_point_centroid":[0.52503,0.11999,0.06],"force_p95":168.32174,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":179.62337,"mean_force":86.21422,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.5131,0.12512,0.04989]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":104.0,"contact_point_centroid":[0.52518,0.10681,0.05695],"force_p95":17.72524,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":40.92121,"mean_force":6.89023,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.51123,0.12137,0.05331]},{"body_a":"attachment","body_b":"peg","contact_count":699.0,"contact_point_centroid":[0.50125,0.02231,0.04093],"force_p95":9.35186,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.39101,"mean_force":2.99333,"phase_index":2.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.50135,0.03366,0.03612]},{"body_a":"peg","body_b":"channel_base_body","contact_count":568.0,"contact_point_centroid":[0.49861,-0.00261,0.00984],"force_p95":8.63339,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.24633,"mean_force":3.51217,"phase_index":2.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.50168,0.03776,0.03626]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":336.0,"contact_point_centroid":[0.47489,0.05585,0.03183],"force_p95":4.78526,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.60848,"mean_force":1.25339,"phase_index":2.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.50462,0.08327,0.03688]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":271.0,"contact_point_centroid":[0.5251,-0.03976,0.02512],"force_p95":5.25738,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.43609,"mean_force":1.4199,"phase_index":2.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.49841,-0.01164,0.03549]},{"body_a":"peg","body_b":"channel_base_body","contact_count":718.0,"contact_point_centroid":[0.50573,0.10461,0.00937],"force_p95":0.57579,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.56209,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50911,0.15338,0.19925]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":6.0,"contact_point_centroid":[0.47434,0.0976,0.05659],"force_p95":2.38239,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.48637,"mean_force":1.55707,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.51147,0.12727,0.04278]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49972,0.19855,0.29707]}],"total_contact_groups":11},"final_pose_error":0.01428,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50714,-0.07323,0.03602],"final_tcp_position":[0.49635,-0.04536,0.03508],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":202.64595,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":745.0,"n_steps_budget":1000.0,"object_pos_end":[0.50584,0.10459,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18479,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.55189,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":750.0,"raw_peak_contact_force":3.33087,"subtask_id":"approach","tcp_end":[0.51957,0.1097,0.10698],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.0746,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":418.0,"n_steps_budget":1000.0,"object_pos_end":[0.49461,0.09905,0.03552],"object_pos_start":[0.50584,0.10459,0.03384],"object_to_goal_dist_end":0.17919,"object_to_goal_dist_start":0.18479,"object_z_max":0.03532,"peak_contact_force":0.77412,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":918.0,"raw_peak_contact_force":202.64595,"subtask_id":"contact","tcp_end":[0.51079,0.12701,0.0418],"tcp_start":[0.51957,0.1097,0.10698],"tcp_to_object_dist_end":0.0329,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50714,-0.07323,0.03602],"object_pos_start":[0.49461,0.09905,0.03552],"object_to_goal_dist_end":0.01062,"object_to_goal_dist_start":0.17919,"object_z_max":0.03857,"peak_contact_force":9.10497,"phase_name":"push_peg","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1874.0,"raw_peak_contact_force":13.39101,"subtask_id":"push","tcp_end":[0.49635,-0.04536,0.03508],"tcp_start":[0.51079,0.12701,0.0418],"tcp_to_object_dist_end":0.0299,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `b230a5798f38c3fb8968a6bc74f96ee85fe7026f3170cf8216fc868a1c5c570f`; realized-scene SHA-256: `07dc0764c781629358e2f97446117d9c410d14c078397be91277b4276116a1de`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50305,0.06746,0.04]},{"name":"goal","value":[0.50305,-0.09254,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.50305,0.06746,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.50305,-0.09254,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.64528,"average_solve_count":265.0,"average_success_count":265.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.06688,"contact_peg.contact_speed":0.00904,"push_peg.force_guard_threshold":33.9821,"push_peg.push_depth":0.18188,"push_peg.push_speed":0.04362},"optimized_scores":{"best_composite_score":0.44407,"best_fitness_score":0.72407,"best_task_score":0.93788},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":131.0,"contact_point_centroid":[0.52504,0.08807,0.06],"force_p95":142.24772,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":209.89992,"mean_force":87.21537,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.51186,0.08822,0.04918]},{"body_a":"peg","body_b":"channel_base_body","contact_count":592.0,"contact_point_centroid":[0.51224,0.0743,0.00843],"force_p95":179.10412,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":180.66732,"mean_force":102.68057,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50554,0.08374,0.06099]},{"body_a":"attachment","body_b":"peg","contact_count":399.0,"contact_point_centroid":[0.51736,0.07934,0.05294],"force_p95":178.81926,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":180.17535,"mean_force":151.79977,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50887,0.08663,0.05099]},{"body_a":"attachment","body_b":"peg","contact_count":630.0,"contact_point_centroid":[0.50244,0.00108,0.04236],"force_p95":15.93788,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":36.78932,"mean_force":4.87004,"phase_index":2.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.50184,0.01273,0.03762]},{"body_a":"peg","body_b":"channel_base_body","contact_count":21.0,"contact_point_centroid":[0.50672,-0.1004,0.06007],"force_p95":32.88499,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":33.39667,"mean_force":24.19267,"phase_index":2.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.49988,-0.05324,0.03681]},{"body_a":"peg","body_b":"channel_base_body","contact_count":508.0,"contact_point_centroid":[0.50141,-0.02352,0.00986],"force_p95":11.74007,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.57292,"mean_force":5.2286,"phase_index":2.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.50214,0.01993,0.03782]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":164.0,"contact_point_centroid":[0.52511,0.06958,0.05595],"force_p95":5.90103,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.47596,"mean_force":2.93762,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50962,0.08681,0.05063]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":259.0,"contact_point_centroid":[0.52508,-0.04172,0.02755],"force_p95":4.03346,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.06234,"mean_force":1.08426,"phase_index":2.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.50098,-0.01271,0.03721]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":95.0,"contact_point_centroid":[0.4749,0.0271,0.0342],"force_p95":4.9912,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.2316,"mean_force":1.40228,"phase_index":2.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.5033,0.05515,0.03833]},{"body_a":"peg","body_b":"channel_base_body","contact_count":767.0,"contact_point_centroid":[0.50305,0.06749,0.00935],"force_p95":0.55402,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.55786,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49888,0.13589,0.19984]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":5.0,"contact_point_centroid":[0.47442,0.05407,0.05875],"force_p95":1.56413,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.6346,"mean_force":1.03793,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.5079,0.08805,0.04335]}],"total_contact_groups":11},"final_pose_error":0.07157,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50618,-0.0826,0.03543],"final_tcp_position":[0.49979,-0.05403,0.03668],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":209.89992,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":783.0,"n_steps_budget":1000.0,"object_pos_end":[0.50309,0.06745,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14762,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54374,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":767.0,"raw_peak_contact_force":2.06903,"subtask_id":"approach","tcp_end":[0.49959,0.07422,0.10624],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07284,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":592.0,"n_steps_budget":1000.0,"object_pos_end":[0.49439,0.05625,0.03712],"object_pos_start":[0.50309,0.06745,0.0338],"object_to_goal_dist_end":0.13639,"object_to_goal_dist_start":0.14762,"object_z_max":0.0369,"peak_contact_force":0.54254,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1291.0,"raw_peak_contact_force":209.89992,"subtask_id":"contact","tcp_end":[0.50738,0.08796,0.04256],"tcp_start":[0.49959,0.07422,0.10624],"tcp_to_object_dist_end":0.0347,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":856.0,"n_steps_budget":1000.0,"object_pos_end":[0.50619,-0.08255,0.03545],"object_pos_start":[0.49439,0.05625,0.03712],"object_to_goal_dist_end":0.00809,"object_to_goal_dist_start":0.13639,"object_z_max":0.03922,"peak_contact_force":21.25058,"phase_name":"push_peg","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1513.0,"raw_peak_contact_force":36.78932,"subtask_id":"push","tcp_end":[0.49979,-0.05403,0.03668],"tcp_start":[0.49982,-0.05403,0.03672],"tcp_to_object_dist_end":0.02925,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```