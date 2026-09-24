## Search State

- **Seed**: 8
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → contact → push → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | admittance_control | position_control | pose_tolerance | force_exceeded | time_limit | time_limit | pose_tolerance | 9 | 0.7933 | 1.00 | ❌ rejected |
| 12 | approach → contact → push → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | admittance_control | position_control | pose_tolerance | force_exceeded | time_limit | time_limit | pose_tolerance | 9 | 0.7933 | 1.00 | ❌ rejected |
| 11 | approach → contact → push → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | admittance_control | position_control | pose_tolerance | force_exceeded | time_limit | time_limit | pose_tolerance | 9 | 0.7933 | 1.00 | ❌ rejected |
| 10 | approach → contact → push → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | admittance_control | position_control | pose_tolerance | force_exceeded | time_limit | time_limit | pose_tolerance | 9 | 0.7933 | 1.00 | ❌ rejected |
| 9 | approach → contact → push → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | admittance_control | position_control | pose_tolerance | force_exceeded | time_limit | time_limit | pose_tolerance | 9 | 0.7933 | 1.00 | ❌ rejected |

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
| push_main | 1.00 | 1.00 | 0.1252 |
| push_final | 1.00 | 1.00 | 0.1015 |
| retract_1 | 1.00 | 0.33 | 0.3448 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.100, 0.399, 0.350)→(0.100, 0.190, 0.349) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 2.333 | 10.807 | 26.464 |
| contact_1 | contact | 1.00 / force_exceeded | (0.100, 0.190, 0.349)→(0.100, 0.189, 0.348) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 2.333 | 15.061 | 19.800 |
| push_main | push | 1.00 / time_limit | (0.100, 0.189, 0.348)→(0.095, 0.081, 0.412) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 3.333 | 1.272 | 29.952 |
| push_final | push | 1.00 / time_limit | (0.095, 0.081, 0.412)→(0.104, -0.019, 0.412) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 2.333 | 12.253 | 29.472 |
| retract_1 | retract | 1.00 / step_budget | (0.104, -0.019, 0.412)→(0.100, 0.321, 0.353) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.33 / 1.333 | 0.000 | 20.338 |

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
- **Final σ (mean)**: 0.390


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.27586,"average_solve_count":203.0,"average_success_count":203.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.08245,"contact_1.contact_force_threshold":9.92847,"push_final.push_final_distance":0.10019,"push_final.push_final_speed":0.04236,"push_final.push_final_time":6.29929,"push_main.push_main_distance":0.30255,"push_main.push_main_speed":0.02922,"push_main.push_main_time":10.4829,"retract_1.retract_speed":0.11236},"optimized_scores":{"best_composite_score":0.79333,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":631.0,"contact_point_centroid":[0.16444,0.09061,0.39482],"force_p95":19.85021,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":26.77321,"mean_force":12.97975,"phase_index":2.0,"phase_name":"push_main","phase_type":"push","tcp_position_centroid":[0.09908,0.14789,0.36982]},{"body_a":"door_panel","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.16453,-0.01779,0.44993],"force_p95":22.9141,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":25.46011,"mean_force":8.4867,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.09673,0.03584,0.41957]},{"body_a":"door_panel","body_b":"link7","contact_count":716.0,"contact_point_centroid":[0.16082,0.01537,0.44458],"force_p95":15.88488,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.83778,"mean_force":11.18239,"phase_index":3.0,"phase_name":"push_final","phase_type":"push","tcp_position_centroid":[0.09537,0.07238,0.41444]},{"body_a":"door_panel","body_b":"link7","contact_count":75.0,"contact_point_centroid":[0.16508,0.14398,0.37232],"force_p95":21.41794,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.22989,"mean_force":14.88285,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.09984,0.20136,0.34845]},{"body_a":"door_panel","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.16509,0.13212,0.37229],"force_p95":18.57678,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.82415,"mean_force":9.32969,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.09987,0.18953,0.34843]},{"body_a":"door_panel","body_b":"link6","contact_count":311.0,"contact_point_centroid":[0.10098,0.18528,0.4554],"force_p95":15.47992,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.71735,"mean_force":8.43786,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.09968,0.25985,0.34811]},{"body_a":"world","body_b":"door_panel","contact_count":824.0,"contact_point_centroid":[0.30073,0.18869,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.09968,0.29563,0.34805]},{"body_a":"world","body_b":"door_panel","contact_count":16.0,"contact_point_centroid":[0.30601,0.1503,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.09985,0.18947,0.34835]},{"body_a":"world","body_b":"door_panel","contact_count":932.0,"contact_point_centroid":[0.3133,0.1284,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_main","phase_type":"push","tcp_position_centroid":[0.09911,0.14712,0.37029]},{"body_a":"world","body_b":"door_panel","contact_count":912.0,"contact_point_centroid":[0.32944,0.09548,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"push_final","phase_type":"push","tcp_position_centroid":[0.09535,0.07123,0.41468]},{"body_a":"world","body_b":"door_panel","contact_count":620.0,"contact_point_centroid":[0.3366,0.08425,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.09876,0.18872,0.38475]}],"total_contact_groups":11},"final_pose_error":0.01988,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.09978,0.33022,0.35204],"hinge_angle":0.55708,"initial_hinge_angle":-0.0604,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.0604,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":26.77321,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":836.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":13.99931,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1210.0,"raw_peak_contact_force":22.22989,"subtask_id":"reach_contact","tcp_end":[0.09989,0.18978,0.34853],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.40923,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":14.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":13.58728,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":21.0,"raw_peak_contact_force":19.82415,"tcp_end":[0.09983,0.18872,0.34815],"tcp_start":[0.09989,0.18978,0.34853],"tcp_to_object_dist_end":0.4084,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":3.35772,"phase_name":"push_main","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1563.0,"raw_peak_contact_force":26.77321,"subtask_id":"push_hinge","tcp_end":[0.0971,0.10827,0.40058],"tcp_start":[0.09983,0.18872,0.34815],"tcp_to_object_dist_end":0.42616,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":11.1952,"phase_name":"push_final","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1628.0,"raw_peak_contact_force":23.83778,"subtask_id":"push_hinge","tcp_end":[0.09673,0.03579,0.41956],"tcp_start":[0.0971,0.10827,0.40058],"tcp_to_object_dist_end":0.43205,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":727.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":623.0,"raw_peak_contact_force":25.46011,"tcp_end":[0.09978,0.33022,0.35204],"tcp_start":[0.09673,0.03579,0.41956],"tcp_to_object_dist_end":0.49289,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.20392,"average_solve_count":255.0,"average_success_count":255.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.09137,"contact_1.contact_force_threshold":8.56876,"push_final.push_final_distance":0.18402,"push_final.push_final_speed":0.06636,"push_final.push_final_time":4.77535,"push_main.push_main_distance":0.26501,"push_main.push_main_speed":0.07384,"push_main.push_main_time":3.10119,"retract_1.retract_speed":0.02404},"optimized_scores":{"best_composite_score":0.79333,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":577.0,"contact_point_centroid":[0.17267,-0.02683,0.4419],"force_p95":28.75336,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":32.8539,"mean_force":13.08538,"phase_index":3.0,"phase_name":"push_final","phase_type":"push","tcp_position_centroid":[0.09979,0.01871,0.41573]},{"body_a":"door_panel","body_b":"link7","contact_count":669.0,"contact_point_centroid":[0.16357,0.07561,0.40627],"force_p95":19.77913,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":31.25978,"mean_force":13.45045,"phase_index":2.0,"phase_name":"push_main","phase_type":"push","tcp_position_centroid":[0.09825,0.13293,0.37989]},{"body_a":"door_panel","body_b":"link7","contact_count":76.0,"contact_point_centroid":[0.16509,0.14419,0.37229],"force_p95":24.27559,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":25.19946,"mean_force":15.04703,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.09986,0.20158,0.34842]},{"body_a":"door_panel","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.16509,0.13215,0.37228],"force_p95":18.9034,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.61336,"mean_force":8.62341,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.09986,0.18957,0.34842]},{"body_a":"door_panel","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.19461,-0.05833,0.42786],"force_p95":19.10575,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.15006,"mean_force":18.707,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.10743,-0.03802,0.40859]},{"body_a":"door_panel","body_b":"link6","contact_count":20.0,"contact_point_centroid":[0.10346,0.14833,0.45277],"force_p95":11.01297,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.62793,"mean_force":6.56437,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.09984,0.21443,0.34823]},{"body_a":"world","body_b":"door_panel","contact_count":960.0,"contact_point_centroid":[0.30308,0.16374,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.09972,0.2922,0.34804]},{"body_a":"world","body_b":"door_panel","contact_count":28.0,"contact_point_centroid":[0.306,0.15037,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.09985,0.18954,0.34835]},{"body_a":"world","body_b":"door_panel","contact_count":896.0,"contact_point_centroid":[0.31649,0.12163,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_main","phase_type":"push","tcp_position_centroid":[0.09823,0.13192,0.37998]},{"body_a":"world","body_b":"door_panel","contact_count":912.0,"contact_point_centroid":[0.34232,0.07712,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"push_final","phase_type":"push","tcp_position_centroid":[0.10028,0.01541,0.41537]},{"body_a":"world","body_b":"door_panel","contact_count":796.0,"contact_point_centroid":[0.35168,0.06547,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.10417,0.14402,0.38288]}],"total_contact_groups":11},"final_pose_error":0.01968,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.10019,0.33033,0.35066],"hinge_angle":0.67111,"initial_hinge_angle":0.12924,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.12924,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":32.8539,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":824.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":4.76388,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1056.0,"raw_peak_contact_force":25.19946,"subtask_id":"reach_contact","tcp_end":[0.09988,0.18984,0.34853],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.40926,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":14.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":14.88028,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":32.0,"raw_peak_contact_force":19.61336,"tcp_end":[0.09983,0.18879,0.34814],"tcp_start":[0.09988,0.18984,0.34853],"tcp_to_object_dist_end":0.40843,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_main","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1565.0,"raw_peak_contact_force":31.25978,"subtask_id":"push_hinge","tcp_end":[0.09419,0.06977,0.4171],"tcp_start":[0.09983,0.18879,0.34814],"tcp_to_object_dist_end":0.43326,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":16.50269,"phase_name":"push_final","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1489.0,"raw_peak_contact_force":32.8539,"subtask_id":"push_hinge","tcp_end":[0.10743,-0.03803,0.40859],"tcp_start":[0.09419,0.06977,0.4171],"tcp_to_object_dist_end":0.42418,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":981.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":798.0,"raw_peak_contact_force":19.15006,"tcp_end":[0.10019,0.33033,0.35066],"tcp_start":[0.10743,-0.03803,0.40859],"tcp_to_object_dist_end":0.49206,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.34855,"average_solve_count":241.0,"average_success_count":241.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.1053,"contact_1.contact_force_threshold":8.86626,"push_final.push_final_distance":0.19219,"push_final.push_final_speed":0.07323,"push_final.push_final_time":9.33066,"push_main.push_main_distance":0.349,"push_main.push_main_speed":0.07653,"push_main.push_main_time":12.30826,"retract_1.retract_speed":0.03021},"optimized_scores":{"best_composite_score":0.79333,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":51.0,"contact_point_centroid":[0.1651,0.14046,0.37246],"force_p95":25.42417,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":31.96137,"mean_force":15.6205,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.09988,0.19785,0.34856]},{"body_a":"door_panel","body_b":"link7","contact_count":657.0,"contact_point_centroid":[0.16332,0.07297,0.40812],"force_p95":20.03632,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":31.82266,"mean_force":13.50863,"phase_index":2.0,"phase_name":"push_main","phase_type":"push","tcp_position_centroid":[0.09808,0.13031,0.3815]},{"body_a":"door_panel","body_b":"link7","contact_count":601.0,"contact_point_centroid":[0.17573,-0.032,0.43977],"force_p95":28.45546,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":31.72325,"mean_force":12.21322,"phase_index":3.0,"phase_name":"push_final","phase_type":"push","tcp_position_centroid":[0.1008,0.00984,0.41479]},{"body_a":"door_panel","body_b":"link7","contact_count":7.0,"contact_point_centroid":[0.16509,0.13177,0.3723],"force_p95":19.40827,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.96159,"mean_force":11.74313,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.09986,0.18919,0.34838]},{"body_a":"door_panel","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.19892,-0.06334,0.42168],"force_p95":16.40258,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.40258,"mean_force":16.40258,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.10775,-0.05407,0.40743]},{"body_a":"world","body_b":"door_panel","contact_count":864.0,"contact_point_centroid":[0.30408,0.1586,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.09971,0.29998,0.34806]},{"body_a":"world","body_b":"door_panel","contact_count":20.0,"contact_point_centroid":[0.30602,0.15028,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.09986,0.18925,0.34837]},{"body_a":"world","body_b":"door_panel","contact_count":948.0,"contact_point_centroid":[0.31648,0.12175,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_main","phase_type":"push","tcp_position_centroid":[0.09822,0.13206,0.38004]},{"body_a":"world","body_b":"door_panel","contact_count":828.0,"contact_point_centroid":[0.34382,0.07529,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"push_final","phase_type":"push","tcp_position_centroid":[0.10099,0.00808,0.41463]},{"body_a":"world","body_b":"door_panel","contact_count":940.0,"contact_point_centroid":[0.35376,0.06322,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.10444,0.12096,0.38655]}],"total_contact_groups":10},"final_pose_error":0.04894,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.10093,0.30131,0.35491],"hinge_angle":0.68624,"initial_hinge_angle":0.15917,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.15917,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":31.96137,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":807.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":13.65925,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":915.0,"raw_peak_contact_force":31.96137,"subtask_id":"reach_contact","tcp_end":[0.0999,0.18985,0.34862],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.40934,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":17.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":16.71466,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":27.0,"raw_peak_contact_force":19.96159,"tcp_end":[0.09983,0.18846,0.34818],"tcp_start":[0.0999,0.18985,0.34862],"tcp_to_object_dist_end":0.40831,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.45781,"phase_name":"push_main","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1605.0,"raw_peak_contact_force":31.82266,"subtask_id":"push_hinge","tcp_end":[0.09377,0.06529,0.41841],"tcp_start":[0.09983,0.18846,0.34818],"tcp_to_object_dist_end":0.43374,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":9.06251,"phase_name":"push_final","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1429.0,"raw_peak_contact_force":31.72325,"subtask_id":"push_hinge","tcp_end":[0.10775,-0.05407,0.40743],"tcp_start":[0.09377,0.06529,0.41841],"tcp_to_object_dist_end":0.4249,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":941.0,"raw_peak_contact_force":16.40258,"tcp_end":[0.10093,0.30131,0.35491],"tcp_start":[0.10775,-0.05407,0.40743],"tcp_to_object_dist_end":0.47638,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```