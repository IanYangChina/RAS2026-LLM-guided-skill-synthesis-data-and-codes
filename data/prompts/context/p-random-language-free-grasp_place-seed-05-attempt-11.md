## Search State

- **Seed**: 5
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | contact_lost | pose_tolerance | 9 | 0.0294 | 0.39 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.1664 | 0.32 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 5 | 0.3836 | 0.52 | ✅ accepted |
| 8 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.0608 | 0.36 | ✅ accepted |
| 7 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.0416 | 0.32 | ❌ rejected |

**Proposal policy**: task_score is 0.39 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `ca83b0c5488ee900ee32f323a4fc38ffcc2f5381fd3d2b180044b561c962382d`
- Frozen object start: [0.530500292374538, 0.030794078973649372, 0.03]
- Frozen task target: [0.6015325561042142, 0.17858013800881417, 0.10808960535724847]
- Goal object position: (0.6015325561042142, 0.17858013800881417, 0.10808960535724847)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.6015325561042142, 0.17858013800881417, 0.10808960535724847)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.530500292374538, 0.030794078973649372, 0.03)
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
  frozen_object_start: [0.5305, 0.0308, 0.03]
  frozen_task_target: [0.6015, 0.1786, 0.1081]
  frozen_object_starts: {'grasp_target': [0.530500292374538, 0.030794078973649372, 0.03]}
  frozen_targets: {'place_target': [0.6015325561042142, 0.17858013800881417, 0.10808960535724847]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: ca83b0c5488ee900ee32f323a4fc38ffcc2f5381fd3d2b180044b561c962382d

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
| `object` | offset from object initial position (0.530500292374538, 0.030794078973649372, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.6015325561042142, 0.17858013800881417, 0.10808960535724847) | final destination targets |
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

## Current Skill (Q=0.029) — your mutation base

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
  - 0.1
  weight: 0.5
- id: reach_goal
  weight: 0.5
phases:
- id: approach_object
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
    approach_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 1
    strategy: repeat
  subtask_id: reach_object
- id: descend_to_object
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
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_object
- id: grasp_object
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
  guards:
  - id: grasp_contact
    when: during_phase
    predicate: bilateral_grasp
    threshold: 0.01
    on_failure: retry
  retries:
    max_attempts: 2
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
      distance: 0.1
      axis: world_z
      mode: add_to_offset
      sign: positive
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.12
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: lift_check
    when: after_phase
    predicate: object_lifted
    threshold: 0.05
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: repeat
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
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.02
      - 0.12
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=1, strategy=repeat
- **descend_to_object** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.03], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **grasp_object** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=grasp_contact, when=during_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.01
  - retries: max_attempts=2, strategy=repeat
- **lift_object** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.1, mode=add_to_offset, sign=positive}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=lift_check, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.05
  - retries: max_attempts=1, strategy=repeat
- **approach_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.029
- **task_score** (E): 0.394
- **fitness_score**: 0.659  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.630

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1658 |
| descend_to_object | 1.00 | 1.00 | 0.0846 |
| grasp_object | 0.00 | 1.00 | 0.0000 |
| lift_object | 0.00 | 1.00 | 0.1004 |
| transport_to_goal | 0.67 | 0.67 | 0.1128 |
| descend_to_place | 1.00 | 1.00 | 0.0849 |
| release_object | 1.00 | 1.00 | 0.0214 |
| retract | 1.00 | 1.00 | 0.1208 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.511, 0.017, 0.138) | (0.516, 0.018, 0.030)→(0.516, 0.018, 0.026) | 0.234→0.236 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_object | descend | 1.00 / step_budget | (0.511, 0.017, 0.138)→(0.511, 0.018, 0.053) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_object | grasp | 0.00 / guard_failure | (0.506, 0.018, 0.048)→(0.506, 0.018, 0.048) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 40.333 | 0.143 | 0.173 |
| lift_object | lift | 0.00 / step_budget | (0.506, 0.018, 0.048)→(0.502, 0.018, 0.148) | (0.516, 0.018, 0.026)→(0.506, 0.018, 0.119) | 0.236→0.204 | 1.00 / 32.333 | 0.093 | 0.405 |
| transport_to_goal | approach | 0.67 / step_budget | (0.514, 0.045, 0.175)→(0.575, 0.129, 0.218) | (0.506, 0.018, 0.119)→(0.581, 0.126, 0.134) | 0.204→0.119 | 0.67 / 15.333 | 55983.952 | 0.158 |
| descend_to_place | descend | 1.00 / step_budget | (0.575, 0.129, 0.218)→(0.594, 0.165, 0.166) | (0.581, 0.126, 0.133)→(0.590, 0.136, 0.069) | 0.120→0.109 | 1.00 / 13.667 | 55983.997 | 0.751 |
| release_object | release | 1.00 / step_budget | (0.594, 0.165, 0.166)→(0.588, 0.163, 0.187) | (0.590, 0.136, 0.069)→(0.576, 0.134, 0.023) | 0.109→0.157 | 1.00 / 4.000 | 0.130 | 0.667 |
| retract | retract | 1.00 / step_budget | (0.588, 0.163, 0.187)→(0.602, 0.177, 0.305) | (0.576, 0.134, 0.023)→(0.576, 0.134, 0.023) | 0.157→0.157 | 1.00 / 4.000 | 0.123 | 0.140 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.567
- phase_score: 0.516
- phase_breakdown.reach_goal_score: 0.823
- phase_breakdown.reach_object_score: 0.210
- grasp_place_fitness: 0.748

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.748
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.567
- **Median Q (composite search score)**: 0.057
- **K-run variance**: 0.0073
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.253


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `181fdad61feb8a6d3dd6561c82dc2730a5598964bf30fa08b43615687239c379`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `eed1fc17ff57094d5189888f0dc8540ea7c165c4c73333e7487a550c7ded377e`; realized-scene SHA-256: `ca83b0c5488ee900ee32f323a4fc38ffcc2f5381fd3d2b180044b561c962382d`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5305,0.03079,0.03]},{"name":"goal","value":[0.60153,0.17858,0.10809]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5305,0.03079,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.60153,0.17858,0.10809]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.00937,"average_solve_count":320.0,"average_success_count":320.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.0545,"descend_to_object.descend_speed":0.06912,"descend_to_place.place_speed":0.0272,"lift_object.lift_height":0.18826,"lift_object.lift_speed":0.06258,"retract.retract_height":0.14452,"retract.retract_speed":0.03921,"transport_to_goal.carry_height":0.1063,"transport_to_goal.transport_speed":0.06536},"optimized_scores":{"best_composite_score":0.11795,"best_fitness_score":0.74795,"best_task_score":0.56683},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":335.0,"contact_point_centroid":[0.58044,0.17416,-0.00334],"force_p95":0.71963,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.79969,"mean_force":0.20468,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.58913,0.17382,0.12362]},{"body_a":"world","body_b":"grasp_target","contact_count":193.0,"contact_point_centroid":[0.52647,0.02939,-0.00119],"force_p95":0.23255,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.42835,"mean_force":0.07483,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51867,0.02994,0.04816]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":548.0,"contact_point_centroid":[0.59742,0.1933,0.1063],"force_p95":0.12666,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35247,"mean_force":0.09162,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.59349,0.17526,0.11134]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":481.0,"contact_point_centroid":[0.59675,0.15694,0.10666],"force_p95":0.13712,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34975,"mean_force":0.10238,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.59349,0.17526,0.11133]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20468.0,"contact_point_centroid":[0.51638,0.04883,0.09713],"force_p95":0.07443,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30002,"mean_force":0.05022,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51624,0.02979,0.09602]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18334.0,"contact_point_centroid":[0.51529,0.01062,0.0995],"force_p95":0.07976,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2934,"mean_force":0.0547,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51623,0.02979,0.09843]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2724.0,"contact_point_centroid":[0.59716,0.19111,0.15827],"force_p95":0.1227,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24079,"mean_force":0.09078,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59404,0.17304,0.16248]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2372.0,"contact_point_centroid":[0.59605,0.15476,0.15845],"force_p95":0.13765,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21766,"mean_force":0.10215,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59407,0.17307,0.16206]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.53051,0.03066,-0.00208],"force_p95":0.14213,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18245,"mean_force":0.12888,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52105,0.0301,0.04706]},{"body_a":"world","body_b":"grasp_target","contact_count":1732.0,"contact_point_centroid":[0.57925,0.17422,-0.00198],"force_p95":0.12866,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14589,"mean_force":0.12272,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.59183,0.17503,0.18362]},{"body_a":"world","body_b":"grasp_target","contact_count":2328.0,"contact_point_centroid":[0.5305,0.03079,-0.00194],"force_p95":0.13103,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12284,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51083,0.01385,0.21801]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4955.0,"contact_point_centroid":[0.51985,0.01087,0.04821],"force_p95":0.07841,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1342,"mean_force":0.05224,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52053,0.03007,0.04647]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13081.0,"contact_point_centroid":[0.55239,0.11493,0.1706],"force_p95":0.10166,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13223,"mean_force":0.06511,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55127,0.09611,0.17146]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13966.0,"contact_point_centroid":[0.55206,0.07858,0.17113],"force_p95":0.09767,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12423,"mean_force":0.06197,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55197,0.09736,0.17197]},{"body_a":"world","body_b":"grasp_target","contact_count":3556.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.52364,0.0295,0.08252]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5910.0,"contact_point_centroid":[0.52068,0.04914,0.048],"force_p95":0.07062,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07956,"mean_force":0.04481,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52054,0.03007,0.04647]}],"total_contact_groups":16},"final_pose_error":0.01998,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.57924,0.17422,0.02602],"final_tcp_position":[0.59739,0.1771,0.23312],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":167951.73011,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":583.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2328.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.5242,0.02822,0.13703],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11122,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":889.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3556.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.52543,0.0304,0.05222],"tcp_start":[0.5242,0.02822,0.13703],"tcp_to_object_dist_end":0.02669,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53042,0.03015,0.02574],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18404,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.13941,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12669.0,"raw_peak_contact_force":0.18245,"tcp_end":[0.52051,0.03007,0.04644],"tcp_start":[0.52051,0.03007,0.04644],"tcp_to_object_dist_end":0.02295,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52139,0.03,0.12098],"object_pos_start":[0.53042,0.03013,0.02575],"object_to_goal_dist_end":0.16931,"object_to_goal_dist_start":0.18405,"object_z_max":0.12086,"peak_contact_force":0.08911,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":38995.0,"raw_peak_contact_force":0.42835,"tcp_end":[0.51639,0.0298,0.1479],"tcp_start":[0.52051,0.03007,0.04644],"tcp_to_object_dist_end":0.02739,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":898.0,"n_steps_budget":1000.0,"object_pos_end":[0.59593,0.17106,0.1704],"object_pos_start":[0.52139,0.03,0.12098],"object_to_goal_dist_end":0.06301,"object_to_goal_dist_start":0.16931,"object_z_max":0.17036,"peak_contact_force":167951.73011,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":27047.0,"raw_peak_contact_force":0.13223,"subtask_id":"reach_goal","tcp_end":[0.5945,0.17125,0.20341],"tcp_start":[0.51639,0.0298,0.1479],"tcp_to_object_dist_end":0.03304,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":15.0,"n_steps":269.0,"n_steps_budget":1000.0,"object_pos_end":[0.59975,0.17574,0.07972],"object_pos_start":[0.59593,0.17106,0.1704],"object_to_goal_dist_end":0.02857,"object_to_goal_dist_start":0.06301,"object_z_max":0.1704,"peak_contact_force":0.13711,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5096.0,"raw_peak_contact_force":0.24079,"subtask_id":"reach_goal","tcp_end":[0.59601,0.176,0.11571],"tcp_start":[0.5945,0.17125,0.20341],"tcp_to_object_dist_end":0.03619,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57882,0.17423,0.02638],"object_pos_start":[0.59975,0.17574,0.07972],"object_to_goal_dist_end":0.08492,"object_to_goal_dist_start":0.02857,"object_z_max":0.07972,"peak_contact_force":0.14526,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1364.0,"raw_peak_contact_force":0.79969,"tcp_end":[0.58899,0.17378,0.13591],"tcp_start":[0.59601,0.176,0.11571],"tcp_to_object_dist_end":0.11,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":433.0,"n_steps_budget":1000.0,"object_pos_end":[0.57924,0.17422,0.02602],"object_pos_start":[0.57882,0.17423,0.02638],"object_to_goal_dist_end":0.08515,"object_to_goal_dist_start":0.08492,"object_z_max":0.02638,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1732.0,"raw_peak_contact_force":0.14589,"tcp_end":[0.59739,0.1771,0.23312],"tcp_start":[0.58899,0.17378,0.13591],"tcp_to_object_dist_end":0.20791,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `5dcdc1a4e2a8d4c3bb30f9ac92fb306bea0b16a8f449f4d02b0333754e50f910`; realized-scene SHA-256: `584133b5261cffac0dd4282704ff39e97bf4d452e60b02507679bbdea5a4de22`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50382,-0.01567,0.03]},{"name":"goal","value":[0.58691,0.18745,0.24812]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.50382,-0.01567,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58691,0.18745,0.24812]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.28947,"average_solve_count":266.0,"average_success_count":266.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.0908,"descend_to_object.descend_speed":0.07294,"descend_to_place.place_speed":0.03996,"lift_object.lift_height":0.19661,"lift_object.lift_speed":0.05968,"retract.retract_height":0.15031,"retract.retract_speed":0.03837,"transport_to_goal.carry_height":0.11498,"transport_to_goal.transport_speed":0.08268},"optimized_scores":{"best_composite_score":-0.08618,"best_fitness_score":0.54382,"best_task_score":0.17111},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3964.0,"contact_point_centroid":[0.54592,0.0667,-0.00226],"force_p95":0.1253,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.76252,"mean_force":0.135,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.5471,0.11385,0.23114]},{"body_a":"world","body_b":"grasp_target","contact_count":202.0,"contact_point_centroid":[0.49974,-0.01422,-0.00124],"force_p95":0.22212,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.35995,"mean_force":0.06547,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49224,-0.01541,0.05314]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11955.0,"contact_point_centroid":[0.49019,0.00338,0.09605],"force_p95":0.10979,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32301,"mean_force":0.08045,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49,-0.01537,0.09857]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13410.0,"contact_point_centroid":[0.48978,-0.03395,0.09611],"force_p95":0.10247,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31015,"mean_force":0.07234,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49001,-0.01537,0.09871]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4322.0,"contact_point_centroid":[0.50719,0.03861,0.17785],"force_p95":0.13963,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20886,"mean_force":0.10649,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50378,0.02028,0.18223]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4981.0,"contact_point_centroid":[0.50663,0.00181,0.17753],"force_p95":0.12557,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.191,"mean_force":0.09249,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50361,0.01989,0.18185]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.50381,-0.01568,-0.00209],"force_p95":0.1458,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15202,"mean_force":0.1296,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49456,-0.01545,0.05175]},{"body_a":"world","body_b":"grasp_target","contact_count":1980.0,"contact_point_centroid":[0.50382,-0.01567,-0.00193],"force_p95":0.13308,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12287,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49889,-0.00698,0.21955]},{"body_a":"world","body_b":"grasp_target","contact_count":1936.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.49775,-0.01489,0.09463]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.54595,0.06669,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.56267,0.15026,0.23743]},{"body_a":"world","body_b":"grasp_target","contact_count":2116.0,"contact_point_centroid":[0.54595,0.06669,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.57193,0.16708,0.3174]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4822.0,"contact_point_centroid":[0.49521,0.00359,0.05097],"force_p95":0.09962,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10435,"mean_force":0.05658,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.4941,-0.01544,0.05123]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5591.0,"contact_point_centroid":[0.49422,-0.03425,0.05113],"force_p95":0.07658,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08387,"mean_force":0.04637,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.4941,-0.01544,0.05123]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4066.0,"contact_point_centroid":[0.54854,0.11614,0.2335],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01635,"mean_force":0.01039,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.54817,0.11613,0.23126]},{"body_a":"left_finger","body_b":"right_finger","contact_count":219.0,"contact_point_centroid":[0.56508,0.15097,0.23526],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01269,"mean_force":0.01012,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.5648,0.15096,0.23306]}],"total_contact_groups":15},"final_pose_error":0.01979,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.54595,0.06669,0.01602],"final_tcp_position":[0.58391,0.18394,0.37919],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":1.76252,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":496.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1980.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.49975,-0.01428,0.13899],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11305,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":484.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1936.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.49885,-0.01551,0.05649],"tcp_start":[0.49975,-0.01428,0.13899],"tcp_to_object_dist_end":0.03087,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50372,-0.01533,0.02557],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31235,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.14855,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12217.0,"raw_peak_contact_force":0.15202,"tcp_end":[0.49407,-0.01544,0.05121],"tcp_start":[0.49407,-0.01544,0.05121],"tcp_to_object_dist_end":0.02739,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4921,-0.01539,0.11581],"object_pos_start":[0.50372,-0.01534,0.02553],"object_to_goal_dist_end":0.26007,"object_to_goal_dist_start":0.31239,"object_z_max":0.1157,"peak_contact_force":0.10739,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":25567.0,"raw_peak_contact_force":0.35995,"tcp_end":[0.48996,-0.01536,0.14962],"tcp_start":[0.49407,-0.01544,0.05121],"tcp_to_object_dist_end":0.03388,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":591.0,"n_steps_budget":1000.0,"object_pos_end":[0.54256,0.05763,0.04796],"object_pos_start":[0.4921,-0.01539,0.11581],"object_to_goal_dist_end":0.24266,"object_to_goal_dist_start":0.26007,"object_z_max":0.18004,"peak_contact_force":0.0,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9303.0,"raw_peak_contact_force":0.20886,"subtask_id":"reach_goal","tcp_end":[0.52653,0.06756,0.23102],"tcp_start":[0.52645,0.06746,0.23095],"tcp_to_object_dist_end":0.18403,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54595,0.06669,0.01602],"object_pos_start":[0.54273,0.05767,0.04473],"object_to_goal_dist_end":0.26482,"object_to_goal_dist_start":0.24528,"object_z_max":0.04473,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8030.0,"raw_peak_contact_force":1.76252,"subtask_id":"reach_goal","tcp_end":[0.56593,0.15113,0.23564],"tcp_start":[0.52653,0.06756,0.23102],"tcp_to_object_dist_end":0.23614,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54595,0.06669,0.01602],"object_pos_start":[0.54595,0.06669,0.01602],"object_to_goal_dist_end":0.26482,"object_to_goal_dist_start":0.26482,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1019.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.56148,0.14986,0.25748],"tcp_start":[0.56593,0.15113,0.23564],"tcp_to_object_dist_end":0.25586,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":529.0,"n_steps_budget":1000.0,"object_pos_end":[0.54595,0.06669,0.01602],"object_pos_start":[0.54595,0.06669,0.01602],"object_to_goal_dist_end":0.26482,"object_to_goal_dist_start":0.26482,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2116.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58391,0.18394,0.37919],"tcp_start":[0.56148,0.14986,0.25748],"tcp_to_object_dist_end":0.38351,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `53da4dc33bcb1151bde99c46f4ec5d44dda63d23acc62ec623c12d4d0fb32574`; realized-scene SHA-256: `8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51251,0.03972,0.03]},{"name":"goal","value":[0.62757,0.17252,0.14502]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.51251,0.03972,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.62757,0.17252,0.14502]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.24351,"average_solve_count":308.0,"average_success_count":308.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.09241,"descend_to_object.descend_speed":0.03112,"descend_to_place.place_speed":0.05308,"lift_object.lift_height":0.21781,"lift_object.lift_speed":0.06191,"retract.retract_height":0.17769,"retract.retract_speed":0.0837,"transport_to_goal.carry_height":0.09723,"transport_to_goal.transport_speed":0.02479},"optimized_scores":{"best_composite_score":0.05654,"best_fitness_score":0.68654,"best_task_score":0.44332},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":277.0,"contact_point_centroid":[0.6032,0.16246,-0.00448],"force_p95":0.96127,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.07942,"mean_force":0.25082,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.61316,0.16573,0.15708]},{"body_a":"world","body_b":"grasp_target","contact_count":188.0,"contact_point_centroid":[0.50896,0.03813,-0.00118],"force_p95":0.23058,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.42684,"mean_force":0.07188,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.50111,0.03873,0.04807]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":433.0,"contact_point_centroid":[0.62101,0.18536,0.13854],"force_p95":0.15512,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.41765,"mean_force":0.11181,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.61722,0.16704,0.14348]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":658.0,"contact_point_centroid":[0.61998,0.14905,0.13896],"force_p95":0.12084,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.39812,"mean_force":0.07783,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.61735,0.16708,0.1437]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20421.0,"contact_point_centroid":[0.4989,0.05759,0.0969],"force_p95":0.07483,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30086,"mean_force":0.05032,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.4987,0.03854,0.09574]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18377.0,"contact_point_centroid":[0.49776,0.01938,0.0994],"force_p95":0.07981,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29128,"mean_force":0.05454,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49869,0.03854,0.09829]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2171.0,"contact_point_centroid":[0.61299,0.17581,0.1791],"force_p95":0.14461,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25053,"mean_force":0.10904,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60954,0.15745,0.18327]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2836.0,"contact_point_centroid":[0.61235,0.13954,0.17856],"force_p95":0.12558,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22789,"mean_force":0.08658,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60972,0.15766,0.18242]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.51253,0.03957,-0.00209],"force_p95":0.14393,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18523,"mean_force":0.12942,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.50341,0.03893,0.04691]},{"body_a":"world","body_b":"grasp_target","contact_count":2272.0,"contact_point_centroid":[0.60263,0.16234,-0.00197],"force_p95":0.13175,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.151,"mean_force":0.12242,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.61742,0.16812,0.23495]},{"body_a":"world","body_b":"grasp_target","contact_count":2088.0,"contact_point_centroid":[0.51251,0.03972,-0.00193],"force_p95":0.13221,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12286,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50278,0.01775,0.2188]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4952.0,"contact_point_centroid":[0.50222,0.01969,0.04812],"force_p95":0.07885,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13632,"mean_force":0.05224,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.50291,0.03888,0.04635]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14300.0,"contact_point_centroid":[0.54684,0.10897,0.17715],"force_p95":0.10403,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13172,"mean_force":0.0663,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5456,0.09016,0.17815]},{"body_a":"world","body_b":"grasp_target","contact_count":3752.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.50655,0.03821,0.07878]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15389.0,"contact_point_centroid":[0.54694,0.07263,0.17806],"force_p95":0.09784,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12215,"mean_force":0.06214,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54678,0.09139,0.17897]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5923.0,"contact_point_centroid":[0.50306,0.05796,0.04792],"force_p95":0.07104,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07198,"mean_force":0.04478,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.50291,0.03888,0.04635]}],"total_contact_groups":16},"final_pose_error":0.01983,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.60262,0.16234,0.02602],"final_tcp_position":[0.62452,0.17128,0.30316],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":167951.73011,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":523.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2088.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.50773,0.03626,0.13805],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11219,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":938.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3752.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.50767,0.03928,0.05171],"tcp_start":[0.50773,0.03626,0.13805],"tcp_to_object_dist_end":0.02615,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51243,0.039,0.02572],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21288,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.14087,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12679.0,"raw_peak_contact_force":0.18523,"tcp_end":[0.50288,0.03888,0.04632],"tcp_start":[0.50288,0.03888,0.04632],"tcp_to_object_dist_end":0.02271,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50394,0.03876,0.12069],"object_pos_start":[0.51243,0.03897,0.02573],"object_to_goal_dist_end":0.18376,"object_to_goal_dist_start":0.21289,"object_z_max":0.12058,"peak_contact_force":0.08105,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":38986.0,"raw_peak_contact_force":0.42684,"tcp_end":[0.49883,0.03856,0.1475],"tcp_start":[0.50288,0.03888,0.04632],"tcp_to_object_dist_end":0.02729,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.60492,0.14929,0.18454],"object_pos_start":[0.50394,0.03876,0.12069],"object_to_goal_dist_end":0.05113,"object_to_goal_dist_start":0.18376,"object_z_max":0.18447,"peak_contact_force":0.12622,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":29689.0,"raw_peak_contact_force":0.13172,"subtask_id":"reach_goal","tcp_end":[0.60274,0.1492,0.21815],"tcp_start":[0.49883,0.03856,0.1475],"tcp_to_object_dist_end":0.03368,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":258.0,"n_steps_budget":1000.0,"object_pos_end":[0.62338,0.16702,0.11254],"object_pos_start":[0.60492,0.14929,0.18454],"object_to_goal_dist_end":0.03321,"object_to_goal_dist_start":0.05113,"object_z_max":0.18454,"peak_contact_force":167951.73011,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5007.0,"raw_peak_contact_force":0.25053,"subtask_id":"reach_goal","tcp_end":[0.61952,0.16758,0.14804],"tcp_start":[0.60274,0.1492,0.21815],"tcp_to_object_dist_end":0.03571,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60445,0.16219,0.02645],"object_pos_start":[0.62338,0.16702,0.11254],"object_to_goal_dist_end":0.12125,"object_to_goal_dist_start":0.03321,"object_z_max":0.11254,"peak_contact_force":0.12176,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1368.0,"raw_peak_contact_force":1.07942,"tcp_end":[0.61309,0.1657,0.16743],"tcp_start":[0.61952,0.16758,0.14804],"tcp_to_object_dist_end":0.14129,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":568.0,"n_steps_budget":1000.0,"object_pos_end":[0.60262,0.16234,0.02602],"object_pos_start":[0.60445,0.16219,0.02645],"object_to_goal_dist_end":0.12202,"object_to_goal_dist_start":0.12125,"object_z_max":0.02662,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2272.0,"raw_peak_contact_force":0.151,"tcp_end":[0.62452,0.17128,0.30316],"tcp_start":[0.61309,0.1657,0.16743],"tcp_to_object_dist_end":0.27815,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```