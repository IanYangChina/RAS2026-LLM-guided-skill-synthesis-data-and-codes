## Search State

- **Seed**: 8
- **Iteration**: 1 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 0 | approach → descend → contact → lift → approach → descend | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.4299 | 0.25 | ✅ accepted |

**Proposal policy**: task_score is 0.25 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.430) — your mutation base

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

- **Composite score**: 0.430
- **task_score** (E): 0.254
- **fitness_score**: 0.583  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.167
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.320

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0977 |
| descend_1 | 1.00 | 1.00 | 0.1607 |
| contact_1 | 1.00 | 1.00 | 0.0096 |
| lift_1 | 1.00 | 1.00 | 0.1210 |
| transport_1 | 0.00 | 1.00 | 0.0964 |
| release_1 | 0.67 | 1.00 | 0.1118 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.517, -0.002, 0.215) | (0.522, -0.001, 0.030)→(0.522, -0.001, 0.026) | 0.287→0.289 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.517, -0.002, 0.215)→(0.517, -0.001, 0.054) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 4.000 | 0.123 | 0.123 |
| contact_1 | contact | 1.00 / force_exceeded | (0.517, -0.001, 0.054)→(0.511, -0.001, 0.047) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 45.000 | 0.143 | 0.189 |
| lift_1 | lift | 1.00 / step_budget | (0.511, -0.001, 0.047)→(0.507, -0.001, 0.168) | (0.522, -0.001, 0.026)→(0.518, -0.001, 0.140) | 0.289→0.237 | 1.00 / 23.667 | 0.080 | 0.447 |
| transport_1 | approach | 0.00 / step_budget | (0.507, -0.001, 0.168)→(0.542, 0.076, 0.213) | (0.518, -0.001, 0.140)→(0.547, 0.086, 0.115) | 0.237→0.185 | 1.00 / 13.333 | 0.112 | 0.728 |
| release_1 | descend | 0.67 / step_budget | (0.542, 0.076, 0.213)→(0.588, 0.175, 0.191) | (0.547, 0.086, 0.115)→(0.572, 0.131, 0.016) | 0.185→0.208 | 1.00 / 4.000 | 0.123 | 1.140 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.317
- phase_score: 0.336
- phase_breakdown.approach_1_score: 0.019
- phase_breakdown.descend_1_score: 0.870
- phase_breakdown.transport_arc_score: 0.057
- phase_breakdown.release_1_score: 0.446
- phase_breakdown.grasp_1_score: 1.000
- grasp_place_fitness: 0.615

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.615
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.317
- **Median Q (composite search score)**: 0.422
- **K-run variance**: 0.0005
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.188


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.79874,"average_solve_count":159.0,"average_success_count":159.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.2295,"contact_1.contact_force":10.06274,"lift_1.lift_height":0.14142,"transport_1.transport_speed":0.07247},"optimized_scores":{"best_composite_score":0.40608,"best_fitness_score":0.55941,"best_task_score":0.20709},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":176.0,"contact_point_centroid":[0.52228,0.14925,-0.00818],"force_p95":1.34793,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.85176,"mean_force":0.45733,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51137,0.11912,0.23288]},{"body_a":"world","body_b":"grasp_target","contact_count":139.0,"contact_point_centroid":[0.48017,0.04635,-0.0012],"force_p95":0.26304,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.40451,"mean_force":0.05549,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47158,0.04706,0.04988]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14212.0,"contact_point_centroid":[0.47074,0.06574,0.10707],"force_p95":0.09768,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29806,"mean_force":0.05893,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46919,0.04684,0.10646]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13449.0,"contact_point_centroid":[0.47001,0.02786,0.10599],"force_p95":0.11812,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29626,"mean_force":0.06245,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46916,0.04684,0.10599]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7474.0,"contact_point_centroid":[0.49215,0.06232,0.19792],"force_p95":0.13495,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24459,"mean_force":0.10224,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.4874,0.08059,0.20134]},{"body_a":"world","body_b":"grasp_target","contact_count":1644.0,"contact_point_centroid":[0.48273,0.0486,-0.00214],"force_p95":0.15745,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21355,"mean_force":0.1326,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47366,0.04728,0.0486]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8247.0,"contact_point_centroid":[0.49169,0.09703,0.19737],"force_p95":0.13306,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18565,"mean_force":0.09342,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.48641,0.07896,0.20004]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4091.0,"contact_point_centroid":[0.47232,0.02801,0.04901],"force_p95":0.07998,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14675,"mean_force":0.05205,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47307,0.04722,0.04796]},{"body_a":"world","body_b":"grasp_target","contact_count":812.0,"contact_point_centroid":[0.4827,0.04873,-0.00184],"force_p95":0.13728,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12323,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49126,0.01868,0.28068]},{"body_a":"world","body_b":"grasp_target","contact_count":4600.0,"contact_point_centroid":[0.52125,0.15065,-0.00199],"force_p95":0.12289,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13202,"mean_force":0.12155,"phase_index":5.0,"phase_name":"release_1","phase_type":"descend","tcp_position_centroid":[0.54854,0.18097,0.22443]},{"body_a":"world","body_b":"grasp_target","contact_count":2584.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47979,0.04336,0.15735]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4990.0,"contact_point_centroid":[0.47317,0.06634,0.04905],"force_p95":0.07327,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07448,"mean_force":0.04412,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47307,0.04722,0.04796]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4288.0,"contact_point_centroid":[0.54596,0.17594,0.22765],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01503,"mean_force":0.01039,"phase_index":5.0,"phase_name":"release_1","phase_type":"descend","tcp_position_centroid":[0.54549,0.17592,0.22542]}],"total_contact_groups":13},"final_pose_error":0.01477,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.52125,0.15065,0.01602],"final_tcp_position":[0.57352,0.21944,0.22276],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":1.85176,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":204.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":812.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.48328,0.0392,0.26203],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.2362,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":646.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2584.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.47849,0.0477,0.05483],"tcp_start":[0.48328,0.0392,0.26203],"tcp_to_object_dist_end":0.02913,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":11.0,"n_steps_budget":600.0,"object_pos_end":[0.48266,0.04762,0.02555],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29101,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.15386,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":10725.0,"raw_peak_contact_force":0.21355,"subtask_id":"grasp_1","tcp_end":[0.47304,0.04722,0.04793],"tcp_start":[0.47849,0.0477,0.05483],"tcp_to_object_dist_end":0.02436,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":813.0,"n_steps_budget":900.0,"object_pos_end":[0.47868,0.04778,0.1478],"object_pos_start":[0.48266,0.04762,0.02555],"object_to_goal_dist_end":0.22422,"object_to_goal_dist_start":0.29101,"object_z_max":0.14769,"peak_contact_force":0.13531,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":27800.0,"raw_peak_contact_force":0.40451,"tcp_end":[0.46947,0.04688,0.17778],"tcp_start":[0.47304,0.04722,0.04793],"tcp_to_object_dist_end":0.03138,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51829,0.14925,0.01129],"object_pos_start":[0.47868,0.04778,0.1478],"object_to_goal_dist_end":0.24171,"object_to_goal_dist_start":0.22422,"object_z_max":0.18702,"peak_contact_force":0.10876,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":15897.0,"raw_peak_contact_force":1.85176,"subtask_id":"transport_arc","tcp_end":[0.5123,0.12061,0.23411],"tcp_start":[0.46947,0.04688,0.17778],"tcp_to_object_dist_end":0.22474,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52125,0.15065,0.01602],"object_pos_start":[0.51829,0.14925,0.01129],"object_to_goal_dist_end":0.23619,"object_to_goal_dist_start":0.24171,"object_z_max":0.01681,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8888.0,"raw_peak_contact_force":0.13202,"subtask_id":"release_1","tcp_end":[0.57041,0.21816,0.21509],"tcp_start":[0.5123,0.12061,0.23411],"tcp_to_object_dist_end":0.21587,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.82979,"average_solve_count":141.0,"average_success_count":141.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.11941,"contact_1.contact_force":6.53356,"lift_1.lift_height":0.12903,"transport_1.transport_speed":0.0934},"optimized_scores":{"best_composite_score":0.42222,"best_fitness_score":0.57555,"best_task_score":0.23794},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3160.0,"contact_point_centroid":[0.58524,0.13208,-0.00233],"force_p95":0.12901,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.72802,"mean_force":0.1402,"phase_index":5.0,"phase_name":"release_1","phase_type":"descend","tcp_position_centroid":[0.57762,0.15058,0.19877]},{"body_a":"world","body_b":"grasp_target","contact_count":141.0,"contact_point_centroid":[0.53433,-0.02047,-0.00115],"force_p95":0.34875,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.4741,"mean_force":0.06833,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5242,-0.02086,0.04805]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11793.0,"contact_point_centroid":[0.52332,-0.00176,0.09882],"force_p95":0.10229,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27291,"mean_force":0.06269,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52162,-0.0208,0.09776]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13273.0,"contact_point_centroid":[0.52323,-0.03974,0.09825],"force_p95":0.09488,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27286,"mean_force":0.05646,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52164,-0.0208,0.09712]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2218.0,"contact_point_centroid":[0.56068,0.06891,0.19787],"force_p95":0.13848,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21705,"mean_force":0.10601,"phase_index":5.0,"phase_name":"release_1","phase_type":"descend","tcp_position_centroid":[0.55463,0.08713,0.20195]},{"body_a":"world","body_b":"grasp_target","contact_count":1636.0,"contact_point_centroid":[0.53703,-0.02127,-0.00205],"force_p95":0.13561,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17155,"mean_force":0.12657,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52643,-0.0209,0.04711]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11333.0,"contact_point_centroid":[0.53972,0.00555,0.18196],"force_p95":0.11386,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16453,"mean_force":0.08129,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53436,0.02402,0.18294]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11034.0,"contact_point_centroid":[0.53951,0.04224,0.18157],"force_p95":0.11721,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16319,"mean_force":0.08371,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53425,0.02371,0.18277]},{"body_a":"world","body_b":"grasp_target","contact_count":1920.0,"contact_point_centroid":[0.53702,-0.02132,-0.00193],"force_p95":0.1331,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12288,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5138,-0.00952,0.22774]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2403.0,"contact_point_centroid":[0.56063,0.1056,0.19767],"force_p95":0.11987,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13471,"mean_force":0.09666,"phase_index":5.0,"phase_name":"release_1","phase_type":"descend","tcp_position_centroid":[0.55477,0.08754,0.20191]},{"body_a":"world","body_b":"grasp_target","contact_count":1252.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52955,-0.02016,0.10482]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4845.0,"contact_point_centroid":[0.52534,-0.00164,0.04716],"force_p95":0.06799,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0982,"mean_force":0.04504,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52581,-0.02089,0.04636]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5377.0,"contact_point_centroid":[0.52516,-0.0401,0.04745],"force_p95":0.06423,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08225,"mean_force":0.04096,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52581,-0.02089,0.04636]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2515.0,"contact_point_centroid":[0.5775,0.14802,0.20205],"force_p95":0.01133,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01641,"mean_force":0.01056,"phase_index":5.0,"phase_name":"release_1","phase_type":"descend","tcp_position_centroid":[0.57707,0.14802,0.19985]}],"total_contact_groups":14},"final_pose_error":0.05962,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.58529,0.13224,0.01602],"final_tcp_position":[0.58672,0.17359,0.19943],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":1.72802,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":481.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1920.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.5301,-0.01941,0.15634],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13052,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":313.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1252.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53155,-0.02098,0.0541],"tcp_start":[0.5301,-0.01941,0.15634],"tcp_to_object_dist_end":0.02861,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":9.0,"n_steps_budget":600.0,"object_pos_end":[0.53695,-0.02099,0.02582],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31659,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13499,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":11858.0,"raw_peak_contact_force":0.17155,"subtask_id":"grasp_1","tcp_end":[0.52578,-0.02089,0.04632],"tcp_start":[0.53155,-0.02098,0.0541],"tcp_to_object_dist_end":0.02335,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":723.0,"n_steps_budget":810.0,"object_pos_end":[0.53292,-0.02099,0.13595],"object_pos_start":[0.53695,-0.02099,0.02582],"object_to_goal_dist_end":0.27013,"object_to_goal_dist_start":0.31659,"object_z_max":0.13583,"peak_contact_force":0.0,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":25207.0,"raw_peak_contact_force":0.4741,"tcp_end":[0.52189,-0.0208,0.16272],"tcp_start":[0.52578,-0.02089,0.04632],"tcp_to_object_dist_end":0.02895,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55506,0.06727,0.1721],"object_pos_start":[0.53292,-0.02099,0.13595],"object_to_goal_dist_end":0.17337,"object_to_goal_dist_start":0.27013,"object_z_max":0.17208,"peak_contact_force":0.11388,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":22367.0,"raw_peak_contact_force":0.16453,"subtask_id":"transport_arc","tcp_end":[0.54988,0.06744,0.20756],"tcp_start":[0.52189,-0.0208,0.16272],"tcp_to_object_dist_end":0.03584,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58529,0.13224,0.01602],"object_pos_start":[0.55506,0.06727,0.1721],"object_to_goal_dist_end":0.21536,"object_to_goal_dist_start":0.17337,"object_z_max":0.1721,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10296.0,"raw_peak_contact_force":1.72802,"subtask_id":"release_1","tcp_end":[0.58323,0.17249,0.19178],"tcp_start":[0.54988,0.06744,0.20756],"tcp_to_object_dist_end":0.18033,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.76923,"average_solve_count":143.0,"average_success_count":143.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.19387,"contact_1.contact_force":10.06002,"lift_1.lift_height":0.12941,"transport_1.transport_speed":0.07046},"optimized_scores":{"best_composite_score":0.46155,"best_fitness_score":0.61488,"best_task_score":0.31747},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2840.0,"contact_point_centroid":[0.60904,0.10866,-0.0023],"force_p95":0.13079,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.56037,"mean_force":0.13888,"phase_index":5.0,"phase_name":"release_1","phase_type":"descend","tcp_position_centroid":[0.60319,0.11887,0.17478]},{"body_a":"world","body_b":"grasp_target","contact_count":147.0,"contact_point_centroid":[0.543,-0.02812,-0.00118],"force_p95":0.32215,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.46239,"mean_force":0.07094,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53265,-0.02857,0.04767]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13300.0,"contact_point_centroid":[0.53179,-0.04744,0.0975],"force_p95":0.09454,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2721,"mean_force":0.0566,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53009,-0.02848,0.09614]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11908.0,"contact_point_centroid":[0.53174,-0.00945,0.09873],"force_p95":0.10225,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27073,"mean_force":0.06207,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53007,-0.02848,0.0975]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3164.0,"contact_point_centroid":[0.57941,0.0461,0.18241],"force_p95":0.13143,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23603,"mean_force":0.10231,"phase_index":5.0,"phase_name":"release_1","phase_type":"descend","tcp_position_centroid":[0.57368,0.0643,0.18665]},{"body_a":"world","body_b":"grasp_target","contact_count":1644.0,"contact_point_centroid":[0.54561,-0.02918,-0.00207],"force_p95":0.14065,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18234,"mean_force":0.12788,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53496,-0.02865,0.04679]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11449.0,"contact_point_centroid":[0.55114,-0.01102,0.17688],"force_p95":0.11379,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16802,"mean_force":0.08027,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54584,0.00747,0.17765]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11220.0,"contact_point_centroid":[0.55095,0.02582,0.17654],"force_p95":0.11534,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16663,"mean_force":0.08199,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54574,0.00728,0.17754]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3217.0,"contact_point_centroid":[0.57976,0.08305,0.18217],"force_p95":0.12213,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16646,"mean_force":0.09923,"phase_index":5.0,"phase_name":"release_1","phase_type":"descend","tcp_position_centroid":[0.57402,0.06492,0.18652]},{"body_a":"world","body_b":"grasp_target","contact_count":1268.0,"contact_point_centroid":[0.5456,-0.02923,-0.00189],"force_p95":0.13591,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12301,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51741,-0.01261,0.26246]},{"body_a":"world","body_b":"grasp_target","contact_count":2064.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53735,-0.02714,0.13984]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4839.0,"contact_point_centroid":[0.53387,-0.00932,0.04693],"force_p95":0.0697,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10379,"mean_force":0.04528,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53431,-0.02863,0.04598]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5879.0,"contact_point_centroid":[0.53427,-0.04782,0.04796],"force_p95":0.06169,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0776,"mean_force":0.03769,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53431,-0.02863,0.04598]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2105.0,"contact_point_centroid":[0.6033,0.11737,0.17856],"force_p95":0.01124,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01626,"mean_force":0.01058,"phase_index":5.0,"phase_name":"release_1","phase_type":"descend","tcp_position_centroid":[0.60286,0.11736,0.17629]}],"total_contact_groups":14},"final_pose_error":0.03569,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.60913,0.10863,0.01602],"final_tcp_position":[0.61298,0.13554,0.17303],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":1.56037,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":318.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1268.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.53692,-0.02559,0.22691],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.20111,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":516.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2064.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.54026,-0.02879,0.05445],"tcp_start":[0.53692,-0.02559,0.22691],"tcp_to_object_dist_end":0.02893,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":48.0,"n_steps":11.0,"n_steps_budget":600.0,"object_pos_end":[0.54553,-0.02874,0.02576],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26073,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.14026,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":12362.0,"raw_peak_contact_force":0.18234,"subtask_id":"grasp_1","tcp_end":[0.53428,-0.02862,0.04595],"tcp_start":[0.54026,-0.02879,0.05445],"tcp_to_object_dist_end":0.02311,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":724.0,"n_steps_budget":810.0,"object_pos_end":[0.54156,-0.02869,0.13604],"object_pos_start":[0.54553,-0.02874,0.02576],"object_to_goal_dist_end":0.21793,"object_to_goal_dist_start":0.26073,"object_z_max":0.13592,"peak_contact_force":0.1034,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":25355.0,"raw_peak_contact_force":0.46239,"tcp_end":[0.53036,-0.02848,0.16251],"tcp_start":[0.53428,-0.02862,0.04595],"tcp_to_object_dist_end":0.02875,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56854,0.04054,0.16165],"object_pos_start":[0.54156,-0.02869,0.13604],"object_to_goal_dist_end":0.14086,"object_to_goal_dist_start":0.21793,"object_z_max":0.16162,"peak_contact_force":0.1135,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":22669.0,"raw_peak_contact_force":0.16802,"subtask_id":"transport_arc","tcp_end":[0.56356,0.04083,0.19668],"tcp_start":[0.53036,-0.02848,0.16251],"tcp_to_object_dist_end":0.03539,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.60913,0.10863,0.01602],"object_pos_start":[0.56854,0.04054,0.16165],"object_to_goal_dist_end":0.17211,"object_to_goal_dist_start":0.14086,"object_z_max":0.16165,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11326.0,"raw_peak_contact_force":1.56037,"subtask_id":"release_1","tcp_end":[0.6091,0.1346,0.16499],"tcp_start":[0.56356,0.04083,0.19668],"tcp_to_object_dist_end":0.15122,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```