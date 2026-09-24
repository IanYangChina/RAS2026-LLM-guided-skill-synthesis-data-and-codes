## Search State

- **Seed**: 3
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.3095 | 1.00 | ❌ rejected |
| 12 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 10 | 0.0522 | 0.48 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 10 | -0.2603 | 0.18 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.1952 | 0.76 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.3928 | 1.00 | ❌ rejected |

**Proposal policy**: task_score is near-perfect (1.00). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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

## Current Skill (Q=0.309) — your mutation base

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

- **Composite score**: 0.309
- **task_score** (E): 1.000
- **fitness_score**: 0.879  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.570

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1088 |
| descend_1 | 1.00 | 1.00 | 0.1446 |
| grasp_1 | 1.00 | 1.00 | 0.0128 |
| lift_1 | 1.00 | 1.00 | 0.1271 |
| transport_to_goal | 1.00 | 1.00 | 0.2373 |
| place_object | 1.00 | 1.00 | 0.0969 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.504, -0.001, 0.200) | (0.511, 0.002, 0.030)→(0.511, 0.002, 0.026) | 0.244→0.246 | 1.00 / 4.000 | 0.122 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.504, -0.001, 0.200)→(0.506, 0.002, 0.055) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 4.000 | 10.029 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.506, 0.002, 0.055)→(0.498, 0.001, 0.046) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 43.667 | 0.148 | 0.199 |
| lift_1 | lift | 1.00 / step_budget | (0.498, 0.001, 0.046)→(0.494, 0.001, 0.173) | (0.511, 0.002, 0.026)→(0.503, 0.002, 0.149) | 0.246→0.236 | 1.00 / 37.667 | 0.080 | 0.413 |
| transport_to_goal | approach | 1.00 / step_budget | (0.494, 0.001, 0.173)→(0.614, 0.168, 0.270) | (0.503, 0.002, 0.149)→(0.618, 0.167, 0.241) | 0.236→0.105 | 1.00 / 33.000 | 0.085 | 0.125 |
| place_object | descend | 1.00 / step_budget | (0.614, 0.168, 0.270)→(0.621, 0.177, 0.174) | (0.618, 0.167, 0.241)→(0.615, 0.176, 0.144) | 0.105→0.015 | 1.00 / 25.667 | 0.118 | 0.237 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.255
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.269
- phase_breakdown.approach_1_score: 0.007
- phase_breakdown.release_1_score: 0.000
- phase_breakdown.descend_1_score: 0.861
- phase_breakdown.transport_arc_score: 0.059
- phase_breakdown.grasp_1_score: 1.000
- grasp_place_fitness: 0.963

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.963
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.392
- **K-run variance**: 0.0139
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.316


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.11919,"average_solve_count":344.0,"average_success_count":344.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.11528,"approach_1.approach_speed":0.04949,"descend_1.descend_speed":0.02996,"descend_1.grasp_z_offset":0.01001,"lift_1.lift_height":0.11801,"lift_1.lift_speed":0.0366,"place_object.place_speed":0.1683,"place_object.place_z_offset":0.02265,"transport_to_goal.transport_speed":0.06273},"optimized_scores":{"best_composite_score":0.39245,"best_fitness_score":0.96245,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":86.0,"contact_point_centroid":[0.45469,-0.02504,-0.00155],"force_p95":0.35249,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.37348,"mean_force":0.15199,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44673,-0.02509,0.0485]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2543.0,"contact_point_centroid":[0.62014,0.18131,0.2056],"force_p95":0.12428,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2622,"mean_force":0.07397,"phase_index":5.0,"phase_name":"place_object","phase_type":"descend","tcp_position_centroid":[0.62116,0.20016,0.20683]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2180.0,"contact_point_centroid":[0.62024,0.21864,0.20831],"force_p95":0.12464,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2595,"mean_force":0.07801,"phase_index":5.0,"phase_name":"place_object","phase_type":"descend","tcp_position_centroid":[0.62101,0.19994,0.21]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6540.0,"contact_point_centroid":[0.44463,-0.04398,0.09658],"force_p95":0.08268,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25717,"mean_force":0.05473,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44448,-0.02499,0.09537]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5559.0,"contact_point_centroid":[0.44545,-0.00582,0.09647],"force_p95":0.08561,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25111,"mean_force":0.06238,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44448,-0.02499,0.09537]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45859,-0.02623,-0.0021],"force_p95":0.15145,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20774,"mean_force":0.13017,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44878,-0.02516,0.04856]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4097.0,"contact_point_centroid":[0.4487,-0.00592,0.04862],"force_p95":0.07986,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14753,"mean_force":0.05215,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44774,-0.02513,0.04756]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20600.0,"contact_point_centroid":[0.53268,0.07064,0.19875],"force_p95":0.07376,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14484,"mean_force":0.04829,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53313,0.08969,0.19825]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18877.0,"contact_point_centroid":[0.53364,0.11023,0.19911],"force_p95":0.07772,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13856,"mean_force":0.05225,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53424,0.09109,0.19891]},{"body_a":"world","body_b":"grasp_target","contact_count":1120.0,"contact_point_centroid":[0.45856,-0.02632,-0.00188],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12306,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48128,-0.01055,0.23391]},{"body_a":"world","body_b":"grasp_target","contact_count":920.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45794,-0.02367,0.1114]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4958.0,"contact_point_centroid":[0.44788,-0.04422,0.04879],"force_p95":0.07095,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07373,"mean_force":0.04417,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44775,-0.02513,0.04756]}],"total_contact_groups":12},"final_pose_error":0.01978,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.61924,0.20339,0.12471],"final_tcp_position":[0.62438,0.2043,0.15528],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":0.37348,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":281.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1120.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.46203,-0.02217,0.16415],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13823,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":230.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":920.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.4555,-0.02538,0.05537],"tcp_start":[0.46203,-0.02217,0.16415],"tcp_to_object_dist_end":0.02952,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45851,-0.02546,0.02563],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30313,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.14847,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10855.0,"raw_peak_contact_force":0.20774,"subtask_id":"grasp_1","tcp_end":[0.44771,-0.02512,0.04753],"tcp_start":[0.4555,-0.02538,0.05537],"tcp_to_object_dist_end":0.02442,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":327.0,"n_steps_budget":1000.0,"object_pos_end":[0.4518,-0.02518,0.12289],"object_pos_start":[0.45851,-0.02546,0.02563],"object_to_goal_dist_end":0.29385,"object_to_goal_dist_start":0.30313,"object_z_max":0.1226,"peak_contact_force":0.08195,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":12185.0,"raw_peak_contact_force":0.37348,"tcp_end":[0.44428,-0.02497,0.14613],"tcp_start":[0.44771,-0.02512,0.04753],"tcp_to_object_dist_end":0.02442,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":35.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.62211,0.19658,0.22103],"object_pos_start":[0.4518,-0.02518,0.12289],"object_to_goal_dist_end":0.10784,"object_to_goal_dist_start":0.29385,"object_z_max":0.22093,"peak_contact_force":0.08278,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":39477.0,"raw_peak_contact_force":0.14484,"subtask_id":"transport_arc","tcp_end":[0.61919,0.19686,0.25001],"tcp_start":[0.44428,-0.02497,0.14613],"tcp_to_object_dist_end":0.02913,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":21.0,"n_steps":163.0,"n_steps_budget":1000.0,"object_pos_end":[0.61924,0.20339,0.12471],"object_pos_start":[0.62211,0.19658,0.22103],"object_to_goal_dist_end":0.01593,"object_to_goal_dist_start":0.10784,"object_z_max":0.22103,"peak_contact_force":0.11822,"phase_name":"place_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4723.0,"raw_peak_contact_force":0.2622,"tcp_end":[0.62438,0.2043,0.15528],"tcp_start":[0.61919,0.19686,0.25001],"tcp_to_object_dist_end":0.03102,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.89676,"average_solve_count":339.0,"average_success_count":339.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.10682,"approach_1.approach_speed":0.04442,"descend_1.descend_speed":0.02708,"descend_1.grasp_z_offset":0.01095,"lift_1.lift_height":0.10246,"lift_1.lift_speed":0.05281,"place_object.place_speed":0.13841,"place_object.place_z_offset":0.01346,"transport_to_goal.transport_speed":0.02621},"optimized_scores":{"best_composite_score":0.1427,"best_fitness_score":0.7127,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":88.0,"contact_point_centroid":[0.54038,0.00056,-0.0014],"force_p95":0.40808,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.41977,"mean_force":0.13897,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52809,0.00083,0.04601]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6443.0,"contact_point_centroid":[0.52632,0.01992,0.08689],"force_p95":0.07839,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27866,"mean_force":0.05321,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52548,0.00079,0.08468]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5866.0,"contact_point_centroid":[0.52637,-0.01841,0.0866],"force_p95":0.08151,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27622,"mean_force":0.05715,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52548,0.00079,0.08418]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2464.0,"contact_point_centroid":[0.63715,0.16554,0.2648],"force_p95":0.11194,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22487,"mean_force":0.0657,"phase_index":5.0,"phase_name":"place_object","phase_type":"descend","tcp_position_centroid":[0.63718,0.14702,0.26582]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2373.0,"contact_point_centroid":[0.6363,0.12764,0.26771],"force_p95":0.12436,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21119,"mean_force":0.07827,"phase_index":5.0,"phase_name":"place_object","phase_type":"descend","tcp_position_centroid":[0.63692,0.14666,0.26841]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54431,0.0011,-0.00203],"force_p95":0.13312,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16053,"mean_force":0.12566,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53042,0.00087,0.0463]},{"body_a":"world","body_b":"grasp_target","contact_count":1244.0,"contact_point_centroid":[0.54431,0.00113,-0.00189],"force_p95":0.13606,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12302,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51581,0.00044,0.22863]},{"body_a":"world","body_b":"grasp_target","contact_count":816.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53504,0.00095,0.10648]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17415.0,"contact_point_centroid":[0.57759,0.05089,0.21537],"force_p95":0.08399,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11789,"mean_force":0.05658,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.57633,0.06987,0.21501]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17329.0,"contact_point_centroid":[0.57825,0.08873,0.21564],"force_p95":0.08272,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10984,"mean_force":0.05664,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.57623,0.06974,0.21485]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4922.0,"contact_point_centroid":[0.53044,-0.01839,0.04766],"force_p95":0.06731,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09934,"mean_force":0.0444,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52922,0.00085,0.0449]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5366.0,"contact_point_centroid":[0.52998,0.02007,0.04751],"force_p95":0.06408,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08154,"mean_force":0.04101,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52922,0.00085,0.0449]}],"total_contact_groups":12},"final_pose_error":0.01978,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.63602,0.15219,0.19289],"final_tcp_position":[0.64162,0.15303,0.22271],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":29.84288,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":312.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1244.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.53451,0.00092,0.15424],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1286,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":204.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":29.84288,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":816.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53798,0.00101,0.05559],"tcp_start":[0.53451,0.00092,0.15424],"tcp_to_object_dist_end":0.03024,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54422,0.00093,0.02585],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.2504,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.13221,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12088.0,"raw_peak_contact_force":0.16053,"subtask_id":"grasp_1","tcp_end":[0.52919,0.00085,0.04486],"tcp_start":[0.53798,0.00101,0.05559],"tcp_to_object_dist_end":0.02424,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":304.0,"n_steps_budget":1000.0,"object_pos_end":[0.53663,0.00081,0.10624],"object_pos_start":[0.54422,0.00093,0.02585],"object_to_goal_dist_end":0.21037,"object_to_goal_dist_start":0.2504,"object_z_max":0.10598,"peak_contact_force":0.0797,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":12397.0,"raw_peak_contact_force":0.41977,"tcp_end":[0.52515,0.00079,0.12775],"tcp_start":[0.52919,0.00085,0.04486],"tcp_to_object_dist_end":0.02438,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.63725,0.14133,0.28148],"object_pos_start":[0.53663,0.00081,0.10624],"object_to_goal_dist_end":0.0925,"object_to_goal_dist_start":0.21037,"object_z_max":0.2813,"peak_contact_force":0.08547,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":34744.0,"raw_peak_contact_force":0.11789,"subtask_id":"transport_arc","tcp_end":[0.6331,0.14122,0.31005],"tcp_start":[0.52515,0.00079,0.12775],"tcp_to_object_dist_end":0.02887,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":153.0,"n_steps_budget":1000.0,"object_pos_end":[0.63602,0.15219,0.19289],"object_pos_start":[0.63725,0.14133,0.28148],"object_to_goal_dist_end":0.01314,"object_to_goal_dist_start":0.0925,"object_z_max":0.28154,"peak_contact_force":0.11326,"phase_name":"place_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4837.0,"raw_peak_contact_force":0.22487,"tcp_end":[0.64162,0.15303,0.22271],"tcp_start":[0.6331,0.14122,0.31005],"tcp_to_object_dist_end":0.03036,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.04559,"average_solve_count":329.0,"average_success_count":329.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.24429,"approach_1.approach_speed":0.04619,"descend_1.descend_speed":0.02288,"descend_1.grasp_z_offset":0.01003,"lift_1.lift_height":0.21908,"lift_1.lift_speed":0.05093,"place_object.place_speed":0.10455,"place_object.place_z_offset":0.01602,"transport_to_goal.transport_speed":0.04998},"optimized_scores":{"best_composite_score":0.39331,"best_fitness_score":0.96331,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":91.0,"contact_point_centroid":[0.52666,0.02854,-0.00155],"force_p95":0.41997,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.44476,"mean_force":0.14213,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51509,0.02863,0.04577]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14778.0,"contact_point_centroid":[0.51318,0.04758,0.1413],"force_p95":0.07972,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29672,"mean_force":0.05254,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51267,0.02848,0.13927]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13326.0,"contact_point_centroid":[0.51298,0.00931,0.14467],"force_p95":0.08141,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2683,"mean_force":0.05651,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51269,0.02848,0.14279]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53057,0.03062,-0.00217],"force_p95":0.1683,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23003,"mean_force":0.13495,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51741,0.02879,0.04582]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3277.0,"contact_point_centroid":[0.59255,0.18775,0.19764],"force_p95":0.10973,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22274,"mean_force":0.06348,"phase_index":5.0,"phase_name":"place_object","phase_type":"descend","tcp_position_centroid":[0.59294,0.16912,0.19825]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3021.0,"contact_point_centroid":[0.59159,0.14971,0.20111],"force_p95":0.12599,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21084,"mean_force":0.07228,"phase_index":5.0,"phase_name":"place_object","phase_type":"descend","tcp_position_centroid":[0.5928,0.16886,0.20112]},{"body_a":"world","body_b":"grasp_target","contact_count":324.0,"contact_point_centroid":[0.5305,0.03079,-0.00161],"force_p95":0.13823,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1243,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50728,0.00817,0.29098]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4557.0,"contact_point_centroid":[0.51699,0.00955,0.04702],"force_p95":0.07451,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12725,"mean_force":0.04707,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51624,0.02872,0.04449]},{"body_a":"world","body_b":"grasp_target","contact_count":1788.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.1226,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51964,0.02361,0.16839]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8801.0,"contact_point_centroid":[0.55157,0.07658,0.24481],"force_p95":0.08264,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11189,"mean_force":0.05383,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55068,0.09558,0.24431]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8641.0,"contact_point_centroid":[0.55224,0.1143,0.24506],"force_p95":0.08194,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11133,"mean_force":0.05465,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55051,0.09528,0.24429]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5059.0,"contact_point_centroid":[0.51712,0.04802,0.04628],"force_p95":0.07516,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07784,"mean_force":0.04435,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51625,0.02872,0.0445]}],"total_contact_groups":12},"final_pose_error":0.01969,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.58865,0.17345,0.11355],"final_tcp_position":[0.59595,0.17447,0.14253],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":0.44476,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":82.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02597],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18339,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12213,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":324.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.51643,0.01823,0.28027],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.255,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":447.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02597],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18339,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1788.0,"raw_peak_contact_force":0.12264,"subtask_id":"descend_1","tcp_end":[0.52486,0.02924,0.05471],"tcp_start":[0.51643,0.01823,0.28027],"tcp_to_object_dist_end":0.02928,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53048,0.02937,0.0254],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18479,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.16276,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11416.0,"raw_peak_contact_force":0.23003,"subtask_id":"grasp_1","tcp_end":[0.51621,0.02872,0.04445],"tcp_start":[0.52486,0.02924,0.05471],"tcp_to_object_dist_end":0.02381,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":714.0,"n_steps_budget":1000.0,"object_pos_end":[0.52044,0.02888,0.21933],"object_pos_start":[0.53048,0.02937,0.0254],"object_to_goal_dist_end":0.20337,"object_to_goal_dist_start":0.18479,"object_z_max":0.21907,"peak_contact_force":0.07769,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":28195.0,"raw_peak_contact_force":0.44476,"tcp_end":[0.51329,0.02852,0.24397],"tcp_start":[0.51621,0.02872,0.04445],"tcp_to_object_dist_end":0.02566,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":34.0,"n_steps":479.0,"n_steps_budget":1000.0,"object_pos_end":[0.59542,0.1645,0.22142],"object_pos_start":[0.52044,0.02888,0.21933],"object_to_goal_dist_end":0.11436,"object_to_goal_dist_start":0.20337,"object_z_max":0.22141,"peak_contact_force":0.08637,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":17442.0,"raw_peak_contact_force":0.11189,"subtask_id":"transport_arc","tcp_end":[0.59111,0.16448,0.24892],"tcp_start":[0.51329,0.02852,0.24397],"tcp_to_object_dist_end":0.02784,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":189.0,"n_steps_budget":1000.0,"object_pos_end":[0.58865,0.17345,0.11355],"object_pos_start":[0.59542,0.1645,0.22142],"object_to_goal_dist_end":0.0149,"object_to_goal_dist_start":0.11436,"object_z_max":0.22142,"peak_contact_force":0.12344,"phase_name":"place_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":6298.0,"raw_peak_contact_force":0.22274,"tcp_end":[0.59595,0.17447,0.14253],"tcp_start":[0.59111,0.16448,0.24892],"tcp_to_object_dist_end":0.02991,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```