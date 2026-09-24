## Search State

- **Seed**: 4
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 13 | -0.0521 | 0.49 | ✅ accepted |
| 11 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.0573 | 0.33 | ✅ accepted |
| 10 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.1808 | 0.21 | ❌ rejected |
| 9 | approach → contact → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 8 | -0.2250 | 0.20 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.2972 | 0.19 | ❌ rejected |

**Proposal policy**: task_score is 0.49 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.052) — your mutation base

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
  - 0.12
  weight: 0.3
- id: place_at_goal
  target_entity: object
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
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.08
      - 0.18
      default: 0.12
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.3
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_object
- id: descend_to_grasp
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
    - 0.01
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.3
      binds_to:
      - path: generator.speed
        mode: replace
    grasp_z_offset:
      type: scalar
      range:
      - 0.0
      - 0.04
      default: 0.01
      binds_to:
      - path: target.offset.z
        mode: replace
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
  parameters:
    grasp_force_threshold:
      type: scalar
      range:
      - 0.05
      - 0.5
      default: 0.1
      binds_to:
      - path: guards.grasp_contact.threshold
        mode: replace
    grasp_retry_x:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: retry.offset.x
        mode: replace
    grasp_retry_y:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: retry.offset.y
        mode: replace
  guards:
  - id: grasp_contact
    when: during_phase
    predicate: bilateral_grasp
    threshold: 0.1
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.0
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
      distance: 0.15
      axis: world_z
      mode: replace_offset_projection
      sign: positive
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.1
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.3
      binds_to:
      - path: generator.speed
        mode: replace
- id: transport_to_goal
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
    tolerance: 0.02
    orientation:
      mode: keep_current
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
      - 0.1
      - 0.5
      default: 0.3
      binds_to:
      - path: generator.speed
        mode: replace
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
    - 0.02
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    place_height:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: target.offset.z
        mode: replace
    place_speed:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.3
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: place_at_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.12], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.01], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - grasp_z_offset: status=consumed; consumers=target.offset.z (replace)
- **grasp_object** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - grasp_force_threshold: status=consumed; consumers=guards.grasp_contact.threshold (replace)
    - grasp_retry_x: status=consumed; consumers=retry.offset.x (replace)
    - grasp_retry_y: status=consumed; consumers=retry.offset.y (replace)
  - guards:
    - id=grasp_contact, when=during_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.1
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.0]
- **lift_object** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.15, mode=replace_offset_projection, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
- **transport_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_height: status=consumed; consumers=target.offset.z (replace)
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.02], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_height: status=consumed; consumers=target.offset.z (replace)
    - place_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: -0.052
- **task_score** (E): 0.490
- **fitness_score**: 0.718  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.770

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1479 |
| descend_to_grasp | 1.00 | 1.00 | 0.1102 |
| grasp_object | 0.00 | 1.00 | 0.0000 |
| lift_object | 1.00 | 1.00 | 0.1014 |
| transport_to_goal | 1.00 | 1.00 | 0.2503 |
| descend_to_place | 1.00 | 1.00 | 0.0739 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.519, 0.005, 0.156) | (0.526, 0.005, 0.030)→(0.526, 0.005, 0.026) | 0.246→0.249 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.519, 0.005, 0.156)→(0.521, 0.005, 0.046) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_object | grasp | 0.00 / guard_failure | (0.516, 0.005, 0.040)→(0.516, 0.005, 0.040) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 44.000 | 0.137 | 0.179 |
| lift_object | lift | 1.00 / step_budget | (0.516, 0.005, 0.040)→(0.512, 0.005, 0.141) | (0.526, 0.005, 0.026)→(0.527, 0.005, 0.123) | 0.249→0.206 | 1.00 / 27.333 | 98.416 | 0.546 |
| transport_to_goal | approach | 1.00 / step_budget | (0.512, 0.005, 0.141)→(0.605, 0.166, 0.301) | (0.527, 0.005, 0.123)→(0.590, 0.122, 0.067) | 0.206→0.167 | 1.00 / 14.000 | 91003.588 | 1.553 |
| descend_to_place | descend | 1.00 / step_budget | (0.605, 0.166, 0.301)→(0.608, 0.171, 0.227) | (0.590, 0.122, 0.067)→(0.590, 0.124, 0.049) | 0.167→0.149 | 1.00 / 14.000 | 55983.992 | 0.179 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.566
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.565
- phase_breakdown.place_at_goal_score: 0.466
- phase_breakdown.approach_object_score: 0.795
- grasp_place_fitness: 0.972

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.972
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: -0.158
- **K-run variance**: 0.0326
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Parameters at lower bound**: descend_to_grasp.grasp_z_offset
- **Final σ (mean)**: 0.317


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.32673,"average_solve_count":101.0,"average_success_count":101.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.08714,"approach_object.approach_speed":0.4456,"descend_to_grasp.descend_speed":0.33996,"descend_to_grasp.grasp_z_offset":0.0,"descend_to_place.place_height":0.02706,"descend_to_place.place_speed":0.29854,"grasp_object.grasp_force_threshold":0.26132,"grasp_object.grasp_retry_x":-0.01884,"grasp_object.grasp_retry_y":0.01583,"lift_object.lift_height":0.12954,"lift_object.lift_speed":0.32742,"transport_to_goal.transport_height":0.17749,"transport_to_goal.transport_speed":0.3014},"optimized_scores":{"best_composite_score":-0.15841,"best_fitness_score":0.61159,"best_task_score":0.27654},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1514.0,"contact_point_centroid":[0.60348,0.09052,-0.00276],"force_p95":0.34238,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.19559,"mean_force":0.1554,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.61375,0.11498,0.30076]},{"body_a":"world","body_b":"grasp_target","contact_count":72.0,"contact_point_centroid":[0.54144,0.00118,-0.00138],"force_p95":0.54773,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57872,"mean_force":0.13271,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.53176,0.00089,0.03973]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3274.0,"contact_point_centroid":[0.5548,0.04839,0.18526],"force_p95":0.12631,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37621,"mean_force":0.08417,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54892,0.03008,0.18464]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5578.0,"contact_point_centroid":[0.53077,0.01996,0.09104],"force_p95":0.10592,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34998,"mean_force":0.06652,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52923,0.00085,0.08869]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6376.0,"contact_point_centroid":[0.53072,-0.01806,0.08867],"force_p95":0.10017,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31089,"mean_force":0.05958,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52925,0.00085,0.08695]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2667.0,"contact_point_centroid":[0.55288,0.00923,0.18307],"force_p95":0.1637,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30264,"mean_force":0.09964,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54732,0.02785,0.18174]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.5443,0.00116,-0.00202],"force_p95":0.12808,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14471,"mean_force":0.12457,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.53335,0.00092,0.03898]},{"body_a":"world","body_b":"grasp_target","contact_count":1196.0,"contact_point_centroid":[0.54431,0.00113,-0.00189],"force_p95":0.13615,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12304,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51658,0.00046,0.21789]},{"body_a":"world","body_b":"grasp_target","contact_count":664.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53577,0.00096,0.09011]},{"body_a":"world","body_b":"grasp_target","contact_count":740.0,"contact_point_centroid":[0.6034,0.09051,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.64299,0.15351,0.2965]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5292.0,"contact_point_centroid":[0.53287,0.02021,0.04052],"force_p95":0.07416,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09501,"mean_force":0.04969,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.53299,0.00092,0.03858]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6432.0,"contact_point_centroid":[0.53239,-0.01815,0.04007],"force_p95":0.06303,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08831,"mean_force":0.04103,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.53299,0.00092,0.03858]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1423.0,"contact_point_centroid":[0.61758,0.11928,0.30898],"force_p95":0.01214,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01623,"mean_force":0.01068,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.61708,0.11927,0.30667]},{"body_a":"left_finger","body_b":"right_finger","contact_count":789.0,"contact_point_centroid":[0.64342,0.15352,0.29881],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01281,"mean_force":0.01045,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.64299,0.15351,0.29642]}],"total_contact_groups":14},"final_pose_error":0.01987,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.6034,0.09051,0.01602],"final_tcp_position":[0.64431,0.15592,0.23764],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":2.19559,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":300.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1196.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.53514,0.00093,0.1344],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.10876,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":166.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":664.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53816,0.00101,0.04503],"tcp_start":[0.53514,0.00093,0.1344],"tcp_to_object_dist_end":0.01998,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54423,0.00114,0.02593],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25021,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12803,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13528.0,"raw_peak_contact_force":0.14471,"tcp_end":[0.53297,0.00092,0.03856],"tcp_start":[0.53297,0.00092,0.03856],"tcp_to_object_dist_end":0.01693,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":351.0,"n_steps_budget":600.0,"object_pos_end":[0.54541,0.00105,0.1308],"object_pos_start":[0.54424,0.00114,0.02593],"object_to_goal_dist_end":0.19684,"object_to_goal_dist_start":0.25021,"object_z_max":0.13055,"peak_contact_force":0.10624,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":12026.0,"raw_peak_contact_force":0.57872,"tcp_end":[0.52922,0.00085,0.14871],"tcp_start":[0.53297,0.00092,0.03856],"tcp_to_object_dist_end":0.02414,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":754.0,"n_steps_budget":1000.0,"object_pos_end":[0.6034,0.09051,0.01602],"object_pos_start":[0.54541,0.00105,0.1308],"object_to_goal_dist_end":0.19281,"object_to_goal_dist_start":0.19684,"object_z_max":0.19515,"peak_contact_force":0.12263,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8878.0,"raw_peak_contact_force":2.19559,"subtask_id":"place_at_goal","tcp_end":[0.64189,0.15133,0.35068],"tcp_start":[0.52922,0.00085,0.14871],"tcp_to_object_dist_end":0.34231,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":185.0,"n_steps_budget":1000.0,"object_pos_end":[0.6034,0.09051,0.01602],"object_pos_start":[0.6034,0.09051,0.01602],"object_to_goal_dist_end":0.19281,"object_to_goal_dist_start":0.19281,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1529.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_at_goal","tcp_end":[0.64431,0.15592,0.23764],"tcp_start":[0.64189,0.15133,0.35068],"tcp_to_object_dist_end":0.23466,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.22,"average_solve_count":100.0,"average_success_count":100.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.10924,"approach_object.approach_speed":0.39594,"descend_to_grasp.descend_speed":0.41466,"descend_to_grasp.grasp_z_offset":0.00122,"descend_to_place.place_height":0.01935,"descend_to_place.place_speed":0.26529,"grasp_object.grasp_force_threshold":0.36356,"grasp_object.grasp_retry_x":-0.00312,"grasp_object.grasp_retry_y":-0.00191,"lift_object.lift_height":0.12244,"lift_object.lift_speed":0.37739,"transport_to_goal.transport_height":0.10402,"transport_to_goal.transport_speed":0.20751},"optimized_scores":{"best_composite_score":0.20215,"best_fitness_score":0.97215,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":78.0,"contact_point_centroid":[0.52746,0.02916,-0.00143],"force_p95":0.53154,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55008,"mean_force":0.11767,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51853,0.0292,0.04122]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6142.0,"contact_point_centroid":[0.51711,0.04815,0.08866],"force_p95":0.09853,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32509,"mean_force":0.05778,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.5162,0.02905,0.08671]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5948.0,"contact_point_centroid":[0.51731,0.00998,0.08951],"force_p95":0.09594,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31228,"mean_force":0.0588,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51622,0.02905,0.08746]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1202.0,"contact_point_centroid":[0.59587,0.15144,0.17215],"force_p95":0.17543,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2914,"mean_force":0.09605,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59338,0.16999,0.17452]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1165.0,"contact_point_centroid":[0.59615,0.18837,0.17147],"force_p95":0.16925,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28908,"mean_force":0.0981,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59344,0.17011,0.17354]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.53055,0.0306,-0.00214],"force_p95":0.15687,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22033,"mean_force":0.13311,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52025,0.02933,0.04017]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6015.0,"contact_point_centroid":[0.55839,0.08198,0.17055],"force_p95":0.12139,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2049,"mean_force":0.07777,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55451,0.10064,0.17023]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5934.0,"contact_point_centroid":[0.55932,0.12002,0.17121],"force_p95":0.11086,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19953,"mean_force":0.07806,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55491,0.10137,0.17053]},{"body_a":"world","body_b":"grasp_target","contact_count":1056.0,"contact_point_centroid":[0.5305,0.03079,-0.00188],"force_p95":0.1365,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12309,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.5105,0.01258,0.22946]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5800.0,"contact_point_centroid":[0.52008,0.01012,0.04171],"force_p95":0.07288,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.133,"mean_force":0.04495,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.51988,0.0293,0.03978]},{"body_a":"world","body_b":"grasp_target","contact_count":816.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52294,0.02777,0.10178]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5998.0,"contact_point_centroid":[0.52006,0.04854,0.04164],"force_p95":0.0734,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07693,"mean_force":0.0449,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.51989,0.0293,0.03978]}],"total_contact_groups":12},"final_pose_error":0.01964,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.59966,0.17335,0.11476],"final_tcp_position":[0.59527,0.17356,0.14536],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":167951.73011,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":265.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1056.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.52277,0.02604,0.15703],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13133,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":204.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":816.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.52495,0.02962,0.04595],"tcp_start":[0.52277,0.02604,0.15703],"tcp_to_object_dist_end":0.02072,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53047,0.02969,0.02557],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18446,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.15066,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13602.0,"raw_peak_contact_force":0.22033,"tcp_end":[0.51987,0.0293,0.03976],"tcp_start":[0.51987,0.0293,0.03976],"tcp_to_object_dist_end":0.01771,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":325.0,"n_steps_budget":600.0,"object_pos_end":[0.53174,0.02944,0.124],"object_pos_start":[0.53047,0.02967,0.0256],"object_to_goal_dist_end":0.16543,"object_to_goal_dist_start":0.18447,"object_z_max":0.12375,"peak_contact_force":0.10538,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":12168.0,"raw_peak_contact_force":0.55008,"tcp_end":[0.51611,0.02904,0.14257],"tcp_start":[0.51987,0.0293,0.03976],"tcp_to_object_dist_end":0.02427,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":459.0,"n_steps_budget":1000.0,"object_pos_end":[0.59958,0.167,0.17006],"object_pos_start":[0.53174,0.02944,0.124],"object_to_goal_dist_end":0.06307,"object_to_goal_dist_start":0.16543,"object_z_max":0.16998,"peak_contact_force":0.12395,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":11949.0,"raw_peak_contact_force":0.2049,"subtask_id":"place_at_goal","tcp_end":[0.59214,0.16672,0.19922],"tcp_start":[0.51611,0.02904,0.14257],"tcp_to_object_dist_end":0.0301,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":102.0,"n_steps_budget":1000.0,"object_pos_end":[0.59966,0.17335,0.11476],"object_pos_start":[0.59958,0.167,0.17006],"object_to_goal_dist_end":0.00868,"object_to_goal_dist_start":0.06307,"object_z_max":0.17007,"peak_contact_force":167951.73011,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2367.0,"raw_peak_contact_force":0.2914,"subtask_id":"place_at_goal","tcp_end":[0.59527,0.17356,0.14536],"tcp_start":[0.59214,0.16672,0.19922],"tcp_to_object_dist_end":0.03092,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.58,"average_solve_count":100.0,"average_success_count":100.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.12705,"approach_object.approach_speed":0.25033,"descend_to_grasp.descend_speed":0.33397,"descend_to_grasp.grasp_z_offset":0.00052,"descend_to_place.place_height":0.0312,"descend_to_place.place_speed":0.31573,"grasp_object.grasp_force_threshold":0.3871,"grasp_object.grasp_retry_x":0.00527,"grasp_object.grasp_retry_y":-0.01102,"lift_object.lift_height":0.11041,"lift_object.lift_speed":0.29536,"transport_to_goal.transport_height":0.12134,"transport_to_goal.transport_speed":0.39881},"optimized_scores":{"best_composite_score":-0.20004,"best_fitness_score":0.56996,"best_task_score":0.19434},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1369.0,"contact_point_centroid":[0.5679,0.10899,-0.00284],"force_p95":0.40592,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.25879,"mean_force":0.15797,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.56089,0.13589,0.30233]},{"body_a":"world","body_b":"grasp_target","contact_count":78.0,"contact_point_centroid":[0.50122,-0.01494,-0.00132],"force_p95":0.48512,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.51051,"mean_force":0.11385,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49315,-0.0151,0.04177]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5712.0,"contact_point_centroid":[0.49137,-0.03416,0.08616],"force_p95":0.08162,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30985,"mean_force":0.05461,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49086,-0.01505,0.08425]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5343.0,"contact_point_centroid":[0.4914,0.0041,0.08584],"force_p95":0.08422,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30933,"mean_force":0.05737,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49089,-0.01505,0.08354]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3794.0,"contact_point_centroid":[0.51251,0.04372,0.17588],"force_p95":0.12155,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24891,"mean_force":0.08004,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50752,0.02521,0.17448]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3308.0,"contact_point_centroid":[0.51003,0.00155,0.17036],"force_p95":0.15116,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2417,"mean_force":0.08711,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50521,0.02022,0.16883]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.50382,-0.01559,-0.00205],"force_p95":0.13571,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17049,"mean_force":0.12655,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49473,-0.01512,0.04071]},{"body_a":"world","body_b":"grasp_target","contact_count":892.0,"contact_point_centroid":[0.50382,-0.01567,-0.00185],"force_p95":0.13709,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12317,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49965,-0.00617,0.23953]},{"body_a":"world","body_b":"grasp_target","contact_count":928.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.49887,-0.01402,0.11138]},{"body_a":"world","body_b":"grasp_target","contact_count":400.0,"contact_point_centroid":[0.56788,0.10903,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.58283,0.18138,0.32733]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5832.0,"contact_point_centroid":[0.49457,0.00407,0.04228],"force_p95":0.06926,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11186,"mean_force":0.04498,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.4944,-0.01511,0.04038]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5903.0,"contact_point_centroid":[0.49459,-0.03431,0.04226],"force_p95":0.06955,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08877,"mean_force":0.04502,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.4944,-0.01511,0.04038]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1283.0,"contact_point_centroid":[0.56382,0.14111,0.31068],"force_p95":0.01197,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01621,"mean_force":0.01066,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.56346,0.14111,0.3084]},{"body_a":"left_finger","body_b":"right_finger","contact_count":427.0,"contact_point_centroid":[0.58314,0.18139,0.3295],"force_p95":0.01094,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01098,"mean_force":0.01045,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.58283,0.18138,0.32733]}],"total_contact_groups":14},"final_pose_error":0.01957,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.56788,0.10903,0.01602],"final_tcp_position":[0.58382,0.1839,0.29832],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":273010.51813,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":224.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":892.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.5002,-0.01293,0.17601],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15006,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":232.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":928.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.49929,-0.01516,0.04601],"tcp_start":[0.5002,-0.01293,0.17601],"tcp_to_object_dist_end":0.0205,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50376,-0.01525,0.02585],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.3121,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13363,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13539.0,"raw_peak_contact_force":0.17049,"tcp_end":[0.49438,-0.01511,0.04036],"tcp_start":[0.49438,-0.01511,0.04036],"tcp_to_object_dist_end":0.01728,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":36.0,"n_steps":284.0,"n_steps_budget":600.0,"object_pos_end":[0.50515,-0.0151,0.1141],"object_pos_start":[0.50376,-0.01524,0.02585],"object_to_goal_dist_end":0.25626,"object_to_goal_dist_start":0.31209,"object_z_max":0.11383,"peak_contact_force":295.0375,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":11133.0,"raw_peak_contact_force":0.51051,"tcp_end":[0.49063,-0.01504,0.13141],"tcp_start":[0.49438,-0.01511,0.04036],"tcp_to_object_dist_end":0.0226,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":738.0,"n_steps_budget":1000.0,"object_pos_end":[0.56788,0.10903,0.01602],"object_pos_start":[0.50515,-0.0151,0.1141],"object_to_goal_dist_end":0.24572,"object_to_goal_dist_start":0.25626,"object_z_max":0.19464,"peak_contact_force":273010.51813,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9754.0,"raw_peak_contact_force":2.25879,"subtask_id":"place_at_goal","tcp_end":[0.58196,0.17898,0.35224],"tcp_start":[0.49063,-0.01504,0.13141],"tcp_to_object_dist_end":0.34371,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":100.0,"n_steps_budget":1000.0,"object_pos_end":[0.56788,0.10903,0.01602],"object_pos_start":[0.56788,0.10903,0.01602],"object_to_goal_dist_end":0.24572,"object_to_goal_dist_start":0.24572,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":827.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_at_goal","tcp_end":[0.58382,0.1839,0.29832],"tcp_start":[0.58196,0.17898,0.35224],"tcp_to_object_dist_end":0.2925,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```