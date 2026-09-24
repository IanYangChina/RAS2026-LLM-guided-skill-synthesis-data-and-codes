## Search State

- **Seed**: 7
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → contact → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | position_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 10 | -0.1290 | 0.30 | ❌ rejected |
| 4 | approach → contact → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | position_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.2917 | 0.57 | ✅ accepted |
| 3 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.1565 | 0.33 | ❌ rejected |
| 2 | approach → contact → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | position_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.0671 | 0.31 | ❌ rejected |
| 1 | approach → contact → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | position_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.1237 | 0.42 | ✅ accepted |

**Proposal policy**: task_score is 0.30 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.129) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: align_standoff
  anchor: object
  offset:
  - 0.0
  - 0.025
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
    - 0.025
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
    - 0.025
    - 0.005
  parameters:
    contact_force:
      type: scalar
      range:
      - 1.0
      - 10.0
      default: 3.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    speed:
      type: scalar
      range:
      - 0.005
      - 0.03
      default: 0.015
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
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - -0.02
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
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.025, 0.05], tolerance=0.005
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **contact_1** (`contact`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.025, 0.005]
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **align_1** (`align`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, -0.02], tolerance=0.005
  - parameter_bindings:
    - align_speed: status=consumed; consumers=generator.speed (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.16, mode=add_to_offset, sign=positive}, tolerance=0.01
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=1, strategy=reduce_speed
- **retract_1** (`retract`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.05], tolerance=0.01
  - parameter_bindings:
    - retract_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: -0.129
- **task_score** (E): 0.301
- **fitness_score**: 0.261  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.590

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 0.67 | 1.00 | 0.1917 |
| contact_1 | 1.00 | 1.00 | 0.0667 |
| align_1 | 1.00 | 1.00 | 0.0051 |
| push_1 | 0.00 | 1.00 | 0.0003 |
| retract_1 | 0.67 | 1.00 | 0.1502 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 0.67 / step_budget | (0.500, 0.200, 0.300)→(0.502, 0.138, 0.120) | (0.509, 0.098, 0.040)→(0.502, 0.098, 0.034) | 0.179→0.178 | 1.00 / 1.000 | 0.550 | 2.732 |
| contact_1 | contact | 1.00 / force_exceeded | (0.502, 0.138, 0.120)→(0.496, 0.124, 0.056) | (0.502, 0.098, 0.034)→(0.502, 0.097, 0.034) | 0.178→0.177 | 1.00 / 2.000 | 14.051 | 11.267 |
| align_1 | align | 1.00 / step_budget | (0.496, 0.124, 0.056)→(0.492, 0.128, 0.055) | (0.502, 0.097, 0.034)→(0.501, 0.097, 0.034) | 0.177→0.177 | 1.00 / 1.000 | 0.551 | 17.615 |
| push_1 | push | 0.00 / guard_failure | (0.490, 0.101, 0.052)→(0.490, 0.101, 0.052) | (0.501, 0.097, 0.034)→(0.502, 0.077, 0.036) | 0.177→0.157 | 1.00 / 2.333 | 18.832 | 40.366 |
| retract_1 | retract | 0.67 / step_budget | (0.490, 0.101, 0.052)→(0.494, -0.046, 0.080) | (0.502, 0.077, 0.036)→(0.501, 0.022, 0.024) | 0.157→0.103 | 1.00 / 1.000 | 0.681 | 38.005 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.531
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.423
- phase_score: 0.175
- phase_breakdown.push_goal_score: 0.002
- phase_breakdown.align_standoff_score: 0.580

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.274
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.423
- **Median Q (composite search score)**: -0.120
- **K-run variance**: 0.0003
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.280


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.55975,"average_solve_count":318.0,"average_success_count":318.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.02181,"approach_1.speed":0.0478,"contact_1.contact_force":4.9112,"contact_1.speed":0.01477,"push_1.pose_tolerance":0.02997,"push_1.push_distance":0.17149,"push_1.push_speed":0.01846,"push_1.retry_offset_x":-0.00171,"push_1.retry_offset_y":0.00043,"retract_1.retract_speed":0.03865},"optimized_scores":{"best_composite_score":-0.12013,"best_fitness_score":0.26987,"best_task_score":0.29533},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":76.0,"contact_point_centroid":[0.50525,0.09728,0.00963],"force_p95":29.09389,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":43.45965,"mean_force":9.79027,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49475,0.12661,0.05824]},{"body_a":"attachment","body_b":"peg","contact_count":29.0,"contact_point_centroid":[0.49983,0.10588,0.05538],"force_p95":38.43883,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":42.83522,"mean_force":25.08449,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49429,0.11578,0.05743]},{"body_a":"attachment","body_b":"peg","contact_count":56.0,"contact_point_centroid":[0.50088,0.09065,0.05295],"force_p95":19.17476,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":36.16,"mean_force":9.08063,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49318,0.09893,0.05628]},{"body_a":"peg","body_b":"channel_base_body","contact_count":996.0,"contact_point_centroid":[0.50494,0.06752,0.00824],"force_p95":2.71969,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":32.70833,"mean_force":1.15306,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49304,0.02567,0.06646]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":8.0,"contact_point_centroid":[0.52507,0.08223,0.05901],"force_p95":19.8669,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":25.1967,"mean_force":4.66445,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49419,0.11759,0.05734]},{"body_a":"peg","body_b":"channel_base_body","contact_count":210.0,"contact_point_centroid":[0.49765,0.11337,0.00951],"force_p95":21.4483,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.58312,"mean_force":6.09168,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49771,0.14087,0.06053]},{"body_a":"attachment","body_b":"peg","contact_count":89.0,"contact_point_centroid":[0.50423,0.12972,0.05883],"force_p95":21.57295,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.03204,"mean_force":13.16456,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49885,0.14,0.06077]},{"body_a":"peg","body_b":"channel_base_body","contact_count":322.0,"contact_point_centroid":[0.50359,0.11164,0.00941],"force_p95":0.60415,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.95922,"mean_force":0.59791,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50152,0.14194,0.08862]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50701,0.12933,0.05885],"force_p95":17.51502,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.51502,"mean_force":17.51502,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50031,0.13887,0.06159]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":26.0,"contact_point_centroid":[0.52504,0.04957,0.03379],"force_p95":8.39706,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.71405,"mean_force":3.53535,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49405,0.02456,0.06785]},{"body_a":"peg","body_b":"channel_base_body","contact_count":978.0,"contact_point_centroid":[0.50363,0.11166,0.00939],"force_p95":0.60846,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.55189,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50163,0.17166,0.20442]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49967,0.19945,0.29932]}],"total_contact_groups":12},"final_pose_error":0.03587,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50528,0.06452,0.0243],"final_tcp_position":[0.49515,-0.04617,0.0791],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":43.45965,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50372,0.11181,0.03388],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19194,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.50812,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":994.0,"raw_peak_contact_force":2.06328,"subtask_id":"align_standoff","tcp_end":[0.50504,0.14544,0.11685],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08954,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":322.0,"n_steps_budget":1000.0,"object_pos_end":[0.50375,0.11167,0.03385],"object_pos_start":[0.50372,0.11181,0.03388],"object_to_goal_dist_end":0.1918,"object_to_goal_dist_start":0.19194,"object_z_max":0.03391,"peak_contact_force":17.95922,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":323.0,"raw_peak_contact_force":17.95922,"subtask_id":"align_standoff","tcp_end":[0.50031,0.13886,0.06143],"tcp_start":[0.50504,0.14544,0.11685],"tcp_to_object_dist_end":0.03889,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":210.0,"n_steps_budget":600.0,"object_pos_end":[0.50199,0.11051,0.03384],"object_pos_start":[0.50375,0.11167,0.03385],"object_to_goal_dist_end":0.19062,"object_to_goal_dist_start":0.1918,"object_z_max":0.03484,"peak_contact_force":0.54844,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":299.0,"raw_peak_contact_force":23.58312,"tcp_end":[0.49649,0.14201,0.06055],"tcp_start":[0.50031,0.13886,0.06143],"tcp_to_object_dist_end":0.04166,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":79.0,"n_steps_budget":1000.0,"object_pos_end":[0.50495,0.0863,0.03974],"object_pos_start":[0.50199,0.11051,0.03384],"object_to_goal_dist_end":0.16637,"object_to_goal_dist_start":0.19062,"object_z_max":0.04055,"peak_contact_force":37.14999,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":113.0,"raw_peak_contact_force":43.45965,"subtask_id":"push_goal","tcp_end":[0.49426,0.10417,0.05707],"tcp_start":[0.49426,0.10447,0.05709],"tcp_to_object_dist_end":0.02708,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50528,0.06452,0.0243],"object_pos_start":[0.50512,0.08572,0.03962],"object_to_goal_dist_end":0.14547,"object_to_goal_dist_start":0.1658,"object_z_max":0.03962,"peak_contact_force":0.74832,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1078.0,"raw_peak_contact_force":36.16,"tcp_end":[0.49515,-0.04617,0.0791],"tcp_start":[0.49426,0.10417,0.05707],"tcp_to_object_dist_end":0.12393,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.0163,"average_solve_count":184.0,"average_success_count":184.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.01334,"approach_1.speed":0.07678,"contact_1.contact_force":4.58911,"contact_1.speed":0.0186,"push_1.pose_tolerance":0.03556,"push_1.push_distance":0.17255,"push_1.push_speed":0.02633,"push_1.retry_offset_x":-0.00306,"push_1.retry_offset_y":0.00384,"retract_1.retract_speed":0.06416},"optimized_scores":{"best_composite_score":-0.11555,"best_fitness_score":0.27445,"best_task_score":0.42331},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":991.0,"contact_point_centroid":[0.49605,0.06496,0.00927],"force_p95":40.76095,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":51.18957,"mean_force":15.04745,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48504,0.062,0.06829]},{"body_a":"attachment","body_b":"peg","contact_count":580.0,"contact_point_centroid":[0.49252,0.09828,0.06034],"force_p95":41.98082,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":50.61602,"mean_force":24.85604,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48272,0.09691,0.06469]},{"body_a":"peg","body_b":"channel_base_body","contact_count":16.0,"contact_point_centroid":[0.49109,0.11996,0.00965],"force_p95":30.13631,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":33.86555,"mean_force":9.53452,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48133,0.14634,0.0617]},{"body_a":"attachment","body_b":"peg","contact_count":7.0,"contact_point_centroid":[0.49022,0.13935,0.05733],"force_p95":31.96897,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":33.46236,"mean_force":20.64651,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48101,0.14574,0.06137]},{"body_a":"peg","body_b":"channel_base_body","contact_count":201.0,"contact_point_centroid":[0.48026,0.1199,0.00981],"force_p95":19.46867,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":25.54631,"mean_force":6.26668,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.48294,0.14586,0.06208]},{"body_a":"attachment","body_b":"peg","contact_count":189.0,"contact_point_centroid":[0.49181,0.13873,0.05831],"force_p95":19.09499,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":25.01786,"mean_force":6.19013,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.48301,0.14579,0.06208]},{"body_a":"peg","body_b":"channel_base_body","contact_count":269.0,"contact_point_centroid":[0.49618,0.11918,0.00942],"force_p95":0.59857,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.65389,"mean_force":0.57223,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48332,0.14417,0.07602]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.49438,0.13688,0.05883],"force_p95":8.12999,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.12999,"mean_force":8.12999,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48541,0.14376,0.06279]},{"body_a":"peg","body_b":"channel_base_body","contact_count":949.0,"contact_point_centroid":[0.49612,0.11922,0.00945],"force_p95":0.60115,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.54729,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49052,0.1716,0.1927]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49946,0.19926,0.29839]}],"total_contact_groups":10},"final_pose_error":0.06173,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49571,0.03395,0.02425],"final_tcp_position":[0.49111,-0.0202,0.07753],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":51.18957,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":974.0,"n_steps_budget":1000.0,"object_pos_end":[0.49607,0.11937,0.03385],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.1995,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.59469,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":973.0,"raw_peak_contact_force":2.24822,"subtask_id":"align_standoff","tcp_end":[0.48318,0.14528,0.09379],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.06656,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":269.0,"n_steps_budget":1000.0,"object_pos_end":[0.49599,0.11897,0.03383],"object_pos_start":[0.49607,0.11937,0.03385],"object_to_goal_dist_end":0.1991,"object_to_goal_dist_start":0.1995,"object_z_max":0.03407,"peak_contact_force":8.65389,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":270.0,"raw_peak_contact_force":8.65389,"subtask_id":"align_standoff","tcp_end":[0.48542,0.14377,0.06274],"tcp_start":[0.48318,0.14528,0.09379],"tcp_to_object_dist_end":0.03952,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":201.0,"n_steps_budget":600.0,"object_pos_end":[0.4941,0.11963,0.03476],"object_pos_start":[0.49599,0.11897,0.03383],"object_to_goal_dist_end":0.19979,"object_to_goal_dist_start":0.1991,"object_z_max":0.03507,"peak_contact_force":0.55361,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":390.0,"raw_peak_contact_force":25.54631,"tcp_end":[0.48176,0.14694,0.06216],"tcp_start":[0.48542,0.14377,0.06274],"tcp_to_object_dist_end":0.04061,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":16.0,"n_steps_budget":1000.0,"object_pos_end":[0.49406,0.11924,0.03427],"object_pos_start":[0.4941,0.11963,0.03476],"object_to_goal_dist_end":0.19941,"object_to_goal_dist_start":0.19979,"object_z_max":0.03476,"peak_contact_force":17.10791,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":23.0,"raw_peak_contact_force":33.86555,"subtask_id":"push_goal","tcp_end":[0.48083,0.14496,0.06112],"tcp_start":[0.48085,0.1451,0.06118],"tcp_to_object_dist_end":0.03947,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49571,0.03395,0.02425],"object_pos_start":[0.49415,0.11914,0.03416],"object_to_goal_dist_end":0.11511,"object_to_goal_dist_start":0.19931,"object_z_max":0.04078,"peak_contact_force":0.62616,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1571.0,"raw_peak_contact_force":51.18957,"tcp_end":[0.49111,-0.0202,0.07753],"tcp_start":[0.48083,0.14496,0.06112],"tcp_to_object_dist_end":0.07611,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.49844,"average_solve_count":321.0,"average_success_count":321.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.01487,"approach_1.speed":0.03137,"contact_1.contact_force":6.81771,"contact_1.speed":0.0138,"push_1.pose_tolerance":0.03635,"push_1.push_distance":0.15929,"push_1.push_speed":0.0384,"push_1.retry_offset_x":-0.00108,"push_1.retry_offset_y":-0.00159,"retract_1.retract_speed":0.0528},"optimized_scores":{"best_composite_score":-0.15138,"best_fitness_score":0.23862,"best_task_score":0.18398},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":50.0,"contact_point_centroid":[0.50528,0.03946,0.00912],"force_p95":28.1611,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":43.773,"mean_force":5.42695,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49708,0.07791,0.04033]},{"body_a":"attachment","body_b":"peg","contact_count":21.0,"contact_point_centroid":[0.50271,0.06552,0.04611],"force_p95":40.36762,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":42.89449,"mean_force":11.79937,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49675,0.07679,0.03995]},{"body_a":"attachment","body_b":"peg","contact_count":319.0,"contact_point_centroid":[0.49963,0.01972,0.04147],"force_p95":16.39674,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":26.6666,"mean_force":5.68032,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4932,0.02937,0.04348]},{"body_a":"peg","body_b":"channel_base_body","contact_count":961.0,"contact_point_centroid":[0.50499,-0.02312,0.00868],"force_p95":6.67492,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":25.86256,"mean_force":2.34836,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49417,-0.01415,0.05977]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52543,0.04017,0.05006],"force_p95":12.65803,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.71084,"mean_force":1.97247,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49639,0.06981,0.03935]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":167.0,"contact_point_centroid":[0.52501,0.01002,0.02166],"force_p95":5.6866,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.5929,"mean_force":3.49254,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49323,0.02905,0.04362]},{"body_a":"peg","body_b":"channel_base_body","contact_count":636.0,"contact_point_centroid":[0.50599,0.06157,0.00941],"force_p95":0.55326,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.18666,"mean_force":0.62551,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50868,0.10621,0.09577]},{"body_a":"attachment","body_b":"peg","contact_count":15.0,"contact_point_centroid":[0.5049,0.07968,0.04957],"force_p95":6.17778,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.91544,"mean_force":3.95351,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50329,0.09162,0.04788]},{"body_a":"peg","body_b":"channel_base_body","contact_count":972.0,"contact_point_centroid":[0.50586,0.06296,0.00937],"force_p95":0.55508,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.56049,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50791,0.15919,0.22036]},{"body_a":"peg","body_b":"channel_base_body","contact_count":281.0,"contact_point_centroid":[0.50464,0.05891,0.00952],"force_p95":0.67,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.71449,"mean_force":0.61137,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49934,0.09219,0.04164]},{"body_a":"attachment","body_b":"peg","contact_count":40.0,"contact_point_centroid":[0.50464,0.07865,0.04822],"force_p95":2.67062,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.29092,"mean_force":0.69988,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50108,0.09058,0.04189]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49957,0.19881,0.29775]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":9.0,"contact_point_centroid":[0.52518,0.06112,0.05948],"force_p95":0.82606,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.85498,"mean_force":0.29989,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50325,0.0915,0.0475]}],"total_contact_groups":13},"final_pose_error":0.01175,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50097,-0.03309,0.02414],"final_tcp_position":[0.49598,-0.07222,0.08217],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":43.773,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50593,0.06297,0.0338],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14323,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54709,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1006.0,"raw_peak_contact_force":3.88411,"subtask_id":"align_standoff","tcp_end":[0.51706,0.12223,0.15059],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13143,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":637.0,"n_steps_budget":1000.0,"object_pos_end":[0.506,0.0608,0.03562],"object_pos_start":[0.50593,0.06297,0.0338],"object_to_goal_dist_end":0.141,"object_to_goal_dist_start":0.14323,"object_z_max":0.03572,"peak_contact_force":15.54049,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":660.0,"raw_peak_contact_force":7.18666,"subtask_id":"align_standoff","tcp_end":[0.5028,0.09025,0.04327],"tcp_start":[0.51706,0.12223,0.15059],"tcp_to_object_dist_end":0.03059,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":281.0,"n_steps_budget":600.0,"object_pos_end":[0.50588,0.06123,0.03378],"object_pos_start":[0.506,0.0608,0.03562],"object_to_goal_dist_end":0.14148,"object_to_goal_dist_start":0.141,"object_z_max":0.03562,"peak_contact_force":0.54975,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":321.0,"raw_peak_contact_force":3.71449,"tcp_end":[0.49868,0.09368,0.04242],"tcp_start":[0.5028,0.09025,0.04327],"tcp_to_object_dist_end":0.03435,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":81.0,"n_steps_budget":1000.0,"object_pos_end":[0.50683,0.02614,0.03424],"object_pos_start":[0.50588,0.06123,0.03378],"object_to_goal_dist_end":0.10651,"object_to_goal_dist_start":0.14148,"object_z_max":0.04117,"peak_contact_force":2.23721,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":103.0,"raw_peak_contact_force":43.773,"subtask_id":"push_goal","tcp_end":[0.49582,0.05252,0.03833],"tcp_start":[0.49584,0.05282,0.03838],"tcp_to_object_dist_end":0.02888,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50097,-0.03309,0.02414],"object_pos_start":[0.50675,0.02587,0.03456],"object_to_goal_dist_end":0.04953,"object_to_goal_dist_start":0.10622,"object_z_max":0.04059,"peak_contact_force":0.6672,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1447.0,"raw_peak_contact_force":26.6666,"tcp_end":[0.49598,-0.07222,0.08217],"tcp_start":[0.49582,0.05252,0.03833],"tcp_to_object_dist_end":0.07017,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```