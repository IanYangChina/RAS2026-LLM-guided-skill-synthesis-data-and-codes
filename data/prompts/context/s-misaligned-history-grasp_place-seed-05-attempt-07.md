## Search State

- **Seed**: 5
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 9  | 0.0447 | 0.39 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 9  | 0.0447 | 0.39 | ✅ accepted |
| 5 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 9  | -0.3167 | 0.22 | ❌ rejected |
| 4 | push → release → pull → release → release → grasp → retract → approach | impedance_motion | linear_cartesian | arc_cartesian | — | linear_cartesian | — | linear_cartesian | linear_cartesian | impedance_control | admittance_control | impedance_control | position_control | admittance_control | position_control | position_control | position_control | time_limit | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 6  | -0.3167 | 0.22 | ❌ rejected |
| 3 | push → release → pull → release → release → grasp → retract → approach | impedance_motion | linear_cartesian | arc_cartesian | — | linear_cartesian | — | linear_cartesian | linear_cartesian | impedance_control | admittance_control | impedance_control | position_control | admittance_control | position_control | position_control | position_control | time_limit | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 6  | 0.0447 | 0.39 | ❌ rejected |

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

## Current Skill (Q=0.045) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_object
  anchor: object
  weight: 0.3
- id: reach_goal
  weight: 0.7
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
    - 0.12
    tolerance: 0.015
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
  guards:
  - id: contact_watch
    when: during_phase
    predicate: force_below
    threshold: 15.0
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.01
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
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.04
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
  parameters:
    grip_force:
      type: scalar
      range:
      - 5.0
      - 30.0
      default: 20.0
      binds_to:
      - path: guards.grasp_verify.threshold
        mode: replace
  guards:
  - id: grasp_verify
    when: after_phase
    predicate: bilateral_grasp
    threshold: 10.0
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - -0.005
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
      distance: 0.12
      axis: world_z
      mode: replace_offset_projection
      sign: positive
    tolerance: 0.015
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
      - 0.1
      default: 0.05
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
    tolerance: 0.015
    orientation:
      mode: keep_current
  parameters:
    goal_approach_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
- id: descend_to_goal
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
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_goal_speed:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.04
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
- id: retract_from_goal
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
      distance: 0.1
      axis: world_z
      mode: replace_offset_projection
      sign: positive
    tolerance: 0.015
    orientation:
      mode: keep_current
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    retract_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.12], tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=contact_watch, when=during_phase, predicate=force_below, on_failure=retry, threshold=15.0
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, 0.01]
- **descend_to_object** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **grasp_object** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - grip_force: status=consumed; consumers=guards.grasp_verify.threshold (replace)
  - guards:
    - id=grasp_verify, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=10.0
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, -0.005]
- **lift_object** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.12, mode=replace_offset_projection, sign=positive}, tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
- **approach_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - goal_approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_goal** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_goal_speed: status=consumed; consumers=generator.speed (replace)
- **release_object** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **retract_from_goal** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.1, mode=replace_offset_projection, sign=positive}, tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - retract_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.045
- **task_score** (E): 0.392
- **fitness_score**: 0.675  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.630

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1409 |
| descend_to_object | 1.00 | 1.00 | 0.1288 |
| grasp_object | 1.00 | 1.00 | 0.0124 |
| lift_object | 1.00 | 1.00 | 0.1507 |
| approach_goal | 0.67 | 1.00 | 0.1750 |
| descend_to_goal | 1.00 | 1.00 | 0.0850 |
| release_object | 1.00 | 1.00 | 0.0210 |
| retract_from_goal | 1.00 | 1.00 | 0.1185 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, 0.016, 0.163) | (0.516, 0.018, 0.030)→(0.516, 0.018, 0.026) | 0.234→0.236 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_object | descend | 1.00 / step_budget | (0.510, 0.016, 0.163)→(0.510, 0.018, 0.034) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 4.000 | 8.041 | 0.123 |
| grasp_object | grasp | 1.00 / step_budget | (0.510, 0.018, 0.034)→(0.502, 0.017, 0.025) | (0.516, 0.018, 0.026)→(0.515, 0.017, 0.026) | 0.236→0.237 | 1.00 / 41.000 | 0.146 | 0.219 |
| lift_object | lift | 1.00 / step_budget | (0.502, 0.017, 0.025)→(0.498, 0.017, 0.176) | (0.515, 0.017, 0.026)→(0.509, 0.017, 0.169) | 0.237→0.210 | 1.00 / 41.000 | 0.073 | 0.627 |
| approach_goal | approach | 0.67 / step_budget | (0.498, 0.017, 0.176)→(0.585, 0.147, 0.228) | (0.509, 0.017, 0.169)→(0.593, 0.147, 0.214) | 0.210→0.081 | 1.00 / 40.000 | 0.072 | 0.093 |
| descend_to_goal | descend | 1.00 / step_budget | (0.585, 0.147, 0.228)→(0.600, 0.176, 0.169) | (0.593, 0.147, 0.214)→(0.607, 0.176, 0.153) | 0.081→0.015 | 1.00 / 34.000 | 0.085 | 0.131 |
| release_object | release | 1.00 / step_budget | (0.600, 0.176, 0.169)→(0.594, 0.175, 0.189) | (0.607, 0.176, 0.153)→(0.607, 0.176, 0.014) | 0.015→0.153 | 1.00 / 4.000 | 0.101 | 1.601 |
| retract_from_goal | retract | 1.00 / step_budget | (0.594, 0.175, 0.189)→(0.592, 0.174, 0.308) | (0.607, 0.176, 0.014)→(0.607, 0.176, 0.016) | 0.153→0.151 | 1.00 / 4.000 | 0.123 | 0.125 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.541
- phase_score: 0.837
- phase_breakdown.reach_goal_score: 0.823
- phase_breakdown.reach_object_score: 0.869
- grasp_place_fitness: 0.748

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.748
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.541
- **Median Q (composite search score)**: 0.060
- **K-run variance**: 0.0045
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.351


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.0,"average_solve_count":406.0,"average_success_count":406.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.goal_approach_speed":0.02049,"approach_object.approach_speed":0.12292,"descend_to_goal.descend_goal_speed":0.03081,"descend_to_object.descend_speed":0.03335,"grasp_object.grip_force":11.93932,"lift_object.lift_height":0.18868,"lift_object.lift_speed":0.04477,"retract_from_goal.retract_height":0.1271,"retract_from_goal.retract_speed":0.09237},"optimized_scores":{"best_composite_score":0.11823,"best_fitness_score":0.74823,"best_task_score":0.54102},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":310.0,"contact_point_centroid":[0.60102,0.17537,-0.00418],"force_p95":0.81711,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.23054,"mean_force":0.23263,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.58889,0.17352,0.12412]},{"body_a":"world","body_b":"grasp_target","contact_count":113.0,"contact_point_centroid":[0.52557,0.02858,-0.0014],"force_p95":0.61298,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65281,"mean_force":0.173,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51509,0.0294,0.02591]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19298.0,"contact_point_centroid":[0.51282,0.04833,0.11297],"force_p95":0.07677,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29477,"mean_force":0.05229,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.5124,0.02923,0.11116]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18781.0,"contact_point_centroid":[0.51287,0.0101,0.11706],"force_p95":0.07843,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28629,"mean_force":0.05294,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51241,0.02923,0.11493]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53055,0.03046,-0.00212],"force_p95":0.15794,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24293,"mean_force":0.13216,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.51766,0.02958,0.02601]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":888.0,"contact_point_centroid":[0.59399,0.15583,0.11106],"force_p95":0.09774,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20021,"mean_force":0.05925,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.59339,0.17501,0.11119]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1181.0,"contact_point_centroid":[0.59514,0.19397,0.11108],"force_p95":0.07421,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18231,"mean_force":0.04612,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.59347,0.17503,0.11132]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4057.0,"contact_point_centroid":[0.51733,0.0103,0.02741],"force_p95":0.08035,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14173,"mean_force":0.05188,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.51643,0.0295,0.02465]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4845.0,"contact_point_centroid":[0.59492,0.19126,0.15751],"force_p95":0.07213,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13949,"mean_force":0.05241,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.5934,0.17217,0.15763]},{"body_a":"world","body_b":"grasp_target","contact_count":1344.0,"contact_point_centroid":[0.5305,0.03079,-0.0019],"force_p95":0.13563,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12299,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51055,0.01299,0.23174]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4737.0,"contact_point_centroid":[0.59491,0.15311,0.15808],"force_p95":0.07555,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13311,"mean_force":0.05296,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.59339,0.17216,0.15785]},{"body_a":"world","body_b":"grasp_target","contact_count":2804.0,"contact_point_centroid":[0.60338,0.17538,-0.00198],"force_p95":0.12308,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12414,"mean_force":0.1226,"phase_index":7.0,"phase_name":"retract_from_goal","phase_type":"retract","tcp_position_centroid":[0.58546,0.17241,0.19171]},{"body_a":"world","body_b":"grasp_target","contact_count":1740.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.52259,0.02835,0.09754]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14891.0,"contact_point_centroid":[0.55303,0.11932,0.19763],"force_p95":0.07861,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09554,"mean_force":0.053,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55218,0.10018,0.19682]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4988.0,"contact_point_centroid":[0.51726,0.04865,0.02644],"force_p95":0.07273,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08821,"mean_force":0.04483,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.51644,0.0295,0.02466]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16166.0,"contact_point_centroid":[0.55322,0.08198,0.19752],"force_p95":0.07378,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08273,"mean_force":0.04884,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55266,0.10101,0.19683]}],"total_contact_groups":16},"final_pose_error":0.01496,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.60338,0.17538,0.01602],"final_tcp_position":[0.58588,0.17249,0.24806],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":23.87709,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":337.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1344.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.52333,0.02684,0.16235],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13658,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":435.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":23.87709,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1740.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.52494,0.03006,0.03424],"tcp_start":[0.52333,0.02684,0.16235],"tcp_to_object_dist_end":0.00995,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53037,0.02945,0.02561],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18468,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.14993,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10845.0,"raw_peak_contact_force":0.24293,"tcp_end":[0.51641,0.02949,0.02462],"tcp_start":[0.52494,0.03006,0.03424],"tcp_to_object_dist_end":0.014,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":975.0,"n_steps_budget":1000.0,"object_pos_end":[0.52398,0.02929,0.19058],"object_pos_start":[0.53037,0.02945,0.02561],"object_to_goal_dist_end":0.18737,"object_to_goal_dist_start":0.18468,"object_z_max":0.19042,"peak_contact_force":0.06944,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":38192.0,"raw_peak_contact_force":0.65281,"tcp_end":[0.5129,0.02926,0.19877],"tcp_start":[0.51641,0.02949,0.02462],"tcp_to_object_dist_end":0.01378,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":789.0,"n_steps_budget":1000.0,"object_pos_end":[0.60118,0.16971,0.18481],"object_pos_start":[0.52398,0.02929,0.19058],"object_to_goal_dist_end":0.07723,"object_to_goal_dist_start":0.18737,"object_z_max":0.19066,"peak_contact_force":0.07294,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":31057.0,"raw_peak_contact_force":0.09554,"tcp_end":[0.59336,0.16956,0.19948],"tcp_start":[0.5129,0.02926,0.19877],"tcp_to_object_dist_end":0.01663,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":255.0,"n_steps_budget":1000.0,"object_pos_end":[0.60385,0.17552,0.09921],"object_pos_start":[0.60118,0.16971,0.18481],"object_to_goal_dist_end":0.00967,"object_to_goal_dist_start":0.07723,"object_z_max":0.18481,"peak_contact_force":0.08979,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9582.0,"raw_peak_contact_force":0.13949,"subtask_id":"reach_goal","tcp_end":[0.5958,0.17569,0.11542],"tcp_start":[0.59336,0.16956,0.19948],"tcp_to_object_dist_end":0.0181,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60345,0.1754,0.01635],"object_pos_start":[0.60385,0.17552,0.09921],"object_to_goal_dist_end":0.09181,"object_to_goal_dist_start":0.00967,"object_z_max":0.09921,"peak_contact_force":0.11686,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2379.0,"raw_peak_contact_force":1.23054,"tcp_end":[0.58877,0.17348,0.1356],"tcp_start":[0.5958,0.17569,0.11542],"tcp_to_object_dist_end":0.12017,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":701.0,"n_steps_budget":870.0,"object_pos_end":[0.60338,0.17538,0.01602],"object_pos_start":[0.60345,0.1754,0.01635],"object_to_goal_dist_end":0.09214,"object_to_goal_dist_start":0.09181,"object_z_max":0.01636,"peak_contact_force":0.12263,"phase_name":"retract_from_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2804.0,"raw_peak_contact_force":0.12414,"tcp_end":[0.58588,0.17249,0.24806],"tcp_start":[0.58877,0.17348,0.1356],"tcp_to_object_dist_end":0.23272,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.17133,"average_solve_count":286.0,"average_success_count":286.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.goal_approach_speed":0.04463,"approach_object.approach_speed":0.1157,"descend_to_goal.descend_goal_speed":0.06798,"descend_to_object.descend_speed":0.05379,"grasp_object.grip_force":17.23364,"lift_object.lift_height":0.11318,"lift_object.lift_speed":0.03987,"retract_from_goal.retract_height":0.14172,"retract_from_goal.retract_speed":0.06839},"optimized_scores":{"best_composite_score":-0.0445,"best_fitness_score":0.5855,"best_task_score":0.21275},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":156.0,"contact_point_centroid":[0.58644,0.18339,-0.00912],"force_p95":1.52279,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.05739,"mean_force":0.51157,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.57806,0.18206,0.25485]},{"body_a":"world","body_b":"grasp_target","contact_count":106.0,"contact_point_centroid":[0.49909,-0.01524,-0.00133],"force_p95":0.57983,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62273,"mean_force":0.18046,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.4894,-0.0153,0.02696]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10036.0,"contact_point_centroid":[0.48677,0.0039,0.07597],"force_p95":0.07729,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29279,"mean_force":0.05391,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48664,-0.01525,0.07343]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10575.0,"contact_point_centroid":[0.48673,-0.03435,0.07517],"force_p95":0.07578,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2745,"mean_force":0.05173,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48664,-0.01525,0.07302]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50381,-0.01551,-0.00203],"force_p95":0.13368,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1642,"mean_force":0.12573,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.4918,-0.01532,0.02705]},{"body_a":"world","body_b":"grasp_target","contact_count":1256.0,"contact_point_centroid":[0.50382,-0.01567,-0.00189],"force_p95":0.13606,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12302,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49926,-0.00654,0.23295]},{"body_a":"world","body_b":"grasp_target","contact_count":3268.0,"contact_point_centroid":[0.58826,0.18297,-0.00202],"force_p95":0.12328,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1261,"mean_force":0.1205,"phase_index":7.0,"phase_name":"retract_from_goal","phase_type":"retract","tcp_position_centroid":[0.57624,0.18133,0.32395]},{"body_a":"world","body_b":"grasp_target","contact_count":1764.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.49797,-0.01446,0.0985]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4108.0,"contact_point_centroid":[0.49117,0.00389,0.02859],"force_p95":0.07628,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11372,"mean_force":0.05174,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49063,-0.01531,0.02583]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1161.0,"contact_point_centroid":[0.58257,0.20241,0.23687],"force_p95":0.07236,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10541,"mean_force":0.04513,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.58102,0.18325,0.23678]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14012.0,"contact_point_centroid":[0.56506,0.16687,0.24375],"force_p95":0.08978,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10479,"mean_force":0.05985,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.56352,0.14773,0.24237]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17206.0,"contact_point_centroid":[0.56455,0.12921,0.24301],"force_p95":0.07267,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10013,"mean_force":0.04876,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.56371,0.14807,0.24235]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20024.0,"contact_point_centroid":[0.51492,0.0673,0.19075],"force_p95":0.07073,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09092,"mean_force":0.0497,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51473,0.0481,0.18912]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":21769.0,"contact_point_centroid":[0.514,0.02757,0.18902],"force_p95":0.06864,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08908,"mean_force":0.04627,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51404,0.04669,0.18762]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4892.0,"contact_point_centroid":[0.49122,-0.03439,0.02766],"force_p95":0.06854,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0888,"mean_force":0.04477,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49063,-0.01531,0.02583]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1166.0,"contact_point_centroid":[0.58262,0.16429,0.23722],"force_p95":0.072,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07802,"mean_force":0.04404,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.58105,0.18326,0.23686]}],"total_contact_groups":16},"final_pose_error":0.01495,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.58826,0.18297,0.01602],"final_tcp_position":[0.5769,0.18147,0.3878],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":2.05739,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":315.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1256.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.49997,-0.01358,0.16397],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13802,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":441.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1764.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.49879,-0.0154,0.03446],"tcp_start":[0.49997,-0.01358,0.16397],"tcp_to_object_dist_end":0.00983,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50367,-0.01517,0.02587],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31206,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13101,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10800.0,"raw_peak_contact_force":0.1642,"tcp_end":[0.4906,-0.01531,0.02579],"tcp_start":[0.49879,-0.0154,0.03446],"tcp_to_object_dist_end":0.01308,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":524.0,"n_steps_budget":1000.0,"object_pos_end":[0.49814,-0.01522,0.12046],"object_pos_start":[0.50367,-0.01517,0.02587],"object_to_goal_dist_end":0.25544,"object_to_goal_dist_start":0.31206,"object_z_max":0.12029,"peak_contact_force":0.07957,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":20717.0,"raw_peak_contact_force":0.62273,"tcp_end":[0.48658,-0.01524,0.12467],"tcp_start":[0.4906,-0.01531,0.02579],"tcp_to_object_dist_end":0.0123,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5514,0.1047,0.2386],"object_pos_start":[0.49814,-0.01522,0.12046],"object_to_goal_dist_end":0.09054,"object_to_goal_dist_start":0.25544,"object_z_max":0.23849,"peak_contact_force":0.06886,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":41793.0,"raw_peak_contact_force":0.09092,"tcp_end":[0.54328,0.10471,0.25076],"tcp_start":[0.48658,-0.01524,0.12467],"tcp_to_object_dist_end":0.01462,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":856.0,"n_steps_budget":1000.0,"object_pos_end":[0.58716,0.18389,0.22256],"object_pos_start":[0.5514,0.1047,0.2386],"object_to_goal_dist_end":0.0258,"object_to_goal_dist_start":0.09054,"object_z_max":0.23861,"peak_contact_force":0.09312,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":31218.0,"raw_peak_contact_force":0.10479,"subtask_id":"reach_goal","tcp_end":[0.58234,0.18359,0.24012],"tcp_start":[0.54328,0.10471,0.25076],"tcp_to_object_dist_end":0.01821,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58774,0.18185,0.00853],"object_pos_start":[0.58716,0.18389,0.22256],"object_to_goal_dist_end":0.23966,"object_to_goal_dist_start":0.0258,"object_z_max":0.22256,"peak_contact_force":0.08567,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2483.0,"raw_peak_contact_force":2.05739,"tcp_end":[0.57803,0.18206,0.26097],"tcp_start":[0.58234,0.18359,0.24012],"tcp_to_object_dist_end":0.25263,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":817.0,"n_steps_budget":1000.0,"object_pos_end":[0.58826,0.18297,0.01602],"object_pos_start":[0.58774,0.18185,0.00853],"object_to_goal_dist_end":0.23214,"object_to_goal_dist_start":0.23966,"object_z_max":0.01671,"peak_contact_force":0.12263,"phase_name":"retract_from_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3268.0,"raw_peak_contact_force":0.1261,"tcp_end":[0.5769,0.18147,0.3878],"tcp_start":[0.57803,0.18206,0.26097],"tcp_to_object_dist_end":0.37195,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.925,"average_solve_count":440.0,"average_success_count":440.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.goal_approach_speed":0.03485,"approach_object.approach_speed":0.10786,"descend_to_goal.descend_goal_speed":0.0447,"descend_to_object.descend_speed":0.05975,"grasp_object.grip_force":22.57974,"lift_object.lift_height":0.19346,"lift_object.lift_speed":0.03598,"retract_from_goal.retract_height":0.15648,"retract_from_goal.retract_speed":0.02687},"optimized_scores":{"best_composite_score":0.06034,"best_fitness_score":0.69034,"best_task_score":0.42304},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":258.0,"contact_point_centroid":[0.6265,0.16961,-0.0054],"force_p95":1.0625,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.51524,"mean_force":0.28533,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.6157,0.16814,0.162]},{"body_a":"world","body_b":"grasp_target","contact_count":116.0,"contact_point_centroid":[0.50787,0.03724,-0.00144],"force_p95":0.56497,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60632,"mean_force":0.17807,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.4978,0.03802,0.02674]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19921.0,"contact_point_centroid":[0.49523,0.05696,0.11595],"force_p95":0.07399,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28193,"mean_force":0.05056,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49521,0.03782,0.11425]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19555.0,"contact_point_centroid":[0.49528,0.01866,0.11933],"force_p95":0.07509,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26849,"mean_force":0.05067,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49523,0.03782,0.11722]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51257,0.03936,-0.00214],"force_p95":0.16542,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25018,"mean_force":0.13411,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.50033,0.03824,0.02682]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":965.0,"contact_point_centroid":[0.62061,0.15034,0.14831],"force_p95":0.08959,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15244,"mean_force":0.05455,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.61986,0.16949,0.14812]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1179.0,"contact_point_centroid":[0.62139,0.18853,0.14815],"force_p95":0.07352,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15024,"mean_force":0.04579,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.61992,0.16951,0.14825]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4461.0,"contact_point_centroid":[0.62089,0.18677,0.19414],"force_p95":0.07277,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14818,"mean_force":0.05246,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.61955,0.16766,0.19411]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4047.0,"contact_point_centroid":[0.49979,0.01894,0.02834],"force_p95":0.0816,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.148,"mean_force":0.05192,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49914,0.03814,0.02554]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4452.0,"contact_point_centroid":[0.62092,0.14859,0.19472],"force_p95":0.07242,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14393,"mean_force":0.05206,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.61955,0.16765,0.19428]},{"body_a":"world","body_b":"grasp_target","contact_count":1332.0,"contact_point_centroid":[0.51251,0.03972,-0.0019],"force_p95":0.13564,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12299,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.5029,0.01664,0.23232]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.62865,0.16961,-0.00198],"force_p95":0.12281,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12454,"mean_force":0.1224,"phase_index":7.0,"phase_name":"retract_from_goal","phase_type":"retract","tcp_position_centroid":[0.61273,0.16718,0.22899]},{"body_a":"world","body_b":"grasp_target","contact_count":1736.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.50602,0.03654,0.09795]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19144.0,"contact_point_centroid":[0.55882,0.12345,0.2189],"force_p95":0.07371,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09229,"mean_force":0.05,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55833,0.10428,0.21795]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5016.0,"contact_point_centroid":[0.49975,0.05732,0.02736],"force_p95":0.07407,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0901,"mean_force":0.04483,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49915,0.03814,0.02555]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20139.0,"contact_point_centroid":[0.55845,0.08496,0.21894],"force_p95":0.07089,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08123,"mean_force":0.04741,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55812,0.10406,0.21789]}],"total_contact_groups":16},"final_pose_error":0.04049,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.62865,0.16961,0.01602],"final_tcp_position":[0.61331,0.16729,0.28778],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1.51524,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":334.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1332.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.50759,0.03451,0.1631],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13727,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":434.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1736.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.5074,0.03881,0.03451],"tcp_start":[0.50759,0.03451,0.1631],"tcp_to_object_dist_end":0.00995,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51239,0.03813,0.02552],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21356,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.15593,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10863.0,"raw_peak_contact_force":0.25018,"tcp_end":[0.49911,0.03813,0.02551],"tcp_start":[0.5074,0.03881,0.03451],"tcp_to_object_dist_end":0.01328,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":972.0,"n_steps_budget":1000.0,"object_pos_end":[0.50619,0.03788,0.19636],"object_pos_start":[0.51239,0.03813,0.02552],"object_to_goal_dist_end":0.18841,"object_to_goal_dist_start":0.21356,"object_z_max":0.1962,"peak_contact_force":0.06949,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":39592.0,"raw_peak_contact_force":0.60632,"tcp_end":[0.49571,0.03786,0.20444],"tcp_start":[0.49911,0.03813,0.02551],"tcp_to_object_dist_end":0.01323,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":957.0,"n_steps_budget":1000.0,"object_pos_end":[0.62579,0.16583,0.21966],"object_pos_start":[0.50619,0.03788,0.19636],"object_to_goal_dist_end":0.07495,"object_to_goal_dist_start":0.18841,"object_z_max":0.21964,"peak_contact_force":0.07375,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":39283.0,"raw_peak_contact_force":0.09229,"tcp_end":[0.61905,0.16595,0.23461],"tcp_start":[0.49571,0.03786,0.20444],"tcp_to_object_dist_end":0.0164,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":234.0,"n_steps_budget":1000.0,"object_pos_end":[0.62932,0.16994,0.13647],"object_pos_start":[0.62579,0.16583,0.21966],"object_to_goal_dist_end":0.00911,"object_to_goal_dist_start":0.07495,"object_z_max":0.21966,"peak_contact_force":0.07135,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8913.0,"raw_peak_contact_force":0.14818,"subtask_id":"reach_goal","tcp_end":[0.62207,0.17011,0.15269],"tcp_start":[0.61905,0.16595,0.23461],"tcp_to_object_dist_end":0.01777,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.62878,0.16957,0.01606],"object_pos_start":[0.62932,0.16994,0.13647],"object_to_goal_dist_end":0.129,"object_to_goal_dist_start":0.00911,"object_z_max":0.13647,"peak_contact_force":0.09982,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2402.0,"raw_peak_contact_force":1.51524,"tcp_end":[0.61564,0.16812,0.17172],"tcp_start":[0.62207,0.17011,0.15269],"tcp_to_object_dist_end":0.15622,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.62865,0.16961,0.01602],"object_pos_start":[0.62878,0.16957,0.01606],"object_to_goal_dist_end":0.12904,"object_to_goal_dist_start":0.129,"object_z_max":0.01647,"peak_contact_force":0.12263,"phase_name":"retract_from_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12454,"tcp_end":[0.61331,0.16729,0.28778],"tcp_start":[0.61564,0.16812,0.17172],"tcp_to_object_dist_end":0.27221,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```