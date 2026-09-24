## Search State

- **Seed**: 3
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 9 | -0.1706 | 0.04 | ❌ rejected |
| 13 | approach → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | -0.1634 | 0.08 | ❌ rejected |
| 12 | approach → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 9 | 0.0037 | 0.24 | ❌ rejected |
| 11 | approach → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 9 | 0.1012 | 0.32 | ❌ rejected |
| 10 | approach → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | 0.3813 | 0.52 | ✅ accepted |

**Proposal policy**: task_score is 0.04 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.171) — your mutation base

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

- **Composite score**: -0.171
- **task_score** (E): 0.044
- **fitness_score**: 0.169  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.540

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| prep_1 | 1.00 | 1.00 | 0.1240 |
| approach_1 | 1.00 | 1.00 | 0.1589 |
| contact_1 | 1.00 | 1.00 | 0.0137 |
| push_1 | 0.00 | 1.00 | 0.0007 |
| retract_1 | 1.00 | 1.00 | 0.1304 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| prep_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.505, 0.133, 0.205) | (0.509, 0.081, 0.040)→(0.502, 0.081, 0.034) | 0.165→0.162 | 1.00 / 1.000 | 0.552 | 3.954 |
| approach_1 | approach | 1.00 / step_budget | (0.505, 0.133, 0.205)→(0.500, 0.122, 0.048) | (0.502, 0.081, 0.034)→(0.502, 0.081, 0.034) | 0.162→0.162 | 1.00 / 1.000 | 0.546 | 117.578 |
| contact_1 | contact | 1.00 / force_exceeded | (0.500, 0.122, 0.048)→(0.497, 0.113, 0.038) | (0.502, 0.081, 0.034)→(0.502, 0.081, 0.034) | 0.162→0.161 | 1.00 / 2.667 | 39.266 | 13.314 |
| push_1 | push | 0.00 / guard_failure | (0.499, 0.109, 0.036)→(0.499, 0.109, 0.036) | (0.502, 0.081, 0.034)→(0.502, 0.080, 0.034) | 0.161→0.160 | 1.00 / 2.333 | 1622.080 | 727.062 |
| retract_1 | retract | 1.00 / step_budget | (0.499, 0.109, 0.036)→(0.496, 0.108, 0.166) | (0.502, 0.079, 0.035)→(0.505, 0.060, 0.031) | 0.159→0.141 | 1.00 / 1.000 | 0.561 | 190.206 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.319
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.072
- phase_score: 0.270
- phase_breakdown.approach_score: 0.650
- phase_breakdown.contact_score: 0.587
- phase_breakdown.push_score: 0.037

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.191
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.072
- **Median Q (composite search score)**: -0.160
- **K-run variance**: 0.0005
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.328


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.12195,"average_solve_count":246.0,"average_success_count":246.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.lateral_offset":-0.00148,"approach_1.speed":0.05524,"contact_1.contact_force":12.10117,"contact_1.speed":0.02796,"prep_1.arc_height":0.07441,"prep_1.speed":0.02614,"push_1.push_depth":0.15816,"push_1.speed":0.05369,"retract_1.speed":0.06304},"optimized_scores":{"best_composite_score":-0.1495,"best_fitness_score":0.1905,"best_task_score":0.07179},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.53797,0.08869,0.05945],"force_p95":975.45921,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":975.45921,"mean_force":975.45921,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49258,0.08567,0.0368]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":21.0,"contact_point_centroid":[0.53692,0.09744,0.05869],"force_p95":343.53106,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":436.20809,"mean_force":95.33737,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49369,0.08307,0.03568]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":10.0,"contact_point_centroid":[0.47483,0.10126,0.05954],"force_p95":347.68274,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":351.60464,"mean_force":203.22944,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48487,0.09825,0.05451]},{"body_a":"peg","body_b":"channel_base_body","contact_count":12.0,"contact_point_centroid":[0.50179,0.06625,0.00936],"force_p95":44.53176,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":88.37023,"mean_force":9.01707,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48931,0.09187,0.04162]},{"body_a":"attachment","body_b":"peg","contact_count":4.0,"contact_point_centroid":[0.49292,0.07571,0.03893],"force_p95":74.84302,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":85.35588,"mean_force":28.10869,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49199,0.08722,0.03851]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":1.0,"contact_point_centroid":[0.47498,0.09716,0.04983],"force_p95":21.91812,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":21.91812,"mean_force":21.91812,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48575,0.09709,0.04458]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":1.0,"contact_point_centroid":[0.47499,0.09725,0.04993],"force_p95":14.00783,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":14.00783,"mean_force":14.00783,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48577,0.09718,0.04468]},{"body_a":"peg","body_b":"channel_base_body","contact_count":422.0,"contact_point_centroid":[0.49854,0.02082,0.00906],"force_p95":0.87721,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.99707,"mean_force":0.61315,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49035,0.08397,0.09925]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":16.0,"contact_point_centroid":[0.47494,0.03157,0.03086],"force_p95":6.81248,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.36778,"mean_force":1.62801,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49067,0.08389,0.10108]},{"body_a":"peg","body_b":"channel_base_body","contact_count":416.0,"contact_point_centroid":[0.49442,0.05887,0.00934],"force_p95":0.59572,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.58138,"phase_index":0.0,"phase_name":"prep_1","phase_type":"approach","tcp_position_centroid":[0.47152,0.12531,0.2796]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"prep_1","phase_type":"approach","tcp_position_centroid":[0.4979,0.19613,0.30099]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":6.0,"contact_point_centroid":[0.52505,0.00728,0.05055],"force_p95":0.67218,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.70146,"mean_force":0.51181,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48977,0.08409,0.09127]},{"body_a":"peg","body_b":"channel_base_body","contact_count":434.0,"contact_point_centroid":[0.4941,0.05894,0.00939],"force_p95":0.55038,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55382,"mean_force":0.54609,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47232,0.09793,0.12553]},{"body_a":"peg","body_b":"channel_base_body","contact_count":18.0,"contact_point_centroid":[0.49356,0.05924,0.00939],"force_p95":0.54912,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5493,"mean_force":0.54554,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48619,0.0979,0.04588]},{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.49379,0.07286,0.03659],"force_p95":0.0,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49325,0.08446,0.03562]}],"total_contact_groups":15},"final_pose_error":0.01976,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50166,0.00795,0.02413],"final_tcp_position":[0.49026,0.08426,0.16639],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":975.45921,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":445.0,"n_steps_budget":1000.0,"object_pos_end":[0.49424,0.05894,0.03386],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.1392,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.55186,"phase_name":"prep_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":451.0,"raw_peak_contact_force":4.20518,"tcp_end":[0.46097,0.09793,0.20506],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.17871,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":434.0,"n_steps_budget":1000.0,"object_pos_end":[0.49429,0.0589,0.03391],"object_pos_start":[0.49424,0.05894,0.03386],"object_to_goal_dist_end":0.13916,"object_to_goal_dist_start":0.1392,"object_z_max":0.03391,"peak_contact_force":0.549,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":444.0,"raw_peak_contact_force":351.60464,"subtask_id":"approach","tcp_end":[0.48701,0.09845,0.04753],"tcp_start":[0.46097,0.09793,0.20506],"tcp_to_object_dist_end":0.04246,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":18.0,"n_steps_budget":600.0,"object_pos_end":[0.49427,0.05887,0.03391],"object_pos_start":[0.49429,0.0589,0.03391],"object_to_goal_dist_end":0.13912,"object_to_goal_dist_start":0.13916,"object_z_max":0.03391,"peak_contact_force":14.00783,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":19.0,"raw_peak_contact_force":14.00783,"subtask_id":"contact","tcp_end":[0.48575,0.09709,0.04458],"tcp_start":[0.48701,0.09845,0.04753],"tcp_to_object_dist_end":0.04058,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":12.0,"n_steps_budget":1000.0,"object_pos_end":[0.49406,0.05801,0.03388],"object_pos_start":[0.49427,0.05887,0.03391],"object_to_goal_dist_end":0.13827,"object_to_goal_dist_start":0.13912,"object_z_max":0.03391,"peak_contact_force":975.45921,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":18.0,"raw_peak_contact_force":975.45921,"subtask_id":"push","tcp_end":[0.49306,0.08481,0.03594],"tcp_start":[0.49258,0.08567,0.0368],"tcp_to_object_dist_end":0.0269,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":430.0,"n_steps_budget":1000.0,"object_pos_end":[0.50166,0.00795,0.02413],"object_pos_start":[0.49393,0.05574,0.03378],"object_to_goal_dist_end":0.08939,"object_to_goal_dist_start":0.13602,"object_z_max":0.04078,"peak_contact_force":0.60163,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":467.0,"raw_peak_contact_force":436.20809,"tcp_end":[0.49026,0.08426,0.16639],"tcp_start":[0.49306,0.08481,0.03594],"tcp_to_object_dist_end":0.16183,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.14692,"average_solve_count":211.0,"average_success_count":211.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.lateral_offset":-0.0018,"approach_1.speed":0.04393,"contact_1.contact_force":9.73775,"contact_1.speed":0.02139,"prep_1.arc_height":0.12262,"prep_1.speed":0.04233,"push_1.push_depth":0.11466,"push_1.speed":0.05333,"retract_1.speed":0.07003},"optimized_scores":{"best_composite_score":-0.20267,"best_fitness_score":0.13733,"best_task_score":0.02064},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.54545,0.11107,0.05999],"force_p95":608.59904,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":608.65474,"mean_force":608.09773,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50092,0.10981,0.03604]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54587,0.11072,0.06],"force_p95":133.66871,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":133.66871,"mean_force":133.66871,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50128,0.10921,0.03618]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":4.0,"contact_point_centroid":[0.52512,0.10965,0.05994],"force_p95":93.4415,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":106.93329,"mean_force":35.04594,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50128,0.10922,0.03632]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.50555,0.09782,0.04549],"force_p95":48.00651,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":53.25484,"mean_force":18.25707,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50094,0.10974,0.03608]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.50694,0.06229,0.00989],"force_p95":47.2894,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":52.48416,"mean_force":17.84438,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50094,0.10974,0.03608]},{"body_a":"peg","body_b":"channel_base_body","contact_count":190.0,"contact_point_centroid":[0.50595,0.07764,0.00943],"force_p95":5.01365,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.94031,"mean_force":1.16929,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50121,0.11414,0.04006]},{"body_a":"attachment","body_b":"peg","contact_count":33.0,"contact_point_centroid":[0.50561,0.09838,0.04635],"force_p95":5.21497,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.48125,"mean_force":3.78305,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50085,0.11031,0.03643]},{"body_a":"peg","body_b":"channel_base_body","contact_count":263.0,"contact_point_centroid":[0.50535,0.08085,0.00933],"force_p95":0.60642,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.60478,"phase_index":0.0,"phase_name":"prep_1","phase_type":"approach","tcp_position_centroid":[0.52286,0.15165,0.2639]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"prep_1","phase_type":"approach","tcp_position_centroid":[0.50145,0.19566,0.29857]},{"body_a":"peg","body_b":"channel_base_body","contact_count":392.0,"contact_point_centroid":[0.50642,0.06982,0.0094],"force_p95":0.64564,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.83636,"mean_force":0.5602,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49819,0.10866,0.10421]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":43.0,"contact_point_centroid":[0.52533,0.07248,0.04047],"force_p95":0.5121,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63004,"mean_force":0.21928,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49921,0.10962,0.04661]},{"body_a":"peg","body_b":"channel_base_body","contact_count":391.0,"contact_point_centroid":[0.50598,0.08092,0.00938],"force_p95":0.55007,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55023,"mean_force":0.54678,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51859,0.12443,0.12943]}],"total_contact_groups":12},"final_pose_error":0.01989,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50674,0.0701,0.03379],"final_tcp_position":[0.49849,0.10858,0.1665],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":3889.7992,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":292.0,"n_steps_budget":1000.0,"object_pos_end":[0.50598,0.0809,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16113,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54526,"phase_name":"prep_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":299.0,"raw_peak_contact_force":4.32595,"tcp_end":[0.53428,0.12823,0.20951],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.18419,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":391.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.08089,0.03378],"object_pos_start":[0.50598,0.0809,0.03378],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16113,"object_z_max":0.03378,"peak_contact_force":0.55006,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":391.0,"raw_peak_contact_force":0.55023,"subtask_id":"approach","tcp_end":[0.50391,0.12087,0.04873],"tcp_start":[0.53428,0.12823,0.20951],"tcp_to_object_dist_end":0.04274,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":190.0,"n_steps_budget":750.0,"object_pos_end":[0.50598,0.07999,0.03482],"object_pos_start":[0.50599,0.08089,0.03378],"object_to_goal_dist_end":0.16018,"object_to_goal_dist_start":0.16112,"object_z_max":0.03481,"peak_contact_force":83.79661,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":223.0,"raw_peak_contact_force":5.94031,"subtask_id":"contact","tcp_end":[0.50091,0.10986,0.03603],"tcp_start":[0.50391,0.12087,0.04873],"tcp_to_object_dist_end":0.03032,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.506,0.07992,0.03486],"object_pos_start":[0.50598,0.07999,0.03482],"object_to_goal_dist_end":0.16012,"object_to_goal_dist_start":0.16018,"object_z_max":0.03493,"peak_contact_force":3889.7992,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":8.0,"raw_peak_contact_force":608.65474,"subtask_id":"push","tcp_end":[0.50128,0.10921,0.03618],"tcp_start":[0.50098,0.10959,0.03616],"tcp_to_object_dist_end":0.0297,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":416.0,"n_steps_budget":1000.0,"object_pos_end":[0.50674,0.0701,0.03379],"object_pos_start":[0.50633,0.07936,0.03527],"object_to_goal_dist_end":0.15038,"object_to_goal_dist_start":0.15955,"object_z_max":0.03715,"peak_contact_force":0.53678,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":440.0,"raw_peak_contact_force":133.66871,"tcp_end":[0.49849,0.10858,0.1665],"tcp_start":[0.50128,0.10921,0.03618],"tcp_to_object_dist_end":0.13842,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.45946,"average_solve_count":148.0,"average_success_count":148.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.lateral_offset":0.00562,"approach_1.speed":0.05758,"contact_1.contact_force":13.90972,"contact_1.speed":0.02703,"prep_1.arc_height":0.15286,"prep_1.speed":0.0693,"push_1.push_depth":0.17789,"push_1.speed":0.01004,"retract_1.speed":0.09993},"optimized_scores":{"best_composite_score":-0.15953,"best_fitness_score":0.18047,"best_task_score":0.04099},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.55072,0.12,0.05999],"force_p95":596.90539,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":597.07166,"mean_force":595.13749,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50301,0.13251,0.03454]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.5507,0.12,0.06],"force_p95":19.9947,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":19.9947,"mean_force":19.9947,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50299,0.13267,0.03454]},{"body_a":"peg","body_b":"channel_base_body","contact_count":163.0,"contact_point_centroid":[0.50581,0.10248,0.00944],"force_p95":3.34377,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.24581,"mean_force":0.78805,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50459,0.13872,0.03938]},{"body_a":"attachment","body_b":"peg","contact_count":24.0,"contact_point_centroid":[0.50605,0.12167,0.04164],"force_p95":4.37108,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.7333,"mean_force":1.88028,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50316,0.13361,0.03521]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.50754,0.08495,0.00973],"force_p95":5.12632,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.18293,"mean_force":4.5127,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50301,0.13251,0.03454]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.50606,0.12055,0.04103],"force_p95":4.92947,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.98676,"mean_force":4.29722,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50301,0.13251,0.03454]},{"body_a":"peg","body_b":"channel_base_body","contact_count":198.0,"contact_point_centroid":[0.50529,0.10451,0.00934],"force_p95":0.70185,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.60344,"phase_index":0.0,"phase_name":"prep_1","phase_type":"approach","tcp_position_centroid":[0.51028,0.19462,0.24137]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"prep_1","phase_type":"approach","tcp_position_centroid":[0.50072,0.20075,0.29503]},{"body_a":"peg","body_b":"channel_base_body","contact_count":407.0,"contact_point_centroid":[0.50672,0.10133,0.00943],"force_p95":0.58788,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.73991,"mean_force":0.54305,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49994,0.13163,0.09887]},{"body_a":"peg","body_b":"channel_base_body","contact_count":372.0,"contact_point_centroid":[0.50581,0.10481,0.00939],"force_p95":0.57511,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57958,"mean_force":0.54637,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51294,0.15911,0.12408]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":21.0,"contact_point_centroid":[0.52502,0.1017,0.05904],"force_p95":0.08888,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.09103,"mean_force":0.01832,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49997,0.13217,0.07446]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50584,0.12022,0.03987],"force_p95":0.0,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50309,0.13215,0.03469]}],"total_contact_groups":12},"final_pose_error":0.02,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5068,0.10196,0.03388],"final_tcp_position":[0.50032,0.13141,0.1649],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":597.07166,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":225.0,"n_steps_budget":1000.0,"object_pos_end":[0.50584,0.10461,0.03383],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18481,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.55944,"phase_name":"prep_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":230.0,"raw_peak_contact_force":3.33087,"tcp_end":[0.51871,0.17149,0.19905],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.1787,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":372.0,"n_steps_budget":1000.0,"object_pos_end":[0.506,0.10464,0.03384],"object_pos_start":[0.50584,0.10461,0.03383],"object_to_goal_dist_end":0.18484,"object_to_goal_dist_start":0.18481,"object_z_max":0.03384,"peak_contact_force":0.54015,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":372.0,"raw_peak_contact_force":0.57958,"subtask_id":"approach","tcp_end":[0.5086,0.14677,0.04811],"tcp_start":[0.51871,0.17149,0.19905],"tcp_to_object_dist_end":0.04456,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":163.0,"n_steps_budget":630.0,"object_pos_end":[0.50631,0.10269,0.03442],"object_pos_start":[0.506,0.10464,0.03384],"object_to_goal_dist_end":0.18289,"object_to_goal_dist_start":0.18484,"object_z_max":0.0345,"peak_contact_force":19.9947,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":188.0,"raw_peak_contact_force":19.9947,"subtask_id":"contact","tcp_end":[0.50299,0.13263,0.03451],"tcp_start":[0.5086,0.14677,0.04811],"tcp_to_object_dist_end":0.03012,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50636,0.10259,0.03449],"object_pos_start":[0.50631,0.10269,0.03442],"object_to_goal_dist_end":0.18278,"object_to_goal_dist_start":0.18289,"object_z_max":0.03459,"peak_contact_force":0.98212,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":9.0,"raw_peak_contact_force":597.07166,"subtask_id":"push","tcp_end":[0.50309,0.13215,0.03469],"tcp_start":[0.50304,0.13237,0.03458],"tcp_to_object_dist_end":0.02975,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":408.0,"n_steps_budget":960.0,"object_pos_end":[0.5068,0.10196,0.03388],"object_pos_start":[0.50647,0.10226,0.03473],"object_to_goal_dist_end":0.18219,"object_to_goal_dist_start":0.18245,"object_z_max":0.03542,"peak_contact_force":0.54488,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":429.0,"raw_peak_contact_force":0.73991,"tcp_end":[0.50032,0.13141,0.1649],"tcp_start":[0.50309,0.13215,0.03469],"tcp_to_object_dist_end":0.13444,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```