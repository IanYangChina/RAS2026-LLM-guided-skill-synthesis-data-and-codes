## Search State

- **Seed**: 7
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | 0.2670 | 0.68 | ❌ rejected |
| 8 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | 0.2775 | 0.69 | ❌ rejected |
| 7 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | 0.2748 | 0.69 | ❌ rejected |
| 6 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | 0.2819 | 0.69 | ❌ rejected |
| 5 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | 0.2790 | 0.71 | ✅ accepted |

**Proposal policy**: task_score is 0.68 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `c8d09cd43835becf8e5eb4413394fad8627e4bf404e9e7726e9f380b60e09752`
- Frozen object start: [0.51501145599256, 0.047665656116349056, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.51501145599256, 0.047665656116349056, 0.025)
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
  frozen_object_start: [0.515, 0.0477, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.51501145599256, 0.047665656116349056, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [-0.015, -0.1977, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: c8d09cd43835becf8e5eb4413394fad8627e4bf404e9e7726e9f380b60e09752

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

## Current Skill (Q=0.267) — your mutation base

```yaml
skill: push_to_goal
phases:
- id: approach_1
  type: approach
  generator: arc_cartesian
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
  control: admittance_control
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
  control: position_control
  termination: pose_tolerance
  parameters:
    push_depth:
      type: scalar
      range:
      - 0.01
      - 0.1
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
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1

```

## Design Metrics

- **Composite score**: 0.267
- **task_score** (E): 0.680
- **fitness_score**: 0.627  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2773 |
| contact_1 | 1.00 | 1.00 | 0.0580 |
| push_1 | 1.00 | 1.00 | 0.1255 |
| retract_1 | 0.00 | 1.00 | 0.1383 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.508, 0.104, 0.047) | (0.513, 0.027, 0.025)→(0.513, 0.027, 0.025) | 0.180→0.180 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / step_budget | (0.508, 0.104, 0.047)→(0.508, 0.054, 0.021) | (0.513, 0.027, 0.025)→(0.515, 0.018, 0.025) | 0.180→0.171 | 1.00 / 2.667 | 0.923 | 12.178 |
| push_1 | push | 1.00 / step_budget | (0.508, 0.054, 0.021)→(0.502, -0.069, 0.025) | (0.515, 0.018, 0.025)→(0.517, -0.103, 0.029) | 0.171→0.059 | 1.00 / 3.667 | 62.291 | 87.616 |
| retract_1 | retract | 0.00 / step_budget | (0.502, -0.069, 0.025)→(0.497, 0.052, 0.090) | (0.517, -0.103, 0.029)→(0.514, -0.098, 0.025) | 0.059→0.059 | 1.00 / 4.000 | 0.245 | 48.391 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.854
- lateral_force_integral: None
- approach_alignment: 0.457
- goal_progress: 0.747
- terminal_score: 0.747
- phase_score: 0.806
- phase_breakdown.push_score: 0.800
- phase_breakdown.approach_score: 0.733
- phase_breakdown.contact_score: 0.863

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.782
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.747
- **Median Q (composite search score)**: 0.200
- **K-run variance**: 0.0121
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.453


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `75e2389a1a667086aa2b9c0de482ff37adf5571150b90a83772692baadf8b52e`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `154c216c563de6b8ee153943e5b668ca6d0c7dfd9253696b060f91a67dca06ec`; realized-scene SHA-256: `c8d09cd43835becf8e5eb4413394fad8627e4bf404e9e7726e9f380b60e09752`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51501,0.04767,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.01501,-0.19767,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.51501,0.04767,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.60843,"average_solve_count":166.0,"average_success_count":166.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.09995,"contact_1.speed":0.03739,"push_1.push_depth":0.09626,"push_1.push_distance":0.14671,"push_1.push_speed":0.09728,"retract_1.speed":0.06478},"optimized_scores":{"best_composite_score":0.19994,"best_fitness_score":0.55994,"best_task_score":0.62442},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1402.0,"contact_point_centroid":[0.52465,-0.04307,-0.00018],"force_p95":57.085,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":77.0126,"mean_force":38.69861,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50522,0.01125,0.02238]},{"body_a":"push_box","body_b":"link7","contact_count":768.0,"contact_point_centroid":[0.53263,-0.00223,0.0546],"force_p95":65.48786,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":73.58232,"mean_force":53.24961,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50537,0.01495,0.02213]},{"body_a":"attachment","body_b":"push_box","contact_count":773.0,"contact_point_centroid":[0.52331,0.00533,0.05011],"force_p95":65.40088,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":71.40666,"mean_force":43.98128,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50541,0.01536,0.02212]},{"body_a":"push_box","body_b":"link7","contact_count":28.0,"contact_point_centroid":[0.53349,-0.06687,0.05496],"force_p95":57.58768,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":60.36576,"mean_force":27.59176,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50125,-0.04338,0.02519]},{"body_a":"attachment","body_b":"push_box","contact_count":50.0,"contact_point_centroid":[0.52233,-0.05015,0.05668],"force_p95":45.04192,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":51.03822,"mean_force":12.58508,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50044,-0.04076,0.02587]},{"body_a":"world","body_b":"push_box","contact_count":3819.0,"contact_point_centroid":[0.51159,-0.0771,-1e-05],"force_p95":0.24559,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":44.57877,"mean_force":0.32969,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49754,0.01417,0.05807]},{"body_a":"attachment","body_b":"push_box","contact_count":168.0,"contact_point_centroid":[0.51567,0.06811,0.03394],"force_p95":7.22538,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.0278,"mean_force":3.50283,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.51002,0.07996,0.0216]},{"body_a":"world","body_b":"push_box","contact_count":2945.0,"contact_point_centroid":[0.51507,0.0458,-1e-05],"force_p95":2.37177,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.51439,"mean_force":0.44856,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50829,0.10091,0.02647]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50358,0.07681,0.17794]}],"total_contact_groups":9},"final_pose_error":0.10452,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51141,-0.07643,0.02499],"final_tcp_position":[0.49717,0.06427,0.09027],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":77.0126,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.51015,0.12542,0.03668],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07878,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":819.0,"n_steps_budget":930.0,"object_pos_end":[0.51723,0.03826,0.02502],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.18905,"object_to_goal_dist_start":0.19823,"object_z_max":0.02508,"peak_contact_force":1.08211,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3113.0,"raw_peak_contact_force":10.0278,"tcp_end":[0.51049,0.07507,0.02053],"tcp_start":[0.51015,0.12542,0.03668],"tcp_to_object_dist_end":0.03769,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":777.0,"n_steps_budget":870.0,"object_pos_end":[0.51375,-0.0816,0.0298],"object_pos_start":[0.51723,0.03826,0.02502],"object_to_goal_dist_end":0.06994,"object_to_goal_dist_start":0.18905,"object_z_max":0.02985,"peak_contact_force":60.99849,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2943.0,"raw_peak_contact_force":77.0126,"tcp_end":[0.50201,-0.04476,0.02483],"tcp_start":[0.51049,0.07507,0.02053],"tcp_to_object_dist_end":0.03898,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51141,-0.07643,0.02499],"object_pos_start":[0.51375,-0.0816,0.0298],"object_to_goal_dist_end":0.07445,"object_to_goal_dist_start":0.06994,"object_z_max":0.0298,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3897.0,"raw_peak_contact_force":60.36576,"tcp_end":[0.49717,0.06427,0.09027],"tcp_start":[0.50201,-0.04476,0.02483],"tcp_to_object_dist_end":0.15576,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `4d55d9375783bea830660bf0a13dfc76a97a0d4f5645e7ebcc1ef7143776d0b7`; realized-scene SHA-256: `f3b8ea82cefd9504be10e2d47c49094a836a703404c06bdee3b01a27a59bf7be`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47924,0.05847,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.02076,-0.20847,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.47924,0.05847,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.25234,"average_solve_count":214.0,"average_success_count":214.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.03535,"contact_1.speed":0.04733,"push_1.push_depth":0.09973,"push_1.push_distance":0.05977,"push_1.push_speed":0.06951,"retract_1.speed":0.0821},"optimized_scores":{"best_composite_score":0.17883,"best_fitness_score":0.53883,"best_task_score":0.66963},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1125.0,"contact_point_centroid":[0.49617,-0.03022,-9e-05],"force_p95":42.71054,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":54.22409,"mean_force":13.46135,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48453,0.01779,0.02041]},{"body_a":"attachment","body_b":"push_box","contact_count":792.0,"contact_point_centroid":[0.49709,0.01049,0.04201],"force_p95":36.00018,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":42.966,"mean_force":13.80843,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.484,0.02169,0.02051]},{"body_a":"push_box","body_b":"link7","contact_count":395.0,"contact_point_centroid":[0.50824,0.02696,0.05193],"force_p95":29.48937,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.08109,"mean_force":18.40945,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47996,0.04785,0.02084]},{"body_a":"attachment","body_b":"push_box","contact_count":137.0,"contact_point_centroid":[0.47713,0.0792,0.03125],"force_p95":13.83257,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.66674,"mean_force":7.58238,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.4748,0.09104,0.02756]},{"body_a":"world","body_b":"push_box","contact_count":2509.0,"contact_point_centroid":[0.4795,0.05717,-2e-05],"force_p95":3.60074,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.11531,"mean_force":0.65876,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47418,0.1071,0.04234]},{"body_a":"world","body_b":"push_box","contact_count":3986.0,"contact_point_centroid":[0.49887,-0.08084,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.45582,"mean_force":0.24716,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49254,0.01639,0.05581]},{"body_a":"attachment","body_b":"push_box","contact_count":5.0,"contact_point_centroid":[0.50081,-0.0553,0.03204],"force_p95":0.89932,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.9037,"mean_force":0.64203,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49458,-0.04346,0.0201]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48583,0.07608,0.19234]}],"total_contact_groups":8},"final_pose_error":0.09584,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49882,-0.0808,0.02499],"final_tcp_position":[0.49424,0.07275,0.09357],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":54.22409,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.47661,0.13096,0.06731],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08398,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":673.0,"n_steps_budget":840.0,"object_pos_end":[0.48076,0.04952,0.02499],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.20045,"object_to_goal_dist_start":0.2095,"object_z_max":0.02512,"peak_contact_force":0.00064,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2646.0,"raw_peak_contact_force":17.66674,"tcp_end":[0.47509,0.08606,0.02303],"tcp_start":[0.47661,0.13096,0.06731],"tcp_to_object_dist_end":0.03703,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":846.0,"n_steps_budget":1000.0,"object_pos_end":[0.49927,-0.08003,0.02507],"object_pos_start":[0.48076,0.04952,0.02499],"object_to_goal_dist_end":0.06997,"object_to_goal_dist_start":0.20045,"object_z_max":0.03405,"peak_contact_force":1.51036,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2312.0,"raw_peak_contact_force":54.22409,"tcp_end":[0.49467,-0.04336,0.02014],"tcp_start":[0.47509,0.08606,0.02303],"tcp_to_object_dist_end":0.03728,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49882,-0.0808,0.02499],"object_pos_start":[0.49927,-0.08003,0.02507],"object_to_goal_dist_end":0.06921,"object_to_goal_dist_start":0.06997,"object_z_max":0.02507,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3991.0,"raw_peak_contact_force":1.45582,"tcp_end":[0.49424,0.07275,0.09357],"tcp_start":[0.49467,-0.04336,0.02014],"tcp_to_object_dist_end":0.16823,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `0a9238470f4497c7aa88b149b7cee960f9853513db10bf496723f5ea1d3a6043`; realized-scene SHA-256: `2cf7387f3e8baf02f18930263090d6f78777bdbc147b7fa30c178332e76b547b`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.54443,-0.02558,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.04443,-0.12442,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.54443,-0.02558,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.29237,"average_solve_count":236.0,"average_success_count":236.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.03398,"contact_1.speed":0.03478,"push_1.push_depth":0.09803,"push_1.push_distance":0.15136,"push_1.push_speed":0.07864,"retract_1.speed":0.07325},"optimized_scores":{"best_composite_score":0.42215,"best_fitness_score":0.78215,"best_task_score":0.74708},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":982.0,"contact_point_centroid":[0.55633,-0.07523,0.05406],"force_p95":111.39846,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":131.61196,"mean_force":76.92547,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52238,-0.05908,0.02362]},{"body_a":"attachment","body_b":"push_box","contact_count":986.0,"contact_point_centroid":[0.54145,-0.06748,0.05346],"force_p95":85.33825,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":91.68625,"mean_force":50.96008,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52245,-0.05883,0.0236]},{"body_a":"world","body_b":"push_box","contact_count":1918.0,"contact_point_centroid":[0.55009,-0.10933,-0.00035],"force_p95":74.04405,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":88.06003,"mean_force":49.91683,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52215,-0.06018,0.02375]},{"body_a":"push_box","body_b":"link7","contact_count":57.0,"contact_point_centroid":[0.54774,-0.12631,0.05681],"force_p95":73.10042,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":83.35079,"mean_force":31.93549,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50733,-0.11421,0.02983]},{"body_a":"world","body_b":"push_box","contact_count":3670.0,"contact_point_centroid":[0.53164,-0.13775,-3e-05],"force_p95":0.26708,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":79.89334,"mean_force":0.57838,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50212,-0.04146,0.05873]},{"body_a":"attachment","body_b":"push_box","contact_count":70.0,"contact_point_centroid":[0.53133,-0.1167,0.06083],"force_p95":54.21433,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":70.67075,"mean_force":19.95818,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50682,-0.11187,0.03026]},{"body_a":"attachment","body_b":"push_box","contact_count":170.0,"contact_point_centroid":[0.54506,-0.00499,0.03679],"force_p95":7.52247,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.84018,"mean_force":3.28636,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53907,0.0069,0.02118]},{"body_a":"world","body_b":"push_box","contact_count":3497.0,"contact_point_centroid":[0.54452,-0.0273,-1e-05],"force_p95":1.80504,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.4528,"mean_force":0.41016,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53627,0.03047,0.02698]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51674,0.04354,0.17358]}],"total_contact_groups":9},"final_pose_error":0.14503,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53104,-0.13763,0.02499],"final_tcp_position":[0.50031,0.01966,0.0864],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":131.61196,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.5372,0.05709,0.03845],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08407,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":964.0,"n_steps_budget":1000.0,"object_pos_end":[0.54771,-0.03467,0.02504],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.1248,"object_to_goal_dist_start":0.13211,"object_z_max":0.0251,"peak_contact_force":1.68529,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3667.0,"raw_peak_contact_force":8.84018,"tcp_end":[0.5397,0.0022,0.02008],"tcp_start":[0.5372,0.05709,0.03845],"tcp_to_object_dist_end":0.03806,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":992.0,"n_steps_budget":1000.0,"object_pos_end":[0.53668,-0.14617,0.03102],"object_pos_start":[0.54771,-0.03467,0.02504],"object_to_goal_dist_end":0.03737,"object_to_goal_dist_start":0.1248,"object_z_max":0.03102,"peak_contact_force":124.36492,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3886.0,"raw_peak_contact_force":131.61196,"tcp_end":[0.50842,-0.11877,0.02886],"tcp_start":[0.5397,0.0022,0.02008],"tcp_to_object_dist_end":0.03942,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53104,-0.13763,0.02499],"object_pos_start":[0.53668,-0.14617,0.03102],"object_to_goal_dist_end":0.03341,"object_to_goal_dist_start":0.03737,"object_z_max":0.03486,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3797.0,"raw_peak_contact_force":83.35079,"tcp_end":[0.50031,0.01966,0.0864],"tcp_start":[0.50842,-0.11877,0.02886],"tcp_to_object_dist_end":0.17162,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```