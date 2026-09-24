## Search State

- **Seed**: 3
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.4008 | 1.00 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 12 | -0.0777 | 0.48 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.3766 | 0.95 | ❌ rejected |
| 3 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.4037 | 1.00 | ✅ accepted |
| 2 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.1237 | 0.43 | ✅ accepted |

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

## Current Skill (Q=0.401) — your mutation base

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

- **Composite score**: 0.401
- **task_score** (E): 1.000
- **fitness_score**: 0.971  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.570

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1992 |
| descend_1 | 1.00 | 1.00 | 0.0592 |
| grasp_1 | 1.00 | 1.00 | 0.0118 |
| lift_1 | 1.00 | 1.00 | 0.1153 |
| transport_to_goal | 1.00 | 1.00 | 0.2459 |
| place_object_1 | 1.00 | 1.00 | 0.0365 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.002, 0.106) | (0.511, 0.002, 0.030)→(0.511, 0.002, 0.026) | 0.244→0.246 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.506, 0.002, 0.106)→(0.505, 0.002, 0.047) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.505, 0.002, 0.047)→(0.497, 0.001, 0.038) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 42.667 | 0.143 | 0.190 |
| lift_1 | lift | 1.00 / step_budget | (0.497, 0.001, 0.038)→(0.494, 0.001, 0.153) | (0.511, 0.002, 0.026)→(0.504, 0.001, 0.138) | 0.246→0.222 | 1.00 / 36.667 | 0.086 | 0.480 |
| transport_to_goal | approach | 1.00 / step_budget | (0.494, 0.001, 0.153)→(0.617, 0.171, 0.271) | (0.504, 0.001, 0.138)→(0.626, 0.172, 0.249) | 0.222→0.111 | 1.00 / 23.333 | 0.109 | 0.153 |
| place_object_1 | descend | 1.00 / step_budget | (0.620, 0.176, 0.203)→(0.620, 0.178, 0.167) | (0.626, 0.172, 0.249)→(0.628, 0.178, 0.145) | 0.111→0.010 | 1.00 / 20.667 | 30.644 | 0.305 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.700
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.272
- phase_breakdown.approach_1_score: 0.175
- phase_breakdown.release_1_score: 0.000
- phase_breakdown.descend_1_score: 0.781
- phase_breakdown.transport_arc_score: 0.064
- phase_breakdown.grasp_1_score: 1.000
- grasp_place_fitness: 0.979

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.979
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.403
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Parameters at lower bound**: descend_1.grasp_z_offset
- **Final σ (mean)**: 0.366


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.83405,"average_solve_count":464.0,"average_success_count":464.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.06779,"approach_1.approach_speed":0.07837,"descend_1.descend_speed":0.01778,"descend_1.grasp_z_offset":0.01,"lift_1.lift_height":0.15042,"lift_1.lift_speed":0.03071,"place_object_1.place_speed":0.01018,"place_object_1.place_z_offset":0.00581,"transport_to_goal.transport_speed":0.08412},"optimized_scores":{"best_composite_score":0.40943,"best_fitness_score":0.97943,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":90.0,"contact_point_centroid":[0.45474,-0.02546,-0.00148],"force_p95":0.49084,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.50861,"mean_force":0.23649,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44585,-0.02557,0.03225]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2453.0,"contact_point_centroid":[0.62674,0.21893,0.19806],"force_p95":0.16766,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35752,"mean_force":0.09581,"phase_index":5.0,"phase_name":"place_object_1","phase_type":"descend","tcp_position_centroid":[0.62098,0.20055,0.19847]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2090.0,"contact_point_centroid":[0.62629,0.18211,0.19831],"force_p95":0.18582,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33872,"mean_force":0.10573,"phase_index":5.0,"phase_name":"place_object_1","phase_type":"descend","tcp_position_centroid":[0.62098,0.20055,0.19838]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8697.0,"contact_point_centroid":[0.44371,-0.04461,0.09704],"force_p95":0.07548,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24591,"mean_force":0.05226,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44351,-0.02546,0.0952]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8690.0,"contact_point_centroid":[0.4437,-0.00631,0.09717],"force_p95":0.07374,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24003,"mean_force":0.05199,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44351,-0.02546,0.09525]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45857,-0.02618,-0.00206],"force_p95":0.14049,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19262,"mean_force":0.12744,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44796,-0.02565,0.03242]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18294.0,"contact_point_centroid":[0.52839,0.06448,0.2056],"force_p95":0.07776,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15828,"mean_force":0.05128,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52811,0.08359,0.20401]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18637.0,"contact_point_centroid":[0.53146,0.10657,0.2073],"force_p95":0.07728,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15517,"mean_force":0.05021,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53117,0.08742,0.20559]},{"body_a":"world","body_b":"grasp_target","contact_count":1412.0,"contact_point_centroid":[0.45856,-0.02632,-0.0019],"force_p95":0.1356,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12297,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47993,-0.01115,0.20983]},{"body_a":"world","body_b":"grasp_target","contact_count":2212.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45544,-0.02441,0.07557]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4820.0,"contact_point_centroid":[0.44687,-0.00639,0.03369],"force_p95":0.06829,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09924,"mean_force":0.04489,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44687,-0.02561,0.03139]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5171.0,"contact_point_centroid":[0.44672,-0.04484,0.03319],"force_p95":0.06705,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07911,"mean_force":0.04297,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44688,-0.02561,0.0314]}],"total_contact_groups":12},"final_pose_error":0.01474,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.63346,0.20467,0.11063],"final_tcp_position":[0.62309,0.2045,0.13233],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":0.50861,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":354.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1412.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.46011,-0.02303,0.11703],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.09108,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":553.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2212.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.45426,-0.02587,0.03844],"tcp_start":[0.46011,-0.02303,0.11703],"tcp_to_object_dist_end":0.01315,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45845,-0.02568,0.02578],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30328,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.13778,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11791.0,"raw_peak_contact_force":0.19262,"subtask_id":"grasp_1","tcp_end":[0.44685,-0.0256,0.03137],"tcp_start":[0.45426,-0.02587,0.03844],"tcp_to_object_dist_end":0.01288,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":434.0,"n_steps_budget":1000.0,"object_pos_end":[0.45297,-0.02547,0.15463],"object_pos_start":[0.45845,-0.02568,0.02578],"object_to_goal_dist_end":0.29603,"object_to_goal_dist_start":0.30328,"object_z_max":0.15434,"peak_contact_force":0.07434,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":17477.0,"raw_peak_contact_force":0.50861,"tcp_end":[0.4435,-0.02544,0.16225],"tcp_start":[0.44685,-0.0256,0.03137],"tcp_to_object_dist_end":0.01215,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":937.0,"n_steps_budget":1000.0,"object_pos_end":[0.63478,0.19802,0.23649],"object_pos_start":[0.45297,-0.02547,0.15463],"object_to_goal_dist_end":0.12289,"object_to_goal_dist_start":0.29603,"object_z_max":0.23644,"peak_contact_force":0.11118,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":36931.0,"raw_peak_contact_force":0.15828,"subtask_id":"transport_arc","tcp_end":[0.61963,0.19754,0.251],"tcp_start":[0.4435,-0.02544,0.16225],"tcp_to_object_dist_end":0.02098,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":15.0,"n_steps":235.0,"n_steps_budget":1000.0,"object_pos_end":[0.63609,0.20466,0.11754],"object_pos_start":[0.63478,0.19802,0.23649],"object_to_goal_dist_end":0.00774,"object_to_goal_dist_start":0.12289,"object_z_max":0.23649,"peak_contact_force":0.18683,"phase_name":"place_object_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4543.0,"raw_peak_contact_force":0.35752,"tcp_end":[0.62309,0.2045,0.13233],"tcp_start":[0.62427,0.20461,0.1384],"tcp_to_object_dist_end":0.01969,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.97143,"average_solve_count":350.0,"average_success_count":350.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.05084,"approach_1.approach_speed":0.04471,"descend_1.descend_speed":0.04329,"descend_1.grasp_z_offset":0.01775,"lift_1.lift_height":0.12748,"lift_1.lift_speed":0.05039,"place_object_1.place_speed":0.04538,"place_object_1.place_z_offset":0.01237,"transport_to_goal.transport_speed":0.037},"optimized_scores":{"best_composite_score":0.40338,"best_fitness_score":0.97338,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":86.0,"contact_point_centroid":[0.54011,0.00077,-0.00141],"force_p95":0.49833,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.52827,"mean_force":0.17584,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52879,0.00085,0.03594]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7337.0,"contact_point_centroid":[0.52659,-0.01833,0.0899],"force_p95":0.0809,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30476,"mean_force":0.05717,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52605,0.0008,0.08738]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7778.0,"contact_point_centroid":[0.52651,0.01988,0.08787],"force_p95":0.0785,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28888,"mean_force":0.05472,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52605,0.0008,0.08569]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2484.0,"contact_point_centroid":[0.64431,0.16944,0.275],"force_p95":0.09818,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19234,"mean_force":0.07101,"phase_index":5.0,"phase_name":"place_object_1","phase_type":"descend","tcp_position_centroid":[0.63998,0.1507,0.27407]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2252.0,"contact_point_centroid":[0.643,0.13191,0.27523],"force_p95":0.10904,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18569,"mean_force":0.07722,"phase_index":5.0,"phase_name":"place_object_1","phase_type":"descend","tcp_position_centroid":[0.63996,0.15067,0.27464]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5443,0.00102,-0.00203],"force_p95":0.13218,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15396,"mean_force":0.1254,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53116,0.0009,0.03633]},{"body_a":"world","body_b":"grasp_target","contact_count":1676.0,"contact_point_centroid":[0.54431,0.00113,-0.00192],"force_p95":0.13424,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12292,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5164,0.00046,0.20061]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53559,0.00097,0.06339]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4115.0,"contact_point_centroid":[0.5309,-0.01833,0.03757],"force_p95":0.0762,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11941,"mean_force":0.05179,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52991,0.00087,0.03487]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17360.0,"contact_point_centroid":[0.58023,0.05319,0.22819],"force_p95":0.0869,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10863,"mean_force":0.05675,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.57873,0.07221,0.22633]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17527.0,"contact_point_centroid":[0.5831,0.09476,0.23212],"force_p95":0.0802,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09835,"mean_force":0.05581,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.58151,0.07578,0.2307]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4878.0,"contact_point_centroid":[0.53085,0.01995,0.03669],"force_p95":0.06824,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09463,"mean_force":0.04472,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52991,0.00087,0.03488]}],"total_contact_groups":12},"final_pose_error":0.01971,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.65161,0.15448,0.20055],"final_tcp_position":[0.64279,0.15472,0.22228],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":0.52827,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":420.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1676.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.53561,0.00095,0.09844],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.07294,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.5382,0.00102,0.04463],"tcp_start":[0.53561,0.00095,0.09844],"tcp_to_object_dist_end":0.01958,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54419,0.00075,0.02587],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.2505,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.13033,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10793.0,"raw_peak_contact_force":0.15396,"subtask_id":"grasp_1","tcp_end":[0.52988,0.00087,0.03484],"tcp_start":[0.5382,0.00102,0.04463],"tcp_to_object_dist_end":0.01689,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":396.0,"n_steps_budget":1000.0,"object_pos_end":[0.53739,0.00086,0.13044],"object_pos_start":[0.54419,0.00075,0.02587],"object_to_goal_dist_end":0.20137,"object_to_goal_dist_start":0.2505,"object_z_max":0.13019,"peak_contact_force":0.08108,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":15201.0,"raw_peak_contact_force":0.52827,"tcp_end":[0.52596,0.00081,0.14286],"tcp_start":[0.52988,0.00087,0.03484],"tcp_to_object_dist_end":0.01688,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.64456,0.14716,0.29921],"object_pos_start":[0.53739,0.00086,0.13044],"object_to_goal_dist_end":0.1087,"object_to_goal_dist_start":0.20137,"object_z_max":0.29903,"peak_contact_force":0.08961,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":34887.0,"raw_peak_contact_force":0.10863,"subtask_id":"transport_arc","tcp_end":[0.63817,0.14745,0.31931],"tcp_start":[0.52596,0.00081,0.14286],"tcp_to_object_dist_end":0.02109,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":176.0,"n_steps_budget":1000.0,"object_pos_end":[0.65161,0.15448,0.20055],"object_pos_start":[0.64456,0.14716,0.29921],"object_to_goal_dist_end":0.01087,"object_to_goal_dist_start":0.1087,"object_z_max":0.29929,"peak_contact_force":0.10837,"phase_name":"place_object_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4736.0,"raw_peak_contact_force":0.19234,"tcp_end":[0.64279,0.15472,0.22228],"tcp_start":[0.63817,0.14745,0.31931],"tcp_to_object_dist_end":0.02345,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.21654,"average_solve_count":254.0,"average_success_count":254.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.05367,"approach_1.approach_speed":0.0773,"descend_1.descend_speed":0.02953,"descend_1.grasp_z_offset":0.01944,"lift_1.lift_height":0.12629,"lift_1.lift_speed":0.06043,"place_object_1.place_speed":0.07235,"place_object_1.place_z_offset":0.02434,"transport_to_goal.transport_speed":0.05923},"optimized_scores":{"best_composite_score":0.38949,"best_fitness_score":0.95949,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":89.0,"contact_point_centroid":[0.52771,0.02872,-0.00151],"force_p95":0.32121,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.40306,"mean_force":0.1007,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51438,0.02878,0.0487]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1767.0,"contact_point_centroid":[0.59674,0.15363,0.18687],"force_p95":0.19057,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36413,"mean_force":0.11684,"phase_index":5.0,"phase_name":"place_object_1","phase_type":"descend","tcp_position_centroid":[0.59429,0.17189,0.19095]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7452.0,"contact_point_centroid":[0.51309,0.04764,0.10024],"force_p95":0.08989,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29288,"mean_force":0.0575,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51185,0.02862,0.09925]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1715.0,"contact_point_centroid":[0.59704,0.18985,0.18722],"force_p95":0.1847,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28764,"mean_force":0.11734,"phase_index":5.0,"phase_name":"place_object_1","phase_type":"descend","tcp_position_centroid":[0.5943,0.17188,0.19127]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6734.0,"contact_point_centroid":[0.5129,0.0095,0.10033],"force_p95":0.09708,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26423,"mean_force":0.0618,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51185,0.02862,0.09945]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53057,0.03068,-0.00216],"force_p95":0.16627,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22377,"mean_force":0.13398,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51679,0.02895,0.04878]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7182.0,"contact_point_centroid":[0.5511,0.07435,0.19077],"force_p95":0.13266,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19118,"mean_force":0.08714,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54762,0.09291,0.19292]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7988.0,"contact_point_centroid":[0.5537,0.11439,0.19397],"force_p95":0.11607,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18991,"mean_force":0.0762,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54951,0.09606,0.19501]},{"body_a":"world","body_b":"grasp_target","contact_count":1572.0,"contact_point_centroid":[0.5305,0.03079,-0.00191],"force_p95":0.13468,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12294,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51053,0.0132,0.20181]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4325.0,"contact_point_centroid":[0.51645,0.00968,0.04854],"force_p95":0.07688,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13503,"mean_force":0.04955,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51559,0.02887,0.04739]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52213,0.02858,0.06997]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5033.0,"contact_point_centroid":[0.51665,0.04808,0.04859],"force_p95":0.07442,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07649,"mean_force":0.04405,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5156,0.02887,0.0474]}],"total_contact_groups":12},"final_pose_error":0.01507,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.5946,0.17551,0.10951],"final_tcp_position":[0.59496,0.17495,0.1455],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":91.63557,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":394.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1572.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52336,0.02718,0.10149],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.07589,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.52353,0.02938,0.05666],"tcp_start":[0.52336,0.02718,0.10149],"tcp_to_object_dist_end":0.03145,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53049,0.02951,0.02545],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18466,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.16228,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11158.0,"raw_peak_contact_force":0.22377,"subtask_id":"grasp_1","tcp_end":[0.51556,0.02887,0.04736],"tcp_start":[0.52353,0.02938,0.05666],"tcp_to_object_dist_end":0.02652,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":33.0,"n_steps":376.0,"n_steps_budget":1000.0,"object_pos_end":[0.52295,0.02908,0.12793],"object_pos_start":[0.53049,0.02951,0.02545],"object_to_goal_dist_end":0.17005,"object_to_goal_dist_start":0.18466,"object_z_max":0.12767,"peak_contact_force":0.1027,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":14275.0,"raw_peak_contact_force":0.40306,"tcp_end":[0.51177,0.02861,0.15403],"tcp_start":[0.51556,0.02887,0.04736],"tcp_to_object_dist_end":0.0284,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":17.0,"n_steps":661.0,"n_steps_budget":1000.0,"object_pos_end":[0.59826,0.16933,0.21027],"object_pos_start":[0.52295,0.02908,0.12793],"object_to_goal_dist_end":0.10265,"object_to_goal_dist_start":0.17005,"object_z_max":0.21016,"peak_contact_force":0.12733,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":15170.0,"raw_peak_contact_force":0.19118,"subtask_id":"transport_arc","tcp_end":[0.59305,0.16816,0.24336],"tcp_start":[0.51177,0.02861,0.15403],"tcp_to_object_dist_end":0.03352,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":21.0,"n_steps":187.0,"n_steps_budget":1000.0,"object_pos_end":[0.59632,0.1749,0.11601],"object_pos_start":[0.59826,0.16933,0.21027],"object_to_goal_dist_end":0.01017,"object_to_goal_dist_start":0.10265,"object_z_max":0.21029,"peak_contact_force":91.63557,"phase_name":"place_object_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3482.0,"raw_peak_contact_force":0.36413,"tcp_end":[0.59496,0.17495,0.1455],"tcp_start":[0.59618,0.17497,0.15131],"tcp_to_object_dist_end":0.02952,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```