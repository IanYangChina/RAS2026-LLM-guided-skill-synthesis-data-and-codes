## Search State

- **Seed**: 4
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.1114 | 0.22 | ❌ rejected |
| 2 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.2299 | 0.37 | ✅ accepted |
| 1 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | -0.0426 | 0.00 | ❌ rejected |
| 0 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 3 | 0.2607 | 0.15 | ✅ accepted |

**Proposal policy**: task_score is 0.22 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.111) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
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
    - 0.04
    - 0.0
    tolerance: 0.02
    orientation:
      mode: none
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach
- id: contact_peg
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - -0.01
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    contact_force:
      type: scalar
      range:
      - 3.0
      - 15.0
      default: 8.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    contact_speed:
      type: scalar
      range:
      - 0.008
      - 0.04
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
- id: push_channel
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.02
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: channel_axis
      tolerance: 0.1
  parameters:
    push_speed:
      type: scalar
      range:
      - 0.02
      - 0.12
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace
- id: retract_lift
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
    - 0.1
    tolerance: 0.02
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_peg** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.04, 0.0], tolerance=0.02
  - orientation: mode=none
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **contact_peg** (`contact`)
  - target: source=yaml, anchor=task_object, offset=[0.0, -0.01, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
    - contact_speed: status=consumed; consumers=generator.speed (replace)
- **push_channel** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - push_speed: status=consumed; consumers=generator.speed (replace)
- **retract_lift** (`retract`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.111
- **task_score** (E): 0.219
- **fitness_score**: 0.255  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.167
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.310

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 1.00 | 0.2516 |
| contact_peg | 1.00 | 1.00 | 0.0234 |
| push_channel | 0.00 | 1.00 | 0.0001 |
| retract_lift | 1.00 | 1.00 | 0.1948 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.516, 0.131, 0.060) | (0.521, 0.084, 0.040)→(0.505, 0.084, 0.034) | 0.166→0.165 | 1.00 / 1.333 | 105.702 | 163.073 |
| contact_peg | contact | 1.00 / force_exceeded | (0.516, 0.131, 0.060)→(0.512, 0.111, 0.048) | (0.505, 0.084, 0.034)→(0.505, 0.076, 0.035) | 0.165→0.156 | 1.00 / 2.333 | 54.334 | 37.757 |
| push_channel | push | 0.00 / guard_failure | (0.512, 0.111, 0.048)→(0.512, 0.111, 0.048) | (0.505, 0.076, 0.035)→(0.505, 0.076, 0.035) | 0.156→0.156 | 1.00 / 2.000 | 50.730 | 67.336 |
| retract_lift | retract | 1.00 / step_budget | (0.512, 0.111, 0.048)→(0.498, -0.065, 0.128) | (0.505, 0.076, 0.035)→(0.506, 0.039, 0.027) | 0.156→0.120 | 1.00 / 1.000 | 0.522 | 89.622 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.374
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.185
- phase_score: 0.290
- phase_breakdown.contact_score: 0.733
- phase_breakdown.push_score: 0.015
- phase_breakdown.approach_score: 0.671

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.378
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.472
- **Median Q (composite search score)**: 0.078
- **K-run variance**: 0.0029
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.288


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.01124,"average_solve_count":89.0,"average_success_count":89.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.14538,"contact_peg.contact_force":5.76023,"contact_peg.contact_speed":0.02315,"push_channel.push_depth":0.19227,"push_channel.push_speed":0.07814},"optimized_scores":{"best_composite_score":0.07834,"best_fitness_score":0.13834,"best_task_score":7e-05},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":26.0,"contact_point_centroid":[0.53656,0.11969,0.05916],"force_p95":467.32864,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":483.81989,"mean_force":364.96459,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.52903,0.12828,0.06115]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.53691,0.11982,0.05953],"force_p95":144.51541,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":144.73466,"mean_force":142.94898,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.52949,0.12861,0.06191]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":9.0,"contact_point_centroid":[0.53713,0.1199,0.05974],"force_p95":140.9879,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":141.1827,"mean_force":115.84961,"phase_index":3.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.52951,0.12858,0.0624]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.53689,0.11979,0.05947],"force_p95":103.80507,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":103.80507,"mean_force":103.80507,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.52945,0.12856,0.06181]},{"body_a":"peg","body_b":"channel_base_body","contact_count":456.0,"contact_point_centroid":[0.50562,0.0809,0.00935],"force_p95":0.5605,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.58023,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.51498,0.16051,0.16813]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50042,0.19789,0.29313]},{"body_a":"peg","body_b":"channel_base_body","contact_count":527.0,"contact_point_centroid":[0.50601,0.08089,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55008,"mean_force":0.54677,"phase_index":3.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.51294,0.03243,0.09345]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.50594,0.06888,0.00938],"force_p95":0.54801,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54819,"mean_force":0.5469,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.52949,0.12861,0.06191]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.52106,0.09068,0.00938],"force_p95":0.54459,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54459,"mean_force":0.54459,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.52945,0.12856,0.06181]}],"total_contact_groups":9},"final_pose_error":0.01973,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50595,0.08087,0.03378],"final_tcp_position":[0.49921,-0.06364,0.12899],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":483.81989,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":485.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.08089,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":316.00879,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":518.0,"raw_peak_contact_force":483.81989,"subtask_id":"approach","tcp_end":[0.52945,0.12856,0.06181],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.06007,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.08087,0.03378],"object_pos_start":[0.50599,0.08089,0.03378],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.16112,"object_z_max":0.03378,"peak_contact_force":103.80507,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":103.80507,"subtask_id":"contact","tcp_end":[0.52947,0.12858,0.06186],"tcp_start":[0.52945,0.12856,0.06181],"tcp_to_object_dist_end":0.06014,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50597,0.08086,0.03378],"object_pos_start":[0.50599,0.08087,0.03378],"object_to_goal_dist_end":0.16109,"object_to_goal_dist_start":0.1611,"object_z_max":0.03378,"peak_contact_force":141.57008,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":6.0,"raw_peak_contact_force":144.73466,"subtask_id":"push","tcp_end":[0.52951,0.12866,0.06201],"tcp_start":[0.5295,0.12864,0.06197],"tcp_to_object_dist_end":0.06031,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":527.0,"n_steps_budget":1000.0,"object_pos_end":[0.50595,0.08087,0.03378],"object_pos_start":[0.50596,0.08089,0.03378],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.16112,"object_z_max":0.03378,"peak_contact_force":0.54819,"phase_name":"retract_lift","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":536.0,"raw_peak_contact_force":141.1827,"tcp_end":[0.49921,-0.06364,0.12899],"tcp_start":[0.52951,0.12866,0.06201],"tcp_to_object_dist_end":0.17319,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.608,"average_solve_count":125.0,"average_success_count":125.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.10152,"contact_peg.contact_force":7.6922,"contact_peg.contact_speed":0.0251,"push_channel.push_depth":0.18208,"push_channel.push_speed":0.1129},"optimized_scores":{"best_composite_score":0.18797,"best_fitness_score":0.24797,"best_task_score":0.1851},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":13.0,"contact_point_centroid":[0.52501,0.12,0.06],"force_p95":111.03183,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":112.92852,"mean_force":88.02299,"phase_index":3.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.50839,0.12637,0.04521]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":2.0,"contact_point_centroid":[0.525,0.12,0.06],"force_p95":51.99945,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":52.02599,"mean_force":51.76054,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51012,0.12873,0.04463]},{"body_a":"peg","body_b":"channel_base_body","contact_count":537.0,"contact_point_centroid":[0.49912,0.05334,0.00857],"force_p95":8.88338,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.31801,"mean_force":1.47851,"phase_index":3.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.50207,0.02975,0.08531]},{"body_a":"attachment","body_b":"peg","contact_count":74.0,"contact_point_centroid":[0.50423,0.10282,0.05004],"force_p95":10.88621,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.66952,"mean_force":5.28703,"phase_index":3.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.50677,0.11442,0.04907]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":25.0,"contact_point_centroid":[0.47493,0.02266,0.02552],"force_p95":9.9851,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.10268,"mean_force":3.84087,"phase_index":3.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.50359,0.06633,0.06801]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":4.0,"contact_point_centroid":[0.52501,0.06857,0.02408],"force_p95":6.93306,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.08066,"mean_force":2.30965,"phase_index":3.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.49771,-0.06323,0.12749]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.5011,0.08217,0.00996],"force_p95":5.39156,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.93123,"mean_force":2.3229,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51011,0.12872,0.04461]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.50785,0.11702,0.04541],"force_p95":5.04596,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.58949,"mean_force":1.9479,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51011,0.12872,0.04461]},{"body_a":"peg","body_b":"channel_base_body","contact_count":338.0,"contact_point_centroid":[0.50415,0.09662,0.0096],"force_p95":3.28531,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.41093,"mean_force":1.31813,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.51231,0.13629,0.04849]},{"body_a":"attachment","body_b":"peg","contact_count":131.0,"contact_point_centroid":[0.50854,0.11947,0.04654],"force_p95":3.22788,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.97585,"mean_force":2.18881,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.51074,0.13122,0.04576]},{"body_a":"peg","body_b":"channel_base_body","contact_count":444.0,"contact_point_centroid":[0.50565,0.10463,0.00937],"force_p95":0.5793,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.5718,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50906,0.17318,0.17365]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.5001,0.19865,0.29443]}],"total_contact_groups":12},"final_pose_error":0.01984,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50536,0.04487,0.0242],"final_tcp_position":[0.49766,-0.06437,0.12801],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":112.92852,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":471.0,"n_steps_budget":1000.0,"object_pos_end":[0.50587,0.10457,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18477,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.55047,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":476.0,"raw_peak_contact_force":3.33087,"subtask_id":"approach","tcp_end":[0.51875,0.14879,0.05868],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05233,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":343.0,"n_steps_budget":1000.0,"object_pos_end":[0.50397,0.09965,0.03513],"object_pos_start":[0.50587,0.10457,0.03384],"object_to_goal_dist_end":0.17976,"object_to_goal_dist_start":0.18477,"object_z_max":0.03524,"peak_contact_force":55.97426,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":469.0,"raw_peak_contact_force":5.41093,"subtask_id":"contact","tcp_end":[0.51013,0.12873,0.04464],"tcp_start":[0.51875,0.14879,0.05868],"tcp_to_object_dist_end":0.03122,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50395,0.09962,0.03513],"object_pos_start":[0.50397,0.09965,0.03513],"object_to_goal_dist_end":0.17973,"object_to_goal_dist_start":0.17976,"object_z_max":0.03513,"peak_contact_force":5.93123,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":8.0,"raw_peak_contact_force":52.02599,"subtask_id":"push","tcp_end":[0.51005,0.12872,0.04453],"tcp_start":[0.51008,0.12872,0.04458],"tcp_to_object_dist_end":0.03119,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":560.0,"n_steps_budget":1000.0,"object_pos_end":[0.50536,0.04487,0.0242],"object_pos_start":[0.50388,0.09957,0.03513],"object_to_goal_dist_end":0.12598,"object_to_goal_dist_start":0.17968,"object_z_max":0.04078,"peak_contact_force":0.4855,"phase_name":"retract_lift","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":653.0,"raw_peak_contact_force":112.92852,"tcp_end":[0.49766,-0.06437,0.12801],"tcp_start":[0.51005,0.12872,0.04453],"tcp_to_object_dist_end":0.15089,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.43333,"average_solve_count":150.0,"average_success_count":150.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.08391,"contact_peg.contact_force":5.89971,"contact_peg.contact_speed":0.02245,"push_channel.push_depth":0.15349,"push_channel.push_speed":0.09865},"optimized_scores":{"best_composite_score":0.06801,"best_fitness_score":0.37801,"best_task_score":0.47208},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":68.0,"contact_point_centroid":[0.5004,0.04978,0.04336],"force_p95":11.20347,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.75339,"mean_force":4.24588,"phase_index":3.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.49563,0.06055,0.0444]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52504,0.03271,0.02517],"force_p95":10.30446,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.32411,"mean_force":3.56343,"phase_index":3.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.49504,0.05221,0.0488]},{"body_a":"peg","body_b":"channel_base_body","contact_count":420.0,"contact_point_centroid":[0.50626,0.00064,0.00861],"force_p95":6.73533,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.74303,"mean_force":1.22282,"phase_index":3.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.49561,-0.0008,0.08312]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.50421,0.03136,0.00994],"force_p95":5.19073,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.24657,"mean_force":3.47105,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49774,0.07609,0.03694]},{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.50226,0.06442,0.0407],"force_p95":4.75885,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.78352,"mean_force":4.53685,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49774,0.07609,0.03694]},{"body_a":"peg","body_b":"channel_base_body","contact_count":984.0,"contact_point_centroid":[0.50398,0.0515,0.00974],"force_p95":3.30961,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.05472,"mean_force":1.80169,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49682,0.09339,0.04449]},{"body_a":"attachment","body_b":"peg","contact_count":608.0,"contact_point_centroid":[0.501,0.07474,0.04435],"force_p95":3.01931,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.73513,"mean_force":2.22327,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49712,0.08644,0.04138]},{"body_a":"peg","body_b":"channel_base_body","contact_count":478.0,"contact_point_centroid":[0.50301,0.0675,0.00933],"force_p95":0.56083,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.56465,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49906,0.15672,0.17625]}],"total_contact_groups":8},"final_pose_error":0.01999,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5066,-0.00807,0.02413],"final_tcp_position":[0.49667,-0.06612,0.12601],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":14.75339,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":494.0,"n_steps_budget":1000.0,"object_pos_end":[0.50309,0.06748,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14764,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54729,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":478.0,"raw_peak_contact_force":2.06903,"subtask_id":"approach","tcp_end":[0.4994,0.1149,0.05813],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05343,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50583,0.04711,0.03633],"object_pos_start":[0.50309,0.06748,0.0338],"object_to_goal_dist_end":0.1273,"object_to_goal_dist_start":0.14764,"object_z_max":0.03649,"peak_contact_force":3.2239,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1592.0,"raw_peak_contact_force":4.05472,"subtask_id":"contact","tcp_end":[0.49776,0.07612,0.03699],"tcp_start":[0.4994,0.1149,0.05813],"tcp_to_object_dist_end":0.03012,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50583,0.04707,0.03633],"object_pos_start":[0.50583,0.04711,0.03633],"object_to_goal_dist_end":0.12725,"object_to_goal_dist_start":0.1273,"object_z_max":0.03633,"peak_contact_force":4.68812,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":5.0,"raw_peak_contact_force":5.24657,"subtask_id":"push","tcp_end":[0.49767,0.07604,0.03683],"tcp_start":[0.49771,0.07606,0.0369],"tcp_to_object_dist_end":0.0301,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":463.0,"n_steps_budget":1000.0,"object_pos_end":[0.5066,-0.00807,0.02413],"object_pos_start":[0.5058,0.04703,0.03633],"object_to_goal_dist_end":0.07395,"object_to_goal_dist_start":0.12721,"object_z_max":0.04076,"peak_contact_force":0.53273,"phase_name":"retract_lift","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":520.0,"raw_peak_contact_force":14.75339,"tcp_end":[0.49667,-0.06612,0.12601],"tcp_start":[0.49767,0.07604,0.03683],"tcp_to_object_dist_end":0.11768,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```