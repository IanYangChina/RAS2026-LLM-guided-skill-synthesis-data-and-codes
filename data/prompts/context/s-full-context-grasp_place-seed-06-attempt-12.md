## Search State

- **Seed**: 6
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 16 | -0.3830 | 0.27 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 16 | -0.3662 | 0.30 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 12 | -0.1459 | 0.28 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 14 | -0.2636 | 0.31 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 9 | 0.2855 | 0.73 | ✅ accepted |

**Proposal policy**: task_score is 0.27 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.383) — your mutation base

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
  weight: 0.2
- id: reach_grasp
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.04
  weight: 0.2
- id: lift_clearance
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.2
- id: reach_goal
  offset:
  - 0.0
  - 0.0
  - 0.035
  weight: 0.4
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
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.2
      axis: world_z
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    lift_distance:
      type: scalar
      range:
      - 0.1
      - 0.35
      default: 0.2
      binds_to:
      - path: target.offset_along_axis.distance
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
    - 0.035
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_goal

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
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.2, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **transport_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.035], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: -0.383
- **task_score** (E): 0.269
- **fitness_score**: 0.597  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.980

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above | 1.00 | 1.00 | 0.1312 |
| descend_to_grasp | 1.00 | 1.00 | 0.1220 |
| grasp_close | 1.00 | 1.00 | 0.0117 |
| lift_object | 1.00 | 1.00 | 0.2419 |
| transport_to_goal | 0.67 | 1.00 | 0.1949 |
| descend_to_goal | 1.00 | 1.00 | 0.1391 |
| release_object | 1.00 | 1.00 | 0.0203 |
| retract_from_goal | 1.00 | 1.00 | 0.2158 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, 0.032, 0.177) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.496, 0.032, 0.177)→(0.495, 0.025, 0.055) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 | 1.00 / 4.000 | 27.129 | 0.123 |
| grasp_close | grasp | 1.00 / step_budget | (0.495, 0.025, 0.055)→(0.487, 0.024, 0.047) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.272 | 1.00 / 44.000 | 0.167 | 0.203 |
| lift_object | lift | 1.00 / step_budget | (0.487, 0.024, 0.047)→(0.485, 0.024, 0.288) | (0.500, 0.024, 0.026)→(0.490, 0.024, 0.262) | 0.272→0.213 | 1.00 / 37.000 | 0.084 | 0.412 |
| transport_to_goal | approach | 0.67 / step_budget | (0.485, 0.024, 0.288)→(0.571, 0.150, 0.399) | (0.490, 0.024, 0.262)→(0.553, 0.131, 0.011) | 0.213→0.218 | 1.00 / 7.000 | 0.436 | 2.562 |
| descend_to_goal | descend | 1.00 / step_budget | (0.571, 0.150, 0.399)→(0.594, 0.191, 0.271) | (0.553, 0.131, 0.011)→(0.556, 0.133, 0.019) | 0.218→0.209 | 1.00 / 8.000 | 0.123 | 0.414 |
| release_object | release | 1.00 / step_budget | (0.594, 0.191, 0.271)→(0.590, 0.190, 0.290) | (0.556, 0.133, 0.019)→(0.556, 0.133, 0.019) | 0.209→0.209 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract_from_goal | retract | 1.00 / step_budget | (0.590, 0.190, 0.290)→(0.591, 0.190, 0.506) | (0.556, 0.133, 0.019)→(0.556, 0.133, 0.019) | 0.209→0.209 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.420
- phase_score: 0.552
- phase_breakdown.approach_pre_grasp_score: 0.857
- phase_breakdown.reach_goal_score: 0.466
- phase_breakdown.reach_grasp_score: 0.720
- phase_breakdown.lift_clearance_score: 0.395
- phase_breakdown.transport_clearance_score: 0.410
- grasp_place_fitness: 0.674

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.674
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.420
- **Median Q (composite search score)**: -0.405
- **K-run variance**: 0.0031
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.329


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":9.0,"average_failure_rate":0.01982,"average_mean_iterations":7.04846,"average_solve_count":454.0,"average_success_count":445.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_height":0.15543,"approach_above.arc_height":0.03317,"approach_above.speed":0.04691,"descend_to_goal.descend_goal_offset":0.05177,"descend_to_goal.speed":0.04803,"descend_to_grasp.descend_offset":0.02157,"descend_to_grasp.speed":0.03077,"grasp_close.grasp_duration":0.13067,"lift_object.lift_distance":0.28136,"lift_object.speed":0.04344,"release_object.release_duration":0.22211,"retract_from_goal.retract_distance":0.28646,"retract_from_goal.retract_speed":0.06584,"transport_to_goal.arc_height":0.09362,"transport_to_goal.transport_height":0.18859,"transport_to_goal.transport_speed":0.21254},"optimized_scores":{"best_composite_score":-0.43764,"best_fitness_score":0.54236,"best_task_score":0.16181},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1546.0,"contact_point_centroid":[0.52805,0.05597,-0.00311],"force_p95":0.42573,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.66293,"mean_force":0.16779,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52278,0.05647,0.45145]},{"body_a":"world","body_b":"grasp_target","contact_count":86.0,"contact_point_centroid":[0.49993,-0.01444,-0.00149],"force_p95":0.3799,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.39749,"mean_force":0.14195,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48992,-0.01461,0.04843]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16750.0,"contact_point_centroid":[0.48774,0.0046,0.17586],"force_p95":0.08221,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27128,"mean_force":0.05709,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48775,-0.01457,0.17521]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18704.0,"contact_point_centroid":[0.48761,-0.03363,0.17453],"force_p95":0.07719,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26668,"mean_force":0.05167,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48774,-0.01456,0.17382]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5561.0,"contact_point_centroid":[0.49077,-0.03095,0.34684],"force_p95":0.12962,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24733,"mean_force":0.08012,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.48821,-0.01251,0.34838]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5332.0,"contact_point_centroid":[0.4909,0.00646,0.34661],"force_p95":0.1267,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2469,"mean_force":0.0841,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.48847,-0.01204,0.34894]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50384,-0.01559,-0.00209],"force_p95":0.14794,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20097,"mean_force":0.12937,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.49212,-0.01463,0.04854]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4343.0,"contact_point_centroid":[0.49149,0.00457,0.04867],"force_p95":0.07449,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1428,"mean_force":0.04949,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.49098,-0.01462,0.04731]},{"body_a":"world","body_b":"grasp_target","contact_count":1844.0,"contact_point_centroid":[0.50382,-0.01567,-0.00192],"force_p95":0.13354,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12289,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.49906,0.01362,0.2406]},{"body_a":"world","body_b":"grasp_target","contact_count":1796.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.49808,-0.01051,0.12068]},{"body_a":"world","body_b":"grasp_target","contact_count":2540.0,"contact_point_centroid":[0.52808,0.05588,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.56084,0.13571,0.38245]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.52808,0.05588,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.57918,0.1792,0.30423]},{"body_a":"world","body_b":"grasp_target","contact_count":3580.0,"contact_point_centroid":[0.52808,0.05588,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_from_goal","phase_type":"retract","tcp_position_centroid":[0.57838,0.17852,0.43869]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4946.0,"contact_point_centroid":[0.49144,-0.03377,0.04859],"force_p95":0.07084,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07253,"mean_force":0.0444,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.49099,-0.01462,0.04731]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1620.0,"contact_point_centroid":[0.5235,0.05726,0.45426],"force_p95":0.01186,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01622,"mean_force":0.01059,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52317,0.05725,0.45194]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2717.0,"contact_point_centroid":[0.56136,0.13566,0.3848],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01277,"mean_force":0.01042,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.56082,0.13565,0.38254]}],"total_contact_groups":17},"final_pose_error":0.04906,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.52808,0.05588,0.01602],"final_tcp_position":[0.58149,0.17952,0.56151],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":2.66293,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":462.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1844.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_pre_grasp","tcp_end":[0.49998,-0.00648,0.18582],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16012,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":449.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1796.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.49894,-0.0147,0.05602],"tcp_start":[0.49998,-0.00648,0.18582],"tcp_to_object_dist_end":0.03041,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50376,-0.01493,0.02567],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31202,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.14578,"phase_name":"grasp_close","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11089.0,"raw_peak_contact_force":0.20097,"tcp_end":[0.49096,-0.01462,0.04727],"tcp_start":[0.49894,-0.0147,0.05602],"tcp_to_object_dist_end":0.02511,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":36.0,"n_steps":901.0,"n_steps_budget":1000.0,"object_pos_end":[0.4932,-0.015,0.28097],"object_pos_start":[0.50376,-0.01493,0.02567],"object_to_goal_dist_end":0.22549,"object_to_goal_dist_start":0.31202,"object_z_max":0.2807,"peak_contact_force":0.08779,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":35540.0,"raw_peak_contact_force":0.39749,"subtask_id":"lift_clearance","tcp_end":[0.48873,-0.01459,0.30882],"tcp_start":[0.49096,-0.01462,0.04727],"tcp_to_object_dist_end":0.02821,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52808,0.05588,0.01602],"object_pos_start":[0.4932,-0.015,0.28097],"object_to_goal_dist_end":0.2732,"object_to_goal_dist_start":0.22549,"object_z_max":0.37005,"peak_contact_force":0.12263,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":14059.0,"raw_peak_contact_force":2.66293,"subtask_id":"transport_clearance","tcp_end":[0.54098,0.09296,0.46431],"tcp_start":[0.48873,-0.01459,0.30882],"tcp_to_object_dist_end":0.45,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":635.0,"n_steps_budget":1000.0,"object_pos_end":[0.52808,0.05588,0.01602],"object_pos_start":[0.52808,0.05588,0.01602],"object_to_goal_dist_end":0.2732,"object_to_goal_dist_start":0.2732,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5257.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.5816,0.17997,0.30351],"tcp_start":[0.54098,0.09296,0.46431],"tcp_to_object_dist_end":0.31767,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.52808,0.05588,0.01602],"object_pos_start":[0.52808,0.05588,0.01602],"object_to_goal_dist_end":0.2732,"object_to_goal_dist_start":0.2732,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1017.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57847,0.17882,0.32401],"tcp_start":[0.5816,0.17997,0.30351],"tcp_to_object_dist_end":0.33543,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":895.0,"n_steps_budget":1000.0,"object_pos_end":[0.52808,0.05588,0.01602],"object_pos_start":[0.52808,0.05588,0.01602],"object_to_goal_dist_end":0.2732,"object_to_goal_dist_start":0.2732,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_from_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3580.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58149,0.17952,0.56151],"tcp_start":[0.57847,0.17882,0.32401],"tcp_to_object_dist_end":0.56187,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.74127,"average_solve_count":487.0,"average_success_count":487.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_height":0.11576,"approach_above.arc_height":0.036,"approach_above.speed":0.09086,"descend_to_goal.descend_goal_offset":0.06585,"descend_to_goal.speed":0.01691,"descend_to_grasp.descend_offset":0.02002,"descend_to_grasp.speed":0.01347,"grasp_close.grasp_duration":0.19097,"lift_object.lift_distance":0.19757,"lift_object.speed":0.03048,"release_object.release_duration":0.08961,"retract_from_goal.retract_distance":0.23567,"retract_from_goal.retract_speed":0.06771,"transport_to_goal.arc_height":0.06092,"transport_to_goal.transport_height":0.17816,"transport_to_goal.transport_speed":0.22656},"optimized_scores":{"best_composite_score":-0.30619,"best_fitness_score":0.67381,"best_task_score":0.42025},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":54.0,"contact_point_centroid":[0.60578,0.16397,-0.01371],"force_p95":2.35627,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.53527,"mean_force":1.38411,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.60351,0.14937,0.32823]},{"body_a":"world","body_b":"grasp_target","contact_count":1367.0,"contact_point_centroid":[0.61645,0.18422,-0.0026],"force_p95":0.16564,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.99734,"mean_force":0.12976,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.61271,0.15946,0.27166]},{"body_a":"world","body_b":"grasp_target","contact_count":92.0,"contact_point_centroid":[0.50872,0.03903,-0.00149],"force_p95":0.37887,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.43736,"mean_force":0.16885,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49821,0.03929,0.04621]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10772.0,"contact_point_centroid":[0.52435,0.04745,0.2827],"force_p95":0.11681,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28484,"mean_force":0.07605,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52095,0.06614,0.2837]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12354.0,"contact_point_centroid":[0.49548,0.01993,0.13349],"force_p95":0.0777,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25289,"mean_force":0.05361,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49578,0.03909,0.13158]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12977.0,"contact_point_centroid":[0.49586,0.05822,0.13114],"force_p95":0.07585,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25025,"mean_force":0.05169,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49579,0.03909,0.12898]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11124.0,"contact_point_centroid":[0.52566,0.08565,0.28387],"force_p95":0.12003,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24563,"mean_force":0.07385,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52181,0.06701,0.28464]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51251,0.03966,-0.00203],"force_p95":0.2253,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23376,"mean_force":0.16323,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.50049,0.03948,0.04671]},{"body_a":"world","body_b":"grasp_target","contact_count":2212.0,"contact_point_centroid":[0.51251,0.03972,-0.00194],"force_p95":0.13205,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12285,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.50219,0.04,0.23373]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4694.0,"contact_point_centroid":[0.49969,0.0202,0.04819],"force_p95":0.07888,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13303,"mean_force":0.05462,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.49933,0.03939,0.04543]},{"body_a":"world","body_b":"grasp_target","contact_count":1428.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.5061,0.04265,0.10343]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.6167,0.18472,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.61784,0.16754,0.21721]},{"body_a":"world","body_b":"grasp_target","contact_count":3596.0,"contact_point_centroid":[0.6167,0.18472,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_from_goal","phase_type":"retract","tcp_position_centroid":[0.61523,0.16647,0.34344]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4938.0,"contact_point_centroid":[0.49986,0.05857,0.04789],"force_p95":0.07731,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11373,"mean_force":0.05372,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.49933,0.03939,0.04543]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1457.0,"contact_point_centroid":[0.61313,0.15951,0.27373],"force_p95":0.01177,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01641,"mean_force":0.01063,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.61272,0.15948,0.27142]},{"body_a":"left_finger","body_b":"right_finger","contact_count":229.0,"contact_point_centroid":[0.62042,0.16837,0.21619],"force_p95":0.01087,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01254,"mean_force":0.00979,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.62007,0.16834,0.21371]}],"total_contact_groups":16},"final_pose_error":0.01978,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.6167,0.18472,0.01602],"final_tcp_position":[0.61682,0.16684,0.45249],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":2.53527,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":554.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2212.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_pre_grasp","tcp_end":[0.50778,0.04536,0.15233],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12653,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":357.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1428.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.50733,0.04008,0.05443],"tcp_start":[0.50778,0.04536,0.15233],"tcp_to_object_dist_end":0.02888,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51244,0.03946,0.02586],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21251,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.2184,"phase_name":"grasp_close","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11432.0,"raw_peak_contact_force":0.23376,"tcp_end":[0.4993,0.03939,0.0454],"tcp_start":[0.50733,0.04008,0.05443],"tcp_to_object_dist_end":0.02355,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":630.0,"n_steps_budget":1000.0,"object_pos_end":[0.5036,0.03924,0.19993],"object_pos_start":[0.51244,0.03946,0.02586],"object_to_goal_dist_end":0.19012,"object_to_goal_dist_start":0.21251,"object_z_max":0.19966,"peak_contact_force":0.0776,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":25423.0,"raw_peak_contact_force":0.43736,"subtask_id":"lift_clearance","tcp_end":[0.49623,0.03912,0.22346],"tcp_start":[0.4993,0.03939,0.0454],"tcp_to_object_dist_end":0.02465,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.60821,0.17823,-0.01037],"object_pos_start":[0.5036,0.03924,0.19993],"object_to_goal_dist_end":0.1567,"object_to_goal_dist_start":0.19012,"object_z_max":0.29566,"peak_contact_force":1.06159,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":21950.0,"raw_peak_contact_force":2.53527,"subtask_id":"transport_clearance","tcp_end":[0.6058,0.15128,0.32763],"tcp_start":[0.49623,0.03912,0.22346],"tcp_to_object_dist_end":0.33908,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":348.0,"n_steps_budget":1000.0,"object_pos_end":[0.6167,0.18472,0.01602],"object_pos_start":[0.60821,0.17823,-0.01037],"object_to_goal_dist_end":0.13004,"object_to_goal_dist_start":0.1567,"object_z_max":0.01754,"peak_contact_force":0.12263,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2824.0,"raw_peak_contact_force":0.99734,"subtask_id":"reach_goal","tcp_end":[0.62157,0.16869,0.21752],"tcp_start":[0.6058,0.15128,0.32763],"tcp_to_object_dist_end":0.2022,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.6167,0.18472,0.01602],"object_pos_start":[0.6167,0.18472,0.01602],"object_to_goal_dist_end":0.13004,"object_to_goal_dist_start":0.13004,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1029.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61657,0.16707,0.2366],"tcp_start":[0.62157,0.16869,0.21752],"tcp_to_object_dist_end":0.22129,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":899.0,"n_steps_budget":1000.0,"object_pos_end":[0.6167,0.18472,0.01602],"object_pos_start":[0.6167,0.18472,0.01602],"object_to_goal_dist_end":0.13004,"object_to_goal_dist_start":0.13004,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_from_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3596.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61682,0.16684,0.45249],"tcp_start":[0.61657,0.16707,0.2366],"tcp_to_object_dist_end":0.43684,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.82881,"average_solve_count":479.0,"average_success_count":479.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_height":0.156,"approach_above.arc_height":0.09681,"approach_above.speed":0.04731,"descend_to_goal.descend_goal_offset":0.05216,"descend_to_goal.speed":0.01808,"descend_to_grasp.descend_offset":0.02034,"descend_to_grasp.speed":0.02069,"grasp_close.grasp_duration":0.20964,"lift_object.lift_distance":0.30572,"lift_object.speed":0.04827,"release_object.release_duration":0.13174,"retract_from_goal.retract_distance":0.21389,"retract_from_goal.retract_speed":0.09908,"transport_to_goal.arc_height":0.03494,"transport_to_goal.transport_height":0.17862,"transport_to_goal.transport_speed":0.27316},"optimized_scores":{"best_composite_score":-0.4052,"best_fitness_score":0.5748,"best_task_score":0.22514},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1508.0,"contact_point_centroid":[0.52326,0.15966,-0.00309],"force_p95":0.45219,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.487,"mean_force":0.16501,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54593,0.17242,0.40644]},{"body_a":"world","body_b":"grasp_target","contact_count":82.0,"contact_point_centroid":[0.4803,0.048,-0.0014],"force_p95":0.34387,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.40154,"mean_force":0.09816,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46943,0.04804,0.04832]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18588.0,"contact_point_centroid":[0.46812,0.06694,0.18876],"force_p95":0.08033,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28618,"mean_force":0.05486,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46751,0.04785,0.18763]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5065.0,"contact_point_centroid":[0.48595,0.05554,0.3563],"force_p95":0.13689,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27324,"mean_force":0.08909,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.48364,0.07397,0.35873]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18192.0,"contact_point_centroid":[0.46749,0.02874,0.18993],"force_p95":0.08238,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25938,"mean_force":0.05621,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.4675,0.04785,0.18917]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5286.0,"contact_point_centroid":[0.48862,0.09577,0.35901],"force_p95":0.12422,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24564,"mean_force":0.08702,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.48579,0.07741,0.36172]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.4827,0.04866,-0.00204],"force_p95":0.13663,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17551,"mean_force":0.12637,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.47164,0.04828,0.04837]},{"body_a":"world","body_b":"grasp_target","contact_count":2124.0,"contact_point_centroid":[0.4827,0.04873,-0.00193],"force_p95":0.13221,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12286,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.49191,0.04342,0.25978]},{"body_a":"world","body_b":"grasp_target","contact_count":1424.0,"contact_point_centroid":[0.52327,0.1597,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.5721,0.21481,0.34894]},{"body_a":"world","body_b":"grasp_target","contact_count":1968.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47833,0.05225,0.12373]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.52327,0.1597,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.57541,0.22364,0.29102]},{"body_a":"world","body_b":"grasp_target","contact_count":2840.0,"contact_point_centroid":[0.52327,0.1597,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_from_goal","phase_type":"retract","tcp_position_centroid":[0.57424,0.22268,0.40574]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4840.0,"contact_point_centroid":[0.46975,0.02893,0.04921],"force_p95":0.06839,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09947,"mean_force":0.04497,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.47055,0.04817,0.04723]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5383.0,"contact_point_centroid":[0.47006,0.06739,0.04887],"force_p95":0.0657,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0821,"mean_force":0.04106,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.47055,0.04817,0.04723]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1532.0,"contact_point_centroid":[0.54742,0.17416,0.40897],"force_p95":0.01177,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01629,"mean_force":0.01062,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54702,0.17414,0.40669]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1512.0,"contact_point_centroid":[0.57261,0.21485,0.35117],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01288,"mean_force":0.0105,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.5721,0.21481,0.34891]}],"total_contact_groups":17},"final_pose_error":0.01996,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.52327,0.1597,0.02602],"final_tcp_position":[0.57582,0.22319,0.50469],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":81.14225,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":532.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2124.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_pre_grasp","tcp_end":[0.48119,0.05576,0.19282],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16696,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":492.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":81.14225,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1968.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.47821,0.04896,0.05529],"tcp_start":[0.48119,0.05576,0.19282],"tcp_to_object_dist_end":0.02961,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48262,0.0483,0.02582],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29042,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.13562,"phase_name":"grasp_close","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12023.0,"raw_peak_contact_force":0.17551,"tcp_end":[0.47052,0.04817,0.0472],"tcp_start":[0.47821,0.04896,0.05529],"tcp_to_object_dist_end":0.02457,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":961.0,"n_steps_budget":1000.0,"object_pos_end":[0.47283,0.04822,0.30501],"object_pos_start":[0.48262,0.0483,0.02582],"object_to_goal_dist_end":0.22377,"object_to_goal_dist_start":0.29042,"object_z_max":0.30474,"peak_contact_force":0.08594,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":36862.0,"raw_peak_contact_force":0.40154,"subtask_id":"lift_clearance","tcp_end":[0.46857,0.04795,0.33317],"tcp_start":[0.47052,0.04817,0.0472],"tcp_to_object_dist_end":0.02848,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52327,0.1597,0.02602],"object_pos_start":[0.47283,0.04822,0.30501],"object_to_goal_dist_end":0.22366,"object_to_goal_dist_start":0.22377,"object_z_max":0.35401,"peak_contact_force":0.12264,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":13391.0,"raw_peak_contact_force":2.487,"subtask_id":"transport_clearance","tcp_end":[0.56742,0.20616,0.40625],"tcp_start":[0.46857,0.04795,0.33317],"tcp_to_object_dist_end":0.3856,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":356.0,"n_steps_budget":1000.0,"object_pos_end":[0.52327,0.1597,0.02602],"object_pos_start":[0.52327,0.1597,0.02602],"object_to_goal_dist_end":0.22366,"object_to_goal_dist_start":0.22366,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2936.0,"raw_peak_contact_force":0.12264,"subtask_id":"reach_goal","tcp_end":[0.57792,0.22484,0.29067],"tcp_start":[0.56742,0.20616,0.40625],"tcp_to_object_dist_end":0.27797,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.52327,0.1597,0.02602],"object_pos_start":[0.52327,0.1597,0.02602],"object_to_goal_dist_end":0.22366,"object_to_goal_dist_start":0.22366,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1021.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57467,0.22317,0.31072],"tcp_start":[0.57792,0.22484,0.29067],"tcp_to_object_dist_end":0.29618,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":710.0,"n_steps_budget":1000.0,"object_pos_end":[0.52327,0.1597,0.02602],"object_pos_start":[0.52327,0.1597,0.02602],"object_to_goal_dist_end":0.22366,"object_to_goal_dist_start":0.22366,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"retract_from_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2840.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57582,0.22319,0.50469],"tcp_start":[0.57467,0.22317,0.31072],"tcp_to_object_dist_end":0.48571,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```