## Search State

- **Seed**: 3
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 12 | -0.0777 | 0.48 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.3766 | 0.95 | ❌ rejected |
| 3 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.4037 | 1.00 | ✅ accepted |
| 2 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.1237 | 0.43 | ✅ accepted |
| 1 | approach → descend → grasp → lift → release | linear_cartesian | linear_cartesian | — | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | 5 | 0.2342 | 0.20 | ❌ rejected |

**Proposal policy**: task_score is 0.48 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

**Mode**: fixed (subtask targets are defined by the task configuration)

Available subtask IDs for phase binding:
| Subtask ID | Anchor | Target offset (m) | Metric | CMA-ES offset param |
|---|---|---|---|---|
| approach_1 | object | (0.00, 0.00, 0.00) | distance | approach_height |
| descend_1 | object | (0.00, 0.00, 0.02) | distance | grasp_z_offset |
| grasp_1 | object | (0.00, 0.00, 0.02) | contact | — |
| transport_arc | goal | (0.00, 0.00, 0.00) | distance | — |
| release_1 | goal | (0.00, 0.00, 0.00) | distance | — |

Annotate phases with `subtask_id: <id>` to bind them to a subtask target.
- A phase bound to a subtask receives a navigation waypoint computed from that subtask's anchor and offset.
- Only the **last phase** bound to a given subtask is used for subtask scoring.
- Phases without `subtask_id` are not scored against subtasks but still execute normally.

## Current Skill (Q=-0.078) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
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
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_1
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
    - 0.02
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
    grasp_z_offset:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: descend_1
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
  subtask_id: grasp_1
- id: lift_1
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
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.05
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
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
    transport_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: transport_arc
- id: place_object
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
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    place_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    place_z_offset:
      type: scalar
      range:
      - -0.05
      - 0.05
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: release_1

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.02], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - grasp_z_offset: status=consumed; consumers=target.offset.z (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **lift_1** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
- **transport_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **place_object** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_speed: status=consumed; consumers=generator.speed (replace)
    - place_z_offset: status=consumed; consumers=target.offset.z (replace)

## Design Metrics

- **Composite score**: -0.078
- **task_score** (E): 0.479
- **fitness_score**: 0.702  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.780

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1058 |
| descend_1 | 1.00 | 1.00 | 0.1465 |
| grasp_1 | 1.00 | 1.00 | 0.0128 |
| lift_1 | 1.00 | 1.00 | 0.1534 |
| transport_to_goal | 1.00 | 1.00 | 0.2190 |
| place_object | 1.00 | 1.00 | 0.1373 |
| release_at_goal | 1.00 | 1.00 | 0.0196 |
| retract_from_goal | 1.00 | 1.00 | 0.1049 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.507, 0.002, 0.202) | (0.511, 0.002, 0.030)→(0.511, 0.002, 0.026) | 0.244→0.246 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.507, 0.002, 0.202)→(0.506, 0.002, 0.055) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 4.000 | 11.401 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.506, 0.002, 0.055)→(0.498, 0.002, 0.046) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 42.000 | 0.146 | 0.195 |
| lift_1 | lift | 1.00 / step_budget | (0.498, 0.002, 0.046)→(0.495, 0.002, 0.199) | (0.511, 0.002, 0.026)→(0.502, 0.002, 0.175) | 0.246→0.224 | 1.00 / 37.667 | 0.079 | 0.391 |
| transport_to_goal | approach | 1.00 / step_budget | (0.495, 0.002, 0.199)→(0.615, 0.168, 0.273) | (0.502, 0.002, 0.175)→(0.619, 0.168, 0.245) | 0.224→0.108 | 1.00 / 31.000 | 0.092 | 0.128 |
| place_object | descend | 1.00 / step_budget | (0.615, 0.168, 0.273)→(0.621, 0.178, 0.136) | (0.619, 0.168, 0.245)→(0.622, 0.177, 0.106) | 0.108→0.033 | 1.00 / 29.000 | 0.098 | 0.249 |
| release_at_goal | release | 1.00 / step_budget | (0.621, 0.178, 0.136)→(0.614, 0.176, 0.154) | (0.622, 0.177, 0.106)→(0.603, 0.175, 0.026) | 0.033→0.115 | 1.00 / 4.000 | 0.129 | 1.153 |
| retract_from_goal | retract | 1.00 / step_budget | (0.614, 0.176, 0.154)→(0.623, 0.180, 0.259) | (0.603, 0.175, 0.026)→(0.602, 0.175, 0.026) | 0.115→0.115 | 1.00 / 4.000 | 9.148 | 0.151 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.566
- phase_score: 0.403
- phase_breakdown.approach_1_score: 0.072
- phase_breakdown.release_1_score: 0.854
- phase_breakdown.descend_1_score: 0.861
- phase_breakdown.transport_arc_score: 0.064
- phase_breakdown.grasp_1_score: 1.000
- grasp_place_fitness: 0.746

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.746
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.566
- **Median Q (composite search score)**: -0.047
- **K-run variance**: 0.0028
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.320


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.9951,"average_solve_count":408.0,"average_success_count":408.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.17849,"approach_1.approach_speed":0.06178,"descend_1.descend_speed":0.03381,"descend_1.grasp_z_offset":0.01048,"lift_1.lift_height":0.11419,"lift_1.lift_speed":0.04238,"place_object.place_speed":0.05446,"place_object.place_z_offset":-0.01796,"release_at_goal.release_duration":0.74836,"retract_from_goal.retract_height":0.11502,"retract_from_goal.retract_speed":0.05847,"transport_to_goal.transport_speed":0.05649},"optimized_scores":{"best_composite_score":-0.04674,"best_fitness_score":0.73326,"best_task_score":0.54277},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":354.0,"contact_point_centroid":[0.60637,0.20274,-0.00326],"force_p95":0.6823,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.94869,"mean_force":0.19671,"phase_index":6.0,"phase_name":"release_at_goal","phase_type":"release","tcp_position_centroid":[0.61599,0.20112,0.11907]},{"body_a":"world","body_b":"grasp_target","contact_count":85.0,"contact_point_centroid":[0.45491,-0.0248,-0.00151],"force_p95":0.35151,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.37588,"mean_force":0.1388,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44704,-0.02506,0.04928]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":674.0,"contact_point_centroid":[0.62101,0.22167,0.10485],"force_p95":0.12713,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36899,"mean_force":0.08147,"phase_index":6.0,"phase_name":"release_at_goal","phase_type":"release","tcp_position_centroid":[0.62047,0.2028,0.10824]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":823.0,"contact_point_centroid":[0.62096,0.18419,0.10517],"force_p95":0.10965,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35064,"mean_force":0.06622,"phase_index":6.0,"phase_name":"release_at_goal","phase_type":"release","tcp_position_centroid":[0.62051,0.20281,0.10829]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6240.0,"contact_point_centroid":[0.44492,-0.04395,0.09518],"force_p95":0.08404,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26533,"mean_force":0.05531,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44481,-0.02496,0.09422]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2921.0,"contact_point_centroid":[0.61833,0.17808,0.17879],"force_p95":0.1232,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26113,"mean_force":0.08374,"phase_index":5.0,"phase_name":"place_object","phase_type":"descend","tcp_position_centroid":[0.61796,0.19666,0.18185]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5304.0,"contact_point_centroid":[0.44575,-0.00579,0.095],"force_p95":0.08602,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25949,"mean_force":0.06296,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44481,-0.02496,0.09422]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2824.0,"contact_point_centroid":[0.61933,0.21532,0.17837],"force_p95":0.11967,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24535,"mean_force":0.08549,"phase_index":5.0,"phase_name":"place_object","phase_type":"descend","tcp_position_centroid":[0.61796,0.19668,0.18139]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45859,-0.02623,-0.0021],"force_p95":0.152,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20804,"mean_force":0.13031,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44908,-0.02514,0.04914]},{"body_a":"world","body_b":"grasp_target","contact_count":1496.0,"contact_point_centroid":[0.6054,0.20289,-0.00199],"force_p95":0.12725,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14769,"mean_force":0.12274,"phase_index":7.0,"phase_name":"retract_from_goal","phase_type":"retract","tcp_position_centroid":[0.61952,0.20332,0.17042]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4097.0,"contact_point_centroid":[0.44898,-0.00589,0.04899],"force_p95":0.07965,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14766,"mean_force":0.05216,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44804,-0.0251,0.04814]},{"body_a":"world","body_b":"grasp_target","contact_count":660.0,"contact_point_centroid":[0.45856,-0.02632,-0.00181],"force_p95":0.13762,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12337,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48375,-0.00931,0.26442]},{"body_a":"world","body_b":"grasp_target","contact_count":1396.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.46012,-0.02257,0.14205]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18397.0,"contact_point_centroid":[0.52564,0.06231,0.19228],"force_p95":0.08295,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11922,"mean_force":0.05243,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5263,0.08104,0.19227]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14876.0,"contact_point_centroid":[0.52461,0.09814,0.19038],"force_p95":0.10129,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11504,"mean_force":0.06547,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52477,0.07911,0.19131]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4962.0,"contact_point_centroid":[0.44816,-0.04419,0.0492],"force_p95":0.07089,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07365,"mean_force":0.04413,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44804,-0.0251,0.04814]}],"total_contact_groups":16},"final_pose_error":0.01996,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.60539,0.2029,0.02602],"final_tcp_position":[0.62548,0.20625,0.20982],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":16.03276,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":166.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12264,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":660.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.46614,-0.02001,0.22561],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.19983,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":349.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1396.0,"raw_peak_contact_force":0.12264,"subtask_id":"descend_1","tcp_end":[0.4558,-0.02535,0.05597],"tcp_start":[0.46614,-0.02001,0.22561],"tcp_to_object_dist_end":0.03009,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45851,-0.02545,0.02562],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30312,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.14909,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10859.0,"raw_peak_contact_force":0.20804,"subtask_id":"grasp_1","tcp_end":[0.44801,-0.02509,0.04811],"tcp_start":[0.4558,-0.02535,0.05597],"tcp_to_object_dist_end":0.02482,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":312.0,"n_steps_budget":1000.0,"object_pos_end":[0.45186,-0.02518,0.1188],"object_pos_start":[0.45851,-0.02545,0.02562],"object_to_goal_dist_end":0.29373,"object_to_goal_dist_start":0.30312,"object_z_max":0.11851,"peak_contact_force":0.0816,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":11629.0,"raw_peak_contact_force":0.37588,"tcp_end":[0.44456,-0.02494,0.14285],"tcp_start":[0.44801,-0.02509,0.04811],"tcp_to_object_dist_end":0.02513,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.61551,0.18948,0.21594],"object_pos_start":[0.45186,-0.02518,0.1188],"object_to_goal_dist_end":0.10456,"object_to_goal_dist_start":0.29373,"object_z_max":0.21584,"peak_contact_force":0.09557,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":33273.0,"raw_peak_contact_force":0.11922,"subtask_id":"transport_arc","tcp_end":[0.61432,0.19067,0.24681],"tcp_start":[0.44456,-0.02494,0.14285],"tcp_to_object_dist_end":0.03092,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":244.0,"n_steps_budget":1000.0,"object_pos_end":[0.62581,0.20289,0.0814],"object_pos_start":[0.61551,0.18948,0.21594],"object_to_goal_dist_end":0.03343,"object_to_goal_dist_start":0.10456,"object_z_max":0.21594,"peak_contact_force":0.10275,"phase_name":"place_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5745.0,"raw_peak_contact_force":0.26113,"subtask_id":"release_1","tcp_end":[0.62334,0.20364,0.11409],"tcp_start":[0.61432,0.19067,0.24681],"tcp_to_object_dist_end":0.0328,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60478,0.20296,0.0263],"object_pos_start":[0.62581,0.20289,0.0814],"object_to_goal_dist_end":0.09156,"object_to_goal_dist_start":0.03343,"object_z_max":0.0814,"peak_contact_force":0.14779,"phase_name":"release_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1851.0,"raw_peak_contact_force":0.94869,"tcp_end":[0.61584,0.20106,0.13187],"tcp_start":[0.62334,0.20364,0.11409],"tcp_to_object_dist_end":0.10617,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":374.0,"n_steps_budget":1000.0,"object_pos_end":[0.60539,0.2029,0.02602],"object_pos_start":[0.60478,0.20296,0.0263],"object_to_goal_dist_end":0.09166,"object_to_goal_dist_start":0.09156,"object_z_max":0.0263,"peak_contact_force":16.03276,"phase_name":"retract_from_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1496.0,"raw_peak_contact_force":0.14769,"tcp_end":[0.62548,0.20625,0.20982],"tcp_start":[0.61584,0.20106,0.13187],"tcp_to_object_dist_end":0.18493,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.12719,"average_solve_count":456.0,"average_success_count":456.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.17219,"approach_1.approach_speed":0.07837,"descend_1.descend_speed":0.01781,"descend_1.grasp_z_offset":0.01019,"lift_1.lift_height":0.24892,"lift_1.lift_speed":0.04802,"place_object.place_speed":0.07161,"place_object.place_z_offset":-0.01899,"release_at_goal.release_duration":0.52543,"retract_from_goal.retract_height":0.14538,"retract_from_goal.retract_speed":0.0286,"transport_to_goal.transport_speed":0.06606},"optimized_scores":{"best_composite_score":-0.15266,"best_fitness_score":0.62734,"best_task_score":0.32796},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":230.0,"contact_point_centroid":[0.62359,0.14677,-0.00615],"force_p95":1.05258,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.61358,"mean_force":0.30772,"phase_index":6.0,"phase_name":"release_at_goal","phase_type":"release","tcp_position_centroid":[0.63711,0.15354,0.19956]},{"body_a":"world","body_b":"grasp_target","contact_count":89.0,"contact_point_centroid":[0.54063,0.00094,-0.0014],"force_p95":0.39695,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.40705,"mean_force":0.14232,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52832,0.00083,0.04557]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16249.0,"contact_point_centroid":[0.52678,0.01992,0.15876],"force_p95":0.07756,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29096,"mean_force":0.05428,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52589,0.00079,0.15647]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3440.0,"contact_point_centroid":[0.64069,0.16967,0.25635],"force_p95":0.13476,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27113,"mean_force":0.08134,"phase_index":5.0,"phase_name":"place_object","phase_type":"descend","tcp_position_centroid":[0.64021,0.15106,0.25768]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16347.0,"contact_point_centroid":[0.52642,-0.01832,0.15741],"force_p95":0.07848,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26151,"mean_force":0.05416,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52591,0.00079,0.1555]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3892.0,"contact_point_centroid":[0.64019,0.13219,0.25857],"force_p95":0.13455,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23097,"mean_force":0.0834,"phase_index":5.0,"phase_name":"place_object","phase_type":"descend","tcp_position_centroid":[0.64014,0.15095,0.25947]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":981.0,"contact_point_centroid":[0.63962,0.13577,0.18308],"force_p95":0.10562,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18988,"mean_force":0.06076,"phase_index":6.0,"phase_name":"release_at_goal","phase_type":"release","tcp_position_centroid":[0.64072,0.15467,0.18495]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":897.0,"contact_point_centroid":[0.64009,0.17351,0.18298],"force_p95":0.10811,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18266,"mean_force":0.06069,"phase_index":6.0,"phase_name":"release_at_goal","phase_type":"release","tcp_position_centroid":[0.64079,0.15469,0.18511]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9656.0,"contact_point_centroid":[0.58175,0.09037,0.29734],"force_p95":0.08842,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1654,"mean_force":0.06249,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.57947,0.07137,0.29735]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11118.0,"contact_point_centroid":[0.58267,0.05466,0.29836],"force_p95":0.08057,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16236,"mean_force":0.05447,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.58111,0.07352,0.29816]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54431,0.00113,-0.00203],"force_p95":0.13164,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15414,"mean_force":0.12545,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53064,0.00088,0.04591]},{"body_a":"world","body_b":"grasp_target","contact_count":2148.0,"contact_point_centroid":[0.62345,0.14678,-0.00197],"force_p95":0.12691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1509,"mean_force":0.12162,"phase_index":7.0,"phase_name":"retract_from_goal","phase_type":"retract","tcp_position_centroid":[0.6399,0.15499,0.26119]},{"body_a":"world","body_b":"grasp_target","contact_count":728.0,"contact_point_centroid":[0.54431,0.00113,-0.00182],"force_p95":0.13759,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1233,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51473,0.0004,0.26002]},{"body_a":"world","body_b":"grasp_target","contact_count":1296.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53384,0.00091,0.13791]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4825.0,"contact_point_centroid":[0.53035,-0.01823,0.04681],"force_p95":0.0682,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10091,"mean_force":0.04484,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52945,0.00085,0.0445]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4329.0,"contact_point_centroid":[0.53057,0.02007,0.04694],"force_p95":0.07513,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09384,"mean_force":0.04984,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52945,0.00086,0.04451]}],"total_contact_groups":16},"final_pose_error":0.01988,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.62344,0.14677,0.02602],"final_tcp_position":[0.64509,0.15708,0.31679],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":11.28807,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":183.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":728.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.53183,0.00085,0.21779],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.19218,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":324.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1296.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53828,0.00102,0.05528],"tcp_start":[0.53183,0.00085,0.21779],"tcp_to_object_dist_end":0.02987,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54421,0.00108,0.02586],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25029,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.1317,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10954.0,"raw_peak_contact_force":0.15414,"subtask_id":"grasp_1","tcp_end":[0.52942,0.00085,0.04447],"tcp_start":[0.53828,0.00102,0.05528],"tcp_to_object_dist_end":0.02377,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":835.0,"n_steps_budget":1000.0,"object_pos_end":[0.53334,0.00095,0.24859],"object_pos_start":[0.54421,0.00108,0.02586],"object_to_goal_dist_end":0.20263,"object_to_goal_dist_start":0.25029,"object_z_max":0.24833,"peak_contact_force":0.07558,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":32685.0,"raw_peak_contact_force":0.40705,"tcp_end":[0.52678,0.0008,0.27358],"tcp_start":[0.52942,0.00085,0.04447],"tcp_to_object_dist_end":0.02584,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":616.0,"n_steps_budget":1000.0,"object_pos_end":[0.6437,0.14705,0.29972],"object_pos_start":[0.53334,0.00095,0.24859],"object_to_goal_dist_end":0.10925,"object_to_goal_dist_start":0.20263,"object_z_max":0.29966,"peak_contact_force":0.10628,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":20774.0,"raw_peak_contact_force":0.1654,"subtask_id":"transport_arc","tcp_end":[0.63796,0.147,0.32763],"tcp_start":[0.52678,0.0008,0.27358],"tcp_to_object_dist_end":0.02849,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":235.0,"n_steps_budget":1000.0,"object_pos_end":[0.6378,0.15426,0.16057],"object_pos_start":[0.6437,0.14705,0.29972],"object_to_goal_dist_end":0.0323,"object_to_goal_dist_start":0.10925,"object_z_max":0.29972,"peak_contact_force":0.10042,"phase_name":"place_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7332.0,"raw_peak_contact_force":0.27113,"subtask_id":"release_1","tcp_end":[0.643,0.1552,0.19087],"tcp_start":[0.63796,0.147,0.32763],"tcp_to_object_dist_end":0.03076,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.626,0.1481,0.02519],"object_pos_start":[0.6378,0.15426,0.16057],"object_to_goal_dist_end":0.16761,"object_to_goal_dist_start":0.0323,"object_z_max":0.16057,"peak_contact_force":0.08662,"phase_name":"release_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2108.0,"raw_peak_contact_force":1.61358,"tcp_end":[0.63707,0.15353,0.20824],"tcp_start":[0.643,0.1552,0.19087],"tcp_to_object_dist_end":0.18347,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":537.0,"n_steps_budget":1000.0,"object_pos_end":[0.62344,0.14677,0.02602],"object_pos_start":[0.626,0.1481,0.02519],"object_to_goal_dist_end":0.16723,"object_to_goal_dist_start":0.16761,"object_z_max":0.02666,"peak_contact_force":11.28807,"phase_name":"retract_from_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2148.0,"raw_peak_contact_force":0.1509,"tcp_end":[0.64509,0.15708,0.31679],"tcp_start":[0.63707,0.15353,0.20824],"tcp_to_object_dist_end":0.29176,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.04038,"average_solve_count":421.0,"average_success_count":421.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.11398,"approach_1.approach_speed":0.04992,"descend_1.descend_speed":0.03259,"descend_1.grasp_z_offset":0.01,"lift_1.lift_height":0.15565,"lift_1.lift_speed":0.03329,"place_object.place_speed":0.05832,"place_object.place_z_offset":-0.02327,"release_at_goal.release_duration":0.80535,"retract_from_goal.retract_height":0.16098,"retract_from_goal.retract_speed":0.07044,"transport_to_goal.transport_speed":0.04819},"optimized_scores":{"best_composite_score":-0.03372,"best_fitness_score":0.74628,"best_task_score":0.56582},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":350.0,"contact_point_centroid":[0.58006,0.174,-0.00315],"force_p95":0.68254,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.89595,"mean_force":0.20486,"phase_index":6.0,"phase_name":"release_at_goal","phase_type":"release","tcp_position_centroid":[0.58851,0.17304,0.11021]},{"body_a":"world","body_b":"grasp_target","contact_count":98.0,"contact_point_centroid":[0.52661,0.02894,-0.00162],"force_p95":0.37039,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.39084,"mean_force":0.16075,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51493,0.02894,0.04535]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":955.0,"contact_point_centroid":[0.5958,0.19354,0.09745],"force_p95":0.10127,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31669,"mean_force":0.05946,"phase_index":6.0,"phase_name":"release_at_goal","phase_type":"release","tcp_position_centroid":[0.59306,0.17454,0.09836]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":939.0,"contact_point_centroid":[0.59506,0.15561,0.09736],"force_p95":0.09627,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29464,"mean_force":0.05943,"phase_index":6.0,"phase_name":"release_at_goal","phase_type":"release","tcp_position_centroid":[0.59309,0.17455,0.09841]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10891.0,"contact_point_centroid":[0.5124,0.0479,0.111],"force_p95":0.07739,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25664,"mean_force":0.04986,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51241,0.02878,0.1085]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9504.0,"contact_point_centroid":[0.51269,0.00956,0.11125],"force_p95":0.07917,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22898,"mean_force":0.05508,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51242,0.02878,0.10866]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53056,0.03064,-0.00214],"force_p95":0.16147,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22353,"mean_force":0.13319,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51732,0.0291,0.04579]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4253.0,"contact_point_centroid":[0.59564,0.18961,0.17895],"force_p95":0.1002,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21531,"mean_force":0.0647,"phase_index":5.0,"phase_name":"place_object","phase_type":"descend","tcp_position_centroid":[0.59331,0.17065,0.17906]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4266.0,"contact_point_centroid":[0.5949,0.15174,0.17897],"force_p95":0.10394,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18396,"mean_force":0.06332,"phase_index":5.0,"phase_name":"place_object","phase_type":"descend","tcp_position_centroid":[0.59331,0.17063,0.17932]},{"body_a":"world","body_b":"grasp_target","contact_count":2088.0,"contact_point_centroid":[0.57824,0.17428,-0.00199],"force_p95":0.12551,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15336,"mean_force":0.12272,"phase_index":7.0,"phase_name":"retract_from_goal","phase_type":"retract","tcp_position_centroid":[0.59147,0.17461,0.18597]},{"body_a":"world","body_b":"grasp_target","contact_count":1176.0,"contact_point_centroid":[0.5305,0.03079,-0.00189],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12304,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51012,0.01242,0.23219]},{"body_a":"world","body_b":"grasp_target","contact_count":868.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52257,0.02765,0.10941]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4737.0,"contact_point_centroid":[0.51724,0.00986,0.04703],"force_p95":0.07198,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11398,"mean_force":0.04544,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51615,0.02903,0.04446]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11336.0,"contact_point_centroid":[0.55262,0.0805,0.21241],"force_p95":0.07492,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09974,"mean_force":0.05131,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55217,0.0996,0.21126]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11350.0,"contact_point_centroid":[0.55324,0.1186,0.21275],"force_p95":0.07445,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09645,"mean_force":0.05128,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55212,0.09951,0.21122]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5024.0,"contact_point_centroid":[0.51706,0.04833,0.04624],"force_p95":0.07408,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0763,"mean_force":0.04452,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51616,0.02903,0.04447]}],"total_contact_groups":16},"final_pose_error":0.01985,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.57823,0.17428,0.02602],"final_tcp_position":[0.59772,0.17716,0.24964],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":33.95866,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":295.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1176.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.5226,0.02597,0.16146],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13575,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":217.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":33.95866,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":868.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.52478,0.02957,0.05469],"tcp_start":[0.5226,0.02597,0.16146],"tcp_to_object_dist_end":0.02926,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53047,0.02961,0.02549],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18457,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.15666,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11561.0,"raw_peak_contact_force":0.22353,"subtask_id":"grasp_1","tcp_end":[0.51612,0.02902,0.04442],"tcp_start":[0.52478,0.02957,0.05469],"tcp_to_object_dist_end":0.02376,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":496.0,"n_steps_budget":1000.0,"object_pos_end":[0.5218,0.02904,0.15832],"object_pos_start":[0.53047,0.02961,0.02549],"object_to_goal_dist_end":0.17675,"object_to_goal_dist_start":0.18457,"object_z_max":0.15805,"peak_contact_force":0.08033,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":20493.0,"raw_peak_contact_force":0.39084,"tcp_end":[0.51259,0.02879,0.18065],"tcp_start":[0.51612,0.02902,0.04442],"tcp_to_object_dist_end":0.02415,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":597.0,"n_steps_budget":1000.0,"object_pos_end":[0.59728,0.16714,0.21846],"object_pos_start":[0.5218,0.02904,0.15832],"object_to_goal_dist_end":0.11104,"object_to_goal_dist_start":0.17675,"object_z_max":0.21837,"peak_contact_force":0.07443,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":22686.0,"raw_peak_contact_force":0.09974,"subtask_id":"transport_arc","tcp_end":[0.59247,0.16705,0.24452],"tcp_start":[0.51259,0.02879,0.18065],"tcp_to_object_dist_end":0.0265,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":260.0,"n_steps_budget":1000.0,"object_pos_end":[0.60097,0.17534,0.07564],"object_pos_start":[0.59728,0.16714,0.21846],"object_to_goal_dist_end":0.03262,"object_to_goal_dist_start":0.11104,"object_z_max":0.21847,"peak_contact_force":0.09195,"phase_name":"place_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8519.0,"raw_peak_contact_force":0.21531,"subtask_id":"release_1","tcp_end":[0.59593,0.17532,0.1036],"tcp_start":[0.59247,0.16705,0.24452],"tcp_to_object_dist_end":0.02841,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57758,0.17429,0.02632],"object_pos_start":[0.60097,0.17534,0.07564],"object_to_goal_dist_end":0.08531,"object_to_goal_dist_start":0.03262,"object_z_max":0.07564,"peak_contact_force":0.15343,"phase_name":"release_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2244.0,"raw_peak_contact_force":0.89595,"tcp_end":[0.58834,0.17298,0.12303],"tcp_start":[0.59593,0.17532,0.1036],"tcp_to_object_dist_end":0.09731,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":522.0,"n_steps_budget":1000.0,"object_pos_end":[0.57823,0.17428,0.02602],"object_pos_start":[0.57758,0.17429,0.02632],"object_to_goal_dist_end":0.08542,"object_to_goal_dist_start":0.08531,"object_z_max":0.02632,"peak_contact_force":0.12263,"phase_name":"retract_from_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2088.0,"raw_peak_contact_force":0.15336,"tcp_end":[0.59772,0.17716,0.24964],"tcp_start":[0.58834,0.17298,0.12303],"tcp_to_object_dist_end":0.22449,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```