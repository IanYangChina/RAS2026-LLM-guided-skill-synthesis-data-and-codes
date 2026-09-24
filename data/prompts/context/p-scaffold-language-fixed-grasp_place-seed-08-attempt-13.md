## Search State

- **Seed**: 8
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 4 | 0.2222 | 0.27 | ❌ rejected |
| 12 | approach → descend → grasp → lift → approach | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 2 | 0.4965 | 0.44 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 5 | 0.1994 | 0.17 | ✅ accepted |
| 10 | approach → descend → grasp → lift → approach → release → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.2883 | 0.25 | ✅ accepted |
| 9 | approach → descend → grasp → lift → approach → release → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.2878 | 0.13 | ✅ accepted |

**Proposal policy**: task_score is 0.27 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.222) — your mutation base

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
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.3
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
    tolerance: 0.01
    orientation:
      mode: keep_current
  subtask_id: descend_1
- id: grasp_1
  type: grasp
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.02
    tolerance: 0.01
    orientation:
      mode: keep_current
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
    - 0.0
    offset_along_axis:
      distance: 0.15
      axis: world_z
      mode: add_to_offset
      sign: positive
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
- id: transport_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  subtask_id: transport_arc

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.15], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.02], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.02], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none
- **lift_1** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.15, mode=add_to_offset, sign=positive}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
- **transport_1** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.222
- **task_score** (E): 0.274
- **fitness_score**: 0.602  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.380

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0789 |
| descend_1 | 1.00 | 1.00 | 0.1803 |
| grasp_1 | 1.00 | 1.00 | 0.0108 |
| lift_1 | 0.67 | 1.00 | 0.1158 |
| transport_1 | 1.00 | 1.00 | 0.2579 |
| descend_to_release | 1.00 | 1.00 | 0.0576 |
| release_1 | 1.00 | 1.00 | 0.0199 |
| retract_1 | 1.00 | 1.00 | 0.0659 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.516, -0.002, 0.235) | (0.522, -0.001, 0.030)→(0.522, -0.001, 0.026) | 0.287→0.289 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.516, -0.002, 0.235)→(0.517, -0.001, 0.055) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.517, -0.001, 0.055)→(0.511, -0.001, 0.046) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 46.333 | 0.142 | 0.190 |
| lift_1 | lift | 0.67 / step_budget | (0.511, -0.001, 0.046)→(0.507, -0.001, 0.161) | (0.522, -0.001, 0.026)→(0.519, -0.001, 0.135) | 0.289→0.243 | 1.00 / 26.000 | 0.104 | 0.443 |
| transport_1 | approach | 1.00 / step_budget | (0.507, -0.001, 0.161)→(0.601, 0.196, 0.290) | (0.519, -0.001, 0.135)→(0.596, 0.165, 0.016) | 0.243→0.196 | 1.00 / 8.333 | 91004.625 | 1.947 |
| descend_to_release | descend | 1.00 / step_budget | (0.601, 0.196, 0.290)→(0.604, 0.203, 0.233) | (0.596, 0.165, 0.016)→(0.596, 0.165, 0.016) | 0.196→0.196 | 1.00 / 8.000 | 0.123 | 0.125 |
| release_1 | release | 1.00 / step_budget | (0.604, 0.203, 0.233)→(0.599, 0.202, 0.252) | (0.596, 0.165, 0.016)→(0.596, 0.165, 0.016) | 0.196→0.196 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract_1 | retract | 1.00 / step_budget | (0.599, 0.202, 0.252)→(0.597, 0.201, 0.318) | (0.596, 0.165, 0.016)→(0.596, 0.165, 0.016) | 0.196→0.196 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.342
- phase_score: 0.390
- phase_breakdown.transport_arc_score: 0.171
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.descend_1_score: 0.870
- phase_breakdown.approach_1_score: 0.038
- phase_breakdown.release_1_score: 0.384
- grasp_place_fitness: 0.637

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.637
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.342
- **Median Q (composite search score)**: 0.213
- **K-run variance**: 0.0006
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.480


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.68452,"average_solve_count":168.0,"average_success_count":168.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.23234,"lift_1.lift_height":0.10797,"release_1.release_duration":0.46675,"transport_1.transport_speed":1.69413},"optimized_scores":{"best_composite_score":0.19673,"best_fitness_score":0.57673,"best_task_score":0.22592},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1037.0,"contact_point_centroid":[0.55792,0.17215,-0.00305],"force_p95":0.5253,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.93457,"mean_force":0.17318,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55513,0.18814,0.28218]},{"body_a":"world","body_b":"grasp_target","contact_count":135.0,"contact_point_centroid":[0.48009,0.04626,-0.00122],"force_p95":0.2777,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.41607,"mean_force":0.05822,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47145,0.04711,0.04882]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11396.0,"contact_point_centroid":[0.47001,0.06593,0.09345],"force_p95":0.08986,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2999,"mean_force":0.05596,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46902,0.04688,0.09238]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10936.0,"contact_point_centroid":[0.46937,0.02782,0.09383],"force_p95":0.08912,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29872,"mean_force":0.05717,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46898,0.04688,0.0932]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3749.0,"contact_point_centroid":[0.49811,0.10642,0.18106],"force_p95":0.12456,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28456,"mean_force":0.08283,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.49241,0.0879,0.18148]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3714.0,"contact_point_centroid":[0.49838,0.06995,0.1814],"force_p95":0.13335,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25927,"mean_force":0.08362,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.49278,0.08853,0.18208]},{"body_a":"world","body_b":"grasp_target","contact_count":1680.0,"contact_point_centroid":[0.48273,0.04859,-0.00213],"force_p95":0.15669,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21337,"mean_force":0.13221,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4736,0.04733,0.04773]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4091.0,"contact_point_centroid":[0.4722,0.02805,0.04837],"force_p95":0.08037,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14736,"mean_force":0.05201,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47291,0.04726,0.04694]},{"body_a":"world","body_b":"grasp_target","contact_count":804.0,"contact_point_centroid":[0.4827,0.04873,-0.00184],"force_p95":0.13728,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12324,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49126,0.01866,0.28179]},{"body_a":"world","body_b":"grasp_target","contact_count":2608.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47982,0.04331,0.15849]},{"body_a":"world","body_b":"grasp_target","contact_count":636.0,"contact_point_centroid":[0.55791,0.17212,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_release","phase_type":"descend","tcp_position_centroid":[0.57604,0.22241,0.28722]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.55791,0.17212,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57485,0.22416,0.25899]},{"body_a":"world","body_b":"grasp_target","contact_count":2052.0,"contact_point_centroid":[0.55791,0.17212,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.57206,0.22274,0.30963]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4989.0,"contact_point_centroid":[0.47304,0.06638,0.04834],"force_p95":0.07334,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07465,"mean_force":0.04416,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47291,0.04726,0.04695]},{"body_a":"left_finger","body_b":"right_finger","contact_count":889.0,"contact_point_centroid":[0.5592,0.1942,0.29048],"force_p95":0.01289,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01624,"mean_force":0.01086,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55895,0.19418,0.28827]},{"body_a":"left_finger","body_b":"right_finger","contact_count":662.0,"contact_point_centroid":[0.57652,0.22246,0.28928],"force_p95":0.01111,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01292,"mean_force":0.01068,"phase_index":5.0,"phase_name":"descend_to_release","phase_type":"descend","tcp_position_centroid":[0.57605,0.22243,0.28696]}],"total_contact_groups":17},"final_pose_error":0.01382,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.55791,0.17212,0.01602],"final_tcp_position":[0.57232,0.22277,0.34499],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":1.93457,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":202.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":804.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.48332,0.0391,0.2644],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.23857,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":652.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2608.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.47849,0.0477,0.05491],"tcp_start":[0.48332,0.0391,0.2644],"tcp_to_object_dist_end":0.02922,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.48265,0.04762,0.02556],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.291,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.15294,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10760.0,"raw_peak_contact_force":0.21337,"subtask_id":"grasp_1","tcp_end":[0.47288,0.04726,0.04692],"tcp_start":[0.47849,0.0477,0.05491],"tcp_to_object_dist_end":0.02348,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":603.0,"n_steps_budget":690.0,"object_pos_end":[0.47988,0.04735,0.11661],"object_pos_start":[0.48265,0.04762,0.02556],"object_to_goal_dist_end":0.2373,"object_to_goal_dist_start":0.291,"object_z_max":0.1165,"peak_contact_force":0.10402,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":22467.0,"raw_peak_contact_force":0.41607,"tcp_end":[0.46906,0.04689,0.14339],"tcp_start":[0.47288,0.04726,0.04692],"tcp_to_object_dist_end":0.02889,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":675.0,"n_steps_budget":1000.0,"object_pos_end":[0.55791,0.17212,0.01602],"object_pos_start":[0.47988,0.04735,0.11661],"object_to_goal_dist_end":0.22313,"object_to_goal_dist_start":0.2373,"object_z_max":0.19108,"peak_contact_force":0.12263,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9389.0,"raw_peak_contact_force":1.93457,"subtask_id":"transport_arc","tcp_end":[0.57514,0.21988,0.31414],"tcp_start":[0.46906,0.04689,0.14339],"tcp_to_object_dist_end":0.30241,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":159.0,"n_steps_budget":1000.0,"object_pos_end":[0.55791,0.17212,0.01602],"object_pos_start":[0.55791,0.17212,0.01602],"object_to_goal_dist_end":0.22313,"object_to_goal_dist_start":0.22313,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_release","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1298.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.57787,0.22552,0.25867],"tcp_start":[0.57514,0.21988,0.31414],"tcp_to_object_dist_end":0.24925,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.55791,0.17212,0.01602],"object_pos_start":[0.55791,0.17212,0.01602],"object_to_goal_dist_end":0.22313,"object_to_goal_dist_start":0.22313,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1023.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.5739,0.22364,0.2787],"tcp_start":[0.57787,0.22552,0.25867],"tcp_to_object_dist_end":0.26816,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.55791,0.17212,0.01602],"object_pos_start":[0.55791,0.17212,0.01602],"object_to_goal_dist_end":0.22313,"object_to_goal_dist_start":0.22313,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2052.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57232,0.22277,0.34499],"tcp_start":[0.5739,0.22364,0.2787],"tcp_to_object_dist_end":0.33316,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.81707,"average_solve_count":164.0,"average_success_count":164.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.21305,"lift_1.lift_height":0.1027,"release_1.release_duration":0.70658,"transport_1.transport_speed":1.27335},"optimized_scores":{"best_composite_score":0.21294,"best_fitness_score":0.59294,"best_task_score":0.25472},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1008.0,"contact_point_centroid":[0.5984,0.15483,-0.00311],"force_p95":0.55249,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.11494,"mean_force":0.16887,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.59043,0.1773,0.26499]},{"body_a":"world","body_b":"grasp_target","contact_count":145.0,"contact_point_centroid":[0.53465,-0.02069,-0.00114],"force_p95":0.33148,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.45642,"mean_force":0.06954,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52419,-0.02087,0.04677]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4278.0,"contact_point_centroid":[0.54642,0.02113,0.17228],"force_p95":0.1308,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32142,"mean_force":0.082,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54068,0.0397,0.17197]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10432.0,"contact_point_centroid":[0.52271,-0.00168,0.0886],"force_p95":0.09407,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27859,"mean_force":0.05699,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5216,-0.02081,0.08652]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11690.0,"contact_point_centroid":[0.52264,-0.03986,0.08802],"force_p95":0.08474,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2762,"mean_force":0.05172,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52161,-0.02081,0.08615]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4369.0,"contact_point_centroid":[0.54864,0.06448,0.17641],"force_p95":0.10694,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19678,"mean_force":0.08119,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54288,0.04593,0.17612]},{"body_a":"world","body_b":"grasp_target","contact_count":1680.0,"contact_point_centroid":[0.53703,-0.02125,-0.00205],"force_p95":0.1358,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17504,"mean_force":0.1267,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52658,-0.02092,0.04602]},{"body_a":"world","body_b":"grasp_target","contact_count":976.0,"contact_point_centroid":[0.53702,-0.02132,-0.00187],"force_p95":0.13691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12313,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51298,-0.00872,0.27238]},{"body_a":"world","body_b":"grasp_target","contact_count":2304.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52878,-0.0194,0.14926]},{"body_a":"world","body_b":"grasp_target","contact_count":620.0,"contact_point_centroid":[0.59843,0.15488,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_release","phase_type":"descend","tcp_position_centroid":[0.60508,0.22006,0.26446]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.59843,0.15488,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60293,0.22245,0.23515]},{"body_a":"world","body_b":"grasp_target","contact_count":2052.0,"contact_point_centroid":[0.59843,0.15488,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.59975,0.22096,0.28487]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5088.0,"contact_point_centroid":[0.52521,-0.00159,0.04712],"force_p95":0.06652,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08908,"mean_force":0.04307,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52582,-0.0209,0.04506]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5864.0,"contact_point_centroid":[0.52508,-0.04013,0.04716],"force_p95":0.06057,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07749,"mean_force":0.0379,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52582,-0.0209,0.04507]},{"body_a":"left_finger","body_b":"right_finger","contact_count":863.0,"contact_point_centroid":[0.59354,0.18501,0.27255],"force_p95":0.01328,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01612,"mean_force":0.01078,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.59326,0.185,0.27022]},{"body_a":"left_finger","body_b":"right_finger","contact_count":666.0,"contact_point_centroid":[0.60563,0.2201,0.26669],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01273,"mean_force":0.01039,"phase_index":5.0,"phase_name":"descend_to_release","phase_type":"descend","tcp_position_centroid":[0.60509,0.22008,0.26433]}],"total_contact_groups":17},"final_pose_error":0.0145,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.59843,0.15488,0.01602],"final_tcp_position":[0.6,0.221,0.32017],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":2.11494,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":245.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":976.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52814,-0.01789,0.24604],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.22023,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":576.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2304.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53179,-0.02098,0.05445],"tcp_start":[0.52814,-0.01789,0.24604],"tcp_to_object_dist_end":0.02891,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":49.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.53694,-0.02094,0.02581],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31656,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13475,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12632.0,"raw_peak_contact_force":0.17504,"subtask_id":"grasp_1","tcp_end":[0.5258,-0.0209,0.04503],"tcp_start":[0.53179,-0.02098,0.05445],"tcp_to_object_dist_end":0.02222,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":573.0,"n_steps_budget":660.0,"object_pos_end":[0.53417,-0.02089,0.11151],"object_pos_start":[0.53694,-0.02094,0.02581],"object_to_goal_dist_end":0.27716,"object_to_goal_dist_start":0.31656,"object_z_max":0.11139,"peak_contact_force":0.10243,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":22267.0,"raw_peak_contact_force":0.45642,"tcp_end":[0.52166,-0.02081,0.13525],"tcp_start":[0.5258,-0.0209,0.04503],"tcp_to_object_dist_end":0.02684,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":715.0,"n_steps_budget":1000.0,"object_pos_end":[0.59843,0.15488,0.01602],"object_pos_start":[0.53417,-0.02089,0.11151],"object_to_goal_dist_end":0.20514,"object_to_goal_dist_start":0.27716,"object_z_max":0.18409,"peak_contact_force":0.12263,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":10518.0,"raw_peak_contact_force":2.11494,"subtask_id":"transport_arc","tcp_end":[0.60481,0.21688,0.29175],"tcp_start":[0.52166,-0.02081,0.13525],"tcp_to_object_dist_end":0.28269,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":155.0,"n_steps_budget":1000.0,"object_pos_end":[0.59843,0.15488,0.01602],"object_pos_start":[0.59843,0.15488,0.01602],"object_to_goal_dist_end":0.20514,"object_to_goal_dist_start":0.20514,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_release","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1286.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.60632,0.22383,0.23563],"tcp_start":[0.60481,0.21688,0.29175],"tcp_to_object_dist_end":0.23032,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59843,0.15488,0.01602],"object_pos_start":[0.59843,0.15488,0.01602],"object_to_goal_dist_end":0.20514,"object_to_goal_dist_start":0.20514,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1025.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.60183,0.22191,0.25452],"tcp_start":[0.60632,0.22383,0.23563],"tcp_to_object_dist_end":0.24777,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.59843,0.15488,0.01602],"object_pos_start":[0.59843,0.15488,0.01602],"object_to_goal_dist_end":0.20514,"object_to_goal_dist_start":0.20514,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2052.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.6,0.221,0.32017],"tcp_start":[0.60183,0.22191,0.25452],"tcp_to_object_dist_end":0.31125,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.75862,"average_solve_count":174.0,"average_success_count":174.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.1588,"lift_1.lift_height":0.22613,"release_1.release_duration":0.48688,"transport_1.transport_speed":0.81106},"optimized_scores":{"best_composite_score":0.25685,"best_fitness_score":0.63685,"best_task_score":0.34203},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":371.0,"contact_point_centroid":[0.63059,0.16675,-0.00557],"force_p95":1.33205,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.79135,"mean_force":0.26674,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.61645,0.13767,0.25886]},{"body_a":"world","body_b":"grasp_target","contact_count":147.0,"contact_point_centroid":[0.54326,-0.02825,-0.00116],"force_p95":0.32287,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.45741,"mean_force":0.07149,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53248,-0.02859,0.04636]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3420.0,"contact_point_centroid":[0.56486,0.04618,0.2196],"force_p95":0.16175,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3362,"mean_force":0.09807,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.5582,0.02781,0.22059]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3719.0,"contact_point_centroid":[0.56248,0.00566,0.21821],"force_p95":0.14647,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32228,"mean_force":0.08562,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55607,0.02372,0.21921]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17752.0,"contact_point_centroid":[0.53212,-0.04739,0.11425],"force_p95":0.09456,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2852,"mean_force":0.05782,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52997,-0.0285,0.11232]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15552.0,"contact_point_centroid":[0.5326,-0.00947,0.11476],"force_p95":0.1032,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28133,"mean_force":0.06481,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52997,-0.0285,0.11291]},{"body_a":"world","body_b":"grasp_target","contact_count":1680.0,"contact_point_centroid":[0.54561,-0.02914,-0.00206],"force_p95":0.13898,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18225,"mean_force":0.12762,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53491,-0.02866,0.04565]},{"body_a":"world","body_b":"grasp_target","contact_count":1592.0,"contact_point_centroid":[0.5456,-0.02923,-0.00191],"force_p95":0.13465,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12293,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51754,-0.01285,0.24619]},{"body_a":"world","body_b":"grasp_target","contact_count":664.0,"contact_point_centroid":[0.63075,0.16708,-0.00198],"force_p95":0.12667,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1289,"mean_force":0.12315,"phase_index":5.0,"phase_name":"descend_to_release","phase_type":"descend","tcp_position_centroid":[0.62524,0.1564,0.23484]},{"body_a":"world","body_b":"grasp_target","contact_count":1680.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53756,-0.02742,0.12344]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.63075,0.16708,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62367,0.1599,0.20389]},{"body_a":"world","body_b":"grasp_target","contact_count":2052.0,"contact_point_centroid":[0.63075,0.16708,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.61975,0.15865,0.25354]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5080.0,"contact_point_centroid":[0.53347,-0.00932,0.04727],"force_p95":0.06709,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09865,"mean_force":0.04306,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53414,-0.02864,0.04466]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5879.0,"contact_point_centroid":[0.53313,-0.04787,0.04701],"force_p95":0.06123,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.078,"mean_force":0.03794,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53415,-0.02864,0.04466]},{"body_a":"left_finger","body_b":"right_finger","contact_count":266.0,"contact_point_centroid":[0.61947,0.1427,0.26293],"force_p95":0.01422,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01623,"mean_force":0.01138,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.61916,0.14269,0.26065]},{"body_a":"left_finger","body_b":"right_finger","contact_count":218.0,"contact_point_centroid":[0.62631,0.16069,0.20272],"force_p95":0.01107,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01286,"mean_force":0.01022,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62602,0.16067,0.20041]}],"total_contact_groups":17},"final_pose_error":0.01463,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.63075,0.16708,0.01602],"final_tcp_position":[0.61995,0.15867,0.28883],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":273013.62842,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":399.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1592.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.53755,-0.02617,0.19384],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16804,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":420.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1680.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.54017,-0.02878,0.05429],"tcp_start":[0.53755,-0.02617,0.19384],"tcp_to_object_dist_end":0.02879,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":49.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.54552,-0.02873,0.02577],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26072,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.13721,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12639.0,"raw_peak_contact_force":0.18225,"subtask_id":"grasp_1","tcp_end":[0.53412,-0.02864,0.04463],"tcp_start":[0.54017,-0.02878,0.05429],"tcp_to_object_dist_end":0.02204,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54148,-0.02876,0.17762],"object_pos_start":[0.54552,-0.02873,0.02577],"object_to_goal_dist_end":0.21416,"object_to_goal_dist_start":0.26072,"object_z_max":0.17743,"peak_contact_force":0.10523,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":33451.0,"raw_peak_contact_force":0.45741,"tcp_end":[0.53047,-0.02851,0.20504],"tcp_start":[0.53412,-0.02864,0.04463],"tcp_to_object_dist_end":0.02955,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":541.0,"n_steps_budget":1000.0,"object_pos_end":[0.63073,0.16728,0.0165],"object_pos_start":[0.54148,-0.02876,0.17762],"object_to_goal_dist_end":0.16045,"object_to_goal_dist_start":0.21416,"object_z_max":0.20397,"peak_contact_force":273013.62842,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7776.0,"raw_peak_contact_force":1.79135,"subtask_id":"transport_arc","tcp_end":[0.62421,0.15241,0.264],"tcp_start":[0.53047,-0.02851,0.20504],"tcp_to_object_dist_end":0.24803,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":166.0,"n_steps_budget":1000.0,"object_pos_end":[0.63075,0.16708,0.01602],"object_pos_start":[0.63073,0.16728,0.0165],"object_to_goal_dist_end":0.16093,"object_to_goal_dist_start":0.16045,"object_z_max":0.0165,"peak_contact_force":0.12263,"phase_name":"descend_to_release","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1371.0,"raw_peak_contact_force":0.1289,"subtask_id":"release_1","tcp_end":[0.62768,0.161,0.20443],"tcp_start":[0.62421,0.15241,0.264],"tcp_to_object_dist_end":0.18854,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.63075,0.16708,0.01602],"object_pos_start":[0.63075,0.16708,0.01602],"object_to_goal_dist_end":0.16093,"object_to_goal_dist_start":0.16093,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1018.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.6223,0.15945,0.22324],"tcp_start":[0.62768,0.161,0.20443],"tcp_to_object_dist_end":0.20754,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.63075,0.16708,0.01602],"object_pos_start":[0.63075,0.16708,0.01602],"object_to_goal_dist_end":0.16093,"object_to_goal_dist_start":0.16093,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2052.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61995,0.15867,0.28883],"tcp_start":[0.6223,0.15945,0.22324],"tcp_to_object_dist_end":0.27315,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```