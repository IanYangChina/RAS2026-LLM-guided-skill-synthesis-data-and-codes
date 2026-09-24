## Search State

- **Seed**: 7
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → align → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | impedance_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.1412 | 0.54 | ❌ rejected |
| 13 | approach → align → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | -0.1555 | 0.14 | ❌ rejected |
| 12 | approach → align → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | impedance_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.2088 | 0.42 | ❌ rejected |
| 11 | approach → align → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.3926 | 0.72 | ✅ accepted |
| 10 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.2442 | 0.27 | ❌ rejected |

**Proposal policy**: task_score is 0.54 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415`
- Frozen object start: [0.5100076373283734, 0.11177710407756605, 0.04]
- Frozen task target: [0.5100076373283734, -0.04822289592243395, 0.04]
- Goal object position: (0.5100076373283734, -0.04822289592243395, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5100076373283734, 0.11177710407756605, 0.04)
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
  frozen_object_start: [0.51, 0.1118, 0.04]
  frozen_task_target: [0.51, -0.0482, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5100076373283734, 0.11177710407756605, 0.04]}
  frozen_targets: {'channel_exit': [0.5100076373283734, -0.04822289592243395, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415

## Subtask Layer

**Mode**: free (you define subtask targets; use `subtasks:` block in your YAML)

Define subtasks in a `subtasks:` block **before** `phases:`. Each subtask specifies an intermediate optimisation target.

**Required fields** — always include both, never omit:
- `anchor` (**required**): fixture | goal | object | world
- `target_entity` (**required**): hinge | object | tcp

Subtask anchors are separate from phase `target.anchor` vocabulary: subtasks use `world | object | goal | fixture`, while phase targets use `world | task_goal | task_object | fixture | body | site | current_tcp`.

Optional fields:
- `metric`: contact | distance | goal_progress | hinge_angle (default: distance)
- `offset`: [x, y, z] in metres relative to anchor (default: [0, 0, 0])
- `param_offset_key`: CMA-ES parameter added to offset at runtime (optional)
- `weight`: scoring weight [0.1, 1.0] (default: 1.0)

**Anchor resolution for this task** — choose anchor so the resolved position is meaningful:
| Anchor | Resolves to | Best used for |
|--------|-------------|---------------|
| `world` | absolute world-frame coordinate | fixed reference points not tied to objects |
| `object` | offset from object initial position (0.5100076373283734, 0.11177710407756605, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5100076373283734, -0.04822289592243395, 0.04) | final destination targets |
| `fixture` | offset from fixture pose (0.54, 0.0, 0.035) | approach/contact targets near fixture |

Annotate each phase with `subtask_id: <id>` to bind it to a subtask.
Only the **last phase** bound to a given subtask contributes to subtask scoring.

Example (two subtasks — one near object start, one at goal):
```yaml
subtasks:
  - id: reach_pre_contact
    anchor: object         # resolved to object initial position (see table above)
    target_entity: tcp     # score TCP distance to this target
    metric: distance
    offset: [0.0, 0.0, 0.10]  # 10 cm above object start position
    weight: 0.3
  - id: reach_goal
    anchor: goal           # resolved to task goal position (see table above)
    target_entity: tcp
    metric: distance
    offset: [0.0, 0.0, 0.0]
    weight: 0.7
phases:
  - id: approach_1
    type: approach
    subtask_id: reach_pre_contact
    ...
  - id: push_1
    type: push
    subtask_id: reach_goal
    ...
```

## Current Skill (Q=0.141) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: align_standoff
  anchor: object
  offset:
  - 0.0
  - 0.02
  - 0.05
  weight: 0.3
- id: push_goal
  metric: goal_progress
  weight: 0.7
phases:
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
    - 0.05
    tolerance: 0.005
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: align_standoff
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
    - 0.02
    - 0.0
    tolerance: 0.005
  parameters:
    align_speed:
      type: scalar
      range:
      - 0.005
      - 0.03
      default: 0.01
      binds_to:
      - path: generator.speed
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
    - 0.0
    - 0.0
  parameters:
    contact_force:
      type: scalar
      range:
      - 1.0
      - 10.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    speed:
      type: scalar
      range:
      - 0.005
      - 0.03
      default: 0.01
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: align_standoff
- id: push_1
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.16
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.14
      - 0.2
      default: 0.16
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 1
    strategy: reduce_speed
  subtask_id: push_goal
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.05
    tolerance: 0.01
  parameters:
    retract_speed:
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
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.02, 0.05], tolerance=0.005
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **align_1** (`align`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.02, 0.0], tolerance=0.005
  - parameter_bindings:
    - align_speed: status=consumed; consumers=generator.speed (replace)
- **contact_1** (`contact`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.16, mode=add_to_offset, sign=positive}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=1, strategy=reduce_speed
- **retract_1** (`retract`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.05], tolerance=0.01
  - parameter_bindings:
    - retract_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.141
- **task_score** (E): 0.536
- **fitness_score**: 0.331  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.390

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2151 |
| align_1 | 1.00 | 1.00 | 0.0561 |
| contact_1 | 1.00 | 1.00 | 0.0007 |
| push_1 | 0.00 | 1.00 | 0.0002 |
| retract_1 | 0.67 | 1.00 | 0.1220 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.505, 0.131, 0.098) | (0.509, 0.098, 0.040)→(0.502, 0.098, 0.034) | 0.179→0.178 | 1.00 / 1.000 | 0.532 | 2.732 |
| align_1 | align | 1.00 / step_budget | (0.505, 0.131, 0.098)→(0.498, 0.128, 0.043) | (0.502, 0.098, 0.034)→(0.502, 0.098, 0.034) | 0.178→0.178 | 1.00 / 1.333 | 112.786 | 115.832 |
| contact_1 | contact | 1.00 / force_exceeded | (0.498, 0.128, 0.043)→(0.498, 0.128, 0.043) | (0.502, 0.098, 0.034)→(0.502, 0.098, 0.034) | 0.178→0.178 | 1.00 / 2.000 | 24.942 | 24.942 |
| push_1 | push | 0.00 / guard_failure | (0.496, 0.063, 0.039)→(0.496, 0.063, 0.039) | (0.502, 0.098, 0.034)→(0.507, 0.034, 0.036) | 0.178→0.115 | 1.00 / 2.667 | 26.369 | 86.364 |
| retract_1 | retract | 0.67 / step_budget | (0.496, 0.063, 0.039)→(0.495, -0.051, 0.077) | (0.507, 0.034, 0.036)→(0.501, -0.011, 0.027) | 0.114→0.072 | 1.00 / 1.667 | 0.554 | 84.287 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 1.000
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 1.000
- phase_score: 0.326
- phase_breakdown.push_goal_score: 0.305
- phase_breakdown.align_standoff_score: 0.375

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.596
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.076
- **K-run variance**: 0.0380
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.321


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `474e87cb3f7f98c9c8d99c8760356b7c026b70b97898f68d5a6c39ba94bca956`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `a79e5fd8fc80d9ecadd30a274b12d8d7e7d0841df5ca68ae512c46dc86b114e6`; realized-scene SHA-256: `d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51001,0.11178,0.04]},{"name":"goal","value":[0.51001,-0.04822,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.51001,0.11178,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.51001,-0.04822,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.7303,"average_solve_count":330.0,"average_success_count":330.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.0197,"approach_1.speed":0.02862,"contact_1.contact_force":4.59352,"contact_1.contact_speed":0.01563,"push_1.push_speed":0.03528,"retract_1.retract_speed":0.04603},"optimized_scores":{"best_composite_score":0.40577,"best_fitness_score":0.59577,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.54057,-0.0176,0.06],"force_p95":68.43945,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":68.73404,"mean_force":65.78817,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49622,-0.02043,0.03587]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.54055,-0.0185,0.05998],"force_p95":60.70867,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":65.23612,"mean_force":45.92473,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49619,-0.02129,0.03584]},{"body_a":"attachment","body_b":"peg","contact_count":294.0,"contact_point_centroid":[0.50214,0.04946,0.0424],"force_p95":24.24246,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.25122,"mean_force":7.1068,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49641,0.06081,0.0371]},{"body_a":"peg","body_b":"channel_base_body","contact_count":176.0,"contact_point_centroid":[0.50539,0.02426,0.00984],"force_p95":24.18364,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":26.53499,"mean_force":11.39047,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49659,0.06803,0.03741]},{"body_a":"attachment","body_b":"peg","contact_count":391.0,"contact_point_centroid":[0.50071,-0.05719,0.05449],"force_p95":16.92944,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.97648,"mean_force":7.32324,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49429,-0.04754,0.05657]},{"body_a":"peg","body_b":"channel_base_body","contact_count":323.0,"contact_point_centroid":[0.50511,-0.10018,0.03889],"force_p95":13.70359,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.44199,"mean_force":6.59466,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.495,-0.06176,0.0695]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":243.0,"contact_point_centroid":[0.52511,0.02054,0.02639],"force_p95":8.21154,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.921,"mean_force":1.79621,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49618,0.04766,0.03662]},{"body_a":"peg","body_b":"channel_base_body","contact_count":6.0,"contact_point_centroid":[0.51403,0.09852,0.00961],"force_p95":6.98982,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.2357,"mean_force":2.40068,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50001,0.14126,0.04262]},{"body_a":"attachment","body_b":"peg","contact_count":4.0,"contact_point_centroid":[0.50349,0.12934,0.05012],"force_p95":7.147,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.87483,"mean_force":3.2197,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49988,0.14121,0.04244]},{"body_a":"peg","body_b":"channel_base_body","contact_count":199.0,"contact_point_centroid":[0.50408,0.10951,0.00942],"force_p95":0.61444,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.82657,"mean_force":0.6288,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50228,0.14278,0.07143]},{"body_a":"attachment","body_b":"peg","contact_count":6.0,"contact_point_centroid":[0.50346,0.12965,0.05472],"force_p95":6.80617,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.41611,"mean_force":3.3159,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50057,0.14159,0.04834]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":289.0,"contact_point_centroid":[0.52509,-0.08342,0.05084],"force_p95":5.99933,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.36663,"mean_force":3.28158,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4947,-0.05687,0.06509]},{"body_a":"peg","body_b":"channel_base_body","contact_count":449.0,"contact_point_centroid":[0.50563,-0.06486,0.00991],"force_p95":3.08147,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.86209,"mean_force":0.92013,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49434,-0.04594,0.05472]},{"body_a":"peg","body_b":"channel_base_body","contact_count":677.0,"contact_point_centroid":[0.50362,0.11165,0.00938],"force_p95":0.61095,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.55568,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50211,0.17155,0.19615]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4997,0.19943,0.29918]}],"total_contact_groups":15},"final_pose_error":0.00994,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50613,-0.07242,0.03171],"final_tcp_position":[0.49601,-0.07599,0.08183],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":68.73404,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":699.0,"n_steps_budget":1000.0,"object_pos_end":[0.5037,0.11172,0.0339],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19185,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.55106,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":693.0,"raw_peak_contact_force":2.06328,"subtask_id":"align_standoff","tcp_end":[0.50588,0.14465,0.09862],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07265,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":199.0,"n_steps_budget":1000.0,"object_pos_end":[0.50396,0.11138,0.03441],"object_pos_start":[0.5037,0.11172,0.0339],"object_to_goal_dist_end":0.1915,"object_to_goal_dist_start":0.19185,"object_z_max":0.03441,"peak_contact_force":0.44837,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":205.0,"raw_peak_contact_force":7.82657,"tcp_end":[0.50033,0.14137,0.04311],"tcp_start":[0.50588,0.14465,0.09862],"tcp_to_object_dist_end":0.03143,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":6.0,"n_steps_budget":900.0,"object_pos_end":[0.50364,0.11143,0.03438],"object_pos_start":[0.50396,0.11138,0.03441],"object_to_goal_dist_end":0.19154,"object_to_goal_dist_start":0.1915,"object_z_max":0.03441,"peak_contact_force":8.2357,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":10.0,"raw_peak_contact_force":8.2357,"subtask_id":"align_standoff","tcp_end":[0.49962,0.14109,0.04209],"tcp_start":[0.50033,0.14137,0.04311],"tcp_to_object_dist_end":0.03091,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":428.0,"n_steps_budget":1000.0,"object_pos_end":[0.50719,-0.04942,0.03701],"object_pos_start":[0.50364,0.11143,0.03438],"object_to_goal_dist_end":0.03156,"object_to_goal_dist_start":0.19154,"object_z_max":0.03825,"peak_contact_force":1.12685,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":715.0,"raw_peak_contact_force":68.73404,"subtask_id":"push_goal","tcp_end":[0.49621,-0.02096,0.03585],"tcp_start":[0.49622,-0.02073,0.03587],"tcp_to_object_dist_end":0.03053,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":695.0,"n_steps_budget":1000.0,"object_pos_end":[0.50613,-0.07242,0.03171],"object_pos_start":[0.50702,-0.05041,0.03675],"object_to_goal_dist_end":0.01279,"object_to_goal_dist_start":0.03059,"object_z_max":0.04766,"peak_contact_force":0.33798,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1457.0,"raw_peak_contact_force":65.23612,"tcp_end":[0.49601,-0.07599,0.08183],"tcp_start":[0.49621,-0.02096,0.03585],"tcp_to_object_dist_end":0.05125,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `3ca2e925d364d2c0fe81fb71ee31d40f947a20e349a0720e1c44a2dd2bc628da`; realized-scene SHA-256: `c5fb87552d009c7e1ef813cadc54d289d6d9c896c1dd51a37fa468bf6305165e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48616,0.11898,0.04]},{"name":"goal","value":[0.48616,-0.04102,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48616,0.11898,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48616,-0.04102,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.92641,"average_solve_count":231.0,"average_success_count":231.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.02234,"approach_1.speed":0.04911,"contact_1.contact_force":2.12528,"contact_1.contact_speed":0.0189,"push_1.push_speed":0.02513,"retract_1.retract_speed":0.07213},"optimized_scores":{"best_composite_score":0.0757,"best_fitness_score":0.2657,"best_task_score":0.47466},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.53251,0.11775,0.05999],"force_p95":109.78426,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":112.37739,"mean_force":86.44606,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48781,0.11413,0.03662]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":15.0,"contact_point_centroid":[0.53235,0.1152,0.05998],"force_p95":83.26952,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":108.00469,"mean_force":55.93853,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48761,0.1117,0.03666]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":36.0,"contact_point_centroid":[0.475,0.08515,0.04614],"force_p95":36.07767,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":48.21355,"mean_force":23.53196,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48579,0.08507,0.04091]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":442.0,"contact_point_centroid":[0.52541,0.06605,0.03007],"force_p95":29.01992,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":33.88988,"mean_force":16.4647,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4861,0.08054,0.04217]},{"body_a":"attachment","body_b":"peg","contact_count":436.0,"contact_point_centroid":[0.49598,0.07526,0.04077],"force_p95":29.31058,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":32.77891,"mean_force":22.76422,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48604,0.08098,0.04203]},{"body_a":"peg","body_b":"channel_base_body","contact_count":57.0,"contact_point_centroid":[0.49723,0.0927,0.0097],"force_p95":24.80859,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":26.01455,"mean_force":10.62821,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48806,0.13533,0.03842]},{"body_a":"attachment","body_b":"peg","contact_count":58.0,"contact_point_centroid":[0.49444,0.12346,0.04431],"force_p95":24.55753,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":25.79881,"mean_force":9.99756,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48791,0.13475,0.03821]},{"body_a":"peg","body_b":"channel_base_body","contact_count":987.0,"contact_point_centroid":[0.50065,0.0473,0.00889],"force_p95":20.28811,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":24.00076,"mean_force":7.17352,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4884,0.043,0.05186]},{"body_a":"peg","body_b":"link7","contact_count":130.0,"contact_point_centroid":[0.52101,0.07886,0.0664],"force_p95":11.76132,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.17672,"mean_force":8.60338,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48617,0.09966,0.03801]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":27.0,"contact_point_centroid":[0.47496,0.01121,0.02441],"force_p95":9.3922,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.82963,"mean_force":3.52928,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48942,0.02508,0.05617]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":11.0,"contact_point_centroid":[0.52522,0.094,0.0139],"force_p95":9.32545,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.43701,"mean_force":2.58872,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48777,0.11567,0.0367]},{"body_a":"peg","body_b":"channel_base_body","contact_count":4.0,"contact_point_centroid":[0.49431,0.10265,0.00932],"force_p95":3.66645,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20529,"mean_force":1.49328,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48967,0.14876,0.04118]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.49554,0.13685,0.05331],"force_p95":3.85028,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.85028,"mean_force":3.85028,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48951,0.14868,0.04095]},{"body_a":"peg","body_b":"channel_base_body","contact_count":650.0,"contact_point_centroid":[0.49613,0.11909,0.00944],"force_p95":0.61406,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.55125,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49089,0.17487,0.19612]},{"body_a":"peg","body_b":"channel_base_body","contact_count":225.0,"contact_point_centroid":[0.49614,0.11869,0.00942],"force_p95":0.61066,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.15349,"mean_force":0.55491,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.48553,0.14985,0.07042]},{"body_a":"attachment","body_b":"peg","contact_count":5.0,"contact_point_centroid":[0.49552,0.13709,0.05671],"force_p95":0.94547,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.97572,"mean_force":0.78113,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.48939,0.1489,0.04395]}],"total_contact_groups":17},"final_pose_error":0.05451,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49315,0.03509,0.02414],"final_tcp_position":[0.49298,-0.02931,0.07122],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":112.37739,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":675.0,"n_steps_budget":1000.0,"object_pos_end":[0.49604,0.11955,0.03386],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19968,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.49923,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":674.0,"raw_peak_contact_force":2.24822,"subtask_id":"align_standoff","tcp_end":[0.48372,0.15143,0.09934],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07386,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":225.0,"n_steps_budget":1000.0,"object_pos_end":[0.49599,0.11893,0.0337],"object_pos_start":[0.49604,0.11955,0.03386],"object_to_goal_dist_end":0.19907,"object_to_goal_dist_start":0.19968,"object_z_max":0.03394,"peak_contact_force":0.61649,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":230.0,"raw_peak_contact_force":1.15349,"tcp_end":[0.48982,0.14883,0.04145],"tcp_start":[0.48372,0.15143,0.09934],"tcp_to_object_dist_end":0.03149,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":4.0,"n_steps_budget":750.0,"object_pos_end":[0.49605,0.11889,0.0337],"object_pos_start":[0.49599,0.11893,0.0337],"object_to_goal_dist_end":0.19903,"object_to_goal_dist_start":0.19907,"object_z_max":0.0337,"peak_contact_force":4.20529,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":5.0,"raw_peak_contact_force":4.20529,"subtask_id":"align_standoff","tcp_end":[0.48942,0.14864,0.04082],"tcp_start":[0.48982,0.14883,0.04145],"tcp_to_object_dist_end":0.0313,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":97.0,"n_steps_budget":1000.0,"object_pos_end":[0.50646,0.08875,0.0373],"object_pos_start":[0.49605,0.11889,0.0337],"object_to_goal_dist_end":0.16889,"object_to_goal_dist_start":0.19903,"object_z_max":0.03924,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":128.0,"raw_peak_contact_force":112.37739,"subtask_id":"push_goal","tcp_end":[0.48785,0.1136,0.03659],"tcp_start":[0.48783,0.11383,0.03661],"tcp_to_object_dist_end":0.03106,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49315,0.03509,0.02414],"object_pos_start":[0.50669,0.08829,0.03736],"object_to_goal_dist_end":0.11638,"object_to_goal_dist_start":0.16844,"object_z_max":0.0405,"peak_contact_force":0.68573,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2073.0,"raw_peak_contact_force":108.00469,"tcp_end":[0.49298,-0.02931,0.07122],"tcp_start":[0.48785,0.1136,0.03659],"tcp_to_object_dist_end":0.07977,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `f85f1938a541e3d507519c8f918b8ca98f1f9baf6ab2f6f3ba2c32478e079e47`; realized-scene SHA-256: `a0d7ea14565b0a67e86de15fa43f3773b761884db645527685cd53e0fd95aeb9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.52962,0.06295,0.04]},{"name":"goal","value":[0.52962,-0.09705,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.52962,0.06295,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.52962,-0.09705,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.60853,"average_solve_count":258.0,"average_success_count":258.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.01535,"approach_1.speed":0.0462,"contact_1.contact_force":6.69449,"contact_1.contact_speed":0.02332,"push_1.push_speed":0.03712,"retract_1.retract_speed":0.05017},"optimized_scores":{"best_composite_score":-0.05786,"best_fitness_score":0.13214,"best_task_score":0.13476},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":429.0,"contact_point_centroid":[0.52503,0.09489,0.05998],"force_p95":336.8386,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":338.51539,"mean_force":328.75467,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50737,0.09483,0.05008]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.525,0.09515,0.06],"force_p95":79.61877,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":79.61877,"mean_force":79.61877,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50509,0.09504,0.04584]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.52501,0.09514,0.05999],"force_p95":77.70234,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":77.98012,"mean_force":74.55308,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50514,0.09503,0.04588]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.52502,0.09514,0.05999],"force_p95":62.38585,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":62.38585,"mean_force":62.38585,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50519,0.09503,0.04593]},{"body_a":"peg","body_b":"channel_base_body","contact_count":984.0,"contact_point_centroid":[0.50405,0.01544,0.00869],"force_p95":7.15483,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.13005,"mean_force":2.04003,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49918,0.0202,0.06004]},{"body_a":"attachment","body_b":"peg","contact_count":285.0,"contact_point_centroid":[0.50403,0.05747,0.04697],"force_p95":8.42722,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.74325,"mean_force":5.13649,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50089,0.06879,0.04823]},{"body_a":"peg","body_b":"channel_base_body","contact_count":774.0,"contact_point_centroid":[0.50579,0.06295,0.00936],"force_p95":0.55649,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.56404,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51156,0.14751,0.1938]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49975,0.19838,0.29679]},{"body_a":"peg","body_b":"channel_base_body","contact_count":575.0,"contact_point_centroid":[0.50604,0.06307,0.00938],"force_p95":0.55274,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55532,"mean_force":0.54657,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50985,0.09521,0.0569]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.49798,0.04917,0.00939],"force_p95":0.55252,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55347,"mean_force":0.5471,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50514,0.09503,0.04588]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.51903,0.0506,0.00939],"force_p95":0.54451,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54451,"mean_force":0.54451,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50519,0.09503,0.04593]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":9.0,"contact_point_centroid":[0.52505,0.05698,0.0127],"force_p95":0.35706,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.37143,"mean_force":0.322,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50216,0.07425,0.04828]}],"total_contact_groups":12},"final_pose_error":0.03399,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5048,0.00486,0.02415],"final_tcp_position":[0.49706,-0.04865,0.0772],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":338.51539,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":802.0,"n_steps_budget":1000.0,"object_pos_end":[0.50595,0.06302,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14328,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54643,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":808.0,"raw_peak_contact_force":3.88411,"subtask_id":"align_standoff","tcp_end":[0.52434,0.09829,0.09644],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07419,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":575.0,"n_steps_budget":1000.0,"object_pos_end":[0.50602,0.06295,0.03381],"object_pos_start":[0.50595,0.06302,0.03381],"object_to_goal_dist_end":0.14321,"object_to_goal_dist_start":0.14328,"object_z_max":0.03381,"peak_contact_force":337.29327,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1004.0,"raw_peak_contact_force":338.51539,"tcp_end":[0.50519,0.09503,0.04593],"tcp_start":[0.52434,0.09829,0.09644],"tcp_to_object_dist_end":0.0343,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":690.0,"object_pos_end":[0.50599,0.06294,0.03381],"object_pos_start":[0.50602,0.06295,0.03381],"object_to_goal_dist_end":0.1432,"object_to_goal_dist_start":0.14321,"object_z_max":0.03381,"peak_contact_force":62.38585,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":62.38585,"subtask_id":"align_standoff","tcp_end":[0.50517,0.09503,0.04591],"tcp_start":[0.50519,0.09503,0.04593],"tcp_to_object_dist_end":0.03431,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50596,0.06294,0.03381],"object_pos_start":[0.50599,0.06294,0.03381],"object_to_goal_dist_end":0.1432,"object_to_goal_dist_start":0.1432,"object_z_max":0.03381,"peak_contact_force":77.98012,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":6.0,"raw_peak_contact_force":77.98012,"subtask_id":"push_goal","tcp_end":[0.50509,0.09504,0.04584],"tcp_start":[0.50512,0.09504,0.04586],"tcp_to_object_dist_end":0.03429,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5048,0.00486,0.02415],"object_pos_start":[0.50594,0.06299,0.03381],"object_to_goal_dist_end":0.08646,"object_to_goal_dist_start":0.14325,"object_z_max":0.0406,"peak_contact_force":0.63891,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1279.0,"raw_peak_contact_force":79.61877,"tcp_end":[0.49706,-0.04865,0.0772],"tcp_start":[0.50509,0.09504,0.04584],"tcp_to_object_dist_end":0.07574,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```