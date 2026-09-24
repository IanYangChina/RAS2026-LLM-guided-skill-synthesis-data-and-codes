## Search State

- **Seed**: 5
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.0416 | 0.32 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.0563 | 0.35 | ✅ accepted |
| 5 | push → release → pull → release → release → grasp → retract → approach | impedance_motion | linear_cartesian | arc_cartesian | — | linear_cartesian | — | linear_cartesian | linear_cartesian | impedance_control | admittance_control | impedance_control | position_control | admittance_control | position_control | position_control | position_control | time_limit | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 6 | -0.3167 | 0.22 | ❌ rejected |
| 4 | push → release → pull → release → release → grasp → retract → approach | impedance_motion | linear_cartesian | arc_cartesian | — | linear_cartesian | — | linear_cartesian | linear_cartesian | impedance_control | admittance_control | impedance_control | position_control | admittance_control | position_control | position_control | position_control | time_limit | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 6 | -0.3167 | 0.22 | ❌ rejected |
| 3 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 7 | -0.3280 | 0.21 | ❌ rejected |

**Proposal policy**: task_score is 0.32 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.042) — your mutation base

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
  offset:
  - 0.0
  - 0.0
  - 0.1
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
  - id: grasp_check
    when: during_phase
    predicate: bilateral_grasp
    threshold: 1.0
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
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_goal
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
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    place_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_goal
- id: release_object
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
- id: retract_after_place
  type: retract
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
      distance: 0.12
      axis: world_z
      mode: add_to_offset
      sign: positive
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.15
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    retract_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace

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
    - id=grasp_check, when=during_phase, predicate=bilateral_grasp, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=repeat
- **lift_object** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.1, mode=add_to_offset, sign=positive}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
- **approach_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **descend_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_speed: status=consumed; consumers=generator.speed (replace)
- **release_object** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **retract_after_place** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.12, mode=add_to_offset, sign=positive}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - retract_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.042
- **task_score** (E): 0.318
- **fitness_score**: 0.622  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.580

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1660 |
| descend_to_object | 1.00 | 1.00 | 0.0843 |
| grasp_object | 0.00 | 1.00 | 0.0073 |
| lift_object | 1.00 | 1.00 | 0.1217 |
| approach_goal | 0.00 | 1.00 | 0.0928 |
| descend_place | 0.67 | 1.00 | 0.0819 |
| release_object | 1.00 | 1.00 | 0.0222 |
| retract_after_place | 1.00 | 1.00 | 0.1161 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.511, 0.017, 0.138) | (0.516, 0.018, 0.030)→(0.516, 0.018, 0.026) | 0.234→0.236 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_object | descend | 1.00 / step_budget | (0.511, 0.017, 0.138)→(0.511, 0.018, 0.054) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_object | grasp | 0.00 / guard_failure | (0.511, 0.018, 0.054)→(0.506, 0.018, 0.048) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 40.333 | 0.143 | 0.174 |
| lift_object | lift | 1.00 / step_budget | (0.506, 0.018, 0.048)→(0.498, 0.018, 0.170) | (0.516, 0.018, 0.026)→(0.504, 0.018, 0.136) | 0.236→0.205 | 1.00 / 20.667 | 0.125 | 0.399 |
| approach_goal | approach | 0.00 / step_budget | (0.498, 0.018, 0.170)→(0.540, 0.091, 0.197) | (0.504, 0.018, 0.136)→(0.541, 0.080, 0.016) | 0.205→0.195 | 1.00 / 8.333 | 0.123 | 1.476 |
| descend_place | descend | 0.67 / step_budget | (0.540, 0.091, 0.197)→(0.579, 0.151, 0.176) | (0.541, 0.080, 0.016)→(0.541, 0.080, 0.016) | 0.195→0.195 | 1.00 / 8.333 | 0.123 | 0.123 |
| release_object | release | 1.00 / step_budget | (0.579, 0.151, 0.176)→(0.573, 0.150, 0.198) | (0.541, 0.080, 0.016)→(0.541, 0.080, 0.016) | 0.195→0.195 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract_after_place | retract | 1.00 / step_budget | (0.573, 0.150, 0.198)→(0.571, 0.149, 0.314) | (0.541, 0.080, 0.016)→(0.541, 0.080, 0.016) | 0.195→0.195 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 0.000
- terminal_score: 0.496
- phase_score: 0.197
- phase_breakdown.reach_goal_score: 0.184
- phase_breakdown.reach_object_score: 0.211
- grasp_place_fitness: 0.713

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.713
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.496
- **Median Q (composite search score)**: 0.053
- **K-run variance**: 0.0063
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.245


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.50239,"average_solve_count":209.0,"average_success_count":209.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.transport_speed":0.08965,"approach_object.approach_speed":0.04999,"descend_place.place_speed":0.06383,"descend_to_object.descend_speed":0.0806,"lift_object.lift_height":0.14757,"lift_object.lift_speed":0.09636,"retract_after_place.retract_height":0.12714,"retract_after_place.retract_speed":0.09706},"optimized_scores":{"best_composite_score":0.13264,"best_fitness_score":0.71264,"best_task_score":0.4965},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2057.0,"contact_point_centroid":[0.56874,0.14006,-0.00245],"force_p95":0.18486,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.47555,"mean_force":0.1427,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.56095,0.11946,0.18359]},{"body_a":"world","body_b":"grasp_target","contact_count":151.0,"contact_point_centroid":[0.52805,0.02947,-0.00118],"force_p95":0.27761,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.42149,"mean_force":0.06363,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51886,0.02995,0.04833]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19276.0,"contact_point_centroid":[0.51762,0.01084,0.12412],"force_p95":0.1049,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30544,"mean_force":0.0656,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51566,0.02975,0.12373]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20140.0,"contact_point_centroid":[0.51826,0.0486,0.12484],"force_p95":0.09656,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30102,"mean_force":0.06289,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51566,0.02975,0.12403]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7150.0,"contact_point_centroid":[0.53868,0.05152,0.17506],"force_p95":0.12438,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24369,"mean_force":0.09994,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53361,0.06977,0.17871]},{"body_a":"world","body_b":"grasp_target","contact_count":1604.0,"contact_point_centroid":[0.53051,0.03068,-0.00208],"force_p95":0.14225,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18256,"mean_force":0.12864,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52109,0.03011,0.04724]},{"body_a":"world","body_b":"grasp_target","contact_count":2336.0,"contact_point_centroid":[0.5305,0.03079,-0.00194],"force_p95":0.13103,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12283,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51083,0.01386,0.21794]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7532.0,"contact_point_centroid":[0.53937,0.08856,0.17526],"force_p95":0.12368,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13548,"mean_force":0.09535,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53401,0.07041,0.17886]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4105.0,"contact_point_centroid":[0.51983,0.01086,0.04827],"force_p95":0.07827,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13432,"mean_force":0.05198,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52052,0.03007,0.04657]},{"body_a":"world","body_b":"grasp_target","contact_count":3228.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.52359,0.02947,0.08331]},{"body_a":"world","body_b":"grasp_target","contact_count":3752.0,"contact_point_centroid":[0.56871,0.14016,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.58345,0.15923,0.14074]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.56871,0.14016,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.58572,0.17103,0.12547]},{"body_a":"world","body_b":"grasp_target","contact_count":3012.0,"contact_point_centroid":[0.56871,0.14016,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.58063,0.16938,0.19946]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4910.0,"contact_point_centroid":[0.52066,0.04915,0.04808],"force_p95":0.07067,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07953,"mean_force":0.04452,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52052,0.03007,0.04657]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1906.0,"contact_point_centroid":[0.56152,0.12018,0.18528],"force_p95":0.01127,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01634,"mean_force":0.01062,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.56104,0.12016,0.18302]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3999.0,"contact_point_centroid":[0.58406,0.15938,0.14286],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01292,"mean_force":0.01046,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.58351,0.15934,0.1406]}],"total_contact_groups":17},"final_pose_error":0.01456,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.56871,0.14016,0.01602],"final_tcp_position":[0.58112,0.16949,0.2581],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":1.47555,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":585.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2336.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.52417,0.02821,0.13706],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11125,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":807.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3228.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.52541,0.03039,0.05232],"tcp_start":[0.52417,0.02821,0.13706],"tcp_to_object_dist_end":0.02679,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":0.0,"n_steps_budget":50.0,"object_pos_end":[0.53042,0.03015,0.02574],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18404,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.14025,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10619.0,"raw_peak_contact_force":0.18256,"tcp_end":[0.52049,0.03007,0.04654],"tcp_start":[0.52541,0.03039,0.05232],"tcp_to_object_dist_end":0.02305,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":873.0,"n_steps_budget":960.0,"object_pos_end":[0.51884,0.03001,0.14433],"object_pos_start":[0.53042,0.03015,0.02574],"object_to_goal_dist_end":0.17385,"object_to_goal_dist_start":0.18404,"object_z_max":0.15388,"peak_contact_force":0.13072,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":39567.0,"raw_peak_contact_force":0.42149,"tcp_end":[0.51294,0.02958,0.1759],"tcp_start":[0.52049,0.03007,0.04654],"tcp_to_object_dist_end":0.03211,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56871,0.14016,0.01602],"object_pos_start":[0.51884,0.03001,0.14433],"object_to_goal_dist_end":0.10503,"object_to_goal_dist_start":0.17385,"object_z_max":0.14647,"peak_contact_force":0.12263,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":18645.0,"raw_peak_contact_force":1.47555,"subtask_id":"reach_goal","tcp_end":[0.56033,0.12014,0.1815],"tcp_start":[0.51294,0.02958,0.1759],"tcp_to_object_dist_end":0.1669,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":538.0,"n_steps_budget":1000.0,"object_pos_end":[0.56871,0.14016,0.01602],"object_pos_start":[0.56871,0.14016,0.01602],"object_to_goal_dist_end":0.10503,"object_to_goal_dist_start":0.10503,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7751.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.59038,0.17249,0.12432],"tcp_start":[0.56033,0.12014,0.1815],"tcp_to_object_dist_end":0.11509,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56871,0.14016,0.01602],"object_pos_start":[0.56871,0.14016,0.01602],"object_to_goal_dist_end":0.10503,"object_to_goal_dist_start":0.10503,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1012.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58387,0.17043,0.14522],"tcp_start":[0.59038,0.17249,0.12432],"tcp_to_object_dist_end":0.13356,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":753.0,"n_steps_budget":840.0,"object_pos_end":[0.56871,0.14016,0.01602],"object_pos_start":[0.56871,0.14016,0.01602],"object_to_goal_dist_end":0.10503,"object_to_goal_dist_start":0.10503,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3012.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58112,0.16949,0.2581],"tcp_start":[0.58387,0.17043,0.14522],"tcp_to_object_dist_end":0.24416,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.74586,"average_solve_count":181.0,"average_success_count":181.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.transport_speed":0.1046,"approach_object.approach_speed":0.07515,"descend_place.place_speed":0.06958,"descend_to_object.descend_speed":0.06783,"lift_object.lift_height":0.12483,"lift_object.lift_speed":0.0962,"retract_after_place.retract_height":0.1269,"retract_after_place.retract_speed":0.09766},"optimized_scores":{"best_composite_score":-0.06127,"best_fitness_score":0.51873,"best_task_score":0.12076},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":4426.0,"contact_point_centroid":[0.50671,-0.01316,-0.0022],"force_p95":0.12376,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.4436,"mean_force":0.13134,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51255,0.04627,0.20882]},{"body_a":"world","body_b":"grasp_target","contact_count":150.0,"contact_point_centroid":[0.50153,-0.01471,-0.00122],"force_p95":0.25295,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.3579,"mean_force":0.0531,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.4925,-0.01542,0.05307]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11792.0,"contact_point_centroid":[0.49164,0.00314,0.11569],"force_p95":0.12263,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34167,"mean_force":0.09005,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48914,-0.01536,0.11862]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13884.0,"contact_point_centroid":[0.49082,-0.03379,0.11253],"force_p95":0.12171,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32505,"mean_force":0.07737,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48927,-0.01536,0.11469]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1829.0,"contact_point_centroid":[0.49399,0.01373,0.15968],"force_p95":0.1569,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24562,"mean_force":0.10723,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.48878,-0.00446,0.16485]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1960.0,"contact_point_centroid":[0.49414,-0.02189,0.16024],"force_p95":0.12141,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16622,"mean_force":0.09774,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.48902,-0.00386,0.16533]},{"body_a":"world","body_b":"grasp_target","contact_count":1604.0,"contact_point_centroid":[0.50381,-0.01567,-0.00208],"force_p95":0.14465,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15197,"mean_force":0.12877,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49462,-0.01545,0.05173]},{"body_a":"world","body_b":"grasp_target","contact_count":2016.0,"contact_point_centroid":[0.50382,-0.01567,-0.00193],"force_p95":0.13256,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12287,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49873,-0.00698,0.21945]},{"body_a":"world","body_b":"grasp_target","contact_count":2036.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.49766,-0.0149,0.09425]},{"body_a":"world","body_b":"grasp_target","contact_count":5600.0,"contact_point_centroid":[0.5067,-0.01317,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.54261,0.11251,0.23513]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.5067,-0.01317,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.5504,0.13525,0.24263]},{"body_a":"world","body_b":"grasp_target","contact_count":2892.0,"contact_point_centroid":[0.5067,-0.01317,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.54726,0.13432,0.3177]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4088.0,"contact_point_centroid":[0.49501,0.00362,0.05102],"force_p95":0.09703,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10439,"mean_force":0.05517,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49409,-0.01544,0.05114]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4645.0,"contact_point_centroid":[0.49421,-0.03431,0.05107],"force_p95":0.07636,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08381,"mean_force":0.0463,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49409,-0.01544,0.05114]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4450.0,"contact_point_centroid":[0.51383,0.04844,0.21301],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01636,"mean_force":0.01046,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51359,0.04844,0.21071]},{"body_a":"left_finger","body_b":"right_finger","contact_count":5988.0,"contact_point_centroid":[0.54313,0.11253,0.23735],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01276,"mean_force":0.01043,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.54262,0.11252,0.23514]}],"total_contact_groups":17},"final_pose_error":0.01368,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.5067,-0.01317,0.01602],"final_tcp_position":[0.54784,0.13441,0.37613],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":1.4436,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":505.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2016.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.49958,-0.0143,0.13874],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11281,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":509.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2036.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.49884,-0.01551,0.05638],"tcp_start":[0.49958,-0.0143,0.13874],"tcp_to_object_dist_end":0.03077,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":0.0,"n_steps_budget":50.0,"object_pos_end":[0.50373,-0.01533,0.02555],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31237,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.1479,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10337.0,"raw_peak_contact_force":0.15197,"tcp_end":[0.49406,-0.01544,0.05111],"tcp_start":[0.49884,-0.01551,0.05638],"tcp_to_object_dist_end":0.02733,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":723.0,"n_steps_budget":810.0,"object_pos_end":[0.49087,-0.01543,0.12155],"object_pos_start":[0.50373,-0.01533,0.02555],"object_to_goal_dist_end":0.25768,"object_to_goal_dist_start":0.31237,"object_z_max":0.13062,"peak_contact_force":0.11332,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":25826.0,"raw_peak_contact_force":0.3579,"tcp_end":[0.48637,-0.0153,0.15883],"tcp_start":[0.49406,-0.01544,0.05111],"tcp_to_object_dist_end":0.03755,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5067,-0.01317,0.01602],"object_pos_start":[0.49087,-0.01543,0.12155],"object_to_goal_dist_end":0.3171,"object_to_goal_dist_start":0.25768,"object_z_max":0.13265,"peak_contact_force":0.12263,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":12665.0,"raw_peak_contact_force":1.4436,"subtask_id":"reach_goal","tcp_end":[0.51843,0.06216,0.2196],"tcp_start":[0.48637,-0.0153,0.15883],"tcp_to_object_dist_end":0.21738,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5067,-0.01317,0.01602],"object_pos_start":[0.5067,-0.01317,0.01602],"object_to_goal_dist_end":0.3171,"object_to_goal_dist_start":0.3171,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11588.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.55359,0.13612,0.24052],"tcp_start":[0.51843,0.06216,0.2196],"tcp_to_object_dist_end":0.27365,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5067,-0.01317,0.01602],"object_pos_start":[0.5067,-0.01317,0.01602],"object_to_goal_dist_end":0.3171,"object_to_goal_dist_start":0.3171,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1023.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.54923,0.1349,0.26283],"tcp_start":[0.55359,0.13612,0.24052],"tcp_to_object_dist_end":0.29094,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":723.0,"n_steps_budget":810.0,"object_pos_end":[0.5067,-0.01317,0.01602],"object_pos_start":[0.5067,-0.01317,0.01602],"object_to_goal_dist_end":0.3171,"object_to_goal_dist_start":0.3171,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2892.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.54784,0.13441,0.37613],"tcp_start":[0.54923,0.1349,0.26283],"tcp_to_object_dist_end":0.39135,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.37931,"average_solve_count":232.0,"average_success_count":232.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.transport_speed":0.03508,"approach_object.approach_speed":0.08578,"descend_place.place_speed":0.04739,"descend_to_object.descend_speed":0.04114,"lift_object.lift_height":0.14492,"lift_object.lift_speed":0.09778,"retract_after_place.retract_height":0.13634,"retract_after_place.retract_speed":0.09487},"optimized_scores":{"best_composite_score":0.05333,"best_fitness_score":0.63333,"best_task_score":0.33791},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2131.0,"contact_point_centroid":[0.54816,0.11299,-0.00245],"force_p95":0.1733,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.51018,"mean_force":0.14217,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.54234,0.09107,0.19147]},{"body_a":"world","body_b":"grasp_target","contact_count":144.0,"contact_point_centroid":[0.51011,0.03818,-0.00117],"force_p95":0.30499,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.418,"mean_force":0.0613,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.50131,0.03873,0.04851]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18791.0,"contact_point_centroid":[0.49985,0.01956,0.12383],"force_p95":0.10613,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30334,"mean_force":0.06575,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49811,0.03848,0.12345]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20020.0,"contact_point_centroid":[0.50051,0.05733,0.12498],"force_p95":0.09473,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30148,"mean_force":0.06188,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49808,0.03848,0.12417]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6783.0,"contact_point_centroid":[0.52033,0.0437,0.17761],"force_p95":0.12717,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24735,"mean_force":0.10209,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51566,0.06197,0.18116]},{"body_a":"world","body_b":"grasp_target","contact_count":1604.0,"contact_point_centroid":[0.51252,0.0396,-0.00209],"force_p95":0.14455,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18847,"mean_force":0.12933,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.50345,0.03892,0.04735]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7462.0,"contact_point_centroid":[0.52106,0.08043,0.1779],"force_p95":0.12458,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14301,"mean_force":0.09362,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51603,0.06232,0.18136]},{"body_a":"world","body_b":"grasp_target","contact_count":2108.0,"contact_point_centroid":[0.51251,0.03972,-0.00193],"force_p95":0.13221,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12286,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.5028,0.01775,0.21881]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4102.0,"contact_point_centroid":[0.50218,0.01966,0.04835],"force_p95":0.07866,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13728,"mean_force":0.052,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.50289,0.03887,0.04672]},{"body_a":"world","body_b":"grasp_target","contact_count":3264.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.50644,0.03811,0.08164]},{"body_a":"world","body_b":"grasp_target","contact_count":5600.0,"contact_point_centroid":[0.54813,0.11309,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.57823,0.12926,0.17322]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.54813,0.11309,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.58835,0.14374,0.16469]},{"body_a":"world","body_b":"grasp_target","contact_count":3252.0,"contact_point_centroid":[0.54813,0.11309,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.58392,0.14247,0.24335]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4926.0,"contact_point_centroid":[0.50302,0.05796,0.04818],"force_p95":0.07114,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07178,"mean_force":0.04445,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.50289,0.03887,0.04672]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1999.0,"contact_point_centroid":[0.543,0.09155,0.19337],"force_p95":0.01149,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01609,"mean_force":0.01059,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.54252,0.09153,0.19113]},{"body_a":"left_finger","body_b":"right_finger","contact_count":216.0,"contact_point_centroid":[0.59175,0.14456,0.16304],"force_p95":0.01107,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01285,"mean_force":0.01029,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.59115,0.14452,0.1607]}],"total_contact_groups":17},"final_pose_error":0.01437,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.54813,0.11309,0.01602],"final_tcp_position":[0.58454,0.14258,0.30663],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1.51018,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":528.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2108.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.50775,0.03631,0.13784],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11197,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":816.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3264.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.50764,0.03926,0.05208],"tcp_start":[0.50775,0.03631,0.13784],"tcp_to_object_dist_end":0.02652,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":0.0,"n_steps_budget":50.0,"object_pos_end":[0.51243,0.039,0.02571],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21289,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.14227,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10632.0,"raw_peak_contact_force":0.18847,"tcp_end":[0.50286,0.03887,0.04669],"tcp_start":[0.50764,0.03926,0.05208],"tcp_to_object_dist_end":0.02306,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":843.0,"n_steps_budget":930.0,"object_pos_end":[0.50114,0.03887,0.1426],"object_pos_start":[0.51243,0.039,0.02571],"object_to_goal_dist_end":0.18399,"object_to_goal_dist_start":0.21289,"object_z_max":0.15185,"peak_contact_force":0.13177,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":38955.0,"raw_peak_contact_force":0.418,"tcp_end":[0.49538,0.03827,0.174],"tcp_start":[0.50286,0.03887,0.04669],"tcp_to_object_dist_end":0.03193,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54813,0.11309,0.01602],"object_pos_start":[0.50114,0.03887,0.1426],"object_to_goal_dist_end":0.16274,"object_to_goal_dist_start":0.18399,"object_z_max":0.1521,"peak_contact_force":0.12263,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":18375.0,"raw_peak_contact_force":1.51018,"subtask_id":"reach_goal","tcp_end":[0.54181,0.09158,0.18957],"tcp_start":[0.49538,0.03827,0.174],"tcp_to_object_dist_end":0.17499,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54813,0.11309,0.01602],"object_pos_start":[0.54813,0.11309,0.01602],"object_to_goal_dist_end":0.16274,"object_to_goal_dist_start":0.16274,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11538.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.59256,0.14489,0.16348],"tcp_start":[0.54181,0.09158,0.18957],"tcp_to_object_dist_end":0.15726,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54813,0.11309,0.01602],"object_pos_start":[0.54813,0.11309,0.01602],"object_to_goal_dist_end":0.16274,"object_to_goal_dist_start":0.16274,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1016.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58671,0.14327,0.18448],"tcp_start":[0.59256,0.14489,0.16348],"tcp_to_object_dist_end":0.17543,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":813.0,"n_steps_budget":900.0,"object_pos_end":[0.54813,0.11309,0.01602],"object_pos_start":[0.54813,0.11309,0.01602],"object_to_goal_dist_end":0.16274,"object_to_goal_dist_start":0.16274,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3252.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58454,0.14258,0.30663],"tcp_start":[0.58671,0.14327,0.18448],"tcp_to_object_dist_end":0.29436,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```