## Search State

- **Seed**: 9
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → descend → grasp → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 15 | 0.1034 | 1.00 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 15 | 0.1044 | 1.00 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 15 | 0.1049 | 1.00 | ✅ accepted |
| 8 | approach → descend → grasp → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 15 | 0.1037 | 1.00 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 15 | 0.1000 | 1.00 | ❌ rejected |

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

## Current Skill (Q=0.103) — your mutation base

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

- **Composite score**: 0.103
- **task_score** (E): 1.000
- **fitness_score**: 0.973  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.870

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0852 |
| descend_1 | 1.00 | 1.00 | 0.1829 |
| grasp_1 | 1.00 | 1.00 | 0.0130 |
| lift_1 | 1.00 | 1.00 | 0.1618 |
| transport_1 | 1.00 | 1.00 | 0.2299 |
| descend_to_place | 1.00 | 1.00 | 0.1484 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.511, -0.009, 0.228) | (0.515, -0.017, 0.030)→(0.515, -0.017, 0.026) | 0.268→0.270 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.511, -0.009, 0.228)→(0.510, -0.016, 0.046) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.510, -0.016, 0.046)→(0.502, -0.016, 0.036) | (0.515, -0.017, 0.026)→(0.515, -0.016, 0.026) | 0.270→0.270 | 1.00 / 42.667 | 0.150 | 0.209 |
| lift_1 | lift | 1.00 / step_budget | (0.502, -0.016, 0.036)→(0.511, -0.016, 0.197) | (0.515, -0.016, 0.026)→(0.520, -0.016, 0.183) | 0.270→0.229 | 1.00 / 37.000 | 0.081 | 0.477 |
| transport_1 | approach | 1.00 / step_budget | (0.511, -0.016, 0.197)→(0.596, 0.141, 0.332) | (0.520, -0.016, 0.183)→(0.612, 0.141, 0.315) | 0.229→0.153 | 1.00 / 22.333 | 0.117 | 0.160 |
| descend_to_place | descend | 1.00 / step_budget | (0.596, 0.141, 0.332)→(0.611, 0.174, 0.189) | (0.612, 0.141, 0.315)→(0.622, 0.174, 0.168) | 0.153→0.010 | 1.00 / 24.000 | 0.114 | 0.567 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.596
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.498
- phase_breakdown.reach_object_approach_score: 0.183
- phase_breakdown.approach_goal_score: 0.169
- phase_breakdown.lift_clearance_score: 0.684
- phase_breakdown.place_goal_score: 0.952
- grasp_place_fitness: 0.974

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.974
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.103
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.293


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.94862,"average_solve_count":506.0,"average_success_count":506.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.19083,"approach_1.arc_height":0.11439,"approach_1.speed":0.02156,"descend_1.descend_height":0.00124,"descend_1.descend_speed":0.02963,"descend_1.descend_tolerance":0.02097,"descend_to_place.descend_speed_place":0.04774,"descend_to_place.place_height":0.0108,"descend_to_place.place_tolerance":0.02226,"lift_1.lift_height":0.22284,"lift_1.lift_speed":0.03058,"transport_1.transport_arc":0.0945,"transport_1.transport_height":0.12426,"transport_1.transport_speed":0.01287,"transport_1.transport_tolerance":0.07148},"optimized_scores":{"best_composite_score":0.10312,"best_fitness_score":0.97312,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"right_finger","body_b":"grasp_target","contact_count":2311.0,"contact_point_centroid":[0.60673,0.21874,0.29256],"force_p95":0.14626,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.56736,"mean_force":0.09685,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.6009,0.2,0.29256]},{"body_a":"world","body_b":"grasp_target","contact_count":94.0,"contact_point_centroid":[0.53312,-0.02093,-0.00148],"force_p95":0.43343,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.4599,"mean_force":0.18146,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5222,-0.02092,0.03688]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2595.0,"contact_point_centroid":[0.6069,0.18101,0.29453],"force_p95":0.13457,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34972,"mean_force":0.08465,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60075,0.19941,0.2945]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13676.0,"contact_point_centroid":[0.52624,-0.00169,0.13217],"force_p95":0.07783,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26891,"mean_force":0.05446,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5259,-0.02081,0.12968]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14229.0,"contact_point_centroid":[0.52611,-0.03991,0.13051],"force_p95":0.07651,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25426,"mean_force":0.05287,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52581,-0.02081,0.12834]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53702,-0.02119,-0.00204],"force_p95":0.13494,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16397,"mean_force":0.12609,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52447,-0.02096,0.03745]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4638.0,"contact_point_centroid":[0.555,0.06115,0.31485],"force_p95":0.10779,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15153,"mean_force":0.06712,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55275,0.04207,0.31264]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5700.0,"contact_point_centroid":[0.55481,0.02411,0.31426],"force_p95":0.09112,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14502,"mean_force":0.05748,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55302,0.04292,0.31295]},{"body_a":"world","body_b":"grasp_target","contact_count":696.0,"contact_point_centroid":[0.53702,-0.02132,-0.00182],"force_p95":0.13762,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12333,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51792,-0.01118,0.27577]},{"body_a":"world","body_b":"grasp_target","contact_count":1516.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53136,-0.02066,0.14429]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4112.0,"contact_point_centroid":[0.52402,-0.00173,0.03881],"force_p95":0.07659,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12252,"mean_force":0.05179,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52327,-0.02094,0.03608]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4888.0,"contact_point_centroid":[0.52403,-0.04002,0.03789],"force_p95":0.06893,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09011,"mean_force":0.04472,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52327,-0.02094,0.03608]}],"total_contact_groups":12},"final_pose_error":0.01963,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.61675,0.21792,0.21142],"final_tcp_position":[0.60548,0.21809,0.2346],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":0.56736,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":175.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":696.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object_approach","tcp_end":[0.53263,-0.02029,0.24009],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.21411,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":379.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1516.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object_approach","tcp_end":[0.53216,-0.0211,0.04661],"tcp_start":[0.53263,-0.02029,0.24009],"tcp_to_object_dist_end":0.02116,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53691,-0.02085,0.02584],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31648,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13254,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10800.0,"raw_peak_contact_force":0.16397,"tcp_end":[0.52324,-0.02094,0.03604],"tcp_start":[0.53216,-0.0211,0.04661],"tcp_to_object_dist_end":0.01706,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":724.0,"n_steps_budget":1000.0,"object_pos_end":[0.54186,-0.02077,0.21368],"object_pos_start":[0.53691,-0.02085,0.02584],"object_to_goal_dist_end":0.25785,"object_to_goal_dist_start":0.31648,"object_z_max":0.21343,"peak_contact_force":0.07985,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":27999.0,"raw_peak_contact_force":0.4599,"subtask_id":"lift_clearance","tcp_end":[0.53296,-0.02078,0.22931],"tcp_start":[0.52324,-0.02094,0.03604],"tcp_to_object_dist_end":0.01798,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":21.0,"n_steps":322.0,"n_steps_budget":1000.0,"object_pos_end":[0.61374,0.18314,0.33106],"object_pos_start":[0.54186,-0.02077,0.21368],"object_to_goal_dist_end":0.13149,"object_to_goal_dist_start":0.25785,"object_z_max":0.34838,"peak_contact_force":0.12196,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":10338.0,"raw_peak_contact_force":0.15153,"subtask_id":"approach_goal","tcp_end":[0.59772,0.18315,0.34921],"tcp_start":[0.53296,-0.02078,0.22931],"tcp_to_object_dist_end":0.02421,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":20.0,"n_steps":217.0,"n_steps_budget":1000.0,"object_pos_end":[0.61675,0.21792,0.21142],"object_pos_start":[0.61374,0.18314,0.33106],"object_to_goal_dist_end":0.01242,"object_to_goal_dist_start":0.13149,"object_z_max":0.33106,"peak_contact_force":0.13801,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4906.0,"raw_peak_contact_force":0.56736,"subtask_id":"place_goal","tcp_end":[0.60548,0.21809,0.2346],"tcp_start":[0.59772,0.18315,0.34921],"tcp_to_object_dist_end":0.02577,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.09223,"average_solve_count":412.0,"average_success_count":412.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.21159,"approach_1.arc_height":0.09131,"approach_1.speed":0.07095,"descend_1.descend_height":0.00035,"descend_1.descend_speed":0.03107,"descend_1.descend_tolerance":0.02962,"descend_to_place.descend_speed_place":0.06428,"descend_to_place.place_height":-0.00276,"descend_to_place.place_tolerance":0.01728,"lift_1.lift_height":0.15517,"lift_1.lift_speed":0.03363,"transport_1.transport_arc":0.05384,"transport_1.transport_height":0.19695,"transport_1.transport_speed":0.02968,"transport_1.transport_tolerance":0.06478},"optimized_scores":{"best_composite_score":0.10365,"best_fitness_score":0.97365,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"right_finger","body_b":"grasp_target","contact_count":3708.0,"contact_point_centroid":[0.6244,0.1602,0.27039],"force_p95":0.12564,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.51539,"mean_force":0.08433,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62085,0.14142,0.26908]},{"body_a":"world","body_b":"grasp_target","contact_count":100.0,"contact_point_centroid":[0.54194,-0.02823,-0.00153],"force_p95":0.43669,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.45699,"mean_force":0.17606,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53019,-0.02833,0.03524]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4299.0,"contact_point_centroid":[0.62445,0.12248,0.27155],"force_p95":0.11786,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35638,"mean_force":0.07469,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62072,0.14105,0.27086]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9046.0,"contact_point_centroid":[0.53436,-0.0091,0.0987],"force_p95":0.08083,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25689,"mean_force":0.05654,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53385,-0.02824,0.09611]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9771.0,"contact_point_centroid":[0.53414,-0.0473,0.0966],"force_p95":0.07815,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25223,"mean_force":0.05344,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53369,-0.02823,0.0945]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54562,-0.02904,-0.00208],"force_p95":0.14607,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20608,"mean_force":0.12901,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53246,-0.0284,0.03583]},{"body_a":"world","body_b":"grasp_target","contact_count":576.0,"contact_point_centroid":[0.5456,-0.02923,-0.00178],"force_p95":0.13791,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12347,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51955,-0.01325,0.28444]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4090.0,"contact_point_centroid":[0.53221,-0.00916,0.03714],"force_p95":0.0786,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13324,"mean_force":0.05186,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53124,-0.02836,0.03441]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6002.0,"contact_point_centroid":[0.56522,0.00287,0.26098],"force_p95":0.08564,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12539,"mean_force":0.05464,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.56403,0.02178,0.25963]},{"body_a":"world","body_b":"grasp_target","contact_count":1664.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53744,-0.02671,0.1528]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5025.0,"contact_point_centroid":[0.56599,0.04159,0.26287],"force_p95":0.0963,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11949,"mean_force":0.06191,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.56439,0.02248,0.26065]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4940.0,"contact_point_centroid":[0.53218,-0.04747,0.0362],"force_p95":0.07085,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08238,"mean_force":0.04467,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53125,-0.02836,0.03442]}],"total_contact_groups":12},"final_pose_error":0.01986,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.63549,0.15782,0.1741],"final_tcp_position":[0.62713,0.15789,0.19182],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":0.51539,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":145.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12264,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":576.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object_approach","tcp_end":[0.53672,-0.02493,0.25894],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.23313,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":416.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1664.0,"raw_peak_contact_force":0.12264,"subtask_id":"reach_object_approach","tcp_end":[0.54023,-0.02862,0.04525],"tcp_start":[0.53672,-0.02493,0.25894],"tcp_to_object_dist_end":0.01998,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5455,-0.02837,0.02572],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26049,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.14147,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10830.0,"raw_peak_contact_force":0.20608,"tcp_end":[0.53121,-0.02836,0.03438],"tcp_start":[0.54023,-0.02862,0.04525],"tcp_to_object_dist_end":0.01671,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":493.0,"n_steps_budget":1000.0,"object_pos_end":[0.55128,-0.02827,0.14907],"object_pos_start":[0.5455,-0.02837,0.02572],"object_to_goal_dist_end":0.21155,"object_to_goal_dist_start":0.26049,"object_z_max":0.14882,"peak_contact_force":0.08172,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":18917.0,"raw_peak_contact_force":0.45699,"subtask_id":"lift_clearance","tcp_end":[0.54044,-0.02824,0.16173],"tcp_start":[0.53121,-0.02836,0.03438],"tcp_to_object_dist_end":0.01667,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":317.0,"n_steps_budget":1000.0,"object_pos_end":[0.62975,0.12363,0.3392],"object_pos_start":[0.55128,-0.02827,0.14907],"object_to_goal_dist_end":0.16748,"object_to_goal_dist_start":0.21155,"object_z_max":0.33895,"peak_contact_force":0.10651,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":11027.0,"raw_peak_contact_force":0.12539,"subtask_id":"approach_goal","tcp_end":[0.61488,0.12383,0.35363],"tcp_start":[0.54044,-0.02824,0.16173],"tcp_to_object_dist_end":0.02072,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":296.0,"n_steps_budget":1000.0,"object_pos_end":[0.63549,0.15782,0.1741],"object_pos_start":[0.62975,0.12363,0.3392],"object_to_goal_dist_end":0.00809,"object_to_goal_dist_start":0.16748,"object_z_max":0.33935,"peak_contact_force":0.08962,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8007.0,"raw_peak_contact_force":0.51539,"subtask_id":"place_goal","tcp_end":[0.62713,0.15789,0.19182],"tcp_start":[0.61488,0.12383,0.35363],"tcp_to_object_dist_end":0.01959,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.30031,"average_solve_count":323.0,"average_success_count":323.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.1519,"approach_1.arc_height":0.06566,"approach_1.speed":0.07027,"descend_1.descend_height":0.00021,"descend_1.descend_speed":0.03248,"descend_1.descend_tolerance":0.02496,"descend_to_place.descend_speed_place":0.0607,"descend_to_place.place_height":0.00099,"descend_to_place.place_tolerance":0.01362,"lift_1.lift_height":0.19582,"lift_1.lift_speed":0.05624,"transport_1.transport_arc":0.05735,"transport_1.transport_height":0.16708,"transport_1.transport_speed":0.08061,"transport_1.transport_tolerance":0.06925},"optimized_scores":{"best_composite_score":0.10345,"best_fitness_score":0.97345,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"right_finger","body_b":"grasp_target","contact_count":3301.0,"contact_point_centroid":[0.5941,0.15047,0.21636],"force_p95":0.14001,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.61728,"mean_force":0.0938,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.5881,0.13183,0.21484]},{"body_a":"world","body_b":"grasp_target","contact_count":86.0,"contact_point_centroid":[0.46018,0.00267,-0.00158],"force_p95":0.44472,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.51304,"mean_force":0.13292,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45018,0.00249,0.03877]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3462.0,"contact_point_centroid":[0.59368,0.11285,0.2192],"force_p95":0.14216,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34788,"mean_force":0.0882,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.58763,0.1313,0.21786]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11404.0,"contact_point_centroid":[0.45288,-0.01692,0.11798],"force_p95":0.07802,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27501,"mean_force":0.05127,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45306,0.00221,0.1162]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10649.0,"contact_point_centroid":[0.45286,0.02142,0.11703],"force_p95":0.07998,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26748,"mean_force":0.05356,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45298,0.00222,0.11481]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.46294,0.00019,-0.00223],"force_p95":0.18548,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25656,"mean_force":0.13922,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.45218,0.00253,0.03833]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2969.0,"contact_point_centroid":[0.50109,0.05976,0.25801],"force_p95":0.11566,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20341,"mean_force":0.07446,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.49818,0.04076,0.2559]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3543.0,"contact_point_centroid":[0.5018,0.02281,0.2576],"force_p95":0.10722,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18251,"mean_force":0.06657,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.499,0.04157,0.25622]},{"body_a":"world","body_b":"grasp_target","contact_count":1248.0,"contact_point_centroid":[0.46286,-7e-05,-0.00189],"force_p95":0.13606,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12302,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48269,0.03594,0.24758]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4776.0,"contact_point_centroid":[0.45111,0.02177,0.03961],"force_p95":0.07429,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13806,"mean_force":0.04507,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.45112,0.00252,0.03732]},{"body_a":"world","body_b":"grasp_target","contact_count":1188.0,"contact_point_centroid":[0.46286,-7e-05,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45988,0.0112,0.11711]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5477.0,"contact_point_centroid":[0.45084,-0.01685,0.03912],"force_p95":0.07333,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0786,"mean_force":0.04174,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.45113,0.00252,0.03733]}],"total_contact_groups":12},"final_pose_error":0.01971,"key_states":{"actual_goal_position":[0.61015,0.15287,0.12219],"final_object_position":[0.61308,0.14637,0.11699],"final_tcp_position":[0.60149,0.14666,0.13976],"realised_goal_position":[0.61015,0.15287,0.12219],"realised_object_initial_position":[0.46286,-7e-05,0.03]},"peak_contact_force":0.61728,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":313.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.03],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.23148,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1248.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object_approach","tcp_end":[0.46257,0.01928,0.18577],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16091,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":297.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1188.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object_approach","tcp_end":[0.45901,0.00272,0.04518],"tcp_start":[0.46257,0.01928,0.18577],"tcp_to_object_dist_end":0.01974,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46282,0.00193,0.02522],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.23214,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.17636,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12053.0,"raw_peak_contact_force":0.25656,"tcp_end":[0.45109,0.00252,0.0373],"tcp_start":[0.45901,0.00272,0.04518],"tcp_to_object_dist_end":0.01684,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":544.0,"n_steps_budget":1000.0,"object_pos_end":[0.46796,0.0017,0.18524],"object_pos_start":[0.46282,0.00193,0.02522],"object_to_goal_dist_end":0.2169,"object_to_goal_dist_start":0.23214,"object_z_max":0.18497,"peak_contact_force":0.08004,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":22139.0,"raw_peak_contact_force":0.51304,"subtask_id":"lift_clearance","tcp_end":[0.45876,0.00195,0.20146],"tcp_start":[0.45109,0.00252,0.0373],"tcp_to_object_dist_end":0.01864,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":223.0,"n_steps_budget":1000.0,"object_pos_end":[0.59337,0.11684,0.27566],"object_pos_start":[0.46796,0.0017,0.18524],"object_to_goal_dist_end":0.15854,"object_to_goal_dist_start":0.2169,"object_z_max":0.27849,"peak_contact_force":0.12116,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":6512.0,"raw_peak_contact_force":0.20341,"subtask_id":"approach_goal","tcp_end":[0.57594,0.117,0.29414],"tcp_start":[0.45876,0.00195,0.20146],"tcp_to_object_dist_end":0.0254,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":298.0,"n_steps_budget":1000.0,"object_pos_end":[0.61308,0.14637,0.11699],"object_pos_start":[0.59337,0.11684,0.27566],"object_to_goal_dist_end":0.00883,"object_to_goal_dist_start":0.15854,"object_z_max":0.27566,"peak_contact_force":0.11543,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":6763.0,"raw_peak_contact_force":0.61728,"subtask_id":"place_goal","tcp_end":[0.60149,0.14666,0.13976],"tcp_start":[0.57594,0.117,0.29414],"tcp_to_object_dist_end":0.02555,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```