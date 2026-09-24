## Search State

- **Seed**: 9
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8  | 0.3674 | 1.00 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8  | 0.4499 | 1.00 | ✅ accepted |
| 7 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8  | 0.4498 | 1.00 | ✅ accepted |
| 6 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8  | 0.4214 | 0.94 | ✅ accepted |
| 5 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8  | 0.4498 | 1.00 | ❌ rejected |

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
| descend_to_grasp | 1.00 | 1.00 | 0.1140 |
| grasp | 1.00 | 1.00 | 0.0120 |
| lift | 1.00 | 1.00 | 0.1536 |
| transport_to_goal | 1.00 | 1.00 | 0.2200 |
| descend_to_goal | 1.00 | 1.00 | 0.0779 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, -0.014, 0.158) | (0.515, -0.017, 0.030)→(0.515, -0.017, 0.026) | 0.268→0.270 | 1.00 / 4.000 | 13.174 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.510, -0.014, 0.158)→(0.509, -0.016, 0.044) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.509, -0.016, 0.044)→(0.501, -0.016, 0.035) | (0.515, -0.017, 0.026)→(0.515, -0.016, 0.026) | 0.270→0.270 | 1.00 / 42.333 | 0.148 | 0.194 |
| lift | lift | 1.00 / step_budget | (0.501, -0.016, 0.035)→(0.499, -0.016, 0.189) | (0.515, -0.016, 0.026)→(0.510, -0.016, 0.178) | 0.270→0.234 | 1.00 / 39.000 | 0.081 | 0.515 |
| transport_to_goal | approach | 1.00 / step_budget | (0.499, -0.016, 0.189)→(0.602, 0.159, 0.257) | (0.510, -0.016, 0.178)→(0.615, 0.159, 0.241) | 0.234→0.076 | 1.00 / 28.000 | 0.100 | 0.126 |
| descend_to_goal | descend | 1.00 / step_budget | (0.602, 0.159, 0.257)→(0.610, 0.174, 0.181) | (0.615, 0.159, 0.241)→(0.623, 0.173, 0.162) | 0.076→0.013 | 1.00 / 21.667 | 0.164 | 0.388 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.503
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.651
- phase_breakdown.reach_pre_grasp_score: 0.552
- phase_breakdown.reach_goal_pre_place_score: 0.552
- phase_breakdown.place_score: 0.798
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
- **Final σ (mean)**: 0.465


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.04178,"average_solve_count":383.0,"average_success_count":383.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.speed":0.04061,"descend_to_goal.place_z_offset":-0.01082,"descend_to_goal.speed":0.03939,"descend_to_grasp.speed":0.07789,"lift.lift_height":0.23545,"lift.speed":0.05358,"transport_to_goal.arc_height":0.20024,"transport_to_goal.speed":0.04083},"optimized_scores":{"best_composite_score":0.44972,"best_fitness_score":0.96972,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"right_finger","body_b":"grasp_target","contact_count":1309.0,"contact_point_centroid":[0.60788,0.22918,0.26437],"force_p95":0.16209,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.51509,"mean_force":0.10317,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.60215,0.2108,0.2663]},{"body_a":"world","body_b":"grasp_target","contact_count":71.0,"contact_point_centroid":[0.53376,-0.02041,-0.00163],"force_p95":0.47947,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.49748,"mean_force":0.27446,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52083,-0.02017,0.03866]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1101.0,"contact_point_centroid":[0.60752,0.19218,0.26694],"force_p95":0.20494,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.39867,"mean_force":0.11829,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.60205,0.21049,0.26795]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5552.0,"contact_point_centroid":[0.51964,-0.00093,0.13024],"force_p95":0.08633,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30689,"mean_force":0.05981,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51929,-0.02013,0.12755]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6182.0,"contact_point_centroid":[0.51961,-0.03921,0.13218],"force_p95":0.08298,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29514,"mean_force":0.05543,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.5193,-0.02013,0.13019]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53706,-0.02113,-0.0021],"force_p95":0.15204,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21634,"mean_force":0.13039,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52306,-0.02021,0.03917]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7357.0,"contact_point_centroid":[0.54988,0.0752,0.305],"force_p95":0.11046,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14307,"mean_force":0.07417,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54659,0.05627,0.30307]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4089.0,"contact_point_centroid":[0.52309,-0.00097,0.04044],"force_p95":0.07946,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13927,"mean_force":0.05186,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52184,-0.02018,0.03776]},{"body_a":"world","body_b":"grasp_target","contact_count":876.0,"contact_point_centroid":[0.53702,-0.02132,-0.00185],"force_p95":0.13713,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12318,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.51223,-0.00792,0.2324]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8592.0,"contact_point_centroid":[0.55094,0.04046,0.30533],"force_p95":0.09898,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13817,"mean_force":0.0653,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54764,0.05911,0.30412]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52748,-0.01905,0.08732]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4963.0,"contact_point_centroid":[0.52302,-0.0393,0.03953],"force_p95":0.07181,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0789,"mean_force":0.04456,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52184,-0.02018,0.03776]}],"total_contact_groups":12},"final_pose_error":0.02451,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.61492,0.21933,0.19352],"final_tcp_position":[0.60527,0.21982,0.21923],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":0.51509,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":220.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":876.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.527,-0.01701,0.15778],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13221,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53004,-0.02033,0.04728],"tcp_start":[0.527,-0.01701,0.15778],"tcp_to_object_dist_end":0.0224,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53695,-0.0203,0.02565],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31615,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.14663,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10852.0,"raw_peak_contact_force":0.21634,"tcp_end":[0.52181,-0.02018,0.03772],"tcp_start":[0.53004,-0.02033,0.04728],"tcp_to_object_dist_end":0.01937,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":298.0,"n_steps_budget":1000.0,"object_pos_end":[0.53256,-0.02007,0.21867],"object_pos_start":[0.53695,-0.0203,0.02565],"object_to_goal_dist_end":0.25998,"object_to_goal_dist_start":0.31615,"object_z_max":0.218,"peak_contact_force":0.08676,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":11805.0,"raw_peak_contact_force":0.49748,"tcp_end":[0.51989,-0.02013,0.23333],"tcp_start":[0.52181,-0.02018,0.03772],"tcp_to_object_dist_end":0.01937,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":557.0,"n_steps_budget":1000.0,"object_pos_end":[0.61415,0.20419,0.28117],"object_pos_start":[0.53256,-0.02007,0.21867],"object_to_goal_dist_end":0.07753,"object_to_goal_dist_start":0.25998,"object_z_max":0.32349,"peak_contact_force":0.11181,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":15949.0,"raw_peak_contact_force":0.14307,"subtask_id":"reach_goal_pre_place","tcp_end":[0.60081,0.20408,0.30289],"tcp_start":[0.51989,-0.02013,0.23333],"tcp_to_object_dist_end":0.02548,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":11.0,"n_steps":135.0,"n_steps_budget":1000.0,"object_pos_end":[0.61492,0.21933,0.19352],"object_pos_start":[0.61415,0.20419,0.28117],"object_to_goal_dist_end":0.01689,"object_to_goal_dist_start":0.07753,"object_z_max":0.28117,"peak_contact_force":0.28857,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2410.0,"raw_peak_contact_force":0.51509,"subtask_id":"place","tcp_end":[0.60527,0.21982,0.21923],"tcp_start":[0.60081,0.20408,0.30289],"tcp_to_object_dist_end":0.02746,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.66972,"average_solve_count":436.0,"average_success_count":436.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.speed":0.04872,"descend_to_goal.place_z_offset":0.00171,"descend_to_goal.speed":0.01642,"descend_to_grasp.speed":0.0792,"lift.lift_height":0.14784,"lift.speed":0.02763,"transport_to_goal.arc_height":0.24311,"transport_to_goal.speed":0.02287},"optimized_scores":{"best_composite_score":0.43938,"best_fitness_score":0.95938,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"right_finger","body_b":"grasp_target","contact_count":1368.0,"contact_point_centroid":[0.6254,0.1643,0.23475],"force_p95":0.10666,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.45725,"mean_force":0.08611,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.61953,0.14551,0.23412]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1478.0,"contact_point_centroid":[0.62535,0.12729,0.2332],"force_p95":0.10385,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35218,"mean_force":0.0788,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.61971,0.14584,0.23275]},{"body_a":"world","body_b":"grasp_target","contact_count":102.0,"contact_point_centroid":[0.54294,-0.02765,-0.00179],"force_p95":0.2971,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.33571,"mean_force":0.18027,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52813,-0.02722,0.04689]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3325.0,"contact_point_centroid":[0.52742,-0.00795,0.09539],"force_p95":0.10819,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27527,"mean_force":0.06319,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.5265,-0.02716,0.09347]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4066.0,"contact_point_centroid":[0.52709,-0.04612,0.09592],"force_p95":0.09829,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25492,"mean_force":0.05415,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52647,-0.02716,0.09348]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54571,-0.02913,-0.00217],"force_p95":0.16914,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22765,"mean_force":0.13523,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53061,-0.02729,0.04766]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8417.0,"contact_point_centroid":[0.55866,0.01141,0.22513],"force_p95":0.09565,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14522,"mean_force":0.05864,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55646,0.03019,0.22399]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6944.0,"contact_point_centroid":[0.5582,0.04774,0.22259],"force_p95":0.11247,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13889,"mean_force":0.06877,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55565,0.02874,0.22206]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4399.0,"contact_point_centroid":[0.53101,-0.00811,0.0475],"force_p95":0.08558,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13861,"mean_force":0.05274,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.5294,-0.02725,0.04621]},{"body_a":"world","body_b":"grasp_target","contact_count":896.0,"contact_point_centroid":[0.5456,-0.02923,-0.00185],"force_p95":0.13709,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12317,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.51574,-0.01104,0.23127]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53481,-0.02594,0.09246]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5156.0,"contact_point_centroid":[0.53195,-0.04631,0.04888],"force_p95":0.07828,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08197,"mean_force":0.04408,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52941,-0.02725,0.04622]}],"total_contact_groups":12},"final_pose_error":0.02484,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.63636,0.1541,0.17133],"final_tcp_position":[0.62464,0.15482,0.19979],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":0.45725,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":225.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":896.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.53414,-0.0235,0.1566],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1312,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.5376,-0.02749,0.05606],"tcp_start":[0.53414,-0.0235,0.1566],"tcp_to_object_dist_end":0.03113,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54586,-0.02785,0.02533],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26022,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.16787,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11355.0,"raw_peak_contact_force":0.22765,"tcp_end":[0.52937,-0.02725,0.04618],"tcp_start":[0.5376,-0.02749,0.05606],"tcp_to_object_dist_end":0.02659,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":184.0,"n_steps_budget":1000.0,"object_pos_end":[0.5394,-0.02777,0.13365],"object_pos_start":[0.54586,-0.02785,0.02533],"object_to_goal_dist_end":0.21849,"object_to_goal_dist_start":0.26022,"object_z_max":0.13299,"peak_contact_force":0.08357,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":7493.0,"raw_peak_contact_force":0.33571,"tcp_end":[0.52664,-0.02714,0.15473],"tcp_start":[0.52937,-0.02725,0.04618],"tcp_to_object_dist_end":0.02466,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":482.0,"n_steps_budget":1000.0,"object_pos_end":[0.62864,0.13805,0.23136],"object_pos_start":[0.5394,-0.02777,0.13365],"object_to_goal_dist_end":0.06085,"object_to_goal_dist_start":0.21849,"object_z_max":0.23921,"peak_contact_force":0.10297,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":15361.0,"raw_peak_contact_force":0.14522,"subtask_id":"reach_goal_pre_place","tcp_end":[0.61735,0.13929,0.25806],"tcp_start":[0.52664,-0.02714,0.15473],"tcp_to_object_dist_end":0.02901,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":118.0,"n_steps_budget":1000.0,"object_pos_end":[0.63636,0.1541,0.17133],"object_pos_start":[0.62864,0.13805,0.23136],"object_to_goal_dist_end":0.01268,"object_to_goal_dist_start":0.06085,"object_z_max":0.23136,"peak_contact_force":0.10588,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2846.0,"raw_peak_contact_force":0.45725,"subtask_id":"place","tcp_end":[0.62464,0.15482,0.19979],"tcp_start":[0.61735,0.13929,0.25806],"tcp_to_object_dist_end":0.03079,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.16817,"average_solve_count":333.0,"average_success_count":333.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.speed":0.07013,"descend_to_goal.place_z_offset":-0.02094,"descend_to_goal.speed":0.06488,"descend_to_grasp.speed":0.04601,"lift.lift_height":0.19616,"lift.speed":0.04489,"transport_to_goal.arc_height":0.27658,"transport_to_goal.speed":0.0463},"optimized_scores":{"best_composite_score":0.46021,"best_fitness_score":0.98021,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":70.0,"contact_point_centroid":[0.45975,-3e-05,-0.00152],"force_p95":0.68401,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.71088,"mean_force":0.4146,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45032,-0.00024,0.02242]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4624.0,"contact_point_centroid":[0.44921,0.01891,0.09745],"force_p95":0.07867,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28771,"mean_force":0.05423,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44902,-0.00025,0.09556]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4653.0,"contact_point_centroid":[0.44923,-0.01939,0.09698],"force_p95":0.07872,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26207,"mean_force":0.05409,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44903,-0.00025,0.0951]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2453.0,"contact_point_centroid":[0.59555,0.15861,0.17047],"force_p95":0.09445,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1927,"mean_force":0.06186,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.59352,0.13959,0.16944]},{"body_a":"world","body_b":"grasp_target","contact_count":804.0,"contact_point_centroid":[0.46286,-7e-05,-0.00184],"force_p95":0.13728,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12324,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.48466,-4e-05,0.23263]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.46283,-5e-05,-0.00201],"force_p95":0.12815,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13805,"mean_force":0.12422,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45226,-0.0002,0.02265]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2383.0,"contact_point_centroid":[0.59569,0.12082,0.17],"force_p95":0.09333,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13372,"mean_force":0.06215,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.59369,0.13976,0.16829]},{"body_a":"world","body_b":"grasp_target","contact_count":3120.0,"contact_point_centroid":[0.46286,-7e-05,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.46163,-0.0001,0.09059]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4389.0,"contact_point_centroid":[0.45112,0.01906,0.02389],"force_p95":0.07365,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09392,"mean_force":0.04931,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45116,-0.00022,0.02161]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7980.0,"contact_point_centroid":[0.51314,0.0423,0.2156],"force_p95":0.07502,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08993,"mean_force":0.05054,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51268,0.06137,0.2137]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7350.0,"contact_point_centroid":[0.51017,0.07772,0.21512],"force_p95":0.07886,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08754,"mean_force":0.05362,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50976,0.05857,0.21286]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5091.0,"contact_point_centroid":[0.45101,-0.01929,0.02347],"force_p95":0.06453,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08395,"mean_force":0.04268,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45116,-0.00022,0.02161]}],"total_contact_groups":12},"final_pose_error":0.02483,"key_states":{"actual_goal_position":[0.61015,0.15287,0.12219],"final_object_position":[0.61782,0.14672,0.12073],"final_tcp_position":[0.60079,0.14667,0.12339],"realised_goal_position":[0.61015,0.15287,0.12219],"realised_object_initial_position":[0.46286,-7e-05,0.03]},"peak_contact_force":39.27746,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":202.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.03],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.23148,"object_z_max":0.03,"peak_contact_force":39.27746,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":804.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.46803,-7e-05,0.15924],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13332,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":780.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3120.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.4587,-0.00012,0.02876],"tcp_start":[0.46803,-7e-05,0.15924],"tcp_to_object_dist_end":0.00498,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46271,-5e-05,0.02593],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.23322,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12821,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11280.0,"raw_peak_contact_force":0.13805,"tcp_end":[0.45113,-0.00022,0.02159],"tcp_start":[0.4587,-0.00012,0.02876],"tcp_to_object_dist_end":0.01237,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":232.0,"n_steps_budget":1000.0,"object_pos_end":[0.45883,-0.00023,0.18185],"object_pos_start":[0.46271,-5e-05,0.02593],"object_to_goal_dist_end":0.22337,"object_to_goal_dist_start":0.23322,"object_z_max":0.18115,"peak_contact_force":0.07255,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":9347.0,"raw_peak_contact_force":0.71088,"tcp_end":[0.44932,-0.00024,0.1781],"tcp_start":[0.45113,-0.00022,0.02159],"tcp_to_object_dist_end":0.01022,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":399.0,"n_steps_budget":1000.0,"object_pos_end":[0.60305,0.13389,0.20926],"object_pos_start":[0.45883,-0.00023,0.18185],"object_to_goal_dist_end":0.0894,"object_to_goal_dist_start":0.22337,"object_z_max":0.2293,"peak_contact_force":0.08477,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":15330.0,"raw_peak_contact_force":0.08993,"subtask_id":"reach_goal_pre_place","tcp_end":[0.58862,0.13373,0.20935],"tcp_start":[0.44932,-0.00024,0.1781],"tcp_to_object_dist_end":0.01443,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":141.0,"n_steps_budget":1000.0,"object_pos_end":[0.61782,0.14672,0.12073],"object_pos_start":[0.60305,0.13389,0.20926],"object_to_goal_dist_end":0.00994,"object_to_goal_dist_start":0.0894,"object_z_max":0.20926,"peak_contact_force":0.09884,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4836.0,"raw_peak_contact_force":0.1927,"subtask_id":"place","tcp_end":[0.60079,0.14667,0.12339],"tcp_start":[0.58862,0.13373,0.20935],"tcp_to_object_dist_end":0.01723,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```