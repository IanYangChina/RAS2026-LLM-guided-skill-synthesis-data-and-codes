## Search State

- **Seed**: 3
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.3928 | 1.00 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 10 | 0.3147 | 0.94 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.3802 | 0.95 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.4008 | 1.00 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 12 | -0.0777 | 0.48 | ❌ rejected |

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

## Current Skill (Q=0.393) — your mutation base

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

- **Composite score**: 0.393
- **task_score** (E): 1.000
- **fitness_score**: 0.963  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.570

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0793 |
| descend_1 | 1.00 | 1.00 | 0.1745 |
| grasp_1 | 1.00 | 1.00 | 0.0128 |
| lift_1 | 1.00 | 1.00 | 0.1364 |
| transport_to_goal | 1.00 | 1.00 | 0.2345 |
| place_object | 1.00 | 1.00 | 0.1019 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.504, 0.001, 0.230) | (0.511, 0.002, 0.030)→(0.511, 0.002, 0.026) | 0.244→0.246 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.504, 0.001, 0.230)→(0.506, 0.002, 0.055) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 4.000 | 12.477 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.506, 0.002, 0.055)→(0.498, 0.002, 0.046) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 41.667 | 0.147 | 0.195 |
| lift_1 | lift | 1.00 / step_budget | (0.498, 0.002, 0.046)→(0.494, 0.002, 0.182) | (0.511, 0.002, 0.026)→(0.503, 0.002, 0.158) | 0.246→0.222 | 1.00 / 37.667 | 0.080 | 0.390 |
| transport_to_goal | approach | 1.00 / step_budget | (0.494, 0.002, 0.182)→(0.617, 0.171, 0.273) | (0.503, 0.002, 0.158)→(0.621, 0.171, 0.245) | 0.222→0.108 | 1.00 / 32.000 | 0.091 | 0.113 |
| place_object | descend | 1.00 / step_budget | (0.617, 0.171, 0.273)→(0.621, 0.178, 0.172) | (0.621, 0.171, 0.245)→(0.624, 0.178, 0.141) | 0.108→0.008 | 1.00 / 25.333 | 0.132 | 0.232 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.589
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.344
- phase_breakdown.approach_1_score: 0.008
- phase_breakdown.release_1_score: 0.470
- phase_breakdown.descend_1_score: 0.852
- phase_breakdown.transport_arc_score: 0.068
- phase_breakdown.grasp_1_score: 1.000
- grasp_place_fitness: 0.963

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.963
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.393
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.380


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.04878,"average_solve_count":369.0,"average_success_count":369.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.14829,"approach_1.approach_speed":0.09257,"descend_1.descend_speed":0.0381,"descend_1.grasp_z_offset":0.01006,"lift_1.lift_height":0.18169,"lift_1.lift_speed":0.0462,"place_object.place_speed":0.04815,"place_object.place_z_offset":0.01464,"transport_to_goal.transport_speed":0.03472},"optimized_scores":{"best_composite_score":0.39251,"best_fitness_score":0.96251,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":84.0,"contact_point_centroid":[0.45569,-0.02456,-0.00148],"force_p95":0.35689,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.3905,"mean_force":0.11694,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44684,-0.0251,0.04877]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10600.0,"contact_point_centroid":[0.44475,-0.04398,0.12874],"force_p95":0.08213,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27439,"mean_force":0.05404,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44464,-0.02499,0.12778]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9010.0,"contact_point_centroid":[0.44558,-0.00583,0.1286],"force_p95":0.08468,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27134,"mean_force":0.0616,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44464,-0.02499,0.12778]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2708.0,"contact_point_centroid":[0.62098,0.18144,0.20426],"force_p95":0.11407,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2673,"mean_force":0.0706,"phase_index":5.0,"phase_name":"place_object","phase_type":"descend","tcp_position_centroid":[0.62056,0.19957,0.20597]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2024.0,"contact_point_centroid":[0.62251,0.2185,0.19931],"force_p95":0.13738,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24931,"mean_force":0.09802,"phase_index":5.0,"phase_name":"place_object","phase_type":"descend","tcp_position_centroid":[0.6207,0.19977,0.20323]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45859,-0.02623,-0.0021],"force_p95":0.15127,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20745,"mean_force":0.13013,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44893,-0.02518,0.04858]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4098.0,"contact_point_centroid":[0.44885,-0.00593,0.04864],"force_p95":0.0798,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14721,"mean_force":0.05214,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44789,-0.02514,0.04758]},{"body_a":"world","body_b":"grasp_target","contact_count":836.0,"contact_point_centroid":[0.45856,-0.02632,-0.00185],"force_p95":0.13728,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12321,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48248,-0.01005,0.24994]},{"body_a":"world","body_b":"grasp_target","contact_count":1168.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45902,-0.02321,0.12729]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13999.0,"contact_point_centroid":[0.5225,0.09534,0.22695],"force_p95":0.10091,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11815,"mean_force":0.0646,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52304,0.07625,0.22764]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17678.0,"contact_point_centroid":[0.5274,0.06402,0.22886],"force_p95":0.07859,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11288,"mean_force":0.04981,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52825,0.0828,0.229]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4957.0,"contact_point_centroid":[0.44803,-0.04423,0.04881],"force_p95":0.0709,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07364,"mean_force":0.04417,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4479,-0.02514,0.04759]}],"total_contact_groups":12},"final_pose_error":0.01972,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.62791,0.20305,0.11427],"final_tcp_position":[0.62415,0.20426,0.14713],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":0.3905,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":210.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":836.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.46407,-0.02121,0.19678],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17093,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":292.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1168.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.45565,-0.0254,0.0554],"tcp_start":[0.46407,-0.02121,0.19678],"tcp_to_object_dist_end":0.02953,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45851,-0.02547,0.02563],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30313,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.14832,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10855.0,"raw_peak_contact_force":0.20745,"subtask_id":"grasp_1","tcp_end":[0.44787,-0.02514,0.04756],"tcp_start":[0.45565,-0.0254,0.0554],"tcp_to_object_dist_end":0.02437,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":530.0,"n_steps_budget":1000.0,"object_pos_end":[0.45127,-0.02518,0.18445],"object_pos_start":[0.45851,-0.02547,0.02563],"object_to_goal_dist_end":0.30234,"object_to_goal_dist_start":0.30313,"object_z_max":0.18416,"peak_contact_force":0.08101,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":19694.0,"raw_peak_contact_force":0.3905,"tcp_end":[0.44485,-0.02499,0.20972],"tcp_start":[0.44787,-0.02514,0.04756],"tcp_to_object_dist_end":0.02607,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":906.0,"n_steps_budget":1000.0,"object_pos_end":[0.62003,0.1951,0.22175],"object_pos_start":[0.45127,-0.02518,0.18445],"object_to_goal_dist_end":0.10889,"object_to_goal_dist_start":0.30234,"object_z_max":0.22172,"peak_contact_force":0.11278,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":31677.0,"raw_peak_contact_force":0.11815,"subtask_id":"transport_arc","tcp_end":[0.61888,0.19623,0.2528],"tcp_start":[0.44485,-0.02499,0.20972],"tcp_to_object_dist_end":0.03109,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":21.0,"n_steps":193.0,"n_steps_budget":1000.0,"object_pos_end":[0.62791,0.20305,0.11427],"object_pos_start":[0.62003,0.1951,0.22175],"object_to_goal_dist_end":0.00562,"object_to_goal_dist_start":0.10889,"object_z_max":0.22175,"peak_contact_force":0.1367,"phase_name":"place_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4732.0,"raw_peak_contact_force":0.2673,"subtask_id":"release_1","tcp_end":[0.62415,0.20426,0.14713],"tcp_start":[0.61888,0.19623,0.2528],"tcp_to_object_dist_end":0.0331,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.75459,"average_solve_count":436.0,"average_success_count":436.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.23296,"approach_1.approach_speed":0.02213,"descend_1.descend_speed":0.04802,"descend_1.grasp_z_offset":0.01003,"lift_1.lift_height":0.17077,"lift_1.lift_speed":0.05711,"place_object.place_speed":0.02328,"place_object.place_z_offset":0.01839,"transport_to_goal.transport_speed":0.04178},"optimized_scores":{"best_composite_score":0.39343,"best_fitness_score":0.96343,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":86.0,"contact_point_centroid":[0.54138,0.00082,-0.00139],"force_p95":0.38397,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.43539,"mean_force":0.11495,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52811,0.00083,0.04545]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10771.0,"contact_point_centroid":[0.52638,-0.01838,0.11929],"force_p95":0.07929,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3025,"mean_force":0.05472,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5255,0.00079,0.1168]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11396.0,"contact_point_centroid":[0.52637,0.01992,0.11888],"force_p95":0.0772,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28459,"mean_force":0.05245,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5255,0.00079,0.11664]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2440.0,"contact_point_centroid":[0.64557,0.1708,0.28081],"force_p95":0.09727,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22527,"mean_force":0.07129,"phase_index":5.0,"phase_name":"place_object","phase_type":"descend","tcp_position_centroid":[0.6411,0.15205,0.28126]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2275.0,"contact_point_centroid":[0.64508,0.13336,0.28093],"force_p95":0.09928,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21797,"mean_force":0.07473,"phase_index":5.0,"phase_name":"place_object","phase_type":"descend","tcp_position_centroid":[0.64108,0.15203,0.28164]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54431,0.00103,-0.00203],"force_p95":0.13242,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1543,"mean_force":0.12546,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53049,0.00087,0.04572]},{"body_a":"world","body_b":"grasp_target","contact_count":420.0,"contact_point_centroid":[0.54431,0.00113,-0.0017],"force_p95":0.13814,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12382,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51125,0.00031,0.28707]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4116.0,"contact_point_centroid":[0.5305,-0.01835,0.04699],"force_p95":0.07633,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12419,"mean_force":0.05182,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52929,0.00085,0.04432]},{"body_a":"world","body_b":"grasp_target","contact_count":1700.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53122,0.00084,0.1638]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14587.0,"contact_point_centroid":[0.58149,0.05468,0.25637],"force_p95":0.08368,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10706,"mean_force":0.057,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.58012,0.07363,0.25621]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14374.0,"contact_point_centroid":[0.58231,0.09257,0.2567],"force_p95":0.08262,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10005,"mean_force":0.05754,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5801,0.0736,0.25619]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4875.0,"contact_point_centroid":[0.53041,0.01992,0.04612],"force_p95":0.0684,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09399,"mean_force":0.0447,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52929,0.00085,0.04432]}],"total_contact_groups":12},"final_pose_error":0.01972,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.64953,0.15526,0.19859],"final_tcp_position":[0.64327,0.15523,0.2285],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":0.43539,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":106.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12234,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":420.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52647,0.0007,0.2713],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.24592,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":425.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1700.0,"raw_peak_contact_force":0.12264,"subtask_id":"descend_1","tcp_end":[0.5381,0.00101,0.05506],"tcp_start":[0.52647,0.0007,0.2713],"tcp_to_object_dist_end":0.02969,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54422,0.00076,0.02587],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25049,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.13077,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10791.0,"raw_peak_contact_force":0.1543,"subtask_id":"grasp_1","tcp_end":[0.52926,0.00085,0.04428],"tcp_start":[0.5381,0.00101,0.05506],"tcp_to_object_dist_end":0.02373,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":547.0,"n_steps_budget":1000.0,"object_pos_end":[0.53526,0.00085,0.17208],"object_pos_start":[0.54422,0.00076,0.02587],"object_to_goal_dist_end":0.19419,"object_to_goal_dist_start":0.25049,"object_z_max":0.17182,"peak_contact_force":0.07578,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":22253.0,"raw_peak_contact_force":0.43539,"tcp_end":[0.52583,0.00079,0.19539],"tcp_start":[0.52926,0.00085,0.04428],"tcp_to_object_dist_end":0.02514,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":856.0,"n_steps_budget":1000.0,"object_pos_end":[0.64396,0.14966,0.29638],"object_pos_start":[0.53526,0.00085,0.17208],"object_to_goal_dist_end":0.10567,"object_to_goal_dist_start":0.19419,"object_z_max":0.29625,"peak_contact_force":0.08464,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":28961.0,"raw_peak_contact_force":0.10706,"subtask_id":"transport_arc","tcp_end":[0.63998,0.14963,0.32468],"tcp_start":[0.52583,0.00079,0.19539],"tcp_to_object_dist_end":0.02859,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":180.0,"n_steps_budget":1000.0,"object_pos_end":[0.64953,0.15526,0.19859],"object_pos_start":[0.64396,0.14966,0.29638],"object_to_goal_dist_end":0.00822,"object_to_goal_dist_start":0.10567,"object_z_max":0.29638,"peak_contact_force":0.09713,"phase_name":"place_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4715.0,"raw_peak_contact_force":0.22527,"subtask_id":"release_1","tcp_end":[0.64327,0.15523,0.2285],"tcp_start":[0.63998,0.14963,0.32468],"tcp_to_object_dist_end":0.03056,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.86592,"average_solve_count":358.0,"average_success_count":358.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.17522,"approach_1.approach_speed":0.04833,"descend_1.descend_speed":0.04999,"descend_1.grasp_z_offset":0.01084,"lift_1.lift_height":0.11521,"lift_1.lift_speed":0.02168,"place_object.place_speed":0.07085,"place_object.place_z_offset":0.01276,"transport_to_goal.transport_speed":0.04549},"optimized_scores":{"best_composite_score":0.39248,"best_fitness_score":0.96248,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":120.0,"contact_point_centroid":[0.52726,0.02892,-0.00169],"force_p95":0.30373,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.34342,"mean_force":0.15222,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51501,0.02892,0.04612]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8021.0,"contact_point_centroid":[0.51286,0.04786,0.09178],"force_p95":0.07974,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23436,"mean_force":0.05092,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5126,0.02876,0.08952]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53056,0.03066,-0.00215],"force_p95":0.16419,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22396,"mean_force":0.13358,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51755,0.02909,0.04672]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6949.0,"contact_point_centroid":[0.51245,0.00955,0.09269],"force_p95":0.08379,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21239,"mean_force":0.0562,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5126,0.02876,0.09037]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3458.0,"contact_point_centroid":[0.59341,0.19043,0.19513],"force_p95":0.1068,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20264,"mean_force":0.06395,"phase_index":5.0,"phase_name":"place_object","phase_type":"descend","tcp_position_centroid":[0.59421,0.17156,0.19518]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3163.0,"contact_point_centroid":[0.59278,0.15228,0.19695],"force_p95":0.11242,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17472,"mean_force":0.06925,"phase_index":5.0,"phase_name":"place_object","phase_type":"descend","tcp_position_centroid":[0.59417,0.17147,0.19676]},{"body_a":"world","body_b":"grasp_target","contact_count":732.0,"contact_point_centroid":[0.5305,0.03079,-0.00182],"force_p95":0.13759,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1233,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50936,0.01112,0.26172]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4329.0,"contact_point_centroid":[0.51704,0.00978,0.04726],"force_p95":0.07798,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13754,"mean_force":0.0496,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51638,0.02902,0.04538]},{"body_a":"world","body_b":"grasp_target","contact_count":1308.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52187,0.02653,0.13887]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13319.0,"contact_point_centroid":[0.55342,0.11975,0.19269],"force_p95":0.0757,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11481,"mean_force":0.0516,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55249,0.10065,0.19135]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13319.0,"contact_point_centroid":[0.5527,0.08156,0.19223],"force_p95":0.07538,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10562,"mean_force":0.05144,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55249,0.10065,0.19135]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5270.0,"contact_point_centroid":[0.51723,0.0482,0.04751],"force_p95":0.07174,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07394,"mean_force":0.04223,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51639,0.02902,0.04539]}],"total_contact_groups":12},"final_pose_error":0.01996,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.59366,0.17492,0.11154],"final_tcp_position":[0.59623,0.17522,0.1398],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":37.18503,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":184.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":732.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.5209,0.0237,0.22075],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1951,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":327.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":37.18503,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1308.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.525,0.02956,0.05561],"tcp_start":[0.5209,0.0237,0.22075],"tcp_to_object_dist_end":0.03013,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53048,0.02953,0.02547],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18464,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.16049,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11399.0,"raw_peak_contact_force":0.22396,"subtask_id":"grasp_1","tcp_end":[0.51635,0.02901,0.04535],"tcp_start":[0.525,0.02956,0.05561],"tcp_to_object_dist_end":0.02439,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":370.0,"n_steps_budget":1000.0,"object_pos_end":[0.52242,0.02919,0.11889],"object_pos_start":[0.53048,0.02953,0.02547],"object_to_goal_dist_end":0.16939,"object_to_goal_dist_start":0.18464,"object_z_max":0.11864,"peak_contact_force":0.08299,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":15090.0,"raw_peak_contact_force":0.34342,"tcp_end":[0.51246,0.02876,0.14118],"tcp_start":[0.51635,0.02901,0.04535],"tcp_to_object_dist_end":0.02441,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":701.0,"n_steps_budget":1000.0,"object_pos_end":[0.59773,0.16881,0.21597],"object_pos_start":[0.52242,0.02919,0.11889],"object_to_goal_dist_end":0.10839,"object_to_goal_dist_start":0.16939,"object_z_max":0.21584,"peak_contact_force":0.07545,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":26638.0,"raw_peak_contact_force":0.11481,"subtask_id":"transport_arc","tcp_end":[0.59337,0.16863,0.24289],"tcp_start":[0.51246,0.02876,0.14118],"tcp_to_object_dist_end":0.02727,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":186.0,"n_steps_budget":1000.0,"object_pos_end":[0.59366,0.17492,0.11154],"object_pos_start":[0.59773,0.16881,0.21597],"object_to_goal_dist_end":0.00934,"object_to_goal_dist_start":0.10839,"object_z_max":0.216,"peak_contact_force":0.16314,"phase_name":"place_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":6621.0,"raw_peak_contact_force":0.20264,"subtask_id":"release_1","tcp_end":[0.59623,0.17522,0.1398],"tcp_start":[0.59337,0.16863,0.24289],"tcp_to_object_dist_end":0.02838,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```