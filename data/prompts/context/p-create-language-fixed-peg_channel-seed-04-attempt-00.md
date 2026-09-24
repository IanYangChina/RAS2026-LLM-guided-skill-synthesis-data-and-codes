## Search State

- **Seed**: 4
- **Iteration**: 1 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 0 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 3 | 0.2607 | 0.15 | ✅ accepted |

**Proposal policy**: task_score is 0.15 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.261) — your mutation base

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
    offset:
    - 0.0
    - 0.04
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
  subtask_id: approach
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.02
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    contact_force:
      type: scalar
      range:
      - 1.0
      - 20.0
      default: 10.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    speed:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: contact
- id: push_1
  type: push
  generator: impedance_motion
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
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: push
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: world
    offset:
    - 0.5
    - -0.08
    - 0.1
    tolerance: 0.02
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.04, 0.0], tolerance=0.02
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings: none
- **contact_1** (`contact`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.02, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=world, offset=[0.5, -0.08, 0.04], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **retract_1** (`retract`)
  - target: source=yaml, anchor=world, offset=[0.5, -0.08, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.261
- **task_score** (E): 0.149
- **fitness_score**: 0.221  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.210

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2531 |
| contact_1 | 1.00 | 1.00 | 0.0054 |
| push_1 | 0.00 | 1.00 | 0.0334 |
| retract_1 | 0.00 | 1.00 | 0.0341 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.516, 0.130, 0.058) | (0.521, 0.084, 0.040)→(0.505, 0.084, 0.034) | 0.166→0.165 | 1.00 / 1.000 | 0.547 | 3.242 |
| contact_1 | contact | 1.00 / force_exceeded | (0.516, 0.130, 0.058)→(0.514, 0.127, 0.054) | (0.505, 0.084, 0.034)→(0.505, 0.084, 0.034) | 0.165→0.164 | 1.00 / 2.000 | 61.887 | 61.887 |
| push_1 | push | 0.00 / step_budget | (0.514, 0.127, 0.054)→(0.513, 0.095, 0.052) | (0.505, 0.084, 0.034)→(0.504, 0.066, 0.034) | 0.164→0.146 | 1.00 / 3.000 | 319.297 | 510.262 |
| retract_1 | retract | 0.00 / step_budget | (0.513, 0.095, 0.052)→(0.509, 0.113, 0.034) | (0.504, 0.066, 0.034)→(0.504, 0.017, 0.031) | 0.146→0.099 | 1.00 / 2.000 | 234.297 | 707.720 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.928
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.256
- phase_score: 0.258
- phase_breakdown.contact_score: 0.565
- phase_breakdown.push_score: 0.018
- phase_breakdown.approach_score: 0.673

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.257
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.256
- **Median Q (composite search score)**: 0.257
- **K-run variance**: 0.0008
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.341


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.61074,"average_solve_count":149.0,"average_success_count":149.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force":12.47693,"contact_1.speed":0.03256,"push_1.speed":0.03965},"optimized_scores":{"best_composite_score":0.29735,"best_fitness_score":0.25735,"best_task_score":0.25584},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":967.0,"contact_point_centroid":[0.52501,0.11994,0.05975],"force_p95":196.31799,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":470.56631,"mean_force":187.77448,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52334,0.11977,0.05308]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":371.0,"contact_point_centroid":[0.46857,0.11974,0.0599],"force_p95":289.09337,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":417.65999,"mean_force":262.88018,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51193,0.09778,0.04716]},{"body_a":"world","body_b":"link7","contact_count":444.0,"contact_point_centroid":[0.51617,0.18279,-1e-05],"force_p95":128.39679,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":390.55565,"mean_force":70.24223,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52288,0.11984,0.05272]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":609.0,"contact_point_centroid":[0.52503,0.11992,0.05996],"force_p95":188.7586,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":215.2332,"mean_force":178.92413,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51821,0.11873,0.052]},{"body_a":"world","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.51226,0.18249,-0.0],"force_p95":117.33797,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":124.6609,"mean_force":66.11563,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.52201,0.11952,0.05232]},{"body_a":"world","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.5285,0.18618,-1e-05],"force_p95":52.91743,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":52.91743,"mean_force":52.91743,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52697,0.12425,0.05438]},{"body_a":"attachment","body_b":"peg","contact_count":6.0,"contact_point_centroid":[0.50432,0.09452,0.05585],"force_p95":36.27815,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":36.71064,"mean_force":23.0923,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5135,0.0992,0.05053]},{"body_a":"peg","body_b":"channel_base_body","contact_count":944.0,"contact_point_centroid":[0.50414,0.03667,0.00916],"force_p95":0.78491,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":36.57904,"mean_force":0.72415,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51598,0.11185,0.0501]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":10.0,"contact_point_centroid":[0.52505,-0.01087,0.03524],"force_p95":5.41831,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.841,"mean_force":1.68111,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51261,0.09648,0.04726]},{"body_a":"peg","body_b":"channel_base_body","contact_count":494.0,"contact_point_centroid":[0.50571,0.0809,0.00936],"force_p95":0.56027,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.57765,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50873,0.16953,0.17385]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50315,0.22162,0.2867]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":9.0,"contact_point_centroid":[0.47491,-0.03111,0.05855],"force_p95":2.45609,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.9663,"mean_force":0.91676,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5122,0.09531,0.05043]},{"body_a":"peg","body_b":"channel_base_body","contact_count":16.0,"contact_point_centroid":[0.50405,0.0808,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55008,"mean_force":0.54695,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.5281,0.12523,0.05589]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50599,0.08085,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55007,"mean_force":0.54677,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52344,0.11986,0.05311]}],"total_contact_groups":14},"final_pose_error":0.19638,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50467,-0.06765,0.02439],"final_tcp_position":[0.51167,0.10632,0.03906],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":470.56631,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":523.0,"n_steps_budget":1000.0,"object_pos_end":[0.50597,0.08086,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16109,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.5461,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":530.0,"raw_peak_contact_force":4.32595,"subtask_id":"approach","tcp_end":[0.52944,0.12651,0.05798],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05674,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":16.0,"n_steps_budget":840.0,"object_pos_end":[0.50599,0.08089,0.03378],"object_pos_start":[0.50597,0.08086,0.03378],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16109,"object_z_max":0.03378,"peak_contact_force":52.91743,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":17.0,"raw_peak_contact_force":52.91743,"subtask_id":"contact","tcp_end":[0.52685,0.12415,0.05424],"tcp_start":[0.52944,0.12651,0.05798],"tcp_to_object_dist_end":0.05221,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50595,0.08088,0.03378],"object_pos_start":[0.50599,0.08089,0.03378],"object_to_goal_dist_end":0.16111,"object_to_goal_dist_start":0.16112,"object_z_max":0.03378,"peak_contact_force":183.43054,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2411.0,"raw_peak_contact_force":470.56631,"subtask_id":"push","tcp_end":[0.5222,0.11952,0.0524],"tcp_start":[0.52685,0.12415,0.05424],"tcp_to_object_dist_end":0.04587,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50467,-0.06765,0.02439],"object_pos_start":[0.50595,0.08088,0.03378],"object_to_goal_dist_end":0.02044,"object_to_goal_dist_start":0.16111,"object_z_max":0.04926,"peak_contact_force":278.46031,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1953.0,"raw_peak_contact_force":417.65999,"tcp_end":[0.51167,0.10632,0.03906],"tcp_start":[0.5222,0.11952,0.0524],"tcp_to_object_dist_end":0.17472,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.61268,"average_solve_count":142.0,"average_success_count":142.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force":5.76093,"contact_1.speed":0.04464,"push_1.speed":0.05893},"optimized_scores":{"best_composite_score":0.25659,"best_fitness_score":0.21659,"best_task_score":0.12651},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link7","contact_count":905.0,"contact_point_centroid":[0.47402,0.1199,0.05971],"force_p95":760.62907,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":977.5362,"mean_force":486.1474,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51341,0.09204,0.04359]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":686.0,"contact_point_centroid":[0.52504,0.09216,0.04584],"force_p95":500.41756,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":617.70456,"mean_force":357.89228,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51337,0.0899,0.04487]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":152.0,"contact_point_centroid":[0.47493,0.1199,0.05304],"force_p95":592.88487,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":617.1779,"mean_force":472.60588,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51313,0.07919,0.05248]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":282.0,"contact_point_centroid":[0.525,0.11994,0.06],"force_p95":406.11623,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":570.12372,"mean_force":199.39811,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51308,0.07915,0.05273]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":690.0,"contact_point_centroid":[0.52502,0.0971,0.05461],"force_p95":327.51879,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":473.48506,"mean_force":178.87858,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51339,0.09642,0.05291]},{"body_a":"world","body_b":"link7","contact_count":542.0,"contact_point_centroid":[0.51314,0.1627,-2e-05],"force_p95":239.93029,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":408.0749,"mean_force":140.46163,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51364,0.09968,0.0531]},{"body_a":"peg","body_b":"channel_base_body","contact_count":946.0,"contact_point_centroid":[0.50424,0.07168,0.00969],"force_p95":1.7676,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":83.94161,"mean_force":1.29682,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51367,0.1017,0.05306]},{"body_a":"attachment","body_b":"peg","contact_count":525.0,"contact_point_centroid":[0.50417,0.10231,0.05305],"force_p95":3.18861,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":79.74874,"mean_force":1.53442,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51346,0.10279,0.05302]},{"body_a":"world","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.51831,0.20736,-3e-05],"force_p95":58.98577,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":58.98577,"mean_force":58.98577,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.51683,0.14547,0.05439]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.52506,0.07993,0.04415],"force_p95":4.276,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.57138,"mean_force":1.18262,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51292,0.09829,0.05301]},{"body_a":"peg","body_b":"channel_base_body","contact_count":475.0,"contact_point_centroid":[0.50552,0.10461,0.00937],"force_p95":0.57792,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.57014,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50391,0.18011,0.17423]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50403,0.2188,0.29002]},{"body_a":"peg","body_b":"channel_base_body","contact_count":905.0,"contact_point_centroid":[0.50362,0.06005,0.00938],"force_p95":0.55973,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60713,"mean_force":0.54668,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51341,0.09204,0.04359]},{"body_a":"peg","body_b":"channel_base_body","contact_count":20.0,"contact_point_centroid":[0.50944,0.10608,0.00939],"force_p95":0.5757,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57678,"mean_force":0.54608,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.51793,0.14669,0.0563]}],"total_contact_groups":14},"final_pose_error":0.20265,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50362,0.06007,0.03378],"final_tcp_position":[0.51367,0.11073,0.03291],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":977.5362,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":502.0,"n_steps_budget":1000.0,"object_pos_end":[0.50589,0.10472,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18492,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.54401,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":507.0,"raw_peak_contact_force":3.33087,"subtask_id":"approach","tcp_end":[0.51939,0.14819,0.05893],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05197,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.50591,0.10456,0.03384],"object_pos_start":[0.50589,0.10472,0.03384],"object_to_goal_dist_end":0.18476,"object_to_goal_dist_start":0.18492,"object_z_max":0.03384,"peak_contact_force":58.98577,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":21.0,"raw_peak_contact_force":58.98577,"subtask_id":"contact","tcp_end":[0.51675,0.14537,0.05424],"tcp_start":[0.51939,0.14819,0.05893],"tcp_to_object_dist_end":0.04689,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50362,0.06007,0.03377],"object_pos_start":[0.50591,0.10456,0.03384],"object_to_goal_dist_end":0.14026,"object_to_goal_dist_start":0.18476,"object_z_max":0.03706,"peak_contact_force":530.63858,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3174.0,"raw_peak_contact_force":617.1779,"subtask_id":"push","tcp_end":[0.51315,0.07975,0.05228],"tcp_start":[0.51675,0.14537,0.05424],"tcp_to_object_dist_end":0.02865,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":905.0,"n_steps_budget":1000.0,"object_pos_end":[0.50362,0.06007,0.03378],"object_pos_start":[0.50362,0.06007,0.03377],"object_to_goal_dist_end":0.14026,"object_to_goal_dist_start":0.14026,"object_z_max":0.03378,"peak_contact_force":296.19723,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2496.0,"raw_peak_contact_force":977.5362,"tcp_end":[0.51367,0.11073,0.03291],"tcp_start":[0.51315,0.07975,0.05228],"tcp_to_object_dist_end":0.05165,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.56954,"average_solve_count":151.0,"average_success_count":151.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force":5.70314,"contact_1.speed":0.0256,"push_1.speed":0.04656},"optimized_scores":{"best_composite_score":0.22802,"best_fitness_score":0.18802,"best_task_score":0.06346},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link7","contact_count":930.0,"contact_point_centroid":[0.46778,0.11994,0.05998],"force_p95":305.94447,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":727.96334,"mean_force":223.70696,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5067,0.09897,0.03968]},{"body_a":"world","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.4973,0.14783,-1e-05],"force_p95":524.33897,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":525.71777,"mean_force":348.42995,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50353,0.0845,0.05242]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":763.0,"contact_point_centroid":[0.46965,0.11991,0.06],"force_p95":349.63048,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":443.04069,"mean_force":248.603,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50235,0.08233,0.05254]},{"body_a":"world","body_b":"link7","contact_count":624.0,"contact_point_centroid":[0.49993,0.1496,-2e-05],"force_p95":201.2065,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":305.67085,"mean_force":106.56003,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50162,0.08644,0.05288]},{"body_a":"world","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.50025,0.17361,-6e-05],"force_p95":73.75703,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":73.75703,"mean_force":73.75703,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49872,0.11166,0.05427]},{"body_a":"peg","body_b":"channel_base_body","contact_count":988.0,"contact_point_centroid":[0.50297,0.05916,0.00939],"force_p95":0.57959,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":37.47066,"mean_force":0.63565,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50181,0.0853,0.05278]},{"body_a":"attachment","body_b":"peg","contact_count":23.0,"contact_point_centroid":[0.50263,0.08438,0.05578],"force_p95":28.77347,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.08929,"mean_force":3.88092,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5007,0.08422,0.05328]},{"body_a":"peg","body_b":"channel_base_body","contact_count":504.0,"contact_point_centroid":[0.503,0.06746,0.00934],"force_p95":0.55899,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.56372,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49516,0.16528,0.17607]},{"body_a":"peg","body_b":"channel_base_body","contact_count":935.0,"contact_point_centroid":[0.50286,0.05722,0.00939],"force_p95":0.55163,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55644,"mean_force":0.54622,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50669,0.09906,0.03965]},{"body_a":"peg","body_b":"channel_base_body","contact_count":20.0,"contact_point_centroid":[0.50415,0.06883,0.00938],"force_p95":0.55022,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55065,"mean_force":0.54648,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49919,0.11278,0.05588]}],"total_contact_groups":10},"final_pose_error":0.2142,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50274,0.05731,0.03387],"final_tcp_position":[0.50246,0.12239,0.02988],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":727.96334,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":520.0,"n_steps_budget":1000.0,"object_pos_end":[0.50306,0.0675,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14766,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.55098,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":504.0,"raw_peak_contact_force":2.06903,"subtask_id":"approach","tcp_end":[0.50009,0.11414,0.05811],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05268,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":20.0,"n_steps_budget":900.0,"object_pos_end":[0.50309,0.06745,0.0338],"object_pos_start":[0.50306,0.0675,0.0338],"object_to_goal_dist_end":0.14762,"object_to_goal_dist_start":0.14766,"object_z_max":0.0338,"peak_contact_force":73.75703,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":21.0,"raw_peak_contact_force":73.75703,"subtask_id":"contact","tcp_end":[0.4987,0.11157,0.05414],"tcp_start":[0.50009,0.11414,0.05811],"tcp_to_object_dist_end":0.04878,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50298,0.05726,0.03387],"object_pos_start":[0.50309,0.06745,0.0338],"object_to_goal_dist_end":0.13742,"object_to_goal_dist_start":0.14762,"object_z_max":0.03679,"peak_contact_force":243.82118,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2398.0,"raw_peak_contact_force":443.04069,"subtask_id":"push","tcp_end":[0.50351,0.08449,0.05242],"tcp_start":[0.4987,0.11157,0.05414],"tcp_to_object_dist_end":0.03295,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":935.0,"n_steps_budget":1000.0,"object_pos_end":[0.50274,0.05731,0.03387],"object_pos_start":[0.50298,0.05726,0.03387],"object_to_goal_dist_end":0.13747,"object_to_goal_dist_start":0.13742,"object_z_max":0.03388,"peak_contact_force":128.23454,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1869.0,"raw_peak_contact_force":727.96334,"tcp_end":[0.50246,0.12239,0.02988],"tcp_start":[0.50351,0.08449,0.05242],"tcp_to_object_dist_end":0.0652,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```