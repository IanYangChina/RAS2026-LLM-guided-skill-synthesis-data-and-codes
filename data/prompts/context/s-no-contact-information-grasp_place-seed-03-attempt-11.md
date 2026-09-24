## Search State

- **Seed**: 3
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | time_limit | pose_tolerance | 9 | 0.3766 | 0.94 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.4581 | 1.00 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.4581 | 1.00 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.4580 | 1.00 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.4581 | 1.00 | ❌ rejected |

**Proposal policy**: task_score is near-perfect (0.94). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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

## Current Skill (Q=0.377) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
subtasks:
- id: pre_grasp_approach
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.12
  weight: 0.2
- id: grasp_position
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.005
  weight: 0.3
- id: lift_clearance
  anchor: object
  target_entity: object
  offset:
  - 0.0
  - 0.0
  - 0.12
  weight: 0.2
- id: placement_accuracy
  target_entity: object
  weight: 0.3
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
    tolerance: 0.015
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
  subtask_id: pre_grasp_approach
- id: descend_grasp
  type: descend
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.005
    tolerance: 0.01
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
    descend_z_offset:
      type: scalar
      range:
      - -0.01
      - 0.02
      default: 0.005
      binds_to:
      - path: target.offset.z
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
    tolerance: 0.015
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
  subtask_id: lift_clearance
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
    tolerance: 0.015
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
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.01
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
    place_z_offset:
      type: scalar
      range:
      - -0.01
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: replace
  guards:
  - id: contact_place
    when: during_phase
    predicate: contact_detected
    threshold: 1.0
    on_failure: continue
  subtask_id: placement_accuracy

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.12], tolerance=0.015
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.005], tolerance=0.01
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - descend_z_offset: status=consumed; consumers=target.offset.z (replace)
  - guards:
    - id=contact_check, when=during_phase, predicate=contact_detected, on_failure=continue, threshold=1.0
- **grasp** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=bilateral_grasp, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.005, 0.005, 0.0]
- **lift** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.12], tolerance=0.015
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=object_lifted_check, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.03
  - retries: max_attempts=1, strategy=reduce_speed
- **transport_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.12], tolerance=0.015
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **descend_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - parameter_bindings:
    - place_speed: status=consumed; consumers=generator.speed (replace)
    - place_z_offset: status=consumed; consumers=target.offset.z (replace)
  - guards:
    - id=contact_place, when=during_phase, predicate=contact_detected, on_failure=continue, threshold=1.0

## Design Metrics

- **Composite score**: 0.377
- **task_score** (E): 0.937
- **fitness_score**: 0.947  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.570

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_object | 1.00 | 0.1435 |
| descend_grasp | 1.00 | 0.1292 |
| grasp | 1.00 | 0.0129 |
| lift | 1.00 | 0.1320 |
| transport_to_goal | 1.00 | 0.1358 |
| descend_place | 1.00 | 0.1047 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.002, 0.163) | (0.511, 0.002, 0.030)→(0.511, 0.002, 0.026) | 0.244→0.246 |
| descend_grasp | descend | 1.00 / step_budget | (0.506, 0.002, 0.163)→(0.506, 0.002, 0.034) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 |
| grasp | grasp | 1.00 / step_budget | (0.506, 0.002, 0.034)→(0.497, 0.002, 0.024) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.025) | 0.246→0.246 |
| lift | lift | 1.00 / step_budget | (0.497, 0.002, 0.024)→(0.493, 0.001, 0.156) | (0.511, 0.002, 0.025)→(0.508, 0.001, 0.150) | 0.246→0.220 |
| transport_to_goal | approach | 1.00 / time_limit | (0.493, 0.001, 0.156)→(0.564, 0.102, 0.207) | (0.508, 0.001, 0.150)→(0.571, 0.104, 0.192) | 0.220→0.113 |
| descend_place | descend | 1.00 / step_budget | (0.564, 0.102, 0.207)→(0.612, 0.168, 0.146) | (0.571, 0.104, 0.192)→(0.616, 0.170, 0.126) | 0.113→0.021 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.414
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.773
- phase_breakdown.pre_grasp_approach_score: 0.746
- phase_breakdown.lift_clearance_score: 0.601
- phase_breakdown.placement_accuracy_score: 0.789
- phase_breakdown.grasp_position_score: 0.891
- grasp_place_fitness: 0.977

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.977
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.407
- **K-run variance**: 0.0018
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.322


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.53012,"average_solve_count":166.0,"average_success_count":166.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.17795,"descend_grasp.descend_speed":0.05642,"descend_grasp.descend_z_offset":-0.00572,"descend_place.place_speed":0.05895,"descend_place.place_z_offset":0.00452,"lift.lift_height":0.1712,"lift.lift_speed":0.13371,"transport_to_goal.transport_speed":0.19968,"transport_to_goal.transport_time_limit":591.7514},"optimized_scores":{"best_composite_score":0.31622,"best_fitness_score":0.88622,"best_task_score":0.81214},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":110.0,"contact_point_centroid":[0.45552,-0.02522,-0.00146],"force_p95":0.77569,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.93431,"mean_force":0.14223,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44427,-0.0256,0.02348]},{"body_a":"grasp_target","body_b":"hand","contact_count":175.0,"contact_point_centroid":[0.47387,-0.0199,0.07253],"force_p95":0.13126,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.60611,"mean_force":0.08896,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44223,-0.02554,0.04151]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10249.0,"contact_point_centroid":[0.44278,-0.04468,0.09543],"force_p95":0.10505,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31172,"mean_force":0.06482,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44185,-0.02551,0.09295]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12426.0,"contact_point_centroid":[0.44425,-0.0067,0.09354],"force_p95":0.09352,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31008,"mean_force":0.05523,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44184,-0.02551,0.09209]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14240.0,"contact_point_centroid":[0.49559,0.0205,0.18886],"force_p95":0.10488,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23615,"mean_force":0.07057,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.49107,0.0392,0.18812]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45809,-0.02634,-0.00244],"force_p95":0.1754,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2051,"mean_force":0.15289,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44691,-0.02567,0.02236]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15464.0,"contact_point_centroid":[0.49329,0.05837,0.1888],"force_p95":0.09866,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17206,"mean_force":0.06355,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.49139,0.03959,0.18821]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17246.0,"contact_point_centroid":[0.56941,0.16037,0.16134],"force_p95":0.08893,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15265,"mean_force":0.05612,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.57151,0.14136,0.16032]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18274.0,"contact_point_centroid":[0.57833,0.12486,0.15762],"force_p95":0.07754,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14966,"mean_force":0.0544,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.57294,0.1431,0.15897]},{"body_a":"grasp_target","body_b":"hand","contact_count":395.0,"contact_point_centroid":[0.47703,-0.02536,0.05351],"force_p95":0.13185,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14827,"mean_force":0.1141,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44623,-0.02565,0.02173]},{"body_a":"world","body_b":"grasp_target","contact_count":1200.0,"contact_point_centroid":[0.45856,-0.02632,-0.00189],"force_p95":0.13608,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12303,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48022,-0.011,0.23319]},{"body_a":"world","body_b":"grasp_target","contact_count":1884.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.45581,-0.02433,0.09585]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5276.0,"contact_point_centroid":[0.44659,-0.00656,0.0226],"force_p95":0.06746,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10373,"mean_force":0.04126,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44572,-0.02564,0.02126]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4420.0,"contact_point_centroid":[0.44503,-0.04492,0.02399],"force_p95":0.07993,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09588,"mean_force":0.04959,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44572,-0.02564,0.02126]}],"total_contact_groups":14},"final_pose_error":0.0367,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.60985,0.18552,0.10719],"final_tcp_position":[0.60555,0.18271,0.12826],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"phases":[{"n_steps":301.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"pre_grasp_approach","tcp_end":[0.46052,-0.02289,0.16416],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1382,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":471.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"grasp_position","tcp_end":[0.45399,-0.02586,0.02902],"tcp_start":[0.46052,-0.02289,0.16416],"tcp_to_object_dist_end":0.00549,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45759,-0.02592,0.02471],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30427,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.44569,-0.02564,0.02123],"tcp_start":[0.45399,-0.02586,0.02902],"tcp_to_object_dist_end":0.01241,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":649.0,"n_steps_budget":810.0,"object_pos_end":[0.46029,-0.02639,0.16958],"object_pos_start":[0.45759,-0.02592,0.02471],"object_to_goal_dist_end":0.29489,"object_to_goal_dist_start":0.30427,"object_z_max":0.16941,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"lift_clearance","tcp_end":[0.44223,-0.02551,0.17786],"tcp_start":[0.44569,-0.02564,0.02123],"tcp_to_object_dist_end":0.01989,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54411,0.09826,0.18431],"object_pos_start":[0.46029,-0.02639,0.16958],"object_to_goal_dist_end":0.15625,"object_to_goal_dist_start":0.29489,"object_z_max":0.18429,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","tcp_end":[0.53739,0.09668,0.20089],"tcp_start":[0.44223,-0.02551,0.17786],"tcp_to_object_dist_end":0.01796,"terminated_normally":true,"termination_reason":"time_limit"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.60985,0.18552,0.10719],"object_pos_start":[0.54411,0.09826,0.18431],"object_to_goal_dist_end":0.03121,"object_to_goal_dist_start":0.15625,"object_z_max":0.18431,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"placement_accuracy","tcp_end":[0.60555,0.18271,0.12826],"tcp_start":[0.53739,0.09668,0.20089],"tcp_to_object_dist_end":0.02169,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.9078,"average_solve_count":141.0,"average_success_count":141.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.17502,"descend_grasp.descend_speed":0.09228,"descend_grasp.descend_z_offset":0.00275,"descend_place.place_speed":0.05962,"descend_place.place_z_offset":0.00847,"lift.lift_height":0.14612,"lift.lift_speed":0.07611,"transport_to_goal.transport_speed":0.16032,"transport_to_goal.transport_time_limit":927.8305},"optimized_scores":{"best_composite_score":0.40654,"best_fitness_score":0.97654,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":98.0,"contact_point_centroid":[0.53943,0.00015,-0.00124],"force_p95":0.6644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.73942,"mean_force":0.15302,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52812,0.0008,0.02754]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13405.0,"contact_point_centroid":[0.52615,0.01984,0.0915],"force_p95":0.07804,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33672,"mean_force":0.05404,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52514,0.00075,0.08934]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13187.0,"contact_point_centroid":[0.52628,-0.01836,0.09281],"force_p95":0.07848,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33319,"mean_force":0.05462,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52514,0.00075,0.09055]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54429,0.00113,-0.00203],"force_p95":0.13339,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15234,"mean_force":0.12536,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53069,0.00085,0.02763]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13360.0,"contact_point_centroid":[0.61213,0.13833,0.20812],"force_p95":0.09283,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15226,"mean_force":0.07056,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.61314,0.1192,0.20611]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18274.0,"contact_point_centroid":[0.61772,0.10105,0.20531],"force_p95":0.0767,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14824,"mean_force":0.05399,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.61315,0.11924,0.20603]},{"body_a":"world","body_b":"grasp_target","contact_count":1284.0,"contact_point_centroid":[0.54431,0.00113,-0.0019],"force_p95":0.13564,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12301,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51653,0.00045,0.2315]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18201.0,"contact_point_centroid":[0.5549,0.02089,0.19079],"force_p95":0.08391,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12808,"mean_force":0.05558,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5525,0.03981,0.18981]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17897.0,"contact_point_centroid":[0.55222,0.05835,0.19061],"force_p95":0.08152,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1239,"mean_force":0.05576,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5521,0.03931,0.18932]},{"body_a":"world","body_b":"grasp_target","contact_count":1536.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.53541,0.00095,0.09849]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4735.0,"contact_point_centroid":[0.53069,-0.01824,0.02791],"force_p95":0.06863,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09794,"mean_force":0.04528,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.5294,0.00082,0.02616]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4255.0,"contact_point_centroid":[0.53072,0.02003,0.02854],"force_p95":0.07471,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09475,"mean_force":0.05095,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.5294,0.00082,0.02616]}],"total_contact_groups":12},"final_pose_error":0.01585,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.64131,0.15039,0.17385],"final_tcp_position":[0.63652,0.14814,0.19418],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"phases":[{"n_steps":322.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"pre_grasp_approach","tcp_end":[0.53541,0.00093,0.16202],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1363,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":384.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"grasp_position","tcp_end":[0.53836,0.00101,0.03656],"tcp_start":[0.53541,0.00093,0.16202],"tcp_to_object_dist_end":0.0121,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54415,0.00081,0.02588],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25048,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.52937,0.00083,0.02612],"tcp_start":[0.53836,0.00101,0.03656],"tcp_to_object_dist_end":0.01478,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":698.0,"n_steps_budget":1000.0,"object_pos_end":[0.53841,0.0008,0.15128],"object_pos_start":[0.54415,0.00081,0.02588],"object_to_goal_dist_end":0.19558,"object_to_goal_dist_start":0.25048,"object_z_max":0.15112,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"lift_clearance","tcp_end":[0.52545,0.00076,0.15788],"tcp_start":[0.52937,0.00083,0.02612],"tcp_to_object_dist_end":0.01454,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.59349,0.08222,0.21408],"object_pos_start":[0.53841,0.0008,0.15128],"object_to_goal_dist_end":0.09599,"object_to_goal_dist_start":0.19558,"object_z_max":0.21402,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","tcp_end":[0.58432,0.08038,0.22846],"tcp_start":[0.52545,0.00076,0.15788],"tcp_to_object_dist_end":0.01715,"terminated_normally":true,"termination_reason":"time_limit"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.64131,0.15039,0.17385],"object_pos_start":[0.59349,0.08222,0.21408],"object_to_goal_dist_end":0.01992,"object_to_goal_dist_start":0.09599,"object_z_max":0.21408,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"placement_accuracy","tcp_end":[0.63652,0.14814,0.19418],"tcp_start":[0.58432,0.08038,0.22846],"tcp_to_object_dist_end":0.02102,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.05691,"average_solve_count":123.0,"average_success_count":123.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.17341,"descend_grasp.descend_speed":0.10037,"descend_grasp.descend_z_offset":0.0014,"descend_place.place_speed":0.07025,"descend_place.place_z_offset":0.00659,"lift.lift_height":0.12189,"lift.lift_speed":0.09131,"transport_to_goal.transport_speed":0.16981,"transport_to_goal.transport_time_limit":1250.16544},"optimized_scores":{"best_composite_score":0.40695,"best_fitness_score":0.97695,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":104.0,"contact_point_centroid":[0.52694,0.02895,-0.00132],"force_p95":0.62419,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.78123,"mean_force":0.13621,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.5146,0.02938,0.02697]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9197.0,"contact_point_centroid":[0.51237,0.04841,0.08139],"force_p95":0.08338,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35248,"mean_force":0.06008,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51169,0.0292,0.07868]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11249.0,"contact_point_centroid":[0.51337,0.01026,0.07915],"force_p95":0.07992,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32894,"mean_force":0.0507,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51171,0.02921,0.07743]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53056,0.03069,-0.00212],"force_p95":0.157,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23117,"mean_force":0.13166,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51721,0.02957,0.02677]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5250.0,"contact_point_centroid":[0.51715,0.01047,0.02739],"force_p95":0.06624,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14887,"mean_force":0.04107,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51593,0.02949,0.02535]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7654.0,"contact_point_centroid":[0.58496,0.13298,0.14878],"force_p95":0.08244,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14769,"mean_force":0.05394,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.58042,0.15123,0.14923]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19822.0,"contact_point_centroid":[0.54112,0.05952,0.15886],"force_p95":0.07908,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14378,"mean_force":0.05199,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53777,0.07813,0.15821]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6048.0,"contact_point_centroid":[0.57763,0.16987,0.15301],"force_p95":0.09057,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14206,"mean_force":0.06348,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.58032,0.15107,0.1495]},{"body_a":"world","body_b":"grasp_target","contact_count":1268.0,"contact_point_centroid":[0.5305,0.03079,-0.00189],"force_p95":0.13591,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12301,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51062,0.01302,0.23171]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16377.0,"contact_point_centroid":[0.53656,0.09643,0.16031],"force_p95":0.09038,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13434,"mean_force":0.06133,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53728,0.07732,0.15771]},{"body_a":"world","body_b":"grasp_target","contact_count":1552.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.52263,0.02838,0.09783]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4230.0,"contact_point_centroid":[0.51664,0.04883,0.02813],"force_p95":0.08072,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08878,"mean_force":0.05195,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51594,0.02949,0.02536]}],"total_contact_groups":12},"final_pose_error":0.00996,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.59718,0.17479,0.09788],"final_tcp_position":[0.59376,0.17237,0.11452],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"phases":[{"n_steps":318.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"pre_grasp_approach","tcp_end":[0.52331,0.02687,0.16217],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13639,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":388.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"grasp_position","tcp_end":[0.52478,0.03006,0.03532],"tcp_start":[0.52331,0.02687,0.16217],"tcp_to_object_dist_end":0.01094,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5304,0.02991,0.02559],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18431,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.5159,0.02948,0.02532],"tcp_start":[0.52478,0.03006,0.03532],"tcp_to_object_dist_end":0.01451,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":541.0,"n_steps_budget":840.0,"object_pos_end":[0.52558,0.02986,0.12792],"object_pos_start":[0.5304,0.02991,0.02559],"object_to_goal_dist_end":0.16816,"object_to_goal_dist_start":0.18431,"object_z_max":0.12776,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"lift_clearance","tcp_end":[0.51181,0.02922,0.13284],"tcp_start":[0.5159,0.02948,0.02532],"tcp_to_object_dist_end":0.01464,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.57683,0.13218,0.17671],"object_pos_start":[0.52558,0.02986,0.12792],"object_to_goal_dist_end":0.08644,"object_to_goal_dist_start":0.16816,"object_z_max":0.17667,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","tcp_end":[0.56904,0.12979,0.19025],"tcp_start":[0.51181,0.02922,0.13284],"tcp_to_object_dist_end":0.0158,"terminated_normally":true,"termination_reason":"time_limit"},{"n_steps":378.0,"n_steps_budget":1000.0,"object_pos_end":[0.59718,0.17479,0.09788],"object_pos_start":[0.57683,0.13218,0.17671],"object_to_goal_dist_end":0.01172,"object_to_goal_dist_start":0.08644,"object_z_max":0.17671,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"placement_accuracy","tcp_end":[0.59376,0.17237,0.11452],"tcp_start":[0.56904,0.12979,0.19025],"tcp_to_object_dist_end":0.01716,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```