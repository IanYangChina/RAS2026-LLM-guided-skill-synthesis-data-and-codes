## Search State

- **Seed**: 4
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | 0.2567 | 0.57 | ❌ rejected |
| 13 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | 0.0748 | 0.38 | ❌ rejected |
| 12 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | impedance_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | -0.0034 | 0.01 | ❌ rejected |
| 11 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 10 | -0.2346 | 0.00 | ❌ rejected |
| 10 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | 0.2373 | 0.55 | ❌ rejected |

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

## Current Skill (Q=0.257) — your mutation base

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

- **Composite score**: 0.257
- **task_score** (E): 0.567
- **fitness_score**: 0.547  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.490

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_1 | 1.00 | 1.00 | 0.2395 |
| approach_1 | 1.00 | 1.00 | 0.0367 |
| contact_1 | 1.00 | 1.00 | 0.0054 |
| push_1 | 0.33 | 1.00 | 0.1621 |
| retract_1 | 0.67 | 1.00 | 0.1148 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_1 | align | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.516, 0.147, 0.068) | (0.521, 0.084, 0.040)→(0.505, 0.084, 0.034) | 0.166→0.165 | 1.00 / 1.000 | 0.546 | 3.242 |
| approach_1 | approach | 1.00 / step_budget | (0.516, 0.147, 0.068)→(0.503, 0.128, 0.041) | (0.505, 0.084, 0.034)→(0.505, 0.084, 0.034) | 0.165→0.165 | 1.00 / 1.333 | 0.830 | 23.478 |
| contact_1 | contact | 1.00 / force_exceeded | (0.503, 0.128, 0.041)→(0.502, 0.124, 0.038) | (0.505, 0.084, 0.034)→(0.505, 0.084, 0.034) | 0.165→0.164 | 1.00 / 2.000 | 36.698 | 36.698 |
| push_1 | push | 0.33 / step_budget | (0.502, 0.124, 0.038)→(0.499, -0.038, 0.037) | (0.505, 0.084, 0.034)→(0.506, -0.067, 0.036) | 0.164→0.018 | 1.00 / 3.000 | 61.289 | 134.718 |
| retract_1 | retract | 0.67 / step_budget | (0.499, -0.038, 0.037)→(0.496, -0.027, 0.151) | (0.506, -0.067, 0.036)→(0.504, -0.067, 0.034) | 0.018→0.017 | 1.00 / 1.000 | 0.547 | 63.094 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.908
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.908
- phase_score: 0.664
- phase_breakdown.push_score: 0.575
- phase_breakdown.contact_score: 0.685
- phase_breakdown.approach_score: 0.913

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.762
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.908
- **Median Q (composite search score)**: 0.150
- **K-run variance**: 0.0231
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.403


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.76821,"average_solve_count":151.0,"average_success_count":151.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_y":-9e-05,"approach_1.approach_z_offset":0.00875,"contact_1.contact_force":9.30184,"contact_1.speed":0.03389,"push_1.push_depth":0.01526,"push_1.push_speed":0.09365,"retract_1.retract_height":0.18306,"retract_1.speed":0.07098},"optimized_scores":{"best_composite_score":0.14962,"best_fitness_score":0.43962,"best_task_score":0.29293},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":26.0,"contact_point_centroid":[0.52501,0.12,0.06],"force_p95":88.49172,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":90.1977,"mean_force":71.13653,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50468,0.12363,0.04153]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":171.0,"contact_point_centroid":[0.54375,-0.01676,0.06],"force_p95":58.3775,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":75.63256,"mean_force":44.56793,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49902,-0.0141,0.03692]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":43.0,"contact_point_centroid":[0.52501,0.11999,0.06],"force_p95":66.36455,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":69.30778,"mean_force":56.93074,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50936,0.12787,0.0456]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.54316,-0.04699,0.06],"force_p95":62.6275,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":63.38896,"mean_force":56.43575,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49847,-0.0511,0.03678]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.525,0.12,0.06],"force_p95":58.52277,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":58.52277,"mean_force":58.52277,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50629,0.12581,0.04279]},{"body_a":"attachment","body_b":"peg","contact_count":708.0,"contact_point_centroid":[0.50431,0.014,0.04244],"force_p95":13.24144,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.05075,"mean_force":4.9001,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49982,0.02575,0.0371]},{"body_a":"peg","body_b":"channel_base_body","contact_count":636.0,"contact_point_centroid":[0.50568,-0.00719,0.00982],"force_p95":13.52359,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.30686,"mean_force":5.79061,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50031,0.03724,0.03754]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.50644,-0.10007,0.05931],"force_p95":12.55687,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.39702,"mean_force":6.13083,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49848,-0.05064,0.03679]},{"body_a":"attachment","body_b":"peg","contact_count":33.0,"contact_point_centroid":[0.50435,-0.06167,0.05106],"force_p95":2.90432,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.1129,"mean_force":0.68335,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49706,-0.04979,0.03908]},{"body_a":"peg","body_b":"channel_base_body","contact_count":13.0,"contact_point_centroid":[0.50634,-0.10012,0.05943],"force_p95":4.85182,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.40609,"mean_force":1.07925,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49816,-0.05114,0.0371]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":324.0,"contact_point_centroid":[0.52505,0.00102,0.02309],"force_p95":3.58442,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.51149,"mean_force":0.97264,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49985,0.02935,0.03707]},{"body_a":"peg","body_b":"channel_base_body","contact_count":722.0,"contact_point_centroid":[0.50579,0.08089,0.00936],"force_p95":0.55347,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.5679,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.51439,0.17032,0.17874]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50605,-0.07875,0.00942],"force_p95":0.55494,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.9019,"mean_force":0.54707,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.495,-0.03712,0.09454]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49997,0.19873,0.29562]},{"body_a":"peg","body_b":"channel_base_body","contact_count":197.0,"contact_point_centroid":[0.5059,0.08092,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55006,"mean_force":0.54677,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51695,0.13366,0.05341]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.52172,0.07217,0.00938],"force_p95":0.54612,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54612,"mean_force":0.54612,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50629,0.12581,0.04279]}],"total_contact_groups":16},"final_pose_error":0.06761,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50605,-0.07781,0.03378],"final_tcp_position":[0.49531,-0.03471,0.1543],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":90.1977,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":751.0,"n_steps_budget":1000.0,"object_pos_end":[0.50597,0.08086,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16109,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54611,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":758.0,"raw_peak_contact_force":4.32595,"tcp_end":[0.52966,0.14307,0.06764],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07469,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":197.0,"n_steps_budget":600.0,"object_pos_end":[0.50599,0.08087,0.03378],"object_pos_start":[0.50597,0.08086,0.03378],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.16109,"object_z_max":0.03378,"peak_contact_force":1.39306,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":240.0,"raw_peak_contact_force":69.30778,"tcp_end":[0.50629,0.12581,0.04279],"tcp_start":[0.52966,0.14307,0.06764],"tcp_to_object_dist_end":0.04584,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.50597,0.08086,0.03378],"object_pos_start":[0.50599,0.08087,0.03378],"object_to_goal_dist_end":0.16109,"object_to_goal_dist_start":0.1611,"object_z_max":0.03378,"peak_contact_force":58.52277,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":58.52277,"tcp_end":[0.50622,0.12576,0.04271],"tcp_start":[0.50629,0.12581,0.04279],"tcp_to_object_dist_end":0.04579,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50649,-0.07982,0.03622],"object_pos_start":[0.50597,0.08086,0.03378],"object_to_goal_dist_end":0.00751,"object_to_goal_dist_start":0.16109,"object_z_max":0.03687,"peak_contact_force":4.99547,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1868.0,"raw_peak_contact_force":90.1977,"subtask_id":"push","tcp_end":[0.49847,-0.05097,0.03678],"tcp_start":[0.50622,0.12576,0.04271],"tcp_to_object_dist_end":0.02995,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50605,-0.07781,0.03378],"object_pos_start":[0.50649,-0.07982,0.03622],"object_to_goal_dist_end":0.00895,"object_to_goal_dist_start":0.00751,"object_z_max":0.03631,"peak_contact_force":0.54277,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1049.0,"raw_peak_contact_force":63.38896,"tcp_end":[0.49531,-0.03471,0.1543],"tcp_start":[0.49847,-0.05097,0.03678],"tcp_to_object_dist_end":0.12844,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.56774,"average_solve_count":155.0,"average_success_count":155.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_y":0.00179,"approach_1.approach_z_offset":0.00433,"contact_1.contact_force":6.03941,"contact_1.speed":0.0254,"push_1.push_depth":0.07026,"push_1.push_speed":0.09675,"retract_1.retract_height":0.13739,"retract_1.speed":0.06485},"optimized_scores":{"best_composite_score":0.14861,"best_fitness_score":0.43861,"best_task_score":0.50107},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":767.0,"contact_point_centroid":[0.54619,0.06908,0.05998],"force_p95":160.97404,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":194.19471,"mean_force":117.28894,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50084,0.07252,0.03616]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":311.0,"contact_point_centroid":[0.52501,0.05252,0.06],"force_p95":131.49974,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":149.34358,"mean_force":59.2939,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5008,0.05236,0.03658]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.54522,-0.0157,0.05998],"force_p95":60.85643,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":60.91433,"mean_force":56.57573,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50055,-0.01075,0.03678]},{"body_a":"attachment","body_b":"peg","contact_count":344.0,"contact_point_centroid":[0.50182,0.05745,0.04075],"force_p95":21.15907,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":46.62572,"mean_force":3.59156,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50082,0.069,0.0363]},{"body_a":"peg","body_b":"channel_base_body","contact_count":807.0,"contact_point_centroid":[0.49951,0.03235,0.00961],"force_p95":6.33115,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":46.22526,"mean_force":1.93045,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50085,0.07076,0.03617]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.55196,0.12,0.05998],"force_p95":20.36011,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":20.36011,"mean_force":20.36011,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50182,0.14124,0.03404]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":230.0,"contact_point_centroid":[0.47482,0.01089,0.04204],"force_p95":2.21679,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.25508,"mean_force":0.60307,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50073,0.04038,0.03673]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":138.0,"contact_point_centroid":[0.5251,0.08596,0.0315],"force_p95":0.90064,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.06626,"mean_force":0.40745,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50095,0.11621,0.0356]},{"body_a":"peg","body_b":"channel_base_body","contact_count":694.0,"contact_point_centroid":[0.50568,0.10459,0.00937],"force_p95":0.57582,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.56264,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50901,0.18278,0.17964]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49983,0.19916,0.2962]},{"body_a":"peg","body_b":"channel_base_body","contact_count":988.0,"contact_point_centroid":[0.50566,-0.04641,0.00943],"force_p95":0.62699,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.28094,"mean_force":0.54749,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.497,-0.00018,0.09059]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":280.0,"contact_point_centroid":[0.52509,-0.04578,0.04992],"force_p95":0.42954,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.94514,"mean_force":0.10955,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49724,-0.00167,0.08301]},{"body_a":"peg","body_b":"channel_base_body","contact_count":166.0,"contact_point_centroid":[0.50614,0.10481,0.00939],"force_p95":0.57567,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57589,"mean_force":0.54628,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51169,0.15858,0.0539]},{"body_a":"peg","body_b":"channel_base_body","contact_count":88.0,"contact_point_centroid":[0.50561,0.10512,0.00939],"force_p95":0.57571,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57577,"mean_force":0.54634,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50298,0.14476,0.03645]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.50322,-0.02265,0.04061],"force_p95":0.14984,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16649,"mean_force":0.0555,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50055,-0.01075,0.03678]}],"total_contact_groups":15},"final_pose_error":0.03139,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50681,-0.04583,0.03382],"final_tcp_position":[0.49725,-0.0024,0.14405],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":194.19471,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":721.0,"n_steps_budget":1000.0,"object_pos_end":[0.50583,0.10467,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18486,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.54529,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":726.0,"raw_peak_contact_force":3.33087,"tcp_end":[0.51924,0.1672,0.06837],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07269,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":166.0,"n_steps_budget":600.0,"object_pos_end":[0.50587,0.10457,0.03384],"object_pos_start":[0.50583,0.10467,0.03384],"object_to_goal_dist_end":0.18476,"object_to_goal_dist_start":0.18486,"object_z_max":0.03384,"peak_contact_force":0.55155,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":166.0,"raw_peak_contact_force":0.57589,"tcp_end":[0.50517,0.14909,0.04035],"tcp_start":[0.51924,0.1672,0.06837],"tcp_to_object_dist_end":0.045,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":88.0,"n_steps_budget":630.0,"object_pos_end":[0.50598,0.1046,0.03384],"object_pos_start":[0.50587,0.10457,0.03384],"object_to_goal_dist_end":0.1848,"object_to_goal_dist_start":0.18476,"object_z_max":0.03384,"peak_contact_force":20.36011,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":89.0,"raw_peak_contact_force":20.36011,"tcp_end":[0.50181,0.14119,0.03401],"tcp_start":[0.50517,0.14909,0.04035],"tcp_to_object_dist_end":0.03683,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50409,-0.0402,0.03714],"object_pos_start":[0.50598,0.1046,0.03384],"object_to_goal_dist_end":0.04011,"object_to_goal_dist_start":0.1848,"object_z_max":0.03743,"peak_contact_force":106.34101,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2597.0,"raw_peak_contact_force":194.19471,"subtask_id":"push","tcp_end":[0.50056,-0.01057,0.03678],"tcp_start":[0.50181,0.14119,0.03401],"tcp_to_object_dist_end":0.02984,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50681,-0.04583,0.03382],"object_pos_start":[0.50409,-0.0402,0.03714],"object_to_goal_dist_end":0.03538,"object_to_goal_dist_start":0.04011,"object_z_max":0.03762,"peak_contact_force":0.54868,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1274.0,"raw_peak_contact_force":60.91433,"tcp_end":[0.49725,-0.0024,0.14405],"tcp_start":[0.50056,-0.01057,0.03678],"tcp_to_object_dist_end":0.11887,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.63694,"average_solve_count":157.0,"average_success_count":157.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_y":-0.00058,"approach_1.approach_z_offset":0.00931,"contact_1.contact_force":12.31834,"contact_1.speed":0.01629,"push_1.push_depth":0.03183,"push_1.push_speed":0.09731,"retract_1.retract_height":0.14795,"retract_1.speed":0.0707},"optimized_scores":{"best_composite_score":0.47184,"best_fitness_score":0.76184,"best_task_score":0.90789},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":705.0,"contact_point_centroid":[0.5424,0.03125,0.05999],"force_p95":110.06279,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":119.76302,"mean_force":91.89016,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49755,0.03285,0.03687]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.54285,-0.04858,0.05998],"force_p95":63.80752,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":64.97894,"mean_force":56.76849,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49818,-0.05269,0.03671]},{"body_a":"attachment","body_b":"peg","contact_count":507.0,"contact_point_centroid":[0.50295,0.00636,0.04235],"force_p95":26.31586,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":35.25625,"mean_force":5.67912,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49772,0.01792,0.03691]},{"body_a":"peg","body_b":"channel_base_body","contact_count":710.0,"contact_point_centroid":[0.50352,-0.00844,0.00974],"force_p95":23.02164,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":34.52387,"mean_force":4.04489,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49754,0.03378,0.03687]},{"body_a":"peg","body_b":"channel_base_body","contact_count":8.0,"contact_point_centroid":[0.50556,-0.1003,0.06018],"force_p95":32.82291,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":33.48867,"mean_force":18.65021,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49819,-0.05197,0.03674]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54162,0.10626,0.05998],"force_p95":31.21166,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":31.21166,"mean_force":31.21166,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49689,0.10507,0.03641]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":373.0,"contact_point_centroid":[0.52515,-0.00997,0.02538],"force_p95":7.35759,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.76998,"mean_force":1.62868,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49773,0.01805,0.03692]},{"body_a":"peg","body_b":"channel_base_body","contact_count":33.0,"contact_point_centroid":[0.50522,-0.10031,0.06026],"force_p95":2.77536,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.95369,"mean_force":0.94229,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49718,-0.05202,0.03801]},{"body_a":"attachment","body_b":"peg","contact_count":54.0,"contact_point_centroid":[0.50124,-0.06254,0.04752],"force_p95":1.946,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.86774,"mean_force":0.79775,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49637,-0.05067,0.04028]},{"body_a":"peg","body_b":"channel_base_body","contact_count":724.0,"contact_point_centroid":[0.50309,0.06747,0.00935],"force_p95":0.55474,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.55853,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49876,0.16431,0.18135]},{"body_a":"peg","body_b":"channel_base_body","contact_count":973.0,"contact_point_centroid":[0.50065,-0.07853,0.00943],"force_p95":0.55686,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.69308,"mean_force":0.54059,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49465,-0.04104,0.09636]},{"body_a":"peg","body_b":"channel_base_body","contact_count":372.0,"contact_point_centroid":[0.50298,0.06736,0.00938],"force_p95":0.55058,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55081,"mean_force":0.54665,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49768,0.11714,0.0504]},{"body_a":"peg","body_b":"channel_base_body","contact_count":41.0,"contact_point_centroid":[0.50348,0.06866,0.00938],"force_p95":0.55056,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55069,"mean_force":0.54664,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49765,0.10687,0.03818]}],"total_contact_groups":13},"final_pose_error":0.03171,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50028,-0.0778,0.03386],"final_tcp_position":[0.49503,-0.04397,0.15431],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":119.76302,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":740.0,"n_steps_budget":1000.0,"object_pos_end":[0.50305,0.06742,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14758,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54764,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":724.0,"raw_peak_contact_force":2.06903,"tcp_end":[0.49917,0.13003,0.06836],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07162,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":372.0,"n_steps_budget":600.0,"object_pos_end":[0.50301,0.06748,0.0338],"object_pos_start":[0.50305,0.06742,0.0338],"object_to_goal_dist_end":0.14764,"object_to_goal_dist_start":0.14758,"object_z_max":0.0338,"peak_contact_force":0.54501,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":372.0,"raw_peak_contact_force":0.55081,"tcp_end":[0.49858,0.10834,0.04004],"tcp_start":[0.49917,0.13003,0.06836],"tcp_to_object_dist_end":0.04157,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":41.0,"n_steps_budget":870.0,"object_pos_end":[0.50307,0.06743,0.0338],"object_pos_start":[0.50301,0.06748,0.0338],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14764,"object_z_max":0.0338,"peak_contact_force":31.21166,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":42.0,"raw_peak_contact_force":31.21166,"tcp_end":[0.49687,0.105,0.03634],"tcp_start":[0.49858,0.10834,0.04004],"tcp_to_object_dist_end":0.03816,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50593,-0.0818,0.0361],"object_pos_start":[0.50307,0.06743,0.0338],"object_to_goal_dist_end":0.00733,"object_to_goal_dist_start":0.14759,"object_z_max":0.03907,"peak_contact_force":72.53154,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2303.0,"raw_peak_contact_force":119.76302,"subtask_id":"push","tcp_end":[0.49819,-0.05258,0.03671],"tcp_start":[0.49687,0.105,0.03634],"tcp_to_object_dist_end":0.03024,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50028,-0.0778,0.03386],"object_pos_start":[0.50593,-0.0818,0.0361],"object_to_goal_dist_end":0.00653,"object_to_goal_dist_start":0.00733,"object_z_max":0.03695,"peak_contact_force":0.54841,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1063.0,"raw_peak_contact_force":64.97894,"tcp_end":[0.49503,-0.04397,0.15431],"tcp_start":[0.49819,-0.05258,0.03671],"tcp_to_object_dist_end":0.12523,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```