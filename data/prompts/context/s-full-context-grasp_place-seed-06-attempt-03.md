## Search State

- **Seed**: 6
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 14 | -0.3100 | 0.22 | ❌ rejected |
| 2 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 14 | -0.3044 | 0.23 | ❌ rejected |
| 1 | approach → descend → grasp → lift → approach → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 12 | -0.1602 | 0.25 | ✅ accepted |
| 0 | align → lift → push → approach → approach → descend → grasp → rotate | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | arc_cartesian | linear_cartesian | — | impedance_motion | position_control | position_control | impedance_control | force_threshold_switch | position_control | admittance_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6 | -0.1416 | 0.25 | ✅ accepted |

**Proposal policy**: task_score is 0.22 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.310) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: approach_pre_grasp
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.12
  weight: 0.3
- id: reach_grasp
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.04
  weight: 0.2
- id: approach_lift
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.2
  weight: 0.3
- id: reach_goal
  weight: 0.2
phases:
- id: approach_above
  type: approach
  generator: arc_cartesian
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
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.08
      - 0.18
      default: 0.12
      binds_to:
      - path: target.offset.z
        mode: replace
    arc_height:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.arc_height
        mode: replace
    speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_pre_grasp
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
    - 0.04
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_offset:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.04
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_grasp
- id: grasp_close
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
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: duration.max_time
        mode: replace
  guards:
  - id: check_grasp
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.5
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: repeat
- id: lift_object
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
    - 0.2
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.12
      - 0.28
      default: 0.2
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_lift
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
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_goal
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
  parameters:
    release_duration:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: duration.max_time
        mode: replace
- id: retract_up
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
    - 0.1
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: add
    speed:
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
- **approach_above** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.12], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.04], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_offset: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **grasp_close** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - grasp_duration: status=consumed; consumers=duration.max_time (replace)
  - guards:
    - id=check_grasp, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.5
  - retries: max_attempts=1, strategy=repeat
- **lift_object** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.2], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **transport_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **release_object** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - release_duration: status=consumed; consumers=duration.max_time (replace)
- **retract_up** (`retract`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_height: status=consumed; consumers=target.offset.z (add)
    - speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: -0.310
- **task_score** (E): 0.216
- **fitness_score**: 0.570  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.880

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above | 1.00 | 1.00 | 0.1296 |
| descend_to_grasp | 1.00 | 1.00 | 0.1232 |
| grasp_close | 1.00 | 1.00 | 0.0117 |
| lift_object | 0.00 | 1.00 | 0.1105 |
| transport_to_goal | 0.00 | 1.00 | 0.0907 |
| descend_to_place | 0.67 | 1.00 | 0.1088 |
| release_object | 1.00 | 1.00 | 0.0220 |
| retract_up | 1.00 | 1.00 | 0.1927 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, 0.030, 0.179) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.496, 0.030, 0.179)→(0.495, 0.025, 0.055) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 | 1.00 / 4.000 | 6.565 | 0.123 |
| grasp_close | grasp | 1.00 / step_budget | (0.495, 0.025, 0.055)→(0.487, 0.024, 0.047) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.272 | 1.00 / 44.000 | 0.141 | 0.187 |
| lift_object | lift | 0.00 / step_budget | (0.487, 0.024, 0.047)→(0.483, 0.024, 0.157) | (0.500, 0.024, 0.026)→(0.491, 0.024, 0.128) | 0.272→0.223 | 1.00 / 23.667 | 0.123 | 0.421 |
| transport_to_goal | approach | 0.00 / step_budget | (0.483, 0.024, 0.157)→(0.521, 0.082, 0.214) | (0.491, 0.024, 0.128)→(0.527, 0.081, 0.016) | 0.223→0.237 | 1.00 / 8.000 | 9752.657 | 1.662 |
| descend_to_place | descend | 0.67 / step_budget | (0.521, 0.082, 0.214)→(0.578, 0.165, 0.195) | (0.527, 0.081, 0.016)→(0.527, 0.081, 0.016) | 0.237→0.237 | 1.00 / 8.000 | 6499.315 | 0.125 |
| release_object | release | 1.00 / step_budget | (0.578, 0.165, 0.195)→(0.573, 0.164, 0.217) | (0.527, 0.081, 0.016)→(0.527, 0.081, 0.016) | 0.237→0.237 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract_up | retract | 1.00 / step_budget | (0.573, 0.164, 0.217)→(0.597, 0.194, 0.404) | (0.527, 0.081, 0.016)→(0.527, 0.081, 0.016) | 0.237→0.237 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.307
- phase_score: 0.331
- phase_breakdown.approach_pre_grasp_score: 0.277
- phase_breakdown.reach_goal_score: 0.032
- phase_breakdown.reach_grasp_score: 0.741
- phase_breakdown.place_at_goal_score: 0.819
- phase_breakdown.approach_lift_score: 0.087
- grasp_place_fitness: 0.616

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.616
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.307
- **Median Q (composite search score)**: -0.324
- **K-run variance**: 0.0011
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.325


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.23028,"average_solve_count":317.0,"average_success_count":317.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_height":0.14965,"approach_above.arc_height":0.0619,"approach_above.speed":0.04821,"descend_to_grasp.descend_offset":0.02062,"descend_to_grasp.speed":0.02648,"descend_to_place.place_speed":0.04141,"grasp_close.grasp_duration":0.1486,"lift_object.lift_height":0.19666,"lift_object.speed":0.06655,"release_object.release_duration":0.1138,"retract_up.retract_height":0.09595,"retract_up.speed":0.08766,"transport_to_goal.approach_goal_height":0.12552,"transport_to_goal.transport_speed":0.06947},"optimized_scores":{"best_composite_score":-0.34182,"best_fitness_score":0.53818,"best_task_score":0.15109},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":632.0,"contact_point_centroid":[0.52894,0.03529,-0.00369],"force_p95":0.74819,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.7658,"mean_force":0.20075,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51311,0.04491,0.21385]},{"body_a":"world","body_b":"grasp_target","contact_count":162.0,"contact_point_centroid":[0.50054,-0.01389,-0.00117],"force_p95":0.24985,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.4342,"mean_force":0.07141,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48935,-0.01468,0.04815]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16367.0,"contact_point_centroid":[0.48859,0.00441,0.09713],"force_p95":0.10016,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28925,"mean_force":0.06193,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.4868,-0.01463,0.09656]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18364.0,"contact_point_centroid":[0.48855,-0.03354,0.09711],"force_p95":0.08904,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28209,"mean_force":0.05593,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48682,-0.01463,0.09635]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7010.0,"contact_point_centroid":[0.50045,0.02747,0.17425],"force_p95":0.13629,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.265,"mean_force":0.0971,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.49524,0.00899,0.17567]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8256.0,"contact_point_centroid":[0.50079,-0.00823,0.17509],"force_p95":0.12228,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20706,"mean_force":0.08274,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.49572,0.00995,0.17669]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50384,-0.01558,-0.00208],"force_p95":0.14691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19733,"mean_force":0.12893,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.49209,-0.01472,0.04757]},{"body_a":"world","body_b":"grasp_target","contact_count":2692.0,"contact_point_centroid":[0.50382,-0.01567,-0.00195],"force_p95":0.12957,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12281,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.49901,0.02779,0.23162]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.52908,0.0353,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12299,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.536,0.09465,0.22218]},{"body_a":"world","body_b":"grasp_target","contact_count":1704.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.4981,-0.01134,0.11475]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.52908,0.0353,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.55231,0.13176,0.23161]},{"body_a":"world","body_b":"grasp_target","contact_count":2704.0,"contact_point_centroid":[0.52908,0.0353,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.56693,0.15804,0.33814]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4344.0,"contact_point_centroid":[0.49146,0.00455,0.04803],"force_p95":0.07512,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12255,"mean_force":0.04965,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.49095,-0.0147,0.04633]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5353.0,"contact_point_centroid":[0.49215,-0.03383,0.04854],"force_p95":0.06666,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07175,"mean_force":0.0412,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.49095,-0.0147,0.04633]},{"body_a":"left_finger","body_b":"right_finger","contact_count":437.0,"contact_point_centroid":[0.51419,0.04653,0.21773],"force_p95":0.01424,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01649,"mean_force":0.01113,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51393,0.04653,0.21559]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4312.0,"contact_point_centroid":[0.53619,0.09452,0.22439],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01279,"mean_force":0.01035,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.53593,0.09452,0.22215]}],"total_contact_groups":17},"final_pose_error":0.01977,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.52908,0.0353,0.01602],"final_tcp_position":[0.58442,0.18379,0.4248],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":9748.81782,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":674.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2692.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_pre_grasp","tcp_end":[0.50006,-0.00805,0.17444],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14867,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":426.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1704.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.4989,-0.01479,0.05503],"tcp_start":[0.50006,-0.00805,0.17444],"tcp_to_object_dist_end":0.02944,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50375,-0.0149,0.02569],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31198,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.14575,"phase_name":"grasp_close","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11497.0,"raw_peak_contact_force":0.19733,"tcp_end":[0.49092,-0.0147,0.0463],"tcp_start":[0.4989,-0.01479,0.05503],"tcp_to_object_dist_end":0.02428,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49498,-0.01491,0.12634],"object_pos_start":[0.50375,-0.0149,0.02569],"object_to_goal_dist_end":0.25344,"object_to_goal_dist_start":0.31198,"object_z_max":0.12622,"peak_contact_force":0.10383,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":34893.0,"raw_peak_contact_force":0.4342,"subtask_id":"approach_lift","tcp_end":[0.48696,-0.01462,0.15508],"tcp_start":[0.49092,-0.0147,0.0463],"tcp_to_object_dist_end":0.02984,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52908,0.0353,0.01601],"object_pos_start":[0.49498,-0.01491,0.12634],"object_to_goal_dist_end":0.2835,"object_to_goal_dist_start":0.25344,"object_z_max":0.16664,"peak_contact_force":9748.81782,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":16335.0,"raw_peak_contact_force":1.7658,"subtask_id":"reach_goal","tcp_end":[0.51537,0.04933,0.2186],"tcp_start":[0.48696,-0.01462,0.15508],"tcp_to_object_dist_end":0.20354,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52908,0.0353,0.01602],"object_pos_start":[0.52908,0.0353,0.01601],"object_to_goal_dist_end":0.28349,"object_to_goal_dist_start":0.2835,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8312.0,"raw_peak_contact_force":0.12299,"subtask_id":"place_at_goal","tcp_end":[0.55566,0.13252,0.22945],"tcp_start":[0.51537,0.04933,0.2186],"tcp_to_object_dist_end":0.23603,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.52908,0.0353,0.01602],"object_pos_start":[0.52908,0.0353,0.01602],"object_to_goal_dist_end":0.28349,"object_to_goal_dist_start":0.28349,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1024.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.55107,0.13139,0.25182],"tcp_start":[0.55566,0.13252,0.22945],"tcp_to_object_dist_end":0.25558,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":676.0,"n_steps_budget":1000.0,"object_pos_end":[0.52908,0.0353,0.01602],"object_pos_start":[0.52908,0.0353,0.01602],"object_to_goal_dist_end":0.28349,"object_to_goal_dist_start":0.28349,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2704.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58442,0.18379,0.4248],"tcp_start":[0.55107,0.13139,0.25182],"tcp_to_object_dist_end":0.43842,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.29333,"average_solve_count":300.0,"average_success_count":300.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_height":0.17968,"approach_above.arc_height":0.04187,"approach_above.speed":0.07179,"descend_to_grasp.descend_offset":0.02115,"descend_to_grasp.speed":0.03252,"descend_to_place.place_speed":0.07121,"grasp_close.grasp_duration":0.24595,"lift_object.lift_height":0.27883,"lift_object.speed":0.06814,"release_object.release_duration":0.11966,"retract_up.retract_height":0.07738,"retract_up.speed":0.04789,"transport_to_goal.approach_goal_height":0.13306,"transport_to_goal.transport_speed":0.09976},"optimized_scores":{"best_composite_score":-0.26412,"best_fitness_score":0.61588,"best_task_score":0.30731},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2124.0,"contact_point_centroid":[0.54741,0.08154,-0.00243],"force_p95":0.17451,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.5414,"mean_force":0.14239,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.537,0.08404,0.19313]},{"body_a":"world","body_b":"grasp_target","contact_count":163.0,"contact_point_centroid":[0.50941,0.03884,-0.00116],"force_p95":0.23806,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.41593,"mean_force":0.06885,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49786,0.03918,0.04831]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3980.0,"contact_point_centroid":[0.51196,0.03447,0.16486],"force_p95":0.13919,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29591,"mean_force":0.09351,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5065,0.05303,0.16677]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17167.0,"contact_point_centroid":[0.49742,0.05792,0.09863],"force_p95":0.09526,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29407,"mean_force":0.05967,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49537,0.03899,0.09795]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16595.0,"contact_point_centroid":[0.4968,0.02004,0.09806],"force_p95":0.10058,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28792,"mean_force":0.06138,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49535,0.03898,0.09774]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4555.0,"contact_point_centroid":[0.51279,0.07146,0.16625],"force_p95":0.12128,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2851,"mean_force":0.0785,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50676,0.0533,0.167]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51251,0.03966,-0.00204],"force_p95":0.13438,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16444,"mean_force":0.12583,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.50068,0.03941,0.04806]},{"body_a":"world","body_b":"grasp_target","contact_count":1852.0,"contact_point_centroid":[0.51251,0.03972,-0.00192],"force_p95":0.13354,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12289,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.50105,0.03984,0.2697]},{"body_a":"world","body_b":"grasp_target","contact_count":2136.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50634,0.0437,0.13415]},{"body_a":"world","body_b":"grasp_target","contact_count":3780.0,"contact_point_centroid":[0.54757,0.08152,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59094,0.13956,0.16322]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.54757,0.08152,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.61724,0.16859,0.13753]},{"body_a":"world","body_b":"grasp_target","contact_count":2660.0,"contact_point_centroid":[0.54757,0.08152,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.61864,0.1693,0.22912]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4362.0,"contact_point_centroid":[0.4998,0.02014,0.04852],"force_p95":0.0734,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10179,"mean_force":0.04932,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.49953,0.03932,0.04678]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4883.0,"contact_point_centroid":[0.50003,0.05846,0.04818],"force_p95":0.06957,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08794,"mean_force":0.04468,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.49954,0.03932,0.04678]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1943.0,"contact_point_centroid":[0.53913,0.08585,0.19698],"force_p95":0.01181,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01652,"mean_force":0.01075,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5388,0.08583,0.1947]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4005.0,"contact_point_centroid":[0.59141,0.13961,0.16546],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01284,"mean_force":0.01051,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59096,0.13959,0.16319]}],"total_contact_groups":17},"final_pose_error":0.01979,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.54757,0.08152,0.01602],"final_tcp_position":[0.62485,0.17148,0.30283],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":9748.93459,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":464.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1852.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_pre_grasp","tcp_end":[0.50783,0.04756,0.21356],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.18776,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":534.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2136.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.50757,0.04001,0.05582],"tcp_start":[0.50783,0.04756,0.21356],"tcp_to_object_dist_end":0.03021,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51243,0.03937,0.02584],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21258,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.13345,"phase_name":"grasp_close","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11045.0,"raw_peak_contact_force":0.16444,"tcp_end":[0.4995,0.03932,0.04674],"tcp_start":[0.50757,0.04001,0.05582],"tcp_to_object_dist_end":0.02457,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50347,0.03922,0.1295],"object_pos_start":[0.51243,0.03937,0.02584],"object_to_goal_dist_end":0.18278,"object_to_goal_dist_start":0.21258,"object_z_max":0.12942,"peak_contact_force":0.12846,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":33925.0,"raw_peak_contact_force":0.41593,"subtask_id":"approach_lift","tcp_end":[0.49562,0.03901,0.15889],"tcp_start":[0.4995,0.03932,0.04674],"tcp_to_object_dist_end":0.03042,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54757,0.08152,0.01602],"object_pos_start":[0.50347,0.03922,0.1295],"object_to_goal_dist_end":0.17698,"object_to_goal_dist_start":0.18278,"object_z_max":0.14339,"peak_contact_force":9748.93459,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":12602.0,"raw_peak_contact_force":1.5414,"subtask_id":"reach_goal","tcp_end":[0.5507,0.0977,0.20505],"tcp_start":[0.49562,0.03901,0.15889],"tcp_to_object_dist_end":0.18975,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":945.0,"n_steps_budget":1000.0,"object_pos_end":[0.54757,0.08152,0.01602],"object_pos_start":[0.54757,0.08152,0.01602],"object_to_goal_dist_end":0.17698,"object_to_goal_dist_start":0.17698,"object_z_max":0.01602,"peak_contact_force":9748.84649,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7785.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_at_goal","tcp_end":[0.62185,0.16995,0.13722],"tcp_start":[0.5507,0.0977,0.20505],"tcp_to_object_dist_end":0.16741,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54757,0.08152,0.01602],"object_pos_start":[0.54757,0.08152,0.01602],"object_to_goal_dist_end":0.17698,"object_to_goal_dist_start":0.17698,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1020.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61543,0.168,0.15691],"tcp_start":[0.62185,0.16995,0.13722],"tcp_to_object_dist_end":0.1787,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":665.0,"n_steps_budget":1000.0,"object_pos_end":[0.54757,0.08152,0.01602],"object_pos_start":[0.54757,0.08152,0.01602],"object_to_goal_dist_end":0.17698,"object_to_goal_dist_start":0.17698,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2660.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62485,0.17148,0.30283],"tcp_start":[0.61543,0.168,0.15691],"tcp_to_object_dist_end":0.31036,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.01934,"average_solve_count":362.0,"average_success_count":362.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_height":0.10838,"approach_above.arc_height":0.02302,"approach_above.speed":0.05817,"descend_to_grasp.descend_offset":0.02102,"descend_to_grasp.speed":0.01284,"descend_to_place.place_speed":0.08144,"grasp_close.grasp_duration":0.2322,"lift_object.lift_height":0.21588,"lift_object.speed":0.06735,"release_object.release_duration":0.10504,"retract_up.retract_height":0.17447,"retract_up.speed":0.07316,"transport_to_goal.approach_goal_height":0.14863,"transport_to_goal.transport_speed":0.02014},"optimized_scores":{"best_composite_score":-0.32398,"best_fitness_score":0.55602,"best_task_score":0.18899},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":233.0,"contact_point_centroid":[0.50529,0.12527,-0.00653],"force_p95":1.18549,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.67816,"mean_force":0.33385,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.49608,0.0986,0.21548]},{"body_a":"world","body_b":"grasp_target","contact_count":154.0,"contact_point_centroid":[0.47958,0.04682,-0.00116],"force_p95":0.28467,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.41152,"mean_force":0.07326,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46889,0.04761,0.0494]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17611.0,"contact_point_centroid":[0.46805,0.06631,0.09878],"force_p95":0.09333,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29541,"mean_force":0.05813,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.4664,0.04738,0.09817]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16689.0,"contact_point_centroid":[0.46744,0.02838,0.09821],"force_p95":0.11239,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26832,"mean_force":0.06138,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46638,0.04738,0.09801]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7407.0,"contact_point_centroid":[0.48324,0.05304,0.17945],"force_p95":0.1338,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24314,"mean_force":0.10227,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.47861,0.07133,0.18286]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48272,0.04866,-0.00208],"force_p95":0.14544,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19775,"mean_force":0.12872,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.4715,0.04788,0.04873]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8246.0,"contact_point_centroid":[0.48325,0.08859,0.17909],"force_p95":0.13293,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18849,"mean_force":0.09266,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.47812,0.07051,0.18192]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.4827,0.04873,-0.00194],"force_p95":0.13205,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12285,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.49007,0.03565,0.22946]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.50478,0.1263,-0.00198],"force_p95":0.12302,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12881,"mean_force":0.12211,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.52826,0.15129,0.21628]},{"body_a":"world","body_b":"grasp_target","contact_count":1376.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47792,0.04944,0.10191]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.50478,0.1263,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.55311,0.19283,0.22134]},{"body_a":"world","body_b":"grasp_target","contact_count":3752.0,"contact_point_centroid":[0.50478,0.1263,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.56526,0.2094,0.36196]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4832.0,"contact_point_centroid":[0.46962,0.02852,0.04951],"force_p95":0.06915,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10503,"mean_force":0.04503,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.47041,0.04777,0.04759]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5419.0,"contact_point_centroid":[0.46995,0.067,0.04924],"force_p95":0.06709,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.06994,"mean_force":0.04095,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.47041,0.04777,0.0476]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4306.0,"contact_point_centroid":[0.5289,0.15148,0.21857],"force_p95":0.01109,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01551,"mean_force":0.01042,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.52837,0.15146,0.21629]},{"body_a":"left_finger","body_b":"right_finger","contact_count":5.0,"contact_point_centroid":[0.49913,0.09997,0.22064],"force_p95":0.01409,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01409,"mean_force":0.01409,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.49695,0.09994,0.2171]}],"total_contact_groups":17},"final_pose_error":0.01992,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.50478,0.1263,0.01602],"final_tcp_position":[0.58126,0.22706,0.48513],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":9760.21755,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":551.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2200.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_pre_grasp","tcp_end":[0.48056,0.05057,0.1478],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12181,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":344.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":19.45009,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1376.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.47806,0.04854,0.05563],"tcp_start":[0.48056,0.05057,0.1478],"tcp_to_object_dist_end":0.02997,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48264,0.04806,0.0257],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29064,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.14364,"phase_name":"grasp_close","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12051.0,"raw_peak_contact_force":0.19775,"tcp_end":[0.47038,0.04777,0.04756],"tcp_start":[0.47806,0.04854,0.05563],"tcp_to_object_dist_end":0.02507,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4746,0.04811,0.12776],"object_pos_start":[0.48264,0.04806,0.0257],"object_to_goal_dist_end":0.23394,"object_to_goal_dist_start":0.29064,"object_z_max":0.12764,"peak_contact_force":0.13719,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":34454.0,"raw_peak_contact_force":0.41152,"subtask_id":"approach_lift","tcp_end":[0.46645,0.04739,0.15807],"tcp_start":[0.47038,0.04777,0.04756],"tcp_to_object_dist_end":0.03139,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50381,0.12596,0.01549],"object_pos_start":[0.4746,0.04811,0.12776],"object_to_goal_dist_end":0.25081,"object_to_goal_dist_start":0.23394,"object_z_max":0.16928,"peak_contact_force":9760.21755,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":15891.0,"raw_peak_contact_force":1.67816,"subtask_id":"reach_goal","tcp_end":[0.49698,0.09999,0.21716],"tcp_start":[0.46645,0.04739,0.15807],"tcp_to_object_dist_end":0.20345,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50478,0.1263,0.01602],"object_pos_start":[0.50381,0.12596,0.01549],"object_to_goal_dist_end":0.24991,"object_to_goal_dist_start":0.25081,"object_z_max":0.01669,"peak_contact_force":9748.97703,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8306.0,"raw_peak_contact_force":0.12881,"subtask_id":"place_at_goal","tcp_end":[0.55648,0.19402,0.21957],"tcp_start":[0.49698,0.09999,0.21716],"tcp_to_object_dist_end":0.22066,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50478,0.1263,0.01602],"object_pos_start":[0.50478,0.1263,0.01602],"object_to_goal_dist_end":0.24991,"object_to_goal_dist_start":0.24991,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1025.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.55187,0.1923,0.24138],"tcp_start":[0.55648,0.19402,0.21957],"tcp_to_object_dist_end":0.23951,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":938.0,"n_steps_budget":1000.0,"object_pos_end":[0.50478,0.1263,0.01602],"object_pos_start":[0.50478,0.1263,0.01602],"object_to_goal_dist_end":0.24991,"object_to_goal_dist_start":0.24991,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3752.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58126,0.22706,0.48513],"tcp_start":[0.55187,0.1923,0.24138],"tcp_to_object_dist_end":0.48587,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```