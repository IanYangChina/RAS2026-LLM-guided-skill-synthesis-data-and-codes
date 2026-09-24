## Search State

- **Seed**: 5
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → contact → push → retract | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4690 | 0.74 | ❌ rejected |
| 8 | approach → contact → push → retract | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4711 | 0.75 | ❌ rejected |
| 7 | approach → contact → push → retract | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | -0.0435 | 0.02 | ❌ rejected |
| 6 | approach → contact → push → retract | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4737 | 0.75 | ❌ rejected |
| 5 | approach → contact → push → retract | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | -0.2041 | 0.00 | ❌ rejected |

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

## Current Skill (Q=0.469) — your mutation base

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

- **Composite score**: 0.469
- **task_score** (E): 0.744
- **fitness_score**: 0.679  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.210

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2855 |
| contact_1 | 1.00 | 1.00 | 0.0536 |
| push_1 | 1.00 | 1.00 | 0.1255 |
| retract_1 | 0.00 | 1.00 | 0.1656 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.514, 0.101, 0.036) | (0.519, 0.022, 0.025)→(0.519, 0.022, 0.025) | 0.173→0.173 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / step_budget | (0.514, 0.101, 0.036)→(0.514, 0.050, 0.020) | (0.519, 0.022, 0.025)→(0.521, 0.013, 0.025) | 0.173→0.165 | 1.00 / 4.000 | 2.879 | 11.153 |
| push_1 | push | 1.00 / step_budget | (0.514, 0.050, 0.020)→(0.501, -0.075, 0.024) | (0.521, 0.013, 0.025)→(0.514, -0.109, 0.028) | 0.165→0.048 | 1.00 / 3.000 | 55.989 | 96.379 |
| retract_1 | retract | 0.00 / step_budget | (0.501, -0.075, 0.024)→(0.497, 0.071, 0.102) | (0.514, -0.109, 0.028)→(0.511, -0.107, 0.025) | 0.048→0.049 | 1.00 / 4.000 | 0.245 | 54.005 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.425
- goal_progress: 0.954
- terminal_score: 0.954
- phase_score: 0.845
- phase_breakdown.contact_score: 0.871
- phase_breakdown.push_score: 0.840
- phase_breakdown.approach_score: 0.820

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.889
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.954
- **Median Q (composite search score)**: 0.370
- **K-run variance**: 0.0220
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.357


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.74051,"average_solve_count":158.0,"average_success_count":158.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.speed":0.04052,"push_1.push_depth":0.09983,"retract_1.retract_height":0.05803},"optimized_scores":{"best_composite_score":0.35888,"best_fitness_score":0.56888,"best_task_score":0.61873},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":797.0,"contact_point_centroid":[0.54976,-0.01137,0.05471],"force_p95":115.50352,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":131.47717,"mean_force":75.87615,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51805,0.00433,0.02363]},{"body_a":"attachment","body_b":"push_box","contact_count":803.0,"contact_point_centroid":[0.53691,-0.00397,0.05225],"force_p95":101.1157,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":110.05108,"mean_force":55.4433,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51815,0.00479,0.02361]},{"body_a":"world","body_b":"push_box","contact_count":1507.0,"contact_point_centroid":[0.54481,-0.04744,-0.00032],"force_p95":79.19197,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":97.27242,"mean_force":52.11058,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51766,0.00191,0.02393]},{"body_a":"push_box","body_b":"link7","contact_count":44.0,"contact_point_centroid":[0.54945,-0.0614,0.05576],"force_p95":83.85575,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":92.54813,"mean_force":39.6486,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50683,-0.05189,0.03029]},{"body_a":"attachment","body_b":"push_box","contact_count":66.0,"contact_point_centroid":[0.52792,-0.05434,0.05948],"force_p95":63.19391,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":83.57647,"mean_force":21.49455,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50594,-0.04814,0.03149]},{"body_a":"world","body_b":"push_box","contact_count":3671.0,"contact_point_centroid":[0.52566,-0.08181,-3e-05],"force_p95":0.43031,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":82.19133,"mean_force":0.49277,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50095,0.02435,0.07117]},{"body_a":"attachment","body_b":"push_box","contact_count":148.0,"contact_point_centroid":[0.53734,0.05751,0.0367],"force_p95":7.81332,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.43166,"mean_force":3.50198,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53129,0.06944,0.0212]},{"body_a":"world","body_b":"push_box","contact_count":2767.0,"contact_point_centroid":[0.53664,0.03513,-1e-05],"force_p95":2.11386,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.3522,"mean_force":0.43871,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52896,0.09107,0.02609]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51292,0.07216,0.17685]}],"total_contact_groups":9},"final_pose_error":0.07247,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52502,-0.08181,0.02499],"final_tcp_position":[0.49872,0.08972,0.10979],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":131.47717,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.53035,0.11538,0.03637],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07949,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":771.0,"n_steps_budget":870.0,"object_pos_end":[0.53913,0.02786,0.02492],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.18211,"object_to_goal_dist_start":0.1905,"object_z_max":0.0251,"peak_contact_force":5.96807,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2915.0,"raw_peak_contact_force":10.43166,"tcp_end":[0.53188,0.06465,0.0202],"tcp_start":[0.53035,0.11538,0.03637],"tcp_to_object_dist_end":0.0378,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":807.0,"n_steps_budget":900.0,"object_pos_end":[0.53351,-0.08397,0.03139],"object_pos_start":[0.53913,0.02786,0.02492],"object_to_goal_dist_end":0.07433,"object_to_goal_dist_start":0.18211,"object_z_max":0.03138,"peak_contact_force":113.57947,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3107.0,"raw_peak_contact_force":131.47717,"tcp_end":[0.50769,-0.05509,0.02904],"tcp_start":[0.53188,0.06465,0.0202],"tcp_to_object_dist_end":0.03881,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52502,-0.08181,0.02499],"object_pos_start":[0.53351,-0.08397,0.03139],"object_to_goal_dist_end":0.07263,"object_to_goal_dist_start":0.07433,"object_z_max":0.03494,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3781.0,"raw_peak_contact_force":92.54813,"tcp_end":[0.49872,0.08972,0.10979],"tcp_start":[0.50769,-0.05509,0.02904],"tcp_to_object_dist_end":0.19315,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.71338,"average_solve_count":157.0,"average_success_count":157.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.speed":0.03601,"push_1.push_depth":0.09905,"retract_1.retract_height":0.13915},"optimized_scores":{"best_composite_score":0.67863,"best_fitness_score":0.88863,"best_task_score":0.95353},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1125.0,"contact_point_centroid":[0.5075,-0.10531,-0.00013],"force_p95":58.42223,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":75.46715,"mean_force":20.14826,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49794,-0.05347,0.01976]},{"body_a":"push_box","body_b":"link7","contact_count":471.0,"contact_point_centroid":[0.52563,-0.0501,0.05218],"force_p95":44.20713,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":56.40318,"mean_force":29.60464,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49898,-0.02834,0.01999]},{"body_a":"attachment","body_b":"push_box","contact_count":728.0,"contact_point_centroid":[0.51108,-0.0635,0.04283],"force_p95":49.52908,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":55.39362,"mean_force":20.38313,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49798,-0.05217,0.01975]},{"body_a":"push_box","body_b":"link7","contact_count":41.0,"contact_point_centroid":[0.52516,-0.13923,0.0503],"force_p95":7.94523,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.30848,"mean_force":5.12411,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49397,-0.11381,0.02043]},{"body_a":"world","body_b":"push_box","contact_count":3859.0,"contact_point_centroid":[0.50097,-0.1554,-2e-05],"force_p95":0.26566,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.492,"mean_force":0.31004,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49324,-0.03956,0.0536]},{"body_a":"attachment","body_b":"push_box","contact_count":157.0,"contact_point_centroid":[0.50613,0.0018,0.03416],"force_p95":7.61387,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.56481,"mean_force":3.15585,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49974,0.01367,0.0213]},{"body_a":"world","body_b":"push_box","contact_count":3186.0,"contact_point_centroid":[0.50475,-0.02033,-1e-05],"force_p95":1.6729,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.41783,"mean_force":0.40463,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49817,0.03656,0.02515]},{"body_a":"push_box","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.53169,-0.00312,0.0501],"force_p95":3.26284,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.83086,"mean_force":1.20425,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50011,0.00938,0.02064]},{"body_a":"world","body_b":"push_box","contact_count":3580.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4992,0.04658,0.17199]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.51009,-0.13128,0.05007],"force_p95":0.0,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49583,-0.11939,0.01977]}],"total_contact_groups":10},"final_pose_error":0.13278,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50105,-0.15601,0.02499],"final_tcp_position":[0.49447,0.03247,0.08846],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":75.46715,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":895.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3580.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.50029,0.06252,0.03384],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08192,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":877.0,"n_steps_budget":990.0,"object_pos_end":[0.50705,-0.02777,0.02502],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.12243,"object_to_goal_dist_start":0.13127,"object_z_max":0.02507,"peak_contact_force":1.63947,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3348.0,"raw_peak_contact_force":10.56481,"tcp_end":[0.50013,0.00902,0.02058],"tcp_start":[0.50029,0.06252,0.03384],"tcp_to_object_dist_end":0.0377,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":778.0,"n_steps_budget":870.0,"object_pos_end":[0.50055,-0.15637,0.02504],"object_pos_start":[0.50705,-0.02777,0.02502],"object_to_goal_dist_end":0.00639,"object_to_goal_dist_start":0.12243,"object_z_max":0.02803,"peak_contact_force":0.14727,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2324.0,"raw_peak_contact_force":75.46715,"tcp_end":[0.49583,-0.11939,0.01977],"tcp_start":[0.50013,0.00902,0.02058],"tcp_to_object_dist_end":0.03765,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50105,-0.15601,0.02499],"object_pos_start":[0.50055,-0.15637,0.02504],"object_to_goal_dist_end":0.0061,"object_to_goal_dist_start":0.00639,"object_z_max":0.02767,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3901.0,"raw_peak_contact_force":19.30848,"tcp_end":[0.49447,0.03247,0.08846],"tcp_start":[0.49583,-0.11939,0.01977],"tcp_to_object_dist_end":0.19899,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.76471,"average_solve_count":153.0,"average_success_count":153.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.speed":0.04584,"push_1.push_depth":0.09999,"retract_1.retract_height":0.10241},"optimized_scores":{"best_composite_score":0.36959,"best_fitness_score":0.57959,"best_task_score":0.65977},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1375.0,"contact_point_centroid":[0.52351,-0.0436,-0.00014],"force_p95":60.41844,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":82.19323,"mean_force":35.91115,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50492,0.01042,0.02203]},{"body_a":"push_box","body_b":"link7","contact_count":768.0,"contact_point_centroid":[0.53188,-0.00429,0.05442],"force_p95":58.85696,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":69.76047,"mean_force":48.02544,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.505,0.0132,0.02184]},{"body_a":"attachment","body_b":"push_box","contact_count":776.0,"contact_point_centroid":[0.52246,0.00365,0.04935],"force_p95":60.27622,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":63.99562,"mean_force":40.96308,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50506,0.01384,0.02183]},{"body_a":"push_box","body_b":"link7","contact_count":13.0,"contact_point_centroid":[0.52892,-0.0736,0.05477],"force_p95":48.9639,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":50.15977,"mean_force":24.39312,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50007,-0.04926,0.02356]},{"body_a":"attachment","body_b":"push_box","contact_count":36.0,"contact_point_centroid":[0.52,-0.0566,0.05614],"force_p95":38.83379,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":43.30485,"mean_force":7.51321,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49913,-0.04637,0.02427]},{"body_a":"world","body_b":"push_box","contact_count":3844.0,"contact_point_centroid":[0.50625,-0.08321,-2e-05],"force_p95":0.2457,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":28.89595,"mean_force":0.28789,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49651,0.02441,0.06576]},{"body_a":"attachment","body_b":"push_box","contact_count":120.0,"contact_point_centroid":[0.51656,0.06849,0.03614],"force_p95":7.48044,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.46167,"mean_force":2.9432,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50996,0.08033,0.02166]},{"body_a":"world","body_b":"push_box","contact_count":2352.0,"contact_point_centroid":[0.5152,0.04612,-1e-05],"force_p95":1.65642,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.77995,"mean_force":0.40194,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50825,0.10195,0.02677]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50358,0.07681,0.17794]}],"total_contact_groups":9},"final_pose_error":0.07271,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50601,-0.08282,0.02499],"final_tcp_position":[0.49661,0.09082,0.10789],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":82.19323,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.51015,0.12542,0.03668],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07878,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":660.0,"n_steps_budget":750.0,"object_pos_end":[0.51706,0.03872,0.02494],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.18949,"object_to_goal_dist_start":0.19823,"object_z_max":0.02511,"peak_contact_force":1.02954,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2472.0,"raw_peak_contact_force":12.46167,"tcp_end":[0.51039,0.07559,0.02061],"tcp_start":[0.51015,0.12542,0.03668],"tcp_to_object_dist_end":0.03772,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":778.0,"n_steps_budget":870.0,"object_pos_end":[0.50828,-0.08682,0.02897],"object_pos_start":[0.51706,0.03872,0.02494],"object_to_goal_dist_end":0.06385,"object_to_goal_dist_start":0.18949,"object_z_max":0.02948,"peak_contact_force":54.24027,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2919.0,"raw_peak_contact_force":82.19323,"tcp_end":[0.50044,-0.04963,0.02342],"tcp_start":[0.51039,0.07559,0.02061],"tcp_to_object_dist_end":0.0384,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50601,-0.08282,0.02499],"object_pos_start":[0.50828,-0.08682,0.02897],"object_to_goal_dist_end":0.06745,"object_to_goal_dist_start":0.06385,"object_z_max":0.02905,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3893.0,"raw_peak_contact_force":50.15977,"tcp_end":[0.49661,0.09082,0.10789],"tcp_start":[0.50044,-0.04963,0.02342],"tcp_to_object_dist_end":0.19265,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```