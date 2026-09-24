## Search State

- **Seed**: 3
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → descend → release → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 11 | -0.0137 | 0.48 | ✅ accepted |
| 2 | rotate → retract → descend → pull → rotate | impedance_motion | arc_cartesian | linear_cartesian | arc_cartesian | arc_cartesian | position_control | position_control | admittance_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 3 | 0.0374 | 0.17 | ❌ rejected |
| 1 | rotate → retract → descend → pull → rotate | impedance_motion | arc_cartesian | linear_cartesian | arc_cartesian | arc_cartesian | position_control | position_control | admittance_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 3 | 0.0374 | 0.17 | ❌ rejected |
| 0 | rotate → retract → descend → pull → rotate | impedance_motion | arc_cartesian | linear_cartesian | arc_cartesian | arc_cartesian | position_control | position_control | admittance_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 3 | 0.0374 | 0.17 | ✅ accepted |

**Proposal policy**: task_score is 0.48 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
- task_score stagnant: change coupled targets, parameters, terminations, phase types, controls, subtasks, or ordering when evidence shows they need to change together.
A HOLD wastes an iteration when task_score is below 0.9.

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

## Current Skill (Q=-0.014) — your mutation base

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
  type: release
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
    - 0.005
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
      - 0.0
      - 0.02
      default: 0.005
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
- id: release
  type: release
  control: position_control
  termination: time_limit
  end_effector_action: open
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
  parameters:
    release_duration:
      type: scalar
      range:
      - 0.5
      - 2.0
      default: 1.0
      binds_to:
      - path: duration.max_time
        mode: replace
- id: retract
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.2
    tolerance: 0.02
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.12
      - 0.25
      default: 0.2
      binds_to:
      - path: target.offset.z
        mode: replace
    retract_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace

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
- **grasp** (`release`)
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
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.005], tolerance=0.01
  - parameter_bindings:
    - place_speed: status=consumed; consumers=generator.speed (replace)
    - place_z_offset: status=consumed; consumers=target.offset.z (replace)
  - guards:
    - id=contact_place, when=during_phase, predicate=contact_detected, on_failure=continue, threshold=1.0
- **release** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - release_duration: status=consumed; consumers=duration.max_time (replace)
- **retract** (`retract`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.2], tolerance=0.02
  - parameter_bindings:
    - retract_height: status=consumed; consumers=target.offset.z (replace)
    - retract_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: -0.014
- **task_score** (E): 0.480
- **fitness_score**: 0.716  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.730

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_object | 1.00 | 0.1435 |
| descend_grasp | 1.00 | 0.1244 |
| grasp | 1.00 | 0.0128 |
| lift | 1.00 | 0.1313 |
| transport_to_goal | 0.67 | 0.2048 |
| descend_place | 1.00 | 0.0919 |
| release | 1.00 | 0.0209 |
| retract | 1.00 | 0.1251 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.002, 0.163) | (0.511, 0.002, 0.030)→(0.511, 0.002, 0.026) | 0.244→0.246 |
| descend_grasp | descend | 1.00 / step_budget | (0.506, 0.002, 0.163)→(0.506, 0.002, 0.039) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 |
| grasp | release | 1.00 / step_budget | (0.506, 0.002, 0.039)→(0.497, 0.002, 0.029) | (0.511, 0.002, 0.026)→(0.510, 0.002, 0.025) | 0.246→0.246 |
| lift | lift | 1.00 / step_budget | (0.497, 0.002, 0.029)→(0.493, 0.001, 0.160) | (0.510, 0.002, 0.025)→(0.504, 0.002, 0.151) | 0.246→0.223 |
| transport_to_goal | approach | 0.67 / step_budget | (0.493, 0.001, 0.160)→(0.603, 0.154, 0.235) | (0.504, 0.002, 0.151)→(0.605, 0.155, 0.221) | 0.223→0.092 |
| descend_place | descend | 1.00 / step_budget | (0.603, 0.154, 0.235)→(0.620, 0.177, 0.149) | (0.605, 0.155, 0.221)→(0.620, 0.178, 0.134) | 0.092→0.009 |
| release | release | 1.00 / step_budget | (0.620, 0.177, 0.149)→(0.613, 0.175, 0.169) | (0.620, 0.178, 0.134)→(0.608, 0.172, 0.025) | 0.009→0.115 |
| retract | retract | 1.00 / step_budget | (0.613, 0.175, 0.169)→(0.623, 0.180, 0.294) | (0.608, 0.172, 0.025)→(0.604, 0.172, 0.026) | 0.115→0.114 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.567
- phase_score: 0.696
- phase_breakdown.pre_grasp_approach_score: 0.745
- phase_breakdown.lift_clearance_score: 0.509
- phase_breakdown.placement_accuracy_score: 0.669
- phase_breakdown.grasp_position_score: 0.817
- grasp_place_fitness: 0.758

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.758
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.567
- **Median Q (composite search score)**: 0.024
- **K-run variance**: 0.0031
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.297


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.62332,"average_solve_count":223.0,"average_success_count":223.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.18571,"descend_grasp.descend_speed":0.04613,"descend_grasp.descend_z_offset":-0.00703,"descend_place.place_speed":0.07069,"descend_place.place_z_offset":0.00145,"lift.lift_height":0.1304,"lift.lift_speed":0.05805,"release.release_duration":1.28436,"retract.retract_height":0.15627,"retract.retract_speed":0.11899,"transport_to_goal.transport_speed":0.15112},"optimized_scores":{"best_composite_score":0.02376,"best_fitness_score":0.75376,"best_task_score":0.54613},"replay_outcomes":[{"contacts":{"omitted_contact_groups":2,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":320.0,"contact_point_centroid":[0.61161,0.19693,-0.00425],"force_p95":0.68697,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.97817,"mean_force":0.21526,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.61527,0.20042,0.12299]},{"body_a":"world","body_b":"grasp_target","contact_count":120.0,"contact_point_centroid":[0.45309,-0.02555,-0.00161],"force_p95":0.70504,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.81735,"mean_force":0.18405,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44436,-0.0256,0.02205]},{"body_a":"grasp_target","body_b":"hand","contact_count":367.0,"contact_point_centroid":[0.47173,-0.01488,0.08875],"force_p95":0.16676,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.50981,"mean_force":0.10491,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44178,-0.02552,0.05705]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12430.0,"contact_point_centroid":[0.44239,-0.00643,0.07874],"force_p95":0.07173,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24928,"mean_force":0.04762,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44173,-0.02551,0.07752]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10810.0,"contact_point_centroid":[0.44043,-0.04469,0.08226],"force_p95":0.07681,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24319,"mean_force":0.05315,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44173,-0.02551,0.07999]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45805,-0.02616,-0.00253],"force_p95":0.18772,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22973,"mean_force":0.15927,"phase_index":2.0,"phase_name":"grasp","phase_type":"release","tcp_position_centroid":[0.44689,-0.02567,0.02117]},{"body_a":"grasp_target","body_b":"hand","contact_count":416.0,"contact_point_centroid":[0.47562,-0.02684,0.05321],"force_p95":0.16458,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19933,"mean_force":0.14812,"phase_index":2.0,"phase_name":"grasp","phase_type":"release","tcp_position_centroid":[0.44644,-0.02566,0.02076]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1214.0,"contact_point_centroid":[0.61489,0.22022,0.1149],"force_p95":0.06911,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15718,"mean_force":0.0422,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.61991,0.20203,0.11111]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1242.0,"contact_point_centroid":[0.62478,0.18332,0.11099],"force_p95":0.07173,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1495,"mean_force":0.04314,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.61987,0.20202,0.11104]},{"body_a":"world","body_b":"grasp_target","contact_count":1200.0,"contact_point_centroid":[0.45856,-0.02632,-0.00189],"force_p95":0.13608,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12303,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48022,-0.011,0.23319]},{"body_a":"world","body_b":"grasp_target","contact_count":1824.0,"contact_point_centroid":[0.61162,0.19686,-0.00198],"force_p95":0.12419,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13044,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.6194,0.20313,0.1925]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8600.0,"contact_point_centroid":[0.59955,0.19954,0.16071],"force_p95":0.06894,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12759,"mean_force":0.04852,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.60432,0.18125,0.15731]},{"body_a":"world","body_b":"grasp_target","contact_count":1908.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.4558,-0.02432,0.09529]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8600.0,"contact_point_centroid":[0.60901,0.16258,0.15769],"force_p95":0.07107,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11404,"mean_force":0.05007,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.60432,0.18125,0.15731]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20462.0,"contact_point_centroid":[0.5177,0.05061,0.17167],"force_p95":0.0699,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1027,"mean_force":0.04844,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51547,0.06962,0.17032]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4431.0,"contact_point_centroid":[0.44454,-0.04491,0.02285],"force_p95":0.07837,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10142,"mean_force":0.04972,"phase_index":2.0,"phase_name":"grasp","phase_type":"release","tcp_position_centroid":[0.4457,-0.02564,0.02007]}],"total_contact_groups":18},"final_pose_error":0.01991,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.61163,0.19686,0.02602],"final_tcp_position":[0.6262,0.2066,0.25093],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"phases":[{"n_steps":301.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"pre_grasp_approach","tcp_end":[0.46052,-0.02289,0.16416],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1382,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":477.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"grasp_position","tcp_end":[0.454,-0.02586,0.02783],"tcp_start":[0.46052,-0.02289,0.16416],"tcp_to_object_dist_end":0.00494,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45687,-0.02596,0.02449],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30478,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"release","tcp_end":[0.44567,-0.02563,0.02004],"tcp_start":[0.454,-0.02586,0.02783],"tcp_to_object_dist_end":0.01205,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":565.0,"n_steps_budget":1000.0,"object_pos_end":[0.45268,-0.02594,0.13687],"object_pos_start":[0.45687,-0.02596,0.02449],"object_to_goal_dist_end":0.29467,"object_to_goal_dist_start":0.30478,"object_z_max":0.13669,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"lift_clearance","tcp_end":[0.44182,-0.0255,0.13598],"tcp_start":[0.44567,-0.02563,0.02004],"tcp_to_object_dist_end":0.0109,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58824,0.15995,0.2034],"object_pos_start":[0.45268,-0.02594,0.13687],"object_to_goal_dist_end":0.10979,"object_to_goal_dist_start":0.29467,"object_z_max":0.20334,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","tcp_end":[0.58861,0.15989,0.20648],"tcp_start":[0.44182,-0.0255,0.13598],"tcp_to_object_dist_end":0.00311,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":430.0,"n_steps_budget":1000.0,"object_pos_end":[0.61836,0.20206,0.1092],"object_pos_start":[0.58824,0.15995,0.2034],"object_to_goal_dist_end":0.01416,"object_to_goal_dist_start":0.10979,"object_z_max":0.2034,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"placement_accuracy","tcp_end":[0.62198,0.20254,0.11496],"tcp_start":[0.58861,0.15989,0.20648],"tcp_to_object_dist_end":0.00682,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61154,0.19685,0.02643],"object_pos_start":[0.61836,0.20206,0.1092],"object_to_goal_dist_end":0.09036,"object_to_goal_dist_start":0.01416,"object_z_max":0.1092,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","tcp_end":[0.61514,0.20038,0.1347],"tcp_start":[0.62198,0.20254,0.11496],"tcp_to_object_dist_end":0.10839,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":456.0,"n_steps_budget":720.0,"object_pos_end":[0.61163,0.19686,0.02602],"object_pos_start":[0.61154,0.19685,0.02643],"object_to_goal_dist_end":0.09073,"object_to_goal_dist_start":0.09036,"object_z_max":0.02643,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.6262,0.2066,0.25093],"tcp_start":[0.61514,0.20038,0.1347],"tcp_to_object_dist_end":0.22559,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.7268,"average_solve_count":194.0,"average_success_count":194.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.16702,"descend_grasp.descend_speed":0.09549,"descend_grasp.descend_z_offset":0.0105,"descend_place.place_speed":0.0567,"descend_place.place_z_offset":0.00929,"lift.lift_height":0.14722,"lift.lift_speed":0.06564,"release.release_duration":1.14428,"retract.retract_height":0.2187,"retract.retract_speed":0.11356,"transport_to_goal.transport_speed":0.13416},"optimized_scores":{"best_composite_score":-0.09263,"best_fitness_score":0.63737,"best_task_score":0.32755},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":172.0,"contact_point_centroid":[0.6264,0.14926,-0.0085],"force_p95":1.39146,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.59723,"mean_force":0.44057,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.63513,0.15152,0.21659]},{"body_a":"world","body_b":"grasp_target","contact_count":104.0,"contact_point_centroid":[0.5399,0.00084,-0.0013],"force_p95":0.48876,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.56169,"mean_force":0.12801,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52827,0.00079,0.03523]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13022.0,"contact_point_centroid":[0.52643,0.01989,0.10342],"force_p95":0.08061,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31371,"mean_force":0.05753,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52531,0.00075,0.10111]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14510.0,"contact_point_centroid":[0.52632,-0.01827,0.09958],"force_p95":0.07692,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29352,"mean_force":0.05242,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52532,0.00075,0.09753]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1219.0,"contact_point_centroid":[0.63617,0.17151,0.20504],"force_p95":0.06882,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28149,"mean_force":0.04387,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.63871,0.15256,0.20075]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1404.0,"contact_point_centroid":[0.64326,0.13382,0.20147],"force_p95":0.06462,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23184,"mean_force":0.03934,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.63871,0.15256,0.20075]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5066.0,"contact_point_centroid":[0.62932,0.16073,0.24572],"force_p95":0.07063,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22787,"mean_force":0.05035,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.63172,0.14176,0.24169]},{"body_a":"world","body_b":"grasp_target","contact_count":2533.0,"contact_point_centroid":[0.62162,0.14919,-0.00201],"force_p95":0.13814,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20897,"mean_force":0.12294,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.63936,0.1542,0.30812]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5834.0,"contact_point_centroid":[0.63618,0.12309,0.24264],"force_p95":0.06789,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18396,"mean_force":0.04552,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.63173,0.14177,0.24165]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18808.0,"contact_point_centroid":[0.58017,0.05189,0.22551],"force_p95":0.08331,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16902,"mean_force":0.05444,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.57717,0.07073,0.22438]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18516.0,"contact_point_centroid":[0.57645,0.0902,0.22677],"force_p95":0.0814,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15912,"mean_force":0.05464,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.57756,0.07125,0.22483]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5443,0.00116,-0.00203],"force_p95":0.13335,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15384,"mean_force":0.12533,"phase_index":2.0,"phase_name":"grasp","phase_type":"release","tcp_position_centroid":[0.53081,0.00085,0.03545]},{"body_a":"world","body_b":"grasp_target","contact_count":1284.0,"contact_point_centroid":[0.54431,0.00113,-0.0019],"force_p95":0.13564,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12301,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51653,0.00045,0.2315]},{"body_a":"world","body_b":"grasp_target","contact_count":1436.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.53547,0.00095,0.10238]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4840.0,"contact_point_centroid":[0.53076,-0.01823,0.03563],"force_p95":0.0686,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10199,"mean_force":0.04466,"phase_index":2.0,"phase_name":"grasp","phase_type":"release","tcp_position_centroid":[0.52954,0.00083,0.03397]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4149.0,"contact_point_centroid":[0.53083,0.02004,0.03652],"force_p95":0.07523,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09584,"mean_force":0.0518,"phase_index":2.0,"phase_name":"grasp","phase_type":"release","tcp_position_centroid":[0.52954,0.00083,0.03397]}],"total_contact_groups":16},"final_pose_error":0.01981,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.62124,0.14916,0.02602],"final_tcp_position":[0.64574,0.15727,0.3901],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"phases":[{"n_steps":322.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"pre_grasp_approach","tcp_end":[0.53541,0.00093,0.16202],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1363,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":359.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"grasp_position","tcp_end":[0.53838,0.00101,0.04438],"tcp_start":[0.53541,0.00093,0.16202],"tcp_to_object_dist_end":0.0193,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54418,0.00106,0.02587],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25032,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"release","tcp_end":[0.52951,0.00083,0.03393],"tcp_start":[0.53838,0.00101,0.04438],"tcp_to_object_dist_end":0.01674,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":736.0,"n_steps_budget":1000.0,"object_pos_end":[0.53645,0.00082,0.15274],"object_pos_start":[0.54418,0.00106,0.02587],"object_to_goal_dist_end":0.19637,"object_to_goal_dist_start":0.25032,"object_z_max":0.15259,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"lift_clearance","tcp_end":[0.52566,0.00076,0.16674],"tcp_start":[0.52951,0.00083,0.03393],"tcp_to_object_dist_end":0.01767,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.63044,0.13382,0.25897],"object_pos_start":[0.53645,0.00082,0.15274],"object_to_goal_dist_end":0.0741,"object_to_goal_dist_start":0.19637,"object_z_max":0.25886,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","tcp_end":[0.62531,0.13204,0.27937],"tcp_start":[0.52566,0.00076,0.16674],"tcp_to_object_dist_end":0.02111,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":254.0,"n_steps_budget":1000.0,"object_pos_end":[0.64499,0.15517,0.18337],"object_pos_start":[0.63044,0.13382,0.25897],"object_to_goal_dist_end":0.00867,"object_to_goal_dist_start":0.0741,"object_z_max":0.25898,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"placement_accuracy","tcp_end":[0.64048,0.15285,0.205],"tcp_start":[0.62531,0.13204,0.27937],"tcp_to_object_dist_end":0.02221,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.63132,0.14925,0.02308],"object_pos_start":[0.64499,0.15517,0.18337],"object_to_goal_dist_end":0.16904,"object_to_goal_dist_start":0.00867,"object_z_max":0.18337,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","tcp_end":[0.63509,0.15152,0.22421],"tcp_start":[0.64048,0.15285,0.205],"tcp_to_object_dist_end":0.20117,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":645.0,"n_steps_budget":1000.0,"object_pos_end":[0.62124,0.14916,0.02602],"object_pos_start":[0.63132,0.14925,0.02308],"object_to_goal_dist_end":0.16742,"object_to_goal_dist_start":0.16904,"object_z_max":0.02742,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.64574,0.15727,0.3901],"tcp_start":[0.63509,0.15152,0.22421],"tcp_to_object_dist_end":0.365,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.12214,"average_solve_count":262.0,"average_success_count":262.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.13237,"descend_grasp.descend_speed":0.09398,"descend_grasp.descend_z_offset":0.00933,"descend_place.place_speed":0.02128,"descend_place.place_z_offset":0.01133,"lift.lift_height":0.15954,"lift.lift_speed":0.04674,"release.release_duration":1.98368,"retract.retract_height":0.15103,"retract.retract_speed":0.12401,"transport_to_goal.transport_speed":0.17212},"optimized_scores":{"best_composite_score":0.02769,"best_fitness_score":0.75769,"best_task_score":0.56689},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":316.0,"contact_point_centroid":[0.58044,0.1713,-0.00416],"force_p95":0.78366,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.23146,"mean_force":0.2228,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.58957,0.17416,0.13628]},{"body_a":"world","body_b":"grasp_target","contact_count":115.0,"contact_point_centroid":[0.526,0.02904,-0.00138],"force_p95":0.4517,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.50033,"mean_force":0.13203,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51475,0.02937,0.03467]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14025.0,"contact_point_centroid":[0.51233,0.0484,0.10794],"force_p95":0.08247,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27148,"mean_force":0.05913,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51195,0.0292,0.1052]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17127.0,"contact_point_centroid":[0.51346,0.01025,0.10546],"force_p95":0.07805,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2484,"mean_force":0.04981,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51195,0.0292,0.10373]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1345.0,"contact_point_centroid":[0.59933,0.15681,0.12444],"force_p95":0.06659,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21543,"mean_force":0.04065,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.59395,0.1755,0.12335]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53055,0.03075,-0.00211],"force_p95":0.15539,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21439,"mean_force":0.13125,"phase_index":2.0,"phase_name":"grasp","phase_type":"release","tcp_position_centroid":[0.51737,0.02956,0.03477]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1324.0,"contact_point_centroid":[0.59007,0.19406,0.12761],"force_p95":0.06459,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21427,"mean_force":0.03988,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.59398,0.17551,0.12339]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5824.0,"contact_point_centroid":[0.58938,0.19137,0.17589],"force_p95":0.06917,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19134,"mean_force":0.04716,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.59393,0.173,0.17247]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13982.0,"contact_point_centroid":[0.55631,0.08359,0.19792],"force_p95":0.07128,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16801,"mean_force":0.0483,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55332,0.10244,0.1966]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5270.0,"contact_point_centroid":[0.51728,0.01045,0.03536],"force_p95":0.06676,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16714,"mean_force":0.04109,"phase_index":2.0,"phase_name":"grasp","phase_type":"release","tcp_position_centroid":[0.51612,0.02947,0.03335]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5760.0,"contact_point_centroid":[0.59863,0.15431,0.17345],"force_p95":0.07067,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16179,"mean_force":0.04879,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.59391,0.17297,0.17283]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12299.0,"contact_point_centroid":[0.55204,0.12388,0.20068],"force_p95":0.07812,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16011,"mean_force":0.05314,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5549,0.10508,0.19742]},{"body_a":"world","body_b":"grasp_target","contact_count":1368.0,"contact_point_centroid":[0.58014,0.17116,-0.00198],"force_p95":0.13516,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14402,"mean_force":0.12265,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.59227,0.17534,0.19341]},{"body_a":"world","body_b":"grasp_target","contact_count":1336.0,"contact_point_centroid":[0.5305,0.03079,-0.0019],"force_p95":0.13564,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12299,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51053,0.01302,0.23162]},{"body_a":"world","body_b":"grasp_target","contact_count":1468.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.52264,0.02836,0.10207]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4225.0,"contact_point_centroid":[0.51674,0.0488,0.03615],"force_p95":0.08108,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08463,"mean_force":0.05178,"phase_index":2.0,"phase_name":"grasp","phase_type":"release","tcp_position_centroid":[0.51612,0.02947,0.03336]}],"total_contact_groups":16},"final_pose_error":0.01999,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.58014,0.17116,0.02602],"final_tcp_position":[0.59738,0.1772,0.23962],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"phases":[{"n_steps":335.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"pre_grasp_approach","tcp_end":[0.52332,0.02686,0.16224],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13647,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":367.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"grasp_position","tcp_end":[0.52485,0.03004,0.04334],"tcp_start":[0.52332,0.02686,0.16224],"tcp_to_object_dist_end":0.01824,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53044,0.03006,0.0256],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18417,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"release","tcp_end":[0.51609,0.02947,0.03332],"tcp_start":[0.52485,0.03004,0.04334],"tcp_to_object_dist_end":0.01631,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":825.0,"n_steps_budget":1000.0,"object_pos_end":[0.52266,0.02991,0.16454],"object_pos_start":[0.53044,0.03006,0.0256],"object_to_goal_dist_end":0.17751,"object_to_goal_dist_start":0.18417,"object_z_max":0.16438,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"lift_clearance","tcp_end":[0.51236,0.02923,0.17845],"tcp_start":[0.51609,0.02947,0.03332],"tcp_to_object_dist_end":0.01732,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":670.0,"n_steps_budget":1000.0,"object_pos_end":[0.59583,0.17207,0.2002],"object_pos_start":[0.52266,0.02991,0.16454],"object_to_goal_dist_end":0.09252,"object_to_goal_dist_start":0.17751,"object_z_max":0.20017,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","tcp_end":[0.59403,0.17064,0.21784],"tcp_start":[0.51236,0.02923,0.17845],"tcp_to_object_dist_end":0.01779,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":286.0,"n_steps_budget":1000.0,"object_pos_end":[0.59764,0.1779,0.10835],"object_pos_start":[0.59583,0.17207,0.2002],"object_to_goal_dist_end":0.00396,"object_to_goal_dist_start":0.09252,"object_z_max":0.2002,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"placement_accuracy","tcp_end":[0.59615,0.17611,0.12731],"tcp_start":[0.59403,0.17064,0.21784],"tcp_to_object_dist_end":0.01911,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58026,0.17119,0.02651],"object_pos_start":[0.59764,0.1779,0.10835],"object_to_goal_dist_end":0.08463,"object_to_goal_dist_start":0.00396,"object_z_max":0.10835,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","tcp_end":[0.58944,0.17412,0.14791],"tcp_start":[0.59615,0.17611,0.12731],"tcp_to_object_dist_end":0.12178,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":342.0,"n_steps_budget":600.0,"object_pos_end":[0.58014,0.17116,0.02602],"object_pos_start":[0.58026,0.17119,0.02651],"object_to_goal_dist_end":0.08514,"object_to_goal_dist_start":0.08463,"object_z_max":0.02651,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.59738,0.1772,0.23962],"tcp_start":[0.58944,0.17412,0.14791],"tcp_to_object_dist_end":0.21438,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```