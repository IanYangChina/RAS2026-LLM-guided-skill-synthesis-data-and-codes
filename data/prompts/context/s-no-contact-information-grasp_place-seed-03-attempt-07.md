## Search State

- **Seed**: 3
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.4581 | 1.00 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.4581 | 1.00 | ✅ accepted |
| 5 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.4581 | 1.00 | ✅ accepted |
| 4 | approach → descend → release → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 11 | -0.0124 | 0.48 | ✅ accepted |
| 3 | approach → descend → release → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 11 | -0.0137 | 0.48 | ✅ accepted |

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

## Current Skill (Q=0.458) — your mutation base

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

- **Composite score**: 0.458
- **task_score** (E): 1.000
- **fitness_score**: 0.978  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.520

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_object | 1.00 | 0.1435 |
| descend_grasp | 1.00 | 0.1297 |
| grasp | 1.00 | 0.0129 |
| lift | 1.00 | 0.1267 |
| transport_to_goal | 0.67 | 0.2003 |
| descend_place | 1.00 | 0.0989 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.002, 0.163) | (0.511, 0.002, 0.030)→(0.511, 0.002, 0.026) | 0.244→0.246 |
| descend_grasp | descend | 1.00 / step_budget | (0.506, 0.002, 0.163)→(0.506, 0.002, 0.033) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 |
| grasp | grasp | 1.00 / step_budget | (0.506, 0.002, 0.033)→(0.497, 0.002, 0.024) | (0.511, 0.002, 0.026)→(0.510, 0.002, 0.025) | 0.246→0.247 |
| lift | lift | 1.00 / step_budget | (0.497, 0.002, 0.024)→(0.493, 0.001, 0.150) | (0.510, 0.002, 0.025)→(0.506, 0.002, 0.146) | 0.247→0.218 |
| transport_to_goal | approach | 0.67 / step_budget | (0.493, 0.001, 0.150)→(0.599, 0.150, 0.232) | (0.506, 0.002, 0.146)→(0.606, 0.152, 0.220) | 0.218→0.097 |
| descend_place | descend | 1.00 / step_budget | (0.599, 0.150, 0.232)→(0.620, 0.178, 0.147) | (0.606, 0.152, 0.220)→(0.626, 0.181, 0.131) | 0.097→0.007 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.631
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.742
- phase_breakdown.pre_grasp_approach_score: 0.745
- phase_breakdown.lift_clearance_score: 0.421
- phase_breakdown.placement_accuracy_score: 0.860
- phase_breakdown.grasp_position_score: 0.837
- grasp_place_fitness: 0.981

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.981
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.457
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.325


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.78125,"average_solve_count":160.0,"average_success_count":160.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.19947,"descend_grasp.descend_speed":0.09394,"descend_grasp.descend_z_offset":-0.00759,"descend_place.place_speed":0.06089,"descend_place.place_z_offset":0.00698,"lift.lift_height":0.10491,"lift.lift_speed":0.08667,"transport_to_goal.transport_speed":0.11979},"optimized_scores":{"best_composite_score":0.46072,"best_fitness_score":0.98072,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":114.0,"contact_point_centroid":[0.4533,-0.02572,-0.00164],"force_p95":0.74697,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.93568,"mean_force":0.15718,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.4444,-0.0256,0.02168]},{"body_a":"grasp_target","body_b":"hand","contact_count":366.0,"contact_point_centroid":[0.47196,-0.01018,0.09164],"force_p95":0.17802,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.59625,"mean_force":0.10888,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.4419,-0.02553,0.05987]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7308.0,"contact_point_centroid":[0.44055,-0.04471,0.06701],"force_p95":0.07803,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28784,"mean_force":0.05656,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44187,-0.02552,0.06438]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8932.0,"contact_point_centroid":[0.44259,-0.00649,0.06565],"force_p95":0.0744,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26912,"mean_force":0.04828,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44187,-0.02552,0.06438]},{"body_a":"grasp_target","body_b":"hand","contact_count":423.0,"contact_point_centroid":[0.47521,-0.03062,0.05311],"force_p95":0.17591,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23797,"mean_force":0.15798,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44661,-0.02567,0.02029]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45802,-0.02615,-0.00257],"force_p95":0.1911,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23409,"mean_force":0.16137,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44698,-0.02568,0.02063]},{"body_a":"world","body_b":"grasp_target","contact_count":1200.0,"contact_point_centroid":[0.45856,-0.02632,-0.00189],"force_p95":0.13608,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12303,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48022,-0.011,0.23319]},{"body_a":"world","body_b":"grasp_target","contact_count":1764.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.45598,-0.02433,0.09505]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16620.0,"contact_point_centroid":[0.59428,0.19316,0.14793],"force_p95":0.06983,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11179,"mean_force":0.0483,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.59887,0.17482,0.14455]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16620.0,"contact_point_centroid":[0.60345,0.15613,0.14495],"force_p95":0.07147,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10845,"mean_force":0.04992,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.59887,0.17482,0.14455]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20207.0,"contact_point_centroid":[0.50789,0.03922,0.15091],"force_p95":0.07221,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10489,"mean_force":0.04995,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50603,0.0583,0.14924]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4430.0,"contact_point_centroid":[0.44459,-0.04492,0.02227],"force_p95":0.07838,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1015,"mean_force":0.04984,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44579,-0.02565,0.01953]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5258.0,"contact_point_centroid":[0.44655,-0.00655,0.02076],"force_p95":0.06951,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09981,"mean_force":0.04135,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44578,-0.02565,0.01952]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20980.0,"contact_point_centroid":[0.50346,0.07632,0.15102],"force_p95":0.07118,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09466,"mean_force":0.04782,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50527,0.05736,0.14875]}],"total_contact_groups":14},"final_pose_error":0.01,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.62827,0.2064,0.10721],"final_tcp_position":[0.62358,0.20446,0.11454],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"phases":[{"n_steps":301.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"pre_grasp_approach","tcp_end":[0.46052,-0.02289,0.16416],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1382,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":441.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"grasp_position","tcp_end":[0.4541,-0.02587,0.02731],"tcp_start":[0.46052,-0.02289,0.16416],"tcp_to_object_dist_end":0.00466,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45671,-0.02599,0.02446],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.3049,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.44576,-0.02564,0.0195],"tcp_start":[0.4541,-0.02587,0.02731],"tcp_to_object_dist_end":0.01204,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":406.0,"n_steps_budget":780.0,"object_pos_end":[0.45303,-0.02609,0.1121],"object_pos_start":[0.45671,-0.02599,0.02446],"object_to_goal_dist_end":0.29371,"object_to_goal_dist_start":0.3049,"object_z_max":0.11192,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"lift_clearance","tcp_end":[0.44176,-0.02551,0.11014],"tcp_start":[0.44576,-0.02564,0.0195],"tcp_to_object_dist_end":0.01146,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.57608,0.13843,0.1861],"object_pos_start":[0.45303,-0.02609,0.1121],"object_to_goal_dist_end":0.1139,"object_to_goal_dist_start":0.29371,"object_z_max":0.18604,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","tcp_end":[0.56981,0.13697,0.18952],"tcp_start":[0.44176,-0.02551,0.11014],"tcp_to_object_dist_end":0.00728,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":831.0,"n_steps_budget":1000.0,"object_pos_end":[0.62827,0.2064,0.10721],"object_pos_start":[0.57608,0.13843,0.1861],"object_to_goal_dist_end":0.00738,"object_to_goal_dist_start":0.1139,"object_z_max":0.1861,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"placement_accuracy","tcp_end":[0.62358,0.20446,0.11454],"tcp_start":[0.56981,0.13697,0.18952],"tcp_to_object_dist_end":0.00891,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.82249,"average_solve_count":169.0,"average_success_count":169.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.19738,"descend_grasp.descend_speed":0.09923,"descend_grasp.descend_z_offset":0.00225,"descend_place.place_speed":0.05602,"descend_place.place_z_offset":0.00811,"lift.lift_height":0.18189,"lift.lift_speed":0.08207,"transport_to_goal.transport_speed":0.11772},"optimized_scores":{"best_composite_score":0.4565,"best_fitness_score":0.9765,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":99.0,"contact_point_centroid":[0.53966,0.00035,-0.00127],"force_p95":0.69048,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.75265,"mean_force":0.16029,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.5281,0.0008,0.02715]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16681.0,"contact_point_centroid":[0.52623,0.01984,0.10868],"force_p95":0.07798,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33994,"mean_force":0.05408,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52521,0.00075,0.10651]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16483.0,"contact_point_centroid":[0.52636,-0.01835,0.11009],"force_p95":0.07838,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33685,"mean_force":0.05448,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52521,0.00075,0.10785]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4336.0,"contact_point_centroid":[0.63215,0.16549,0.25269],"force_p95":0.08678,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19703,"mean_force":0.05822,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.63574,0.14677,0.24961]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5136.0,"contact_point_centroid":[0.64035,0.12857,0.24841],"force_p95":0.07041,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18044,"mean_force":0.04954,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.63595,0.14705,0.24792]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54429,0.00113,-0.00203],"force_p95":0.13339,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15228,"mean_force":0.12536,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53067,0.00085,0.02734]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19307.0,"contact_point_centroid":[0.58401,0.05655,0.24281],"force_p95":0.08152,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15149,"mean_force":0.05334,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5809,0.07522,0.24227]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17168.0,"contact_point_centroid":[0.58016,0.09474,0.24471],"force_p95":0.0901,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14424,"mean_force":0.05936,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.58133,0.07577,0.24266]},{"body_a":"world","body_b":"grasp_target","contact_count":1284.0,"contact_point_centroid":[0.54431,0.00113,-0.0019],"force_p95":0.13564,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12301,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51653,0.00045,0.2315]},{"body_a":"world","body_b":"grasp_target","contact_count":1532.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.53543,0.00095,0.09831]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4726.0,"contact_point_centroid":[0.53067,-0.01824,0.02762],"force_p95":0.06863,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09776,"mean_force":0.04535,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52938,0.00082,0.02587]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4264.0,"contact_point_centroid":[0.5307,0.02003,0.02824],"force_p95":0.0747,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0948,"mean_force":0.05087,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52938,0.00082,0.02587]}],"total_contact_groups":12},"final_pose_error":0.00994,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.6454,0.15638,0.18844],"final_tcp_position":[0.64163,0.15426,0.20616],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"phases":[{"n_steps":322.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"pre_grasp_approach","tcp_end":[0.53541,0.00093,0.16202],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1363,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":383.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"grasp_position","tcp_end":[0.53835,0.00101,0.03627],"tcp_start":[0.53541,0.00093,0.16202],"tcp_to_object_dist_end":0.01186,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54415,0.0008,0.02588],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25049,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.52935,0.00083,0.02583],"tcp_start":[0.53835,0.00101,0.03627],"tcp_to_object_dist_end":0.0148,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":874.0,"n_steps_budget":1000.0,"object_pos_end":[0.53824,0.00083,0.18554],"object_pos_start":[0.54415,0.0008,0.02588],"object_to_goal_dist_end":0.19164,"object_to_goal_dist_start":0.25049,"object_z_max":0.18538,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"lift_clearance","tcp_end":[0.52577,0.00077,0.19316],"tcp_start":[0.52935,0.00083,0.02583],"tcp_to_object_dist_end":0.01462,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.63686,0.14252,0.27395],"object_pos_start":[0.53824,0.00083,0.18554],"object_to_goal_dist_end":0.08499,"object_to_goal_dist_start":0.19164,"object_z_max":0.27386,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","tcp_end":[0.63226,0.14085,0.29008],"tcp_start":[0.52577,0.00077,0.19316],"tcp_to_object_dist_end":0.01685,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":253.0,"n_steps_budget":1000.0,"object_pos_end":[0.6454,0.15638,0.18844],"object_pos_start":[0.63686,0.14252,0.27395],"object_to_goal_dist_end":0.00387,"object_to_goal_dist_start":0.08499,"object_z_max":0.27396,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"placement_accuracy","tcp_end":[0.64163,0.15426,0.20616],"tcp_start":[0.63226,0.14085,0.29008],"tcp_to_object_dist_end":0.01825,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.02174,"average_solve_count":138.0,"average_success_count":138.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.25807,"descend_grasp.descend_speed":0.13507,"descend_grasp.descend_z_offset":0.00181,"descend_place.place_speed":0.07939,"descend_place.place_z_offset":0.00398,"lift.lift_height":0.1363,"lift.lift_speed":0.10755,"transport_to_goal.transport_speed":0.09546},"optimized_scores":{"best_composite_score":0.45698,"best_fitness_score":0.97698,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":99.0,"contact_point_centroid":[0.5267,0.02867,-0.00136],"force_p95":0.54866,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.78464,"mean_force":0.12505,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51462,0.02938,0.02758]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10305.0,"contact_point_centroid":[0.51281,0.04843,0.08856],"force_p95":0.10785,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35906,"mean_force":0.06027,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51178,0.0292,0.08641]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12157.0,"contact_point_centroid":[0.51385,0.01054,0.08715],"force_p95":0.08489,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33739,"mean_force":0.05158,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51181,0.0292,0.08561]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2324.0,"contact_point_centroid":[0.59403,0.19256,0.17547],"force_p95":0.16107,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25046,"mean_force":0.10852,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.59415,0.17324,0.17587]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53056,0.03069,-0.00212],"force_p95":0.15698,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23055,"mean_force":0.13165,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51723,0.02956,0.02745]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3662.0,"contact_point_centroid":[0.60166,0.15705,0.16824],"force_p95":0.11969,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1941,"mean_force":0.07379,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.5943,0.17353,0.17021]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10849.0,"contact_point_centroid":[0.5532,0.12131,0.18241],"force_p95":0.11697,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16315,"mean_force":0.08179,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55262,0.10206,0.18091]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14599.0,"contact_point_centroid":[0.55781,0.084,0.18068],"force_p95":0.09197,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16029,"mean_force":0.05981,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55246,0.10176,0.18078]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5252.0,"contact_point_centroid":[0.51717,0.01046,0.02807],"force_p95":0.06625,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14736,"mean_force":0.04107,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51596,0.02948,0.02603]},{"body_a":"world","body_b":"grasp_target","contact_count":1268.0,"contact_point_centroid":[0.5305,0.03079,-0.00189],"force_p95":0.13591,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12301,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51062,0.01302,0.23171]},{"body_a":"world","body_b":"grasp_target","contact_count":1496.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.52264,0.02838,0.09831]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4230.0,"contact_point_centroid":[0.51666,0.04882,0.02882],"force_p95":0.08073,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0885,"mean_force":0.05194,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51596,0.02948,0.02604]}],"total_contact_groups":12},"final_pose_error":0.00995,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.604,0.17918,0.09859],"final_tcp_position":[0.59623,0.1763,0.12017],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"phases":[{"n_steps":318.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"pre_grasp_approach","tcp_end":[0.52331,0.02687,0.16217],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13639,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":374.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"grasp_position","tcp_end":[0.5248,0.03006,0.03601],"tcp_start":[0.52331,0.02687,0.16217],"tcp_to_object_dist_end":0.01152,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53041,0.02991,0.02559],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.1843,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.51593,0.02948,0.02599],"tcp_start":[0.5248,0.03006,0.03601],"tcp_to_object_dist_end":0.01449,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":594.0,"n_steps_budget":810.0,"object_pos_end":[0.52655,0.03,0.13918],"object_pos_start":[0.53041,0.02991,0.02559],"object_to_goal_dist_end":0.16931,"object_to_goal_dist_start":0.1843,"object_z_max":0.13902,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"lift_clearance","tcp_end":[0.512,0.02922,0.14796],"tcp_start":[0.51593,0.02948,0.02599],"tcp_to_object_dist_end":0.01702,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":881.0,"n_steps_budget":1000.0,"object_pos_end":[0.60619,0.17513,0.20044],"object_pos_start":[0.52655,0.03,0.13918],"object_to_goal_dist_end":0.09253,"object_to_goal_dist_start":0.16931,"object_z_max":0.20038,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","tcp_end":[0.59455,0.17156,0.21689],"tcp_start":[0.512,0.02922,0.14796],"tcp_to_object_dist_end":0.02046,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":274.0,"n_steps_budget":1000.0,"object_pos_end":[0.604,0.17918,0.09859],"object_pos_start":[0.60619,0.17513,0.20044],"object_to_goal_dist_end":0.00983,"object_to_goal_dist_start":0.09253,"object_z_max":0.20044,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"placement_accuracy","tcp_end":[0.59623,0.1763,0.12017],"tcp_start":[0.59455,0.17156,0.21689],"tcp_to_object_dist_end":0.02312,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```