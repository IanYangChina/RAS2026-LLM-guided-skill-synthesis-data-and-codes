## Search State

- **Seed**: 3
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | approach → approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.1008 | 0.26 | ✅ accepted |
| 0 | rotate → retract → descend → pull | impedance_motion | arc_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | admittance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 3 | -0.2100 | 0.00 | ✅ accepted |

**Proposal policy**: task_score is 0.26 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

- Task name: push_to_goal
- Frozen realised-scene SHA-256: `35b7946dd60174c5d3e72b05c58367a0800836a817579e6ae5b810157d0560be`
- Frozen object start: [0.45027790005723495, -0.03158273920846803, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.45027790005723495, -0.03158273920846803, 0.025)
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.8
- Force limit: 25.0 N
- Robot initial TCP position: (0.5, 0.0, 0.3)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **object displacement ratio toward goal_object_position**

## Scene Entities

robot:
  model: panda_pusher
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5, 0, 0.3]
objects:
  - name: push_box
    role: manipulated_object
    dynamics: free
    geometry: box
    dimensions_m: [0.05, 0.05, 0.05]
    mass_kg: 0.1
  - name: goal_marker
    role: target_marker
    dynamics: static
    geometry: point
task_landmarks:
  frozen_object_start: [0.4503, -0.0316, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.45027790005723495, -0.03158273920846803, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [0.0497, -0.1184, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: 35b7946dd60174c5d3e72b05c58367a0800836a817579e6ae5b810157d0560be

## Subtask Layer

**Mode**: fixed (subtask targets are defined by the task configuration)

Available subtask IDs for phase binding:
| Subtask ID | Anchor | Target offset (m) | Metric | CMA-ES offset param |
|---|---|---|---|---|
| approach | object | (0.00, 0.08, 0.00) | distance | — |
| contact | object | (0.00, 0.03, 0.00) | distance | — |
| push | goal | (0.00, 0.03, 0.00) | distance | push_depth |

Annotate phases with `subtask_id: <id>` to bind them to a subtask target.
- A phase bound to a subtask receives a navigation waypoint computed from that subtask's anchor and offset.
- Only the **last phase** bound to a given subtask is used for subtask scoring.
- Phases without `subtask_id` are not scored against subtasks but still execute normally.

## Current Skill (Q=0.101) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: task_object
    offset:
    - 0.0
    - 0.0
    - 0.0
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach
- id: contact_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: task_object
    offset:
    - 0.0
    - 0.0
    - 0.0
  parameters:
    contact_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: contact
- id: push_1
  type: push
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.15
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
  parameters:
    push_depth:
      type: scalar
      range:
      - 0.02
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.03
      default: 0.02
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: push
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: world
    offset:
    - 0.0
    - 0.0
    - 0.0
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.1
      - 0.3
      default: 0.2
      binds_to:
      - path: target.offset.z
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=task_object, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **contact_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=task_object, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - contact_speed: status=consumed; consumers=generator.speed (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=task_goal, entity=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.15, mode=add_to_offset, sign=positive}
  - parameter_bindings:
    - push_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **retract_1** (`retract`)
  - target: source=yaml, anchor=world, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - retract_height: status=consumed; consumers=target.offset.z (replace)

## Design Metrics

- **Composite score**: 0.101
- **task_score** (E): 0.256
- **fitness_score**: 0.411  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.310

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2592 |
| contact_1 | 1.00 | 1.00 | 0.0185 |
| push_1 | 0.67 | 1.00 | 0.1564 |
| retract_1 | 0.00 | 1.00 | 0.2593 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.523, 0.002, 0.047) | (0.513, 0.002, 0.025)→(0.518, 0.002, 0.024) | 0.160→0.160 | 1.00 / 4.333 | 252.413 | 283.375 |
| contact_1 | approach | 1.00 / step_budget | (0.523, 0.002, 0.047)→(0.540, 0.002, 0.043) | (0.518, 0.002, 0.024)→(0.519, 0.002, 0.029) | 0.160→0.162 | 1.00 / 3.000 | 190.428 | 226.963 |
| push_1 | push | 0.67 / step_budget | (0.540, 0.002, 0.043)→(0.504, -0.142, 0.023) | (0.519, 0.002, 0.029)→(0.524, -0.042, 0.025) | 0.162→0.118 | 1.00 / 4.000 | 0.245 | 134.847 |
| retract_1 | retract | 0.00 / step_budget | (0.504, -0.142, 0.023)→(0.266, -0.076, 0.099) | (0.524, -0.042, 0.025)→(0.524, -0.042, 0.025) | 0.118→0.118 | 1.00 / 4.000 | 0.245 | 0.245 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.354
- lateral_force_integral: None
- approach_alignment: 0.675
- goal_progress: 0.248
- terminal_score: 0.248
- phase_score: 0.605
- phase_breakdown.approach_score: 0.178
- phase_breakdown.push_score: 0.881
- phase_breakdown.contact_score: 0.430

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.463
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.306
- **Median Q (composite search score)**: 0.123
- **K-run variance**: 0.0029
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Parameters at lower bound**: push_1.push_depth
- **Final σ (mean)**: 0.376


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `01fea9f27a58d64b0f9b0ff0cae1096a52b0da1ad311c77058a75ddb9aab77d2`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `c53c9bf1992485fcf877d50f4ee23d3483b4b9e63e5a19adda2461c26d89c46e`; realized-scene SHA-256: `35b7946dd60174c5d3e72b05c58367a0800836a817579e6ae5b810157d0560be`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45028,-0.03158,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.04972,-0.11842,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.45028,-0.03158,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.75,"average_solve_count":156.0,"average_success_count":156.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.10647,"contact_1.contact_speed":0.08318,"push_1.push_depth":0.02,"push_1.push_tolerance":0.01177,"retract_1.retract_height":0.26359},"optimized_scores":{"best_composite_score":0.02711,"best_fitness_score":0.33711,"best_task_score":0.21391},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":122.0,"contact_point_centroid":[0.46888,-0.02926,0.04615],"force_p95":279.06471,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":287.43204,"mean_force":242.3408,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.45845,-0.02899,0.05008]},{"body_a":"attachment","body_b":"push_box","contact_count":397.0,"contact_point_centroid":[0.48103,-0.03266,0.04425],"force_p95":234.88898,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":239.80068,"mean_force":208.24497,"phase_index":1.0,"phase_name":"contact_1","phase_type":"approach","tcp_position_centroid":[0.47459,-0.03202,0.0451]},{"body_a":"world","body_b":"push_box","contact_count":794.0,"contact_point_centroid":[0.47013,-0.03298,-0.00102],"force_p95":122.67574,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":151.957,"mean_force":104.62665,"phase_index":1.0,"phase_name":"contact_1","phase_type":"approach","tcp_position_centroid":[0.47459,-0.03202,0.0451]},{"body_a":"world","body_b":"push_box","contact_count":3492.0,"contact_point_centroid":[0.45075,-0.03161,-8e-05],"force_p95":111.38963,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":148.52125,"mean_force":8.73835,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47365,-0.01544,0.16215]},{"body_a":"attachment","body_b":"push_box","contact_count":193.0,"contact_point_centroid":[0.47522,-0.04599,0.04289],"force_p95":134.13149,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":139.40483,"mean_force":69.12114,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48456,-0.05054,0.03742]},{"body_a":"world","body_b":"push_box","contact_count":1862.0,"contact_point_centroid":[0.45979,-0.05228,-0.00011],"force_p95":78.93898,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":107.50512,"mean_force":7.4982,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49199,-0.10806,0.02653]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.46217,-0.0564,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.39625,-0.12596,0.06604]}],"total_contact_groups":7},"final_pose_error":0.33629,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.46217,-0.0564,0.02499],"final_tcp_position":[0.28956,-0.09208,0.11948],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":287.43204,"phases":[{"contact_detected":true,"contact_event_count":3.0,"n_steps":886.0,"n_steps_budget":1000.0,"object_pos_end":[0.45374,-0.03235,0.02386],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12642,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":262.43694,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3614.0,"raw_peak_contact_force":287.43204,"subtask_id":"approach","tcp_end":[0.46501,-0.03058,0.04806],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.02675,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":397.0,"n_steps_budget":600.0,"object_pos_end":[0.44743,-0.03299,0.03151],"object_pos_start":[0.45374,-0.03235,0.02386],"object_to_goal_dist_end":0.12845,"object_to_goal_dist_start":0.12642,"object_z_max":0.03195,"peak_contact_force":229.65874,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1191.0,"raw_peak_contact_force":239.80068,"subtask_id":"contact","tcp_end":[0.47743,-0.03299,0.03846],"tcp_start":[0.46501,-0.03058,0.04806],"tcp_to_object_dist_end":0.0308,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":630.0,"n_steps_budget":870.0,"object_pos_end":[0.46217,-0.0564,0.02499],"object_pos_start":[0.44743,-0.03299,0.03151],"object_to_goal_dist_end":0.10096,"object_to_goal_dist_start":0.12845,"object_z_max":0.03548,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2055.0,"raw_peak_contact_force":139.40483,"subtask_id":"push","tcp_end":[0.50211,-0.1592,0.01953],"tcp_start":[0.47743,-0.03299,0.03846],"tcp_to_object_dist_end":0.11042,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.46217,-0.0564,0.02499],"object_pos_start":[0.46217,-0.0564,0.02499],"object_to_goal_dist_end":0.10096,"object_to_goal_dist_start":0.10096,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.28956,-0.09208,0.11948],"tcp_start":[0.50211,-0.1592,0.01953],"tcp_to_object_dist_end":0.19999,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `234a0edc218dcf63b67654ddcfd8b0f12da84040687f62c4c4845001a50f549a`; realized-scene SHA-256: `721a00290a47301d7751e432f1a041db545f1b55cfdb74b1d642c32f5b25f702`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.55317,0.00136,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.05317,-0.15136,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.55317,0.00136,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.81935,"average_solve_count":155.0,"average_success_count":155.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.14184,"contact_1.contact_speed":0.05583,"push_1.push_depth":0.03853,"push_1.push_tolerance":0.00525,"retract_1.retract_height":0.12957},"optimized_scores":{"best_composite_score":0.12267,"best_fitness_score":0.43267,"best_task_score":0.3061},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":93.0,"contact_point_centroid":[0.56225,0.00117,0.04707],"force_p95":262.09816,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":280.18468,"mean_force":221.19659,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5508,0.00113,0.04901]},{"body_a":"attachment","body_b":"push_box","contact_count":368.0,"contact_point_centroid":[0.58168,0.00123,0.04599],"force_p95":217.62532,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":218.04567,"mean_force":204.79064,"phase_index":1.0,"phase_name":"contact_1","phase_type":"approach","tcp_position_centroid":[0.57002,0.0012,0.0471]},{"body_a":"world","body_b":"push_box","contact_count":3468.0,"contact_point_centroid":[0.5534,0.00136,-5e-05],"force_p95":64.1086,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":140.9873,"mean_force":6.21411,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5234,0.00059,0.16312]},{"body_a":"attachment","body_b":"push_box","contact_count":519.0,"contact_point_centroid":[0.57468,-0.02723,0.04597],"force_p95":138.8694,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":140.35898,"mean_force":100.02292,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.56558,-0.03375,0.04637]},{"body_a":"world","body_b":"push_box","contact_count":2747.0,"contact_point_centroid":[0.55,-0.0352,-0.00021],"force_p95":117.96654,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":130.3277,"mean_force":19.29905,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53584,-0.0824,0.03463]},{"body_a":"world","body_b":"push_box","contact_count":1210.0,"contact_point_centroid":[0.56409,0.00134,-0.00064],"force_p95":108.4434,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":109.53048,"mean_force":62.64908,"phase_index":1.0,"phase_name":"contact_1","phase_type":"approach","tcp_position_centroid":[0.56941,0.0012,0.0472]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.54196,-0.04689,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.37338,-0.10616,0.04739]}],"total_contact_groups":7},"final_pose_error":0.25952,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.54196,-0.04689,0.02499],"final_tcp_position":[0.24426,-0.06951,0.0761],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":280.18468,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":868.0,"n_steps_budget":1000.0,"object_pos_end":[0.55805,0.00138,0.02377],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16213,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":245.16105,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3561.0,"raw_peak_contact_force":280.18468,"subtask_id":"approach","tcp_end":[0.56005,0.00118,0.04685],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.02317,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":368.0,"n_steps_budget":600.0,"object_pos_end":[0.56295,0.0014,0.02714],"object_pos_start":[0.55805,0.00138,0.02377],"object_to_goal_dist_end":0.16398,"object_to_goal_dist_start":0.16213,"object_z_max":0.02701,"peak_contact_force":175.8911,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1578.0,"raw_peak_contact_force":218.04567,"subtask_id":"contact","tcp_end":[0.57933,0.00126,0.04601],"tcp_start":[0.56005,0.00118,0.04685],"tcp_to_object_dist_end":0.02499,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54196,-0.04689,0.02499],"object_pos_start":[0.56295,0.0014,0.02714],"object_to_goal_dist_end":0.11132,"object_to_goal_dist_start":0.16398,"object_z_max":0.03555,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3266.0,"raw_peak_contact_force":140.35898,"subtask_id":"push","tcp_end":[0.50227,-0.14237,0.02409],"tcp_start":[0.57933,0.00126,0.04601],"tcp_to_object_dist_end":0.1034,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54196,-0.04689,0.02499],"object_pos_start":[0.54196,-0.04689,0.02499],"object_to_goal_dist_end":0.11132,"object_to_goal_dist_start":0.11132,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.24426,-0.06951,0.0761],"tcp_start":[0.50227,-0.14237,0.02409],"tcp_to_object_dist_end":0.30291,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `107d1233d3b0a09f0fa34aa18231b315c9a1d92237bb254399d486ed8004836a`; realized-scene SHA-256: `b2a76c5d1121259d09d3db2c62740fd8fe93dd873d8f379ba1928ff319a7d266`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5366,0.03695,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.0366,-0.18695,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5366,0.03695,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.85621,"average_solve_count":153.0,"average_success_count":153.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.14767,"contact_1.contact_speed":0.06215,"push_1.push_depth":0.03492,"push_1.push_tolerance":0.0084,"retract_1.retract_height":0.19302},"optimized_scores":{"best_composite_score":0.15262,"best_fitness_score":0.46262,"best_task_score":0.24836},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":89.0,"contact_point_centroid":[0.54702,0.03346,0.04697],"force_p95":262.95952,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":282.50957,"mean_force":223.65522,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5357,0.03338,0.04925]},{"body_a":"attachment","body_b":"push_box","contact_count":368.0,"contact_point_centroid":[0.56543,0.03645,0.04579],"force_p95":222.20802,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":223.04351,"mean_force":209.13389,"phase_index":1.0,"phase_name":"contact_1","phase_type":"approach","tcp_position_centroid":[0.55387,0.03655,0.04728]},{"body_a":"world","body_b":"push_box","contact_count":3373.0,"contact_point_centroid":[0.53679,0.03693,-5e-05],"force_p95":49.4306,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":146.20951,"mean_force":6.18512,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51537,0.01765,0.16352]},{"body_a":"world","body_b":"push_box","contact_count":2621.0,"contact_point_centroid":[0.56554,-0.00929,-0.0002],"force_p95":109.87203,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":124.77601,"mean_force":17.16214,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52987,-0.06083,0.03352]},{"body_a":"attachment","body_b":"push_box","contact_count":458.0,"contact_point_centroid":[0.56548,0.01424,0.04573],"force_p95":117.86397,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":124.47857,"mean_force":95.7018,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5578,0.00612,0.04685]},{"body_a":"world","body_b":"push_box","contact_count":1027.0,"contact_point_centroid":[0.55189,0.03543,-0.00076],"force_p95":114.70884,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":116.80398,"mean_force":75.34139,"phase_index":1.0,"phase_name":"contact_1","phase_type":"approach","tcp_position_centroid":[0.55328,0.03641,0.04737]},{"body_a":"push_box","body_b":"link7","contact_count":33.0,"contact_point_centroid":[0.56677,-0.02114,0.06645],"force_p95":2.64257,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.71371,"mean_force":1.67641,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5337,-0.04731,0.03359]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.56677,-0.02333,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.38576,-0.09589,0.06049]}],"total_contact_groups":8},"final_pose_error":0.28769,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.56677,-0.02333,0.02499],"final_tcp_position":[0.26494,-0.06589,0.10228],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":282.50957,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":845.0,"n_steps_budget":1000.0,"object_pos_end":[0.54075,0.03757,0.02376],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.19195,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":249.64236,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3462.0,"raw_peak_contact_force":282.50957,"subtask_id":"approach","tcp_end":[0.54425,0.03484,0.04705],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.02371,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":368.0,"n_steps_budget":600.0,"object_pos_end":[0.54632,0.03857,0.02855],"object_pos_start":[0.54075,0.03757,0.02376],"object_to_goal_dist_end":0.19421,"object_to_goal_dist_start":0.19195,"object_z_max":0.02841,"peak_contact_force":165.73386,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1395.0,"raw_peak_contact_force":223.04351,"subtask_id":"contact","tcp_end":[0.56427,0.0379,0.0458],"tcp_start":[0.54425,0.03484,0.04705],"tcp_to_object_dist_end":0.0249,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56677,-0.02333,0.02499],"object_pos_start":[0.54632,0.03857,0.02855],"object_to_goal_dist_end":0.14319,"object_to_goal_dist_start":0.19421,"object_z_max":0.03532,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3112.0,"raw_peak_contact_force":124.77601,"subtask_id":"push","tcp_end":[0.50628,-0.12546,0.02467],"tcp_start":[0.56427,0.0379,0.0458],"tcp_to_object_dist_end":0.1187,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56677,-0.02333,0.02499],"object_pos_start":[0.56677,-0.02333,0.02499],"object_to_goal_dist_end":0.14319,"object_to_goal_dist_start":0.14319,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.26494,-0.06589,0.10228],"tcp_start":[0.50628,-0.12546,0.02467],"tcp_to_object_dist_end":0.31446,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```