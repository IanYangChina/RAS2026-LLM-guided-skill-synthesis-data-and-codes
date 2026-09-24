## Search State

- **Seed**: 2
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | approach → contact → push → retract | linear_cartesian | impedance_motion | linear_cartesian | arc_cartesian | position_control | admittance_control | position_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.5811 | 0.74 | ❌ rejected |
| 0 | approach → contact → push → retract | linear_cartesian | impedance_motion | linear_cartesian | arc_cartesian | position_control | admittance_control | position_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.5898 | 0.76 | ✅ accepted |

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
- Frozen realised-scene SHA-256: `8c36a5f9300ba3a57ccc09620ec8ba0a5276276ed83fb4303679e150911bfa14`
- Frozen object start: [0.47139345610991795, -0.0241810627903052, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.47139345610991795, -0.0241810627903052, 0.025)
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
  frozen_object_start: [0.4714, -0.0242, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.47139345610991795, -0.0241810627903052, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [0.0286, -0.1258, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: 8c36a5f9300ba3a57ccc09620ec8ba0a5276276ed83fb4303679e150911bfa14

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

## Current Skill (Q=0.581) — your mutation base

```yaml
skill: push_to_goal
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.3
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: contact_1
  type: contact
  generator: impedance_motion
  control: admittance_control
  termination: contact_detected
- id: push_1
  type: push
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.02
      - 0.2
- id: retract_1
  type: retract
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance

```

## Design Metrics

- **Composite score**: 0.581
- **task_score** (E): 0.735
- **fitness_score**: 0.791  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.210

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2776 |
| contact_1 | 1.00 | 1.00 | 0.0490 |
| push_1 | 1.00 | 1.00 | 0.1409 |
| retract_1 | 0.00 | 1.00 | 0.1675 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.488, 0.059, 0.033) | (0.492, -0.018, 0.025)→(0.492, -0.018, 0.025) | 0.139→0.139 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / step_budget | (0.488, 0.059, 0.033)→(0.487, 0.011, 0.021) | (0.492, -0.018, 0.025)→(0.493, -0.026, 0.025) | 0.139→0.132 | 1.00 / 3.667 | 9.345 | 12.503 |
| push_1 | push | 1.00 / step_budget | (0.487, 0.011, 0.021)→(0.499, -0.124, 0.023) | (0.493, -0.026, 0.025)→(0.497, -0.147, 0.027) | 0.132→0.040 | 1.00 / 3.000 | 43.997 | 82.681 |
| retract_1 | retract | 0.00 / step_budget | (0.499, -0.124, 0.023)→(0.496, 0.015, 0.115) | (0.497, -0.147, 0.027)→(0.492, -0.145, 0.025) | 0.040→0.037 | 1.00 / 4.000 | 0.245 | 25.909 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.479
- goal_progress: 0.821
- terminal_score: 0.821
- phase_score: 0.835
- phase_breakdown.approach_score: 0.820
- phase_breakdown.push_score: 0.821
- phase_breakdown.contact_score: 0.869

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.830
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.821
- **Median Q (composite search score)**: 0.583
- **K-run variance**: 0.0010
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.183


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `27920116be2b9a598fe307ae470bb0295293d051bb1ef513a0996a4d851f2459`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `1a1e2536715050e6c37d8aed13e4ecd62004f6234f1413b07d7b475a233f55c9`; realized-scene SHA-256: `8c36a5f9300ba3a57ccc09620ec8ba0a5276276ed83fb4303679e150911bfa14`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47139,-0.02418,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.02861,-0.12582,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.47139,-0.02418,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.27885,"average_solve_count":208.0,"average_success_count":208.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.1834,"approach_1.speed":0.0229,"push_1.push_distance":0.10715},"optimized_scores":{"best_composite_score":0.61967,"best_fitness_score":0.82967,"best_task_score":0.8214},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1255.0,"contact_point_centroid":[0.48547,-0.11362,-9e-05],"force_p95":51.36838,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":65.98173,"mean_force":11.76355,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48102,-0.06838,0.01947]},{"body_a":"attachment","body_b":"push_box","contact_count":741.0,"contact_point_centroid":[0.48709,-0.07235,0.03256],"force_p95":37.41423,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":47.33246,"mean_force":13.73974,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47959,-0.06063,0.01954]},{"body_a":"push_box","body_b":"link7","contact_count":282.0,"contact_point_centroid":[0.49927,-0.0413,0.051],"force_p95":34.81287,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":38.15957,"mean_force":26.08557,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47156,-0.01754,0.02016]},{"body_a":"attachment","body_b":"push_box","contact_count":83.0,"contact_point_centroid":[0.47345,-0.0028,0.03317],"force_p95":9.615,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.76681,"mean_force":3.7949,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.46689,0.00908,0.0221]},{"body_a":"world","body_b":"push_box","contact_count":1912.0,"contact_point_centroid":[0.4715,-0.02529,-1e-05],"force_p95":1.67451,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.87557,"mean_force":0.41381,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.46618,0.03036,0.02619]},{"body_a":"world","body_b":"push_box","contact_count":3997.0,"contact_point_centroid":[0.48539,-0.16783,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.8465,"mean_force":0.24597,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49212,-0.06444,0.06954]},{"body_a":"world","body_b":"push_box","contact_count":3736.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48364,0.02604,0.16666]}],"total_contact_groups":7},"final_pose_error":0.1481,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.48541,-0.16784,0.02499],"final_tcp_position":[0.49368,0.00682,0.11268],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":65.98173,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":934.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3736.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.46887,0.05264,0.03404],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07739,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":523.0,"n_steps_budget":600.0,"object_pos_end":[0.4727,-0.03173,0.02494],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12138,"object_to_goal_dist_start":0.12903,"object_z_max":0.02511,"peak_contact_force":16.0,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1995.0,"raw_peak_contact_force":11.76681,"tcp_end":[0.46711,0.0051,0.02142],"tcp_start":[0.46887,0.05264,0.03404],"tcp_to_object_dist_end":0.03742,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":843.0,"n_steps_budget":930.0,"object_pos_end":[0.48553,-0.16724,0.02502],"object_pos_start":[0.4727,-0.03173,0.02494],"object_to_goal_dist_end":0.0225,"object_to_goal_dist_start":0.12138,"object_z_max":0.0307,"peak_contact_force":0.93015,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2278.0,"raw_peak_contact_force":65.98173,"tcp_end":[0.49444,-0.13131,0.01985],"tcp_start":[0.46711,0.0051,0.02142],"tcp_to_object_dist_end":0.03738,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48541,-0.16784,0.02499],"object_pos_start":[0.48553,-0.16724,0.02502],"object_to_goal_dist_end":0.02304,"object_to_goal_dist_start":0.0225,"object_z_max":0.02502,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3997.0,"raw_peak_contact_force":0.8465,"tcp_end":[0.49368,0.00682,0.11268],"tcp_start":[0.49444,-0.13131,0.01985],"tcp_to_object_dist_end":0.19561,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `e864853e179d3df1b19d9aaa17e18a5fe8c66fe7533fc0dd3a88a693de7416e7`; realized-scene SHA-256: `35b7946dd60174c5d3e72b05c58367a0800836a817579e6ae5b810157d0560be`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45028,-0.03158,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.04972,-0.11842,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.45028,-0.03158,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.78322,"average_solve_count":143.0,"average_success_count":143.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.08366,"approach_1.speed":0.09983,"push_1.push_distance":0.08589},"optimized_scores":{"best_composite_score":0.54056,"best_fitness_score":0.75056,"best_task_score":0.63498},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1302.0,"contact_point_centroid":[0.45789,-0.10557,-6e-05],"force_p95":35.24985,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":47.66593,"mean_force":6.95659,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47203,-0.06797,0.01959]},{"body_a":"attachment","body_b":"push_box","contact_count":593.0,"contact_point_centroid":[0.47336,-0.06516,0.03361],"force_p95":28.20365,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":46.05627,"mean_force":10.85801,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46631,-0.05371,0.01964]},{"body_a":"push_box","body_b":"link7","contact_count":255.0,"contact_point_centroid":[0.48086,-0.04442,0.05075],"force_p95":22.00306,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":31.17757,"mean_force":15.02291,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.45389,-0.02211,0.02003]},{"body_a":"attachment","body_b":"push_box","contact_count":81.0,"contact_point_centroid":[0.45175,-0.01027,0.03112],"force_p95":10.59669,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.84089,"mean_force":3.89762,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.44606,0.00163,0.02244]},{"body_a":"world","body_b":"push_box","contact_count":1931.0,"contact_point_centroid":[0.4503,-0.03238,-1e-05],"force_p95":1.58592,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.85297,"mean_force":0.41001,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.4458,0.02307,0.0266]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.48662,-0.12763,0.02298],"force_p95":3.71924,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.71924,"mean_force":3.71924,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49317,-0.11807,0.01988]},{"body_a":"world","body_b":"push_box","contact_count":3987.0,"contact_point_centroid":[0.45546,-0.13545,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.68247,"mean_force":0.24636,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49123,-0.05129,0.0709]},{"body_a":"world","body_b":"push_box","contact_count":3404.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47375,0.02263,0.1666]}],"total_contact_groups":8},"final_pose_error":0.1347,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.45543,-0.13545,0.02499],"final_tcp_position":[0.49323,0.02021,0.11461],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":47.66593,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":851.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3404.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.44887,0.04566,0.03429],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07782,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":523.0,"n_steps_budget":600.0,"object_pos_end":[0.45146,-0.03912,0.02496],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12104,"object_to_goal_dist_start":0.12843,"object_z_max":0.02505,"peak_contact_force":3.18069,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2012.0,"raw_peak_contact_force":13.84089,"tcp_end":[0.4462,-0.0022,0.02177],"tcp_start":[0.44887,0.04566,0.03429],"tcp_to_object_dist_end":0.03743,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":753.0,"n_steps_budget":840.0,"object_pos_end":[0.45612,-0.13486,0.02501],"object_pos_start":[0.45146,-0.03912,0.02496],"object_to_goal_dist_end":0.04641,"object_to_goal_dist_start":0.12104,"object_z_max":0.03224,"peak_contact_force":0.74094,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2150.0,"raw_peak_contact_force":47.66593,"tcp_end":[0.49317,-0.11807,0.01988],"tcp_start":[0.4462,-0.0022,0.02177],"tcp_to_object_dist_end":0.04099,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45543,-0.13545,0.02499],"object_pos_start":[0.45612,-0.13486,0.02501],"object_to_goal_dist_end":0.04688,"object_to_goal_dist_start":0.04641,"object_z_max":0.02506,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3988.0,"raw_peak_contact_force":3.71924,"tcp_end":[0.49323,0.02021,0.11461],"tcp_start":[0.49317,-0.11807,0.01988],"tcp_to_object_dist_end":0.18355,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `c820cf29ab3e34ea9695cb40d5aba5de55f3ad951ee91f0df578ae7146ee7727`; realized-scene SHA-256: `721a00290a47301d7751e432f1a041db545f1b55cfdb74b1d642c32f5b25f702`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.55317,0.00136,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.05317,-0.15136,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.55317,0.00136,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.81212,"average_solve_count":165.0,"average_success_count":165.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.20479,"approach_1.speed":0.08425,"push_1.push_distance":0.13531},"optimized_scores":{"best_composite_score":0.58305,"best_fitness_score":0.79305,"best_task_score":0.74955},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":989.0,"contact_point_centroid":[0.56366,-0.05775,0.05447],"force_p95":130.04046,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":134.39663,"mean_force":87.97647,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52824,-0.04582,0.0243]},{"body_a":"world","body_b":"push_box","contact_count":1936.0,"contact_point_centroid":[0.56086,-0.09009,-0.00038],"force_p95":100.5262,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":111.16003,"mean_force":57.48426,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52804,-0.04693,0.02445]},{"body_a":"attachment","body_b":"push_box","contact_count":986.0,"contact_point_centroid":[0.54828,-0.05329,0.05538],"force_p95":86.62709,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":92.61107,"mean_force":57.75022,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5282,-0.04602,0.02433]},{"body_a":"push_box","body_b":"link7","contact_count":42.0,"contact_point_centroid":[0.55127,-0.12587,0.05672],"force_p95":46.14877,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":73.16084,"mean_force":21.60838,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50836,-0.12097,0.03059]},{"body_a":"world","body_b":"push_box","contact_count":3604.0,"contact_point_centroid":[0.53782,-0.13231,-2e-05],"force_p95":0.44187,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":71.95921,"mean_force":0.45443,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50334,-0.04815,0.08213]},{"body_a":"attachment","body_b":"push_box","contact_count":96.0,"contact_point_centroid":[0.52944,-0.11588,0.05925],"force_p95":28.91561,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":54.80371,"mean_force":6.95738,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50675,-0.11343,0.03562]},{"body_a":"attachment","body_b":"push_box","contact_count":92.0,"contact_point_centroid":[0.55345,0.02248,0.03693],"force_p95":8.46963,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.90053,"mean_force":2.80268,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54758,0.03444,0.02024]},{"body_a":"world","body_b":"push_box","contact_count":1877.0,"contact_point_centroid":[0.55332,-0.00039,-1e-05],"force_p95":1.02047,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.3283,"mean_force":0.38921,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54518,0.05605,0.02337]},{"body_a":"world","body_b":"push_box","contact_count":3872.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5223,0.03844,0.16444]}],"total_contact_groups":9},"final_pose_error":0.13471,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.5359,-0.13197,0.02499],"final_tcp_position":[0.50118,0.01891,0.11901],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":134.39663,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":968.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3872.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.54659,0.07722,0.03112],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07639,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":529.0,"n_steps_budget":600.0,"object_pos_end":[0.55489,-0.00656,0.02497],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.15358,"object_to_goal_dist_start":0.16043,"object_z_max":0.02513,"peak_contact_force":8.85336,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1969.0,"raw_peak_contact_force":11.90053,"tcp_end":[0.54815,0.03039,0.01977],"tcp_start":[0.54659,0.07722,0.03112],"tcp_to_object_dist_end":0.03792,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54882,-0.13971,0.03054],"object_pos_start":[0.55489,-0.00656,0.02497],"object_to_goal_dist_end":0.0502,"object_to_goal_dist_start":0.15358,"object_z_max":0.03106,"peak_contact_force":130.32098,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3911.0,"raw_peak_contact_force":134.39663,"tcp_end":[0.50968,-0.12317,0.02913],"tcp_start":[0.54815,0.03039,0.01977],"tcp_to_object_dist_end":0.04251,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5359,-0.13197,0.02499],"object_pos_start":[0.54882,-0.13971,0.03054],"object_to_goal_dist_end":0.04018,"object_to_goal_dist_start":0.0502,"object_z_max":0.03259,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3742.0,"raw_peak_contact_force":73.16084,"tcp_end":[0.50118,0.01891,0.11901],"tcp_start":[0.50968,-0.12317,0.02913],"tcp_to_object_dist_end":0.18113,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```