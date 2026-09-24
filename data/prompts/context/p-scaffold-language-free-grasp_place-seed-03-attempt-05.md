## Search State

- **Seed**: 3
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 10 | 0.1512 | 0.46 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | contact_detected | pose_tolerance | 7 | 0.2125 | 0.47 | ❌ rejected |
| 3 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | contact_detected | pose_tolerance | 7 | 0.2215 | 0.49 | ✅ accepted |
| 2 | approach → descend → grasp → lift → release | linear_cartesian | linear_cartesian | — | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | 5 | 0.2342 | 0.20 | ❌ rejected |
| 1 | approach → descend → grasp → lift → release | linear_cartesian | linear_cartesian | — | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | 5 | 0.2342 | 0.20 | ❌ rejected |

**Proposal policy**: task_score is 0.46 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `51caab5aeef033bda3880e250ac3d834b494dfd11f1563b679caeea40811318b`
- Frozen object start: [0.45856491671436245, -0.02631894934039003, 0.03]
- Frozen task target: [0.6301274465206397, 0.20821620360643678, 0.11411929633605988]
- Goal object position: (0.6301274465206397, 0.20821620360643678, 0.11411929633605988)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.6301274465206397, 0.20821620360643678, 0.11411929633605988)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.45856491671436245, -0.02631894934039003, 0.03)
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
  frozen_object_start: [0.4586, -0.0263, 0.03]
  frozen_task_target: [0.6301, 0.2082, 0.1141]
  frozen_object_starts: {'grasp_target': [0.45856491671436245, -0.02631894934039003, 0.03]}
  frozen_targets: {'place_target': [0.6301274465206397, 0.20821620360643678, 0.11411929633605988]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 51caab5aeef033bda3880e250ac3d834b494dfd11f1563b679caeea40811318b

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
| `object` | offset from object initial position (0.45856491671436245, -0.02631894934039003, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.6301274465206397, 0.20821620360643678, 0.11411929633605988) | final destination targets |
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

## Current Skill (Q=0.151) — your mutation base

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
  - 0.1
  weight: 0.2
- id: grasp_object
  anchor: object
  target_entity: object
  weight: 0.2
- id: lift_object
  anchor: object
  target_entity: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.1
- id: transport_to_goal
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.2
- id: place_at_goal
  target_entity: object
  weight: 0.3
phases:
- id: approach_1
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
  termination: contact_detected
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: grasp_object
- id: grasp_1
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
    orientation:
      mode: keep_current
  subtask_id: grasp_object
- id: lift_1
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
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
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
  subtask_id: lift_object
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
    - 0.15
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
    transport_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: transport_to_goal
- id: descend_2
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: contact_detected
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: place_at_goal
- id: release_1
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
    orientation:
      mode: keep_current
  subtask_id: place_at_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none
- **lift_1** (`lift`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **transport_1** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
    - transport_height: status=consumed; consumers=target.offset.z (replace)
- **descend_2** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.151
- **task_score** (E): 0.456
- **fitness_score**: 0.706  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.125
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.680

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1576 |
| descend_1 | 1.00 | 1.00 | 0.1154 |
| grasp_1 | 1.00 | 1.00 | 0.0119 |
| lift_1 | 1.00 | 1.00 | 0.1720 |
| transport_1 | 1.00 | 1.00 | 0.2272 |
| descend_2 | 1.00 | 1.00 | 0.0108 |
| release_1 | 1.00 | 1.00 | 0.0197 |
| retract_1 | 1.00 | 1.00 | 0.0946 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.002, 0.148) | (0.511, 0.002, 0.030)→(0.511, 0.002, 0.026) | 0.244→0.246 | 1.00 / 4.000 | 25.293 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.506, 0.002, 0.148)→(0.506, 0.002, 0.033) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.506, 0.002, 0.033)→(0.498, 0.002, 0.024) | (0.511, 0.002, 0.026)→(0.511, 0.001, 0.026) | 0.246→0.246 | 1.00 / 42.333 | 0.139 | 0.199 |
| lift_1 | lift | 1.00 / step_budget | (0.498, 0.002, 0.024)→(0.507, 0.001, 0.196) | (0.511, 0.001, 0.026)→(0.519, 0.001, 0.192) | 0.246→0.218 | 1.00 / 37.667 | 524.419 | 0.614 |
| transport_1 | approach | 1.00 / step_budget | (0.507, 0.001, 0.196)→(0.618, 0.171, 0.280) | (0.519, 0.001, 0.192)→(0.628, 0.171, 0.268) | 0.218→0.131 | 1.00 / 36.333 | 3253.490 | 0.102 |
| descend_2 | descend | 1.00 / force_exceeded | (0.618, 0.171, 0.280)→(0.617, 0.171, 0.269) | (0.628, 0.171, 0.268)→(0.626, 0.171, 0.257) | 0.131→0.120 | 1.00 / 36.667 | 56522.361 | 0.152 |
| release_1 | release | 1.00 / step_budget | (0.617, 0.171, 0.269)→(0.613, 0.170, 0.289) | (0.626, 0.171, 0.257)→(0.623, 0.172, 0.003) | 0.120→0.135 | 1.00 / 4.000 | 0.459 | 2.219 |
| retract_1 | retract | 1.00 / step_budget | (0.613, 0.170, 0.289)→(0.612, 0.169, 0.383) | (0.623, 0.172, 0.003)→(0.624, 0.176, 0.016) | 0.135→0.122 | 1.00 / 4.000 | 0.123 | 0.450 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.538
- phase_score: 0.471
- phase_breakdown.place_at_goal_score: 0.078
- phase_breakdown.transport_to_goal_score: 0.530
- phase_breakdown.reach_object_score: 0.672
- phase_breakdown.grasp_object_score: 0.736
- phase_breakdown.lift_object_score: 0.602
- grasp_place_fitness: 0.747

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.747
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.538
- **Median Q (composite search score)**: 0.185
- **K-run variance**: 0.0028
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.290


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `952d4e9e12c194d228cf63d10b31c959edc327920598c352d26dcf1284463776`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `ab36b663de63a40a5839be0af4fc1d53d37f9e78d4183a3de7f11063534632b8`; realized-scene SHA-256: `51caab5aeef033bda3880e250ac3d834b494dfd11f1563b679caeea40811318b`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45856,-0.02632,0.03]},{"name":"goal","value":[0.63013,0.20822,0.11412]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.45856,-0.02632,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63013,0.20822,0.11412]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.10174,"average_solve_count":344.0,"average_success_count":344.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.07448,"descend_1.speed":0.04341,"descend_2.place_force_threshold":11.70807,"descend_2.speed":0.02956,"lift_1.lift_height":0.19926,"lift_1.speed":0.05166,"retract_1.retract_height":0.11015,"retract_1.speed":0.06084,"transport_1.speed":0.05204,"transport_1.transport_height":0.13307},"optimized_scores":{"best_composite_score":0.18472,"best_fitness_score":0.73972,"best_task_score":0.5195},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":154.0,"contact_point_centroid":[0.62378,0.20857,-0.00888],"force_p95":1.47606,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.09206,"mean_force":0.53193,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.614,0.19464,0.2475]},{"body_a":"world","body_b":"grasp_target","contact_count":79.0,"contact_point_centroid":[0.45593,-0.02561,-0.0014],"force_p95":0.61128,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.71726,"mean_force":0.182,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44577,-0.02563,0.02252]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12129.0,"contact_point_centroid":[0.44883,-0.04462,0.1123],"force_p95":0.07579,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27396,"mean_force":0.05204,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44869,-0.02552,0.11029]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11600.0,"contact_point_centroid":[0.44897,-0.00639,0.11406],"force_p95":0.07771,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27175,"mean_force":0.05385,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44877,-0.02552,0.11164]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45856,-0.02613,-0.00205],"force_p95":0.13832,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19157,"mean_force":0.12707,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44783,-0.02571,0.02244]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.62501,0.20791,-0.002],"force_p95":0.12323,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16237,"mean_force":0.12131,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.61196,0.19379,0.29865]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":150.0,"contact_point_centroid":[0.61805,0.17718,0.23647],"force_p95":0.10416,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1568,"mean_force":0.05969,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.61876,0.19619,0.23577]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":200.0,"contact_point_centroid":[0.61976,0.21528,0.23649],"force_p95":0.10077,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15596,"mean_force":0.05909,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.61876,0.19619,0.23577]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1287.0,"contact_point_centroid":[0.61795,0.21491,0.23079],"force_p95":0.07632,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14913,"mean_force":0.04567,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61695,0.19586,0.2302]},{"body_a":"world","body_b":"grasp_target","contact_count":1184.0,"contact_point_centroid":[0.45856,-0.02632,-0.00189],"force_p95":0.13638,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12304,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48072,-0.01077,0.22616]},{"body_a":"world","body_b":"grasp_target","contact_count":3020.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45607,-0.02418,0.08577]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1020.0,"contact_point_centroid":[0.61729,0.17675,0.23079],"force_p95":0.09019,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10636,"mean_force":0.05121,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61693,0.19586,0.23014]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17327.0,"contact_point_centroid":[0.53409,0.06407,0.21997],"force_p95":0.07802,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10467,"mean_force":0.05189,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53379,0.08315,0.2189]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16619.0,"contact_point_centroid":[0.54038,0.11011,0.22148],"force_p95":0.0784,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09318,"mean_force":0.05309,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53971,0.09102,0.22013]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4810.0,"contact_point_centroid":[0.44676,-0.00646,0.0238],"force_p95":0.06771,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0927,"mean_force":0.04485,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44673,-0.02567,0.02142]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5172.0,"contact_point_centroid":[0.44661,-0.04491,0.02328],"force_p95":0.0665,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08675,"mean_force":0.04305,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44673,-0.02567,0.02142]}],"total_contact_groups":16},"final_pose_error":0.01581,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.62501,0.2079,0.01602],"final_tcp_position":[0.61238,0.19387,0.34796],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":9760.30694,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":297.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1184.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.46123,-0.02246,0.1491],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12317,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":755.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3020.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.45421,-0.02594,0.02844],"tcp_start":[0.46123,-0.02246,0.1491],"tcp_to_object_dist_end":0.005,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45842,-0.02566,0.02582],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30328,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.13563,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11782.0,"raw_peak_contact_force":0.19157,"subtask_id":"grasp_object","tcp_end":[0.4467,-0.02567,0.02139],"tcp_start":[0.45421,-0.02594,0.02844],"tcp_to_object_dist_end":0.01252,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":608.0,"n_steps_budget":1000.0,"object_pos_end":[0.46743,-0.02554,0.20418],"object_pos_start":[0.45842,-0.02566,0.02582],"object_to_goal_dist_end":0.29871,"object_to_goal_dist_start":0.30328,"object_z_max":0.2039,"peak_contact_force":1573.09317,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":23808.0,"raw_peak_contact_force":0.71726,"subtask_id":"lift_object","tcp_end":[0.4545,-0.02552,0.20552],"tcp_start":[0.4467,-0.02567,0.02139],"tcp_to_object_dist_end":0.013,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":35.0,"n_steps":876.0,"n_steps_budget":1000.0,"object_pos_end":[0.62981,0.19575,0.22553],"object_pos_start":[0.46743,-0.02554,0.20418],"object_to_goal_dist_end":0.1121,"object_to_goal_dist_start":0.29871,"object_z_max":0.22551,"peak_contact_force":9760.30694,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":33946.0,"raw_peak_contact_force":0.10467,"subtask_id":"transport_to_goal","tcp_end":[0.61888,0.19581,0.2364],"tcp_start":[0.4545,-0.02552,0.20552],"tcp_to_object_dist_end":0.01543,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":33.0,"n_steps":10.0,"n_steps_budget":1000.0,"object_pos_end":[0.62963,0.1966,0.22354],"object_pos_start":[0.62981,0.19575,0.22553],"object_to_goal_dist_end":0.11003,"object_to_goal_dist_start":0.1121,"object_z_max":0.22553,"peak_contact_force":42.26043,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":350.0,"raw_peak_contact_force":0.1568,"subtask_id":"place_at_goal","tcp_end":[0.61853,0.19639,0.2346],"tcp_start":[0.61888,0.19581,0.2364],"tcp_to_object_dist_end":0.01567,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.62302,0.20203,0.00734],"object_pos_start":[0.62963,0.1966,0.22354],"object_to_goal_dist_end":0.1072,"object_to_goal_dist_start":0.11003,"object_z_max":0.22354,"peak_contact_force":0.1757,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2461.0,"raw_peak_contact_force":2.09206,"subtask_id":"place_at_goal","tcp_end":[0.61398,0.19463,0.25353],"tcp_start":[0.61853,0.19639,0.2346],"tcp_to_object_dist_end":0.24647,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.62501,0.2079,0.01602],"object_pos_start":[0.62302,0.20203,0.00734],"object_to_goal_dist_end":0.09823,"object_to_goal_dist_start":0.1072,"object_z_max":0.01716,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.16237,"tcp_end":[0.61238,0.19387,0.34796],"tcp_start":[0.61398,0.19463,0.25353],"tcp_to_object_dist_end":0.33248,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `aa6ec658384c70fac6b4eb656cc8c53536c3d5c760368ab2b384dccf294e2c48`; realized-scene SHA-256: `1959b3932a54fd3d3850620783d44a63a35b8fa059f78d939fdbdef5fbfc64e8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.54431,0.00113,0.03]},{"name":"goal","value":[0.64762,0.15808,0.1911]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.54431,0.00113,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.64762,0.15808,0.1911]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.0788,"average_solve_count":368.0,"average_success_count":368.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.05796,"descend_1.speed":0.09315,"descend_2.place_force_threshold":12.76787,"descend_2.speed":0.02237,"lift_1.lift_height":0.22007,"lift_1.speed":0.02522,"retract_1.retract_height":0.10103,"retract_1.speed":0.06361,"transport_1.speed":0.03147,"transport_1.transport_height":0.20031},"optimized_scores":{"best_composite_score":0.07708,"best_fitness_score":0.63208,"best_task_score":0.31102},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":48.0,"contact_point_centroid":[0.64337,0.15215,-0.00993],"force_p95":2.41255,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.63403,"mean_force":1.30746,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.63954,0.14923,0.37572]},{"body_a":"world","body_b":"grasp_target","contact_count":3496.0,"contact_point_centroid":[0.64789,0.15227,-0.00233],"force_p95":0.12533,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.06158,"mean_force":0.12634,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.63925,0.14892,0.4197]},{"body_a":"world","body_b":"grasp_target","contact_count":94.0,"contact_point_centroid":[0.54015,0.00072,-0.00145],"force_p95":0.53227,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57069,"mean_force":0.21194,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52839,0.00083,0.02766]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13938.0,"contact_point_centroid":[0.53362,-0.01836,0.12929],"force_p95":0.07887,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27293,"mean_force":0.05588,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53275,0.00073,0.12697]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14275.0,"contact_point_centroid":[0.53333,0.01979,0.12564],"force_p95":0.07802,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26352,"mean_force":0.05501,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53251,0.00073,0.12346]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1039.0,"contact_point_centroid":[0.64256,0.16931,0.36788],"force_p95":0.07905,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1828,"mean_force":0.05597,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.64127,0.15022,0.36768]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1045.0,"contact_point_centroid":[0.64262,0.13128,0.3681],"force_p95":0.07762,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16391,"mean_force":0.05423,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.64127,0.15022,0.36772]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5443,0.00099,-0.00203],"force_p95":0.13192,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15902,"mean_force":0.12531,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53071,0.00088,0.02825]},{"body_a":"world","body_b":"grasp_target","contact_count":1288.0,"contact_point_centroid":[0.54431,0.00113,-0.0019],"force_p95":0.13564,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12301,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51605,0.00044,0.22494]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":911.0,"contact_point_centroid":[0.64217,0.169,0.35648],"force_p95":0.09182,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13804,"mean_force":0.05563,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.64042,0.14977,0.35495]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53517,0.00096,0.07895]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1254.0,"contact_point_centroid":[0.64145,0.13086,0.35607],"force_p95":0.07142,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11576,"mean_force":0.04203,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.64047,0.14979,0.35524]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4115.0,"contact_point_centroid":[0.53061,-0.01834,0.02948],"force_p95":0.07609,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11311,"mean_force":0.05172,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52945,0.00086,0.02681]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16154.0,"contact_point_centroid":[0.5901,0.09421,0.29845],"force_p95":0.08021,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10567,"mean_force":0.05421,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.58921,0.07507,0.29754]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17939.0,"contact_point_centroid":[0.58995,0.05626,0.29837],"force_p95":0.07361,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0968,"mean_force":0.04925,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.58939,0.07527,0.2978]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4878.0,"contact_point_centroid":[0.53053,0.01994,0.02861],"force_p95":0.06812,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09627,"mean_force":0.04479,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52946,0.00086,0.02681]}],"total_contact_groups":16},"final_pose_error":0.01341,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.64785,0.15221,0.01602],"final_tcp_position":[0.64006,0.14908,0.46549],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":167951.73011,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":323.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":40.32833,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1288.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.53474,0.00093,0.14728],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12164,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.53786,0.00101,0.03654],"tcp_start":[0.53474,0.00093,0.14728],"tcp_to_object_dist_end":0.01234,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54416,0.00073,0.02588],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25053,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12987,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10793.0,"raw_peak_contact_force":0.15902,"subtask_id":"grasp_object","tcp_end":[0.52942,0.00086,0.02677],"tcp_start":[0.53786,0.00101,0.03654],"tcp_to_object_dist_end":0.01477,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":757.0,"n_steps_budget":1000.0,"object_pos_end":[0.55191,0.0007,0.21824],"object_pos_start":[0.54416,0.00073,0.02588],"object_to_goal_dist_end":0.18619,"object_to_goal_dist_start":0.25053,"object_z_max":0.21799,"peak_contact_force":0.08114,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":28307.0,"raw_peak_contact_force":0.57069,"subtask_id":"lift_object","tcp_end":[0.54014,0.00068,0.22661],"tcp_start":[0.52942,0.00086,0.02677],"tcp_to_object_dist_end":0.01444,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":881.0,"n_steps_budget":1000.0,"object_pos_end":[0.64981,0.15027,0.35911],"object_pos_start":[0.55191,0.0007,0.21824],"object_to_goal_dist_end":0.1682,"object_to_goal_dist_start":0.18619,"object_z_max":0.35897,"peak_contact_force":0.09265,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":34093.0,"raw_peak_contact_force":0.10567,"subtask_id":"transport_to_goal","tcp_end":[0.64161,0.14994,0.37421],"tcp_start":[0.54014,0.00068,0.22661],"tcp_to_object_dist_end":0.01719,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":55.0,"n_steps_budget":1000.0,"object_pos_end":[0.64712,0.14981,0.34343],"object_pos_start":[0.64981,0.15027,0.35911],"object_to_goal_dist_end":0.15255,"object_to_goal_dist_start":0.1682,"object_z_max":0.35911,"peak_contact_force":167951.73011,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2084.0,"raw_peak_contact_force":0.1828,"subtask_id":"place_at_goal","tcp_end":[0.64105,0.15004,0.35948],"tcp_start":[0.64161,0.14994,0.37421],"tcp_to_object_dist_end":0.01716,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.64497,0.14732,-0.01029],"object_pos_start":[0.64712,0.14981,0.34343],"object_to_goal_dist_end":0.2017,"object_to_goal_dist_start":0.15255,"object_z_max":0.34343,"peak_contact_force":1.12755,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2213.0,"raw_peak_contact_force":2.63403,"subtask_id":"place_at_goal","tcp_end":[0.63954,0.14923,0.37787],"tcp_start":[0.64105,0.15004,0.35948],"tcp_to_object_dist_end":0.3882,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":874.0,"n_steps_budget":990.0,"object_pos_end":[0.64785,0.15221,0.01602],"object_pos_start":[0.64497,0.14732,-0.01029],"object_to_goal_dist_end":0.17518,"object_to_goal_dist_start":0.2017,"object_z_max":0.01723,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3496.0,"raw_peak_contact_force":1.06158,"tcp_end":[0.64006,0.14908,0.46549],"tcp_start":[0.63954,0.14923,0.37787],"tcp_to_object_dist_end":0.44955,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `e1209649252ffcf03853fe0727696e22a1eda11729c6c1ae21659980557d7e98`; realized-scene SHA-256: `e32d7866764afb23ec7c7faebb4bcca0aa39fbf2f1ab61f3c9c527b297153af9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5305,0.03079,0.03]},{"name":"goal","value":[0.60153,0.17858,0.10809]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5305,0.03079,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.60153,0.17858,0.10809]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.0,"average_solve_count":334.0,"average_success_count":334.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.0665,"descend_1.speed":0.08683,"descend_2.place_force_threshold":9.20163,"descend_2.speed":0.03433,"lift_1.lift_height":0.1488,"lift_1.speed":0.01028,"retract_1.retract_height":0.14193,"retract_1.speed":0.06356,"transport_1.speed":0.04621,"transport_1.transport_height":0.13565},"optimized_scores":{"best_composite_score":0.19182,"best_fitness_score":0.74682,"best_task_score":0.53839},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":177.0,"contact_point_centroid":[0.59821,0.16676,-0.00813],"force_p95":1.44811,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.93034,"mean_force":0.44989,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58632,0.1656,0.22738]},{"body_a":"world","body_b":"grasp_target","contact_count":113.0,"contact_point_centroid":[0.52671,0.02888,-0.0016],"force_p95":0.47827,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55325,"mean_force":0.21463,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51527,0.02932,0.02497]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10263.0,"contact_point_centroid":[0.519,0.04819,0.08782],"force_p95":0.07805,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25402,"mean_force":0.05258,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51868,0.02913,0.08575]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53055,0.03044,-0.00212],"force_p95":0.15996,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24652,"mean_force":0.13268,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51765,0.0295,0.02551]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9360.0,"contact_point_centroid":[0.51923,0.00998,0.08957],"force_p95":0.08328,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24018,"mean_force":0.05599,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5188,0.02913,0.08689]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4052.0,"contact_point_centroid":[0.51732,0.01022,0.0269],"force_p95":0.08065,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14175,"mean_force":0.0519,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51641,0.02942,0.02414]},{"body_a":"world","body_b":"grasp_target","contact_count":1252.0,"contact_point_centroid":[0.5305,0.03079,-0.00189],"force_p95":0.13606,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12302,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51029,0.01265,0.22516]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.60034,0.16644,-0.002],"force_p95":0.1229,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1257,"mean_force":0.12136,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.58393,0.1648,0.28367]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1231.0,"contact_point_centroid":[0.59006,0.18599,0.2115],"force_p95":0.07217,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12381,"mean_force":0.04345,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58965,0.16674,0.21003]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52254,0.02846,0.07616]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1344.0,"contact_point_centroid":[0.59248,0.18677,0.22305],"force_p95":0.07351,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11778,"mean_force":0.05048,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.59224,0.16761,0.22239]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1344.0,"contact_point_centroid":[0.59253,0.14843,0.22338],"force_p95":0.07243,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11326,"mean_force":0.04901,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.59224,0.16761,0.22239]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1308.0,"contact_point_centroid":[0.5898,0.14757,0.21194],"force_p95":0.06864,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10103,"mean_force":0.04089,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58972,0.16676,0.21017]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13069.0,"contact_point_centroid":[0.55939,0.08181,0.19308],"force_p95":0.07053,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09462,"mean_force":0.04739,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55918,0.10092,0.19163]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4996.0,"contact_point_centroid":[0.51725,0.04858,0.02594],"force_p95":0.07302,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09053,"mean_force":0.04485,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51642,0.02942,0.02415]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12052.0,"contact_point_centroid":[0.56058,0.12227,0.19425],"force_p95":0.07251,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08753,"mean_force":0.05096,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.56028,0.10307,0.19284]}],"total_contact_groups":16},"final_pose_error":0.0403,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.60034,0.16644,0.01602],"final_tcp_position":[0.58441,0.16489,0.33598],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":1573.09317,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":314.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":35.42938,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1252.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.52283,0.02629,0.14776],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12206,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.52473,0.02997,0.03347],"tcp_start":[0.52283,0.02629,0.14776],"tcp_to_object_dist_end":0.00946,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53037,0.02937,0.02559],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18476,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.15144,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10848.0,"raw_peak_contact_force":0.24652,"subtask_id":"grasp_object","tcp_end":[0.51639,0.02941,0.02411],"tcp_start":[0.52473,0.02997,0.03347],"tcp_to_object_dist_end":0.01406,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":510.0,"n_steps_budget":1000.0,"object_pos_end":[0.53792,0.02917,0.15231],"object_pos_start":[0.53037,0.02937,0.02559],"object_to_goal_dist_end":0.1683,"object_to_goal_dist_start":0.18476,"object_z_max":0.15206,"peak_contact_force":0.08346,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":19736.0,"raw_peak_contact_force":0.55325,"subtask_id":"lift_object","tcp_end":[0.52533,0.02911,0.15525],"tcp_start":[0.51639,0.02941,0.02411],"tcp_to_object_dist_end":0.01293,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":612.0,"n_steps_budget":1000.0,"object_pos_end":[0.60437,0.16732,0.22064],"object_pos_start":[0.53792,0.02917,0.15231],"object_to_goal_dist_end":0.11314,"object_to_goal_dist_start":0.1683,"object_z_max":0.22053,"peak_contact_force":0.07026,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":25121.0,"raw_peak_contact_force":0.09462,"subtask_id":"transport_to_goal","tcp_end":[0.59335,0.16738,0.22955],"tcp_start":[0.52533,0.02911,0.15525],"tcp_to_object_dist_end":0.01418,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":64.0,"n_steps_budget":1000.0,"object_pos_end":[0.60093,0.16703,0.2043],"object_pos_start":[0.60437,0.16732,0.22064],"object_to_goal_dist_end":0.0969,"object_to_goal_dist_start":0.11314,"object_z_max":0.22066,"peak_contact_force":1573.09317,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2688.0,"raw_peak_contact_force":0.11778,"subtask_id":"place_at_goal","tcp_end":[0.59133,0.16726,0.21397],"tcp_start":[0.59335,0.16738,0.22955],"tcp_to_object_dist_end":0.01363,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59995,0.16571,0.01169],"object_pos_start":[0.60093,0.16703,0.2043],"object_to_goal_dist_end":0.09727,"object_to_goal_dist_start":0.0969,"object_z_max":0.2043,"peak_contact_force":0.07476,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2716.0,"raw_peak_contact_force":1.93034,"subtask_id":"place_at_goal","tcp_end":[0.58629,0.16559,0.2343],"tcp_start":[0.59133,0.16726,0.21397],"tcp_to_object_dist_end":0.22303,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.60034,0.16644,0.01602],"object_pos_start":[0.59995,0.16571,0.01169],"object_to_goal_dist_end":0.09288,"object_to_goal_dist_start":0.09727,"object_z_max":0.01664,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.1257,"tcp_end":[0.58441,0.16489,0.33598],"tcp_start":[0.58629,0.16559,0.2343],"tcp_to_object_dist_end":0.32036,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```