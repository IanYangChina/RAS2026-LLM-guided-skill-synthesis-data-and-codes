## Search State

- **Seed**: 6
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | impedance_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 16 | -0.3747 | 0.29 | ❌ rejected |
| 13 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 16 | -0.3716 | 0.29 | ❌ rejected |
| 12 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 16 | -0.3830 | 0.27 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 16 | -0.3662 | 0.30 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 12 | -0.1459 | 0.28 | ❌ rejected |

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

## Current Skill (Q=-0.375) — your mutation base

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

- **Composite score**: -0.375
- **task_score** (E): 0.286
- **fitness_score**: 0.605  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.980

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above | 1.00 | 1.00 | 0.1465 |
| descend_to_grasp | 1.00 | 1.00 | 0.1069 |
| grasp_close | 1.00 | 1.00 | 0.0117 |
| lift_object | 1.00 | 1.00 | 0.2455 |
| transport_to_goal | 0.00 | 1.00 | 0.1179 |
| descend_to_place | 1.00 | 1.00 | 0.1597 |
| release_object | 1.00 | 1.00 | 0.0209 |
| retract_from_goal | 1.00 | 1.00 | 0.2010 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, 0.033, 0.162) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.496, 0.033, 0.162)→(0.495, 0.025, 0.055) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_close | grasp | 1.00 / step_budget | (0.495, 0.025, 0.055)→(0.487, 0.025, 0.047) | (0.500, 0.024, 0.026)→(0.500, 0.025, 0.026) | 0.271→0.271 | 1.00 / 43.333 | 0.167 | 0.198 |
| lift_object | lift | 1.00 / step_budget | (0.487, 0.025, 0.047)→(0.484, 0.024, 0.292) | (0.500, 0.025, 0.026)→(0.490, 0.024, 0.265) | 0.271→0.219 | 1.00 / 39.000 | 0.079 | 0.418 |
| transport_to_goal | approach | 0.00 / step_budget | (0.484, 0.024, 0.292)→(0.544, 0.114, 0.338) | (0.490, 0.024, 0.265)→(0.548, 0.113, 0.303) | 0.219→0.141 | 1.00 / 16.333 | 0.132 | 0.193 |
| descend_to_place | descend | 1.00 / step_budget | (0.544, 0.114, 0.338)→(0.592, 0.190, 0.212) | (0.548, 0.113, 0.303)→(0.570, 0.167, 0.019) | 0.141→0.196 | 1.00 / 8.333 | 91003.405 | 2.231 |
| release_object | release | 1.00 / step_budget | (0.592, 0.190, 0.212)→(0.587, 0.188, 0.232) | (0.570, 0.167, 0.019)→(0.570, 0.167, 0.019) | 0.196→0.196 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract_from_goal | retract | 1.00 / step_budget | (0.587, 0.188, 0.232)→(0.587, 0.188, 0.433) | (0.570, 0.167, 0.019)→(0.570, 0.167, 0.019) | 0.196→0.196 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.420
- phase_score: 0.580
- phase_breakdown.approach_pre_grasp_score: 0.709
- phase_breakdown.reach_goal_score: 0.674
- phase_breakdown.reach_grasp_score: 0.737
- phase_breakdown.lift_clearance_score: 0.106
- grasp_place_fitness: 0.672

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.672
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.420
- **Median Q (composite search score)**: -0.400
- **K-run variance**: 0.0023
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.315


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.98054,"average_solve_count":411.0,"average_success_count":411.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_height":0.13622,"approach_above.arc_height":0.08621,"approach_above.speed":0.07479,"descend_to_grasp.descend_offset":0.02067,"descend_to_grasp.speed":0.02449,"descend_to_place.place_offset":0.01491,"descend_to_place.speed":0.02276,"grasp_close.grasp_duration":0.23897,"lift_object.lift_distance":0.25685,"lift_object.speed":0.05926,"release_object.release_duration":0.12367,"retract_from_goal.retract_distance":0.21705,"retract_from_goal.speed":0.14165,"transport_to_goal.arc_height":0.04279,"transport_to_goal.transport_offset_z":0.07021,"transport_to_goal.transport_speed":0.0685},"optimized_scores":{"best_composite_score":-0.41605,"best_fitness_score":0.56395,"best_task_score":0.20283},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1673.0,"contact_point_centroid":[0.55198,0.1038,-0.00296],"force_p95":0.35323,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32962,"mean_force":0.16844,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.56724,0.15278,0.27838]},{"body_a":"world","body_b":"grasp_target","contact_count":84.0,"contact_point_centroid":[0.50143,-0.01436,-0.00145],"force_p95":0.35098,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.41532,"mean_force":0.11349,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48981,-0.01451,0.04758]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1240.0,"contact_point_centroid":[0.54068,0.10864,0.31881],"force_p95":0.15469,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31944,"mean_force":0.12547,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.53671,0.09066,0.32338]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16436.0,"contact_point_centroid":[0.48822,-0.03354,0.16278],"force_p95":0.08032,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27906,"mean_force":0.05334,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48761,-0.01447,0.1615]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14835.0,"contact_point_centroid":[0.48814,0.00468,0.16485],"force_p95":0.08211,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27882,"mean_force":0.05786,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48761,-0.01446,0.16363]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50384,-0.01558,-0.0021],"force_p95":0.14999,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20382,"mean_force":0.12988,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.49207,-0.01454,0.0476]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1475.0,"contact_point_centroid":[0.54134,0.07414,0.31768],"force_p95":0.13367,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17382,"mean_force":0.1065,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.53724,0.09182,0.32243]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12191.0,"contact_point_centroid":[0.50628,0.04154,0.30817],"force_p95":0.12872,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14922,"mean_force":0.07824,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50444,0.02276,0.3099]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4340.0,"contact_point_centroid":[0.49145,0.00467,0.04802],"force_p95":0.07535,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14367,"mean_force":0.04947,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.49093,-0.01452,0.04636]},{"body_a":"world","body_b":"grasp_target","contact_count":2412.0,"contact_point_centroid":[0.50382,-0.01567,-0.00194],"force_p95":0.13067,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12283,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.49902,0.02499,0.22753]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14681.0,"contact_point_centroid":[0.50566,0.00432,0.30868],"force_p95":0.1105,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13796,"mean_force":0.06428,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50443,0.02277,0.31002]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.55153,0.10567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12265,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.57811,0.17943,0.2603]},{"body_a":"world","body_b":"grasp_target","contact_count":1552.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.49799,-0.01074,0.10919]},{"body_a":"world","body_b":"grasp_target","contact_count":2668.0,"contact_point_centroid":[0.55153,0.10567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_from_goal","phase_type":"retract","tcp_position_centroid":[0.5763,0.1785,0.37732]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4954.0,"contact_point_centroid":[0.49143,-0.03368,0.04793],"force_p95":0.07117,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0734,"mean_force":0.0444,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.49093,-0.01452,0.04636]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1793.0,"contact_point_centroid":[0.568,0.15352,0.2801],"force_p95":0.01179,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01642,"mean_force":0.0106,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.56761,0.15351,0.27787]}],"total_contact_groups":17},"final_pose_error":0.01998,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.55153,0.10567,0.02602],"final_tcp_position":[0.57769,0.17884,0.47717],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":2.32962,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":604.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2412.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_pre_grasp","tcp_end":[0.49991,-0.00707,0.16327],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13757,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":388.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1552.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.49884,-0.0146,0.05504],"tcp_start":[0.49991,-0.00707,0.16327],"tcp_to_object_dist_end":0.02946,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50376,-0.01486,0.02565],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31198,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.14747,"phase_name":"grasp_close","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11094.0,"raw_peak_contact_force":0.20382,"tcp_end":[0.4909,-0.01452,0.04633],"tcp_start":[0.49884,-0.0146,0.05504],"tcp_to_object_dist_end":0.02436,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":811.0,"n_steps_budget":1000.0,"object_pos_end":[0.49425,-0.01469,0.2567],"object_pos_start":[0.50376,-0.01486,0.02565],"object_to_goal_dist_end":0.22253,"object_to_goal_dist_start":0.31198,"object_z_max":0.25643,"peak_contact_force":0.07642,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":31355.0,"raw_peak_contact_force":0.41532,"subtask_id":"lift_clearance","tcp_end":[0.48842,-0.01448,0.28336],"tcp_start":[0.4909,-0.01452,0.04633],"tcp_to_object_dist_end":0.02729,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53592,0.07797,0.30128],"object_pos_start":[0.49425,-0.01469,0.2567],"object_to_goal_dist_end":0.13195,"object_to_goal_dist_start":0.22253,"object_z_max":0.30128,"peak_contact_force":0.12611,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":26872.0,"raw_peak_contact_force":0.14922,"subtask_id":"reach_goal","tcp_end":[0.53202,0.07874,0.33619],"tcp_start":[0.48842,-0.01448,0.28336],"tcp_to_object_dist_end":0.03513,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":747.0,"n_steps_budget":1000.0,"object_pos_end":[0.55153,0.10567,0.02602],"object_pos_start":[0.53592,0.07797,0.30128],"object_to_goal_dist_end":0.23931,"object_to_goal_dist_start":0.13195,"object_z_max":0.30128,"peak_contact_force":0.12265,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":6181.0,"raw_peak_contact_force":2.32962,"subtask_id":"reach_goal","tcp_end":[0.58107,0.18034,0.25927],"tcp_start":[0.53202,0.07874,0.33619],"tcp_to_object_dist_end":0.24669,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.55153,0.10567,0.02602],"object_pos_start":[0.55153,0.10567,0.02602],"object_to_goal_dist_end":0.23931,"object_to_goal_dist_start":0.23931,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1021.0,"raw_peak_contact_force":0.12265,"tcp_end":[0.5771,0.17898,0.28009],"tcp_start":[0.58107,0.18034,0.25927],"tcp_to_object_dist_end":0.26567,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":667.0,"n_steps_budget":960.0,"object_pos_end":[0.55153,0.10567,0.02602],"object_pos_start":[0.55153,0.10567,0.02602],"object_to_goal_dist_end":0.23931,"object_to_goal_dist_start":0.23931,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"retract_from_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2668.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57769,0.17884,0.47717],"tcp_start":[0.5771,0.17898,0.28009],"tcp_to_object_dist_end":0.4578,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.13991,"average_solve_count":436.0,"average_success_count":436.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_height":0.10433,"approach_above.arc_height":0.06399,"approach_above.speed":0.06452,"descend_to_grasp.descend_offset":0.02143,"descend_to_grasp.speed":0.02278,"descend_to_place.place_offset":0.01435,"descend_to_place.speed":0.0284,"grasp_close.grasp_duration":0.32314,"lift_object.lift_distance":0.26395,"lift_object.speed":0.04279,"release_object.release_duration":0.16274,"retract_from_goal.retract_distance":0.21263,"retract_from_goal.speed":0.14779,"transport_to_goal.arc_height":0.05432,"transport_to_goal.transport_offset_z":0.12107,"transport_to_goal.transport_speed":0.06999},"optimized_scores":{"best_composite_score":-0.30792,"best_fitness_score":0.67208,"best_task_score":0.4199},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":775.0,"contact_point_centroid":[0.61161,0.17853,-0.00354],"force_p95":0.70254,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.82548,"mean_force":0.18646,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61165,0.15927,0.18585]},{"body_a":"world","body_b":"grasp_target","contact_count":85.0,"contact_point_centroid":[0.50875,0.04002,-0.00144],"force_p95":0.40077,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.43386,"mean_force":0.15197,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.4982,0.03988,0.0477]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16572.0,"contact_point_centroid":[0.49634,0.0588,0.16781],"force_p95":0.07785,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27756,"mean_force":0.05443,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49592,0.03968,0.16639]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16533.0,"contact_point_centroid":[0.49574,0.02058,0.16746],"force_p95":0.0797,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25018,"mean_force":0.05465,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49594,0.03969,0.16646]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3052.0,"contact_point_centroid":[0.5862,0.11036,0.27164],"force_p95":0.13391,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24541,"mean_force":0.10337,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.5816,0.12869,0.27648]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3355.0,"contact_point_centroid":[0.58636,0.14686,0.27153],"force_p95":0.11868,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23213,"mean_force":0.0935,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.58169,0.12877,0.27631]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51251,0.03976,-0.00203],"force_p95":0.22152,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22328,"mean_force":0.16219,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.5004,0.04007,0.048]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11597.0,"contact_point_centroid":[0.52478,0.0489,0.30995],"force_p95":0.13283,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20554,"mean_force":0.08035,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52224,0.06745,0.3117]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12094.0,"contact_point_centroid":[0.52646,0.08711,0.31039],"force_p95":0.12205,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19352,"mean_force":0.07704,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5234,0.06862,0.31216]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4360.0,"contact_point_centroid":[0.49992,0.05916,0.04838],"force_p95":0.08344,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14243,"mean_force":0.05963,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.49925,0.03997,0.04671]},{"body_a":"world","body_b":"grasp_target","contact_count":3100.0,"contact_point_centroid":[0.51251,0.03972,-0.00195],"force_p95":0.12782,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12278,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.50184,0.05644,0.23158]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.61143,0.17874,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.61514,0.16605,0.1623]},{"body_a":"world","body_b":"grasp_target","contact_count":1156.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50627,0.04449,0.09594]},{"body_a":"world","body_b":"grasp_target","contact_count":2768.0,"contact_point_centroid":[0.61143,0.17874,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_from_goal","phase_type":"retract","tcp_position_centroid":[0.61146,0.16474,0.2773]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4882.0,"contact_point_centroid":[0.49985,0.02085,0.04821],"force_p95":0.07543,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11601,"mean_force":0.05273,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.49925,0.03997,0.04672]},{"body_a":"left_finger","body_b":"right_finger","contact_count":569.0,"contact_point_centroid":[0.6146,0.16175,0.18077],"force_p95":0.01306,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01649,"mean_force":0.01098,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61409,0.16173,0.17865]}],"total_contact_groups":17},"final_pose_error":0.01998,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.61143,0.17874,0.01602],"final_tcp_position":[0.61266,0.16498,0.37443],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1.82548,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":776.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3100.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_pre_grasp","tcp_end":[0.50797,0.04835,0.13583],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11024,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":289.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1156.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.50727,0.04068,0.05573],"tcp_start":[0.50797,0.04835,0.13583],"tcp_to_object_dist_end":0.03018,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51242,0.03996,0.02587],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.2122,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.22104,"phase_name":"grasp_close","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11042.0,"raw_peak_contact_force":0.22328,"tcp_end":[0.49922,0.03997,0.04668],"tcp_start":[0.50727,0.04068,0.05573],"tcp_to_object_dist_end":0.02464,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":855.0,"n_steps_budget":1000.0,"object_pos_end":[0.50202,0.03983,0.26432],"object_pos_start":[0.51242,0.03996,0.02587],"object_to_goal_dist_end":0.21817,"object_to_goal_dist_start":0.2122,"object_z_max":0.26405,"peak_contact_force":0.07565,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":33190.0,"raw_peak_contact_force":0.43386,"subtask_id":"lift_clearance","tcp_end":[0.49681,0.03975,0.29102],"tcp_start":[0.49922,0.03997,0.04668],"tcp_to_object_dist_end":0.02721,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.57411,0.11485,0.28808],"object_pos_start":[0.50202,0.03983,0.26432],"object_to_goal_dist_end":0.16324,"object_to_goal_dist_start":0.21817,"object_z_max":0.29247,"peak_contact_force":0.13494,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":23691.0,"raw_peak_contact_force":0.20554,"subtask_id":"reach_goal","tcp_end":[0.5694,0.11506,0.32381],"tcp_start":[0.49681,0.03975,0.29102],"tcp_to_object_dist_end":0.03604,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":629.0,"n_steps_budget":1000.0,"object_pos_end":[0.61143,0.17874,0.01602],"object_pos_start":[0.57411,0.11485,0.28808],"object_to_goal_dist_end":0.13016,"object_to_goal_dist_start":0.16324,"object_z_max":0.28808,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7751.0,"raw_peak_contact_force":1.82548,"subtask_id":"reach_goal","tcp_end":[0.61961,0.1673,0.16234],"tcp_start":[0.5694,0.11506,0.32381],"tcp_to_object_dist_end":0.14699,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61143,0.17874,0.01602],"object_pos_start":[0.61143,0.17874,0.01602],"object_to_goal_dist_end":0.13016,"object_to_goal_dist_start":0.13016,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1026.0,"raw_peak_contact_force":0.12264,"tcp_end":[0.6135,0.16549,0.18175],"tcp_start":[0.61961,0.1673,0.16234],"tcp_to_object_dist_end":0.16627,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":692.0,"n_steps_budget":900.0,"object_pos_end":[0.61143,0.17874,0.01602],"object_pos_start":[0.61143,0.17874,0.01602],"object_to_goal_dist_end":0.13016,"object_to_goal_dist_start":0.13016,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_from_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2768.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61266,0.16498,0.37443],"tcp_start":[0.6135,0.16549,0.18175],"tcp_to_object_dist_end":0.35867,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.9977,"average_solve_count":435.0,"average_success_count":435.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_height":0.15332,"approach_above.arc_height":0.05849,"approach_above.speed":0.09531,"descend_to_grasp.descend_offset":0.02022,"descend_to_grasp.speed":0.02759,"descend_to_place.place_offset":-0.01836,"descend_to_place.speed":0.0252,"grasp_close.grasp_duration":0.14797,"lift_object.lift_distance":0.27484,"lift_object.speed":0.03367,"release_object.release_duration":0.13785,"retract_from_goal.retract_distance":0.23299,"retract_from_goal.speed":0.12397,"transport_to_goal.arc_height":0.02258,"transport_to_goal.transport_offset_z":0.13737,"transport_to_goal.transport_speed":0.11501},"optimized_scores":{"best_composite_score":-0.40014,"best_fitness_score":0.57986,"best_task_score":0.23457},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1731.0,"contact_point_centroid":[0.54657,0.21498,-0.00283],"force_p95":0.41968,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.53743,"mean_force":0.17146,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.55907,0.1965,0.2598]},{"body_a":"world","body_b":"grasp_target","contact_count":82.0,"contact_point_centroid":[0.47904,0.04803,-0.00141],"force_p95":0.38395,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.40385,"mean_force":0.15094,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46949,0.04828,0.04802]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":404.0,"contact_point_centroid":[0.53458,0.13208,0.34332],"force_p95":0.19822,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29092,"mean_force":0.13214,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.53068,0.15014,0.34839]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17988.0,"contact_point_centroid":[0.46717,0.0671,0.17745],"force_p95":0.0761,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28691,"mean_force":0.05154,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46735,0.04806,0.17657]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15536.0,"contact_point_centroid":[0.46636,0.02887,0.17936],"force_p95":0.08383,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24636,"mean_force":0.05778,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46736,0.04806,0.17813]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":569.0,"contact_point_centroid":[0.53531,0.16824,0.34133],"force_p95":0.13625,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23446,"mean_force":0.09425,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.53102,0.15081,0.34663]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12209.0,"contact_point_centroid":[0.49484,0.10769,0.32522],"force_p95":0.12346,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22373,"mean_force":0.07724,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.49215,0.08909,0.32683]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12219.0,"contact_point_centroid":[0.49427,0.07057,0.32503],"force_p95":0.1236,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21345,"mean_force":0.07776,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.49219,0.08915,0.32691]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.4827,0.04868,-0.00203],"force_p95":0.13288,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1663,"mean_force":0.12547,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.47157,0.0485,0.04809]},{"body_a":"world","body_b":"grasp_target","contact_count":2352.0,"contact_point_centroid":[0.4827,0.04873,-0.00194],"force_p95":0.13103,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12283,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.49242,0.05277,0.26207]},{"body_a":"world","body_b":"grasp_target","contact_count":1892.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47797,0.05344,0.12056]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.54741,0.21771,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.57155,0.22047,0.21485]},{"body_a":"world","body_b":"grasp_target","contact_count":3052.0,"contact_point_centroid":[0.54741,0.21771,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_from_goal","phase_type":"retract","tcp_position_centroid":[0.56903,0.2191,0.33999]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4924.0,"contact_point_centroid":[0.46968,0.02915,0.04899],"force_p95":0.06759,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08841,"mean_force":0.04434,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.47047,0.04839,0.04695]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5293.0,"contact_point_centroid":[0.47005,0.06761,0.04886],"force_p95":0.06515,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08201,"mean_force":0.04157,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.47048,0.04839,0.04696]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1871.0,"contact_point_centroid":[0.5596,0.19663,0.26193],"force_p95":0.01134,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01654,"mean_force":0.01059,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.55913,0.1966,0.25962]}],"total_contact_groups":17},"final_pose_error":0.0198,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.54741,0.21771,0.01602],"final_tcp_position":[0.57048,0.21953,0.44782],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":273009.96897,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":589.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2352.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_pre_grasp","tcp_end":[0.48055,0.05788,0.18655],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16081,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":473.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1892.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.47814,0.04918,0.05501],"tcp_start":[0.48055,0.05788,0.18655],"tcp_to_object_dist_end":0.02935,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48262,0.04849,0.02586],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29027,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.13229,"phase_name":"grasp_close","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12017.0,"raw_peak_contact_force":0.1663,"tcp_end":[0.47045,0.04839,0.04692],"tcp_start":[0.47814,0.04918,0.05501],"tcp_to_object_dist_end":0.02433,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":859.0,"n_steps_budget":1000.0,"object_pos_end":[0.4726,0.04806,0.27525],"object_pos_start":[0.48262,0.04849,0.02586],"object_to_goal_dist_end":0.21594,"object_to_goal_dist_start":0.29027,"object_z_max":0.27497,"peak_contact_force":0.08464,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":33606.0,"raw_peak_contact_force":0.40385,"subtask_id":"lift_clearance","tcp_end":[0.46818,0.04814,0.30204],"tcp_start":[0.47045,0.04839,0.04692],"tcp_to_object_dist_end":0.02715,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":15.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53341,0.1476,0.31832],"object_pos_start":[0.4726,0.04806,0.27525],"object_to_goal_dist_end":0.12909,"object_to_goal_dist_start":0.21594,"object_z_max":0.31832,"peak_contact_force":0.13495,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":24428.0,"raw_peak_contact_force":0.22373,"subtask_id":"reach_goal","tcp_end":[0.52963,0.14781,0.35493],"tcp_start":[0.46818,0.04814,0.30204],"tcp_to_object_dist_end":0.03681,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":644.0,"n_steps_budget":1000.0,"object_pos_end":[0.54741,0.21771,0.01602],"object_pos_start":[0.53341,0.1476,0.31832],"object_to_goal_dist_end":0.2175,"object_to_goal_dist_start":0.12909,"object_z_max":0.31832,"peak_contact_force":273009.96897,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4575.0,"raw_peak_contact_force":2.53743,"subtask_id":"reach_goal","tcp_end":[0.57511,0.22187,0.21412],"tcp_start":[0.52963,0.14781,0.35493],"tcp_to_object_dist_end":0.20007,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54741,0.21771,0.01602],"object_pos_start":[0.54741,0.21771,0.01602],"object_to_goal_dist_end":0.2175,"object_to_goal_dist_start":0.2175,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1025.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57031,0.21986,0.23463],"tcp_start":[0.57511,0.22187,0.21412],"tcp_to_object_dist_end":0.21982,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":763.0,"n_steps_budget":1000.0,"object_pos_end":[0.54741,0.21771,0.01602],"object_pos_start":[0.54741,0.21771,0.01602],"object_to_goal_dist_end":0.2175,"object_to_goal_dist_start":0.2175,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_from_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3052.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57048,0.21953,0.44782],"tcp_start":[0.57031,0.21986,0.23463],"tcp_to_object_dist_end":0.43242,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```