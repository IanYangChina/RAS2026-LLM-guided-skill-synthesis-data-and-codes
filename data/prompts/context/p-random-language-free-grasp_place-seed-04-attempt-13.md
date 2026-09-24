## Search State

- **Seed**: 4
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 13 | -0.0487 | 0.50 | ✅ accepted |
| 12 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 13 | -0.0521 | 0.49 | ✅ accepted |
| 11 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.0573 | 0.33 | ✅ accepted |
| 10 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.1808 | 0.21 | ❌ rejected |
| 9 | approach → contact → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 8 | -0.2250 | 0.20 | ❌ rejected |

**Proposal policy**: task_score is 0.50 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.049) — your mutation base

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

- **Composite score**: -0.049
- **task_score** (E): 0.496
- **fitness_score**: 0.721  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.770

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1249 |
| descend_to_grasp | 1.00 | 1.00 | 0.1344 |
| grasp_object | 0.00 | 1.00 | 0.0000 |
| lift_object | 1.00 | 1.00 | 0.1213 |
| transport_to_goal | 1.00 | 1.00 | 0.2443 |
| descend_to_place | 1.00 | 1.00 | 0.0680 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.518, 0.004, 0.180) | (0.526, 0.005, 0.030)→(0.526, 0.005, 0.026) | 0.246→0.249 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.518, 0.004, 0.180)→(0.521, 0.005, 0.045) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_object | grasp | 0.00 / guard_failure | (0.516, 0.005, 0.039)→(0.516, 0.005, 0.039) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 44.000 | 0.137 | 0.179 |
| lift_object | lift | 1.00 / step_budget | (0.516, 0.005, 0.039)→(0.512, 0.005, 0.160) | (0.526, 0.005, 0.026)→(0.528, 0.005, 0.143) | 0.249→0.212 | 1.00 / 28.333 | 0.100 | 0.541 |
| transport_to_goal | approach | 1.00 / step_budget | (0.512, 0.005, 0.160)→(0.605, 0.165, 0.303) | (0.528, 0.005, 0.143)→(0.591, 0.129, 0.075) | 0.212→0.173 | 1.00 / 14.333 | 3249.684 | 1.640 |
| descend_to_place | descend | 1.00 / step_budget | (0.605, 0.165, 0.303)→(0.608, 0.171, 0.235) | (0.591, 0.129, 0.075)→(0.591, 0.131, 0.051) | 0.173→0.149 | 1.00 / 13.667 | 3249.680 | 0.180 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.290
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.483
- phase_breakdown.place_at_goal_score: 0.417
- phase_breakdown.approach_object_score: 0.637
- grasp_place_fitness: 0.973

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.973
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: -0.146
- **K-run variance**: 0.0323
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.379


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.04,"average_solve_count":100.0,"average_success_count":100.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.16393,"approach_object.approach_speed":0.45293,"descend_to_grasp.descend_speed":0.27991,"descend_to_grasp.grasp_z_offset":5e-05,"descend_to_place.place_height":0.04102,"descend_to_place.place_speed":0.18013,"grasp_object.grasp_force_threshold":0.35819,"grasp_object.grasp_retry_x":0.01164,"grasp_object.grasp_retry_y":0.01102,"lift_object.lift_height":0.12468,"lift_object.lift_speed":0.34194,"transport_to_goal.transport_height":0.10926,"transport_to_goal.transport_speed":0.29596},"optimized_scores":{"best_composite_score":-0.14609,"best_fitness_score":0.62391,"best_task_score":0.30035},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":756.0,"contact_point_centroid":[0.62244,0.12259,-0.00355],"force_p95":0.70572,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.21796,"mean_force":0.18642,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.62461,0.12987,0.26435]},{"body_a":"world","body_b":"grasp_target","contact_count":73.0,"contact_point_centroid":[0.54117,0.00089,-0.00135],"force_p95":0.549,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.56826,"mean_force":0.13096,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.53194,0.00089,0.03968]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4168.0,"contact_point_centroid":[0.565,0.06221,0.18161],"force_p95":0.13365,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3505,"mean_force":0.08618,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55928,0.04382,0.18105]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5564.0,"contact_point_centroid":[0.5308,0.01998,0.08937],"force_p95":0.1034,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33188,"mean_force":0.06443,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52948,0.00085,0.08704]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3608.0,"contact_point_centroid":[0.56348,0.02347,0.18055],"force_p95":0.15828,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32182,"mean_force":0.0965,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.558,0.04203,0.17943]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6312.0,"contact_point_centroid":[0.53077,-0.01809,0.08748],"force_p95":0.09758,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31649,"mean_force":0.05805,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52948,0.00085,0.08578]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.5443,0.00116,-0.00202],"force_p95":0.12792,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1444,"mean_force":0.12457,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.53363,0.00093,0.03886]},{"body_a":"world","body_b":"grasp_target","contact_count":760.0,"contact_point_centroid":[0.54431,0.00113,-0.00183],"force_p95":0.13759,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12327,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51526,0.00042,0.25574]},{"body_a":"world","body_b":"grasp_target","contact_count":1124.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53462,0.00093,0.12741]},{"body_a":"world","body_b":"grasp_target","contact_count":264.0,"contact_point_centroid":[0.62237,0.1226,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.64108,0.15193,0.26931]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5292.0,"contact_point_centroid":[0.53308,0.02021,0.04009],"force_p95":0.07423,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09502,"mean_force":0.0497,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.53327,0.00092,0.03846]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6432.0,"contact_point_centroid":[0.53262,-0.01815,0.03971],"force_p95":0.063,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08828,"mean_force":0.04102,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.53326,0.00092,0.03846]},{"body_a":"left_finger","body_b":"right_finger","contact_count":614.0,"contact_point_centroid":[0.62863,0.13484,0.27147],"force_p95":0.01293,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01621,"mean_force":0.01081,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.62842,0.13483,0.26918]},{"body_a":"left_finger","body_b":"right_finger","contact_count":279.0,"contact_point_centroid":[0.6416,0.15194,0.27166],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01099,"mean_force":0.01054,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.64108,0.15193,0.26934]}],"total_contact_groups":14},"final_pose_error":0.01955,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.62237,0.1226,0.01602],"final_tcp_position":[0.64245,0.15389,0.2505],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":9748.76408,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":191.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":760.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.5326,0.00086,0.20962],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.18398,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":281.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1124.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53845,0.00101,0.04493],"tcp_start":[0.5326,0.00086,0.20962],"tcp_to_object_dist_end":0.01979,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54423,0.00114,0.02593],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25021,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12783,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13528.0,"raw_peak_contact_force":0.1444,"tcp_end":[0.53325,0.00092,0.03844],"tcp_start":[0.53325,0.00092,0.03844],"tcp_to_object_dist_end":0.01665,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":338.0,"n_steps_budget":600.0,"object_pos_end":[0.54528,0.00105,0.12643],"object_pos_start":[0.54423,0.00114,0.02593],"object_to_goal_dist_end":0.19828,"object_to_goal_dist_start":0.25021,"object_z_max":0.12618,"peak_contact_force":0.10593,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":11949.0,"raw_peak_contact_force":0.56826,"tcp_end":[0.52942,0.00086,0.14366],"tcp_start":[0.53325,0.00092,0.03844],"tcp_to_object_dist_end":0.02342,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":652.0,"n_steps_budget":1000.0,"object_pos_end":[0.62237,0.1226,0.01602],"object_pos_start":[0.54528,0.00105,0.12643],"object_to_goal_dist_end":0.18042,"object_to_goal_dist_start":0.19828,"object_z_max":0.19375,"peak_contact_force":0.12259,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9146.0,"raw_peak_contact_force":2.21796,"subtask_id":"place_at_goal","tcp_end":[0.63999,0.15009,0.28395],"tcp_start":[0.52942,0.00086,0.14366],"tcp_to_object_dist_end":0.26991,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":66.0,"n_steps_budget":1000.0,"object_pos_end":[0.62237,0.1226,0.01602],"object_pos_start":[0.62237,0.1226,0.01602],"object_to_goal_dist_end":0.18042,"object_to_goal_dist_start":0.18042,"object_z_max":0.01602,"peak_contact_force":9748.76408,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":543.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_at_goal","tcp_end":[0.64245,0.15389,0.2505],"tcp_start":[0.63999,0.15009,0.28395],"tcp_to_object_dist_end":0.23741,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.35345,"average_solve_count":116.0,"average_success_count":116.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.12336,"approach_object.approach_speed":0.29782,"descend_to_grasp.descend_speed":0.25095,"descend_to_grasp.grasp_z_offset":0.00023,"descend_to_place.place_height":0.02469,"descend_to_place.place_speed":0.2852,"grasp_object.grasp_force_threshold":0.27327,"grasp_object.grasp_retry_x":-0.01087,"grasp_object.grasp_retry_y":0.01377,"lift_object.lift_height":0.1851,"lift_object.lift_speed":0.10711,"transport_to_goal.transport_height":0.12629,"transport_to_goal.transport_speed":0.44339},"optimized_scores":{"best_composite_score":0.20337,"best_fitness_score":0.97337,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":80.0,"contact_point_centroid":[0.52809,0.02919,-0.00147],"force_p95":0.45852,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.53874,"mean_force":0.11155,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.5187,0.02924,0.04018]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5225.0,"contact_point_centroid":[0.56127,0.08459,0.21431],"force_p95":0.11614,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37581,"mean_force":0.0767,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55676,0.10336,0.21348]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8931.0,"contact_point_centroid":[0.51789,0.04811,0.11168],"force_p95":0.10541,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31822,"mean_force":0.06371,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51622,0.02908,0.10966]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9014.0,"contact_point_centroid":[0.51816,0.01015,0.11391],"force_p95":0.10173,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30414,"mean_force":0.06289,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51622,0.02908,0.11203]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1671.0,"contact_point_centroid":[0.595,0.18762,0.18497],"force_p95":0.14835,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29422,"mean_force":0.08622,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59321,0.16944,0.18707]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1474.0,"contact_point_centroid":[0.59563,0.15042,0.18833],"force_p95":0.17111,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2912,"mean_force":0.10089,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59299,0.16902,0.19073]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5503.0,"contact_point_centroid":[0.5598,0.11874,0.21393],"force_p95":0.1055,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22292,"mean_force":0.07328,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55488,0.1001,0.21286]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.53055,0.03059,-0.00214],"force_p95":0.15631,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2208,"mean_force":0.133,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52033,0.02936,0.0392]},{"body_a":"world","body_b":"grasp_target","contact_count":976.0,"contact_point_centroid":[0.5305,0.03079,-0.00187],"force_p95":0.13691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12313,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51043,0.0124,0.23624]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5798.0,"contact_point_centroid":[0.52017,0.01016,0.04075],"force_p95":0.0728,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13352,"mean_force":0.04496,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.51997,0.02933,0.03882]},{"body_a":"world","body_b":"grasp_target","contact_count":892.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52292,0.02764,0.10808]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6000.0,"contact_point_centroid":[0.52015,0.04858,0.04069],"force_p95":0.0733,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07798,"mean_force":0.04489,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.51998,0.02933,0.03882]}],"total_contact_groups":12},"final_pose_error":0.01998,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.59569,0.1729,0.11972],"final_tcp_position":[0.59546,0.17369,0.15118],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":0.53874,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":245.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":976.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.52259,0.02575,0.17051],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1448,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":223.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":892.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.52505,0.02965,0.045],"tcp_start":[0.52259,0.02575,0.17051],"tcp_to_object_dist_end":0.01978,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53047,0.0297,0.02558],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18445,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.15014,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13602.0,"raw_peak_contact_force":0.2208,"tcp_end":[0.51996,0.02933,0.0388],"tcp_start":[0.51996,0.02933,0.0388],"tcp_to_object_dist_end":0.01689,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":538.0,"n_steps_budget":1000.0,"object_pos_end":[0.53255,0.02944,0.18515],"object_pos_start":[0.53047,0.02967,0.0256],"object_to_goal_dist_end":0.18149,"object_to_goal_dist_start":0.18446,"object_z_max":0.18489,"peak_contact_force":0.10058,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":18025.0,"raw_peak_contact_force":0.53874,"tcp_end":[0.51664,0.0291,0.20422],"tcp_start":[0.51996,0.02933,0.0388],"tcp_to_object_dist_end":0.02483,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":406.0,"n_steps_budget":1000.0,"object_pos_end":[0.5965,0.16524,0.19441],"object_pos_start":[0.53255,0.02944,0.18515],"object_to_goal_dist_end":0.08749,"object_to_goal_dist_start":0.18149,"object_z_max":0.19439,"peak_contact_force":0.11387,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":10728.0,"raw_peak_contact_force":0.37581,"subtask_id":"place_at_goal","tcp_end":[0.59149,0.16499,0.22415],"tcp_start":[0.51664,0.0291,0.20422],"tcp_to_object_dist_end":0.03016,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":133.0,"n_steps_budget":1000.0,"object_pos_end":[0.59569,0.1729,0.11972],"object_pos_start":[0.5965,0.16524,0.19441],"object_to_goal_dist_end":0.0142,"object_to_goal_dist_start":0.08749,"object_z_max":0.19441,"peak_contact_force":0.15447,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3145.0,"raw_peak_contact_force":0.29422,"subtask_id":"place_at_goal","tcp_end":[0.59546,0.17369,0.15118],"tcp_start":[0.59149,0.16499,0.22415],"tcp_to_object_dist_end":0.03147,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.09009,"average_solve_count":111.0,"average_success_count":111.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.10918,"approach_object.approach_speed":0.1374,"descend_to_grasp.descend_speed":0.41237,"descend_to_grasp.grasp_z_offset":0.00077,"descend_to_place.place_height":0.03681,"descend_to_place.place_speed":0.22265,"grasp_object.grasp_force_threshold":0.37553,"grasp_object.grasp_retry_x":-0.0131,"grasp_object.grasp_retry_y":-0.00694,"lift_object.lift_height":0.11274,"lift_object.lift_speed":0.27241,"transport_to_goal.transport_height":0.17043,"transport_to_goal.transport_speed":0.29278},"optimized_scores":{"best_composite_score":-0.20329,"best_fitness_score":0.56671,"best_task_score":0.18759},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1759.0,"contact_point_centroid":[0.55383,0.09779,-0.00273],"force_p95":0.2747,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32487,"mean_force":0.1519,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.56022,0.13394,0.33665]},{"body_a":"world","body_b":"grasp_target","contact_count":75.0,"contact_point_centroid":[0.50086,-0.01519,-0.00136],"force_p95":0.49779,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.51477,"mean_force":0.11908,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49306,-0.01509,0.04153]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4384.0,"contact_point_centroid":[0.5121,0.04259,0.18508],"force_p95":0.12018,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34925,"mean_force":0.08137,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50681,0.02412,0.18406]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5824.0,"contact_point_centroid":[0.49132,-0.03415,0.08691],"force_p95":0.08263,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31094,"mean_force":0.05478,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49076,-0.01505,0.08505]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5413.0,"contact_point_centroid":[0.49133,0.00411,0.0864],"force_p95":0.0858,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31047,"mean_force":0.05782,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49078,-0.01505,0.08408]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3773.0,"contact_point_centroid":[0.51036,0.00215,0.18107],"force_p95":0.14633,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25756,"mean_force":0.09066,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50527,0.02081,0.17956]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.50382,-0.01559,-0.00205],"force_p95":0.13594,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17065,"mean_force":0.12666,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49464,-0.01511,0.04057]},{"body_a":"world","body_b":"grasp_target","contact_count":1044.0,"contact_point_centroid":[0.50382,-0.01567,-0.00187],"force_p95":0.1365,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12309,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49952,-0.00634,0.23058]},{"body_a":"world","body_b":"grasp_target","contact_count":836.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.49877,-0.01415,0.10236]},{"body_a":"world","body_b":"grasp_target","contact_count":668.0,"contact_point_centroid":[0.55373,0.09776,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.5839,0.18245,0.35446]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5832.0,"contact_point_centroid":[0.49446,0.00408,0.04212],"force_p95":0.06926,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11184,"mean_force":0.04498,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49429,-0.01511,0.04021]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5903.0,"contact_point_centroid":[0.49449,-0.0343,0.0421],"force_p95":0.06955,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08891,"mean_force":0.04502,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.4943,-0.01511,0.04022]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1705.0,"contact_point_centroid":[0.56256,0.13809,0.34473],"force_p95":0.01172,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01621,"mean_force":0.01061,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.56227,0.13809,0.34243]},{"body_a":"left_finger","body_b":"right_finger","contact_count":710.0,"contact_point_centroid":[0.58421,0.18245,0.35677],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01277,"mean_force":0.01048,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.5839,0.18244,0.3546]}],"total_contact_groups":14},"final_pose_error":0.01946,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.55373,0.09776,0.01602],"final_tcp_position":[0.58477,0.18511,0.30413],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":9748.81443,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":262.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1044.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.5001,-0.01319,0.15848],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13254,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":209.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":836.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.49919,-0.01516,0.04582],"tcp_start":[0.5001,-0.01319,0.15848],"tcp_to_object_dist_end":0.02034,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50375,-0.01525,0.02584],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.3121,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13388,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13539.0,"raw_peak_contact_force":0.17065,"tcp_end":[0.49428,-0.01511,0.0402],"tcp_start":[0.49428,-0.01511,0.0402],"tcp_to_object_dist_end":0.0172,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":289.0,"n_steps_budget":600.0,"object_pos_end":[0.50536,-0.01505,0.11593],"object_pos_start":[0.50375,-0.01524,0.02585],"object_to_goal_dist_end":0.25521,"object_to_goal_dist_start":0.31209,"object_z_max":0.11565,"peak_contact_force":0.09461,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":11312.0,"raw_peak_contact_force":0.51477,"tcp_end":[0.49056,-0.01504,0.1333],"tcp_start":[0.49428,-0.01511,0.0402],"tcp_to_object_dist_end":0.02283,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":896.0,"n_steps_budget":1000.0,"object_pos_end":[0.55373,0.09776,0.01602],"object_pos_start":[0.50536,-0.01505,0.11593],"object_to_goal_dist_end":0.25103,"object_to_goal_dist_start":0.25521,"object_z_max":0.21196,"peak_contact_force":9748.81443,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":11621.0,"raw_peak_contact_force":2.32487,"subtask_id":"place_at_goal","tcp_end":[0.58297,0.17996,0.40067],"tcp_start":[0.49056,-0.01504,0.1333],"tcp_to_object_dist_end":0.39442,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":167.0,"n_steps_budget":1000.0,"object_pos_end":[0.55373,0.09776,0.01602],"object_pos_start":[0.55373,0.09776,0.01602],"object_to_goal_dist_end":0.25103,"object_to_goal_dist_start":0.25103,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1378.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_at_goal","tcp_end":[0.58477,0.18511,0.30413],"tcp_start":[0.58297,0.17996,0.40067],"tcp_to_object_dist_end":0.30266,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```