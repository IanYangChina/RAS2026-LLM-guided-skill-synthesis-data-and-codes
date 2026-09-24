## Search State

- **Seed**: 4
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 12 | 0.1213 | 0.74 | ❌ rejected |
| 2 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 12 | 0.2195 | 0.93 | ✅ accepted |
| 1 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 14 | -0.2274 | 0.36 | ✅ accepted |
| 0 | push → align → release → insert → lift | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | admittance_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.0580 | 0.20 | ✅ accepted |

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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.934, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.121) — your mutation base

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

- **Composite score**: 0.121
- **task_score** (E): 0.737
- **fitness_score**: 0.841  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.720

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1709 |
| descend_to_grasp | 1.00 | 1.00 | 0.0831 |
| grasp | 1.00 | 1.00 | 0.0130 |
| lift | 1.00 | 1.00 | 0.1319 |
| approach_goal | 0.00 | 1.00 | 0.1434 |
| descend_to_place | 1.00 | 1.00 | 0.0691 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.520, 0.005, 0.133) | (0.526, 0.005, 0.030)→(0.526, 0.005, 0.026) | 0.246→0.249 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.520, 0.005, 0.133)→(0.537, 0.008, 0.052) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.537, 0.008, 0.052)→(0.528, 0.008, 0.042) | (0.526, 0.005, 0.026)→(0.526, 0.007, 0.025) | 0.249→0.248 | 1.00 / 44.667 | 0.208 | 0.284 |
| lift | lift | 1.00 / step_budget | (0.528, 0.008, 0.042)→(0.523, 0.007, 0.173) | (0.526, 0.007, 0.025)→(0.530, 0.007, 0.153) | 0.248→0.198 | 1.00 / 38.333 | 0.083 | 0.611 |
| approach_goal | approach | 0.00 / step_budget | (0.523, 0.007, 0.173)→(0.580, 0.123, 0.234) | (0.530, 0.007, 0.153)→(0.585, 0.124, 0.203) | 0.198→0.071 | 1.00 / 25.333 | 0.194 | 0.252 |
| descend_to_place | descend | 1.00 / step_budget | (0.580, 0.123, 0.234)→(0.607, 0.170, 0.202) | (0.585, 0.124, 0.203)→(0.607, 0.170, 0.098) | 0.071→0.086 | 1.00 / 17.333 | 0.123 | 0.837 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.338
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 1.000
- phase_score: 0.681
- phase_breakdown.approach_goal_score: 0.129
- phase_breakdown.place_at_goal_score: 0.638
- phase_breakdown.grasp_at_object_score: 0.664
- phase_breakdown.reach_pre_grasp_score: 0.851
- phase_breakdown.lift_clearance_score: 0.854
- grasp_place_fitness: 0.974

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.974
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.253
- **K-run variance**: 0.0350
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.324


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.03704,"average_solve_count":108.0,"average_success_count":108.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_height":0.10057,"approach_goal.speed":0.13543,"approach_object.approach_height":0.09678,"approach_object.speed":0.29289,"descend_to_grasp.descend_z":0.02007,"descend_to_grasp.lateral_offset_x":0.01948,"descend_to_grasp.lateral_offset_y":0.00679,"descend_to_grasp.speed":0.48114,"descend_to_place.place_z_offset":0.0307,"descend_to_place.speed":0.28318,"lift.lift_height":0.18109,"lift.speed":0.12266},"optimized_scores":{"best_composite_score":0.25404,"best_fitness_score":0.97404,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":106.0,"contact_point_centroid":[0.54138,0.0062,-0.00189],"force_p95":0.48736,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60057,"mean_force":0.09706,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.54507,0.00656,0.04278]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9811.0,"contact_point_centroid":[0.54171,-0.01328,0.11572],"force_p95":0.08401,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35565,"mean_force":0.05241,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.5416,0.00581,0.11358]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8780.0,"contact_point_centroid":[0.54226,0.02507,0.11428],"force_p95":0.08645,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31985,"mean_force":0.05538,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.54166,0.00583,0.11134]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54422,0.00163,-0.00248],"force_p95":0.24189,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.29928,"mean_force":0.15704,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.54805,0.00668,0.04199]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12943.0,"contact_point_centroid":[0.62039,0.14196,0.21873],"force_p95":0.09796,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27928,"mean_force":0.06747,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61946,0.1234,0.22075]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11934.0,"contact_point_centroid":[0.62026,0.10368,0.21947],"force_p95":0.12474,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27607,"mean_force":0.07388,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61873,0.12238,0.22105]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20010.0,"contact_point_centroid":[0.56814,0.02858,0.21056],"force_p95":0.07425,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14758,"mean_force":0.05001,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5673,0.04761,0.20871]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4635.0,"contact_point_centroid":[0.54701,0.02589,0.04258],"force_p95":0.08704,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14737,"mean_force":0.04608,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.5468,0.00664,0.04046]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18260.0,"contact_point_centroid":[0.56965,0.06894,0.21155],"force_p95":0.08092,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14079,"mean_force":0.0543,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.56881,0.04978,0.21013]},{"body_a":"world","body_b":"grasp_target","contact_count":1952.0,"contact_point_centroid":[0.54431,0.00113,-0.00193],"force_p95":0.13308,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12288,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51735,0.00049,0.21577]},{"body_a":"world","body_b":"grasp_target","contact_count":1164.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.54471,0.00386,0.09083]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5288.0,"contact_point_centroid":[0.54704,-0.01308,0.04223],"force_p95":0.08849,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09412,"mean_force":0.04495,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.54683,0.00664,0.04049]}],"total_contact_groups":12},"final_pose_error":0.01069,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.64568,0.15518,0.17833],"final_tcp_position":[0.64266,0.15512,0.21281],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":0.60057,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":489.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1952.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.53696,0.00099,0.13331],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.10754,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":291.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1164.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_at_object","tcp_end":[0.55537,0.00688,0.05108],"tcp_start":[0.53696,0.00099,0.13331],"tcp_to_object_dist_end":0.02799,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54403,0.00512,0.02428],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.24892,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.22113,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11723.0,"raw_peak_contact_force":0.29928,"subtask_id":"grasp_at_object","tcp_end":[0.54678,0.00664,0.04042],"tcp_start":[0.55537,0.00688,0.05108],"tcp_to_object_dist_end":0.01645,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":480.0,"n_steps_budget":840.0,"object_pos_end":[0.54833,0.00475,0.16683],"object_pos_start":[0.54403,0.00512,0.02428],"object_to_goal_dist_end":0.18428,"object_to_goal_dist_start":0.24892,"object_z_max":0.16657,"peak_contact_force":0.08017,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":18697.0,"raw_peak_contact_force":0.60057,"subtask_id":"lift_clearance","tcp_end":[0.54072,0.00515,0.18579],"tcp_start":[0.54678,0.00664,0.04042],"tcp_to_object_dist_end":0.02043,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.60147,0.08818,0.20822],"object_pos_start":[0.54833,0.00475,0.16683],"object_to_goal_dist_end":0.0855,"object_to_goal_dist_start":0.18428,"object_z_max":0.20816,"peak_contact_force":0.08079,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":38270.0,"raw_peak_contact_force":0.14758,"subtask_id":"approach_goal","tcp_end":[0.59625,0.08845,0.23614],"tcp_start":[0.54072,0.00515,0.18579],"tcp_to_object_dist_end":0.02841,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":20.0,"n_steps":912.0,"n_steps_budget":1000.0,"object_pos_end":[0.64568,0.15518,0.17833],"object_pos_start":[0.60147,0.08818,0.20822],"object_to_goal_dist_end":0.01324,"object_to_goal_dist_start":0.0855,"object_z_max":0.20822,"peak_contact_force":0.12818,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":24877.0,"raw_peak_contact_force":0.27928,"subtask_id":"place_at_goal","tcp_end":[0.64266,0.15512,0.21281],"tcp_start":[0.59625,0.08845,0.23614],"tcp_to_object_dist_end":0.03461,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.21,"average_solve_count":100.0,"average_success_count":100.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_height":0.11679,"approach_goal.speed":0.13644,"approach_object.approach_height":0.07863,"approach_object.speed":0.48996,"descend_to_grasp.descend_z":0.02007,"descend_to_grasp.lateral_offset_x":0.01609,"descend_to_grasp.lateral_offset_y":0.00856,"descend_to_grasp.speed":0.32668,"descend_to_place.place_z_offset":0.02207,"descend_to_place.speed":0.23036,"lift.lift_height":0.16644,"lift.speed":0.39621},"optimized_scores":{"best_composite_score":0.25333,"best_fitness_score":0.97333,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":98.0,"contact_point_centroid":[0.52798,0.03592,-0.00193],"force_p95":0.52865,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63194,"mean_force":0.09953,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52833,0.03644,0.04324]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8086.0,"contact_point_centroid":[0.52655,0.01653,0.1085],"force_p95":0.08516,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.38119,"mean_force":0.05255,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52642,0.03556,0.10625]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6941.0,"contact_point_centroid":[0.52715,0.05488,0.10715],"force_p95":0.08773,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34317,"mean_force":0.05782,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52642,0.03559,0.10416]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53047,0.03136,-0.0025],"force_p95":0.24652,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.30394,"mean_force":0.15811,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53115,0.03671,0.04254]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3838.0,"contact_point_centroid":[0.58866,0.1333,0.16335],"force_p95":0.11556,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26814,"mean_force":0.08024,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.58319,0.15193,0.16342]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3764.0,"contact_point_centroid":[0.58865,0.17089,0.16225],"force_p95":0.11671,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24652,"mean_force":0.08229,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.58333,0.15223,0.16287]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17808.0,"contact_point_centroid":[0.54967,0.06296,0.18399],"force_p95":0.09168,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20069,"mean_force":0.05594,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.54799,0.0819,0.18266]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16848.0,"contact_point_centroid":[0.54985,0.10196,0.18341],"force_p95":0.09865,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1656,"mean_force":0.05856,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.54848,0.08292,0.18297]},{"body_a":"world","body_b":"grasp_target","contact_count":2064.0,"contact_point_centroid":[0.5305,0.03079,-0.00193],"force_p95":0.13251,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12286,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51105,0.01405,0.20709]},{"body_a":"world","body_b":"grasp_target","contact_count":964.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52986,0.03267,0.08242]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4285.0,"contact_point_centroid":[0.53043,0.05592,0.04426],"force_p95":0.09031,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11962,"mean_force":0.04952,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52993,0.03661,0.0411]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5316.0,"contact_point_centroid":[0.53018,0.01686,0.04291],"force_p95":0.08855,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09529,"mean_force":0.04498,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52995,0.03661,0.04113]}],"total_contact_groups":12},"final_pose_error":0.00994,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.59998,0.17157,0.09941],"final_tcp_position":[0.5941,0.17198,0.13017],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":0.63194,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":517.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2064.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.52419,0.02841,0.11593],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.09016,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":241.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":964.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_at_object","tcp_end":[0.53828,0.03725,0.05111],"tcp_start":[0.52419,0.02841,0.11593],"tcp_to_object_dist_end":0.02705,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53029,0.03502,0.02422],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18088,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.22634,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11401.0,"raw_peak_contact_force":0.30394,"subtask_id":"grasp_at_object","tcp_end":[0.52991,0.03661,0.04107],"tcp_start":[0.53828,0.03725,0.05111],"tcp_to_object_dist_end":0.01692,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":392.0,"n_steps_budget":600.0,"object_pos_end":[0.53636,0.03434,0.1511],"object_pos_start":[0.53029,0.03502,0.02422],"object_to_goal_dist_end":0.16402,"object_to_goal_dist_start":0.18088,"object_z_max":0.15084,"peak_contact_force":0.08456,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":15125.0,"raw_peak_contact_force":0.63194,"subtask_id":"lift_clearance","tcp_end":[0.52682,0.03489,0.17123],"tcp_start":[0.52991,0.03661,0.04107],"tcp_to_object_dist_end":0.02228,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58367,0.13272,0.17233],"object_pos_start":[0.53636,0.03434,0.1511],"object_to_goal_dist_end":0.08093,"object_to_goal_dist_start":0.16402,"object_z_max":0.1723,"peak_contact_force":0.09767,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":34656.0,"raw_peak_contact_force":0.20069,"subtask_id":"approach_goal","tcp_end":[0.5746,0.13284,0.20057],"tcp_start":[0.52682,0.03489,0.17123],"tcp_to_object_dist_end":0.02966,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":314.0,"n_steps_budget":1000.0,"object_pos_end":[0.59998,0.17157,0.09941],"object_pos_start":[0.58367,0.13272,0.17233],"object_to_goal_dist_end":0.01126,"object_to_goal_dist_start":0.08093,"object_z_max":0.17233,"peak_contact_force":0.11852,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7602.0,"raw_peak_contact_force":0.26814,"subtask_id":"place_at_goal","tcp_end":[0.5941,0.17198,0.13017],"tcp_start":[0.5746,0.13284,0.20057],"tcp_to_object_dist_end":0.03132,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.12121,"average_solve_count":99.0,"average_success_count":99.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_height":0.05056,"approach_goal.speed":0.25957,"approach_object.approach_height":0.11025,"approach_object.speed":0.18616,"descend_to_grasp.descend_z":0.02011,"descend_to_grasp.lateral_offset_x":0.01953,"descend_to_grasp.lateral_offset_y":-0.00387,"descend_to_grasp.speed":0.23319,"descend_to_place.place_z_offset":0.02246,"descend_to_place.speed":0.17584,"lift.lift_height":0.1577,"lift.speed":0.33998},"optimized_scores":{"best_composite_score":-0.14336,"best_fitness_score":0.57664,"best_task_score":0.21231},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1454.0,"contact_point_centroid":[0.57453,0.18372,-0.00285],"force_p95":0.39219,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.96436,"mean_force":0.15964,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57754,0.17267,0.261]},{"body_a":"world","body_b":"grasp_target","contact_count":89.0,"contact_point_centroid":[0.50119,-0.01857,-0.0017],"force_p95":0.45834,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.59918,"mean_force":0.09562,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.50634,-0.01867,0.04516]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13284.0,"contact_point_centroid":[0.52745,0.03476,0.20392],"force_p95":0.12987,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.40763,"mean_force":0.07352,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52772,0.05373,0.20476]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7639.0,"contact_point_centroid":[0.50266,0.00084,0.10515],"force_p95":0.07813,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37915,"mean_force":0.05006,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.50236,-0.0182,0.10285]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6474.0,"contact_point_centroid":[0.50204,-0.03745,0.1034],"force_p95":0.08708,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33996,"mean_force":0.05706,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.50241,-0.01821,0.1015]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3.0,"contact_point_centroid":[0.56484,0.13271,0.25939],"force_p95":0.27136,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27497,"mean_force":0.24966,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.56772,0.14735,0.26522]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50375,-0.01593,-0.00227],"force_p95":0.19093,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24973,"mean_force":0.14216,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50907,-0.01873,0.04472]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16484.0,"contact_point_centroid":[0.52828,0.07356,0.20514],"force_p95":0.10016,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23881,"mean_force":0.0588,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52821,0.0549,0.20551]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":134.0,"contact_point_centroid":[0.56947,0.1633,0.25999],"force_p95":0.10769,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21576,"mean_force":0.03007,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.56781,0.14798,0.26491]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4414.0,"contact_point_centroid":[0.50746,-0.03793,0.04563],"force_p95":0.08256,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15035,"mean_force":0.0484,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50789,-0.01871,0.04339]},{"body_a":"world","body_b":"grasp_target","contact_count":1656.0,"contact_point_centroid":[0.50382,-0.01567,-0.00192],"force_p95":0.13462,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12292,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49893,-0.00692,0.22471]},{"body_a":"world","body_b":"grasp_target","contact_count":1316.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50643,-0.01646,0.09983]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5134.0,"contact_point_centroid":[0.5081,0.00061,0.0453],"force_p95":0.07892,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08095,"mean_force":0.04413,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.5079,-0.01871,0.04341]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1383.0,"contact_point_centroid":[0.57878,0.17411,0.26331],"force_p95":0.01243,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01622,"mean_force":0.01061,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57821,0.17409,0.26111]}],"total_contact_groups":14},"final_pose_error":0.00999,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.57445,0.18386,0.01602],"final_tcp_position":[0.58288,0.18385,0.26218],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":1.96436,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":415.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1656.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.49968,-0.0142,0.14906],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12312,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":329.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1316.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_at_object","tcp_end":[0.516,-0.01884,0.05262],"tcp_start":[0.49968,-0.0142,0.14906],"tcp_to_object_dist_end":0.02943,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50362,-0.01775,0.02503],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31435,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.1772,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11348.0,"raw_peak_contact_force":0.24973,"subtask_id":"grasp_at_object","tcp_end":[0.50787,-0.01871,0.04336],"tcp_start":[0.516,-0.01884,0.05262],"tcp_to_object_dist_end":0.01885,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":358.0,"n_steps_budget":600.0,"object_pos_end":[0.50645,-0.01738,0.14173],"object_pos_start":[0.50362,-0.01775,0.02503],"object_to_goal_dist_end":0.24443,"object_to_goal_dist_start":0.31435,"object_z_max":0.14146,"peak_contact_force":0.08454,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":14202.0,"raw_peak_contact_force":0.59918,"subtask_id":"lift_clearance","tcp_end":[0.50062,-0.01777,0.16311],"tcp_start":[0.50787,-0.01871,0.04336],"tcp_to_object_dist_end":0.02217,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":12.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.57002,0.15083,0.22704],"object_pos_start":[0.50645,-0.01738,0.14173],"object_to_goal_dist_end":0.0455,"object_to_goal_dist_start":0.24443,"object_z_max":0.22706,"peak_contact_force":0.40443,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":29768.0,"raw_peak_contact_force":0.40763,"subtask_id":"approach_goal","tcp_end":[0.56771,0.14721,0.26524],"tcp_start":[0.50062,-0.01777,0.16311],"tcp_to_object_dist_end":0.03844,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":468.0,"n_steps_budget":1000.0,"object_pos_end":[0.57445,0.18386,0.01602],"object_pos_start":[0.57002,0.15083,0.22704],"object_to_goal_dist_end":0.23246,"object_to_goal_dist_start":0.0455,"object_z_max":0.22704,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2974.0,"raw_peak_contact_force":1.96436,"subtask_id":"place_at_goal","tcp_end":[0.58288,0.18385,0.26218],"tcp_start":[0.56771,0.14721,0.26524],"tcp_to_object_dist_end":0.2463,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```