## Search State

- **Seed**: 6
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 8 | -0.0647 | 0.66 | ❌ rejected |
| 11 | approach → approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.2188 | 0.94 | ✅ accepted |
| 10 | approach → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | 0.3681 | 0.42 | ❌ rejected |
| 9 | approach → approach → contact → push → retract → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 10 | -0.3081 | 0.00 | ❌ rejected |
| 8 | approach → approach → contact → push → retract → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.3271 | 0.67 | ❌ rejected |

**Proposal policy**: task_score is 0.66 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen object start: [0.5030531481177555, 0.06746166958506708, 0.04]
- Frozen task target: [0.5030531481177555, -0.09253833041493292, 0.04]
- Goal object position: (0.5030531481177555, -0.09253833041493292, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5030531481177555, 0.06746166958506708, 0.04)
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
  frozen_object_start: [0.5031, 0.0675, 0.04]
  frozen_task_target: [0.5031, -0.0925, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5030531481177555, 0.06746166958506708, 0.04]}
  frozen_targets: {'channel_exit': [0.5030531481177555, -0.09253833041493292, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: 07dc0764c781629358e2f97446117d9c410d14c078397be91277b4276116a1de

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

## Current Skill (Q=-0.065) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: approach
  anchor: object
  offset:
  - 0.0
  - 0.04
  - 0.0
- id: contact
  anchor: object
  offset:
  - 0.0
  - 0.02
  - 0.0
- id: push
  anchor: world
  offset:
  - 0.5
  - -0.08
  - 0.04
phases:
- id: align_1
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
    - 0.05
    tolerance: 0.02
    orientation:
      mode: keep_current
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: approach
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
    - 0.02
    - -0.01
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    lateral_offset_x:
      type: scalar
      range:
      - -0.01
      - 0.01
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: replace
    lateral_offset_y:
      type: scalar
      range:
      - -0.01
      - 0.01
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.03
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
      - -0.04
      - 0.04
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: add
    speed:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: force_check
    when: during_phase
    predicate: force_below
    threshold: 30.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.005
    - 0.0
    - 0.0
  subtask_id: push
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
    tolerance: 0.05
    orientation:
      mode: none
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.15
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
- **align_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.04, 0.05], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings: none
  - retries: max_attempts=0, strategy=repeat
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.02, -0.01], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - lateral_offset_x: status=consumed; consumers=target.offset.x (replace)
    - lateral_offset_y: status=consumed; consumers=target.offset.y (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=world, offset=[0.5, -0.08, 0.04], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_depth: status=consumed; consumers=target.offset.y (add)
    - speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_check, when=during_phase, predicate=force_below, on_failure=retry, threshold=30.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.005, 0.0, 0.0]
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.15], tolerance=0.05
  - orientation: mode=none
  - parameter_bindings:
    - retract_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: -0.065
- **task_score** (E): 0.664
- **fitness_score**: 0.395  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.460

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_1 | 1.00 | 1.00 | 0.2005 |
| approach_1 | 1.00 | 1.00 | 0.0855 |
| push_1 | 0.33 | 1.00 | 0.0981 |
| retract_1 | 1.00 | 1.00 | 0.0916 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.497, 0.145, 0.108) | (0.500, 0.099, 0.040)→(0.501, 0.099, 0.034) | 0.180→0.180 | 1.00 / 1.000 | 0.560 | 2.127 |
| approach_1 | approach | 1.00 / step_budget | (0.497, 0.145, 0.108)→(0.507, 0.108, 0.034) | (0.501, 0.099, 0.034)→(0.496, 0.062, 0.038) | 0.180→0.142 | 1.00 / 1.000 | 0.740 | 209.152 |
| push_1 | push | 0.33 / step_budget | (0.507, 0.108, 0.034)→(0.500, 0.011, 0.033) | (0.496, 0.062, 0.038)→(0.499, -0.024, 0.030) | 0.142→0.058 | 1.00 / 2.000 | 1.563 | 12.885 |
| retract_1 | retract | 1.00 / step_budget | (0.500, 0.011, 0.033)→(0.500, 0.018, 0.124) | (0.499, -0.024, 0.030)→(0.497, -0.025, 0.027) | 0.058→0.058 | 1.00 / 1.000 | 0.585 | 4.900 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.848
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.848
- phase_score: 0.326
- phase_breakdown.push_score: 0.364
- phase_breakdown.approach_score: 0.539
- phase_breakdown.contact_score: 0.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.535
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.848
- **Median Q (composite search score)**: -0.115
- **K-run variance**: 0.0100
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.257


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
{"anchors":[{"name":"object","value":[0.50305,0.06746,0.04]},{"name":"goal","value":[0.50305,-0.09254,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.50305,0.06746,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.50305,-0.09254,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.98131,"average_solve_count":214.0,"average_success_count":214.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.lateral_offset_x":-0.00162,"approach_1.lateral_offset_y":0.00488,"approach_1.speed":0.02183,"push_1.force_thresh":34.06569,"push_1.push_depth":-0.00855,"push_1.speed":0.06584,"retract_1.retract_height":0.11855,"retract_1.speed":0.0573},"optimized_scores":{"best_composite_score":0.07489,"best_fitness_score":0.53489,"best_task_score":0.84815},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":352.0,"contact_point_centroid":[0.50644,0.06318,0.00887],"force_p95":148.61572,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":157.50199,"mean_force":37.18181,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49926,0.09719,0.0684]},{"body_a":"attachment","body_b":"peg","contact_count":118.0,"contact_point_centroid":[0.50982,0.08138,0.05442],"force_p95":154.3792,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":156.95162,"mean_force":109.27493,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5013,0.08929,0.05378]},{"body_a":"attachment","body_b":"peg","contact_count":602.0,"contact_point_centroid":[0.50003,0.00028,0.04526],"force_p95":7.03537,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.0282,"mean_force":1.85243,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49556,0.01214,0.03032]},{"body_a":"peg","body_b":"channel_base_body","contact_count":987.0,"contact_point_centroid":[0.50258,-0.0217,0.00963],"force_p95":4.83814,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.9253,"mean_force":1.32175,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49566,0.02385,0.0299]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":199.0,"contact_point_centroid":[0.52502,-0.04474,0.02741],"force_p95":4.88465,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.53134,"mean_force":2.37908,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49555,0.01336,0.03026]},{"body_a":"peg","body_b":"channel_base_body","contact_count":88.0,"contact_point_centroid":[0.50142,-0.06816,0.00857],"force_p95":0.71217,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.80584,"mean_force":0.63809,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49442,-0.02573,0.06178]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.49979,-0.04218,0.04559],"force_p95":3.33941,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.68588,"mean_force":1.30243,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49577,-0.03025,0.03245]},{"body_a":"peg","body_b":"channel_base_body","contact_count":385.0,"contact_point_centroid":[0.50304,0.06739,0.00932],"force_p95":0.61054,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.56899,"phase_index":0.0,"phase_name":"align_1","phase_type":"approach","tcp_position_centroid":[0.49942,0.15735,0.20055]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.52502,0.01962,0.05779],"force_p95":1.68644,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.68644,"mean_force":1.68644,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50267,0.08455,0.04548]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47482,0.01318,0.05504],"force_p95":0.39791,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.25828,"mean_force":0.17814,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49614,0.07073,0.02831]}],"total_contact_groups":10},"final_pose_error":0.04939,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49957,-0.06824,0.0241],"final_tcp_position":[0.49471,-0.02427,0.10199],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":157.50199,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":401.0,"n_steps_budget":1000.0,"object_pos_end":[0.50302,0.06748,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14764,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54683,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":385.0,"raw_peak_contact_force":2.06903,"subtask_id":"approach","tcp_end":[0.49999,0.1165,0.10729],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08839,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":383.0,"n_steps_budget":1000.0,"object_pos_end":[0.50258,0.00108,0.03821],"object_pos_start":[0.50302,0.06748,0.0338],"object_to_goal_dist_end":0.08114,"object_to_goal_dist_start":0.14764,"object_z_max":0.04299,"peak_contact_force":0.36644,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":471.0,"raw_peak_contact_force":157.50199,"tcp_end":[0.49913,0.078,0.03153],"tcp_start":[0.49999,0.1165,0.10729],"tcp_to_object_dist_end":0.07729,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50297,-0.06686,0.02759],"object_pos_start":[0.50258,0.00108,0.03821],"object_to_goal_dist_end":0.01832,"object_to_goal_dist_start":0.08114,"object_z_max":0.04041,"peak_contact_force":1.44317,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1812.0,"raw_peak_contact_force":11.0282,"subtask_id":"push","tcp_end":[0.49579,-0.03018,0.03247],"tcp_start":[0.49913,0.078,0.03153],"tcp_to_object_dist_end":0.03769,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":88.0,"n_steps_budget":1000.0,"object_pos_end":[0.49957,-0.06824,0.0241],"object_pos_start":[0.50297,-0.06686,0.02759],"object_to_goal_dist_end":0.01978,"object_to_goal_dist_start":0.01832,"object_z_max":0.0276,"peak_contact_force":0.60416,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":91.0,"raw_peak_contact_force":3.80584,"tcp_end":[0.49471,-0.02427,0.10199],"tcp_start":[0.49579,-0.03018,0.03247],"tcp_to_object_dist_end":0.08958,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `625c03a21403c0f6267b643060335ee3d751a26340ace08db5429afcee4c5ccf`; realized-scene SHA-256: `d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51001,0.11178,0.04]},{"name":"goal","value":[0.51001,-0.04822,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.51001,0.11178,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.51001,-0.04822,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.30198,"average_solve_count":202.0,"average_success_count":202.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.lateral_offset_x":0.00452,"approach_1.lateral_offset_y":-0.00203,"approach_1.speed":0.02676,"push_1.force_thresh":34.37909,"push_1.push_depth":0.00491,"push_1.speed":0.06326,"retract_1.retract_height":0.16386,"retract_1.speed":0.07227},"optimized_scores":{"best_composite_score":-0.11461,"best_fitness_score":0.34539,"best_task_score":0.57633},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":199.0,"contact_point_centroid":[0.52507,0.11996,0.05999],"force_p95":170.79674,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":236.13142,"mean_force":122.99828,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51354,0.12596,0.05018]},{"body_a":"peg","body_b":"channel_base_body","contact_count":578.0,"contact_point_centroid":[0.51105,0.11229,0.00863],"force_p95":177.89082,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":185.29445,"mean_force":84.71028,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50898,0.13213,0.06163]},{"body_a":"attachment","body_b":"peg","contact_count":361.0,"contact_point_centroid":[0.51832,0.11788,0.053],"force_p95":180.30867,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":184.79986,"mean_force":134.98412,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5116,0.12638,0.05126]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":86.0,"contact_point_centroid":[0.52513,0.10856,0.05642],"force_p95":8.56734,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.82619,"mean_force":3.55176,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51237,0.12516,0.052]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":29.0,"contact_point_centroid":[0.47433,0.09467,0.04915],"force_p95":7.45784,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.77566,"mean_force":1.66126,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51002,0.12231,0.04011]},{"body_a":"peg","body_b":"channel_base_body","contact_count":878.0,"contact_point_centroid":[0.49714,0.02569,0.00989],"force_p95":1.50124,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.42415,"mean_force":0.86538,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50119,0.06344,0.02887]},{"body_a":"peg","body_b":"channel_base_body","contact_count":134.0,"contact_point_centroid":[0.49812,-0.01941,0.00948],"force_p95":0.58999,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.35952,"mean_force":0.55803,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49784,0.01965,0.08313]},{"body_a":"attachment","body_b":"peg","contact_count":810.0,"contact_point_centroid":[0.4999,0.04934,0.02915],"force_p95":1.09605,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.25094,"mean_force":0.56903,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50104,0.06124,0.02888]},{"body_a":"peg","body_b":"channel_base_body","contact_count":350.0,"contact_point_centroid":[0.50351,0.11176,0.00934],"force_p95":0.6343,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.56822,"phase_index":0.0,"phase_name":"align_1","phase_type":"approach","tcp_position_centroid":[0.50263,0.17712,0.19971]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.49866,-0.00055,0.03126],"force_p95":1.79281,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.79281,"mean_force":1.79281,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49918,0.01143,0.03127]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"align_1","phase_type":"approach","tcp_position_centroid":[0.49997,0.19934,0.29835]}],"total_contact_groups":11},"final_pose_error":0.04964,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49797,-0.0193,0.03378],"final_tcp_position":[0.49849,0.01994,0.14623],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":236.13142,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":372.0,"n_steps_budget":1000.0,"object_pos_end":[0.50375,0.11176,0.0338],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.1919,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.56268,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":366.0,"raw_peak_contact_force":2.06328,"subtask_id":"approach","tcp_end":[0.50616,0.15629,0.10861],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08709,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":598.0,"n_steps_budget":1000.0,"object_pos_end":[0.49723,0.08489,0.03312],"object_pos_start":[0.50375,0.11176,0.0338],"object_to_goal_dist_end":0.16505,"object_to_goal_dist_start":0.1919,"object_z_max":0.03832,"peak_contact_force":1.11488,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1253.0,"raw_peak_contact_force":236.13142,"tcp_end":[0.50686,0.11628,0.03091],"tcp_start":[0.50616,0.15629,0.10861],"tcp_to_object_dist_end":0.03292,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49786,-0.01853,0.03498],"object_pos_start":[0.49723,0.08489,0.03312],"object_to_goal_dist_end":0.06171,"object_to_goal_dist_start":0.16505,"object_z_max":0.03679,"peak_contact_force":1.19415,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1688.0,"raw_peak_contact_force":2.42415,"subtask_id":"push","tcp_end":[0.49918,0.01143,0.03127],"tcp_start":[0.50686,0.11628,0.03091],"tcp_to_object_dist_end":0.03022,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":134.0,"n_steps_budget":1000.0,"object_pos_end":[0.49797,-0.0193,0.03378],"object_pos_start":[0.49786,-0.01853,0.03498],"object_to_goal_dist_end":0.06106,"object_to_goal_dist_start":0.06171,"object_z_max":0.03501,"peak_contact_force":0.53745,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":135.0,"raw_peak_contact_force":2.35952,"tcp_end":[0.49849,0.01994,0.14623],"tcp_start":[0.49918,0.01143,0.03127],"tcp_to_object_dist_end":0.1191,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `abe38b4b57ac37a91047e57d04e408cb1fd05583a47670bcb186dc9505a3f021`; realized-scene SHA-256: `c5fb87552d009c7e1ef813cadc54d289d6d9c896c1dd51a37fa468bf6305165e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48616,0.11898,0.04]},{"name":"goal","value":[0.48616,-0.04102,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48616,0.11898,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48616,-0.04102,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.17188,"average_solve_count":192.0,"average_success_count":192.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.lateral_offset_x":0.00322,"approach_1.lateral_offset_y":0.00399,"approach_1.speed":0.0262,"push_1.force_thresh":30.96372,"push_1.push_depth":-0.00732,"push_1.speed":0.0477,"retract_1.retract_height":0.13887,"retract_1.speed":0.07894},"optimized_scores":{"best_composite_score":-0.15434,"best_fitness_score":0.30566,"best_task_score":0.56717},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":746.0,"contact_point_centroid":[0.50697,0.11921,0.00739],"force_p95":221.69085,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":233.82131,"mean_force":118.91935,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49985,0.14042,0.05733]},{"body_a":"attachment","body_b":"peg","contact_count":542.0,"contact_point_centroid":[0.51079,0.12662,0.04954],"force_p95":225.11906,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":233.18799,"mean_force":163.77131,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50491,0.13608,0.04727]},{"body_a":"peg","body_b":"world","contact_count":82.0,"contact_point_centroid":[0.50283,0.13067,-1e-05],"force_p95":26.60276,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":28.7688,"mean_force":13.89549,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50458,0.135,0.04469]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":108.0,"contact_point_centroid":[0.52559,0.11784,0.04742],"force_p95":21.40951,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.54599,"mean_force":12.66561,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51951,0.13437,0.04581]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":31.0,"contact_point_centroid":[0.525,0.12,0.06],"force_p95":24.68499,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":25.204,"mean_force":17.93994,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51241,0.12461,0.0342]},{"body_a":"peg","body_b":"channel_base_body","contact_count":966.0,"contact_point_centroid":[0.50032,0.03136,0.00843],"force_p95":2.04319,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.63195,"mean_force":0.70506,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50936,0.08849,0.03379]},{"body_a":"peg","body_b":"channel_base_body","contact_count":106.0,"contact_point_centroid":[0.49481,0.01136,0.00853],"force_p95":0.82113,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.5358,"mean_force":0.82444,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50501,0.05646,0.07348]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":9.0,"contact_point_centroid":[0.47496,0.03581,0.02468],"force_p95":7.92973,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.13506,"mean_force":2.81244,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50458,0.05686,0.06251]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":37.0,"contact_point_centroid":[0.47344,0.08039,0.03018],"force_p95":5.59996,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.56709,"mean_force":1.20006,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51373,0.12661,0.03565]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":8.0,"contact_point_centroid":[0.47293,0.10287,0.0599],"force_p95":4.49986,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.83042,"mean_force":2.42174,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51835,0.13154,0.04018]},{"body_a":"attachment","body_b":"peg","contact_count":166.0,"contact_point_centroid":[0.50876,0.04844,0.0389],"force_p95":2.10502,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.52231,"mean_force":0.78324,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50723,0.06048,0.03405]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.50712,0.03823,0.0407],"force_p95":2.85617,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.14542,"mean_force":1.165,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50646,0.05041,0.03415]},{"body_a":"peg","body_b":"channel_base_body","contact_count":340.0,"contact_point_centroid":[0.49639,0.11903,0.00939],"force_p95":0.63431,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.56429,"phase_index":0.0,"phase_name":"align_1","phase_type":"approach","tcp_position_centroid":[0.49175,0.1803,0.19941]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"align_1","phase_type":"approach","tcp_position_centroid":[0.49959,0.19904,0.2964]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":2.0,"contact_point_centroid":[0.525,0.0112,0.02416],"force_p95":0.42367,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.42604,"mean_force":0.40228,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50901,0.08413,0.03374]}],"total_contact_groups":15},"final_pose_error":0.04988,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49447,0.01188,0.02419],"final_tcp_position":[0.50559,0.05748,0.12367],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":233.82131,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":365.0,"n_steps_budget":1000.0,"object_pos_end":[0.49602,0.11913,0.03403],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19926,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.57183,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":364.0,"raw_peak_contact_force":2.24822,"subtask_id":"approach","tcp_end":[0.48515,0.16278,0.10959],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08793,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":757.0,"n_steps_budget":1000.0,"object_pos_end":[0.48728,0.09856,0.04225],"object_pos_start":[0.49602,0.11913,0.03403],"object_to_goal_dist_end":0.17903,"object_to_goal_dist_start":0.19926,"object_z_max":0.04234,"peak_contact_force":0.73989,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1486.0,"raw_peak_contact_force":233.82131,"tcp_end":[0.51631,0.13071,0.03821],"tcp_start":[0.48515,0.16278,0.10959],"tcp_to_object_dist_end":0.04351,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49704,0.01277,0.02691],"object_pos_start":[0.48728,0.09856,0.04225],"object_to_goal_dist_end":0.09374,"object_to_goal_dist_start":0.17903,"object_z_max":0.04225,"peak_contact_force":2.05156,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1202.0,"raw_peak_contact_force":25.204,"subtask_id":"push","tcp_end":[0.50648,0.05048,0.03418],"tcp_start":[0.51631,0.13071,0.03821],"tcp_to_object_dist_end":0.03954,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":106.0,"n_steps_budget":1000.0,"object_pos_end":[0.49447,0.01188,0.02419],"object_pos_start":[0.49704,0.01277,0.02691],"object_to_goal_dist_end":0.09339,"object_to_goal_dist_start":0.09374,"object_z_max":0.02701,"peak_contact_force":0.61217,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":118.0,"raw_peak_contact_force":8.5358,"tcp_end":[0.50559,0.05748,0.12367],"tcp_start":[0.50648,0.05048,0.03418],"tcp_to_object_dist_end":0.10999,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```