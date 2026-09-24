## Search State

- **Seed**: 4
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 12 | 0.2255 | 0.95 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 12 | 0.1540 | 0.81 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 12 | 0.1193 | 0.74 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 12 | -0.0847 | 0.52 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 12 | 0.1427 | 0.95 | ❌ rejected |

**Proposal policy**: task_score is near-perfect (0.95). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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

## Current Skill (Q=0.225) — your mutation base

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
  weight: 0.2
- id: grasp_at_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.03
  weight: 0.3
- id: lift_clearance
  anchor: object
  target_entity: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.2
- id: approach_goal
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.1
- id: place_at_goal
  target_entity: object
  weight: 0.2
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
    - 0.1
    tolerance: 0.01
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - -1.0
      align_with: world_z
      tolerance: 0.1
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
    speed:
      type: scalar
      range:
      - 0.05
      - 0.5
      default: 0.2
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_pre_grasp
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
    - 0.03
    tolerance: 0.01
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - -1.0
      align_with: world_z
      tolerance: 0.1
  parameters:
    descend_z:
      type: scalar
      range:
      - 0.02
      - 0.05
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
    lateral_offset_x:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: add
    lateral_offset_y:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: add
    speed:
      type: scalar
      range:
      - 0.05
      - 0.5
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: grasp_at_object
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
    - 0.03
    tolerance: 0.02
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - -1.0
      align_with: world_z
      tolerance: 0.1
  guards:
  - id: grasp_guard
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.5
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: repeat
  subtask_id: grasp_at_object
- id: lift
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.2
    tolerance: 0.02
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - -1.0
      align_with: world_z
      tolerance: 0.1
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.1
      - 0.3
      default: 0.2
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.05
      - 0.4
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: lifted_guard
    when: after_phase
    predicate: object_lifted
    threshold: 0.02
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: repeat
  subtask_id: lift_clearance
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
    tolerance: 0.01
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - -1.0
      align_with: world_z
      tolerance: 0.1
  parameters:
    approach_goal_height:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_goal
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
    tolerance: 0.01
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - -1.0
      align_with: world_z
      tolerance: 0.1
  parameters:
    place_z_offset:
      type: scalar
      range:
      - 0.0
      - 0.04
      default: 0.02
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: place_at_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.03], tolerance=0.01
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - descend_z: status=consumed; consumers=target.offset.z (replace)
    - lateral_offset_x: status=consumed; consumers=target.offset.x (add)
    - lateral_offset_y: status=consumed; consumers=target.offset.y (add)
    - speed: status=consumed; consumers=generator.speed (replace)
- **grasp** (`grasp`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.03], tolerance=0.02
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings: none
  - guards:
    - id=grasp_guard, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.5
  - retries: max_attempts=2, strategy=repeat
- **lift** (`lift`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.2], tolerance=0.02
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=lifted_guard, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.02
  - retries: max_attempts=1, strategy=repeat
- **approach_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - approach_goal_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.02], tolerance=0.01
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - place_z_offset: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.225
- **task_score** (E): 0.946
- **fitness_score**: 0.945  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.720

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1773 |
| descend_to_grasp | 1.00 | 1.00 | 0.0763 |
| grasp | 1.00 | 1.00 | 0.0127 |
| lift | 1.00 | 1.00 | 0.1116 |
| approach_goal | 0.33 | 1.00 | 0.1585 |
| descend_to_place | 1.00 | 1.00 | 0.0759 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.520, 0.005, 0.126) | (0.526, 0.005, 0.030)→(0.526, 0.005, 0.026) | 0.246→0.249 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.520, 0.005, 0.126)→(0.535, 0.003, 0.052) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.535, 0.003, 0.052)→(0.527, 0.003, 0.042) | (0.526, 0.005, 0.026)→(0.526, 0.004, 0.025) | 0.249→0.251 | 1.00 / 43.000 | 0.208 | 0.282 |
| lift | lift | 1.00 / step_budget | (0.527, 0.003, 0.042)→(0.522, 0.004, 0.153) | (0.526, 0.004, 0.025)→(0.529, 0.004, 0.134) | 0.251→0.213 | 1.00 / 38.667 | 13.908 | 0.644 |
| approach_goal | approach | 0.33 / step_budget | (0.522, 0.004, 0.153)→(0.581, 0.118, 0.230) | (0.529, 0.004, 0.134)→(0.587, 0.119, 0.204) | 0.213→0.081 | 1.00 / 39.000 | 0.090 | 0.147 |
| descend_to_place | descend | 1.00 / step_budget | (0.581, 0.118, 0.230)→(0.606, 0.169, 0.203) | (0.587, 0.119, 0.204)→(0.609, 0.170, 0.173) | 0.081→0.014 | 1.00 / 30.667 | 0.094 | 0.199 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.569
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 1.000
- phase_score: 0.593
- phase_breakdown.approach_goal_score: 0.404
- phase_breakdown.place_at_goal_score: 0.585
- phase_breakdown.grasp_at_object_score: 0.666
- phase_breakdown.reach_pre_grasp_score: 0.426
- phase_breakdown.lift_clearance_score: 0.750
- grasp_place_fitness: 0.975

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.975
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.253
- **K-run variance**: 0.0016
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.355


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.29,"average_solve_count":100.0,"average_success_count":100.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_height":0.13238,"approach_goal.speed":0.23998,"approach_object.approach_height":0.10175,"approach_object.speed":0.21222,"descend_to_grasp.descend_z":0.02012,"descend_to_grasp.lateral_offset_x":0.01999,"descend_to_grasp.lateral_offset_y":-0.00651,"descend_to_grasp.speed":0.42238,"descend_to_place.place_z_offset":0.03282,"descend_to_place.speed":0.11826,"lift.lift_height":0.12599,"lift.speed":0.11339},"optimized_scores":{"best_composite_score":0.25304,"best_fitness_score":0.97304,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":109.0,"contact_point_centroid":[0.54049,-0.00448,-0.00192],"force_p95":0.48944,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.69543,"mean_force":0.09855,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.54588,-0.00468,0.04341]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6000.0,"contact_point_centroid":[0.54217,0.01514,0.08693],"force_p95":0.08654,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.42799,"mean_force":0.05467,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.54215,-0.004,0.08497]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5721.0,"contact_point_centroid":[0.54144,-0.02321,0.08794],"force_p95":0.09016,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35307,"mean_force":0.05422,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.54214,-0.00398,0.08573]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54421,0.00061,-0.0025],"force_p95":0.24726,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.30316,"mean_force":0.15838,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.54883,-0.00471,0.04242]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5948.0,"contact_point_centroid":[0.62685,0.15248,0.23954],"force_p95":0.08284,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19978,"mean_force":0.05041,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.6282,0.13379,0.23921]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4473.0,"contact_point_centroid":[0.62683,0.11517,0.23715],"force_p95":0.10136,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18871,"mean_force":0.06794,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62852,0.13427,0.23868]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17288.0,"contact_point_centroid":[0.57549,0.03607,0.19565],"force_p95":0.08476,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17345,"mean_force":0.05674,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5763,0.05523,0.19437]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20343.0,"contact_point_centroid":[0.57685,0.07509,0.19692],"force_p95":0.07634,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16509,"mean_force":0.04887,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.57687,0.05612,0.19537]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4617.0,"contact_point_centroid":[0.54753,-0.02395,0.04289],"force_p95":0.0886,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14074,"mean_force":0.04622,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.5476,-0.00471,0.04091]},{"body_a":"world","body_b":"grasp_target","contact_count":1908.0,"contact_point_centroid":[0.54431,0.00113,-0.00193],"force_p95":0.13338,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12288,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51734,0.00049,0.2181]},{"body_a":"world","body_b":"grasp_target","contact_count":1212.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.54508,-0.00177,0.09351]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5307.0,"contact_point_centroid":[0.54768,0.01507,0.04265],"force_p95":0.09016,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09384,"mean_force":0.04497,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.54762,-0.00471,0.04094]}],"total_contact_groups":12},"final_pose_error":0.00997,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.64422,0.15367,0.19031],"final_tcp_position":[0.64085,0.1524,0.21933],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":0.69543,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":478.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1908.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.53697,0.00099,0.13826],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11248,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":303.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1212.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_at_object","tcp_end":[0.55602,-0.00462,0.0514],"tcp_start":[0.53697,0.00099,0.13826],"tcp_to_object_dist_end":0.02854,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54402,-0.00305,0.02422],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25407,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.22606,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11724.0,"raw_peak_contact_force":0.30316,"subtask_id":"grasp_at_object","tcp_end":[0.54757,-0.00471,0.04088],"tcp_start":[0.55602,-0.00462,0.0514],"tcp_to_object_dist_end":0.01712,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":300.0,"n_steps_budget":630.0,"object_pos_end":[0.5438,-0.00227,0.1128],"object_pos_start":[0.54402,-0.00305,0.02422],"object_to_goal_dist_end":0.20646,"object_to_goal_dist_start":0.25407,"object_z_max":0.11253,"peak_contact_force":0.07934,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":11830.0,"raw_peak_contact_force":0.69543,"subtask_id":"lift_clearance","tcp_end":[0.54044,-0.00328,0.13077],"tcp_start":[0.54757,-0.00471,0.04088],"tcp_to_object_dist_end":0.01832,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.62403,0.11575,0.23764],"object_pos_start":[0.5438,-0.00227,0.1128],"object_to_goal_dist_end":0.06719,"object_to_goal_dist_start":0.20646,"object_z_max":0.23748,"peak_contact_force":0.10291,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":37631.0,"raw_peak_contact_force":0.17345,"subtask_id":"approach_goal","tcp_end":[0.61674,0.11494,0.26446],"tcp_start":[0.54044,-0.00328,0.13077],"tcp_to_object_dist_end":0.02781,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":33.0,"n_steps":295.0,"n_steps_budget":1000.0,"object_pos_end":[0.64422,0.15367,0.19031],"object_pos_start":[0.62403,0.11575,0.23764],"object_to_goal_dist_end":0.00563,"object_to_goal_dist_start":0.06719,"object_z_max":0.23772,"peak_contact_force":0.09836,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10421.0,"raw_peak_contact_force":0.19978,"subtask_id":"place_at_goal","tcp_end":[0.64085,0.1524,0.21933],"tcp_start":[0.61674,0.11494,0.26446],"tcp_to_object_dist_end":0.02925,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.9292,"average_solve_count":113.0,"average_success_count":113.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_height":0.09423,"approach_goal.speed":0.13437,"approach_object.approach_height":0.05065,"approach_object.speed":0.24691,"descend_to_grasp.descend_z":0.02075,"descend_to_grasp.lateral_offset_x":0.01536,"descend_to_grasp.lateral_offset_y":-0.00422,"descend_to_grasp.speed":0.24145,"descend_to_place.place_z_offset":0.0239,"descend_to_place.speed":0.14291,"lift.lift_height":0.18839,"lift.speed":0.11631},"optimized_scores":{"best_composite_score":0.25476,"best_fitness_score":0.97476,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":97.0,"contact_point_centroid":[0.52697,0.02628,-0.00178],"force_p95":0.47692,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65863,"mean_force":0.09901,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52697,0.02616,0.0425]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9890.0,"contact_point_centroid":[0.52561,0.04578,0.11815],"force_p95":0.08363,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.39758,"mean_force":0.05327,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52559,0.02661,0.11623]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9905.0,"contact_point_centroid":[0.52563,0.00745,0.11822],"force_p95":0.08175,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33755,"mean_force":0.05157,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52559,0.02661,0.11634]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53051,0.0304,-0.00241],"force_p95":0.2249,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.28556,"mean_force":0.15144,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52955,0.02631,0.04178]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5329.0,"contact_point_centroid":[0.58604,0.17548,0.16216],"force_p95":0.07248,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17822,"mean_force":0.04941,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.58616,0.15634,0.16108]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5060.0,"contact_point_centroid":[0.58565,0.1372,0.16191],"force_p95":0.07593,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15474,"mean_force":0.05149,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.58618,0.15639,0.16098]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4733.0,"contact_point_centroid":[0.52843,0.00702,0.04231],"force_p95":0.08395,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14402,"mean_force":0.04518,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52835,0.02625,0.04037]},{"body_a":"world","body_b":"grasp_target","contact_count":2292.0,"contact_point_centroid":[0.5305,0.03079,-0.00194],"force_p95":0.13153,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12284,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51101,0.01421,0.19291]},{"body_a":"world","body_b":"grasp_target","contact_count":676.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52919,0.02772,0.06794]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":22710.0,"contact_point_centroid":[0.55426,0.10928,0.19299],"force_p95":0.06787,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11934,"mean_force":0.04449,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55472,0.09015,0.19069]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19992.0,"contact_point_centroid":[0.55405,0.07163,0.19324],"force_p95":0.07345,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10244,"mean_force":0.04941,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55508,0.09087,0.19072]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5219.0,"contact_point_centroid":[0.52843,0.04583,0.04213],"force_p95":0.08579,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08943,"mean_force":0.04473,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52837,0.02625,0.04039]}],"total_contact_groups":12},"final_pose_error":0.00997,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.59606,0.17196,0.10747],"final_tcp_position":[0.59422,0.17188,0.133],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":41.55849,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":574.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2292.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.5242,0.02866,0.08789],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.06223,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":169.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":676.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_at_object","tcp_end":[0.53648,0.02676,0.05007],"tcp_start":[0.5242,0.02866,0.08789],"tcp_to_object_dist_end":0.02511,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53036,0.0275,0.02455],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18673,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.20942,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11752.0,"raw_peak_contact_force":0.28556,"subtask_id":"grasp_at_object","tcp_end":[0.52833,0.02624,0.04034],"tcp_start":[0.53648,0.02676,0.05007],"tcp_to_object_dist_end":0.01596,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":495.0,"n_steps_budget":930.0,"object_pos_end":[0.53825,0.02779,0.17587],"object_pos_start":[0.53036,0.0275,0.02455],"object_to_goal_dist_end":0.17702,"object_to_goal_dist_start":0.18673,"object_z_max":0.1756,"peak_contact_force":41.55849,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":19892.0,"raw_peak_contact_force":0.65863,"subtask_id":"lift_clearance","tcp_end":[0.52683,0.02719,0.19343],"tcp_start":[0.52833,0.02624,0.04034],"tcp_to_object_dist_end":0.02096,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5838,0.1418,0.16853],"object_pos_start":[0.53825,0.02779,0.17587],"object_to_goal_dist_end":0.07294,"object_to_goal_dist_start":0.17702,"object_z_max":0.17609,"peak_contact_force":0.07092,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":42702.0,"raw_peak_contact_force":0.11934,"subtask_id":"approach_goal","tcp_end":[0.58021,0.14166,0.19268],"tcp_start":[0.52683,0.02719,0.19343],"tcp_to_object_dist_end":0.02441,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":253.0,"n_steps_budget":1000.0,"object_pos_end":[0.59606,0.17196,0.10747],"object_pos_start":[0.5838,0.1418,0.16853],"object_to_goal_dist_end":0.00861,"object_to_goal_dist_start":0.07294,"object_z_max":0.16853,"peak_contact_force":0.06966,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10389.0,"raw_peak_contact_force":0.17822,"subtask_id":"place_at_goal","tcp_end":[0.59422,0.17188,0.133],"tcp_start":[0.58021,0.14166,0.19268],"tcp_to_object_dist_end":0.02559,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.30303,"average_solve_count":99.0,"average_success_count":99.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_height":0.07421,"approach_goal.speed":0.19039,"approach_object.approach_height":0.11367,"approach_object.speed":0.25351,"descend_to_grasp.descend_z":0.02022,"descend_to_grasp.lateral_offset_x":0.01561,"descend_to_grasp.lateral_offset_y":0.00375,"descend_to_grasp.speed":0.274,"descend_to_place.place_z_offset":0.01864,"descend_to_place.speed":0.16865,"lift.lift_height":0.13035,"lift.speed":0.26978},"optimized_scores":{"best_composite_score":0.16868,"best_fitness_score":0.88868,"best_task_score":0.83876},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":92.0,"contact_point_centroid":[0.50072,-0.0121,-0.0017],"force_p95":0.46093,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5766,"mean_force":0.09028,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.50339,-0.01212,0.04654]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4828.0,"contact_point_centroid":[0.50165,0.0067,0.0906],"force_p95":0.09198,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35573,"mean_force":0.06106,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.50078,-0.01252,0.08932]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5893.0,"contact_point_centroid":[0.50085,-0.0315,0.09061],"force_p95":0.08494,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35437,"mean_force":0.05211,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.50079,-0.01251,0.08859]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50377,-0.01539,-0.00231],"force_p95":0.20123,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25814,"mean_force":0.14463,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50589,-0.0121,0.04579]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11859.0,"contact_point_centroid":[0.56438,0.15793,0.24007],"force_p95":0.11815,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21912,"mean_force":0.07935,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.56198,0.13948,0.24238]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11014.0,"contact_point_centroid":[0.56513,0.12118,0.24051],"force_p95":0.12722,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21421,"mean_force":0.08537,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.56208,0.13969,0.24246]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4054.0,"contact_point_centroid":[0.50565,0.00713,0.04615],"force_p95":0.08678,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16424,"mean_force":0.05205,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50475,-0.01209,0.04451]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19904.0,"contact_point_centroid":[0.5218,0.02513,0.18463],"force_p95":0.076,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14963,"mean_force":0.05009,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52154,0.04415,0.18353]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18010.0,"contact_point_centroid":[0.52309,0.06544,0.18612],"force_p95":0.08286,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14632,"mean_force":0.05465,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52247,0.04628,0.18548]},{"body_a":"world","body_b":"grasp_target","contact_count":1620.0,"contact_point_centroid":[0.50382,-0.01567,-0.00192],"force_p95":0.13462,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12293,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49894,-0.00691,0.22627]},{"body_a":"world","body_b":"grasp_target","contact_count":1312.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50483,-0.01316,0.10219]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5152.0,"contact_point_centroid":[0.50484,-0.0314,0.04634],"force_p95":0.08145,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08369,"mean_force":0.04403,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50476,-0.01209,0.04452]}],"total_contact_groups":12},"final_pose_error":0.01049,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.58803,0.18417,0.22197],"final_tcp_position":[0.58275,0.18387,0.25782],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":0.5766,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":406.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1620.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.49976,-0.01415,0.15268],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12673,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":328.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1312.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_at_object","tcp_end":[0.51266,-0.01215,0.05348],"tcp_start":[0.49976,-0.01415,0.15268],"tcp_to_object_dist_end":0.02906,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50364,-0.01313,0.02488],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31145,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.1896,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11006.0,"raw_peak_contact_force":0.25814,"subtask_id":"grasp_at_object","tcp_end":[0.50472,-0.01209,0.04448],"tcp_start":[0.51266,-0.01215,0.05348],"tcp_to_object_dist_end":0.01965,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":284.0,"n_steps_budget":600.0,"object_pos_end":[0.50633,-0.01376,0.1144],"object_pos_start":[0.50364,-0.01313,0.02488],"object_to_goal_dist_end":0.25467,"object_to_goal_dist_start":0.31145,"object_z_max":0.11412,"peak_contact_force":0.0852,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":10813.0,"raw_peak_contact_force":0.5766,"subtask_id":"lift_clearance","tcp_end":[0.5001,-0.01294,0.13575],"tcp_start":[0.50472,-0.01209,0.04448],"tcp_to_object_dist_end":0.02225,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":35.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55355,0.09843,0.20619],"object_pos_start":[0.50633,-0.01376,0.1144],"object_to_goal_dist_end":0.1039,"object_to_goal_dist_start":0.25467,"object_z_max":0.20613,"peak_contact_force":0.09537,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":37914.0,"raw_peak_contact_force":0.14963,"subtask_id":"approach_goal","tcp_end":[0.54555,0.09867,0.2336],"tcp_start":[0.5001,-0.01294,0.13575],"tcp_to_object_dist_end":0.02856,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":993.0,"n_steps_budget":1000.0,"object_pos_end":[0.58803,0.18417,0.22197],"object_pos_start":[0.55355,0.09843,0.20619],"object_to_goal_dist_end":0.02638,"object_to_goal_dist_start":0.1039,"object_z_max":0.22197,"peak_contact_force":0.11516,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":22873.0,"raw_peak_contact_force":0.21912,"subtask_id":"place_at_goal","tcp_end":[0.58275,0.18387,0.25782],"tcp_start":[0.54555,0.09867,0.2336],"tcp_to_object_dist_end":0.03624,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```