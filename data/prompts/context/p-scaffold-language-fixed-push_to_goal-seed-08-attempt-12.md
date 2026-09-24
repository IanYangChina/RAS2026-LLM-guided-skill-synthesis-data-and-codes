## Search State

- **Seed**: 8
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | force_threshold_switch | impedance_control | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 5 | 0.4463 | 0.76 | ✅ accepted |
| 11 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 7 | 0.3707 | 0.49 | ❌ rejected |
| 10 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.5091 | 0.65 | ❌ rejected |
| 9 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 8 | 0.0554 | 0.00 | ❌ rejected |
| 8 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | force_threshold_switch | impedance_control | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 5 | 0.4404 | 0.75 | ❌ rejected |

**Proposal policy**: task_score is 0.76 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.446) — your mutation base

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

- **Composite score**: 0.446
- **task_score** (E): 0.763
- **fitness_score**: 0.756  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.310

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2844 |
| contact_1 | 1.00 | 1.00 | 0.0483 |
| push_1 | 1.00 | 1.00 | 0.1387 |
| retract_1 | 0.00 | 1.00 | 0.1473 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.521, 0.075, 0.032) | (0.526, -0.001, 0.025)→(0.526, -0.001, 0.025) | 0.156→0.156 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / step_budget | (0.521, 0.075, 0.032)→(0.521, 0.028, 0.020) | (0.526, -0.001, 0.025)→(0.528, -0.008, 0.025) | 0.156→0.150 | 1.00 / 3.000 | 3.389 | 12.541 |
| push_1 | push | 1.00 / step_budget | (0.521, 0.028, 0.020)→(0.504, -0.106, 0.026) | (0.528, -0.008, 0.025)→(0.522, -0.136, 0.029) | 0.150→0.038 | 1.00 / 3.000 | 75.661 | 110.644 |
| retract_1 | retract | 0.00 / step_budget | (0.504, -0.106, 0.026)→(0.498, 0.014, 0.110) | (0.522, -0.136, 0.029)→(0.519, -0.136, 0.025) | 0.038→0.035 | 1.00 / 4.000 | 0.245 | 54.759 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.916
- lateral_force_integral: None
- approach_alignment: 0.447
- goal_progress: 0.745
- terminal_score: 0.745
- phase_score: 0.822
- phase_breakdown.contact_score: 0.848
- phase_breakdown.approach_score: 0.822
- phase_breakdown.push_score: 0.807

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.791
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.830
- **Median Q (composite search score)**: 0.463
- **K-run variance**: 0.0014
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.351


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.51705,"average_solve_count":176.0,"average_success_count":176.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.23951,"push_1.push_distance":0.15228,"push_1.push_speed":0.0957,"retract_1.retract_height":0.10558,"retract_1.speed":0.02534},"optimized_scores":{"best_composite_score":0.39496,"best_fitness_score":0.70496,"best_task_score":0.83006},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1513.0,"contact_point_centroid":[0.48863,-0.04856,-0.0001],"force_p95":57.22258,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":74.15341,"mean_force":12.30524,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48359,-0.00181,0.01926]},{"body_a":"attachment","body_b":"push_box","contact_count":901.0,"contact_point_centroid":[0.49,-0.00486,0.0315],"force_p95":44.05233,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":53.60506,"mean_force":13.99643,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48273,0.00658,0.01935]},{"body_a":"push_box","body_b":"link7","contact_count":343.0,"contact_point_centroid":[0.50549,0.03655,0.05141],"force_p95":42.34307,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":46.04901,"mean_force":29.76717,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47747,0.05921,0.02006]},{"body_a":"attachment","body_b":"push_box","contact_count":105.0,"contact_point_centroid":[0.47907,0.0795,0.02918],"force_p95":8.07072,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.5515,"mean_force":3.47063,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47458,0.09126,0.02156]},{"body_a":"world","body_b":"push_box","contact_count":1861.0,"contact_point_centroid":[0.47956,0.05705,-1e-05],"force_p95":1.75689,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.83506,"mean_force":0.44468,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47369,0.11068,0.02457]},{"body_a":"world","body_b":"push_box","contact_count":3985.0,"contact_point_centroid":[0.48774,-0.11658,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.40358,"mean_force":0.24642,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49041,-0.03761,0.05734]},{"body_a":"attachment","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.49138,-0.09087,0.02048],"force_p95":1.00125,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.0768,"mean_force":0.55685,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4929,-0.07905,0.01969]},{"body_a":"world","body_b":"push_box","contact_count":3972.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48715,0.06586,0.16416]}],"total_contact_groups":8},"final_pose_error":0.1544,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.4877,-0.11659,0.02499],"final_tcp_position":[0.4919,0.00665,0.09322],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":74.15341,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":993.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3972.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.47614,0.13178,0.03157],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07366,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":519.0,"n_steps_budget":600.0,"object_pos_end":[0.4812,0.05027,0.02512],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.20115,"object_to_goal_dist_start":0.2095,"object_z_max":0.0252,"peak_contact_force":1.50959,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1966.0,"raw_peak_contact_force":11.5515,"tcp_end":[0.4749,0.08694,0.02102],"tcp_start":[0.47614,0.13178,0.03157],"tcp_to_object_dist_end":0.03743,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48813,-0.11546,0.02509],"object_pos_start":[0.4812,0.05027,0.02512],"object_to_goal_dist_end":0.03653,"object_to_goal_dist_start":0.20115,"object_z_max":0.02778,"peak_contact_force":0.44486,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2757.0,"raw_peak_contact_force":74.15341,"tcp_end":[0.49292,-0.07895,0.01971],"tcp_start":[0.4749,0.08694,0.02102],"tcp_to_object_dist_end":0.03721,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4877,-0.11659,0.02499],"object_pos_start":[0.48813,-0.11546,0.02509],"object_to_goal_dist_end":0.0356,"object_to_goal_dist_start":0.03653,"object_z_max":0.02509,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3988.0,"raw_peak_contact_force":1.40358,"tcp_end":[0.4919,0.00665,0.09322],"tcp_start":[0.49292,-0.07895,0.01971],"tcp_to_object_dist_end":0.14092,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.79085,"average_solve_count":153.0,"average_success_count":153.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.16893,"push_1.push_distance":0.1034,"push_1.push_speed":0.07905,"retract_1.retract_height":0.09831,"retract_1.speed":0.09995},"optimized_scores":{"best_composite_score":0.48148,"best_fitness_score":0.79148,"best_task_score":0.7451},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":990.0,"contact_point_centroid":[0.55554,-0.0754,0.0542],"force_p95":110.37357,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":128.23714,"mean_force":75.84133,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5224,-0.05928,0.02344]},{"body_a":"attachment","body_b":"push_box","contact_count":997.0,"contact_point_centroid":[0.54131,-0.06755,0.0531],"force_p95":87.91135,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":94.53869,"mean_force":51.86493,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52252,-0.05884,0.02341]},{"body_a":"world","body_b":"push_box","contact_count":1920.0,"contact_point_centroid":[0.54937,-0.11038,-0.00034],"force_p95":74.1362,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":87.23581,"mean_force":49.75496,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52208,-0.06079,0.02361]},{"body_a":"push_box","body_b":"link7","contact_count":37.0,"contact_point_centroid":[0.55095,-0.12577,0.05599],"force_p95":75.21045,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":83.08056,"mean_force":25.65606,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50789,-0.11846,0.03013]},{"body_a":"world","body_b":"push_box","contact_count":3683.0,"contact_point_centroid":[0.53388,-0.14626,-3e-05],"force_p95":0.31237,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":71.14517,"mean_force":0.37499,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50284,-0.04716,0.08109]},{"body_a":"attachment","body_b":"push_box","contact_count":56.0,"contact_point_centroid":[0.53005,-0.12114,0.06075],"force_p95":52.53498,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":67.35634,"mean_force":14.06287,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50706,-0.11553,0.03187]},{"body_a":"attachment","body_b":"push_box","contact_count":85.0,"contact_point_centroid":[0.54513,-0.00428,0.03662],"force_p95":9.6618,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.54545,"mean_force":3.39524,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.539,0.00761,0.02053]},{"body_a":"world","body_b":"push_box","contact_count":1922.0,"contact_point_centroid":[0.54452,-0.02698,-1e-05],"force_p95":0.97284,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.79059,"mean_force":0.40074,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53668,0.02975,0.024]},{"body_a":"world","body_b":"push_box","contact_count":3616.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51809,0.02558,0.16513]}],"total_contact_groups":9},"final_pose_error":0.13336,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53345,-0.1461,0.02499],"final_tcp_position":[0.50081,0.02036,0.11873],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":128.23714,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":904.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3616.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.53817,0.05149,0.03197],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07764,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":532.0,"n_steps_budget":600.0,"object_pos_end":[0.54653,-0.03298,0.02506],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.12593,"object_to_goal_dist_start":0.13211,"object_z_max":0.02511,"peak_contact_force":1.15254,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2007.0,"raw_peak_contact_force":10.54545,"tcp_end":[0.53949,0.00376,0.02003],"tcp_start":[0.53817,0.05149,0.03197],"tcp_to_object_dist_end":0.03775,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53699,-0.14837,0.03114],"object_pos_start":[0.54653,-0.03298,0.02506],"object_to_goal_dist_end":0.03753,"object_to_goal_dist_start":0.12593,"object_z_max":0.03115,"peak_contact_force":109.35713,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3907.0,"raw_peak_contact_force":128.23714,"tcp_end":[0.50895,-0.12051,0.02878],"tcp_start":[0.53949,0.00376,0.02003],"tcp_to_object_dist_end":0.03959,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53345,-0.1461,0.02499],"object_pos_start":[0.53699,-0.14837,0.03114],"object_to_goal_dist_end":0.03368,"object_to_goal_dist_start":0.03753,"object_z_max":0.03383,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3776.0,"raw_peak_contact_force":83.08056,"tcp_end":[0.50081,0.02036,0.11873],"tcp_start":[0.50895,-0.12051,0.02878],"tcp_to_object_dist_end":0.19381,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.79333,"average_solve_count":150.0,"average_success_count":150.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.1634,"push_1.push_distance":0.0911,"push_1.push_speed":0.08111,"retract_1.retract_height":0.10435,"retract_1.speed":0.09591},"optimized_scores":{"best_composite_score":0.46251,"best_fitness_score":0.77251,"best_task_score":0.71389},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":919.0,"contact_point_centroid":[0.56327,-0.07961,0.05369],"force_p95":117.30491,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":129.5418,"mean_force":77.52459,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52756,-0.06359,0.02369]},{"body_a":"world","body_b":"push_box","contact_count":1861.0,"contact_point_centroid":[0.55654,-0.11107,-0.00035],"force_p95":80.84959,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":92.96168,"mean_force":48.22112,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52785,-0.06283,0.02364]},{"body_a":"world","body_b":"push_box","contact_count":3688.0,"contact_point_centroid":[0.53655,-0.14499,-3e-05],"force_p95":0.28069,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":79.79283,"mean_force":0.35842,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50331,-0.04857,0.08009]},{"body_a":"attachment","body_b":"push_box","contact_count":921.0,"contact_point_centroid":[0.54703,-0.07206,0.05529],"force_p95":72.14043,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":73.99877,"mean_force":46.50194,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52765,-0.06341,0.02369]},{"body_a":"push_box","body_b":"link7","contact_count":34.0,"contact_point_centroid":[0.55172,-0.12206,0.05643],"force_p95":65.48439,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":70.26678,"mean_force":18.64706,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50844,-0.11736,0.03056]},{"body_a":"attachment","body_b":"push_box","contact_count":48.0,"contact_point_centroid":[0.53018,-0.11997,0.06052],"force_p95":40.40303,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":59.52025,"mean_force":11.1961,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50756,-0.11433,0.03236]},{"body_a":"attachment","body_b":"push_box","contact_count":78.0,"contact_point_centroid":[0.5553,-0.01348,0.03762],"force_p95":10.16049,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.52698,"mean_force":3.73071,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54914,-0.00161,0.02033]},{"body_a":"world","body_b":"push_box","contact_count":1978.0,"contact_point_centroid":[0.55472,-0.03622,-1e-05],"force_p95":1.02306,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.75611,"mean_force":0.39846,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54659,0.02074,0.02373]},{"body_a":"world","body_b":"push_box","contact_count":3644.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52296,0.02111,0.16506]}],"total_contact_groups":9},"final_pose_error":0.13766,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53605,-0.14487,0.02499],"final_tcp_position":[0.50122,0.01635,0.11703],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55472,-0.03508,0.025]},"peak_contact_force":129.5418,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":911.0,"n_steps_budget":1000.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.025],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3644.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.54794,0.04249,0.03178],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07816,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.55769,-0.04237,0.02486],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.12211,"object_to_goal_dist_start":0.12728,"object_z_max":0.02513,"peak_contact_force":7.50497,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2056.0,"raw_peak_contact_force":15.52698,"tcp_end":[0.5497,-0.00564,0.01983],"tcp_start":[0.54794,0.04249,0.03178],"tcp_to_object_dist_end":0.03793,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":934.0,"n_steps_budget":1000.0,"object_pos_end":[0.53991,-0.14521,0.03099],"object_pos_start":[0.55769,-0.04237,0.02486],"object_to_goal_dist_end":0.04064,"object_to_goal_dist_start":0.12211,"object_z_max":0.03099,"peak_contact_force":117.18177,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3701.0,"raw_peak_contact_force":129.5418,"tcp_end":[0.50952,-0.11934,0.02932],"tcp_start":[0.5497,-0.00564,0.01983],"tcp_to_object_dist_end":0.03995,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53605,-0.14487,0.02499],"object_pos_start":[0.53991,-0.14521,0.03099],"object_to_goal_dist_end":0.03642,"object_to_goal_dist_start":0.04064,"object_z_max":0.03389,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3770.0,"raw_peak_contact_force":79.79283,"tcp_end":[0.50122,0.01635,0.11703],"tcp_start":[0.50952,-0.11934,0.02932],"tcp_to_object_dist_end":0.18888,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```