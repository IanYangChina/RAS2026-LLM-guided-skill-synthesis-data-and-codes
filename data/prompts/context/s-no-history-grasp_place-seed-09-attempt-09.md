## Search State

- **Seed**: 9
- **Iteration**: 10 / 15

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

## Current Skill (Q=-0.034) — your mutation base

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

- **Composite score**: -0.034
- **task_score** (E): 0.386
- **fitness_score**: 0.666  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.700

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1360 |
| descend_1 | 1.00 | 1.00 | 0.1244 |
| grasp_1 | 1.00 | 1.00 | 0.0126 |
| lift_1 | 1.00 | 1.00 | 0.1418 |
| approach_goal | 1.00 | 1.00 | 0.2429 |
| descend_goal | 1.00 | 0.67 | 0.0536 |
| release_1 | 1.00 | 1.00 | 0.0198 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, -0.015, 0.170) | (0.515, -0.017, 0.030)→(0.515, -0.017, 0.026) | 0.268→0.270 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.510, -0.015, 0.170)→(0.510, -0.016, 0.046) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.510, -0.016, 0.046)→(0.502, -0.016, 0.037) | (0.515, -0.017, 0.026)→(0.515, -0.016, 0.026) | 0.270→0.270 | 1.00 / 42.000 | 0.136 | 0.176 |
| lift_1 | lift | 1.00 / step_budget | (0.502, -0.016, 0.037)→(0.498, -0.016, 0.178) | (0.515, -0.016, 0.026)→(0.506, -0.016, 0.162) | 0.270→0.234 | 1.00 / 38.000 | 0.077 | 0.474 |
| approach_goal | approach | 1.00 / step_budget | (0.498, -0.016, 0.178)→(0.609, 0.171, 0.277) | (0.506, -0.016, 0.162)→(0.616, 0.171, 0.254) | 0.234→0.087 | 1.00 / 30.667 | 0.094 | 0.153 |
| descend_goal | descend | 1.00 / step_budget | (0.610, 0.173, 0.267)→(0.612, 0.178, 0.214) | (0.616, 0.171, 0.254)→(0.618, 0.174, 0.182) | 0.087→0.021 | 0.67 / 29.000 | 0.046 | 0.235 |
| release_1 | release | 1.00 / step_budget | (0.612, 0.178, 0.214)→(0.607, 0.176, 0.233) | (0.619, 0.173, 0.167)→(0.614, 0.169, 0.022) | 0.031→0.148 | 1.00 / 2.667 | 0.181 | 1.819 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.526
- phase_score: 0.379
- phase_breakdown.reach_goal_score: 0.214
- phase_breakdown.lift_clearance_score: 0.673
- phase_breakdown.reach_object_score: 0.458
- grasp_place_fitness: 0.737

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.737
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.526
- **Median Q (composite search score)**: -0.052
- **K-run variance**: 0.0028
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.342


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.34746,"average_solve_count":236.0,"average_success_count":236.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_z":0.1331,"approach_1.speed":0.14437,"approach_goal.goal_approach_z":0.10124,"approach_goal.speed":0.0928,"descend_1.descend_z":0.00513,"descend_1.speed":0.0685,"descend_goal.goal_z_offset":0.04712,"descend_goal.speed":0.0693,"lift_1.lift_height":0.16564,"lift_1.speed":0.05071,"release_1.release_duration":1.24771},"optimized_scores":{"best_composite_score":-0.0887,"best_fitness_score":0.6113,"best_task_score":0.27585},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":630.0,"contact_point_centroid":[0.62318,0.20505,-0.00411],"force_p95":0.88957,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.33814,"mean_force":0.21432,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60197,0.22059,0.26199]},{"body_a":"world","body_b":"grasp_target","contact_count":110.0,"contact_point_centroid":[0.53243,-0.02046,-0.00132],"force_p95":0.49364,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.52688,"mean_force":0.13094,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52138,-0.02066,0.03617]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":258.0,"contact_point_centroid":[0.61019,0.20057,0.28222],"force_p95":0.21451,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34368,"mean_force":0.13867,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.60422,0.21727,0.28742]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15385.0,"contact_point_centroid":[0.5194,-0.00148,0.11271],"force_p95":0.07985,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30589,"mean_force":0.05622,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51863,-0.02059,0.11028]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":153.0,"contact_point_centroid":[0.60963,0.23491,0.28578],"force_p95":0.24291,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30502,"mean_force":0.1546,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.60401,0.21655,0.2912]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16276.0,"contact_point_centroid":[0.51939,-0.03964,0.11054],"force_p95":0.07751,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28968,"mean_force":0.05384,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51863,-0.02059,0.10846]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13280.0,"contact_point_centroid":[0.56001,0.07211,0.23583],"force_p95":0.09583,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25508,"mean_force":0.06382,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55755,0.09098,0.23471]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13272.0,"contact_point_centroid":[0.55928,0.10793,0.23471],"force_p95":0.10083,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24839,"mean_force":0.06293,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55679,0.08902,0.23372]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53704,-0.02116,-0.00206],"force_p95":0.14048,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18272,"mean_force":0.12749,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5239,-0.0207,0.03625]},{"body_a":"world","body_b":"grasp_target","contact_count":1196.0,"contact_point_centroid":[0.53702,-0.02132,-0.00189],"force_p95":0.13615,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12304,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51327,-0.00893,0.23796]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4100.0,"contact_point_centroid":[0.52365,-0.00147,0.03759],"force_p95":0.07772,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1278,"mean_force":0.05183,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52269,-0.02068,0.03487]},{"body_a":"world","body_b":"grasp_target","contact_count":1248.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52879,-0.01959,0.11009]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4914.0,"contact_point_centroid":[0.52363,-0.03977,0.03666],"force_p95":0.06982,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08099,"mean_force":0.04471,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52269,-0.02068,0.03487]}],"total_contact_groups":13},"final_pose_error":0.01026,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.62297,0.20488,0.016],"final_tcp_position":[0.6054,0.22206,0.26151],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":2.33814,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":300.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1196.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.52876,-0.01843,0.17518],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14942,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":312.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1248.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53132,-0.02083,0.04496],"tcp_start":[0.52876,-0.01843,0.17518],"tcp_to_object_dist_end":0.01979,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53692,-0.02064,0.02578],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31635,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.137,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10814.0,"raw_peak_contact_force":0.18272,"tcp_end":[0.52266,-0.02068,0.03483],"tcp_start":[0.53132,-0.02083,0.04496],"tcp_to_object_dist_end":0.01689,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":849.0,"n_steps_budget":1000.0,"object_pos_end":[0.52739,-0.02055,0.16967],"object_pos_start":[0.53692,-0.02064,0.02578],"object_to_goal_dist_end":0.26449,"object_to_goal_dist_start":0.31635,"object_z_max":0.16951,"peak_contact_force":0.07932,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":31771.0,"raw_peak_contact_force":0.52688,"subtask_id":"lift_clearance","tcp_end":[0.51902,-0.02059,0.18592],"tcp_start":[0.52266,-0.02068,0.03483],"tcp_to_object_dist_end":0.01829,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":862.0,"n_steps_budget":1000.0,"object_pos_end":[0.61566,0.21585,0.27092],"object_pos_start":[0.52739,-0.02055,0.16967],"object_to_goal_dist_end":0.06484,"object_to_goal_dist_start":0.26449,"object_z_max":0.27085,"peak_contact_force":0.13884,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":26552.0,"raw_peak_contact_force":0.25508,"tcp_end":[0.60394,0.21546,0.29428],"tcp_start":[0.51902,-0.02059,0.18592],"tcp_to_object_dist_end":0.02614,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":88.0,"n_steps_budget":1000.0,"object_pos_end":[0.62154,0.21082,0.21095],"object_pos_start":[0.61566,0.21585,0.27092],"object_to_goal_dist_end":0.02062,"object_to_goal_dist_start":0.06484,"object_z_max":0.27092,"peak_contact_force":0.0,"phase_name":"descend_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":411.0,"raw_peak_contact_force":0.34368,"subtask_id":"reach_goal","tcp_end":[0.6054,0.22206,0.26151],"tcp_start":[0.60572,0.22142,0.26698],"tcp_to_object_dist_end":0.05425,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.62297,0.20488,0.016],"object_pos_start":[0.62316,0.20703,0.16506],"object_to_goal_dist_end":0.19319,"object_to_goal_dist_start":0.04887,"object_z_max":0.16506,"peak_contact_force":0.12296,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":630.0,"raw_peak_contact_force":2.33814,"subtask_id":"reach_goal","tcp_end":[0.60155,0.22034,0.28054],"tcp_start":[0.6054,0.22206,0.26151],"tcp_to_object_dist_end":0.26585,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.29044,"average_solve_count":272.0,"average_success_count":272.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_z":0.12569,"approach_1.speed":0.08462,"approach_goal.goal_approach_z":0.11895,"approach_goal.speed":0.0466,"descend_1.descend_z":0.00843,"descend_1.speed":0.0926,"descend_goal.goal_z_offset":0.01194,"descend_goal.speed":0.08174,"lift_1.lift_height":0.15896,"lift_1.speed":0.0453,"release_1.release_duration":1.05241},"optimized_scores":{"best_composite_score":-0.05171,"best_fitness_score":0.64829,"best_task_score":0.3555},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":117.0,"contact_point_centroid":[0.61843,0.16451,-0.01087],"force_p95":1.42859,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.72898,"mean_force":0.64212,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62249,0.15982,0.21183]},{"body_a":"world","body_b":"grasp_target","contact_count":117.0,"contact_point_centroid":[0.54081,-0.02778,-0.00136],"force_p95":0.44549,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.47113,"mean_force":0.12733,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52954,-0.02825,0.03881]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15241.0,"contact_point_centroid":[0.52769,-0.00904,0.11277],"force_p95":0.08095,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28395,"mean_force":0.0564,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5268,-0.02815,0.11037]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16111.0,"contact_point_centroid":[0.52769,-0.04719,0.11007],"force_p95":0.07839,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27559,"mean_force":0.05421,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52681,-0.02815,0.10802]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54563,-0.02905,-0.00209],"force_p95":0.14751,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20455,"mean_force":0.1293,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53215,-0.02832,0.039]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2912.0,"contact_point_centroid":[0.62838,0.17657,0.24291],"force_p95":0.09921,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19311,"mean_force":0.06455,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.62603,0.1576,0.24215]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3090.0,"contact_point_centroid":[0.62853,0.13867,0.24218],"force_p95":0.10089,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17666,"mean_force":0.06305,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.62608,0.15771,0.24084]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1331.0,"contact_point_centroid":[0.62636,0.14183,0.19834],"force_p95":0.06531,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15082,"mean_force":0.04039,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62603,0.16098,0.19733]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1237.0,"contact_point_centroid":[0.62667,0.18023,0.19821],"force_p95":0.07075,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14185,"mean_force":0.04343,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.626,0.16097,0.19727]},{"body_a":"world","body_b":"grasp_target","contact_count":1400.0,"contact_point_centroid":[0.5456,-0.02923,-0.0019],"force_p95":0.1356,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12298,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51701,-0.01241,0.23382]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4093.0,"contact_point_centroid":[0.53201,-0.00908,0.04029],"force_p95":0.0789,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13565,"mean_force":0.05186,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53093,-0.02829,0.03757]},{"body_a":"world","body_b":"grasp_target","contact_count":1100.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53694,-0.02701,0.1076]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12716.0,"contact_point_centroid":[0.57663,0.08212,0.2309],"force_p95":0.08824,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10474,"mean_force":0.06146,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.57457,0.06309,0.2292]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14663.0,"contact_point_centroid":[0.57588,0.04319,0.22952],"force_p95":0.0793,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10048,"mean_force":0.05401,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.57399,0.06204,0.22861]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4942.0,"contact_point_centroid":[0.53197,-0.04739,0.03935],"force_p95":0.07112,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0794,"mean_force":0.04464,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53093,-0.02829,0.03758]}],"total_contact_groups":15},"final_pose_error":0.01466,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.62502,0.15524,0.02229],"final_tcp_position":[0.62798,0.16142,0.20224],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":1.72898,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":351.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1400.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.53651,-0.02558,0.16695],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14127,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":275.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1100.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53964,-0.02854,0.04803],"tcp_start":[0.53651,-0.02558,0.16695],"tcp_to_object_dist_end":0.02281,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54551,-0.02835,0.0257],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26048,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.14288,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10835.0,"raw_peak_contact_force":0.20455,"tcp_end":[0.5309,-0.02829,0.03754],"tcp_start":[0.53964,-0.02854,0.04803],"tcp_to_object_dist_end":0.01881,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":845.0,"n_steps_budget":1000.0,"object_pos_end":[0.53501,-0.02818,0.16331],"object_pos_start":[0.54551,-0.02835,0.0257],"object_to_goal_dist_end":0.2169,"object_to_goal_dist_start":0.26048,"object_z_max":0.16316,"peak_contact_force":0.07931,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":31469.0,"raw_peak_contact_force":0.47113,"subtask_id":"lift_clearance","tcp_end":[0.52719,-0.02815,0.18209],"tcp_start":[0.5309,-0.02829,0.03754],"tcp_to_object_dist_end":0.02034,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":35.0,"n_steps":813.0,"n_steps_budget":1000.0,"object_pos_end":[0.63,0.15412,0.25754],"object_pos_start":[0.53501,-0.02818,0.16331],"object_to_goal_dist_end":0.08139,"object_to_goal_dist_start":0.2169,"object_z_max":0.25744,"peak_contact_force":0.07508,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":27379.0,"raw_peak_contact_force":0.10474,"tcp_end":[0.62507,0.1541,0.28111],"tcp_start":[0.52719,-0.02815,0.18209],"tcp_to_object_dist_end":0.02408,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":167.0,"n_steps_budget":1000.0,"object_pos_end":[0.62737,0.16095,0.17763],"object_pos_start":[0.63,0.15412,0.25754],"object_to_goal_dist_end":0.0068,"object_to_goal_dist_start":0.08139,"object_z_max":0.25754,"peak_contact_force":0.07044,"phase_name":"descend_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":6002.0,"raw_peak_contact_force":0.19311,"subtask_id":"reach_goal","tcp_end":[0.62798,0.16142,0.20224],"tcp_start":[0.62507,0.1541,0.28111],"tcp_to_object_dist_end":0.02462,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.62502,0.15524,0.02229],"object_pos_start":[0.62737,0.16095,0.17763],"object_to_goal_dist_end":0.15514,"object_to_goal_dist_start":0.0068,"object_z_max":0.17763,"peak_contact_force":0.27986,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2685.0,"raw_peak_contact_force":1.72898,"subtask_id":"reach_goal","tcp_end":[0.62245,0.15981,0.22065],"tcp_start":[0.62798,0.16142,0.20224],"tcp_to_object_dist_end":0.19844,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.98201,"average_solve_count":278.0,"average_success_count":278.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_z":0.12429,"approach_1.speed":0.12648,"approach_goal.goal_approach_z":0.14557,"approach_goal.speed":0.0588,"descend_1.descend_z":0.00477,"descend_1.speed":0.18616,"descend_goal.goal_z_offset":0.04318,"descend_goal.speed":0.06821,"lift_1.lift_height":0.14419,"lift_1.speed":0.02369,"release_1.release_duration":0.55965},"optimized_scores":{"best_composite_score":0.03726,"best_fitness_score":0.73726,"best_task_score":0.52573},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":195.0,"contact_point_centroid":[0.58789,0.14787,-0.00713],"force_p95":1.28195,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.38886,"mean_force":0.37218,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59814,0.14812,0.18793]},{"body_a":"world","body_b":"grasp_target","contact_count":113.0,"contact_point_centroid":[0.45882,-0.00019,-0.00139],"force_p95":0.37161,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.42282,"mean_force":0.1534,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45023,-0.00022,0.03842]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13220.0,"contact_point_centroid":[0.44793,0.01891,0.10348],"force_p95":0.07298,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24668,"mean_force":0.05113,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44773,-0.00023,0.1016]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13258.0,"contact_point_centroid":[0.44796,-0.01937,0.1033],"force_p95":0.07365,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22118,"mean_force":0.05107,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44774,-0.00023,0.10141]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1310.0,"contact_point_centroid":[0.60231,0.13006,0.17722],"force_p95":0.06631,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16911,"mean_force":0.04132,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60201,0.14929,0.17415]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3621.0,"contact_point_centroid":[0.60081,0.16557,0.21978],"force_p95":0.07978,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16904,"mean_force":0.05163,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.60067,0.14652,0.21799]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1433.0,"contact_point_centroid":[0.60237,0.16856,0.17668],"force_p95":0.06644,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15854,"mean_force":0.0381,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60195,0.14927,0.17401]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3321.0,"contact_point_centroid":[0.60059,0.12744,0.21894],"force_p95":0.08563,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.155,"mean_force":0.05508,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.6008,0.14663,0.21677]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.46285,-4e-05,-0.00202],"force_p95":0.12805,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14167,"mean_force":0.12436,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.45248,-0.00019,0.03853]},{"body_a":"world","body_b":"grasp_target","contact_count":1196.0,"contact_point_centroid":[0.46286,-7e-05,-0.00189],"force_p95":0.13615,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12304,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48236,-5e-05,0.23569]},{"body_a":"world","body_b":"grasp_target","contact_count":1136.0,"contact_point_centroid":[0.46286,-7e-05,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.46096,-9e-05,0.10708]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16493.0,"contact_point_centroid":[0.52368,0.05453,0.21224],"force_p95":0.0673,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09935,"mean_force":0.04618,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52377,0.07362,0.21012]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4389.0,"contact_point_centroid":[0.45133,0.01909,0.03956],"force_p95":0.07395,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09441,"mean_force":0.04934,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.45141,-0.00021,0.0375]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15017.0,"contact_point_centroid":[0.52293,0.09196,0.21199],"force_p95":0.07416,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09058,"mean_force":0.05018,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52287,0.07277,0.2096]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5332.0,"contact_point_centroid":[0.45084,-0.01929,0.03909],"force_p95":0.06282,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08779,"mean_force":0.04089,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.45141,-0.00021,0.0375]}],"total_contact_groups":15},"final_pose_error":0.01488,"key_states":{"actual_goal_position":[0.61015,0.15287,0.12219],"final_object_position":[0.59444,0.14765,0.02717],"final_tcp_position":[0.60407,0.14976,0.17859],"realised_goal_position":[0.61015,0.15287,0.12219],"realised_object_initial_position":[0.46286,-7e-05,0.03]},"peak_contact_force":1.38886,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":300.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.03],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.23148,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1196.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.46471,-8e-05,0.16896],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14296,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":284.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1136.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.45911,-0.00011,0.04508],"tcp_start":[0.46471,-8e-05,0.16896],"tcp_to_object_dist_end":0.01942,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46275,-0.0,0.02592],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.23316,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12812,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11521.0,"raw_peak_contact_force":0.14167,"tcp_end":[0.45139,-0.00021,0.03747],"tcp_start":[0.45911,-0.00011,0.04508],"tcp_to_object_dist_end":0.01621,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":662.0,"n_steps_budget":1000.0,"object_pos_end":[0.45551,-0.00023,0.15181],"object_pos_start":[0.46275,-0.0,0.02592],"object_to_goal_dist_end":0.21961,"object_to_goal_dist_start":0.23316,"object_z_max":0.15162,"peak_contact_force":0.07252,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":26591.0,"raw_peak_contact_force":0.42282,"subtask_id":"lift_clearance","tcp_end":[0.44784,-0.00022,0.1671],"tcp_start":[0.45139,-0.00021,0.03747],"tcp_to_object_dist_end":0.0171,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":775.0,"n_steps_budget":1000.0,"object_pos_end":[0.60331,0.14388,0.23495],"object_pos_start":[0.45551,-0.00023,0.15181],"object_to_goal_dist_end":0.11333,"object_to_goal_dist_start":0.21961,"object_z_max":0.23486,"peak_contact_force":0.06924,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":31510.0,"raw_peak_contact_force":0.09935,"tcp_end":[0.59871,0.14383,0.25428],"tcp_start":[0.44784,-0.00022,0.1671],"tcp_to_object_dist_end":0.01987,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":171.0,"n_steps_budget":1000.0,"object_pos_end":[0.60561,0.14957,0.1581],"object_pos_start":[0.60331,0.14388,0.23495],"object_to_goal_dist_end":0.03635,"object_to_goal_dist_start":0.11333,"object_z_max":0.23495,"peak_contact_force":0.06766,"phase_name":"descend_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":6942.0,"raw_peak_contact_force":0.16904,"subtask_id":"reach_goal","tcp_end":[0.60407,0.14976,0.17859],"tcp_start":[0.59871,0.14383,0.25428],"tcp_to_object_dist_end":0.02055,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59444,0.14765,0.02717],"object_pos_start":[0.60561,0.14957,0.1581],"object_to_goal_dist_end":0.09645,"object_to_goal_dist_start":0.03635,"object_z_max":0.1581,"peak_contact_force":0.13988,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2938.0,"raw_peak_contact_force":1.38886,"subtask_id":"reach_goal","tcp_end":[0.59808,0.14811,0.19828],"tcp_start":[0.60407,0.14976,0.17859],"tcp_to_object_dist_end":0.17114,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```