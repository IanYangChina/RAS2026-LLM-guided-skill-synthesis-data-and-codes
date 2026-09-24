## Search State

- **Seed**: 8
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → descend → contact → lift → approach → descend | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.4211 | 0.24 | ❌ rejected |
| 7 | approach → descend → contact → lift → approach → descend | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.4221 | 0.24 | ❌ rejected |
| 6 | approach → descend → contact → lift → approach → descend | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.4211 | 0.24 | ❌ rejected |
| 5 | approach → descend → contact → lift → approach → descend → release | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | 0.2318 | 0.17 | ❌ rejected |
| 4 | approach → descend → contact → lift → approach → descend | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.4199 | 0.23 | ❌ rejected |

**Proposal policy**: task_score is 0.24 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.421) — your mutation base

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

- **Composite score**: 0.421
- **task_score** (E): 0.236
- **fitness_score**: 0.574  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.167
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.320

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0914 |
| descend_1 | 1.00 | 1.00 | 0.1654 |
| contact_1 | 1.00 | 1.00 | 0.0096 |
| lift_1 | 1.00 | 1.00 | 0.1191 |
| transport_1 | 0.00 | 1.00 | 0.0914 |
| release_1 | 0.33 | 1.00 | 0.1104 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.516, -0.001, 0.220) | (0.522, -0.001, 0.030)→(0.522, -0.001, 0.026) | 0.287→0.289 | 1.00 / 4.000 | 10.930 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.516, -0.001, 0.220)→(0.517, -0.001, 0.054) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 4.000 | 0.123 | 0.123 |
| contact_1 | contact | 1.00 / force_exceeded | (0.517, -0.001, 0.054)→(0.511, -0.001, 0.047) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 44.000 | 0.142 | 0.187 |
| lift_1 | lift | 1.00 / step_budget | (0.511, -0.001, 0.047)→(0.507, -0.001, 0.166) | (0.522, -0.001, 0.026)→(0.518, -0.001, 0.138) | 0.289→0.238 | 1.00 / 23.667 | 0.113 | 0.432 |
| transport_1 | approach | 0.00 / step_budget | (0.507, -0.001, 0.166)→(0.540, 0.072, 0.209) | (0.518, -0.001, 0.138)→(0.545, 0.081, 0.111) | 0.238→0.192 | 1.00 / 13.000 | 0.155 | 0.722 |
| release_1 | descend | 0.33 / step_budget | (0.540, 0.072, 0.209)→(0.585, 0.170, 0.190) | (0.545, 0.081, 0.111)→(0.570, 0.109, 0.016) | 0.192→0.218 | 1.00 / 4.000 | 0.123 | 1.131 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.285
- phase_score: 0.315
- phase_breakdown.approach_1_score: 0.019
- phase_breakdown.descend_1_score: 0.872
- phase_breakdown.transport_arc_score: 0.046
- phase_breakdown.release_1_score: 0.346
- phase_breakdown.grasp_1_score: 1.000
- grasp_place_fitness: 0.599

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.599
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.285
- **Median Q (composite search score)**: 0.411
- **K-run variance**: 0.0003
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.203


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.83333,"average_solve_count":150.0,"average_success_count":150.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.17617,"contact_1.contact_force":7.88548,"lift_1.lift_height":0.13742,"transport_1.transport_speed":0.07562},"optimized_scores":{"best_composite_score":0.40601,"best_fitness_score":0.55934,"best_task_score":0.20702},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":142.0,"contact_point_centroid":[0.52257,0.14806,-0.00858],"force_p95":1.49129,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.83407,"mean_force":0.54201,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51112,0.11893,0.23042]},{"body_a":"world","body_b":"grasp_target","contact_count":135.0,"contact_point_centroid":[0.48011,0.04631,-0.00122],"force_p95":0.27296,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.40178,"mean_force":0.0563,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47157,0.04712,0.05004]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13775.0,"contact_point_centroid":[0.47063,0.0658,0.10569],"force_p95":0.09748,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29768,"mean_force":0.05872,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46915,0.04689,0.10512]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13076.0,"contact_point_centroid":[0.46988,0.0279,0.10463],"force_p95":0.11717,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29607,"mean_force":0.06196,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46912,0.04689,0.10467]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7608.0,"contact_point_centroid":[0.49204,0.06232,0.19485],"force_p95":0.13428,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24677,"mean_force":0.10172,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.48729,0.0806,0.19823]},{"body_a":"world","body_b":"grasp_target","contact_count":1640.0,"contact_point_centroid":[0.48273,0.0486,-0.00213],"force_p95":0.15649,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21259,"mean_force":0.1324,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47361,0.04732,0.0488]},{"body_a":"world","body_b":"grasp_target","contact_count":4600.0,"contact_point_centroid":[0.52153,0.1503,-0.00202],"force_p95":0.12299,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20164,"mean_force":0.1216,"phase_index":5.0,"phase_name":"release_1","phase_type":"descend","tcp_position_centroid":[0.54769,0.17974,0.22332]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8380.0,"contact_point_centroid":[0.49173,0.09726,0.19438],"force_p95":0.13253,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17775,"mean_force":0.0931,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.48644,0.07917,0.19707]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4091.0,"contact_point_centroid":[0.47227,0.02806,0.04915],"force_p95":0.07978,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14676,"mean_force":0.05207,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47302,0.04727,0.04817]},{"body_a":"world","body_b":"grasp_target","contact_count":1208.0,"contact_point_centroid":[0.4827,0.04873,-0.00189],"force_p95":0.13606,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12303,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49048,0.02014,0.25687]},{"body_a":"world","body_b":"grasp_target","contact_count":1996.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47894,0.04478,0.13341]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4988.0,"contact_point_centroid":[0.47312,0.06638,0.0492],"force_p95":0.07307,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07423,"mean_force":0.04411,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47303,0.04727,0.04817]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4259.0,"contact_point_centroid":[0.54543,0.17515,0.22635],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01646,"mean_force":0.01037,"phase_index":5.0,"phase_name":"release_1","phase_type":"descend","tcp_position_centroid":[0.54489,0.17513,0.22412]}],"total_contact_groups":13},"final_pose_error":0.01686,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.52152,0.1503,0.01602],"final_tcp_position":[0.57227,0.21742,0.22264],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":1.83407,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":303.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1208.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.48191,0.04203,0.21335],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.18745,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":499.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1996.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.47839,0.04776,0.05484],"tcp_start":[0.48191,0.04203,0.21335],"tcp_to_object_dist_end":0.02916,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":10.0,"n_steps_budget":600.0,"object_pos_end":[0.48266,0.04765,0.02556],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29098,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.15305,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":10719.0,"raw_peak_contact_force":0.21259,"subtask_id":"grasp_1","tcp_end":[0.473,0.04727,0.04814],"tcp_start":[0.47839,0.04776,0.05484],"tcp_to_object_dist_end":0.02456,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":783.0,"n_steps_budget":870.0,"object_pos_end":[0.47859,0.04781,0.14404],"object_pos_start":[0.48266,0.04765,0.02556],"object_to_goal_dist_end":0.22565,"object_to_goal_dist_start":0.29098,"object_z_max":0.14393,"peak_contact_force":0.13508,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":26986.0,"raw_peak_contact_force":0.40178,"tcp_end":[0.4694,0.04692,0.17397],"tcp_start":[0.473,0.04727,0.04814],"tcp_to_object_dist_end":0.03132,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51714,0.14802,0.00696],"object_pos_start":[0.47859,0.04781,0.14404],"object_to_goal_dist_end":0.24635,"object_to_goal_dist_start":0.22565,"object_z_max":0.18466,"peak_contact_force":0.21578,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":16130.0,"raw_peak_contact_force":1.83407,"subtask_id":"transport_arc","tcp_end":[0.5119,0.12017,0.23147],"tcp_start":[0.4694,0.04692,0.17397],"tcp_to_object_dist_end":0.22629,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52152,0.1503,0.01602],"object_pos_start":[0.51714,0.14802,0.00696],"object_to_goal_dist_end":0.23624,"object_to_goal_dist_start":0.24635,"object_z_max":0.01685,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8859.0,"raw_peak_contact_force":0.20164,"subtask_id":"release_1","tcp_end":[0.56915,0.21615,0.21501],"tcp_start":[0.5119,0.12017,0.23147],"tcp_to_object_dist_end":0.21495,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.82877,"average_solve_count":146.0,"average_success_count":146.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.18203,"contact_1.contact_force":12.36851,"lift_1.lift_height":0.13255,"transport_1.transport_speed":0.07697},"optimized_scores":{"best_composite_score":0.41132,"best_fitness_score":0.56465,"best_task_score":0.21647},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3369.0,"contact_point_centroid":[0.57957,0.10476,-0.00232],"force_p95":0.12654,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.68347,"mean_force":0.13728,"phase_index":5.0,"phase_name":"release_1","phase_type":"descend","tcp_position_centroid":[0.57643,0.14704,0.19948]},{"body_a":"world","body_b":"grasp_target","contact_count":144.0,"contact_point_centroid":[0.53456,-0.02065,-0.00115],"force_p95":0.31942,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.44431,"mean_force":0.06669,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52444,-0.02087,0.04842]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12225.0,"contact_point_centroid":[0.52358,-0.00179,0.10062],"force_p95":0.10199,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2988,"mean_force":0.06291,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52187,-0.02081,0.09971]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13636.0,"contact_point_centroid":[0.52336,-0.03975,0.10058],"force_p95":0.09491,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29428,"mean_force":0.0571,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52187,-0.02081,0.09968]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1785.0,"contact_point_centroid":[0.55896,0.09988,0.19872],"force_p95":0.14046,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24421,"mean_force":0.10862,"phase_index":5.0,"phase_name":"release_1","phase_type":"descend","tcp_position_centroid":[0.55297,0.08165,0.20344]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11072.0,"contact_point_centroid":[0.53934,0.00424,0.18408],"force_p95":0.11437,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16567,"mean_force":0.08228,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53411,0.02257,0.18536]},{"body_a":"world","body_b":"grasp_target","contact_count":1632.0,"contact_point_centroid":[0.53703,-0.02127,-0.00205],"force_p95":0.13558,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16535,"mean_force":0.1266,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52667,-0.02091,0.04745]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10085.0,"contact_point_centroid":[0.53886,0.03948,0.18332],"force_p95":0.13485,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16133,"mean_force":0.08995,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53355,0.02096,0.18449]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1998.0,"contact_point_centroid":[0.559,0.0642,0.19902],"force_p95":0.12233,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14774,"mean_force":0.09584,"phase_index":5.0,"phase_name":"release_1","phase_type":"descend","tcp_position_centroid":[0.55315,0.0822,0.20339]},{"body_a":"world","body_b":"grasp_target","contact_count":1232.0,"contact_point_centroid":[0.53702,-0.02132,-0.00189],"force_p95":0.13606,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12302,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51337,-0.00902,0.25819]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4386.0,"contact_point_centroid":[0.52644,-0.0017,0.04782],"force_p95":0.07407,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12522,"mean_force":0.04919,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52606,-0.0209,0.04672]},{"body_a":"world","body_b":"grasp_target","contact_count":1968.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52919,-0.01974,0.13492]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4888.0,"contact_point_centroid":[0.52622,-0.04002,0.04821],"force_p95":0.0686,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08777,"mean_force":0.04449,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52606,-0.0209,0.04672]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2720.0,"contact_point_centroid":[0.5763,0.14443,0.20281],"force_p95":0.0112,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01609,"mean_force":0.01053,"phase_index":5.0,"phase_name":"release_1","phase_type":"descend","tcp_position_centroid":[0.57584,0.14442,0.20051]}],"total_contact_groups":14},"final_pose_error":0.06026,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.5796,0.1048,0.01602],"final_tcp_position":[0.58656,0.17289,0.19985],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":32.5459,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":309.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":32.5459,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1232.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52912,-0.01855,0.21715],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.19132,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":492.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1968.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53176,-0.021,0.05427],"tcp_start":[0.52912,-0.01855,0.21715],"tcp_to_object_dist_end":0.02874,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":8.0,"n_steps_budget":600.0,"object_pos_end":[0.53695,-0.02101,0.02582],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31661,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13492,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":10906.0,"raw_peak_contact_force":0.16535,"subtask_id":"grasp_1","tcp_end":[0.52604,-0.0209,0.04668],"tcp_start":[0.53176,-0.021,0.05427],"tcp_to_object_dist_end":0.02355,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":753.0,"n_steps_budget":840.0,"object_pos_end":[0.53284,-0.02103,0.13933],"object_pos_start":[0.53695,-0.02101,0.02582],"object_to_goal_dist_end":0.26931,"object_to_goal_dist_start":0.31661,"object_z_max":0.13921,"peak_contact_force":0.09946,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":26005.0,"raw_peak_contact_force":0.44431,"tcp_end":[0.52218,-0.02081,0.16665],"tcp_start":[0.52604,-0.0209,0.04668],"tcp_to_object_dist_end":0.02933,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55485,0.06483,0.17238],"object_pos_start":[0.53284,-0.02103,0.13933],"object_to_goal_dist_end":0.17564,"object_to_goal_dist_start":0.26931,"object_z_max":0.17236,"peak_contact_force":0.11453,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":21157.0,"raw_peak_contact_force":0.16567,"subtask_id":"transport_arc","tcp_end":[0.54924,0.06511,0.20878],"tcp_start":[0.52218,-0.02081,0.16665],"tcp_to_object_dist_end":0.03684,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5796,0.1048,0.01602],"object_pos_start":[0.55485,0.06483,0.17238],"object_to_goal_dist_end":0.22955,"object_to_goal_dist_start":0.17564,"object_z_max":0.17238,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9872.0,"raw_peak_contact_force":1.68347,"subtask_id":"release_1","tcp_end":[0.58308,0.1718,0.19221],"tcp_start":[0.54924,0.06511,0.20878],"tcp_to_object_dist_end":0.18853,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.59091,"average_solve_count":154.0,"average_success_count":154.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.19595,"contact_1.contact_force":6.12247,"lift_1.lift_height":0.12401,"transport_1.transport_speed":0.04184},"optimized_scores":{"best_composite_score":0.44584,"best_fitness_score":0.59918,"best_task_score":0.28544},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2406.0,"contact_point_centroid":[0.60853,0.07069,-0.00237],"force_p95":0.14961,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.50816,"mean_force":0.14246,"phase_index":5.0,"phase_name":"release_1","phase_type":"descend","tcp_position_centroid":[0.59887,0.11137,0.17151]},{"body_a":"world","body_b":"grasp_target","contact_count":146.0,"contact_point_centroid":[0.54313,-0.02834,-0.00116],"force_p95":0.32064,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.45043,"mean_force":0.06986,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5326,-0.02858,0.04728]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11512.0,"contact_point_centroid":[0.53161,-0.00943,0.09647],"force_p95":0.10185,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28554,"mean_force":0.0616,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53,-0.02849,0.09483]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13004.0,"contact_point_centroid":[0.53159,-0.04745,0.09546],"force_p95":0.094,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27854,"mean_force":0.05552,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53001,-0.02849,0.09399]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3812.0,"contact_point_centroid":[0.57686,0.07834,0.17399],"force_p95":0.13712,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22744,"mean_force":0.10888,"phase_index":5.0,"phase_name":"release_1","phase_type":"descend","tcp_position_centroid":[0.5711,0.06009,0.17823]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4300.0,"contact_point_centroid":[0.57643,0.0418,0.17408],"force_p95":0.12162,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18671,"mean_force":0.09643,"phase_index":5.0,"phase_name":"release_1","phase_type":"descend","tcp_position_centroid":[0.57099,0.05982,0.17832]},{"body_a":"world","body_b":"grasp_target","contact_count":1648.0,"contact_point_centroid":[0.54561,-0.02913,-0.00207],"force_p95":0.13894,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18233,"mean_force":0.12777,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53492,-0.02865,0.0464]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11796.0,"contact_point_centroid":[0.54849,-0.01544,0.16982],"force_p95":0.11278,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.167,"mean_force":0.07785,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54329,0.00303,0.17021]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11100.0,"contact_point_centroid":[0.54791,0.02045,0.1692],"force_p95":0.13235,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.167,"mean_force":0.08243,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54266,0.00185,0.16951]},{"body_a":"world","body_b":"grasp_target","contact_count":1252.0,"contact_point_centroid":[0.5456,-0.02923,-0.00189],"force_p95":0.13606,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12302,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51738,-0.01259,0.26345]},{"body_a":"world","body_b":"grasp_target","contact_count":2084.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53734,-0.02713,0.14073]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4839.0,"contact_point_centroid":[0.53369,-0.00934,0.04793],"force_p95":0.06828,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09854,"mean_force":0.04501,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53425,-0.02863,0.04557]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5637.0,"contact_point_centroid":[0.5338,-0.04783,0.04731],"force_p95":0.06241,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07756,"mean_force":0.03949,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53426,-0.02863,0.04557]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1655.0,"contact_point_centroid":[0.59913,0.10997,0.17529],"force_p95":0.01159,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0156,"mean_force":0.01058,"phase_index":5.0,"phase_name":"release_1","phase_type":"descend","tcp_position_centroid":[0.59869,0.10997,0.17304]}],"total_contact_groups":14},"final_pose_error":0.04888,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.6086,0.07065,0.01602],"final_tcp_position":[0.60665,0.12399,0.17175],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":1.50816,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":314.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1252.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.5369,-0.02556,0.22882],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.20302,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":521.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2084.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.54026,-0.02879,0.05422],"tcp_start":[0.5369,-0.02556,0.22882],"tcp_to_object_dist_end":0.0287,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":12.0,"n_steps_budget":600.0,"object_pos_end":[0.54553,-0.0287,0.02577],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.2607,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.13702,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":12124.0,"raw_peak_contact_force":0.18233,"subtask_id":"grasp_1","tcp_end":[0.53423,-0.02863,0.04553],"tcp_start":[0.54026,-0.02879,0.05422],"tcp_to_object_dist_end":0.02277,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":693.0,"n_steps_budget":780.0,"object_pos_end":[0.54188,-0.02865,0.13101],"object_pos_start":[0.54553,-0.0287,0.02577],"object_to_goal_dist_end":0.21875,"object_to_goal_dist_start":0.2607,"object_z_max":0.13089,"peak_contact_force":0.10315,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":24662.0,"raw_peak_contact_force":0.45043,"tcp_end":[0.53025,-0.02849,0.15674],"tcp_start":[0.53423,-0.02863,0.04553],"tcp_to_object_dist_end":0.02824,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56309,0.03098,0.15252],"object_pos_start":[0.54188,-0.02865,0.13101],"object_to_goal_dist_end":0.15298,"object_to_goal_dist_start":0.21875,"object_z_max":0.1525,"peak_contact_force":0.13482,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":22896.0,"raw_peak_contact_force":0.167,"subtask_id":"transport_arc","tcp_end":[0.55811,0.03098,0.18697],"tcp_start":[0.53025,-0.02849,0.15674],"tcp_to_object_dist_end":0.03481,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.6086,0.07065,0.01602],"object_pos_start":[0.56309,0.03098,0.15252],"object_to_goal_dist_end":0.18806,"object_to_goal_dist_start":0.15298,"object_z_max":0.15252,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":12173.0,"raw_peak_contact_force":1.50816,"subtask_id":"release_1","tcp_end":[0.60274,0.12313,0.16392],"tcp_start":[0.55811,0.03098,0.18697],"tcp_to_object_dist_end":0.15705,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```