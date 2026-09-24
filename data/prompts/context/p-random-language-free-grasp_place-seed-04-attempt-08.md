## Search State

- **Seed**: 4
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.2972 | 0.19 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.0742 | 0.21 | ✅ accepted |
| 6 | push → align → release → insert → lift | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | admittance_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.0580 | 0.20 | ❌ rejected |
| 5 | push → align → release → insert → lift | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | admittance_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.0580 | 0.20 | ❌ rejected |
| 4 | push → align → release → insert → lift | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | admittance_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.0580 | 0.20 | ❌ rejected |

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

## Current Skill (Q=-0.297) — your mutation base

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

- **Composite score**: -0.297
- **task_score** (E): 0.185
- **fitness_score**: 0.183  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.480

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 0.00 | 1.00 | 0.1210 |
| descend_to_grasp | 0.67 | 1.00 | 0.0355 |
| grasp_object | 1.00 | 1.00 | 0.0010 |
| lift_object | 1.00 | 1.00 | 0.1684 |
| transport_to_goal | 0.00 | 1.00 | 0.1189 |
| descend_to_place | 0.00 | 1.00 | 0.0183 |
| release_object | 1.00 | 1.00 | 0.0219 |
| retract_after_place | 1.00 | 1.00 | 0.0774 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.446, 0.003, 0.193) | (0.526, 0.005, 0.030)→(0.499, 0.011, 0.019) | 0.246→0.261 | 1.00 / 5.000 | 239.177 | 1468.747 |
| descend_to_grasp | descend | 0.67 / step_budget | (0.446, 0.003, 0.193)→(0.466, 0.004, 0.168) | (0.499, 0.011, 0.019)→(0.499, 0.011, 0.019) | 0.261→0.261 | 1.00 / 5.000 | 330.254 | 856.301 |
| grasp_object | grasp | 1.00 / step_budget | (0.466, 0.004, 0.168)→(0.466, 0.005, 0.167) | (0.499, 0.011, 0.019)→(0.499, 0.011, 0.019) | 0.261→0.261 | 1.00 / 9.000 | 66.311 | 225.480 |
| lift_object | lift | 1.00 / step_budget | (0.466, 0.005, 0.167)→(0.464, 0.005, 0.336) | (0.499, 0.011, 0.019)→(0.499, 0.011, 0.019) | 0.261→0.261 | 1.00 / 8.333 | 94251.260 | 203.012 |
| transport_to_goal | approach | 0.00 / step_budget | (0.464, 0.005, 0.336)→(0.530, 0.093, 0.320) | (0.499, 0.011, 0.019)→(0.499, 0.011, 0.019) | 0.261→0.261 | 1.00 / 9.667 | 91182.236 | 428.141 |
| descend_to_place | descend | 0.00 / step_budget | (0.530, 0.093, 0.320)→(0.534, 0.102, 0.305) | (0.499, 0.011, 0.019)→(0.499, 0.011, 0.019) | 0.261→0.261 | 1.00 / 9.667 | 268.231 | 296.017 |
| release_object | release | 1.00 / step_budget | (0.534, 0.102, 0.305)→(0.536, 0.102, 0.327) | (0.499, 0.011, 0.019)→(0.499, 0.011, 0.019) | 0.261→0.261 | 1.00 / 5.333 | 136.213 | 259.393 |
| retract_after_place | retract | 1.00 / step_budget | (0.536, 0.102, 0.327)→(0.537, 0.102, 0.404) | (0.499, 0.011, 0.019)→(0.499, 0.011, 0.019) | 0.261→0.261 | 1.00 / 4.667 | 0.266 | 197.985 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 0.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: None
- terminal_score: 0.265
- phase_score: 0.053
- phase_breakdown.place_at_goal_score: 0.015
- phase_breakdown.approach_object_score: 0.143
- grasp_place_fitness: 0.223

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.223
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.265
- **Median Q (composite search score)**: -0.308
- **K-run variance**: 0.0009
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.359


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":57.0,"average_failure_rate":0.30645,"average_mean_iterations":65.23118,"average_solve_count":186.0,"average_success_count":129.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.12976,"descend_to_grasp.descend_distance":0.04996,"descend_to_place.place_height":0.02943,"lift_object.lift_height":0.15212,"retract_after_place.retract_height":0.14169,"transport_to_goal.transport_height":0.13206},"optimized_scores":{"best_composite_score":-0.30833,"best_fitness_score":0.17167,"best_task_score":0.16687},"replay_outcomes":[{"contacts":{"omitted_contact_groups":10,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":887.0,"contact_point_centroid":[0.64826,0.0014,-0.00046],"force_p95":270.6207,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1523.34291,"mean_force":205.84379,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.42545,0.00027,0.15086]},{"body_a":"world","body_b":"link6","contact_count":544.0,"contact_point_centroid":[0.66682,0.00088,-0.00025],"force_p95":489.7129,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":782.04832,"mean_force":327.78969,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.46326,0.00109,0.18321]},{"body_a":"link5","body_b":"hand","contact_count":242.0,"contact_point_centroid":[0.54744,-0.00782,0.25377],"force_p95":323.81529,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":342.87898,"mean_force":274.15188,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52531,0.06375,0.29203]},{"body_a":"world","body_b":"link7","contact_count":23.0,"contact_point_centroid":[0.53991,0.00358,-0.00392],"force_p95":0.0,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":316.17028,"mean_force":13.74653,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.38906,-6e-05,0.04616]},{"body_a":"link5","body_b":"hand","contact_count":200.0,"contact_point_centroid":[0.54354,0.01646,0.22148],"force_p95":198.56205,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":259.46191,"mean_force":135.58912,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.5398,0.07286,0.29551]},{"body_a":"link5","body_b":"hand","contact_count":2.0,"contact_point_centroid":[0.54353,0.01608,0.22058],"force_p95":228.71611,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":230.14718,"mean_force":215.83646,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.53868,0.07364,0.29306]},{"body_a":"world","body_b":"link6","contact_count":5.0,"contact_point_centroid":[0.68813,-0.00952,-9e-05],"force_p95":210.99757,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":223.83855,"mean_force":131.7589,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46646,0.00489,0.1662]},{"body_a":"link5","body_b":"hand","contact_count":9.0,"contact_point_centroid":[0.54698,0.01697,0.24169],"force_p95":173.82265,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":176.06,"mean_force":130.69233,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.54067,0.07324,0.316]},{"body_a":"world","body_b":"link6","contact_count":450.0,"contact_point_centroid":[0.68803,-0.00956,-0.00013],"force_p95":72.65433,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":97.89568,"mean_force":67.71371,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46646,0.00473,0.16626]},{"body_a":"grasp_target","body_b":"link7","contact_count":274.0,"contact_point_centroid":[0.53095,0.00446,0.03092],"force_p95":2.96646,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.28895,"mean_force":0.50198,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.40439,7e-05,0.10164]},{"body_a":"left_finger","body_b":"link5","contact_count":602.0,"contact_point_centroid":[0.52143,0.04669,0.3465],"force_p95":1.62002,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3.67055,"mean_force":0.57192,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.54147,0.07338,0.37011]},{"body_a":"grasp_target","body_b":"hand","contact_count":96.0,"contact_point_centroid":[0.50244,0.0156,0.04298],"force_p95":2.5139,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.36948,"mean_force":1.02928,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39765,0.0,0.07354]},{"body_a":"world","body_b":"grasp_target","contact_count":3786.0,"contact_point_centroid":[0.51496,0.00726,-0.00229],"force_p95":0.29595,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.08745,"mean_force":0.15767,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.43613,0.00029,0.16049]},{"body_a":"grasp_target","body_b":"link6","contact_count":88.0,"contact_point_centroid":[0.55028,0.01343,0.02552],"force_p95":0.74719,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.79296,"mean_force":0.4131,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39501,-0.0,0.07908]},{"body_a":"world","body_b":"grasp_target","contact_count":2208.0,"contact_point_centroid":[0.50953,0.00838,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.46324,0.00109,0.18327]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50953,0.00838,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46646,0.00473,0.16626]}],"total_contact_groups":26},"final_pose_error":0.01977,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.50953,0.00838,0.01602],"final_tcp_position":[0.54192,0.07296,0.43739],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":9749.35209,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50953,0.00838,0.01602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.26858,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":332.11128,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5154.0,"raw_peak_contact_force":1523.34291,"subtask_id":"approach_object","tcp_end":[0.45838,0.00071,0.20157],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.19263,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":552.0,"n_steps_budget":1000.0,"object_pos_end":[0.50953,0.00838,0.01602],"object_pos_start":[0.50953,0.00838,0.01602],"object_to_goal_dist_end":0.26858,"object_to_goal_dist_start":0.26858,"object_z_max":0.01602,"peak_contact_force":248.6058,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2752.0,"raw_peak_contact_force":782.04832,"tcp_end":[0.46644,0.00447,0.16683],"tcp_start":[0.45838,0.00071,0.20157],"tcp_to_object_dist_end":0.15689,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50953,0.00838,0.01602],"object_pos_start":[0.50953,0.00838,0.01602],"object_to_goal_dist_end":0.26858,"object_to_goal_dist_start":0.26858,"object_z_max":0.01602,"peak_contact_force":66.00371,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":2596.0,"raw_peak_contact_force":97.89568,"tcp_end":[0.46645,0.00476,0.16613],"tcp_start":[0.46644,0.00447,0.16683],"tcp_to_object_dist_end":0.15621,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":432.0,"n_steps_budget":960.0,"object_pos_end":[0.50953,0.00838,0.01602],"object_pos_start":[0.50953,0.00838,0.01602],"object_to_goal_dist_end":0.26858,"object_to_goal_dist_start":0.26858,"object_z_max":0.01602,"peak_contact_force":9749.35209,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":3654.0,"raw_peak_contact_force":223.83855,"tcp_end":[0.46582,0.00471,0.29847],"tcp_start":[0.46645,0.00476,0.16613],"tcp_to_object_dist_end":0.28583,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":655.0,"n_steps_budget":1000.0,"object_pos_end":[0.50953,0.00838,0.01602],"object_pos_start":[0.50953,0.00838,0.01602],"object_to_goal_dist_end":0.26858,"object_to_goal_dist_start":0.26858,"object_z_max":0.01602,"peak_contact_force":252.5369,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5728.0,"raw_peak_contact_force":342.87898,"subtask_id":"place_at_goal","tcp_end":[0.53859,0.07373,0.29294],"tcp_start":[0.46582,0.00471,0.29847],"tcp_to_object_dist_end":0.28601,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.50953,0.00838,0.01602],"object_pos_start":[0.50953,0.00838,0.01602],"object_to_goal_dist_end":0.26858,"object_to_goal_dist_start":0.26858,"object_z_max":0.01602,"peak_contact_force":234.73798,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":19.0,"raw_peak_contact_force":230.14718,"tcp_end":[0.53891,0.07354,0.29324],"tcp_start":[0.53859,0.07373,0.29294],"tcp_to_object_dist_end":0.28629,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50953,0.00838,0.01602],"object_pos_start":[0.50953,0.00838,0.01602],"object_to_goal_dist_end":0.26858,"object_to_goal_dist_start":0.26858,"object_z_max":0.01602,"peak_contact_force":103.17022,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1221.0,"raw_peak_contact_force":259.46191,"tcp_end":[0.54023,0.07303,0.3154],"tcp_start":[0.53891,0.07354,0.29324],"tcp_to_object_dist_end":0.30782,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":438.0,"n_steps_budget":900.0,"object_pos_end":[0.50953,0.00838,0.01602],"object_pos_start":[0.50953,0.00838,0.01602],"object_to_goal_dist_end":0.26858,"object_to_goal_dist_start":0.26858,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2363.0,"raw_peak_contact_force":176.06,"tcp_end":[0.54192,0.07296,0.43739],"tcp_start":[0.54023,0.07303,0.3154],"tcp_to_object_dist_end":0.42752,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":60.0,"average_failure_rate":0.30457,"average_mean_iterations":64.62944,"average_solve_count":197.0,"average_success_count":137.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.09958,"descend_to_grasp.descend_distance":0.07645,"descend_to_place.place_height":0.02871,"lift_object.lift_height":0.22596,"retract_after_place.retract_height":0.09477,"transport_to_goal.transport_height":0.14115},"optimized_scores":{"best_composite_score":-0.25695,"best_fitness_score":0.22305,"best_task_score":0.26515},"replay_outcomes":[{"contacts":{"omitted_contact_groups":11,"reported_contact_groups":[{"body_a":"world","body_b":"link7","contact_count":24.0,"contact_point_centroid":[0.537,0.00791,-0.00346],"force_p95":212.62765,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1351.2206,"mean_force":66.72378,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.38725,0.00385,0.04558]},{"body_a":"world","body_b":"link6","contact_count":887.0,"contact_point_centroid":[0.64609,0.00826,-0.00044],"force_p95":214.59018,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1347.74481,"mean_force":200.74618,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.41761,0.00786,0.141]},{"body_a":"world","body_b":"link6","contact_count":960.0,"contact_point_centroid":[0.65953,0.0179,-0.00026],"force_p95":377.34947,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":876.52479,"mean_force":294.09058,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.45971,0.01469,0.19057]},{"body_a":"link5","body_b":"hand","contact_count":52.0,"contact_point_centroid":[0.55006,0.02567,0.26818],"force_p95":550.59119,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":604.46223,"mean_force":401.82015,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51774,0.1051,0.28948]},{"body_a":"link5","body_b":"hand","contact_count":3.0,"contact_point_centroid":[0.54732,0.03103,0.24861],"force_p95":356.74021,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":359.84121,"mean_force":319.89312,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.52349,0.10814,0.29018]},{"body_a":"link5","body_b":"hand","contact_count":200.0,"contact_point_centroid":[0.54682,0.03135,0.24683],"force_p95":311.88675,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":322.45344,"mean_force":250.75702,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.52497,0.10785,0.29162]},{"body_a":"link5","body_b":"hand","contact_count":15.0,"contact_point_centroid":[0.54933,0.03252,0.26827],"force_p95":242.34356,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":253.72512,"mean_force":157.3698,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.52591,0.10878,0.3127]},{"body_a":"world","body_b":"link6","contact_count":450.0,"contact_point_centroid":[0.68895,0.00791,-0.00012],"force_p95":71.8688,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":207.3831,"mean_force":67.6357,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46578,0.0165,0.16451]},{"body_a":"world","body_b":"link6","contact_count":6.0,"contact_point_centroid":[0.68906,0.00778,-9e-05],"force_p95":196.9994,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":197.37466,"mean_force":131.37476,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46578,0.01667,0.16442]},{"body_a":"grasp_target","body_b":"link7","contact_count":220.0,"contact_point_centroid":[0.50774,0.0148,0.03427],"force_p95":3.73502,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.76757,"mean_force":0.68539,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39907,0.00441,0.09123]},{"body_a":"grasp_target","body_b":"hand","contact_count":194.0,"contact_point_centroid":[0.4989,0.01867,0.04886],"force_p95":2.2089,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.5282,"mean_force":0.67034,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39832,0.00433,0.0882]},{"body_a":"left_finger","body_b":"link5","contact_count":410.0,"contact_point_centroid":[0.51497,0.07151,0.34058],"force_p95":1.82436,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2.82597,"mean_force":0.87271,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.52641,0.10865,0.3525]},{"body_a":"world","body_b":"grasp_target","contact_count":3525.0,"contact_point_centroid":[0.49974,0.03902,-0.00259],"force_p95":0.43012,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.57812,"mean_force":0.17731,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.43057,0.00768,0.15421]},{"body_a":"grasp_target","body_b":"link6","contact_count":28.0,"contact_point_centroid":[0.54435,0.03059,0.0049],"force_p95":0.61593,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.68548,"mean_force":0.4317,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.38722,0.00389,0.05448]},{"body_a":"left_finger","body_b":"link5","contact_count":22.0,"contact_point_centroid":[0.51755,0.06757,0.29226],"force_p95":0.25944,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.25952,"mean_force":0.23163,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.52546,0.10833,0.30815]},{"body_a":"world","body_b":"grasp_target","contact_count":3856.0,"contact_point_centroid":[0.49107,0.04084,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.45973,0.0147,0.19052]}],"total_contact_groups":27},"final_pose_error":0.01988,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.49107,0.04084,0.01602],"final_tcp_position":[0.5266,0.10833,0.38662],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":1351.2206,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49107,0.04084,0.01602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.19912,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":194.31437,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4878.0,"raw_peak_contact_force":1351.2206,"subtask_id":"approach_object","tcp_end":[0.44655,0.0144,0.19606],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.18734,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":964.0,"n_steps_budget":1000.0,"object_pos_end":[0.49107,0.04084,0.01602],"object_pos_start":[0.49107,0.04084,0.01602],"object_to_goal_dist_end":0.19912,"object_to_goal_dist_start":0.19912,"object_z_max":0.01602,"peak_contact_force":240.61288,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4816.0,"raw_peak_contact_force":876.52479,"tcp_end":[0.46578,0.01575,0.16507],"tcp_start":[0.44655,0.0144,0.19606],"tcp_to_object_dist_end":0.15325,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49107,0.04084,0.01602],"object_pos_start":[0.49107,0.04084,0.01602],"object_to_goal_dist_end":0.19912,"object_to_goal_dist_start":0.19912,"object_z_max":0.01602,"peak_contact_force":65.76868,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":2588.0,"raw_peak_contact_force":207.3831,"tcp_end":[0.46577,0.01653,0.16437],"tcp_start":[0.46578,0.01575,0.16507],"tcp_to_object_dist_end":0.15245,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":797.0,"n_steps_budget":1000.0,"object_pos_end":[0.49107,0.04084,0.01602],"object_pos_start":[0.49107,0.04084,0.01602],"object_to_goal_dist_end":0.19912,"object_to_goal_dist_start":0.19912,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":6611.0,"raw_peak_contact_force":197.37466,"tcp_end":[0.46459,0.01702,0.36139],"tcp_start":[0.46577,0.01653,0.16437],"tcp_to_object_dist_end":0.34721,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":537.0,"n_steps_budget":1000.0,"object_pos_end":[0.49107,0.04084,0.01602],"object_pos_start":[0.49107,0.04084,0.01602],"object_to_goal_dist_end":0.19912,"object_to_goal_dist_start":0.19912,"object_z_max":0.01602,"peak_contact_force":320.42886,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4532.0,"raw_peak_contact_force":604.46223,"subtask_id":"place_at_goal","tcp_end":[0.52328,0.10823,0.29012],"tcp_start":[0.46459,0.01702,0.36139],"tcp_to_object_dist_end":0.28409,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.49107,0.04084,0.01602],"object_pos_start":[0.49107,0.04084,0.01602],"object_to_goal_dist_end":0.19912,"object_to_goal_dist_start":0.19912,"object_z_max":0.01602,"peak_contact_force":323.37702,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":27.0,"raw_peak_contact_force":359.84121,"tcp_end":[0.52382,0.10803,0.29008],"tcp_start":[0.52328,0.10823,0.29012],"tcp_to_object_dist_end":0.28407,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":6.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49107,0.04084,0.01602],"object_pos_start":[0.49107,0.04084,0.01602],"object_to_goal_dist_end":0.19912,"object_to_goal_dist_start":0.19912,"object_z_max":0.01602,"peak_contact_force":231.23678,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1243.0,"raw_peak_contact_force":322.45344,"tcp_end":[0.52548,0.10835,0.31169],"tcp_start":[0.52382,0.10803,0.29008],"tcp_to_object_dist_end":0.30523,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":268.0,"n_steps_budget":600.0,"object_pos_end":[0.49107,0.04084,0.01602],"object_pos_start":[0.49107,0.04084,0.01602],"object_to_goal_dist_end":0.19912,"object_to_goal_dist_start":0.19912,"object_z_max":0.01602,"peak_contact_force":0.55349,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1497.0,"raw_peak_contact_force":253.72512,"tcp_end":[0.5266,0.10833,0.38662],"tcp_start":[0.52548,0.10835,0.31169],"tcp_to_object_dist_end":0.37836,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":22.0,"average_failure_rate":0.13095,"average_mean_iterations":30.54762,"average_solve_count":168.0,"average_success_count":146.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.08897,"descend_to_grasp.descend_distance":0.11855,"descend_to_place.place_height":0.02313,"lift_object.lift_height":0.20184,"retract_after_place.retract_height":0.05497,"transport_to_goal.transport_height":0.16916},"optimized_scores":{"best_composite_score":-0.32623,"best_fitness_score":0.15377,"best_task_score":0.12309},"replay_outcomes":[{"contacts":{"omitted_contact_groups":9,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":888.0,"contact_point_centroid":[0.64218,-0.00402,-0.00046],"force_p95":203.5235,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1531.67848,"mean_force":199.51001,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.40931,-0.00392,0.13462]},{"body_a":"world","body_b":"link6","contact_count":995.0,"contact_point_centroid":[0.65085,-0.00407,-0.00027],"force_p95":361.58312,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":910.33075,"mean_force":279.3635,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.45262,-0.00662,0.19136]},{"body_a":"world","body_b":"link6","contact_count":450.0,"contact_point_centroid":[0.67667,-0.00788,-0.00012],"force_p95":71.04209,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":371.16147,"mean_force":69.27929,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46472,-0.00681,0.17201]},{"body_a":"link5","body_b":"hand","contact_count":294.0,"contact_point_centroid":[0.54871,0.01085,0.34254],"force_p95":324.83857,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":337.0827,"mean_force":297.96296,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51849,0.08729,0.36208]},{"body_a":"world","body_b":"link7","contact_count":24.0,"contact_point_centroid":[0.53431,0.00106,-0.00375],"force_p95":0.0,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":319.35454,"mean_force":13.30644,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.38284,-0.00223,0.04549]},{"body_a":"link5","body_b":"hand","contact_count":200.0,"contact_point_centroid":[0.54994,0.0454,0.28218],"force_p95":285.61708,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":298.0616,"mean_force":259.374,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.53301,0.10893,0.34812]},{"body_a":"link5","body_b":"hand","contact_count":200.0,"contact_point_centroid":[0.54284,0.07318,0.24988],"force_p95":193.63823,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":196.26252,"mean_force":130.70165,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.54088,0.12321,0.33428]},{"body_a":"world","body_b":"link6","contact_count":6.0,"contact_point_centroid":[0.67675,-0.00792,-9e-05],"force_p95":180.83091,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":187.8216,"mean_force":110.93414,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46466,-0.00683,0.17189]},{"body_a":"link5","body_b":"hand","contact_count":9.0,"contact_point_centroid":[0.54521,0.07308,0.26864],"force_p95":160.8948,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":164.16854,"mean_force":123.02533,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.54153,0.12337,0.35439]},{"body_a":"grasp_target","body_b":"link7","contact_count":587.0,"contact_point_centroid":[0.50133,-0.02023,0.04498],"force_p95":1.04019,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.18272,"mean_force":0.34589,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.40223,-0.00308,0.11747]},{"body_a":"grasp_target","body_b":"hand","contact_count":374.0,"contact_point_centroid":[0.49349,-0.03115,0.05442],"force_p95":2.13501,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.48473,"mean_force":0.51456,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39787,-0.00261,0.10309]},{"body_a":"world","body_b":"grasp_target","contact_count":2792.0,"contact_point_centroid":[0.4912,-0.01686,-0.00292],"force_p95":0.33219,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.43954,"mean_force":0.20257,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.42637,-0.00383,0.15133]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.49679,-0.01574,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12265,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.45268,-0.00662,0.1913]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.49679,-0.01574,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46472,-0.00681,0.17201]},{"body_a":"world","body_b":"grasp_target","contact_count":2792.0,"contact_point_centroid":[0.49679,-0.01574,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46376,-0.00692,0.27261]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.49679,-0.01574,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.4978,0.05434,0.332]}],"total_contact_groups":25},"final_pose_error":0.0199,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.49679,-0.01574,0.02602],"final_tcp_position":[0.54282,0.12353,0.38899],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":273004.30507,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4968,-0.01574,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31422,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":191.10579,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4665.0,"raw_peak_contact_force":1531.67848,"subtask_id":"approach_object","tcp_end":[0.43182,-0.00668,0.18219],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16938,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49679,-0.01574,0.02602],"object_pos_start":[0.4968,-0.01574,0.02602],"object_to_goal_dist_end":0.31422,"object_to_goal_dist_start":0.31422,"object_z_max":0.02602,"peak_contact_force":501.54324,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4995.0,"raw_peak_contact_force":910.33075,"tcp_end":[0.46486,-0.00675,0.17318],"tcp_start":[0.43182,-0.00668,0.18219],"tcp_to_object_dist_end":0.15085,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49679,-0.01574,0.02602],"object_pos_start":[0.49679,-0.01574,0.02602],"object_to_goal_dist_end":0.31422,"object_to_goal_dist_start":0.31422,"object_z_max":0.02602,"peak_contact_force":67.16045,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":2590.0,"raw_peak_contact_force":371.16147,"tcp_end":[0.46471,-0.00683,0.17186],"tcp_start":[0.46486,-0.00675,0.17318],"tcp_to_object_dist_end":0.1496,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":698.0,"n_steps_budget":1000.0,"object_pos_end":[0.49679,-0.01574,0.02602],"object_pos_start":[0.49679,-0.01574,0.02602],"object_to_goal_dist_end":0.31422,"object_to_goal_dist_start":0.31422,"object_z_max":0.02602,"peak_contact_force":273004.30507,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":5793.0,"raw_peak_contact_force":187.8216,"tcp_end":[0.46292,-0.00707,0.3476],"tcp_start":[0.46471,-0.00683,0.17186],"tcp_to_object_dist_end":0.32348,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49679,-0.01574,0.02602],"object_pos_start":[0.49679,-0.01574,0.02602],"object_to_goal_dist_end":0.31422,"object_to_goal_dist_start":0.31422,"object_z_max":0.02602,"peak_contact_force":272973.74238,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8621.0,"raw_peak_contact_force":337.0827,"subtask_id":"place_at_goal","tcp_end":[0.52884,0.0969,0.3772],"tcp_start":[0.46292,-0.00707,0.3476],"tcp_to_object_dist_end":0.37019,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":200.0,"n_steps_budget":1000.0,"object_pos_end":[0.49679,-0.01574,0.02602],"object_pos_start":[0.49679,-0.01574,0.02602],"object_to_goal_dist_end":0.31422,"object_to_goal_dist_start":0.31422,"object_z_max":0.02602,"peak_contact_force":246.57771,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1876.0,"raw_peak_contact_force":298.0616,"tcp_end":[0.53954,0.12419,0.33213],"tcp_start":[0.52884,0.0969,0.3772],"tcp_to_object_dist_end":0.33928,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49679,-0.01574,0.02602],"object_pos_start":[0.49679,-0.01574,0.02602],"object_to_goal_dist_end":0.31422,"object_to_goal_dist_start":0.31422,"object_z_max":0.02602,"peak_contact_force":74.23315,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1219.0,"raw_peak_contact_force":196.26252,"tcp_end":[0.54134,0.12324,0.35385],"tcp_start":[0.53954,0.12419,0.33213],"tcp_to_object_dist_end":0.35885,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":146.0,"n_steps_budget":600.0,"object_pos_end":[0.49679,-0.01574,0.02602],"object_pos_start":[0.49679,-0.01574,0.02602],"object_to_goal_dist_end":0.31422,"object_to_goal_dist_start":0.31422,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":616.0,"raw_peak_contact_force":164.16854,"tcp_end":[0.54282,0.12353,0.38899],"tcp_start":[0.54134,0.12324,0.35385],"tcp_to_object_dist_end":0.39149,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```