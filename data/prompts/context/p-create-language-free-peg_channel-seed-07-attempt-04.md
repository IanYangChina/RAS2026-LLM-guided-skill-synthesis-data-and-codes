## Search State

- **Seed**: 7
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → contact → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | position_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.2917 | 0.57 | ✅ accepted |
| 3 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.1565 | 0.33 | ❌ rejected |
| 2 | approach → contact → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | position_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.0671 | 0.31 | ❌ rejected |
| 1 | approach → contact → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | position_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.1237 | 0.42 | ✅ accepted |
| 0 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.2119 | 0.23 | ✅ accepted |

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

## Current Skill (Q=0.292) — your mutation base

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

- **Composite score**: 0.292
- **task_score** (E): 0.573
- **fitness_score**: 0.532  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.440

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 0.67 | 1.00 | 0.1937 |
| contact_1 | 1.00 | 1.00 | 0.0612 |
| align_1 | 1.00 | 1.00 | 0.0172 |
| push_1 | 0.33 | 1.00 | 0.0993 |
| retract_1 | 1.00 | 1.00 | 0.1113 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 0.67 / step_budget | (0.500, 0.200, 0.300)→(0.503, 0.136, 0.119) | (0.509, 0.098, 0.040)→(0.502, 0.098, 0.034) | 0.179→0.178 | 1.00 / 1.000 | 0.537 | 2.732 |
| contact_1 | contact | 1.00 / force_exceeded | (0.503, 0.136, 0.119)→(0.497, 0.126, 0.059) | (0.502, 0.098, 0.034)→(0.502, 0.098, 0.034) | 0.178→0.178 | 1.00 / 2.000 | 12.931 | 12.931 |
| align_1 | align | 1.00 / step_budget | (0.497, 0.126, 0.059)→(0.495, 0.128, 0.043) | (0.502, 0.098, 0.034)→(0.503, 0.098, 0.034) | 0.178→0.178 | 1.00 / 1.333 | 33.443 | 63.442 |
| push_1 | push | 0.33 / step_budget | (0.495, 0.128, 0.043)→(0.496, 0.029, 0.043) | (0.503, 0.098, 0.034)→(0.505, 0.010, 0.033) | 0.178→0.091 | 1.00 / 2.333 | 74.665 | 119.237 |
| retract_1 | retract | 1.00 / step_budget | (0.496, 0.029, 0.043)→(0.496, -0.075, 0.083) | (0.505, 0.010, 0.033)→(0.502, -0.029, 0.024) | 0.091→0.055 | 1.00 / 1.000 | 0.615 | 79.874 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.984
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.984
- phase_score: 0.650
- phase_breakdown.push_goal_score: 0.695
- phase_breakdown.align_standoff_score: 0.546

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.783
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.984
- **Median Q (composite search score)**: 0.187
- **K-run variance**: 0.0320
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Parameters at upper bound**: push_1.push_speed
- **Final σ (mean)**: 0.220


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.78065,"average_solve_count":310.0,"average_success_count":310.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.0205,"approach_1.speed":0.02527,"contact_1.contact_force":8.96803,"contact_1.speed":0.02227,"push_1.push_distance":0.17147,"push_1.push_speed":0.03874,"retract_1.retract_speed":0.03889},"optimized_scores":{"best_composite_score":0.54348,"best_fitness_score":0.78348,"best_task_score":0.9838},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":103.0,"contact_point_centroid":[0.50455,0.10213,0.00936],"force_p95":61.36063,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":70.2436,"mean_force":17.4796,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49885,0.13894,0.05426]},{"body_a":"attachment","body_b":"peg","contact_count":49.0,"contact_point_centroid":[0.50469,0.12873,0.05738],"force_p95":63.16431,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":69.58294,"mean_force":35.8033,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.4995,0.13904,0.05738]},{"body_a":"attachment","body_b":"peg","contact_count":920.0,"contact_point_centroid":[0.49999,0.0519,0.03921],"force_p95":53.88898,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":57.41303,"mean_force":30.40721,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4933,0.06078,0.04127]},{"body_a":"peg","body_b":"channel_base_body","contact_count":894.0,"contact_point_centroid":[0.50702,0.02838,0.00974],"force_p95":43.42967,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":48.3647,"mean_force":24.57108,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49334,0.05966,0.04133]},{"body_a":"attachment","body_b":"peg","contact_count":203.0,"contact_point_centroid":[0.50089,-0.00683,0.04133],"force_p95":38.88772,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":41.28301,"mean_force":20.90807,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49172,-0.00149,0.04558]},{"body_a":"peg","body_b":"channel_base_body","contact_count":797.0,"contact_point_centroid":[0.50617,-0.03852,0.00853],"force_p95":29.80474,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":37.37396,"mean_force":5.33987,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49309,-0.03371,0.06106]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":806.0,"contact_point_centroid":[0.52534,0.03131,0.02652],"force_p95":27.63681,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":28.60649,"mean_force":17.7554,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49317,0.05191,0.0412]},{"body_a":"peg","body_b":"channel_base_body","contact_count":323.0,"contact_point_centroid":[0.50358,0.1116,0.00941],"force_p95":0.60695,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.24708,"mean_force":0.59819,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50147,0.14216,0.08917]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":191.0,"contact_point_centroid":[0.52515,-0.01807,0.02745],"force_p95":14.42988,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.94696,"mean_force":9.79893,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49174,-0.00082,0.04533]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50692,0.12933,0.05884],"force_p95":17.849,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.849,"mean_force":17.849,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50028,0.13893,0.06156]},{"body_a":"peg","body_b":"channel_base_body","contact_count":978.0,"contact_point_centroid":[0.50361,0.1117,0.00938],"force_p95":0.60828,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.55297,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5016,0.17187,0.20513]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49967,0.19946,0.29937]}],"total_contact_groups":12},"final_pose_error":0.00992,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50513,-0.04563,0.02413],"final_tcp_position":[0.49588,-0.07493,0.08254],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":70.2436,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50371,0.11177,0.0338],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19191,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.54493,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":994.0,"raw_peak_contact_force":2.06328,"subtask_id":"align_standoff","tcp_end":[0.50498,0.14581,0.1181],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09092,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":323.0,"n_steps_budget":1000.0,"object_pos_end":[0.50375,0.11168,0.03381],"object_pos_start":[0.50371,0.11177,0.0338],"object_to_goal_dist_end":0.19182,"object_to_goal_dist_start":0.19191,"object_z_max":0.03398,"peak_contact_force":18.24708,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":324.0,"raw_peak_contact_force":18.24708,"subtask_id":"align_standoff","tcp_end":[0.50028,0.13892,0.0614],"tcp_start":[0.50498,0.14581,0.1181],"tcp_to_object_dist_end":0.03893,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":103.0,"n_steps_budget":630.0,"object_pos_end":[0.50359,0.10754,0.03662],"object_pos_start":[0.50375,0.11168,0.03381],"object_to_goal_dist_end":0.18761,"object_to_goal_dist_start":0.19182,"object_z_max":0.03658,"peak_contact_force":0.42105,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":152.0,"raw_peak_contact_force":70.2436,"tcp_end":[0.4972,0.1384,0.0453],"tcp_start":[0.50028,0.13892,0.0614],"tcp_to_object_dist_end":0.03268,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50783,-0.02326,0.03847],"object_pos_start":[0.50359,0.10754,0.03662],"object_to_goal_dist_end":0.05729,"object_to_goal_dist_start":0.18761,"object_z_max":0.04027,"peak_contact_force":56.5472,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2620.0,"raw_peak_contact_force":57.41303,"subtask_id":"push_goal","tcp_end":[0.49351,0.00964,0.04187],"tcp_start":[0.4972,0.1384,0.0453],"tcp_to_object_dist_end":0.03604,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":798.0,"n_steps_budget":1000.0,"object_pos_end":[0.50513,-0.04563,0.02413],"object_pos_start":[0.50783,-0.02326,0.03847],"object_to_goal_dist_end":0.0382,"object_to_goal_dist_start":0.05729,"object_z_max":0.0386,"peak_contact_force":0.68339,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1191.0,"raw_peak_contact_force":41.28301,"tcp_end":[0.49588,-0.07493,0.08254],"tcp_start":[0.49351,0.00964,0.04187],"tcp_to_object_dist_end":0.066,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.66912,"average_solve_count":272.0,"average_success_count":272.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.01316,"approach_1.speed":0.05859,"contact_1.contact_force":4.43279,"contact_1.speed":0.01925,"push_1.push_distance":0.17557,"push_1.push_speed":0.03874,"retract_1.retract_speed":0.04446},"optimized_scores":{"best_composite_score":0.14416,"best_fitness_score":0.38416,"best_task_score":0.43986},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50059,0.10314,0.00609],"force_p95":167.40776,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":176.73824,"mean_force":133.62421,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49116,0.11407,0.05042]},{"body_a":"attachment","body_b":"peg","contact_count":1000.0,"contact_point_centroid":[0.50102,0.11161,0.04831],"force_p95":166.85706,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":175.91982,"mean_force":133.05044,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49116,0.11407,0.05042]},{"body_a":"peg","body_b":"channel_base_body","contact_count":944.0,"contact_point_centroid":[0.5003,0.0349,0.00841],"force_p95":119.82695,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":150.60249,"mean_force":20.23372,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4939,-0.0095,0.06791]},{"body_a":"attachment","body_b":"peg","contact_count":240.0,"contact_point_centroid":[0.50446,0.04891,0.0551],"force_p95":137.90208,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":150.0819,"mean_force":77.10862,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49498,0.04489,0.05791]},{"body_a":"peg","body_b":"channel_base_body","contact_count":407.0,"contact_point_centroid":[0.49335,0.11903,0.00803],"force_p95":104.6072,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":113.52887,"mean_force":82.14252,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.48673,0.14976,0.05086]},{"body_a":"attachment","body_b":"peg","contact_count":407.0,"contact_point_centroid":[0.49403,0.14168,0.04895],"force_p95":104.04442,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":112.93856,"mean_force":81.65633,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.48673,0.14976,0.05086]},{"body_a":"peg","body_b":"channel_base_body","contact_count":326.0,"contact_point_centroid":[0.49611,0.11916,0.00946],"force_p95":0.61073,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.75115,"mean_force":0.57948,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48423,0.14609,0.08149]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.49559,0.13758,0.05879],"force_p95":13.24619,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.24619,"mean_force":13.24619,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48688,0.14488,0.06258]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":15.0,"contact_point_centroid":[0.52512,0.04723,0.02446],"force_p95":7.20731,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.4064,"mean_force":2.12211,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49228,-0.00756,0.06568]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":14.0,"contact_point_centroid":[0.47499,0.00317,0.025],"force_p95":7.10359,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.22585,"mean_force":3.23919,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49394,-0.03768,0.0738]},{"body_a":"peg","body_b":"channel_base_body","contact_count":975.0,"contact_point_centroid":[0.49614,0.11909,0.00942],"force_p95":0.6093,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.54973,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4909,0.17305,0.19817]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49946,0.1993,0.29855]}],"total_contact_groups":12},"final_pose_error":0.00992,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49702,0.02462,0.02415],"final_tcp_position":[0.49592,-0.07374,0.08348],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":176.73824,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49601,0.11929,0.03389],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19942,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.51954,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":999.0,"raw_peak_contact_force":2.24822,"subtask_id":"align_standoff","tcp_end":[0.48397,0.14807,0.10423],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07695,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":326.0,"n_steps_budget":1000.0,"object_pos_end":[0.49602,0.11929,0.03404],"object_pos_start":[0.49601,0.11929,0.03389],"object_to_goal_dist_end":0.19942,"object_to_goal_dist_start":0.19942,"object_z_max":0.03418,"peak_contact_force":13.75115,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":327.0,"raw_peak_contact_force":13.75115,"subtask_id":"align_standoff","tcp_end":[0.48691,0.14488,0.06248],"tcp_start":[0.48397,0.14807,0.10423],"tcp_to_object_dist_end":0.03933,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":407.0,"n_steps_budget":960.0,"object_pos_end":[0.49815,0.12345,0.03109],"object_pos_start":[0.49602,0.11929,0.03404],"object_to_goal_dist_end":0.20365,"object_to_goal_dist_start":0.19942,"object_z_max":0.03416,"peak_contact_force":99.88199,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":814.0,"raw_peak_contact_force":113.52887,"tcp_end":[0.48734,0.15288,0.04603],"tcp_start":[0.48691,0.14488,0.06248],"tcp_to_object_dist_end":0.03473,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50145,0.07239,0.02641],"object_pos_start":[0.49815,0.12345,0.03109],"object_to_goal_dist_end":0.15301,"object_to_goal_dist_start":0.20365,"object_z_max":0.03138,"peak_contact_force":165.75191,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2000.0,"raw_peak_contact_force":176.73824,"subtask_id":"push_goal","tcp_end":[0.49235,0.06441,0.05108],"tcp_start":[0.48734,0.15288,0.04603],"tcp_to_object_dist_end":0.02749,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":951.0,"n_steps_budget":1000.0,"object_pos_end":[0.49702,0.02462,0.02415],"object_pos_start":[0.50145,0.07239,0.02641],"object_to_goal_dist_end":0.10585,"object_to_goal_dist_start":0.15301,"object_z_max":0.04075,"peak_contact_force":0.64362,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1213.0,"raw_peak_contact_force":150.60249,"tcp_end":[0.49592,-0.07374,0.08348],"tcp_start":[0.49235,0.06441,0.05108],"tcp_to_object_dist_end":0.11486,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.66543,"average_solve_count":269.0,"average_success_count":269.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.01953,"approach_1.speed":0.079,"contact_1.contact_force":4.93401,"contact_1.speed":0.01462,"push_1.push_distance":0.17126,"push_1.push_speed":0.05,"retract_1.retract_speed":0.0422},"optimized_scores":{"best_composite_score":0.18733,"best_fitness_score":0.42733,"best_task_score":0.29421},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":824.0,"contact_point_centroid":[0.54526,0.04979,0.05998],"force_p95":104.76766,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":123.56094,"mean_force":81.73845,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50043,0.05149,0.03666]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":92.0,"contact_point_centroid":[0.525,0.02205,0.06],"force_p95":83.70266,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":88.05545,"mean_force":39.05409,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50071,0.02206,0.0368]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.54543,0.0079,0.05999],"force_p95":47.45816,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":47.73743,"mean_force":43.30712,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50064,0.01174,0.03682]},{"body_a":"peg","body_b":"channel_base_body","contact_count":821.0,"contact_point_centroid":[0.50539,0.0069,0.00988],"force_p95":18.50514,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.88742,"mean_force":2.88151,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50044,0.05219,0.03667]},{"body_a":"attachment","body_b":"peg","contact_count":663.0,"contact_point_centroid":[0.5052,0.03869,0.04425],"force_p95":18.91708,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":27.62288,"mean_force":3.1927,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50045,0.0505,0.03667]},{"body_a":"attachment","body_b":"peg","contact_count":220.0,"contact_point_centroid":[0.50154,-0.01475,0.04152],"force_p95":6.81512,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.70941,"mean_force":3.0101,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49738,-0.00359,0.04212]},{"body_a":"peg","body_b":"channel_base_body","contact_count":789.0,"contact_point_centroid":[0.50429,-0.06027,0.00883],"force_p95":6.83799,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.89944,"mean_force":1.57686,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49664,-0.03407,0.05898]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":395.0,"contact_point_centroid":[0.5251,0.02436,0.02908],"force_p95":2.21885,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.93051,"mean_force":0.66705,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50042,0.05377,0.03666]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":59.0,"contact_point_centroid":[0.52502,-0.03821,0.02569],"force_p95":7.47382,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.65521,"mean_force":3.37944,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49741,-0.0417,0.0643]},{"body_a":"peg","body_b":"channel_base_body","contact_count":452.0,"contact_point_centroid":[0.50598,0.06293,0.00938],"force_p95":0.5532,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.79608,"mean_force":0.561,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.51092,0.10333,0.09375]},{"body_a":"peg","body_b":"channel_base_body","contact_count":97.0,"contact_point_centroid":[0.50508,0.04741,0.00967],"force_p95":4.27495,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.55346,"mean_force":1.24379,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.5025,0.09231,0.04579]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.5059,0.08097,0.05706],"force_p95":5.79623,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.41582,"mean_force":2.27634,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50488,0.09294,0.05485]},{"body_a":"attachment","body_b":"peg","contact_count":25.0,"contact_point_centroid":[0.50551,0.08033,0.05093],"force_p95":5.57548,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.29436,"mean_force":3.24223,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50226,0.09228,0.04453]},{"body_a":"peg","body_b":"channel_base_body","contact_count":972.0,"contact_point_centroid":[0.50586,0.06296,0.00937],"force_p95":0.55508,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.56049,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50908,0.15456,0.21163]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49962,0.19867,0.29747]}],"total_contact_groups":15},"final_pose_error":0.00993,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50447,-0.066,0.02437],"final_tcp_position":[0.49625,-0.07492,0.08233],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":123.56094,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50593,0.06297,0.0338],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14323,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54709,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1006.0,"raw_peak_contact_force":3.88411,"subtask_id":"align_standoff","tcp_end":[0.51923,0.1137,0.13445],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11349,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":452.0,"n_steps_budget":1000.0,"object_pos_end":[0.50597,0.06285,0.03381],"object_pos_start":[0.50593,0.06297,0.0338],"object_to_goal_dist_end":0.14311,"object_to_goal_dist_start":0.14323,"object_z_max":0.03381,"peak_contact_force":6.79608,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":455.0,"raw_peak_contact_force":6.79608,"subtask_id":"align_standoff","tcp_end":[0.50476,0.09273,0.05406],"tcp_start":[0.51923,0.1137,0.13445],"tcp_to_object_dist_end":0.03611,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":97.0,"n_steps_budget":660.0,"object_pos_end":[0.50609,0.0622,0.0344],"object_pos_start":[0.50597,0.06285,0.03381],"object_to_goal_dist_end":0.14244,"object_to_goal_dist_start":0.14311,"object_z_max":0.03493,"peak_contact_force":0.02538,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":122.0,"raw_peak_contact_force":6.55346,"tcp_end":[0.50119,0.09214,0.03742],"tcp_start":[0.50476,0.09273,0.05406],"tcp_to_object_dist_end":0.03049,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50698,-0.0178,0.03527],"object_pos_start":[0.50609,0.0622,0.0344],"object_to_goal_dist_end":0.06277,"object_to_goal_dist_start":0.14244,"object_z_max":0.03625,"peak_contact_force":1.69603,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2795.0,"raw_peak_contact_force":123.56094,"subtask_id":"push_goal","tcp_end":[0.50067,0.01187,0.03684],"tcp_start":[0.50119,0.09214,0.03742],"tcp_to_object_dist_end":0.03037,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":810.0,"n_steps_budget":1000.0,"object_pos_end":[0.50447,-0.066,0.02437],"object_pos_start":[0.50698,-0.0178,0.03527],"object_to_goal_dist_end":0.02145,"object_to_goal_dist_start":0.06277,"object_z_max":0.04078,"peak_contact_force":0.51652,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1073.0,"raw_peak_contact_force":47.73743,"tcp_end":[0.49625,-0.07492,0.08233],"tcp_start":[0.50067,0.01187,0.03684],"tcp_to_object_dist_end":0.05921,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```