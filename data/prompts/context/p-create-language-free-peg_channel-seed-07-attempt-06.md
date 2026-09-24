## Search State

- **Seed**: 7
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → contact → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | position_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | force_exceeded | pose_tolerance | 11 | -0.1741 | 0.30 | ❌ rejected |
| 5 | approach → contact → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | position_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 10 | -0.1290 | 0.30 | ❌ rejected |
| 4 | approach → contact → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | position_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.2917 | 0.57 | ✅ accepted |
| 3 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.1565 | 0.33 | ❌ rejected |
| 2 | approach → contact → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | position_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.0671 | 0.31 | ❌ rejected |

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

## Current Skill (Q=-0.174) — your mutation base

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

- **Composite score**: -0.174
- **task_score** (E): 0.298
- **fitness_score**: 0.266  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.640

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1787 |
| contact_1 | 1.00 | 1.00 | 0.0747 |
| align_1 | 1.00 | 1.00 | 0.0225 |
| push_1 | 0.00 | 1.00 | 0.0278 |
| retract_1 | 0.33 | 1.00 | 0.1270 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.503, 0.137, 0.135) | (0.509, 0.098, 0.040)→(0.502, 0.098, 0.034) | 0.179→0.178 | 1.00 / 1.000 | 0.556 | 2.732 |
| contact_1 | contact | 1.00 / force_exceeded | (0.503, 0.137, 0.135)→(0.498, 0.119, 0.063) | (0.502, 0.098, 0.034)→(0.502, 0.098, 0.034) | 0.178→0.178 | 1.00 / 2.000 | 19.432 | 19.432 |
| align_1 | align | 1.00 / step_budget | (0.498, 0.119, 0.063)→(0.503, 0.113, 0.044) | (0.502, 0.098, 0.034)→(0.500, 0.085, 0.034) | 0.178→0.165 | 1.00 / 2.333 | 97.081 | 149.638 |
| push_1 | push | 0.00 / guard_failure | (0.503, 0.113, 0.044)→(0.502, 0.086, 0.042) | (0.500, 0.085, 0.034)→(0.498, 0.057, 0.034) | 0.165→0.137 | 1.00 / 2.000 | 36.444 | 66.876 |
| retract_1 | retract | 0.33 / step_budget | (0.502, 0.086, 0.042)→(0.497, -0.035, 0.075) | (0.498, 0.057, 0.034)→(0.494, -0.003, 0.038) | 0.137→0.078 | 1.00 / 2.000 | 1.914 | 79.682 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.829
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.175
- phase_score: 0.543
- phase_breakdown.push_goal_score: 0.656
- phase_breakdown.align_standoff_score: 0.281

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.396
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.535
- **Median Q (composite search score)**: -0.169
- **K-run variance**: 0.0117
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.304


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.67544,"average_solve_count":228.0,"average_success_count":228.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.01383,"approach_1.speed":0.06725,"contact_1.contact_force":5.72108,"contact_1.speed":0.02125,"push_1.force_guard_threshold":21.03994,"push_1.max_force":30.6867,"push_1.push_distance":0.18488,"push_1.push_speed":0.01634,"push_1.retry_offset_x":0.00411,"push_1.retry_offset_y":0.00618,"retract_1.retract_speed":0.05363},"optimized_scores":{"best_composite_score":-0.16918,"best_fitness_score":0.27082,"best_task_score":0.53513},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":1000.0,"contact_point_centroid":[0.51391,0.1227,0.05303],"force_p95":138.88397,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":142.94845,"mean_force":107.77392,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.5058,0.12864,0.05429]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50967,0.11291,0.00854],"force_p95":139.08618,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":141.90468,"mean_force":106.69978,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.5058,0.12864,0.05429]},{"body_a":"attachment","body_b":"peg","contact_count":962.0,"contact_point_centroid":[0.50445,0.04253,0.05422],"force_p95":30.98808,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":62.35775,"mean_force":14.12236,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50026,0.05124,0.05583]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":575.0,"contact_point_centroid":[0.47496,0.01788,0.02325],"force_p95":21.42196,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":44.2206,"mean_force":7.76737,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50052,0.05427,0.05539]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":256.0,"contact_point_centroid":[0.47443,0.08698,0.02142],"force_p95":40.24891,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":40.325,"mean_force":36.64924,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50825,0.12702,0.04806]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.50587,0.11567,0.0426],"force_p95":33.35267,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":33.46812,"mean_force":31.77965,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50506,0.12663,0.04196]},{"body_a":"peg","body_b":"channel_base_body","contact_count":933.0,"contact_point_centroid":[0.49898,0.01705,0.00981],"force_p95":20.24664,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":33.15957,"mean_force":12.60467,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50024,0.04991,0.05616]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.49485,0.08191,0.00952],"force_p95":30.81855,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":30.82397,"mean_force":30.57903,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50506,0.12663,0.04196]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":3.0,"contact_point_centroid":[0.47458,0.0743,0.02574],"force_p95":20.93515,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.99245,"mean_force":20.25736,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50506,0.12663,0.04196]},{"body_a":"peg","body_b":"channel_base_body","contact_count":341.0,"contact_point_centroid":[0.50373,0.11168,0.00943],"force_p95":0.59908,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.88988,"mean_force":0.5894,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50229,0.13742,0.09227]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51126,0.128,0.05889],"force_p95":16.41884,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.41884,"mean_force":16.41884,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50074,0.13169,0.06332]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":103.0,"contact_point_centroid":[0.52513,0.11003,0.05661],"force_p95":6.77911,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.57549,"mean_force":4.3039,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50859,0.12717,0.05416]},{"body_a":"peg","body_b":"channel_base_body","contact_count":910.0,"contact_point_centroid":[0.50358,0.11163,0.00939],"force_p95":0.60941,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.55244,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50223,0.17063,0.20737]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49968,0.19943,0.2993]}],"total_contact_groups":14},"final_pose_error":0.05918,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49552,-0.02579,0.04033],"final_tcp_position":[0.49815,-0.02345,0.07266],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":142.94845,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":932.0,"n_steps_budget":1000.0,"object_pos_end":[0.50377,0.11178,0.0338],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19192,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.62119,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":926.0,"raw_peak_contact_force":2.06328,"subtask_id":"align_standoff","tcp_end":[0.50615,0.14337,0.1226],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09428,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":341.0,"n_steps_budget":1000.0,"object_pos_end":[0.50367,0.11168,0.03389],"object_pos_start":[0.50377,0.11178,0.0338],"object_to_goal_dist_end":0.19182,"object_to_goal_dist_start":0.19192,"object_z_max":0.03405,"peak_contact_force":16.88988,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":342.0,"raw_peak_contact_force":16.88988,"subtask_id":"align_standoff","tcp_end":[0.50075,0.13166,0.06316],"tcp_start":[0.50615,0.14337,0.1226],"tcp_to_object_dist_end":0.03555,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49726,0.09015,0.03865],"object_pos_start":[0.50367,0.11168,0.03389],"object_to_goal_dist_end":0.17018,"object_to_goal_dist_start":0.19182,"object_z_max":0.03872,"peak_contact_force":60.02826,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":2359.0,"raw_peak_contact_force":142.94845,"tcp_end":[0.5051,0.12664,0.04202],"tcp_start":[0.50075,0.13166,0.06316],"tcp_to_object_dist_end":0.03748,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.49724,0.0901,0.03864],"object_pos_start":[0.49726,0.09015,0.03865],"object_to_goal_dist_end":0.17013,"object_to_goal_dist_start":0.17018,"object_z_max":0.03865,"peak_contact_force":33.46812,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":9.0,"raw_peak_contact_force":33.46812,"subtask_id":"push_goal","tcp_end":[0.50498,0.12665,0.04183],"tcp_start":[0.50502,0.12663,0.04189],"tcp_to_object_dist_end":0.03749,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49552,-0.02579,0.04033],"object_pos_start":[0.49722,0.09004,0.03863],"object_to_goal_dist_end":0.05439,"object_to_goal_dist_start":0.17007,"object_z_max":0.04032,"peak_contact_force":4.72897,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2470.0,"raw_peak_contact_force":62.35775,"tcp_end":[0.49815,-0.02345,0.07266],"tcp_start":[0.50498,0.12665,0.04183],"tcp_to_object_dist_end":0.03252,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.7907,"average_solve_count":215.0,"average_success_count":215.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.02967,"approach_1.speed":0.08329,"contact_1.contact_force":6.46584,"contact_1.speed":0.0191,"push_1.force_guard_threshold":22.18322,"push_1.max_force":28.0291,"push_1.push_distance":0.15539,"push_1.push_speed":0.03545,"push_1.retry_offset_x":-0.00192,"push_1.retry_offset_y":0.00252,"retract_1.retract_speed":0.04355},"optimized_scores":{"best_composite_score":-0.30912,"best_fitness_score":0.13088,"best_task_score":0.1834},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":620.0,"contact_point_centroid":[0.50266,0.1193,0.00727],"force_p95":218.49869,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":232.69736,"mean_force":122.67,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49395,0.13724,0.05257]},{"body_a":"attachment","body_b":"peg","contact_count":620.0,"contact_point_centroid":[0.50342,0.13194,0.05062],"force_p95":220.20802,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":232.1709,"mean_force":124.02194,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49395,0.13724,0.05257]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49711,0.0878,0.00901],"force_p95":141.68062,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":166.02951,"mean_force":45.16273,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5023,0.06994,0.05987]},{"body_a":"attachment","body_b":"peg","contact_count":618.0,"contact_point_centroid":[0.51025,0.09991,0.05589],"force_p95":149.75843,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":165.42876,"mean_force":75.07703,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50499,0.10012,0.05656]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.50458,0.11902,0.00654],"force_p95":157.07757,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":157.76021,"mean_force":128.12362,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50326,0.13634,0.0468]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.51217,0.13039,0.04715],"force_p95":156.2693,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":156.94883,"mean_force":127.45739,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50326,0.13634,0.0468]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":530.0,"contact_point_centroid":[0.47428,0.09196,0.03434],"force_p95":35.66156,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":46.56796,"mean_force":19.10055,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50314,0.07667,0.05903]},{"body_a":"peg","body_b":"world","contact_count":142.0,"contact_point_centroid":[0.49771,0.12886,-1e-05],"force_p95":28.92742,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":34.09617,"mean_force":9.62878,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49941,0.13624,0.04842]},{"body_a":"peg","body_b":"channel_base_body","contact_count":448.0,"contact_point_centroid":[0.49598,0.1197,0.00944],"force_p95":0.57961,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.77126,"mean_force":0.57095,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48441,0.14442,0.09178]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.49875,0.13776,0.05849],"force_p95":13.29367,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.29367,"mean_force":13.29367,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48788,0.13909,0.06333]},{"body_a":"peg","body_b":"channel_base_body","contact_count":796.0,"contact_point_centroid":[0.4962,0.11906,0.00941],"force_p95":0.60644,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.55186,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49074,0.17436,0.20839]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49944,0.19923,0.29834]}],"total_contact_groups":12},"final_pose_error":0.07552,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49314,0.08659,0.0338],"final_tcp_position":[0.49725,-0.00707,0.07057],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":232.69736,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":821.0,"n_steps_budget":1000.0,"object_pos_end":[0.49604,0.11966,0.03404],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19979,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.50082,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":820.0,"raw_peak_contact_force":2.24822,"subtask_id":"align_standoff","tcp_end":[0.48354,0.15051,0.12396],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09588,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":448.0,"n_steps_budget":1000.0,"object_pos_end":[0.49602,0.11948,0.0339],"object_pos_start":[0.49604,0.11966,0.03404],"object_to_goal_dist_end":0.19962,"object_to_goal_dist_start":0.19979,"object_z_max":0.03407,"peak_contact_force":13.77126,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":449.0,"raw_peak_contact_force":13.77126,"subtask_id":"align_standoff","tcp_end":[0.48791,0.13908,0.06322],"tcp_start":[0.48354,0.15051,0.12396],"tcp_to_object_dist_end":0.03618,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":620.0,"n_steps_budget":720.0,"object_pos_end":[0.49927,0.11809,0.02904],"object_pos_start":[0.49602,0.11948,0.0339],"object_to_goal_dist_end":0.1984,"object_to_goal_dist_start":0.19962,"object_z_max":0.03398,"peak_contact_force":230.21206,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1382.0,"raw_peak_contact_force":232.69736,"tcp_end":[0.50323,0.13629,0.04676],"tcp_start":[0.48791,0.13908,0.06322],"tcp_to_object_dist_end":0.02571,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.49927,0.11813,0.02907],"object_pos_start":[0.49927,0.11809,0.02904],"object_to_goal_dist_end":0.19843,"object_to_goal_dist_start":0.1984,"object_z_max":0.02911,"peak_contact_force":75.67684,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":6.0,"raw_peak_contact_force":157.76021,"subtask_id":"push_goal","tcp_end":[0.50336,0.13648,0.04691],"tcp_start":[0.5033,0.13641,0.04685],"tcp_to_object_dist_end":0.02592,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49314,0.08659,0.0338],"object_pos_start":[0.49932,0.11822,0.02915],"object_to_goal_dist_end":0.16684,"object_to_goal_dist_start":0.19851,"object_z_max":0.03798,"peak_contact_force":0.54809,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2148.0,"raw_peak_contact_force":166.02951,"tcp_end":[0.49725,-0.00707,0.07057],"tcp_start":[0.50336,0.13648,0.04691],"tcp_to_object_dist_end":0.1007,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.52158,"average_solve_count":278.0,"average_success_count":278.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.00525,"approach_1.speed":0.0603,"contact_1.contact_force":8.33604,"contact_1.speed":0.02398,"push_1.force_guard_threshold":17.50536,"push_1.max_force":30.24069,"push_1.push_distance":0.15267,"push_1.push_speed":0.04989,"push_1.retry_offset_x":0.00102,"push_1.retry_offset_y":0.00107,"retract_1.retract_speed":0.07512},"optimized_scores":{"best_composite_score":-0.04412,"best_fitness_score":0.39588,"best_task_score":0.17461},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":998.0,"contact_point_centroid":[0.50433,0.03851,0.00979],"force_p95":58.35236,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":73.26681,"mean_force":8.31287,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50209,0.07981,0.04783]},{"body_a":"attachment","body_b":"peg","contact_count":891.0,"contact_point_centroid":[0.50394,0.06809,0.04669],"force_p95":59.20524,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":72.76507,"mean_force":8.8859,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.502,0.07953,0.04738]},{"body_a":"peg","body_b":"channel_base_body","contact_count":538.0,"contact_point_centroid":[0.50589,0.06305,0.00938],"force_p95":0.55271,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.63394,"mean_force":0.5969,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.51117,0.10233,0.10888]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51381,0.07932,0.05869],"force_p95":27.15983,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":27.15983,"mean_force":27.15983,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50523,0.08685,0.06229]},{"body_a":"attachment","body_b":"peg","contact_count":207.0,"contact_point_centroid":[0.495,-0.03556,0.04562],"force_p95":3.7024,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.65758,"mean_force":1.25101,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49459,-0.02361,0.04565]},{"body_a":"peg","body_b":"channel_base_body","contact_count":871.0,"contact_point_centroid":[0.49619,-0.0058,0.00992],"force_p95":2.97119,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.39899,"mean_force":1.29996,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49753,0.03397,0.03759]},{"body_a":"attachment","body_b":"peg","contact_count":735.0,"contact_point_centroid":[0.49701,0.02091,0.03844],"force_p95":2.69042,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.9843,"mean_force":1.11967,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49752,0.03281,0.03757]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":48.0,"contact_point_centroid":[0.47498,-0.05391,0.03811],"force_p95":2.7807,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.75005,"mean_force":1.3879,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49446,-0.02476,0.04627]},{"body_a":"peg","body_b":"channel_base_body","contact_count":597.0,"contact_point_centroid":[0.49364,-0.06401,0.00997],"force_p95":2.86733,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.99971,"mean_force":0.89458,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49502,-0.04376,0.05963]},{"body_a":"peg","body_b":"channel_base_body","contact_count":972.0,"contact_point_centroid":[0.50586,0.06296,0.00937],"force_p95":0.55508,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.56049,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50915,0.15661,0.22361]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4996,0.19872,0.29773]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":212.0,"contact_point_centroid":[0.47496,0.01955,0.03004],"force_p95":1.36243,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.63208,"mean_force":0.43554,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49737,0.04913,0.03738]},{"body_a":"peg","body_b":"channel_base_body","contact_count":233.0,"contact_point_centroid":[0.49354,-0.10003,0.04558],"force_p95":1.00202,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.25922,"mean_force":0.18715,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49555,-0.06336,0.07337]}],"total_contact_groups":13},"final_pose_error":0.00999,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49348,-0.06963,0.04041],"final_tcp_position":[0.49608,-0.07541,0.08203],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":73.26681,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50593,0.06297,0.0338],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14323,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54709,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1006.0,"raw_peak_contact_force":3.88411,"subtask_id":"align_standoff","tcp_end":[0.51938,0.11762,0.15748],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13588,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":538.0,"n_steps_budget":1000.0,"object_pos_end":[0.50602,0.06305,0.03382],"object_pos_start":[0.50593,0.06297,0.0338],"object_to_goal_dist_end":0.14331,"object_to_goal_dist_start":0.14323,"object_z_max":0.03382,"peak_contact_force":27.63394,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":539.0,"raw_peak_contact_force":27.63394,"subtask_id":"align_standoff","tcp_end":[0.50523,0.0868,0.06214],"tcp_start":[0.51938,0.11762,0.15748],"tcp_to_object_dist_end":0.03697,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50386,0.04679,0.03562],"object_pos_start":[0.50602,0.06305,0.03382],"object_to_goal_dist_end":0.12693,"object_to_goal_dist_start":0.14331,"object_z_max":0.04023,"peak_contact_force":1.00263,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1889.0,"raw_peak_contact_force":73.26681,"tcp_end":[0.5015,0.07642,0.04225],"tcp_start":[0.50523,0.0868,0.06214],"tcp_to_object_dist_end":0.03045,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49823,-0.03661,0.0351],"object_pos_start":[0.50386,0.04679,0.03562],"object_to_goal_dist_end":0.0437,"object_to_goal_dist_start":0.12693,"object_z_max":0.03562,"peak_contact_force":0.18731,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1818.0,"raw_peak_contact_force":9.39899,"subtask_id":"push_goal","tcp_end":[0.49733,-0.00661,0.03738],"tcp_start":[0.5015,0.07642,0.04225],"tcp_to_object_dist_end":0.03011,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":622.0,"n_steps_budget":780.0,"object_pos_end":[0.49348,-0.06963,0.04041],"object_pos_start":[0.49823,-0.03661,0.0351],"object_to_goal_dist_end":0.01226,"object_to_goal_dist_start":0.0437,"object_z_max":0.04078,"peak_contact_force":0.46606,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1085.0,"raw_peak_contact_force":10.65758,"tcp_end":[0.49608,-0.07541,0.08203],"tcp_start":[0.49733,-0.00661,0.03738],"tcp_to_object_dist_end":0.0421,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```