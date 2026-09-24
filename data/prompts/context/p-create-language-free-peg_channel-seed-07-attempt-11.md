## Search State

- **Seed**: 7
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → align → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.3926 | 0.72 | ✅ accepted |
| 10 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.2442 | 0.27 | ❌ rejected |
| 9 | approach → contact → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | position_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.2975 | 0.56 | ❌ rejected |
| 8 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.1961 | 0.12 | ❌ rejected |
| 7 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 9 | -0.0167 | 0.39 | ❌ rejected |

**Proposal policy**: task_score is 0.72 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.722, which indicates the subtask decomposition is already effective.
> Preserve the current subtask decomposition unless the evidence shows a subtask change is necessary. Prefer refining phases, parameters, control modes, or termination conditions first.
> Unnecessary subtask redesign when performance is already high often causes regression.

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

## Current Skill (Q=0.393) — your mutation base

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

- **Composite score**: 0.393
- **task_score** (E): 0.722
- **fitness_score**: 0.633  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.440

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 0.67 | 1.00 | 0.1928 |
| align_1 | 1.00 | 1.00 | 0.0830 |
| contact_1 | 1.00 | 1.00 | 0.0001 |
| push_1 | 0.67 | 1.00 | 0.1145 |
| retract_1 | 1.00 | 1.00 | 0.0897 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 0.67 / step_budget | (0.500, 0.200, 0.300)→(0.503, 0.132, 0.121) | (0.509, 0.098, 0.040)→(0.502, 0.098, 0.034) | 0.179→0.178 | 1.00 / 1.000 | 0.533 | 2.732 |
| align_1 | align | 1.00 / step_budget | (0.503, 0.132, 0.121)→(0.500, 0.123, 0.040) | (0.502, 0.098, 0.034)→(0.503, 0.094, 0.033) | 0.178→0.174 | 1.00 / 2.333 | 140.836 | 198.422 |
| contact_1 | contact | 1.00 / force_exceeded | (0.500, 0.123, 0.040)→(0.500, 0.123, 0.040) | (0.503, 0.094, 0.033)→(0.503, 0.094, 0.033) | 0.174→0.174 | 1.00 / 2.667 | 57.089 | 56.775 |
| push_1 | push | 0.67 / step_budget | (0.500, 0.123, 0.040)→(0.498, 0.009, 0.037) | (0.503, 0.094, 0.033)→(0.507, -0.020, 0.037) | 0.174→0.062 | 1.00 / 2.667 | 26.353 | 111.373 |
| retract_1 | retract | 1.00 / step_budget | (0.498, 0.009, 0.037)→(0.496, -0.069, 0.076) | (0.507, -0.020, 0.037)→(0.502, -0.059, 0.030) | 0.062→0.026 | 1.00 / 1.667 | 19.913 | 49.733 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 1.000
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 1.000
- phase_score: 0.461
- phase_breakdown.push_goal_score: 0.512
- phase_breakdown.align_standoff_score: 0.344

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.677
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.401
- **K-run variance**: 0.0016
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.372


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.67937,"average_solve_count":315.0,"average_success_count":315.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.01099,"approach_1.speed":0.02924,"contact_1.contact_force":1.37549,"contact_1.speed":0.02075,"push_1.push_distance":0.17754,"push_1.push_speed":0.03748,"retract_1.retract_speed":0.08501},"optimized_scores":{"best_composite_score":0.43689,"best_fitness_score":0.67689,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":580.0,"contact_point_centroid":[0.50559,0.11059,0.00919],"force_p95":100.60379,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":106.06102,"mean_force":21.50984,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50204,0.13714,0.07494]},{"body_a":"attachment","body_b":"peg","contact_count":191.0,"contact_point_centroid":[0.50957,0.12728,0.05367],"force_p95":102.70045,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":105.53412,"mean_force":63.75659,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50297,0.13568,0.05503]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":765.0,"contact_point_centroid":[0.54306,0.08465,0.05999],"force_p95":69.06869,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":72.93984,"mean_force":61.79163,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49864,0.08261,0.03564]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.54327,0.04068,0.05999],"force_p95":56.48388,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":56.67154,"mean_force":50.11411,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49901,0.03799,0.03567]},{"body_a":"attachment","body_b":"peg","contact_count":529.0,"contact_point_centroid":[0.50095,0.06753,0.04028],"force_p95":13.61187,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.08703,"mean_force":2.28868,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49871,0.0793,0.03567]},{"body_a":"peg","body_b":"channel_base_body","contact_count":863.0,"contact_point_centroid":[0.49999,0.04425,0.00978],"force_p95":8.48362,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.07638,"mean_force":1.76605,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49866,0.08439,0.03567]},{"body_a":"peg","body_b":"channel_base_body","contact_count":765.0,"contact_point_centroid":[0.50589,-0.04153,0.00878],"force_p95":5.67352,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.14785,"mean_force":1.62844,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49582,-0.02304,0.05929]},{"body_a":"attachment","body_b":"peg","contact_count":250.0,"contact_point_centroid":[0.50095,0.00426,0.04171],"force_p95":6.45088,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.92411,"mean_force":3.35578,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49592,0.015,0.04244]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":161.0,"contact_point_centroid":[0.52511,0.02901,0.03412],"force_p95":3.05441,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.00957,"mean_force":0.77832,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49882,0.05837,0.03566]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":110.0,"contact_point_centroid":[0.47481,0.06083,0.03341],"force_p95":0.81377,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.56952,"mean_force":0.33984,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49859,0.09032,0.03568]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":59.0,"contact_point_centroid":[0.52501,-0.00683,0.01626],"force_p95":3.39394,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.49235,"mean_force":2.38195,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49552,0.01299,0.04287]},{"body_a":"peg","body_b":"channel_base_body","contact_count":978.0,"contact_point_centroid":[0.50361,0.1117,0.00938],"force_p95":0.60828,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.55297,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50156,0.17007,0.20613]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49966,0.19945,0.29938]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.51754,0.09245,0.00957],"force_p95":0.44962,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.44962,"mean_force":0.44962,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50058,0.13252,0.03758]}],"total_contact_groups":14},"final_pose_error":0.00992,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50595,-0.0527,0.02415],"final_tcp_position":[0.49622,-0.07446,0.0827],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":106.06102,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50371,0.11177,0.0338],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19191,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.54493,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":994.0,"raw_peak_contact_force":2.06328,"subtask_id":"align_standoff","tcp_end":[0.5049,0.14228,0.12015],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09159,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":582.0,"n_steps_budget":1000.0,"object_pos_end":[0.50292,0.10251,0.0343],"object_pos_start":[0.50371,0.11177,0.0338],"object_to_goal_dist_end":0.18262,"object_to_goal_dist_start":0.19191,"object_z_max":0.03574,"peak_contact_force":0.4656,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":771.0,"raw_peak_contact_force":106.06102,"tcp_end":[0.50058,0.13252,0.03758],"tcp_start":[0.5049,0.14228,0.12015],"tcp_to_object_dist_end":0.03028,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":930.0,"object_pos_end":[0.50288,0.10254,0.03429],"object_pos_start":[0.50292,0.10251,0.0343],"object_to_goal_dist_end":0.18265,"object_to_goal_dist_start":0.18262,"object_z_max":0.0343,"peak_contact_force":1.39339,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1.0,"raw_peak_contact_force":0.44962,"subtask_id":"align_standoff","tcp_end":[0.50047,0.13247,0.03746],"tcp_start":[0.50058,0.13252,0.03758],"tcp_to_object_dist_end":0.03019,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50671,0.0088,0.03606],"object_pos_start":[0.50288,0.10254,0.03429],"object_to_goal_dist_end":0.08914,"object_to_goal_dist_start":0.18265,"object_z_max":0.03628,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2428.0,"raw_peak_contact_force":72.93984,"subtask_id":"push_goal","tcp_end":[0.49902,0.03811,0.03569],"tcp_start":[0.50047,0.13247,0.03746],"tcp_to_object_dist_end":0.03031,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":816.0,"n_steps_budget":960.0,"object_pos_end":[0.50595,-0.0527,0.02415],"object_pos_start":[0.50671,0.0088,0.03606],"object_to_goal_dist_end":0.03212,"object_to_goal_dist_start":0.08914,"object_z_max":0.0407,"peak_contact_force":0.64358,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1077.0,"raw_peak_contact_force":56.67154,"tcp_end":[0.49622,-0.07446,0.0827],"tcp_start":[0.49902,0.03811,0.03569],"tcp_to_object_dist_end":0.06321,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.7873,"average_solve_count":315.0,"average_success_count":315.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.01732,"approach_1.speed":0.0349,"contact_1.contact_force":3.66137,"contact_1.speed":0.01541,"push_1.push_distance":0.1613,"push_1.push_speed":0.03346,"retract_1.retract_speed":0.07143},"optimized_scores":{"best_composite_score":0.40115,"best_fitness_score":0.64115,"best_task_score":0.84214},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":850.0,"contact_point_centroid":[0.50281,0.08053,0.00845],"force_p95":171.55638,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":172.91201,"mean_force":80.77568,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49849,0.11283,0.04431]},{"body_a":"attachment","body_b":"peg","contact_count":865.0,"contact_point_centroid":[0.50306,0.10162,0.04454],"force_p95":171.03439,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":172.45058,"mean_force":79.38609,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49841,0.11129,0.0442]},{"body_a":"attachment","body_b":"peg","contact_count":664.0,"contact_point_centroid":[0.5017,0.13901,0.04862],"force_p95":156.87419,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":167.90746,"mean_force":104.4521,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49425,0.14655,0.05012]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49963,0.11903,0.00828],"force_p95":134.01088,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":164.39044,"mean_force":63.11515,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49091,0.14518,0.06171]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50338,0.14284,0.04313],"force_p95":93.82232,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":93.82232,"mean_force":93.82232,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.498,0.15168,0.04306]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.51428,0.11803,0.00717],"force_p95":86.59201,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":86.59201,"mean_force":86.59201,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.498,0.15168,0.04306]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":172.0,"contact_point_centroid":[0.47462,0.08254,0.03451],"force_p95":35.71451,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":43.73407,"mean_force":9.09766,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49781,0.11138,0.04235]},{"body_a":"peg","body_b":"world","contact_count":398.0,"contact_point_centroid":[0.49892,0.12639,-0.00021],"force_p95":29.33556,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":33.65048,"mean_force":19.39444,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49636,0.14853,0.04694]},{"body_a":"attachment","body_b":"peg","contact_count":232.0,"contact_point_centroid":[0.49857,0.00785,0.04006],"force_p95":9.31898,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.73796,"mean_force":5.04163,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49191,0.01712,0.043]},{"body_a":"peg","body_b":"world","contact_count":14.0,"contact_point_centroid":[0.49924,0.12298,-0.00012],"force_p95":12.93551,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.08919,"mean_force":9.9467,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49802,0.15222,0.0433]},{"body_a":"peg","body_b":"channel_base_body","contact_count":793.0,"contact_point_centroid":[0.50198,-0.03373,0.00863],"force_p95":6.99798,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.12453,"mean_force":1.93401,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49341,-0.02381,0.06037]},{"body_a":"peg","body_b":"world","contact_count":1.0,"contact_point_centroid":[0.4993,0.12296,-0.00024],"force_p95":10.50007,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.50007,"mean_force":10.50007,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.498,0.15168,0.04306]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":83.0,"contact_point_centroid":[0.52504,0.01897,0.01689],"force_p95":8.3283,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.92709,"mean_force":5.33434,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49406,0.04147,0.03846]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":126.0,"contact_point_centroid":[0.52501,0.00195,0.01963],"force_p95":4.89587,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.1447,"mean_force":3.86468,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49194,0.01833,0.04255]},{"body_a":"peg","body_b":"channel_base_body","contact_count":975.0,"contact_point_centroid":[0.49615,0.11914,0.00943],"force_p95":0.60899,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.54827,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49108,0.17148,0.20071]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49946,0.19929,0.2986]}],"total_contact_groups":16},"final_pose_error":0.00992,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49459,-0.04216,0.02415],"final_tcp_position":[0.49599,-0.07449,0.08279],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":172.91201,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49603,0.11905,0.03392],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19919,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.50789,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":999.0,"raw_peak_contact_force":2.24822,"subtask_id":"align_standoff","tcp_end":[0.4843,0.14493,0.10902],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08029,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49931,0.12252,0.03033],"object_pos_start":[0.49603,0.11905,0.03392],"object_to_goal_dist_end":0.20275,"object_to_goal_dist_start":0.19919,"object_z_max":0.03413,"peak_contact_force":130.78001,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":2062.0,"raw_peak_contact_force":167.90746,"tcp_end":[0.498,0.15168,0.04306],"tcp_start":[0.4843,0.14493,0.10902],"tcp_to_object_dist_end":0.03184,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.4993,0.12254,0.03034],"object_pos_start":[0.49931,0.12252,0.03033],"object_to_goal_dist_end":0.20277,"object_to_goal_dist_start":0.20275,"object_z_max":0.03033,"peak_contact_force":93.82232,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3.0,"raw_peak_contact_force":93.82232,"subtask_id":"align_standoff","tcp_end":[0.498,0.15173,0.04305],"tcp_start":[0.498,0.15168,0.04306],"tcp_to_object_dist_end":0.03186,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5072,0.00749,0.03892],"object_pos_start":[0.4993,0.12254,0.03034],"object_to_goal_dist_end":0.08779,"object_to_goal_dist_start":0.20277,"object_z_max":0.03891,"peak_contact_force":17.47626,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1984.0,"raw_peak_contact_force":172.91201,"subtask_id":"push_goal","tcp_end":[0.49408,0.0348,0.03858],"tcp_start":[0.498,0.15173,0.04305],"tcp_to_object_dist_end":0.0303,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":824.0,"n_steps_budget":1000.0,"object_pos_end":[0.49459,-0.04216,0.02415],"object_pos_start":[0.5072,0.00749,0.03892],"object_to_goal_dist_end":0.04138,"object_to_goal_dist_start":0.08779,"object_z_max":0.04064,"peak_contact_force":0.56826,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1151.0,"raw_peak_contact_force":14.73796,"tcp_end":[0.49599,-0.07449,0.08279],"tcp_start":[0.49408,0.0348,0.03858],"tcp_to_object_dist_end":0.06698,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.78776,"average_solve_count":245.0,"average_success_count":245.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.03,"approach_1.speed":0.09125,"contact_1.contact_force":1.81665,"contact_1.speed":0.01656,"push_1.push_distance":0.15658,"push_1.push_speed":0.04987,"retract_1.retract_speed":0.01142},"optimized_scores":{"best_composite_score":0.3397,"best_fitness_score":0.5797,"best_task_score":0.32459},"replay_outcomes":[{"contacts":{"omitted_contact_groups":4,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":92.0,"contact_point_centroid":[0.52509,0.08607,0.05996],"force_p95":303.49421,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":321.2985,"mean_force":270.64255,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50331,0.08598,0.041]},{"body_a":"channel_base_body","body_b":"link7","contact_count":69.0,"contact_point_centroid":[0.55622,-0.1,0.06499],"force_p95":87.15338,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":88.2684,"mean_force":61.58022,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50055,-0.04154,0.03741]},{"body_a":"channel_base_body","body_b":"link7","contact_count":9.0,"contact_point_centroid":[0.55582,-0.1,0.065],"force_p95":62.74778,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":77.78983,"mean_force":39.87332,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50096,-0.0462,0.03773]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":6.0,"contact_point_centroid":[0.52503,0.08606,0.05999],"force_p95":75.38064,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":77.18146,"mean_force":66.03097,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50268,0.08594,0.04053]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.52505,0.08609,0.05998],"force_p95":76.05221,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":76.05221,"mean_force":76.05221,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50276,0.08597,0.04059]},{"body_a":"peg","body_b":"channel_base_body","contact_count":588.0,"contact_point_centroid":[0.50474,0.05716,0.00948],"force_p95":12.85509,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":59.5359,"mean_force":2.94341,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50929,0.0961,0.08029]},{"body_a":"attachment","body_b":"peg","contact_count":140.0,"contact_point_centroid":[0.50659,0.07542,0.0479],"force_p95":51.15924,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":59.07249,"mean_force":10.28997,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50417,0.08713,0.04562]},{"body_a":"attachment","body_b":"peg","contact_count":992.0,"contact_point_centroid":[0.50252,-0.06618,0.06062],"force_p95":56.62184,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":58.52828,"mean_force":37.02756,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49626,-0.05537,0.05448]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":408.0,"contact_point_centroid":[0.54497,0.01718,0.06],"force_p95":51.87245,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":56.99217,"mean_force":44.07299,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4999,0.01696,0.03705]},{"body_a":"peg","body_b":"channel_base_body","contact_count":945.0,"contact_point_centroid":[0.50695,-0.10074,0.06362],"force_p95":52.38175,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":54.63233,"mean_force":37.48393,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49609,-0.05576,0.05526]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":600.0,"contact_point_centroid":[0.5253,-0.08334,0.05914],"force_p95":21.66007,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.75508,"mean_force":12.91376,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49591,-0.05691,0.05877]},{"body_a":"peg","body_b":"channel_base_body","contact_count":702.0,"contact_point_centroid":[0.50565,-0.02966,0.00992],"force_p95":12.98918,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.30807,"mean_force":5.68263,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50007,0.01613,0.03723]},{"body_a":"attachment","body_b":"peg","contact_count":789.0,"contact_point_centroid":[0.50459,0.00358,0.04306],"force_p95":12.88611,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.26113,"mean_force":4.75734,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50006,0.01535,0.03722]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":263.0,"contact_point_centroid":[0.52503,-0.00914,0.01786],"force_p95":2.96893,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.24331,"mean_force":0.84314,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49993,0.01911,0.03709]},{"body_a":"peg","body_b":"channel_base_body","contact_count":972.0,"contact_point_centroid":[0.50586,0.06296,0.00937],"force_p95":0.55508,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.56049,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50912,0.15241,0.21132]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49964,0.19856,0.29734]}],"total_contact_groups":20},"final_pose_error":0.03421,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50422,-0.08109,0.04066],"final_tcp_position":[0.4952,-0.05901,0.06341],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":321.2985,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50593,0.06297,0.0338],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14323,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54709,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1006.0,"raw_peak_contact_force":3.88411,"subtask_id":"align_standoff","tcp_end":[0.51922,0.10976,0.13422],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11157,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":596.0,"n_steps_budget":1000.0,"object_pos_end":[0.50647,0.05609,0.03509],"object_pos_start":[0.50593,0.06297,0.0338],"object_to_goal_dist_end":0.13634,"object_to_goal_dist_start":0.14323,"object_z_max":0.03675,"peak_contact_force":291.26374,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":830.0,"raw_peak_contact_force":321.2985,"tcp_end":[0.50276,0.08597,0.04059],"tcp_start":[0.51922,0.10976,0.13422],"tcp_to_object_dist_end":0.03061,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50648,0.05609,0.03508],"object_pos_start":[0.50647,0.05609,0.03509],"object_to_goal_dist_end":0.13633,"object_to_goal_dist_start":0.13634,"object_z_max":0.03509,"peak_contact_force":76.05221,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3.0,"raw_peak_contact_force":76.05221,"subtask_id":"align_standoff","tcp_end":[0.50275,0.08597,0.04058],"tcp_start":[0.50276,0.08597,0.04059],"tcp_to_object_dist_end":0.03061,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50693,-0.07547,0.03589],"object_pos_start":[0.50648,0.05609,0.03508],"object_to_goal_dist_end":0.00924,"object_to_goal_dist_start":0.13633,"object_z_max":0.0364,"peak_contact_force":61.58253,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2237.0,"raw_peak_contact_force":88.2684,"subtask_id":"push_goal","tcp_end":[0.50093,-0.0461,0.03773],"tcp_start":[0.50275,0.08597,0.04058],"tcp_to_object_dist_end":0.03004,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50422,-0.08109,0.04066],"object_pos_start":[0.50693,-0.07547,0.03589],"object_to_goal_dist_end":0.00441,"object_to_goal_dist_start":0.00924,"object_z_max":0.04142,"peak_contact_force":58.52828,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2619.0,"raw_peak_contact_force":77.78983,"tcp_end":[0.4952,-0.05901,0.06341],"tcp_start":[0.50093,-0.0461,0.03773],"tcp_to_object_dist_end":0.03297,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```