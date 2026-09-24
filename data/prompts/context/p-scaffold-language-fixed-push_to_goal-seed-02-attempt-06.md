## Search State

- **Seed**: 2
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → contact → push → retract | linear_cartesian | impedance_motion | linear_cartesian | arc_cartesian | position_control | admittance_control | position_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.5817 | 0.73 | ❌ rejected |
| 5 | approach → contact → push → retract | linear_cartesian | impedance_motion | linear_cartesian | arc_cartesian | position_control | admittance_control | position_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.5886 | 0.74 | ❌ rejected |
| 4 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | -0.1308 | 0.00 | ❌ rejected |
| 3 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 9 | -0.1933 | 0.00 | ❌ rejected |
| 2 | approach → contact → push → retract | linear_cartesian | impedance_motion | linear_cartesian | arc_cartesian | position_control | admittance_control | position_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.5949 | 0.76 | ✅ accepted |

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

## Current Skill (Q=0.582) — your mutation base

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

- **Composite score**: 0.582
- **task_score** (E): 0.729
- **fitness_score**: 0.792  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.210

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2776 |
| contact_1 | 1.00 | 1.00 | 0.0490 |
| push_1 | 1.00 | 1.00 | 0.1381 |
| retract_1 | 0.00 | 1.00 | 0.1669 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.488, 0.059, 0.033) | (0.492, -0.018, 0.025)→(0.492, -0.018, 0.025) | 0.139→0.139 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / step_budget | (0.488, 0.059, 0.033)→(0.487, 0.011, 0.021) | (0.492, -0.018, 0.025)→(0.493, -0.026, 0.025) | 0.139→0.132 | 1.00 / 2.000 | 2.786 | 14.734 |
| push_1 | push | 1.00 / step_budget | (0.487, 0.011, 0.021)→(0.499, -0.121, 0.023) | (0.493, -0.026, 0.025)→(0.492, -0.143, 0.027) | 0.132→0.041 | 1.00 / 3.333 | 43.752 | 87.396 |
| retract_1 | retract | 0.00 / step_budget | (0.499, -0.121, 0.023)→(0.496, 0.017, 0.116) | (0.492, -0.143, 0.027)→(0.488, -0.141, 0.025) | 0.041→0.037 | 1.00 / 4.000 | 0.245 | 26.934 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.453
- goal_progress: 0.804
- terminal_score: 0.804
- phase_score: 0.843
- phase_breakdown.approach_score: 0.822
- phase_breakdown.push_score: 0.837
- phase_breakdown.contact_score: 0.868

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.827
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.804
- **Median Q (composite search score)**: 0.583
- **K-run variance**: 0.0009
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.302


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.78472,"average_solve_count":144.0,"average_success_count":144.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.28424,"approach_1.speed":0.09979,"push_1.push_distance":0.09611},"optimized_scores":{"best_composite_score":0.61746,"best_fitness_score":0.82746,"best_task_score":0.80353},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1244.0,"contact_point_centroid":[0.48243,-0.10999,-0.00011],"force_p95":55.04314,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":69.61433,"mean_force":12.54491,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.482,-0.06646,0.01959]},{"body_a":"attachment","body_b":"push_box","contact_count":653.0,"contact_point_centroid":[0.48729,-0.06189,0.03495],"force_p95":40.02172,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":50.40101,"mean_force":16.33714,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47865,-0.05027,0.01973]},{"body_a":"push_box","body_b":"link7","contact_count":284.0,"contact_point_centroid":[0.50006,-0.04104,0.05116],"force_p95":37.65871,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.23969,"mean_force":28.44652,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47214,-0.0168,0.0204]},{"body_a":"attachment","body_b":"push_box","contact_count":77.0,"contact_point_centroid":[0.47009,-0.00285,0.02746],"force_p95":10.92272,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.29564,"mean_force":3.92221,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.46688,0.00905,0.02207]},{"body_a":"world","body_b":"push_box","contact_count":1934.0,"contact_point_centroid":[0.47162,-0.02491,-1e-05],"force_p95":0.90885,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.21939,"mean_force":0.40441,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.46618,0.03022,0.02611]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.47485,-0.1532,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.37276,"mean_force":0.24533,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49205,-0.05434,0.07023]},{"body_a":"world","body_b":"push_box","contact_count":3424.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48366,0.02611,0.16637]}],"total_contact_groups":7},"final_pose_error":0.13826,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.47485,-0.1532,0.02499],"final_tcp_position":[0.49371,0.01671,0.11379],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":69.61433,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":856.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3424.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.46886,0.05266,0.03395],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.0774,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":524.0,"n_steps_budget":600.0,"object_pos_end":[0.47307,-0.03174,0.02504],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12129,"object_to_goal_dist_start":0.12903,"object_z_max":0.02518,"peak_contact_force":0.0,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2011.0,"raw_peak_contact_force":16.29564,"tcp_end":[0.46711,0.00512,0.02142],"tcp_start":[0.46886,0.05266,0.03395],"tcp_to_object_dist_end":0.03751,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":783.0,"n_steps_budget":870.0,"object_pos_end":[0.47492,-0.15315,0.02441],"object_pos_start":[0.47307,-0.03174,0.02504],"object_to_goal_dist_end":0.02528,"object_to_goal_dist_start":0.12129,"object_z_max":0.03103,"peak_contact_force":0.40559,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2181.0,"raw_peak_contact_force":69.61433,"tcp_end":[0.4943,-0.12051,0.01987],"tcp_start":[0.46711,0.00512,0.02142],"tcp_to_object_dist_end":0.03822,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47485,-0.1532,0.02499],"object_pos_start":[0.47492,-0.15315,0.02441],"object_to_goal_dist_end":0.02535,"object_to_goal_dist_start":0.02528,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.37276,"tcp_end":[0.49371,0.01671,0.11379],"tcp_start":[0.4943,-0.12051,0.01987],"tcp_to_object_dist_end":0.19264,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.3027,"average_solve_count":185.0,"average_success_count":185.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.18589,"approach_1.speed":0.0585,"push_1.push_distance":0.08926},"optimized_scores":{"best_composite_score":0.54441,"best_fitness_score":0.75441,"best_task_score":0.62372},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1362.0,"contact_point_centroid":[0.45777,-0.10925,-6e-05],"force_p95":39.07458,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":54.72263,"mean_force":6.49027,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47274,-0.07173,0.0195]},{"body_a":"attachment","body_b":"push_box","contact_count":595.0,"contact_point_centroid":[0.4717,-0.06597,0.03171],"force_p95":29.69859,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":39.29041,"mean_force":10.49401,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.466,-0.0545,0.01961]},{"body_a":"push_box","body_b":"link7","contact_count":209.0,"contact_point_centroid":[0.47999,-0.04256,0.05044],"force_p95":25.61106,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":30.91217,"mean_force":18.26107,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.45216,-0.01786,0.02025]},{"body_a":"attachment","body_b":"push_box","contact_count":79.0,"contact_point_centroid":[0.45217,-0.01019,0.03178],"force_p95":10.72058,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.77808,"mean_force":4.32719,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.44607,0.00169,0.02247]},{"body_a":"world","body_b":"push_box","contact_count":1929.0,"contact_point_centroid":[0.45038,-0.03252,-1e-05],"force_p95":1.46819,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.1683,"mean_force":0.42459,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.44582,0.02308,0.02668]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.48693,-0.13112,0.02283],"force_p95":7.74767,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.74767,"mean_force":7.74767,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49326,-0.12137,0.01986]},{"body_a":"world","body_b":"push_box","contact_count":3976.0,"contact_point_centroid":[0.45315,-0.13813,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.55769,"mean_force":0.24766,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49127,-0.05449,0.07061]},{"body_a":"world","body_b":"push_box","contact_count":3696.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47372,0.02261,0.16667]}],"total_contact_groups":8},"final_pose_error":0.13859,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.45315,-0.13815,0.02499],"final_tcp_position":[0.4932,0.01637,0.11388],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":54.72263,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":924.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3696.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.44889,0.04564,0.03442],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07781,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":523.0,"n_steps_budget":600.0,"object_pos_end":[0.45157,-0.03892,0.02507],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12118,"object_to_goal_dist_start":0.12843,"object_z_max":0.02515,"peak_contact_force":7.6292,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2008.0,"raw_peak_contact_force":15.77808,"tcp_end":[0.44622,-0.00217,0.0218],"tcp_start":[0.44889,0.04564,0.03442],"tcp_to_object_dist_end":0.03727,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":783.0,"n_steps_budget":870.0,"object_pos_end":[0.45424,-0.13713,0.025],"object_pos_start":[0.45157,-0.03892,0.02507],"object_to_goal_dist_end":0.04754,"object_to_goal_dist_start":0.12118,"object_z_max":0.02944,"peak_contact_force":0.61447,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2166.0,"raw_peak_contact_force":54.72263,"tcp_end":[0.49326,-0.12129,0.01988],"tcp_start":[0.44622,-0.00217,0.0218],"tcp_to_object_dist_end":0.04243,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45315,-0.13815,0.02499],"object_pos_start":[0.45424,-0.13713,0.025],"object_to_goal_dist_end":0.04833,"object_to_goal_dist_start":0.04754,"object_z_max":0.02517,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3977.0,"raw_peak_contact_force":7.74767,"tcp_end":[0.4932,0.01637,0.11388],"tcp_start":[0.49326,-0.12129,0.01988],"tcp_to_object_dist_end":0.18271,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.80625,"average_solve_count":160.0,"average_success_count":160.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.1076,"approach_1.speed":0.09059,"push_1.push_distance":0.13435},"optimized_scores":{"best_composite_score":0.58326,"best_fitness_score":0.79326,"best_task_score":0.75844},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":985.0,"contact_point_centroid":[0.5622,-0.058,0.05485],"force_p95":130.49311,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":137.85016,"mean_force":87.23629,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.528,-0.04578,0.02423]},{"body_a":"world","body_b":"push_box","contact_count":1927.0,"contact_point_centroid":[0.55905,-0.09187,-0.00037],"force_p95":100.08829,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":111.84565,"mean_force":57.15613,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52773,-0.04707,0.02438]},{"body_a":"attachment","body_b":"push_box","contact_count":990.0,"contact_point_centroid":[0.54785,-0.05278,0.0545],"force_p95":88.95254,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":97.33803,"mean_force":58.93667,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5281,-0.0454,0.02421]},{"body_a":"push_box","body_b":"link7","contact_count":42.0,"contact_point_centroid":[0.55175,-0.12416,0.05707],"force_p95":51.4324,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":72.68211,"mean_force":20.29359,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50878,-0.11992,0.03095]},{"body_a":"world","body_b":"push_box","contact_count":3582.0,"contact_point_centroid":[0.53658,-0.13325,-2e-05],"force_p95":0.49577,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":71.0493,"mean_force":0.44623,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50364,-0.04713,0.08253]},{"body_a":"attachment","body_b":"push_box","contact_count":98.0,"contact_point_centroid":[0.52941,-0.1146,0.05941],"force_p95":31.27992,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":55.74252,"mean_force":6.70439,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50707,-0.11184,0.0364]},{"body_a":"attachment","body_b":"push_box","contact_count":89.0,"contact_point_centroid":[0.55366,0.02257,0.03749],"force_p95":10.11854,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.12765,"mean_force":3.25608,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54759,0.03452,0.02024]},{"body_a":"world","body_b":"push_box","contact_count":1878.0,"contact_point_centroid":[0.55317,-0.00049,-1e-05],"force_p95":0.94557,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.54148,"mean_force":0.40644,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54519,0.05605,0.0233]},{"body_a":"world","body_b":"push_box","contact_count":3848.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52232,0.03847,0.16436]}],"total_contact_groups":9},"final_pose_error":0.13424,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53472,-0.13279,0.02499],"final_tcp_position":[0.50138,0.01937,0.11907],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":137.85016,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":962.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3848.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.5466,0.07725,0.031],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07641,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":529.0,"n_steps_budget":600.0,"object_pos_end":[0.55389,-0.00634,0.02508],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.15344,"object_to_goal_dist_start":0.16043,"object_z_max":0.02516,"peak_contact_force":0.72856,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1967.0,"raw_peak_contact_force":12.12765,"tcp_end":[0.54817,0.03042,0.01979],"tcp_start":[0.5466,0.07725,0.031],"tcp_to_object_dist_end":0.03757,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54757,-0.14018,0.0309],"object_pos_start":[0.55389,-0.00634,0.02508],"object_to_goal_dist_end":0.04893,"object_to_goal_dist_start":0.15344,"object_z_max":0.0311,"peak_contact_force":130.23507,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3902.0,"raw_peak_contact_force":137.85016,"tcp_end":[0.51011,-0.12218,0.02951],"tcp_start":[0.54817,0.03042,0.01979],"tcp_to_object_dist_end":0.04159,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53472,-0.13279,0.02499],"object_pos_start":[0.54757,-0.14018,0.0309],"object_to_goal_dist_end":0.03875,"object_to_goal_dist_start":0.04893,"object_z_max":0.03325,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3722.0,"raw_peak_contact_force":72.68211,"tcp_end":[0.50138,0.01937,0.11907],"tcp_start":[0.51011,-0.12218,0.02951],"tcp_to_object_dist_end":0.18198,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```