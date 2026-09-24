## Search State

- **Seed**: 4
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 10 | 0.0947 | 0.48 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 12 | -0.2160 | 0.56 | ✅ accepted |
| 6 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 13 | -0.1855 | 0.34 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 13 | -0.4950 | 0.22 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 13 | -0.1874 | 0.33 | ❌ rejected |

**Proposal policy**: task_score is 0.48 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
- task_score stagnant: change coupled targets, parameters, terminations, phase types, controls, subtasks, or ordering when evidence shows they need to change together.
A HOLD wastes an iteration when task_score is below 0.9.

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
- Frozen realised-scene SHA-256: `1959b3932a54fd3d3850620783d44a63a35b8fa059f78d939fdbdef5fbfc64e8`
- Frozen object start: [0.5443056105572368, 0.0011327552814361583, 0.03]
- Frozen task target: [0.6476243705707704, 0.15808360238956023, 0.19110337479925443]
- Goal object position: (0.6476243705707704, 0.15808360238956023, 0.19110337479925443)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.6476243705707704, 0.15808360238956023, 0.19110337479925443)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5443056105572368, 0.0011327552814361583, 0.03)
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
  frozen_object_start: [0.5443, 0.0011, 0.03]
  frozen_task_target: [0.6476, 0.1581, 0.1911]
  frozen_object_starts: {'grasp_target': [0.5443056105572368, 0.0011327552814361583, 0.03]}
  frozen_targets: {'place_target': [0.6476243705707704, 0.15808360238956023, 0.19110337479925443]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 1959b3932a54fd3d3850620783d44a63a35b8fa059f78d939fdbdef5fbfc64e8

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
| `object` | offset from object initial position (0.5443056105572368, 0.0011327552814361583, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.6476243705707704, 0.15808360238956023, 0.19110337479925443) | final destination targets |
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

## Current Skill (Q=0.095) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: grasp_approach
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.3
- id: place
  weight: 0.7
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
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.2
      - 1.0
      default: 0.5
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: grasp_approach
- id: descend_grasp
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
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.08
      - 0.5
      default: 0.25
      binds_to:
      - path: generator.speed
        mode: replace
    grasp_z_offset:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: grasp_approach
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
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.12
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    lift_guard_threshold:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.015
      binds_to:
      - path: guards.lift_guard.threshold
        mode: replace
    lift_height:
      type: scalar
      range:
      - 0.08
      - 0.2
      default: 0.12
      binds_to:
      - path: target.offset.z
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.25
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: lift_guard
    when: during_phase
    predicate: object_lifted
    threshold: 0.015
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: reduce_speed
- id: approach_goal
  type: approach
  generator: linear_cartesian
  control: impedance_control
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
    approach_goal_speed:
      type: scalar
      range:
      - 0.15
      - 0.7
      default: 0.4
      binds_to:
      - path: generator.speed
        mode: replace
    place_approach_z:
      type: scalar
      range:
      - 0.08
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    transport_guard_threshold:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.01
      binds_to:
      - path: guards.transport_guard.threshold
        mode: replace
  guards:
  - id: transport_guard
    when: during_phase
    predicate: object_lifted
    threshold: 0.01
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: reduce_speed
  subtask_id: place
- id: descend_place
  type: descend
  generator: linear_cartesian
  control: impedance_control
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
    descend_place_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.12
      binds_to:
      - path: generator.speed
        mode: replace
    place_z_offset:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: place

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - grasp_z_offset: status=consumed; consumers=target.offset.z (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **lift_1** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.12], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_guard_threshold: status=consumed; consumers=guards.lift_guard.threshold (replace)
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=lift_guard, when=during_phase, predicate=object_lifted, on_failure=retry, threshold=0.015
  - retries: max_attempts=2, strategy=reduce_speed
- **approach_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_goal_speed: status=consumed; consumers=generator.speed (replace)
    - place_approach_z: status=consumed; consumers=target.offset.z (replace)
    - transport_guard_threshold: status=consumed; consumers=guards.transport_guard.threshold (replace)
  - guards:
    - id=transport_guard, when=during_phase, predicate=object_lifted, on_failure=retry, threshold=0.01
  - retries: max_attempts=2, strategy=reduce_speed
- **descend_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_place_speed: status=consumed; consumers=generator.speed (replace)
    - place_z_offset: status=consumed; consumers=target.offset.z (replace)

## Design Metrics

- **Composite score**: 0.095
- **task_score** (E): 0.475
- **fitness_score**: 0.715  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.620

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_1 | 1.00 | 0.1508 |
| descend_grasp | 1.00 | 0.1145 |
| grasp_1 | 1.00 | 0.0135 |
| lift_1 | 1.00 | 0.1034 |
| approach_goal | 1.00 | 0.2315 |
| descend_place | 1.00 | 0.0574 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.519, 0.005, 0.153) | (0.526, 0.005, 0.030)→(0.526, 0.005, 0.026) | 0.246→0.249 |
| descend_grasp | descend | 1.00 / step_budget | (0.519, 0.005, 0.153)→(0.521, 0.005, 0.039) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 |
| grasp_1 | grasp | 1.00 / step_budget | (0.521, 0.005, 0.039)→(0.512, 0.005, 0.028) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 |
| lift_1 | lift | 1.00 / step_budget | (0.512, 0.005, 0.028)→(0.508, 0.005, 0.132) | (0.526, 0.005, 0.026)→(0.528, 0.005, 0.122) | 0.249→0.205 |
| approach_goal | approach | 1.00 / step_budget | (0.508, 0.005, 0.132)→(0.604, 0.165, 0.262) | (0.528, 0.005, 0.122)→(0.567, 0.109, 0.062) | 0.205→0.172 |
| descend_place | descend | 1.00 / step_budget | (0.604, 0.165, 0.262)→(0.607, 0.171, 0.205) | (0.567, 0.109, 0.062)→(0.567, 0.112, 0.043) | 0.172→0.160 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.419
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 1.000
- phase_score: 0.550
- phase_breakdown.place_score: 0.721
- phase_breakdown.grasp_approach_score: 0.153
- grasp_place_fitness: 0.977

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.977
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: -0.020
- **K-run variance**: 0.0346
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.298


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `104d9d5641b6f93313b49acc931f841aa27a6ce63eca9eff4a16c33838e2c9c3`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `9de75aa839370ff688dada9a37e29517e2f368ed4f09f6a013379103594581cf`; realized-scene SHA-256: `1959b3932a54fd3d3850620783d44a63a35b8fa059f78d939fdbdef5fbfc64e8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.54431,0.00113,0.03]},{"name":"goal","value":[0.64762,0.15808,0.1911]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.54431,0.00113,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.64762,0.15808,0.1911]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.4,"average_solve_count":100.0,"average_success_count":100.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.1177,"approach_1.approach_speed":0.46184,"approach_goal.approach_goal_speed":0.4427,"approach_goal.place_approach_z":0.10409,"descend_grasp.descend_speed":0.23808,"descend_grasp.grasp_z_offset":-0.00463,"descend_place.descend_place_speed":0.17159,"descend_place.place_z_offset":0.01517,"lift_1.lift_height":0.1267,"lift_1.lift_speed":0.36287},"optimized_scores":{"best_composite_score":-0.02022,"best_fitness_score":0.59978,"best_task_score":0.24814},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1558.0,"contact_point_centroid":[0.57531,0.07127,-0.00273],"force_p95":0.26284,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.74822,"mean_force":0.1613,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.60651,0.10798,0.23728]},{"body_a":"world","body_b":"grasp_target","contact_count":70.0,"contact_point_centroid":[0.54064,0.00073,-0.00138],"force_p95":0.65474,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.67964,"mean_force":0.16428,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52795,0.00082,0.03062]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4640.0,"contact_point_centroid":[0.52897,-0.01808,0.07912],"force_p95":0.11536,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35336,"mean_force":0.07802,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52549,0.00077,0.07689]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1555.0,"contact_point_centroid":[0.54406,0.03771,0.15074],"force_p95":0.21219,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33873,"mean_force":0.11324,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53799,0.01944,0.15177]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4949.0,"contact_point_centroid":[0.529,0.01955,0.07716],"force_p95":0.11271,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33542,"mean_force":0.07427,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52552,0.00078,0.07526]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1487.0,"contact_point_centroid":[0.54249,-0.00135,0.14945],"force_p95":0.20039,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30873,"mean_force":0.10503,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53628,0.01705,0.14968]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5443,0.001,-0.00203],"force_p95":0.13229,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15853,"mean_force":0.12538,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53051,0.00087,0.03087]},{"body_a":"world","body_b":"grasp_target","contact_count":1020.0,"contact_point_centroid":[0.54431,0.00113,-0.00187],"force_p95":0.13691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12311,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51616,0.00044,0.23329]},{"body_a":"world","body_b":"grasp_target","contact_count":880.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.53546,0.00095,0.10265]},{"body_a":"world","body_b":"grasp_target","contact_count":500.0,"contact_point_centroid":[0.57465,0.07018,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.64087,0.15237,0.25082]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4115.0,"contact_point_centroid":[0.53051,-0.01835,0.03215],"force_p95":0.07616,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11564,"mean_force":0.05173,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52929,0.00085,0.02948]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4878.0,"contact_point_centroid":[0.53041,0.01992,0.03127],"force_p95":0.06823,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0962,"mean_force":0.04479,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52929,0.00085,0.02948]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1552.0,"contact_point_centroid":[0.60969,0.11145,0.24296],"force_p95":0.01186,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01605,"mean_force":0.01051,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.60925,0.11144,0.2407]},{"body_a":"left_finger","body_b":"right_finger","contact_count":536.0,"contact_point_centroid":[0.64134,0.15237,0.25336],"force_p95":0.01093,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01096,"mean_force":0.0104,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.64086,0.15235,0.25102]}],"total_contact_groups":14},"final_pose_error":0.01486,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.57465,0.07018,0.01602],"final_tcp_position":[0.64269,0.15491,0.21992],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"phases":[{"n_steps":256.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"grasp_approach","tcp_end":[0.53444,0.00091,0.16456],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13889,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":220.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"grasp_approach","tcp_end":[0.53837,0.00101,0.04028],"tcp_start":[0.53444,0.00091,0.16456],"tcp_to_object_dist_end":0.01545,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54417,0.00072,0.02588],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25053,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.52926,0.00084,0.02944],"tcp_start":[0.53837,0.00101,0.04028],"tcp_to_object_dist_end":0.01533,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":343.0,"n_steps_budget":600.0,"object_pos_end":[0.54512,0.00087,0.12509],"object_pos_start":[0.54417,0.00072,0.02588],"object_to_goal_dist_end":0.19895,"object_to_goal_dist_start":0.25053,"object_z_max":0.12484,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","tcp_end":[0.52539,0.00078,0.13666],"tcp_start":[0.52926,0.00084,0.02944],"tcp_to_object_dist_end":0.02287,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":657.0,"n_steps_budget":1000.0,"object_pos_end":[0.57465,0.07018,0.01602],"object_pos_start":[0.54512,0.00087,0.12509],"object_to_goal_dist_end":0.20906,"object_to_goal_dist_start":0.19895,"object_z_max":0.14772,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"place","tcp_end":[0.63977,0.15012,0.27872],"tcp_start":[0.52539,0.00078,0.13666],"tcp_to_object_dist_end":0.28221,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":125.0,"n_steps_budget":1000.0,"object_pos_end":[0.57465,0.07018,0.01602],"object_pos_start":[0.57465,0.07018,0.01602],"object_to_goal_dist_end":0.20906,"object_to_goal_dist_start":0.20906,"object_z_max":0.01602,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"place","tcp_end":[0.64269,0.15491,0.21992],"tcp_start":[0.63977,0.15012,0.27872],"tcp_to_object_dist_end":0.23105,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `349f925163f8e9284ad51ad55d38356f2e3c8deb4dc54e8ff12260e5f6d4b0f8`; realized-scene SHA-256: `e32d7866764afb23ec7c7faebb4bcca0aa39fbf2f1ab61f3c9c527b297153af9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5305,0.03079,0.03]},{"name":"goal","value":[0.60153,0.17858,0.10809]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5305,0.03079,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.60153,0.17858,0.10809]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.28,"average_solve_count":100.0,"average_success_count":100.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.10313,"approach_1.approach_speed":0.50213,"approach_goal.approach_goal_speed":0.41756,"approach_goal.place_approach_z":0.08119,"descend_grasp.descend_speed":0.30932,"descend_grasp.grasp_z_offset":-0.00837,"descend_place.descend_place_speed":0.15053,"descend_place.place_z_offset":0.00164,"lift_1.lift_height":0.12039,"lift_1.lift_speed":0.45022},"optimized_scores":{"best_composite_score":0.35711,"best_fitness_score":0.97711,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":78.0,"contact_point_centroid":[0.52679,0.02818,-0.00145],"force_p95":0.71364,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.73918,"mean_force":0.15826,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51464,0.029,0.02757]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4437.0,"contact_point_centroid":[0.51551,0.00995,0.07329],"force_p95":0.11302,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34705,"mean_force":0.07552,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5123,0.02884,0.0709]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4800.0,"contact_point_centroid":[0.51546,0.04767,0.07092],"force_p95":0.11039,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34695,"mean_force":0.07173,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51234,0.02884,0.06904]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1008.0,"contact_point_centroid":[0.59716,0.18788,0.14721],"force_p95":0.20677,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29929,"mean_force":0.1165,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.5926,0.17001,0.15092]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":759.0,"contact_point_centroid":[0.59685,0.15196,0.14817],"force_p95":0.21684,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26828,"mean_force":0.14692,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.59255,0.16988,0.15209]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53057,0.03043,-0.00216],"force_p95":0.16935,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25891,"mean_force":0.13497,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51723,0.02918,0.02744]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4486.0,"contact_point_centroid":[0.55511,0.07691,0.15025],"force_p95":0.14677,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22679,"mean_force":0.0991,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5494,0.0955,0.14938]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5214.0,"contact_point_centroid":[0.55739,0.1177,0.1513],"force_p95":0.12144,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20735,"mean_force":0.08727,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5516,0.09934,0.15077]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3995.0,"contact_point_centroid":[0.51716,0.0099,0.02884],"force_p95":0.08267,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15145,"mean_force":0.05257,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51602,0.0291,0.02611]},{"body_a":"world","body_b":"grasp_target","contact_count":1092.0,"contact_point_centroid":[0.5305,0.03079,-0.00188],"force_p95":0.1365,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12307,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51056,0.01268,0.22636]},{"body_a":"world","body_b":"grasp_target","contact_count":832.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.52299,0.02789,0.09374]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5029.0,"contact_point_centroid":[0.51697,0.04828,0.0279],"force_p95":0.07466,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08818,"mean_force":0.04474,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51603,0.0291,0.02612]}],"total_contact_groups":12},"final_pose_error":0.01499,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.60092,0.1742,0.09735],"final_tcp_position":[0.59484,0.17388,0.12229],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"phases":[{"n_steps":274.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"grasp_approach","tcp_end":[0.5229,0.02623,0.15075],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12504,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":208.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"grasp_approach","tcp_end":[0.52494,0.02967,0.03635],"tcp_start":[0.5229,0.02623,0.15075],"tcp_to_object_dist_end":0.01179,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53039,0.02913,0.02548],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18499,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.516,0.0291,0.02608],"tcp_start":[0.52494,0.02967,0.03635],"tcp_to_object_dist_end":0.0144,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":318.0,"n_steps_budget":600.0,"object_pos_end":[0.53237,0.02902,0.11918],"object_pos_start":[0.53039,0.02913,0.02548],"object_to_goal_dist_end":0.16515,"object_to_goal_dist_start":0.18499,"object_z_max":0.11893,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","tcp_end":[0.51212,0.02883,0.12702],"tcp_start":[0.516,0.0291,0.02608],"tcp_to_object_dist_end":0.02172,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":457.0,"n_steps_budget":1000.0,"object_pos_end":[0.60053,0.16684,0.15456],"object_pos_start":[0.53237,0.02902,0.11918],"object_to_goal_dist_end":0.04794,"object_to_goal_dist_start":0.16515,"object_z_max":0.1545,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"place","tcp_end":[0.59158,0.1666,0.17693],"tcp_start":[0.51212,0.02883,0.12702],"tcp_to_object_dist_end":0.0241,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":126.0,"n_steps_budget":1000.0,"object_pos_end":[0.60092,0.1742,0.09735],"object_pos_start":[0.60053,0.16684,0.15456],"object_to_goal_dist_end":0.01162,"object_to_goal_dist_start":0.04794,"object_z_max":0.15457,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"place","tcp_end":[0.59484,0.17388,0.12229],"tcp_start":[0.59158,0.1666,0.17693],"tcp_to_object_dist_end":0.02567,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `a1798e4fdcacfe8740623adfe3f78d2bc74e0d14c8233e64f02c40cf2a534ecc`; realized-scene SHA-256: `584133b5261cffac0dd4282704ff39e97bf4d452e60b02507679bbdea5a4de22`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50382,-0.01567,0.03]},{"name":"goal","value":[0.58691,0.18745,0.24812]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.50382,-0.01567,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58691,0.18745,0.24812]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.41,"average_solve_count":100.0,"average_success_count":100.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.09449,"approach_1.approach_speed":0.78177,"approach_goal.approach_goal_speed":0.40971,"approach_goal.place_approach_z":0.09768,"descend_grasp.descend_speed":0.41137,"descend_grasp.grasp_z_offset":-0.00588,"descend_place.descend_place_speed":0.23253,"descend_place.place_z_offset":0.00936,"lift_1.lift_height":0.12129,"lift_1.lift_speed":0.25972},"optimized_scores":{"best_composite_score":-0.0529,"best_fitness_score":0.5671,"best_task_score":0.17795},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1629.0,"contact_point_centroid":[0.5263,0.09021,-0.00273],"force_p95":0.23675,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.78837,"mean_force":0.16598,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55411,0.12484,0.27323]},{"body_a":"world","body_b":"grasp_target","contact_count":72.0,"contact_point_centroid":[0.50028,-0.01462,-0.00135],"force_p95":0.64299,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.68595,"mean_force":0.15757,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4893,-0.01507,0.03118]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1758.0,"contact_point_centroid":[0.50343,0.02888,0.15554],"force_p95":0.19101,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37125,"mean_force":0.10852,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.4974,0.01047,0.15511]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4603.0,"contact_point_centroid":[0.48945,0.00397,0.07663],"force_p95":0.10969,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36147,"mean_force":0.07103,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48707,-0.01504,0.07411]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5085.0,"contact_point_centroid":[0.48948,-0.0339,0.07484],"force_p95":0.10642,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3323,"mean_force":0.06579,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48708,-0.01504,0.07307]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1773.0,"contact_point_centroid":[0.502,-0.01116,0.15263],"force_p95":0.18405,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30876,"mean_force":0.09826,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.49594,0.00725,0.15199]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50382,-0.01549,-0.00205],"force_p95":0.13908,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18075,"mean_force":0.12708,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49174,-0.0151,0.03106]},{"body_a":"world","body_b":"grasp_target","contact_count":1088.0,"contact_point_centroid":[0.50382,-0.01567,-0.00188],"force_p95":0.1365,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12308,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49946,-0.00646,0.22318]},{"body_a":"world","body_b":"grasp_target","contact_count":780.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.4987,-0.01425,0.09184]},{"body_a":"world","body_b":"grasp_target","contact_count":508.0,"contact_point_centroid":[0.5249,0.09083,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.582,0.18105,0.30183]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4099.0,"contact_point_centroid":[0.49115,0.00412,0.03262],"force_p95":0.07746,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12227,"mean_force":0.05179,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49059,-0.01509,0.02986]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4912.0,"contact_point_centroid":[0.49119,-0.03418,0.0317],"force_p95":0.06953,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08496,"mean_force":0.04475,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49059,-0.01509,0.02986]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1693.0,"contact_point_centroid":[0.55565,0.1271,0.27775],"force_p95":0.01169,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01648,"mean_force":0.01055,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55525,0.12709,0.27559]},{"body_a":"left_finger","body_b":"right_finger","contact_count":542.0,"contact_point_centroid":[0.58233,0.18106,0.30416],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01277,"mean_force":0.01045,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.582,0.18105,0.30183]}],"total_contact_groups":14},"final_pose_error":0.01494,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.5249,0.09083,0.01602],"final_tcp_position":[0.58324,0.18399,0.27154],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"phases":[{"n_steps":273.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"grasp_approach","tcp_end":[0.50001,-0.01338,0.14386],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11792,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":195.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"grasp_approach","tcp_end":[0.49912,-0.01517,0.03913],"tcp_start":[0.50001,-0.01338,0.14386],"tcp_to_object_dist_end":0.01393,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50369,-0.015,0.02581],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31198,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.49056,-0.01509,0.02983],"tcp_start":[0.49912,-0.01517,0.03913],"tcp_to_object_dist_end":0.01374,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":310.0,"n_steps_budget":600.0,"object_pos_end":[0.50594,-0.01501,0.12143],"object_pos_start":[0.50369,-0.015,0.02581],"object_to_goal_dist_end":0.25218,"object_to_goal_dist_start":0.31198,"object_z_max":0.12117,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","tcp_end":[0.4869,-0.01502,0.13174],"tcp_start":[0.49056,-0.01509,0.02983],"tcp_to_object_dist_end":0.02166,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":710.0,"n_steps_budget":1000.0,"object_pos_end":[0.5249,0.09083,0.01602],"object_pos_start":[0.50594,-0.01501,0.12143],"object_to_goal_dist_end":0.25894,"object_to_goal_dist_start":0.25218,"object_z_max":0.15989,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"place","tcp_end":[0.58127,0.17843,0.32907],"tcp_start":[0.4869,-0.01502,0.13174],"tcp_to_object_dist_end":0.32993,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":127.0,"n_steps_budget":1000.0,"object_pos_end":[0.5249,0.09083,0.01602],"object_pos_start":[0.5249,0.09083,0.01602],"object_to_goal_dist_end":0.25894,"object_to_goal_dist_start":0.25894,"object_z_max":0.01602,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"place","tcp_end":[0.58324,0.18399,0.27154],"tcp_start":[0.58127,0.17843,0.32907],"tcp_to_object_dist_end":0.27817,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```