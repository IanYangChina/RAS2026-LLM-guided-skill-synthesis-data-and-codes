## Search State

- **Seed**: 9
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → descend → grasp → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 15 | 0.1037 | 1.00 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 15 | 0.1000 | 1.00 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 15 | 0.1040 | 1.00 | ✅ accepted |
| 5 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 15 | -0.2383 | 0.38 | ✅ accepted |
| 4 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 15 | -0.2407 | 0.38 | ✅ accepted |

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

## Current Skill (Q=0.104) — your mutation base

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

- **Composite score**: 0.104
- **task_score** (E): 1.000
- **fitness_score**: 0.974  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.870

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0765 |
| descend_1 | 1.00 | 1.00 | 0.1917 |
| grasp_1 | 1.00 | 1.00 | 0.0131 |
| lift_1 | 1.00 | 1.00 | 0.1772 |
| transport_1 | 1.00 | 1.00 | 0.1971 |
| descend_to_place | 1.00 | 1.00 | 0.0899 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.516, -0.014, 0.238) | (0.515, -0.017, 0.030)→(0.515, -0.017, 0.026) | 0.268→0.270 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.516, -0.014, 0.238)→(0.511, -0.016, 0.046) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 4.000 | 10.193 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.511, -0.016, 0.046)→(0.502, -0.016, 0.037) | (0.515, -0.017, 0.026)→(0.515, -0.016, 0.026) | 0.270→0.270 | 1.00 / 43.000 | 0.136 | 0.177 |
| lift_1 | lift | 1.00 / step_budget | (0.502, -0.016, 0.037)→(0.511, -0.016, 0.214) | (0.515, -0.016, 0.026)→(0.520, -0.016, 0.198) | 0.270→0.235 | 1.00 / 38.000 | 0.078 | 0.479 |
| transport_1 | approach | 1.00 / step_budget | (0.511, -0.016, 0.214)→(0.598, 0.143, 0.270) | (0.520, -0.016, 0.198)→(0.611, 0.143, 0.254) | 0.235→0.097 | 1.00 / 29.333 | 0.098 | 0.111 |
| descend_to_place | descend | 1.00 / step_budget | (0.598, 0.143, 0.270)→(0.610, 0.171, 0.188) | (0.611, 0.143, 0.254)→(0.622, 0.171, 0.169) | 0.097→0.012 | 1.00 / 26.000 | 0.105 | 0.419 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.577
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.489
- phase_breakdown.reach_object_approach_score: 0.184
- phase_breakdown.approach_goal_score: 0.485
- phase_breakdown.lift_clearance_score: 0.437
- phase_breakdown.place_goal_score: 0.910
- grasp_place_fitness: 0.974

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.974
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.104
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Parameters at lower bound**: transport_1.transport_arc
- **Final σ (mean)**: 0.365


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.94647,"average_solve_count":467.0,"average_success_count":467.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.1892,"approach_1.arc_height":0.08651,"approach_1.speed":0.08128,"descend_1.descend_height":0.00148,"descend_1.descend_speed":0.04763,"descend_1.descend_tolerance":0.0317,"descend_to_place.descend_speed_place":0.0288,"descend_to_place.place_height":0.00303,"descend_to_place.place_tolerance":0.01889,"lift_1.lift_height":0.2728,"lift_1.lift_speed":0.02189,"transport_1.transport_arc":0.02,"transport_1.transport_height":0.17263,"transport_1.transport_speed":0.03614,"transport_1.transport_tolerance":0.06704},"optimized_scores":{"best_composite_score":0.10369,"best_fitness_score":0.97369,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":90.0,"contact_point_centroid":[0.53298,-0.021,-0.00142],"force_p95":0.46132,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.48873,"mean_force":0.17293,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5226,-0.02111,0.03701]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3669.0,"contact_point_centroid":[0.60486,0.21883,0.29805],"force_p95":0.10438,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.41915,"mean_force":0.07414,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60119,0.19993,0.29706]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16936.0,"contact_point_centroid":[0.5267,-0.00186,0.15713],"force_p95":0.07731,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28779,"mean_force":0.05435,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52638,-0.02099,0.15472]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4019.0,"contact_point_centroid":[0.60471,0.18095,0.29943],"force_p95":0.09499,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2795,"mean_force":0.06729,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60109,0.19952,0.29882]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17698.0,"contact_point_centroid":[0.52664,-0.04007,0.15638],"force_p95":0.07636,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26808,"mean_force":0.05245,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52636,-0.02099,0.15431]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53702,-0.02121,-0.00203],"force_p95":0.13107,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14975,"mean_force":0.1252,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52484,-0.02115,0.03736]},{"body_a":"world","body_b":"grasp_target","contact_count":676.0,"contact_point_centroid":[0.53702,-0.02132,-0.00181],"force_p95":0.13762,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12335,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52189,-0.0133,0.27589]},{"body_a":"world","body_b":"grasp_target","contact_count":1488.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53314,-0.02161,0.14326]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4120.0,"contact_point_centroid":[0.52425,-0.00192,0.03875],"force_p95":0.07612,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10096,"mean_force":0.05176,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52364,-0.02113,0.03599]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4391.0,"contact_point_centroid":[0.56304,0.08819,0.32619],"force_p95":0.08488,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09616,"mean_force":0.0577,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.5618,0.06901,0.32376]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5426.0,"contact_point_centroid":[0.56188,0.04872,0.32475],"force_p95":0.07486,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09286,"mean_force":0.04919,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.56138,0.06769,0.32326]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4873.0,"contact_point_centroid":[0.52429,-0.0402,0.0378],"force_p95":0.06816,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08634,"mean_force":0.04472,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52364,-0.02113,0.03599]}],"total_contact_groups":12},"final_pose_error":0.01951,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.61633,0.21893,0.20738],"final_tcp_position":[0.60569,0.21899,0.22724],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":0.48873,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":170.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":676.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object_approach","tcp_end":[0.53569,-0.02197,0.23862],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.21261,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":372.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1488.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object_approach","tcp_end":[0.53251,-0.0213,0.0465],"tcp_start":[0.53569,-0.02197,0.23862],"tcp_to_object_dist_end":0.02098,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53691,-0.02099,0.02588],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31657,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12938,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10793.0,"raw_peak_contact_force":0.14975,"tcp_end":[0.52361,-0.02113,0.03595],"tcp_start":[0.53251,-0.0213,0.0465],"tcp_to_object_dist_end":0.01668,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":897.0,"n_steps_budget":1000.0,"object_pos_end":[0.54161,-0.02087,0.26217],"object_pos_start":[0.53691,-0.02099,0.02588],"object_to_goal_dist_end":0.26369,"object_to_goal_dist_start":0.31657,"object_z_max":0.26191,"peak_contact_force":0.07791,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":34724.0,"raw_peak_contact_force":0.48873,"subtask_id":"lift_clearance","tcp_end":[0.53366,-0.02095,0.27903],"tcp_start":[0.52361,-0.02113,0.03595],"tcp_to_object_dist_end":0.01864,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":264.0,"n_steps_budget":1000.0,"object_pos_end":[0.60735,0.18176,0.34748],"object_pos_start":[0.54161,-0.02087,0.26217],"object_to_goal_dist_end":0.14746,"object_to_goal_dist_start":0.26369,"object_z_max":0.3473,"peak_contact_force":0.08818,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9817.0,"raw_peak_contact_force":0.09616,"subtask_id":"approach_goal","tcp_end":[0.59767,0.18203,0.36438],"tcp_start":[0.53366,-0.02095,0.27903],"tcp_to_object_dist_end":0.01948,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":267.0,"n_steps_budget":1000.0,"object_pos_end":[0.61633,0.21893,0.20738],"object_pos_start":[0.60735,0.18176,0.34748],"object_to_goal_dist_end":0.01068,"object_to_goal_dist_start":0.14746,"object_z_max":0.34752,"peak_contact_force":0.10053,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7688.0,"raw_peak_contact_force":0.41915,"subtask_id":"place_goal","tcp_end":[0.60569,0.21899,0.22724],"tcp_start":[0.59767,0.18203,0.36438],"tcp_to_object_dist_end":0.02252,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.9646,"average_solve_count":339.0,"average_success_count":339.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.20001,"approach_1.arc_height":0.07551,"approach_1.speed":0.03841,"descend_1.descend_height":0.00192,"descend_1.descend_speed":0.0243,"descend_1.descend_tolerance":0.03676,"descend_to_place.descend_speed_place":0.05331,"descend_to_place.place_height":0.01544,"descend_to_place.place_tolerance":0.00885,"lift_1.lift_height":0.13382,"lift_1.lift_speed":0.03971,"transport_1.transport_arc":0.0299,"transport_1.transport_height":0.05155,"transport_1.transport_speed":0.05525,"transport_1.transport_tolerance":0.05686},"optimized_scores":{"best_composite_score":0.10297,"best_fitness_score":0.97297,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":96.0,"contact_point_centroid":[0.54183,-0.02835,-0.00146],"force_p95":0.44114,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.46933,"mean_force":0.16472,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53081,-0.02869,0.03707]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1028.0,"contact_point_centroid":[0.62083,0.15376,0.20775],"force_p95":0.13282,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33808,"mean_force":0.08554,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61671,0.13484,0.20642]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7722.0,"contact_point_centroid":[0.5342,-0.00941,0.0884],"force_p95":0.07874,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27416,"mean_force":0.05514,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53396,-0.02857,0.08577]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8201.0,"contact_point_centroid":[0.53407,-0.04767,0.08734],"force_p95":0.07677,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26305,"mean_force":0.05281,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53389,-0.02857,0.08518]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1229.0,"contact_point_centroid":[0.62017,0.11597,0.20698],"force_p95":0.11023,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23719,"mean_force":0.07157,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61658,0.13455,0.20667]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5456,-0.02908,-0.00205],"force_p95":0.13698,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1693,"mean_force":0.12667,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.533,-0.02876,0.03756]},{"body_a":"world","body_b":"grasp_target","contact_count":740.0,"contact_point_centroid":[0.5456,-0.02923,-0.00183],"force_p95":0.13759,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12329,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52361,-0.01603,0.28282]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4105.0,"contact_point_centroid":[0.53256,-0.00952,0.0389],"force_p95":0.07722,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12518,"mean_force":0.0518,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53179,-0.02873,0.03614]},{"body_a":"world","body_b":"grasp_target","contact_count":1568.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.54042,-0.02874,0.14912]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4438.0,"contact_point_centroid":[0.57073,0.01656,0.18574],"force_p95":0.07808,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11893,"mean_force":0.05135,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.57006,0.03556,0.18403]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3728.0,"contact_point_centroid":[0.57135,0.05516,0.18676],"force_p95":0.08319,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10216,"mean_force":0.058,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.57029,0.03603,0.18427]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4902.0,"contact_point_centroid":[0.53257,-0.04781,0.03794],"force_p95":0.06941,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09043,"mean_force":0.04473,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53179,-0.02873,0.03614]}],"total_contact_groups":12},"final_pose_error":0.01965,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.63608,0.14832,0.17849],"final_tcp_position":[0.62248,0.14841,0.19476],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":30.33315,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":186.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":740.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object_approach","tcp_end":[0.54203,-0.02857,0.24946],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.22347,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":392.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":30.33315,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1568.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object_approach","tcp_end":[0.54079,-0.029,0.04702],"tcp_start":[0.54203,-0.02857,0.24946],"tcp_to_object_dist_end":0.02155,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54549,-0.02866,0.02582],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26065,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.13415,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10807.0,"raw_peak_contact_force":0.1693,"tcp_end":[0.53176,-0.02872,0.0361],"tcp_start":[0.54079,-0.029,0.04702],"tcp_to_object_dist_end":0.01716,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":405.0,"n_steps_budget":1000.0,"object_pos_end":[0.55083,-0.02855,0.1271],"object_pos_start":[0.54549,-0.02866,0.02582],"object_to_goal_dist_end":0.21597,"object_to_goal_dist_start":0.26065,"object_z_max":0.12686,"peak_contact_force":0.08148,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":16019.0,"raw_peak_contact_force":0.46933,"subtask_id":"lift_clearance","tcp_end":[0.54006,-0.02853,0.14048],"tcp_start":[0.53176,-0.02872,0.0361],"tcp_to_object_dist_end":0.01717,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":33.0,"n_steps":220.0,"n_steps_budget":1000.0,"object_pos_end":[0.62512,0.12105,0.2023],"object_pos_start":[0.55083,-0.02855,0.1271],"object_to_goal_dist_end":0.05128,"object_to_goal_dist_start":0.21597,"object_z_max":0.20225,"peak_contact_force":0.09786,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8166.0,"raw_peak_contact_force":0.11893,"subtask_id":"approach_goal","tcp_end":[0.61187,0.12121,0.21764],"tcp_start":[0.54006,-0.02853,0.14048],"tcp_to_object_dist_end":0.02027,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":85.0,"n_steps_budget":1000.0,"object_pos_end":[0.63608,0.14832,0.17849],"object_pos_start":[0.62512,0.12105,0.2023],"object_to_goal_dist_end":0.01699,"object_to_goal_dist_start":0.05128,"object_z_max":0.2023,"peak_contact_force":0.1044,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2257.0,"raw_peak_contact_force":0.33808,"subtask_id":"place_goal","tcp_end":[0.62248,0.14841,0.19476],"tcp_start":[0.61187,0.12121,0.21764],"tcp_to_object_dist_end":0.02121,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.74953,"average_solve_count":527.0,"average_success_count":527.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.17939,"approach_1.arc_height":0.13033,"approach_1.speed":0.02795,"descend_1.descend_height":0.00013,"descend_1.descend_speed":0.04117,"descend_1.descend_tolerance":0.01832,"descend_to_place.descend_speed_place":0.01199,"descend_to_place.place_height":0.00286,"descend_to_place.place_tolerance":0.01197,"lift_1.lift_height":0.21488,"lift_1.lift_speed":0.03561,"transport_1.transport_arc":0.06947,"transport_1.transport_height":0.07155,"transport_1.transport_speed":0.03277,"transport_1.transport_tolerance":0.06656},"optimized_scores":{"best_composite_score":0.10446,"best_fitness_score":0.97446,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"right_finger","body_b":"grasp_target","contact_count":2228.0,"contact_point_centroid":[0.59624,0.15409,0.18681],"force_p95":0.12291,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.50038,"mean_force":0.08651,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59085,0.13546,0.18536]},{"body_a":"world","body_b":"grasp_target","contact_count":88.0,"contact_point_centroid":[0.45924,0.00111,-0.00152],"force_p95":0.44234,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.4795,"mean_force":0.19263,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45092,0.0009,0.03854]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2042.0,"contact_point_centroid":[0.59629,0.11707,0.1863],"force_p95":0.12265,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.39299,"mean_force":0.09099,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59103,0.13564,0.18468]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12383.0,"contact_point_centroid":[0.45389,-0.01837,0.13042],"force_p95":0.07518,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25649,"mean_force":0.05179,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45365,0.00078,0.12852]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12386.0,"contact_point_centroid":[0.45383,0.01993,0.13036],"force_p95":0.07399,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25269,"mean_force":0.05154,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45365,0.00078,0.1285]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.46287,0.0,-0.00209],"force_p95":0.14767,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2113,"mean_force":0.12928,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.45292,0.00094,0.03862]},{"body_a":"world","body_b":"grasp_target","contact_count":684.0,"contact_point_centroid":[0.46286,-7e-05,-0.00181],"force_p95":0.13762,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12334,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48556,0.01041,0.26581]},{"body_a":"world","body_b":"grasp_target","contact_count":1472.0,"contact_point_centroid":[0.46286,-7e-05,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.46352,0.00547,0.13651]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3740.0,"contact_point_centroid":[0.51133,0.07043,0.25009],"force_p95":0.0901,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11907,"mean_force":0.05872,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51002,0.05132,0.24798]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4229.0,"contact_point_centroid":[0.51229,0.03344,0.25028],"force_p95":0.08714,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11352,"mean_force":0.05394,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51116,0.05244,0.24868]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5295.0,"contact_point_centroid":[0.45119,0.02011,0.03884],"force_p95":0.06636,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10815,"mean_force":0.04107,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.45186,0.00092,0.03761]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5078.0,"contact_point_centroid":[0.45185,-0.01837,0.03934],"force_p95":0.06928,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07756,"mean_force":0.04376,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.45186,0.00092,0.03761]}],"total_contact_groups":12},"final_pose_error":0.01992,"key_states":{"actual_goal_position":[0.61015,0.15287,0.12219],"final_object_position":[0.61485,0.14589,0.12129],"final_tcp_position":[0.60063,0.14586,0.14109],"realised_goal_position":[0.61015,0.15287,0.12219],"realised_object_initial_position":[0.46286,-7e-05,0.03]},"peak_contact_force":0.50038,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":172.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.03],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.23148,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":684.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object_approach","tcp_end":[0.46903,0.00977,0.22567],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.19999,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":368.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1472.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object_approach","tcp_end":[0.45977,0.00106,0.04551],"tcp_start":[0.46903,0.00977,0.22567],"tcp_to_object_dist_end":0.01977,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46277,0.00069,0.02568],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.2328,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.14554,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12173.0,"raw_peak_contact_force":0.2113,"tcp_end":[0.45183,0.00092,0.03758],"tcp_start":[0.45977,0.00106,0.04551],"tcp_to_object_dist_end":0.01616,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":619.0,"n_steps_budget":1000.0,"object_pos_end":[0.46681,0.0006,0.20608],"object_pos_start":[0.46277,0.00069,0.02568],"object_to_goal_dist_end":0.22532,"object_to_goal_dist_start":0.2328,"object_z_max":0.2058,"peak_contact_force":0.07329,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":24857.0,"raw_peak_contact_force":0.4795,"subtask_id":"lift_clearance","tcp_end":[0.45901,0.00068,0.22119],"tcp_start":[0.45183,0.00092,0.03758],"tcp_to_object_dist_end":0.01701,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":225.0,"n_steps_budget":1000.0,"object_pos_end":[0.60034,0.12712,0.21171],"object_pos_start":[0.46681,0.0006,0.20608],"object_to_goal_dist_end":0.09366,"object_to_goal_dist_start":0.22532,"object_z_max":0.24895,"peak_contact_force":0.10739,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7969.0,"raw_peak_contact_force":0.11907,"subtask_id":"approach_goal","tcp_end":[0.58536,0.12716,0.2282],"tcp_start":[0.45901,0.00068,0.22119],"tcp_to_object_dist_end":0.02228,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":185.0,"n_steps_budget":1000.0,"object_pos_end":[0.61485,0.14589,0.12129],"object_pos_start":[0.60034,0.12712,0.21171],"object_to_goal_dist_end":0.00846,"object_to_goal_dist_start":0.09366,"object_z_max":0.21171,"peak_contact_force":0.10994,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4270.0,"raw_peak_contact_force":0.50038,"subtask_id":"place_goal","tcp_end":[0.60063,0.14586,0.14109],"tcp_start":[0.58536,0.12716,0.2282],"tcp_to_object_dist_end":0.02437,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```