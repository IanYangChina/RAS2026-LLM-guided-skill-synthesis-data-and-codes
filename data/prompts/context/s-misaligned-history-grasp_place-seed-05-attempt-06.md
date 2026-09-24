## Search State

- **Seed**: 5
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 9  | 0.0447 | 0.39 | ✅ accepted |
| 5 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 9  | -0.3167 | 0.22 | ❌ rejected |
| 4 | push → release → pull → release → release → grasp → retract → approach | impedance_motion | linear_cartesian | arc_cartesian | — | linear_cartesian | — | linear_cartesian | linear_cartesian | impedance_control | admittance_control | impedance_control | position_control | admittance_control | position_control | position_control | position_control | time_limit | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 6  | -0.3167 | 0.22 | ❌ rejected |
| 3 | push → release → pull → release → release → grasp → retract → approach | impedance_motion | linear_cartesian | arc_cartesian | — | linear_cartesian | — | linear_cartesian | linear_cartesian | impedance_control | admittance_control | impedance_control | position_control | admittance_control | position_control | position_control | position_control | time_limit | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 6  | -0.3167 | 0.22 | ✅ accepted |
| 2 | push → release → pull → release → release → grasp → retract → approach | impedance_motion | linear_cartesian | arc_cartesian | — | linear_cartesian | — | linear_cartesian | linear_cartesian | impedance_control | admittance_control | impedance_control | position_control | admittance_control | position_control | position_control | position_control | time_limit | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 6  | 0.0447 | 0.39 | ❌ rejected |

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
| descend_to_object | 1.00 | 1.00 | 0.1287 |
| grasp_object | 1.00 | 1.00 | 0.0123 |
| lift_object | 1.00 | 1.00 | 0.1628 |
| approach_goal | 0.67 | 1.00 | 0.1755 |
| descend_to_goal | 1.00 | 1.00 | 0.0827 |
| release_object | 1.00 | 1.00 | 0.0210 |
| retract_from_goal | 1.00 | 1.00 | 0.0951 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, 0.016, 0.163) | (0.516, 0.018, 0.030)→(0.516, 0.018, 0.026) | 0.234→0.236 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_object | descend | 1.00 / step_budget | (0.510, 0.016, 0.163)→(0.510, 0.018, 0.034) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_object | grasp | 1.00 / step_budget | (0.510, 0.018, 0.034)→(0.502, 0.017, 0.025) | (0.516, 0.018, 0.026)→(0.515, 0.017, 0.026) | 0.236→0.237 | 1.00 / 41.000 | 0.146 | 0.219 |
| lift_object | lift | 1.00 / step_budget | (0.502, 0.017, 0.025)→(0.499, 0.017, 0.188) | (0.515, 0.017, 0.026)→(0.509, 0.017, 0.181) | 0.237→0.207 | 1.00 / 43.000 | 0.070 | 0.635 |
| approach_goal | approach | 0.67 / step_budget | (0.499, 0.017, 0.188)→(0.587, 0.150, 0.235) | (0.509, 0.017, 0.181)→(0.594, 0.150, 0.221) | 0.207→0.078 | 1.00 / 39.333 | 0.075 | 0.091 |
| descend_to_goal | descend | 1.00 / step_budget | (0.587, 0.150, 0.235)→(0.600, 0.176, 0.170) | (0.594, 0.150, 0.221)→(0.607, 0.176, 0.153) | 0.078→0.014 | 1.00 / 38.000 | 0.072 | 0.137 |
| release_object | release | 1.00 / step_budget | (0.600, 0.176, 0.170)→(0.594, 0.174, 0.190) | (0.607, 0.176, 0.153)→(0.606, 0.176, 0.013) | 0.014→0.154 | 1.00 / 4.000 | 0.099 | 1.590 |
| retract_from_goal | retract | 1.00 / step_budget | (0.594, 0.174, 0.190)→(0.591, 0.173, 0.285) | (0.606, 0.176, 0.013)→(0.606, 0.176, 0.016) | 0.154→0.151 | 1.00 / 4.000 | 0.123 | 0.125 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.541
- phase_score: 0.835
- phase_breakdown.reach_goal_score: 0.821
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
- **Parameters at lower bound**: approach_goal.goal_approach_speed
- **Final σ (mean)**: 0.315


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.10141,"average_solve_count":355.0,"average_success_count":355.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.goal_approach_speed":0.04682,"approach_object.approach_speed":0.04806,"descend_to_goal.descend_goal_speed":0.02871,"descend_to_object.descend_speed":0.07683,"grasp_object.grip_force":16.29595,"lift_object.lift_height":0.192,"lift_object.lift_speed":0.05392,"retract_from_goal.retract_height":0.14638,"retract_from_goal.retract_speed":0.08443},"optimized_scores":{"best_composite_score":0.11826,"best_fitness_score":0.74826,"best_task_score":0.54099},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":308.0,"contact_point_centroid":[0.60114,0.17535,-0.00427],"force_p95":0.82487,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.23126,"mean_force":0.23422,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.58887,0.17349,0.12434]},{"body_a":"world","body_b":"grasp_target","contact_count":112.0,"contact_point_centroid":[0.5254,0.02875,-0.00138],"force_p95":0.62963,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.71067,"mean_force":0.16822,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51513,0.0294,0.02613]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19475.0,"contact_point_centroid":[0.51288,0.04833,0.11485],"force_p95":0.07707,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32117,"mean_force":0.05248,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51244,0.02923,0.11304]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19006.0,"contact_point_centroid":[0.51293,0.0101,0.11898],"force_p95":0.07838,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31289,"mean_force":0.05302,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51245,0.02923,0.11685]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53055,0.03046,-0.00212],"force_p95":0.15802,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24284,"mean_force":0.13219,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.51768,0.02958,0.02609]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1181.0,"contact_point_centroid":[0.59513,0.19397,0.11122],"force_p95":0.07421,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17606,"mean_force":0.04612,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.59345,0.17501,0.11148]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":903.0,"contact_point_centroid":[0.5941,0.15582,0.11126],"force_p95":0.09771,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17357,"mean_force":0.05853,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.5934,0.17499,0.11138]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4057.0,"contact_point_centroid":[0.51735,0.0103,0.02749],"force_p95":0.08037,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14185,"mean_force":0.05188,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.51645,0.0295,0.02473]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4921.0,"contact_point_centroid":[0.59486,0.1912,0.15763],"force_p95":0.07274,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13957,"mean_force":0.05244,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.59334,0.17211,0.15777]},{"body_a":"world","body_b":"grasp_target","contact_count":1464.0,"contact_point_centroid":[0.5305,0.03079,-0.00191],"force_p95":0.13511,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12296,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.5103,0.01293,0.23191]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4801.0,"contact_point_centroid":[0.59484,0.15305,0.1582],"force_p95":0.07543,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13244,"mean_force":0.05307,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.59334,0.1721,0.15798]},{"body_a":"world","body_b":"grasp_target","contact_count":3332.0,"contact_point_centroid":[0.60371,0.17536,-0.00199],"force_p95":0.12294,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12425,"mean_force":0.1226,"phase_index":7.0,"phase_name":"retract_from_goal","phase_type":"retract","tcp_position_centroid":[0.58549,0.17239,0.20135]},{"body_a":"world","body_b":"grasp_target","contact_count":1620.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.52258,0.02834,0.09753]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14039.0,"contact_point_centroid":[0.55335,0.11969,0.19938],"force_p95":0.08058,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09336,"mean_force":0.05347,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55246,0.10055,0.19861]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4989.0,"contact_point_centroid":[0.51728,0.04865,0.02652],"force_p95":0.07274,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08826,"mean_force":0.04482,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.51646,0.0295,0.02474]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15299.0,"contact_point_centroid":[0.5533,0.08197,0.19925],"force_p95":0.07428,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0845,"mean_force":0.04914,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55271,0.10099,0.19861]}],"total_contact_groups":16},"final_pose_error":0.01498,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.60371,0.17536,0.01602],"final_tcp_position":[0.58609,0.17252,0.26743],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":1.23126,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":367.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1464.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.52319,0.02681,0.16243],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13666,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":405.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1620.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.52496,0.03006,0.03431],"tcp_start":[0.52319,0.02681,0.16243],"tcp_to_object_dist_end":0.01,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53037,0.02945,0.02561],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18468,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.15002,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10846.0,"raw_peak_contact_force":0.24284,"tcp_end":[0.51643,0.02949,0.02469],"tcp_start":[0.52496,0.03006,0.03431],"tcp_to_object_dist_end":0.01397,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":987.0,"n_steps_budget":1000.0,"object_pos_end":[0.52396,0.02929,0.19366],"object_pos_start":[0.53037,0.02945,0.02561],"object_to_goal_dist_end":0.18875,"object_to_goal_dist_start":0.18468,"object_z_max":0.1935,"peak_contact_force":0.06918,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":38593.0,"raw_peak_contact_force":0.71067,"tcp_end":[0.51296,0.02926,0.20218],"tcp_start":[0.51643,0.02949,0.02469],"tcp_to_object_dist_end":0.01391,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":750.0,"n_steps_budget":1000.0,"object_pos_end":[0.60123,0.1696,0.18496],"object_pos_start":[0.52396,0.02929,0.19366],"object_to_goal_dist_end":0.07739,"object_to_goal_dist_start":0.18875,"object_z_max":0.19373,"peak_contact_force":0.0744,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":29338.0,"raw_peak_contact_force":0.09336,"tcp_end":[0.59331,0.16947,0.19967],"tcp_start":[0.51296,0.02926,0.20218],"tcp_to_object_dist_end":0.0167,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":259.0,"n_steps_budget":1000.0,"object_pos_end":[0.60386,0.17549,0.09931],"object_pos_start":[0.60123,0.1696,0.18496],"object_to_goal_dist_end":0.0096,"object_to_goal_dist_start":0.07739,"object_z_max":0.18496,"peak_contact_force":0.07147,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9722.0,"raw_peak_contact_force":0.13957,"subtask_id":"reach_goal","tcp_end":[0.59578,0.17566,0.11557],"tcp_start":[0.59331,0.16947,0.19967],"tcp_to_object_dist_end":0.01817,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60379,0.17538,0.01636],"object_pos_start":[0.60386,0.17549,0.09931],"object_to_goal_dist_end":0.09182,"object_to_goal_dist_start":0.0096,"object_z_max":0.09931,"peak_contact_force":0.11688,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2392.0,"raw_peak_contact_force":1.23126,"tcp_end":[0.58876,0.17346,0.13576],"tcp_start":[0.59578,0.17566,0.11557],"tcp_to_object_dist_end":0.12036,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":833.0,"n_steps_budget":1000.0,"object_pos_end":[0.60371,0.17536,0.01602],"object_pos_start":[0.60379,0.17538,0.01636],"object_to_goal_dist_end":0.09215,"object_to_goal_dist_start":0.09182,"object_z_max":0.01636,"peak_contact_force":0.12263,"phase_name":"retract_from_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3332.0,"raw_peak_contact_force":0.12425,"tcp_end":[0.58609,0.17252,0.26743],"tcp_start":[0.58876,0.17346,0.13576],"tcp_to_object_dist_end":0.25204,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.20205,"average_solve_count":292.0,"average_success_count":292.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.goal_approach_speed":0.03496,"approach_object.approach_speed":0.0871,"descend_to_goal.descend_goal_speed":0.07342,"descend_to_object.descend_speed":0.05533,"grasp_object.grip_force":16.34545,"lift_object.lift_height":0.14161,"lift_object.lift_speed":0.04083,"retract_from_goal.retract_height":0.09152,"retract_from_goal.retract_speed":0.06947},"optimized_scores":{"best_composite_score":-0.04441,"best_fitness_score":0.58559,"best_task_score":0.21272},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":154.0,"contact_point_centroid":[0.58475,0.18166,-0.00933],"force_p95":1.49879,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.0281,"mean_force":0.51346,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.57737,0.18079,0.25618]},{"body_a":"world","body_b":"grasp_target","contact_count":106.0,"contact_point_centroid":[0.49908,-0.01525,-0.00132],"force_p95":0.57852,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60744,"mean_force":0.18139,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48947,-0.0153,0.02704]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13313.0,"contact_point_centroid":[0.4867,0.00391,0.09158],"force_p95":0.07658,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28593,"mean_force":0.0521,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48671,-0.01524,0.08935]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13742.0,"contact_point_centroid":[0.48666,-0.03437,0.09013],"force_p95":0.07422,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26792,"mean_force":0.05086,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48671,-0.01524,0.0882]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50381,-0.01551,-0.00203],"force_p95":0.13368,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16408,"mean_force":0.12574,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49187,-0.01532,0.02712]},{"body_a":"world","body_b":"grasp_target","contact_count":1284.0,"contact_point_centroid":[0.50382,-0.01567,-0.0019],"force_p95":0.13564,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12301,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49929,-0.00651,0.23326]},{"body_a":"world","body_b":"grasp_target","contact_count":1984.0,"contact_point_centroid":[0.58658,0.18181,-0.00205],"force_p95":0.12412,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12516,"mean_force":0.11898,"phase_index":7.0,"phase_name":"retract_from_goal","phase_type":"retract","tcp_position_centroid":[0.57536,0.18003,0.30032]},{"body_a":"world","body_b":"grasp_target","contact_count":1760.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.49802,-0.01446,0.0985]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10780.0,"contact_point_centroid":[0.56625,0.1314,0.25312],"force_p95":0.0734,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12228,"mean_force":0.05009,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.56519,0.15042,0.25261]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":927.0,"contact_point_centroid":[0.58073,0.16284,0.23806],"force_p95":0.09041,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1161,"mean_force":0.05475,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.5803,0.18197,0.23793]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10199.0,"contact_point_centroid":[0.56616,0.16913,0.25325],"force_p95":0.07645,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11582,"mean_force":0.05285,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.56498,0.15005,0.2527]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4108.0,"contact_point_centroid":[0.49121,0.00389,0.02865],"force_p95":0.07627,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11378,"mean_force":0.05174,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49069,-0.01531,0.02589]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1179.0,"contact_point_centroid":[0.58176,0.20095,0.23815],"force_p95":0.07102,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10831,"mean_force":0.04395,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.58033,0.18199,0.23802]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19838.0,"contact_point_centroid":[0.51749,0.07124,0.21353],"force_p95":0.07472,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08986,"mean_force":0.05051,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51709,0.05205,0.21228]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4892.0,"contact_point_centroid":[0.49127,-0.03439,0.02773],"force_p95":0.06853,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08873,"mean_force":0.04477,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49069,-0.01531,0.02589]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":21394.0,"contact_point_centroid":[0.51668,0.03176,0.2122],"force_p95":0.06991,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08494,"mean_force":0.04712,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51651,0.05087,0.21119]}],"total_contact_groups":16},"final_pose_error":0.01495,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.58658,0.18181,0.01602],"final_tcp_position":[0.57562,0.18005,0.33891],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":2.0281,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":322.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1284.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.50005,-0.01357,0.16407],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13812,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":440.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1760.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.49886,-0.0154,0.03453],"tcp_start":[0.50005,-0.01357,0.16407],"tcp_to_object_dist_end":0.00985,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50367,-0.01517,0.02587],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31206,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13102,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10800.0,"raw_peak_contact_force":0.16408,"tcp_end":[0.49066,-0.01531,0.02586],"tcp_start":[0.49886,-0.0154,0.03453],"tcp_to_object_dist_end":0.01301,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":673.0,"n_steps_budget":1000.0,"object_pos_end":[0.49803,-0.0152,0.14744],"object_pos_start":[0.50367,-0.01517,0.02587],"object_to_goal_dist_end":0.24311,"object_to_goal_dist_start":0.31206,"object_z_max":0.14727,"peak_contact_force":0.07007,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":27161.0,"raw_peak_contact_force":0.60744,"tcp_end":[0.48686,-0.01524,0.153],"tcp_start":[0.49066,-0.01531,0.02586],"tcp_to_object_dist_end":0.01248,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55615,0.11392,0.25717],"object_pos_start":[0.49803,-0.0152,0.14744],"object_to_goal_dist_end":0.08022,"object_to_goal_dist_start":0.24311,"object_z_max":0.25706,"peak_contact_force":0.0763,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":41232.0,"raw_peak_contact_force":0.08986,"tcp_end":[0.54818,0.1139,0.27095],"tcp_start":[0.48686,-0.01524,0.153],"tcp_to_object_dist_end":0.01592,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":549.0,"n_steps_budget":1000.0,"object_pos_end":[0.58701,0.18236,0.22426],"object_pos_start":[0.55615,0.11392,0.25717],"object_to_goal_dist_end":0.02439,"object_to_goal_dist_start":0.08022,"object_z_max":0.25717,"peak_contact_force":0.07195,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":20979.0,"raw_peak_contact_force":0.12228,"subtask_id":"reach_goal","tcp_end":[0.58166,0.18227,0.24137],"tcp_start":[0.54818,0.1139,0.27095],"tcp_to_object_dist_end":0.01792,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58632,0.18191,0.00804],"object_pos_start":[0.58701,0.18236,0.22426],"object_to_goal_dist_end":0.24015,"object_to_goal_dist_start":0.02439,"object_z_max":0.22426,"peak_contact_force":0.08064,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2260.0,"raw_peak_contact_force":2.0281,"tcp_end":[0.57735,0.18078,0.26222],"tcp_start":[0.58166,0.18227,0.24137],"tcp_to_object_dist_end":0.25434,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":496.0,"n_steps_budget":840.0,"object_pos_end":[0.58658,0.18181,0.01602],"object_pos_start":[0.58632,0.18191,0.00804],"object_to_goal_dist_end":0.23217,"object_to_goal_dist_start":0.24015,"object_z_max":0.0167,"peak_contact_force":0.12263,"phase_name":"retract_from_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1984.0,"raw_peak_contact_force":0.12516,"tcp_end":[0.57562,0.18005,0.33891],"tcp_start":[0.57735,0.18078,0.26222],"tcp_to_object_dist_end":0.32308,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.82955,"average_solve_count":440.0,"average_success_count":440.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.goal_approach_speed":0.02,"approach_object.approach_speed":0.14213,"descend_to_goal.descend_goal_speed":0.01731,"descend_to_object.descend_speed":0.05979,"grasp_object.grip_force":15.86869,"lift_object.lift_height":0.19829,"lift_object.lift_speed":0.0212,"retract_from_goal.retract_height":0.09154,"retract_from_goal.retract_speed":0.08361},"optimized_scores":{"best_composite_score":0.06033,"best_fitness_score":0.69033,"best_task_score":0.42304},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":258.0,"contact_point_centroid":[0.6264,0.1696,-0.0054],"force_p95":1.05761,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.51057,"mean_force":0.28508,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.61567,0.16811,0.16223]},{"body_a":"world","body_b":"grasp_target","contact_count":117.0,"contact_point_centroid":[0.50772,0.03742,-0.00145],"force_p95":0.54775,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.58727,"mean_force":0.18037,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49779,0.03802,0.02678]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20514.0,"contact_point_centroid":[0.49523,0.05696,0.11818],"force_p95":0.07382,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27412,"mean_force":0.05048,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49522,0.03782,0.11649]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20166.0,"contact_point_centroid":[0.49528,0.01867,0.12164],"force_p95":0.07506,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26025,"mean_force":0.05052,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49523,0.03782,0.11954]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51257,0.03936,-0.00214],"force_p95":0.16534,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24998,"mean_force":0.13408,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.50032,0.03824,0.02687]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":959.0,"contact_point_centroid":[0.62061,0.15032,0.14848],"force_p95":0.09229,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15957,"mean_force":0.05491,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.61983,0.16946,0.14835]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1179.0,"contact_point_centroid":[0.6214,0.18849,0.14835],"force_p95":0.07358,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15689,"mean_force":0.04582,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.61989,0.16948,0.14848]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4727.0,"contact_point_centroid":[0.62075,0.18662,0.19465],"force_p95":0.07204,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14985,"mean_force":0.05155,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.61939,0.16755,0.19464]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4048.0,"contact_point_centroid":[0.49979,0.01894,0.02839],"force_p95":0.08157,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1481,"mean_force":0.05191,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49913,0.03814,0.02559]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4556.0,"contact_point_centroid":[0.62067,0.1485,0.19437],"force_p95":0.07355,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14533,"mean_force":0.0529,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.6194,0.16757,0.194]},{"body_a":"world","body_b":"grasp_target","contact_count":1300.0,"contact_point_centroid":[0.51251,0.03972,-0.0019],"force_p95":0.13564,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.123,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.5029,0.01672,0.232]},{"body_a":"world","body_b":"grasp_target","contact_count":2104.0,"contact_point_centroid":[0.62858,0.1696,-0.00198],"force_p95":0.12355,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12452,"mean_force":0.12219,"phase_index":7.0,"phase_name":"retract_from_goal","phase_type":"retract","tcp_position_centroid":[0.61255,0.16713,0.21033]},{"body_a":"world","body_b":"grasp_target","contact_count":1732.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.50598,0.03658,0.09788]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18890.0,"contact_point_centroid":[0.55892,0.12351,0.22122],"force_p95":0.07363,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09099,"mean_force":0.04988,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55842,0.10433,0.22031]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5016.0,"contact_point_centroid":[0.49975,0.05733,0.0274],"force_p95":0.07407,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09,"mean_force":0.04482,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49914,0.03814,0.0256]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19799.0,"contact_point_centroid":[0.55833,0.08478,0.22122],"force_p95":0.07124,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0806,"mean_force":0.04751,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55798,0.10389,0.2202]}],"total_contact_groups":16},"final_pose_error":0.01499,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.62858,0.1696,0.01602],"final_tcp_position":[0.61272,0.16714,0.24881],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1.51057,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":326.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1300.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.50752,0.03457,0.16281],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13698,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":433.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1732.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.50739,0.03881,0.03456],"tcp_start":[0.50752,0.03457,0.16281],"tcp_to_object_dist_end":0.01,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51239,0.03813,0.02552],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21356,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.15586,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10864.0,"raw_peak_contact_force":0.24998,"tcp_end":[0.49911,0.03814,0.02556],"tcp_start":[0.50739,0.03881,0.03456],"tcp_to_object_dist_end":0.01329,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50609,0.03788,0.20076],"object_pos_start":[0.51239,0.03813,0.02552],"object_to_goal_dist_end":0.18972,"object_to_goal_dist_start":0.21356,"object_z_max":0.20059,"peak_contact_force":0.06974,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":40797.0,"raw_peak_contact_force":0.58727,"tcp_end":[0.49574,0.03787,0.2091],"tcp_start":[0.49911,0.03814,0.02556],"tcp_to_object_dist_end":0.01329,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":943.0,"n_steps_budget":1000.0,"object_pos_end":[0.62566,0.16576,0.21975],"object_pos_start":[0.50609,0.03788,0.20076],"object_to_goal_dist_end":0.07506,"object_to_goal_dist_start":0.18972,"object_z_max":0.21974,"peak_contact_force":0.07354,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":38689.0,"raw_peak_contact_force":0.09099,"tcp_end":[0.61898,0.16588,0.23479],"tcp_start":[0.49574,0.03787,0.2091],"tcp_to_object_dist_end":0.01645,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":248.0,"n_steps_budget":1000.0,"object_pos_end":[0.62919,0.1699,0.13648],"object_pos_start":[0.62566,0.16576,0.21975],"object_to_goal_dist_end":0.00908,"object_to_goal_dist_start":0.07506,"object_z_max":0.21975,"peak_contact_force":0.07212,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9283.0,"raw_peak_contact_force":0.14985,"subtask_id":"reach_goal","tcp_end":[0.62202,0.17008,0.15288],"tcp_start":[0.61898,0.16588,0.23479],"tcp_to_object_dist_end":0.0179,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.6287,0.16957,0.01606],"object_pos_start":[0.62919,0.1699,0.13648],"object_to_goal_dist_end":0.129,"object_to_goal_dist_start":0.00908,"object_z_max":0.13648,"peak_contact_force":0.09942,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2396.0,"raw_peak_contact_force":1.51057,"tcp_end":[0.61561,0.16809,0.17194],"tcp_start":[0.62202,0.17008,0.15288],"tcp_to_object_dist_end":0.15644,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":526.0,"n_steps_budget":690.0,"object_pos_end":[0.62858,0.1696,0.01602],"object_pos_start":[0.6287,0.16957,0.01606],"object_to_goal_dist_end":0.12904,"object_to_goal_dist_start":0.129,"object_z_max":0.01647,"peak_contact_force":0.12263,"phase_name":"retract_from_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2104.0,"raw_peak_contact_force":0.12452,"tcp_end":[0.61272,0.16714,0.24881],"tcp_start":[0.61561,0.16809,0.17194],"tcp_to_object_dist_end":0.23334,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```