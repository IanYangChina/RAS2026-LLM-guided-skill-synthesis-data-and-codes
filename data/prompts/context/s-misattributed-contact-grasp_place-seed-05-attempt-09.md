## Search State

- **Seed**: 5
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 10 | 0.0041 | 0.37 | ✅ accepted |
| 8 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | 8 | -0.0090 | 0.27 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 12 | -0.1377 | 0.35 | ✅ accepted |
| 6 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 10 | -0.0229 | 0.33 | ✅ accepted |
| 5 | push → release → pull → release → release → grasp → retract → approach | impedance_motion | linear_cartesian | arc_cartesian | — | linear_cartesian | — | linear_cartesian | linear_cartesian | impedance_control | admittance_control | impedance_control | position_control | admittance_control | position_control | position_control | position_control | time_limit | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 6 | -0.3167 | 0.22 | ❌ rejected |

**Proposal policy**: task_score is 0.37 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.004) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: approach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.2
- id: grasp_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.03
  weight: 0.2
- id: lift_object
  anchor: object
  target_entity: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.2
- id: place_at_goal
  target_entity: object
  weight: 0.4
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
    approach_offset_z:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_object
- id: descend
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
    descend_offset_z:
      type: scalar
      range:
      - 0.02
      - 0.05
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: grasp_object
- id: grasp
  type: grasp
  control: impedance_control
  termination: time_limit
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
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
    - 0.005
  subtask_id: grasp_object
- id: lift
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
    - 0.12
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    lift_offset_z:
      type: scalar
      range:
      - 0.08
      - 0.18
      default: 0.12
      binds_to:
      - path: target.offset.z
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: lift_check
    when: after_phase
    predicate: object_lifted
    threshold: 0.03
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.015
  subtask_id: lift_object
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
    - 0.05
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    transport_offset_z:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: target.offset.z
        mode: replace
    transport_speed:
      type: scalar
      range:
      - 0.03
      - 0.12
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: place_at_goal
- id: descend_to_place
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
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    place_offset_z:
      type: scalar
      range:
      - -0.01
      - 0.03
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: replace
    place_speed:
      type: scalar
      range:
      - 0.01
      - 0.06
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: place_at_goal
- id: release
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
  subtask_id: place_at_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_offset_z: status=consumed; consumers=target.offset.z (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.03], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_offset_z: status=consumed; consumers=target.offset.z (replace)
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **grasp** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.005]
- **lift** (`lift`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.12], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_offset_z: status=consumed; consumers=target.offset.z (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=lift_check, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.03
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, 0.015]
- **transport_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.05], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_offset_z: status=consumed; consumers=target.offset.z (replace)
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_offset_z: status=consumed; consumers=target.offset.z (replace)
    - place_speed: status=consumed; consumers=generator.speed (replace)
- **release** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.004
- **task_score** (E): 0.370
- **fitness_score**: 0.654  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.650

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1516 |
| descend | 1.00 | 1.00 | 0.1027 |
| grasp | 1.00 | 1.00 | 0.0119 |
| lift | 1.00 | 1.00 | 0.1016 |
| transport_to_goal | 0.00 | 1.00 | 0.0945 |
| descend_to_place | 0.00 | 1.00 | 0.0391 |
| release | 1.00 | 1.00 | 0.0229 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, 0.017, 0.152) | (0.516, 0.018, 0.030)→(0.516, 0.018, 0.026) | 0.234→0.236 | 1.00 / 4.000 | 0.123 | 0.123 |
| descend | descend | 1.00 / step_budget | (0.510, 0.017, 0.152)→(0.511, 0.018, 0.050) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 44.333 | 0.139 | 0.189 |
| grasp | grasp | 1.00 / step_budget | (0.511, 0.018, 0.050)→(0.503, 0.018, 0.041) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 28.000 | 0.097 | 0.462 |
| lift | lift | 1.00 / step_budget | (0.503, 0.018, 0.041)→(0.509, 0.018, 0.142) | (0.516, 0.018, 0.026)→(0.519, 0.018, 0.119) | 0.236→0.197 | 1.00 / 25.000 | 0.099 | 0.140 |
| transport_to_goal | approach | 0.00 / step_budget | (0.509, 0.018, 0.142)→(0.551, 0.093, 0.173) | (0.519, 0.018, 0.119)→(0.557, 0.093, 0.143) | 0.197→0.108 | 1.00 / 11.667 | 94251.089 | 1.081 |
| descend_to_place | descend | 0.00 / step_budget | (0.551, 0.093, 0.173)→(0.569, 0.124, 0.170) | (0.557, 0.093, 0.143)→(0.582, 0.125, 0.053) | 0.108→0.134 | 1.00 / 3.333 | 0.152 | 0.552 |
| release | release | 1.00 / step_budget | (0.569, 0.124, 0.170)→(0.563, 0.122, 0.192) | (0.582, 0.125, 0.053)→(0.576, 0.124, 0.020) | 0.134→0.161 | 1.00 / 4.000 | 0.123 | 0.138 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.511
- phase_score: 0.491
- phase_breakdown.approach_object_score: 0.604
- phase_breakdown.place_at_goal_score: 0.221
- phase_breakdown.grasp_object_score: 0.662
- phase_breakdown.lift_object_score: 0.749
- grasp_place_fitness: 0.721

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.721
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.511
- **Median Q (composite search score)**: 0.028
- **K-run variance**: 0.0044
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.298


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.11429,"average_solve_count":210.0,"average_success_count":210.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_offset_z":0.11735,"approach_object.approach_speed":0.03423,"descend.descend_offset_z":0.03107,"descend.descend_speed":0.05972,"descend_to_place.place_offset_z":0.00815,"descend_to_place.place_speed":0.02775,"lift.lift_offset_z":0.12876,"lift.lift_speed":0.07158,"transport_to_goal.transport_offset_z":0.07248,"transport_to_goal.transport_speed":0.08356},"optimized_scores":{"best_composite_score":0.07053,"best_fitness_score":0.72053,"best_task_score":0.51073},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2046.0,"contact_point_centroid":[0.59023,0.13914,-0.00234],"force_p95":0.17925,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.27294,"mean_force":0.1404,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57113,0.13156,0.14005]},{"body_a":"world","body_b":"grasp_target","contact_count":199.0,"contact_point_centroid":[0.5283,0.02955,-0.00119],"force_p95":0.24068,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.43999,"mean_force":0.06661,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.516,0.02975,0.04578]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15096.0,"contact_point_centroid":[0.52141,0.04866,0.0914],"force_p95":0.09131,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28748,"mean_force":0.06047,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51915,0.02969,0.08962]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15223.0,"contact_point_centroid":[0.52056,0.01076,0.08904],"force_p95":0.10026,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2747,"mean_force":0.05908,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51886,0.02968,0.08734]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3700.0,"contact_point_centroid":[0.5719,0.10387,0.1435],"force_p95":0.12265,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22455,"mean_force":0.10108,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.5662,0.12212,0.14758]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53052,0.03068,-0.00208],"force_p95":0.1433,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19952,"mean_force":0.12863,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51867,0.02995,0.04551]},{"body_a":"world","body_b":"grasp_target","contact_count":2140.0,"contact_point_centroid":[0.5305,0.03079,-0.00193],"force_p95":0.13221,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12285,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51066,0.01366,0.22684]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11471.0,"contact_point_centroid":[0.55105,0.0574,0.1483],"force_p95":0.11418,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13825,"mean_force":0.08027,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54566,0.07598,0.14893]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11856.0,"contact_point_centroid":[0.55127,0.09462,0.14847],"force_p95":0.11182,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13802,"mean_force":0.07767,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54573,0.0761,0.14897]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3822.0,"contact_point_centroid":[0.57188,0.14037,0.14317],"force_p95":0.11702,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13459,"mean_force":0.09744,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.56626,0.12226,0.14746]},{"body_a":"world","body_b":"grasp_target","contact_count":3668.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.52369,0.02943,0.08959]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.59049,0.13909,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.5691,0.13483,0.13881]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5012.0,"contact_point_centroid":[0.51763,0.0107,0.04734],"force_p95":0.06723,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11098,"mean_force":0.04303,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51746,0.02987,0.04412]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4938.0,"contact_point_centroid":[0.51799,0.04915,0.04594],"force_p95":0.07122,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07497,"mean_force":0.045,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51747,0.02987,0.04413]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1830.0,"contact_point_centroid":[0.57197,0.13226,0.1418],"force_p95":0.01174,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01891,"mean_force":0.01066,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57151,0.13224,0.13958]},{"body_a":"left_finger","body_b":"right_finger","contact_count":221.0,"contact_point_centroid":[0.57276,0.13564,0.13685],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01101,"mean_force":0.0101,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.5721,0.13562,0.1344]}],"total_contact_groups":16},"final_pose_error":0.05502,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.59049,0.13909,0.01602],"final_tcp_position":[0.5736,0.13595,0.13697],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":273004.76975,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":536.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3668.0,"raw_peak_contact_force":0.12263,"subtask_id":"approach_object","tcp_end":[0.5241,0.02799,0.1542],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12837,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":917.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.14073,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11750.0,"raw_peak_contact_force":0.19952,"subtask_id":"grasp_object","tcp_end":[0.52546,0.0304,0.05344],"tcp_start":[0.5241,0.02799,0.1542],"tcp_to_object_dist_end":0.02788,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53043,0.0301,0.02571],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18409,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.0988,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":30518.0,"raw_peak_contact_force":0.43999,"subtask_id":"grasp_object","tcp_end":[0.51744,0.02987,0.04409],"tcp_start":[0.52546,0.0304,0.05344],"tcp_to_object_dist_end":0.02251,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":886.0,"n_steps_budget":990.0,"object_pos_end":[0.53578,0.03002,0.11746],"object_pos_start":[0.53043,0.0301,0.02571],"object_to_goal_dist_end":0.16273,"object_to_goal_dist_start":0.18409,"object_z_max":0.11738,"peak_contact_force":0.11511,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":23327.0,"raw_peak_contact_force":0.13825,"subtask_id":"lift_object","tcp_end":[0.52573,0.02982,0.1436],"tcp_start":[0.51744,0.02987,0.04409],"tcp_to_object_dist_end":0.028,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.57151,0.11693,0.12392],"object_pos_start":[0.53578,0.03002,0.11746],"object_to_goal_dist_end":0.07038,"object_to_goal_dist_start":0.16273,"object_z_max":0.12392,"peak_contact_force":273004.76975,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":11398.0,"raw_peak_contact_force":1.27294,"subtask_id":"place_at_goal","tcp_end":[0.56637,0.11674,0.15817],"tcp_start":[0.52573,0.02982,0.1436],"tcp_to_object_dist_end":0.03463,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.59049,0.13909,0.01602],"object_pos_start":[0.57151,0.11693,0.12392],"object_to_goal_dist_end":0.10079,"object_to_goal_dist_start":0.07038,"object_z_max":0.12392,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1021.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_at_goal","tcp_end":[0.5736,0.13595,0.13697],"tcp_start":[0.56637,0.11674,0.15817],"tcp_to_object_dist_end":0.12217,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59049,0.13909,0.01602],"object_pos_start":[0.59049,0.13909,0.01602],"object_to_goal_dist_end":0.10079,"object_to_goal_dist_start":0.10079,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2140.0,"raw_peak_contact_force":0.13845,"subtask_id":"place_at_goal","tcp_end":[0.56733,0.13437,0.1589],"tcp_start":[0.5736,0.13595,0.13697],"tcp_to_object_dist_end":0.14483,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.18687,"average_solve_count":198.0,"average_success_count":198.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_offset_z":0.11411,"approach_object.approach_speed":0.05546,"descend.descend_offset_z":0.02256,"descend.descend_speed":0.04209,"descend_to_place.place_offset_z":0.01044,"descend_to_place.place_speed":0.04991,"lift.lift_offset_z":0.14874,"lift.lift_speed":0.06496,"transport_to_goal.transport_offset_z":0.06373,"transport_to_goal.transport_speed":0.07255},"optimized_scores":{"best_composite_score":-0.08585,"best_fitness_score":0.56415,"best_task_score":0.18918},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":444.0,"contact_point_centroid":[0.55907,0.09931,-0.00434],"force_p95":0.94856,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.81658,"mean_force":0.2338,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.5406,0.0953,0.21123]},{"body_a":"world","body_b":"grasp_target","contact_count":162.0,"contact_point_centroid":[0.50121,-0.01519,-0.00111],"force_p95":0.28378,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.44987,"mean_force":0.06792,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.48968,-0.01539,0.04226]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16609.0,"contact_point_centroid":[0.49363,0.00373,0.09204],"force_p95":0.09363,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30488,"mean_force":0.06079,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49197,-0.01529,0.09006]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17825.0,"contact_point_centroid":[0.49355,-0.03422,0.09081],"force_p95":0.09011,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27484,"mean_force":0.05731,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.4919,-0.01529,0.08932]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8562.0,"contact_point_centroid":[0.53689,0.05649,0.20095],"force_p95":0.12687,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22387,"mean_force":0.08446,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.53113,0.07493,0.20278]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13589.0,"contact_point_centroid":[0.51646,0.04284,0.17388],"force_p95":0.09422,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16579,"mean_force":0.06931,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51128,0.02406,0.17288]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8671.0,"contact_point_centroid":[0.53697,0.09365,0.20085],"force_p95":0.11327,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16197,"mean_force":0.0835,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.53128,0.07524,0.20291]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14459.0,"contact_point_centroid":[0.51583,0.00448,0.17311],"force_p95":0.09369,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15256,"mean_force":0.0655,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5109,0.0232,0.17219]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50381,-0.01557,-0.00203],"force_p95":0.13254,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15162,"mean_force":0.1253,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49216,-0.01543,0.04187]},{"body_a":"world","body_b":"grasp_target","contact_count":1944.0,"contact_point_centroid":[0.50382,-0.01567,-0.00193],"force_p95":0.13308,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12288,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49882,-0.00689,0.22672]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.55944,0.09938,-0.00199],"force_p95":0.12378,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12694,"mean_force":0.12282,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.53799,0.09669,0.21479]},{"body_a":"world","body_b":"grasp_target","contact_count":2700.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.49767,-0.01485,0.09712]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4117.0,"contact_point_centroid":[0.49141,0.00385,0.04341],"force_p95":0.07656,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11435,"mean_force":0.05208,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.491,-0.01542,0.04063]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5259.0,"contact_point_centroid":[0.49092,-0.03447,0.04315],"force_p95":0.06463,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08762,"mean_force":0.04159,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.491,-0.01542,0.04063]},{"body_a":"left_finger","body_b":"right_finger","contact_count":237.0,"contact_point_centroid":[0.54163,0.09625,0.21386],"force_p95":0.01436,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01566,"mean_force":0.01162,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.54105,0.09625,0.21164]},{"body_a":"left_finger","body_b":"right_finger","contact_count":222.0,"contact_point_centroid":[0.54065,0.09718,0.21188],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01103,"mean_force":0.01005,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.54033,0.09717,0.2098]}],"total_contact_groups":16},"final_pose_error":0.11107,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.55944,0.09938,0.01602],"final_tcp_position":[0.54156,0.09733,0.21211],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":9748.36582,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":487.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2700.0,"raw_peak_contact_force":0.12263,"subtask_id":"approach_object","tcp_end":[0.49975,-0.01418,0.15287],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12693,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":675.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13153,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11176.0,"raw_peak_contact_force":0.15162,"subtask_id":"grasp_object","tcp_end":[0.49886,-0.01552,0.04911],"tcp_start":[0.49975,-0.01418,0.15287],"tcp_to_object_dist_end":0.02362,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50372,-0.01527,0.02587],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.3121,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.10448,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":34596.0,"raw_peak_contact_force":0.44987,"subtask_id":"grasp_object","tcp_end":[0.49097,-0.01542,0.0406],"tcp_start":[0.49886,-0.01552,0.04911],"tcp_to_object_dist_end":0.01948,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50752,-0.01521,0.12305],"object_pos_start":[0.50372,-0.01527,0.02587],"object_to_goal_dist_end":0.25103,"object_to_goal_dist_start":0.3121,"object_z_max":0.12294,"peak_contact_force":0.09399,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":28048.0,"raw_peak_contact_force":0.16579,"subtask_id":"lift_object","tcp_end":[0.49747,-0.01523,0.14617],"tcp_start":[0.49097,-0.01542,0.0406],"tcp_to_object_dist_end":0.02521,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53363,0.06046,0.17258],"object_pos_start":[0.50752,-0.01521,0.12305],"object_to_goal_dist_end":0.15707,"object_to_goal_dist_start":0.25103,"object_z_max":0.17255,"peak_contact_force":9748.36582,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":17914.0,"raw_peak_contact_force":1.81658,"subtask_id":"place_at_goal","tcp_end":[0.5275,0.06051,0.20213],"tcp_start":[0.49747,-0.01523,0.14617],"tcp_to_object_dist_end":0.03018,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5594,0.09921,0.01612],"object_pos_start":[0.53363,0.06046,0.17258],"object_to_goal_dist_end":0.24973,"object_to_goal_dist_start":0.15707,"object_z_max":0.17258,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1022.0,"raw_peak_contact_force":0.12694,"subtask_id":"place_at_goal","tcp_end":[0.54156,0.09733,0.21211],"tcp_start":[0.5275,0.06051,0.20213],"tcp_to_object_dist_end":0.1968,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.55944,0.09938,0.01602],"object_pos_start":[0.5594,0.09921,0.01612],"object_to_goal_dist_end":0.24976,"object_to_goal_dist_start":0.24973,"object_z_max":0.01612,"peak_contact_force":0.12262,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1944.0,"raw_peak_contact_force":0.13845,"subtask_id":"place_at_goal","tcp_end":[0.53664,0.09641,0.23524],"tcp_start":[0.54156,0.09733,0.21211],"tcp_to_object_dist_end":0.22043,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.1401,"average_solve_count":207.0,"average_success_count":207.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_offset_z":0.11255,"approach_object.approach_speed":0.04576,"descend.descend_offset_z":0.02482,"descend.descend_speed":0.04101,"descend_to_place.place_offset_z":0.02934,"descend_to_place.place_speed":0.05981,"lift.lift_offset_z":0.15979,"lift.lift_speed":0.06078,"transport_to_goal.transport_offset_z":0.05407,"transport_to_goal.transport_speed":0.07593},"optimized_scores":{"best_composite_score":0.02755,"best_fitness_score":0.67755,"best_task_score":0.41115},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":184.0,"contact_point_centroid":[0.5802,0.13667,-0.0068],"force_p95":1.10842,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.40652,"mean_force":0.37377,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.58492,0.13615,0.17063]},{"body_a":"world","body_b":"grasp_target","contact_count":184.0,"contact_point_centroid":[0.50927,0.03787,-0.00119],"force_p95":0.30431,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.49676,"mean_force":0.07557,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.4983,0.03847,0.03993]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18326.0,"contact_point_centroid":[0.5011,0.05743,0.08736],"force_p95":0.08027,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2966,"mean_force":0.05558,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.50002,0.03836,0.08545]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18354.0,"contact_point_centroid":[0.50118,0.01931,0.08856],"force_p95":0.08288,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2665,"mean_force":0.05501,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.50009,0.03836,0.08639]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51254,0.03958,-0.0021],"force_p95":0.14965,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21635,"mean_force":0.13003,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50095,0.03871,0.03951]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12322.0,"contact_point_centroid":[0.57707,0.09953,0.15619],"force_p95":0.12649,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15329,"mean_force":0.07514,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57212,0.11819,0.15647]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":504.0,"contact_point_centroid":[0.59335,0.1189,0.15258],"force_p95":0.13545,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1392,"mean_force":0.09371,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.5889,0.13723,0.15596]},{"body_a":"world","body_b":"grasp_target","contact_count":2108.0,"contact_point_centroid":[0.51251,0.03972,-0.00193],"force_p95":0.13221,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12286,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50263,0.0176,0.22497]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12701.0,"contact_point_centroid":[0.57807,0.13762,0.15616],"force_p95":0.10802,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13412,"mean_force":0.07312,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57292,0.11902,0.1566]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":583.0,"contact_point_centroid":[0.59405,0.15544,0.15235],"force_p95":0.12532,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13154,"mean_force":0.08323,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.58896,0.13724,0.15607]},{"body_a":"world","body_b":"grasp_target","contact_count":3696.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.50634,0.03799,0.0838]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16450.0,"contact_point_centroid":[0.53853,0.09436,0.14955],"force_p95":0.08359,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11633,"mean_force":0.05775,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53509,0.0754,0.14844]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5055.0,"contact_point_centroid":[0.49966,0.01937,0.04138],"force_p95":0.06876,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10857,"mean_force":0.04294,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49977,0.03862,0.03821]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16107.0,"contact_point_centroid":[0.53756,0.05554,0.14921],"force_p95":0.08186,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1082,"mean_force":0.05898,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53427,0.07448,0.14807]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5454.0,"contact_point_centroid":[0.49949,0.0579,0.04081],"force_p95":0.06789,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07506,"mean_force":0.04106,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49977,0.03862,0.03822]}],"total_contact_groups":15},"final_pose_error":0.05281,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.57941,0.13474,0.02659],"final_tcp_position":[0.59081,0.13764,0.15951],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1.40652,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":528.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3696.0,"raw_peak_contact_force":0.12263,"subtask_id":"approach_object","tcp_end":[0.50762,0.03607,0.15029],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12442,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":924.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.14582,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":12309.0,"raw_peak_contact_force":0.21635,"subtask_id":"grasp_object","tcp_end":[0.50762,0.03926,0.0469],"tcp_start":[0.50762,0.03607,0.15029],"tcp_to_object_dist_end":0.02145,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":33.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51243,0.03886,0.02565],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21301,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.08844,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":36864.0,"raw_peak_contact_force":0.49676,"subtask_id":"grasp_object","tcp_end":[0.49974,0.03861,0.03818],"tcp_start":[0.50762,0.03926,0.0469],"tcp_to_object_dist_end":0.01783,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":33.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51304,0.03844,0.11667],"object_pos_start":[0.51243,0.03886,0.02565],"object_to_goal_dist_end":0.1786,"object_to_goal_dist_start":0.21301,"object_z_max":0.11656,"peak_contact_force":0.08727,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":32557.0,"raw_peak_contact_force":0.11633,"subtask_id":"lift_object","tcp_end":[0.50456,0.03845,0.13724],"tcp_start":[0.49974,0.03861,0.03818],"tcp_to_object_dist_end":0.02225,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56454,0.10208,0.13386],"object_pos_start":[0.51304,0.03844,0.11667],"object_to_goal_dist_end":0.09518,"object_to_goal_dist_start":0.1786,"object_z_max":0.13384,"peak_contact_force":0.13293,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":25023.0,"raw_peak_contact_force":0.15329,"subtask_id":"place_at_goal","tcp_end":[0.55983,0.10228,0.16002],"tcp_start":[0.50456,0.03845,0.13724],"tcp_to_object_dist_end":0.02658,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.59557,0.13776,0.12601],"object_pos_start":[0.56454,0.10208,0.13386],"object_to_goal_dist_end":0.05092,"object_to_goal_dist_start":0.09518,"object_z_max":0.13386,"peak_contact_force":0.20961,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1271.0,"raw_peak_contact_force":1.40652,"subtask_id":"place_at_goal","tcp_end":[0.59081,0.13764,0.15951],"tcp_start":[0.55983,0.10228,0.16002],"tcp_to_object_dist_end":0.03383,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57941,0.13474,0.02659],"object_pos_start":[0.59557,0.13776,0.12601],"object_to_goal_dist_end":0.13332,"object_to_goal_dist_start":0.05092,"object_z_max":0.12601,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2108.0,"raw_peak_contact_force":0.13845,"subtask_id":"place_at_goal","tcp_end":[0.58485,0.13613,0.18068],"tcp_start":[0.59081,0.13764,0.15951],"tcp_to_object_dist_end":0.1542,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```