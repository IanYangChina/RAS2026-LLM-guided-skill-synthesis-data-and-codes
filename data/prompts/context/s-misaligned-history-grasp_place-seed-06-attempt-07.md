## Search State

- **Seed**: 6
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → descend → grasp → lift → push → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 11  | -0.1416 | 0.25 | ❌ rejected |
| 6 | align → lift → push → approach → approach → descend → grasp → rotate | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | arc_cartesian | linear_cartesian | — | impedance_motion | position_control | position_control | impedance_control | force_threshold_switch | position_control | admittance_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6  | -0.1417 | 0.25 | ❌ rejected |
| 5 | align → lift → push → approach → approach → descend → grasp → rotate | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | arc_cartesian | linear_cartesian | — | impedance_motion | position_control | position_control | impedance_control | force_threshold_switch | position_control | admittance_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6  | -0.2456 | 0.17 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | admittance_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 7  | -0.1415 | 0.25 | ✅ accepted |
| 3 | align → lift → push → approach → approach → descend → grasp → rotate | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | arc_cartesian | linear_cartesian | — | impedance_motion | position_control | position_control | impedance_control | force_threshold_switch | position_control | admittance_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6  | -0.1048 | 0.29 | ✅ accepted |

**Proposal policy**: task_score is 0.29 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.105) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_pre_grasp
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.3
- id: reach_goal
  offset:
  - 0.0
  - 0.0
  - 0.05
  weight: 0.7
phases:
- id: approach_1
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    generator.arc_height:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.arc_height
        mode: replace
    generator.speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_pre_grasp
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    generator.speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_pre_grasp
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
    orientation:
      mode: keep_current
  parameters:
    duration.max_time:
      type: scalar
      range:
      - 0.5
      - 2.0
      default: 1.0
      binds_to:
      - path: duration.max_time
        mode: replace
  guards:
  - id: grasp_check
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.5
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: repeat
- id: lift_1
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.25
      axis: world_z
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    generator.speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    target.offset_along_axis.distance:
      type: scalar
      range:
      - 0.15
      - 0.3
      default: 0.25
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
  guards:
  - id: lift_check
    when: after_phase
    predicate: object_lifted
    threshold: 0.1
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: repeat
  subtask_id: reach_pre_grasp
- id: transport_1
  type: push
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.05
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    generator.arc_height:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.arc_height
        mode: replace
    generator.speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_goal
- id: descend_2
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
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    generator.speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_goal
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
    orientation:
      mode: keep_current
  parameters:
    duration.max_time:
      type: scalar
      range:
      - 0.3
      - 1.0
      default: 0.5
      binds_to:
      - path: duration.max_time
        mode: replace
- id: retract_1
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
    - 0.1
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    generator.speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.15], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - generator.arc_height: status=consumed; consumers=generator.arc_height (replace)
    - generator.speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - generator.speed: status=consumed; consumers=generator.speed (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - duration.max_time: status=consumed; consumers=duration.max_time (replace)
  - guards:
    - id=grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.5
  - retries: max_attempts=2, strategy=repeat
- **lift_1** (`lift`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.25, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - generator.speed: status=consumed; consumers=generator.speed (replace)
    - target.offset_along_axis.distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
  - guards:
    - id=lift_check, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.1
  - retries: max_attempts=1, strategy=repeat
- **transport_1** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.05], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - generator.arc_height: status=consumed; consumers=generator.arc_height (replace)
    - generator.speed: status=consumed; consumers=generator.speed (replace)
- **descend_2** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - generator.speed: status=consumed; consumers=generator.speed (replace)
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - duration.max_time: status=consumed; consumers=duration.max_time (replace)
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - generator.speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: -0.105
- **task_score** (E): 0.292
- **fitness_score**: 0.625  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.730

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1275 |
| descend_1 | 1.00 | 1.00 | 0.1473 |
| grasp_1 | 1.00 | 1.00 | 0.0118 |
| lift_1 | 1.00 | 1.00 | 0.2002 |
| transport_1 | 1.00 | 1.00 | 0.2064 |
| descend_2 | 1.00 | 1.00 | 0.0494 |
| release_1 | 1.00 | 1.00 | 0.0206 |
| retract_1 | 1.00 | 1.00 | 0.0802 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, 0.033, 0.182) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.496, 0.033, 0.182)→(0.495, 0.025, 0.034) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.495, 0.025, 0.034)→(0.487, 0.024, 0.026) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.272 | 1.00 / 43.000 | 0.135 | 0.179 |
| lift_1 | lift | 1.00 / step_budget | (0.487, 0.024, 0.026)→(0.496, 0.024, 0.226) | (0.500, 0.024, 0.026)→(0.507, 0.024, 0.219) | 0.272→0.216 | 1.00 / 39.000 | 0.077 | 0.650 |
| transport_1 | push | 1.00 / step_budget | (0.496, 0.024, 0.226)→(0.591, 0.185, 0.263) | (0.507, 0.024, 0.219)→(0.599, 0.185, 0.246) | 0.216→0.041 | 1.00 / 29.333 | 0.114 | 0.207 |
| descend_2 | descend | 1.00 / step_budget | (0.591, 0.185, 0.263)→(0.594, 0.192, 0.215) | (0.599, 0.185, 0.246)→(0.601, 0.192, 0.196) | 0.041→0.013 | 1.00 / 27.333 | 656.194 | 0.255 |
| release_1 | release | 1.00 / step_budget | (0.594, 0.192, 0.215)→(0.589, 0.190, 0.235) | (0.601, 0.192, 0.196)→(0.600, 0.193, 0.012) | 0.013→0.196 | 1.00 / 4.000 | 0.097 | 1.818 |
| retract_1 | retract | 1.00 / step_budget | (0.589, 0.190, 0.235)→(0.587, 0.189, 0.315) | (0.600, 0.193, 0.012)→(0.600, 0.194, 0.016) | 0.196→0.192 | 1.00 / 4.000 | 0.123 | 0.126 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.423
- phase_score: 0.341
- phase_breakdown.reach_pre_grasp_score: 0.129
- phase_breakdown.reach_goal_score: 0.432
- grasp_place_fitness: 0.690

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.690
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.423
- **Median Q (composite search score)**: -0.130
- **K-run variance**: 0.0022
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.382


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.96437,"average_solve_count":421.0,"average_success_count":421.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.generator.arc_height":0.08916,"approach_1.generator.speed":0.03751,"descend_1.generator.speed":0.03211,"descend_2.generator.speed":0.02783,"grasp_1.duration.max_time":0.82417,"lift_1.generator.speed":0.04927,"lift_1.target.offset_along_axis.distance":0.17098,"release_1.duration.max_time":0.93874,"retract_1.generator.speed":0.06885,"transport_1.generator.arc_height":0.03943,"transport_1.generator.speed":0.02264},"optimized_scores":{"best_composite_score":-0.14449,"best_fitness_score":0.58551,"best_task_score":0.21272},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":139.0,"contact_point_centroid":[0.58786,0.18294,-0.0097],"force_p95":1.54453,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.15017,"mean_force":0.57625,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57746,0.18005,0.26911]},{"body_a":"world","body_b":"grasp_target","contact_count":87.0,"contact_point_centroid":[0.50099,-0.01429,-0.00144],"force_p95":0.58844,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64616,"mean_force":0.16061,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4896,-0.01472,0.02689]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9773.0,"contact_point_centroid":[0.49364,0.00449,0.10317],"force_p95":0.08105,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30435,"mean_force":0.05648,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49303,-0.01464,0.10067]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10434.0,"contact_point_centroid":[0.49343,-0.0337,0.10049],"force_p95":0.07787,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28965,"mean_force":0.05371,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49285,-0.01464,0.09837]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50384,-0.01541,-0.00208],"force_p95":0.14839,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22213,"mean_force":0.12958,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49183,-0.01475,0.02701]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":981.0,"contact_point_centroid":[0.58335,0.16228,0.25138],"force_p95":0.0873,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1984,"mean_force":0.05373,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58015,0.18119,0.25019]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":988.0,"contact_point_centroid":[0.58313,0.20023,0.25074],"force_p95":0.09261,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18973,"mean_force":0.05498,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58015,0.18119,0.2502]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2063.0,"contact_point_centroid":[0.5824,0.15725,0.27386],"force_p95":0.08399,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17213,"mean_force":0.0597,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.57922,0.17597,0.2731]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1710.0,"contact_point_centroid":[0.58206,0.19504,0.27387],"force_p95":0.09546,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16506,"mean_force":0.0722,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.57925,0.17601,0.273]},{"body_a":"world","body_b":"grasp_target","contact_count":2164.0,"contact_point_centroid":[0.50382,-0.01567,-0.00193],"force_p95":0.13205,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12285,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49902,0.01836,0.23583]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4077.0,"contact_point_centroid":[0.49121,0.00447,0.02853],"force_p95":0.07879,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13091,"mean_force":0.05183,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49065,-0.01473,0.02578]},{"body_a":"world","body_b":"grasp_target","contact_count":1272.0,"contact_point_centroid":[0.58952,0.18243,-0.00214],"force_p95":0.1246,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12671,"mean_force":0.11627,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5758,0.17939,0.31395]},{"body_a":"world","body_b":"grasp_target","contact_count":2000.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49796,-0.01071,0.10602]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14704.0,"contact_point_centroid":[0.53122,0.04212,0.24903],"force_p95":0.08145,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10052,"mean_force":0.05504,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.52962,0.06102,0.24777]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12971.0,"contact_point_centroid":[0.53197,0.08175,0.25077],"force_p95":0.08904,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09489,"mean_force":0.06126,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.53036,0.06269,0.24888]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4951.0,"contact_point_centroid":[0.49123,-0.03385,0.02763],"force_p95":0.07082,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08604,"mean_force":0.04478,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49066,-0.01473,0.02578]}],"total_contact_groups":16},"final_pose_error":0.01983,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.58951,0.18242,0.01602],"final_tcp_position":[0.57597,0.17937,0.35484],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":2.15017,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":542.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2164.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.49997,-0.00673,0.17831],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1526,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":500.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2000.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_pre_grasp","tcp_end":[0.49882,-0.01481,0.03442],"tcp_start":[0.49997,-0.00673,0.17831],"tcp_to_object_dist_end":0.00981,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50368,-0.01465,0.02571],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31183,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.14258,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10828.0,"raw_peak_contact_force":0.22213,"tcp_end":[0.49062,-0.01473,0.02575],"tcp_start":[0.49882,-0.01481,0.03442],"tcp_to_object_dist_end":0.01306,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":536.0,"n_steps_budget":1000.0,"object_pos_end":[0.51166,-0.0146,0.172],"object_pos_start":[0.50368,-0.01465,0.02571],"object_to_goal_dist_end":0.22865,"object_to_goal_dist_start":0.31183,"object_z_max":0.17173,"peak_contact_force":0.08016,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":20294.0,"raw_peak_contact_force":0.64616,"subtask_id":"reach_pre_grasp","tcp_end":[0.49914,-0.0146,0.17735],"tcp_start":[0.49062,-0.01473,0.02575],"tcp_to_object_dist_end":0.01361,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":807.0,"n_steps_budget":1000.0,"object_pos_end":[0.58886,0.17132,0.27732],"object_pos_start":[0.51166,-0.0146,0.172],"object_to_goal_dist_end":0.03342,"object_to_goal_dist_start":0.22865,"object_z_max":0.27785,"peak_contact_force":0.08335,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":27675.0,"raw_peak_contact_force":0.10052,"subtask_id":"reach_goal","tcp_end":[0.57814,0.17125,0.29103],"tcp_start":[0.49914,-0.0146,0.17735],"tcp_to_object_dist_end":0.0174,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":31.0,"n_steps":126.0,"n_steps_budget":1000.0,"object_pos_end":[0.59269,0.18153,0.23927],"object_pos_start":[0.58886,0.17132,0.27732],"object_to_goal_dist_end":0.01211,"object_to_goal_dist_start":0.03342,"object_z_max":0.27732,"peak_contact_force":0.0,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3773.0,"raw_peak_contact_force":0.17213,"subtask_id":"reach_goal","tcp_end":[0.58164,0.18151,0.25417],"tcp_start":[0.57814,0.17125,0.29103],"tcp_to_object_dist_end":0.01854,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58884,0.18066,0.00532],"object_pos_start":[0.59269,0.18153,0.23927],"object_to_goal_dist_end":0.2429,"object_to_goal_dist_start":0.01211,"object_z_max":0.23927,"peak_contact_force":0.12005,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2108.0,"raw_peak_contact_force":2.15017,"tcp_end":[0.57743,0.18004,0.2746],"tcp_start":[0.58164,0.18151,0.25417],"tcp_to_object_dist_end":0.26952,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":318.0,"n_steps_budget":930.0,"object_pos_end":[0.58951,0.18242,0.01602],"object_pos_start":[0.58884,0.18066,0.00532],"object_to_goal_dist_end":0.23217,"object_to_goal_dist_start":0.2429,"object_z_max":0.01675,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1272.0,"raw_peak_contact_force":0.12671,"tcp_end":[0.57597,0.17937,0.35484],"tcp_start":[0.57743,0.18004,0.2746],"tcp_to_object_dist_end":0.3391,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.89463,"average_solve_count":484.0,"average_success_count":484.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.generator.arc_height":0.04715,"approach_1.generator.speed":0.05949,"descend_1.generator.speed":0.02677,"descend_2.generator.speed":0.01849,"grasp_1.duration.max_time":0.84794,"lift_1.generator.speed":0.02124,"lift_1.target.offset_along_axis.distance":0.27597,"release_1.duration.max_time":0.72941,"retract_1.generator.speed":0.03041,"transport_1.generator.arc_height":0.07825,"transport_1.generator.speed":0.07218},"optimized_scores":{"best_composite_score":-0.03957,"best_fitness_score":0.69043,"best_task_score":0.42314},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":254.0,"contact_point_centroid":[0.62603,0.17252,-0.00543],"force_p95":1.07673,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.51976,"mean_force":0.29077,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61647,0.16888,0.16277]},{"body_a":"world","body_b":"grasp_target","contact_count":84.0,"contact_point_centroid":[0.50844,0.03916,-0.00144],"force_p95":0.60986,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65164,"mean_force":0.23593,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49819,0.03922,0.02642]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18232.0,"contact_point_centroid":[0.50209,0.05811,0.15405],"force_p95":0.07594,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29305,"mean_force":0.05178,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50202,0.03897,0.15222]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18352.0,"contact_point_centroid":[0.50236,0.01984,0.15845],"force_p95":0.07472,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29262,"mean_force":0.05118,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50224,0.03896,0.15638]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9050.0,"contact_point_centroid":[0.56606,0.08333,0.29118],"force_p95":0.09785,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16398,"mean_force":0.0646,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.56391,0.10223,0.29044]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9009.0,"contact_point_centroid":[0.57241,0.12798,0.28794],"force_p95":0.09219,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1582,"mean_force":0.06441,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.56995,0.10907,0.28691]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5125,0.03954,-0.00203],"force_p95":0.13296,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15527,"mean_force":0.12543,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50034,0.03942,0.0267]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1036.0,"contact_point_centroid":[0.62164,0.15115,0.14948],"force_p95":0.08417,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14659,"mean_force":0.05073,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.6207,0.17026,0.14895]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1243.0,"contact_point_centroid":[0.62176,0.18928,0.1492],"force_p95":0.07459,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14329,"mean_force":0.04458,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62066,0.17025,0.14888]},{"body_a":"world","body_b":"grasp_target","contact_count":2264.0,"contact_point_centroid":[0.51251,0.03972,-0.00194],"force_p95":0.13153,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12284,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50155,0.04483,0.25421]},{"body_a":"world","body_b":"grasp_target","contact_count":1472.0,"contact_point_centroid":[0.62842,0.17238,-0.00197],"force_p95":0.1238,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12525,"mean_force":0.12195,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.61369,0.16797,0.21111]},{"body_a":"world","body_b":"grasp_target","contact_count":2092.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50621,0.04382,0.10836]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2493.0,"contact_point_centroid":[0.62203,0.15136,0.1859],"force_p95":0.09536,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12145,"mean_force":0.06836,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.62239,0.17048,0.18527]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4108.0,"contact_point_centroid":[0.4998,0.02013,0.02821],"force_p95":0.0768,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0989,"mean_force":0.05165,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49915,0.03932,0.02543]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4881.0,"contact_point_centroid":[0.49976,0.05841,0.02723],"force_p95":0.06897,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09649,"mean_force":0.04494,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49915,0.03932,0.02543]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3451.0,"contact_point_centroid":[0.62331,0.18924,0.18422],"force_p95":0.07248,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09407,"mean_force":0.04989,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.62239,0.17049,0.18382]}],"total_contact_groups":16},"final_pose_error":0.01998,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.62842,0.17238,0.01602],"final_tcp_position":[0.61371,0.16792,0.25259],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1968.42347,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":567.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2264.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.50796,0.04779,0.18331],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15756,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":523.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2092.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_pre_grasp","tcp_end":[0.50741,0.04004,0.03439],"tcp_start":[0.50796,0.04779,0.18331],"tcp_to_object_dist_end":0.00981,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51236,0.0392,0.02588],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.2127,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.13003,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10789.0,"raw_peak_contact_force":0.15527,"tcp_end":[0.49912,0.03932,0.02539],"tcp_start":[0.50741,0.04004,0.03439],"tcp_to_object_dist_end":0.01325,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":912.0,"n_steps_budget":1000.0,"object_pos_end":[0.52041,0.03905,0.27481],"object_pos_start":[0.51236,0.0392,0.02588],"object_to_goal_dist_end":0.21481,"object_to_goal_dist_start":0.2127,"object_z_max":0.27455,"peak_contact_force":0.07012,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":36668.0,"raw_peak_contact_force":0.65164,"subtask_id":"reach_pre_grasp","tcp_end":[0.50921,0.03898,0.28235],"tcp_start":[0.49912,0.03932,0.02539],"tcp_to_object_dist_end":0.0135,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":571.0,"n_steps_budget":1000.0,"object_pos_end":[0.62867,0.16987,0.19883],"object_pos_start":[0.52041,0.03905,0.27481],"object_to_goal_dist_end":0.05388,"object_to_goal_dist_start":0.21481,"object_z_max":0.30055,"peak_contact_force":0.0988,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":18059.0,"raw_peak_contact_force":0.16398,"subtask_id":"reach_goal","tcp_end":[0.62395,0.17073,0.21438],"tcp_start":[0.50921,0.03898,0.28235],"tcp_to_object_dist_end":0.01628,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":175.0,"n_steps_budget":1000.0,"object_pos_end":[0.62805,0.17052,0.13676],"object_pos_start":[0.62867,0.16987,0.19883],"object_to_goal_dist_end":0.00851,"object_to_goal_dist_start":0.05388,"object_z_max":0.19883,"peak_contact_force":1968.42347,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5944.0,"raw_peak_contact_force":0.12145,"subtask_id":"reach_goal","tcp_end":[0.62281,0.17088,0.15334],"tcp_start":[0.62395,0.17073,0.21438],"tcp_to_object_dist_end":0.01739,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.62855,0.17221,0.01601],"object_pos_start":[0.62805,0.17052,0.13676],"object_to_goal_dist_end":0.12902,"object_to_goal_dist_start":0.00851,"object_z_max":0.13676,"peak_contact_force":0.10198,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2533.0,"raw_peak_contact_force":1.51976,"tcp_end":[0.61641,0.16886,0.17236],"tcp_start":[0.62281,0.17088,0.15334],"tcp_to_object_dist_end":0.15685,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":368.0,"n_steps_budget":1000.0,"object_pos_end":[0.62842,0.17238,0.01602],"object_pos_start":[0.62855,0.17221,0.01601],"object_to_goal_dist_end":0.12901,"object_to_goal_dist_start":0.12902,"object_z_max":0.01647,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1472.0,"raw_peak_contact_force":0.12525,"tcp_end":[0.61371,0.16792,0.25259],"tcp_start":[0.61641,0.16886,0.17236],"tcp_to_object_dist_end":0.23706,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.28289,"average_solve_count":304.0,"average_success_count":304.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.generator.arc_height":0.05913,"approach_1.generator.speed":0.08009,"descend_1.generator.speed":0.03637,"descend_2.generator.speed":0.03295,"grasp_1.duration.max_time":1.29696,"lift_1.generator.speed":0.05838,"lift_1.target.offset_along_axis.distance":0.21153,"release_1.duration.max_time":0.72633,"retract_1.generator.speed":0.05632,"transport_1.generator.arc_height":0.06001,"transport_1.generator.speed":0.1292},"optimized_scores":{"best_composite_score":-0.13027,"best_fitness_score":0.59973,"best_task_score":0.23935},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":218.0,"contact_point_centroid":[0.58225,0.22823,-0.00783],"force_p95":1.17437,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.78427,"mean_force":0.36536,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57199,0.22145,0.24849]},{"body_a":"world","body_b":"grasp_target","contact_count":80.0,"contact_point_centroid":[0.47983,0.04832,-0.00137],"force_p95":0.56524,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65181,"mean_force":0.17465,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46922,0.04812,0.02787]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1364.0,"contact_point_centroid":[0.57719,0.23527,0.2581],"force_p95":0.15961,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.47068,"mean_force":0.1029,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.57278,0.21726,0.2612]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1023.0,"contact_point_centroid":[0.57735,0.19909,0.25848],"force_p95":0.17361,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.45625,"mean_force":0.129,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.57273,0.21717,0.26157]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":436.0,"contact_point_centroid":[0.57875,0.24057,0.22746],"force_p95":0.16476,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.40804,"mean_force":0.10688,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57483,0.2229,0.23255]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7867.0,"contact_point_centroid":[0.5136,0.08699,0.27403],"force_p95":0.1224,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35645,"mean_force":0.07639,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.51008,0.10575,0.27322]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":312.0,"contact_point_centroid":[0.57982,0.20526,0.22819],"force_p95":0.21226,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32494,"mean_force":0.1415,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57497,0.22297,0.23293]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8398.0,"contact_point_centroid":[0.51793,0.13112,0.2783],"force_p95":0.10427,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31623,"mean_force":0.07253,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.51391,0.11244,0.27727]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12438.0,"contact_point_centroid":[0.47264,0.06701,0.12037],"force_p95":0.07849,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29876,"mean_force":0.05413,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47235,0.04789,0.11815]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12483.0,"contact_point_centroid":[0.47291,0.0288,0.1232],"force_p95":0.07757,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27672,"mean_force":0.05372,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4725,0.04789,0.12079]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48269,0.04858,-0.00203],"force_p95":0.1332,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15919,"mean_force":0.12551,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47127,0.04835,0.02779]},{"body_a":"world","body_b":"grasp_target","contact_count":2504.0,"contact_point_centroid":[0.4827,0.04873,-0.00194],"force_p95":0.13053,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12282,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49229,0.05333,0.2604]},{"body_a":"world","body_b":"grasp_target","contact_count":1332.0,"contact_point_centroid":[0.5832,0.22756,-0.00197],"force_p95":0.12455,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12704,"mean_force":0.1201,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.57029,0.22061,0.29595]},{"body_a":"world","body_b":"grasp_target","contact_count":2080.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47781,0.05333,0.10829]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5065.0,"contact_point_centroid":[0.47,0.02901,0.02969],"force_p95":0.06614,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09409,"mean_force":0.04283,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47014,0.04824,0.02666]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5374.0,"contact_point_centroid":[0.46981,0.0675,0.02913],"force_p95":0.06521,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09277,"mean_force":0.0414,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47014,0.04824,0.02666]}],"total_contact_groups":16},"final_pose_error":0.01996,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.5832,0.22756,0.01602],"final_tcp_position":[0.57045,0.22059,0.3369],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":1.78427,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":627.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2504.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.48039,0.05783,0.18293],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15719,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":520.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2080.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_pre_grasp","tcp_end":[0.47803,0.04906,0.03466],"tcp_start":[0.48039,0.05783,0.18293],"tcp_to_object_dist_end":0.00983,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48256,0.04826,0.02587],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29042,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.13147,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12239.0,"raw_peak_contact_force":0.15919,"tcp_end":[0.47011,0.04823,0.02663],"tcp_start":[0.47803,0.04906,0.03466],"tcp_to_object_dist_end":0.01247,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":650.0,"n_steps_budget":1000.0,"object_pos_end":[0.49023,0.04801,0.21104],"object_pos_start":[0.48256,0.04826,0.02587],"object_to_goal_dist_end":0.20367,"object_to_goal_dist_start":0.29042,"object_z_max":0.21077,"peak_contact_force":0.08017,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":25001.0,"raw_peak_contact_force":0.65181,"subtask_id":"reach_pre_grasp","tcp_end":[0.47869,0.04794,0.21802],"tcp_start":[0.47011,0.04823,0.02663],"tcp_to_object_dist_end":0.01349,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":605.0,"n_steps_budget":1000.0,"object_pos_end":[0.58093,0.21258,0.26236],"object_pos_start":[0.49023,0.04801,0.21104],"object_to_goal_dist_end":0.0358,"object_to_goal_dist_start":0.20367,"object_z_max":0.28643,"peak_contact_force":0.16045,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":16265.0,"raw_peak_contact_force":0.35645,"subtask_id":"reach_goal","tcp_end":[0.57119,0.2125,0.28388],"tcp_start":[0.47869,0.04794,0.21802],"tcp_to_object_dist_end":0.02362,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":13.0,"n_steps":152.0,"n_steps_budget":1000.0,"object_pos_end":[0.58294,0.22401,0.21218],"object_pos_start":[0.58093,0.21258,0.26236],"object_to_goal_dist_end":0.01897,"object_to_goal_dist_start":0.0358,"object_z_max":0.26236,"peak_contact_force":0.15711,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2387.0,"raw_peak_contact_force":0.47068,"subtask_id":"reach_goal","tcp_end":[0.57636,0.2234,0.23656],"tcp_start":[0.57119,0.2125,0.28388],"tcp_to_object_dist_end":0.02527,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58317,0.22673,0.01437],"object_pos_start":[0.58294,0.22401,0.21218],"object_to_goal_dist_end":0.21613,"object_to_goal_dist_start":0.01897,"object_z_max":0.21218,"peak_contact_force":0.06866,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":966.0,"raw_peak_contact_force":1.78427,"tcp_end":[0.57196,0.22144,0.25678],"tcp_start":[0.57636,0.2234,0.23656],"tcp_to_object_dist_end":0.24273,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":333.0,"n_steps_budget":1000.0,"object_pos_end":[0.5832,0.22756,0.01602],"object_pos_start":[0.58317,0.22673,0.01437],"object_to_goal_dist_end":0.21447,"object_to_goal_dist_start":0.21613,"object_z_max":0.01675,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1332.0,"raw_peak_contact_force":0.12704,"tcp_end":[0.57045,0.22059,0.3369],"tcp_start":[0.57196,0.22144,0.25678],"tcp_to_object_dist_end":0.32121,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```