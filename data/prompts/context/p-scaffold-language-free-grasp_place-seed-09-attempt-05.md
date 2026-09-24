## Search State

- **Seed**: 9
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 15 | -0.2383 | 0.38 | ✅ accepted |
| 4 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 15 | -0.2407 | 0.38 | ✅ accepted |
| 3 | approach → descend → grasp → lift → approach → release | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | time_limit | pose_tolerance | pose_tolerance | time_limit | 9 | 0.0853 | 0.36 | ✅ accepted |
| 2 | approach → descend → grasp → lift → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | force_threshold_switch | admittance_control | position_control | position_control | position_control | pose_tolerance | contact_detected | time_limit | pose_tolerance | pose_tolerance | 4 | 0.3630 | 0.36 | ✅ accepted |
| 1 | approach → descend → grasp → lift → push → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | position_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | time_limit | pose_tolerance | pose_tolerance | time_limit | 5 | 0.0495 | 0.27 | ❌ rejected |

**Proposal policy**: task_score is 0.38 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.238) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_object_approach
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.2
- id: lift_clearance
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.15
- id: approach_goal
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.2
- id: place_descent
  weight: 0.25
- id: place_goal
  target_entity: object
  metric: goal_progress
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
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    arc_height:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
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
  subtask_id: reach_object_approach
- id: descend_1
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
    - 0.02
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    descend_height:
      type: scalar
      range:
      - 0.0
      - 0.06
      default: 0.02
      binds_to:
      - path: target.offset.z
        mode: replace
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
    descend_tolerance:
      type: scalar
      range:
      - 0.01
      - 0.04
      default: 0.02
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: reach_object_approach
- id: grasp_1
  type: grasp
  control: position_control
  termination: time_limit
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
  guards:
  - id: check_grasp
    when: after_phase
    predicate: bilateral_grasp
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: repeat
- id: lift_1
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.02
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
    lift_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: lift_clearance
- id: transport_1
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.05
    orientation:
      mode: keep_current
  parameters:
    transport_arc:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.06
      binds_to:
      - path: generator.arc_height
        mode: replace
    transport_height:
      type: scalar
      range:
      - 0.05
      - 0.25
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    transport_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    transport_tolerance:
      type: scalar
      range:
      - 0.03
      - 0.1
      default: 0.05
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: approach_goal
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
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    descend_speed_place:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
    place_height:
      type: scalar
      range:
      - -0.02
      - 0.05
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: replace
    place_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.03
      default: 0.015
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: place_descent
- id: release_1
  type: release
  control: position_control
  termination: time_limit
  end_effector_action: open
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
  subtask_id: place_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.02], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_height: status=consumed; consumers=target.offset.z (replace)
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - descend_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none
  - guards:
    - id=check_grasp, when=after_phase, predicate=bilateral_grasp, on_failure=retry
  - retries: max_attempts=2, strategy=repeat
- **lift_1** (`lift`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
- **transport_1** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.05
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_arc: status=consumed; consumers=generator.arc_height (replace)
    - transport_height: status=consumed; consumers=target.offset.z (replace)
    - transport_speed: status=consumed; consumers=generator.speed (replace)
    - transport_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **descend_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed_place: status=consumed; consumers=generator.speed (replace)
    - place_height: status=consumed; consumers=target.offset.z (replace)
    - place_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **release_1** (`release`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: -0.238
- **task_score** (E): 0.383
- **fitness_score**: 0.662  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.900

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0948 |
| descend_1 | 1.00 | 1.00 | 0.1693 |
| grasp_1 | 1.00 | 1.00 | 0.0130 |
| lift_1 | 1.00 | 1.00 | 0.1236 |
| transport_1 | 1.00 | 0.67 | 0.2529 |
| descend_to_place | 1.00 | 0.67 | 0.1430 |
| release_1 | 1.00 | 1.00 | 0.0197 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.515, -0.011, 0.218) | (0.515, -0.017, 0.030)→(0.515, -0.017, 0.026) | 0.268→0.270 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.515, -0.011, 0.218)→(0.511, -0.016, 0.049) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.511, -0.016, 0.049)→(0.502, -0.016, 0.039) | (0.515, -0.017, 0.026)→(0.515, -0.016, 0.026) | 0.270→0.270 | 1.00 / 41.667 | 0.149 | 0.193 |
| lift_1 | lift | 1.00 / step_budget | (0.502, -0.016, 0.039)→(0.510, -0.016, 0.162) | (0.515, -0.016, 0.026)→(0.522, -0.016, 0.144) | 0.270→0.227 | 1.00 / 32.000 | 0.090 | 0.476 |
| transport_1 | approach | 1.00 / step_budget | (0.510, -0.016, 0.162)→(0.596, 0.140, 0.333) | (0.522, -0.016, 0.144)→(0.613, 0.134, 0.254) | 0.227→0.144 | 0.67 / 16.333 | 0.067 | 0.178 |
| descend_to_place | descend | 1.00 / step_budget | (0.596, 0.140, 0.333)→(0.611, 0.174, 0.195) | (0.613, 0.134, 0.254)→(0.628, 0.166, 0.099) | 0.144→0.074 | 0.67 / 11.333 | 0.073 | 1.183 |
| release_1 | release | 1.00 / step_budget | (0.611, 0.174, 0.195)→(0.606, 0.172, 0.214) | (0.628, 0.166, 0.099)→(0.627, 0.167, 0.020) | 0.074→0.150 | 1.00 / 3.333 | 0.145 | 1.088 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.534
- phase_score: 0.320
- phase_breakdown.lift_clearance_score: 0.439
- phase_breakdown.reach_object_approach_score: 0.214
- phase_breakdown.approach_goal_score: 0.201
- phase_breakdown.place_descent_score: 0.685
- phase_breakdown.place_goal_score: 0.000
- grasp_place_fitness: 0.733

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.733
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.534
- **Median Q (composite search score)**: -0.257
- **K-run variance**: 0.0027
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Parameters at lower bound**: descend_1.descend_height
- **Final σ (mean)**: 0.295


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.18033,"average_solve_count":366.0,"average_success_count":366.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.14348,"approach_1.arc_height":0.07321,"approach_1.speed":0.05741,"descend_1.descend_height":0.0,"descend_1.descend_speed":0.04064,"descend_1.descend_tolerance":0.03018,"descend_to_place.descend_speed_place":0.03983,"descend_to_place.place_height":0.0103,"descend_to_place.place_tolerance":0.01765,"lift_1.lift_height":0.20003,"lift_1.lift_speed":0.06353,"transport_1.transport_arc":0.08367,"transport_1.transport_height":0.11464,"transport_1.transport_speed":0.04865,"transport_1.transport_tolerance":0.04552},"optimized_scores":{"best_composite_score":-0.29,"best_fitness_score":0.61,"best_task_score":0.27295},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":658.0,"contact_point_centroid":[0.63153,0.19868,-0.00472],"force_p95":0.98741,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.5103,"mean_force":0.22346,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60085,0.20125,0.27491]},{"body_a":"world","body_b":"grasp_target","contact_count":96.0,"contact_point_centroid":[0.53436,-0.0173,-0.00162],"force_p95":0.44635,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5292,"mean_force":0.11472,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52178,-0.01798,0.03579]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8412.0,"contact_point_centroid":[0.52825,0.00082,0.11446],"force_p95":0.11208,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3342,"mean_force":0.07503,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52515,-0.01815,0.11211]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10015.0,"contact_point_centroid":[0.5277,-0.03686,0.11156],"force_p95":0.10332,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31191,"mean_force":0.06572,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52501,-0.01814,0.11006]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53716,-0.02086,-0.00229],"force_p95":0.2058,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.27906,"mean_force":0.14403,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52416,-0.01802,0.0356]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1867.0,"contact_point_centroid":[0.54849,0.03381,0.26851],"force_p95":0.17625,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24213,"mean_force":0.10837,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54274,0.0152,0.26793]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2543.0,"contact_point_centroid":[0.54906,-0.00067,0.26945],"force_p95":0.1478,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20148,"mean_force":0.08692,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54348,0.0175,0.26951]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3579.0,"contact_point_centroid":[0.5247,0.00121,0.03738],"force_p95":0.09318,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16877,"mean_force":0.05795,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52295,-0.018,0.03424]},{"body_a":"world","body_b":"grasp_target","contact_count":1456.0,"contact_point_centroid":[0.53702,-0.02132,-0.00191],"force_p95":0.13511,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12296,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51538,0.02852,0.23449]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.63161,0.19857,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12272,"mean_force":0.12261,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60145,0.21571,0.23243]},{"body_a":"world","body_b":"grasp_target","contact_count":1032.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53089,-0.00992,0.10977]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4951.0,"contact_point_centroid":[0.52413,-0.03729,0.03612],"force_p95":0.08269,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08855,"mean_force":0.04633,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52297,-0.018,0.03425]},{"body_a":"left_finger","body_b":"right_finger","contact_count":639.0,"contact_point_centroid":[0.60168,0.20252,0.27352],"force_p95":0.0133,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01571,"mean_force":0.01087,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60121,0.2025,0.27122]},{"body_a":"left_finger","body_b":"right_finger","contact_count":223.0,"contact_point_centroid":[0.60397,0.21674,0.23065],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01101,"mean_force":0.01004,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60338,0.21671,0.22865]}],"total_contact_groups":14},"final_pose_error":0.01975,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.63161,0.19857,0.01602],"final_tcp_position":[0.60505,0.21687,0.23333],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":2.5103,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":365.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1456.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object_approach","tcp_end":[0.53193,-0.00222,0.17194],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14725,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":258.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1032.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object_approach","tcp_end":[0.53182,-0.01802,0.04469],"tcp_start":[0.53193,-0.00222,0.17194],"tcp_to_object_dist_end":0.01966,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53699,-0.0185,0.02505],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31508,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.18877,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10330.0,"raw_peak_contact_force":0.27906,"tcp_end":[0.52293,-0.01799,0.0342],"tcp_start":[0.53182,-0.01802,0.04469],"tcp_to_object_dist_end":0.01679,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":618.0,"n_steps_budget":1000.0,"object_pos_end":[0.5476,-0.01851,0.18841],"object_pos_start":[0.53699,-0.0185,0.02505],"object_to_goal_dist_end":0.25483,"object_to_goal_dist_start":0.31508,"object_z_max":0.18816,"peak_contact_force":0.10769,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":18523.0,"raw_peak_contact_force":0.5292,"subtask_id":"lift_clearance","tcp_end":[0.53257,-0.0184,0.20585],"tcp_start":[0.52293,-0.01799,0.0342],"tcp_to_object_dist_end":0.02302,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":315.0,"n_steps_budget":1000.0,"object_pos_end":[0.6177,0.16368,0.13689],"object_pos_start":[0.5476,-0.01851,0.18841],"object_to_goal_dist_end":0.09557,"object_to_goal_dist_start":0.25483,"object_z_max":0.31129,"peak_contact_force":0.0,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4410.0,"raw_peak_contact_force":0.24213,"subtask_id":"approach_goal","tcp_end":[0.5968,0.18127,0.33261],"tcp_start":[0.53257,-0.0184,0.20585],"tcp_to_object_dist_end":0.19762,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":197.0,"n_steps_budget":1000.0,"object_pos_end":[0.6316,0.19856,0.01601],"object_pos_start":[0.6177,0.16368,0.13689],"object_to_goal_dist_end":0.19478,"object_to_goal_dist_start":0.09557,"object_z_max":0.13689,"peak_contact_force":0.12273,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1297.0,"raw_peak_contact_force":2.5103,"subtask_id":"place_descent","tcp_end":[0.60505,0.21687,0.23333],"tcp_start":[0.5968,0.18127,0.33261],"tcp_to_object_dist_end":0.2197,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.63161,0.19857,0.01602],"object_pos_start":[0.6316,0.19856,0.01601],"object_to_goal_dist_end":0.19477,"object_to_goal_dist_start":0.19478,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1023.0,"raw_peak_contact_force":0.12272,"subtask_id":"place_goal","tcp_end":[0.60034,0.21514,0.25191],"tcp_start":[0.60505,0.21687,0.23333],"tcp_to_object_dist_end":0.23853,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.10905,"average_solve_count":431.0,"average_success_count":431.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.16551,"approach_1.arc_height":0.03251,"approach_1.speed":0.04212,"descend_1.descend_height":0.00332,"descend_1.descend_speed":0.03067,"descend_1.descend_tolerance":0.02244,"descend_to_place.descend_speed_place":0.04432,"descend_to_place.place_height":0.01976,"descend_to_place.place_tolerance":0.01713,"lift_1.lift_height":0.13511,"lift_1.lift_speed":0.05288,"transport_1.transport_arc":0.0747,"transport_1.transport_height":0.22132,"transport_1.transport_speed":0.05719,"transport_1.transport_tolerance":0.05252},"optimized_scores":{"best_composite_score":-0.25747,"best_fitness_score":0.64253,"best_task_score":0.3409},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":574.0,"contact_point_centroid":[0.64395,0.15891,-0.00406],"force_p95":0.83829,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.04354,"mean_force":0.21129,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62257,0.15666,0.21441]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2337.0,"contact_point_centroid":[0.62521,0.15471,0.3153],"force_p95":0.19207,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.55958,"mean_force":0.11751,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61923,0.13609,0.31545]},{"body_a":"world","body_b":"grasp_target","contact_count":92.0,"contact_point_centroid":[0.54333,-0.02895,-0.00138],"force_p95":0.43627,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.48823,"mean_force":0.10693,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53128,-0.02907,0.0389]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3179.0,"contact_point_centroid":[0.62547,0.11887,0.31093],"force_p95":0.14505,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32889,"mean_force":0.08697,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61951,0.13683,0.31175]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7340.0,"contact_point_centroid":[0.53513,-0.0098,0.09148],"force_p95":0.08067,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2988,"mean_force":0.05717,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53445,-0.02891,0.08902]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7678.0,"contact_point_centroid":[0.53499,-0.04798,0.08981],"force_p95":0.07906,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2794,"mean_force":0.05527,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53432,-0.02891,0.08769]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5384.0,"contact_point_centroid":[0.55974,0.02719,0.26191],"force_p95":0.10472,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14884,"mean_force":0.06743,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55753,0.00817,0.25982]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54559,-0.02913,-0.00202],"force_p95":0.1297,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1466,"mean_force":0.12496,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53356,-0.02915,0.03925]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6238.0,"contact_point_centroid":[0.56056,-0.00883,0.26484],"force_p95":0.09424,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14243,"mean_force":0.06073,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55845,0.01001,0.26348]},{"body_a":"world","body_b":"grasp_target","contact_count":992.0,"contact_point_centroid":[0.5456,-0.02923,-0.00187],"force_p95":0.13691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12312,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52954,-0.02003,0.26755]},{"body_a":"world","body_b":"grasp_target","contact_count":1296.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.54294,-0.03051,0.13324]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4129.0,"contact_point_centroid":[0.53292,-0.00991,0.04061],"force_p95":0.07602,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09762,"mean_force":0.05168,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53235,-0.02912,0.03784]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4864.0,"contact_point_centroid":[0.53296,-0.04819,0.03965],"force_p95":0.068,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08978,"mean_force":0.04476,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53235,-0.02912,0.03784]}],"total_contact_groups":13},"final_pose_error":0.01951,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.64397,0.15879,0.01599],"final_tcp_position":[0.62745,0.15791,0.21407],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":2.04354,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":249.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":992.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object_approach","tcp_end":[0.5465,-0.03166,0.21484],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.18884,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":324.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1296.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object_approach","tcp_end":[0.54134,-0.02941,0.04876],"tcp_start":[0.5465,-0.03166,0.21484],"tcp_to_object_dist_end":0.02314,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54549,-0.02896,0.02589],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26084,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12929,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10793.0,"raw_peak_contact_force":0.1466,"tcp_end":[0.53231,-0.02911,0.0378],"tcp_start":[0.54134,-0.02941,0.04876],"tcp_to_object_dist_end":0.01776,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":400.0,"n_steps_budget":1000.0,"object_pos_end":[0.55108,-0.02883,0.12645],"object_pos_start":[0.54549,-0.02896,0.02589],"object_to_goal_dist_end":0.21628,"object_to_goal_dist_start":0.26084,"object_z_max":0.12621,"peak_contact_force":0.08059,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":15110.0,"raw_peak_contact_force":0.48823,"subtask_id":"lift_clearance","tcp_end":[0.54014,-0.02884,0.14197],"tcp_start":[0.53231,-0.02911,0.0378],"tcp_to_object_dist_end":0.01899,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":365.0,"n_steps_budget":1000.0,"object_pos_end":[0.62988,0.12214,0.36183],"object_pos_start":[0.55108,-0.02883,0.12645],"object_to_goal_dist_end":0.18982,"object_to_goal_dist_start":0.21628,"object_z_max":0.36161,"peak_contact_force":0.108,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":11622.0,"raw_peak_contact_force":0.14884,"subtask_id":"approach_goal","tcp_end":[0.61463,0.12228,0.38012],"tcp_start":[0.54014,-0.02884,0.14197],"tcp_to_object_dist_end":0.02381,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":309.0,"n_steps_budget":1000.0,"object_pos_end":[0.63817,0.15238,0.1704],"object_pos_start":[0.62988,0.12214,0.36183],"object_to_goal_dist_end":0.01512,"object_to_goal_dist_start":0.18982,"object_z_max":0.36193,"peak_contact_force":0.0,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5516.0,"raw_peak_contact_force":0.55958,"subtask_id":"place_descent","tcp_end":[0.62745,0.15791,0.21407],"tcp_start":[0.61463,0.12228,0.38012],"tcp_to_object_dist_end":0.04531,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.64397,0.15879,0.01599],"object_pos_start":[0.63817,0.15238,0.1704],"object_to_goal_dist_end":0.16143,"object_to_goal_dist_start":0.01512,"object_z_max":0.1704,"peak_contact_force":0.12337,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":574.0,"raw_peak_contact_force":2.04354,"subtask_id":"place_goal","tcp_end":[0.62212,0.1565,0.2323],"tcp_start":[0.62745,0.15791,0.21407],"tcp_to_object_dist_end":0.21742,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.76035,"average_solve_count":459.0,"average_success_count":459.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.21706,"approach_1.arc_height":0.05902,"approach_1.speed":0.01334,"descend_1.descend_height":0.00749,"descend_1.descend_speed":0.02767,"descend_1.descend_tolerance":0.02185,"descend_to_place.descend_speed_place":0.04538,"descend_to_place.place_height":-0.00127,"descend_to_place.place_tolerance":0.02265,"lift_1.lift_height":0.13248,"lift_1.lift_speed":0.05533,"transport_1.transport_arc":0.06854,"transport_1.transport_height":0.16557,"transport_1.transport_speed":0.03798,"transport_1.transport_tolerance":0.07682},"optimized_scores":{"best_composite_score":-0.16738,"best_fitness_score":0.73262,"best_task_score":0.53429},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":160.0,"contact_point_centroid":[0.599,0.14514,-0.00729],"force_p95":0.99862,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.09766,"mean_force":0.42491,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59446,0.14478,0.14551]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3975.0,"contact_point_centroid":[0.59324,0.1498,0.21523],"force_p95":0.1197,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.4803,"mean_force":0.07838,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.5874,0.13108,0.21392]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":779.0,"contact_point_centroid":[0.60478,0.12729,0.13303],"force_p95":0.11424,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.41401,"mean_force":0.07217,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5987,0.14603,0.13259]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":786.0,"contact_point_centroid":[0.60467,0.16488,0.13281],"force_p95":0.11755,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.41294,"mean_force":0.07352,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59869,0.14602,0.13257]},{"body_a":"world","body_b":"grasp_target","contact_count":79.0,"contact_point_centroid":[0.46056,-0.00027,-0.00138],"force_p95":0.36267,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.41051,"mean_force":0.10963,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4507,-0.00021,0.04626]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3662.0,"contact_point_centroid":[0.59379,0.11297,0.21139],"force_p95":0.12123,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37731,"mean_force":0.08106,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.58798,0.13173,0.21053]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6705.0,"contact_point_centroid":[0.45332,0.01896,0.09296],"force_p95":0.07599,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26505,"mean_force":0.05186,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45313,-0.00017,0.09067]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6187.0,"contact_point_centroid":[0.45308,-0.01936,0.09135],"force_p95":0.08145,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24529,"mean_force":0.05572,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.453,-0.00018,0.08914]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.46285,-6e-05,-0.00202],"force_p95":0.12938,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15261,"mean_force":0.12456,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.45258,-0.00018,0.04618]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5344.0,"contact_point_centroid":[0.4956,0.05532,0.22465],"force_p95":0.08518,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1429,"mean_force":0.05412,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.49407,0.03634,0.2223]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4810.0,"contact_point_centroid":[0.49654,0.01876,0.22745],"force_p95":0.09306,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14066,"mean_force":0.06028,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.49566,0.03787,0.22527]},{"body_a":"world","body_b":"grasp_target","contact_count":480.0,"contact_point_centroid":[0.46286,-7e-05,-0.00174],"force_p95":0.13798,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12365,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48225,-5e-05,0.28836]},{"body_a":"world","body_b":"grasp_target","contact_count":1744.0,"contact_point_centroid":[0.46286,-7e-05,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.46149,-8e-05,0.16057]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5263.0,"contact_point_centroid":[0.4509,-0.01941,0.04704],"force_p95":0.06407,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08331,"mean_force":0.04182,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.45153,-0.00019,0.04517]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5095.0,"contact_point_centroid":[0.45094,0.01905,0.04764],"force_p95":0.06584,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08212,"mean_force":0.04301,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.45153,-0.00019,0.04517]}],"total_contact_groups":15},"final_pose_error":0.02,"key_states":{"actual_goal_position":[0.61015,0.15287,0.12219],"final_object_position":[0.60609,0.14454,0.02862],"final_tcp_position":[0.6013,0.14647,0.13767],"realised_goal_position":[0.61015,0.15287,0.12219],"realised_object_initial_position":[0.46286,-7e-05,0.03]},"peak_contact_force":1.09766,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":121.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.03],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.23148,"object_z_max":0.03,"peak_contact_force":0.12254,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":480.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object_approach","tcp_end":[0.46536,-6e-05,0.26647],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.24046,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":436.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1744.0,"raw_peak_contact_force":0.12264,"subtask_id":"reach_object_approach","tcp_end":[0.45936,-0.00011,0.05309],"tcp_start":[0.46536,-6e-05,0.26647],"tcp_to_object_dist_end":0.0273,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46277,-7e-05,0.02591],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.2332,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12903,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12158.0,"raw_peak_contact_force":0.15261,"tcp_end":[0.4515,-0.0002,0.04514],"tcp_start":[0.45936,-0.00011,0.05309],"tcp_to_object_dist_end":0.02229,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":318.0,"n_steps_budget":1000.0,"object_pos_end":[0.46695,-0.0002,0.11792],"object_pos_start":[0.46277,-7e-05,0.02591],"object_to_goal_dist_end":0.20965,"object_to_goal_dist_start":0.2332,"object_z_max":0.11764,"peak_contact_force":0.08298,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":12971.0,"raw_peak_contact_force":0.41051,"subtask_id":"lift_clearance","tcp_end":[0.45777,-0.00011,0.1392],"tcp_start":[0.4515,-0.0002,0.04514],"tcp_to_object_dist_end":0.02318,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":282.0,"n_steps_budget":1000.0,"object_pos_end":[0.59101,0.11677,0.26245],"object_pos_start":[0.46695,-0.0002,0.11792],"object_to_goal_dist_end":0.1461,"object_to_goal_dist_start":0.20965,"object_z_max":0.26275,"peak_contact_force":0.09445,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":10154.0,"raw_peak_contact_force":0.1429,"subtask_id":"approach_goal","tcp_end":[0.57624,0.11729,0.28566],"tcp_start":[0.45777,-0.00011,0.1392],"tcp_to_object_dist_end":0.02751,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":293.0,"n_steps_budget":1000.0,"object_pos_end":[0.61287,0.14652,0.11048],"object_pos_start":[0.59101,0.11677,0.26245],"object_to_goal_dist_end":0.01359,"object_to_goal_dist_start":0.1461,"object_z_max":0.26245,"peak_contact_force":0.09507,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7637.0,"raw_peak_contact_force":0.4803,"subtask_id":"place_descent","tcp_end":[0.6013,0.14647,0.13767],"tcp_start":[0.57624,0.11729,0.28566],"tcp_to_object_dist_end":0.02955,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60609,0.14454,0.02862],"object_pos_start":[0.61287,0.14652,0.11048],"object_to_goal_dist_end":0.09402,"object_to_goal_dist_start":0.01359,"object_z_max":0.11048,"peak_contact_force":0.18868,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1725.0,"raw_peak_contact_force":1.09766,"subtask_id":"place_goal","tcp_end":[0.59435,0.14475,0.15724],"tcp_start":[0.6013,0.14647,0.13767],"tcp_to_object_dist_end":0.12916,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```