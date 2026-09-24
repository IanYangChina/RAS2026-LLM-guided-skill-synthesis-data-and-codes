## Search State

- **Seed**: 8
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | 0.1471 | 0.28 | ❌ rejected |
| 1 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | 0.2688 | 0.29 | ✅ accepted |
| 0 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 4 | 0.0851 | 0.15 | ✅ accepted |

**Proposal policy**: task_score is 0.28 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.147) — your mutation base

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
    - 0.1
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
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
  parameters:
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
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.15
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.1
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
- id: transport_1
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: place_target
    offset:
    - 0.0
    - 0.0
    - 0.1
  parameters:
    arc_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.arc_height
        mode: replace
  subtask_id: transport_arc
- id: descend_2
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: place_target
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: release_1
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
  subtask_id: release_1

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.1]
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.02]
  - parameter_bindings:
    - grasp_z_offset: status=consumed; consumers=target.offset.z (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **lift_1** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.15]
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
- **transport_1** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=place_target, offset=[0.0, 0.0, 0.1]
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
- **descend_2** (`descend`)
  - target: source=yaml, anchor=task_goal, entity=place_target, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.147
- **task_score** (E): 0.275
- **fitness_score**: 0.597  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.450

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1518 |
| descend_1 | 1.00 | 1.00 | 0.0980 |
| grasp_1 | 1.00 | 1.00 | 0.0130 |
| lift_1 | 0.33 | 1.00 | 0.2088 |
| transport_1 | 0.00 | 1.00 | 0.1737 |
| descend_2 | 0.00 | 1.00 | 0.1454 |
| release_1 | 1.00 | 0.67 | 0.0266 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.517, -0.001, 0.156) | (0.522, -0.001, 0.030)→(0.522, -0.001, 0.026) | 0.287→0.289 | 1.00 / 4.000 | 11.594 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.517, -0.001, 0.156)→(0.516, -0.001, 0.058) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.516, -0.001, 0.058)→(0.508, -0.001, 0.048) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.290 | 1.00 / 36.333 | 0.151 | 0.177 |
| lift_1 | lift | 0.33 / step_budget | (0.508, -0.001, 0.048)→(0.638, -0.011, 0.184) | (0.522, -0.001, 0.026)→(0.662, -0.037, 0.189) | 0.290→0.267 | 1.00 / 14.667 | 3475.923 | 877.626 |
| transport_1 | approach | 0.00 / step_budget | (0.638, -0.011, 0.184)→(0.662, 0.073, 0.325) | (0.662, -0.037, 0.189)→(1.443, -0.078, -5.816) | 0.267→6.256 | 1.00 / 17.667 | 0.126 | 1211.667 |
| descend_2 | descend | 0.00 / step_budget | (0.662, 0.073, 0.325)→(0.588, 0.158, 0.283) | (1.443, -0.078, -5.816)→(2.196, -0.136, -24.918) | 6.256→25.280 | 1.00 / 19.667 | 219.782 | 813.820 |
| release_1 | release | 1.00 / step_budget | (0.588, 0.158, 0.283)→(0.588, 0.158, 0.309) | (2.196, -0.136, -24.918)→(2.330, -0.149, -30.320) | 25.280→30.661 | 0.67 / 2.000 | 0.048 | 105.895 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.747
- phase_score: 0.275
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.transport_arc_score: 0.030
- phase_breakdown.approach_1_score: 0.038
- phase_breakdown.descend_1_score: 0.822
- phase_breakdown.release_1_score: 0.166
- grasp_place_fitness: 0.831

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.831
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.747
- **Median Q (composite search score)**: 0.044
- **K-run variance**: 0.0276
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.222


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":8.0,"average_failure_rate":0.05128,"average_mean_iterations":14.60897,"average_solve_count":156.0,"average_success_count":148.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.15608,"descend_1.grasp_z_offset":0.02392,"descend_2.descend_tolerance":0.01743,"lift_1.lift_height":0.22913,"transport_1.arc_height":0.10213,"transport_1.transport_speed":0.17898},"optimized_scores":{"best_composite_score":0.38134,"best_fitness_score":0.83134,"best_task_score":0.74723},"replay_outcomes":[{"contacts":{"omitted_contact_groups":10,"reported_contact_groups":[{"body_a":"world","body_b":"hand","contact_count":101.0,"contact_point_centroid":[0.63474,0.0013,-0.00152],"force_p95":698.20345,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":885.02295,"mean_force":245.86899,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.58352,0.01194,0.02837]},{"body_a":"world","body_b":"link6","contact_count":653.0,"contact_point_centroid":[0.57807,0.20646,-0.00033],"force_p95":574.23577,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":696.88855,"mean_force":427.48684,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.58226,0.21735,0.29351]},{"body_a":"world","body_b":"link6","contact_count":765.0,"contact_point_centroid":[0.57432,-0.08173,-0.00017],"force_p95":310.35578,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":674.44839,"mean_force":250.78026,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.61701,0.10907,0.18544]},{"body_a":"world","body_b":"link7","contact_count":7.0,"contact_point_centroid":[0.61651,-0.06982,-0.00021],"force_p95":597.30482,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":608.99787,"mean_force":211.24597,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.54801,0.05942,0.04662]},{"body_a":"world","body_b":"link6","contact_count":8.0,"contact_point_centroid":[0.50004,-0.02224,-8e-05],"force_p95":336.01366,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":352.2488,"mean_force":276.762,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51511,0.02653,0.28796]},{"body_a":"world","body_b":"link6","contact_count":85.0,"contact_point_centroid":[0.5963,0.21723,-0.00016],"force_p95":85.1952,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":92.10037,"mean_force":60.89302,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58868,0.22629,0.29393]},{"body_a":"world","body_b":"right_finger","contact_count":970.0,"contact_point_centroid":[0.57324,-0.00158,-0.00689],"force_p95":13.70417,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":27.19008,"mean_force":8.34252,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.55976,-0.02242,-0.00465]},{"body_a":"world","body_b":"left_finger","contact_count":896.0,"contact_point_centroid":[0.55,-0.04771,-0.00563],"force_p95":16.58843,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":18.36975,"mean_force":11.14988,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.56029,-0.02381,-0.00557]},{"body_a":"world","body_b":"grasp_target","contact_count":328.0,"contact_point_centroid":[0.52082,0.01784,-0.00765],"force_p95":2.55964,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.69667,"mean_force":0.88074,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53578,-0.00774,0.0112]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14629.0,"contact_point_centroid":[0.61134,0.11595,0.17092],"force_p95":0.17958,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.75044,"mean_force":0.09773,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.60744,0.10533,0.18671]},{"body_a":"grasp_target","body_b":"hand","contact_count":885.0,"contact_point_centroid":[0.60829,0.06613,0.16295],"force_p95":0.44483,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.41471,"mean_force":0.21871,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.6137,0.10325,0.17551]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11992.0,"contact_point_centroid":[0.60207,0.09109,0.20233],"force_p95":0.1773,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.0082,"mean_force":0.07504,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.60552,0.10468,0.18894]},{"body_a":"grasp_target","body_b":"hand","contact_count":191.0,"contact_point_centroid":[0.58669,0.22808,0.24904],"force_p95":0.60261,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.76842,"mean_force":0.38844,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58873,0.2262,0.29949]},{"body_a":"grasp_target","body_b":"hand","contact_count":876.0,"contact_point_centroid":[0.57553,0.21253,0.26154],"force_p95":0.36802,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.5272,"mean_force":0.3501,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.57897,0.20941,0.3065]},{"body_a":"grasp_target","body_b":"hand","contact_count":1000.0,"contact_point_centroid":[0.53176,0.07842,0.32238],"force_p95":0.36613,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.50271,"mean_force":0.34243,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53164,0.07589,0.36704]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48278,0.04868,-0.00215],"force_p95":0.16388,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20374,"mean_force":0.13383,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4711,0.04706,0.0512]}],"total_contact_groups":26},"final_pose_error":0.06344,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.53997,0.23723,0.22129],"final_tcp_position":[0.58857,0.22666,0.29353],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":885.02295,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":356.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1420.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.48125,0.04287,0.1938],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16789,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":424.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1696.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.47804,0.04773,0.05856],"tcp_start":[0.48125,0.04287,0.1938],"tcp_to_object_dist_end":0.03289,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":35.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4828,0.04778,0.02535],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29101,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.16474,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":9667.0,"raw_peak_contact_force":0.20374,"subtask_id":"grasp_1","tcp_end":[0.46991,0.04695,0.04995],"tcp_start":[0.47804,0.04773,0.05856],"tcp_to_object_dist_end":0.02779,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52595,0.02531,0.27802],"object_pos_start":[0.4828,0.04778,0.02535],"object_to_goal_dist_end":0.21638,"object_to_goal_dist_start":0.29101,"object_z_max":0.27793,"peak_contact_force":344.14294,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":30573.0,"raw_peak_contact_force":885.02295,"tcp_end":[0.5154,0.0291,0.28671],"tcp_start":[0.46991,0.04695,0.04995],"tcp_to_object_dist_end":0.01418,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55629,0.17193,0.38037],"object_pos_start":[0.52595,0.02531,0.27802],"object_to_goal_dist_end":0.16236,"object_to_goal_dist_start":0.21638,"object_z_max":0.39052,"peak_contact_force":0.34854,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":41298.0,"raw_peak_contact_force":352.2488,"subtask_id":"transport_arc","tcp_end":[0.56375,0.17064,0.39464],"tcp_start":[0.5154,0.0291,0.28671],"tcp_to_object_dist_end":0.01615,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":876.0,"n_steps_budget":1000.0,"object_pos_end":[0.58497,0.22793,0.27843],"object_pos_start":[0.55629,0.17193,0.38037],"object_to_goal_dist_end":0.04806,"object_to_goal_dist_start":0.16236,"object_z_max":0.38037,"peak_contact_force":361.7864,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":36553.0,"raw_peak_contact_force":696.88855,"subtask_id":"release_1","tcp_end":[0.58857,0.22666,0.29353],"tcp_start":[0.56375,0.17064,0.39464],"tcp_to_object_dist_end":0.01558,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53997,0.23723,0.22129],"object_pos_start":[0.58497,0.22793,0.27843],"object_to_goal_dist_end":0.04371,"object_to_goal_dist_start":0.04806,"object_z_max":0.27889,"peak_contact_force":0.0,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2743.0,"raw_peak_contact_force":92.10037,"subtask_id":"release_1","tcp_end":[0.58892,0.22615,0.32008],"tcp_start":[0.58857,0.22666,0.29353],"tcp_to_object_dist_end":0.11081,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":31.0,"average_failure_rate":0.22464,"average_mean_iterations":49.02899,"average_solve_count":138.0,"average_success_count":107.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.10868,"descend_1.grasp_z_offset":0.0183,"descend_2.descend_tolerance":0.02451,"lift_1.lift_height":0.18634,"transport_1.arc_height":0.09557,"transport_1.transport_speed":0.17328},"optimized_scores":{"best_composite_score":0.01625,"best_fitness_score":0.46625,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":9,"reported_contact_groups":[{"body_a":"world","body_b":"link7","contact_count":131.0,"contact_point_centroid":[0.79817,0.01726,-7e-05],"force_p95":564.93928,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1611.1601,"mean_force":118.97538,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.88922,-0.03708,0.11989]},{"body_a":"world","body_b":"link6","contact_count":901.0,"contact_point_centroid":[0.67161,0.08199,-0.00028],"force_p95":364.90958,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1292.38277,"mean_force":269.90492,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.84497,-0.02603,0.17763]},{"body_a":"world","body_b":"link6","contact_count":990.0,"contact_point_centroid":[0.66655,0.09324,-0.00021],"force_p95":423.87333,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":886.92108,"mean_force":237.67837,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.62023,0.11119,0.28589]},{"body_a":"world","body_b":"hand","contact_count":116.0,"contact_point_centroid":[0.68105,0.02789,-0.00069],"force_p95":566.72046,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":859.53063,"mean_force":205.81163,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.60687,0.01326,-0.0005]},{"body_a":"world","body_b":"link6","contact_count":36.0,"contact_point_centroid":[0.59395,0.20612,-0.00087],"force_p95":405.42654,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":511.4007,"mean_force":280.57895,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.67897,-0.02512,0.11315]},{"body_a":"world","body_b":"link7","contact_count":23.0,"contact_point_centroid":[0.69368,0.08754,-0.00126],"force_p95":358.81011,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":362.09611,"mean_force":208.74581,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.64044,-0.03887,0.0703]},{"body_a":"world","body_b":"link6","contact_count":80.0,"contact_point_centroid":[0.66383,0.1168,-0.00011],"force_p95":68.6331,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":93.37263,"mean_force":48.11048,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57,0.15188,0.27708]},{"body_a":"world","body_b":"link5","contact_count":73.0,"contact_point_centroid":[0.53952,0.04989,-2e-05],"force_p95":51.34682,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":75.42751,"mean_force":19.39486,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57001,0.15188,0.27708]},{"body_a":"world","body_b":"link5","contact_count":285.0,"contact_point_centroid":[0.54053,0.04523,-3e-05],"force_p95":74.20323,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":75.36809,"mean_force":64.79584,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.57373,0.14399,0.27798]},{"body_a":"world","body_b":"left_finger","contact_count":1197.0,"contact_point_centroid":[0.62018,0.01802,-0.01131],"force_p95":13.05014,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":24.79754,"mean_force":8.96803,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.60465,0.03381,-0.01095]},{"body_a":"world","body_b":"right_finger","contact_count":1063.0,"contact_point_centroid":[0.59007,0.05388,-0.01187],"force_p95":17.14134,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":21.56723,"mean_force":12.03503,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.60504,0.03612,-0.0129]},{"body_a":"world","body_b":"grasp_target","contact_count":357.0,"contact_point_centroid":[0.57474,0.01216,-0.00857],"force_p95":2.52414,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.79778,"mean_force":0.82488,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.58592,0.02895,-0.00059]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":528.0,"contact_point_centroid":[0.56494,-0.03178,0.04029],"force_p95":1.47646,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.32345,"mean_force":0.61311,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.55953,-0.01455,0.03946]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":218.0,"contact_point_centroid":[0.85116,-0.00655,0.13658],"force_p95":0.72948,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.22224,"mean_force":0.31244,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.84957,-0.00357,0.13155]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":862.0,"contact_point_centroid":[0.59356,-0.00696,0.03854],"force_p95":0.42104,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.74283,"mean_force":0.21936,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.60675,-0.01406,0.03061]},{"body_a":"grasp_target","body_b":"hand","contact_count":49.0,"contact_point_centroid":[0.60962,0.03201,0.03941],"force_p95":0.56234,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.59413,"mean_force":0.38477,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.60336,0.00277,0.00434]}],"total_contact_groups":25},"final_pose_error":0.11076,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[5.67671,-0.52805,-91.20856],"final_tcp_position":[0.57026,0.1516,0.27715],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":1611.1601,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":514.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":34.5374,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2052.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.53008,-0.01956,0.14541],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1196,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":285.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1140.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53123,-0.021,0.0524],"tcp_start":[0.53008,-0.01956,0.14541],"tcp_to_object_dist_end":0.02701,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53693,-0.02129,0.02584],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31682,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13441,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11270.0,"raw_peak_contact_force":0.15748,"subtask_id":"grasp_1","tcp_end":[0.52254,-0.02088,0.04216],"tcp_start":[0.53123,-0.021,0.0524],"tcp_to_object_dist_end":0.02176,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":240.0,"n_steps_budget":1000.0,"object_pos_end":[0.75372,-0.03462,0.17095],"object_pos_start":[0.53693,-0.02129,0.02584],"object_to_goal_dist_end":0.30122,"object_to_goal_dist_start":0.31682,"object_z_max":0.17071,"peak_contact_force":335.56471,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4231.0,"raw_peak_contact_force":859.53063,"tcp_end":[0.6971,-0.02239,0.13154],"tcp_start":[0.52254,-0.02088,0.04216],"tcp_to_object_dist_end":0.07006,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[2.99809,-0.25184,-17.85387],"object_pos_start":[0.75372,-0.03462,0.17095],"object_to_goal_dist_end":18.22474,"object_to_goal_dist_start":0.30122,"object_z_max":0.17161,"peak_contact_force":0.01094,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5136.0,"raw_peak_contact_force":1611.1601,"subtask_id":"transport_arc","tcp_end":[0.69988,0.04452,0.28852],"tcp_start":[0.6971,-0.02239,0.13154],"tcp_to_object_dist_end":18.28978,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":6.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[5.23027,-0.48201,-75.05878],"object_pos_start":[2.99809,-0.25184,-17.85387],"object_to_goal_dist_end":75.41119,"object_to_goal_dist_start":18.22474,"object_z_max":-17.85387,"peak_contact_force":148.61397,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5517.0,"raw_peak_contact_force":886.92108,"subtask_id":"release_1","tcp_end":[0.57026,0.1516,0.27715],"tcp_start":[0.69988,0.04452,0.28852],"tcp_to_object_dist_end":75.48257,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[5.67671,-0.52805,-91.20856],"object_pos_start":[5.23027,-0.48201,-75.05878],"object_to_goal_dist_end":91.55938,"object_to_goal_dist_start":75.41119,"object_z_max":-75.05878,"peak_contact_force":0.0,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":371.0,"raw_peak_contact_force":93.37263,"subtask_id":"release_1","tcp_end":[0.57005,0.15183,0.30393],"tcp_start":[0.57026,0.1516,0.27715],"tcp_to_object_dist_end":91.65738,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":34.0,"average_failure_rate":0.24286,"average_mean_iterations":52.15,"average_solve_count":140.0,"average_success_count":106.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.09192,"descend_1.grasp_z_offset":0.02862,"descend_2.descend_tolerance":0.0144,"lift_1.lift_height":0.20402,"transport_1.arc_height":0.11857,"transport_1.transport_speed":0.14751},"optimized_scores":{"best_composite_score":0.04361,"best_fitness_score":0.49361,"best_task_score":0.07904},"replay_outcomes":[{"contacts":{"omitted_contact_groups":11,"reported_contact_groups":[{"body_a":"world","body_b":"link7","contact_count":77.0,"contact_point_centroid":[0.79694,-0.01657,-4e-05],"force_p95":701.69267,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1671.59159,"mean_force":165.21849,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.88432,-0.07746,0.11944]},{"body_a":"world","body_b":"link6","contact_count":907.0,"contact_point_centroid":[0.67128,0.04388,-0.00029],"force_p95":360.33425,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1255.0431,"mean_force":270.96929,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.84605,-0.06994,0.17383]},{"body_a":"world","body_b":"hand","contact_count":113.0,"contact_point_centroid":[0.69746,0.02319,-0.00063],"force_p95":531.44658,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":888.32425,"mean_force":209.978,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.62894,-0.00871,0.00579]},{"body_a":"world","body_b":"link6","contact_count":968.0,"contact_point_centroid":[0.6931,0.04238,-0.00025],"force_p95":416.06025,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":857.65136,"mean_force":234.12895,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.6551,0.05962,0.28697]},{"body_a":"world","body_b":"link6","contact_count":29.0,"contact_point_centroid":[0.57995,0.17961,-0.00078],"force_p95":438.34571,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":464.43858,"mean_force":301.29046,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.69654,-0.03939,0.12177]},{"body_a":"world","body_b":"link7","contact_count":29.0,"contact_point_centroid":[0.6967,0.07708,-0.00054],"force_p95":337.18554,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":345.20196,"mean_force":227.51307,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.6759,-0.05141,0.08345]},{"body_a":"world","body_b":"link6","contact_count":81.0,"contact_point_centroid":[0.693,0.05448,-0.00011],"force_p95":90.8738,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":132.21314,"mean_force":52.88531,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60438,0.09652,0.27782]},{"body_a":"world","body_b":"link5","contact_count":349.0,"contact_point_centroid":[0.57204,-0.00918,-6e-05],"force_p95":83.18018,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":84.48625,"mean_force":77.01384,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.60872,0.08814,0.2792]},{"body_a":"world","body_b":"link5","contact_count":59.0,"contact_point_centroid":[0.57086,-0.00593,-1e-05],"force_p95":45.27194,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":47.31365,"mean_force":14.821,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60438,0.09653,0.27781]},{"body_a":"world","body_b":"right_finger","contact_count":903.0,"contact_point_centroid":[0.60852,0.03381,-0.01086],"force_p95":18.52668,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":22.32954,"mean_force":12.29304,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.62243,0.01924,-0.01133]},{"body_a":"world","body_b":"left_finger","contact_count":982.0,"contact_point_centroid":[0.63739,0.00421,-0.00935],"force_p95":15.02325,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":18.17005,"mean_force":9.79953,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.62254,0.01621,-0.01001]},{"body_a":"world","body_b":"grasp_target","contact_count":321.0,"contact_point_centroid":[0.5835,0.0017,-0.0071],"force_p95":2.19052,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.53428,"mean_force":0.74231,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.59702,0.01428,0.00686]},{"body_a":"world","body_b":"grasp_target","contact_count":4665.0,"contact_point_centroid":[0.77947,-0.15466,-0.0018],"force_p95":0.14648,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.78759,"mean_force":0.10896,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.84284,-0.06747,0.17915]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":437.0,"contact_point_centroid":[0.55088,-0.03268,0.04256],"force_p95":1.37673,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.70725,"mean_force":0.72033,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.54897,-0.01202,0.04406]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":554.0,"contact_point_centroid":[0.5976,-0.00637,0.02912],"force_p95":0.53196,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.9342,"mean_force":0.21862,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.60718,-0.01817,0.02071]},{"body_a":"grasp_target","body_b":"hand","contact_count":83.0,"contact_point_centroid":[0.60803,0.01719,0.05932],"force_p95":0.81096,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.84293,"mean_force":0.51636,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.63029,-0.02145,0.01463]}],"total_contact_groups":27},"final_pose_error":0.12527,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.77396,-0.15506,0.02658],"final_tcp_position":[0.60464,0.09627,0.27784],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":9748.05991,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":586.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2340.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.53822,-0.02709,0.12806],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.10233,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":205.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":820.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53943,-0.0287,0.06245],"tcp_start":[0.53822,-0.02709,0.12806],"tcp_to_object_dist_end":0.03696,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":31.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54563,-0.0291,0.02533],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26121,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.15396,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":8652.0,"raw_peak_contact_force":0.16991,"subtask_id":"grasp_1","tcp_end":[0.53085,-0.02848,0.05193],"tcp_start":[0.53943,-0.0287,0.06245],"tcp_to_object_dist_end":0.03043,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":240.0,"n_steps_budget":1000.0,"object_pos_end":[0.7062,-0.10144,0.11684],"object_pos_start":[0.54563,-0.0291,0.02533],"object_to_goal_dist_end":0.28274,"object_to_goal_dist_start":0.26121,"object_z_max":0.12653,"peak_contact_force":9748.05991,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":3499.0,"raw_peak_contact_force":888.32425,"tcp_end":[0.70098,-0.03867,0.13245],"tcp_start":[0.53085,-0.02848,0.05193],"tcp_to_object_dist_end":0.06489,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.77396,-0.15506,0.02658],"object_pos_start":[0.7062,-0.10144,0.11684],"object_to_goal_dist_end":0.38066,"object_to_goal_dist_start":0.28274,"object_z_max":0.11684,"peak_contact_force":0.01935,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":10028.0,"raw_peak_contact_force":1671.59159,"subtask_id":"transport_arc","tcp_end":[0.72191,0.00438,0.29123],"tcp_start":[0.70098,-0.03867,0.13245],"tcp_to_object_dist_end":0.31332,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":11.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.77396,-0.15506,0.02658],"object_pos_start":[0.77396,-0.15506,0.02658],"object_to_goal_dist_end":0.38066,"object_to_goal_dist_start":0.38066,"object_z_max":0.02658,"peak_contact_force":148.94473,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10520.0,"raw_peak_contact_force":857.65136,"subtask_id":"release_1","tcp_end":[0.60464,0.09627,0.27784],"tcp_start":[0.72191,0.00438,0.29123],"tcp_to_object_dist_end":0.39366,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.77396,-0.15506,0.02658],"object_pos_start":[0.77396,-0.15506,0.02658],"object_to_goal_dist_end":0.38066,"object_to_goal_dist_start":0.38066,"object_z_max":0.02658,"peak_contact_force":0.14487,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1357.0,"raw_peak_contact_force":132.21314,"subtask_id":"release_1","tcp_end":[0.60452,0.09611,0.30443],"tcp_start":[0.60464,0.09627,0.27784],"tcp_to_object_dist_end":0.41109,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```