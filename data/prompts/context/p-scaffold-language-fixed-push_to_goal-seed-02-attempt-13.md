## Search State

- **Seed**: 2
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → contact → push → retract | linear_cartesian | impedance_motion | linear_cartesian | arc_cartesian | position_control | admittance_control | position_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.5829 | 0.74 | ❌ rejected |
| 12 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.5838 | 0.72 | ✅ accepted |
| 11 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.1150 | 0.00 | ❌ rejected |
| 10 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.5971 | 0.76 | ✅ accepted |
| 9 | approach → contact → push → retract | linear_cartesian | impedance_motion | linear_cartesian | arc_cartesian | position_control | admittance_control | position_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.5975 | 0.76 | ❌ rejected |

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

## Current Skill (Q=0.583) — your mutation base

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

- **Composite score**: 0.583
- **task_score** (E): 0.738
- **fitness_score**: 0.793  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.210

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2776 |
| contact_1 | 1.00 | 1.00 | 0.0490 |
| push_1 | 1.00 | 1.00 | 0.1377 |
| retract_1 | 0.00 | 1.00 | 0.1676 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.488, 0.059, 0.033) | (0.492, -0.018, 0.025)→(0.492, -0.018, 0.025) | 0.139→0.139 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / step_budget | (0.488, 0.059, 0.033)→(0.487, 0.011, 0.021) | (0.492, -0.018, 0.025)→(0.493, -0.026, 0.025) | 0.139→0.132 | 1.00 / 2.667 | 7.854 | 12.918 |
| push_1 | push | 1.00 / step_budget | (0.487, 0.011, 0.021)→(0.499, -0.121, 0.023) | (0.493, -0.026, 0.025)→(0.493, -0.143, 0.027) | 0.132→0.039 | 1.00 / 3.667 | 44.445 | 82.572 |
| retract_1 | retract | 0.00 / step_budget | (0.499, -0.121, 0.023)→(0.496, 0.018, 0.116) | (0.493, -0.143, 0.027)→(0.489, -0.141, 0.025) | 0.039→0.036 | 1.00 / 4.000 | 0.245 | 28.324 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.989
- lateral_force_integral: None
- approach_alignment: 0.443
- goal_progress: 0.838
- terminal_score: 0.838
- phase_score: 0.825
- phase_breakdown.contact_score: 0.869
- phase_breakdown.approach_score: 0.820
- phase_breakdown.push_score: 0.801

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.830
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.838
- **Median Q (composite search score)**: 0.582
- **K-run variance**: 0.0009
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.241


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.26829,"average_solve_count":205.0,"average_success_count":205.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.20674,"approach_1.speed":0.04709,"push_1.push_distance":0.0927},"optimized_scores":{"best_composite_score":0.62038,"best_fitness_score":0.83038,"best_task_score":0.83804},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1095.0,"contact_point_centroid":[0.48391,-0.10906,-0.0001],"force_p95":50.46953,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":61.53204,"mean_force":14.11345,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48201,-0.06422,0.01966]},{"body_a":"attachment","body_b":"push_box","contact_count":649.0,"contact_point_centroid":[0.48917,-0.06357,0.0366],"force_p95":36.77775,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":47.45437,"mean_force":16.40898,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47946,-0.05199,0.01978]},{"body_a":"push_box","body_b":"link7","contact_count":322.0,"contact_point_centroid":[0.50008,-0.04446,0.05144],"force_p95":33.75493,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":46.20104,"mean_force":25.47897,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47303,-0.02108,0.0202]},{"body_a":"attachment","body_b":"push_box","contact_count":83.0,"contact_point_centroid":[0.47345,-0.0028,0.03317],"force_p95":9.615,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.76681,"mean_force":3.7949,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.46689,0.00908,0.0221]},{"body_a":"world","body_b":"push_box","contact_count":1912.0,"contact_point_centroid":[0.4715,-0.02529,-1e-05],"force_p95":1.67451,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.87557,"mean_force":0.41381,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.46618,0.03036,0.02619]},{"body_a":"world","body_b":"push_box","contact_count":3994.0,"contact_point_centroid":[0.47912,-0.15156,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.99894,"mean_force":0.24615,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49202,-0.05069,0.07071]},{"body_a":"world","body_b":"push_box","contact_count":3736.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48364,0.02604,0.16666]}],"total_contact_groups":7},"final_pose_error":0.13429,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.47916,-0.15156,0.02499],"final_tcp_position":[0.49374,0.02065,0.11448],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":61.53204,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":934.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3736.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.46887,0.05264,0.03404],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07739,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":523.0,"n_steps_budget":600.0,"object_pos_end":[0.4727,-0.03173,0.02494],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12138,"object_to_goal_dist_start":0.12903,"object_z_max":0.02511,"peak_contact_force":16.0,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1995.0,"raw_peak_contact_force":11.76681,"tcp_end":[0.46711,0.0051,0.02142],"tcp_start":[0.46887,0.05264,0.03404],"tcp_to_object_dist_end":0.03742,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":752.0,"n_steps_budget":840.0,"object_pos_end":[0.47924,-0.15104,0.02503],"object_pos_start":[0.4727,-0.03173,0.02494],"object_to_goal_dist_end":0.02079,"object_to_goal_dist_start":0.12138,"object_z_max":0.03267,"peak_contact_force":1.62272,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2066.0,"raw_peak_contact_force":61.53204,"tcp_end":[0.49423,-0.11706,0.01986],"tcp_start":[0.46711,0.0051,0.02142],"tcp_to_object_dist_end":0.03749,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47916,-0.15156,0.02499],"object_pos_start":[0.47924,-0.15104,0.02503],"object_to_goal_dist_end":0.0209,"object_to_goal_dist_start":0.02079,"object_z_max":0.02503,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3994.0,"raw_peak_contact_force":0.99894,"tcp_end":[0.49374,0.02065,0.11448],"tcp_start":[0.49423,-0.11706,0.01986],"tcp_to_object_dist_end":0.19462,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.80255,"average_solve_count":157.0,"average_success_count":157.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.18009,"approach_1.speed":0.08231,"push_1.push_distance":0.09153},"optimized_scores":{"best_composite_score":0.546,"best_fitness_score":0.756,"best_task_score":0.6199},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1330.0,"contact_point_centroid":[0.45849,-0.10919,-9e-05],"force_p95":35.88974,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":48.43734,"mean_force":7.4246,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47259,-0.07234,0.01956]},{"body_a":"attachment","body_b":"push_box","contact_count":589.0,"contact_point_centroid":[0.47322,-0.06649,0.03363],"force_p95":28.53426,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.53235,"mean_force":11.65544,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46598,-0.05501,0.01969]},{"body_a":"push_box","body_b":"link7","contact_count":248.0,"contact_point_centroid":[0.48075,-0.04384,0.05062],"force_p95":23.0908,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":26.85258,"mean_force":17.36167,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.45345,-0.02181,0.02008]},{"body_a":"attachment","body_b":"push_box","contact_count":81.0,"contact_point_centroid":[0.45166,-0.01025,0.03099],"force_p95":11.2747,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.11586,"mean_force":3.80284,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.44606,0.00166,0.02247]},{"body_a":"world","body_b":"push_box","contact_count":1938.0,"contact_point_centroid":[0.45025,-0.03249,-1e-05],"force_p95":1.09772,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.76556,"mean_force":0.40612,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.44583,0.02297,0.02669]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.48685,-0.13322,0.02288],"force_p95":11.28301,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.28301,"mean_force":11.28301,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49326,-0.12354,0.01987]},{"body_a":"world","body_b":"push_box","contact_count":3990.0,"contact_point_centroid":[0.45257,-0.13855,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.64986,"mean_force":0.24857,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49128,-0.05634,0.07058]},{"body_a":"world","body_b":"push_box","contact_count":3472.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47379,0.02258,0.16687]}],"total_contact_groups":8},"final_pose_error":0.1395,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.45255,-0.13855,0.02499],"final_tcp_position":[0.49321,0.01538,0.1141],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":48.43734,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":868.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3472.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.44892,0.04563,0.03449],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07781,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":523.0,"n_steps_budget":600.0,"object_pos_end":[0.45136,-0.03902,0.02506],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12117,"object_to_goal_dist_start":0.12843,"object_z_max":0.02508,"peak_contact_force":0.18604,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2019.0,"raw_peak_contact_force":15.11586,"tcp_end":[0.44621,-0.0022,0.02179],"tcp_start":[0.44892,0.04563,0.03449],"tcp_to_object_dist_end":0.03732,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":783.0,"n_steps_budget":870.0,"object_pos_end":[0.45296,-0.13805,0.02485],"object_pos_start":[0.45136,-0.03902,0.02506],"object_to_goal_dist_end":0.04853,"object_to_goal_dist_start":0.12117,"object_z_max":0.03251,"peak_contact_force":1.4156,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2167.0,"raw_peak_contact_force":48.43734,"tcp_end":[0.49326,-0.12354,0.01987],"tcp_start":[0.44621,-0.0022,0.02179],"tcp_to_object_dist_end":0.04312,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45255,-0.13855,0.02499],"object_pos_start":[0.45296,-0.13805,0.02485],"object_to_goal_dist_end":0.04882,"object_to_goal_dist_start":0.04853,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3991.0,"raw_peak_contact_force":11.28301,"tcp_end":[0.49321,0.01538,0.1141],"tcp_start":[0.49326,-0.12354,0.01987],"tcp_to_object_dist_end":0.18245,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.81176,"average_solve_count":170.0,"average_success_count":170.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.1881,"approach_1.speed":0.07877,"push_1.push_distance":0.13463},"optimized_scores":{"best_composite_score":0.58239,"best_fitness_score":0.79239,"best_task_score":0.75619},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":985.0,"contact_point_centroid":[0.56245,-0.05846,0.05461],"force_p95":130.744,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":137.74534,"mean_force":86.5705,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52788,-0.04597,0.02414]},{"body_a":"world","body_b":"push_box","contact_count":1889.0,"contact_point_centroid":[0.55974,-0.0925,-0.00038],"force_p95":100.39539,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":112.07253,"mean_force":57.8174,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52737,-0.04842,0.02442]},{"body_a":"attachment","body_b":"push_box","contact_count":993.0,"contact_point_centroid":[0.54755,-0.05282,0.05412],"force_p95":90.37084,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":97.64639,"mean_force":57.49549,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52805,-0.04534,0.02411]},{"body_a":"push_box","body_b":"link7","contact_count":42.0,"contact_point_centroid":[0.55176,-0.12429,0.05709],"force_p95":51.43107,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":72.69107,"mean_force":20.36618,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5088,-0.12007,0.03097]},{"body_a":"world","body_b":"push_box","contact_count":3584.0,"contact_point_centroid":[0.53669,-0.13296,-2e-05],"force_p95":0.48683,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":70.93844,"mean_force":0.44545,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50365,-0.04724,0.08255]},{"body_a":"attachment","body_b":"push_box","contact_count":95.0,"contact_point_centroid":[0.52975,-0.1154,0.05962],"force_p95":31.88273,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":55.77391,"mean_force":6.95097,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50718,-0.11259,0.03595]},{"body_a":"attachment","body_b":"push_box","contact_count":92.0,"contact_point_centroid":[0.5539,0.02251,0.038],"force_p95":10.36985,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.87216,"mean_force":3.36576,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.5476,0.03445,0.02024]},{"body_a":"world","body_b":"push_box","contact_count":1882.0,"contact_point_centroid":[0.55322,-0.00045,-1e-05],"force_p95":1.04389,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.3661,"mean_force":0.41617,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.5452,0.056,0.02332]},{"body_a":"world","body_b":"push_box","contact_count":3900.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52232,0.03848,0.16433]}],"total_contact_groups":9},"final_pose_error":0.1343,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53496,-0.13246,0.02499],"final_tcp_position":[0.50139,0.01931,0.11909],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":137.74534,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":975.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3900.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.5466,0.07724,0.03104],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.0764,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":529.0,"n_steps_budget":600.0,"object_pos_end":[0.55444,-0.00622,0.02516],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.15374,"object_to_goal_dist_start":0.16043,"object_z_max":0.02518,"peak_contact_force":7.37541,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1974.0,"raw_peak_contact_force":11.87216,"tcp_end":[0.54818,0.03046,0.01981],"tcp_start":[0.5466,0.07724,0.03104],"tcp_to_object_dist_end":0.0376,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54755,-0.14027,0.03092],"object_pos_start":[0.55444,-0.00622,0.02516],"object_to_goal_dist_end":0.04889,"object_to_goal_dist_start":0.15374,"object_z_max":0.03111,"peak_contact_force":130.29788,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3867.0,"raw_peak_contact_force":137.74534,"tcp_end":[0.51012,-0.12233,0.02953],"tcp_start":[0.54818,0.03046,0.01981],"tcp_to_object_dist_end":0.04152,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53496,-0.13246,0.02499],"object_pos_start":[0.54755,-0.14027,0.03092],"object_to_goal_dist_end":0.03911,"object_to_goal_dist_start":0.04889,"object_z_max":0.03329,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3721.0,"raw_peak_contact_force":72.69107,"tcp_end":[0.50139,0.01931,0.11909],"tcp_start":[0.51012,-0.12233,0.02953],"tcp_to_object_dist_end":0.18171,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```