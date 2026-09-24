## Search State

- **Seed**: 9
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | force_threshold_switch | admittance_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 5 | 0.6844 | 0.80 | ❌ rejected |
| 9 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | force_threshold_switch | admittance_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 5 | 0.7704 | 0.72 | ❌ rejected |
| 8 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 9 | 0.3380 | 0.54 | ❌ rejected |
| 7 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 8 | 0.3790 | 0.45 | ❌ rejected |
| 6 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 7 | -0.1530 | 0.04 | ❌ rejected |

**Proposal policy**: task_score is 0.80 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `2cf7387f3e8baf02f18930263090d6f78777bdbc147b7fa30c178332e76b547b`
- Frozen object start: [0.5444299044764102, -0.025581934909493356, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.5444299044764102, -0.025581934909493356, 0.025)
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
  frozen_object_start: [0.5444, -0.0256, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.5444299044764102, -0.025581934909493356, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [-0.0444, -0.1244, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: 2cf7387f3e8baf02f18930263090d6f78777bdbc147b7fa30c178332e76b547b

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

## Current Skill (Q=0.684) — your mutation base

```yaml
skill: push_to_goal
phases:
- id: approach_1
  type: approach
  generator: arc_cartesian
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
  control: admittance_control
  termination: force_exceeded
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
  termination: time_limit
  parameters:
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

- **Composite score**: 0.684
- **task_score** (E): 0.805
- **fitness_score**: 0.772  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.222
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.310

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2785 |
| contact_1 | 0.67 | 1.00 | 0.0447 |
| push_1 | 1.00 | 1.00 | 0.1353 |
| retract_1 | 0.00 | 1.00 | 0.1363 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.513, 0.061, 0.033) | (0.518, -0.020, 0.025)→(0.518, -0.020, 0.025) | 0.139→0.139 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 0.67 / force_exceeded | (0.513, 0.061, 0.033)→(0.513, 0.018, 0.022) | (0.518, -0.020, 0.025)→(0.518, -0.020, 0.025) | 0.139→0.139 | 1.00 / 4.667 | 11.068 | 0.245 |
| push_1 | push | 1.00 / time_limit | (0.513, 0.018, 0.022)→(0.503, -0.112, 0.026) | (0.518, -0.020, 0.025)→(0.521, -0.143, 0.029) | 0.139→0.028 | 1.00 / 4.000 | 71.981 | 95.211 |
| retract_1 | retract | 0.00 / step_budget | (0.503, -0.112, 0.026)→(0.498, 0.013, 0.080) | (0.521, -0.143, 0.029)→(0.517, -0.139, 0.025) | 0.028→0.026 | 1.00 / 4.000 | 0.245 | 56.676 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.814
- lateral_force_integral: None
- approach_alignment: 0.477
- goal_progress: 0.746
- terminal_score: 0.746
- phase_score: 0.747
- phase_breakdown.approach_score: 0.821
- phase_breakdown.push_score: 0.711
- phase_breakdown.contact_score: 0.757

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.837
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.950
- **Median Q (composite search score)**: 0.757
- **K-run variance**: 0.0124
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.385


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `327b95871eb659cd41b4cf66bc0b4dfb3b240662e8501854b46ee2b8b86a04c5`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `5ffd2bb280d1d50ec9ffd23c1ed75abf73d645c1d10372a9b5bb6e9fac6e0bf8`; realized-scene SHA-256: `2cf7387f3e8baf02f18930263090d6f78777bdbc147b7fa30c178332e76b547b`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.54443,-0.02558,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.04443,-0.12442,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.54443,-0.02558,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.47977,"average_solve_count":173.0,"average_success_count":173.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.2092,"contact_1.speed":0.04999,"push_1.push_speed":0.08542,"retract_1.retract_height":0.19701,"retract_1.speed":0.01646},"optimized_scores":{"best_composite_score":0.76989,"best_fitness_score":0.74656,"best_task_score":0.74626},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":962.0,"contact_point_centroid":[0.55334,-0.06509,0.05446],"force_p95":108.54823,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":127.56729,"mean_force":69.91276,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52156,-0.04893,0.02327]},{"body_a":"attachment","body_b":"push_box","contact_count":978.0,"contact_point_centroid":[0.54002,-0.05693,0.05226],"force_p95":89.36048,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":97.33047,"mean_force":49.22349,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52183,-0.04796,0.02322]},{"body_a":"world","body_b":"push_box","contact_count":1937.0,"contact_point_centroid":[0.54638,-0.09781,-0.00029],"force_p95":73.09467,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":88.08621,"mean_force":44.56041,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52188,-0.048,0.02327]},{"body_a":"push_box","body_b":"link7","contact_count":63.0,"contact_point_centroid":[0.54839,-0.1178,0.05596],"force_p95":80.93582,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":87.47274,"mean_force":32.81755,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50698,-0.10579,0.0296]},{"body_a":"world","body_b":"push_box","contact_count":3637.0,"contact_point_centroid":[0.52896,-0.13208,-3e-05],"force_p95":0.27894,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":74.4345,"mean_force":0.59459,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50204,-0.04202,0.05549]},{"body_a":"attachment","body_b":"push_box","contact_count":79.0,"contact_point_centroid":[0.53056,-0.10857,0.06018],"force_p95":60.21482,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":72.0411,"mean_force":20.73709,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50637,-0.10322,0.03008]},{"body_a":"world","body_b":"push_box","contact_count":3720.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51729,0.04386,0.17039]},{"body_a":"world","body_b":"push_box","contact_count":2116.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53652,0.03317,0.02429]}],"total_contact_groups":8},"final_pose_error":0.15597,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52825,-0.13195,0.02499],"final_tcp_position":[0.5005,0.01058,0.0801],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":127.56729,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":930.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3720.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.53811,0.05607,0.03239],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08223,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":529.0,"n_steps_budget":720.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.02499,"peak_contact_force":20.21508,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2116.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.53855,0.01136,0.02094],"tcp_start":[0.53811,0.05607,0.03239],"tcp_to_object_dist_end":0.03762,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":992.0,"n_steps_budget":1000.0,"object_pos_end":[0.53448,-0.13942,0.03114],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.03659,"object_to_goal_dist_start":0.13211,"object_z_max":0.03115,"peak_contact_force":108.21844,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3877.0,"raw_peak_contact_force":127.56729,"tcp_end":[0.50807,-0.1104,0.02857],"tcp_start":[0.53855,0.01136,0.02094],"tcp_to_object_dist_end":0.03933,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52825,-0.13195,0.02499],"object_pos_start":[0.53448,-0.13942,0.03114],"object_to_goal_dist_end":0.03352,"object_to_goal_dist_start":0.03659,"object_z_max":0.03494,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3779.0,"raw_peak_contact_force":87.47274,"tcp_end":[0.5005,0.01058,0.0801],"tcp_start":[0.50807,-0.1104,0.02857],"tcp_to_object_dist_end":0.15531,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `e094d2c5a71c8b89ef1fa30d7ce553b9c4ed64cd3fbca90620c3ede94e719cec`; realized-scene SHA-256: `d6f67641a3df0efca2ae6de2763dea57e4736e336d1ca3e6fe373ea0745d2d85`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.55472,-0.03508,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.05472,-0.11492,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.55472,-0.03508,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.47126,"average_solve_count":174.0,"average_success_count":174.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.25049,"contact_1.speed":0.04483,"push_1.push_speed":0.08471,"retract_1.retract_height":0.08937,"retract_1.speed":0.01777},"optimized_scores":{"best_composite_score":0.7565,"best_fitness_score":0.73317,"best_task_score":0.71845},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":936.0,"contact_point_centroid":[0.56092,-0.07006,0.05384],"force_p95":110.19222,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":129.33314,"mean_force":69.84657,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52713,-0.05355,0.02322]},{"body_a":"world","body_b":"push_box","contact_count":1928.0,"contact_point_centroid":[0.55335,-0.10103,-0.0003],"force_p95":76.95663,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":90.76995,"mean_force":42.85087,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52782,-0.0518,0.02312]},{"body_a":"world","body_b":"push_box","contact_count":3646.0,"contact_point_centroid":[0.53149,-0.13172,-3e-05],"force_p95":0.30071,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":80.74036,"mean_force":0.564,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50284,-0.04243,0.05566]},{"body_a":"push_box","body_b":"link7","contact_count":59.0,"contact_point_centroid":[0.54973,-0.11697,0.05615],"force_p95":72.41635,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":78.98261,"mean_force":29.56127,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50802,-0.1063,0.02984]},{"body_a":"attachment","body_b":"push_box","contact_count":955.0,"contact_point_centroid":[0.54608,-0.06161,0.05438],"force_p95":74.16653,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":76.45534,"mean_force":42.83381,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52754,-0.05247,0.02315]},{"body_a":"attachment","body_b":"push_box","contact_count":74.0,"contact_point_centroid":[0.53196,-0.10906,0.06059],"force_p95":52.18348,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":65.09812,"mean_force":18.09601,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50745,-0.10396,0.03025]},{"body_a":"world","body_b":"push_box","contact_count":3752.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52219,0.03965,0.16907]},{"body_a":"world","body_b":"push_box","contact_count":2412.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54645,0.0239,0.02367]}],"total_contact_groups":8},"final_pose_error":0.15609,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53079,-0.13166,0.02499],"final_tcp_position":[0.50108,0.01035,0.08027],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55472,-0.03508,0.025]},"peak_contact_force":129.33314,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":938.0,"n_steps_budget":1000.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.025],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3752.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.54794,0.04702,0.03174],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08265,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":603.0,"n_steps_budget":810.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.02499,"peak_contact_force":12.74382,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2412.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.5487,0.00188,0.02061],"tcp_start":[0.54794,0.04702,0.03174],"tcp_to_object_dist_end":0.0377,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":962.0,"n_steps_budget":1000.0,"object_pos_end":[0.53685,-0.13861,0.03096],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.03902,"object_to_goal_dist_start":0.12728,"object_z_max":0.03097,"peak_contact_force":107.34186,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3819.0,"raw_peak_contact_force":129.33314,"tcp_end":[0.50916,-0.11061,0.029],"tcp_start":[0.5487,0.00188,0.02061],"tcp_to_object_dist_end":0.03943,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53079,-0.13166,0.02499],"object_pos_start":[0.53685,-0.13861,0.03096],"object_to_goal_dist_end":0.03584,"object_to_goal_dist_start":0.03902,"object_z_max":0.03474,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3779.0,"raw_peak_contact_force":80.74036,"tcp_end":[0.50108,0.01035,0.08027],"tcp_start":[0.50916,-0.11061,0.029],"tcp_to_object_dist_end":0.15526,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `0fd7d18e656259f06515eb57b82afa0c0febd9395a43c1a5f926ddaec3767c64`; realized-scene SHA-256: `5de0d8cc5a3c16249bcf1097af6edba15dfacc79d06e3eed726605dcb01257b0`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45543,-9e-05,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.04457,-0.14991,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.45543,-9e-05,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.56111,"average_solve_count":180.0,"average_success_count":180.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.06467,"contact_1.speed":0.02168,"push_1.push_speed":0.09905,"retract_1.retract_height":0.08689,"retract_1.speed":0.07247},"optimized_scores":{"best_composite_score":0.52679,"best_fitness_score":0.83679,"best_task_score":0.95011},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":871.0,"contact_point_centroid":[0.47268,-0.04781,0.02487],"force_p95":16.00309,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.73365,"mean_force":4.30654,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46988,-0.03592,0.02003]},{"body_a":"world","body_b":"push_box","contact_count":1811.0,"contact_point_centroid":[0.47093,-0.07417,-4e-05],"force_p95":7.90333,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.53931,"mean_force":2.55197,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46909,-0.0326,0.02022]},{"body_a":"push_box","body_b":"link7","contact_count":85.0,"contact_point_centroid":[0.48233,0.00389,0.05008],"force_p95":15.44613,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.90483,"mean_force":5.97082,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.45343,0.02144,0.02045]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.49222,-0.12623,0.02047],"force_p95":1.81389,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.81389,"mean_force":1.81389,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49309,-0.11429,0.02]},{"body_a":"world","body_b":"push_box","contact_count":3999.0,"contact_point_centroid":[0.49251,-0.15216,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.20939,"mean_force":0.24589,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49104,-0.04626,0.04878]},{"body_a":"world","body_b":"push_box","contact_count":3640.0,"contact_point_centroid":[0.45543,-9e-05,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47735,0.05545,0.17352]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.45543,-9e-05,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.45058,0.05837,0.02689]}],"total_contact_groups":7},"final_pose_error":0.14937,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49251,-0.15217,0.02499],"final_tcp_position":[0.49279,0.01805,0.08037],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45543,-9e-05,0.025]},"peak_contact_force":28.73365,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":910.0,"n_steps_budget":1000.0,"object_pos_end":[0.45543,-9e-05,0.02499],"object_pos_start":[0.45543,-9e-05,0.025],"object_to_goal_dist_end":0.1564,"object_to_goal_dist_start":0.1564,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3640.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.45384,0.08031,0.03462],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08098,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45543,-9e-05,0.02499],"object_pos_start":[0.45543,-9e-05,0.02499],"object_to_goal_dist_end":0.1564,"object_to_goal_dist_start":0.1564,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.45089,0.04052,0.02361],"tcp_start":[0.45384,0.08031,0.03462],"tcp_to_object_dist_end":0.04089,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49246,-0.15134,0.02497],"object_pos_start":[0.45543,-9e-05,0.02499],"object_to_goal_dist_end":0.00766,"object_to_goal_dist_start":0.1564,"object_z_max":0.02538,"peak_contact_force":0.38175,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2767.0,"raw_peak_contact_force":28.73365,"tcp_end":[0.49309,-0.11429,0.02],"tcp_start":[0.45089,0.04052,0.02361],"tcp_to_object_dist_end":0.03739,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49251,-0.15217,0.02499],"object_pos_start":[0.49246,-0.15134,0.02497],"object_to_goal_dist_end":0.0078,"object_to_goal_dist_start":0.00766,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":1.81389,"tcp_end":[0.49279,0.01805,0.08037],"tcp_start":[0.49309,-0.11429,0.02],"tcp_to_object_dist_end":0.179,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```