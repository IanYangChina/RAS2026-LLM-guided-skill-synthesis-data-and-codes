## Search State

- **Seed**: 4
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 18 | -0.8181 | 0.19 | ❌ rejected |
| 13 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 13 | -0.0487 | 0.50 | ✅ accepted |
| 12 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 13 | -0.0521 | 0.49 | ✅ accepted |
| 11 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.0573 | 0.33 | ✅ accepted |
| 10 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.1808 | 0.21 | ❌ rejected |

**Proposal policy**: task_score is 0.19 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.818) — your mutation base

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

- **Composite score**: -0.818
- **task_score** (E): 0.190
- **fitness_score**: 0.182  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 1.000

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 0.00 | 1.00 | 0.1175 |
| descend_to_grasp | 0.00 | 1.00 | 0.0258 |
| grasp_object | 0.00 | 1.00 | 0.0000 |
| lift_object | 0.00 | 1.00 | 0.1966 |
| transport_to_goal | 0.00 | 1.00 | 0.1139 |
| descend_to_place | 0.33 | 1.00 | 0.1302 |
| release_object | 1.00 | 1.00 | 0.0266 |
| retract_after_place | 1.00 | 1.00 | 0.0706 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.459, 0.006, 0.193) | (0.526, 0.005, 0.030)→(0.499, 0.009, 0.019) | 0.246→0.262 | 1.00 / 5.000 | 305.877 | 1408.742 |
| descend_to_grasp | descend | 0.00 / step_budget | (0.459, 0.006, 0.193)→(0.465, 0.013, 0.175) | (0.499, 0.009, 0.019)→(0.499, 0.009, 0.019) | 0.262→0.262 | 1.00 / 5.000 | 361.168 | 849.872 |
| grasp_object | grasp | 0.00 / guard_failure | (0.465, 0.013, 0.174)→(0.465, 0.013, 0.174) | (0.499, 0.009, 0.019)→(0.499, 0.009, 0.019) | 0.262→0.262 | 1.00 / 9.667 | 182025.042 | 284.257 |
| lift_object | lift | 0.00 / step_budget | (0.465, 0.013, 0.174)→(0.462, 0.013, 0.370) | (0.499, 0.009, 0.019)→(0.499, 0.009, 0.019) | 0.262→0.262 | 1.00 / 8.000 | 6499.399 | 204.407 |
| transport_to_goal | approach | 0.00 / step_budget | (0.462, 0.013, 0.370)→(0.536, 0.096, 0.367) | (0.499, 0.009, 0.019)→(0.499, 0.009, 0.019) | 0.262→0.262 | 1.00 / 8.667 | 184.001 | 378.758 |
| descend_to_place | descend | 0.33 / step_budget | (0.536, 0.096, 0.367)→(0.606, 0.159, 0.285) | (0.499, 0.009, 0.019)→(0.494, 0.025, 0.019) | 0.262→0.257 | 1.00 / 9.667 | 181990.597 | 880.236 |
| release_object | release | 1.00 / step_budget | (0.606, 0.159, 0.285)→(0.607, 0.159, 0.312) | (0.494, 0.025, 0.019)→(0.494, 0.025, 0.019) | 0.257→0.257 | 1.00 / 4.000 | 0.123 | 180.717 |
| retract_after_place | retract | 1.00 / step_budget | (0.607, 0.159, 0.312)→(0.617, 0.173, 0.377) | (0.494, 0.025, 0.019)→(0.494, 0.025, 0.019) | 0.257→0.257 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 0.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: None
- terminal_score: 0.270
- phase_score: 0.065
- phase_breakdown.place_at_goal_score: 0.015
- phase_breakdown.approach_object_score: 0.180
- grasp_place_fitness: 0.219

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.219
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.270
- **Median Q (composite search score)**: -0.827
- **K-run variance**: 0.0008
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.257


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":24.0,"average_failure_rate":0.2,"average_mean_iterations":45.65,"average_solve_count":120.0,"average_success_count":96.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.12197,"approach_object.approach_speed":0.26103,"descend_to_grasp.descend_speed":0.31051,"descend_to_grasp.grasp_offset_x":-0.01108,"descend_to_grasp.grasp_offset_y":0.00862,"descend_to_grasp.grasp_z_offset":0.01291,"descend_to_place.place_height":0.00852,"descend_to_place.place_speed":0.37602,"grasp_object.grasp_force_threshold":0.16242,"grasp_object.grasp_retry_x":0.00798,"grasp_object.grasp_retry_y":0.00481,"lift_object.lift_height":0.24886,"lift_object.lift_speed":0.43074,"release_object.release_duration":0.49871,"retract_after_place.retract_height":0.20627,"retract_after_place.retract_speed":0.32535,"transport_to_goal.transport_height":0.21327,"transport_to_goal.transport_speed":0.31304},"optimized_scores":{"best_composite_score":-0.82708,"best_fitness_score":0.17292,"best_task_score":0.17722},"replay_outcomes":[{"contacts":{"omitted_contact_groups":14,"reported_contact_groups":[{"body_a":"world","body_b":"link7","contact_count":24.0,"contact_point_centroid":[0.54197,0.00334,-0.00358],"force_p95":218.65179,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1375.37693,"mean_force":68.0256,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39217,-2e-05,0.04516]},{"body_a":"world","body_b":"link6","contact_count":664.0,"contact_point_centroid":[0.65862,0.00045,-0.00043],"force_p95":422.10397,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1364.54844,"mean_force":218.52345,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.43097,0.00037,0.142]},{"body_a":"world","body_b":"link6","contact_count":138.0,"contact_point_centroid":[0.66541,0.10946,-0.00113],"force_p95":720.18354,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1078.85119,"mean_force":285.55753,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.46624,0.17759,0.17799]},{"body_a":"world","body_b":"link5","contact_count":660.0,"contact_point_centroid":[0.52534,0.20431,-0.00024],"force_p95":436.46733,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":824.42673,"mean_force":284.24721,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.4786,0.01522,0.16649]},{"body_a":"link5","body_b":"hand","contact_count":273.0,"contact_point_centroid":[0.57129,0.17889,0.21747],"force_p95":292.21449,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":685.40185,"mean_force":105.32457,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.46588,0.16984,0.18057]},{"body_a":"world","body_b":"link6","contact_count":415.0,"contact_point_centroid":[0.66458,0.00255,-0.00026],"force_p95":397.5297,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":678.51381,"mean_force":214.63578,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.45124,-0.00037,0.16969]},{"body_a":"world","body_b":"link7","contact_count":28.0,"contact_point_centroid":[0.53351,0.02968,-0.00019],"force_p95":398.13588,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":421.41141,"mean_force":215.11908,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.41129,0.07462,0.08013]},{"body_a":"link5","body_b":"hand","contact_count":158.0,"contact_point_centroid":[0.55278,-0.00208,0.32795],"force_p95":365.19076,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":398.68761,"mean_force":314.10803,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52463,0.06658,0.36516]},{"body_a":"world","body_b":"hand","contact_count":10.0,"contact_point_centroid":[0.46736,0.00812,-2e-05],"force_p95":212.90375,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":213.73109,"mean_force":171.92479,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.39692,-0.00109,0.10005]},{"body_a":"world","body_b":"link6","contact_count":501.0,"contact_point_centroid":[0.67554,0.00556,-0.00012],"force_p95":70.34882,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":175.38074,"mean_force":68.32201,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46478,0.00061,0.17339]},{"body_a":"world","body_b":"link6","contact_count":6.0,"contact_point_centroid":[0.67551,0.00555,-0.0001],"force_p95":166.71163,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":167.75103,"mean_force":97.4871,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46471,0.00058,0.17338]},{"body_a":"world","body_b":"link5","contact_count":71.0,"contact_point_centroid":[0.55078,0.22755,-0.00015],"force_p95":109.60608,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":109.92654,"mean_force":71.68314,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.60864,0.12721,0.27123]},{"body_a":"grasp_target","body_b":"link7","contact_count":151.0,"contact_point_centroid":[0.51851,0.00264,0.03234],"force_p95":3.66859,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.3438,"mean_force":0.91108,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.40382,8e-05,0.08596]},{"body_a":"grasp_target","body_b":"hand","contact_count":117.0,"contact_point_centroid":[0.50541,-0.00057,0.04505],"force_p95":2.25537,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.22928,"mean_force":0.96195,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.4019,6e-05,0.07867]},{"body_a":"grasp_target","body_b":"hand","contact_count":286.0,"contact_point_centroid":[0.48959,0.03307,0.03091],"force_p95":1.43944,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.58596,"mean_force":0.74589,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.40878,0.01177,0.10143]},{"body_a":"world","body_b":"grasp_target","contact_count":2862.0,"contact_point_centroid":[0.51573,0.00332,-0.0024],"force_p95":0.36856,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.16676,"mean_force":0.16773,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.44512,0.00039,0.15631]}],"total_contact_groups":30},"final_pose_error":0.01994,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.4887,0.05105,0.01602],"final_tcp_position":[0.6442,0.15432,0.37809],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":273004.12038,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":783.0,"n_steps_budget":1000.0,"object_pos_end":[0.50766,0.00376,0.01602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.27214,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":334.47163,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3908.0,"raw_peak_contact_force":1375.37693,"subtask_id":"approach_object","tcp_end":[0.46495,0.00101,0.17179],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16154,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":424.0,"n_steps_budget":1000.0,"object_pos_end":[0.50766,0.00376,0.01602],"object_pos_start":[0.50766,0.00376,0.01602],"object_to_goal_dist_end":0.27214,"object_to_goal_dist_start":0.27214,"object_z_max":0.01602,"peak_contact_force":327.60264,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2111.0,"raw_peak_contact_force":678.51381,"tcp_end":[0.46496,0.00053,0.17462],"tcp_start":[0.46495,0.00101,0.17179],"tcp_to_object_dist_end":0.16428,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":100.0,"n_steps_budget":50.0,"object_pos_end":[0.50766,0.00376,0.01602],"object_pos_start":[0.50766,0.00376,0.01602],"object_to_goal_dist_end":0.27214,"object_to_goal_dist_start":0.27214,"object_z_max":0.01602,"peak_contact_force":66.88607,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3305.0,"raw_peak_contact_force":175.38074,"tcp_end":[0.46477,0.00054,0.17329],"tcp_start":[0.46477,0.00055,0.17329],"tcp_to_object_dist_end":0.16305,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":534.0,"n_steps_budget":600.0,"object_pos_end":[0.50766,0.00376,0.01602],"object_pos_start":[0.50766,0.00376,0.01602],"object_to_goal_dist_end":0.27214,"object_to_goal_dist_start":0.27214,"object_z_max":0.01602,"peak_contact_force":9749.0074,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4489.0,"raw_peak_contact_force":167.75103,"tcp_end":[0.4626,0.00012,0.37133],"tcp_start":[0.46477,0.00054,0.17329],"tcp_to_object_dist_end":0.35817,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":398.0,"n_steps_budget":1000.0,"object_pos_end":[0.50766,0.00376,0.01602],"object_pos_start":[0.50766,0.00376,0.01602],"object_to_goal_dist_end":0.27214,"object_to_goal_dist_start":0.27214,"object_z_max":0.01602,"peak_contact_force":273.46633,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3504.0,"raw_peak_contact_force":398.68761,"subtask_id":"place_at_goal","tcp_end":[0.53489,0.07115,0.36675],"tcp_start":[0.4626,0.00012,0.37133],"tcp_to_object_dist_end":0.35819,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4887,0.05105,0.01602],"object_pos_start":[0.50766,0.00376,0.01602],"object_to_goal_dist_end":0.25955,"object_to_goal_dist_start":0.27214,"object_z_max":0.02422,"peak_contact_force":272969.13985,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9483.0,"raw_peak_contact_force":1078.85119,"subtask_id":"place_at_goal","tcp_end":[0.60748,0.12419,0.27025],"tcp_start":[0.53489,0.07115,0.36675],"tcp_to_object_dist_end":0.28999,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4887,0.05105,0.01602],"object_pos_start":[0.4887,0.05105,0.01602],"object_to_goal_dist_end":0.25955,"object_to_goal_dist_start":0.25955,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1098.0,"raw_peak_contact_force":109.92654,"subtask_id":"place_at_goal","tcp_end":[0.60853,0.12596,0.29774],"tcp_start":[0.60748,0.12419,0.27025],"tcp_to_object_dist_end":0.31518,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":316.0,"n_steps_budget":600.0,"object_pos_end":[0.4887,0.05105,0.01602],"object_pos_start":[0.4887,0.05105,0.01602],"object_to_goal_dist_end":0.25955,"object_to_goal_dist_start":0.25955,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1264.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.6442,0.15432,0.37809],"tcp_start":[0.60853,0.12596,0.29774],"tcp_to_object_dist_end":0.40736,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":16.0,"average_failure_rate":0.13008,"average_mean_iterations":31.0,"average_solve_count":123.0,"average_success_count":107.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.16889,"approach_object.approach_speed":0.26811,"descend_to_grasp.descend_speed":0.32389,"descend_to_grasp.grasp_offset_x":0.00206,"descend_to_grasp.grasp_offset_y":-0.00564,"descend_to_grasp.grasp_z_offset":0.01788,"descend_to_place.place_height":0.01911,"descend_to_place.place_speed":0.25464,"grasp_object.grasp_force_threshold":0.13107,"grasp_object.grasp_retry_x":-0.00628,"grasp_object.grasp_retry_y":0.00934,"lift_object.lift_height":0.23758,"lift_object.lift_speed":0.21178,"release_object.release_duration":0.43168,"retract_after_place.retract_height":0.21281,"retract_after_place.retract_speed":0.22543,"transport_to_goal.transport_height":0.22472,"transport_to_goal.transport_speed":0.29923},"optimized_scores":{"best_composite_score":-0.78089,"best_fitness_score":0.21911,"best_task_score":0.26989},"replay_outcomes":[{"contacts":{"omitted_contact_groups":10,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":850.0,"contact_point_centroid":[0.64753,0.01587,-0.00045],"force_p95":352.87686,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1515.83813,"mean_force":223.23884,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.42633,0.01396,0.15389]},{"body_a":"world","body_b":"link6","contact_count":577.0,"contact_point_centroid":[0.63768,0.03206,-0.00022],"force_p95":583.02283,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":950.36242,"mean_force":287.0264,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.4413,0.03959,0.19544]},{"body_a":"world","body_b":"link6","contact_count":770.0,"contact_point_centroid":[0.58863,0.14457,-0.00025],"force_p95":672.18788,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":807.82255,"mean_force":462.38335,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.56932,0.14604,0.29353]},{"body_a":"link5","body_b":"hand","contact_count":134.0,"contact_point_centroid":[0.55139,0.04011,0.31897],"force_p95":399.14842,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":432.89855,"mean_force":322.91947,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51967,0.11725,0.33244]},{"body_a":"world","body_b":"link6","contact_count":501.0,"contact_point_centroid":[0.67268,0.04557,-0.00012],"force_p95":69.42802,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":426.32815,"mean_force":70.24317,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46428,0.05769,0.17607]},{"body_a":"world","body_b":"link6","contact_count":85.0,"contact_point_centroid":[0.66197,0.17559,-0.0001],"force_p95":83.67327,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":303.12797,"mean_force":60.32367,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.62088,0.17522,0.29175]},{"body_a":"link5","body_b":"hand","contact_count":588.0,"contact_point_centroid":[0.4692,0.0872,0.24679],"force_p95":271.37673,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":296.82231,"mean_force":218.95617,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.5374,0.12673,0.3021]},{"body_a":"world","body_b":"link6","contact_count":4.0,"contact_point_centroid":[0.6726,0.04608,-0.0001],"force_p95":234.78632,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":238.85792,"mean_force":170.1053,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46424,0.05771,0.17598]},{"body_a":"grasp_target","body_b":"link7","contact_count":170.0,"contact_point_centroid":[0.50826,0.01513,0.03447],"force_p95":4.06588,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.85682,"mean_force":0.81779,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39944,0.00677,0.09072]},{"body_a":"grasp_target","body_b":"hand","contact_count":149.0,"contact_point_centroid":[0.4991,0.01727,0.04833],"force_p95":2.50869,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.74226,"mean_force":0.81066,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39855,0.00666,0.087]},{"body_a":"world","body_b":"grasp_target","contact_count":3483.0,"contact_point_centroid":[0.49876,0.037,-0.00244],"force_p95":0.36552,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.52426,"mean_force":0.1682,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.43879,0.01348,0.16569]},{"body_a":"grasp_target","body_b":"link5","contact_count":474.0,"contact_point_centroid":[0.51423,0.03416,0.02755],"force_p95":0.7582,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.4474,"mean_force":0.43422,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.53937,0.12934,0.29479]},{"body_a":"grasp_target","body_b":"link6","contact_count":33.0,"contact_point_centroid":[0.54422,0.03477,0.00874],"force_p95":0.67598,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.79157,"mean_force":0.43392,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.38857,0.00621,0.0615]},{"body_a":"world","body_b":"grasp_target","contact_count":3799.0,"contact_point_centroid":[0.49412,0.04111,-0.00265],"force_p95":0.41676,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.76751,"mean_force":0.17731,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.56234,0.14124,0.29866]},{"body_a":"world","body_b":"grasp_target","contact_count":2408.0,"contact_point_centroid":[0.49067,0.03819,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.44202,0.03982,0.19551]},{"body_a":"world","body_b":"grasp_target","contact_count":2004.0,"contact_point_centroid":[0.49067,0.03819,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46428,0.05769,0.17607]}],"total_contact_groups":26},"final_pose_error":0.01763,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.49564,0.04108,0.01602],"final_tcp_position":[0.61814,0.17569,0.31573],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":273004.1209,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":964.0,"n_steps_budget":1000.0,"object_pos_end":[0.49067,0.03819,0.01602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.20119,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":337.20559,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4708.0,"raw_peak_contact_force":1515.83813,"subtask_id":"approach_object","tcp_end":[0.4592,0.02816,0.19763],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.18459,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":602.0,"n_steps_budget":1000.0,"object_pos_end":[0.49067,0.03819,0.01602],"object_pos_start":[0.49067,0.03819,0.01602],"object_to_goal_dist_end":0.20119,"object_to_goal_dist_start":0.20119,"object_z_max":0.01602,"peak_contact_force":368.21764,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2985.0,"raw_peak_contact_force":950.36242,"tcp_end":[0.46441,0.05751,0.17716],"tcp_start":[0.4592,0.02816,0.19763],"tcp_to_object_dist_end":0.16441,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":100.0,"n_steps_budget":50.0,"object_pos_end":[0.49067,0.03819,0.01602],"object_pos_start":[0.49067,0.03819,0.01602],"object_to_goal_dist_end":0.20119,"object_to_goal_dist_start":0.20119,"object_z_max":0.01602,"peak_contact_force":273004.1209,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3288.0,"raw_peak_contact_force":426.32815,"tcp_end":[0.46427,0.05771,0.17599],"tcp_start":[0.46427,0.05771,0.17599],"tcp_to_object_dist_end":0.1633,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":627.0,"n_steps_budget":720.0,"object_pos_end":[0.49067,0.03819,0.01602],"object_pos_start":[0.49067,0.03819,0.01602],"object_to_goal_dist_end":0.20119,"object_to_goal_dist_start":0.20119,"object_z_max":0.01602,"peak_contact_force":9749.06622,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":5250.0,"raw_peak_contact_force":238.85792,"tcp_end":[0.46154,0.06004,0.36317],"tcp_start":[0.46427,0.05771,0.17599],"tcp_to_object_dist_end":0.34906,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":403.0,"n_steps_budget":1000.0,"object_pos_end":[0.49067,0.03819,0.01602],"object_pos_start":[0.49067,0.03819,0.01602],"object_to_goal_dist_end":0.20119,"object_to_goal_dist_start":0.20119,"object_z_max":0.01602,"peak_contact_force":278.41452,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3499.0,"raw_peak_contact_force":432.89855,"subtask_id":"place_at_goal","tcp_end":[0.52693,0.11698,0.33069],"tcp_start":[0.46154,0.06004,0.36317],"tcp_to_object_dist_end":0.3264,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49564,0.04108,0.01602],"object_pos_start":[0.49067,0.03819,0.01602],"object_to_goal_dist_end":0.19646,"object_to_goal_dist_start":0.20119,"object_z_max":0.01606,"peak_contact_force":1.79281,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9904.0,"raw_peak_contact_force":807.82255,"subtask_id":"place_at_goal","tcp_end":[0.62106,0.1753,0.29175],"tcp_start":[0.52693,0.11698,0.33069],"tcp_to_object_dist_end":0.33132,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49564,0.04108,0.01602],"object_pos_start":[0.49564,0.04108,0.01602],"object_to_goal_dist_end":0.19646,"object_to_goal_dist_start":0.19646,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1106.0,"raw_peak_contact_force":303.12797,"subtask_id":"place_at_goal","tcp_end":[0.62115,0.17535,0.31684],"tcp_start":[0.62106,0.1753,0.29175],"tcp_to_object_dist_end":0.35253,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.49564,0.04108,0.01602],"object_pos_start":[0.49564,0.04108,0.01602],"object_to_goal_dist_end":0.19646,"object_to_goal_dist_start":0.19646,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":80.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61814,0.17569,0.31573],"tcp_start":[0.62115,0.17535,0.31684],"tcp_to_object_dist_end":0.35064,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":12.0,"average_failure_rate":0.09836,"average_mean_iterations":25.59016,"average_solve_count":122.0,"average_success_count":110.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.14379,"approach_object.approach_speed":0.32298,"descend_to_grasp.descend_speed":0.27626,"descend_to_grasp.grasp_offset_x":-0.01906,"descend_to_grasp.grasp_offset_y":0.00639,"descend_to_grasp.grasp_z_offset":0.02645,"descend_to_place.place_height":-0.00225,"descend_to_place.place_speed":0.33987,"grasp_object.grasp_force_threshold":0.09693,"grasp_object.grasp_retry_x":0.00097,"grasp_object.grasp_retry_y":4e-05,"lift_object.lift_height":0.25932,"lift_object.lift_speed":0.31277,"release_object.release_duration":0.63466,"retract_after_place.retract_height":0.20819,"retract_after_place.retract_speed":0.18539,"transport_to_goal.transport_height":0.17539,"transport_to_goal.transport_speed":0.23974},"optimized_scores":{"best_composite_score":-0.84643,"best_fitness_score":0.15357,"best_task_score":0.12329},"replay_outcomes":[{"contacts":{"omitted_contact_groups":8,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":887.0,"contact_point_centroid":[0.64065,-0.00544,-0.00044],"force_p95":253.5301,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1335.01041,"mean_force":204.24743,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.41642,-0.00611,0.14804]},{"body_a":"world","body_b":"link7","contact_count":23.0,"contact_point_centroid":[0.53309,0.00041,-0.00337],"force_p95":285.28006,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1329.93512,"mean_force":71.60491,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.38194,-0.00272,0.04645]},{"body_a":"world","body_b":"link6","contact_count":757.0,"contact_point_centroid":[0.62358,-0.00919,-0.00021],"force_p95":572.26616,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":920.74041,"mean_force":316.04243,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.4375,-0.01436,0.20607]},{"body_a":"world","body_b":"link6","contact_count":280.0,"contact_point_centroid":[0.57083,0.16876,-0.00033],"force_p95":709.79325,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":754.03401,"mean_force":515.01652,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.58262,0.16763,0.29354]},{"body_a":"link5","body_b":"hand","contact_count":211.0,"contact_point_centroid":[0.54955,0.09294,0.30767],"force_p95":233.54118,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":304.68913,"mean_force":130.93591,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52302,-0.00758,0.34519]},{"body_a":"world","body_b":"link6","contact_count":493.0,"contact_point_centroid":[0.67649,-0.01632,-0.00012],"force_p95":70.05693,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":251.06247,"mean_force":71.82848,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46475,-0.01976,0.17222]},{"body_a":"world","body_b":"link6","contact_count":5.0,"contact_point_centroid":[0.67652,-0.01627,-0.00011],"force_p95":200.6562,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":206.61269,"mean_force":124.72114,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46468,-0.01977,0.17212]},{"body_a":"world","body_b":"link6","contact_count":84.0,"contact_point_centroid":[0.58971,0.18108,-0.00013],"force_p95":78.27101,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":129.09753,"mean_force":56.88764,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.59035,0.17644,0.29422]},{"body_a":"grasp_target","body_b":"link7","contact_count":420.0,"contact_point_centroid":[0.50095,-0.02137,0.04381],"force_p95":1.13169,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.00707,"mean_force":0.43976,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.40049,-0.00375,0.11433]},{"body_a":"grasp_target","body_b":"hand","contact_count":312.0,"contact_point_centroid":[0.49294,-0.03083,0.05504],"force_p95":2.43752,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.32119,"mean_force":0.56299,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39711,-0.00328,0.10322]},{"body_a":"world","body_b":"grasp_target","contact_count":3045.0,"contact_point_centroid":[0.4945,-0.01696,-0.00265],"force_p95":0.29686,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.40067,"mean_force":0.18335,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.43274,-0.00611,0.16417]},{"body_a":"world","body_b":"grasp_target","contact_count":3128.0,"contact_point_centroid":[0.49878,-0.01623,-0.00199],"force_p95":0.13489,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14379,"mean_force":0.12269,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.43815,-0.01443,0.20586]},{"body_a":"world","body_b":"grasp_target","contact_count":2004.0,"contact_point_centroid":[0.49875,-0.01623,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46475,-0.01976,0.17224]},{"body_a":"world","body_b":"grasp_target","contact_count":2156.0,"contact_point_centroid":[0.49875,-0.01623,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46383,-0.01991,0.28023]},{"body_a":"world","body_b":"grasp_target","contact_count":2552.0,"contact_point_centroid":[0.49875,-0.01623,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52129,0.01665,0.36782]},{"body_a":"world","body_b":"grasp_target","contact_count":2528.0,"contact_point_centroid":[0.49875,-0.01623,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57407,0.14335,0.33207]}],"total_contact_groups":24},"final_pose_error":0.01983,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.49875,-0.01623,0.02602],"final_tcp_position":[0.58809,0.18779,0.43651],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":273004.12026,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49885,-0.01622,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31395,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":245.9545,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4687.0,"raw_peak_contact_force":1335.01041,"subtask_id":"approach_object","tcp_end":[0.45204,-0.0121,0.20871],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.18864,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":782.0,"n_steps_budget":1000.0,"object_pos_end":[0.49875,-0.01623,0.02602],"object_pos_start":[0.49885,-0.01622,0.02602],"object_to_goal_dist_end":0.31398,"object_to_goal_dist_start":0.31395,"object_z_max":0.02605,"peak_contact_force":387.68231,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3965.0,"raw_peak_contact_force":920.74041,"tcp_end":[0.4649,-0.01978,0.17347],"tcp_start":[0.45204,-0.0121,0.20871],"tcp_to_object_dist_end":0.15133,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":100.0,"n_steps_budget":50.0,"object_pos_end":[0.49875,-0.01623,0.02602],"object_pos_start":[0.49875,-0.01623,0.02602],"object_to_goal_dist_end":0.31398,"object_to_goal_dist_start":0.31398,"object_z_max":0.02602,"peak_contact_force":273004.12026,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3282.0,"raw_peak_contact_force":251.06247,"tcp_end":[0.46474,-0.01983,0.17214],"tcp_start":[0.46474,-0.01982,0.17214],"tcp_to_object_dist_end":0.15007,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":539.0,"n_steps_budget":600.0,"object_pos_end":[0.49875,-0.01623,0.02602],"object_pos_start":[0.49875,-0.01623,0.02602],"object_to_goal_dist_end":0.31398,"object_to_goal_dist_start":0.31398,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4505.0,"raw_peak_contact_force":206.61269,"tcp_end":[0.46278,-0.02042,0.37654],"tcp_start":[0.46474,-0.01983,0.17214],"tcp_to_object_dist_end":0.35238,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":638.0,"n_steps_budget":1000.0,"object_pos_end":[0.49875,-0.01623,0.02602],"object_pos_start":[0.49875,-0.01623,0.02602],"object_to_goal_dist_end":0.31398,"object_to_goal_dist_start":0.31398,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5590.0,"raw_peak_contact_force":304.68913,"subtask_id":"place_at_goal","tcp_end":[0.54548,0.09897,0.40327],"tcp_start":[0.46278,-0.02042,0.37654],"tcp_to_object_dist_end":0.3972,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":632.0,"n_steps_budget":1000.0,"object_pos_end":[0.49875,-0.01623,0.02602],"object_pos_start":[0.49875,-0.01623,0.02602],"object_to_goal_dist_end":0.31398,"object_to_goal_dist_start":0.31398,"object_z_max":0.02602,"peak_contact_force":273000.85814,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5534.0,"raw_peak_contact_force":754.03401,"subtask_id":"place_at_goal","tcp_end":[0.59044,0.17626,0.29378],"tcp_start":[0.54548,0.09897,0.40327],"tcp_to_object_dist_end":0.34228,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49875,-0.01623,0.02602],"object_pos_start":[0.49875,-0.01623,0.02602],"object_to_goal_dist_end":0.31398,"object_to_goal_dist_start":0.31398,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1107.0,"raw_peak_contact_force":129.09753,"subtask_id":"place_at_goal","tcp_end":[0.59041,0.17679,0.32078],"tcp_start":[0.59044,0.17626,0.29378],"tcp_to_object_dist_end":0.36406,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":377.0,"n_steps_budget":600.0,"object_pos_end":[0.49875,-0.01623,0.02602],"object_pos_start":[0.49875,-0.01623,0.02602],"object_to_goal_dist_end":0.31398,"object_to_goal_dist_start":0.31398,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1508.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58809,0.18779,0.43651],"tcp_start":[0.59041,0.17679,0.32078],"tcp_to_object_dist_end":0.46702,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```