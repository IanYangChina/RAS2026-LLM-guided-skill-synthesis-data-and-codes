## Search State

- **Seed**: 1
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.5571 | 1.00 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.5604 | 1.00 | ✅ accepted |
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 9 | 0.1764 | 0.43 | ❌ rejected |
| 3 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.4387 | 0.79 | ✅ accepted |
| 2 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.2393 | 0.40 | ✅ accepted |

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
- Frozen realised-scene SHA-256: `a2ed2c4162d37489f2d2d0fa0373774d72c951d58f2469e0ba2d602ff46b6cfb`
- Frozen object start: [0.5011821624700257, 0.045046369632593536, 0.03]
- Frozen task target: [0.5644159612719634, 0.2448649447137244, 0.1467747178015728]
- Goal object position: (0.5644159612719634, 0.2448649447137244, 0.1467747178015728)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5644159612719634, 0.2448649447137244, 0.1467747178015728)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5011821624700257, 0.045046369632593536, 0.03)
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
  frozen_object_start: [0.5012, 0.045, 0.03]
  frozen_task_target: [0.5644, 0.2449, 0.1468]
  frozen_object_starts: {'grasp_target': [0.5011821624700257, 0.045046369632593536, 0.03]}
  frozen_targets: {'place_target': [0.5644159612719634, 0.2448649447137244, 0.1467747178015728]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: a2ed2c4162d37489f2d2d0fa0373774d72c951d58f2469e0ba2d602ff46b6cfb

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
| `object` | offset from object initial position (0.5011821624700257, 0.045046369632593536, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5644159612719634, 0.2448649447137244, 0.1467747178015728) | final destination targets |
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

## Current Skill (Q=0.557) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: subtask_approach
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.2
- id: subtask_lift
  anchor: object
  target_entity: object
  offset:
  - 0.0
  - 0.0
  - 0.2
  weight: 0.3
- id: subtask_place
  target_entity: object
  metric: goal_progress
  weight: 0.5
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
    - 0.12
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.12
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: subtask_approach
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.01
    tolerance: 0.008
    orientation:
      mode: keep_current
  parameters:
    depth:
      type: scalar
      range:
      - 0.0
      - 0.05
      default: 0.01
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: subtask_approach
- id: grasp_1
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
    - 0.25
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.15
      - 0.4
      default: 0.25
      binds_to:
      - path: target.offset.z
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.03
      - 0.15
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: lift_success
    when: after_phase
    predicate: object_lifted
    args:
      z_threshold: 0.1
    threshold: 0.1
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.01
  subtask_id: subtask_lift
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
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_goal_offset_z:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
- id: descend_goal
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
    tolerance: 0.015
    orientation:
      mode: keep_current
  parameters:
    place_offset_z:
      type: scalar
      range:
      - -0.03
      - 0.05
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: subtask_place

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.12], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.01], tolerance=0.008
  - orientation: mode=keep_current
  - parameter_bindings:
    - depth: status=consumed; consumers=target.offset.z (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **lift_1** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.25], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=lift_success, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.1, args={'z_threshold': 0.1}
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.01]
- **approach_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_goal_offset_z: status=consumed; consumers=target.offset.z (replace)
- **descend_goal** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_offset_z: status=consumed; consumers=target.offset.z (replace)

## Design Metrics

- **Composite score**: 0.557
- **task_score** (E): 1.000
- **fitness_score**: 0.977  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.420

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1103 |
| descend_1 | 1.00 | 1.00 | 0.1574 |
| grasp_1 | 1.00 | 1.00 | 0.0110 |
| lift_1 | 1.00 | 1.00 | 0.2191 |
| approach_goal | 1.00 | 1.00 | 0.2316 |
| descend_goal | 1.00 | 1.00 | 0.0838 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.481, -0.000, 0.197) | (0.479, -0.000, 0.030)→(0.479, -0.000, 0.026) | 0.276→0.278 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.481, -0.000, 0.197)→(0.474, -0.000, 0.040) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.474, -0.000, 0.040)→(0.467, -0.001, 0.032) | (0.479, -0.000, 0.026)→(0.479, -0.001, 0.026) | 0.278→0.278 | 1.00 / 45.333 | 0.146 | 0.214 |
| lift_1 | lift | 1.00 / step_budget | (0.467, -0.001, 0.032)→(0.475, -0.001, 0.251) | (0.479, -0.001, 0.026)→(0.484, -0.001, 0.239) | 0.278→0.259 | 1.00 / 40.000 | 0.074 | 0.566 |
| approach_goal | approach | 1.00 / step_budget | (0.475, -0.001, 0.251)→(0.598, 0.190, 0.255) | (0.484, -0.001, 0.239)→(0.604, 0.190, 0.238) | 0.259→0.089 | 1.00 / 40.000 | 0.076 | 0.123 |
| descend_goal | descend | 1.00 / step_budget | (0.598, 0.190, 0.255)→(0.603, 0.199, 0.172) | (0.604, 0.190, 0.238)→(0.602, 0.199, 0.154) | 0.089→0.013 | 1.00 / 36.667 | 103.675 | 0.167 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.484
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 1.000
- phase_score: 0.724
- phase_breakdown.subtask_approach_score: 0.146
- phase_breakdown.subtask_lift_score: 0.840
- phase_breakdown.subtask_place_score: 0.886
- grasp_place_fitness: 0.980

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.980
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.557
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.393


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `8110053be9072e64e15984c6424e4a66fe19af4b6c37a60139a43e94cc34ad53`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `46ef03f7b16015a0d14bf26d80c05d326b92c02b0bf759391930f5ab902d1933`; realized-scene SHA-256: `a2ed2c4162d37489f2d2d0fa0373774d72c951d58f2469e0ba2d602ff46b6cfb`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50118,0.04505,0.03]},{"name":"goal","value":[0.56442,0.24486,0.14677]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.50118,0.04505,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.56442,0.24486,0.14677]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.5545,"average_solve_count":211.0,"average_success_count":211.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.15627,"approach_goal.approach_goal_offset_z":0.11178,"descend_1.depth":0.00153,"descend_goal.place_offset_z":-0.00661,"lift_1.lift_height":0.21641,"lift_1.lift_speed":0.05543},"optimized_scores":{"best_composite_score":0.55959,"best_fitness_score":0.97959,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":88.0,"contact_point_centroid":[0.49829,0.04257,-0.00151],"force_p95":0.55994,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.66458,"mean_force":0.17198,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48728,0.04317,0.02667]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13437.0,"contact_point_centroid":[0.49104,0.06199,0.12135],"force_p95":0.07957,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31317,"mean_force":0.05352,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49057,0.04293,0.11926]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12583.0,"contact_point_centroid":[0.49148,0.02381,0.12652],"force_p95":0.0832,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29461,"mean_force":0.05595,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49088,0.04293,0.12397]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50124,0.04463,-0.00216],"force_p95":0.17164,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25998,"mean_force":0.13545,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48951,0.0434,0.02659]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3450.0,"contact_point_centroid":[0.55821,0.21553,0.20041],"force_p95":0.1012,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16321,"mean_force":0.06547,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.55786,0.23487,0.19885]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4314.0,"contact_point_centroid":[0.55807,0.2533,0.20212],"force_p95":0.07832,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15106,"mean_force":0.0495,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.55779,0.23463,0.20099]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3761.0,"contact_point_centroid":[0.48938,0.02404,0.02841],"force_p95":0.08614,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14927,"mean_force":0.05577,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48834,0.0433,0.02537]},{"body_a":"world","body_b":"grasp_target","contact_count":796.0,"contact_point_centroid":[0.50118,0.04505,-0.00184],"force_p95":0.13736,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12324,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49877,0.01703,0.25298]},{"body_a":"world","body_b":"grasp_target","contact_count":2456.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49597,0.03989,0.11678]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9239.0,"contact_point_centroid":[0.52722,0.11608,0.23541],"force_p95":0.09134,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11114,"mean_force":0.06113,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52573,0.13524,0.23329]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11579.0,"contact_point_centroid":[0.52751,0.15802,0.23479],"force_p95":0.07538,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09935,"mean_force":0.04884,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52699,0.13915,0.23384]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5479.0,"contact_point_centroid":[0.48815,0.0624,0.02791],"force_p95":0.07123,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0899,"mean_force":0.04125,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48835,0.0433,0.02537]}],"total_contact_groups":12},"final_pose_error":0.01498,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.5594,0.2397,0.13939],"final_tcp_position":[0.55972,0.24034,0.15365],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":0.66458,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":200.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":796.0,"raw_peak_contact_force":0.13845,"subtask_id":"subtask_approach","tcp_end":[0.49832,0.03592,0.20333],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17757,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":614.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2456.0,"raw_peak_contact_force":0.12263,"subtask_id":"subtask_approach","tcp_end":[0.4964,0.04402,0.03388],"tcp_start":[0.49832,0.03592,0.20333],"tcp_to_object_dist_end":0.00926,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50109,0.04323,0.02547],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24368,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.1599,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11040.0,"raw_peak_contact_force":0.25998,"tcp_end":[0.48831,0.04329,0.02534],"tcp_start":[0.4964,0.04402,0.03388],"tcp_to_object_dist_end":0.01277,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":688.0,"n_steps_budget":1000.0,"object_pos_end":[0.50915,0.04307,0.21579],"object_pos_start":[0.50109,0.04323,0.02547],"object_to_goal_dist_end":0.22031,"object_to_goal_dist_start":0.24368,"object_z_max":0.21553,"peak_contact_force":0.07936,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":26108.0,"raw_peak_contact_force":0.66458,"subtask_id":"subtask_lift","tcp_end":[0.49721,0.04295,0.22251],"tcp_start":[0.48831,0.04329,0.02534],"tcp_to_object_dist_end":0.01371,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":35.0,"n_steps":562.0,"n_steps_budget":1000.0,"object_pos_end":[0.56716,0.22947,0.23614],"object_pos_start":[0.50915,0.04307,0.21579],"object_to_goal_dist_end":0.09072,"object_to_goal_dist_start":0.22031,"object_z_max":0.23611,"peak_contact_force":0.09068,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":20818.0,"raw_peak_contact_force":0.11114,"tcp_end":[0.55715,0.22951,0.24838],"tcp_start":[0.49721,0.04295,0.22251],"tcp_to_object_dist_end":0.01582,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":207.0,"n_steps_budget":1000.0,"object_pos_end":[0.5594,0.2397,0.13939],"object_pos_start":[0.56716,0.22947,0.23614],"object_to_goal_dist_end":0.01031,"object_to_goal_dist_start":0.09072,"object_z_max":0.23614,"peak_contact_force":0.07382,"phase_name":"descend_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7764.0,"raw_peak_contact_force":0.16321,"subtask_id":"subtask_place","tcp_end":[0.55972,0.24034,0.15365],"tcp_start":[0.55715,0.22951,0.24838],"tcp_to_object_dist_end":0.01428,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1efc3ad2e58ea1c47cd56203c4986b53dab7b80d759e458b85d233ccc9cc04bd`; realized-scene SHA-256: `67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47616,-0.02015,0.03]},{"name":"goal","value":[0.63142,0.15919,0.19002]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.47616,-0.02015,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63142,0.15919,0.19002]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.38554,"average_solve_count":249.0,"average_success_count":249.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.09933,"approach_goal.approach_goal_offset_z":0.06946,"descend_1.depth":0.00869,"descend_goal.place_offset_z":0.01496,"lift_1.lift_height":0.27384,"lift_1.lift_speed":0.03687},"optimized_scores":{"best_composite_score":0.55728,"best_fitness_score":0.97728,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":82.0,"contact_point_centroid":[0.47226,-0.01936,-0.00145],"force_p95":0.51563,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.52964,"mean_force":0.20581,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46325,-0.01956,0.03475]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16975.0,"contact_point_centroid":[0.46671,-0.03864,0.15926],"force_p95":0.07379,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2719,"mean_force":0.05095,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46665,-0.01951,0.15738]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16631.0,"contact_point_centroid":[0.46672,-0.00035,0.15901],"force_p95":0.07419,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27017,"mean_force":0.0516,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46663,-0.01951,0.15693]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47616,-0.02006,-0.00205],"force_p95":0.13838,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18747,"mean_force":0.12693,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46526,-0.0196,0.03479]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1649.0,"contact_point_centroid":[0.62169,0.13067,0.23721],"force_p95":0.08374,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15541,"mean_force":0.05593,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.62034,0.1496,0.23604]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1471.0,"contact_point_centroid":[0.62176,0.16881,0.23738],"force_p95":0.08876,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15279,"mean_force":0.06384,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.62034,0.14959,0.2361]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12788.0,"contact_point_centroid":[0.54656,0.04632,0.26551],"force_p95":0.07101,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13985,"mean_force":0.04718,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.54642,0.06536,0.26412]},{"body_a":"world","body_b":"grasp_target","contact_count":1144.0,"contact_point_centroid":[0.47616,-0.02015,-0.00188],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12305,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48819,-0.00824,0.22601]},{"body_a":"world","body_b":"grasp_target","contact_count":1588.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47282,-0.01841,0.09398]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10631.0,"contact_point_centroid":[0.54757,0.0851,0.26637],"force_p95":0.07865,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11385,"mean_force":0.05537,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5469,0.06589,0.26406]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5007.0,"contact_point_centroid":[0.46391,-0.00035,0.03619],"force_p95":0.06709,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09792,"mean_force":0.04337,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46415,-0.01957,0.03369]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5154.0,"contact_point_centroid":[0.46406,-0.03882,0.03564],"force_p95":0.06681,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08603,"mean_force":0.04299,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46415,-0.01957,0.03369]}],"total_contact_groups":12},"final_pose_error":0.01466,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.63135,0.15363,0.19881],"final_tcp_position":[0.62379,0.15354,0.21614],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":0.52964,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":287.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1144.0,"raw_peak_contact_force":0.13845,"subtask_id":"subtask_approach","tcp_end":[0.47661,-0.01715,0.14888],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1229,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":397.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1588.0,"raw_peak_contact_force":0.12263,"subtask_id":"subtask_approach","tcp_end":[0.47182,-0.01974,0.04136],"tcp_start":[0.47661,-0.01715,0.14888],"tcp_to_object_dist_end":0.01595,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47605,-0.01964,0.0258],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28825,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.13648,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11961.0,"raw_peak_contact_force":0.18747,"tcp_end":[0.46412,-0.01957,0.03366],"tcp_start":[0.47182,-0.01974,0.04136],"tcp_to_object_dist_end":0.01429,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":834.0,"n_steps_budget":1000.0,"object_pos_end":[0.48134,-0.01958,0.26638],"object_pos_start":[0.47605,-0.01964,0.0258],"object_to_goal_dist_end":0.24559,"object_to_goal_dist_start":0.28825,"object_z_max":0.26611,"peak_contact_force":0.06915,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":33688.0,"raw_peak_contact_force":0.52964,"subtask_id":"subtask_lift","tcp_end":[0.47291,-0.01957,0.27993],"tcp_start":[0.46412,-0.01957,0.03366],"tcp_to_object_dist_end":0.01595,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":592.0,"n_steps_budget":1000.0,"object_pos_end":[0.62476,0.14637,0.23591],"object_pos_start":[0.48134,-0.01958,0.26638],"object_to_goal_dist_end":0.04812,"object_to_goal_dist_start":0.24559,"object_z_max":0.26657,"peak_contact_force":0.0685,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":23419.0,"raw_peak_contact_force":0.13985,"tcp_end":[0.61813,0.14625,0.25256],"tcp_start":[0.47291,-0.01957,0.27993],"tcp_to_object_dist_end":0.01792,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":33.0,"n_steps":89.0,"n_steps_budget":1000.0,"object_pos_end":[0.63135,0.15363,0.19881],"object_pos_start":[0.62476,0.14637,0.23591],"object_to_goal_dist_end":0.0104,"object_to_goal_dist_start":0.04812,"object_z_max":0.23591,"peak_contact_force":0.08359,"phase_name":"descend_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3120.0,"raw_peak_contact_force":0.15541,"subtask_id":"subtask_place","tcp_end":[0.62379,0.15354,0.21614],"tcp_start":[0.61813,0.14625,0.25256],"tcp_to_object_dist_end":0.01891,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `37495cb43897015e78e007c86af160d11c8460c1ce7249e5c03dce38206c0daf`; realized-scene SHA-256: `5ce27bcdb8582e1d517b17df0f9c2ad7b05701113a75707627744a889253e6a7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45856,-0.02632,0.03]},{"name":"goal","value":[0.63013,0.20822,0.11412]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.45856,-0.02632,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63013,0.20822,0.11412]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.5,"average_solve_count":270.0,"average_success_count":270.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.19323,"approach_goal.approach_goal_offset_z":0.15937,"descend_1.depth":0.01176,"descend_goal.place_offset_z":0.01886,"lift_1.lift_height":0.24475,"lift_1.lift_speed":0.03586},"optimized_scores":{"best_composite_score":0.55449,"best_fitness_score":0.97449,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":84.0,"contact_point_centroid":[0.4548,-0.02504,-0.00149],"force_p95":0.47424,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.50416,"mean_force":0.19625,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4465,-0.02548,0.03848]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14228.0,"contact_point_centroid":[0.44963,-0.0446,0.1453],"force_p95":0.07488,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25991,"mean_force":0.05174,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44941,-0.02545,0.14344]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14230.0,"contact_point_centroid":[0.44961,-0.00631,0.14534],"force_p95":0.07376,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2436,"mean_force":0.05151,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44941,-0.02545,0.14343]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45858,-0.02622,-0.00207],"force_p95":0.14317,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1945,"mean_force":0.12818,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44848,-0.02555,0.03852]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4604.0,"contact_point_centroid":[0.62069,0.21802,0.21271],"force_p95":0.09339,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18276,"mean_force":0.0572,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.62064,0.19901,0.21146]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4804.0,"contact_point_centroid":[0.62016,0.18006,0.20938],"force_p95":0.09189,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17062,"mean_force":0.0563,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.62081,0.19928,0.20778]},{"body_a":"world","body_b":"grasp_target","contact_count":544.0,"contact_point_centroid":[0.45856,-0.02632,-0.00177],"force_p95":0.13796,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12352,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48436,-0.00901,0.27083]},{"body_a":"world","body_b":"grasp_target","contact_count":2840.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45987,-0.02251,0.14002]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15290.0,"contact_point_centroid":[0.53398,0.0636,0.25712],"force_p95":0.07664,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11932,"mean_force":0.05047,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53429,0.08281,0.2554]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16500.0,"contact_point_centroid":[0.53873,0.10796,0.25762],"force_p95":0.06932,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11651,"mean_force":0.04672,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53881,0.08886,0.25582]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5303.0,"contact_point_centroid":[0.44677,-0.00625,0.03891],"force_p95":0.06565,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10718,"mean_force":0.04116,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4474,-0.02551,0.0375]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5420.0,"contact_point_centroid":[0.44678,-0.04479,0.03879],"force_p95":0.06559,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07298,"mean_force":0.04111,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44741,-0.02551,0.0375]}],"total_contact_groups":12},"final_pose_error":0.01492,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.61534,0.2039,0.12235],"final_tcp_position":[0.62446,0.20457,0.1463],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":310.86786,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":137.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":544.0,"raw_peak_contact_force":0.13845,"subtask_id":"subtask_approach","tcp_end":[0.46749,-0.01932,0.23908],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.21336,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":710.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2840.0,"raw_peak_contact_force":0.12264,"subtask_id":"subtask_approach","tcp_end":[0.45482,-0.02577,0.04465],"tcp_start":[0.46749,-0.01932,0.23908],"tcp_to_object_dist_end":0.01901,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":48.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45847,-0.02569,0.02574],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.3033,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.1408,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12523.0,"raw_peak_contact_force":0.1945,"tcp_end":[0.44738,-0.0255,0.03747],"tcp_start":[0.45482,-0.02577,0.04465],"tcp_to_object_dist_end":0.01615,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":711.0,"n_steps_budget":1000.0,"object_pos_end":[0.46272,-0.02558,0.23508],"object_pos_start":[0.45847,-0.02569,0.02574],"object_to_goal_dist_end":0.31196,"object_to_goal_dist_start":0.3033,"object_z_max":0.2348,"peak_contact_force":0.073,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":28542.0,"raw_peak_contact_force":0.50416,"subtask_id":"subtask_lift","tcp_end":[0.45505,-0.02555,0.2508],"tcp_start":[0.44738,-0.0255,0.03747],"tcp_to_object_dist_end":0.01749,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":770.0,"n_steps_budget":1000.0,"object_pos_end":[0.62049,0.19474,0.24187],"object_pos_start":[0.46272,-0.02558,0.23508],"object_to_goal_dist_end":0.12882,"object_to_goal_dist_start":0.31196,"object_z_max":0.24292,"peak_contact_force":0.06983,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":31790.0,"raw_peak_contact_force":0.11932,"tcp_end":[0.61876,0.19498,0.26422],"tcp_start":[0.45505,-0.02555,0.2508],"tcp_to_object_dist_end":0.02242,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":33.0,"n_steps":244.0,"n_steps_budget":1000.0,"object_pos_end":[0.61534,0.2039,0.12235],"object_pos_start":[0.62049,0.19474,0.24187],"object_to_goal_dist_end":0.01746,"object_to_goal_dist_start":0.12882,"object_z_max":0.24187,"peak_contact_force":310.86786,"phase_name":"descend_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9408.0,"raw_peak_contact_force":0.18276,"subtask_id":"subtask_place","tcp_end":[0.62446,0.20457,0.1463],"tcp_start":[0.61876,0.19498,0.26422],"tcp_to_object_dist_end":0.02564,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```