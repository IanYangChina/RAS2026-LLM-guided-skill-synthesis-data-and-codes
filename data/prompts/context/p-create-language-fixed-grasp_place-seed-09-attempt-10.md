## Search State

- **Seed**: 9
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → descend → contact → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 4 | 0.1681 | 0.17 | ❌ rejected |
| 9 | approach → descend → contact → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | force_threshold_switch | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | time_limit | pose_tolerance | time_limit | 5 | 0.1402 | 0.19 | ❌ rejected |
| 8 | approach → descend → contact → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | force_threshold_switch | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 4 | 0.2054 | 0.24 | ❌ rejected |
| 7 | approach → descend → contact → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 3 | 0.2768 | 0.28 | ❌ rejected |
| 6 | approach → descend → contact → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | force_threshold_switch | impedance_control | impedance_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 8 | 0.1752 | 0.18 | ✅ accepted |

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
- Frozen realised-scene SHA-256: `0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8`
- Frozen object start: [0.5370249203970084, -0.021318279091244466, 0.03]
- Frozen task target: [0.6103148150051562, 0.2277534082920179, 0.2074111944405348]
- Goal object position: (0.6103148150051562, 0.2277534082920179, 0.2074111944405348)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.6103148150051562, 0.2277534082920179, 0.2074111944405348)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5370249203970084, -0.021318279091244466, 0.03)
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
  frozen_object_start: [0.537, -0.0213, 0.03]
  frozen_task_target: [0.6103, 0.2278, 0.2074]
  frozen_object_starts: {'grasp_target': [0.5370249203970084, -0.021318279091244466, 0.03]}
  frozen_targets: {'place_target': [0.6103148150051562, 0.2277534082920179, 0.2074111944405348]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8

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

## Current Skill (Q=0.168) — your mutation base

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
    tolerance: 0.005
    orientation:
      mode: keep_current
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
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - -0.015
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
- id: grasp_1
  type: grasp
  control: position_control
  termination: time_limit
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
      distance: 0.1
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
      default: 0.12
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
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.1
      - 1.0
      default: 0.3
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: transport_arc
- id: place_descend
  type: descend
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
    tolerance: 0.005
    orientation:
      mode: keep_current
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
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.08], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings: none
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.02], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings: none
- **contact_1** (`contact`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, -0.015]
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none
- **lift_1** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.1, mode=add_to_offset, sign=positive}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
- **transport_1** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **place_descend** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings: none
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.168
- **task_score** (E): 0.165
- **fitness_score**: 0.465  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.083
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.380

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 0.67 | 1.00 | 0.1633 |
| descend_1 | 1.00 | 1.00 | 0.0912 |
| contact_1 | 0.67 | 1.00 | 0.0041 |
| grasp_1 | 1.00 | 1.00 | 0.0120 |
| lift_1 | 1.00 | 1.00 | 0.1285 |
| transport_1 | 0.67 | 1.00 | 0.2539 |
| place_descend | 1.00 | 1.00 | 0.1430 |
| release_1 | 1.00 | 1.00 | 0.0206 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 0.67 / step_budget | (0.500, -0.000, 0.301)→(0.504, -0.012, 0.141) | (0.515, -0.017, 0.030)→(0.515, -0.017, 0.026) | 0.268→0.270 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.504, -0.012, 0.141)→(0.509, -0.016, 0.050) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 4.000 | 0.123 | 0.123 |
| contact_1 | contact | 0.67 / force_exceeded | (0.509, -0.016, 0.050)→(0.508, -0.016, 0.047) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 4.000 | 122.006 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.508, -0.016, 0.047)→(0.500, -0.016, 0.038) | (0.515, -0.017, 0.026)→(0.515, -0.016, 0.026) | 0.270→0.270 | 1.00 / 38.000 | 0.148 | 0.182 |
| lift_1 | lift | 1.00 / step_budget | (0.499, -0.016, 0.087)→(0.496, -0.016, 0.215) | (0.515, -0.016, 0.026)→(0.513, -0.022, 0.084) | 0.270→0.257 | 1.00 / 17.000 | 55983.984 | 0.836 |
| transport_1 | approach | 0.67 / step_budget | (0.496, -0.016, 0.215)→(0.599, 0.152, 0.330) | (0.513, -0.022, 0.084)→(0.507, -0.020, 0.016) | 0.257→0.283 | 1.00 / 8.667 | 185256.424 | 1.096 |
| place_descend | descend | 1.00 / step_budget | (0.599, 0.152, 0.330)→(0.610, 0.174, 0.191) | (0.507, -0.020, 0.016)→(0.507, -0.020, 0.016) | 0.283→0.283 | 1.00 / 8.000 | 3249.647 | 0.123 |
| release_1 | release | 1.00 / step_budget | (0.610, 0.174, 0.191)→(0.604, 0.173, 0.211) | (0.507, -0.020, 0.016)→(0.507, -0.020, 0.016) | 0.283→0.283 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.251
- phase_score: 0.310
- phase_breakdown.transport_arc_score: 0.038
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.release_1_score: 0.265
- phase_breakdown.approach_1_score: 0.185
- phase_breakdown.descend_1_score: 0.903
- grasp_place_fitness: 0.596

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.596
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.251
- **Median Q (composite search score)**: 0.136
- **K-run variance**: 0.0169
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.375


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `425c48e82220fc6e1b680086671cf7dd2586733ee271dec2149f96a25d69d0c6`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `58e88c03db0a62276863b22a53636bc89fead3e4bc7f4d35fd72d2282ace32bf`; realized-scene SHA-256: `0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53702,-0.02132,0.03]},{"name":"goal","value":[0.61031,0.22775,0.20741]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.53702,-0.02132,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.61031,0.22775,0.20741]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.84868,"average_solve_count":152.0,"average_success_count":152.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force":8.35415,"lift_1.lift_height":0.12365,"transport_1.transport_arc_height":0.21636,"transport_1.transport_speed":0.85386},"optimized_scores":{"best_composite_score":0.13592,"best_fitness_score":0.51592,"best_task_score":0.08871},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3644.0,"contact_point_centroid":[0.50917,-0.06399,-0.00219],"force_p95":0.1279,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.35071,"mean_force":0.13454,"phase_index":5.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53234,0.02821,0.30847]},{"body_a":"world","body_b":"grasp_target","contact_count":146.0,"contact_point_centroid":[0.53522,-0.02081,-0.00112],"force_p95":0.51032,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.7139,"mean_force":0.09951,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51785,-0.02081,0.02375]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7518.0,"contact_point_centroid":[0.51999,-0.00224,0.07369],"force_p95":0.15192,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.42636,"mean_force":0.09607,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5152,-0.02075,0.07319]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7706.0,"contact_point_centroid":[0.52014,-0.03923,0.07266],"force_p95":0.1486,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.40214,"mean_force":0.0944,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5152,-0.02075,0.0724]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":168.0,"contact_point_centroid":[0.51711,-0.03884,0.13019],"force_p95":0.31656,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.38635,"mean_force":0.1635,"phase_index":5.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51388,-0.02219,0.13593]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":64.0,"contact_point_centroid":[0.51937,-0.0032,0.1277],"force_p95":0.17076,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18602,"mean_force":0.11213,"phase_index":5.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51494,-0.02101,0.13375]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53701,-0.02114,-0.00206],"force_p95":0.13773,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18017,"mean_force":0.12775,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52078,-0.02087,0.02336]},{"body_a":"world","body_b":"grasp_target","contact_count":3996.0,"contact_point_centroid":[0.53702,-0.02132,-0.00196],"force_p95":0.12459,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12275,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51307,-0.00943,0.21064]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52721,-0.01914,0.08479]},{"body_a":"world","body_b":"grasp_target","contact_count":252.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52966,-0.02104,0.03761]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.50902,-0.06404,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.59693,0.19862,0.28385]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.50902,-0.06404,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60001,0.21508,0.229]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3672.0,"contact_point_centroid":[0.52225,-0.00195,0.02547],"force_p95":0.09793,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11081,"mean_force":0.05778,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51953,-0.02084,0.02197]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3852.0,"contact_point_centroid":[0.5227,-0.03974,0.02429],"force_p95":0.09094,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09361,"mean_force":0.05619,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51953,-0.02084,0.02197]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3635.0,"contact_point_centroid":[0.53433,0.03218,0.32056],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01642,"mean_force":0.01048,"phase_index":5.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53398,0.03218,0.31826]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4301.0,"contact_point_centroid":[0.59736,0.19861,0.28621],"force_p95":0.01095,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01278,"mean_force":0.01037,"phase_index":6.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.59692,0.19859,0.28394]}],"total_contact_groups":17},"final_pose_error":0.02519,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.50902,-0.06404,0.01602],"final_tcp_position":[0.60327,0.21642,0.22878],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":167951.73011,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3996.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.5248,-0.01661,0.1456],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1203,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.5316,-0.02108,0.04305],"tcp_start":[0.5248,-0.01661,0.1456],"tcp_to_object_dist_end":0.01787,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":63.0,"n_steps_budget":600.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":252.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_1","tcp_end":[0.52804,-0.02101,0.0315],"tcp_start":[0.5316,-0.02108,0.04305],"tcp_to_object_dist_end":0.01053,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":34.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53721,-0.02076,0.02571],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31641,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13762,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":9324.0,"raw_peak_contact_force":0.18017,"tcp_end":[0.5195,-0.02084,0.02193],"tcp_start":[0.52804,-0.02101,0.0315],"tcp_to_object_dist_end":0.01811,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":693.0,"n_steps_budget":780.0,"object_pos_end":[0.5298,-0.02063,0.11076],"object_pos_start":[0.53721,-0.02076,0.02571],"object_to_goal_dist_end":0.27842,"object_to_goal_dist_start":0.31641,"object_z_max":0.11072,"peak_contact_force":167951.73011,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":15370.0,"raw_peak_contact_force":0.7139,"tcp_end":[0.51537,-0.02074,0.13315],"tcp_start":[0.5195,-0.02084,0.02193],"tcp_to_object_dist_end":0.02663,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50902,-0.06404,0.01602],"object_pos_start":[0.5298,-0.02063,0.11076],"object_to_goal_dist_end":0.36337,"object_to_goal_dist_start":0.27842,"object_z_max":0.11076,"peak_contact_force":9748.92918,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7511.0,"raw_peak_contact_force":1.35071,"subtask_id":"transport_arc","tcp_end":[0.58775,0.17058,0.37849],"tcp_start":[0.51537,-0.02074,0.13315],"tcp_to_object_dist_end":0.43889,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50902,-0.06404,0.01602],"object_pos_start":[0.50902,-0.06404,0.01602],"object_to_goal_dist_end":0.36337,"object_to_goal_dist_start":0.36337,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8301.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.60327,0.21642,0.22878],"tcp_start":[0.58775,0.17058,0.37849],"tcp_to_object_dist_end":0.36443,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50902,-0.06404,0.01602],"object_pos_start":[0.50902,-0.06404,0.01602],"object_to_goal_dist_end":0.36337,"object_to_goal_dist_start":0.36337,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1019.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.59884,0.21452,0.2484],"tcp_start":[0.60327,0.21642,0.22878],"tcp_to_object_dist_end":0.37371,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1e57d18e69439f9d4839513252d085a45363faa5c1c2b52093c9c8149b88bb68`; realized-scene SHA-256: `9bdc6de22965641ffcaccb8421100561fe91fb98e16735236cc25272572d8879`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5456,-0.02923,0.03]},{"name":"goal","value":[0.63284,0.16493,0.17692]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5456,-0.02923,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63284,0.16493,0.17692]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.10625,"average_solve_count":160.0,"average_success_count":160.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force":7.36775,"lift_1.lift_height":0.16006,"transport_1.transport_arc_height":0.18533,"transport_1.transport_speed":0.36018},"optimized_scores":{"best_composite_score":0.02744,"best_fitness_score":0.28244,"best_task_score":0.15595},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":4736.0,"contact_point_centroid":[0.54835,-0.0458,-0.00212],"force_p95":0.12423,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.3215,"mean_force":0.12893,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52389,-0.02705,0.25229]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5172.0,"contact_point_centroid":[0.52997,-0.00876,0.08933],"force_p95":0.14845,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35908,"mean_force":0.10998,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52527,-0.02709,0.09188]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6721.0,"contact_point_centroid":[0.52935,-0.0451,0.0898],"force_p95":0.13784,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30941,"mean_force":0.09138,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52526,-0.02709,0.09111]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54568,-0.02918,-0.00219],"force_p95":0.17662,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2235,"mean_force":0.13615,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53055,-0.02726,0.05197]},{"body_a":"world","body_b":"grasp_target","contact_count":3996.0,"contact_point_centroid":[0.5456,-0.02923,-0.00196],"force_p95":0.12459,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12275,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51493,-0.01166,0.21886]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3889.0,"contact_point_centroid":[0.5316,-0.0082,0.04952],"force_p95":0.11402,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13215,"mean_force":0.05675,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52934,-0.02723,0.05052]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53152,-0.02415,0.10345]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53761,-0.02746,0.06052]},{"body_a":"world","body_b":"grasp_target","contact_count":3820.0,"contact_point_centroid":[0.54862,-0.04651,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.573,0.06064,0.38817]},{"body_a":"world","body_b":"grasp_target","contact_count":2120.0,"contact_point_centroid":[0.54862,-0.04651,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.62769,0.16052,0.25388]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.54862,-0.04651,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.6246,0.1621,0.17896]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4643.0,"contact_point_centroid":[0.53119,-0.04595,0.05106],"force_p95":0.08204,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08659,"mean_force":0.04697,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52935,-0.02723,0.05053]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4570.0,"contact_point_centroid":[0.52399,-0.02704,0.2675],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01609,"mean_force":0.01052,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52365,-0.02704,0.26513]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4071.0,"contact_point_centroid":[0.57345,0.06076,0.39053],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01284,"mean_force":0.01046,"phase_index":5.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.57307,0.06076,0.38819]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2279.0,"contact_point_centroid":[0.62811,0.16054,0.25611],"force_p95":0.01095,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0128,"mean_force":0.01038,"phase_index":6.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.62769,0.16053,0.25375]},{"body_a":"left_finger","body_b":"right_finger","contact_count":221.0,"contact_point_centroid":[0.62766,0.16293,0.17784],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01268,"mean_force":0.01009,"phase_index":7.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62722,0.16292,0.17559]}],"total_contact_groups":16},"final_pose_error":0.00491,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.54862,-0.04651,0.01602],"final_tcp_position":[0.62884,0.16336,0.1793],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":273011.13294,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3996.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52722,-0.01997,0.16384],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13934,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53761,-0.02746,0.06052],"tcp_start":[0.52722,-0.01997,0.16384],"tcp_to_object_dist_end":0.03546,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":160.34347,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":4.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_1","tcp_end":[0.53752,-0.02746,0.0604],"tcp_start":[0.53761,-0.02746,0.06052],"tcp_to_object_dist_end":0.03536,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54578,-0.02774,0.02522],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26022,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.17787,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10332.0,"raw_peak_contact_force":0.2235,"tcp_end":[0.52932,-0.02722,0.05049],"tcp_start":[0.53752,-0.02746,0.0604],"tcp_to_object_dist_end":0.03016,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1835.0,"n_steps_budget":1000.0,"object_pos_end":[0.54862,-0.04651,0.01602],"object_pos_start":[0.54578,-0.02774,0.02522],"object_to_goal_dist_end":0.27873,"object_to_goal_dist_start":0.26022,"object_z_max":0.11063,"peak_contact_force":0.12263,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":21199.0,"raw_peak_contact_force":1.3215,"tcp_end":[0.52414,-0.02707,0.3658],"tcp_start":[0.52577,-0.0271,0.19793],"tcp_to_object_dist_end":0.35117,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":955.0,"n_steps_budget":1000.0,"object_pos_end":[0.54862,-0.04651,0.01602],"object_pos_start":[0.54862,-0.04651,0.01602],"object_to_goal_dist_end":0.27873,"object_to_goal_dist_start":0.27873,"object_z_max":0.01602,"peak_contact_force":273011.13294,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7891.0,"raw_peak_contact_force":0.12263,"subtask_id":"transport_arc","tcp_end":[0.62779,0.15822,0.33203],"tcp_start":[0.52414,-0.02707,0.3658],"tcp_to_object_dist_end":0.38476,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":530.0,"n_steps_budget":1000.0,"object_pos_end":[0.54862,-0.04651,0.01602],"object_pos_start":[0.54862,-0.04651,0.01602],"object_to_goal_dist_end":0.27873,"object_to_goal_dist_start":0.27873,"object_z_max":0.01602,"peak_contact_force":9748.69543,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4399.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62884,0.16336,0.1793],"tcp_start":[0.62779,0.15822,0.33203],"tcp_to_object_dist_end":0.27774,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54862,-0.04651,0.01602],"object_pos_start":[0.54862,-0.04651,0.01602],"object_to_goal_dist_end":0.27873,"object_to_goal_dist_start":0.27873,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1021.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.62306,0.1616,0.19827],"tcp_start":[0.62884,0.16336,0.1793],"tcp_to_object_dist_end":0.28647,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `5836f8a66456087ed82e2e1accc6472c2a7681a19bf8e3d54637158aadaafc47`; realized-scene SHA-256: `776f3cbcac69f75f44cb26f0b1a492bbf1ced59f3c5fca79400c3f557c2ce565`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.46286,-7e-05,0.03]},{"name":"goal","value":[0.61015,0.15287,0.12219]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.46286,-7e-05,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.61015,0.15287,0.12219]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.11628,"average_solve_count":129.0,"average_success_count":129.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force":7.47363,"lift_1.lift_height":0.11742,"transport_1.transport_arc_height":0.21766,"transport_1.transport_speed":0.29811},"optimized_scores":{"best_composite_score":0.34105,"best_fitness_score":0.59605,"best_task_score":0.25142},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2711.0,"contact_point_centroid":[0.46399,0.05064,-0.00241],"force_p95":0.18241,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.81454,"mean_force":0.14577,"phase_index":5.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51678,0.06723,0.2691]},{"body_a":"world","body_b":"grasp_target","contact_count":121.0,"contact_point_centroid":[0.46006,0.00013,-0.00108],"force_p95":0.35577,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.47334,"mean_force":0.06016,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44946,-0.00022,0.04231]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1902.0,"contact_point_centroid":[0.45264,0.02007,0.16566],"force_p95":0.16627,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31819,"mean_force":0.10051,"phase_index":5.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.44672,0.00173,0.16624]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9997.0,"contact_point_centroid":[0.44942,0.01872,0.09024],"force_p95":0.10334,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31103,"mean_force":0.06713,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.447,-0.00023,0.08813]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1837.0,"contact_point_centroid":[0.45242,-0.01704,0.16401],"force_p95":0.17873,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29867,"mean_force":0.0964,"phase_index":5.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.44641,0.0014,0.16418]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10721.0,"contact_point_centroid":[0.44943,-0.01906,0.08777],"force_p95":0.10142,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.274,"mean_force":0.06334,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44702,-0.00023,0.08621]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.46285,-4e-05,-0.00202],"force_p95":0.12794,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14259,"mean_force":0.12443,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.45186,-0.00019,0.04164]},{"body_a":"world","body_b":"grasp_target","contact_count":3216.0,"contact_point_centroid":[0.46286,-7e-05,-0.00195],"force_p95":0.12703,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12278,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47924,-5e-05,0.20559]},{"body_a":"world","body_b":"grasp_target","contact_count":1588.0,"contact_point_centroid":[0.46286,-7e-05,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45797,-0.00011,0.07929]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.46286,-7e-05,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.45822,-0.00012,0.04787]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.46393,0.0517,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.58914,0.13649,0.20839]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.46393,0.0517,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59249,0.14243,0.16508]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4226.0,"contact_point_centroid":[0.45088,0.01909,0.04268],"force_p95":0.07598,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09429,"mean_force":0.0512,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.45079,-0.0002,0.0406]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5332.0,"contact_point_centroid":[0.45035,-0.01926,0.04273],"force_p95":0.06295,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08752,"mean_force":0.0408,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.45078,-0.0002,0.0406]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2867.0,"contact_point_centroid":[0.51789,0.06791,0.27218],"force_p95":0.01104,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01521,"mean_force":0.01051,"phase_index":5.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51752,0.06791,0.26993]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4276.0,"contact_point_centroid":[0.5895,0.13647,0.2109],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01294,"mean_force":0.01043,"phase_index":6.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.58911,0.13645,0.20862]}],"total_contact_groups":17},"final_pose_error":0.04495,"key_states":{"actual_goal_position":[0.61015,0.15287,0.12219],"final_object_position":[0.46393,0.0517,0.01602],"final_tcp_position":[0.5968,0.14356,0.1641],"realised_goal_position":[0.61015,0.15287,0.12219],"realised_object_initial_position":[0.46286,-7e-05,0.03]},"peak_contact_force":273009.2107,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":805.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.03],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.23148,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3216.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.46064,-9e-05,0.11433],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.08834,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":397.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1588.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.45822,-0.00012,0.04787],"tcp_start":[0.46064,-9e-05,0.11433],"tcp_to_object_dist_end":0.02234,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":205.55248,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":4.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_1","tcp_end":[0.45813,-0.00012,0.04775],"tcp_start":[0.45822,-0.00012,0.04787],"tcp_to_object_dist_end":0.02224,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46276,1e-05,0.02591],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.23314,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12783,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11358.0,"raw_peak_contact_force":0.14259,"tcp_end":[0.45076,-0.0002,0.04057],"tcp_start":[0.45813,-0.00012,0.04775],"tcp_to_object_dist_end":0.01895,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":663.0,"n_steps_budget":750.0,"object_pos_end":[0.45982,-0.00018,0.12421],"object_pos_start":[0.46276,1e-05,0.02591],"object_to_goal_dist_end":0.21454,"object_to_goal_dist_start":0.23314,"object_z_max":0.1241,"peak_contact_force":0.09877,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":20839.0,"raw_peak_contact_force":0.47334,"tcp_end":[0.44705,-0.00022,0.14693],"tcp_start":[0.45076,-0.0002,0.04057],"tcp_to_object_dist_end":0.02607,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.46393,0.0517,0.01602],"object_pos_start":[0.45982,-0.00018,0.12421],"object_to_goal_dist_end":0.20709,"object_to_goal_dist_start":0.21454,"object_z_max":0.16251,"peak_contact_force":273009.2107,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9317.0,"raw_peak_contact_force":1.81454,"subtask_id":"transport_arc","tcp_end":[0.58019,0.12658,0.2805],"tcp_start":[0.44705,-0.00022,0.14693],"tcp_to_object_dist_end":0.29845,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.46393,0.0517,0.01602],"object_pos_start":[0.46393,0.0517,0.01602],"object_to_goal_dist_end":0.20709,"object_to_goal_dist_start":0.20709,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8276.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.5968,0.14356,0.1641],"tcp_start":[0.58019,0.12658,0.2805],"tcp_to_object_dist_end":0.21914,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46393,0.0517,0.01602],"object_pos_start":[0.46393,0.0517,0.01602],"object_to_goal_dist_end":0.20709,"object_to_goal_dist_start":0.20709,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1022.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.59086,0.14197,0.18487],"tcp_start":[0.5968,0.14356,0.1641],"tcp_to_object_dist_end":0.22972,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```