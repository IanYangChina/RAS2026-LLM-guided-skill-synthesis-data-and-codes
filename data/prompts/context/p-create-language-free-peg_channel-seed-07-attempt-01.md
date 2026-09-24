## Search State

- **Seed**: 7
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | approach → contact → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | position_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.1237 | 0.42 | ✅ accepted |
| 0 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.2119 | 0.23 | ✅ accepted |

**Proposal policy**: task_score is 0.42 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.124) — your mutation base

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
      default: 0.05
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
      default: 0.01
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
      - 0.12
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
  guards:
  - id: force_limit
    when: during_phase
    predicate: force_below
    threshold: 40.0
    on_failure: continue
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
  - guards:
    - id=force_limit, when=during_phase, predicate=force_below, on_failure=continue, threshold=40.0
  - retries: max_attempts=1, strategy=reduce_speed
- **retract_1** (`retract`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.05], tolerance=0.01
  - parameter_bindings:
    - retract_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.124
- **task_score** (E): 0.423
- **fitness_score**: 0.364  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.440

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1997 |
| contact_1 | 1.00 | 1.00 | 0.0548 |
| align_1 | 1.00 | 1.00 | 0.0168 |
| push_1 | 0.00 | 1.00 | 0.0454 |
| retract_1 | 0.67 | 1.00 | 0.1367 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.503, 0.134, 0.113) | (0.509, 0.098, 0.040)→(0.502, 0.098, 0.034) | 0.179→0.178 | 1.00 / 1.000 | 0.530 | 2.732 |
| contact_1 | contact | 1.00 / force_exceeded | (0.503, 0.134, 0.113)→(0.497, 0.125, 0.060) | (0.502, 0.098, 0.034)→(0.502, 0.102, 0.033) | 0.178→0.183 | 1.00 / 2.333 | 20.808 | 6.785 |
| align_1 | align | 1.00 / step_budget | (0.497, 0.125, 0.060)→(0.495, 0.127, 0.044) | (0.502, 0.102, 0.033)→(0.502, 0.099, 0.033) | 0.183→0.179 | 1.00 / 1.667 | 37.638 | 67.484 |
| push_1 | push | 0.00 / guard_failure | (0.495, 0.127, 0.044)→(0.493, 0.082, 0.042) | (0.502, 0.099, 0.033)→(0.504, 0.054, 0.035) | 0.179→0.135 | 1.00 / 3.000 | 56.227 | 56.227 |
| retract_1 | retract | 0.67 / step_budget | (0.493, 0.082, 0.042)→(0.495, -0.048, 0.078) | (0.504, 0.054, 0.035)→(0.499, -0.008, 0.024) | 0.135→0.074 | 1.00 / 1.000 | 0.582 | 93.631 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 1.000
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.659
- phase_score: 0.630
- phase_breakdown.push_goal_score: 0.666
- phase_breakdown.align_standoff_score: 0.547

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.642
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.659
- **Median Q (composite search score)**: 0.025
- **K-run variance**: 0.0397
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.259


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.72364,"average_solve_count":275.0,"average_success_count":275.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.01947,"approach_1.speed":0.0483,"contact_1.contact_force":4.67872,"contact_1.speed":0.02139,"push_1.push_distance":0.17908,"push_1.push_speed":0.03793,"retract_1.retract_speed":0.05264},"optimized_scores":{"best_composite_score":0.40158,"best_fitness_score":0.64158,"best_task_score":0.65853},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":107.0,"contact_point_centroid":[0.50301,0.10365,0.00932],"force_p95":62.40851,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":69.47481,"mean_force":19.86909,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49901,0.13884,0.05441]},{"body_a":"attachment","body_b":"peg","contact_count":54.0,"contact_point_centroid":[0.50496,0.12877,0.05723],"force_p95":63.77669,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":68.8508,"mean_force":38.4806,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49965,0.13894,0.05748]},{"body_a":"attachment","body_b":"peg","contact_count":725.0,"contact_point_centroid":[0.49941,0.05588,0.03982],"force_p95":35.20702,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.35427,"mean_force":14.15303,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49342,0.06591,0.04093]},{"body_a":"peg","body_b":"channel_base_body","contact_count":626.0,"contact_point_centroid":[0.50654,0.02852,0.00985],"force_p95":25.9793,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":31.15377,"mean_force":13.27646,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4935,0.0647,0.04106]},{"body_a":"attachment","body_b":"peg","contact_count":201.0,"contact_point_centroid":[0.49963,-0.00636,0.04072],"force_p95":27.23893,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.85264,"mean_force":14.38861,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49126,0.00055,0.04473]},{"body_a":"peg","body_b":"channel_base_body","contact_count":802.0,"contact_point_centroid":[0.503,-0.04091,0.00854],"force_p95":20.86504,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":26.31107,"mean_force":3.76428,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49288,-0.03253,0.06069]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":527.0,"contact_point_centroid":[0.52519,0.03169,0.02571],"force_p95":22.0721,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":24.21333,"mean_force":9.4173,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49328,0.05365,0.04083]},{"body_a":"peg","body_b":"channel_base_body","contact_count":316.0,"contact_point_centroid":[0.50366,0.11168,0.0094],"force_p95":0.59638,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.19704,"mean_force":0.60365,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50153,0.14185,0.08843]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50722,0.1294,0.05877],"force_p95":18.74279,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.74279,"mean_force":18.74279,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50032,0.13878,0.06161]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":183.0,"contact_point_centroid":[0.52505,-0.01703,0.02745],"force_p95":12.49452,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.58638,"mean_force":7.50111,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49129,0.00137,0.04442]},{"body_a":"peg","body_b":"channel_base_body","contact_count":978.0,"contact_point_centroid":[0.50362,0.11164,0.00939],"force_p95":0.60822,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.55168,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50164,0.17161,0.20425]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49967,0.19944,0.29931]}],"total_contact_groups":12},"final_pose_error":0.00993,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49665,-0.04826,0.02413],"final_tcp_position":[0.49587,-0.07489,0.08256],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":69.47481,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50374,0.11169,0.0338],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19183,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.55045,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":994.0,"raw_peak_contact_force":2.06328,"subtask_id":"align_standoff","tcp_end":[0.50504,0.14534,0.11654],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08932,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":316.0,"n_steps_budget":1000.0,"object_pos_end":[0.50366,0.11176,0.03381],"object_pos_start":[0.50374,0.11169,0.0338],"object_to_goal_dist_end":0.19189,"object_to_goal_dist_start":0.19183,"object_z_max":0.03391,"peak_contact_force":19.19704,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":317.0,"raw_peak_contact_force":19.19704,"subtask_id":"align_standoff","tcp_end":[0.50033,0.13877,0.06146],"tcp_start":[0.50504,0.14534,0.11654],"tcp_to_object_dist_end":0.0388,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":107.0,"n_steps_budget":660.0,"object_pos_end":[0.50322,0.10773,0.03645],"object_pos_start":[0.50366,0.11176,0.03381],"object_to_goal_dist_end":0.18779,"object_to_goal_dist_start":0.19189,"object_z_max":0.03647,"peak_contact_force":0.4264,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":161.0,"raw_peak_contact_force":69.47481,"tcp_end":[0.49726,0.13827,0.04532],"tcp_start":[0.50033,0.13877,0.06146],"tcp_to_object_dist_end":0.03235,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":823.0,"n_steps_budget":1000.0,"object_pos_end":[0.50779,-0.01779,0.04013],"object_pos_start":[0.50322,0.10773,0.03645],"object_to_goal_dist_end":0.0627,"object_to_goal_dist_start":0.18779,"object_z_max":0.0403,"peak_contact_force":40.35427,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1878.0,"raw_peak_contact_force":40.35427,"subtask_id":"push_goal","tcp_end":[0.49318,0.01237,0.04118],"tcp_start":[0.49726,0.13827,0.04532],"tcp_to_object_dist_end":0.03353,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":804.0,"n_steps_budget":1000.0,"object_pos_end":[0.49665,-0.04826,0.02413],"object_pos_start":[0.50779,-0.01779,0.04013],"object_to_goal_dist_end":0.03564,"object_to_goal_dist_start":0.0627,"object_z_max":0.04015,"peak_contact_force":0.53262,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1186.0,"raw_peak_contact_force":28.85264,"tcp_end":[0.49587,-0.07489,0.08256],"tcp_start":[0.49318,0.01237,0.04118],"tcp_to_object_dist_end":0.06421,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.15244,"average_solve_count":164.0,"average_success_count":164.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.01475,"approach_1.speed":0.08261,"contact_1.contact_force":5.90886,"contact_1.speed":0.02352,"push_1.push_distance":0.15991,"push_1.push_speed":0.03928,"retract_1.retract_speed":0.06704},"optimized_scores":{"best_composite_score":0.02477,"best_fitness_score":0.26477,"best_task_score":0.40387},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":992.0,"contact_point_centroid":[0.49773,0.08404,0.00851],"force_p95":115.48477,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":131.07139,"mean_force":51.33819,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49064,0.07868,0.06013]},{"body_a":"attachment","body_b":"peg","contact_count":688.0,"contact_point_centroid":[0.50022,0.10463,0.05402],"force_p95":118.52096,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":130.27815,"mean_force":74.65451,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49055,0.10498,0.05708]},{"body_a":"attachment","body_b":"peg","contact_count":419.0,"contact_point_centroid":[0.49333,0.13948,0.05065],"force_p95":115.46462,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":125.9208,"mean_force":94.59004,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.4865,0.14803,0.0521]},{"body_a":"peg","body_b":"channel_base_body","contact_count":419.0,"contact_point_centroid":[0.49292,0.1192,0.00846],"force_p95":81.68075,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":104.22836,"mean_force":59.35628,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.4865,0.14803,0.0521]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.49379,0.14301,0.04617],"force_p95":79.10637,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":79.10637,"mean_force":79.10637,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48719,0.1515,0.04713]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.47904,0.11878,0.00784],"force_p95":65.22802,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":65.22802,"mean_force":65.22802,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48719,0.1515,0.04713]},{"body_a":"peg","body_b":"world","contact_count":419.0,"contact_point_centroid":[0.49617,0.13383,-0.00071],"force_p95":48.17518,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":51.8845,"mean_force":38.13708,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.4865,0.14803,0.0521]},{"body_a":"peg","body_b":"world","contact_count":73.0,"contact_point_centroid":[0.4963,0.12984,-0.00028],"force_p95":29.77258,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":32.58037,"mean_force":15.01635,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48765,0.14929,0.04898]},{"body_a":"peg","body_b":"world","contact_count":1.0,"contact_point_centroid":[0.49632,0.13018,-0.00072],"force_p95":16.97516,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.97516,"mean_force":16.97516,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48719,0.1515,0.04713]},{"body_a":"peg","body_b":"channel_base_body","contact_count":941.0,"contact_point_centroid":[0.49611,0.11914,0.00941],"force_p95":0.61078,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.55055,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49051,0.17157,0.1926]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49946,0.19925,0.29833]},{"body_a":"peg","body_b":"channel_base_body","contact_count":257.0,"contact_point_centroid":[0.49625,0.11968,0.00943],"force_p95":0.59387,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60237,"mean_force":0.53446,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48342,0.14424,0.07563]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":6.0,"contact_point_centroid":[0.47499,0.05022,0.05982],"force_p95":0.10469,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.10955,"mean_force":0.07137,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49051,0.02303,0.06617]}],"total_contact_groups":13},"final_pose_error":0.07737,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.4949,0.04108,0.02428],"final_tcp_position":[0.49202,-0.00533,0.07136],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":131.07139,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":966.0,"n_steps_budget":1000.0,"object_pos_end":[0.49606,0.1197,0.03387],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19984,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.49207,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":965.0,"raw_peak_contact_force":2.24822,"subtask_id":"align_standoff","tcp_end":[0.48316,0.14525,0.09368],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.06631,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":257.0,"n_steps_budget":1000.0,"object_pos_end":[0.49603,0.13266,0.03065],"object_pos_start":[0.49606,0.1197,0.03387],"object_to_goal_dist_end":0.2129,"object_to_goal_dist_start":0.19984,"object_z_max":0.03389,"peak_contact_force":41.81674,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":257.0,"raw_peak_contact_force":0.60237,"subtask_id":"align_standoff","tcp_end":[0.48553,0.1439,0.0622],"tcp_start":[0.48316,0.14525,0.09368],"tcp_to_object_dist_end":0.03511,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":419.0,"n_steps_budget":870.0,"object_pos_end":[0.49633,0.1268,0.02918],"object_pos_start":[0.49603,0.13266,0.03065],"object_to_goal_dist_end":0.20711,"object_to_goal_dist_start":0.2129,"object_z_max":0.03065,"peak_contact_force":111.85705,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1257.0,"raw_peak_contact_force":125.9208,"tcp_end":[0.48719,0.1515,0.04713],"tcp_start":[0.48553,0.1439,0.0622],"tcp_to_object_dist_end":0.03188,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.49635,0.12681,0.0292],"object_pos_start":[0.49633,0.1268,0.02918],"object_to_goal_dist_end":0.20712,"object_to_goal_dist_start":0.20711,"object_z_max":0.02918,"peak_contact_force":79.10637,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3.0,"raw_peak_contact_force":79.10637,"subtask_id":"push_goal","tcp_end":[0.48721,0.15154,0.04713],"tcp_start":[0.48719,0.1515,0.04713],"tcp_to_object_dist_end":0.03189,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4949,0.04108,0.02428],"object_pos_start":[0.49635,0.12681,0.0292],"object_to_goal_dist_end":0.1222,"object_to_goal_dist_start":0.20712,"object_z_max":0.04078,"peak_contact_force":0.59463,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1759.0,"raw_peak_contact_force":131.07139,"tcp_end":[0.49202,-0.00533,0.07136],"tcp_start":[0.48721,0.15154,0.04713],"tcp_to_object_dist_end":0.06617,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.12432,"average_solve_count":185.0,"average_success_count":185.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.01976,"approach_1.speed":0.0972,"contact_1.contact_force":1.0302,"contact_1.speed":0.02753,"push_1.push_distance":0.16071,"push_1.push_speed":0.03291,"retract_1.retract_speed":0.07286},"optimized_scores":{"best_composite_score":-0.0551,"best_fitness_score":0.1849,"best_task_score":0.20616},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":15.0,"contact_point_centroid":[0.54347,0.08102,0.05999],"force_p95":81.43773,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":120.96835,"mean_force":53.77624,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4986,0.08115,0.03665]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.54398,0.08342,0.05999],"force_p95":48.60311,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":49.21966,"mean_force":43.05414,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49916,0.08345,0.03655]},{"body_a":"peg","body_b":"channel_base_body","contact_count":45.0,"contact_point_centroid":[0.50331,0.04276,0.0098],"force_p95":13.61249,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.48605,"mean_force":7.08439,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50024,0.08844,0.03786]},{"body_a":"attachment","body_b":"peg","contact_count":38.0,"contact_point_centroid":[0.50434,0.07557,0.04352],"force_p95":13.65566,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.24816,"mean_force":7.89652,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49993,0.08741,0.03749]},{"body_a":"peg","body_b":"channel_base_body","contact_count":926.0,"contact_point_centroid":[0.50664,-0.00533,0.00884],"force_p95":8.81048,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.57343,"mean_force":2.72639,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49581,0.00248,0.0584]},{"body_a":"attachment","body_b":"peg","contact_count":361.0,"contact_point_centroid":[0.50145,0.0401,0.04198],"force_p95":9.82148,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.18703,"mean_force":5.38679,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49587,0.0504,0.04325]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":290.0,"contact_point_centroid":[0.52504,0.02075,0.02409],"force_p95":7.6499,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.03452,"mean_force":3.71672,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49578,0.03832,0.047]},{"body_a":"peg","body_b":"channel_base_body","contact_count":96.0,"contact_point_centroid":[0.50736,0.04872,0.00966],"force_p95":6.02668,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.05546,"mean_force":1.2851,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50315,0.09261,0.04805]},{"body_a":"attachment","body_b":"peg","contact_count":26.0,"contact_point_centroid":[0.50584,0.08066,0.05313],"force_p95":6.43429,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.84055,"mean_force":3.21231,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50304,0.0926,0.04737]},{"body_a":"peg","body_b":"channel_base_body","contact_count":972.0,"contact_point_centroid":[0.50586,0.06296,0.00937],"force_p95":0.55508,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.56049,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50942,0.15321,0.20907]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49966,0.19855,0.29725]},{"body_a":"peg","body_b":"channel_base_body","contact_count":394.0,"contact_point_centroid":[0.50588,0.06308,0.00938],"force_p95":0.55285,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55532,"mean_force":0.54656,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.5116,0.10227,0.09268]}],"total_contact_groups":12},"final_pose_error":0.01819,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50683,-0.01735,0.02414],"final_tcp_position":[0.49613,-0.0651,0.0803],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":120.96835,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50593,0.06297,0.0338],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14323,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54709,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1006.0,"raw_peak_contact_force":3.88411,"subtask_id":"align_standoff","tcp_end":[0.51981,0.11126,0.12985],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.10839,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":394.0,"n_steps_budget":1000.0,"object_pos_end":[0.50602,0.06302,0.03381],"object_pos_start":[0.50593,0.06297,0.0338],"object_to_goal_dist_end":0.14328,"object_to_goal_dist_start":0.14323,"object_z_max":0.03381,"peak_contact_force":1.40885,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":394.0,"raw_peak_contact_force":0.55532,"subtask_id":"align_standoff","tcp_end":[0.50541,0.09304,0.05631],"tcp_start":[0.51981,0.11126,0.12985],"tcp_to_object_dist_end":0.03752,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":96.0,"n_steps_budget":660.0,"object_pos_end":[0.50607,0.06245,0.03434],"object_pos_start":[0.50602,0.06302,0.03381],"object_to_goal_dist_end":0.14269,"object_to_goal_dist_start":0.14328,"object_z_max":0.03492,"peak_contact_force":0.63078,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":122.0,"raw_peak_contact_force":7.05546,"tcp_end":[0.50186,0.09246,0.03974],"tcp_start":[0.50541,0.09304,0.05631],"tcp_to_object_dist_end":0.03078,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":54.0,"n_steps_budget":1000.0,"object_pos_end":[0.50669,0.05418,0.03618],"object_pos_start":[0.50607,0.06245,0.03434],"object_to_goal_dist_end":0.1344,"object_to_goal_dist_start":0.14269,"object_z_max":0.03613,"peak_contact_force":49.21966,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":85.0,"raw_peak_contact_force":49.21966,"subtask_id":"push_goal","tcp_end":[0.49915,0.08323,0.03654],"tcp_start":[0.50186,0.09246,0.03974],"tcp_to_object_dist_end":0.03002,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50683,-0.01735,0.02414],"object_pos_start":[0.50669,0.05418,0.03618],"object_to_goal_dist_end":0.06499,"object_to_goal_dist_start":0.1344,"object_z_max":0.04069,"peak_contact_force":0.61913,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1592.0,"raw_peak_contact_force":120.96835,"tcp_end":[0.49613,-0.0651,0.0803],"tcp_start":[0.49915,0.08323,0.03654],"tcp_to_object_dist_end":0.07449,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```