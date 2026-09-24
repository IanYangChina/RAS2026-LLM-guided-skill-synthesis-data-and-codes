## Search State

- **Seed**: 4
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.0742 | 0.21 | ✅ accepted |
| 6 | push → align → release → insert → lift | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | admittance_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.0580 | 0.20 | ❌ rejected |
| 5 | push → align → release → insert → lift | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | admittance_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.0580 | 0.20 | ❌ rejected |
| 4 | push → align → release → insert → lift | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | admittance_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.0580 | 0.20 | ❌ rejected |
| 3 | push → align → release → insert → lift | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | admittance_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.0580 | 0.20 | ❌ rejected |

**Proposal policy**: task_score is 0.21 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.074) — your mutation base

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
  subtask_id: approach_object
- id: descend_to_grasp
  type: descend
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
      distance: 0.08
      axis: world_z
      mode: replace_offset_projection
      sign: negative
    tolerance: 0.015
    orientation:
      mode: keep_current
  parameters:
    descend_distance:
      type: scalar
      range:
      - 0.04
      - 0.12
      default: 0.08
      binds_to:
      - path: target.offset_along_axis.distance
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
    tolerance: 0.015
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
- id: release_object
  type: release
  control: position_control
  termination: pose_tolerance
  end_effector_action: open
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
- id: retract_after_place
  type: retract
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
      distance: 0.1
      axis: world_z
      mode: replace_offset_projection
      sign: positive
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.12], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.08, mode=replace_offset_projection, sign=negative}, tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
- **grasp_object** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **lift_object** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.15, mode=replace_offset_projection, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
- **transport_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_height: status=consumed; consumers=target.offset.z (replace)
- **descend_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.02], tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_height: status=consumed; consumers=target.offset.z (replace)
- **release_object** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **retract_after_place** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.1, mode=replace_offset_projection, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_height: status=consumed; consumers=target.offset_along_axis.distance (replace)

## Design Metrics

- **Composite score**: -0.074
- **task_score** (E): 0.211
- **fitness_score**: 0.406  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.480

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1638 |
| descend_to_grasp | 1.00 | 1.00 | 0.1031 |
| grasp_object | 1.00 | 1.00 | 0.0129 |
| lift_object | 1.00 | 1.00 | 0.1498 |
| transport_to_goal | 1.00 | 1.00 | 0.2443 |
| descend_to_place | 1.00 | 1.00 | 0.1061 |
| release_object | 1.00 | 1.00 | 0.0200 |
| retract_after_place | 1.00 | 1.00 | 0.0971 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.520, 0.005, 0.140) | (0.526, 0.005, 0.030)→(0.526, 0.005, 0.026) | 0.246→0.249 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.520, 0.005, 0.140)→(0.515, 0.005, 0.037) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_object | grasp | 1.00 / step_budget | (0.515, 0.005, 0.037)→(0.507, 0.004, 0.027) | (0.526, 0.005, 0.026)→(0.526, 0.004, 0.025) | 0.249→0.250 | 1.00 / 32.333 | 0.162 | 0.252 |
| lift_object | lift | 1.00 / step_budget | (0.507, 0.004, 0.027)→(0.503, 0.004, 0.177) | (0.526, 0.004, 0.025)→(0.536, 0.010, 0.063) | 0.250→0.222 | 1.00 / 11.333 | 3249.685 | 0.945 |
| transport_to_goal | approach | 1.00 / step_budget | (0.503, 0.004, 0.177)→(0.603, 0.162, 0.328) | (0.536, 0.010, 0.063)→(0.539, 0.019, 0.016) | 0.222→0.242 | 1.00 / 8.000 | 6499.247 | 0.658 |
| descend_to_place | descend | 1.00 / step_budget | (0.603, 0.162, 0.328)→(0.608, 0.171, 0.223) | (0.539, 0.019, 0.016)→(0.539, 0.019, 0.016) | 0.242→0.242 | 1.00 / 8.000 | 3249.669 | 0.123 |
| release_object | release | 1.00 / step_budget | (0.608, 0.171, 0.223)→(0.603, 0.170, 0.242) | (0.539, 0.019, 0.016)→(0.539, 0.019, 0.016) | 0.242→0.242 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract_after_place | retract | 1.00 / step_budget | (0.603, 0.170, 0.242)→(0.601, 0.169, 0.339) | (0.539, 0.019, 0.016)→(0.539, 0.019, 0.016) | 0.242→0.242 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.136
- phase_score: 0.305
- phase_breakdown.place_at_goal_score: 0.043
- phase_breakdown.approach_object_score: 0.916
- grasp_place_fitness: 0.538

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.538
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.311
- **Median Q (composite search score)**: -0.109
- **K-run variance**: 0.0094
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.349


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.90625,"average_solve_count":192.0,"average_success_count":192.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.09129,"descend_to_grasp.descend_distance":0.1143,"descend_to_place.place_height":0.0194,"lift_object.lift_height":0.14727,"retract_after_place.retract_height":0.11146,"transport_to_goal.transport_height":0.12949},"optimized_scores":{"best_composite_score":-0.17161,"best_fitness_score":0.30839,"best_task_score":0.18585},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":559.0,"contact_point_centroid":[0.54553,0.00607,-0.00313],"force_p95":0.55694,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.15108,"mean_force":0.17471,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51839,0.00064,0.12319]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2514.0,"contact_point_centroid":[0.52441,-0.01782,0.06327],"force_p95":0.18314,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37321,"mean_force":0.10525,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51825,0.00063,0.06192]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2500.0,"contact_point_centroid":[0.52442,0.01914,0.06233],"force_p95":0.18618,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35113,"mean_force":0.10677,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51829,0.00063,0.0613]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54431,0.00098,-0.00203],"force_p95":0.13422,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16419,"mean_force":0.12535,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52327,0.00072,0.0299]},{"body_a":"world","body_b":"grasp_target","contact_count":1284.0,"contact_point_centroid":[0.54431,0.00113,-0.0019],"force_p95":0.13564,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12301,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51645,0.00045,0.22037]},{"body_a":"world","body_b":"grasp_target","contact_count":3352.0,"contact_point_centroid":[0.54621,0.00716,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12379,"mean_force":0.12264,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.57903,0.07757,0.23008]},{"body_a":"world","body_b":"grasp_target","contact_count":904.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53201,0.00088,0.08858]},{"body_a":"world","body_b":"grasp_target","contact_count":656.0,"contact_point_centroid":[0.54621,0.00716,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.64109,0.15247,0.26589]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.54621,0.00716,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.63939,0.15426,0.22304]},{"body_a":"world","body_b":"grasp_target","contact_count":1504.0,"contact_point_centroid":[0.54621,0.00716,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.63627,0.15322,0.2874]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2901.0,"contact_point_centroid":[0.52721,-0.01815,0.03023],"force_p95":0.09404,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10809,"mean_force":0.0701,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52205,0.0007,0.02853]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3191.0,"contact_point_centroid":[0.52737,0.01946,0.0295],"force_p95":0.08805,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09037,"mean_force":0.06573,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52205,0.0007,0.02853]},{"body_a":"left_finger","body_b":"right_finger","contact_count":137.0,"contact_point_centroid":[0.51848,0.00064,0.15338],"force_p95":0.01569,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01615,"mean_force":0.01245,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51815,0.00064,0.15112]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3586.0,"contact_point_centroid":[0.57964,0.07782,0.23261],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01271,"mean_force":0.01043,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.57923,0.07781,0.23033]},{"body_a":"left_finger","body_b":"right_finger","contact_count":222.0,"contact_point_centroid":[0.64192,0.15498,0.2221],"force_p95":0.01092,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01263,"mean_force":0.01,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.64153,0.15495,0.21973]},{"body_a":"left_finger","body_b":"right_finger","contact_count":707.0,"contact_point_centroid":[0.64168,0.15249,0.26761],"force_p95":0.01093,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01095,"mean_force":0.01036,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.6411,0.15248,0.26561]}],"total_contact_groups":16},"final_pose_error":0.01998,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.54621,0.00716,0.01602],"final_tcp_position":[0.63661,0.15326,0.33378],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":1.15108,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":322.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1284.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.53522,0.00093,0.13859],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11293,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":226.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":904.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53082,0.00085,0.03862],"tcp_start":[0.53522,0.00093,0.13859],"tcp_to_object_dist_end":0.01846,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54417,0.00064,0.0259],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25057,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.13121,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":7892.0,"raw_peak_contact_force":0.16419,"tcp_end":[0.52202,0.0007,0.02849],"tcp_start":[0.53082,0.00085,0.03862],"tcp_to_object_dist_end":0.0223,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":422.0,"n_steps_budget":930.0,"object_pos_end":[0.5462,0.00717,0.01604],"object_pos_start":[0.54417,0.00064,0.0259],"object_to_goal_dist_end":0.25241,"object_to_goal_dist_start":0.25057,"object_z_max":0.08592,"peak_contact_force":0.12383,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":5710.0,"raw_peak_contact_force":1.15108,"tcp_end":[0.51825,0.00064,0.1563],"tcp_start":[0.52202,0.0007,0.02849],"tcp_to_object_dist_end":0.14317,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":838.0,"n_steps_budget":1000.0,"object_pos_end":[0.54621,0.00716,0.01602],"object_pos_start":[0.5462,0.00717,0.01604],"object_to_goal_dist_end":0.25242,"object_to_goal_dist_start":0.25241,"object_z_max":0.01604,"peak_contact_force":0.12263,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":6938.0,"raw_peak_contact_force":0.12379,"subtask_id":"place_at_goal","tcp_end":[0.63976,0.14996,0.30424],"tcp_start":[0.51825,0.00064,0.1563],"tcp_to_object_dist_end":0.33499,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":164.0,"n_steps_budget":1000.0,"object_pos_end":[0.54621,0.00716,0.01602],"object_pos_start":[0.54621,0.00716,0.01602],"object_to_goal_dist_end":0.25242,"object_to_goal_dist_start":0.25242,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1363.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.64317,0.15532,0.22441],"tcp_start":[0.63976,0.14996,0.30424],"tcp_to_object_dist_end":0.27346,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54621,0.00716,0.01602],"object_pos_start":[0.54621,0.00716,0.01602],"object_to_goal_dist_end":0.25242,"object_to_goal_dist_start":0.25242,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1022.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.63816,0.15385,0.24223],"tcp_start":[0.64317,0.15532,0.22441],"tcp_to_object_dist_end":0.28486,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":376.0,"n_steps_budget":720.0,"object_pos_end":[0.54621,0.00716,0.01602],"object_pos_start":[0.54621,0.00716,0.01602],"object_to_goal_dist_end":0.25242,"object_to_goal_dist_start":0.25242,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1504.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.63661,0.15326,0.33378],"tcp_start":[0.63816,0.15385,0.24223],"tcp_to_object_dist_end":0.36123,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.91262,"average_solve_count":206.0,"average_success_count":206.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.08326,"descend_to_grasp.descend_distance":0.11851,"descend_to_place.place_height":0.01539,"lift_object.lift_height":0.20184,"retract_after_place.retract_height":0.11766,"transport_to_goal.transport_height":0.18241},"optimized_scores":{"best_composite_score":-0.10865,"best_fitness_score":0.37135,"best_task_score":0.31073},"replay_outcomes":[{"contacts":{"omitted_contact_groups":2,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1255.0,"contact_point_centroid":[0.55668,0.03474,-0.00247],"force_p95":0.44405,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.19362,"mean_force":0.15172,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.5065,0.02562,0.14502]},{"body_a":"grasp_target","body_b":"hand","contact_count":74.0,"contact_point_centroid":[0.52519,0.04504,0.06487],"force_p95":0.21038,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.50581,"mean_force":0.08971,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.50738,0.02566,0.02707]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2003.0,"contact_point_centroid":[0.51256,0.00695,0.05245],"force_p95":0.19765,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.43013,"mean_force":0.11606,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.50644,0.02561,0.04932]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2935.0,"contact_point_centroid":[0.51195,0.04362,0.05453],"force_p95":0.14071,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.39685,"mean_force":0.09301,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.50629,0.0256,0.05352]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53075,0.02927,-0.0023],"force_p95":0.23944,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.33584,"mean_force":0.1527,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.51135,0.02593,0.0187]},{"body_a":"grasp_target","body_b":"hand","contact_count":321.0,"contact_point_centroid":[0.52775,0.04638,0.05545],"force_p95":0.19467,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21001,"mean_force":0.05378,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.51024,0.02587,0.0175]},{"body_a":"world","body_b":"grasp_target","contact_count":1328.0,"contact_point_centroid":[0.5305,0.03079,-0.0019],"force_p95":0.13564,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12299,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51066,0.0129,0.21666]},{"body_a":"world","body_b":"grasp_target","contact_count":956.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52001,0.02651,0.07911]},{"body_a":"world","body_b":"grasp_target","contact_count":2344.0,"contact_point_centroid":[0.55916,0.03552,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54958,0.09855,0.23708]},{"body_a":"world","body_b":"grasp_target","contact_count":1180.0,"contact_point_centroid":[0.55916,0.03552,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.594,0.17146,0.20777]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.55916,0.03552,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.59148,0.17425,0.1369]},{"body_a":"world","body_b":"grasp_target","contact_count":1488.0,"contact_point_centroid":[0.55916,0.03552,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.58688,0.17271,0.20516]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2271.0,"contact_point_centroid":[0.51558,0.00719,0.01996],"force_p95":0.11309,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12126,"mean_force":0.07819,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.51013,0.02586,0.01738]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3239.0,"contact_point_centroid":[0.51529,0.04531,0.01882],"force_p95":0.10593,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11756,"mean_force":0.07417,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.51016,0.02587,0.01741]},{"body_a":"left_finger","body_b":"right_finger","contact_count":894.0,"contact_point_centroid":[0.50679,0.02562,0.16908],"force_p95":0.01254,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01629,"mean_force":0.01081,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.50645,0.02561,0.16682]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2524.0,"contact_point_centroid":[0.54996,0.09851,0.23931],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01277,"mean_force":0.01036,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54955,0.09849,0.23704]}],"total_contact_groups":18},"final_pose_error":0.02,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.55916,0.03552,0.01602],"final_tcp_position":[0.587,0.1727,0.25457],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":9748.92573,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":333.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1328.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.52328,0.02665,0.13126],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.10557,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":239.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":956.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.51887,0.02638,0.02702],"tcp_start":[0.52328,0.02665,0.13126],"tcp_to_object_dist_end":0.01248,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53062,0.02623,0.02512],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18741,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.18062,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":7631.0,"raw_peak_contact_force":0.33584,"tcp_end":[0.51011,0.02584,0.01735],"tcp_start":[0.51887,0.02638,0.02702],"tcp_to_object_dist_end":0.02194,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":589.0,"n_steps_budget":1000.0,"object_pos_end":[0.55916,0.03552,0.01602],"object_pos_start":[0.53062,0.02623,0.02512],"object_to_goal_dist_end":0.17532,"object_to_goal_dist_start":0.18741,"object_z_max":0.08523,"peak_contact_force":9748.73688,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":7161.0,"raw_peak_contact_force":1.19362,"tcp_end":[0.50679,0.02563,0.19972],"tcp_start":[0.51011,0.02584,0.01735],"tcp_to_object_dist_end":0.19128,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":586.0,"n_steps_budget":1000.0,"object_pos_end":[0.55916,0.03552,0.01602],"object_pos_start":[0.55916,0.03552,0.01602],"object_to_goal_dist_end":0.17532,"object_to_goal_dist_start":0.17532,"object_z_max":0.01602,"peak_contact_force":9748.92573,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4868.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_at_goal","tcp_end":[0.59281,0.16774,0.27649],"tcp_start":[0.50679,0.02563,0.19972],"tcp_to_object_dist_end":0.29404,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":295.0,"n_steps_budget":1000.0,"object_pos_end":[0.55916,0.03552,0.01602],"object_pos_start":[0.55916,0.03552,0.01602],"object_to_goal_dist_end":0.17532,"object_to_goal_dist_start":0.17532,"object_z_max":0.01602,"peak_contact_force":9748.7603,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2433.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.59647,0.1758,0.13687],"tcp_start":[0.59281,0.16774,0.27649],"tcp_to_object_dist_end":0.18888,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.55916,0.03552,0.01602],"object_pos_start":[0.55916,0.03552,0.01602],"object_to_goal_dist_end":0.17532,"object_to_goal_dist_start":0.17532,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1021.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58974,0.17366,0.15669],"tcp_start":[0.59647,0.1758,0.13687],"tcp_to_object_dist_end":0.19952,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":372.0,"n_steps_budget":750.0,"object_pos_end":[0.55916,0.03552,0.01602],"object_pos_start":[0.55916,0.03552,0.01602],"object_to_goal_dist_end":0.17532,"object_to_goal_dist_start":0.17532,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1488.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.587,0.1727,0.25457],"tcp_start":[0.58974,0.17366,0.15669],"tcp_to_object_dist_end":0.27658,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.91469,"average_solve_count":211.0,"average_success_count":211.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.10016,"descend_to_grasp.descend_distance":0.11892,"descend_to_place.place_height":0.0454,"lift_object.lift_height":0.15871,"retract_after_place.retract_height":0.12163,"transport_to_goal.transport_height":0.18679},"optimized_scores":{"best_composite_score":0.05773,"best_fitness_score":0.53773,"best_task_score":0.13625},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3505.0,"contact_point_centroid":[0.51158,0.01466,-0.00228],"force_p95":0.12658,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.72627,"mean_force":0.13668,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53563,0.09119,0.30402]},{"body_a":"world","body_b":"grasp_target","contact_count":82.0,"contact_point_centroid":[0.50181,-0.0123,-0.0015],"force_p95":0.46409,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.49042,"mean_force":0.10457,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48644,-0.01321,0.03732]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4962.0,"contact_point_centroid":[0.48897,0.0056,0.10101],"force_p95":0.1282,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.39599,"mean_force":0.09089,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48422,-0.01317,0.09879]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5765.0,"contact_point_centroid":[0.48889,-0.03168,0.10085],"force_p95":0.11968,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35395,"mean_force":0.0824,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.4842,-0.01317,0.09937]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":189.0,"contact_point_centroid":[0.49171,0.00755,0.17424],"force_p95":0.23966,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31506,"mean_force":0.15897,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.48492,-0.01077,0.17731]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":345.0,"contact_point_centroid":[0.49165,-0.02674,0.17505],"force_p95":0.21409,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28468,"mean_force":0.10855,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.48533,-0.00939,0.17862]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50397,-0.01538,-0.00222],"force_p95":0.18365,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25507,"mean_force":0.13866,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.48894,-0.01323,0.03688]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4019.0,"contact_point_centroid":[0.48953,0.00582,0.03807],"force_p95":0.09735,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15619,"mean_force":0.0571,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.48779,-0.01322,0.03568]},{"body_a":"world","body_b":"grasp_target","contact_count":1140.0,"contact_point_centroid":[0.50382,-0.01567,-0.00188],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12306,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49951,-0.00641,0.22617]},{"body_a":"world","body_b":"grasp_target","contact_count":980.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.49705,-0.01333,0.0969]},{"body_a":"world","body_b":"grasp_target","contact_count":840.0,"contact_point_centroid":[0.51157,0.01469,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.58002,0.17552,0.35723]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.51157,0.01469,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.58108,0.18225,0.30742]},{"body_a":"world","body_b":"grasp_target","contact_count":1512.0,"contact_point_centroid":[0.51157,0.01469,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.57951,0.18141,0.37744]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4692.0,"contact_point_centroid":[0.48968,-0.03229,0.03788],"force_p95":0.0858,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0906,"mean_force":0.04941,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.4878,-0.01322,0.03569]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3506.0,"contact_point_centroid":[0.5384,0.09583,0.3122],"force_p95":0.01104,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01612,"mean_force":0.01051,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53806,0.09582,0.30996]},{"body_a":"left_finger","body_b":"right_finger","contact_count":888.0,"contact_point_centroid":[0.58032,0.17555,0.35935],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01271,"mean_force":0.01054,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.58003,0.17554,0.3571]}],"total_contact_groups":17},"final_pose_error":0.01981,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.51157,0.01469,0.01602],"final_tcp_position":[0.58006,0.1815,0.42903],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":9748.69316,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":286.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1140.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.50015,-0.01334,0.14935],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1234,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":245.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":980.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.496,-0.01329,0.04449],"tcp_start":[0.50015,-0.01334,0.14935],"tcp_to_object_dist_end":0.0202,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50417,-0.01364,0.02522],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.3114,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.17354,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10511.0,"raw_peak_contact_force":0.25507,"tcp_end":[0.48777,-0.01322,0.03565],"tcp_start":[0.496,-0.01329,0.04449],"tcp_to_object_dist_end":0.01945,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":437.0,"n_steps_budget":990.0,"object_pos_end":[0.50185,-0.01315,0.15547],"object_pos_start":[0.50417,-0.01364,0.02522],"object_to_goal_dist_end":0.23677,"object_to_goal_dist_start":0.3114,"object_z_max":0.15523,"peak_contact_force":0.19474,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":10809.0,"raw_peak_contact_force":0.49042,"tcp_end":[0.48429,-0.01316,0.17475],"tcp_start":[0.48777,-0.01322,0.03565],"tcp_to_object_dist_end":0.02608,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51157,0.01469,0.01602],"object_pos_start":[0.50185,-0.01315,0.15547],"object_to_goal_dist_end":0.29898,"object_to_goal_dist_start":0.23677,"object_z_max":0.15858,"peak_contact_force":9748.69316,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7545.0,"raw_peak_contact_force":1.72627,"subtask_id":"place_at_goal","tcp_end":[0.57701,0.16884,0.40419],"tcp_start":[0.48429,-0.01316,0.17475],"tcp_to_object_dist_end":0.42275,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":210.0,"n_steps_budget":1000.0,"object_pos_end":[0.51157,0.01469,0.01602],"object_pos_start":[0.51157,0.01469,0.01602],"object_to_goal_dist_end":0.29898,"object_to_goal_dist_start":0.29898,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1728.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.5835,0.18314,0.30718],"tcp_start":[0.57701,0.16884,0.40419],"tcp_to_object_dist_end":0.34399,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51157,0.01469,0.01602],"object_pos_start":[0.51157,0.01469,0.01602],"object_to_goal_dist_end":0.29898,"object_to_goal_dist_start":0.29898,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1022.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.5804,0.18189,0.32721],"tcp_start":[0.5835,0.18314,0.30718],"tcp_to_object_dist_end":0.35991,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":378.0,"n_steps_budget":780.0,"object_pos_end":[0.51157,0.01469,0.01602],"object_pos_start":[0.51157,0.01469,0.01602],"object_to_goal_dist_end":0.29898,"object_to_goal_dist_start":0.29898,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1512.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58006,0.1815,0.42903],"tcp_start":[0.5804,0.18189,0.32721],"tcp_to_object_dist_end":0.45066,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```