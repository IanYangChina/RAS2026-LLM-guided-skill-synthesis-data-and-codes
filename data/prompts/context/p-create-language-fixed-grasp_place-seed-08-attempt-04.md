## Search State

- **Seed**: 8
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → descend → contact → lift → approach → descend | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.4199 | 0.23 | ❌ rejected |
| 3 | approach → descend → contact → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6 | 0.2086 | 0.21 | ❌ rejected |
| 2 | approach → descend → contact → lift → approach → descend → release → approach | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.2506 | 0.20 | ❌ rejected |
| 1 | approach → descend → contact → lift → approach → descend → release | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.2766 | 0.16 | ❌ rejected |
| 0 | approach → descend → contact → lift → approach → descend | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.4299 | 0.25 | ✅ accepted |

**Proposal policy**: task_score is 0.23 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c`
- Frozen object start: [0.48269722766055606, 0.048727684333792556, 0.03]
- Frozen task target: [0.5818710838485517, 0.2288548935820029, 0.2304844767544324]
- Goal object position: (0.5818710838485517, 0.2288548935820029, 0.2304844767544324)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5818710838485517, 0.2288548935820029, 0.2304844767544324)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.48269722766055606, 0.048727684333792556, 0.03)
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
  frozen_object_start: [0.4827, 0.0487, 0.03]
  frozen_task_target: [0.5819, 0.2289, 0.2305]
  frozen_object_starts: {'grasp_target': [0.48269722766055606, 0.048727684333792556, 0.03]}
  frozen_targets: {'place_target': [0.5818710838485517, 0.2288548935820029, 0.2304844767544324]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c

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

## Current Skill (Q=0.420) — your mutation base

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
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.08
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.08
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: approach_1
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
    - 0.02
    orientation:
      mode: keep_current
  subtask_id: descend_1
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    contact_force:
      type: scalar
      range:
      - 1.0
      - 20.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
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
    - 0.1
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
- id: transport_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: placement_surface
    offset:
    - 0.0
    - 0.0
    - 0.1
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
- id: release_1
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  end_effector_action: open
  target:
    source: yaml
    anchor: task_goal
    entity: placement_surface
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
  subtask_id: release_1

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.08]
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.02]
  - orientation: mode=keep_current
  - parameter_bindings: none
- **contact_1** (`contact`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
- **lift_1** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1]
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
- **transport_1** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.1]
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **release_1** (`descend`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.420
- **task_score** (E): 0.234
- **fitness_score**: 0.573  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.167
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.320

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0811 |
| descend_1 | 1.00 | 1.00 | 0.1767 |
| contact_1 | 1.00 | 1.00 | 0.0095 |
| lift_1 | 1.00 | 1.00 | 0.1125 |
| transport_1 | 0.00 | 1.00 | 0.0882 |
| release_1 | 0.33 | 1.00 | 0.1080 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.516, -0.001, 0.231) | (0.522, -0.001, 0.030)→(0.522, -0.001, 0.026) | 0.287→0.289 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.516, -0.001, 0.231)→(0.517, -0.001, 0.055) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 4.000 | 0.123 | 0.123 |
| contact_1 | contact | 1.00 / force_exceeded | (0.517, -0.001, 0.055)→(0.511, -0.001, 0.047) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 43.333 | 0.142 | 0.187 |
| lift_1 | lift | 1.00 / step_budget | (0.511, -0.001, 0.047)→(0.507, -0.001, 0.159) | (0.522, -0.001, 0.026)→(0.518, -0.001, 0.132) | 0.289→0.239 | 1.00 / 25.000 | 0.113 | 0.428 |
| transport_1 | approach | 0.00 / step_budget | (0.507, -0.001, 0.159)→(0.538, 0.069, 0.203) | (0.518, -0.001, 0.132)→(0.544, 0.076, 0.107) | 0.239→0.194 | 1.00 / 15.000 | 0.128 | 0.722 |
| release_1 | descend | 0.33 / step_budget | (0.538, 0.069, 0.203)→(0.583, 0.166, 0.188) | (0.544, 0.076, 0.107)→(0.565, 0.107, 0.016) | 0.194→0.219 | 1.00 / 4.000 | 0.123 | 1.039 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.287
- phase_score: 0.301
- phase_breakdown.approach_1_score: 0.026
- phase_breakdown.descend_1_score: 0.873
- phase_breakdown.transport_arc_score: 0.041
- phase_breakdown.release_1_score: 0.263
- phase_breakdown.grasp_1_score: 1.000
- grasp_place_fitness: 0.600

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.600
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.287
- **Median Q (composite search score)**: 0.409
- **K-run variance**: 0.0004
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.342


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `2cbd02033d1f1347f2ac2d0b012406a96501e6b48f5b172bd88b34d6c745630c`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `5745d7c2d025a63f908a4bf0f58182445bb06541d436718f39304ac5569d60c0`; realized-scene SHA-256: `f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.4827,0.04873,0.03]},{"name":"goal","value":[0.58187,0.22885,0.23048]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.4827,0.04873,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58187,0.22885,0.23048]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.84211,"average_solve_count":152.0,"average_success_count":152.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.19988,"contact_1.contact_force":17.20098,"lift_1.lift_height":0.14016,"transport_1.transport_speed":0.07316},"optimized_scores":{"best_composite_score":0.4038,"best_fitness_score":0.55713,"best_task_score":0.20298},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":467.0,"contact_point_centroid":[0.51934,0.14312,-0.00426],"force_p95":0.93848,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.83614,"mean_force":0.23842,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.50994,0.11678,0.23067]},{"body_a":"world","body_b":"grasp_target","contact_count":139.0,"contact_point_centroid":[0.48019,0.04638,-0.00121],"force_p95":0.26151,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.39583,"mean_force":0.05498,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47167,0.04709,0.0506]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14057.0,"contact_point_centroid":[0.47083,0.06569,0.107],"force_p95":0.10009,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29646,"mean_force":0.05958,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46927,0.04686,0.10654]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13212.0,"contact_point_centroid":[0.46997,0.02787,0.10563],"force_p95":0.12227,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29408,"mean_force":0.06356,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46924,0.04686,0.10586]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6807.0,"contact_point_centroid":[0.49091,0.06019,0.19555],"force_p95":0.13448,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24271,"mean_force":0.10273,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.4861,0.07844,0.19918]},{"body_a":"world","body_b":"grasp_target","contact_count":1632.0,"contact_point_centroid":[0.48273,0.04861,-0.00214],"force_p95":0.15713,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21266,"mean_force":0.13257,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47371,0.0473,0.04931]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7475.0,"contact_point_centroid":[0.49073,0.09539,0.19533],"force_p95":0.12815,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1882,"mean_force":0.09474,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.48543,0.07729,0.19829]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4092.0,"contact_point_centroid":[0.47237,0.02803,0.04949],"force_p95":0.07958,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14622,"mean_force":0.05209,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47315,0.04724,0.0487]},{"body_a":"world","body_b":"grasp_target","contact_count":992.0,"contact_point_centroid":[0.4827,0.04873,-0.00187],"force_p95":0.13691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12312,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4908,0.01938,0.26798]},{"body_a":"world","body_b":"grasp_target","contact_count":4600.0,"contact_point_centroid":[0.51902,0.1436,-0.00199],"force_p95":0.12265,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12698,"mean_force":0.12265,"phase_index":5.0,"phase_name":"release_1","phase_type":"descend","tcp_position_centroid":[0.54858,0.181,0.22433]},{"body_a":"world","body_b":"grasp_target","contact_count":2260.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47927,0.04413,0.14441]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4988.0,"contact_point_centroid":[0.47323,0.06635,0.04957],"force_p95":0.07308,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0742,"mean_force":0.04409,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47315,0.04724,0.0487]},{"body_a":"left_finger","body_b":"right_finger","contact_count":276.0,"contact_point_centroid":[0.5115,0.1185,0.23407],"force_p95":0.0144,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01552,"mean_force":0.01125,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51101,0.11849,0.23208]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4288.0,"contact_point_centroid":[0.54572,0.17544,0.2277],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01277,"mean_force":0.0104,"phase_index":5.0,"phase_name":"release_1","phase_type":"descend","tcp_position_centroid":[0.54521,0.17542,0.22538]}],"total_contact_groups":14},"final_pose_error":0.01477,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.51902,0.1436,0.01602],"final_tcp_position":[0.57353,0.21945,0.22274],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":1.83614,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":249.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":992.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.48243,0.04075,0.23574],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.20988,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":565.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2260.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.47844,0.04772,0.05499],"tcp_start":[0.48243,0.04075,0.23574],"tcp_to_object_dist_end":0.0293,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":8.0,"n_steps_budget":600.0,"object_pos_end":[0.48266,0.04765,0.02556],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29099,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.15375,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":10712.0,"raw_peak_contact_force":0.21266,"subtask_id":"grasp_1","tcp_end":[0.47312,0.04724,0.04867],"tcp_start":[0.47844,0.04772,0.05499],"tcp_to_object_dist_end":0.02501,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":813.0,"n_steps_budget":900.0,"object_pos_end":[0.47802,0.04808,0.14659],"object_pos_start":[0.48266,0.04765,0.02556],"object_to_goal_dist_end":0.22473,"object_to_goal_dist_start":0.29099,"object_z_max":0.14648,"peak_contact_force":0.13532,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":27408.0,"raw_peak_contact_force":0.39583,"tcp_end":[0.46954,0.0469,0.17732],"tcp_start":[0.47312,0.04724,0.04867],"tcp_to_object_dist_end":0.03191,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5192,0.14367,0.01606],"object_pos_start":[0.47802,0.04808,0.14659],"object_to_goal_dist_end":0.23908,"object_to_goal_dist_start":0.22473,"object_z_max":0.18294,"peak_contact_force":0.12727,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":15025.0,"raw_peak_contact_force":1.83614,"subtask_id":"transport_arc","tcp_end":[0.5124,0.12068,0.2339],"tcp_start":[0.46954,0.0469,0.17732],"tcp_to_object_dist_end":0.21915,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51902,0.1436,0.01602],"object_pos_start":[0.5192,0.14367,0.01606],"object_to_goal_dist_end":0.2392,"object_to_goal_dist_start":0.23908,"object_z_max":0.01606,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8888.0,"raw_peak_contact_force":0.12698,"subtask_id":"release_1","tcp_end":[0.57041,0.21816,0.21507],"tcp_start":[0.5124,0.12068,0.2339],"tcp_to_object_dist_end":0.21868,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `2b35d39beba75b46a5edd8e67b975c00ef2c88fb75a3753bdd32db5918adf9e2`; realized-scene SHA-256: `0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53702,-0.02132,0.03]},{"name":"goal","value":[0.61031,0.22775,0.20741]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.53702,-0.02132,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.61031,0.22775,0.20741]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.75497,"average_solve_count":151.0,"average_success_count":151.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.21254,"contact_1.contact_force":12.05612,"lift_1.lift_height":0.13139,"transport_1.transport_speed":0.06932},"optimized_scores":{"best_composite_score":0.40913,"best_fitness_score":0.56247,"best_task_score":0.21274},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3369.0,"contact_point_centroid":[0.57774,0.10036,-0.00231],"force_p95":0.12747,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.70278,"mean_force":0.13863,"phase_index":5.0,"phase_name":"release_1","phase_type":"descend","tcp_position_centroid":[0.57446,0.14179,0.19783]},{"body_a":"world","body_b":"grasp_target","contact_count":146.0,"contact_point_centroid":[0.53459,-0.02063,-0.00115],"force_p95":0.30619,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.44087,"mean_force":0.06606,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52445,-0.02086,0.04864]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12220.0,"contact_point_centroid":[0.52359,-0.00177,0.10026],"force_p95":0.10193,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29859,"mean_force":0.06295,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52188,-0.0208,0.09942]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13669.0,"contact_point_centroid":[0.52335,-0.03973,0.10031],"force_p95":0.0945,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29336,"mean_force":0.05699,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52188,-0.0208,0.09948]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1711.0,"contact_point_centroid":[0.55699,0.09472,0.19541],"force_p95":0.14104,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24506,"mean_force":0.11119,"phase_index":5.0,"phase_name":"release_1","phase_type":"descend","tcp_position_centroid":[0.55108,0.0765,0.20037]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10994.0,"contact_point_centroid":[0.53842,0.00185,0.18187],"force_p95":0.11506,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16657,"mean_force":0.08272,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53323,0.02017,0.18327]},{"body_a":"world","body_b":"grasp_target","contact_count":1632.0,"contact_point_centroid":[0.53703,-0.02126,-0.00205],"force_p95":0.13582,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16584,"mean_force":0.12662,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52669,-0.0209,0.04767]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10005.0,"contact_point_centroid":[0.53805,0.03733,0.1812],"force_p95":0.13429,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16312,"mean_force":0.09059,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53277,0.01882,0.18255]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1966.0,"contact_point_centroid":[0.55679,0.05871,0.19584],"force_p95":0.12283,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14598,"mean_force":0.09538,"phase_index":5.0,"phase_name":"release_1","phase_type":"descend","tcp_position_centroid":[0.55116,0.07668,0.2004]},{"body_a":"world","body_b":"grasp_target","contact_count":980.0,"contact_point_centroid":[0.53702,-0.02132,-0.00187],"force_p95":0.13691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12313,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51303,-0.00875,0.27209]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4269.0,"contact_point_centroid":[0.52671,-0.00168,0.04814],"force_p95":0.07555,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12518,"mean_force":0.05042,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52608,-0.02089,0.04693]},{"body_a":"world","body_b":"grasp_target","contact_count":2292.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52883,-0.01943,0.14903]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4888.0,"contact_point_centroid":[0.52624,-0.03998,0.04836],"force_p95":0.0684,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08783,"mean_force":0.04446,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52608,-0.02089,0.04693]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2721.0,"contact_point_centroid":[0.57417,0.13893,0.20102],"force_p95":0.01107,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01609,"mean_force":0.01059,"phase_index":5.0,"phase_name":"release_1","phase_type":"descend","tcp_position_centroid":[0.57378,0.13892,0.19879]}],"total_contact_groups":14},"final_pose_error":0.06577,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.57773,0.10047,0.01602],"final_tcp_position":[0.58465,0.16783,0.19873],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":1.70278,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":246.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":980.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52824,-0.01795,0.24542],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.21961,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":573.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2292.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53179,-0.02098,0.05451],"tcp_start":[0.52824,-0.01795,0.24542],"tcp_to_object_dist_end":0.02897,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":8.0,"n_steps_budget":600.0,"object_pos_end":[0.53695,-0.02099,0.02582],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31659,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13484,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":10789.0,"raw_peak_contact_force":0.16584,"subtask_id":"grasp_1","tcp_end":[0.52606,-0.02089,0.0469],"tcp_start":[0.53179,-0.02098,0.05451],"tcp_to_object_dist_end":0.02373,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":753.0,"n_steps_budget":840.0,"object_pos_end":[0.5327,-0.02101,0.13824],"object_pos_start":[0.53695,-0.02099,0.02582],"object_to_goal_dist_end":0.26961,"object_to_goal_dist_start":0.31659,"object_z_max":0.13812,"peak_contact_force":0.09961,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":26035.0,"raw_peak_contact_force":0.44087,"tcp_end":[0.52219,-0.0208,0.16577],"tcp_start":[0.52606,-0.02089,0.0469],"tcp_to_object_dist_end":0.02947,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5529,0.05958,0.1687],"object_pos_start":[0.5327,-0.02101,0.13824],"object_to_goal_dist_end":0.18187,"object_to_goal_dist_start":0.26961,"object_z_max":0.16866,"peak_contact_force":0.11413,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":20999.0,"raw_peak_contact_force":0.16657,"subtask_id":"transport_arc","tcp_end":[0.54738,0.05993,0.20531],"tcp_start":[0.52219,-0.0208,0.16577],"tcp_to_object_dist_end":0.03703,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.57773,0.10047,0.01602],"object_pos_start":[0.5529,0.05958,0.1687],"object_to_goal_dist_end":0.23215,"object_to_goal_dist_start":0.18187,"object_z_max":0.1687,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9767.0,"raw_peak_contact_force":1.70278,"subtask_id":"release_1","tcp_end":[0.58114,0.16676,0.19116],"tcp_start":[0.54738,0.05993,0.20531],"tcp_to_object_dist_end":0.1873,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `530652a2467d9ac78fab654e7ed7fc5283ca1649270bc8f158e04c16074f9f95`; realized-scene SHA-256: `9bdc6de22965641ffcaccb8421100561fe91fb98e16735236cc25272572d8879`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5456,-0.02923,0.03]},{"name":"goal","value":[0.63284,0.16493,0.17692]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5456,-0.02923,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63284,0.16493,0.17692]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.58621,"average_solve_count":145.0,"average_success_count":145.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.1782,"contact_1.contact_force":8.50698,"lift_1.lift_height":0.10247,"transport_1.transport_speed":0.01677},"optimized_scores":{"best_composite_score":0.44681,"best_fitness_score":0.60014,"best_task_score":0.28721},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1597.0,"contact_point_centroid":[0.59813,0.07591,-0.00254],"force_p95":0.2797,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.28657,"mean_force":0.14535,"phase_index":5.0,"phase_name":"release_1","phase_type":"descend","tcp_position_centroid":[0.59602,0.10725,0.16364]},{"body_a":"world","body_b":"grasp_target","contact_count":149.0,"contact_point_centroid":[0.54304,-0.02822,-0.00116],"force_p95":0.30322,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.44874,"mean_force":0.06967,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53255,-0.02858,0.04722]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10147.0,"contact_point_centroid":[0.5311,-0.00938,0.08887],"force_p95":0.09619,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28521,"mean_force":0.0585,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52995,-0.02849,0.08702]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11431.0,"contact_point_centroid":[0.53116,-0.04751,0.08757],"force_p95":0.08822,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27911,"mean_force":0.05293,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52996,-0.02849,0.08591]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5848.0,"contact_point_centroid":[0.57675,0.08023,0.16003],"force_p95":0.12551,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24786,"mean_force":0.10333,"phase_index":5.0,"phase_name":"release_1","phase_type":"descend","tcp_position_centroid":[0.57173,0.06196,0.16412]},{"body_a":"world","body_b":"grasp_target","contact_count":1648.0,"contact_point_centroid":[0.54561,-0.02913,-0.00207],"force_p95":0.13894,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18236,"mean_force":0.12776,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53489,-0.02865,0.04634]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6352.0,"contact_point_centroid":[0.57704,0.04461,0.16005],"force_p95":0.12103,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17556,"mean_force":0.09498,"phase_index":5.0,"phase_name":"release_1","phase_type":"descend","tcp_position_centroid":[0.57218,0.06276,0.16415]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12249.0,"contact_point_centroid":[0.54598,0.01952,0.14977],"force_p95":0.11965,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16256,"mean_force":0.07567,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54175,0.0009,0.15073]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13359.0,"contact_point_centroid":[0.54573,-0.01772,0.14993],"force_p95":0.11067,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16047,"mean_force":0.06999,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54173,0.00081,0.1507]},{"body_a":"world","body_b":"grasp_target","contact_count":1408.0,"contact_point_centroid":[0.5456,-0.02923,-0.0019],"force_p95":0.1356,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12297,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51747,-0.01272,0.25525]},{"body_a":"world","body_b":"grasp_target","contact_count":1896.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53746,-0.02728,0.13247]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4839.0,"contact_point_centroid":[0.53361,-0.00934,0.04792],"force_p95":0.06831,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0985,"mean_force":0.04501,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53422,-0.02863,0.04551]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5637.0,"contact_point_centroid":[0.53375,-0.04783,0.04729],"force_p95":0.06243,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07763,"mean_force":0.03949,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53423,-0.02863,0.04551]},{"body_a":"left_finger","body_b":"right_finger","contact_count":747.0,"contact_point_centroid":[0.59705,0.10671,0.16788],"force_p95":0.0134,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0157,"mean_force":0.01078,"phase_index":5.0,"phase_name":"release_1","phase_type":"descend","tcp_position_centroid":[0.59668,0.10671,0.16564]}],"total_contact_groups":14},"final_pose_error":0.06217,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.59817,0.0759,0.01602],"final_tcp_position":[0.60027,0.11313,0.16591],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":1.28657,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":353.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1408.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.53724,-0.02587,0.21223],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.18643,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":474.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1896.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.54022,-0.02879,0.05415],"tcp_start":[0.53724,-0.02587,0.21223],"tcp_to_object_dist_end":0.02865,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":12.0,"n_steps_budget":600.0,"object_pos_end":[0.54553,-0.0287,0.02577],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.2607,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.13701,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":12124.0,"raw_peak_contact_force":0.18236,"subtask_id":"grasp_1","tcp_end":[0.5342,-0.02863,0.04548],"tcp_start":[0.54022,-0.02879,0.05415],"tcp_to_object_dist_end":0.02273,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":573.0,"n_steps_budget":660.0,"object_pos_end":[0.54231,-0.02862,0.11087],"object_pos_start":[0.54553,-0.0287,0.02577],"object_to_goal_dist_end":0.22365,"object_to_goal_dist_start":0.2607,"object_z_max":0.11075,"peak_contact_force":0.10305,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":21727.0,"raw_peak_contact_force":0.44874,"tcp_end":[0.53003,-0.02848,0.13529],"tcp_start":[0.5342,-0.02863,0.04548],"tcp_to_object_dist_end":0.02734,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56029,0.02574,0.13561],"object_pos_start":[0.54231,-0.02862,0.11087],"object_to_goal_dist_end":0.1623,"object_to_goal_dist_start":0.22365,"object_z_max":0.13559,"peak_contact_force":0.14209,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":25608.0,"raw_peak_contact_force":0.16256,"subtask_id":"transport_arc","tcp_end":[0.55519,0.02617,0.1687],"tcp_start":[0.53003,-0.02848,0.13529],"tcp_to_object_dist_end":0.03349,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.59817,0.0759,0.01602],"object_pos_start":[0.56029,0.02574,0.13561],"object_to_goal_dist_end":0.18713,"object_to_goal_dist_start":0.1623,"object_z_max":0.13561,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":14544.0,"raw_peak_contact_force":1.28657,"subtask_id":"release_1","tcp_end":[0.5963,0.11232,0.15829],"tcp_start":[0.55519,0.02617,0.1687],"tcp_to_object_dist_end":0.14687,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```