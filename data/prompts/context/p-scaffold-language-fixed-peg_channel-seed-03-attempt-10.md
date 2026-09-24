## Search State

- **Seed**: 3
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | 0.3813 | 0.52 | ✅ accepted |
| 9 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.1035 | 0.22 | ❌ rejected |
| 8 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | -0.0530 | 0.00 | ❌ rejected |
| 7 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.1535 | 0.27 | ❌ rejected |
| 6 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | -0.0508 | 0.22 | ❌ rejected |

**Proposal policy**: task_score is 0.52 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.381) — your mutation base

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

- **Composite score**: 0.381
- **task_score** (E): 0.515
- **fitness_score**: 0.671  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.490

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| prep_1 | 1.00 | 1.00 | 0.1624 |
| approach_1 | 1.00 | 1.00 | 0.1109 |
| contact_1 | 1.00 | 1.00 | 0.0151 |
| push_1 | 0.33 | 1.00 | 0.1946 |
| retract_1 | 1.00 | 1.00 | 0.1304 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| prep_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.505, 0.131, 0.156) | (0.509, 0.081, 0.040)→(0.502, 0.081, 0.034) | 0.165→0.162 | 1.00 / 1.000 | 0.545 | 3.954 |
| approach_1 | approach | 1.00 / step_budget | (0.505, 0.131, 0.156)→(0.497, 0.122, 0.048) | (0.502, 0.081, 0.034)→(0.502, 0.082, 0.034) | 0.162→0.162 | 1.00 / 1.000 | 0.547 | 0.561 |
| contact_1 | contact | 1.00 / force_exceeded | (0.497, 0.122, 0.048)→(0.495, 0.112, 0.037) | (0.502, 0.082, 0.034)→(0.502, 0.081, 0.034) | 0.162→0.162 | 1.00 / 2.333 | 15.094 | 6.501 |
| push_1 | push | 0.33 / step_budget | (0.495, 0.112, 0.037)→(0.500, -0.082, 0.039) | (0.502, 0.081, 0.034)→(0.503, -0.099, 0.032) | 0.162→0.028 | 1.00 / 3.333 | 3.822 | 209.028 |
| retract_1 | retract | 1.00 / step_budget | (0.500, -0.082, 0.039)→(0.498, -0.082, 0.169) | (0.503, -0.099, 0.032)→(0.502, -0.100, 0.029) | 0.028→0.038 | 1.00 / 1.000 | 0.541 | 101.364 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 1.000
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.763
- phase_score: 0.755
- phase_breakdown.approach_score: 0.478
- phase_breakdown.contact_score: 0.465
- phase_breakdown.push_score: 0.944

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.758
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.763
- **Median Q (composite search score)**: 0.396
- **K-run variance**: 0.0060
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.318


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.44091,"average_solve_count":220.0,"average_success_count":220.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.lateral_offset":0.00134,"approach_1.speed":0.05727,"contact_1.contact_force":4.8154,"contact_1.speed":0.01483,"prep_1.speed":0.06395,"push_1.push_depth":0.15433,"push_1.speed":0.07624,"retract_1.speed":0.07288},"optimized_scores":{"best_composite_score":0.28015,"best_fitness_score":0.57015,"best_task_score":0.27713},"replay_outcomes":[{"contacts":{"omitted_contact_groups":2,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":615.0,"contact_point_centroid":[0.53376,0.00468,0.05999],"force_p95":181.27211,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":232.61685,"mean_force":134.29813,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48847,0.00794,0.0379]},{"body_a":"channel_base_body","body_b":"link7","contact_count":61.0,"contact_point_centroid":[0.53708,-0.10001,0.06497],"force_p95":199.69194,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":228.82288,"mean_force":124.26119,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49406,-0.07709,0.03883]},{"body_a":"attachment","body_b":"peg","contact_count":887.0,"contact_point_centroid":[0.49798,-0.01207,0.03481],"force_p95":125.87901,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":153.00007,"mean_force":80.52203,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48931,-0.00814,0.03803]},{"body_a":"peg","body_b":"channel_base_body","contact_count":959.0,"contact_point_centroid":[0.50778,-0.02076,0.00863],"force_p95":107.42668,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":150.69691,"mean_force":49.1171,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48914,-0.00259,0.03801]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":818.0,"contact_point_centroid":[0.52628,-0.02012,0.02504],"force_p95":104.86924,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":112.31478,"mean_force":63.94848,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48922,-0.01059,0.03797]},{"body_a":"peg","body_b":"channel_base_body","contact_count":406.0,"contact_point_centroid":[0.4992,-0.07488,0.00797],"force_p95":0.74575,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":78.89615,"mean_force":1.4231,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49425,-0.08705,0.10457]},{"body_a":"attachment","body_b":"peg","contact_count":20.0,"contact_point_centroid":[0.50743,-0.08745,0.03735],"force_p95":45.44855,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":78.8657,"mean_force":16.67025,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4965,-0.08754,0.04209]},{"body_a":"peg","body_b":"channel_base_body","contact_count":32.0,"contact_point_centroid":[0.50535,-0.10021,0.03009],"force_p95":37.50812,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":48.45598,"mean_force":19.53515,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49584,-0.08379,0.03978]},{"body_a":"peg","body_b":"link7","contact_count":244.0,"contact_point_centroid":[0.51906,-0.00235,0.06803],"force_p95":35.59266,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":47.06768,"mean_force":17.23336,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48859,0.02285,0.03796]},{"body_a":"channel_base_body","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54038,-0.1,0.065],"force_p95":43.26061,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":43.26061,"mean_force":43.26061,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49709,-0.08763,0.04035]},{"body_a":"peg","body_b":"world","contact_count":102.0,"contact_point_centroid":[0.50837,-0.06788,-0.00075],"force_p95":12.24899,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":31.16462,"mean_force":1.87191,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49203,-0.06773,0.03802]},{"body_a":"peg","body_b":"channel_base_body","contact_count":5.0,"contact_point_centroid":[0.50171,-0.10009,0.02993],"force_p95":15.74027,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.83829,"mean_force":8.36473,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49706,-0.08759,0.04038]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.53137,0.09291,0.05999],"force_p95":9.80759,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":9.80759,"mean_force":9.80759,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48602,0.09208,0.03763]},{"body_a":"peg","body_b":"channel_base_body","contact_count":313.0,"contact_point_centroid":[0.49447,0.05889,0.00933],"force_p95":0.62041,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.59291,"phase_index":0.0,"phase_name":"prep_1","phase_type":"approach","tcp_position_centroid":[0.48286,0.15294,0.22239]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"prep_1","phase_type":"approach","tcp_position_centroid":[0.49854,0.19697,0.29495]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":1.0,"contact_point_centroid":[0.47498,0.04981,0.06],"force_p95":1.35454,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.35454,"mean_force":1.35454,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48658,0.08138,0.03776]}],"total_contact_groups":18},"final_pose_error":0.01993,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49381,-0.07397,0.02413],"final_tcp_position":[0.49433,-0.08701,0.1706],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":232.61685,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":342.0,"n_steps_budget":1000.0,"object_pos_end":[0.4942,0.0589,0.03385],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13915,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54255,"phase_name":"prep_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":348.0,"raw_peak_contact_force":4.20518,"tcp_end":[0.46849,0.111,0.15559],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.1349,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":300.0,"n_steps_budget":1000.0,"object_pos_end":[0.49403,0.05906,0.03388],"object_pos_start":[0.4942,0.0589,0.03385],"object_to_goal_dist_end":0.13932,"object_to_goal_dist_start":0.13915,"object_z_max":0.03388,"peak_contact_force":0.54533,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":300.0,"raw_peak_contact_force":0.55326,"subtask_id":"approach","tcp_end":[0.48797,0.09994,0.04668],"tcp_start":[0.46849,0.111,0.15559],"tcp_to_object_dist_end":0.04327,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":156.0,"n_steps_budget":1000.0,"object_pos_end":[0.49397,0.05898,0.0339],"object_pos_start":[0.49403,0.05906,0.03388],"object_to_goal_dist_end":0.13924,"object_to_goal_dist_start":0.13932,"object_z_max":0.0339,"peak_contact_force":9.80759,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":157.0,"raw_peak_contact_force":9.80759,"subtask_id":"contact","tcp_end":[0.48602,0.09205,0.03762],"tcp_start":[0.48797,0.09994,0.04668],"tcp_to_object_dist_end":0.03422,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50608,-0.07521,0.0187],"object_pos_start":[0.49397,0.05898,0.0339],"object_to_goal_dist_end":0.02266,"object_to_goal_dist_start":0.13924,"object_z_max":0.03972,"peak_contact_force":4.47987,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3719.0,"raw_peak_contact_force":232.61685,"subtask_id":"push","tcp_end":[0.49709,-0.0874,0.04033],"tcp_start":[0.48602,0.09205,0.03762],"tcp_to_object_dist_end":0.02641,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":406.0,"n_steps_budget":1000.0,"object_pos_end":[0.49381,-0.07397,0.02413],"object_pos_start":[0.50608,-0.07521,0.0187],"object_to_goal_dist_end":0.01808,"object_to_goal_dist_start":0.02266,"object_z_max":0.02482,"peak_contact_force":0.53261,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":432.0,"raw_peak_contact_force":78.89615,"tcp_end":[0.49433,-0.08701,0.1706],"tcp_start":[0.49709,-0.0874,0.04033],"tcp_to_object_dist_end":0.14705,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.99296,"average_solve_count":284.0,"average_success_count":284.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.lateral_offset":-0.00758,"approach_1.speed":0.01663,"contact_1.contact_force":11.57863,"contact_1.speed":0.01603,"prep_1.speed":0.08587,"push_1.push_depth":0.02354,"push_1.speed":0.08316,"retract_1.speed":0.06606},"optimized_scores":{"best_composite_score":0.46813,"best_fitness_score":0.75813,"best_task_score":0.76327},"replay_outcomes":[{"contacts":{"omitted_contact_groups":2,"reported_contact_groups":[{"body_a":"channel_base_body","body_b":"link7","contact_count":88.0,"contact_point_centroid":[0.54357,-0.1,0.06497],"force_p95":184.49707,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":198.86733,"mean_force":140.12737,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50106,-0.07414,0.03772]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":429.0,"contact_point_centroid":[0.5436,0.01654,0.05999],"force_p95":128.80099,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":157.79057,"mean_force":107.45171,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49881,0.01708,0.03675]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":8.0,"contact_point_centroid":[0.52502,-0.08061,0.05999],"force_p95":118.41093,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":129.75687,"mean_force":67.78305,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50209,-0.08049,0.03867]},{"body_a":"attachment","body_b":"peg","contact_count":392.0,"contact_point_centroid":[0.50382,-0.0196,0.04445],"force_p95":97.11044,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":120.7361,"mean_force":26.15971,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4992,-0.00811,0.03687]},{"body_a":"peg","body_b":"channel_base_body","contact_count":222.0,"contact_point_centroid":[0.50245,-0.10662,0.04511],"force_p95":107.55576,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":119.20312,"mean_force":43.53247,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5001,-0.06666,0.03714]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":39.0,"contact_point_centroid":[0.47473,-0.1067,0.02319],"force_p95":31.4915,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":91.20099,"mean_force":13.90413,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50136,-0.07605,0.03802]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":324.0,"contact_point_centroid":[0.5252,-0.02034,0.03912],"force_p95":17.12933,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":70.9844,"mean_force":3.72704,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49906,0.0108,0.03693]},{"body_a":"channel_base_body","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.54478,-0.10001,0.06497],"force_p95":60.96062,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":61.13942,"mean_force":52.33889,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50205,-0.08177,0.03887]},{"body_a":"peg","body_b":"channel_base_body","contact_count":374.0,"contact_point_centroid":[0.50475,-0.01292,0.00966],"force_p95":23.53356,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":47.3075,"mean_force":4.33273,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49878,0.02814,0.0368]},{"body_a":"peg","body_b":"channel_base_body","contact_count":293.0,"contact_point_centroid":[0.50607,0.0805,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32713,"mean_force":0.57288,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49786,0.11458,0.03967]},{"body_a":"peg","body_b":"channel_base_body","contact_count":293.0,"contact_point_centroid":[0.50542,0.08086,0.00934],"force_p95":0.58945,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.59884,"phase_index":0.0,"phase_name":"prep_1","phase_type":"approach","tcp_position_centroid":[0.51426,0.16305,0.22208]},{"body_a":"attachment","body_b":"peg","contact_count":4.0,"contact_point_centroid":[0.50566,0.09879,0.05151],"force_p95":3.68769,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.95155,"mean_force":2.10251,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49849,0.11069,0.03632]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"prep_1","phase_type":"approach","tcp_position_centroid":[0.50065,0.19726,0.29419]},{"body_a":"peg","body_b":"world","contact_count":382.0,"contact_point_centroid":[0.50477,-0.15584,-0.00036],"force_p95":0.71792,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.49444,"mean_force":0.54521,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49899,-0.08117,0.10935]},{"body_a":"peg","body_b":"channel_base_body","contact_count":29.0,"contact_point_centroid":[0.50122,-0.11309,0.04365],"force_p95":1.16978,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.64505,"mean_force":0.35802,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5012,-0.08188,0.04174]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":2.0,"contact_point_centroid":[0.47495,-0.11546,0.02361],"force_p95":1.37634,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.38677,"mean_force":1.28249,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50209,-0.08159,0.03883]}],"total_contact_groups":18},"final_pose_error":0.01976,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50567,-0.15883,0.02746],"final_tcp_position":[0.49928,-0.08114,0.16928],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":198.86733,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":322.0,"n_steps_budget":1000.0,"object_pos_end":[0.50598,0.0809,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16113,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54522,"phase_name":"prep_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":329.0,"raw_peak_contact_force":4.32595,"tcp_end":[0.52812,0.13059,0.15558],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.1334,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":276.0,"n_steps_budget":1000.0,"object_pos_end":[0.50597,0.0809,0.03378],"object_pos_start":[0.50598,0.0809,0.03378],"object_to_goal_dist_end":0.16113,"object_to_goal_dist_start":0.16113,"object_z_max":0.03378,"peak_contact_force":0.54527,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":276.0,"raw_peak_contact_force":0.55023,"subtask_id":"approach","tcp_end":[0.49954,0.1216,0.04857],"tcp_start":[0.52812,0.13059,0.15558],"tcp_to_object_dist_end":0.04379,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":293.0,"n_steps_budget":1000.0,"object_pos_end":[0.50597,0.08077,0.03396],"object_pos_start":[0.50597,0.0809,0.03378],"object_to_goal_dist_end":0.161,"object_to_goal_dist_start":0.16113,"object_z_max":0.03393,"peak_contact_force":30.40831,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":297.0,"raw_peak_contact_force":4.32713,"subtask_id":"contact","tcp_end":[0.49852,0.11059,0.03625],"tcp_start":[0.49954,0.1216,0.04857],"tcp_to_object_dist_end":0.03082,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":802.0,"n_steps_budget":1000.0,"object_pos_end":[0.49984,-0.11451,0.04164],"object_pos_start":[0.50597,0.08077,0.03396],"object_to_goal_dist_end":0.03455,"object_to_goal_dist_start":0.161,"object_z_max":0.04248,"peak_contact_force":6.93377,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1876.0,"raw_peak_contact_force":198.86733,"subtask_id":"push","tcp_end":[0.5021,-0.0815,0.03883],"tcp_start":[0.49852,0.11059,0.03625],"tcp_to_object_dist_end":0.0332,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":422.0,"n_steps_budget":1000.0,"object_pos_end":[0.50567,-0.15883,0.02746],"object_pos_start":[0.49984,-0.11451,0.04164],"object_to_goal_dist_end":0.08002,"object_to_goal_dist_start":0.03455,"object_z_max":0.04171,"peak_contact_force":0.57253,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":420.0,"raw_peak_contact_force":61.13942,"tcp_end":[0.49928,-0.08114,0.16928],"tcp_start":[0.5021,-0.0815,0.03883],"tcp_to_object_dist_end":0.16183,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.05776,"average_solve_count":277.0,"average_success_count":277.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.lateral_offset":-0.00207,"approach_1.speed":0.04503,"contact_1.contact_force":4.92784,"contact_1.speed":0.0286,"prep_1.speed":0.05209,"push_1.push_depth":0.06625,"push_1.speed":0.04945,"retract_1.speed":0.07035},"optimized_scores":{"best_composite_score":0.39567,"best_fitness_score":0.68567,"best_task_score":0.50555},"replay_outcomes":[{"contacts":{"omitted_contact_groups":4,"reported_contact_groups":[{"body_a":"channel_base_body","body_b":"link7","contact_count":137.0,"contact_point_centroid":[0.54351,-0.10001,0.06497],"force_p95":177.86989,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":195.59958,"mean_force":130.1043,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50107,-0.07239,0.03736]},{"body_a":"peg","body_b":"channel_base_body","contact_count":333.0,"contact_point_centroid":[0.50881,-0.10316,0.06286],"force_p95":146.37012,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":164.05595,"mean_force":84.37317,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49789,-0.06655,0.0676]},{"body_a":"attachment","body_b":"peg","contact_count":479.0,"contact_point_centroid":[0.5014,-0.02001,0.0401],"force_p95":98.85219,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":163.91721,"mean_force":34.88996,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49994,-0.00836,0.03671]},{"body_a":"attachment","body_b":"peg","contact_count":305.0,"contact_point_centroid":[0.50341,-0.0748,0.06849],"force_p95":147.28517,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":163.48648,"mean_force":92.41763,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49778,-0.06583,0.06612]},{"body_a":"peg","body_b":"channel_base_body","contact_count":295.0,"contact_point_centroid":[0.50236,-0.10691,0.04746],"force_p95":106.12112,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":162.9683,"mean_force":52.81636,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5005,-0.06588,0.03698]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":17.0,"contact_point_centroid":[0.52501,-0.07564,0.06],"force_p95":128.95294,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":132.63919,"mean_force":69.59771,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5016,-0.07555,0.03786]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":527.0,"contact_point_centroid":[0.5444,0.02473,0.05999],"force_p95":119.92257,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":124.68055,"mean_force":103.51421,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49958,0.02541,0.03657]},{"body_a":"channel_base_body","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.54433,-0.10001,0.06496],"force_p95":82.65043,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":86.56571,"mean_force":58.53906,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50178,-0.07802,0.03819]},{"body_a":"peg","body_b":"channel_base_body","contact_count":562.0,"contact_point_centroid":[0.49796,-0.01462,0.00961],"force_p95":25.48431,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":39.33957,"mean_force":4.79039,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49971,0.02342,0.03666]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":228.0,"contact_point_centroid":[0.5254,-0.08284,0.05756],"force_p95":34.77614,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":36.4596,"mean_force":18.98111,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49742,-0.06597,0.07878]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.52501,-0.0781,0.06],"force_p95":30.7593,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":32.90617,"mean_force":14.78122,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50178,-0.07802,0.03818]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":125.0,"contact_point_centroid":[0.47465,0.00345,0.02564],"force_p95":3.81977,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.31689,"mean_force":1.06375,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49962,0.03293,0.03674]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":44.0,"contact_point_centroid":[0.47462,-0.0763,0.04927],"force_p95":12.81488,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.96416,"mean_force":6.90129,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49766,-0.07023,0.09451]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":82.0,"contact_point_centroid":[0.52517,0.06654,0.03775],"force_p95":3.80257,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.37589,"mean_force":0.76666,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49924,0.09634,0.03608]},{"body_a":"peg","body_b":"channel_base_body","contact_count":159.0,"contact_point_centroid":[0.50536,0.1037,0.00939],"force_p95":0.57598,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.36683,"mean_force":0.65631,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50028,0.13848,0.0404]},{"body_a":"attachment","body_b":"peg","contact_count":9.0,"contact_point_centroid":[0.50554,0.12244,0.04845],"force_p95":4.85744,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.89013,"mean_force":2.13607,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50005,0.13431,0.03653]}],"total_contact_groups":20},"final_pose_error":0.01982,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50576,-0.06734,0.03404],"final_tcp_position":[0.49897,-0.07762,0.16856],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":195.59958,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":310.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.10468,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18488,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.54706,"phase_name":"prep_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":315.0,"raw_peak_contact_force":3.33087,"tcp_end":[0.5183,0.15168,0.15735],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13273,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":267.0,"n_steps_budget":1000.0,"object_pos_end":[0.50583,0.10463,0.03384],"object_pos_start":[0.50599,0.10468,0.03384],"object_to_goal_dist_end":0.18483,"object_to_goal_dist_start":0.18488,"object_z_max":0.03384,"peak_contact_force":0.55005,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":267.0,"raw_peak_contact_force":0.57941,"subtask_id":"approach","tcp_end":[0.50255,0.14478,0.04841],"tcp_start":[0.5183,0.15168,0.15735],"tcp_to_object_dist_end":0.04284,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":159.0,"n_steps_budget":600.0,"object_pos_end":[0.50583,0.10427,0.03421],"object_pos_start":[0.50583,0.10463,0.03384],"object_to_goal_dist_end":0.18446,"object_to_goal_dist_start":0.18483,"object_z_max":0.03416,"peak_contact_force":5.06664,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":168.0,"raw_peak_contact_force":5.36683,"subtask_id":"contact","tcp_end":[0.5001,0.13395,0.03624],"tcp_start":[0.50255,0.14478,0.04841],"tcp_to_object_dist_end":0.0303,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50239,-0.10752,0.03698],"object_pos_start":[0.50583,0.10427,0.03421],"object_to_goal_dist_end":0.02778,"object_to_goal_dist_start":0.18446,"object_z_max":0.03995,"peak_contact_force":0.05201,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2224.0,"raw_peak_contact_force":195.59958,"subtask_id":"push","tcp_end":[0.50177,-0.07799,0.03817],"tcp_start":[0.5001,0.13395,0.03624],"tcp_to_object_dist_end":0.02955,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":544.0,"n_steps_budget":1000.0,"object_pos_end":[0.50576,-0.06734,0.03404],"object_pos_start":[0.50239,-0.10752,0.03698],"object_to_goal_dist_end":0.01513,"object_to_goal_dist_start":0.02778,"object_z_max":0.06733,"peak_contact_force":0.51866,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1093.0,"raw_peak_contact_force":164.05595,"tcp_end":[0.49897,-0.07762,0.16856],"tcp_start":[0.50177,-0.07799,0.03817],"tcp_to_object_dist_end":0.13508,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```