## Search State

- **Seed**: 9
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → align → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | 0.0795 | 0.23 | ❌ rejected |
| 8 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 6 | 0.1261 | 0.00 | ❌ rejected |
| 7 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 6 | 0.3181 | 0.26 | ✅ accepted |
| 6 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 6 | 0.0974 | 0.11 | ❌ rejected |
| 5 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 6 | 0.0937 | 0.11 | ❌ rejected |

**Proposal policy**: task_score is 0.23 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.079) — your mutation base

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
    tolerance: 0.01
  parameters:
    lateral_x:
      type: scalar
      range:
      - -0.03
      - 0.03
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: add
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
    - 0.02
    - 0.0
    tolerance: 0.005
  parameters:
    contact_force:
      type: scalar
      range:
      - 1.0
      - 20.0
      default: 8.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
  subtask_id: contact
- id: push_channel
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: time_limit
  target:
    source: yaml
    anchor: world
    offset:
    - 0.5
    - -0.08
    - 0.04
    offset_along_axis:
      distance: 0.16
      axis: channel_axis
      mode: replace_offset_projection
      sign: positive
    tolerance: 0.02
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.16
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: push
- id: retract_up
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.02
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

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_peg** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.04, 0.0], tolerance=0.01
  - parameter_bindings:
    - lateral_x: status=consumed; consumers=target.offset.x (add)
    - speed: status=consumed; consumers=generator.speed (replace)
- **contact_peg** (`contact`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.02, 0.0], tolerance=0.005
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
- **push_channel** (`push`)
  - target: source=yaml, anchor=world, offset=[0.5, -0.08, 0.04], offset_along_axis={axis=channel_axis, distance=0.16, mode=replace_offset_projection, sign=positive}, tolerance=0.02
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
- **retract_up** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.079
- **task_score** (E): 0.225
- **fitness_score**: 0.369  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.490

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_high | 1.00 | 1.00 | 0.1146 |
| align_behind | 1.00 | 1.00 | 0.1646 |
| contact_peg | 1.00 | 1.00 | 0.0001 |
| push_channel | 0.33 | 1.00 | 0.1507 |
| retract_up | 1.00 | 1.00 | 0.1303 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_high | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.514, 0.166, 0.199) | (0.512, 0.067, 0.040)→(0.502, 0.066, 0.034) | 0.150→0.147 | 1.00 / 1.000 | 0.573 | 4.034 |
| align_behind | align | 1.00 / step_budget | (0.514, 0.166, 0.199)→(0.494, 0.112, 0.047) | (0.502, 0.066, 0.034)→(0.502, 0.067, 0.034) | 0.147→0.147 | 1.00 / 2.000 | 158.547 | 200.488 |
| contact_peg | contact | 1.00 / force_exceeded | (0.494, 0.112, 0.047)→(0.494, 0.112, 0.047) | (0.502, 0.067, 0.034)→(0.502, 0.067, 0.034) | 0.147→0.147 | 1.00 / 2.000 | 108.561 | 108.561 |
| push_channel | push | 0.33 / step_budget | (0.494, 0.112, 0.047)→(0.499, -0.038, 0.037) | (0.502, 0.067, 0.034)→(0.501, -0.045, 0.033) | 0.147→0.037 | 1.00 / 3.333 | 169.219 | 206.724 |
| retract_up | retract | 1.00 / step_budget | (0.499, -0.038, 0.037)→(0.497, -0.038, 0.168) | (0.501, -0.045, 0.033)→(0.501, -0.049, 0.032) | 0.037→0.033 | 1.00 / 1.667 | 0.492 | 73.797 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.871
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.294
- phase_score: 0.463
- phase_breakdown.approach_score: 0.414
- phase_breakdown.contact_score: 0.367
- phase_breakdown.push_score: 0.512

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.396
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.299
- **Median Q (composite search score)**: 0.104
- **K-run variance**: 0.0013
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.345


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.25105,"average_solve_count":239.0,"average_success_count":239.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_behind.align_speed":0.06382,"align_behind.lateral_x":-0.02268,"approach_high.approach_speed":0.04322,"approach_high.arc_height":0.14374,"contact_peg.contact_force":10.13888,"push_channel.push_distance":0.19929,"push_channel.push_speed":0.06229,"retract_up.retract_speed":0.06649},"optimized_scores":{"best_composite_score":0.10576,"best_fitness_score":0.39576,"best_task_score":0.29438},"replay_outcomes":[{"contacts":{"omitted_contact_groups":2,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":618.0,"contact_point_centroid":[0.53885,0.0016,0.05999],"force_p95":166.15469,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":184.02558,"mean_force":121.6575,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49376,0.00401,0.03746]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":66.0,"contact_point_centroid":[0.52502,-0.04645,0.05999],"force_p95":152.55984,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":182.03522,"mean_force":122.79854,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50068,-0.04639,0.03647]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":1.0,"contact_point_centroid":[0.47499,0.10731,0.04759],"force_p95":143.00726,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":143.00726,"mean_force":143.00726,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.48575,0.10723,0.0423]},{"body_a":"attachment","body_b":"peg","contact_count":866.0,"contact_point_centroid":[0.50018,0.00997,0.0373],"force_p95":119.38092,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":133.11741,"mean_force":71.94209,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49219,0.01718,0.03766]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":27.0,"contact_point_centroid":[0.47498,0.09871,0.04582],"force_p95":120.88553,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":122.3186,"mean_force":62.84418,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48571,0.09863,0.04049]},{"body_a":"peg","body_b":"channel_base_body","contact_count":956.0,"contact_point_centroid":[0.50876,-0.00809,0.00956],"force_p95":89.33392,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":103.85488,"mean_force":40.09127,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49209,0.01992,0.03779]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":842.0,"contact_point_centroid":[0.52614,-0.00065,0.03247],"force_p95":92.69461,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":96.32757,"mean_force":53.33459,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49198,0.01871,0.03769]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":43.0,"contact_point_centroid":[0.47499,0.11109,0.05354],"force_p95":79.60803,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":86.1056,"mean_force":65.4496,"phase_index":1.0,"phase_name":"align_behind","phase_type":"align","tcp_position_centroid":[0.48576,0.111,0.04829]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.5452,-0.04223,0.05997],"force_p95":60.86593,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":61.11959,"mean_force":54.06152,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.50067,-0.04672,0.0365]},{"body_a":"peg","body_b":"link7","contact_count":313.0,"contact_point_centroid":[0.52151,0.02284,0.06693],"force_p95":41.36746,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":43.88259,"mean_force":22.21871,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48867,0.04542,0.03802]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":4.0,"contact_point_centroid":[0.52501,-0.04678,0.06],"force_p95":29.54524,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":34.75911,"mean_force":8.68978,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.50067,-0.04672,0.0365]},{"body_a":"peg","body_b":"channel_base_body","contact_count":97.0,"contact_point_centroid":[0.50485,0.0628,0.00923],"force_p95":1.38128,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.68589,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.51254,0.20152,0.23667]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.50127,0.20216,0.2938]},{"body_a":"peg","body_b":"channel_base_body","contact_count":29.0,"contact_point_centroid":[0.50672,-0.1002,0.056],"force_p95":2.50338,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.59532,"mean_force":1.0974,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49993,-0.03929,0.03662]},{"body_a":"peg","body_b":"channel_base_body","contact_count":419.0,"contact_point_centroid":[0.50302,-0.07776,0.00941],"force_p95":0.57012,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.82066,"mean_force":0.53647,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.49773,-0.04656,0.10062]},{"body_a":"peg","body_b":"channel_base_body","contact_count":530.0,"contact_point_centroid":[0.50591,0.06306,0.00938],"force_p95":0.55305,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55904,"mean_force":0.54659,"phase_index":1.0,"phase_name":"align_behind","phase_type":"align","tcp_position_centroid":[0.50059,0.14331,0.11198]}],"total_contact_groups":18},"final_pose_error":0.01995,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50292,-0.07648,0.0338],"final_tcp_position":[0.49782,-0.04655,0.16673],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":184.02558,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":125.0,"n_steps_budget":1000.0,"object_pos_end":[0.50595,0.06297,0.03379],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14323,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54414,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":131.0,"raw_peak_contact_force":3.88411,"tcp_end":[0.52125,0.18098,0.19012],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.19647,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":530.0,"n_steps_budget":1000.0,"object_pos_end":[0.50603,0.063,0.03381],"object_pos_start":[0.50595,0.06297,0.03379],"object_to_goal_dist_end":0.14327,"object_to_goal_dist_start":0.14323,"object_z_max":0.03381,"peak_contact_force":65.0945,"phase_name":"align_behind","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":573.0,"raw_peak_contact_force":86.1056,"subtask_id":"approach","tcp_end":[0.48575,0.10723,0.0423],"tcp_start":[0.52125,0.18098,0.19012],"tcp_to_object_dist_end":0.04939,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.50603,0.06297,0.03381],"object_pos_start":[0.50603,0.063,0.03381],"object_to_goal_dist_end":0.14324,"object_to_goal_dist_start":0.14327,"object_z_max":0.03381,"peak_contact_force":143.00726,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":143.00726,"subtask_id":"contact","tcp_end":[0.48576,0.10714,0.04217],"tcp_start":[0.48575,0.10723,0.0423],"tcp_to_object_dist_end":0.04931,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50304,-0.07661,0.03398],"object_pos_start":[0.50603,0.06297,0.03381],"object_to_goal_dist_end":0.00755,"object_to_goal_dist_start":0.14324,"object_z_max":0.04189,"peak_contact_force":176.20562,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3717.0,"raw_peak_contact_force":184.02558,"tcp_end":[0.50067,-0.04673,0.03648],"tcp_start":[0.48576,0.10714,0.04217],"tcp_to_object_dist_end":0.03007,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":419.0,"n_steps_budget":1000.0,"object_pos_end":[0.50292,-0.07648,0.0338],"object_pos_start":[0.50304,-0.07661,0.03398],"object_to_goal_dist_end":0.0077,"object_to_goal_dist_start":0.00755,"object_z_max":0.03429,"peak_contact_force":0.54133,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":450.0,"raw_peak_contact_force":61.11959,"tcp_end":[0.49782,-0.04655,0.16673],"tcp_start":[0.50067,-0.04673,0.03648],"tcp_to_object_dist_end":0.13635,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.55026,"average_solve_count":189.0,"average_success_count":189.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_behind.align_speed":0.08737,"align_behind.lateral_x":0.00442,"approach_high.approach_speed":0.07725,"approach_high.arc_height":0.09734,"contact_peg.contact_force":8.10014,"push_channel.push_distance":0.19738,"push_channel.push_speed":0.04755,"retract_up.retract_speed":0.09995},"optimized_scores":{"best_composite_score":0.02833,"best_fitness_score":0.31833,"best_task_score":0.08292},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":134.0,"contact_point_centroid":[0.52506,0.10147,0.05997],"force_p95":333.27115,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":369.32577,"mean_force":316.44259,"phase_index":1.0,"phase_name":"align_behind","phase_type":"align","tcp_position_centroid":[0.51178,0.10147,0.05942]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":19.0,"contact_point_centroid":[0.54568,-0.0481,0.05997],"force_p95":213.02866,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":232.02241,"mean_force":120.31021,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50024,-0.04118,0.03885]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":801.0,"contact_point_centroid":[0.52504,-0.00368,0.05998],"force_p95":201.83711,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":218.42844,"mean_force":152.22665,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50215,-0.00356,0.04209]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":4.0,"contact_point_centroid":[0.52507,-0.0421,0.05996],"force_p95":84.96924,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":99.96381,"mean_force":24.99095,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.50019,-0.04178,0.03887]},{"body_a":"peg","body_b":"channel_base_body","contact_count":999.0,"contact_point_centroid":[0.49701,0.00986,0.00888],"force_p95":54.24016,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":68.1757,"mean_force":25.41579,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50286,0.00639,0.04337]},{"body_a":"attachment","body_b":"peg","contact_count":777.0,"contact_point_centroid":[0.50367,0.00572,0.04236],"force_p95":60.76931,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":68.07921,"mean_force":34.86711,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.5023,-0.00165,0.04237]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.52503,0.10154,0.05999],"force_p95":63.69533,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":63.69533,"mean_force":63.69533,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.51105,0.10151,0.05824]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.54564,-0.04872,0.05997],"force_p95":59.4501,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":61.3068,"mean_force":38.16622,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.5002,-0.04178,0.03884]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":630.0,"contact_point_centroid":[0.47473,-0.0173,0.02551],"force_p95":30.05059,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":34.70478,"mean_force":18.21273,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50137,-0.01473,0.04076]},{"body_a":"peg","body_b":"channel_base_body","contact_count":399.0,"contact_point_centroid":[0.50207,0.0,0.00809],"force_p95":0.72616,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.99573,"mean_force":0.6244,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.4973,-0.04163,0.10319]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":5.0,"contact_point_centroid":[0.52502,0.02326,0.02431],"force_p95":6.25875,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.70592,"mean_force":1.85497,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.49695,-0.04161,0.11013]},{"body_a":"peg","body_b":"channel_base_body","contact_count":110.0,"contact_point_centroid":[0.50469,0.0567,0.00926],"force_p95":1.55556,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.69131,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.5321,0.1449,0.26163]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.50546,0.19038,0.29821]},{"body_a":"peg","body_b":"channel_base_body","contact_count":555.0,"contact_point_centroid":[0.50614,0.05656,0.00938],"force_p95":0.59955,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63861,"mean_force":0.54643,"phase_index":1.0,"phase_name":"align_behind","phase_type":"align","tcp_position_centroid":[0.5228,0.11066,0.11469]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.49293,0.06878,0.00938],"force_p95":0.54735,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54735,"mean_force":0.54735,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.51105,0.10151,0.05824]}],"total_contact_groups":15},"final_pose_error":0.01984,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5025,0.0001,0.02409],"final_tcp_position":[0.49742,-0.04161,0.16919],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":369.32577,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":139.0,"n_steps_budget":1000.0,"object_pos_end":[0.50616,0.0566,0.03376],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.13688,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":0.59922,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":147.0,"raw_peak_contact_force":4.44541,"tcp_end":[0.54224,0.1261,0.2085],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.19148,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":555.0,"n_steps_budget":1000.0,"object_pos_end":[0.50611,0.05664,0.03379],"object_pos_start":[0.50616,0.0566,0.03376],"object_to_goal_dist_end":0.13691,"object_to_goal_dist_start":0.13688,"object_z_max":0.03382,"peak_contact_force":320.43038,"phase_name":"align_behind","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":689.0,"raw_peak_contact_force":369.32577,"subtask_id":"approach","tcp_end":[0.51105,0.10151,0.05824],"tcp_start":[0.54224,0.1261,0.2085],"tcp_to_object_dist_end":0.05134,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.50613,0.05665,0.03379],"object_pos_start":[0.50611,0.05664,0.03379],"object_to_goal_dist_end":0.13693,"object_to_goal_dist_start":0.13691,"object_z_max":0.03379,"peak_contact_force":63.69533,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":63.69533,"subtask_id":"contact","tcp_end":[0.51106,0.10152,0.05822],"tcp_start":[0.51105,0.10151,0.05824],"tcp_to_object_dist_end":0.05133,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49636,0.00051,0.02453],"object_pos_start":[0.50613,0.05665,0.03379],"object_to_goal_dist_end":0.08206,"object_to_goal_dist_start":0.13693,"object_z_max":0.04052,"peak_contact_force":173.38244,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3226.0,"raw_peak_contact_force":232.02241,"tcp_end":[0.50022,-0.04177,0.03883],"tcp_start":[0.51106,0.10152,0.05822],"tcp_to_object_dist_end":0.0448,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":399.0,"n_steps_budget":960.0,"object_pos_end":[0.5025,0.0001,0.02409],"object_pos_start":[0.49636,0.00051,0.02453],"object_to_goal_dist_end":0.0817,"object_to_goal_dist_start":0.08206,"object_z_max":0.02461,"peak_contact_force":0.49887,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":411.0,"raw_peak_contact_force":99.96381,"tcp_end":[0.49742,-0.04161,0.16919],"tcp_start":[0.50022,-0.04177,0.03883],"tcp_to_object_dist_end":0.15106,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.13428,"average_solve_count":283.0,"average_success_count":283.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_behind.align_speed":0.01006,"align_behind.lateral_x":-0.01173,"approach_high.approach_speed":0.05068,"approach_high.arc_height":0.17135,"contact_peg.contact_force":9.66309,"push_channel.push_distance":0.12521,"push_channel.push_speed":0.06725,"retract_up.retract_speed":0.06316},"optimized_scores":{"best_composite_score":0.10431,"best_fitness_score":0.39431,"best_task_score":0.29895},"replay_outcomes":[{"contacts":{"omitted_contact_groups":2,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":637.0,"contact_point_centroid":[0.53742,0.01842,0.05998],"force_p95":180.26767,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":204.12551,"mean_force":148.80757,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49229,0.02147,0.03743]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":109.0,"contact_point_centroid":[0.47494,0.11479,0.0447],"force_p95":170.07661,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":171.49297,"mean_force":115.55947,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48507,0.1175,0.03974]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":107.0,"contact_point_centroid":[0.47498,0.11998,0.05169],"force_p95":95.19374,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":146.03356,"mean_force":84.43019,"phase_index":1.0,"phase_name":"align_behind","phase_type":"align","tcp_position_centroid":[0.48113,0.12943,0.0485]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":1.0,"contact_point_centroid":[0.47497,0.11998,0.04528],"force_p95":118.97968,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":118.97968,"mean_force":118.97968,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.48389,0.12661,0.04084]},{"body_a":"attachment","body_b":"peg","contact_count":658.0,"contact_point_centroid":[0.4994,0.01145,0.03702],"force_p95":69.84284,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":79.16024,"mean_force":23.59147,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49235,0.02084,0.03747]},{"body_a":"peg","body_b":"channel_base_body","contact_count":806.0,"contact_point_centroid":[0.50443,0.00085,0.00973],"force_p95":51.1216,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":63.26399,"mean_force":11.11642,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49112,0.03705,0.03781]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.54221,-0.03103,0.05997],"force_p95":59.33329,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":60.30653,"mean_force":52.02034,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.49762,-0.0254,0.03676]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":599.0,"contact_point_centroid":[0.52527,-0.00559,0.02522],"force_p95":33.93145,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":45.35511,"mean_force":16.92353,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49283,0.01541,0.03743]},{"body_a":"peg","body_b":"channel_base_body","contact_count":82.0,"contact_point_centroid":[0.49575,0.08,0.00928],"force_p95":1.73888,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.77147,"mean_force":0.70258,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.48794,0.20284,0.24074]},{"body_a":"peg","body_b":"link7","contact_count":17.0,"contact_point_centroid":[0.51688,0.00932,0.06988],"force_p95":2.98258,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.05574,"mean_force":2.30069,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49064,0.03639,0.03767]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46907,0.07994,0.03235],"force_p95":1.18295,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.95027,"mean_force":0.45938,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.49845,0.20199,0.29246]},{"body_a":"peg","body_b":"channel_base_body","contact_count":417.0,"contact_point_centroid":[0.50034,-0.06151,0.00998],"force_p95":1.59912,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.68582,"mean_force":0.5998,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.49468,-0.02528,0.1012]},{"body_a":"peg","body_b":"channel_base_body","contact_count":299.0,"contact_point_centroid":[0.49713,-0.10004,0.0423],"force_p95":1.60403,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.36158,"mean_force":0.26565,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.49444,-0.02524,0.11992]},{"body_a":"attachment","body_b":"peg","contact_count":9.0,"contact_point_centroid":[0.50175,-0.03636,0.03503],"force_p95":2.09062,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.24287,"mean_force":0.79891,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.49749,-0.02548,0.03699]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":7.0,"contact_point_centroid":[0.47484,0.06982,0.05998],"force_p95":1.83724,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.94252,"mean_force":0.77856,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48578,0.10075,0.03814]},{"body_a":"peg","body_b":"channel_base_body","contact_count":645.0,"contact_point_centroid":[0.49384,0.07995,0.00938],"force_p95":0.58906,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65031,"mean_force":0.54649,"phase_index":1.0,"phase_name":"align_behind","phase_type":"align","tcp_position_centroid":[0.47795,0.15397,0.1106]}],"total_contact_groups":18},"final_pose_error":0.01985,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49805,-0.06932,0.03958],"final_tcp_position":[0.49479,-0.02523,0.1671],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.47029,0.07994,0.04]},"peak_contact_force":204.12551,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":110.0,"n_steps_budget":1000.0,"object_pos_end":[0.49383,0.07987,0.03377],"object_pos_start":[0.47029,0.07994,0.04],"object_to_goal_dist_end":0.16011,"object_to_goal_dist_start":0.16268,"object_z_max":0.04001,"peak_contact_force":0.57526,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":117.0,"raw_peak_contact_force":3.77147,"tcp_end":[0.47878,0.18969,0.19805],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.19818,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":645.0,"n_steps_budget":1000.0,"object_pos_end":[0.49381,0.07993,0.03378],"object_pos_start":[0.49383,0.07987,0.03377],"object_to_goal_dist_end":0.16017,"object_to_goal_dist_start":0.16011,"object_z_max":0.03379,"peak_contact_force":90.11564,"phase_name":"align_behind","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":752.0,"raw_peak_contact_force":146.03356,"subtask_id":"approach","tcp_end":[0.48389,0.12661,0.04084],"tcp_start":[0.47878,0.18969,0.19805],"tcp_to_object_dist_end":0.04824,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.4938,0.07995,0.03378],"object_pos_start":[0.49381,0.07993,0.03378],"object_to_goal_dist_end":0.16019,"object_to_goal_dist_start":0.16017,"object_z_max":0.03378,"peak_contact_force":118.97968,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":118.97968,"subtask_id":"contact","tcp_end":[0.48394,0.12657,0.04077],"tcp_start":[0.48389,0.12661,0.04084],"tcp_to_object_dist_end":0.04817,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":945.0,"n_steps_budget":1000.0,"object_pos_end":[0.50383,-0.0596,0.04024],"object_pos_start":[0.4938,0.07995,0.03378],"object_to_goal_dist_end":0.02076,"object_to_goal_dist_start":0.16019,"object_z_max":0.04173,"peak_contact_force":158.06768,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2833.0,"raw_peak_contact_force":204.12551,"tcp_end":[0.49761,-0.0253,0.03675],"tcp_start":[0.48394,0.12657,0.04077],"tcp_to_object_dist_end":0.03503,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":420.0,"n_steps_budget":1000.0,"object_pos_end":[0.49805,-0.06932,0.03958],"object_pos_start":[0.50383,-0.0596,0.04024],"object_to_goal_dist_end":0.01086,"object_to_goal_dist_start":0.02076,"object_z_max":0.04079,"peak_contact_force":0.43532,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":903.0,"raw_peak_contact_force":60.30653,"tcp_end":[0.49479,-0.02523,0.1671],"tcp_start":[0.49761,-0.0253,0.03675],"tcp_to_object_dist_end":0.13497,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```