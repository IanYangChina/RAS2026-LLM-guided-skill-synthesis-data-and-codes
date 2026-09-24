## Search State

- **Seed**: 9
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6 | -0.3197 | 0.14 | ❌ rejected |
| 3 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6 | -0.1514 | 0.17 | ✅ accepted |
| 2 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | admittance_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 7 | -0.1532 | 0.17 | ✅ accepted |
| 1 | rotate → pull → push → descend → descend → grasp → approach | impedance_motion | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | linear_cartesian | impedance_control | impedance_control | impedance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | time_limit | time_limit | pose_tolerance | contact_detected | grasp_success | pose_tolerance | 6 | -0.1646 | 0.13 | ✅ accepted |
| 0 | rotate → pull → push → descend → descend → grasp → approach | impedance_motion | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | linear_cartesian | impedance_control | impedance_control | impedance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | time_limit | time_limit | pose_tolerance | contact_detected | grasp_success | pose_tolerance | 6 | -0.1649 | 0.13 | ✅ accepted |

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

## Current Skill (Q=-0.320) — your mutation base

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

- **Composite score**: -0.320
- **task_score** (E): 0.144
- **fitness_score**: 0.160  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.480

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 0.00 | 1.00 | 0.1535 |
| descend_to_grasp | 0.00 | 1.00 | 0.0464 |
| grasp | 1.00 | 1.00 | 0.0000 |
| lift | 1.00 | 1.00 | 0.0975 |
| approach_goal | 0.00 | 1.00 | 0.1412 |
| descend_place | 0.00 | 1.00 | 0.0238 |
| release_object | 1.00 | 1.00 | 0.0211 |
| retract | 1.00 | 1.00 | 0.1485 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.423, -0.005, 0.168) | (0.515, -0.017, 0.030)→(0.477, -0.017, 0.016) | 0.268→0.293 | 1.00 / 5.667 | 91097.926 | 698.438 |
| descend_to_grasp | descend | 0.00 / step_budget | (0.423, -0.005, 0.168)→(0.447, -0.027, 0.171) | (0.477, -0.017, 0.016)→(0.477, -0.017, 0.016) | 0.293→0.293 | 1.00 / 10.000 | 91047.751 | 196.275 |
| grasp | grasp | 1.00 / step_budget | (0.447, -0.028, 0.169)→(0.447, -0.028, 0.169) | (0.477, -0.017, 0.016)→(0.477, -0.017, 0.016) | 0.293→0.293 | 1.00 / 8.333 | 6499.326 | 172.590 |
| lift | lift | 1.00 / step_budget | (0.446, -0.028, 0.274)→(0.445, -0.026, 0.371) | (0.477, -0.017, 0.016)→(0.477, -0.017, 0.016) | 0.293→0.293 | 1.00 / 9.333 | 91217.381 | 336.155 |
| approach_goal | approach | 0.00 / step_budget | (0.445, -0.026, 0.371)→(0.524, 0.079, 0.331) | (0.477, -0.017, 0.016)→(0.477, -0.017, 0.016) | 0.293→0.293 | 1.00 / 9.333 | 254.749 | 293.928 |
| descend_place | descend | 0.00 / step_budget | (0.524, 0.079, 0.331)→(0.527, 0.080, 0.308) | (0.477, -0.017, 0.016)→(0.477, -0.017, 0.016) | 0.293→0.293 | 1.00 / 5.333 | 113.563 | 228.551 |
| release_object | release | 1.00 / step_budget | (0.527, 0.080, 0.308)→(0.528, 0.081, 0.329) | (0.477, -0.017, 0.016)→(0.477, -0.017, 0.016) | 0.293→0.293 | 1.00 / 4.667 | 114.565 | 218.538 |
| retract | retract | 1.00 / step_budget | (0.528, 0.081, 0.329)→(0.530, 0.080, 0.477) | (0.477, -0.017, 0.016)→(0.477, -0.017, 0.016) | 0.293→0.293 | 1.00 / 5.000 | 189.663 | 1388.033 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 0.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: 0.000
- terminal_score: 0.153
- phase_score: 0.012
- phase_breakdown.reach_goal_score: 0.013
- phase_breakdown.reach_object_score: 0.010
- grasp_place_fitness: 0.173

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.173
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.172
- **Median Q (composite search score)**: -0.316
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.344


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":55.0,"average_failure_rate":0.24775,"average_mean_iterations":53.91892,"average_solve_count":222.0,"average_success_count":167.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.transport_speed":0.09104,"approach_object.approach_speed":0.07661,"descend_to_grasp.descend_speed":0.09379,"lift.lift_height":0.13856,"release_object.release_timeout":0.66788,"retract.retract_height":0.17256},"optimized_scores":{"best_composite_score":-0.33593,"best_fitness_score":0.14407,"best_task_score":0.10755},"replay_outcomes":[{"contacts":{"omitted_contact_groups":9,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":887.0,"contact_point_centroid":[0.64554,-0.00424,-0.00044],"force_p95":201.95867,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1336.7138,"mean_force":197.59355,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.41113,-0.00418,0.13215]},{"body_a":"world","body_b":"link7","contact_count":24.0,"contact_point_centroid":[0.53588,0.00047,-0.00317],"force_p95":218.79215,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1268.05474,"mean_force":63.56072,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.38607,-0.00246,0.04609]},{"body_a":"world","body_b":"link6","contact_count":944.0,"contact_point_centroid":[0.63491,-0.00913,-0.00022],"force_p95":465.69779,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":941.85115,"mean_force":288.85296,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.43795,-0.01384,0.19297]},{"body_a":"link5","body_b":"hand","contact_count":208.0,"contact_point_centroid":[0.55228,0.0106,0.31843],"force_p95":302.6399,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":329.71391,"mean_force":251.12412,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52085,0.07995,0.35629]},{"body_a":"link5","body_b":"hand","contact_count":3.0,"contact_point_centroid":[0.55068,0.03583,0.28447],"force_p95":262.73526,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":265.96207,"mean_force":233.31723,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.52892,0.09434,0.35234]},{"body_a":"link5","body_b":"hand","contact_count":200.0,"contact_point_centroid":[0.55046,0.03623,0.28402],"force_p95":205.97884,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":239.08047,"mean_force":126.60771,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.53048,0.09452,0.35407]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.68264,-0.02282,-0.00012],"force_p95":70.29539,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":217.58442,"mean_force":67.81626,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46474,-0.03011,0.16426]},{"body_a":"link5","body_b":"hand","contact_count":50.0,"contact_point_centroid":[0.55027,0.03294,0.41012],"force_p95":178.41859,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":187.10549,"mean_force":147.52366,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.53347,0.09473,0.48769]},{"body_a":"world","body_b":"link6","contact_count":5.0,"contact_point_centroid":[0.68273,-0.02289,-9e-05],"force_p95":184.94219,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":185.84252,"mean_force":125.13451,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46473,-0.03024,0.16417]},{"body_a":"grasp_target","body_b":"link7","contact_count":364.0,"contact_point_centroid":[0.52173,-0.01417,0.0327],"force_p95":1.10816,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.1062,"mean_force":0.4723,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.40033,-0.00282,0.10072]},{"body_a":"grasp_target","body_b":"hand","contact_count":154.0,"contact_point_centroid":[0.49994,-0.02863,0.04777],"force_p95":2.03041,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.77983,"mean_force":0.84343,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39526,-0.00252,0.08154]},{"body_a":"world","body_b":"grasp_target","contact_count":3661.0,"contact_point_centroid":[0.50811,-0.02382,-0.00243],"force_p95":0.3605,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.3166,"mean_force":0.1658,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.42345,-0.00399,0.14444]},{"body_a":"grasp_target","body_b":"link6","contact_count":126.0,"contact_point_centroid":[0.5463,-0.02855,0.02347],"force_p95":0.68611,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.81022,"mean_force":0.30864,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39312,-0.00251,0.08301]},{"body_a":"world","body_b":"grasp_target","contact_count":3860.0,"contact_point_centroid":[0.50163,-0.02409,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.43844,-0.01402,0.19286]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.50163,-0.02409,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46474,-0.03011,0.16426]},{"body_a":"world","body_b":"grasp_target","contact_count":3904.0,"contact_point_centroid":[0.50163,-0.02409,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46326,-0.0299,0.29539]}],"total_contact_groups":25},"final_pose_error":0.02998,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.50163,-0.02409,0.01602],"final_tcp_position":[0.53387,0.09477,0.51659],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":273077.28306,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50163,-0.02409,0.01602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.33447,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":341.82637,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4804.0,"raw_peak_contact_force":941.85115,"subtask_id":"reach_object","tcp_end":[0.43159,-0.00697,0.17731],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17667,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":965.0,"n_steps_budget":1000.0,"object_pos_end":[0.50163,-0.02409,0.01602],"object_pos_start":[0.50163,-0.02409,0.01602],"object_to_goal_dist_end":0.33447,"object_to_goal_dist_start":0.33447,"object_z_max":0.01602,"peak_contact_force":66.53323,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3525.0,"raw_peak_contact_force":217.58442,"subtask_id":"reach_object","tcp_end":[0.4649,-0.02966,0.16561],"tcp_start":[0.43159,-0.00697,0.17731],"tcp_to_object_dist_end":0.15413,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.50163,-0.02409,0.01602],"object_pos_start":[0.50163,-0.02409,0.01602],"object_to_goal_dist_end":0.33447,"object_to_goal_dist_start":0.33447,"object_z_max":0.01602,"peak_contact_force":9748.94647,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":8152.0,"raw_peak_contact_force":185.84252,"tcp_end":[0.46473,-0.03017,0.16413],"tcp_start":[0.46473,-0.03016,0.16413],"tcp_to_object_dist_end":0.15276,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":976.0,"n_steps_budget":870.0,"object_pos_end":[0.50163,-0.02409,0.01602],"object_pos_start":[0.50163,-0.02409,0.01602],"object_to_goal_dist_end":0.33447,"object_to_goal_dist_start":0.33447,"object_z_max":0.01602,"peak_contact_force":273077.28306,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":8593.0,"raw_peak_contact_force":329.71391,"subtask_id":"reach_object","tcp_end":[0.46236,-0.02883,0.37962],"tcp_start":[0.46393,-0.03026,0.2829],"tcp_to_object_dist_end":0.36575,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50163,-0.02409,0.01602],"object_pos_start":[0.50163,-0.02409,0.01602],"object_to_goal_dist_end":0.33447,"object_to_goal_dist_start":0.33447,"object_z_max":0.01602,"peak_contact_force":257.27227,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":27.0,"raw_peak_contact_force":265.96207,"subtask_id":"reach_goal","tcp_end":[0.52877,0.09441,0.35225],"tcp_start":[0.46236,-0.02883,0.37962],"tcp_to_object_dist_end":0.35753,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50163,-0.02409,0.01602],"object_pos_start":[0.50163,-0.02409,0.01602],"object_to_goal_dist_end":0.33447,"object_to_goal_dist_start":0.33447,"object_z_max":0.01602,"peak_contact_force":55.36724,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1225.0,"raw_peak_contact_force":239.08047,"subtask_id":"reach_goal","tcp_end":[0.52915,0.09454,0.35221],"tcp_start":[0.52877,0.09441,0.35225],"tcp_to_object_dist_end":0.35757,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50163,-0.02409,0.01602],"object_pos_start":[0.50163,-0.02409,0.01602],"object_to_goal_dist_end":0.33447,"object_to_goal_dist_start":0.33447,"object_z_max":0.01602,"peak_contact_force":145.04631,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1274.0,"raw_peak_contact_force":187.10549,"tcp_end":[0.53104,0.0945,0.37388],"tcp_start":[0.52915,0.09454,0.35221],"tcp_to_object_dist_end":0.37814,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":306.0,"n_steps_budget":1000.0,"object_pos_end":[0.50163,-0.02409,0.01602],"object_pos_start":[0.50163,-0.02409,0.01602],"object_to_goal_dist_end":0.33447,"object_to_goal_dist_start":0.33447,"object_z_max":0.01602,"peak_contact_force":189.87529,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":5216.0,"raw_peak_contact_force":1336.7138,"tcp_end":[0.53387,0.09477,0.51659],"tcp_start":[0.53104,0.0945,0.37388],"tcp_to_object_dist_end":0.51549,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":63.0,"average_failure_rate":0.28899,"average_mean_iterations":62.54587,"average_solve_count":218.0,"average_success_count":155.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.transport_speed":0.13216,"approach_object.approach_speed":0.06539,"descend_to_grasp.descend_speed":0.09359,"lift.lift_height":0.11708,"release_object.release_timeout":0.72684,"retract.retract_height":0.18798},"optimized_scores":{"best_composite_score":-0.30715,"best_fitness_score":0.17285,"best_task_score":0.15293},"replay_outcomes":[{"contacts":{"omitted_contact_groups":14,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":887.0,"contact_point_centroid":[0.64472,-0.00546,-0.00046],"force_p95":200.39104,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1481.39924,"mean_force":198.67084,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.41005,-0.00535,0.13257]},{"body_a":"world","body_b":"link6","contact_count":969.0,"contact_point_centroid":[0.63572,-0.01218,-0.00023],"force_p95":514.79849,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":950.42804,"mean_force":296.91865,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.43812,-0.01763,0.19227]},{"body_a":"link5","body_b":"hand","contact_count":7.0,"contact_point_centroid":[0.53084,0.03176,0.17647],"force_p95":448.00913,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":458.9403,"mean_force":297.32464,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.46502,-0.05008,0.15659]},{"body_a":"world","body_b":"link7","contact_count":23.0,"contact_point_centroid":[0.53824,0.00017,-0.00348],"force_p95":0.0,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":394.04932,"mean_force":17.13258,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.38542,-0.00327,0.04703]},{"body_a":"link5","body_b":"hand","contact_count":50.0,"contact_point_centroid":[0.54958,-0.03285,0.28997],"force_p95":293.70108,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":303.40377,"mean_force":247.72288,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51813,0.03551,0.32772]},{"body_a":"link5","body_b":"hand","contact_count":5.0,"contact_point_centroid":[0.54992,-0.0096,0.26871],"force_p95":287.8835,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":292.475,"mean_force":246.84111,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.52342,0.04934,0.3256]},{"body_a":"world","body_b":"link6","contact_count":545.0,"contact_point_centroid":[0.69021,-0.02152,-0.00013],"force_p95":105.16603,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":258.42135,"mean_force":72.80575,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4647,-0.05254,0.15065]},{"body_a":"link5","body_b":"hand","contact_count":125.0,"contact_point_centroid":[0.54622,-0.01193,0.39108],"force_p95":222.05322,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":237.01683,"mean_force":190.65215,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.52706,0.05009,0.46617]},{"body_a":"world","body_b":"link6","contact_count":4.0,"contact_point_centroid":[0.69033,-0.02166,-0.0001],"force_p95":214.6627,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":222.31063,"mean_force":162.04499,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46469,-0.05263,0.15051]},{"body_a":"link5","body_b":"hand","contact_count":601.0,"contact_point_centroid":[0.52862,0.03643,0.17689],"force_p95":106.90826,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":193.3054,"mean_force":24.56014,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46473,-0.05253,0.15084]},{"body_a":"link5","body_b":"hand","contact_count":200.0,"contact_point_centroid":[0.54917,-0.00448,0.2622],"force_p95":188.51339,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":192.91277,"mean_force":120.62633,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.52559,0.05158,0.3242]},{"body_a":"link5","body_b":"hand","contact_count":4.0,"contact_point_centroid":[0.52648,0.03654,0.17803],"force_p95":11.37473,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":13.38203,"mean_force":3.34551,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46469,-0.05263,0.15051]},{"body_a":"grasp_target","body_b":"link6","contact_count":140.0,"contact_point_centroid":[0.54766,-0.0147,0.02448],"force_p95":0.68922,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.36147,"mean_force":0.38117,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39356,-0.00338,0.08643]},{"body_a":"grasp_target","body_b":"link7","contact_count":425.0,"contact_point_centroid":[0.5292,-0.01692,0.03315],"force_p95":1.16244,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.17504,"mean_force":0.39872,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.40132,-0.00388,0.10657]},{"body_a":"world","body_b":"grasp_target","contact_count":3658.0,"contact_point_centroid":[0.51364,-0.02929,-0.00233],"force_p95":0.33331,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.29635,"mean_force":0.16074,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.42258,-0.00512,0.14504]},{"body_a":"grasp_target","body_b":"hand","contact_count":139.0,"contact_point_centroid":[0.50019,-0.03513,0.04694],"force_p95":2.31655,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.01831,"mean_force":0.94634,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39485,-0.00335,0.08147]}],"total_contact_groups":30},"final_pose_error":0.02977,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.50732,-0.02922,0.01602],"final_tcp_position":[0.52631,0.0487,0.50263],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":273004.12074,"phases":[{"contact_detected":true,"contact_event_count":7.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50732,-0.02922,0.01602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.28167,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":272757.4122,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4976.0,"raw_peak_contact_force":950.42804,"subtask_id":"reach_object","tcp_end":[0.42853,-0.00865,0.17475],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1784,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":11.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50732,-0.02922,0.01602],"object_pos_start":[0.50732,-0.02922,0.01602],"object_to_goal_dist_end":0.28167,"object_to_goal_dist_start":0.28167,"object_z_max":0.01602,"peak_contact_force":273004.12074,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4140.0,"raw_peak_contact_force":258.42135,"subtask_id":"reach_object","tcp_end":[0.46503,-0.05074,0.1558],"tcp_start":[0.42853,-0.00865,0.17475],"tcp_to_object_dist_end":0.14761,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.50732,-0.02922,0.01602],"object_pos_start":[0.50732,-0.02922,0.01602],"object_to_goal_dist_end":0.28167,"object_to_goal_dist_start":0.28167,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":5809.0,"raw_peak_contact_force":222.31063,"tcp_end":[0.46468,-0.05256,0.15047],"tcp_start":[0.46468,-0.05255,0.15047],"tcp_to_object_dist_end":0.14297,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":687.0,"n_steps_budget":750.0,"object_pos_end":[0.50732,-0.02922,0.01602],"object_pos_start":[0.50732,-0.02922,0.01602],"object_to_goal_dist_end":0.28167,"object_to_goal_dist_start":0.28167,"object_z_max":0.01602,"peak_contact_force":269.46482,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4234.0,"raw_peak_contact_force":303.40377,"subtask_id":"reach_object","tcp_end":[0.46298,-0.04975,0.34386],"tcp_start":[0.46367,-0.05247,0.24785],"tcp_to_object_dist_end":0.33146,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":493.0,"n_steps_budget":1000.0,"object_pos_end":[0.50732,-0.02922,0.01602],"object_pos_start":[0.50732,-0.02922,0.01602],"object_to_goal_dist_end":0.28167,"object_to_goal_dist_start":0.28167,"object_z_max":0.01602,"peak_contact_force":245.3171,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":47.0,"raw_peak_contact_force":292.475,"subtask_id":"reach_goal","tcp_end":[0.5229,0.04861,0.32563],"tcp_start":[0.46298,-0.04975,0.34386],"tcp_to_object_dist_end":0.31963,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":6.0,"n_steps":5.0,"n_steps_budget":1000.0,"object_pos_end":[0.50732,-0.02922,0.01602],"object_pos_start":[0.50732,-0.02922,0.01602],"object_to_goal_dist_end":0.28167,"object_to_goal_dist_start":0.28167,"object_z_max":0.01602,"peak_contact_force":62.98134,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1302.0,"raw_peak_contact_force":192.91277,"subtask_id":"reach_goal","tcp_end":[0.52408,0.05032,0.32527],"tcp_start":[0.5229,0.04861,0.32563],"tcp_to_object_dist_end":0.31976,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50732,-0.02922,0.01602],"object_pos_start":[0.50732,-0.02922,0.01602],"object_to_goal_dist_end":0.28167,"object_to_goal_dist_start":0.28167,"object_z_max":0.01602,"peak_contact_force":198.52688,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1587.0,"raw_peak_contact_force":237.01683,"tcp_end":[0.52595,0.05166,0.34427],"tcp_start":[0.52408,0.05032,0.32527],"tcp_to_object_dist_end":0.33859,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":338.0,"n_steps_budget":1000.0,"object_pos_end":[0.50732,-0.02922,0.01602],"object_pos_start":[0.50732,-0.02922,0.01602],"object_to_goal_dist_end":0.28167,"object_to_goal_dist_start":0.28167,"object_z_max":0.01602,"peak_contact_force":190.41124,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":5272.0,"raw_peak_contact_force":1481.39924,"tcp_end":[0.52631,0.0487,0.50263],"tcp_start":[0.52595,0.05166,0.34427],"tcp_to_object_dist_end":0.49318,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":31.0,"average_failure_rate":0.13778,"average_mean_iterations":32.18667,"average_solve_count":225.0,"average_success_count":194.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.transport_speed":0.10756,"approach_object.approach_speed":0.09784,"descend_to_grasp.descend_speed":0.018,"lift.lift_height":0.11945,"release_object.release_timeout":0.52699,"retract.retract_height":0.17379},"optimized_scores":{"best_composite_score":-0.31607,"best_fitness_score":0.16393,"best_task_score":0.17239},"replay_outcomes":[{"contacts":{"omitted_contact_groups":8,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":888.0,"contact_point_centroid":[0.63838,-0.00018,-0.00044],"force_p95":201.24441,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1345.98459,"mean_force":198.28863,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39616,-0.0001,0.11805]},{"body_a":"world","body_b":"link7","contact_count":25.0,"contact_point_centroid":[0.52855,0.00318,-0.00311],"force_p95":205.27221,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1284.1778,"mean_force":61.63072,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.37824,-0.0002,0.04559]},{"body_a":"link5","body_b":"hand","contact_count":135.0,"contact_point_centroid":[0.5408,0.01895,0.29383],"force_p95":365.56017,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":375.34735,"mean_force":332.10152,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5149,0.09725,0.31253]},{"body_a":"link5","body_b":"hand","contact_count":224.0,"contact_point_centroid":[0.53962,0.02613,0.21783],"force_p95":298.90258,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":323.34777,"mean_force":270.24801,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.52744,0.09586,0.27163]},{"body_a":"link5","body_b":"hand","contact_count":200.0,"contact_point_centroid":[0.53083,0.03462,0.17601],"force_p95":220.49775,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":253.65918,"mean_force":185.5272,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.52713,0.09593,0.24773]},{"body_a":"link5","body_b":"hand","contact_count":11.0,"contact_point_centroid":[0.53635,0.03728,0.19791],"force_p95":230.48003,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":231.49055,"mean_force":173.09486,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.52826,0.09728,0.26893]},{"body_a":"world","body_b":"link6","contact_count":1000.0,"contact_point_centroid":[0.61965,0.00029,-0.00025],"force_p95":194.49818,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":203.03488,"mean_force":191.73111,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.40144,-1e-05,0.16274]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.60631,0.00047,-0.00014],"force_p95":87.08518,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":112.81789,"mean_force":75.75937,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.41136,0.00016,0.19099]},{"body_a":"world","body_b":"link6","contact_count":4.0,"contact_point_centroid":[0.60645,0.00042,-0.00011],"force_p95":106.17164,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":109.6169,"mean_force":89.31786,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.4114,0.00013,0.19094]},{"body_a":"grasp_target","body_b":"hand","contact_count":43.0,"contact_point_centroid":[0.44205,0.011,0.0415],"force_p95":3.60098,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.83184,"mean_force":1.3963,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.38733,-0.00018,0.04864]},{"body_a":"left_finger","body_b":"link5","contact_count":320.0,"contact_point_centroid":[0.5105,0.06688,0.3143],"force_p95":1.61436,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3.67186,"mean_force":0.70754,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.52909,0.09805,0.33559]},{"body_a":"world","body_b":"grasp_target","contact_count":3906.0,"contact_point_centroid":[0.4271,0.00139,-0.00214],"force_p95":0.13797,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.3861,"mean_force":0.13904,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.40783,-7e-05,0.12863]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.42202,0.00162,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.40144,-1e-05,0.16274]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.42202,0.00162,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.41136,0.00016,0.19099]},{"body_a":"world","body_b":"grasp_target","contact_count":2372.0,"contact_point_centroid":[0.42202,0.00162,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.41031,2e-05,0.28905]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.42202,0.00162,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.47351,0.05696,0.30816]}],"total_contact_groups":24},"final_pose_error":0.02954,"key_states":{"actual_goal_position":[0.61015,0.15287,0.12219],"final_object_position":[0.42202,0.00162,0.01602],"final_tcp_position":[0.52947,0.09664,0.41253],"realised_goal_position":[0.61015,0.15287,0.12219],"realised_object_initial_position":[0.46286,-7e-05,0.03]},"peak_contact_force":9748.91033,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.42202,0.00162,0.01602],"object_pos_start":[0.46286,-7e-05,0.03],"object_to_goal_dist_end":0.2637,"object_to_goal_dist_start":0.23148,"object_z_max":0.03,"peak_contact_force":194.53925,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5000.0,"raw_peak_contact_force":203.03488,"subtask_id":"reach_object","tcp_end":[0.40818,-0.00011,0.15262],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13731,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.42202,0.00162,0.01602],"object_pos_start":[0.42202,0.00162,0.01602],"object_to_goal_dist_end":0.2637,"object_to_goal_dist_start":0.2637,"object_z_max":0.01602,"peak_contact_force":72.60042,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3500.0,"raw_peak_contact_force":112.81789,"subtask_id":"reach_object","tcp_end":[0.41107,0.00019,0.19098],"tcp_start":[0.40818,-0.00011,0.15262],"tcp_to_object_dist_end":0.17531,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.42202,0.00162,0.01602],"object_pos_start":[0.42202,0.00162,0.01602],"object_to_goal_dist_end":0.2637,"object_to_goal_dist_start":0.2637,"object_z_max":0.01602,"peak_contact_force":9748.91033,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":4893.0,"raw_peak_contact_force":109.6169,"tcp_end":[0.41141,0.00013,0.19091],"tcp_start":[0.4114,0.00013,0.19091],"tcp_to_object_dist_end":0.17522,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":593.0,"n_steps_budget":750.0,"object_pos_end":[0.42202,0.00162,0.01602],"object_pos_start":[0.42202,0.00162,0.01602],"object_to_goal_dist_end":0.2637,"object_to_goal_dist_start":0.2637,"object_z_max":0.01602,"peak_contact_force":305.3953,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":8430.0,"raw_peak_contact_force":375.34735,"subtask_id":"reach_object","tcp_end":[0.41076,-2e-05,0.39008],"tcp_start":[0.41053,5e-05,0.29049],"tcp_to_object_dist_end":0.37424,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.42202,0.00162,0.01602],"object_pos_start":[0.42202,0.00162,0.01602],"object_to_goal_dist_end":0.2637,"object_to_goal_dist_start":0.2637,"object_z_max":0.01602,"peak_contact_force":261.65852,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2096.0,"raw_peak_contact_force":323.34777,"subtask_id":"reach_goal","tcp_end":[0.5211,0.09538,0.31448],"tcp_start":[0.41076,-2e-05,0.39008],"tcp_to_object_dist_end":0.32816,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":224.0,"n_steps_budget":1000.0,"object_pos_end":[0.42202,0.00162,0.01602],"object_pos_start":[0.42202,0.00162,0.01602],"object_to_goal_dist_end":0.2637,"object_to_goal_dist_start":0.2637,"object_z_max":0.01602,"peak_contact_force":222.34182,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1222.0,"raw_peak_contact_force":253.65918,"subtask_id":"reach_goal","tcp_end":[0.52732,0.09508,0.24576],"tcp_start":[0.5211,0.09538,0.31448],"tcp_to_object_dist_end":0.26945,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.42202,0.00162,0.01602],"object_pos_start":[0.42202,0.00162,0.01602],"object_to_goal_dist_end":0.2637,"object_to_goal_dist_start":0.2637,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1563.0,"raw_peak_contact_force":231.49055,"tcp_end":[0.52775,0.09681,0.26823],"tcp_start":[0.52732,0.09508,0.24576],"tcp_to_object_dist_end":0.28957,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":308.0,"n_steps_budget":1000.0,"object_pos_end":[0.42202,0.00162,0.01602],"object_pos_start":[0.42202,0.00162,0.01602],"object_to_goal_dist_end":0.2637,"object_to_goal_dist_start":0.2637,"object_z_max":0.01602,"peak_contact_force":188.70237,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4862.0,"raw_peak_contact_force":1345.98459,"tcp_end":[0.52947,0.09664,0.41253],"tcp_start":[0.52775,0.09681,0.26823],"tcp_to_object_dist_end":0.42165,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```