## Search State

- **Seed**: 6
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 5 | 0.1996 | 0.31 | ✅ accepted |
| 8 | approach → descend → grasp → lift → push | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 4 | 0.3137 | 0.25 | ❌ rejected |
| 7 | approach → descend → grasp → lift → push → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 5 | 0.2166 | 0.28 | ✅ accepted |
| 6 | align → lift → push → approach → approach → descend → grasp → rotate | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | arc_cartesian | linear_cartesian | — | impedance_motion | position_control | position_control | impedance_control | force_threshold_switch | position_control | admittance_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6 | -0.1416 | 0.25 | ❌ rejected |
| 5 | align → lift → push → approach → approach → descend → grasp → rotate | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | arc_cartesian | linear_cartesian | — | impedance_motion | position_control | position_control | impedance_control | force_threshold_switch | position_control | admittance_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6 | -0.1417 | 0.25 | ❌ rejected |

**Proposal policy**: task_score is 0.31 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `584133b5261cffac0dd4282704ff39e97bf4d452e60b02507679bbdea5a4de22`
- Frozen object start: [0.5038164351471943, -0.015672913018666156, 0.03]
- Frozen task target: [0.5869067239795378, 0.18744967655878825, 0.24811674852797]
- Goal object position: (0.5869067239795378, 0.18744967655878825, 0.24811674852797)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5869067239795378, 0.18744967655878825, 0.24811674852797)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5038164351471943, -0.015672913018666156, 0.03)
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
  frozen_object_start: [0.5038, -0.0157, 0.03]
  frozen_task_target: [0.5869, 0.1874, 0.2481]
  frozen_object_starts: {'grasp_target': [0.5038164351471943, -0.015672913018666156, 0.03]}
  frozen_targets: {'place_target': [0.5869067239795378, 0.18744967655878825, 0.24811674852797]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 584133b5261cffac0dd4282704ff39e97bf4d452e60b02507679bbdea5a4de22

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
| `object` | offset from object initial position (0.5038164351471943, -0.015672913018666156, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5869067239795378, 0.18744967655878825, 0.24811674852797) | final destination targets |
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

## Current Skill (Q=0.200) — your mutation base

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
  weight: 0.2
- id: lift_object
  anchor: object
  target_entity: object
  metric: goal_progress
  weight: 0.3
- id: place_object
  target_entity: object
  metric: goal_progress
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
    - 0.1
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: reach_object
- id: descend_to_grasp
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
    - 0.02
  parameters:
    descend_offset:
      type: scalar
      range:
      - 0.0
      - 0.05
      default: 0.02
      binds_to:
      - path: target.offset.z
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
- id: grasp_object
  type: grasp
  control: position_control
  termination: time_limit
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
  guards:
  - id: grasp_check
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.5
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - -0.005
- id: lift_object
  type: lift
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.2
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.1
      - 0.3
      default: 0.2
      binds_to:
      - path: target.offset.z
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: lift_object
- id: approach_goal
  type: approach
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.15
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: place_object
- id: descend_to_place
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
    - 0.02
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: place_object
- id: release_object
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
  retries:
    max_attempts: 0
    strategy: repeat
- id: retract
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.2
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.1
      - 0.3
      default: 0.2
      binds_to:
      - path: target.offset.z
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.1]
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
  - retries: max_attempts=0, strategy=repeat
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.02]
  - parameter_bindings:
    - descend_offset: status=consumed; consumers=target.offset.z (replace)
  - retries: max_attempts=0, strategy=repeat
- **grasp_object** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.5
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, -0.005]
- **lift_object** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.2]
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
  - retries: max_attempts=0, strategy=repeat
- **approach_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15]
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat
- **descend_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.02]
  - parameter_bindings: none
  - retries: max_attempts=0, strategy=repeat
- **release_object** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - retries: max_attempts=0, strategy=repeat
- **retract** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.2]
  - parameter_bindings:
    - retract_height: status=consumed; consumers=target.offset.z (replace)
  - retries: max_attempts=0, strategy=repeat

## Design Metrics

- **Composite score**: 0.200
- **task_score** (E): 0.306
- **fitness_score**: 0.630  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.430

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1210 |
| descend_to_grasp | 1.00 | 1.00 | 0.1469 |
| grasp_object | 1.00 | 1.00 | 0.0125 |
| lift_object | 0.33 | 1.00 | 0.1608 |
| approach_goal | 0.00 | 1.00 | 0.0950 |
| descend_to_place | 1.00 | 1.00 | 0.1266 |
| release_object | 1.00 | 1.00 | 0.0217 |
| retract | 0.33 | 1.00 | 0.1591 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, 0.021, 0.186) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 | 1.00 / 4.000 | 0.123 | 0.123 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.496, 0.021, 0.186)→(0.495, 0.024, 0.039) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 | 1.00 / 42.667 | 0.152 | 0.207 |
| grasp_object | grasp | 1.00 / step_budget | (0.495, 0.024, 0.039)→(0.486, 0.023, 0.030) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.272 | 1.00 / 35.667 | 55983.965 | 0.680 |
| lift_object | lift | 0.33 / step_budget | (0.486, 0.023, 0.030)→(0.482, 0.023, 0.191) | (0.500, 0.024, 0.026)→(0.493, 0.023, 0.177) | 0.272→0.211 | 1.00 / 28.000 | 0.110 | 0.144 |
| approach_goal | approach | 0.00 / step_budget | (0.482, 0.023, 0.191)→(0.523, 0.087, 0.246) | (0.493, 0.023, 0.177)→(0.531, 0.088, 0.226) | 0.211→0.134 | 1.00 / 33.667 | 0.097 | 0.220 |
| descend_to_place | descend | 1.00 / step_budget | (0.523, 0.087, 0.246)→(0.590, 0.186, 0.220) | (0.531, 0.088, 0.226)→(0.588, 0.186, 0.192) | 0.134→0.023 | 1.00 / 3.333 | 0.201 | 1.737 |
| release_object | release | 1.00 / step_budget | (0.590, 0.186, 0.220)→(0.585, 0.184, 0.241) | (0.588, 0.186, 0.192)→(0.579, 0.183, 0.020) | 0.023→0.190 | 1.00 / 4.000 | 27.129 | 0.263 |
| retract | retract | 0.33 / step_budget | (0.585, 0.184, 0.241)→(0.584, 0.184, 0.400) | (0.579, 0.183, 0.020)→(0.568, 0.182, 0.026) | 0.190→0.185 | 1.00 / 4.000 | 0.123 | 0.138 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.447
- phase_score: 0.526
- phase_breakdown.lift_object_score: 0.143
- phase_breakdown.reach_object_score: 0.293
- phase_breakdown.place_object_score: 0.848
- grasp_place_fitness: 0.701

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.701
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.447
- **Median Q (composite search score)**: 0.173
- **K-run variance**: 0.0026
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.482


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `daf90631fcbaf423e19452d0c9b90b9715013985cc94ef12ca0cd881e96195aa`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `94660347aa4f41f6801e53bd449f8df59691da8bebfa4fef4947a3513fe04781`; realized-scene SHA-256: `584133b5261cffac0dd4282704ff39e97bf4d452e60b02507679bbdea5a4de22`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50382,-0.01567,0.03]},{"name":"goal","value":[0.58691,0.18745,0.24812]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.50382,-0.01567,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58691,0.18745,0.24812]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.82383,"average_solve_count":193.0,"average_success_count":193.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.transport_speed":0.06743,"approach_object.approach_height":0.10721,"descend_to_grasp.descend_offset":0.0092,"lift_object.lift_height":0.23015,"retract.retract_height":0.231},"optimized_scores":{"best_composite_score":0.15427,"best_fitness_score":0.58427,"best_task_score":0.21972},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":156.0,"contact_point_centroid":[0.55222,0.15665,-0.0089],"force_p95":1.56105,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.02174,"mean_force":0.50143,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.56844,0.16321,0.27437]},{"body_a":"world","body_b":"grasp_target","contact_count":135.0,"contact_point_centroid":[0.50049,-0.0152,-0.0011],"force_p95":0.35775,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.59531,"mean_force":0.08831,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48849,-0.01539,0.03629]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20385.0,"contact_point_centroid":[0.48755,0.00364,0.11353],"force_p95":0.07482,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32575,"mean_force":0.05059,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48596,-0.01535,0.11185]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17570.0,"contact_point_centroid":[0.48681,-0.03453,0.11532],"force_p95":0.08015,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32525,"mean_force":0.05714,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48595,-0.01535,0.11274]},{"body_a":"world","body_b":"grasp_target","contact_count":3864.0,"contact_point_centroid":[0.55111,0.15581,-0.00208],"force_p95":0.15252,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24662,"mean_force":0.12494,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.56675,0.16268,0.36075]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1108.0,"contact_point_centroid":[0.56547,0.18245,0.25553],"force_p95":0.07545,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20144,"mean_force":0.04717,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.57126,0.16419,0.2556]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17300.0,"contact_point_centroid":[0.544,0.13234,0.2564],"force_p95":0.08184,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1854,"mean_force":0.05754,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.54615,0.11347,0.25498]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19169.0,"contact_point_centroid":[0.55022,0.09448,0.25492],"force_p95":0.07579,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18333,"mean_force":0.05236,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.54592,0.11303,0.25494]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1150.0,"contact_point_centroid":[0.57485,0.14541,0.25389],"force_p95":0.07359,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17938,"mean_force":0.04585,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.57125,0.16419,0.25558]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50381,-0.01576,-0.00203],"force_p95":0.13258,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16022,"mean_force":0.12522,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49124,-0.01541,0.03585]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16128.0,"contact_point_centroid":[0.50301,5e-05,0.22563],"force_p95":0.08758,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14346,"mean_force":0.05987,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.50036,0.01895,0.22418]},{"body_a":"world","body_b":"grasp_target","contact_count":1876.0,"contact_point_centroid":[0.50382,-0.01567,-0.00193],"force_p95":0.13354,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12289,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49877,-0.00694,0.22327]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16966.0,"contact_point_centroid":[0.50176,0.03788,0.2251],"force_p95":0.08087,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12787,"mean_force":0.05668,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.50032,0.01893,0.22412]},{"body_a":"world","body_b":"grasp_target","contact_count":1280.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.49778,-0.01484,0.09446]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5329.0,"contact_point_centroid":[0.49079,0.00366,0.0365],"force_p95":0.06675,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0952,"mean_force":0.04108,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49002,-0.0154,0.03455]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4146.0,"contact_point_centroid":[0.48948,-0.03467,0.03716],"force_p95":0.07904,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09351,"mean_force":0.05186,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49002,-0.0154,0.03455]}],"total_contact_groups":16},"final_pose_error":0.07157,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.55046,0.15562,0.02602],"final_tcp_position":[0.56752,0.16287,0.43989],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":2.02174,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":470.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1280.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.49965,-0.01425,0.14607],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12013,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":320.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13264,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11275.0,"raw_peak_contact_force":0.16022,"tcp_end":[0.49854,-0.01546,0.04369],"tcp_start":[0.49965,-0.01425,0.14607],"tcp_to_object_dist_end":0.01844,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50369,-0.01578,0.02588],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31244,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.08321,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":38090.0,"raw_peak_contact_force":0.59531,"tcp_end":[0.48999,-0.0154,0.03451],"tcp_start":[0.49854,-0.01546,0.04369],"tcp_to_object_dist_end":0.0162,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49555,-0.0157,0.17776],"object_pos_start":[0.50369,-0.01578,0.02588],"object_to_goal_dist_end":0.2336,"object_to_goal_dist_start":0.31244,"object_z_max":0.17757,"peak_contact_force":0.09067,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":33094.0,"raw_peak_contact_force":0.14346,"subtask_id":"lift_object","tcp_end":[0.4864,-0.01535,0.19513],"tcp_start":[0.48999,-0.0154,0.03451],"tcp_to_object_dist_end":0.01964,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":36.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52225,0.05181,0.23288],"object_pos_start":[0.49555,-0.0157,0.17776],"object_to_goal_dist_end":0.15103,"object_to_goal_dist_start":0.2336,"object_z_max":0.23282,"peak_contact_force":0.07584,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":36469.0,"raw_peak_contact_force":0.1854,"subtask_id":"place_object","tcp_end":[0.51643,0.05109,0.25581],"tcp_start":[0.4864,-0.01535,0.19513],"tcp_to_object_dist_end":0.02366,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56965,0.16467,0.22965],"object_pos_start":[0.52225,0.05181,0.23288],"object_to_goal_dist_end":0.03403,"object_to_goal_dist_start":0.15103,"object_z_max":0.23288,"peak_contact_force":0.08586,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2414.0,"raw_peak_contact_force":2.02174,"subtask_id":"place_object","tcp_end":[0.57252,0.16438,0.25864],"tcp_start":[0.51643,0.05109,0.25581],"tcp_to_object_dist_end":0.02914,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56373,0.1615,0.01606],"object_pos_start":[0.56965,0.16467,0.22965],"object_to_goal_dist_end":0.23465,"object_to_goal_dist_start":0.03403,"object_z_max":0.22965,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":3864.0,"raw_peak_contact_force":0.24662,"tcp_end":[0.5684,0.16321,0.28045],"tcp_start":[0.57252,0.16438,0.25864],"tcp_to_object_dist_end":0.26444,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55046,0.15562,0.02602],"object_pos_start":[0.56373,0.1615,0.01606],"object_to_goal_dist_end":0.22731,"object_to_goal_dist_start":0.23465,"object_z_max":0.02981,"peak_contact_force":0.12262,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1876.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.56752,0.16287,0.43989],"tcp_start":[0.5684,0.16321,0.28045],"tcp_to_object_dist_end":0.41428,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `fe7e0be33c0bb4db9d2bbbb069b6113d0e5a69a675a0d70bc1f582243e99e3cf`; realized-scene SHA-256: `8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51251,0.03972,0.03]},{"name":"goal","value":[0.62757,0.17252,0.14502]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.51251,0.03972,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.62757,0.17252,0.14502]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.83069,"average_solve_count":189.0,"average_success_count":189.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.transport_speed":0.06854,"approach_object.approach_height":0.15386,"descend_to_grasp.descend_offset":0.00105,"lift_object.lift_height":0.24013,"retract.retract_height":0.17231},"optimized_scores":{"best_composite_score":0.27133,"best_fitness_score":0.70133,"best_task_score":0.44715},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":266.0,"contact_point_centroid":[0.60831,0.16676,-0.005],"force_p95":1.00309,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.20266,"mean_force":0.26014,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.61519,0.16751,0.16846]},{"body_a":"world","body_b":"grasp_target","contact_count":144.0,"contact_point_centroid":[0.50896,0.03719,-0.00124],"force_p95":0.49626,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.76707,"mean_force":0.10833,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49689,0.03809,0.0279]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16587.0,"contact_point_centroid":[0.4953,0.05712,0.10451],"force_p95":0.1126,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34944,"mean_force":0.06341,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49436,0.03789,0.10254]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20457.0,"contact_point_centroid":[0.49662,0.0193,0.10513],"force_p95":0.08625,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32623,"mean_force":0.05012,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49438,0.03789,0.10366]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11511.0,"contact_point_centroid":[0.59397,0.1195,0.1825],"force_p95":0.1194,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.288,"mean_force":0.07019,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.58784,0.13626,0.18392]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":514.0,"contact_point_centroid":[0.62072,0.18869,0.15349],"force_p95":0.14684,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27652,"mean_force":0.09462,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.61912,0.16869,0.15417]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6907.0,"contact_point_centroid":[0.58519,0.15168,0.18626],"force_p95":0.16457,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27007,"mean_force":0.10974,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.58403,0.13249,0.18689]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":896.0,"contact_point_centroid":[0.62541,0.15174,0.15201],"force_p95":0.12443,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24485,"mean_force":0.0599,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.61932,0.16875,0.15454]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51258,0.03962,-0.00214],"force_p95":0.16211,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22725,"mean_force":0.1329,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49978,0.03833,0.02735]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5054.0,"contact_point_centroid":[0.50015,0.01923,0.02754],"force_p95":0.07011,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18153,"mean_force":0.04269,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49852,0.03823,0.02601]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12029.0,"contact_point_centroid":[0.52224,0.08638,0.20517],"force_p95":0.12111,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16753,"mean_force":0.08321,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52066,0.06707,0.20455]},{"body_a":"world","body_b":"grasp_target","contact_count":3972.0,"contact_point_centroid":[0.6081,0.16666,-0.00198],"force_p95":0.1244,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14768,"mean_force":0.12243,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.61244,0.16671,0.25481]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16994.0,"contact_point_centroid":[0.52424,0.04851,0.20436],"force_p95":0.095,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14123,"mean_force":0.05631,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52012,0.06652,0.20413]},{"body_a":"world","body_b":"grasp_target","contact_count":1456.0,"contact_point_centroid":[0.51251,0.03972,-0.00191],"force_p95":0.13511,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12296,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50275,0.017,0.24547]},{"body_a":"world","body_b":"grasp_target","contact_count":1916.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50612,0.03689,0.11249]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4233.0,"contact_point_centroid":[0.49886,0.05755,0.02877],"force_p95":0.08282,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09506,"mean_force":0.05194,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49853,0.03823,0.02602]}],"total_contact_groups":16},"final_pose_error":0.01488,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.6081,0.16666,0.02602],"final_tcp_position":[0.6132,0.16689,0.33598],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":167951.73011,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":365.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1916.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.50766,0.03506,0.19107],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16519,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":479.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.15928,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11087.0,"raw_peak_contact_force":0.22725,"tcp_end":[0.50723,0.03893,0.03545],"tcp_start":[0.50766,0.03506,0.19107],"tcp_to_object_dist_end":0.01084,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":33.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51246,0.03871,0.02553],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21315,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":167951.73011,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":37188.0,"raw_peak_contact_force":0.76707,"tcp_end":[0.4985,0.03823,0.02598],"tcp_start":[0.50723,0.03893,0.03545],"tcp_to_object_dist_end":0.01398,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50714,0.03848,0.1749],"object_pos_start":[0.51246,0.03871,0.02553],"object_to_goal_dist_end":0.18266,"object_to_goal_dist_start":0.21315,"object_z_max":0.17471,"peak_contact_force":0.15044,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":29023.0,"raw_peak_contact_force":0.16753,"subtask_id":"lift_object","tcp_end":[0.49482,0.03793,0.18657],"tcp_start":[0.4985,0.03823,0.02598],"tcp_to_object_dist_end":0.01698,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":21.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55412,0.09333,0.20429],"object_pos_start":[0.50714,0.03848,0.1749],"object_to_goal_dist_end":0.1232,"object_to_goal_dist_start":0.18266,"object_z_max":0.20428,"peak_contact_force":0.14584,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":18418.0,"raw_peak_contact_force":0.288,"subtask_id":"place_object","tcp_end":[0.54562,0.09233,0.22414],"tcp_start":[0.49482,0.03793,0.18657],"tcp_to_object_dist_end":0.02162,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":846.0,"n_steps_budget":1000.0,"object_pos_end":[0.62295,0.1688,0.12729],"object_pos_start":[0.55412,0.09333,0.20429],"object_to_goal_dist_end":0.0187,"object_to_goal_dist_start":0.1232,"object_z_max":0.20429,"peak_contact_force":0.11283,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1676.0,"raw_peak_contact_force":1.20266,"subtask_id":"place_object","tcp_end":[0.62111,0.16916,0.15817],"tcp_start":[0.54562,0.09233,0.22414],"tcp_to_object_dist_end":0.03093,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60984,0.16671,0.02627],"object_pos_start":[0.62295,0.1688,0.12729],"object_to_goal_dist_end":0.12021,"object_to_goal_dist_start":0.0187,"object_z_max":0.12729,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":3972.0,"raw_peak_contact_force":0.14768,"tcp_end":[0.61512,0.1675,0.17841],"tcp_start":[0.62111,0.16916,0.15817],"tcp_to_object_dist_end":0.15223,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":993.0,"n_steps_budget":1000.0,"object_pos_end":[0.6081,0.16666,0.02602],"object_pos_start":[0.60984,0.16671,0.02627],"object_to_goal_dist_end":0.12073,"object_to_goal_dist_start":0.12021,"object_z_max":0.0266,"peak_contact_force":0.12262,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1456.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.6132,0.16689,0.33598],"tcp_start":[0.61512,0.1675,0.17841],"tcp_to_object_dist_end":0.31,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `28f75809d7d1d0a11ca1a36dd459ad950e5a80b6bae34006f33ac9620425f5e5`; realized-scene SHA-256: `f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.4827,0.04873,0.03]},{"name":"goal","value":[0.58187,0.22885,0.23048]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.4827,0.04873,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58187,0.22885,0.23048]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.90526,"average_solve_count":190.0,"average_success_count":190.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.transport_speed":0.0954,"approach_object.approach_height":0.18374,"descend_to_grasp.descend_offset":0.00358,"lift_object.lift_height":0.1862,"retract.retract_height":0.2721},"optimized_scores":{"best_composite_score":0.1732,"best_fitness_score":0.6032,"best_task_score":0.25041},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":149.0,"contact_point_centroid":[0.55033,0.22212,-0.00892],"force_p95":1.42164,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.98659,"mean_force":0.51425,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.57188,0.22179,0.25762]},{"body_a":"world","body_b":"grasp_target","contact_count":141.0,"contact_point_centroid":[0.4794,0.0457,-0.00124],"force_p95":0.4131,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.67734,"mean_force":0.09703,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.468,0.04678,0.03158]},{"body_a":"world","body_b":"grasp_target","contact_count":3780.0,"contact_point_centroid":[0.54652,0.2246,-0.00212],"force_p95":0.19045,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.3937,"mean_force":0.12808,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.57013,0.22104,0.34621]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17000.0,"contact_point_centroid":[0.46569,0.06577,0.1118],"force_p95":0.08438,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33613,"mean_force":0.05884,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46556,0.04656,0.10915]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20719.0,"contact_point_centroid":[0.46791,0.02768,0.10926],"force_p95":0.07984,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3128,"mean_force":0.04976,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46555,0.04656,0.10779]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1304.0,"contact_point_centroid":[0.5673,0.2407,0.24279],"force_p95":0.07495,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2851,"mean_force":0.04789,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.57474,0.22309,0.23958]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1402.0,"contact_point_centroid":[0.57919,0.20423,0.23994],"force_p95":0.07218,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27328,"mean_force":0.04338,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.57478,0.2231,0.23966]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48279,0.04862,-0.00216],"force_p95":0.16758,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23474,"mean_force":0.1346,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.47077,0.04707,0.0308]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5132.0,"contact_point_centroid":[0.47125,0.02795,0.03085],"force_p95":0.07039,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19927,"mean_force":0.0421,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46956,0.04695,0.02958]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":21636.0,"contact_point_centroid":[0.55091,0.15879,0.24802],"force_p95":0.07196,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18635,"mean_force":0.04696,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.54556,0.17712,0.24747]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18492.0,"contact_point_centroid":[0.54187,0.1966,0.25069],"force_p95":0.08722,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1677,"mean_force":0.05332,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.54619,0.17808,0.24738]},{"body_a":"world","body_b":"grasp_target","contact_count":1140.0,"contact_point_centroid":[0.4827,0.04873,-0.00188],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12306,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49045,0.0199,0.26046]},{"body_a":"world","body_b":"grasp_target","contact_count":2284.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47873,0.04457,0.12851]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16131.0,"contact_point_centroid":[0.48542,0.10222,0.22616],"force_p95":0.08867,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1221,"mean_force":0.0602,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.48643,0.08311,0.22385]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19087.0,"contact_point_centroid":[0.49069,0.06472,0.22478],"force_p95":0.07774,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11061,"mean_force":0.05165,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.48648,0.08319,0.22392]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4244.0,"contact_point_centroid":[0.46943,0.06629,0.03202],"force_p95":0.08677,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09819,"mean_force":0.05203,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46957,0.04695,0.02959]}],"total_contact_groups":16},"final_pose_error":0.11193,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.54564,0.22431,0.02602],"final_tcp_position":[0.57089,0.22129,0.42429],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":81.14225,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":286.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2284.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.48196,0.0416,0.22059],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1947,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":571.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.16413,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11176.0,"raw_peak_contact_force":0.23474,"tcp_end":[0.47795,0.04776,0.03813],"tcp_start":[0.48196,0.0416,0.22059],"tcp_to_object_dist_end":0.01305,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48271,0.04758,0.02545],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29109,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.08213,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":37860.0,"raw_peak_contact_force":0.67734,"tcp_end":[0.46953,0.04695,0.02955],"tcp_start":[0.47795,0.04776,0.03813],"tcp_to_object_dist_end":0.01382,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47604,0.04758,0.17723],"object_pos_start":[0.48271,0.04758,0.02545],"object_to_goal_dist_end":0.21656,"object_to_goal_dist_start":0.29109,"object_z_max":0.17705,"peak_contact_force":0.08818,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":35218.0,"raw_peak_contact_force":0.1221,"subtask_id":"lift_object","tcp_end":[0.46597,0.04659,0.19062],"tcp_start":[0.46953,0.04695,0.02955],"tcp_to_object_dist_end":0.01678,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51514,0.11912,0.23973],"object_pos_start":[0.47604,0.04758,0.17723],"object_to_goal_dist_end":0.12876,"object_to_goal_dist_start":0.21656,"object_z_max":0.23967,"peak_contact_force":0.06987,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":40128.0,"raw_peak_contact_force":0.18635,"subtask_id":"place_object","tcp_end":[0.50833,0.11719,0.2587],"tcp_start":[0.46597,0.04659,0.19062],"tcp_to_object_dist_end":0.02025,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5724,0.22406,0.21771],"object_pos_start":[0.51514,0.11912,0.23973],"object_to_goal_dist_end":0.01661,"object_to_goal_dist_start":0.12876,"object_z_max":0.23973,"peak_contact_force":0.40558,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2855.0,"raw_peak_contact_force":1.98659,"subtask_id":"place_object","tcp_end":[0.5761,0.22347,0.24294],"tcp_start":[0.50833,0.11719,0.2587],"tcp_to_object_dist_end":0.02551,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56367,0.22098,0.01621],"object_pos_start":[0.5724,0.22406,0.21771],"object_to_goal_dist_end":0.21519,"object_to_goal_dist_start":0.01661,"object_z_max":0.21771,"peak_contact_force":81.14225,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":3780.0,"raw_peak_contact_force":0.3937,"tcp_end":[0.57184,0.22179,0.26411],"tcp_start":[0.5761,0.22347,0.24294],"tcp_to_object_dist_end":0.24804,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54564,0.22431,0.02602],"object_pos_start":[0.56367,0.22098,0.01621],"object_to_goal_dist_end":0.2077,"object_to_goal_dist_start":0.21519,"object_z_max":0.02949,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1140.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.57089,0.22129,0.42429],"tcp_start":[0.57184,0.22179,0.26411],"tcp_to_object_dist_end":0.39908,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```