## Search State

- **Seed**: 4
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | 0.1862 | 0.32 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | 6 | 0.2135 | 0.31 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | 4 | 0.3107 | 0.31 | ❌ rejected |
| 5 | approach → descend → grasp → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | time_limit | 1 | 0.3394 | 0.34 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | 3 | 0.3577 | 0.31 | ❌ rejected |

**Proposal policy**: task_score is 0.32 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.186) — your mutation base

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

- **Composite score**: 0.186
- **task_score** (E): 0.317
- **fitness_score**: 0.636  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.450

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1369 |
| descend_1 | 1.00 | 1.00 | 0.1287 |
| grasp_1 | 1.00 | 1.00 | 0.0124 |
| lift_1 | 1.00 | 1.00 | 0.1059 |
| transport_arc | 1.00 | 1.00 | 0.1887 |
| place_descend | 1.00 | 1.00 | 0.0186 |
| release_1 | 1.00 | 1.00 | 0.0153 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.519, 0.004, 0.167) | (0.526, 0.005, 0.030)→(0.526, 0.005, 0.026) | 0.246→0.249 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.519, 0.004, 0.167)→(0.521, 0.005, 0.039) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.521, 0.005, 0.039)→(0.513, 0.005, 0.029) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 41.000 | 0.135 | 0.178 |
| lift_1 | lift | 1.00 / step_budget | (0.513, 0.005, 0.029)→(0.521, 0.005, 0.135) | (0.526, 0.005, 0.026)→(0.539, 0.005, 0.126) | 0.249→0.202 | 1.00 / 23.667 | 524.435 | 0.595 |
| transport_arc | approach | 1.00 / step_budget | (0.521, 0.005, 0.135)→(0.601, 0.159, 0.180) | (0.539, 0.005, 0.126)→(0.578, 0.095, 0.012) | 0.202→0.195 | 1.00 / 6.667 | 0.199 | 1.581 |
| place_descend | descend | 1.00 / step_budget | (0.601, 0.159, 0.180)→(0.608, 0.173, 0.181) | (0.578, 0.095, 0.012)→(0.578, 0.095, 0.016) | 0.195→0.191 | 1.00 / 8.333 | 91001.615 | 0.191 |
| release_1 | release | 1.00 / step_budget | (0.608, 0.173, 0.181)→(0.601, 0.171, 0.167) | (0.578, 0.095, 0.016)→(0.578, 0.095, 0.016) | 0.191→0.191 | 1.00 / 8.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.541
- phase_score: 0.699
- phase_breakdown.descend_1_score: 0.837
- phase_breakdown.transport_arc_score: 0.675
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.approach_1_score: 0.034
- phase_breakdown.release_1_score: 0.621
- grasp_place_fitness: 0.746

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.746
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.541
- **Median Q (composite search score)**: 0.151
- **K-run variance**: 0.0063
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.264


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.68421,"average_solve_count":152.0,"average_success_count":152.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.06569,"descend_1.grasp_z_offset":0.01358,"lift_1.lift_height":0.12542,"place_descend.place_z_offset":0.00323,"release_1.release_duration":1.1668,"transport_arc.arc_height":0.27537},"optimized_scores":{"best_composite_score":0.15076,"best_fitness_score":0.60076,"best_task_score":0.24516},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1317.0,"contact_point_centroid":[0.58906,0.05603,-0.00274],"force_p95":0.37845,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.70123,"mean_force":0.16129,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.60198,0.09634,0.19083]},{"body_a":"world","body_b":"grasp_target","contact_count":80.0,"contact_point_centroid":[0.54168,0.00074,-0.00132],"force_p95":0.56387,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64706,"mean_force":0.11867,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52942,0.00085,0.02724]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5388.0,"contact_point_centroid":[0.5352,-0.01812,0.07493],"force_p95":0.10926,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30314,"mean_force":0.07171,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53217,0.00075,0.07295]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5601.0,"contact_point_centroid":[0.53486,0.0196,0.07371],"force_p95":0.10846,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29498,"mean_force":0.06936,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53207,0.00075,0.07171]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1609.0,"contact_point_centroid":[0.55223,0.03407,0.14909],"force_p95":0.20949,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28173,"mean_force":0.11757,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.54637,0.01549,0.14863]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2124.0,"contact_point_centroid":[0.55292,-0.00148,0.14914],"force_p95":0.17416,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26804,"mean_force":0.1,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.54706,0.01663,0.14979]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54429,0.00099,-0.00203],"force_p95":0.13173,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15791,"mean_force":0.12532,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53175,0.0009,0.02736]},{"body_a":"world","body_b":"grasp_target","contact_count":1468.0,"contact_point_centroid":[0.54431,0.00113,-0.00191],"force_p95":0.13511,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12296,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51668,0.00046,0.20762]},{"body_a":"world","body_b":"grasp_target","contact_count":3552.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53595,0.00097,0.06569]},{"body_a":"world","body_b":"grasp_target","contact_count":3620.0,"contact_point_centroid":[0.58909,0.05617,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.6381,0.15034,0.18245]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.58909,0.05617,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.63778,0.15479,0.17188]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4115.0,"contact_point_centroid":[0.53128,-0.01832,0.02862],"force_p95":0.07606,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11212,"mean_force":0.05173,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53049,0.00088,0.0259]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4878.0,"contact_point_centroid":[0.53125,0.01996,0.02774],"force_p95":0.06805,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09583,"mean_force":0.04477,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53049,0.00088,0.02591]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1137.0,"contact_point_centroid":[0.60825,0.10452,0.19452],"force_p95":0.01274,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01644,"mean_force":0.01074,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.60774,0.10452,0.19229]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3836.0,"contact_point_centroid":[0.63853,0.15035,0.18465],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01286,"mean_force":0.01051,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.63809,0.15033,0.18245]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1921.0,"contact_point_centroid":[0.63835,0.15482,0.17411],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01275,"mean_force":0.01045,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.63777,0.15479,0.17184]}],"total_contact_groups":16},"final_pose_error":0.01082,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.58909,0.05617,0.01602],"final_tcp_position":[0.64319,0.15627,0.18464],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":1573.09317,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":368.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1468.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.53566,0.00095,0.11325],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.08766,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":888.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3552.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.5389,0.00103,0.03565],"tcp_start":[0.53566,0.00095,0.11325],"tcp_to_object_dist_end":0.01104,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54416,0.00074,0.02588],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25052,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.1297,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10793.0,"raw_peak_contact_force":0.15791,"subtask_id":"grasp_1","tcp_end":[0.53046,0.00088,0.02587],"tcp_start":[0.5389,0.00103,0.03565],"tcp_to_object_dist_end":0.0137,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":370.0,"n_steps_budget":810.0,"object_pos_end":[0.55863,0.00066,0.12581],"object_pos_start":[0.54416,0.00074,0.02588],"object_to_goal_dist_end":0.19226,"object_to_goal_dist_start":0.25052,"object_z_max":0.12558,"peak_contact_force":1573.09317,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":11069.0,"raw_peak_contact_force":0.64706,"tcp_end":[0.53866,0.00069,0.1323],"tcp_start":[0.53046,0.00088,0.02587],"tcp_to_object_dist_end":0.021,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":601.0,"n_steps_budget":1000.0,"object_pos_end":[0.58909,0.05617,0.01602],"object_pos_start":[0.55863,0.00066,0.12581],"object_to_goal_dist_end":0.21087,"object_to_goal_dist_start":0.19226,"object_z_max":0.14922,"peak_contact_force":0.12263,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":6187.0,"raw_peak_contact_force":1.70123,"subtask_id":"transport_arc","tcp_end":[0.6348,0.14325,0.18746],"tcp_start":[0.53866,0.00069,0.1323],"tcp_to_object_dist_end":0.19765,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":905.0,"n_steps_budget":1000.0,"object_pos_end":[0.58909,0.05617,0.01602],"object_pos_start":[0.58909,0.05617,0.01602],"object_to_goal_dist_end":0.21087,"object_to_goal_dist_start":0.21087,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7456.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.64319,0.15627,0.18464],"tcp_start":[0.6348,0.14325,0.18746],"tcp_to_object_dist_end":0.20342,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58909,0.05617,0.01602],"object_pos_start":[0.58909,0.05617,0.01602],"object_to_goal_dist_end":0.21087,"object_to_goal_dist_start":0.21087,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":3721.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.63679,0.15452,0.16956],"tcp_start":[0.64319,0.15627,0.18464],"tcp_to_object_dist_end":0.18848,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.65035,"average_solve_count":143.0,"average_success_count":143.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.1519,"descend_1.grasp_z_offset":0.01835,"lift_1.lift_height":0.14003,"place_descend.place_z_offset":0.0021,"release_1.release_duration":1.56238,"transport_arc.arc_height":0.34071},"optimized_scores":{"best_composite_score":0.296,"best_fitness_score":0.746,"best_task_score":0.54064},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":78.0,"contact_point_centroid":[0.60137,0.17079,-0.00667],"force_p95":1.00787,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.14474,"mean_force":0.581,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.58858,0.15969,0.11439]},{"body_a":"world","body_b":"grasp_target","contact_count":80.0,"contact_point_centroid":[0.52811,0.02911,-0.00139],"force_p95":0.47631,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54302,"mean_force":0.10102,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51608,0.02966,0.03483]},{"body_a":"world","body_b":"grasp_target","contact_count":3620.0,"contact_point_centroid":[0.60183,0.17286,-0.00211],"force_p95":0.12339,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.32777,"mean_force":0.12197,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.59179,0.17003,0.10326]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5961.0,"contact_point_centroid":[0.52135,0.04837,0.08356],"force_p95":0.10724,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30075,"mean_force":0.06822,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51865,0.0295,0.08168]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5663.0,"contact_point_centroid":[0.52164,0.01061,0.08652],"force_p95":0.10742,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29884,"mean_force":0.07075,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51888,0.02949,0.08429]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2920.0,"contact_point_centroid":[0.5519,0.05766,0.14413],"force_p95":0.18403,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27926,"mean_force":0.10868,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.54654,0.07619,0.14373]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3637.0,"contact_point_centroid":[0.55383,0.09756,0.14293],"force_p95":0.14846,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27563,"mean_force":0.091,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.54807,0.07939,0.14326]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53053,0.03058,-0.00209],"force_p95":0.15011,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21766,"mean_force":0.13003,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51837,0.02983,0.0348]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4082.0,"contact_point_centroid":[0.51778,0.01055,0.0362],"force_p95":0.07927,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14168,"mean_force":0.05186,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51715,0.02975,0.03341]},{"body_a":"world","body_b":"grasp_target","contact_count":840.0,"contact_point_centroid":[0.5305,0.03079,-0.00185],"force_p95":0.13728,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12321,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51004,0.01176,0.25061]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52261,0.0279,0.106]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.60184,0.17284,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58945,0.17403,0.09092]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4956.0,"contact_point_centroid":[0.51777,0.04887,0.03523],"force_p95":0.07183,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08428,"mean_force":0.04469,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51716,0.02975,0.03342]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3596.0,"contact_point_centroid":[0.59253,0.1705,0.10515],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01619,"mean_force":0.01048,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.59203,0.17048,0.10291]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1938.0,"contact_point_centroid":[0.59009,0.17407,0.09322],"force_p95":0.01095,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01279,"mean_force":0.01036,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58944,0.17403,0.09091]}],"total_contact_groups":15},"final_pose_error":0.0101,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.60184,0.17284,0.01602],"final_tcp_position":[0.59606,0.17606,0.10209],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":1.14474,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":211.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":840.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52193,0.02471,0.19879],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17309,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.52534,0.0303,0.04276],"tcp_start":[0.52193,0.02471,0.19879],"tcp_to_object_dist_end":0.01753,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53041,0.02978,0.02567],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18437,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.1445,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10838.0,"raw_peak_contact_force":0.21766,"subtask_id":"grasp_1","tcp_end":[0.51712,0.02975,0.03338],"tcp_start":[0.52534,0.0303,0.04276],"tcp_to_object_dist_end":0.01536,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":384.0,"n_steps_budget":840.0,"object_pos_end":[0.54295,0.02967,0.13317],"object_pos_start":[0.53041,0.02978,0.02567],"object_to_goal_dist_end":0.16197,"object_to_goal_dist_start":0.18437,"object_z_max":0.13292,"peak_contact_force":0.10187,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":11704.0,"raw_peak_contact_force":0.54302,"tcp_end":[0.5252,0.02951,0.1466],"tcp_start":[0.51712,0.02975,0.03338],"tcp_to_object_dist_end":0.02226,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":411.0,"n_steps_budget":1000.0,"object_pos_end":[0.60234,0.1704,0.00297],"object_pos_start":[0.54295,0.02967,0.13317],"object_to_goal_dist_end":0.10544,"object_to_goal_dist_start":0.16197,"object_z_max":0.13339,"peak_contact_force":0.35252,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":6635.0,"raw_peak_contact_force":1.14474,"subtask_id":"transport_arc","tcp_end":[0.59018,0.16294,0.11182],"tcp_start":[0.5252,0.02951,0.1466],"tcp_to_object_dist_end":0.10978,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":905.0,"n_steps_budget":1000.0,"object_pos_end":[0.60184,0.17284,0.01602],"object_pos_start":[0.60234,0.1704,0.00297],"object_to_goal_dist_end":0.09225,"object_to_goal_dist_start":0.10544,"object_z_max":0.0165,"peak_contact_force":0.12263,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7216.0,"raw_peak_contact_force":0.32777,"tcp_end":[0.59606,0.17606,0.10209],"tcp_start":[0.59018,0.16294,0.11182],"tcp_to_object_dist_end":0.08632,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60184,0.17284,0.01602],"object_pos_start":[0.60184,0.17284,0.01602],"object_to_goal_dist_end":0.09225,"object_to_goal_dist_start":0.09225,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":3738.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.58824,0.17366,0.0889],"tcp_start":[0.59606,0.17606,0.10209],"tcp_to_object_dist_end":0.07414,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.77707,"average_solve_count":157.0,"average_success_count":157.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.13986,"descend_1.grasp_z_offset":0.01044,"lift_1.lift_height":0.11902,"place_descend.place_z_offset":0.01827,"release_1.release_duration":1.70569,"transport_arc.arc_height":0.49073},"optimized_scores":{"best_composite_score":0.11188,"best_fitness_score":0.56188,"best_task_score":0.16568},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1588.0,"contact_point_centroid":[0.54375,0.05725,-0.00259],"force_p95":0.29749,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.89598,"mean_force":0.15512,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.55143,0.11252,0.22488]},{"body_a":"world","body_b":"grasp_target","contact_count":74.0,"contact_point_centroid":[0.50159,-0.01532,-0.00135],"force_p95":0.53737,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5962,"mean_force":0.1262,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48989,-0.01537,0.02994]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4953.0,"contact_point_centroid":[0.49449,0.00374,0.07458],"force_p95":0.10645,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30662,"mean_force":0.06732,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49245,-0.01528,0.07211]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2689.0,"contact_point_centroid":[0.51085,-0.01122,0.15293],"force_p95":0.17471,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30248,"mean_force":0.09838,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.50522,0.00728,0.15236]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5450.0,"contact_point_centroid":[0.49445,-0.03417,0.07265],"force_p95":0.10285,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28441,"mean_force":0.0623,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49233,-0.01528,0.07095]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2784.0,"contact_point_centroid":[0.51183,0.02801,0.1552],"force_p95":0.15196,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27027,"mean_force":0.09753,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.50615,0.00957,0.15486]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50381,-0.01554,-0.00203],"force_p95":0.1322,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15794,"mean_force":0.12538,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49206,-0.01541,0.02993]},{"body_a":"world","body_b":"grasp_target","contact_count":844.0,"contact_point_centroid":[0.50382,-0.01567,-0.00185],"force_p95":0.13728,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12321,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49972,-0.00598,0.24637]},{"body_a":"world","body_b":"grasp_target","contact_count":3240.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49812,-0.0141,0.10798]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.54356,0.0572,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.57961,0.17892,0.24545]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54356,0.0572,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57957,0.18421,0.24583]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4112.0,"contact_point_centroid":[0.49133,0.00381,0.03145],"force_p95":0.0761,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11596,"mean_force":0.05177,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49088,-0.01539,0.02869]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4884.0,"contact_point_centroid":[0.4914,-0.03447,0.03053],"force_p95":0.06831,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0911,"mean_force":0.04474,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49088,-0.01539,0.02869]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1453.0,"contact_point_centroid":[0.5554,0.12057,0.23065],"force_p95":0.01188,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01528,"mean_force":0.01058,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.55504,0.12057,0.22831]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4296.0,"contact_point_centroid":[0.58023,0.17894,0.24759],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01278,"mean_force":0.01039,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.57961,0.17893,0.24546]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1920.0,"contact_point_centroid":[0.58011,0.18424,0.24798],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01272,"mean_force":0.01045,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57957,0.18421,0.24583]}],"total_contact_groups":16},"final_pose_error":0.01022,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.54356,0.0572,0.01602],"final_tcp_position":[0.58362,0.18563,0.25688],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":273004.60093,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":212.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":844.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50036,-0.01262,0.18931],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16336,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":810.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3240.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.49887,-0.01549,0.03714],"tcp_start":[0.50036,-0.01262,0.18931],"tcp_to_object_dist_end":0.01217,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50369,-0.01525,0.02588],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.3121,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12997,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10796.0,"raw_peak_contact_force":0.15794,"subtask_id":"grasp_1","tcp_end":[0.49085,-0.01539,0.02865],"tcp_start":[0.49887,-0.01549,0.03714],"tcp_to_object_dist_end":0.01313,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":319.0,"n_steps_budget":750.0,"object_pos_end":[0.51685,-0.01518,0.11884],"object_pos_start":[0.50369,-0.01525,0.02588],"object_to_goal_dist_end":0.25035,"object_to_goal_dist_start":0.3121,"object_z_max":0.11859,"peak_contact_force":0.1089,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":10477.0,"raw_peak_contact_force":0.5962,"tcp_end":[0.49826,-0.0152,0.12588],"tcp_start":[0.49085,-0.01539,0.02865],"tcp_to_object_dist_end":0.01988,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":743.0,"n_steps_budget":1000.0,"object_pos_end":[0.54356,0.0572,0.01602],"object_pos_start":[0.51685,-0.01518,0.11884],"object_to_goal_dist_end":0.26965,"object_to_goal_dist_start":0.25035,"object_z_max":0.16416,"peak_contact_force":0.12263,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8514.0,"raw_peak_contact_force":1.89598,"subtask_id":"transport_arc","tcp_end":[0.57794,0.17215,0.2395],"tcp_start":[0.49826,-0.0152,0.12588],"tcp_to_object_dist_end":0.25365,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54356,0.0572,0.01602],"object_pos_start":[0.54356,0.0572,0.01602],"object_to_goal_dist_end":0.26965,"object_to_goal_dist_start":0.26965,"object_z_max":0.01602,"peak_contact_force":273004.60093,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8296.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58362,0.18563,0.25688],"tcp_start":[0.57794,0.17215,0.2395],"tcp_to_object_dist_end":0.27588,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54356,0.0572,0.01602],"object_pos_start":[0.54356,0.0572,0.01602],"object_to_goal_dist_end":0.26965,"object_to_goal_dist_start":0.26965,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":3720.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.57882,0.18394,0.24381],"tcp_start":[0.58362,0.18563,0.25688],"tcp_to_object_dist_end":0.26305,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```