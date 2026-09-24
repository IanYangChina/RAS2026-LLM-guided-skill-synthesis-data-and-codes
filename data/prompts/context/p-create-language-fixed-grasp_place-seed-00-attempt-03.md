## Search State

- **Seed**: 0
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | 5 | 0.2553 | 0.32 | ✅ accepted |
| 2 | approach → descend → grasp → approach → release | linear_cartesian | linear_cartesian | — | arc_cartesian | — | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | time_limit | 2 | 0.1528 | 0.25 | ✅ accepted |
| 1 | approach → descend → grasp → lift → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 4 | 0.2796 | 0.21 | ❌ rejected |
| 0 | approach → descend → grasp → approach → release | linear_cartesian | linear_cartesian | — | arc_cartesian | — | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | time_limit | 2 | 0.1529 | 0.25 | ✅ accepted |

**Proposal policy**: task_score is 0.32 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.255) — your mutation base

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
- id: lift_transport
  type: lift
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
    tolerance: 0.01
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
    lift_speed:
      type: scalar
      range:
      - 0.05
      - 0.5
      default: 0.2
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: grasp_retention
    when: during_phase
    predicate: bilateral_grasp
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: reduce_speed
  subtask_id: transport_arc
- id: place_approach
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
      default: 0.2
      binds_to:
      - path: generator.speed
        mode: replace
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
    orientation:
      mode: keep_current
  subtask_id: release_1

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
- **lift_transport** (`lift`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=grasp_retention, when=during_phase, predicate=bilateral_grasp, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=reduce_speed
- **place_approach** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_speed: status=consumed; consumers=generator.speed (replace)
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.255
- **task_score** (E): 0.318
- **fitness_score**: 0.625  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.370

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1139 |
| descend_1 | 1.00 | 1.00 | 0.1402 |
| grasp_1 | 1.00 | 1.00 | 0.0117 |
| lift_transport | 0.00 | 0.33 | 0.0011 |
| place_approach | 1.00 | 1.00 | 0.0885 |
| release_1 | 1.00 | 1.00 | 0.0219 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.494, 0.001, 0.191) | (0.497, 0.001, 0.030)→(0.497, 0.001, 0.026) | 0.263→0.265 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.494, 0.001, 0.191)→(0.492, 0.001, 0.051) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.265 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.492, 0.001, 0.051)→(0.484, 0.000, 0.043) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.266 | 1.00 / 39.000 | 0.142 | 0.192 |
| lift_transport | lift | 0.00 / guard_failure | (0.540, 0.115, 0.179)→(0.540, 0.116, 0.179) | (0.497, 0.001, 0.026)→(0.557, 0.117, 0.148) | 0.266→0.095 | 0.33 / 1.000 | 0.003 | 0.450 |
| place_approach | approach | 1.00 / step_budget | (0.540, 0.116, 0.179)→(0.577, 0.180, 0.180) | (0.559, 0.121, 0.145)→(0.582, 0.156, 0.016) | 0.092→0.175 | 1.00 / 8.000 | 6499.342 | 1.610 |
| release_1 | release | 1.00 / step_budget | (0.577, 0.180, 0.180)→(0.571, 0.178, 0.201) | (0.582, 0.156, 0.016)→(0.582, 0.156, 0.016) | 0.175→0.175 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.413
- phase_score: 0.479
- phase_breakdown.approach_1_score: 0.038
- phase_breakdown.descend_1_score: 0.895
- phase_breakdown.transport_arc_score: 0.271
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.release_1_score: 0.589
- grasp_place_fitness: 0.678

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.678
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.413
- **Median Q (composite search score)**: 0.230
- **K-run variance**: 0.0014
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.300


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.08247,"average_solve_count":97.0,"average_success_count":97.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.12671,"descend_1.grasp_z_offset":0.01014,"lift_transport.lift_height":0.06411,"lift_transport.lift_speed":0.32716,"place_approach.place_speed":0.27888},"optimized_scores":{"best_composite_score":0.22774,"best_fitness_score":0.59774,"best_task_score":0.24704},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3652.0,"contact_point_centroid":[0.56923,0.11487,-0.00222],"force_p95":0.13268,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.52144,"mean_force":0.13749,"phase_index":4.0,"phase_name":"place_approach","phase_type":"approach","tcp_position_centroid":[0.5384,0.11629,0.19053]},{"body_a":"world","body_b":"grasp_target","contact_count":146.0,"contact_point_centroid":[0.51316,-0.02029,-0.00122],"force_p95":0.34967,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54313,"mean_force":0.21951,"phase_index":3.0,"phase_name":"lift_transport","phase_type":"lift","tcp_position_centroid":[0.49956,-0.02034,0.03723]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4969.0,"contact_point_centroid":[0.51195,0.03322,0.08597],"force_p95":0.12455,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.44822,"mean_force":0.07367,"phase_index":3.0,"phase_name":"lift_transport","phase_type":"lift","tcp_position_centroid":[0.50855,0.01456,0.08427]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4483.0,"contact_point_centroid":[0.51016,-0.00938,0.07943],"force_p95":0.1342,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33312,"mean_force":0.07959,"phase_index":3.0,"phase_name":"lift_transport","phase_type":"lift","tcp_position_centroid":[0.50707,0.00958,0.07732]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5137,-0.02287,-0.00205],"force_p95":0.13816,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17181,"mean_force":0.12683,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50162,-0.02249,0.03677]},{"body_a":"world","body_b":"grasp_target","contact_count":1696.0,"contact_point_centroid":[0.5137,-0.02302,-0.00192],"force_p95":0.13411,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12291,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50332,-0.01005,0.23265]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4104.0,"contact_point_centroid":[0.50101,-0.00326,0.03825],"force_p95":0.07743,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12596,"mean_force":0.0518,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50044,-0.02246,0.03549]},{"body_a":"world","body_b":"grasp_target","contact_count":1500.0,"contact_point_centroid":[0.5137,-0.02302,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5074,-0.02162,0.10419]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.56923,0.11514,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.54635,0.14746,0.21552]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4905.0,"contact_point_centroid":[0.50106,-0.04155,0.03731],"force_p95":0.06955,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09046,"mean_force":0.04472,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50044,-0.02246,0.03549]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3716.0,"contact_point_centroid":[0.5393,0.11786,0.19391],"force_p95":0.01111,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01635,"mean_force":0.01053,"phase_index":4.0,"phase_name":"place_approach","phase_type":"approach","tcp_position_centroid":[0.53894,0.11785,0.19161]},{"body_a":"left_finger","body_b":"right_finger","contact_count":221.0,"contact_point_centroid":[0.54903,0.14818,0.21313],"force_p95":0.01094,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01096,"mean_force":0.01007,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.54867,0.14817,0.21086]}],"total_contact_groups":12},"final_pose_error":0.01024,"key_states":{"actual_goal_position":[0.5541,0.15165,0.22199],"final_object_position":[0.56923,0.11514,0.01602],"final_tcp_position":[0.54986,0.1484,0.21325],"realised_goal_position":[0.5541,0.15165,0.22199],"realised_object_initial_position":[0.5137,-0.02302,0.03]},"peak_contact_force":1.52144,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":425.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.03],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26269,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1696.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50877,-0.02068,0.16501],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1391,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":375.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1500.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.50863,-0.02266,0.04451],"tcp_start":[0.50877,-0.02068,0.16501],"tcp_to_object_dist_end":0.01918,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51359,-0.0224,0.02581],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26537,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.13501,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10809.0,"raw_peak_contact_force":0.17181,"subtask_id":"grasp_1","tcp_end":[0.50041,-0.02246,0.03545],"tcp_start":[0.50863,-0.02266,0.04451],"tcp_to_object_dist_end":0.01633,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":350.0,"n_steps_budget":600.0,"object_pos_end":[0.55068,0.07248,0.13996],"object_pos_start":[0.51359,-0.0224,0.02581],"object_to_goal_dist_end":0.11406,"object_to_goal_dist_start":0.26537,"object_z_max":0.13996,"peak_contact_force":0.0,"phase_name":"lift_transport","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":9598.0,"raw_peak_contact_force":0.54313,"subtask_id":"transport_arc","tcp_end":[0.52617,0.07145,0.16429],"tcp_start":[0.52631,0.07095,0.16398],"tcp_to_object_dist_end":0.03456,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":996.0,"n_steps_budget":1000.0,"object_pos_end":[0.56923,0.11514,0.01602],"object_pos_start":[0.55272,0.07649,0.13717],"object_to_goal_dist_end":0.20973,"object_to_goal_dist_start":0.11334,"object_z_max":0.13717,"peak_contact_force":0.12263,"phase_name":"place_approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7368.0,"raw_peak_contact_force":1.52144,"subtask_id":"release_1","tcp_end":[0.54986,0.1484,0.21325],"tcp_start":[0.52617,0.07145,0.16429],"tcp_to_object_dist_end":0.20095,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56923,0.11514,0.01602],"object_pos_start":[0.56923,0.11514,0.01602],"object_to_goal_dist_end":0.20973,"object_to_goal_dist_start":0.20973,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1021.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.54503,0.14705,0.23577],"tcp_start":[0.54986,0.1484,0.21325],"tcp_to_object_dist_end":0.22337,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.02913,"average_solve_count":103.0,"average_success_count":103.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.15652,"descend_1.grasp_z_offset":0.01265,"lift_transport.lift_height":0.09634,"lift_transport.lift_speed":0.42476,"place_approach.place_speed":0.22633},"optimized_scores":{"best_composite_score":0.30781,"best_fitness_score":0.67781,"best_task_score":0.41278},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":671.0,"contact_point_centroid":[0.58579,0.23777,-0.00354],"force_p95":0.69537,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.77435,"mean_force":0.19051,"phase_index":4.0,"phase_name":"place_approach","phase_type":"approach","tcp_position_centroid":[0.55328,0.22647,0.16162]},{"body_a":"world","body_b":"grasp_target","contact_count":181.0,"contact_point_centroid":[0.50179,0.04711,-0.00144],"force_p95":0.35568,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.44447,"mean_force":0.24379,"phase_index":3.0,"phase_name":"lift_transport","phase_type":"lift","tcp_position_centroid":[0.48812,0.04645,0.04037]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7060.0,"contact_point_centroid":[0.51477,0.12901,0.10354],"force_p95":0.11385,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.4171,"mean_force":0.07412,"phase_index":3.0,"phase_name":"lift_transport","phase_type":"lift","tcp_position_centroid":[0.51095,0.11036,0.10213]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6198.0,"contact_point_centroid":[0.51204,0.0849,0.09776],"force_p95":0.13819,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27954,"mean_force":0.08444,"phase_index":3.0,"phase_name":"lift_transport","phase_type":"lift","tcp_position_centroid":[0.50845,0.1038,0.09563]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50123,0.04486,-0.00214],"force_p95":0.16034,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22795,"mean_force":0.13285,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48964,0.04354,0.03985]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9.0,"contact_point_centroid":[0.55371,0.21927,0.18925],"force_p95":0.13845,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13986,"mean_force":0.0644,"phase_index":4.0,"phase_name":"place_approach","phase_type":"approach","tcp_position_centroid":[0.547,0.20653,0.19647]},{"body_a":"world","body_b":"grasp_target","contact_count":1412.0,"contact_point_centroid":[0.50118,0.04505,-0.0019],"force_p95":0.1356,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12297,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49802,0.01916,0.24704]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.58611,0.23786,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12262,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55355,0.23558,0.1479]},{"body_a":"world","body_b":"grasp_target","contact_count":1832.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49583,0.04178,0.11998]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5038.0,"contact_point_centroid":[0.48838,0.02419,0.04177],"force_p95":0.07035,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11634,"mean_force":0.04297,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48849,0.04344,0.03863]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5513.0,"contact_point_centroid":[0.4882,0.06276,0.04118],"force_p95":0.06989,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07473,"mean_force":0.04095,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4885,0.04344,0.03863]},{"body_a":"left_finger","body_b":"right_finger","contact_count":490.0,"contact_point_centroid":[0.55505,0.23011,0.15884],"force_p95":0.01346,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01633,"mean_force":0.01094,"phase_index":4.0,"phase_name":"place_approach","phase_type":"approach","tcp_position_centroid":[0.55476,0.23007,0.15652]},{"body_a":"left_finger","body_b":"right_finger","contact_count":225.0,"contact_point_centroid":[0.55666,0.2369,0.14586],"force_p95":0.01089,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0109,"mean_force":0.00992,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55623,0.23687,0.14361]}],"total_contact_groups":13},"final_pose_error":0.00998,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.58611,0.23786,0.01602],"final_tcp_position":[0.55788,0.23733,0.14667],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":9748.97801,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":354.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1412.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.49773,0.03964,0.19397],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16808,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":458.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1832.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.49647,0.04416,0.04727],"tcp_start":[0.49773,0.03964,0.19397],"tcp_to_object_dist_end":0.02179,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50113,0.04382,0.02552],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24316,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.15483,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12351.0,"raw_peak_contact_force":0.22795,"subtask_id":"grasp_1","tcp_end":[0.48846,0.04343,0.0386],"tcp_start":[0.49647,0.04416,0.04727],"tcp_to_object_dist_end":0.01821,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":511.0,"n_steps_budget":600.0,"object_pos_end":[0.56339,0.20552,0.16942],"object_pos_start":[0.50113,0.04382,0.02552],"object_to_goal_dist_end":0.04541,"object_to_goal_dist_start":0.24316,"object_z_max":0.16949,"peak_contact_force":0.0094,"phase_name":"lift_transport","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":13439.0,"raw_peak_contact_force":0.44447,"subtask_id":"transport_arc","tcp_end":[0.547,0.20644,0.1965],"tcp_start":[0.54702,0.20428,0.19575],"tcp_to_object_dist_end":0.03167,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":243.0,"n_steps_budget":1000.0,"object_pos_end":[0.58611,0.23786,0.01601],"object_pos_start":[0.56654,0.21292,0.16516],"object_to_goal_dist_end":0.13273,"object_to_goal_dist_start":0.03692,"object_z_max":0.16516,"peak_contact_force":9748.97801,"phase_name":"place_approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1170.0,"raw_peak_contact_force":1.77435,"subtask_id":"release_1","tcp_end":[0.55788,0.23733,0.14667],"tcp_start":[0.547,0.20644,0.1965],"tcp_to_object_dist_end":0.13367,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58611,0.23786,0.01602],"object_pos_start":[0.58611,0.23786,0.01601],"object_to_goal_dist_end":0.13273,"object_to_goal_dist_start":0.13273,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1025.0,"raw_peak_contact_force":0.12264,"subtask_id":"release_1","tcp_end":[0.55194,0.23481,0.16784],"tcp_start":[0.55788,0.23733,0.14667],"tcp_to_object_dist_end":0.15564,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.07692,"average_solve_count":91.0,"average_success_count":91.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.17603,"descend_1.grasp_z_offset":0.02734,"lift_transport.lift_height":0.11677,"lift_transport.lift_speed":0.33698,"place_approach.place_speed":0.25343},"optimized_scores":{"best_composite_score":0.23026,"best_fitness_score":0.60026,"best_task_score":0.2934},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3661.0,"contact_point_centroid":[0.58973,0.11626,-0.00222],"force_p95":0.13144,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.53511,"mean_force":0.13729,"phase_index":4.0,"phase_name":"place_approach","phase_type":"approach","tcp_position_centroid":[0.58863,0.11774,0.17633]},{"body_a":"world","body_b":"grasp_target","contact_count":161.0,"contact_point_centroid":[0.47834,-0.01703,-0.00128],"force_p95":0.29877,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.36133,"mean_force":0.14878,"phase_index":3.0,"phase_name":"lift_transport","phase_type":"lift","tcp_position_centroid":[0.46532,-0.01723,0.05643]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3182.0,"contact_point_centroid":[0.49682,-0.00341,0.09549],"force_p95":0.16354,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30162,"mean_force":0.10985,"phase_index":3.0,"phase_name":"lift_transport","phase_type":"lift","tcp_position_centroid":[0.49411,0.01495,0.09898]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3358.0,"contact_point_centroid":[0.50097,0.03701,0.10082],"force_p95":0.14893,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21874,"mean_force":0.10119,"phase_index":3.0,"phase_name":"lift_transport","phase_type":"lift","tcp_position_centroid":[0.4977,0.0188,0.10426]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47617,-0.0201,-0.00204],"force_p95":0.13692,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17587,"mean_force":0.12616,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46556,-0.01962,0.05551]},{"body_a":"world","body_b":"grasp_target","contact_count":1040.0,"contact_point_centroid":[0.47616,-0.02015,-0.00187],"force_p95":0.13652,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1231,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48823,-0.00805,0.25845]},{"body_a":"world","body_b":"grasp_target","contact_count":1932.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47328,-0.01833,0.13814]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.5898,0.11649,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61873,0.15204,0.18097]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2870.0,"contact_point_centroid":[0.46395,-0.00074,0.05183],"force_p95":0.09458,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09922,"mean_force":0.07184,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46448,-0.0196,0.05441]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3300.0,"contact_point_centroid":[0.4634,-0.03836,0.05171],"force_p95":0.08513,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08672,"mean_force":0.06362,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46448,-0.0196,0.05441]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3683.0,"contact_point_centroid":[0.59055,0.11945,0.17878],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01646,"mean_force":0.0106,"phase_index":4.0,"phase_name":"place_approach","phase_type":"approach","tcp_position_centroid":[0.59026,0.11944,0.17651]},{"body_a":"left_finger","body_b":"right_finger","contact_count":226.0,"contact_point_centroid":[0.62175,0.15288,0.18],"force_p95":0.01086,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01268,"mean_force":0.00989,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62141,0.15287,0.17755]}],"total_contact_groups":12},"final_pose_error":0.01405,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.5898,0.11649,0.01602],"final_tcp_position":[0.62287,0.15303,0.18073],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":9748.9254,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":261.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1040.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.47684,-0.01698,0.2154],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.18941,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":483.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1932.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.47205,-0.01977,0.06225],"tcp_start":[0.47684,-0.01698,0.2154],"tcp_to_object_dist_end":0.03647,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4761,-0.01962,0.02583],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28819,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.13709,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":7970.0,"raw_peak_contact_force":0.17587,"subtask_id":"grasp_1","tcp_end":[0.46445,-0.0196,0.05438],"tcp_start":[0.47205,-0.01977,0.06225],"tcp_to_object_dist_end":0.03083,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":361.0,"n_steps_budget":660.0,"object_pos_end":[0.55705,0.07346,0.13445],"object_pos_start":[0.4761,-0.01962,0.02583],"object_to_goal_dist_end":0.12637,"object_to_goal_dist_start":0.28819,"object_z_max":0.13482,"peak_contact_force":0.0,"phase_name":"lift_transport","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":6701.0,"raw_peak_contact_force":0.36133,"subtask_id":"transport_arc","tcp_end":[0.54704,0.07136,0.17665],"tcp_start":[0.54677,0.07108,0.1764],"tcp_to_object_dist_end":0.04342,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5898,0.11649,0.01602],"object_pos_start":[0.55803,0.07472,0.13377],"object_to_goal_dist_end":0.18393,"object_to_goal_dist_start":0.12524,"object_z_max":0.13377,"peak_contact_force":9748.9254,"phase_name":"place_approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7344.0,"raw_peak_contact_force":1.53511,"subtask_id":"release_1","tcp_end":[0.62287,0.15303,0.18073],"tcp_start":[0.54704,0.07136,0.17665],"tcp_to_object_dist_end":0.17193,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5898,0.11649,0.01602],"object_pos_start":[0.5898,0.11649,0.01602],"object_to_goal_dist_end":0.18393,"object_to_goal_dist_start":0.18393,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1026.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.61718,0.15156,0.20038],"tcp_start":[0.62287,0.15303,0.18073],"tcp_to_object_dist_end":0.18965,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```