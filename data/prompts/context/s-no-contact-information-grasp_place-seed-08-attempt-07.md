## Search State

- **Seed**: 8
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → descend → grasp → lift → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 8 | -0.2248 | 0.27 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.1449 | 0.46 | ✅ accepted |
| 5 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | 0.1348 | 0.22 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | 0.1369 | 0.23 | ✅ accepted |
| 3 | pull → insert → descend → contact → release | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | impedance_control | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | contact_detected | force_exceeded | time_limit | 5 | 0.0851 | 0.15 | ❌ rejected |

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
- Frozen realised-scene SHA-256: `f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c`
- Frozen object start: [0.48269722766055606, 0.048727684333792556, 0.03]
- Frozen task target: [0.5818710838485517, 0.2288548935820029, 0.2304844767544324]
- Goal object position: (0.5818710838485517, 0.2288548935820029, 0.2304844767544324)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5818710838485517, 0.2288548935820029, 0.2304844767544324)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.48269722766055606, 0.048727684333792556, 0.03)
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
  frozen_object_start: [0.4827, 0.0487, 0.03]
  frozen_task_target: [0.5819, 0.2289, 0.2305]
  frozen_object_starts: {'grasp_target': [0.48269722766055606, 0.048727684333792556, 0.03]}
  frozen_targets: {'place_target': [0.5818710838485517, 0.2288548935820029, 0.2304844767544324]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c

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
| `object` | offset from object initial position (0.48269722766055606, 0.048727684333792556, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5818710838485517, 0.2288548935820029, 0.2304844767544324) | final destination targets |
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

## Current Skill (Q=-0.225) — your mutation base

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
  - 0.05
  weight: 0.3
- id: place_at_goal
  target_entity: object
  metric: goal_progress
  weight: 0.7
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_object
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
    - 0.02
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_depth:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_object
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
  subtask_id: reach_object
- id: lift_1
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
    - 0.1
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
- id: transport_1
  type: approach
  generator: arc_cartesian
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
    arc_height:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.05
      binds_to:
      - path: generator.arc_height
        mode: replace
    transport_speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: place_at_goal
- id: place_1
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
    - 0.03
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    place_depth:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
    place_speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: place_at_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.02], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_depth: status=consumed; consumers=target.offset.z (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none
- **lift_1** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
- **transport_1** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **place_1** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.03], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_depth: status=consumed; consumers=target.offset.z (replace)
    - place_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: -0.225
- **task_score** (E): 0.267
- **fitness_score**: 0.355  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.580

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_1 | 1.00 | 0.1587 |
| descend_1 | 1.00 | 0.1010 |
| grasp_1 | 1.00 | 0.0125 |
| pull_1 | 1.00 | 0.0204 |
| lift_1 | 1.00 | 0.0943 |
| transport_1 | 1.00 | 0.2628 |
| place_1 | 1.00 | 0.0548 |
| release_1 | 1.00 | 0.0192 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.516, -0.001, 0.148) | (0.522, -0.001, 0.030)→(0.522, -0.001, 0.026) | 0.287→0.289 |
| descend_1 | descend | 1.00 / step_budget | (0.516, -0.001, 0.148)→(0.516, -0.001, 0.047) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 |
| grasp_1 | grasp | 1.00 / step_budget | (0.516, -0.001, 0.047)→(0.508, -0.001, 0.037) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 |
| pull_1 | lift | 1.00 / step_budget | (0.508, -0.001, 0.037)→(0.505, -0.001, 0.057) | (0.522, -0.001, 0.026)→(0.518, -0.001, 0.046) | 0.289→0.278 |
| lift_1 | lift | 1.00 / step_budget | (0.505, -0.001, 0.057)→(0.501, -0.001, 0.151) | (0.518, -0.001, 0.046)→(0.518, -0.001, 0.136) | 0.278→0.238 |
| transport_1 | approach | 1.00 / step_budget | (0.501, -0.001, 0.151)→(0.598, 0.191, 0.299) | (0.518, -0.001, 0.136)→(0.603, 0.166, 0.104) | 0.238→0.112 |
| place_1 | descend | 1.00 / step_budget | (0.598, 0.191, 0.299)→(0.603, 0.201, 0.245) | (0.603, 0.166, 0.104)→(0.609, 0.174, 0.015) | 0.112→0.199 |
| release_1 | release | 1.00 / step_budget | (0.603, 0.201, 0.245)→(0.599, 0.199, 0.264) | (0.609, 0.174, 0.015)→(0.609, 0.173, 0.016) | 0.199→0.199 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: None
- terminal_score: 0.288
- phase_score: 0.121
- phase_breakdown.reach_object_score: 0.404
- phase_breakdown.place_at_goal_score: 0.000
- grasp_place_fitness: 0.365

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.365
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.288
- **Median Q (composite search score)**: -0.220
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.401


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `2cbd02033d1f1347f2ac2d0b012406a96501e6b48f5b172bd88b34d6c745630c`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `5745d7c2d025a63f908a4bf0f58182445bb06541d436718f39304ac5569d60c0`; realized-scene SHA-256: `f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.4827,0.04873,0.03]},{"name":"goal","value":[0.58187,0.22885,0.23048]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.4827,0.04873,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58187,0.22885,0.23048]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.36752,"average_solve_count":234.0,"average_success_count":234.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.13316,"descend_1.descend_depth":0.01236,"lift_1.lift_height":0.10272,"place_1.place_depth":0.0297,"place_1.place_speed":0.12243,"pull_1.pull_height":0.05872,"transport_1.arc_height":0.0777,"transport_1.transport_speed":0.02134},"optimized_scores":{"best_composite_score":-0.23957,"best_fitness_score":0.34043,"best_task_score":0.23812},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":269.0,"contact_point_centroid":[0.59274,0.24418,-0.00794],"force_p95":1.47272,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.41601,"mean_force":0.36888,"phase_index":6.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.57393,0.21871,0.29652]},{"body_a":"world","body_b":"grasp_target","contact_count":84.0,"contact_point_centroid":[0.47987,0.04655,-0.00152],"force_p95":0.44547,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.51007,"mean_force":0.12659,"phase_index":3.0,"phase_name":"pull_1","phase_type":"lift","tcp_position_centroid":[0.46943,0.04655,0.04047]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2811.0,"contact_point_centroid":[0.46748,0.06557,0.05928],"force_p95":0.08887,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30856,"mean_force":0.055,"phase_index":3.0,"phase_name":"pull_1","phase_type":"lift","tcp_position_centroid":[0.46758,0.04637,0.0573]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2585.0,"contact_point_centroid":[0.4677,0.02716,0.05933],"force_p95":0.08795,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26243,"mean_force":0.05759,"phase_index":3.0,"phase_name":"pull_1","phase_type":"lift","tcp_position_centroid":[0.46762,0.04637,0.05672]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9144.0,"contact_point_centroid":[0.49022,0.0638,0.26026],"force_p95":0.14635,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24388,"mean_force":0.09085,"phase_index":5.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.4847,0.08223,0.25993]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48276,0.04853,-0.00218],"force_p95":0.17146,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24212,"mean_force":0.13566,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47166,0.04679,0.04016]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9213.0,"contact_point_centroid":[0.49235,0.10397,0.26389],"force_p95":0.13122,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20639,"mean_force":0.0899,"phase_index":5.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.48688,0.08553,0.26376]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4209.0,"contact_point_centroid":[0.46599,0.0649,0.11595],"force_p95":0.10652,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15639,"mean_force":0.06483,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4637,0.04597,0.11416]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3935.0,"contact_point_centroid":[0.4661,0.02703,0.1184],"force_p95":0.10529,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14741,"mean_force":0.0679,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46365,0.04597,0.11622]},{"body_a":"world","body_b":"grasp_target","contact_count":1164.0,"contact_point_centroid":[0.4827,0.04873,-0.00189],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12305,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49072,0.02004,0.22554]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.59273,0.24361,-0.00191],"force_p95":0.13142,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13402,"mean_force":0.12115,"phase_index":7.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57346,0.22115,0.27745]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5030.0,"contact_point_centroid":[0.47029,0.02742,0.04171],"force_p95":0.07131,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1281,"mean_force":0.04304,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47056,0.04668,0.03903]},{"body_a":"world","body_b":"grasp_target","contact_count":1288.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47889,0.04438,0.09714]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5563.0,"contact_point_centroid":[0.47011,0.06603,0.04111],"force_p95":0.07144,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07473,"mean_force":0.04079,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47056,0.04668,0.03903]},{"body_a":"left_finger","body_b":"right_finger","contact_count":175.0,"contact_point_centroid":[0.5755,0.2201,0.2914],"force_p95":0.01553,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01642,"mean_force":0.01198,"phase_index":6.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.57481,0.22007,0.28913]},{"body_a":"left_finger","body_b":"right_finger","contact_count":224.0,"contact_point_centroid":[0.57532,0.22204,0.27576],"force_p95":0.01092,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01097,"mean_force":0.01,"phase_index":7.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57499,0.222,0.27322]}],"total_contact_groups":16},"final_pose_error":0.01952,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.59273,0.24362,0.01602],"final_tcp_position":[0.5763,0.22236,0.27773],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"phases":[{"n_steps":292.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_object","tcp_end":[0.48201,0.04159,0.14862],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12281,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":322.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_object","tcp_end":[0.47833,0.04743,0.04707],"tcp_start":[0.48201,0.04159,0.14862],"tcp_to_object_dist_end":0.02154,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48266,0.0472,0.02538],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29139,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","subtask_id":"reach_object","tcp_end":[0.47053,0.04668,0.039],"tcp_start":[0.47833,0.04743,0.04707],"tcp_to_object_dist_end":0.01824,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":132.0,"n_steps_budget":600.0,"object_pos_end":[0.4798,0.04657,0.06414],"object_pos_start":[0.48266,0.0472,0.02538],"object_to_goal_dist_end":0.26706,"object_to_goal_dist_start":0.29139,"object_z_max":0.06385,"phase_name":"pull_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","tcp_end":[0.46665,0.04628,0.07835],"tcp_start":[0.47053,0.04668,0.039],"tcp_to_object_dist_end":0.01936,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":256.0,"n_steps_budget":660.0,"object_pos_end":[0.47933,0.0463,0.14399],"object_pos_start":[0.4798,0.04657,0.06414],"object_to_goal_dist_end":0.22654,"object_to_goal_dist_start":0.26706,"object_z_max":0.14371,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","tcp_end":[0.46321,0.04593,0.16158],"tcp_start":[0.46665,0.04628,0.07835],"tcp_to_object_dist_end":0.02386,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":981.0,"n_steps_budget":1000.0,"object_pos_end":[0.5853,0.224,0.13129],"object_pos_start":[0.47933,0.0463,0.14399],"object_to_goal_dist_end":0.09937,"object_to_goal_dist_start":0.22654,"object_z_max":0.30542,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"place_at_goal","tcp_end":[0.57056,0.21286,0.32777],"tcp_start":[0.46321,0.04593,0.16158],"tcp_to_object_dist_end":0.19735,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":95.0,"n_steps_budget":1000.0,"object_pos_end":[0.59279,0.2426,0.01678],"object_pos_start":[0.5853,0.224,0.13129],"object_to_goal_dist_end":0.21443,"object_to_goal_dist_start":0.09937,"object_z_max":0.13129,"phase_name":"place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"place_at_goal","tcp_end":[0.5763,0.22236,0.27773],"tcp_start":[0.57056,0.21286,0.32777],"tcp_to_object_dist_end":0.26225,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59273,0.24362,0.01602],"object_pos_start":[0.59279,0.2426,0.01678],"object_to_goal_dist_end":0.21525,"object_to_goal_dist_start":0.21443,"object_z_max":0.01716,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","tcp_end":[0.57263,0.22065,0.29724],"tcp_start":[0.5763,0.22236,0.27773],"tcp_to_object_dist_end":0.28287,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `2b35d39beba75b46a5edd8e67b975c00ef2c88fb75a3753bdd32db5918adf9e2`; realized-scene SHA-256: `0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53702,-0.02132,0.03]},{"name":"goal","value":[0.61031,0.22775,0.20741]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.53702,-0.02132,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.61031,0.22775,0.20741]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.38819,"average_solve_count":237.0,"average_success_count":237.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.0928,"descend_1.descend_depth":0.01173,"lift_1.lift_height":0.12018,"place_1.place_depth":0.02384,"place_1.place_speed":0.15983,"pull_1.pull_height":0.03896,"transport_1.arc_height":0.03622,"transport_1.transport_speed":0.05736},"optimized_scores":{"best_composite_score":-0.22011,"best_fitness_score":0.35989,"best_task_score":0.27457},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":196.0,"contact_point_centroid":[0.62574,0.20002,-0.0091],"force_p95":1.46423,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.02327,"mean_force":0.45841,"phase_index":6.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.60473,0.21844,0.26354]},{"body_a":"world","body_b":"grasp_target","contact_count":90.0,"contact_point_centroid":[0.53256,-0.02039,-0.00147],"force_p95":0.45485,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.47573,"mean_force":0.18212,"phase_index":3.0,"phase_name":"pull_1","phase_type":"lift","tcp_position_centroid":[0.52162,-0.02067,0.03689]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1598.0,"contact_point_centroid":[0.52012,-0.00143,0.04718],"force_p95":0.14966,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27893,"mean_force":0.06108,"phase_index":3.0,"phase_name":"pull_1","phase_type":"lift","tcp_position_centroid":[0.52014,-0.02065,0.04441]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1696.0,"contact_point_centroid":[0.52001,-0.03979,0.04651],"force_p95":0.14853,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26519,"mean_force":0.05916,"phase_index":3.0,"phase_name":"pull_1","phase_type":"lift","tcp_position_centroid":[0.52017,-0.02065,0.0443]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8844.0,"contact_point_centroid":[0.55064,0.08281,0.23237],"force_p95":0.15233,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24181,"mean_force":0.09564,"phase_index":5.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54509,0.06431,0.2318]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10049.0,"contact_point_centroid":[0.55204,0.04965,0.23351],"force_p95":0.12106,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20286,"mean_force":0.08556,"phase_index":5.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.5465,0.06792,0.23339]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53704,-0.02116,-0.00206],"force_p95":0.14024,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18219,"mean_force":0.12743,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.524,-0.02072,0.03733]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5169.0,"contact_point_centroid":[0.51742,-0.00151,0.10268],"force_p95":0.10507,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13994,"mean_force":0.06584,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51544,-0.02054,0.1002]},{"body_a":"world","body_b":"grasp_target","contact_count":1220.0,"contact_point_centroid":[0.53702,-0.02132,-0.00189],"force_p95":0.13606,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12303,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51328,-0.00883,0.2249]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5729.0,"contact_point_centroid":[0.5175,-0.03944,0.10117],"force_p95":0.10037,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13715,"mean_force":0.06081,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51545,-0.02054,0.09953]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.62579,0.2009,-0.00196],"force_p95":0.13235,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13509,"mean_force":0.11638,"phase_index":7.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60244,0.21987,0.24813]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4101.0,"contact_point_centroid":[0.5237,-0.00149,0.03865],"force_p95":0.07768,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12846,"mean_force":0.05184,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52278,-0.02069,0.03593]},{"body_a":"world","body_b":"grasp_target","contact_count":1252.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52863,-0.01954,0.09578]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4912.0,"contact_point_centroid":[0.52369,-0.03978,0.03773],"force_p95":0.0698,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08316,"mean_force":0.0447,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52278,-0.02069,0.03593]},{"body_a":"left_finger","body_b":"right_finger","contact_count":71.0,"contact_point_centroid":[0.60643,0.22022,0.25663],"force_p95":0.01613,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01637,"mean_force":0.01305,"phase_index":6.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.60541,0.2202,0.25406]},{"body_a":"left_finger","body_b":"right_finger","contact_count":220.0,"contact_point_centroid":[0.60472,0.22079,0.24682],"force_p95":0.01171,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01183,"mean_force":0.01039,"phase_index":7.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60423,0.22077,0.24438]}],"total_contact_groups":16},"final_pose_error":0.01979,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.62579,0.20091,0.01602],"final_tcp_position":[0.60577,0.22113,0.24934],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"phases":[{"n_steps":306.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_object","tcp_end":[0.52872,-0.0183,0.14755],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12185,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":313.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_object","tcp_end":[0.53124,-0.02084,0.04577],"tcp_start":[0.52872,-0.0183,0.14755],"tcp_to_object_dist_end":0.02059,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53692,-0.02066,0.02578],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31636,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","subtask_id":"reach_object","tcp_end":[0.52275,-0.02069,0.03589],"tcp_start":[0.53124,-0.02084,0.04577],"tcp_to_object_dist_end":0.01741,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":78.0,"n_steps_budget":600.0,"object_pos_end":[0.5319,-0.02069,0.04541],"object_pos_start":[0.53692,-0.02066,0.02578],"object_to_goal_dist_end":0.30679,"object_to_goal_dist_start":0.31636,"object_z_max":0.04514,"phase_name":"pull_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","tcp_end":[0.51897,-0.02062,0.05528],"tcp_start":[0.52275,-0.02069,0.03589],"tcp_to_object_dist_end":0.01627,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":330.0,"n_steps_budget":780.0,"object_pos_end":[0.53172,-0.02039,0.14144],"object_pos_start":[0.5319,-0.02069,0.04541],"object_to_goal_dist_end":0.26852,"object_to_goal_dist_start":0.30679,"object_z_max":0.14118,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","tcp_end":[0.51516,-0.02053,0.15584],"tcp_start":[0.51897,-0.02062,0.05528],"tcp_to_object_dist_end":0.02195,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":995.0,"n_steps_budget":1000.0,"object_pos_end":[0.6166,0.20028,0.16518],"object_pos_start":[0.53172,-0.02039,0.14144],"object_to_goal_dist_end":0.05077,"object_to_goal_dist_start":0.26852,"object_z_max":0.26764,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"place_at_goal","tcp_end":[0.60287,0.21227,0.29739],"tcp_start":[0.51516,-0.02053,0.15584],"tcp_to_object_dist_end":0.13346,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":90.0,"n_steps_budget":1000.0,"object_pos_end":[0.62591,0.20458,0.01194],"object_pos_start":[0.6166,0.20028,0.16518],"object_to_goal_dist_end":0.19746,"object_to_goal_dist_start":0.05077,"object_z_max":0.16518,"phase_name":"place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"place_at_goal","tcp_end":[0.60577,0.22113,0.24934],"tcp_start":[0.60287,0.21227,0.29739],"tcp_to_object_dist_end":0.23883,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.62579,0.20091,0.01602],"object_pos_start":[0.62591,0.20458,0.01194],"object_to_goal_dist_end":0.19388,"object_to_goal_dist_start":0.19746,"object_z_max":0.01711,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","tcp_end":[0.60144,0.21934,0.26758],"tcp_start":[0.60577,0.22113,0.24934],"tcp_to_object_dist_end":0.2534,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `530652a2467d9ac78fab654e7ed7fc5283ca1649270bc8f158e04c16074f9f95`; realized-scene SHA-256: `9bdc6de22965641ffcaccb8421100561fe91fb98e16735236cc25272572d8879`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5456,-0.02923,0.03]},{"name":"goal","value":[0.63284,0.16493,0.17692]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5456,-0.02923,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63284,0.16493,0.17692]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.475,"average_solve_count":240.0,"average_success_count":240.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.07114,"descend_1.descend_depth":0.01349,"lift_1.lift_height":0.11808,"place_1.place_depth":0.01442,"place_1.place_speed":0.19281,"pull_1.pull_height":0.01833,"transport_1.arc_height":0.06147,"transport_1.transport_speed":0.05309},"optimized_scores":{"best_composite_score":-0.21474,"best_fitness_score":0.36526,"best_task_score":0.28842},"replay_outcomes":[{"contacts":{"omitted_contact_groups":3,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":689.0,"contact_point_centroid":[0.60824,0.07364,-0.00394],"force_p95":0.84603,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.23327,"mean_force":0.20491,"phase_index":5.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.60714,0.12227,0.27543]},{"body_a":"world","body_b":"grasp_target","contact_count":56.0,"contact_point_centroid":[0.53738,-0.02788,-0.00102],"force_p95":0.59792,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.82367,"mean_force":0.15789,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52822,-0.02822,0.03874]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5628.0,"contact_point_centroid":[0.52743,-0.04701,0.08236],"force_p95":0.1032,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37116,"mean_force":0.06338,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52528,-0.02812,0.08062]},{"body_a":"world","body_b":"grasp_target","contact_count":80.0,"contact_point_centroid":[0.54527,-0.02866,-0.00208],"force_p95":0.3511,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.36826,"mean_force":0.24215,"phase_index":3.0,"phase_name":"pull_1","phase_type":"lift","tcp_position_centroid":[0.53019,-0.02828,0.03695]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5063.0,"contact_point_centroid":[0.5274,-0.00909,0.08388],"force_p95":0.10872,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3386,"mean_force":0.06854,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52527,-0.02812,0.08129]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6106.0,"contact_point_centroid":[0.54538,0.02196,0.20381],"force_p95":0.15642,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22919,"mean_force":0.09745,"phase_index":5.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.5397,0.00344,0.2032]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":404.0,"contact_point_centroid":[0.53094,-0.0473,0.03884],"force_p95":0.16603,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21426,"mean_force":0.10064,"phase_index":3.0,"phase_name":"pull_1","phase_type":"lift","tcp_position_centroid":[0.53018,-0.02828,0.03696]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":344.0,"contact_point_centroid":[0.53102,-0.00911,0.03971],"force_p95":0.16815,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2104,"mean_force":0.10651,"phase_index":3.0,"phase_name":"pull_1","phase_type":"lift","tcp_position_centroid":[0.53018,-0.02828,0.03696]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54563,-0.02905,-0.00208],"force_p95":0.14696,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20546,"mean_force":0.12917,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53227,-0.02834,0.03861]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6914.0,"contact_point_centroid":[0.54686,-0.01211,0.20591],"force_p95":0.12465,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16872,"mean_force":0.08788,"phase_index":5.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54126,0.00617,0.20598]},{"body_a":"world","body_b":"grasp_target","contact_count":1280.0,"contact_point_centroid":[0.5456,-0.02923,-0.0019],"force_p95":0.13566,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12301,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51673,-0.01217,0.22432]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4093.0,"contact_point_centroid":[0.53208,-0.0091,0.03988],"force_p95":0.07881,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13559,"mean_force":0.05184,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53104,-0.02831,0.03716]},{"body_a":"world","body_b":"grasp_target","contact_count":456.0,"contact_point_centroid":[0.60825,0.07389,-0.00199],"force_p95":0.12273,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12285,"mean_force":0.12261,"phase_index":6.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.6241,0.15376,0.2421]},{"body_a":"world","body_b":"grasp_target","contact_count":1216.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53646,-0.02683,0.09611]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.60825,0.07389,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62278,0.15802,0.20774]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4942.0,"contact_point_centroid":[0.53204,-0.04741,0.03894],"force_p95":0.07102,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08005,"mean_force":0.04464,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53104,-0.02831,0.03717]}],"total_contact_groups":19},"final_pose_error":0.01959,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.60825,0.07389,0.01602],"final_tcp_position":[0.62692,0.15908,0.20908],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"phases":[{"n_steps":321.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_object","tcp_end":[0.53606,-0.02519,0.14673],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12115,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":304.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_object","tcp_end":[0.53958,-0.02855,0.04733],"tcp_start":[0.53606,-0.02519,0.14673],"tcp_to_object_dist_end":0.02215,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54551,-0.02835,0.02571],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26048,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","subtask_id":"reach_object","tcp_end":[0.53101,-0.0283,0.03713],"tcp_start":[0.53958,-0.02855,0.04733],"tcp_to_object_dist_end":0.01846,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.54281,-0.0283,0.02702],"object_pos_start":[0.54551,-0.02835,0.02571],"object_to_goal_dist_end":0.26061,"object_to_goal_dist_start":0.26048,"object_z_max":0.0268,"phase_name":"pull_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","tcp_end":[0.52904,-0.02825,0.03764],"tcp_start":[0.53101,-0.0283,0.03713],"tcp_to_object_dist_end":0.01738,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":328.0,"n_steps_budget":750.0,"object_pos_end":[0.54192,-0.02803,0.12145],"object_pos_start":[0.54281,-0.0283,0.02702],"object_to_goal_dist_end":0.2204,"object_to_goal_dist_start":0.26061,"object_z_max":0.1212,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","tcp_end":[0.52504,-0.0281,0.13639],"tcp_start":[0.52904,-0.02825,0.03764],"tcp_to_object_dist_end":0.02255,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":914.0,"n_steps_budget":1000.0,"object_pos_end":[0.60825,0.0739,0.01601],"object_pos_start":[0.54192,-0.02803,0.12145],"object_to_goal_dist_end":0.1865,"object_to_goal_dist_start":0.2204,"object_z_max":0.24014,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"place_at_goal","tcp_end":[0.62206,0.14876,0.27231],"tcp_start":[0.52504,-0.0281,0.13639],"tcp_to_object_dist_end":0.26736,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":114.0,"n_steps_budget":1000.0,"object_pos_end":[0.60825,0.07389,0.01602],"object_pos_start":[0.60825,0.0739,0.01601],"object_to_goal_dist_end":0.1865,"object_to_goal_dist_start":0.1865,"object_z_max":0.01602,"phase_name":"place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"place_at_goal","tcp_end":[0.62692,0.15908,0.20908],"tcp_start":[0.62206,0.14876,0.27231],"tcp_to_object_dist_end":0.21184,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60825,0.07389,0.01602],"object_pos_start":[0.60825,0.07389,0.01602],"object_to_goal_dist_end":0.1865,"object_to_goal_dist_start":0.1865,"object_z_max":0.01602,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","tcp_end":[0.62145,0.15757,0.22717],"tcp_start":[0.62692,0.15908,0.20908],"tcp_to_object_dist_end":0.22751,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```