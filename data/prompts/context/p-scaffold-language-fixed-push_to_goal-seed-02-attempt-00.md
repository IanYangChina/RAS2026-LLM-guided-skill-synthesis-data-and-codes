## Search State

- **Seed**: 2
- **Iteration**: 1 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 0 | approach → contact → push → retract | linear_cartesian | impedance_motion | linear_cartesian | arc_cartesian | position_control | admittance_control | position_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.5898 | 0.76 | ✅ accepted |

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

## Current Skill (Q=0.590) — your mutation base

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

- **Composite score**: 0.590
- **task_score** (E): 0.756
- **fitness_score**: 0.800  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.210

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2775 |
| contact_1 | 1.00 | 1.00 | 0.0490 |
| push_1 | 1.00 | 1.00 | 0.1374 |
| retract_1 | 0.00 | 1.00 | 0.1683 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.488, 0.058, 0.033) | (0.492, -0.018, 0.025)→(0.492, -0.018, 0.025) | 0.139→0.139 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / step_budget | (0.488, 0.058, 0.033)→(0.487, 0.011, 0.021) | (0.492, -0.018, 0.025)→(0.493, -0.026, 0.025) | 0.139→0.132 | 1.00 / 2.667 | 7.477 | 12.947 |
| push_1 | push | 1.00 / step_budget | (0.487, 0.011, 0.021)→(0.499, -0.121, 0.023) | (0.493, -0.026, 0.025)→(0.496, -0.144, 0.027) | 0.132→0.037 | 1.00 / 3.000 | 49.180 | 83.991 |
| retract_1 | retract | 0.00 / step_budget | (0.499, -0.121, 0.023)→(0.496, 0.019, 0.116) | (0.496, -0.144, 0.027)→(0.492, -0.142, 0.025) | 0.037→0.034 | 1.00 / 4.000 | 0.245 | 27.458 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.444
- goal_progress: 0.876
- terminal_score: 0.876
- phase_score: 0.830
- phase_breakdown.approach_score: 0.820
- phase_breakdown.push_score: 0.811
- phase_breakdown.contact_score: 0.869

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.849
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.876
- **Median Q (composite search score)**: 0.584
- **K-run variance**: 0.0014
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.180


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.26829,"average_solve_count":205.0,"average_success_count":205.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.15268,"approach_1.speed":0.04577,"push_1.push_distance":0.09368},"optimized_scores":{"best_composite_score":0.63851,"best_fitness_score":0.84851,"best_task_score":0.87579},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1101.0,"contact_point_centroid":[0.48506,-0.10785,-9e-05],"force_p95":50.4934,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":65.06869,"mean_force":12.29224,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48128,-0.06248,0.01951]},{"body_a":"attachment","body_b":"push_box","contact_count":662.0,"contact_point_centroid":[0.48779,-0.0659,0.03386],"force_p95":36.85292,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":50.40997,"mean_force":14.21743,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47964,-0.05424,0.01963]},{"body_a":"push_box","body_b":"link7","contact_count":274.0,"contact_point_centroid":[0.49938,-0.0415,0.05116],"force_p95":34.22608,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.16123,"mean_force":24.45176,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.472,-0.01732,0.02014]},{"body_a":"attachment","body_b":"push_box","contact_count":83.0,"contact_point_centroid":[0.47345,-0.0028,0.03317],"force_p95":9.615,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.76681,"mean_force":3.7949,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.46689,0.00908,0.0221]},{"body_a":"world","body_b":"push_box","contact_count":1912.0,"contact_point_centroid":[0.4715,-0.02529,-1e-05],"force_p95":1.67451,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.87557,"mean_force":0.41381,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.46618,0.03036,0.02619]},{"body_a":"world","body_b":"push_box","contact_count":3989.0,"contact_point_centroid":[0.48463,-0.15456,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.98671,"mean_force":0.24618,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49202,-0.05126,0.07083]},{"body_a":"world","body_b":"push_box","contact_count":3736.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48364,0.02604,0.16666]}],"total_contact_groups":7},"final_pose_error":0.13465,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.48463,-0.15455,0.02499],"final_tcp_position":[0.49373,0.02025,0.11457],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":65.06869,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":934.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3736.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.46887,0.05264,0.03404],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07739,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":523.0,"n_steps_budget":600.0,"object_pos_end":[0.4727,-0.03173,0.02494],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12138,"object_to_goal_dist_start":0.12903,"object_z_max":0.02511,"peak_contact_force":16.0,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1995.0,"raw_peak_contact_force":11.76681,"tcp_end":[0.46711,0.0051,0.02142],"tcp_start":[0.46887,0.05264,0.03404],"tcp_to_object_dist_end":0.03742,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":753.0,"n_steps_budget":840.0,"object_pos_end":[0.48474,-0.15368,0.02513],"object_pos_start":[0.4727,-0.03173,0.02494],"object_to_goal_dist_end":0.0157,"object_to_goal_dist_start":0.12138,"object_z_max":0.03124,"peak_contact_force":0.38216,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2037.0,"raw_peak_contact_force":65.06869,"tcp_end":[0.49422,-0.11798,0.01985],"tcp_start":[0.46711,0.0051,0.02142],"tcp_to_object_dist_end":0.03732,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48463,-0.15455,0.02499],"object_pos_start":[0.48474,-0.15368,0.02513],"object_to_goal_dist_end":0.01603,"object_to_goal_dist_start":0.0157,"object_z_max":0.02513,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3989.0,"raw_peak_contact_force":0.98671,"tcp_end":[0.49373,0.02025,0.11457],"tcp_start":[0.49422,-0.11798,0.01985],"tcp_to_object_dist_end":0.19663,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.27184,"average_solve_count":206.0,"average_success_count":206.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.15956,"approach_1.speed":0.04148,"push_1.push_distance":0.0879},"optimized_scores":{"best_composite_score":0.54684,"best_fitness_score":0.75684,"best_task_score":0.63662},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1379.0,"contact_point_centroid":[0.45852,-0.10725,-7e-05],"force_p95":32.69983,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":47.72548,"mean_force":6.73922,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47236,-0.06996,0.01953]},{"body_a":"attachment","body_b":"push_box","contact_count":606.0,"contact_point_centroid":[0.47351,-0.06625,0.03383],"force_p95":26.57074,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.02358,"mean_force":10.81178,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46638,-0.05477,0.01963]},{"body_a":"push_box","body_b":"link7","contact_count":253.0,"contact_point_centroid":[0.48059,-0.04434,0.05062],"force_p95":21.78777,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.81594,"mean_force":15.82383,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.45347,-0.02171,0.01998]},{"body_a":"attachment","body_b":"push_box","contact_count":81.0,"contact_point_centroid":[0.45166,-0.01025,0.03099],"force_p95":11.26319,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.10783,"mean_force":3.80063,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.44606,0.00166,0.02246]},{"body_a":"world","body_b":"push_box","contact_count":1938.0,"contact_point_centroid":[0.45025,-0.03249,-1e-05],"force_p95":1.0973,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.75998,"mean_force":0.40602,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.44582,0.02297,0.02667]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.48671,-0.12967,0.02296],"force_p95":8.61168,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.61168,"mean_force":8.61168,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49325,-0.12011,0.01988]},{"body_a":"world","body_b":"push_box","contact_count":3979.0,"contact_point_centroid":[0.45502,-0.13753,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.95385,"mean_force":0.2483,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4913,-0.05261,0.07114]},{"body_a":"world","body_b":"push_box","contact_count":3712.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47374,0.02259,0.16679]}],"total_contact_groups":8},"final_pose_error":0.1355,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.45503,-0.13752,0.02499],"final_tcp_position":[0.49327,0.01933,0.1148],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":47.72548,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":928.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3712.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.4489,0.04564,0.03445],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07781,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":523.0,"n_steps_budget":600.0,"object_pos_end":[0.45136,-0.03902,0.02506],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12118,"object_to_goal_dist_start":0.12843,"object_z_max":0.02508,"peak_contact_force":0.18606,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2019.0,"raw_peak_contact_force":15.10783,"tcp_end":[0.44621,-0.0022,0.02179],"tcp_start":[0.4489,0.04564,0.03445],"tcp_to_object_dist_end":0.03732,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":783.0,"n_steps_budget":870.0,"object_pos_end":[0.45574,-0.13653,0.02495],"object_pos_start":[0.45136,-0.03902,0.02506],"object_to_goal_dist_end":0.04626,"object_to_goal_dist_start":0.12118,"object_z_max":0.03091,"peak_contact_force":16.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2238.0,"raw_peak_contact_force":47.72548,"tcp_end":[0.49325,-0.12011,0.01988],"tcp_start":[0.44621,-0.0022,0.02179],"tcp_to_object_dist_end":0.04126,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45503,-0.13752,0.02499],"object_pos_start":[0.45574,-0.13653,0.02495],"object_to_goal_dist_end":0.04667,"object_to_goal_dist_start":0.04626,"object_z_max":0.02512,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3980.0,"raw_peak_contact_force":8.61168,"tcp_end":[0.49327,0.01933,0.1148],"tcp_start":[0.49325,-0.12011,0.01988],"tcp_to_object_dist_end":0.18474,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.80128,"average_solve_count":156.0,"average_success_count":156.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.19235,"approach_1.speed":0.09599,"push_1.push_distance":0.13644},"optimized_scores":{"best_composite_score":0.58401,"best_fitness_score":0.79401,"best_task_score":0.75666},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":990.0,"contact_point_centroid":[0.56311,-0.05821,0.05451],"force_p95":131.16017,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":139.1785,"mean_force":86.95151,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52817,-0.04612,0.02416]},{"body_a":"world","body_b":"push_box","contact_count":1903.0,"contact_point_centroid":[0.56055,-0.09185,-0.00039],"force_p95":101.64317,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":112.77812,"mean_force":57.97224,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52772,-0.04838,0.02442]},{"body_a":"attachment","body_b":"push_box","contact_count":992.0,"contact_point_centroid":[0.54777,-0.05333,0.05417],"force_p95":89.95612,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":99.55888,"mean_force":57.73765,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52822,-0.04596,0.02415]},{"body_a":"push_box","body_b":"link7","contact_count":42.0,"contact_point_centroid":[0.55166,-0.1261,0.05699],"force_p95":48.60234,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":72.77667,"mean_force":20.91556,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50877,-0.1216,0.03082]},{"body_a":"world","body_b":"push_box","contact_count":3581.0,"contact_point_centroid":[0.53731,-0.13369,-2e-05],"force_p95":0.48828,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":70.92485,"mean_force":0.45105,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50362,-0.04825,0.08257]},{"body_a":"attachment","body_b":"push_box","contact_count":95.0,"contact_point_centroid":[0.52999,-0.11661,0.05985],"force_p95":29.53315,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":55.16531,"mean_force":6.93999,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50716,-0.11413,0.03578]},{"body_a":"attachment","body_b":"push_box","contact_count":88.0,"contact_point_centroid":[0.55379,0.02265,0.03797],"force_p95":9.95959,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.9651,"mean_force":3.27352,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54758,0.03461,0.02029]},{"body_a":"world","body_b":"push_box","contact_count":1900.0,"contact_point_centroid":[0.55321,-0.00022,-1e-05],"force_p95":1.02405,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.36493,"mean_force":0.40231,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54521,0.05574,0.0234]},{"body_a":"world","body_b":"push_box","contact_count":3820.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5223,0.03842,0.16453]}],"total_contact_groups":9},"final_pose_error":0.13493,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53534,-0.13343,0.02499],"final_tcp_position":[0.50137,0.01865,0.11917],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":139.1785,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":955.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3820.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.54657,0.07718,0.03124],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07637,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":529.0,"n_steps_budget":600.0,"object_pos_end":[0.5545,-0.00648,0.025],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.15352,"object_to_goal_dist_start":0.16043,"object_z_max":0.02513,"peak_contact_force":6.24574,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1988.0,"raw_peak_contact_force":11.9651,"tcp_end":[0.54816,0.03038,0.01979],"tcp_start":[0.54657,0.07718,0.03124],"tcp_to_object_dist_end":0.03777,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54827,-0.14092,0.03079],"object_pos_start":[0.5545,-0.00648,0.025],"object_to_goal_dist_end":0.04946,"object_to_goal_dist_start":0.15352,"object_z_max":0.0311,"peak_contact_force":131.15864,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3885.0,"raw_peak_contact_force":139.1785,"tcp_end":[0.51008,-0.12382,0.02936],"tcp_start":[0.54816,0.03038,0.01979],"tcp_to_object_dist_end":0.04187,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53534,-0.13343,0.02499],"object_pos_start":[0.54827,-0.14092,0.03079],"object_to_goal_dist_end":0.03904,"object_to_goal_dist_start":0.04946,"object_z_max":0.03303,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3718.0,"raw_peak_contact_force":72.77667,"tcp_end":[0.50137,0.01865,0.11917],"tcp_start":[0.51008,-0.12382,0.02936],"tcp_to_object_dist_end":0.18207,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```