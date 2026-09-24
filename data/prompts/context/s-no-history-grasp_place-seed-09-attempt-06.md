## Search State

- **Seed**: 9
- **Iteration**: 7 / 15

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

## Current Skill (Q=0.027) — your mutation base

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
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_z:
      type: scalar
      range:
      - 0.0
      - 0.04
      default: 0.02
      binds_to:
      - path: target.offset.z
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
    tolerance: 0.015
    orientation:
      mode: keep_current
  parameters:
    goal_approach_z:
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
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    place_z_offset:
      type: scalar
      range:
      - -0.04
      - 0.02
      default: -0.01
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
  subtask_id: reach_goal
- id: release_1
  type: release
  control: position_control
  termination: time_limit
  end_effector_action: open
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
  retries:
    max_attempts: 0
    strategy: repeat
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.015
    orientation:
      mode: keep_current
  parameters:
    retract_z:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat

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
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.02], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_z: status=consumed; consumers=target.offset.z (replace)
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
  - retries: max_attempts=0, strategy=repeat
- **approach_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - goal_approach_z: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat
- **descend_goal** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_z_offset: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none
  - retries: max_attempts=0, strategy=repeat
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1], tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_z: status=consumed; consumers=target.offset.z (replace)
  - retries: max_attempts=0, strategy=repeat

## Design Metrics

- **Composite score**: 0.027
- **task_score** (E): 0.363
- **fitness_score**: 0.657  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.630

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1396 |
| descend_1 | 1.00 | 1.00 | 0.1239 |
| grasp_1 | 1.00 | 1.00 | 0.0123 |
| lift_1 | 1.00 | 1.00 | 0.0980 |
| approach_goal | 0.33 | 1.00 | 0.2018 |
| descend_goal | 1.00 | 1.00 | 0.0863 |
| release_1 | 1.00 | 1.00 | 0.0208 |
| retract_1 | 1.00 | 1.00 | 0.1252 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, -0.015, 0.167) | (0.515, -0.017, 0.030)→(0.515, -0.017, 0.026) | 0.268→0.270 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.510, -0.015, 0.167)→(0.510, -0.017, 0.043) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.510, -0.017, 0.043)→(0.502, -0.016, 0.034) | (0.515, -0.017, 0.026)→(0.515, -0.016, 0.026) | 0.270→0.270 | 1.00 / 41.667 | 0.134 | 0.170 |
| lift_1 | lift | 1.00 / step_budget | (0.502, -0.016, 0.034)→(0.498, -0.016, 0.132) | (0.515, -0.016, 0.026)→(0.514, -0.016, 0.117) | 0.270→0.237 | 1.00 / 23.667 | 0.072 | 0.564 |
| approach_goal | approach | 0.33 / step_budget | (0.498, -0.016, 0.132)→(0.594, 0.135, 0.209) | (0.514, -0.016, 0.117)→(0.600, 0.135, 0.181) | 0.237→0.060 | 1.00 / 14.667 | 5.483 | 0.204 |
| descend_goal | descend | 1.00 / step_budget | (0.594, 0.135, 0.209)→(0.612, 0.178, 0.146) | (0.600, 0.135, 0.181)→(0.611, 0.145, 0.033) | 0.060→0.142 | 1.00 / 14.667 | 91001.630 | 1.296 |
| release_1 | release | 1.00 / step_budget | (0.612, 0.178, 0.146)→(0.605, 0.176, 0.166) | (0.611, 0.145, 0.033)→(0.605, 0.137, 0.019) | 0.142→0.158 | 1.00 / 4.000 | 0.146 | 0.359 |
| retract_1 | retract | 1.00 / step_budget | (0.605, 0.176, 0.166)→(0.603, 0.175, 0.291) | (0.605, 0.137, 0.019)→(0.604, 0.137, 0.019) | 0.158→0.158 | 1.00 / 4.000 | 0.123 | 0.147 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.501
- phase_score: 0.543
- phase_breakdown.reach_goal_score: 0.578
- phase_breakdown.lift_clearance_score: 0.446
- phase_breakdown.reach_object_score: 0.551
- grasp_place_fitness: 0.730

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.730
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.501
- **Median Q (composite search score)**: 0.011
- **K-run variance**: 0.0030
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.242


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.66364,"average_solve_count":220.0,"average_success_count":220.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_z":0.13611,"approach_1.speed":0.05223,"approach_goal.goal_approach_z":0.10019,"approach_goal.speed":0.07122,"descend_1.descend_z":0.01165,"descend_goal.place_z_offset":-0.01546,"descend_goal.speed":0.11824,"lift_1.lift_height":0.10501,"retract_1.retract_z":0.14259},"optimized_scores":{"best_composite_score":-0.03132,"best_fitness_score":0.59868,"best_task_score":0.25186},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2249.0,"contact_point_centroid":[0.59716,0.15042,-0.00252],"force_p95":0.15732,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.85843,"mean_force":0.14417,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.5937,0.19358,0.1987]},{"body_a":"world","body_b":"grasp_target","contact_count":98.0,"contact_point_centroid":[0.53389,-0.02046,-0.00125],"force_p95":0.40611,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.53147,"mean_force":0.09131,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52167,-0.02075,0.03761]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6756.0,"contact_point_centroid":[0.52135,-0.00174,0.07905],"force_p95":0.10698,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32783,"mean_force":0.06897,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51886,-0.02069,0.07684]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":383.0,"contact_point_centroid":[0.57991,0.12317,0.22509],"force_p95":0.16324,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30822,"mean_force":0.09759,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.57466,0.14017,0.22961]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":216.0,"contact_point_centroid":[0.58023,0.15712,0.22631],"force_p95":0.22375,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30646,"mean_force":0.17272,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.57445,0.13914,0.23066]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7337.0,"contact_point_centroid":[0.52146,-0.03951,0.07703],"force_p95":0.10292,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30033,"mean_force":0.06472,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5189,-0.02069,0.07553]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11023.0,"contact_point_centroid":[0.54749,0.07123,0.17442],"force_p95":0.14708,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18112,"mean_force":0.08363,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.54246,0.05273,0.1742]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53703,-0.02117,-0.00205],"force_p95":0.13812,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17134,"mean_force":0.12686,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52422,-0.0208,0.03749]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11623.0,"contact_point_centroid":[0.54846,0.03717,0.17634],"force_p95":0.12009,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15583,"mean_force":0.07988,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.54353,0.05559,0.17625]},{"body_a":"world","body_b":"grasp_target","contact_count":1320.0,"contact_point_centroid":[0.53702,-0.02132,-0.0019],"force_p95":0.13564,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.123,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51296,-0.00885,0.23969]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4105.0,"contact_point_centroid":[0.52384,-0.00157,0.03883],"force_p95":0.07737,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12608,"mean_force":0.05181,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.523,-0.02078,0.0361]},{"body_a":"world","body_b":"grasp_target","contact_count":1616.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52867,-0.01961,0.11122]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.59721,0.15044,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60155,0.22186,0.18467]},{"body_a":"world","body_b":"grasp_target","contact_count":3128.0,"contact_point_centroid":[0.59721,0.15044,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.59776,0.22018,0.26736]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4903.0,"contact_point_centroid":[0.52385,-0.03986,0.0379],"force_p95":0.06946,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09016,"mean_force":0.04472,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.523,-0.02078,0.0361]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2145.0,"contact_point_centroid":[0.59552,0.197,0.19928],"force_p95":0.01147,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01638,"mean_force":0.01065,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.59505,0.19699,0.19705]}],"total_contact_groups":17},"final_pose_error":0.01537,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.59721,0.15044,0.01602],"final_tcp_position":[0.59846,0.22037,0.33135],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":273004.63035,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":331.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1320.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.52859,-0.01838,0.17808],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15232,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":404.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1616.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53147,-0.02093,0.04596],"tcp_start":[0.52859,-0.01838,0.17808],"tcp_to_object_dist_end":0.0207,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53692,-0.02072,0.02581],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31639,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13512,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10808.0,"raw_peak_contact_force":0.17134,"tcp_end":[0.52297,-0.02077,0.03606],"tcp_start":[0.53147,-0.02093,0.04596],"tcp_to_object_dist_end":0.01731,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":452.0,"n_steps_budget":690.0,"object_pos_end":[0.53413,-0.02068,0.11037],"object_pos_start":[0.53692,-0.02072,0.02581],"object_to_goal_dist_end":0.27738,"object_to_goal_dist_start":0.31639,"object_z_max":0.11022,"peak_contact_force":0.1066,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":14191.0,"raw_peak_contact_force":0.53147,"subtask_id":"lift_clearance","tcp_end":[0.51878,-0.02068,0.12667],"tcp_start":[0.52297,-0.02077,0.03606],"tcp_to_object_dist_end":0.02239,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":14.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.57872,0.13627,0.20646],"object_pos_start":[0.53413,-0.02068,0.11037],"object_to_goal_dist_end":0.09679,"object_to_goal_dist_start":0.27738,"object_z_max":0.20638,"peak_contact_force":0.15386,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":22646.0,"raw_peak_contact_force":0.18112,"subtask_id":"reach_goal","tcp_end":[0.57368,0.13598,0.23377],"tcp_start":[0.51878,-0.02068,0.12667],"tcp_to_object_dist_end":0.02777,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":693.0,"n_steps_budget":1000.0,"object_pos_end":[0.59721,0.15044,0.01602],"object_pos_start":[0.57872,0.13627,0.20646],"object_to_goal_dist_end":0.20683,"object_to_goal_dist_start":0.09679,"object_z_max":0.20646,"peak_contact_force":273004.63035,"phase_name":"descend_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4993.0,"raw_peak_contact_force":1.85843,"subtask_id":"reach_goal","tcp_end":[0.60542,0.22335,0.18444],"tcp_start":[0.57368,0.13598,0.23377],"tcp_to_object_dist_end":0.18371,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59721,0.15044,0.01602],"object_pos_start":[0.59721,0.15044,0.01602],"object_to_goal_dist_end":0.20683,"object_to_goal_dist_start":0.20683,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1026.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.60009,0.22121,0.20401],"tcp_start":[0.60542,0.22335,0.18444],"tcp_to_object_dist_end":0.20089,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":782.0,"n_steps_budget":900.0,"object_pos_end":[0.59721,0.15044,0.01602],"object_pos_start":[0.59721,0.15044,0.01602],"object_to_goal_dist_end":0.20683,"object_to_goal_dist_start":0.20683,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3128.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.59846,0.22037,0.33135],"tcp_start":[0.60009,0.22121,0.20401],"tcp_to_object_dist_end":0.32299,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.89394,"average_solve_count":198.0,"average_success_count":198.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_z":0.12098,"approach_1.speed":0.07169,"approach_goal.goal_approach_z":0.0665,"approach_goal.speed":0.07561,"descend_1.descend_z":0.01026,"descend_goal.place_z_offset":-0.01501,"descend_goal.speed":0.14404,"lift_1.lift_height":0.10588,"retract_1.retract_z":0.12048},"optimized_scores":{"best_composite_score":0.01144,"best_fitness_score":0.64144,"best_task_score":0.33527},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":698.0,"contact_point_centroid":[0.63286,0.13271,-0.00356],"force_p95":0.97107,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.75876,"mean_force":0.2074,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.61914,0.1478,0.17258]},{"body_a":"world","body_b":"grasp_target","contact_count":102.0,"contact_point_centroid":[0.54215,-0.02787,-0.00124],"force_p95":0.42939,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5611,"mean_force":0.09044,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52979,-0.02838,0.03574]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6728.0,"contact_point_centroid":[0.52976,-0.00938,0.07711],"force_p95":0.10831,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3294,"mean_force":0.07093,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52698,-0.02828,0.07491]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7318.0,"contact_point_centroid":[0.52984,-0.04708,0.07535],"force_p95":0.10408,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30848,"mean_force":0.06652,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52701,-0.02828,0.07384]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10499.0,"contact_point_centroid":[0.56788,0.06205,0.16226],"force_p95":0.12926,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22841,"mean_force":0.08699,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.56289,0.04365,0.16309]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":78.0,"contact_point_centroid":[0.61311,0.10958,0.20391],"force_p95":0.13778,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20505,"mean_force":0.03474,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.60754,0.12425,0.20953]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54562,-0.02904,-0.00207],"force_p95":0.14439,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19744,"mean_force":0.12852,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53241,-0.02846,0.03558]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10876.0,"contact_point_centroid":[0.5684,0.02668,0.16298],"force_p95":0.12402,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15941,"mean_force":0.08383,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.56368,0.04507,0.16394]},{"body_a":"world","body_b":"grasp_target","contact_count":1464.0,"contact_point_centroid":[0.5456,-0.02923,-0.00191],"force_p95":0.13511,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12296,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51698,-0.01249,0.23137]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4093.0,"contact_point_centroid":[0.53217,-0.00922,0.03686],"force_p95":0.07841,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12972,"mean_force":0.05184,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53118,-0.02843,0.03413]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.6329,0.1336,-0.00199],"force_p95":0.12265,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12272,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62114,0.15758,0.15922]},{"body_a":"world","body_b":"grasp_target","contact_count":1436.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53688,-0.02714,0.1025]},{"body_a":"world","body_b":"grasp_target","contact_count":2640.0,"contact_point_centroid":[0.6329,0.1336,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.6166,0.15621,0.23099]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4932.0,"contact_point_centroid":[0.53214,-0.04753,0.03591],"force_p95":0.07053,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08127,"mean_force":0.0447,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53118,-0.02843,0.03414]},{"body_a":"left_finger","body_b":"right_finger","contact_count":571.0,"contact_point_centroid":[0.62117,0.15059,0.17136],"force_p95":0.0137,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01511,"mean_force":0.01077,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.62077,0.15058,0.16904]},{"body_a":"left_finger","body_b":"right_finger","contact_count":223.0,"contact_point_centroid":[0.62451,0.15849,0.15829],"force_p95":0.01095,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01097,"mean_force":0.01001,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62399,0.15848,0.15582]}],"total_contact_groups":16},"final_pose_error":0.01536,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.6329,0.1336,0.01602],"final_tcp_position":[0.61706,0.15629,0.28391],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":16.19529,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":367.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1464.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.53671,-0.02571,0.16219],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1365,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":359.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1436.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53977,-0.02868,0.04431],"tcp_start":[0.53671,-0.02571,0.16219],"tcp_to_object_dist_end":0.0192,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5455,-0.02841,0.02574],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26051,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.14008,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10825.0,"raw_peak_contact_force":0.19744,"tcp_end":[0.53115,-0.02842,0.0341],"tcp_start":[0.53977,-0.02868,0.04431],"tcp_to_object_dist_end":0.01661,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":465.0,"n_steps_budget":690.0,"object_pos_end":[0.54266,-0.02825,0.11054],"object_pos_start":[0.5455,-0.02841,0.02574],"object_to_goal_dist_end":0.22329,"object_to_goal_dist_start":0.26051,"object_z_max":0.1104,"peak_contact_force":0.0,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":14148.0,"raw_peak_contact_force":0.5611,"subtask_id":"lift_clearance","tcp_end":[0.52691,-0.02827,0.12561],"tcp_start":[0.53115,-0.02842,0.0341],"tcp_to_object_dist_end":0.0218,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.61351,0.1224,0.18085],"object_pos_start":[0.54266,-0.02825,0.11054],"object_to_goal_dist_end":0.04688,"object_to_goal_dist_start":0.22329,"object_z_max":0.18235,"peak_contact_force":16.19529,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":21375.0,"raw_peak_contact_force":0.22841,"subtask_id":"reach_goal","tcp_end":[0.60716,0.12357,0.2104],"tcp_start":[0.52691,-0.02827,0.12561],"tcp_to_object_dist_end":0.03025,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":274.0,"n_steps_budget":1000.0,"object_pos_end":[0.6329,0.13359,0.01602],"object_pos_start":[0.61351,0.1224,0.18085],"object_to_goal_dist_end":0.16392,"object_to_goal_dist_start":0.04688,"object_z_max":0.18085,"peak_contact_force":0.12273,"phase_name":"descend_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1347.0,"raw_peak_contact_force":1.75876,"subtask_id":"reach_goal","tcp_end":[0.62561,0.15865,0.15917],"tcp_start":[0.60716,0.12357,0.2104],"tcp_to_object_dist_end":0.14551,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.6329,0.1336,0.01602],"object_pos_start":[0.6329,0.13359,0.01602],"object_to_goal_dist_end":0.16392,"object_to_goal_dist_start":0.16392,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1023.0,"raw_peak_contact_force":0.12272,"tcp_end":[0.61946,0.15706,0.17858],"tcp_start":[0.62561,0.15865,0.15917],"tcp_to_object_dist_end":0.16479,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":660.0,"n_steps_budget":780.0,"object_pos_end":[0.6329,0.1336,0.01602],"object_pos_start":[0.6329,0.1336,0.01602],"object_to_goal_dist_end":0.16392,"object_to_goal_dist_start":0.16392,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2640.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61706,0.15629,0.28391],"tcp_start":[0.61946,0.15706,0.17858],"tcp_to_object_dist_end":0.26931,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.03571,"average_solve_count":168.0,"average_success_count":168.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_z":0.11508,"approach_1.speed":0.10468,"approach_goal.goal_approach_z":0.07176,"approach_goal.speed":0.19906,"descend_1.descend_z":0.0033,"descend_goal.place_z_offset":-0.03395,"descend_goal.speed":0.08874,"lift_1.lift_height":0.1261,"retract_1.retract_z":0.15746},"optimized_scores":{"best_composite_score":0.10039,"best_fitness_score":0.73039,"best_task_score":0.50111},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":246.0,"contact_point_centroid":[0.58998,0.13051,-0.00376],"force_p95":0.74771,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.8307,"mean_force":0.24864,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59666,0.14865,0.10404]},{"body_a":"world","body_b":"grasp_target","contact_count":84.0,"contact_point_centroid":[0.46027,-1e-05,-0.00123],"force_p95":0.50553,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60031,"mean_force":0.09842,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45004,-0.00023,0.03242]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1066.0,"contact_point_centroid":[0.60305,0.13033,0.08861],"force_p95":0.22512,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.41918,"mean_force":0.09041,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60081,0.14981,0.09054]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7561.0,"contact_point_centroid":[0.44943,0.01877,0.08444],"force_p95":0.10358,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32184,"mean_force":0.06551,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44753,-0.00024,0.08231]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1047.0,"contact_point_centroid":[0.60223,0.16831,0.08969],"force_p95":0.13837,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30435,"mean_force":0.06513,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60136,0.14996,0.09111]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8218.0,"contact_point_centroid":[0.44948,-0.01913,0.08183],"force_p95":0.10175,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28431,"mean_force":0.06106,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44756,-0.00024,0.08019]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3639.0,"contact_point_centroid":[0.60493,0.16695,0.1379],"force_p95":0.11861,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26969,"mean_force":0.07393,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.60132,0.14833,0.13833]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3332.0,"contact_point_centroid":[0.6055,0.12943,0.13889],"force_p95":0.12567,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25165,"mean_force":0.08175,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.60125,0.14828,0.13938]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9635.0,"contact_point_centroid":[0.5314,0.05857,0.16385],"force_p95":0.1173,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20222,"mean_force":0.08374,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52721,0.07735,0.16309]},{"body_a":"world","body_b":"grasp_target","contact_count":3480.0,"contact_point_centroid":[0.58251,0.12589,-0.00199],"force_p95":0.12647,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19518,"mean_force":0.12277,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.59308,0.14766,0.18721]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11433.0,"contact_point_centroid":[0.53203,0.09568,0.16412],"force_p95":0.10004,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17399,"mean_force":0.0723,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52707,0.07721,0.16305]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.46284,-5e-05,-0.00201],"force_p95":0.12815,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14044,"mean_force":0.12429,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.45228,-0.0002,0.03201]},{"body_a":"world","body_b":"grasp_target","contact_count":1300.0,"contact_point_centroid":[0.46286,-7e-05,-0.0019],"force_p95":0.13564,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.123,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4821,-5e-05,0.23097]},{"body_a":"world","body_b":"grasp_target","contact_count":1568.0,"contact_point_centroid":[0.46286,-7e-05,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.46031,-0.0001,0.09839]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4389.0,"contact_point_centroid":[0.45115,0.01906,0.03323],"force_p95":0.07366,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09403,"mean_force":0.04929,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.45119,-0.00021,0.03097]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5091.0,"contact_point_centroid":[0.45104,-0.01929,0.03281],"force_p95":0.06449,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08635,"mean_force":0.04271,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.45119,-0.00021,0.03097]}],"total_contact_groups":16},"final_pose_error":0.01495,"key_states":{"actual_goal_position":[0.61015,0.15287,0.12219],"final_object_position":[0.5825,0.12588,0.02602],"final_tcp_position":[0.59373,0.14779,0.25847],"realised_goal_position":[0.61015,0.15287,0.12219],"realised_object_initial_position":[0.46286,-7e-05,0.03]},"peak_contact_force":0.8307,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":326.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.03],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.23148,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1300.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.46438,-8e-05,0.15979],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13378,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":392.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1568.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.45881,-0.00012,0.03831],"tcp_start":[0.46438,-8e-05,0.15979],"tcp_to_object_dist_end":0.01294,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46274,-3e-05,0.02592],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.23319,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12819,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11280.0,"raw_peak_contact_force":0.14044,"tcp_end":[0.45117,-0.00021,0.03095],"tcp_start":[0.45881,-0.00012,0.03831],"tcp_to_object_dist_end":0.01261,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":480.0,"n_steps_budget":810.0,"object_pos_end":[0.4647,-0.00018,0.13136],"object_pos_start":[0.46274,-3e-05,0.02592],"object_to_goal_dist_end":0.21134,"object_to_goal_dist_start":0.23319,"object_z_max":0.13119,"peak_contact_force":0.10795,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":15863.0,"raw_peak_contact_force":0.60031,"subtask_id":"lift_clearance","tcp_end":[0.4475,-0.00023,0.14266],"tcp_start":[0.45117,-0.00021,0.03095],"tcp_to_object_dist_end":0.02058,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":829.0,"n_steps_budget":1000.0,"object_pos_end":[0.60642,0.14707,0.15688],"object_pos_start":[0.4647,-0.00018,0.13136],"object_to_goal_dist_end":0.03537,"object_to_goal_dist_start":0.21134,"object_z_max":0.15687,"peak_contact_force":0.09846,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":21068.0,"raw_peak_contact_force":0.20222,"subtask_id":"reach_goal","tcp_end":[0.6008,0.14658,0.18414],"tcp_start":[0.4475,-0.00023,0.14266],"tcp_to_object_dist_end":0.02783,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":249.0,"n_steps_budget":1000.0,"object_pos_end":[0.60434,0.15023,0.06636],"object_pos_start":[0.60642,0.14707,0.15688],"object_to_goal_dist_end":0.05619,"object_to_goal_dist_start":0.03537,"object_z_max":0.15688,"peak_contact_force":0.13701,"phase_name":"descend_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":6971.0,"raw_peak_contact_force":0.26969,"subtask_id":"reach_goal","tcp_end":[0.60402,0.15062,0.09554],"tcp_start":[0.6008,0.14658,0.18414],"tcp_to_object_dist_end":0.02919,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58465,0.12693,0.02618],"object_pos_start":[0.60434,0.15023,0.06636],"object_to_goal_dist_end":0.10267,"object_to_goal_dist_start":0.05619,"object_z_max":0.06636,"peak_contact_force":0.19311,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2359.0,"raw_peak_contact_force":0.8307,"tcp_end":[0.59652,0.14861,0.11569],"tcp_start":[0.60402,0.15062,0.09554],"tcp_to_object_dist_end":0.09286,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":870.0,"n_steps_budget":990.0,"object_pos_end":[0.5825,0.12588,0.02602],"object_pos_start":[0.58465,0.12693,0.02618],"object_to_goal_dist_end":0.10364,"object_to_goal_dist_start":0.10267,"object_z_max":0.02618,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3480.0,"raw_peak_contact_force":0.19518,"tcp_end":[0.59373,0.14779,0.25847],"tcp_start":[0.59652,0.14861,0.11569],"tcp_to_object_dist_end":0.23376,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```