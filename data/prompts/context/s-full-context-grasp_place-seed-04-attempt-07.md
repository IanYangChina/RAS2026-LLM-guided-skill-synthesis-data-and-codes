## Search State

- **Seed**: 4
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 12 | -0.0847 | 0.52 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 12 | 0.1427 | 0.95 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 12 | 0.2521 | 1.00 | ✅ accepted |
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 13 | -0.1769 | 0.36 | ❌ rejected |
| 3 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 12 | 0.1213 | 0.74 | ❌ rejected |

**Proposal policy**: task_score is 0.52 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.085) — your mutation base

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

- **Composite score**: -0.085
- **task_score** (E): 0.523
- **fitness_score**: 0.635  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.720

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1422 |
| descend_to_grasp | 1.00 | 1.00 | 0.0984 |
| grasp | 1.00 | 1.00 | 0.0134 |
| lift | 1.00 | 1.00 | 0.1376 |
| approach_goal | 1.00 | 0.67 | 0.1746 |
| descend_to_place | 1.00 | 1.00 | 0.0524 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.519, 0.004, 0.161) | (0.526, 0.005, 0.030)→(0.526, 0.005, 0.026) | 0.246→0.249 | 1.00 / 4.000 | 22.821 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.519, 0.004, 0.161)→(0.532, 0.005, 0.064) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 4.000 | 18.431 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.532, 0.005, 0.064)→(0.523, 0.005, 0.054) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 28.000 | 0.145 | 0.177 |
| lift | lift | 1.00 / step_budget | (0.523, 0.005, 0.054)→(0.523, 0.005, 0.191) | (0.526, 0.005, 0.026)→(0.531, 0.005, 0.160) | 0.249→0.205 | 1.00 / 22.333 | 0.110 | 0.380 |
| approach_goal | approach | 1.00 / step_budget | (0.523, 0.005, 0.191)→(0.592, 0.137, 0.261) | (0.531, 0.005, 0.160)→(0.599, 0.133, 0.203) | 0.205→0.063 | 0.67 / 14.000 | 0.114 | 0.363 |
| descend_to_place | descend | 1.00 / step_budget | (0.592, 0.137, 0.261)→(0.603, 0.162, 0.216) | (0.599, 0.133, 0.203)→(0.614, 0.168, 0.053) | 0.063→0.132 | 1.00 / 8.667 | 55986.315 | 0.710 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.239
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 1.000
- phase_score: 0.634
- phase_breakdown.approach_goal_score: 0.376
- phase_breakdown.place_at_goal_score: 0.524
- phase_breakdown.grasp_at_object_score: 0.864
- phase_breakdown.reach_pre_grasp_score: 0.361
- phase_breakdown.lift_clearance_score: 0.800
- grasp_place_fitness: 0.957

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.957
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: -0.096
- **K-run variance**: 0.0668
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.354


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.32479,"average_solve_count":117.0,"average_success_count":117.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_height":0.09106,"approach_goal.speed":0.13493,"approach_object.approach_height":0.07678,"approach_object.speed":0.41095,"descend_to_grasp.descend_z":0.02129,"descend_to_grasp.lateral_offset_x":0.01711,"descend_to_grasp.lateral_offset_y":-0.0034,"descend_to_grasp.speed":0.36112,"descend_to_place.place_z_offset":0.01533,"descend_to_place.speed":0.21686,"lift.lift_height":0.24974,"lift.speed":0.173},"optimized_scores":{"best_composite_score":-0.09596,"best_fitness_score":0.62404,"best_task_score":0.33154},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3.0,"contact_point_centroid":[0.65188,0.14861,-0.00126],"force_p95":1.68339,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.69208,"mean_force":1.46704,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.63702,0.14493,0.21786]},{"body_a":"world","body_b":"grasp_target","contact_count":72.0,"contact_point_centroid":[0.54126,-0.00114,-0.0017],"force_p95":0.39277,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.41974,"mean_force":0.08064,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.54023,-0.00168,0.05411]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":191.0,"contact_point_centroid":[0.62562,0.10333,0.25895],"force_p95":0.27634,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.41357,"mean_force":0.13907,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62312,0.12148,0.26439]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1432.0,"contact_point_centroid":[0.58181,0.03666,0.25133],"force_p95":0.20711,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.40973,"mean_force":0.1231,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.57956,0.05509,0.25454]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":357.0,"contact_point_centroid":[0.62731,0.14014,0.25531],"force_p95":0.21346,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.39256,"mean_force":0.09745,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62411,0.1234,0.26024]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4306.0,"contact_point_centroid":[0.54016,0.01716,0.13903],"force_p95":0.13994,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.38291,"mean_force":0.09008,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.53986,-0.0013,0.14196]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3827.0,"contact_point_centroid":[0.53902,-0.01994,0.14191],"force_p95":0.14376,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34085,"mean_force":0.09697,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.53989,-0.00129,0.14475]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1667.0,"contact_point_centroid":[0.58228,0.07238,0.25073],"force_p95":0.17024,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32651,"mean_force":0.10536,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.57909,0.0544,0.25438]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54431,0.00098,-0.00223],"force_p95":0.18419,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23629,"mean_force":0.13874,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.54296,-0.00165,0.05397]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2641.0,"contact_point_centroid":[0.5409,-0.02048,0.04976],"force_p95":0.10371,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14391,"mean_force":0.076,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.54178,-0.00166,0.05252]},{"body_a":"world","body_b":"grasp_target","contact_count":876.0,"contact_point_centroid":[0.54431,0.00113,-0.00185],"force_p95":0.13713,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12318,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51615,0.00044,0.21869]},{"body_a":"world","body_b":"grasp_target","contact_count":572.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.54081,-0.00025,0.09858]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3834.0,"contact_point_centroid":[0.54301,0.01721,0.05102],"force_p95":0.09598,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09688,"mean_force":0.0556,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.54179,-0.00166,0.05253]}],"total_contact_groups":13},"final_pose_error":0.01978,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.64517,0.16373,0.02562],"final_tcp_position":[0.63721,0.14525,0.21731],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":55.04732,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":220.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":876.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.53391,0.00089,0.13477],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.10924,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":143.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":55.04732,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":572.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_at_object","tcp_end":[0.55041,-0.00151,0.06348],"tcp_start":[0.53391,0.00089,0.13477],"tcp_to_object_dist_end":0.03805,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5442,-0.00071,0.02521],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25186,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.17488,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":8275.0,"raw_peak_contact_force":0.23629,"subtask_id":"grasp_at_object","tcp_end":[0.54176,-0.00166,0.05248],"tcp_start":[0.55041,-0.00151,0.06348],"tcp_to_object_dist_end":0.0274,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":20.0,"n_steps":364.0,"n_steps_budget":810.0,"object_pos_end":[0.55105,-0.00011,0.21352],"object_pos_start":[0.5442,-0.00071,0.02521],"object_to_goal_dist_end":0.18669,"object_to_goal_dist_start":0.25186,"object_z_max":0.21305,"peak_contact_force":0.1175,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":8205.0,"raw_peak_contact_force":0.41974,"subtask_id":"lift_clearance","tcp_end":[0.54171,-0.00084,0.24544],"tcp_start":[0.54176,-0.00166,0.05248],"tcp_to_object_dist_end":0.03327,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":156.0,"n_steps_budget":1000.0,"object_pos_end":[0.62685,0.1176,0.231],"object_pos_start":[0.55105,-0.00011,0.21352],"object_to_goal_dist_end":0.06051,"object_to_goal_dist_start":0.18669,"object_z_max":0.23092,"peak_contact_force":0.24294,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3099.0,"raw_peak_contact_force":0.40973,"subtask_id":"approach_goal","tcp_end":[0.62183,0.1182,0.26684],"tcp_start":[0.54171,-0.00084,0.24544],"tcp_to_object_dist_end":0.03619,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":114.0,"n_steps_budget":1000.0,"object_pos_end":[0.64517,0.16373,0.02562],"object_pos_start":[0.62685,0.1176,0.231],"object_to_goal_dist_end":0.1656,"object_to_goal_dist_start":0.06051,"object_z_max":0.23102,"peak_contact_force":1.69208,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":551.0,"raw_peak_contact_force":1.69208,"subtask_id":"place_at_goal","tcp_end":[0.63721,0.14525,0.21731],"tcp_start":[0.62183,0.1182,0.26684],"tcp_to_object_dist_end":0.19274,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.58095,"average_solve_count":105.0,"average_success_count":105.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_height":0.10332,"approach_goal.speed":0.16641,"approach_object.approach_height":0.12228,"approach_object.speed":0.19149,"descend_to_grasp.descend_z":0.02013,"descend_to_grasp.lateral_offset_x":0.01245,"descend_to_grasp.lateral_offset_y":0.00265,"descend_to_grasp.speed":0.17731,"descend_to_place.place_z_offset":0.0157,"descend_to_place.speed":0.08909,"lift.lift_height":0.19417,"lift.speed":0.17191},"optimized_scores":{"best_composite_score":0.23727,"best_fitness_score":0.95727,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"right_finger","body_b":"grasp_target","contact_count":1772.0,"contact_point_centroid":[0.58637,0.16908,0.16493],"force_p95":0.1781,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.43867,"mean_force":0.08694,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.58544,0.15076,0.1688]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1539.0,"contact_point_centroid":[0.55285,0.06044,0.19118],"force_p95":0.16715,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.38934,"mean_force":0.09991,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55188,0.07913,0.19427]},{"body_a":"world","body_b":"grasp_target","contact_count":64.0,"contact_point_centroid":[0.5277,0.03064,-0.00149],"force_p95":0.35529,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.37628,"mean_force":0.07799,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52544,0.03076,0.05502]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2783.0,"contact_point_centroid":[0.52429,0.0119,0.11651],"force_p95":0.14585,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35125,"mean_force":0.0962,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52532,0.03056,0.11929]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3138.0,"contact_point_centroid":[0.52532,0.04906,0.11796],"force_p95":0.13827,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34757,"mean_force":0.08851,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52537,0.03056,0.12115]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1392.0,"contact_point_centroid":[0.58616,0.13135,0.16656],"force_p95":0.17999,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31404,"mean_force":0.10671,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.58512,0.15002,0.1705]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1320.0,"contact_point_centroid":[0.55339,0.09849,0.19122],"force_p95":0.16527,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23029,"mean_force":0.10481,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55231,0.08,0.19439]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53049,0.03075,-0.00203],"force_p95":0.12891,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14329,"mean_force":0.125,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52791,0.03095,0.05516]},{"body_a":"world","body_b":"grasp_target","contact_count":668.0,"contact_point_centroid":[0.5305,0.03079,-0.00181],"force_p95":0.13762,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12336,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51015,0.01126,0.24151]},{"body_a":"world","body_b":"grasp_target","contact_count":848.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52731,0.02746,0.12145]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2680.0,"contact_point_centroid":[0.52588,0.01207,0.0512],"force_p95":0.09954,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10004,"mean_force":0.07573,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52676,0.03087,0.0538]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2924.0,"contact_point_centroid":[0.52664,0.0495,0.05079],"force_p95":0.09168,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09206,"mean_force":0.07007,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52676,0.03087,0.0538]}],"total_contact_groups":12},"final_pose_error":0.01997,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.59751,0.16576,0.10094],"final_tcp_position":[0.59239,0.16625,0.13657],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":167951.73011,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":168.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":68.217,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":668.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.52153,0.02366,0.17967],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15407,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":212.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":848.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_at_object","tcp_end":[0.5352,0.03141,0.06431],"tcp_start":[0.52153,0.02366,0.17967],"tcp_to_object_dist_end":0.03858,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53041,0.03068,0.02588],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18355,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12877,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":7404.0,"raw_peak_contact_force":0.14329,"subtask_id":"grasp_at_object","tcp_end":[0.52673,0.03087,0.05376],"tcp_start":[0.5352,0.03141,0.06431],"tcp_to_object_dist_end":0.02812,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":257.0,"n_steps_budget":630.0,"object_pos_end":[0.53651,0.03025,0.15953],"object_pos_start":[0.53041,0.03068,0.02588],"object_to_goal_dist_end":0.16993,"object_to_goal_dist_start":0.18355,"object_z_max":0.15906,"peak_contact_force":0.10935,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":5985.0,"raw_peak_contact_force":0.37628,"subtask_id":"lift_clearance","tcp_end":[0.52725,0.03049,0.19069],"tcp_start":[0.52673,0.03087,0.05376],"tcp_to_object_dist_end":0.0325,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":124.0,"n_steps_budget":1000.0,"object_pos_end":[0.5864,0.13489,0.16583],"object_pos_start":[0.53651,0.03025,0.15953],"object_to_goal_dist_end":0.07397,"object_to_goal_dist_start":0.16993,"object_z_max":0.16577,"peak_contact_force":0.09992,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2859.0,"raw_peak_contact_force":0.38934,"subtask_id":"approach_goal","tcp_end":[0.57992,0.13556,0.19961],"tcp_start":[0.52725,0.03049,0.19069],"tcp_to_object_dist_end":0.0344,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":140.0,"n_steps_budget":1000.0,"object_pos_end":[0.59751,0.16576,0.10094],"object_pos_start":[0.5864,0.13489,0.16583],"object_to_goal_dist_end":0.01522,"object_to_goal_dist_start":0.07397,"object_z_max":0.16585,"peak_contact_force":167951.73011,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3164.0,"raw_peak_contact_force":0.43867,"subtask_id":"place_at_goal","tcp_end":[0.59239,0.16625,0.13657],"tcp_start":[0.57992,0.13556,0.19961],"tcp_to_object_dist_end":0.03599,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.15385,"average_solve_count":104.0,"average_success_count":104.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_height":0.1072,"approach_goal.speed":0.27822,"approach_object.approach_height":0.11089,"approach_object.speed":0.21761,"descend_to_grasp.descend_z":0.02007,"descend_to_grasp.lateral_offset_x":0.01203,"descend_to_grasp.lateral_offset_y":-0.00069,"descend_to_grasp.speed":0.23602,"descend_to_place.place_z_offset":0.03412,"descend_to_place.speed":0.09078,"lift.lift_height":0.14122,"lift.speed":0.23607},"optimized_scores":{"best_composite_score":-0.3953,"best_fitness_score":0.3247,"best_task_score":0.23789},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":65.0,"contact_point_centroid":[0.50077,-0.01521,-0.00152],"force_p95":0.30541,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.34514,"mean_force":0.0779,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49984,-0.0154,0.05622]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.4998,0.00333,0.09124],"force_p95":0.16216,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33851,"mean_force":0.09647,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.4991,-0.01535,0.09425]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1968.0,"contact_point_centroid":[0.49903,-0.03385,0.091],"force_p95":0.15497,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33276,"mean_force":0.09056,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.4991,-0.01535,0.09425]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2223.0,"contact_point_centroid":[0.52877,0.06797,0.19958],"force_p95":0.14326,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2901,"mean_force":0.09375,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52783,0.04935,0.20313]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2544.0,"contact_point_centroid":[0.5301,0.03406,0.20267],"force_p95":0.13347,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2009,"mean_force":0.08393,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52917,0.05243,0.20633]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50381,-0.01563,-0.00203],"force_p95":0.13294,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15243,"mean_force":0.12553,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.5022,-0.01542,0.05622]},{"body_a":"world","body_b":"grasp_target","contact_count":684.0,"contact_point_centroid":[0.50382,-0.01567,-0.00181],"force_p95":0.13762,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12334,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50025,-0.0058,0.23675]},{"body_a":"world","body_b":"grasp_target","contact_count":792.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50401,-0.01381,0.11683]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2673.0,"contact_point_centroid":[0.50175,0.00339,0.05206],"force_p95":0.09988,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10717,"mean_force":0.07587,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50109,-0.01541,0.05499]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2936.0,"contact_point_centroid":[0.50099,-0.03404,0.05181],"force_p95":0.09211,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09254,"mean_force":0.06991,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50109,-0.01541,0.05499]}],"total_contact_groups":10},"final_pose_error":0.01992,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.59909,0.17389,0.03349],"final_tcp_position":[0.5803,0.17338,0.29468],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":5.5229,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":172.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":684.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.50085,-0.01218,0.16983],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14388,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":198.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":792.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_at_object","tcp_end":[0.50923,-0.0155,0.0645],"tcp_start":[0.50085,-0.01218,0.16983],"tcp_to_object_dist_end":0.03886,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50373,-0.01539,0.02586],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31219,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13158,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":7409.0,"raw_peak_contact_force":0.15243,"subtask_id":"grasp_at_object","tcp_end":[0.50106,-0.01541,0.05495],"tcp_start":[0.50923,-0.0155,0.0645],"tcp_to_object_dist_end":0.02922,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":164.0,"n_steps_budget":600.0,"object_pos_end":[0.50685,-0.01533,0.10798],"object_pos_start":[0.50373,-0.01539,0.02586],"object_to_goal_dist_end":0.25916,"object_to_goal_dist_start":0.31219,"object_z_max":0.1075,"peak_contact_force":0.10397,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":3837.0,"raw_peak_contact_force":0.34514,"subtask_id":"lift_clearance","tcp_end":[0.50004,-0.01532,0.13779],"tcp_start":[0.50106,-0.01541,0.05495],"tcp_to_object_dist_end":0.03058,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":265.0,"n_steps_budget":1000.0,"object_pos_end":[0.58432,0.14516,0.21205],"object_pos_start":[0.50685,-0.01533,0.10798],"object_to_goal_dist_end":0.05565,"object_to_goal_dist_start":0.25916,"object_z_max":0.24459,"peak_contact_force":0.0,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4767.0,"raw_peak_contact_force":0.2901,"subtask_id":"approach_goal","tcp_end":[0.57541,0.15836,0.31719],"tcp_start":[0.50004,-0.01532,0.13779],"tcp_to_object_dist_end":0.10634,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":63.0,"n_steps_budget":1000.0,"object_pos_end":[0.59909,0.17389,0.03349],"object_pos_start":[0.58432,0.14516,0.21205],"object_to_goal_dist_end":0.21539,"object_to_goal_dist_start":0.05565,"object_z_max":0.21205,"peak_contact_force":5.5229,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"place_at_goal","tcp_end":[0.5803,0.17338,0.29468],"tcp_start":[0.57541,0.15836,0.31719],"tcp_to_object_dist_end":0.26186,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```