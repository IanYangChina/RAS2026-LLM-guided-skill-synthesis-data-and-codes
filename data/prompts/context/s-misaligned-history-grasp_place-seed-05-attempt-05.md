## Search State

- **Seed**: 5
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 9  | -0.3167 | 0.22 | ❌ rejected |
| 4 | push → release → pull → release → release → grasp → retract → approach | impedance_motion | linear_cartesian | arc_cartesian | — | linear_cartesian | — | linear_cartesian | linear_cartesian | impedance_control | admittance_control | impedance_control | position_control | admittance_control | position_control | position_control | position_control | time_limit | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 6  | -0.3167 | 0.22 | ❌ rejected |
| 3 | push → release → pull → release → release → grasp → retract → approach | impedance_motion | linear_cartesian | arc_cartesian | — | linear_cartesian | — | linear_cartesian | linear_cartesian | impedance_control | admittance_control | impedance_control | position_control | admittance_control | position_control | position_control | position_control | time_limit | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 6  | -0.3167 | 0.22 | ✅ accepted |
| 2 | push → release → pull → release → release → grasp → retract → approach | impedance_motion | linear_cartesian | arc_cartesian | — | linear_cartesian | — | linear_cartesian | linear_cartesian | impedance_control | admittance_control | impedance_control | position_control | admittance_control | position_control | position_control | position_control | time_limit | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 6  | -0.3167 | 0.22 | ❌ rejected |
| 1 | push → release → pull → release → release → grasp → retract → approach | impedance_motion | linear_cartesian | arc_cartesian | — | linear_cartesian | — | linear_cartesian | linear_cartesian | impedance_control | admittance_control | impedance_control | position_control | admittance_control | position_control | position_control | position_control | time_limit | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 6  | 0.0447 | 0.39 | ✅ accepted |

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
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.630

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1410 |
| descend_to_object | 1.00 | 1.00 | 0.1288 |
| grasp_object | 1.00 | 1.00 | 0.0123 |
| lift_object | 1.00 | 1.00 | 0.1251 |
| approach_goal | 0.67 | 1.00 | 0.1795 |
| descend_to_goal | 1.00 | 1.00 | 0.0816 |
| release_object | 1.00 | 1.00 | 0.0210 |
| retract_from_goal | 1.00 | 1.00 | 0.1034 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, 0.016, 0.163) | (0.516, 0.018, 0.030)→(0.516, 0.018, 0.026) | 0.234→0.236 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_object | descend | 1.00 / step_budget | (0.510, 0.016, 0.163)→(0.510, 0.018, 0.034) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 4.000 | 6.575 | 0.123 |
| grasp_object | grasp | 1.00 / step_budget | (0.510, 0.018, 0.034)→(0.502, 0.017, 0.025) | (0.516, 0.018, 0.026)→(0.515, 0.017, 0.026) | 0.236→0.237 | 1.00 / 41.000 | 0.146 | 0.219 |
| lift_object | lift | 1.00 / step_budget | (0.502, 0.017, 0.025)→(0.498, 0.017, 0.150) | (0.515, 0.017, 0.026)→(0.510, 0.017, 0.145) | 0.237→0.201 | 1.00 / 41.000 | 0.073 | 0.608 |
| approach_goal | approach | 0.67 / step_budget | (0.498, 0.017, 0.150)→(0.585, 0.146, 0.229) | (0.510, 0.017, 0.145)→(0.592, 0.146, 0.215) | 0.201→0.077 | 1.00 / 38.333 | 524.418 | 0.090 |
| descend_to_goal | descend | 1.00 / step_budget | (0.585, 0.146, 0.229)→(0.600, 0.176, 0.169) | (0.592, 0.146, 0.215)→(0.606, 0.176, 0.153) | 0.077→0.015 | 1.00 / 36.000 | 0.079 | 0.125 |
| release_object | release | 1.00 / step_budget | (0.600, 0.176, 0.169)→(0.594, 0.174, 0.189) | (0.606, 0.176, 0.153)→(0.607, 0.177, 0.014) | 0.015→0.153 | 1.00 / 4.000 | 0.102 | 1.595 |
| retract_from_goal | retract | 1.00 / step_budget | (0.594, 0.174, 0.189)→(0.592, 0.173, 0.293) | (0.607, 0.177, 0.014)→(0.607, 0.177, 0.016) | 0.153→0.151 | 1.00 / 4.000 | 0.123 | 0.125 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.541
- phase_score: 0.836
- phase_breakdown.reach_goal_score: 0.822
- phase_breakdown.reach_object_score: 0.868
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
- **Final σ (mean)**: 0.332


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.89655,"average_solve_count":406.0,"average_success_count":406.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.goal_approach_speed":0.05226,"approach_object.approach_speed":0.06745,"descend_to_goal.descend_goal_speed":0.03557,"descend_to_object.descend_speed":0.0273,"grasp_object.grip_force":18.51643,"lift_object.lift_height":0.1053,"lift_object.lift_speed":0.03102,"retract_from_goal.retract_height":0.14542,"retract_from_goal.retract_speed":0.04651},"optimized_scores":{"best_composite_score":0.11831,"best_fitness_score":0.74831,"best_task_score":0.5412},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":301.0,"contact_point_centroid":[0.60049,0.1786,-0.00415],"force_p95":0.84817,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.22263,"mean_force":0.24264,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.5882,0.17251,0.12333]},{"body_a":"world","body_b":"grasp_target","contact_count":124.0,"contact_point_centroid":[0.52567,0.02884,-0.00143],"force_p95":0.53743,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57601,"mean_force":0.17788,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51499,0.02939,0.02584]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10317.0,"contact_point_centroid":[0.51273,0.04826,0.06987],"force_p95":0.07838,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26329,"mean_force":0.05322,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51225,0.02922,0.06783]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9401.0,"contact_point_centroid":[0.51285,0.01008,0.07193],"force_p95":0.08324,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25247,"mean_force":0.05679,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51226,0.02922,0.06931]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53055,0.03046,-0.00212],"force_p95":0.15801,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24289,"mean_force":0.13218,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.51765,0.02958,0.02607]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1264.0,"contact_point_centroid":[0.59383,0.193,0.11054],"force_p95":0.07444,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19149,"mean_force":0.04481,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.59276,0.17401,0.11022]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":860.0,"contact_point_centroid":[0.59267,0.15485,0.11062],"force_p95":0.0972,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17973,"mean_force":0.06033,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.59278,0.17402,0.11024]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4057.0,"contact_point_centroid":[0.51733,0.0103,0.02747],"force_p95":0.08036,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14181,"mean_force":0.05188,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.51642,0.0295,0.02471]},{"body_a":"world","body_b":"grasp_target","contact_count":1428.0,"contact_point_centroid":[0.5305,0.03079,-0.00191],"force_p95":0.13543,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12297,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51038,0.01297,0.23175]},{"body_a":"world","body_b":"grasp_target","contact_count":3812.0,"contact_point_centroid":[0.60362,0.17863,-0.00199],"force_p95":0.12282,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12466,"mean_force":0.12259,"phase_index":7.0,"phase_name":"retract_from_goal","phase_type":"retract","tcp_position_centroid":[0.58485,0.17142,0.19952]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4234.0,"contact_point_centroid":[0.59194,0.1496,0.15193],"force_p95":0.08814,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12299,"mean_force":0.05773,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.59125,0.16868,0.15131]},{"body_a":"world","body_b":"grasp_target","contact_count":1788.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.52251,0.02834,0.09759]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4731.0,"contact_point_centroid":[0.5921,0.18738,0.15283],"force_p95":0.07456,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11964,"mean_force":0.05261,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.59112,0.16846,0.15276]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20723.0,"contact_point_centroid":[0.55093,0.07995,0.15408],"force_p95":0.07069,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09146,"mean_force":0.04839,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55065,0.09908,0.15281]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4989.0,"contact_point_centroid":[0.51725,0.04865,0.0265],"force_p95":0.07274,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08825,"mean_force":0.04482,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.51643,0.0295,0.02471]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20151.0,"contact_point_centroid":[0.55263,0.12101,0.15554],"force_p95":0.0705,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08425,"mean_force":0.04961,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5523,0.10184,0.15444]}],"total_contact_groups":16},"final_pose_error":0.01491,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.60362,0.17863,0.01602],"final_tcp_position":[0.58543,0.17155,0.26535],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":19.47964,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":358.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1428.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.52324,0.02683,0.16234],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13657,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":447.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":19.47964,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1788.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.52491,0.03006,0.03427],"tcp_start":[0.52324,0.02683,0.16234],"tcp_to_object_dist_end":0.01,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53037,0.02945,0.02561],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18468,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.15,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10846.0,"raw_peak_contact_force":0.24289,"tcp_end":[0.51639,0.02949,0.02467],"tcp_start":[0.52491,0.03006,0.03427],"tcp_to_object_dist_end":0.01401,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":521.0,"n_steps_budget":1000.0,"object_pos_end":[0.52465,0.02927,0.11185],"object_pos_start":[0.53037,0.02945,0.02561],"object_to_goal_dist_end":0.16798,"object_to_goal_dist_start":0.18468,"object_z_max":0.11169,"peak_contact_force":0.0805,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":19842.0,"raw_peak_contact_force":0.57601,"tcp_end":[0.51216,0.02922,0.11562],"tcp_start":[0.51639,0.02949,0.02467],"tcp_to_object_dist_end":0.01305,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":35.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.59811,0.16319,0.17858],"object_pos_start":[0.52465,0.02927,0.11185],"object_to_goal_dist_end":0.07223,"object_to_goal_dist_start":0.16798,"object_z_max":0.17852,"peak_contact_force":0.08931,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":40874.0,"raw_peak_contact_force":0.09146,"tcp_end":[0.58955,0.16348,0.19137],"tcp_start":[0.51216,0.02922,0.11562],"tcp_to_object_dist_end":0.01539,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":248.0,"n_steps_budget":1000.0,"object_pos_end":[0.60274,0.17452,0.09925],"object_pos_start":[0.59811,0.16319,0.17858],"object_to_goal_dist_end":0.0098,"object_to_goal_dist_start":0.07223,"object_z_max":0.17858,"peak_contact_force":0.07294,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8965.0,"raw_peak_contact_force":0.12299,"subtask_id":"reach_goal","tcp_end":[0.59509,0.17462,0.11431],"tcp_start":[0.58955,0.16348,0.19137],"tcp_to_object_dist_end":0.01689,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60373,0.17868,0.01631],"object_pos_start":[0.60274,0.17452,0.09925],"object_to_goal_dist_end":0.0918,"object_to_goal_dist_start":0.0098,"object_z_max":0.09925,"peak_contact_force":0.11888,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2425.0,"raw_peak_contact_force":1.22263,"tcp_end":[0.58808,0.17247,0.13458],"tcp_start":[0.59509,0.17462,0.11431],"tcp_to_object_dist_end":0.11946,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":953.0,"n_steps_budget":1000.0,"object_pos_end":[0.60362,0.17863,0.01602],"object_pos_start":[0.60373,0.17868,0.01631],"object_to_goal_dist_end":0.09209,"object_to_goal_dist_start":0.0918,"object_z_max":0.01633,"peak_contact_force":0.12263,"phase_name":"retract_from_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3812.0,"raw_peak_contact_force":0.12466,"tcp_end":[0.58543,0.17155,0.26535],"tcp_start":[0.58808,0.17247,0.13458],"tcp_to_object_dist_end":0.2501,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.10611,"average_solve_count":311.0,"average_success_count":311.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.goal_approach_speed":0.02899,"approach_object.approach_speed":0.09643,"descend_to_goal.descend_goal_speed":0.03662,"descend_to_object.descend_speed":0.05664,"grasp_object.grip_force":15.52254,"lift_object.lift_height":0.12671,"lift_object.lift_speed":0.03847,"retract_from_goal.retract_height":0.10141,"retract_from_goal.retract_speed":0.06526},"optimized_scores":{"best_composite_score":-0.04436,"best_fitness_score":0.58564,"best_task_score":0.21273},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":155.0,"contact_point_centroid":[0.58609,0.18261,-0.00904],"force_p95":1.52167,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.04438,"mean_force":0.51501,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.57779,0.18153,0.25534]},{"body_a":"world","body_b":"grasp_target","contact_count":107.0,"contact_point_centroid":[0.49929,-0.01506,-0.00133],"force_p95":0.57616,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.61427,"mean_force":0.17871,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.4895,-0.0153,0.02697]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11704.0,"contact_point_centroid":[0.48672,0.00391,0.08371],"force_p95":0.07659,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28838,"mean_force":0.0523,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48673,-0.01525,0.08138]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12112.0,"contact_point_centroid":[0.48671,-0.03437,0.08231],"force_p95":0.0742,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2705,"mean_force":0.05098,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48673,-0.01525,0.08034]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50381,-0.01551,-0.00203],"force_p95":0.13364,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16398,"mean_force":0.12573,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.4919,-0.01532,0.02706]},{"body_a":"world","body_b":"grasp_target","contact_count":1272.0,"contact_point_centroid":[0.50382,-0.01567,-0.0019],"force_p95":0.13583,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12301,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49928,-0.00653,0.23303]},{"body_a":"world","body_b":"grasp_target","contact_count":2256.0,"contact_point_centroid":[0.58809,0.18235,-0.00204],"force_p95":0.12388,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12585,"mean_force":0.11958,"phase_index":7.0,"phase_name":"retract_from_goal","phase_type":"retract","tcp_position_centroid":[0.57579,0.18076,0.30452]},{"body_a":"world","body_b":"grasp_target","contact_count":1764.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.498,-0.01445,0.09842]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4108.0,"contact_point_centroid":[0.49123,0.00389,0.0286],"force_p95":0.07626,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11374,"mean_force":0.05174,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49072,-0.01531,0.02583]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1167.0,"contact_point_centroid":[0.58224,0.20188,0.23737],"force_p95":0.07245,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11325,"mean_force":0.04506,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.58075,0.18272,0.23724]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13211.0,"contact_point_centroid":[0.56583,0.16831,0.24838],"force_p95":0.08933,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10809,"mean_force":0.05855,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.56437,0.14917,0.24703]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15923.0,"contact_point_centroid":[0.56523,0.13037,0.24772],"force_p95":0.07265,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09219,"mean_force":0.04859,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.56442,0.14925,0.24703]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4891.0,"contact_point_centroid":[0.49129,-0.03439,0.02767],"force_p95":0.06853,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08869,"mean_force":0.04478,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49072,-0.01531,0.02584]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":21731.0,"contact_point_centroid":[0.5153,0.02964,0.20042],"force_p95":0.06856,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08693,"mean_force":0.04622,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51531,0.04878,0.19902]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1165.0,"contact_point_centroid":[0.58229,0.16374,0.23773],"force_p95":0.07185,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0854,"mean_force":0.04418,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.58078,0.18273,0.23731]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20167.0,"contact_point_centroid":[0.51612,0.06924,0.20187],"force_p95":0.07038,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08319,"mean_force":0.04929,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51593,0.05004,0.20029]}],"total_contact_groups":16},"final_pose_error":0.01489,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.58809,0.18235,0.01602],"final_tcp_position":[0.57615,0.18082,0.34805],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":1573.09317,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":319.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1272.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.50003,-0.01356,0.16415],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1382,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":441.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1764.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.49889,-0.0154,0.03447],"tcp_start":[0.50003,-0.01356,0.16415],"tcp_to_object_dist_end":0.00979,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50367,-0.01518,0.02587],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31206,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13099,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10799.0,"raw_peak_contact_force":0.16398,"tcp_end":[0.49069,-0.01531,0.0258],"tcp_start":[0.49889,-0.0154,0.03447],"tcp_to_object_dist_end":0.01298,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":593.0,"n_steps_budget":1000.0,"object_pos_end":[0.49813,-0.01525,0.13331],"object_pos_start":[0.50367,-0.01518,0.02587],"object_to_goal_dist_end":0.2493,"object_to_goal_dist_start":0.31206,"object_z_max":0.13314,"peak_contact_force":0.07013,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":23923.0,"raw_peak_contact_force":0.61427,"tcp_end":[0.48677,-0.01524,0.13807],"tcp_start":[0.49069,-0.01531,0.0258],"tcp_to_object_dist_end":0.01231,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55338,0.10888,0.24799],"object_pos_start":[0.49813,-0.01525,0.13331],"object_to_goal_dist_end":0.08542,"object_to_goal_dist_start":0.2493,"object_z_max":0.24787,"peak_contact_force":1573.09317,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":41898.0,"raw_peak_contact_force":0.08693,"tcp_end":[0.54555,0.1089,0.26047],"tcp_start":[0.48677,-0.01524,0.13807],"tcp_to_object_dist_end":0.01474,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":789.0,"n_steps_budget":1000.0,"object_pos_end":[0.58686,0.18334,0.22319],"object_pos_start":[0.55338,0.10888,0.24799],"object_to_goal_dist_end":0.02526,"object_to_goal_dist_start":0.08542,"object_z_max":0.248,"peak_contact_force":0.09302,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":29134.0,"raw_peak_contact_force":0.10809,"subtask_id":"reach_goal","tcp_end":[0.58208,0.18304,0.24058],"tcp_start":[0.54555,0.1089,0.26047],"tcp_to_object_dist_end":0.01804,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58755,0.18138,0.00854],"object_pos_start":[0.58686,0.18334,0.22319],"object_to_goal_dist_end":0.23966,"object_to_goal_dist_start":0.02526,"object_z_max":0.22319,"peak_contact_force":0.08616,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2487.0,"raw_peak_contact_force":2.04438,"tcp_end":[0.57776,0.18152,0.26144],"tcp_start":[0.58208,0.18304,0.24058],"tcp_to_object_dist_end":0.25309,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":564.0,"n_steps_budget":990.0,"object_pos_end":[0.58809,0.18235,0.01602],"object_pos_start":[0.58755,0.18138,0.00854],"object_to_goal_dist_end":0.23216,"object_to_goal_dist_start":0.23966,"object_z_max":0.01669,"peak_contact_force":0.12263,"phase_name":"retract_from_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2256.0,"raw_peak_contact_force":0.12585,"tcp_end":[0.57615,0.18082,0.34805],"tcp_start":[0.57776,0.18152,0.26144],"tcp_to_object_dist_end":0.33225,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.01804,"average_solve_count":388.0,"average_success_count":388.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.goal_approach_speed":0.03336,"approach_object.approach_speed":0.05319,"descend_to_goal.descend_goal_speed":0.05683,"descend_to_object.descend_speed":0.06761,"grasp_object.grip_force":17.64398,"lift_object.lift_height":0.18632,"lift_object.lift_speed":0.04257,"retract_from_goal.retract_height":0.10739,"retract_from_goal.retract_speed":0.0487},"optimized_scores":{"best_composite_score":0.06027,"best_fitness_score":0.69027,"best_task_score":0.42304},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":258.0,"contact_point_centroid":[0.62619,0.1695,-0.0054],"force_p95":1.06587,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.51857,"mean_force":0.28545,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.61573,0.16817,0.16202]},{"body_a":"world","body_b":"grasp_target","contact_count":113.0,"contact_point_centroid":[0.50766,0.03739,-0.00142],"force_p95":0.59736,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63379,"mean_force":0.1714,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49781,0.03803,0.02678]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18797.0,"contact_point_centroid":[0.49527,0.05695,0.11234],"force_p95":0.07481,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29283,"mean_force":0.0511,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49516,0.03782,0.11059]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18334.0,"contact_point_centroid":[0.49533,0.01868,0.11582],"force_p95":0.07632,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27999,"mean_force":0.05153,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49518,0.03783,0.11367]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51257,0.03936,-0.00214],"force_p95":0.16535,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24987,"mean_force":0.13409,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.50029,0.03824,0.02666]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":981.0,"contact_point_centroid":[0.62068,0.15038,0.14843],"force_p95":0.08933,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15157,"mean_force":0.05364,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.61989,0.16952,0.14815]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1179.0,"contact_point_centroid":[0.62139,0.18856,0.14822],"force_p95":0.07334,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14978,"mean_force":0.04575,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.61994,0.16954,0.14826]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4047.0,"contact_point_centroid":[0.49976,0.01895,0.02818],"force_p95":0.08157,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14723,"mean_force":0.05192,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.4991,0.03815,0.02538]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4439.0,"contact_point_centroid":[0.621,0.18683,0.1943],"force_p95":0.07284,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14482,"mean_force":0.05277,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.61968,0.16778,0.19419]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4234.0,"contact_point_centroid":[0.62087,0.14875,0.19334],"force_p95":0.08627,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14002,"mean_force":0.0545,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.6197,0.16782,0.19287]},{"body_a":"world","body_b":"grasp_target","contact_count":1432.0,"contact_point_centroid":[0.51251,0.03972,-0.00191],"force_p95":0.13533,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12297,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.5028,0.01664,0.23226]},{"body_a":"world","body_b":"grasp_target","contact_count":2944.0,"contact_point_centroid":[0.62833,0.16949,-0.00198],"force_p95":0.12317,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12456,"mean_force":0.12232,"phase_index":7.0,"phase_name":"retract_from_goal","phase_type":"retract","tcp_position_centroid":[0.61269,0.1672,0.21784]},{"body_a":"world","body_b":"grasp_target","contact_count":1688.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.50601,0.03659,0.09781]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19942.0,"contact_point_centroid":[0.55903,0.12377,0.21527],"force_p95":0.07321,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09034,"mean_force":0.04952,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55856,0.1046,0.21443]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5017.0,"contact_point_centroid":[0.49973,0.05733,0.02719],"force_p95":0.07404,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08971,"mean_force":0.04482,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49911,0.03815,0.02539]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20721.0,"contact_point_centroid":[0.55852,0.08509,0.2153],"force_p95":0.07149,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08027,"mean_force":0.04753,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55817,0.1042,0.21431]}],"total_contact_groups":16},"final_pose_error":0.01499,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.62833,0.16949,0.01602],"final_tcp_position":[0.61303,0.16725,0.2644],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1.51857,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":359.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1432.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.50757,0.03459,0.16282],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13698,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":422.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1688.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.50736,0.03882,0.03434],"tcp_start":[0.50757,0.03459,0.16282],"tcp_to_object_dist_end":0.00983,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51239,0.03813,0.02552],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21356,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.15586,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10864.0,"raw_peak_contact_force":0.24987,"tcp_end":[0.49907,0.03814,0.02535],"tcp_start":[0.50736,0.03882,0.03434],"tcp_to_object_dist_end":0.01332,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":926.0,"n_steps_budget":1000.0,"object_pos_end":[0.50631,0.03789,0.18928],"object_pos_start":[0.51239,0.03813,0.02552],"object_to_goal_dist_end":0.18652,"object_to_goal_dist_start":0.21356,"object_z_max":0.18912,"peak_contact_force":0.06951,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":37244.0,"raw_peak_contact_force":0.63379,"tcp_end":[0.49561,0.03786,0.19725],"tcp_start":[0.49907,0.03814,0.02535],"tcp_to_object_dist_end":0.01334,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":987.0,"n_steps_budget":1000.0,"object_pos_end":[0.626,0.16603,0.21922],"object_pos_start":[0.50631,0.03789,0.18928],"object_to_goal_dist_end":0.07449,"object_to_goal_dist_start":0.18652,"object_z_max":0.21919,"peak_contact_force":0.07146,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":40663.0,"raw_peak_contact_force":0.09034,"tcp_end":[0.61923,0.16615,0.23436],"tcp_start":[0.49561,0.03786,0.19725],"tcp_to_object_dist_end":0.01659,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":232.0,"n_steps_budget":1000.0,"object_pos_end":[0.62878,0.16996,0.13628],"object_pos_start":[0.626,0.16603,0.21922],"object_to_goal_dist_end":0.00919,"object_to_goal_dist_start":0.07449,"object_z_max":0.21922,"peak_contact_force":0.07184,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8673.0,"raw_peak_contact_force":0.14482,"subtask_id":"reach_goal","tcp_end":[0.62209,0.17014,0.15271],"tcp_start":[0.61923,0.16615,0.23436],"tcp_to_object_dist_end":0.01774,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.62845,0.16945,0.01607],"object_pos_start":[0.62878,0.16996,0.13628],"object_to_goal_dist_end":0.129,"object_to_goal_dist_start":0.00919,"object_z_max":0.13628,"peak_contact_force":0.10001,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2418.0,"raw_peak_contact_force":1.51857,"tcp_end":[0.61566,0.16815,0.17173],"tcp_start":[0.62209,0.17014,0.15271],"tcp_to_object_dist_end":0.1562,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":736.0,"n_steps_budget":1000.0,"object_pos_end":[0.62833,0.16949,0.01602],"object_pos_start":[0.62845,0.16945,0.01607],"object_to_goal_dist_end":0.12904,"object_to_goal_dist_start":0.129,"object_z_max":0.01647,"peak_contact_force":0.12263,"phase_name":"retract_from_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2944.0,"raw_peak_contact_force":0.12456,"tcp_end":[0.61303,0.16725,0.2644],"tcp_start":[0.61566,0.16815,0.17173],"tcp_to_object_dist_end":0.24886,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```