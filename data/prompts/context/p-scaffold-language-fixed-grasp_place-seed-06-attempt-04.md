## Search State

- **Seed**: 6
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.0095 | 0.37 | ✅ accepted |
| 3 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | admittance_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | 0.0159 | 0.28 | ✅ accepted |
| 2 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | position_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | time_limit | pose_tolerance | pose_tolerance | time_limit | 8 | 0.0726 | 0.24 | ❌ rejected |
| 1 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | position_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | time_limit | pose_tolerance | pose_tolerance | time_limit | 7 | 0.1345 | 0.25 | ✅ accepted |
| 0 | approach → descend → grasp → lift → release | linear_cartesian | linear_cartesian | — | linear_cartesian | — | force_threshold_switch | admittance_control | position_control | position_control | position_control | pose_tolerance | contact_detected | time_limit | pose_tolerance | time_limit | 3 | 0.3184 | 0.17 | ✅ accepted |

**Proposal policy**: task_score is 0.37 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `584133b5261cffac0dd4282704ff39e97bf4d452e60b02507679bbdea5a4de22`
- Frozen object start: [0.5038164351471943, -0.015672913018666156, 0.03]
- Frozen task target: [0.5869067239795378, 0.18744967655878825, 0.24811674852797]
- Goal object position: (0.5869067239795378, 0.18744967655878825, 0.24811674852797)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5869067239795378, 0.18744967655878825, 0.24811674852797)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5038164351471943, -0.015672913018666156, 0.03)
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
  frozen_object_start: [0.5038, -0.0157, 0.03]
  frozen_task_target: [0.5869, 0.1874, 0.2481]
  frozen_object_starts: {'grasp_target': [0.5038164351471943, -0.015672913018666156, 0.03]}
  frozen_targets: {'place_target': [0.5869067239795378, 0.18744967655878825, 0.24811674852797]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 584133b5261cffac0dd4282704ff39e97bf4d452e60b02507679bbdea5a4de22

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

## Current Skill (Q=0.009) — your mutation base

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
    offset:
    - 0.0
    - 0.0
    - 0.0
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
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_1
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: admittance_control
  termination: contact_detected
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    grasp_z_offset:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
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
      distance: 0.2
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
      - 0.1
      - 0.3
      default: 0.2
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.3
      default: 0.1
      binds_to:
      - path: generator.speed
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
    - 0.1
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    arc_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.2
      binds_to:
      - path: generator.arc_height
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.08
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
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: release_1

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - grasp_z_offset: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **lift_1** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.2, mode=add_to_offset, sign=positive}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **transport_arc** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **place_descend** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.009
- **task_score** (E): 0.371
- **fitness_score**: 0.579  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.570

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1503 |
| descend_1 | 1.00 | 1.00 | 0.1158 |
| grasp_1 | 1.00 | 1.00 | 0.0115 |
| lift_1 | 0.67 | 1.00 | 0.1068 |
| transport_arc | 1.00 | 1.00 | 0.2526 |
| place_descend | 1.00 | 1.00 | 0.0867 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, 0.022, 0.155) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.496, 0.022, 0.155)→(0.495, 0.024, 0.039) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.495, 0.024, 0.039)→(0.487, 0.023, 0.031) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.272 | 1.00 / 43.000 | 0.144 | 0.206 |
| lift_1 | lift | 0.67 / step_budget | (0.487, 0.023, 0.031)→(0.483, 0.023, 0.138) | (0.500, 0.024, 0.026)→(0.495, 0.023, 0.122) | 0.272→0.223 | 1.00 / 31.000 | 0.093 | 0.615 |
| transport_arc | approach | 1.00 / step_budget | (0.483, 0.023, 0.138)→(0.588, 0.182, 0.301) | (0.495, 0.023, 0.122)→(0.534, 0.088, 0.080) | 0.223→0.214 | 1.00 / 11.333 | 91005.423 | 1.317 |
| place_descend | descend | 1.00 / step_budget | (0.588, 0.182, 0.301)→(0.594, 0.193, 0.215) | (0.534, 0.088, 0.080)→(0.536, 0.091, 0.049) | 0.214→0.203 | 1.00 / 12.333 | 94279.753 | 0.203 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: 1.000
- terminal_score: 0.817
- phase_score: 0.446
- phase_breakdown.descend_1_score: 0.878
- phase_breakdown.transport_arc_score: 0.142
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.approach_1_score: 0.127
- phase_breakdown.release_1_score: 0.823
- grasp_place_fitness: 0.631

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.631
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.817
- **Median Q (composite search score)**: -0.004
- **K-run variance**: 0.0014
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.369


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `daf90631fcbaf423e19452d0c9b90b9715013985cc94ef12ca0cd881e96195aa`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `94660347aa4f41f6801e53bd449f8df59691da8bebfa4fef4947a3513fe04781`; realized-scene SHA-256: `584133b5261cffac0dd4282704ff39e97bf4d452e60b02507679bbdea5a4de22`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50382,-0.01567,0.03]},{"name":"goal","value":[0.58691,0.18745,0.24812]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.50382,-0.01567,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58691,0.18745,0.24812]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.47111,"average_solve_count":225.0,"average_success_count":225.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.11546,"approach_1.speed":0.0499,"descend_1.grasp_z_offset":0.01155,"descend_1.speed":0.09334,"lift_1.lift_height":0.13949,"lift_1.speed":0.10257,"place_descend.speed":0.04582,"transport_arc.arc_height":0.0514,"transport_arc.speed":0.0969},"optimized_scores":{"best_composite_score":-0.02902,"best_fitness_score":0.54098,"best_task_score":0.12329},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2576.0,"contact_point_centroid":[0.49856,-0.00464,-0.00241],"force_p95":0.12634,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.64254,"mean_force":0.14146,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.53413,0.08451,0.29759]},{"body_a":"world","body_b":"grasp_target","contact_count":128.0,"contact_point_centroid":[0.5004,-0.01535,-0.00109],"force_p95":0.47919,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.67644,"mean_force":0.0866,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48937,-0.01544,0.02906]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11176.0,"contact_point_centroid":[0.48978,0.00344,0.0846],"force_p95":0.1097,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34031,"mean_force":0.07082,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48676,-0.01539,0.08287]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11747.0,"contact_point_centroid":[0.48989,-0.03417,0.08334],"force_p95":0.10672,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30755,"mean_force":0.06796,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48678,-0.01539,0.08196]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1343.0,"contact_point_centroid":[0.49293,0.01048,0.17609],"force_p95":0.18844,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26493,"mean_force":0.12612,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.48826,-0.00771,0.17917]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1777.0,"contact_point_centroid":[0.49256,-0.02519,0.17649],"force_p95":0.17578,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2593,"mean_force":0.10627,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.48842,-0.00733,0.18014]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5038,-0.01554,-0.00202],"force_p95":0.13065,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15404,"mean_force":0.12503,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49204,-0.01548,0.0286]},{"body_a":"world","body_b":"grasp_target","contact_count":1928.0,"contact_point_centroid":[0.50382,-0.01567,-0.00193],"force_p95":0.13308,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12288,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49888,-0.00687,0.22747]},{"body_a":"world","body_b":"grasp_target","contact_count":2740.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49783,-0.01488,0.08981]},{"body_a":"world","body_b":"grasp_target","contact_count":980.0,"contact_point_centroid":[0.49842,-0.00462,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.57986,0.17755,0.29793]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4115.0,"contact_point_centroid":[0.49131,0.00374,0.03013],"force_p95":0.0759,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11258,"mean_force":0.05177,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49085,-0.01546,0.02736]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4883.0,"contact_point_centroid":[0.49138,-0.03454,0.0292],"force_p95":0.06798,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08914,"mean_force":0.0447,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49085,-0.01546,0.02736]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2540.0,"contact_point_centroid":[0.53692,0.08941,0.30431],"force_p95":0.01105,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0157,"mean_force":0.0106,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.53661,0.0894,0.30201]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1053.0,"contact_point_centroid":[0.58036,0.17761,0.2999],"force_p95":0.01095,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01252,"mean_force":0.01038,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.57988,0.17759,0.29761]}],"total_contact_groups":14},"final_pose_error":0.00984,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.49842,-0.00462,0.01602],"final_tcp_position":[0.58279,0.18377,0.25626],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":9748.90357,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":483.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1928.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.4998,-0.01416,0.15436],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12842,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":685.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2740.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.49878,-0.01556,0.03575],"tcp_start":[0.4998,-0.01416,0.15436],"tcp_to_object_dist_end":0.01095,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50368,-0.01531,0.02589],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31213,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12871,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10798.0,"raw_peak_contact_force":0.15404,"subtask_id":"grasp_1","tcp_end":[0.49082,-0.01546,0.02733],"tcp_start":[0.49878,-0.01556,0.03575],"tcp_to_object_dist_end":0.01294,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":20.0,"n_steps":783.0,"n_steps_budget":870.0,"object_pos_end":[0.50331,-0.0154,0.14015],"object_pos_start":[0.50368,-0.01531,0.02589],"object_to_goal_dist_end":0.24452,"object_to_goal_dist_start":0.31213,"object_z_max":0.14005,"peak_contact_force":0.11983,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":23051.0,"raw_peak_contact_force":0.67644,"tcp_end":[0.487,-0.01539,0.15487],"tcp_start":[0.49082,-0.01546,0.02733],"tcp_to_object_dist_end":0.02197,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":917.0,"n_steps_budget":1000.0,"object_pos_end":[0.49842,-0.00462,0.01602],"object_pos_start":[0.50331,-0.0154,0.14015],"object_to_goal_dist_end":0.31399,"object_to_goal_dist_start":0.24452,"object_z_max":0.18128,"peak_contact_force":0.12263,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8236.0,"raw_peak_contact_force":1.64254,"subtask_id":"transport_arc","tcp_end":[0.57828,0.1722,0.33872],"tcp_start":[0.487,-0.01539,0.15487],"tcp_to_object_dist_end":0.37653,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":245.0,"n_steps_budget":1000.0,"object_pos_end":[0.49842,-0.00462,0.01602],"object_pos_start":[0.49842,-0.00462,0.01602],"object_to_goal_dist_end":0.31399,"object_to_goal_dist_start":0.31399,"object_z_max":0.01602,"peak_contact_force":9748.90357,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2033.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.58279,0.18377,0.25626],"tcp_start":[0.57828,0.1722,0.33872],"tcp_to_object_dist_end":0.31674,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `fe7e0be33c0bb4db9d2bbbb069b6113d0e5a69a675a0d70bc1f582243e99e3cf`; realized-scene SHA-256: `8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51251,0.03972,0.03]},{"name":"goal","value":[0.62757,0.17252,0.14502]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.51251,0.03972,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.62757,0.17252,0.14502]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.27099,"average_solve_count":262.0,"average_success_count":262.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.09501,"approach_1.speed":0.02094,"descend_1.grasp_z_offset":0.01981,"descend_1.speed":0.03348,"lift_1.lift_height":0.1007,"lift_1.speed":0.05782,"place_descend.speed":0.09349,"transport_arc.arc_height":0.23576,"transport_arc.speed":0.1471},"optimized_scores":{"best_composite_score":0.06132,"best_fitness_score":0.63132,"best_task_score":0.8174},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":192.0,"contact_point_centroid":[0.508,0.03771,-0.00122],"force_p95":0.32575,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5193,"mean_force":0.09091,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49771,0.0383,0.03901]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2217.0,"contact_point_centroid":[0.61984,0.18226,0.19014],"force_p95":0.17149,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36443,"mean_force":0.10886,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.61636,0.16419,0.19444]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2212.0,"contact_point_centroid":[0.61937,0.14588,0.19034],"force_p95":0.16899,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33782,"mean_force":0.10926,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.61635,0.16419,0.19436]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18434.0,"contact_point_centroid":[0.49576,0.05721,0.08398],"force_p95":0.07774,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30973,"mean_force":0.05277,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49531,0.03812,0.08198]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18182.0,"contact_point_centroid":[0.49581,0.01902,0.08578],"force_p95":0.07845,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30317,"mean_force":0.05284,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49531,0.03812,0.08354]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8377.0,"contact_point_centroid":[0.53725,0.0597,0.19905],"force_p95":0.12489,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25575,"mean_force":0.0754,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.53282,0.07837,0.19801]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8228.0,"contact_point_centroid":[0.54244,0.10213,0.20351],"force_p95":0.11141,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22452,"mean_force":0.07684,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.53781,0.0834,0.2025]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51255,0.03951,-0.00211],"force_p95":0.15407,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21914,"mean_force":0.13105,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50073,0.03856,0.03861]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4080.0,"contact_point_centroid":[0.50004,0.01926,0.04012],"force_p95":0.08003,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14675,"mean_force":0.05187,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49955,0.03846,0.03732]},{"body_a":"world","body_b":"grasp_target","contact_count":2352.0,"contact_point_centroid":[0.51251,0.03972,-0.00194],"force_p95":0.13103,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12283,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50256,0.0178,0.21621]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50631,0.03814,0.07281]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4977.0,"contact_point_centroid":[0.50005,0.0576,0.03913],"force_p95":0.07268,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08091,"mean_force":0.04459,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49956,0.03846,0.03732]}],"total_contact_groups":12},"final_pose_error":0.00975,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.62197,0.16862,0.11556],"final_tcp_position":[0.62128,0.16922,0.1517],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":83.17983,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":589.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2352.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50758,0.03636,0.13292],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.10707,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.50743,0.03911,0.04602],"tcp_start":[0.50758,0.03636,0.13292],"tcp_to_object_dist_end":0.02065,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51244,0.03859,0.02562],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21319,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.14796,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10857.0,"raw_peak_contact_force":0.21914,"subtask_id":"grasp_1","tcp_end":[0.49953,0.03846,0.03728],"tcp_start":[0.50743,0.03911,0.04602],"tcp_to_object_dist_end":0.0174,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":956.0,"n_steps_budget":1000.0,"object_pos_end":[0.50246,0.03815,0.10931],"object_pos_start":[0.51244,0.03859,0.02562],"object_to_goal_dist_end":0.18704,"object_to_goal_dist_start":0.21319,"object_z_max":0.10924,"peak_contact_force":0.06807,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":36808.0,"raw_peak_contact_force":0.5193,"tcp_end":[0.49543,0.03813,0.12819],"tcp_start":[0.49953,0.03846,0.03728],"tcp_to_object_dist_end":0.02015,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":17.0,"n_steps":650.0,"n_steps_budget":1000.0,"object_pos_end":[0.61737,0.15937,0.20722],"object_pos_start":[0.50246,0.03815,0.10931],"object_to_goal_dist_end":0.06438,"object_to_goal_dist_start":0.18704,"object_z_max":0.2143,"peak_contact_force":0.13311,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":16605.0,"raw_peak_contact_force":0.25575,"subtask_id":"transport_arc","tcp_end":[0.6133,0.15963,0.24057],"tcp_start":[0.49543,0.03813,0.12819],"tcp_to_object_dist_end":0.0336,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":21.0,"n_steps":246.0,"n_steps_budget":1000.0,"object_pos_end":[0.62197,0.16862,0.11556],"object_pos_start":[0.61737,0.15937,0.20722],"object_to_goal_dist_end":0.03024,"object_to_goal_dist_start":0.06438,"object_z_max":0.20722,"peak_contact_force":83.17983,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4429.0,"raw_peak_contact_force":0.36443,"subtask_id":"release_1","tcp_end":[0.62128,0.16922,0.1517],"tcp_start":[0.6133,0.15963,0.24057],"tcp_to_object_dist_end":0.03616,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `28f75809d7d1d0a11ca1a36dd459ad950e5a80b6bae34006f33ac9620425f5e5`; realized-scene SHA-256: `f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.4827,0.04873,0.03]},{"name":"goal","value":[0.58187,0.22885,0.23048]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.4827,0.04873,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58187,0.22885,0.23048]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.40816,"average_solve_count":245.0,"average_success_count":245.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.13995,"approach_1.speed":0.05595,"descend_1.grasp_z_offset":0.00855,"descend_1.speed":0.05517,"lift_1.lift_height":0.20682,"lift_1.speed":0.06163,"place_descend.speed":0.07597,"transport_arc.arc_height":0.29561,"transport_arc.speed":0.08072},"optimized_scores":{"best_composite_score":-0.00386,"best_fitness_score":0.56614,"best_task_score":0.17259},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1962.0,"contact_point_centroid":[0.48647,0.10921,-0.00259],"force_p95":0.2407,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.05351,"mean_force":0.15272,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.52654,0.14434,0.30678]},{"body_a":"world","body_b":"grasp_target","contact_count":171.0,"contact_point_centroid":[0.47892,0.04614,-0.00124],"force_p95":0.45571,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65012,"mean_force":0.09879,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46871,0.04709,0.03017]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18241.0,"contact_point_centroid":[0.46725,0.06593,0.07843],"force_p95":0.08118,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31585,"mean_force":0.05603,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4662,0.04686,0.07657]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18117.0,"contact_point_centroid":[0.46728,0.02782,0.08008],"force_p95":0.08361,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27937,"mean_force":0.05585,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4662,0.04686,0.07796]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4487.0,"contact_point_centroid":[0.47102,0.033,0.17794],"force_p95":0.14971,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26263,"mean_force":0.084,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.46656,0.0515,0.17838]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4163.0,"contact_point_centroid":[0.47151,0.0709,0.1803],"force_p95":0.14988,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26075,"mean_force":0.09089,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.46703,0.0522,0.18064]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48274,0.04847,-0.00213],"force_p95":0.16058,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24389,"mean_force":0.13295,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47146,0.04738,0.02948]},{"body_a":"world","body_b":"grasp_target","contact_count":1724.0,"contact_point_centroid":[0.4827,0.04873,-0.00192],"force_p95":0.13411,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12291,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48982,0.02099,0.23924]},{"body_a":"world","body_b":"grasp_target","contact_count":3540.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47793,0.04571,0.10305]},{"body_a":"world","body_b":"grasp_target","contact_count":968.0,"contact_point_centroid":[0.48637,0.10914,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.5735,0.21876,0.28149]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5019.0,"contact_point_centroid":[0.47013,0.02803,0.03125],"force_p95":0.06923,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11364,"mean_force":0.043,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47033,0.04727,0.02834]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5505.0,"contact_point_centroid":[0.46995,0.06659,0.03063],"force_p95":0.0694,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08071,"mean_force":0.04114,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47033,0.04727,0.02834]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1940.0,"contact_point_centroid":[0.53013,0.14919,0.31213],"force_p95":0.01145,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01524,"mean_force":0.01049,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.52968,0.14917,0.30991]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1031.0,"contact_point_centroid":[0.57396,0.21878,0.28379],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01276,"mean_force":0.01046,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.5735,0.21875,0.28151]}],"total_contact_groups":14},"final_pose_error":0.00988,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.48637,0.10914,0.01602],"final_tcp_position":[0.57737,0.225,0.23839],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":273016.01371,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":432.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1724.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.48102,0.04348,0.17799],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15207,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":885.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3540.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.47803,0.04803,0.03616],"tcp_start":[0.48102,0.04348,0.17799],"tcp_to_object_dist_end":0.01118,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4826,0.04742,0.02554],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29116,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.15427,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12324.0,"raw_peak_contact_force":0.24389,"subtask_id":"grasp_1","tcp_end":[0.4703,0.04726,0.02831],"tcp_start":[0.47803,0.04803,0.03616],"tcp_to_object_dist_end":0.01261,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47832,0.04688,0.11737],"object_pos_start":[0.4826,0.04742,0.02554],"object_to_goal_dist_end":0.23798,"object_to_goal_dist_start":0.29116,"object_z_max":0.11727,"peak_contact_force":0.09044,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":36529.0,"raw_peak_contact_force":0.65012,"tcp_end":[0.46625,0.04688,0.12991],"tcp_start":[0.4703,0.04726,0.02831],"tcp_to_object_dist_end":0.0174,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":971.0,"n_steps_budget":1000.0,"object_pos_end":[0.48637,0.10914,0.01602],"object_pos_start":[0.47832,0.04688,0.11737],"object_to_goal_dist_end":0.26353,"object_to_goal_dist_start":0.23798,"object_z_max":0.21846,"peak_contact_force":273016.01371,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":12552.0,"raw_peak_contact_force":2.05351,"subtask_id":"transport_arc","tcp_end":[0.57105,0.21338,0.32436],"tcp_start":[0.46625,0.04688,0.12991],"tcp_to_object_dist_end":0.33632,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":242.0,"n_steps_budget":1000.0,"object_pos_end":[0.48637,0.10914,0.01602],"object_pos_start":[0.48637,0.10914,0.01602],"object_to_goal_dist_end":0.26353,"object_to_goal_dist_start":0.26353,"object_z_max":0.01602,"peak_contact_force":273007.17629,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1999.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.57737,0.225,0.23839],"tcp_start":[0.57105,0.21338,0.32436],"tcp_to_object_dist_end":0.26675,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```