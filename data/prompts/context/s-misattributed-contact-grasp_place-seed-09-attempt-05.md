## Search State

- **Seed**: 9
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 8 | -0.2863 | 0.14 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6 | -0.3197 | 0.14 | ❌ rejected |
| 3 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6 | -0.1514 | 0.17 | ✅ accepted |
| 2 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | admittance_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 7 | -0.1532 | 0.17 | ✅ accepted |
| 1 | rotate → pull → push → descend → descend → grasp → approach | impedance_motion | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | linear_cartesian | impedance_control | impedance_control | impedance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | time_limit | time_limit | pose_tolerance | contact_detected | grasp_success | pose_tolerance | 6 | -0.1646 | 0.13 | ✅ accepted |

**Proposal policy**: task_score is 0.14 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.286) — your mutation base

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
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_object
- id: descend_to_grasp
  type: descend
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    descend_force_threshold:
      type: scalar
      range:
      - 2.0
      - 15.0
      default: 8.0
      binds_to:
      - path: termination.force_threshold
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
      distance: 0.1
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
      default: 0.1
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
  subtask_id: reach_goal
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
  subtask_id: reach_goal
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
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
- **grasp** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=grasp_bilateral, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=1.0
  - retries: max_attempts=1, strategy=repeat
- **lift** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.1, mode=add_to_offset, sign=positive}, tolerance=0.02
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

- **Composite score**: -0.286
- **task_score** (E): 0.140
- **fitness_score**: 0.169  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.125
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.580

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 0.00 | 1.00 | 0.2081 |
| descend_to_grasp | 1.00 | 1.00 | 0.0000 |
| grasp | 1.00 | 1.00 | 0.0000 |
| lift | 1.00 | 1.00 | 0.1036 |
| approach_goal | 0.00 | 1.00 | 0.1910 |
| descend_place | 0.00 | 1.00 | 0.0005 |
| release_object | 1.00 | 1.00 | 0.0223 |
| retract | 1.00 | 1.00 | 0.1597 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.385, -0.012, 0.128) | (0.515, -0.017, 0.030)→(0.474, -0.019, 0.016) | 0.268→0.296 | 1.00 / 5.333 | 159.707 | 94.911 |
| descend_to_grasp | descend | 1.00 / force_exceeded | (0.385, -0.012, 0.128)→(0.385, -0.012, 0.128) | (0.474, -0.019, 0.016)→(0.474, -0.019, 0.016) | 0.296→0.296 | 1.00 / 9.333 | 501.257 | 98.607 |
| grasp | grasp | 1.00 / step_budget | (0.386, -0.012, 0.128)→(0.386, -0.012, 0.128) | (0.474, -0.019, 0.016)→(0.473, -0.019, 0.016) | 0.296→0.297 | 1.00 / 8.333 | 94250.623 | 97.686 |
| lift | lift | 1.00 / step_budget | (0.384, -0.013, 0.231)→(0.384, -0.013, 0.335) | (0.473, -0.019, 0.016)→(0.473, -0.019, 0.016) | 0.297→0.297 | 1.00 / 9.000 | 231.382 | 407.514 |
| approach_goal | approach | 0.00 / step_budget | (0.384, -0.013, 0.335)→(0.518, 0.111, 0.309) | (0.473, -0.019, 0.016)→(0.473, -0.019, 0.016) | 0.297→0.297 | 1.00 / 9.333 | 195.594 | 201.422 |
| descend_place | descend | 0.00 / step_budget | (0.518, 0.111, 0.309)→(0.518, 0.111, 0.309) | (0.473, -0.019, 0.016)→(0.473, -0.019, 0.016) | 0.297→0.297 | 1.00 / 5.333 | 89.479 | 212.088 |
| release_object | release | 1.00 / step_budget | (0.518, 0.111, 0.309)→(0.519, 0.112, 0.331) | (0.473, -0.019, 0.016)→(0.473, -0.019, 0.016) | 0.297→0.297 | 1.00 / 4.667 | 175.145 | 202.596 |
| retract | retract | 1.00 / step_budget | (0.519, 0.112, 0.331)→(0.520, 0.110, 0.490) | (0.473, -0.019, 0.016)→(0.473, -0.019, 0.016) | 0.297→0.297 | 1.00 / 5.333 | 197.809 | 1362.976 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 0.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: 0.000
- terminal_score: 0.160
- phase_score: 0.038
- phase_breakdown.reach_goal_score: 0.019
- phase_breakdown.reach_object_score: 0.081
- grasp_place_fitness: 0.207

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.207
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.160
- **Median Q (composite search score)**: -0.298
- **K-run variance**: 0.0008
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.305


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":62.0,"average_failure_rate":0.29952,"average_mean_iterations":63.3285,"average_solve_count":207.0,"average_success_count":145.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.transport_speed":0.08682,"approach_object.approach_arc":0.24997,"approach_object.approach_speed":0.09906,"descend_to_grasp.descend_force_threshold":6.65667,"descend_to_grasp.descend_speed":0.07131,"lift.lift_height":0.08599,"release_object.release_timeout":0.29747,"retract.retract_height":0.15549},"optimized_scores":{"best_composite_score":-0.31275,"best_fitness_score":0.14225,"best_task_score":0.10728},"replay_outcomes":[{"contacts":{"omitted_contact_groups":10,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":320.0,"contact_point_centroid":[0.63858,-0.0149,-0.00078],"force_p95":246.14086,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1348.62246,"mean_force":209.05231,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39745,-0.01376,0.12357]},{"body_a":"link5","body_b":"hand","contact_count":132.0,"contact_point_centroid":[0.54955,0.04695,0.28003],"force_p95":380.51028,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":454.17062,"mean_force":305.65867,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51547,0.12317,0.30811]},{"body_a":"link5","body_b":"hand","contact_count":200.0,"contact_point_centroid":[0.54601,0.05712,0.25841],"force_p95":223.90056,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":257.14578,"mean_force":150.52863,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.52337,0.12906,0.31254]},{"body_a":"link5","body_b":"hand","contact_count":2.0,"contact_point_centroid":[0.54616,0.05689,0.25798],"force_p95":245.77726,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":249.0791,"mean_force":216.06068,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.5222,0.12928,0.30996]},{"body_a":"link5","body_b":"hand","contact_count":40.0,"contact_point_centroid":[0.54734,0.05489,0.36421],"force_p95":227.45423,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":230.99604,"mean_force":184.6351,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.52551,0.12907,0.42167]},{"body_a":"world","body_b":"link6","contact_count":5.0,"contact_point_centroid":[0.63876,-0.01618,-9e-05],"force_p95":93.12792,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":93.61633,"mean_force":80.77674,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.40506,-0.01579,0.14117]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.63857,-0.01614,-0.00013],"force_p95":78.98922,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":85.22133,"mean_force":70.97283,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.405,-0.01576,0.14128]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.63769,-0.0161,-0.00024],"force_p95":76.84469,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":76.84469,"mean_force":76.84469,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.40457,-0.01572,0.1418]},{"body_a":"grasp_target","body_b":"link7","contact_count":174.0,"contact_point_centroid":[0.51264,-0.01632,0.03755],"force_p95":2.74737,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.96172,"mean_force":0.61465,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39423,-0.01282,0.10773]},{"body_a":"grasp_target","body_b":"link6","contact_count":100.0,"contact_point_centroid":[0.5394,-0.02449,0.02808],"force_p95":0.83545,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.77908,"mean_force":0.49103,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.38952,-0.01251,0.10229]},{"body_a":"grasp_target","body_b":"hand","contact_count":92.0,"contact_point_centroid":[0.49475,-0.02491,0.05095],"force_p95":2.20278,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.77568,"mean_force":0.85048,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39016,-0.01237,0.0936]},{"body_a":"world","body_b":"grasp_target","contact_count":1521.0,"contact_point_centroid":[0.51323,-0.02211,-0.00234],"force_p95":0.34409,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.22586,"mean_force":0.17375,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.42934,-0.01213,0.14992]},{"body_a":"left_finger","body_b":"link5","contact_count":154.0,"contact_point_centroid":[0.51539,0.09077,0.35211],"force_p95":1.40094,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1.56391,"mean_force":0.64334,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.52555,0.12971,0.37218]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.49732,-0.0227,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.405,-0.01576,0.14128]},{"body_a":"world","body_b":"grasp_target","contact_count":1624.0,"contact_point_centroid":[0.49732,-0.0227,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.40272,-0.01588,0.20634]},{"body_a":"world","body_b":"grasp_target","contact_count":3468.0,"contact_point_centroid":[0.49732,-0.0227,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.47687,0.07616,0.28857]}],"total_contact_groups":26},"final_pose_error":0.02961,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.49732,-0.0227,0.01602],"final_tcp_position":[0.52572,0.12851,0.4584],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":9748.92296,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":440.0,"n_steps_budget":1000.0,"object_pos_end":[0.49732,-0.0227,0.01602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.33485,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":76.84469,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5.0,"raw_peak_contact_force":76.84469,"subtask_id":"reach_object","tcp_end":[0.40457,-0.01572,0.1418],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15643,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.49732,-0.0227,0.01602],"object_pos_start":[0.49732,-0.0227,0.01602],"object_to_goal_dist_end":0.33485,"object_to_goal_dist_start":0.33485,"object_z_max":0.01602,"peak_contact_force":68.02829,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3489.0,"raw_peak_contact_force":85.22133,"subtask_id":"reach_object","tcp_end":[0.40457,-0.01572,0.14177],"tcp_start":[0.40457,-0.01572,0.1418],"tcp_to_object_dist_end":0.15641,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.49732,-0.0227,0.01602],"object_pos_start":[0.49732,-0.0227,0.01602],"object_to_goal_dist_end":0.33485,"object_to_goal_dist_start":0.33485,"object_z_max":0.01602,"peak_contact_force":9748.92296,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3332.0,"raw_peak_contact_force":93.61633,"tcp_end":[0.40507,-0.01579,0.14112],"tcp_start":[0.40507,-0.01579,0.14112],"tcp_to_object_dist_end":0.15559,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":406.0,"n_steps_budget":600.0,"object_pos_end":[0.49732,-0.0227,0.01602],"object_pos_start":[0.49732,-0.0227,0.01602],"object_to_goal_dist_end":0.33485,"object_to_goal_dist_start":0.33485,"object_z_max":0.01602,"peak_contact_force":268.98073,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":7303.0,"raw_peak_contact_force":454.17062,"tcp_end":[0.40198,-0.01595,0.27357],"tcp_start":[0.40316,-0.01586,0.20726],"tcp_to_object_dist_end":0.27472,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":867.0,"n_steps_budget":1000.0,"object_pos_end":[0.49732,-0.0227,0.01602],"object_pos_start":[0.49732,-0.0227,0.01602],"object_to_goal_dist_end":0.33485,"object_to_goal_dist_start":0.33485,"object_z_max":0.01602,"peak_contact_force":259.76584,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":18.0,"raw_peak_contact_force":249.0791,"subtask_id":"reach_goal","tcp_end":[0.52209,0.12934,0.30983],"tcp_start":[0.40198,-0.01595,0.27357],"tcp_to_object_dist_end":0.33175,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.49732,-0.0227,0.01602],"object_pos_start":[0.49732,-0.0227,0.01602],"object_to_goal_dist_end":0.33485,"object_to_goal_dist_start":0.33485,"object_z_max":0.01602,"peak_contact_force":98.65496,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1229.0,"raw_peak_contact_force":257.14578,"subtask_id":"reach_goal","tcp_end":[0.52239,0.12923,0.31011],"tcp_start":[0.52209,0.12934,0.30983],"tcp_to_object_dist_end":0.33196,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49732,-0.0227,0.01602],"object_pos_start":[0.49732,-0.0227,0.01602],"object_to_goal_dist_end":0.33485,"object_to_goal_dist_start":0.33485,"object_z_max":0.01602,"peak_contact_force":229.07439,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1282.0,"raw_peak_contact_force":230.99604,"tcp_end":[0.52383,0.12917,0.33245],"tcp_start":[0.52239,0.12923,0.31011],"tcp_to_object_dist_end":0.35199,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":272.0,"n_steps_budget":990.0,"object_pos_end":[0.49732,-0.0227,0.01602],"object_pos_start":[0.49732,-0.0227,0.01602],"object_to_goal_dist_end":0.33485,"object_to_goal_dist_start":0.33485,"object_z_max":0.01602,"peak_contact_force":192.50072,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2214.0,"raw_peak_contact_force":1348.62246,"tcp_end":[0.52572,0.12851,0.4584],"tcp_start":[0.52383,0.12917,0.33245],"tcp_to_object_dist_end":0.46837,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":54.0,"average_failure_rate":0.28421,"average_mean_iterations":60.47368,"average_solve_count":190.0,"average_success_count":136.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.transport_speed":0.14513,"approach_object.approach_arc":0.23751,"approach_object.approach_speed":0.12309,"descend_to_grasp.descend_force_threshold":7.21454,"descend_to_grasp.descend_speed":0.01816,"lift.lift_height":0.13355,"release_object.release_timeout":0.60064,"retract.retract_height":0.17919},"optimized_scores":{"best_composite_score":-0.29806,"best_fitness_score":0.15694,"best_task_score":0.15284},"replay_outcomes":[{"contacts":{"omitted_contact_groups":11,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":440.0,"contact_point_centroid":[0.63945,-0.01815,-0.00064],"force_p95":231.55346,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1393.69256,"mean_force":207.10799,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.40293,-0.01704,0.13244]},{"body_a":"link5","body_b":"hand","contact_count":166.0,"contact_point_centroid":[0.55101,0.01175,0.31358],"force_p95":354.49986,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":372.50187,"mean_force":310.45259,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52233,0.08596,0.33842]},{"body_a":"link5","body_b":"hand","contact_count":4.0,"contact_point_centroid":[0.55222,0.0223,0.27548],"force_p95":282.0833,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":282.41504,"mean_force":256.11658,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.53212,0.08617,0.33409]},{"body_a":"link5","body_b":"hand","contact_count":240.0,"contact_point_centroid":[0.54825,0.01773,0.38283],"force_p95":260.85124,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":272.35563,"mean_force":216.62155,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.53274,0.08299,0.45375]},{"body_a":"link5","body_b":"hand","contact_count":200.0,"contact_point_centroid":[0.55178,0.02246,0.27402],"force_p95":221.35636,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":270.27789,"mean_force":132.60529,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.53281,0.08661,0.33395]},{"body_a":"world","body_b":"link6","contact_count":4.0,"contact_point_centroid":[0.63792,-0.02097,-0.00011],"force_p95":104.80423,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":107.68546,"mean_force":88.76219,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.41396,-0.02125,0.1561]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.63775,-0.02093,-0.00013],"force_p95":77.22318,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":84.45288,"mean_force":71.22182,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.41391,-0.02123,0.15622]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.63688,-0.02089,-0.00024],"force_p95":70.40131,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":70.40131,"mean_force":70.40131,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.41353,-0.0212,0.15671]},{"body_a":"grasp_target","body_b":"link6","contact_count":272.0,"contact_point_centroid":[0.54162,-0.01813,0.02771],"force_p95":0.35684,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.8858,"mean_force":0.17535,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39839,-0.01552,0.12107]},{"body_a":"grasp_target","body_b":"link7","contact_count":170.0,"contact_point_centroid":[0.52891,-0.0205,0.03007],"force_p95":2.87724,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.67549,"mean_force":0.50798,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39565,-0.01462,0.10709]},{"body_a":"world","body_b":"grasp_target","contact_count":2145.0,"contact_point_centroid":[0.51806,-0.03023,-0.00261],"force_p95":0.39701,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.50323,"mean_force":0.17639,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.42431,-0.01542,0.14879]},{"body_a":"grasp_target","body_b":"hand","contact_count":18.0,"contact_point_centroid":[0.50635,-0.04044,0.03789],"force_p95":1.9365,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.18657,"mean_force":0.85234,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39895,-0.01383,0.06418]},{"body_a":"left_finger","body_b":"link5","contact_count":86.0,"contact_point_centroid":[0.52458,0.05051,0.34667],"force_p95":0.76486,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1.48378,"mean_force":0.39575,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.53434,0.0867,0.37083]},{"body_a":"left_finger","body_b":"link5","contact_count":39.0,"contact_point_centroid":[0.52414,0.05118,0.32447],"force_p95":0.31662,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.31743,"mean_force":0.28428,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.5333,0.08664,0.34792]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.50975,-0.03089,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.41353,-0.0212,0.15671]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.50975,-0.03089,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.41391,-0.02123,0.15622]}],"total_contact_groups":27},"final_pose_error":0.02971,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.50975,-0.03089,0.01602],"final_tcp_position":[0.52947,0.07874,0.50477],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":273004.72857,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":560.0,"n_steps_budget":1000.0,"object_pos_end":[0.50975,-0.03089,0.01602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.28175,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":214.71415,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5.0,"raw_peak_contact_force":70.40131,"subtask_id":"reach_object","tcp_end":[0.41353,-0.0212,0.15671],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17072,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50975,-0.03089,0.01602],"object_pos_start":[0.50975,-0.03089,0.01602],"object_to_goal_dist_end":0.28175,"object_to_goal_dist_start":0.28175,"object_z_max":0.01602,"peak_contact_force":68.89948,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3498.0,"raw_peak_contact_force":84.45288,"subtask_id":"reach_object","tcp_end":[0.41353,-0.0212,0.15668],"tcp_start":[0.41353,-0.0212,0.15671],"tcp_to_object_dist_end":0.17069,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.50975,-0.03089,0.01602],"object_pos_start":[0.50975,-0.03089,0.01602],"object_to_goal_dist_end":0.28175,"object_to_goal_dist_start":0.28175,"object_z_max":0.01602,"peak_contact_force":273002.82482,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":5522.0,"raw_peak_contact_force":107.68546,"tcp_end":[0.41397,-0.02125,0.15608],"tcp_start":[0.41397,-0.02125,0.15608],"tcp_to_object_dist_end":0.16995,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":673.0,"n_steps_budget":840.0,"object_pos_end":[0.50975,-0.03089,0.01602],"object_pos_start":[0.50975,-0.03089,0.01602],"object_to_goal_dist_end":0.28175,"object_to_goal_dist_start":0.28175,"object_z_max":0.01602,"peak_contact_force":276.42465,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":6085.0,"raw_peak_contact_force":372.50187,"tcp_end":[0.41292,-0.02151,0.38342],"tcp_start":[0.41277,-0.02135,0.26978],"tcp_to_object_dist_end":0.38006,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":713.0,"n_steps_budget":1000.0,"object_pos_end":[0.50975,-0.03089,0.01602],"object_pos_start":[0.50975,-0.03089,0.01602],"object_to_goal_dist_end":0.28175,"object_to_goal_dist_start":0.28175,"object_z_max":0.01602,"peak_contact_force":235.30989,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":38.0,"raw_peak_contact_force":282.41504,"subtask_id":"reach_goal","tcp_end":[0.53203,0.08624,0.33427],"tcp_start":[0.41292,-0.02151,0.38342],"tcp_to_object_dist_end":0.33985,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":6.0,"n_steps":4.0,"n_steps_budget":1000.0,"object_pos_end":[0.50975,-0.03089,0.01602],"object_pos_start":[0.50975,-0.03089,0.01602],"object_to_goal_dist_end":0.28175,"object_to_goal_dist_start":0.28175,"object_z_max":0.01602,"peak_contact_force":60.9422,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1263.0,"raw_peak_contact_force":270.27789,"subtask_id":"reach_goal","tcp_end":[0.53209,0.08619,0.33344],"tcp_start":[0.53203,0.08624,0.33427],"tcp_to_object_dist_end":0.33906,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50975,-0.03089,0.01602],"object_pos_start":[0.50975,-0.03089,0.01602],"object_to_goal_dist_end":0.28175,"object_to_goal_dist_start":0.28175,"object_z_max":0.01602,"peak_contact_force":215.21763,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1730.0,"raw_peak_contact_force":272.35563,"tcp_end":[0.53331,0.0866,0.35397],"tcp_start":[0.53209,0.08619,0.33344],"tcp_to_object_dist_end":0.35857,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":351.0,"n_steps_budget":1000.0,"object_pos_end":[0.50975,-0.03089,0.01602],"object_pos_start":[0.50975,-0.03089,0.01602],"object_to_goal_dist_end":0.28175,"object_to_goal_dist_start":0.28175,"object_z_max":0.01602,"peak_contact_force":196.69523,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3054.0,"raw_peak_contact_force":1393.69256,"tcp_end":[0.52947,0.07874,0.50477],"tcp_start":[0.53331,0.0866,0.35397],"tcp_to_object_dist_end":0.50128,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":72.0,"average_failure_rate":0.28125,"average_mean_iterations":59.71875,"average_solve_count":256.0,"average_success_count":184.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.transport_speed":0.07362,"approach_object.approach_arc":0.12708,"approach_object.approach_speed":0.03924,"descend_to_grasp.descend_force_threshold":10.05059,"descend_to_grasp.descend_speed":0.08868,"lift.lift_height":0.15048,"release_object.release_timeout":0.33786,"retract.retract_height":0.23177},"optimized_scores":{"best_composite_score":-0.24822,"best_fitness_score":0.20678,"best_task_score":0.15953},"replay_outcomes":[{"contacts":{"omitted_contact_groups":11,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":852.0,"contact_point_centroid":[0.59889,-0.00154,-0.00046],"force_p95":205.20296,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1346.61219,"mean_force":207.29412,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.34908,-0.00023,0.1006]},{"body_a":"link5","body_b":"hand","contact_count":21.0,"contact_point_centroid":[0.54743,0.02948,0.27812],"force_p95":378.12712,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":395.8686,"mean_force":254.49615,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.49889,0.12044,0.27959]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.58322,0.00633,-0.00027],"force_p95":137.48732,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":137.48732,"mean_force":137.48732,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.33755,-0.00023,0.08627]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.584,0.00631,-0.00014],"force_p95":91.42536,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":126.14601,"mean_force":73.67494,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.3381,-0.00026,0.08587]},{"body_a":"link5","body_b":"hand","contact_count":200.0,"contact_point_centroid":[0.54757,0.02674,0.27999],"force_p95":108.44608,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":108.84046,"mean_force":68.63844,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.50053,0.11841,0.28525]},{"body_a":"link5","body_b":"hand","contact_count":7.0,"contact_point_centroid":[0.5492,0.0297,0.30096],"force_p95":97.77961,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":104.43661,"mean_force":54.96931,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.50124,0.12087,0.30648]},{"body_a":"world","body_b":"link6","contact_count":4.0,"contact_point_centroid":[0.58424,0.00629,-0.00011],"force_p95":86.84833,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":91.75647,"mean_force":61.0362,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.33826,-0.00028,0.0857]},{"body_a":"link5","body_b":"hand","contact_count":1.0,"contact_point_centroid":[0.54741,0.02611,0.27741],"force_p95":72.77188,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":72.77188,"mean_force":72.77188,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.50045,0.11785,0.28205]},{"body_a":"grasp_target","body_b":"link7","contact_count":487.0,"contact_point_centroid":[0.44824,-0.00771,0.03308],"force_p95":0.43538,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.68046,"mean_force":0.21683,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.34484,-0.00025,0.09348]},{"body_a":"grasp_target","body_b":"hand","contact_count":76.0,"contact_point_centroid":[0.4417,-0.01534,0.04864],"force_p95":3.19949,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.60026,"mean_force":1.00395,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.35562,-0.00022,0.08469]},{"body_a":"world","body_b":"grasp_target","contact_count":3643.0,"contact_point_centroid":[0.42566,-0.00296,-0.00244],"force_p95":0.25484,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.68661,"mean_force":0.16087,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.36517,-0.00018,0.11231]},{"body_a":"grasp_target","body_b":"link7","contact_count":27.0,"contact_point_centroid":[0.43811,-0.00421,0.0376],"force_p95":0.47894,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.52038,"mean_force":0.22152,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.33761,-0.00031,0.08904]},{"body_a":"world","body_b":"grasp_target","contact_count":2781.0,"contact_point_centroid":[0.41049,-0.00447,-0.00199],"force_p95":0.13136,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24275,"mean_force":0.12272,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.33577,-0.0004,0.2138]},{"body_a":"grasp_target","body_b":"link7","contact_count":550.0,"contact_point_centroid":[0.44034,-0.00395,0.03473],"force_p95":0.2224,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23363,"mean_force":0.15612,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.3381,-0.00026,0.08587]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.41597,-0.0038,-0.00268],"force_p95":0.19579,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1986,"mean_force":0.14685,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.33755,-0.00023,0.08627]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.41339,-0.00412,-0.00237],"force_p95":0.18557,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19518,"mean_force":0.14883,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.3381,-0.00026,0.08587]}],"total_contact_groups":27},"final_pose_error":0.02994,"key_states":{"actual_goal_position":[0.61015,0.15287,0.12219],"final_object_position":[0.41072,-0.0045,0.01602],"final_tcp_position":[0.50357,0.12136,0.50783],"realised_goal_position":[0.61015,0.15287,0.12219],"realised_object_initial_position":[0.46286,-7e-05,0.03]},"peak_contact_force":1366.84211,"phases":[{"contact_detected":true,"contact_event_count":6.0,"n_steps":969.0,"n_steps_budget":1000.0,"object_pos_end":[0.41557,-0.00399,0.01463],"object_pos_start":[0.46286,-7e-05,0.03],"object_to_goal_dist_end":0.27209,"object_to_goal_dist_start":0.23148,"object_z_max":0.03,"peak_contact_force":187.56086,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":6.0,"raw_peak_contact_force":137.48732,"subtask_id":"reach_object","tcp_end":[0.33755,-0.00023,0.08627],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.10599,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.41555,-0.00399,0.01464],"object_pos_start":[0.41557,-0.00399,0.01463],"object_to_goal_dist_end":0.2721,"object_to_goal_dist_start":0.27209,"object_z_max":0.01463,"peak_contact_force":1366.84211,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4045.0,"raw_peak_contact_force":126.14601,"subtask_id":"reach_object","tcp_end":[0.33754,-0.00023,0.08628],"tcp_start":[0.33755,-0.00023,0.08627],"tcp_to_object_dist_end":0.10598,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.41157,-0.00445,0.01548],"object_pos_start":[0.41555,-0.00399,0.01464],"object_to_goal_dist_end":0.2749,"object_to_goal_dist_start":0.2721,"object_z_max":0.01556,"peak_contact_force":0.12263,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":5735.0,"raw_peak_contact_force":91.75647,"tcp_end":[0.33826,-0.00028,0.08568],"tcp_start":[0.33826,-0.00028,0.08568],"tcp_to_object_dist_end":0.10158,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":701.0,"n_steps_budget":960.0,"object_pos_end":[0.41072,-0.0045,0.01602],"object_pos_start":[0.41098,-0.00451,0.01556],"object_to_goal_dist_end":0.27533,"object_to_goal_dist_start":0.27533,"object_z_max":0.01745,"peak_contact_force":148.74103,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4239.0,"raw_peak_contact_force":395.8686,"tcp_end":[0.33583,-0.00044,0.34721],"tcp_start":[0.33635,-0.00037,0.2164],"tcp_to_object_dist_end":0.33958,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":509.0,"n_steps_budget":1000.0,"object_pos_end":[0.41072,-0.0045,0.01602],"object_pos_start":[0.41072,-0.0045,0.01602],"object_to_goal_dist_end":0.27533,"object_to_goal_dist_start":0.27533,"object_z_max":0.01602,"peak_contact_force":91.70567,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9.0,"raw_peak_contact_force":72.77188,"subtask_id":"reach_goal","tcp_end":[0.50045,0.11785,0.28205],"tcp_start":[0.33583,-0.00044,0.34721],"tcp_to_object_dist_end":0.30625,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.41072,-0.0045,0.01602],"object_pos_start":[0.41072,-0.0045,0.01602],"object_to_goal_dist_end":0.27533,"object_to_goal_dist_start":0.27533,"object_z_max":0.01602,"peak_contact_force":108.84046,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1223.0,"raw_peak_contact_force":108.84046,"subtask_id":"reach_goal","tcp_end":[0.50057,0.11762,0.28217],"tcp_start":[0.50045,0.11785,0.28205],"tcp_to_object_dist_end":0.3063,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.41072,-0.0045,0.01602],"object_pos_start":[0.41072,-0.0045,0.01602],"object_to_goal_dist_end":0.27533,"object_to_goal_dist_start":0.27533,"object_z_max":0.01602,"peak_contact_force":81.14225,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1615.0,"raw_peak_contact_force":104.43661,"tcp_end":[0.50128,0.12064,0.30591],"tcp_start":[0.50057,0.11762,0.28217],"tcp_to_object_dist_end":0.32847,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":6.0,"n_steps":402.0,"n_steps_budget":1000.0,"object_pos_end":[0.41072,-0.0045,0.01602],"object_pos_start":[0.41072,-0.0045,0.01602],"object_to_goal_dist_end":0.27533,"object_to_goal_dist_start":0.27533,"object_z_max":0.01602,"peak_contact_force":204.23114,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":5066.0,"raw_peak_contact_force":1346.61219,"tcp_end":[0.50357,0.12136,0.50783],"tcp_start":[0.50128,0.12064,0.30591],"tcp_to_object_dist_end":0.51608,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```