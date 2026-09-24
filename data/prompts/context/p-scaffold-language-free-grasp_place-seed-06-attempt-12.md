## Search State

- **Seed**: 6
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → grasp → lift → approach → align → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 15 | 0.0759 | 1.00 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → align → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 15 | 0.0764 | 1.00 | ✅ accepted |
| 10 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 11 | -0.0894 | 0.28 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 11 | -0.0782 | 0.29 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 11 | -0.0744 | 0.30 | ❌ rejected |

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
| approach_1 | 1.00 | 1.00 | 0.1210 |
| descend_1 | 1.00 | 1.00 | 0.1435 |
| grasp_1 | 1.00 | 1.00 | 0.0125 |
| lift_1 | 0.00 | 1.00 | 0.1185 |
| transport_above_goal | 1.00 | 1.00 | 0.2724 |
| align_over_goal | 1.00 | 1.00 | 0.0161 |
| descend_to_place | 1.00 | 1.00 | 0.1041 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, 0.022, 0.185) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.496, 0.022, 0.185)→(0.495, 0.024, 0.041) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.495, 0.024, 0.041)→(0.486, 0.023, 0.032) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.272 | 1.00 / 42.333 | 0.151 | 0.201 |
| lift_1 | lift | 0.00 / step_budget | (0.486, 0.023, 0.032)→(0.490, 0.023, 0.151) | (0.500, 0.024, 0.026)→(0.499, 0.024, 0.137) | 0.272→0.216 | 1.00 / 37.000 | 0.080 | 0.588 |
| transport_above_goal | approach | 1.00 / step_budget | (0.490, 0.023, 0.151)→(0.588, 0.181, 0.348) | (0.499, 0.024, 0.137)→(0.600, 0.185, 0.334) | 0.216→0.126 | 1.00 / 36.667 | 0.084 | 0.168 |
| align_over_goal | align | 1.00 / step_budget | (0.588, 0.181, 0.348)→(0.592, 0.187, 0.334) | (0.600, 0.185, 0.334)→(0.604, 0.191, 0.318) | 0.126→0.111 | 1.00 / 34.000 | 0.090 | 0.297 |
| descend_to_place | descend | 1.00 / step_budget | (0.592, 0.187, 0.334)→(0.595, 0.193, 0.230) | (0.604, 0.191, 0.318)→(0.606, 0.197, 0.211) | 0.111→0.009 | 1.00 / 27.333 | 0.094 | 0.305 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.664
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.585
- phase_breakdown.approach_object_score: 0.163
- phase_breakdown.transport_to_goal_score: 0.572
- phase_breakdown.lift_object_score: 0.510
- phase_breakdown.place_at_goal_score: 0.929
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
- **Final σ (mean)**: 0.318


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.33077,"average_solve_count":260.0,"average_success_count":260.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_over_goal.align_speed":0.0437,"align_over_goal.align_tolerance":0.01995,"align_over_goal.align_z_offset":0.1132,"approach_1.approach_speed":0.05547,"approach_1.approach_z_offset":0.1592,"descend_1.descend_speed":0.04761,"descend_1.descend_z_offset":0.00616,"descend_to_place.descend_place_speed":0.05334,"descend_to_place.descend_place_z_offset":-0.00518,"descend_to_place.descend_tolerance":0.03535,"lift_1.lift_height":0.2479,"lift_1.lift_speed":0.08017,"transport_above_goal.transport_height":0.15091,"transport_above_goal.transport_speed":0.17272,"transport_above_goal.transport_tolerance":0.02379},"optimized_scores":{"best_composite_score":0.07663,"best_fitness_score":0.97663,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":162.0,"contact_point_centroid":[0.50017,-0.01544,-0.00116],"force_p95":0.39641,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62329,"mean_force":0.09743,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48853,-0.01539,0.03294]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20695.0,"contact_point_centroid":[0.49074,0.00358,0.09504],"force_p95":0.07355,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31667,"mean_force":0.0495,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48955,-0.01546,0.09319]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18215.0,"contact_point_centroid":[0.48997,-0.03464,0.09619],"force_p95":0.07915,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31535,"mean_force":0.055,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48955,-0.01546,0.09351]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":420.0,"contact_point_centroid":[0.57575,0.19568,0.37967],"force_p95":0.08538,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22158,"mean_force":0.05226,"phase_index":5.0,"phase_name":"align_over_goal","phase_type":"align","tcp_position_centroid":[0.58106,0.17733,0.37814]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1990.0,"contact_point_centroid":[0.57901,0.1996,0.33465],"force_p95":0.08922,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21078,"mean_force":0.06098,"phase_index":6.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.58255,0.18093,0.33261]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1975.0,"contact_point_centroid":[0.58949,0.16315,0.33242],"force_p95":0.08751,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17952,"mean_force":0.06147,"phase_index":6.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.58257,0.181,0.33148]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13485.0,"contact_point_centroid":[0.54014,0.06331,0.2709],"force_p95":0.08347,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17167,"mean_force":0.05545,"phase_index":4.0,"phase_name":"transport_above_goal","phase_type":"approach","tcp_position_centroid":[0.53651,0.08194,0.26965]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":420.0,"contact_point_centroid":[0.58626,0.15881,0.37853],"force_p95":0.07314,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16326,"mean_force":0.04992,"phase_index":5.0,"phase_name":"align_over_goal","phase_type":"align","tcp_position_centroid":[0.58106,0.17733,0.37814]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12970.0,"contact_point_centroid":[0.53549,0.10184,0.27287],"force_p95":0.08515,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16097,"mean_force":0.05709,"phase_index":4.0,"phase_name":"transport_above_goal","phase_type":"approach","tcp_position_centroid":[0.53696,0.08295,0.2708]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50381,-0.01576,-0.00203],"force_p95":0.13268,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15966,"mean_force":0.12518,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49129,-0.01541,0.03273]},{"body_a":"world","body_b":"grasp_target","contact_count":1360.0,"contact_point_centroid":[0.50382,-0.01567,-0.0019],"force_p95":0.1356,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12299,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49896,-0.0065,0.24964]},{"body_a":"world","body_b":"grasp_target","contact_count":2128.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49783,-0.01451,0.11855]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5326.0,"contact_point_centroid":[0.49082,0.00366,0.03336],"force_p95":0.06669,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09487,"mean_force":0.0411,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49006,-0.0154,0.03143]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4146.0,"contact_point_centroid":[0.48951,-0.03467,0.03402],"force_p95":0.07897,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09404,"mean_force":0.05187,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49006,-0.0154,0.03143]}],"total_contact_groups":14},"final_pose_error":0.0349,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.59368,0.18788,0.25875],"final_tcp_position":[0.58402,0.18411,0.27755],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":0.62329,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":341.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1360.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.49988,-0.01362,0.19793],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17197,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":532.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2128.0,"raw_peak_contact_force":0.12263,"subtask_id":"approach_object","tcp_end":[0.49862,-0.01546,0.04055],"tcp_start":[0.49988,-0.01362,0.19793],"tcp_to_object_dist_end":0.01544,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50368,-0.01577,0.02588],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31243,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13276,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11272.0,"raw_peak_contact_force":0.15966,"subtask_id":"lift_object","tcp_end":[0.49003,-0.0154,0.03139],"tcp_start":[0.49862,-0.01546,0.04055],"tcp_to_object_dist_end":0.01472,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5033,-0.01591,0.14812],"object_pos_start":[0.50368,-0.01577,0.02588],"object_to_goal_dist_end":0.24155,"object_to_goal_dist_start":0.31243,"object_z_max":0.14798,"peak_contact_force":0.08053,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":39072.0,"raw_peak_contact_force":0.62329,"subtask_id":"lift_object","tcp_end":[0.49371,-0.01556,0.16106],"tcp_start":[0.49003,-0.0154,0.03139],"tcp_to_object_dist_end":0.01611,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":725.0,"n_steps_budget":1000.0,"object_pos_end":[0.59028,0.17953,0.36305],"object_pos_start":[0.5033,-0.01591,0.14812],"object_to_goal_dist_end":0.11526,"object_to_goal_dist_start":0.24155,"object_z_max":0.36281,"peak_contact_force":0.0688,"phase_name":"transport_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":26455.0,"raw_peak_contact_force":0.17167,"subtask_id":"transport_to_goal","tcp_end":[0.58089,0.17645,0.37904],"tcp_start":[0.49371,-0.01556,0.16106],"tcp_to_object_dist_end":0.0188,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.59156,0.18181,0.35899],"object_pos_start":[0.59028,0.17953,0.36305],"object_to_goal_dist_end":0.11111,"object_to_goal_dist_start":0.11526,"object_z_max":0.36316,"peak_contact_force":0.06951,"phase_name":"align_over_goal","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":840.0,"raw_peak_contact_force":0.22158,"subtask_id":"place_at_goal","tcp_end":[0.5816,0.17843,0.37544],"tcp_start":[0.58089,0.17645,0.37904],"tcp_to_object_dist_end":0.01953,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":123.0,"n_steps_budget":1000.0,"object_pos_end":[0.59368,0.18788,0.25875],"object_pos_start":[0.59156,0.18181,0.35899],"object_to_goal_dist_end":0.01262,"object_to_goal_dist_start":0.11111,"object_z_max":0.35899,"peak_contact_force":0.08358,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3965.0,"raw_peak_contact_force":0.21078,"subtask_id":"place_at_goal","tcp_end":[0.58402,0.18411,0.27755],"tcp_start":[0.5816,0.17843,0.37544],"tcp_to_object_dist_end":0.02147,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.17988,"average_solve_count":328.0,"average_success_count":328.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_over_goal.align_speed":0.06526,"align_over_goal.align_tolerance":0.02962,"align_over_goal.align_z_offset":0.11582,"approach_1.approach_speed":0.03773,"approach_1.approach_z_offset":0.15956,"descend_1.descend_speed":0.06121,"descend_1.descend_z_offset":0.00945,"descend_to_place.descend_place_speed":0.02993,"descend_to_place.descend_place_z_offset":-0.00021,"descend_to_place.descend_tolerance":0.02079,"lift_1.lift_height":0.20038,"lift_1.lift_speed":0.0668,"transport_above_goal.transport_height":0.20455,"transport_above_goal.transport_speed":0.10498,"transport_above_goal.transport_tolerance":0.0425},"optimized_scores":{"best_composite_score":0.074,"best_fitness_score":0.974,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":168.0,"contact_point_centroid":[0.50847,0.03717,-0.0012],"force_p95":0.3372,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.53857,"mean_force":0.08892,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4972,0.03809,0.0363]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2190.0,"contact_point_centroid":[0.61989,0.18529,0.23066],"force_p95":0.12356,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.4434,"mean_force":0.09699,"phase_index":6.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61921,0.16612,0.22665]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":550.0,"contact_point_centroid":[0.61321,0.17792,0.30912],"force_p95":0.16487,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.38467,"mean_force":0.09923,"phase_index":5.0,"phase_name":"align_over_goal","phase_type":"align","tcp_position_centroid":[0.61395,0.15881,0.30506]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2673.0,"contact_point_centroid":[0.62871,0.14928,0.2297],"force_p95":0.11446,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3676,"mean_force":0.08344,"phase_index":6.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61915,0.16604,0.22816]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17000.0,"contact_point_centroid":[0.49877,0.05727,0.09147],"force_p95":0.08329,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30249,"mean_force":0.05831,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49861,0.03808,0.08869]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20764.0,"contact_point_centroid":[0.50032,0.01914,0.08936],"force_p95":0.0774,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2769,"mean_force":0.04906,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49853,0.03808,0.08775]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":706.0,"contact_point_centroid":[0.62207,0.14168,0.30662],"force_p95":0.1366,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24634,"mean_force":0.07785,"phase_index":5.0,"phase_name":"align_over_goal","phase_type":"align","tcp_position_centroid":[0.614,0.15886,0.30486]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51258,0.03969,-0.00213],"force_p95":0.15899,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21111,"mean_force":0.13212,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49989,0.03832,0.03579]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5030.0,"contact_point_centroid":[0.50032,0.01922,0.03595],"force_p95":0.07386,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17736,"mean_force":0.04305,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49865,0.03822,0.03445]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5062.0,"contact_point_centroid":[0.5517,0.112,0.22481],"force_p95":0.10041,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16326,"mean_force":0.06554,"phase_index":4.0,"phase_name":"transport_above_goal","phase_type":"approach","tcp_position_centroid":[0.5525,0.09292,0.22224]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5967.0,"contact_point_centroid":[0.55717,0.07476,0.22341],"force_p95":0.09255,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15559,"mean_force":0.05731,"phase_index":4.0,"phase_name":"transport_above_goal","phase_type":"approach","tcp_position_centroid":[0.55272,0.09315,0.22259]},{"body_a":"world","body_b":"grasp_target","contact_count":1536.0,"contact_point_centroid":[0.51251,0.03972,-0.00191],"force_p95":0.13468,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12294,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50263,0.0168,0.24843]},{"body_a":"world","body_b":"grasp_target","contact_count":2008.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.506,0.03678,0.1196]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4222.0,"contact_point_centroid":[0.49893,0.05753,0.03719],"force_p95":0.0836,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0894,"mean_force":0.05181,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49866,0.03822,0.03446]}],"total_contact_groups":14},"final_pose_error":0.02057,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.63461,0.17406,0.14299],"final_tcp_position":[0.6223,0.16974,0.16451],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":0.53857,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":385.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1536.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.50759,0.03489,0.19659],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17071,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":502.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2008.0,"raw_peak_contact_force":0.12263,"subtask_id":"approach_object","tcp_end":[0.50722,0.03891,0.04389],"tcp_start":[0.50759,0.03489,0.19659],"tcp_to_object_dist_end":0.01865,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5125,0.03889,0.02556],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21301,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.15657,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11052.0,"raw_peak_contact_force":0.21111,"subtask_id":"lift_object","tcp_end":[0.49863,0.03822,0.03442],"tcp_start":[0.50722,0.03891,0.04389],"tcp_to_object_dist_end":0.01648,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51131,0.03908,0.12728],"object_pos_start":[0.5125,0.03889,0.02556],"object_to_goal_dist_end":0.17787,"object_to_goal_dist_start":0.21301,"object_z_max":0.12716,"peak_contact_force":0.08024,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":37932.0,"raw_peak_contact_force":0.53857,"subtask_id":"lift_object","tcp_end":[0.50284,0.03829,0.14363],"tcp_start":[0.49863,0.03822,0.03442],"tcp_to_object_dist_end":0.01844,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":325.0,"n_steps_budget":1000.0,"object_pos_end":[0.62631,0.15951,0.30039],"object_pos_start":[0.51131,0.03908,0.12728],"object_to_goal_dist_end":0.15591,"object_to_goal_dist_start":0.17787,"object_z_max":0.29986,"peak_contact_force":0.10257,"phase_name":"transport_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":11029.0,"raw_peak_contact_force":0.16326,"subtask_id":"transport_to_goal","tcp_end":[0.61079,0.15511,0.3153],"tcp_start":[0.50284,0.03829,0.14363],"tcp_to_object_dist_end":0.02196,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":51.0,"n_steps_budget":600.0,"object_pos_end":[0.63551,0.16843,0.27103],"object_pos_start":[0.62631,0.15951,0.30039],"object_to_goal_dist_end":0.12632,"object_to_goal_dist_start":0.15591,"object_z_max":0.30119,"peak_contact_force":0.11243,"phase_name":"align_over_goal","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1256.0,"raw_peak_contact_force":0.38467,"subtask_id":"place_at_goal","tcp_end":[0.61795,0.16323,0.28675],"tcp_start":[0.61079,0.15511,0.3153],"tcp_to_object_dist_end":0.02414,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":20.0,"n_steps":219.0,"n_steps_budget":1000.0,"object_pos_end":[0.63461,0.17406,0.14299],"object_pos_start":[0.63551,0.16843,0.27103],"object_to_goal_dist_end":0.00749,"object_to_goal_dist_start":0.12632,"object_z_max":0.27103,"peak_contact_force":0.1106,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4863.0,"raw_peak_contact_force":0.4434,"subtask_id":"place_at_goal","tcp_end":[0.6223,0.16974,0.16451],"tcp_start":[0.61795,0.16323,0.28675],"tcp_to_object_dist_end":0.02517,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.32414,"average_solve_count":290.0,"average_success_count":290.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_over_goal.align_speed":0.06724,"align_over_goal.align_tolerance":0.01449,"align_over_goal.align_z_offset":0.10055,"approach_1.approach_speed":0.03495,"approach_1.approach_z_offset":0.12165,"descend_1.descend_speed":0.05985,"descend_1.descend_z_offset":0.005,"descend_to_place.descend_place_speed":0.04425,"descend_to_place.descend_place_z_offset":-0.00926,"descend_to_place.descend_tolerance":0.02736,"lift_1.lift_height":0.1993,"lift_1.lift_speed":0.07146,"transport_above_goal.transport_height":0.14791,"transport_above_goal.transport_speed":0.15777,"transport_above_goal.transport_tolerance":0.03365},"optimized_scores":{"best_composite_score":0.07695,"best_fitness_score":0.97695,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":162.0,"contact_point_centroid":[0.47826,0.04568,-0.00126],"force_p95":0.4012,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.6026,"mean_force":0.09955,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46793,0.04679,0.03277]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17000.0,"contact_point_centroid":[0.46923,0.06595,0.0916],"force_p95":0.08425,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31332,"mean_force":0.05838,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46946,0.04676,0.08891]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20979.0,"contact_point_centroid":[0.47139,0.02784,0.08968],"force_p95":0.07769,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28625,"mean_force":0.04865,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46941,0.04676,0.08819]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":724.0,"contact_point_centroid":[0.56723,0.23388,0.35003],"force_p95":0.09649,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28346,"mean_force":0.06679,"phase_index":5.0,"phase_name":"align_over_goal","phase_type":"align","tcp_position_centroid":[0.573,0.21567,0.34665]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2096.0,"contact_point_centroid":[0.57132,0.24028,0.3012],"force_p95":0.09209,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26115,"mean_force":0.0656,"phase_index":6.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57604,0.22191,0.29797]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48279,0.04864,-0.00216],"force_p95":0.16661,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23227,"mean_force":0.1343,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47056,0.04707,0.03225]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5005.0,"contact_point_centroid":[0.47131,0.02797,0.0323],"force_p95":0.07899,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19322,"mean_force":0.04318,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46935,0.04695,0.03103]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2510.0,"contact_point_centroid":[0.58359,0.20457,0.29786],"force_p95":0.08464,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18657,"mean_force":0.05712,"phase_index":6.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57604,0.22191,0.29793]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":944.0,"contact_point_centroid":[0.57902,0.19772,0.34672],"force_p95":0.07941,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17642,"mean_force":0.05076,"phase_index":5.0,"phase_name":"align_over_goal","phase_type":"align","tcp_position_centroid":[0.57301,0.21569,0.34663]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9165.0,"contact_point_centroid":[0.52654,0.11132,0.24817],"force_p95":0.08481,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16797,"mean_force":0.05376,"phase_index":4.0,"phase_name":"transport_above_goal","phase_type":"approach","tcp_position_centroid":[0.52149,0.12958,0.24724]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7754.0,"contact_point_centroid":[0.5185,0.14782,0.24943],"force_p95":0.09002,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14949,"mean_force":0.06136,"phase_index":4.0,"phase_name":"transport_above_goal","phase_type":"approach","tcp_position_centroid":[0.52113,0.12899,0.24651]},{"body_a":"world","body_b":"grasp_target","contact_count":1968.0,"contact_point_centroid":[0.4827,0.04873,-0.00193],"force_p95":0.13308,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12287,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48946,0.02129,0.23024]},{"body_a":"world","body_b":"grasp_target","contact_count":1656.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47769,0.04571,0.09927]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4239.0,"contact_point_centroid":[0.46929,0.06629,0.03351],"force_p95":0.08656,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09696,"mean_force":0.05199,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46936,0.04695,0.03104]}],"total_contact_groups":14},"final_pose_error":0.02726,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.58844,0.23025,0.23088],"final_tcp_position":[0.57796,0.22527,0.24797],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":0.6026,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":493.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1968.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.48054,0.04395,0.15995],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13404,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":414.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1656.0,"raw_peak_contact_force":0.12263,"subtask_id":"approach_object","tcp_end":[0.4777,0.04776,0.03956],"tcp_start":[0.48054,0.04395,0.15995],"tcp_to_object_dist_end":0.01447,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48272,0.04763,0.02546],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29105,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.16315,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11044.0,"raw_peak_contact_force":0.23227,"subtask_id":"lift_object","tcp_end":[0.46933,0.04695,0.031],"tcp_start":[0.4777,0.04776,0.03956],"tcp_to_object_dist_end":0.01451,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48313,0.04793,0.13461],"object_pos_start":[0.48272,0.04763,0.02546],"object_to_goal_dist_end":0.22732,"object_to_goal_dist_start":0.29105,"object_z_max":0.13452,"peak_contact_force":0.08,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":38141.0,"raw_peak_contact_force":0.6026,"subtask_id":"lift_object","tcp_end":[0.47381,0.047,0.14753],"tcp_start":[0.46933,0.04695,0.031],"tcp_to_object_dist_end":0.01595,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":467.0,"n_steps_budget":1000.0,"object_pos_end":[0.58235,0.21706,0.3371],"object_pos_start":[0.48313,0.04793,0.13461],"object_to_goal_dist_end":0.10727,"object_to_goal_dist_start":0.22732,"object_z_max":0.33671,"peak_contact_force":0.08037,"phase_name":"transport_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":16919.0,"raw_peak_contact_force":0.16797,"subtask_id":"transport_to_goal","tcp_end":[0.57165,0.21268,0.35088],"tcp_start":[0.47381,0.047,0.14753],"tcp_to_object_dist_end":0.01798,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":44.0,"n_steps_budget":600.0,"object_pos_end":[0.58638,0.22419,0.32504],"object_pos_start":[0.58235,0.21706,0.3371],"object_to_goal_dist_end":0.09478,"object_to_goal_dist_start":0.10727,"object_z_max":0.33753,"peak_contact_force":0.08912,"phase_name":"align_over_goal","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1668.0,"raw_peak_contact_force":0.28346,"subtask_id":"place_at_goal","tcp_end":[0.57502,0.21928,0.33931],"tcp_start":[0.57165,0.21268,0.35088],"tcp_to_object_dist_end":0.01889,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":139.0,"n_steps_budget":1000.0,"object_pos_end":[0.58844,0.23025,0.23088],"object_pos_start":[0.58638,0.22419,0.32504],"object_to_goal_dist_end":0.00672,"object_to_goal_dist_start":0.09478,"object_z_max":0.32504,"peak_contact_force":0.08823,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4606.0,"raw_peak_contact_force":0.26115,"subtask_id":"place_at_goal","tcp_end":[0.57796,0.22527,0.24797],"tcp_start":[0.57502,0.21928,0.33931],"tcp_to_object_dist_end":0.02066,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```