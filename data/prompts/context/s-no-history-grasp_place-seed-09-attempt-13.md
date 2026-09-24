## Search State

- **Seed**: 9
- **Iteration**: 14 / 15

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

## Current Skill (Q=0.014) — your mutation base

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

- **Composite score**: 0.014
- **task_score** (E): 0.383
- **fitness_score**: 0.664  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.650

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1355 |
| descend_1 | 1.00 | 1.00 | 0.1242 |
| grasp_1 | 1.00 | 1.00 | 0.0131 |
| lift_1 | 1.00 | 1.00 | 0.0991 |
| approach_goal | 1.00 | 1.00 | 0.2516 |
| descend_goal | 1.00 | 0.33 | 0.0457 |
| release_1 | 1.00 | 1.00 | 0.0194 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, -0.014, 0.171) | (0.515, -0.017, 0.030)→(0.515, -0.017, 0.026) | 0.268→0.270 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.510, -0.014, 0.171)→(0.510, -0.016, 0.046) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.510, -0.016, 0.046)→(0.502, -0.016, 0.037) | (0.515, -0.017, 0.026)→(0.515, -0.016, 0.026) | 0.270→0.270 | 1.00 / 42.000 | 0.139 | 0.188 |
| lift_1 | lift | 1.00 / step_budget | (0.502, -0.016, 0.037)→(0.498, -0.016, 0.136) | (0.515, -0.016, 0.026)→(0.515, -0.016, 0.121) | 0.270→0.236 | 1.00 / 23.000 | 0.108 | 0.525 |
| approach_goal | approach | 1.00 / step_budget | (0.498, -0.016, 0.136)→(0.609, 0.171, 0.254) | (0.515, -0.016, 0.121)→(0.615, 0.171, 0.228) | 0.236→0.061 | 1.00 / 16.667 | 0.154 | 0.186 |
| descend_goal | descend | 1.00 / step_budget | (0.609, 0.171, 0.254)→(0.612, 0.176, 0.209) | (0.615, 0.171, 0.228)→(0.620, 0.171, 0.161) | 0.061→0.023 | 0.33 / 10.000 | 0.029 | 0.305 |
| release_1 | release | 1.00 / step_budget | (0.612, 0.176, 0.209)→(0.607, 0.175, 0.227) | (0.620, 0.171, 0.161)→(0.626, 0.172, 0.020) | 0.023→0.150 | 1.00 / 3.333 | 0.145 | 1.741 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.532
- phase_score: 0.479
- phase_breakdown.reach_goal_score: 0.460
- phase_breakdown.lift_clearance_score: 0.469
- phase_breakdown.reach_object_score: 0.518
- grasp_place_fitness: 0.739

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.739
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.532
- **Median Q (composite search score)**: -0.009
- **K-run variance**: 0.0030
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.321


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.05814,"average_solve_count":258.0,"average_success_count":258.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_z":0.13077,"approach_1.speed":0.07099,"approach_goal.goal_approach_z":0.07756,"approach_goal.speed":0.05933,"descend_1.descend_z":0.00038,"descend_1.speed":0.19925,"descend_goal.goal_z_offset":0.01645,"descend_goal.speed":0.01426,"lift_1.lift_height":0.11516,"lift_1.speed":0.10325},"optimized_scores":{"best_composite_score":-0.03878,"best_fitness_score":0.61122,"best_task_score":0.27664},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":611.0,"contact_point_centroid":[0.62596,0.21144,-0.00416],"force_p95":0.89102,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.02495,"mean_force":0.20959,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60075,0.21809,0.24082]},{"body_a":"world","body_b":"grasp_target","contact_count":77.0,"contact_point_centroid":[0.53411,-0.01999,-0.00139],"force_p95":0.51656,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54678,"mean_force":0.11797,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52108,-0.02047,0.03628]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":117.0,"contact_point_centroid":[0.60896,0.23219,0.2611],"force_p95":0.24902,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3319,"mean_force":0.18021,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.6028,0.21419,0.26611]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4499.0,"contact_point_centroid":[0.52143,-0.00148,0.07935],"force_p95":0.11074,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32866,"mean_force":0.07383,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51858,-0.02042,0.07692]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4912.0,"contact_point_centroid":[0.52157,-0.03922,0.07757],"force_p95":0.10754,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30501,"mean_force":0.06932,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51861,-0.02042,0.07592]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":257.0,"contact_point_centroid":[0.60817,0.19792,0.25978],"force_p95":0.13895,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23984,"mean_force":0.07624,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.60283,0.21442,0.26454]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10216.0,"contact_point_centroid":[0.56131,0.1082,0.19312],"force_p95":0.15029,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20134,"mean_force":0.08945,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55621,0.0897,0.1929]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53705,-0.02113,-0.00207],"force_p95":0.14459,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1976,"mean_force":0.12854,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52361,-0.02052,0.03634]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11436.0,"contact_point_centroid":[0.56159,0.07252,0.19348],"force_p95":0.12101,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16005,"mean_force":0.0813,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55667,0.09087,0.19361]},{"body_a":"world","body_b":"grasp_target","contact_count":1020.0,"contact_point_centroid":[0.53702,-0.02132,-0.00187],"force_p95":0.13691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12311,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51269,-0.00847,0.24019]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4093.0,"contact_point_centroid":[0.52347,-0.00129,0.03769],"force_p95":0.07837,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13041,"mean_force":0.05185,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52241,-0.0205,0.03498]},{"body_a":"world","body_b":"grasp_target","contact_count":932.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5286,-0.01914,0.11214]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4933.0,"contact_point_centroid":[0.52343,-0.0396,0.03677],"force_p95":0.07048,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08066,"mean_force":0.04468,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52242,-0.0205,0.03498]}],"total_contact_groups":13},"final_pose_error":0.01954,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.62611,0.2114,0.016],"final_tcp_position":[0.60484,0.21963,0.24077],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":2.02495,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":256.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1020.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.52773,-0.01771,0.17783],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15214,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":233.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":932.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53134,-0.02064,0.04556],"tcp_start":[0.52773,-0.01771,0.17783],"tcp_to_object_dist_end":0.02036,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53692,-0.0205,0.02574],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31626,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.14032,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10826.0,"raw_peak_contact_force":0.1976,"tcp_end":[0.52238,-0.0205,0.03494],"tcp_start":[0.53134,-0.02064,0.04556],"tcp_to_object_dist_end":0.01721,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":316.0,"n_steps_budget":720.0,"object_pos_end":[0.53578,-0.02043,0.11688],"object_pos_start":[0.53692,-0.0205,0.02574],"object_to_goal_dist_end":0.27449,"object_to_goal_dist_start":0.31626,"object_z_max":0.11663,"peak_contact_force":0.10663,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":9488.0,"raw_peak_contact_force":0.54678,"subtask_id":"lift_clearance","tcp_end":[0.51838,-0.0204,0.13078],"tcp_start":[0.52238,-0.0205,0.03494],"tcp_to_object_dist_end":0.02227,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":13.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.60832,0.21371,0.24156],"object_pos_start":[0.53578,-0.02043,0.11688],"object_to_goal_dist_end":0.03698,"object_to_goal_dist_start":0.27449,"object_z_max":0.24146,"peak_contact_force":0.20134,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":21652.0,"raw_peak_contact_force":0.20134,"subtask_id":"reach_goal","tcp_end":[0.60305,0.21352,0.26805],"tcp_start":[0.51838,-0.0204,0.13078],"tcp_to_object_dist_end":0.02701,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":72.0,"n_steps_budget":1000.0,"object_pos_end":[0.61768,0.21039,0.16882],"object_pos_start":[0.60832,0.21371,0.24156],"object_to_goal_dist_end":0.04295,"object_to_goal_dist_start":0.03698,"object_z_max":0.24156,"peak_contact_force":0.0,"phase_name":"descend_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":374.0,"raw_peak_contact_force":0.3319,"subtask_id":"reach_goal","tcp_end":[0.60484,0.21963,0.24077],"tcp_start":[0.60305,0.21352,0.26805],"tcp_to_object_dist_end":0.07366,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.62611,0.2114,0.016],"object_pos_start":[0.61768,0.21039,0.16882],"object_to_goal_dist_end":0.19276,"object_to_goal_dist_start":0.04295,"object_z_max":0.16882,"peak_contact_force":0.12285,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":611.0,"raw_peak_contact_force":2.02495,"tcp_end":[0.60028,0.21785,0.25918],"tcp_start":[0.60484,0.21963,0.24077],"tcp_to_object_dist_end":0.24463,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.30769,"average_solve_count":221.0,"average_success_count":221.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_z":0.12451,"approach_1.speed":0.11051,"approach_goal.goal_approach_z":0.09083,"approach_goal.speed":0.02423,"descend_1.descend_z":0.00169,"descend_1.speed":0.12014,"descend_goal.goal_z_offset":0.03028,"descend_goal.speed":0.0779,"lift_1.lift_height":0.11452,"lift_1.speed":0.09307},"optimized_scores":{"best_composite_score":-0.00855,"best_fitness_score":0.64145,"best_task_score":0.33938},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":569.0,"contact_point_centroid":[0.65088,0.15841,-0.00413],"force_p95":0.84672,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.96162,"mean_force":0.21513,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62253,0.15809,0.22583]},{"body_a":"world","body_b":"grasp_target","contact_count":84.0,"contact_point_centroid":[0.5432,-0.02763,-0.00139],"force_p95":0.46485,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.52775,"mean_force":0.11091,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52938,-0.02801,0.0372]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4473.0,"contact_point_centroid":[0.52992,-0.00901,0.07974],"force_p95":0.11249,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32151,"mean_force":0.07561,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52682,-0.02792,0.07731]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":147.0,"contact_point_centroid":[0.63141,0.1741,0.2438],"force_p95":0.2205,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30506,"mean_force":0.17093,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.62554,0.15604,0.24836]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4851.0,"contact_point_centroid":[0.53005,-0.04671,0.07792],"force_p95":0.10893,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3045,"mean_force":0.07163,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52686,-0.02792,0.07625]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":287.0,"contact_point_centroid":[0.63105,0.13965,0.24104],"force_p95":0.15716,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23718,"mean_force":0.08851,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.62572,0.15642,0.24573]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54564,-0.02902,-0.00211],"force_p95":0.15385,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21958,"mean_force":0.13095,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53192,-0.02809,0.03723]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8605.0,"contact_point_centroid":[0.57716,0.0777,0.18678],"force_p95":0.15001,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16833,"mean_force":0.09379,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.57156,0.05921,0.18619]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9613.0,"contact_point_centroid":[0.57749,0.04148,0.18693],"force_p95":0.12113,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15822,"mean_force":0.0855,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.57192,0.05979,0.18663]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4081.0,"contact_point_centroid":[0.53187,-0.00884,0.03852],"force_p95":0.07977,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14283,"mean_force":0.05191,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53071,-0.02805,0.03582]},{"body_a":"world","body_b":"grasp_target","contact_count":1068.0,"contact_point_centroid":[0.5456,-0.02923,-0.00188],"force_p95":0.1365,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12308,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51658,-0.01185,0.23641]},{"body_a":"world","body_b":"grasp_target","contact_count":916.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53662,-0.0264,0.10919]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4970.0,"contact_point_centroid":[0.53181,-0.04717,0.03759],"force_p95":0.07209,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07953,"mean_force":0.04459,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53071,-0.02805,0.03582]}],"total_contact_groups":13},"final_pose_error":0.01998,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.65111,0.15826,0.01599],"final_tcp_position":[0.62723,0.15938,0.22556],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":1.96162,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":268.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1068.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.5355,-0.0246,0.17095],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14536,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":229.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":916.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53969,-0.02829,0.04667],"tcp_start":[0.5355,-0.0246,0.17095],"tcp_to_object_dist_end":0.0215,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54552,-0.02815,0.02563],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26037,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.14798,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10851.0,"raw_peak_contact_force":0.21958,"tcp_end":[0.53068,-0.02805,0.03578],"tcp_start":[0.53969,-0.02829,0.04667],"tcp_to_object_dist_end":0.01798,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":322.0,"n_steps_budget":780.0,"object_pos_end":[0.54396,-0.02803,0.11589],"object_pos_start":[0.54552,-0.02815,0.02563],"object_to_goal_dist_end":0.22104,"object_to_goal_dist_start":0.26037,"object_z_max":0.11564,"peak_contact_force":0.10942,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":9408.0,"raw_peak_contact_force":0.52775,"subtask_id":"lift_clearance","tcp_end":[0.52658,-0.0279,0.13089],"tcp_start":[0.53068,-0.02805,0.03578],"tcp_to_object_dist_end":0.02296,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":14.0,"n_steps":888.0,"n_steps_budget":1000.0,"object_pos_end":[0.63039,0.15521,0.22597],"object_pos_start":[0.54396,-0.02803,0.11589],"object_to_goal_dist_end":0.05007,"object_to_goal_dist_start":0.22104,"object_z_max":0.22587,"peak_contact_force":0.15356,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":18218.0,"raw_peak_contact_force":0.16833,"subtask_id":"reach_goal","tcp_end":[0.62514,0.15499,0.25242],"tcp_start":[0.52658,-0.0279,0.13089],"tcp_to_object_dist_end":0.02696,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":56.0,"n_steps_budget":1000.0,"object_pos_end":[0.63862,0.1545,0.17915],"object_pos_start":[0.63039,0.15521,0.22597],"object_to_goal_dist_end":0.01213,"object_to_goal_dist_start":0.05007,"object_z_max":0.22598,"peak_contact_force":0.0,"phase_name":"descend_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":434.0,"raw_peak_contact_force":0.30506,"subtask_id":"reach_goal","tcp_end":[0.62723,0.15938,0.22556],"tcp_start":[0.62514,0.15499,0.25242],"tcp_to_object_dist_end":0.04804,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.65111,0.15826,0.01599],"object_pos_start":[0.63862,0.1545,0.17915],"object_to_goal_dist_end":0.1621,"object_to_goal_dist_start":0.01213,"object_z_max":0.17915,"peak_contact_force":0.12345,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":569.0,"raw_peak_contact_force":1.96162,"tcp_end":[0.62213,0.15794,0.24364],"tcp_start":[0.62723,0.15938,0.22556],"tcp_to_object_dist_end":0.22948,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.24345,"average_solve_count":267.0,"average_success_count":267.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_z":0.11315,"approach_1.speed":0.04593,"approach_goal.goal_approach_z":0.13355,"approach_goal.speed":0.04712,"descend_1.descend_z":0.00127,"descend_1.speed":0.09236,"descend_goal.goal_z_offset":0.01976,"descend_goal.speed":0.17324,"lift_1.lift_height":0.1254,"lift_1.speed":0.07147},"optimized_scores":{"best_composite_score":0.08888,"best_fitness_score":0.73888,"best_task_score":0.53151},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":143.0,"contact_point_centroid":[0.59505,0.14959,-0.00858],"force_p95":1.15549,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.23702,"mean_force":0.49151,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59766,0.14793,0.16898]},{"body_a":"world","body_b":"grasp_target","contact_count":73.0,"contact_point_centroid":[0.46032,-0.00042,-0.00137],"force_p95":0.44021,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.49905,"mean_force":0.12042,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45086,-0.00022,0.04026]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5856.0,"contact_point_centroid":[0.44939,0.0189,0.09211],"force_p95":0.09565,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30272,"mean_force":0.0611,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44847,-0.00023,0.08986]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6475.0,"contact_point_centroid":[0.44935,-0.01925,0.09017],"force_p95":0.09181,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29866,"mean_force":0.05629,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44847,-0.00023,0.08837]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":943.0,"contact_point_centroid":[0.60435,0.13012,0.15516],"force_p95":0.08691,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27853,"mean_force":0.05689,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60165,0.14911,0.15509]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2058.0,"contact_point_centroid":[0.60569,0.12804,0.19999],"force_p95":0.13214,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27835,"mean_force":0.08138,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.60127,0.14695,0.19861]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2169.0,"contact_point_centroid":[0.60563,0.16536,0.20117],"force_p95":0.12471,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27274,"mean_force":0.07364,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.60117,0.14684,0.20034]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":971.0,"contact_point_centroid":[0.60371,0.16809,0.15423],"force_p95":0.09099,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25099,"mean_force":0.05627,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60164,0.1491,0.15507]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10171.0,"contact_point_centroid":[0.52906,0.05597,0.19445],"force_p95":0.10797,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18871,"mean_force":0.07584,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52489,0.07461,0.19368]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10271.0,"contact_point_centroid":[0.53134,0.09481,0.19608],"force_p95":0.10375,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16959,"mean_force":0.07416,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52654,0.07618,0.19475]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.46285,-9e-05,-0.00202],"force_p95":0.12874,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14654,"mean_force":0.12445,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.453,-0.00019,0.04012]},{"body_a":"world","body_b":"grasp_target","contact_count":1108.0,"contact_point_centroid":[0.46286,-7e-05,-0.00188],"force_p95":0.13648,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12307,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48304,-4e-05,0.23338]},{"body_a":"world","body_b":"grasp_target","contact_count":904.0,"contact_point_centroid":[0.46286,-7e-05,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.46202,-9e-05,0.10542]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4864.0,"contact_point_centroid":[0.45212,0.019,0.041],"force_p95":0.06806,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08906,"mean_force":0.04481,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.45194,-0.0002,0.03911]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4848.0,"contact_point_centroid":[0.45215,-0.01939,0.04101],"force_p95":0.06799,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08732,"mean_force":0.04477,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.45194,-0.0002,0.03911]}],"total_contact_groups":15},"final_pose_error":0.01965,"key_states":{"actual_goal_position":[0.61015,0.15287,0.12219],"final_object_position":[0.60014,0.14714,0.02809],"final_tcp_position":[0.60413,0.14967,0.16038],"realised_goal_position":[0.61015,0.15287,0.12219],"realised_object_initial_position":[0.46286,-7e-05,0.03]},"peak_contact_force":1.23702,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":278.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.03],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.23148,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1108.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.46572,-7e-05,0.16276],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13677,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":226.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":904.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.45987,-0.00011,0.04706],"tcp_start":[0.46572,-7e-05,0.16276],"tcp_to_object_dist_end":0.02125,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46275,-0.00017,0.02591],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.23327,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.1285,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11512.0,"raw_peak_contact_force":0.14654,"tcp_end":[0.45191,-0.0002,0.03908],"tcp_start":[0.45987,-0.00011,0.04706],"tcp_to_object_dist_end":0.01706,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":334.0,"n_steps_budget":1000.0,"object_pos_end":[0.46421,-6e-05,0.12942],"object_pos_start":[0.46275,-0.00017,0.02591],"object_to_goal_dist_end":0.21151,"object_to_goal_dist_start":0.23327,"object_z_max":0.12913,"peak_contact_force":0.10661,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":12404.0,"raw_peak_contact_force":0.49905,"subtask_id":"lift_clearance","tcp_end":[0.44825,-0.00022,0.1451],"tcp_start":[0.45191,-0.0002,0.03908],"tcp_to_object_dist_end":0.02237,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":807.0,"n_steps_budget":1000.0,"object_pos_end":[0.60651,0.1441,0.21728],"object_pos_start":[0.46421,-6e-05,0.12942],"object_to_goal_dist_end":0.09556,"object_to_goal_dist_start":0.21151,"object_z_max":0.21718,"peak_contact_force":0.10679,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":20442.0,"raw_peak_contact_force":0.18871,"subtask_id":"reach_goal","tcp_end":[0.59881,0.14402,0.24186],"tcp_start":[0.44825,-0.00022,0.1451],"tcp_to_object_dist_end":0.02576,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":146.0,"n_steps_budget":1000.0,"object_pos_end":[0.60431,0.14908,0.13425],"object_pos_start":[0.60651,0.1441,0.21728],"object_to_goal_dist_end":0.01392,"object_to_goal_dist_start":0.09556,"object_z_max":0.2173,"peak_contact_force":0.08779,"phase_name":"descend_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4227.0,"raw_peak_contact_force":0.27835,"subtask_id":"reach_goal","tcp_end":[0.60413,0.14967,0.16038],"tcp_start":[0.59881,0.14402,0.24186],"tcp_to_object_dist_end":0.02614,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60014,0.14714,0.02809],"object_pos_start":[0.60431,0.14908,0.13425],"object_to_goal_dist_end":0.09481,"object_to_goal_dist_start":0.01392,"object_z_max":0.13425,"peak_contact_force":0.18819,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2057.0,"raw_peak_contact_force":1.23702,"tcp_end":[0.59758,0.14791,0.17959],"tcp_start":[0.60413,0.14967,0.16038],"tcp_to_object_dist_end":0.15153,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```