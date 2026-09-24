## Search State

- **Seed**: 5
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 10 | 0.0152 | 0.39 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 11 | -0.0742 | 0.31 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 11 | -0.1531 | 0.32 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 10 | -0.0686 | 0.39 | ✅ accepted |
| 3 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 10 | -0.0063 | 0.35 | ✅ accepted |

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

## Current Skill (Q=0.015) — your mutation base

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
  weight: 0.2
- id: grasp_target
  anchor: object
  weight: 0.2
- id: lift_clear
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.2
- id: transport_goal
  offset:
  - 0.0
  - 0.0
  - 0.05
  weight: 0.2
- id: place_goal
  offset:
  - 0.0
  - 0.0
  - 0.02
  weight: 0.2
phases:
- id: approach_1
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
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    arc_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.arc_height
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
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
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.05
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    depth:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: grasp_target
- id: grasp_1
  type: grasp
  control: position_control
  termination: grasp_success
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.005
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
    - -0.01
- id: lift_1
  type: lift
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
    - 0.15
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: lift_check
    when: after_phase
    predicate: object_lifted
    threshold: 0.02
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.01
  subtask_id: lift_clear
- id: transport_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: place_target
    offset:
    - 0.0
    - 0.0
    - 0.05
    tolerance: 0.015
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
    transport_z:
      type: scalar
      range:
      - 0.03
      - 0.15
      default: 0.05
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: transport_goal
- id: place_descend_1
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: place_target
    offset:
    - 0.0
    - 0.0
    - 0.02
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    place_z:
      type: scalar
      range:
      - 0.0
      - 0.05
      default: 0.02
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: place_goal
- id: release_1
  type: release
  control: position_control
  termination: pose_tolerance
  end_effector_action: open
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.01

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.05], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - depth: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings: none
  - guards:
    - id=grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, -0.01]
- **lift_1** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.15], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=lift_check, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.02
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.01]
- **transport_1** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=place_target, offset=[0.0, 0.0, 0.05], tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
    - transport_z: status=consumed; consumers=target.offset.z (replace)
- **place_descend_1** (`descend`)
  - target: source=yaml, anchor=task_goal, entity=place_target, offset=[0.0, 0.0, 0.02], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_z: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.015
- **task_score** (E): 0.386
- **fitness_score**: 0.665  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.650

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1742 |
| descend_1 | 1.00 | 1.00 | 0.0870 |
| grasp_1 | 1.00 | 1.00 | 0.0123 |
| lift_1 | 0.00 | 1.00 | 0.0987 |
| transport_1 | 0.67 | 1.00 | 0.1793 |
| place_descend_1 | 1.00 | 1.00 | 0.0471 |
| release_1 | 1.00 | 1.00 | 0.0210 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.511, 0.027, 0.131) | (0.516, 0.018, 0.030)→(0.516, 0.018, 0.026) | 0.234→0.236 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.511, 0.027, 0.131)→(0.510, 0.019, 0.044) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.510, 0.019, 0.044)→(0.502, 0.019, 0.035) | (0.516, 0.018, 0.026)→(0.516, 0.019, 0.026) | 0.236→0.236 | 1.00 / 41.000 | 0.167 | 0.198 |
| lift_1 | lift | 0.00 / step_budget | (0.502, 0.019, 0.035)→(0.505, 0.019, 0.134) | (0.516, 0.019, 0.026)→(0.514, 0.019, 0.116) | 0.236→0.199 | 1.00 / 35.667 | 0.088 | 0.549 |
| transport_1 | approach | 0.67 / step_budget | (0.505, 0.019, 0.134)→(0.587, 0.150, 0.214) | (0.514, 0.019, 0.116)→(0.577, 0.146, 0.126) | 0.199→0.083 | 1.00 / 16.667 | 0.125 | 0.706 |
| place_descend_1 | descend | 1.00 / step_budget | (0.587, 0.150, 0.214)→(0.599, 0.175, 0.188) | (0.577, 0.146, 0.126)→(0.586, 0.149, 0.046) | 0.083→0.129 | 1.00 / 13.333 | 0.125 | 0.711 |
| release_1 | release | 1.00 / step_budget | (0.599, 0.175, 0.188)→(0.594, 0.173, 0.208) | (0.586, 0.149, 0.046)→(0.579, 0.149, 0.019) | 0.129→0.156 | 1.00 / 4.000 | 0.117 | 0.485 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.569
- phase_score: 0.683
- phase_breakdown.lift_clear_score: 0.425
- phase_breakdown.transport_goal_score: 0.753
- phase_breakdown.place_goal_score: 0.795
- phase_breakdown.grasp_target_score: 0.620
- phase_breakdown.reach_object_score: 0.819
- grasp_place_fitness: 0.750

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.750
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.569
- **Median Q (composite search score)**: 0.022
- **K-run variance**: 0.0052
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.368


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.20202,"average_solve_count":198.0,"average_success_count":198.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.arc_height":0.15264,"approach_1.speed":0.04946,"descend_1.depth":0.01922,"descend_1.speed":0.06324,"lift_1.lift_height":0.2925,"lift_1.speed":0.0586,"place_descend_1.place_z":0.02235,"place_descend_1.speed":0.0574,"transport_1.speed":0.09523,"transport_1.transport_z":0.06855},"optimized_scores":{"best_composite_score":0.09984,"best_fitness_score":0.74984,"best_task_score":0.56905},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":249.0,"contact_point_centroid":[0.57949,0.17353,-0.00458],"force_p95":0.93833,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.20827,"mean_force":0.26528,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58864,0.17258,0.14753]},{"body_a":"world","body_b":"grasp_target","contact_count":204.0,"contact_point_centroid":[0.52671,0.03098,-0.00115],"force_p95":0.28145,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.48956,"mean_force":0.11845,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51496,0.03096,0.04521]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":834.0,"contact_point_centroid":[0.59588,0.19272,0.12977],"force_p95":0.20649,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.42338,"mean_force":0.09128,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59258,0.17391,0.13212]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":907.0,"contact_point_centroid":[0.59578,0.15549,0.13036],"force_p95":0.1673,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.38926,"mean_force":0.08062,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59263,0.17393,0.13218]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19699.0,"contact_point_centroid":[0.51597,0.01167,0.09445],"force_p95":0.07692,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28855,"mean_force":0.05168,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51507,0.03076,0.0922]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18977.0,"contact_point_centroid":[0.51599,0.04988,0.09227],"force_p95":0.07706,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28522,"mean_force":0.05373,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.515,0.03076,0.09021]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1128.0,"contact_point_centroid":[0.59775,0.19125,0.15076],"force_p95":0.13,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26485,"mean_force":0.09121,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.59396,0.17244,0.15239]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1235.0,"contact_point_centroid":[0.5982,0.154,0.15197],"force_p95":0.10774,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24944,"mean_force":0.07482,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.59393,0.17238,0.15279]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5305,0.03074,-0.00203],"force_p95":0.22573,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23013,"mean_force":0.16218,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5179,0.03118,0.04498]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12679.0,"contact_point_centroid":[0.55637,0.08207,0.15118],"force_p95":0.08358,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14838,"mean_force":0.05798,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55429,0.10103,0.1508]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4840.0,"contact_point_centroid":[0.5175,0.05016,0.04539],"force_p95":0.07845,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1396,"mean_force":0.05421,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51671,0.0311,0.04361]},{"body_a":"world","body_b":"grasp_target","contact_count":3044.0,"contact_point_centroid":[0.5305,0.03079,-0.00195],"force_p95":0.12782,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12279,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50963,0.046,0.22419]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12892.0,"contact_point_centroid":[0.5559,0.11998,0.15058],"force_p95":0.08343,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13774,"mean_force":0.05686,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55428,0.10103,0.15078]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4150.0,"contact_point_centroid":[0.51745,0.01189,0.04639],"force_p95":0.08579,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12866,"mean_force":0.06102,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51671,0.0311,0.04361]},{"body_a":"world","body_b":"grasp_target","contact_count":1044.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52367,0.0351,0.09283]}],"total_contact_groups":15},"final_pose_error":0.00981,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.58183,0.17347,0.02601],"final_tcp_position":[0.59515,0.17461,0.13675],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":1.20827,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":762.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3044.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.52484,0.03857,0.13257],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.10698,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":261.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1044.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_target","tcp_end":[0.52495,0.0317,0.05323],"tcp_start":[0.52484,0.03857,0.13257],"tcp_to_object_dist_end":0.02778,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5304,0.03082,0.02587],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18345,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.22202,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10790.0,"raw_peak_contact_force":0.23013,"tcp_end":[0.51668,0.0311,0.04358],"tcp_start":[0.52495,0.0317,0.05323],"tcp_to_object_dist_end":0.0224,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52304,0.03064,0.11442],"object_pos_start":[0.5304,0.03082,0.02587],"object_to_goal_dist_end":0.16759,"object_to_goal_dist_start":0.18345,"object_z_max":0.11431,"peak_contact_force":0.08,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":38880.0,"raw_peak_contact_force":0.48956,"subtask_id":"lift_clear","tcp_end":[0.51758,0.03073,0.1392],"tcp_start":[0.51668,0.0311,0.04358],"tcp_to_object_dist_end":0.02538,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":753.0,"n_steps_budget":1000.0,"object_pos_end":[0.59912,0.17056,0.13789],"object_pos_start":[0.52304,0.03064,0.11442],"object_to_goal_dist_end":0.03096,"object_to_goal_dist_start":0.16759,"object_z_max":0.13787,"peak_contact_force":0.09887,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":25571.0,"raw_peak_contact_force":0.14838,"subtask_id":"transport_goal","tcp_end":[0.59367,0.17058,0.16676],"tcp_start":[0.51758,0.03073,0.1392],"tcp_to_object_dist_end":0.02938,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":97.0,"n_steps_budget":1000.0,"object_pos_end":[0.60132,0.17444,0.10659],"object_pos_start":[0.59912,0.17056,0.13789],"object_to_goal_dist_end":0.00441,"object_to_goal_dist_start":0.03096,"object_z_max":0.13789,"peak_contact_force":0.12897,"phase_name":"place_descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2363.0,"raw_peak_contact_force":0.26485,"subtask_id":"place_goal","tcp_end":[0.59515,0.17461,0.13675],"tcp_start":[0.59367,0.17058,0.16676],"tcp_to_object_dist_end":0.03078,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58183,0.17347,0.02601],"object_pos_start":[0.60132,0.17444,0.10659],"object_to_goal_dist_end":0.08457,"object_to_goal_dist_start":0.00441,"object_z_max":0.10659,"peak_contact_force":0.1056,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1990.0,"raw_peak_contact_force":1.20827,"tcp_end":[0.58856,0.17256,0.15696],"tcp_start":[0.59515,0.17461,0.13675],"tcp_to_object_dist_end":0.13113,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.22764,"average_solve_count":246.0,"average_success_count":246.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.arc_height":0.18985,"approach_1.speed":0.07043,"descend_1.depth":0.01135,"descend_1.speed":0.04133,"lift_1.lift_height":0.17467,"lift_1.speed":0.06461,"place_descend_1.place_z":0.00675,"place_descend_1.speed":0.04878,"transport_1.speed":0.05198,"transport_1.transport_z":0.06962},"optimized_scores":{"best_composite_score":-0.0764,"best_fitness_score":0.5736,"best_task_score":0.20203},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2269.0,"contact_point_centroid":[0.58135,0.12696,-0.00255],"force_p95":0.15612,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.7452,"mean_force":0.14458,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.57274,0.16377,0.24683]},{"body_a":"world","body_b":"grasp_target","contact_count":170.0,"contact_point_centroid":[0.5009,-0.01379,-0.00118],"force_p95":0.29862,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.49756,"mean_force":0.07223,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48921,-0.0143,0.03884]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16143.0,"contact_point_centroid":[0.49256,0.00472,0.08833],"force_p95":0.09829,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30638,"mean_force":0.06241,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49076,-0.0143,0.08641]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17714.0,"contact_point_centroid":[0.49257,-0.03319,0.08754],"force_p95":0.08932,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28927,"mean_force":0.0579,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49075,-0.0143,0.08614]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":482.0,"contact_point_centroid":[0.56143,0.14467,0.2467],"force_p95":0.19931,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23303,"mean_force":0.15154,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.55584,0.12671,0.2506]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50386,-0.01546,-0.00212],"force_p95":0.15684,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22183,"mean_force":0.13166,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49179,-0.01433,0.03829]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":786.0,"contact_point_centroid":[0.56166,0.10981,0.24699],"force_p95":0.13475,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20642,"mean_force":0.0927,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.55599,0.12714,0.25046]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11085.0,"contact_point_centroid":[0.52684,0.06962,0.19449],"force_p95":0.13523,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17177,"mean_force":0.08325,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52196,0.05103,0.19408]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12399.0,"contact_point_centroid":[0.52642,0.03168,0.19352],"force_p95":0.10888,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14659,"mean_force":0.07515,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52154,0.05006,0.19328]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4079.0,"contact_point_centroid":[0.49119,0.0049,0.03981],"force_p95":0.08012,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1463,"mean_force":0.05189,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49063,-0.01432,0.03706]},{"body_a":"world","body_b":"grasp_target","contact_count":2408.0,"contact_point_centroid":[0.50382,-0.01567,-0.00194],"force_p95":0.13067,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12283,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49881,0.01764,0.21391]},{"body_a":"world","body_b":"grasp_target","contact_count":1216.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49782,-0.01065,0.08901]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.58137,0.12701,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57946,0.18249,0.24794]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4985.0,"contact_point_centroid":[0.49121,-0.03345,0.03891],"force_p95":0.07254,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07981,"mean_force":0.04456,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49064,-0.01432,0.03706]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2202.0,"contact_point_centroid":[0.57406,0.16552,0.24898],"force_p95":0.0116,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01596,"mean_force":0.01067,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.5736,0.16551,0.24683]},{"body_a":"left_finger","body_b":"right_finger","contact_count":214.0,"contact_point_centroid":[0.58193,0.1833,0.24601],"force_p95":0.01111,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01287,"mean_force":0.01034,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58146,0.18329,0.24404]}],"total_contact_groups":16},"final_pose_error":0.00998,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.58137,0.12701,0.01602],"final_tcp_position":[0.58252,0.18354,0.2468],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":1.7452,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":603.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2408.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.49965,-0.00707,0.1325],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.10691,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":304.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1216.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_target","tcp_end":[0.49866,-0.01438,0.04571],"tcp_start":[0.49965,-0.00707,0.1325],"tcp_to_object_dist_end":0.0204,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50374,-0.01447,0.02559],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31177,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.15042,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10864.0,"raw_peak_contact_force":0.22183,"tcp_end":[0.4906,-0.01432,0.03703],"tcp_start":[0.49866,-0.01438,0.04571],"tcp_to_object_dist_end":0.01742,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50636,-0.01404,0.12235],"object_pos_start":[0.50374,-0.01447,0.02559],"object_to_goal_dist_end":0.25081,"object_to_goal_dist_start":0.31177,"object_z_max":0.12224,"peak_contact_force":0.11388,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":34027.0,"raw_peak_contact_force":0.49756,"subtask_id":"lift_clear","tcp_end":[0.49549,-0.01435,0.143],"tcp_start":[0.4906,-0.01432,0.03703],"tcp_to_object_dist_end":0.02333,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55877,0.12115,0.22456],"object_pos_start":[0.50636,-0.01404,0.12235],"object_to_goal_dist_end":0.07577,"object_to_goal_dist_start":0.25081,"object_z_max":0.22447,"peak_contact_force":0.15399,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":23484.0,"raw_peak_contact_force":0.17177,"subtask_id":"transport_goal","tcp_end":[0.55423,0.12107,0.25376],"tcp_start":[0.49549,-0.01435,0.143],"tcp_to_object_dist_end":0.02955,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":751.0,"n_steps_budget":1000.0,"object_pos_end":[0.58137,0.12701,0.01602],"object_pos_start":[0.55877,0.12115,0.22456],"object_to_goal_dist_end":0.2399,"object_to_goal_dist_start":0.07577,"object_z_max":0.22456,"peak_contact_force":0.12263,"phase_name":"place_descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5739.0,"raw_peak_contact_force":1.7452,"subtask_id":"place_goal","tcp_end":[0.58252,0.18354,0.2468],"tcp_start":[0.55423,0.12107,0.25376],"tcp_to_object_dist_end":0.2376,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58137,0.12701,0.01602],"object_pos_start":[0.58137,0.12701,0.01602],"object_to_goal_dist_end":0.2399,"object_to_goal_dist_start":0.2399,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1014.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57837,0.18203,0.26768],"tcp_start":[0.58252,0.18354,0.2468],"tcp_to_object_dist_end":0.25763,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.53234,"average_solve_count":201.0,"average_success_count":201.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.arc_height":0.09102,"approach_1.speed":0.05289,"descend_1.depth":5e-05,"descend_1.speed":0.06646,"lift_1.lift_height":0.22506,"lift_1.speed":0.05783,"place_descend_1.place_z":0.03164,"place_descend_1.speed":0.04068,"transport_1.speed":0.11703,"transport_1.transport_z":0.09596},"optimized_scores":{"best_composite_score":0.02228,"best_fitness_score":0.67228,"best_task_score":0.38729},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1203.0,"contact_point_centroid":[0.57424,0.14574,-0.00275],"force_p95":0.44902,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.79901,"mean_force":0.16669,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.59595,0.14198,0.20615]},{"body_a":"world","body_b":"grasp_target","contact_count":186.0,"contact_point_centroid":[0.5084,0.03968,-0.00114],"force_p95":0.45469,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.66009,"mean_force":0.09741,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4974,0.03963,0.02688]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18892.0,"contact_point_centroid":[0.49842,0.05861,0.0757],"force_p95":0.078,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.317,"mean_force":0.05382,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49782,0.03947,0.0738]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8015.0,"contact_point_centroid":[0.53515,0.09406,0.14656],"force_p95":0.14721,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29301,"mean_force":0.07889,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53184,0.07542,0.1472]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19730.0,"contact_point_centroid":[0.49844,0.0204,0.0752],"force_p95":0.07625,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2811,"mean_force":0.0516,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49781,0.03947,0.07329]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7698.0,"contact_point_centroid":[0.5338,0.05571,0.14579],"force_p95":0.13993,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24902,"mean_force":0.0767,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53085,0.07436,0.1463]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51249,0.03981,-0.00202],"force_p95":0.1287,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14346,"mean_force":0.12457,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5002,0.03988,0.0266]},{"body_a":"world","body_b":"grasp_target","contact_count":3916.0,"contact_point_centroid":[0.51251,0.03972,-0.00196],"force_p95":0.12472,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12275,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50162,0.0674,0.23185]},{"body_a":"world","body_b":"grasp_target","contact_count":1252.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50638,0.04445,0.08114]},{"body_a":"world","body_b":"grasp_target","contact_count":560.0,"contact_point_centroid":[0.57385,0.14574,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.61509,0.16259,0.20074]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.57385,0.14574,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61563,0.16638,0.18055]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4129.0,"contact_point_centroid":[0.49965,0.05899,0.028],"force_p95":0.07557,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09528,"mean_force":0.05175,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49901,0.03978,0.02533]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4864.0,"contact_point_centroid":[0.49972,0.02072,0.02722],"force_p95":0.06796,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08954,"mean_force":0.04468,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49901,0.03978,0.02533]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1088.0,"contact_point_centroid":[0.59875,0.14462,0.2108],"force_p95":0.01251,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01556,"mean_force":0.01065,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.59851,0.1446,0.20851]},{"body_a":"left_finger","body_b":"right_finger","contact_count":603.0,"contact_point_centroid":[0.61539,0.1626,0.20314],"force_p95":0.01095,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01259,"mean_force":0.01036,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.61509,0.16258,0.20079]},{"body_a":"left_finger","body_b":"right_finger","contact_count":219.0,"contact_point_centroid":[0.61877,0.16728,0.17922],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01097,"mean_force":0.01014,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61822,0.16725,0.17699]}],"total_contact_groups":16},"final_pose_error":0.01,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.57385,0.14574,0.01602],"final_tcp_position":[0.61986,0.16759,0.1807],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1.79901,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":980.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3916.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.50811,0.04852,0.12821],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.10266,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":313.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1252.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_target","tcp_end":[0.50726,0.0405,0.03428],"tcp_start":[0.50811,0.04852,0.12821],"tcp_to_object_dist_end":0.00982,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51236,0.03995,0.02591],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12872,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10793.0,"raw_peak_contact_force":0.14346,"tcp_end":[0.49898,0.03978,0.02529],"tcp_start":[0.50726,0.0405,0.03428],"tcp_to_object_dist_end":0.0134,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51125,0.03952,0.11045],"object_pos_start":[0.51236,0.03995,0.02591],"object_to_goal_dist_end":0.18005,"object_to_goal_dist_start":0.21222,"object_z_max":0.11036,"peak_contact_force":0.07033,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":38808.0,"raw_peak_contact_force":0.66009,"subtask_id":"lift_clear","tcp_end":[0.50066,0.03952,0.11964],"tcp_start":[0.49898,0.03978,0.02529],"tcp_to_object_dist_end":0.01402,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.57385,0.14574,0.01602],"object_pos_start":[0.51125,0.03952,0.11045],"object_to_goal_dist_end":0.14229,"object_to_goal_dist_start":0.18005,"object_z_max":0.15849,"peak_contact_force":0.12263,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":18004.0,"raw_peak_contact_force":1.79901,"subtask_id":"transport_goal","tcp_end":[0.61201,0.15845,0.22087],"tcp_start":[0.50066,0.03952,0.11964],"tcp_to_object_dist_end":0.20876,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":140.0,"n_steps_budget":1000.0,"object_pos_end":[0.57385,0.14574,0.01602],"object_pos_start":[0.57385,0.14574,0.01602],"object_to_goal_dist_end":0.14229,"object_to_goal_dist_start":0.14229,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"place_descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1163.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.61986,0.16759,0.1807],"tcp_start":[0.61201,0.15845,0.22087],"tcp_to_object_dist_end":0.17237,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57385,0.14574,0.01602],"object_pos_start":[0.57385,0.14574,0.01602],"object_to_goal_dist_end":0.14229,"object_to_goal_dist_start":0.14229,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1019.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61411,0.16585,0.19999],"tcp_start":[0.61986,0.16759,0.1807],"tcp_to_object_dist_end":0.1894,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```