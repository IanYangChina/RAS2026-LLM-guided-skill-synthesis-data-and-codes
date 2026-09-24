## Search State

- **Seed**: 6
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → descend → grasp → lift → approach → align → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 15 | 0.0754 | 1.00 | ❌ rejected |
| 12 | approach → descend → grasp → lift → approach → align → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 15 | 0.0759 | 1.00 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → align → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 15 | 0.0764 | 1.00 | ✅ accepted |
| 10 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 11 | -0.0894 | 0.28 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 11 | -0.0782 | 0.29 | ❌ rejected |

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
- Frozen realised-scene SHA-256: `584133b5261cffac0dd4282704ff39e97bf4d452e60b02507679bbdea5a4de22`
- Frozen object start: [0.5038164351471943, -0.015672913018666156, 0.03]
- Frozen task target: [0.5869067239795378, 0.18744967655878825, 0.24811674852797]
- Goal object position: (0.5869067239795378, 0.18744967655878825, 0.24811674852797)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5869067239795378, 0.18744967655878825, 0.24811674852797)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5038164351471943, -0.015672913018666156, 0.03)
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
  frozen_object_start: [0.5038, -0.0157, 0.03]
  frozen_task_target: [0.5869, 0.1874, 0.2481]
  frozen_object_starts: {'grasp_target': [0.5038164351471943, -0.015672913018666156, 0.03]}
  frozen_targets: {'place_target': [0.5869067239795378, 0.18744967655878825, 0.24811674852797]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 584133b5261cffac0dd4282704ff39e97bf4d452e60b02507679bbdea5a4de22

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
| `object` | offset from object initial position (0.5038164351471943, -0.015672913018666156, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5869067239795378, 0.18744967655878825, 0.24811674852797) | final destination targets |
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

## Current Skill (Q=0.075) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: approach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.2
- id: lift_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.2
- id: transport_to_goal
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.3
- id: place_at_goal
  target_entity: object
  metric: goal_progress
  weight: 0.3
phases:
- id: approach_1
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
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    approach_z_offset:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: approach_object
- id: descend_1
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
    - 0.02
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    descend_z_offset:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: approach_object
- id: grasp_1
  type: grasp
  control: position_control
  termination: time_limit
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: lift_object
- id: lift_1
  type: lift
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
    - 0.15
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.1
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
  subtask_id: lift_object
- id: transport_above_goal
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
    - 0.15
  parameters:
    transport_height:
      type: scalar
      range:
      - 0.1
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    transport_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
    transport_tolerance:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.03
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: transport_to_goal
- id: align_over_goal
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.08
  parameters:
    align_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    align_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.03
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
    align_z_offset:
      type: scalar
      range:
      - 0.05
      - 0.12
      default: 0.08
      binds_to:
      - path: target.offset.z
        mode: replace
  guards:
  - id: object_held
    when: during_phase
    predicate: bilateral_grasp
    threshold: 0.1
    on_failure: abort
  subtask_id: place_at_goal
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
  parameters:
    descend_place_speed:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
    descend_place_z_offset:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: replace
    descend_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  guards:
  - id: no_table_collision
    when: during_phase
    predicate: force_below
    args:
      max_force: 15.0
    threshold: 15.0
    on_failure: abort
  - id: object_still_held
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.1
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: reduce_speed
  subtask_id: place_at_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.1]
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - approach_z_offset: status=consumed; consumers=target.offset.z (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.02]
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - descend_z_offset: status=consumed; consumers=target.offset.z (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **lift_1** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.15]
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
- **transport_above_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15]
  - parameter_bindings:
    - transport_height: status=consumed; consumers=target.offset.z (replace)
    - transport_speed: status=consumed; consumers=generator.speed (replace)
    - transport_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **align_over_goal** (`align`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.08]
  - parameter_bindings:
    - align_speed: status=consumed; consumers=generator.speed (replace)
    - align_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
    - align_z_offset: status=consumed; consumers=target.offset.z (replace)
  - guards:
    - id=object_held, when=during_phase, predicate=bilateral_grasp, on_failure=abort, threshold=0.1
- **descend_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - descend_place_speed: status=consumed; consumers=generator.speed (replace)
    - descend_place_z_offset: status=consumed; consumers=target.offset.z (replace)
    - descend_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
  - guards:
    - id=no_table_collision, when=during_phase, predicate=force_below, on_failure=abort, threshold=15.0, args={'max_force': 15.0}
    - id=object_still_held, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.1
  - retries: max_attempts=1, strategy=reduce_speed

## Design Metrics

- **Composite score**: 0.075
- **task_score** (E): 1.000
- **fitness_score**: 0.975  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.900

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1489 |
| descend_1 | 1.00 | 1.00 | 0.1157 |
| grasp_1 | 1.00 | 1.00 | 0.0124 |
| lift_1 | 0.33 | 1.00 | 0.1254 |
| transport_above_goal | 0.67 | 1.00 | 0.2017 |
| align_over_goal | 1.00 | 1.00 | 0.0612 |
| descend_to_place | 1.00 | 1.00 | 0.0658 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, 0.021, 0.157) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 | 1.00 / 4.000 | 12.963 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.496, 0.021, 0.157)→(0.494, 0.024, 0.042) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.494, 0.024, 0.042)→(0.486, 0.023, 0.032) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.272 | 1.00 / 42.667 | 0.152 | 0.206 |
| lift_1 | lift | 0.33 / step_budget | (0.486, 0.023, 0.032)→(0.491, 0.023, 0.158) | (0.500, 0.024, 0.026)→(0.501, 0.024, 0.143) | 0.272→0.217 | 1.00 / 37.000 | 0.081 | 0.592 |
| transport_above_goal | approach | 0.67 / step_budget | (0.491, 0.023, 0.158)→(0.574, 0.153, 0.286) | (0.501, 0.024, 0.143)→(0.584, 0.156, 0.269) | 0.217→0.101 | 1.00 / 35.667 | 0.086 | 0.140 |
| align_over_goal | align | 1.00 / step_budget | (0.574, 0.153, 0.286)→(0.592, 0.190, 0.290) | (0.584, 0.156, 0.269)→(0.602, 0.193, 0.271) | 0.101→0.064 | 1.00 / 35.000 | 0.089 | 0.231 |
| descend_to_place | descend | 1.00 / step_budget | (0.592, 0.190, 0.290)→(0.594, 0.193, 0.224) | (0.602, 0.193, 0.271)→(0.604, 0.197, 0.204) | 0.064→0.007 | 1.00 / 30.333 | 0.093 | 0.257 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.733
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.586
- phase_breakdown.approach_object_score: 0.164
- phase_breakdown.transport_to_goal_score: 0.637
- phase_breakdown.lift_object_score: 0.430
- phase_breakdown.place_at_goal_score: 0.918
- grasp_place_fitness: 0.977

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.977
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.076
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.309


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `daf90631fcbaf423e19452d0c9b90b9715013985cc94ef12ca0cd881e96195aa`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `94660347aa4f41f6801e53bd449f8df59691da8bebfa4fef4947a3513fe04781`; realized-scene SHA-256: `584133b5261cffac0dd4282704ff39e97bf4d452e60b02507679bbdea5a4de22`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50382,-0.01567,0.03]},{"name":"goal","value":[0.58691,0.18745,0.24812]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.50382,-0.01567,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58691,0.18745,0.24812]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.43494,"average_solve_count":269.0,"average_success_count":269.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_over_goal.align_speed":0.0751,"align_over_goal.align_tolerance":0.01408,"align_over_goal.align_z_offset":0.09418,"approach_1.approach_speed":0.06103,"approach_1.approach_z_offset":0.08923,"descend_1.descend_speed":0.04535,"descend_1.descend_z_offset":0.01134,"descend_to_place.descend_place_speed":0.03205,"descend_to_place.descend_place_z_offset":0.00447,"descend_to_place.descend_tolerance":0.021,"lift_1.lift_height":0.21986,"lift_1.lift_speed":0.07754,"transport_above_goal.transport_height":0.1434,"transport_above_goal.transport_speed":0.08487,"transport_above_goal.transport_tolerance":0.01234},"optimized_scores":{"best_composite_score":0.07262,"best_fitness_score":0.97262,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":158.0,"contact_point_centroid":[0.49963,-0.01544,-0.00116],"force_p95":0.33241,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.53496,"mean_force":0.09206,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48844,-0.01537,0.03787]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20802.0,"contact_point_centroid":[0.49104,0.00358,0.09803],"force_p95":0.07295,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30477,"mean_force":0.04916,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48991,-0.01546,0.09617]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18314.0,"contact_point_centroid":[0.49021,-0.03464,0.09874],"force_p95":0.07889,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3009,"mean_force":0.05463,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48988,-0.01546,0.09603]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1712.0,"contact_point_centroid":[0.58001,0.20194,0.30625],"force_p95":0.08391,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19987,"mean_force":0.06324,"phase_index":6.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.58255,0.18294,0.3041]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1936.0,"contact_point_centroid":[0.59004,0.16534,0.30477],"force_p95":0.07965,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16252,"mean_force":0.05719,"phase_index":6.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.58254,0.1829,0.3048]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50381,-0.01576,-0.00203],"force_p95":0.13284,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16097,"mean_force":0.12531,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49109,-0.01539,0.03773]},{"body_a":"world","body_b":"grasp_target","contact_count":2236.0,"contact_point_centroid":[0.50382,-0.01567,-0.00194],"force_p95":0.13166,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12284,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49861,-0.00703,0.21411]},{"body_a":"world","body_b":"grasp_target","contact_count":1136.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49749,-0.01489,0.08653]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13963.0,"contact_point_centroid":[0.56492,0.11522,0.2981],"force_p95":0.07389,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12057,"mean_force":0.05109,"phase_index":5.0,"phase_name":"align_over_goal","phase_type":"align","tcp_position_centroid":[0.55895,0.13342,0.29688]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12869.0,"contact_point_centroid":[0.55692,0.1517,0.2992],"force_p95":0.0753,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11886,"mean_force":0.05403,"phase_index":5.0,"phase_name":"align_over_goal","phase_type":"align","tcp_position_centroid":[0.55858,0.13265,0.29635]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18380.0,"contact_point_centroid":[0.51474,0.05439,0.21554],"force_p95":0.07711,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11877,"mean_force":0.05324,"phase_index":4.0,"phase_name":"transport_above_goal","phase_type":"approach","tcp_position_centroid":[0.51458,0.0353,0.21332]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18644.0,"contact_point_centroid":[0.51738,0.01707,0.216],"force_p95":0.07596,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10801,"mean_force":0.05198,"phase_index":4.0,"phase_name":"transport_above_goal","phase_type":"approach","tcp_position_centroid":[0.51492,0.036,0.21413]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5327.0,"contact_point_centroid":[0.49069,0.00368,0.0384],"force_p95":0.06673,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0959,"mean_force":0.04111,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48987,-0.01538,0.03643]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4146.0,"contact_point_centroid":[0.48939,-0.03465,0.03908],"force_p95":0.079,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09356,"mean_force":0.05186,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48987,-0.01538,0.03643]}],"total_contact_groups":14},"final_pose_error":0.02054,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.58925,0.18781,0.24682],"final_tcp_position":[0.58338,0.18474,0.27264],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":0.53496,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":560.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2236.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.49942,-0.01439,0.12806],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.10214,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":284.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1136.0,"raw_peak_contact_force":0.12263,"subtask_id":"approach_object","tcp_end":[0.49834,-0.01544,0.04554],"tcp_start":[0.49942,-0.01439,0.12806],"tcp_to_object_dist_end":0.02028,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5037,-0.01578,0.02588],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31244,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13287,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11273.0,"raw_peak_contact_force":0.16097,"subtask_id":"lift_object","tcp_end":[0.48984,-0.01538,0.03639],"tcp_start":[0.49834,-0.01544,0.04554],"tcp_to_object_dist_end":0.0174,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50299,-0.01593,0.14376],"object_pos_start":[0.5037,-0.01578,0.02588],"object_to_goal_dist_end":0.24351,"object_to_goal_dist_start":0.31244,"object_z_max":0.14363,"peak_contact_force":0.0795,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":39274.0,"raw_peak_contact_force":0.53496,"subtask_id":"lift_object","tcp_end":[0.49454,-0.01558,0.16104],"tcp_start":[0.48984,-0.01538,0.03639],"tcp_to_object_dist_end":0.01924,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54295,0.08345,0.24398],"object_pos_start":[0.50299,-0.01593,0.14376],"object_to_goal_dist_end":0.11299,"object_to_goal_dist_start":0.24351,"object_z_max":0.24387,"peak_contact_force":0.0775,"phase_name":"transport_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":37024.0,"raw_peak_contact_force":0.11877,"subtask_id":"transport_to_goal","tcp_end":[0.53628,0.08211,0.26589],"tcp_start":[0.49454,-0.01558,0.16104],"tcp_to_object_dist_end":0.02294,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":712.0,"n_steps_budget":1000.0,"object_pos_end":[0.58929,0.18449,0.30633],"object_pos_start":[0.54295,0.08345,0.24398],"object_to_goal_dist_end":0.05834,"object_to_goal_dist_start":0.11299,"object_z_max":0.30626,"peak_contact_force":0.07509,"phase_name":"align_over_goal","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":26832.0,"raw_peak_contact_force":0.12057,"subtask_id":"place_at_goal","tcp_end":[0.58224,0.18137,0.33063],"tcp_start":[0.53628,0.08211,0.26589],"tcp_to_object_dist_end":0.0255,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":33.0,"n_steps":112.0,"n_steps_budget":1000.0,"object_pos_end":[0.58925,0.18781,0.24682],"object_pos_start":[0.58929,0.18449,0.30633],"object_to_goal_dist_end":0.00271,"object_to_goal_dist_start":0.05834,"object_z_max":0.30633,"peak_contact_force":0.07935,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3648.0,"raw_peak_contact_force":0.19987,"subtask_id":"place_at_goal","tcp_end":[0.58338,0.18474,0.27264],"tcp_start":[0.58224,0.18137,0.33063],"tcp_to_object_dist_end":0.02665,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `fe7e0be33c0bb4db9d2bbbb069b6113d0e5a69a675a0d70bc1f582243e99e3cf`; realized-scene SHA-256: `8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51251,0.03972,0.03]},{"name":"goal","value":[0.62757,0.17252,0.14502]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.51251,0.03972,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.62757,0.17252,0.14502]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.3064,"average_solve_count":297.0,"average_success_count":297.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_over_goal.align_speed":0.08679,"align_over_goal.align_tolerance":0.0119,"align_over_goal.align_z_offset":0.07397,"approach_1.approach_speed":0.01025,"approach_1.approach_z_offset":0.0976,"descend_1.descend_speed":0.07599,"descend_1.descend_z_offset":0.00501,"descend_to_place.descend_place_speed":0.05229,"descend_to_place.descend_place_z_offset":-0.01109,"descend_to_place.descend_tolerance":0.01844,"lift_1.lift_height":0.18898,"lift_1.lift_speed":0.09013,"transport_above_goal.transport_height":0.15673,"transport_above_goal.transport_speed":0.08529,"transport_above_goal.transport_tolerance":0.03049},"optimized_scores":{"best_composite_score":0.07649,"best_fitness_score":0.97649,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":162.0,"contact_point_centroid":[0.50906,0.03749,-0.00123],"force_p95":0.43995,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.66178,"mean_force":0.09806,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4969,0.03805,0.03166]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17000.0,"contact_point_centroid":[0.50016,0.05728,0.10291],"force_p95":0.0833,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33529,"mean_force":0.05872,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49989,0.03809,0.10014]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1983.0,"contact_point_centroid":[0.61357,0.18119,0.25803],"force_p95":0.10515,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32018,"mean_force":0.07506,"phase_index":5.0,"phase_name":"align_over_goal","phase_type":"align","tcp_position_centroid":[0.61584,0.16236,0.25489]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20703.0,"contact_point_centroid":[0.50168,0.01916,0.10033],"force_p95":0.07859,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30751,"mean_force":0.04962,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49977,0.03808,0.09873]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1823.0,"contact_point_centroid":[0.61947,0.18786,0.19365],"force_p95":0.11169,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27533,"mean_force":0.08345,"phase_index":6.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62076,0.16882,0.19074]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2439.0,"contact_point_centroid":[0.62279,0.14482,0.25422],"force_p95":0.09282,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25322,"mean_force":0.06326,"phase_index":5.0,"phase_name":"align_over_goal","phase_type":"align","tcp_position_centroid":[0.61597,0.16252,0.25398]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2396.0,"contact_point_centroid":[0.62834,0.1515,0.19034],"force_p95":0.09032,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23684,"mean_force":0.06346,"phase_index":6.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62077,0.16883,0.19034]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51258,0.03965,-0.00213],"force_p95":0.16167,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22517,"mean_force":0.13278,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49956,0.03829,0.03118]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5250.0,"contact_point_centroid":[0.49971,0.01917,0.03155],"force_p95":0.06838,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19125,"mean_force":0.04119,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49832,0.03819,0.02984]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7217.0,"contact_point_centroid":[0.56106,0.07786,0.2238],"force_p95":0.08851,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1416,"mean_force":0.05654,"phase_index":4.0,"phase_name":"transport_above_goal","phase_type":"approach","tcp_position_centroid":[0.5567,0.09624,0.22305]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6084.0,"contact_point_centroid":[0.55536,0.11494,0.22523],"force_p95":0.09236,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13988,"mean_force":0.06463,"phase_index":4.0,"phase_name":"transport_above_goal","phase_type":"approach","tcp_position_centroid":[0.55639,0.0959,0.22274]},{"body_a":"world","body_b":"grasp_target","contact_count":2344.0,"contact_point_centroid":[0.51251,0.03972,-0.00194],"force_p95":0.13103,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12283,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50252,0.01774,0.21762]},{"body_a":"world","body_b":"grasp_target","contact_count":1232.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50583,0.03749,0.08694]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4238.0,"contact_point_centroid":[0.49873,0.05753,0.03264],"force_p95":0.08298,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0928,"mean_force":0.05183,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49832,0.03819,0.02984]}],"total_contact_groups":14},"final_pose_error":0.018,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.63422,0.17466,0.13383],"final_tcp_position":[0.62223,0.1703,0.15098],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":19.87833,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":587.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":19.87833,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2344.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.50749,0.03634,0.13531],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.10945,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":308.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1232.0,"raw_peak_contact_force":0.12263,"subtask_id":"approach_object","tcp_end":[0.50695,0.03888,0.03927],"tcp_start":[0.50749,0.03634,0.13531],"tcp_to_object_dist_end":0.01439,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51246,0.03877,0.02553],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21311,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.15905,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11288.0,"raw_peak_contact_force":0.22517,"subtask_id":"lift_object","tcp_end":[0.49829,0.03818,0.0298],"tcp_start":[0.50695,0.03888,0.03927],"tcp_to_object_dist_end":0.01481,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51606,0.03918,0.16088],"object_pos_start":[0.51246,0.03877,0.02553],"object_to_goal_dist_end":0.17454,"object_to_goal_dist_start":0.21311,"object_z_max":0.16071,"peak_contact_force":0.08111,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":37865.0,"raw_peak_contact_force":0.66178,"subtask_id":"lift_object","tcp_end":[0.5059,0.03835,0.17315],"tcp_start":[0.49829,0.03818,0.0298],"tcp_to_object_dist_end":0.01595,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":388.0,"n_steps_budget":1000.0,"object_pos_end":[0.62595,0.16138,0.26741],"object_pos_start":[0.51606,0.03918,0.16088],"object_to_goal_dist_end":0.12291,"object_to_goal_dist_start":0.17454,"object_z_max":0.26715,"peak_contact_force":0.0891,"phase_name":"transport_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":13301.0,"raw_peak_contact_force":0.1416,"subtask_id":"transport_to_goal","tcp_end":[0.6126,0.15767,0.27988],"tcp_start":[0.5059,0.03835,0.17315],"tcp_to_object_dist_end":0.01864,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":148.0,"n_steps_budget":600.0,"object_pos_end":[0.63318,0.17191,0.21244],"object_pos_start":[0.62595,0.16138,0.26741],"object_to_goal_dist_end":0.06766,"object_to_goal_dist_start":0.12291,"object_z_max":0.26764,"peak_contact_force":0.09729,"phase_name":"align_over_goal","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":4422.0,"raw_peak_contact_force":0.32018,"subtask_id":"place_at_goal","tcp_end":[0.62073,0.16782,0.22718],"tcp_start":[0.6126,0.15767,0.27988],"tcp_to_object_dist_end":0.01972,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":149.0,"n_steps_budget":1000.0,"object_pos_end":[0.63422,0.17466,0.13383],"object_pos_start":[0.63318,0.17191,0.21244],"object_to_goal_dist_end":0.0132,"object_to_goal_dist_start":0.06766,"object_z_max":0.21244,"peak_contact_force":0.11145,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4219.0,"raw_peak_contact_force":0.27533,"subtask_id":"place_at_goal","tcp_end":[0.62223,0.1703,0.15098],"tcp_start":[0.62073,0.16782,0.22718],"tcp_to_object_dist_end":0.02138,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `28f75809d7d1d0a11ca1a36dd459ad950e5a80b6bae34006f33ac9620425f5e5`; realized-scene SHA-256: `f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.4827,0.04873,0.03]},{"name":"goal","value":[0.58187,0.22885,0.23048]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.4827,0.04873,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58187,0.22885,0.23048]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.25541,"average_solve_count":231.0,"average_success_count":231.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_over_goal.align_speed":0.03549,"align_over_goal.align_tolerance":0.0136,"align_over_goal.align_z_offset":0.08745,"approach_1.approach_speed":0.068,"approach_1.approach_z_offset":0.17048,"descend_1.descend_speed":0.06034,"descend_1.descend_z_offset":0.00503,"descend_to_place.descend_place_speed":0.0564,"descend_to_place.descend_place_z_offset":-0.00321,"descend_to_place.descend_tolerance":0.02227,"lift_1.lift_height":0.19065,"lift_1.lift_speed":0.06618,"transport_above_goal.transport_height":0.10065,"transport_above_goal.transport_speed":0.1282,"transport_above_goal.transport_tolerance":0.02312},"optimized_scores":{"best_composite_score":0.07705,"best_fitness_score":0.97705,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":165.0,"contact_point_centroid":[0.47848,0.04562,-0.00121],"force_p95":0.38295,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57896,"mean_force":0.09278,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4681,0.04679,0.03313]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17010.0,"contact_point_centroid":[0.4692,0.06594,0.08756],"force_p95":0.08423,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30095,"mean_force":0.05825,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46942,0.04675,0.08486]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1668.0,"contact_point_centroid":[0.57097,0.24035,0.2865],"force_p95":0.08966,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29532,"mean_force":0.0667,"phase_index":6.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57553,0.22192,0.28326]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":21001.0,"contact_point_centroid":[0.47132,0.02783,0.08572],"force_p95":0.07745,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27525,"mean_force":0.04849,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46938,0.04675,0.08424]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":324.0,"contact_point_centroid":[0.5684,0.23672,0.31569],"force_p95":0.11729,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25158,"mean_force":0.07254,"phase_index":5.0,"phase_name":"align_over_goal","phase_type":"align","tcp_position_centroid":[0.57397,0.21855,0.31226]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48279,0.04864,-0.00216],"force_p95":0.16686,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2323,"mean_force":0.1344,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4707,0.04707,0.0324]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2030.0,"contact_point_centroid":[0.5831,0.20459,0.28313],"force_p95":0.08382,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20764,"mean_force":0.05693,"phase_index":6.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57553,0.22191,0.28332]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5089.0,"contact_point_centroid":[0.47128,0.02795,0.03246],"force_p95":0.07067,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19291,"mean_force":0.04249,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4695,0.04695,0.03119]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":420.0,"contact_point_centroid":[0.58012,0.20071,0.3121],"force_p95":0.08465,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18309,"mean_force":0.05514,"phase_index":5.0,"phase_name":"align_over_goal","phase_type":"align","tcp_position_centroid":[0.57398,0.21855,0.31226]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13874.0,"contact_point_centroid":[0.52766,0.11477,0.22539],"force_p95":0.07931,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16024,"mean_force":0.05236,"phase_index":4.0,"phase_name":"transport_above_goal","phase_type":"approach","tcp_position_centroid":[0.52259,0.13304,0.22455]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11744.0,"contact_point_centroid":[0.51964,0.15156,0.22737],"force_p95":0.08904,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15014,"mean_force":0.06021,"phase_index":4.0,"phase_name":"transport_above_goal","phase_type":"approach","tcp_position_centroid":[0.52242,0.13276,0.22426]},{"body_a":"world","body_b":"grasp_target","contact_count":1332.0,"contact_point_centroid":[0.4827,0.04873,-0.0019],"force_p95":0.13564,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12299,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49019,0.02022,0.2542]},{"body_a":"world","body_b":"grasp_target","contact_count":2272.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47838,0.04484,0.12312]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4241.0,"contact_point_centroid":[0.46938,0.06628,0.03363],"force_p95":0.08681,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09704,"mean_force":0.05199,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4695,0.04695,0.03119]}],"total_contact_groups":14},"final_pose_error":0.0222,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.58712,0.22966,0.23096],"final_tcp_position":[0.57735,0.22491,0.24865],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":18.8876,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":334.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":18.8876,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1332.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.48162,0.04219,0.20796],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.18206,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":568.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2272.0,"raw_peak_contact_force":0.12263,"subtask_id":"approach_object","tcp_end":[0.47785,0.04776,0.03972],"tcp_start":[0.48162,0.04219,0.20796],"tcp_to_object_dist_end":0.01457,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48272,0.04763,0.02546],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29105,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.16344,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11130.0,"raw_peak_contact_force":0.2323,"subtask_id":"lift_object","tcp_end":[0.46947,0.04695,0.03116],"tcp_start":[0.47785,0.04776,0.03972],"tcp_to_object_dist_end":0.01444,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48249,0.04788,0.1257],"object_pos_start":[0.48272,0.04763,0.02546],"object_to_goal_dist_end":0.23153,"object_to_goal_dist_start":0.29105,"object_z_max":0.12558,"peak_contact_force":0.08091,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":38176.0,"raw_peak_contact_force":0.57896,"subtask_id":"lift_object","tcp_end":[0.4735,0.04697,0.1389],"tcp_start":[0.46947,0.04695,0.03116],"tcp_to_object_dist_end":0.016,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":706.0,"n_steps_budget":1000.0,"object_pos_end":[0.5834,0.22218,0.29694],"object_pos_start":[0.48249,0.04788,0.1257],"object_to_goal_dist_end":0.0668,"object_to_goal_dist_start":0.23153,"object_z_max":0.29673,"peak_contact_force":0.09081,"phase_name":"transport_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":25618.0,"raw_peak_contact_force":0.16024,"subtask_id":"transport_to_goal","tcp_end":[0.57386,0.21782,0.31257],"tcp_start":[0.4735,0.04697,0.1389],"tcp_to_object_dist_end":0.01883,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.58428,0.22404,0.2956],"object_pos_start":[0.5834,0.22218,0.29694],"object_to_goal_dist_end":0.06533,"object_to_goal_dist_start":0.0668,"object_z_max":0.29702,"peak_contact_force":0.0948,"phase_name":"align_over_goal","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":744.0,"raw_peak_contact_force":0.25158,"subtask_id":"place_at_goal","tcp_end":[0.5745,0.21951,0.31154],"tcp_start":[0.57386,0.21782,0.31257],"tcp_to_object_dist_end":0.01924,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":113.0,"n_steps_budget":1000.0,"object_pos_end":[0.58712,0.22966,0.23096],"object_pos_start":[0.58428,0.22404,0.2956],"object_to_goal_dist_end":0.00533,"object_to_goal_dist_start":0.06533,"object_z_max":0.2956,"peak_contact_force":0.08842,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3698.0,"raw_peak_contact_force":0.29532,"subtask_id":"place_at_goal","tcp_end":[0.57735,0.22491,0.24865],"tcp_start":[0.5745,0.21951,0.31154],"tcp_to_object_dist_end":0.02075,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```