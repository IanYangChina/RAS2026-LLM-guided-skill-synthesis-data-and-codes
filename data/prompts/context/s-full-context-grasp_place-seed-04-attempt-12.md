## Search State

- **Seed**: 4
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 12 | -0.0000 | 0.50 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 12 | 0.1406 | 0.94 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 12 | 0.2255 | 0.95 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 12 | 0.1540 | 0.81 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 12 | 0.1193 | 0.74 | ❌ rejected |

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

## Current Skill (Q=-0.000) — your mutation base

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

- **Composite score**: -0.000
- **task_score** (E): 0.502
- **fitness_score**: 0.720  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.720

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1558 |
| descend_to_grasp | 1.00 | 1.00 | 0.0949 |
| grasp | 1.00 | 1.00 | 0.0127 |
| lift | 1.00 | 1.00 | 0.1210 |
| approach_goal | 0.67 | 0.67 | 0.1650 |
| descend_to_place | 1.00 | 1.00 | 0.0704 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.520, 0.005, 0.148) | (0.526, 0.005, 0.030)→(0.526, 0.005, 0.026) | 0.246→0.249 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.520, 0.005, 0.148)→(0.533, 0.007, 0.054) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.533, 0.007, 0.054)→(0.525, 0.007, 0.044) | (0.526, 0.005, 0.026)→(0.526, 0.007, 0.025) | 0.249→0.249 | 1.00 / 42.667 | 0.204 | 0.259 |
| lift | lift | 1.00 / step_budget | (0.525, 0.007, 0.044)→(0.522, 0.007, 0.165) | (0.526, 0.007, 0.025)→(0.534, 0.006, 0.143) | 0.249→0.199 | 1.00 / 30.333 | 0.105 | 0.573 |
| approach_goal | approach | 0.67 / step_budget | (0.522, 0.007, 0.165)→(0.588, 0.130, 0.243) | (0.534, 0.006, 0.143)→(0.594, 0.131, 0.183) | 0.199→0.060 | 0.67 / 14.000 | 0.079 | 0.202 |
| descend_to_place | descend | 1.00 / step_budget | (0.588, 0.130, 0.243)→(0.606, 0.170, 0.217) | (0.594, 0.131, 0.183)→(0.609, 0.151, 0.051) | 0.060→0.145 | 1.00 / 12.333 | 0.123 | 1.487 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.249
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 1.000
- phase_score: 0.617
- phase_breakdown.approach_goal_score: 0.527
- phase_breakdown.place_at_goal_score: 0.408
- phase_breakdown.grasp_at_object_score: 0.708
- phase_breakdown.reach_pre_grasp_score: 0.856
- phase_breakdown.lift_clearance_score: 0.498
- grasp_place_fitness: 0.971

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.971
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: -0.095
- **K-run variance**: 0.0321
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.331


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.49495,"average_solve_count":99.0,"average_success_count":99.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_height":0.12595,"approach_goal.speed":0.32464,"approach_object.approach_height":0.11266,"approach_object.speed":0.28593,"descend_to_grasp.descend_z":0.02278,"descend_to_grasp.lateral_offset_x":0.0156,"descend_to_grasp.lateral_offset_y":0.00133,"descend_to_grasp.speed":0.1877,"descend_to_place.place_z_offset":0.03007,"descend_to_place.speed":0.20295,"lift.lift_height":0.2027,"lift.speed":0.22803},"optimized_scores":{"best_composite_score":-0.09465,"best_fitness_score":0.62535,"best_task_score":0.31025},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":525.0,"contact_point_centroid":[0.65434,0.16578,-0.0047],"force_p95":1.12685,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.20494,"mean_force":0.25316,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.63856,0.14891,0.25272]},{"body_a":"world","body_b":"grasp_target","contact_count":74.0,"contact_point_centroid":[0.5406,0.00221,-0.00153],"force_p95":0.488,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.58001,"mean_force":0.10833,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.54261,0.00198,0.04626]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8264.0,"contact_point_centroid":[0.54137,0.02108,0.12744],"force_p95":0.0927,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37751,"mean_force":0.06024,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.54045,0.0019,0.12554]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9695.0,"contact_point_centroid":[0.54087,-0.01709,0.12522],"force_p95":0.08462,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36119,"mean_force":0.05248,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.54044,0.0019,0.12347]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10525.0,"contact_point_centroid":[0.58477,0.04434,0.24305],"force_p95":0.12364,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22106,"mean_force":0.08449,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.58002,0.06272,0.24436]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9379.0,"contact_point_centroid":[0.58672,0.08325,0.24447],"force_p95":0.12509,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21921,"mean_force":0.0948,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.58145,0.06478,0.24576]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54429,0.00129,-0.00209],"force_p95":0.14525,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19414,"mean_force":0.12975,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.54521,0.00204,0.04619]},{"body_a":"world","body_b":"grasp_target","contact_count":1816.0,"contact_point_centroid":[0.54431,0.00113,-0.00192],"force_p95":0.1336,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1229,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51726,0.00049,0.22364]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4339.0,"contact_point_centroid":[0.54442,0.02124,0.04805],"force_p95":0.07505,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12638,"mean_force":0.04912,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.54399,0.00202,0.0447]},{"body_a":"world","body_b":"grasp_target","contact_count":1236.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.54318,0.00156,0.10111]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4936.0,"contact_point_centroid":[0.54408,-0.01712,0.04661],"force_p95":0.07032,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07245,"mean_force":0.04478,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.544,0.00202,0.04471]},{"body_a":"left_finger","body_b":"right_finger","contact_count":453.0,"contact_point_centroid":[0.63936,0.15003,0.24897],"force_p95":0.01451,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0177,"mean_force":0.01096,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.63931,0.15002,0.2467]}],"total_contact_groups":12},"final_pose_error":0.00993,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.65449,0.16829,0.01598],"final_tcp_position":[0.64197,0.15378,0.22811],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":2.20494,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":455.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1816.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.53685,0.00099,0.14918],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12338,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":309.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1236.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_at_object","tcp_end":[0.55236,0.00219,0.05511],"tcp_start":[0.53685,0.00099,0.14918],"tcp_to_object_dist_end":0.0302,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54419,0.00191,0.02565],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.24993,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.14033,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11075.0,"raw_peak_contact_force":0.19414,"subtask_id":"grasp_at_object","tcp_end":[0.54396,0.00202,0.04466],"tcp_start":[0.55236,0.00219,0.05511],"tcp_to_object_dist_end":0.01902,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":480.0,"n_steps_budget":600.0,"object_pos_end":[0.55827,0.00181,0.18653],"object_pos_start":[0.54419,0.00191,0.02565],"object_to_goal_dist_end":0.18007,"object_to_goal_dist_start":0.24993,"object_z_max":0.18628,"peak_contact_force":0.10407,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":18033.0,"raw_peak_contact_force":0.58001,"subtask_id":"lift_clearance","tcp_end":[0.54104,0.00187,0.20877],"tcp_start":[0.54396,0.00202,0.04466],"tcp_to_object_dist_end":0.02813,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.64564,0.14438,0.18154],"object_pos_start":[0.55827,0.00181,0.18653],"object_to_goal_dist_end":0.01683,"object_to_goal_dist_start":0.18007,"object_z_max":0.25293,"peak_contact_force":0.0,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":19904.0,"raw_peak_contact_force":0.22106,"subtask_id":"approach_goal","tcp_end":[0.63468,0.14164,0.29738],"tcp_start":[0.54104,0.00187,0.20877],"tcp_to_object_dist_end":0.11639,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":194.0,"n_steps_budget":1000.0,"object_pos_end":[0.65449,0.16829,0.01598],"object_pos_start":[0.64564,0.14438,0.18154],"object_to_goal_dist_end":0.17556,"object_to_goal_dist_start":0.01683,"object_z_max":0.18154,"peak_contact_force":0.12488,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":978.0,"raw_peak_contact_force":2.20494,"subtask_id":"place_at_goal","tcp_end":[0.64197,0.15378,0.22811],"tcp_start":[0.63468,0.14164,0.29738],"tcp_to_object_dist_end":0.21299,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.10101,"average_solve_count":99.0,"average_success_count":99.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_height":0.08467,"approach_goal.speed":0.24375,"approach_object.approach_height":0.08883,"approach_object.speed":0.20325,"descend_to_grasp.descend_z":0.02081,"descend_to_grasp.lateral_offset_x":0.01357,"descend_to_grasp.lateral_offset_y":-0.00268,"descend_to_grasp.speed":0.29494,"descend_to_place.place_z_offset":0.03977,"descend_to_place.speed":0.26413,"lift.lift_height":0.14001,"lift.speed":0.15126},"optimized_scores":{"best_composite_score":0.251,"best_fitness_score":0.971,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":90.0,"contact_point_centroid":[0.527,0.02703,-0.00165],"force_p95":0.49073,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.59199,"mean_force":0.09837,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52687,0.02725,0.04528]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6783.0,"contact_point_centroid":[0.52558,0.0466,0.09612],"force_p95":0.08239,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.38616,"mean_force":0.05209,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52553,0.02757,0.09392]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5591.0,"contact_point_centroid":[0.52469,0.00836,0.0949],"force_p95":0.08997,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33945,"mean_force":0.06015,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52554,0.02756,0.09314]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53051,0.03048,-0.0023],"force_p95":0.20006,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25914,"mean_force":0.14424,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52939,0.0274,0.04469]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1209.0,"contact_point_centroid":[0.59241,0.18676,0.16337],"force_p95":0.11859,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19678,"mean_force":0.08307,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.5926,0.16843,0.16684]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1008.0,"contact_point_centroid":[0.59103,0.14966,0.16403],"force_p95":0.12325,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18602,"mean_force":0.09571,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59255,0.16835,0.16709]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16697.0,"contact_point_centroid":[0.55469,0.07477,0.1604],"force_p95":0.10076,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18312,"mean_force":0.05909,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55598,0.09391,0.16001]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19260.0,"contact_point_centroid":[0.5559,0.11383,0.16094],"force_p95":0.08183,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18244,"mean_force":0.05181,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55649,0.09491,0.16032]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4219.0,"contact_point_centroid":[0.52753,0.00811,0.04547],"force_p95":0.08725,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16633,"mean_force":0.05034,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52821,0.02733,0.04329]},{"body_a":"world","body_b":"grasp_target","contact_count":1976.0,"contact_point_centroid":[0.5305,0.03079,-0.00193],"force_p95":0.13308,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12287,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51103,0.01401,0.21202]},{"body_a":"world","body_b":"grasp_target","contact_count":1012.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52887,0.02804,0.08879]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5150.0,"contact_point_centroid":[0.52828,0.04667,0.04511],"force_p95":0.08103,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08328,"mean_force":0.04424,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52822,0.02733,0.0433]}],"total_contact_groups":12},"final_pose_error":0.00987,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.59422,0.1734,0.12014],"final_tcp_position":[0.59469,0.17285,0.15208],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":0.59199,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":495.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1976.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.52422,0.0283,0.1262],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1004,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":253.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1012.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_at_object","tcp_end":[0.53638,0.02785,0.0531],"tcp_start":[0.52422,0.0283,0.1262],"tcp_to_object_dist_end":0.02787,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53039,0.02837,0.02492],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18586,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.18748,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11169.0,"raw_peak_contact_force":0.25914,"subtask_id":"grasp_at_object","tcp_end":[0.52818,0.02733,0.04325],"tcp_start":[0.53638,0.02785,0.0531],"tcp_to_object_dist_end":0.0185,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":326.0,"n_steps_budget":600.0,"object_pos_end":[0.53545,0.02868,0.12493],"object_pos_start":[0.53039,0.02837,0.02492],"object_to_goal_dist_end":0.16468,"object_to_goal_dist_start":0.18586,"object_z_max":0.12466,"peak_contact_force":0.08756,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":12464.0,"raw_peak_contact_force":0.59199,"subtask_id":"lift_clearance","tcp_end":[0.52642,0.02802,0.14545],"tcp_start":[0.52818,0.02733,0.04325],"tcp_to_object_dist_end":0.02243,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.59155,0.16567,0.15016],"object_pos_start":[0.53545,0.02868,0.12493],"object_to_goal_dist_end":0.04513,"object_to_goal_dist_start":0.16468,"object_z_max":0.15015,"peak_contact_force":0.11213,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":35957.0,"raw_peak_contact_force":0.18312,"subtask_id":"approach_goal","tcp_end":[0.5915,0.16485,0.18096],"tcp_start":[0.52642,0.02802,0.14545],"tcp_to_object_dist_end":0.0308,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":21.0,"n_steps":104.0,"n_steps_budget":1000.0,"object_pos_end":[0.59422,0.1734,0.12014],"object_pos_start":[0.59155,0.16567,0.15016],"object_to_goal_dist_end":0.01501,"object_to_goal_dist_start":0.04513,"object_z_max":0.15016,"peak_contact_force":0.12065,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2217.0,"raw_peak_contact_force":0.19678,"subtask_id":"place_at_goal","tcp_end":[0.59469,0.17285,0.15208],"tcp_start":[0.5915,0.16485,0.18096],"tcp_to_object_dist_end":0.03195,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.26263,"average_solve_count":99.0,"average_success_count":99.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_height":0.13256,"approach_goal.speed":0.18055,"approach_object.approach_height":0.12999,"approach_object.speed":0.21195,"descend_to_grasp.descend_z":0.02044,"descend_to_grasp.lateral_offset_x":0.01177,"descend_to_grasp.lateral_offset_y":0.00831,"descend_to_grasp.speed":0.16263,"descend_to_place.place_z_offset":0.03259,"descend_to_place.speed":0.2916,"lift.lift_height":0.13789,"lift.speed":0.32298},"optimized_scores":{"best_composite_score":-0.15644,"best_fitness_score":0.56356,"best_task_score":0.196},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1628.0,"contact_point_centroid":[0.57881,0.11195,-0.00275],"force_p95":0.2803,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06027,"mean_force":0.16112,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57408,0.16523,0.26683]},{"body_a":"world","body_b":"grasp_target","contact_count":104.0,"contact_point_centroid":[0.50093,-0.00835,-0.00221],"force_p95":0.36992,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54596,"mean_force":0.07794,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.50013,-0.00815,0.04836]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4252.0,"contact_point_centroid":[0.50001,0.01003,0.08612],"force_p95":0.1263,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.39567,"mean_force":0.07403,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49901,-0.00908,0.0872]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6047.0,"contact_point_centroid":[0.49912,-0.02764,0.09389],"force_p95":0.10327,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36531,"mean_force":0.05337,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49903,-0.0092,0.09236]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50383,-0.01535,-0.00263],"force_p95":0.28378,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.32318,"mean_force":0.16636,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50272,-0.00805,0.04667]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4072.0,"contact_point_centroid":[0.55484,0.13023,0.24915],"force_p95":0.13322,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26046,"mean_force":0.10365,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.54926,0.11217,0.25264]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3901.0,"contact_point_centroid":[0.55491,0.09462,0.24962],"force_p95":0.13973,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20778,"mean_force":0.10974,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.54955,0.11274,0.25285]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16786.0,"contact_point_centroid":[0.51762,0.01549,0.1904],"force_p95":0.10259,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20246,"mean_force":0.05817,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51599,0.03383,0.18995]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10645.0,"contact_point_centroid":[0.51862,0.05463,0.18939],"force_p95":0.13429,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18372,"mean_force":0.08875,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51684,0.03578,0.19225]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4227.0,"contact_point_centroid":[0.50193,0.01117,0.04583],"force_p95":0.11303,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14111,"mean_force":0.05732,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50159,-0.00806,0.04541]},{"body_a":"world","body_b":"grasp_target","contact_count":1476.0,"contact_point_centroid":[0.50382,-0.01567,-0.00191],"force_p95":0.13511,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12296,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49902,-0.0068,0.23449]},{"body_a":"world","body_b":"grasp_target","contact_count":1452.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.5033,-0.01108,0.11086]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5253.0,"contact_point_centroid":[0.50151,-0.02774,0.04683],"force_p95":0.0984,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10285,"mean_force":0.04363,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50162,-0.00806,0.04545]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1586.0,"contact_point_centroid":[0.57481,0.16675,0.26957],"force_p95":0.01176,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01609,"mean_force":0.01067,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.5748,0.16674,0.26725]}],"total_contact_groups":14},"final_pose_error":0.01061,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.57899,0.11116,0.01602],"final_tcp_position":[0.58266,0.18336,0.27188],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":2.06027,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":370.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1476.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.49986,-0.01398,0.16895],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.143,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":363.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1452.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_at_object","tcp_end":[0.50946,-0.00807,0.05428],"tcp_start":[0.49986,-0.01398,0.16895],"tcp_to_object_dist_end":0.02981,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50363,-0.01068,0.0234],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31095,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.28469,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11280.0,"raw_peak_contact_force":0.32318,"subtask_id":"grasp_at_object","tcp_end":[0.50157,-0.00805,0.04539],"tcp_start":[0.50946,-0.00807,0.05428],"tcp_to_object_dist_end":0.02224,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":31.0,"n_steps":299.0,"n_steps_budget":600.0,"object_pos_end":[0.50817,-0.01272,0.11721],"object_pos_start":[0.50363,-0.01068,0.0234],"object_to_goal_dist_end":0.2518,"object_to_goal_dist_start":0.31095,"object_z_max":0.11694,"peak_contact_force":0.12291,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":10403.0,"raw_peak_contact_force":0.54596,"subtask_id":"lift_clearance","tcp_end":[0.49977,-0.01033,0.14185],"tcp_start":[0.50157,-0.00805,0.04539],"tcp_to_object_dist_end":0.02615,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54615,0.08198,0.21801],"object_pos_start":[0.50817,-0.01272,0.11721],"object_to_goal_dist_end":0.11701,"object_to_goal_dist_start":0.2518,"object_z_max":0.21794,"peak_contact_force":0.12511,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":27431.0,"raw_peak_contact_force":0.20246,"subtask_id":"approach_goal","tcp_end":[0.53874,0.08454,0.25044],"tcp_start":[0.49977,-0.01033,0.14185],"tcp_to_object_dist_end":0.03337,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.57899,0.11116,0.01602],"object_pos_start":[0.54615,0.08198,0.21801],"object_to_goal_dist_end":0.24444,"object_to_goal_dist_start":0.11701,"object_z_max":0.22054,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11187.0,"raw_peak_contact_force":2.06027,"subtask_id":"place_at_goal","tcp_end":[0.58266,0.18336,0.27188],"tcp_start":[0.53874,0.08454,0.25044],"tcp_to_object_dist_end":0.26587,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```