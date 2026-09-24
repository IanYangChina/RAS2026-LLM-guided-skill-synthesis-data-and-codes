## Search State

- **Seed**: 6
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → descend → grasp → lift → approach → align → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 15 | 0.0766 | 1.00 | ✅ accepted |
| 13 | approach → descend → grasp → lift → approach → align → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 15 | 0.0754 | 1.00 | ❌ rejected |
| 12 | approach → descend → grasp → lift → approach → align → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 15 | 0.0759 | 1.00 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → align → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 15 | 0.0764 | 1.00 | ✅ accepted |
| 10 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 11 | -0.0894 | 0.28 | ❌ rejected |

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

## Current Skill (Q=0.077) — your mutation base

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

- **Composite score**: 0.077
- **task_score** (E): 1.000
- **fitness_score**: 0.977  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.900

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1466 |
| descend_1 | 1.00 | 1.00 | 0.1194 |
| grasp_1 | 1.00 | 1.00 | 0.0125 |
| lift_1 | 0.00 | 1.00 | 0.1162 |
| transport_above_goal | 1.00 | 1.00 | 0.2520 |
| align_over_goal | 1.00 | 1.00 | 0.0226 |
| descend_to_place | 1.00 | 1.00 | 0.0848 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, 0.021, 0.159) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.496, 0.021, 0.159)→(0.494, 0.024, 0.040) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.494, 0.024, 0.040)→(0.486, 0.023, 0.031) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.272 | 1.00 / 42.333 | 0.151 | 0.205 |
| lift_1 | lift | 0.00 / step_budget | (0.486, 0.023, 0.031)→(0.490, 0.023, 0.147) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.134) | 0.272→0.219 | 1.00 / 37.000 | 0.080 | 0.599 |
| transport_above_goal | approach | 1.00 / step_budget | (0.490, 0.023, 0.147)→(0.585, 0.175, 0.320) | (0.500, 0.024, 0.134)→(0.600, 0.179, 0.308) | 0.219→0.102 | 1.00 / 31.667 | 0.093 | 0.169 |
| align_over_goal | align | 1.00 / step_budget | (0.585, 0.175, 0.320)→(0.591, 0.185, 0.303) | (0.600, 0.179, 0.308)→(0.607, 0.190, 0.291) | 0.102→0.083 | 1.00 / 27.667 | 0.103 | 0.320 |
| descend_to_place | descend | 1.00 / step_budget | (0.591, 0.185, 0.303)→(0.594, 0.193, 0.219) | (0.607, 0.190, 0.291)→(0.607, 0.198, 0.202) | 0.083→0.011 | 1.00 / 27.000 | 0.112 | 0.368 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.245
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.562
- phase_breakdown.approach_object_score: 0.163
- phase_breakdown.transport_to_goal_score: 0.539
- phase_breakdown.lift_object_score: 0.597
- phase_breakdown.place_at_goal_score: 0.826
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
- **Final σ (mean)**: 0.296


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.18246,"average_solve_count":285.0,"average_success_count":285.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_over_goal.align_speed":0.06779,"align_over_goal.align_tolerance":0.02415,"align_over_goal.align_z_offset":0.0846,"approach_1.approach_speed":0.07577,"approach_1.approach_z_offset":0.07925,"descend_1.descend_speed":0.04676,"descend_1.descend_z_offset":0.00636,"descend_to_place.descend_place_speed":0.02523,"descend_to_place.descend_place_z_offset":0.00364,"descend_to_place.descend_tolerance":0.01463,"lift_1.lift_height":0.18825,"lift_1.lift_speed":0.05987,"transport_above_goal.transport_height":0.16255,"transport_above_goal.transport_speed":0.13107,"transport_above_goal.transport_tolerance":0.04971},"optimized_scores":{"best_composite_score":0.07618,"best_fitness_score":0.97618,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":183.0,"contact_point_centroid":[0.49935,-0.01538,-0.00111],"force_p95":0.35555,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.52972,"mean_force":0.09588,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48816,-0.01538,0.03289]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":611.0,"contact_point_centroid":[0.57715,0.18675,0.36644],"force_p95":0.15238,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35527,"mean_force":0.08499,"phase_index":5.0,"phase_name":"align_over_goal","phase_type":"align","tcp_position_centroid":[0.57773,0.16773,0.36277]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":572.0,"contact_point_centroid":[0.58644,0.15054,0.36594],"force_p95":0.13307,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30533,"mean_force":0.08537,"phase_index":5.0,"phase_name":"align_over_goal","phase_type":"align","tcp_position_centroid":[0.57771,0.16768,0.36288]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2387.0,"contact_point_centroid":[0.58064,0.19723,0.31206],"force_p95":0.11458,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30214,"mean_force":0.08534,"phase_index":6.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.58087,0.17818,0.30888]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2333.0,"contact_point_centroid":[0.59068,0.16171,0.30892],"force_p95":0.11725,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28596,"mean_force":0.08716,"phase_index":6.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.58093,0.17836,0.30726]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20715.0,"contact_point_centroid":[0.49048,0.00358,0.07979],"force_p95":0.07353,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2647,"mean_force":0.04931,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48924,-0.01545,0.07797]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18059.0,"contact_point_centroid":[0.48973,-0.03463,0.08095],"force_p95":0.07931,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26128,"mean_force":0.05524,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48925,-0.01545,0.07827]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5941.0,"contact_point_centroid":[0.53367,0.04676,0.23696],"force_p95":0.09692,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18502,"mean_force":0.06153,"phase_index":4.0,"phase_name":"transport_above_goal","phase_type":"approach","tcp_position_centroid":[0.52974,0.06527,0.23561]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5647.0,"contact_point_centroid":[0.53079,0.08691,0.24132],"force_p95":0.09552,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1683,"mean_force":0.06308,"phase_index":4.0,"phase_name":"transport_above_goal","phase_type":"approach","tcp_position_centroid":[0.53097,0.06788,0.23915]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50381,-0.01576,-0.00203],"force_p95":0.13298,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16031,"mean_force":0.12522,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49094,-0.01539,0.03265]},{"body_a":"world","body_b":"grasp_target","contact_count":2280.0,"contact_point_centroid":[0.50382,-0.01567,-0.00194],"force_p95":0.13153,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12284,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49859,-0.00708,0.20905]},{"body_a":"world","body_b":"grasp_target","contact_count":1068.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49742,-0.01493,0.07898]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5325.0,"contact_point_centroid":[0.49057,0.00368,0.03335],"force_p95":0.0667,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09556,"mean_force":0.0411,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48971,-0.01538,0.03135]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4149.0,"contact_point_centroid":[0.48929,-0.03465,0.03402],"force_p95":0.07894,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09444,"mean_force":0.05184,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48971,-0.01538,0.03135]}],"total_contact_groups":14},"final_pose_error":0.01461,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.5965,0.18851,0.24718],"final_tcp_position":[0.58298,0.18367,0.26531],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":0.52972,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":571.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2280.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.49936,-0.01446,0.11799],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.09208,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":267.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1068.0,"raw_peak_contact_force":0.12263,"subtask_id":"approach_object","tcp_end":[0.49826,-0.01544,0.04045],"tcp_start":[0.49936,-0.01446,0.11799],"tcp_to_object_dist_end":0.01547,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50368,-0.01576,0.02588],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31243,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13304,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11274.0,"raw_peak_contact_force":0.16031,"subtask_id":"lift_object","tcp_end":[0.48968,-0.01538,0.03131],"tcp_start":[0.49826,-0.01544,0.04045],"tcp_to_object_dist_end":0.01502,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50264,-0.01587,0.11515],"object_pos_start":[0.50368,-0.01576,0.02588],"object_to_goal_dist_end":0.25714,"object_to_goal_dist_start":0.31243,"object_z_max":0.11504,"peak_contact_force":0.08141,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":38957.0,"raw_peak_contact_force":0.52972,"subtask_id":"lift_object","tcp_end":[0.49328,-0.01555,0.1283],"tcp_start":[0.48968,-0.01538,0.03131],"tcp_to_object_dist_end":0.01615,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":350.0,"n_steps_budget":1000.0,"object_pos_end":[0.59293,0.16744,0.35791],"object_pos_start":[0.50264,-0.01587,0.11515],"object_to_goal_dist_end":0.11177,"object_to_goal_dist_start":0.25714,"object_z_max":0.35723,"peak_contact_force":0.09708,"phase_name":"transport_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":11588.0,"raw_peak_contact_force":0.18502,"subtask_id":"transport_to_goal","tcp_end":[0.57583,0.16275,0.36915],"tcp_start":[0.49328,-0.01555,0.1283],"tcp_to_object_dist_end":0.02099,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":46.0,"n_steps_budget":600.0,"object_pos_end":[0.59893,0.17905,0.33914],"object_pos_start":[0.59293,0.16744,0.35791],"object_to_goal_dist_end":0.0922,"object_to_goal_dist_start":0.11177,"object_z_max":0.35919,"peak_contact_force":0.10349,"phase_name":"align_over_goal","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1183.0,"raw_peak_contact_force":0.35527,"subtask_id":"place_at_goal","tcp_end":[0.5801,0.17354,0.35085],"tcp_start":[0.57583,0.16275,0.36915],"tcp_to_object_dist_end":0.02285,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":204.0,"n_steps_budget":1000.0,"object_pos_end":[0.5965,0.18851,0.24718],"object_pos_start":[0.59893,0.17905,0.33914],"object_to_goal_dist_end":0.0097,"object_to_goal_dist_start":0.0922,"object_z_max":0.33914,"peak_contact_force":0.11162,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4720.0,"raw_peak_contact_force":0.30214,"subtask_id":"place_at_goal","tcp_end":[0.58298,0.18367,0.26531],"tcp_start":[0.5801,0.17354,0.35085],"tcp_to_object_dist_end":0.02312,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.26578,"average_solve_count":301.0,"average_success_count":301.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_over_goal.align_speed":0.07977,"align_over_goal.align_tolerance":0.01689,"align_over_goal.align_z_offset":0.07157,"approach_1.approach_speed":0.03924,"approach_1.approach_z_offset":0.15055,"descend_1.descend_speed":0.03976,"descend_1.descend_z_offset":0.00529,"descend_to_place.descend_place_speed":0.04951,"descend_to_place.descend_place_z_offset":-0.00373,"descend_to_place.descend_tolerance":0.01683,"lift_1.lift_height":0.18617,"lift_1.lift_speed":0.07769,"transport_above_goal.transport_height":0.13264,"transport_above_goal.transport_speed":0.07374,"transport_above_goal.transport_tolerance":0.02848},"optimized_scores":{"best_composite_score":0.07671,"best_fitness_score":0.97671,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":178.0,"contact_point_centroid":[0.50808,0.03723,-0.00125],"force_p95":0.39879,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64467,"mean_force":0.09942,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49701,0.03809,0.03173]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1810.0,"contact_point_centroid":[0.61831,0.18661,0.19665],"force_p95":0.1139,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.40852,"mean_force":0.08527,"phase_index":6.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61961,0.16759,0.19366]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17000.0,"contact_point_centroid":[0.49954,0.05729,0.09458],"force_p95":0.08315,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32868,"mean_force":0.05859,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49938,0.0381,0.09181]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":959.0,"contact_point_centroid":[0.61358,0.18095,0.24811],"force_p95":0.10363,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30714,"mean_force":0.07602,"phase_index":5.0,"phase_name":"align_over_goal","phase_type":"align","tcp_position_centroid":[0.61562,0.16207,0.24523]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20753.0,"contact_point_centroid":[0.50108,0.01916,0.09232],"force_p95":0.07783,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30155,"mean_force":0.04936,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49929,0.03809,0.09071]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2405.0,"contact_point_centroid":[0.62708,0.15028,0.19362],"force_p95":0.09585,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28446,"mean_force":0.06467,"phase_index":6.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61961,0.16759,0.19355]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1162.0,"contact_point_centroid":[0.6225,0.14441,0.24508],"force_p95":0.09188,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26147,"mean_force":0.06416,"phase_index":5.0,"phase_name":"align_over_goal","phase_type":"align","tcp_position_centroid":[0.61567,0.16213,0.24495]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51258,0.03966,-0.00213],"force_p95":0.16089,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22215,"mean_force":0.13261,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49979,0.03833,0.03139]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5024.0,"contact_point_centroid":[0.50023,0.01923,0.03155],"force_p95":0.07373,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17456,"mean_force":0.04301,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49855,0.03823,0.03004]},{"body_a":"world","body_b":"grasp_target","contact_count":1644.0,"contact_point_centroid":[0.51251,0.03972,-0.00192],"force_p95":0.13462,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12292,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50263,0.01698,0.24399]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8047.0,"contact_point_centroid":[0.56092,0.07886,0.20467],"force_p95":0.08492,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13008,"mean_force":0.055,"phase_index":4.0,"phase_name":"transport_above_goal","phase_type":"approach","tcp_position_centroid":[0.55669,0.09732,0.20386]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6876.0,"contact_point_centroid":[0.55561,0.11653,0.20675],"force_p95":0.09044,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12705,"mean_force":0.06193,"phase_index":4.0,"phase_name":"transport_above_goal","phase_type":"approach","tcp_position_centroid":[0.55687,0.09751,0.20403]},{"body_a":"world","body_b":"grasp_target","contact_count":2012.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50593,0.03693,0.11298]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4228.0,"contact_point_centroid":[0.49887,0.05755,0.03281],"force_p95":0.08312,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09271,"mean_force":0.05184,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49856,0.03823,0.03005]}],"total_contact_groups":14},"final_pose_error":0.01637,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.63462,0.17432,0.14001],"final_tcp_position":[0.62182,0.16982,0.15639],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":0.64467,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":412.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1644.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.5076,0.03517,0.18777],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16189,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":503.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2012.0,"raw_peak_contact_force":0.12263,"subtask_id":"approach_object","tcp_end":[0.50717,0.03893,0.03947],"tcp_start":[0.5076,0.03517,0.18777],"tcp_to_object_dist_end":0.01449,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51248,0.0388,0.02554],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21308,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.15829,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11052.0,"raw_peak_contact_force":0.22215,"subtask_id":"lift_object","tcp_end":[0.49852,0.03823,0.03001],"tcp_start":[0.50717,0.03893,0.03947],"tcp_to_object_dist_end":0.01467,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51446,0.03914,0.1439],"object_pos_start":[0.51248,0.0388,0.02554],"object_to_goal_dist_end":0.17489,"object_to_goal_dist_start":0.21308,"object_z_max":0.14377,"peak_contact_force":0.07956,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":37931.0,"raw_peak_contact_force":0.64467,"subtask_id":"lift_object","tcp_end":[0.50466,0.03832,0.15609],"tcp_start":[0.49852,0.03823,0.03001],"tcp_to_object_dist_end":0.01566,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":423.0,"n_steps_budget":1000.0,"object_pos_end":[0.62594,0.16233,0.24476],"object_pos_start":[0.51446,0.03914,0.1439],"object_to_goal_dist_end":0.10027,"object_to_goal_dist_start":0.17489,"object_z_max":0.24453,"peak_contact_force":0.08909,"phase_name":"transport_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":14923.0,"raw_peak_contact_force":0.13008,"subtask_id":"transport_to_goal","tcp_end":[0.6131,0.15867,0.2575],"tcp_start":[0.50466,0.03832,0.15609],"tcp_to_object_dist_end":0.01845,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":71.0,"n_steps_budget":600.0,"object_pos_end":[0.63305,0.17022,0.21557],"object_pos_start":[0.62594,0.16233,0.24476],"object_to_goal_dist_end":0.07079,"object_to_goal_dist_start":0.10027,"object_z_max":0.24494,"peak_contact_force":0.10406,"phase_name":"align_over_goal","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":2121.0,"raw_peak_contact_force":0.30714,"subtask_id":"place_at_goal","tcp_end":[0.61906,0.16591,0.22913],"tcp_start":[0.6131,0.15867,0.2575],"tcp_to_object_dist_end":0.01995,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":150.0,"n_steps_budget":1000.0,"object_pos_end":[0.63462,0.17432,0.14001],"object_pos_start":[0.63305,0.17022,0.21557],"object_to_goal_dist_end":0.00884,"object_to_goal_dist_start":0.07079,"object_z_max":0.21557,"peak_contact_force":0.11218,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4215.0,"raw_peak_contact_force":0.40852,"subtask_id":"place_at_goal","tcp_end":[0.62182,0.16982,0.15639],"tcp_start":[0.61906,0.16591,0.22913],"tcp_to_object_dist_end":0.02127,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.53077,"average_solve_count":260.0,"average_success_count":260.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_over_goal.align_speed":0.08648,"align_over_goal.align_tolerance":0.0159,"align_over_goal.align_z_offset":0.10271,"approach_1.approach_speed":0.07526,"approach_1.approach_z_offset":0.13364,"descend_1.descend_speed":0.05351,"descend_1.descend_z_offset":0.00502,"descend_to_place.descend_place_speed":0.03209,"descend_to_place.descend_place_z_offset":-0.00773,"descend_to_place.descend_tolerance":0.0132,"lift_1.lift_height":0.24913,"lift_1.lift_speed":0.07693,"transport_above_goal.transport_height":0.14223,"transport_above_goal.transport_speed":0.15186,"transport_above_goal.transport_tolerance":0.04999},"optimized_scores":{"best_composite_score":0.07701,"best_fitness_score":0.97701,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":166.0,"contact_point_centroid":[0.47869,0.04552,-0.00129],"force_p95":0.37589,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62248,"mean_force":0.09802,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46785,0.0468,0.03279]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3135.0,"contact_point_centroid":[0.57107,0.2388,0.28751],"force_p95":0.10897,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.39408,"mean_force":0.0794,"phase_index":6.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57459,0.22013,0.28443]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17000.0,"contact_point_centroid":[0.46872,0.06594,0.09557],"force_p95":0.08433,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32403,"mean_force":0.05847,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46885,0.04674,0.09287]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":825.0,"contact_point_centroid":[0.56552,0.22725,0.33524],"force_p95":0.11356,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29617,"mean_force":0.077,"phase_index":5.0,"phase_name":"align_over_goal","phase_type":"align","tcp_position_centroid":[0.56946,0.20878,0.33246]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20908.0,"contact_point_centroid":[0.47088,0.02783,0.09359],"force_p95":0.07824,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29598,"mean_force":0.04892,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46881,0.04674,0.09209]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3877.0,"contact_point_centroid":[0.58309,0.20351,0.28285],"force_p95":0.08687,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26347,"mean_force":0.06222,"phase_index":6.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57467,0.22027,0.28309]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":955.0,"contact_point_centroid":[0.57738,0.19161,0.3327],"force_p95":0.09894,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23686,"mean_force":0.0657,"phase_index":5.0,"phase_name":"align_over_goal","phase_type":"align","tcp_position_centroid":[0.56945,0.20876,0.33247]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48279,0.04864,-0.00216],"force_p95":0.16641,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23197,"mean_force":0.13425,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4706,0.04708,0.03224]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5015.0,"contact_point_centroid":[0.47133,0.02798,0.03229],"force_p95":0.07835,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19343,"mean_force":0.04311,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4694,0.04697,0.03102]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5077.0,"contact_point_centroid":[0.52152,0.10162,0.23884],"force_p95":0.09964,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19328,"mean_force":0.06021,"phase_index":4.0,"phase_name":"transport_above_goal","phase_type":"approach","tcp_position_centroid":[0.51607,0.11969,0.23811]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4333.0,"contact_point_centroid":[0.51452,0.13881,0.24075],"force_p95":0.10208,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18343,"mean_force":0.06658,"phase_index":4.0,"phase_name":"transport_above_goal","phase_type":"approach","tcp_position_centroid":[0.51616,0.11984,0.23829]},{"body_a":"world","body_b":"grasp_target","contact_count":1704.0,"contact_point_centroid":[0.4827,0.04873,-0.00192],"force_p95":0.13411,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12291,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48965,0.0211,0.23613]},{"body_a":"world","body_b":"grasp_target","contact_count":1820.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47783,0.04556,0.10512]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4239.0,"contact_point_centroid":[0.46932,0.0663,0.03349],"force_p95":0.08666,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09657,"mean_force":0.05198,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4694,0.04697,0.03103]}],"total_contact_groups":14},"final_pose_error":0.01294,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.58923,0.23109,0.2175],"final_tcp_position":[0.57752,0.22542,0.23446],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":0.62248,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":427.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1704.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.48077,0.04364,0.17174],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14582,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":455.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1820.0,"raw_peak_contact_force":0.12263,"subtask_id":"approach_object","tcp_end":[0.47774,0.04777,0.03955],"tcp_start":[0.48077,0.04364,0.17174],"tcp_to_object_dist_end":0.01444,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48272,0.04764,0.02546],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29104,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.16297,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11054.0,"raw_peak_contact_force":0.23197,"subtask_id":"lift_object","tcp_end":[0.46937,0.04696,0.03099],"tcp_start":[0.47774,0.04777,0.03955],"tcp_to_object_dist_end":0.01447,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48206,0.04789,0.14326],"object_pos_start":[0.48272,0.04764,0.02546],"object_to_goal_dist_end":0.22432,"object_to_goal_dist_start":0.29104,"object_z_max":0.14314,"peak_contact_force":0.08013,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":38074.0,"raw_peak_contact_force":0.62248,"subtask_id":"lift_object","tcp_end":[0.47264,0.04695,0.15627],"tcp_start":[0.46937,0.04696,0.03099],"tcp_to_object_dist_end":0.01609,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":34.0,"n_steps":279.0,"n_steps_budget":1000.0,"object_pos_end":[0.57988,0.20725,0.32196],"object_pos_start":[0.48206,0.04789,0.14326],"object_to_goal_dist_end":0.09401,"object_to_goal_dist_start":0.22432,"object_z_max":0.32134,"peak_contact_force":0.09175,"phase_name":"transport_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9410.0,"raw_peak_contact_force":0.19328,"subtask_id":"transport_to_goal","tcp_end":[0.56635,0.20237,0.33409],"tcp_start":[0.47264,0.04695,0.15627],"tcp_to_object_dist_end":0.01881,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":57.0,"n_steps_budget":600.0,"object_pos_end":[0.58789,0.22185,0.31696],"object_pos_start":[0.57988,0.20725,0.32196],"object_to_goal_dist_end":0.08697,"object_to_goal_dist_start":0.09401,"object_z_max":0.32317,"peak_contact_force":0.10224,"phase_name":"align_over_goal","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1780.0,"raw_peak_contact_force":0.29617,"subtask_id":"place_at_goal","tcp_end":[0.57333,0.21606,0.32916],"tcp_start":[0.56635,0.20237,0.33409],"tcp_to_object_dist_end":0.01985,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":240.0,"n_steps_budget":1000.0,"object_pos_end":[0.58923,0.23109,0.2175],"object_pos_start":[0.58789,0.22185,0.31696],"object_to_goal_dist_end":0.01509,"object_to_goal_dist_start":0.08697,"object_z_max":0.31696,"peak_contact_force":0.11177,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7012.0,"raw_peak_contact_force":0.39408,"subtask_id":"place_at_goal","tcp_end":[0.57752,0.22542,0.23446],"tcp_start":[0.57333,0.21606,0.32916],"tcp_to_object_dist_end":0.02137,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```