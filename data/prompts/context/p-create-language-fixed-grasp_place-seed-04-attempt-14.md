## Search State

- **Seed**: 4
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | 0.2305 | 0.31 | ❌ rejected |
| 13 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | 4 | 0.3140 | 0.32 | ❌ rejected |
| 12 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | 3 | 0.3649 | 0.32 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | 3 | 0.3424 | 0.27 | ❌ rejected |
| 10 | approach → descend → grasp → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | time_limit | 1 | 0.3400 | 0.34 | ✅ accepted |

**Proposal policy**: task_score is 0.31 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.231) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: approach_1
  anchor: object
- id: descend_1
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.02
- id: grasp_1
  anchor: object
  metric: contact
  offset:
  - 0.0
  - 0.0
  - 0.02
- id: transport_arc
- id: release_1
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
    - 0.0
    offset_along_axis:
      distance: 0.05
      axis: world_z
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.05
      binds_to:
      - path: target.offset_along_axis.distance
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
    tolerance: 0.005
    orientation:
      mode: keep_current
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
    orientation:
      mode: keep_current
  subtask_id: grasp_1
- id: transport_arc
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
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
  subtask_id: transport_arc
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
    orientation:
      mode: keep_current
  subtask_id: release_1

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.05, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.02], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings: none
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none
- **transport_arc** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings: none
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.231
- **task_score** (E): 0.312
- **fitness_score**: 0.631  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.400

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1494 |
| descend_1 | 1.00 | 1.00 | 0.1102 |
| grasp_1 | 1.00 | 1.00 | 0.0123 |
| lift_1 | 1.00 | 1.00 | 0.1458 |
| transport_arc | 1.00 | 0.67 | 0.1907 |
| place_descend | 1.00 | 1.00 | 0.0525 |
| release_1 | 1.00 | 1.00 | 0.0209 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.520, 0.006, 0.154) | (0.526, 0.005, 0.030)→(0.526, 0.005, 0.026) | 0.246→0.249 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.520, 0.006, 0.154)→(0.521, 0.005, 0.044) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.521, 0.005, 0.044)→(0.513, 0.005, 0.035) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 43.000 | 0.135 | 0.179 |
| lift_1 | lift | 1.00 / step_budget | (0.513, 0.005, 0.035)→(0.509, 0.005, 0.181) | (0.526, 0.005, 0.026)→(0.527, 0.005, 0.165) | 0.249→0.196 | 1.00 / 23.667 | 0.108 | 0.566 |
| transport_arc | approach | 1.00 / step_budget | (0.509, 0.005, 0.181)→(0.601, 0.160, 0.232) | (0.527, 0.005, 0.165)→(0.561, 0.098, 0.029) | 0.196→0.181 | 0.67 / 5.333 | 0.082 | 1.307 |
| place_descend | descend | 1.00 / step_budget | (0.601, 0.160, 0.232)→(0.608, 0.173, 0.182) | (0.561, 0.098, 0.029)→(0.562, 0.104, 0.016) | 0.181→0.195 | 1.00 / 8.333 | 91001.534 | 0.611 |
| release_1 | release | 1.00 / step_budget | (0.608, 0.173, 0.182)→(0.602, 0.171, 0.202) | (0.562, 0.104, 0.016)→(0.562, 0.104, 0.016) | 0.195→0.195 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.538
- phase_score: 0.515
- phase_breakdown.descend_1_score: 0.830
- phase_breakdown.transport_arc_score: 0.335
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.approach_1_score: 0.216
- phase_breakdown.release_1_score: 0.583
- grasp_place_fitness: 0.745

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.745
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.538
- **Median Q (composite search score)**: 0.196
- **K-run variance**: 0.0069
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.399


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.77987,"average_solve_count":159.0,"average_success_count":159.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.07852,"lift_1.lift_height":0.16521,"place_descend.place_z_offset":0.01571,"transport_arc.arc_height":0.46591,"transport_arc.transport_height":0.05212},"optimized_scores":{"best_composite_score":0.19602,"best_fitness_score":0.59602,"best_task_score":0.23992},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1569.0,"contact_point_centroid":[0.56518,0.06667,-0.00267],"force_p95":0.30728,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.74586,"mean_force":0.15355,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.5951,0.09294,0.22855]},{"body_a":"world","body_b":"grasp_target","contact_count":78.0,"contact_point_centroid":[0.54104,0.00076,-0.00134],"force_p95":0.53588,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.59794,"mean_force":0.12446,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52933,0.00086,0.03376]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6984.0,"contact_point_centroid":[0.52987,-0.01801,0.09809],"force_p95":0.11042,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33459,"mean_force":0.07265,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52666,0.00082,0.09625]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7089.0,"contact_point_centroid":[0.52973,0.01966,0.09699],"force_p95":0.11007,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31264,"mean_force":0.0718,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5267,0.00082,0.09498]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1162.0,"contact_point_centroid":[0.5402,0.03099,0.18525],"force_p95":0.19918,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28069,"mean_force":0.10836,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.53427,0.01269,0.18691]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1091.0,"contact_point_centroid":[0.5393,-0.00722,0.1847],"force_p95":0.21172,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27968,"mean_force":0.10999,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.53327,0.01117,0.18577]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5443,0.00101,-0.00203],"force_p95":0.13163,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15436,"mean_force":0.12529,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53186,0.00091,0.03393]},{"body_a":"world","body_b":"grasp_target","contact_count":1376.0,"contact_point_centroid":[0.54431,0.00113,-0.0019],"force_p95":0.1356,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12298,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51656,0.00045,0.21408]},{"body_a":"world","body_b":"grasp_target","contact_count":3572.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53591,0.00097,0.07508]},{"body_a":"world","body_b":"grasp_target","contact_count":3256.0,"contact_point_centroid":[0.56497,0.06665,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.63929,0.15161,0.20997]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.56497,0.06665,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.63975,0.15544,0.19827]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4116.0,"contact_point_centroid":[0.53136,-0.01832,0.0352],"force_p95":0.07611,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11688,"mean_force":0.05176,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53061,0.00089,0.03248]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4878.0,"contact_point_centroid":[0.53134,0.01996,0.03432],"force_p95":0.06811,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09477,"mean_force":0.04474,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53061,0.00089,0.03248]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1446.0,"contact_point_centroid":[0.60027,0.09909,0.2329],"force_p95":0.01122,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01427,"mean_force":0.01063,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.59988,0.09908,0.23066]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3492.0,"contact_point_centroid":[0.63967,0.15163,0.21221],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01284,"mean_force":0.0104,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.63928,0.15161,0.20997]},{"body_a":"left_finger","body_b":"right_finger","contact_count":223.0,"contact_point_centroid":[0.64265,0.15622,0.19745],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0127,"mean_force":0.01001,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.64227,0.1562,0.19534]}],"total_contact_groups":16},"final_pose_error":0.00934,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.56497,0.06665,0.01602],"final_tcp_position":[0.64354,0.15653,0.19856],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":273004.35603,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":345.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1376.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.53544,0.00094,0.12609],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.10046,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":893.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3572.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53894,0.00103,0.04224],"tcp_start":[0.53544,0.00094,0.12609],"tcp_to_object_dist_end":0.01709,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54418,0.00076,0.02588],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.2505,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12981,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10794.0,"raw_peak_contact_force":0.15436,"subtask_id":"grasp_1","tcp_end":[0.53058,0.00088,0.03244],"tcp_start":[0.53894,0.00103,0.04224],"tcp_to_object_dist_end":0.0151,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":486.0,"n_steps_budget":1000.0,"object_pos_end":[0.54495,0.00094,0.16371],"object_pos_start":[0.54418,0.00076,0.02588],"object_to_goal_dist_end":0.1897,"object_to_goal_dist_start":0.2505,"object_z_max":0.16346,"peak_contact_force":0.11375,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":14151.0,"raw_peak_contact_force":0.59794,"tcp_end":[0.52694,0.00083,0.17804],"tcp_start":[0.53058,0.00088,0.03244],"tcp_to_object_dist_end":0.02302,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":602.0,"n_steps_budget":1000.0,"object_pos_end":[0.56497,0.06665,0.01602],"object_pos_start":[0.54495,0.00094,0.16371],"object_to_goal_dist_end":0.21412,"object_to_goal_dist_start":0.1897,"object_z_max":0.17574,"peak_contact_force":0.12263,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5268.0,"raw_peak_contact_force":1.74586,"subtask_id":"transport_arc","tcp_end":[0.63523,0.14439,0.23564],"tcp_start":[0.52694,0.00083,0.17804],"tcp_to_object_dist_end":0.24334,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":814.0,"n_steps_budget":1000.0,"object_pos_end":[0.56497,0.06665,0.01602],"object_pos_start":[0.56497,0.06665,0.01602],"object_to_goal_dist_end":0.21412,"object_to_goal_dist_start":0.21412,"object_z_max":0.01602,"peak_contact_force":273004.35603,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":6748.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.64354,0.15653,0.19856],"tcp_start":[0.63523,0.14439,0.23564],"tcp_to_object_dist_end":0.21811,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56497,0.06665,0.01602],"object_pos_start":[0.56497,0.06665,0.01602],"object_to_goal_dist_end":0.21412,"object_to_goal_dist_start":0.21412,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1023.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.63831,0.15499,0.21736],"tcp_start":[0.64354,0.15653,0.19856],"tcp_to_object_dist_end":0.23177,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.71053,"average_solve_count":152.0,"average_success_count":152.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.05808,"lift_1.lift_height":0.14655,"place_descend.place_z_offset":0.00981,"transport_arc.arc_height":0.31743,"transport_arc.transport_height":0.05066},"optimized_scores":{"best_composite_score":0.34488,"best_fitness_score":0.74488,"best_task_score":0.53792},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3602.0,"contact_point_centroid":[0.6059,0.1908,-0.00226],"force_p95":0.12852,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.58808,"mean_force":0.13718,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.59195,0.17042,0.128]},{"body_a":"world","body_b":"grasp_target","contact_count":79.0,"contact_point_centroid":[0.52765,0.02935,-0.0014],"force_p95":0.55695,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.59071,"mean_force":0.12501,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51579,0.02968,0.03441]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6171.0,"contact_point_centroid":[0.51598,0.01061,0.09222],"force_p95":0.10792,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32812,"mean_force":0.07093,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51326,0.02951,0.08995]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6560.0,"contact_point_centroid":[0.51594,0.04838,0.0891],"force_p95":0.1074,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32006,"mean_force":0.0678,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51329,0.02951,0.08721]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3315.0,"contact_point_centroid":[0.54445,0.05857,0.17045],"force_p95":0.17856,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29613,"mean_force":0.10819,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.53907,0.07705,0.17021]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3982.0,"contact_point_centroid":[0.54727,0.09956,0.17031],"force_p95":0.14593,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27385,"mean_force":0.09327,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.54152,0.08141,0.17073]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53053,0.03058,-0.00209],"force_p95":0.14965,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2173,"mean_force":0.12992,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51835,0.02986,0.03443]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4083.0,"contact_point_centroid":[0.51776,0.01058,0.03583],"force_p95":0.07919,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14045,"mean_force":0.05186,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51713,0.02978,0.03305]},{"body_a":"world","body_b":"grasp_target","contact_count":1512.0,"contact_point_centroid":[0.5305,0.03079,-0.00191],"force_p95":0.13487,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12295,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51076,0.01316,0.20413]},{"body_a":"world","body_b":"grasp_target","contact_count":3324.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52306,0.02896,0.06569]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.60596,0.19097,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59159,0.17501,0.11225]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4956.0,"contact_point_centroid":[0.51775,0.0489,0.03486],"force_p95":0.07172,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08407,"mean_force":0.04467,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51713,0.02978,0.03305]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3555.0,"contact_point_centroid":[0.5927,0.17086,0.12883],"force_p95":0.01109,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01634,"mean_force":0.01062,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.59222,0.17084,0.12654]},{"body_a":"left_finger","body_b":"right_finger","contact_count":219.0,"contact_point_centroid":[0.59543,0.17608,0.11053],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01099,"mean_force":0.01019,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59482,0.17606,0.10838]}],"total_contact_groups":14},"final_pose_error":0.00861,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.60596,0.19097,0.01602],"final_tcp_position":[0.59644,0.17654,0.11126],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":1.58808,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":379.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1512.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52352,0.02708,0.10628],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.08065,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":831.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3324.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.52526,0.03032,0.04233],"tcp_start":[0.52352,0.02708,0.10628],"tcp_to_object_dist_end":0.01714,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5304,0.0298,0.02568],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18436,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.14414,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10839.0,"raw_peak_contact_force":0.2173,"subtask_id":"grasp_1","tcp_end":[0.5171,0.02977,0.03301],"tcp_start":[0.52526,0.03032,0.04233],"tcp_to_object_dist_end":0.01519,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":418.0,"n_steps_budget":930.0,"object_pos_end":[0.53109,0.02966,0.14678],"object_pos_start":[0.5304,0.0298,0.02568],"object_to_goal_dist_end":0.16922,"object_to_goal_dist_start":0.18436,"object_z_max":0.14652,"peak_contact_force":0.10172,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":12810.0,"raw_peak_contact_force":0.59071,"tcp_end":[0.51336,0.02952,0.16018],"tcp_start":[0.5171,0.02977,0.03301],"tcp_to_object_dist_end":0.02223,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":443.0,"n_steps_budget":1000.0,"object_pos_end":[0.60197,0.17261,0.05474],"object_pos_start":[0.53109,0.02966,0.14678],"object_to_goal_dist_end":0.05369,"object_to_goal_dist_start":0.16922,"object_z_max":0.15711,"peak_contact_force":0.0,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7297.0,"raw_peak_contact_force":0.29613,"subtask_id":"transport_arc","tcp_end":[0.58934,0.16273,0.15901],"tcp_start":[0.51336,0.02952,0.16018],"tcp_to_object_dist_end":0.1055,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":925.0,"n_steps_budget":1000.0,"object_pos_end":[0.60596,0.19097,0.01602],"object_pos_start":[0.60197,0.17261,0.05474],"object_to_goal_dist_end":0.09301,"object_to_goal_dist_start":0.05369,"object_z_max":0.05474,"peak_contact_force":0.12263,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7157.0,"raw_peak_contact_force":1.58808,"subtask_id":"release_1","tcp_end":[0.59644,0.17654,0.11126],"tcp_start":[0.58934,0.16273,0.15901],"tcp_to_object_dist_end":0.09679,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60596,0.19097,0.01602],"object_pos_start":[0.60596,0.19097,0.01602],"object_to_goal_dist_end":0.09301,"object_to_goal_dist_start":0.09301,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1019.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58967,0.17438,0.13196],"tcp_start":[0.59644,0.17654,0.11126],"tcp_to_object_dist_end":0.11824,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.8503,"average_solve_count":167.0,"average_success_count":167.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.18101,"lift_1.lift_height":0.1843,"place_descend.place_z_offset":-0.00568,"transport_arc.arc_height":0.49516,"transport_arc.transport_height":0.06198},"optimized_scores":{"best_composite_score":0.15073,"best_fitness_score":0.55073,"best_task_score":0.1581},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1960.0,"contact_point_centroid":[0.5161,0.05462,-0.00259],"force_p95":0.21898,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.87833,"mean_force":0.14899,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.54079,0.09739,0.28414]},{"body_a":"world","body_b":"grasp_target","contact_count":73.0,"contact_point_centroid":[0.50129,-0.01523,-0.00135],"force_p95":0.48666,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.50815,"mean_force":0.11888,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48985,-0.01534,0.04001]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7462.0,"contact_point_centroid":[0.49033,0.00363,0.11296],"force_p95":0.11242,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30097,"mean_force":0.07265,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4875,-0.0153,0.11069]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8007.0,"contact_point_centroid":[0.49035,-0.03413,0.11038],"force_p95":0.10888,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29092,"mean_force":0.06868,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48749,-0.0153,0.10866]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1124.0,"contact_point_centroid":[0.49778,0.0142,0.21386],"force_p95":0.18381,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27363,"mean_force":0.10343,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.49148,-0.00419,0.21495]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1067.0,"contact_point_centroid":[0.49723,-0.02383,0.21299],"force_p95":0.1956,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25068,"mean_force":0.10729,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.49102,-0.0054,0.2137]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50381,-0.01562,-0.00203],"force_p95":0.13269,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16625,"mean_force":0.12556,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49225,-0.01537,0.03999]},{"body_a":"world","body_b":"grasp_target","contact_count":552.0,"contact_point_centroid":[0.50382,-0.01567,-0.00177],"force_p95":0.13794,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12351,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49998,-0.00532,0.26651]},{"body_a":"world","body_b":"grasp_target","contact_count":3728.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49836,-0.0135,0.13282]},{"body_a":"world","body_b":"grasp_target","contact_count":1696.0,"contact_point_centroid":[0.51597,0.05459,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.58048,0.17992,0.2613]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.51597,0.05459,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58025,0.1846,0.23765]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5086.0,"contact_point_centroid":[0.49096,0.00389,0.04188],"force_p95":0.06587,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09468,"mean_force":0.04292,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49109,-0.01536,0.03874]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5373.0,"contact_point_centroid":[0.49084,-0.0346,0.0414],"force_p95":0.06414,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08336,"mean_force":0.04113,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49109,-0.01536,0.03875]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1909.0,"contact_point_centroid":[0.54416,0.10337,0.28941],"force_p95":0.01159,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01653,"mean_force":0.01057,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.54378,0.10337,0.28712]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1801.0,"contact_point_centroid":[0.58093,0.17994,0.26343],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01288,"mean_force":0.01049,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.58048,0.17993,0.26124]},{"body_a":"left_finger","body_b":"right_finger","contact_count":224.0,"contact_point_centroid":[0.58303,0.18542,0.23581],"force_p95":0.01092,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01094,"mean_force":0.00997,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58233,0.18541,0.23372]}],"total_contact_groups":16},"final_pose_error":0.00702,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.51597,0.05459,0.01602],"final_tcp_position":[0.58344,0.18577,0.23657],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":1.87833,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":139.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":552.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50051,-0.01141,0.22979],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.20384,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":932.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3728.0,"raw_peak_contact_force":0.12264,"subtask_id":"descend_1","tcp_end":[0.49898,-0.01546,0.04724],"tcp_start":[0.50051,-0.01141,0.22979],"tcp_to_object_dist_end":0.02177,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50372,-0.0154,0.02586],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.3122,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13165,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12259.0,"raw_peak_contact_force":0.16625,"subtask_id":"grasp_1","tcp_end":[0.49106,-0.01536,0.03871],"tcp_start":[0.49898,-0.01546,0.04724],"tcp_to_object_dist_end":0.01804,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":519.0,"n_steps_budget":1000.0,"object_pos_end":[0.50445,-0.01533,0.18348],"object_pos_start":[0.50372,-0.0154,0.02586],"object_to_goal_dist_end":0.22825,"object_to_goal_dist_start":0.3122,"object_z_max":0.18321,"peak_contact_force":0.108,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":15542.0,"raw_peak_contact_force":0.50815,"tcp_end":[0.48781,-0.01529,0.20331],"tcp_start":[0.49106,-0.01536,0.03871],"tcp_to_object_dist_end":0.02589,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":707.0,"n_steps_budget":1000.0,"object_pos_end":[0.51597,0.05459,0.01602],"object_pos_start":[0.50445,-0.01533,0.18348],"object_to_goal_dist_end":0.27668,"object_to_goal_dist_start":0.22825,"object_z_max":0.20391,"peak_contact_force":0.12263,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":6060.0,"raw_peak_contact_force":1.87833,"subtask_id":"transport_arc","tcp_end":[0.57771,0.17176,0.30231],"tcp_start":[0.48781,-0.01529,0.20331],"tcp_to_object_dist_end":0.31544,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":424.0,"n_steps_budget":1000.0,"object_pos_end":[0.51597,0.05459,0.01602],"object_pos_start":[0.51597,0.05459,0.01602],"object_to_goal_dist_end":0.27668,"object_to_goal_dist_start":0.27668,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3497.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.58344,0.18577,0.23657],"tcp_start":[0.57771,0.17176,0.30231],"tcp_to_object_dist_end":0.26534,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51597,0.05459,0.01602],"object_pos_start":[0.51597,0.05459,0.01602],"object_to_goal_dist_end":0.27668,"object_to_goal_dist_start":0.27668,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1024.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57909,0.18413,0.2574],"tcp_start":[0.58344,0.18577,0.23657],"tcp_to_object_dist_end":0.28112,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```