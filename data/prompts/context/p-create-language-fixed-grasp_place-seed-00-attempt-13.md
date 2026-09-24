## Search State

- **Seed**: 0
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.1351 | 0.40 | ❌ rejected |
| 12 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | 0.1748 | 0.31 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.3365 | 0.57 | ✅ accepted |
| 10 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | 0.1875 | 0.33 | ✅ accepted |
| 9 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 7 | -0.1181 | 0.32 | ❌ rejected |

**Proposal policy**: task_score is 0.40 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `f07a678caf5b8ea43212ad5a337315ad102b1ae725b01cf669f7af9bd0eea2ea`
- Frozen object start: [0.5136961687321454, -0.02302132862361297, 0.03]
- Frozen task target: [0.5540973523936195, 0.15165276355285293, 0.22199053588004086]
- Goal object position: (0.5540973523936195, 0.15165276355285293, 0.22199053588004086)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5540973523936195, 0.15165276355285293, 0.22199053588004086)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5136961687321454, -0.02302132862361297, 0.03)
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
  frozen_object_start: [0.5137, -0.023, 0.03]
  frozen_task_target: [0.5541, 0.1517, 0.222]
  frozen_object_starts: {'grasp_target': [0.5136961687321454, -0.02302132862361297, 0.03]}
  frozen_targets: {'place_target': [0.5540973523936195, 0.15165276355285293, 0.22199053588004086]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: f07a678caf5b8ea43212ad5a337315ad102b1ae725b01cf669f7af9bd0eea2ea

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

## Current Skill (Q=0.135) — your mutation base

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
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.3
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
    tolerance: 0.01
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
  subtask_id: grasp_1
- id: lift_vertical
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
    tolerance: 0.02
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
    lift_speed:
      type: scalar
      range:
      - 0.05
      - 0.5
      default: 0.2
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 2
    strategy: reduce_speed
- id: transport
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
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.05
      - 0.5
      default: 0.2
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: transport_arc
- id: place_approach
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
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    place_speed:
      type: scalar
      range:
      - 0.05
      - 0.5
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.02], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - grasp_z_offset: status=consumed; consumers=target.offset.z (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none
- **lift_vertical** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.15, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=2, strategy=reduce_speed
- **transport** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **place_approach** (`descend`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.135
- **task_score** (E): 0.396
- **fitness_score**: 0.655  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.520

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0430 |
| descend_1 | 1.00 | 1.00 | 0.2130 |
| grasp_1 | 0.00 | 1.00 | 0.0000 |
| lift_vertical | 1.00 | 1.00 | 0.1028 |
| transport | 0.00 | 1.00 | 0.1210 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, -0.000, 0.271) | (0.497, 0.001, 0.030)→(0.497, 0.001, 0.026) | 0.263→0.265 | 1.00 / 4.000 | 10.911 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.496, -0.000, 0.271)→(0.493, 0.001, 0.058) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.265 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 0.00 / guard_failure | (0.488, 0.001, 0.053)→(0.488, 0.001, 0.053) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.266 | 1.00 / 31.333 | 0.154 | 0.206 |
| lift_vertical | lift | 1.00 / step_budget | (0.488, 0.001, 0.053)→(0.485, 0.001, 0.155) | (0.497, 0.001, 0.026)→(0.494, 0.001, 0.123) | 0.266→0.220 | 1.00 / 22.333 | 0.116 | 0.360 |
| transport | approach | 0.00 / guard_failure | (0.485, 0.001, 0.155)→(0.529, 0.097, 0.211) | (0.494, 0.001, 0.123)→(0.534, 0.102, 0.119) | 0.220→0.140 | 1.00 / 7.667 | 3254.090 | 0.764 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.449
- phase_score: 0.337
- phase_breakdown.approach_1_score: 0.004
- phase_breakdown.descend_1_score: 0.861
- phase_breakdown.transport_arc_score: 0.183
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.release_1_score: 0.000
- grasp_place_fitness: 0.684

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.684
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.449
- **Median Q (composite search score)**: 0.140
- **K-run variance**: 0.0006
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.421


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `096c354712624ed6bd8f9b9cbbbc2b7d35a94d9c1517cfb8353e2e383be5aaf0`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `3798aa6551d21849355469c7d63897f628ac7de9267c18bb4301fe6cfaae0164`; realized-scene SHA-256: `f07a678caf5b8ea43212ad5a337315ad102b1ae725b01cf669f7af9bd0eea2ea`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5137,-0.02302,0.03]},{"name":"goal","value":[0.5541,0.15165,0.22199]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5137,-0.02302,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5541,0.15165,0.22199]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.1134,"average_solve_count":97.0,"average_success_count":97.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.20573,"descend_1.grasp_z_offset":0.01422,"grasp_1.grasp_duration":36.93791,"lift_vertical.lift_height":0.14658,"lift_vertical.lift_speed":0.32562,"place_approach.place_speed":0.17542,"place_approach.place_z_offset":0.04035,"transport.transport_speed":0.14414},"optimized_scores":{"best_composite_score":0.13992,"best_fitness_score":0.65992,"best_task_score":0.40905},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"right_finger","body_b":"grasp_target","contact_count":4019.0,"contact_point_centroid":[0.50226,-0.00325,0.11085],"force_p95":0.13076,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33982,"mean_force":0.09412,"phase_index":3.0,"phase_name":"lift_vertical","phase_type":"lift","tcp_position_centroid":[0.50081,-0.0218,0.11413]},{"body_a":"world","body_b":"grasp_target","contact_count":78.0,"contact_point_centroid":[0.51185,-0.02166,-0.00134],"force_p95":0.29818,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.33704,"mean_force":0.06264,"phase_index":3.0,"phase_name":"lift_vertical","phase_type":"lift","tcp_position_centroid":[0.50297,-0.02187,0.05519]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4203.0,"contact_point_centroid":[0.50189,-0.04026,0.10948],"force_p95":0.13139,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33623,"mean_force":0.09079,"phase_index":3.0,"phase_name":"lift_vertical","phase_type":"lift","tcp_position_centroid":[0.50081,-0.0218,0.11285]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1701.0,"contact_point_centroid":[0.51172,-0.01463,0.19367],"force_p95":0.13218,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31786,"mean_force":0.09901,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.50641,0.00361,0.19744]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.51373,-0.02291,-0.00209],"force_p95":0.14711,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19622,"mean_force":0.12924,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50456,-0.02191,0.05404]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1638.0,"contact_point_centroid":[0.51183,0.0222,0.1939],"force_p95":0.12258,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18699,"mean_force":0.1017,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.5065,0.00388,0.19767]},{"body_a":"world","body_b":"grasp_target","contact_count":412.0,"contact_point_centroid":[0.5137,-0.02302,-0.0017],"force_p95":0.13814,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12384,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50303,-0.00689,0.27797]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3208.0,"contact_point_centroid":[0.50473,-0.00312,0.05086],"force_p95":0.10164,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12887,"mean_force":0.07653,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50422,-0.02189,0.05367]},{"body_a":"world","body_b":"grasp_target","contact_count":1448.0,"contact_point_centroid":[0.5137,-0.02302,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50713,-0.0185,0.15625]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3582.0,"contact_point_centroid":[0.50396,-0.04054,0.05076],"force_p95":0.09453,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09467,"mean_force":0.07008,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50423,-0.02189,0.05368]}],"total_contact_groups":10},"final_pose_error":0.1666,"key_states":{"actual_goal_position":[0.5541,0.15165,0.22199],"final_object_position":[0.52074,0.02882,0.1798],"final_tcp_position":[0.51352,0.02919,0.21658],"realised_goal_position":[0.5541,0.15165,0.22199],"realised_object_initial_position":[0.5137,-0.02302,0.03]},"peak_contact_force":0.33982,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":104.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.03],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26269,"object_z_max":0.03,"peak_contact_force":0.1223,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":412.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50689,-0.0151,0.25273],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.22695,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":362.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1448.0,"raw_peak_contact_force":0.12264,"subtask_id":"descend_1","tcp_end":[0.50908,-0.02199,0.05952],"tcp_start":[0.50689,-0.0151,0.25273],"tcp_to_object_dist_end":0.03383,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51367,-0.02224,0.02574],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26531,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.14246,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":8594.0,"raw_peak_contact_force":0.19622,"subtask_id":"grasp_1","tcp_end":[0.50421,-0.02189,0.05366],"tcp_start":[0.50421,-0.02189,0.05366],"tcp_to_object_dist_end":0.02948,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":370.0,"n_steps_budget":600.0,"object_pos_end":[0.5092,-0.02215,0.14568],"object_pos_start":[0.51367,-0.02222,0.02576],"object_to_goal_dist_end":0.19506,"object_to_goal_dist_start":0.26528,"object_z_max":0.14541,"peak_contact_force":0.11892,"phase_name":"lift_vertical","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":8300.0,"raw_peak_contact_force":0.33982,"tcp_end":[0.50096,-0.02179,0.18075],"tcp_start":[0.50421,-0.02189,0.05366],"tcp_to_object_dist_end":0.03603,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":14.0,"n_steps":182.0,"n_steps_budget":1000.0,"object_pos_end":[0.52074,0.02882,0.1798],"object_pos_start":[0.5092,-0.02215,0.14568],"object_to_goal_dist_end":0.13409,"object_to_goal_dist_start":0.19506,"object_z_max":0.17959,"peak_contact_force":0.31786,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3339.0,"raw_peak_contact_force":0.31786,"subtask_id":"transport_arc","tcp_end":[0.51352,0.02919,0.21658],"tcp_start":[0.50096,-0.02179,0.18075],"tcp_to_object_dist_end":0.03748,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `ed2df336ade3d991e9495251c8398520a59dd014a70bd2d7bb71dc7aefccaa8a`; realized-scene SHA-256: `a2ed2c4162d37489f2d2d0fa0373774d72c951d58f2469e0ba2d602ff46b6cfb`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50118,0.04505,0.03]},{"name":"goal","value":[0.56442,0.24486,0.14677]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.50118,0.04505,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.56442,0.24486,0.14677]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.93277,"average_solve_count":119.0,"average_success_count":119.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.28323,"descend_1.grasp_z_offset":0.01098,"grasp_1.grasp_duration":43.45569,"lift_vertical.lift_height":0.10987,"lift_vertical.lift_speed":0.29139,"place_approach.place_speed":0.209,"place_approach.place_z_offset":0.03215,"transport.transport_speed":0.20397},"optimized_scores":{"best_composite_score":0.16354,"best_fitness_score":0.68354,"best_task_score":0.44857},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1.0,"contact_point_centroid":[0.55332,0.21491,-0.00177],"force_p95":1.64633,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.64633,"mean_force":1.64633,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.55242,0.21844,0.22641]},{"body_a":"world","body_b":"grasp_target","contact_count":84.0,"contact_point_centroid":[0.49893,0.04182,-0.00156],"force_p95":0.33335,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.4204,"mean_force":0.07583,"phase_index":3.0,"phase_name":"lift_vertical","phase_type":"lift","tcp_position_centroid":[0.49111,0.04259,0.05211]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3237.0,"contact_point_centroid":[0.48988,0.02348,0.08937],"force_p95":0.12877,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35627,"mean_force":0.09024,"phase_index":3.0,"phase_name":"lift_vertical","phase_type":"lift","tcp_position_centroid":[0.48905,0.0424,0.09144]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5286.0,"contact_point_centroid":[0.48944,0.06091,0.09311],"force_p95":0.11487,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30233,"mean_force":0.06162,"phase_index":3.0,"phase_name":"lift_vertical","phase_type":"lift","tcp_position_centroid":[0.48898,0.04239,0.09321]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3990.0,"contact_point_centroid":[0.51848,0.09917,0.17153],"force_p95":0.14267,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29089,"mean_force":0.10582,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.51429,0.11732,0.17527]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.50122,0.04491,-0.00224],"force_p95":0.17836,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23013,"mean_force":0.13925,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49274,0.04275,0.05079]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4362.0,"contact_point_centroid":[0.51745,0.13305,0.17095],"force_p95":0.14612,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22253,"mean_force":0.09979,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.51343,0.11488,0.1741]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4645.0,"contact_point_centroid":[0.49304,0.02358,0.05],"force_p95":0.10663,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15248,"mean_force":0.05685,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49241,0.04272,0.05044]},{"body_a":"world","body_b":"grasp_target","contact_count":332.0,"contact_point_centroid":[0.50118,0.04505,-0.00162],"force_p95":0.13823,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12425,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49899,0.01281,0.30146]},{"body_a":"world","body_b":"grasp_target","contact_count":1868.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.1226,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.4974,0.03535,0.18061]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6074.0,"contact_point_centroid":[0.49245,0.0615,0.05085],"force_p95":0.07476,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07731,"mean_force":0.04284,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49242,0.04272,0.05045]}],"total_contact_groups":11},"final_pose_error":0.03506,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.55701,0.23895,0.0269],"final_tcp_position":[0.55255,0.21878,0.22658],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":1.64633,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":84.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02597],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24191,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.1221,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":332.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.49881,0.02782,0.30378],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.27834,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":467.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02597],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24191,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1868.0,"raw_peak_contact_force":0.12264,"subtask_id":"descend_1","tcp_end":[0.4972,0.04311,0.05604],"tcp_start":[0.49881,0.02782,0.30378],"tcp_to_object_dist_end":0.03035,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50115,0.04328,0.02522],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24375,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.17826,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12523.0,"raw_peak_contact_force":0.23013,"subtask_id":"grasp_1","tcp_end":[0.4924,0.04271,0.05043],"tcp_start":[0.4924,0.04271,0.05043],"tcp_to_object_dist_end":0.02669,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":282.0,"n_steps_budget":600.0,"object_pos_end":[0.49943,0.04332,0.11163],"object_pos_start":[0.50115,0.04326,0.02523],"object_to_goal_dist_end":0.21465,"object_to_goal_dist_start":0.24376,"object_z_max":0.11137,"peak_contact_force":0.12488,"phase_name":"lift_vertical","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":8607.0,"raw_peak_contact_force":0.4204,"tcp_end":[0.48875,0.04237,0.14089],"tcp_start":[0.4924,0.04271,0.05043],"tcp_to_object_dist_end":0.03116,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":552.0,"n_steps_budget":1000.0,"object_pos_end":[0.55701,0.23895,0.0269],"object_pos_start":[0.49943,0.04332,0.11163],"object_to_goal_dist_end":0.12025,"object_to_goal_dist_start":0.21465,"object_z_max":0.17218,"peak_contact_force":1.64633,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8353.0,"raw_peak_contact_force":1.64633,"subtask_id":"transport_arc","tcp_end":[0.55255,0.21878,0.22658],"tcp_start":[0.48875,0.04237,0.14089],"tcp_to_object_dist_end":0.20075,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `291bc6f2bd023fc25503740a7343328e565e43fc71fa3c9c5d2fdbe2d4351fd2`; realized-scene SHA-256: `67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47616,-0.02015,0.03]},{"name":"goal","value":[0.63142,0.15919,0.19002]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.47616,-0.02015,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63142,0.15919,0.19002]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.0,"average_solve_count":99.0,"average_success_count":99.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.2087,"descend_1.grasp_z_offset":0.01297,"grasp_1.grasp_duration":60.36209,"lift_vertical.lift_height":0.11014,"lift_vertical.lift_speed":0.49871,"place_approach.place_speed":0.21684,"place_approach.place_z_offset":0.00347,"transport.transport_speed":0.1889},"optimized_scores":{"best_composite_score":0.1018,"best_fitness_score":0.6218,"best_task_score":0.33064},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"right_finger","body_b":"grasp_target","contact_count":2507.0,"contact_point_centroid":[0.49175,0.02752,0.15933],"force_p95":0.15868,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32833,"mean_force":0.09806,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.48935,0.0092,0.16356]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3033.0,"contact_point_centroid":[0.46583,-0.00041,0.0949],"force_p95":0.13689,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31858,"mean_force":0.09302,"phase_index":3.0,"phase_name":"lift_vertical","phase_type":"lift","tcp_position_centroid":[0.46539,-0.01907,0.09786]},{"body_a":"world","body_b":"grasp_target","contact_count":76.0,"contact_point_centroid":[0.47376,-0.01879,-0.00138],"force_p95":0.30379,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.31742,"mean_force":0.06405,"phase_index":3.0,"phase_name":"lift_vertical","phase_type":"lift","tcp_position_centroid":[0.46748,-0.01913,0.05491]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3311.0,"contact_point_centroid":[0.46532,-0.03759,0.09461],"force_p95":0.13253,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31715,"mean_force":0.08681,"phase_index":3.0,"phase_name":"lift_vertical","phase_type":"lift","tcp_position_centroid":[0.46539,-0.01907,0.09771]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2678.0,"contact_point_centroid":[0.49324,-0.00709,0.16065],"force_p95":0.13918,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20997,"mean_force":0.09117,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.49105,0.01109,0.16497]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.47618,-0.02005,-0.00208],"force_p95":0.14434,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.191,"mean_force":0.1285,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46898,-0.01917,0.05379]},{"body_a":"world","body_b":"grasp_target","contact_count":388.0,"contact_point_centroid":[0.47616,-0.02015,-0.00168],"force_p95":0.1382,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12394,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49181,-0.00591,0.27959]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3208.0,"contact_point_centroid":[0.46919,-0.00039,0.05072],"force_p95":0.10144,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12813,"mean_force":0.07656,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46867,-0.01916,0.05349]},{"body_a":"world","body_b":"grasp_target","contact_count":1496.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12261,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47717,-0.01611,0.15746]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3575.0,"contact_point_centroid":[0.46841,-0.0378,0.05061],"force_p95":0.09414,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09431,"mean_force":0.07013,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46867,-0.01916,0.05349]}],"total_contact_groups":10},"final_pose_error":0.19107,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.52353,0.03968,0.1496],"final_tcp_position":[0.51946,0.04202,0.18881],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":9760.30694,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":98.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02601],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28839,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":32.4881,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":388.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.48256,-0.01307,0.25583],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.23002,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":374.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02601],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28839,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1496.0,"raw_peak_contact_force":0.12264,"subtask_id":"descend_1","tcp_end":[0.47329,-0.01925,0.05859],"tcp_start":[0.48256,-0.01307,0.25583],"tcp_to_object_dist_end":0.03271,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47612,-0.01944,0.02577],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.2881,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.14008,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":8587.0,"raw_peak_contact_force":0.191,"subtask_id":"grasp_1","tcp_end":[0.46865,-0.01916,0.05347],"tcp_start":[0.46865,-0.01916,0.05347],"tcp_to_object_dist_end":0.02869,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":274.0,"n_steps_budget":600.0,"object_pos_end":[0.47422,-0.01926,0.11244],"object_pos_start":[0.47613,-0.01943,0.02579],"object_to_goal_dist_end":0.25015,"object_to_goal_dist_start":0.28808,"object_z_max":0.11216,"peak_contact_force":0.1054,"phase_name":"lift_vertical","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":6420.0,"raw_peak_contact_force":0.31858,"tcp_end":[0.46518,-0.01905,0.14419],"tcp_start":[0.46865,-0.01916,0.05347],"tcp_to_object_dist_end":0.03301,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":256.0,"n_steps_budget":1000.0,"object_pos_end":[0.52353,0.03968,0.1496],"object_pos_start":[0.47422,-0.01926,0.11244],"object_to_goal_dist_end":0.16601,"object_to_goal_dist_start":0.25015,"object_z_max":0.14967,"peak_contact_force":9760.30694,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5185.0,"raw_peak_contact_force":0.32833,"subtask_id":"transport_arc","tcp_end":[0.51946,0.04202,0.18881],"tcp_start":[0.46518,-0.01905,0.14419],"tcp_to_object_dist_end":0.03949,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```