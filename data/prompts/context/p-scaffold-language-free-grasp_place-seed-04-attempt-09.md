## Search State

- **Seed**: 4
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → descend → grasp → lift → approach → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6 | 0.2039 | 0.37 | ✅ accepted |
| 8 | approach → descend → grasp → lift → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | force_threshold_switch | position_control | position_control | position_control | admittance_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | time_limit | 4 | 0.3580 | 0.37 | ❌ rejected |
| 7 | approach → descend → grasp → lift → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | force_threshold_switch | position_control | position_control | position_control | admittance_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | time_limit | 4 | 0.3576 | 0.37 | ❌ rejected |
| 6 | approach → descend → grasp → lift → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | force_threshold_switch | position_control | position_control | position_control | admittance_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | time_limit | 4 | 0.3576 | 0.37 | ❌ rejected |
| 5 | approach → descend → grasp → lift → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | force_threshold_switch | position_control | position_control | position_control | admittance_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | time_limit | 4 | 0.3576 | 0.37 | ❌ rejected |

**Proposal policy**: task_score is 0.37 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.204) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.08
  weight: 0.25
- id: grasp_lift
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.2
  weight: 0.35
- id: place_at_goal
  weight: 0.4
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_object
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.005
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_object
- id: grasp_1
  type: grasp
  control: position_control
  termination: time_limit
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.02
- id: lift_1
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.2
    tolerance: 0.03
    orientation:
      mode: keep_current
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
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: grasp_lift
- id: transport_1
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
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: place_at_goal
- id: release_1
  type: release
  control: position_control
  termination: time_limit
  end_effector_action: open
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.02
- id: retract_1
  type: retract
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
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.005], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - parameter_bindings: none
- **lift_1** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.2], tolerance=0.03
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **transport_1** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - parameter_bindings: none
- **retract_1** (`retract`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.204
- **task_score** (E): 0.370
- **fitness_score**: 0.654  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.450

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1556 |
| descend_1 | 1.00 | 1.00 | 0.0983 |
| grasp_1 | 1.00 | 1.00 | 0.0133 |
| lift_1 | 1.00 | 1.00 | 0.1058 |
| transport_1 | 1.00 | 1.00 | 0.1827 |
| release_1 | 1.00 | 1.00 | 0.0214 |
| retract_1 | 1.00 | 1.00 | 0.0726 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.519, 0.005, 0.148) | (0.526, 0.005, 0.030)→(0.526, 0.005, 0.026) | 0.246→0.249 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.519, 0.005, 0.148)→(0.521, 0.005, 0.050) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 4.000 | 10.688 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.521, 0.005, 0.050)→(0.512, 0.005, 0.040) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 41.000 | 0.142 | 0.188 |
| lift_1 | lift | 1.00 / step_budget | (0.512, 0.005, 0.040)→(0.520, 0.005, 0.145) | (0.526, 0.005, 0.026)→(0.532, 0.005, 0.130) | 0.249→0.199 | 1.00 / 37.667 | 0.084 | 0.405 |
| transport_1 | approach | 1.00 / step_budget | (0.520, 0.005, 0.145)→(0.602, 0.162, 0.172) | (0.532, 0.005, 0.130)→(0.609, 0.162, 0.152) | 0.199→0.034 | 1.00 / 38.000 | 0.075 | 0.101 |
| release_1 | release | 1.00 / step_budget | (0.602, 0.162, 0.172)→(0.596, 0.160, 0.193) | (0.609, 0.162, 0.152)→(0.595, 0.160, 0.024) | 0.034→0.161 | 1.00 / 3.333 | 0.168 | 1.375 |
| retract_1 | retract | 1.00 / step_budget | (0.596, 0.160, 0.193)→(0.608, 0.172, 0.263) | (0.595, 0.160, 0.024)→(0.586, 0.158, 0.026) | 0.161→0.160 | 1.00 / 4.000 | 0.123 | 0.215 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.560
- phase_score: 0.387
- phase_breakdown.reach_object_score: 0.298
- phase_breakdown.grasp_lift_score: 0.125
- phase_breakdown.place_at_goal_score: 0.673
- grasp_place_fitness: 0.749

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.749
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.560
- **Median Q (composite search score)**: 0.182
- **K-run variance**: 0.0049
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.288


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.89914,"average_solve_count":347.0,"average_success_count":347.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.09611,"descend_1.speed":0.08068,"lift_1.lift_height":0.13583,"lift_1.speed":0.01567,"retract_1.speed":0.05155,"transport_1.speed":0.03024},"optimized_scores":{"best_composite_score":0.18169,"best_fitness_score":0.63169,"best_task_score":0.32525},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":164.0,"contact_point_centroid":[0.62864,0.14335,-0.00782],"force_p95":1.27794,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.60271,"mean_force":0.44468,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.63129,0.14584,0.18756]},{"body_a":"world","body_b":"grasp_target","contact_count":117.0,"contact_point_centroid":[0.54164,0.00061,-0.00161],"force_p95":0.31691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.37073,"mean_force":0.16622,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5281,0.00082,0.03933]},{"body_a":"world","body_b":"grasp_target","contact_count":1356.0,"contact_point_centroid":[0.61926,0.14218,-0.00209],"force_p95":0.19981,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25814,"mean_force":0.1288,"phase_index":6.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.6369,0.15122,0.23624]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4298.0,"contact_point_centroid":[0.53161,-0.01844,0.082],"force_p95":0.08577,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22526,"mean_force":0.05748,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53129,0.00074,0.0792]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4815.0,"contact_point_centroid":[0.53163,0.01981,0.08228],"force_p95":0.08221,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21598,"mean_force":0.05291,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53142,0.00074,0.08016]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1063.0,"contact_point_centroid":[0.63673,0.12795,0.17745],"force_p95":0.07878,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1994,"mean_force":0.04794,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.6353,0.14709,0.17474]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1225.0,"contact_point_centroid":[0.6366,0.16623,0.17641],"force_p95":0.07383,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19216,"mean_force":0.04437,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.63533,0.14711,0.17481]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54431,0.00102,-0.00203],"force_p95":0.13253,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15378,"mean_force":0.12547,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53043,0.00087,0.04023]},{"body_a":"world","body_b":"grasp_target","contact_count":1220.0,"contact_point_centroid":[0.54431,0.00113,-0.00189],"force_p95":0.13606,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12303,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51633,0.00045,0.22481]},{"body_a":"world","body_b":"grasp_target","contact_count":744.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53555,0.00095,0.09901]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4115.0,"contact_point_centroid":[0.53046,-0.01835,0.0415],"force_p95":0.07629,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12226,"mean_force":0.0518,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52922,0.00085,0.03883]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12402.0,"contact_point_centroid":[0.58703,0.05519,0.15539],"force_p95":0.07628,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10483,"mean_force":0.05231,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.58603,0.07424,0.15326]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11907.0,"contact_point_centroid":[0.58958,0.09699,0.15675],"force_p95":0.07837,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10385,"mean_force":0.05398,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.58858,0.0779,0.1545]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4878.0,"contact_point_centroid":[0.53036,0.01992,0.04063],"force_p95":0.06837,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09468,"mean_force":0.04471,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52922,0.00085,0.03884]}],"total_contact_groups":14},"final_pose_error":0.01981,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.61799,0.14217,0.02602],"final_tcp_position":[0.6435,0.15603,0.27184],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":1.60271,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":306.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1220.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.53499,0.00093,0.1474],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12174,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":186.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":744.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.53812,0.00101,0.04959],"tcp_start":[0.53499,0.00093,0.1474],"tcp_to_object_dist_end":0.02437,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5442,0.00075,0.02587],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25051,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.13072,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10793.0,"raw_peak_contact_force":0.15378,"tcp_end":[0.52919,0.00085,0.0388],"tcp_start":[0.53812,0.00101,0.04959],"tcp_to_object_dist_end":0.01981,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":230.0,"n_steps_budget":1000.0,"object_pos_end":[0.54993,0.00056,0.11848],"object_pos_start":[0.5442,0.00075,0.02587],"object_to_goal_dist_end":0.19908,"object_to_goal_dist_start":0.25051,"object_z_max":0.11805,"peak_contact_force":0.08381,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":9230.0,"raw_peak_contact_force":0.37073,"subtask_id":"grasp_lift","tcp_end":[0.53777,0.0007,0.13258],"tcp_start":[0.52919,0.00085,0.0388],"tcp_to_object_dist_end":0.01862,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":657.0,"n_steps_budget":1000.0,"object_pos_end":[0.64453,0.1469,0.15857],"object_pos_start":[0.54993,0.00056,0.11848],"object_to_goal_dist_end":0.03454,"object_to_goal_dist_start":0.19908,"object_z_max":0.15851,"peak_contact_force":0.07743,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":24309.0,"raw_peak_contact_force":0.10483,"subtask_id":"place_at_goal","tcp_end":[0.63699,0.14703,0.17833],"tcp_start":[0.53777,0.0007,0.13258],"tcp_to_object_dist_end":0.02115,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.63154,0.14545,0.02688],"object_pos_start":[0.64453,0.1469,0.15857],"object_to_goal_dist_end":0.16549,"object_to_goal_dist_start":0.03454,"object_z_max":0.15857,"peak_contact_force":0.19516,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2452.0,"raw_peak_contact_force":1.60271,"tcp_end":[0.63124,0.14583,0.19762],"tcp_start":[0.63699,0.14703,0.17833],"tcp_to_object_dist_end":0.17073,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":361.0,"n_steps_budget":1000.0,"object_pos_end":[0.61799,0.14217,0.02602],"object_pos_start":[0.63154,0.14545,0.02688],"object_to_goal_dist_end":0.16848,"object_to_goal_dist_start":0.16549,"object_z_max":0.02916,"peak_contact_force":0.12267,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1356.0,"raw_peak_contact_force":0.25814,"tcp_end":[0.6435,0.15603,0.27184],"tcp_start":[0.63124,0.14583,0.19762],"tcp_to_object_dist_end":0.24753,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.02108,"average_solve_count":332.0,"average_success_count":332.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.03318,"descend_1.speed":0.04242,"lift_1.lift_height":0.12993,"lift_1.speed":0.03038,"retract_1.speed":0.09765,"transport_1.speed":0.05037},"optimized_scores":{"best_composite_score":0.29862,"best_fitness_score":0.74862,"best_task_score":0.56024},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":357.0,"contact_point_centroid":[0.57928,0.16153,-0.00339],"force_p95":0.73694,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.85054,"mean_force":0.19595,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58319,0.16201,0.11001]},{"body_a":"world","body_b":"grasp_target","contact_count":94.0,"contact_point_centroid":[0.52778,0.02909,-0.00173],"force_p95":0.37541,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.39473,"mean_force":0.19746,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51507,0.02895,0.04029]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4310.0,"contact_point_centroid":[0.51818,0.04806,0.08182],"force_p95":0.08786,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24952,"mean_force":0.05342,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51835,0.02891,0.07978]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4060.0,"contact_point_centroid":[0.51837,0.00972,0.08249],"force_p95":0.08645,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23751,"mean_force":0.05458,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51834,0.02891,0.07982]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53056,0.03056,-0.00215],"force_p95":0.16538,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22958,"mean_force":0.13388,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5172,0.0291,0.04095]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1153.0,"contact_point_centroid":[0.5889,0.14462,0.10097],"force_p95":0.0749,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19597,"mean_force":0.04561,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.588,0.16366,0.09864]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1135.0,"contact_point_centroid":[0.58875,0.18284,0.1006],"force_p95":0.0806,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18774,"mean_force":0.04887,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58793,0.16362,0.09852]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4074.0,"contact_point_centroid":[0.51705,0.00981,0.04235],"force_p95":0.08158,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15473,"mean_force":0.05189,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51602,0.02903,0.03962]},{"body_a":"world","body_b":"grasp_target","contact_count":1108.0,"contact_point_centroid":[0.57856,0.16157,-0.00198],"force_p95":0.13128,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14131,"mean_force":0.12278,"phase_index":6.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5884,0.16865,0.1558]},{"body_a":"world","body_b":"grasp_target","contact_count":1296.0,"contact_point_centroid":[0.5305,0.03079,-0.0019],"force_p95":0.13564,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.123,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51013,0.01256,0.22558]},{"body_a":"world","body_b":"grasp_target","contact_count":788.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52273,0.02787,0.09964]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8763.0,"contact_point_centroid":[0.55631,0.0769,0.11423],"force_p95":0.07691,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09947,"mean_force":0.05179,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55556,0.09594,0.11211]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8118.0,"contact_point_centroid":[0.55746,0.11734,0.11412],"force_p95":0.0788,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08779,"mean_force":0.05547,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55673,0.09822,0.11178]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5029.0,"contact_point_centroid":[0.51697,0.0482,0.04141],"force_p95":0.07452,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0778,"mean_force":0.0444,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51602,0.02903,0.03963]}],"total_contact_groups":14},"final_pose_error":0.01997,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.57856,0.16157,0.02602],"final_tcp_position":[0.59569,0.17537,0.18927],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":31.81906,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":325.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1296.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.52286,0.02635,0.14742],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12172,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":197.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":31.81906,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":788.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.52469,0.02957,0.04984],"tcp_start":[0.52286,0.02635,0.14742],"tcp_to_object_dist_end":0.02454,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53046,0.02935,0.02549],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18479,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.15764,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10903.0,"raw_peak_contact_force":0.22958,"tcp_end":[0.51599,0.02902,0.03959],"tcp_start":[0.52469,0.02957,0.04984],"tcp_to_object_dist_end":0.0202,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":201.0,"n_steps_budget":1000.0,"object_pos_end":[0.53582,0.02923,0.11146],"object_pos_start":[0.53046,0.02935,0.02549],"object_to_goal_dist_end":0.1632,"object_to_goal_dist_start":0.18479,"object_z_max":0.111,"peak_contact_force":0.08549,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":8464.0,"raw_peak_contact_force":0.39473,"subtask_id":"grasp_lift","tcp_end":[0.524,0.02902,0.12624],"tcp_start":[0.51599,0.02902,0.03959],"tcp_to_object_dist_end":0.01893,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":456.0,"n_steps_budget":1000.0,"object_pos_end":[0.59873,0.16357,0.08299],"object_pos_start":[0.53582,0.02923,0.11146],"object_to_goal_dist_end":0.02938,"object_to_goal_dist_start":0.1632,"object_z_max":0.11219,"peak_contact_force":0.07887,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":16881.0,"raw_peak_contact_force":0.09947,"subtask_id":"place_at_goal","tcp_end":[0.59011,0.1636,0.10191],"tcp_start":[0.524,0.02902,0.12624],"tcp_to_object_dist_end":0.02079,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57799,0.16156,0.02631],"object_pos_start":[0.59873,0.16357,0.08299],"object_to_goal_dist_end":0.08679,"object_to_goal_dist_start":0.02938,"object_z_max":0.08299,"peak_contact_force":0.14133,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2645.0,"raw_peak_contact_force":0.85054,"tcp_end":[0.58303,0.16196,0.12297],"tcp_start":[0.59011,0.1636,0.10191],"tcp_to_object_dist_end":0.09679,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":277.0,"n_steps_budget":600.0,"object_pos_end":[0.57856,0.16157,0.02602],"object_pos_start":[0.57799,0.16156,0.02631],"object_to_goal_dist_end":0.08691,"object_to_goal_dist_start":0.08679,"object_z_max":0.02631,"peak_contact_force":0.12264,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1108.0,"raw_peak_contact_force":0.14131,"tcp_end":[0.59569,0.17537,0.18927],"tcp_start":[0.58303,0.16196,0.12297],"tcp_to_object_dist_end":0.16472,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.22264,"average_solve_count":265.0,"average_success_count":265.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.06587,"descend_1.speed":0.0631,"lift_1.lift_height":0.18025,"lift_1.speed":0.05941,"retract_1.speed":0.07374,"transport_1.speed":0.05338},"optimized_scores":{"best_composite_score":0.13126,"best_fitness_score":0.58126,"best_task_score":0.2245},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":135.0,"contact_point_centroid":[0.56858,0.17163,-0.0098],"force_p95":1.58599,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.67279,"mean_force":0.57843,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57425,0.17302,0.25079]},{"body_a":"world","body_b":"grasp_target","contact_count":70.0,"contact_point_centroid":[0.50152,-0.01526,-0.00153],"force_p95":0.40439,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.44983,"mean_force":0.17853,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48976,-0.01503,0.04172]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5468.0,"contact_point_centroid":[0.49321,0.00418,0.10721],"force_p95":0.08391,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29635,"mean_force":0.05793,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49303,-0.01499,0.1046]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5878.0,"contact_point_centroid":[0.49317,-0.03409,0.10686],"force_p95":0.08047,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27513,"mean_force":0.05501,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49304,-0.01499,0.10477]},{"body_a":"world","body_b":"grasp_target","contact_count":1066.0,"contact_point_centroid":[0.56349,0.17171,-0.00221],"force_p95":0.19114,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24415,"mean_force":0.12653,"phase_index":6.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.57849,0.1794,0.29518]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1225.0,"contact_point_centroid":[0.5787,0.19354,0.23488],"force_p95":0.07043,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18681,"mean_force":0.04428,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57731,0.1743,0.23294]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50383,-0.01554,-0.00206],"force_p95":0.13974,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18145,"mean_force":0.12726,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49177,-0.01506,0.04192]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1220.0,"contact_point_centroid":[0.57942,0.15517,0.23579],"force_p95":0.06874,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17118,"mean_force":0.042,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57731,0.1743,0.23295]},{"body_a":"world","body_b":"grasp_target","contact_count":1180.0,"contact_point_centroid":[0.50382,-0.01567,-0.00189],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12304,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49928,-0.00637,0.22636]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4105.0,"contact_point_centroid":[0.49118,0.00417,0.04347],"force_p95":0.07763,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1313,"mean_force":0.05184,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49064,-0.01504,0.04072]},{"body_a":"world","body_b":"grasp_target","contact_count":788.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49859,-0.01419,0.10039]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13741.0,"contact_point_centroid":[0.53942,0.06266,0.20718],"force_p95":0.07285,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0975,"mean_force":0.0498,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53825,0.0817,0.20499]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12648.0,"contact_point_centroid":[0.54098,0.10467,0.20867],"force_p95":0.07848,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09501,"mean_force":0.05331,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53991,0.08554,0.20626]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4908.0,"contact_point_centroid":[0.49123,-0.03413,0.04255],"force_p95":0.06979,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08485,"mean_force":0.04467,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49064,-0.01504,0.04072]}],"total_contact_groups":14},"final_pose_error":0.01981,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.56166,0.17169,0.02602],"final_tcp_position":[0.58347,0.1849,0.32877],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":1.67279,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":296.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1180.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.49994,-0.01331,0.14945],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12351,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":197.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":788.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.49903,-0.01513,0.04998],"tcp_start":[0.49994,-0.01331,0.14945],"tcp_to_object_dist_end":0.02444,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50373,-0.01504,0.02579],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31201,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13659,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10813.0,"raw_peak_contact_force":0.18145,"tcp_end":[0.49061,-0.01504,0.04069],"tcp_start":[0.49903,-0.01513,0.04998],"tcp_to_object_dist_end":0.01985,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":286.0,"n_steps_budget":1000.0,"object_pos_end":[0.51017,-0.01504,0.15934],"object_pos_start":[0.50373,-0.01504,0.02579],"object_to_goal_dist_end":0.23404,"object_to_goal_dist_start":0.31201,"object_z_max":0.15888,"peak_contact_force":0.08363,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":11416.0,"raw_peak_contact_force":0.44983,"subtask_id":"grasp_lift","tcp_end":[0.49887,-0.01498,0.17673],"tcp_start":[0.49061,-0.01504,0.04069],"tcp_to_object_dist_end":0.02074,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":694.0,"n_steps_budget":1000.0,"object_pos_end":[0.5852,0.17405,0.21359],"object_pos_start":[0.51017,-0.01504,0.15934],"object_to_goal_dist_end":0.03707,"object_to_goal_dist_start":0.23404,"object_z_max":0.21352,"peak_contact_force":0.07017,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":26389.0,"raw_peak_contact_force":0.0975,"subtask_id":"place_at_goal","tcp_end":[0.57871,0.1742,0.23599],"tcp_start":[0.49887,-0.01498,0.17673],"tcp_to_object_dist_end":0.02332,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5754,0.17181,0.01754],"object_pos_start":[0.5852,0.17405,0.21359],"object_to_goal_dist_end":0.2314,"object_to_goal_dist_start":0.03707,"object_z_max":0.21359,"peak_contact_force":0.16745,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2580.0,"raw_peak_contact_force":1.67279,"tcp_end":[0.57422,0.17302,0.25721],"tcp_start":[0.57871,0.1742,0.23599],"tcp_to_object_dist_end":0.23968,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":291.0,"n_steps_budget":810.0,"object_pos_end":[0.56166,0.17169,0.02602],"object_pos_start":[0.5754,0.17181,0.01754],"object_to_goal_dist_end":0.22408,"object_to_goal_dist_start":0.2314,"object_z_max":0.02909,"peak_contact_force":0.12287,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1066.0,"raw_peak_contact_force":0.24415,"tcp_end":[0.58347,0.1849,0.32877],"tcp_start":[0.57422,0.17302,0.25721],"tcp_to_object_dist_end":0.30383,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```