## Search State

- **Seed**: 8
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6 | 0.1379 | 0.28 | ❌ rejected |
| 13 | approach → descend → contact → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | force_threshold_switch | impedance_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 8 | -0.0829 | 0.15 | ❌ rejected |
| 12 | approach → descend → contact → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 8 | 0.1112 | 0.17 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 7 | -0.0565 | 0.15 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.4223 | 0.74 | ❌ rejected |

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

## Current Skill (Q=0.138) — your mutation base

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
  guards:
  - id: grasp_secured
    when: before_phase
    predicate: bilateral_grasp
    threshold: 0.5
    on_failure: abort
- id: transport_1
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
    - 0.1
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: grasp_retained
    when: before_phase
    predicate: bilateral_grasp
    threshold: 0.5
    on_failure: abort
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
    - -0.03
    tolerance: 0.015
    orientation:
      mode: keep_current
  parameters:
    place_offset_z:
      type: scalar
      range:
      - -0.06
      - -0.01
      default: -0.03
      binds_to:
      - path: target.offset.z
        mode: replace
    place_speed:
      type: scalar
      range:
      - 0.01
      - 0.15
      default: 0.03
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
  - guards:
    - id=grasp_secured, when=before_phase, predicate=bilateral_grasp, on_failure=abort, threshold=0.5
- **transport_1** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=grasp_retained, when=before_phase, predicate=bilateral_grasp, on_failure=abort, threshold=0.5
- **place_1** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, -0.03], tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_offset_z: status=consumed; consumers=target.offset.z (replace)
    - place_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.138
- **task_score** (E): 0.282
- **fitness_score**: 0.618  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.480

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_1 | 1.00 | 0.1396 |
| descend_1 | 1.00 | 0.1273 |
| grasp_1 | 1.00 | 0.0126 |
| lift_1 | 1.00 | 0.1108 |
| transport_1 | 1.00 | 0.2668 |
| place_1 | 1.00 | 0.0655 |
| release_1 | 1.00 | 0.0197 |
| retract_1 | 1.00 | 0.0803 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.515, -0.001, 0.167) | (0.522, -0.001, 0.030)→(0.522, -0.001, 0.026) | 0.287→0.289 |
| descend_1 | descend | 1.00 / step_budget | (0.515, -0.001, 0.167)→(0.516, -0.001, 0.040) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 |
| grasp_1 | grasp | 1.00 / step_budget | (0.516, -0.001, 0.040)→(0.508, -0.001, 0.031) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 |
| lift_1 | lift | 1.00 / step_budget | (0.508, -0.001, 0.031)→(0.504, -0.001, 0.142) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.131) | 0.289→0.238 |
| transport_1 | approach | 1.00 / step_budget | (0.504, -0.001, 0.142)→(0.602, 0.197, 0.289) | (0.522, -0.001, 0.131)→(0.605, 0.183, 0.161) | 0.238→0.092 |
| place_1 | descend | 1.00 / step_budget | (0.602, 0.197, 0.289)→(0.604, 0.203, 0.224) | (0.605, 0.183, 0.161)→(0.611, 0.186, 0.010) | 0.092→0.197 |
| release_1 | release | 1.00 / step_budget | (0.604, 0.203, 0.224)→(0.599, 0.201, 0.243) | (0.611, 0.186, 0.010)→(0.611, 0.187, 0.016) | 0.197→0.191 |
| retract_1 | retract | 1.00 / step_budget | (0.599, 0.201, 0.243)→(0.597, 0.201, 0.323) | (0.611, 0.187, 0.016)→(0.611, 0.187, 0.016) | 0.191→0.191 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.338
- phase_score: 0.094
- phase_breakdown.reach_object_score: 0.313
- phase_breakdown.place_at_goal_score: 0.000
- grasp_place_fitness: 0.646

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.646
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.338
- **Median Q (composite search score)**: 0.129
- **K-run variance**: 0.0004
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.309


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.39033,"average_solve_count":269.0,"average_success_count":269.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.16688,"descend_1.descend_depth":0.00213,"lift_1.lift_height":0.13758,"place_1.place_offset_z":0.00741,"place_1.place_speed":0.03361,"transport_1.transport_speed":0.04075},"optimized_scores":{"best_composite_score":0.11919,"best_fitness_score":0.59919,"best_task_score":0.23881},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":112.0,"contact_point_centroid":[0.59307,0.23245,-0.01134],"force_p95":1.4419,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.95172,"mean_force":0.72528,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.5772,0.22455,0.25806]},{"body_a":"world","body_b":"grasp_target","contact_count":77.0,"contact_point_centroid":[0.47982,0.04597,-0.0015],"force_p95":0.62845,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.66507,"mean_force":0.15325,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46922,0.04663,0.0304]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6323.0,"contact_point_centroid":[0.46867,0.06542,0.08163],"force_p95":0.10495,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3192,"mean_force":0.06203,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46695,0.0464,0.07969]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5983.0,"contact_point_centroid":[0.46875,0.0274,0.08414],"force_p95":0.10507,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2923,"mean_force":0.0643,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46695,0.0464,0.08175]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48277,0.04842,-0.00218],"force_p95":0.17366,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25641,"mean_force":0.13637,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4716,0.04688,0.03002]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":197.0,"contact_point_centroid":[0.57911,0.2366,0.3056],"force_p95":0.17216,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2534,"mean_force":0.07005,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.57494,0.22029,0.31112]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11006.0,"contact_point_centroid":[0.52097,0.11073,0.22415],"force_p95":0.1307,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25272,"mean_force":0.08253,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.5168,0.12918,0.22493]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.59371,0.23195,-0.00256],"force_p95":0.12676,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22116,"mean_force":0.11066,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5745,0.22384,0.25164]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":70.0,"contact_point_centroid":[0.58101,0.20236,0.30743],"force_p95":0.1862,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19282,"mean_force":0.12538,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.57491,0.22011,0.3134]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10854.0,"contact_point_centroid":[0.52284,0.15019,0.22679],"force_p95":0.12734,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1709,"mean_force":0.08376,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51841,0.13171,0.22741]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4999.0,"contact_point_centroid":[0.47024,0.02753,0.03168],"force_p95":0.07121,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1547,"mean_force":0.04308,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47048,0.04677,0.02889]},{"body_a":"world","body_b":"grasp_target","contact_count":992.0,"contact_point_centroid":[0.4827,0.04873,-0.00187],"force_p95":0.13691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12312,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49104,0.01962,0.23527]},{"body_a":"world","body_b":"grasp_target","contact_count":1220.0,"contact_point_centroid":[0.59372,0.2319,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.57192,0.22251,0.31086]},{"body_a":"world","body_b":"grasp_target","contact_count":1664.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47905,0.04407,0.10165]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5518.0,"contact_point_centroid":[0.47011,0.06613,0.03106],"force_p95":0.07197,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08268,"mean_force":0.0414,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47049,0.04677,0.0289]},{"body_a":"left_finger","body_b":"right_finger","contact_count":169.0,"contact_point_centroid":[0.57659,0.22466,0.24885],"force_p95":0.01438,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01653,"mean_force":0.01159,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57603,0.22462,0.24686]}],"total_contact_groups":16},"final_pose_error":0.01978,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.59372,0.2319,0.01602],"final_tcp_position":[0.57212,0.2225,0.35166],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"phases":[{"n_steps":249.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_object","tcp_end":[0.48243,0.04086,0.16808],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14228,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":416.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_object","tcp_end":[0.47832,0.04753,0.0369],"tcp_start":[0.48243,0.04086,0.16808],"tcp_to_object_dist_end":0.01179,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48261,0.047,0.02538],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29153,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","subtask_id":"reach_object","tcp_end":[0.47045,0.04676,0.02886],"tcp_start":[0.47832,0.04753,0.0369],"tcp_to_object_dist_end":0.01265,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":365.0,"n_steps_budget":870.0,"object_pos_end":[0.48521,0.04669,0.13899],"object_pos_start":[0.48261,0.047,0.02538],"object_to_goal_dist_end":0.2256,"object_to_goal_dist_start":0.29153,"object_z_max":0.13872,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"reach_object","tcp_end":[0.46688,0.04639,0.14692],"tcp_start":[0.47045,0.04676,0.02886],"tcp_to_object_dist_end":0.01997,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":951.0,"n_steps_budget":1000.0,"object_pos_end":[0.58084,0.21933,0.28997],"object_pos_start":[0.48521,0.04669,0.13899],"object_to_goal_dist_end":0.06026,"object_to_goal_dist_start":0.2256,"object_z_max":0.28988,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"place_at_goal","tcp_end":[0.57488,0.21976,0.31415],"tcp_start":[0.46688,0.04639,0.14692],"tcp_to_object_dist_end":0.0249,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":146.0,"n_steps_budget":1000.0,"object_pos_end":[0.59388,0.22986,-0.00248],"object_pos_start":[0.58084,0.21933,0.28997],"object_to_goal_dist_end":0.23328,"object_to_goal_dist_start":0.06026,"object_z_max":0.28997,"phase_name":"place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"place_at_goal","tcp_end":[0.57766,0.22524,0.25156],"tcp_start":[0.57488,0.21976,0.31415],"tcp_to_object_dist_end":0.2546,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59372,0.2319,0.01602],"object_pos_start":[0.59388,0.22986,-0.00248],"object_to_goal_dist_end":0.21481,"object_to_goal_dist_start":0.23328,"object_z_max":0.01689,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","subtask_id":"place_at_goal","tcp_end":[0.5735,0.22331,0.27138],"tcp_start":[0.57766,0.22524,0.25156],"tcp_to_object_dist_end":0.25631,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":305.0,"n_steps_budget":660.0,"object_pos_end":[0.59372,0.2319,0.01602],"object_pos_start":[0.59372,0.2319,0.01602],"object_to_goal_dist_end":0.21481,"object_to_goal_dist_start":0.21481,"object_z_max":0.01602,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","subtask_id":"place_at_goal","tcp_end":[0.57212,0.2225,0.35166],"tcp_start":[0.5735,0.22331,0.27138],"tcp_to_object_dist_end":0.33647,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.79327,"average_solve_count":208.0,"average_success_count":208.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.10307,"descend_1.descend_depth":0.01049,"lift_1.lift_height":0.12744,"place_1.place_offset_z":0.01917,"place_1.place_speed":0.05523,"transport_1.transport_speed":0.08564},"optimized_scores":{"best_composite_score":0.12884,"best_fitness_score":0.60884,"best_task_score":0.27013},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":806.0,"contact_point_centroid":[0.59997,0.18535,-0.00363],"force_p95":0.75817,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.01798,"mean_force":0.18626,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.5956,0.19366,0.27704]},{"body_a":"world","body_b":"grasp_target","contact_count":78.0,"contact_point_centroid":[0.53437,-0.02034,-0.00136],"force_p95":0.52071,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55357,"mean_force":0.11472,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52156,-0.02069,0.03599]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5136.0,"contact_point_centroid":[0.52182,-0.00171,0.08459],"force_p95":0.11026,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33077,"mean_force":0.07308,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.519,-0.02063,0.08222]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5572.0,"contact_point_centroid":[0.52193,-0.03944,0.08236],"force_p95":0.10695,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30451,"mean_force":0.06873,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51904,-0.02063,0.08071]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6710.0,"contact_point_centroid":[0.55069,0.0399,0.18916],"force_p95":0.13289,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25725,"mean_force":0.0934,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54505,0.05829,0.18923]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6784.0,"contact_point_centroid":[0.55203,0.08029,0.19127],"force_p95":0.12926,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19772,"mean_force":0.09182,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54634,0.06193,0.19149]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53703,-0.02116,-0.00206],"force_p95":0.13991,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18155,"mean_force":0.12734,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52411,-0.02074,0.03609]},{"body_a":"world","body_b":"grasp_target","contact_count":1064.0,"contact_point_centroid":[0.53702,-0.02132,-0.00188],"force_p95":0.1365,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12309,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51305,-0.00861,0.23485]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4101.0,"contact_point_centroid":[0.52377,-0.00151,0.03741],"force_p95":0.07761,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12722,"mean_force":0.05183,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52289,-0.02072,0.03469]},{"body_a":"world","body_b":"grasp_target","contact_count":472.0,"contact_point_centroid":[0.59983,0.18529,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12262,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.60488,0.21969,0.26744]},{"body_a":"world","body_b":"grasp_target","contact_count":1504.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52842,-0.01936,0.105]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.59983,0.18529,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60273,0.2218,0.23922]},{"body_a":"world","body_b":"grasp_target","contact_count":1268.0,"contact_point_centroid":[0.59983,0.18529,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.59999,0.22047,0.29819]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4911.0,"contact_point_centroid":[0.52376,-0.0398,0.03649],"force_p95":0.06973,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0851,"mean_force":0.0447,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52289,-0.02072,0.03469]},{"body_a":"left_finger","body_b":"right_finger","contact_count":680.0,"contact_point_centroid":[0.59789,0.19855,0.28247],"force_p95":0.01308,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01621,"mean_force":0.01081,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.59745,0.19854,0.28021]},{"body_a":"left_finger","body_b":"right_finger","contact_count":496.0,"contact_point_centroid":[0.6054,0.21973,0.26963],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01262,"mean_force":0.01059,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.60489,0.21971,0.26727]}],"total_contact_groups":17},"final_pose_error":0.0198,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.59983,0.18529,0.01602],"final_tcp_position":[0.60021,0.22047,0.33889],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"phases":[{"n_steps":267.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_object","tcp_end":[0.52822,-0.01793,0.16743],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14173,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":376.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_object","tcp_end":[0.53136,-0.02086,0.04453],"tcp_start":[0.52822,-0.01793,0.16743],"tcp_to_object_dist_end":0.01936,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53692,-0.02067,0.02579],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31636,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","subtask_id":"reach_object","tcp_end":[0.52286,-0.02071,0.03465],"tcp_start":[0.53136,-0.02086,0.04453],"tcp_to_object_dist_end":0.01662,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":358.0,"n_steps_budget":810.0,"object_pos_end":[0.53633,-0.02065,0.12849],"object_pos_start":[0.53692,-0.02067,0.02579],"object_to_goal_dist_end":0.27094,"object_to_goal_dist_start":0.31636,"object_z_max":0.12824,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"reach_object","tcp_end":[0.51893,-0.02062,0.14262],"tcp_start":[0.52286,-0.02071,0.03465],"tcp_to_object_dist_end":0.02241,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":969.0,"n_steps_budget":1000.0,"object_pos_end":[0.59983,0.18528,0.01602],"object_pos_start":[0.53633,-0.02065,0.12849],"object_to_goal_dist_end":0.19633,"object_to_goal_dist_start":0.27094,"object_z_max":0.22033,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"place_at_goal","tcp_end":[0.60436,0.21666,0.29195],"tcp_start":[0.51893,-0.02062,0.14262],"tcp_to_object_dist_end":0.27774,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":118.0,"n_steps_budget":1000.0,"object_pos_end":[0.59983,0.18529,0.01602],"object_pos_start":[0.59983,0.18528,0.01602],"object_to_goal_dist_end":0.19633,"object_to_goal_dist_start":0.19633,"object_z_max":0.01602,"phase_name":"place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"place_at_goal","tcp_end":[0.60609,0.22315,0.23997],"tcp_start":[0.60436,0.21666,0.29195],"tcp_to_object_dist_end":0.22722,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59983,0.18529,0.01602],"object_pos_start":[0.59983,0.18529,0.01602],"object_to_goal_dist_end":0.19633,"object_to_goal_dist_start":0.19633,"object_z_max":0.01602,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","subtask_id":"place_at_goal","tcp_end":[0.60166,0.22126,0.25862],"tcp_start":[0.60609,0.22315,0.23997],"tcp_to_object_dist_end":0.24526,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":317.0,"n_steps_budget":630.0,"object_pos_end":[0.59983,0.18529,0.01602],"object_pos_start":[0.59983,0.18529,0.01602],"object_to_goal_dist_end":0.19633,"object_to_goal_dist_start":0.19633,"object_z_max":0.01602,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","subtask_id":"place_at_goal","tcp_end":[0.60021,0.22047,0.33889],"tcp_start":[0.60166,0.22126,0.25862],"tcp_to_object_dist_end":0.32478,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.45455,"average_solve_count":253.0,"average_success_count":253.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.12092,"descend_1.descend_depth":0.00511,"lift_1.lift_height":0.12563,"place_1.place_offset_z":-0.01003,"place_1.place_speed":0.07323,"transport_1.transport_speed":0.02118},"optimized_scores":{"best_composite_score":0.16567,"best_fitness_score":0.64567,"best_task_score":0.33841},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":482.0,"contact_point_centroid":[0.63937,0.14266,-0.00467],"force_p95":0.98909,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.07338,"mean_force":0.23327,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.62635,0.15897,0.20971]},{"body_a":"world","body_b":"grasp_target","contact_count":80.0,"contact_point_centroid":[0.54242,-0.02809,-0.00139],"force_p95":0.57157,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64751,"mean_force":0.14213,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5297,-0.02832,0.03023]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4990.0,"contact_point_centroid":[0.53009,-0.00932,0.07789],"force_p95":0.11151,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33592,"mean_force":0.07467,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52706,-0.02822,0.07547]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5443.0,"contact_point_centroid":[0.5302,-0.04701,0.07601],"force_p95":0.10728,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31758,"mean_force":0.07009,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52709,-0.02822,0.07433]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9202.0,"contact_point_centroid":[0.57567,0.07691,0.19086],"force_p95":0.13042,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21968,"mean_force":0.08642,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.57149,0.05851,0.19219]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54562,-0.029,-0.00208],"force_p95":0.14692,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21818,"mean_force":0.12923,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53226,-0.02839,0.03034]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9568.0,"contact_point_centroid":[0.57367,0.03605,0.18817],"force_p95":0.12845,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1828,"mean_force":0.08465,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.56928,0.05443,0.18933]},{"body_a":"world","body_b":"grasp_target","contact_count":1092.0,"contact_point_centroid":[0.5456,-0.02923,-0.00188],"force_p95":0.1365,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12307,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51667,-0.01192,0.23415]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4082.0,"contact_point_centroid":[0.53207,-0.00916,0.03161],"force_p95":0.07873,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13375,"mean_force":0.05186,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53101,-0.02836,0.02889]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.63916,0.14291,-0.00199],"force_p95":0.12385,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12543,"mean_force":0.12275,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62343,0.16041,0.17961]},{"body_a":"world","body_b":"grasp_target","contact_count":1556.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53626,-0.02662,0.10168]},{"body_a":"world","body_b":"grasp_target","contact_count":1284.0,"contact_point_centroid":[0.63916,0.14291,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.61947,0.15917,0.23864]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4943.0,"contact_point_centroid":[0.53202,-0.04747,0.03068],"force_p95":0.07081,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08721,"mean_force":0.04474,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53102,-0.02836,0.0289]},{"body_a":"left_finger","body_b":"right_finger","contact_count":352.0,"contact_point_centroid":[0.62735,0.15976,0.20296],"force_p95":0.01415,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01579,"mean_force":0.01112,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.62677,0.15975,0.20048]},{"body_a":"left_finger","body_b":"right_finger","contact_count":221.0,"contact_point_centroid":[0.62648,0.16123,0.17833],"force_p95":0.01095,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01097,"mean_force":0.01008,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62599,0.16122,0.17601]}],"total_contact_groups":15},"final_pose_error":0.01988,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.63916,0.14291,0.01602],"final_tcp_position":[0.61952,0.15914,0.27928],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"phases":[{"n_steps":274.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_object","tcp_end":[0.53561,-0.02472,0.16651],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14091,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":389.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_object","tcp_end":[0.53967,-0.02861,0.03905],"tcp_start":[0.53561,-0.02472,0.16651],"tcp_to_object_dist_end":0.01433,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54548,-0.02831,0.02572],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26045,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","subtask_id":"reach_object","tcp_end":[0.53098,-0.02835,0.02886],"tcp_start":[0.53967,-0.02861,0.03905],"tcp_to_object_dist_end":0.01483,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":357.0,"n_steps_budget":810.0,"object_pos_end":[0.54593,-0.0282,0.12597],"object_pos_start":[0.54548,-0.02831,0.02572],"object_to_goal_dist_end":0.21783,"object_to_goal_dist_start":0.26045,"object_z_max":0.12572,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"reach_object","tcp_end":[0.52694,-0.02821,0.13504],"tcp_start":[0.53098,-0.02835,0.02886],"tcp_to_object_dist_end":0.02104,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":899.0,"n_steps_budget":1000.0,"object_pos_end":[0.63353,0.14517,0.176],"object_pos_start":[0.54593,-0.0282,0.12597],"object_to_goal_dist_end":0.0198,"object_to_goal_dist_start":0.21783,"object_z_max":0.22886,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"place_at_goal","tcp_end":[0.62531,0.15501,0.2614],"tcp_start":[0.52694,-0.02821,0.13504],"tcp_to_object_dist_end":0.08636,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":173.0,"n_steps_budget":1000.0,"object_pos_end":[0.63918,0.14279,0.01605],"object_pos_start":[0.63353,0.14517,0.176],"object_to_goal_dist_end":0.16251,"object_to_goal_dist_start":0.0198,"object_z_max":0.176,"phase_name":"place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"place_at_goal","tcp_end":[0.6279,0.16165,0.18052],"tcp_start":[0.62531,0.15501,0.2614],"tcp_to_object_dist_end":0.16592,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.63916,0.14291,0.01602],"object_pos_start":[0.63918,0.14279,0.01605],"object_to_goal_dist_end":0.16252,"object_to_goal_dist_start":0.16251,"object_z_max":0.01605,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","subtask_id":"place_at_goal","tcp_end":[0.62191,0.15993,0.19901],"tcp_start":[0.6279,0.16165,0.18052],"tcp_to_object_dist_end":0.18458,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":321.0,"n_steps_budget":630.0,"object_pos_end":[0.63916,0.14291,0.01602],"object_pos_start":[0.63916,0.14291,0.01602],"object_to_goal_dist_end":0.16252,"object_to_goal_dist_start":0.16252,"object_z_max":0.01602,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","subtask_id":"place_at_goal","tcp_end":[0.61952,0.15914,0.27928],"tcp_start":[0.62191,0.15993,0.19901],"tcp_to_object_dist_end":0.26449,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```