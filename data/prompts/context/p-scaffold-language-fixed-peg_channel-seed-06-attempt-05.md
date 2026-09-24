## Search State

- **Seed**: 6
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | 0.4079 | 0.57 | ❌ rejected |
| 4 | approach → align → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 10 | -0.3377 | 0.19 | ❌ rejected |
| 3 | approach → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 10 | -0.1649 | 0.21 | ❌ rejected |
| 2 | approach → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | 0.4631 | 0.73 | ✅ accepted |
| 1 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.3601 | 0.73 | ✅ accepted |

**Proposal policy**: task_score is 0.57 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.408) — your mutation base

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

- **Composite score**: 0.408
- **task_score** (E): 0.575
- **fitness_score**: 0.698  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.490

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_1 | 1.00 | 1.00 | 0.2005 |
| approach_1 | 1.00 | 0.67 | 0.0712 |
| contact_1 | 1.00 | 1.00 | 0.0008 |
| push_1 | 0.00 | 1.00 | 0.2013 |
| retract_1 | 1.00 | 1.00 | 0.1070 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.497, 0.145, 0.108) | (0.500, 0.099, 0.040)→(0.501, 0.099, 0.034) | 0.180→0.180 | 1.00 / 1.000 | 0.560 | 2.127 |
| approach_1 | approach | 1.00 / step_budget | (0.497, 0.145, 0.108)→(0.506, 0.114, 0.045) | (0.501, 0.099, 0.034)→(0.504, 0.083, 0.032) | 0.180→0.163 | 0.67 / 2.000 | 108.644 | 190.452 |
| contact_1 | contact | 1.00 / force_exceeded | (0.506, 0.114, 0.045)→(0.505, 0.114, 0.044) | (0.504, 0.083, 0.032)→(0.504, 0.080, 0.029) | 0.163→0.160 | 1.00 / 2.333 | 90.540 | 90.540 |
| push_1 | push | 0.00 / step_budget | (0.505, 0.114, 0.044)→(0.504, -0.087, 0.038) | (0.504, 0.080, 0.029)→(0.499, 0.003, 0.025) | 0.160→0.087 | 1.00 / 3.000 | 246.953 | 271.430 |
| retract_1 | retract | 1.00 / step_budget | (0.504, -0.087, 0.038)→(0.503, -0.079, 0.145) | (0.499, 0.003, 0.025)→(0.500, 0.003, 0.024) | 0.087→0.087 | 1.00 / 1.000 | 0.674 | 98.638 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.886
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.886
- phase_score: 0.771
- phase_breakdown.push_score: 0.788
- phase_breakdown.approach_score: 0.610
- phase_breakdown.contact_score: 0.882

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.817
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.886
- **Median Q (composite search score)**: 0.374
- **K-run variance**: 0.0075
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.332


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.84244,"average_solve_count":311.0,"average_success_count":311.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.lateral_offset_x":0.00509,"approach_1.lateral_offset_y":0.01,"approach_1.speed":0.01948,"contact_1.contact_force_threshold":2.33782,"push_1.push_depth":0.13982,"push_1.speed":0.09763,"retract_1.retract_height":0.14242,"retract_1.speed":0.01873},"optimized_scores":{"best_composite_score":0.5271,"best_fitness_score":0.8171,"best_task_score":0.88603},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_base_body","contact_count":269.0,"contact_point_centroid":[0.51146,-0.10025,0.06499],"force_p95":252.79778,"geom_a":"pusher_tip","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":311.6211,"mean_force":209.3336,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50788,-0.08751,0.03951]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":45.0,"contact_point_centroid":[0.52503,-0.08788,0.06],"force_p95":270.09278,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":282.9168,"mean_force":148.71422,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51005,-0.08671,0.03978]},{"body_a":"peg","body_b":"channel_base_body","contact_count":555.0,"contact_point_centroid":[0.50289,-0.10237,0.04073],"force_p95":168.31137,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":170.44355,"mean_force":110.98541,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50374,-0.0595,0.03758]},{"body_a":"attachment","body_b":"peg","contact_count":827.0,"contact_point_centroid":[0.50142,-0.06201,0.04253],"force_p95":167.38436,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":170.02941,"mean_force":94.66138,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50398,-0.05305,0.03759]},{"body_a":"peg","body_b":"channel_base_body","contact_count":324.0,"contact_point_centroid":[0.50722,0.06839,0.00907],"force_p95":139.5526,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":143.41817,"mean_force":32.84222,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50185,0.09933,0.0724]},{"body_a":"attachment","body_b":"peg","contact_count":104.0,"contact_point_centroid":[0.51265,0.08069,0.05514],"force_p95":142.60312,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":142.95097,"mean_force":100.73884,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50559,0.0898,0.05458]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":9.0,"contact_point_centroid":[0.52505,-0.08756,0.05999],"force_p95":86.17395,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":123.49116,"mean_force":17.07659,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50997,-0.08635,0.03998]},{"body_a":"peg","body_b":"channel_base_body","contact_count":829.0,"contact_point_centroid":[0.49809,-0.07632,0.00908],"force_p95":88.2294,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":97.69619,"mean_force":23.57205,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50404,-0.04125,0.03758]},{"body_a":"attachment","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.51377,-0.10003,0.065],"force_p95":93.09092,"geom_a":"pusher_tip","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":93.09092,"mean_force":93.09092,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50991,-0.08663,0.03988]},{"body_a":"attachment","body_b":"peg","contact_count":18.0,"contact_point_centroid":[0.49833,-0.08889,0.04217],"force_p95":61.29897,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":74.31816,"mean_force":21.20452,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50976,-0.08602,0.04034]},{"body_a":"peg","body_b":"channel_base_body","contact_count":134.0,"contact_point_centroid":[0.49462,-0.07628,0.00841],"force_p95":24.71024,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":62.7958,"mean_force":4.63977,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50851,-0.07994,0.07577]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":41.0,"contact_point_centroid":[0.47463,-0.0757,0.0259],"force_p95":27.61328,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":30.03507,"mean_force":11.58679,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50902,-0.08475,0.04328]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":58.0,"contact_point_centroid":[0.47481,-0.07455,0.02577],"force_p95":16.36743,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.64678,"mean_force":10.38009,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50826,-0.07032,0.03904]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":9.0,"contact_point_centroid":[0.52524,-0.01546,0.02708],"force_p95":16.12568,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.24494,"mean_force":8.25589,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50126,0.04618,0.03551]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.50302,-0.00654,0.00951],"force_p95":3.95744,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.95744,"mean_force":3.95744,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50554,0.08182,0.04066]},{"body_a":"peg","body_b":"channel_base_body","contact_count":385.0,"contact_point_centroid":[0.50304,0.06739,0.00932],"force_p95":0.61054,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.56899,"phase_index":0.0,"phase_name":"align_1","phase_type":"approach","tcp_position_centroid":[0.49942,0.15735,0.20055]}],"total_contact_groups":16},"final_pose_error":0.04983,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49817,-0.0743,0.02403],"final_tcp_position":[0.50898,-0.07891,0.13308],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":311.6211,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":401.0,"n_steps_budget":1000.0,"object_pos_end":[0.50302,0.06748,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14764,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54683,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":385.0,"raw_peak_contact_force":2.06903,"subtask_id":"approach","tcp_end":[0.49999,0.1165,0.10729],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08839,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":342.0,"n_steps_budget":1000.0,"object_pos_end":[0.50405,0.02526,0.03775],"object_pos_start":[0.50302,0.06748,0.0338],"object_to_goal_dist_end":0.10536,"object_to_goal_dist_start":0.14764,"object_z_max":0.04113,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":428.0,"raw_peak_contact_force":143.41817,"subtask_id":"contact","tcp_end":[0.50654,0.08311,0.04191],"tcp_start":[0.49999,0.1165,0.10729],"tcp_to_object_dist_end":0.05805,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":11.0,"n_steps_budget":600.0,"object_pos_end":[0.50376,0.0146,0.02997],"object_pos_start":[0.50405,0.02526,0.03775],"object_to_goal_dist_end":0.09521,"object_to_goal_dist_start":0.10536,"object_z_max":0.03775,"peak_contact_force":3.95744,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1.0,"raw_peak_contact_force":3.95744,"tcp_end":[0.50547,0.08167,0.04057],"tcp_start":[0.50654,0.08311,0.04191],"tcp_to_object_dist_end":0.06793,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49234,-0.07456,0.0256],"object_pos_start":[0.50376,0.0146,0.02997],"object_to_goal_dist_end":0.0172,"object_to_goal_dist_start":0.09521,"object_z_max":0.0305,"peak_contact_force":282.61063,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2592.0,"raw_peak_contact_force":311.6211,"subtask_id":"push","tcp_end":[0.50991,-0.08663,0.03988],"tcp_start":[0.50547,0.08167,0.04057],"tcp_to_object_dist_end":0.02566,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":134.0,"n_steps_budget":1000.0,"object_pos_end":[0.49817,-0.0743,0.02403],"object_pos_start":[0.49234,-0.07456,0.0256],"object_to_goal_dist_end":0.01705,"object_to_goal_dist_start":0.0172,"object_z_max":0.02629,"peak_contact_force":0.76948,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":203.0,"raw_peak_contact_force":123.49116,"tcp_end":[0.50898,-0.07891,0.13308],"tcp_start":[0.50991,-0.08663,0.03988],"tcp_to_object_dist_end":0.10968,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.17597,"average_solve_count":233.0,"average_success_count":233.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.lateral_offset_x":-0.00287,"approach_1.lateral_offset_y":0.00942,"approach_1.speed":0.04441,"contact_1.contact_force_threshold":9.04608,"push_1.push_depth":0.14509,"push_1.speed":0.04348,"retract_1.retract_height":0.15751,"retract_1.speed":0.05023},"optimized_scores":{"best_composite_score":0.37407,"best_fitness_score":0.66407,"best_task_score":0.46706},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":618.0,"contact_point_centroid":[0.51999,0.08607,0.05281],"force_p95":169.58316,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":246.66338,"mean_force":134.43459,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51218,0.08267,0.05076]},{"body_a":"peg","body_b":"channel_base_body","contact_count":992.0,"contact_point_centroid":[0.5119,0.06709,0.00813],"force_p95":163.09798,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":220.92647,"mean_force":84.0692,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50881,0.03162,0.04666]},{"body_a":"attachment","body_b":"channel_base_body","contact_count":112.0,"contact_point_centroid":[0.50449,-0.10027,0.065],"force_p95":216.06653,"geom_a":"pusher_tip","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":220.91165,"mean_force":192.78882,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50166,-0.08829,0.03846]},{"body_a":"attachment","body_b":"peg","contact_count":227.0,"contact_point_centroid":[0.51594,0.12417,0.05292],"force_p95":196.49766,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":208.87831,"mean_force":151.34242,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50584,0.13034,0.05147]},{"body_a":"peg","body_b":"channel_base_body","contact_count":402.0,"contact_point_centroid":[0.51118,0.11628,0.00856],"force_p95":193.17118,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":204.36758,"mean_force":85.76232,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50421,0.13711,0.06567]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":434.0,"contact_point_centroid":[0.52502,0.08702,0.06],"force_p95":114.36854,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":175.65493,"mean_force":85.48678,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51228,0.0874,0.05111]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.52024,0.11994,0.00743],"force_p95":133.72285,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":133.72285,"mean_force":133.72285,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.51246,0.12744,0.04804]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.52181,0.12006,0.05096],"force_p95":124.33234,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":124.33234,"mean_force":124.33234,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.51246,0.12744,0.04804]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":152.0,"contact_point_centroid":[0.52514,0.09511,0.05269],"force_p95":51.47379,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":121.07153,"mean_force":14.43366,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51161,0.09981,0.04941]},{"body_a":"attachment","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.50467,-0.10003,0.065],"force_p95":76.02908,"geom_a":"pusher_tip","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":78.60073,"mean_force":57.48435,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5018,-0.08765,0.03831]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":87.0,"contact_point_centroid":[0.52526,0.10964,0.05442],"force_p95":19.84169,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.17582,"mean_force":10.13062,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50959,0.12822,0.04879]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.52539,0.10907,0.05519],"force_p95":14.73545,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.73545,"mean_force":14.73545,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.51246,0.12744,0.04804]},{"body_a":"peg","body_b":"channel_base_body","contact_count":350.0,"contact_point_centroid":[0.50351,0.11176,0.00934],"force_p95":0.6343,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.56822,"phase_index":0.0,"phase_name":"align_1","phase_type":"approach","tcp_position_centroid":[0.50263,0.17712,0.19971]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":5.0,"contact_point_centroid":[0.47495,0.06066,0.02551],"force_p95":0.81206,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.84049,"mean_force":0.60035,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50574,-0.00384,0.04203]},{"body_a":"peg","body_b":"channel_base_body","contact_count":131.0,"contact_point_centroid":[0.50532,0.03727,0.00804],"force_p95":0.68347,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.68382,"mean_force":0.60594,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50077,-0.07984,0.08621]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"align_1","phase_type":"approach","tcp_position_centroid":[0.49997,0.19934,0.29835]}],"total_contact_groups":16},"final_pose_error":0.04953,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50551,0.03705,0.02413],"final_tcp_position":[0.50127,-0.07949,0.14697],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":246.66338,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":372.0,"n_steps_budget":1000.0,"object_pos_end":[0.50375,0.11176,0.0338],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.1919,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.56268,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":366.0,"raw_peak_contact_force":2.06328,"subtask_id":"approach","tcp_end":[0.50616,0.15629,0.10861],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08709,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":402.0,"n_steps_budget":1000.0,"object_pos_end":[0.50755,0.10824,0.03038],"object_pos_start":[0.50375,0.11176,0.0338],"object_to_goal_dist_end":0.18864,"object_to_goal_dist_start":0.1919,"object_z_max":0.03388,"peak_contact_force":192.65467,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":716.0,"raw_peak_contact_force":208.87831,"subtask_id":"contact","tcp_end":[0.51246,0.12744,0.04804],"tcp_start":[0.50616,0.15629,0.10861],"tcp_to_object_dist_end":0.02655,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.50754,0.10824,0.03039],"object_pos_start":[0.50755,0.10824,0.03038],"object_to_goal_dist_end":0.18863,"object_to_goal_dist_start":0.18864,"object_z_max":0.03038,"peak_contact_force":133.72285,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3.0,"raw_peak_contact_force":133.72285,"tcp_end":[0.51253,0.12743,0.04807],"tcp_start":[0.51246,0.12744,0.04804],"tcp_to_object_dist_end":0.02657,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50544,0.03706,0.02413],"object_pos_start":[0.50754,0.10824,0.03039],"object_to_goal_dist_end":0.11826,"object_to_goal_dist_start":0.18863,"object_z_max":0.03988,"peak_contact_force":210.66068,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2313.0,"raw_peak_contact_force":246.66338,"subtask_id":"push","tcp_end":[0.5018,-0.08769,0.03832],"tcp_start":[0.51253,0.12743,0.04807],"tcp_to_object_dist_end":0.12561,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":131.0,"n_steps_budget":1000.0,"object_pos_end":[0.50551,0.03705,0.02413],"object_pos_start":[0.50544,0.03706,0.02413],"object_to_goal_dist_end":0.11825,"object_to_goal_dist_start":0.11826,"object_z_max":0.02413,"peak_contact_force":0.6834,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":134.0,"raw_peak_contact_force":78.60073,"tcp_end":[0.50127,-0.07949,0.14697],"tcp_start":[0.5018,-0.08769,0.03832],"tcp_to_object_dist_end":0.16938,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.43802,"average_solve_count":242.0,"average_success_count":242.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.lateral_offset_x":-0.00299,"approach_1.lateral_offset_y":0.00673,"approach_1.speed":0.07268,"contact_1.contact_force_threshold":12.66886,"push_1.push_depth":0.09077,"push_1.speed":0.06406,"retract_1.retract_height":0.16726,"retract_1.speed":0.04068},"optimized_scores":{"best_composite_score":0.32247,"best_fitness_score":0.61247,"best_task_score":0.37187},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_base_body","contact_count":329.0,"contact_point_centroid":[0.50142,-0.10019,0.065],"force_p95":245.33411,"geom_a":"pusher_tip","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":256.00452,"mean_force":222.86886,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49761,-0.08779,0.03612]},{"body_a":"attachment","body_b":"peg","contact_count":383.0,"contact_point_centroid":[0.51257,0.08676,0.0512],"force_p95":195.08931,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":230.80981,"mean_force":138.07885,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50373,0.0838,0.04937]},{"body_a":"peg","body_b":"channel_base_body","contact_count":993.0,"contact_point_centroid":[0.50527,0.06137,0.00791],"force_p95":169.34428,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":225.86734,"mean_force":53.53561,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49966,-0.00652,0.04193]},{"body_a":"attachment","body_b":"peg","contact_count":154.0,"contact_point_centroid":[0.5009,0.12902,0.05149],"force_p95":213.34006,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":219.05981,"mean_force":126.33382,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49195,0.13628,0.05066]},{"body_a":"peg","body_b":"channel_base_body","contact_count":333.0,"contact_point_centroid":[0.49903,0.11935,0.00837],"force_p95":184.186,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":211.49361,"mean_force":57.04267,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48809,0.14453,0.06886]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50594,0.12476,0.0472],"force_p95":133.94086,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":133.94086,"mean_force":133.94086,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49753,0.13288,0.04475]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.51796,0.11953,0.00554],"force_p95":122.94897,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":122.94897,"mean_force":122.94897,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49753,0.13288,0.04475]},{"body_a":"attachment","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.50382,-0.10002,0.065],"force_p95":93.82223,"geom_a":"pusher_tip","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":93.82223,"mean_force":93.82223,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49984,-0.08697,0.0356]},{"body_a":"peg","body_b":"world","contact_count":14.0,"contact_point_centroid":[0.50147,0.13109,-0.0002],"force_p95":70.68184,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":75.48821,"mean_force":26.38053,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49761,0.13421,0.0449]},{"body_a":"peg","body_b":"world","contact_count":36.0,"contact_point_centroid":[0.50044,0.13109,-3e-05],"force_p95":24.02631,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":24.44753,"mean_force":19.89348,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49615,0.13368,0.04562]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":110.0,"contact_point_centroid":[0.52506,0.086,0.05445],"force_p95":14.59824,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.47222,"mean_force":10.39607,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50524,0.0662,0.05035]},{"body_a":"peg","body_b":"world","contact_count":1.0,"contact_point_centroid":[0.50139,0.13112,-9e-05],"force_p95":14.01579,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.01579,"mean_force":14.01579,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49753,0.13288,0.04475]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":23.0,"contact_point_centroid":[0.47487,0.02315,0.02577],"force_p95":9.8518,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.93885,"mean_force":3.03065,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49722,0.00254,0.04019]},{"body_a":"peg","body_b":"channel_base_body","contact_count":340.0,"contact_point_centroid":[0.49639,0.11903,0.00939],"force_p95":0.63431,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.56429,"phase_index":0.0,"phase_name":"align_1","phase_type":"approach","tcp_position_centroid":[0.49175,0.1803,0.19941]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"align_1","phase_type":"approach","tcp_position_centroid":[0.49959,0.19904,0.2964]},{"body_a":"peg","body_b":"channel_base_body","contact_count":145.0,"contact_point_centroid":[0.49675,0.04535,0.00807],"force_p95":0.6436,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.6436,"mean_force":0.60568,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49869,-0.07844,0.08692]}],"total_contact_groups":16},"final_pose_error":0.04976,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49533,0.04568,0.02415],"final_tcp_position":[0.49934,-0.07828,0.15386],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":256.00452,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":365.0,"n_steps_budget":1000.0,"object_pos_end":[0.49602,0.11913,0.03403],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19926,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.57183,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":364.0,"raw_peak_contact_force":2.24822,"subtask_id":"approach","tcp_end":[0.48515,0.16278,0.10959],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08793,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":333.0,"n_steps_budget":750.0,"object_pos_end":[0.50131,0.11587,0.02659],"object_pos_start":[0.49602,0.11913,0.03403],"object_to_goal_dist_end":0.19633,"object_to_goal_dist_start":0.19926,"object_z_max":0.03406,"peak_contact_force":133.27707,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":523.0,"raw_peak_contact_force":219.05981,"subtask_id":"contact","tcp_end":[0.49753,0.13288,0.04475],"tcp_start":[0.48515,0.16278,0.10959],"tcp_to_object_dist_end":0.02517,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.50131,0.11585,0.02656],"object_pos_start":[0.50131,0.11587,0.02659],"object_to_goal_dist_end":0.19631,"object_to_goal_dist_start":0.19633,"object_z_max":0.02659,"peak_contact_force":133.94086,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3.0,"raw_peak_contact_force":133.94086,"tcp_end":[0.49755,0.13285,0.04474],"tcp_start":[0.49753,0.13288,0.04475],"tcp_to_object_dist_end":0.02517,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49812,0.04538,0.02415],"object_pos_start":[0.50131,0.11585,0.02656],"object_to_goal_dist_end":0.12639,"object_to_goal_dist_start":0.19631,"object_z_max":0.03959,"peak_contact_force":247.58769,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1852.0,"raw_peak_contact_force":256.00452,"subtask_id":"push","tcp_end":[0.49984,-0.08697,0.0356],"tcp_start":[0.49755,0.13285,0.04474],"tcp_to_object_dist_end":0.13286,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":145.0,"n_steps_budget":1000.0,"object_pos_end":[0.49533,0.04568,0.02415],"object_pos_start":[0.49812,0.04538,0.02415],"object_to_goal_dist_end":0.12676,"object_to_goal_dist_start":0.12639,"object_z_max":0.02415,"peak_contact_force":0.56827,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":146.0,"raw_peak_contact_force":93.82223,"tcp_end":[0.49934,-0.07828,0.15386],"tcp_start":[0.49984,-0.08697,0.0356],"tcp_to_object_dist_end":0.17946,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```