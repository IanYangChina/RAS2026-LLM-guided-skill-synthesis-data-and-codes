## Search State

- **Seed**: 1
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | admittance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.5609 | 1.00 | ❌ rejected |
| 13 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.5282 | 0.93 | ❌ rejected |
| 12 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | admittance_control | position_control | admittance_control | admittance_control | admittance_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 7 | 0.1452 | 0.20 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | admittance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.3717 | 0.72 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.4772 | 0.84 | ❌ rejected |

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

- Task name: grasp_place
- Frozen realised-scene SHA-256: `a2ed2c4162d37489f2d2d0fa0373774d72c951d58f2469e0ba2d602ff46b6cfb`
- Frozen object start: [0.5011821624700257, 0.045046369632593536, 0.03]
- Frozen task target: [0.5644159612719634, 0.2448649447137244, 0.1467747178015728]
- Goal object position: (0.5644159612719634, 0.2448649447137244, 0.1467747178015728)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5644159612719634, 0.2448649447137244, 0.1467747178015728)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5011821624700257, 0.045046369632593536, 0.03)
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
  frozen_object_start: [0.5012, 0.045, 0.03]
  frozen_task_target: [0.5644, 0.2449, 0.1468]
  frozen_object_starts: {'grasp_target': [0.5011821624700257, 0.045046369632593536, 0.03]}
  frozen_targets: {'place_target': [0.5644159612719634, 0.2448649447137244, 0.1467747178015728]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: a2ed2c4162d37489f2d2d0fa0373774d72c951d58f2469e0ba2d602ff46b6cfb

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
| `object` | offset from object initial position (0.5011821624700257, 0.045046369632593536, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5644159612719634, 0.2448649447137244, 0.1467747178015728) | final destination targets |
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

## Current Skill (Q=0.561) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: subtask_approach
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.2
- id: subtask_lift
  anchor: object
  target_entity: object
  offset:
  - 0.0
  - 0.0
  - 0.2
  weight: 0.3
- id: subtask_place
  target_entity: object
  metric: goal_progress
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
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.12
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.12
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: subtask_approach
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.01
    tolerance: 0.008
    orientation:
      mode: keep_current
  parameters:
    depth:
      type: scalar
      range:
      - 0.0
      - 0.05
      default: 0.01
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: subtask_approach
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
- id: lift_1
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.25
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.15
      - 0.4
      default: 0.25
      binds_to:
      - path: target.offset.z
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.03
      - 0.15
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: subtask_lift
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
    approach_goal_offset_z:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
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
    tolerance: 0.015
    orientation:
      mode: keep_current
  parameters:
    place_offset_z:
      type: scalar
      range:
      - -0.03
      - 0.05
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: subtask_place

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.12], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.01], tolerance=0.008
  - orientation: mode=keep_current
  - parameter_bindings:
    - depth: status=consumed; consumers=target.offset.z (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **lift_1** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.25], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
- **approach_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_goal_offset_z: status=consumed; consumers=target.offset.z (replace)
- **descend_goal** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_offset_z: status=consumed; consumers=target.offset.z (replace)

## Design Metrics

- **Composite score**: 0.561
- **task_score** (E): 1.000
- **fitness_score**: 0.981  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.420

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0766 |
| descend_1 | 1.00 | 1.00 | 0.2007 |
| grasp_1 | 1.00 | 1.00 | 0.0110 |
| lift_1 | 1.00 | 1.00 | 0.2374 |
| approach_goal | 1.00 | 1.00 | 0.2424 |
| descend_goal | 1.00 | 1.00 | 0.0734 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.488, 0.006, 0.234) | (0.479, -0.000, 0.030)→(0.479, -0.000, 0.026) | 0.276→0.278 | 1.00 / 4.000 | 0.127 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.488, 0.006, 0.234)→(0.474, -0.000, 0.034) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 4.000 | 0.123 | 0.126 |
| grasp_1 | grasp | 1.00 / step_budget | (0.474, -0.000, 0.034)→(0.467, -0.001, 0.027) | (0.479, -0.000, 0.026)→(0.479, -0.001, 0.026) | 0.278→0.278 | 1.00 / 45.000 | 0.148 | 0.237 |
| lift_1 | lift | 1.00 / step_budget | (0.467, -0.001, 0.027)→(0.475, -0.001, 0.264) | (0.479, -0.001, 0.026)→(0.486, -0.001, 0.257) | 0.278→0.269 | 1.00 / 40.667 | 0.075 | 0.645 |
| approach_goal | approach | 1.00 / step_budget | (0.475, -0.001, 0.264)→(0.598, 0.190, 0.232) | (0.486, -0.001, 0.257)→(0.606, 0.190, 0.219) | 0.269→0.071 | 1.00 / 39.000 | 0.079 | 0.114 |
| descend_goal | descend | 1.00 / step_budget | (0.598, 0.190, 0.232)→(0.602, 0.199, 0.159) | (0.606, 0.190, 0.219)→(0.604, 0.199, 0.145) | 0.071→0.012 | 1.00 / 38.667 | 0.079 | 0.157 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.528
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 1.000
- phase_score: 0.486
- phase_breakdown.subtask_approach_score: 0.150
- phase_breakdown.subtask_lift_score: 0.176
- phase_breakdown.subtask_place_score: 0.806
- grasp_place_fitness: 0.982

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.982
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.562
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.412


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `8110053be9072e64e15984c6424e4a66fe19af4b6c37a60139a43e94cc34ad53`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `46ef03f7b16015a0d14bf26d80c05d326b92c02b0bf759391930f5ab902d1933`; realized-scene SHA-256: `a2ed2c4162d37489f2d2d0fa0373774d72c951d58f2469e0ba2d602ff46b6cfb`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50118,0.04505,0.03]},{"name":"goal","value":[0.56442,0.24486,0.14677]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.50118,0.04505,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.56442,0.24486,0.14677]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.46,"average_solve_count":250.0,"average_success_count":250.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.07174,"approach_goal.approach_goal_offset_z":0.11462,"descend_1.depth":0.00143,"descend_goal.place_offset_z":-0.00584,"lift_1.lift_height":0.23014,"lift_1.lift_speed":0.03436},"optimized_scores":{"best_composite_score":0.55925,"best_fitness_score":0.97925,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":92.0,"contact_point_centroid":[0.49708,0.04247,-0.00159],"force_p95":0.60448,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62997,"mean_force":0.23747,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48709,0.04308,0.02602]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15686.0,"contact_point_centroid":[0.49048,0.06199,0.13028],"force_p95":0.07344,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29068,"mean_force":0.04995,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49067,0.04286,0.12873]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14887.0,"contact_point_centroid":[0.49072,0.02368,0.13294],"force_p95":0.07589,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27355,"mean_force":0.05143,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4908,0.04286,0.13076]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50125,0.04462,-0.00217],"force_p95":0.17334,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.26328,"mean_force":0.13609,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48928,0.0433,0.02619]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3723.0,"contact_point_centroid":[0.55773,0.21524,0.20355],"force_p95":0.09839,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16161,"mean_force":0.06133,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.55782,0.23461,0.20169]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3778.0,"contact_point_centroid":[0.48918,0.02401,0.02798],"force_p95":0.08598,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15021,"mean_force":0.05525,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48811,0.0432,0.02497]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4567.0,"contact_point_centroid":[0.5578,0.25313,0.2051],"force_p95":0.07614,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14493,"mean_force":0.04807,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.55775,0.2344,0.20354]},{"body_a":"world","body_b":"grasp_target","contact_count":1392.0,"contact_point_centroid":[0.50118,0.04505,-0.0019],"force_p95":0.1356,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12298,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49823,0.01903,0.2113]},{"body_a":"world","body_b":"grasp_target","contact_count":1284.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49551,0.04149,0.07569]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9179.0,"contact_point_centroid":[0.52684,0.11661,0.24414],"force_p95":0.08783,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1065,"mean_force":0.06001,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52608,0.13581,0.242]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11619.0,"contact_point_centroid":[0.52706,0.15704,0.24333],"force_p95":0.07356,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10139,"mean_force":0.04768,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52681,0.1381,0.2422]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4964.0,"contact_point_centroid":[0.48875,0.06236,0.02681],"force_p95":0.07627,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08776,"mean_force":0.04546,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48812,0.0432,0.02498]}],"total_contact_groups":12},"final_pose_error":0.01497,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.55906,0.23971,0.14145],"final_tcp_position":[0.55975,0.24034,0.15442],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":0.62997,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":349.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1392.0,"raw_peak_contact_force":0.13845,"subtask_id":"subtask_approach","tcp_end":[0.49771,0.03928,0.12041],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.09463,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":321.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1284.0,"raw_peak_contact_force":0.12263,"subtask_id":"subtask_approach","tcp_end":[0.49616,0.04393,0.03346],"tcp_start":[0.49771,0.03928,0.12041],"tcp_to_object_dist_end":0.00905,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50107,0.0432,0.02544],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24373,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.16072,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10542.0,"raw_peak_contact_force":0.26328,"tcp_end":[0.48808,0.04319,0.02494],"tcp_start":[0.49616,0.04393,0.03346],"tcp_to_object_dist_end":0.013,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":746.0,"n_steps_budget":1000.0,"object_pos_end":[0.5088,0.04295,0.23065],"object_pos_start":[0.50107,0.0432,0.02544],"object_to_goal_dist_end":0.2256,"object_to_goal_dist_start":0.24373,"object_z_max":0.23038,"peak_contact_force":0.07065,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":30665.0,"raw_peak_contact_force":0.62997,"subtask_id":"subtask_lift","tcp_end":[0.49734,0.04292,0.23613],"tcp_start":[0.48808,0.04319,0.02494],"tcp_to_object_dist_end":0.0127,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":547.0,"n_steps_budget":1000.0,"object_pos_end":[0.56729,0.22907,0.241],"object_pos_start":[0.5088,0.04295,0.23065],"object_to_goal_dist_end":0.09559,"object_to_goal_dist_start":0.2256,"object_z_max":0.24099,"peak_contact_force":0.09237,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":20798.0,"raw_peak_contact_force":0.1065,"tcp_end":[0.55708,0.22914,0.25195],"tcp_start":[0.49734,0.04292,0.23613],"tcp_to_object_dist_end":0.01497,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":213.0,"n_steps_budget":1000.0,"object_pos_end":[0.55906,0.23971,0.14145],"object_pos_start":[0.56729,0.22907,0.241],"object_to_goal_dist_end":0.00914,"object_to_goal_dist_start":0.09559,"object_z_max":0.241,"peak_contact_force":0.07269,"phase_name":"descend_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8290.0,"raw_peak_contact_force":0.16161,"subtask_id":"subtask_place","tcp_end":[0.55975,0.24034,0.15442],"tcp_start":[0.55708,0.22914,0.25195],"tcp_to_object_dist_end":0.013,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1efc3ad2e58ea1c47cd56203c4986b53dab7b80d759e458b85d233ccc9cc04bd`; realized-scene SHA-256: `67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47616,-0.02015,0.03]},{"name":"goal","value":[0.63142,0.15919,0.19002]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.47616,-0.02015,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63142,0.15919,0.19002]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.45344,"average_solve_count":247.0,"average_success_count":247.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.25898,"approach_goal.approach_goal_offset_z":0.09037,"descend_1.depth":0.00164,"descend_goal.place_offset_z":-0.01459,"lift_1.lift_height":0.23283,"lift_1.lift_speed":0.04669},"optimized_scores":{"best_composite_score":0.56151,"best_fitness_score":0.98151,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":83.0,"contact_point_centroid":[0.47234,-0.01892,-0.00147],"force_p95":0.62405,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.654,"mean_force":0.238,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46371,-0.0193,0.02813]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14624.0,"contact_point_centroid":[0.46682,-0.03836,0.136],"force_p95":0.07365,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27059,"mean_force":0.05057,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46674,-0.01923,0.13402]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14058.0,"contact_point_centroid":[0.4667,-7e-05,0.13283],"force_p95":0.07429,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27046,"mean_force":0.05213,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46656,-0.01923,0.13069]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47617,-0.01996,-0.00208],"force_p95":0.1451,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22277,"mean_force":0.12881,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46573,-0.01934,0.02811]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3586.0,"contact_point_centroid":[0.62182,0.17035,0.23225],"force_p95":0.07402,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14686,"mean_force":0.05007,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.62181,0.15125,0.23025]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3660.0,"contact_point_centroid":[0.62185,0.13195,0.23293],"force_p95":0.07366,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14531,"mean_force":0.0487,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.62177,0.1512,0.23076]},{"body_a":"world","body_b":"grasp_target","contact_count":140.0,"contact_point_centroid":[0.47616,-0.02015,-0.00106],"force_p95":0.13842,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12212,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49591,-0.00255,0.29781]},{"body_a":"world","body_b":"grasp_target","contact_count":3668.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13411,"mean_force":0.12278,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48015,-0.01325,0.16178]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12494.0,"contact_point_centroid":[0.54892,0.08777,0.25547],"force_p95":0.07716,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1057,"mean_force":0.05217,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5487,0.06856,0.25327]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14349.0,"contact_point_centroid":[0.54606,0.04666,0.25436],"force_p95":0.06813,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10394,"mean_force":0.04638,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5462,0.06575,0.25271]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4812.0,"contact_point_centroid":[0.46455,-8e-05,0.02924],"force_p95":0.06829,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10222,"mean_force":0.04492,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46461,-0.01932,0.02701]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5435.0,"contact_point_centroid":[0.46405,-0.03856,0.02864],"force_p95":0.06532,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08192,"mean_force":0.04113,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46461,-0.01932,0.02702]}],"total_contact_groups":12},"final_pose_error":0.01481,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.62357,0.15517,0.17416],"final_tcp_position":[0.62548,0.15556,0.18849],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":0.654,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":36.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02619],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28828,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.13462,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":140.0,"raw_peak_contact_force":0.13845,"subtask_id":"subtask_approach","tcp_end":[0.49022,-0.00696,0.29391],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.26841,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":917.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02619],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28828,"object_z_max":0.02619,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3668.0,"raw_peak_contact_force":0.13411,"subtask_id":"subtask_approach","tcp_end":[0.47235,-0.01948,0.03468],"tcp_start":[0.49022,-0.00696,0.29391],"tcp_to_object_dist_end":0.00949,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47604,-0.01934,0.02573],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28811,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.14141,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12047.0,"raw_peak_contact_force":0.22277,"tcp_end":[0.46458,-0.01932,0.02698],"tcp_start":[0.47235,-0.01948,0.03468],"tcp_to_object_dist_end":0.01153,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":717.0,"n_steps_budget":1000.0,"object_pos_end":[0.48228,-0.01905,0.23268],"object_pos_start":[0.47604,-0.01934,0.02573],"object_to_goal_dist_end":0.2363,"object_to_goal_dist_start":0.28811,"object_z_max":0.2324,"peak_contact_force":0.07801,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":28765.0,"raw_peak_contact_force":0.654,"subtask_id":"subtask_lift","tcp_end":[0.47246,-0.01925,0.23898],"tcp_start":[0.46458,-0.01932,0.02698],"tcp_to_object_dist_end":0.01167,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":653.0,"n_steps_budget":1000.0,"object_pos_end":[0.6258,0.14729,0.25683],"object_pos_start":[0.48228,-0.01905,0.23268],"object_to_goal_dist_end":0.0681,"object_to_goal_dist_start":0.2363,"object_z_max":0.25682,"peak_contact_force":0.06975,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":26843.0,"raw_peak_contact_force":0.1057,"tcp_end":[0.61933,0.14741,0.26989],"tcp_start":[0.47246,-0.01925,0.23898],"tcp_to_object_dist_end":0.01458,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":173.0,"n_steps_budget":1000.0,"object_pos_end":[0.62357,0.15517,0.17416],"object_pos_start":[0.6258,0.14729,0.25683],"object_to_goal_dist_end":0.01814,"object_to_goal_dist_start":0.0681,"object_z_max":0.25683,"peak_contact_force":0.07262,"phase_name":"descend_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7246.0,"raw_peak_contact_force":0.14686,"subtask_id":"subtask_place","tcp_end":[0.62548,0.15556,0.18849],"tcp_start":[0.61933,0.14741,0.26989],"tcp_to_object_dist_end":0.01446,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `37495cb43897015e78e007c86af160d11c8460c1ce7249e5c03dce38206c0daf`; realized-scene SHA-256: `5ce27bcdb8582e1d517b17df0f9c2ad7b05701113a75707627744a889253e6a7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45856,-0.02632,0.03]},{"name":"goal","value":[0.63013,0.20822,0.11412]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.45856,-0.02632,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63013,0.20822,0.11412]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.38571,"average_solve_count":280.0,"average_success_count":280.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.257,"approach_goal.approach_goal_offset_z":0.06052,"descend_1.depth":0.00238,"descend_goal.place_offset_z":0.01105,"lift_1.lift_height":0.31075,"lift_1.lift_speed":0.04426},"optimized_scores":{"best_composite_score":0.56194,"best_fitness_score":0.98194,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":79.0,"contact_point_centroid":[0.45607,-0.02512,-0.00144],"force_p95":0.5592,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65092,"mean_force":0.15997,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44647,-0.02538,0.02921]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20283.0,"contact_point_centroid":[0.4493,-0.0445,0.17241],"force_p95":0.07085,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27005,"mean_force":0.04869,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44964,-0.02532,0.1711]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20271.0,"contact_point_centroid":[0.4494,-0.00613,0.17524],"force_p95":0.07026,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25737,"mean_force":0.04832,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44975,-0.02532,0.17365]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45858,-0.02615,-0.00208],"force_p95":0.14608,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22386,"mean_force":0.12909,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44856,-0.02545,0.02912]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1278.0,"contact_point_centroid":[0.6197,0.17825,0.15697],"force_p95":0.10343,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16249,"mean_force":0.07382,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.61855,0.19729,0.15607]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1794.0,"contact_point_centroid":[0.61975,0.21629,0.15546],"force_p95":0.08703,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15994,"mean_force":0.05598,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.61863,0.19741,0.1554]},{"body_a":"world","body_b":"grasp_target","contact_count":280.0,"contact_point_centroid":[0.45856,-0.02632,-0.00155],"force_p95":0.13832,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12461,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4882,-0.00661,0.2949]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14637.0,"contact_point_centroid":[0.53675,0.06576,0.24405],"force_p95":0.08016,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12932,"mean_force":0.05217,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53609,0.08487,0.24326]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14107.0,"contact_point_centroid":[0.53746,0.10498,0.24346],"force_p95":0.079,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12579,"mean_force":0.05294,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53682,0.08587,0.24261]},{"body_a":"world","body_b":"grasp_target","contact_count":3656.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12261,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.4637,-0.02031,0.15975]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5283.0,"contact_point_centroid":[0.44683,-0.00617,0.02946],"force_p95":0.06574,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10494,"mean_force":0.04113,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44747,-0.02541,0.02809]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5441.0,"contact_point_centroid":[0.44683,-0.04471,0.02933],"force_p95":0.06565,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08151,"mean_force":0.04118,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44748,-0.02541,0.0281]}],"total_contact_groups":12},"final_pose_error":0.01474,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.63076,0.20136,0.12057],"final_tcp_position":[0.62184,0.20172,0.13549],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":0.65092,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":71.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02591],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30368,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12273,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":280.0,"raw_peak_contact_force":0.13845,"subtask_id":"subtask_approach","tcp_end":[0.47476,-0.01494,0.28911],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.26394,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":914.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02591],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30368,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3656.0,"raw_peak_contact_force":0.12264,"subtask_id":"subtask_approach","tcp_end":[0.45497,-0.02567,0.03523],"tcp_start":[0.47476,-0.01494,0.28911],"tcp_to_object_dist_end":0.00991,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":48.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45845,-0.0255,0.02571],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30317,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.14301,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12524.0,"raw_peak_contact_force":0.22386,"tcp_end":[0.44745,-0.02541,0.02807],"tcp_start":[0.45497,-0.02567,0.03523],"tcp_to_object_dist_end":0.01125,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":952.0,"n_steps_budget":1000.0,"object_pos_end":[0.46613,-0.02547,0.30691],"object_pos_start":[0.45845,-0.0255,0.02571],"object_to_goal_dist_end":0.34448,"object_to_goal_dist_start":0.30317,"object_z_max":0.30663,"peak_contact_force":0.07694,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":40633.0,"raw_peak_contact_force":0.65092,"subtask_id":"subtask_lift","tcp_end":[0.45581,-0.02541,0.3167],"tcp_start":[0.44745,-0.02541,0.02807],"tcp_to_object_dist_end":0.01423,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":728.0,"n_steps_budget":1000.0,"object_pos_end":[0.62483,0.19348,0.16027],"object_pos_start":[0.46613,-0.02547,0.30691],"object_to_goal_dist_end":0.04873,"object_to_goal_dist_start":0.34448,"object_z_max":0.30709,"peak_contact_force":0.07636,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":28744.0,"raw_peak_contact_force":0.12932,"tcp_end":[0.61672,0.19348,0.1744],"tcp_start":[0.45581,-0.02541,0.3167],"tcp_to_object_dist_end":0.01629,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":95.0,"n_steps_budget":1000.0,"object_pos_end":[0.63076,0.20136,0.12057],"object_pos_start":[0.62483,0.19348,0.16027],"object_to_goal_dist_end":0.00943,"object_to_goal_dist_start":0.04873,"object_z_max":0.16027,"peak_contact_force":0.09299,"phase_name":"descend_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3072.0,"raw_peak_contact_force":0.16249,"subtask_id":"subtask_place","tcp_end":[0.62184,0.20172,0.13549],"tcp_start":[0.61672,0.19348,0.1744],"tcp_to_object_dist_end":0.01739,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```