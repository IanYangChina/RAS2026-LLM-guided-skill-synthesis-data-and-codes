## Search State

- **Seed**: 7
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → contact → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | position_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.2975 | 0.56 | ❌ rejected |
| 8 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.1961 | 0.12 | ❌ rejected |
| 7 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 9 | -0.0167 | 0.39 | ❌ rejected |
| 6 | approach → contact → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | position_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | force_exceeded | pose_tolerance | 11 | -0.1741 | 0.30 | ❌ rejected |
| 5 | approach → contact → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | position_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 10 | -0.1290 | 0.30 | ❌ rejected |

**Proposal policy**: task_score is 0.56 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.297) — your mutation base

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

- **Composite score**: 0.297
- **task_score** (E): 0.561
- **fitness_score**: 0.537  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.440

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 0.67 | 1.00 | 0.1963 |
| contact_1 | 1.00 | 1.00 | 0.0613 |
| align_1 | 1.00 | 1.00 | 0.0143 |
| push_1 | 0.33 | 1.00 | 0.1037 |
| retract_1 | 1.00 | 1.00 | 0.1064 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 0.67 / step_budget | (0.500, 0.200, 0.300)→(0.502, 0.136, 0.116) | (0.509, 0.098, 0.040)→(0.502, 0.098, 0.034) | 0.179→0.178 | 1.00 / 1.000 | 0.551 | 2.732 |
| contact_1 | contact | 1.00 / force_exceeded | (0.502, 0.136, 0.116)→(0.497, 0.124, 0.057) | (0.502, 0.098, 0.034)→(0.502, 0.098, 0.034) | 0.178→0.178 | 1.00 / 2.333 | 15.491 | 15.491 |
| align_1 | align | 1.00 / step_budget | (0.497, 0.124, 0.057)→(0.496, 0.127, 0.043) | (0.502, 0.098, 0.034)→(0.503, 0.097, 0.033) | 0.178→0.177 | 1.00 / 2.333 | 125.347 | 209.607 |
| push_1 | push | 0.33 / step_budget | (0.496, 0.127, 0.043)→(0.496, 0.023, 0.043) | (0.503, 0.097, 0.033)→(0.503, 0.003, 0.030) | 0.177→0.084 | 1.00 / 2.667 | 89.081 | 143.600 |
| retract_1 | retract | 1.00 / step_budget | (0.496, 0.023, 0.043)→(0.496, -0.074, 0.082) | (0.503, 0.003, 0.030)→(0.501, -0.037, 0.030) | 0.084→0.046 | 1.00 / 1.333 | 0.581 | 90.309 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 1.000
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.950
- phase_score: 0.781
- phase_breakdown.push_goal_score: 0.877
- phase_breakdown.align_standoff_score: 0.557

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.849
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.950
- **Median Q (composite search score)**: 0.144
- **K-run variance**: 0.0485
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.241


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.91703,"average_solve_count":229.0,"average_success_count":229.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.02178,"approach_1.speed":0.09963,"contact_1.contact_force":7.02067,"contact_1.speed":0.01975,"push_1.push_distance":0.17911,"push_1.push_speed":0.03948,"retract_1.retract_speed":0.0389},"optimized_scores":{"best_composite_score":0.60882,"best_fitness_score":0.84882,"best_task_score":0.95028},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":132.0,"contact_point_centroid":[0.50463,0.11162,0.00871],"force_p95":92.90769,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":98.74252,"mean_force":45.73655,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50069,0.13763,0.05562]},{"body_a":"attachment","body_b":"peg","contact_count":98.0,"contact_point_centroid":[0.50766,0.12882,0.0558],"force_p95":94.9473,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":98.19258,"mean_force":60.94039,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50093,0.13763,0.0574]},{"body_a":"attachment","body_b":"peg","contact_count":932.0,"contact_point_centroid":[0.50153,0.04835,0.04205],"force_p95":61.99766,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":65.44344,"mean_force":25.14644,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49628,0.05827,0.0434]},{"body_a":"peg","body_b":"channel_base_body","contact_count":983.0,"contact_point_centroid":[0.50375,0.02671,0.00966],"force_p95":61.35328,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":65.10654,"mean_force":24.03159,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49631,0.05758,0.04343]},{"body_a":"peg","body_b":"channel_base_body","contact_count":581.0,"contact_point_centroid":[0.50298,-0.10058,0.03668],"force_p95":53.50856,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":55.12904,"mean_force":29.97814,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49452,-0.05274,0.06518]},{"body_a":"attachment","body_b":"peg","contact_count":588.0,"contact_point_centroid":[0.49752,-0.05481,0.05705],"force_p95":50.43975,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":51.06373,"mean_force":28.53751,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4939,-0.04402,0.05784]},{"body_a":"peg","body_b":"channel_base_body","contact_count":182.0,"contact_point_centroid":[0.50355,0.11149,0.00941],"force_p95":0.59651,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.13889,"mean_force":0.66309,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50266,0.1374,0.07785]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50941,0.12883,0.0588],"force_p95":21.64981,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.64981,"mean_force":21.64981,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50105,0.13669,0.06227]},{"body_a":"peg","body_b":"channel_base_body","contact_count":713.0,"contact_point_centroid":[0.50561,-0.08207,0.00991],"force_p95":15.87917,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.28189,"mean_force":5.92757,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49427,-0.04955,0.0621]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":142.0,"contact_point_centroid":[0.52502,-0.02405,0.0266],"force_p95":8.7438,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.54028,"mean_force":5.66885,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49674,0.01094,0.04388]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":472.0,"contact_point_centroid":[0.52512,-0.09076,0.02663],"force_p95":8.11998,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.23037,"mean_force":4.96545,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.494,-0.0452,0.05924]},{"body_a":"peg","body_b":"channel_base_body","contact_count":978.0,"contact_point_centroid":[0.50361,0.11173,0.00938],"force_p95":0.61231,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.55296,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50213,0.16805,0.19235]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4997,0.19939,0.29907]}],"total_contact_groups":13},"final_pose_error":0.00996,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50399,-0.07214,0.04062],"final_tcp_position":[0.49591,-0.07586,0.08191],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":98.74252,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50368,0.1117,0.03393],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19183,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.59745,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":994.0,"raw_peak_contact_force":2.06328,"subtask_id":"align_standoff","tcp_end":[0.50595,0.13861,0.09402],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.06587,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":182.0,"n_steps_budget":1000.0,"object_pos_end":[0.50375,0.11175,0.03381],"object_pos_start":[0.50368,0.1117,0.03393],"object_to_goal_dist_end":0.19189,"object_to_goal_dist_start":0.19183,"object_z_max":0.03393,"peak_contact_force":22.13889,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":183.0,"raw_peak_contact_force":22.13889,"subtask_id":"align_standoff","tcp_end":[0.50104,0.13669,0.06212],"tcp_start":[0.50595,0.13861,0.09402],"tcp_to_object_dist_end":0.03782,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":132.0,"n_steps_budget":600.0,"object_pos_end":[0.50394,0.10696,0.03546],"object_pos_start":[0.50375,0.11175,0.03381],"object_to_goal_dist_end":0.18706,"object_to_goal_dist_start":0.19189,"object_z_max":0.03539,"peak_contact_force":0.41309,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":230.0,"raw_peak_contact_force":98.74252,"tcp_end":[0.49893,0.13695,0.0466],"tcp_start":[0.50104,0.13669,0.06212],"tcp_to_object_dist_end":0.03238,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5035,-0.06074,0.02806],"object_pos_start":[0.50394,0.10696,0.03546],"object_to_goal_dist_end":0.02293,"object_to_goal_dist_start":0.18706,"object_z_max":0.04045,"peak_contact_force":2.57849,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2057.0,"raw_peak_contact_force":65.44344,"subtask_id":"push_goal","tcp_end":[0.49487,-0.02438,0.0418],"tcp_start":[0.49893,0.13695,0.0466],"tcp_to_object_dist_end":0.03981,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":745.0,"n_steps_budget":1000.0,"object_pos_end":[0.50399,-0.07214,0.04062],"object_pos_start":[0.5035,-0.06074,0.02806],"object_to_goal_dist_end":0.00884,"object_to_goal_dist_start":0.02293,"object_z_max":0.04082,"peak_contact_force":0.46762,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2354.0,"raw_peak_contact_force":55.12904,"tcp_end":[0.49591,-0.07586,0.08191],"tcp_start":[0.49487,-0.02438,0.0418],"tcp_to_object_dist_end":0.04224,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.6699,"average_solve_count":309.0,"average_success_count":309.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.01427,"approach_1.speed":0.04956,"contact_1.contact_force":6.8257,"contact_1.speed":0.01496,"push_1.push_distance":0.16639,"push_1.push_speed":0.03031,"retract_1.retract_speed":0.04377},"optimized_scores":{"best_composite_score":0.1391,"best_fitness_score":0.3791,"best_task_score":0.45512},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50005,0.10845,0.00618],"force_p95":166.16449,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":176.58182,"mean_force":130.32087,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49095,0.12112,0.0503]},{"body_a":"attachment","body_b":"peg","contact_count":1000.0,"contact_point_centroid":[0.5006,0.11801,0.04826],"force_p95":165.60721,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":175.84904,"mean_force":129.7597,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49095,0.12112,0.0503]},{"body_a":"peg","body_b":"channel_base_body","contact_count":993.0,"contact_point_centroid":[0.50082,0.03796,0.0084],"force_p95":115.07669,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":146.78228,"mean_force":23.47868,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49377,-0.00259,0.06747]},{"body_a":"attachment","body_b":"peg","contact_count":291.0,"contact_point_centroid":[0.50442,0.05576,0.05499],"force_p95":130.02488,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":146.19896,"mean_force":78.10115,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49464,0.05243,0.05797]},{"body_a":"peg","body_b":"channel_base_body","contact_count":380.0,"contact_point_centroid":[0.49354,0.11901,0.00801],"force_p95":101.60529,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":117.12115,"mean_force":79.70021,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.4868,0.14953,0.05094]},{"body_a":"attachment","body_b":"peg","contact_count":380.0,"contact_point_centroid":[0.49425,0.14166,0.04894],"force_p95":104.73294,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":116.37912,"mean_force":80.62614,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.4868,0.14953,0.05094]},{"body_a":"peg","body_b":"world","contact_count":61.0,"contact_point_centroid":[0.49734,0.12529,-3e-05],"force_p95":18.31836,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.78156,"mean_force":10.43235,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.48736,0.15228,0.04666]},{"body_a":"peg","body_b":"channel_base_body","contact_count":327.0,"contact_point_centroid":[0.49596,0.11934,0.00947],"force_p95":0.6053,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.21977,"mean_force":0.5763,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48432,0.14623,0.08217]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.49623,0.13832,0.05853],"force_p95":12.71603,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.71603,"mean_force":12.71603,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48702,0.14484,0.06257]},{"body_a":"peg","body_b":"world","contact_count":4.0,"contact_point_centroid":[0.4964,0.11118,-2e-05],"force_p95":10.26537,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.87139,"mean_force":3.259,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48849,0.13683,0.04717]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":6.0,"contact_point_centroid":[0.47498,0.00639,0.02991],"force_p95":5.91433,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.46037,"mean_force":1.82639,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49414,-0.04028,0.07511]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":11.0,"contact_point_centroid":[0.52507,0.04885,0.02475],"force_p95":6.91314,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.17349,"mean_force":2.1245,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4924,-0.00919,0.06717]},{"body_a":"peg","body_b":"channel_base_body","contact_count":975.0,"contact_point_centroid":[0.49615,0.11914,0.00943],"force_p95":0.60899,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.54827,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49094,0.1732,0.19874]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49946,0.19929,0.2985]}],"total_contact_groups":14},"final_pose_error":0.01178,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49588,0.02676,0.02411],"final_tcp_position":[0.4958,-0.07151,0.083],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":176.58182,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49603,0.11905,0.03392],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19919,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.50789,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":999.0,"raw_peak_contact_force":2.24822,"subtask_id":"align_standoff","tcp_end":[0.48404,0.14837,0.10538],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07817,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":327.0,"n_steps_budget":1000.0,"object_pos_end":[0.49602,0.11966,0.03405],"object_pos_start":[0.49603,0.11905,0.03392],"object_to_goal_dist_end":0.19979,"object_to_goal_dist_start":0.19919,"object_z_max":0.03413,"peak_contact_force":13.21977,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":328.0,"raw_peak_contact_force":13.21977,"subtask_id":"align_standoff","tcp_end":[0.48704,0.14484,0.06247],"tcp_start":[0.48404,0.14837,0.10538],"tcp_to_object_dist_end":0.03901,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":380.0,"n_steps_budget":900.0,"object_pos_end":[0.49737,0.12407,0.03072],"object_pos_start":[0.49602,0.11966,0.03405],"object_to_goal_dist_end":0.2043,"object_to_goal_dist_start":0.19979,"object_z_max":0.03417,"peak_contact_force":104.89974,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":821.0,"raw_peak_contact_force":117.12115,"tcp_end":[0.48741,0.15279,0.04609],"tcp_start":[0.48704,0.14484,0.06247],"tcp_to_object_dist_end":0.03406,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50007,0.07825,0.02556],"object_pos_start":[0.49737,0.12407,0.03072],"object_to_goal_dist_end":0.1589,"object_to_goal_dist_start":0.2043,"object_z_max":0.03101,"peak_contact_force":157.88729,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2004.0,"raw_peak_contact_force":176.58182,"subtask_id":"push_goal","tcp_end":[0.49187,0.0748,0.05061],"tcp_start":[0.48741,0.15279,0.04609],"tcp_to_object_dist_end":0.02658,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49588,0.02676,0.02411],"object_pos_start":[0.50007,0.07825,0.02556],"object_to_goal_dist_end":0.10802,"object_to_goal_dist_start":0.1589,"object_z_max":0.04076,"peak_contact_force":0.56438,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1301.0,"raw_peak_contact_force":146.78228,"tcp_end":[0.4958,-0.07151,0.083],"tcp_start":[0.49187,0.0748,0.05061],"tcp_to_object_dist_end":0.11456,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.58456,"average_solve_count":272.0,"average_success_count":272.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.02403,"approach_1.speed":0.05518,"contact_1.contact_force":6.76977,"contact_1.speed":0.01749,"push_1.push_distance":0.17062,"push_1.push_speed":0.04923,"retract_1.retract_speed":0.0768},"optimized_scores":{"best_composite_score":0.14448,"best_fitness_score":0.38448,"best_task_score":0.2788},"replay_outcomes":[{"contacts":{"omitted_contact_groups":3,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":181.0,"contact_point_centroid":[0.54565,0.09096,0.05986],"force_p95":396.86207,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":412.95677,"mean_force":311.95835,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50077,0.09063,0.03643]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":172.0,"contact_point_centroid":[0.52504,0.0908,0.05998],"force_p95":305.37823,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":321.78456,"mean_force":186.31095,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50079,0.09064,0.03646]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":874.0,"contact_point_centroid":[0.54576,0.05443,0.05998],"force_p95":150.71431,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":188.77333,"mean_force":102.20009,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5005,0.05583,0.03748]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":396.0,"contact_point_centroid":[0.52501,0.04216,0.05999],"force_p95":110.73649,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":153.06596,"mean_force":58.94213,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50052,0.04206,0.03758]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.54575,0.0158,0.05997],"force_p95":67.32723,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":69.01709,"mean_force":53.90312,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50047,0.01919,0.03767]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":5.0,"contact_point_centroid":[0.52502,0.01918,0.05999],"force_p95":37.95114,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":45.46469,"mean_force":10.67232,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50047,0.01917,0.03769]},{"body_a":"attachment","body_b":"peg","contact_count":602.0,"contact_point_centroid":[0.5053,0.04086,0.04492],"force_p95":21.51016,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":34.165,"mean_force":3.33168,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5005,0.05266,0.03751]},{"body_a":"peg","body_b":"channel_base_body","contact_count":858.0,"contact_point_centroid":[0.5049,0.01134,0.00987],"force_p95":16.61907,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":33.94699,"mean_force":2.6291,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5005,0.05587,0.03748]},{"body_a":"peg","body_b":"channel_base_body","contact_count":699.0,"contact_point_centroid":[0.50288,-0.05518,0.0088],"force_p95":5.00436,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.3968,"mean_force":1.47159,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49653,-0.03111,0.05971]},{"body_a":"attachment","body_b":"peg","contact_count":216.0,"contact_point_centroid":[0.50108,-0.00911,0.04216],"force_p95":5.86985,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.23295,"mean_force":3.00649,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4973,0.00214,0.04308]},{"body_a":"peg","body_b":"channel_base_body","contact_count":608.0,"contact_point_centroid":[0.50585,0.06195,0.0094],"force_p95":0.55322,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.11461,"mean_force":0.60869,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50896,0.10609,0.09612]},{"body_a":"attachment","body_b":"peg","contact_count":10.0,"contact_point_centroid":[0.50504,0.08015,0.05178],"force_p95":8.66985,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.34778,"mean_force":4.25423,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50354,0.0921,0.04967]},{"body_a":"attachment","body_b":"peg","contact_count":80.0,"contact_point_centroid":[0.50648,0.0787,0.04849],"force_p95":6.8821,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.99407,"mean_force":1.2175,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50102,0.09063,0.03731]},{"body_a":"peg","body_b":"channel_base_body","contact_count":232.0,"contact_point_centroid":[0.50636,0.05441,0.00963],"force_p95":4.08521,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.21607,"mean_force":0.88086,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50094,0.09063,0.03744]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":415.0,"contact_point_centroid":[0.52509,0.02617,0.03061],"force_p95":2.59808,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.17773,"mean_force":0.66581,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5005,0.05572,0.03749]},{"body_a":"peg","body_b":"channel_base_body","contact_count":972.0,"contact_point_centroid":[0.50586,0.06296,0.00937],"force_p95":0.55508,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.56049,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50805,0.15861,0.21927]}],"total_contact_groups":19},"final_pose_error":0.00999,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50334,-0.06632,0.02421],"final_tcp_position":[0.49625,-0.07468,0.08242],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":412.95677,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50593,0.06297,0.0338],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14323,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54709,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1006.0,"raw_peak_contact_force":3.88411,"subtask_id":"align_standoff","tcp_end":[0.51728,0.12128,0.1488],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12944,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":608.0,"n_steps_budget":1000.0,"object_pos_end":[0.5066,0.06166,0.03529],"object_pos_start":[0.50593,0.06297,0.0338],"object_to_goal_dist_end":0.14189,"object_to_goal_dist_start":0.14323,"object_z_max":0.03531,"peak_contact_force":11.11461,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":619.0,"raw_peak_contact_force":11.11461,"subtask_id":"align_standoff","tcp_end":[0.5031,0.09091,0.04567],"tcp_start":[0.51728,0.12128,0.1488],"tcp_to_object_dist_end":0.03124,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":234.0,"n_steps_budget":600.0,"object_pos_end":[0.50691,0.06071,0.03377],"object_pos_start":[0.5066,0.06166,0.03529],"object_to_goal_dist_end":0.14102,"object_to_goal_dist_start":0.14189,"object_z_max":0.0356,"peak_contact_force":270.72877,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":692.0,"raw_peak_contact_force":412.95677,"tcp_end":[0.50073,0.09069,0.037],"tcp_start":[0.5031,0.09091,0.04567],"tcp_to_object_dist_end":0.03078,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5069,-0.00962,0.03587],"object_pos_start":[0.50691,0.06071,0.03377],"object_to_goal_dist_end":0.07084,"object_to_goal_dist_start":0.14102,"object_z_max":0.03613,"peak_contact_force":106.77705,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3145.0,"raw_peak_contact_force":188.77333,"subtask_id":"push_goal","tcp_end":[0.50047,0.01921,0.03767],"tcp_start":[0.50073,0.09069,0.037],"tcp_to_object_dist_end":0.02959,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":732.0,"n_steps_budget":930.0,"object_pos_end":[0.50334,-0.06632,0.02421],"object_pos_start":[0.5069,-0.00962,0.03587],"object_to_goal_dist_end":0.02116,"object_to_goal_dist_start":0.07084,"object_z_max":0.04077,"peak_contact_force":0.70957,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":924.0,"raw_peak_contact_force":69.01709,"tcp_end":[0.49625,-0.07468,0.08242],"tcp_start":[0.50047,0.01921,0.03767],"tcp_to_object_dist_end":0.05923,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```