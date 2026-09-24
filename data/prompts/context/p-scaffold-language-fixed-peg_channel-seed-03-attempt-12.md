## Search State

- **Seed**: 3
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 9 | 0.0037 | 0.24 | ❌ rejected |
| 11 | approach → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 9 | 0.1012 | 0.32 | ❌ rejected |
| 10 | approach → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | 0.3813 | 0.52 | ✅ accepted |
| 9 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.1035 | 0.22 | ❌ rejected |
| 8 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | -0.0530 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.24 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.004) — your mutation base

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

- **Composite score**: 0.004
- **task_score** (E): 0.238
- **fitness_score**: 0.344  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.540

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| prep_1 | 1.00 | 1.00 | 0.1624 |
| approach_1 | 1.00 | 1.00 | 0.1183 |
| contact_1 | 1.00 | 1.00 | 0.0034 |
| push_1 | 0.00 | 1.00 | 0.1473 |
| retract_1 | 1.00 | 1.00 | 0.1303 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| prep_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.505, 0.131, 0.156) | (0.509, 0.081, 0.040)→(0.502, 0.082, 0.034) | 0.165→0.162 | 1.00 / 1.000 | 0.546 | 3.954 |
| approach_1 | approach | 1.00 / step_budget | (0.505, 0.131, 0.156)→(0.496, 0.134, 0.040) | (0.502, 0.082, 0.034)→(0.502, 0.082, 0.034) | 0.162→0.162 | 1.00 / 1.333 | 22.055 | 117.627 |
| contact_1 | contact | 1.00 / force_exceeded | (0.496, 0.134, 0.040)→(0.494, 0.135, 0.037) | (0.502, 0.082, 0.034)→(0.502, 0.082, 0.034) | 0.162→0.162 | 1.00 / 2.000 | 162.349 | 189.192 |
| push_1 | push | 0.00 / step_budget | (0.494, 0.135, 0.037)→(0.502, -0.012, 0.038) | (0.502, 0.082, 0.034)→(0.502, -0.028, 0.032) | 0.162→0.054 | 1.00 / 3.667 | 241.294 | 583.417 |
| retract_1 | retract | 1.00 / step_budget | (0.502, -0.012, 0.038)→(0.499, -0.012, 0.169) | (0.502, -0.028, 0.032)→(0.506, -0.027, 0.031) | 0.054→0.055 | 1.00 / 1.000 | 0.609 | 128.365 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.705
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.148
- phase_score: 0.695
- phase_breakdown.approach_score: 0.640
- phase_breakdown.contact_score: 0.475
- phase_breakdown.push_score: 0.786

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.476
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.367
- **Median Q (composite search score)**: -0.040
- **K-run variance**: 0.0091
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.438


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.63131,"average_solve_count":198.0,"average_success_count":198.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.arc_height":0.03001,"approach_1.lateral_offset":-0.00867,"approach_1.speed":0.03845,"contact_1.contact_force":9.94688,"contact_1.speed":0.00641,"prep_1.speed":0.08345,"push_1.push_depth":0.1976,"push_1.speed":0.09883,"retract_1.speed":0.09999},"optimized_scores":{"best_composite_score":0.13613,"best_fitness_score":0.47613,"best_task_score":0.14799},"replay_outcomes":[{"contacts":{"omitted_contact_groups":3,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":586.0,"contact_point_centroid":[0.55499,0.01584,0.05998],"force_p95":211.01859,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":661.98423,"mean_force":127.06727,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49054,0.01544,0.04086]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":116.0,"contact_point_centroid":[0.47494,0.11881,0.05849],"force_p95":342.61602,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":351.75092,"mean_force":245.95843,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48269,0.11948,0.05455]},{"body_a":"channel_base_body","body_b":"link7","contact_count":198.0,"contact_point_centroid":[0.56855,-0.10013,0.06493],"force_p95":297.69564,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":310.20326,"mean_force":250.03778,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49805,-0.06683,0.03964]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":21.0,"contact_point_centroid":[0.47492,0.10798,0.04618],"force_p95":235.65135,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":251.43783,"mean_force":149.47461,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48565,0.10798,0.04097]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":2.0,"contact_point_centroid":[0.47496,0.11052,0.04849],"force_p95":172.26882,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":176.29532,"mean_force":136.0303,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48571,0.11045,0.04323]},{"body_a":"attachment","body_b":"peg","contact_count":838.0,"contact_point_centroid":[0.5009,-0.0155,0.03776],"force_p95":123.08375,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":148.49759,"mean_force":66.10099,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49287,-0.01326,0.04045]},{"body_a":"peg","body_b":"channel_base_body","contact_count":969.0,"contact_point_centroid":[0.50373,-0.01498,0.00786],"force_p95":109.76962,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":143.87192,"mean_force":47.17318,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4922,-0.00236,0.04055]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":546.0,"contact_point_centroid":[0.52589,0.00488,0.02393],"force_p95":85.42639,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":92.63524,"mean_force":46.76252,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49026,0.01641,0.041]},{"body_a":"channel_base_body","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.57112,-0.1001,0.06494],"force_p95":82.60218,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":87.79988,"mean_force":57.30294,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50042,-0.06788,0.03993]},{"body_a":"peg","body_b":"channel_base_body","contact_count":390.0,"contact_point_centroid":[0.50127,-0.05367,0.0082],"force_p95":0.75515,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":80.52228,"mean_force":0.98388,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49773,-0.06767,0.10426]},{"body_a":"attachment","body_b":"peg","contact_count":13.0,"contact_point_centroid":[0.49947,-0.0699,0.04198],"force_p95":54.08028,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":77.42106,"mean_force":15.72278,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50019,-0.06771,0.04099]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":26.0,"contact_point_centroid":[0.4747,-0.05763,0.02649],"force_p95":30.30557,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":38.54556,"mean_force":8.02593,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4998,-0.06764,0.04303]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":127.0,"contact_point_centroid":[0.47479,-0.04825,0.02462],"force_p95":19.17164,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":34.63555,"mean_force":13.97182,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49865,-0.06717,0.0397]},{"body_a":"peg","body_b":"world","contact_count":124.0,"contact_point_centroid":[0.50641,-0.04829,-0.00034],"force_p95":6.609,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.2765,"mean_force":0.76953,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49525,-0.04749,0.03957]},{"body_a":"peg","body_b":"channel_base_body","contact_count":305.0,"contact_point_centroid":[0.49471,0.059,0.00933],"force_p95":0.62867,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.59415,"phase_index":0.0,"phase_name":"prep_1","phase_type":"approach","tcp_position_centroid":[0.48283,0.15277,0.22213]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"prep_1","phase_type":"approach","tcp_position_centroid":[0.49846,0.19673,0.29455]}],"total_contact_groups":19},"final_pose_error":0.01996,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50306,-0.0538,0.02409],"final_tcp_position":[0.49777,-0.06779,0.1701],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":661.98423,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":334.0,"n_steps_budget":1000.0,"object_pos_end":[0.49408,0.05905,0.03385],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13931,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54742,"phase_name":"prep_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":340.0,"raw_peak_contact_force":4.20518,"tcp_end":[0.46852,0.11104,0.15564],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13487,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":424.0,"n_steps_budget":1000.0,"object_pos_end":[0.49417,0.0591,0.03389],"object_pos_start":[0.49408,0.05905,0.03385],"object_to_goal_dist_end":0.13936,"object_to_goal_dist_start":0.13931,"object_z_max":0.03389,"peak_contact_force":65.06642,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":540.0,"raw_peak_contact_force":351.75092,"subtask_id":"approach","tcp_end":[0.48578,0.11022,0.04355],"tcp_start":[0.46852,0.11104,0.15564],"tcp_to_object_dist_end":0.05269,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":4.0,"n_steps_budget":1000.0,"object_pos_end":[0.49399,0.05901,0.03389],"object_pos_start":[0.49417,0.0591,0.03389],"object_to_goal_dist_end":0.13928,"object_to_goal_dist_start":0.13936,"object_z_max":0.03389,"peak_contact_force":95.76528,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":6.0,"raw_peak_contact_force":176.29532,"subtask_id":"contact","tcp_end":[0.48549,0.11101,0.04273],"tcp_start":[0.48578,0.11022,0.04355],"tcp_to_object_dist_end":0.05343,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49242,-0.05395,0.02587],"object_pos_start":[0.49399,0.05901,0.03389],"object_to_goal_dist_end":0.03059,"object_to_goal_dist_start":0.13928,"object_z_max":0.04036,"peak_contact_force":281.48007,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3409.0,"raw_peak_contact_force":661.98423,"subtask_id":"push","tcp_end":[0.50039,-0.06799,0.03988],"tcp_start":[0.48549,0.11101,0.04273],"tcp_to_object_dist_end":0.02138,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":390.0,"n_steps_budget":960.0,"object_pos_end":[0.50306,-0.0538,0.02409],"object_pos_start":[0.49242,-0.05395,0.02587],"object_to_goal_dist_end":0.03081,"object_to_goal_dist_start":0.03059,"object_z_max":0.02678,"peak_contact_force":0.72542,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":439.0,"raw_peak_contact_force":87.79988,"tcp_end":[0.49777,-0.06779,0.1701],"tcp_start":[0.50039,-0.06799,0.03988],"tcp_to_object_dist_end":0.14677,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.95695,"average_solve_count":302.0,"average_success_count":302.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.arc_height":0.03623,"approach_1.lateral_offset":0.00215,"approach_1.speed":0.02235,"contact_1.contact_force":4.56457,"contact_1.speed":0.02618,"prep_1.speed":0.04557,"push_1.push_depth":0.19661,"push_1.speed":0.09123,"retract_1.speed":0.0497},"optimized_scores":{"best_composite_score":-0.08553,"best_fitness_score":0.25447,"best_task_score":0.19922},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":833.0,"contact_point_centroid":[0.55499,0.05611,0.05995],"force_p95":283.47095,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":585.71375,"mean_force":145.40988,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.502,0.05669,0.03717]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":780.0,"contact_point_centroid":[0.52503,0.04784,0.05999],"force_p95":274.61718,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":367.46333,"mean_force":173.93229,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50209,0.04796,0.03721]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.555,0.11535,0.0599],"force_p95":158.19922,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":158.19922,"mean_force":158.19922,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50231,0.13341,0.0352]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.55499,0.00397,0.05997],"force_p95":132.53798,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":145.10536,"mean_force":77.59789,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50199,0.0059,0.03763]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":4.0,"contact_point_centroid":[0.52501,0.00558,0.05999],"force_p95":83.01787,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":91.7093,"mean_force":31.36894,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50199,0.0059,0.03763]},{"body_a":"attachment","body_b":"peg","contact_count":435.0,"contact_point_centroid":[0.50439,0.03668,0.04076],"force_p95":14.89705,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":48.84716,"mean_force":2.79292,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50207,0.04846,0.03723]},{"body_a":"peg","body_b":"channel_base_body","contact_count":842.0,"contact_point_centroid":[0.50347,0.01552,0.0097],"force_p95":6.77444,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":48.49505,"mean_force":1.80831,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50199,0.05657,0.03719]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":303.0,"contact_point_centroid":[0.52521,0.00718,0.02788],"force_p95":1.65572,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.44397,"mean_force":0.63583,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50208,0.03708,0.0373]},{"body_a":"peg","body_b":"channel_base_body","contact_count":310.0,"contact_point_centroid":[0.5055,0.08083,0.00934],"force_p95":0.57836,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.59599,"phase_index":0.0,"phase_name":"prep_1","phase_type":"approach","tcp_position_centroid":[0.51407,0.16333,0.22267]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"prep_1","phase_type":"approach","tcp_position_centroid":[0.50041,0.19768,0.29508]},{"body_a":"attachment","body_b":"peg","contact_count":27.0,"contact_point_centroid":[0.50459,-0.00602,0.05389],"force_p95":1.33957,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.49411,"mean_force":0.53195,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50024,0.00584,0.04805]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":96.0,"contact_point_centroid":[0.52502,-0.02248,0.0591],"force_p95":0.1475,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.14232,"mean_force":0.0681,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49918,0.00579,0.0983]},{"body_a":"peg","body_b":"channel_base_body","contact_count":419.0,"contact_point_centroid":[0.50625,-0.02571,0.00954],"force_p95":0.59399,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.90812,"mean_force":0.5275,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4993,0.00578,0.10145]},{"body_a":"peg","body_b":"channel_base_body","contact_count":344.0,"contact_point_centroid":[0.50594,0.08095,0.00938],"force_p95":0.55007,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55023,"mean_force":0.54677,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51674,0.14828,0.09955]},{"body_a":"peg","body_b":"channel_base_body","contact_count":22.0,"contact_point_centroid":[0.50666,0.07968,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55007,"mean_force":0.54669,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50385,0.13452,0.0374]}],"total_contact_groups":15},"final_pose_error":0.01985,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50696,-0.02221,0.03378],"final_tcp_position":[0.49939,0.00569,0.16792],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":585.71375,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":339.0,"n_steps_budget":1000.0,"object_pos_end":[0.50596,0.08089,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54642,"phase_name":"prep_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":346.0,"raw_peak_contact_force":4.32595,"tcp_end":[0.52811,0.13054,0.15546],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13328,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":344.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.08089,0.03378],"object_pos_start":[0.50596,0.08089,0.03378],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16112,"object_z_max":0.03378,"peak_contact_force":0.55006,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":344.0,"raw_peak_contact_force":0.55023,"subtask_id":"approach","tcp_end":[0.50599,0.13398,0.04002],"tcp_start":[0.52811,0.13054,0.15546],"tcp_to_object_dist_end":0.05346,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":22.0,"n_steps_budget":810.0,"object_pos_end":[0.50596,0.08089,0.03378],"object_pos_start":[0.50599,0.08089,0.03378],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16112,"object_z_max":0.03378,"peak_contact_force":158.19922,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":23.0,"raw_peak_contact_force":158.19922,"subtask_id":"contact","tcp_end":[0.50223,0.13326,0.03509],"tcp_start":[0.50599,0.13398,0.04002],"tcp_to_object_dist_end":0.05252,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5068,-0.02362,0.03607],"object_pos_start":[0.50596,0.08089,0.03378],"object_to_goal_dist_end":0.05693,"object_to_goal_dist_start":0.16112,"object_z_max":0.03789,"peak_contact_force":176.66738,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3193.0,"raw_peak_contact_force":585.71375,"subtask_id":"push","tcp_end":[0.50198,0.00587,0.0376],"tcp_start":[0.50223,0.13326,0.03509],"tcp_to_object_dist_end":0.02991,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":419.0,"n_steps_budget":1000.0,"object_pos_end":[0.50696,-0.02221,0.03378],"object_pos_start":[0.5068,-0.02362,0.03607],"object_to_goal_dist_end":0.05854,"object_to_goal_dist_start":0.05693,"object_z_max":0.03615,"peak_contact_force":0.55307,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":550.0,"raw_peak_contact_force":145.10536,"tcp_end":[0.49939,0.00569,0.16792],"tcp_start":[0.50198,0.00587,0.0376],"tcp_to_object_dist_end":0.13722,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.19173,"average_solve_count":266.0,"average_success_count":266.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.arc_height":0.07793,"approach_1.lateral_offset":-0.00683,"approach_1.speed":0.04272,"contact_1.contact_force":8.0988,"contact_1.speed":0.02811,"prep_1.speed":0.03528,"push_1.push_depth":0.12909,"push_1.speed":0.07258,"retract_1.speed":0.05848},"optimized_scores":{"best_composite_score":-0.03956,"best_fitness_score":0.30044,"best_task_score":0.36679},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":866.0,"contact_point_centroid":[0.55496,0.07462,0.05995],"force_p95":364.75045,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":502.55296,"mean_force":167.506,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50056,0.07725,0.03723]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":517.0,"contact_point_centroid":[0.52504,0.05066,0.05998],"force_p95":316.18447,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":379.92797,"mean_force":165.64865,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50212,0.05074,0.03722]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.55215,0.12,0.05982],"force_p95":233.08261,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":233.08261,"mean_force":233.08261,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49472,0.16032,0.0343]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.555,0.02843,0.05998],"force_p95":142.68154,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":152.18955,"mean_force":86.96004,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50214,0.02578,0.03759]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":5.0,"contact_point_centroid":[0.52507,0.02563,0.05997],"force_p95":95.06782,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":108.91747,"mean_force":29.71734,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50212,0.02579,0.03762]},{"body_a":"attachment","body_b":"peg","contact_count":412.0,"contact_point_centroid":[0.50464,0.05586,0.04147],"force_p95":12.46756,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":51.33208,"mean_force":2.94246,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50139,0.06755,0.03732]},{"body_a":"peg","body_b":"channel_base_body","contact_count":801.0,"contact_point_centroid":[0.50384,0.03534,0.00968],"force_p95":8.60291,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":47.3101,"mean_force":1.87253,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50037,0.07813,0.03723]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":300.0,"contact_point_centroid":[0.52514,0.02613,0.03091],"force_p95":2.26199,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":26.88138,"mean_force":0.75484,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50185,0.05649,0.03726]},{"body_a":"peg","body_b":"channel_base_body","contact_count":286.0,"contact_point_centroid":[0.50548,0.10474,0.00936],"force_p95":0.60679,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.58587,"phase_index":0.0,"phase_name":"prep_1","phase_type":"approach","tcp_position_centroid":[0.50886,0.17465,0.22449]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"prep_1","phase_type":"approach","tcp_position_centroid":[0.50004,0.19856,0.2961]},{"body_a":"peg","body_b":"channel_base_body","contact_count":418.0,"contact_point_centroid":[0.50675,-0.00524,0.00939],"force_p95":0.58154,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.66019,"mean_force":0.54708,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49941,0.02557,0.1015]},{"body_a":"peg","body_b":"channel_base_body","contact_count":400.0,"contact_point_centroid":[0.50577,0.10464,0.00939],"force_p95":0.57552,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57941,"mean_force":0.54638,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50706,0.17911,0.09957]},{"body_a":"peg","body_b":"channel_base_body","contact_count":8.0,"contact_point_centroid":[0.50815,0.09688,0.00939],"force_p95":0.55214,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55233,"mean_force":0.54522,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49553,0.15976,0.03515]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":6.0,"contact_point_centroid":[0.52502,-0.00501,0.05887],"force_p95":0.09899,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.10949,"mean_force":0.04686,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50089,0.02564,0.0411]}],"total_contact_groups":14},"final_pose_error":0.01995,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50685,-0.0053,0.0338],"final_tcp_position":[0.49952,0.02549,0.16781],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":502.55296,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":313.0,"n_steps_budget":1000.0,"object_pos_end":[0.50596,0.10457,0.03383],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18477,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.5445,"phase_name":"prep_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":318.0,"raw_peak_contact_force":3.33087,"tcp_end":[0.51827,0.15176,0.1576],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13303,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":400.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.10468,0.03384],"object_pos_start":[0.50596,0.10457,0.03383],"object_to_goal_dist_end":0.18488,"object_to_goal_dist_start":0.18477,"object_z_max":0.03384,"peak_contact_force":0.54982,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":400.0,"raw_peak_contact_force":0.57941,"subtask_id":"approach","tcp_end":[0.49625,0.15911,0.03599],"tcp_start":[0.51827,0.15176,0.1576],"tcp_to_object_dist_end":0.05534,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":8.0,"n_steps_budget":810.0,"object_pos_end":[0.50583,0.10467,0.03384],"object_pos_start":[0.50599,0.10468,0.03384],"object_to_goal_dist_end":0.18486,"object_to_goal_dist_start":0.18488,"object_z_max":0.03384,"peak_contact_force":233.08261,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":9.0,"raw_peak_contact_force":233.08261,"subtask_id":"contact","tcp_end":[0.49453,0.16034,0.03412],"tcp_start":[0.49625,0.15911,0.03599],"tcp_to_object_dist_end":0.05681,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50682,-0.0055,0.03412],"object_pos_start":[0.50583,0.10467,0.03384],"object_to_goal_dist_end":0.07504,"object_to_goal_dist_start":0.18486,"object_z_max":0.04132,"peak_contact_force":265.73429,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2896.0,"raw_peak_contact_force":502.55296,"subtask_id":"push","tcp_end":[0.50215,0.02575,0.03758],"tcp_start":[0.49453,0.16034,0.03412],"tcp_to_object_dist_end":0.03179,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":418.0,"n_steps_budget":1000.0,"object_pos_end":[0.50685,-0.0053,0.0338],"object_pos_start":[0.50682,-0.0055,0.03412],"object_to_goal_dist_end":0.07527,"object_to_goal_dist_start":0.07504,"object_z_max":0.03412,"peak_contact_force":0.54859,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":432.0,"raw_peak_contact_force":152.18955,"tcp_end":[0.49952,0.02549,0.16781],"tcp_start":[0.50215,0.02575,0.03758],"tcp_to_object_dist_end":0.1377,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```