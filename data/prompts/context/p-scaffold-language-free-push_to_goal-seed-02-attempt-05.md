## Search State

- **Seed**: 2
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → contact → push → retract | linear_cartesian | impedance_motion | linear_cartesian | arc_cartesian | position_control | admittance_control | position_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.5886 | 0.74 | ❌ rejected |
| 4 | approach → contact → push → retract | linear_cartesian | impedance_motion | linear_cartesian | arc_cartesian | position_control | admittance_control | position_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.5887 | 0.74 | ❌ rejected |
| 3 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | -0.0782 | 0.15 | ❌ rejected |
| 2 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | -0.2441 | 0.00 | ❌ rejected |
| 1 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | -0.0581 | 0.01 | ❌ rejected |

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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.756, which indicates the subtask decomposition is already effective.
> Preserve the current subtask decomposition unless the evidence shows a subtask change is necessary. Prefer refining phases, parameters, control modes, or termination conditions first.
> Unnecessary subtask redesign when performance is already high often causes regression.

## Subtask Layer

**Mode**: free (you define subtask targets; use `subtasks:` block in your YAML)

Define subtasks in a `subtasks:` block **before** `phases:`. Each subtask specifies an intermediate optimisation target.

**Required fields** — always include both, never omit:
- `anchor` (**required**): fixture | goal | object | world
- `target_entity` (**required**): hinge | object | tcp

Subtask anchors are separate from phase `target.anchor` vocabulary: subtasks use `world | object | goal | fixture`, while phase targets use `world | task_goal | task_object | fixture | body | site | current_tcp`.

Optional fields:
- `metric`: contact | distance | goal_progress | hinge_angle (default: distance)
- `offset`: [x, y, z] in metres relative to anchor (default: [0, 0, 0])
- `param_offset_key`: CMA-ES parameter added to offset at runtime (optional)
- `weight`: scoring weight [0.1, 1.0] (default: 1.0)

**Anchor resolution for this task** — choose anchor so the resolved position is meaningful:
| Anchor | Resolves to | Best used for |
|--------|-------------|---------------|
| `world` | absolute world-frame coordinate | fixed reference points not tied to objects |
| `object` | offset from object initial position (0.47139345610991795, -0.0241810627903052, 0.025) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5, -0.15, 0.025) | final destination targets |
| `fixture` | offset from fixture pose (if defined, else world) | targets near fixture |

Annotate each phase with `subtask_id: <id>` to bind it to a subtask.
Only the **last phase** bound to a given subtask contributes to subtask scoring.

Example (two subtasks — one near object start, one at goal):
```yaml
subtasks:
  - id: reach_pre_contact
    anchor: object         # resolved to object initial position (see table above)
    target_entity: tcp     # score TCP distance to this target
    metric: distance
    offset: [0.0, 0.0, 0.10]  # 10 cm above object start position
    weight: 0.3
  - id: reach_goal
    anchor: goal           # resolved to task goal position (see table above)
    target_entity: tcp
    metric: distance
    offset: [0.0, 0.0, 0.0]
    weight: 0.7
phases:
  - id: approach_1
    type: approach
    subtask_id: reach_pre_contact
    ...
  - id: push_1
    type: push
    subtask_id: reach_goal
    ...
```

## Current Skill (Q=0.589) — your mutation base

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

- **Composite score**: 0.589
- **task_score** (E): 0.739
- **fitness_score**: 0.799  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.210

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2776 |
| contact_1 | 1.00 | 1.00 | 0.0490 |
| push_1 | 1.00 | 1.00 | 0.1414 |
| retract_1 | 0.00 | 1.00 | 0.1678 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.488, 0.059, 0.033) | (0.492, -0.018, 0.025)→(0.492, -0.018, 0.025) | 0.139→0.139 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / step_budget | (0.488, 0.059, 0.033)→(0.487, 0.011, 0.021) | (0.492, -0.018, 0.025)→(0.493, -0.026, 0.025) | 0.139→0.132 | 1.00 / 3.333 | 5.169 | 14.662 |
| push_1 | push | 1.00 / step_budget | (0.487, 0.011, 0.021)→(0.499, -0.125, 0.023) | (0.493, -0.026, 0.025)→(0.494, -0.147, 0.027) | 0.132→0.039 | 1.00 / 4.000 | 46.666 | 89.028 |
| retract_1 | retract | 0.00 / step_budget | (0.499, -0.125, 0.023)→(0.496, 0.015, 0.116) | (0.494, -0.147, 0.027)→(0.490, -0.145, 0.025) | 0.039→0.036 | 1.00 / 4.000 | 0.245 | 26.865 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.458
- goal_progress: 0.821
- terminal_score: 0.821
- phase_score: 0.855
- phase_breakdown.contact_score: 0.868
- phase_breakdown.push_score: 0.859
- phase_breakdown.approach_score: 0.822

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.841
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.821
- **Median Q (composite search score)**: 0.581
- **K-run variance**: 0.0010
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.350


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.30978,"average_solve_count":184.0,"average_success_count":184.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.19097,"approach_1.speed":0.05909,"push_1.push_distance":0.10045},"optimized_scores":{"best_composite_score":0.63125,"best_fitness_score":0.84125,"best_task_score":0.82133},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1189.0,"contact_point_centroid":[0.48457,-0.11421,-0.0001],"force_p95":57.56804,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":71.61139,"mean_force":14.67761,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48199,-0.06827,0.01966]},{"body_a":"push_box","body_b":"link7","contact_count":308.0,"contact_point_centroid":[0.50059,-0.04348,0.05126],"force_p95":40.6819,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":52.52332,"mean_force":30.14528,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47262,-0.01904,0.02049]},{"body_a":"attachment","body_b":"push_box","contact_count":702.0,"contact_point_centroid":[0.48848,-0.0661,0.03558],"force_p95":39.98061,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":50.1938,"mean_force":16.9126,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47929,-0.05448,0.01982]},{"body_a":"attachment","body_b":"push_box","contact_count":75.0,"contact_point_centroid":[0.47026,-0.0027,0.02776],"force_p95":11.66263,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.2738,"mean_force":4.03713,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.46687,0.00921,0.02209]},{"body_a":"world","body_b":"push_box","contact_count":1933.0,"contact_point_centroid":[0.47161,-0.02489,-1e-05],"force_p95":0.90389,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.67929,"mean_force":0.40398,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.46618,0.03017,0.02607]},{"body_a":"attachment","body_b":"push_box","contact_count":2.0,"contact_point_centroid":[0.49153,-0.13644,0.02123],"force_p95":5.38975,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.60898,"mean_force":3.41666,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49439,-0.12491,0.01987]},{"body_a":"world","body_b":"push_box","contact_count":3983.0,"contact_point_centroid":[0.47929,-0.16016,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.22554,"mean_force":0.24753,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49212,-0.05731,0.07065]},{"body_a":"world","body_b":"push_box","contact_count":3712.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48363,0.02607,0.16655]}],"total_contact_groups":8},"final_pose_error":0.14018,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.47931,-0.16016,0.02499],"final_tcp_position":[0.49377,0.01462,0.11414],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":71.61139,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":928.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3712.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.46884,0.05267,0.03389],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.0774,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":523.0,"n_steps_budget":600.0,"object_pos_end":[0.47306,-0.03185,0.02485],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12118,"object_to_goal_dist_start":0.12903,"object_z_max":0.02517,"peak_contact_force":0.56944,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2008.0,"raw_peak_contact_force":16.2738,"tcp_end":[0.46711,0.00512,0.02141],"tcp_start":[0.46884,0.05267,0.03389],"tcp_to_object_dist_end":0.03761,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":812.0,"n_steps_budget":900.0,"object_pos_end":[0.48011,-0.15899,0.02497],"object_pos_start":[0.47306,-0.03185,0.02485],"object_to_goal_dist_end":0.02183,"object_to_goal_dist_start":0.12118,"object_z_max":0.03225,"peak_contact_force":8.38709,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2199.0,"raw_peak_contact_force":71.61139,"tcp_end":[0.49439,-0.12487,0.01987],"tcp_start":[0.46711,0.00512,0.02141],"tcp_to_object_dist_end":0.03734,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47931,-0.16016,0.02499],"object_pos_start":[0.48011,-0.15899,0.02497],"object_to_goal_dist_end":0.02305,"object_to_goal_dist_start":0.02183,"object_z_max":0.02507,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3985.0,"raw_peak_contact_force":5.60898,"tcp_end":[0.49377,0.01462,0.11414],"tcp_start":[0.49439,-0.12487,0.01987],"tcp_to_object_dist_end":0.19674,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.80255,"average_solve_count":157.0,"average_success_count":157.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.14412,"approach_1.speed":0.08255,"push_1.push_distance":0.09571},"optimized_scores":{"best_composite_score":0.5536,"best_fitness_score":0.7636,"best_task_score":0.64135},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1396.0,"contact_point_centroid":[0.45882,-0.11271,-7e-05],"force_p95":40.51174,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":56.41674,"mean_force":7.35166,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47282,-0.07528,0.01953]},{"body_a":"attachment","body_b":"push_box","contact_count":639.0,"contact_point_centroid":[0.47257,-0.06913,0.03273],"force_p95":30.15627,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.22073,"mean_force":11.29928,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46634,-0.05776,0.01967]},{"body_a":"push_box","body_b":"link7","contact_count":235.0,"contact_point_centroid":[0.48039,-0.04417,0.05062],"force_p95":26.66326,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":36.06299,"mean_force":19.45054,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.45277,-0.02003,0.02027]},{"body_a":"attachment","body_b":"push_box","contact_count":79.0,"contact_point_centroid":[0.45217,-0.01019,0.03178],"force_p95":10.72047,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.77754,"mean_force":4.32716,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.44607,0.00169,0.02247]},{"body_a":"world","body_b":"push_box","contact_count":1929.0,"contact_point_centroid":[0.45038,-0.03252,-1e-05],"force_p95":1.46821,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.16808,"mean_force":0.42459,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.44582,0.02308,0.02668]},{"body_a":"attachment","body_b":"push_box","contact_count":4.0,"contact_point_centroid":[0.48591,-0.13673,0.02321],"force_p95":2.10474,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.25703,"mean_force":1.29367,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49298,-0.12765,0.01989]},{"body_a":"world","body_b":"push_box","contact_count":3988.0,"contact_point_centroid":[0.45465,-0.14195,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.48589,"mean_force":0.24665,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49131,-0.06045,0.07014]},{"body_a":"world","body_b":"push_box","contact_count":3468.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4738,0.02258,0.16689]}],"total_contact_groups":8},"final_pose_error":0.14391,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.45466,-0.14188,0.02499],"final_tcp_position":[0.49319,0.01099,0.1134],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":56.41674,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":867.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3468.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.4489,0.04564,0.03442],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07781,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":523.0,"n_steps_budget":600.0,"object_pos_end":[0.45157,-0.03892,0.02507],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12118,"object_to_goal_dist_start":0.12843,"object_z_max":0.02515,"peak_contact_force":7.6284,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2008.0,"raw_peak_contact_force":15.77754,"tcp_end":[0.44623,-0.00217,0.0218],"tcp_start":[0.4489,0.04564,0.03442],"tcp_to_object_dist_end":0.03727,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":813.0,"n_steps_budget":900.0,"object_pos_end":[0.45492,-0.14174,0.02489],"object_pos_start":[0.45157,-0.03892,0.02507],"object_to_goal_dist_end":0.04583,"object_to_goal_dist_start":0.12118,"object_z_max":0.03041,"peak_contact_force":0.41969,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2270.0,"raw_peak_contact_force":56.41674,"tcp_end":[0.49335,-0.12763,0.01985],"tcp_start":[0.44623,-0.00217,0.0218],"tcp_to_object_dist_end":0.04125,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45466,-0.14188,0.02499],"object_pos_start":[0.45492,-0.14174,0.02489],"object_to_goal_dist_end":0.04606,"object_to_goal_dist_start":0.04583,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3992.0,"raw_peak_contact_force":2.25703,"tcp_end":[0.49319,0.01099,0.1134],"tcp_start":[0.49335,-0.12763,0.01985],"tcp_to_object_dist_end":0.18075,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.81609,"average_solve_count":174.0,"average_success_count":174.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.16891,"approach_1.speed":0.07474,"push_1.push_distance":0.13464},"optimized_scores":{"best_composite_score":0.58093,"best_fitness_score":0.79093,"best_task_score":0.75383},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":986.0,"contact_point_centroid":[0.56303,-0.05792,0.0545],"force_p95":131.38018,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":139.05629,"mean_force":87.13729,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52807,-0.04558,0.02417]},{"body_a":"world","body_b":"push_box","contact_count":1915.0,"contact_point_centroid":[0.56021,-0.09096,-0.00038],"force_p95":100.54251,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":112.16072,"mean_force":57.50356,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52777,-0.04715,0.02437]},{"body_a":"attachment","body_b":"push_box","contact_count":998.0,"contact_point_centroid":[0.54779,-0.05214,0.05425],"force_p95":88.10144,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":93.60668,"mean_force":57.12099,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52831,-0.04466,0.02411]},{"body_a":"push_box","body_b":"link7","contact_count":42.0,"contact_point_centroid":[0.55177,-0.12433,0.05704],"force_p95":50.23133,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":72.73013,"mean_force":20.69176,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50886,-0.11989,0.0309]},{"body_a":"world","body_b":"push_box","contact_count":3596.0,"contact_point_centroid":[0.53711,-0.13239,-2e-05],"force_p95":0.46651,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":71.59814,"mean_force":0.44704,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50369,-0.04727,0.08236]},{"body_a":"attachment","body_b":"push_box","contact_count":95.0,"contact_point_centroid":[0.5301,-0.11523,0.05991],"force_p95":30.47655,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":55.81759,"mean_force":6.91522,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50726,-0.11259,0.03575]},{"body_a":"attachment","body_b":"push_box","contact_count":84.0,"contact_point_centroid":[0.55227,0.02257,0.0338],"force_p95":7.66025,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.93335,"mean_force":2.61392,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54755,0.03454,0.02024]},{"body_a":"world","body_b":"push_box","contact_count":1916.0,"contact_point_centroid":[0.55349,7e-05,-1e-05],"force_p95":0.94726,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.34719,"mean_force":0.36434,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54523,0.05554,0.02334]},{"body_a":"world","body_b":"push_box","contact_count":3916.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52229,0.03843,0.16448]}],"total_contact_groups":9},"final_pose_error":0.13423,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53516,-0.13201,0.02499],"final_tcp_position":[0.50141,0.0194,0.11904],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":139.05629,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":979.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3916.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.54658,0.0772,0.03118],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07637,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":529.0,"n_steps_budget":600.0,"object_pos_end":[0.55514,-0.00648,0.02495],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.15374,"object_to_goal_dist_start":0.16043,"object_z_max":0.02514,"peak_contact_force":7.30875,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2000.0,"raw_peak_contact_force":11.93335,"tcp_end":[0.54813,0.03033,0.01976],"tcp_start":[0.54658,0.0772,0.03118],"tcp_to_object_dist_end":0.03783,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54798,-0.13959,0.03085],"object_pos_start":[0.55514,-0.00648,0.02495],"object_to_goal_dist_end":0.04945,"object_to_goal_dist_start":0.15374,"object_z_max":0.0311,"peak_contact_force":131.18991,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3899.0,"raw_peak_contact_force":139.05629,"tcp_end":[0.51016,-0.12211,0.02945],"tcp_start":[0.54813,0.03033,0.01976],"tcp_to_object_dist_end":0.04169,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53516,-0.13201,0.02499],"object_pos_start":[0.54798,-0.13959,0.03085],"object_to_goal_dist_end":0.03949,"object_to_goal_dist_start":0.04945,"object_z_max":0.03313,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3733.0,"raw_peak_contact_force":72.73013,"tcp_end":[0.50141,0.0194,0.11904],"tcp_start":[0.51016,-0.12211,0.02945],"tcp_to_object_dist_end":0.18141,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```