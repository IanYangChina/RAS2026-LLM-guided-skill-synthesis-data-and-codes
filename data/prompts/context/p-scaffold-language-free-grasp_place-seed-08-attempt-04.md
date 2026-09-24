## Search State

- **Seed**: 8
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → descend → grasp → lift → push → grasp | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | impedance_control | position_control | time_limit | time_limit | grasp_success | pose_tolerance | pose_tolerance | time_limit | 7 | 0.2678 | 0.54 | ✅ accepted |
| 3 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 10 | -0.0818 | 0.26 | ❌ rejected |
| 2 | approach → descend → grasp → lift → approach → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 8 | 0.0682 | 0.30 | ❌ rejected |
| 1 | approach → descend → grasp → lift → push → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 8 | 0.0773 | 0.32 | ✅ accepted |
| 0 | approach → descend → grasp → lift → release | linear_cartesian | linear_cartesian | — | linear_cartesian | — | force_threshold_switch | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | time_limit | 2 | 0.3457 | 0.14 | ✅ accepted |

**Proposal policy**: task_score is 0.54 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.268) — your mutation base

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
  termination: grasp_success
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
  guards:
  - id: grasp_check
    when: after_phase
    predicate: bilateral_grasp
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
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
  type: push
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
  guards:
  - id: object_held
    when: during_phase
    predicate: object_lifted
    threshold: 0.05
    on_failure: abort
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
  - parameter_bindings: none
  - guards:
    - id=grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, -0.005]
- **lift_1** (`lift`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
- **transport_1** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.03], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
    - transport_xy_offset_x: status=consumed; consumers=target.offset.x (add)
    - transport_xy_offset_y: status=consumed; consumers=target.offset.y (add)
    - transport_z_offset_delta: status=consumed; consumers=target.offset.z (replace)
  - guards:
    - id=object_held, when=during_phase, predicate=object_lifted, on_failure=abort, threshold=0.05
- **hold_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.268
- **task_score** (E): 0.542
- **fitness_score**: 0.738  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.470

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1262 |
| descend_1 | 1.00 | 1.00 | 0.1427 |
| grasp_1 | 1.00 | 1.00 | 0.0088 |
| lift_1 | 1.00 | 1.00 | 0.1553 |
| transport_1 | 0.33 | 0.33 | 0.1961 |
| hold_1 | 1.00 | 1.00 | 0.0157 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / time_limit | (0.500, -0.000, 0.301)→(0.517, -0.000, 0.184) | (0.522, -0.001, 0.030)→(0.522, -0.001, 0.026) | 0.287→0.289 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / time_limit | (0.517, -0.000, 0.184)→(0.516, -0.001, 0.042) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 4.333 | 0.148 | 0.213 |
| grasp_1 | grasp | 1.00 / step_budget | (0.514, -0.001, 0.039)→(0.508, -0.001, 0.032) | (0.522, -0.001, 0.026)→(0.520, -0.001, 0.025) | 0.289→0.291 | 1.00 / 35.000 | 0.315 | 0.373 |
| lift_1 | lift | 1.00 / step_budget | (0.508, -0.001, 0.032)→(0.515, -0.001, 0.187) | (0.520, -0.001, 0.025)→(0.531, -0.001, 0.169) | 0.291→0.227 | 1.00 / 23.000 | 0.107 | 1.917 |
| transport_1 | push | 0.33 / guard_failure | (0.515, -0.001, 0.187)→(0.588, 0.176, 0.210) | (0.531, -0.001, 0.169)→(0.601, 0.183, 0.123) | 0.227→0.093 | 0.33 / 10.333 | 0.039 | 0.264 |
| hold_1 | grasp | 1.00 / step_budget | (0.595, 0.225, 0.232)→(0.590, 0.223, 0.218) | (0.598, 0.225, 0.209)→(0.593, 0.224, 0.192) | 0.027→0.041 | 1.00 / 31.000 | 0.095 | 0.275 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.763
- phase_score: 0.600
- phase_breakdown.transport_to_goal_score: 0.761
- phase_breakdown.reach_above_object_score: 0.478
- phase_breakdown.hold_at_goal_score: 0.724
- phase_breakdown.reach_object_score: 0.594
- phase_breakdown.lift_object_score: 0.317
- grasp_place_fitness: 0.854

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.854
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.763
- **Median Q (composite search score)**: 0.210
- **K-run variance**: 0.0068
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.378


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.05263,"average_solve_count":133.0,"average_success_count":133.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.08095,"descend_1.grasp_offset_z":-0.00765,"lift_1.lift_height":0.23348,"transport_1.transport_speed":0.61091,"transport_1.transport_xy_offset_x":0.024,"transport_1.transport_xy_offset_y":0.00993,"transport_1.transport_z_offset_delta":0.01108},"optimized_scores":{"best_composite_score":0.38419,"best_fitness_score":0.85419,"best_task_score":0.76332},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"left_finger","contact_count":47.0,"contact_point_centroid":[0.47635,0.01648,-0.00075],"force_p95":4.88174,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":4.93656,"mean_force":2.33397,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46871,0.04708,0.00839]},{"body_a":"world","body_b":"right_finger","contact_count":26.0,"contact_point_centroid":[0.47223,0.07877,-0.00019],"force_p95":3.05899,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3.29142,"mean_force":1.89593,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46902,0.04712,0.00789]},{"body_a":"world","body_b":"left_finger","contact_count":2160.0,"contact_point_centroid":[0.47687,0.01129,-0.00088],"force_p95":0.77412,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.80111,"mean_force":0.62758,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46947,0.04714,0.00799]},{"body_a":"world","body_b":"grasp_target","contact_count":212.0,"contact_point_centroid":[0.47569,0.04794,-0.00258],"force_p95":0.28594,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.70525,"mean_force":0.1428,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46748,0.04696,0.01495]},{"body_a":"grasp_target","body_b":"hand","contact_count":414.0,"contact_point_centroid":[0.49614,0.04125,0.10621],"force_p95":0.2508,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.54422,"mean_force":0.13447,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46757,0.04714,0.07306]},{"body_a":"grasp_target","body_b":"hand","contact_count":550.0,"contact_point_centroid":[0.49619,0.04961,0.0476],"force_p95":0.4311,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.43255,"mean_force":0.40709,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47026,0.04726,0.00878]},{"body_a":"grasp_target","body_b":"hand","contact_count":103.0,"contact_point_centroid":[0.50269,0.04614,0.05365],"force_p95":0.19773,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.39386,"mean_force":0.13292,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47739,0.04807,0.01955]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11356.0,"contact_point_centroid":[0.46946,0.06663,0.12307],"force_p95":0.09519,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34281,"mean_force":0.06218,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46913,0.04742,0.12057]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13649.0,"contact_point_centroid":[0.47159,0.0286,0.12468],"force_p95":0.08446,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32918,"mean_force":0.05242,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46921,0.04743,0.1235]},{"body_a":"world","body_b":"right_finger","contact_count":1421.0,"contact_point_centroid":[0.47221,0.08271,-0.00017],"force_p95":0.25858,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.27538,"mean_force":0.20671,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46928,0.0471,0.00781]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6277.0,"contact_point_centroid":[0.59556,0.20509,0.21937],"force_p95":0.11037,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2749,"mean_force":0.07204,"phase_index":5.0,"phase_name":"hold_1","phase_type":"grasp","tcp_position_centroid":[0.59063,0.22375,0.21992]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.48017,0.04855,-0.00346],"force_p95":0.25973,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.26224,"mean_force":0.22028,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47026,0.04726,0.00878]},{"body_a":"world","body_b":"grasp_target","contact_count":3332.0,"contact_point_centroid":[0.48268,0.04873,-0.00203],"force_p95":0.15297,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25671,"mean_force":0.12643,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47667,0.0473,0.05398]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7900.0,"contact_point_centroid":[0.59201,0.24243,0.22008],"force_p95":0.08126,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21551,"mean_force":0.05451,"phase_index":5.0,"phase_name":"hold_1","phase_type":"grasp","tcp_position_centroid":[0.59057,0.22372,0.21974]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6571.0,"contact_point_centroid":[0.54214,0.1226,0.23213],"force_p95":0.11935,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20895,"mean_force":0.0818,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.53642,0.14084,0.23295]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6099.0,"contact_point_centroid":[0.54139,0.16214,0.23368],"force_p95":0.11163,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19925,"mean_force":0.08112,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.53814,0.1433,0.23294]}],"total_contact_groups":17},"final_pose_error":0.01981,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.59337,0.22431,0.19191],"final_tcp_position":[0.59485,0.22513,0.23237],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":4.93656,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":897.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3584.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_above_object","tcp_end":[0.47908,0.04637,0.11333],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.08741,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":833.0,"n_steps_budget":1000.0,"object_pos_end":[0.48305,0.04874,0.02461],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29085,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.19985,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3435.0,"raw_peak_contact_force":0.39386,"subtask_id":"reach_object","tcp_end":[0.47743,0.04815,0.01585],"tcp_start":[0.47908,0.04637,0.11333],"tcp_to_object_dist_end":0.01042,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":13.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.47778,0.04854,0.02292],"object_pos_start":[0.48305,0.04874,0.02461],"object_to_goal_dist_end":0.294,"object_to_goal_dist_start":0.29085,"object_z_max":0.02461,"peak_contact_force":0.67583,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":6331.0,"raw_peak_contact_force":0.80111,"subtask_id":"reach_object","tcp_end":[0.46921,0.04714,0.00777],"tcp_start":[0.46922,0.04712,0.00777],"tcp_to_object_dist_end":0.01746,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":721.0,"n_steps_budget":1000.0,"object_pos_end":[0.49264,0.04935,0.23251],"object_pos_start":[0.47704,0.04854,0.02297],"object_to_goal_dist_end":0.20047,"object_to_goal_dist_start":0.29421,"object_z_max":0.23226,"peak_contact_force":0.10909,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":25704.0,"raw_peak_contact_force":4.93656,"subtask_id":"lift_object","tcp_end":[0.47372,0.04815,0.23675],"tcp_start":[0.46921,0.04714,0.00777],"tcp_to_object_dist_end":0.01942,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":31.0,"n_steps":508.0,"n_steps_budget":600.0,"object_pos_end":[0.59777,0.22528,0.20934],"object_pos_start":[0.49264,0.04935,0.23251],"object_to_goal_dist_end":0.02669,"object_to_goal_dist_start":0.20047,"object_z_max":0.23289,"peak_contact_force":0.11838,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":12670.0,"raw_peak_contact_force":0.20895,"subtask_id":"transport_to_goal","tcp_end":[0.59485,0.22513,0.23237],"tcp_start":[0.47372,0.04815,0.23675],"tcp_to_object_dist_end":0.02322,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":31.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59337,0.22431,0.19191],"object_pos_start":[0.59777,0.22528,0.20934],"object_to_goal_dist_end":0.04051,"object_to_goal_dist_start":0.02669,"object_z_max":0.20934,"peak_contact_force":0.09542,"phase_name":"hold_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":14177.0,"raw_peak_contact_force":0.2749,"subtask_id":"hold_at_goal","tcp_end":[0.58983,0.22339,0.21757],"tcp_start":[0.59485,0.22513,0.23237],"tcp_to_object_dist_end":0.02592,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.2233,"average_solve_count":103.0,"average_success_count":103.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.17444,"descend_1.grasp_offset_z":0.02722,"lift_1.lift_height":0.15664,"transport_1.transport_speed":0.32712,"transport_1.transport_xy_offset_x":0.00707,"transport_1.transport_xy_offset_y":0.02166,"transport_1.transport_z_offset_delta":0.03841},"optimized_scores":{"best_composite_score":0.20966,"best_fitness_score":0.67966,"best_task_score":0.42556},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":80.0,"contact_point_centroid":[0.53505,-0.02119,-0.00133],"force_p95":0.38478,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.43107,"mean_force":0.08874,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52225,-0.02104,0.04359]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7179.0,"contact_point_centroid":[0.52795,-0.00244,0.09586],"force_p95":0.10257,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27765,"mean_force":0.06299,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52496,-0.02117,0.09435]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4343.0,"contact_point_centroid":[0.56407,0.0518,0.1859],"force_p95":0.1502,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27525,"mean_force":0.09197,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.5586,0.07061,0.18554]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6071.0,"contact_point_centroid":[0.52741,-0.04025,0.09805],"force_p95":0.10815,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27235,"mean_force":0.07162,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52506,-0.02117,0.09553]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5063.0,"contact_point_centroid":[0.56511,0.08974,0.18528],"force_p95":0.12975,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26478,"mean_force":0.08348,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.55891,0.07154,0.18583]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53702,-0.02143,-0.00203],"force_p95":0.13355,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15092,"mean_force":0.12569,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52461,-0.02107,0.04377]},{"body_a":"world","body_b":"grasp_target","contact_count":3996.0,"contact_point_centroid":[0.53702,-0.02132,-0.00196],"force_p95":0.12459,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12275,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51604,-0.011,0.24528]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52993,-0.02046,0.11315]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5336.0,"contact_point_centroid":[0.52408,-0.00197,0.0443],"force_p95":0.06847,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1006,"mean_force":0.04119,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52335,-0.02105,0.0423]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4150.0,"contact_point_centroid":[0.52257,-0.0403,0.04523],"force_p95":0.08065,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08746,"mean_force":0.05174,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52335,-0.02105,0.0423]}],"total_contact_groups":10},"final_pose_error":0.05195,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.62028,0.21843,0.07999],"final_tcp_position":[0.6015,0.20494,0.22418],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":0.43107,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3996.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_above_object","tcp_end":[0.53033,-0.01947,0.20628],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.18039,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.5318,-0.02118,0.05226],"tcp_start":[0.53033,-0.01947,0.20628],"tcp_to_object_dist_end":0.02675,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53692,-0.02149,0.02586],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31697,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13366,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11286.0,"raw_peak_contact_force":0.15092,"subtask_id":"reach_object","tcp_end":[0.52332,-0.02105,0.04226],"tcp_start":[0.5318,-0.02118,0.05226],"tcp_to_object_dist_end":0.02131,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":421.0,"n_steps_budget":900.0,"object_pos_end":[0.54679,-0.02201,0.14066],"object_pos_start":[0.53692,-0.02149,0.02586],"object_to_goal_dist_end":0.26622,"object_to_goal_dist_start":0.31697,"object_z_max":0.14042,"peak_contact_force":0.10507,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":13330.0,"raw_peak_contact_force":0.43107,"subtask_id":"lift_object","tcp_end":[0.53185,-0.02139,0.16339],"tcp_start":[0.52332,-0.02105,0.04226],"tcp_to_object_dist_end":0.02721,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":485.0,"n_steps_budget":600.0,"object_pos_end":[0.62028,0.21843,0.07999],"object_pos_start":[0.54679,-0.02201,0.14066],"object_to_goal_dist_end":0.12815,"object_to_goal_dist_start":0.26622,"object_z_max":0.17807,"peak_contact_force":0.0,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":9406.0,"raw_peak_contact_force":0.27525,"subtask_id":"transport_to_goal","tcp_end":[0.6015,0.20494,0.22418],"tcp_start":[0.53185,-0.02139,0.16339],"tcp_to_object_dist_end":0.14603,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.0396,"average_solve_count":101.0,"average_success_count":101.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.20749,"descend_1.grasp_offset_z":0.01493,"lift_1.lift_height":0.15536,"transport_1.transport_speed":0.91091,"transport_1.transport_xy_offset_x":-0.04999,"transport_1.transport_xy_offset_y":-0.01995,"transport_1.transport_z_offset_delta":0.00998},"optimized_scores":{"best_composite_score":0.20966,"best_fitness_score":0.67966,"best_task_score":0.43738},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":80.0,"contact_point_centroid":[0.54372,-0.02875,-0.00136],"force_p95":0.33978,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.38424,"mean_force":0.08117,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5304,-0.02868,0.04834]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2797.0,"contact_point_centroid":[0.55567,0.00302,0.16375],"force_p95":0.14049,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30876,"mean_force":0.09067,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.55001,0.02192,0.16399]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5527.0,"contact_point_centroid":[0.53546,-0.04781,0.09621],"force_p95":0.11812,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26063,"mean_force":0.07557,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53324,-0.02874,0.09531]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6625.0,"contact_point_centroid":[0.53655,-0.01006,0.09505],"force_p95":0.11201,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2593,"mean_force":0.06578,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53311,-0.02874,0.0944]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3385.0,"contact_point_centroid":[0.55727,0.04283,0.16316],"force_p95":0.10176,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1842,"mean_force":0.07533,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.55064,0.02468,0.16429]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54561,-0.02924,-0.00205],"force_p95":0.13583,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16729,"mean_force":0.12641,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53274,-0.02874,0.04857]},{"body_a":"world","body_b":"grasp_target","contact_count":3996.0,"contact_point_centroid":[0.5456,-0.02923,-0.00196],"force_p95":0.12459,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12275,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52033,-0.01485,0.26277]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53889,-0.02843,0.13033]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5803.0,"contact_point_centroid":[0.53303,-0.00951,0.04925],"force_p95":0.06734,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09363,"mean_force":0.03801,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53148,-0.02871,0.04705]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5131.0,"contact_point_centroid":[0.53289,-0.04806,0.04951],"force_p95":0.07067,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08606,"mean_force":0.04298,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53148,-0.02871,0.04705]}],"total_contact_groups":10},"final_pose_error":0.05221,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.58536,0.10492,0.07929],"final_tcp_position":[0.56765,0.09705,0.17284],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":0.38424,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3996.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_above_object","tcp_end":[0.5403,-0.02783,0.23387],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.20792,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.53986,-0.02893,0.05722],"tcp_start":[0.5403,-0.02783,0.23387],"tcp_to_object_dist_end":0.03172,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":49.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54553,-0.02905,0.0258],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26094,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.13546,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12734.0,"raw_peak_contact_force":0.16729,"subtask_id":"reach_object","tcp_end":[0.53145,-0.02871,0.04702],"tcp_start":[0.53986,-0.02893,0.05722],"tcp_to_object_dist_end":0.02546,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":403.0,"n_steps_budget":840.0,"object_pos_end":[0.5531,-0.02889,0.13398],"object_pos_start":[0.54553,-0.02905,0.0258],"object_to_goal_dist_end":0.21393,"object_to_goal_dist_start":0.26094,"object_z_max":0.13374,"peak_contact_force":0.10801,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":12232.0,"raw_peak_contact_force":0.38424,"subtask_id":"lift_object","tcp_end":[0.54034,-0.02892,0.16199],"tcp_start":[0.53145,-0.02871,0.04702],"tcp_to_object_dist_end":0.03078,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":320.0,"n_steps_budget":600.0,"object_pos_end":[0.58536,0.10492,0.07929],"object_pos_start":[0.5531,-0.02889,0.13398],"object_to_goal_dist_end":0.12404,"object_to_goal_dist_start":0.21393,"object_z_max":0.13788,"peak_contact_force":0.0,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":6182.0,"raw_peak_contact_force":0.30876,"subtask_id":"transport_to_goal","tcp_end":[0.56765,0.09705,0.17284],"tcp_start":[0.54034,-0.02892,0.16199],"tcp_to_object_dist_end":0.09553,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```