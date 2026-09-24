## Search State

- **Seed**: 9
- **Iteration**: 13 / 15

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

## Current Skill (Q=0.184) — your mutation base

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

- **Composite score**: 0.184
- **task_score** (E): 0.757
- **fitness_score**: 0.854  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.670

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1464 |
| descend_1 | 1.00 | 1.00 | 0.1170 |
| grasp_1 | 1.00 | 1.00 | 0.0127 |
| lift_1 | 1.00 | 1.00 | 0.1434 |
| approach_goal | 1.00 | 1.00 | 0.1555 |
| descend_goal | 1.00 | 1.00 | 0.0763 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, -0.015, 0.160) | (0.515, -0.017, 0.030)→(0.515, -0.017, 0.026) | 0.268→0.270 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.510, -0.015, 0.160)→(0.510, -0.016, 0.043) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.510, -0.016, 0.043)→(0.502, -0.016, 0.033) | (0.515, -0.017, 0.026)→(0.515, -0.016, 0.026) | 0.270→0.270 | 1.00 / 42.000 | 0.136 | 0.180 |
| lift_1 | lift | 1.00 / step_budget | (0.502, -0.016, 0.033)→(0.498, -0.016, 0.177) | (0.515, -0.016, 0.026)→(0.507, -0.016, 0.163) | 0.270→0.234 | 1.00 / 38.000 | 0.078 | 0.471 |
| approach_goal | approach | 1.00 / step_budget | (0.526, 0.060, 0.214)→(0.607, 0.167, 0.287) | (0.507, -0.016, 0.163)→(0.609, 0.159, 0.183) | 0.234→0.144 | 1.00 / 15.667 | 0.134 | 0.904 |
| descend_goal | descend | 1.00 / step_budget | (0.607, 0.169, 0.282)→(0.612, 0.176, 0.206) | (0.609, 0.159, 0.183)→(0.608, 0.165, 0.107) | 0.144→0.073 | 1.00 / 17.333 | 3249.824 | 0.299 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.327
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 1.000
- phase_score: 0.552
- phase_breakdown.reach_goal_score: 0.450
- phase_breakdown.lift_clearance_score: 0.696
- phase_breakdown.reach_object_score: 0.626
- grasp_place_fitness: 0.976

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.976
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.304
- **K-run variance**: 0.0293
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.362


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.34956,"average_solve_count":226.0,"average_success_count":226.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_z":0.13954,"approach_1.speed":0.13331,"approach_goal.arc_height":0.05542,"approach_goal.goal_approach_z":0.07358,"approach_goal.speed":0.18085,"descend_1.descend_z":0.00041,"descend_1.speed":0.18551,"descend_goal.goal_z_offset":0.03437,"descend_goal.speed":0.11665,"lift_1.lift_height":0.14999,"lift_1.speed":0.03342},"optimized_scores":{"best_composite_score":-0.05815,"best_fitness_score":0.61185,"best_task_score":0.27083},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":500.0,"contact_point_centroid":[0.59836,0.18776,-0.00477],"force_p95":1.02899,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.12778,"mean_force":0.23449,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5957,0.19205,0.28056]},{"body_a":"world","body_b":"grasp_target","contact_count":116.0,"contact_point_centroid":[0.53208,-0.02044,-0.00138],"force_p95":0.48644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.51896,"mean_force":0.16134,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5213,-0.02068,0.03104]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6058.0,"contact_point_centroid":[0.53867,0.01069,0.2227],"force_p95":0.15798,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3029,"mean_force":0.08613,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53487,0.02944,0.22194]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14213.0,"contact_point_centroid":[0.51925,-0.0015,0.09995],"force_p95":0.07939,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26681,"mean_force":0.05597,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51853,-0.02061,0.09751]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6865.0,"contact_point_centroid":[0.53984,0.0501,0.22395],"force_p95":0.13783,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26387,"mean_force":0.07737,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53566,0.03158,0.22364]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14986.0,"contact_point_centroid":[0.51923,-0.03967,0.09756],"force_p95":0.07743,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25701,"mean_force":0.05376,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51853,-0.02061,0.09545]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53703,-0.02113,-0.00206],"force_p95":0.14005,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18221,"mean_force":0.1274,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5239,-0.02072,0.03139]},{"body_a":"world","body_b":"grasp_target","contact_count":1172.0,"contact_point_centroid":[0.53702,-0.02132,-0.00189],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12304,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51316,-0.00885,0.24118]},{"body_a":"world","body_b":"grasp_target","contact_count":240.0,"contact_point_centroid":[0.59829,0.18756,-0.002],"force_p95":0.12407,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12453,"mean_force":0.12293,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.60352,0.21616,0.2637]},{"body_a":"world","body_b":"grasp_target","contact_count":1204.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52894,-0.01956,0.11065]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4097.0,"contact_point_centroid":[0.52364,-0.0015,0.03272],"force_p95":0.07762,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12256,"mean_force":0.05181,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52268,-0.0207,0.03001]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4916.0,"contact_point_centroid":[0.52362,-0.0398,0.0318],"force_p95":0.06966,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08473,"mean_force":0.04474,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52268,-0.0207,0.03001]},{"body_a":"left_finger","body_b":"right_finger","contact_count":382.0,"contact_point_centroid":[0.59856,0.19893,0.28172],"force_p95":0.01408,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01591,"mean_force":0.01115,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.59821,0.19892,0.27947]},{"body_a":"left_finger","body_b":"right_finger","contact_count":261.0,"contact_point_centroid":[0.60408,0.21624,0.26606],"force_p95":0.01094,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01254,"mean_force":0.01029,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.60354,0.21622,0.26352]}],"total_contact_groups":14},"final_pose_error":0.01437,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.59829,0.18755,0.01602],"final_tcp_position":[0.60432,0.21929,0.25173],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":9749.16276,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":294.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1172.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.52864,-0.01833,0.18134],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15558,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":301.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1204.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53142,-0.02085,0.04014],"tcp_start":[0.52864,-0.01833,0.18134],"tcp_to_object_dist_end":0.0152,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5369,-0.02062,0.02579],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31633,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13639,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10813.0,"raw_peak_contact_force":0.18221,"tcp_end":[0.52265,-0.0207,0.02997],"tcp_start":[0.53142,-0.02085,0.04014],"tcp_to_object_dist_end":0.01485,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":781.0,"n_steps_budget":1000.0,"object_pos_end":[0.52896,-0.02059,0.15447],"object_pos_start":[0.5369,-0.02062,0.02579],"object_to_goal_dist_end":0.26664,"object_to_goal_dist_start":0.31633,"object_z_max":0.15431,"peak_contact_force":0.07999,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":29315.0,"raw_peak_contact_force":0.51896,"subtask_id":"lift_clearance","tcp_end":[0.51881,-0.02061,0.16558],"tcp_start":[0.52265,-0.0207,0.02997],"tcp_to_object_dist_end":0.01505,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":779.0,"n_steps_budget":1000.0,"object_pos_end":[0.59827,0.18772,0.01627],"object_pos_start":[0.52896,-0.02059,0.15447],"object_to_goal_dist_end":0.19565,"object_to_goal_dist_start":0.26664,"object_z_max":0.25495,"peak_contact_force":0.1247,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":13805.0,"raw_peak_contact_force":2.12778,"subtask_id":"reach_goal","tcp_end":[0.60258,0.21268,0.27506],"tcp_start":[0.6023,0.20981,0.27727],"tcp_to_object_dist_end":0.26002,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":60.0,"n_steps_budget":1000.0,"object_pos_end":[0.59829,0.18755,0.01601],"object_pos_start":[0.59828,0.18764,0.01602],"object_to_goal_dist_end":0.19595,"object_to_goal_dist_start":0.19592,"object_z_max":0.01602,"peak_contact_force":9749.16276,"phase_name":"descend_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":501.0,"raw_peak_contact_force":0.12453,"subtask_id":"reach_goal","tcp_end":[0.60432,0.21929,0.25173],"tcp_start":[0.60452,0.21805,0.25826],"tcp_to_object_dist_end":0.23792,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.24281,"average_solve_count":313.0,"average_success_count":313.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_z":0.10224,"approach_1.speed":0.07811,"approach_goal.arc_height":0.08005,"approach_goal.goal_approach_z":0.14765,"approach_goal.speed":0.04904,"descend_1.descend_z":0.00458,"descend_1.speed":0.19833,"descend_goal.goal_z_offset":0.00991,"descend_goal.speed":0.18215,"lift_1.lift_height":0.17494,"lift_1.speed":0.01359},"optimized_scores":{"best_composite_score":0.30369,"best_fitness_score":0.97369,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":129.0,"contact_point_centroid":[0.54072,-0.0278,-0.00141],"force_p95":0.4256,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.4531,"mean_force":0.1426,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52937,-0.02824,0.03473]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1910.0,"contact_point_centroid":[0.62944,0.17238,0.25943],"force_p95":0.15761,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.41677,"mean_force":0.09965,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.62513,0.15461,0.26164]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2108.0,"contact_point_centroid":[0.62905,0.13638,0.26254],"force_p95":0.17109,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.38244,"mean_force":0.10558,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.62496,0.15427,0.26501]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17617.0,"contact_point_centroid":[0.52766,-0.00904,0.11672],"force_p95":0.08059,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24961,"mean_force":0.05595,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52672,-0.02814,0.11434]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18575.0,"contact_point_centroid":[0.52765,-0.04719,0.11375],"force_p95":0.0779,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2477,"mean_force":0.05385,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52673,-0.02814,0.11169]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14176.0,"contact_point_centroid":[0.55609,0.00376,0.28583],"force_p95":0.09961,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24728,"mean_force":0.06384,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55277,0.02234,0.28544]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11652.0,"contact_point_centroid":[0.55526,0.03975,0.28384],"force_p95":0.11564,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21584,"mean_force":0.0766,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55195,0.02086,0.28284]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54563,-0.02903,-0.00209],"force_p95":0.14869,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21543,"mean_force":0.12958,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53209,-0.02832,0.03509]},{"body_a":"world","body_b":"grasp_target","contact_count":1612.0,"contact_point_centroid":[0.5456,-0.02923,-0.00192],"force_p95":0.13462,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12293,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51713,-0.01265,0.22229]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4088.0,"contact_point_centroid":[0.53196,-0.00907,0.03637],"force_p95":0.079,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13411,"mean_force":0.05186,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53086,-0.02828,0.03366]},{"body_a":"world","body_b":"grasp_target","contact_count":908.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53722,-0.02721,0.09419]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4945.0,"contact_point_centroid":[0.53191,-0.04739,0.03544],"force_p95":0.07124,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08294,"mean_force":0.04467,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53086,-0.02828,0.03366]}],"total_contact_groups":12},"final_pose_error":0.01947,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.62636,0.15941,0.17803],"final_tcp_position":[0.62812,0.16072,0.20523],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":0.4531,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":404.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1612.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.53696,-0.02598,0.14402],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11836,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":227.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":908.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53963,-0.02853,0.04409],"tcp_start":[0.53696,-0.02598,0.14402],"tcp_to_object_dist_end":0.01905,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5455,-0.0283,0.02569],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26046,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.14358,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10833.0,"raw_peak_contact_force":0.21543,"tcp_end":[0.53083,-0.02828,0.03362],"tcp_start":[0.53963,-0.02853,0.04409],"tcp_to_object_dist_end":0.01668,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":977.0,"n_steps_budget":1000.0,"object_pos_end":[0.53526,-0.02811,0.17803],"object_pos_start":[0.5455,-0.0283,0.02569],"object_to_goal_dist_end":0.21631,"object_to_goal_dist_start":0.26046,"object_z_max":0.17787,"peak_contact_force":0.08006,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":36321.0,"raw_peak_contact_force":0.4531,"subtask_id":"lift_clearance","tcp_end":[0.52722,-0.02815,0.19413],"tcp_start":[0.53083,-0.02828,0.03362],"tcp_to_object_dist_end":0.018,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":17.0,"n_steps":930.0,"n_steps_budget":1000.0,"object_pos_end":[0.6301,0.14788,0.30116],"object_pos_start":[0.53526,-0.02811,0.17803],"object_to_goal_dist_end":0.12543,"object_to_goal_dist_start":0.21631,"object_z_max":0.31781,"peak_contact_force":0.15257,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":25828.0,"raw_peak_contact_force":0.24728,"subtask_id":"reach_goal","tcp_end":[0.6225,0.14802,0.32511],"tcp_start":[0.52722,-0.02815,0.19413],"tcp_to_object_dist_end":0.02513,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":197.0,"n_steps_budget":1000.0,"object_pos_end":[0.62636,0.15941,0.17803],"object_pos_start":[0.6301,0.14788,0.30116],"object_to_goal_dist_end":0.00858,"object_to_goal_dist_start":0.12543,"object_z_max":0.30116,"peak_contact_force":0.18919,"phase_name":"descend_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4018.0,"raw_peak_contact_force":0.41677,"subtask_id":"reach_goal","tcp_end":[0.62812,0.16072,0.20523],"tcp_start":[0.6225,0.14802,0.32511],"tcp_to_object_dist_end":0.02729,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.25455,"average_solve_count":220.0,"average_success_count":220.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_z":0.10845,"approach_1.speed":0.14104,"approach_goal.arc_height":0.06483,"approach_goal.goal_approach_z":0.13845,"approach_goal.speed":0.16125,"descend_1.descend_z":0.00311,"descend_1.speed":0.1978,"descend_goal.goal_z_offset":0.02086,"descend_goal.speed":0.10737,"lift_1.lift_height":0.14843,"lift_1.speed":0.01652},"optimized_scores":{"best_composite_score":0.30586,"best_fitness_score":0.97586,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":112.0,"contact_point_centroid":[0.45894,-2e-05,-0.00138],"force_p95":0.3848,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.43981,"mean_force":0.15785,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45019,-0.00022,0.03695]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2120.0,"contact_point_centroid":[0.59992,0.16272,0.20532],"force_p95":0.15112,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35709,"mean_force":0.08741,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.59916,0.14469,0.20863]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1781.0,"contact_point_centroid":[0.59973,0.12569,0.21011],"force_p95":0.16893,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35508,"mean_force":0.10759,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.59875,0.14428,0.21321]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9204.0,"contact_point_centroid":[0.50404,0.03235,0.24102],"force_p95":0.11241,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33814,"mean_force":0.07148,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.50051,0.05115,0.2398]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9270.0,"contact_point_centroid":[0.50681,0.07237,0.24436],"force_p95":0.10745,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33076,"mean_force":0.07142,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5031,0.05357,0.24291]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13660.0,"contact_point_centroid":[0.44788,0.01891,0.10416],"force_p95":0.0729,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25022,"mean_force":0.05108,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44768,-0.00024,0.10228]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13698.0,"contact_point_centroid":[0.4479,-0.01937,0.10398],"force_p95":0.07358,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22474,"mean_force":0.05102,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44769,-0.00024,0.10209]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.46284,-4e-05,-0.00202],"force_p95":0.12808,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14142,"mean_force":0.12434,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.45243,-0.00019,0.03705]},{"body_a":"world","body_b":"grasp_target","contact_count":1320.0,"contact_point_centroid":[0.46286,-7e-05,-0.0019],"force_p95":0.13564,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.123,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48194,-5e-05,0.22773]},{"body_a":"world","body_b":"grasp_target","contact_count":1032.0,"contact_point_centroid":[0.46286,-7e-05,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.46059,-0.0001,0.09862]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4389.0,"contact_point_centroid":[0.45128,0.01909,0.03814],"force_p95":0.07394,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09431,"mean_force":0.04934,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.45136,-0.00021,0.03603]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5332.0,"contact_point_centroid":[0.4508,-0.01929,0.03766],"force_p95":0.06281,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08748,"mean_force":0.04089,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.45136,-0.00021,0.03603]}],"total_contact_groups":12},"final_pose_error":0.01986,"key_states":{"actual_goal_position":[0.61015,0.15287,0.12219],"final_object_position":[0.59911,0.14836,0.12844],"final_tcp_position":[0.60372,0.14911,0.16147],"realised_goal_position":[0.61015,0.15287,0.12219],"realised_object_initial_position":[0.46286,-7e-05,0.03]},"peak_contact_force":0.43981,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":331.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.03],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.23148,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1320.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.46412,-8e-05,0.15337],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12736,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":258.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1032.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.45908,-0.00011,0.04361],"tcp_start":[0.46412,-8e-05,0.15337],"tcp_to_object_dist_end":0.01799,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46275,-1e-05,0.02592],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.23316,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12817,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11521.0,"raw_peak_contact_force":0.14142,"tcp_end":[0.45133,-0.00021,0.036],"tcp_start":[0.45908,-0.00011,0.04361],"tcp_to_object_dist_end":0.01523,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":684.0,"n_steps_budget":1000.0,"object_pos_end":[0.45567,-0.00023,0.15584],"object_pos_start":[0.46275,-1e-05,0.02592],"object_to_goal_dist_end":0.22008,"object_to_goal_dist_start":0.23316,"object_z_max":0.15565,"peak_contact_force":0.07255,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":27470.0,"raw_peak_contact_force":0.43981,"subtask_id":"lift_clearance","tcp_end":[0.4478,-0.00022,0.16986],"tcp_start":[0.45133,-0.00021,0.036],"tcp_to_object_dist_end":0.01607,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":663.0,"n_steps_budget":1000.0,"object_pos_end":[0.59985,0.14021,0.23113],"object_pos_start":[0.45567,-0.00023,0.15584],"object_to_goal_dist_end":0.11016,"object_to_goal_dist_start":0.22008,"object_z_max":0.25262,"peak_contact_force":0.12623,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":18474.0,"raw_peak_contact_force":0.33814,"subtask_id":"reach_goal","tcp_end":[0.59524,0.14001,0.26218],"tcp_start":[0.4478,-0.00022,0.16986],"tcp_to_object_dist_end":0.0314,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":178.0,"n_steps_budget":1000.0,"object_pos_end":[0.59911,0.14836,0.12844],"object_pos_start":[0.59985,0.14021,0.23113],"object_to_goal_dist_end":0.01347,"object_to_goal_dist_start":0.11016,"object_z_max":0.23113,"peak_contact_force":0.12047,"phase_name":"descend_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3901.0,"raw_peak_contact_force":0.35709,"subtask_id":"reach_goal","tcp_end":[0.60372,0.14911,0.16147],"tcp_start":[0.59524,0.14001,0.26218],"tcp_to_object_dist_end":0.03335,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```