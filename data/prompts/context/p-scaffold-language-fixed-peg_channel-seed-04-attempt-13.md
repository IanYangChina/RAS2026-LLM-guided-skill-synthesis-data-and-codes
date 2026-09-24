## Search State

- **Seed**: 4
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | 0.0748 | 0.38 | ❌ rejected |
| 12 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | impedance_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | -0.0034 | 0.01 | ❌ rejected |
| 11 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 10 | -0.2346 | 0.00 | ❌ rejected |
| 10 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | 0.2373 | 0.55 | ❌ rejected |
| 9 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 10 | -0.2300 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.38 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.075) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
phases:
- id: align_1
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.06
    - 0.02
    tolerance: 0.01
    orientation:
      mode: none
  parameters:
    lateral_offset_y:
      type: scalar
      range:
      - -0.01
      - 0.01
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: add
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
    - -0.01
    tolerance: 0.005
    orientation:
      mode: none
  parameters:
    approach_z_offset:
      type: scalar
      range:
      - -0.02
      - 0.01
      default: -0.01
      binds_to:
      - path: target.offset.z
        mode: replace
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
    tolerance: 0.005
    orientation:
      mode: none
  parameters:
    contact_force:
      type: scalar
      range:
      - 5.0
      - 25.0
      default: 15
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
- id: push_1
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.0
      axis: channel_axis
      mode: replace_offset_projection
      sign: positive
    tolerance: 0.01
    orientation:
      mode: none
  parameters:
    push_depth:
      type: scalar
      range:
      - 0.0
      - 0.05
      default: 0.02
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
- id: retract_1
  type: retract
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.01
    orientation:
      mode: none
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.12
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **align_1** (`align`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.06, 0.02], tolerance=0.01
  - orientation: mode=none
  - parameter_bindings:
    - lateral_offset_y: status=consumed; consumers=target.offset.y (add)
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.04, -0.01], tolerance=0.005
  - orientation: mode=none
  - parameter_bindings:
    - approach_z_offset: status=consumed; consumers=target.offset.z (replace)
- **contact_1** (`contact`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.02, 0.0], tolerance=0.005
  - orientation: mode=none
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.0, mode=replace_offset_projection, sign=positive}, tolerance=0.01
  - orientation: mode=none
  - parameter_bindings:
    - push_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.15], tolerance=0.01
  - orientation: mode=none
  - parameter_bindings:
    - retract_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.075
- **task_score** (E): 0.377
- **fitness_score**: 0.498  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.067
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.490

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_1 | 1.00 | 1.00 | 0.2219 |
| approach_1 | 1.00 | 1.00 | 0.0485 |
| contact_1 | 0.33 | 1.00 | 0.0156 |
| push_1 | 0.00 | 1.00 | 0.1706 |
| retract_1 | 0.67 | 1.00 | 0.1008 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_1 | align | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.516, 0.141, 0.088) | (0.521, 0.084, 0.040)→(0.505, 0.084, 0.034) | 0.166→0.164 | 1.00 / 1.000 | 0.548 | 3.242 |
| approach_1 | approach | 1.00 / step_budget | (0.516, 0.141, 0.088)→(0.504, 0.127, 0.044) | (0.505, 0.084, 0.034)→(0.505, 0.084, 0.034) | 0.164→0.164 | 1.00 / 1.333 | 110.062 | 113.145 |
| contact_1 | contact | 0.33 / step_budget | (0.504, 0.127, 0.044)→(0.501, 0.112, 0.050) | (0.505, 0.084, 0.034)→(0.505, 0.081, 0.036) | 0.164→0.161 | 1.00 / 2.000 | 23.392 | 24.443 |
| push_1 | push | 0.00 / step_budget | (0.501, 0.112, 0.050)→(0.497, -0.058, 0.056) | (0.505, 0.081, 0.036)→(0.507, 0.008, 0.028) | 0.161→0.090 | 1.00 / 1.667 | 11.182 | 43.408 |
| retract_1 | retract | 0.67 / step_budget | (0.497, -0.058, 0.056)→(0.494, -0.052, 0.156) | (0.507, 0.008, 0.028)→(0.504, 0.005, 0.024) | 0.090→0.089 | 1.00 / 1.000 | 0.642 | 22.393 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.874
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.874
- phase_score: 0.540
- phase_breakdown.push_score: 0.395
- phase_breakdown.contact_score: 0.633
- phase_breakdown.approach_score: 0.884

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.674
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.874
- **Median Q (composite search score)**: -0.076
- **K-run variance**: 0.0477
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Parameters at lower bound**: align_1.lateral_offset_y
- **Final σ (mean)**: 0.334


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.36702,"average_solve_count":188.0,"average_success_count":188.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_y":-0.01,"approach_1.approach_z_offset":0.01042,"contact_1.contact_force":18.71661,"contact_1.speed":0.02269,"push_1.push_depth":0.17844,"push_1.push_speed":0.07704,"retract_1.retract_height":0.09866,"retract_1.speed":0.04645},"optimized_scores":{"best_composite_score":-0.08349,"best_fitness_score":0.40651,"best_task_score":0.09364},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":195.0,"contact_point_centroid":[0.50399,0.07044,0.05257],"force_p95":16.29596,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.26678,"mean_force":9.13845,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49913,0.08092,0.05466]},{"body_a":"peg","body_b":"channel_base_body","contact_count":997.0,"contact_point_centroid":[0.50551,0.03681,0.00849],"force_p95":11.70394,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.21712,"mean_force":2.30041,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49783,0.00796,0.0561]},{"body_a":"peg","body_b":"channel_base_body","contact_count":949.0,"contact_point_centroid":[0.50573,0.03055,0.00806],"force_p95":0.72703,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.65555,"mean_force":0.64107,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49365,-0.07302,0.10316]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":11.0,"contact_point_centroid":[0.525,0.05552,0.02417],"force_p95":9.15483,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.16218,"mean_force":3.5112,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49371,-0.075,0.13241]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52508,0.06641,0.05776],"force_p95":7.96016,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.97008,"mean_force":6.19948,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50049,0.08804,0.05614]},{"body_a":"peg","body_b":"channel_base_body","contact_count":676.0,"contact_point_centroid":[0.50576,0.08085,0.00936],"force_p95":0.55524,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.56934,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.51443,0.16567,0.18873]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.5,0.19852,0.2957]},{"body_a":"peg","body_b":"channel_base_body","contact_count":605.0,"contact_point_centroid":[0.50556,0.07189,0.00965],"force_p95":0.98312,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.31776,"mean_force":0.59835,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50287,0.11119,0.0513]},{"body_a":"attachment","body_b":"peg","contact_count":291.0,"contact_point_centroid":[0.50408,0.09435,0.05475],"force_p95":1.0641,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.89039,"mean_force":0.30707,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.5023,0.10623,0.05438]},{"body_a":"peg","body_b":"channel_base_body","contact_count":191.0,"contact_point_centroid":[0.50606,0.08092,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55006,"mean_force":0.54677,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51837,0.12862,0.06795]}],"total_contact_groups":10},"final_pose_error":0.01,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50652,0.03134,0.02428],"final_tcp_position":[0.49385,-0.07829,0.14821],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":19.26678,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":705.0,"n_steps_budget":1000.0,"object_pos_end":[0.50596,0.08089,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.5464,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":712.0,"raw_peak_contact_force":4.32595,"tcp_end":[0.52969,0.13405,0.08736],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07912,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":191.0,"n_steps_budget":600.0,"object_pos_end":[0.50596,0.08087,0.03378],"object_pos_start":[0.50596,0.08089,0.03378],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.16112,"object_z_max":0.03378,"peak_contact_force":0.54819,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":191.0,"raw_peak_contact_force":0.55006,"tcp_end":[0.50729,0.12288,0.04857],"tcp_start":[0.52969,0.13405,0.08736],"tcp_to_object_dist_end":0.04456,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":605.0,"n_steps_budget":750.0,"object_pos_end":[0.50575,0.07529,0.03783],"object_pos_start":[0.50596,0.08087,0.03378],"object_to_goal_dist_end":0.15541,"object_to_goal_dist_start":0.1611,"object_z_max":0.03783,"peak_contact_force":0.44703,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":896.0,"raw_peak_contact_force":2.31776,"tcp_end":[0.50206,0.10186,0.05741],"tcp_start":[0.50729,0.12288,0.04857],"tcp_to_object_dist_end":0.0332,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5061,0.03066,0.02413],"object_pos_start":[0.50575,0.07529,0.03783],"object_to_goal_dist_end":0.11196,"object_to_goal_dist_start":0.15541,"object_z_max":0.04039,"peak_contact_force":0.55103,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1208.0,"raw_peak_contact_force":19.26678,"tcp_end":[0.49706,-0.08028,0.05881],"tcp_start":[0.50206,0.10186,0.05741],"tcp_to_object_dist_end":0.11658,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":949.0,"n_steps_budget":1000.0,"object_pos_end":[0.50652,0.03134,0.02428],"object_pos_start":[0.5061,0.03066,0.02413],"object_to_goal_dist_end":0.11263,"object_to_goal_dist_start":0.11196,"object_z_max":0.02454,"peak_contact_force":0.64893,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":960.0,"raw_peak_contact_force":9.65555,"tcp_end":[0.49385,-0.07829,0.14821],"tcp_start":[0.49706,-0.08028,0.05881],"tcp_to_object_dist_end":0.16594,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.64571,"average_solve_count":175.0,"average_success_count":175.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_y":-0.00372,"approach_1.approach_z_offset":0.01104,"contact_1.contact_force":8.67577,"contact_1.speed":0.02925,"push_1.push_depth":0.14791,"push_1.push_speed":0.07601,"retract_1.retract_height":0.12561,"retract_1.speed":0.07414},"optimized_scores":{"best_composite_score":-0.07567,"best_fitness_score":0.41433,"best_task_score":0.16265},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":198.0,"contact_point_centroid":[0.5039,0.09418,0.05247],"force_p95":17.52485,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.96513,"mean_force":9.05985,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49887,0.10458,0.05458]},{"body_a":"peg","body_b":"channel_base_body","contact_count":997.0,"contact_point_centroid":[0.50661,0.06097,0.00848],"force_p95":11.49273,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.34102,"mean_force":2.37868,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4976,0.03054,0.05612]},{"body_a":"peg","body_b":"channel_base_body","contact_count":950.0,"contact_point_centroid":[0.50671,0.05576,0.0081],"force_p95":0.68987,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.82838,"mean_force":0.74885,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49359,-0.05016,0.11644]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":35.0,"contact_point_centroid":[0.52502,0.05601,0.02453],"force_p95":9.29991,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.37344,"mean_force":4.22144,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49349,-0.04817,0.1243]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":38.0,"contact_point_centroid":[0.52504,0.08503,0.04028],"force_p95":9.04193,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.37255,"mean_force":4.67817,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49874,0.06712,0.05606]},{"body_a":"peg","body_b":"channel_base_body","contact_count":639.0,"contact_point_centroid":[0.50573,0.10463,0.00937],"force_p95":0.57595,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.56403,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50904,0.18026,0.18982]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49985,0.19906,0.29624]},{"body_a":"peg","body_b":"channel_base_body","contact_count":484.0,"contact_point_centroid":[0.50598,0.09624,0.00963],"force_p95":1.16842,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.79004,"mean_force":0.62464,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50165,0.13541,0.05131]},{"body_a":"attachment","body_b":"peg","contact_count":219.0,"contact_point_centroid":[0.50382,0.11816,0.05525],"force_p95":0.89834,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.34717,"mean_force":0.35352,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50155,0.12998,0.05443]},{"body_a":"peg","body_b":"channel_base_body","contact_count":196.0,"contact_point_centroid":[0.50585,0.10456,0.00939],"force_p95":0.57566,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57597,"mean_force":0.54636,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5115,0.15501,0.06839]}],"total_contact_groups":10},"final_pose_error":0.01024,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50676,0.05567,0.02413],"final_tcp_position":[0.49391,-0.05701,0.17503],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":19.96513,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":666.0,"n_steps_budget":1000.0,"object_pos_end":[0.50587,0.10457,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18477,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.55192,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":671.0,"raw_peak_contact_force":3.33087,"tcp_end":[0.51929,0.16226,0.08822],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08042,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":196.0,"n_steps_budget":600.0,"object_pos_end":[0.50584,0.10459,0.03384],"object_pos_start":[0.50587,0.10457,0.03384],"object_to_goal_dist_end":0.18479,"object_to_goal_dist_start":0.18477,"object_z_max":0.03384,"peak_contact_force":0.5518,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":196.0,"raw_peak_contact_force":0.57597,"tcp_end":[0.50481,0.14725,0.04886],"tcp_start":[0.51929,0.16226,0.08822],"tcp_to_object_dist_end":0.04524,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":484.0,"n_steps_budget":600.0,"object_pos_end":[0.50609,0.0992,0.0378],"object_pos_start":[0.50584,0.10459,0.03384],"object_to_goal_dist_end":0.17932,"object_to_goal_dist_start":0.18479,"object_z_max":0.0378,"peak_contact_force":0.50662,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":703.0,"raw_peak_contact_force":1.79004,"tcp_end":[0.50177,0.12564,0.05731],"tcp_start":[0.50481,0.14725,0.04886],"tcp_to_object_dist_end":0.03314,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50682,0.05579,0.02415],"object_pos_start":[0.50609,0.0992,0.0378],"object_to_goal_dist_end":0.13688,"object_to_goal_dist_start":0.17932,"object_z_max":0.0404,"peak_contact_force":0.56838,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1233.0,"raw_peak_contact_force":19.96513,"tcp_end":[0.49688,-0.059,0.05901],"tcp_start":[0.50177,0.12564,0.05731],"tcp_to_object_dist_end":0.12038,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":950.0,"n_steps_budget":1000.0,"object_pos_end":[0.50676,0.05567,0.02413],"object_pos_start":[0.50682,0.05579,0.02415],"object_to_goal_dist_end":0.13676,"object_to_goal_dist_start":0.13688,"object_z_max":0.0253,"peak_contact_force":0.68467,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":985.0,"raw_peak_contact_force":9.82838,"tcp_end":[0.49391,-0.05701,0.17503],"tcp_start":[0.49688,-0.059,0.05901],"tcp_to_object_dist_end":0.18877,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.4321,"average_solve_count":162.0,"average_success_count":162.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_y":-0.00571,"approach_1.approach_z_offset":-0.00231,"contact_1.contact_force":11.1497,"contact_1.speed":0.03439,"push_1.push_depth":0.10858,"push_1.push_speed":0.06472,"retract_1.retract_height":0.14884,"retract_1.speed":0.04928},"optimized_scores":{"best_composite_score":0.3837,"best_fitness_score":0.6737,"best_task_score":0.87365},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":32.0,"contact_point_centroid":[0.54322,0.11089,0.05979],"force_p95":338.17215,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":338.30913,"mean_force":303.50392,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4986,0.10955,0.03581]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":211.0,"contact_point_centroid":[0.54224,0.09447,0.05999],"force_p95":77.57958,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":90.99106,"mean_force":59.90594,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49739,0.09385,0.03664]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54353,0.11089,0.05986],"force_p95":69.22105,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":69.22105,"mean_force":69.22105,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49889,0.10955,0.036]},{"body_a":"attachment","body_b":"peg","contact_count":20.0,"contact_point_centroid":[0.50448,-0.0415,0.04572],"force_p95":28.42595,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":47.695,"mean_force":4.68131,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49581,-0.03459,0.04958]},{"body_a":"peg","body_b":"channel_base_body","contact_count":998.0,"contact_point_centroid":[0.49694,-0.07069,0.00818],"force_p95":0.76686,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":45.452,"mean_force":0.75322,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49299,-0.02323,0.09632]},{"body_a":"attachment","body_b":"peg","contact_count":637.0,"contact_point_centroid":[0.50065,0.00662,0.04207],"force_p95":32.98238,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":36.41656,"mean_force":13.48345,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49569,0.01694,0.04255]},{"body_a":"peg","body_b":"channel_base_body","contact_count":837.0,"contact_point_centroid":[0.50394,0.00249,0.00968],"force_p95":30.11251,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":34.02642,"mean_force":9.62994,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49615,0.0375,0.04095]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":363.0,"contact_point_centroid":[0.52514,-0.03084,0.02905],"force_p95":14.25704,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.71141,"mean_force":8.59751,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49569,-0.00838,0.04533]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":18.0,"contact_point_centroid":[0.47499,-0.09546,0.02433],"force_p95":8.39914,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.66993,"mean_force":3.43144,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49262,-0.02566,0.0714]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":4.0,"contact_point_centroid":[0.52507,-0.03916,0.02592],"force_p95":5.07504,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.43194,"mean_force":2.80452,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49644,-0.03472,0.04914]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":36.0,"contact_point_centroid":[0.47488,0.03023,0.03394],"force_p95":3.89165,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.04735,"mean_force":0.9195,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4955,0.06005,0.03745]},{"body_a":"peg","body_b":"channel_base_body","contact_count":671.0,"contact_point_centroid":[0.50309,0.06744,0.00935],"force_p95":0.55492,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.55947,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49884,0.16207,0.19132]},{"body_a":"peg","body_b":"channel_base_body","contact_count":341.0,"contact_point_centroid":[0.50306,0.06751,0.00938],"force_p95":0.55059,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55083,"mean_force":0.54665,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4976,0.11664,0.05834]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.50282,0.04947,0.00938],"force_p95":0.54717,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54717,"mean_force":0.54717,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49889,0.10955,0.036]}],"total_contact_groups":14},"final_pose_error":0.05457,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49882,-0.07232,0.02414],"final_tcp_position":[0.49321,-0.02157,0.14508],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":338.30913,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":687.0,"n_steps_budget":1000.0,"object_pos_end":[0.50302,0.06743,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54675,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":671.0,"raw_peak_contact_force":2.06903,"tcp_end":[0.49932,0.12559,0.08824],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07975,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":341.0,"n_steps_budget":600.0,"object_pos_end":[0.50305,0.06742,0.0338],"object_pos_start":[0.50302,0.06743,0.0338],"object_to_goal_dist_end":0.14758,"object_to_goal_dist_start":0.14759,"object_z_max":0.0338,"peak_contact_force":329.08583,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":373.0,"raw_peak_contact_force":338.30913,"tcp_end":[0.49889,0.10955,0.036],"tcp_start":[0.49932,0.12559,0.08824],"tcp_to_object_dist_end":0.0424,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":660.0,"object_pos_end":[0.50302,0.06743,0.0338],"object_pos_start":[0.50305,0.06742,0.0338],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14758,"object_z_max":0.0338,"peak_contact_force":69.22105,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":69.22105,"tcp_end":[0.49894,0.10956,0.03601],"tcp_start":[0.49889,0.10955,0.036],"tcp_to_object_dist_end":0.04239,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50717,-0.06223,0.03529],"object_pos_start":[0.50302,0.06743,0.0338],"object_to_goal_dist_end":0.01973,"object_to_goal_dist_start":0.14759,"object_z_max":0.04036,"peak_contact_force":32.42789,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2084.0,"raw_peak_contact_force":90.99106,"tcp_end":[0.49647,-0.03456,0.04913],"tcp_start":[0.49894,0.10956,0.03601],"tcp_to_object_dist_end":0.03273,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49882,-0.07232,0.02414],"object_pos_start":[0.50717,-0.06223,0.03529],"object_to_goal_dist_end":0.01766,"object_to_goal_dist_start":0.01973,"object_z_max":0.03534,"peak_contact_force":0.59384,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1040.0,"raw_peak_contact_force":47.695,"tcp_end":[0.49321,-0.02157,0.14508],"tcp_start":[0.49647,-0.03456,0.04913],"tcp_to_object_dist_end":0.13127,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```