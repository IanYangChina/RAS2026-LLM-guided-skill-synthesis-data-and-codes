## Search State

- **Seed**: 1
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | 0.1204 | 0.19 | ❌ rejected |
| 0 | approach → descend → grasp → approach → release | linear_cartesian | linear_cartesian | — | arc_cartesian | — | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | time_limit | 0 | 0.2458 | 0.25 | ✅ accepted |

**Proposal policy**: task_score is 0.19 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.120) — your mutation base

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
  subtask_id: grasp_1
- id: transport_1
  type: approach
  generator: arc_cartesian
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
  subtask_id: transport_arc
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
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.08]
  - orientation: mode=keep_current
  - parameter_bindings: none
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.02]
  - orientation: mode=keep_current
  - parameter_bindings: none
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **transport_1** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.120
- **task_score** (E): 0.186
- **fitness_score**: 0.570  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.450

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1676 |
| descend_1 | 1.00 | 1.00 | 0.0989 |
| grasp_1 | 1.00 | 1.00 | 0.0111 |
| lift_1 | 1.00 | 1.00 | 0.1229 |
| transport_1 | 0.00 | 1.00 | 0.1113 |
| place_descend | 0.33 | 1.00 | 0.1414 |
| release_1 | 1.00 | 1.00 | 0.0220 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.477, -0.001, 0.138) | (0.479, -0.000, 0.030)→(0.479, -0.000, 0.026) | 0.276→0.278 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.477, -0.001, 0.138)→(0.474, -0.000, 0.040) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.474, -0.000, 0.040)→(0.466, -0.001, 0.032) | (0.479, -0.000, 0.026)→(0.479, -0.001, 0.026) | 0.278→0.278 | 1.00 / 44.333 | 0.143 | 0.206 |
| lift_1 | lift | 1.00 / step_budget | (0.466, -0.001, 0.032)→(0.473, -0.001, 0.154) | (0.479, -0.001, 0.026)→(0.487, -0.001, 0.136) | 0.278→0.244 | 1.00 / 20.333 | 0.151 | 0.568 |
| transport_1 | approach | 0.00 / step_budget | (0.473, -0.001, 0.154)→(0.510, 0.063, 0.234) | (0.487, -0.001, 0.136)→(0.491, 0.026, 0.016) | 0.244→0.254 | 1.00 / 8.333 | 94251.442 | 1.723 |
| place_descend | descend | 0.33 / step_budget | (0.510, 0.063, 0.234)→(0.579, 0.170, 0.180) | (0.491, 0.026, 0.016)→(0.491, 0.026, 0.016) | 0.254→0.254 | 1.00 / 9.000 | 91002.351 | 0.123 |
| release_1 | release | 1.00 / step_budget | (0.579, 0.170, 0.180)→(0.573, 0.168, 0.202) | (0.491, 0.026, 0.016)→(0.491, 0.026, 0.016) | 0.254→0.254 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.219
- phase_score: 0.294
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.approach_1_score: 0.057
- phase_breakdown.transport_arc_score: 0.030
- phase_breakdown.descend_1_score: 0.723
- phase_breakdown.release_1_score: 0.353
- grasp_place_fitness: 0.589

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.589
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.219
- **Median Q (composite search score)**: 0.121
- **K-run variance**: 0.0002
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.354


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.9026,"average_solve_count":154.0,"average_success_count":154.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.13567,"descend_1.grasp_z_offset":6e-05,"lift_1.lift_height":0.20852,"place_descend.place_z_offset":0.03303,"transport_1.arc_height":0.05012,"transport_1.transport_z_offset":0.11313},"optimized_scores":{"best_composite_score":0.13881,"best_fitness_score":0.58881,"best_task_score":0.21875},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3529.0,"contact_point_centroid":[0.48797,0.07454,-0.00226],"force_p95":0.12647,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.85213,"mean_force":0.13658,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.50515,0.08166,0.23438]},{"body_a":"world","body_b":"grasp_target","contact_count":140.0,"contact_point_centroid":[0.49857,0.04225,-0.00121],"force_p95":0.48955,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.66842,"mean_force":0.07969,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48687,0.0433,0.02786]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14306.0,"contact_point_centroid":[0.49163,0.06186,0.095],"force_p95":0.13053,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3146,"mean_force":0.07204,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48871,0.04308,0.09429]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13648.0,"contact_point_centroid":[0.49174,0.02434,0.09649],"force_p95":0.12909,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31059,"mean_force":0.07397,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48877,0.04308,0.09556]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":332.0,"contact_point_centroid":[0.49792,0.061,0.18462],"force_p95":0.24346,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28601,"mean_force":0.13448,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.49439,0.04437,0.19018]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50124,0.04468,-0.00215],"force_p95":0.1656,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2494,"mean_force":0.13417,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48939,0.04355,0.02718]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":150.0,"contact_point_centroid":[0.49837,0.02574,0.1838],"force_p95":0.2193,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23685,"mean_force":0.12692,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.49459,0.04361,0.18922]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4048.0,"contact_point_centroid":[0.48873,0.02425,0.02878],"force_p95":0.08168,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14884,"mean_force":0.05191,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48823,0.04345,0.02596]},{"body_a":"world","body_b":"grasp_target","contact_count":1644.0,"contact_point_centroid":[0.50118,0.04505,-0.00192],"force_p95":0.13462,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12292,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49789,0.01959,0.23671]},{"body_a":"world","body_b":"grasp_target","contact_count":1744.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49565,0.04214,0.10327]},{"body_a":"world","body_b":"grasp_target","contact_count":3012.0,"contact_point_centroid":[0.48784,0.07454,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.53851,0.18128,0.21421]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.48784,0.07454,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55484,0.23619,0.17689]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5017.0,"contact_point_centroid":[0.48872,0.06263,0.02778],"force_p95":0.0742,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08986,"mean_force":0.04483,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48824,0.04345,0.02597]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3592.0,"contact_point_centroid":[0.50607,0.08322,0.23843],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01618,"mean_force":0.01046,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.50569,0.0832,0.23611]},{"body_a":"left_finger","body_b":"right_finger","contact_count":220.0,"contact_point_centroid":[0.55764,0.23744,0.17491],"force_p95":0.0111,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01286,"mean_force":0.01015,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5573,0.23741,0.17268]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3196.0,"contact_point_centroid":[0.53886,0.18103,0.21665],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01284,"mean_force":0.0105,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.53841,0.181,0.2144]}],"total_contact_groups":16},"final_pose_error":0.00998,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.48784,0.07454,0.01602],"final_tcp_position":[0.55875,0.23779,0.17562],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":9748.75159,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":412.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1644.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.49758,0.04032,0.17345],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14755,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":436.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1744.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.49635,0.04419,0.03457],"tcp_start":[0.49758,0.04032,0.17345],"tcp_to_object_dist_end":0.00986,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50107,0.04344,0.02551],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24349,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.15606,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10865.0,"raw_peak_contact_force":0.2494,"subtask_id":"grasp_1","tcp_end":[0.4882,0.04344,0.02593],"tcp_start":[0.49635,0.04419,0.03457],"tcp_to_object_dist_end":0.01288,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50687,0.04306,0.16662],"object_pos_start":[0.50107,0.04344,0.02551],"object_to_goal_dist_end":0.21078,"object_to_goal_dist_start":0.24349,"object_z_max":0.16647,"peak_contact_force":0.23621,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":28094.0,"raw_peak_contact_force":0.66842,"tcp_end":[0.4949,0.04311,0.18841],"tcp_start":[0.4882,0.04344,0.02593],"tcp_to_object_dist_end":0.02486,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48784,0.07454,0.01602],"object_pos_start":[0.50687,0.04306,0.16662],"object_to_goal_dist_end":0.22797,"object_to_goal_dist_start":0.21078,"object_z_max":0.16684,"peak_contact_force":9748.75159,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7603.0,"raw_peak_contact_force":1.85213,"subtask_id":"transport_arc","tcp_end":[0.51853,0.11959,0.26181],"tcp_start":[0.4949,0.04311,0.18841],"tcp_to_object_dist_end":0.25177,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":753.0,"n_steps_budget":1000.0,"object_pos_end":[0.48784,0.07454,0.01602],"object_pos_start":[0.48784,0.07454,0.01602],"object_to_goal_dist_end":0.22797,"object_to_goal_dist_start":0.22797,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":6208.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.55875,0.23779,0.17562],"tcp_start":[0.51853,0.11959,0.26181],"tcp_to_object_dist_end":0.23906,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48784,0.07454,0.01602],"object_pos_start":[0.48784,0.07454,0.01602],"object_to_goal_dist_end":0.22797,"object_to_goal_dist_start":0.22797,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1020.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.5534,0.23547,0.19679],"tcp_start":[0.55875,0.23779,0.17562],"tcp_to_object_dist_end":0.25075,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.89362,"average_solve_count":141.0,"average_success_count":141.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.07796,"descend_1.grasp_z_offset":0.00663,"lift_1.lift_height":0.13369,"place_descend.place_z_offset":0.00428,"transport_1.arc_height":0.20013,"transport_1.transport_z_offset":0.05551},"optimized_scores":{"best_composite_score":0.10157,"best_fitness_score":0.55157,"best_task_score":0.14903},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2232.0,"contact_point_centroid":[0.48735,-0.01545,-0.00243],"force_p95":0.15791,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.76905,"mean_force":0.14242,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.48902,0.00355,0.22403]},{"body_a":"world","body_b":"grasp_target","contact_count":132.0,"contact_point_centroid":[0.47437,-0.01925,-0.00109],"force_p95":0.36761,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5331,"mean_force":0.05438,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46273,-0.01959,0.03536]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11222.0,"contact_point_centroid":[0.46754,-0.00063,0.08604],"force_p95":0.10343,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28392,"mean_force":0.06527,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46524,-0.01954,0.08409]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11704.0,"contact_point_centroid":[0.46753,-0.03843,0.08492],"force_p95":0.10079,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27783,"mean_force":0.0632,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46517,-0.01954,0.08327]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3113.0,"contact_point_centroid":[0.47654,0.0015,0.16563],"force_p95":0.17313,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2351,"mean_force":0.10585,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.47087,-0.01687,0.16692]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3487.0,"contact_point_centroid":[0.47658,-0.03487,0.16606],"force_p95":0.13809,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2327,"mean_force":0.09625,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.47098,-0.01672,0.16768]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47616,-0.02005,-0.00204],"force_p95":0.13651,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17687,"mean_force":0.12641,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46498,-0.01965,0.03465]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.47616,-0.02015,-0.00194],"force_p95":0.13205,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12285,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4863,-0.00909,0.20861]},{"body_a":"world","body_b":"grasp_target","contact_count":996.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47174,-0.01913,0.07911]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.48732,-0.01544,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.55241,0.07585,0.21894]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.48732,-0.01544,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59185,0.12248,0.20075]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5072.0,"contact_point_centroid":[0.46362,-0.00037,0.03634],"force_p95":0.06601,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0986,"mean_force":0.04292,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46387,-0.01962,0.03356]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5394.0,"contact_point_centroid":[0.46349,-0.03887,0.03583],"force_p95":0.06489,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08619,"mean_force":0.04117,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46387,-0.01962,0.03356]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2118.0,"contact_point_centroid":[0.49064,0.00498,0.22913],"force_p95":0.01156,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01587,"mean_force":0.01063,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.49032,0.00499,0.22679]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4298.0,"contact_point_centroid":[0.55268,0.07579,0.22128],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01278,"mean_force":0.01038,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.55235,0.07579,0.21897]},{"body_a":"left_finger","body_b":"right_finger","contact_count":221.0,"contact_point_centroid":[0.59482,0.12314,0.19906],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.011,"mean_force":0.01008,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59435,0.12313,0.19673]}],"total_contact_groups":16},"final_pose_error":0.05095,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.48732,-0.01544,0.01602],"final_tcp_position":[0.59567,0.12328,0.19957],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":273006.80763,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":551.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2200.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.47412,-0.01854,0.11736],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.09137,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":249.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":996.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.47159,-0.01979,0.04131],"tcp_start":[0.47412,-0.01854,0.11736],"tcp_to_object_dist_end":0.01596,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47605,-0.01968,0.02583],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28826,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.13471,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12266.0,"raw_peak_contact_force":0.17687,"subtask_id":"grasp_1","tcp_end":[0.46384,-0.01962,0.03353],"tcp_start":[0.47159,-0.01979,0.04131],"tcp_to_object_dist_end":0.01444,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":723.0,"n_steps_budget":810.0,"object_pos_end":[0.48651,-0.01949,0.1316],"object_pos_start":[0.47605,-0.01968,0.02583],"object_to_goal_dist_end":0.23736,"object_to_goal_dist_start":0.28826,"object_z_max":0.13149,"peak_contact_force":0.11022,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":23058.0,"raw_peak_contact_force":0.5331,"tcp_end":[0.47161,-0.01957,0.14805],"tcp_start":[0.46384,-0.01962,0.03353],"tcp_to_object_dist_end":0.0222,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48732,-0.01544,0.01602],"object_pos_start":[0.48651,-0.01949,0.1316],"object_to_goal_dist_end":0.28554,"object_to_goal_dist_start":0.23736,"object_z_max":0.16371,"peak_contact_force":273005.4527,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":10950.0,"raw_peak_contact_force":1.76905,"subtask_id":"transport_arc","tcp_end":[0.50326,0.0192,0.24692],"tcp_start":[0.47161,-0.01957,0.14805],"tcp_to_object_dist_end":0.23403,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48732,-0.01544,0.01602],"object_pos_start":[0.48732,-0.01544,0.01602],"object_to_goal_dist_end":0.28554,"object_to_goal_dist_start":0.28554,"object_z_max":0.01602,"peak_contact_force":273006.80763,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8298.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.59567,0.12328,0.19957],"tcp_start":[0.50326,0.0192,0.24692],"tcp_to_object_dist_end":0.2543,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48732,-0.01544,0.01602],"object_pos_start":[0.48732,-0.01544,0.01602],"object_to_goal_dist_end":0.28554,"object_to_goal_dist_start":0.28554,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1021.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.59041,0.1221,0.22056],"tcp_start":[0.59567,0.12328,0.19957],"tcp_to_object_dist_end":0.26717,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.88889,"average_solve_count":135.0,"average_success_count":135.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.08486,"descend_1.grasp_z_offset":0.00801,"lift_1.lift_height":0.11196,"place_descend.place_z_offset":0.04833,"transport_1.arc_height":0.05409,"transport_1.transport_z_offset":0.07371},"optimized_scores":{"best_composite_score":0.12081,"best_fitness_score":0.57081,"best_task_score":0.19002},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1461.0,"contact_point_centroid":[0.49927,0.02023,-0.00266],"force_p95":0.31043,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.54759,"mean_force":0.15321,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.49687,0.03618,0.18396]},{"body_a":"world","body_b":"grasp_target","contact_count":128.0,"contact_point_centroid":[0.45685,-0.02502,-0.00112],"force_p95":0.35741,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.50155,"mean_force":0.04961,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44581,-0.02553,0.03749]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9711.0,"contact_point_centroid":[0.44981,-0.00649,0.0796],"force_p95":0.09757,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2729,"mean_force":0.06033,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44826,-0.02548,0.07757]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10149.0,"contact_point_centroid":[0.44964,-0.04445,0.07777],"force_p95":0.09837,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26938,"mean_force":0.0585,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4481,-0.02547,0.07617]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5301.0,"contact_point_centroid":[0.47002,0.01148,0.14653],"force_p95":0.15785,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24265,"mean_force":0.09677,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.46437,-0.00697,0.14635]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5808.0,"contact_point_centroid":[0.47071,-0.02419,0.14728],"force_p95":0.12991,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22262,"mean_force":0.08916,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.46517,-0.00591,0.14751]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45857,-0.0262,-0.00206],"force_p95":0.14143,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19271,"mean_force":0.12763,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44791,-0.02561,0.03669]},{"body_a":"world","body_b":"grasp_target","contact_count":2136.0,"contact_point_centroid":[0.45856,-0.02632,-0.00193],"force_p95":0.13221,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12285,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47847,-0.01182,0.2122]},{"body_a":"world","body_b":"grasp_target","contact_count":1072.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45509,-0.02494,0.08341]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.49932,0.0203,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.54715,0.10516,0.17555]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.49932,0.0203,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57705,0.14813,0.16735]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4826.0,"contact_point_centroid":[0.44683,-0.00636,0.03798],"force_p95":0.06847,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10162,"mean_force":0.04489,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44684,-0.02557,0.03567]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5168.0,"contact_point_centroid":[0.44669,-0.0448,0.03748],"force_p95":0.06724,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07561,"mean_force":0.04294,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44684,-0.02557,0.03567]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1266.0,"contact_point_centroid":[0.49916,0.0388,0.18791],"force_p95":0.01279,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01632,"mean_force":0.01083,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.49888,0.03881,0.18568]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4236.0,"contact_point_centroid":[0.54745,0.10504,0.1778],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0128,"mean_force":0.01052,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.54705,0.10504,0.17558]},{"body_a":"left_finger","body_b":"right_finger","contact_count":219.0,"contact_point_centroid":[0.58001,0.14897,0.16523],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0126,"mean_force":0.01016,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57982,0.14896,0.16317]}],"total_contact_groups":16},"final_pose_error":0.07675,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.49932,0.0203,0.01602],"final_tcp_position":[0.58123,0.14915,0.16585],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":1.54759,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":535.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2136.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.45805,-0.02416,0.12435],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.09835,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":268.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1072.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.45435,-0.02584,0.04289],"tcp_start":[0.45805,-0.02416,0.12435],"tcp_to_object_dist_end":0.0174,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45847,-0.02569,0.02577],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30329,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.13873,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11794.0,"raw_peak_contact_force":0.19271,"subtask_id":"grasp_1","tcp_end":[0.44681,-0.02557,0.03564],"tcp_start":[0.45435,-0.02584,0.04289],"tcp_to_object_dist_end":0.01527,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":573.0,"n_steps_budget":660.0,"object_pos_end":[0.46862,-0.02558,0.11082],"object_pos_start":[0.45847,-0.02569,0.02577],"object_to_goal_dist_end":0.28417,"object_to_goal_dist_start":0.30329,"object_z_max":0.11071,"peak_contact_force":0.10666,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":19988.0,"raw_peak_contact_force":0.50155,"tcp_end":[0.45386,-0.02552,0.12663],"tcp_start":[0.44681,-0.02557,0.03564],"tcp_to_object_dist_end":0.02164,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49932,0.0203,0.01602],"object_pos_start":[0.46862,-0.02558,0.11082],"object_to_goal_dist_end":0.24909,"object_to_goal_dist_start":0.28417,"object_z_max":0.14355,"peak_contact_force":0.12263,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":13836.0,"raw_peak_contact_force":1.54759,"subtask_id":"transport_arc","tcp_end":[0.50809,0.05091,0.19245],"tcp_start":[0.45386,-0.02552,0.12663],"tcp_to_object_dist_end":0.17928,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49932,0.0203,0.01602],"object_pos_start":[0.49932,0.0203,0.01602],"object_to_goal_dist_end":0.24909,"object_to_goal_dist_start":0.24909,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8236.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58123,0.14915,0.16585],"tcp_start":[0.50809,0.05091,0.19245],"tcp_to_object_dist_end":0.21392,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49932,0.0203,0.01602],"object_pos_start":[0.49932,0.0203,0.01602],"object_to_goal_dist_end":0.24909,"object_to_goal_dist_start":0.24909,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1019.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.57544,0.14764,0.18729],"tcp_start":[0.58123,0.14915,0.16585],"tcp_to_object_dist_end":0.22659,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```