## Search State

- **Seed**: 9
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8  | -0.0199 | 0.38 | ✅ accepted |
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 10  | -0.1646 | 0.13 | ✅ accepted |
| 3 | rotate → pull → push → descend → descend → grasp → approach | impedance_motion | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | linear_cartesian | impedance_control | impedance_control | impedance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | time_limit | time_limit | pose_tolerance | contact_detected | grasp_success | pose_tolerance | 6  | -0.1650 | 0.13 | ❌ rejected |
| 2 | rotate → pull → push → descend → descend → grasp → approach | impedance_motion | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | linear_cartesian | impedance_control | impedance_control | impedance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | time_limit | time_limit | pose_tolerance | contact_detected | grasp_success | pose_tolerance | 6  | -0.1646 | 0.13 | ✅ accepted |
| 1 | rotate → pull → push → descend → descend → grasp → approach | impedance_motion | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | linear_cartesian | impedance_control | impedance_control | impedance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | time_limit | time_limit | pose_tolerance | contact_detected | grasp_success | pose_tolerance | 6  | 0.4214 | 0.94 | ✅ accepted |

**Proposal policy**: task_score is near-perfect (0.94). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.943, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.421) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_pre_grasp
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.3
- id: reach_goal_pre_place
  offset:
  - 0.0
  - 0.0
  - 0.08
  weight: 0.3
- id: place
  weight: 0.4
phases:
- id: approach_above
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
    - 0.1
    tolerance: 0.03
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: approach_timeout
    when: before_phase
    predicate: force_below
    threshold: 10.0
    on_failure: abort
  subtask_id: reach_pre_grasp
- id: descend_to_grasp
  type: descend
  generator: linear_cartesian
  control: admittance_control
  termination: contact_detected
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: contact_force_ok
    when: during_phase
    predicate: force_below
    threshold: 15.0
    on_failure: abort
- id: grasp
  type: grasp
  control: position_control
  termination: grasp_success
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.0
  guards:
  - id: bilateral
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.5
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.005
- id: lift
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.04
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.08
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
- id: transport_to_goal
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
    - 0.08
    tolerance: 0.03
    orientation:
      mode: keep_current
  parameters:
    arc_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.12
      binds_to:
      - path: generator.arc_height
        mode: replace
    speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_goal_pre_place
- id: descend_to_goal
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
    tolerance: 0.025
    orientation:
      mode: keep_current
  parameters:
    place_z_offset:
      type: scalar
      range:
      - -0.05
      - 0.05
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: place

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_above** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.1], tolerance=0.03
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=approach_timeout, when=before_phase, predicate=force_below, on_failure=abort, threshold=10.0
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=contact_force_ok, when=during_phase, predicate=force_below, on_failure=abort, threshold=15.0
- **grasp** (`grasp`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=bilateral, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.5
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.005]
- **lift** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], tolerance=0.04
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **transport_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.08], tolerance=0.03
  - orientation: mode=keep_current
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_goal** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.025
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_z_offset: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.421
- **task_score** (E): 0.943
- **fitness_score**: 0.941  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.520

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above | 1.00 | 1.00 | 0.1475 |
| descend_to_grasp | 1.00 | 1.00 | 0.1139 |
| grasp | 1.00 | 1.00 | 0.0120 |
| lift | 1.00 | 1.00 | 0.1571 |
| transport_to_goal | 1.00 | 1.00 | 0.2233 |
| descend_to_goal | 1.00 | 1.00 | 0.0827 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, -0.014, 0.158) | (0.515, -0.017, 0.030)→(0.515, -0.017, 0.026) | 0.268→0.270 | 1.00 / 4.000 | 13.730 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.510, -0.014, 0.158)→(0.509, -0.016, 0.044) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.509, -0.016, 0.044)→(0.501, -0.016, 0.035) | (0.515, -0.017, 0.026)→(0.515, -0.016, 0.026) | 0.270→0.270 | 1.00 / 42.000 | 0.147 | 0.194 |
| lift | lift | 1.00 / step_budget | (0.501, -0.016, 0.035)→(0.499, -0.016, 0.192) | (0.515, -0.016, 0.026)→(0.510, -0.016, 0.181) | 0.270→0.235 | 1.00 / 38.667 | 0.087 | 0.519 |
| transport_to_goal | approach | 1.00 / step_budget | (0.499, -0.016, 0.192)→(0.604, 0.161, 0.262) | (0.510, -0.016, 0.181)→(0.619, 0.160, 0.244) | 0.235→0.079 | 1.00 / 22.333 | 55983.994 | 0.180 |
| descend_to_goal | descend | 1.00 / step_budget | (0.604, 0.161, 0.262)→(0.611, 0.174, 0.181) | (0.619, 0.160, 0.244)→(0.624, 0.174, 0.159) | 0.079→0.019 | 1.00 / 16.667 | 0.204 | 0.425 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.191
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.664
- phase_breakdown.reach_pre_grasp_score: 0.555
- phase_breakdown.reach_goal_pre_place_score: 0.551
- phase_breakdown.place_score: 0.830
- grasp_place_fitness: 0.980

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.980
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.450
- **K-run variance**: 0.0023
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.389


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.46405,"average_solve_count":306.0,"average_success_count":306.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.speed":0.04889,"descend_to_goal.place_z_offset":0.00695,"descend_to_goal.speed":0.07438,"descend_to_grasp.speed":0.07796,"lift.lift_height":0.16844,"lift.speed":0.04618,"transport_to_goal.arc_height":0.21947,"transport_to_goal.speed":0.0565},"optimized_scores":{"best_composite_score":0.44998,"best_fitness_score":0.96998,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":75.0,"contact_point_centroid":[0.53388,-0.02043,-0.00163],"force_p95":0.45596,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.47199,"mean_force":0.27128,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52085,-0.02019,0.03833]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":864.0,"contact_point_centroid":[0.60707,0.22748,0.26471],"force_p95":0.18885,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.4603,"mean_force":0.11534,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.60167,0.20906,0.26784]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":942.0,"contact_point_centroid":[0.60742,0.19068,0.26559],"force_p95":0.19057,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.41135,"mean_force":0.10755,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.60164,0.20899,0.26811]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3983.0,"contact_point_centroid":[0.51925,-0.00094,0.09963],"force_p95":0.09696,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2874,"mean_force":0.05783,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51915,-0.02015,0.09702]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4307.0,"contact_point_centroid":[0.51909,-0.03929,0.09942],"force_p95":0.09303,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27727,"mean_force":0.05501,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51916,-0.02015,0.0974]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53706,-0.02113,-0.0021],"force_p95":0.15163,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21612,"mean_force":0.13029,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52309,-0.02022,0.03893]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7213.0,"contact_point_centroid":[0.54852,0.07108,0.26534],"force_p95":0.11313,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21516,"mean_force":0.08216,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54433,0.05225,0.26327]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8262.0,"contact_point_centroid":[0.54868,0.03375,0.26534],"force_p95":0.10656,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17388,"mean_force":0.07442,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54438,0.05235,0.26396]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4089.0,"contact_point_centroid":[0.52311,-0.00099,0.04021],"force_p95":0.0794,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13887,"mean_force":0.05186,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52187,-0.0202,0.03752]},{"body_a":"world","body_b":"grasp_target","contact_count":872.0,"contact_point_centroid":[0.53702,-0.02132,-0.00185],"force_p95":0.13717,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12319,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.5124,-0.00799,0.2318]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52754,-0.01909,0.08695]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4961.0,"contact_point_centroid":[0.52305,-0.03932,0.0393],"force_p95":0.07175,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07914,"mean_force":0.04457,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52187,-0.0202,0.03753]}],"total_contact_groups":12},"final_pose_error":0.02498,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.6144,0.2173,0.21172],"final_tcp_position":[0.6046,0.21744,0.23639],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":0.47199,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":219.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":872.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.5271,-0.01707,0.15729],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13172,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53006,-0.02035,0.04703],"tcp_start":[0.5271,-0.01707,0.15729],"tcp_to_object_dist_end":0.02216,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53695,-0.02031,0.02566],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31615,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.14628,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10850.0,"raw_peak_contact_force":0.21612,"tcp_end":[0.52184,-0.0202,0.03749],"tcp_start":[0.53006,-0.02035,0.04703],"tcp_to_object_dist_end":0.01919,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":202.0,"n_steps_budget":1000.0,"object_pos_end":[0.53175,-0.02014,0.15386],"object_pos_start":[0.53695,-0.02031,0.02566],"object_to_goal_dist_end":0.2655,"object_to_goal_dist_start":0.31615,"object_z_max":0.15319,"peak_contact_force":0.08522,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":8365.0,"raw_peak_contact_force":0.47199,"tcp_end":[0.51933,-0.02013,0.16664],"tcp_start":[0.52184,-0.0202,0.03749],"tcp_to_object_dist_end":0.01783,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":20.0,"n_steps":608.0,"n_steps_budget":1000.0,"object_pos_end":[0.61347,0.20109,0.27433],"object_pos_start":[0.53175,-0.02014,0.15386],"object_to_goal_dist_end":0.0721,"object_to_goal_dist_start":0.2655,"object_z_max":0.29936,"peak_contact_force":0.12921,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":15475.0,"raw_peak_contact_force":0.21516,"subtask_id":"reach_goal_pre_place","tcp_end":[0.59973,0.20131,0.29622],"tcp_start":[0.51933,-0.02013,0.16664],"tcp_to_object_dist_end":0.02585,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":96.0,"n_steps_budget":1000.0,"object_pos_end":[0.6144,0.2173,0.21172],"object_pos_start":[0.61347,0.20109,0.27433],"object_to_goal_dist_end":0.01202,"object_to_goal_dist_start":0.0721,"object_z_max":0.27433,"peak_contact_force":0.1306,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1806.0,"raw_peak_contact_force":0.4603,"subtask_id":"place","tcp_end":[0.6046,0.21744,0.23639],"tcp_start":[0.59973,0.20131,0.29622],"tcp_to_object_dist_end":0.02654,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.34328,"average_solve_count":335.0,"average_success_count":335.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.speed":0.01287,"descend_to_goal.place_z_offset":-0.01836,"descend_to_goal.speed":0.07175,"descend_to_grasp.speed":0.07953,"lift.lift_height":0.22544,"lift.speed":0.05509,"transport_to_goal.arc_height":0.22933,"transport_to_goal.speed":0.06129},"optimized_scores":{"best_composite_score":0.35404,"best_fitness_score":0.87404,"best_task_score":0.82967},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"right_finger","body_b":"grasp_target","contact_count":1356.0,"contact_point_centroid":[0.62806,0.16706,0.22725],"force_p95":0.18238,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.5014,"mean_force":0.10439,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.62132,0.14832,0.22741]},{"body_a":"world","body_b":"grasp_target","contact_count":74.0,"contact_point_centroid":[0.54376,-0.02776,-0.00175],"force_p95":0.36871,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.41142,"mean_force":0.19134,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52824,-0.02721,0.0473]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1570.0,"contact_point_centroid":[0.62776,0.1303,0.22649],"force_p95":0.17005,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.40652,"mean_force":0.09061,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.62141,0.14847,0.22667]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5152.0,"contact_point_centroid":[0.52824,-0.008,0.13759],"force_p95":0.1024,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35048,"mean_force":0.06528,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52682,-0.02715,0.13643]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5773.0,"contact_point_centroid":[0.52811,-0.04611,0.13525],"force_p95":0.09665,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32525,"mean_force":0.05971,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.5268,-0.02715,0.13378]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54571,-0.02913,-0.00217],"force_p95":0.16833,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22658,"mean_force":0.13517,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.5306,-0.02728,0.04779]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4309.0,"contact_point_centroid":[0.57363,0.06813,0.27246],"force_p95":0.11779,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17057,"mean_force":0.08567,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.56826,0.04947,0.27236]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4891.0,"contact_point_centroid":[0.56975,0.02503,0.26958],"force_p95":0.11264,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16775,"mean_force":0.07886,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.56508,0.0436,0.26949]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4423.0,"contact_point_centroid":[0.53099,-0.00815,0.04755],"force_p95":0.08881,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1396,"mean_force":0.0525,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52938,-0.02724,0.04634]},{"body_a":"world","body_b":"grasp_target","contact_count":916.0,"contact_point_centroid":[0.5456,-0.02923,-0.00186],"force_p95":0.13709,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12316,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.51531,-0.01081,0.23257]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53478,-0.02593,0.09258]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4885.0,"contact_point_centroid":[0.53168,-0.04631,0.04861],"force_p95":0.08122,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08546,"mean_force":0.04625,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52939,-0.02724,0.04635]}],"total_contact_groups":12},"final_pose_error":0.02496,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.63397,0.15657,0.15021],"final_tcp_position":[0.62593,0.15719,0.18126],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":167951.73011,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":230.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":916.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.53409,-0.02348,0.1567],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13132,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53758,-0.02749,0.05618],"tcp_start":[0.53409,-0.02348,0.1567],"tcp_to_object_dist_end":0.03126,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54589,-0.0279,0.02532],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26024,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.16653,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11108.0,"raw_peak_contact_force":0.22658,"tcp_end":[0.52935,-0.02724,0.0463],"tcp_start":[0.53758,-0.02749,0.05618],"tcp_to_object_dist_end":0.02672,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":284.0,"n_steps_budget":1000.0,"object_pos_end":[0.54029,-0.02772,0.20765],"object_pos_start":[0.54589,-0.0279,0.02532],"object_to_goal_dist_end":0.21593,"object_to_goal_dist_start":0.26024,"object_z_max":0.20699,"peak_contact_force":0.10451,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":10999.0,"raw_peak_contact_force":0.41142,"tcp_end":[0.5274,-0.02715,0.2319],"tcp_start":[0.52935,-0.02724,0.0463],"tcp_to_object_dist_end":0.02747,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":388.0,"n_steps_budget":1000.0,"object_pos_end":[0.6293,0.14011,0.23709],"object_pos_start":[0.54029,-0.02772,0.20765],"object_to_goal_dist_end":0.06519,"object_to_goal_dist_start":0.21593,"object_z_max":0.26081,"peak_contact_force":167951.73011,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9200.0,"raw_peak_contact_force":0.17057,"subtask_id":"reach_goal_pre_place","tcp_end":[0.61845,0.14088,0.26613],"tcp_start":[0.5274,-0.02715,0.2319],"tcp_to_object_dist_end":0.03101,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":17.0,"n_steps":132.0,"n_steps_budget":1000.0,"object_pos_end":[0.63397,0.15657,0.15021],"object_pos_start":[0.6293,0.14011,0.23709],"object_to_goal_dist_end":0.02801,"object_to_goal_dist_start":0.06519,"object_z_max":0.23709,"peak_contact_force":0.24395,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2926.0,"raw_peak_contact_force":0.5014,"subtask_id":"place","tcp_end":[0.62593,0.15719,0.18126],"tcp_start":[0.61845,0.14088,0.26613],"tcp_to_object_dist_end":0.03208,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.99296,"average_solve_count":426.0,"average_success_count":426.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.speed":0.07256,"descend_to_goal.place_z_offset":-0.01977,"descend_to_goal.speed":0.01888,"descend_to_grasp.speed":0.04708,"lift.lift_height":0.19603,"lift.speed":0.0407,"transport_to_goal.arc_height":0.13287,"transport_to_goal.speed":0.04521},"optimized_scores":{"best_composite_score":0.46021,"best_fitness_score":0.98021,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":74.0,"contact_point_centroid":[0.4598,-3e-05,-0.00149],"force_p95":0.65234,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.67465,"mean_force":0.39593,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45027,-0.00024,0.02242]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1830.0,"contact_point_centroid":[0.60277,0.12479,0.18052],"force_p95":0.14066,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31401,"mean_force":0.09646,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.59711,0.14324,0.17979]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1832.0,"contact_point_centroid":[0.60288,0.16187,0.1805],"force_p95":0.13864,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2877,"mean_force":0.09916,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.59714,0.14327,0.17979]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4662.0,"contact_point_centroid":[0.44916,0.01891,0.09712],"force_p95":0.07692,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27417,"mean_force":0.05402,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44897,-0.00025,0.09523]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4694.0,"contact_point_centroid":[0.44918,-0.01939,0.09661],"force_p95":0.07841,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25356,"mean_force":0.0539,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44898,-0.00025,0.09473]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8476.0,"contact_point_centroid":[0.50192,0.03045,0.24501],"force_p95":0.10004,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15536,"mean_force":0.05955,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50004,0.04931,0.24357]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7647.0,"contact_point_centroid":[0.5031,0.06934,0.24531],"force_p95":0.10438,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14157,"mean_force":0.06455,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50111,0.05032,0.24329]},{"body_a":"world","body_b":"grasp_target","contact_count":804.0,"contact_point_centroid":[0.46286,-7e-05,-0.00184],"force_p95":0.13728,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12324,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.48462,-4e-05,0.23246]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.46283,-5e-05,-0.00201],"force_p95":0.12815,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13806,"mean_force":0.12422,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45226,-0.0002,0.02267]},{"body_a":"world","body_b":"grasp_target","contact_count":3116.0,"contact_point_centroid":[0.46286,-7e-05,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.46158,-0.0001,0.09046]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4389.0,"contact_point_centroid":[0.45112,0.01906,0.0239],"force_p95":0.07365,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09392,"mean_force":0.04931,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45115,-0.00022,0.02163]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5091.0,"contact_point_centroid":[0.45101,-0.01929,0.02348],"force_p95":0.06453,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08395,"mean_force":0.04268,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45115,-0.00022,0.02163]}],"total_contact_groups":12},"final_pose_error":0.02469,"key_states":{"actual_goal_position":[0.61015,0.15287,0.12219],"final_object_position":[0.62345,0.14835,0.11418],"final_tcp_position":[0.60265,0.14847,0.12553],"realised_goal_position":[0.61015,0.15287,0.12219],"realised_object_initial_position":[0.46286,-7e-05,0.03]},"peak_contact_force":40.94593,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":202.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.03],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.23148,"object_z_max":0.03,"peak_contact_force":40.94593,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":804.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.46795,-7e-05,0.15902],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13309,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":779.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3116.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.45869,-0.00012,0.02878],"tcp_start":[0.46795,-7e-05,0.15902],"tcp_to_object_dist_end":0.00499,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46271,-5e-05,0.02593],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.23322,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12822,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11280.0,"raw_peak_contact_force":0.13806,"tcp_end":[0.45112,-0.00022,0.0216],"tcp_start":[0.45869,-0.00012,0.02878],"tcp_to_object_dist_end":0.01237,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":234.0,"n_steps_budget":1000.0,"object_pos_end":[0.45865,-0.00023,0.18242],"object_pos_start":[0.46271,-5e-05,0.02593],"object_to_goal_dist_end":0.22365,"object_to_goal_dist_start":0.23322,"object_z_max":0.18173,"peak_contact_force":0.07204,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":9430.0,"raw_peak_contact_force":0.67465,"tcp_end":[0.44931,-0.00024,0.17824],"tcp_start":[0.45112,-0.00022,0.0216],"tcp_to_object_dist_end":0.01023,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":491.0,"n_steps_budget":1000.0,"object_pos_end":[0.61464,0.13947,0.21984],"object_pos_start":[0.45865,-0.00023,0.18242],"object_to_goal_dist_end":0.09867,"object_to_goal_dist_start":0.22365,"object_z_max":0.27561,"peak_contact_force":0.12122,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":16123.0,"raw_peak_contact_force":0.15536,"subtask_id":"reach_goal_pre_place","tcp_end":[0.59482,0.1396,0.22406],"tcp_start":[0.44931,-0.00024,0.17824],"tcp_to_object_dist_end":0.02026,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":17.0,"n_steps":170.0,"n_steps_budget":1000.0,"object_pos_end":[0.62345,0.14835,0.11418],"object_pos_start":[0.61464,0.13947,0.21984],"object_to_goal_dist_end":0.01617,"object_to_goal_dist_start":0.09867,"object_z_max":0.21984,"peak_contact_force":0.23861,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3662.0,"raw_peak_contact_force":0.31401,"subtask_id":"place","tcp_end":[0.60265,0.14847,0.12553],"tcp_start":[0.59482,0.1396,0.22406],"tcp_to_object_dist_end":0.0237,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```