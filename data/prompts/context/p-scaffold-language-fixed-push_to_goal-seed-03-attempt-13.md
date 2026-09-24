## Search State

- **Seed**: 3
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4502 | 0.65 | ❌ rejected |
| 12 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4501 | 0.63 | ❌ rejected |
| 11 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4593 | 0.65 | ❌ rejected |
| 10 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4794 | 0.72 | ❌ rejected |
| 9 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | -0.2082 | 0.02 | ❌ rejected |

**Proposal policy**: task_score is 0.65 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.450) — your mutation base

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

- **Composite score**: 0.450
- **task_score** (E): 0.647
- **fitness_score**: 0.660  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.210

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2806 |
| contact_1 | 1.00 | 1.00 | 0.0495 |
| push_1 | 1.00 | 1.00 | 0.1240 |
| retract_1 | 0.00 | 1.00 | 0.1665 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.508, 0.077, 0.036) | (0.513, 0.002, 0.025)→(0.513, 0.002, 0.025) | 0.160→0.160 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / step_budget | (0.508, 0.077, 0.036)→(0.509, 0.030, 0.021) | (0.513, 0.002, 0.025)→(0.516, -0.007, 0.025) | 0.160→0.152 | 1.00 / 2.333 | 1.293 | 11.281 |
| push_1 | push | 1.00 / step_budget | (0.509, 0.030, 0.021)→(0.504, -0.088, 0.026) | (0.516, -0.007, 0.025)→(0.508, -0.113, 0.029) | 0.152→0.058 | 1.00 / 4.000 | 77.845 | 107.064 |
| retract_1 | retract | 0.00 / step_budget | (0.504, -0.088, 0.026)→(0.497, 0.061, 0.100) | (0.508, -0.113, 0.029)→(0.503, -0.111, 0.025) | 0.058→0.057 | 1.00 / 4.000 | 0.245 | 60.903 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.855
- lateral_force_integral: None
- approach_alignment: 0.432
- goal_progress: 0.635
- terminal_score: 0.635
- phase_score: 0.848
- phase_breakdown.contact_score: 0.885
- phase_breakdown.approach_score: 0.819
- phase_breakdown.push_score: 0.838

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.763
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.681
- **Median Q (composite search score)**: 0.430
- **K-run variance**: 0.0059
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.512


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.5419,"average_solve_count":179.0,"average_success_count":179.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.06797,"contact_1.speed":0.04063,"push_1.push_depth":0.08919},"optimized_scores":{"best_composite_score":0.55293,"best_fitness_score":0.76293,"best_task_score":0.63518},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1390.0,"contact_point_centroid":[0.46006,-0.11178,-0.0001],"force_p95":43.36413,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":58.47857,"mean_force":7.9295,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47349,-0.07407,0.01953]},{"body_a":"attachment","body_b":"push_box","contact_count":556.0,"contact_point_centroid":[0.4741,-0.06477,0.03529],"force_p95":31.97484,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":41.5111,"mean_force":13.61936,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46547,-0.05318,0.01973]},{"body_a":"push_box","body_b":"link7","contact_count":249.0,"contact_point_centroid":[0.48133,-0.04618,0.05062],"force_p95":28.40343,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.1795,"mean_force":20.2624,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.45366,-0.0215,0.02029]},{"body_a":"attachment","body_b":"push_box","contact_count":126.0,"contact_point_centroid":[0.4548,-0.01072,0.03569],"force_p95":8.48611,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.93472,"mean_force":4.30652,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.4461,0.00117,0.0224]},{"body_a":"world","body_b":"push_box","contact_count":2710.0,"contact_point_centroid":[0.45046,-0.03288,-1e-05],"force_p95":2.30544,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.54246,"mean_force":0.47448,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.44576,0.02173,0.02638]},{"body_a":"push_box","body_b":"link7","contact_count":22.0,"contact_point_centroid":[0.4768,-0.02214,0.04996],"force_p95":7.47282,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.59231,"mean_force":3.89034,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.44627,-0.00255,0.02175]},{"body_a":"world","body_b":"push_box","contact_count":3981.0,"contact_point_centroid":[0.45378,-0.14142,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.50298,"mean_force":0.24665,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4914,-0.04492,0.05216]},{"body_a":"world","body_b":"push_box","contact_count":3584.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47376,0.02259,0.1668]}],"total_contact_groups":8},"final_pose_error":0.13651,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.45394,-0.14139,0.02499],"final_tcp_position":[0.49331,0.02887,0.08742],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":58.47857,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":896.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3584.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.44892,0.04563,0.0345],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07781,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":737.0,"n_steps_budget":840.0,"object_pos_end":[0.45185,-0.04007,0.02501],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12002,"object_to_goal_dist_start":0.12843,"object_z_max":0.02517,"peak_contact_force":0.00056,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2858.0,"raw_peak_contact_force":13.93472,"tcp_end":[0.44634,-0.00329,0.02165],"tcp_start":[0.44892,0.04563,0.0345],"tcp_to_object_dist_end":0.03734,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":783.0,"n_steps_budget":870.0,"object_pos_end":[0.454,-0.14126,0.02495],"object_pos_start":[0.45185,-0.04007,0.02501],"object_to_goal_dist_end":0.04682,"object_to_goal_dist_start":0.12002,"object_z_max":0.03138,"peak_contact_force":4.64546,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2195.0,"raw_peak_contact_force":58.47857,"tcp_end":[0.4933,-0.12232,0.01988],"tcp_start":[0.44634,-0.00329,0.02165],"tcp_to_object_dist_end":0.04391,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45394,-0.14139,0.02499],"object_pos_start":[0.454,-0.14126,0.02495],"object_to_goal_dist_end":0.04685,"object_to_goal_dist_start":0.04682,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3981.0,"raw_peak_contact_force":0.50298,"tcp_end":[0.49331,0.02887,0.08742],"tcp_start":[0.4933,-0.12232,0.01988],"tcp_to_object_dist_end":0.18556,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.27363,"average_solve_count":201.0,"average_success_count":201.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.05286,"contact_1.speed":0.03969,"push_1.push_depth":0.09438},"optimized_scores":{"best_composite_score":0.43013,"best_fitness_score":0.64013,"best_task_score":0.68109},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":752.0,"contact_point_centroid":[0.55921,-0.04528,0.05443],"force_p95":115.78828,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":134.66128,"mean_force":73.90435,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52632,-0.02965,0.02355]},{"body_a":"world","body_b":"push_box","contact_count":1487.0,"contact_point_centroid":[0.55255,-0.07927,-0.00031],"force_p95":86.30995,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":101.32885,"mean_force":47.99258,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52626,-0.02997,0.02363]},{"body_a":"push_box","body_b":"link7","contact_count":44.0,"contact_point_centroid":[0.55207,-0.08973,0.05559],"force_p95":69.81019,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":89.98594,"mean_force":33.00569,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50859,-0.08178,0.03022]},{"body_a":"attachment","body_b":"push_box","contact_count":747.0,"contact_point_centroid":[0.54499,-0.03882,0.05381],"force_p95":83.1576,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":87.36714,"mean_force":49.39911,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52623,-0.02996,0.0236]},{"body_a":"world","body_b":"push_box","contact_count":3679.0,"contact_point_centroid":[0.53013,-0.10832,-3e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":79.74896,"mean_force":0.48262,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50241,-0.00245,0.0669]},{"body_a":"attachment","body_b":"push_box","contact_count":67.0,"contact_point_centroid":[0.53066,-0.08369,0.0591],"force_p95":51.70917,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":56.52854,"mean_force":16.64025,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50771,-0.07799,0.03114]},{"body_a":"attachment","body_b":"push_box","contact_count":148.0,"contact_point_centroid":[0.55465,0.02207,0.04276],"force_p95":8.57778,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.29016,"mean_force":4.28508,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54737,0.03404,0.02197]},{"body_a":"world","body_b":"push_box","contact_count":2515.0,"contact_point_centroid":[0.55319,-0.00085,-1e-05],"force_p95":2.96575,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.41415,"mean_force":0.50474,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54429,0.05276,0.02883]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52133,0.03695,0.16955]}],"total_contact_groups":9},"final_pose_error":0.09717,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52943,-0.10815,0.02499],"final_tcp_position":[0.49983,0.06556,0.10192],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":134.66128,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.54471,0.07422,0.0414],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07517,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":708.0,"n_steps_budget":810.0,"object_pos_end":[0.55527,-0.00747,0.02509],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.15287,"object_to_goal_dist_start":0.16043,"object_z_max":0.0251,"peak_contact_force":1.78226,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2663.0,"raw_peak_contact_force":11.29016,"tcp_end":[0.54828,0.02936,0.02037],"tcp_start":[0.54471,0.07422,0.0414],"tcp_to_object_dist_end":0.03779,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":771.0,"n_steps_budget":870.0,"object_pos_end":[0.53719,-0.11295,0.03111],"object_pos_start":[0.55527,-0.00747,0.02509],"object_to_goal_dist_end":0.05285,"object_to_goal_dist_start":0.15287,"object_z_max":0.03111,"peak_contact_force":114.22407,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2986.0,"raw_peak_contact_force":134.66128,"tcp_end":[0.5096,-0.08516,0.0293],"tcp_start":[0.54828,0.02936,0.02037],"tcp_to_object_dist_end":0.0392,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52943,-0.10815,0.02499],"object_pos_start":[0.53719,-0.11295,0.03111],"object_to_goal_dist_end":0.05116,"object_to_goal_dist_start":0.05285,"object_z_max":0.03473,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3790.0,"raw_peak_contact_force":89.98594,"tcp_end":[0.49983,0.06556,0.10192],"tcp_start":[0.5096,-0.08516,0.0293],"tcp_to_object_dist_end":0.19228,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.74522,"average_solve_count":157.0,"average_success_count":157.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.09901,"contact_1.speed":0.03772,"push_1.push_depth":0.09997},"optimized_scores":{"best_composite_score":0.36748,"best_fitness_score":0.57748,"best_task_score":0.62404},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":807.0,"contact_point_centroid":[0.54967,-0.01083,0.05462],"force_p95":114.61622,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":128.05156,"mean_force":75.4973,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51822,0.00475,0.02345]},{"body_a":"attachment","body_b":"push_box","contact_count":803.0,"contact_point_centroid":[0.53658,-0.00439,0.05168],"force_p95":101.00788,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":109.65351,"mean_force":56.24036,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51816,0.00447,0.02347]},{"body_a":"world","body_b":"push_box","contact_count":1549.0,"contact_point_centroid":[0.54424,-0.04564,-0.00031],"force_p95":77.91496,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":95.38512,"mean_force":51.09922,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51797,0.00312,0.02366]},{"body_a":"push_box","body_b":"link7","contact_count":44.0,"contact_point_centroid":[0.54918,-0.06241,0.05582],"force_p95":83.51262,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":92.2212,"mean_force":39.73275,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50683,-0.05255,0.03022]},{"body_a":"attachment","body_b":"push_box","contact_count":63.0,"contact_point_centroid":[0.52875,-0.05544,0.05998],"force_p95":62.56948,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":82.16327,"mean_force":22.4915,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50606,-0.04935,0.03122]},{"body_a":"world","body_b":"push_box","contact_count":3688.0,"contact_point_centroid":[0.52532,-0.08282,-3e-05],"force_p95":0.24645,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":81.90454,"mean_force":0.49288,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50096,0.02359,0.07092]},{"body_a":"attachment","body_b":"push_box","contact_count":161.0,"contact_point_centroid":[0.53835,0.05735,0.03858],"force_p95":6.82028,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.61911,"mean_force":2.36352,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53127,0.0693,0.02039]},{"body_a":"world","body_b":"push_box","contact_count":2556.0,"contact_point_centroid":[0.53688,0.03446,-1e-05],"force_p95":1.62885,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.33559,"mean_force":0.40329,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52922,0.08948,0.02307]},{"body_a":"world","body_b":"push_box","contact_count":3964.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51453,0.05557,0.16387]}],"total_contact_groups":9},"final_pose_error":0.0728,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52476,-0.08279,0.02499],"final_tcp_position":[0.49873,0.08939,0.10969],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":128.05156,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":991.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3964.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.5309,0.1113,0.0307],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07478,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":739.0,"n_steps_budget":840.0,"object_pos_end":[0.53944,0.02754,0.02507],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.18186,"object_to_goal_dist_start":0.1905,"object_z_max":0.02514,"peak_contact_force":2.0968,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2717.0,"raw_peak_contact_force":8.61911,"tcp_end":[0.53185,0.06442,0.01984],"tcp_start":[0.5309,0.1113,0.0307],"tcp_to_object_dist_end":0.03802,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":810.0,"n_steps_budget":900.0,"object_pos_end":[0.53324,-0.08483,0.03136],"object_pos_start":[0.53944,0.02754,0.02507],"object_to_goal_dist_end":0.07343,"object_to_goal_dist_start":0.18186,"object_z_max":0.03137,"peak_contact_force":114.66448,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3159.0,"raw_peak_contact_force":128.05156,"tcp_end":[0.50768,-0.05569,0.029],"tcp_start":[0.53185,0.06442,0.01984],"tcp_to_object_dist_end":0.03883,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52476,-0.08279,0.02499],"object_pos_start":[0.53324,-0.08483,0.03136],"object_to_goal_dist_end":0.07162,"object_to_goal_dist_start":0.07343,"object_z_max":0.03481,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3795.0,"raw_peak_contact_force":92.2212,"tcp_end":[0.49873,0.08939,0.10969],"tcp_start":[0.50768,-0.05569,0.029],"tcp_to_object_dist_end":0.19365,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```