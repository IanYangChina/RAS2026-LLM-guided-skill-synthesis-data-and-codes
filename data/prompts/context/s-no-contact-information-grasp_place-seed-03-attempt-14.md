## Search State

- **Seed**: 3
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.5534 | 1.00 | ❌ rejected |
| 13 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.5535 | 1.00 | ✅ accepted |
| 12 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.4581 | 1.00 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | time_limit | pose_tolerance | 9 | 0.3766 | 0.94 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.4581 | 1.00 | ❌ rejected |

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
- Frozen realised-scene SHA-256: `5ce27bcdb8582e1d517b17df0f9c2ad7b05701113a75707627744a889253e6a7`
- Frozen object start: [0.45856491671436245, -0.02631894934039003, 0.03]
- Frozen task target: [0.6301274465206397, 0.20821620360643678, 0.11411929633605987]
- Goal object position: (0.6301274465206397, 0.20821620360643678, 0.11411929633605987)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.6301274465206397, 0.20821620360643678, 0.11411929633605987)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.45856491671436245, -0.02631894934039003, 0.03)
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
  frozen_object_start: [0.4586, -0.0263, 0.03]
  frozen_task_target: [0.6301, 0.2082, 0.1141]
  frozen_object_starts: {'grasp_target': [0.45856491671436245, -0.02631894934039003, 0.03]}
  frozen_targets: {'place_target': [0.6301274465206397, 0.20821620360643678, 0.11411929633605987]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 5ce27bcdb8582e1d517b17df0f9c2ad7b05701113a75707627744a889253e6a7

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
| `object` | offset from object initial position (0.45856491671436245, -0.02631894934039003, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.6301274465206397, 0.20821620360643678, 0.11411929633605987) | final destination targets |
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

## Current Skill (Q=0.553) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
subtasks:
- id: grasp_position
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.005
  weight: 0.5
- id: placement_accuracy
  target_entity: object
  weight: 0.5
phases:
- id: approach_object
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
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: grasp_position
- id: descend_grasp
  type: descend
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
    - 0.005
    tolerance: 0.015
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: contact_check
    when: during_phase
    predicate: contact_detected
    threshold: 1.0
    on_failure: continue
  subtask_id: grasp_position
- id: grasp
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
  guards:
  - id: bilateral_grasp
    when: after_phase
    predicate: bilateral_grasp
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.005
    - 0.005
    - 0.0
- id: lift
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
    tolerance: 0.02
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
    lift_speed:
      type: scalar
      range:
      - 0.03
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: object_lifted_check
    when: after_phase
    predicate: object_lifted
    threshold: 0.03
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: reduce_speed
  subtask_id: placement_accuracy
- id: transport_to_goal
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
    - 0.12
    tolerance: 0.02
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
- id: descend_place
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
  parameters:
    place_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: placement_accuracy

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.12], tolerance=0.02
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.005], tolerance=0.015
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=contact_check, when=during_phase, predicate=contact_detected, on_failure=continue, threshold=1.0
- **grasp** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=bilateral_grasp, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.005, 0.005, 0.0]
- **lift** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.12], tolerance=0.02
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=object_lifted_check, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.03
  - retries: max_attempts=1, strategy=reduce_speed
- **transport_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.12], tolerance=0.02
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **descend_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.015
  - parameter_bindings:
    - place_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.553
- **task_score** (E): 1.000
- **fitness_score**: 0.973  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.420

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_object | 1.00 | 0.1383 |
| descend_grasp | 1.00 | 0.1233 |
| grasp | 1.00 | 0.0131 |
| lift | 1.00 | 0.1246 |
| transport_to_goal | 1.00 | 0.2319 |
| descend_place | 1.00 | 0.0933 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.002, 0.168) | (0.511, 0.002, 0.030)→(0.511, 0.002, 0.026) | 0.244→0.246 |
| descend_grasp | descend | 1.00 / step_budget | (0.506, 0.002, 0.168)→(0.506, 0.002, 0.045) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 |
| grasp | grasp | 1.00 / step_budget | (0.506, 0.002, 0.045)→(0.497, 0.002, 0.035) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 |
| lift | lift | 1.00 / step_budget | (0.497, 0.002, 0.035)→(0.493, 0.001, 0.160) | (0.511, 0.002, 0.026)→(0.506, 0.002, 0.147) | 0.246→0.222 |
| transport_to_goal | approach | 1.00 / step_budget | (0.493, 0.001, 0.160)→(0.617, 0.171, 0.244) | (0.506, 0.002, 0.147)→(0.623, 0.174, 0.228) | 0.222→0.090 |
| descend_place | descend | 1.00 / step_budget | (0.617, 0.171, 0.244)→(0.621, 0.178, 0.151) | (0.623, 0.174, 0.228)→(0.627, 0.181, 0.133) | 0.090→0.007 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.601
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.773
- phase_breakdown.placement_accuracy_score: 0.741
- phase_breakdown.grasp_position_score: 0.805
- grasp_place_fitness: 0.974

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.974
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.553
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.411


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `a4a71a7b2980790489e8194d1356bdee33fb951291c2e0792659ad3d3b3dc711`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `8a78b0f0015ebaf8c4b14c8fbc8142d9b66e4b4efca10f362859101c0ae207df`; realized-scene SHA-256: `5ce27bcdb8582e1d517b17df0f9c2ad7b05701113a75707627744a889253e6a7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45856,-0.02632,0.03]},{"name":"goal","value":[0.63013,0.20822,0.11412]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.45856,-0.02632,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63013,0.20822,0.11412]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.86441,"average_solve_count":177.0,"average_success_count":177.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.18168,"descend_grasp.descend_speed":0.09975,"descend_place.place_speed":0.09578,"lift.lift_height":0.15942,"lift.lift_speed":0.04934,"transport_to_goal.transport_speed":0.16691},"optimized_scores":{"best_composite_score":0.55389,"best_fitness_score":0.97389,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":78.0,"contact_point_centroid":[0.45524,-0.02541,-0.00142],"force_p95":0.42082,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.45449,"mean_force":0.16491,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44554,-0.02537,0.03817]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4100.0,"contact_point_centroid":[0.61509,0.21843,0.1797],"force_p95":0.07801,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29315,"mean_force":0.05148,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62034,0.20029,0.17617]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8334.0,"contact_point_centroid":[0.44156,-0.04447,0.10856],"force_p95":0.07937,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25124,"mean_force":0.05711,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44295,-0.02528,0.10594]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10186.0,"contact_point_centroid":[0.44365,-0.00625,0.10726],"force_p95":0.07384,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24383,"mean_force":0.04824,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44295,-0.02528,0.10594]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4100.0,"contact_point_centroid":[0.62531,0.18168,0.1764],"force_p95":0.07856,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22687,"mean_force":0.05246,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62034,0.20029,0.17617]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45859,-0.02635,-0.00207],"force_p95":0.14585,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19384,"mean_force":0.12849,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44766,-0.02543,0.03822]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15421.0,"contact_point_centroid":[0.53545,0.07071,0.20042],"force_p95":0.074,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19085,"mean_force":0.05105,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53276,0.08966,0.1991]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15718.0,"contact_point_centroid":[0.52882,0.10649,0.20115],"force_p95":0.07089,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17618,"mean_force":0.0494,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53123,0.08771,0.1987]},{"body_a":"world","body_b":"grasp_target","contact_count":960.0,"contact_point_centroid":[0.45856,-0.02632,-0.00186],"force_p95":0.13692,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12314,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48125,-0.01055,0.23596]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5298.0,"contact_point_centroid":[0.44736,-0.0063,0.03849],"force_p95":0.06675,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13355,"mean_force":0.04132,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4465,-0.02539,0.03712]},{"body_a":"world","body_b":"grasp_target","contact_count":1184.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.45743,-0.02378,0.10701]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4427.0,"contact_point_centroid":[0.44578,-0.04466,0.03987],"force_p95":0.07994,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08168,"mean_force":0.04916,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44651,-0.02539,0.03712]}],"total_contact_groups":12},"final_pose_error":0.01498,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.62355,0.20614,0.11008],"final_tcp_position":[0.62393,0.20465,0.12728],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"phases":[{"n_steps":241.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"grasp_position","tcp_end":[0.46221,-0.02203,0.16916],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14325,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":296.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"grasp_position","tcp_end":[0.45478,-0.02561,0.04516],"tcp_start":[0.46221,-0.02203,0.16916],"tcp_to_object_dist_end":0.01952,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45849,-0.02594,0.02573],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30348,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.44648,-0.02539,0.03709],"tcp_start":[0.45478,-0.02561,0.04516],"tcp_to_object_dist_end":0.01655,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":463.0,"n_steps_budget":1000.0,"object_pos_end":[0.45347,-0.02598,0.16365],"object_pos_start":[0.45849,-0.02594,0.02573],"object_to_goal_dist_end":0.29751,"object_to_goal_dist_start":0.30348,"object_z_max":0.16336,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"placement_accuracy","tcp_end":[0.44311,-0.02527,0.17698],"tcp_start":[0.44648,-0.02539,0.03709],"tcp_to_object_dist_end":0.0169,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":779.0,"n_steps_budget":1000.0,"object_pos_end":[0.61799,0.19755,0.20669],"object_pos_start":[0.45347,-0.02598,0.16365],"object_to_goal_dist_end":0.09397,"object_to_goal_dist_start":0.29751,"object_z_max":0.20666,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","tcp_end":[0.61856,0.19661,0.22299],"tcp_start":[0.44311,-0.02527,0.17698],"tcp_to_object_dist_end":0.01633,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":205.0,"n_steps_budget":1000.0,"object_pos_end":[0.62355,0.20614,0.11008],"object_pos_start":[0.61799,0.19755,0.20669],"object_to_goal_dist_end":0.00799,"object_to_goal_dist_start":0.09397,"object_z_max":0.20669,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"placement_accuracy","tcp_end":[0.62393,0.20465,0.12728],"tcp_start":[0.61856,0.19661,0.22299],"tcp_to_object_dist_end":0.01727,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `aa6ec658384c70fac6b4eb656cc8c53536c3d5c760368ab2b384dccf294e2c48`; realized-scene SHA-256: `1959b3932a54fd3d3850620783d44a63a35b8fa059f78d939fdbdef5fbfc64e8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.54431,0.00113,0.03]},{"name":"goal","value":[0.64762,0.15808,0.1911]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.54431,0.00113,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.64762,0.15808,0.1911]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.91667,"average_solve_count":144.0,"average_success_count":144.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.17571,"descend_grasp.descend_speed":0.13025,"descend_place.place_speed":0.06794,"lift.lift_height":0.1352,"lift.lift_speed":0.08838,"transport_to_goal.transport_speed":0.1413},"optimized_scores":{"best_composite_score":0.55329,"best_fitness_score":0.97329,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":81.0,"contact_point_centroid":[0.54138,0.00096,-0.00135],"force_p95":0.5107,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.61779,"mean_force":0.12397,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52795,0.00078,0.035]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6949.0,"contact_point_centroid":[0.52666,0.01986,0.09361],"force_p95":0.08214,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34601,"mean_force":0.05917,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52521,0.00073,0.09134]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7611.0,"contact_point_centroid":[0.52663,-0.01829,0.09111],"force_p95":0.07955,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32347,"mean_force":0.05493,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52525,0.00073,0.08922]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2960.0,"contact_point_centroid":[0.63757,0.17131,0.25624],"force_p95":0.09226,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23376,"mean_force":0.06468,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.64045,0.15247,0.25305]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3965.0,"contact_point_centroid":[0.64478,0.13423,0.25178],"force_p95":0.07877,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18949,"mean_force":0.05106,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.6405,0.15253,0.25203]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12238.0,"contact_point_centroid":[0.5803,0.09396,0.22129],"force_p95":0.10592,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17803,"mean_force":0.06759,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.58043,0.07489,0.21916]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14665.0,"contact_point_centroid":[0.58631,0.05932,0.22258],"force_p95":0.0876,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17576,"mean_force":0.05564,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.58259,0.07767,0.22193]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5443,0.00116,-0.00203],"force_p95":0.13347,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15432,"mean_force":0.12533,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53044,0.00084,0.0352]},{"body_a":"world","body_b":"grasp_target","contact_count":1012.0,"contact_point_centroid":[0.54431,0.00113,-0.00187],"force_p95":0.13691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12311,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51605,0.00044,0.23486]},{"body_a":"world","body_b":"grasp_target","contact_count":1100.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.53498,0.00093,0.10554]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4840.0,"contact_point_centroid":[0.5305,-0.01824,0.03536],"force_p95":0.06863,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10189,"mean_force":0.04465,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52917,0.00081,0.03373]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4149.0,"contact_point_centroid":[0.5306,0.02003,0.03624],"force_p95":0.07527,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09609,"mean_force":0.05182,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52918,0.00081,0.03373]}],"total_contact_groups":12},"final_pose_error":0.015,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.65016,0.15847,0.18502],"final_tcp_position":[0.64276,0.15553,0.20506],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"phases":[{"n_steps":254.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"grasp_position","tcp_end":[0.5343,0.0009,0.16718],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14152,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":275.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"grasp_position","tcp_end":[0.5382,0.001,0.0444],"tcp_start":[0.5343,0.0009,0.16718],"tcp_to_object_dist_end":0.01937,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54418,0.00104,0.02587],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25033,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.52914,0.00081,0.03369],"tcp_start":[0.5382,0.001,0.0444],"tcp_to_object_dist_end":0.01695,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":392.0,"n_steps_budget":960.0,"object_pos_end":[0.53916,0.00085,0.13806],"object_pos_start":[0.54418,0.00104,0.02587],"object_to_goal_dist_end":0.19824,"object_to_goal_dist_start":0.25033,"object_z_max":0.13779,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"placement_accuracy","tcp_end":[0.52528,0.00074,0.1493],"tcp_start":[0.52914,0.00081,0.03369],"tcp_to_object_dist_end":0.01787,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":789.0,"n_steps_budget":1000.0,"object_pos_end":[0.64834,0.15289,0.27699],"object_pos_start":[0.53916,0.00085,0.13806],"object_to_goal_dist_end":0.08605,"object_to_goal_dist_start":0.19824,"object_z_max":0.27686,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","tcp_end":[0.63955,0.15005,0.29473],"tcp_start":[0.52528,0.00074,0.1493],"tcp_to_object_dist_end":0.02,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":194.0,"n_steps_budget":1000.0,"object_pos_end":[0.65016,0.15847,0.18502],"object_pos_start":[0.64834,0.15289,0.27699],"object_to_goal_dist_end":0.00661,"object_to_goal_dist_start":0.08605,"object_z_max":0.27702,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"placement_accuracy","tcp_end":[0.64276,0.15553,0.20506],"tcp_start":[0.63955,0.15005,0.29473],"tcp_to_object_dist_end":0.02157,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `e1209649252ffcf03853fe0727696e22a1eda11729c6c1ae21659980557d7e98`; realized-scene SHA-256: `e32d7866764afb23ec7c7faebb4bcca0aa39fbf2f1ab61f3c9c527b297153af9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5305,0.03079,0.03]},{"name":"goal","value":[0.60153,0.17858,0.10809]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5305,0.03079,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.60153,0.17858,0.10809]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.7561,"average_solve_count":164.0,"average_success_count":164.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.1591,"descend_grasp.descend_speed":0.1048,"descend_place.place_speed":0.05037,"lift.lift_height":0.1378,"lift.lift_speed":0.07994,"transport_to_goal.transport_speed":0.112},"optimized_scores":{"best_composite_score":0.55316,"best_fitness_score":0.97316,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":84.0,"contact_point_centroid":[0.52762,0.02913,-0.00147],"force_p95":0.47137,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60939,"mean_force":0.13242,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51457,0.02913,0.0356]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6749.0,"contact_point_centroid":[0.51268,0.04818,0.09495],"force_p95":0.08487,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34418,"mean_force":0.06123,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51196,0.02896,0.09225]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8288.0,"contact_point_centroid":[0.51362,0.01001,0.09259],"force_p95":0.08188,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31589,"mean_force":0.05162,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51197,0.02896,0.09083]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2921.0,"contact_point_centroid":[0.59111,0.18965,0.17389],"force_p95":0.11005,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26951,"mean_force":0.07725,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.59282,0.17065,0.1711]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53057,0.03073,-0.00214],"force_p95":0.16126,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22743,"mean_force":0.13288,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51709,0.0293,0.03563]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3863.0,"contact_point_centroid":[0.59911,0.15307,0.17038],"force_p95":0.08908,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19897,"mean_force":0.05762,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.59284,0.17068,0.17068]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8647.0,"contact_point_centroid":[0.54843,0.11449,0.1824],"force_p95":0.10952,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17536,"mean_force":0.06488,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54904,0.09534,0.18026]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10455.0,"contact_point_centroid":[0.55518,0.0803,0.18259],"force_p95":0.08893,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1725,"mean_force":0.054,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55088,0.09844,0.18172]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5267.0,"contact_point_centroid":[0.51708,0.0102,0.0363],"force_p95":0.0653,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1637,"mean_force":0.04103,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51585,0.02922,0.03422]},{"body_a":"world","body_b":"grasp_target","contact_count":1008.0,"contact_point_centroid":[0.5305,0.03079,-0.00187],"force_p95":0.13691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12311,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51045,0.01244,0.23484]},{"body_a":"world","body_b":"grasp_target","contact_count":1132.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.5225,0.02775,0.10562]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4244.0,"contact_point_centroid":[0.51657,0.04857,0.037],"force_p95":0.08002,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08548,"mean_force":0.05175,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51585,0.02922,0.03423]}],"total_contact_groups":12},"final_pose_error":0.01496,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.60591,0.17912,0.10247],"final_tcp_position":[0.59564,0.17518,0.12141],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"phases":[{"n_steps":253.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"grasp_position","tcp_end":[0.52268,0.02587,0.16725],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14153,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":283.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"grasp_position","tcp_end":[0.52474,0.02979,0.04446],"tcp_start":[0.52268,0.02587,0.16725],"tcp_to_object_dist_end":0.01935,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53047,0.02988,0.02552],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18434,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.51582,0.02922,0.03419],"tcp_start":[0.52474,0.02979,0.04446],"tcp_to_object_dist_end":0.01704,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":397.0,"n_steps_budget":1000.0,"object_pos_end":[0.52556,0.02966,0.14058],"object_pos_start":[0.53047,0.02988,0.02552],"object_to_goal_dist_end":0.17031,"object_to_goal_dist_start":0.18434,"object_z_max":0.14031,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"placement_accuracy","tcp_end":[0.51203,0.02897,0.15245],"tcp_start":[0.51582,0.02922,0.03419],"tcp_to_object_dist_end":0.01801,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":540.0,"n_steps_budget":1000.0,"object_pos_end":[0.60326,0.17073,0.19901],"object_pos_start":[0.52556,0.02966,0.14058],"object_to_goal_dist_end":0.09128,"object_to_goal_dist_start":0.17031,"object_z_max":0.19892,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","tcp_end":[0.59207,0.16711,0.21492],"tcp_start":[0.51203,0.02897,0.15245],"tcp_to_object_dist_end":0.01978,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":219.0,"n_steps_budget":1000.0,"object_pos_end":[0.60591,0.17912,0.10247],"object_pos_start":[0.60326,0.17073,0.19901],"object_to_goal_dist_end":0.00715,"object_to_goal_dist_start":0.09128,"object_z_max":0.19903,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"placement_accuracy","tcp_end":[0.59564,0.17518,0.12141],"tcp_start":[0.59207,0.16711,0.21492],"tcp_to_object_dist_end":0.02191,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```