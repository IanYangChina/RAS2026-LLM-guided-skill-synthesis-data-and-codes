## Search State

- **Seed**: 4
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | 0.2373 | 0.55 | ❌ rejected |
| 9 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 10 | -0.2300 | 0.00 | ❌ rejected |
| 8 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 10 | -0.1387 | 0.21 | ❌ rejected |
| 7 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | 0.2661 | 0.58 | ✅ accepted |
| 6 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | 0.2699 | 0.58 | ✅ accepted |

**Proposal policy**: task_score is 0.55 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.237) — your mutation base

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

- **Composite score**: 0.237
- **task_score** (E): 0.549
- **fitness_score**: 0.527  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.490

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_1 | 1.00 | 1.00 | 0.2398 |
| approach_1 | 1.00 | 1.00 | 0.0383 |
| contact_1 | 1.00 | 1.00 | 0.0003 |
| push_1 | 0.33 | 1.00 | 0.1626 |
| retract_1 | 1.00 | 1.00 | 0.0939 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_1 | align | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.516, 0.144, 0.068) | (0.521, 0.084, 0.040)→(0.505, 0.084, 0.034) | 0.166→0.165 | 1.00 / 1.000 | 0.545 | 3.242 |
| approach_1 | approach | 1.00 / step_budget | (0.516, 0.144, 0.068)→(0.504, 0.129, 0.037) | (0.505, 0.084, 0.034)→(0.505, 0.084, 0.034) | 0.165→0.165 | 1.00 / 2.000 | 221.305 | 251.834 |
| contact_1 | contact | 1.00 / force_exceeded | (0.504, 0.129, 0.037)→(0.504, 0.128, 0.037) | (0.505, 0.084, 0.034)→(0.505, 0.084, 0.034) | 0.165→0.165 | 1.00 / 2.000 | 59.035 | 64.784 |
| push_1 | push | 0.33 / step_budget | (0.504, 0.128, 0.037)→(0.499, -0.034, 0.037) | (0.505, 0.084, 0.034)→(0.506, -0.064, 0.036) | 0.165→0.022 | 1.00 / 2.333 | 85.046 | 163.068 |
| retract_1 | retract | 1.00 / step_budget | (0.499, -0.034, 0.037)→(0.496, -0.029, 0.130) | (0.506, -0.064, 0.036)→(0.506, -0.064, 0.034) | 0.022→0.022 | 1.00 / 1.000 | 0.545 | 69.600 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.919
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.919
- phase_score: 0.633
- phase_breakdown.push_score: 0.561
- phase_breakdown.contact_score: 0.611
- phase_breakdown.approach_score: 0.872

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.748
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.919
- **Median Q (composite search score)**: 0.149
- **K-run variance**: 0.0246
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.396


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.44099,"average_solve_count":161.0,"average_success_count":161.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_y":0.00098,"approach_1.approach_z_offset":0.00907,"contact_1.contact_force":13.27405,"contact_1.speed":0.01777,"push_1.push_depth":0.01728,"push_1.push_speed":0.09859,"retract_1.retract_height":0.10879,"retract_1.speed":0.05141},"optimized_scores":{"best_composite_score":0.14925,"best_fitness_score":0.43925,"best_task_score":0.28787},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":22.0,"contact_point_centroid":[0.52501,0.12,0.06],"force_p95":88.39066,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":88.66196,"mean_force":68.78237,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50449,0.12357,0.04116]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":2.0,"contact_point_centroid":[0.525,0.12,0.06],"force_p95":75.00703,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":75.86932,"mean_force":67.24637,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50612,0.12565,0.04265]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":214.0,"contact_point_centroid":[0.54396,-0.00775,0.06],"force_p95":61.6335,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":72.46306,"mean_force":45.58594,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4992,-0.00512,0.03691]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.52501,0.11999,0.06],"force_p95":64.15626,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":67.14748,"mean_force":54.25782,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50897,0.12763,0.04531]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.54321,-0.04737,0.06],"force_p95":58.75684,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":59.29025,"mean_force":53.95614,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49852,-0.05146,0.03678]},{"body_a":"peg","body_b":"channel_base_body","contact_count":639.0,"contact_point_centroid":[0.50604,-0.00897,0.00983],"force_p95":14.24013,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.05336,"mean_force":5.87864,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50018,0.03549,0.03735]},{"body_a":"attachment","body_b":"peg","contact_count":713.0,"contact_point_centroid":[0.50437,0.01286,0.04273],"force_p95":13.83964,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.92893,"mean_force":4.95187,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49972,0.02461,0.03697]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":308.0,"contact_point_centroid":[0.52505,-0.00077,0.02266],"force_p95":3.48218,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.27282,"mean_force":0.91042,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49977,0.02759,0.03697]},{"body_a":"peg","body_b":"channel_base_body","contact_count":722.0,"contact_point_centroid":[0.50579,0.08089,0.00936],"force_p95":0.55347,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.5679,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.5144,0.17083,0.17869]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49997,0.19874,0.29562]},{"body_a":"peg","body_b":"channel_base_body","contact_count":29.0,"contact_point_centroid":[0.50606,-0.10015,0.05937],"force_p95":1.80292,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.86767,"mean_force":0.25978,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49695,-0.05014,0.0393]},{"body_a":"attachment","body_b":"peg","contact_count":9.0,"contact_point_centroid":[0.50483,-0.0632,0.04935],"force_p95":1.73914,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.74514,"mean_force":0.68666,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49791,-0.05134,0.03729]},{"body_a":"peg","body_b":"channel_base_body","contact_count":990.0,"contact_point_centroid":[0.50544,-0.08166,0.00939],"force_p95":0.55652,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.05042,"mean_force":0.54993,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49491,-0.04324,0.08394]},{"body_a":"peg","body_b":"channel_base_body","contact_count":194.0,"contact_point_centroid":[0.5059,0.08073,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55006,"mean_force":0.54677,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51717,0.13434,0.05369]},{"body_a":"peg","body_b":"channel_base_body","contact_count":8.0,"contact_point_centroid":[0.50411,0.08414,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55006,"mean_force":0.54699,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50612,0.12567,0.04267]}],"total_contact_groups":15},"final_pose_error":0.01521,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50554,-0.08169,0.03379],"final_tcp_position":[0.49515,-0.04774,0.1312],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":88.66196,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":751.0,"n_steps_budget":1000.0,"object_pos_end":[0.50597,0.08086,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16109,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54611,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":758.0,"raw_peak_contact_force":4.32595,"tcp_end":[0.52966,0.14407,0.06762],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07551,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":194.0,"n_steps_budget":600.0,"object_pos_end":[0.50596,0.08089,0.03378],"object_pos_start":[0.50597,0.08086,0.03378],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16109,"object_z_max":0.03378,"peak_contact_force":48.4936,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":228.0,"raw_peak_contact_force":67.14748,"tcp_end":[0.50636,0.1258,0.04296],"tcp_start":[0.52966,0.14407,0.06762],"tcp_to_object_dist_end":0.04585,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":8.0,"n_steps_budget":930.0,"object_pos_end":[0.50599,0.08089,0.03378],"object_pos_start":[0.50596,0.08089,0.03378],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16112,"object_z_max":0.03378,"peak_contact_force":58.62342,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":10.0,"raw_peak_contact_force":75.86932,"tcp_end":[0.50582,0.12545,0.04223],"tcp_start":[0.50636,0.1258,0.04296],"tcp_to_object_dist_end":0.04536,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50684,-0.08016,0.03677],"object_pos_start":[0.50599,0.08089,0.03378],"object_to_goal_dist_end":0.00757,"object_to_goal_dist_start":0.16112,"object_z_max":0.03687,"peak_contact_force":57.74349,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1896.0,"raw_peak_contact_force":88.66196,"tcp_end":[0.49852,-0.05139,0.03678],"tcp_start":[0.50582,0.12545,0.04223],"tcp_to_object_dist_end":0.02995,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50554,-0.08169,0.03379],"object_pos_start":[0.50684,-0.08016,0.03677],"object_to_goal_dist_end":0.0085,"object_to_goal_dist_start":0.00757,"object_z_max":0.03677,"peak_contact_force":0.54001,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1030.0,"raw_peak_contact_force":59.29025,"tcp_end":[0.49515,-0.04774,0.1312],"tcp_start":[0.49852,-0.05139,0.03678],"tcp_to_object_dist_end":0.10369,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.8371,"average_solve_count":221.0,"average_success_count":221.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_y":-0.00623,"approach_1.approach_z_offset":-0.01038,"contact_1.contact_force":6.48528,"contact_1.speed":0.01025,"push_1.push_depth":0.02177,"push_1.push_speed":0.09955,"retract_1.retract_height":0.09274,"retract_1.speed":0.01037},"optimized_scores":{"best_composite_score":0.10498,"best_fitness_score":0.39498,"best_task_score":0.43951},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":63.0,"contact_point_centroid":[0.55499,0.11999,0.05979],"force_p95":391.40146,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":393.04857,"mean_force":325.30958,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50685,0.14844,0.03252]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":756.0,"contact_point_centroid":[0.5478,0.08142,0.05997],"force_p95":237.91585,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":279.49227,"mean_force":127.33462,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50226,0.0868,0.03569]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":665.0,"contact_point_centroid":[0.52503,0.07549,0.05999],"force_p95":211.54737,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":271.20203,"mean_force":135.85062,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50148,0.07685,0.03612]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":5.0,"contact_point_centroid":[0.52501,0.00068,0.05999],"force_p95":85.76687,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":87.94469,"mean_force":57.06028,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5007,0.00062,0.03688]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.555,0.12,0.05995],"force_p95":59.45683,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":59.45683,"mean_force":59.45683,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50751,0.14858,0.03271]},{"body_a":"attachment","body_b":"peg","contact_count":333.0,"contact_point_centroid":[0.50269,0.06105,0.04041],"force_p95":16.63552,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":57.3657,"mean_force":3.26806,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50136,0.07263,0.0362]},{"body_a":"peg","body_b":"channel_base_body","contact_count":819.0,"contact_point_centroid":[0.50187,0.0502,0.0096],"force_p95":5.63842,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":55.14133,"mean_force":1.76216,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50244,0.08937,0.03562]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":127.0,"contact_point_centroid":[0.52517,0.04446,0.04808],"force_p95":1.51412,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":28.18855,"mean_force":0.60569,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5019,0.07619,0.03596]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.5452,-0.0043,0.05999],"force_p95":22.09905,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":22.0992,"mean_force":21.47371,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50046,0.0002,0.03684]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":53.0,"contact_point_centroid":[0.4748,0.03353,0.03443],"force_p95":1.29277,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.92546,"mean_force":0.77593,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50085,0.06705,0.03655]},{"body_a":"peg","body_b":"channel_base_body","contact_count":700.0,"contact_point_centroid":[0.50568,0.10469,0.00937],"force_p95":0.57582,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.5625,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50899,0.17896,0.17975]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49982,0.19907,0.29623]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50595,-0.03163,0.00943],"force_p95":0.60142,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.89923,"mean_force":0.54565,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49703,0.00764,0.07479]},{"body_a":"peg","body_b":"channel_base_body","contact_count":234.0,"contact_point_centroid":[0.50589,0.10464,0.00939],"force_p95":0.57569,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57589,"mean_force":0.54633,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51079,0.15266,0.04573]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.52389,0.10531,0.00939],"force_p95":0.53558,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.53558,"mean_force":0.53558,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50751,0.14858,0.03271]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52518,-0.03282,0.05981],"force_p95":0.33423,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.40034,"mean_force":0.14086,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49815,0.0028,0.0405]}],"total_contact_groups":16},"final_pose_error":0.01606,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50631,-0.03068,0.0341],"final_tcp_position":[0.49714,0.00454,0.11434],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":393.04857,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":727.0,"n_steps_budget":1000.0,"object_pos_end":[0.506,0.10464,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18484,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.54131,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":732.0,"raw_peak_contact_force":3.33087,"tcp_end":[0.51923,0.15969,0.06838],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.06633,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":234.0,"n_steps_budget":600.0,"object_pos_end":[0.50599,0.10464,0.03384],"object_pos_start":[0.506,0.10464,0.03384],"object_to_goal_dist_end":0.18484,"object_to_goal_dist_start":0.18484,"object_z_max":0.03384,"peak_contact_force":351.01068,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":297.0,"raw_peak_contact_force":393.04857,"tcp_end":[0.50751,0.14858,0.03271],"tcp_start":[0.51923,0.15969,0.06838],"tcp_to_object_dist_end":0.04399,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50598,0.1046,0.03384],"object_pos_start":[0.50599,0.10464,0.03384],"object_to_goal_dist_end":0.1848,"object_to_goal_dist_start":0.18484,"object_z_max":0.03384,"peak_contact_force":59.45683,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":59.45683,"tcp_end":[0.50753,0.14858,0.03271],"tcp_start":[0.50751,0.14858,0.03271],"tcp_to_object_dist_end":0.04403,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50456,-0.03002,0.03561],"object_pos_start":[0.50598,0.1046,0.03384],"object_to_goal_dist_end":0.05038,"object_to_goal_dist_start":0.1848,"object_z_max":0.03772,"peak_contact_force":195.40672,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2753.0,"raw_peak_contact_force":279.49227,"tcp_end":[0.50068,0.00098,0.03685],"tcp_start":[0.50753,0.14858,0.03271],"tcp_to_object_dist_end":0.03126,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50631,-0.03068,0.0341],"object_pos_start":[0.50456,-0.03002,0.03561],"object_to_goal_dist_end":0.05007,"object_to_goal_dist_start":0.05038,"object_z_max":0.03676,"peak_contact_force":0.54084,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1040.0,"raw_peak_contact_force":87.94469,"tcp_end":[0.49714,0.00454,0.11434],"tcp_start":[0.50068,0.00098,0.03685],"tcp_to_object_dist_end":0.08811,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.64189,"average_solve_count":148.0,"average_success_count":148.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_y":-0.00092,"approach_1.approach_z_offset":-0.00058,"contact_1.contact_force":19.18218,"contact_1.speed":0.03402,"push_1.push_depth":0.03196,"push_1.push_speed":0.09941,"retract_1.retract_height":0.13993,"retract_1.speed":0.06528},"optimized_scores":{"best_composite_score":0.45766,"best_fitness_score":0.74766,"best_task_score":0.91897},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":63.0,"contact_point_centroid":[0.54314,0.11288,0.05991],"force_p95":284.84738,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":295.30532,"mean_force":227.54852,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49857,0.11143,0.03599]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":709.0,"contact_point_centroid":[0.54374,0.03492,0.05999],"force_p95":109.7282,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":121.05121,"mean_force":92.06224,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49896,0.03649,0.03671]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.54339,-0.04738,0.05999],"force_p95":60.79764,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":61.5661,"mean_force":53.88147,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49876,-0.05155,0.03668]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54364,0.11288,0.05997],"force_p95":59.02485,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":59.02485,"mean_force":59.02485,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49909,0.11145,0.03606]},{"body_a":"peg","body_b":"channel_base_body","contact_count":782.0,"contact_point_centroid":[0.49975,-0.005,0.0096],"force_p95":16.46372,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":30.59888,"mean_force":2.26851,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49897,0.03493,0.03671]},{"body_a":"attachment","body_b":"peg","contact_count":356.0,"contact_point_centroid":[0.50161,0.01768,0.04181],"force_p95":24.24989,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.82634,"mean_force":4.24565,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49895,0.02934,0.03676]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":172.0,"contact_point_centroid":[0.52513,0.01635,0.02955],"force_p95":6.35141,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.74517,"mean_force":1.38277,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49884,0.04551,0.03669]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":136.0,"contact_point_centroid":[0.47483,-0.01719,0.0533],"force_p95":1.78994,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.13371,"mean_force":0.40283,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49919,0.01417,0.03692]},{"body_a":"peg","body_b":"channel_base_body","contact_count":724.0,"contact_point_centroid":[0.50309,0.06747,0.00935],"force_p95":0.55474,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.55853,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49876,0.16415,0.18135]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.5062,-0.08013,0.00941],"force_p95":0.55346,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.87018,"mean_force":0.54466,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49527,-0.04065,0.09063]},{"body_a":"peg","body_b":"channel_base_body","contact_count":319.0,"contact_point_centroid":[0.50292,0.06737,0.00938],"force_p95":0.55058,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55081,"mean_force":0.54664,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49762,0.11835,0.04736]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.49749,0.08447,0.00938],"force_p95":0.55071,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55071,"mean_force":0.55071,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49909,0.11145,0.03606]},{"body_a":"attachment","body_b":"peg","contact_count":15.0,"contact_point_centroid":[0.50562,-0.06237,0.05535],"force_p95":0.42682,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.47244,"mean_force":0.28618,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49723,-0.05036,0.03885]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.50692,-0.10007,0.05981],"force_p95":0.13451,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13451,"mean_force":0.13451,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49878,-0.05117,0.03669]},{"body_a":"peg","body_b":"channel_base_body","contact_count":13.0,"contact_point_centroid":[0.50691,-0.10026,0.05954],"force_p95":0.05459,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.08103,"mean_force":0.01023,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4984,-0.05156,0.03697]}],"total_contact_groups":15},"final_pose_error":0.0323,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50628,-0.07957,0.03378],"final_tcp_position":[0.4955,-0.0427,0.14568],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":295.30532,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":740.0,"n_steps_budget":1000.0,"object_pos_end":[0.50305,0.06742,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14758,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54764,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":724.0,"raw_peak_contact_force":2.06903,"tcp_end":[0.49917,0.12971,0.06836],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07134,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":319.0,"n_steps_budget":600.0,"object_pos_end":[0.50303,0.0675,0.0338],"object_pos_start":[0.50305,0.06742,0.0338],"object_to_goal_dist_end":0.14766,"object_to_goal_dist_start":0.14758,"object_z_max":0.0338,"peak_contact_force":264.41162,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":382.0,"raw_peak_contact_force":295.30532,"tcp_end":[0.49909,0.11145,0.03606],"tcp_start":[0.49917,0.12971,0.06836],"tcp_to_object_dist_end":0.04418,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.50306,0.0675,0.0338],"object_pos_start":[0.50303,0.0675,0.0338],"object_to_goal_dist_end":0.14766,"object_to_goal_dist_start":0.14766,"object_z_max":0.0338,"peak_contact_force":59.02485,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":59.02485,"tcp_end":[0.49911,0.11145,0.03606],"tcp_start":[0.49909,0.11145,0.03606],"tcp_to_object_dist_end":0.04419,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50681,-0.08065,0.03601],"object_pos_start":[0.50306,0.0675,0.0338],"object_to_goal_dist_end":0.00792,"object_to_goal_dist_start":0.14766,"object_z_max":0.03734,"peak_contact_force":1.98807,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2156.0,"raw_peak_contact_force":121.05121,"tcp_end":[0.49878,-0.05136,0.0367],"tcp_start":[0.49911,0.11145,0.03606],"tcp_to_object_dist_end":0.03038,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50628,-0.07957,0.03378],"object_pos_start":[0.50681,-0.08065,0.03601],"object_to_goal_dist_end":0.00885,"object_to_goal_dist_start":0.00792,"object_z_max":0.03601,"peak_contact_force":0.55295,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1030.0,"raw_peak_contact_force":61.5661,"tcp_end":[0.4955,-0.0427,0.14568],"tcp_start":[0.49878,-0.05136,0.0367],"tcp_to_object_dist_end":0.11832,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```