## Search State

- **Seed**: 1
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.5604 | 1.00 | ✅ accepted |
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 9 | 0.1764 | 0.43 | ❌ rejected |
| 3 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.4387 | 0.79 | ✅ accepted |
| 2 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.2393 | 0.40 | ✅ accepted |
| 1 | approach → descend → grasp → lift → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | admittance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 4 | 0.3429 | 0.34 | ❌ rejected |

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

## Current Skill (Q=0.560) — your mutation base

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
  guards:
  - id: lift_success
    when: after_phase
    predicate: object_lifted
    args:
      z_threshold: 0.1
    threshold: 0.1
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.01
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
  - guards:
    - id=lift_success, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.1, args={'z_threshold': 0.1}
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.01]
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

- **Composite score**: 0.560
- **task_score** (E): 1.000
- **fitness_score**: 0.980  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.420

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0711 |
| descend_1 | 1.00 | 1.00 | 0.2205 |
| grasp_1 | 1.00 | 1.00 | 0.0110 |
| lift_1 | 1.00 | 1.00 | 0.2051 |
| approach_goal | 1.00 | 1.00 | 0.2348 |
| descend_goal | 1.00 | 1.00 | 0.0893 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.482, -0.000, 0.256) | (0.479, -0.000, 0.030)→(0.479, -0.000, 0.026) | 0.276→0.278 | 1.00 / 4.000 | 0.124 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.482, -0.000, 0.256)→(0.474, -0.000, 0.035) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 4.000 | 0.123 | 0.124 |
| grasp_1 | grasp | 1.00 / step_budget | (0.474, -0.000, 0.035)→(0.467, -0.001, 0.028) | (0.479, -0.000, 0.026)→(0.479, -0.001, 0.026) | 0.278→0.278 | 1.00 / 45.333 | 0.146 | 0.219 |
| lift_1 | lift | 1.00 / step_budget | (0.467, -0.001, 0.028)→(0.475, -0.001, 0.232) | (0.479, -0.001, 0.026)→(0.485, -0.001, 0.225) | 0.278→0.257 | 1.00 / 40.667 | 0.074 | 0.635 |
| approach_goal | approach | 1.00 / step_budget | (0.475, -0.001, 0.232)→(0.599, 0.191, 0.267) | (0.485, -0.001, 0.225)→(0.606, 0.190, 0.252) | 0.257→0.103 | 1.00 / 35.667 | 0.092 | 0.121 |
| descend_goal | descend | 1.00 / step_budget | (0.599, 0.191, 0.267)→(0.603, 0.200, 0.179) | (0.606, 0.190, 0.252)→(0.602, 0.200, 0.162) | 0.103→0.014 | 1.00 / 40.667 | 0.076 | 0.169 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.354
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 1.000
- phase_score: 0.539
- phase_breakdown.subtask_approach_score: 0.148
- phase_breakdown.subtask_lift_score: 0.239
- phase_breakdown.subtask_place_score: 0.874
- grasp_place_fitness: 0.981

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.981
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.560
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.437


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.44444,"average_solve_count":261.0,"average_success_count":261.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.29953,"approach_goal.approach_goal_offset_z":0.14143,"descend_1.depth":9e-05,"descend_goal.place_offset_z":0.0129,"lift_1.lift_height":0.26494,"lift_1.lift_speed":0.04801},"optimized_scores":{"best_composite_score":0.55971,"best_fitness_score":0.97971,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":88.0,"contact_point_centroid":[0.49695,0.04252,-0.00155],"force_p95":0.64642,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.68326,"mean_force":0.23493,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48745,0.04319,0.02602]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18524.0,"contact_point_centroid":[0.49064,0.06206,0.14778],"force_p95":0.07194,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30311,"mean_force":0.04877,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49103,0.04294,0.14636]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17086.0,"contact_point_centroid":[0.49091,0.02374,0.15022],"force_p95":0.07635,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28192,"mean_force":0.05163,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49114,0.04294,0.14817]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50125,0.04463,-0.00217],"force_p95":0.17317,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.26178,"mean_force":0.13588,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4896,0.04341,0.02601]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3746.0,"contact_point_centroid":[0.48948,0.02403,0.02784],"force_p95":0.08621,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15289,"mean_force":0.05606,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48843,0.0433,0.02479]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4927.0,"contact_point_centroid":[0.55811,0.25299,0.22803],"force_p95":0.07652,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14703,"mean_force":0.04791,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.55808,0.23428,0.2264]},{"body_a":"world","body_b":"grasp_target","contact_count":436.0,"contact_point_centroid":[0.50118,0.04505,-0.00171],"force_p95":0.13814,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12376,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49888,0.01494,0.30698]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3940.0,"contact_point_centroid":[0.55784,0.21498,0.22729],"force_p95":0.09801,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13827,"mean_force":0.06235,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.5581,0.23436,0.22554]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49666,0.03755,0.17192]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8895.0,"contact_point_centroid":[0.52669,0.11577,0.27454],"force_p95":0.09006,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10961,"mean_force":0.061,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52634,0.13499,0.27294]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11406.0,"contact_point_centroid":[0.52703,0.15544,0.27397],"force_p95":0.07283,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10541,"mean_force":0.04732,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52682,0.13653,0.273]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5539.0,"contact_point_centroid":[0.48815,0.06241,0.02736],"force_p95":0.07081,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08452,"mean_force":0.04082,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48844,0.0433,0.02479]}],"total_contact_groups":12},"final_pose_error":0.01468,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.55738,0.23978,0.15935],"final_tcp_position":[0.56008,0.24054,0.17303],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":0.68326,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":110.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.1224,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":436.0,"raw_peak_contact_force":0.13845,"subtask_id":"subtask_approach","tcp_end":[0.49884,0.03109,0.31552],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.28984,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12264,"subtask_id":"subtask_approach","tcp_end":[0.49652,0.04403,0.03334],"tcp_start":[0.49884,0.03109,0.31552],"tcp_to_object_dist_end":0.00873,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50109,0.04323,0.02545],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.2437,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.16095,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11085.0,"raw_peak_contact_force":0.26178,"tcp_end":[0.48841,0.04329,0.02476],"tcp_start":[0.49652,0.04403,0.03334],"tcp_to_object_dist_end":0.0127,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":860.0,"n_steps_budget":1000.0,"object_pos_end":[0.50895,0.04302,0.26423],"object_pos_start":[0.50109,0.04323,0.02545],"object_to_goal_dist_end":0.24003,"object_to_goal_dist_start":0.2437,"object_z_max":0.26397,"peak_contact_force":0.07043,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":35698.0,"raw_peak_contact_force":0.68326,"subtask_id":"subtask_lift","tcp_end":[0.49781,0.04298,0.27077],"tcp_start":[0.48841,0.04329,0.02476],"tcp_to_object_dist_end":0.01292,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":534.0,"n_steps_budget":1000.0,"object_pos_end":[0.56711,0.22868,0.26758],"object_pos_start":[0.50895,0.04302,0.26423],"object_to_goal_dist_end":0.12191,"object_to_goal_dist_start":0.24003,"object_z_max":0.26757,"peak_contact_force":0.09404,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":20301.0,"raw_peak_contact_force":0.10961,"tcp_end":[0.55725,0.22867,0.27928],"tcp_start":[0.49781,0.04298,0.27077],"tcp_to_object_dist_end":0.0153,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":230.0,"n_steps_budget":1000.0,"object_pos_end":[0.55738,0.23978,0.15935],"object_pos_start":[0.56711,0.22868,0.26758],"object_to_goal_dist_end":0.01528,"object_to_goal_dist_start":0.12191,"object_z_max":0.26758,"peak_contact_force":0.08072,"phase_name":"descend_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8867.0,"raw_peak_contact_force":0.14703,"subtask_id":"subtask_place","tcp_end":[0.56008,0.24054,0.17303],"tcp_start":[0.55725,0.22867,0.27928],"tcp_to_object_dist_end":0.01396,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.45902,"average_solve_count":244.0,"average_success_count":244.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.28884,"approach_goal.approach_goal_offset_z":0.11126,"descend_1.depth":0.00557,"descend_goal.place_offset_z":0.01796,"lift_1.lift_height":0.2617,"lift_1.lift_speed":0.0533},"optimized_scores":{"best_composite_score":0.55999,"best_fitness_score":0.97999,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":82.0,"contact_point_centroid":[0.47349,-0.01928,-0.00141],"force_p95":0.50524,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.59126,"mean_force":0.16988,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46347,-0.01943,0.0317]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16478.0,"contact_point_centroid":[0.46662,-0.00023,0.15225],"force_p95":0.07266,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28089,"mean_force":0.05029,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4668,-0.01938,0.15043]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16441.0,"contact_point_centroid":[0.46647,-0.03854,0.14854],"force_p95":0.07347,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27849,"mean_force":0.05067,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46662,-0.01938,0.14688]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47616,-0.02001,-0.00206],"force_p95":0.14057,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19275,"mean_force":0.12755,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4656,-0.01947,0.03162]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2604.0,"contact_point_centroid":[0.62155,0.13163,0.25803],"force_p95":0.09372,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16755,"mean_force":0.06273,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.62187,0.15091,0.25638]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3192.0,"contact_point_centroid":[0.62202,0.16967,0.25867],"force_p95":0.08194,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16422,"mean_force":0.05203,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.6218,0.15082,0.25722]},{"body_a":"world","body_b":"grasp_target","contact_count":204.0,"contact_point_centroid":[0.47616,-0.02015,-0.00136],"force_p95":0.13839,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12472,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49375,-0.00407,0.30233]},{"body_a":"world","body_b":"grasp_target","contact_count":3812.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12666,"mean_force":0.12264,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47841,-0.01468,0.17001]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12244.0,"contact_point_centroid":[0.54724,0.04635,0.27914],"force_p95":0.07734,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12091,"mean_force":0.05227,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.54648,0.06545,0.27779]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11997.0,"contact_point_centroid":[0.54932,0.08684,0.27964],"force_p95":0.0779,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11368,"mean_force":0.05259,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.54851,0.06774,0.27815]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4819.0,"contact_point_centroid":[0.46446,-0.00023,0.03279],"force_p95":0.0679,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09869,"mean_force":0.04489,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46448,-0.01945,0.03052]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5172.0,"contact_point_centroid":[0.46433,-0.03868,0.03233],"force_p95":0.06664,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07982,"mean_force":0.04296,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46449,-0.01945,0.03052]}],"total_contact_groups":12},"final_pose_error":0.01488,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.62432,0.15477,0.20154],"final_tcp_position":[0.62549,0.15518,0.22102],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":0.59126,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":52.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02587],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28847,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12703,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":204.0,"raw_peak_contact_force":0.13845,"subtask_id":"subtask_approach","tcp_end":[0.48669,-0.00974,0.30584],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.28036,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":953.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02587],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28847,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3812.0,"raw_peak_contact_force":0.12666,"subtask_id":"subtask_approach","tcp_end":[0.47219,-0.01961,0.0382],"tcp_start":[0.48669,-0.00974,0.30584],"tcp_to_object_dist_end":0.01282,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47605,-0.01951,0.02578],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28818,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.13803,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11791.0,"raw_peak_contact_force":0.19275,"tcp_end":[0.46445,-0.01945,0.03049],"tcp_start":[0.47219,-0.01961,0.0382],"tcp_to_object_dist_end":0.01251,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":801.0,"n_steps_budget":1000.0,"object_pos_end":[0.48281,-0.01947,0.2568],"object_pos_start":[0.47605,-0.01951,0.02578],"object_to_goal_dist_end":0.2418,"object_to_goal_dist_start":0.28818,"object_z_max":0.25653,"peak_contact_force":0.07733,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":33001.0,"raw_peak_contact_force":0.59126,"subtask_id":"subtask_lift","tcp_end":[0.4728,-0.01943,0.26789],"tcp_start":[0.46445,-0.01945,0.03049],"tcp_to_object_dist_end":0.01495,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":633.0,"n_steps_budget":1000.0,"object_pos_end":[0.62398,0.14645,0.273],"object_pos_start":[0.48281,-0.01947,0.2568],"object_to_goal_dist_end":0.08428,"object_to_goal_dist_start":0.2418,"object_z_max":0.27308,"peak_contact_force":0.09036,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":24241.0,"raw_peak_contact_force":0.12091,"tcp_end":[0.61921,0.14691,0.29132],"tcp_start":[0.4728,-0.01943,0.26789],"tcp_to_object_dist_end":0.01894,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":151.0,"n_steps_budget":1000.0,"object_pos_end":[0.62432,0.15477,0.20154],"object_pos_start":[0.62398,0.14645,0.273],"object_to_goal_dist_end":0.01424,"object_to_goal_dist_start":0.08428,"object_z_max":0.273,"peak_contact_force":0.07692,"phase_name":"descend_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5796.0,"raw_peak_contact_force":0.16755,"subtask_id":"subtask_place","tcp_end":[0.62549,0.15518,0.22102],"tcp_start":[0.61921,0.14691,0.29132],"tcp_to_object_dist_end":0.01952,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.61574,"average_solve_count":216.0,"average_success_count":216.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.09593,"approach_goal.approach_goal_offset_z":0.12935,"descend_1.depth":0.00171,"descend_goal.place_offset_z":0.01452,"lift_1.lift_height":0.15236,"lift_1.lift_speed":0.04492},"optimized_scores":{"best_composite_score":0.56148,"best_fitness_score":0.98148,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":82.0,"contact_point_centroid":[0.4545,-0.02539,-0.00145],"force_p95":0.60782,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62919,"mean_force":0.24058,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44623,-0.02551,0.02856]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8774.0,"contact_point_centroid":[0.44906,-0.04458,0.09394],"force_p95":0.07493,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26582,"mean_force":0.05212,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44885,-0.02543,0.09209]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8774.0,"contact_point_centroid":[0.44904,-0.00628,0.09401],"force_p95":0.07367,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25246,"mean_force":0.05183,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44885,-0.02543,0.09209]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45857,-0.02616,-0.00206],"force_p95":0.14252,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20169,"mean_force":0.12805,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44813,-0.02558,0.02846]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3367.0,"contact_point_centroid":[0.62189,0.18119,0.18666],"force_p95":0.09595,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19386,"mean_force":0.06087,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.62129,0.2004,0.1851]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3749.0,"contact_point_centroid":[0.62182,0.21913,0.1871],"force_p95":0.08347,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17786,"mean_force":0.05295,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.62123,0.20032,0.18595]},{"body_a":"world","body_b":"grasp_target","contact_count":1200.0,"contact_point_centroid":[0.45856,-0.02632,-0.00189],"force_p95":0.13608,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12303,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48081,-0.01086,0.22404]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15667.0,"contact_point_centroid":[0.53498,0.06532,0.1945],"force_p95":0.08876,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13142,"mean_force":0.05706,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5342,0.08446,0.19271]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17376.0,"contact_point_centroid":[0.53471,0.10339,0.19394],"force_p95":0.08052,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12735,"mean_force":0.05159,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53412,0.08439,0.19265]},{"body_a":"world","body_b":"grasp_target","contact_count":1664.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45658,-0.02411,0.0888]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5288.0,"contact_point_centroid":[0.44648,-0.00629,0.0292],"force_p95":0.06534,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10033,"mean_force":0.04114,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44704,-0.02554,0.02744]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5426.0,"contact_point_centroid":[0.44648,-0.04483,0.02904],"force_p95":0.0656,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08019,"mean_force":0.04121,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44705,-0.02554,0.02744]}],"total_contact_groups":12},"final_pose_error":0.01498,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.62472,0.20396,0.12505],"final_tcp_position":[0.62412,0.20436,0.14182],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":0.62919,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":301.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1200.0,"raw_peak_contact_force":0.13845,"subtask_id":"subtask_approach","tcp_end":[0.46138,-0.02255,0.1452],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11928,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":416.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1664.0,"raw_peak_contact_force":0.12263,"subtask_id":"subtask_approach","tcp_end":[0.45454,-0.0258,0.03456],"tcp_start":[0.46138,-0.02255,0.1452],"tcp_to_object_dist_end":0.00946,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":48.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45844,-0.02561,0.02576],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30324,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.13999,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12514.0,"raw_peak_contact_force":0.20169,"tcp_end":[0.44702,-0.02553,0.02741],"tcp_start":[0.45454,-0.0258,0.03456],"tcp_to_object_dist_end":0.01154,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":438.0,"n_steps_budget":1000.0,"object_pos_end":[0.4639,-0.02547,0.15423],"object_pos_start":[0.45844,-0.02561,0.02576],"object_to_goal_dist_end":0.28957,"object_to_goal_dist_start":0.30324,"object_z_max":0.15395,"peak_contact_force":0.07365,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":17630.0,"raw_peak_contact_force":0.62919,"subtask_id":"subtask_lift","tcp_end":[0.45391,-0.02544,0.15869],"tcp_start":[0.44702,-0.02553,0.02741],"tcp_to_object_dist_end":0.01094,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":33.0,"n_steps":880.0,"n_steps_budget":1000.0,"object_pos_end":[0.62789,0.19626,0.21614],"object_pos_start":[0.4639,-0.02547,0.15423],"object_to_goal_dist_end":0.10275,"object_to_goal_dist_start":0.28957,"object_z_max":0.21611,"peak_contact_force":0.09257,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":33043.0,"raw_peak_contact_force":0.13142,"tcp_end":[0.61955,0.19663,0.23133],"tcp_start":[0.45391,-0.02544,0.15869],"tcp_to_object_dist_end":0.01733,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":187.0,"n_steps_budget":1000.0,"object_pos_end":[0.62472,0.20396,0.12505],"object_pos_start":[0.62789,0.19626,0.21614],"object_to_goal_dist_end":0.01292,"object_to_goal_dist_start":0.10275,"object_z_max":0.21614,"peak_contact_force":0.07127,"phase_name":"descend_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7116.0,"raw_peak_contact_force":0.19386,"subtask_id":"subtask_place","tcp_end":[0.62412,0.20436,0.14182],"tcp_start":[0.61955,0.19663,0.23133],"tcp_to_object_dist_end":0.01678,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```