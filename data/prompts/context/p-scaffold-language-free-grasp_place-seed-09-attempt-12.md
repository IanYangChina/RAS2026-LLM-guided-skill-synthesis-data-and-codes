## Search State

- **Seed**: 9
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → grasp → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.2650 | 0.54 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 15 | 0.1034 | 1.00 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 15 | 0.1044 | 1.00 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 15 | 0.1049 | 1.00 | ✅ accepted |
| 8 | approach → descend → grasp → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 15 | 0.1037 | 1.00 | ❌ rejected |

**Proposal policy**: task_score is 0.54 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.265) — your mutation base

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

## Design Metrics

- **Composite score**: 0.265
- **task_score** (E): 0.543
- **fitness_score**: 0.735  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.470

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 0.00 | 1.00 | 0.0588 |
| descend_1 | 1.00 | 1.00 | 0.1946 |
| grasp_1 | 1.00 | 1.00 | 0.0143 |
| lift_1 | 1.00 | 1.00 | 0.1176 |
| transport_1 | 0.00 | 0.33 | 0.1926 |
| descend_to_place | 1.00 | 1.00 | 0.1312 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, 0.009, 0.247) | (0.515, -0.017, 0.030)→(0.515, -0.017, 0.026) | 0.268→0.270 | 1.00 / 4.000 | 28.562 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.510, 0.009, 0.247)→(0.511, -0.013, 0.054) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 4.000 | 0.123 | 0.126 |
| grasp_1 | grasp | 1.00 / step_budget | (0.511, -0.013, 0.054)→(0.502, -0.013, 0.044) | (0.515, -0.017, 0.026)→(0.515, -0.014, 0.025) | 0.270→0.269 | 1.00 / 41.333 | 0.225 | 0.271 |
| lift_1 | lift | 1.00 / step_budget | (0.502, -0.013, 0.044)→(0.510, -0.014, 0.161) | (0.515, -0.014, 0.025)→(0.527, -0.015, 0.138) | 0.269→0.225 | 1.00 / 24.667 | 0.129 | 0.453 |
| transport_1 | approach | 0.00 / step_budget | (0.510, -0.014, 0.161)→(0.580, 0.097, 0.298) | (0.527, -0.015, 0.138)→(0.593, 0.080, 0.234) | 0.225→0.130 | 0.33 / 7.000 | 0.040 | 0.312 |
| descend_to_place | descend | 1.00 / step_budget | (0.580, 0.097, 0.298)→(0.607, 0.163, 0.189) | (0.593, 0.080, 0.234)→(0.637, 0.162, 0.053) | 0.130→0.123 | 1.00 / 14.000 | 3249.652 | 1.608 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.143
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.465
- phase_breakdown.reach_object_approach_score: 0.223
- phase_breakdown.approach_goal_score: 0.159
- phase_breakdown.lift_clearance_score: 0.599
- phase_breakdown.place_goal_score: 0.868
- grasp_place_fitness: 0.965

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.965
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.172
- **K-run variance**: 0.0269
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.335


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.93802,"average_solve_count":242.0,"average_success_count":242.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.17455,"approach_1.arc_height":0.09134,"approach_1.speed":0.09383,"lift_1.lift_height":0.1742,"transport_1.transport_arc":0.10022,"transport_1.transport_height":0.15592,"transport_1.transport_speed":0.06543},"optimized_scores":{"best_composite_score":0.12749,"best_fitness_score":0.59749,"best_task_score":0.26882},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":292.0,"contact_point_centroid":[0.66128,0.21837,-0.00688],"force_p95":1.76446,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.34087,"mean_force":0.41506,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59996,0.18732,0.26048]},{"body_a":"world","body_b":"grasp_target","contact_count":73.0,"contact_point_centroid":[0.53582,-0.01846,-0.00174],"force_p95":0.36468,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.46753,"mean_force":0.11134,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51994,-0.01766,0.04413]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":832.0,"contact_point_centroid":[0.54345,-0.02389,0.22564],"force_p95":0.24336,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35453,"mean_force":0.13871,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53713,-0.00531,0.2258]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3164.0,"contact_point_centroid":[0.5278,-0.03692,0.09732],"force_p95":0.14286,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33408,"mean_force":0.09212,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52368,-0.01806,0.09511]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3646.0,"contact_point_centroid":[0.52817,0.00051,0.10048],"force_p95":0.12325,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27177,"mean_force":0.08157,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52403,-0.01809,0.09858]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53721,-0.02108,-0.00229],"force_p95":0.26339,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2681,"mean_force":0.17509,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52227,-0.01768,0.04402]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":963.0,"contact_point_centroid":[0.54162,0.00882,0.21501],"force_p95":0.19744,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25839,"mean_force":0.11601,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53525,-0.00914,0.21471]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4674.0,"contact_point_centroid":[0.52248,0.0014,0.04567],"force_p95":0.08794,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17348,"mean_force":0.05551,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52111,-0.01766,0.04271]},{"body_a":"world","body_b":"grasp_target","contact_count":184.0,"contact_point_centroid":[0.53702,-0.02132,-0.00128],"force_p95":0.13839,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12438,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50787,0.0036,0.28252]},{"body_a":"world","body_b":"grasp_target","contact_count":1080.0,"contact_point_centroid":[0.53702,-0.02132,-0.002],"force_p95":0.12432,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12867,"mean_force":0.12278,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52364,-0.0076,0.1534]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4676.0,"contact_point_centroid":[0.52309,-0.03714,0.04447],"force_p95":0.09817,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10812,"mean_force":0.06168,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52113,-0.01766,0.04273]},{"body_a":"left_finger","body_b":"right_finger","contact_count":474.0,"contact_point_centroid":[0.60009,0.18541,0.26579],"force_p95":0.01432,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01576,"mean_force":0.011,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59956,0.18539,0.26353]}],"total_contact_groups":12},"final_pose_error":0.02983,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.65229,0.21333,0.01542],"final_tcp_position":[0.60411,0.20743,0.22834],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":85.43521,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":47.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02591],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31678,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":85.43521,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":184.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object_approach","tcp_end":[0.51779,0.00253,0.25549],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.23162,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":270.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02591],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31678,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1080.0,"raw_peak_contact_force":0.12867,"subtask_id":"reach_object_approach","tcp_end":[0.5306,-0.01768,0.05436],"tcp_start":[0.51779,0.00253,0.25549],"tcp_to_object_dist_end":0.02928,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53722,-0.01891,0.02499],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31538,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.23801,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11150.0,"raw_peak_contact_force":0.2681,"tcp_end":[0.52108,-0.01766,0.04268],"tcp_start":[0.5306,-0.01768,0.05436],"tcp_to_object_dist_end":0.02397,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":265.0,"n_steps_budget":990.0,"object_pos_end":[0.55019,-0.0198,0.14746],"object_pos_start":[0.53722,-0.01891,0.02499],"object_to_goal_dist_end":0.26171,"object_to_goal_dist_start":0.31538,"object_z_max":0.14702,"peak_contact_force":0.14374,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":6883.0,"raw_peak_contact_force":0.46753,"subtask_id":"lift_clearance","tcp_end":[0.53153,-0.01867,0.17006],"tcp_start":[0.52108,-0.01766,0.04268],"tcp_to_object_dist_end":0.02933,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":157.0,"n_steps_budget":1000.0,"object_pos_end":[0.60985,0.10333,0.26398],"object_pos_start":[0.55019,-0.0198,0.14746],"object_to_goal_dist_end":0.13668,"object_to_goal_dist_start":0.26171,"object_z_max":0.2869,"peak_contact_force":0.0,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1795.0,"raw_peak_contact_force":0.35453,"subtask_id":"approach_goal","tcp_end":[0.58923,0.13145,0.35229],"tcp_start":[0.53153,-0.01867,0.17006],"tcp_to_object_dist_end":0.09494,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":194.0,"n_steps_budget":1000.0,"object_pos_end":[0.65229,0.21333,0.01542],"object_pos_start":[0.60985,0.10333,0.26398],"object_to_goal_dist_end":0.19706,"object_to_goal_dist_start":0.13668,"object_z_max":0.26398,"peak_contact_force":0.17942,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":766.0,"raw_peak_contact_force":2.34087,"subtask_id":"place_goal","tcp_end":[0.60411,0.20743,0.22834],"tcp_start":[0.58923,0.13145,0.35229],"tcp_to_object_dist_end":0.21839,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.92147,"average_solve_count":191.0,"average_success_count":191.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.15465,"approach_1.arc_height":0.09189,"approach_1.speed":0.08645,"lift_1.lift_height":0.16207,"transport_1.transport_arc":0.08755,"transport_1.transport_height":0.13539,"transport_1.transport_speed":0.09997},"optimized_scores":{"best_composite_score":0.17212,"best_fitness_score":0.64212,"best_task_score":0.35896},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":369.0,"contact_point_centroid":[0.64883,0.13684,-0.00536],"force_p95":1.08368,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.95101,"mean_force":0.26403,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61561,0.12515,0.22201]},{"body_a":"world","body_b":"grasp_target","contact_count":77.0,"contact_point_centroid":[0.54444,-0.02437,-0.00197],"force_p95":0.36221,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.45867,"mean_force":0.10429,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52819,-0.02322,0.04373]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":362.0,"contact_point_centroid":[0.54731,-0.03992,0.18038],"force_p95":0.32499,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.43463,"mean_force":0.17836,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54073,-0.02138,0.18037]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":522.0,"contact_point_centroid":[0.54901,-0.00199,0.18491],"force_p95":0.26665,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3678,"mean_force":0.15268,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54201,-0.01963,0.18513]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2875.0,"contact_point_centroid":[0.53694,-0.04277,0.09237],"force_p95":0.14442,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33361,"mean_force":0.09541,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53214,-0.02392,0.09118]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54591,-0.0288,-0.00244],"force_p95":0.28273,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.30555,"mean_force":0.18314,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53054,-0.02325,0.04342]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3207.0,"contact_point_centroid":[0.5364,-0.0052,0.09258],"force_p95":0.12842,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28535,"mean_force":0.08426,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53208,-0.02391,0.09023]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4603.0,"contact_point_centroid":[0.53097,-0.00419,0.04443],"force_p95":0.09806,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18205,"mean_force":0.05851,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52935,-0.02322,0.04206]},{"body_a":"world","body_b":"grasp_target","contact_count":280.0,"contact_point_centroid":[0.5456,-0.02923,-0.00155],"force_p95":0.13832,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12461,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5127,0.00866,0.26984]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4480.0,"contact_point_centroid":[0.53188,-0.04306,0.04328],"force_p95":0.1113,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12459,"mean_force":0.06506,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52939,-0.02322,0.0421]},{"body_a":"world","body_b":"grasp_target","contact_count":952.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12256,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53248,-0.00881,0.14066]},{"body_a":"left_finger","body_b":"right_finger","contact_count":373.0,"contact_point_centroid":[0.61608,0.12586,0.22321],"force_p95":0.01478,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01635,"mean_force":0.01133,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61587,0.12585,0.22096]}],"total_contact_groups":12},"final_pose_error":0.0294,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.64914,0.13738,0.02661],"final_tcp_position":[0.62268,0.1442,0.19513],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":9748.68065,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":71.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02591],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26098,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12273,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":280.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object_approach","tcp_end":[0.52745,0.00574,0.22918],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.20706,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":238.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02591],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26098,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":952.0,"raw_peak_contact_force":0.12264,"subtask_id":"reach_object_approach","tcp_end":[0.53893,-0.02324,0.05405],"tcp_start":[0.52745,0.00574,0.22918],"tcp_to_object_dist_end":0.02943,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54591,-0.02535,0.02443],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.25887,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.26094,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10883.0,"raw_peak_contact_force":0.30555,"tcp_end":[0.52933,-0.02322,0.04203],"tcp_start":[0.53893,-0.02324,0.05405],"tcp_to_object_dist_end":0.02428,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":17.0,"n_steps":244.0,"n_steps_budget":930.0,"object_pos_end":[0.55843,-0.02601,0.13504],"object_pos_start":[0.54591,-0.02535,0.02443],"object_to_goal_dist_end":0.20916,"object_to_goal_dist_start":0.25887,"object_z_max":0.1346,"peak_contact_force":0.15939,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":6159.0,"raw_peak_contact_force":0.45867,"subtask_id":"lift_clearance","tcp_end":[0.53982,-0.02492,0.15753],"tcp_start":[0.52933,-0.02322,0.04203],"tcp_to_object_dist_end":0.02921,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":116.0,"n_steps_budget":1000.0,"object_pos_end":[0.60136,0.05074,0.21322],"object_pos_start":[0.55843,-0.02601,0.13504],"object_to_goal_dist_end":0.12388,"object_to_goal_dist_start":0.20916,"object_z_max":0.2246,"peak_contact_force":0.0,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":884.0,"raw_peak_contact_force":0.43463,"subtask_id":"approach_goal","tcp_end":[0.59808,0.07467,0.29463],"tcp_start":[0.53982,-0.02492,0.15753],"tcp_to_object_dist_end":0.08492,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":169.0,"n_steps_budget":1000.0,"object_pos_end":[0.64914,0.13738,0.02661],"object_pos_start":[0.60136,0.05074,0.21322],"object_to_goal_dist_end":0.15368,"object_to_goal_dist_start":0.12388,"object_z_max":0.21322,"peak_contact_force":9748.68065,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":742.0,"raw_peak_contact_force":1.95101,"subtask_id":"place_goal","tcp_end":[0.62268,0.1442,0.19513],"tcp_start":[0.59808,0.07467,0.29463],"tcp_to_object_dist_end":0.17072,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.48263,"average_solve_count":259.0,"average_success_count":259.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.17444,"approach_1.arc_height":0.06008,"approach_1.speed":0.07349,"lift_1.lift_height":0.15889,"transport_1.transport_arc":0.02765,"transport_1.transport_height":0.16919,"transport_1.transport_speed":0.01113},"optimized_scores":{"best_composite_score":0.49549,"best_fitness_score":0.96549,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"right_finger","body_b":"grasp_target","contact_count":2084.0,"contact_point_centroid":[0.5795,0.13153,0.19597],"force_p95":0.23228,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.53098,"mean_force":0.10555,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57403,0.11274,0.19544]},{"body_a":"world","body_b":"grasp_target","contact_count":68.0,"contact_point_centroid":[0.46081,0.00229,-0.00168],"force_p95":0.38026,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.43254,"mean_force":0.11779,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45373,0.00252,0.0475]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2198.0,"contact_point_centroid":[0.57894,0.09353,0.19828],"force_p95":0.20284,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3434,"mean_force":0.09478,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.5735,0.11209,0.19693]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4567.0,"contact_point_centroid":[0.45583,-0.01681,0.09936],"force_p95":0.09112,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28492,"mean_force":0.05497,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45519,0.0022,0.09731]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3752.0,"contact_point_centroid":[0.45596,0.02143,0.10053],"force_p95":0.09564,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27717,"mean_force":0.0634,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4553,0.00219,0.09927]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.46289,0.0001,-0.00223],"force_p95":0.18308,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2383,"mean_force":0.13867,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.45599,0.00257,0.04704]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4073.0,"contact_point_centroid":[0.45587,0.02184,0.04728],"force_p95":0.08452,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16835,"mean_force":0.05233,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.45496,0.00256,0.04606]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2292.0,"contact_point_centroid":[0.48905,0.00995,0.1922],"force_p95":0.09948,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14761,"mean_force":0.06259,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.48775,0.02897,0.19049]},{"body_a":"world","body_b":"grasp_target","contact_count":196.0,"contact_point_centroid":[0.46286,-7e-05,-0.00133],"force_p95":0.13839,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12462,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49483,0.01148,0.28423]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1921.0,"contact_point_centroid":[0.48798,0.04666,0.19027],"force_p95":0.09731,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.138,"mean_force":0.0655,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.48617,0.02755,0.18895]},{"body_a":"world","body_b":"grasp_target","contact_count":1096.0,"contact_point_centroid":[0.46286,-7e-05,-0.002],"force_p95":0.12371,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12742,"mean_force":0.12272,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47353,0.01118,0.15511]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5581.0,"contact_point_centroid":[0.45589,-0.01659,0.04848],"force_p95":0.07205,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07685,"mean_force":0.0401,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.45497,0.00256,0.04606]}],"total_contact_groups":12},"final_pose_error":0.02994,"key_states":{"actual_goal_position":[0.61015,0.15287,0.12219],"final_object_position":[0.60902,0.13643,0.11747],"final_tcp_position":[0.5945,0.13744,0.14253],"realised_goal_position":[0.61015,0.15287,0.12219],"realised_object_initial_position":[0.46286,-7e-05,0.03]},"peak_contact_force":0.53098,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02588],"object_pos_start":[0.46286,-7e-05,0.03],"object_to_goal_dist_end":0.23316,"object_to_goal_dist_start":0.23148,"object_z_max":0.03,"peak_contact_force":0.12782,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":196.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object_approach","tcp_end":[0.48536,0.01954,0.25643],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.23247,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":274.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.02588],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.23316,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1096.0,"raw_peak_contact_force":0.12742,"subtask_id":"reach_object_approach","tcp_end":[0.46343,0.00276,0.05504],"tcp_start":[0.48536,0.01954,0.25643],"tcp_to_object_dist_end":0.02916,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4628,0.00179,0.02519],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.23226,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.17718,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11454.0,"raw_peak_contact_force":0.2383,"tcp_end":[0.45493,0.00256,0.04603],"tcp_start":[0.46343,0.00276,0.05504],"tcp_to_object_dist_end":0.02228,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":212.0,"n_steps_budget":870.0,"object_pos_end":[0.47267,0.00111,0.133],"object_pos_start":[0.4628,0.00179,0.02519],"object_to_goal_dist_end":0.20506,"object_to_goal_dist_start":0.23226,"object_z_max":0.13251,"peak_contact_force":0.08376,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":8387.0,"raw_peak_contact_force":0.43254,"subtask_id":"lift_clearance","tcp_end":[0.45851,0.00188,0.15484],"tcp_start":[0.45493,0.00256,0.04603],"tcp_to_object_dist_end":0.02604,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":21.0,"n_steps":120.0,"n_steps_budget":1000.0,"object_pos_end":[0.56634,0.08454,0.22355],"object_pos_start":[0.47267,0.00111,0.133],"object_to_goal_dist_end":0.12985,"object_to_goal_dist_start":0.20506,"object_z_max":0.22273,"peak_contact_force":0.11953,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4213.0,"raw_peak_contact_force":0.14761,"subtask_id":"approach_goal","tcp_end":[0.55145,0.08628,0.2466],"tcp_start":[0.45851,0.00188,0.15484],"tcp_to_object_dist_end":0.0275,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":181.0,"n_steps_budget":1000.0,"object_pos_end":[0.60902,0.13643,0.11747],"object_pos_start":[0.56634,0.08454,0.22355],"object_to_goal_dist_end":0.01714,"object_to_goal_dist_start":0.12985,"object_z_max":0.22723,"peak_contact_force":0.09729,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4282.0,"raw_peak_contact_force":0.53098,"subtask_id":"place_goal","tcp_end":[0.5945,0.13744,0.14253],"tcp_start":[0.55145,0.08628,0.2466],"tcp_to_object_dist_end":0.02898,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```