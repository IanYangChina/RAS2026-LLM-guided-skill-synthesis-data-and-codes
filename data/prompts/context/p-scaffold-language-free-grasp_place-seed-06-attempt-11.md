## Search State

- **Seed**: 6
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → descend → grasp → lift → approach → align → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 15 | 0.0764 | 1.00 | ✅ accepted |
| 10 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 11 | -0.0894 | 0.28 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 11 | -0.0782 | 0.29 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 11 | -0.0744 | 0.30 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | 8 | 0.0508 | 0.19 | ❌ rejected |

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

## Current Skill (Q=0.076) — your mutation base

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

- **Composite score**: 0.076
- **task_score** (E): 1.000
- **fitness_score**: 0.976  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.900

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1029 |
| descend_1 | 1.00 | 1.00 | 0.1638 |
| grasp_1 | 1.00 | 1.00 | 0.0125 |
| lift_1 | 0.33 | 1.00 | 0.1229 |
| transport_above_goal | 1.00 | 1.00 | 0.2633 |
| align_over_goal | 1.00 | 1.00 | 0.0333 |
| descend_to_place | 1.00 | 1.00 | 0.0674 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, 0.021, 0.204) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.496, 0.021, 0.204)→(0.495, 0.024, 0.041) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.495, 0.024, 0.041)→(0.486, 0.023, 0.032) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.272 | 1.00 / 42.333 | 0.152 | 0.205 |
| lift_1 | lift | 0.33 / step_budget | (0.486, 0.023, 0.032)→(0.491, 0.023, 0.154) | (0.500, 0.024, 0.026)→(0.501, 0.024, 0.141) | 0.272→0.218 | 1.00 / 37.000 | 0.080 | 0.602 |
| transport_above_goal | approach | 1.00 / step_budget | (0.491, 0.023, 0.154)→(0.588, 0.181, 0.337) | (0.501, 0.024, 0.141)→(0.600, 0.185, 0.323) | 0.218→0.116 | 1.00 / 33.333 | 0.086 | 0.166 |
| align_over_goal | align | 1.00 / step_budget | (0.588, 0.181, 0.337)→(0.593, 0.190, 0.307) | (0.600, 0.185, 0.323)→(0.604, 0.194, 0.291) | 0.116→0.084 | 1.00 / 32.333 | 0.095 | 0.300 |
| descend_to_place | descend | 1.00 / step_budget | (0.593, 0.190, 0.307)→(0.595, 0.193, 0.240) | (0.604, 0.194, 0.291)→(0.606, 0.198, 0.222) | 0.084→0.017 | 1.00 / 30.000 | 0.103 | 0.246 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.166
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.548
- phase_breakdown.approach_object_score: 0.163
- phase_breakdown.transport_to_goal_score: 0.665
- phase_breakdown.lift_object_score: 0.372
- phase_breakdown.place_at_goal_score: 0.804
- grasp_place_fitness: 0.977

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.977
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.077
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Parameters at lower bound**: descend_1.descend_z_offset
- **Final σ (mean)**: 0.304


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.44622,"average_solve_count":251.0,"average_success_count":251.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_over_goal.align_speed":0.05115,"align_over_goal.align_tolerance":0.01615,"align_over_goal.align_z_offset":0.06911,"approach_1.approach_speed":0.0484,"approach_1.approach_z_offset":0.14089,"descend_1.descend_speed":0.07668,"descend_1.descend_z_offset":0.00837,"descend_to_place.descend_place_speed":0.05804,"descend_to_place.descend_place_z_offset":-0.00113,"descend_to_place.descend_tolerance":0.03513,"lift_1.lift_height":0.17691,"lift_1.lift_speed":0.07638,"transport_above_goal.transport_height":0.1837,"transport_above_goal.transport_speed":0.13639,"transport_above_goal.transport_tolerance":0.03698},"optimized_scores":{"best_composite_score":0.07526,"best_fitness_score":0.97526,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":159.0,"contact_point_centroid":[0.49947,-0.01531,-0.00116],"force_p95":0.36625,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.56922,"mean_force":0.09421,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48865,-0.0154,0.03494]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2500.0,"contact_point_centroid":[0.57835,0.19429,0.37033],"force_p95":0.08785,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31957,"mean_force":0.06461,"phase_index":5.0,"phase_name":"align_over_goal","phase_type":"align","tcp_position_centroid":[0.58057,0.17568,0.36803]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20762.0,"contact_point_centroid":[0.49202,0.00355,0.09443],"force_p95":0.07299,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3034,"mean_force":0.04922,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49094,-0.01551,0.09256]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18508.0,"contact_point_centroid":[0.49119,-0.03468,0.09524],"force_p95":0.07844,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29965,"mean_force":0.05409,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49092,-0.01551,0.09253]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":804.0,"contact_point_centroid":[0.59193,0.16607,0.31039],"force_p95":0.11969,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2817,"mean_force":0.08365,"phase_index":6.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.58343,0.18334,0.30973]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":944.0,"contact_point_centroid":[0.58239,0.20207,0.31363],"force_p95":0.10523,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22073,"mean_force":0.07184,"phase_index":6.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.5834,0.18329,0.31074]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1963.0,"contact_point_centroid":[0.58793,0.15783,0.37039],"force_p95":0.11378,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21418,"mean_force":0.08287,"phase_index":5.0,"phase_name":"align_over_goal","phase_type":"align","tcp_position_centroid":[0.5805,0.17548,0.36927]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8698.0,"contact_point_centroid":[0.53811,0.05402,0.27237],"force_p95":0.08742,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18611,"mean_force":0.05779,"phase_index":4.0,"phase_name":"transport_above_goal","phase_type":"approach","tcp_position_centroid":[0.53443,0.07261,0.27085]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8263.0,"contact_point_centroid":[0.53439,0.09353,0.27571],"force_p95":0.08792,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16639,"mean_force":0.06002,"phase_index":4.0,"phase_name":"transport_above_goal","phase_type":"approach","tcp_position_centroid":[0.53529,0.07454,0.27339]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50381,-0.01576,-0.00203],"force_p95":0.13254,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15981,"mean_force":0.1252,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49128,-0.01542,0.03479]},{"body_a":"world","body_b":"grasp_target","contact_count":1604.0,"contact_point_centroid":[0.50382,-0.01567,-0.00191],"force_p95":0.13462,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12293,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49886,-0.00669,0.24036]},{"body_a":"world","body_b":"grasp_target","contact_count":1744.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49779,-0.01466,0.11055]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5329.0,"contact_point_centroid":[0.49081,0.00366,0.03544],"force_p95":0.06673,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09496,"mean_force":0.04109,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49005,-0.0154,0.0335]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4146.0,"contact_point_centroid":[0.48951,-0.03467,0.03609],"force_p95":0.07903,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09348,"mean_force":0.05186,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49005,-0.0154,0.0335]}],"total_contact_groups":14},"final_pose_error":0.03485,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.59761,0.18934,0.26234],"final_tcp_position":[0.58412,0.18465,0.28161],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":0.56922,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":402.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1604.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.49978,-0.0139,0.17965],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1537,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":436.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1744.0,"raw_peak_contact_force":0.12263,"subtask_id":"approach_object","tcp_end":[0.49858,-0.01547,0.04264],"tcp_start":[0.49978,-0.0139,0.17965],"tcp_to_object_dist_end":0.01742,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50369,-0.01579,0.02588],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31244,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13261,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11275.0,"raw_peak_contact_force":0.15981,"subtask_id":"lift_object","tcp_end":[0.49002,-0.0154,0.03346],"tcp_start":[0.49858,-0.01547,0.04264],"tcp_to_object_dist_end":0.01563,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50549,-0.01595,0.14219],"object_pos_start":[0.50369,-0.01579,0.02588],"object_to_goal_dist_end":0.24335,"object_to_goal_dist_start":0.31244,"object_z_max":0.14207,"peak_contact_force":0.07931,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":39429.0,"raw_peak_contact_force":0.56922,"subtask_id":"lift_object","tcp_end":[0.49646,-0.01565,0.15673],"tcp_start":[0.49002,-0.0154,0.03346],"tcp_to_object_dist_end":0.01712,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":488.0,"n_steps_budget":1000.0,"object_pos_end":[0.59384,0.17411,0.38679],"object_pos_start":[0.50549,-0.01595,0.14219],"object_to_goal_dist_end":0.13948,"object_to_goal_dist_start":0.24335,"object_z_max":0.38632,"peak_contact_force":0.08998,"phase_name":"transport_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":16961.0,"raw_peak_contact_force":0.18611,"subtask_id":"transport_to_goal","tcp_end":[0.57876,0.16971,0.40063],"tcp_start":[0.49646,-0.01565,0.15673],"tcp_to_object_dist_end":0.02094,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":158.0,"n_steps_budget":1000.0,"object_pos_end":[0.59669,0.18643,0.31435],"object_pos_start":[0.59384,0.17411,0.38679],"object_to_goal_dist_end":0.06696,"object_to_goal_dist_start":0.13948,"object_z_max":0.38736,"peak_contact_force":0.11458,"phase_name":"align_over_goal","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":4463.0,"raw_peak_contact_force":0.31957,"subtask_id":"place_at_goal","tcp_end":[0.58313,0.18224,0.33184],"tcp_start":[0.57876,0.16971,0.40063],"tcp_to_object_dist_end":0.02252,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":67.0,"n_steps_budget":1000.0,"object_pos_end":[0.59761,0.18934,0.26234],"object_pos_start":[0.59669,0.18643,0.31435],"object_to_goal_dist_end":0.0179,"object_to_goal_dist_start":0.06696,"object_z_max":0.31435,"peak_contact_force":0.11042,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1748.0,"raw_peak_contact_force":0.2817,"subtask_id":"place_at_goal","tcp_end":[0.58412,0.18465,0.28161],"tcp_start":[0.58313,0.18224,0.33184],"tcp_to_object_dist_end":0.02399,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.44344,"average_solve_count":221.0,"average_success_count":221.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_over_goal.align_speed":0.04995,"align_over_goal.align_tolerance":0.01649,"align_over_goal.align_z_offset":0.10341,"approach_1.approach_speed":0.04975,"approach_1.approach_z_offset":0.18843,"descend_1.descend_speed":0.0974,"descend_1.descend_z_offset":0.0055,"descend_to_place.descend_place_speed":0.05108,"descend_to_place.descend_place_z_offset":-0.00286,"descend_to_place.descend_tolerance":0.03518,"lift_1.lift_height":0.19933,"lift_1.lift_speed":0.08975,"transport_above_goal.transport_height":0.14843,"transport_above_goal.transport_speed":0.12742,"transport_above_goal.transport_tolerance":0.02525},"optimized_scores":{"best_composite_score":0.07674,"best_fitness_score":0.97674,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":164.0,"contact_point_centroid":[0.50945,0.03754,-0.00124],"force_p95":0.42949,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65479,"mean_force":0.09207,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49719,0.03807,0.03221]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17000.0,"contact_point_centroid":[0.50011,0.05729,0.10384],"force_p95":0.08309,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33655,"mean_force":0.05868,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49986,0.03809,0.10107]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20702.0,"contact_point_centroid":[0.50164,0.01916,0.10127],"force_p95":0.07831,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30908,"mean_force":0.04958,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49975,0.03809,0.09966]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":792.0,"contact_point_centroid":[0.61181,0.18126,0.27291],"force_p95":0.07771,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27563,"mean_force":0.05763,"phase_index":5.0,"phase_name":"align_over_goal","phase_type":"align","tcp_position_centroid":[0.61663,0.1628,0.26914]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1798.0,"contact_point_centroid":[0.61616,0.18576,0.22659],"force_p95":0.08503,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24435,"mean_force":0.06031,"phase_index":6.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62018,0.16716,0.22275]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51258,0.03966,-0.00214],"force_p95":0.16144,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22289,"mean_force":0.13277,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49993,0.03831,0.0317]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2246.0,"contact_point_centroid":[0.62454,0.14867,0.22224],"force_p95":0.07535,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21776,"mean_force":0.05045,"phase_index":6.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62021,0.16719,0.22218]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":940.0,"contact_point_centroid":[0.62051,0.14407,0.27023],"force_p95":0.07225,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20977,"mean_force":0.04882,"phase_index":5.0,"phase_name":"align_over_goal","phase_type":"align","tcp_position_centroid":[0.61661,0.16277,0.26923]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5023.0,"contact_point_centroid":[0.50034,0.0192,0.03185],"force_p95":0.07383,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1743,"mean_force":0.04301,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49869,0.03821,0.03036]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9636.0,"contact_point_centroid":[0.56455,0.0829,0.22583],"force_p95":0.07839,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15857,"mean_force":0.05053,"phase_index":4.0,"phase_name":"transport_above_goal","phase_type":"approach","tcp_position_centroid":[0.56112,0.1016,0.22469]},{"body_a":"world","body_b":"grasp_target","contact_count":1192.0,"contact_point_centroid":[0.51251,0.03972,-0.00189],"force_p95":0.13623,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12304,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50265,0.01615,0.2623]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7938.0,"contact_point_centroid":[0.55846,0.11992,0.22731],"force_p95":0.0895,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13821,"mean_force":0.0599,"phase_index":4.0,"phase_name":"transport_above_goal","phase_type":"approach","tcp_position_centroid":[0.56057,0.101,0.22418]},{"body_a":"world","body_b":"grasp_target","contact_count":2272.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50613,0.0362,0.1314]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4229.0,"contact_point_centroid":[0.49896,0.05752,0.03308],"force_p95":0.08319,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09287,"mean_force":0.05185,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49869,0.03821,0.03036]}],"total_contact_groups":14},"final_pose_error":0.03509,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.63074,0.17271,0.15996],"final_tcp_position":[0.62236,0.16937,0.17673],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":0.65479,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":299.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1192.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.50747,0.03371,0.22462],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.19876,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":568.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2272.0,"raw_peak_contact_force":0.12263,"subtask_id":"approach_object","tcp_end":[0.50732,0.0389,0.0398],"tcp_start":[0.50747,0.03371,0.22462],"tcp_to_object_dist_end":0.01475,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51248,0.03878,0.02553],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21309,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.15874,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11052.0,"raw_peak_contact_force":0.22289,"subtask_id":"lift_object","tcp_end":[0.49866,0.0382,0.03032],"tcp_start":[0.50732,0.0389,0.0398],"tcp_to_object_dist_end":0.01465,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51546,0.03917,0.16174],"object_pos_start":[0.51248,0.03878,0.02553],"object_to_goal_dist_end":0.17501,"object_to_goal_dist_start":0.21309,"object_z_max":0.16157,"peak_contact_force":0.08098,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":37866.0,"raw_peak_contact_force":0.65479,"subtask_id":"lift_object","tcp_end":[0.5055,0.03834,0.17448],"tcp_start":[0.49866,0.0382,0.03032],"tcp_to_object_dist_end":0.0162,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":468.0,"n_steps_budget":1000.0,"object_pos_end":[0.62057,0.16267,0.25984],"object_pos_start":[0.51546,0.03917,0.16174],"object_to_goal_dist_end":0.11545,"object_to_goal_dist_start":0.17501,"object_z_max":0.25966,"peak_contact_force":0.07745,"phase_name":"transport_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":17574.0,"raw_peak_contact_force":0.15857,"subtask_id":"transport_to_goal","tcp_end":[0.61504,0.16058,0.27522],"tcp_start":[0.5055,0.03834,0.17448],"tcp_to_object_dist_end":0.01648,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":44.0,"n_steps_budget":600.0,"object_pos_end":[0.62632,0.16808,0.24478],"object_pos_start":[0.62057,0.16267,0.25984],"object_to_goal_dist_end":0.09986,"object_to_goal_dist_start":0.11545,"object_z_max":0.25991,"peak_contact_force":0.07632,"phase_name":"align_over_goal","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1732.0,"raw_peak_contact_force":0.27563,"subtask_id":"place_at_goal","tcp_end":[0.61898,0.1654,0.26013],"tcp_start":[0.61504,0.16058,0.27522],"tcp_to_object_dist_end":0.01722,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":106.0,"n_steps_budget":1000.0,"object_pos_end":[0.63074,0.17271,0.15996],"object_pos_start":[0.62632,0.16808,0.24478],"object_to_goal_dist_end":0.01527,"object_to_goal_dist_start":0.09986,"object_z_max":0.24478,"peak_contact_force":0.08793,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4044.0,"raw_peak_contact_force":0.24435,"subtask_id":"place_at_goal","tcp_end":[0.62236,0.16937,0.17673],"tcp_start":[0.61898,0.1654,0.26013],"tcp_to_object_dist_end":0.01904,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.24436,"average_solve_count":266.0,"average_success_count":266.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_over_goal.align_speed":0.05662,"align_over_goal.align_tolerance":0.01022,"align_over_goal.align_z_offset":0.10495,"approach_1.approach_speed":0.09152,"approach_1.approach_z_offset":0.17152,"descend_1.descend_speed":0.05691,"descend_1.descend_z_offset":0.005,"descend_to_place.descend_place_speed":0.03188,"descend_to_place.descend_place_z_offset":0.00439,"descend_to_place.descend_tolerance":0.02659,"lift_1.lift_height":0.20892,"lift_1.lift_speed":0.06132,"transport_above_goal.transport_height":0.13285,"transport_above_goal.transport_speed":0.11378,"transport_above_goal.transport_tolerance":0.03499},"optimized_scores":{"best_composite_score":0.07718,"best_fitness_score":0.97718,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":185.0,"contact_point_centroid":[0.47839,0.0457,-0.00122],"force_p95":0.36194,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.58161,"mean_force":0.09499,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46796,0.04679,0.03292]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1232.0,"contact_point_centroid":[0.5697,0.23631,0.33503],"force_p95":0.09617,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30483,"mean_force":0.07354,"phase_index":5.0,"phase_name":"align_over_goal","phase_type":"align","tcp_position_centroid":[0.57373,0.21778,0.33193]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17000.0,"contact_point_centroid":[0.46857,0.06592,0.08381],"force_p95":0.08419,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30226,"mean_force":0.05825,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46877,0.04672,0.08112]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":21005.0,"contact_point_centroid":[0.47069,0.02781,0.08201],"force_p95":0.07749,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27343,"mean_force":0.04847,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46873,0.04672,0.08052]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48279,0.04864,-0.00216],"force_p95":0.16666,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23229,"mean_force":0.13434,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4707,0.04708,0.0322]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1408.0,"contact_point_centroid":[0.58222,0.20079,0.33204],"force_p95":0.09103,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21737,"mean_force":0.06575,"phase_index":5.0,"phase_name":"align_over_goal","phase_type":"align","tcp_position_centroid":[0.57373,0.21778,0.33193]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1427.0,"contact_point_centroid":[0.5733,0.24284,0.30303],"force_p95":0.10799,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21315,"mean_force":0.07756,"phase_index":6.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57714,0.22427,0.29982]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5088.0,"contact_point_centroid":[0.47128,0.02796,0.03225],"force_p95":0.07072,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19263,"mean_force":0.0425,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4695,0.04696,0.03098]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1792.0,"contact_point_centroid":[0.58607,0.20759,0.29873],"force_p95":0.08559,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1912,"mean_force":0.06212,"phase_index":6.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57717,0.22432,0.29851]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8998.0,"contact_point_centroid":[0.52437,0.10913,0.22997],"force_p95":0.08426,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15265,"mean_force":0.05426,"phase_index":4.0,"phase_name":"transport_above_goal","phase_type":"approach","tcp_position_centroid":[0.51915,0.12733,0.2291]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7623.0,"contact_point_centroid":[0.51662,0.14591,0.23165],"force_p95":0.08966,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14436,"mean_force":0.06145,"phase_index":4.0,"phase_name":"transport_above_goal","phase_type":"approach","tcp_position_centroid":[0.51896,0.12701,0.2287]},{"body_a":"world","body_b":"grasp_target","contact_count":1272.0,"contact_point_centroid":[0.4827,0.04873,-0.0019],"force_p95":0.13583,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12301,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49023,0.02023,0.25465]},{"body_a":"world","body_b":"grasp_target","contact_count":2312.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47837,0.04486,0.12332]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4240.0,"contact_point_centroid":[0.46938,0.06629,0.03343],"force_p95":0.08684,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09684,"mean_force":0.052,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4695,0.04696,0.03099]}],"total_contact_groups":14},"final_pose_error":0.02617,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.59094,0.23208,0.24412],"final_tcp_position":[0.57831,0.22607,0.26065],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":0.58161,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":319.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1272.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.48162,0.04221,0.20882],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.18292,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":578.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2312.0,"raw_peak_contact_force":0.12263,"subtask_id":"approach_object","tcp_end":[0.47784,0.04777,0.03951],"tcp_start":[0.48162,0.04221,0.20882],"tcp_to_object_dist_end":0.01437,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48272,0.04763,0.02546],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29105,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.16326,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11128.0,"raw_peak_contact_force":0.23229,"subtask_id":"lift_object","tcp_end":[0.46947,0.04696,0.03095],"tcp_start":[0.47784,0.04777,0.03951],"tcp_to_object_dist_end":0.01436,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48124,0.04782,0.11868],"object_pos_start":[0.48272,0.04763,0.02546],"object_to_goal_dist_end":0.23538,"object_to_goal_dist_start":0.29105,"object_z_max":0.11857,"peak_contact_force":0.08031,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":38190.0,"raw_peak_contact_force":0.58161,"subtask_id":"lift_object","tcp_end":[0.47224,0.04691,0.13174],"tcp_start":[0.46947,0.04696,0.03095],"tcp_to_object_dist_end":0.01589,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":469.0,"n_steps_budget":1000.0,"object_pos_end":[0.58513,0.21762,0.32258],"object_pos_start":[0.48124,0.04782,0.11868],"object_to_goal_dist_end":0.09284,"object_to_goal_dist_start":0.23538,"object_z_max":0.32218,"peak_contact_force":0.08939,"phase_name":"transport_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":16621.0,"raw_peak_contact_force":0.15265,"subtask_id":"transport_to_goal","tcp_end":[0.57101,0.21221,0.33521],"tcp_start":[0.47224,0.04691,0.13174],"tcp_to_object_dist_end":0.0197,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":88.0,"n_steps_budget":600.0,"object_pos_end":[0.58995,0.22846,0.31515],"object_pos_start":[0.58513,0.21762,0.32258],"object_to_goal_dist_end":0.08505,"object_to_goal_dist_start":0.09284,"object_z_max":0.3231,"peak_contact_force":0.09261,"phase_name":"align_over_goal","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":2640.0,"raw_peak_contact_force":0.30483,"subtask_id":"place_at_goal","tcp_end":[0.57665,0.22292,0.32898],"tcp_start":[0.57101,0.21221,0.33521],"tcp_to_object_dist_end":0.01997,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":112.0,"n_steps_budget":1000.0,"object_pos_end":[0.59094,0.23208,0.24412],"object_pos_start":[0.58995,0.22846,0.31515],"object_to_goal_dist_end":0.01669,"object_to_goal_dist_start":0.08505,"object_z_max":0.31515,"peak_contact_force":0.1101,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3219.0,"raw_peak_contact_force":0.21315,"subtask_id":"place_at_goal","tcp_end":[0.57831,0.22607,0.26065],"tcp_start":[0.57665,0.22292,0.32898],"tcp_to_object_dist_end":0.02166,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```