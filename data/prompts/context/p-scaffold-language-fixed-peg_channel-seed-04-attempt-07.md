## Search State

- **Seed**: 4
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | 0.2661 | 0.58 | ✅ accepted |
| 6 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | 0.2699 | 0.58 | ✅ accepted |
| 5 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | 0.2632 | 0.58 | ✅ accepted |
| 4 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 7 | 0.2734 | 0.48 | ✅ accepted |
| 3 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 10 | -0.2646 | 0.00 | ❌ rejected |

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

## Current Skill (Q=0.266) — your mutation base

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

- **Composite score**: 0.266
- **task_score** (E): 0.585
- **fitness_score**: 0.556  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.490

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_1 | 1.00 | 1.00 | 0.2391 |
| approach_1 | 1.00 | 1.00 | 0.0373 |
| contact_1 | 1.00 | 1.00 | 0.0057 |
| push_1 | 0.33 | 1.00 | 0.1646 |
| retract_1 | 1.00 | 1.00 | 0.0953 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_1 | align | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.516, 0.148, 0.068) | (0.521, 0.084, 0.040)→(0.505, 0.084, 0.034) | 0.166→0.165 | 1.00 / 1.000 | 0.548 | 3.242 |
| approach_1 | approach | 1.00 / step_budget | (0.516, 0.148, 0.068)→(0.503, 0.128, 0.041) | (0.505, 0.084, 0.034)→(0.505, 0.084, 0.034) | 0.165→0.165 | 1.00 / 1.000 | 0.362 | 23.026 |
| contact_1 | contact | 1.00 / force_exceeded | (0.503, 0.128, 0.041)→(0.502, 0.124, 0.038) | (0.505, 0.084, 0.034)→(0.505, 0.084, 0.034) | 0.165→0.164 | 1.00 / 2.000 | 38.080 | 38.080 |
| push_1 | push | 0.33 / step_budget | (0.502, 0.124, 0.038)→(0.499, -0.041, 0.037) | (0.505, 0.084, 0.034)→(0.506, -0.070, 0.036) | 0.164→0.016 | 1.00 / 2.333 | 54.672 | 117.223 |
| retract_1 | retract | 1.00 / step_budget | (0.499, -0.041, 0.037)→(0.496, -0.038, 0.132) | (0.506, -0.070, 0.036)→(0.506, -0.069, 0.034) | 0.016→0.016 | 1.00 / 1.000 | 0.354 | 62.316 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.934
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.934
- phase_score: 0.658
- phase_breakdown.push_score: 0.582
- phase_breakdown.contact_score: 0.648
- phase_breakdown.approach_score: 0.893

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.768
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.934
- **Median Q (composite search score)**: 0.181
- **K-run variance**: 0.0228
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.354


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.69427,"average_solve_count":157.0,"average_success_count":157.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_y":0.0032,"approach_1.approach_z_offset":0.00915,"contact_1.contact_force":21.56585,"contact_1.speed":0.01554,"push_1.push_depth":0.0355,"push_1.push_speed":0.08576,"retract_1.retract_height":0.11976,"retract_1.speed":0.07428},"optimized_scores":{"best_composite_score":0.13887,"best_fitness_score":0.42887,"best_task_score":0.29971},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":23.0,"contact_point_centroid":[0.52501,0.12,0.06],"force_p95":81.79262,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":83.74292,"mean_force":67.33745,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50443,0.12365,0.04101]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":204.0,"contact_point_centroid":[0.54415,-0.00634,0.06],"force_p95":57.55685,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":69.30183,"mean_force":43.20398,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4994,-0.00341,0.0369]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":26.0,"contact_point_centroid":[0.52501,0.12,0.06],"force_p95":65.13358,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":67.95168,"mean_force":52.0113,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50822,0.12725,0.04449]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.5434,-0.04331,0.05999],"force_p95":61.28653,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":62.09784,"mean_force":53.98481,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49873,-0.04761,0.03677]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.525,0.12,0.06],"force_p95":50.42369,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":50.42369,"mean_force":50.42369,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50591,0.12559,0.04227]},{"body_a":"attachment","body_b":"peg","contact_count":688.0,"contact_point_centroid":[0.50445,0.01858,0.0424],"force_p95":12.30336,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.42993,"mean_force":4.55006,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49997,0.03034,0.03697]},{"body_a":"peg","body_b":"channel_base_body","contact_count":639.0,"contact_point_centroid":[0.50588,-0.0074,0.00985],"force_p95":12.24389,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.52697,"mean_force":5.21208,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50034,0.037,0.03734]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":413.0,"contact_point_centroid":[0.52506,-0.00849,0.02423],"force_p95":4.14096,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.93694,"mean_force":1.14403,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49979,0.02003,0.03694]},{"body_a":"peg","body_b":"channel_base_body","contact_count":720.0,"contact_point_centroid":[0.50575,0.08089,0.00936],"force_p95":0.55357,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.56796,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.5144,0.17191,0.17871]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49997,0.19877,0.29562]},{"body_a":"peg","body_b":"channel_base_body","contact_count":912.0,"contact_point_centroid":[0.50669,-0.07595,0.00942],"force_p95":0.55559,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.66662,"mean_force":0.54297,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49527,-0.03906,0.09177]},{"body_a":"peg","body_b":"channel_base_body","contact_count":198.0,"contact_point_centroid":[0.50598,0.08087,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55006,"mean_force":0.54677,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51723,0.13557,0.05372]},{"body_a":"peg","body_b":"channel_base_body","contact_count":7.0,"contact_point_centroid":[0.50813,0.08227,0.00938],"force_p95":0.5495,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55006,"mean_force":0.54646,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50611,0.12571,0.04255]},{"body_a":"attachment","body_b":"peg","contact_count":20.0,"contact_point_centroid":[0.50555,-0.05834,0.0538],"force_p95":0.44671,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.52405,"mean_force":0.21916,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49742,-0.0464,0.03884]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":85.0,"contact_point_centroid":[0.52501,-0.07521,0.05661],"force_p95":0.16044,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.28482,"mean_force":0.0238,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49551,-0.0395,0.1102]}],"total_contact_groups":15},"final_pose_error":0.01022,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50685,-0.07511,0.03387],"final_tcp_position":[0.49554,-0.0456,0.14704],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":83.74292,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":749.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.08089,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.55006,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":756.0,"raw_peak_contact_force":4.32595,"tcp_end":[0.52966,0.14616,0.06763],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07724,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":198.0,"n_steps_budget":600.0,"object_pos_end":[0.50599,0.08089,0.03378],"object_pos_start":[0.50599,0.08089,0.03378],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16112,"object_z_max":0.03378,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":224.0,"raw_peak_contact_force":67.95168,"tcp_end":[0.5063,0.12583,0.0428],"tcp_start":[0.52966,0.14616,0.06763],"tcp_to_object_dist_end":0.04584,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":7.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.08087,0.03378],"object_pos_start":[0.50599,0.08089,0.03378],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.16112,"object_z_max":0.03378,"peak_contact_force":50.42369,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":8.0,"raw_peak_contact_force":50.42369,"tcp_end":[0.50584,0.12555,0.04218],"tcp_start":[0.5063,0.12583,0.0428],"tcp_to_object_dist_end":0.04546,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50683,-0.07633,0.03627],"object_pos_start":[0.50599,0.08087,0.03378],"object_to_goal_dist_end":0.0086,"object_to_goal_dist_start":0.1611,"object_z_max":0.03661,"peak_contact_force":0.4001,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1967.0,"raw_peak_contact_force":83.74292,"tcp_end":[0.49875,-0.0475,0.03679],"tcp_start":[0.50584,0.12555,0.04218],"tcp_to_object_dist_end":0.02995,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":916.0,"n_steps_budget":1000.0,"object_pos_end":[0.50685,-0.07511,0.03387],"object_pos_start":[0.50683,-0.07633,0.03627],"object_to_goal_dist_end":0.01041,"object_to_goal_dist_start":0.0086,"object_z_max":0.0363,"peak_contact_force":0.54611,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1019.0,"raw_peak_contact_force":62.09784,"tcp_end":[0.49554,-0.0456,0.14704],"tcp_start":[0.49875,-0.0475,0.03679],"tcp_to_object_dist_end":0.1175,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.43871,"average_solve_count":155.0,"average_success_count":155.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_y":-0.00014,"approach_1.approach_z_offset":0.00777,"contact_1.contact_force":9.67743,"contact_1.speed":0.03004,"push_1.push_depth":0.02748,"push_1.push_speed":0.09963,"retract_1.retract_height":0.093,"retract_1.speed":0.05468},"optimized_scores":{"best_composite_score":0.18141,"best_fitness_score":0.47141,"best_task_score":0.52068},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":743.0,"contact_point_centroid":[0.54595,0.0625,0.05999],"force_p95":129.0733,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":148.24527,"mean_force":107.30784,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5008,0.06551,0.03626]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":113.0,"contact_point_centroid":[0.525,0.06234,0.06],"force_p95":110.4528,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":112.98391,"mean_force":52.29927,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50083,0.06214,0.03655]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.54485,-0.0273,0.05999],"force_p95":70.04374,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":71.90309,"mean_force":56.25263,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50028,-0.02175,0.03676]},{"body_a":"attachment","body_b":"peg","contact_count":369.0,"contact_point_centroid":[0.50323,0.03833,0.04066],"force_p95":23.78517,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":43.24215,"mean_force":4.26376,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50073,0.05003,0.03644]},{"body_a":"peg","body_b":"channel_base_body","contact_count":753.0,"contact_point_centroid":[0.50116,0.02599,0.00963],"force_p95":17.73251,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":43.205,"mean_force":2.52517,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50081,0.066,0.03624]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.55083,0.12,0.05999],"force_p95":14.37905,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":14.37905,"mean_force":14.37905,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50175,0.13746,0.0343]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":94.0,"contact_point_centroid":[0.47463,0.07772,0.03803],"force_p95":2.35988,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.69823,"mean_force":0.56163,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50096,0.10747,0.03598]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":220.0,"contact_point_centroid":[0.52522,0.00214,0.02494],"force_p95":3.80904,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.40498,"mean_force":0.67259,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50068,0.03159,0.03674]},{"body_a":"peg","body_b":"channel_base_body","contact_count":695.0,"contact_point_centroid":[0.50566,0.1046,0.00937],"force_p95":0.57582,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.56261,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50902,0.18184,0.17956]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49983,0.19914,0.2962]},{"body_a":"peg","body_b":"channel_base_body","contact_count":890.0,"contact_point_centroid":[0.50671,-0.05107,0.0094],"force_p95":0.58147,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.80799,"mean_force":0.54695,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49667,-0.01507,0.07834]},{"body_a":"peg","body_b":"channel_base_body","contact_count":148.0,"contact_point_centroid":[0.506,0.10508,0.00939],"force_p95":0.57567,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57589,"mean_force":0.54638,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51199,0.15768,0.0555]},{"body_a":"peg","body_b":"channel_base_body","contact_count":146.0,"contact_point_centroid":[0.50619,0.10448,0.00939],"force_p95":0.57571,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57577,"mean_force":0.54621,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50278,0.14242,0.03754]},{"body_a":"attachment","body_b":"peg","contact_count":13.0,"contact_point_centroid":[0.50661,-0.03255,0.05447],"force_p95":0.23175,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35834,"mean_force":0.0446,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49884,-0.02077,0.03861]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":195.0,"contact_point_centroid":[0.52501,-0.05062,0.0588],"force_p95":0.06838,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.29807,"mean_force":0.01523,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49662,-0.01488,0.08226]}],"total_contact_groups":15},"final_pose_error":0.00997,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50696,-0.05056,0.0338],"final_tcp_position":[0.49682,-0.01999,0.12054],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":148.24527,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":722.0,"n_steps_budget":1000.0,"object_pos_end":[0.50585,0.1047,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18489,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.54289,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":727.0,"raw_peak_contact_force":3.33087,"tcp_end":[0.51924,0.16537,0.06826],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07103,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":148.0,"n_steps_budget":600.0,"object_pos_end":[0.50599,0.10464,0.03384],"object_pos_start":[0.50585,0.1047,0.03384],"object_to_goal_dist_end":0.18484,"object_to_goal_dist_start":0.18489,"object_z_max":0.03384,"peak_contact_force":0.54106,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":148.0,"raw_peak_contact_force":0.57589,"tcp_end":[0.50555,0.14914,0.04356],"tcp_start":[0.51924,0.16537,0.06826],"tcp_to_object_dist_end":0.04555,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":146.0,"n_steps_budget":600.0,"object_pos_end":[0.50591,0.10456,0.03384],"object_pos_start":[0.50599,0.10464,0.03384],"object_to_goal_dist_end":0.18476,"object_to_goal_dist_start":0.18484,"object_z_max":0.03384,"peak_contact_force":14.37905,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":147.0,"raw_peak_contact_force":14.37905,"tcp_end":[0.50174,0.13741,0.03428],"tcp_start":[0.50555,0.14914,0.04356],"tcp_to_object_dist_end":0.03312,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50664,-0.05079,0.03594],"object_pos_start":[0.50591,0.10456,0.03384],"object_to_goal_dist_end":0.03023,"object_to_goal_dist_start":0.18476,"object_z_max":0.03791,"peak_contact_force":96.38893,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2292.0,"raw_peak_contact_force":148.24527,"tcp_end":[0.50028,-0.02161,0.03675],"tcp_start":[0.50174,0.13741,0.03428],"tcp_to_object_dist_end":0.02988,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":892.0,"n_steps_budget":1000.0,"object_pos_end":[0.50696,-0.05056,0.0338],"object_pos_start":[0.50664,-0.05079,0.03594],"object_to_goal_dist_end":0.03088,"object_to_goal_dist_start":0.03023,"object_z_max":0.03594,"peak_contact_force":0.00424,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1101.0,"raw_peak_contact_force":71.90309,"tcp_end":[0.49682,-0.01999,0.12054],"tcp_start":[0.50028,-0.02161,0.03675],"tcp_to_object_dist_end":0.09252,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.36364,"average_solve_count":187.0,"average_success_count":187.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_y":0.00166,"approach_1.approach_z_offset":0.00568,"contact_1.contact_force":7.17947,"contact_1.speed":0.01549,"push_1.push_depth":0.00791,"push_1.push_speed":0.09967,"retract_1.retract_height":0.10803,"retract_1.speed":0.02925},"optimized_scores":{"best_composite_score":0.47807,"best_fitness_score":0.76807,"best_task_score":0.93386},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":694.0,"contact_point_centroid":[0.54312,0.03407,0.05998],"force_p95":108.67076,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":119.67954,"mean_force":89.9238,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49832,0.0356,0.03676]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.54296,-0.04939,0.05999],"force_p95":52.65566,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":52.94648,"mean_force":49.85748,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4983,-0.05345,0.0367]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54284,0.10962,0.05996],"force_p95":49.43718,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":49.43718,"mean_force":49.43718,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49821,0.10832,0.03617]},{"body_a":"peg","body_b":"channel_base_body","contact_count":767.0,"contact_point_centroid":[0.5014,-0.00332,0.00963],"force_p95":17.01526,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":33.59328,"mean_force":2.55737,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49832,0.03671,0.03677]},{"body_a":"attachment","body_b":"peg","contact_count":371.0,"contact_point_centroid":[0.50144,-0.00511,0.04137],"force_p95":20.70471,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":33.30765,"mean_force":4.53821,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49845,0.00657,0.03685]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":103.0,"contact_point_centroid":[0.52514,-0.03538,0.02848],"force_p95":8.26113,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.1161,"mean_force":1.6172,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49839,-0.00689,0.0368]},{"body_a":"peg","body_b":"channel_base_body","contact_count":9.0,"contact_point_centroid":[0.50567,-0.10027,0.04927],"force_p95":9.54725,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.10643,"mean_force":2.2586,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49832,-0.05228,0.03673]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":151.0,"contact_point_centroid":[0.47478,-0.00598,0.02419],"force_p95":1.65747,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.96181,"mean_force":0.63254,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49861,0.0236,0.03697]},{"body_a":"peg","body_b":"channel_base_body","contact_count":186.0,"contact_point_centroid":[0.50497,-0.10011,0.05642],"force_p95":2.47553,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.12735,"mean_force":0.44095,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4952,-0.04737,0.06685]},{"body_a":"attachment","body_b":"peg","contact_count":22.0,"contact_point_centroid":[0.5051,-0.06483,0.05457],"force_p95":5.35781,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.49893,"mean_force":2.45806,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49709,-0.05285,0.03787]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50493,-0.08217,0.0094],"force_p95":0.60002,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.01662,"mean_force":0.56907,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49472,-0.04511,0.08195]},{"body_a":"peg","body_b":"channel_base_body","contact_count":720.0,"contact_point_centroid":[0.50302,0.06746,0.00935],"force_p95":0.55476,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.5586,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49876,0.16541,0.18149]},{"body_a":"peg","body_b":"channel_base_body","contact_count":386.0,"contact_point_centroid":[0.50307,0.06741,0.00938],"force_p95":0.55058,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55081,"mean_force":0.54664,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49763,0.1184,0.04881]},{"body_a":"peg","body_b":"channel_base_body","contact_count":8.0,"contact_point_centroid":[0.50501,0.06641,0.00938],"force_p95":0.54957,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55056,"mean_force":0.54679,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49841,0.10846,0.03647]}],"total_contact_groups":14},"final_pose_error":0.01739,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50488,-0.08196,0.03378],"final_tcp_position":[0.49489,-0.04887,0.12825],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":119.67954,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":736.0,"n_steps_budget":1000.0,"object_pos_end":[0.50306,0.0675,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14766,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.5503,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":720.0,"raw_peak_contact_force":2.06903,"tcp_end":[0.49918,0.13222,0.06864],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07361,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":386.0,"n_steps_budget":600.0,"object_pos_end":[0.50303,0.0675,0.0338],"object_pos_start":[0.50306,0.0675,0.0338],"object_to_goal_dist_end":0.14766,"object_to_goal_dist_start":0.14766,"object_z_max":0.0338,"peak_contact_force":0.54555,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":386.0,"raw_peak_contact_force":0.55081,"tcp_end":[0.49857,0.10858,0.03672],"tcp_start":[0.49918,0.13222,0.06864],"tcp_to_object_dist_end":0.04143,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":8.0,"n_steps_budget":900.0,"object_pos_end":[0.50301,0.06748,0.0338],"object_pos_start":[0.50303,0.0675,0.0338],"object_to_goal_dist_end":0.14764,"object_to_goal_dist_start":0.14766,"object_z_max":0.0338,"peak_contact_force":49.43718,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":9.0,"raw_peak_contact_force":49.43718,"tcp_end":[0.49816,0.10827,0.03609],"tcp_start":[0.49857,0.10858,0.03672],"tcp_to_object_dist_end":0.04114,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50559,-0.08324,0.03487],"object_pos_start":[0.50301,0.06748,0.0338],"object_to_goal_dist_end":0.00825,"object_to_goal_dist_start":0.14764,"object_z_max":0.03768,"peak_contact_force":67.22769,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2095.0,"raw_peak_contact_force":119.67954,"tcp_end":[0.4983,-0.05323,0.0367],"tcp_start":[0.49816,0.10827,0.03609],"tcp_to_object_dist_end":0.03094,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50488,-0.08196,0.03378],"object_pos_start":[0.50559,-0.08324,0.03487],"object_to_goal_dist_end":0.00815,"object_to_goal_dist_start":0.00825,"object_z_max":0.03499,"peak_contact_force":0.51264,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1212.0,"raw_peak_contact_force":52.94648,"tcp_end":[0.49489,-0.04887,0.12825],"tcp_start":[0.4983,-0.05323,0.0367],"tcp_to_object_dist_end":0.10059,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```