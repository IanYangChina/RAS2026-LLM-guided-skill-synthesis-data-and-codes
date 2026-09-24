## Search State

- **Seed**: 8
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | force_threshold_switch | impedance_control | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 5 | 0.4361 | 0.73 | ❌ rejected |
| 1 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 12 | -0.0999 | 0.20 | ❌ rejected |
| 0 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | force_threshold_switch | impedance_control | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 5 | 0.4443 | 0.76 | ✅ accepted |

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

## Current Skill (Q=0.436) — your mutation base

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

- **Composite score**: 0.436
- **task_score** (E): 0.728
- **fitness_score**: 0.746  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.310

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2844 |
| contact_1 | 1.00 | 1.00 | 0.0483 |
| push_1 | 1.00 | 1.00 | 0.1422 |
| retract_1 | 0.00 | 1.00 | 0.1430 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.521, 0.075, 0.032) | (0.526, -0.001, 0.025)→(0.526, -0.001, 0.025) | 0.156→0.156 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / step_budget | (0.521, 0.075, 0.032)→(0.521, 0.028, 0.020) | (0.526, -0.001, 0.025)→(0.528, -0.008, 0.025) | 0.156→0.150 | 1.00 / 3.000 | 3.389 | 12.541 |
| push_1 | push | 1.00 / step_budget | (0.521, 0.028, 0.020)→(0.503, -0.110, 0.026) | (0.528, -0.008, 0.025)→(0.515, -0.137, 0.029) | 0.150→0.044 | 1.00 / 4.333 | 77.936 | 113.499 |
| retract_1 | retract | 0.00 / step_budget | (0.503, -0.110, 0.026)→(0.499, 0.006, 0.108) | (0.515, -0.137, 0.029)→(0.513, -0.135, 0.025) | 0.044→0.042 | 1.00 / 4.000 | 0.245 | 54.671 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.912
- lateral_force_integral: None
- approach_alignment: 0.555
- goal_progress: 0.728
- terminal_score: 0.728
- phase_score: 0.823
- phase_breakdown.contact_score: 0.848
- phase_breakdown.approach_score: 0.822
- phase_breakdown.push_score: 0.808

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.785
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.759
- **Median Q (composite search score)**: 0.459
- **K-run variance**: 0.0019
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.357


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.8038,"average_solve_count":158.0,"average_success_count":158.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.2287,"push_1.push_distance":0.17942,"push_1.push_speed":0.09961,"retract_1.retract_height":0.19078,"retract_1.speed":0.09423},"optimized_scores":{"best_composite_score":0.37456,"best_fitness_score":0.68456,"best_task_score":0.75895},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1512.0,"contact_point_centroid":[0.48063,-0.05072,-9e-05],"force_p95":58.78198,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":75.07385,"mean_force":12.74357,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48258,-0.00604,0.01911]},{"body_a":"attachment","body_b":"push_box","contact_count":866.0,"contact_point_centroid":[0.4888,-0.00331,0.03338],"force_p95":45.6812,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":54.1486,"mean_force":15.08189,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4813,0.00795,0.01922]},{"body_a":"push_box","body_b":"link7","contact_count":362.0,"contact_point_centroid":[0.50476,0.03371,0.05164],"force_p95":43.16612,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":47.92739,"mean_force":30.33195,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47724,0.05655,0.02]},{"body_a":"attachment","body_b":"push_box","contact_count":105.0,"contact_point_centroid":[0.47907,0.0795,0.02918],"force_p95":8.07072,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.5515,"mean_force":3.47063,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47458,0.09126,0.02156]},{"body_a":"world","body_b":"push_box","contact_count":1861.0,"contact_point_centroid":[0.47956,0.05705,-1e-05],"force_p95":1.75689,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.83506,"mean_force":0.44468,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47369,0.11068,0.02457]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.48589,-0.09367,0.02165],"force_p95":7.07461,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.07461,"mean_force":7.07461,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49051,-0.08284,0.01933]},{"body_a":"world","body_b":"push_box","contact_count":3989.0,"contact_point_centroid":[0.46611,-0.1126,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.54103,"mean_force":0.24768,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48934,-0.02229,0.07084]},{"body_a":"world","body_b":"push_box","contact_count":3972.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48715,0.06586,0.16416]}],"total_contact_groups":8},"final_pose_error":0.11244,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.46608,-0.11258,0.02499],"final_tcp_position":[0.4922,0.04348,0.11483],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":75.07385,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":993.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3972.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.47614,0.13178,0.03157],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07366,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":519.0,"n_steps_budget":600.0,"object_pos_end":[0.4812,0.05027,0.02512],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.20115,"object_to_goal_dist_start":0.2095,"object_z_max":0.0252,"peak_contact_force":1.50959,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1966.0,"raw_peak_contact_force":11.5515,"tcp_end":[0.4749,0.08694,0.02102],"tcp_start":[0.47614,0.13178,0.03157],"tcp_to_object_dist_end":0.03743,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.46641,-0.11164,0.02498],"object_pos_start":[0.4812,0.05027,0.02512],"object_to_goal_dist_end":0.05099,"object_to_goal_dist_start":0.20115,"object_z_max":0.02827,"peak_contact_force":1.4147,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2740.0,"raw_peak_contact_force":75.07385,"tcp_end":[0.49051,-0.08284,0.01933],"tcp_start":[0.4749,0.08694,0.02102],"tcp_to_object_dist_end":0.03796,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.46608,-0.11258,0.02499],"object_pos_start":[0.46641,-0.11164,0.02498],"object_to_goal_dist_end":0.0505,"object_to_goal_dist_start":0.05099,"object_z_max":0.02504,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3990.0,"raw_peak_contact_force":7.07461,"tcp_end":[0.4922,0.04348,0.11483],"tcp_start":[0.49051,-0.08284,0.01933],"tcp_to_object_dist_end":0.18197,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.50595,"average_solve_count":168.0,"average_success_count":168.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.09222,"push_1.push_distance":0.10446,"push_1.push_speed":0.08057,"retract_1.retract_height":0.14401,"retract_1.speed":0.0293},"optimized_scores":{"best_composite_score":0.47493,"best_fitness_score":0.78493,"best_task_score":0.72849},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":990.0,"contact_point_centroid":[0.55581,-0.0755,0.05419],"force_p95":110.43857,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":131.49725,"mean_force":76.20741,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52254,-0.05946,0.02347]},{"body_a":"attachment","body_b":"push_box","contact_count":997.0,"contact_point_centroid":[0.54154,-0.06768,0.05326],"force_p95":87.92017,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":93.57094,"mean_force":52.07923,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52266,-0.05902,0.02345]},{"body_a":"world","body_b":"push_box","contact_count":1920.0,"contact_point_centroid":[0.54968,-0.11047,-0.00034],"force_p95":73.80939,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":88.19761,"mean_force":49.99542,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52222,-0.061,0.02364]},{"body_a":"push_box","body_b":"link7","contact_count":42.0,"contact_point_centroid":[0.55118,-0.12585,0.05602],"force_p95":74.36452,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":81.17184,"mean_force":29.92774,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50818,-0.11906,0.03009]},{"body_a":"world","body_b":"push_box","contact_count":3653.0,"contact_point_centroid":[0.53609,-0.14592,-3e-05],"force_p95":0.28336,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":77.39758,"mean_force":0.44065,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50361,-0.07009,0.06715]},{"body_a":"attachment","body_b":"push_box","contact_count":63.0,"contact_point_centroid":[0.53118,-0.12195,0.06141],"force_p95":53.07513,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":64.81791,"mean_force":15.97602,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50738,-0.11666,0.03137]},{"body_a":"attachment","body_b":"push_box","contact_count":85.0,"contact_point_centroid":[0.54513,-0.00428,0.03662],"force_p95":9.6618,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.54545,"mean_force":3.39524,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.539,0.00761,0.02053]},{"body_a":"world","body_b":"push_box","contact_count":1922.0,"contact_point_centroid":[0.54452,-0.02698,-1e-05],"force_p95":0.97284,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.79059,"mean_force":0.40074,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53668,0.02975,0.024]},{"body_a":"world","body_b":"push_box","contact_count":3616.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51809,0.02558,0.16513]}],"total_contact_groups":9},"final_pose_error":0.18219,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53562,-0.1458,0.02499],"final_tcp_position":[0.50224,-0.02458,0.09796],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":131.49725,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":904.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3616.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.53817,0.05149,0.03197],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07764,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":532.0,"n_steps_budget":600.0,"object_pos_end":[0.54653,-0.03298,0.02506],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.12593,"object_to_goal_dist_start":0.13211,"object_z_max":0.02511,"peak_contact_force":1.15254,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2007.0,"raw_peak_contact_force":10.54545,"tcp_end":[0.53949,0.00376,0.02003],"tcp_start":[0.53817,0.05149,0.03197],"tcp_to_object_dist_end":0.03775,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53766,-0.14872,0.03102],"object_pos_start":[0.54653,-0.03298,0.02506],"object_to_goal_dist_end":0.03816,"object_to_goal_dist_start":0.12593,"object_z_max":0.03106,"peak_contact_force":111.09726,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3907.0,"raw_peak_contact_force":131.49725,"tcp_end":[0.50916,-0.12107,0.02883],"tcp_start":[0.53949,0.00376,0.02003],"tcp_to_object_dist_end":0.03976,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53562,-0.1458,0.02499],"object_pos_start":[0.53766,-0.14872,0.03102],"object_to_goal_dist_end":0.03587,"object_to_goal_dist_start":0.03816,"object_z_max":0.03386,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3758.0,"raw_peak_contact_force":81.17184,"tcp_end":[0.50224,-0.02458,0.09796],"tcp_start":[0.50916,-0.12107,0.02883],"tcp_to_object_dist_end":0.14537,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.78767,"average_solve_count":146.0,"average_success_count":146.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.21575,"push_1.push_distance":0.10002,"push_1.push_speed":0.09875,"retract_1.retract_height":0.08299,"retract_1.speed":0.08959},"optimized_scores":{"best_composite_score":0.45895,"best_fitness_score":0.76895,"best_task_score":0.69658},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":822.0,"contact_point_centroid":[0.56356,-0.08075,0.05404],"force_p95":123.61893,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":133.92656,"mean_force":81.36473,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5283,-0.06622,0.02378]},{"body_a":"world","body_b":"push_box","contact_count":1633.0,"contact_point_centroid":[0.55803,-0.11279,-0.00036],"force_p95":91.72807,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":103.53984,"mean_force":52.21186,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52831,-0.06634,0.02383]},{"body_a":"attachment","body_b":"push_box","contact_count":824.0,"contact_point_centroid":[0.54708,-0.07437,0.05374],"force_p95":80.6672,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":84.47361,"mean_force":50.90919,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52837,-0.06606,0.02378]},{"body_a":"world","body_b":"push_box","contact_count":3708.0,"contact_point_centroid":[0.5388,-0.14535,-3e-05],"force_p95":0.27425,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":75.76616,"mean_force":0.38531,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.504,-0.06015,0.0768]},{"body_a":"push_box","body_b":"link7","contact_count":36.0,"contact_point_centroid":[0.55236,-0.128,0.0566],"force_p95":63.09522,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":71.93386,"mean_force":21.18685,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50907,-0.12442,0.0306]},{"body_a":"attachment","body_b":"push_box","contact_count":51.0,"contact_point_centroid":[0.53331,-0.12576,0.06201],"force_p95":40.82339,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":59.80841,"mean_force":12.49056,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50844,-0.1223,0.03176]},{"body_a":"attachment","body_b":"push_box","contact_count":78.0,"contact_point_centroid":[0.5553,-0.01348,0.03762],"force_p95":10.16049,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.52698,"mean_force":3.73071,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54914,-0.00161,0.02033]},{"body_a":"world","body_b":"push_box","contact_count":1978.0,"contact_point_centroid":[0.55472,-0.03622,-1e-05],"force_p95":1.02306,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.75611,"mean_force":0.39846,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54659,0.02074,0.02373]},{"body_a":"world","body_b":"push_box","contact_count":3644.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52296,0.02111,0.16506]}],"total_contact_groups":9},"final_pose_error":0.15421,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53833,-0.14523,0.02499],"final_tcp_position":[0.50195,0.00044,0.11247],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55472,-0.03508,0.025]},"peak_contact_force":133.92656,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":911.0,"n_steps_budget":1000.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.025],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3644.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.54794,0.04249,0.03178],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07816,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.55769,-0.04237,0.02486],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.12211,"object_to_goal_dist_start":0.12728,"object_z_max":0.02513,"peak_contact_force":7.50497,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2056.0,"raw_peak_contact_force":15.52698,"tcp_end":[0.5497,-0.00564,0.01983],"tcp_start":[0.54794,0.04249,0.03178],"tcp_to_object_dist_end":0.03793,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":835.0,"n_steps_budget":930.0,"object_pos_end":[0.54225,-0.15025,0.03105],"object_pos_start":[0.55769,-0.04237,0.02486],"object_to_goal_dist_end":0.04268,"object_to_goal_dist_start":0.12211,"object_z_max":0.03106,"peak_contact_force":121.29492,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3279.0,"raw_peak_contact_force":133.92656,"tcp_end":[0.51017,-0.12641,0.02943],"tcp_start":[0.5497,-0.00564,0.01983],"tcp_to_object_dist_end":0.04001,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53833,-0.14523,0.02499],"object_pos_start":[0.54225,-0.15025,0.03105],"object_to_goal_dist_end":0.03862,"object_to_goal_dist_start":0.04268,"object_z_max":0.034,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3795.0,"raw_peak_contact_force":75.76616,"tcp_end":[0.50195,0.00044,0.11247],"tcp_start":[0.51017,-0.12641,0.02943],"tcp_to_object_dist_end":0.17377,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```