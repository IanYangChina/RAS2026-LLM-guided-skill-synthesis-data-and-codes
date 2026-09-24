## Search State

- **Seed**: 8
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 10 | -0.1165 | 0.28 | ✅ accepted |
| 1 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 10 | -0.0544 | 0.24 | ✅ accepted |
| 0 | pull → insert → descend → contact → release | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | impedance_control | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | contact_detected | force_exceeded | time_limit | 5 | 0.0851 | 0.15 | ✅ accepted |

**Proposal policy**: task_score is 0.28 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.117) — your mutation base

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
  weight: 0.4
- id: reach_goal
  weight: 0.6
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
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.08
      - 0.15
      default: 0.1
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
    - 0.03
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_offset_z:
      type: scalar
      range:
      - 0.0
      - 0.06
      default: 0.03
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
  subtask_id: reach_object
- id: grasp_1
  type: grasp
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
  subtask_id: reach_object
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
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.08
      - 0.12
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_object
- id: move_to_goal
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
    - 0.05
    tolerance: 0.03
    orientation:
      mode: keep_current
  parameters:
    approach_goal_height:
      type: scalar
      range:
      - 0.0
      - 0.1
      default: 0.05
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.2
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_goal
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
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    place_z_offset:
      type: scalar
      range:
      - 0.0
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.2
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
  subtask_id: reach_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.03], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_offset_z: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **lift_1** (`lift`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **move_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.05], tolerance=0.03
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_goal_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **place_1** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_z_offset: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none

## Design Metrics

- **Composite score**: -0.117
- **task_score** (E): 0.277
- **fitness_score**: 0.533  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.650

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1390 |
| descend_1 | 1.00 | 1.00 | 0.1329 |
| grasp_1 | 1.00 | 1.00 | 0.0126 |
| lift_1 | 1.00 | 1.00 | 0.0935 |
| move_to_goal | 1.00 | 1.00 | 0.2341 |
| place_1 | 1.00 | 1.00 | 0.0088 |
| release_1 | 1.00 | 1.00 | 0.0202 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.516, -0.001, 0.169) | (0.522, -0.001, 0.030)→(0.522, -0.001, 0.026) | 0.287→0.289 | 1.00 / 4.000 | 0.123 | 0.123 |
| descend_1 | descend | 1.00 / step_budget | (0.516, -0.001, 0.169)→(0.516, -0.001, 0.036) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 43.000 | 0.143 | 0.207 |
| grasp_1 | grasp | 1.00 / step_budget | (0.516, -0.001, 0.036)→(0.508, -0.001, 0.027) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 30.000 | 0.161 | 0.629 |
| lift_1 | lift | 1.00 / step_budget | (0.508, -0.001, 0.027)→(0.516, -0.001, 0.120) | (0.522, -0.001, 0.026)→(0.530, -0.001, 0.108) | 0.289→0.244 | 1.00 / 6.667 | 0.223 | 1.942 |
| move_to_goal | approach | 1.00 / step_budget | (0.516, -0.001, 0.120)→(0.598, 0.187, 0.226) | (0.530, -0.001, 0.108)→(0.595, 0.170, 0.011) | 0.244→0.199 | 1.00 / 8.333 | 94253.653 | 0.212 |
| place_1 | descend | 1.00 / step_budget | (0.598, 0.187, 0.226)→(0.600, 0.193, 0.220) | (0.595, 0.170, 0.011)→(0.594, 0.170, 0.016) | 0.199→0.194 | 1.00 / 4.000 | 0.123 | 0.133 |
| release_1 | release | 1.00 / step_budget | (0.600, 0.193, 0.220)→(0.595, 0.191, 0.240) | (0.594, 0.170, 0.016)→(0.594, 0.170, 0.016) | 0.194→0.194 | 1.00 / 4.000 | 0.123 | 0.138 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.261
- phase_score: 0.451
- phase_breakdown.reach_goal_score: 0.531
- phase_breakdown.reach_object_score: 0.330
- grasp_place_fitness: 0.608

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.608
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.333
- **Median Q (composite search score)**: -0.051
- **K-run variance**: 0.0098
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.394


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.65161,"average_solve_count":155.0,"average_success_count":155.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.13898,"approach_1.speed":0.08609,"descend_1.descend_offset_z":0.00065,"descend_1.speed":0.0725,"lift_1.lift_height":0.11313,"lift_1.speed":0.05799,"move_to_goal.approach_goal_height":0.06347,"move_to_goal.speed":0.36324,"place_1.place_z_offset":0.01199,"place_1.speed":0.13287},"optimized_scores":{"best_composite_score":-0.0512,"best_fitness_score":0.5988,"best_task_score":0.23776},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":83.0,"contact_point_centroid":[0.58357,0.20916,-0.00893],"force_p95":1.68129,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.29303,"mean_force":0.80599,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.56885,0.20808,0.26746]},{"body_a":"world","body_b":"grasp_target","contact_count":190.0,"contact_point_centroid":[0.47946,0.04565,-0.00124],"force_p95":0.4372,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62447,"mean_force":0.08717,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46885,0.04685,0.02928]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3596.0,"contact_point_centroid":[0.51052,0.11793,0.16773],"force_p95":0.14491,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32838,"mean_force":0.08136,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.50591,0.09942,0.16772]},{"body_a":"world","body_b":"grasp_target","contact_count":156.0,"contact_point_centroid":[0.58009,0.20788,-0.00579],"force_p95":0.25466,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.31979,"mean_force":0.10762,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.57267,0.21517,0.26646]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3002.0,"contact_point_centroid":[0.50776,0.07697,0.16479],"force_p95":0.17236,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31409,"mean_force":0.09285,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.5038,0.09567,0.16437]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19084.0,"contact_point_centroid":[0.47213,0.06581,0.07497],"force_p95":0.07914,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30005,"mean_force":0.0535,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47164,0.0467,0.07306]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18978.0,"contact_point_centroid":[0.47237,0.02761,0.07685],"force_p95":0.08046,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26337,"mean_force":0.05311,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47182,0.0467,0.07468]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48275,0.04842,-0.00215],"force_p95":0.16632,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25172,"mean_force":0.1345,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47134,0.04714,0.02857]},{"body_a":"world","body_b":"grasp_target","contact_count":1624.0,"contact_point_centroid":[0.4827,0.04873,-0.00192],"force_p95":0.13462,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12293,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48993,0.02101,0.23884]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.58034,0.20809,-0.00194],"force_p95":0.1246,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12507,"mean_force":0.12024,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57124,0.21731,0.25749]},{"body_a":"world","body_b":"grasp_target","contact_count":1856.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47822,0.04552,0.10562]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5005.0,"contact_point_centroid":[0.47005,0.02779,0.03046],"force_p95":0.07089,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11537,"mean_force":0.04302,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47022,0.04703,0.02744]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5532.0,"contact_point_centroid":[0.46987,0.06638,0.02981],"force_p95":0.07044,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0828,"mean_force":0.04117,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47022,0.04703,0.02745]},{"body_a":"left_finger","body_b":"right_finger","contact_count":74.0,"contact_point_centroid":[0.57412,0.2169,0.26379],"force_p95":0.0159,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01621,"mean_force":0.01302,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.57364,0.21688,0.26197]},{"body_a":"left_finger","body_b":"right_finger","contact_count":228.0,"contact_point_centroid":[0.57345,0.21826,0.25555],"force_p95":0.01152,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01191,"mean_force":0.01006,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57296,0.21823,0.2532]}],"total_contact_groups":15},"final_pose_error":0.01982,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.58034,0.20809,0.01602],"final_tcp_position":[0.5745,0.21847,0.25766],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":273012.41853,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":407.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1856.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.48109,0.04351,0.17706],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15114,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":464.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.15887,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":12337.0,"raw_peak_contact_force":0.25172,"subtask_id":"reach_object","tcp_end":[0.47811,0.04781,0.03546],"tcp_start":[0.48109,0.04351,0.17706],"tcp_to_object_dist_end":0.01054,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":33.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4826,0.0472,0.02547],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29135,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.08943,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":38252.0,"raw_peak_contact_force":0.62447,"subtask_id":"reach_object","tcp_end":[0.47019,0.04702,0.02741],"tcp_start":[0.47811,0.04781,0.03546],"tcp_to_object_dist_end":0.01256,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48949,0.04682,0.11142],"object_pos_start":[0.4826,0.0472,0.02547],"object_to_goal_dist_end":0.23632,"object_to_goal_dist_start":0.29135,"object_z_max":0.11133,"peak_contact_force":0.34961,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":6681.0,"raw_peak_contact_force":2.29303,"subtask_id":"reach_object","tcp_end":[0.47711,0.04678,0.12219],"tcp_start":[0.47019,0.04702,0.02741],"tcp_to_object_dist_end":0.01641,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":410.0,"n_steps_budget":1000.0,"object_pos_end":[0.58189,0.20938,-0.00127],"object_pos_start":[0.48949,0.04682,0.11142],"object_to_goal_dist_end":0.23257,"object_to_goal_dist_start":0.23632,"object_z_max":0.20332,"peak_contact_force":273012.41853,"phase_name":"move_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":230.0,"raw_peak_contact_force":0.31979,"subtask_id":"reach_goal","tcp_end":[0.57124,0.21234,0.27135],"tcp_start":[0.47711,0.04678,0.12219],"tcp_to_object_dist_end":0.27285,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":39.0,"n_steps_budget":1000.0,"object_pos_end":[0.58039,0.20821,0.0156],"object_pos_start":[0.58189,0.20938,-0.00127],"object_to_goal_dist_end":0.21588,"object_to_goal_dist_start":0.23257,"object_z_max":0.01545,"peak_contact_force":0.12263,"phase_name":"place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1028.0,"raw_peak_contact_force":0.12507,"subtask_id":"reach_goal","tcp_end":[0.5745,0.21847,0.25766],"tcp_start":[0.57124,0.21234,0.27135],"tcp_to_object_dist_end":0.24235,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58034,0.20809,0.01602],"object_pos_start":[0.58039,0.20821,0.0156],"object_to_goal_dist_end":0.21547,"object_to_goal_dist_start":0.21588,"object_z_max":0.01666,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1624.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_goal","tcp_end":[0.57028,0.21678,0.27733],"tcp_start":[0.5745,0.21847,0.25766],"tcp_to_object_dist_end":0.26165,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.15957,"average_solve_count":188.0,"average_success_count":188.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.13141,"approach_1.speed":0.0536,"descend_1.descend_offset_z":0.00076,"descend_1.speed":0.05375,"lift_1.lift_height":0.11812,"lift_1.speed":0.06155,"move_to_goal.approach_goal_height":0.02128,"move_to_goal.speed":0.30103,"place_1.place_z_offset":0.00962,"place_1.speed":0.29627},"optimized_scores":{"best_composite_score":-0.04185,"best_fitness_score":0.60815,"best_task_score":0.26121},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":312.0,"contact_point_centroid":[0.59164,0.16964,-0.00504],"force_p95":1.22301,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.82005,"mean_force":0.30056,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.59417,0.18343,0.20269]},{"body_a":"world","body_b":"grasp_target","contact_count":196.0,"contact_point_centroid":[0.53384,-0.02059,-0.00115],"force_p95":0.41144,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.6514,"mean_force":0.0864,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5213,-0.02082,0.02666]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16337.0,"contact_point_centroid":[0.52649,-0.00169,0.07431],"force_p95":0.09042,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30219,"mean_force":0.06225,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52457,-0.02071,0.07255]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2415.0,"contact_point_centroid":[0.54973,0.01269,0.14138],"force_p95":0.17061,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29586,"mean_force":0.09337,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.54566,0.03142,0.14237]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2939.0,"contact_point_centroid":[0.55217,0.05836,0.1444],"force_p95":0.16839,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29445,"mean_force":0.08387,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.54828,0.03999,0.1456]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17658.0,"contact_point_centroid":[0.52637,-0.03964,0.07285],"force_p95":0.08683,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28964,"mean_force":0.05831,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52445,-0.02071,0.0715]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53702,-0.02113,-0.00204],"force_p95":0.13558,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17585,"mean_force":0.12633,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52406,-0.02089,0.02646]},{"body_a":"world","body_b":"grasp_target","contact_count":1948.0,"contact_point_centroid":[0.53702,-0.02132,-0.00193],"force_p95":0.13308,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12288,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5136,-0.00944,0.23362]},{"body_a":"world","body_b":"grasp_target","contact_count":104.0,"contact_point_centroid":[0.58902,0.16895,-0.00181],"force_p95":0.13652,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13758,"mean_force":0.12384,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.60136,0.20783,0.21094]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.589,0.16891,-0.00199],"force_p95":0.12399,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12848,"mean_force":0.12283,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59865,0.21004,0.2103]},{"body_a":"world","body_b":"grasp_target","contact_count":1772.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5292,-0.02011,0.10082]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4100.0,"contact_point_centroid":[0.52373,-0.00166,0.02779],"force_p95":0.07678,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11335,"mean_force":0.05177,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52282,-0.02086,0.02506]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4904.0,"contact_point_centroid":[0.52372,-0.03995,0.02686],"force_p95":0.06886,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09265,"mean_force":0.04477,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52282,-0.02086,0.02506]},{"body_a":"left_finger","body_b":"right_finger","contact_count":129.0,"contact_point_centroid":[0.59914,0.19714,0.21048],"force_p95":0.01604,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01652,"mean_force":0.01265,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.59863,0.19713,0.20823]},{"body_a":"left_finger","body_b":"right_finger","contact_count":112.0,"contact_point_centroid":[0.60142,0.20785,0.21351],"force_p95":0.0114,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01263,"mean_force":0.01056,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.60136,0.20784,0.21094]},{"body_a":"left_finger","body_b":"right_finger","contact_count":226.0,"contact_point_centroid":[0.60111,0.21117,0.20919],"force_p95":0.0109,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01255,"mean_force":0.00988,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.6009,0.21115,0.20679]}],"total_contact_groups":16},"final_pose_error":0.01984,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.589,0.16891,0.01602],"final_tcp_position":[0.60239,0.21095,0.21007],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":9748.39343,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":488.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1772.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.52987,-0.01928,0.16807],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14224,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":443.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13257,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10804.0,"raw_peak_contact_force":0.17585,"subtask_id":"reach_object","tcp_end":[0.53142,-0.02102,0.03487],"tcp_start":[0.52987,-0.01928,0.16807],"tcp_to_object_dist_end":0.01048,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53688,-0.02074,0.02584],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.3164,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.28276,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":34191.0,"raw_peak_contact_force":0.6514,"subtask_id":"reach_object","tcp_end":[0.52279,-0.02086,0.02503],"tcp_start":[0.53142,-0.02102,0.03487],"tcp_to_object_dist_end":0.01411,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54426,-0.02059,0.11268],"object_pos_start":[0.53688,-0.02074,0.02584],"object_to_goal_dist_end":0.27388,"object_to_goal_dist_start":0.3164,"object_z_max":0.11257,"peak_contact_force":0.13766,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":5795.0,"raw_peak_contact_force":1.82005,"subtask_id":"reach_object","tcp_end":[0.53097,-0.02066,0.12495],"tcp_start":[0.52279,-0.02086,0.02503],"tcp_to_object_dist_end":0.01809,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":410.0,"n_steps_budget":1000.0,"object_pos_end":[0.58887,0.16878,0.01668],"object_pos_start":[0.54426,-0.02059,0.11268],"object_to_goal_dist_end":0.20079,"object_to_goal_dist_start":0.27388,"object_z_max":0.15069,"peak_contact_force":9748.39343,"phase_name":"move_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":216.0,"raw_peak_contact_force":0.13758,"subtask_id":"reach_goal","tcp_end":[0.60121,0.20549,0.21155],"tcp_start":[0.53097,-0.02066,0.12495],"tcp_to_object_dist_end":0.19868,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":26.0,"n_steps_budget":1000.0,"object_pos_end":[0.58889,0.16866,0.01612],"object_pos_start":[0.58887,0.16878,0.01668],"object_to_goal_dist_end":0.20135,"object_to_goal_dist_start":0.20079,"object_z_max":0.01668,"peak_contact_force":0.12263,"phase_name":"place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1026.0,"raw_peak_contact_force":0.12848,"subtask_id":"reach_goal","tcp_end":[0.60239,0.21095,0.21007],"tcp_start":[0.60121,0.20549,0.21155],"tcp_to_object_dist_end":0.19896,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.589,0.16891,0.01602],"object_pos_start":[0.58889,0.16866,0.01612],"object_to_goal_dist_end":0.20136,"object_to_goal_dist_start":0.20135,"object_z_max":0.01612,"peak_contact_force":0.12262,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1948.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_goal","tcp_end":[0.59735,0.20943,0.22974],"tcp_start":[0.60239,0.21095,0.21007],"tcp_to_object_dist_end":0.21769,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.46341,"average_solve_count":164.0,"average_success_count":164.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.12571,"approach_1.speed":0.06235,"descend_1.descend_offset_z":0.00378,"descend_1.speed":0.06334,"lift_1.lift_height":0.09773,"lift_1.speed":0.0672,"move_to_goal.approach_goal_height":0.03739,"move_to_goal.speed":0.2692,"place_1.place_z_offset":0.01103,"place_1.speed":0.30399},"optimized_scores":{"best_composite_score":-0.25653,"best_fitness_score":0.39347,"best_task_score":0.33273},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":211.0,"contact_point_centroid":[0.61762,0.12526,-0.00632],"force_p95":1.29971,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.71227,"mean_force":0.38376,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.61312,0.12831,0.18745]},{"body_a":"world","body_b":"grasp_target","contact_count":204.0,"contact_point_centroid":[0.54332,-0.02821,-0.00118],"force_p95":0.37469,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.61075,"mean_force":0.07818,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52968,-0.02847,0.0291]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1873.0,"contact_point_centroid":[0.56286,-0.00636,0.12874],"force_p95":0.18667,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31298,"mean_force":0.1057,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.55772,0.01211,0.12944]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12181.0,"contact_point_centroid":[0.5355,-0.00941,0.06766],"force_p95":0.10577,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30316,"mean_force":0.06725,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53319,-0.02835,0.06598]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13376.0,"contact_point_centroid":[0.53564,-0.04709,0.06668],"force_p95":0.09764,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29053,"mean_force":0.06226,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53315,-0.02835,0.06557]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2109.0,"contact_point_centroid":[0.56531,0.03518,0.13072],"force_p95":0.1688,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25796,"mean_force":0.09747,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.5599,0.01693,0.13167]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54561,-0.02901,-0.00206],"force_p95":0.14154,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19329,"mean_force":0.12788,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53245,-0.02858,0.02905]},{"body_a":"world","body_b":"grasp_target","contact_count":88.0,"contact_point_centroid":[0.61391,0.13323,-0.00166],"force_p95":0.17164,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17896,"mean_force":0.12185,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.62138,0.14646,0.19488]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.61386,0.13336,-0.00198],"force_p95":0.12768,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14518,"mean_force":0.12303,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61839,0.14805,0.19233]},{"body_a":"world","body_b":"grasp_target","contact_count":2076.0,"contact_point_centroid":[0.5456,-0.02923,-0.00193],"force_p95":0.1323,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12286,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51761,-0.01311,0.23006]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4089.0,"contact_point_centroid":[0.53219,-0.00934,0.03033],"force_p95":0.07796,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12653,"mean_force":0.05182,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5312,-0.02854,0.02761]},{"body_a":"world","body_b":"grasp_target","contact_count":1592.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53747,-0.02768,0.0991]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4924.0,"contact_point_centroid":[0.53216,-0.04764,0.0294],"force_p95":0.06994,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08839,"mean_force":0.04479,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5312,-0.02854,0.02761]},{"body_a":"left_finger","body_b":"right_finger","contact_count":45.0,"contact_point_centroid":[0.62026,0.14194,0.19666],"force_p95":0.01565,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01565,"mean_force":0.01427,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.61976,0.14194,0.19442]},{"body_a":"left_finger","body_b":"right_finger","contact_count":92.0,"contact_point_centroid":[0.62146,0.14645,0.19681],"force_p95":0.01306,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01364,"mean_force":0.0116,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.62138,0.14645,0.19489]},{"body_a":"left_finger","body_b":"right_finger","contact_count":220.0,"contact_point_centroid":[0.62118,0.14893,0.19074],"force_p95":0.01124,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01128,"mean_force":0.01022,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62087,0.14892,0.18867]}],"total_contact_groups":16},"final_pose_error":0.01976,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.61386,0.13337,0.01602],"final_tcp_position":[0.62259,0.14869,0.19264],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":1.71227,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":520.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1592.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.53796,-0.02667,0.16153],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13575,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":398.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.13742,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10813.0,"raw_peak_contact_force":0.19329,"subtask_id":"reach_object","tcp_end":[0.53988,-0.0288,0.03776],"tcp_start":[0.53796,-0.02667,0.16153],"tcp_to_object_dist_end":0.01306,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54547,-0.02846,0.02578],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26053,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.10992,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":25761.0,"raw_peak_contact_force":0.61075,"subtask_id":"reach_object","tcp_end":[0.53117,-0.02854,0.02757],"tcp_start":[0.53988,-0.0288,0.03776],"tcp_to_object_dist_end":0.01441,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":794.0,"n_steps_budget":900.0,"object_pos_end":[0.55555,-0.02815,0.09984],"object_pos_start":[0.54547,-0.02846,0.02578],"object_to_goal_dist_end":0.22181,"object_to_goal_dist_start":0.26053,"object_z_max":0.09977,"peak_contact_force":0.18078,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4238.0,"raw_peak_contact_force":1.71227,"subtask_id":"reach_object","tcp_end":[0.54031,-0.02831,0.11243],"tcp_start":[0.53117,-0.02854,0.02757],"tcp_to_object_dist_end":0.01977,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":359.0,"n_steps_budget":1000.0,"object_pos_end":[0.61355,0.13305,0.01688],"object_pos_start":[0.55555,-0.02815,0.09984],"object_to_goal_dist_end":0.16432,"object_to_goal_dist_start":0.22181,"object_z_max":0.13466,"peak_contact_force":0.14651,"phase_name":"move_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":180.0,"raw_peak_contact_force":0.17896,"subtask_id":"reach_goal","tcp_end":[0.62096,0.14463,0.19574],"tcp_start":[0.54031,-0.02831,0.11243],"tcp_to_object_dist_end":0.17939,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":22.0,"n_steps_budget":1000.0,"object_pos_end":[0.61359,0.13416,0.01635],"object_pos_start":[0.61355,0.13305,0.01688],"object_to_goal_dist_end":0.16462,"object_to_goal_dist_start":0.16432,"object_z_max":0.01688,"peak_contact_force":0.12263,"phase_name":"place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1020.0,"raw_peak_contact_force":0.14518,"subtask_id":"reach_goal","tcp_end":[0.62259,0.14869,0.19264],"tcp_start":[0.62096,0.14463,0.19574],"tcp_to_object_dist_end":0.17712,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61386,0.13337,0.01602],"object_pos_start":[0.61359,0.13416,0.01635],"object_to_goal_dist_end":0.16506,"object_to_goal_dist_start":0.16462,"object_z_max":0.01635,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2076.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_goal","tcp_end":[0.61692,0.14757,0.2118],"tcp_start":[0.62259,0.14869,0.19264],"tcp_to_object_dist_end":0.19632,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```