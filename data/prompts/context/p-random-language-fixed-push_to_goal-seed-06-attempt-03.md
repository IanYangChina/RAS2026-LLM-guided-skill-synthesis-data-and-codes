## Search State

- **Seed**: 6
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → contact → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | pose_tolerance | 4 | 0.7898 | 0.72 | ❌ rejected |
| 2 | approach → contact → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | time_limit | 5 | 0.7722 | 0.73 | ✅ accepted |
| 1 | approach → contact → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | pose_tolerance | 4 | -0.0824 | 0.00 | ✅ accepted |
| 0 | align → lift → push → approach → approach → descend → grasp | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | force_threshold_switch | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | -0.0821 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.72 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `5f9daa62d5a7a2b8a7116f2dfbb5f9857bb0d5d4b297d304a4e76a9a270e7ec7`
- Frozen object start: [0.5045797221766332, -0.01880749562239939, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.5045797221766332, -0.01880749562239939, 0.025)
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
  frozen_object_start: [0.5046, -0.0188, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.5045797221766332, -0.01880749562239939, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [-0.0046, -0.1312, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: 5f9daa62d5a7a2b8a7116f2dfbb5f9857bb0d5d4b297d304a4e76a9a270e7ec7

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

## Current Skill (Q=0.790) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
phases:
- id: approach_1
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: push_box
    offset:
    - 0.0
    - 0.08
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
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    entity: push_box
    offset:
    - 0.0
    - 0.03
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    force_threshold:
      type: scalar
      range:
      - 2.0
      - 10.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
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
    entity: goal_marker
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.1
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
    orientation:
      mode: none
  parameters:
    push_depth:
      type: scalar
      range:
      - 0.02
      - 0.25
      default: 0.12
      binds_to:
      - path: target.offset_along_axis.distance
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
  subtask_id: push

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.08, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **contact_1** (`contact`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.03, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - force_threshold: status=consumed; consumers=termination.force_threshold (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=task_goal, entity=goal_marker, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.1, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=none
  - parameter_bindings:
    - push_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.790
- **task_score** (E): 0.720
- **fitness_score**: 0.686  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.230

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2842 |
| contact_1 | 1.00 | 1.00 | 0.0451 |
| push_1 | 1.00 | 1.00 | 0.2186 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, 0.107, 0.040) | (0.500, 0.029, 0.025)→(0.500, 0.029, 0.025) | 0.180→0.180 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / force_exceeded | (0.496, 0.107, 0.040)→(0.495, 0.066, 0.023) | (0.500, 0.029, 0.025)→(0.500, 0.029, 0.025) | 0.180→0.180 | 1.00 / 5.000 | 26.118 | 0.245 |
| push_1 | push | 1.00 / step_budget | (0.495, 0.066, 0.023)→(0.496, -0.152, 0.020) | (0.500, 0.029, 0.025)→(0.541, -0.139, 0.025) | 0.180→0.050 | 1.00 / 3.333 | 2.319 | 53.732 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.972
- lateral_force_integral: None
- approach_alignment: 0.737
- goal_progress: 0.767
- terminal_score: 0.767
- phase_score: 0.656
- phase_breakdown.contact_score: 0.770
- phase_breakdown.approach_score: 0.675
- phase_breakdown.push_score: 0.580

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.701
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.767
- **Median Q (composite search score)**: 0.796
- **K-run variance**: 0.0002
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.378


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `acf3715aaa310bcc73047d49f01e71bc863ef036ae437b7dc851a0f6d3fe40ae`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `ec1d0331416d42e6883eeb3b72499fac99c0735b785eb70ece69dc94e8044fc3`; realized-scene SHA-256: `5f9daa62d5a7a2b8a7116f2dfbb5f9857bb0d5d4b297d304a4e76a9a270e7ec7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50458,-0.01881,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.00458,-0.13119,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.50458,-0.01881,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.33498,"average_solve_count":203.0,"average_success_count":203.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.07511,"contact_1.force_threshold":4.67557,"push_1.push_depth":0.02011,"push_1.speed":0.03556},"optimized_scores":{"best_composite_score":0.79568,"best_fitness_score":0.69235,"best_task_score":0.70504},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":326.0,"contact_point_centroid":[0.50392,-0.06765,0.03796],"force_p95":21.6878,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":34.85266,"mean_force":3.77287,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49647,-0.05702,0.01886]},{"body_a":"push_box","body_b":"link7","contact_count":56.0,"contact_point_centroid":[0.53143,-0.08884,0.05237],"force_p95":29.34147,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":34.07748,"mean_force":5.63876,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49591,-0.08595,0.01876]},{"body_a":"world","body_b":"push_box","contact_count":432.0,"contact_point_centroid":[0.52234,-0.11391,-6e-05],"force_p95":15.28209,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.70393,"mean_force":4.09904,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49651,-0.06699,0.01909]},{"body_a":"world","body_b":"push_box","contact_count":3700.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49929,0.04665,0.17177]},{"body_a":"world","body_b":"push_box","contact_count":1936.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49857,0.03996,0.02573]}],"total_contact_groups":5},"final_pose_error":0.01975,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53197,-0.17185,0.02509],"final_tcp_position":[0.49566,-0.15142,0.01972],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":34.85266,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":925.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3700.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.50051,0.06254,0.03389],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08193,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":484.0,"n_steps_budget":600.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.02499,"peak_contact_force":23.41683,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1936.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.4999,0.01813,0.02151],"tcp_start":[0.50051,0.06254,0.03389],"tcp_to_object_dist_end":0.03739,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":465.0,"n_steps_budget":1000.0,"object_pos_end":[0.53197,-0.17185,0.02509],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.03872,"object_to_goal_dist_start":0.13127,"object_z_max":0.02678,"peak_contact_force":6.46541,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":814.0,"raw_peak_contact_force":34.85266,"subtask_id":"push","tcp_end":[0.49566,-0.15142,0.01972],"tcp_start":[0.4999,0.01813,0.02151],"tcp_to_object_dist_end":0.04201,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `589e611c6c27578474525e3fd29be4fb5907d8bbd5d1ca44922bfd811e342c78`; realized-scene SHA-256: `c8d09cd43835becf8e5eb4413394fad8627e4bf404e9e7726e9f380b60e09752`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51501,0.04767,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.01501,-0.19767,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.51501,0.04767,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.81757,"average_solve_count":148.0,"average_success_count":148.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.08327,"contact_1.force_threshold":5.90819,"push_1.push_depth":0.02069,"push_1.speed":0.0943},"optimized_scores":{"best_composite_score":0.80385,"best_fitness_score":0.70052,"best_task_score":0.76737},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":313.0,"contact_point_centroid":[0.53934,-0.05982,0.05386],"force_p95":66.66135,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":81.00617,"mean_force":30.06181,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50193,-0.0567,0.02125]},{"body_a":"world","body_b":"push_box","contact_count":893.0,"contact_point_centroid":[0.54334,-0.08969,-0.00012],"force_p95":58.24721,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":76.11065,"mean_force":18.21041,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50127,-0.05925,0.0208]},{"body_a":"attachment","body_b":"push_box","contact_count":422.0,"contact_point_centroid":[0.51703,-0.03366,0.05026],"force_p95":54.11234,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":65.90588,"mean_force":19.80561,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50302,-0.0269,0.02088]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50347,0.0757,0.18115]},{"body_a":"world","body_b":"push_box","contact_count":1868.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50839,0.10405,0.03119]}],"total_contact_groups":5},"final_pose_error":0.01997,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.54551,-0.14254,0.02497],"final_tcp_position":[0.49577,-0.15146,0.02008],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":81.00617,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.50996,0.12481,0.04379],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07956,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":467.0,"n_steps_budget":600.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.02499,"peak_contact_force":27.51458,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1868.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.51005,0.08458,0.023],"tcp_start":[0.50996,0.12481,0.04379],"tcp_to_object_dist_end":0.0373,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":627.0,"n_steps_budget":1000.0,"object_pos_end":[0.54551,-0.14254,0.02497],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.04612,"object_to_goal_dist_start":0.19823,"object_z_max":0.02987,"peak_contact_force":0.24516,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1628.0,"raw_peak_contact_force":81.00617,"subtask_id":"push","tcp_end":[0.49577,-0.15146,0.02008],"tcp_start":[0.51005,0.08458,0.023],"tcp_to_object_dist_end":0.05077,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `f2c9c63f0d9eca1b3ff8bf951759f6a3adee73f9f65e1cd3613c5e9d1203ebcc`; realized-scene SHA-256: `f3b8ea82cefd9504be10e2d47c49094a836a703404c06bdee3b01a27a59bf7be`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47924,0.05847,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.02076,-0.20847,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.47924,0.05847,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.28079,"average_solve_count":203.0,"average_success_count":203.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.09683,"contact_1.force_threshold":2.97443,"push_1.push_depth":0.02175,"push_1.speed":0.01977},"optimized_scores":{"best_composite_score":0.76993,"best_fitness_score":0.6666,"best_task_score":0.68653},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":343.0,"contact_point_centroid":[0.48749,5e-05,0.04005],"force_p95":30.17189,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":45.33727,"mean_force":5.69005,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48041,0.01047,0.02009]},{"body_a":"world","body_b":"push_box","contact_count":1317.0,"contact_point_centroid":[0.52593,-0.06915,-0.00012],"force_p95":10.65959,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":29.73012,"mean_force":1.8666,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48763,-0.06256,0.02004]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48515,0.0811,0.18049]},{"body_a":"world","body_b":"push_box","contact_count":1836.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47393,0.11438,0.03063]}],"total_contact_groups":4},"final_pose_error":0.01985,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.54573,-0.10287,0.02499],"final_tcp_position":[0.49664,-0.15327,0.01993],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":45.33727,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.47607,0.13503,0.04192],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07847,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":459.0,"n_steps_budget":600.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.02499,"peak_contact_force":27.42135,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1836.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.47482,0.09541,0.02338],"tcp_start":[0.47607,0.13503,0.04192],"tcp_to_object_dist_end":0.03723,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":674.0,"n_steps_budget":1000.0,"object_pos_end":[0.54573,-0.10287,0.02499],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.06567,"object_to_goal_dist_start":0.2095,"object_z_max":0.02618,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1660.0,"raw_peak_contact_force":45.33727,"subtask_id":"push","tcp_end":[0.49664,-0.15327,0.01993],"tcp_start":[0.47482,0.09541,0.02338],"tcp_to_object_dist_end":0.07054,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```