## Search State

- **Seed**: 4
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 12 | 0.1193 | 0.74 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 12 | -0.0847 | 0.52 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 12 | 0.1427 | 0.95 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 12 | 0.2521 | 1.00 | ✅ accepted |
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 13 | -0.1769 | 0.36 | ❌ rejected |

**Proposal policy**: task_score is 0.74 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.119) — your mutation base

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

- **Composite score**: 0.119
- **task_score** (E): 0.735
- **fitness_score**: 0.839  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.720

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1680 |
| descend_to_grasp | 1.00 | 1.00 | 0.0838 |
| grasp | 1.00 | 1.00 | 0.0127 |
| lift | 1.00 | 1.00 | 0.1578 |
| approach_goal | 1.00 | 1.00 | 0.1829 |
| descend_to_place | 1.00 | 1.00 | 0.0632 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.520, 0.005, 0.136) | (0.526, 0.005, 0.030)→(0.526, 0.005, 0.026) | 0.246→0.249 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.520, 0.005, 0.136)→(0.534, 0.006, 0.053) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.534, 0.006, 0.053)→(0.525, 0.006, 0.043) | (0.526, 0.005, 0.026)→(0.526, 0.006, 0.026) | 0.249→0.249 | 1.00 / 43.667 | 0.148 | 0.189 |
| lift | lift | 1.00 / step_budget | (0.525, 0.006, 0.043)→(0.523, 0.006, 0.201) | (0.526, 0.006, 0.026)→(0.533, 0.006, 0.180) | 0.249→0.195 | 1.00 / 35.333 | 0.086 | 0.590 |
| approach_goal | approach | 1.00 / step_budget | (0.523, 0.006, 0.201)→(0.599, 0.154, 0.271) | (0.533, 0.006, 0.180)→(0.594, 0.153, 0.133) | 0.195→0.112 | 1.00 / 18.667 | 91003.772 | 0.995 |
| descend_to_place | descend | 1.00 / step_budget | (0.599, 0.154, 0.271)→(0.606, 0.170, 0.211) | (0.594, 0.153, 0.133)→(0.596, 0.160, 0.105) | 0.112→0.090 | 1.00 / 17.333 | 0.148 | 0.209 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.079
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 1.000
- phase_score: 0.669
- phase_breakdown.approach_goal_score: 0.693
- phase_breakdown.place_at_goal_score: 0.388
- phase_breakdown.grasp_at_object_score: 0.697
- phase_breakdown.reach_pre_grasp_score: 0.874
- phase_breakdown.lift_clearance_score: 0.889
- grasp_place_fitness: 0.974

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.974
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.251
- **K-run variance**: 0.0356
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.391


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.43662,"average_solve_count":142.0,"average_success_count":142.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_height":0.05409,"approach_goal.speed":0.23796,"approach_object.approach_height":0.09975,"approach_object.speed":0.05734,"descend_to_grasp.descend_z":0.02081,"descend_to_grasp.lateral_offset_x":0.01264,"descend_to_grasp.lateral_offset_y":0.00352,"descend_to_grasp.speed":0.31886,"descend_to_place.place_z_offset":0.02218,"descend_to_place.speed":0.20258,"lift.lift_height":0.13277,"lift.speed":0.17152},"optimized_scores":{"best_composite_score":0.25146,"best_fitness_score":0.97146,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":91.0,"contact_point_centroid":[0.54103,0.00386,-0.00159],"force_p95":0.44487,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60202,"mean_force":0.09578,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.53972,0.00378,0.04483]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6587.0,"contact_point_centroid":[0.53843,-0.01565,0.09345],"force_p95":0.08065,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35443,"mean_force":0.0518,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.53871,0.00338,0.09114]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5541.0,"contact_point_centroid":[0.53917,0.02263,0.09197],"force_p95":0.08518,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34465,"mean_force":0.05882,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.53869,0.0034,0.08891]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1310.0,"contact_point_centroid":[0.63812,0.16568,0.21337],"force_p95":0.10524,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25521,"mean_force":0.07898,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.63683,0.14715,0.21623]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54431,0.00135,-0.00225],"force_p95":0.18531,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24639,"mean_force":0.14062,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.54223,0.00387,0.04448]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1229.0,"contact_point_centroid":[0.63864,0.12845,0.21405],"force_p95":0.10856,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24019,"mean_force":0.08279,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.63679,0.14709,0.21632]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18351.0,"contact_point_centroid":[0.58616,0.09283,0.18125],"force_p95":0.08457,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20641,"mean_force":0.05485,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.58591,0.07371,0.18051]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19465.0,"contact_point_centroid":[0.58376,0.05127,0.17937],"force_p95":0.08166,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20446,"mean_force":0.05155,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.58353,0.07028,0.17826]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4707.0,"contact_point_centroid":[0.5411,0.02305,0.04512],"force_p95":0.07673,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15135,"mean_force":0.04555,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.54102,0.00384,0.04301]},{"body_a":"world","body_b":"grasp_target","contact_count":2380.0,"contact_point_centroid":[0.54431,0.00113,-0.00194],"force_p95":0.13103,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12283,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51714,0.00049,0.21736]},{"body_a":"world","body_b":"grasp_target","contact_count":1104.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.54183,0.00245,0.09392]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5124.0,"contact_point_centroid":[0.54112,-0.0155,0.04496],"force_p95":0.07776,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07959,"mean_force":0.04413,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.54103,0.00384,0.04302]}],"total_contact_groups":12},"final_pose_error":0.00996,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.64502,0.1526,0.17759],"final_tcp_position":[0.64067,0.1528,0.20849],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":0.60202,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":596.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2380.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.53702,0.001,0.13636],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11058,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":276.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1104.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_at_object","tcp_end":[0.54938,0.00403,0.0533],"tcp_start":[0.53702,0.001,0.13636],"tcp_to_object_dist_end":0.0279,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5442,0.00303,0.0251],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.2496,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.17671,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11631.0,"raw_peak_contact_force":0.24639,"subtask_id":"grasp_at_object","tcp_end":[0.54099,0.00384,0.04298],"tcp_start":[0.54938,0.00403,0.0533],"tcp_to_object_dist_end":0.01818,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":315.0,"n_steps_budget":600.0,"object_pos_end":[0.54904,0.00286,0.11928],"object_pos_start":[0.5442,0.00303,0.0251],"object_to_goal_dist_end":0.19741,"object_to_goal_dist_start":0.2496,"object_z_max":0.11903,"peak_contact_force":0.08239,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":12219.0,"raw_peak_contact_force":0.60202,"subtask_id":"lift_clearance","tcp_end":[0.53995,0.00304,0.13858],"tcp_start":[0.54099,0.00384,0.04298],"tcp_to_object_dist_end":0.02133,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.63959,0.14148,0.19544],"object_pos_start":[0.54904,0.00286,0.11928],"object_to_goal_dist_end":0.01895,"object_to_goal_dist_start":0.19741,"object_z_max":0.19536,"peak_contact_force":0.09962,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":37816.0,"raw_peak_contact_force":0.20641,"subtask_id":"approach_goal","tcp_end":[0.63362,0.14157,0.22566],"tcp_start":[0.53995,0.00304,0.13858],"tcp_to_object_dist_end":0.03081,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":108.0,"n_steps_budget":1000.0,"object_pos_end":[0.64502,0.1526,0.17759],"object_pos_start":[0.63959,0.14148,0.19544],"object_to_goal_dist_end":0.01482,"object_to_goal_dist_start":0.01895,"object_z_max":0.19546,"peak_contact_force":0.09915,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2539.0,"raw_peak_contact_force":0.25521,"subtask_id":"place_at_goal","tcp_end":[0.64067,0.1528,0.20849],"tcp_start":[0.63362,0.14157,0.22566],"tcp_to_object_dist_end":0.03121,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.48485,"average_solve_count":99.0,"average_success_count":99.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_height":0.11994,"approach_goal.speed":0.21128,"approach_object.approach_height":0.09336,"approach_object.speed":0.43017,"descend_to_grasp.descend_z":0.02076,"descend_to_grasp.lateral_offset_x":0.01942,"descend_to_grasp.lateral_offset_y":0.00149,"descend_to_grasp.speed":0.31497,"descend_to_place.place_z_offset":0.0399,"descend_to_place.speed":0.15649,"lift.lift_height":0.17875,"lift.speed":0.3333},"optimized_scores":{"best_composite_score":0.25373,"best_fitness_score":0.97373,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":80.0,"contact_point_centroid":[0.52593,0.03074,-0.00143],"force_p95":0.50052,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.6367,"mean_force":0.11164,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.5321,0.03074,0.04399]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8654.0,"contact_point_centroid":[0.52835,0.04977,0.1159],"force_p95":0.07348,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37459,"mean_force":0.05067,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52844,0.03058,0.11377]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8571.0,"contact_point_centroid":[0.52843,0.01144,0.11539],"force_p95":0.07378,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36631,"mean_force":0.0509,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52845,0.03058,0.11323]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1728.0,"contact_point_centroid":[0.59133,0.15055,0.18388],"force_p95":0.15545,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24844,"mean_force":0.10626,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59302,0.16933,0.1871]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2267.0,"contact_point_centroid":[0.59292,0.18767,0.18255],"force_p95":0.13181,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2127,"mean_force":0.08402,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59305,0.16944,0.18622]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15598.0,"contact_point_centroid":[0.5562,0.07657,0.19813],"force_p95":0.10002,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15922,"mean_force":0.0623,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55702,0.09565,0.1977]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18236.0,"contact_point_centroid":[0.55682,0.11433,0.19807],"force_p95":0.08906,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1568,"mean_force":0.05349,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55691,0.09546,0.19764]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53048,0.03079,-0.00203],"force_p95":0.13006,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14542,"mean_force":0.12546,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53467,0.03093,0.04369]},{"body_a":"world","body_b":"grasp_target","contact_count":1940.0,"contact_point_centroid":[0.5305,0.03079,-0.00193],"force_p95":0.13308,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12288,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51104,0.014,0.21417]},{"body_a":"world","body_b":"grasp_target","contact_count":1124.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53151,0.02977,0.09016]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4860.0,"contact_point_centroid":[0.53353,0.05005,0.04411],"force_p95":0.06768,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08782,"mean_force":0.04476,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53347,0.03085,0.04225]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4864.0,"contact_point_centroid":[0.53355,0.01165,0.04419],"force_p95":0.06768,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08778,"mean_force":0.04471,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53347,0.03085,0.04225]}],"total_contact_groups":12},"final_pose_error":0.00985,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.5907,0.1744,0.12239],"final_tcp_position":[0.59573,0.17454,0.15484],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":0.6367,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":486.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1940.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.52424,0.02829,0.13046],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.10466,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":281.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1124.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_at_object","tcp_end":[0.5417,0.03141,0.05224],"tcp_start":[0.52424,0.02829,0.13046],"tcp_to_object_dist_end":0.02852,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53038,0.03082,0.02585],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18346,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12965,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11524.0,"raw_peak_contact_force":0.14542,"subtask_id":"grasp_at_object","tcp_end":[0.53344,0.03084,0.04222],"tcp_start":[0.5417,0.03141,0.05224],"tcp_to_object_dist_end":0.01665,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":419.0,"n_steps_budget":600.0,"object_pos_end":[0.5344,0.03068,0.16567],"object_pos_start":[0.53038,0.03082,0.02585],"object_to_goal_dist_end":0.17233,"object_to_goal_dist_start":0.18346,"object_z_max":0.1654,"peak_contact_force":0.06751,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":17305.0,"raw_peak_contact_force":0.6367,"subtask_id":"lift_clearance","tcp_end":[0.5274,0.0306,0.18497],"tcp_start":[0.53344,0.03084,0.04222],"tcp_to_object_dist_end":0.02052,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.59166,0.16596,0.18685],"object_pos_start":[0.5344,0.03068,0.16567],"object_to_goal_dist_end":0.08037,"object_to_goal_dist_start":0.17233,"object_z_max":0.18683,"peak_contact_force":0.09767,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":33834.0,"raw_peak_contact_force":0.15922,"subtask_id":"approach_goal","tcp_end":[0.59207,0.16542,0.21659],"tcp_start":[0.5274,0.0306,0.18497],"tcp_to_object_dist_end":0.02975,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":21.0,"n_steps":183.0,"n_steps_budget":1000.0,"object_pos_end":[0.5907,0.1744,0.12239],"object_pos_start":[0.59166,0.16596,0.18685],"object_to_goal_dist_end":0.01842,"object_to_goal_dist_start":0.08037,"object_z_max":0.18685,"peak_contact_force":0.22114,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3995.0,"raw_peak_contact_force":0.24844,"subtask_id":"place_at_goal","tcp_end":[0.59573,0.17454,0.15484],"tcp_start":[0.59207,0.16542,0.21659],"tcp_to_object_dist_end":0.03284,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.54955,"average_solve_count":111.0,"average_success_count":111.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_height":0.14682,"approach_goal.speed":0.25334,"approach_object.approach_height":0.10156,"approach_object.speed":0.21693,"descend_to_grasp.descend_z":0.02046,"descend_to_grasp.lateral_offset_x":0.01246,"descend_to_grasp.lateral_offset_y":-0.00105,"descend_to_grasp.speed":0.25743,"descend_to_place.place_z_offset":0.01339,"descend_to_place.speed":0.14917,"lift.lift_height":0.27391,"lift.speed":0.16521},"optimized_scores":{"best_composite_score":-0.14743,"best_fitness_score":0.57257,"best_task_score":0.2055},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":770.0,"contact_point_centroid":[0.55348,0.15225,-0.00402],"force_p95":0.99728,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.62054,"mean_force":0.22262,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.56512,0.13893,0.36064]},{"body_a":"world","body_b":"grasp_target","contact_count":76.0,"contact_point_centroid":[0.50075,-0.0164,-0.00137],"force_p95":0.42108,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.53151,"mean_force":0.09323,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.50062,-0.0162,0.04662]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12532.0,"contact_point_centroid":[0.50031,0.00289,0.15462],"force_p95":0.09662,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34517,"mean_force":0.05664,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49945,-0.01608,0.15314]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11242.0,"contact_point_centroid":[0.49975,-0.03518,0.15695],"force_p95":0.10248,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33256,"mean_force":0.06209,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49948,-0.01608,0.15567]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6441.0,"contact_point_centroid":[0.52625,0.01784,0.30282],"force_p95":0.13678,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25593,"mean_force":0.0962,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52124,0.03627,0.30409]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7212.0,"contact_point_centroid":[0.52642,0.05585,0.30346],"force_p95":0.12714,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21157,"mean_force":0.08658,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52177,0.03751,0.30476]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5038,-0.01573,-0.00205],"force_p95":0.13698,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17372,"mean_force":0.12701,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50292,-0.01623,0.04628]},{"body_a":"world","body_b":"grasp_target","contact_count":1732.0,"contact_point_centroid":[0.50382,-0.01567,-0.00192],"force_p95":0.13411,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12291,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49889,-0.00699,0.21998]},{"body_a":"world","body_b":"grasp_target","contact_count":1172.0,"contact_point_centroid":[0.55168,0.15246,-0.00199],"force_p95":0.12268,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12271,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57696,0.16848,0.31965]},{"body_a":"world","body_b":"grasp_target","contact_count":1156.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50332,-0.01525,0.09645]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4733.0,"contact_point_centroid":[0.50175,-0.03541,0.04723],"force_p95":0.06834,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09368,"mean_force":0.04579,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50178,-0.01621,0.04501]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4990.0,"contact_point_centroid":[0.50168,0.00299,0.04711],"force_p95":0.06736,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0817,"mean_force":0.04406,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50178,-0.01621,0.04501]},{"body_a":"left_finger","body_b":"right_finger","contact_count":791.0,"contact_point_centroid":[0.56568,0.14011,0.36361],"force_p95":0.01273,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01613,"mean_force":0.01081,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.56562,0.14011,0.36128]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1248.0,"contact_point_centroid":[0.57693,0.16851,0.32178],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01102,"mean_force":0.01047,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57697,0.1685,0.31959]}],"total_contact_groups":14},"final_pose_error":0.00983,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.55168,0.15246,0.01602],"final_tcp_position":[0.58253,0.18224,0.26861],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":273011.1193,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":434.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1732.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.49967,-0.01427,0.14044],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1145,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":289.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1156.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_at_object","tcp_end":[0.50966,-0.01632,0.0539],"tcp_start":[0.49967,-0.01427,0.14044],"tcp_to_object_dist_end":0.02849,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50371,-0.01608,0.02578],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.3127,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13658,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11523.0,"raw_peak_contact_force":0.17372,"subtask_id":"grasp_at_object","tcp_end":[0.50175,-0.01621,0.04498],"tcp_start":[0.50966,-0.01632,0.0539],"tcp_to_object_dist_end":0.0193,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":671.0,"n_steps_budget":960.0,"object_pos_end":[0.51608,-0.01593,0.25456],"object_pos_start":[0.50371,-0.01608,0.02578],"object_to_goal_dist_end":0.21546,"object_to_goal_dist_start":0.3127,"object_z_max":0.25429,"peak_contact_force":0.10762,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":23850.0,"raw_peak_contact_force":0.53151,"subtask_id":"lift_clearance","tcp_end":[0.50124,-0.01603,0.27986],"tcp_start":[0.50175,-0.01621,0.04498],"tcp_to_object_dist_end":0.02933,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5517,0.15247,0.01602],"object_pos_start":[0.51608,-0.01593,0.25456],"object_to_goal_dist_end":0.23734,"object_to_goal_dist_start":0.21546,"object_z_max":0.29998,"peak_contact_force":273011.1193,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":15214.0,"raw_peak_contact_force":2.62054,"subtask_id":"approach_goal","tcp_end":[0.57266,0.15623,0.37026],"tcp_start":[0.50124,-0.01603,0.27986],"tcp_to_object_dist_end":0.35488,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":293.0,"n_steps_budget":1000.0,"object_pos_end":[0.55168,0.15246,0.01602],"object_pos_start":[0.5517,0.15247,0.01602],"object_to_goal_dist_end":0.23735,"object_to_goal_dist_start":0.23734,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2420.0,"raw_peak_contact_force":0.12271,"subtask_id":"place_at_goal","tcp_end":[0.58253,0.18224,0.26861],"tcp_start":[0.57266,0.15623,0.37026],"tcp_to_object_dist_end":0.2562,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```