## Search State

- **Seed**: 4
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | 0.2699 | 0.58 | ✅ accepted |
| 5 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | 0.2632 | 0.58 | ✅ accepted |
| 4 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 7 | 0.2734 | 0.48 | ✅ accepted |
| 3 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 10 | -0.2646 | 0.00 | ❌ rejected |
| 2 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 7 | 0.2681 | 0.46 | ✅ accepted |

**Proposal policy**: task_score is 0.58 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.270) — your mutation base

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

- **Composite score**: 0.270
- **task_score** (E): 0.584
- **fitness_score**: 0.560  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.490

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_1 | 1.00 | 1.00 | 0.2394 |
| approach_1 | 1.00 | 1.00 | 0.0356 |
| contact_1 | 1.00 | 1.00 | 0.0074 |
| push_1 | 0.00 | 1.00 | 0.1643 |
| retract_1 | 1.00 | 1.00 | 0.1086 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_1 | align | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.516, 0.147, 0.068) | (0.521, 0.084, 0.040)→(0.505, 0.084, 0.034) | 0.166→0.165 | 1.00 / 1.000 | 0.546 | 3.242 |
| approach_1 | approach | 1.00 / step_budget | (0.516, 0.147, 0.068)→(0.504, 0.128, 0.042) | (0.505, 0.084, 0.034)→(0.505, 0.084, 0.034) | 0.165→0.164 | 1.00 / 1.333 | 15.657 | 20.531 |
| contact_1 | contact | 1.00 / force_exceeded | (0.504, 0.128, 0.042)→(0.502, 0.123, 0.038) | (0.505, 0.084, 0.034)→(0.505, 0.084, 0.034) | 0.164→0.165 | 1.00 / 2.000 | 35.591 | 49.204 |
| push_1 | push | 0.00 / step_budget | (0.502, 0.123, 0.038)→(0.499, -0.042, 0.037) | (0.505, 0.084, 0.034)→(0.506, -0.071, 0.036) | 0.165→0.014 | 1.00 / 2.000 | 0.565 | 116.804 |
| retract_1 | retract | 1.00 / step_budget | (0.499, -0.042, 0.037)→(0.496, -0.039, 0.145) | (0.506, -0.071, 0.036)→(0.505, -0.070, 0.034) | 0.014→0.015 | 1.00 / 1.000 | 0.547 | 54.450 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.924
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.924
- phase_score: 0.662
- phase_breakdown.push_score: 0.578
- phase_breakdown.contact_score: 0.667
- phase_breakdown.approach_score: 0.909

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.767
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.924
- **Median Q (composite search score)**: 0.193
- **K-run variance**: 0.0219
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.410


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.74534,"average_solve_count":161.0,"average_success_count":161.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_y":0.00576,"approach_1.approach_z_offset":0.0099,"contact_1.contact_force":9.52868,"contact_1.speed":0.02847,"push_1.push_depth":0.02422,"push_1.push_speed":0.07619,"retract_1.retract_height":0.16811,"retract_1.speed":0.09999},"optimized_scores":{"best_composite_score":0.14026,"best_fitness_score":0.43026,"best_task_score":0.29886},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":2.0,"contact_point_centroid":[0.525,0.12,0.06],"force_p95":94.48428,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":96.52618,"mean_force":76.10723,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50633,0.12567,0.04303]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":25.0,"contact_point_centroid":[0.525,0.12,0.06],"force_p95":77.28719,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":79.60687,"mean_force":62.26841,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5047,0.12367,0.04152]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":10.0,"contact_point_centroid":[0.52501,0.12,0.06],"force_p95":59.19648,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":60.46581,"mean_force":46.50912,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50745,0.12659,0.04408]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":163.0,"contact_point_centroid":[0.54386,-0.01313,0.06],"force_p95":56.36788,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":60.34917,"mean_force":43.22388,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49912,-0.01026,0.03693]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54326,-0.04368,0.06],"force_p95":57.6946,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":57.6946,"mean_force":57.6946,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49858,-0.04796,0.03679]},{"body_a":"peg","body_b":"channel_base_body","contact_count":608.0,"contact_point_centroid":[0.50609,-0.00618,0.00984],"force_p95":12.48526,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.13231,"mean_force":5.53474,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50032,0.03828,0.03753]},{"body_a":"attachment","body_b":"peg","contact_count":740.0,"contact_point_centroid":[0.5043,0.0164,0.04226],"force_p95":11.74653,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.92662,"mean_force":4.23454,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49985,0.02816,0.03709]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":335.0,"contact_point_centroid":[0.52503,0.00603,0.01882],"force_p95":2.62817,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.6917,"mean_force":0.71447,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49994,0.03411,0.03708]},{"body_a":"peg","body_b":"channel_base_body","contact_count":718.0,"contact_point_centroid":[0.50577,0.08085,0.00936],"force_p95":0.55366,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.56802,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.5144,0.17314,0.17873]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49998,0.19881,0.29562]},{"body_a":"peg","body_b":"channel_base_body","contact_count":964.0,"contact_point_centroid":[0.50659,-0.07665,0.0094],"force_p95":0.56385,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.96593,"mean_force":0.54805,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49534,-0.03624,0.11429]},{"body_a":"peg","body_b":"channel_base_body","contact_count":200.0,"contact_point_centroid":[0.5059,0.081,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55006,"mean_force":0.54678,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51755,0.13728,0.05427]},{"body_a":"peg","body_b":"channel_base_body","contact_count":7.0,"contact_point_centroid":[0.50813,0.08227,0.00938],"force_p95":0.5495,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55006,"mean_force":0.54646,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50632,0.12569,0.04306]},{"body_a":"attachment","body_b":"peg","contact_count":12.0,"contact_point_centroid":[0.50613,-0.05771,0.05914],"force_p95":0.29179,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.39797,"mean_force":0.06687,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49663,-0.0459,0.04049]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":7.0,"contact_point_centroid":[0.52502,-0.07553,0.04551],"force_p95":0.34803,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.35044,"mean_force":0.16973,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49684,-0.04571,0.04085]}],"total_contact_groups":15},"final_pose_error":0.01181,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50663,-0.0764,0.03381],"final_tcp_position":[0.49581,-0.04534,0.19372],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":96.52618,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":747.0,"n_steps_budget":1000.0,"object_pos_end":[0.50596,0.08089,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.5464,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":754.0,"raw_peak_contact_force":4.32595,"tcp_end":[0.52966,0.14857,0.06763],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.0793,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":200.0,"n_steps_budget":600.0,"object_pos_end":[0.50599,0.08089,0.03378],"object_pos_start":[0.50596,0.08089,0.03378],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16112,"object_z_max":0.03378,"peak_contact_force":45.87167,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":210.0,"raw_peak_contact_force":60.46581,"tcp_end":[0.50654,0.12582,0.04331],"tcp_start":[0.52966,0.14857,0.06763],"tcp_to_object_dist_end":0.04594,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":7.0,"n_steps_budget":600.0,"object_pos_end":[0.50599,0.08087,0.03378],"object_pos_start":[0.50599,0.08089,0.03378],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.16112,"object_z_max":0.03378,"peak_contact_force":55.68828,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":9.0,"raw_peak_contact_force":96.52618,"tcp_end":[0.50605,0.12546,0.04265],"tcp_start":[0.50654,0.12582,0.04331],"tcp_to_object_dist_end":0.04547,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50702,-0.07697,0.03661],"object_pos_start":[0.50599,0.08087,0.03378],"object_to_goal_dist_end":0.00837,"object_to_goal_dist_start":0.1611,"object_z_max":0.03673,"peak_contact_force":1.04484,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1871.0,"raw_peak_contact_force":79.60687,"tcp_end":[0.4986,-0.04784,0.03682],"tcp_start":[0.50605,0.12546,0.04265],"tcp_to_object_dist_end":0.03032,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":967.0,"n_steps_budget":1000.0,"object_pos_end":[0.50663,-0.0764,0.03381],"object_pos_start":[0.50702,-0.07697,0.03661],"object_to_goal_dist_end":0.00976,"object_to_goal_dist_start":0.00837,"object_z_max":0.03661,"peak_contact_force":0.54865,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":984.0,"raw_peak_contact_force":57.6946,"tcp_end":[0.49581,-0.04534,0.19372],"tcp_start":[0.4986,-0.04784,0.03682],"tcp_to_object_dist_end":0.16326,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.55063,"average_solve_count":158.0,"average_success_count":158.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_y":-0.0013,"approach_1.approach_z_offset":0.00951,"contact_1.contact_force":17.68523,"contact_1.speed":0.04279,"push_1.push_depth":0.02562,"push_1.push_speed":0.09988,"retract_1.retract_height":0.12374,"retract_1.speed":0.06698},"optimized_scores":{"best_composite_score":0.19266,"best_fitness_score":0.48266,"best_task_score":0.53007},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":746.0,"contact_point_centroid":[0.54586,0.0599,0.05999],"force_p95":130.437,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":150.10333,"mean_force":106.41593,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50079,0.06271,0.0363]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":125.0,"contact_point_centroid":[0.525,0.06166,0.06],"force_p95":103.16636,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":111.39434,"mean_force":49.2253,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50083,0.06146,0.03656]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.54469,-0.03044,0.05999],"force_p95":50.79989,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":50.86704,"mean_force":50.19548,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50014,-0.02473,0.03674]},{"body_a":"attachment","body_b":"peg","contact_count":372.0,"contact_point_centroid":[0.50199,0.05562,0.03977],"force_p95":15.71159,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":32.92533,"mean_force":2.83444,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50082,0.06728,0.03626]},{"body_a":"peg","body_b":"channel_base_body","contact_count":733.0,"contact_point_centroid":[0.50035,0.02177,0.00968],"force_p95":7.95407,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":30.87029,"mean_force":1.86512,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5008,0.06152,0.03631]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":173.0,"contact_point_centroid":[0.47473,0.0156,0.02928],"force_p95":3.89101,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.16792,"mean_force":0.99252,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50073,0.0447,0.03673]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.55037,0.12,0.05997],"force_p95":17.83034,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":18.04972,"mean_force":15.49029,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50177,0.13565,0.03439]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":162.0,"contact_point_centroid":[0.52517,0.02821,0.02348],"force_p95":2.49129,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.29654,"mean_force":0.56771,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50071,0.05787,0.03624]},{"body_a":"peg","body_b":"channel_base_body","contact_count":695.0,"contact_point_centroid":[0.50566,0.1046,0.00937],"force_p95":0.57582,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.56261,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50901,0.1813,0.17964]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49983,0.19912,0.2962]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50632,-0.05438,0.00941],"force_p95":0.56406,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.06917,"mean_force":0.54545,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49674,-0.01572,0.0919]},{"body_a":"attachment","body_b":"peg","contact_count":4.0,"contact_point_centroid":[0.50271,-0.03665,0.04011],"force_p95":0.7275,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.76857,"mean_force":0.51843,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50014,-0.02472,0.03676]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":222.0,"contact_point_centroid":[0.52502,-0.05396,0.0574],"force_p95":0.18915,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.72104,"mean_force":0.03471,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49681,-0.01581,0.09244]},{"body_a":"peg","body_b":"channel_base_body","contact_count":139.0,"contact_point_centroid":[0.50631,0.10481,0.00939],"force_p95":0.57566,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57589,"mean_force":0.5463,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51217,0.15718,0.05652]},{"body_a":"peg","body_b":"channel_base_body","contact_count":172.0,"contact_point_centroid":[0.50566,0.10447,0.00939],"force_p95":0.57571,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57579,"mean_force":0.54638,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50279,0.14127,0.03815]}],"total_contact_groups":15},"final_pose_error":0.01331,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50688,-0.05398,0.03382],"final_tcp_position":[0.49702,-0.02154,0.14794],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":150.10333,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":722.0,"n_steps_budget":1000.0,"object_pos_end":[0.50585,0.1047,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18489,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.54289,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":727.0,"raw_peak_contact_force":3.33087,"tcp_end":[0.51923,0.16433,0.06846],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07024,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":139.0,"n_steps_budget":600.0,"object_pos_end":[0.50587,0.10457,0.03384],"object_pos_start":[0.50585,0.1047,0.03384],"object_to_goal_dist_end":0.18476,"object_to_goal_dist_start":0.18489,"object_z_max":0.03384,"peak_contact_force":0.55172,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":139.0,"raw_peak_contact_force":0.57589,"tcp_end":[0.50582,0.1492,0.04535],"tcp_start":[0.51923,0.16433,0.06846],"tcp_to_object_dist_end":0.04609,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":172.0,"n_steps_budget":600.0,"object_pos_end":[0.50583,0.10466,0.03384],"object_pos_start":[0.50587,0.10457,0.03384],"object_to_goal_dist_end":0.18486,"object_to_goal_dist_start":0.18476,"object_z_max":0.03384,"peak_contact_force":18.04972,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":176.0,"raw_peak_contact_force":18.04972,"tcp_end":[0.50178,0.13557,0.03435],"tcp_start":[0.50582,0.1492,0.04535],"tcp_to_object_dist_end":0.03118,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50428,-0.05432,0.03628],"object_pos_start":[0.50583,0.10466,0.03384],"object_to_goal_dist_end":0.0263,"object_to_goal_dist_start":0.18486,"object_z_max":0.03831,"peak_contact_force":0.65153,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2311.0,"raw_peak_contact_force":150.10333,"tcp_end":[0.50024,-0.02444,0.03678],"tcp_start":[0.50178,0.13557,0.03435],"tcp_to_object_dist_end":0.03015,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50688,-0.05398,0.03382],"object_pos_start":[0.50428,-0.05432,0.03628],"object_to_goal_dist_end":0.02761,"object_to_goal_dist_start":0.0263,"object_z_max":0.0365,"peak_contact_force":0.54748,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1228.0,"raw_peak_contact_force":50.86704,"tcp_end":[0.49702,-0.02154,0.14794],"tcp_start":[0.50024,-0.02444,0.03678],"tcp_to_object_dist_end":0.11905,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.38514,"average_solve_count":148.0,"average_success_count":148.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_y":-0.00275,"approach_1.approach_z_offset":0.00774,"contact_1.contact_force":11.23275,"contact_1.speed":0.00917,"push_1.push_depth":0.02743,"push_1.push_speed":0.09757,"retract_1.retract_height":0.06653,"retract_1.speed":0.06016},"optimized_scores":{"best_composite_score":0.47686,"best_fitness_score":0.76686,"best_task_score":0.92443},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":709.0,"contact_point_centroid":[0.54261,0.032,0.05999],"force_p95":109.33635,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":120.70278,"mean_force":91.23938,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49777,0.03364,0.03684]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.54292,-0.0489,0.05999],"force_p95":54.78332,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":54.78962,"mean_force":51.17021,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49826,-0.05299,0.03671]},{"body_a":"attachment","body_b":"peg","contact_count":379.0,"contact_point_centroid":[0.5012,0.00456,0.04067],"force_p95":23.9094,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.14249,"mean_force":4.79017,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49793,0.01617,0.03687]},{"body_a":"peg","body_b":"channel_base_body","contact_count":757.0,"contact_point_centroid":[0.50175,-0.00536,0.00963],"force_p95":17.62333,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":36.3089,"mean_force":2.7296,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49778,0.03404,0.03684]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54194,0.10782,0.05999],"force_p95":33.03568,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":33.03568,"mean_force":33.03568,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49725,0.10657,0.03636]},{"body_a":"peg","body_b":"channel_base_body","contact_count":13.0,"contact_point_centroid":[0.50618,-0.10011,0.05983],"force_p95":23.63389,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.38624,"mean_force":6.56286,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49827,-0.05168,0.03673]},{"body_a":"peg","body_b":"channel_base_body","contact_count":27.0,"contact_point_centroid":[0.50473,-0.10007,0.06011],"force_p95":12.65841,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.58761,"mean_force":3.10639,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49752,-0.05244,0.03767]},{"body_a":"attachment","body_b":"peg","contact_count":36.0,"contact_point_centroid":[0.50355,-0.06383,0.05113],"force_p95":10.44862,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.18178,"mean_force":2.47736,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49714,-0.052,0.0384]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":125.0,"contact_point_centroid":[0.47484,-0.00902,0.02975],"force_p95":1.74748,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.63204,"mean_force":0.57555,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49813,0.02054,0.03704]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":206.0,"contact_point_centroid":[0.52518,-0.02029,0.03244],"force_p95":4.77877,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.17293,"mean_force":1.00832,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49799,0.00846,0.03688]},{"body_a":"peg","body_b":"channel_base_body","contact_count":576.0,"contact_point_centroid":[0.50201,-0.08107,0.00943],"force_p95":0.59096,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.69829,"mean_force":0.59061,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49465,-0.04786,0.06621]},{"body_a":"peg","body_b":"channel_base_body","contact_count":726.0,"contact_point_centroid":[0.50307,0.06743,0.00935],"force_p95":0.55473,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.5585,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49876,0.16329,0.18135]},{"body_a":"peg","body_b":"channel_base_body","contact_count":333.0,"contact_point_centroid":[0.50306,0.06746,0.00938],"force_p95":0.55059,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55081,"mean_force":0.54665,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49771,0.11625,0.04966]},{"body_a":"peg","body_b":"channel_base_body","contact_count":26.0,"contact_point_centroid":[0.5035,0.06799,0.00938],"force_p95":0.55046,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55049,"mean_force":0.54666,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49786,0.10759,0.03753]}],"total_contact_groups":14},"final_pose_error":0.00998,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50171,-0.08045,0.0338],"final_tcp_position":[0.49462,-0.05112,0.09413],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":120.70278,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":742.0,"n_steps_budget":1000.0,"object_pos_end":[0.50301,0.06745,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14761,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54722,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":726.0,"raw_peak_contact_force":2.06903,"tcp_end":[0.49916,0.12799,0.06833],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.0698,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":333.0,"n_steps_budget":600.0,"object_pos_end":[0.50301,0.06745,0.0338],"object_pos_start":[0.50301,0.06745,0.0338],"object_to_goal_dist_end":0.14761,"object_to_goal_dist_start":0.14761,"object_z_max":0.0338,"peak_contact_force":0.54685,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":333.0,"raw_peak_contact_force":0.55081,"tcp_end":[0.49853,0.10823,0.03862],"tcp_start":[0.49916,0.12799,0.06833],"tcp_to_object_dist_end":0.0413,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":26.0,"n_steps_budget":1000.0,"object_pos_end":[0.50302,0.06743,0.0338],"object_pos_start":[0.50301,0.06745,0.0338],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14761,"object_z_max":0.0338,"peak_contact_force":33.03568,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":27.0,"raw_peak_contact_force":33.03568,"tcp_end":[0.49721,0.10649,0.03629],"tcp_start":[0.49853,0.10823,0.03862],"tcp_to_object_dist_end":0.03957,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50572,-0.08203,0.03476],"object_pos_start":[0.50302,0.06743,0.0338],"object_to_goal_dist_end":0.00802,"object_to_goal_dist_start":0.14759,"object_z_max":0.03875,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2189.0,"raw_peak_contact_force":120.70278,"tcp_end":[0.49828,-0.05283,0.03673],"tcp_start":[0.49721,0.10649,0.03629],"tcp_to_object_dist_end":0.0302,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":592.0,"n_steps_budget":720.0,"object_pos_end":[0.50171,-0.08045,0.0338],"object_pos_start":[0.50572,-0.08203,0.03476],"object_to_goal_dist_end":0.00645,"object_to_goal_dist_start":0.00802,"object_z_max":0.03586,"peak_contact_force":0.54358,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":642.0,"raw_peak_contact_force":54.78962,"tcp_end":[0.49462,-0.05112,0.09413],"tcp_start":[0.49828,-0.05283,0.03673],"tcp_to_object_dist_end":0.06746,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```