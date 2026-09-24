## Search State

- **Seed**: 8
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → descend → grasp → lift → approach → grasp | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | impedance_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | pose_tolerance | time_limit | 9 | 0.1146 | 0.43 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 12 | -0.0171 | 0.41 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → grasp | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | impedance_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | pose_tolerance | time_limit | 9 | 0.1855 | 0.56 | ✅ accepted |
| 4 | approach → descend → grasp → lift → push → grasp | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | impedance_control | position_control | time_limit | time_limit | grasp_success | pose_tolerance | pose_tolerance | time_limit | 7 | 0.2678 | 0.54 | ✅ accepted |
| 3 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 10 | -0.0818 | 0.26 | ❌ rejected |

**Proposal policy**: task_score is 0.43 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.115) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_above_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.12
  weight: 0.2
- id: reach_object
  anchor: object
  weight: 0.2
- id: lift_object
  anchor: object
  target_entity: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.2
- id: transport_to_goal
  target_entity: object
  weight: 0.2
- id: hold_at_goal
  target_entity: object
  weight: 0.4
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: time_limit
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.12
    orientation:
      mode: none
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.08
      - 0.25
      default: 0.12
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_above_object
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: time_limit
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: none
  parameters:
    grasp_offset_z:
      type: scalar
      range:
      - -0.01
      - 0.03
      default: 0.005
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
  parameters:
    grasp_duration:
      type: scalar
      range:
      - 0.5
      - 3.0
      default: 1.5
      binds_to:
      - path: duration.max_time
        mode: replace
  guards:
  - id: grasp_check
    when: after_phase
    predicate: bilateral_grasp
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 3
    strategy: offset_target
    offset:
    - 0.005
    - 0.005
    - -0.005
  subtask_id: reach_object
- id: lift_1
  type: lift
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.1
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: lift_object
- id: transport_1
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
    - 0.03
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.1
      - 1.0
      default: 0.35
      binds_to:
      - path: generator.speed
        mode: replace
    transport_xy_offset_x:
      type: scalar
      range:
      - -0.05
      - 0.05
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: add
    transport_xy_offset_y:
      type: scalar
      range:
      - -0.05
      - 0.05
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: add
    transport_z_offset_delta:
      type: scalar
      range:
      - -0.03
      - 0.07
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: transport_to_goal
- id: hold_1
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
    hold_duration:
      type: scalar
      range:
      - 0.5
      - 3.0
      default: 1.5
      binds_to:
      - path: duration.max_time
        mode: replace
  subtask_id: hold_at_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.12]
  - orientation: mode=none
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0]
  - orientation: mode=none
  - parameter_bindings:
    - grasp_offset_z: status=consumed; consumers=target.offset.z (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - grasp_duration: status=consumed; consumers=duration.max_time (replace)
  - guards:
    - id=grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=1.0
  - retries: max_attempts=3, strategy=offset_target, offset=[0.005, 0.005, -0.005]
- **lift_1** (`lift`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
- **transport_1** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.03], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
    - transport_xy_offset_x: status=consumed; consumers=target.offset.x (add)
    - transport_xy_offset_y: status=consumed; consumers=target.offset.y (add)
    - transport_z_offset_delta: status=consumed; consumers=target.offset.z (replace)
- **hold_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - hold_duration: status=consumed; consumers=duration.max_time (replace)

## Design Metrics

- **Composite score**: 0.115
- **task_score** (E): 0.426
- **fitness_score**: 0.685  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.570

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1004 |
| descend_1 | 1.00 | 1.00 | 0.1657 |
| grasp_1 | 1.00 | 1.00 | 0.0127 |
| lift_1 | 1.00 | 1.00 | 0.1358 |
| transport_1 | 1.00 | 0.67 | 0.2105 |
| hold_1 | 1.00 | 1.00 | 0.0157 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / time_limit | (0.500, -0.000, 0.301)→(0.518, -0.001, 0.212) | (0.522, -0.001, 0.030)→(0.522, -0.001, 0.026) | 0.287→0.289 | 1.00 / 4.000 | 5.193 | 0.138 |
| descend_1 | descend | 1.00 / time_limit | (0.518, -0.001, 0.212)→(0.516, -0.001, 0.046) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.516, -0.001, 0.046)→(0.508, -0.001, 0.037) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.290 | 1.00 / 44.667 | 0.142 | 0.180 |
| lift_1 | lift | 1.00 / step_budget | (0.508, -0.001, 0.037)→(0.517, -0.001, 0.172) | (0.522, -0.001, 0.026)→(0.533, -0.001, 0.153) | 0.290→0.228 | 1.00 / 22.333 | 72.219 | 0.490 |
| transport_1 | approach | 1.00 / step_budget | (0.517, -0.001, 0.172)→(0.608, 0.184, 0.201) | (0.533, -0.001, 0.153)→(0.617, 0.189, 0.103) | 0.228→0.110 | 0.67 / 10.000 | 5.955 | 0.788 |
| hold_1 | grasp | 1.00 / step_budget | (0.608, 0.184, 0.201)→(0.602, 0.183, 0.186) | (0.617, 0.189, 0.103)→(0.619, 0.197, 0.070) | 0.110→0.139 | 1.00 / 13.333 | 0.124 | 0.774 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.670
- phase_score: 0.588
- phase_breakdown.transport_to_goal_score: 0.526
- phase_breakdown.reach_above_object_score: 0.530
- phase_breakdown.hold_at_goal_score: 0.433
- phase_breakdown.reach_object_score: 0.767
- phase_breakdown.lift_object_score: 0.841
- grasp_place_fitness: 0.813

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.813
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.670
- **Median Q (composite search score)**: 0.061
- **K-run variance**: 0.0083
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.284


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.06087,"average_solve_count":115.0,"average_success_count":115.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.14895,"descend_1.grasp_offset_z":0.01501,"grasp_1.grasp_duration":1.20424,"hold_1.hold_duration":0.86042,"lift_1.lift_height":0.18112,"transport_1.transport_speed":0.71,"transport_1.transport_xy_offset_x":-0.02071,"transport_1.transport_xy_offset_y":0.0028,"transport_1.transport_z_offset_delta":0.00425},"optimized_scores":{"best_composite_score":0.24251,"best_fitness_score":0.81251,"best_task_score":0.6698},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":79.0,"contact_point_centroid":[0.48058,0.04687,-0.00138],"force_p95":0.49163,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55835,"mean_force":0.11479,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46842,0.04725,0.03209]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6943.0,"contact_point_centroid":[0.47366,0.06647,0.10329],"force_p95":0.1109,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28325,"mean_force":0.07399,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4714,0.04724,0.1009]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8978.0,"contact_point_centroid":[0.4748,0.02868,0.10027],"force_p95":0.09951,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2732,"mean_force":0.05977,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47124,0.04723,0.09915]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5490.0,"contact_point_centroid":[0.55299,0.2351,0.21205],"force_p95":0.10049,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22671,"mean_force":0.07656,"phase_index":5.0,"phase_name":"hold_1","phase_type":"grasp","tcp_position_centroid":[0.54814,0.21594,0.21308]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4685.0,"contact_point_centroid":[0.5208,0.15513,0.20598],"force_p95":0.12669,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22442,"mean_force":0.09646,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51609,0.1361,0.20473]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48276,0.04868,-0.00212],"force_p95":0.15611,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21394,"mean_force":0.13144,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47073,0.04749,0.03171]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5746.0,"contact_point_centroid":[0.52281,0.11707,0.20371],"force_p95":0.12922,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20575,"mean_force":0.08305,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51558,0.13494,0.20449]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5752.0,"contact_point_centroid":[0.5555,0.19783,0.21106],"force_p95":0.09234,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20342,"mean_force":0.07209,"phase_index":5.0,"phase_name":"hold_1","phase_type":"grasp","tcp_position_centroid":[0.5481,0.21593,0.21298]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5163.0,"contact_point_centroid":[0.4712,0.02836,0.03174],"force_p95":0.0734,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18507,"mean_force":0.04203,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46952,0.04737,0.03048]},{"body_a":"world","body_b":"grasp_target","contact_count":2372.0,"contact_point_centroid":[0.4827,0.04873,-0.00194],"force_p95":0.13103,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12283,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48902,0.02235,0.23947]},{"body_a":"world","body_b":"grasp_target","contact_count":3340.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47742,0.04672,0.10215]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4210.0,"contact_point_centroid":[0.46939,0.06668,0.03293],"force_p95":0.08798,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09645,"mean_force":0.05202,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46952,0.04737,0.03049]}],"total_contact_groups":12},"final_pose_error":0.01996,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.55299,0.21656,0.17921],"final_tcp_position":[0.55259,0.21734,0.22378],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":216.43118,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":594.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":15.33469,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2372.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_above_object","tcp_end":[0.48012,0.04526,0.18143],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15548,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":835.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3340.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.47763,0.04816,0.03875],"tcp_start":[0.48012,0.04526,0.18143],"tcp_to_object_dist_end":0.01372,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48268,0.04795,0.0256],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29076,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.15426,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11173.0,"raw_peak_contact_force":0.21394,"subtask_id":"reach_object","tcp_end":[0.46949,0.04736,0.03045],"tcp_start":[0.47763,0.04816,0.03875],"tcp_to_object_dist_end":0.01407,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":504.0,"n_steps_budget":1000.0,"object_pos_end":[0.49562,0.04859,0.17308],"object_pos_start":[0.48268,0.04795,0.0256],"object_to_goal_dist_end":0.20791,"object_to_goal_dist_start":0.29076,"object_z_max":0.17283,"peak_contact_force":216.43118,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":16000.0,"raw_peak_contact_force":0.55835,"subtask_id":"lift_object","tcp_end":[0.47827,0.04755,0.18737],"tcp_start":[0.46949,0.04736,0.03045],"tcp_to_object_dist_end":0.0225,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":476.0,"n_steps_budget":1000.0,"object_pos_end":[0.55867,0.2184,0.19493],"object_pos_start":[0.49562,0.04859,0.17308],"object_to_goal_dist_end":0.04373,"object_to_goal_dist_start":0.20791,"object_z_max":0.19489,"peak_contact_force":0.09276,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":10431.0,"raw_peak_contact_force":0.22442,"subtask_id":"transport_to_goal","tcp_end":[0.55259,0.21734,0.22378],"tcp_start":[0.47827,0.04755,0.18737],"tcp_to_object_dist_end":0.02951,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.55299,0.21656,0.17921],"object_pos_start":[0.55867,0.2184,0.19493],"object_to_goal_dist_end":0.06012,"object_to_goal_dist_start":0.04373,"object_z_max":0.19493,"peak_contact_force":0.12708,"phase_name":"hold_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11242.0,"raw_peak_contact_force":0.22671,"subtask_id":"hold_at_goal","tcp_end":[0.54729,0.21557,0.21098],"tcp_start":[0.55259,0.21734,0.22378],"tcp_to_object_dist_end":0.03229,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.06542,"average_solve_count":107.0,"average_success_count":107.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.19196,"descend_1.grasp_offset_z":0.01828,"grasp_1.grasp_duration":2.37713,"hold_1.hold_duration":1.04968,"lift_1.lift_height":0.16496,"transport_1.transport_speed":0.39873,"transport_1.transport_xy_offset_x":0.01319,"transport_1.transport_xy_offset_y":0.0026,"transport_1.transport_z_offset_delta":0.01159},"optimized_scores":{"best_composite_score":0.04005,"best_fitness_score":0.61005,"best_task_score":0.27567},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":35.0,"contact_point_centroid":[0.63544,0.22713,-0.00965],"force_p95":1.74989,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.80039,"mean_force":1.28337,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.61492,0.21319,0.20707]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.63442,0.2156,-0.00246],"force_p95":0.13111,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.82588,"mean_force":0.12956,"phase_index":5.0,"phase_name":"hold_1","phase_type":"grasp","tcp_position_centroid":[0.61092,0.2147,0.1948]},{"body_a":"world","body_b":"grasp_target","contact_count":78.0,"contact_point_centroid":[0.53443,-0.02118,-0.00132],"force_p95":0.43054,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.48838,"mean_force":0.10126,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52206,-0.02106,0.03832]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4817.0,"contact_point_centroid":[0.57258,0.06336,0.1859],"force_p95":0.15671,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37677,"mean_force":0.09955,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.56711,0.08222,0.18475]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7646.0,"contact_point_centroid":[0.52814,-0.00251,0.09604],"force_p95":0.10343,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28501,"mean_force":0.06475,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52482,-0.02119,0.09464]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6426.0,"contact_point_centroid":[0.5276,-0.04024,0.09879],"force_p95":0.10953,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27171,"mean_force":0.07414,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52496,-0.02119,0.09638]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6280.0,"contact_point_centroid":[0.57319,0.09923,0.1844],"force_p95":0.11423,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24655,"mean_force":0.07871,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.56674,0.08116,0.1846]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53702,-0.02144,-0.00203],"force_p95":0.13358,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14975,"mean_force":0.12555,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52442,-0.0211,0.03843]},{"body_a":"world","body_b":"grasp_target","contact_count":3880.0,"contact_point_centroid":[0.53702,-0.02132,-0.00196],"force_p95":0.12481,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12275,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51688,-0.01144,0.25268]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53075,-0.02094,0.11775]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5336.0,"contact_point_centroid":[0.52393,-0.002,0.03901],"force_p95":0.06844,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09923,"mean_force":0.04119,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52315,-0.02108,0.03696]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4149.0,"contact_point_centroid":[0.52245,-0.04033,0.03995],"force_p95":0.08062,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08743,"mean_force":0.05171,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52315,-0.02108,0.03696]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1735.0,"contact_point_centroid":[0.61137,0.21455,0.19587],"force_p95":0.0119,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0164,"mean_force":0.01059,"phase_index":5.0,"phase_name":"hold_1","phase_type":"grasp","tcp_position_centroid":[0.61053,0.21452,0.19373]}],"total_contact_groups":13},"final_pose_error":0.0199,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.63447,0.21573,0.01602],"final_tcp_position":[0.61581,0.21606,0.2075],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":17.77374,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":971.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3880.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_above_object","tcp_end":[0.53242,-0.02063,0.21795],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.19199,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.53165,-0.02121,0.04686],"tcp_start":[0.53242,-0.02063,0.21795],"tcp_to_object_dist_end":0.02153,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5369,-0.02149,0.02587],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31697,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13375,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11285.0,"raw_peak_contact_force":0.14975,"subtask_id":"reach_object","tcp_end":[0.52312,-0.02108,0.03692],"tcp_start":[0.53165,-0.02121,0.04686],"tcp_to_object_dist_end":0.01767,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":466.0,"n_steps_budget":960.0,"object_pos_end":[0.548,-0.02211,0.15265],"object_pos_start":[0.5369,-0.02149,0.02587],"object_to_goal_dist_end":0.26328,"object_to_goal_dist_start":0.31697,"object_z_max":0.15241,"peak_contact_force":0.11672,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":14150.0,"raw_peak_contact_force":0.48838,"subtask_id":"lift_object","tcp_end":[0.532,-0.0214,0.17155],"tcp_start":[0.52312,-0.02108,0.03692],"tcp_to_object_dist_end":0.02478,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":607.0,"n_steps_budget":1000.0,"object_pos_end":[0.63613,0.22208,-0.00284],"object_pos_start":[0.548,-0.02211,0.15265],"object_to_goal_dist_end":0.21191,"object_to_goal_dist_start":0.26328,"object_z_max":0.16838,"peak_contact_force":17.77374,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":11132.0,"raw_peak_contact_force":1.80039,"subtask_id":"transport_to_goal","tcp_end":[0.61581,0.21606,0.2075],"tcp_start":[0.532,-0.0214,0.17155],"tcp_to_object_dist_end":0.2114,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.63447,0.21573,0.01602],"object_pos_start":[0.63613,0.22208,-0.00284],"object_to_goal_dist_end":0.19328,"object_to_goal_dist_start":0.21191,"object_z_max":0.01682,"peak_contact_force":0.12263,"phase_name":"hold_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3535.0,"raw_peak_contact_force":0.82588,"subtask_id":"hold_at_goal","tcp_end":[0.61006,0.21434,0.1925],"tcp_start":[0.61581,0.21606,0.2075],"tcp_to_object_dist_end":0.17816,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.06604,"average_solve_count":106.0,"average_success_count":106.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.21078,"descend_1.grasp_offset_z":-0.00016,"grasp_1.grasp_duration":1.26006,"hold_1.hold_duration":1.70601,"lift_1.lift_height":0.15188,"transport_1.transport_speed":0.2563,"transport_1.transport_xy_offset_x":0.03414,"transport_1.transport_xy_offset_y":-0.03377,"transport_1.transport_z_offset_delta":0.00544},"optimized_scores":{"best_composite_score":0.06136,"best_fitness_score":0.63136,"best_task_score":0.33325},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1599.0,"contact_point_centroid":[0.66814,0.15889,-0.0026],"force_p95":0.28568,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.26938,"mean_force":0.14655,"phase_index":5.0,"phase_name":"hold_1","phase_type":"grasp","tcp_position_centroid":[0.64877,0.11868,0.15695]},{"body_a":"world","body_b":"grasp_target","contact_count":80.0,"contact_point_centroid":[0.54368,-0.02884,-0.00137],"force_p95":0.37883,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.42336,"mean_force":0.09075,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53013,-0.02862,0.04481]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4452.0,"contact_point_centroid":[0.59305,0.01767,0.1604],"force_p95":0.15693,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33845,"mean_force":0.10044,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.58936,0.03627,0.16179]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6870.0,"contact_point_centroid":[0.53622,-0.00997,0.09346],"force_p95":0.10526,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27434,"mean_force":0.06338,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53301,-0.02869,0.09177]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5710.0,"contact_point_centroid":[0.53576,-0.0478,0.09507],"force_p95":0.11032,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25874,"mean_force":0.07281,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53311,-0.02869,0.0924]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4787.0,"contact_point_centroid":[0.59626,0.05648,0.15988],"force_p95":0.14513,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23504,"mean_force":0.09399,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.59104,0.03842,0.16202]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54562,-0.02927,-0.00206],"force_p95":0.13976,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1754,"mean_force":0.12728,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53248,-0.02868,0.04503]},{"body_a":"world","body_b":"grasp_target","contact_count":3996.0,"contact_point_centroid":[0.5456,-0.02923,-0.00196],"force_p95":0.12459,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12275,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52035,-0.01485,0.26443]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53874,-0.02838,0.13186]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5801.0,"contact_point_centroid":[0.53177,-0.00939,0.04647],"force_p95":0.06729,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11501,"mean_force":0.03816,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53121,-0.02865,0.04353]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5134.0,"contact_point_centroid":[0.53136,-0.04793,0.04684],"force_p95":0.07153,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07802,"mean_force":0.04291,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53122,-0.02865,0.04353]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1410.0,"contact_point_centroid":[0.64911,0.11864,0.15838],"force_p95":0.01192,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01654,"mean_force":0.01061,"phase_index":5.0,"phase_name":"hold_1","phase_type":"grasp","tcp_position_centroid":[0.64839,0.11861,0.15609]}],"total_contact_groups":12},"final_pose_error":0.01988,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.66814,0.15905,0.01602],"final_tcp_position":[0.65505,0.11961,0.17143],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":1.26938,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3996.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_above_object","tcp_end":[0.54033,-0.02783,0.237],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.21105,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.53969,-0.02887,0.05373],"tcp_start":[0.54033,-0.02783,0.237],"tcp_to_object_dist_end":0.02834,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":49.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54554,-0.02901,0.02577],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26093,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.13936,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12735.0,"raw_peak_contact_force":0.1754,"subtask_id":"reach_object","tcp_end":[0.53118,-0.02865,0.04349],"tcp_start":[0.53969,-0.02887,0.05373],"tcp_to_object_dist_end":0.02281,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":403.0,"n_steps_budget":840.0,"object_pos_end":[0.55525,-0.02955,0.13446],"object_pos_start":[0.54554,-0.02901,0.02577],"object_to_goal_dist_end":0.21365,"object_to_goal_dist_start":0.26093,"object_z_max":0.13423,"peak_contact_force":0.11001,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":12660.0,"raw_peak_contact_force":0.42336,"subtask_id":"lift_object","tcp_end":[0.54027,-0.02887,0.15839],"tcp_start":[0.53118,-0.02865,0.04349],"tcp_to_object_dist_end":0.02824,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":491.0,"n_steps_budget":1000.0,"object_pos_end":[0.65674,0.12768,0.11735],"object_pos_start":[0.55525,-0.02955,0.13446],"object_to_goal_dist_end":0.07421,"object_to_goal_dist_start":0.21365,"object_z_max":0.1347,"peak_contact_force":0.0,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9239.0,"raw_peak_contact_force":0.33845,"subtask_id":"transport_to_goal","tcp_end":[0.65505,0.11961,0.17143],"tcp_start":[0.54027,-0.02887,0.15839],"tcp_to_object_dist_end":0.05471,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.66814,0.15905,0.01602],"object_pos_start":[0.65674,0.12768,0.11735],"object_to_goal_dist_end":0.16483,"object_to_goal_dist_start":0.07421,"object_z_max":0.11735,"peak_contact_force":0.12263,"phase_name":"hold_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3009.0,"raw_peak_contact_force":1.26938,"subtask_id":"hold_at_goal","tcp_end":[0.64827,0.11858,0.15581],"tcp_start":[0.65505,0.11961,0.17143],"tcp_to_object_dist_end":0.14688,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```