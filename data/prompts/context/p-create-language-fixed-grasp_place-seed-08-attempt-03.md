## Search State

- **Seed**: 8
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → descend → contact → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6 | 0.2086 | 0.21 | ❌ rejected |
| 2 | approach → descend → contact → lift → approach → descend → release → approach | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.2506 | 0.20 | ❌ rejected |
| 1 | approach → descend → contact → lift → approach → descend → release | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.2766 | 0.16 | ❌ rejected |
| 0 | approach → descend → contact → lift → approach → descend | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.4299 | 0.25 | ✅ accepted |

**Proposal policy**: task_score is 0.21 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.209) — your mutation base

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

- **Composite score**: 0.209
- **task_score** (E): 0.215
- **fitness_score**: 0.564  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.125
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.480

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0965 |
| descend_1 | 1.00 | 1.00 | 0.1622 |
| contact_grasp | 1.00 | 1.00 | 0.0096 |
| lift_1 | 1.00 | 1.00 | 0.1061 |
| transport_arc | 0.00 | 1.00 | 0.0741 |
| descend_place | 0.33 | 1.00 | 0.1227 |
| release_1 | 1.00 | 1.00 | 0.0221 |
| retract_1 | 1.00 | 1.00 | 0.1357 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.517, -0.002, 0.217) | (0.522, -0.001, 0.030)→(0.522, -0.001, 0.026) | 0.287→0.289 | 1.00 / 4.000 | 11.277 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.517, -0.002, 0.217)→(0.517, -0.001, 0.054) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 4.000 | 0.123 | 0.123 |
| contact_grasp | contact | 1.00 / force_exceeded | (0.517, -0.001, 0.054)→(0.511, -0.001, 0.047) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 45.000 | 0.143 | 0.189 |
| lift_1 | lift | 1.00 / step_budget | (0.511, -0.001, 0.047)→(0.507, -0.001, 0.153) | (0.522, -0.001, 0.026)→(0.518, -0.001, 0.126) | 0.289→0.241 | 1.00 / 25.000 | 82.810 | 0.440 |
| transport_arc | approach | 0.00 / step_budget | (0.507, -0.001, 0.153)→(0.525, 0.043, 0.210) | (0.518, -0.001, 0.126)→(0.530, 0.051, 0.105) | 0.241→0.221 | 1.00 / 12.000 | 0.505 | 0.762 |
| descend_place | descend | 0.33 / step_budget | (0.525, 0.043, 0.210)→(0.579, 0.151, 0.197) | (0.530, 0.051, 0.105)→(0.554, 0.085, 0.016) | 0.221→0.233 | 1.00 / 8.000 | 3249.711 | 1.421 |
| release_1 | release | 1.00 / step_budget | (0.579, 0.151, 0.197)→(0.574, 0.150, 0.219) | (0.554, 0.085, 0.016)→(0.554, 0.085, 0.016) | 0.233→0.233 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract_1 | retract | 1.00 / step_budget | (0.574, 0.150, 0.219)→(0.572, 0.149, 0.354) | (0.554, 0.085, 0.016)→(0.554, 0.085, 0.016) | 0.233→0.233 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.267
- phase_score: 0.291
- phase_breakdown.approach_1_score: 0.015
- phase_breakdown.descend_1_score: 0.871
- phase_breakdown.transport_arc_score: 0.029
- phase_breakdown.release_1_score: 0.248
- phase_breakdown.grasp_1_score: 1.000
- grasp_place_fitness: 0.589

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.589
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.267
- **Median Q (composite search score)**: 0.197
- **K-run variance**: 0.0003
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.434


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.67337,"average_solve_count":199.0,"average_success_count":199.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.22343,"contact_grasp.contact_force":8.15308,"lift_1.lift_height":0.14056,"release_1.release_delay":0.49212,"transport_arc.arc_height":0.03169,"transport_arc.transport_speed":0.05069},"optimized_scores":{"best_composite_score":0.1943,"best_fitness_score":0.5493,"best_task_score":0.18675},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":27.0,"contact_point_centroid":[0.50359,0.10628,-0.00719],"force_p95":1.92815,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.93884,"mean_force":1.31753,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.49236,0.08837,0.24653]},{"body_a":"world","body_b":"grasp_target","contact_count":3983.0,"contact_point_centroid":[0.50466,0.12201,-0.00222],"force_p95":0.12751,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.21177,"mean_force":0.12916,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.52978,0.15085,0.23319]},{"body_a":"world","body_b":"grasp_target","contact_count":139.0,"contact_point_centroid":[0.48018,0.04635,-0.00121],"force_p95":0.26283,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.40475,"mean_force":0.05595,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47158,0.04706,0.04983]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14235.0,"contact_point_centroid":[0.4707,0.06576,0.10696],"force_p95":0.09737,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29808,"mean_force":0.0589,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46918,0.04684,0.1063]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13576.0,"contact_point_centroid":[0.46995,0.02785,0.10636],"force_p95":0.11436,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29608,"mean_force":0.06195,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46915,0.04684,0.10626]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7815.0,"contact_point_centroid":[0.48223,0.04634,0.20549],"force_p95":0.13594,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24226,"mean_force":0.1023,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.4775,0.06463,0.20883]},{"body_a":"world","body_b":"grasp_target","contact_count":1644.0,"contact_point_centroid":[0.48273,0.04859,-0.00214],"force_p95":0.15745,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21358,"mean_force":0.1326,"phase_index":2.0,"phase_name":"contact_grasp","phase_type":"contact","tcp_position_centroid":[0.47366,0.04727,0.04857]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8683.0,"contact_point_centroid":[0.48214,0.08166,0.2044],"force_p95":0.13356,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20955,"mean_force":0.0927,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.47687,0.06358,0.20686]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4091.0,"contact_point_centroid":[0.47231,0.02801,0.04898],"force_p95":0.08,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14681,"mean_force":0.05205,"phase_index":2.0,"phase_name":"contact_grasp","phase_type":"contact","tcp_position_centroid":[0.47306,0.04722,0.04792]},{"body_a":"world","body_b":"grasp_target","contact_count":832.0,"contact_point_centroid":[0.4827,0.04873,-0.00184],"force_p95":0.13728,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12321,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49125,0.0187,0.2783]},{"body_a":"world","body_b":"grasp_target","contact_count":2524.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47974,0.04346,0.1548]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.50467,0.12211,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55967,0.20172,0.22726]},{"body_a":"world","body_b":"grasp_target","contact_count":3372.0,"contact_point_centroid":[0.50467,0.12211,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.55655,0.20033,0.31306]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4990.0,"contact_point_centroid":[0.47316,0.06634,0.04903],"force_p95":0.07327,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0745,"mean_force":0.04413,"phase_index":2.0,"phase_name":"contact_grasp","phase_type":"contact","tcp_position_centroid":[0.47307,0.04722,0.04793]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4127.0,"contact_point_centroid":[0.53171,0.15321,0.23503],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01606,"mean_force":0.01043,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.53119,0.15319,0.23272]},{"body_a":"left_finger","body_b":"right_finger","contact_count":225.0,"contact_point_centroid":[0.56219,0.20268,0.22491],"force_p95":0.01091,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01092,"mean_force":0.00994,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5618,0.20266,0.22303]}],"total_contact_groups":16},"final_pose_error":0.01432,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.50467,0.12211,0.01602],"final_tcp_position":[0.55731,0.20052,0.38295],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":1.93884,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":209.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":832.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.48321,0.0394,0.25694],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.23111,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":631.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2524.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.47848,0.0477,0.05479],"tcp_start":[0.48321,0.0394,0.25694],"tcp_to_object_dist_end":0.0291,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":11.0,"n_steps_budget":600.0,"object_pos_end":[0.48266,0.04762,0.02555],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29101,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.15386,"phase_name":"contact_grasp","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":10725.0,"raw_peak_contact_force":0.21358,"subtask_id":"grasp_1","tcp_end":[0.47304,0.04722,0.04789],"tcp_start":[0.47848,0.0477,0.05479],"tcp_to_object_dist_end":0.02433,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":813.0,"n_steps_budget":900.0,"object_pos_end":[0.47881,0.04772,0.14727],"object_pos_start":[0.48266,0.04762,0.02555],"object_to_goal_dist_end":0.2244,"object_to_goal_dist_start":0.29101,"object_z_max":0.14716,"peak_contact_force":0.13561,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":27950.0,"raw_peak_contact_force":0.40475,"tcp_end":[0.46946,0.04687,0.17694],"tcp_start":[0.47304,0.04722,0.04789],"tcp_to_object_dist_end":0.03113,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49825,0.11494,0.0014],"object_pos_start":[0.47881,0.04772,0.14727],"object_to_goal_dist_end":0.26916,"object_to_goal_dist_start":0.2244,"object_z_max":0.20075,"peak_contact_force":1.26922,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":16525.0,"raw_peak_contact_force":1.93884,"subtask_id":"transport_arc","tcp_end":[0.49254,0.08865,0.2469],"tcp_start":[0.46946,0.04687,0.17694],"tcp_to_object_dist_end":0.24698,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50467,0.12211,0.01602],"object_pos_start":[0.49825,0.11494,0.0014],"object_to_goal_dist_end":0.25169,"object_to_goal_dist_start":0.26916,"object_z_max":0.01701,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8110.0,"raw_peak_contact_force":1.21177,"tcp_end":[0.56296,0.20294,0.22575],"tcp_start":[0.49254,0.08865,0.2469],"tcp_to_object_dist_end":0.2322,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50467,0.12211,0.01602],"object_pos_start":[0.50467,0.12211,0.01602],"object_to_goal_dist_end":0.25169,"object_to_goal_dist_start":0.25169,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1025.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.55847,0.20118,0.2472],"tcp_start":[0.56296,0.20294,0.22575],"tcp_to_object_dist_end":0.25018,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":843.0,"n_steps_budget":930.0,"object_pos_end":[0.50467,0.12211,0.01602],"object_pos_start":[0.50467,0.12211,0.01602],"object_to_goal_dist_end":0.25169,"object_to_goal_dist_start":0.25169,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3372.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.55731,0.20052,0.38295],"tcp_start":[0.55847,0.20118,0.2472],"tcp_to_object_dist_end":0.37889,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.67241,"average_solve_count":174.0,"average_success_count":174.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.11475,"contact_grasp.contact_force":12.48795,"lift_1.lift_height":0.10576,"release_1.release_delay":0.19247,"transport_arc.arc_height":0.02266,"transport_arc.transport_speed":0.01813},"optimized_scores":{"best_composite_score":0.197,"best_fitness_score":0.552,"best_task_score":0.19084},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1577.0,"contact_point_centroid":[0.56694,0.07555,-0.00263],"force_p95":0.29801,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.58819,"mean_force":0.14919,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.56715,0.12161,0.1917]},{"body_a":"world","body_b":"grasp_target","contact_count":147.0,"contact_point_centroid":[0.5347,-0.0205,-0.00115],"force_p95":0.31142,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.44735,"mean_force":0.06827,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52414,-0.02086,0.04804]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11743.0,"contact_point_centroid":[0.52279,-0.03979,0.08967],"force_p95":0.08984,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27238,"mean_force":0.05391,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52158,-0.0208,0.0884]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10470.0,"contact_point_centroid":[0.52282,-0.00171,0.09048],"force_p95":0.09805,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27208,"mean_force":0.05962,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52156,-0.0208,0.0893]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4626.0,"contact_point_centroid":[0.55071,0.08235,0.18398],"force_p95":0.12379,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24415,"mean_force":0.10152,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.54573,0.06404,0.18831]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12371.0,"contact_point_centroid":[0.53065,-0.01499,0.16236],"force_p95":0.12067,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18023,"mean_force":0.07491,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.5266,0.00344,0.16353]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11166.0,"contact_point_centroid":[0.531,0.02214,0.16224],"force_p95":0.12362,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17412,"mean_force":0.08232,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.52665,0.00361,0.16369]},{"body_a":"world","body_b":"grasp_target","contact_count":1636.0,"contact_point_centroid":[0.53703,-0.02127,-0.00205],"force_p95":0.13561,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17156,"mean_force":0.12657,"phase_index":2.0,"phase_name":"contact_grasp","phase_type":"contact","tcp_position_centroid":[0.5264,-0.0209,0.0471]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5069.0,"contact_point_centroid":[0.55076,0.04647,0.18405],"force_p95":0.11429,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15082,"mean_force":0.09217,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.54593,0.06465,0.18831]},{"body_a":"world","body_b":"grasp_target","contact_count":1980.0,"contact_point_centroid":[0.53702,-0.02132,-0.00193],"force_p95":0.13308,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12287,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51384,-0.00956,0.22533]},{"body_a":"world","body_b":"grasp_target","contact_count":1196.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52959,-0.0202,0.10246]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.56685,0.07541,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57026,0.13914,0.19466]},{"body_a":"world","body_b":"grasp_target","contact_count":3372.0,"contact_point_centroid":[0.56685,0.07541,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5664,0.13804,0.28065]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4845.0,"contact_point_centroid":[0.52532,-0.00164,0.04719],"force_p95":0.06799,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09819,"mean_force":0.04504,"phase_index":2.0,"phase_name":"contact_grasp","phase_type":"contact","tcp_position_centroid":[0.52578,-0.02089,0.04635]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5377.0,"contact_point_centroid":[0.52514,-0.0401,0.04747],"force_p95":0.06424,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08226,"mean_force":0.04096,"phase_index":2.0,"phase_name":"contact_grasp","phase_type":"contact","tcp_position_centroid":[0.52578,-0.02089,0.04635]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1406.0,"contact_point_centroid":[0.56873,0.1248,0.19427],"force_p95":0.01252,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01479,"mean_force":0.01063,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.56836,0.12479,0.19192]}],"total_contact_groups":17},"final_pose_error":0.01427,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.56685,0.07541,0.01602],"final_tcp_position":[0.56711,0.13817,0.35052],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":9748.88679,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":496.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":33.58702,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1980.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.53018,-0.01949,0.15151],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12569,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":299.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1196.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53152,-0.02098,0.0541],"tcp_start":[0.53018,-0.01949,0.15151],"tcp_to_object_dist_end":0.02861,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":9.0,"n_steps_budget":600.0,"object_pos_end":[0.53695,-0.02099,0.02582],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31659,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13499,"phase_name":"contact_grasp","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":11858.0,"raw_peak_contact_force":0.17156,"subtask_id":"grasp_1","tcp_end":[0.52576,-0.02089,0.04632],"tcp_start":[0.53152,-0.02098,0.0541],"tcp_to_object_dist_end":0.02336,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":603.0,"n_steps_budget":690.0,"object_pos_end":[0.53334,-0.02095,0.11413],"object_pos_start":[0.53695,-0.02099,0.02582],"object_to_goal_dist_end":0.27655,"object_to_goal_dist_start":0.31659,"object_z_max":0.11402,"peak_contact_force":248.18981,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":22360.0,"raw_peak_contact_force":0.44735,"tcp_end":[0.52165,-0.02079,0.13971],"tcp_start":[0.52576,-0.02089,0.04632],"tcp_to_object_dist_end":0.02812,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":17.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54069,0.02863,0.15699],"object_pos_start":[0.53334,-0.02095,0.11413],"object_to_goal_dist_end":0.21689,"object_to_goal_dist_start":0.27655,"object_z_max":0.15695,"peak_contact_force":0.12345,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":23537.0,"raw_peak_contact_force":0.18023,"subtask_id":"transport_arc","tcp_end":[0.53584,0.02918,0.1915],"tcp_start":[0.52165,-0.02079,0.13971],"tcp_to_object_dist_end":0.03486,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56685,0.07541,0.01602],"object_pos_start":[0.54069,0.02863,0.15699],"object_to_goal_dist_end":0.24845,"object_to_goal_dist_start":0.21689,"object_z_max":0.15699,"peak_contact_force":9748.88679,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":12678.0,"raw_peak_contact_force":1.58819,"tcp_end":[0.57409,0.14004,0.19293],"tcp_start":[0.53584,0.02918,0.1915],"tcp_to_object_dist_end":0.18849,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56685,0.07541,0.01602],"object_pos_start":[0.56685,0.07541,0.01602],"object_to_goal_dist_end":0.24845,"object_to_goal_dist_start":0.24845,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1018.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.5688,0.13872,0.21468],"tcp_start":[0.57409,0.14004,0.19293],"tcp_to_object_dist_end":0.20851,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":843.0,"n_steps_budget":930.0,"object_pos_end":[0.56685,0.07541,0.01602],"object_pos_start":[0.56685,0.07541,0.01602],"object_to_goal_dist_end":0.24845,"object_to_goal_dist_start":0.24845,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3372.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.56711,0.13817,0.35052],"tcp_start":[0.5688,0.13872,0.21468],"tcp_to_object_dist_end":0.34034,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.67222,"average_solve_count":180.0,"average_success_count":180.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.20968,"contact_grasp.contact_force":9.69372,"lift_1.lift_height":0.10847,"release_1.release_delay":0.08518,"transport_arc.arc_height":0.02581,"transport_arc.transport_speed":0.02145},"optimized_scores":{"best_composite_score":0.23445,"best_fitness_score":0.58945,"best_task_score":0.26653},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1521.0,"contact_point_centroid":[0.59045,0.05705,-0.00262],"force_p95":0.3001,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.46281,"mean_force":0.14822,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.59104,0.09592,0.17506]},{"body_a":"world","body_b":"grasp_target","contact_count":147.0,"contact_point_centroid":[0.543,-0.02812,-0.00117],"force_p95":0.32166,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.46759,"mean_force":0.07009,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53267,-0.02858,0.04768]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11747.0,"contact_point_centroid":[0.53141,-0.0475,0.09002],"force_p95":0.09084,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27176,"mean_force":0.05405,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5301,-0.02849,0.08851]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10570.0,"contact_point_centroid":[0.53129,-0.0094,0.09154],"force_p95":0.09607,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27026,"mean_force":0.05889,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53007,-0.02849,0.09016]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4670.0,"contact_point_centroid":[0.56766,0.06241,0.1767],"force_p95":0.13091,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24688,"mean_force":0.10401,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.56253,0.04412,0.18086]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5148.0,"contact_point_centroid":[0.56803,0.02705,0.17647],"force_p95":0.12018,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19572,"mean_force":0.09416,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.56309,0.04518,0.1807]},{"body_a":"world","body_b":"grasp_target","contact_count":1644.0,"contact_point_centroid":[0.54561,-0.02918,-0.00207],"force_p95":0.14058,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18217,"mean_force":0.12786,"phase_index":2.0,"phase_name":"contact_grasp","phase_type":"contact","tcp_position_centroid":[0.53499,-0.02865,0.04677]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12776.0,"contact_point_centroid":[0.54059,-0.02798,0.16373],"force_p95":0.1189,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16741,"mean_force":0.0726,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.53651,-0.00951,0.1647]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11615.0,"contact_point_centroid":[0.54064,0.0089,0.16312],"force_p95":0.12359,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16449,"mean_force":0.07946,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.53642,-0.00968,0.16446]},{"body_a":"world","body_b":"grasp_target","contact_count":1176.0,"contact_point_centroid":[0.5456,-0.02923,-0.00189],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12304,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51738,-0.01258,0.26943]},{"body_a":"world","body_b":"grasp_target","contact_count":2228.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53724,-0.02703,0.14687]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.59043,0.05699,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59538,0.11036,0.17472]},{"body_a":"world","body_b":"grasp_target","contact_count":3372.0,"contact_point_centroid":[0.59043,0.05699,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.59112,0.1094,0.26009]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4840.0,"contact_point_centroid":[0.53389,-0.00932,0.04689],"force_p95":0.06969,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10374,"mean_force":0.04527,"phase_index":2.0,"phase_name":"contact_grasp","phase_type":"contact","tcp_position_centroid":[0.53433,-0.02863,0.04596]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5878.0,"contact_point_centroid":[0.53428,-0.04782,0.04792],"force_p95":0.06166,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0775,"mean_force":0.0377,"phase_index":2.0,"phase_name":"contact_grasp","phase_type":"contact","tcp_position_centroid":[0.53434,-0.02863,0.04596]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1308.0,"contact_point_centroid":[0.59309,0.09886,0.1771],"force_p95":0.01218,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01654,"mean_force":0.01077,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.59268,0.09886,0.17476]}],"total_contact_groups":17},"final_pose_error":0.01472,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.59043,0.05699,0.01602],"final_tcp_position":[0.59184,0.1095,0.32993],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":1.46281,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":295.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1176.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.53659,-0.02537,0.24124],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.21545,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":557.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2228.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.54029,-0.02879,0.05442],"tcp_start":[0.53659,-0.02537,0.24124],"tcp_to_object_dist_end":0.0289,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":48.0,"n_steps":11.0,"n_steps_budget":600.0,"object_pos_end":[0.54553,-0.02875,0.02576],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26074,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.14019,"phase_name":"contact_grasp","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":12362.0,"raw_peak_contact_force":0.18217,"subtask_id":"grasp_1","tcp_end":[0.53431,-0.02863,0.04593],"tcp_start":[0.54029,-0.02879,0.05442],"tcp_to_object_dist_end":0.02308,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":603.0,"n_steps_budget":690.0,"object_pos_end":[0.54209,-0.02867,0.11644],"object_pos_start":[0.54553,-0.02875,0.02576],"object_to_goal_dist_end":0.22221,"object_to_goal_dist_start":0.26074,"object_z_max":0.11633,"peak_contact_force":0.10383,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":22464.0,"raw_peak_contact_force":0.46759,"tcp_end":[0.5302,-0.02848,0.14166],"tcp_start":[0.53431,-0.02863,0.04593],"tcp_to_object_dist_end":0.02788,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55184,0.00963,0.15612],"object_pos_start":[0.54209,-0.02867,0.11644],"object_to_goal_dist_end":0.17638,"object_to_goal_dist_start":0.22221,"object_z_max":0.15609,"peak_contact_force":0.12361,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":24391.0,"raw_peak_contact_force":0.16741,"subtask_id":"transport_arc","tcp_end":[0.54698,0.01012,0.19017],"tcp_start":[0.5302,-0.02848,0.14166],"tcp_to_object_dist_end":0.0344,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.59043,0.05699,0.01602],"object_pos_start":[0.55184,0.00963,0.15612],"object_to_goal_dist_end":0.19834,"object_to_goal_dist_start":0.17638,"object_z_max":0.15612,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":12647.0,"raw_peak_contact_force":1.46281,"tcp_end":[0.59956,0.11105,0.17351],"tcp_start":[0.54698,0.01012,0.19017],"tcp_to_object_dist_end":0.16676,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59043,0.05699,0.01602],"object_pos_start":[0.59043,0.05699,0.01602],"object_to_goal_dist_end":0.19834,"object_to_goal_dist_start":0.19834,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1023.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.59377,0.10999,0.19451],"tcp_start":[0.59956,0.11105,0.17351],"tcp_to_object_dist_end":0.18623,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":843.0,"n_steps_budget":930.0,"object_pos_end":[0.59043,0.05699,0.01602],"object_pos_start":[0.59043,0.05699,0.01602],"object_to_goal_dist_end":0.19834,"object_to_goal_dist_start":0.19834,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3372.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.59184,0.1095,0.32993],"tcp_start":[0.59377,0.10999,0.19451],"tcp_to_object_dist_end":0.31828,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```