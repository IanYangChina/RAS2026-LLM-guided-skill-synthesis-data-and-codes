## Search State

- **Seed**: 5
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → contact → push → retract | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | 0.0309 | 0.44 | ❌ rejected |
| 11 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 5 | -0.0569 | 0.03 | ❌ rejected |
| 10 | approach → contact → push → retract | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4729 | 0.75 | ❌ rejected |
| 9 | approach → contact → push → retract | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4690 | 0.74 | ❌ rejected |
| 8 | approach → contact → push → retract | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4711 | 0.75 | ❌ rejected |

**Proposal policy**: task_score is 0.44 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.031) — your mutation base

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

- **Composite score**: 0.031
- **task_score** (E): 0.440
- **fitness_score**: 0.391  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2312 |
| contact_1 | 1.00 | 1.00 | 0.0814 |
| push_1 | 0.00 | 1.00 | 0.0734 |
| retract_1 | 1.00 | 1.00 | 0.1252 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.515, 0.099, 0.094) | (0.519, 0.022, 0.025)→(0.519, 0.022, 0.025) | 0.173→0.173 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / step_budget | (0.515, 0.099, 0.094)→(0.514, 0.055, 0.025) | (0.519, 0.022, 0.025)→(0.520, 0.018, 0.025) | 0.173→0.170 | 1.00 / 4.000 | 7.086 | 12.933 |
| push_1 | push | 0.00 / guard_failure | (0.514, 0.055, 0.025)→(0.505, -0.017, 0.020) | (0.520, 0.018, 0.025)→(0.519, -0.052, 0.026) | 0.170→0.101 | 1.00 / 2.667 | 25.916 | 36.288 |
| retract_1 | retract | 1.00 / step_budget | (0.505, -0.017, 0.020)→(0.502, -0.017, 0.146) | (0.519, -0.052, 0.026)→(0.520, -0.055, 0.025) | 0.101→0.097 | 1.00 / 4.000 | 0.245 | 26.635 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.443
- lateral_force_integral: None
- approach_alignment: 0.637
- goal_progress: 0.443
- terminal_score: 0.443
- phase_score: 0.390
- phase_breakdown.contact_score: 0.841
- phase_breakdown.push_score: 0.176
- phase_breakdown.approach_score: 0.249

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.411
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.474
- **Median Q (composite search score)**: 0.041
- **K-run variance**: 0.0005
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.229


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.01036,"average_solve_count":193.0,"average_success_count":193.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.10898,"contact_1.speed":0.02158,"push_1.push_depth":0.05402,"push_1.speed":0.04269,"retract_1.retract_height":0.08878,"retract_1.speed":0.06764},"optimized_scores":{"best_composite_score":0.0005,"best_fitness_score":0.3605,"best_task_score":0.40227},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":5.0,"contact_point_centroid":[0.52547,-0.01499,0.05119],"force_p95":40.09524,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":49.57095,"mean_force":10.88921,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5167,-0.00344,0.02185]},{"body_a":"attachment","body_b":"push_box","contact_count":101.0,"contact_point_centroid":[0.52858,0.02582,0.03694],"force_p95":7.42663,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.48774,"mean_force":2.94344,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.524,0.03753,0.02355]},{"body_a":"world","body_b":"push_box","contact_count":842.0,"contact_point_centroid":[0.53393,-0.04222,-4e-05],"force_p95":0.41267,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":30.50271,"mean_force":0.33385,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51376,-0.0032,0.05779]},{"body_a":"world","body_b":"push_box","contact_count":138.0,"contact_point_centroid":[0.5381,-0.0052,-5e-05],"force_p95":7.35666,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":26.06366,"mean_force":2.71791,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52574,0.04552,0.02434]},{"body_a":"attachment","body_b":"push_box","contact_count":111.0,"contact_point_centroid":[0.53188,0.06098,0.02934],"force_p95":5.88976,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.14565,"mean_force":4.33207,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53181,0.07296,0.02931]},{"body_a":"world","body_b":"push_box","contact_count":3920.0,"contact_point_centroid":[0.53659,0.03659,-1e-05],"force_p95":1.38881,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.49388,"mean_force":0.36444,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53078,0.08597,0.04958]},{"body_a":"world","body_b":"push_box","contact_count":1932.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51848,0.0651,0.20569]}],"total_contact_groups":7},"final_pose_error":0.01999,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53385,-0.04128,0.02499],"final_tcp_position":[0.51351,-0.00293,0.09096],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":49.57095,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":483.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1932.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.53227,0.11213,0.09366],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.10191,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53699,0.03491,0.02495],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.18857,"object_to_goal_dist_start":0.1905,"object_z_max":0.02501,"peak_contact_force":0.00026,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":4031.0,"raw_peak_contact_force":7.14565,"subtask_id":"contact","tcp_end":[0.53197,0.07184,0.02744],"tcp_start":[0.53227,0.11213,0.09366],"tcp_to_object_dist_end":0.03735,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":158.0,"n_steps_budget":1000.0,"object_pos_end":[0.53203,-0.03762,0.02547],"object_pos_start":[0.53699,0.03491,0.02495],"object_to_goal_dist_end":0.11685,"object_to_goal_dist_start":0.18857,"object_z_max":0.02652,"peak_contact_force":40.48774,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":239.0,"raw_peak_contact_force":40.48774,"subtask_id":"push","tcp_end":[0.51685,-0.00286,0.02188],"tcp_start":[0.53197,0.07184,0.02744],"tcp_to_object_dist_end":0.0381,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":227.0,"n_steps_budget":840.0,"object_pos_end":[0.53385,-0.04128,0.02499],"object_pos_start":[0.53203,-0.03762,0.02547],"object_to_goal_dist_end":0.11387,"object_to_goal_dist_start":0.11685,"object_z_max":0.02602,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":847.0,"raw_peak_contact_force":49.57095,"tcp_end":[0.51351,-0.00293,0.09096],"tcp_start":[0.51685,-0.00286,0.02188],"tcp_to_object_dist_end":0.07897,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.24365,"average_solve_count":197.0,"average_success_count":197.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.09839,"contact_1.speed":0.02694,"push_1.push_depth":0.07412,"push_1.speed":0.03269,"retract_1.retract_height":0.16642,"retract_1.speed":0.08109},"optimized_scores":{"best_composite_score":0.05126,"best_fitness_score":0.41126,"best_task_score":0.44303},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":69.0,"contact_point_centroid":[0.50213,-0.02216,0.03429],"force_p95":9.18956,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":35.67478,"mean_force":3.24377,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49798,-0.01033,0.02074]},{"body_a":"attachment","body_b":"push_box","contact_count":5.0,"contact_point_centroid":[0.50133,-0.05062,0.0435],"force_p95":22.07991,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":27.35473,"mean_force":6.12603,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4951,-0.03882,0.02511]},{"body_a":"world","body_b":"push_box","contact_count":97.0,"contact_point_centroid":[0.51159,-0.05991,-7e-05],"force_p95":7.87737,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.40127,"mean_force":2.86881,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49847,-0.00478,0.02122]},{"body_a":"world","body_b":"push_box","contact_count":1738.0,"contact_point_centroid":[0.50237,-0.07761,-2e-05],"force_p95":0.26371,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.60846,"mean_force":0.27234,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49333,-0.03828,0.0943]},{"body_a":"attachment","body_b":"push_box","contact_count":87.0,"contact_point_centroid":[0.50259,0.00413,0.03687],"force_p95":12.92036,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.00779,"mean_force":7.99998,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50034,0.01608,0.02685]},{"body_a":"world","body_b":"push_box","contact_count":3082.0,"contact_point_centroid":[0.50472,-0.01934,-1e-05],"force_p95":2.41578,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.57879,"mean_force":0.47108,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49923,0.03609,0.05486]},{"body_a":"world","body_b":"push_box","contact_count":1712.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49991,0.04133,0.20233]}],"total_contact_groups":7},"final_pose_error":0.01996,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50222,-0.07692,0.02499],"final_tcp_position":[0.49358,-0.03815,0.16615],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":35.67478,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":428.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1712.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.50119,0.06195,0.09437],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.10653,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":799.0,"n_steps_budget":1000.0,"object_pos_end":[0.50596,-0.02324,0.0248],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.1269,"object_to_goal_dist_start":0.13127,"object_z_max":0.02506,"peak_contact_force":8.91696,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3169.0,"raw_peak_contact_force":14.00779,"subtask_id":"contact","tcp_end":[0.50055,0.01367,0.02337],"tcp_start":[0.50119,0.06195,0.09437],"tcp_to_object_dist_end":0.03733,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":116.0,"n_steps_budget":1000.0,"object_pos_end":[0.50273,-0.0749,0.02566],"object_pos_start":[0.50596,-0.02324,0.0248],"object_to_goal_dist_end":0.07515,"object_to_goal_dist_start":0.1269,"object_z_max":0.02652,"peak_contact_force":35.67478,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":166.0,"raw_peak_contact_force":35.67478,"subtask_id":"push","tcp_end":[0.49643,-0.03831,0.01949],"tcp_start":[0.50055,0.01367,0.02337],"tcp_to_object_dist_end":0.03764,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":450.0,"n_steps_budget":1000.0,"object_pos_end":[0.50222,-0.07692,0.02499],"object_pos_start":[0.50273,-0.0749,0.02566],"object_to_goal_dist_end":0.07311,"object_to_goal_dist_start":0.07515,"object_z_max":0.02615,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1743.0,"raw_peak_contact_force":27.35473,"tcp_end":[0.49358,-0.03815,0.16615],"tcp_start":[0.49643,-0.03831,0.01949],"tcp_to_object_dist_end":0.14664,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.32212,"average_solve_count":208.0,"average_success_count":208.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.10913,"contact_1.speed":0.03047,"push_1.push_depth":0.07459,"push_1.speed":0.03928,"retract_1.retract_height":0.17918,"retract_1.speed":0.06302},"optimized_scores":{"best_composite_score":0.04096,"best_fitness_score":0.40096,"best_task_score":0.47396},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":140.0,"contact_point_centroid":[0.51186,0.02331,0.03964],"force_p95":7.51297,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":32.70273,"mean_force":2.16576,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50553,0.0348,0.02089]},{"body_a":"world","body_b":"push_box","contact_count":128.0,"contact_point_centroid":[0.52362,-0.02003,-0.0001],"force_p95":9.56929,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.22751,"mean_force":3.14608,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5059,0.03845,0.02111]},{"body_a":"attachment","body_b":"push_box","contact_count":62.0,"contact_point_centroid":[0.51198,0.07072,0.03365],"force_p95":16.34779,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.64636,"mean_force":10.87487,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.51066,0.08265,0.0282]},{"body_a":"push_box","body_b":"link7","contact_count":7.0,"contact_point_centroid":[0.53944,-0.0125,0.0529],"force_p95":9.53063,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.52763,"mean_force":2.15293,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50257,-0.00542,0.01997]},{"body_a":"world","body_b":"push_box","contact_count":2264.0,"contact_point_centroid":[0.51523,0.04727,-1e-05],"force_p95":3.10185,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.0322,"mean_force":0.54235,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50954,0.10057,0.05663]},{"body_a":"world","body_b":"push_box","contact_count":1987.0,"contact_point_centroid":[0.52316,-0.04828,-3e-05],"force_p95":0.28735,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.97917,"mean_force":0.25918,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49921,-0.01069,0.10136]},{"body_a":"push_box","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.53962,-0.0176,0.05275],"force_p95":2.25447,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.34538,"mean_force":1.01626,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50194,-0.01154,0.01997]},{"body_a":"world","body_b":"push_box","contact_count":1952.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50634,0.0706,0.20579]}],"total_contact_groups":8},"final_pose_error":0.01979,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52283,-0.04825,0.02499],"final_tcp_position":[0.49949,-0.01058,0.17955],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":32.70273,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":488.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1952.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.51152,0.12218,0.09386],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.10153,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":586.0,"n_steps_budget":1000.0,"object_pos_end":[0.51611,0.04371,0.02494],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.19438,"object_to_goal_dist_start":0.19823,"object_z_max":0.02506,"peak_contact_force":12.34153,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2326.0,"raw_peak_contact_force":17.64636,"subtask_id":"contact","tcp_end":[0.51088,0.08043,0.0245],"tcp_start":[0.51152,0.12218,0.09386],"tcp_to_object_dist_end":0.03709,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":190.0,"n_steps_budget":1000.0,"object_pos_end":[0.52366,-0.04302,0.02621],"object_pos_start":[0.51611,0.04371,0.02494],"object_to_goal_dist_end":0.10957,"object_to_goal_dist_start":0.19438,"object_z_max":0.02705,"peak_contact_force":1.58578,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":275.0,"raw_peak_contact_force":32.70273,"subtask_id":"push","tcp_end":[0.50227,-0.01058,0.01997],"tcp_start":[0.51088,0.08043,0.0245],"tcp_to_object_dist_end":0.03936,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":514.0,"n_steps_budget":1000.0,"object_pos_end":[0.52283,-0.04825,0.02499],"object_pos_start":[0.52366,-0.04302,0.02621],"object_to_goal_dist_end":0.10428,"object_to_goal_dist_start":0.10957,"object_z_max":0.02676,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1992.0,"raw_peak_contact_force":2.97917,"tcp_end":[0.49949,-0.01058,0.17955],"tcp_start":[0.50227,-0.01058,0.01997],"tcp_to_object_dist_end":0.16079,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```