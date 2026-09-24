## Search State

- **Seed**: 4
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 12 | 0.2195 | 0.93 | ✅ accepted |
| 1 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 14 | -0.2274 | 0.36 | ✅ accepted |
| 0 | push → align → release → insert → lift | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | admittance_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.0580 | 0.20 | ✅ accepted |

**Proposal policy**: task_score is near-perfect (0.93). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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

## Current Skill (Q=0.220) — your mutation base

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

- **Composite score**: 0.220
- **task_score** (E): 0.934
- **fitness_score**: 0.940  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.720

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1770 |
| descend_to_grasp | 1.00 | 1.00 | 0.0757 |
| grasp | 1.00 | 1.00 | 0.0127 |
| lift | 1.00 | 1.00 | 0.1267 |
| approach_goal | 0.67 | 1.00 | 0.1508 |
| descend_to_place | 1.00 | 0.67 | 0.0610 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.520, 0.005, 0.127) | (0.526, 0.005, 0.030)→(0.526, 0.005, 0.026) | 0.246→0.249 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.520, 0.005, 0.127)→(0.535, 0.006, 0.053) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.535, 0.006, 0.053)→(0.527, 0.006, 0.043) | (0.526, 0.005, 0.026)→(0.526, 0.006, 0.025) | 0.249→0.249 | 1.00 / 44.000 | 0.154 | 0.205 |
| lift | lift | 1.00 / step_budget | (0.527, 0.006, 0.043)→(0.523, 0.006, 0.169) | (0.526, 0.006, 0.025)→(0.531, 0.006, 0.149) | 0.249→0.198 | 1.00 / 38.000 | 0.078 | 0.603 |
| approach_goal | approach | 0.67 / step_budget | (0.523, 0.006, 0.169)→(0.581, 0.129, 0.229) | (0.531, 0.006, 0.149)→(0.586, 0.129, 0.199) | 0.198→0.063 | 1.00 / 26.667 | 0.103 | 0.178 |
| descend_to_place | descend | 1.00 / step_budget | (0.581, 0.129, 0.229)→(0.606, 0.168, 0.204) | (0.586, 0.129, 0.199)→(0.607, 0.171, 0.166) | 0.063→0.020 | 0.67 / 18.000 | 0.066 | 0.275 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.111
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 1.000
- phase_score: 0.612
- phase_breakdown.approach_goal_score: 0.065
- phase_breakdown.place_at_goal_score: 0.683
- phase_breakdown.grasp_at_object_score: 0.682
- phase_breakdown.reach_pre_grasp_score: 0.587
- phase_breakdown.lift_clearance_score: 0.734
- grasp_place_fitness: 0.976

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.976
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.251
- **K-run variance**: 0.0023
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.385


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.0084,"average_solve_count":119.0,"average_success_count":119.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_height":0.10465,"approach_goal.speed":0.1077,"approach_object.approach_height":0.06728,"approach_object.speed":0.11108,"descend_to_grasp.descend_z":0.02099,"descend_to_grasp.lateral_offset_x":0.01653,"descend_to_grasp.lateral_offset_y":-0.00036,"descend_to_grasp.speed":0.16527,"descend_to_place.place_z_offset":0.02653,"descend_to_place.speed":0.22291,"lift.lift_height":0.15892,"lift.speed":0.26082},"optimized_scores":{"best_composite_score":0.25593,"best_fitness_score":0.97593,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":82.0,"contact_point_centroid":[0.54081,0.00044,-0.00143],"force_p95":0.47911,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62211,"mean_force":0.10645,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.54218,0.00055,0.04254]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7600.0,"contact_point_centroid":[0.54011,0.01974,0.10391],"force_p95":0.07508,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36808,"mean_force":0.05204,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.54009,0.00059,0.10201]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7600.0,"contact_point_centroid":[0.54013,-0.01856,0.10391],"force_p95":0.07446,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35152,"mean_force":0.05182,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.54009,0.00059,0.10201]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54429,0.00107,-0.00206],"force_p95":0.13853,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16931,"mean_force":0.12752,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.54468,0.0006,0.04244]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15187.0,"contact_point_centroid":[0.61329,0.12967,0.20686],"force_p95":0.09054,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16313,"mean_force":0.06271,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61104,0.11091,0.20766]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13461.0,"contact_point_centroid":[0.61406,0.09274,0.20689],"force_p95":0.09789,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16069,"mean_force":0.07053,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61156,0.11164,0.20766]},{"body_a":"world","body_b":"grasp_target","contact_count":2540.0,"contact_point_centroid":[0.54431,0.00113,-0.00194],"force_p95":0.13053,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12282,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51743,0.0005,0.20099]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18402.0,"contact_point_centroid":[0.56115,0.01576,0.18943],"force_p95":0.08219,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13812,"mean_force":0.05398,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.56046,0.0349,0.18724]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20523.0,"contact_point_centroid":[0.56171,0.05476,0.18981],"force_p95":0.07305,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12846,"mean_force":0.04886,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.56098,0.03569,0.18785]},{"body_a":"world","body_b":"grasp_target","contact_count":844.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.54322,0.00086,0.07658]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4834.0,"contact_point_centroid":[0.54353,-0.01861,0.04286],"force_p95":0.06943,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10971,"mean_force":0.04477,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.54345,0.00058,0.04095]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4904.0,"contact_point_centroid":[0.54352,0.01979,0.04285],"force_p95":0.06972,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08816,"mean_force":0.04473,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.54346,0.00058,0.04095]}],"total_contact_groups":12},"final_pose_error":0.01212,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.64162,0.15352,0.175],"final_tcp_position":[0.64137,0.15322,0.20847],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":0.62211,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":636.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2540.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.53727,0.001,0.10433],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.07863,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":211.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":844.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_at_object","tcp_end":[0.55179,0.00074,0.05123],"tcp_start":[0.53727,0.001,0.10433],"tcp_to_object_dist_end":0.0263,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54418,0.00072,0.02575],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25061,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.13685,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11538.0,"raw_peak_contact_force":0.16931,"subtask_id":"grasp_at_object","tcp_end":[0.54342,0.00058,0.04091],"tcp_start":[0.55179,0.00074,0.05123],"tcp_to_object_dist_end":0.01519,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":380.0,"n_steps_budget":600.0,"object_pos_end":[0.54992,0.00075,0.14729],"object_pos_start":[0.54418,0.00072,0.02575],"object_to_goal_dist_end":0.19031,"object_to_goal_dist_start":0.25061,"object_z_max":0.14702,"peak_contact_force":0.07173,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":15282.0,"raw_peak_contact_force":0.62211,"subtask_id":"lift_clearance","tcp_end":[0.54057,0.00066,0.165],"tcp_start":[0.54342,0.00058,0.04091],"tcp_to_object_dist_end":0.02003,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":33.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5922,0.0672,0.18912],"object_pos_start":[0.54992,0.00075,0.14729],"object_to_goal_dist_end":0.10647,"object_to_goal_dist_start":0.19031,"object_z_max":0.18909,"peak_contact_force":0.0839,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":38925.0,"raw_peak_contact_force":0.13812,"subtask_id":"approach_goal","tcp_end":[0.58247,0.06708,0.21315],"tcp_start":[0.54057,0.00066,0.165],"tcp_to_object_dist_end":0.02592,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.64162,0.15352,0.175],"object_pos_start":[0.5922,0.0672,0.18912],"object_to_goal_dist_end":0.01778,"object_to_goal_dist_start":0.10647,"object_z_max":0.18912,"peak_contact_force":0.09762,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":28648.0,"raw_peak_contact_force":0.16313,"subtask_id":"place_at_goal","tcp_end":[0.64137,0.15322,0.20847],"tcp_start":[0.58247,0.06708,0.21315],"tcp_to_object_dist_end":0.03348,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.11719,"average_solve_count":128.0,"average_success_count":128.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_height":0.09185,"approach_goal.speed":0.16315,"approach_object.approach_height":0.10086,"approach_object.speed":0.07482,"descend_to_grasp.descend_z":0.02063,"descend_to_grasp.lateral_offset_x":0.01406,"descend_to_grasp.lateral_offset_y":0.00516,"descend_to_grasp.speed":0.40179,"descend_to_place.place_z_offset":0.02841,"descend_to_place.speed":0.14284,"lift.lift_height":0.16152,"lift.speed":0.21176},"optimized_scores":{"best_composite_score":0.25136,"best_fitness_score":0.97136,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":88.0,"contact_point_centroid":[0.52731,0.03363,-0.00166],"force_p95":0.43397,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.59256,"mean_force":0.09297,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52766,0.03382,0.0451]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7671.0,"contact_point_centroid":[0.52606,0.01428,0.10634],"force_p95":0.07982,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35586,"mean_force":0.05153,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52602,0.03327,0.10423]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6409.0,"contact_point_centroid":[0.52674,0.05252,0.10572],"force_p95":0.08594,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34147,"mean_force":0.05947,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52604,0.03328,0.10339]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53049,0.0311,-0.00229],"force_p95":0.19367,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25384,"mean_force":0.143,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53014,0.03405,0.0446]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2321.0,"contact_point_centroid":[0.58855,0.18234,0.16143],"force_p95":0.1171,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23936,"mean_force":0.07739,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.5896,0.1635,0.16264]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2825.0,"contact_point_centroid":[0.58852,0.14499,0.1608],"force_p95":0.10921,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20998,"mean_force":0.06683,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.58963,0.16356,0.16243]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18104.0,"contact_point_centroid":[0.55621,0.1161,0.17581],"force_p95":0.08289,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15142,"mean_force":0.05512,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55638,0.09693,0.17513]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20312.0,"contact_point_centroid":[0.55557,0.07733,0.17572],"force_p95":0.07535,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14395,"mean_force":0.04988,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5561,0.09636,0.17502]},{"body_a":"world","body_b":"grasp_target","contact_count":2184.0,"contact_point_centroid":[0.5305,0.03079,-0.00193],"force_p95":0.13205,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12285,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51078,0.01387,0.21832]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4346.0,"contact_point_centroid":[0.52933,0.0532,0.04623],"force_p95":0.08191,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12987,"mean_force":0.04891,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52895,0.03395,0.04319]},{"body_a":"world","body_b":"grasp_target","contact_count":1148.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52931,0.03123,0.09464]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5145.0,"contact_point_centroid":[0.52905,0.01461,0.04513],"force_p95":0.07854,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08128,"mean_force":0.04432,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52896,0.03395,0.0432]}],"total_contact_groups":12},"final_pose_error":0.00999,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.59567,0.17236,0.10873],"final_tcp_position":[0.59437,0.17239,0.13967],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":0.59256,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":547.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2184.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.52418,0.02817,0.13813],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11232,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":287.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1148.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_at_object","tcp_end":[0.53714,0.03455,0.05305],"tcp_start":[0.52418,0.02817,0.13813],"tcp_to_object_dist_end":0.02808,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53037,0.03307,0.02498],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18206,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.18151,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11291.0,"raw_peak_contact_force":0.25384,"subtask_id":"grasp_at_object","tcp_end":[0.52893,0.03395,0.04316],"tcp_start":[0.53714,0.03455,0.05305],"tcp_to_object_dist_end":0.01825,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":371.0,"n_steps_budget":600.0,"object_pos_end":[0.53676,0.03258,0.14607],"object_pos_start":[0.53037,0.03307,0.02498],"object_to_goal_dist_end":0.16417,"object_to_goal_dist_start":0.18206,"object_z_max":0.14579,"peak_contact_force":0.0821,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":14168.0,"raw_peak_contact_force":0.59256,"subtask_id":"lift_clearance","tcp_end":[0.5268,0.03289,0.16694],"tcp_start":[0.52893,0.03395,0.04316],"tcp_to_object_dist_end":0.02313,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58779,0.15548,0.15759],"object_pos_start":[0.53676,0.03258,0.14607],"object_to_goal_dist_end":0.05633,"object_to_goal_dist_start":0.16417,"object_z_max":0.15758,"peak_contact_force":0.09899,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":38416.0,"raw_peak_contact_force":0.15142,"subtask_id":"approach_goal","tcp_end":[0.58679,0.15556,0.1874],"tcp_start":[0.5268,0.03289,0.16694],"tcp_to_object_dist_end":0.02982,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":179.0,"n_steps_budget":1000.0,"object_pos_end":[0.59567,0.17236,0.10873],"object_pos_start":[0.58779,0.15548,0.15759],"object_to_goal_dist_end":0.00857,"object_to_goal_dist_start":0.05633,"object_z_max":0.15759,"peak_contact_force":0.10179,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5146.0,"raw_peak_contact_force":0.23936,"subtask_id":"place_at_goal","tcp_end":[0.59437,0.17239,0.13967],"tcp_start":[0.58679,0.15556,0.1874],"tcp_to_object_dist_end":0.03097,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.28283,"average_solve_count":99.0,"average_success_count":99.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_height":0.05978,"approach_goal.speed":0.27577,"approach_object.approach_height":0.09871,"approach_object.speed":0.49158,"descend_to_grasp.descend_z":0.02124,"descend_to_grasp.lateral_offset_x":0.01993,"descend_to_grasp.lateral_offset_y":-0.00149,"descend_to_grasp.speed":0.10882,"descend_to_place.place_z_offset":0.01786,"descend_to_place.speed":0.14462,"lift.lift_height":0.17015,"lift.speed":0.39132},"optimized_scores":{"best_composite_score":0.15123,"best_fitness_score":0.87123,"best_task_score":0.80261},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":82.0,"contact_point_centroid":[0.50036,-0.01641,-0.00149],"force_p95":0.42327,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.59523,"mean_force":0.10855,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.50686,-0.01659,0.04617]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":735.0,"contact_point_centroid":[0.57718,0.1503,0.27204],"force_p95":0.2465,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.42377,"mean_force":0.1281,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57633,0.16862,0.2771]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7858.0,"contact_point_centroid":[0.50281,0.00264,0.11014],"force_p95":0.07844,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37373,"mean_force":0.05098,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.50274,-0.01641,0.10822]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6805.0,"contact_point_centroid":[0.50229,-0.03562,0.10893],"force_p95":0.08732,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34608,"mean_force":0.05788,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.5028,-0.01641,0.10712]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1049.0,"contact_point_centroid":[0.57845,0.18778,0.27033],"force_p95":0.1276,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2824,"mean_force":0.08325,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57692,0.17014,0.27518]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13361.0,"contact_point_centroid":[0.53031,0.04258,0.2199],"force_p95":0.11499,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24589,"mean_force":0.07237,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53099,0.06154,0.22093]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15999.0,"contact_point_centroid":[0.53107,0.08081,0.22047],"force_p95":0.10498,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23367,"mean_force":0.06099,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53123,0.06211,0.22128]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50378,-0.01574,-0.00209],"force_p95":0.14589,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1917,"mean_force":0.12965,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50933,-0.01662,0.04568]},{"body_a":"world","body_b":"grasp_target","contact_count":1756.0,"contact_point_centroid":[0.50382,-0.01567,-0.00192],"force_p95":0.13372,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1229,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49887,-0.007,0.21853]},{"body_a":"world","body_b":"grasp_target","contact_count":1192.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50654,-0.01547,0.09447]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4850.0,"contact_point_centroid":[0.50821,-0.0358,0.04631],"force_p95":0.0705,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11748,"mean_force":0.0446,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50818,-0.0166,0.04438]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4932.0,"contact_point_centroid":[0.50824,0.00262,0.04629],"force_p95":0.07097,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07143,"mean_force":0.04467,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50818,-0.0166,0.04438]}],"total_contact_groups":12},"final_pose_error":0.00994,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.58316,0.18573,0.21539],"final_tcp_position":[0.58092,0.1797,0.26424],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":0.59523,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":440.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1756.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.49966,-0.01428,0.13762],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11169,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":298.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1192.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_at_object","tcp_end":[0.51611,-0.01672,0.05344],"tcp_start":[0.49966,-0.01428,0.13762],"tcp_to_object_dist_end":0.03007,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50368,-0.01631,0.02565],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31295,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.14248,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11582.0,"raw_peak_contact_force":0.1917,"subtask_id":"grasp_at_object","tcp_end":[0.50815,-0.0166,0.04434],"tcp_start":[0.51611,-0.01672,0.05344],"tcp_to_object_dist_end":0.01922,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":378.0,"n_steps_budget":600.0,"object_pos_end":[0.50688,-0.01622,0.15429],"object_pos_start":[0.50368,-0.01631,0.02565],"object_to_goal_dist_end":0.23809,"object_to_goal_dist_start":0.31295,"object_z_max":0.15401,"peak_contact_force":0.08161,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":14745.0,"raw_peak_contact_force":0.59523,"subtask_id":"lift_clearance","tcp_end":[0.5009,-0.01626,0.1762],"tcp_start":[0.50815,-0.0166,0.04434],"tcp_to_object_dist_end":0.02271,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":20.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.57814,0.16414,0.25007],"object_pos_start":[0.50688,-0.01622,0.15429],"object_to_goal_dist_end":0.02498,"object_to_goal_dist_start":0.23809,"object_z_max":0.24992,"peak_contact_force":0.126,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":29360.0,"raw_peak_contact_force":0.24589,"subtask_id":"approach_goal","tcp_end":[0.57454,0.16289,0.28504],"tcp_start":[0.5009,-0.01626,0.1762],"tcp_to_object_dist_end":0.03518,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":119.0,"n_steps_budget":1000.0,"object_pos_end":[0.58316,0.18573,0.21539],"object_pos_start":[0.57814,0.16414,0.25007],"object_to_goal_dist_end":0.03298,"object_to_goal_dist_start":0.02498,"object_z_max":0.25013,"peak_contact_force":0.0,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1784.0,"raw_peak_contact_force":0.42377,"subtask_id":"place_at_goal","tcp_end":[0.58092,0.1797,0.26424],"tcp_start":[0.57454,0.16289,0.28504],"tcp_to_object_dist_end":0.04927,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```