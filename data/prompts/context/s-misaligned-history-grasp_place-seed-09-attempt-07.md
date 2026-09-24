## Search State

- **Seed**: 9
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8  | 0.4498 | 1.00 | ✅ accepted |
| 6 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8  | 0.4214 | 0.94 | ✅ accepted |
| 5 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8  | -0.0199 | 0.38 | ✅ accepted |
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 10  | -0.1646 | 0.13 | ✅ accepted |
| 3 | rotate → pull → push → descend → descend → grasp → approach | impedance_motion | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | linear_cartesian | impedance_control | impedance_control | impedance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | time_limit | time_limit | pose_tolerance | contact_detected | grasp_success | pose_tolerance | 6  | 0.4499 | 1.00 | ✅ accepted |

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

## Current Skill (Q=0.450) — your mutation base

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

- **Composite score**: 0.450
- **task_score** (E): 1.000
- **fitness_score**: 0.970  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.520

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above | 1.00 | 1.00 | 0.1473 |
| descend_to_grasp | 1.00 | 1.00 | 0.1141 |
| grasp | 1.00 | 1.00 | 0.0119 |
| lift | 1.00 | 1.00 | 0.1495 |
| transport_to_goal | 1.00 | 1.00 | 0.2210 |
| descend_to_goal | 1.00 | 1.00 | 0.0759 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, -0.014, 0.158) | (0.515, -0.017, 0.030)→(0.515, -0.017, 0.026) | 0.268→0.270 | 1.00 / 4.000 | 27.129 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.510, -0.014, 0.158)→(0.509, -0.016, 0.044) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.509, -0.016, 0.044)→(0.501, -0.016, 0.035) | (0.515, -0.017, 0.026)→(0.515, -0.016, 0.026) | 0.270→0.270 | 1.00 / 42.000 | 0.145 | 0.194 |
| lift | lift | 1.00 / step_budget | (0.501, -0.016, 0.035)→(0.499, -0.016, 0.185) | (0.515, -0.016, 0.026)→(0.510, -0.016, 0.174) | 0.270→0.230 | 1.00 / 38.000 | 0.081 | 0.505 |
| transport_to_goal | approach | 1.00 / step_budget | (0.499, -0.016, 0.185)→(0.603, 0.159, 0.259) | (0.510, -0.016, 0.174)→(0.614, 0.159, 0.238) | 0.230→0.073 | 1.00 / 27.333 | 0.118 | 0.250 |
| descend_to_goal | descend | 1.00 / step_budget | (0.603, 0.159, 0.259)→(0.610, 0.174, 0.185) | (0.614, 0.159, 0.238)→(0.622, 0.175, 0.162) | 0.073→0.018 | 1.00 / 19.000 | 0.114 | 0.442 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.256
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.564
- phase_breakdown.reach_pre_grasp_score: 0.552
- phase_breakdown.reach_goal_pre_place_score: 0.551
- phase_breakdown.place_score: 0.584
- grasp_place_fitness: 0.980

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.980
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.447
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.377


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.17549,"average_solve_count":359.0,"average_success_count":359.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.speed":0.07772,"descend_to_goal.place_z_offset":-0.01466,"descend_to_goal.speed":0.05054,"descend_to_grasp.speed":0.07362,"lift.lift_height":0.23346,"lift.speed":0.0403,"transport_to_goal.arc_height":0.24714,"transport_to_goal.speed":0.02902},"optimized_scores":{"best_composite_score":0.44742,"best_fitness_score":0.96742,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"right_finger","body_b":"grasp_target","contact_count":1446.0,"contact_point_centroid":[0.60757,0.22882,0.25956],"force_p95":0.12923,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.52334,"mean_force":0.09411,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.60185,0.2101,0.25807]},{"body_a":"world","body_b":"grasp_target","contact_count":80.0,"contact_point_centroid":[0.53383,-0.0202,-0.00164],"force_p95":0.40808,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.42316,"mean_force":0.24779,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52068,-0.02009,0.04077]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1571.0,"contact_point_centroid":[0.60778,0.19164,0.2598],"force_p95":0.12759,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.39366,"mean_force":0.08586,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.60183,0.21003,0.25841]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5713.0,"contact_point_centroid":[0.51934,-0.00086,0.13074],"force_p95":0.08601,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26752,"mean_force":0.05757,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51913,-0.02005,0.12815]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6283.0,"contact_point_centroid":[0.51928,-0.03915,0.13243],"force_p95":0.08181,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25997,"mean_force":0.05396,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51916,-0.02005,0.13049]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53707,-0.02114,-0.00211],"force_p95":0.1533,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21602,"mean_force":0.13076,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52296,-0.02013,0.04143]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4090.0,"contact_point_centroid":[0.52304,-0.0009,0.0427],"force_p95":0.07964,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1428,"mean_force":0.05186,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52174,-0.02011,0.04002]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7481.0,"contact_point_centroid":[0.55118,0.08106,0.29761],"force_p95":0.10471,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13861,"mean_force":0.06829,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54859,0.06207,0.29561]},{"body_a":"world","body_b":"grasp_target","contact_count":836.0,"contact_point_centroid":[0.53702,-0.02132,-0.00185],"force_p95":0.13728,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12321,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.51256,-0.00803,0.23153]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8766.0,"contact_point_centroid":[0.55137,0.04427,0.29683],"force_p95":0.09467,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12894,"mean_force":0.06003,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54894,0.06302,0.29555]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52745,-0.01902,0.08814]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4969.0,"contact_point_centroid":[0.52296,-0.03923,0.04179],"force_p95":0.07204,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07609,"mean_force":0.04451,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52175,-0.02011,0.04003]}],"total_contact_groups":12},"final_pose_error":0.02437,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.6175,0.2192,0.19145],"final_tcp_position":[0.60499,0.21922,0.21495],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":0.52334,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":210.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":836.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.52703,-0.01698,0.15794],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13237,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.52991,-0.02026,0.04953],"tcp_start":[0.52703,-0.01698,0.15794],"tcp_to_object_dist_end":0.02459,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53696,-0.02028,0.02563],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31614,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.14784,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10859.0,"raw_peak_contact_force":0.21602,"tcp_end":[0.52171,-0.02011,0.03999],"tcp_start":[0.52991,-0.02026,0.04953],"tcp_to_object_dist_end":0.02094,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":300.0,"n_steps_budget":1000.0,"object_pos_end":[0.53198,-0.02002,0.21795],"object_pos_start":[0.53696,-0.02028,0.02563],"object_to_goal_dist_end":0.26008,"object_to_goal_dist_start":0.31614,"object_z_max":0.21729,"peak_contact_force":0.08683,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":12076.0,"raw_peak_contact_force":0.42316,"tcp_end":[0.51981,-0.02005,0.23389],"tcp_start":[0.52171,-0.02011,0.03999],"tcp_to_object_dist_end":0.02005,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":521.0,"n_steps_budget":1000.0,"object_pos_end":[0.61262,0.20196,0.27659],"object_pos_start":[0.53198,-0.02002,0.21795],"object_to_goal_dist_end":0.07386,"object_to_goal_dist_start":0.26008,"object_z_max":0.30686,"peak_contact_force":0.1105,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":16247.0,"raw_peak_contact_force":0.13861,"subtask_id":"reach_goal_pre_place","tcp_end":[0.59991,0.2018,0.2982],"tcp_start":[0.51981,-0.02005,0.23389],"tcp_to_object_dist_end":0.02508,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":134.0,"n_steps_budget":1000.0,"object_pos_end":[0.6175,0.2192,0.19145],"object_pos_start":[0.61262,0.20196,0.27659],"object_to_goal_dist_end":0.01948,"object_to_goal_dist_start":0.07386,"object_z_max":0.27659,"peak_contact_force":0.11048,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3017.0,"raw_peak_contact_force":0.52334,"subtask_id":"place","tcp_end":[0.60499,0.21922,0.21495],"tcp_start":[0.59991,0.2018,0.2982],"tcp_to_object_dist_end":0.02663,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.38951,"average_solve_count":267.0,"average_success_count":267.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.speed":0.07292,"descend_to_goal.place_z_offset":-0.00345,"descend_to_goal.speed":0.05175,"descend_to_grasp.speed":0.07985,"lift.lift_height":0.16937,"lift.speed":0.02989,"transport_to_goal.arc_height":0.17189,"transport_to_goal.speed":0.13495},"optimized_scores":{"best_composite_score":0.44201,"best_fitness_score":0.96201,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"right_finger","body_b":"grasp_target","contact_count":1126.0,"contact_point_centroid":[0.62705,0.16604,0.2316],"force_p95":0.15801,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.44494,"mean_force":0.10153,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.62125,0.14806,0.23368]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":914.0,"contact_point_centroid":[0.62704,0.12927,0.23505],"force_p95":0.18847,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.42192,"mean_force":0.11619,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.62088,0.14733,0.23711]},{"body_a":"world","body_b":"grasp_target","contact_count":96.0,"contact_point_centroid":[0.54269,-0.02799,-0.00171],"force_p95":0.32693,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.3633,"mean_force":0.19489,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52826,-0.02731,0.04478]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5853.0,"contact_point_centroid":[0.56177,0.049,0.24869],"force_p95":0.12377,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34728,"mean_force":0.07833,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55741,0.03034,0.24782]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5791.0,"contact_point_centroid":[0.56375,0.01499,0.25054],"force_p95":0.12439,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32239,"mean_force":0.08084,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55928,0.03372,0.24959]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3621.0,"contact_point_centroid":[0.52668,-0.04651,0.10498],"force_p95":0.10029,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28391,"mean_force":0.0658,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52662,-0.02724,0.10239]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54569,-0.02912,-0.00216],"force_p95":0.16443,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22663,"mean_force":0.13404,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53071,-0.02738,0.04557]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4725.0,"contact_point_centroid":[0.52645,-0.0083,0.10305],"force_p95":0.09018,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21677,"mean_force":0.05246,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.5266,-0.02724,0.10043]},{"body_a":"world","body_b":"grasp_target","contact_count":864.0,"contact_point_centroid":[0.5456,-0.02923,-0.00185],"force_p95":0.13725,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12319,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.51602,-0.01112,0.23083]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53494,-0.02599,0.09138]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4751.0,"contact_point_centroid":[0.53104,-0.00828,0.04679],"force_p95":0.07322,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11384,"mean_force":0.0451,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52948,-0.02734,0.04412]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4697.0,"contact_point_centroid":[0.53127,-0.04662,0.04624],"force_p95":0.08473,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09028,"mean_force":0.04938,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52949,-0.02734,0.04413]}],"total_contact_groups":12},"final_pose_error":0.0244,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.63468,0.15896,0.15873],"final_tcp_position":[0.62566,0.15648,0.19521],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":0.44494,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":217.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":864.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.53424,-0.02351,0.15657],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13117,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53764,-0.02759,0.05389],"tcp_start":[0.53424,-0.02351,0.15657],"tcp_to_object_dist_end":0.02903,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54569,-0.02809,0.02545],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26037,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.15946,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11248.0,"raw_peak_contact_force":0.22663,"tcp_end":[0.52945,-0.02734,0.04408],"tcp_start":[0.53764,-0.02759,0.05389],"tcp_to_object_dist_end":0.02472,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":213.0,"n_steps_budget":1000.0,"object_pos_end":[0.53935,-0.02754,0.15458],"object_pos_start":[0.54569,-0.02809,0.02545],"object_to_goal_dist_end":0.21514,"object_to_goal_dist_start":0.26037,"object_z_max":0.15392,"peak_contact_force":0.08412,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":8442.0,"raw_peak_contact_force":0.3633,"tcp_end":[0.5269,-0.02723,0.1738],"tcp_start":[0.52945,-0.02734,0.04408],"tcp_to_object_dist_end":0.0229,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":441.0,"n_steps_budget":1000.0,"object_pos_end":[0.62792,0.14111,0.23484],"object_pos_start":[0.53935,-0.02754,0.15458],"object_to_goal_dist_end":0.06282,"object_to_goal_dist_start":0.21514,"object_z_max":0.25943,"peak_contact_force":0.12386,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":11644.0,"raw_peak_contact_force":0.34728,"subtask_id":"reach_goal_pre_place","tcp_end":[0.61859,0.14085,0.26672],"tcp_start":[0.5269,-0.02723,0.1738],"tcp_to_object_dist_end":0.03321,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":6.0,"n_steps":117.0,"n_steps_budget":1000.0,"object_pos_end":[0.63468,0.15896,0.15873],"object_pos_start":[0.62792,0.14111,0.23484],"object_to_goal_dist_end":0.01923,"object_to_goal_dist_start":0.06282,"object_z_max":0.23484,"peak_contact_force":0.12249,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2040.0,"raw_peak_contact_force":0.44494,"subtask_id":"place","tcp_end":[0.62566,0.15648,0.19521],"tcp_start":[0.61859,0.14085,0.26672],"tcp_to_object_dist_end":0.03765,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.20377,"average_solve_count":265.0,"average_success_count":265.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.speed":0.04562,"descend_to_goal.place_z_offset":0.00263,"descend_to_goal.speed":0.05655,"descend_to_grasp.speed":0.04816,"lift.lift_height":0.16405,"lift.speed":0.05343,"transport_to_goal.arc_height":0.19062,"transport_to_goal.speed":0.14416},"optimized_scores":{"best_composite_score":0.46017,"best_fitness_score":0.98017,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":68.0,"contact_point_centroid":[0.46063,-3e-05,-0.00146],"force_p95":0.65684,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.72915,"mean_force":0.3116,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45018,-0.00024,0.0225]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1507.0,"contact_point_centroid":[0.59741,0.12061,0.18263],"force_p95":0.11773,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35629,"mean_force":0.07959,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.59395,0.13962,0.18167]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3672.0,"contact_point_centroid":[0.44914,0.01891,0.08222],"force_p95":0.07827,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29483,"mean_force":0.05441,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44896,-0.00026,0.08032]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1900.0,"contact_point_centroid":[0.59626,0.15804,0.18248],"force_p95":0.10016,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28008,"mean_force":0.06475,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.59389,0.13956,0.18205]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3724.0,"contact_point_centroid":[0.44915,-0.01938,0.08138],"force_p95":0.07859,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27565,"mean_force":0.05407,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44898,-0.00026,0.07951]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6954.0,"contact_point_centroid":[0.50644,0.03457,0.20954],"force_p95":0.11211,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26452,"mean_force":0.06404,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50466,0.05345,0.20816]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6995.0,"contact_point_centroid":[0.51145,0.07688,0.21199],"force_p95":0.10051,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21741,"mean_force":0.05894,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50958,0.05812,0.21037]},{"body_a":"world","body_b":"grasp_target","contact_count":832.0,"contact_point_centroid":[0.46286,-7e-05,-0.00184],"force_p95":0.13728,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12321,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.48472,-4e-05,0.23322]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.46283,-5e-05,-0.00201],"force_p95":0.12815,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13805,"mean_force":0.12422,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45225,-0.0002,0.0226]},{"body_a":"world","body_b":"grasp_target","contact_count":3120.0,"contact_point_centroid":[0.46286,-7e-05,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.46163,-0.0001,0.09059]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4389.0,"contact_point_centroid":[0.45111,0.01906,0.02384],"force_p95":0.07365,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09392,"mean_force":0.04931,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45115,-0.00022,0.02156]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5091.0,"contact_point_centroid":[0.451,-0.01929,0.02342],"force_p95":0.06453,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08393,"mean_force":0.04268,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45115,-0.00022,0.02156]}],"total_contact_groups":12},"final_pose_error":0.02457,"key_states":{"actual_goal_position":[0.61015,0.15287,0.12219],"final_object_position":[0.61491,0.146,0.1345],"final_tcp_position":[0.60039,0.14598,0.14629],"realised_goal_position":[0.61015,0.15287,0.12219],"realised_object_initial_position":[0.46286,-7e-05,0.03]},"peak_contact_force":81.14186,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":209.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.03],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.23148,"object_z_max":0.03,"peak_contact_force":81.14186,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":832.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.46804,-7e-05,0.15922],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1333,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":780.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3120.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.45868,-0.00012,0.02871],"tcp_start":[0.46804,-7e-05,0.15922],"tcp_to_object_dist_end":0.00496,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46271,-5e-05,0.02593],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.23322,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12822,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11280.0,"raw_peak_contact_force":0.13805,"tcp_end":[0.45112,-0.00022,0.02153],"tcp_start":[0.45868,-0.00012,0.02871],"tcp_to_object_dist_end":0.0124,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":185.0,"n_steps_budget":1000.0,"object_pos_end":[0.46016,-0.00024,0.14973],"object_pos_start":[0.46271,-5e-05,0.02593],"object_to_goal_dist_end":0.21609,"object_to_goal_dist_start":0.23322,"object_z_max":0.14903,"peak_contact_force":0.07264,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":7464.0,"raw_peak_contact_force":0.72915,"tcp_end":[0.44913,-0.00024,0.14628],"tcp_start":[0.45112,-0.00022,0.02153],"tcp_to_object_dist_end":0.01156,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":36.0,"n_steps":400.0,"n_steps_budget":1000.0,"object_pos_end":[0.60263,0.13388,0.20295],"object_pos_start":[0.46016,-0.00024,0.14973],"object_to_goal_dist_end":0.08331,"object_to_goal_dist_start":0.21609,"object_z_max":0.23059,"peak_contact_force":0.11944,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":13949.0,"raw_peak_contact_force":0.26452,"subtask_id":"reach_goal_pre_place","tcp_end":[0.58969,0.13422,0.21332],"tcp_start":[0.44913,-0.00024,0.14628],"tcp_to_object_dist_end":0.01658,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":113.0,"n_steps_budget":1000.0,"object_pos_end":[0.61491,0.146,0.1345],"object_pos_start":[0.60263,0.13388,0.20295],"object_to_goal_dist_end":0.01488,"object_to_goal_dist_start":0.08331,"object_z_max":0.20295,"peak_contact_force":0.10791,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3407.0,"raw_peak_contact_force":0.35629,"subtask_id":"place","tcp_end":[0.60039,0.14598,0.14629],"tcp_start":[0.58969,0.13422,0.21332],"tcp_to_object_dist_end":0.0187,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```