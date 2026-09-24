## Search State

- **Seed**: 6
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → descend → grasp → lift → approach → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 12 | -0.1355 | 0.30 | ✅ accepted |
| 6 | approach → descend → grasp → lift → approach → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 12 | -0.1606 | 0.25 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 12 | -0.1606 | 0.25 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 15 | -0.4428 | 0.21 | ❌ rejected |
| 3 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 14 | -0.3100 | 0.22 | ❌ rejected |

**Proposal policy**: task_score is 0.30 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.135) — your mutation base

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
- id: lift_clearance
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.15
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
    - 0.0
    tolerance: 0.02
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
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.2, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **transport_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.02
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

- **Composite score**: -0.135
- **task_score** (E): 0.304
- **fitness_score**: 0.615  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.750

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above | 1.00 | 1.00 | 0.1424 |
| descend_to_grasp | 1.00 | 1.00 | 0.1114 |
| grasp_close | 1.00 | 1.00 | 0.0117 |
| lift_object | 1.00 | 1.00 | 0.1966 |
| transport_to_goal | 1.00 | 1.00 | 0.1949 |
| release_object | 1.00 | 1.00 | 0.0213 |
| retract_up | 1.00 | 1.00 | 0.2006 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, 0.033, 0.166) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.496, 0.033, 0.166)→(0.495, 0.025, 0.055) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_close | grasp | 1.00 / step_budget | (0.495, 0.025, 0.055)→(0.487, 0.025, 0.046) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.272 | 1.00 / 43.667 | 0.165 | 0.195 |
| lift_object | lift | 1.00 / step_budget | (0.487, 0.025, 0.046)→(0.484, 0.024, 0.243) | (0.500, 0.024, 0.026)→(0.491, 0.024, 0.218) | 0.272→0.206 | 1.00 / 38.000 | 0.077 | 0.411 |
| transport_to_goal | approach | 1.00 / step_budget | (0.484, 0.024, 0.243)→(0.587, 0.182, 0.203) | (0.491, 0.024, 0.218)→(0.585, 0.182, 0.172) | 0.206→0.042 | 1.00 / 24.000 | 0.111 | 0.234 |
| release_object | release | 1.00 / step_budget | (0.587, 0.182, 0.203)→(0.582, 0.180, 0.224) | (0.585, 0.182, 0.172)→(0.575, 0.177, 0.022) | 0.042→0.189 | 1.00 / 3.333 | 0.218 | 1.661 |
| retract_up | retract | 1.00 / step_budget | (0.582, 0.180, 0.224)→(0.597, 0.195, 0.423) | (0.575, 0.177, 0.022)→(0.567, 0.181, 0.026) | 0.189→0.186 | 1.00 / 4.000 | 0.123 | 0.217 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.437
- phase_score: 0.648
- phase_breakdown.approach_pre_grasp_score: 0.511
- phase_breakdown.reach_goal_score: 0.673
- phase_breakdown.reach_grasp_score: 0.731
- phase_breakdown.lift_clearance_score: 0.714
- grasp_place_fitness: 0.681

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.681
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.437
- **Median Q (composite search score)**: -0.162
- **K-run variance**: 0.0023
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.343


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.21552,"average_solve_count":348.0,"average_success_count":348.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_height":0.12417,"approach_above.arc_height":0.05187,"approach_above.speed":0.04912,"descend_to_grasp.descend_offset":0.02079,"descend_to_grasp.speed":0.03225,"grasp_close.grasp_duration":0.14539,"lift_object.lift_distance":0.22603,"lift_object.speed":0.03195,"release_object.release_duration":0.15142,"retract_up.retract_height":0.09143,"retract_up.speed":0.05301,"transport_to_goal.transport_speed":0.15658},"optimized_scores":{"best_composite_score":-0.17587,"best_fitness_score":0.57413,"best_task_score":0.22362},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":158.0,"contact_point_centroid":[0.5583,0.17228,-0.00863],"force_p95":1.4017,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.95774,"mean_force":0.48351,"phase_index":5.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.57274,0.17038,0.25552]},{"body_a":"world","body_b":"grasp_target","contact_count":91.0,"contact_point_centroid":[0.5003,-0.0142,-0.00154],"force_p95":0.37245,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.39013,"mean_force":0.15415,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48973,-0.01438,0.04741]},{"body_a":"world","body_b":"grasp_target","contact_count":2423.0,"contact_point_centroid":[0.55652,0.1755,-0.00215],"force_p95":0.22096,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.32904,"mean_force":0.12922,"phase_index":6.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.5786,0.17848,0.3453]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":717.0,"contact_point_centroid":[0.57524,0.19065,0.2353],"force_p95":0.13108,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27735,"mean_force":0.0763,"phase_index":5.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.5756,0.17164,0.23777]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15495.0,"contact_point_centroid":[0.48724,-0.03342,0.1471],"force_p95":0.07471,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25632,"mean_force":0.04969,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48742,-0.01433,0.14592]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13402.0,"contact_point_centroid":[0.48742,0.00486,0.1473],"force_p95":0.07927,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25492,"mean_force":0.0559,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48741,-0.01433,0.14618]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9258.0,"contact_point_centroid":[0.53085,0.05619,0.24583],"force_p95":0.09163,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2243,"mean_force":0.05564,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52996,0.07524,0.2452]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":928.0,"contact_point_centroid":[0.5745,0.15308,0.23484],"force_p95":0.08899,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21323,"mean_force":0.05654,"phase_index":5.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.57563,0.17166,0.23783]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50385,-0.01558,-0.00211],"force_p95":0.15319,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21111,"mean_force":0.13075,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.49198,-0.01441,0.04767]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9152.0,"contact_point_centroid":[0.53008,0.09415,0.24518],"force_p95":0.08874,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17288,"mean_force":0.05607,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52989,0.07512,0.24518]},{"body_a":"world","body_b":"grasp_target","contact_count":2620.0,"contact_point_centroid":[0.50382,-0.01567,-0.00194],"force_p95":0.13005,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12281,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.49887,0.0246,0.22223]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4336.0,"contact_point_centroid":[0.4914,0.0048,0.04803],"force_p95":0.07551,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12951,"mean_force":0.04951,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.49084,-0.01439,0.04643]},{"body_a":"world","body_b":"grasp_target","contact_count":1360.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.49796,-0.01056,0.10369]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4971.0,"contact_point_centroid":[0.49136,-0.03356,0.04797],"force_p95":0.07174,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0739,"mean_force":0.04429,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.49084,-0.01439,0.04644]}],"total_contact_groups":14},"final_pose_error":0.01986,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.55513,0.17563,0.02602],"final_tcp_position":[0.58559,0.18592,0.41979],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":1.95774,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":656.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2620.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_pre_grasp","tcp_end":[0.4998,-0.00682,0.1522],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12656,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":340.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1360.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.4988,-0.01446,0.05513],"tcp_start":[0.4998,-0.00682,0.1522],"tcp_to_object_dist_end":0.02957,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50377,-0.01478,0.0256],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31196,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.15034,"phase_name":"grasp_close","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11107.0,"raw_peak_contact_force":0.21111,"tcp_end":[0.49081,-0.01439,0.0464],"tcp_start":[0.4988,-0.01446,0.05513],"tcp_to_object_dist_end":0.02451,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":717.0,"n_steps_budget":1000.0,"object_pos_end":[0.49454,-0.0145,0.22741],"object_pos_start":[0.50377,-0.01478,0.0256],"object_to_goal_dist_end":0.22303,"object_to_goal_dist_start":0.31196,"object_z_max":0.22714,"peak_contact_force":0.07741,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":28988.0,"raw_peak_contact_force":0.39013,"subtask_id":"lift_clearance","tcp_end":[0.48802,-0.01434,0.25284],"tcp_start":[0.49081,-0.01439,0.0464],"tcp_to_object_dist_end":0.02626,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":509.0,"n_steps_budget":1000.0,"object_pos_end":[0.57734,0.17135,0.20997],"object_pos_start":[0.49454,-0.0145,0.22741],"object_to_goal_dist_end":0.04249,"object_to_goal_dist_start":0.22303,"object_z_max":0.22762,"peak_contact_force":0.11444,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":18410.0,"raw_peak_contact_force":0.2243,"subtask_id":"reach_goal","tcp_end":[0.57717,0.17146,0.24132],"tcp_start":[0.48802,-0.01434,0.25284],"tcp_to_object_dist_end":0.03135,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56963,0.16632,0.0182],"object_pos_start":[0.57734,0.17135,0.20997],"object_to_goal_dist_end":0.23153,"object_to_goal_dist_start":0.04249,"object_z_max":0.20997,"peak_contact_force":0.33847,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1803.0,"raw_peak_contact_force":1.95774,"tcp_end":[0.5727,0.17038,0.2624],"tcp_start":[0.57717,0.17146,0.24132],"tcp_to_object_dist_end":0.24426,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":651.0,"n_steps_budget":1000.0,"object_pos_end":[0.55513,0.17563,0.02602],"object_pos_start":[0.56963,0.16632,0.0182],"object_to_goal_dist_end":0.22467,"object_to_goal_dist_start":0.23153,"object_z_max":0.02956,"peak_contact_force":0.12263,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2423.0,"raw_peak_contact_force":0.32904,"tcp_end":[0.58559,0.18592,0.41979],"tcp_start":[0.5727,0.17038,0.2624],"tcp_to_object_dist_end":0.39509,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.84709,"average_solve_count":412.0,"average_success_count":412.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_height":0.15136,"approach_above.arc_height":0.05636,"approach_above.speed":0.02397,"descend_to_grasp.descend_offset":0.0206,"descend_to_grasp.speed":0.01844,"grasp_close.grasp_duration":0.11546,"lift_object.lift_distance":0.15017,"lift_object.speed":0.04291,"release_object.release_duration":0.11173,"retract_up.retract_height":0.16363,"retract_up.speed":0.05948,"transport_to_goal.transport_speed":0.13878},"optimized_scores":{"best_composite_score":-0.06854,"best_fitness_score":0.68146,"best_task_score":0.43691},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":304.0,"contact_point_centroid":[0.59675,0.15539,-0.0043],"force_p95":0.69412,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.23359,"mean_force":0.22243,"phase_index":5.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.60651,0.15875,0.14861]},{"body_a":"world","body_b":"grasp_target","contact_count":86.0,"contact_point_centroid":[0.50898,0.03935,-0.00144],"force_p95":0.41088,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.43737,"mean_force":0.15944,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.4984,0.03946,0.04707]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":785.0,"contact_point_centroid":[0.61014,0.17873,0.13233],"force_p95":0.12449,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31809,"mean_force":0.07052,"phase_index":5.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.61085,0.16019,0.13594]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":648.0,"contact_point_centroid":[0.6088,0.14136,0.13338],"force_p95":0.11933,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29393,"mean_force":0.07926,"phase_index":5.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.6109,0.16021,0.13604]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9204.0,"contact_point_centroid":[0.49593,0.05841,0.11128],"force_p95":0.07795,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28948,"mean_force":0.05399,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49585,0.03924,0.10897]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9320.0,"contact_point_centroid":[0.49557,0.02011,0.10933],"force_p95":0.07955,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24917,"mean_force":0.05357,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49588,0.03925,0.10789]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51251,0.03975,-0.00203],"force_p95":0.21807,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2192,"mean_force":0.16227,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.50061,0.03965,0.0474]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7484.0,"contact_point_centroid":[0.5483,0.07563,0.15839],"force_p95":0.10428,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20554,"mean_force":0.06125,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54866,0.09474,0.15793]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8157.0,"contact_point_centroid":[0.54974,0.11485,0.15785],"force_p95":0.09432,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17741,"mean_force":0.05628,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5498,0.09593,0.15758]},{"body_a":"world","body_b":"grasp_target","contact_count":2828.0,"contact_point_centroid":[0.51251,0.03972,-0.00195],"force_p95":0.12892,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1228,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.5012,0.04928,0.25683]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.59646,0.15529,-0.00199],"force_p95":0.12323,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13511,"mean_force":0.1226,"phase_index":6.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.61442,0.16464,0.27245]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50639,0.04433,0.11857]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4868.0,"contact_point_centroid":[0.50041,0.05872,0.04937],"force_p95":0.07498,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11854,"mean_force":0.0536,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.49946,0.03955,0.04612]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4613.0,"contact_point_centroid":[0.49967,0.02037,0.0477],"force_p95":0.07982,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1119,"mean_force":0.05597,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.49946,0.03955,0.04612]}],"total_contact_groups":14},"final_pose_error":0.02319,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.59646,0.15529,0.02602],"final_tcp_position":[0.62544,0.17122,0.3856],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1.23359,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":708.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2828.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_pre_grasp","tcp_end":[0.50813,0.04852,0.18214],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15643,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":450.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1800.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.50749,0.04025,0.05514],"tcp_start":[0.50813,0.04852,0.18214],"tcp_to_object_dist_end":0.02955,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51242,0.03966,0.02588],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21238,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.21664,"phase_name":"grasp_close","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11281.0,"raw_peak_contact_force":0.2192,"tcp_end":[0.49943,0.03955,0.04609],"tcp_start":[0.50749,0.04025,0.05514],"tcp_to_object_dist_end":0.02402,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":459.0,"n_steps_budget":1000.0,"object_pos_end":[0.50435,0.03947,0.15343],"object_pos_start":[0.51242,0.03966,0.02588],"object_to_goal_dist_end":0.18154,"object_to_goal_dist_start":0.21238,"object_z_max":0.15316,"peak_contact_force":0.07915,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":18610.0,"raw_peak_contact_force":0.43737,"subtask_id":"lift_clearance","tcp_end":[0.49595,0.03925,0.17679],"tcp_start":[0.49943,0.03955,0.04609],"tcp_to_object_dist_end":0.02482,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":454.0,"n_steps_budget":1000.0,"object_pos_end":[0.60939,0.16022,0.10909],"object_pos_start":[0.50435,0.03947,0.15343],"object_to_goal_dist_end":0.04211,"object_to_goal_dist_start":0.18154,"object_z_max":0.15371,"peak_contact_force":0.10492,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":15641.0,"raw_peak_contact_force":0.20554,"subtask_id":"reach_goal","tcp_end":[0.61291,0.16029,0.13984],"tcp_start":[0.49595,0.03925,0.17679],"tcp_to_object_dist_end":0.03095,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59635,0.15535,0.02642],"object_pos_start":[0.60939,0.16022,0.10909],"object_to_goal_dist_end":0.12384,"object_to_goal_dist_start":0.04211,"object_z_max":0.10909,"peak_contact_force":0.12828,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1737.0,"raw_peak_contact_force":1.23359,"tcp_end":[0.60641,0.15873,0.15982],"tcp_start":[0.61291,0.16029,0.13984],"tcp_to_object_dist_end":0.13382,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.59646,0.15529,0.02602],"object_pos_start":[0.59635,0.15535,0.02642],"object_to_goal_dist_end":0.12421,"object_to_goal_dist_start":0.12384,"object_z_max":0.02643,"peak_contact_force":0.12263,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.13511,"tcp_end":[0.62544,0.17122,0.3856],"tcp_start":[0.60641,0.15873,0.15982],"tcp_to_object_dist_end":0.3611,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.11842,"average_solve_count":380.0,"average_success_count":380.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_height":0.13113,"approach_above.arc_height":0.06105,"approach_above.speed":0.0357,"descend_to_grasp.descend_offset":0.02003,"descend_to_grasp.speed":0.03054,"grasp_close.grasp_duration":0.25136,"lift_object.lift_distance":0.27233,"lift_object.speed":0.05239,"release_object.release_duration":0.05431,"retract_up.retract_height":0.15426,"retract_up.speed":0.0585,"transport_to_goal.transport_speed":0.16328},"optimized_scores":{"best_composite_score":-0.16197,"best_fitness_score":0.58803,"best_task_score":0.25037},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":181.0,"contact_point_centroid":[0.55031,0.21124,-0.00767],"force_p95":1.37306,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.79039,"mean_force":0.40803,"phase_index":5.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.56555,0.2112,0.24281]},{"body_a":"world","body_b":"grasp_target","contact_count":80.0,"contact_point_centroid":[0.48023,0.0486,-0.00139],"force_p95":0.34522,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.40698,"mean_force":0.10946,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46928,0.04842,0.04778]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":721.0,"contact_point_centroid":[0.56736,0.23146,0.22111],"force_p95":0.12762,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31665,"mean_force":0.07785,"phase_index":5.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.56844,0.2127,0.22523]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16317.0,"contact_point_centroid":[0.4679,0.06733,0.17255],"force_p95":0.08053,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29325,"mean_force":0.05535,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46722,0.04821,0.17111]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":775.0,"contact_point_centroid":[0.56541,0.194,0.22212],"force_p95":0.10088,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28576,"mean_force":0.06636,"phase_index":5.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.56849,0.21274,0.22535]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7177.0,"contact_point_centroid":[0.51367,0.10261,0.2658],"force_p95":0.12078,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27363,"mean_force":0.07246,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51298,0.12176,0.26605]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8631.0,"contact_point_centroid":[0.51545,0.14405,0.26424],"force_p95":0.09714,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25748,"mean_force":0.05595,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51524,0.1254,0.26452]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16249.0,"contact_point_centroid":[0.46723,0.02911,0.1726],"force_p95":0.08077,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25677,"mean_force":0.05552,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46721,0.04821,0.17161]},{"body_a":"world","body_b":"grasp_target","contact_count":3533.0,"contact_point_centroid":[0.5496,0.2116,-0.002],"force_p95":0.12812,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18741,"mean_force":0.12224,"phase_index":6.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.57234,0.21915,0.35766]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48269,0.04868,-0.00202],"force_p95":0.12969,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15402,"mean_force":0.12472,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.47147,0.04865,0.04785]},{"body_a":"world","body_b":"grasp_target","contact_count":3004.0,"contact_point_centroid":[0.4827,0.04873,-0.00195],"force_p95":0.12823,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12279,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.49159,0.05568,0.25045]},{"body_a":"world","body_b":"grasp_target","contact_count":1544.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47769,0.05351,0.10926]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4897.0,"contact_point_centroid":[0.46962,0.02931,0.049],"force_p95":0.06737,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08229,"mean_force":0.04457,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.47038,0.04854,0.04671]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5315.0,"contact_point_centroid":[0.46999,0.06776,0.04871],"force_p95":0.06445,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08149,"mean_force":0.04138,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.47038,0.04854,0.04671]}],"total_contact_groups":14},"final_pose_error":0.01999,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.54943,0.21179,0.02602],"final_tcp_position":[0.58127,0.22767,0.4648],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":1.79039,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":752.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3004.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_pre_grasp","tcp_end":[0.48001,0.05784,0.16396],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13827,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":386.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1544.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.47804,0.04934,0.05476],"tcp_start":[0.48001,0.05784,0.16396],"tcp_to_object_dist_end":0.02913,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48261,0.04857,0.02589],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29019,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12922,"phase_name":"grasp_close","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12012.0,"raw_peak_contact_force":0.15402,"tcp_end":[0.47035,0.04854,0.04668],"tcp_start":[0.47804,0.04934,0.05476],"tcp_to_object_dist_end":0.02413,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":847.0,"n_steps_budget":1000.0,"object_pos_end":[0.47344,0.04843,0.27242],"object_pos_start":[0.48261,0.04857,0.02589],"object_to_goal_dist_end":0.21464,"object_to_goal_dist_start":0.29019,"object_z_max":0.27215,"peak_contact_force":0.07543,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":32646.0,"raw_peak_contact_force":0.40698,"subtask_id":"lift_clearance","tcp_end":[0.46806,0.04829,0.29939],"tcp_start":[0.47035,0.04854,0.04668],"tcp_to_object_dist_end":0.0275,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":468.0,"n_steps_budget":1000.0,"object_pos_end":[0.56718,0.21309,0.19581],"object_pos_start":[0.47344,0.04843,0.27242],"object_to_goal_dist_end":0.04082,"object_to_goal_dist_start":0.21464,"object_z_max":0.27263,"peak_contact_force":0.11215,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":15808.0,"raw_peak_contact_force":0.27363,"subtask_id":"reach_goal","tcp_end":[0.57011,0.21276,0.22921],"tcp_start":[0.46806,0.04829,0.29939],"tcp_to_object_dist_end":0.03353,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5586,0.20854,0.02104],"object_pos_start":[0.56718,0.21309,0.19581],"object_to_goal_dist_end":0.21171,"object_to_goal_dist_start":0.04082,"object_z_max":0.19581,"peak_contact_force":0.18844,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1677.0,"raw_peak_contact_force":1.79039,"tcp_end":[0.56552,0.2112,0.24994],"tcp_start":[0.57011,0.21276,0.22921],"tcp_to_object_dist_end":0.22902,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":891.0,"n_steps_budget":1000.0,"object_pos_end":[0.54943,0.21179,0.02602],"object_pos_start":[0.5586,0.20854,0.02104],"object_to_goal_dist_end":0.20772,"object_to_goal_dist_start":0.21171,"object_z_max":0.02704,"peak_contact_force":0.12263,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3533.0,"raw_peak_contact_force":0.18741,"tcp_end":[0.58127,0.22767,0.4648],"tcp_start":[0.56552,0.2112,0.24994],"tcp_to_object_dist_end":0.44022,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```