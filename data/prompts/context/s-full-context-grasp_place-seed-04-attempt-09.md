## Search State

- **Seed**: 4
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 12 | 0.1540 | 0.81 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 12 | 0.1193 | 0.74 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 12 | -0.0847 | 0.52 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 12 | 0.1427 | 0.95 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 12 | 0.2521 | 1.00 | ✅ accepted |

**Proposal policy**: task_score is 0.81 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.154) — your mutation base

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

- **Composite score**: 0.154
- **task_score** (E): 0.807
- **fitness_score**: 0.874  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.720

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1882 |
| descend_to_grasp | 1.00 | 1.00 | 0.0630 |
| grasp | 1.00 | 1.00 | 0.0126 |
| lift | 1.00 | 1.00 | 0.1061 |
| approach_goal | 0.33 | 1.00 | 0.1392 |
| descend_to_place | 1.00 | 1.00 | 0.0735 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.520, 0.005, 0.115) | (0.526, 0.005, 0.030)→(0.526, 0.005, 0.026) | 0.246→0.249 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.520, 0.005, 0.115)→(0.530, 0.007, 0.053) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.530, 0.007, 0.053)→(0.522, 0.007, 0.044) | (0.526, 0.005, 0.026)→(0.526, 0.006, 0.026) | 0.249→0.248 | 1.00 / 42.000 | 0.151 | 0.189 |
| lift | lift | 1.00 / step_budget | (0.522, 0.007, 0.044)→(0.522, 0.006, 0.150) | (0.526, 0.006, 0.026)→(0.532, 0.006, 0.130) | 0.248→0.202 | 1.00 / 36.000 | 0.084 | 0.556 |
| approach_goal | approach | 0.33 / step_budget | (0.522, 0.006, 0.150)→(0.573, 0.111, 0.210) | (0.532, 0.006, 0.130)→(0.581, 0.110, 0.180) | 0.202→0.076 | 1.00 / 23.333 | 0.161 | 0.205 |
| descend_to_place | descend | 1.00 / step_budget | (0.573, 0.111, 0.210)→(0.606, 0.169, 0.205) | (0.581, 0.110, 0.180)→(0.610, 0.166, 0.143) | 0.076→0.040 | 1.00 / 13.667 | 1.915 | 0.270 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.335
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 1.000
- phase_score: 0.499
- phase_breakdown.approach_goal_score: 0.053
- phase_breakdown.place_at_goal_score: 0.610
- phase_breakdown.grasp_at_object_score: 0.656
- phase_breakdown.reach_pre_grasp_score: 0.468
- phase_breakdown.lift_clearance_score: 0.405
- grasp_place_fitness: 0.979

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.979
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.171
- **K-run variance**: 0.0087
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.351


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.91,"average_solve_count":100.0,"average_success_count":100.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_height":0.12428,"approach_goal.speed":0.12106,"approach_object.approach_height":0.05604,"approach_object.speed":0.23645,"descend_to_grasp.descend_z":0.02,"descend_to_grasp.lateral_offset_x":0.01555,"descend_to_grasp.lateral_offset_y":1e-05,"descend_to_grasp.speed":0.33783,"descend_to_place.place_z_offset":0.03286,"descend_to_place.speed":0.18016,"lift.lift_height":0.12857,"lift.speed":0.20971},"optimized_scores":{"best_composite_score":0.25867,"best_fitness_score":0.97867,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":83.0,"contact_point_centroid":[0.54007,0.00078,-0.00138],"force_p95":0.48541,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65396,"mean_force":0.1161,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.54093,0.00084,0.04063]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6300.0,"contact_point_centroid":[0.53932,0.01999,0.08806],"force_p95":0.07481,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37369,"mean_force":0.0523,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.53929,0.00083,0.08616]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6300.0,"contact_point_centroid":[0.53934,-0.01831,0.08806],"force_p95":0.07459,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35571,"mean_force":0.05215,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.53929,0.00083,0.08616]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13669.0,"contact_point_centroid":[0.6133,0.09066,0.20452],"force_p95":0.11457,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18828,"mean_force":0.07228,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60965,0.10936,0.20435]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13348.0,"contact_point_centroid":[0.61311,0.12687,0.20466],"force_p95":0.11392,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18264,"mean_force":0.07323,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60878,0.10817,0.20406]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54429,0.0011,-0.00204],"force_p95":0.13301,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15008,"mean_force":0.12603,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.54342,0.00089,0.04057]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18674.0,"contact_point_centroid":[0.55902,0.01395,0.16755],"force_p95":0.07958,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14158,"mean_force":0.05307,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55844,0.03299,0.16577]},{"body_a":"world","body_b":"grasp_target","contact_count":2284.0,"contact_point_centroid":[0.54431,0.00113,-0.00194],"force_p95":0.13153,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12284,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51744,0.0005,0.19524]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18202.0,"contact_point_centroid":[0.55872,0.05154,0.16712],"force_p95":0.07972,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13179,"mean_force":0.05435,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55807,0.03246,0.16517]},{"body_a":"world","body_b":"grasp_target","contact_count":752.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.5426,0.001,0.0698]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4841.0,"contact_point_centroid":[0.54227,-0.01832,0.04099],"force_p95":0.06847,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10478,"mean_force":0.0448,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.54219,0.00087,0.03908]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4884.0,"contact_point_centroid":[0.54225,0.02008,0.04098],"force_p95":0.06862,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08738,"mean_force":0.04472,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.54219,0.00087,0.03908]}],"total_contact_groups":12},"final_pose_error":0.01442,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.64429,0.15114,0.18026],"final_tcp_position":[0.64018,0.15131,0.21364],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":0.65396,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":572.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2284.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.53713,0.001,0.09272],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.06708,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":188.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":752.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_at_object","tcp_end":[0.55053,0.00103,0.0493],"tcp_start":[0.53713,0.001,0.09272],"tcp_to_object_dist_end":0.0241,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54418,0.00093,0.02582],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25043,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.13222,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11525.0,"raw_peak_contact_force":0.15008,"subtask_id":"grasp_at_object","tcp_end":[0.54216,0.00087,0.03904],"tcp_start":[0.55053,0.00103,0.0493],"tcp_to_object_dist_end":0.01338,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":315.0,"n_steps_budget":600.0,"object_pos_end":[0.54842,0.00091,0.12018],"object_pos_start":[0.54418,0.00093,0.02582],"object_to_goal_dist_end":0.19893,"object_to_goal_dist_start":0.25043,"object_z_max":0.11992,"peak_contact_force":0.07114,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":12683.0,"raw_peak_contact_force":0.65396,"subtask_id":"lift_clearance","tcp_end":[0.54003,0.00087,0.13495],"tcp_start":[0.54216,0.00087,0.03904],"tcp_to_object_dist_end":0.01698,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.59013,0.06407,0.17911],"object_pos_start":[0.54842,0.00091,0.12018],"object_to_goal_dist_end":0.11085,"object_to_goal_dist_start":0.19893,"object_z_max":0.17903,"peak_contact_force":0.08874,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":36876.0,"raw_peak_contact_force":0.14158,"subtask_id":"approach_goal","tcp_end":[0.57985,0.064,0.20061],"tcp_start":[0.54003,0.00087,0.13495],"tcp_to_object_dist_end":0.02383,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":21.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.64429,0.15114,0.18026],"object_pos_start":[0.59013,0.06407,0.17911],"object_to_goal_dist_end":0.0133,"object_to_goal_dist_start":0.11085,"object_z_max":0.18025,"peak_contact_force":0.11889,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":27017.0,"raw_peak_contact_force":0.18828,"subtask_id":"place_at_goal","tcp_end":[0.64018,0.15131,0.21364],"tcp_start":[0.57985,0.064,0.20061],"tcp_to_object_dist_end":0.03364,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.90476,"average_solve_count":105.0,"average_success_count":105.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_height":0.0648,"approach_goal.speed":0.26613,"approach_object.approach_height":0.05634,"approach_object.speed":0.36037,"descend_to_grasp.descend_z":0.0231,"descend_to_grasp.lateral_offset_x":0.00497,"descend_to_grasp.lateral_offset_y":0.00607,"descend_to_grasp.speed":0.45105,"descend_to_place.place_z_offset":0.02871,"descend_to_place.speed":0.17153,"lift.lift_height":0.1549,"lift.speed":0.117},"optimized_scores":{"best_composite_score":0.03262,"best_fitness_score":0.75262,"best_task_score":0.57648},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":87.0,"contact_point_centroid":[0.52788,0.03402,-0.00158],"force_p95":0.37173,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.50738,"mean_force":0.07964,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51906,0.03371,0.0474]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":65.0,"contact_point_centroid":[0.59078,0.18486,0.15727],"force_p95":0.34813,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.40391,"mean_force":0.19286,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59246,0.16765,0.16322]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6647.0,"contact_point_centroid":[0.52215,0.05228,0.10416],"force_p95":0.09448,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33228,"mean_force":0.06122,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52121,0.03311,0.10283]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7628.0,"contact_point_centroid":[0.52169,0.01413,0.10348],"force_p95":0.08809,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32379,"mean_force":0.05499,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52115,0.03312,0.1018]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10820.0,"contact_point_centroid":[0.55888,0.11467,0.15793],"force_p95":0.13424,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32324,"mean_force":0.09058,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55548,0.09616,0.15981]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":282.0,"contact_point_centroid":[0.59503,0.15237,0.15559],"force_p95":0.15739,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28345,"mean_force":0.08086,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59253,0.16819,0.16072]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53058,0.03099,-0.00226],"force_p95":0.19107,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2503,"mean_force":0.14079,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52127,0.03393,0.04705]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12342.0,"contact_point_centroid":[0.55881,0.07827,0.1585],"force_p95":0.13088,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23429,"mean_force":0.08145,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55573,0.09664,0.15984]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4064.0,"contact_point_centroid":[0.521,0.05305,0.04697],"force_p95":0.08493,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15698,"mean_force":0.05216,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.5201,0.03383,0.04568]},{"body_a":"world","body_b":"grasp_target","contact_count":2244.0,"contact_point_centroid":[0.5305,0.03079,-0.00194],"force_p95":0.13153,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12284,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51101,0.01417,0.19585]},{"body_a":"world","body_b":"grasp_target","contact_count":576.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52515,0.0313,0.07406]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5141.0,"contact_point_centroid":[0.52018,0.0146,0.04752],"force_p95":0.07766,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08102,"mean_force":0.04361,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52011,0.03384,0.04569]}],"total_contact_groups":12},"final_pose_error":0.00993,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.59727,0.16308,0.02705],"final_tcp_position":[0.59468,0.17308,0.14142],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":5.51166,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":562.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2244.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.52419,0.02861,0.09358],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.06789,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":144.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":576.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_at_object","tcp_end":[0.52813,0.03439,0.05519],"tcp_start":[0.52419,0.02861,0.09358],"tcp_to_object_dist_end":0.02948,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53048,0.03287,0.0251],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18212,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.18369,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11005.0,"raw_peak_contact_force":0.2503,"subtask_id":"grasp_at_object","tcp_end":[0.52007,0.03383,0.04565],"tcp_start":[0.52813,0.03439,0.05519],"tcp_to_object_dist_end":0.02305,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":31.0,"n_steps":379.0,"n_steps_budget":750.0,"object_pos_end":[0.5401,0.03224,0.13802],"object_pos_start":[0.53048,0.03287,0.0251],"object_to_goal_dist_end":0.16151,"object_to_goal_dist_start":0.18212,"object_z_max":0.13776,"peak_contact_force":0.10179,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":14362.0,"raw_peak_contact_force":0.50738,"subtask_id":"lift_clearance","tcp_end":[0.52581,0.03269,0.16081],"tcp_start":[0.52007,0.03383,0.04565],"tcp_to_object_dist_end":0.02691,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":15.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.59532,0.16517,0.12636],"object_pos_start":[0.5401,0.03224,0.13802],"object_to_goal_dist_end":0.0235,"object_to_goal_dist_start":0.16151,"object_z_max":0.13825,"peak_contact_force":0.27784,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":23162.0,"raw_peak_contact_force":0.32324,"subtask_id":"approach_goal","tcp_end":[0.59252,0.16717,0.16428],"tcp_start":[0.52581,0.03269,0.16081],"tcp_to_object_dist_end":0.03807,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":82.0,"n_steps_budget":1000.0,"object_pos_end":[0.59727,0.16308,0.02705],"object_pos_start":[0.59532,0.16517,0.12636],"object_to_goal_dist_end":0.08262,"object_to_goal_dist_start":0.0235,"object_z_max":0.12636,"peak_contact_force":5.51166,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":347.0,"raw_peak_contact_force":0.40391,"subtask_id":"place_at_goal","tcp_end":[0.59468,0.17308,0.14142],"tcp_start":[0.59252,0.16717,0.16428],"tcp_to_object_dist_end":0.11484,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.26168,"average_solve_count":107.0,"average_success_count":107.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_height":0.11084,"approach_goal.speed":0.2019,"approach_object.approach_height":0.12025,"approach_object.speed":0.20719,"descend_to_grasp.descend_z":0.02156,"descend_to_grasp.lateral_offset_x":0.01392,"descend_to_grasp.lateral_offset_y":0.00019,"descend_to_grasp.speed":0.27559,"descend_to_place.place_z_offset":0.01975,"descend_to_place.speed":0.16254,"lift.lift_height":0.14672,"lift.speed":0.09581},"optimized_scores":{"best_composite_score":0.17086,"best_fitness_score":0.89086,"best_task_score":0.84492},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":80.0,"contact_point_centroid":[0.50093,-0.01491,-0.00142],"force_p95":0.37053,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.50638,"mean_force":0.08347,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.50221,-0.01517,0.04757]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5865.0,"contact_point_centroid":[0.50077,0.00405,0.1005],"force_p95":0.08942,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35011,"mean_force":0.0607,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49989,-0.01511,0.0988]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6900.0,"contact_point_centroid":[0.49993,-0.03411,0.1004],"force_p95":0.08192,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32869,"mean_force":0.05278,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49989,-0.01511,0.0988]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6758.0,"contact_point_centroid":[0.56995,0.1271,0.25733],"force_p95":0.12616,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2181,"mean_force":0.10036,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.56528,0.14534,0.25966]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7311.0,"contact_point_centroid":[0.56955,0.16354,0.25688],"force_p95":0.1241,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20456,"mean_force":0.09349,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.56525,0.14528,0.25966]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5038,-0.01558,-0.00205],"force_p95":0.13756,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1672,"mean_force":0.12703,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.5045,-0.01518,0.04735]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18069.0,"contact_point_centroid":[0.52177,0.02135,0.20506],"force_p95":0.08898,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15113,"mean_force":0.05486,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5207,0.04033,0.20407]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17158.0,"contact_point_centroid":[0.52293,0.06174,0.20719],"force_p95":0.08585,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15087,"mean_force":0.05749,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52171,0.04269,0.20642]},{"body_a":"world","body_b":"grasp_target","contact_count":1564.0,"contact_point_centroid":[0.50382,-0.01567,-0.00191],"force_p95":0.13468,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12294,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49897,-0.00687,0.22957]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4111.0,"contact_point_centroid":[0.50427,0.00404,0.04787],"force_p95":0.07726,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13127,"mean_force":0.05199,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50335,-0.01517,0.04608]},{"body_a":"world","body_b":"grasp_target","contact_count":1352.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50415,-0.01466,0.10622]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4897.0,"contact_point_centroid":[0.50343,-0.03424,0.04775],"force_p95":0.06907,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0866,"mean_force":0.04451,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50336,-0.01517,0.04608]}],"total_contact_groups":12},"final_pose_error":0.00998,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.58732,0.18343,0.22317],"final_tcp_position":[0.58263,0.18345,0.25978],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":0.50638,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":392.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1564.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.49979,-0.01411,0.15898],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13303,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":338.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1352.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_at_object","tcp_end":[0.51124,-0.01527,0.05502],"tcp_start":[0.49979,-0.01411,0.15898],"tcp_to_object_dist_end":0.02994,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50371,-0.01518,0.02578],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31212,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13571,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10808.0,"raw_peak_contact_force":0.1672,"subtask_id":"grasp_at_object","tcp_end":[0.50333,-0.01517,0.04605],"tcp_start":[0.51124,-0.01527,0.05502],"tcp_to_object_dist_end":0.02027,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":345.0,"n_steps_budget":840.0,"object_pos_end":[0.50778,-0.01517,0.13256],"object_pos_start":[0.50371,-0.01518,0.02578],"object_to_goal_dist_end":0.24631,"object_to_goal_dist_start":0.31212,"object_z_max":0.13228,"peak_contact_force":0.07997,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":12845.0,"raw_peak_contact_force":0.50638,"subtask_id":"lift_clearance","tcp_end":[0.5,-0.0151,0.15312],"tcp_start":[0.50333,-0.01517,0.04605],"tcp_to_object_dist_end":0.02198,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55636,0.10113,0.23602],"object_pos_start":[0.50778,-0.01517,0.13256],"object_to_goal_dist_end":0.09236,"object_to_goal_dist_start":0.24631,"object_z_max":0.23594,"peak_contact_force":0.115,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":35227.0,"raw_peak_contact_force":0.15113,"subtask_id":"approach_goal","tcp_end":[0.54724,0.101,0.26496],"tcp_start":[0.5,-0.0151,0.15312],"tcp_to_object_dist_end":0.03034,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":750.0,"n_steps_budget":1000.0,"object_pos_end":[0.58732,0.18343,0.22317],"object_pos_start":[0.55636,0.10113,0.23602],"object_to_goal_dist_end":0.02528,"object_to_goal_dist_start":0.09236,"object_z_max":0.23603,"peak_contact_force":0.11557,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":14069.0,"raw_peak_contact_force":0.2181,"subtask_id":"place_at_goal","tcp_end":[0.58263,0.18345,0.25978],"tcp_start":[0.54724,0.101,0.26496],"tcp_to_object_dist_end":0.03691,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```