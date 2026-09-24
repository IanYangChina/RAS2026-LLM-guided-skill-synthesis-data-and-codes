## Search State

- **Seed**: 3
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4714 | 0.74 | ✅ accepted |
| 1 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4584 | 0.64 | ✅ accepted |
| 0 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4526 | 0.63 | ✅ accepted |

**Proposal policy**: task_score is 0.74 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.471) — your mutation base

```yaml
skill: push_to_goal
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: contact_detected
  parameters:
    speed:
      type: scalar
      range:
      - 0.005
      - 0.05
- id: push_1
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  parameters:
    push_depth:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance

```

## Design Metrics

- **Composite score**: 0.471
- **task_score** (E): 0.737
- **fitness_score**: 0.681  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.210

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2761 |
| contact_1 | 1.00 | 1.00 | 0.0438 |
| push_1 | 1.00 | 1.00 | 0.1317 |
| retract_1 | 0.00 | 1.00 | 0.1657 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.508, 0.075, 0.040) | (0.513, 0.002, 0.025)→(0.513, 0.002, 0.025) | 0.160→0.160 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / step_budget | (0.508, 0.075, 0.040)→(0.509, 0.036, 0.022) | (0.513, 0.002, 0.025)→(0.515, -0.004, 0.025) | 0.160→0.154 | 1.00 / 3.333 | 2.316 | 6.794 |
| push_1 | push | 1.00 / step_budget | (0.509, 0.036, 0.022)→(0.503, -0.090, 0.025) | (0.515, -0.004, 0.025)→(0.520, -0.123, 0.029) | 0.154→0.042 | 1.00 / 3.667 | 68.864 | 87.494 |
| retract_1 | retract | 0.00 / step_budget | (0.503, -0.090, 0.025)→(0.497, 0.058, 0.098) | (0.520, -0.123, 0.029)→(0.517, -0.118, 0.025) | 0.042→0.045 | 1.00 / 4.000 | 0.245 | 54.649 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.435
- goal_progress: 0.905
- terminal_score: 0.905
- phase_score: 0.784
- phase_breakdown.contact_score: 0.650
- phase_breakdown.approach_score: 0.819
- phase_breakdown.push_score: 0.850

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.832
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.905
- **Median Q (composite search score)**: 0.445
- **K-run variance**: 0.0130
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.352


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.47514,"average_solve_count":181.0,"average_success_count":181.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.08397,"contact_1.speed":0.01671,"push_1.push_depth":0.09998},"optimized_scores":{"best_composite_score":0.62235,"best_fitness_score":0.83235,"best_task_score":0.90493},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":779.0,"contact_point_centroid":[0.47465,-0.0721,0.02938],"force_p95":16.77704,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":27.95426,"mean_force":4.50923,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46983,-0.06015,0.0206]},{"body_a":"world","body_b":"push_box","contact_count":1635.0,"contact_point_centroid":[0.46927,-0.0948,-5e-05],"force_p95":7.6415,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.70147,"mean_force":2.44275,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46694,-0.0517,0.02092]},{"body_a":"push_box","body_b":"link7","contact_count":10.0,"contact_point_centroid":[0.50267,-0.08273,0.0505],"force_p95":1.70002,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.79687,"mean_force":0.83957,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4737,-0.07057,0.02046]},{"body_a":"world","body_b":"push_box","contact_count":3988.0,"contact_point_centroid":[0.49828,-0.16209,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.82391,"mean_force":0.24628,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49162,-0.04666,0.05213]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.49371,-0.13636,0.02001],"force_p95":0.57574,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.57574,"mean_force":0.57574,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49361,-0.12438,0.02003]},{"body_a":"world","body_b":"push_box","contact_count":3464.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4738,0.02257,0.16692]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.44551,0.02818,0.02747]}],"total_contact_groups":7},"final_pose_error":0.13747,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49824,-0.16208,0.02499],"final_tcp_position":[0.49345,0.02779,0.0874],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":27.95426,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":866.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3464.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.44892,0.04563,0.03449],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07781,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.44568,0.01443,0.02479],"tcp_start":[0.44892,0.04563,0.03449],"tcp_to_object_dist_end":0.04624,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":893.0,"n_steps_budget":990.0,"object_pos_end":[0.4982,-0.16133,0.02504],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.01147,"object_to_goal_dist_start":0.12843,"object_z_max":0.02531,"peak_contact_force":0.87764,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2424.0,"raw_peak_contact_force":27.95426,"tcp_end":[0.49361,-0.12438,0.02003],"tcp_start":[0.44568,0.01443,0.02479],"tcp_to_object_dist_end":0.03756,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49824,-0.16208,0.02499],"object_pos_start":[0.4982,-0.16133,0.02504],"object_to_goal_dist_end":0.01221,"object_to_goal_dist_start":0.01147,"object_z_max":0.02504,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3989.0,"raw_peak_contact_force":0.82391,"tcp_end":[0.49345,0.02779,0.0874],"tcp_start":[0.49361,-0.12438,0.02003],"tcp_to_object_dist_end":0.19992,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.53158,"average_solve_count":190.0,"average_success_count":190.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.06429,"contact_1.speed":0.03498,"push_1.push_depth":0.0969},"optimized_scores":{"best_composite_score":0.44527,"best_fitness_score":0.65527,"best_task_score":0.66611},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":789.0,"contact_point_centroid":[0.56032,-0.04561,0.05438],"force_p95":118.5805,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":140.36034,"mean_force":78.12458,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52697,-0.03043,0.02364]},{"body_a":"world","body_b":"push_box","contact_count":1600.0,"contact_point_centroid":[0.55363,-0.07776,-0.00032],"force_p95":87.75514,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":102.56605,"mean_force":49.47672,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52726,-0.02961,0.02357]},{"body_a":"attachment","body_b":"push_box","contact_count":786.0,"contact_point_centroid":[0.54559,-0.03924,0.05349],"force_p95":84.72274,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":88.70469,"mean_force":52.27805,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52693,-0.03059,0.02367]},{"body_a":"world","body_b":"push_box","contact_count":3672.0,"contact_point_centroid":[0.53312,-0.10752,-3e-05],"force_p95":0.24987,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":84.24891,"mean_force":0.4922,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50261,-0.00567,0.0664]},{"body_a":"push_box","body_b":"link7","contact_count":54.0,"contact_point_centroid":[0.54941,-0.09457,0.05717],"force_p95":67.66399,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":74.32809,"mean_force":26.10282,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50856,-0.08371,0.03065]},{"body_a":"attachment","body_b":"push_box","contact_count":62.0,"contact_point_centroid":[0.53258,-0.08626,0.06073],"force_p95":50.58197,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":72.43338,"mean_force":17.86143,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50808,-0.08163,0.03117]},{"body_a":"attachment","body_b":"push_box","contact_count":172.0,"contact_point_centroid":[0.55474,0.02172,0.04042],"force_p95":6.41588,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.17813,"mean_force":2.49153,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54763,0.03369,0.02047]},{"body_a":"world","body_b":"push_box","contact_count":2839.0,"contact_point_centroid":[0.55332,-0.0013,-1e-05],"force_p95":1.73075,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.61788,"mean_force":0.4073,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54503,0.05435,0.02418]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5221,0.03816,0.16541]}],"total_contact_groups":9},"final_pose_error":0.10104,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.5325,-0.10742,0.02499],"final_tcp_position":[0.50001,0.06183,0.10065],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":140.36034,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.54626,0.07663,0.03316],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07602,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":821.0,"n_steps_budget":930.0,"object_pos_end":[0.55501,-0.00789,0.02509],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.15239,"object_to_goal_dist_start":0.16043,"object_z_max":0.02523,"peak_contact_force":5.11175,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3011.0,"raw_peak_contact_force":9.17813,"tcp_end":[0.54834,0.02892,0.01972],"tcp_start":[0.54626,0.07663,0.03316],"tcp_to_object_dist_end":0.03779,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":804.0,"n_steps_budget":900.0,"object_pos_end":[0.53879,-0.11459,0.03116],"object_pos_start":[0.55501,-0.00789,0.02509],"object_to_goal_dist_end":0.05288,"object_to_goal_dist_start":0.15239,"object_z_max":0.03116,"peak_contact_force":116.99059,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3175.0,"raw_peak_contact_force":140.36034,"tcp_end":[0.50983,-0.08817,0.02953],"tcp_start":[0.54834,0.02892,0.01972],"tcp_to_object_dist_end":0.03923,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5325,-0.10742,0.02499],"object_pos_start":[0.53879,-0.11459,0.03116],"object_to_goal_dist_end":0.05357,"object_to_goal_dist_start":0.05288,"object_z_max":0.03504,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3788.0,"raw_peak_contact_force":84.24891,"tcp_end":[0.50001,0.06183,0.10065],"tcp_start":[0.50983,-0.08817,0.02953],"tcp_to_object_dist_end":0.18822,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.26923,"average_solve_count":208.0,"average_success_count":208.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.02192,"contact_1.speed":0.03512,"push_1.push_depth":0.09946},"optimized_scores":{"best_composite_score":0.34646,"best_fitness_score":0.55646,"best_task_score":0.64146},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":746.0,"contact_point_centroid":[0.54322,-0.01741,0.05492],"force_p95":87.56096,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":94.16727,"mean_force":54.18133,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51557,-0.00102,0.02241]},{"body_a":"attachment","body_b":"push_box","contact_count":746.0,"contact_point_centroid":[0.53366,-0.01077,0.05156],"force_p95":80.8547,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":93.69317,"mean_force":44.04009,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51561,-0.00093,0.02243]},{"body_a":"world","body_b":"push_box","contact_count":3792.0,"contact_point_centroid":[0.51974,-0.08487,-3e-05],"force_p95":0.25046,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":78.87342,"mean_force":0.39563,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49945,0.01915,0.06742]},{"body_a":"push_box","body_b":"link7","contact_count":38.0,"contact_point_centroid":[0.54127,-0.07464,0.05522],"force_p95":73.98802,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":75.91631,"mean_force":34.63988,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50417,-0.05462,0.0275]},{"body_a":"attachment","body_b":"push_box","contact_count":53.0,"contact_point_centroid":[0.52653,-0.06068,0.05875],"force_p95":56.9285,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":72.12315,"mean_force":19.66201,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50361,-0.05249,0.02809]},{"body_a":"world","body_b":"push_box","contact_count":1491.0,"contact_point_centroid":[0.53502,-0.05303,-0.00021],"force_p95":57.90066,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":67.1485,"mean_force":36.21013,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51577,-0.00023,0.02239]},{"body_a":"attachment","body_b":"push_box","contact_count":199.0,"contact_point_centroid":[0.53783,0.0574,0.04265],"force_p95":9.28194,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.95826,"mean_force":5.61012,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53079,0.06937,0.02447]},{"body_a":"world","body_b":"push_box","contact_count":2618.0,"contact_point_centroid":[0.5369,0.03422,-1e-05],"force_p95":3.79537,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.68433,"mean_force":0.67596,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52817,0.08339,0.03389]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5132,0.05123,0.17421]}],"total_contact_groups":9},"final_pose_error":0.07721,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.5193,-0.08448,0.02499],"final_tcp_position":[0.49803,0.08581,0.10714],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":94.16727,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.52839,0.10278,0.05105],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07128,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":737.0,"n_steps_budget":870.0,"object_pos_end":[0.53873,0.02742,0.02503],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.1816,"object_to_goal_dist_start":0.1905,"object_z_max":0.0251,"peak_contact_force":1.592,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2817.0,"raw_peak_contact_force":10.95826,"tcp_end":[0.53188,0.06425,0.02115],"tcp_start":[0.52839,0.10278,0.05105],"tcp_to_object_dist_end":0.03766,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":787.0,"n_steps_budget":900.0,"object_pos_end":[0.52247,-0.09188,0.03052],"object_pos_start":[0.53873,0.02742,0.02503],"object_to_goal_dist_end":0.06256,"object_to_goal_dist_start":0.1816,"object_z_max":0.03053,"peak_contact_force":88.72305,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2983.0,"raw_peak_contact_force":94.16727,"tcp_end":[0.5051,-0.05721,0.02664],"tcp_start":[0.53188,0.06425,0.02115],"tcp_to_object_dist_end":0.03897,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5193,-0.08448,0.02499],"object_pos_start":[0.52247,-0.09188,0.03052],"object_to_goal_dist_end":0.0683,"object_to_goal_dist_start":0.06256,"object_z_max":0.03056,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3883.0,"raw_peak_contact_force":78.87342,"tcp_end":[0.49803,0.08581,0.10714],"tcp_start":[0.5051,-0.05721,0.02664],"tcp_to_object_dist_end":0.19026,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```