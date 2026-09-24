## Search State

- **Seed**: 3
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.5535 | 1.00 | ✅ accepted |
| 12 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.4581 | 1.00 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | time_limit | pose_tolerance | 9 | 0.3766 | 0.94 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.4581 | 1.00 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.4581 | 1.00 | ❌ rejected |

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
| approach_object | 1.00 | 0.1384 |
| descend_grasp | 1.00 | 0.1232 |
| grasp | 1.00 | 0.0131 |
| lift | 1.00 | 0.1270 |
| transport_to_goal | 1.00 | 0.2281 |
| descend_place | 1.00 | 0.0935 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.002, 0.168) | (0.511, 0.002, 0.030)→(0.511, 0.002, 0.026) | 0.244→0.246 |
| descend_grasp | descend | 1.00 / step_budget | (0.506, 0.002, 0.168)→(0.506, 0.002, 0.045) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 |
| grasp | grasp | 1.00 / step_budget | (0.506, 0.002, 0.045)→(0.497, 0.002, 0.035) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 |
| lift | lift | 1.00 / step_budget | (0.497, 0.002, 0.035)→(0.494, 0.001, 0.162) | (0.511, 0.002, 0.026)→(0.507, 0.001, 0.149) | 0.246→0.219 |
| transport_to_goal | approach | 1.00 / step_budget | (0.494, 0.001, 0.162)→(0.617, 0.171, 0.244) | (0.507, 0.001, 0.149)→(0.622, 0.173, 0.227) | 0.219→0.090 |
| descend_place | descend | 1.00 / step_budget | (0.617, 0.171, 0.244)→(0.621, 0.178, 0.151) | (0.622, 0.173, 0.227)→(0.625, 0.181, 0.132) | 0.090→0.006 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.528
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
- **Final σ (mean)**: 0.299


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.01258,"average_solve_count":159.0,"average_success_count":159.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.17763,"descend_grasp.descend_speed":0.10216,"descend_place.place_speed":0.05234,"lift.lift_height":0.13211,"lift.lift_speed":0.11387,"transport_to_goal.transport_speed":0.1521},"optimized_scores":{"best_composite_score":0.55389,"best_fitness_score":0.97389,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":74.0,"contact_point_centroid":[0.45644,-0.02536,-0.00141],"force_p95":0.41154,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.53661,"mean_force":0.11635,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44531,-0.02536,0.03851]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3655.0,"contact_point_centroid":[0.61604,0.21901,0.17913],"force_p95":0.08087,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33351,"mean_force":0.05826,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.6205,0.20056,0.17576]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5652.0,"contact_point_centroid":[0.44322,-0.04451,0.09371],"force_p95":0.09151,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30086,"mean_force":0.06329,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44296,-0.02528,0.09098]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7073.0,"contact_point_centroid":[0.44467,-0.00637,0.09302],"force_p95":0.08086,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29663,"mean_force":0.05218,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44295,-0.02528,0.09137]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4510.0,"contact_point_centroid":[0.62501,0.18192,0.17722],"force_p95":0.07316,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23978,"mean_force":0.04905,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62043,0.20047,0.17692]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15627.0,"contact_point_centroid":[0.54096,0.07705,0.18893],"force_p95":0.08915,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20354,"mean_force":0.05463,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53755,0.09593,0.18735]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16103.0,"contact_point_centroid":[0.52951,0.10694,0.18726],"force_p95":0.07932,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19772,"mean_force":0.05236,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53134,0.08819,0.18472]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45859,-0.02635,-0.00207],"force_p95":0.14585,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19384,"mean_force":0.12849,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44766,-0.02543,0.03822]},{"body_a":"world","body_b":"grasp_target","contact_count":960.0,"contact_point_centroid":[0.45856,-0.02632,-0.00186],"force_p95":0.13692,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12314,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48125,-0.01055,0.23596]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5298.0,"contact_point_centroid":[0.44736,-0.0063,0.03849],"force_p95":0.06675,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13355,"mean_force":0.04132,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4465,-0.02539,0.03712]},{"body_a":"world","body_b":"grasp_target","contact_count":1184.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.45743,-0.02378,0.10701]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4427.0,"contact_point_centroid":[0.44578,-0.04466,0.03987],"force_p95":0.07994,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08168,"mean_force":0.04916,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44651,-0.02539,0.03712]}],"total_contact_groups":12},"final_pose_error":0.01496,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.62523,0.20702,0.10615],"final_tcp_position":[0.62394,0.20472,0.12729],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"phases":[{"n_steps":241.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"grasp_position","tcp_end":[0.46221,-0.02203,0.16916],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14325,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":296.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"grasp_position","tcp_end":[0.45478,-0.02561,0.04516],"tcp_start":[0.46221,-0.02203,0.16916],"tcp_to_object_dist_end":0.01952,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45849,-0.02594,0.02573],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30348,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.44648,-0.02539,0.03709],"tcp_start":[0.45478,-0.02561,0.04516],"tcp_to_object_dist_end":0.01655,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":335.0,"n_steps_budget":750.0,"object_pos_end":[0.45798,-0.02617,0.13351],"object_pos_start":[0.45849,-0.02594,0.02573],"object_to_goal_dist_end":0.29146,"object_to_goal_dist_start":0.30348,"object_z_max":0.13322,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"placement_accuracy","tcp_end":[0.44294,-0.02527,0.14954],"tcp_start":[0.44648,-0.02539,0.03709],"tcp_to_object_dist_end":0.022,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":830.0,"n_steps_budget":1000.0,"object_pos_end":[0.62054,0.19911,0.20194],"object_pos_start":[0.45798,-0.02617,0.13351],"object_to_goal_dist_end":0.08881,"object_to_goal_dist_start":0.29146,"object_z_max":0.20188,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","tcp_end":[0.619,0.19716,0.22193],"tcp_start":[0.44294,-0.02527,0.14954],"tcp_to_object_dist_end":0.02015,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":215.0,"n_steps_budget":1000.0,"object_pos_end":[0.62523,0.20702,0.10615],"object_pos_start":[0.62054,0.19911,0.20194],"object_to_goal_dist_end":0.00943,"object_to_goal_dist_start":0.08881,"object_z_max":0.20194,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"placement_accuracy","tcp_end":[0.62394,0.20472,0.12729],"tcp_start":[0.619,0.19716,0.22193],"tcp_to_object_dist_end":0.02131,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.76243,"average_solve_count":181.0,"average_success_count":181.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.15518,"descend_grasp.descend_speed":0.09099,"descend_place.place_speed":0.06455,"lift.lift_height":0.15741,"lift.lift_speed":0.06543,"transport_to_goal.transport_speed":0.11322},"optimized_scores":{"best_composite_score":0.55333,"best_fitness_score":0.97333,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":83.0,"contact_point_centroid":[0.54025,0.00097,-0.00136],"force_p95":0.51858,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55911,"mean_force":0.16409,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52801,0.00078,0.03477]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8475.0,"contact_point_centroid":[0.52635,0.01991,0.10478],"force_p95":0.08209,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31055,"mean_force":0.05994,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52521,0.00074,0.10238]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9906.0,"contact_point_centroid":[0.52613,-0.01826,0.10116],"force_p95":0.07706,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29086,"mean_force":0.05254,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52522,0.00074,0.09913]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4146.0,"contact_point_centroid":[0.63612,0.17088,0.25377],"force_p95":0.06904,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22378,"mean_force":0.04828,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.64029,0.15226,0.25172]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4127.0,"contact_point_centroid":[0.64432,0.13348,0.25164],"force_p95":0.06962,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18332,"mean_force":0.04892,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.6403,0.15227,0.25153]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14347.0,"contact_point_centroid":[0.58609,0.05897,0.23438],"force_p95":0.08335,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16998,"mean_force":0.05494,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5828,0.0777,0.23319]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13385.0,"contact_point_centroid":[0.58214,0.09742,0.23631],"force_p95":0.08757,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15995,"mean_force":0.05795,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5834,0.07847,0.23384]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5443,0.00116,-0.00203],"force_p95":0.13346,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15425,"mean_force":0.12533,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53043,0.00084,0.03512]},{"body_a":"world","body_b":"grasp_target","contact_count":1032.0,"contact_point_centroid":[0.54431,0.00113,-0.00187],"force_p95":0.13668,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1231,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51612,0.00044,0.23447]},{"body_a":"world","body_b":"grasp_target","contact_count":1132.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.53498,0.00093,0.10536]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4840.0,"contact_point_centroid":[0.5305,-0.01824,0.03528],"force_p95":0.06862,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10185,"mean_force":0.04465,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52917,0.00081,0.03366]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4149.0,"contact_point_centroid":[0.53059,0.02003,0.03617],"force_p95":0.07526,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09608,"mean_force":0.05182,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52917,0.00081,0.03366]}],"total_contact_groups":12},"final_pose_error":0.01483,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.64975,0.15806,0.186],"final_tcp_position":[0.64271,0.15546,0.20484],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"phases":[{"n_steps":259.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"grasp_position","tcp_end":[0.53439,0.0009,0.16685],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14118,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":283.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"grasp_position","tcp_end":[0.53819,0.001,0.04433],"tcp_start":[0.53439,0.0009,0.16685],"tcp_to_object_dist_end":0.0193,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54418,0.00104,0.02587],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25033,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.52914,0.00081,0.03362],"tcp_start":[0.53819,0.001,0.04433],"tcp_to_object_dist_end":0.01692,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":489.0,"n_steps_budget":1000.0,"object_pos_end":[0.53832,0.00082,0.16013],"object_pos_start":[0.54418,0.00104,0.02587],"object_to_goal_dist_end":0.194,"object_to_goal_dist_start":0.25033,"object_z_max":0.15987,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"placement_accuracy","tcp_end":[0.52545,0.00075,0.17143],"tcp_start":[0.52914,0.00081,0.03362],"tcp_to_object_dist_end":0.01712,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":753.0,"n_steps_budget":1000.0,"object_pos_end":[0.64744,0.152,0.27857],"object_pos_start":[0.53832,0.00082,0.16013],"object_to_goal_dist_end":0.08768,"object_to_goal_dist_start":0.194,"object_z_max":0.27845,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","tcp_end":[0.6392,0.14956,0.29536],"tcp_start":[0.52545,0.00075,0.17143],"tcp_to_object_dist_end":0.01886,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":197.0,"n_steps_budget":1000.0,"object_pos_end":[0.64975,0.15806,0.186],"object_pos_start":[0.64744,0.152,0.27857],"object_to_goal_dist_end":0.00553,"object_to_goal_dist_start":0.08768,"object_z_max":0.27859,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"placement_accuracy","tcp_end":[0.64271,0.15546,0.20484],"tcp_start":[0.6392,0.14956,0.29536],"tcp_to_object_dist_end":0.02029,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.83444,"average_solve_count":151.0,"average_success_count":151.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.16521,"descend_grasp.descend_speed":0.13138,"descend_place.place_speed":0.04427,"lift.lift_height":0.15005,"lift.lift_speed":0.0901,"transport_to_goal.transport_speed":0.18459},"optimized_scores":{"best_composite_score":0.55317,"best_fitness_score":0.97317,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":83.0,"contact_point_centroid":[0.52783,0.02887,-0.00146],"force_p95":0.50028,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.61333,"mean_force":0.12356,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51461,0.02913,0.03565]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7402.0,"contact_point_centroid":[0.51282,0.04814,0.10129],"force_p95":0.09441,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34593,"mean_force":0.06431,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51199,0.02896,0.09863]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9038.0,"contact_point_centroid":[0.51369,0.01012,0.09879],"force_p95":0.08272,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31797,"mean_force":0.05143,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.512,0.02896,0.09705]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3996.0,"contact_point_centroid":[0.58802,0.18891,0.17376],"force_p95":0.08309,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22874,"mean_force":0.05503,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.59271,0.17051,0.16972]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53057,0.03073,-0.00214],"force_p95":0.16127,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22743,"mean_force":0.13288,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.5171,0.0293,0.03564]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9484.0,"contact_point_centroid":[0.55511,0.08115,0.19021],"force_p95":0.08716,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19052,"mean_force":0.0508,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55196,0.09975,0.18893]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4781.0,"contact_point_centroid":[0.59675,0.15183,0.16989],"force_p95":0.07764,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18979,"mean_force":0.04754,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.59273,0.17058,0.16891]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5267.0,"contact_point_centroid":[0.51708,0.0102,0.03631],"force_p95":0.0653,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16373,"mean_force":0.04104,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51585,0.02922,0.03423]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8263.0,"contact_point_centroid":[0.54924,0.11746,0.19163],"force_p95":0.11132,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15581,"mean_force":0.06303,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55128,0.09856,0.1885]},{"body_a":"world","body_b":"grasp_target","contact_count":1008.0,"contact_point_centroid":[0.5305,0.03079,-0.00187],"force_p95":0.13691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12311,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51045,0.01244,0.23484]},{"body_a":"world","body_b":"grasp_target","contact_count":1108.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.52247,0.02776,0.10552]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4244.0,"contact_point_centroid":[0.51658,0.04857,0.037],"force_p95":0.08002,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08548,"mean_force":0.05175,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51586,0.02922,0.03424]}],"total_contact_groups":12},"final_pose_error":0.0149,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.6015,0.17771,0.10406],"final_tcp_position":[0.5956,0.17511,0.12131],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"phases":[{"n_steps":253.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"grasp_position","tcp_end":[0.52268,0.02587,0.16725],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14153,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":277.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"grasp_position","tcp_end":[0.52475,0.02979,0.04446],"tcp_start":[0.52268,0.02587,0.16725],"tcp_to_object_dist_end":0.01935,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53047,0.02988,0.02552],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18434,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.51583,0.02922,0.0342],"tcp_start":[0.52475,0.02979,0.04446],"tcp_to_object_dist_end":0.01703,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":435.0,"n_steps_budget":1000.0,"object_pos_end":[0.526,0.02973,0.1527],"object_pos_start":[0.53047,0.02988,0.02552],"object_to_goal_dist_end":0.17278,"object_to_goal_dist_start":0.18434,"object_z_max":0.15244,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"placement_accuracy","tcp_end":[0.51216,0.02898,0.16486],"tcp_start":[0.51583,0.02922,0.0342],"tcp_to_object_dist_end":0.01843,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":467.0,"n_steps_budget":1000.0,"object_pos_end":[0.59829,0.16874,0.20027],"object_pos_start":[0.526,0.02973,0.1527],"object_to_goal_dist_end":0.09276,"object_to_goal_dist_start":0.17278,"object_z_max":0.20019,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","tcp_end":[0.59179,0.16665,0.21558],"tcp_start":[0.51216,0.02898,0.16486],"tcp_to_object_dist_end":0.01677,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":222.0,"n_steps_budget":1000.0,"object_pos_end":[0.6015,0.17771,0.10406],"object_pos_start":[0.59829,0.16874,0.20027],"object_to_goal_dist_end":0.00413,"object_to_goal_dist_start":0.09276,"object_z_max":0.20027,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"placement_accuracy","tcp_end":[0.5956,0.17511,0.12131],"tcp_start":[0.59179,0.16665,0.21558],"tcp_to_object_dist_end":0.01842,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```