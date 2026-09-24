## Search State

- **Seed**: 9
- **Iteration**: 12 / 15

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

## Current Skill (Q=-0.033) — your mutation base

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

- **Composite score**: -0.033
- **task_score** (E): 0.384
- **fitness_score**: 0.667  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.700

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1483 |
| descend_1 | 1.00 | 1.00 | 0.1141 |
| grasp_1 | 1.00 | 1.00 | 0.0125 |
| lift_1 | 1.00 | 1.00 | 0.1373 |
| approach_goal | 1.00 | 1.00 | 0.2506 |
| descend_goal | 1.00 | 1.00 | 0.0473 |
| release_1 | 1.00 | 1.00 | 0.0196 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, -0.015, 0.158) | (0.515, -0.017, 0.030)→(0.515, -0.017, 0.026) | 0.268→0.270 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.510, -0.015, 0.158)→(0.510, -0.016, 0.044) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.510, -0.016, 0.044)→(0.502, -0.016, 0.035) | (0.515, -0.017, 0.026)→(0.515, -0.016, 0.026) | 0.270→0.270 | 1.00 / 42.000 | 0.136 | 0.181 |
| lift_1 | lift | 1.00 / step_budget | (0.502, -0.016, 0.035)→(0.498, -0.016, 0.172) | (0.515, -0.016, 0.026)→(0.509, -0.016, 0.156) | 0.270→0.232 | 1.00 / 37.000 | 0.046 | 0.485 |
| approach_goal | approach | 1.00 / step_budget | (0.498, -0.016, 0.172)→(0.609, 0.171, 0.282) | (0.509, -0.016, 0.156)→(0.616, 0.172, 0.166) | 0.232→0.126 | 1.00 / 23.000 | 91005.403 | 0.808 |
| descend_goal | descend | 1.00 / step_budget | (0.610, 0.174, 0.261)→(0.612, 0.178, 0.214) | (0.616, 0.172, 0.166)→(0.616, 0.177, 0.120) | 0.126→0.080 | 1.00 / 24.333 | 90998.814 | 0.207 |
| release_1 | release | 1.00 / step_budget | (0.612, 0.178, 0.214)→(0.607, 0.176, 0.233) | (0.616, 0.177, 0.120)→(0.613, 0.174, 0.021) | 0.080→0.149 | 1.00 / 2.667 | 0.221 | 1.179 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.526
- phase_score: 0.567
- phase_breakdown.reach_goal_score: 0.376
- phase_breakdown.lift_clearance_score: 0.617
- phase_breakdown.reach_object_score: 0.853
- grasp_place_fitness: 0.740

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.740
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.526
- **Median Q (composite search score)**: -0.052
- **K-run variance**: 0.0029
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.292


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.19672,"average_solve_count":244.0,"average_success_count":244.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_z":0.11756,"approach_1.speed":0.10846,"approach_goal.goal_approach_z":0.12199,"approach_goal.speed":0.19422,"descend_1.descend_z":0.00492,"descend_1.speed":0.15899,"descend_goal.goal_z_offset":0.02603,"descend_goal.speed":0.09318,"lift_1.lift_height":0.15567,"lift_1.speed":0.01986,"release_1.release_duration":1.23659},"optimized_scores":{"best_composite_score":-0.08687,"best_fitness_score":0.61313,"best_task_score":0.27881},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":222.0,"contact_point_centroid":[0.61426,0.22042,-0.00844],"force_p95":1.37155,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.12146,"mean_force":0.39335,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.60177,0.20818,0.30963]},{"body_a":"world","body_b":"grasp_target","contact_count":131.0,"contact_point_centroid":[0.5325,-0.02033,-0.00142],"force_p95":0.39295,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.44856,"mean_force":0.14287,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52145,-0.02064,0.03577]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6916.0,"contact_point_centroid":[0.54986,0.04037,0.22062],"force_p95":0.15019,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27652,"mean_force":0.08589,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.54597,0.05915,0.2197]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16052.0,"contact_point_centroid":[0.5192,-0.00146,0.11002],"force_p95":0.0788,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25797,"mean_force":0.05368,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51883,-0.02057,0.1079]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16451.0,"contact_point_centroid":[0.51927,-0.03965,0.10688],"force_p95":0.07721,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2466,"mean_force":0.05297,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51884,-0.02057,0.105]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8149.0,"contact_point_centroid":[0.55131,0.08079,0.22224],"force_p95":0.1285,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23625,"mean_force":0.07431,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.54713,0.06227,0.22158]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53704,-0.02115,-0.00206],"force_p95":0.14067,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18297,"mean_force":0.12754,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5241,-0.02069,0.03614]},{"body_a":"world","body_b":"grasp_target","contact_count":1384.0,"contact_point_centroid":[0.53702,-0.02132,-0.0019],"force_p95":0.1356,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12298,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51341,-0.00909,0.23009]},{"body_a":"world","body_b":"grasp_target","contact_count":528.0,"contact_point_centroid":[0.61388,0.21995,-0.00191],"force_p95":0.1282,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12892,"mean_force":0.116,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.60549,0.21996,0.27971]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4099.0,"contact_point_centroid":[0.52368,-0.00147,0.03755],"force_p95":0.07763,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1275,"mean_force":0.05184,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52291,-0.02067,0.03478]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.61388,0.21995,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12265,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60277,0.22201,0.2448]},{"body_a":"world","body_b":"grasp_target","contact_count":1036.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52923,-0.01973,0.10227]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4916.0,"contact_point_centroid":[0.52372,-0.03976,0.03662],"force_p95":0.06996,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08095,"mean_force":0.0447,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52292,-0.02067,0.03478]},{"body_a":"left_finger","body_b":"right_finger","contact_count":97.0,"contact_point_centroid":[0.60382,0.2128,0.31494],"force_p95":0.016,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01648,"mean_force":0.013,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.60353,0.21279,0.31242]},{"body_a":"left_finger","body_b":"right_finger","contact_count":568.0,"contact_point_centroid":[0.60594,0.21999,0.28189],"force_p95":0.01119,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01159,"mean_force":0.01044,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.60549,0.21998,0.27958]},{"body_a":"left_finger","body_b":"right_finger","contact_count":222.0,"contact_point_centroid":[0.6049,0.22295,0.24342],"force_p95":0.01095,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01097,"mean_force":0.01003,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60467,0.22292,0.24126]}],"total_contact_groups":16},"final_pose_error":0.0133,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.61388,0.21995,0.01602],"final_tcp_position":[0.606,0.22337,0.24523],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":273016.02652,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":347.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1384.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.5292,-0.0187,0.15973],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13396,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":259.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1036.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53144,-0.02083,0.04477],"tcp_start":[0.5292,-0.0187,0.15973],"tcp_to_object_dist_end":0.01957,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53692,-0.02063,0.02578],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31634,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13714,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10815.0,"raw_peak_contact_force":0.18297,"tcp_end":[0.52288,-0.02067,0.03474],"tcp_start":[0.53144,-0.02083,0.04477],"tcp_to_object_dist_end":0.01665,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":847.0,"n_steps_budget":1000.0,"object_pos_end":[0.52758,-0.02058,0.16025],"object_pos_start":[0.53692,-0.02063,0.02578],"object_to_goal_dist_end":0.26597,"object_to_goal_dist_start":0.31634,"object_z_max":0.16009,"peak_contact_force":0.0691,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":32634.0,"raw_peak_contact_force":0.44856,"subtask_id":"lift_clearance","tcp_end":[0.51915,-0.02057,0.176],"tcp_start":[0.52288,-0.02067,0.03474],"tcp_to_object_dist_end":0.01786,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":794.0,"n_steps_budget":1000.0,"object_pos_end":[0.61391,0.2187,0.01452],"object_pos_start":[0.52758,-0.02058,0.16025],"object_to_goal_dist_end":0.19314,"object_to_goal_dist_start":0.26597,"object_z_max":0.25641,"peak_contact_force":273016.02652,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":15384.0,"raw_peak_contact_force":2.12146,"subtask_id":"reach_goal","tcp_end":[0.60463,0.21601,0.31426],"tcp_start":[0.51915,-0.02057,0.176],"tcp_to_object_dist_end":0.29989,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":132.0,"n_steps_budget":1000.0,"object_pos_end":[0.61388,0.21995,0.01601],"object_pos_start":[0.61391,0.2187,0.01452],"object_to_goal_dist_end":0.19159,"object_to_goal_dist_start":0.19314,"object_z_max":0.01688,"peak_contact_force":272996.26016,"phase_name":"descend_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1096.0,"raw_peak_contact_force":0.12892,"subtask_id":"reach_goal","tcp_end":[0.606,0.22337,0.24523],"tcp_start":[0.60655,0.22304,0.25213],"tcp_to_object_dist_end":0.22938,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61388,0.21995,0.01602],"object_pos_start":[0.61388,0.21995,0.01602],"object_to_goal_dist_end":0.19158,"object_to_goal_dist_start":0.19158,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1022.0,"raw_peak_contact_force":0.12265,"tcp_end":[0.60171,0.22148,0.26421],"tcp_start":[0.606,0.22337,0.24523],"tcp_to_object_dist_end":0.24849,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.02639,"average_solve_count":341.0,"average_success_count":341.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_z":0.13506,"approach_1.speed":0.06918,"approach_goal.goal_approach_z":0.15954,"approach_goal.speed":0.0148,"descend_1.descend_z":0.00457,"descend_1.speed":0.08193,"descend_goal.goal_z_offset":0.03101,"descend_goal.speed":0.14613,"lift_1.lift_height":0.15905,"lift_1.speed":0.01072,"release_1.release_duration":0.88109},"optimized_scores":{"best_composite_score":-0.05183,"best_fitness_score":0.64817,"best_task_score":0.34835},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":119.0,"contact_point_centroid":[0.61422,0.16451,-0.01113],"force_p95":1.56724,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.91764,"mean_force":0.65343,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62385,0.16026,0.23688]},{"body_a":"world","body_b":"grasp_target","contact_count":133.0,"contact_point_centroid":[0.54084,-0.02784,-0.00144],"force_p95":0.40005,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.45109,"mean_force":0.14349,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52966,-0.02826,0.03482]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16452.0,"contact_point_centroid":[0.52759,-0.00905,0.11026],"force_p95":0.07965,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25072,"mean_force":0.05448,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52702,-0.02816,0.10803]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17022.0,"contact_point_centroid":[0.52763,-0.04722,0.1074],"force_p95":0.07799,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24319,"mean_force":0.05339,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52703,-0.02816,0.10549]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54563,-0.02904,-0.00209],"force_p95":0.14801,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21447,"mean_force":0.12943,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53237,-0.02834,0.03519]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2966.0,"contact_point_centroid":[0.62864,0.17742,0.27494],"force_p95":0.08336,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1969,"mean_force":0.05554,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.62737,0.15851,0.2737]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3141.0,"contact_point_centroid":[0.62859,0.13943,0.2741],"force_p95":0.08723,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17773,"mean_force":0.05551,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.62741,0.15859,0.27267]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1278.0,"contact_point_centroid":[0.62747,0.14218,0.2234],"force_p95":0.06894,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13984,"mean_force":0.04228,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62701,0.16134,0.22147]},{"body_a":"world","body_b":"grasp_target","contact_count":1360.0,"contact_point_centroid":[0.5456,-0.02923,-0.0019],"force_p95":0.1356,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12299,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51682,-0.01234,0.23802]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4088.0,"contact_point_centroid":[0.53205,-0.0091,0.03655],"force_p95":0.07875,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13646,"mean_force":0.05186,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53116,-0.0283,0.03378]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1239.0,"contact_point_centroid":[0.62766,0.1806,0.22345],"force_p95":0.07133,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12514,"mean_force":0.04344,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62699,0.16133,0.22142]},{"body_a":"world","body_b":"grasp_target","contact_count":1232.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53682,-0.02693,0.11001]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17877.0,"contact_point_centroid":[0.5747,0.04228,0.24553],"force_p95":0.07678,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09297,"mean_force":0.05066,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.57375,0.06118,0.24491]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15090.0,"contact_point_centroid":[0.57563,0.08105,0.24721],"force_p95":0.08699,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09183,"mean_force":0.05861,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.57416,0.06193,0.24549]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4943.0,"contact_point_centroid":[0.53206,-0.04741,0.03561],"force_p95":0.07132,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08275,"mean_force":0.04468,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53116,-0.0283,0.03379]}],"total_contact_groups":15},"final_pose_error":0.01966,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.6182,0.15669,0.01963],"final_tcp_position":[0.62893,0.1618,0.22694],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":1.91764,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":341.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1360.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.5364,-0.02543,0.17588],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15019,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":308.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1232.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.5398,-0.02856,0.0441],"tcp_start":[0.5364,-0.02543,0.17588],"tcp_to_object_dist_end":0.019,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5455,-0.02832,0.0257],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26046,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.14305,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10831.0,"raw_peak_contact_force":0.21447,"tcp_end":[0.53113,-0.0283,0.03375],"tcp_start":[0.5398,-0.02856,0.0441],"tcp_to_object_dist_end":0.01647,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":883.0,"n_steps_budget":1000.0,"object_pos_end":[0.53596,-0.02817,0.16292],"object_pos_start":[0.5455,-0.02832,0.0257],"object_to_goal_dist_end":0.2165,"object_to_goal_dist_start":0.26046,"object_z_max":0.16277,"peak_contact_force":0.06881,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":33607.0,"raw_peak_contact_force":0.45109,"subtask_id":"lift_clearance","tcp_end":[0.52739,-0.02816,0.17834],"tcp_start":[0.53113,-0.0283,0.03375],"tcp_to_object_dist_end":0.01764,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":922.0,"n_steps_budget":1000.0,"object_pos_end":[0.63131,0.15548,0.29926],"object_pos_start":[0.53596,-0.02817,0.16292],"object_to_goal_dist_end":0.12271,"object_to_goal_dist_start":0.2165,"object_z_max":0.29913,"peak_contact_force":0.08383,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":32967.0,"raw_peak_contact_force":0.09297,"subtask_id":"reach_goal","tcp_end":[0.62616,0.15529,0.32028],"tcp_start":[0.52739,-0.02816,0.17834],"tcp_to_object_dist_end":0.02165,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":159.0,"n_steps_budget":1000.0,"object_pos_end":[0.62414,0.16127,0.20411],"object_pos_start":[0.63131,0.15548,0.29926],"object_to_goal_dist_end":0.02878,"object_to_goal_dist_start":0.12271,"object_z_max":0.29927,"peak_contact_force":0.07086,"phase_name":"descend_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":6107.0,"raw_peak_contact_force":0.1969,"subtask_id":"reach_goal","tcp_end":[0.62893,0.1618,0.22694],"tcp_start":[0.62616,0.15529,0.32028],"tcp_to_object_dist_end":0.02333,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.6182,0.15669,0.01963],"object_pos_start":[0.62414,0.16127,0.20411],"object_to_goal_dist_end":0.15818,"object_to_goal_dist_start":0.02878,"object_z_max":0.20411,"peak_contact_force":0.31047,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2636.0,"raw_peak_contact_force":1.91764,"tcp_end":[0.62382,0.16025,0.24499],"tcp_start":[0.62893,0.1618,0.22694],"tcp_to_object_dist_end":0.22546,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.87234,"average_solve_count":141.0,"average_success_count":141.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_z":0.09329,"approach_1.speed":0.11375,"approach_goal.goal_approach_z":0.10009,"approach_goal.speed":0.19193,"descend_1.descend_z":0.0024,"descend_1.speed":0.15066,"descend_goal.goal_z_offset":0.0307,"descend_goal.speed":0.17351,"lift_1.lift_height":0.14025,"lift_1.speed":0.06865,"release_1.release_duration":1.40372},"optimized_scores":{"best_composite_score":0.04003,"best_fitness_score":0.74003,"best_task_score":0.52617},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":134.0,"contact_point_centroid":[0.59885,0.15104,-0.00911],"force_p95":1.22008,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.49599,"mean_force":0.52534,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59612,0.14647,0.17966]},{"body_a":"world","body_b":"grasp_target","contact_count":91.0,"contact_point_centroid":[0.45967,-0.00037,-0.00129],"force_p95":0.51249,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5565,"mean_force":0.12136,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45046,-0.00022,0.03651]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":761.0,"contact_point_centroid":[0.60596,0.12894,0.16507],"force_p95":0.10258,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.44955,"mean_force":0.07053,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59995,0.14762,0.16498]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":819.0,"contact_point_centroid":[0.60503,0.16646,0.16456],"force_p95":0.11007,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.42844,"mean_force":0.06842,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59991,0.1476,0.16491]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9283.0,"contact_point_centroid":[0.44958,0.01879,0.09445],"force_p95":0.10238,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30751,"mean_force":0.06495,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44789,-0.00023,0.0923]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9943.0,"contact_point_centroid":[0.44944,-0.01915,0.09269],"force_p95":0.10189,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30236,"mean_force":0.0613,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44788,-0.00023,0.09092]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1032.0,"contact_point_centroid":[0.60456,0.16404,0.19264],"force_p95":0.13902,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29641,"mean_force":0.08503,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.59947,0.1453,0.19265]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":976.0,"contact_point_centroid":[0.60534,0.12666,0.19315],"force_p95":0.13477,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29034,"mean_force":0.08603,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.59945,0.14528,0.19276]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7068.0,"contact_point_centroid":[0.53132,0.0578,0.18724],"force_p95":0.12252,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20816,"mean_force":0.08086,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52719,0.0766,0.18654]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7995.0,"contact_point_centroid":[0.52994,0.09313,0.18717],"force_p95":0.10655,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17821,"mean_force":0.07246,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52508,0.07463,0.18579]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.46284,-0.0001,-0.00202],"force_p95":0.1286,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14574,"mean_force":0.12438,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.45263,-0.00019,0.03618]},{"body_a":"world","body_b":"grasp_target","contact_count":1480.0,"contact_point_centroid":[0.46286,-7e-05,-0.00191],"force_p95":0.13511,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12296,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48152,-4e-05,0.21963]},{"body_a":"world","body_b":"grasp_target","contact_count":916.0,"contact_point_centroid":[0.46286,-7e-05,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.46042,-9e-05,0.09038]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4847.0,"contact_point_centroid":[0.45167,-0.01939,0.03708],"force_p95":0.06797,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08963,"mean_force":0.04478,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.45158,-0.0002,0.03517]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4864.0,"contact_point_centroid":[0.45165,0.019,0.03707],"force_p95":0.06804,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08921,"mean_force":0.04481,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.45158,-0.0002,0.03518]}],"total_contact_groups":15},"final_pose_error":0.01955,"key_states":{"actual_goal_position":[0.61015,0.15287,0.12219],"final_object_position":[0.60655,0.14557,0.02621],"final_tcp_position":[0.60236,0.14811,0.17017],"realised_goal_position":[0.61015,0.15287,0.12219],"realised_object_initial_position":[0.46286,-7e-05,0.03]},"peak_contact_force":1.49599,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":371.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.03],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.23148,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1480.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.46361,-8e-05,0.13792],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1119,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":229.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":916.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.45914,-0.00011,0.04264],"tcp_start":[0.46361,-8e-05,0.13792],"tcp_to_object_dist_end":0.01703,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46275,-0.00018,0.02592],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.23328,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12837,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11511.0,"raw_peak_contact_force":0.14574,"tcp_end":[0.45155,-0.0002,0.03515],"tcp_start":[0.45914,-0.00011,0.04264],"tcp_to_object_dist_end":0.01451,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":580.0,"n_steps_budget":1000.0,"object_pos_end":[0.46451,-0.00022,0.14628],"object_pos_start":[0.46275,-0.00018,0.02592],"object_to_goal_dist_end":0.21266,"object_to_goal_dist_start":0.23328,"object_z_max":0.14611,"peak_contact_force":0.0,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":19317.0,"raw_peak_contact_force":0.5565,"subtask_id":"lift_clearance","tcp_end":[0.44791,-0.00021,0.161],"tcp_start":[0.45155,-0.0002,0.03515],"tcp_to_object_dist_end":0.02219,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":572.0,"n_steps_budget":1000.0,"object_pos_end":[0.60283,0.14313,0.18286],"object_pos_start":[0.46451,-0.00022,0.14628],"object_to_goal_dist_end":0.06188,"object_to_goal_dist_start":0.21266,"object_z_max":0.18281,"peak_contact_force":0.09902,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":15063.0,"raw_peak_contact_force":0.20816,"subtask_id":"reach_goal","tcp_end":[0.59725,0.14274,0.21091],"tcp_start":[0.44791,-0.00021,0.161],"tcp_to_object_dist_end":0.02861,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":82.0,"n_steps_budget":1000.0,"object_pos_end":[0.60917,0.14853,0.1412],"object_pos_start":[0.60283,0.14313,0.18286],"object_to_goal_dist_end":0.01952,"object_to_goal_dist_start":0.06188,"object_z_max":0.18286,"peak_contact_force":0.10985,"phase_name":"descend_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2008.0,"raw_peak_contact_force":0.29641,"subtask_id":"reach_goal","tcp_end":[0.60236,0.14811,0.17017],"tcp_start":[0.59725,0.14274,0.21091],"tcp_to_object_dist_end":0.02977,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60655,0.14557,0.02621],"object_pos_start":[0.60917,0.14853,0.1412],"object_to_goal_dist_end":0.09632,"object_to_goal_dist_start":0.01952,"object_z_max":0.1412,"peak_contact_force":0.22971,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1714.0,"raw_peak_contact_force":1.49599,"tcp_end":[0.59605,0.14645,0.18966],"tcp_start":[0.60236,0.14811,0.17017],"tcp_to_object_dist_end":0.16379,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```