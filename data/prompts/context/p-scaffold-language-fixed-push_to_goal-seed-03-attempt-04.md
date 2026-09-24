## Search State

- **Seed**: 3
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4751 | 0.73 | ❌ rejected |
| 3 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4582 | 0.64 | ❌ rejected |
| 2 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4714 | 0.74 | ✅ accepted |
| 1 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4584 | 0.64 | ✅ accepted |
| 0 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4526 | 0.63 | ✅ accepted |

**Proposal policy**: task_score is 0.73 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.475) — your mutation base

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

- **Composite score**: 0.475
- **task_score** (E): 0.729
- **fitness_score**: 0.685  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.210

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2843 |
| contact_1 | 1.00 | 1.00 | 0.0449 |
| push_1 | 1.00 | 1.00 | 0.1271 |
| retract_1 | 0.00 | 1.00 | 0.1659 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.509, 0.078, 0.032) | (0.513, 0.002, 0.025)→(0.513, 0.002, 0.025) | 0.160→0.160 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / step_budget | (0.509, 0.078, 0.032)→(0.509, 0.035, 0.021) | (0.513, 0.002, 0.025)→(0.515, -0.004, 0.025) | 0.160→0.155 | 1.00 / 3.000 | 2.581 | 6.939 |
| push_1 | push | 1.00 / step_budget | (0.509, 0.035, 0.021)→(0.504, -0.087, 0.026) | (0.515, -0.004, 0.025)→(0.521, -0.117, 0.029) | 0.155→0.046 | 1.00 / 3.667 | 77.049 | 102.982 |
| retract_1 | retract | 0.00 / step_budget | (0.504, -0.087, 0.026)→(0.497, 0.062, 0.100) | (0.521, -0.117, 0.029)→(0.516, -0.114, 0.025) | 0.046→0.046 | 1.00 / 4.000 | 0.245 | 56.467 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.989
- lateral_force_integral: None
- approach_alignment: 0.420
- goal_progress: 0.909
- terminal_score: 0.909
- phase_score: 0.767
- phase_breakdown.contact_score: 0.720
- phase_breakdown.approach_score: 0.819
- phase_breakdown.push_score: 0.774

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.823
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.909
- **Median Q (composite search score)**: 0.446
- **K-run variance**: 0.0107
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.425


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.10185,"average_solve_count":216.0,"average_success_count":216.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.05273,"contact_1.speed":0.02035,"push_1.push_depth":0.09075},"optimized_scores":{"best_composite_score":0.61346,"best_fitness_score":0.82346,"best_task_score":0.90862},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":676.0,"contact_point_centroid":[0.47042,-0.06677,0.02364],"force_p95":16.02305,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.91055,"mean_force":4.67263,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46868,-0.05484,0.02022]},{"body_a":"world","body_b":"push_box","contact_count":1490.0,"contact_point_centroid":[0.468,-0.09418,-5e-05],"force_p95":7.5025,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.59488,"mean_force":2.39903,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46768,-0.05204,0.02038]},{"body_a":"push_box","body_b":"link7","contact_count":7.0,"contact_point_centroid":[0.47736,-0.0209,0.05028],"force_p95":2.49077,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.11498,"mean_force":0.88594,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4489,-0.00563,0.02073]},{"body_a":"attachment","body_b":"push_box","contact_count":2.0,"contact_point_centroid":[0.49189,-0.1271,0.02075],"force_p95":2.1975,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.2549,"mean_force":1.68092,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4934,-0.11525,0.02003]},{"body_a":"world","body_b":"push_box","contact_count":3986.0,"contact_point_centroid":[0.48858,-0.15275,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.70613,"mean_force":0.24645,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49151,-0.03869,0.05285]},{"body_a":"world","body_b":"push_box","contact_count":3700.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47374,0.02259,0.16678]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.44556,0.02572,0.02702]}],"total_contact_groups":7},"final_pose_error":0.13097,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.48859,-0.15273,0.02499],"final_tcp_position":[0.49343,0.03445,0.08868],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":37.91055,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":925.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3700.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.44891,0.04563,0.03449],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.0778,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.4458,0.0092,0.02384],"tcp_start":[0.44891,0.04563,0.03449],"tcp_to_object_dist_end":0.04105,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":808.0,"n_steps_budget":900.0,"object_pos_end":[0.48898,-0.15187,0.02496],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.01117,"object_to_goal_dist_start":0.12843,"object_z_max":0.02542,"peak_contact_force":0.0003,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2173.0,"raw_peak_contact_force":37.91055,"tcp_end":[0.4934,-0.11521,0.02004],"tcp_start":[0.4458,0.0092,0.02384],"tcp_to_object_dist_end":0.03725,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48859,-0.15273,0.02499],"object_pos_start":[0.48898,-0.15187,0.02496],"object_to_goal_dist_end":0.01174,"object_to_goal_dist_start":0.01117,"object_z_max":0.02503,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3988.0,"raw_peak_contact_force":2.2549,"tcp_end":[0.49343,0.03445,0.08868],"tcp_start":[0.4934,-0.11521,0.02004],"tcp_to_object_dist_end":0.19778,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.78289,"average_solve_count":152.0,"average_success_count":152.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.09569,"contact_1.speed":0.04996,"push_1.push_depth":0.09895},"optimized_scores":{"best_composite_score":0.44645,"best_fitness_score":0.65645,"best_task_score":0.65819},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":793.0,"contact_point_centroid":[0.56112,-0.045,0.05423],"force_p95":120.4648,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":140.03032,"mean_force":79.50276,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52709,-0.02998,0.02372]},{"body_a":"world","body_b":"push_box","contact_count":1563.0,"contact_point_centroid":[0.5552,-0.07813,-0.00034],"force_p95":90.32347,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":102.55681,"mean_force":51.60051,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52697,-0.0305,0.02382]},{"body_a":"attachment","body_b":"push_box","contact_count":796.0,"contact_point_centroid":[0.5459,-0.03835,0.05371],"force_p95":85.84166,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":92.22069,"mean_force":51.64421,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52718,-0.02973,0.02371]},{"body_a":"world","body_b":"push_box","contact_count":3678.0,"contact_point_centroid":[0.53439,-0.10684,-3e-05],"force_p95":0.30512,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":84.35207,"mean_force":0.50426,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50274,-0.00638,0.06647]},{"body_a":"push_box","body_b":"link7","contact_count":51.0,"contact_point_centroid":[0.5498,-0.09545,0.05733],"force_p95":67.60371,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":77.38564,"mean_force":28.00282,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50882,-0.08493,0.03079]},{"body_a":"attachment","body_b":"push_box","contact_count":61.0,"contact_point_centroid":[0.53338,-0.0872,0.0617],"force_p95":48.46386,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":70.21214,"mean_force":17.80699,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50833,-0.08285,0.03126]},{"body_a":"attachment","body_b":"push_box","contact_count":106.0,"contact_point_centroid":[0.55416,0.02241,0.03891],"force_p95":7.9248,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.41073,"mean_force":3.16004,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54762,0.03434,0.02023]},{"body_a":"world","body_b":"push_box","contact_count":2022.0,"contact_point_centroid":[0.55325,-0.00068,-1e-05],"force_p95":1.05334,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.92909,"mean_force":0.41862,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54525,0.05536,0.02321]},{"body_a":"world","body_b":"push_box","contact_count":3828.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52233,0.03847,0.16438]}],"total_contact_groups":9},"final_pose_error":0.10131,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.5338,-0.10682,0.02499],"final_tcp_position":[0.50008,0.06149,0.10072],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":140.03032,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":957.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3828.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.5466,0.07724,0.03105],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.0764,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":573.0,"n_steps_budget":660.0,"object_pos_end":[0.55529,-0.00677,0.02501],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.15354,"object_to_goal_dist_start":0.16043,"object_z_max":0.02513,"peak_contact_force":6.34074,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2128.0,"raw_peak_contact_force":11.41073,"tcp_end":[0.54821,0.03002,0.01973],"tcp_start":[0.5466,0.07724,0.03105],"tcp_to_object_dist_end":0.03784,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":805.0,"n_steps_budget":900.0,"object_pos_end":[0.54002,-0.11477,0.03118],"object_pos_start":[0.55529,-0.00677,0.02501],"object_to_goal_dist_end":0.05367,"object_to_goal_dist_start":0.15354,"object_z_max":0.03119,"peak_contact_force":117.09284,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3152.0,"raw_peak_contact_force":140.03032,"tcp_end":[0.51002,-0.08912,0.02972],"tcp_start":[0.54821,0.03002,0.01973],"tcp_to_object_dist_end":0.0395,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5338,-0.10682,0.02499],"object_pos_start":[0.54002,-0.11477,0.03118],"object_to_goal_dist_end":0.05484,"object_to_goal_dist_start":0.05367,"object_z_max":0.03488,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3790.0,"raw_peak_contact_force":84.35207,"tcp_end":[0.50008,0.06149,0.10072],"tcp_start":[0.51002,-0.08912,0.02972],"tcp_to_object_dist_end":0.18762,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.75,"average_solve_count":156.0,"average_success_count":156.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.09997,"contact_1.speed":0.03919,"push_1.push_depth":0.09979},"optimized_scores":{"best_composite_score":0.36525,"best_fitness_score":0.57525,"best_task_score":0.62016},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":805.0,"contact_point_centroid":[0.54982,-0.01115,0.05451],"force_p95":114.08021,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":131.00396,"mean_force":75.38881,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51815,0.00476,0.02343]},{"body_a":"attachment","body_b":"push_box","contact_count":807.0,"contact_point_centroid":[0.53681,-0.00399,0.05204],"force_p95":100.27952,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":110.79314,"mean_force":54.55744,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51819,0.00491,0.02342]},{"body_a":"world","body_b":"push_box","contact_count":1517.0,"contact_point_centroid":[0.54454,-0.04715,-0.00032],"force_p95":77.53073,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":93.58353,"mean_force":51.76161,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51775,0.00223,0.02373]},{"body_a":"push_box","body_b":"link7","contact_count":44.0,"contact_point_centroid":[0.54874,-0.06195,0.05584],"force_p95":79.53892,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":82.79443,"mean_force":38.21776,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50666,-0.05202,0.03014]},{"body_a":"world","body_b":"push_box","contact_count":3662.0,"contact_point_centroid":[0.5253,-0.08196,-3e-05],"force_p95":0.46896,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":70.65246,"mean_force":0.48885,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50088,0.02437,0.0712]},{"body_a":"attachment","body_b":"push_box","contact_count":66.0,"contact_point_centroid":[0.52733,-0.05478,0.05841],"force_p95":55.95337,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":65.2454,"mean_force":20.03374,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5058,-0.04838,0.03131]},{"body_a":"attachment","body_b":"push_box","contact_count":154.0,"contact_point_centroid":[0.53792,0.05741,0.03752],"force_p95":6.88244,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.16035,"mean_force":2.62748,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53127,0.06938,0.02041]},{"body_a":"world","body_b":"push_box","contact_count":2494.0,"contact_point_centroid":[0.53672,0.03468,-1e-05],"force_p95":1.87127,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.16625,"mean_force":0.41512,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52923,0.08946,0.02307]},{"body_a":"world","body_b":"push_box","contact_count":3964.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51453,0.05557,0.16387]}],"total_contact_groups":9},"final_pose_error":0.07252,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52458,-0.08194,0.02499],"final_tcp_position":[0.4987,0.08968,0.10977],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":131.00396,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":991.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3964.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.5309,0.1113,0.0307],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07478,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":714.0,"n_steps_budget":810.0,"object_pos_end":[0.53937,0.02764,0.0251],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.18195,"object_to_goal_dist_start":0.1905,"object_z_max":0.02511,"peak_contact_force":1.15681,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2648.0,"raw_peak_contact_force":9.16035,"tcp_end":[0.53185,0.06456,0.01987],"tcp_start":[0.5309,0.1113,0.0307],"tcp_to_object_dist_end":0.03804,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":810.0,"n_steps_budget":900.0,"object_pos_end":[0.53308,-0.0845,0.03127],"object_pos_start":[0.53937,0.02764,0.0251],"object_to_goal_dist_end":0.07365,"object_to_goal_dist_start":0.18195,"object_z_max":0.03128,"peak_contact_force":114.05494,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3129.0,"raw_peak_contact_force":131.00396,"tcp_end":[0.50759,-0.05527,0.02895],"tcp_start":[0.53185,0.06456,0.01987],"tcp_to_object_dist_end":0.03886,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52458,-0.08194,0.02499],"object_pos_start":[0.53308,-0.0845,0.03127],"object_to_goal_dist_end":0.07236,"object_to_goal_dist_start":0.07365,"object_z_max":0.0347,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3772.0,"raw_peak_contact_force":82.79443,"tcp_end":[0.4987,0.08968,0.10977],"tcp_start":[0.50759,-0.05527,0.02895],"tcp_to_object_dist_end":0.19316,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```