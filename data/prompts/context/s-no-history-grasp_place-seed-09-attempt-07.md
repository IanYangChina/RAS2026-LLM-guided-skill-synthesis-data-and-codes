## Search State

- **Seed**: 9
- **Iteration**: 8 / 15

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

- Task name: grasp_place
- Frozen realised-scene SHA-256: `0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8`
- Frozen object start: [0.5370249203970084, -0.021318279091244466, 0.03]
- Frozen task target: [0.6103148150051562, 0.2277534082920179, 0.2074111944405348]
- Goal object position: (0.6103148150051562, 0.2277534082920179, 0.2074111944405348)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.6103148150051562, 0.2277534082920179, 0.2074111944405348)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5370249203970084, -0.021318279091244466, 0.03)
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 20.0 N
- Robot initial TCP position: (0.5, 0.0, 0.3)
- Robot initial gripper state: **open** (gripper starts fully open; ensure a `grasp`/`force_grasp` phase closes it before lifting)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **final object-to-realised-airborne-3D-target proximity. Grasp/lift signals are optimiser fitness diagnostics only; they do not gate the canonical task_score.**

## Scene Entities

robot:
  model: panda_full
  tcp_site: attachment_site
  gripper: franka_hand
  tcp_initial_world: [0.5, 0, 0.3]
objects:
  - name: grasp_target
    role: manipulated_object
    dynamics: free
    geometry: box
    dimensions_m: [0.04, 0.04, 0.06]
    mass_kg: 0.05
  - name: placement_surface
    role: goal_area
    dynamics: static
    geometry: point
task_landmarks:
  frozen_object_start: [0.537, -0.0213, 0.03]
  frozen_task_target: [0.6103, 0.2278, 0.2074]
  frozen_object_starts: {'grasp_target': [0.5370249203970084, -0.021318279091244466, 0.03]}
  frozen_targets: {'place_target': [0.6103148150051562, 0.2277534082920179, 0.2074111944405348]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8

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
| `object` | offset from object initial position (0.5370249203970084, -0.021318279091244466, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.6103148150051562, 0.2277534082920179, 0.2074111944405348) | final destination targets |
| `fixture` | offset from fixture pose (if defined, else world) | targets near fixture |

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

## Current Skill (Q=0.354) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.3
- id: lift_clearance
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.2
- id: reach_goal
  weight: 0.5
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.015
    orientation:
      mode: keep_current
  parameters:
    approach_z:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: reach_object
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.02
    tolerance: 0.015
    orientation:
      mode: keep_current
  parameters:
    descend_z:
      type: scalar
      range:
      - 0.0
      - 0.05
      default: 0.02
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
- id: grasp_1
  type: grasp
  control: position_control
  termination: grasp_success
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
  guards:
  - id: grasp_check
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.5
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.005
    - 0.0
    - 0.0
- id: lift_1
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.12
    tolerance: 0.015
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.08
      - 0.2
      default: 0.12
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: lift_clearance
- id: approach_goal
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    goal_approach_z:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.3
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: reach_goal
- id: descend_goal
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.03
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    goal_z_offset:
      type: scalar
      range:
      - 0.0
      - 0.06
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: grasp_held
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.5
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: reduce_speed
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: reach_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.1], tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_z: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.02], tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_z: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none
  - guards:
    - id=grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.5
  - retries: max_attempts=1, strategy=offset_target, offset=[0.005, 0.0, 0.0]
- **lift_1** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.12], tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat
- **approach_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - goal_approach_z: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat
- **descend_goal** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.03], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - goal_z_offset: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=grasp_held, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.5
  - retries: max_attempts=1, strategy=reduce_speed, offset=[0.0, 0.0, 0.0]

## Design Metrics

- **Composite score**: 0.354
- **task_score** (E): 1.000
- **fitness_score**: 0.974  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.620

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1423 |
| descend_1 | 1.00 | 1.00 | 0.1198 |
| grasp_1 | 1.00 | 1.00 | 0.0126 |
| lift_1 | 1.00 | 1.00 | 0.1289 |
| approach_goal | 1.00 | 1.00 | 0.2378 |
| descend_goal | 1.00 | 1.00 | 0.0422 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, -0.015, 0.164) | (0.515, -0.017, 0.030)→(0.515, -0.017, 0.026) | 0.268→0.270 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.510, -0.015, 0.164)→(0.510, -0.016, 0.044) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.510, -0.016, 0.044)→(0.502, -0.016, 0.035) | (0.515, -0.017, 0.026)→(0.515, -0.016, 0.026) | 0.270→0.270 | 1.00 / 42.000 | 0.136 | 0.177 |
| lift_1 | lift | 1.00 / step_budget | (0.502, -0.016, 0.035)→(0.498, -0.016, 0.164) | (0.515, -0.016, 0.026)→(0.507, -0.016, 0.149) | 0.270→0.235 | 1.00 / 38.000 | 0.077 | 0.487 |
| approach_goal | approach | 1.00 / step_budget | (0.498, -0.016, 0.164)→(0.609, 0.171, 0.247) | (0.507, -0.016, 0.149)→(0.614, 0.171, 0.220) | 0.235→0.053 | 1.00 / 29.000 | 0.105 | 0.186 |
| descend_goal | descend | 1.00 / step_budget | (0.609, 0.171, 0.247)→(0.612, 0.176, 0.206) | (0.614, 0.171, 0.220)→(0.615, 0.176, 0.177) | 0.053→0.012 | 1.00 / 28.667 | 0.113 | 0.238 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.436
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 1.000
- phase_score: 0.529
- phase_breakdown.reach_goal_score: 0.541
- phase_breakdown.lift_clearance_score: 0.549
- phase_breakdown.reach_object_score: 0.497
- grasp_place_fitness: 0.979

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.979
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.353
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.360


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `425c48e82220fc6e1b680086671cf7dd2586733ee271dec2149f96a25d69d0c6`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `58e88c03db0a62276863b22a53636bc89fead3e4bc7f4d35fd72d2282ace32bf`; realized-scene SHA-256: `0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53702,-0.02132,0.03]},{"name":"goal","value":[0.61031,0.22775,0.20741]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.53702,-0.02132,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.61031,0.22775,0.20741]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.95833,"average_solve_count":240.0,"average_success_count":240.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_z":0.1283,"approach_1.speed":0.02383,"approach_goal.goal_approach_z":0.06131,"approach_goal.speed":0.25741,"descend_1.descend_z":0.00717,"descend_1.speed":0.10331,"descend_goal.goal_z_offset":0.03133,"descend_goal.speed":0.09743,"lift_1.lift_height":0.13526,"lift_1.speed":0.05859},"optimized_scores":{"best_composite_score":0.35188,"best_fitness_score":0.97188,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":113.0,"contact_point_centroid":[0.53411,-0.02031,-0.00129],"force_p95":0.41859,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.51226,"mean_force":0.08975,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52145,-0.02066,0.03821]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12187.0,"contact_point_centroid":[0.51982,-0.0015,0.09999],"force_p95":0.08074,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31006,"mean_force":0.05706,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5187,-0.0206,0.09763]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12862.0,"contact_point_centroid":[0.51984,-0.03964,0.0979],"force_p95":0.07904,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29621,"mean_force":0.05482,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51872,-0.0206,0.09588]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":220.0,"contact_point_centroid":[0.60965,0.19763,0.25347],"force_p95":0.13098,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2767,"mean_force":0.09352,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.60353,0.21611,0.25363]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":233.0,"contact_point_centroid":[0.60932,0.23475,0.25331],"force_p95":0.12957,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27318,"mean_force":0.0894,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.60353,0.21609,0.25367]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8814.0,"contact_point_centroid":[0.56251,0.07438,0.20338],"force_p95":0.1152,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22436,"mean_force":0.07667,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55832,0.09315,0.20246]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9683.0,"contact_point_centroid":[0.56308,0.11405,0.20407],"force_p95":0.10347,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19856,"mean_force":0.0723,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5591,0.09536,0.20335]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53704,-0.02117,-0.00206],"force_p95":0.14041,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18233,"mean_force":0.12749,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52405,-0.02071,0.0382]},{"body_a":"world","body_b":"grasp_target","contact_count":1444.0,"contact_point_centroid":[0.53702,-0.02132,-0.00191],"force_p95":0.13511,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12296,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51286,-0.00887,0.23618]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4101.0,"contact_point_centroid":[0.52374,-0.00148,0.03954],"force_p95":0.0777,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12919,"mean_force":0.05185,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52284,-0.02069,0.03682]},{"body_a":"world","body_b":"grasp_target","contact_count":1136.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52899,-0.01965,0.10859]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4913.0,"contact_point_centroid":[0.52373,-0.03978,0.03862],"force_p95":0.06981,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08127,"mean_force":0.04468,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52284,-0.02069,0.03682]}],"total_contact_groups":12},"final_pose_error":0.01723,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.61301,0.21856,0.22041],"final_tcp_position":[0.60407,0.21728,0.2509],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":0.51226,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":362.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1444.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.52881,-0.01854,0.1702],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14444,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":284.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1136.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53147,-0.02083,0.04695],"tcp_start":[0.52881,-0.01854,0.1702],"tcp_to_object_dist_end":0.02166,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53692,-0.02066,0.02578],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31636,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13704,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10814.0,"raw_peak_contact_force":0.18233,"tcp_end":[0.52281,-0.02068,0.03679],"tcp_start":[0.53147,-0.02083,0.04695],"tcp_to_object_dist_end":0.0179,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":677.0,"n_steps_budget":1000.0,"object_pos_end":[0.52824,-0.02058,0.14014],"object_pos_start":[0.53692,-0.02066,0.02578],"object_to_goal_dist_end":0.27006,"object_to_goal_dist_start":0.31636,"object_z_max":0.13999,"peak_contact_force":0.07987,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":25162.0,"raw_peak_contact_force":0.51226,"subtask_id":"lift_clearance","tcp_end":[0.51892,-0.02059,0.15759],"tcp_start":[0.52281,-0.02068,0.03679],"tcp_to_object_dist_end":0.01978,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":692.0,"n_steps_budget":1000.0,"object_pos_end":[0.611,0.21588,0.22446],"object_pos_start":[0.52824,-0.02058,0.14014],"object_to_goal_dist_end":0.02079,"object_to_goal_dist_start":0.27006,"object_z_max":0.22439,"peak_contact_force":0.1234,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":18497.0,"raw_peak_contact_force":0.22436,"subtask_id":"reach_goal","tcp_end":[0.60359,0.21518,0.25495],"tcp_start":[0.51892,-0.02059,0.15759],"tcp_to_object_dist_end":0.03139,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":20.0,"n_steps_budget":1000.0,"object_pos_end":[0.61301,0.21856,0.22041],"object_pos_start":[0.611,0.21588,0.22446],"object_to_goal_dist_end":0.01615,"object_to_goal_dist_start":0.02079,"object_z_max":0.22446,"peak_contact_force":0.12472,"phase_name":"descend_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":453.0,"raw_peak_contact_force":0.2767,"subtask_id":"reach_goal","tcp_end":[0.60407,0.21728,0.2509],"tcp_start":[0.60359,0.21518,0.25495],"tcp_to_object_dist_end":0.0318,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1e57d18e69439f9d4839513252d085a45363faa5c1c2b52093c9c8149b88bb68`; realized-scene SHA-256: `9bdc6de22965641ffcaccb8421100561fe91fb98e16735236cc25272572d8879`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5456,-0.02923,0.03]},{"name":"goal","value":[0.63284,0.16493,0.17692]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5456,-0.02923,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63284,0.16493,0.17692]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.16863,"average_solve_count":255.0,"average_success_count":255.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_z":0.11483,"approach_1.speed":0.09216,"approach_goal.goal_approach_z":0.12147,"approach_goal.speed":0.1767,"descend_1.descend_z":0.0059,"descend_1.speed":0.05382,"descend_goal.goal_z_offset":0.01841,"descend_goal.speed":0.13667,"lift_1.lift_height":0.15843,"lift_1.speed":0.01235},"optimized_scores":{"best_composite_score":0.35278,"best_fitness_score":0.97278,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":134.0,"contact_point_centroid":[0.54104,-0.02769,-0.00143],"force_p95":0.38812,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.43624,"mean_force":0.1402,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52934,-0.02824,0.03591]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1388.0,"contact_point_centroid":[0.63144,0.17543,0.25054],"force_p95":0.16003,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2618,"mean_force":0.0959,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.6263,0.15735,0.25175]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1254.0,"contact_point_centroid":[0.63172,0.13864,0.25138],"force_p95":0.16508,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25843,"mean_force":0.10184,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.62629,0.15731,0.25226]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16105.0,"contact_point_centroid":[0.5276,-0.00905,0.10976],"force_p95":0.08079,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24505,"mean_force":0.05588,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52668,-0.02815,0.1074]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16873.0,"contact_point_centroid":[0.52759,-0.0472,0.10663],"force_p95":0.07823,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24078,"mean_force":0.05412,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52669,-0.02815,0.10454]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8008.0,"contact_point_centroid":[0.57692,0.03957,0.22777],"force_p95":0.11794,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21109,"mean_force":0.0807,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.57217,0.05837,0.2263]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54563,-0.02904,-0.00208],"force_p95":0.14774,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20778,"mean_force":0.12934,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53209,-0.02833,0.03632]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9180.0,"contact_point_centroid":[0.57807,0.07936,0.22852],"force_p95":0.10246,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20726,"mean_force":0.07141,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.57343,0.06073,0.22765]},{"body_a":"world","body_b":"grasp_target","contact_count":1480.0,"contact_point_centroid":[0.5456,-0.02923,-0.00191],"force_p95":0.13511,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12296,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51719,-0.01253,0.22855]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4090.0,"contact_point_centroid":[0.53196,-0.00908,0.03759],"force_p95":0.0789,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13431,"mean_force":0.05185,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53086,-0.02829,0.03489]},{"body_a":"world","body_b":"grasp_target","contact_count":1092.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53693,-0.0271,0.10104]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4944.0,"contact_point_centroid":[0.53192,-0.0474,0.03666],"force_p95":0.07112,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08178,"mean_force":0.04467,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53087,-0.02829,0.03489]}],"total_contact_groups":12},"final_pose_error":0.02,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.62994,0.16083,0.18194],"final_tcp_position":[0.62797,0.16086,0.21429],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":0.43624,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":371.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1480.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.53685,-0.02579,0.15636],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13068,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":273.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1092.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53958,-0.02854,0.04528],"tcp_start":[0.53685,-0.02579,0.15636],"tcp_to_object_dist_end":0.02019,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5455,-0.02832,0.0257],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26046,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.14286,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10834.0,"raw_peak_contact_force":0.20778,"tcp_end":[0.53083,-0.02829,0.03485],"tcp_start":[0.53958,-0.02854,0.04528],"tcp_to_object_dist_end":0.01729,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":890.0,"n_steps_budget":1000.0,"object_pos_end":[0.53534,-0.02814,0.16234],"object_pos_start":[0.5455,-0.02832,0.0257],"object_to_goal_dist_end":0.21678,"object_to_goal_dist_start":0.26046,"object_z_max":0.16219,"peak_contact_force":0.07976,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":33112.0,"raw_peak_contact_force":0.43624,"subtask_id":"lift_clearance","tcp_end":[0.52708,-0.02816,0.17891],"tcp_start":[0.53083,-0.02829,0.03485],"tcp_to_object_dist_end":0.01851,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":666.0,"n_steps_budget":1000.0,"object_pos_end":[0.63115,0.15454,0.25306],"object_pos_start":[0.53534,-0.02814,0.16234],"object_to_goal_dist_end":0.07686,"object_to_goal_dist_start":0.21678,"object_z_max":0.25297,"peak_contact_force":0.11918,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":17188.0,"raw_peak_contact_force":0.21109,"subtask_id":"reach_goal","tcp_end":[0.62523,0.15419,0.28361],"tcp_start":[0.52708,-0.02816,0.17891],"tcp_to_object_dist_end":0.03112,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":21.0,"n_steps":123.0,"n_steps_budget":1000.0,"object_pos_end":[0.62994,0.16083,0.18194],"object_pos_start":[0.63115,0.15454,0.25306],"object_to_goal_dist_end":0.0071,"object_to_goal_dist_start":0.07686,"object_z_max":0.25306,"peak_contact_force":0.14449,"phase_name":"descend_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2642.0,"raw_peak_contact_force":0.2618,"subtask_id":"reach_goal","tcp_end":[0.62797,0.16086,0.21429],"tcp_start":[0.62523,0.15419,0.28361],"tcp_to_object_dist_end":0.03241,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `5836f8a66456087ed82e2e1accc6472c2a7681a19bf8e3d54637158aadaafc47`; realized-scene SHA-256: `776f3cbcac69f75f44cb26f0b1a492bbf1ced59f3c5fca79400c3f557c2ce565`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.46286,-7e-05,0.03]},{"name":"goal","value":[0.61015,0.15287,0.12219]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.46286,-7e-05,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.61015,0.15287,0.12219]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.62032,"average_solve_count":187.0,"average_success_count":187.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_z":0.12007,"approach_1.speed":0.11874,"approach_goal.goal_approach_z":0.09243,"approach_goal.speed":0.19809,"descend_1.descend_z":1e-05,"descend_1.speed":0.07959,"descend_goal.goal_z_offset":0.01201,"descend_goal.speed":0.19659,"lift_1.lift_height":0.1361,"lift_1.speed":0.0357},"optimized_scores":{"best_composite_score":0.35878,"best_fitness_score":0.97878,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":99.0,"contact_point_centroid":[0.45829,-0.00021,-0.00133],"force_p95":0.48764,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.51146,"mean_force":0.16888,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45016,-0.00023,0.03365]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11882.0,"contact_point_centroid":[0.44777,0.01891,0.09477],"force_p95":0.07297,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27493,"mean_force":0.05135,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44757,-0.00024,0.09289]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11916.0,"contact_point_centroid":[0.4478,-0.01938,0.0946],"force_p95":0.07367,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24649,"mean_force":0.05127,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44758,-0.00024,0.09271]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2163.0,"contact_point_centroid":[0.59945,0.16476,0.18138],"force_p95":0.08642,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17605,"mean_force":0.05219,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.59959,0.14558,0.17903]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2077.0,"contact_point_centroid":[0.59903,0.12636,0.18171],"force_p95":0.08707,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15797,"mean_force":0.05276,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.59958,0.14557,0.17917]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.46284,-4e-05,-0.00201],"force_p95":0.12814,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14077,"mean_force":0.12431,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.45233,-0.0002,0.03363]},{"body_a":"world","body_b":"grasp_target","contact_count":1244.0,"contact_point_centroid":[0.46286,-7e-05,-0.00189],"force_p95":0.13606,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12302,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48228,-5e-05,0.23365]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11452.0,"contact_point_centroid":[0.52387,0.05435,0.18017],"force_p95":0.07384,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12305,"mean_force":0.0499,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52374,0.07351,0.17812]},{"body_a":"world","body_b":"grasp_target","contact_count":1224.0,"contact_point_centroid":[0.46286,-7e-05,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.46085,-0.0001,0.10275]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11588.0,"contact_point_centroid":[0.52355,0.09226,0.17997],"force_p95":0.07382,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11349,"mean_force":0.04955,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52334,0.07313,0.17799]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4389.0,"contact_point_centroid":[0.4512,0.01909,0.03484],"force_p95":0.07393,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09412,"mean_force":0.04934,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.45126,-0.00021,0.03261]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5332.0,"contact_point_centroid":[0.45072,-0.01929,0.03434],"force_p95":0.06278,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08673,"mean_force":0.04089,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.45126,-0.00021,0.03261]}],"total_contact_groups":12},"final_pose_error":0.01948,"key_states":{"actual_goal_position":[0.61015,0.15287,0.12219],"final_object_position":[0.60333,0.14859,0.13008],"final_tcp_position":[0.60261,0.14854,0.15164],"realised_goal_position":[0.61015,0.15287,0.12219],"realised_object_initial_position":[0.46286,-7e-05,0.03]},"peak_contact_force":0.51146,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":312.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.03],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.23148,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1244.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.4646,-8e-05,0.16494],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13893,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":306.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1224.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.459,-0.00012,0.04018],"tcp_start":[0.4646,-8e-05,0.16494],"tcp_to_object_dist_end":0.01468,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46274,-1e-05,0.02592],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.23317,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12824,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11521.0,"raw_peak_contact_force":0.14077,"tcp_end":[0.45123,-0.00021,0.03258],"tcp_start":[0.459,-0.00012,0.04018],"tcp_to_object_dist_end":0.0133,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":595.0,"n_steps_budget":1000.0,"object_pos_end":[0.45651,-0.00023,0.14399],"object_pos_start":[0.46274,-1e-05,0.02592],"object_to_goal_dist_end":0.21799,"object_to_goal_dist_start":0.23317,"object_z_max":0.1438,"peak_contact_force":0.07217,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":23897.0,"raw_peak_contact_force":0.51146,"subtask_id":"lift_clearance","tcp_end":[0.44762,-0.00023,0.15415],"tcp_start":[0.45123,-0.00021,0.03258],"tcp_to_object_dist_end":0.0135,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":569.0,"n_steps_budget":1000.0,"object_pos_end":[0.59836,0.14295,0.18241],"object_pos_start":[0.45651,-0.00023,0.14399],"object_to_goal_dist_end":0.06216,"object_to_goal_dist_start":0.21799,"object_z_max":0.18236,"peak_contact_force":0.07377,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":23040.0,"raw_peak_contact_force":0.12305,"subtask_id":"reach_goal","tcp_end":[0.59722,0.14278,0.20324],"tcp_start":[0.44762,-0.00023,0.15415],"tcp_to_object_dist_end":0.02086,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":99.0,"n_steps_budget":1000.0,"object_pos_end":[0.60333,0.14859,0.13008],"object_pos_start":[0.59836,0.14295,0.18241],"object_to_goal_dist_end":0.01127,"object_to_goal_dist_start":0.06216,"object_z_max":0.18241,"peak_contact_force":0.07124,"phase_name":"descend_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4240.0,"raw_peak_contact_force":0.17605,"subtask_id":"reach_goal","tcp_end":[0.60261,0.14854,0.15164],"tcp_start":[0.59722,0.14278,0.20324],"tcp_to_object_dist_end":0.02157,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```