## Search State

- **Seed**: 6
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9 | 0.0037 | 0.31 | ✅ accepted |
| 1 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 5 | 0.1410 | 0.18 | ❌ rejected |
| 0 | align → lift → push → approach → approach → descend → grasp → rotate | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | arc_cartesian | linear_cartesian | — | impedance_motion | position_control | position_control | impedance_control | force_threshold_switch | position_control | admittance_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6 | -0.1416 | 0.25 | ✅ accepted |

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
- Frozen object start: [0.5869067239795378, 0.18744967655878825, 0.24811674852797]
- Frozen task target: [0.5, 0.0, 0.3]
- Goal object position: (0.5, 0.0, 0.3)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5, 0.0, 0.3)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5869067239795378, 0.18744967655878825, 0.24811674852797)
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 20.0 N
- Robot initial TCP position: (0.5038164351471943, -0.015672913018666156, 0.03)
- Robot initial gripper state: **open** (gripper starts fully open; ensure a `grasp`/`force_grasp` phase closes it before lifting)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **final object-to-realised-airborne-3D-target proximity. Grasp/lift signals are optimiser fitness diagnostics only; they do not gate the canonical task_score.**

## Scene Entities

robot:
  model: panda_full
  tcp_site: attachment_site
  gripper: franka_hand
  tcp_initial_world: [0.5038164351471943, -0.015672913018666156, 0.03]
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
  frozen_object_starts: {'grasp_target': [0.5869067239795378, 0.18744967655878825, 0.24811674852797]}
  frozen_targets: {'place_target': [0.5, 0.0, 0.3]}
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
| `object` | offset from object initial position (0.5869067239795378, 0.18744967655878825, 0.24811674852797) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5, 0.0, 0.3) | final destination targets |
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

## Current Skill (Q=0.004) — your mutation base

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
  - 0.15
  weight: 0.2
- id: grasp_success
  anchor: object
  metric: contact
  weight: 0.2
- id: lift_clearance
  anchor: object
  target_entity: object
  metric: goal_progress
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.2
- id: transport_accuracy
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.2
- id: place_accuracy
  offset:
  - 0.0
  - 0.0
  - 0.03
  weight: 0.2
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
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: contact_before_approach
    when: before_phase
    predicate: contact_detected
    threshold: 1.0
    on_failure: continue
  subtask_id: reach_object
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
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    grasp_z_offset:
      type: scalar
      range:
      - -0.01
      - 0.01
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: add
  subtask_id: grasp_success
- id: grasp_1
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
  parameters:
    grasp_duration:
      type: scalar
      range:
      - 0.5
      - 2.0
      default: 1.0
      binds_to:
      - path: duration.max_time
        mode: replace
  guards:
  - id: bilateral_grasp_check
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
  subtask_id: grasp_success
- id: lift_1
  type: lift
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
    - 0.2
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.08
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: object_lifted_check
    when: after_phase
    predicate: object_lifted
    threshold: 0.05
    on_failure: abort
  subtask_id: lift_clearance
- id: transport_to_goal
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
    - 0.2
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: transport_contact
    when: during_phase
    predicate: force_below
    threshold: 18.0
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.02
  subtask_id: transport_accuracy
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
    - 0.03
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    place_z_offset:
      type: scalar
      range:
      - -0.01
      - 0.01
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: add
  subtask_id: place_accuracy
- id: release_1
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
      - 0.3
      - 1.0
      default: 0.5
      binds_to:
      - path: duration.max_time
        mode: replace
  subtask_id: place_accuracy
- id: retract_1
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
    - 0.25
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.15
      - 0.3
      default: 0.25
      binds_to:
      - path: target.offset.z
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=contact_before_approach, when=before_phase, predicate=contact_detected, on_failure=continue, threshold=1.0
- **descend_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - grasp_z_offset: status=consumed; consumers=target.offset.z (add)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - grasp_duration: status=consumed; consumers=duration.max_time (replace)
  - guards:
    - id=bilateral_grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.5
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, -0.005]
- **lift_1** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.2], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=object_lifted_check, when=after_phase, predicate=object_lifted, on_failure=abort, threshold=0.05
- **transport_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.2], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=transport_contact, when=during_phase, predicate=force_below, on_failure=retry, threshold=18.0
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, 0.02]
- **descend_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.03], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_z_offset: status=consumed; consumers=target.offset.z (add)
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - release_duration: status=consumed; consumers=duration.max_time (replace)
- **retract_1** (`retract`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.25], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_height: status=consumed; consumers=target.offset.z (replace)

## Design Metrics

- **Composite score**: 0.004
- **task_score** (E): 0.308
- **fitness_score**: 0.634  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.630

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 0.00 | 0.00 | 0.0000 |
| descend_grasp | 1.00 | 1.00 | 0.2686 |
| grasp_1 | 1.00 | 1.00 | 0.0118 |
| lift_1 | 1.00 | 1.00 | 0.1756 |
| transport_to_goal | 1.00 | 1.00 | 0.2616 |
| descend_place | 1.00 | 1.00 | 0.1410 |
| release_1 | 1.00 | 1.00 | 0.0203 |
| retract_1 | 1.00 | 1.00 | 0.1345 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 0.00 / guard_failure | (0.500, -0.000, 0.301)→(0.500, -0.000, 0.301) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.030) | 0.269→0.269 | 0.00 / 0.000 | 0.000 | 0.000 |
| descend_grasp | descend | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.495, 0.023, 0.035) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 | 1.00 / 4.000 | 0.123 | 0.138 |
| grasp_1 | grasp | 1.00 / step_budget | (0.495, 0.023, 0.035)→(0.487, 0.022, 0.026) | (0.500, 0.024, 0.026)→(0.500, 0.023, 0.025) | 0.271→0.273 | 1.00 / 41.333 | 0.175 | 0.273 |
| lift_1 | lift | 1.00 / step_budget | (0.487, 0.022, 0.026)→(0.495, 0.022, 0.202) | (0.500, 0.023, 0.025)→(0.506, 0.022, 0.196) | 0.273→0.202 | 1.00 / 40.000 | 0.077 | 0.619 |
| transport_to_goal | approach | 1.00 / step_budget | (0.495, 0.022, 0.202)→(0.590, 0.182, 0.384) | (0.506, 0.022, 0.196)→(0.599, 0.182, 0.371) | 0.202→0.164 | 1.00 / 41.333 | 0.071 | 0.095 |
| descend_place | descend | 1.00 / step_budget | (0.590, 0.182, 0.384)→(0.595, 0.194, 0.243) | (0.599, 0.182, 0.371)→(0.585, 0.193, 0.228) | 0.164→0.025 | 1.00 / 40.000 | 0.081 | 0.148 |
| release_1 | release | 1.00 / step_budget | (0.595, 0.194, 0.243)→(0.591, 0.192, 0.263) | (0.585, 0.193, 0.228)→(0.578, 0.193, 0.018) | 0.025→0.192 | 1.00 / 4.000 | 0.206 | 2.027 |
| retract_1 | retract | 1.00 / step_budget | (0.591, 0.192, 0.263)→(0.598, 0.195, 0.397) | (0.578, 0.193, 0.018)→(0.574, 0.197, 0.026) | 0.192→0.184 | 1.00 / 4.000 | 0.123 | 0.217 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.443
- phase_score: 0.458
- phase_breakdown.lift_clearance_score: 0.174
- phase_breakdown.reach_object_score: 0.078
- phase_breakdown.transport_accuracy_score: 0.497
- phase_breakdown.grasp_success_score: 1.000
- phase_breakdown.place_accuracy_score: 0.542
- grasp_place_fitness: 0.700

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.700
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.443
- **Median Q (composite search score)**: -0.021
- **K-run variance**: 0.0022
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.270


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
{"anchors":[{"name":"object","value":[0.58691,0.18745,0.24812]},{"name":"goal","value":[0.50382,-0.01567,0.03]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58691,0.18745,0.24812]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.50382,-0.01567,0.03]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.31212,"average_solve_count":330.0,"average_success_count":330.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.08478,"descend_grasp.grasp_z_offset":-0.00412,"descend_place.place_z_offset":-0.00562,"grasp_1.grasp_duration":1.27285,"lift_1.lift_height":0.21621,"lift_1.lift_speed":0.045,"release_1.release_duration":0.56298,"retract_1.retract_height":0.18181,"transport_to_goal.transport_speed":0.05132},"optimized_scores":{"best_composite_score":-0.03769,"best_fitness_score":0.59231,"best_task_score":0.22544},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":133.0,"contact_point_centroid":[0.56283,0.18843,-0.01032],"force_p95":1.4772,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.26447,"mean_force":0.59751,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58034,0.18332,0.2963]},{"body_a":"world","body_b":"grasp_target","contact_count":87.0,"contact_point_centroid":[0.49969,-0.01428,-0.00147],"force_p95":0.60362,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62669,"mean_force":0.22974,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48998,-0.01475,0.02689]},{"body_a":"world","body_b":"grasp_target","contact_count":1589.0,"contact_point_centroid":[0.5628,0.18837,-0.00217],"force_p95":0.15238,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.33321,"mean_force":0.12011,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.58232,0.18474,0.35618]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14221.0,"contact_point_centroid":[0.49325,0.00451,0.12648],"force_p95":0.07265,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29526,"mean_force":0.0505,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49348,-0.01467,0.12454]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14537.0,"contact_point_centroid":[0.49309,-0.03382,0.12412],"force_p95":0.0722,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27913,"mean_force":0.04993,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49335,-0.01467,0.12251]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50383,-0.01541,-0.00208],"force_p95":0.14714,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2211,"mean_force":0.12931,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49211,-0.01478,0.02701]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1328.0,"contact_point_centroid":[0.58334,0.16532,0.27972],"force_p95":0.07582,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14989,"mean_force":0.04192,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58266,0.18437,0.27729]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7328.0,"contact_point_centroid":[0.58225,0.19667,0.354],"force_p95":0.07749,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14961,"mean_force":0.05129,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.58167,0.17763,0.35213]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7913.0,"contact_point_centroid":[0.58209,0.15849,0.3533],"force_p95":0.07441,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14324,"mean_force":0.04897,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.58169,0.17771,0.35136]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1126.0,"contact_point_centroid":[0.58384,0.20367,0.27866],"force_p95":0.08109,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14215,"mean_force":0.04872,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58262,0.18435,0.27719]},{"body_a":"world","body_b":"grasp_target","contact_count":3272.0,"contact_point_centroid":[0.50382,-0.01567,-0.00195],"force_p95":0.12698,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12277,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.49843,-0.00738,0.16582]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4078.0,"contact_point_centroid":[0.49137,0.00444,0.02855],"force_p95":0.07854,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12988,"mean_force":0.05182,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49094,-0.01477,0.02578]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":21185.0,"contact_point_centroid":[0.53839,0.05917,0.32112],"force_p95":0.07219,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10161,"mean_force":0.0479,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53817,0.07823,0.32021]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19247.0,"contact_point_centroid":[0.53962,0.09946,0.32372],"force_p95":0.07779,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09323,"mean_force":0.05218,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53907,0.08029,0.32245]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4947.0,"contact_point_centroid":[0.49142,-0.03388,0.02765],"force_p95":0.07063,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08577,"mean_force":0.04481,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49095,-0.01477,0.02579]}],"total_contact_groups":15},"final_pose_error":0.01998,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.56236,0.18878,0.02602],"final_tcp_position":[0.58571,0.18661,0.41],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":2.26447,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":0.0,"n_steps_budget":0.0,"object_pos_end":[0.50382,-0.01567,0.03],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.30942,"object_to_goal_dist_start":0.30942,"peak_contact_force":0.0,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_object","tcp_end":[0.49977,-0.0,0.30085],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.27133,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":819.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3272.0,"raw_peak_contact_force":0.13845,"subtask_id":"grasp_success","tcp_end":[0.49909,-0.01483,0.03442],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.00967,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50369,-0.01468,0.02572],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31183,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.14157,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10825.0,"raw_peak_contact_force":0.2211,"subtask_id":"grasp_success","tcp_end":[0.49091,-0.01476,0.02575],"tcp_start":[0.49909,-0.01483,0.03442],"tcp_to_object_dist_end":0.01277,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":693.0,"n_steps_budget":1000.0,"object_pos_end":[0.51109,-0.01465,0.21684],"object_pos_start":[0.50369,-0.01468,0.02572],"object_to_goal_dist_end":0.21811,"object_to_goal_dist_start":0.31183,"object_z_max":0.21657,"peak_contact_force":0.06972,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":28845.0,"raw_peak_contact_force":0.62669,"subtask_id":"lift_clearance","tcp_end":[0.49979,-0.01463,0.22256],"tcp_start":[0.49091,-0.01476,0.02575],"tcp_to_object_dist_end":0.01267,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58837,0.17119,0.40888],"object_pos_start":[0.51109,-0.01465,0.21684],"object_to_goal_dist_end":0.16159,"object_to_goal_dist_start":0.21811,"object_z_max":0.40869,"peak_contact_force":0.07697,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":40432.0,"raw_peak_contact_force":0.10161,"subtask_id":"transport_accuracy","tcp_end":[0.57965,0.17117,0.42257],"tcp_start":[0.49979,-0.01463,0.22256],"tcp_to_object_dist_end":0.01624,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":374.0,"n_steps_budget":1000.0,"object_pos_end":[0.57233,0.18406,0.26471],"object_pos_start":[0.58837,0.17119,0.40888],"object_to_goal_dist_end":0.02234,"object_to_goal_dist_start":0.16159,"object_z_max":0.40892,"peak_contact_force":0.08191,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":15241.0,"raw_peak_contact_force":0.14961,"subtask_id":"place_accuracy","tcp_end":[0.58399,0.18477,0.28132],"tcp_start":[0.57965,0.17117,0.42257],"tcp_to_object_dist_end":0.02031,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56982,0.18231,0.01175],"object_pos_start":[0.57233,0.18406,0.26471],"object_to_goal_dist_end":0.23704,"object_to_goal_dist_start":0.02234,"object_z_max":0.26471,"peak_contact_force":0.34972,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2587.0,"raw_peak_contact_force":2.26447,"subtask_id":"place_accuracy","tcp_end":[0.58032,0.18332,0.30151],"tcp_start":[0.58399,0.18477,0.28132],"tcp_to_object_dist_end":0.28995,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":406.0,"n_steps_budget":810.0,"object_pos_end":[0.56236,0.18878,0.02602],"object_pos_start":[0.56982,0.18231,0.01175],"object_to_goal_dist_end":0.22345,"object_to_goal_dist_start":0.23704,"object_z_max":0.0272,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1589.0,"raw_peak_contact_force":0.33321,"tcp_end":[0.58571,0.18661,0.41],"tcp_start":[0.58032,0.18332,0.30151],"tcp_to_object_dist_end":0.3847,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `fe7e0be33c0bb4db9d2bbbb069b6113d0e5a69a675a0d70bc1f582243e99e3cf`; realized-scene SHA-256: `8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.62757,0.17252,0.14502]},{"name":"goal","value":[0.51251,0.03972,0.03]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.62757,0.17252,0.14502]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.51251,0.03972,0.03]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.28852,"average_solve_count":357.0,"average_success_count":357.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.05097,"descend_grasp.grasp_z_offset":-0.00149,"descend_place.place_z_offset":0.00129,"grasp_1.grasp_duration":1.21834,"lift_1.lift_height":0.18129,"lift_1.lift_speed":0.02331,"release_1.release_duration":0.63989,"retract_1.retract_height":0.19193,"transport_to_goal.transport_speed":0.02713},"optimized_scores":{"best_composite_score":0.07007,"best_fitness_score":0.70007,"best_task_score":0.44341},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":237.0,"contact_point_centroid":[0.60078,0.17216,-0.00631],"force_p95":1.00371,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.68516,"mean_force":0.30544,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61759,0.16875,0.19479]},{"body_a":"world","body_b":"grasp_target","contact_count":106.0,"contact_point_centroid":[0.50874,0.03616,-0.00174],"force_p95":0.49691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.52409,"mean_force":0.20379,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49802,0.03668,0.02878]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51264,0.03919,-0.00227],"force_p95":0.20172,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.28699,"mean_force":0.14319,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5003,0.03688,0.02897]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11898.0,"contact_point_centroid":[0.50148,0.05563,0.10595],"force_p95":0.07941,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27393,"mean_force":0.0517,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50145,0.03656,0.104]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10764.0,"contact_point_centroid":[0.50161,0.01737,0.10635],"force_p95":0.0835,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27204,"mean_force":0.05498,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50142,0.03656,0.10366]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3566.0,"contact_point_centroid":[0.50067,0.0176,0.0309],"force_p95":0.09247,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16927,"mean_force":0.05799,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49912,0.03679,0.0277]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1328.0,"contact_point_centroid":[0.62222,0.151,0.18304],"force_p95":0.07419,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15651,"mean_force":0.04159,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62139,0.17003,0.18039]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7408.0,"contact_point_centroid":[0.62131,0.1865,0.26068],"force_p95":0.07373,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14906,"mean_force":0.04986,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62095,0.16741,0.25894]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7666.0,"contact_point_centroid":[0.6213,0.14825,0.25931],"force_p95":0.07101,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14613,"mean_force":0.04837,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62101,0.16749,0.25718]},{"body_a":"world","body_b":"grasp_target","contact_count":1848.0,"contact_point_centroid":[0.60076,0.1721,-0.00197],"force_p95":0.12587,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14593,"mean_force":0.12157,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.62009,0.16977,0.26014]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1126.0,"contact_point_centroid":[0.62269,0.18935,0.18187],"force_p95":0.07999,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14242,"mean_force":0.04847,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62134,0.17001,0.18028]},{"body_a":"world","body_b":"grasp_target","contact_count":3320.0,"contact_point_centroid":[0.51251,0.03972,-0.00195],"force_p95":0.12693,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12277,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.50254,0.01864,0.16674]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18309.0,"contact_point_centroid":[0.56375,0.08314,0.25861],"force_p95":0.0685,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0915,"mean_force":0.04569,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5638,0.10231,0.25715]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4929.0,"contact_point_centroid":[0.50006,0.05606,0.02965],"force_p95":0.08221,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08836,"mean_force":0.04659,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49914,0.03679,0.02771]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17594.0,"contact_point_centroid":[0.56418,0.12192,0.25873],"force_p95":0.06867,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08608,"mean_force":0.04778,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.56417,0.10272,0.25762]}],"total_contact_groups":15},"final_pose_error":0.01983,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.60076,0.1721,0.02602],"final_tcp_position":[0.62496,0.1715,0.31732],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1.68516,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":0.0,"n_steps_budget":0.0,"object_pos_end":[0.51251,0.03972,0.03],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21001,"object_to_goal_dist_start":0.21001,"peak_contact_force":0.0,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_object","tcp_end":[0.49977,-0.0,0.30085],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.27404,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":831.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3320.0,"raw_peak_contact_force":0.13845,"subtask_id":"grasp_success","tcp_end":[0.50733,0.03739,0.03663],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.01204,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51244,0.03695,0.02512],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.2145,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.18376,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10295.0,"raw_peak_contact_force":0.28699,"subtask_id":"grasp_success","tcp_end":[0.4991,0.03678,0.02767],"tcp_start":[0.50733,0.03739,0.03663],"tcp_to_object_dist_end":0.01358,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":580.0,"n_steps_budget":1000.0,"object_pos_end":[0.51906,0.03684,0.17991],"object_pos_start":[0.51244,0.03695,0.02512],"object_to_goal_dist_end":0.1772,"object_to_goal_dist_start":0.2145,"object_z_max":0.17965,"peak_contact_force":0.08362,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":22768.0,"raw_peak_contact_force":0.52409,"subtask_id":"lift_clearance","tcp_end":[0.50798,0.03666,0.18698],"tcp_start":[0.4991,0.03678,0.02767],"tcp_to_object_dist_end":0.01315,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":839.0,"n_steps_budget":1000.0,"object_pos_end":[0.62811,0.1649,0.31509],"object_pos_start":[0.51906,0.03684,0.17991],"object_to_goal_dist_end":0.17024,"object_to_goal_dist_start":0.1772,"object_z_max":0.31495,"peak_contact_force":0.06785,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":35903.0,"raw_peak_contact_force":0.0915,"subtask_id":"transport_accuracy","tcp_end":[0.6199,0.165,0.32827],"tcp_start":[0.50798,0.03666,0.18698],"tcp_to_object_dist_end":0.01553,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":366.0,"n_steps_budget":1000.0,"object_pos_end":[0.61314,0.16993,0.16925],"object_pos_start":[0.62811,0.1649,0.31509],"object_to_goal_dist_end":0.02831,"object_to_goal_dist_start":0.17024,"object_z_max":0.31511,"peak_contact_force":0.08052,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":15074.0,"raw_peak_contact_force":0.14906,"subtask_id":"place_accuracy","tcp_end":[0.62333,0.17058,0.18482],"tcp_start":[0.6199,0.165,0.32827],"tcp_to_object_dist_end":0.01862,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60232,0.17087,0.02547],"object_pos_start":[0.61314,0.16993,0.16925],"object_to_goal_dist_end":0.12221,"object_to_goal_dist_start":0.02831,"object_z_max":0.16925,"peak_contact_force":0.08495,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2691.0,"raw_peak_contact_force":1.68516,"subtask_id":"place_accuracy","tcp_end":[0.61755,0.16874,0.20372],"tcp_start":[0.62333,0.17058,0.18482],"tcp_to_object_dist_end":0.17892,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":462.0,"n_steps_budget":840.0,"object_pos_end":[0.60076,0.1721,0.02602],"object_pos_start":[0.60232,0.17087,0.02547],"object_to_goal_dist_end":0.12199,"object_to_goal_dist_start":0.12221,"object_z_max":0.02665,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1848.0,"raw_peak_contact_force":0.14593,"tcp_end":[0.62496,0.1715,0.31732],"tcp_start":[0.61755,0.16874,0.20372],"tcp_to_object_dist_end":0.2923,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `28f75809d7d1d0a11ca1a36dd459ad950e5a80b6bae34006f33ac9620425f5e5`; realized-scene SHA-256: `f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.58187,0.22885,0.23048]},{"name":"goal","value":[0.4827,0.04873,0.03]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58187,0.22885,0.23048]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.4827,0.04873,0.03]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.36086,"average_solve_count":327.0,"average_success_count":327.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.08165,"descend_grasp.grasp_z_offset":-0.00537,"descend_place.place_z_offset":-0.00531,"grasp_1.grasp_duration":1.22691,"lift_1.lift_height":0.19004,"lift_1.lift_speed":0.04711,"release_1.release_duration":0.57224,"retract_1.retract_height":0.25367,"transport_to_goal.transport_speed":0.04973},"optimized_scores":{"best_composite_score":-0.02132,"best_fitness_score":0.60868,"best_task_score":0.25383},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":148.0,"contact_point_centroid":[0.55969,0.22867,-0.0098],"force_p95":1.41177,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.13221,"mean_force":0.52787,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57451,0.22382,0.2779]},{"body_a":"world","body_b":"grasp_target","contact_count":96.0,"contact_point_centroid":[0.47857,0.04438,-0.00172],"force_p95":0.66084,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.70491,"mean_force":0.22104,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4703,0.04507,0.02706]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48286,0.04813,-0.00234],"force_p95":0.21933,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.30976,"mean_force":0.14855,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47242,0.0453,0.02659]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11670.0,"contact_point_centroid":[0.47325,0.06412,0.11155],"force_p95":0.08048,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30169,"mean_force":0.05223,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47309,0.04496,0.10971]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11665.0,"contact_point_centroid":[0.4733,0.0258,0.11167],"force_p95":0.07802,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26637,"mean_force":0.0511,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47309,0.04496,0.10974]},{"body_a":"world","body_b":"grasp_target","contact_count":2700.0,"contact_point_centroid":[0.55969,0.22869,-0.00205],"force_p95":0.12504,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17261,"mean_force":0.11973,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.57716,0.22563,0.37269]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4497.0,"contact_point_centroid":[0.47158,0.02591,0.02808],"force_p95":0.08293,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16498,"mean_force":0.04756,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47129,0.04519,0.02546]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1328.0,"contact_point_centroid":[0.57805,0.20611,0.26241],"force_p95":0.0752,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14903,"mean_force":0.04137,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57699,0.22514,0.25961]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7330.0,"contact_point_centroid":[0.57471,0.23663,0.33532],"force_p95":0.07415,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14657,"mean_force":0.04963,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.57443,0.21758,0.3335]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7588.0,"contact_point_centroid":[0.57465,0.19834,0.33552],"force_p95":0.07169,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14465,"mean_force":0.0482,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.57445,0.21761,0.3333]},{"body_a":"world","body_b":"grasp_target","contact_count":3320.0,"contact_point_centroid":[0.4827,0.04873,-0.00195],"force_p95":0.12693,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12277,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.48849,0.02287,0.16518]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1127.0,"contact_point_centroid":[0.57856,0.24445,0.26114],"force_p95":0.08074,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13674,"mean_force":0.04829,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57695,0.22512,0.25951]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":21730.0,"contact_point_centroid":[0.52444,0.11076,0.30009],"force_p95":0.06884,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09296,"mean_force":0.04602,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52454,0.12992,0.29837]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20907.0,"contact_point_centroid":[0.52454,0.14918,0.29982],"force_p95":0.06937,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08905,"mean_force":0.04812,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52458,0.12997,0.29844]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5708.0,"contact_point_centroid":[0.47068,0.06473,0.02683],"force_p95":0.07696,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08547,"mean_force":0.04157,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47131,0.0452,0.02547]}],"total_contact_groups":15},"final_pose_error":0.01989,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.55969,0.22868,0.02602],"final_tcp_position":[0.58188,0.22834,0.46428],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":2.13221,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":0.0,"n_steps_budget":0.0,"object_pos_end":[0.4827,0.04873,0.03],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28719,"object_to_goal_dist_start":0.28719,"peak_contact_force":0.0,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_object","tcp_end":[0.49977,-0.0,0.30085],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.27573,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":831.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3320.0,"raw_peak_contact_force":0.13845,"subtask_id":"grasp_success","tcp_end":[0.47918,0.04589,0.03347],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.00871,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48261,0.04544,0.02485],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29288,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.20107,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12005.0,"raw_peak_contact_force":0.30976,"subtask_id":"grasp_success","tcp_end":[0.47127,0.04519,0.02543],"tcp_start":[0.47918,0.04589,0.03347],"tcp_to_object_dist_end":0.01136,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":583.0,"n_steps_budget":1000.0,"object_pos_end":[0.48859,0.04524,0.19091],"object_pos_start":[0.48261,0.04544,0.02485],"object_to_goal_dist_end":0.20972,"object_to_goal_dist_start":0.29288,"object_z_max":0.19064,"peak_contact_force":0.07717,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":23431.0,"raw_peak_contact_force":0.70491,"subtask_id":"lift_clearance","tcp_end":[0.47852,0.04511,0.19544],"tcp_start":[0.47127,0.04519,0.02543],"tcp_to_object_dist_end":0.01104,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.57978,0.21062,0.38828],"object_pos_start":[0.48859,0.04524,0.19091],"object_to_goal_dist_end":0.15886,"object_to_goal_dist_start":0.20972,"object_z_max":0.38807,"peak_contact_force":0.06921,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":42637.0,"raw_peak_contact_force":0.09296,"subtask_id":"transport_accuracy","tcp_end":[0.57127,0.21072,0.40005],"tcp_start":[0.47852,0.04511,0.19544],"tcp_to_object_dist_end":0.01453,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":364.0,"n_steps_budget":1000.0,"object_pos_end":[0.56837,0.22479,0.2492],"object_pos_start":[0.57978,0.21062,0.38828],"object_to_goal_dist_end":0.02343,"object_to_goal_dist_start":0.15886,"object_z_max":0.38834,"peak_contact_force":0.08159,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":14918.0,"raw_peak_contact_force":0.14657,"subtask_id":"place_accuracy","tcp_end":[0.57839,0.22567,0.26371],"tcp_start":[0.57127,0.21072,0.40005],"tcp_to_object_dist_end":0.01765,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56297,0.22452,0.01574],"object_pos_start":[0.56837,0.22479,0.2492],"object_to_goal_dist_end":0.21562,"object_to_goal_dist_start":0.02343,"object_z_max":0.2492,"peak_contact_force":0.18365,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2603.0,"raw_peak_contact_force":2.13221,"subtask_id":"place_accuracy","tcp_end":[0.57449,0.22381,0.28366],"tcp_start":[0.57839,0.22567,0.26371],"tcp_to_object_dist_end":0.26817,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":675.0,"n_steps_budget":1000.0,"object_pos_end":[0.55969,0.22868,0.02602],"object_pos_start":[0.56297,0.22452,0.01574],"object_to_goal_dist_end":0.20566,"object_to_goal_dist_start":0.21562,"object_z_max":0.02686,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2700.0,"raw_peak_contact_force":0.17261,"tcp_end":[0.58188,0.22834,0.46428],"tcp_start":[0.57449,0.22381,0.28366],"tcp_to_object_dist_end":0.43882,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```