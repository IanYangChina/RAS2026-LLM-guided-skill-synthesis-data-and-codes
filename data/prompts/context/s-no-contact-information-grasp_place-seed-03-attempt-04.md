## Search State

- **Seed**: 3
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → descend → release → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 11 | -0.0124 | 0.48 | ✅ accepted |
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

## Current Skill (Q=-0.012) — your mutation base

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

- **Composite score**: -0.012
- **task_score** (E): 0.480
- **fitness_score**: 0.718  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.730

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_object | 1.00 | 0.1436 |
| descend_grasp | 1.00 | 0.1270 |
| grasp | 1.00 | 0.0128 |
| lift | 1.00 | 0.1550 |
| transport_to_goal | 0.67 | 0.2114 |
| descend_place | 1.00 | 0.0983 |
| release | 1.00 | 0.0208 |
| retract | 1.00 | 0.1391 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.002, 0.163) | (0.511, 0.002, 0.030)→(0.511, 0.002, 0.026) | 0.244→0.246 |
| descend_grasp | descend | 1.00 / step_budget | (0.506, 0.002, 0.163)→(0.506, 0.002, 0.036) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 |
| grasp | release | 1.00 / step_budget | (0.506, 0.002, 0.036)→(0.497, 0.002, 0.026) | (0.511, 0.002, 0.026)→(0.510, 0.002, 0.025) | 0.246→0.246 |
| lift | lift | 1.00 / step_budget | (0.497, 0.002, 0.026)→(0.493, 0.001, 0.181) | (0.510, 0.002, 0.025)→(0.505, 0.002, 0.174) | 0.246→0.226 |
| transport_to_goal | approach | 0.67 / step_budget | (0.493, 0.001, 0.181)→(0.609, 0.162, 0.244) | (0.505, 0.002, 0.174)→(0.608, 0.162, 0.232) | 0.226→0.101 |
| descend_place | descend | 1.00 / step_budget | (0.609, 0.162, 0.244)→(0.620, 0.178, 0.150) | (0.608, 0.162, 0.232)→(0.620, 0.179, 0.136) | 0.101→0.008 |
| release | release | 1.00 / step_budget | (0.620, 0.178, 0.150)→(0.614, 0.176, 0.169) | (0.620, 0.179, 0.136)→(0.610, 0.174, 0.025) | 0.008→0.114 |
| retract | retract | 1.00 / step_budget | (0.614, 0.176, 0.169)→(0.623, 0.181, 0.308) | (0.610, 0.174, 0.025)→(0.605, 0.173, 0.026) | 0.114→0.114 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.564
- phase_score: 0.734
- phase_breakdown.pre_grasp_approach_score: 0.746
- phase_breakdown.lift_clearance_score: 0.393
- phase_breakdown.placement_accuracy_score: 0.815
- phase_breakdown.grasp_position_score: 0.874
- grasp_place_fitness: 0.759

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.759
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.564
- **Median Q (composite search score)**: 0.025
- **K-run variance**: 0.0031
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.376


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.59073,"average_solve_count":259.0,"average_success_count":259.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.2017,"descend_grasp.descend_speed":0.07912,"descend_grasp.descend_z_offset":-0.00745,"descend_place.place_speed":0.05984,"descend_place.place_z_offset":0.00791,"lift.lift_height":0.17122,"lift.lift_speed":0.03668,"release.release_duration":1.43426,"retract.retract_height":0.2416,"retract.retract_speed":0.15535,"transport_to_goal.transport_speed":0.14149},"optimized_scores":{"best_composite_score":0.02499,"best_fitness_score":0.75499,"best_task_score":0.54874},"replay_outcomes":[{"contacts":{"omitted_contact_groups":2,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":305.0,"contact_point_centroid":[0.61505,0.19733,-0.00454],"force_p95":0.74855,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.21776,"mean_force":0.22742,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.61539,0.20037,0.13089]},{"body_a":"world","body_b":"grasp_target","contact_count":128.0,"contact_point_centroid":[0.45287,-0.02575,-0.00168],"force_p95":0.65511,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.71588,"mean_force":0.19803,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44427,-0.0256,0.02137]},{"body_a":"grasp_target","body_b":"hand","contact_count":427.0,"contact_point_centroid":[0.47124,-0.0115,0.09351],"force_p95":0.1815,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.46649,"mean_force":0.11446,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44171,-0.02552,0.0615]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45802,-0.02615,-0.00256],"force_p95":0.19063,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23374,"mean_force":0.16113,"phase_index":2.0,"phase_name":"grasp","phase_type":"release","tcp_position_centroid":[0.44687,-0.02568,0.02073]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15276.0,"contact_point_centroid":[0.44046,-0.04467,0.10306],"force_p95":0.07726,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22061,"mean_force":0.05158,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44176,-0.02551,0.10097]},{"body_a":"grasp_target","body_b":"hand","contact_count":422.0,"contact_point_centroid":[0.47524,-0.03067,0.05313],"force_p95":0.17486,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20595,"mean_force":0.15719,"phase_index":2.0,"phase_name":"grasp","phase_type":"release","tcp_position_centroid":[0.4465,-0.02567,0.02038]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16849.0,"contact_point_centroid":[0.44254,-0.00642,0.09734],"force_p95":0.07294,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20268,"mean_force":0.04794,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44175,-0.02551,0.09608]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1214.0,"contact_point_centroid":[0.61492,0.22014,0.12231],"force_p95":0.06908,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15619,"mean_force":0.04222,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.61994,0.20195,0.11853]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1238.0,"contact_point_centroid":[0.62481,0.18324,0.11847],"force_p95":0.07177,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14833,"mean_force":0.0433,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.6199,0.20194,0.11847]},{"body_a":"world","body_b":"grasp_target","contact_count":2752.0,"contact_point_centroid":[0.61515,0.19739,-0.00198],"force_p95":0.12415,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13927,"mean_force":0.12259,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.61999,0.20327,0.23893]},{"body_a":"world","body_b":"grasp_target","contact_count":1200.0,"contact_point_centroid":[0.45856,-0.02632,-0.00189],"force_p95":0.13608,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12303,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48022,-0.011,0.23319]},{"body_a":"world","body_b":"grasp_target","contact_count":1792.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.45585,-0.02433,0.09515]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8480.0,"contact_point_centroid":[0.6006,0.20079,0.16929],"force_p95":0.0696,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12077,"mean_force":0.04834,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.60541,0.1825,0.16589]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8480.0,"contact_point_centroid":[0.6101,0.16384,0.16627],"force_p95":0.07192,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10367,"mean_force":0.04991,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.60541,0.1825,0.16589]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4431.0,"contact_point_centroid":[0.44451,-0.04492,0.02239],"force_p95":0.07836,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10147,"mean_force":0.04982,"phase_index":2.0,"phase_name":"grasp","phase_type":"release","tcp_position_centroid":[0.44568,-0.02564,0.01963]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5258.0,"contact_point_centroid":[0.44646,-0.00655,0.02088],"force_p95":0.06948,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09995,"mean_force":0.04135,"phase_index":2.0,"phase_name":"grasp","phase_type":"release","tcp_position_centroid":[0.44568,-0.02564,0.01963]}],"total_contact_groups":18},"final_pose_error":0.0198,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.61515,0.19739,0.02602],"final_tcp_position":[0.62765,0.2071,0.33611],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"phases":[{"n_steps":301.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"pre_grasp_approach","tcp_end":[0.46052,-0.02289,0.16416],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1382,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":448.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"grasp_position","tcp_end":[0.454,-0.02587,0.02741],"tcp_start":[0.46052,-0.02289,0.16416],"tcp_to_object_dist_end":0.0048,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45673,-0.02599,0.02447],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30488,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"release","tcp_end":[0.44565,-0.02564,0.0196],"tcp_start":[0.454,-0.02587,0.02741],"tcp_to_object_dist_end":0.01211,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":781.0,"n_steps_budget":1000.0,"object_pos_end":[0.45282,-0.02595,0.17668],"object_pos_start":[0.45673,-0.02599,0.02447],"object_to_goal_dist_end":0.30031,"object_to_goal_dist_start":0.30488,"object_z_max":0.17649,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"lift_clearance","tcp_end":[0.44211,-0.02551,0.17634],"tcp_start":[0.44565,-0.02564,0.0196],"tcp_to_object_dist_end":0.01072,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58593,0.16186,0.21148],"object_pos_start":[0.45282,-0.02595,0.17668],"object_to_goal_dist_end":0.11654,"object_to_goal_dist_start":0.30031,"object_z_max":0.21146,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","tcp_end":[0.59112,0.16296,0.21535],"tcp_start":[0.44211,-0.02551,0.17634],"tcp_to_object_dist_end":0.00657,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":424.0,"n_steps_budget":1000.0,"object_pos_end":[0.61843,0.20199,0.11682],"object_pos_start":[0.58593,0.16186,0.21148],"object_to_goal_dist_end":0.01352,"object_to_goal_dist_start":0.11654,"object_z_max":0.21148,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"placement_accuracy","tcp_end":[0.62199,0.20246,0.12243],"tcp_start":[0.59112,0.16296,0.21535],"tcp_to_object_dist_end":0.00666,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61482,0.19743,0.02648],"object_pos_start":[0.61843,0.20199,0.11682],"object_to_goal_dist_end":0.08961,"object_to_goal_dist_start":0.01352,"object_z_max":0.11682,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","tcp_end":[0.61528,0.20033,0.14212],"tcp_start":[0.62199,0.20246,0.12243],"tcp_to_object_dist_end":0.11568,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":688.0,"n_steps_budget":870.0,"object_pos_end":[0.61515,0.19739,0.02602],"object_pos_start":[0.61482,0.19743,0.02648],"object_to_goal_dist_end":0.09002,"object_to_goal_dist_start":0.08961,"object_z_max":0.02649,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.62765,0.2071,0.33611],"tcp_start":[0.61528,0.20033,0.14212],"tcp_to_object_dist_end":0.31049,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.77487,"average_solve_count":191.0,"average_success_count":191.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.10493,"descend_grasp.descend_speed":0.11068,"descend_grasp.descend_z_offset":0.00779,"descend_place.place_speed":0.05243,"descend_place.place_z_offset":0.01052,"lift.lift_height":0.1581,"lift.lift_speed":0.06704,"release.release_duration":1.29484,"retract.retract_height":0.1737,"retract.retract_speed":0.19557,"transport_to_goal.transport_speed":0.18449},"optimized_scores":{"best_composite_score":-0.09091,"best_fitness_score":0.63909,"best_task_score":0.32782},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":125.0,"contact_point_centroid":[0.6347,0.15417,-0.01019],"force_p95":1.4703,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.80956,"mean_force":0.60904,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.63786,0.15466,0.22041]},{"body_a":"world","body_b":"grasp_target","contact_count":104.0,"contact_point_centroid":[0.53982,0.00082,-0.00129],"force_p95":0.52597,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60552,"mean_force":0.13637,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52816,0.00079,0.03248]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14136.0,"contact_point_centroid":[0.52638,0.01988,0.1061],"force_p95":0.08055,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31744,"mean_force":0.05724,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52521,0.00075,0.10382]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15558.0,"contact_point_centroid":[0.52628,-0.01828,0.10212],"force_p95":0.07719,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29852,"mean_force":0.05272,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52523,0.00075,0.10007]},{"body_a":"world","body_b":"grasp_target","contact_count":1480.0,"contact_point_centroid":[0.62399,0.15224,-0.00227],"force_p95":0.24414,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25561,"mean_force":0.13753,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.64096,0.15587,0.29326]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1279.0,"contact_point_centroid":[0.6381,0.17444,0.21025],"force_p95":0.06713,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20118,"mean_force":0.04185,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.64135,0.15565,0.20584]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1457.0,"contact_point_centroid":[0.64543,0.13673,0.20744],"force_p95":0.06302,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19751,"mean_force":0.03797,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.64135,0.15565,0.20582]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5060.0,"contact_point_centroid":[0.63655,0.17211,0.25913],"force_p95":0.06879,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18654,"mean_force":0.04722,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.64116,0.15361,0.25597]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18845.0,"contact_point_centroid":[0.58907,0.0636,0.24043],"force_p95":0.08004,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18194,"mean_force":0.05367,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.58664,0.08266,0.23903]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20317.0,"contact_point_centroid":[0.58406,0.10095,0.24081],"force_p95":0.07368,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16872,"mean_force":0.04906,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.58622,0.08217,0.23857]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5241.0,"contact_point_centroid":[0.64481,0.13474,0.25615],"force_p95":0.06657,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16007,"mean_force":0.04638,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.64118,0.15366,0.25512]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5443,0.00115,-0.00203],"force_p95":0.13338,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15339,"mean_force":0.12529,"phase_index":2.0,"phase_name":"grasp","phase_type":"release","tcp_position_centroid":[0.53072,0.00085,0.03269]},{"body_a":"world","body_b":"grasp_target","contact_count":1388.0,"contact_point_centroid":[0.54431,0.00113,-0.0019],"force_p95":0.1356,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12298,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51634,0.00045,0.23135]},{"body_a":"world","body_b":"grasp_target","contact_count":1448.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.53542,0.00095,0.10082]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4840.0,"contact_point_centroid":[0.53069,-0.01823,0.03285],"force_p95":0.06862,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10073,"mean_force":0.04464,"phase_index":2.0,"phase_name":"grasp","phase_type":"release","tcp_position_centroid":[0.52944,0.00083,0.03121]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4149.0,"contact_point_centroid":[0.53077,0.02004,0.03374],"force_p95":0.07524,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0963,"mean_force":0.05182,"phase_index":2.0,"phase_name":"grasp","phase_type":"release","tcp_position_centroid":[0.52944,0.00083,0.03121]}],"total_contact_groups":16},"final_pose_error":0.01999,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.62127,0.15171,0.02602],"final_tcp_position":[0.64516,0.15727,0.34498],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"phases":[{"n_steps":348.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"pre_grasp_approach","tcp_end":[0.53535,0.00094,0.16177],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13605,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":362.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"grasp_position","tcp_end":[0.53832,0.00101,0.04161],"tcp_start":[0.53535,0.00094,0.16177],"tcp_to_object_dist_end":0.0167,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54417,0.00104,0.02587],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25033,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"release","tcp_end":[0.52941,0.00082,0.03117],"tcp_start":[0.53832,0.00101,0.04161],"tcp_to_object_dist_end":0.01568,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":795.0,"n_steps_budget":1000.0,"object_pos_end":[0.53678,0.00083,0.16298],"object_pos_start":[0.54417,0.00104,0.02587],"object_to_goal_dist_end":0.19444,"object_to_goal_dist_start":0.25033,"object_z_max":0.16282,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"lift_clearance","tcp_end":[0.52563,0.00076,0.1749],"tcp_start":[0.52941,0.00082,0.03117],"tcp_to_object_dist_end":0.01633,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.64449,0.15339,0.279],"object_pos_start":[0.53678,0.00083,0.16298],"object_to_goal_dist_end":0.08808,"object_to_goal_dist_start":0.19444,"object_z_max":0.27892,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","tcp_end":[0.64086,0.15181,0.29741],"tcp_start":[0.52563,0.00076,0.1749],"tcp_to_object_dist_end":0.01883,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":243.0,"n_steps_budget":1000.0,"object_pos_end":[0.64563,0.15785,0.19056],"object_pos_start":[0.64449,0.15339,0.279],"object_to_goal_dist_end":0.00208,"object_to_goal_dist_start":0.08808,"object_z_max":0.279,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"placement_accuracy","tcp_end":[0.64313,0.1561,0.2103],"tcp_start":[0.64086,0.15181,0.29741],"tcp_to_object_dist_end":0.01998,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.63778,0.15428,0.02338],"object_pos_start":[0.64563,0.15785,0.19056],"object_to_goal_dist_end":0.16806,"object_to_goal_dist_start":0.00208,"object_z_max":0.19056,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","tcp_end":[0.63782,0.15465,0.22925],"tcp_start":[0.64313,0.1561,0.2103],"tcp_to_object_dist_end":0.20587,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":426.0,"n_steps_budget":600.0,"object_pos_end":[0.62127,0.15171,0.02602],"object_pos_start":[0.63778,0.15428,0.02338],"object_to_goal_dist_end":0.1673,"object_to_goal_dist_start":0.16806,"object_z_max":0.03036,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.64516,0.15727,0.34498],"tcp_start":[0.63782,0.15465,0.22925],"tcp_to_object_dist_end":0.3199,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.84772,"average_solve_count":197.0,"average_success_count":197.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.21723,"descend_grasp.descend_speed":0.07424,"descend_grasp.descend_z_offset":0.00449,"descend_place.place_speed":0.05467,"descend_place.place_z_offset":0.00041,"lift.lift_height":0.17897,"lift.lift_speed":0.07088,"release.release_duration":0.75194,"retract.retract_height":0.15501,"retract.retract_speed":0.1366,"transport_to_goal.transport_speed":0.14572},"optimized_scores":{"best_composite_score":0.02859,"best_fitness_score":0.75859,"best_task_score":0.56411},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":323.0,"contact_point_centroid":[0.57798,0.17127,-0.00389],"force_p95":0.85494,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.98329,"mean_force":0.22045,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.58936,0.17416,0.12519]},{"body_a":"world","body_b":"grasp_target","contact_count":104.0,"contact_point_centroid":[0.52609,0.02859,-0.00133],"force_p95":0.56658,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.67763,"mean_force":0.14333,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51463,0.02938,0.02994]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14467.0,"contact_point_centroid":[0.51228,0.04841,0.11287],"force_p95":0.08236,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33234,"mean_force":0.05939,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51184,0.02921,0.11014]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17593.0,"contact_point_centroid":[0.51344,0.01026,0.11018],"force_p95":0.07846,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30909,"mean_force":0.05029,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51183,0.02921,0.10847]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53056,0.03071,-0.00211],"force_p95":0.15593,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2189,"mean_force":0.13136,"phase_index":2.0,"phase_name":"grasp","phase_type":"release","tcp_position_centroid":[0.51721,0.02956,0.02989]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1215.0,"contact_point_centroid":[0.58939,0.19393,0.11598],"force_p95":0.06898,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19876,"mean_force":0.0429,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.59388,0.17553,0.11251]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1236.0,"contact_point_centroid":[0.59848,0.15677,0.11279],"force_p95":0.07125,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19724,"mean_force":0.04376,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.59385,0.17552,0.11247]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6120.0,"contact_point_centroid":[0.58912,0.19117,0.17096],"force_p95":0.06964,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17764,"mean_force":0.04862,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.5938,0.17282,0.16772]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5259.0,"contact_point_centroid":[0.51716,0.01046,0.03052],"force_p95":0.06645,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15255,"mean_force":0.04106,"phase_index":2.0,"phase_name":"grasp","phase_type":"release","tcp_position_centroid":[0.51595,0.02948,0.02847]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6120.0,"contact_point_centroid":[0.59844,0.15415,0.16826],"force_p95":0.07045,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1518,"mean_force":0.04973,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.5938,0.17282,0.16772]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12498.0,"contact_point_centroid":[0.55171,0.12328,0.2075],"force_p95":0.07617,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14747,"mean_force":0.05228,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55459,0.10447,0.20438]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13951.0,"contact_point_centroid":[0.55607,0.08307,0.20518],"force_p95":0.07065,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14743,"mean_force":0.04824,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55309,0.10195,0.20385]},{"body_a":"world","body_b":"grasp_target","contact_count":1548.0,"contact_point_centroid":[0.57741,0.17107,-0.00198],"force_p95":0.13467,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14564,"mean_force":0.12269,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.59215,0.17534,0.1902]},{"body_a":"world","body_b":"grasp_target","contact_count":1268.0,"contact_point_centroid":[0.5305,0.03079,-0.00189],"force_p95":0.13591,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12301,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51062,0.01302,0.23171]},{"body_a":"world","body_b":"grasp_target","contact_count":1560.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.52255,0.02837,0.0994]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4229.0,"contact_point_centroid":[0.51665,0.04882,0.03126],"force_p95":0.0809,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0866,"mean_force":0.05189,"phase_index":2.0,"phase_name":"grasp","phase_type":"release","tcp_position_centroid":[0.51595,0.02948,0.02848]}],"total_contact_groups":16},"final_pose_error":0.01991,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.5774,0.17107,0.02602],"final_tcp_position":[0.59757,0.17728,0.24364],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"phases":[{"n_steps":318.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"pre_grasp_approach","tcp_end":[0.52331,0.02687,0.16217],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13639,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":390.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"grasp_position","tcp_end":[0.52475,0.03005,0.03846],"tcp_start":[0.52331,0.02687,0.16217],"tcp_to_object_dist_end":0.01372,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53042,0.02996,0.0256],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18425,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"release","tcp_end":[0.51592,0.02948,0.02844],"tcp_start":[0.52475,0.03005,0.03846],"tcp_to_object_dist_end":0.01479,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":851.0,"n_steps_budget":1000.0,"object_pos_end":[0.52397,0.02996,0.1832],"object_pos_start":[0.53042,0.02996,0.0256],"object_to_goal_dist_end":0.1837,"object_to_goal_dist_start":0.18425,"object_z_max":0.18303,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"lift_clearance","tcp_end":[0.51237,0.02925,0.19298],"tcp_start":[0.51592,0.02948,0.02844],"tcp_to_object_dist_end":0.01519,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":669.0,"n_steps_budget":1000.0,"object_pos_end":[0.59477,0.17128,0.20449],"object_pos_start":[0.52397,0.02996,0.1832],"object_to_goal_dist_end":0.09691,"object_to_goal_dist_start":0.1837,"object_z_max":0.20446,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","tcp_end":[0.59384,0.17028,0.21845],"tcp_start":[0.51237,0.02925,0.19298],"tcp_to_object_dist_end":0.01403,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":306.0,"n_steps_budget":1000.0,"object_pos_end":[0.59708,0.17758,0.10115],"object_pos_start":[0.59477,0.17128,0.20449],"object_to_goal_dist_end":0.00831,"object_to_goal_dist_start":0.09691,"object_z_max":0.20449,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"placement_accuracy","tcp_end":[0.59612,0.17616,0.11645],"tcp_start":[0.59384,0.17028,0.21845],"tcp_to_object_dist_end":0.0154,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57747,0.17106,0.02651],"object_pos_start":[0.59708,0.17758,0.10115],"object_to_goal_dist_end":0.08538,"object_to_goal_dist_start":0.00831,"object_z_max":0.10115,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","tcp_end":[0.58922,0.17412,0.13707],"tcp_start":[0.59612,0.17616,0.11645],"tcp_to_object_dist_end":0.11122,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":387.0,"n_steps_budget":600.0,"object_pos_end":[0.5774,0.17107,0.02602],"object_pos_start":[0.57747,0.17106,0.02651],"object_to_goal_dist_end":0.08587,"object_to_goal_dist_start":0.08538,"object_z_max":0.02651,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.59757,0.17728,0.24364],"tcp_start":[0.58922,0.17412,0.13707],"tcp_to_object_dist_end":0.21864,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```