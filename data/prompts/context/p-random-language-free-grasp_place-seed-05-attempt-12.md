## Search State

- **Seed**: 5
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 11 | -0.1602 | 0.21 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | contact_lost | pose_tolerance | 9 | 0.0294 | 0.39 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.1664 | 0.32 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 5 | 0.3836 | 0.52 | ✅ accepted |
| 8 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.0608 | 0.36 | ✅ accepted |

**Proposal policy**: task_score is 0.21 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.160) — your mutation base

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

- **Composite score**: -0.160
- **task_score** (E): 0.215
- **fitness_score**: 0.570  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.730

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1659 |
| descend_to_object | 1.00 | 1.00 | 0.0844 |
| grasp_object | 0.00 | 1.00 | 0.0000 |
| lift_object | 1.00 | 0.67 | 0.1319 |
| approach_goal | 0.00 | 1.00 | 0.2060 |
| descend_to_place | 0.00 | 1.00 | 0.0791 |
| release_object | 1.00 | 0.67 | 0.0259 |
| retract | 0.67 | 0.67 | 0.1088 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.511, 0.017, 0.138) | (0.516, 0.018, 0.030)→(0.516, 0.018, 0.026) | 0.234→0.236 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_object | descend | 1.00 / step_budget | (0.511, 0.017, 0.138)→(0.511, 0.018, 0.054) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_object | grasp | 0.00 / guard_failure | (0.506, 0.018, 0.048)→(0.506, 0.018, 0.048) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 39.333 | 0.141 | 0.173 |
| lift_object | lift | 1.00 / step_budget | (0.506, 0.018, 0.048)→(0.502, 0.018, 0.180) | (0.516, 0.018, 0.026)→(0.512, 0.016, 0.146) | 0.236→0.196 | 0.67 / 17.000 | 0.069 | 0.399 |
| approach_goal | approach | 0.00 / step_budget | (0.502, 0.018, 0.180)→(0.571, 0.097, 0.170) | (0.512, 0.016, 0.146)→(0.563, 0.097, -6.372) | 0.196→6.571 | 1.00 / 24.667 | 56966.355 | 1504.016 |
| descend_to_place | descend | 0.00 / step_budget | (0.571, 0.097, 0.170)→(0.619, 0.129, 0.207) | (0.563, 0.097, -6.372)→(0.601, 0.115, -25.844) | 6.571→26.043 | 1.00 / 26.000 | 94251.481 | 968.805 |
| release_object | release | 1.00 / step_budget | (0.619, 0.129, 0.207)→(0.618, 0.129, 0.233) | (0.601, 0.115, -25.844)→(0.609, 0.119, -31.307) | 26.043→31.506 | 0.67 / 20.667 | 0.041 | 122.269 |
| retract | retract | 0.67 / step_budget | (0.618, 0.129, 0.233)→(0.618, 0.129, 0.342) | (0.609, 0.119, -31.307)→(0.626, 0.137, -53.163) | 31.506→53.362 | 0.67 / 22.333 | 91005.405 | 0.305 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 0.000
- terminal_score: 0.530
- phase_score: 0.116
- phase_breakdown.reach_goal_score: 0.022
- phase_breakdown.reach_object_score: 0.211
- grasp_place_fitness: 0.730

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.730
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.530
- **Median Q (composite search score)**: -0.215
- **K-run variance**: 0.0132
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.266


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.0117,"average_solve_count":171.0,"average_success_count":171.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.carry_height":0.10054,"approach_goal.transport_speed":0.05718,"approach_object.approach_speed":0.09991,"descend_to_object.descend_speed":0.05875,"descend_to_place.place_speed":0.07291,"descend_to_place.place_z_offset":-0.01375,"lift_object.lift_height":0.14013,"lift_object.lift_speed":0.09717,"release_object.release_timeout":0.18949,"retract.retract_height":0.14229,"retract.retract_speed":0.0905},"optimized_scores":{"best_composite_score":-0.00048,"best_fitness_score":0.72952,"best_task_score":0.53031},"replay_outcomes":[{"contacts":{"omitted_contact_groups":12,"reported_contact_groups":[{"body_a":"world","body_b":"hand","contact_count":36.0,"contact_point_centroid":[0.67414,0.12822,-0.00456],"force_p95":1373.08868,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1880.65237,"mean_force":513.15086,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.59026,0.09672,0.03152]},{"body_a":"world","body_b":"link6","contact_count":834.0,"contact_point_centroid":[0.5436,0.25372,-0.00036],"force_p95":305.56045,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1377.40204,"mean_force":282.19288,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53146,0.19319,0.28138]},{"body_a":"world","body_b":"link6","contact_count":987.0,"contact_point_centroid":[0.54162,0.21878,-0.00032],"force_p95":487.07108,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":593.87464,"mean_force":373.2519,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.54682,0.20035,0.2931]},{"body_a":"world","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.61526,0.17654,-5e-05],"force_p95":497.68499,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":500.17744,"mean_force":325.14346,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.61028,0.06849,0.11597]},{"body_a":"world","body_b":"link6","contact_count":81.0,"contact_point_centroid":[0.55946,0.2186,-0.00016],"force_p95":84.66229,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":93.90352,"mean_force":61.22526,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.55308,0.19913,0.29314]},{"body_a":"world","body_b":"left_finger","contact_count":75.0,"contact_point_centroid":[0.59089,0.11806,-0.00214],"force_p95":20.04891,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":20.70957,"mean_force":15.3316,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.58226,0.12027,0.0083]},{"body_a":"grasp_target","body_b":"link7","contact_count":30.0,"contact_point_centroid":[0.59762,0.19347,0.032],"force_p95":3.15338,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.18084,"mean_force":1.52297,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.61024,0.0722,0.11995]},{"body_a":"world","body_b":"grasp_target","contact_count":2240.0,"contact_point_centroid":[0.59483,0.20525,-0.0041],"force_p95":0.65736,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.04404,"mean_force":0.28458,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53753,0.18361,0.25802]},{"body_a":"grasp_target","body_b":"link6","contact_count":791.0,"contact_point_centroid":[0.58956,0.23378,0.03817],"force_p95":0.28948,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.37367,"mean_force":0.24212,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52949,0.19478,0.28175]},{"body_a":"grasp_target","body_b":"link6","contact_count":1000.0,"contact_point_centroid":[0.59194,0.19799,0.03005],"force_p95":0.3434,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.19328,"mean_force":0.28462,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.54669,0.20035,0.29308]},{"body_a":"world","body_b":"grasp_target","contact_count":2198.0,"contact_point_centroid":[0.61201,0.18923,-0.00413],"force_p95":0.42289,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.36072,"mean_force":0.28835,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.54589,0.2008,0.29309]},{"body_a":"left_finger","body_b":"right_finger","contact_count":49719.0,"contact_point_centroid":[0.53697,0.18574,0.26638],"force_p95":0.73636,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.81465,"mean_force":0.35669,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53678,0.18512,0.26812]},{"body_a":"left_finger","body_b":"right_finger","contact_count":49558.0,"contact_point_centroid":[0.5535,0.20047,0.38194],"force_p95":0.7585,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.79106,"mean_force":0.38131,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.55319,0.20029,0.38394]},{"body_a":"left_finger","body_b":"right_finger","contact_count":10967.0,"contact_point_centroid":[0.55326,0.19949,0.29789],"force_p95":0.75174,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.78497,"mean_force":0.37542,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.55302,0.19931,0.2999]},{"body_a":"left_finger","body_b":"right_finger","contact_count":54522.0,"contact_point_centroid":[0.5468,0.20049,0.29109],"force_p95":0.73778,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.76335,"mean_force":0.35896,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.5467,0.20035,0.29308]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":637.0,"contact_point_centroid":[0.56331,0.04681,0.16106],"force_p95":0.44154,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.60916,"mean_force":0.23272,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55475,0.06335,0.1637]}],"total_contact_groups":28},"final_pose_error":0.01226,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.62117,0.19235,0.01602],"final_tcp_position":[0.55363,0.20092,0.45069],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":273016.093,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":535.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2136.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.52426,0.02818,0.13729],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11147,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":941.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3764.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.52543,0.03039,0.05235],"tcp_start":[0.52426,0.02818,0.13729],"tcp_to_object_dist_end":0.02681,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53042,0.03015,0.02574],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18404,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.13952,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12669.0,"raw_peak_contact_force":0.18256,"tcp_end":[0.52052,0.03007,0.04657],"tcp_start":[0.52052,0.03007,0.04657],"tcp_to_object_dist_end":0.02307,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":813.0,"n_steps_budget":900.0,"object_pos_end":[0.52697,0.03006,0.14686],"object_pos_start":[0.53042,0.03012,0.02575],"object_to_goal_dist_end":0.17064,"object_to_goal_dist_start":0.18405,"object_z_max":0.14675,"peak_contact_force":0.10488,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":28510.0,"raw_peak_contact_force":0.42201,"tcp_end":[0.51675,0.02982,0.17432],"tcp_start":[0.52052,0.03007,0.04657],"tcp_to_object_dist_end":0.0293,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":58.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.59841,0.20688,0.01602],"object_pos_start":[0.52697,0.03006,0.14686],"object_to_goal_dist_end":0.09637,"object_to_goal_dist_start":0.17064,"object_z_max":0.14696,"peak_contact_force":167951.73011,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":54929.0,"raw_peak_contact_force":1880.65237,"subtask_id":"reach_goal","tcp_end":[0.53572,0.19556,0.28837],"tcp_start":[0.51675,0.02982,0.17432],"tcp_to_object_dist_end":0.27971,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":63.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.62175,0.19165,0.0163],"object_pos_start":[0.59841,0.20688,0.01602],"object_to_goal_dist_end":0.0949,"object_to_goal_dist_start":0.09637,"object_z_max":0.01649,"peak_contact_force":0.0,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":58707.0,"raw_peak_contact_force":593.87464,"subtask_id":"reach_goal","tcp_end":[0.55323,0.1988,0.29277],"tcp_start":[0.53572,0.19556,0.28837],"tcp_to_object_dist_end":0.28493,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":58.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.62816,0.1878,0.01884],"object_pos_start":[0.62175,0.19165,0.0163],"object_to_goal_dist_end":0.09359,"object_to_goal_dist_start":0.0949,"object_z_max":0.02078,"peak_contact_force":0.0,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":11598.0,"raw_peak_contact_force":93.90352,"tcp_end":[0.55307,0.19955,0.32057],"tcp_start":[0.55323,0.1988,0.29277],"tcp_to_object_dist_end":0.31116,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":63.0,"n_steps":903.0,"n_steps_budget":990.0,"object_pos_end":[0.62117,0.19235,0.01602],"object_pos_start":[0.62816,0.1878,0.01884],"object_to_goal_dist_end":0.09514,"object_to_goal_dist_start":0.09359,"object_z_max":0.01884,"peak_contact_force":273016.093,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":53138.0,"raw_peak_contact_force":0.79106,"tcp_end":[0.55363,0.20092,0.45069],"tcp_start":[0.55307,0.19955,0.32057],"tcp_to_object_dist_end":0.43997,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.59551,"average_solve_count":178.0,"average_success_count":178.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.carry_height":0.10218,"approach_goal.transport_speed":0.07951,"approach_object.approach_speed":0.10007,"descend_to_object.descend_speed":0.05849,"descend_to_place.place_speed":0.05789,"descend_to_place.place_z_offset":0.01739,"lift_object.lift_height":0.18444,"lift_object.lift_speed":0.11007,"release_object.release_timeout":0.18483,"retract.retract_height":0.22615,"retract.retract_speed":0.06845},"optimized_scores":{"best_composite_score":-0.2149,"best_fitness_score":0.5151,"best_task_score":0.11443},"replay_outcomes":[{"contacts":{"omitted_contact_groups":11,"reported_contact_groups":[{"body_a":"world","body_b":"link7","contact_count":68.0,"contact_point_centroid":[0.56233,-0.00692,-0.00175],"force_p95":864.51985,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":979.85921,"mean_force":286.09061,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.43519,-0.01014,0.02125]},{"body_a":"world","body_b":"hand","contact_count":22.0,"contact_point_centroid":[0.49106,-0.09845,-0.00326],"force_p95":144.14033,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":851.57271,"mean_force":48.63792,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.44235,-0.01063,-0.00102]},{"body_a":"world","body_b":"link6","contact_count":999.0,"contact_point_centroid":[0.67103,0.03733,-0.00024],"force_p95":199.19491,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":464.38333,"mean_force":191.18678,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.42958,-0.00127,0.11956]},{"body_a":"world","body_b":"link6","contact_count":837.0,"contact_point_centroid":[0.66198,0.01564,-0.00023],"force_p95":227.21407,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":351.96521,"mean_force":211.11918,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.41964,-0.00287,0.06931]},{"body_a":"world","body_b":"link6","contact_count":82.0,"contact_point_centroid":[0.6618,0.04437,-0.00012],"force_p95":104.4729,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":117.41723,"mean_force":71.20175,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.43383,-0.00308,0.14247]},{"body_a":"world","body_b":"left_finger","contact_count":354.0,"contact_point_centroid":[0.44634,-0.01385,-0.0037],"force_p95":27.313,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":38.93237,"mean_force":3.05046,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.44363,-0.01069,-0.00152]},{"body_a":"world","body_b":"right_finger","contact_count":354.0,"contact_point_centroid":[0.44605,-0.00702,-0.00362],"force_p95":27.29637,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":38.92305,"mean_force":3.06718,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.44364,-0.01069,-0.0016]},{"body_a":"grasp_target","body_b":"hand","contact_count":912.0,"contact_point_centroid":[0.52594,-0.02957,0.03012],"force_p95":1.02832,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.23558,"mean_force":0.39047,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.42129,-0.00349,0.06506]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8.0,"contact_point_centroid":[0.48071,-0.02012,0.01578],"force_p95":3.87266,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.95367,"mean_force":2.60403,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.47628,-0.01154,0.02349]},{"body_a":"world","body_b":"grasp_target","contact_count":3662.0,"contact_point_centroid":[0.4973,-0.02371,-0.00326],"force_p95":0.50101,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.0995,"mean_force":0.22292,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.42225,-0.00355,0.06491]},{"body_a":"grasp_target","body_b":"hand","contact_count":10.0,"contact_point_centroid":[0.52605,-0.02245,0.03881],"force_p95":0.6276,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.65637,"mean_force":0.16119,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.42033,0.0097,0.09298]},{"body_a":"grasp_target","body_b":"link7","contact_count":837.0,"contact_point_centroid":[0.52847,-0.03276,0.03231],"force_p95":0.39951,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.51668,"mean_force":0.18337,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.41964,-0.00287,0.06931]},{"body_a":"grasp_target","body_b":"link7","contact_count":10.0,"contact_point_centroid":[0.52591,-0.0225,0.03914],"force_p95":0.34203,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.51302,"mean_force":0.15247,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.42033,0.0097,0.09298]},{"body_a":"world","body_b":"grasp_target","contact_count":160.0,"contact_point_centroid":[0.50076,-0.01513,-0.00132],"force_p95":0.21764,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.35207,"mean_force":0.05987,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.4925,-0.01542,0.05327]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9855.0,"contact_point_centroid":[0.49328,0.00309,0.12259],"force_p95":0.12585,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32694,"mean_force":0.09241,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49032,-0.01537,0.12557]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10498.0,"contact_point_centroid":[0.49287,-0.03373,0.12362],"force_p95":0.12172,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32534,"mean_force":0.08711,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49032,-0.01537,0.12678]}],"total_contact_groups":27},"final_pose_error":0.11398,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.49359,-0.0203,0.01602],"final_tcp_position":[0.43037,-0.00364,0.28305],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":273005.57504,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":492.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1964.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.49972,-0.01429,0.13885],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11291,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":528.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2112.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.49887,-0.01551,0.05674],"tcp_start":[0.49972,-0.01429,0.13885],"tcp_to_object_dist_end":0.03112,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":36.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50369,-0.01546,0.02551],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31249,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.14399,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11343.0,"raw_peak_contact_force":0.15209,"tcp_end":[0.4941,-0.01544,0.05147],"tcp_start":[0.4941,-0.01544,0.05147],"tcp_to_object_dist_end":0.02767,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":976.0,"n_steps_budget":1000.0,"object_pos_end":[0.50086,-0.01975,0.17526],"object_pos_start":[0.50369,-0.01546,0.02546],"object_to_goal_dist_end":0.23589,"object_to_goal_dist_start":0.31253,"object_z_max":0.18147,"peak_contact_force":0.0,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":20513.0,"raw_peak_contact_force":0.35207,"tcp_end":[0.49087,-0.01537,0.22313],"tcp_start":[0.4941,-0.01544,0.05147],"tcp_to_object_dist_end":0.0491,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":11.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49243,-0.01749,0.01579],"object_pos_start":[0.50086,-0.01975,0.17526],"object_to_goal_dist_end":0.32389,"object_to_goal_dist_start":0.23589,"object_z_max":0.17526,"peak_contact_force":2690.82523,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":10818.0,"raw_peak_contact_force":979.85921,"subtask_id":"reach_goal","tcp_end":[0.41968,0.01046,0.0917],"tcp_start":[0.49087,-0.01537,0.22313],"tcp_to_object_dist_end":0.10879,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49359,-0.0203,0.01602],"object_pos_start":[0.49243,-0.01749,0.01579],"object_to_goal_dist_end":0.32518,"object_to_goal_dist_start":0.32389,"object_z_max":0.01608,"peak_contact_force":273005.57504,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9362.0,"raw_peak_contact_force":464.38333,"subtask_id":"reach_goal","tcp_end":[0.4338,-0.00324,0.14224],"tcp_start":[0.41968,0.01046,0.0917],"tcp_to_object_dist_end":0.1407,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49359,-0.0203,0.01602],"object_pos_start":[0.49359,-0.0203,0.01602],"object_to_goal_dist_end":0.32518,"object_to_goal_dist_start":0.32518,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1107.0,"raw_peak_contact_force":117.41723,"tcp_end":[0.43158,-0.00336,0.17087],"tcp_start":[0.4338,-0.00324,0.14224],"tcp_to_object_dist_end":0.16766,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49359,-0.0203,0.01602],"object_pos_start":[0.49359,-0.0203,0.01602],"object_to_goal_dist_end":0.32518,"object_to_goal_dist_start":0.32518,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.43037,-0.00364,0.28305],"tcp_start":[0.43158,-0.00336,0.17087],"tcp_to_object_dist_end":0.27491,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":62.0,"average_failure_rate":0.24409,"average_mean_iterations":51.92126,"average_solve_count":254.0,"average_success_count":192.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.carry_height":0.0859,"approach_goal.transport_speed":0.09143,"approach_object.approach_speed":0.0754,"descend_to_object.descend_speed":0.0301,"descend_to_place.place_speed":0.03667,"descend_to_place.place_z_offset":-0.00395,"lift_object.lift_height":0.10746,"lift_object.lift_speed":0.0872,"release_object.release_timeout":0.11891,"retract.retract_height":0.1034,"retract.retract_speed":0.08919},"optimized_scores":{"best_composite_score":-0.2651,"best_fitness_score":0.4649,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":7,"reported_contact_groups":[{"body_a":"world","body_b":"link7","contact_count":21.0,"contact_point_centroid":[0.75347,0.16321,-0.00039],"force_p95":1586.69859,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1848.15773,"mean_force":998.24119,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.83995,0.12694,0.12644]},{"body_a":"world","body_b":"hand","contact_count":32.0,"contact_point_centroid":[0.59923,1e-05,-0.00519],"force_p95":1490.5253,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1651.53578,"mean_force":392.74558,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.49921,-0.00754,-0.00442]},{"body_a":"world","body_b":"link6","contact_count":942.0,"contact_point_centroid":[0.66095,0.20411,-0.00033],"force_p95":335.29292,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1219.50803,"mean_force":306.75392,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.88501,0.18863,0.15666]},{"body_a":"world","body_b":"link6","contact_count":872.0,"contact_point_centroid":[0.54594,0.2219,-0.00037],"force_p95":295.86455,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":838.31838,"mean_force":228.77147,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.73205,0.06935,0.12784]},{"body_a":"world","body_b":"link7","contact_count":419.0,"contact_point_centroid":[0.6531,0.12166,-6e-05],"force_p95":235.86078,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":542.58636,"mean_force":74.05603,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.72617,0.06552,0.12324]},{"body_a":"world","body_b":"link6","contact_count":101.0,"contact_point_centroid":[0.66656,0.20888,-0.00016],"force_p95":136.0898,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":155.48661,"mean_force":84.62209,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.87081,0.19153,0.18702]},{"body_a":"world","body_b":"right_finger","contact_count":312.0,"contact_point_centroid":[0.48049,0.00582,-0.00573],"force_p95":35.35988,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":49.82394,"mean_force":14.45996,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.49831,-0.00398,-0.00777]},{"body_a":"world","body_b":"left_finger","contact_count":376.0,"contact_point_centroid":[0.51674,-0.01077,-0.00756],"force_p95":26.21902,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":45.248,"mean_force":10.49978,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.49869,-0.00544,-0.00603]},{"body_a":"grasp_target","body_b":"hand","contact_count":9.0,"contact_point_centroid":[0.52381,0.03292,0.00968],"force_p95":4.616,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.27858,"mean_force":2.15236,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.49802,0.00736,-0.01096]},{"body_a":"world","body_b":"grasp_target","contact_count":105.0,"contact_point_centroid":[0.5153,0.03514,-0.01885],"force_p95":3.87704,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.04904,"mean_force":1.60911,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.50507,0.01423,0.00974]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":806.0,"contact_point_centroid":[0.51432,0.05938,0.10124],"force_p95":0.8644,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.12685,"mean_force":0.31143,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51673,0.04046,0.10306]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":500.0,"contact_point_centroid":[0.51996,0.02476,0.12139],"force_p95":0.92764,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.05688,"mean_force":0.25914,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51382,0.04131,0.1222]},{"body_a":"world","body_b":"grasp_target","contact_count":164.0,"contact_point_centroid":[0.5099,0.03849,-0.0012],"force_p95":0.24684,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.42308,"mean_force":0.06313,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.50122,0.03874,0.04809]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12679.0,"contact_point_centroid":[0.49898,0.01947,0.09341],"force_p95":0.08622,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30083,"mean_force":0.05624,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49872,0.03854,0.09241]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13254.0,"contact_point_centroid":[0.49982,0.0576,0.09259],"force_p95":0.08773,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29986,"mean_force":0.05475,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49877,0.03855,0.09108]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.51253,0.03957,-0.00209],"force_p95":0.14392,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18521,"mean_force":0.12941,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.5034,0.03893,0.04689]}],"total_contact_groups":23},"final_pose_error":0.01923,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.76362,0.23796,-159.52086],"final_tcp_position":[0.86894,0.18965,0.29193],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":9748.86887,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":534.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2132.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.50758,0.03629,0.13784],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11198,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":957.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3828.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.50767,0.03928,0.0517],"tcp_start":[0.50758,0.03629,0.13784],"tcp_to_object_dist_end":0.02613,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51243,0.039,0.02572],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21288,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.14085,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12679.0,"raw_peak_contact_force":0.18521,"tcp_end":[0.50288,0.03888,0.0463],"tcp_start":[0.50288,0.03888,0.0463],"tcp_to_object_dist_end":0.02269,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":693.0,"n_steps_budget":780.0,"object_pos_end":[0.50957,0.03886,0.11667],"object_pos_start":[0.51243,0.03897,0.02573],"object_to_goal_dist_end":0.18054,"object_to_goal_dist_start":0.21289,"object_z_max":0.11658,"peak_contact_force":0.10262,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":26097.0,"raw_peak_contact_force":0.42308,"tcp_end":[0.49888,0.03856,0.14251],"tcp_start":[0.50288,0.03888,0.0463],"tcp_to_object_dist_end":0.02796,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.59859,0.10207,-19.14726],"object_pos_start":[0.50957,0.03886,0.11667],"object_to_goal_dist_end":19.29244,"object_to_goal_dist_start":0.18054,"object_z_max":0.11672,"peak_contact_force":256.51035,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":6835.0,"raw_peak_contact_force":1651.53578,"subtask_id":"reach_goal","tcp_end":[0.75853,0.08502,0.12991],"tcp_start":[0.49888,0.03856,0.14251],"tcp_to_object_dist_end":19.27784,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.68717,0.17501,-77.56335],"object_pos_start":[0.59859,0.10207,-19.14726],"object_to_goal_dist_end":77.7084,"object_to_goal_dist_start":19.29244,"object_z_max":-19.14726,"peak_contact_force":9748.86887,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5257.0,"raw_peak_contact_force":1848.15773,"subtask_id":"reach_goal","tcp_end":[0.87073,0.1914,0.18662],"tcp_start":[0.75853,0.08502,0.12991],"tcp_to_object_dist_end":77.75019,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.70489,0.1896,-93.95537],"object_pos_start":[0.68717,0.17501,-77.56335],"object_to_goal_dist_end":94.10042,"object_to_goal_dist_start":77.7084,"object_z_max":-77.56335,"peak_contact_force":0.0,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":326.0,"raw_peak_contact_force":155.48661,"tcp_end":[0.8697,0.19025,0.20774],"tcp_start":[0.87073,0.1914,0.18662],"tcp_to_object_dist_end":94.16325,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":663.0,"n_steps_budget":750.0,"object_pos_end":[0.76362,0.23796,-159.52086],"object_pos_start":[0.70489,0.1896,-93.95537],"object_to_goal_dist_end":159.66596,"object_to_goal_dist_start":94.10042,"object_z_max":-93.95537,"peak_contact_force":0.0,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.86894,0.18965,0.29193],"tcp_start":[0.8697,0.19025,0.20774],"tcp_to_object_dist_end":159.81283,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```