## Search State

- **Seed**: 3
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.3766 | 0.95 | ❌ rejected |
| 3 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.4037 | 1.00 | ✅ accepted |
| 2 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.1237 | 0.43 | ✅ accepted |
| 1 | approach → descend → grasp → lift → release | linear_cartesian | linear_cartesian | — | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | 5 | 0.2342 | 0.20 | ❌ rejected |
| 0 | approach → descend → grasp → lift → release | linear_cartesian | linear_cartesian | — | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | 5 | 0.2349 | 0.20 | ✅ accepted |

**Proposal policy**: task_score is near-perfect (0.95). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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

## Current Skill (Q=0.377) — your mutation base

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

- **Composite score**: 0.377
- **task_score** (E): 0.946
- **fitness_score**: 0.947  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.570

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2054 |
| descend_1 | 1.00 | 1.00 | 0.0555 |
| grasp_1 | 1.00 | 1.00 | 0.0118 |
| lift_1 | 1.00 | 1.00 | 0.1367 |
| transport_to_goal | 1.00 | 1.00 | 0.2403 |
| place_object | 1.00 | 1.00 | 0.1262 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.002, 0.099) | (0.511, 0.002, 0.030)→(0.511, 0.002, 0.026) | 0.244→0.246 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.506, 0.002, 0.099)→(0.505, 0.002, 0.044) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.505, 0.002, 0.044)→(0.497, 0.002, 0.035) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 42.667 | 0.141 | 0.194 |
| lift_1 | lift | 1.00 / step_budget | (0.497, 0.002, 0.035)→(0.494, 0.001, 0.172) | (0.511, 0.002, 0.026)→(0.505, 0.002, 0.158) | 0.246→0.225 | 1.00 / 34.667 | 0.086 | 0.524 |
| transport_to_goal | approach | 1.00 / step_budget | (0.494, 0.001, 0.172)→(0.618, 0.172, 0.273) | (0.505, 0.002, 0.158)→(0.625, 0.172, 0.253) | 0.225→0.116 | 1.00 / 34.333 | 0.080 | 0.118 |
| place_object | descend | 1.00 / step_budget | (0.618, 0.172, 0.273)→(0.621, 0.179, 0.147) | (0.625, 0.172, 0.253)→(0.623, 0.178, 0.126) | 0.116→0.018 | 1.00 / 32.667 | 0.086 | 0.192 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.590
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.366
- phase_breakdown.approach_1_score: 0.243
- phase_breakdown.release_1_score: 0.598
- phase_breakdown.descend_1_score: 0.802
- phase_breakdown.transport_arc_score: 0.062
- phase_breakdown.grasp_1_score: 1.000
- grasp_place_fitness: 0.978

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.978
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.398
- **K-run variance**: 0.0014
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.467


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.09392,"average_solve_count":362.0,"average_success_count":362.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.05111,"approach_1.approach_speed":0.09792,"descend_1.descend_speed":0.04038,"descend_1.grasp_z_offset":0.01135,"lift_1.lift_height":0.18199,"lift_1.lift_speed":0.04507,"place_object.place_speed":0.03374,"place_object.place_z_offset":0.00642,"transport_to_goal.transport_speed":0.04763},"optimized_scores":{"best_composite_score":0.40845,"best_fitness_score":0.97845,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":81.0,"contact_point_centroid":[0.45431,-0.02515,-0.00144],"force_p95":0.54134,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55638,"mean_force":0.21781,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44595,-0.02552,0.0339]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10575.0,"contact_point_centroid":[0.4438,-0.04456,0.11479],"force_p95":0.07538,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27347,"mean_force":0.05224,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44359,-0.02541,0.11295]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10568.0,"contact_point_centroid":[0.44378,-0.00626,0.11492],"force_p95":0.07392,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27111,"mean_force":0.05202,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44358,-0.02541,0.113]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45857,-0.02618,-0.00206],"force_p95":0.14213,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19425,"mean_force":0.12783,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44798,-0.02559,0.03379]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3524.0,"contact_point_centroid":[0.62269,0.21917,0.19916],"force_p95":0.08663,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16263,"mean_force":0.05975,"phase_index":5.0,"phase_name":"place_object","phase_type":"descend","tcp_position_centroid":[0.62088,0.20011,0.19848]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3550.0,"contact_point_centroid":[0.62244,0.18107,0.2021],"force_p95":0.08679,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15862,"mean_force":0.0572,"phase_index":5.0,"phase_name":"place_object","phase_type":"descend","tcp_position_centroid":[0.6208,0.19998,0.20061]},{"body_a":"world","body_b":"grasp_target","contact_count":1524.0,"contact_point_centroid":[0.45856,-0.02632,-0.00191],"force_p95":0.13468,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12295,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47985,-0.0113,0.20155]},{"body_a":"world","body_b":"grasp_target","contact_count":1520.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45547,-0.0245,0.06836]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4821.0,"contact_point_centroid":[0.44688,-0.00633,0.03505],"force_p95":0.06854,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10073,"mean_force":0.04489,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4469,-0.02555,0.03276]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20253.0,"contact_point_centroid":[0.53308,0.07054,0.22485],"force_p95":0.0683,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09197,"mean_force":0.04598,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5332,0.0896,0.2231]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17371.0,"contact_point_centroid":[0.5353,0.11113,0.22627],"force_p95":0.07738,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08142,"mean_force":0.0524,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53506,0.09192,0.22373]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5216.0,"contact_point_centroid":[0.44667,-0.04479,0.03454],"force_p95":0.0672,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07761,"mean_force":0.04264,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4469,-0.02555,0.03276]}],"total_contact_groups":12},"final_pose_error":0.0196,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.63222,0.2043,0.12102],"final_tcp_position":[0.62423,0.20446,0.13885],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":0.55638,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":382.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1524.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.45989,-0.02326,0.10056],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.07462,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":380.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1520.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.45428,-0.02582,0.03982],"tcp_start":[0.45989,-0.02326,0.10056],"tcp_to_object_dist_end":0.01446,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45846,-0.02564,0.02577],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30326,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.13932,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11837.0,"raw_peak_contact_force":0.19425,"subtask_id":"grasp_1","tcp_end":[0.44687,-0.02555,0.03273],"tcp_start":[0.45428,-0.02582,0.03982],"tcp_to_object_dist_end":0.01352,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":528.0,"n_steps_budget":1000.0,"object_pos_end":[0.45301,-0.02543,0.18491],"object_pos_start":[0.45846,-0.02564,0.02577],"object_to_goal_dist_end":0.30162,"object_to_goal_dist_start":0.30326,"object_z_max":0.18462,"peak_contact_force":0.07355,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":21224.0,"raw_peak_contact_force":0.55638,"tcp_end":[0.44376,-0.0254,0.19512],"tcp_start":[0.44687,-0.02555,0.03273],"tcp_to_object_dist_end":0.01378,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":935.0,"n_steps_budget":1000.0,"object_pos_end":[0.62521,0.19677,0.23612],"object_pos_start":[0.45301,-0.02543,0.18491],"object_to_goal_dist_end":0.12263,"object_to_goal_dist_start":0.30162,"object_z_max":0.23608,"peak_contact_force":0.06821,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":37624.0,"raw_peak_contact_force":0.09197,"subtask_id":"transport_arc","tcp_end":[0.61918,0.19667,0.25222],"tcp_start":[0.44376,-0.0254,0.19512],"tcp_to_object_dist_end":0.01719,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":209.0,"n_steps_budget":1000.0,"object_pos_end":[0.63222,0.2043,0.12102],"object_pos_start":[0.62521,0.19677,0.23612],"object_to_goal_dist_end":0.00821,"object_to_goal_dist_start":0.12263,"object_z_max":0.23612,"peak_contact_force":0.08842,"phase_name":"place_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7074.0,"raw_peak_contact_force":0.16263,"subtask_id":"release_1","tcp_end":[0.62423,0.20446,0.13885],"tcp_start":[0.61918,0.19667,0.25222],"tcp_to_object_dist_end":0.01954,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.29889,"average_solve_count":271.0,"average_success_count":271.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.0513,"approach_1.approach_speed":0.09607,"descend_1.descend_speed":0.03711,"descend_1.grasp_z_offset":0.01259,"lift_1.lift_height":0.13573,"lift_1.lift_speed":0.06202,"place_object.place_speed":0.09404,"place_object.place_z_offset":-0.00877,"transport_to_goal.transport_speed":0.03462},"optimized_scores":{"best_composite_score":0.3978,"best_fitness_score":0.9678,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":85.0,"contact_point_centroid":[0.54154,0.00055,-0.00137],"force_p95":0.40103,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.47621,"mean_force":0.11833,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52753,0.00082,0.0407]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7149.0,"contact_point_centroid":[0.52681,-0.01817,0.09692],"force_p95":0.09831,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30451,"mean_force":0.06254,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52482,0.00078,0.09524]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7406.0,"contact_point_centroid":[0.52653,0.01976,0.09457],"force_p95":0.10276,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29207,"mean_force":0.06094,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52486,0.00078,0.09283]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2704.0,"contact_point_centroid":[0.64643,0.17169,0.26222],"force_p95":0.13317,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24315,"mean_force":0.08479,"phase_index":5.0,"phase_name":"place_object","phase_type":"descend","tcp_position_centroid":[0.64175,0.15309,0.26259]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2794.0,"contact_point_centroid":[0.6464,0.13435,0.26169],"force_p95":0.13742,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23445,"mean_force":0.08496,"phase_index":5.0,"phase_name":"place_object","phase_type":"descend","tcp_position_centroid":[0.64176,0.15312,0.26174]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12808.0,"contact_point_centroid":[0.58629,0.05803,0.23945],"force_p95":0.10729,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16598,"mean_force":0.07276,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.58176,0.07667,0.23859]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54431,0.00103,-0.00203],"force_p95":0.13242,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15383,"mean_force":0.12542,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52997,0.00087,0.04104]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12765.0,"contact_point_centroid":[0.58811,0.09706,0.2418],"force_p95":0.10215,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15282,"mean_force":0.07232,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5831,0.0784,0.24054]},{"body_a":"world","body_b":"grasp_target","contact_count":1576.0,"contact_point_centroid":[0.54431,0.00113,-0.00191],"force_p95":0.13468,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12294,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51676,0.00046,0.20059]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4115.0,"contact_point_centroid":[0.53014,-0.01835,0.04224],"force_p95":0.07628,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12265,"mean_force":0.05181,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52873,0.00085,0.0396]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53493,0.00095,0.06583]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4878.0,"contact_point_centroid":[0.53003,0.01993,0.04137],"force_p95":0.06837,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09454,"mean_force":0.0447,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52874,0.00085,0.0396]}],"total_contact_groups":12},"final_pose_error":0.01995,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.64378,0.15493,0.1728],"final_tcp_position":[0.64339,0.15571,0.20168],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":0.47621,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":395.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1576.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.53567,0.00095,0.09905],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.07354,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53694,0.00099,0.0493],"tcp_start":[0.53567,0.00095,0.09905],"tcp_to_object_dist_end":0.02442,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54421,0.00075,0.02587],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.2505,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.13063,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10793.0,"raw_peak_contact_force":0.15383,"subtask_id":"grasp_1","tcp_end":[0.5287,0.00085,0.03956],"tcp_start":[0.53694,0.00099,0.0493],"tcp_to_object_dist_end":0.02068,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":416.0,"n_steps_budget":1000.0,"object_pos_end":[0.53866,0.00098,0.13737],"object_pos_start":[0.54421,0.00075,0.02587],"object_to_goal_dist_end":0.1986,"object_to_goal_dist_start":0.2505,"object_z_max":0.13712,"peak_contact_force":0.10569,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":14640.0,"raw_peak_contact_force":0.47621,"tcp_end":[0.52486,0.00079,0.15591],"tcp_start":[0.5287,0.00085,0.03956],"tcp_to_object_dist_end":0.02312,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":983.0,"n_steps_budget":1000.0,"object_pos_end":[0.64793,0.15064,0.29704],"object_pos_start":[0.53866,0.00098,0.13737],"object_to_goal_dist_end":0.1062,"object_to_goal_dist_start":0.1986,"object_z_max":0.2969,"peak_contact_force":0.09427,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":25573.0,"raw_peak_contact_force":0.16598,"subtask_id":"transport_arc","tcp_end":[0.64071,0.15067,0.32386],"tcp_start":[0.52486,0.00079,0.15591],"tcp_to_object_dist_end":0.02778,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":207.0,"n_steps_budget":1000.0,"object_pos_end":[0.64378,0.15493,0.1728],"object_pos_start":[0.64793,0.15064,0.29704],"object_to_goal_dist_end":0.01897,"object_to_goal_dist_start":0.1062,"object_z_max":0.29706,"peak_contact_force":0.09379,"phase_name":"place_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5498.0,"raw_peak_contact_force":0.24315,"subtask_id":"release_1","tcp_end":[0.64339,0.15571,0.20168],"tcp_start":[0.64071,0.15067,0.32386],"tcp_to_object_dist_end":0.0289,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.3321,"average_solve_count":271.0,"average_success_count":271.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.05017,"approach_1.approach_speed":0.07266,"descend_1.descend_speed":0.04322,"descend_1.grasp_z_offset":0.01247,"lift_1.lift_height":0.15066,"lift_1.lift_speed":0.0465,"place_object.place_speed":0.08507,"place_object.place_z_offset":-0.02557,"transport_to_goal.transport_speed":0.05295},"optimized_scores":{"best_composite_score":0.32368,"best_fitness_score":0.89368,"best_task_score":0.83829},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":90.0,"contact_point_centroid":[0.52611,0.02859,-0.00152],"force_p95":0.51387,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.53835,"mean_force":0.18662,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51513,0.02925,0.03444]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9459.0,"contact_point_centroid":[0.51283,0.04814,0.09742],"force_p95":0.07878,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29639,"mean_force":0.05336,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5125,0.02907,0.09535]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8641.0,"contact_point_centroid":[0.51296,0.00992,0.09925],"force_p95":0.08259,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28971,"mean_force":0.0568,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51251,0.02908,0.09658]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53056,0.03054,-0.00213],"force_p95":0.16097,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23536,"mean_force":0.13277,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51751,0.02941,0.03466]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5361.0,"contact_point_centroid":[0.59387,0.19042,0.1756],"force_p95":0.08124,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17072,"mean_force":0.05245,"phase_index":5.0,"phase_name":"place_object","phase_type":"descend","tcp_position_centroid":[0.59375,0.17138,0.17388]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5049.0,"contact_point_centroid":[0.59393,0.15227,0.17319],"force_p95":0.08538,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16242,"mean_force":0.05477,"phase_index":5.0,"phase_name":"place_object","phase_type":"descend","tcp_position_centroid":[0.59382,0.17153,0.17094]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4071.0,"contact_point_centroid":[0.51723,0.01013,0.03602],"force_p95":0.0808,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15223,"mean_force":0.05187,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51629,0.02933,0.03328]},{"body_a":"world","body_b":"grasp_target","contact_count":1604.0,"contact_point_centroid":[0.5305,0.03079,-0.00191],"force_p95":0.13462,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12293,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51052,0.01319,0.20036]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52248,0.02879,0.06158]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12146.0,"contact_point_centroid":[0.55235,0.07954,0.20417],"force_p95":0.07589,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09511,"mean_force":0.05142,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55136,0.09856,0.20207]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11320.0,"contact_point_centroid":[0.55443,0.12115,0.20641],"force_p95":0.07873,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09123,"mean_force":0.05474,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55344,0.10204,0.20415]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5001.0,"contact_point_centroid":[0.51716,0.04849,0.03508],"force_p95":0.07355,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08426,"mean_force":0.04459,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51629,0.02933,0.03328]}],"total_contact_groups":12},"final_pose_error":0.01998,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.59343,0.17485,0.08318],"final_tcp_position":[0.59608,0.17548,0.10149],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":0.53835,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":402.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1604.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52339,0.02721,0.09823],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.07265,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.52443,0.02987,0.04256],"tcp_start":[0.52339,0.02721,0.09823],"tcp_to_object_dist_end":0.01764,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53042,0.02946,0.02555],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18468,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.15334,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10872.0,"raw_peak_contact_force":0.23536,"subtask_id":"grasp_1","tcp_end":[0.51626,0.02933,0.03324],"tcp_start":[0.52443,0.02987,0.04256],"tcp_to_object_dist_end":0.01612,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":470.0,"n_steps_budget":1000.0,"object_pos_end":[0.52372,0.02924,0.15288],"object_pos_start":[0.53042,0.02946,0.02555],"object_to_goal_dist_end":0.17425,"object_to_goal_dist_start":0.18468,"object_z_max":0.15262,"peak_contact_force":0.07948,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":18190.0,"raw_peak_contact_force":0.53835,"tcp_end":[0.5126,0.02908,0.1645],"tcp_start":[0.51626,0.02933,0.03324],"tcp_to_object_dist_end":0.01609,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":36.0,"n_steps":635.0,"n_steps_budget":1000.0,"object_pos_end":[0.60054,0.16778,0.22718],"object_pos_start":[0.52372,0.02924,0.15288],"object_to_goal_dist_end":0.11958,"object_to_goal_dist_start":0.17425,"object_z_max":0.22708,"peak_contact_force":0.07793,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":23466.0,"raw_peak_contact_force":0.09511,"subtask_id":"transport_arc","tcp_end":[0.59293,0.16788,0.24385],"tcp_start":[0.5126,0.02908,0.1645],"tcp_to_object_dist_end":0.01833,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":252.0,"n_steps_budget":1000.0,"object_pos_end":[0.59343,0.17485,0.08318],"object_pos_start":[0.60054,0.16778,0.22718],"object_to_goal_dist_end":0.02646,"object_to_goal_dist_start":0.11958,"object_z_max":0.2272,"peak_contact_force":0.0767,"phase_name":"place_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10410.0,"raw_peak_contact_force":0.17072,"subtask_id":"release_1","tcp_end":[0.59608,0.17548,0.10149],"tcp_start":[0.59293,0.16788,0.24385],"tcp_to_object_dist_end":0.01851,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```