## Search State

- **Seed**: 6
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | 0.4631 | 0.73 | ✅ accepted |
| 1 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.3601 | 0.73 | ✅ accepted |
| 0 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.3561 | 0.72 | ✅ accepted |

**Proposal policy**: task_score is 0.73 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.463) — your mutation base

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
    - 0.0
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
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: contact
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
    offset_along_axis:
      distance: 0.04
      axis: world_y
      mode: add_to_offset
      sign: negative
    orientation:
      mode: keep_current
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 2.0
      - 15.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
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
      distance: 0.12
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
    orientation:
      mode: align_axis
      axis:
      - 1.0
      - 0.0
      - 0.0
      align_with: channel_axis
      tolerance: 0.1
  parameters:
    push_depth:
      type: scalar
      range:
      - 0.08
      - 0.18
      default: 0.12
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
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
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.02, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - lateral_offset_x: status=consumed; consumers=target.offset.x (replace)
    - lateral_offset_y: status=consumed; consumers=target.offset.y (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **contact_1** (`contact`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.02, 0.0], offset_along_axis={axis=world_y, distance=0.04, mode=add_to_offset, sign=negative}
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
  - retries: max_attempts=0, strategy=repeat
- **push_1** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.12, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=align_axis, axis=[1.0, 0.0, 0.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - push_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.15], tolerance=0.05
  - orientation: mode=none
  - parameter_bindings:
    - retract_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.463
- **task_score** (E): 0.733
- **fitness_score**: 0.753  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.490

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_1 | 1.00 | 1.00 | 0.2005 |
| approach_1 | 1.00 | 1.00 | 0.0727 |
| contact_1 | 1.00 | 1.00 | 0.0099 |
| push_1 | 0.00 | 1.00 | 0.1927 |
| retract_1 | 1.00 | 1.00 | 0.0657 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.497, 0.145, 0.108) | (0.500, 0.099, 0.040)→(0.501, 0.099, 0.034) | 0.180→0.180 | 1.00 / 1.000 | 0.560 | 2.127 |
| approach_1 | approach | 1.00 / step_budget | (0.497, 0.145, 0.108)→(0.505, 0.114, 0.043) | (0.501, 0.099, 0.034)→(0.498, 0.089, 0.033) | 0.180→0.169 | 1.00 / 2.333 | 93.940 | 209.588 |
| contact_1 | contact | 1.00 / force_exceeded | (0.505, 0.114, 0.043)→(0.501, 0.106, 0.041) | (0.498, 0.089, 0.033)→(0.498, 0.082, 0.033) | 0.169→0.162 | 1.00 / 2.667 | 1345.719 | 49.669 |
| push_1 | push | 0.00 / step_budget | (0.501, 0.106, 0.041)→(0.501, -0.087, 0.034) | (0.498, 0.082, 0.033)→(0.500, -0.112, 0.021) | 0.162→0.117 | 1.00 / 2.000 | 247.156 | 256.287 |
| retract_1 | retract | 1.00 / step_budget | (0.501, -0.087, 0.034)→(0.500, -0.081, 0.100) | (0.500, -0.112, 0.021)→(0.499, -0.113, 0.022) | 0.117→0.118 | 1.00 / 1.000 | 0.607 | 77.662 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 1.000
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.954
- phase_score: 0.804
- phase_breakdown.push_score: 0.830
- phase_breakdown.approach_score: 0.631
- phase_breakdown.contact_score: 0.898

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.864
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.954
- **Median Q (composite search score)**: 0.492
- **K-run variance**: 0.0110
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.325


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.24481,"average_solve_count":241.0,"average_success_count":241.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.lateral_offset_x":3e-05,"approach_1.lateral_offset_y":0.0068,"approach_1.speed":0.02773,"contact_1.contact_force_threshold":14.9806,"push_1.push_depth":0.13883,"push_1.speed":0.06634,"retract_1.retract_height":0.14073,"retract_1.speed":0.05933},"optimized_scores":{"best_composite_score":0.4924,"best_fitness_score":0.7824,"best_task_score":0.90769},"replay_outcomes":[{"contacts":{"omitted_contact_groups":2,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_base_body","contact_count":590.0,"contact_point_centroid":[0.50262,-0.10006,0.065],"force_p95":251.50261,"geom_a":"pusher_tip","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":256.23766,"mean_force":235.23674,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49776,-0.08709,0.03255]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":63.0,"contact_point_centroid":[0.52506,0.08022,0.05999],"force_p95":153.08789,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":227.47477,"mean_force":119.54709,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51187,0.08037,0.04898]},{"body_a":"peg","body_b":"channel_base_body","contact_count":518.0,"contact_point_centroid":[0.51044,0.06904,0.00855],"force_p95":177.60656,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":179.6459,"mean_force":85.46658,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50402,0.09128,0.06327]},{"body_a":"attachment","body_b":"peg","contact_count":308.0,"contact_point_centroid":[0.51543,0.07531,0.05326],"force_p95":177.74748,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":179.15539,"mean_force":142.92212,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50754,0.0836,0.0515]},{"body_a":"peg","body_b":"channel_base_body","contact_count":146.0,"contact_point_centroid":[0.49518,-0.10753,0.0359],"force_p95":90.67811,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":143.19054,"mean_force":40.37057,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49588,-0.06933,0.03298]},{"body_a":"attachment","body_b":"peg","contact_count":239.0,"contact_point_centroid":[0.49543,-0.03945,0.03522],"force_p95":81.45306,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":108.95403,"mean_force":25.27969,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49558,-0.02779,0.03237]},{"body_a":"attachment","body_b":"channel_base_body","contact_count":2.0,"contact_point_centroid":[0.50575,-0.10002,0.065],"force_p95":50.15391,"geom_a":"pusher_tip","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":50.82007,"mean_force":44.1584,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50047,-0.08632,0.03168]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":106.0,"contact_point_centroid":[0.47469,-0.03995,0.03661],"force_p95":12.09626,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":49.33842,"mean_force":3.05262,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49575,-0.0097,0.03235]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":6.0,"contact_point_centroid":[0.52523,-0.11958,0.021],"force_p95":16.4421,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.31716,"mean_force":5.58185,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49606,-0.08432,0.0332]},{"body_a":"peg","body_b":"channel_base_body","contact_count":166.0,"contact_point_centroid":[0.49878,-0.03297,0.00976],"force_p95":8.38676,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.56857,"mean_force":2.26288,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49545,0.00257,0.032]},{"body_a":"peg","body_b":"channel_base_body","contact_count":180.0,"contact_point_centroid":[0.49705,0.02556,0.00987],"force_p95":8.63732,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.34981,"mean_force":3.50027,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50178,0.06714,0.03732]},{"body_a":"attachment","body_b":"peg","contact_count":163.0,"contact_point_centroid":[0.49982,0.05374,0.03689],"force_p95":8.36791,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.87968,"mean_force":3.40095,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50111,0.06556,0.03679]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":61.0,"contact_point_centroid":[0.52502,0.06113,0.05597],"force_p95":3.36109,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.08527,"mean_force":1.95019,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50984,0.08201,0.05029]},{"body_a":"peg","body_b":"world","contact_count":554.0,"contact_point_centroid":[0.5115,-0.2132,-0.00188],"force_p95":0.87922,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.34262,"mean_force":0.62993,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49787,-0.087,0.03251]},{"body_a":"peg","body_b":"channel_base_body","contact_count":385.0,"contact_point_centroid":[0.50304,0.06739,0.00932],"force_p95":0.61054,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.56899,"phase_index":0.0,"phase_name":"align_1","phase_type":"approach","tcp_position_centroid":[0.49942,0.15735,0.20055]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":6.0,"contact_point_centroid":[0.47458,0.04074,0.05753],"force_p95":1.49882,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.57935,"mean_force":0.93116,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50766,0.07869,0.0427]}],"total_contact_groups":18},"final_pose_error":0.04927,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49612,-0.23237,0.01416],"final_tcp_position":[0.49988,-0.07919,0.12367],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":3913.70894,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":401.0,"n_steps_budget":1000.0,"object_pos_end":[0.50302,0.06748,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14764,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54683,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":385.0,"raw_peak_contact_force":2.06903,"subtask_id":"approach","tcp_end":[0.49999,0.1165,0.10729],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08839,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":518.0,"n_steps_budget":1000.0,"object_pos_end":[0.49621,0.04557,0.03788],"object_pos_start":[0.50302,0.06748,0.0338],"object_to_goal_dist_end":0.12565,"object_to_goal_dist_start":0.14764,"object_z_max":0.03768,"peak_contact_force":0.42418,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":956.0,"raw_peak_contact_force":227.47477,"subtask_id":"contact","tcp_end":[0.50705,0.07836,0.04175],"tcp_start":[0.49999,0.1165,0.10729],"tcp_to_object_dist_end":0.03475,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":253.0,"n_steps_budget":600.0,"object_pos_end":[0.49344,0.02485,0.03578],"object_pos_start":[0.49621,0.04557,0.03788],"object_to_goal_dist_end":0.10514,"object_to_goal_dist_start":0.12565,"object_z_max":0.0398,"peak_contact_force":3913.70894,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":370.0,"raw_peak_contact_force":10.34981,"tcp_end":[0.49826,0.05401,0.0354],"tcp_start":[0.50705,0.07836,0.04175],"tcp_to_object_dist_end":0.02955,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50092,-0.22789,0.01413],"object_pos_start":[0.49344,0.02485,0.03578],"object_to_goal_dist_end":0.15014,"object_to_goal_dist_start":0.10514,"object_z_max":0.03983,"peak_contact_force":250.4322,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1807.0,"raw_peak_contact_force":256.23766,"subtask_id":"push","tcp_end":[0.50047,-0.08633,0.03169],"tcp_start":[0.49826,0.05401,0.0354],"tcp_to_object_dist_end":0.14264,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":110.0,"n_steps_budget":1000.0,"object_pos_end":[0.49612,-0.23237,0.01416],"object_pos_start":[0.50092,-0.22789,0.01413],"object_to_goal_dist_end":0.15459,"object_to_goal_dist_start":0.15014,"object_z_max":0.01416,"peak_contact_force":0.63327,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":112.0,"raw_peak_contact_force":50.82007,"tcp_end":[0.49988,-0.07919,0.12367],"tcp_start":[0.50047,-0.08633,0.03169],"tcp_to_object_dist_end":0.18834,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.58294,"average_solve_count":211.0,"average_success_count":211.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.lateral_offset_x":0.0099,"approach_1.lateral_offset_y":0.00552,"approach_1.speed":0.05494,"contact_1.contact_force_threshold":6.44429,"push_1.push_depth":0.15217,"push_1.speed":0.06285,"retract_1.retract_height":0.14036,"retract_1.speed":0.0705},"optimized_scores":{"best_composite_score":0.574,"best_fitness_score":0.864,"best_task_score":0.9543},"replay_outcomes":[{"contacts":{"omitted_contact_groups":2,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_base_body","contact_count":376.0,"contact_point_centroid":[0.50734,-0.10009,0.065],"force_p95":243.27664,"geom_a":"pusher_tip","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":254.70468,"mean_force":212.22994,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50332,-0.08754,0.03607]},{"body_a":"peg","body_b":"channel_base_body","contact_count":391.0,"contact_point_centroid":[0.51047,0.11355,0.00885],"force_p95":171.44382,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":193.23246,"mean_force":63.12578,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51014,0.13683,0.06711]},{"body_a":"attachment","body_b":"peg","contact_count":193.0,"contact_point_centroid":[0.51945,0.12021,0.05429],"force_p95":172.36658,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":192.72619,"mean_force":127.70434,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51413,0.12971,0.05257]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":9.0,"contact_point_centroid":[0.52505,0.11998,0.05999],"force_p95":171.41406,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":172.87947,"mean_force":138.45316,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51104,0.12514,0.03847]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":105.0,"contact_point_centroid":[0.52503,0.11997,0.06],"force_p95":160.6153,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":171.78344,"mean_force":116.81927,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51652,0.12951,0.04984]},{"body_a":"peg","body_b":"channel_base_body","contact_count":164.0,"contact_point_centroid":[0.4942,-0.10825,0.03554],"force_p95":119.28056,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":151.22462,"mean_force":54.2738,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50359,-0.0725,0.0364]},{"body_a":"attachment","body_b":"peg","contact_count":325.0,"contact_point_centroid":[0.50089,-0.01837,0.03949],"force_p95":101.3689,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":130.25795,"mean_force":34.66335,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50568,-0.00788,0.03675]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":448.0,"contact_point_centroid":[0.47469,-0.01726,0.03281],"force_p95":39.3727,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":97.05163,"mean_force":9.12835,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50617,0.00923,0.03673]},{"body_a":"attachment","body_b":"channel_base_body","contact_count":2.0,"contact_point_centroid":[0.50867,-0.10002,0.065],"force_p95":83.98344,"geom_a":"pusher_tip","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":85.72898,"mean_force":68.2736,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50446,-0.08689,0.03563]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":96.0,"contact_point_centroid":[0.52516,0.11071,0.05654],"force_p95":27.98796,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":42.93139,"mean_force":7.52665,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51493,0.12877,0.05209]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.52501,0.11999,0.06],"force_p95":32.24484,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":32.90161,"mean_force":26.93172,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.51502,0.12928,0.04284]},{"body_a":"peg","body_b":"channel_base_body","contact_count":284.0,"contact_point_centroid":[0.49635,-0.01437,0.00969],"force_p95":23.85029,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":32.056,"mean_force":6.67636,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50652,0.01997,0.03679]},{"body_a":"peg","body_b":"world","contact_count":347.0,"contact_point_centroid":[0.50079,-0.15538,-0.0004],"force_p95":0.80988,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.35721,"mean_force":0.55261,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50334,-0.08741,0.03605]},{"body_a":"peg","body_b":"channel_base_body","contact_count":350.0,"contact_point_centroid":[0.50351,0.11176,0.00934],"force_p95":0.6343,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.56822,"phase_index":0.0,"phase_name":"align_1","phase_type":"approach","tcp_position_centroid":[0.50263,0.17712,0.19971]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":11.0,"contact_point_centroid":[0.47477,0.10193,0.05709],"force_p95":0.97167,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.08894,"mean_force":0.33235,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.51487,0.12935,0.04267]},{"body_a":"peg","body_b":"channel_base_body","contact_count":15.0,"contact_point_centroid":[0.48566,0.09773,0.00885],"force_p95":0.78991,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86732,"mean_force":0.48432,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.51476,0.12922,0.04256]}],"total_contact_groups":18},"final_pose_error":0.04973,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50407,-0.15243,0.02671],"final_tcp_position":[0.50384,-0.07977,0.12678],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":254.70468,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":372.0,"n_steps_budget":1000.0,"object_pos_end":[0.50375,0.11176,0.0338],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.1919,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.56268,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":366.0,"raw_peak_contact_force":2.06328,"subtask_id":"approach","tcp_end":[0.50616,0.15629,0.10861],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08709,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":391.0,"n_steps_budget":960.0,"object_pos_end":[0.49684,0.10434,0.03456],"object_pos_start":[0.50375,0.11176,0.0338],"object_to_goal_dist_end":0.18445,"object_to_goal_dist_start":0.1919,"object_z_max":0.03429,"peak_contact_force":142.06375,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":785.0,"raw_peak_contact_force":193.23246,"subtask_id":"contact","tcp_end":[0.51561,0.12969,0.04346],"tcp_start":[0.50616,0.15629,0.10861],"tcp_to_object_dist_end":0.03277,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":15.0,"n_steps_budget":600.0,"object_pos_end":[0.49712,0.10444,0.03646],"object_pos_start":[0.49684,0.10434,0.03456],"object_to_goal_dist_end":0.18449,"object_to_goal_dist_start":0.18445,"object_z_max":0.03642,"peak_contact_force":17.69295,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":29.0,"raw_peak_contact_force":32.90161,"tcp_end":[0.51383,0.12836,0.04168],"tcp_start":[0.51561,0.12969,0.04346],"tcp_to_object_dist_end":0.02964,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50271,-0.15385,0.02618],"object_pos_start":[0.49712,0.10444,0.03646],"object_to_goal_dist_end":0.07518,"object_to_goal_dist_start":0.18449,"object_z_max":0.03959,"peak_contact_force":242.15972,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1953.0,"raw_peak_contact_force":254.70468,"subtask_id":"push","tcp_end":[0.50445,-0.0869,0.03563],"tcp_start":[0.51383,0.12836,0.04168],"tcp_to_object_dist_end":0.06763,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":107.0,"n_steps_budget":1000.0,"object_pos_end":[0.50407,-0.15243,0.02671],"object_pos_start":[0.50271,-0.15385,0.02618],"object_to_goal_dist_end":0.07376,"object_to_goal_dist_start":0.07518,"object_z_max":0.02679,"peak_contact_force":0.50338,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":109.0,"raw_peak_contact_force":85.72898,"tcp_end":[0.50384,-0.07977,0.12678],"tcp_start":[0.50445,-0.0869,0.03563],"tcp_to_object_dist_end":0.12367,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.57542,"average_solve_count":179.0,"average_success_count":179.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.lateral_offset_x":-0.00798,"approach_1.lateral_offset_y":0.00859,"approach_1.speed":0.08582,"contact_1.contact_force_threshold":7.72268,"push_1.push_depth":0.08278,"push_1.speed":0.06529,"retract_1.retract_height":0.06256,"retract_1.speed":0.05309},"optimized_scores":{"best_composite_score":0.32276,"best_fitness_score":0.61276,"best_task_score":0.33619},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_base_body","contact_count":334.0,"contact_point_centroid":[0.50066,-0.10018,0.065],"force_p95":248.99278,"geom_a":"pusher_tip","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":257.91956,"mean_force":226.65142,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49672,-0.08773,0.03579]},{"body_a":"attachment","body_b":"peg","contact_count":377.0,"contact_point_centroid":[0.50764,0.08741,0.05011],"force_p95":180.92373,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":218.03372,"mean_force":136.08811,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49819,0.0851,0.04844]},{"body_a":"attachment","body_b":"peg","contact_count":131.0,"contact_point_centroid":[0.49637,0.13047,0.05156],"force_p95":193.41678,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":208.05682,"mean_force":119.1835,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48762,0.13785,0.05087]},{"body_a":"peg","body_b":"channel_base_body","contact_count":303.0,"contact_point_centroid":[0.49696,0.11936,0.00847],"force_p95":152.057,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":200.7951,"mean_force":49.15386,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48523,0.14595,0.06997]},{"body_a":"peg","body_b":"channel_base_body","contact_count":993.0,"contact_point_centroid":[0.50159,0.06192,0.00769],"force_p95":167.8382,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":199.36398,"mean_force":51.79831,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49654,-0.00696,0.04136]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.4992,0.12606,0.0471],"force_p95":105.75654,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":105.75654,"mean_force":105.75654,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49188,0.13503,0.04463]},{"body_a":"attachment","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.50349,-0.10002,0.065],"force_p95":96.43787,"geom_a":"pusher_tip","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":96.43787,"mean_force":96.43787,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49937,-0.08691,0.0352]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.51884,0.11937,0.00556],"force_p95":88.51231,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":88.51231,"mean_force":88.51231,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49188,0.13503,0.04463]},{"body_a":"peg","body_b":"world","contact_count":21.0,"contact_point_centroid":[0.50239,0.13077,-0.00027],"force_p95":70.39946,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":83.14567,"mean_force":32.77673,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49234,0.13605,0.04495]},{"body_a":"peg","body_b":"world","contact_count":35.0,"contact_point_centroid":[0.50084,0.13081,-0.00018],"force_p95":45.05755,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":45.97548,"mean_force":27.33702,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49079,0.13577,0.04587]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":219.0,"contact_point_centroid":[0.52519,0.0924,0.04451],"force_p95":19.39189,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":42.03473,"mean_force":11.62668,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49865,0.08617,0.04917]},{"body_a":"peg","body_b":"world","contact_count":1.0,"contact_point_centroid":[0.50205,0.13076,-0.00027],"force_p95":20.35627,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.35627,"mean_force":20.35627,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49188,0.13503,0.04463]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":21.0,"contact_point_centroid":[0.47499,0.02504,0.02407],"force_p95":6.74438,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.17487,"mean_force":3.72709,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49511,-0.05516,0.03728]},{"body_a":"peg","body_b":"channel_base_body","contact_count":340.0,"contact_point_centroid":[0.49639,0.11903,0.00939],"force_p95":0.63431,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.56429,"phase_index":0.0,"phase_name":"align_1","phase_type":"approach","tcp_position_centroid":[0.49175,0.1803,0.19941]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"align_1","phase_type":"approach","tcp_position_centroid":[0.49959,0.19904,0.2964]},{"body_a":"peg","body_b":"channel_base_body","contact_count":28.0,"contact_point_centroid":[0.49774,0.04717,0.00804],"force_p95":0.68337,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.68338,"mean_force":0.60857,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49832,-0.08601,0.03892]}],"total_contact_groups":16},"final_pose_error":0.04945,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49743,0.04537,0.02413],"final_tcp_position":[0.49752,-0.08523,0.04837],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":257.91956,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":365.0,"n_steps_budget":1000.0,"object_pos_end":[0.49602,0.11913,0.03403],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19926,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.57183,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":364.0,"raw_peak_contact_force":2.24822,"subtask_id":"approach","tcp_end":[0.48515,0.16278,0.10959],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08793,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":303.0,"n_steps_budget":630.0,"object_pos_end":[0.50201,0.11644,0.02673],"object_pos_start":[0.49602,0.11913,0.03403],"object_to_goal_dist_end":0.1969,"object_to_goal_dist_start":0.19926,"object_z_max":0.03406,"peak_contact_force":139.33324,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":469.0,"raw_peak_contact_force":208.05682,"subtask_id":"contact","tcp_end":[0.49188,0.13503,0.04463],"tcp_start":[0.48515,0.16278,0.10959],"tcp_to_object_dist_end":0.02772,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.50202,0.11642,0.02671],"object_pos_start":[0.50201,0.11644,0.02673],"object_to_goal_dist_end":0.19688,"object_to_goal_dist_start":0.1969,"object_z_max":0.02673,"peak_contact_force":105.75654,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3.0,"raw_peak_contact_force":105.75654,"tcp_end":[0.49193,0.13501,0.04462],"tcp_start":[0.49188,0.13503,0.04463],"tcp_to_object_dist_end":0.02771,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49741,0.04544,0.02412],"object_pos_start":[0.50202,0.11642,0.02671],"object_to_goal_dist_end":0.12647,"object_to_goal_dist_start":0.19688,"object_z_max":0.03958,"peak_contact_force":248.87463,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1965.0,"raw_peak_contact_force":257.91956,"subtask_id":"push","tcp_end":[0.49937,-0.08691,0.0352],"tcp_start":[0.49193,0.13501,0.04462],"tcp_to_object_dist_end":0.13282,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":28.0,"n_steps_budget":750.0,"object_pos_end":[0.49743,0.04537,0.02413],"object_pos_start":[0.49741,0.04544,0.02412],"object_to_goal_dist_end":0.1264,"object_to_goal_dist_start":0.12647,"object_z_max":0.02413,"peak_contact_force":0.68338,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":29.0,"raw_peak_contact_force":96.43787,"tcp_end":[0.49752,-0.08523,0.04837],"tcp_start":[0.49937,-0.08691,0.0352],"tcp_to_object_dist_end":0.13283,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```