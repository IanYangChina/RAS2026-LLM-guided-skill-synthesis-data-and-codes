## Search State

- **Seed**: 4
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 4 | -0.1030 | 0.01 | ❌ rejected |
| 0 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.3038 | 0.61 | ✅ accepted |

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

## Current Skill (Q=-0.103) — your mutation base

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

- **Composite score**: -0.103
- **task_score** (E): 0.012
- **fitness_score**: 0.127  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.230

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 1.00 | 0.2416 |
| contact_peg | 1.00 | 1.00 | 0.0326 |
| push_through_channel | 0.00 | 1.00 | 0.0000 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.516, 0.090, 0.087) | (0.521, 0.084, 0.040)→(0.505, 0.084, 0.034) | 0.166→0.165 | 1.00 / 1.000 | 0.547 | 3.242 |
| contact_peg | descend | 1.00 / step_budget | (0.516, 0.090, 0.087)→(0.513, 0.087, 0.055) | (0.505, 0.084, 0.034)→(0.498, 0.082, 0.033) | 0.165→0.162 | 1.00 / 3.333 | 246.665 | 319.587 |
| push_through_channel | push | 0.00 / guard_failure | (0.513, 0.087, 0.055)→(0.513, 0.087, 0.055) | (0.498, 0.082, 0.033)→(0.498, 0.082, 0.033) | 0.162→0.162 | 1.00 / 3.333 | 119.059 | 119.059 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.037
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.036
- phase_score: 0.226
- phase_breakdown.contact_score: 0.666
- phase_breakdown.approach_score: 0.316
- phase_breakdown.push_score: 0.049

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.150
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.036
- **Median Q (composite search score)**: -0.113
- **K-run variance**: 0.0003
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.489


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.76259,"average_solve_count":139.0,"average_success_count":139.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.09102,"contact_peg.descend_speed":0.01482,"push_through_channel.push_depth":0.11335,"push_through_channel.push_speed":0.02782},"optimized_scores":{"best_composite_score":-0.11541,"best_fitness_score":0.11459,"best_task_score":9e-05},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":918.0,"contact_point_centroid":[0.53277,0.08422,0.0599],"force_p95":322.34226,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":337.75513,"mean_force":303.60231,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"descend","tcp_position_centroid":[0.52159,0.08432,0.06417]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.53526,0.08442,0.05992],"force_p95":74.2674,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":74.36653,"mean_force":73.28023,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.52404,0.08456,0.06411]},{"body_a":"peg","body_b":"channel_base_body","contact_count":769.0,"contact_point_centroid":[0.50579,0.0809,0.00936],"force_p95":0.55183,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.56661,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.51451,0.14114,0.18785]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49988,0.19799,0.29611]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50596,0.08084,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55006,"mean_force":0.54677,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"descend","tcp_position_centroid":[0.52185,0.08438,0.06515]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.51659,0.0872,0.00938],"force_p95":0.54967,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55006,"mean_force":0.54692,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.52404,0.08456,0.06411]}],"total_contact_groups":6},"final_pose_error":0.12224,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50597,0.08086,0.03378],"final_tcp_position":[0.52405,0.08457,0.06411],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":337.75513,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":798.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.08087,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54458,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":805.0,"raw_peak_contact_force":4.32595,"subtask_id":"approach","tcp_end":[0.52988,0.08641,0.08588],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05759,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50597,0.08089,0.03378],"object_pos_start":[0.50599,0.08087,0.03378],"object_to_goal_dist_end":0.16113,"object_to_goal_dist_start":0.1611,"object_z_max":0.03378,"peak_contact_force":281.61808,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1918.0,"raw_peak_contact_force":337.75513,"subtask_id":"contact","tcp_end":[0.52404,0.08456,0.06411],"tcp_start":[0.52988,0.08641,0.08588],"tcp_to_object_dist_end":0.0355,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50598,0.08089,0.03378],"object_pos_start":[0.50597,0.08089,0.03378],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16113,"object_z_max":0.03378,"peak_contact_force":74.36653,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":6.0,"raw_peak_contact_force":74.36653,"subtask_id":"push","tcp_end":[0.52405,0.08457,0.06411],"tcp_start":[0.52405,0.08457,0.06411],"tcp_to_object_dist_end":0.0355,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.59659,"average_solve_count":176.0,"average_success_count":176.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.06594,"contact_peg.descend_speed":0.01139,"push_through_channel.push_depth":0.13847,"push_through_channel.push_speed":0.04436},"optimized_scores":{"best_composite_score":-0.11337,"best_fitness_score":0.11663,"best_task_score":0.00138},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":814.0,"contact_point_centroid":[0.52505,0.10735,0.05998],"force_p95":311.987,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":316.4401,"mean_force":241.20943,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"descend","tcp_position_centroid":[0.50999,0.10732,0.05536]},{"body_a":"peg","body_b":"channel_base_body","contact_count":931.0,"contact_point_centroid":[0.51093,0.10584,0.00839],"force_p95":140.76212,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":145.02491,"mean_force":92.60847,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"descend","tcp_position_centroid":[0.51054,0.10737,0.05756]},{"body_a":"attachment","body_b":"peg","contact_count":841.0,"contact_point_centroid":[0.517,0.10599,0.05462],"force_p95":140.78181,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":144.53834,"mean_force":104.60826,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"descend","tcp_position_centroid":[0.51002,0.1073,0.05554]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.50682,0.10382,0.05459],"force_p95":92.59192,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":93.55074,"mean_force":86.32924,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50833,0.10766,0.05197]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.49051,0.09992,0.00809],"force_p95":84.925,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":85.30658,"mean_force":82.02697,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50833,0.10766,0.05197]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.52506,0.10774,0.05998],"force_p95":76.17595,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":76.31701,"mean_force":62.40998,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50833,0.10766,0.05197]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":231.0,"contact_point_centroid":[0.47368,0.10402,0.02694],"force_p95":49.8514,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":61.02983,"mean_force":34.59046,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"descend","tcp_position_centroid":[0.50882,0.10759,0.05298]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":3.0,"contact_point_centroid":[0.47326,0.10366,0.04079],"force_p95":44.6491,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":44.88164,"mean_force":42.58972,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50833,0.10766,0.05197]},{"body_a":"peg","body_b":"channel_base_body","contact_count":745.0,"contact_point_centroid":[0.50572,0.1046,0.00938],"force_p95":0.57581,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.56152,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50903,0.15315,0.18911]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49973,0.19853,0.29676]}],"total_contact_groups":10},"final_pose_error":0.1452,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.48953,0.10365,0.03119],"final_tcp_position":[0.50832,0.10767,0.05197],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":316.4401,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":772.0,"n_steps_budget":1000.0,"object_pos_end":[0.50582,0.10463,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18482,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.55034,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":777.0,"raw_peak_contact_force":3.33087,"subtask_id":"approach","tcp_end":[0.51936,0.10928,0.08715],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.0552,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":931.0,"n_steps_budget":1000.0,"object_pos_end":[0.48954,0.10367,0.03119],"object_pos_start":[0.50582,0.10463,0.03384],"object_to_goal_dist_end":0.18417,"object_to_goal_dist_start":0.18482,"object_z_max":0.03384,"peak_contact_force":246.0254,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2817.0,"raw_peak_contact_force":316.4401,"subtask_id":"contact","tcp_end":[0.50833,0.10766,0.05198],"tcp_start":[0.51936,0.10928,0.08715],"tcp_to_object_dist_end":0.02831,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.48954,0.10366,0.03119],"object_pos_start":[0.48954,0.10367,0.03119],"object_to_goal_dist_end":0.18417,"object_to_goal_dist_start":0.18417,"object_z_max":0.03119,"peak_contact_force":93.55074,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":12.0,"raw_peak_contact_force":93.55074,"subtask_id":"push","tcp_end":[0.50832,0.10767,0.05197],"tcp_start":[0.50832,0.10766,0.05197],"tcp_to_object_dist_end":0.0283,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.38235,"average_solve_count":204.0,"average_success_count":204.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.06251,"contact_peg.descend_speed":0.00923,"push_through_channel.push_depth":0.12055,"push_through_channel.push_speed":0.01002},"optimized_scores":{"best_composite_score":-0.08011,"best_fitness_score":0.14989,"best_task_score":0.03557},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":473.0,"contact_point_centroid":[0.52505,0.06976,0.05998],"force_p95":266.18552,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":304.56538,"mean_force":161.66149,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"descend","tcp_position_centroid":[0.50727,0.06973,0.04947]},{"body_a":"peg","body_b":"channel_base_body","contact_count":713.0,"contact_point_centroid":[0.51443,0.06882,0.0069],"force_p95":233.5247,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":234.46901,"mean_force":168.06947,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"descend","tcp_position_centroid":[0.50506,0.07017,0.05408]},{"body_a":"attachment","body_b":"peg","contact_count":617.0,"contact_point_centroid":[0.51727,0.06944,0.04937],"force_p95":233.13065,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":233.98153,"mean_force":193.58471,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"descend","tcp_position_centroid":[0.50621,0.06982,0.05063]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.50812,0.06436,0.00716],"force_p95":188.83133,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":189.25848,"mean_force":184.10383,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50709,0.06987,0.04935]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.51849,0.06636,0.0488],"force_p95":188.29635,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":188.70435,"mean_force":183.78617,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50709,0.06987,0.04935]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.52505,0.06991,0.05998],"force_p95":107.13475,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":107.88044,"mean_force":99.32501,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50709,0.06987,0.04935]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52502,0.06604,0.04634],"force_p95":36.59774,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":45.57423,"mean_force":8.24426,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"descend","tcp_position_centroid":[0.50708,0.06953,0.04992]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":15.0,"contact_point_centroid":[0.47464,0.06047,0.01268],"force_p95":43.10734,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":43.49735,"mean_force":34.6317,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"descend","tcp_position_centroid":[0.50708,0.06985,0.04933]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":3.0,"contact_point_centroid":[0.47439,0.06032,0.01313],"force_p95":42.36734,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":42.43877,"mean_force":41.63221,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50709,0.06987,0.04935]},{"body_a":"peg","body_b":"channel_base_body","contact_count":824.0,"contact_point_centroid":[0.50309,0.06745,0.00935],"force_p95":0.55326,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.55709,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49876,0.13571,0.18995]}],"total_contact_groups":10},"final_pose_error":0.13033,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49722,0.06153,0.03306],"final_tcp_position":[0.5071,0.06991,0.04941],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":304.56538,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":840.0,"n_steps_budget":1000.0,"object_pos_end":[0.50302,0.06743,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.5468,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":824.0,"raw_peak_contact_force":2.06903,"subtask_id":"approach","tcp_end":[0.49926,0.07381,0.08653],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05325,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":713.0,"n_steps_budget":1000.0,"object_pos_end":[0.4973,0.06154,0.033],"object_pos_start":[0.50302,0.06743,0.0338],"object_to_goal_dist_end":0.14174,"object_to_goal_dist_start":0.14759,"object_z_max":0.0338,"peak_contact_force":212.35134,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1834.0,"raw_peak_contact_force":304.56538,"subtask_id":"contact","tcp_end":[0.50708,0.06986,0.04933],"tcp_start":[0.49926,0.07381,0.08653],"tcp_to_object_dist_end":0.02077,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.49728,0.06153,0.03301],"object_pos_start":[0.4973,0.06154,0.033],"object_to_goal_dist_end":0.14173,"object_to_goal_dist_start":0.14174,"object_z_max":0.03304,"peak_contact_force":189.25848,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":12.0,"raw_peak_contact_force":189.25848,"subtask_id":"push","tcp_end":[0.5071,0.06991,0.04941],"tcp_start":[0.50709,0.06989,0.04938],"tcp_to_object_dist_end":0.02087,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```