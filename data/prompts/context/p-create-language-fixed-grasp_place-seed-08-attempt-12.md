## Search State

- **Seed**: 8
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → contact → lift → approach → descend → release | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.3310 | 0.26 | ✅ accepted |
| 11 | approach → descend → contact → lift → approach → descend → release | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | force_threshold_switch | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | 0.2594 | 0.22 | ❌ rejected |
| 10 | approach → descend → contact → lift → approach → descend | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.4248 | 0.24 | ❌ rejected |
| 9 | approach → descend → contact → lift → approach → descend | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.3303 | 0.15 | ❌ rejected |
| 8 | approach → descend → contact → lift → approach → descend | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.4211 | 0.24 | ❌ rejected |

**Proposal policy**: task_score is 0.26 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.331) — your mutation base

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
    - 0.05
    orientation:
      mode: keep_current
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: transport_arc
- id: descend_to_goal
  type: descend
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
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: release_1
- id: release_grasp
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
    orientation:
      mode: keep_current

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
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.05]
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_goal** (`descend`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **release_grasp** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.331
- **task_score** (E): 0.264
- **fitness_score**: 0.588  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.143
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.400

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0893 |
| descend_1 | 1.00 | 1.00 | 0.1741 |
| contact_1 | 1.00 | 1.00 | 0.0096 |
| lift_1 | 1.00 | 1.00 | 0.1098 |
| transport_1 | 0.00 | 1.00 | 0.1236 |
| descend_to_goal | 0.67 | 1.00 | 0.0792 |
| release_grasp | 1.00 | 1.00 | 0.0215 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.517, -0.001, 0.229) | (0.522, -0.001, 0.030)→(0.522, -0.001, 0.026) | 0.287→0.289 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.517, -0.001, 0.229)→(0.517, -0.001, 0.055) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 4.000 | 0.123 | 0.123 |
| contact_1 | contact | 1.00 / force_exceeded | (0.517, -0.001, 0.055)→(0.511, -0.001, 0.047) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 45.000 | 0.142 | 0.187 |
| lift_1 | lift | 1.00 / step_budget | (0.511, -0.001, 0.047)→(0.507, -0.001, 0.157) | (0.522, -0.001, 0.026)→(0.518, -0.001, 0.129) | 0.289→0.242 | 1.00 / 25.000 | 0.107 | 0.442 |
| transport_1 | approach | 0.00 / step_budget | (0.507, -0.001, 0.157)→(0.556, 0.101, 0.202) | (0.518, -0.001, 0.129)→(0.559, 0.105, 0.108) | 0.242→0.170 | 1.00 / 14.667 | 0.118 | 0.649 |
| descend_to_goal | descend | 0.67 / step_budget | (0.556, 0.101, 0.202)→(0.589, 0.172, 0.196) | (0.559, 0.105, 0.108)→(0.580, 0.145, 0.016) | 0.170→0.202 | 1.00 / 8.000 | 0.123 | 1.087 |
| release_grasp | release | 1.00 / step_budget | (0.589, 0.172, 0.196)→(0.584, 0.171, 0.217) | (0.580, 0.145, 0.016)→(0.580, 0.145, 0.016) | 0.202→0.202 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.322
- phase_score: 0.353
- phase_breakdown.approach_1_score: 0.006
- phase_breakdown.descend_1_score: 0.872
- phase_breakdown.transport_arc_score: 0.095
- phase_breakdown.release_1_score: 0.423
- phase_breakdown.grasp_1_score: 1.000
- grasp_place_fitness: 0.617

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.617
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.322
- **Median Q (composite search score)**: 0.324
- **K-run variance**: 0.0004
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.295


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.67568,"average_solve_count":148.0,"average_success_count":148.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.17604,"contact_1.contact_force":19.21067,"descend_to_goal.descend_speed":0.03882,"lift_1.lift_height":0.10678,"transport_1.transport_speed":0.19505},"optimized_scores":{"best_composite_score":0.3098,"best_fitness_score":0.56694,"best_task_score":0.22213},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":653.0,"contact_point_centroid":[0.53785,0.17399,-0.00348],"force_p95":0.75381,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.61504,"mean_force":0.19604,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.5325,0.15336,0.21778]},{"body_a":"world","body_b":"grasp_target","contact_count":139.0,"contact_point_centroid":[0.48017,0.04636,-0.0012],"force_p95":0.26184,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.40178,"mean_force":0.05544,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47154,0.04712,0.05005]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11435.0,"contact_point_centroid":[0.47003,0.06594,0.09431],"force_p95":0.08747,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29756,"mean_force":0.05571,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46913,0.04689,0.09349]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11015.0,"contact_point_centroid":[0.46933,0.02783,0.09427],"force_p95":0.08974,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29571,"mean_force":0.05736,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4691,0.04689,0.09399]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6906.0,"contact_point_centroid":[0.49754,0.07174,0.16832],"force_p95":0.1344,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24665,"mean_force":0.09891,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.49305,0.09011,0.17141]},{"body_a":"world","body_b":"grasp_target","contact_count":1640.0,"contact_point_centroid":[0.48273,0.0486,-0.00213],"force_p95":0.15648,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21259,"mean_force":0.1324,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47361,0.04733,0.04877]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7715.0,"contact_point_centroid":[0.49678,0.10656,0.16803],"force_p95":0.12973,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21243,"mean_force":0.08899,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.49199,0.08842,0.17016]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4091.0,"contact_point_centroid":[0.47227,0.02806,0.04913],"force_p95":0.07979,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14677,"mean_force":0.05207,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47302,0.04727,0.04814]},{"body_a":"world","body_b":"grasp_target","contact_count":1208.0,"contact_point_centroid":[0.4827,0.04873,-0.00189],"force_p95":0.13606,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12303,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49048,0.02014,0.25683]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.53765,0.17429,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12293,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.55924,0.19794,0.22067]},{"body_a":"world","body_b":"grasp_target","contact_count":1996.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47894,0.04478,0.13328]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.53765,0.17429,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_grasp","phase_type":"release","tcp_position_centroid":[0.57323,0.22276,0.22307]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4988.0,"contact_point_centroid":[0.47312,0.06638,0.04918],"force_p95":0.07308,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07423,"mean_force":0.04411,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47303,0.04727,0.04814]},{"body_a":"left_finger","body_b":"right_finger","contact_count":440.0,"contact_point_centroid":[0.53499,0.15662,0.22251],"force_p95":0.01328,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01649,"mean_force":0.01115,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53455,0.15661,0.22018]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4300.0,"contact_point_centroid":[0.55968,0.19797,0.22296],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01273,"mean_force":0.01038,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.55924,0.19794,0.22068]},{"body_a":"left_finger","body_b":"right_finger","contact_count":225.0,"contact_point_centroid":[0.57594,0.22381,0.2217],"force_p95":0.01094,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01096,"mean_force":0.00996,"phase_index":6.0,"phase_name":"release_grasp","phase_type":"release","tcp_position_centroid":[0.57539,0.22378,0.21923]}],"total_contact_groups":16},"final_pose_error":0.01105,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.53765,0.17429,0.01602],"final_tcp_position":[0.57651,0.22415,0.22205],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":1.61504,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":303.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1208.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.48191,0.04203,0.21323],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.18734,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":499.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1996.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.47839,0.04776,0.05481],"tcp_start":[0.48191,0.04203,0.21323],"tcp_to_object_dist_end":0.02913,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":10.0,"n_steps_budget":600.0,"object_pos_end":[0.48266,0.04765,0.02556],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29098,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.15303,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":10719.0,"raw_peak_contact_force":0.21259,"subtask_id":"grasp_1","tcp_end":[0.473,0.04727,0.04811],"tcp_start":[0.47839,0.04776,0.05481],"tcp_to_object_dist_end":0.02453,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":603.0,"n_steps_budget":690.0,"object_pos_end":[0.47928,0.04749,0.11554],"object_pos_start":[0.48266,0.04765,0.02556],"object_to_goal_dist_end":0.23797,"object_to_goal_dist_start":0.29098,"object_z_max":0.11543,"peak_contact_force":0.11946,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":22589.0,"raw_peak_contact_force":0.40178,"tcp_end":[0.46918,0.0469,0.14346],"tcp_start":[0.473,0.04727,0.04811],"tcp_to_object_dist_end":0.0297,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53765,0.17429,0.01601],"object_pos_start":[0.47928,0.04749,0.11554],"object_to_goal_dist_end":0.22568,"object_to_goal_dist_start":0.23797,"object_z_max":0.16416,"peak_contact_force":0.12295,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":15714.0,"raw_peak_contact_force":1.61504,"subtask_id":"transport_arc","tcp_end":[0.53836,0.16273,0.22466],"tcp_start":[0.46918,0.0469,0.14346],"tcp_to_object_dist_end":0.20897,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53765,0.17429,0.01602],"object_pos_start":[0.53765,0.17429,0.01601],"object_to_goal_dist_end":0.22567,"object_to_goal_dist_start":0.22568,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8300.0,"raw_peak_contact_force":0.12293,"subtask_id":"release_1","tcp_end":[0.57651,0.22415,0.22205],"tcp_start":[0.53836,0.16273,0.22466],"tcp_to_object_dist_end":0.21551,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53765,0.17429,0.01602],"object_pos_start":[0.53765,0.17429,0.01602],"object_to_goal_dist_end":0.22567,"object_to_goal_dist_start":0.22567,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_grasp","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1025.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57202,0.22217,0.24276],"tcp_start":[0.57651,0.22415,0.22205],"tcp_to_object_dist_end":0.23428,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.73103,"average_solve_count":145.0,"average_success_count":145.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.14923,"contact_1.contact_force":11.27962,"descend_to_goal.descend_speed":0.06776,"lift_1.lift_height":0.12736,"transport_1.transport_speed":0.09408},"optimized_scores":{"best_composite_score":0.32355,"best_fitness_score":0.58069,"best_task_score":0.2484},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2082.0,"contact_point_centroid":[0.58935,0.14576,-0.00245],"force_p95":0.16285,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.62485,"mean_force":0.14966,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.57568,0.14504,0.19197]},{"body_a":"world","body_b":"grasp_target","contact_count":144.0,"contact_point_centroid":[0.53451,-0.02063,-0.00114],"force_p95":0.33226,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.4517,"mean_force":0.0687,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52431,-0.02087,0.04814]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11889.0,"contact_point_centroid":[0.52335,-0.00177,0.09831],"force_p95":0.10184,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27089,"mean_force":0.06219,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52173,-0.02081,0.09729]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13345.0,"contact_point_centroid":[0.52327,-0.03977,0.09791],"force_p95":0.09418,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27066,"mean_force":0.05616,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52174,-0.02081,0.0968]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3276.0,"contact_point_centroid":[0.56445,0.08136,0.18471],"force_p95":0.12457,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2026,"mean_force":0.10048,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.55877,0.09955,0.18911]},{"body_a":"world","body_b":"grasp_target","contact_count":1636.0,"contact_point_centroid":[0.53703,-0.02128,-0.00205],"force_p95":0.13547,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17099,"mean_force":0.12654,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52655,-0.02092,0.04719]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11264.0,"contact_point_centroid":[0.5416,0.01117,0.17384],"force_p95":0.11552,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16865,"mean_force":0.08154,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53638,0.02964,0.17481]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10939.0,"contact_point_centroid":[0.54139,0.04778,0.17351],"force_p95":0.11986,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16798,"mean_force":0.08395,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53625,0.02926,0.17468]},{"body_a":"world","body_b":"grasp_target","contact_count":1580.0,"contact_point_centroid":[0.53702,-0.02132,-0.00191],"force_p95":0.13468,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12294,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51364,-0.00931,0.24238]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3249.0,"contact_point_centroid":[0.56476,0.11854,0.18462],"force_p95":0.12208,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1309,"mean_force":0.1002,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.55909,0.10042,0.18915]},{"body_a":"world","body_b":"grasp_target","contact_count":1592.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52942,-0.02,0.11926]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.58957,0.14663,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_grasp","phase_type":"release","tcp_position_centroid":[0.57882,0.16207,0.19482]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4845.0,"contact_point_centroid":[0.52544,-0.00166,0.04711],"force_p95":0.06797,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09805,"mean_force":0.04504,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52593,-0.0209,0.04644]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5376.0,"contact_point_centroid":[0.52526,-0.04011,0.04741],"force_p95":0.06416,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08198,"mean_force":0.04096,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52593,-0.0209,0.04644]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2058.0,"contact_point_centroid":[0.57666,0.14654,0.19441],"force_p95":0.01156,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01634,"mean_force":0.01059,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.57625,0.14653,0.19209]},{"body_a":"left_finger","body_b":"right_finger","contact_count":222.0,"contact_point_centroid":[0.58184,0.16292,0.19315],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01098,"mean_force":0.01006,"phase_index":6.0,"phase_name":"release_grasp","phase_type":"release","tcp_position_centroid":[0.58132,0.16291,0.19072]}],"total_contact_groups":16},"final_pose_error":0.0717,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.58957,0.14663,0.01602],"final_tcp_position":[0.58263,0.1631,0.19346],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":1.62485,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":396.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1580.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52976,-0.01907,0.18549],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15965,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":398.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1592.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53168,-0.021,0.0542],"tcp_start":[0.52976,-0.01907,0.18549],"tcp_to_object_dist_end":0.02868,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":9.0,"n_steps_budget":600.0,"object_pos_end":[0.53695,-0.021,0.02582],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.3166,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13486,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":11857.0,"raw_peak_contact_force":0.17099,"subtask_id":"grasp_1","tcp_end":[0.5259,-0.0209,0.04641],"tcp_start":[0.53168,-0.021,0.0542],"tcp_to_object_dist_end":0.02336,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":723.0,"n_steps_budget":810.0,"object_pos_end":[0.53298,-0.02099,0.13445],"object_pos_start":[0.53695,-0.021,0.02582],"object_to_goal_dist_end":0.27051,"object_to_goal_dist_start":0.3166,"object_z_max":0.13433,"peak_contact_force":0.10266,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":25378.0,"raw_peak_contact_force":0.4517,"tcp_end":[0.52199,-0.02081,0.16121],"tcp_start":[0.5259,-0.0209,0.04641],"tcp_to_object_dist_end":0.02894,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55905,0.07868,0.15758],"object_pos_start":[0.53298,-0.02099,0.13445],"object_to_goal_dist_end":0.16533,"object_to_goal_dist_start":0.27051,"object_z_max":0.15756,"peak_contact_force":0.11708,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":22203.0,"raw_peak_contact_force":0.16865,"subtask_id":"transport_arc","tcp_end":[0.55387,0.07884,0.19311],"tcp_start":[0.52199,-0.02081,0.16121],"tcp_to_object_dist_end":0.03591,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58957,0.14663,0.01602],"object_pos_start":[0.55905,0.07868,0.15758],"object_to_goal_dist_end":0.20891,"object_to_goal_dist_start":0.16533,"object_z_max":0.15758,"peak_contact_force":0.12263,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10665.0,"raw_peak_contact_force":1.62485,"subtask_id":"release_1","tcp_end":[0.58263,0.1631,0.19346],"tcp_start":[0.55387,0.07884,0.19311],"tcp_to_object_dist_end":0.17833,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58957,0.14663,0.01602],"object_pos_start":[0.58957,0.14663,0.01602],"object_to_goal_dist_end":0.20891,"object_to_goal_dist_start":0.20891,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_grasp","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1022.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57738,0.16158,0.21467],"tcp_start":[0.58263,0.1631,0.19346],"tcp_to_object_dist_end":0.19959,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.525,"average_solve_count":160.0,"average_success_count":160.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.26258,"contact_1.contact_force":8.51454,"descend_to_goal.descend_speed":0.04934,"lift_1.lift_height":0.13172,"transport_1.transport_speed":0.10672},"optimized_scores":{"best_composite_score":0.35973,"best_fitness_score":0.61687,"best_task_score":0.32153},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2468.0,"contact_point_centroid":[0.61146,0.11369,-0.00233],"force_p95":0.14774,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.51262,"mean_force":0.14178,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.60042,0.11358,0.17391]},{"body_a":"world","body_b":"grasp_target","contact_count":148.0,"contact_point_centroid":[0.54314,-0.02827,-0.00117],"force_p95":0.32002,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.47154,"mean_force":0.07097,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53286,-0.02866,0.04774]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12362.0,"contact_point_centroid":[0.53194,-0.00953,0.09966],"force_p95":0.10236,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26886,"mean_force":0.06212,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53028,-0.02857,0.0985]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13843.0,"contact_point_centroid":[0.53196,-0.04753,0.0987],"force_p95":0.09452,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26755,"mean_force":0.05636,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5303,-0.02857,0.09737]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2601.0,"contact_point_centroid":[0.58719,0.06037,0.175],"force_p95":0.13372,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21067,"mean_force":0.10379,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.58122,0.07857,0.1792]},{"body_a":"world","body_b":"grasp_target","contact_count":1644.0,"contact_point_centroid":[0.5456,-0.02917,-0.00206],"force_p95":0.13871,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17888,"mean_force":0.12733,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53518,-0.02874,0.04686]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11325.0,"contact_point_centroid":[0.55748,0.00032,0.17296],"force_p95":0.11454,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1642,"mean_force":0.08116,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55206,0.0188,0.1739]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11086.0,"contact_point_centroid":[0.55714,0.03701,0.17265],"force_p95":0.11696,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15951,"mean_force":0.08309,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55189,0.01848,0.17381]},{"body_a":"world","body_b":"grasp_target","contact_count":1356.0,"contact_point_centroid":[0.5456,-0.02923,-0.0019],"force_p95":0.13561,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12299,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51934,-0.01383,0.29172]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2734.0,"contact_point_centroid":[0.58717,0.09703,0.17481],"force_p95":0.12105,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12935,"mean_force":0.09757,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.5814,0.07893,0.17912]},{"body_a":"world","body_b":"grasp_target","contact_count":2736.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53822,-0.02741,0.1696]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.61158,0.11368,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_grasp","phase_type":"release","tcp_position_centroid":[0.60513,0.12835,0.17293]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4842.0,"contact_point_centroid":[0.53403,-0.00941,0.04678],"force_p95":0.06945,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10311,"mean_force":0.04527,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53452,-0.02871,0.04605]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5875.0,"contact_point_centroid":[0.53451,-0.04791,0.04785],"force_p95":0.06134,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07713,"mean_force":0.0377,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53453,-0.02871,0.04605]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2334.0,"contact_point_centroid":[0.60182,0.1155,0.17601],"force_p95":0.0113,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01762,"mean_force":0.01061,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.6015,0.11549,0.17368]},{"body_a":"left_finger","body_b":"right_finger","contact_count":225.0,"contact_point_centroid":[0.60819,0.12907,0.17136],"force_p95":0.01103,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01258,"mean_force":0.00997,"phase_index":6.0,"phase_name":"release_grasp","phase_type":"release","tcp_position_centroid":[0.6079,0.12906,0.16916]}],"total_contact_groups":16},"final_pose_error":0.043,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.61158,0.11368,0.01602],"final_tcp_position":[0.60931,0.12927,0.17206],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":1.51262,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":340.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1356.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.53797,-0.02602,0.28704],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.26115,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":684.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2736.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.54049,-0.02889,0.05452],"tcp_start":[0.53797,-0.02602,0.28704],"tcp_to_object_dist_end":0.02896,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":48.0,"n_steps":11.0,"n_steps_budget":600.0,"object_pos_end":[0.54552,-0.02879,0.02578],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26076,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.13848,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":12361.0,"raw_peak_contact_force":0.17888,"subtask_id":"grasp_1","tcp_end":[0.5345,-0.02871,0.04601],"tcp_start":[0.54049,-0.02889,0.05452],"tcp_to_object_dist_end":0.02304,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":753.0,"n_steps_budget":840.0,"object_pos_end":[0.54162,-0.0288,0.13833],"object_pos_start":[0.54552,-0.02879,0.02578],"object_to_goal_dist_end":0.21758,"object_to_goal_dist_start":0.26076,"object_z_max":0.13822,"peak_contact_force":0.10027,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":26353.0,"raw_peak_contact_force":0.47154,"tcp_end":[0.53059,-0.02857,0.16501],"tcp_start":[0.5345,-0.02871,0.04601],"tcp_to_object_dist_end":0.02886,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5804,0.06258,0.15166],"object_pos_start":[0.54162,-0.0288,0.13833],"object_to_goal_dist_end":0.11775,"object_to_goal_dist_start":0.21758,"object_z_max":0.15166,"peak_contact_force":0.11462,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":22411.0,"raw_peak_contact_force":0.1642,"subtask_id":"transport_arc","tcp_end":[0.57521,0.0627,0.18704],"tcp_start":[0.53059,-0.02857,0.16501],"tcp_to_object_dist_end":0.03576,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.61158,0.11368,0.01602],"object_pos_start":[0.5804,0.06258,0.15166],"object_to_goal_dist_end":0.1702,"object_to_goal_dist_start":0.11775,"object_z_max":0.15166,"peak_contact_force":0.12263,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10137.0,"raw_peak_contact_force":1.51262,"subtask_id":"release_1","tcp_end":[0.60931,0.12927,0.17206],"tcp_start":[0.57521,0.0627,0.18704],"tcp_to_object_dist_end":0.15683,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61158,0.11368,0.01602],"object_pos_start":[0.61158,0.11368,0.01602],"object_to_goal_dist_end":0.1702,"object_to_goal_dist_start":0.1702,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_grasp","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1025.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.60351,0.12793,0.19256],"tcp_start":[0.60931,0.12927,0.17206],"tcp_to_object_dist_end":0.1773,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```