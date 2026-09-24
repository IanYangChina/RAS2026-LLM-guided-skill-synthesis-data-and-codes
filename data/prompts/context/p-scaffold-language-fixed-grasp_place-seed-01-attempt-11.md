## Search State

- **Seed**: 1
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | admittance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.1066 | 0.18 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.2160 | 0.37 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | admittance_control | position_control | position_control | impedance_control | admittance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.2929 | 0.38 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.1161 | 0.17 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.1617 | 0.34 | ❌ rejected |

**Proposal policy**: task_score is 0.18 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `a2ed2c4162d37489f2d2d0fa0373774d72c951d58f2469e0ba2d602ff46b6cfb`
- Frozen object start: [0.5011821624700257, 0.045046369632593536, 0.03]
- Frozen task target: [0.5644159612719634, 0.2448649447137244, 0.1467747178015728]
- Goal object position: (0.5644159612719634, 0.2448649447137244, 0.1467747178015728)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5644159612719634, 0.2448649447137244, 0.1467747178015728)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5011821624700257, 0.045046369632593536, 0.03)
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
  frozen_object_start: [0.5012, 0.045, 0.03]
  frozen_task_target: [0.5644, 0.2449, 0.1468]
  frozen_object_starts: {'grasp_target': [0.5011821624700257, 0.045046369632593536, 0.03]}
  frozen_targets: {'place_target': [0.5644159612719634, 0.2448649447137244, 0.1467747178015728]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: a2ed2c4162d37489f2d2d0fa0373774d72c951d58f2469e0ba2d602ff46b6cfb

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

## Current Skill (Q=-0.107) — your mutation base

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
    - 0.2
    tolerance: 0.02
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - -1.0
      align_with: world_z
      tolerance: 0.1
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.2
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: approach_1
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: admittance_control
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
    - 0.2
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.1
      - 0.3
      default: 0.2
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
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    transport_arc_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: transport_arc
- id: descend_2
  type: descend
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.01
    tolerance: 0.02
    orientation:
      mode: keep_current
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
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.2], tolerance=0.02
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=world_z, tolerance=0.1
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
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.2], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
- **transport_arc** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_arc_height: status=consumed; consumers=target.offset.z (replace)
- **descend_2** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.01], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings: none
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **retract_1** (`retract`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: -0.107
- **task_score** (E): 0.180
- **fitness_score**: 0.373  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.480

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0300 |
| descend_1 | 1.00 | 1.00 | 0.2198 |
| grasp_1 | 1.00 | 1.00 | 0.0116 |
| lift_1 | 1.00 | 1.00 | 0.0555 |
| transport_arc | 0.00 | 1.00 | 0.0050 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.488, 0.003, 0.285) | (0.479, -0.000, 0.030)→(0.479, -0.000, 0.026) | 0.276→0.278 | 1.00 / 4.000 | 0.127 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.488, 0.003, 0.285)→(0.476, -0.000, 0.066) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 4.000 | 0.123 | 0.127 |
| grasp_1 | grasp | 1.00 / step_budget | (0.476, -0.000, 0.066)→(0.468, -0.000, 0.057) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 25.333 | 0.161 | 0.216 |
| lift_1 | lift | 1.00 / step_budget | (0.472, -0.001, 0.127)→(0.473, 0.004, 0.181) | (0.479, -0.000, 0.026)→(0.477, 0.009, 0.064) | 0.278→0.266 | 1.00 / 10.667 | 0.123 | 0.513 |
| transport_arc | approach | 0.00 / guard_failure | (0.473, 0.004, 0.181)→(0.473, 0.007, 0.186) | (0.477, 0.009, 0.064)→(0.478, 0.011, 0.066) | 0.266→0.264 | 1.00 / 5.667 | 0.082 | 0.169 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.256
- phase_score: 0.231
- phase_breakdown.descend_1_score: 0.726
- phase_breakdown.transport_arc_score: 0.014
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.release_1_score: 0.000
- phase_breakdown.approach_1_score: 0.009
- grasp_place_fitness: 0.579

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.579
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.256
- **Median Q (composite search score)**: -0.206
- **K-run variance**: 0.0211
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.409


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `8110053be9072e64e15984c6424e4a66fe19af4b6c37a60139a43e94cc34ad53`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `46ef03f7b16015a0d14bf26d80c05d326b92c02b0bf759391930f5ab902d1933`; realized-scene SHA-256: `a2ed2c4162d37489f2d2d0fa0373774d72c951d58f2469e0ba2d602ff46b6cfb`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50118,0.04505,0.03]},{"name":"goal","value":[0.56442,0.24486,0.14677]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.50118,0.04505,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.56442,0.24486,0.14677]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.94231,"average_solve_count":104.0,"average_success_count":104.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.22162,"descend_1.grasp_z_offset":0.02002,"lift_1.lift_height":0.19086,"transport_arc.transport_arc_height":0.09266,"transport_arc.transport_clearance":0.20613,"transport_arc.transport_speed":0.19677},"optimized_scores":{"best_composite_score":0.09862,"best_fitness_score":0.57862,"best_task_score":0.25622},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"right_finger","body_b":"grasp_target","contact_count":3985.0,"contact_point_centroid":[0.49338,0.0607,0.11492],"force_p95":0.15679,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30211,"mean_force":0.1119,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49082,0.04244,0.11921]},{"body_a":"world","body_b":"grasp_target","contact_count":84.0,"contact_point_centroid":[0.49965,0.04184,-0.00148],"force_p95":0.26768,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.29981,"mean_force":0.05598,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48813,0.04216,0.05784]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4172.0,"contact_point_centroid":[0.49253,0.02428,0.11493],"force_p95":0.1473,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27716,"mean_force":0.10451,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49081,0.04244,0.11927]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":212.0,"contact_point_centroid":[0.50369,0.063,0.19535],"force_p95":0.20372,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26279,"mean_force":0.13081,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.49691,0.04494,0.19992]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50127,0.04498,-0.00219],"force_p95":0.17915,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23344,"mean_force":0.13634,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49031,0.04236,0.05736]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":337.0,"contact_point_centroid":[0.50347,0.02919,0.19746],"force_p95":0.1397,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17072,"mean_force":0.08283,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.49716,0.04654,0.20223]},{"body_a":"world","body_b":"grasp_target","contact_count":396.0,"contact_point_centroid":[0.50118,0.04505,-0.00168],"force_p95":0.13817,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12391,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49912,0.01353,0.2826]},{"body_a":"world","body_b":"grasp_target","contact_count":1496.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12261,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49725,0.03613,0.16473]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2649.0,"contact_point_centroid":[0.48843,0.02357,0.05226],"force_p95":0.09811,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11773,"mean_force":0.07615,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48923,0.04227,0.05618]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2905.0,"contact_point_centroid":[0.48931,0.06112,0.0526],"force_p95":0.10106,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10145,"mean_force":0.07175,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48924,0.04227,0.05619]}],"total_contact_groups":10},"final_pose_error":0.20711,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.50677,0.04985,0.16597],"final_tcp_position":[0.49792,0.05112,0.20882],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":0.30211,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":100.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02601],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24189,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12223,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":396.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.49876,0.02955,0.26329],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.23779,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":374.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02601],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24189,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1496.0,"raw_peak_contact_force":0.12264,"subtask_id":"descend_1","tcp_end":[0.49729,0.04294,0.06539],"tcp_start":[0.49876,0.02955,0.26329],"tcp_to_object_dist_end":0.03962,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50118,0.04346,0.02533],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24354,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.17493,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":7354.0,"raw_peak_contact_force":0.23344,"subtask_id":"grasp_1","tcp_end":[0.4892,0.04227,0.05615],"tcp_start":[0.49729,0.04294,0.06539],"tcp_to_object_dist_end":0.03309,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":454.0,"n_steps_budget":1000.0,"object_pos_end":[0.50283,0.04375,0.1589],"object_pos_start":[0.50118,0.04346,0.02533],"object_to_goal_dist_end":0.21068,"object_to_goal_dist_start":0.24354,"object_z_max":0.15863,"peak_contact_force":0.12409,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":8241.0,"raw_peak_contact_force":0.30211,"tcp_end":[0.49682,0.04304,0.19669],"tcp_start":[0.4892,0.04227,0.05615],"tcp_to_object_dist_end":0.03828,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":43.0,"n_steps_budget":1000.0,"object_pos_end":[0.50677,0.04985,0.16597],"object_pos_start":[0.50283,0.04375,0.1589],"object_to_goal_dist_end":0.20426,"object_to_goal_dist_start":0.21068,"object_z_max":0.16685,"peak_contact_force":0.0,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":549.0,"raw_peak_contact_force":0.26279,"subtask_id":"transport_arc","tcp_end":[0.49792,0.05112,0.20882],"tcp_start":[0.49682,0.04304,0.19669],"tcp_to_object_dist_end":0.04378,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1efc3ad2e58ea1c47cd56203c4986b53dab7b80d759e458b85d233ccc9cc04bd`; realized-scene SHA-256: `67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47616,-0.02015,0.03]},{"name":"goal","value":[0.63142,0.15919,0.19002]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.47616,-0.02015,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63142,0.15919,0.19002]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.57724,"average_solve_count":123.0,"average_success_count":123.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.26601,"descend_1.grasp_z_offset":0.02032,"lift_1.lift_height":0.1748,"transport_arc.transport_arc_height":0.09028,"transport_arc.transport_clearance":0.19166,"transport_arc.transport_speed":0.41833},"optimized_scores":{"best_composite_score":-0.20638,"best_fitness_score":0.27362,"best_task_score":0.14753},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1346.0,"contact_point_centroid":[0.47239,-0.00764,-0.00222],"force_p95":0.33429,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60577,"mean_force":0.13883,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46867,-0.0183,0.14056]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":601.0,"contact_point_centroid":[0.46566,-1e-05,0.06222],"force_p95":0.21768,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32907,"mean_force":0.11952,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46469,-0.01857,0.0667]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":896.0,"contact_point_centroid":[0.46442,-0.03651,0.06396],"force_p95":0.16051,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27914,"mean_force":0.08156,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46469,-0.01857,0.06807]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.4762,-0.02005,-0.00211],"force_p95":0.1583,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20846,"mean_force":0.131,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46726,-0.01862,0.05877]},{"body_a":"world","body_b":"grasp_target","contact_count":132.0,"contact_point_centroid":[0.47616,-0.02015,-0.00101],"force_p95":0.13842,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12135,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49596,-0.0024,0.29865]},{"body_a":"world","body_b":"grasp_target","contact_count":1740.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12566,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13511,"mean_force":0.123,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48178,-0.01264,0.182]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2175.0,"contact_point_centroid":[0.46753,0.00019,0.05361],"force_p95":0.11579,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13056,"mean_force":0.09113,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46621,-0.01859,0.05769]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.47222,-0.00447,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.46994,-0.01187,0.19245]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3008.0,"contact_point_centroid":[0.46596,-0.03706,0.05369],"force_p95":0.09415,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09492,"mean_force":0.06806,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46622,-0.01859,0.0577]},{"body_a":"left_finger","body_b":"right_finger","contact_count":925.0,"contact_point_centroid":[0.47014,-0.01812,0.16337],"force_p95":0.01308,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01637,"mean_force":0.01096,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46993,-0.01812,0.16103]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4.0,"contact_point_centroid":[0.47013,-0.01188,0.19454],"force_p95":0.01095,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01095,"mean_force":0.01095,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.46994,-0.01187,0.19245]}],"total_contact_groups":11},"final_pose_error":0.25095,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.47222,-0.00447,0.01602],"final_tcp_position":[0.46999,-0.01176,0.1926],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":0.60577,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":34.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02629],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28823,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.1356,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":132.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.49046,-0.00669,0.29644],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.27086,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":435.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02629],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28823,"object_z_max":0.02629,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1740.0,"raw_peak_contact_force":0.13511,"subtask_id":"descend_1","tcp_end":[0.47404,-0.01873,0.06609],"tcp_start":[0.49046,-0.00669,0.29644],"tcp_to_object_dist_end":0.04015,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47613,-0.01901,0.0256],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28794,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.15483,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":6983.0,"raw_peak_contact_force":0.20846,"subtask_id":"grasp_1","tcp_end":[0.46619,-0.01859,0.05766],"tcp_start":[0.47404,-0.01873,0.06609],"tcp_to_object_dist_end":0.03357,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":436.0,"n_steps_budget":900.0,"object_pos_end":[0.47222,-0.00447,0.01602],"object_pos_start":[0.47613,-0.01901,0.0256],"object_to_goal_dist_end":0.28706,"object_to_goal_dist_start":0.28794,"object_z_max":0.04297,"peak_contact_force":0.12263,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":3768.0,"raw_peak_contact_force":0.60577,"tcp_end":[0.46994,-0.01187,0.19245],"tcp_start":[0.47184,-0.01887,0.1811],"tcp_to_object_dist_end":0.1766,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.47222,-0.00447,0.01602],"object_pos_start":[0.47222,-0.00447,0.01602],"object_to_goal_dist_end":0.28706,"object_to_goal_dist_start":0.28706,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8.0,"raw_peak_contact_force":0.12263,"subtask_id":"transport_arc","tcp_end":[0.46999,-0.01176,0.1926],"tcp_start":[0.46994,-0.01187,0.19245],"tcp_to_object_dist_end":0.17675,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `37495cb43897015e78e007c86af160d11c8460c1ce7249e5c03dce38206c0daf`; realized-scene SHA-256: `5ce27bcdb8582e1d517b17df0f9c2ad7b05701113a75707627744a889253e6a7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45856,-0.02632,0.03]},{"name":"goal","value":[0.63013,0.20822,0.11412]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.45856,-0.02632,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63013,0.20822,0.11412]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.55652,"average_solve_count":115.0,"average_success_count":115.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.26602,"descend_1.grasp_z_offset":0.02,"lift_1.lift_height":0.13792,"transport_arc.transport_arc_height":0.0794,"transport_arc.transport_clearance":0.29393,"transport_arc.transport_speed":0.43823},"optimized_scores":{"best_composite_score":-0.2119,"best_fitness_score":0.2681,"best_task_score":0.13587},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":869.0,"contact_point_centroid":[0.45489,-0.01765,-0.00232],"force_p95":0.38847,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63072,"mean_force":0.14619,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45145,-0.02442,0.12029]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":617.0,"contact_point_centroid":[0.44888,-0.00624,0.06254],"force_p95":0.21993,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32251,"mean_force":0.11904,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44792,-0.02476,0.06693]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":927.0,"contact_point_centroid":[0.44771,-0.04268,0.06445],"force_p95":0.16174,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27499,"mean_force":0.08066,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44797,-0.02476,0.06853]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.4586,-0.02622,-0.00211],"force_p95":0.15721,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20734,"mean_force":0.13071,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.45017,-0.02484,0.05863]},{"body_a":"world","body_b":"grasp_target","contact_count":276.0,"contact_point_centroid":[0.45856,-0.02632,-0.00154],"force_p95":0.13832,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12464,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48808,-0.00664,0.29712]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2176.0,"contact_point_centroid":[0.45054,-0.00602,0.05363],"force_p95":0.11563,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13003,"mean_force":0.09109,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44915,-0.02481,0.05763]},{"body_a":"world","body_b":"grasp_target","contact_count":1748.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12273,"mean_force":0.12259,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.46526,-0.01994,0.18065]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.45454,-0.01357,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12261,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.45204,-0.01967,0.15536]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3004.0,"contact_point_centroid":[0.44894,-0.04327,0.05366],"force_p95":0.09394,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09474,"mean_force":0.06813,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44916,-0.02481,0.05764]},{"body_a":"left_finger","body_b":"right_finger","contact_count":421.0,"contact_point_centroid":[0.45317,-0.02394,0.14391],"force_p95":0.01374,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01623,"mean_force":0.01129,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45287,-0.02394,0.14176]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4.0,"contact_point_centroid":[0.4522,-0.01967,0.15745],"force_p95":0.01094,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01094,"mean_force":0.01094,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.45204,-0.01967,0.15536]}],"total_contact_groups":11},"final_pose_error":0.2916,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.45454,-0.01357,0.01602],"final_tcp_position":[0.45208,-0.01958,0.15554],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":0.63072,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":70.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02591],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30368,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12284,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":276.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.47474,-0.01498,0.29431],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.26913,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":437.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02591],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30368,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1748.0,"raw_peak_contact_force":0.12273,"subtask_id":"descend_1","tcp_end":[0.45675,-0.02505,0.06546],"tcp_start":[0.47474,-0.01498,0.29431],"tcp_to_object_dist_end":0.03951,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45853,-0.0252,0.02561],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30293,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.1538,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":6980.0,"raw_peak_contact_force":0.20734,"subtask_id":"grasp_1","tcp_end":[0.44913,-0.0248,0.0576],"tcp_start":[0.45675,-0.02505,0.06546],"tcp_to_object_dist_end":0.03335,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":316.0,"n_steps_budget":690.0,"object_pos_end":[0.45454,-0.01357,0.01602],"object_pos_start":[0.45853,-0.0252,0.02561],"object_to_goal_dist_end":0.29941,"object_to_goal_dist_start":0.30293,"object_z_max":0.04373,"peak_contact_force":0.12263,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":2834.0,"raw_peak_contact_force":0.63072,"tcp_end":[0.45204,-0.01967,0.15536],"tcp_start":[0.45381,-0.02498,0.14435],"tcp_to_object_dist_end":0.1395,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.45454,-0.01357,0.01602],"object_pos_start":[0.45454,-0.01357,0.01602],"object_to_goal_dist_end":0.2994,"object_to_goal_dist_start":0.2994,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8.0,"raw_peak_contact_force":0.12263,"subtask_id":"transport_arc","tcp_end":[0.45208,-0.01958,0.15554],"tcp_start":[0.45204,-0.01967,0.15536],"tcp_to_object_dist_end":0.13967,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```