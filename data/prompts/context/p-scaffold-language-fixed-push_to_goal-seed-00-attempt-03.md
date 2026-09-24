## Search State

- **Seed**: 0
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 9 | 0.0519 | 0.08 | ❌ rejected |
| 2 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 9 | 0.3752 | 0.72 | ❌ rejected |
| 1 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.1724 | 0.16 | ❌ rejected |
| 0 | approach → contact → push → retract | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | force_threshold_switch | admittance_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.7632 | 0.84 | ✅ accepted |

**Proposal policy**: task_score is 0.08 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `79fe20ee7316d80bc617c84166fccacf882b4f96b2faf4b155be83e4f318b183`
- Frozen object start: [0.5164354024785746, -0.027625594348335558, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.5164354024785746, -0.027625594348335558, 0.025)
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
  frozen_object_start: [0.5164, -0.0276, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.5164354024785746, -0.027625594348335558, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [-0.0164, -0.1224, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: 79fe20ee7316d80bc617c84166fccacf882b4f96b2faf4b155be83e4f318b183

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

## Current Skill (Q=0.052) — your mutation base

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
  generator: impedance_motion
  control: admittance_control
  termination: force_exceeded
  parameters:
    contact_force:
      type: scalar
      range:
      - 1.0
      - 20.0
- id: push_1
  type: push
  generator: linear_cartesian
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
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance

```

## Design Metrics

- **Composite score**: 0.052
- **task_score** (E): 0.077
- **fitness_score**: 0.062  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
  → CMA-ES cannot optimise this structure (shaped reward also near zero)
- **Termination Fidelity** (C): 0.500
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.510

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1968 |
| contact_1 | 1.00 | 1.00 | 0.0001 |
| push_1 | 1.00 | 1.00 | 0.0001 |
| retract_1 | 1.00 | 1.00 | 0.0865 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.490, 0.094, 0.131) | (0.496, 0.001, 0.025)→(0.497, 0.013, 0.031) | 0.152→0.164 | 1.00 / 4.333 | 116.631 | 235.615 |
| contact_1 | contact | 1.00 / force_exceeded | (0.490, 0.094, 0.131)→(0.490, 0.094, 0.130) | (0.497, 0.013, 0.031)→(0.497, 0.013, 0.031) | 0.164→0.164 | 1.00 / 4.333 | 46.835 | 46.835 |
| push_1 | push | 1.00 / force_exceeded | (0.490, 0.094, 0.130)→(0.490, 0.094, 0.130) | (0.497, 0.013, 0.031)→(0.496, 0.013, 0.031) | 0.164→0.164 | 1.00 / 4.333 | 67.632 | 67.632 |
| retract_1 | retract | 1.00 / step_budget | (0.490, 0.094, 0.130)→(0.488, 0.094, 0.217) | (0.496, 0.013, 0.031)→(0.495, -0.009, 0.025) | 0.164→0.143 | 1.00 / 4.000 | 0.245 | 70.186 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.135
- lateral_force_integral: None
- approach_alignment: 0.127
- goal_progress: 0.134
- terminal_score: 0.134
- phase_score: 0.053
- phase_breakdown.approach_score: 0.120
- phase_breakdown.contact_score: 0.076
- phase_breakdown.push_score: 0.011

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.085
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.134
- **Median Q (composite search score)**: 0.059
- **K-run variance**: 0.0005
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.356


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `1efc9b29f7d131941a1bd842274a029ca5b2a2ff6a8656033ab118e32e2fae7d`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `6150c547b3cd2920ed4582689733d59ef61d18dc295ccd2a0d2317d1cf4e7764`; realized-scene SHA-256: `79fe20ee7316d80bc617c84166fccacf882b4f96b2faf4b155be83e4f318b183`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51644,-0.02763,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.01644,-0.12237,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.51644,-0.02763,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.94444,"average_solve_count":72.0,"average_success_count":72.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.06577,"approach_1.approach_speed":0.01613,"contact_1.contact_force":6.40585,"contact_1.contact_speed":0.01366,"push_1.push_distance":0.09842,"push_1.push_force_limit":12.22516,"push_1.push_speed":0.02393,"retract_1.retract_height":0.11883,"retract_1.retract_speed":0.06007},"optimized_scores":{"best_composite_score":0.07523,"best_fitness_score":0.08523,"best_task_score":0.13402},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":225.0,"contact_point_centroid":[0.50699,0.00572,0.04559],"force_p95":197.51755,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":245.83168,"mean_force":125.53793,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50947,0.06493,0.13637]},{"body_a":"world","body_b":"push_box","contact_count":3052.0,"contact_point_centroid":[0.51673,-0.02492,-8e-05],"force_p95":85.57927,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":166.72458,"mean_force":9.62853,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4977,0.03394,0.20626]},{"body_a":"push_box","body_b":"link7","contact_count":36.0,"contact_point_centroid":[0.50347,-0.00702,0.06702],"force_p95":38.76569,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":63.15144,"mean_force":10.84068,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5042,0.07363,0.13017]},{"body_a":"push_box","body_b":"link6","contact_count":7.0,"contact_point_centroid":[0.51269,-0.01207,0.06739],"force_p95":61.2749,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":61.61538,"mean_force":53.66642,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50504,0.07335,0.12894]},{"body_a":"push_box","body_b":"link6","contact_count":19.0,"contact_point_centroid":[0.51202,-0.01183,0.06738],"force_p95":53.89347,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":54.10554,"mean_force":17.07008,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5045,0.07359,0.12892]},{"body_a":"world","body_b":"push_box","contact_count":2.0,"contact_point_centroid":[0.51846,-0.01209,-0.00022],"force_p95":43.44275,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":45.46342,"mean_force":25.25663,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50508,0.07331,0.12811]},{"body_a":"push_box","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.50508,0.02184,0.03203],"force_p95":39.67613,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":39.67613,"mean_force":39.67613,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50508,0.07331,0.12811]},{"body_a":"world","body_b":"push_box","contact_count":2188.0,"contact_point_centroid":[0.51626,-0.04108,-6e-05],"force_p95":0.51914,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":37.26161,"mean_force":0.40886,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50284,0.07364,0.18914]},{"body_a":"push_box","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.51267,-0.01234,0.06683],"force_p95":35.73038,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":35.73038,"mean_force":35.73038,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50508,0.07331,0.12811]},{"body_a":"world","body_b":"push_box","contact_count":2.0,"contact_point_centroid":[0.51845,-0.01202,-0.00022],"force_p95":20.9793,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.85881,"mean_force":13.06374,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50512,0.07329,0.12819]},{"body_a":"push_box","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.51272,-0.01237,0.06692],"force_p95":12.86342,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.86342,"mean_force":12.86342,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50512,0.07329,0.12819]},{"body_a":"push_box","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.50514,0.02183,0.03212],"force_p95":11.91784,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.91784,"mean_force":11.91784,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50512,0.07329,0.12819]}],"total_contact_groups":12},"final_pose_error":0.01153,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51643,-0.04434,0.02499],"final_tcp_position":[0.50314,0.0736,0.2355],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51644,-0.02763,0.025]},"peak_contact_force":245.83168,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":856.0,"n_steps_budget":1000.0,"object_pos_end":[0.51825,-0.01055,0.03489],"object_pos_start":[0.51644,-0.02763,0.025],"object_to_goal_dist_end":0.14099,"object_to_goal_dist_start":0.12347,"object_z_max":0.03519,"peak_contact_force":75.66655,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3284.0,"raw_peak_contact_force":245.83168,"subtask_id":"approach","tcp_end":[0.50512,0.07329,0.12819],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.12612,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":690.0,"object_pos_end":[0.51818,-0.01054,0.03488],"object_pos_start":[0.51825,-0.01055,0.03489],"object_to_goal_dist_end":0.14099,"object_to_goal_dist_start":0.14099,"object_z_max":0.03489,"peak_contact_force":21.85881,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":4.0,"raw_peak_contact_force":21.85881,"subtask_id":"contact","tcp_end":[0.50508,0.07331,0.12811],"tcp_start":[0.50512,0.07329,0.12819],"tcp_to_object_dist_end":0.12608,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.51811,-0.01052,0.03487],"object_pos_start":[0.51818,-0.01054,0.03488],"object_to_goal_dist_end":0.14099,"object_to_goal_dist_start":0.14099,"object_z_max":0.03488,"peak_contact_force":45.46342,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4.0,"raw_peak_contact_force":45.46342,"subtask_id":"push","tcp_end":[0.50504,0.07335,0.12803],"tcp_start":[0.50508,0.07331,0.12811],"tcp_to_object_dist_end":0.12603,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":663.0,"n_steps_budget":750.0,"object_pos_end":[0.51643,-0.04434,0.02499],"object_pos_start":[0.51811,-0.01052,0.03487],"object_to_goal_dist_end":0.10693,"object_to_goal_dist_start":0.14099,"object_z_max":0.03587,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2243.0,"raw_peak_contact_force":63.15144,"tcp_end":[0.50314,0.0736,0.2355],"tcp_start":[0.50504,0.07335,0.12803],"tcp_to_object_dist_end":0.24166,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `88c86884172a74f1f27b08fda534b767baf4d8d60d3fd4d782dec9555f4aae87`; realized-scene SHA-256: `258b33ff0697721ed1ba4810cf28d81707440dffd73b12c632f307c6591915c0`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50142,0.05406,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.00142,-0.20406,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.50142,0.05406,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.94366,"average_solve_count":71.0,"average_success_count":71.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.09744,"approach_1.approach_speed":0.05027,"contact_1.contact_force":1.42917,"contact_1.contact_speed":0.01651,"push_1.push_distance":0.11207,"push_1.push_force_limit":15.22693,"push_1.push_speed":0.03317,"retract_1.retract_height":0.10742,"retract_1.retract_speed":0.085},"optimized_scores":{"best_composite_score":0.0211,"best_fitness_score":0.0311,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":40.0,"contact_point_centroid":[0.49612,0.06534,0.04804],"force_p95":203.15407,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":218.21776,"mean_force":169.39454,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50014,0.12927,0.13517]},{"body_a":"world","body_b":"push_box","contact_count":3324.0,"contact_point_centroid":[0.50144,0.05407,-2e-05],"force_p95":0.24534,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":128.10329,"mean_force":2.29505,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49265,0.0655,0.22187]},{"body_a":"push_box","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.50137,0.06654,0.04687],"force_p95":104.65559,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":104.65559,"mean_force":104.65559,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50196,0.13079,0.13349]},{"body_a":"push_box","body_b":"link7","contact_count":37.0,"contact_point_centroid":[0.50088,0.06669,0.04876],"force_p95":58.93418,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":98.26312,"mean_force":14.77801,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50166,0.13092,0.13628]},{"body_a":"push_box","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.50143,0.06661,0.04689],"force_p95":90.21827,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":90.21827,"mean_force":90.21827,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50201,0.13084,0.1335]},{"body_a":"world","body_b":"push_box","contact_count":4.0,"contact_point_centroid":[0.50226,0.05458,-0.00048],"force_p95":66.28119,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":72.03521,"mean_force":26.42756,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50196,0.13079,0.13349]},{"body_a":"world","body_b":"push_box","contact_count":2313.0,"contact_point_centroid":[0.50136,0.05469,-3e-05],"force_p95":0.38166,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":55.2198,"mean_force":0.4907,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49985,0.13087,0.18278]},{"body_a":"world","body_b":"push_box","contact_count":4.0,"contact_point_centroid":[0.50226,0.05459,-0.00046],"force_p95":44.68557,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":48.89238,"mean_force":23.00971,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50201,0.13084,0.1335]}],"total_contact_groups":8},"final_pose_error":0.01139,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50204,0.05479,0.02499],"final_tcp_position":[0.50001,0.13087,0.22974],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50142,0.05406,0.025]},"peak_contact_force":218.21776,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":831.0,"n_steps_budget":1000.0,"object_pos_end":[0.50233,0.05512,0.02404],"object_pos_start":[0.50142,0.05406,0.025],"object_to_goal_dist_end":0.20514,"object_to_goal_dist_start":0.20406,"object_z_max":0.025,"peak_contact_force":201.71756,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3364.0,"raw_peak_contact_force":218.21776,"subtask_id":"approach","tcp_end":[0.50196,0.13079,0.13349],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.13305,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":750.0,"object_pos_end":[0.5023,0.05513,0.02407],"object_pos_start":[0.50233,0.05512,0.02404],"object_to_goal_dist_end":0.20515,"object_to_goal_dist_start":0.20514,"object_z_max":0.02404,"peak_contact_force":104.65559,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":5.0,"raw_peak_contact_force":104.65559,"subtask_id":"contact","tcp_end":[0.50201,0.13084,0.1335],"tcp_start":[0.50196,0.13079,0.13349],"tcp_to_object_dist_end":0.13306,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50227,0.05514,0.0241],"object_pos_start":[0.5023,0.05513,0.02407],"object_to_goal_dist_end":0.20515,"object_to_goal_dist_start":0.20515,"object_z_max":0.02407,"peak_contact_force":90.21827,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":5.0,"raw_peak_contact_force":90.21827,"subtask_id":"push","tcp_end":[0.50205,0.13088,0.13353],"tcp_start":[0.50201,0.13084,0.1335],"tcp_to_object_dist_end":0.13308,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":602.0,"n_steps_budget":690.0,"object_pos_end":[0.50204,0.05479,0.02499],"object_pos_start":[0.50227,0.05514,0.0241],"object_to_goal_dist_end":0.2048,"object_to_goal_dist_start":0.20515,"object_z_max":0.02548,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2350.0,"raw_peak_contact_force":98.26312,"tcp_end":[0.50001,0.13087,0.22974],"tcp_start":[0.50205,0.13088,0.13353],"tcp_to_object_dist_end":0.21844,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `a3cdbd735282928b0caf1de02aaaeed7f0a3d0a10908989412c558d20f3517fa`; realized-scene SHA-256: `8c36a5f9300ba3a57ccc09620ec8ba0a5276276ed83fb4303679e150911bfa14`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47139,-0.02418,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.02861,-0.12582,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.47139,-0.02418,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.83582,"average_solve_count":67.0,"average_success_count":67.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.06522,"approach_1.approach_speed":0.05543,"contact_1.contact_force":5.90609,"contact_1.contact_speed":0.07082,"push_1.push_distance":0.11725,"push_1.push_force_limit":15.0698,"push_1.push_speed":0.06189,"retract_1.retract_height":0.06558,"retract_1.retract_speed":0.0958},"optimized_scores":{"best_composite_score":0.0594,"best_fitness_score":0.0694,"best_task_score":0.09706},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":223.0,"contact_point_centroid":[0.46697,0.00942,0.04587],"force_p95":199.12369,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":242.79562,"mean_force":125.5169,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47146,0.06812,0.13684]},{"body_a":"world","body_b":"push_box","contact_count":2974.0,"contact_point_centroid":[0.47147,-0.02129,-8e-05],"force_p95":72.14249,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":175.00748,"mean_force":9.71526,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47921,0.03559,0.20584]},{"body_a":"push_box","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.47434,-0.00552,0.06856],"force_p95":67.21529,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":67.21529,"mean_force":67.21529,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46352,0.07659,0.12977]},{"body_a":"push_box","body_b":"link7","contact_count":36.0,"contact_point_centroid":[0.46299,-0.00546,0.06945],"force_p95":43.12569,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":49.14367,"mean_force":8.90456,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.46273,0.0767,0.13149]},{"body_a":"push_box","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.46659,-0.00823,0.06706],"force_p95":45.74023,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":45.74023,"mean_force":45.74023,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46352,0.07659,0.12977]},{"body_a":"push_box","body_b":"link6","contact_count":24.0,"contact_point_centroid":[0.4701,-0.00789,0.06851],"force_p95":38.80158,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":45.19538,"mean_force":11.92652,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4629,0.07668,0.13087]},{"body_a":"push_box","body_b":"link6","contact_count":2.0,"contact_point_centroid":[0.46669,-0.00808,0.06725],"force_p95":41.45805,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":41.89061,"mean_force":37.56498,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4636,0.07662,0.13009]},{"body_a":"world","body_b":"push_box","contact_count":2.0,"contact_point_centroid":[0.46911,-0.00804,-0.00027],"force_p95":33.59112,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":33.67356,"mean_force":32.84917,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46352,0.07659,0.12977]},{"body_a":"world","body_b":"push_box","contact_count":1162.0,"contact_point_centroid":[0.467,-0.02994,-0.00011],"force_p95":1.00628,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":28.86204,"mean_force":0.52579,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.46126,0.07689,0.16316]},{"body_a":"world","body_b":"push_box","contact_count":2.0,"contact_point_centroid":[0.46913,-0.00799,-0.00029],"force_p95":13.37992,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.98981,"mean_force":7.89093,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.46357,0.07659,0.12985]},{"body_a":"push_box","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.46292,0.02644,0.03282],"force_p95":7.57319,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.57319,"mean_force":7.57319,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.46357,0.07659,0.12985]},{"body_a":"push_box","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.46665,-0.00821,0.06712],"force_p95":7.37049,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.37049,"mean_force":7.37049,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.46357,0.07659,0.12985]}],"total_contact_groups":12},"final_pose_error":0.00996,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.46711,-0.03823,0.02499],"final_tcp_position":[0.46128,0.07689,0.18554],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":242.79562,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":838.0,"n_steps_budget":1000.0,"object_pos_end":[0.4691,-0.00649,0.03474],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.14712,"object_to_goal_dist_start":0.12903,"object_z_max":0.03499,"peak_contact_force":72.51016,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3199.0,"raw_peak_contact_force":242.79562,"subtask_id":"approach","tcp_end":[0.46357,0.07659,0.12985],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.1264,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":690.0,"object_pos_end":[0.46905,-0.00652,0.03478],"object_pos_start":[0.4691,-0.00649,0.03474],"object_to_goal_dist_end":0.1471,"object_to_goal_dist_start":0.14712,"object_z_max":0.03474,"peak_contact_force":13.98981,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":4.0,"raw_peak_contact_force":13.98981,"subtask_id":"contact","tcp_end":[0.46352,0.07659,0.12977],"tcp_start":[0.46357,0.07659,0.12985],"tcp_to_object_dist_end":0.12634,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.469,-0.00656,0.0348],"object_pos_start":[0.46905,-0.00652,0.03478],"object_to_goal_dist_end":0.14708,"object_to_goal_dist_start":0.1471,"object_z_max":0.03478,"peak_contact_force":67.21529,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4.0,"raw_peak_contact_force":67.21529,"subtask_id":"push","tcp_end":[0.46348,0.07659,0.12968],"tcp_start":[0.46352,0.07659,0.12977],"tcp_to_object_dist_end":0.12627,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":427.0,"n_steps_budget":600.0,"object_pos_end":[0.46711,-0.03823,0.02499],"object_pos_start":[0.469,-0.00656,0.0348],"object_to_goal_dist_end":0.11651,"object_to_goal_dist_start":0.14708,"object_z_max":0.03569,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1222.0,"raw_peak_contact_force":49.14367,"tcp_end":[0.46128,0.07689,0.18554],"tcp_start":[0.46348,0.07659,0.12968],"tcp_to_object_dist_end":0.19765,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```