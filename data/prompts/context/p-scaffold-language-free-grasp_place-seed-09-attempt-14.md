## Search State

- **Seed**: 9
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 14 | 0.1533 | 1.00 | ❌ rejected |
| 13 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 14 | 0.1535 | 1.00 | ✅ accepted |
| 12 | approach → descend → grasp → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.2650 | 0.54 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 15 | 0.1034 | 1.00 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 15 | 0.1044 | 1.00 | ❌ rejected |

**Proposal policy**: task_score is near-perfect (1.00). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 1.000, which indicates the subtask decomposition is already effective.
> Preserve the current subtask decomposition unless the evidence shows a subtask change is necessary. Prefer refining phases, parameters, control modes, or termination conditions first.
> Unnecessary subtask redesign when performance is already high often causes regression.

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

## Current Skill (Q=0.153) — your mutation base

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
  weight: 0.3
- id: lift_clearance
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.25
- id: approach_goal
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.2
- id: place_goal
  target_entity: object
  metric: goal_progress
  weight: 0.25
phases:
- id: approach_1
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
    - 0.15
    tolerance: 0.05
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
    approach_tolerance:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.05
      binds_to:
      - path: termination.pose_tolerance
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
    tolerance: 0.05
    orientation:
      mode: keep_current
  parameters:
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
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.023
    tolerance: 0.015
    orientation:
      mode: keep_current
  parameters:
    descend_speed_place:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
    place_height:
      type: scalar
      range:
      - 0.0
      - 0.05
      default: 0.023
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
  subtask_id: place_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.15], tolerance=0.05
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - approach_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
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
    - transport_height: status=consumed; consumers=target.offset.z (replace)
    - transport_speed: status=consumed; consumers=generator.speed (replace)
    - transport_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **descend_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.023], tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed_place: status=consumed; consumers=generator.speed (replace)
    - place_height: status=consumed; consumers=target.offset.z (replace)
    - place_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)

## Design Metrics

- **Composite score**: 0.153
- **task_score** (E): 1.000
- **fitness_score**: 0.973  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.820

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1290 |
| descend_1 | 1.00 | 1.00 | 0.1313 |
| grasp_1 | 1.00 | 1.00 | 0.0130 |
| lift_1 | 1.00 | 1.00 | 0.1513 |
| transport_1 | 1.00 | 1.00 | 0.2114 |
| descend_to_place | 1.00 | 1.00 | 0.0894 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.509, -0.011, 0.176) | (0.515, -0.017, 0.030)→(0.515, -0.017, 0.026) | 0.268→0.270 | 1.00 / 4.000 | 0.122 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.509, -0.011, 0.176)→(0.510, -0.016, 0.045) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.510, -0.016, 0.045)→(0.501, -0.016, 0.035) | (0.515, -0.017, 0.026)→(0.515, -0.016, 0.026) | 0.270→0.270 | 1.00 / 41.667 | 0.148 | 0.207 |
| lift_1 | lift | 1.00 / step_budget | (0.501, -0.016, 0.035)→(0.511, -0.016, 0.186) | (0.515, -0.016, 0.026)→(0.521, -0.016, 0.172) | 0.270→0.231 | 1.00 / 34.667 | 0.086 | 0.478 |
| transport_1 | approach | 1.00 / step_budget | (0.511, -0.016, 0.186)→(0.598, 0.147, 0.277) | (0.521, -0.016, 0.172)→(0.609, 0.147, 0.260) | 0.231→0.100 | 1.00 / 31.000 | 75.647 | 0.108 |
| descend_to_place | descend | 1.00 / step_budget | (0.598, 0.147, 0.277)→(0.611, 0.173, 0.193) | (0.609, 0.147, 0.260)→(0.621, 0.173, 0.174) | 0.100→0.011 | 1.00 / 26.667 | 0.117 | 0.310 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.466
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.473
- phase_breakdown.reach_object_approach_score: 0.185
- phase_breakdown.approach_goal_score: 0.284
- phase_breakdown.lift_clearance_score: 0.521
- phase_breakdown.place_goal_score: 0.921
- grasp_place_fitness: 0.976

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.976
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.153
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.320


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.91484,"average_solve_count":411.0,"average_success_count":411.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.15568,"approach_1.approach_tolerance":0.05371,"approach_1.speed":0.05453,"descend_1.descend_height":8e-05,"descend_1.descend_speed":0.03359,"descend_1.descend_tolerance":0.02571,"descend_to_place.descend_speed_place":0.02798,"descend_to_place.place_height":0.01587,"descend_to_place.place_tolerance":0.01862,"lift_1.lift_height":0.17821,"lift_1.lift_speed":0.04545,"transport_1.transport_height":0.09073,"transport_1.transport_speed":0.03408,"transport_1.transport_tolerance":0.08226},"optimized_scores":{"best_composite_score":0.15284,"best_fitness_score":0.97284,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":93.0,"contact_point_centroid":[0.53305,-0.01948,-0.00149],"force_p95":0.47788,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.4957,"mean_force":0.16352,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52095,-0.01998,0.03522]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10009.0,"contact_point_centroid":[0.52622,-0.00084,0.11279],"force_p95":0.08333,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28192,"mean_force":0.05829,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52532,-0.01997,0.11034]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1808.0,"contact_point_centroid":[0.60359,0.21976,0.2523],"force_p95":0.10914,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28127,"mean_force":0.07972,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60018,0.20082,0.25149]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10868.0,"contact_point_centroid":[0.52583,-0.039,0.10844],"force_p95":0.07999,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27481,"mean_force":0.05493,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52497,-0.01996,0.10642]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53707,-0.02108,-0.00212],"force_p95":0.15712,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22521,"mean_force":0.13168,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52314,-0.02002,0.03547]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2021.0,"contact_point_centroid":[0.60378,0.18228,0.2519],"force_p95":0.09541,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16266,"mean_force":0.06834,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60018,0.20079,0.25157]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4077.0,"contact_point_centroid":[0.52316,-0.00078,0.0368],"force_p95":0.08025,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14508,"mean_force":0.05187,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52194,-0.01999,0.0341]},{"body_a":"world","body_b":"grasp_target","contact_count":320.0,"contact_point_centroid":[0.53702,-0.02132,-0.00161],"force_p95":0.13824,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12433,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50904,-0.00487,0.2714]},{"body_a":"world","body_b":"grasp_target","contact_count":1456.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12259,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52465,-0.016,0.1362]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5270.0,"contact_point_centroid":[0.5631,0.05686,0.22457],"force_p95":0.08099,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0995,"mean_force":0.05294,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.5618,0.0758,0.22312]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4428.0,"contact_point_centroid":[0.56315,0.09383,0.22472],"force_p95":0.0896,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09602,"mean_force":0.05987,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.56146,0.07474,0.22266]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4984.0,"contact_point_centroid":[0.52309,-0.03913,0.03589],"force_p95":0.07257,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08231,"mean_force":0.04462,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52194,-0.01999,0.03411]}],"total_contact_groups":12},"final_pose_error":0.01475,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.61578,0.21551,0.21124],"final_tcp_position":[0.60412,0.21553,0.22874],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":226.75201,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":81.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02596],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31675,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12215,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":320.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object_approach","tcp_end":[0.52105,-0.01191,0.231],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.20587,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":364.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02596],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31675,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1456.0,"raw_peak_contact_force":0.12264,"subtask_id":"reach_object_approach","tcp_end":[0.53078,-0.02011,0.04452],"tcp_start":[0.52105,-0.01191,0.231],"tcp_to_object_dist_end":0.01956,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53694,-0.0201,0.0256],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31602,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.15045,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10861.0,"raw_peak_contact_force":0.22521,"tcp_end":[0.52191,-0.01999,0.03407],"tcp_start":[0.53078,-0.02011,0.04452],"tcp_to_object_dist_end":0.01725,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":563.0,"n_steps_budget":1000.0,"object_pos_end":[0.5431,-0.0201,0.17078],"object_pos_start":[0.53694,-0.0201,0.0256],"object_to_goal_dist_end":0.2594,"object_to_goal_dist_start":0.31602,"object_z_max":0.17053,"peak_contact_force":0.07963,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":20970.0,"raw_peak_contact_force":0.4957,"subtask_id":"lift_clearance","tcp_end":[0.53223,-0.02002,0.18455],"tcp_start":[0.52191,-0.01999,0.03407],"tcp_to_object_dist_end":0.01754,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":273.0,"n_steps_budget":1000.0,"object_pos_end":[0.60877,0.18727,0.2561],"object_pos_start":[0.5431,-0.0201,0.17078],"object_to_goal_dist_end":0.06334,"object_to_goal_dist_start":0.2594,"object_z_max":0.25576,"peak_contact_force":226.75201,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9698.0,"raw_peak_contact_force":0.0995,"subtask_id":"approach_goal","tcp_end":[0.59767,0.18751,0.27203],"tcp_start":[0.53223,-0.02002,0.18455],"tcp_to_object_dist_end":0.01942,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":140.0,"n_steps_budget":1000.0,"object_pos_end":[0.61578,0.21551,0.21124],"object_pos_start":[0.60877,0.18727,0.2561],"object_to_goal_dist_end":0.01394,"object_to_goal_dist_start":0.06334,"object_z_max":0.25656,"peak_contact_force":0.10771,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3829.0,"raw_peak_contact_force":0.28127,"subtask_id":"place_goal","tcp_end":[0.60412,0.21553,0.22874],"tcp_start":[0.59767,0.18751,0.27203],"tcp_to_object_dist_end":0.02103,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.9686,"average_solve_count":414.0,"average_success_count":414.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.06086,"approach_1.approach_tolerance":0.03687,"approach_1.speed":0.02255,"descend_1.descend_height":5e-05,"descend_1.descend_speed":0.03236,"descend_1.descend_tolerance":0.02945,"descend_to_place.descend_speed_place":0.0373,"descend_to_place.place_height":0.01364,"descend_to_place.place_tolerance":0.02306,"lift_1.lift_height":0.15512,"lift_1.lift_speed":0.05337,"transport_1.transport_height":0.14979,"transport_1.transport_speed":0.05136,"transport_1.transport_tolerance":0.07999},"optimized_scores":{"best_composite_score":0.15134,"best_fitness_score":0.97134,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":99.0,"contact_point_centroid":[0.54374,-0.02651,-0.00153],"force_p95":0.44144,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.49289,"mean_force":0.10243,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52845,-0.02722,0.03482]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7715.0,"contact_point_centroid":[0.53521,-0.00839,0.09486],"force_p95":0.11223,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36599,"mean_force":0.06647,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53285,-0.02723,0.09321]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8151.0,"contact_point_centroid":[0.53545,-0.04583,0.09464],"force_p95":0.10136,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33805,"mean_force":0.06621,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53288,-0.02723,0.09351]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1881.0,"contact_point_centroid":[0.62721,0.1629,0.25185],"force_p95":0.16688,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29532,"mean_force":0.11112,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62131,0.14425,0.25089]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54574,-0.02894,-0.00218],"force_p95":0.17407,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24851,"mean_force":0.13627,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53078,-0.02729,0.0349]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2423.0,"contact_point_centroid":[0.62729,0.12591,0.2521],"force_p95":0.13444,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22848,"mean_force":0.08688,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62119,0.14397,0.25182]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3988.0,"contact_point_centroid":[0.53133,-0.00821,0.03595],"force_p95":0.09487,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15343,"mean_force":0.05664,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52955,-0.02726,0.0335]},{"body_a":"world","body_b":"grasp_target","contact_count":684.0,"contact_point_centroid":[0.5456,-0.02923,-0.00181],"force_p95":0.13762,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12334,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5146,-0.00945,0.22804]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3373.0,"contact_point_centroid":[0.57831,0.06419,0.21941],"force_p95":0.11037,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13816,"mean_force":0.07846,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.57489,0.04536,0.21844]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4184.0,"contact_point_centroid":[0.57856,0.02817,0.21999],"force_p95":0.09443,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13375,"mean_force":0.06506,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.57552,0.04668,0.21952]},{"body_a":"world","body_b":"grasp_target","contact_count":732.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53399,-0.02449,0.08974]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4671.0,"contact_point_centroid":[0.53142,-0.04631,0.03563],"force_p95":0.08427,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08809,"mean_force":0.04932,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52956,-0.02726,0.03351]}],"total_contact_groups":12},"final_pose_error":0.01494,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.63723,0.15741,0.18017],"final_tcp_position":[0.62671,0.15764,0.20207],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":0.49289,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":172.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":684.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object_approach","tcp_end":[0.5331,-0.02166,0.13811],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11304,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":183.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":732.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object_approach","tcp_end":[0.5385,-0.02746,0.04422],"tcp_start":[0.5331,-0.02166,0.13811],"tcp_to_object_dist_end":0.01962,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54588,-0.02749,0.02535],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.25992,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.16543,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10459.0,"raw_peak_contact_force":0.24851,"tcp_end":[0.52953,-0.02725,0.03346],"tcp_start":[0.5385,-0.02746,0.04422],"tcp_to_object_dist_end":0.01826,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":489.0,"n_steps_budget":1000.0,"object_pos_end":[0.55402,-0.02733,0.14629],"object_pos_start":[0.54588,-0.02749,0.02535],"object_to_goal_dist_end":0.21004,"object_to_goal_dist_start":0.25992,"object_z_max":0.14606,"peak_contact_force":0.10701,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":15965.0,"raw_peak_contact_force":0.49289,"subtask_id":"lift_clearance","tcp_end":[0.54066,-0.02734,0.16138],"tcp_start":[0.52953,-0.02725,0.03346],"tcp_to_object_dist_end":0.02015,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":265.0,"n_steps_budget":1000.0,"object_pos_end":[0.63063,0.13326,0.27386],"object_pos_start":[0.55402,-0.02733,0.14629],"object_to_goal_dist_end":0.102,"object_to_goal_dist_start":0.21004,"object_z_max":0.27334,"peak_contact_force":0.11073,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7557.0,"raw_peak_contact_force":0.13816,"subtask_id":"approach_goal","tcp_end":[0.61802,0.13333,0.29161],"tcp_start":[0.54066,-0.02734,0.16138],"tcp_to_object_dist_end":0.02178,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":17.0,"n_steps":218.0,"n_steps_budget":1000.0,"object_pos_end":[0.63723,0.15741,0.18017],"object_pos_start":[0.63063,0.13326,0.27386],"object_to_goal_dist_end":0.00929,"object_to_goal_dist_start":0.102,"object_z_max":0.27486,"peak_contact_force":0.16549,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4304.0,"raw_peak_contact_force":0.29532,"subtask_id":"place_goal","tcp_end":[0.62671,0.15764,0.20207],"tcp_start":[0.61802,0.13333,0.29161],"tcp_to_object_dist_end":0.0243,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.81352,"average_solve_count":488.0,"average_success_count":488.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.07936,"approach_1.approach_tolerance":0.05502,"approach_1.speed":0.05791,"descend_1.descend_height":0.00013,"descend_1.descend_speed":0.02263,"descend_1.descend_tolerance":0.02558,"descend_to_place.descend_speed_place":0.04503,"descend_to_place.place_height":0.01557,"descend_to_place.place_tolerance":0.02222,"lift_1.lift_height":0.2058,"lift_1.lift_speed":0.03293,"transport_1.transport_height":0.16605,"transport_1.transport_speed":0.01794,"transport_1.transport_tolerance":0.05148},"optimized_scores":{"best_composite_score":0.15558,"best_fitness_score":0.97558,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":88.0,"contact_point_centroid":[0.45917,-0.00015,-0.00147],"force_p95":0.42783,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.44633,"mean_force":0.19477,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.452,-0.00022,0.03865]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5100.0,"contact_point_centroid":[0.59008,0.15259,0.21044],"force_p95":0.08144,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35463,"mean_force":0.06005,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.58928,0.13338,0.20786]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11780.0,"contact_point_centroid":[0.45436,0.01893,0.12585],"force_p95":0.07324,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25031,"mean_force":0.05149,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45416,-0.00022,0.12397]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11780.0,"contact_point_centroid":[0.45439,-0.01936,0.12586],"force_p95":0.07321,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24732,"mean_force":0.05143,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45416,-0.00022,0.12397]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6029.0,"contact_point_centroid":[0.59,0.11437,0.21005],"force_p95":0.07392,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21981,"mean_force":0.05078,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.58924,0.13333,0.20813]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.46284,-9e-05,-0.00202],"force_p95":0.1288,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1461,"mean_force":0.12448,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.454,-0.00019,0.03882]},{"body_a":"world","body_b":"grasp_target","contact_count":556.0,"contact_point_centroid":[0.46286,-7e-05,-0.00177],"force_p95":0.13792,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1235,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4881,-3e-05,0.23567]},{"body_a":"world","body_b":"grasp_target","contact_count":932.0,"contact_point_centroid":[0.46286,-7e-05,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.46571,-9e-05,0.10218]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4864.0,"contact_point_centroid":[0.45312,0.019,0.03969],"force_p95":0.06805,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08912,"mean_force":0.04481,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.45294,-0.0002,0.03781]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4350.0,"contact_point_centroid":[0.51492,0.03676,0.23863],"force_p95":0.07456,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08733,"mean_force":0.04922,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51487,0.05589,0.23655]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4848.0,"contact_point_centroid":[0.45315,-0.01939,0.03971],"force_p95":0.06799,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08703,"mean_force":0.04477,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.45294,-0.0002,0.03781]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4053.0,"contact_point_centroid":[0.51223,0.07218,0.23754],"force_p95":0.07591,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07908,"mean_force":0.05092,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51204,0.05305,0.23525]}],"total_contact_groups":12},"final_pose_error":0.0147,"key_states":{"actual_goal_position":[0.61015,0.15287,0.12219],"final_object_position":[0.60983,0.14716,0.13122],"final_tcp_position":[0.60177,0.14713,0.14839],"realised_goal_position":[0.61015,0.15287,0.12219],"realised_object_initial_position":[0.46286,-7e-05,0.03]},"peak_contact_force":0.44633,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":140.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.03],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.23148,"object_z_max":0.03,"peak_contact_force":0.12264,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":556.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object_approach","tcp_end":[0.47298,-6e-05,0.15787],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13224,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":233.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":932.0,"raw_peak_contact_force":0.12264,"subtask_id":"reach_object_approach","tcp_end":[0.46086,-0.00011,0.04573],"tcp_start":[0.47298,-6e-05,0.15787],"tcp_to_object_dist_end":0.01981,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46275,-0.00017,0.02591],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.23328,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12855,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11512.0,"raw_peak_contact_force":0.1461,"tcp_end":[0.45291,-0.0002,0.03778],"tcp_start":[0.46086,-0.00011,0.04573],"tcp_to_object_dist_end":0.01542,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":589.0,"n_steps_budget":1000.0,"object_pos_end":[0.46609,-0.00018,0.19777],"object_pos_start":[0.46275,-0.00017,0.02591],"object_to_goal_dist_end":0.22336,"object_to_goal_dist_start":0.23328,"object_z_max":0.19749,"peak_contact_force":0.07184,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":23648.0,"raw_peak_contact_force":0.44633,"subtask_id":"lift_clearance","tcp_end":[0.45897,-0.0002,0.21236],"tcp_start":[0.45291,-0.0002,0.03778],"tcp_to_object_dist_end":0.01623,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":212.0,"n_steps_budget":1000.0,"object_pos_end":[0.58723,0.12049,0.25149],"object_pos_start":[0.46609,-0.00018,0.19777],"object_to_goal_dist_end":0.13525,"object_to_goal_dist_start":0.22336,"object_z_max":0.25119,"peak_contact_force":0.07805,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8403.0,"raw_peak_contact_force":0.08733,"subtask_id":"approach_goal","tcp_end":[0.57915,0.12065,0.26637],"tcp_start":[0.45897,-0.0002,0.21236],"tcp_to_object_dist_end":0.01693,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":300.0,"n_steps_budget":1000.0,"object_pos_end":[0.60983,0.14716,0.13122],"object_pos_start":[0.58723,0.12049,0.25149],"object_to_goal_dist_end":0.01069,"object_to_goal_dist_start":0.13525,"object_z_max":0.25184,"peak_contact_force":0.07857,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11129.0,"raw_peak_contact_force":0.35463,"subtask_id":"place_goal","tcp_end":[0.60177,0.14713,0.14839],"tcp_start":[0.57915,0.12065,0.26637],"tcp_to_object_dist_end":0.01897,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```