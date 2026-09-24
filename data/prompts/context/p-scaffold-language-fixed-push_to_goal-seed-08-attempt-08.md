## Search State

- **Seed**: 8
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | force_threshold_switch | impedance_control | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 5 | 0.4404 | 0.75 | ❌ rejected |
| 7 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | -0.0171 | 0.01 | ❌ rejected |
| 6 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | -0.1328 | 0.00 | ❌ rejected |
| 5 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | impedance_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | -0.0002 | 0.09 | ❌ rejected |
| 4 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | -0.1049 | 0.01 | ❌ rejected |

**Proposal policy**: task_score is 0.75 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `f3b8ea82cefd9504be10e2d47c49094a836a703404c06bdee3b01a27a59bf7be`
- Frozen object start: [0.4792366731926673, 0.05847322120055107, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.4792366731926673, 0.05847322120055107, 0.025)
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
  frozen_object_start: [0.4792, 0.0585, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.4792366731926673, 0.05847322120055107, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [0.0208, -0.2085, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: f3b8ea82cefd9504be10e2d47c49094a836a703404c06bdee3b01a27a59bf7be

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

## Current Skill (Q=0.440) — your mutation base

```yaml
skill: push_to_goal
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: force_threshold_switch
  termination: pose_tolerance
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.3
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: impedance_control
  termination: contact_detected
- id: push_1
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: pose_tolerance
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.02
      - 0.2
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: retract_1
  type: retract
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.2
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1

```

## Design Metrics

- **Composite score**: 0.440
- **task_score** (E): 0.747
- **fitness_score**: 0.750  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.310

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2844 |
| contact_1 | 1.00 | 1.00 | 0.0483 |
| push_1 | 1.00 | 1.00 | 0.1391 |
| retract_1 | 0.00 | 1.00 | 0.1470 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.521, 0.075, 0.032) | (0.526, -0.001, 0.025)→(0.526, -0.001, 0.025) | 0.156→0.156 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / step_budget | (0.521, 0.075, 0.032)→(0.521, 0.028, 0.020) | (0.526, -0.001, 0.025)→(0.528, -0.008, 0.025) | 0.156→0.150 | 1.00 / 3.000 | 3.389 | 12.541 |
| push_1 | push | 1.00 / step_budget | (0.521, 0.028, 0.020)→(0.503, -0.107, 0.026) | (0.528, -0.008, 0.025)→(0.519, -0.135, 0.029) | 0.150→0.042 | 1.00 / 4.333 | 77.912 | 110.623 |
| retract_1 | retract | 0.00 / step_budget | (0.503, -0.107, 0.026)→(0.498, 0.013, 0.110) | (0.519, -0.135, 0.029)→(0.515, -0.135, 0.025) | 0.042→0.039 | 1.00 / 4.000 | 0.245 | 54.521 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.940
- lateral_force_integral: None
- approach_alignment: 0.507
- goal_progress: 0.753
- terminal_score: 0.753
- phase_score: 0.832
- phase_breakdown.contact_score: 0.848
- phase_breakdown.approach_score: 0.822
- phase_breakdown.push_score: 0.826

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.800
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.778
- **Median Q (composite search score)**: 0.466
- **K-run variance**: 0.0029
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.326


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `8267fcc1127ab3c529e380fe6aea430def9956719b146bd9818eb52355cb895d`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `33d626702a3717cebb1eda35e1cb80c1c9d108c246efccd193577b9105813420`; realized-scene SHA-256: `f3b8ea82cefd9504be10e2d47c49094a836a703404c06bdee3b01a27a59bf7be`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47924,0.05847,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.02076,-0.20847,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.47924,0.05847,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.80368,"average_solve_count":163.0,"average_success_count":163.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.14467,"push_1.push_distance":0.15694,"push_1.push_speed":0.08954,"retract_1.retract_height":0.13773,"retract_1.speed":0.07143},"optimized_scores":{"best_composite_score":0.36512,"best_fitness_score":0.67512,"best_task_score":0.77821},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1531.0,"contact_point_centroid":[0.48654,-0.04592,-8e-05],"force_p95":54.94206,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":70.46059,"mean_force":12.75744,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48309,0.00018,0.01922]},{"body_a":"attachment","body_b":"push_box","contact_count":865.0,"contact_point_centroid":[0.49007,0.00149,0.03365],"force_p95":41.6451,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":48.39438,"mean_force":15.27805,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48176,0.01286,0.0193]},{"body_a":"push_box","body_b":"link7","contact_count":381.0,"contact_point_centroid":[0.50516,0.03521,0.05144],"force_p95":39.81163,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":45.1494,"mean_force":28.66069,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47745,0.05743,0.01993]},{"body_a":"attachment","body_b":"push_box","contact_count":105.0,"contact_point_centroid":[0.47907,0.0795,0.02918],"force_p95":8.07072,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.5515,"mean_force":3.47063,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47458,0.09126,0.02156]},{"body_a":"world","body_b":"push_box","contact_count":1861.0,"contact_point_centroid":[0.47956,0.05705,-1e-05],"force_p95":1.75689,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.83506,"mean_force":0.44468,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47369,0.11068,0.02457]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.4889,-0.08653,0.02111],"force_p95":4.96026,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.96026,"mean_force":4.96026,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4919,-0.07502,0.01958]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.47696,-0.10964,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.67446,"mean_force":0.24692,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48991,-0.02714,0.06291]},{"body_a":"world","body_b":"push_box","contact_count":3972.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48715,0.06586,0.16416]}],"total_contact_groups":8},"final_pose_error":0.13309,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.47696,-0.10965,0.02499],"final_tcp_position":[0.49195,0.0257,0.10312],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":70.46059,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":993.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3972.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.47614,0.13178,0.03157],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07366,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":519.0,"n_steps_budget":600.0,"object_pos_end":[0.4812,0.05027,0.02512],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.20115,"object_to_goal_dist_start":0.2095,"object_z_max":0.0252,"peak_contact_force":1.50959,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1966.0,"raw_peak_contact_force":11.5515,"tcp_end":[0.4749,0.08694,0.02102],"tcp_start":[0.47614,0.13178,0.03157],"tcp_to_object_dist_end":0.03743,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47731,-0.10905,0.02491],"object_pos_start":[0.4812,0.05027,0.02512],"object_to_goal_dist_end":0.04682,"object_to_goal_dist_start":0.20115,"object_z_max":0.02748,"peak_contact_force":3.5691,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2777.0,"raw_peak_contact_force":70.46059,"tcp_end":[0.4919,-0.07502,0.01958],"tcp_start":[0.4749,0.08694,0.02102],"tcp_to_object_dist_end":0.03741,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47696,-0.10965,0.02499],"object_pos_start":[0.47731,-0.10905,0.02491],"object_to_goal_dist_end":0.04647,"object_to_goal_dist_start":0.04682,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4001.0,"raw_peak_contact_force":4.96026,"tcp_end":[0.49195,0.0257,0.10312],"tcp_start":[0.4919,-0.07502,0.01958],"tcp_to_object_dist_end":0.157,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `021f3e69028f16fb65e79b302b37775f7324e143e034cbac30fdb04ffcd99d24`; realized-scene SHA-256: `2cf7387f3e8baf02f18930263090d6f78777bdbc147b7fa30c178332e76b547b`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.54443,-0.02558,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.04443,-0.12442,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.54443,-0.02558,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.79739,"average_solve_count":153.0,"average_success_count":153.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.22239,"push_1.push_distance":0.10434,"push_1.push_speed":0.08188,"retract_1.retract_height":0.05196,"retract_1.speed":0.08391},"optimized_scores":{"best_composite_score":0.4903,"best_fitness_score":0.8003,"best_task_score":0.75305},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":986.0,"contact_point_centroid":[0.55569,-0.07621,0.05422],"force_p95":112.11874,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":131.2904,"mean_force":77.09483,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5223,-0.06039,0.02354]},{"body_a":"attachment","body_b":"push_box","contact_count":993.0,"contact_point_centroid":[0.54113,-0.06855,0.05285],"force_p95":89.08241,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":96.37442,"mean_force":52.60729,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52242,-0.05994,0.02352]},{"body_a":"world","body_b":"push_box","contact_count":1914.0,"contact_point_centroid":[0.54972,-0.11092,-0.00034],"force_p95":76.46633,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":89.23722,"mean_force":50.56236,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.522,-0.06186,0.02371]},{"body_a":"push_box","body_b":"link7","contact_count":36.0,"contact_point_centroid":[0.55066,-0.12721,0.05609],"force_p95":75.25185,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":80.17578,"mean_force":28.94764,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50754,-0.12124,0.03014]},{"body_a":"world","body_b":"push_box","contact_count":3681.0,"contact_point_centroid":[0.53314,-0.14947,-3e-05],"force_p95":0.28828,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":76.77414,"mean_force":0.40558,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50281,-0.06038,0.07473]},{"body_a":"attachment","body_b":"push_box","contact_count":58.0,"contact_point_centroid":[0.52853,-0.12407,0.0604],"force_p95":40.21138,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":67.2082,"mean_force":14.65231,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50662,-0.11803,0.03199]},{"body_a":"attachment","body_b":"push_box","contact_count":85.0,"contact_point_centroid":[0.54513,-0.00428,0.03662],"force_p95":9.6618,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.54545,"mean_force":3.39524,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.539,0.00761,0.02053]},{"body_a":"world","body_b":"push_box","contact_count":1922.0,"contact_point_centroid":[0.54452,-0.02698,-1e-05],"force_p95":0.97284,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.79059,"mean_force":0.40074,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53668,0.02975,0.024]},{"body_a":"world","body_b":"push_box","contact_count":3616.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51809,0.02558,0.16513]}],"total_contact_groups":9},"final_pose_error":0.15861,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53261,-0.14919,0.02499],"final_tcp_position":[0.5012,-0.00334,0.1095],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":131.2904,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":904.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3616.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.53817,0.05149,0.03197],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07764,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":532.0,"n_steps_budget":600.0,"object_pos_end":[0.54653,-0.03298,0.02506],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.12593,"object_to_goal_dist_start":0.13211,"object_z_max":0.02511,"peak_contact_force":1.15254,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2007.0,"raw_peak_contact_force":10.54545,"tcp_end":[0.53949,0.00376,0.02003],"tcp_start":[0.53817,0.05149,0.03197],"tcp_to_object_dist_end":0.03775,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":996.0,"n_steps_budget":1000.0,"object_pos_end":[0.53738,-0.15017,0.03104],"object_pos_start":[0.54653,-0.03298,0.02506],"object_to_goal_dist_end":0.03787,"object_to_goal_dist_start":0.12593,"object_z_max":0.03111,"peak_contact_force":111.53272,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3893.0,"raw_peak_contact_force":131.2904,"tcp_end":[0.50852,-0.12318,0.02891],"tcp_start":[0.53949,0.00376,0.02003],"tcp_to_object_dist_end":0.03957,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53261,-0.14919,0.02499],"object_pos_start":[0.53738,-0.15017,0.03104],"object_to_goal_dist_end":0.03262,"object_to_goal_dist_start":0.03787,"object_z_max":0.034,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3775.0,"raw_peak_contact_force":80.17578,"tcp_end":[0.5012,-0.00334,0.1095],"tcp_start":[0.50852,-0.12318,0.02891],"tcp_to_object_dist_end":0.17146,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `886824c4c8b8334954c1de9b3100fb0acfdd4a04855e7e82a07b72c52723cc86`; realized-scene SHA-256: `d6f67641a3df0efca2ae6de2763dea57e4736e336d1ca3e6fe373ea0745d2d85`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.55472,-0.03508,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.05472,-0.11492,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.55472,-0.03508,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.79333,"average_solve_count":150.0,"average_success_count":150.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.10082,"push_1.push_distance":0.09411,"push_1.push_speed":0.08356,"retract_1.retract_height":0.11866,"retract_1.speed":0.09779},"optimized_scores":{"best_composite_score":0.46581,"best_fitness_score":0.77581,"best_task_score":0.71068},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":925.0,"contact_point_centroid":[0.56352,-0.07995,0.05384],"force_p95":119.1479,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":130.11693,"mean_force":79.5666,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52782,-0.06464,0.02379]},{"body_a":"world","body_b":"push_box","contact_count":1865.0,"contact_point_centroid":[0.55678,-0.11209,-0.00036],"force_p95":83.24535,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":95.24662,"mean_force":49.66249,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52806,-0.06404,0.02377]},{"body_a":"world","body_b":"push_box","contact_count":3667.0,"contact_point_centroid":[0.53704,-0.14531,-3e-05],"force_p95":0.3164,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":78.42819,"mean_force":0.36658,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50333,-0.04921,0.08113]},{"body_a":"attachment","body_b":"push_box","contact_count":930.0,"contact_point_centroid":[0.54726,-0.07285,0.05527],"force_p95":73.98907,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":75.95962,"mean_force":47.5581,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52796,-0.06429,0.02378]},{"body_a":"push_box","body_b":"link7","contact_count":36.0,"contact_point_centroid":[0.55175,-0.12469,0.05651],"force_p95":62.41729,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":71.88421,"mean_force":18.61752,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50846,-0.12005,0.03061]},{"body_a":"attachment","body_b":"push_box","contact_count":57.0,"contact_point_centroid":[0.52974,-0.12159,0.06017],"force_p95":42.87318,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":58.45467,"mean_force":9.85183,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50741,-0.11617,0.03297]},{"body_a":"attachment","body_b":"push_box","contact_count":78.0,"contact_point_centroid":[0.5553,-0.01348,0.03762],"force_p95":10.16049,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.52698,"mean_force":3.73071,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54914,-0.00161,0.02033]},{"body_a":"world","body_b":"push_box","contact_count":1978.0,"contact_point_centroid":[0.55472,-0.03622,-1e-05],"force_p95":1.02306,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.75611,"mean_force":0.39846,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54659,0.02074,0.02373]},{"body_a":"world","body_b":"push_box","contact_count":3644.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52296,0.02111,0.16506]}],"total_contact_groups":9},"final_pose_error":0.1365,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53649,-0.14507,0.02499],"final_tcp_position":[0.50119,0.01727,0.1182],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55472,-0.03508,0.025]},"peak_contact_force":130.11693,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":911.0,"n_steps_budget":1000.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.025],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3644.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.54794,0.04249,0.03178],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07816,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.55769,-0.04237,0.02486],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.12211,"object_to_goal_dist_start":0.12728,"object_z_max":0.02513,"peak_contact_force":7.50497,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2056.0,"raw_peak_contact_force":15.52698,"tcp_end":[0.5497,-0.00564,0.01983],"tcp_start":[0.54794,0.04249,0.03178],"tcp_to_object_dist_end":0.03793,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":940.0,"n_steps_budget":1000.0,"object_pos_end":[0.54092,-0.14714,0.031],"object_pos_start":[0.55769,-0.04237,0.02486],"object_to_goal_dist_end":0.04146,"object_to_goal_dist_start":0.12211,"object_z_max":0.031,"peak_contact_force":118.63421,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3720.0,"raw_peak_contact_force":130.11693,"tcp_end":[0.5096,-0.12217,0.02938],"tcp_start":[0.5497,-0.00564,0.01983],"tcp_to_object_dist_end":0.04009,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53649,-0.14507,0.02499],"object_pos_start":[0.54092,-0.14714,0.031],"object_to_goal_dist_end":0.03683,"object_to_goal_dist_start":0.04146,"object_z_max":0.03415,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3760.0,"raw_peak_contact_force":78.42819,"tcp_end":[0.50119,0.01727,0.1182],"tcp_start":[0.5096,-0.12217,0.02938],"tcp_to_object_dist_end":0.19049,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```