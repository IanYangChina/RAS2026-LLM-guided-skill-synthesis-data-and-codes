## Search State

- **Seed**: 8
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | impedance_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 7 | 0.1247 | 0.31 | ❌ rejected |
| 12 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 13 | -0.3554 | 0.19 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 9 | -0.0812 | 0.15 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.0534 | 0.23 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 5 | -0.2025 | 0.17 | ❌ rejected |

**Proposal policy**: task_score is 0.31 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 1.000, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.125) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: approach_subtask
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.12
  weight: 0.2
- id: place_subtask
  target_entity: object
  weight: 0.8
phases:
- id: approach_obj
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
    - 0.12
    tolerance: 0.02
  parameters:
    pre_grasp_z_offset:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.12
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: approach_subtask
- id: descend_grasp
  type: descend
  generator: linear_cartesian
  control: impedance_control
  termination: contact_detected
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.01
  parameters:
    grasp_z_offset:
      type: scalar
      range:
      - 0.02
      - 0.06
      default: 0.04
      binds_to:
      - path: target.offset.z
        mode: replace
- id: grasp_phase
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
    tolerance: 0.02
  parameters:
    grasp_time:
      type: scalar
      range:
      - 0.2
      - 1.0
      default: 0.5
      binds_to:
      - path: duration.max_time
        mode: replace
  guards:
  - id: check_grasp
    when: after_phase
    predicate: bilateral_grasp
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: repeat
- id: lift_obj
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
    tolerance: 0.02
  parameters:
    lift_z_offset:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
- id: approach_goal
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
  parameters:
    approach_goal_z_offset:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
- id: descend_place
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
  parameters:
    place_z_offset:
      type: scalar
      range:
      - -0.05
      - 0.0
      default: -0.03
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: place_subtask

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_obj** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.12], tolerance=0.02
  - parameter_bindings:
    - pre_grasp_z_offset: status=consumed; consumers=target.offset.z (replace)
- **descend_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - parameter_bindings:
    - grasp_z_offset: status=consumed; consumers=target.offset.z (replace)
- **grasp_phase** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - parameter_bindings:
    - grasp_time: status=consumed; consumers=duration.max_time (replace)
  - guards:
    - id=check_grasp, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=repeat
- **lift_obj** (`lift`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - parameter_bindings:
    - lift_z_offset: status=consumed; consumers=target.offset.z (replace)
- **approach_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - parameter_bindings:
    - approach_goal_z_offset: status=consumed; consumers=target.offset.z (replace)
- **descend_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - parameter_bindings:
    - place_z_offset: status=consumed; consumers=target.offset.z (replace)

## Design Metrics

- **Composite score**: 0.125
- **task_score** (E): 0.306
- **fitness_score**: 0.625  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.500

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_obj | 1.00 | 1.00 | 0.1756 |
| descend_grasp | 1.00 | 1.00 | 0.0839 |
| grasp_phase | 1.00 | 1.00 | 0.0126 |
| lift_obj | 1.00 | 1.00 | 0.1673 |
| approach_goal | 0.67 | 1.00 | 0.2505 |
| descend_place | 1.00 | 1.00 | 0.1603 |
| release_obj | 1.00 | 1.00 | 0.0201 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_obj | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.516, -0.001, 0.130) | (0.522, -0.001, 0.030)→(0.522, -0.001, 0.026) | 0.287→0.289 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_grasp | descend | 1.00 / step_budget | (0.516, -0.001, 0.130)→(0.516, -0.001, 0.047) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_phase | grasp | 1.00 / step_budget | (0.516, -0.001, 0.047)→(0.508, -0.001, 0.037) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.290 | 1.00 / 43.000 | 0.142 | 0.172 |
| lift_obj | lift | 1.00 / step_budget | (0.508, -0.001, 0.037)→(0.517, -0.001, 0.204) | (0.522, -0.001, 0.026)→(0.530, -0.001, 0.189) | 0.290→0.228 | 1.00 / 37.000 | 0.080 | 0.550 |
| approach_goal | approach | 0.67 / step_budget | (0.517, -0.001, 0.204)→(0.599, 0.185, 0.346) | (0.530, -0.001, 0.189)→(0.608, 0.189, 0.326) | 0.228→0.124 | 1.00 / 40.667 | 0.071 | 0.153 |
| descend_place | descend | 1.00 / step_budget | (0.599, 0.185, 0.346)→(0.604, 0.203, 0.187) | (0.608, 0.189, 0.326)→(0.610, 0.207, 0.164) | 0.124→0.041 | 1.00 / 38.667 | 0.048 | 0.246 |
| release_obj | release | 1.00 / step_budget | (0.604, 0.203, 0.187)→(0.598, 0.201, 0.206) | (0.610, 0.207, 0.164)→(0.598, 0.201, 0.025) | 0.041→0.180 | 1.00 / 2.000 | 0.167 | 1.406 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.373
- phase_score: 0.642
- phase_breakdown.place_subtask_score: 0.634
- phase_breakdown.approach_subtask_score: 0.677
- grasp_place_fitness: 0.657

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.657
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.373
- **Median Q (composite search score)**: 0.120
- **K-run variance**: 0.0006
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.492


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.92147,"average_solve_count":191.0,"average_success_count":191.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_z_offset":0.14873,"approach_obj.pre_grasp_z_offset":0.10986,"descend_grasp.grasp_z_offset":0.02004,"descend_place.place_z_offset":-0.02389,"grasp_phase.grasp_time":0.45117,"lift_obj.lift_z_offset":0.24643,"release_obj.release_time":0.25844},"optimized_scores":{"best_composite_score":0.09748,"best_fitness_score":0.59748,"best_task_score":0.24805},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":176.0,"contact_point_centroid":[0.56294,0.21992,-0.00818],"force_p95":1.4878,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.6004,"mean_force":0.43484,"phase_index":6.0,"phase_name":"release_obj","phase_type":"release","tcp_position_centroid":[0.57316,0.22389,0.23785]},{"body_a":"world","body_b":"grasp_target","contact_count":76.0,"contact_point_centroid":[0.47964,0.04705,-0.00143],"force_p95":0.47523,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55502,"mean_force":0.12374,"phase_index":3.0,"phase_name":"lift_obj","phase_type":"lift","tcp_position_centroid":[0.46859,0.0471,0.03761]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11620.0,"contact_point_centroid":[0.47208,0.06644,0.14626],"force_p95":0.08612,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32454,"mean_force":0.06004,"phase_index":3.0,"phase_name":"lift_obj","phase_type":"lift","tcp_position_centroid":[0.47242,0.04723,0.14363]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14493.0,"contact_point_centroid":[0.47424,0.02831,0.14421],"force_p95":0.08157,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29635,"mean_force":0.04982,"phase_index":3.0,"phase_name":"lift_obj","phase_type":"lift","tcp_position_centroid":[0.47236,0.04722,0.14258]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5067.0,"contact_point_centroid":[0.56985,0.23974,0.30044],"force_p95":0.07189,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27659,"mean_force":0.04937,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.57597,0.22173,0.29618]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48276,0.04871,-0.00213],"force_p95":0.15768,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21354,"mean_force":0.13199,"phase_index":2.0,"phase_name":"grasp_phase","phase_type":"grasp","tcp_position_centroid":[0.47084,0.04734,0.03738]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1166.0,"contact_point_centroid":[0.5703,0.24327,0.22477],"force_p95":0.07232,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20636,"mean_force":0.04633,"phase_index":6.0,"phase_name":"release_obj","phase_type":"release","tcp_position_centroid":[0.57618,0.22521,0.22064]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1406.0,"contact_point_centroid":[0.58185,0.20673,0.2212],"force_p95":0.0675,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19253,"mean_force":0.04016,"phase_index":6.0,"phase_name":"release_obj","phase_type":"release","tcp_position_centroid":[0.57618,0.2252,0.22064]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5871.0,"contact_point_centroid":[0.58156,0.20321,0.29826],"force_p95":0.06774,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18589,"mean_force":0.04393,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.57595,0.22169,0.29687]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5259.0,"contact_point_centroid":[0.47117,0.02821,0.03741],"force_p95":0.07311,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18286,"mean_force":0.04136,"phase_index":2.0,"phase_name":"grasp_phase","phase_type":"grasp","tcp_position_centroid":[0.46964,0.04722,0.03615]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14449.0,"contact_point_centroid":[0.5327,0.11814,0.31034],"force_p95":0.07871,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16174,"mean_force":0.05088,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52802,0.1366,0.30891]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12256.0,"contact_point_centroid":[0.5245,0.15524,0.31225],"force_p95":0.08243,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1465,"mean_force":0.05775,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.528,0.13655,0.30887]},{"body_a":"world","body_b":"grasp_target","contact_count":1128.0,"contact_point_centroid":[0.4827,0.04873,-0.00188],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12306,"phase_index":0.0,"phase_name":"approach_obj","phase_type":"approach","tcp_position_centroid":[0.49058,0.01987,0.23025]},{"body_a":"world","body_b":"grasp_target","contact_count":2560.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.47822,0.04478,0.09591]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4210.0,"contact_point_centroid":[0.46945,0.06654,0.03857],"force_p95":0.08824,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0955,"mean_force":0.05199,"phase_index":2.0,"phase_name":"grasp_phase","phase_type":"grasp","tcp_position_centroid":[0.46964,0.04723,0.03615]}],"total_contact_groups":15},"final_pose_error":0.01969,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.57282,0.22311,0.02164],"final_tcp_position":[0.57807,0.22595,0.22569],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":1.6004,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":283.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_obj","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1128.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_subtask","tcp_end":[0.4819,0.04135,0.15795],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13214,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":640.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2560.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.47769,0.04801,0.04444],"tcp_start":[0.4819,0.04135,0.15795],"tcp_to_object_dist_end":0.0191,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48271,0.04797,0.02556],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29077,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.15545,"phase_name":"grasp_phase","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11269.0,"raw_peak_contact_force":0.21354,"tcp_end":[0.46961,0.04722,0.03612],"tcp_start":[0.47769,0.04801,0.04444],"tcp_to_object_dist_end":0.01684,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":683.0,"n_steps_budget":1000.0,"object_pos_end":[0.49134,0.04864,0.23791],"object_pos_start":[0.48271,0.04797,0.02556],"object_to_goal_dist_end":0.20182,"object_to_goal_dist_start":0.29077,"object_z_max":0.23763,"peak_contact_force":0.08209,"phase_name":"lift_obj","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":26189.0,"raw_peak_contact_force":0.55502,"tcp_end":[0.47918,0.04764,0.25239],"tcp_start":[0.46961,0.04722,0.03612],"tcp_to_object_dist_end":0.01894,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":700.0,"n_steps_budget":1000.0,"object_pos_end":[0.58047,0.22089,0.34484],"object_pos_start":[0.49134,0.04864,0.23791],"object_to_goal_dist_end":0.11464,"object_to_goal_dist_start":0.20182,"object_z_max":0.34471,"peak_contact_force":0.06834,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":26705.0,"raw_peak_contact_force":0.16174,"tcp_end":[0.57463,0.21793,0.36432],"tcp_start":[0.47918,0.04764,0.25239],"tcp_to_object_dist_end":0.02055,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":245.0,"n_steps_budget":1000.0,"object_pos_end":[0.58112,0.22885,0.20399],"object_pos_start":[0.58047,0.22089,0.34484],"object_to_goal_dist_end":0.02651,"object_to_goal_dist_start":0.11464,"object_z_max":0.34484,"peak_contact_force":0.06833,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10938.0,"raw_peak_contact_force":0.27659,"subtask_id":"place_subtask","tcp_end":[0.57807,0.22595,0.22569],"tcp_start":[0.57463,0.21793,0.36432],"tcp_to_object_dist_end":0.02211,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57282,0.22311,0.02164],"object_pos_start":[0.58112,0.22885,0.20399],"object_to_goal_dist_end":0.20912,"object_to_goal_dist_start":0.02651,"object_z_max":0.20399,"peak_contact_force":0.14053,"phase_name":"release_obj","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2748.0,"raw_peak_contact_force":1.6004,"tcp_end":[0.57312,0.22388,0.2455],"tcp_start":[0.57807,0.22595,0.22569],"tcp_to_object_dist_end":0.22386,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.83,"average_solve_count":200.0,"average_success_count":200.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_z_offset":0.20096,"approach_obj.pre_grasp_z_offset":0.05239,"descend_grasp.grasp_z_offset":0.02569,"descend_place.place_z_offset":-0.04425,"grasp_phase.grasp_time":0.88931,"lift_obj.lift_z_offset":0.13767,"release_obj.release_time":0.37698},"optimized_scores":{"best_composite_score":0.11973,"best_fitness_score":0.61973,"best_task_score":0.29634},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":181.0,"contact_point_centroid":[0.59514,0.21697,-0.00763],"force_p95":1.24941,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.41172,"mean_force":0.4034,"phase_index":6.0,"phase_name":"release_obj","phase_type":"release","tcp_position_centroid":[0.59926,0.21857,0.19069]},{"body_a":"world","body_b":"grasp_target","contact_count":76.0,"contact_point_centroid":[0.53373,-0.02114,-0.00134],"force_p95":0.47405,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54592,"mean_force":0.12656,"phase_index":3.0,"phase_name":"lift_obj","phase_type":"lift","tcp_position_centroid":[0.52223,-0.02101,0.03884]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1052.0,"contact_point_centroid":[0.60017,0.23892,0.17981],"force_p95":0.08642,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34522,"mean_force":0.05352,"phase_index":6.0,"phase_name":"release_obj","phase_type":"release","tcp_position_centroid":[0.60284,0.22006,0.17539]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7941.0,"contact_point_centroid":[0.52632,-0.00207,0.09203],"force_p95":0.07606,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31893,"mean_force":0.05016,"phase_index":3.0,"phase_name":"lift_obj","phase_type":"lift","tcp_position_centroid":[0.52552,-0.02116,0.09003]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6945.0,"contact_point_centroid":[0.52523,-0.04035,0.09222],"force_p95":0.08037,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31281,"mean_force":0.05579,"phase_index":3.0,"phase_name":"lift_obj","phase_type":"lift","tcp_position_centroid":[0.52542,-0.02115,0.08933]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1180.0,"contact_point_centroid":[0.61142,0.20264,0.17598],"force_p95":0.08013,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30214,"mean_force":0.04907,"phase_index":6.0,"phase_name":"release_obj","phase_type":"release","tcp_position_centroid":[0.60283,0.22006,0.17538]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5067.0,"contact_point_centroid":[0.59611,0.21986,0.2737],"force_p95":0.09826,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19776,"mean_force":0.06361,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.59943,0.20122,0.27044]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5284.0,"contact_point_centroid":[0.60717,0.18413,0.2687],"force_p95":0.0989,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16601,"mean_force":0.06242,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.59956,0.20167,0.26828]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53702,-0.02143,-0.00203],"force_p95":0.13408,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15114,"mean_force":0.12564,"phase_index":2.0,"phase_name":"grasp_phase","phase_type":"grasp","tcp_position_centroid":[0.52438,-0.02104,0.03906]},{"body_a":"world","body_b":"grasp_target","contact_count":1564.0,"contact_point_centroid":[0.53702,-0.02132,-0.00191],"force_p95":0.13468,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12294,"phase_index":0.0,"phase_name":"approach_obj","phase_type":"approach","tcp_position_centroid":[0.51341,-0.00921,0.20117]},{"body_a":"world","body_b":"grasp_target","contact_count":3392.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.52892,-0.02025,0.06645]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18228.0,"contact_point_centroid":[0.56684,0.06886,0.25543],"force_p95":0.07927,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12074,"mean_force":0.05496,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.56353,0.08766,0.25361]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19194.0,"contact_point_centroid":[0.55997,0.10122,0.25038],"force_p95":0.07687,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10888,"mean_force":0.0524,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.56182,0.08239,0.24809]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5333.0,"contact_point_centroid":[0.52391,-0.00195,0.03965],"force_p95":0.06846,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10003,"mean_force":0.04118,"phase_index":2.0,"phase_name":"grasp_phase","phase_type":"grasp","tcp_position_centroid":[0.52311,-0.02102,0.03759]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4151.0,"contact_point_centroid":[0.52241,-0.04028,0.04061],"force_p95":0.08055,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08754,"mean_force":0.05174,"phase_index":2.0,"phase_name":"grasp_phase","phase_type":"grasp","tcp_position_centroid":[0.52311,-0.02102,0.03759]}],"total_contact_groups":15},"final_pose_error":0.01967,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.59655,0.21913,0.0257],"final_tcp_position":[0.60516,0.22069,0.18078],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":1.41172,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":392.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_obj","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1564.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_subtask","tcp_end":[0.52907,-0.01894,0.10018],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.07463,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":848.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3392.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53155,-0.02115,0.04744],"tcp_start":[0.52907,-0.01894,0.10018],"tcp_to_object_dist_end":0.02211,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53691,-0.02145,0.02586],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31694,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.1342,"phase_name":"grasp_phase","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11284.0,"raw_peak_contact_force":0.15114,"tcp_end":[0.52307,-0.02102,0.03756],"tcp_start":[0.53155,-0.02115,0.04744],"tcp_to_object_dist_end":0.01812,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":369.0,"n_steps_budget":810.0,"object_pos_end":[0.54409,-0.02185,0.13059],"object_pos_start":[0.53691,-0.02145,0.02586],"object_to_goal_dist_end":0.26943,"object_to_goal_dist_start":0.31694,"object_z_max":0.13034,"peak_contact_force":0.0796,"phase_name":"lift_obj","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":14962.0,"raw_peak_contact_force":0.54592,"tcp_end":[0.53157,-0.02134,0.14445],"tcp_start":[0.52307,-0.02102,0.03756],"tcp_to_object_dist_end":0.01869,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.60585,0.18789,0.33589],"object_pos_start":[0.54409,-0.02185,0.13059],"object_to_goal_dist_end":0.1346,"object_to_goal_dist_start":0.26943,"object_z_max":0.33569,"peak_contact_force":0.07009,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":37422.0,"raw_peak_contact_force":0.12074,"tcp_end":[0.59507,0.18404,0.35468],"tcp_start":[0.53157,-0.02134,0.14445],"tcp_to_object_dist_end":0.022,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":36.0,"n_steps":316.0,"n_steps_budget":1000.0,"object_pos_end":[0.61229,0.22508,0.15822],"object_pos_start":[0.60585,0.18789,0.33589],"object_to_goal_dist_end":0.04931,"object_to_goal_dist_start":0.1346,"object_z_max":0.33599,"peak_contact_force":0.0,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10351.0,"raw_peak_contact_force":0.19776,"subtask_id":"place_subtask","tcp_end":[0.60516,0.22069,0.18078],"tcp_start":[0.59507,0.18404,0.35468],"tcp_to_object_dist_end":0.02406,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59655,0.21913,0.0257],"object_pos_start":[0.61229,0.22508,0.15822],"object_to_goal_dist_end":0.18244,"object_to_goal_dist_start":0.04931,"object_z_max":0.15822,"peak_contact_force":0.18332,"phase_name":"release_obj","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2413.0,"raw_peak_contact_force":1.41172,"tcp_end":[0.5992,0.21855,0.19973],"tcp_start":[0.60516,0.22069,0.18078],"tcp_to_object_dist_end":0.17405,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.92063,"average_solve_count":189.0,"average_success_count":189.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_z_offset":0.15641,"approach_obj.pre_grasp_z_offset":0.08641,"descend_grasp.grasp_z_offset":0.02646,"descend_place.place_z_offset":-0.04124,"grasp_phase.grasp_time":0.64902,"lift_obj.lift_z_offset":0.20995,"release_obj.release_time":0.29021},"optimized_scores":{"best_composite_score":0.15702,"best_fitness_score":0.65702,"best_task_score":0.37258},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":149.0,"contact_point_centroid":[0.62581,0.1606,-0.00833],"force_p95":1.13953,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.206,"mean_force":0.47448,"phase_index":6.0,"phase_name":"release_obj","phase_type":"release","tcp_position_centroid":[0.62169,0.16052,0.16232]},{"body_a":"world","body_b":"grasp_target","contact_count":79.0,"contact_point_centroid":[0.54273,-0.02868,-0.00135],"force_p95":0.45697,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.549,"mean_force":0.11381,"phase_index":3.0,"phase_name":"lift_obj","phase_type":"lift","tcp_position_centroid":[0.53053,-0.02873,0.03965]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10380.0,"contact_point_centroid":[0.53458,-0.04804,0.12941],"force_p95":0.08358,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33561,"mean_force":0.06022,"phase_index":3.0,"phase_name":"lift_obj","phase_type":"lift","tcp_position_centroid":[0.53441,-0.02885,0.12654]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12613.0,"contact_point_centroid":[0.53568,-0.00988,0.12652],"force_p95":0.07954,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32492,"mean_force":0.05146,"phase_index":3.0,"phase_name":"lift_obj","phase_type":"lift","tcp_position_centroid":[0.53428,-0.02885,0.12475]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1096.0,"contact_point_centroid":[0.62474,0.18084,0.15242],"force_p95":0.08522,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32073,"mean_force":0.05162,"phase_index":6.0,"phase_name":"release_obj","phase_type":"release","tcp_position_centroid":[0.62573,0.16168,0.14912]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1121.0,"contact_point_centroid":[0.63332,0.14366,0.15027],"force_p95":0.08431,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3135,"mean_force":0.0512,"phase_index":6.0,"phase_name":"release_obj","phase_type":"release","tcp_position_centroid":[0.62572,0.16168,0.1491]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5195.0,"contact_point_centroid":[0.62519,0.17678,0.24304],"force_p95":0.08868,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26219,"mean_force":0.05665,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62645,0.15774,0.23963]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4863.0,"contact_point_centroid":[0.6338,0.13983,0.23946],"force_p95":0.09043,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24395,"mean_force":0.06022,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.6265,0.15784,0.23775]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11681.0,"contact_point_centroid":[0.58583,0.04415,0.26714],"force_p95":0.09142,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17769,"mean_force":0.06273,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.58247,0.06294,0.26516]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13269.0,"contact_point_centroid":[0.58151,0.08039,0.26612],"force_p95":0.08299,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15878,"mean_force":0.05521,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5818,0.06153,0.26434]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5456,-0.02929,-0.00204],"force_p95":0.1358,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15029,"mean_force":0.12593,"phase_index":2.0,"phase_name":"grasp_phase","phase_type":"grasp","tcp_position_centroid":[0.5329,-0.0288,0.03984]},{"body_a":"world","body_b":"grasp_target","contact_count":1348.0,"contact_point_centroid":[0.5456,-0.02923,-0.0019],"force_p95":0.13563,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12299,"phase_index":0.0,"phase_name":"approach_obj","phase_type":"approach","tcp_position_centroid":[0.51689,-0.01234,0.21768]},{"body_a":"world","body_b":"grasp_target","contact_count":3584.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.53694,-0.02749,0.08174]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5312.0,"contact_point_centroid":[0.53254,-0.00971,0.04032],"force_p95":0.07161,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10533,"mean_force":0.0411,"phase_index":2.0,"phase_name":"grasp_phase","phase_type":"grasp","tcp_position_centroid":[0.53162,-0.02876,0.03833]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4158.0,"contact_point_centroid":[0.53212,-0.04805,0.04119],"force_p95":0.08316,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09598,"mean_force":0.05182,"phase_index":2.0,"phase_name":"grasp_phase","phase_type":"grasp","tcp_position_centroid":[0.53162,-0.02876,0.03833]}],"total_contact_groups":15},"final_pose_error":0.01974,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.62584,0.16162,0.02903],"final_tcp_position":[0.62829,0.16231,0.15471],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":1.206,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":338.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_obj","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1348.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_subtask","tcp_end":[0.53625,-0.02549,0.13329],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.10774,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":896.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3584.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.54013,-0.02899,0.04848],"tcp_start":[0.53625,-0.02549,0.13329],"tcp_to_object_dist_end":0.02312,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5455,-0.02919,0.02584],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26103,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.13581,"phase_name":"grasp_phase","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11270.0,"raw_peak_contact_force":0.15029,"tcp_end":[0.53159,-0.02876,0.03829],"tcp_start":[0.54013,-0.02899,0.04848],"tcp_to_object_dist_end":0.01867,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":610.0,"n_steps_budget":1000.0,"object_pos_end":[0.55321,-0.02971,0.19976],"object_pos_start":[0.5455,-0.02919,0.02584],"object_to_goal_dist_end":0.21154,"object_to_goal_dist_start":0.26103,"object_z_max":0.1995,"peak_contact_force":0.07924,"phase_name":"lift_obj","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":23072.0,"raw_peak_contact_force":0.549,"tcp_end":[0.54134,-0.02905,0.21634],"tcp_start":[0.53159,-0.02876,0.03829],"tcp_to_object_dist_end":0.0204,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":35.0,"n_steps":720.0,"n_steps_budget":1000.0,"object_pos_end":[0.63662,0.157,0.29803],"object_pos_start":[0.55321,-0.02971,0.19976],"object_to_goal_dist_end":0.12142,"object_to_goal_dist_start":0.21154,"object_z_max":0.29791,"peak_contact_force":0.07475,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":24950.0,"raw_peak_contact_force":0.17769,"tcp_end":[0.62581,0.15378,0.31847],"tcp_start":[0.54134,-0.02905,0.21634],"tcp_to_object_dist_end":0.02335,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":35.0,"n_steps":283.0,"n_steps_budget":1000.0,"object_pos_end":[0.63567,0.1656,0.13084],"object_pos_start":[0.63662,0.157,0.29803],"object_to_goal_dist_end":0.04617,"object_to_goal_dist_start":0.12142,"object_z_max":0.29803,"peak_contact_force":0.07457,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10058.0,"raw_peak_contact_force":0.26219,"subtask_id":"place_subtask","tcp_end":[0.62829,0.16231,0.15471],"tcp_start":[0.62581,0.15378,0.31847],"tcp_to_object_dist_end":0.0252,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.62584,0.16162,0.02903],"object_pos_start":[0.63567,0.1656,0.13084],"object_to_goal_dist_end":0.1481,"object_to_goal_dist_start":0.04617,"object_z_max":0.13084,"peak_contact_force":0.17807,"phase_name":"release_obj","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2366.0,"raw_peak_contact_force":1.206,"tcp_end":[0.62159,0.1605,0.17331],"tcp_start":[0.62829,0.16231,0.15471],"tcp_to_object_dist_end":0.14435,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```