## Search State

- **Seed**: 8
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → descend → contact → lift → approach → descend | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.4248 | 0.24 | ❌ rejected |
| 9 | approach → descend → contact → lift → approach → descend | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.3303 | 0.15 | ❌ rejected |
| 8 | approach → descend → contact → lift → approach → descend | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.4211 | 0.24 | ❌ rejected |
| 7 | approach → descend → contact → lift → approach → descend | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.4221 | 0.24 | ❌ rejected |
| 6 | approach → descend → contact → lift → approach → descend | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.4211 | 0.24 | ❌ rejected |

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

## Current Skill (Q=0.425) — your mutation base

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

- **Composite score**: 0.425
- **task_score** (E): 0.244
- **fitness_score**: 0.578  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.167
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.320

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0611 |
| descend_1 | 1.00 | 1.00 | 0.2128 |
| contact_1 | 1.00 | 1.00 | 0.0096 |
| lift_1 | 1.00 | 1.00 | 0.1152 |
| transport_1 | 0.00 | 0.67 | 0.0921 |
| release_1 | 0.67 | 1.00 | 0.1088 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.516, -0.000, 0.267) | (0.522, -0.001, 0.030)→(0.522, -0.001, 0.026) | 0.287→0.289 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.516, -0.000, 0.267)→(0.517, -0.001, 0.054) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 4.000 | 0.123 | 0.123 |
| contact_1 | contact | 1.00 / force_exceeded | (0.517, -0.001, 0.054)→(0.511, -0.001, 0.047) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 43.667 | 0.141 | 0.185 |
| lift_1 | lift | 1.00 / step_budget | (0.511, -0.001, 0.047)→(0.507, -0.001, 0.162) | (0.522, -0.001, 0.026)→(0.518, -0.001, 0.135) | 0.289→0.239 | 1.00 / 23.667 | 0.113 | 0.437 |
| transport_1 | approach | 0.00 / step_budget | (0.507, -0.001, 0.162)→(0.540, 0.073, 0.206) | (0.518, -0.001, 0.135)→(0.545, 0.079, 0.136) | 0.239→0.170 | 0.67 / 12.333 | 0.078 | 0.198 |
| release_1 | descend | 0.67 / step_budget | (0.540, 0.073, 0.206)→(0.584, 0.169, 0.189) | (0.545, 0.079, 0.136)→(0.568, 0.117, 0.016) | 0.170→0.215 | 1.00 / 4.000 | 0.123 | 1.624 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.324
- phase_score: 0.346
- phase_breakdown.approach_1_score: 0.014
- phase_breakdown.descend_1_score: 0.872
- phase_breakdown.transport_arc_score: 0.063
- phase_breakdown.release_1_score: 0.490
- phase_breakdown.grasp_1_score: 1.000
- grasp_place_fitness: 0.618

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.618
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.324
- **Median Q (composite search score)**: 0.407
- **K-run variance**: 0.0008
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.310


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.52222,"average_solve_count":180.0,"average_success_count":180.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.28901,"contact_1.contact_force":15.89701,"lift_1.lift_height":0.1355,"transport_1.transport_speed":0.01226},"optimized_scores":{"best_composite_score":0.40231,"best_fitness_score":0.55564,"best_task_score":0.19957},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":4514.0,"contact_point_centroid":[0.51348,0.14072,-0.00223],"force_p95":0.12389,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.77736,"mean_force":0.13359,"phase_index":5.0,"phase_name":"release_1","phase_type":"descend","tcp_position_centroid":[0.54024,0.16838,0.21803]},{"body_a":"world","body_b":"grasp_target","contact_count":137.0,"contact_point_centroid":[0.48012,0.04665,-0.00119],"force_p95":0.26463,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.40324,"mean_force":0.05624,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4715,0.04732,0.04963]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13297.0,"contact_point_centroid":[0.46983,0.02811,0.10452],"force_p95":0.11023,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29763,"mean_force":0.06117,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46905,0.04709,0.10431]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13830.0,"contact_point_centroid":[0.47053,0.06604,0.10487],"force_p95":0.09571,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29645,"mean_force":0.0585,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46908,0.0471,0.10413]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8111.0,"contact_point_centroid":[0.48957,0.05901,0.19028],"force_p95":0.13534,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25582,"mean_force":0.1024,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.48503,0.07733,0.19345]},{"body_a":"world","body_b":"grasp_target","contact_count":1648.0,"contact_point_centroid":[0.48273,0.0486,-0.00212],"force_p95":0.1523,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2085,"mean_force":0.13118,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47357,0.04753,0.04843]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9285.0,"contact_point_centroid":[0.4891,0.09382,0.18985],"force_p95":0.13309,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17191,"mean_force":0.08958,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.48407,0.07575,0.19213]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4096.0,"contact_point_centroid":[0.47222,0.02827,0.04894],"force_p95":0.07947,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14484,"mean_force":0.05203,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47296,0.04747,0.04777]},{"body_a":"world","body_b":"grasp_target","contact_count":1240.0,"contact_point_centroid":[0.4827,0.04873,-0.00189],"force_p95":0.13606,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12302,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48988,0.02209,0.30437]},{"body_a":"world","body_b":"grasp_target","contact_count":3176.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47947,0.04519,0.18164]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4968.0,"contact_point_centroid":[0.47307,0.06658,0.04892],"force_p95":0.07248,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07347,"mean_force":0.04421,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47297,0.04748,0.04777]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3961.0,"contact_point_centroid":[0.53925,0.16588,0.22072],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0165,"mean_force":0.01046,"phase_index":5.0,"phase_name":"release_1","phase_type":"descend","tcp_position_centroid":[0.53877,0.16585,0.21845]}],"total_contact_groups":12},"final_pose_error":0.0317,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.51345,0.14077,0.01602],"final_tcp_position":[0.56385,0.20461,0.22087],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":1.77736,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":311.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1240.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.48238,0.04255,0.31124],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.28529,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":794.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3176.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.47844,0.04799,0.05484],"tcp_start":[0.48238,0.04255,0.31124],"tcp_to_object_dist_end":0.02914,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":12.0,"n_steps_budget":600.0,"object_pos_end":[0.48265,0.04777,0.02562],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29087,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.14922,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":10712.0,"raw_peak_contact_force":0.2085,"subtask_id":"grasp_1","tcp_end":[0.47294,0.04747,0.04774],"tcp_start":[0.47844,0.04799,0.05484],"tcp_to_object_dist_end":0.02416,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":783.0,"n_steps_budget":870.0,"object_pos_end":[0.47897,0.04784,0.14261],"object_pos_start":[0.48265,0.04777,0.02562],"object_to_goal_dist_end":0.226,"object_to_goal_dist_start":0.29087,"object_z_max":0.1425,"peak_contact_force":0.1346,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":27264.0,"raw_peak_contact_force":0.40324,"tcp_end":[0.46932,0.04713,0.17175],"tcp_start":[0.47294,0.04747,0.04774],"tcp_to_object_dist_end":0.03071,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50879,0.12712,0.07987],"object_pos_start":[0.47897,0.04784,0.14261],"object_to_goal_dist_end":0.1959,"object_to_goal_dist_start":0.226,"object_z_max":0.17781,"peak_contact_force":0.0,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":17396.0,"raw_peak_contact_force":0.25582,"subtask_id":"transport_arc","tcp_end":[0.50471,0.10891,0.22038],"tcp_start":[0.46932,0.04713,0.17175],"tcp_to_object_dist_end":0.14174,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51345,0.14077,0.01602],"object_pos_start":[0.50879,0.12712,0.07987],"object_to_goal_dist_end":0.24174,"object_to_goal_dist_start":0.1959,"object_z_max":0.07987,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8475.0,"raw_peak_contact_force":1.77736,"subtask_id":"release_1","tcp_end":[0.5607,0.2034,0.21353],"tcp_start":[0.50471,0.10891,0.22038],"tcp_to_object_dist_end":0.21252,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.82759,"average_solve_count":145.0,"average_success_count":145.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.21529,"contact_1.contact_force":9.76164,"lift_1.lift_height":0.11889,"transport_1.transport_speed":0.08391},"optimized_scores":{"best_composite_score":0.40695,"best_fitness_score":0.56028,"best_task_score":0.2078},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2662.0,"contact_point_centroid":[0.57547,0.09478,-0.00236],"force_p95":0.12661,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.58126,"mean_force":0.13837,"phase_index":5.0,"phase_name":"release_1","phase_type":"descend","tcp_position_centroid":[0.57696,0.14898,0.19441]},{"body_a":"world","body_b":"grasp_target","contact_count":144.0,"contact_point_centroid":[0.53455,-0.0206,-0.00114],"force_p95":0.32225,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.44431,"mean_force":0.06585,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52446,-0.02086,0.04847]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11212.0,"contact_point_centroid":[0.52328,-0.00174,0.09585],"force_p95":0.09951,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29973,"mean_force":0.06089,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52188,-0.0208,0.09487]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12557.0,"contact_point_centroid":[0.52305,-0.03977,0.09593],"force_p95":0.0913,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29403,"mean_force":0.0551,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52188,-0.0208,0.09498]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3531.0,"contact_point_centroid":[0.56063,0.10814,0.18938],"force_p95":0.12379,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25349,"mean_force":0.10222,"phase_index":5.0,"phase_name":"release_1","phase_type":"descend","tcp_position_centroid":[0.55547,0.08982,0.19402]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10477.0,"contact_point_centroid":[0.53845,0.03986,0.17221],"force_p95":0.12403,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17089,"mean_force":0.08708,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53346,0.02134,0.17332]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11449.0,"contact_point_centroid":[0.53808,0.0028,0.17214],"force_p95":0.12,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17074,"mean_force":0.07998,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53342,0.02123,0.17325]},{"body_a":"world","body_b":"grasp_target","contact_count":1632.0,"contact_point_centroid":[0.53703,-0.02125,-0.00205],"force_p95":0.13579,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16578,"mean_force":0.12662,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.5267,-0.0209,0.04748]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3878.0,"contact_point_centroid":[0.56056,0.07183,0.18959],"force_p95":0.11635,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14078,"mean_force":0.09217,"phase_index":5.0,"phase_name":"release_1","phase_type":"descend","tcp_position_centroid":[0.55554,0.08999,0.19404]},{"body_a":"world","body_b":"grasp_target","contact_count":960.0,"contact_point_centroid":[0.53702,-0.02132,-0.00186],"force_p95":0.13692,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12314,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51304,-0.00874,0.27329]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4232.0,"contact_point_centroid":[0.52681,-0.00168,0.04807],"force_p95":0.0765,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12513,"mean_force":0.05082,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52609,-0.02089,0.04674]},{"body_a":"world","body_b":"grasp_target","contact_count":2328.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52879,-0.0194,0.15017]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4888.0,"contact_point_centroid":[0.52625,-0.03997,0.04822],"force_p95":0.06841,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08788,"mean_force":0.04446,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52609,-0.02089,0.04674]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1926.0,"contact_point_centroid":[0.57723,0.14722,0.19787],"force_p95":0.01136,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0155,"mean_force":0.01059,"phase_index":5.0,"phase_name":"release_1","phase_type":"descend","tcp_position_centroid":[0.57679,0.14721,0.19554]}],"total_contact_groups":14},"final_pose_error":0.06786,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.57544,0.09472,0.01602],"final_tcp_position":[0.58405,0.16617,0.19629],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":1.58126,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":241.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":960.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52814,-0.01787,0.24797],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.22215,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":582.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2328.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53179,-0.02098,0.0543],"tcp_start":[0.52814,-0.01787,0.24797],"tcp_to_object_dist_end":0.02876,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":8.0,"n_steps_budget":600.0,"object_pos_end":[0.53695,-0.02098,0.02582],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31659,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13461,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":10752.0,"raw_peak_contact_force":0.16578,"subtask_id":"grasp_1","tcp_end":[0.52606,-0.02089,0.04671],"tcp_start":[0.53179,-0.02098,0.0543],"tcp_to_object_dist_end":0.02356,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":663.0,"n_steps_budget":750.0,"object_pos_end":[0.53325,-0.02096,0.12651],"object_pos_start":[0.53695,-0.02098,0.02582],"object_to_goal_dist_end":0.27266,"object_to_goal_dist_start":0.31659,"object_z_max":0.12639,"peak_contact_force":0.10249,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":23913.0,"raw_peak_contact_force":0.44431,"tcp_end":[0.52208,-0.0208,0.15299],"tcp_start":[0.52606,-0.02089,0.04671],"tcp_to_object_dist_end":0.02874,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55338,0.06286,0.16319],"object_pos_start":[0.53325,-0.02096,0.12651],"object_to_goal_dist_end":0.17997,"object_to_goal_dist_start":0.27266,"object_z_max":0.16315,"peak_contact_force":0.11433,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":21926.0,"raw_peak_contact_force":0.17089,"subtask_id":"transport_arc","tcp_end":[0.54836,0.06303,0.19862],"tcp_start":[0.52208,-0.0208,0.15299],"tcp_to_object_dist_end":0.03579,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.57544,0.09472,0.01602],"object_pos_start":[0.55338,0.06286,0.16319],"object_to_goal_dist_end":0.23568,"object_to_goal_dist_start":0.17997,"object_z_max":0.16319,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11997.0,"raw_peak_contact_force":1.58126,"subtask_id":"release_1","tcp_end":[0.58052,0.16512,0.18875],"tcp_start":[0.54836,0.06303,0.19862],"tcp_to_object_dist_end":0.1866,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.83217,"average_solve_count":143.0,"average_success_count":143.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.21117,"contact_1.contact_force":1.8466,"lift_1.lift_height":0.12775,"transport_1.transport_speed":0.08638},"optimized_scores":{"best_composite_score":0.4651,"best_fitness_score":0.61843,"best_task_score":0.32415},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2673.0,"contact_point_centroid":[0.61393,0.11687,-0.00232],"force_p95":0.13113,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.51455,"mean_force":0.13986,"phase_index":5.0,"phase_name":"release_1","phase_type":"descend","tcp_position_centroid":[0.60661,0.12509,0.17449]},{"body_a":"world","body_b":"grasp_target","contact_count":147.0,"contact_point_centroid":[0.54301,-0.02812,-0.00117],"force_p95":0.31999,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.46278,"mean_force":0.0704,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53267,-0.02858,0.04756]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11860.0,"contact_point_centroid":[0.53177,-0.00945,0.09814],"force_p95":0.10213,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28403,"mean_force":0.06215,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53009,-0.02849,0.09678]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13417.0,"contact_point_centroid":[0.53177,-0.04745,0.09683],"force_p95":0.09448,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2726,"mean_force":0.05604,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53011,-0.02849,0.09545]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3396.0,"contact_point_centroid":[0.58419,0.0912,0.18273],"force_p95":0.13519,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2135,"mean_force":0.10432,"phase_index":5.0,"phase_name":"release_1","phase_type":"descend","tcp_position_centroid":[0.57839,0.07306,0.18702]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3557.0,"contact_point_centroid":[0.58325,0.05344,0.18321],"force_p95":0.12917,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21242,"mean_force":0.1014,"phase_index":5.0,"phase_name":"release_1","phase_type":"descend","tcp_position_centroid":[0.57761,0.07155,0.18745]},{"body_a":"world","body_b":"grasp_target","contact_count":1644.0,"contact_point_centroid":[0.54561,-0.02917,-0.00207],"force_p95":0.14037,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18208,"mean_force":0.12781,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53499,-0.02866,0.04667]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11565.0,"contact_point_centroid":[0.5526,-0.00828,0.17722],"force_p95":0.11362,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16766,"mean_force":0.07964,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54732,0.01022,0.17789]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11349.0,"contact_point_centroid":[0.55238,0.02849,0.17687],"force_p95":0.11536,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16654,"mean_force":0.08122,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54717,0.00993,0.17773]},{"body_a":"world","body_b":"grasp_target","contact_count":1168.0,"contact_point_centroid":[0.5456,-0.02923,-0.00189],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12304,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51737,-0.01259,0.27006]},{"body_a":"world","body_b":"grasp_target","contact_count":2244.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53725,-0.02703,0.14758]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4839.0,"contact_point_centroid":[0.5339,-0.00932,0.04684],"force_p95":0.06959,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09924,"mean_force":0.04527,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53434,-0.02863,0.04586]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5878.0,"contact_point_centroid":[0.5342,-0.04783,0.04784],"force_p95":0.06155,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07726,"mean_force":0.0377,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53434,-0.02863,0.04586]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1923.0,"contact_point_centroid":[0.60687,0.12374,0.17832],"force_p95":0.01156,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01647,"mean_force":0.01062,"phase_index":5.0,"phase_name":"release_1","phase_type":"descend","tcp_position_centroid":[0.60641,0.12374,0.17609]}],"total_contact_groups":14},"final_pose_error":0.0307,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.61404,0.11685,0.01602],"final_tcp_position":[0.61545,0.13997,0.17279],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":1.51455,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":293.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1168.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.53659,-0.02536,0.24256],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.21676,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":561.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2244.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.54028,-0.0288,0.0543],"tcp_start":[0.53659,-0.02536,0.24256],"tcp_to_object_dist_end":0.02878,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":48.0,"n_steps":11.0,"n_steps_budget":600.0,"object_pos_end":[0.54553,-0.02875,0.02576],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26074,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.13998,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":12361.0,"raw_peak_contact_force":0.18208,"subtask_id":"grasp_1","tcp_end":[0.53431,-0.02863,0.04582],"tcp_start":[0.54028,-0.0288,0.0543],"tcp_to_object_dist_end":0.02298,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":723.0,"n_steps_budget":810.0,"object_pos_end":[0.54164,-0.02869,0.13451],"object_pos_start":[0.54553,-0.02875,0.02576],"object_to_goal_dist_end":0.21818,"object_to_goal_dist_start":0.26074,"object_z_max":0.1344,"peak_contact_force":0.10339,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":25424.0,"raw_peak_contact_force":0.46278,"tcp_end":[0.53037,-0.02849,0.16082],"tcp_start":[0.53431,-0.02863,0.04582],"tcp_to_object_dist_end":0.02862,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.57138,0.04575,0.16383],"object_pos_start":[0.54164,-0.02869,0.13451],"object_to_goal_dist_end":0.13473,"object_to_goal_dist_start":0.21818,"object_z_max":0.16378,"peak_contact_force":0.11894,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":22914.0,"raw_peak_contact_force":0.16766,"subtask_id":"transport_arc","tcp_end":[0.56633,0.04599,0.19864],"tcp_start":[0.53037,-0.02849,0.16082],"tcp_to_object_dist_end":0.03518,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.61404,0.11685,0.01602],"object_pos_start":[0.57138,0.04575,0.16383],"object_to_goal_dist_end":0.16898,"object_to_goal_dist_start":0.13473,"object_z_max":0.16383,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11549.0,"raw_peak_contact_force":1.51455,"subtask_id":"release_1","tcp_end":[0.61156,0.139,0.16468],"tcp_start":[0.56633,0.04599,0.19864],"tcp_to_object_dist_end":0.15032,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```