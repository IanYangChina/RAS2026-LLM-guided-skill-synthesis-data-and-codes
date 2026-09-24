## Search State

- **Seed**: 5
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → contact → push → retract | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | -0.0435 | 0.02 | ❌ rejected |
| 6 | approach → contact → push → retract | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4737 | 0.75 | ❌ rejected |
| 5 | approach → contact → push → retract | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | -0.2041 | 0.00 | ❌ rejected |
| 4 | approach → contact → push → retract | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4746 | 0.75 | ❌ rejected |
| 3 | approach → contact → push → retract | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4751 | 0.76 | ✅ accepted |

**Proposal policy**: task_score is 0.02 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `b2a76c5d1121259d09d3db2c62740fd8fe93dd873d8f379ba1928ff319a7d266`
- Frozen object start: [0.5366003508494456, 0.03695289476837925, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.5366003508494456, 0.03695289476837925, 0.025)
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
  frozen_object_start: [0.5366, 0.037, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.5366003508494456, 0.03695289476837925, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [-0.0366, -0.187, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: b2a76c5d1121259d09d3db2c62740fd8fe93dd873d8f379ba1928ff319a7d266

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

## Current Skill (Q=-0.044) — your mutation base

```yaml
skill: push_to_goal
phases:
- id: approach_1
  type: approach
  generator: arc_cartesian
  control: force_threshold_switch
  termination: pose_tolerance
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
  generator: impedance_motion
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
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.2

```

## Design Metrics

- **Composite score**: -0.044
- **task_score** (E): 0.017
- **fitness_score**: 0.166  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.210

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2313 |
| contact_1 | 1.00 | 1.00 | 0.0681 |
| push_1 | 0.00 | 1.00 | 0.0067 |
| retract_1 | 1.00 | 1.00 | 0.1443 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.515, 0.099, 0.094) | (0.519, 0.022, 0.025)→(0.519, 0.022, 0.025) | 0.173→0.173 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / step_budget | (0.515, 0.099, 0.094)→(0.514, 0.063, 0.036) | (0.519, 0.022, 0.025)→(0.519, 0.020, 0.025) | 0.173→0.172 | 1.00 / 3.667 | 0.164 | 2.385 |
| push_1 | push | 0.00 / guard_failure | (0.514, 0.063, 0.036)→(0.512, 0.057, 0.034) | (0.519, 0.020, 0.025)→(0.519, 0.020, 0.025) | 0.172→0.171 | 1.00 / 1.667 | 0.241 | 35.509 |
| retract_1 | retract | 1.00 / step_budget | (0.512, 0.057, 0.034)→(0.509, 0.056, 0.178) | (0.519, 0.020, 0.025)→(0.517, 0.019, 0.025) | 0.171→0.170 | 1.00 / 4.000 | 0.245 | 2.239 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.042
- lateral_force_integral: None
- approach_alignment: 0.241
- goal_progress: 0.042
- terminal_score: 0.042
- phase_score: 0.313
- phase_breakdown.contact_score: 0.847
- phase_breakdown.push_score: 0.017
- phase_breakdown.approach_score: 0.253

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.205
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.042
- **Median Q (composite search score)**: -0.053
- **K-run variance**: 0.0008
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.307


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `7ff7a4e3a1b03e3d7ba3d0b298d1ee8847b5344eb55f2aa0aaf582e7a98ab8ac`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `028a6956ebe09ab7c7952341570355f52da12e46fb22d3462091c70c024324ff`; realized-scene SHA-256: `b2a76c5d1121259d09d3db2c62740fd8fe93dd873d8f379ba1928ff319a7d266`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5366,0.03695,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.0366,-0.18695,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5366,0.03695,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.0117,"average_solve_count":171.0,"average_success_count":171.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.speed":0.01075,"push_1.push_depth":0.01016,"retract_1.retract_height":0.1534},"optimized_scores":{"best_composite_score":-0.07204,"best_fitness_score":0.13796,"best_task_score":0.00373},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.52763,0.06188,0.04152],"force_p95":33.60171,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":33.60171,"mean_force":33.60171,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52762,0.0738,0.0415]},{"body_a":"world","body_b":"push_box","contact_count":108.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.81704,"mean_force":0.55161,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52925,0.07908,0.04301]},{"body_a":"world","body_b":"push_box","contact_count":1576.0,"contact_point_centroid":[0.5353,0.03565,-2e-05],"force_p95":0.43677,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.82349,"mean_force":0.26514,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.52439,0.0728,0.11129]},{"body_a":"attachment","body_b":"push_box","contact_count":19.0,"contact_point_centroid":[0.52661,0.06058,0.04421],"force_p95":2.20284,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.48835,"mean_force":0.93329,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.52618,0.07234,0.04415]},{"body_a":"world","body_b":"push_box","contact_count":1944.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51837,0.06508,0.20574]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53008,0.09158,0.05808]}],"total_contact_groups":6},"final_pose_error":0.01998,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.5349,0.03655,0.02499],"final_tcp_position":[0.52473,0.07296,0.17503],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":33.60171,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":486.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1944.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.53212,0.11213,0.09369],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.10193,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.53071,0.08266,0.04435],"tcp_start":[0.53212,0.11213,0.09369],"tcp_to_object_dist_end":0.04999,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":27.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03691,0.02501],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.19046,"object_to_goal_dist_start":0.1905,"object_z_max":0.02499,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":109.0,"raw_peak_contact_force":33.60171,"subtask_id":"push","tcp_end":[0.52752,0.0734,0.0414],"tcp_start":[0.53071,0.08266,0.04435],"tcp_to_object_dist_end":0.04101,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":424.0,"n_steps_budget":960.0,"object_pos_end":[0.5349,0.03655,0.02499],"object_pos_start":[0.5366,0.03691,0.02501],"object_to_goal_dist_end":0.18979,"object_to_goal_dist_start":0.19046,"object_z_max":0.02604,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1595.0,"raw_peak_contact_force":2.82349,"tcp_end":[0.52473,0.07296,0.17503],"tcp_start":[0.52752,0.0734,0.0414],"tcp_to_object_dist_end":0.15473,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1c6409cc6d884b90ecc3937d36e5ea87cc4ef513b6f301a9da66b4e84390f805`; realized-scene SHA-256: `5f9daa62d5a7a2b8a7116f2dfbb5f9857bb0d5d4b297d304a4e76a9a270e7ec7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50458,-0.01881,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.00458,-0.13119,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.50458,-0.01881,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.96067,"average_solve_count":178.0,"average_success_count":178.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.speed":0.01859,"push_1.push_depth":0.10867,"retract_1.retract_height":0.17077},"optimized_scores":{"best_composite_score":-0.05312,"best_fitness_score":0.15688,"best_task_score":0.00552},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.49784,0.0061,0.03841],"force_p95":37.67334,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.67334,"mean_force":37.67334,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4978,0.018,0.03836]},{"body_a":"world","body_b":"push_box","contact_count":100.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.90021,"mean_force":0.61531,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49859,0.02277,0.03954]},{"body_a":"attachment","body_b":"push_box","contact_count":21.0,"contact_point_centroid":[0.49753,0.00492,0.04311],"force_p95":2.15405,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.56741,"mean_force":0.88478,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49633,0.01663,0.04175]},{"body_a":"world","body_b":"push_box","contact_count":1736.0,"contact_point_centroid":[0.50224,-0.02059,-2e-05],"force_p95":0.31889,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.41549,"mean_force":0.26102,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49474,0.01731,0.11685]},{"body_a":"world","body_b":"push_box","contact_count":1716.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4998,0.04133,0.20237]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49876,0.03779,0.05699]}],"total_contact_groups":6},"final_pose_error":0.0198,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50215,-0.01947,0.02499],"final_tcp_position":[0.49515,0.01744,0.18941],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":37.67334,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":429.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1716.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.50097,0.06194,0.09429],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.10647,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.49932,0.02595,0.0406],"tcp_start":[0.50097,0.06194,0.09429],"tcp_to_object_dist_end":0.0477,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":25.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01885,0.02502],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.13123,"object_to_goal_dist_start":0.13127,"object_z_max":0.02499,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":101.0,"raw_peak_contact_force":37.67334,"subtask_id":"push","tcp_end":[0.49775,0.01758,0.03828],"tcp_start":[0.49932,0.02595,0.0406],"tcp_to_object_dist_end":0.03937,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":461.0,"n_steps_budget":1000.0,"object_pos_end":[0.50215,-0.01947,0.02499],"object_pos_start":[0.50458,-0.01885,0.02502],"object_to_goal_dist_end":0.13055,"object_to_goal_dist_start":0.13123,"object_z_max":0.02601,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1757.0,"raw_peak_contact_force":2.56741,"tcp_end":[0.49515,0.01744,0.18941],"tcp_start":[0.49775,0.01758,0.03828],"tcp_to_object_dist_end":0.16866,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `f52ec1899e2888770a8b6b3ae605718303ef4b10e72cfd7d20ce53303721b2b0`; realized-scene SHA-256: `c8d09cd43835becf8e5eb4413394fad8627e4bf404e9e7726e9f380b60e09752`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51501,0.04767,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.01501,-0.19767,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.51501,0.04767,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.83886,"average_solve_count":211.0,"average_success_count":211.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.speed":0.02248,"push_1.push_depth":0.03525,"retract_1.retract_height":0.1678},"optimized_scores":{"best_composite_score":-0.00544,"best_fitness_score":0.20456,"best_task_score":0.04189},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":4.0,"contact_point_centroid":[0.51654,0.06736,0.03642],"force_p95":31.54566,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":35.25337,"mean_force":13.98997,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51041,0.07923,0.02296]},{"body_a":"world","body_b":"push_box","contact_count":16.0,"contact_point_centroid":[0.5156,0.03611,-2e-05],"force_p95":17.60965,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.55364,"mean_force":3.73422,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51041,0.07924,0.02296]},{"body_a":"attachment","body_b":"push_box","contact_count":370.0,"contact_point_centroid":[0.51291,0.07001,0.03234],"force_p95":5.70996,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.6631,"mean_force":3.82632,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.5104,0.08195,0.02699]},{"body_a":"world","body_b":"push_box","contact_count":3679.0,"contact_point_centroid":[0.51498,0.04524,-1e-05],"force_p95":1.99158,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.13079,"mean_force":0.62121,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50958,0.09513,0.04769]},{"body_a":"world","body_b":"push_box","contact_count":1781.0,"contact_point_centroid":[0.51554,0.03905,-2e-05],"force_p95":0.24558,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.32521,"mean_force":0.25149,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50693,0.07794,0.09746]},{"body_a":"attachment","body_b":"push_box","contact_count":5.0,"contact_point_centroid":[0.52225,0.06653,0.05002],"force_p95":0.54376,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.55345,"mean_force":0.37762,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50988,0.07819,0.0226]},{"body_a":"world","body_b":"push_box","contact_count":1964.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50625,0.07067,0.20564]}],"total_contact_groups":7},"final_pose_error":0.0199,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.5154,0.03931,0.02499],"final_tcp_position":[0.50731,0.07808,0.17081],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":35.25337,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":491.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1964.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.51134,0.12225,0.09344],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.1013,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51552,0.04259,0.025],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.19322,"object_to_goal_dist_start":0.19823,"object_z_max":0.02501,"peak_contact_force":6e-05,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":4049.0,"raw_peak_contact_force":6.6631,"subtask_id":"contact","tcp_end":[0.51061,0.07949,0.02314],"tcp_start":[0.51134,0.12225,0.09344],"tcp_to_object_dist_end":0.03727,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":7.0,"n_steps_budget":1000.0,"object_pos_end":[0.51545,0.04172,0.0251],"object_pos_start":[0.51552,0.04259,0.025],"object_to_goal_dist_end":0.19234,"object_to_goal_dist_start":0.19322,"object_z_max":0.02501,"peak_contact_force":0.72182,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":20.0,"raw_peak_contact_force":35.25337,"subtask_id":"push","tcp_end":[0.51007,0.07855,0.0227],"tcp_start":[0.51061,0.07949,0.02314],"tcp_to_object_dist_end":0.03729,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":458.0,"n_steps_budget":1000.0,"object_pos_end":[0.5154,0.03931,0.02499],"object_pos_start":[0.51545,0.04172,0.0251],"object_to_goal_dist_end":0.18993,"object_to_goal_dist_start":0.19234,"object_z_max":0.02527,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1786.0,"raw_peak_contact_force":1.32521,"tcp_end":[0.50731,0.07808,0.17081],"tcp_start":[0.51007,0.07855,0.0227],"tcp_to_object_dist_end":0.1511,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```