## Search State

- **Seed**: 9
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → descend → grasp → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 15 | 0.1049 | 1.00 | ✅ accepted |
| 8 | approach → descend → grasp → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 15 | 0.1037 | 1.00 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 15 | 0.1000 | 1.00 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 15 | 0.1040 | 1.00 | ✅ accepted |
| 5 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 15 | -0.2383 | 0.38 | ✅ accepted |

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

## Current Skill (Q=0.105) — your mutation base

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

- **Composite score**: 0.105
- **task_score** (E): 1.000
- **fitness_score**: 0.975  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.870

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0807 |
| descend_1 | 1.00 | 1.00 | 0.1903 |
| grasp_1 | 1.00 | 1.00 | 0.0131 |
| lift_1 | 1.00 | 1.00 | 0.1733 |
| transport_1 | 1.00 | 1.00 | 0.2469 |
| descend_to_place | 1.00 | 1.00 | 0.1560 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.524, -0.021, 0.236) | (0.515, -0.017, 0.030)→(0.515, -0.017, 0.026) | 0.268→0.270 | 1.00 / 4.000 | 0.122 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.524, -0.021, 0.236)→(0.512, -0.017, 0.046) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 4.000 | 9.953 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.512, -0.017, 0.046)→(0.503, -0.017, 0.036) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.271 | 1.00 / 46.000 | 0.133 | 0.168 |
| lift_1 | lift | 1.00 / step_budget | (0.503, -0.017, 0.036)→(0.511, -0.017, 0.209) | (0.515, -0.017, 0.026)→(0.519, -0.017, 0.195) | 0.271→0.237 | 1.00 / 42.333 | 0.071 | 0.482 |
| transport_1 | approach | 1.00 / step_budget | (0.511, -0.017, 0.209)→(0.599, 0.143, 0.342) | (0.519, -0.017, 0.195)→(0.614, 0.143, 0.326) | 0.237→0.162 | 1.00 / 25.333 | 55983.982 | 0.123 |
| descend_to_place | descend | 1.00 / step_budget | (0.599, 0.143, 0.342)→(0.612, 0.175, 0.190) | (0.614, 0.143, 0.326)→(0.623, 0.175, 0.170) | 0.162→0.012 | 1.00 / 23.667 | 0.129 | 0.510 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.446
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.542
- phase_breakdown.reach_object_approach_score: 0.185
- phase_breakdown.approach_goal_score: 0.149
- phase_breakdown.lift_clearance_score: 0.890
- phase_breakdown.place_goal_score: 0.936
- grasp_place_fitness: 0.976

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.976
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.106
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.325


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.06917,"average_solve_count":506.0,"average_success_count":506.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.18294,"approach_1.arc_height":0.04938,"approach_1.speed":0.07231,"descend_1.descend_height":0.00022,"descend_1.descend_speed":0.02431,"descend_1.descend_tolerance":0.02655,"descend_to_place.descend_speed_place":0.03203,"descend_to_place.place_height":0.00379,"descend_to_place.place_tolerance":0.00682,"lift_1.lift_height":0.1772,"lift_1.lift_speed":0.02232,"transport_1.transport_arc":0.07306,"transport_1.transport_height":0.1926,"transport_1.transport_speed":0.02169,"transport_1.transport_tolerance":0.05866},"optimized_scores":{"best_composite_score":0.10583,"best_fitness_score":0.97583,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"right_finger","body_b":"grasp_target","contact_count":2990.0,"contact_point_centroid":[0.60692,0.21751,0.31636],"force_p95":0.15658,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.52903,"mean_force":0.09972,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60117,0.19874,0.3154]},{"body_a":"world","body_b":"grasp_target","contact_count":108.0,"contact_point_centroid":[0.53341,-0.02192,-0.00152],"force_p95":0.42133,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.45168,"mean_force":0.1834,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52373,-0.02187,0.03595]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3652.0,"contact_point_centroid":[0.60734,0.18111,0.31319],"force_p95":0.11524,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29968,"mean_force":0.08165,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60132,0.1994,0.31259]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11416.0,"contact_point_centroid":[0.52667,-0.04092,0.10908],"force_p95":0.07393,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23675,"mean_force":0.05194,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52656,-0.02176,0.10721]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11585.0,"contact_point_centroid":[0.52678,-0.00263,0.11009],"force_p95":0.07427,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23103,"mean_force":0.05132,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52663,-0.02176,0.10812]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53703,-0.0214,-0.00206],"force_p95":0.13966,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18752,"mean_force":0.12738,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52609,-0.02192,0.03652]},{"body_a":"world","body_b":"grasp_target","contact_count":976.0,"contact_point_centroid":[0.53702,-0.02132,-0.00187],"force_p95":0.13691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12313,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.53377,-0.02024,0.27928]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6070.0,"contact_point_centroid":[0.55313,0.05951,0.29453],"force_p95":0.09805,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13812,"mean_force":0.05925,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55178,0.04041,0.29254]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6837.0,"contact_point_centroid":[0.55408,0.02492,0.2987],"force_p95":0.08721,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12981,"mean_force":0.05448,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55294,0.04388,0.29721]},{"body_a":"world","body_b":"grasp_target","contact_count":1416.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53923,-0.02526,0.13866]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5073.0,"contact_point_centroid":[0.52461,-0.04115,0.03769],"force_p95":0.06586,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09732,"mean_force":0.04297,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52488,-0.02189,0.03514]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5398.0,"contact_point_centroid":[0.52446,-0.00265,0.03732],"force_p95":0.06475,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08526,"mean_force":0.0411,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52488,-0.02189,0.03515]}],"total_contact_groups":12},"final_pose_error":0.01997,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.61798,0.21977,0.2078],"final_tcp_position":[0.60597,0.21967,0.22893],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":0.52903,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":245.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":976.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object_approach","tcp_end":[0.54632,-0.02837,0.2289],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.20321,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":354.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1416.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object_approach","tcp_end":[0.53382,-0.0221,0.04574],"tcp_start":[0.54632,-0.02837,0.2289],"tcp_to_object_dist_end":0.02,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53691,-0.0218,0.02577],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31727,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13793,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12271.0,"raw_peak_contact_force":0.18752,"tcp_end":[0.52485,-0.02189,0.03511],"tcp_start":[0.53382,-0.0221,0.04574],"tcp_to_object_dist_end":0.01525,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":574.0,"n_steps_budget":1000.0,"object_pos_end":[0.54135,-0.02184,0.17065],"object_pos_start":[0.53691,-0.0218,0.02577],"object_to_goal_dist_end":0.26154,"object_to_goal_dist_start":0.31727,"object_z_max":0.1704,"peak_contact_force":0.07085,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":23109.0,"raw_peak_contact_force":0.45168,"subtask_id":"lift_clearance","tcp_end":[0.53237,-0.02173,0.1835],"tcp_start":[0.52485,-0.02189,0.03511],"tcp_to_object_dist_end":0.01568,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":363.0,"n_steps_budget":1000.0,"object_pos_end":[0.61318,0.1811,0.37465],"object_pos_start":[0.54135,-0.02184,0.17065],"object_to_goal_dist_end":0.17365,"object_to_goal_dist_start":0.26154,"object_z_max":0.37458,"peak_contact_force":0.1073,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":12907.0,"raw_peak_contact_force":0.13812,"subtask_id":"approach_goal","tcp_end":[0.59779,0.18128,0.38942],"tcp_start":[0.53237,-0.02173,0.1835],"tcp_to_object_dist_end":0.02134,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":302.0,"n_steps_budget":1000.0,"object_pos_end":[0.61798,0.21977,0.2078],"object_pos_start":[0.61318,0.1811,0.37465],"object_to_goal_dist_end":0.01108,"object_to_goal_dist_start":0.17365,"object_z_max":0.37465,"peak_contact_force":0.17419,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":6642.0,"raw_peak_contact_force":0.52903,"subtask_id":"place_goal","tcp_end":[0.60597,0.21967,0.22893],"tcp_start":[0.59779,0.18128,0.38942],"tcp_to_object_dist_end":0.02431,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.04067,"average_solve_count":418.0,"average_success_count":418.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.16064,"approach_1.arc_height":0.08243,"approach_1.speed":0.04952,"descend_1.descend_height":0.00025,"descend_1.descend_speed":0.03649,"descend_1.descend_tolerance":0.0233,"descend_to_place.descend_speed_place":0.05986,"descend_to_place.place_height":0.01052,"descend_to_place.place_tolerance":0.01983,"lift_1.lift_height":0.18678,"lift_1.lift_speed":0.05046,"transport_1.transport_arc":0.07657,"transport_1.transport_height":0.23353,"transport_1.transport_speed":0.03941,"transport_1.transport_tolerance":0.06724},"optimized_scores":{"best_composite_score":0.10578,"best_fitness_score":0.97578,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"right_finger","body_b":"grasp_target","contact_count":4428.0,"contact_point_centroid":[0.62426,0.15785,0.30466],"force_p95":0.11949,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.54384,"mean_force":0.08476,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62067,0.13898,0.30362]},{"body_a":"world","body_b":"grasp_target","contact_count":89.0,"contact_point_centroid":[0.54175,-0.0296,-0.00143],"force_p95":0.51812,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.53702,"mean_force":0.17437,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53198,-0.02954,0.03571]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5288.0,"contact_point_centroid":[0.62439,0.12119,0.30045],"force_p95":0.11002,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32356,"mean_force":0.06943,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62093,0.13969,0.29991]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12254.0,"contact_point_centroid":[0.53479,-0.0486,0.11421],"force_p95":0.07372,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29132,"mean_force":0.05111,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53497,-0.02942,0.11226]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12449.0,"contact_point_centroid":[0.53463,-0.01026,0.11312],"force_p95":0.07292,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27657,"mean_force":0.05047,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53489,-0.02942,0.11128]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5456,-0.02929,-0.00204],"force_p95":0.13441,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16898,"mean_force":0.12602,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5342,-0.02961,0.03605]},{"body_a":"world","body_b":"grasp_target","contact_count":1144.0,"contact_point_centroid":[0.5456,-0.02923,-0.00188],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12305,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.53614,-0.02425,0.26887]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5559.0,"contact_point_centroid":[0.56037,0.02745,0.30028],"force_p95":0.09731,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12988,"mean_force":0.06014,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55898,0.00835,0.2982]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6310.0,"contact_point_centroid":[0.56125,-0.00836,0.30454],"force_p95":0.08781,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12957,"mean_force":0.05517,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.56013,0.0106,0.30314]},{"body_a":"world","body_b":"grasp_target","contact_count":1256.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.54601,-0.03249,0.1283]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5368.0,"contact_point_centroid":[0.53269,-0.01033,0.0372],"force_p95":0.06385,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09381,"mean_force":0.04116,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53298,-0.02957,0.03463]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5086.0,"contact_point_centroid":[0.53285,-0.04882,0.03753],"force_p95":0.06525,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09317,"mean_force":0.04291,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53298,-0.02957,0.03462]}],"total_contact_groups":12},"final_pose_error":0.01987,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.63816,0.15854,0.18738],"final_tcp_position":[0.6276,0.15835,0.20544],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":29.614,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":287.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1144.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object_approach","tcp_end":[0.55176,-0.03508,0.20841],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.18259,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":314.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":29.614,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1256.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object_approach","tcp_end":[0.54204,-0.02989,0.04556],"tcp_start":[0.55176,-0.03508,0.20841],"tcp_to_object_dist_end":0.01987,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54548,-0.02953,0.02583],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.2613,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.13351,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12254.0,"raw_peak_contact_force":0.16898,"tcp_end":[0.53295,-0.02957,0.03459],"tcp_start":[0.54204,-0.02989,0.04556],"tcp_to_object_dist_end":0.01528,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":598.0,"n_steps_budget":1000.0,"object_pos_end":[0.55056,-0.02931,0.18006],"object_pos_start":[0.54548,-0.02953,0.02583],"object_to_goal_dist_end":0.21097,"object_to_goal_dist_start":0.2613,"object_z_max":0.17981,"peak_contact_force":0.06937,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":24792.0,"raw_peak_contact_force":0.53702,"subtask_id":"lift_clearance","tcp_end":[0.54108,-0.02941,0.19328],"tcp_start":[0.53295,-0.02957,0.03459],"tcp_to_object_dist_end":0.01628,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":338.0,"n_steps_budget":1000.0,"object_pos_end":[0.62989,0.12042,0.38425],"object_pos_start":[0.55056,-0.02931,0.18006],"object_to_goal_dist_end":0.21208,"object_to_goal_dist_start":0.21097,"object_z_max":0.38416,"peak_contact_force":0.1088,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":11869.0,"raw_peak_contact_force":0.12988,"subtask_id":"approach_goal","tcp_end":[0.61438,0.12061,0.39883],"tcp_start":[0.54108,-0.02941,0.19328],"tcp_to_object_dist_end":0.02129,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":351.0,"n_steps_budget":1000.0,"object_pos_end":[0.63816,0.15854,0.18738],"object_pos_start":[0.62989,0.12042,0.38425],"object_to_goal_dist_end":0.01336,"object_to_goal_dist_start":0.21208,"object_z_max":0.38425,"peak_contact_force":0.11535,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9716.0,"raw_peak_contact_force":0.54384,"subtask_id":"place_goal","tcp_end":[0.6276,0.15835,0.20544],"tcp_start":[0.61438,0.12061,0.39883],"tcp_to_object_dist_end":0.02093,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.92623,"average_solve_count":488.0,"average_success_count":488.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.22398,"approach_1.arc_height":0.13493,"approach_1.speed":0.02569,"descend_1.descend_height":0.00161,"descend_1.descend_speed":0.02409,"descend_1.descend_tolerance":0.01965,"descend_to_place.descend_speed_place":0.03144,"descend_to_place.place_height":-0.00446,"descend_to_place.place_tolerance":0.02498,"lift_1.lift_height":0.24514,"lift_1.lift_speed":0.03768,"transport_1.transport_arc":0.05923,"transport_1.transport_height":0.08041,"transport_1.transport_speed":0.03714,"transport_1.transport_tolerance":0.08461},"optimized_scores":{"best_composite_score":0.10302,"best_fitness_score":0.97302,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"right_finger","body_b":"grasp_target","contact_count":2323.0,"contact_point_centroid":[0.59646,0.15478,0.18637],"force_p95":0.11512,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.45805,"mean_force":0.08702,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59166,0.13605,0.18486]},{"body_a":"world","body_b":"grasp_target","contact_count":84.0,"contact_point_centroid":[0.45909,-0.00015,-0.00143],"force_p95":0.43783,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.45781,"mean_force":0.18433,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45128,-0.00022,0.04035]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2370.0,"contact_point_centroid":[0.59648,0.11733,0.18718],"force_p95":0.11638,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.43195,"mean_force":0.085,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59151,0.13589,0.18569]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14220.0,"contact_point_centroid":[0.45415,0.01893,0.14672],"force_p95":0.07393,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2681,"mean_force":0.05168,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45395,-0.00021,0.14483]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14220.0,"contact_point_centroid":[0.45418,-0.01935,0.14673],"force_p95":0.07383,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26491,"mean_force":0.05163,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45395,-0.00021,0.14483]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.46285,-9e-05,-0.00202],"force_p95":0.12873,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14653,"mean_force":0.12445,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.45325,-0.00019,0.04042]},{"body_a":"world","body_b":"grasp_target","contact_count":352.0,"contact_point_centroid":[0.46286,-7e-05,-0.00165],"force_p95":0.13823,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12413,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48724,-5e-05,0.28801]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.46286,-7e-05,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.1226,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.4659,-8e-05,0.15976]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3792.0,"contact_point_centroid":[0.51604,0.07458,0.26697],"force_p95":0.08257,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10245,"mean_force":0.05639,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.5151,0.05544,0.26466]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4342.0,"contact_point_centroid":[0.51683,0.03743,0.26691],"force_p95":0.07832,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0963,"mean_force":0.05103,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51614,0.05647,0.26516]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4864.0,"contact_point_centroid":[0.45237,0.019,0.0413],"force_p95":0.06806,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08903,"mean_force":0.04481,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.45219,-0.0002,0.03941]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4849.0,"contact_point_centroid":[0.4524,-0.01939,0.04131],"force_p95":0.06799,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0861,"mean_force":0.04477,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.45219,-0.0002,0.03941]}],"total_contact_groups":12},"final_pose_error":0.01978,"key_states":{"actual_goal_position":[0.61015,0.15287,0.12219],"final_object_position":[0.61348,0.14635,0.11378],"final_tcp_position":[0.60122,0.14646,0.13417],"realised_goal_position":[0.61015,0.15287,0.12219],"realised_object_initial_position":[0.46286,-7e-05,0.03]},"peak_contact_force":167951.73011,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":89.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02599],"object_pos_start":[0.46286,-7e-05,0.03],"object_to_goal_dist_end":0.23311,"object_to_goal_dist_start":0.23148,"object_z_max":0.03,"peak_contact_force":0.12209,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":352.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object_approach","tcp_end":[0.47332,-6e-05,0.27084],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.24507,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":451.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.02599],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.23311,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1804.0,"raw_peak_contact_force":0.12264,"subtask_id":"reach_object_approach","tcp_end":[0.4601,-0.00011,0.04735],"tcp_start":[0.47332,-6e-05,0.27084],"tcp_to_object_dist_end":0.0215,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46275,-0.00017,0.02591],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.23327,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12849,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11513.0,"raw_peak_contact_force":0.14653,"tcp_end":[0.45217,-0.0002,0.03938],"tcp_start":[0.4601,-0.00011,0.04735],"tcp_to_object_dist_end":0.01713,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":711.0,"n_steps_budget":1000.0,"object_pos_end":[0.46646,-0.00018,0.23437],"object_pos_start":[0.46275,-0.00017,0.02591],"object_to_goal_dist_end":0.23802,"object_to_goal_dist_start":0.23327,"object_z_max":0.23409,"peak_contact_force":0.07154,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":28524.0,"raw_peak_contact_force":0.45781,"subtask_id":"lift_clearance","tcp_end":[0.45937,-0.00019,0.25163],"tcp_start":[0.45217,-0.0002,0.03938],"tcp_to_object_dist_end":0.01866,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":31.0,"n_steps":217.0,"n_steps_budget":1000.0,"object_pos_end":[0.59784,0.12671,0.21832],"object_pos_start":[0.46646,-0.00018,0.23437],"object_to_goal_dist_end":0.10039,"object_to_goal_dist_start":0.23802,"object_z_max":0.25978,"peak_contact_force":167951.73011,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8134.0,"raw_peak_contact_force":0.10245,"subtask_id":"approach_goal","tcp_end":[0.5852,0.12679,0.23631],"tcp_start":[0.45937,-0.00019,0.25163],"tcp_to_object_dist_end":0.02198,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":198.0,"n_steps_budget":1000.0,"object_pos_end":[0.61348,0.14635,0.11378],"object_pos_start":[0.59784,0.12671,0.21832],"object_to_goal_dist_end":0.01115,"object_to_goal_dist_start":0.10039,"object_z_max":0.21832,"peak_contact_force":0.09737,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4693.0,"raw_peak_contact_force":0.45805,"subtask_id":"place_goal","tcp_end":[0.60122,0.14646,0.13417],"tcp_start":[0.5852,0.12679,0.23631],"tcp_to_object_dist_end":0.02379,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```