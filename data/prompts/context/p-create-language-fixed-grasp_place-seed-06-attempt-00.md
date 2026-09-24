## Search State

- **Seed**: 6
- **Iteration**: 1 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 0 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 2 | 0.3367 | 0.22 | ✅ accepted |

**Proposal policy**: task_score is 0.22 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.337) — your mutation base

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
    - 0.0
    tolerance: 0.01
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
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
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
      - 0.2
      default: 0.1
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
    entity: placement_surface
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  subtask_id: transport_arc
- id: place_descend_1
  type: descend
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
      distance: 0.07
      axis: world_z
      mode: add_to_offset
      sign: negative
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    place_height:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.07
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
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
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none
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
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none
- **place_descend_1** (`descend`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.07, mode=add_to_offset, sign=negative}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.337
- **task_score** (E): 0.216
- **fitness_score**: 0.587  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.250

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2650 |
| descend_1 | 1.00 | 1.00 | 0.0045 |
| grasp_1 | 1.00 | 1.00 | 0.0117 |
| lift_1 | 1.00 | 1.00 | 0.0989 |
| transport_1 | 0.00 | 1.00 | 0.1069 |
| place_descend_1 | 1.00 | 1.00 | 0.0794 |
| release_1 | 1.00 | 1.00 | 0.0246 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.495, 0.023, 0.038) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.495, 0.023, 0.038)→(0.494, 0.023, 0.034) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.494, 0.023, 0.034)→(0.486, 0.023, 0.026) | (0.500, 0.024, 0.026)→(0.500, 0.023, 0.025) | 0.271→0.273 | 1.00 / 41.333 | 0.170 | 0.266 |
| lift_1 | lift | 1.00 / step_budget | (0.486, 0.023, 0.026)→(0.482, 0.022, 0.124) | (0.500, 0.023, 0.025)→(0.500, 0.023, 0.113) | 0.273→0.225 | 1.00 / 24.333 | 0.108 | 0.720 |
| transport_1 | approach | 0.00 / step_budget | (0.482, 0.022, 0.124)→(0.536, 0.106, 0.157) | (0.500, 0.023, 0.113)→(0.511, 0.091, 0.016) | 0.225→0.237 | 1.00 / 8.000 | 0.123 | 1.321 |
| place_descend_1 | descend | 1.00 / step_budget | (0.536, 0.106, 0.157)→(0.532, 0.105, 0.078) | (0.511, 0.091, 0.016)→(0.511, 0.091, 0.016) | 0.237→0.237 | 1.00 / 8.667 | 182003.058 | 0.123 |
| release_1 | release | 1.00 / step_budget | (0.532, 0.105, 0.078)→(0.524, 0.103, 0.101) | (0.511, 0.091, 0.016)→(0.511, 0.091, 0.016) | 0.237→0.237 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.312
- phase_score: 0.368
- phase_breakdown.transport_arc_score: 0.164
- phase_breakdown.approach_1_score: 0.820
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.release_1_score: 0.105
- phase_breakdown.descend_1_score: 0.704
- grasp_place_fitness: 0.634

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.634
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.312
- **Median Q (composite search score)**: 0.320
- **K-run variance**: 0.0011
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 11.0
- **Final σ (mean)**: 0.100


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.63014,"average_solve_count":146.0,"average_success_count":146.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift_1.lift_height":0.11021,"place_descend_1.place_height":0.09624},"optimized_scores":{"best_composite_score":0.30647,"best_fitness_score":0.55647,"best_task_score":0.15629},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2327.0,"contact_point_centroid":[0.50255,0.05896,-0.0023],"force_p95":0.14932,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.34017,"mean_force":0.13966,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51531,0.05151,0.15922]},{"body_a":"world","body_b":"grasp_target","contact_count":137.0,"contact_point_centroid":[0.50078,-0.0143,-0.00114],"force_p95":0.51873,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.7335,"mean_force":0.09154,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48857,-0.01487,0.02741]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9406.0,"contact_point_centroid":[0.48871,0.00404,0.07196],"force_p95":0.10877,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33628,"mean_force":0.06879,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48597,-0.01482,0.07033]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10184.0,"contact_point_centroid":[0.48877,-0.03358,0.07103],"force_p95":0.10348,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31007,"mean_force":0.06452,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48599,-0.01482,0.06988]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3605.0,"contact_point_centroid":[0.49652,0.02274,0.12903],"force_p95":0.16368,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29495,"mean_force":0.10042,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.49226,0.00462,0.1317]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3350.0,"contact_point_centroid":[0.49613,-0.01424,0.12882],"force_p95":0.15842,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25178,"mean_force":0.10011,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.49197,0.00403,0.13134]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50383,-0.01544,-0.00207],"force_p95":0.14455,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21802,"mean_force":0.12856,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49128,-0.0149,0.02688]},{"body_a":"world","body_b":"grasp_target","contact_count":3220.0,"contact_point_centroid":[0.50382,-0.01567,-0.00195],"force_p95":0.12703,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12278,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49845,-0.00738,0.1679]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4083.0,"contact_point_centroid":[0.49084,0.00431,0.02839],"force_p95":0.07818,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12773,"mean_force":0.05184,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49011,-0.01489,0.02566]},{"body_a":"world","body_b":"grasp_target","contact_count":88.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49831,-0.01489,0.03659]},{"body_a":"world","body_b":"grasp_target","contact_count":1040.0,"contact_point_centroid":[0.50238,0.05902,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.52408,0.0744,0.12998]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.50238,0.05902,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.51768,0.07343,0.08907]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4937.0,"contact_point_centroid":[0.49084,-0.034,0.02749],"force_p95":0.07026,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08731,"mean_force":0.04475,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49011,-0.01489,0.02566]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2194.0,"contact_point_centroid":[0.51686,0.05402,0.16295],"force_p95":0.01112,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01622,"mean_force":0.01064,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51658,0.05402,0.16073]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1103.0,"contact_point_centroid":[0.52449,0.07441,0.13215],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01281,"mean_force":0.01051,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.52408,0.0744,0.12997]},{"body_a":"left_finger","body_b":"right_finger","contact_count":225.0,"contact_point_centroid":[0.52155,0.07389,0.08525],"force_p95":0.01093,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01095,"mean_force":0.00992,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.52078,0.07388,0.08336]}],"total_contact_groups":16},"final_pose_error":0.00998,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.50238,0.05902,0.01602],"final_tcp_position":[0.52284,0.07419,0.08601],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":273004.33825,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":806.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3220.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.49912,-0.01482,0.03851],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.01338,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":22.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":88.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.49821,-0.01497,0.03422],"tcp_start":[0.49912,-0.01482,0.03851],"tcp_to_object_dist_end":0.00995,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50368,-0.0148,0.02575],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31189,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.1396,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10820.0,"raw_peak_contact_force":0.21802,"subtask_id":"grasp_1","tcp_end":[0.49008,-0.01489,0.02563],"tcp_start":[0.49821,-0.01497,0.03422],"tcp_to_object_dist_end":0.0136,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":633.0,"n_steps_budget":720.0,"object_pos_end":[0.50372,-0.01479,0.11326],"object_pos_start":[0.50368,-0.0148,0.02575],"object_to_goal_dist_end":0.25692,"object_to_goal_dist_start":0.31189,"object_z_max":0.11316,"peak_contact_force":0.11115,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":19727.0,"raw_peak_contact_force":0.7335,"tcp_end":[0.48602,-0.01481,0.12426],"tcp_start":[0.49008,-0.01489,0.02563],"tcp_to_object_dist_end":0.02084,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50238,0.05902,0.01602],"object_pos_start":[0.50372,-0.01479,0.11326],"object_to_goal_dist_end":0.2784,"object_to_goal_dist_start":0.25692,"object_z_max":0.11738,"peak_contact_force":0.12263,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":11476.0,"raw_peak_contact_force":1.34017,"subtask_id":"transport_arc","tcp_end":[0.52712,0.07481,0.17326],"tcp_start":[0.48602,-0.01481,0.12426],"tcp_to_object_dist_end":0.15996,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":260.0,"n_steps_budget":1000.0,"object_pos_end":[0.50238,0.05902,0.01602],"object_pos_start":[0.50238,0.05902,0.01602],"object_to_goal_dist_end":0.2784,"object_to_goal_dist_start":0.2784,"object_z_max":0.01602,"peak_contact_force":273004.33825,"phase_name":"place_descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2143.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.52284,0.07419,0.08601],"tcp_start":[0.52712,0.07481,0.17326],"tcp_to_object_dist_end":0.07449,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50238,0.05902,0.01602],"object_pos_start":[0.50238,0.05902,0.01602],"object_to_goal_dist_end":0.2784,"object_to_goal_dist_start":0.2784,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1025.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.51581,0.07315,0.11001],"tcp_start":[0.52284,0.07419,0.08601],"tcp_to_object_dist_end":0.09599,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.61806,"average_solve_count":144.0,"average_success_count":144.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift_1.lift_height":0.11031,"place_descend_1.place_height":0.06763},"optimized_scores":{"best_composite_score":0.38368,"best_fitness_score":0.63368,"best_task_score":0.31223},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2279.0,"contact_point_centroid":[0.53491,0.10001,-0.0023],"force_p95":0.14719,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.22514,"mean_force":0.138,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54646,0.09359,0.12592]},{"body_a":"world","body_b":"grasp_target","contact_count":151.0,"contact_point_centroid":[0.50896,0.03528,-0.00133],"force_p95":0.5046,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.71266,"mean_force":0.0976,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49666,0.03695,0.02678]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8842.0,"contact_point_centroid":[0.49755,0.01794,0.07224],"force_p95":0.11141,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36464,"mean_force":0.07271,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49414,0.03676,0.07039]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9695.0,"contact_point_centroid":[0.49726,0.05554,0.06959],"force_p95":0.10643,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34284,"mean_force":0.06833,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49419,0.03676,0.06803]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51264,0.03918,-0.00225],"force_p95":0.19559,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.28627,"mean_force":0.14158,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49953,0.03719,0.02603]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3709.0,"contact_point_centroid":[0.51282,0.07314,0.11837],"force_p95":0.15209,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26755,"mean_force":0.10224,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.50911,0.05515,0.1214]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3399.0,"contact_point_centroid":[0.51205,0.03611,0.11839],"force_p95":0.16994,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23386,"mean_force":0.10282,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.50832,0.0543,0.12136]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3566.0,"contact_point_centroid":[0.5001,0.01792,0.02794],"force_p95":0.09159,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16443,"mean_force":0.05794,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49834,0.0371,0.02476]},{"body_a":"world","body_b":"grasp_target","contact_count":3296.0,"contact_point_centroid":[0.51251,0.03972,-0.00195],"force_p95":0.12693,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12277,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50254,0.01861,0.1676]},{"body_a":"world","body_b":"grasp_target","contact_count":92.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50655,0.0375,0.03612]},{"body_a":"world","body_b":"grasp_target","contact_count":692.0,"contact_point_centroid":[0.53482,0.10012,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.5607,0.11049,0.0994]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.53482,0.10012,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55355,0.10893,0.07128]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4901.0,"contact_point_centroid":[0.49949,0.05634,0.02667],"force_p95":0.08099,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08793,"mean_force":0.04671,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49835,0.0371,0.02477]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2095.0,"contact_point_centroid":[0.54947,0.09624,0.12842],"force_p95":0.01184,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01642,"mean_force":0.01062,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54907,0.09623,0.12628]},{"body_a":"left_finger","body_b":"right_finger","contact_count":738.0,"contact_point_centroid":[0.56126,0.1105,0.10167],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01099,"mean_force":0.01045,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.5607,0.11049,0.09942]},{"body_a":"left_finger","body_b":"right_finger","contact_count":226.0,"contact_point_centroid":[0.55743,0.10965,0.06839],"force_p95":0.01086,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01088,"mean_force":0.00989,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55688,0.10963,0.0662]}],"total_contact_groups":16},"final_pose_error":0.00984,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.53482,0.10012,0.01602],"final_tcp_position":[0.55914,0.11009,0.06932],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":273004.71331,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":825.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3296.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50733,0.03737,0.03815],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.0134,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":23.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":92.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.50652,0.03773,0.03362],"tcp_start":[0.50733,0.03737,0.03815],"tcp_to_object_dist_end":0.00988,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51241,0.03713,0.02521],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21435,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.17807,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10267.0,"raw_peak_contact_force":0.28627,"subtask_id":"grasp_1","tcp_end":[0.49831,0.03709,0.02473],"tcp_start":[0.50652,0.03773,0.03362],"tcp_to_object_dist_end":0.0141,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":633.0,"n_steps_budget":720.0,"object_pos_end":[0.51199,0.03694,0.11227],"object_pos_start":[0.51241,0.03713,0.02521],"object_to_goal_dist_end":0.18114,"object_to_goal_dist_start":0.21435,"object_z_max":0.11216,"peak_contact_force":0.11041,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":18688.0,"raw_peak_contact_force":0.71266,"tcp_end":[0.49422,0.03677,0.12327],"tcp_start":[0.49831,0.03709,0.02473],"tcp_to_object_dist_end":0.02091,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53482,0.10012,0.01602],"object_pos_start":[0.51199,0.03694,0.11227],"object_to_goal_dist_end":0.1746,"object_to_goal_dist_start":0.18114,"object_z_max":0.11229,"peak_contact_force":0.12263,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":11482.0,"raw_peak_contact_force":1.22514,"subtask_id":"transport_arc","tcp_end":[0.56366,0.11102,0.12825],"tcp_start":[0.49422,0.03677,0.12327],"tcp_to_object_dist_end":0.11639,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":173.0,"n_steps_budget":1000.0,"object_pos_end":[0.53482,0.10012,0.01602],"object_pos_start":[0.53482,0.10012,0.01602],"object_to_goal_dist_end":0.1746,"object_to_goal_dist_start":0.1746,"object_z_max":0.01602,"peak_contact_force":273004.71331,"phase_name":"place_descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1430.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.55914,0.11009,0.06932],"tcp_start":[0.56366,0.11102,0.12825],"tcp_to_object_dist_end":0.05943,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53482,0.10012,0.01602],"object_pos_start":[0.53482,0.10012,0.01602],"object_to_goal_dist_end":0.1746,"object_to_goal_dist_start":0.1746,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1026.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.55151,0.1085,0.09175],"tcp_start":[0.55914,0.11009,0.06932],"tcp_to_object_dist_end":0.078,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.63514,"average_solve_count":148.0,"average_success_count":148.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift_1.lift_height":0.11068,"place_descend_1.place_height":0.10052},"optimized_scores":{"best_composite_score":0.32,"best_fitness_score":0.57,"best_task_score":0.17974},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2289.0,"contact_point_centroid":[0.49655,0.11465,-0.00235],"force_p95":0.15498,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.39648,"mean_force":0.14236,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.50319,0.10919,0.15696]},{"body_a":"world","body_b":"grasp_target","contact_count":149.0,"contact_point_centroid":[0.47941,0.0438,-0.00138],"force_p95":0.50092,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.71436,"mean_force":0.09431,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46871,0.0454,0.02861]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10114.0,"contact_point_centroid":[0.46881,0.06408,0.07172],"force_p95":0.10494,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33473,"mean_force":0.06546,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46635,0.04518,0.06997]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48283,0.04822,-0.0023],"force_p95":0.20708,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.29443,"mean_force":0.14516,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47143,0.04567,0.02756]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9696.0,"contact_point_centroid":[0.46895,0.02631,0.0741],"force_p95":0.10751,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29363,"mean_force":0.06671,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46635,0.04518,0.07218]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3044.0,"contact_point_centroid":[0.4793,0.04435,0.13071],"force_p95":0.18049,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28677,"mean_force":0.10648,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.47428,0.06266,0.13184]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3674.0,"contact_point_centroid":[0.4795,0.08165,0.13065],"force_p95":0.16007,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27721,"mean_force":0.09774,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.47481,0.06354,0.13229]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4602.0,"contact_point_centroid":[0.47064,0.02633,0.0296],"force_p95":0.07905,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15344,"mean_force":0.04644,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47031,0.04556,0.02643]},{"body_a":"world","body_b":"grasp_target","contact_count":3252.0,"contact_point_centroid":[0.4827,0.04873,-0.00195],"force_p95":0.12703,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12278,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48852,0.02284,0.16791]},{"body_a":"world","body_b":"grasp_target","contact_count":92.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47832,0.046,0.03685]},{"body_a":"world","body_b":"grasp_target","contact_count":1096.0,"contact_point_centroid":[0.4966,0.11481,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.51405,0.13032,0.12355]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.4966,0.11481,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.50771,0.1287,0.08046]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5466.0,"contact_point_centroid":[0.47023,0.06505,0.02883],"force_p95":0.07907,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08568,"mean_force":0.0428,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47032,0.04557,0.02644]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2153.0,"contact_point_centroid":[0.50518,0.11172,0.16061],"force_p95":0.01158,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01605,"mean_force":0.01065,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.50478,0.1117,0.15836]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1169.0,"contact_point_centroid":[0.51457,0.13034,0.12552],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0128,"mean_force":0.01045,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.51404,0.13032,0.12331]},{"body_a":"left_finger","body_b":"right_finger","contact_count":224.0,"contact_point_centroid":[0.51124,0.12949,0.07657],"force_p95":0.01094,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01262,"mean_force":0.00998,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.51074,0.12947,0.07467]}],"total_contact_groups":16},"final_pose_error":0.00982,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.4966,0.11481,0.01602],"final_tcp_position":[0.51284,0.12999,0.07737],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":1.39648,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":814.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3252.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.47923,0.04585,0.03883],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.01358,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":23.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":92.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.47812,0.04628,0.03436],"tcp_start":[0.47923,0.04585,0.03883],"tcp_to_object_dist_end":0.00983,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48262,0.04588,0.02499],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29251,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.19188,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11868.0,"raw_peak_contact_force":0.29443,"subtask_id":"grasp_1","tcp_end":[0.47028,0.04556,0.0264],"tcp_start":[0.47812,0.04628,0.03436],"tcp_to_object_dist_end":0.01242,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":633.0,"n_steps_budget":720.0,"object_pos_end":[0.48324,0.04548,0.11439],"object_pos_start":[0.48262,0.04588,0.02499],"object_to_goal_dist_end":0.2384,"object_to_goal_dist_start":0.29251,"object_z_max":0.11429,"peak_contact_force":0.10343,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":19959.0,"raw_peak_contact_force":0.71436,"tcp_end":[0.46635,0.04519,0.12582],"tcp_start":[0.47028,0.04556,0.0264],"tcp_to_object_dist_end":0.02039,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4966,0.11481,0.01602],"object_pos_start":[0.48324,0.04548,0.11439],"object_to_goal_dist_end":0.25744,"object_to_goal_dist_start":0.2384,"object_z_max":0.1177,"peak_contact_force":0.12263,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":11160.0,"raw_peak_contact_force":1.39648,"subtask_id":"transport_arc","tcp_end":[0.5171,0.13105,0.1691],"tcp_start":[0.46635,0.04519,0.12582],"tcp_to_object_dist_end":0.1553,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":274.0,"n_steps_budget":1000.0,"object_pos_end":[0.4966,0.11481,0.01602],"object_pos_start":[0.4966,0.11481,0.01602],"object_to_goal_dist_end":0.25744,"object_to_goal_dist_start":0.25744,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"place_descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2265.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.51284,0.12999,0.07737],"tcp_start":[0.5171,0.13105,0.1691],"tcp_to_object_dist_end":0.06525,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4966,0.11481,0.01602],"object_pos_start":[0.4966,0.11481,0.01602],"object_to_goal_dist_end":0.25744,"object_to_goal_dist_start":0.25744,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1024.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.50585,0.12823,0.10142],"tcp_start":[0.51284,0.12999,0.07737],"tcp_to_object_dist_end":0.08694,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```