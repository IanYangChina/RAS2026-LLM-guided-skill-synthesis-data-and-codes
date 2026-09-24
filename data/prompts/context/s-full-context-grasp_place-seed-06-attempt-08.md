## Search State

- **Seed**: 6
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → descend → grasp → lift → approach | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 9 | 0.2855 | 0.73 | ✅ accepted |
| 7 | approach → descend → grasp → lift → approach → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 12 | -0.1355 | 0.30 | ✅ accepted |
| 6 | approach → descend → grasp → lift → approach → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 12 | -0.1606 | 0.25 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 12 | -0.1606 | 0.25 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 15 | -0.4428 | 0.21 | ❌ rejected |

**Proposal policy**: task_score is 0.73 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.726, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.286) — your mutation base

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

- **Composite score**: 0.286
- **task_score** (E): 0.726
- **fitness_score**: 0.826  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.540

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above | 1.00 | 1.00 | 0.1487 |
| descend_to_grasp | 1.00 | 1.00 | 0.1038 |
| grasp_close | 1.00 | 1.00 | 0.0117 |
| lift_object | 1.00 | 1.00 | 0.2240 |
| transport_to_goal | 0.67 | 0.67 | 0.1726 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, 0.031, 0.158) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.496, 0.031, 0.158)→(0.495, 0.025, 0.055) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 | 1.00 / 4.000 | 16.032 | 0.123 |
| grasp_close | grasp | 1.00 / step_budget | (0.495, 0.025, 0.055)→(0.487, 0.024, 0.046) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.272 | 1.00 / 44.333 | 0.171 | 0.206 |
| lift_object | lift | 1.00 / step_budget | (0.487, 0.024, 0.046)→(0.484, 0.024, 0.270) | (0.500, 0.024, 0.026)→(0.490, 0.024, 0.244) | 0.272→0.216 | 1.00 / 38.000 | 0.077 | 0.428 |
| transport_to_goal | approach | 0.67 / step_budget | (0.484, 0.024, 0.270)→(0.573, 0.160, 0.237) | (0.490, 0.024, 0.244)→(0.572, 0.162, 0.194) | 0.216→0.049 | 0.67 / 13.000 | 3253.481 | 0.289 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.790
- phase_score: 0.528
- phase_breakdown.approach_pre_grasp_score: 0.757
- phase_breakdown.reach_goal_score: 0.549
- phase_breakdown.reach_grasp_score: 0.728
- phase_breakdown.lift_clearance_score: 0.055
- grasp_place_fitness: 0.858

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.858
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.790
- **Median Q (composite search score)**: 0.309
- **K-run variance**: 0.0015
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.310


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.86973,"average_solve_count":261.0,"average_success_count":261.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_height":0.13113,"approach_above.arc_height":0.05186,"approach_above.speed":0.05052,"descend_to_grasp.descend_offset":0.0202,"descend_to_grasp.speed":0.02033,"grasp_close.grasp_duration":0.18192,"lift_object.lift_distance":0.20493,"lift_object.speed":0.05998,"transport_to_goal.transport_speed":0.17463},"optimized_scores":{"best_composite_score":0.23031,"best_fitness_score":0.77031,"best_task_score":0.61489},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":85.0,"contact_point_centroid":[0.50121,-0.01418,-0.00147],"force_p95":0.35992,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.43071,"mean_force":0.11267,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48977,-0.01445,0.04728]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11872.0,"contact_point_centroid":[0.4878,0.00474,0.13931],"force_p95":0.08206,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27926,"mean_force":0.05706,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48743,-0.01441,0.13804]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12748.0,"contact_point_centroid":[0.4881,-0.03349,0.13584],"force_p95":0.08185,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27437,"mean_force":0.05396,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48744,-0.01441,0.13411]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14243.0,"contact_point_centroid":[0.51873,0.0311,0.24142],"force_p95":0.13085,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23593,"mean_force":0.06914,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5167,0.04989,0.24225]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50385,-0.01558,-0.00211],"force_p95":0.15302,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20731,"mean_force":0.13066,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.49204,-0.01448,0.04726]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14804.0,"contact_point_centroid":[0.51841,0.06997,0.24135],"force_p95":0.10583,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18502,"mean_force":0.06549,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51737,0.05127,0.24258]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4340.0,"contact_point_centroid":[0.49144,0.0048,0.04776],"force_p95":0.07603,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14869,"mean_force":0.04974,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.4909,-0.01446,0.04603]},{"body_a":"world","body_b":"grasp_target","contact_count":2556.0,"contact_point_centroid":[0.50382,-0.01567,-0.00194],"force_p95":0.13017,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12282,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.4989,0.0244,0.22539]},{"body_a":"world","body_b":"grasp_target","contact_count":1524.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.49793,-0.01066,0.10683]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5452.0,"contact_point_centroid":[0.49198,-0.0336,0.04842],"force_p95":0.06771,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.06956,"mean_force":0.04056,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.4909,-0.01446,0.04603]}],"total_contact_groups":10},"final_pose_error":0.07304,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.55544,0.12653,0.22322],"final_tcp_position":[0.55439,0.12602,0.26067],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":9760.30694,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":640.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2556.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_pre_grasp","tcp_end":[0.49986,-0.00698,0.15867],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.133,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":381.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1524.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.49881,-0.01454,0.0547],"tcp_start":[0.49986,-0.00698,0.15867],"tcp_to_object_dist_end":0.02913,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50376,-0.01476,0.02561],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31195,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.15106,"phase_name":"grasp_close","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11592.0,"raw_peak_contact_force":0.20731,"tcp_end":[0.49087,-0.01446,0.046],"tcp_start":[0.49881,-0.01454,0.0547],"tcp_to_object_dist_end":0.02413,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":633.0,"n_steps_budget":1000.0,"object_pos_end":[0.49518,-0.01475,0.20605],"object_pos_start":[0.50376,-0.01476,0.02561],"object_to_goal_dist_end":0.22599,"object_to_goal_dist_start":0.31195,"object_z_max":0.20578,"peak_contact_force":0.07697,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":24705.0,"raw_peak_contact_force":0.43071,"subtask_id":"lift_clearance","tcp_end":[0.4879,-0.01441,0.23136],"tcp_start":[0.49087,-0.01446,0.046],"tcp_to_object_dist_end":0.02634,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":17.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55544,0.12653,0.22322],"object_pos_start":[0.49518,-0.01475,0.20605],"object_to_goal_dist_end":0.07295,"object_to_goal_dist_start":0.22599,"object_z_max":0.2238,"peak_contact_force":9760.30694,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":29047.0,"raw_peak_contact_force":0.23593,"subtask_id":"reach_goal","tcp_end":[0.55439,0.12602,0.26067],"tcp_start":[0.4879,-0.01441,0.23136],"tcp_to_object_dist_end":0.03746,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.11787,"average_solve_count":263.0,"average_success_count":263.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_height":0.11787,"approach_above.arc_height":0.02224,"approach_above.speed":0.07941,"descend_to_grasp.descend_offset":0.02083,"descend_to_grasp.speed":0.02857,"grasp_close.grasp_duration":0.15694,"lift_object.lift_distance":0.22909,"lift_object.speed":0.03974,"transport_to_goal.transport_speed":0.1372},"optimized_scores":{"best_composite_score":0.30853,"best_fitness_score":0.84853,"best_task_score":0.77178},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":90.0,"contact_point_centroid":[0.50871,0.0386,-0.00149],"force_p95":0.36389,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.39923,"mean_force":0.14901,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49822,0.03888,0.04717]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14525.0,"contact_point_centroid":[0.49621,0.0578,0.14944],"force_p95":0.07867,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28065,"mean_force":0.05371,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49588,0.03868,0.14754]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16550.0,"contact_point_centroid":[0.54601,0.07365,0.21793],"force_p95":0.09665,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25828,"mean_force":0.06068,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54692,0.09274,0.2185]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14369.0,"contact_point_centroid":[0.49563,0.01956,0.14911],"force_p95":0.07908,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24109,"mean_force":0.05409,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49589,0.03868,0.14793]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18766.0,"contact_point_centroid":[0.54693,0.11244,0.21739],"force_p95":0.0849,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23254,"mean_force":0.05304,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54765,0.09351,0.21801]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51252,0.03965,-0.00207],"force_p95":0.14271,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18738,"mean_force":0.12785,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.50048,0.03907,0.04748]},{"body_a":"world","body_b":"grasp_target","contact_count":2016.0,"contact_point_centroid":[0.51251,0.03972,-0.00193],"force_p95":0.13256,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12287,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.50241,0.03145,0.23253]},{"body_a":"world","body_b":"grasp_target","contact_count":1412.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50612,0.04082,0.10551]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4391.0,"contact_point_centroid":[0.49962,0.01973,0.04797],"force_p95":0.07509,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12233,"mean_force":0.04933,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.49933,0.03898,0.04619]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5321.0,"contact_point_centroid":[0.50054,0.05811,0.04865],"force_p95":0.06693,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07589,"mean_force":0.04121,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.49933,0.03898,0.0462]}],"total_contact_groups":10},"final_pose_error":0.03611,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.59769,0.14844,0.15117],"final_tcp_position":[0.60134,0.14827,0.18528],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":0.39923,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":505.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2016.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_pre_grasp","tcp_end":[0.50775,0.04219,0.15614],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13023,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":353.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1412.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.50736,0.03966,0.05522],"tcp_start":[0.50775,0.04219,0.15614],"tcp_to_object_dist_end":0.02965,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51244,0.03918,0.02574],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21275,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.14175,"phase_name":"grasp_close","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11512.0,"raw_peak_contact_force":0.18738,"tcp_end":[0.4993,0.03897,0.04616],"tcp_start":[0.50736,0.03966,0.05522],"tcp_to_object_dist_end":0.02428,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":737.0,"n_steps_budget":1000.0,"object_pos_end":[0.50272,0.03899,0.23021],"object_pos_start":[0.51244,0.03918,0.02574],"object_to_goal_dist_end":0.20168,"object_to_goal_dist_start":0.21275,"object_z_max":0.22994,"peak_contact_force":0.07728,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":28984.0,"raw_peak_contact_force":0.39923,"subtask_id":"lift_clearance","tcp_end":[0.49653,0.03873,0.2557],"tcp_start":[0.4993,0.03897,0.04616],"tcp_to_object_dist_end":0.02623,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.59769,0.14844,0.15117],"object_pos_start":[0.50272,0.03899,0.23021],"object_to_goal_dist_end":0.03886,"object_to_goal_dist_start":0.20168,"object_z_max":0.23044,"peak_contact_force":0.13651,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":35316.0,"raw_peak_contact_force":0.25828,"subtask_id":"reach_goal","tcp_end":[0.60134,0.14827,0.18528],"tcp_start":[0.49653,0.03873,0.2557],"tcp_to_object_dist_end":0.0343,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.86667,"average_solve_count":315.0,"average_success_count":315.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_height":0.12706,"approach_above.arc_height":0.05928,"approach_above.speed":0.0669,"descend_to_grasp.descend_offset":0.02002,"descend_to_grasp.speed":0.0157,"grasp_close.grasp_duration":0.25405,"lift_object.lift_distance":0.29697,"lift_object.speed":0.0394,"transport_to_goal.transport_speed":0.14869},"optimized_scores":{"best_composite_score":0.31768,"best_fitness_score":0.85768,"best_task_score":0.78987},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":81.0,"contact_point_centroid":[0.47993,0.04842,-0.00138],"force_p95":0.39792,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.4552,"mean_force":0.1181,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46927,0.04842,0.04782]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15111.0,"contact_point_centroid":[0.51218,0.14018,0.29282],"force_p95":0.10034,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37363,"mean_force":0.06241,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51254,0.12162,0.29417]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17973.0,"contact_point_centroid":[0.46787,0.06733,0.18456],"force_p95":0.07898,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29571,"mean_force":0.05485,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46729,0.04822,0.18314]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13015.0,"contact_point_centroid":[0.50985,0.09794,0.29463],"force_p95":0.13631,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29002,"mean_force":0.07496,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50955,0.11685,0.29584]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17848.0,"contact_point_centroid":[0.46723,0.02911,0.18498],"force_p95":0.08073,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2581,"mean_force":0.05515,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46729,0.04822,0.18405]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48269,0.04872,-0.00202],"force_p95":0.22162,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22192,"mean_force":0.16318,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.47147,0.04865,0.04793]},{"body_a":"world","body_b":"grasp_target","contact_count":2704.0,"contact_point_centroid":[0.4827,0.04873,-0.00195],"force_p95":0.1295,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12281,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.4914,0.05546,0.24722]},{"body_a":"world","body_b":"grasp_target","contact_count":1584.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47766,0.05334,0.10774]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5116.0,"contact_point_centroid":[0.47006,0.06778,0.04912],"force_p95":0.07224,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10805,"mean_force":0.05172,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.47037,0.04854,0.04679]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5096.0,"contact_point_centroid":[0.46954,0.02932,0.04871],"force_p95":0.07363,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10321,"mean_force":0.05077,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.47037,0.04854,0.04679]}],"total_contact_groups":10},"final_pose_error":0.02998,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.5616,0.21071,0.20787],"final_tcp_position":[0.56454,0.20439,0.26555],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":47.85161,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":677.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2704.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_pre_grasp","tcp_end":[0.48007,0.05748,0.16054],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13483,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":396.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":47.85161,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1584.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.47802,0.04933,0.05483],"tcp_start":[0.48007,0.05748,0.16054],"tcp_to_object_dist_end":0.02919,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48261,0.04861,0.0259],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29017,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.21895,"phase_name":"grasp_close","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12012.0,"raw_peak_contact_force":0.22192,"tcp_end":[0.47034,0.04854,0.04676],"tcp_start":[0.47802,0.04933,0.05483],"tcp_to_object_dist_end":0.02421,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":931.0,"n_steps_budget":1000.0,"object_pos_end":[0.47317,0.04846,0.29671],"object_pos_start":[0.48261,0.04861,0.0259],"object_to_goal_dist_end":0.22078,"object_to_goal_dist_start":0.29017,"object_z_max":0.29643,"peak_contact_force":0.07592,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":35902.0,"raw_peak_contact_force":0.4552,"subtask_id":"lift_clearance","tcp_end":[0.4683,0.04831,0.32395],"tcp_start":[0.47034,0.04854,0.04676],"tcp_to_object_dist_end":0.02767,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5616,0.21071,0.20787],"object_pos_start":[0.47317,0.04846,0.29671],"object_to_goal_dist_end":0.03538,"object_to_goal_dist_start":0.22078,"object_z_max":0.2969,"peak_contact_force":0.0,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":28126.0,"raw_peak_contact_force":0.37363,"subtask_id":"reach_goal","tcp_end":[0.56454,0.20439,0.26555],"tcp_start":[0.4683,0.04831,0.32395],"tcp_to_object_dist_end":0.0581,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```