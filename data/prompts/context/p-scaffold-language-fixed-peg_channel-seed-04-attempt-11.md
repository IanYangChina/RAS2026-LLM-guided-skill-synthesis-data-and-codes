## Search State

- **Seed**: 4
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 10 | -0.2346 | 0.00 | ❌ rejected |
| 10 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | 0.2373 | 0.55 | ❌ rejected |
| 9 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 10 | -0.2300 | 0.00 | ❌ rejected |
| 8 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 10 | -0.1387 | 0.21 | ❌ rejected |
| 7 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | 0.2661 | 0.58 | ✅ accepted |

**Proposal policy**: task_score is 0.00 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.235) — your mutation base

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

- **Composite score**: -0.235
- **task_score** (E): 0.000
- **fitness_score**: 0.155  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.590

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_1 | 0.00 | 1.00 | 0.2849 |
| approach_1 | 1.00 | 1.00 | 0.1304 |
| contact_1 | 1.00 | 1.00 | 0.0041 |
| push_1 | 0.00 | 1.00 | 0.0004 |
| retract_1 | 0.67 | 1.00 | 0.0904 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_1 | align | 0.00 / step_budget | (0.500, 0.200, 0.300)→(0.497, -0.014, 0.112) | (0.521, 0.084, 0.040)→(0.505, 0.084, 0.034) | 0.166→0.165 | 1.00 / 1.000 | 0.544 | 3.242 |
| approach_1 | approach | 1.00 / step_budget | (0.497, -0.014, 0.112)→(0.505, 0.098, 0.046) | (0.505, 0.084, 0.034)→(0.505, 0.124, 0.028) | 0.165→0.204 | 1.00 / 1.667 | 60.407 | 210.267 |
| contact_1 | contact | 1.00 / force_exceeded | (0.505, 0.098, 0.046)→(0.503, 0.100, 0.043) | (0.505, 0.124, 0.028)→(0.509, 0.133, 0.021) | 0.204→0.214 | 1.00 / 2.000 | 1352.503 | 51.651 |
| push_1 | push | 0.00 / guard_failure | (0.505, 0.098, 0.042)→(0.505, 0.098, 0.042) | (0.509, 0.133, 0.021)→(0.509, 0.132, 0.022) | 0.214→0.213 | 1.00 / 3.333 | 784.105 | 821.141 |
| retract_1 | retract | 0.67 / step_budget | (0.505, 0.098, 0.042)→(0.502, 0.109, 0.132) | (0.509, 0.132, 0.022)→(0.512, 0.133, 0.023) | 0.213→0.215 | 1.00 / 1.333 | 0.534 | 179.175 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.000
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.000
- phase_score: 0.325
- phase_breakdown.push_score: 0.040
- phase_breakdown.contact_score: 0.930
- phase_breakdown.approach_score: 0.575

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.195
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.000
- **Median Q (composite search score)**: -0.249
- **K-run variance**: 0.0008
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.307


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.72593,"average_solve_count":135.0,"average_success_count":135.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_y":-0.00232,"approach_1.approach_x_offset":-0.00377,"approach_1.approach_z_offset":0.00764,"contact_1.contact_force":12.30236,"contact_1.speed":0.0268,"push_1.push_force_threshold":33.68617,"push_1.push_lateral_x":-0.00586,"push_1.push_speed":0.08371,"retract_1.retract_height":0.1314,"retract_1.speed":0.05473},"optimized_scores":{"best_composite_score":-0.25926,"best_fitness_score":0.13074,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":2.0,"contact_point_centroid":[0.5251,0.09479,0.05996],"force_p95":443.95476,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":444.56301,"mean_force":438.48053,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50843,0.09478,0.05125]},{"body_a":"peg","body_b":"channel_base_body","contact_count":812.0,"contact_point_centroid":[0.50892,0.08234,0.00885],"force_p95":182.81748,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":221.15189,"mean_force":38.16385,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49721,0.03911,0.07653]},{"body_a":"attachment","body_b":"peg","contact_count":275.0,"contact_point_centroid":[0.51251,0.07675,0.05385],"force_p95":198.72442,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":217.50971,"mean_force":111.72631,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50177,0.07505,0.05685]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.5129,0.09033,0.00676],"force_p95":193.36948,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":193.55222,"mean_force":150.5208,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50827,0.09486,0.05127]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.51933,0.09502,0.05005],"force_p95":192.86609,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":193.04958,"mean_force":149.6673,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50827,0.09486,0.05127]},{"body_a":"attachment","body_b":"peg","contact_count":85.0,"contact_point_centroid":[0.51879,0.09803,0.05496],"force_p95":97.45797,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":129.02549,"mean_force":43.80763,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50776,0.09778,0.05822]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50655,0.10436,0.00929],"force_p95":20.73159,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":128.68631,"mean_force":4.30743,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5055,0.10439,0.1017]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.50351,0.08458,0.00683],"force_p95":106.78914,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":106.78914,"mean_force":106.78914,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50792,0.09492,0.05132]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51895,0.09491,0.05014],"force_p95":106.08883,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":106.08883,"mean_force":106.08883,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50792,0.09492,0.05132]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":207.0,"contact_point_centroid":[0.5252,0.09312,0.04641],"force_p95":24.56819,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":54.64732,"mean_force":9.38826,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50262,0.07768,0.05589]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.5252,0.09489,0.05991],"force_p95":36.42069,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":36.84677,"mean_force":32.48343,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50864,0.09479,0.05132]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":9.0,"contact_point_centroid":[0.52507,0.10269,0.05349],"force_p95":13.97762,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.98283,"mean_force":8.21609,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50794,0.09637,0.05361]},{"body_a":"peg","body_b":"channel_base_body","contact_count":971.0,"contact_point_centroid":[0.50581,0.08087,0.00937],"force_p95":0.55064,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.56248,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.4973,0.08855,0.20112]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49932,0.19686,0.29671]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.52507,0.10181,0.05344],"force_p95":0.0,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50857,0.09471,0.05124]}],"total_contact_groups":15},"final_pose_error":0.03603,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50595,0.10429,0.0338],"final_tcp_position":[0.50551,0.1031,0.14778],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":444.56301,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50597,0.0809,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16113,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54527,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1007.0,"raw_peak_contact_force":4.32595,"tcp_end":[0.49655,-0.0144,0.11302],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.1243,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":812.0,"n_steps_budget":870.0,"object_pos_end":[0.50656,0.10217,0.02867],"object_pos_start":[0.50597,0.0809,0.03378],"object_to_goal_dist_end":0.18264,"object_to_goal_dist_start":0.16113,"object_z_max":0.03382,"peak_contact_force":179.27909,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1294.0,"raw_peak_contact_force":221.15189,"tcp_end":[0.50792,0.09492,0.05132],"tcp_start":[0.49655,-0.0144,0.11302],"tcp_to_object_dist_end":0.02381,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":630.0,"object_pos_end":[0.50655,0.10221,0.02865],"object_pos_start":[0.50656,0.10217,0.02867],"object_to_goal_dist_end":0.18268,"object_to_goal_dist_start":0.18264,"object_z_max":0.02867,"peak_contact_force":106.78914,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":106.78914,"tcp_end":[0.50795,0.09501,0.05132],"tcp_start":[0.50792,0.09492,0.05132],"tcp_to_object_dist_end":0.02382,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50669,0.10212,0.02868],"object_pos_start":[0.50655,0.10221,0.02865],"object_to_goal_dist_end":0.18259,"object_to_goal_dist_start":0.18268,"object_z_max":0.0287,"peak_contact_force":432.39806,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":9.0,"raw_peak_contact_force":444.56301,"tcp_end":[0.50877,0.09459,0.05124],"tcp_start":[0.50857,0.09471,0.05124],"tcp_to_object_dist_end":0.02388,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50595,0.10429,0.0338],"object_pos_start":[0.50687,0.10198,0.02873],"object_to_goal_dist_end":0.18449,"object_to_goal_dist_start":0.18245,"object_z_max":0.03445,"peak_contact_force":0.55346,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1097.0,"raw_peak_contact_force":129.02549,"tcp_end":[0.50551,0.1031,0.14778],"tcp_start":[0.50877,0.09459,0.05124],"tcp_to_object_dist_end":0.11399,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.63636,"average_solve_count":154.0,"average_success_count":154.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_y":0.0036,"approach_1.approach_x_offset":0.00111,"approach_1.approach_z_offset":0.00919,"contact_1.contact_force":18.62411,"contact_1.speed":0.02926,"push_1.push_force_threshold":27.51283,"push_1.push_lateral_x":-0.01117,"push_1.push_speed":0.05568,"retract_1.retract_height":0.1656,"retract_1.speed":0.03983},"optimized_scores":{"best_composite_score":-0.24946,"best_fitness_score":0.14054,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":2,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":2.0,"contact_point_centroid":[0.5253,0.11949,0.05987],"force_p95":1171.11461,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1192.56614,"mean_force":978.05087,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50175,0.11932,0.0356]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54655,0.11999,0.05989],"force_p95":1110.56169,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1110.56169,"mean_force":1110.56169,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50195,0.11913,0.03551]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.54695,0.11999,0.05983],"force_p95":252.78854,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":256.63851,"mean_force":198.60207,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5023,0.11865,0.03557]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":15.0,"contact_point_centroid":[0.52534,0.11973,0.05985],"force_p95":62.44837,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":157.4145,"mean_force":14.44371,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50199,0.11942,0.03638]},{"body_a":"peg","body_b":"world","contact_count":4.0,"contact_point_centroid":[0.50794,0.13745,-0.00202],"force_p95":83.35559,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":92.01251,"mean_force":36.21735,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50133,0.11969,0.03584]},{"body_a":"attachment","body_b":"peg","contact_count":4.0,"contact_point_centroid":[0.5114,0.12447,0.03147],"force_p95":80.43418,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":88.71422,"mean_force":34.97852,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50133,0.11969,0.03584]},{"body_a":"peg","body_b":"channel_base_body","contact_count":820.0,"contact_point_centroid":[0.50617,0.10795,0.00943],"force_p95":20.13784,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":64.30408,"mean_force":2.65528,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49752,0.04462,0.07708]},{"body_a":"attachment","body_b":"peg","contact_count":57.0,"contact_point_centroid":[0.50528,0.09168,0.05724],"force_p95":53.92463,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":64.0209,"mean_force":31.31046,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50047,0.08135,0.05902]},{"body_a":"peg","body_b":"world","contact_count":1000.0,"contact_point_centroid":[0.53034,0.14663,-0.00189],"force_p95":0.74187,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":48.01509,"mean_force":0.83122,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49869,0.12998,0.07865]},{"body_a":"attachment","body_b":"peg","contact_count":35.0,"contact_point_centroid":[0.51169,0.12422,0.03292],"force_p95":22.01667,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":46.52942,"mean_force":6.62015,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50142,0.12014,0.03751]},{"body_a":"peg","body_b":"world","contact_count":36.0,"contact_point_centroid":[0.5077,0.14985,-0.00196],"force_p95":0.68248,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":31.79878,"mean_force":1.4709,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50164,0.11892,0.03853]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51092,0.12476,0.03179],"force_p95":31.14296,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":31.14296,"mean_force":31.14296,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50081,0.12009,0.03626]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":66.0,"contact_point_centroid":[0.52508,0.11611,0.03407],"force_p95":8.71709,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.05783,"mean_force":1.21651,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50109,0.0903,0.05453]},{"body_a":"peg","body_b":"channel_base_body","contact_count":973.0,"contact_point_centroid":[0.50574,0.10468,0.00938],"force_p95":0.57571,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.55797,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.4973,0.08932,0.19978]},{"body_a":"peg","body_b":"world","contact_count":81.0,"contact_point_centroid":[0.50724,0.14879,-0.00194],"force_p95":1.64914,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.19045,"mean_force":0.72297,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50215,0.11188,0.04366]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49937,0.19728,0.29716]}],"total_contact_groups":18},"final_pose_error":0.08048,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.54656,0.14579,0.01409],"final_tcp_position":[0.49882,0.13409,0.12211],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":1192.56614,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.10464,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18484,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.54104,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1005.0,"raw_peak_contact_force":3.33087,"tcp_end":[0.49653,-0.01335,0.11004],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14077,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":907.0,"n_steps_budget":960.0,"object_pos_end":[0.50758,0.14987,0.01405],"object_pos_start":[0.50599,0.10464,0.03384],"object_to_goal_dist_end":0.23146,"object_to_goal_dist_start":0.18484,"object_z_max":0.03605,"peak_contact_force":0.5266,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1024.0,"raw_peak_contact_force":64.30408,"tcp_end":[0.50252,0.1178,0.04074],"tcp_start":[0.49653,-0.01335,0.11004],"tcp_to_object_dist_end":0.04203,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":36.0,"n_steps_budget":990.0,"object_pos_end":[0.50798,0.14985,0.01415],"object_pos_start":[0.50758,0.14987,0.01405],"object_to_goal_dist_end":0.23144,"object_to_goal_dist_start":0.23146,"object_z_max":0.01414,"peak_contact_force":31.79878,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":37.0,"raw_peak_contact_force":31.79878,"tcp_end":[0.50079,0.12016,0.03617],"tcp_start":[0.50252,0.1178,0.04074],"tcp_to_object_dist_end":0.03766,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":4.0,"n_steps_budget":1000.0,"object_pos_end":[0.50814,0.14968,0.0143],"object_pos_start":[0.50798,0.14985,0.01415],"object_to_goal_dist_end":0.23125,"object_to_goal_dist_start":0.23144,"object_z_max":0.01451,"peak_contact_force":1192.56614,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":11.0,"raw_peak_contact_force":1192.56614,"tcp_end":[0.50223,0.11875,0.03543],"tcp_start":[0.50195,0.11913,0.03551],"tcp_to_object_dist_end":0.03792,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54656,0.14579,0.01409],"object_pos_start":[0.50833,0.14938,0.01476],"object_to_goal_dist_end":0.23199,"object_to_goal_dist_start":0.23092,"object_z_max":0.01706,"peak_contact_force":0.70717,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1190.0,"raw_peak_contact_force":256.63851,"tcp_end":[0.49882,0.13409,0.12211],"tcp_start":[0.50223,0.11875,0.03543],"tcp_to_object_dist_end":0.11867,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.59333,"average_solve_count":150.0,"average_success_count":150.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_y":-0.0019,"approach_1.approach_x_offset":-0.00126,"approach_1.approach_z_offset":0.00173,"contact_1.contact_force":11.90696,"contact_1.speed":0.01818,"push_1.push_force_threshold":37.4947,"push_1.push_lateral_x":0.00328,"push_1.push_speed":0.09703,"retract_1.retract_height":0.11816,"retract_1.speed":0.04233},"optimized_scores":{"best_composite_score":-0.19507,"best_fitness_score":0.19493,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.52534,0.08252,0.05985],"force_p95":821.32973,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":826.29322,"mean_force":776.76772,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50351,0.08214,0.04017]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":42.0,"contact_point_centroid":[0.52503,0.07751,0.05999],"force_p95":335.40395,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":345.34374,"mean_force":270.28714,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50667,0.07755,0.04795]},{"body_a":"peg","body_b":"channel_base_body","contact_count":750.0,"contact_point_centroid":[0.5057,0.07191,0.00888],"force_p95":166.61158,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":193.03852,"mean_force":37.28727,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49758,0.03232,0.07454]},{"body_a":"attachment","body_b":"peg","contact_count":255.0,"contact_point_centroid":[0.51093,0.06447,0.05401],"force_p95":173.09003,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":192.45906,"mean_force":108.19008,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5017,0.05935,0.05627]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":5.0,"contact_point_centroid":[0.52559,0.08208,0.05972],"force_p95":126.7646,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":151.86023,"mean_force":45.7911,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50364,0.08112,0.04001]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":2.0,"contact_point_centroid":[0.52501,0.08039,0.06],"force_p95":15.54544,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":16.36362,"mean_force":8.18181,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50537,0.08042,0.04532]},{"body_a":"peg","body_b":"world","contact_count":20.0,"contact_point_centroid":[0.51365,0.16303,-0.00238],"force_p95":3.06612,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.56137,"mean_force":1.23063,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50203,0.08376,0.04143]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":7.0,"contact_point_centroid":[0.47474,0.11064,0.05697],"force_p95":2.11738,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.25723,"mean_force":1.18266,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50712,0.07659,0.04898]},{"body_a":"peg","body_b":"channel_base_body","contact_count":984.0,"contact_point_centroid":[0.50307,0.06748,0.00936],"force_p95":0.55225,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.55539,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49733,0.08993,0.2022]},{"body_a":"peg","body_b":"channel_base_body","contact_count":992.0,"contact_point_centroid":[0.487,0.11999,0.00999],"force_p95":0.27114,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86216,"mean_force":0.23624,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50018,0.08954,0.08109]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":4.0,"contact_point_centroid":[0.52504,0.11999,0.02951],"force_p95":0.64853,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.66468,"mean_force":0.52105,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50225,0.08366,0.04075]},{"body_a":"peg","body_b":"world","contact_count":6.0,"contact_point_centroid":[0.51448,0.16271,-0.00161],"force_p95":0.59424,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60791,"mean_force":0.45792,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50275,0.08305,0.04052]},{"body_a":"peg","body_b":"channel_base_body","contact_count":36.0,"contact_point_centroid":[0.50209,0.116,0.00997],"force_p95":0.51171,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.527,"mean_force":0.34318,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50371,0.0818,0.04336]},{"body_a":"peg","body_b":"world","contact_count":999.0,"contact_point_centroid":[0.49191,0.16797,-3e-05],"force_p95":0.37163,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.51263,"mean_force":0.32995,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5002,0.08949,0.08085]}],"total_contact_groups":14},"final_pose_error":0.03353,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.48284,0.14828,0.02184],"final_tcp_position":[0.50079,0.0888,0.12571],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":3918.91969,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50308,0.06743,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54571,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":984.0,"raw_peak_contact_force":2.06903,"tcp_end":[0.49656,-0.01441,0.11275],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.1139,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":752.0,"n_steps_budget":810.0,"object_pos_end":[0.49998,0.11874,0.04056],"object_pos_start":[0.50308,0.06743,0.0338],"object_to_goal_dist_end":0.19874,"object_to_goal_dist_start":0.14759,"object_z_max":0.04073,"peak_contact_force":1.4163,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1054.0,"raw_peak_contact_force":345.34374,"tcp_end":[0.50542,0.08039,0.04537],"tcp_start":[0.49656,-0.01441,0.11275],"tcp_to_object_dist_end":0.03904,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":66.0,"n_steps_budget":1000.0,"object_pos_end":[0.51131,0.14545,0.02162],"object_pos_start":[0.49998,0.11874,0.04056],"object_to_goal_dist_end":0.22648,"object_to_goal_dist_start":0.19874,"object_z_max":0.04056,"peak_contact_force":3918.91969,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":58.0,"raw_peak_contact_force":16.36362,"tcp_end":[0.50169,0.08427,0.04104],"tcp_start":[0.50542,0.08039,0.04537],"tcp_to_object_dist_end":0.0649,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":6.0,"n_steps_budget":1000.0,"object_pos_end":[0.51122,0.1449,0.02199],"object_pos_start":[0.51131,0.14545,0.02162],"object_to_goal_dist_end":0.2259,"object_to_goal_dist_start":0.22648,"object_z_max":0.02206,"peak_contact_force":727.3516,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":13.0,"raw_peak_contact_force":826.29322,"tcp_end":[0.50421,0.08105,0.03999],"tcp_start":[0.50394,0.08154,0.04002],"tcp_to_object_dist_end":0.06671,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48284,0.14828,0.02184],"object_pos_start":[0.51109,0.14462,0.02211],"object_to_goal_dist_end":0.22964,"object_to_goal_dist_start":0.2256,"object_z_max":0.02302,"peak_contact_force":0.33991,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1996.0,"raw_peak_contact_force":151.86023,"tcp_end":[0.50079,0.0888,0.12571],"tcp_start":[0.50421,0.08105,0.03999],"tcp_to_object_dist_end":0.12104,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```