## Search State

- **Seed**: 5
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 6  | 0.5586 | 1.00 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 6  | 0.5586 | 1.00 | ✅ accepted |
| 8 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 6  | 0.0447 | 0.39 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 9  | 0.0447 | 0.39 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 9  | 0.5585 | 1.00 | ❌ rejected |

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
- Frozen realised-scene SHA-256: `ca83b0c5488ee900ee32f323a4fc38ffcc2f5381fd3d2b180044b561c962382d`
- Frozen object start: [0.530500292374538, 0.030794078973649372, 0.03]
- Frozen task target: [0.6015325561042142, 0.17858013800881417, 0.10808960535724847]
- Goal object position: (0.6015325561042142, 0.17858013800881417, 0.10808960535724847)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.6015325561042142, 0.17858013800881417, 0.10808960535724847)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.530500292374538, 0.030794078973649372, 0.03)
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
  frozen_object_start: [0.5305, 0.0308, 0.03]
  frozen_task_target: [0.6015, 0.1786, 0.1081]
  frozen_object_starts: {'grasp_target': [0.530500292374538, 0.030794078973649372, 0.03]}
  frozen_targets: {'place_target': [0.6015325561042142, 0.17858013800881417, 0.10808960535724847]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: ca83b0c5488ee900ee32f323a4fc38ffcc2f5381fd3d2b180044b561c962382d

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
| `object` | offset from object initial position (0.530500292374538, 0.030794078973649372, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.6015325561042142, 0.17858013800881417, 0.10808960535724847) | final destination targets |
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

## Current Skill (Q=0.559) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_object
  anchor: object
  weight: 0.3
- id: reach_goal
  weight: 0.7
phases:
- id: approach_object
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
    - 0.12
    tolerance: 0.015
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: contact_watch
    when: during_phase
    predicate: force_below
    threshold: 15.0
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.01
- id: descend_to_object
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
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_object
- id: grasp_object
  type: grasp
  control: position_control
  termination: grasp_success
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
  guards:
  - id: grasp_verify
    when: after_phase
    predicate: bilateral_grasp
    threshold: 10.0
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - -0.005
- id: lift_object
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
    offset_along_axis:
      distance: 0.12
      axis: world_z
      mode: replace_offset_projection
      sign: positive
    tolerance: 0.015
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.12
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
- id: approach_goal
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
    - 0.1
    tolerance: 0.015
    orientation:
      mode: keep_current
  parameters:
    goal_approach_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
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
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_goal_speed:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.12], tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=contact_watch, when=during_phase, predicate=force_below, on_failure=retry, threshold=15.0
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, 0.01]
- **descend_to_object** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **grasp_object** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=grasp_verify, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=10.0
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, -0.005]
- **lift_object** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.12, mode=replace_offset_projection, sign=positive}, tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
- **approach_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - goal_approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_goal** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_goal_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.559
- **task_score** (E): 1.000
- **fitness_score**: 0.979  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.420

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1410 |
| descend_to_object | 1.00 | 1.00 | 0.1288 |
| grasp_object | 1.00 | 1.00 | 0.0124 |
| lift_object | 1.00 | 1.00 | 0.1693 |
| approach_goal | 0.67 | 1.00 | 0.1809 |
| descend_to_goal | 1.00 | 1.00 | 0.0797 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, 0.016, 0.163) | (0.516, 0.018, 0.030)→(0.516, 0.018, 0.026) | 0.234→0.236 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_object | descend | 1.00 / step_budget | (0.510, 0.016, 0.163)→(0.510, 0.018, 0.034) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_object | grasp | 1.00 / step_budget | (0.510, 0.018, 0.034)→(0.502, 0.017, 0.025) | (0.516, 0.018, 0.026)→(0.515, 0.017, 0.026) | 0.236→0.237 | 1.00 / 41.000 | 0.146 | 0.219 |
| lift_object | lift | 1.00 / step_budget | (0.502, 0.017, 0.025)→(0.499, 0.017, 0.194) | (0.515, 0.017, 0.026)→(0.509, 0.017, 0.186) | 0.237→0.200 | 1.00 / 42.667 | 0.071 | 0.658 |
| approach_goal | approach | 0.67 / step_budget | (0.499, 0.017, 0.194)→(0.591, 0.157, 0.245) | (0.509, 0.017, 0.186)→(0.598, 0.157, 0.229) | 0.200→0.072 | 1.00 / 37.333 | 0.079 | 0.113 |
| descend_to_goal | descend | 1.00 / step_budget | (0.591, 0.157, 0.245)→(0.599, 0.175, 0.172) | (0.598, 0.157, 0.229)→(0.605, 0.175, 0.154) | 0.072→0.014 | 1.00 / 36.000 | 0.080 | 0.148 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.008
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 1.000
- phase_score: 0.836
- phase_breakdown.reach_goal_score: 0.820
- phase_breakdown.reach_object_score: 0.873
- grasp_place_fitness: 0.979

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.979
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.559
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.470


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `181fdad61feb8a6d3dd6561c82dc2730a5598964bf30fa08b43615687239c379`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `eed1fc17ff57094d5189888f0dc8540ea7c165c4c73333e7487a550c7ded377e`; realized-scene SHA-256: `ca83b0c5488ee900ee32f323a4fc38ffcc2f5381fd3d2b180044b561c962382d`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5305,0.03079,0.03]},{"name":"goal","value":[0.60153,0.17858,0.10809]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5305,0.03079,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.60153,0.17858,0.10809]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.01773,"average_solve_count":282.0,"average_success_count":282.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.goal_approach_speed":0.13164,"approach_object.approach_speed":0.02497,"descend_to_goal.descend_goal_speed":0.06219,"descend_to_object.descend_speed":0.07149,"lift_object.lift_height":0.17142,"lift_object.lift_speed":0.05574},"optimized_scores":{"best_composite_score":0.55776,"best_fitness_score":0.97776,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":114.0,"contact_point_centroid":[0.52678,0.02877,-0.00136],"force_p95":0.57826,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.72312,"mean_force":0.13312,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51508,0.0294,0.02597]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16447.0,"contact_point_centroid":[0.51329,0.0483,0.10361],"force_p95":0.07931,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3248,"mean_force":0.05471,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51238,0.02923,0.10163]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15955.0,"contact_point_centroid":[0.51334,0.01015,0.10684],"force_p95":0.08044,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31677,"mean_force":0.05565,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51237,0.02923,0.1046]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53054,0.03046,-0.00212],"force_p95":0.15769,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24283,"mean_force":0.1321,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.51769,0.02959,0.02588]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3172.0,"contact_point_centroid":[0.59514,0.15329,0.15749],"force_p95":0.10462,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17187,"mean_force":0.07526,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.59364,0.17245,0.15742]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4636.0,"contact_point_centroid":[0.59529,0.19112,0.15731],"force_p95":0.08248,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15274,"mean_force":0.05411,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.59364,0.17245,0.15742]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9725.0,"contact_point_centroid":[0.55335,0.07989,0.18904],"force_p95":0.09535,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14847,"mean_force":0.06899,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55134,0.09891,0.18773]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4057.0,"contact_point_centroid":[0.51736,0.01031,0.02728],"force_p95":0.08032,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14149,"mean_force":0.05188,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.51647,0.02951,0.02452]},{"body_a":"world","body_b":"grasp_target","contact_count":1516.0,"contact_point_centroid":[0.5305,0.03079,-0.00191],"force_p95":0.13479,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12295,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.5102,0.01288,0.23211]},{"body_a":"world","body_b":"grasp_target","contact_count":1628.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.52262,0.02837,0.09734]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11931.0,"contact_point_centroid":[0.55627,0.1225,0.1888],"force_p95":0.08519,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11673,"mean_force":0.05794,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55417,0.10371,0.18845]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4986.0,"contact_point_centroid":[0.51729,0.04866,0.02632],"force_p95":0.07268,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08797,"mean_force":0.04484,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.51647,0.02951,0.02453]}],"total_contact_groups":12},"final_pose_error":0.00987,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.59923,0.17553,0.09634],"final_tcp_position":[0.59586,0.17574,0.11565],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":0.72312,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":380.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1516.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.52323,0.02687,0.16216],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13639,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":407.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1628.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.52499,0.03007,0.03412],"tcp_start":[0.52323,0.02687,0.16216],"tcp_to_object_dist_end":0.00983,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53037,0.02945,0.02561],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18468,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.14973,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10843.0,"raw_peak_contact_force":0.24283,"tcp_end":[0.51644,0.0295,0.02449],"tcp_start":[0.52499,0.03007,0.03412],"tcp_to_object_dist_end":0.01397,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":870.0,"n_steps_budget":1000.0,"object_pos_end":[0.52452,0.02925,0.1731],"object_pos_start":[0.53037,0.02945,0.02561],"object_to_goal_dist_end":0.18016,"object_to_goal_dist_start":0.18468,"object_z_max":0.17294,"peak_contact_force":0.0716,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":32516.0,"raw_peak_contact_force":0.72312,"tcp_end":[0.51279,0.02926,0.18141],"tcp_start":[0.51644,0.0295,0.02449],"tcp_to_object_dist_end":0.01438,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":688.0,"n_steps_budget":1000.0,"object_pos_end":[0.6002,0.16981,0.18098],"object_pos_start":[0.52452,0.02925,0.1731],"object_to_goal_dist_end":0.07342,"object_to_goal_dist_start":0.18016,"object_z_max":0.18097,"peak_contact_force":0.09439,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":21656.0,"raw_peak_contact_force":0.14847,"tcp_end":[0.59365,0.16998,0.19886],"tcp_start":[0.51279,0.02926,0.18141],"tcp_to_object_dist_end":0.01905,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":244.0,"n_steps_budget":1000.0,"object_pos_end":[0.59923,0.17553,0.09634],"object_pos_start":[0.6002,0.16981,0.18098],"object_to_goal_dist_end":0.01236,"object_to_goal_dist_start":0.07342,"object_z_max":0.18098,"peak_contact_force":0.09513,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7808.0,"raw_peak_contact_force":0.17187,"subtask_id":"reach_goal","tcp_end":[0.59586,0.17574,0.11565],"tcp_start":[0.59365,0.16998,0.19886],"tcp_to_object_dist_end":0.01961,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `5dcdc1a4e2a8d4c3bb30f9ac92fb306bea0b16a8f449f4d02b0333754e50f910`; realized-scene SHA-256: `584133b5261cffac0dd4282704ff39e97bf4d452e60b02507679bbdea5a4de22`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50382,-0.01567,0.03]},{"name":"goal","value":[0.58691,0.18745,0.24812]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.50382,-0.01567,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58691,0.18745,0.24812]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.9,"average_solve_count":340.0,"average_success_count":340.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.goal_approach_speed":0.06821,"approach_object.approach_speed":0.08149,"descend_to_goal.descend_goal_speed":0.01006,"descend_to_object.descend_speed":0.06991,"lift_object.lift_height":0.18077,"lift_object.lift_speed":0.04921},"optimized_scores":{"best_composite_score":0.55918,"best_fitness_score":0.97918,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":103.0,"contact_point_centroid":[0.49922,-0.01505,-0.00129],"force_p95":0.6219,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65997,"mean_force":0.16949,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48947,-0.0153,0.02725]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17340.0,"contact_point_centroid":[0.48677,0.00392,0.11188],"force_p95":0.07584,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31327,"mean_force":0.05163,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48676,-0.01524,0.10981]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17982.0,"contact_point_centroid":[0.48671,-0.03437,0.11106],"force_p95":0.07342,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29166,"mean_force":0.05015,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48676,-0.01524,0.10923]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50381,-0.01551,-0.00203],"force_p95":0.13369,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16411,"mean_force":0.12574,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49183,-0.01532,0.02719]},{"body_a":"world","body_b":"grasp_target","contact_count":1288.0,"contact_point_centroid":[0.50382,-0.01567,-0.0019],"force_p95":0.13564,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12301,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49932,-0.00653,0.23304]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6593.0,"contact_point_centroid":[0.57051,0.17633,0.27215],"force_p95":0.07173,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12342,"mean_force":0.0513,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.56901,0.15728,0.27211]},{"body_a":"world","body_b":"grasp_target","contact_count":1692.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.49801,-0.01446,0.09852]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4108.0,"contact_point_centroid":[0.49119,0.0039,0.02872],"force_p95":0.07628,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11386,"mean_force":0.05174,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49066,-0.01531,0.02596]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6365.0,"contact_point_centroid":[0.57036,0.13802,0.27244],"force_p95":0.07336,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11026,"mean_force":0.05278,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.56892,0.15711,0.27229]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19625.0,"contact_point_centroid":[0.52178,0.04063,0.24501],"force_p95":0.07607,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09973,"mean_force":0.05103,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52145,0.05977,0.24424]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4892.0,"contact_point_centroid":[0.49124,-0.03439,0.02779],"force_p95":0.06854,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08876,"mean_force":0.04477,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49066,-0.01531,0.02596]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19926.0,"contact_point_centroid":[0.52315,0.0812,0.24667],"force_p95":0.07242,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08326,"mean_force":0.04991,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52261,0.06211,0.24598]}],"total_contact_groups":12},"final_pose_error":0.00995,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.58705,0.17982,0.22981],"final_tcp_position":[0.58054,0.1799,0.24693],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":0.65997,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":323.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1288.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.50009,-0.01358,0.164],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13805,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":423.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1692.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.49883,-0.0154,0.0346],"tcp_start":[0.50009,-0.01358,0.164],"tcp_to_object_dist_end":0.00993,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50367,-0.01517,0.02587],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31206,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13103,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10800.0,"raw_peak_contact_force":0.16411,"tcp_end":[0.49063,-0.01531,0.02593],"tcp_start":[0.49883,-0.0154,0.0346],"tcp_to_object_dist_end":0.01305,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":872.0,"n_steps_budget":1000.0,"object_pos_end":[0.49776,-0.01515,0.18462],"object_pos_start":[0.50367,-0.01517,0.02587],"object_to_goal_dist_end":0.23027,"object_to_goal_dist_start":0.31206,"object_z_max":0.18445,"peak_contact_force":0.06994,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":35425.0,"raw_peak_contact_force":0.65997,"tcp_end":[0.48714,-0.01524,0.19216],"tcp_start":[0.49063,-0.01531,0.02593],"tcp_to_object_dist_end":0.01303,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56674,0.13573,0.28601],"object_pos_start":[0.49776,-0.01515,0.18462],"object_to_goal_dist_end":0.06721,"object_to_goal_dist_start":0.23027,"object_z_max":0.28589,"peak_contact_force":0.07254,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":39551.0,"raw_peak_contact_force":0.09973,"tcp_end":[0.55946,0.13574,0.30154],"tcp_start":[0.48714,-0.01524,0.19216],"tcp_to_object_dist_end":0.01715,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":347.0,"n_steps_budget":1000.0,"object_pos_end":[0.58705,0.17982,0.22981],"object_pos_start":[0.56674,0.13573,0.28601],"object_to_goal_dist_end":0.01983,"object_to_goal_dist_start":0.06721,"object_z_max":0.28601,"peak_contact_force":0.07241,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":12958.0,"raw_peak_contact_force":0.12342,"subtask_id":"reach_goal","tcp_end":[0.58054,0.1799,0.24693],"tcp_start":[0.55946,0.13574,0.30154],"tcp_to_object_dist_end":0.01832,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `53da4dc33bcb1151bde99c46f4ec5d44dda63d23acc62ec623c12d4d0fb32574`; realized-scene SHA-256: `8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51251,0.03972,0.03]},{"name":"goal","value":[0.62757,0.17252,0.14502]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.51251,0.03972,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.62757,0.17252,0.14502]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.88967,"average_solve_count":426.0,"average_success_count":426.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.goal_approach_speed":0.03368,"approach_object.approach_speed":0.08687,"descend_to_goal.descend_goal_speed":0.05771,"descend_to_object.descend_speed":0.02054,"lift_object.lift_height":0.19993,"lift_object.lift_speed":0.02445},"optimized_scores":{"best_composite_score":0.5587,"best_fitness_score":0.9787,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":118.0,"contact_point_centroid":[0.50757,0.03725,-0.00144],"force_p95":0.55077,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.59179,"mean_force":0.17972,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49771,0.03802,0.02659]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20480.0,"contact_point_centroid":[0.4952,0.05696,0.11854],"force_p95":0.07407,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27492,"mean_force":0.05056,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49516,0.03782,0.11685]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20074.0,"contact_point_centroid":[0.49525,0.01867,0.12214],"force_p95":0.07552,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26095,"mean_force":0.05073,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49517,0.03782,0.12004]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51257,0.03936,-0.00214],"force_p95":0.16537,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25046,"mean_force":0.13409,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.50026,0.03824,0.02665]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4460.0,"contact_point_centroid":[0.62091,0.18665,0.19431],"force_p95":0.07287,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14793,"mean_force":0.05298,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.6195,0.1676,0.19431]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4046.0,"contact_point_centroid":[0.49974,0.01894,0.02817],"force_p95":0.08159,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1476,"mean_force":0.05193,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49907,0.03814,0.02537]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4240.0,"contact_point_centroid":[0.62081,0.14858,0.19325],"force_p95":0.08671,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1428,"mean_force":0.05496,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.61953,0.16765,0.19291]},{"body_a":"world","body_b":"grasp_target","contact_count":1356.0,"contact_point_centroid":[0.51251,0.03972,-0.0019],"force_p95":0.13561,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12299,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50294,0.01664,0.23234]},{"body_a":"world","body_b":"grasp_target","contact_count":1828.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.50595,0.03655,0.0981]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18778.0,"contact_point_centroid":[0.55893,0.12352,0.22159],"force_p95":0.0738,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09152,"mean_force":0.04997,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55841,0.10435,0.2207]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5016.0,"contact_point_centroid":[0.4997,0.05732,0.02718],"force_p95":0.07406,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09018,"mean_force":0.04483,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49907,0.03814,0.02538]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19658.0,"contact_point_centroid":[0.55835,0.08482,0.22159],"force_p95":0.07174,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08095,"mean_force":0.04764,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55799,0.10392,0.2206]}],"total_contact_groups":12},"final_pose_error":0.00974,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.62933,0.16993,0.13632],"final_tcp_position":[0.62205,0.17009,0.15267],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":0.59179,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":340.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1356.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.50767,0.03455,0.163],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13717,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":457.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1828.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.50732,0.03881,0.03433],"tcp_start":[0.50767,0.03455,0.163],"tcp_to_object_dist_end":0.00984,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51239,0.03812,0.02552],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21356,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.15587,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10862.0,"raw_peak_contact_force":0.25046,"tcp_end":[0.49904,0.03814,0.02534],"tcp_start":[0.50732,0.03881,0.03433],"tcp_to_object_dist_end":0.01335,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50612,0.03787,0.20164],"object_pos_start":[0.51239,0.03812,0.02552],"object_to_goal_dist_end":0.18996,"object_to_goal_dist_start":0.21356,"object_z_max":0.20146,"peak_contact_force":0.07156,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":40672.0,"raw_peak_contact_force":0.59179,"tcp_end":[0.49567,0.03786,0.20986],"tcp_start":[0.49904,0.03814,0.02534],"tcp_to_object_dist_end":0.01329,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":938.0,"n_steps_budget":1000.0,"object_pos_end":[0.62574,0.16572,0.21984],"object_pos_start":[0.50612,0.03787,0.20164],"object_to_goal_dist_end":0.07515,"object_to_goal_dist_start":0.18996,"object_z_max":0.21983,"peak_contact_force":0.0715,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":38436.0,"raw_peak_contact_force":0.09152,"tcp_end":[0.61895,0.16585,0.23481],"tcp_start":[0.49567,0.03786,0.20986],"tcp_to_object_dist_end":0.01644,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":234.0,"n_steps_budget":1000.0,"object_pos_end":[0.62933,0.16993,0.13632],"object_pos_start":[0.62574,0.16572,0.21984],"object_to_goal_dist_end":0.00926,"object_to_goal_dist_start":0.07515,"object_z_max":0.21984,"peak_contact_force":0.07193,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8700.0,"raw_peak_contact_force":0.14793,"subtask_id":"reach_goal","tcp_end":[0.62205,0.17009,0.15267],"tcp_start":[0.61895,0.16585,0.23481],"tcp_to_object_dist_end":0.0179,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```