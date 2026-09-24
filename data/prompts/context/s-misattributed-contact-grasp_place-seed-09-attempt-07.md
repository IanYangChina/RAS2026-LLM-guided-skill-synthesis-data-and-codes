## Search State

- **Seed**: 9
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → descend → grasp → pull → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 8 | 0.0152 | 0.24 | ✅ accepted |
| 6 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 7 | -0.2526 | 0.17 | ✅ accepted |
| 5 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 8 | -0.2863 | 0.14 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6 | -0.3197 | 0.14 | ❌ rejected |
| 3 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6 | -0.1514 | 0.17 | ✅ accepted |

**Proposal policy**: task_score is 0.24 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
    - 0.0
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
- id: pull_up
  type: pull
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.03
      axis: world_z
      mode: add_to_offset
      sign: positive
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    pull_up_speed:
      type: scalar
      range:
      - 0.01
      - 0.06
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: pull_object_follows
    when: after_phase
    predicate: object_lifted
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
      distance: 0.15
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
      default: 0.15
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.02
      - 0.12
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: lift_object_lost
    when: after_phase
    predicate: object_lifted
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 2
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
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0], tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **grasp** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=grasp_bilateral, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=1.0
  - retries: max_attempts=1, strategy=repeat
- **pull_up** (`pull`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.03, mode=add_to_offset, sign=positive}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - pull_up_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=pull_object_follows, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=1.0
  - retries: max_attempts=1, strategy=repeat
- **lift** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.15, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=lift_object_lost, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=repeat
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

## Design Metrics

- **Composite score**: 0.015
- **task_score** (E): 0.236
- **fitness_score**: 0.595  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.580

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1211 |
| descend_to_grasp | 1.00 | 1.00 | 0.1465 |
| grasp | 1.00 | 1.00 | 0.0126 |
| pull_up | 1.00 | 1.00 | 0.0216 |
| lift | 1.00 | 1.00 | 0.0690 |
| approach_goal | 1.00 | 1.00 | 0.2439 |
| descend_place | 1.00 | 1.00 | 0.1228 |
| release_object | 1.00 | 1.00 | 0.0194 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.511, 0.001, 0.186) | (0.515, -0.017, 0.030)→(0.515, -0.017, 0.026) | 0.268→0.270 | 1.00 / 4.000 | 13.854 | 0.123 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.511, 0.001, 0.186)→(0.510, -0.015, 0.040) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 41.333 | 0.170 | 0.262 |
| grasp | grasp | 1.00 / step_budget | (0.510, -0.015, 0.040)→(0.502, -0.015, 0.031) | (0.515, -0.017, 0.026)→(0.515, -0.015, 0.025) | 0.270→0.269 | 1.00 / 38.000 | 0.079 | 0.503 |
| pull_up | pull | 1.00 / step_budget | (0.497, -0.015, 0.052)→(0.493, -0.015, 0.073) | (0.515, -0.015, 0.025)→(0.509, -0.015, 0.044) | 0.269→0.262 | 1.00 / 17.333 | 0.095 | 0.211 |
| lift | lift | 1.00 / step_budget | (0.486, -0.014, 0.211)→(0.483, -0.014, 0.280) | (0.503, -0.015, 0.063)→(0.498, -0.014, 0.130) | 0.257→0.243 | 1.00 / 8.000 | 3249.708 | 2.221 |
| approach_goal | approach | 1.00 / step_budget | (0.483, -0.014, 0.280)→(0.608, 0.169, 0.310) | (0.498, -0.014, 0.261)→(0.531, 0.076, 0.016) | 0.265→0.217 | 1.00 / 8.000 | 0.123 | 0.123 |
| descend_place | descend | 1.00 / step_budget | (0.608, 0.169, 0.310)→(0.613, 0.178, 0.188) | (0.531, 0.076, 0.016)→(0.531, 0.076, 0.016) | 0.217→0.217 | 1.00 / 4.000 | 0.123 | 0.123 |
| release_object | release | 1.00 / step_budget | (0.613, 0.178, 0.188)→(0.607, 0.177, 0.206) | (0.531, 0.076, 0.016)→(0.531, 0.076, 0.016) | 0.217→0.217 | 1.00 / 4.000 | 0.123 | 0.138 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 0.000
- terminal_score: 0.262
- phase_score: 0.070
- phase_breakdown.reach_object_score: 0.234
- phase_breakdown.place_object_score: 0.000
- grasp_place_fitness: 0.608

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.608
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.262
- **Median Q (composite search score)**: 0.018
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.278


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.50987,"average_solve_count":304.0,"average_success_count":304.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.transport_speed":0.09911,"approach_object.approach_arc_height":0.07986,"approach_object.approach_speed":0.05128,"descend_to_grasp.descend_speed":0.0678,"lift.lift_height":0.07689,"lift.lift_speed":0.0481,"pull_up.pull_up_speed":0.02891,"release_object.release_timeout":0.69575},"optimized_scores":{"best_composite_score":0.02764,"best_fitness_score":0.60764,"best_task_score":0.26195},"replay_outcomes":[{"contacts":{"omitted_contact_groups":2,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":955.0,"contact_point_centroid":[0.5877,0.17099,-0.00347],"force_p95":0.6993,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.35502,"mean_force":0.18739,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.58906,0.1821,0.32885]},{"body_a":"world","body_b":"grasp_target","contact_count":265.0,"contact_point_centroid":[0.53058,-0.0169,-0.00134],"force_p95":0.34451,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.50303,"mean_force":0.11365,"phase_index":3.0,"phase_name":"pull_up","phase_type":"pull","tcp_position_centroid":[0.52058,-0.01875,0.03157]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4253.0,"contact_point_centroid":[0.53389,0.02657,0.26554],"force_p95":0.14198,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34974,"mean_force":0.10194,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52857,0.04476,0.26791]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10971.0,"contact_point_centroid":[0.51746,0.0005,0.05356],"force_p95":0.0849,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27997,"mean_force":0.05957,"phase_index":3.0,"phase_name":"pull_up","phase_type":"pull","tcp_position_centroid":[0.51643,-0.01867,0.05083]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53714,-0.02088,-0.00224],"force_p95":0.19078,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.27115,"mean_force":0.14037,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52418,-0.01882,0.03108]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13140.0,"contact_point_centroid":[0.5173,-0.03765,0.05196],"force_p95":0.07806,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25882,"mean_force":0.052,"phase_index":3.0,"phase_name":"pull_up","phase_type":"pull","tcp_position_centroid":[0.51657,-0.01867,0.05005]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4535.0,"contact_point_centroid":[0.53478,0.0668,0.2669],"force_p95":0.14325,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19757,"mean_force":0.09515,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53019,0.04856,0.26951]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3592.0,"contact_point_centroid":[0.52468,0.0004,0.03281],"force_p95":0.09101,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17164,"mean_force":0.05775,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52296,-0.0188,0.02969]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10732.0,"contact_point_centroid":[0.5086,0.00055,0.14679],"force_p95":0.09431,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15186,"mean_force":0.05641,"phase_index":4.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.50738,-0.01848,0.14546]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10481.0,"contact_point_centroid":[0.5087,-0.03752,0.14857],"force_p95":0.0917,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14663,"mean_force":0.05811,"phase_index":4.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.50729,-0.01848,0.14733]},{"body_a":"world","body_b":"grasp_target","contact_count":1288.0,"contact_point_centroid":[0.53702,-0.02132,-0.0019],"force_p95":0.13564,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12301,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51487,0.02248,0.23965]},{"body_a":"world","body_b":"grasp_target","contact_count":804.0,"contact_point_centroid":[0.58774,0.17086,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12265,"mean_force":0.12263,"phase_index":6.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.60512,0.21918,0.28695]},{"body_a":"world","body_b":"grasp_target","contact_count":1368.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53025,-0.01058,0.11085]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.58774,0.17086,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.60306,0.22254,0.2249]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4913.0,"contact_point_centroid":[0.5241,-0.038,0.0316],"force_p95":0.07952,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08552,"mean_force":0.04625,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52297,-0.0188,0.02971]},{"body_a":"left_finger","body_b":"right_finger","contact_count":889.0,"contact_point_centroid":[0.59147,0.18633,0.33318],"force_p95":0.01273,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01649,"mean_force":0.01075,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.59096,0.18632,0.33076]}],"total_contact_groups":18},"final_pose_error":0.01946,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.58774,0.17086,0.01602],"final_tcp_position":[0.60669,0.22404,0.22617],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":2.35502,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":323.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1368.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.53118,-0.00257,0.18108],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1563,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":342.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.17608,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10305.0,"raw_peak_contact_force":0.27115,"subtask_id":"reach_object","tcp_end":[0.53167,-0.01885,0.03978],"tcp_start":[0.53118,-0.00257,0.18108],"tcp_to_object_dist_end":0.01497,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53695,-0.01896,0.02523],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31534,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.07928,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":24376.0,"raw_peak_contact_force":0.50303,"tcp_end":[0.52293,-0.01879,0.02966],"tcp_start":[0.53167,-0.01885,0.03978],"tcp_to_object_dist_end":0.0147,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":654.0,"n_steps_budget":660.0,"object_pos_end":[0.53108,-0.01875,0.0437],"object_pos_start":[0.53695,-0.01896,0.02523],"object_to_goal_dist_end":0.30634,"object_to_goal_dist_start":0.31534,"object_z_max":0.06167,"peak_contact_force":0.11033,"phase_name":"pull_up","phase_peak_obstacle_force":0.0,"phase_type":"pull","raw_contact_event_count":21213.0,"raw_peak_contact_force":0.15186,"tcp_end":[0.51338,-0.0186,0.07217],"tcp_start":[0.51806,-0.0187,0.05096],"tcp_to_object_dist_end":0.03353,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":594.0,"n_steps_budget":990.0,"object_pos_end":[0.51829,-0.01858,0.11773],"object_pos_start":[0.5244,-0.01871,0.06172],"object_to_goal_dist_end":0.27784,"object_to_goal_dist_start":0.29892,"object_z_max":0.22808,"peak_contact_force":0.12265,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":10632.0,"raw_peak_contact_force":2.35502,"subtask_id":"reach_object","tcp_end":[0.503,-0.01839,0.2442],"tcp_start":[0.50596,-0.01845,0.18705],"tcp_to_object_dist_end":0.12739,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":825.0,"n_steps_budget":1000.0,"object_pos_end":[0.58774,0.17086,0.01602],"object_pos_start":[0.5178,-0.01832,0.22834],"object_to_goal_dist_end":0.20094,"object_to_goal_dist_start":0.26372,"object_z_max":0.27481,"peak_contact_force":0.12263,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1660.0,"raw_peak_contact_force":0.12265,"subtask_id":"place_object","tcp_end":[0.60388,0.21476,0.34385],"tcp_start":[0.503,-0.01839,0.2442],"tcp_to_object_dist_end":0.33115,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":201.0,"n_steps_budget":1000.0,"object_pos_end":[0.58774,0.17086,0.01602],"object_pos_start":[0.58774,0.17086,0.01602],"object_to_goal_dist_end":0.20094,"object_to_goal_dist_start":0.20094,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1025.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_object","tcp_end":[0.60669,0.22404,0.22617],"tcp_start":[0.60388,0.21476,0.34385],"tcp_to_object_dist_end":0.2176,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58774,0.17086,0.01602],"object_pos_start":[0.58774,0.17086,0.01602],"object_to_goal_dist_end":0.20094,"object_to_goal_dist_start":0.20094,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1288.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.60193,0.22197,0.2443],"tcp_start":[0.60669,0.22404,0.22617],"tcp_to_object_dist_end":0.23437,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.64463,"average_solve_count":242.0,"average_success_count":242.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.transport_speed":0.10814,"approach_object.approach_arc_height":0.13068,"approach_object.approach_speed":0.1082,"descend_to_grasp.descend_speed":0.09618,"lift.lift_height":0.07249,"lift.lift_speed":0.06112,"pull_up.pull_up_speed":0.05063,"release_object.release_timeout":0.82098},"optimized_scores":{"best_composite_score":-1e-05,"best_fitness_score":0.57999,"best_task_score":0.20755},"replay_outcomes":[{"contacts":{"omitted_contact_groups":2,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1905.0,"contact_point_centroid":[0.54669,0.01547,-0.00263],"force_p95":0.24321,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.09702,"mean_force":0.14992,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.58537,0.09391,0.28388]},{"body_a":"world","body_b":"grasp_target","contact_count":252.0,"contact_point_centroid":[0.53894,-0.02507,-0.00132],"force_p95":0.34118,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5105,"mean_force":0.11469,"phase_index":3.0,"phase_name":"pull_up","phase_type":"pull","tcp_position_centroid":[0.52873,-0.02679,0.03106]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1085.0,"contact_point_centroid":[0.52462,-0.02796,0.2312],"force_p95":0.20928,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.39404,"mean_force":0.1251,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51931,-0.01009,0.23527]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11271.0,"contact_point_centroid":[0.5255,-0.00749,0.0535],"force_p95":0.08455,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28282,"mean_force":0.05938,"phase_index":3.0,"phase_name":"pull_up","phase_type":"pull","tcp_position_centroid":[0.52435,-0.02665,0.0508]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":871.0,"contact_point_centroid":[0.52423,0.00716,0.23127],"force_p95":0.20282,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27389,"mean_force":0.13216,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51871,-0.01109,0.23485]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54571,-0.0288,-0.00222],"force_p95":0.18664,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.26908,"mean_force":0.13928,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.5323,-0.0269,0.03065]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13286.0,"contact_point_centroid":[0.52542,-0.04564,0.052],"force_p95":0.07847,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26563,"mean_force":0.05258,"phase_index":3.0,"phase_name":"pull_up","phase_type":"pull","tcp_position_centroid":[0.52446,-0.02665,0.05019]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8143.0,"contact_point_centroid":[0.51777,-0.0074,0.14166],"force_p95":0.10892,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18725,"mean_force":0.06861,"phase_index":4.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51518,-0.02634,0.14005]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8811.0,"contact_point_centroid":[0.51781,-0.04517,0.14283],"force_p95":0.09967,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17077,"mean_force":0.06445,"phase_index":4.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51509,-0.02634,0.14169]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3599.0,"contact_point_centroid":[0.53289,-0.00767,0.03234],"force_p95":0.09054,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1533,"mean_force":0.05762,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53107,-0.02686,0.02923]},{"body_a":"world","body_b":"grasp_target","contact_count":1052.0,"contact_point_centroid":[0.5456,-0.02923,-0.00188],"force_p95":0.1365,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12309,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51843,0.00834,0.24178]},{"body_a":"world","body_b":"grasp_target","contact_count":1360.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53753,-0.01974,0.11329]},{"body_a":"world","body_b":"grasp_target","contact_count":804.0,"contact_point_centroid":[0.54661,0.01558,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62593,0.15728,0.25637]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.54661,0.01558,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.62392,0.16045,0.19421]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4923.0,"contact_point_centroid":[0.5323,-0.04605,0.0311],"force_p95":0.07878,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08678,"mean_force":0.04609,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53108,-0.02686,0.02924]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1879.0,"contact_point_centroid":[0.58901,0.09881,0.28864],"force_p95":0.01153,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01622,"mean_force":0.01054,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.58856,0.09881,0.2863]}],"total_contact_groups":18},"final_pose_error":0.01959,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.54661,0.01558,0.01602],"final_tcp_position":[0.62824,0.16166,0.19568],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":2.09702,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":264.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1360.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.53735,-0.0126,0.18666],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16171,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":340.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.17241,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10322.0,"raw_peak_contact_force":0.26908,"subtask_id":"reach_object","tcp_end":[0.53991,-0.02704,0.03967],"tcp_start":[0.53735,-0.0126,0.18666],"tcp_to_object_dist_end":0.01495,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54552,-0.02697,0.02529],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.2597,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.08249,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":24809.0,"raw_peak_contact_force":0.5105,"tcp_end":[0.53104,-0.02686,0.02919],"tcp_start":[0.53991,-0.02704,0.03967],"tcp_to_object_dist_end":0.015,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":668.0,"n_steps_budget":600.0,"object_pos_end":[0.53958,-0.02673,0.04366],"object_pos_start":[0.54552,-0.02697,0.02529],"object_to_goal_dist_end":0.25137,"object_to_goal_dist_start":0.2597,"object_z_max":0.06128,"peak_contact_force":0.11551,"phase_name":"pull_up","phase_peak_obstacle_force":0.0,"phase_type":"pull","raw_contact_event_count":16954.0,"raw_peak_contact_force":0.18725,"tcp_end":[0.52136,-0.02655,0.07174],"tcp_start":[0.5261,-0.0267,0.05054],"tcp_to_object_dist_end":0.03347,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":553.0,"n_steps_budget":750.0,"object_pos_end":[0.5283,-0.02632,0.11254],"object_pos_start":[0.53272,-0.02662,0.06133],"object_to_goal_dist_end":0.22726,"object_to_goal_dist_start":0.24511,"object_z_max":0.21349,"peak_contact_force":0.12263,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":5740.0,"raw_peak_contact_force":2.09702,"subtask_id":"reach_object","tcp_end":[0.51059,-0.02619,0.23044],"tcp_start":[0.51371,-0.02629,0.17761],"tcp_to_object_dist_end":0.11922,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":701.0,"n_steps_budget":1000.0,"object_pos_end":[0.54661,0.01558,0.01602],"object_pos_start":[0.52631,-0.02613,0.21375],"object_to_goal_dist_end":0.23586,"object_to_goal_dist_start":0.22183,"object_z_max":0.2177,"peak_contact_force":0.12263,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1660.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_object","tcp_end":[0.62427,0.1533,0.31329],"tcp_start":[0.51059,-0.02619,0.23044],"tcp_to_object_dist_end":0.33671,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":201.0,"n_steps_budget":1000.0,"object_pos_end":[0.54661,0.01558,0.01602],"object_pos_start":[0.54661,0.01558,0.01602],"object_to_goal_dist_end":0.23586,"object_to_goal_dist_start":0.23586,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1022.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_object","tcp_end":[0.62824,0.16166,0.19568],"tcp_start":[0.62427,0.1533,0.31329],"tcp_to_object_dist_end":0.24552,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54661,0.01558,0.01602],"object_pos_start":[0.54661,0.01558,0.01602],"object_to_goal_dist_end":0.23586,"object_to_goal_dist_start":0.23586,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1052.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.62252,0.15998,0.21358],"tcp_start":[0.62824,0.16166,0.19568],"tcp_to_object_dist_end":0.25621,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.4629,"average_solve_count":283.0,"average_success_count":283.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.transport_speed":0.13136,"approach_object.approach_arc_height":0.08742,"approach_object.approach_speed":0.08845,"descend_to_grasp.descend_speed":0.06319,"lift.lift_height":0.11671,"lift.lift_speed":0.0523,"pull_up.pull_up_speed":0.02856,"release_object.release_timeout":0.74154},"optimized_scores":{"best_composite_score":0.01803,"best_fitness_score":0.59803,"best_task_score":0.23956},"replay_outcomes":[{"contacts":{"omitted_contact_groups":2,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1455.0,"contact_point_centroid":[0.46195,0.04007,-0.00311],"force_p95":0.50865,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.21099,"mean_force":0.18412,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5383,0.09164,0.30358]},{"body_a":"world","body_b":"grasp_target","contact_count":188.0,"contact_point_centroid":[0.45793,0.00256,-0.00131],"force_p95":0.42142,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.49474,"mean_force":0.11467,"phase_index":3.0,"phase_name":"pull_up","phase_type":"pull","tcp_position_centroid":[0.44959,0.00167,0.03436]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14867.0,"contact_point_centroid":[0.43972,-0.01733,0.19558],"force_p95":0.10784,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29441,"mean_force":0.06102,"phase_index":4.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.43801,0.00156,0.19422]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13500.0,"contact_point_centroid":[0.43982,0.02057,0.19705],"force_p95":0.11265,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27291,"mean_force":0.06607,"phase_index":4.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.43799,0.00156,0.1953]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.46291,0.00017,-0.00217],"force_p95":0.16896,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24587,"mean_force":0.13499,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45233,0.00171,0.03376]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":35.0,"contact_point_centroid":[0.44356,-0.01576,0.35829],"force_p95":0.22326,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24385,"mean_force":0.13494,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.43642,0.00197,0.36549]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8861.0,"contact_point_centroid":[0.44585,-0.01755,0.05432],"force_p95":0.07541,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23376,"mean_force":0.05024,"phase_index":3.0,"phase_name":"pull_up","phase_type":"pull","tcp_position_centroid":[0.44592,0.00164,0.05264]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8979.0,"contact_point_centroid":[0.4457,0.02082,0.05416],"force_p95":0.07349,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23062,"mean_force":0.04914,"phase_index":3.0,"phase_name":"pull_up","phase_type":"pull","tcp_position_centroid":[0.44595,0.00164,0.05254]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":28.0,"contact_point_centroid":[0.44303,0.01895,0.35849],"force_p95":0.17035,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17151,"mean_force":0.0873,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.43598,0.00169,0.36569]},{"body_a":"world","body_b":"grasp_target","contact_count":1060.0,"contact_point_centroid":[0.46286,-7e-05,-0.00188],"force_p95":0.1365,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12309,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48324,0.02785,0.24828]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4783.0,"contact_point_centroid":[0.45122,0.02095,0.03498],"force_p95":0.07139,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13154,"mean_force":0.04507,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45125,0.0017,0.03274]},{"body_a":"world","body_b":"grasp_target","contact_count":1512.0,"contact_point_centroid":[0.46286,-7e-05,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.46051,0.00961,0.11482]},{"body_a":"world","body_b":"grasp_target","contact_count":928.0,"contact_point_centroid":[0.45987,0.04293,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.59852,0.14469,0.20774]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.45987,0.04293,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.59859,0.14826,0.14024]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5538.0,"contact_point_centroid":[0.45073,-0.0176,0.03441],"force_p95":0.06868,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07641,"mean_force":0.04091,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45126,0.0017,0.03274]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1641.0,"contact_point_centroid":[0.53657,0.08978,0.30697],"force_p95":0.01222,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0165,"mean_force":0.01068,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53614,0.08977,0.30478]}],"total_contact_groups":18},"final_pose_error":0.01996,"key_states":{"actual_goal_position":[0.61015,0.15287,0.12219],"final_object_position":[0.45987,0.04293,0.01602],"final_tcp_position":[0.60377,0.1496,0.14082],"realised_goal_position":[0.61015,0.15287,0.12219],"realised_object_initial_position":[0.46286,-7e-05,0.03]},"peak_contact_force":9748.87789,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":266.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.03],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.23148,"object_z_max":0.03,"peak_contact_force":41.31789,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1512.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.46428,0.01725,0.189],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1639,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":378.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.16163,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":12121.0,"raw_peak_contact_force":0.24587,"subtask_id":"reach_object","tcp_end":[0.45898,0.00186,0.04028],"tcp_start":[0.46428,0.01725,0.189],"tcp_to_object_dist_end":0.01491,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46278,0.00143,0.02543],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.23241,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.07499,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":18028.0,"raw_peak_contact_force":0.49474,"tcp_end":[0.45123,0.0017,0.03271],"tcp_start":[0.45898,0.00186,0.04028],"tcp_to_object_dist_end":0.01365,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":427.0,"n_steps_budget":690.0,"object_pos_end":[0.45773,0.00139,0.04543],"object_pos_start":[0.46278,0.00143,0.02543],"object_to_goal_dist_end":0.22819,"object_to_goal_dist_start":0.23241,"object_z_max":0.06463,"peak_contact_force":0.05799,"phase_name":"pull_up","phase_peak_obstacle_force":0.0,"phase_type":"pull","raw_contact_event_count":28367.0,"raw_peak_contact_force":0.29441,"tcp_end":[0.44283,0.00161,0.07465],"tcp_start":[0.44694,0.00165,0.05368],"tcp_to_object_dist_end":0.0328,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":891.0,"n_steps_budget":1000.0,"object_pos_end":[0.44816,0.00168,0.15952],"object_pos_start":[0.45253,0.00146,0.06471],"object_to_goal_dist_end":0.22471,"object_to_goal_dist_start":0.22599,"object_z_max":0.34089,"peak_contact_force":9748.87789,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":3159.0,"raw_peak_contact_force":2.21099,"subtask_id":"reach_object","tcp_end":[0.43557,0.00152,0.36562],"tcp_start":[0.43714,0.00155,0.26872],"tcp_to_object_dist_end":0.20648,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":533.0,"n_steps_budget":1000.0,"object_pos_end":[0.45987,0.04293,0.01602],"object_pos_start":[0.44907,0.00157,0.34072],"object_to_goal_dist_end":0.21434,"object_to_goal_dist_start":0.3108,"object_z_max":0.34072,"peak_contact_force":0.12263,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1910.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_object","tcp_end":[0.59467,0.14033,0.2726],"tcp_start":[0.43557,0.00152,0.36562],"tcp_to_object_dist_end":0.30577,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":232.0,"n_steps_budget":1000.0,"object_pos_end":[0.45987,0.04293,0.01602],"object_pos_start":[0.45987,0.04293,0.01602],"object_to_goal_dist_end":0.21434,"object_to_goal_dist_start":0.21434,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1025.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_object","tcp_end":[0.60377,0.1496,0.14082],"tcp_start":[0.59467,0.14033,0.2726],"tcp_to_object_dist_end":0.21831,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45987,0.04293,0.01602],"object_pos_start":[0.45987,0.04293,0.01602],"object_to_goal_dist_end":0.21434,"object_to_goal_dist_start":0.21434,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1060.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.59686,0.14774,0.16004],"tcp_start":[0.60377,0.1496,0.14082],"tcp_to_object_dist_end":0.2247,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```