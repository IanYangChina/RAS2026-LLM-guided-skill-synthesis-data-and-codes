## Search State

- **Seed**: 8
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → descend → contact → lift → approach → descend → release | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | 0.2318 | 0.17 | ❌ rejected |
| 4 | approach → descend → contact → lift → approach → descend | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.4199 | 0.23 | ❌ rejected |
| 3 | approach → descend → contact → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6 | 0.2086 | 0.21 | ❌ rejected |
| 2 | approach → descend → contact → lift → approach → descend → release → approach | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.2506 | 0.20 | ❌ rejected |
| 1 | approach → descend → contact → lift → approach → descend → release | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.2766 | 0.16 | ❌ rejected |

**Proposal policy**: task_score is 0.17 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.232) — your mutation base

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

- **Composite score**: 0.232
- **task_score** (E): 0.165
- **fitness_score**: 0.539  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.143
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.450

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1251 |
| descend_1 | 1.00 | 1.00 | 0.1291 |
| contact_1 | 1.00 | 1.00 | 0.0088 |
| lift_1 | 1.00 | 1.00 | 0.1051 |
| transport_1 | 0.00 | 1.00 | 0.0706 |
| descend_to_release | 1.00 | 1.00 | 0.1810 |
| release_gripper | 1.00 | 1.00 | 0.0211 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.516, -0.001, 0.183) | (0.522, -0.001, 0.030)→(0.522, -0.001, 0.026) | 0.287→0.289 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.516, -0.001, 0.183)→(0.517, -0.001, 0.054) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 4.000 | 0.123 | 0.123 |
| contact_1 | contact | 1.00 / force_exceeded | (0.517, -0.001, 0.054)→(0.511, -0.001, 0.048) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 42.000 | 0.142 | 0.186 |
| lift_1 | lift | 1.00 / step_budget | (0.511, -0.001, 0.048)→(0.503, -0.001, 0.152) | (0.522, -0.001, 0.026)→(0.509, -0.001, 0.120) | 0.289→0.247 | 1.00 / 19.667 | 0.132 | 0.419 |
| transport_1 | approach | 0.00 / step_budget | (0.503, -0.001, 0.152)→(0.514, 0.032, 0.214) | (0.509, -0.001, 0.120)→(0.527, 0.034, 0.016) | 0.247→0.271 | 1.00 / 8.667 | 0.123 | 1.676 |
| descend_to_release | descend | 1.00 / step_budget | (0.514, 0.032, 0.214)→(0.594, 0.191, 0.189) | (0.527, 0.034, 0.016)→(0.527, 0.034, 0.016) | 0.271→0.271 | 1.00 / 8.333 | 0.123 | 0.123 |
| release_gripper | release | 1.00 / step_budget | (0.594, 0.191, 0.189)→(0.589, 0.189, 0.209) | (0.527, 0.034, 0.016)→(0.527, 0.034, 0.016) | 0.271→0.271 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.195
- phase_score: 0.349
- phase_breakdown.approach_1_score: 0.095
- phase_breakdown.descend_1_score: 0.869
- phase_breakdown.transport_arc_score: 0.023
- phase_breakdown.release_1_score: 0.629
- phase_breakdown.grasp_1_score: 1.000
- grasp_place_fitness: 0.554

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.554
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.195
- **Median Q (composite search score)**: 0.229
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.265


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.64286,"average_solve_count":168.0,"average_success_count":168.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.16614,"contact_1.contact_force":11.27425,"descend_to_release.release_height_tolerance":0.02072,"lift_1.lift_height":0.13529,"transport_1.transport_arc_height":0.03753,"transport_1.transport_speed":0.05217},"optimized_scores":{"best_composite_score":0.22942,"best_fitness_score":0.53656,"best_task_score":0.16145},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3338.0,"contact_point_centroid":[0.48115,0.09213,-0.0023],"force_p95":0.12751,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.66236,"mean_force":0.13661,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.4799,0.07533,0.23389]},{"body_a":"world","body_b":"grasp_target","contact_count":139.0,"contact_point_centroid":[0.48018,0.04636,-0.00121],"force_p95":0.26157,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.40135,"mean_force":0.05572,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47152,0.04712,0.05006]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18339.0,"contact_point_centroid":[0.47064,0.06553,0.12024],"force_p95":0.10483,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29746,"mean_force":0.06375,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46838,0.04683,0.12]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16589.0,"contact_point_centroid":[0.47,0.02795,0.11677],"force_p95":0.13074,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29544,"mean_force":0.07026,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46849,0.04684,0.11729]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3915.0,"contact_point_centroid":[0.47158,0.03564,0.18249],"force_p95":0.13919,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25448,"mean_force":0.10755,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.46716,0.05377,0.1863]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4014.0,"contact_point_centroid":[0.47233,0.0722,0.18296],"force_p95":0.1333,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24616,"mean_force":0.10586,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.46745,0.05419,0.18747]},{"body_a":"world","body_b":"grasp_target","contact_count":1640.0,"contact_point_centroid":[0.48273,0.0486,-0.00213],"force_p95":0.15644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21253,"mean_force":0.13239,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47359,0.04733,0.04879]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4091.0,"contact_point_centroid":[0.47224,0.02806,0.04915],"force_p95":0.07978,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14677,"mean_force":0.05207,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.473,0.04727,0.04816]},{"body_a":"world","body_b":"grasp_target","contact_count":1312.0,"contact_point_centroid":[0.4827,0.04873,-0.0019],"force_p95":0.13564,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.123,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4903,0.02043,0.25202]},{"body_a":"world","body_b":"grasp_target","contact_count":1880.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.4788,0.04499,0.12863]},{"body_a":"world","body_b":"grasp_target","contact_count":3304.0,"contact_point_centroid":[0.48111,0.0922,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_release","phase_type":"descend","tcp_position_centroid":[0.54514,0.17877,0.22329]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.48111,0.0922,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_gripper","phase_type":"release","tcp_position_centroid":[0.56319,0.21111,0.21716]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4988.0,"contact_point_centroid":[0.4731,0.06639,0.0492],"force_p95":0.07307,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07423,"mean_force":0.04411,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47301,0.04727,0.04816]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3277.0,"contact_point_centroid":[0.48077,0.07614,0.23758],"force_p95":0.01105,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01636,"mean_force":0.01063,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.48033,0.07612,0.23534]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3557.0,"contact_point_centroid":[0.54597,0.17919,0.22546],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01285,"mean_force":0.01036,"phase_index":5.0,"phase_name":"descend_to_release","phase_type":"descend","tcp_position_centroid":[0.5454,0.17915,0.22323]},{"body_a":"left_finger","body_b":"right_finger","contact_count":218.0,"contact_point_centroid":[0.5661,0.21213,0.21553],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01264,"mean_force":0.01016,"phase_index":6.0,"phase_name":"release_gripper","phase_type":"release","tcp_position_centroid":[0.56542,0.21208,0.21313]}],"total_contact_groups":16},"final_pose_error":0.02044,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.48111,0.0922,0.01602],"final_tcp_position":[0.56979,0.21384,0.2237],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":1.66236,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":329.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1312.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.48167,0.04246,0.20372],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17781,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":470.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1880.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.47837,0.04776,0.05484],"tcp_start":[0.48167,0.04246,0.20372],"tcp_to_object_dist_end":0.02916,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":10.0,"n_steps_budget":600.0,"object_pos_end":[0.48266,0.04765,0.02557],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29098,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.153,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":10719.0,"raw_peak_contact_force":0.21253,"subtask_id":"grasp_1","tcp_end":[0.47298,0.04727,0.04813],"tcp_start":[0.47837,0.04776,0.05484],"tcp_to_object_dist_end":0.02456,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":15.0,"n_steps":783.0,"n_steps_budget":870.0,"object_pos_end":[0.47064,0.04769,0.13299],"object_pos_start":[0.48266,0.04765,0.02557],"object_to_goal_dist_end":0.23387,"object_to_goal_dist_start":0.29098,"object_z_max":0.14234,"peak_contact_force":0.13645,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":35067.0,"raw_peak_contact_force":0.40135,"tcp_end":[0.46558,0.04657,0.16696],"tcp_start":[0.47298,0.04727,0.04813],"tcp_to_object_dist_end":0.03436,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48111,0.0922,0.01602],"object_pos_start":[0.47064,0.04769,0.13299],"object_to_goal_dist_end":0.27354,"object_to_goal_dist_start":0.23387,"object_z_max":0.16603,"peak_contact_force":0.12263,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":14544.0,"raw_peak_contact_force":1.66236,"subtask_id":"transport_arc","tcp_end":[0.48087,0.07931,0.23888],"tcp_start":[0.46558,0.04657,0.16696],"tcp_to_object_dist_end":0.22324,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":426.0,"n_steps_budget":1000.0,"object_pos_end":[0.48111,0.0922,0.01602],"object_pos_start":[0.48111,0.0922,0.01602],"object_to_goal_dist_end":0.27354,"object_to_goal_dist_start":0.27354,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_release","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":6861.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.56655,0.21252,0.21581],"tcp_start":[0.48087,0.07931,0.23888],"tcp_to_object_dist_end":0.24839,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48111,0.0922,0.01602],"object_pos_start":[0.48111,0.0922,0.01602],"object_to_goal_dist_end":0.27354,"object_to_goal_dist_start":0.27354,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_gripper","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1018.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.56194,0.21054,0.23699],"tcp_start":[0.56655,0.21252,0.21581],"tcp_to_object_dist_end":0.26338,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.70909,"average_solve_count":165.0,"average_success_count":165.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.16345,"contact_1.contact_force":11.37781,"descend_to_release.release_height_tolerance":0.02358,"lift_1.lift_height":0.11572,"transport_1.transport_arc_height":0.04598,"transport_1.transport_speed":0.04514},"optimized_scores":{"best_composite_score":0.21893,"best_fitness_score":0.52607,"best_task_score":0.13977},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1569.0,"contact_point_centroid":[0.54555,0.01249,-0.00271],"force_p95":0.28184,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.73952,"mean_force":0.15534,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52407,0.01382,0.20308]},{"body_a":"world","body_b":"grasp_target","contact_count":147.0,"contact_point_centroid":[0.53473,-0.02059,-0.00115],"force_p95":0.30952,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.44835,"mean_force":0.06719,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52438,-0.02087,0.04856]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15643.0,"contact_point_centroid":[0.5232,-0.00186,0.10855],"force_p95":0.10351,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2965,"mean_force":0.06781,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52084,-0.02078,0.10811]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18013.0,"contact_point_centroid":[0.52279,-0.03961,0.10964],"force_p95":0.09528,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2936,"mean_force":0.05903,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52074,-0.02078,0.10928]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8061.0,"contact_point_centroid":[0.52498,0.01295,0.16992],"force_p95":0.13251,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2352,"mean_force":0.10184,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51991,-0.00536,0.17344]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9113.0,"contact_point_centroid":[0.52476,-0.02396,0.16953],"force_p95":0.12601,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23042,"mean_force":0.09015,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51976,-0.00586,0.17237]},{"body_a":"world","body_b":"grasp_target","contact_count":1632.0,"contact_point_centroid":[0.53703,-0.02131,-0.00205],"force_p95":0.1362,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16538,"mean_force":0.12663,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52663,-0.02091,0.0476]},{"body_a":"world","body_b":"grasp_target","contact_count":1428.0,"contact_point_centroid":[0.53702,-0.02132,-0.00191],"force_p95":0.13543,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12297,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51353,-0.0092,0.24929]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4668.0,"contact_point_centroid":[0.52582,-0.00172,0.04752],"force_p95":0.06962,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12528,"mean_force":0.04649,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52602,-0.0209,0.04687]},{"body_a":"world","body_b":"grasp_target","contact_count":1752.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52934,-0.01989,0.12622]},{"body_a":"world","body_b":"grasp_target","contact_count":3532.0,"contact_point_centroid":[0.54558,0.01258,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_to_release","phase_type":"descend","tcp_position_centroid":[0.57723,0.15504,0.19506]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.54558,0.01258,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_gripper","phase_type":"release","tcp_position_centroid":[0.59274,0.20564,0.19069]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4888.0,"contact_point_centroid":[0.52618,-0.04008,0.04831],"force_p95":0.0694,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08772,"mean_force":0.04457,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52602,-0.0209,0.04687]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1433.0,"contact_point_centroid":[0.5241,0.0138,0.20493],"force_p95":0.01211,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01616,"mean_force":0.01075,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52381,0.0138,0.20264]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3756.0,"contact_point_centroid":[0.57758,0.15448,0.19734],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01293,"mean_force":0.01048,"phase_index":5.0,"phase_name":"descend_to_release","phase_type":"descend","tcp_position_centroid":[0.57702,0.15447,0.19509]},{"body_a":"left_finger","body_b":"right_finger","contact_count":219.0,"contact_point_centroid":[0.59585,0.20666,0.18923],"force_p95":0.01105,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01272,"mean_force":0.0102,"phase_index":6.0,"phase_name":"release_gripper","phase_type":"release","tcp_position_centroid":[0.59525,0.20664,0.18717]}],"total_contact_groups":16},"final_pose_error":0.02355,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.54558,0.01258,0.01602],"final_tcp_position":[0.60008,0.20844,0.19865],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":1.73952,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":358.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1428.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52952,-0.01886,0.19933],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17349,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":438.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1752.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53173,-0.02099,0.05443],"tcp_start":[0.52952,-0.01886,0.19933],"tcp_to_object_dist_end":0.0289,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":8.0,"n_steps_budget":600.0,"object_pos_end":[0.53695,-0.02104,0.02582],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31663,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13575,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":11188.0,"raw_peak_contact_force":0.16538,"subtask_id":"grasp_1","tcp_end":[0.52599,-0.0209,0.04683],"tcp_start":[0.53173,-0.02099,0.05443],"tcp_to_object_dist_end":0.0237,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":663.0,"n_steps_budget":750.0,"object_pos_end":[0.52413,-0.02106,0.11375],"object_pos_start":[0.53695,-0.02104,0.02582],"object_to_goal_dist_end":0.27948,"object_to_goal_dist_start":0.31663,"object_z_max":0.12354,"peak_contact_force":0.13057,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":33803.0,"raw_peak_contact_force":0.44835,"tcp_end":[0.51783,-0.02071,0.1442],"tcp_start":[0.52599,-0.0209,0.04683],"tcp_to_object_dist_end":0.03109,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54558,0.01258,0.01602],"object_pos_start":[0.52413,-0.02106,0.11375],"object_to_goal_dist_end":0.29516,"object_to_goal_dist_start":0.27948,"object_z_max":0.16402,"peak_contact_force":0.12263,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":20176.0,"raw_peak_contact_force":1.73952,"subtask_id":"transport_arc","tcp_end":[0.52366,0.01379,0.20238],"tcp_start":[0.51783,-0.02071,0.1442],"tcp_to_object_dist_end":0.18765,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":483.0,"n_steps_budget":1000.0,"object_pos_end":[0.54558,0.01258,0.01602],"object_pos_start":[0.54558,0.01258,0.01602],"object_to_goal_dist_end":0.29516,"object_to_goal_dist_start":0.29516,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_release","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7288.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.5965,0.20709,0.19008],"tcp_start":[0.52366,0.01379,0.20238],"tcp_to_object_dist_end":0.26594,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54558,0.01258,0.01602],"object_pos_start":[0.54558,0.01258,0.01602],"object_to_goal_dist_end":0.29516,"object_to_goal_dist_start":0.29516,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_gripper","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1019.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.59131,0.20505,0.21019],"tcp_start":[0.5965,0.20709,0.19008],"tcp_to_object_dist_end":0.27719,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.75333,"average_solve_count":150.0,"average_success_count":150.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.1114,"contact_1.contact_force":6.76984,"descend_to_release.release_height_tolerance":0.01487,"lift_1.lift_height":0.11712,"transport_1.transport_arc_height":0.0364,"transport_1.transport_speed":0.05865},"optimized_scores":{"best_composite_score":0.24694,"best_fitness_score":0.55408,"best_task_score":0.19504},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2266.0,"contact_point_centroid":[0.55504,-0.00311,-0.00245],"force_p95":0.1505,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.62477,"mean_force":0.14608,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.5382,0.00333,0.20043]},{"body_a":"world","body_b":"grasp_target","contact_count":149.0,"contact_point_centroid":[0.54314,-0.02834,-0.00118],"force_p95":0.28135,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.40609,"mean_force":0.06442,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53313,-0.02854,0.04949]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15168.0,"contact_point_centroid":[0.53181,-0.00948,0.1086],"force_p95":0.12621,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30029,"mean_force":0.07016,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52967,-0.02841,0.10859]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17981.0,"contact_point_centroid":[0.53137,-0.04714,0.11064],"force_p95":0.0989,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29472,"mean_force":0.05914,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52953,-0.02841,0.11061]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6897.0,"contact_point_centroid":[0.53445,-0.03415,0.1653],"force_p95":0.1274,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24527,"mean_force":0.09587,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52965,-0.01604,0.16897]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6269.0,"contact_point_centroid":[0.53483,0.00222,0.16509],"force_p95":0.12691,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2242,"mean_force":0.10451,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52962,-0.01599,0.16907]},{"body_a":"world","body_b":"grasp_target","contact_count":1604.0,"contact_point_centroid":[0.54561,-0.02916,-0.00207],"force_p95":0.14047,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1803,"mean_force":0.12804,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53532,-0.02861,0.04841]},{"body_a":"world","body_b":"grasp_target","contact_count":2108.0,"contact_point_centroid":[0.5456,-0.02923,-0.00193],"force_p95":0.13221,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12286,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5179,-0.01326,0.22283]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4109.0,"contact_point_centroid":[0.53576,-0.00938,0.04889],"force_p95":0.07786,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13578,"mean_force":0.05211,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.5348,-0.02859,0.04779]},{"body_a":"world","body_b":"grasp_target","contact_count":1140.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53781,-0.02775,0.10044]},{"body_a":"world","body_b":"grasp_target","contact_count":4424.0,"contact_point_centroid":[0.55506,-0.00293,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_to_release","phase_type":"descend","tcp_position_centroid":[0.59535,0.10887,0.17419]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.55506,-0.00293,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_gripper","phase_type":"release","tcp_position_centroid":[0.61577,0.15336,0.16094]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4903.0,"contact_point_centroid":[0.53493,-0.04766,0.04895],"force_p95":0.06913,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08662,"mean_force":0.0444,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.5348,-0.02859,0.04779]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2176.0,"contact_point_centroid":[0.53854,0.00375,0.20299],"force_p95":0.01157,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01569,"mean_force":0.01064,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53821,0.00375,0.20069]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4701.0,"contact_point_centroid":[0.59576,0.10881,0.17647],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01281,"mean_force":0.01048,"phase_index":5.0,"phase_name":"descend_to_release","phase_type":"descend","tcp_position_centroid":[0.59531,0.10881,0.17421]},{"body_a":"left_finger","body_b":"right_finger","contact_count":220.0,"contact_point_centroid":[0.61908,0.1542,0.15969],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01103,"mean_force":0.01015,"phase_index":6.0,"phase_name":"release_gripper","phase_type":"release","tcp_position_centroid":[0.61866,0.15418,0.15756]}],"total_contact_groups":16},"final_pose_error":0.0148,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.55506,-0.00293,0.01602],"final_tcp_position":[0.62414,0.15568,0.16933],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":1.62477,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":528.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2108.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.53823,-0.02686,0.14742],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12165,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":285.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1140.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53989,-0.02875,0.05407],"tcp_start":[0.53823,-0.02686,0.14742],"tcp_to_object_dist_end":0.02863,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.54554,-0.02872,0.02576],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26071,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.13873,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":10616.0,"raw_peak_contact_force":0.1803,"subtask_id":"grasp_1","tcp_end":[0.53477,-0.02859,0.04775],"tcp_start":[0.53989,-0.02875,0.05407],"tcp_to_object_dist_end":0.02448,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":20.0,"n_steps":663.0,"n_steps_budget":750.0,"object_pos_end":[0.53219,-0.02942,0.11396],"object_pos_start":[0.54554,-0.02872,0.02576],"object_to_goal_dist_end":0.22774,"object_to_goal_dist_start":0.26071,"object_z_max":0.12461,"peak_contact_force":0.12824,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":33298.0,"raw_peak_contact_force":0.40609,"tcp_end":[0.52658,-0.0283,0.14605],"tcp_start":[0.53477,-0.02859,0.04775],"tcp_to_object_dist_end":0.03259,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55506,-0.00293,0.01602],"object_pos_start":[0.53219,-0.02942,0.11396],"object_to_goal_dist_end":0.24519,"object_to_goal_dist_start":0.22774,"object_z_max":0.1518,"peak_contact_force":0.12263,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":17608.0,"raw_peak_contact_force":1.62477,"subtask_id":"transport_arc","tcp_end":[0.53728,0.00415,0.19931],"tcp_start":[0.52658,-0.0283,0.14605],"tcp_to_object_dist_end":0.18429,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":706.0,"n_steps_budget":1000.0,"object_pos_end":[0.55506,-0.00293,0.01602],"object_pos_start":[0.55506,-0.00293,0.01602],"object_to_goal_dist_end":0.24519,"object_to_goal_dist_start":0.24519,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_release","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9125.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.62007,0.15456,0.16054],"tcp_start":[0.53728,0.00415,0.19931],"tcp_to_object_dist_end":0.22342,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.55506,-0.00293,0.01602],"object_pos_start":[0.55506,-0.00293,0.01602],"object_to_goal_dist_end":0.24519,"object_to_goal_dist_start":0.24519,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_gripper","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1020.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.6141,0.15286,0.18034],"tcp_start":[0.62007,0.15456,0.16054],"tcp_to_object_dist_end":0.234,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```