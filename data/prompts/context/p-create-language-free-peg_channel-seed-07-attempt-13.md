## Search State

- **Seed**: 7
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → align → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | -0.1555 | 0.14 | ❌ rejected |
| 12 | approach → align → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | impedance_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.2088 | 0.42 | ❌ rejected |
| 11 | approach → align → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.3926 | 0.72 | ✅ accepted |
| 10 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.2442 | 0.27 | ❌ rejected |
| 9 | approach → contact → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | position_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.2975 | 0.56 | ❌ rejected |

**Proposal policy**: task_score is 0.14 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.156) — your mutation base

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

- **Composite score**: -0.156
- **task_score** (E): 0.136
- **fitness_score**: 0.134  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.490

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 0.67 | 1.00 | 0.1955 |
| align_1 | 1.00 | 1.00 | 0.0652 |
| contact_1 | 1.00 | 1.00 | 0.0001 |
| push_1 | 0.00 | 1.00 | 0.0000 |
| retract_1 | 0.00 | 1.00 | 0.0176 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 0.67 / step_budget | (0.500, 0.200, 0.300)→(0.503, 0.115, 0.126) | (0.509, 0.098, 0.040)→(0.502, 0.098, 0.034) | 0.179→0.178 | 1.00 / 1.000 | 0.567 | 2.732 |
| align_1 | align | 1.00 / step_budget | (0.503, 0.115, 0.126)→(0.499, 0.098, 0.063) | (0.502, 0.098, 0.034)→(0.503, 0.091, 0.032) | 0.178→0.171 | 1.00 / 2.000 | 110.765 | 154.605 |
| contact_1 | contact | 1.00 / force_exceeded | (0.499, 0.098, 0.063)→(0.499, 0.098, 0.063) | (0.503, 0.091, 0.032)→(0.503, 0.090, 0.032) | 0.171→0.171 | 1.00 / 2.333 | 71.323 | 71.323 |
| push_1 | push | 0.00 / guard_failure | (0.499, 0.098, 0.063)→(0.499, 0.098, 0.063) | (0.503, 0.090, 0.032)→(0.503, 0.090, 0.032) | 0.171→0.171 | 1.00 / 2.333 | 52.191 | 88.383 |
| retract_1 | retract | 0.00 / step_budget | (0.499, 0.098, 0.063)→(0.502, 0.082, 0.067) | (0.503, 0.090, 0.032)→(0.507, 0.068, 0.034) | 0.171→0.148 | 1.00 / 4.333 | 245.343 | 265.404 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.290
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.290
- phase_score: 0.140
- phase_breakdown.push_goal_score: 0.000
- phase_breakdown.align_standoff_score: 0.466

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.200
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.290
- **Median Q (composite search score)**: -0.161
- **K-run variance**: 0.0026
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Parameters at upper bound**: approach_1.speed
- **Final σ (mean)**: 0.404


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.90361,"average_solve_count":166.0,"average_success_count":166.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.02045,"approach_1.speed":0.0893,"contact_1.contact_force":2.75635,"contact_1.speed":0.00692,"push_1.max_push_force":31.96366,"push_1.push_distance":0.16572,"push_1.push_speed":0.04803,"retract_1.retract_speed":0.04558},"optimized_scores":{"best_composite_score":-0.09018,"best_fitness_score":0.19982,"best_task_score":0.28964},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50187,0.11454,0.00857],"force_p95":123.52382,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":220.46234,"mean_force":66.37047,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50048,0.11146,0.0731]},{"body_a":"attachment","body_b":"peg","contact_count":620.0,"contact_point_centroid":[0.50188,0.12123,0.05401],"force_p95":124.45621,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":220.04387,"mean_force":106.19328,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50109,0.10958,0.06434]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":892.0,"contact_point_centroid":[0.52501,0.11995,0.0448],"force_p95":185.02358,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":201.49752,"mean_force":162.69979,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49828,0.08471,0.06887]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.5,0.10297,0.00793],"force_p95":93.06917,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":93.69202,"mean_force":83.11228,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49771,0.10187,0.06521]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.49863,0.11379,0.0538],"force_p95":92.52658,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":93.13392,"mean_force":82.61162,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49771,0.10187,0.06521]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50085,0.08633,0.00892],"force_p95":82.88649,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":90.18422,"mean_force":57.18428,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49825,0.08567,0.06864]},{"body_a":"attachment","body_b":"peg","contact_count":1000.0,"contact_point_centroid":[0.49944,0.09237,0.05672],"force_p95":82.40514,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":89.72841,"mean_force":56.73591,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49825,0.08567,0.06864]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.49656,0.11352,0.00791],"force_p95":80.81207,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":80.81207,"mean_force":80.81207,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49772,0.10193,0.06519]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.49866,0.11396,0.05375],"force_p95":80.25442,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":80.25442,"mean_force":80.25442,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49772,0.10193,0.06519]},{"body_a":"world","body_b":"link6","contact_count":598.0,"contact_point_centroid":[0.51171,0.27185,-1e-05],"force_p95":65.21801,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":69.92742,"mean_force":37.71137,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49833,0.08472,0.06899]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":30.0,"contact_point_centroid":[0.47424,0.11383,0.05597],"force_p95":43.44611,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":46.97766,"mean_force":22.64334,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.47957,0.11791,0.06465]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":51.0,"contact_point_centroid":[0.52507,0.06621,0.02725],"force_p95":5.83815,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.89265,"mean_force":2.75519,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49883,0.08433,0.06928]},{"body_a":"peg","body_b":"channel_base_body","contact_count":978.0,"contact_point_centroid":[0.50363,0.11169,0.00938],"force_p95":0.60768,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.55284,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50199,0.15754,0.20103]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49968,0.19932,0.29917]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":11.0,"contact_point_centroid":[0.52519,0.10832,0.05827],"force_p95":0.27513,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.32267,"mean_force":0.07092,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49011,0.11236,0.08307]}],"total_contact_groups":15},"final_pose_error":0.1656,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50734,0.06543,0.03403],"final_tcp_position":[0.49891,0.0843,0.06929],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":220.46234,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50373,0.11176,0.03385],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.1919,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.55015,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":994.0,"raw_peak_contact_force":2.06328,"subtask_id":"align_standoff","tcp_end":[0.50568,0.11828,0.11144],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07789,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.09632,0.03087],"object_pos_start":[0.50373,0.11176,0.03385],"object_to_goal_dist_end":0.17656,"object_to_goal_dist_start":0.1919,"object_z_max":0.03645,"peak_contact_force":112.29773,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1661.0,"raw_peak_contact_force":220.46234,"tcp_end":[0.49772,0.10193,0.06519],"tcp_start":[0.50568,0.11828,0.11144],"tcp_to_object_dist_end":0.03494,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50119,0.09627,0.03088],"object_pos_start":[0.50118,0.09632,0.03087],"object_to_goal_dist_end":0.17651,"object_to_goal_dist_start":0.17656,"object_z_max":0.03087,"peak_contact_force":80.81207,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":80.81207,"subtask_id":"align_standoff","tcp_end":[0.49771,0.1019,0.0652],"tcp_start":[0.49772,0.10193,0.06519],"tcp_to_object_dist_end":0.03495,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.5012,0.09621,0.03089],"object_pos_start":[0.50119,0.09627,0.03088],"object_to_goal_dist_end":0.17645,"object_to_goal_dist_start":0.17651,"object_z_max":0.03089,"peak_contact_force":68.18133,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":6.0,"raw_peak_contact_force":93.69202,"subtask_id":"push_goal","tcp_end":[0.49771,0.10185,0.06522],"tcp_start":[0.4977,0.10185,0.06522],"tcp_to_object_dist_end":0.03496,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50734,0.06543,0.03403],"object_pos_start":[0.50122,0.09614,0.03089],"object_to_goal_dist_end":0.14574,"object_to_goal_dist_start":0.17638,"object_z_max":0.03401,"peak_contact_force":186.69974,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3541.0,"raw_peak_contact_force":201.49752,"tcp_end":[0.49891,0.0843,0.06929],"tcp_start":[0.49771,0.10185,0.06522],"tcp_to_object_dist_end":0.04086,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.77451,"average_solve_count":204.0,"average_success_count":204.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.02317,"approach_1.speed":0.04633,"contact_1.contact_force":7.64955,"contact_1.speed":0.01843,"push_1.max_push_force":41.80746,"push_1.push_distance":0.17375,"push_1.push_speed":0.04197,"retract_1.retract_speed":0.05505},"optimized_scores":{"best_composite_score":-0.16133,"best_fitness_score":0.12867,"best_task_score":0.11257},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":839.0,"contact_point_centroid":[0.52502,0.11993,0.05681],"force_p95":226.94391,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":245.06971,"mean_force":181.28888,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49235,0.08359,0.06914]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49439,0.11952,0.00829],"force_p95":128.70585,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":135.08552,"mean_force":54.78178,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.48554,0.12064,0.07483]},{"body_a":"attachment","body_b":"peg","contact_count":521.0,"contact_point_centroid":[0.49248,0.12311,0.05214],"force_p95":130.61355,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":134.40856,"mean_force":104.08774,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49229,0.11753,0.06225]},{"body_a":"world","body_b":"link6","contact_count":562.0,"contact_point_centroid":[0.50587,0.2703,-2e-05],"force_p95":114.72897,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":121.92753,"mean_force":74.26352,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49238,0.08343,0.06966]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50104,0.09419,0.00863],"force_p95":99.81705,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":118.21382,"mean_force":65.61118,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49232,0.08599,0.06862]},{"body_a":"attachment","body_b":"peg","contact_count":1000.0,"contact_point_centroid":[0.49517,0.10022,0.05595],"force_p95":101.36035,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":117.70425,"mean_force":67.0705,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49232,0.08599,0.06862]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.49699,0.11975,0.00751],"force_p95":113.54003,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":114.01125,"mean_force":103.90075,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49071,0.11205,0.0626]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.49154,0.12976,0.0515],"force_p95":112.96696,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":113.44064,"mean_force":103.39836,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49071,0.11205,0.0626]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.48649,0.11975,0.00746],"force_p95":98.92148,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":98.92148,"mean_force":98.92148,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49069,0.11208,0.06253]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.49156,0.13008,0.0514],"force_p95":98.31199,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":98.31199,"mean_force":98.31199,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49069,0.11208,0.06253]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":870.0,"contact_point_centroid":[0.52547,0.08466,0.02194],"force_p95":21.4763,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":28.68824,"mean_force":12.11202,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49237,0.0837,0.06908]},{"body_a":"peg","body_b":"channel_base_body","contact_count":975.0,"contact_point_centroid":[0.49615,0.11914,0.00943],"force_p95":0.60899,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.54827,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49109,0.16247,0.20505]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49945,0.19919,0.29858]}],"total_contact_groups":13},"final_pose_error":0.16445,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50755,0.0781,0.03384],"final_tcp_position":[0.49306,0.0832,0.07094],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":245.06971,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49603,0.11905,0.03392],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19919,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.60449,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":999.0,"raw_peak_contact_force":2.24822,"subtask_id":"align_standoff","tcp_end":[0.48435,0.1274,0.11814],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08543,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50218,0.11362,0.0307],"object_pos_start":[0.49603,0.11905,0.03392],"object_to_goal_dist_end":0.19386,"object_to_goal_dist_start":0.19919,"object_z_max":0.03406,"peak_contact_force":129.23739,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1521.0,"raw_peak_contact_force":135.08552,"tcp_end":[0.49069,0.11208,0.06253],"tcp_start":[0.48435,0.1274,0.11814],"tcp_to_object_dist_end":0.03387,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50219,0.1136,0.03073],"object_pos_start":[0.50218,0.11362,0.0307],"object_to_goal_dist_end":0.19384,"object_to_goal_dist_start":0.19386,"object_z_max":0.0307,"peak_contact_force":98.92148,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":98.92148,"subtask_id":"align_standoff","tcp_end":[0.49069,0.11206,0.06256],"tcp_start":[0.49069,0.11208,0.06253],"tcp_to_object_dist_end":0.03388,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50221,0.11359,0.03076],"object_pos_start":[0.50219,0.1136,0.03073],"object_to_goal_dist_end":0.19382,"object_to_goal_dist_start":0.19384,"object_z_max":0.0308,"peak_contact_force":88.39193,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":6.0,"raw_peak_contact_force":114.01125,"subtask_id":"push_goal","tcp_end":[0.49073,0.11206,0.06266],"tcp_start":[0.49073,0.11205,0.06264],"tcp_to_object_dist_end":0.03393,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50755,0.0781,0.03384],"object_pos_start":[0.50223,0.11358,0.03082],"object_to_goal_dist_end":0.1584,"object_to_goal_dist_start":0.19381,"object_z_max":0.03384,"peak_contact_force":217.66819,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4271.0,"raw_peak_contact_force":245.06971,"tcp_end":[0.49306,0.0832,0.07094],"tcp_start":[0.49073,0.11206,0.06266],"tcp_to_object_dist_end":0.04016,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.92697,"average_solve_count":178.0,"average_success_count":178.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.01423,"approach_1.speed":0.1,"contact_1.contact_force":5.92466,"contact_1.speed":0.01249,"push_1.max_push_force":47.88839,"push_1.push_distance":0.1493,"push_1.push_speed":0.02621,"retract_1.retract_speed":0.08517},"optimized_scores":{"best_composite_score":-0.21505,"best_fitness_score":0.07495,"best_task_score":0.00718},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link7","contact_count":532.0,"contact_point_centroid":[0.47496,0.11994,0.05999],"force_p95":340.03038,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":349.64444,"mean_force":210.64514,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51215,0.07881,0.0597]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":197.0,"contact_point_centroid":[0.52507,0.07966,0.05986],"force_p95":211.43561,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":214.84958,"mean_force":192.39854,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51317,0.07874,0.05982]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":913.0,"contact_point_centroid":[0.525,0.11995,0.06],"force_p95":175.21863,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":194.36053,"mean_force":104.612,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51054,0.07905,0.0601]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":406.0,"contact_point_centroid":[0.525,0.11997,0.05962],"force_p95":88.35098,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":108.26741,"mean_force":70.40638,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50933,0.07962,0.07019]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.525,0.11998,0.06],"force_p95":54.00484,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":57.44534,"mean_force":37.01747,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50906,0.07955,0.06214]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50645,0.06021,0.00949],"force_p95":16.85157,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":44.5529,"mean_force":2.18735,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50881,0.08587,0.09424]},{"body_a":"attachment","body_b":"peg","contact_count":167.0,"contact_point_centroid":[0.50712,0.07971,0.05746],"force_p95":34.5702,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":44.32801,"mean_force":10.03316,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50933,0.07959,0.06721]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.525,0.11996,0.06],"force_p95":34.17106,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":34.23506,"mean_force":33.59507,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.5092,0.07952,0.06241]},{"body_a":"peg","body_b":"channel_base_body","contact_count":972.0,"contact_point_centroid":[0.50586,0.06296,0.00937],"force_p95":0.55508,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.56049,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50876,0.14631,0.218]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49964,0.19833,0.29732]},{"body_a":"peg","body_b":"channel_base_body","contact_count":8.0,"contact_point_centroid":[0.50878,0.04477,0.00976],"force_p95":2.39632,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.95863,"mean_force":0.92954,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50908,0.07958,0.06216]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50697,0.05382,0.00964],"force_p95":1.73999,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.72715,"mean_force":0.72211,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51076,0.07903,0.06007]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.50596,0.07958,0.05958],"force_p95":2.54348,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.71787,"mean_force":1.39745,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50917,0.07958,0.06231]},{"body_a":"attachment","body_b":"peg","contact_count":566.0,"contact_point_centroid":[0.50543,0.07884,0.05937],"force_p95":1.48175,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.28202,"mean_force":0.44306,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51042,0.07906,0.06009]},{"body_a":"peg","body_b":"channel_base_body","contact_count":2.0,"contact_point_centroid":[0.5151,0.04607,0.00973],"force_p95":0.85297,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.87585,"mean_force":0.64703,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.5092,0.07952,0.06241]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50605,0.07951,0.0596],"force_p95":0.48974,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.48974,"mean_force":0.48974,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.5092,0.07953,0.06239]}],"total_contact_groups":16},"final_pose_error":0.16209,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50623,0.06006,0.03377],"final_tcp_position":[0.51318,0.07875,0.06003],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":349.64444,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50593,0.06297,0.0338],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14323,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54709,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1006.0,"raw_peak_contact_force":3.88411,"subtask_id":"align_standoff","tcp_end":[0.51852,0.09849,0.14763],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11991,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5062,0.06158,0.03454],"object_pos_start":[0.50593,0.06297,0.0338],"object_to_goal_dist_end":0.14182,"object_to_goal_dist_start":0.14323,"object_z_max":0.03584,"peak_contact_force":90.76132,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1573.0,"raw_peak_contact_force":108.26741,"tcp_end":[0.50921,0.07952,0.06243],"tcp_start":[0.51852,0.09849,0.14763],"tcp_to_object_dist_end":0.03329,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.50619,0.06162,0.03455],"object_pos_start":[0.5062,0.06158,0.03454],"object_to_goal_dist_end":0.14186,"object_to_goal_dist_start":0.14182,"object_z_max":0.03454,"peak_contact_force":34.23506,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":5.0,"raw_peak_contact_force":34.23506,"subtask_id":"align_standoff","tcp_end":[0.50919,0.07955,0.06235],"tcp_start":[0.50921,0.07952,0.06243],"tcp_to_object_dist_end":0.03323,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":8.0,"n_steps_budget":1000.0,"object_pos_end":[0.50618,0.06153,0.03463],"object_pos_start":[0.50619,0.06162,0.03455],"object_to_goal_dist_end":0.14177,"object_to_goal_dist_start":0.14186,"object_z_max":0.03463,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":16.0,"raw_peak_contact_force":57.44534,"subtask_id":"push_goal","tcp_end":[0.50889,0.07951,0.06188],"tcp_start":[0.50891,0.07951,0.06196],"tcp_to_object_dist_end":0.03277,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50623,0.06006,0.03377],"object_pos_start":[0.50619,0.06157,0.03462],"object_to_goal_dist_end":0.14034,"object_to_goal_dist_start":0.14181,"object_z_max":0.0348,"peak_contact_force":331.65988,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3208.0,"raw_peak_contact_force":349.64444,"tcp_end":[0.51318,0.07875,0.06003],"tcp_start":[0.50889,0.07951,0.06188],"tcp_to_object_dist_end":0.03298,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```