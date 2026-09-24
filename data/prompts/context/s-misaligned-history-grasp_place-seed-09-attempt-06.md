## Search State

- **Seed**: 9
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8  | 0.4214 | 0.94 | ✅ accepted |
| 5 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8  | -0.0199 | 0.38 | ✅ accepted |
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 10  | -0.1646 | 0.13 | ✅ accepted |
| 3 | rotate → pull → push → descend → descend → grasp → approach | impedance_motion | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | linear_cartesian | impedance_control | impedance_control | impedance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | time_limit | time_limit | pose_tolerance | contact_detected | grasp_success | pose_tolerance | 6  | -0.1650 | 0.13 | ❌ rejected |
| 2 | rotate → pull → push → descend → descend → grasp → approach | impedance_motion | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | linear_cartesian | impedance_control | impedance_control | impedance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | time_limit | time_limit | pose_tolerance | contact_detected | grasp_success | pose_tolerance | 6  | 0.4498 | 1.00 | ✅ accepted |

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
| approach_above | 1.00 | 1.00 | 0.1475 |
| descend_to_grasp | 1.00 | 1.00 | 0.1139 |
| grasp | 1.00 | 1.00 | 0.0120 |
| lift | 1.00 | 1.00 | 0.1187 |
| transport_to_goal | 1.00 | 1.00 | 0.2327 |
| descend_to_goal | 1.00 | 1.00 | 0.0697 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, -0.014, 0.158) | (0.515, -0.017, 0.030)→(0.515, -0.017, 0.026) | 0.268→0.270 | 1.00 / 4.000 | 13.071 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.510, -0.014, 0.158)→(0.509, -0.016, 0.044) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.509, -0.016, 0.044)→(0.501, -0.016, 0.035) | (0.515, -0.017, 0.026)→(0.515, -0.016, 0.026) | 0.270→0.270 | 1.00 / 42.333 | 0.148 | 0.194 |
| lift | lift | 1.00 / step_budget | (0.501, -0.016, 0.035)→(0.498, -0.016, 0.154) | (0.515, -0.016, 0.026)→(0.511, -0.016, 0.143) | 0.270→0.232 | 1.00 / 38.333 | 0.085 | 0.546 |
| transport_to_goal | approach | 1.00 / step_budget | (0.498, -0.016, 0.154)→(0.603, 0.159, 0.258) | (0.511, -0.016, 0.143)→(0.616, 0.159, 0.237) | 0.232→0.072 | 1.00 / 24.000 | 0.109 | 0.221 |
| descend_to_goal | descend | 1.00 / step_budget | (0.603, 0.159, 0.258)→(0.610, 0.173, 0.190) | (0.616, 0.159, 0.237)→(0.623, 0.173, 0.167) | 0.072→0.013 | 1.00 / 22.667 | 0.123 | 0.462 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.435
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.643
- phase_breakdown.reach_pre_grasp_score: 0.557
- phase_breakdown.reach_goal_pre_place_score: 0.551
- phase_breakdown.place_score: 0.778
- grasp_place_fitness: 0.980

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.980
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.450
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.333


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.05556,"average_solve_count":306.0,"average_success_count":306.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.speed":0.05984,"descend_to_goal.place_z_offset":0.01069,"descend_to_goal.speed":0.04746,"descend_to_grasp.speed":0.07806,"lift.lift_height":0.17524,"lift.speed":0.05887,"transport_to_goal.arc_height":0.24113,"transport_to_goal.speed":0.03147},"optimized_scores":{"best_composite_score":0.44989,"best_fitness_score":0.96989,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"right_finger","body_b":"grasp_target","contact_count":938.0,"contact_point_centroid":[0.60722,0.22696,0.27086],"force_p95":0.15367,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.51264,"mean_force":0.10337,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.60119,0.2081,0.26978]},{"body_a":"world","body_b":"grasp_target","contact_count":70.0,"contact_point_centroid":[0.53415,-0.02014,-0.00162],"force_p95":0.44294,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.49511,"mean_force":0.24141,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52077,-0.02018,0.03854]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1167.0,"contact_point_centroid":[0.60759,0.19002,0.26943],"force_p95":0.12339,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.39281,"mean_force":0.08295,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.60127,0.20833,0.26897]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3733.0,"contact_point_centroid":[0.51977,-0.00095,0.10197],"force_p95":0.09562,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3048,"mean_force":0.0636,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51915,-0.02014,0.09918]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4294.0,"contact_point_centroid":[0.51969,-0.03919,0.10225],"force_p95":0.08743,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29627,"mean_force":0.05747,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51915,-0.02014,0.10025]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53706,-0.02113,-0.0021],"force_p95":0.15184,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21615,"mean_force":0.13034,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52309,-0.02022,0.03902]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8248.0,"contact_point_centroid":[0.54657,0.06944,0.26385],"force_p95":0.10927,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14388,"mean_force":0.07136,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54367,0.05048,0.26185]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4089.0,"contact_point_centroid":[0.52311,-0.00099,0.04029],"force_p95":0.07942,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13905,"mean_force":0.05187,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52187,-0.0202,0.03761]},{"body_a":"world","body_b":"grasp_target","contact_count":864.0,"contact_point_centroid":[0.53702,-0.02132,-0.00185],"force_p95":0.13725,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12319,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.51253,-0.00804,0.2315]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9709.0,"contact_point_centroid":[0.5474,0.03418,0.264],"force_p95":0.09662,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13718,"mean_force":0.06252,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54457,0.05287,0.26274]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52753,-0.01908,0.08706]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4962.0,"contact_point_centroid":[0.52305,-0.03931,0.03939],"force_p95":0.07178,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07889,"mean_force":0.04456,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52187,-0.0202,0.03762]}],"total_contact_groups":12},"final_pose_error":0.02454,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.61815,0.21717,0.21659],"final_tcp_position":[0.60435,0.21692,0.2393],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":0.51264,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":217.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":864.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.5271,-0.01705,0.15739],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13182,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53006,-0.02035,0.04712],"tcp_start":[0.5271,-0.01705,0.15739],"tcp_to_object_dist_end":0.02224,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53695,-0.02031,0.02565],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31615,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.14646,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10851.0,"raw_peak_contact_force":0.21615,"tcp_end":[0.52184,-0.0202,0.03758],"tcp_start":[0.53006,-0.02035,0.04712],"tcp_to_object_dist_end":0.01925,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":209.0,"n_steps_budget":1000.0,"object_pos_end":[0.5328,-0.0201,0.15954],"object_pos_start":[0.53695,-0.02031,0.02565],"object_to_goal_dist_end":0.26407,"object_to_goal_dist_start":0.31615,"object_z_max":0.15888,"peak_contact_force":0.08688,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":8097.0,"raw_peak_contact_force":0.49511,"tcp_end":[0.51939,-0.02013,0.17323],"tcp_start":[0.52184,-0.0202,0.03758],"tcp_to_object_dist_end":0.01916,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":598.0,"n_steps_budget":1000.0,"object_pos_end":[0.61249,0.20105,0.27319],"object_pos_start":[0.5328,-0.0201,0.15954],"object_to_goal_dist_end":0.07103,"object_to_goal_dist_start":0.26407,"object_z_max":0.29383,"peak_contact_force":0.11044,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":17957.0,"raw_peak_contact_force":0.14388,"subtask_id":"reach_goal_pre_place","tcp_end":[0.59952,0.20096,0.29425],"tcp_start":[0.51939,-0.02013,0.17323],"tcp_to_object_dist_end":0.02473,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":94.0,"n_steps_budget":1000.0,"object_pos_end":[0.61815,0.21717,0.21659],"object_pos_start":[0.61249,0.20105,0.27319],"object_to_goal_dist_end":0.01605,"object_to_goal_dist_start":0.07103,"object_z_max":0.27319,"peak_contact_force":0.15274,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2105.0,"raw_peak_contact_force":0.51264,"subtask_id":"place","tcp_end":[0.60435,0.21692,0.2393],"tcp_start":[0.59952,0.20096,0.29425],"tcp_to_object_dist_end":0.02658,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.56275,"average_solve_count":247.0,"average_success_count":247.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.speed":0.06933,"descend_to_goal.place_z_offset":0.0035,"descend_to_goal.speed":0.06715,"descend_to_grasp.speed":0.07908,"lift.lift_height":0.15834,"lift.speed":0.05358,"transport_to_goal.arc_height":0.23638,"transport_to_goal.speed":0.06179},"optimized_scores":{"best_composite_score":0.43934,"best_fitness_score":0.95934,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"right_finger","body_b":"grasp_target","contact_count":1067.0,"contact_point_centroid":[0.62694,0.16591,0.23248],"force_p95":0.15258,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.44332,"mean_force":0.09558,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.62081,0.14711,0.23216]},{"body_a":"world","body_b":"grasp_target","contact_count":75.0,"contact_point_centroid":[0.54288,-0.02748,-0.00174],"force_p95":0.37653,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.41392,"mean_force":0.21138,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52834,-0.02722,0.04728]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3297.0,"contact_point_centroid":[0.52785,-0.00798,0.1033],"force_p95":0.11143,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34484,"mean_force":0.0677,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52674,-0.02715,0.10188]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1219.0,"contact_point_centroid":[0.62665,0.12875,0.23148],"force_p95":0.14979,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32384,"mean_force":0.08443,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.62089,0.14727,0.2315]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3877.0,"contact_point_centroid":[0.52777,-0.04613,0.10164],"force_p95":0.10203,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3191,"mean_force":0.06053,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52674,-0.02715,0.09985]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54571,-0.02913,-0.00217],"force_p95":0.16923,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22764,"mean_force":0.13522,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53062,-0.02728,0.0477]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7132.0,"contact_point_centroid":[0.56057,0.01302,0.23033],"force_p95":0.10171,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16999,"mean_force":0.06517,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55761,0.03172,0.22966]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5991.0,"contact_point_centroid":[0.56187,0.05199,0.22894],"force_p95":0.11568,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15501,"mean_force":0.07477,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55841,0.0331,0.22894]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4395.0,"contact_point_centroid":[0.53102,-0.00811,0.04753],"force_p95":0.08559,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14294,"mean_force":0.05282,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.5294,-0.02724,0.04625]},{"body_a":"world","body_b":"grasp_target","contact_count":872.0,"contact_point_centroid":[0.5456,-0.02923,-0.00185],"force_p95":0.13717,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12319,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.51594,-0.01111,0.23085]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53482,-0.02593,0.09253]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5158.0,"contact_point_centroid":[0.53198,-0.04631,0.0489],"force_p95":0.07827,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08198,"mean_force":0.04408,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52941,-0.02724,0.04626]}],"total_contact_groups":12},"final_pose_error":0.02456,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.63545,0.1544,0.17177],"final_tcp_position":[0.625,0.15515,0.20155],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":0.44332,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":219.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":872.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.53416,-0.02347,0.15675],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13135,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53761,-0.02749,0.0561],"tcp_start":[0.53416,-0.02347,0.15675],"tcp_to_object_dist_end":0.03117,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54587,-0.02785,0.02532],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26021,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.16796,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11353.0,"raw_peak_contact_force":0.22764,"tcp_end":[0.52938,-0.02724,0.04622],"tcp_start":[0.53761,-0.02749,0.0561],"tcp_to_object_dist_end":0.02662,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":186.0,"n_steps_budget":1000.0,"object_pos_end":[0.53999,-0.02785,0.14226],"object_pos_start":[0.54587,-0.02785,0.02532],"object_to_goal_dist_end":0.21676,"object_to_goal_dist_start":0.26021,"object_z_max":0.1416,"peak_contact_force":0.09491,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":7249.0,"raw_peak_contact_force":0.41392,"tcp_end":[0.5268,-0.02714,0.16484],"tcp_start":[0.52938,-0.02724,0.04622],"tcp_to_object_dist_end":0.02616,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":452.0,"n_steps_budget":1000.0,"object_pos_end":[0.62854,0.13854,0.23073],"object_pos_start":[0.53999,-0.02785,0.14226],"object_to_goal_dist_end":0.06008,"object_to_goal_dist_start":0.21676,"object_z_max":0.24039,"peak_contact_force":0.10095,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":13123.0,"raw_peak_contact_force":0.16999,"subtask_id":"reach_goal_pre_place","tcp_end":[0.61765,0.13964,0.25909],"tcp_start":[0.5268,-0.02714,0.16484],"tcp_to_object_dist_end":0.03039,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":96.0,"n_steps_budget":1000.0,"object_pos_end":[0.63545,0.1544,0.17177],"object_pos_start":[0.62854,0.13854,0.23073],"object_to_goal_dist_end":0.01201,"object_to_goal_dist_start":0.06008,"object_z_max":0.23073,"peak_contact_force":0.10361,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2286.0,"raw_peak_contact_force":0.44332,"subtask_id":"place","tcp_end":[0.625,0.15515,0.20155],"tcp_start":[0.61765,0.13964,0.25909],"tcp_to_object_dist_end":0.03157,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.36965,"average_solve_count":257.0,"average_success_count":257.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.speed":0.06133,"descend_to_goal.place_z_offset":-0.01481,"descend_to_goal.speed":0.05814,"descend_to_grasp.speed":0.0519,"lift.lift_height":0.14098,"lift.speed":0.04859,"transport_to_goal.arc_height":0.128,"transport_to_goal.speed":0.1111},"optimized_scores":{"best_composite_score":0.46015,"best_fitness_score":0.98015,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":68.0,"contact_point_centroid":[0.46057,-2e-05,-0.00151],"force_p95":0.68912,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.7303,"mean_force":0.33896,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45018,-0.00024,0.02235]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1740.0,"contact_point_centroid":[0.60054,0.12349,0.17682],"force_p95":0.13512,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.42921,"mean_force":0.08354,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.5964,0.14225,0.1764]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1963.0,"contact_point_centroid":[0.60133,0.16065,0.17793],"force_p95":0.12532,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.39902,"mean_force":0.07855,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.59631,0.14216,0.17725]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6562.0,"contact_point_centroid":[0.49275,0.02006,0.21158],"force_p95":0.12465,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34948,"mean_force":0.07991,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.48899,0.03886,0.20986]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6945.0,"contact_point_centroid":[0.50009,0.06417,0.21786],"force_p95":0.1119,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30233,"mean_force":0.07591,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.49602,0.04548,0.21603]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3054.0,"contact_point_centroid":[0.44907,0.01891,0.07032],"force_p95":0.08475,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29766,"mean_force":0.05529,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44889,-0.00026,0.06843]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3102.0,"contact_point_centroid":[0.44907,-0.01939,0.06957],"force_p95":0.08536,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.274,"mean_force":0.05492,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44891,-0.00026,0.06771]},{"body_a":"world","body_b":"grasp_target","contact_count":820.0,"contact_point_centroid":[0.46286,-7e-05,-0.00184],"force_p95":0.13728,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12322,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.48465,-4e-05,0.23255]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.46283,-5e-05,-0.00201],"force_p95":0.12816,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13807,"mean_force":0.12422,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45223,-0.0002,0.02262]},{"body_a":"world","body_b":"grasp_target","contact_count":3112.0,"contact_point_centroid":[0.46286,-7e-05,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.46158,-0.0001,0.0904]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4389.0,"contact_point_centroid":[0.4511,0.01906,0.02387],"force_p95":0.07364,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09392,"mean_force":0.04931,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45113,-0.00022,0.02158]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5091.0,"contact_point_centroid":[0.45099,-0.01929,0.02345],"force_p95":0.06453,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08394,"mean_force":0.04268,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45113,-0.00022,0.02158]}],"total_contact_groups":12},"final_pose_error":0.02481,"key_states":{"actual_goal_position":[0.61015,0.15287,0.12219],"final_object_position":[0.61516,0.14767,0.11349],"final_tcp_position":[0.602,0.14772,0.13024],"realised_goal_position":[0.61015,0.15287,0.12219],"realised_object_initial_position":[0.46286,-7e-05,0.03]},"peak_contact_force":38.96873,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":206.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.03],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.23148,"object_z_max":0.03,"peak_contact_force":38.96873,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":820.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.46798,-7e-05,0.15883],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13291,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":778.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3112.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.45867,-0.00012,0.02873],"tcp_start":[0.46798,-7e-05,0.15883],"tcp_to_object_dist_end":0.00499,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46271,-5e-05,0.02593],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.23322,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12822,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11280.0,"raw_peak_contact_force":0.13807,"tcp_end":[0.4511,-0.00022,0.02155],"tcp_start":[0.45867,-0.00012,0.02873],"tcp_to_object_dist_end":0.01241,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":154.0,"n_steps_budget":1000.0,"object_pos_end":[0.45896,-0.00025,0.12723],"object_pos_start":[0.46271,-5e-05,0.02593],"object_to_goal_dist_end":0.21524,"object_to_goal_dist_start":0.23322,"object_z_max":0.12653,"peak_contact_force":0.07207,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":6224.0,"raw_peak_contact_force":0.7303,"tcp_end":[0.44897,-0.00025,0.12319],"tcp_start":[0.4511,-0.00022,0.02155],"tcp_to_object_dist_end":0.01078,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":509.0,"n_steps_budget":1000.0,"object_pos_end":[0.60667,0.13706,0.20617],"object_pos_start":[0.45896,-0.00025,0.12723],"object_to_goal_dist_end":0.08553,"object_to_goal_dist_start":0.21524,"object_z_max":0.25392,"peak_contact_force":0.11514,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":13507.0,"raw_peak_contact_force":0.34948,"subtask_id":"reach_goal_pre_place","tcp_end":[0.59273,0.13735,0.22078],"tcp_start":[0.44897,-0.00025,0.12319],"tcp_to_object_dist_end":0.0202,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":145.0,"n_steps_budget":1000.0,"object_pos_end":[0.61516,0.14767,0.11349],"object_pos_start":[0.60667,0.13706,0.20617],"object_to_goal_dist_end":0.0113,"object_to_goal_dist_start":0.08553,"object_z_max":0.20617,"peak_contact_force":0.11222,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3703.0,"raw_peak_contact_force":0.42921,"subtask_id":"place","tcp_end":[0.602,0.14772,0.13024],"tcp_start":[0.59273,0.13735,0.22078],"tcp_to_object_dist_end":0.0213,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```