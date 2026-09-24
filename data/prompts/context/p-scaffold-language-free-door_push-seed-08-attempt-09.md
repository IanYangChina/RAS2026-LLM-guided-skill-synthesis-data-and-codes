## Search State

- **Seed**: 8
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → contact → push → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | admittance_control | position_control | pose_tolerance | force_exceeded | time_limit | time_limit | pose_tolerance | 9 | 0.7933 | 1.00 | ❌ rejected |
| 8 | approach → contact → push → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | admittance_control | position_control | pose_tolerance | force_exceeded | time_limit | time_limit | pose_tolerance | 9 | 0.7933 | 1.00 | ✅ accepted |
| 7 | approach → contact → push → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.3895 | 0.63 | ❌ rejected |
| 6 | approach → contact → push → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | admittance_control | position_control | pose_tolerance | force_exceeded | time_limit | time_limit | pose_tolerance | 9 | 0.7320 | 0.94 | ✅ accepted |
| 5 | approach → contact → push → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | admittance_control | position_control | pose_tolerance | force_exceeded | time_limit | time_limit | pose_tolerance | 9 | 0.6796 | 0.91 | ✅ accepted |

**Proposal policy**: task_score is near-perfect (1.00). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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

- Task name: door_push
- Frozen realised-scene SHA-256: `03ad88d640dcd23384857b752dfa12af63a722a6c6b9379a358f8168d1c71e09`
- Frozen initial hinge angle: -0.060 rad
- target_hinge_angle: 0.524 rad (task success = realised hinge-angle delta ratio; not TCP proximity)
- Goal tolerance: 0.05 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 30.0 N
- Robot initial TCP position: (0.1, 0.4, 0.35)
- Primary evaluation target: **hinge angle delta ratio (realised hinge motion / target_hinge_angle)**

## Scene Entities

robot:
  model: panda_full
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.1, 0.4, 0.35]
objects:
  - name: door_panel
    role: fixture
    dynamics: hinged
    geometry: box
    dimensions_m: [0.4, 0.02, 0.7]
    hinge_axis: Z
    hinge_joint_name: door_hinge
  - name: door_handle
    role: grasp_site
    dynamics: hinged_with_panel
    geometry: site
    body_frame_offset_m: [-0.4, -0.02, 0.35]
  - name: door_frame
    role: fixture
    dynamics: static
    geometry: box
task_landmarks:
  frozen_fixture_position: [0.5, 0.2, 0]
  frozen_initial_hinge_angle_rad: -0.0604
  frozen_fixtures: {'door_panel': [0.5, 0.2, 0.0]}
  door_hinge_axis: [0, 0, 1]
  goal_tolerance_m: 0.05
  force_limit_n: 30
  force_scale_n: 5
  target_hinge_angle_rad: 0.524
  realized_scene_sha256: 03ad88d640dcd23384857b752dfa12af63a722a6c6b9379a358f8168d1c71e09

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 1.000, which indicates the subtask decomposition is already effective.
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
| `object` | offset from object initial position | approach/contact targets near object |
| `goal` | offset from task goal position | final destination targets |
| `fixture` | offset from fixture pose (0.5, 0.2, 0.0) | approach/contact targets near fixture |

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

## Current Skill (Q=0.793) — your mutation base

```yaml
skill: door_push
dsl_version: 2
subtasks:
- id: reach_contact
  anchor: world
  offset:
  - 0.1
  - 0.18
  - 0.35
  weight: 0.3
- id: push_hinge
  anchor: fixture
  target_entity: hinge
  metric: hinge_angle
  weight: 0.7
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: world
    offset:
    - 0.1
    - 0.18
    - 0.35
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.15
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: approach_contact_check
    when: after_phase
    predicate: force_below
    threshold: 30.0
    on_failure: continue
  subtask_id: reach_contact
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: world
    offset:
    - 0.1
    - 0.18
    - 0.35
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 5.0
      - 15.0
      default: 8.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.01
    - 0.0
- id: push_main
  type: push
  generator: linear_cartesian
  control: admittance_control
  termination: time_limit
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.25
      axis: world_y
      mode: add_to_offset
      sign: negative
    tolerance: 0.04
    orientation:
      mode: keep_current
  parameters:
    push_main_distance:
      type: scalar
      range:
      - 0.1
      - 0.4
      default: 0.25
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_main_speed:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
    push_main_time:
      type: scalar
      range:
      - 3.0
      - 15.0
      default: 10.0
      binds_to:
      - path: duration.max_time
        mode: replace
  guards:
  - id: push_main_force_guard
    when: during_phase
    predicate: force_below
    threshold: 35.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.005
    - 0.0
  subtask_id: push_hinge
- id: push_final
  type: push
  generator: linear_cartesian
  control: admittance_control
  termination: time_limit
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.12
      axis: world_y
      mode: add_to_offset
      sign: negative
    tolerance: 0.04
    orientation:
      mode: keep_current
  parameters:
    push_final_distance:
      type: scalar
      range:
      - 0.04
      - 0.25
      default: 0.12
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_final_speed:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
    push_final_time:
      type: scalar
      range:
      - 2.0
      - 12.0
      default: 6.0
      binds_to:
      - path: duration.max_time
        mode: replace
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.005
    - 0.0
  subtask_id: push_hinge
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: world
    offset:
    - 0.1
    - 0.35
    - 0.35
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    retract_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=world, offset=[0.1, 0.18, 0.35], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=approach_contact_check, when=after_phase, predicate=force_below, on_failure=continue, threshold=30.0
- **contact_1** (`contact`)
  - target: source=yaml, anchor=world, offset=[0.1, 0.18, 0.35], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.01, 0.0]
- **push_main** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_y, distance=0.25, mode=add_to_offset, sign=negative}, tolerance=0.04
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_main_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_main_speed: status=consumed; consumers=generator.speed (replace)
    - push_main_time: status=consumed; consumers=duration.max_time (replace)
  - guards:
    - id=push_main_force_guard, when=during_phase, predicate=force_below, on_failure=retry, threshold=35.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.005, 0.0]
- **push_final** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_y, distance=0.12, mode=add_to_offset, sign=negative}, tolerance=0.04
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_final_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_final_speed: status=consumed; consumers=generator.speed (replace)
    - push_final_time: status=consumed; consumers=duration.max_time (replace)
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.005, 0.0]
- **retract_1** (`retract`)
  - target: source=yaml, anchor=world, offset=[0.1, 0.35, 0.35], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.793
- **task_score** (E): 1.000
- **fitness_score**: 1.000  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.540

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2094 |
| contact_1 | 1.00 | 1.00 | 0.0012 |
| push_main | 1.00 | 1.00 | 0.1160 |
| push_final | 1.00 | 1.00 | 0.1111 |
| retract_1 | 1.00 | 0.00 | 0.3554 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.100, 0.399, 0.350)→(0.100, 0.190, 0.349) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 1.000 | 13.326 | 22.609 |
| contact_1 | contact | 1.00 / force_exceeded | (0.100, 0.190, 0.349)→(0.100, 0.189, 0.348) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 2.333 | 17.179 | 21.262 |
| push_main | push | 1.00 / time_limit | (0.100, 0.189, 0.348)→(0.096, 0.090, 0.409) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 1.000 | 8.555 | 29.469 |
| push_final | push | 1.00 / time_limit | (0.096, 0.090, 0.409)→(0.105, -0.020, 0.411) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 2.333 | 8.893 | 30.067 |
| retract_1 | retract | 1.00 / step_budget | (0.105, -0.020, 0.411)→(0.100, 0.330, 0.351) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.00 / 0.000 | 0.000 | 46.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 1.000
- arc_quality: 1.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 1.000
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.793
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 5.3
- **Final σ (mean)**: 0.443


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `ea6bae111f14debb91f5aac35e1b236c8a3b6c6e55761aa2eab002718511c500`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"hinge_delta_deg":10.0,"object_xy_delta":[0.0,0.0]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `4672b672dcc6ffecf2b710096d1b05b46bb79ca3304db4877275d5463822e477`; realized-scene SHA-256: `03ad88d640dcd23384857b752dfa12af63a722a6c6b9379a358f8168d1c71e09`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":-0.0604,"panel":{"name":"door_panel","orientation":[0.99954,0.0,0.0,-0.03019],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99954,0.0,0.0,-0.03019],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.23585,"average_solve_count":212.0,"average_success_count":212.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.09015,"contact_1.contact_force_threshold":6.91292,"push_final.push_final_distance":0.20227,"push_final.push_final_speed":0.04337,"push_final.push_final_time":6.55704,"push_main.push_main_distance":0.27963,"push_main.push_main_speed":0.05619,"push_main.push_main_time":10.55912,"retract_1.retract_speed":0.09067},"optimized_scores":{"best_composite_score":0.79333,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":627.0,"contact_point_centroid":[0.16431,0.08778,0.39712],"force_p95":19.23134,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":27.74454,"mean_force":13.04986,"phase_index":2.0,"phase_name":"push_main","phase_type":"push","tcp_position_centroid":[0.09892,0.14504,0.37176]},{"body_a":"door_panel","body_b":"link7","contact_count":79.0,"contact_point_centroid":[0.16509,0.14386,0.37233],"force_p95":23.53279,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.7102,"mean_force":14.8004,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.09984,0.20127,0.34846]},{"body_a":"door_panel","body_b":"link7","contact_count":697.0,"contact_point_centroid":[0.16107,0.00797,0.44639],"force_p95":16.25521,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.22863,"mean_force":11.28308,"phase_index":3.0,"phase_name":"push_final","phase_type":"push","tcp_position_centroid":[0.09535,0.06448,0.41615]},{"body_a":"door_panel","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.16845,-0.02372,0.44516],"force_p95":21.61296,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.80179,"mean_force":11.23842,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.09858,0.02719,0.41784]},{"body_a":"door_panel","body_b":"link6","contact_count":301.0,"contact_point_centroid":[0.10096,0.18537,0.45542],"force_p95":16.73786,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.18096,"mean_force":8.61201,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.09968,0.25995,0.34812]},{"body_a":"door_panel","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.16507,0.13185,0.37219],"force_p95":18.07821,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.50754,"mean_force":9.965,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.09983,0.18934,0.34832]},{"body_a":"world","body_b":"door_panel","contact_count":848.0,"contact_point_centroid":[0.30077,0.18829,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.09968,0.29393,0.34805]},{"body_a":"world","body_b":"door_panel","contact_count":20.0,"contact_point_centroid":[0.30601,0.15031,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.09982,0.18941,0.34833]},{"body_a":"world","body_b":"door_panel","contact_count":1080.0,"contact_point_centroid":[0.31388,0.12712,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_main","phase_type":"push","tcp_position_centroid":[0.09893,0.1443,0.37253]},{"body_a":"world","body_b":"door_panel","contact_count":900.0,"contact_point_centroid":[0.33081,0.09331,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"push_final","phase_type":"push","tcp_position_centroid":[0.09542,0.06526,0.41578]},{"body_a":"world","body_b":"door_panel","contact_count":648.0,"contact_point_centroid":[0.33863,0.08144,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.09963,0.17918,0.38526]}],"total_contact_groups":11},"final_pose_error":0.01998,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.09988,0.33011,0.35189],"hinge_angle":0.57332,"initial_hinge_angle":-0.0604,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.0604,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":27.74454,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":830.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":13.26551,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1228.0,"raw_peak_contact_force":24.7102,"subtask_id":"reach_contact","tcp_end":[0.09987,0.18987,0.34854],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.40928,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":14.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":16.36085,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":25.0,"raw_peak_contact_force":18.50754,"tcp_end":[0.0998,0.1888,0.34815],"tcp_start":[0.09987,0.18987,0.34854],"tcp_to_object_dist_end":0.40842,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":10.73601,"phase_name":"push_main","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1707.0,"raw_peak_contact_force":27.74454,"subtask_id":"push_hinge","tcp_end":[0.09655,0.10099,0.40445],"tcp_start":[0.0998,0.1888,0.34815],"tcp_to_object_dist_end":0.4279,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":10.84165,"phase_name":"push_final","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1597.0,"raw_peak_contact_force":24.22863,"subtask_id":"push_hinge","tcp_end":[0.09858,0.02715,0.41784],"tcp_start":[0.09655,0.10099,0.40445],"tcp_to_object_dist_end":0.43017,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":759.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":651.0,"raw_peak_contact_force":22.80179,"tcp_end":[0.09988,0.33011,0.35189],"tcp_start":[0.09858,0.02715,0.41784],"tcp_to_object_dist_end":0.49272,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `6091bac9443f311cc90f1388d6700bb5b9c315c724ba8069ca061d7c4a07c1f1`; realized-scene SHA-256: `8483aeff51d0063ec1cf7a724dac4352cd76049b8e216b9602c279ab004268b5`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":0.12924,"panel":{"name":"door_panel","orientation":[0.99791,0.0,0.0,0.06458],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99791,0.0,0.0,0.06458],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.18725,"average_solve_count":251.0,"average_success_count":251.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.06736,"contact_1.contact_force_threshold":10.995,"push_final.push_final_distance":0.13509,"push_final.push_final_speed":0.07773,"push_final.push_final_time":5.71382,"push_main.push_main_distance":0.26542,"push_main.push_main_speed":0.06405,"push_main.push_main_time":13.4136,"retract_1.retract_speed":0.08301},"optimized_scores":{"best_composite_score":0.79333,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.19546,-0.05933,0.42566],"force_p95":47.83997,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":49.97006,"mean_force":28.66915,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.10771,-0.04036,0.40737]},{"body_a":"door_panel","body_b":"link7","contact_count":652.0,"contact_point_centroid":[0.17127,-0.02005,0.44199],"force_p95":28.39129,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":32.86792,"mean_force":12.50761,"phase_index":3.0,"phase_name":"push_final","phase_type":"push","tcp_position_centroid":[0.09939,0.02714,0.41519]},{"body_a":"door_panel","body_b":"link7","contact_count":637.0,"contact_point_centroid":[0.16398,0.08181,0.40186],"force_p95":19.46022,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.93906,"mean_force":13.13908,"phase_index":2.0,"phase_name":"push_main","phase_type":"push","tcp_position_centroid":[0.09859,0.13908,0.37596]},{"body_a":"door_panel","body_b":"link7","contact_count":7.0,"contact_point_centroid":[0.16507,0.13155,0.37211],"force_p95":21.7174,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.86862,"mean_force":11.40495,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.09983,0.18904,0.34824]},{"body_a":"door_panel","body_b":"link7","contact_count":80.0,"contact_point_centroid":[0.16511,0.14368,0.37226],"force_p95":21.38761,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.6469,"mean_force":14.61232,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.09986,0.20111,0.3484]},{"body_a":"door_panel","body_b":"link6","contact_count":20.0,"contact_point_centroid":[0.1034,0.14858,0.45276],"force_p95":15.3971,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.47232,"mean_force":9.22161,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.09984,0.21487,0.3482]},{"body_a":"world","body_b":"door_panel","contact_count":976.0,"contact_point_centroid":[0.30304,0.16395,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.09971,0.29544,0.34801]},{"body_a":"world","body_b":"door_panel","contact_count":20.0,"contact_point_centroid":[0.30605,0.15017,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.09983,0.18912,0.34826]},{"body_a":"world","body_b":"door_panel","contact_count":912.0,"contact_point_centroid":[0.3144,0.12615,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_main","phase_type":"push","tcp_position_centroid":[0.09875,0.14197,0.37337]},{"body_a":"world","body_b":"door_panel","contact_count":860.0,"contact_point_centroid":[0.33993,0.08061,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"push_final","phase_type":"push","tcp_position_centroid":[0.09959,0.02581,0.41486]},{"body_a":"world","body_b":"door_panel","contact_count":812.0,"contact_point_centroid":[0.35233,0.06476,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.10451,0.13129,0.38448]}],"total_contact_groups":11},"final_pose_error":0.01981,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.10023,0.3302,0.35063],"hinge_angle":0.67515,"initial_hinge_angle":0.12924,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.12924,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":49.97006,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":870.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":13.5136,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1076.0,"raw_peak_contact_force":22.6469,"subtask_id":"reach_contact","tcp_end":[0.09988,0.18974,0.34851],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.40919,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":18.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":13.76582,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":27.0,"raw_peak_contact_force":23.86862,"tcp_end":[0.0998,0.18821,0.34807],"tcp_start":[0.09988,0.18974,0.34851],"tcp_to_object_dist_end":0.40809,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":11.55504,"phase_name":"push_main","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1549.0,"raw_peak_contact_force":29.93906,"subtask_id":"push_hinge","tcp_end":[0.09548,0.08695,0.41094],"tcp_start":[0.0998,0.18821,0.34807],"tcp_to_object_dist_end":0.43075,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":15.83762,"phase_name":"push_final","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1512.0,"raw_peak_contact_force":32.86792,"subtask_id":"push_hinge","tcp_end":[0.10771,-0.04034,0.40738],"tcp_start":[0.09548,0.08695,0.41094],"tcp_to_object_dist_end":0.4233,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":967.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":814.0,"raw_peak_contact_force":49.97006,"tcp_end":[0.10023,0.3302,0.35063],"tcp_start":[0.10771,-0.04034,0.40738],"tcp_to_object_dist_end":0.49196,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `3d62b54ff2d8b84e841b6e4711bcf5c00d2771c3332b770c71c3a72dad860645`; realized-scene SHA-256: `0f1da74cddf6e66211f4104e2813e757573c0ccccbad31f53b6672ec96f686dd`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":0.15917,"panel":{"name":"door_panel","orientation":[0.99683,0.0,0.0,0.0795],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99683,0.0,0.0,0.0795],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.98,"average_solve_count":250.0,"average_success_count":250.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.04001,"contact_1.contact_force_threshold":8.61995,"push_final.push_final_distance":0.1963,"push_final.push_final_speed":0.07977,"push_final.push_final_time":9.6422,"push_main.push_main_distance":0.16391,"push_main.push_main_speed":0.06796,"push_main.push_main_time":5.03981,"retract_1.retract_speed":0.1496},"optimized_scores":{"best_composite_score":0.79333,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.1973,-0.06147,0.42345],"force_p95":62.31858,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":65.5985,"mean_force":32.79925,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.10798,-0.04674,0.40697]},{"body_a":"door_panel","body_b":"link7","contact_count":661.0,"contact_point_centroid":[0.17218,-0.02266,0.44167],"force_p95":28.67115,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":33.10574,"mean_force":12.31071,"phase_index":3.0,"phase_name":"push_final","phase_type":"push","tcp_position_centroid":[0.09976,0.02353,0.41522]},{"body_a":"door_panel","body_b":"link7","contact_count":662.0,"contact_point_centroid":[0.16392,0.08039,0.40308],"force_p95":19.58239,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":30.72463,"mean_force":13.16207,"phase_index":2.0,"phase_name":"push_main","phase_type":"push","tcp_position_centroid":[0.09854,0.13769,0.37699]},{"body_a":"door_panel","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.16514,0.13214,0.37223],"force_p95":19.27016,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.41129,"mean_force":7.1371,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.0999,0.18964,0.34838]},{"body_a":"door_panel","body_b":"link7","contact_count":63.0,"contact_point_centroid":[0.16514,0.14079,0.37222],"force_p95":19.99348,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.47065,"mean_force":14.67777,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.0999,0.19823,0.34837]},{"body_a":"world","body_b":"door_panel","contact_count":948.0,"contact_point_centroid":[0.30403,0.15883,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.0997,0.30198,0.34797]},{"body_a":"world","body_b":"door_panel","contact_count":8.0,"contact_point_centroid":[0.30597,0.15047,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.09991,0.18976,0.34842]},{"body_a":"world","body_b":"door_panel","contact_count":1004.0,"contact_point_centroid":[0.31536,0.1239,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_main","phase_type":"push","tcp_position_centroid":[0.0986,0.13724,0.37728]},{"body_a":"world","body_b":"door_panel","contact_count":912.0,"contact_point_centroid":[0.3414,0.07858,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"push_final","phase_type":"push","tcp_position_centroid":[0.10026,0.01944,0.41483]},{"body_a":"world","body_b":"door_panel","contact_count":784.0,"contact_point_centroid":[0.35332,0.06369,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.10455,0.13683,0.3834]}],"total_contact_groups":10},"final_pose_error":0.01976,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.10032,0.33025,0.35035],"hinge_angle":0.68365,"initial_hinge_angle":0.15917,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.15917,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":65.5985,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":912.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":13.19815,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1011.0,"raw_peak_contact_force":20.47065,"subtask_id":"reach_contact","tcp_end":[0.09993,0.18987,0.34849],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.40925,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":11.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":21.41129,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":11.0,"raw_peak_contact_force":21.41129,"tcp_end":[0.09987,0.18915,0.34815],"tcp_start":[0.09993,0.18987,0.34849],"tcp_to_object_dist_end":0.40861,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":3.37439,"phase_name":"push_main","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1666.0,"raw_peak_contact_force":30.72463,"subtask_id":"push_hinge","tcp_end":[0.09527,0.08276,0.4127],"tcp_start":[0.09987,0.18915,0.34815],"tcp_to_object_dist_end":0.43156,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.00036,"phase_name":"push_final","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1573.0,"raw_peak_contact_force":33.10574,"subtask_id":"push_hinge","tcp_end":[0.108,-0.04672,0.40698],"tcp_start":[0.09527,0.08276,0.4127],"tcp_to_object_dist_end":0.42365,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":936.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":786.0,"raw_peak_contact_force":65.5985,"tcp_end":[0.10032,0.33025,0.35035],"tcp_start":[0.108,-0.04672,0.40698],"tcp_to_object_dist_end":0.4918,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```