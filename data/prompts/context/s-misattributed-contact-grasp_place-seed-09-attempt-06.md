## Search State

- **Seed**: 9
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 7 | -0.2526 | 0.17 | ✅ accepted |
| 5 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 8 | -0.2863 | 0.14 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6 | -0.3197 | 0.14 | ❌ rejected |
| 3 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6 | -0.1514 | 0.17 | ✅ accepted |
| 2 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | admittance_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 7 | -0.1532 | 0.17 | ✅ accepted |

**Proposal policy**: task_score is 0.17 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8`
- Frozen object start: [0.5370249203970084, -0.021318279091244466, 0.03]
- Frozen task target: [0.6103148150051562, 0.2277534082920179, 0.2074111944405348]
- Goal object position: (0.6103148150051562, 0.2277534082920179, 0.2074111944405348)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.6103148150051562, 0.2277534082920179, 0.2074111944405348)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5370249203970084, -0.021318279091244466, 0.03)
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
  frozen_object_start: [0.537, -0.0213, 0.03]
  frozen_task_target: [0.6103, 0.2278, 0.2074]
  frozen_object_starts: {'grasp_target': [0.5370249203970084, -0.021318279091244466, 0.03]}
  frozen_targets: {'place_target': [0.6103148150051562, 0.2277534082920179, 0.2074111944405348]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8

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
| `object` | offset from object initial position (0.5370249203970084, -0.021318279091244466, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.6103148150051562, 0.2277534082920179, 0.2074111944405348) | final destination targets |
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

## Current Skill (Q=-0.253) — your mutation base

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
  - 0.15
  weight: 0.3
- id: place_object
  target_entity: object
  metric: goal_progress
  weight: 0.7
phases:
- id: approach_object
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
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_arc_height:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.arc_height
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_object
- id: descend_to_grasp
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
    - 0.03
    tolerance: 0.015
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.02
      - 0.12
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_object
- id: grasp
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
  - id: grasp_bilateral
    when: after_phase
    predicate: bilateral_grasp
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: repeat
- id: lift
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
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
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
  guards:
  - id: lift_object_lost
    when: after_phase
    predicate: object_lifted
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: repeat
  subtask_id: reach_object
- id: approach_goal
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: place_object
- id: descend_place
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
  subtask_id: place_object
- id: release_object
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
  parameters:
    release_timeout:
      type: scalar
      range:
      - 0.1
      - 1.0
      default: 0.5
      binds_to:
      - path: duration.max_time
        mode: replace
- id: retract
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
      distance: 0.15
      axis: world_z
      mode: add_to_offset
      sign: positive
    tolerance: 0.03
    orientation:
      mode: keep_current
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.1
      - 0.3
      default: 0.2
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_arc_height: status=consumed; consumers=generator.arc_height (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.03], tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **grasp** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=grasp_bilateral, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=1.0
  - retries: max_attempts=1, strategy=repeat
- **lift** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.12, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
  - guards:
    - id=lift_object_lost, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=1.0
  - retries: max_attempts=1, strategy=repeat
- **approach_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=grasp_target, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **descend_place** (`descend`)
  - target: source=yaml, anchor=task_goal, entity=grasp_target, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings: none
- **release_object** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - release_timeout: status=consumed; consumers=duration.max_time (replace)
- **retract** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.15, mode=add_to_offset, sign=positive}, tolerance=0.03
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_height: status=consumed; consumers=target.offset_along_axis.distance (replace)

## Design Metrics

- **Composite score**: -0.253
- **task_score** (E): 0.171
- **fitness_score**: 0.277  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.530

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1260 |
| descend_to_grasp | 1.00 | 1.00 | 0.1124 |
| grasp | 1.00 | 1.00 | 0.0125 |
| lift | 1.00 | 1.00 | 0.1342 |
| approach_goal | 1.00 | 1.00 | 0.2170 |
| descend_place | 1.00 | 1.00 | 0.1248 |
| release_object | 1.00 | 1.00 | 0.0195 |
| retract | 1.00 | 1.00 | 0.1940 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.512, 0.002, 0.181) | (0.515, -0.017, 0.030)→(0.515, -0.017, 0.026) | 0.268→0.270 | 1.00 / 4.000 | 0.123 | 0.123 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.512, 0.002, 0.181)→(0.511, -0.014, 0.070) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 18.000 | 0.340 | 0.347 |
| grasp | grasp | 1.00 / step_budget | (0.511, -0.014, 0.070)→(0.502, -0.014, 0.060) | (0.515, -0.017, 0.026)→(0.516, -0.009, 0.023) | 0.270→0.266 | 1.00 / 8.333 | 0.123 | 0.433 |
| lift | lift | 1.00 / step_budget | (0.499, -0.014, 0.195)→(0.497, -0.014, 0.329) | (0.516, -0.009, 0.023)→(0.515, -0.015, 0.026) | 0.266→0.269 | 1.00 / 8.000 | 3249.732 | 0.123 |
| approach_goal | approach | 1.00 / step_budget | (0.497, -0.014, 0.329)→(0.607, 0.167, 0.312) | (0.515, -0.015, 0.026)→(0.515, -0.015, 0.026) | 0.269→0.269 | 1.00 / 8.333 | 0.123 | 0.123 |
| descend_place | descend | 1.00 / step_budget | (0.607, 0.167, 0.312)→(0.613, 0.178, 0.188) | (0.515, -0.015, 0.026)→(0.515, -0.015, 0.026) | 0.269→0.269 | 1.00 / 4.000 | 0.123 | 0.123 |
| release_object | release | 1.00 / step_budget | (0.613, 0.178, 0.188)→(0.607, 0.176, 0.206) | (0.515, -0.015, 0.026)→(0.515, -0.015, 0.026) | 0.269→0.269 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract | retract | 1.00 / step_budget | (0.607, 0.176, 0.206)→(0.607, 0.176, 0.400) | (0.515, -0.015, 0.026)→(0.515, -0.015, 0.026) | 0.269→0.269 | 1.00 / 4.000 | 0.123 | 0.138 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: 0.000
- terminal_score: 0.214
- phase_score: 0.028
- phase_breakdown.reach_object_score: 0.093
- phase_breakdown.place_object_score: 0.000
- grasp_place_fitness: 0.297

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.297
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.214
- **Median Q (composite search score)**: -0.249
- **K-run variance**: 0.0003
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.302


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `425c48e82220fc6e1b680086671cf7dd2586733ee271dec2149f96a25d69d0c6`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `58e88c03db0a62276863b22a53636bc89fead3e4bc7f4d35fd72d2282ace32bf`; realized-scene SHA-256: `0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53702,-0.02132,0.03]},{"name":"goal","value":[0.61031,0.22775,0.20741]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.53702,-0.02132,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.61031,0.22775,0.20741]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.65397,"average_solve_count":315.0,"average_success_count":315.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.transport_speed":0.04217,"approach_object.approach_arc_height":0.06343,"approach_object.approach_speed":0.09729,"descend_to_grasp.descend_speed":0.07689,"lift.lift_height":0.17369,"release_object.release_timeout":0.38387,"retract.retract_height":0.22763},"optimized_scores":{"best_composite_score":-0.27646,"best_fitness_score":0.25354,"best_task_score":0.12171},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3650.0,"contact_point_centroid":[0.53703,-0.01947,-0.00205],"force_p95":0.15718,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.44462,"mean_force":0.12556,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51911,-0.01811,0.21359]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53718,-0.02135,-0.00249],"force_p95":0.33281,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.34877,"mean_force":0.15918,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52475,-0.0182,0.06063]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":299.0,"contact_point_centroid":[0.52369,-0.02519,0.05691],"force_p95":0.14711,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33623,"mean_force":0.06702,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52196,-0.01816,0.06207]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":86.0,"contact_point_centroid":[0.52881,-0.01121,0.05519],"force_p95":0.23349,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28982,"mean_force":0.12762,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52194,-0.01816,0.06208]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1126.0,"contact_point_centroid":[0.52736,-0.00207,0.05283],"force_p95":0.18236,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21958,"mean_force":0.10168,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52361,-0.01817,0.05926]},{"body_a":"world","body_b":"grasp_target","contact_count":1372.0,"contact_point_centroid":[0.53702,-0.02132,-0.0019],"force_p95":0.1356,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12298,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51562,0.02909,0.23725]},{"body_a":"world","body_b":"grasp_target","contact_count":1032.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53104,-0.01011,0.12411]},{"body_a":"world","body_b":"grasp_target","contact_count":2704.0,"contact_point_centroid":[0.537,-0.02029,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.56048,0.09662,0.35604]},{"body_a":"world","body_b":"grasp_target","contact_count":844.0,"contact_point_centroid":[0.537,-0.02029,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.60479,0.21696,0.28959]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.537,-0.02029,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.60296,0.22191,0.22508]},{"body_a":"world","body_b":"grasp_target","contact_count":1744.0,"contact_point_centroid":[0.537,-0.02029,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.60103,0.22076,0.34083]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3109.0,"contact_point_centroid":[0.52377,-0.03253,0.05448],"force_p95":0.07854,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08497,"mean_force":0.04595,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.5236,-0.01817,0.05925]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3476.0,"contact_point_centroid":[0.5193,-0.01811,0.2324],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01804,"mean_force":0.01052,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51897,-0.01811,0.23007]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2878.0,"contact_point_centroid":[0.56096,0.09697,0.35834],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01285,"mean_force":0.01047,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.56061,0.09697,0.35602]},{"body_a":"left_finger","body_b":"right_finger","contact_count":898.0,"contact_point_centroid":[0.60523,0.21702,0.29133],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01102,"mean_force":0.01048,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.60481,0.21701,0.2891]},{"body_a":"left_finger","body_b":"right_finger","contact_count":227.0,"contact_point_centroid":[0.60565,0.2229,0.22369],"force_p95":0.01086,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01088,"mean_force":0.00984,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.60496,0.22287,0.22134]}],"total_contact_groups":16},"final_pose_error":0.02984,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.537,-0.02029,0.02602],"final_tcp_position":[0.60273,0.2213,0.44233],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":0.44462,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":344.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1032.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.53218,-0.00231,0.17761],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15285,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":20.0,"n_steps":258.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.3468,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":6035.0,"raw_peak_contact_force":0.34877,"subtask_id":"reach_object","tcp_end":[0.5319,-0.01821,0.06941],"tcp_start":[0.53218,-0.00231,0.17761],"tcp_to_object_dist_end":0.04381,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53751,-0.01393,0.02297],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31262,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":7511.0,"raw_peak_contact_force":0.44462,"tcp_end":[0.52356,-0.01819,0.05921],"tcp_start":[0.5319,-0.01821,0.06941],"tcp_to_object_dist_end":0.03906,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":952.0,"n_steps_budget":1000.0,"object_pos_end":[0.537,-0.02029,0.02602],"object_pos_start":[0.53751,-0.01393,0.02297],"object_to_goal_dist_end":0.31591,"object_to_goal_dist_start":0.31262,"object_z_max":0.0312,"peak_contact_force":0.12263,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":5582.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.51889,-0.01813,0.36717],"tcp_start":[0.52033,-0.01812,0.21343],"tcp_to_object_dist_end":0.34164,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":676.0,"n_steps_budget":1000.0,"object_pos_end":[0.537,-0.02029,0.02602],"object_pos_start":[0.537,-0.02029,0.02602],"object_to_goal_dist_end":0.31591,"object_to_goal_dist_start":0.31591,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1742.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_object","tcp_end":[0.60328,0.21103,0.34967],"tcp_start":[0.51889,-0.01813,0.36717],"tcp_to_object_dist_end":0.4033,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":211.0,"n_steps_budget":1000.0,"object_pos_end":[0.537,-0.02029,0.02602],"object_pos_start":[0.537,-0.02029,0.02602],"object_to_goal_dist_end":0.31591,"object_to_goal_dist_start":0.31591,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1027.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_object","tcp_end":[0.60662,0.22339,0.22628],"tcp_start":[0.60328,0.21103,0.34967],"tcp_to_object_dist_end":0.323,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.537,-0.02029,0.02602],"object_pos_start":[0.537,-0.02029,0.02602],"object_to_goal_dist_end":0.31591,"object_to_goal_dist_start":0.31591,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1744.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.60182,0.22133,0.24453],"tcp_start":[0.60662,0.22339,0.22628],"tcp_to_object_dist_end":0.33215,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":436.0,"n_steps_budget":1000.0,"object_pos_end":[0.537,-0.02029,0.02602],"object_pos_start":[0.537,-0.02029,0.02602],"object_to_goal_dist_end":0.31591,"object_to_goal_dist_start":0.31591,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1372.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.60273,0.2213,0.44233],"tcp_start":[0.60182,0.22133,0.24453],"tcp_to_object_dist_end":0.4858,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1e57d18e69439f9d4839513252d085a45363faa5c1c2b52093c9c8149b88bb68`; realized-scene SHA-256: `9bdc6de22965641ffcaccb8421100561fe91fb98e16735236cc25272572d8879`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5456,-0.02923,0.03]},{"name":"goal","value":[0.63284,0.16493,0.17692]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5456,-0.02923,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63284,0.16493,0.17692]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.22018,"average_solve_count":218.0,"average_success_count":218.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.transport_speed":0.16146,"approach_object.approach_arc_height":0.06472,"approach_object.approach_speed":0.10993,"descend_to_grasp.descend_speed":0.07902,"lift.lift_height":0.15079,"release_object.release_timeout":0.23043,"retract.retract_height":0.23566},"optimized_scores":{"best_composite_score":-0.24867,"best_fitness_score":0.28133,"best_task_score":0.17618},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3166.0,"contact_point_centroid":[0.54544,-0.0275,-0.00206],"force_p95":0.16362,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.44206,"mean_force":0.12618,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.5272,-0.02575,0.19162]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54575,-0.02933,-0.00248],"force_p95":0.32071,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.34408,"mean_force":0.15823,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53319,-0.02593,0.06026]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":91.0,"contact_point_centroid":[0.5375,-0.01767,0.05474],"force_p95":0.23232,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31663,"mean_force":0.1379,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.53044,-0.02586,0.06168]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":351.0,"contact_point_centroid":[0.53167,-0.03401,0.05699],"force_p95":0.14,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23539,"mean_force":0.06303,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.53031,-0.02586,0.06202]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1321.0,"contact_point_centroid":[0.53501,-0.00886,0.05259],"force_p95":0.18691,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21991,"mean_force":0.10156,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53203,-0.02589,0.05884]},{"body_a":"world","body_b":"grasp_target","contact_count":1396.0,"contact_point_centroid":[0.5456,-0.02923,-0.0019],"force_p95":0.1356,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12298,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.52078,0.02597,0.23443]},{"body_a":"world","body_b":"grasp_target","contact_count":1008.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53965,-0.01799,0.12346]},{"body_a":"world","body_b":"grasp_target","contact_count":1968.0,"contact_point_centroid":[0.54539,-0.02848,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.57453,0.06238,0.3176]},{"body_a":"world","body_b":"grasp_target","contact_count":840.0,"contact_point_centroid":[0.54539,-0.02848,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62531,0.15519,0.25877]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.54539,-0.02848,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.62373,0.15982,0.19447]},{"body_a":"world","body_b":"grasp_target","contact_count":1836.0,"contact_point_centroid":[0.54539,-0.02848,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.62107,0.1588,0.31469]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3120.0,"contact_point_centroid":[0.53225,-0.04129,0.05423],"force_p95":0.08138,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08629,"mean_force":0.04925,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53202,-0.02589,0.05883]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2936.0,"contact_point_centroid":[0.52732,-0.02575,0.21068],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01643,"mean_force":0.01054,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52697,-0.02575,0.20831]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2101.0,"contact_point_centroid":[0.57506,0.0627,0.31989],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01277,"mean_force":0.01045,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.57471,0.0627,0.3176]},{"body_a":"left_finger","body_b":"right_finger","contact_count":220.0,"contact_point_centroid":[0.62665,0.16063,0.1929],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01273,"mean_force":0.01012,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.62609,0.16061,0.19071]},{"body_a":"left_finger","body_b":"right_finger","contact_count":901.0,"contact_point_centroid":[0.62582,0.1552,0.26093],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.011,"mean_force":0.01039,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62531,0.15519,0.25874]}],"total_contact_groups":16},"final_pose_error":0.02991,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.54539,-0.02848,0.02602],"final_tcp_position":[0.62264,0.15917,0.41964],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":9748.95181,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":350.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1008.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.54085,-0.01025,0.17638],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15162,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":20.0,"n_steps":252.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.3437,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":6241.0,"raw_peak_contact_force":0.34408,"subtask_id":"reach_object","tcp_end":[0.54042,-0.02603,0.06931],"tcp_start":[0.54085,-0.01025,0.17638],"tcp_to_object_dist_end":0.04372,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54603,-0.02251,0.02296],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.25763,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":6544.0,"raw_peak_contact_force":0.44206,"tcp_end":[0.53199,-0.0259,0.05879],"tcp_start":[0.54042,-0.02603,0.06931],"tcp_to_object_dist_end":0.03863,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":833.0,"n_steps_budget":960.0,"object_pos_end":[0.54539,-0.02848,0.02602],"object_pos_start":[0.54603,-0.02251,0.02296],"object_to_goal_dist_end":0.26043,"object_to_goal_dist_start":0.25763,"object_z_max":0.03152,"peak_contact_force":9748.95181,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4069.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.52656,-0.02575,0.32105],"tcp_start":[0.52848,-0.02579,0.18993],"tcp_to_object_dist_end":0.29564,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":492.0,"n_steps_budget":1000.0,"object_pos_end":[0.54539,-0.02848,0.02602],"object_pos_start":[0.54539,-0.02848,0.02602],"object_to_goal_dist_end":0.26044,"object_to_goal_dist_start":0.26044,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1741.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_object","tcp_end":[0.62326,0.1498,0.31847],"tcp_start":[0.52656,-0.02575,0.32105],"tcp_to_object_dist_end":0.35125,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":210.0,"n_steps_budget":1000.0,"object_pos_end":[0.54539,-0.02848,0.02602],"object_pos_start":[0.54539,-0.02848,0.02602],"object_to_goal_dist_end":0.26044,"object_to_goal_dist_start":0.26044,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1020.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_object","tcp_end":[0.62807,0.16102,0.19588],"tcp_start":[0.62326,0.1498,0.31847],"tcp_to_object_dist_end":0.26758,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54539,-0.02848,0.02602],"object_pos_start":[0.54539,-0.02848,0.02602],"object_to_goal_dist_end":0.26044,"object_to_goal_dist_start":0.26044,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1836.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62232,0.15934,0.21389],"tcp_start":[0.62807,0.16102,0.19588],"tcp_to_object_dist_end":0.27657,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":459.0,"n_steps_budget":1000.0,"object_pos_end":[0.54539,-0.02848,0.02602],"object_pos_start":[0.54539,-0.02848,0.02602],"object_to_goal_dist_end":0.26044,"object_to_goal_dist_start":0.26044,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1396.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.62264,0.15917,0.41964],"tcp_start":[0.62232,0.15934,0.21389],"tcp_to_object_dist_end":0.44285,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `5836f8a66456087ed82e2e1accc6472c2a7681a19bf8e3d54637158aadaafc47`; realized-scene SHA-256: `776f3cbcac69f75f44cb26f0b1a492bbf1ced59f3c5fca79400c3f557c2ce565`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.46286,-7e-05,0.03]},{"name":"goal","value":[0.61015,0.15287,0.12219]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.46286,-7e-05,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.61015,0.15287,0.12219]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.95197,"average_solve_count":229.0,"average_success_count":229.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.transport_speed":0.1762,"approach_object.approach_arc_height":0.08679,"approach_object.approach_speed":0.05223,"descend_to_grasp.descend_speed":0.09571,"lift.lift_height":0.13734,"release_object.release_timeout":0.5931,"retract.retract_height":0.20842},"optimized_scores":{"best_composite_score":-0.2327,"best_fitness_score":0.2973,"best_task_score":0.21428},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2708.0,"contact_point_centroid":[0.46284,0.00325,-0.00204],"force_p95":0.1432,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.41229,"mean_force":0.12478,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44749,0.00213,0.17997]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.46295,0.00042,-0.0024],"force_p95":0.33905,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.3493,"mean_force":0.15588,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45287,0.0022,0.06344]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":87.0,"contact_point_centroid":[0.4533,-0.00165,0.05715],"force_p95":0.25739,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28213,"mean_force":0.08167,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45096,0.00216,0.06324]},{"body_a":"world","body_b":"grasp_target","contact_count":1112.0,"contact_point_centroid":[0.46286,-7e-05,-0.00188],"force_p95":0.13647,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12307,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48315,0.02815,0.24836]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":27.0,"contact_point_centroid":[0.45805,0.00431,0.05587],"force_p95":0.11604,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12444,"mean_force":0.05552,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45116,0.00216,0.06277]},{"body_a":"world","body_b":"grasp_target","contact_count":1156.0,"contact_point_centroid":[0.46286,-7e-05,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.46081,0.01007,0.12965]},{"body_a":"world","body_b":"grasp_target","contact_count":1944.0,"contact_point_centroid":[0.463,0.00289,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52099,0.07171,0.28107]},{"body_a":"world","body_b":"grasp_target","contact_count":896.0,"contact_point_centroid":[0.463,0.00289,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.59896,0.14489,0.20489]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.463,0.00289,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.59866,0.14827,0.13992]},{"body_a":"world","body_b":"grasp_target","contact_count":1556.0,"contact_point_centroid":[0.463,0.00289,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.59474,0.14703,0.24731]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1836.0,"contact_point_centroid":[0.45311,-0.00531,0.05647],"force_p95":0.06601,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11485,"mean_force":0.03872,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45184,0.00218,0.0624]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":261.0,"contact_point_centroid":[0.45902,0.00466,0.05545],"force_p95":0.03727,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.05915,"mean_force":0.02558,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45182,0.00218,0.06238]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2612.0,"contact_point_centroid":[0.44751,0.00213,0.19237],"force_p95":0.01129,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01617,"mean_force":0.01067,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.4473,0.00213,0.19018]},{"body_a":"left_finger","body_b":"right_finger","contact_count":965.0,"contact_point_centroid":[0.5994,0.14492,0.20685],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01277,"mean_force":0.01037,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.59897,0.1449,0.20466]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2080.0,"contact_point_centroid":[0.52118,0.0716,0.28334],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01265,"mean_force":0.01042,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52086,0.0716,0.28109]},{"body_a":"left_finger","body_b":"right_finger","contact_count":224.0,"contact_point_centroid":[0.60204,0.14912,0.13789],"force_p95":0.01093,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01255,"mean_force":0.00992,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.6015,0.1491,0.13562]}],"total_contact_groups":16},"final_pose_error":0.02989,"key_states":{"actual_goal_position":[0.61015,0.15287,0.12219],"final_object_position":[0.463,0.00289,0.02602],"final_tcp_position":[0.59561,0.14719,0.33831],"realised_goal_position":[0.61015,0.15287,0.12219],"realised_object_initial_position":[0.46286,-7e-05,0.03]},"peak_contact_force":9748.77226,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":279.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.03],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.23148,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1156.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.46408,0.01765,0.18864],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16359,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":14.0,"n_steps":289.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.3287,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3897.0,"raw_peak_contact_force":0.3493,"subtask_id":"reach_object","tcp_end":[0.45927,0.00236,0.07004],"tcp_start":[0.46408,0.01765,0.18864],"tcp_to_object_dist_end":0.04423,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46299,0.00975,0.02362],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.22772,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":5434.0,"raw_peak_contact_force":0.41229,"tcp_end":[0.45181,0.00218,0.06237],"tcp_start":[0.45927,0.00236,0.07004],"tcp_to_object_dist_end":0.04104,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":690.0,"n_steps_budget":870.0,"object_pos_end":[0.463,0.00289,0.02602],"object_pos_start":[0.46299,0.00975,0.02362],"object_to_goal_dist_end":0.23107,"object_to_goal_dist_start":0.22772,"object_z_max":0.02603,"peak_contact_force":0.12263,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4024.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.44651,0.00212,0.29786],"tcp_start":[0.44861,0.00214,0.18022],"tcp_to_object_dist_end":0.27234,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":486.0,"n_steps_budget":1000.0,"object_pos_end":[0.463,0.00289,0.02602],"object_pos_start":[0.463,0.00289,0.02602],"object_to_goal_dist_end":0.23107,"object_to_goal_dist_start":0.23107,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1861.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_object","tcp_end":[0.59541,0.14068,0.26688],"tcp_start":[0.44651,0.00212,0.29786],"tcp_to_object_dist_end":0.30746,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":224.0,"n_steps_budget":1000.0,"object_pos_end":[0.463,0.00289,0.02602],"object_pos_start":[0.463,0.00289,0.02602],"object_to_goal_dist_end":0.23107,"object_to_goal_dist_start":0.23107,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1024.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_object","tcp_end":[0.60384,0.14961,0.14043],"tcp_start":[0.59541,0.14068,0.26688],"tcp_to_object_dist_end":0.23335,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.463,0.00289,0.02602],"object_pos_start":[0.463,0.00289,0.02602],"object_to_goal_dist_end":0.23107,"object_to_goal_dist_start":0.23107,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1556.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.59692,0.14775,0.15974],"tcp_start":[0.60384,0.14961,0.14043],"tcp_to_object_dist_end":0.23833,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":389.0,"n_steps_budget":1000.0,"object_pos_end":[0.463,0.00289,0.02602],"object_pos_start":[0.463,0.00289,0.02602],"object_to_goal_dist_end":0.23107,"object_to_goal_dist_start":0.23107,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1112.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.59561,0.14719,0.33831],"tcp_start":[0.59692,0.14775,0.15974],"tcp_to_object_dist_end":0.36869,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```