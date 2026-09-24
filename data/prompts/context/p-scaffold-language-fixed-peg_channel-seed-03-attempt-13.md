## Search State

- **Seed**: 3
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | -0.1634 | 0.08 | ❌ rejected |
| 12 | approach → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 9 | 0.0037 | 0.24 | ❌ rejected |
| 11 | approach → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 9 | 0.1012 | 0.32 | ❌ rejected |
| 10 | approach → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | 0.3813 | 0.52 | ✅ accepted |
| 9 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.1035 | 0.22 | ❌ rejected |

**Proposal policy**: task_score is 0.08 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `990d03f436076caee02f5d9d8b3b9b0b3759564b7644084e4eac46818881d834`
- Frozen object start: [0.46685193337148995, 0.058944840527687975, 0.04]
- Frozen task target: [0.46685193337148995, -0.10105515947231203, 0.04]
- Goal object position: (0.46685193337148995, -0.10105515947231203, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.46685193337148995, 0.058944840527687975, 0.04)
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
  frozen_object_start: [0.4669, 0.0589, 0.04]
  frozen_task_target: [0.4669, -0.1011, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.46685193337148995, 0.058944840527687975, 0.04]}
  frozen_targets: {'channel_exit': [0.46685193337148995, -0.10105515947231203, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: 990d03f436076caee02f5d9d8b3b9b0b3759564b7644084e4eac46818881d834

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

## Current Skill (Q=-0.163) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
phases:
- id: prep_1
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
    - 0.1
    tolerance: 0.02
  parameters:
    speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace
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
    tolerance: 0.015
  parameters:
    lateral_offset:
      type: scalar
      range:
      - -0.01
      - 0.01
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: add
    speed:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
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
  parameters:
    contact_force:
      type: scalar
      range:
      - 2.0
      - 15.0
      default: 8.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    speed:
      type: scalar
      range:
      - 0.005
      - 0.04
      default: 0.015
      binds_to:
      - path: generator.speed
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
    offset_along_axis:
      distance: 0.16
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
  parameters:
    push_depth:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.16
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.04
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
      - 0.02
      - 0.1
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **prep_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.04, 0.1], tolerance=0.02
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.04, 0.0], tolerance=0.015
  - parameter_bindings:
    - lateral_offset: status=consumed; consumers=target.offset.x (add)
    - speed: status=consumed; consumers=generator.speed (replace)
- **contact_1** (`contact`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.02, 0.0], tolerance=0.01
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=world, offset=[0.5, -0.08, 0.04], offset_along_axis={axis=channel_axis, distance=0.16, mode=add_to_offset, sign=positive}, tolerance=0.02
  - parameter_bindings:
    - push_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: -0.163
- **task_score** (E): 0.081
- **fitness_score**: 0.193  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.133
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.490

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_above | 1.00 | 1.00 | 0.2106 |
| approach_1 | 1.00 | 1.00 | 0.1181 |
| contact_1 | 0.67 | 1.00 | 0.0089 |
| push_1 | 0.00 | 1.00 | 0.0001 |
| retract_1 | 1.00 | 1.00 | 0.1304 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_above | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.497, 0.056, 0.147) | (0.509, 0.081, 0.040)→(0.502, 0.081, 0.034) | 0.165→0.162 | 1.00 / 1.000 | 0.545 | 3.954 |
| approach_1 | approach | 1.00 / step_budget | (0.497, 0.056, 0.147)→(0.503, 0.116, 0.047) | (0.502, 0.081, 0.034)→(0.499, 0.080, 0.035) | 0.162→0.160 | 1.00 / 1.667 | 123.702 | 226.616 |
| contact_1 | contact | 0.67 / force_exceeded | (0.503, 0.116, 0.047)→(0.499, 0.112, 0.041) | (0.499, 0.080, 0.035)→(0.498, 0.072, 0.037) | 0.160→0.152 | 1.00 / 1.667 | 18.153 | 18.366 |
| push_1 | push | 0.00 / guard_failure | (0.497, 0.098, 0.039)→(0.497, 0.098, 0.039) | (0.498, 0.072, 0.037)→(0.500, 0.063, 0.039) | 0.152→0.143 | 1.00 / 2.000 | 98.863 | 113.313 |
| retract_1 | retract | 1.00 / step_budget | (0.497, 0.098, 0.039)→(0.494, 0.098, 0.169) | (0.500, 0.063, 0.039)→(0.501, 0.045, 0.027) | 0.143→0.126 | 1.00 / 1.000 | 0.590 | 155.870 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.386
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.091
- phase_score: 0.236
- phase_breakdown.approach_score: 0.547
- phase_breakdown.contact_score: 0.511
- phase_breakdown.push_score: 0.040

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.234
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.149
- **Median Q (composite search score)**: -0.122
- **K-run variance**: 0.0043
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.264


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `cc7283febf3c95cef1fde4c5a16cbcb134186cb6faf3a169717a9aa53375931d`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `178d67757a065da6e29d31070e25f6065dc7e42bdbf58dfbff0deec513214033`; realized-scene SHA-256: `990d03f436076caee02f5d9d8b3b9b0b3759564b7644084e4eac46818881d834`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.46685,0.05894,0.04]},{"name":"goal","value":[0.46685,-0.10106,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.46685,0.05894,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.46685,-0.10106,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.02844,"average_solve_count":211.0,"average_success_count":211.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_above.speed":0.05594,"approach_1.lateral_offset":-0.00417,"approach_1.speed":0.03753,"contact_1.contact_force":11.41244,"contact_1.speed":0.01427,"push_1.push_depth":0.01519,"push_1.speed":0.04362,"retract_1.speed":0.07108},"optimized_scores":{"best_composite_score":-0.12195,"best_fitness_score":0.16805,"best_task_score":0.0018},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":33.0,"contact_point_centroid":[0.47497,0.08602,0.05194],"force_p95":214.48144,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":237.80556,"mean_force":137.17244,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4857,0.08596,0.04662]},{"body_a":"peg","body_b":"channel_base_body","contact_count":284.0,"contact_point_centroid":[0.49488,0.05812,0.00934],"force_p95":0.96253,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":94.55428,"mean_force":2.61956,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49155,0.07253,0.0969]},{"body_a":"attachment","body_b":"peg","contact_count":13.0,"contact_point_centroid":[0.49406,0.07658,0.05821],"force_p95":91.55741,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":93.9974,"mean_force":45.35359,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4886,0.08646,0.06039]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.53165,0.0872,0.05995],"force_p95":60.32974,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":61.41847,"mean_force":52.7028,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48622,0.08676,0.03768]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.53163,0.08723,0.05996],"force_p95":51.0395,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":51.33265,"mean_force":48.32997,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4862,0.08679,0.0377]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.53161,0.08727,0.05998],"force_p95":20.82769,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":21.08242,"mean_force":18.53516,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48618,0.08682,0.03775]},{"body_a":"peg","body_b":"channel_base_body","contact_count":103.0,"contact_point_centroid":[0.49441,0.05277,0.00946],"force_p95":3.76906,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.63956,"mean_force":0.95187,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48622,0.08915,0.04094]},{"body_a":"attachment","body_b":"peg","contact_count":26.0,"contact_point_centroid":[0.4937,0.07586,0.05279],"force_p95":4.217,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.3141,"mean_force":1.8642,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48609,0.08764,0.03881]},{"body_a":"peg","body_b":"channel_base_body","contact_count":414.0,"contact_point_centroid":[0.49436,0.05893,0.00934],"force_p95":0.59575,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.58153,"phase_index":0.0,"phase_name":"align_above","phase_type":"approach","tcp_position_centroid":[0.49786,0.12442,0.21819]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"align_above","phase_type":"approach","tcp_position_centroid":[0.49938,0.19636,0.29572]},{"body_a":"peg","body_b":"channel_base_body","contact_count":408.0,"contact_point_centroid":[0.49443,0.05487,0.00953],"force_p95":0.5883,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.74425,"mean_force":0.52782,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4838,0.08608,0.10204]},{"body_a":"attachment","body_b":"peg","contact_count":27.0,"contact_point_centroid":[0.49182,0.07423,0.05658],"force_p95":0.58209,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.69942,"mean_force":0.45297,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48568,0.08595,0.04819]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.49626,0.04041,0.00979],"force_p95":0.43329,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.43371,"mean_force":0.42954,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4862,0.08679,0.0377]}],"total_contact_groups":13},"final_pose_error":0.01978,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.4942,0.05834,0.034],"final_tcp_position":[0.48348,0.08626,0.16808],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":237.80556,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":443.0,"n_steps_budget":1000.0,"object_pos_end":[0.49418,0.05887,0.03386],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13912,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54079,"phase_name":"align_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":449.0,"raw_peak_contact_force":4.20518,"tcp_end":[0.4972,0.0556,0.14662],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11285,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":284.0,"n_steps_budget":1000.0,"object_pos_end":[0.49401,0.05925,0.03406],"object_pos_start":[0.49418,0.05887,0.03386],"object_to_goal_dist_end":0.1395,"object_to_goal_dist_start":0.13912,"object_z_max":0.03427,"peak_contact_force":0.63043,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":297.0,"raw_peak_contact_force":94.55428,"subtask_id":"approach","tcp_end":[0.48769,0.09181,0.0465],"tcp_start":[0.4972,0.0556,0.14662],"tcp_to_object_dist_end":0.03542,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":103.0,"n_steps_budget":840.0,"object_pos_end":[0.49444,0.05744,0.03516],"object_pos_start":[0.49401,0.05925,0.03406],"object_to_goal_dist_end":0.13764,"object_to_goal_dist_start":0.1395,"object_z_max":0.03513,"peak_contact_force":21.08242,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":131.0,"raw_peak_contact_force":21.08242,"subtask_id":"contact","tcp_end":[0.48619,0.0868,0.03772],"tcp_start":[0.48769,0.09181,0.0465],"tcp_to_object_dist_end":0.0306,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.49447,0.05742,0.03519],"object_pos_start":[0.49444,0.05744,0.03516],"object_to_goal_dist_end":0.13762,"object_to_goal_dist_start":0.13764,"object_z_max":0.03521,"peak_contact_force":51.33265,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":6.0,"raw_peak_contact_force":51.33265,"subtask_id":"push","tcp_end":[0.48622,0.08677,0.03767],"tcp_start":[0.48621,0.08678,0.03768],"tcp_to_object_dist_end":0.03059,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":408.0,"n_steps_budget":1000.0,"object_pos_end":[0.4942,0.05834,0.034],"object_pos_start":[0.49453,0.05743,0.03521],"object_to_goal_dist_end":0.13859,"object_to_goal_dist_start":0.13762,"object_z_max":0.03577,"peak_contact_force":0.54277,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":472.0,"raw_peak_contact_force":237.80556,"tcp_end":[0.48348,0.08626,0.16808],"tcp_start":[0.48622,0.08677,0.03767],"tcp_to_object_dist_end":0.13738,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1ee374347cb6f80436633ebcb956aaa73ea8a10685d65b21d5c3814cf0c53498`; realized-scene SHA-256: `5d75b33f12bcf5a2f8bdcc4693a93f63ce145f4d32d6acfe75032964e261854c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53544,0.08091,0.04]},{"name":"goal","value":[0.53544,-0.07909,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.53544,0.08091,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.53544,-0.07909,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.07763,"average_solve_count":219.0,"average_success_count":219.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_above.speed":0.06923,"approach_1.lateral_offset":0.00163,"approach_1.speed":0.04248,"contact_1.contact_force":9.26697,"contact_1.speed":0.02123,"push_1.push_depth":0.02016,"push_1.speed":0.02755,"retract_1.speed":0.05913},"optimized_scores":{"best_composite_score":-0.1121,"best_fitness_score":0.1779,"best_task_score":0.0909},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":26.0,"contact_point_centroid":[0.52509,0.11472,0.05996],"force_p95":393.05924,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":396.88973,"mean_force":355.26302,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50778,0.11472,0.04971]},{"body_a":"attachment","body_b":"peg","contact_count":77.0,"contact_point_centroid":[0.5134,0.10164,0.0551],"force_p95":163.06296,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":169.5503,"mean_force":113.74295,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50502,0.10744,0.05647]},{"body_a":"peg","body_b":"channel_base_body","contact_count":360.0,"contact_point_centroid":[0.50624,0.08411,0.00919],"force_p95":151.23473,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":165.05851,"mean_force":24.45527,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49999,0.08537,0.09167]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":57.0,"contact_point_centroid":[0.52536,0.08629,0.0582],"force_p95":45.09068,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":47.81157,"mean_force":27.51958,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50546,0.10804,0.05591]},{"body_a":"peg","body_b":"channel_base_body","contact_count":104.0,"contact_point_centroid":[0.50489,0.05642,0.00974],"force_p95":38.15148,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":40.81541,"mean_force":16.06599,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50391,0.0992,0.04446]},{"body_a":"attachment","body_b":"peg","contact_count":50.0,"contact_point_centroid":[0.5051,0.07776,0.04267],"force_p95":38.34572,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.44695,"mean_force":32.58922,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50306,0.08895,0.04332]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.52501,0.11619,0.06],"force_p95":36.29753,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":36.29753,"mean_force":36.29753,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50659,0.11616,0.04777]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":2.0,"contact_point_centroid":[0.52503,0.11612,0.05999],"force_p95":31.25589,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":32.90093,"mean_force":16.45047,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50671,0.1161,0.04789]},{"body_a":"peg","body_b":"channel_base_body","contact_count":428.0,"contact_point_centroid":[0.49966,0.03203,0.00898],"force_p95":0.83847,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.56839,"mean_force":0.63899,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50003,0.07982,0.10723]},{"body_a":"attachment","body_b":"peg","contact_count":13.0,"contact_point_centroid":[0.50476,0.06859,0.04267],"force_p95":12.15708,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.86181,"mean_force":2.41172,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50247,0.0799,0.04347]},{"body_a":"peg","body_b":"channel_base_body","contact_count":405.0,"contact_point_centroid":[0.50565,0.08086,0.00935],"force_p95":0.56136,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.58444,"phase_index":0.0,"phase_name":"align_above","phase_type":"approach","tcp_position_centroid":[0.49788,0.12439,0.21816]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"align_above","phase_type":"approach","tcp_position_centroid":[0.49938,0.19595,0.29525]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":17.0,"contact_point_centroid":[0.5252,0.06053,0.05999],"force_p95":0.84861,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.74014,"mean_force":0.28221,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50363,0.10104,0.04405]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47471,0.03508,0.0579],"force_p95":0.63878,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.69621,"mean_force":0.16314,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50037,0.0797,0.05686]},{"body_a":"peg","body_b":"channel_base_body","contact_count":2.0,"contact_point_centroid":[0.49315,0.06252,0.00889],"force_p95":0.60815,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60972,"mean_force":0.5941,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50671,0.1161,0.04789]}],"total_contact_groups":15},"final_pose_error":0.01981,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50151,0.01911,0.02415],"final_tcp_position":[0.5002,0.07992,0.17358],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":396.88973,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":434.0,"n_steps_budget":1000.0,"object_pos_end":[0.50596,0.08087,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54815,"phase_name":"align_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":441.0,"raw_peak_contact_force":4.32595,"tcp_end":[0.49722,0.05576,0.14678],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11609,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":360.0,"n_steps_budget":1000.0,"object_pos_end":[0.50129,0.07344,0.03539],"object_pos_start":[0.50596,0.08087,0.03378],"object_to_goal_dist_end":0.15351,"object_to_goal_dist_start":0.1611,"object_z_max":0.03523,"peak_contact_force":370.02183,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":520.0,"raw_peak_contact_force":396.88973,"subtask_id":"approach","tcp_end":[0.50675,0.11607,0.04793],"tcp_start":[0.49722,0.05576,0.14678],"tcp_to_object_dist_end":0.04477,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":2.0,"n_steps_budget":780.0,"object_pos_end":[0.5014,0.0728,0.03573],"object_pos_start":[0.50129,0.07344,0.03539],"object_to_goal_dist_end":0.15287,"object_to_goal_dist_start":0.15351,"object_z_max":0.03555,"peak_contact_force":32.90093,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":4.0,"raw_peak_contact_force":32.90093,"subtask_id":"contact","tcp_end":[0.50659,0.11616,0.04777],"tcp_start":[0.50675,0.11607,0.04793],"tcp_to_object_dist_end":0.0453,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":104.0,"n_steps_budget":1000.0,"object_pos_end":[0.50538,0.05138,0.03996],"object_pos_start":[0.5014,0.0728,0.03573],"object_to_goal_dist_end":0.13149,"object_to_goal_dist_start":0.15287,"object_z_max":0.03996,"peak_contact_force":15.79086,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":172.0,"raw_peak_contact_force":40.81541,"subtask_id":"push","tcp_end":[0.50298,0.08039,0.04319],"tcp_start":[0.50298,0.08059,0.04323],"tcp_to_object_dist_end":0.02929,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":436.0,"n_steps_budget":1000.0,"object_pos_end":[0.50151,0.01911,0.02415],"object_pos_start":[0.50548,0.05096,0.03996],"object_to_goal_dist_end":0.10038,"object_to_goal_dist_start":0.13107,"object_z_max":0.04077,"peak_contact_force":0.56859,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":469.0,"raw_peak_contact_force":16.56839,"tcp_end":[0.5002,0.07992,0.17358],"tcp_start":[0.50298,0.08039,0.04319],"tcp_to_object_dist_end":0.16134,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `e082b57d1be6744ae6d3993c25b90215f3fc56dc7131af62e0630c4f325e4b04`; realized-scene SHA-256: `ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5244,0.10464,0.04]},{"name":"goal","value":[0.5244,-0.05536,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.5244,0.10464,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.5244,-0.05536,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.8913,"average_solve_count":276.0,"average_success_count":276.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_above.speed":0.05189,"approach_1.lateral_offset":0.0044,"approach_1.speed":0.05642,"contact_1.contact_force":8.13001,"contact_1.speed":0.02966,"push_1.push_depth":0.01858,"push_1.speed":0.04036,"retract_1.speed":0.03123},"optimized_scores":{"best_composite_score":-0.25607,"best_fitness_score":0.23393,"best_task_score":0.14914},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.5492,0.12,0.05994],"force_p95":245.95762,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":247.79009,"mean_force":182.84714,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50262,0.1283,0.03471]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":9.0,"contact_point_centroid":[0.5488,0.11999,0.05989],"force_p95":194.3372,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":213.23696,"mean_force":69.81878,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50246,0.12727,0.03472]},{"body_a":"attachment","body_b":"peg","contact_count":118.0,"contact_point_centroid":[0.51796,0.12362,0.05401],"force_p95":176.04501,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":188.40251,"mean_force":135.96903,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50912,0.12862,0.05513]},{"body_a":"peg","body_b":"channel_base_body","contact_count":414.0,"contact_point_centroid":[0.50816,0.10892,0.0091],"force_p95":165.07447,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":177.99563,"mean_force":38.22414,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50174,0.09718,0.09043]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":102.0,"contact_point_centroid":[0.5254,0.11231,0.05757],"force_p95":51.44594,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":59.96605,"mean_force":31.02328,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50964,0.12947,0.05458]},{"body_a":"peg","body_b":"channel_base_body","contact_count":441.0,"contact_point_centroid":[0.50528,0.06037,0.00829],"force_p95":0.74072,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.34785,"mean_force":0.64622,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4996,0.12692,0.09915]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":9.0,"contact_point_centroid":[0.52502,0.03362,0.02395],"force_p95":8.93255,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.98959,"mean_force":2.28375,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49937,0.12687,0.07273]},{"body_a":"peg","body_b":"channel_base_body","contact_count":417.0,"contact_point_centroid":[0.50563,0.10467,0.00937],"force_p95":0.57962,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.57345,"phase_index":0.0,"phase_name":"align_above","phase_type":"approach","tcp_position_centroid":[0.49786,0.12474,0.21852]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"align_above","phase_type":"approach","tcp_position_centroid":[0.49942,0.19686,0.29633]},{"body_a":"peg","body_b":"channel_base_body","contact_count":77.0,"contact_point_centroid":[0.49504,0.09224,0.00934],"force_p95":1.01418,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.11319,"mean_force":0.51159,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.5089,0.13689,0.04152]},{"body_a":"peg","body_b":"channel_base_body","contact_count":20.0,"contact_point_centroid":[0.50002,0.08429,0.00996],"force_p95":0.56313,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.58015,"mean_force":0.50191,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50331,0.13093,0.03538]},{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.5116,0.12947,0.05531],"force_p95":0.46229,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.48662,"mean_force":0.24331,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.51383,0.13996,0.04717]}],"total_contact_groups":12},"final_pose_error":0.0199,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50593,0.05784,0.02414],"final_tcp_position":[0.49972,0.12704,0.16498],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":247.79009,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":444.0,"n_steps_budget":1000.0,"object_pos_end":[0.50591,0.10456,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18476,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.54743,"phase_name":"align_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":449.0,"raw_peak_contact_force":3.33087,"tcp_end":[0.4972,0.05553,0.14655],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12322,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":414.0,"n_steps_budget":1000.0,"object_pos_end":[0.50265,0.10834,0.03542],"object_pos_start":[0.50591,0.10456,0.03384],"object_to_goal_dist_end":0.18842,"object_to_goal_dist_start":0.18476,"object_z_max":0.03541,"peak_contact_force":0.45371,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":634.0,"raw_peak_contact_force":188.40251,"subtask_id":"approach","tcp_end":[0.51394,0.13994,0.04732],"tcp_start":[0.4972,0.05553,0.14655],"tcp_to_object_dist_end":0.0356,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":77.0,"n_steps_budget":600.0,"object_pos_end":[0.49928,0.08457,0.04079],"object_pos_start":[0.50265,0.10834,0.03542],"object_to_goal_dist_end":0.16457,"object_to_goal_dist_start":0.18842,"object_z_max":0.04079,"peak_contact_force":0.47429,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":79.0,"raw_peak_contact_force":1.11319,"subtask_id":"contact","tcp_end":[0.50425,0.13282,0.03637],"tcp_start":[0.51394,0.13994,0.04732],"tcp_to_object_dist_end":0.04871,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":21.0,"n_steps_budget":1000.0,"object_pos_end":[0.50047,0.08114,0.04057],"object_pos_start":[0.49928,0.08457,0.04079],"object_to_goal_dist_end":0.16115,"object_to_goal_dist_start":0.16457,"object_z_max":0.04081,"peak_contact_force":229.46541,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":23.0,"raw_peak_contact_force":247.79009,"subtask_id":"push","tcp_end":[0.50255,0.12777,0.03467],"tcp_start":[0.50258,0.128,0.03468],"tcp_to_object_dist_end":0.04705,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":449.0,"n_steps_budget":1000.0,"object_pos_end":[0.50593,0.05784,0.02414],"object_pos_start":[0.5006,0.08074,0.04054],"object_to_goal_dist_end":0.13887,"object_to_goal_dist_start":0.16074,"object_z_max":0.04054,"peak_contact_force":0.65853,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":459.0,"raw_peak_contact_force":213.23696,"tcp_end":[0.49972,0.12704,0.16498],"tcp_start":[0.50255,0.12777,0.03467],"tcp_to_object_dist_end":0.15704,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```