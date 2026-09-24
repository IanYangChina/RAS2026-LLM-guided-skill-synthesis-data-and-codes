## Search State

- **Seed**: 3
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 9 | 0.1012 | 0.32 | ❌ rejected |
| 10 | approach → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | 0.3813 | 0.52 | ✅ accepted |
| 9 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.1035 | 0.22 | ❌ rejected |
| 8 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | -0.0530 | 0.00 | ❌ rejected |
| 7 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.1535 | 0.27 | ❌ rejected |

**Proposal policy**: task_score is 0.32 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.101) — your mutation base

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

- **Composite score**: 0.101
- **task_score** (E): 0.319
- **fitness_score**: 0.441  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.540

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| prep_1 | 1.00 | 1.00 | 0.1623 |
| approach_1 | 1.00 | 1.00 | 0.1104 |
| contact_1 | 1.00 | 1.00 | 0.0118 |
| push_1 | 1.00 | 1.00 | 0.1587 |
| retract_1 | 1.00 | 1.00 | 0.1304 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| prep_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.505, 0.131, 0.156) | (0.509, 0.081, 0.040)→(0.502, 0.081, 0.034) | 0.165→0.162 | 1.00 / 1.000 | 0.547 | 3.954 |
| approach_1 | approach | 1.00 / step_budget | (0.505, 0.131, 0.156)→(0.497, 0.122, 0.048) | (0.502, 0.081, 0.034)→(0.502, 0.081, 0.034) | 0.162→0.162 | 1.00 / 1.000 | 0.554 | 128.865 |
| contact_1 | contact | 1.00 / force_exceeded | (0.497, 0.122, 0.048)→(0.495, 0.115, 0.039) | (0.502, 0.081, 0.034)→(0.502, 0.081, 0.034) | 0.162→0.162 | 1.00 / 2.333 | 22.069 | 10.257 |
| push_1 | push | 1.00 / step_budget | (0.495, 0.115, 0.039)→(0.496, -0.044, 0.039) | (0.502, 0.081, 0.034)→(0.505, -0.058, 0.033) | 0.162→0.024 | 1.00 / 3.333 | 75.063 | 446.469 |
| retract_1 | retract | 1.00 / step_budget | (0.496, -0.044, 0.039)→(0.494, -0.044, 0.170) | (0.505, -0.058, 0.033)→(0.501, -0.057, 0.031) | 0.024→0.026 | 1.00 / 1.000 | 0.610 | 141.866 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.666
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.214
- phase_score: 0.635
- phase_breakdown.approach_score: 0.653
- phase_breakdown.contact_score: 0.567
- phase_breakdown.push_score: 0.652

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.467
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.502
- **Median Q (composite search score)**: 0.108
- **K-run variance**: 0.0006
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.401


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.4322,"average_solve_count":236.0,"average_success_count":236.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.lateral_offset":-0.0025,"approach_1.speed":0.03086,"contact_1.contact_force":4.82243,"contact_1.speed":0.03464,"prep_1.speed":0.06386,"push_1.lateral_correction":0.00415,"push_1.push_depth":0.17937,"push_1.speed":0.08806,"retract_1.speed":0.06991},"optimized_scores":{"best_composite_score":0.12664,"best_fitness_score":0.46664,"best_task_score":0.21396},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":47.0,"contact_point_centroid":[0.4749,0.1058,0.0598],"force_p95":349.80388,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":385.46471,"mean_force":298.36895,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48453,0.10105,0.0548]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":11.0,"contact_point_centroid":[0.555,0.0734,0.05999],"force_p95":246.37483,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":266.96777,"mean_force":163.82547,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48581,0.08612,0.043]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47498,-0.06442,0.05321],"force_p95":250.52283,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":254.40776,"mean_force":169.10721,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4858,-0.06443,0.04807]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":612.0,"contact_point_centroid":[0.47499,0.00701,0.04909],"force_p95":110.53583,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":247.39084,"mean_force":78.75145,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4858,0.00702,0.04391]},{"body_a":"attachment","body_b":"peg","contact_count":746.0,"contact_point_centroid":[0.49471,-0.00039,0.04001],"force_p95":55.52807,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":65.41927,"mean_force":31.73034,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48581,0.00339,0.04398]},{"body_a":"attachment","body_b":"peg","contact_count":18.0,"contact_point_centroid":[0.49611,-0.06454,0.03996],"force_p95":50.52019,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":65.41177,"mean_force":27.1864,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48582,-0.06466,0.04458]},{"body_a":"peg","body_b":"channel_base_body","contact_count":839.0,"contact_point_centroid":[0.50333,-0.00657,0.0092],"force_p95":49.35762,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":58.94499,"mean_force":24.87591,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48581,0.01073,0.0439]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.52544,-0.05295,0.02764],"force_p95":41.93673,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":47.34414,"mean_force":13.71613,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48583,-0.06449,0.04718]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":426.0,"contact_point_centroid":[0.52534,-0.04355,0.0256],"force_p95":37.83965,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":45.5548,"mean_force":23.75646,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48581,-0.03003,0.04382]},{"body_a":"peg","body_b":"channel_base_body","contact_count":402.0,"contact_point_centroid":[0.49699,-0.04806,0.00842],"force_p95":8.94547,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":43.77128,"mean_force":1.90069,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48352,-0.06409,0.10756]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":1.0,"contact_point_centroid":[0.475,0.09968,0.05092],"force_p95":15.16572,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":15.16572,"mean_force":15.16572,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48568,0.09959,0.04547]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":60.0,"contact_point_centroid":[0.4749,-0.04932,0.02547],"force_p95":10.38592,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.53994,"mean_force":5.3219,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48286,-0.06405,0.10785]},{"body_a":"peg","body_b":"channel_base_body","contact_count":313.0,"contact_point_centroid":[0.49447,0.05889,0.00933],"force_p95":0.62041,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.59291,"phase_index":0.0,"phase_name":"prep_1","phase_type":"approach","tcp_position_centroid":[0.48286,0.15294,0.22239]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"prep_1","phase_type":"approach","tcp_position_centroid":[0.49854,0.19697,0.29495]},{"body_a":"peg","body_b":"channel_base_body","contact_count":342.0,"contact_point_centroid":[0.49409,0.05895,0.00939],"force_p95":0.5504,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55326,"mean_force":0.54621,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4765,0.1049,0.09624]},{"body_a":"peg","body_b":"channel_base_body","contact_count":12.0,"contact_point_centroid":[0.49639,0.06509,0.00939],"force_p95":0.5495,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54951,"mean_force":0.54581,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48609,0.10004,0.04635]}],"total_contact_groups":17},"final_pose_error":0.01981,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49455,-0.04756,0.02412],"final_tcp_position":[0.48321,-0.06417,0.17397],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":385.46471,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":342.0,"n_steps_budget":1000.0,"object_pos_end":[0.4942,0.0589,0.03385],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13915,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54255,"phase_name":"prep_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":348.0,"raw_peak_contact_force":4.20518,"tcp_end":[0.46849,0.111,0.15559],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.1349,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":342.0,"n_steps_budget":1000.0,"object_pos_end":[0.49422,0.05885,0.03389],"object_pos_start":[0.4942,0.0589,0.03385],"object_to_goal_dist_end":0.13911,"object_to_goal_dist_start":0.13915,"object_z_max":0.03389,"peak_contact_force":0.54136,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":389.0,"raw_peak_contact_force":385.46471,"subtask_id":"approach","tcp_end":[0.4867,0.10043,0.04754],"tcp_start":[0.46849,0.111,0.15559],"tcp_to_object_dist_end":0.0444,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":12.0,"n_steps_budget":600.0,"object_pos_end":[0.494,0.05889,0.03389],"object_pos_start":[0.49422,0.05885,0.03389],"object_to_goal_dist_end":0.13916,"object_to_goal_dist_start":0.13911,"object_z_max":0.03389,"peak_contact_force":15.16572,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":13.0,"raw_peak_contact_force":15.16572,"subtask_id":"contact","tcp_end":[0.48566,0.0995,0.04535],"tcp_start":[0.4867,0.10043,0.04754],"tcp_to_object_dist_end":0.04301,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":848.0,"n_steps_budget":1000.0,"object_pos_end":[0.50792,-0.04762,0.02777],"object_pos_start":[0.494,0.05889,0.03389],"object_to_goal_dist_end":0.0355,"object_to_goal_dist_start":0.13916,"object_z_max":0.04046,"peak_contact_force":37.6511,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2637.0,"raw_peak_contact_force":266.96777,"subtask_id":"push","tcp_end":[0.48581,-0.06439,0.04361],"tcp_start":[0.48566,0.0995,0.04535],"tcp_to_object_dist_end":0.03195,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":402.0,"n_steps_budget":1000.0,"object_pos_end":[0.49455,-0.04756,0.02412],"object_pos_start":[0.50792,-0.04762,0.02777],"object_to_goal_dist_end":0.03652,"object_to_goal_dist_start":0.0355,"object_z_max":0.02783,"peak_contact_force":0.73805,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":544.0,"raw_peak_contact_force":254.40776,"tcp_end":[0.48321,-0.06417,0.17397],"tcp_start":[0.48581,-0.06439,0.04361],"tcp_to_object_dist_end":0.15119,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.07914,"average_solve_count":278.0,"average_success_count":278.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.lateral_offset":-0.00578,"approach_1.speed":0.02704,"contact_1.contact_force":14.93018,"contact_1.speed":0.02589,"prep_1.speed":0.08761,"push_1.lateral_correction":0.01106,"push_1.push_depth":0.17747,"push_1.speed":0.09839,"retract_1.speed":0.03404},"optimized_scores":{"best_composite_score":0.06859,"best_fitness_score":0.40859,"best_task_score":0.24037},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":786.0,"contact_point_centroid":[0.55472,0.02598,0.05997],"force_p95":288.16346,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":530.5458,"mean_force":127.41038,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50047,0.02639,0.03736]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.555,-0.04875,0.05999],"force_p95":77.66567,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":81.29183,"mean_force":53.97426,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50205,-0.05009,0.03704]},{"body_a":"attachment","body_b":"peg","contact_count":373.0,"contact_point_centroid":[0.50317,0.02026,0.04258],"force_p95":24.8108,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":55.12646,"mean_force":4.98741,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50031,0.03192,0.03746]},{"body_a":"peg","body_b":"channel_base_body","contact_count":668.0,"contact_point_centroid":[0.5022,-0.01925,0.0096],"force_p95":18.9695,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":50.24166,"mean_force":3.10018,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50063,0.02241,0.0373]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":234.0,"contact_point_centroid":[0.52521,0.02649,0.0313],"force_p95":8.25973,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":32.37028,"mean_force":1.52165,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49935,0.05638,0.03783]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":82.0,"contact_point_centroid":[0.47465,-0.067,0.03501],"force_p95":2.03838,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.22738,"mean_force":0.80565,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50184,-0.03754,0.03705]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54392,0.11182,0.05999],"force_p95":11.76259,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":11.76259,"mean_force":11.76259,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49933,0.11049,0.03616]},{"body_a":"peg","body_b":"channel_base_body","contact_count":192.0,"contact_point_centroid":[0.50592,0.08021,0.00938],"force_p95":0.55007,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.22133,"mean_force":0.58891,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49907,0.11503,0.04017]},{"body_a":"peg","body_b":"channel_base_body","contact_count":31.0,"contact_point_centroid":[0.49832,-0.10061,0.03267],"force_p95":0.68006,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.20457,"mean_force":0.43837,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50092,-0.05012,0.0403]},{"body_a":"attachment","body_b":"peg","contact_count":27.0,"contact_point_centroid":[0.50118,-0.06174,0.05081],"force_p95":0.72018,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.76696,"mean_force":0.50732,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50007,-0.05,0.04704]},{"body_a":"attachment","body_b":"peg","contact_count":5.0,"contact_point_centroid":[0.5057,0.0988,0.04993],"force_p95":4.45376,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.76461,"mean_force":1.75556,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49929,0.11068,0.0363]},{"body_a":"peg","body_b":"channel_base_body","contact_count":293.0,"contact_point_centroid":[0.50542,0.08086,0.00934],"force_p95":0.58945,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.59884,"phase_index":0.0,"phase_name":"prep_1","phase_type":"approach","tcp_position_centroid":[0.51424,0.16309,0.22217]},{"body_a":"peg","body_b":"channel_base_body","contact_count":2.0,"contact_point_centroid":[0.49965,-0.1004,0.01462],"force_p95":3.6981,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.72579,"mean_force":3.44891,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50202,-0.04988,0.037]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"prep_1","phase_type":"approach","tcp_position_centroid":[0.50064,0.19729,0.29424]},{"body_a":"peg","body_b":"channel_base_body","contact_count":411.0,"contact_point_centroid":[0.50127,-0.07942,0.00949],"force_p95":0.64332,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.00858,"mean_force":0.53879,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49909,-0.04981,0.10397]},{"body_a":"peg","body_b":"channel_base_body","contact_count":272.0,"contact_point_centroid":[0.50604,0.08097,0.00938],"force_p95":0.55008,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55023,"mean_force":0.54677,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5143,0.12598,0.10306]}],"total_contact_groups":16},"final_pose_error":0.01987,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50216,-0.0773,0.03427],"final_tcp_position":[0.49933,-0.04987,0.16734],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":530.5458,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":322.0,"n_steps_budget":1000.0,"object_pos_end":[0.50598,0.0809,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16113,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54522,"phase_name":"prep_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":329.0,"raw_peak_contact_force":4.32595,"tcp_end":[0.5281,0.13066,0.1557],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13353,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":272.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.08087,0.03378],"object_pos_start":[0.50598,0.0809,0.03378],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.16113,"object_z_max":0.03378,"peak_contact_force":0.54459,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":272.0,"raw_peak_contact_force":0.55023,"subtask_id":"approach","tcp_end":[0.50101,0.1216,0.04843],"tcp_start":[0.5281,0.13066,0.1557],"tcp_to_object_dist_end":0.04357,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":192.0,"n_steps_budget":630.0,"object_pos_end":[0.50594,0.08068,0.03399],"object_pos_start":[0.50599,0.08087,0.03378],"object_to_goal_dist_end":0.16091,"object_to_goal_dist_start":0.1611,"object_z_max":0.03397,"peak_contact_force":47.20003,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":198.0,"raw_peak_contact_force":11.76259,"subtask_id":"contact","tcp_end":[0.49934,0.11046,0.03614],"tcp_start":[0.50101,0.1216,0.04843],"tcp_to_object_dist_end":0.03058,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":942.0,"n_steps_budget":1000.0,"object_pos_end":[0.49889,-0.08034,0.0375],"object_pos_start":[0.50594,0.08068,0.03399],"object_to_goal_dist_end":0.00276,"object_to_goal_dist_start":0.16091,"object_z_max":0.03793,"peak_contact_force":112.01228,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2145.0,"raw_peak_contact_force":530.5458,"subtask_id":"push","tcp_end":[0.50205,-0.05001,0.03702],"tcp_start":[0.49934,0.11046,0.03614],"tcp_to_object_dist_end":0.0305,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":434.0,"n_steps_budget":1000.0,"object_pos_end":[0.50216,-0.0773,0.03427],"object_pos_start":[0.49889,-0.08034,0.0375],"object_to_goal_dist_end":0.0067,"object_to_goal_dist_start":0.00276,"object_z_max":0.03823,"peak_contact_force":0.54524,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":472.0,"raw_peak_contact_force":81.29183,"tcp_end":[0.49933,-0.04987,0.16734],"tcp_start":[0.50205,-0.05001,0.03702],"tcp_to_object_dist_end":0.1359,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.0,"average_solve_count":244.0,"average_success_count":244.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.lateral_offset":-0.00233,"approach_1.speed":0.05208,"contact_1.contact_force":2.05108,"contact_1.speed":0.00568,"prep_1.speed":0.06654,"push_1.lateral_correction":0.00371,"push_1.push_depth":0.16669,"push_1.speed":0.0683,"retract_1.speed":0.06916},"optimized_scores":{"best_composite_score":0.10831,"best_fitness_score":0.44831,"best_task_score":0.50225},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":782.0,"contact_point_centroid":[0.5549,0.0525,0.05997],"force_p95":408.76216,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":541.89378,"mean_force":119.9529,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49941,0.05418,0.03719]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.555,-0.01613,0.05998],"force_p95":86.19116,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":89.89701,"mean_force":64.51846,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.501,-0.01743,0.03685]},{"body_a":"peg","body_b":"channel_base_body","contact_count":698.0,"contact_point_centroid":[0.5055,0.00916,0.00974],"force_p95":24.37153,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":46.58588,"mean_force":4.31925,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49941,0.05309,0.03716]},{"body_a":"attachment","body_b":"peg","contact_count":522.0,"contact_point_centroid":[0.50419,0.04379,0.04357],"force_p95":26.30989,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":43.6521,"mean_force":5.37035,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49963,0.05546,0.03723]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":366.0,"contact_point_centroid":[0.52511,0.02119,0.02991],"force_p95":4.67908,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":31.94073,"mean_force":1.2963,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4996,0.05052,0.0373]},{"body_a":"peg","body_b":"channel_base_body","contact_count":456.0,"contact_point_centroid":[0.50594,0.10444,0.00939],"force_p95":0.57569,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.84263,"mean_force":0.55359,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49968,0.13716,0.03904]},{"body_a":"attachment","body_b":"peg","contact_count":15.0,"contact_point_centroid":[0.50574,0.12267,0.05003],"force_p95":1.16478,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.43443,"mean_force":0.27882,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49978,0.13458,0.03676]},{"body_a":"peg","body_b":"channel_base_body","contact_count":277.0,"contact_point_centroid":[0.50542,0.10452,0.00936],"force_p95":0.60989,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.58718,"phase_index":0.0,"phase_name":"prep_1","phase_type":"approach","tcp_position_centroid":[0.50901,0.17438,0.22368]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":14.0,"contact_point_centroid":[0.52502,-0.04719,0.05999],"force_p95":2.6041,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.69078,"mean_force":0.45614,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49916,-0.01745,0.04889]},{"body_a":"attachment","body_b":"peg","contact_count":26.0,"contact_point_centroid":[0.50411,-0.02921,0.05723],"force_p95":2.02939,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.59558,"mean_force":0.5762,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49897,-0.0175,0.04989]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"prep_1","phase_type":"approach","tcp_position_centroid":[0.50022,0.19828,0.2952]},{"body_a":"peg","body_b":"channel_base_body","contact_count":408.0,"contact_point_centroid":[0.50697,-0.04944,0.00952],"force_p95":0.57094,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62761,"mean_force":0.51985,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49827,-0.01732,0.10099]},{"body_a":"peg","body_b":"channel_base_body","contact_count":265.0,"contact_point_centroid":[0.50572,0.10483,0.00939],"force_p95":0.57515,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57941,"mean_force":0.54635,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50965,0.14802,0.10356]}],"total_contact_groups":13},"final_pose_error":0.01976,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50686,-0.0458,0.03381],"final_tcp_position":[0.49835,-0.01732,0.16727],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":541.89378,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":304.0,"n_steps_budget":1000.0,"object_pos_end":[0.50583,0.10464,0.03383],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18483,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.55296,"phase_name":"prep_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":309.0,"raw_peak_contact_force":3.33087,"tcp_end":[0.5183,0.15175,0.15754],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13296,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":265.0,"n_steps_budget":1000.0,"object_pos_end":[0.50597,0.10471,0.03384],"object_pos_start":[0.50583,0.10464,0.03383],"object_to_goal_dist_end":0.18491,"object_to_goal_dist_start":0.18483,"object_z_max":0.03384,"peak_contact_force":0.57562,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":265.0,"raw_peak_contact_force":0.57941,"subtask_id":"approach","tcp_end":[0.50224,0.14478,0.04877],"tcp_start":[0.5183,0.15175,0.15754],"tcp_to_object_dist_end":0.04293,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":456.0,"n_steps_budget":1000.0,"object_pos_end":[0.50589,0.10461,0.03387],"object_pos_start":[0.50597,0.10471,0.03384],"object_to_goal_dist_end":0.1848,"object_to_goal_dist_start":0.18491,"object_z_max":0.03386,"peak_contact_force":3.84263,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":471.0,"raw_peak_contact_force":3.84263,"subtask_id":"contact","tcp_end":[0.4998,0.1345,0.03669],"tcp_start":[0.50224,0.14478,0.04877],"tcp_to_object_dist_end":0.03064,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":972.0,"n_steps_budget":1000.0,"object_pos_end":[0.50695,-0.04685,0.03499],"object_pos_start":[0.50589,0.10461,0.03387],"object_to_goal_dist_end":0.03424,"object_to_goal_dist_start":0.1848,"object_z_max":0.03827,"peak_contact_force":75.52544,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2368.0,"raw_peak_contact_force":541.89378,"subtask_id":"push","tcp_end":[0.50102,-0.0173,0.03685],"tcp_start":[0.4998,0.1345,0.03669],"tcp_to_object_dist_end":0.03019,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":408.0,"n_steps_budget":1000.0,"object_pos_end":[0.50686,-0.0458,0.03381],"object_pos_start":[0.50695,-0.04685,0.03499],"object_to_goal_dist_end":0.03542,"object_to_goal_dist_start":0.03424,"object_z_max":0.03555,"peak_contact_force":0.54596,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":452.0,"raw_peak_contact_force":89.89701,"tcp_end":[0.49835,-0.01732,0.16727],"tcp_start":[0.50102,-0.0173,0.03685],"tcp_to_object_dist_end":0.13673,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```