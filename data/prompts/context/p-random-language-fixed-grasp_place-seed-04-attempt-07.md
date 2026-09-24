## Search State

- **Seed**: 4
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.1431 | 0.34 | ✅ accepted |
| 6 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.1776 | 0.31 | ✅ accepted |
| 5 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.0835 | 0.22 | ✅ accepted |
| 4 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.1679 | 0.30 | ✅ accepted |
| 3 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.2603 | 0.32 | ✅ accepted |

**Proposal policy**: task_score is 0.34 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.143) — your mutation base

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
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    grasp_z_offset:
      type: scalar
      range:
      - 0.0
      - 0.05
      default: 0.02
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: descend_1
- id: grasp_1
  type: grasp
  control: impedance_control
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
      - 0.1
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
- id: transport_arc
  type: approach
  generator: arc_cartesian
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
  parameters:
    arc_height:
      type: scalar
      range:
      - 0.1
      - 0.3
      default: 0.2
      binds_to:
      - path: generator.arc_height
        mode: replace
    transport_speed:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.3
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: transport_arc
- id: descend_to_place
  type: descend
  generator: linear_cartesian
  control: admittance_control
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
  parameters:
    place_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
    place_z_offset:
      type: scalar
      range:
      - -0.03
      - 0.03
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: release_1
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
  subtask_id: release_1

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.02], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - grasp_z_offset: status=consumed; consumers=target.offset.z (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **lift_1** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
- **transport_arc** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_speed: status=consumed; consumers=generator.speed (replace)
    - place_z_offset: status=consumed; consumers=target.offset.z (replace)
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.143
- **task_score** (E): 0.342
- **fitness_score**: 0.643  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.500

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0723 |
| descend_1 | 1.00 | 1.00 | 0.1875 |
| grasp_1 | 1.00 | 1.00 | 0.0134 |
| lift_1 | 1.00 | 1.00 | 0.1256 |
| transport_arc | 1.00 | 1.00 | 0.1900 |
| descend_to_place | 1.00 | 1.00 | 0.0071 |
| release_1 | 1.00 | 1.00 | 0.0208 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.517, 0.003, 0.234) | (0.526, 0.005, 0.030)→(0.526, 0.005, 0.026) | 0.246→0.249 | 1.00 / 4.000 | 0.122 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.517, 0.003, 0.234)→(0.521, 0.005, 0.047) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.521, 0.005, 0.047)→(0.512, 0.005, 0.037) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 43.000 | 0.145 | 0.198 |
| lift_1 | lift | 1.00 / step_budget | (0.512, 0.005, 0.037)→(0.509, 0.005, 0.162) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.145) | 0.249→0.203 | 1.00 / 22.667 | 0.111 | 0.528 |
| transport_arc | approach | 1.00 / step_budget | (0.509, 0.005, 0.162)→(0.601, 0.160, 0.185) | (0.526, 0.005, 0.145)→(0.573, 0.113, 0.041) | 0.203→0.160 | 1.00 / 14.667 | 0.118 | 1.471 |
| descend_to_place | descend | 1.00 / step_budget | (0.601, 0.160, 0.185)→(0.601, 0.163, 0.178) | (0.573, 0.113, 0.041)→(0.573, 0.113, 0.040) | 0.160→0.161 | 1.00 / 15.000 | 182630.705 | 0.252 |
| release_1 | release | 1.00 / step_budget | (0.601, 0.163, 0.178)→(0.596, 0.161, 0.198) | (0.573, 0.113, 0.040)→(0.573, 0.114, 0.020) | 0.161→0.180 | 1.00 / 3.333 | 0.175 | 0.434 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.581
- phase_score: 0.683
- phase_breakdown.release_1_score: 0.506
- phase_breakdown.approach_1_score: 0.006
- phase_breakdown.descend_1_score: 0.867
- phase_breakdown.transport_arc_score: 0.673
- phase_breakdown.grasp_1_score: 1.000
- grasp_place_fitness: 0.763

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.763
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.581
- **Median Q (composite search score)**: 0.108
- **K-run variance**: 0.0076
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.394


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.776,"average_solve_count":125.0,"average_success_count":125.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.11808,"descend_1.grasp_z_offset":0.00211,"descend_to_place.place_speed":0.2395,"descend_to_place.place_z_offset":-0.00906,"lift_1.lift_height":0.1096,"transport_arc.arc_height":0.25951,"transport_arc.transport_speed":0.23659},"optimized_scores":{"best_composite_score":0.10785,"best_fitness_score":0.60785,"best_task_score":0.27269},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":663.0,"contact_point_centroid":[0.58956,0.08891,-0.00403],"force_p95":0.90255,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.85014,"mean_force":0.23874,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.6095,0.11216,0.19444]},{"body_a":"world","body_b":"grasp_target","contact_count":76.0,"contact_point_centroid":[0.54158,0.00077,-0.00135],"force_p95":0.4993,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5318,"mean_force":0.11387,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52799,0.00082,0.03748]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4282.0,"contact_point_centroid":[0.52853,-0.0181,0.07825],"force_p95":0.111,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3248,"mean_force":0.07448,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52546,0.00078,0.07595]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2537.0,"contact_point_centroid":[0.54491,0.03967,0.15343],"force_p95":0.13809,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30855,"mean_force":0.08767,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.53893,0.02139,0.15324]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4524.0,"contact_point_centroid":[0.5286,0.01958,0.07631],"force_p95":0.1095,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30466,"mean_force":0.07152,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52551,0.00078,0.07438]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2053.0,"contact_point_centroid":[0.54393,0.00196,0.15335],"force_p95":0.1806,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27974,"mean_force":0.10324,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.53828,0.02055,0.15247]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5443,0.00102,-0.00203],"force_p95":0.13248,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1546,"mean_force":0.12545,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53052,0.00087,0.03766]},{"body_a":"world","body_b":"grasp_target","contact_count":1088.0,"contact_point_centroid":[0.54431,0.00113,-0.00188],"force_p95":0.1365,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12308,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51607,0.00044,0.23376]},{"body_a":"world","body_b":"grasp_target","contact_count":80.0,"contact_point_centroid":[0.58811,0.09649,-0.00198],"force_p95":0.12507,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12523,"mean_force":0.12278,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.6342,0.14504,0.18602]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.58811,0.09648,-0.00199],"force_p95":0.12276,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12363,"mean_force":0.12264,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.63092,0.14544,0.18354]},{"body_a":"world","body_b":"grasp_target","contact_count":884.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53545,0.00095,0.10664]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4115.0,"contact_point_centroid":[0.53052,-0.01835,0.03893],"force_p95":0.07626,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12071,"mean_force":0.05179,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52931,0.00085,0.03626]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4878.0,"contact_point_centroid":[0.53043,0.01993,0.03805],"force_p95":0.06833,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09504,"mean_force":0.04473,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52931,0.00085,0.03626]},{"body_a":"left_finger","body_b":"right_finger","contact_count":728.0,"contact_point_centroid":[0.61235,0.11542,0.19749],"force_p95":0.01325,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01629,"mean_force":0.01093,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.61206,0.11541,0.19517]},{"body_a":"left_finger","body_b":"right_finger","contact_count":84.0,"contact_point_centroid":[0.63449,0.14504,0.18811],"force_p95":0.01103,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01104,"mean_force":0.01064,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.63419,0.14503,0.18604]},{"body_a":"left_finger","body_b":"right_finger","contact_count":223.0,"contact_point_centroid":[0.6341,0.14628,0.18206],"force_p95":0.01092,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01094,"mean_force":0.01002,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.63355,0.14627,0.18021]}],"total_contact_groups":16},"final_pose_error":0.01726,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.58811,0.09648,0.01602],"final_tcp_position":[0.63518,0.1463,0.18406],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":272976.39206,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":273.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1088.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.53445,0.00091,0.16537],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1397,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":221.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":884.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53825,0.00101,0.04702],"tcp_start":[0.53445,0.00091,0.16537],"tcp_to_object_dist_end":0.02185,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54419,0.00074,0.02587],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25051,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.13061,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10793.0,"raw_peak_contact_force":0.1546,"subtask_id":"grasp_1","tcp_end":[0.52928,0.00085,0.03622],"tcp_start":[0.53825,0.00101,0.04702],"tcp_to_object_dist_end":0.01815,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":301.0,"n_steps_budget":690.0,"object_pos_end":[0.5424,0.00085,0.11153],"object_pos_start":[0.54419,0.00074,0.02587],"object_to_goal_dist_end":0.20524,"object_to_goal_dist_start":0.25051,"object_z_max":0.11128,"peak_contact_force":0.10733,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":8882.0,"raw_peak_contact_force":0.5318,"tcp_end":[0.5252,0.00078,0.12646],"tcp_start":[0.52928,0.00085,0.03622],"tcp_to_object_dist_end":0.02278,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":537.0,"n_steps_budget":1000.0,"object_pos_end":[0.58811,0.09645,0.01605],"object_pos_start":[0.5424,0.00085,0.11153],"object_to_goal_dist_end":0.19489,"object_to_goal_dist_start":0.20524,"object_z_max":0.15501,"peak_contact_force":0.1253,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5981.0,"raw_peak_contact_force":1.85014,"subtask_id":"transport_arc","tcp_end":[0.63419,0.14399,0.18782],"tcp_start":[0.5252,0.00078,0.12646],"tcp_to_object_dist_end":0.18408,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":20.0,"n_steps_budget":1000.0,"object_pos_end":[0.58812,0.09643,0.01603],"object_pos_start":[0.58811,0.09645,0.01605],"object_to_goal_dist_end":0.19492,"object_to_goal_dist_start":0.19489,"object_z_max":0.01605,"peak_contact_force":272976.39206,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":164.0,"raw_peak_contact_force":0.12523,"subtask_id":"release_1","tcp_end":[0.63518,0.1463,0.18406],"tcp_start":[0.63419,0.14399,0.18782],"tcp_to_object_dist_end":0.18148,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58811,0.09648,0.01602],"object_pos_start":[0.58812,0.09643,0.01603],"object_to_goal_dist_end":0.19491,"object_to_goal_dist_start":0.19492,"object_z_max":0.01603,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1023.0,"raw_peak_contact_force":0.12363,"subtask_id":"release_1","tcp_end":[0.62939,0.14498,0.20284],"tcp_start":[0.63518,0.1463,0.18406],"tcp_to_object_dist_end":0.19738,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.66207,"average_solve_count":145.0,"average_success_count":145.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.24557,"descend_1.grasp_z_offset":0.001,"descend_to_place.place_speed":0.155,"descend_to_place.place_z_offset":-0.00026,"lift_1.lift_height":0.15539,"transport_arc.arc_height":0.24229,"transport_arc.transport_speed":0.40566},"optimized_scores":{"best_composite_score":0.26308,"best_fitness_score":0.76308,"best_task_score":0.5807},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":180.0,"contact_point_centroid":[0.58611,0.17559,-0.00611],"force_p95":0.90815,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.05458,"mean_force":0.37372,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58373,0.16545,0.12079]},{"body_a":"world","body_b":"grasp_target","contact_count":83.0,"contact_point_centroid":[0.52747,0.02808,-0.00147],"force_p95":0.53032,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54642,"mean_force":0.11582,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51492,0.02866,0.03692]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":293.0,"contact_point_centroid":[0.595,0.18507,0.11655],"force_p95":0.16857,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.5072,"mean_force":0.08594,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59007,0.16624,0.11559]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":289.0,"contact_point_centroid":[0.59454,0.14743,0.11579],"force_p95":0.13631,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.50076,"mean_force":0.08564,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59007,0.16621,0.11569]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4487.0,"contact_point_centroid":[0.55788,0.07991,0.16194],"force_p95":0.13415,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.48666,"mean_force":0.0897,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.55208,0.09858,0.16054]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4825.0,"contact_point_centroid":[0.55967,0.11997,0.16122],"force_p95":0.11765,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.40395,"mean_force":0.08326,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.55374,0.10148,0.16005]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":761.0,"contact_point_centroid":[0.59444,0.14817,0.11023],"force_p95":0.09934,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34882,"mean_force":0.06925,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58827,0.16696,0.10924]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":966.0,"contact_point_centroid":[0.59378,0.18589,0.11041],"force_p95":0.1163,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33762,"mean_force":0.06159,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58823,0.16694,0.10919]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6131.0,"contact_point_centroid":[0.51587,0.00966,0.09832],"force_p95":0.11256,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31983,"mean_force":0.07581,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51247,0.0285,0.09608]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6516.0,"contact_point_centroid":[0.51577,0.04731,0.09507],"force_p95":0.11191,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31849,"mean_force":0.07292,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5125,0.0285,0.0932]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53058,0.03048,-0.00218],"force_p95":0.17426,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24609,"mean_force":0.13602,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51748,0.02884,0.03672]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3763.0,"contact_point_centroid":[0.51776,0.00956,0.03837],"force_p95":0.08647,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15412,"mean_force":0.0557,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51629,0.02876,0.03539]},{"body_a":"world","body_b":"grasp_target","contact_count":316.0,"contact_point_centroid":[0.5305,0.03079,-0.0016],"force_p95":0.13825,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12436,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50734,0.0082,0.29135]},{"body_a":"world","body_b":"grasp_target","contact_count":1760.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12259,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51991,0.02364,0.16355]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4962.0,"contact_point_centroid":[0.51729,0.04791,0.03722],"force_p95":0.0768,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08164,"mean_force":0.04521,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5163,0.02876,0.0354]}],"total_contact_groups":15},"final_pose_error":0.01663,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.5957,0.16951,0.02728],"final_tcp_position":[0.59056,0.1673,0.11323],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":1903.19204,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":80.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02596],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18339,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12218,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":316.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.51638,0.01814,0.28116],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.25591,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":440.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02596],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18339,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1760.0,"raw_peak_contact_force":0.12264,"subtask_id":"descend_1","tcp_end":[0.52506,0.0293,0.04564],"tcp_start":[0.51638,0.01814,0.28116],"tcp_to_object_dist_end":0.02042,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53045,0.02904,0.02541],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18507,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.16304,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10525.0,"raw_peak_contact_force":0.24609,"subtask_id":"grasp_1","tcp_end":[0.51626,0.02876,0.03536],"tcp_start":[0.52506,0.0293,0.04564],"tcp_to_object_dist_end":0.01733,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":445.0,"n_steps_budget":990.0,"object_pos_end":[0.52995,0.02886,0.15432],"object_pos_start":[0.53045,0.02904,0.02541],"object_to_goal_dist_end":0.17227,"object_to_goal_dist_start":0.18507,"object_z_max":0.15406,"peak_contact_force":0.11308,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":12730.0,"raw_peak_contact_force":0.54642,"tcp_end":[0.51263,0.02851,0.17119],"tcp_start":[0.51626,0.02876,0.03536],"tcp_to_object_dist_end":0.02418,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":393.0,"n_steps_budget":1000.0,"object_pos_end":[0.59527,0.16521,0.09185],"object_pos_start":[0.52995,0.02886,0.15432],"object_to_goal_dist_end":0.02195,"object_to_goal_dist_start":0.17227,"object_z_max":0.15479,"peak_contact_force":0.10535,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9312.0,"raw_peak_contact_force":0.48666,"subtask_id":"transport_arc","tcp_end":[0.59087,0.16548,0.11837],"tcp_start":[0.51263,0.02851,0.17119],"tcp_to_object_dist_end":0.02688,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":20.0,"n_steps_budget":1000.0,"object_pos_end":[0.59615,0.16749,0.08672],"object_pos_start":[0.59527,0.16521,0.09185],"object_to_goal_dist_end":0.02467,"object_to_goal_dist_start":0.02195,"object_z_max":0.09185,"peak_contact_force":1903.19204,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":582.0,"raw_peak_contact_force":0.5072,"subtask_id":"release_1","tcp_end":[0.59056,0.1673,0.11323],"tcp_start":[0.59087,0.16548,0.11837],"tcp_to_object_dist_end":0.02709,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5957,0.16951,0.02728],"object_pos_start":[0.59615,0.16749,0.08672],"object_to_goal_dist_end":0.08153,"object_to_goal_dist_start":0.02467,"object_z_max":0.08672,"peak_contact_force":0.27834,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1907.0,"raw_peak_contact_force":1.05458,"subtask_id":"release_1","tcp_end":[0.58356,0.1654,0.13381],"tcp_start":[0.59056,0.1673,0.11323],"tcp_to_object_dist_end":0.1073,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.8169,"average_solve_count":142.0,"average_success_count":142.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.20768,"descend_1.grasp_z_offset":0.0029,"descend_to_place.place_speed":0.15015,"descend_to_place.place_z_offset":-0.02407,"lift_1.lift_height":0.16994,"transport_arc.arc_height":0.29948,"transport_arc.transport_speed":0.36899},"optimized_scores":{"best_composite_score":0.05845,"best_fitness_score":0.55845,"best_task_score":0.17381},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1144.0,"contact_point_centroid":[0.53626,0.07543,-0.00312],"force_p95":0.50306,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.07542,"mean_force":0.17627,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.54854,0.11296,0.25628]},{"body_a":"world","body_b":"grasp_target","contact_count":74.0,"contact_point_centroid":[0.50109,-0.01482,-0.00139],"force_p95":0.48636,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.50688,"mean_force":0.11797,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48989,-0.01489,0.0401]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6948.0,"contact_point_centroid":[0.49011,0.00411,0.10667],"force_p95":0.1113,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29914,"mean_force":0.07143,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48754,-0.01485,0.10435]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1501.0,"contact_point_centroid":[0.50074,0.02071,0.20763],"force_p95":0.1713,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29613,"mean_force":0.09821,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.49451,0.00219,0.20769]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7559.0,"contact_point_centroid":[0.49014,-0.03371,0.10468],"force_p95":0.10749,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29342,"mean_force":0.06691,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48753,-0.01485,0.10295]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1504.0,"contact_point_centroid":[0.50042,-0.01673,0.20718],"force_p95":0.17712,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27379,"mean_force":0.09839,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.49429,0.00169,0.20722]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50383,-0.01558,-0.00207],"force_p95":0.14241,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1921,"mean_force":0.12806,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49228,-0.01492,0.03999]},{"body_a":"world","body_b":"grasp_target","contact_count":368.0,"contact_point_centroid":[0.50382,-0.01567,-0.00166],"force_p95":0.13823,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12404,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50005,-0.00442,0.27992]},{"body_a":"world","body_b":"grasp_target","contact_count":1564.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12261,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49916,-0.01236,0.1523]},{"body_a":"world","body_b":"grasp_target","contact_count":120.0,"contact_point_centroid":[0.53606,0.07594,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.5771,0.17243,0.24325]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.53606,0.07594,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57506,0.17442,0.23766]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5069.0,"contact_point_centroid":[0.491,0.00435,0.04188],"force_p95":0.06736,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10094,"mean_force":0.04295,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49115,-0.01491,0.03879]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5411.0,"contact_point_centroid":[0.49087,-0.03416,0.04138],"force_p95":0.06587,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07682,"mean_force":0.04113,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49115,-0.01491,0.0388]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1058.0,"contact_point_centroid":[0.55283,0.12074,0.25937],"force_p95":0.013,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01543,"mean_force":0.01071,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.5524,0.12073,0.25704]},{"body_a":"left_finger","body_b":"right_finger","contact_count":129.0,"contact_point_centroid":[0.5773,0.17243,0.24531],"force_p95":0.01089,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01263,"mean_force":0.01037,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57709,0.17242,0.24328]},{"body_a":"left_finger","body_b":"right_finger","contact_count":224.0,"contact_point_centroid":[0.57769,0.17528,0.23565],"force_p95":0.01089,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01089,"mean_force":0.00996,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57704,0.17527,0.23324]}],"total_contact_groups":16},"final_pose_error":0.01983,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.53606,0.07594,0.01602],"final_tcp_position":[0.57865,0.17532,0.23739],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":273012.53236,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":93.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.026],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31225,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12213,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":368.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50039,-0.00981,0.25624],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.23033,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":391.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.026],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31225,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1564.0,"raw_peak_contact_force":0.12264,"subtask_id":"descend_1","tcp_end":[0.49961,-0.01499,0.04811],"tcp_start":[0.50039,-0.00981,0.25624],"tcp_to_object_dist_end":0.0225,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50373,-0.01507,0.02574],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31206,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13993,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12280.0,"raw_peak_contact_force":0.1921,"subtask_id":"grasp_1","tcp_end":[0.49112,-0.0149,0.03876],"tcp_start":[0.49961,-0.01499,0.04811],"tcp_to_object_dist_end":0.01812,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":474.0,"n_steps_budget":1000.0,"object_pos_end":[0.50434,-0.01486,0.17007],"object_pos_start":[0.50373,-0.01507,0.02574],"object_to_goal_dist_end":0.23203,"object_to_goal_dist_start":0.31206,"object_z_max":0.1698,"peak_contact_force":0.11198,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":14581.0,"raw_peak_contact_force":0.50688,"tcp_end":[0.48776,-0.01484,0.18923],"tcp_start":[0.49112,-0.0149,0.03876],"tcp_to_object_dist_end":0.02534,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":544.0,"n_steps_budget":1000.0,"object_pos_end":[0.53606,0.07594,0.01602],"object_pos_start":[0.50434,-0.01486,0.17007],"object_to_goal_dist_end":0.26247,"object_to_goal_dist_start":0.23203,"object_z_max":0.2031,"peak_contact_force":0.12263,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5207.0,"raw_peak_contact_force":2.07542,"subtask_id":"transport_arc","tcp_end":[0.57674,0.17032,0.24736],"tcp_start":[0.48776,-0.01484,0.18923],"tcp_to_object_dist_end":0.25314,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":30.0,"n_steps_budget":1000.0,"object_pos_end":[0.53606,0.07594,0.01602],"object_pos_start":[0.53606,0.07594,0.01602],"object_to_goal_dist_end":0.26247,"object_to_goal_dist_start":0.26247,"object_z_max":0.01602,"peak_contact_force":273012.53236,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":249.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.57865,0.17532,0.23739],"tcp_start":[0.57674,0.17032,0.24736],"tcp_to_object_dist_end":0.24637,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53606,0.07594,0.01602],"object_pos_start":[0.53606,0.07594,0.01602],"object_to_goal_dist_end":0.26247,"object_to_goal_dist_start":0.26247,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1024.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.57392,0.17395,0.2576],"tcp_start":[0.57865,0.17532,0.23739],"tcp_to_object_dist_end":0.26344,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```