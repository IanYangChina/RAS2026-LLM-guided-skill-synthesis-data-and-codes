## Search State

- **Seed**: 5
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 5 | -0.0569 | 0.03 | ❌ rejected |
| 10 | approach → contact → push → retract | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4729 | 0.75 | ❌ rejected |
| 9 | approach → contact → push → retract | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4690 | 0.74 | ❌ rejected |
| 8 | approach → contact → push → retract | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4711 | 0.75 | ❌ rejected |
| 7 | approach → contact → push → retract | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | -0.0435 | 0.02 | ❌ rejected |

**Proposal policy**: task_score is 0.03 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.057) — your mutation base

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

- **Composite score**: -0.057
- **task_score** (E): 0.031
- **fitness_score**: 0.253  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.310

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2777 |
| contact_1 | 1.00 | 1.00 | 0.0521 |
| push_1 | 0.00 | 1.00 | 0.0001 |
| retract_1 | 1.00 | 1.00 | 0.1279 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.514, 0.101, 0.044) | (0.519, 0.022, 0.025)→(0.519, 0.022, 0.025) | 0.173→0.173 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / step_budget | (0.514, 0.101, 0.044)→(0.514, 0.054, 0.021) | (0.519, 0.022, 0.025)→(0.520, 0.017, 0.025) | 0.173→0.169 | 1.00 / 3.000 | 5.854 | 8.581 |
| push_1 | push | 0.00 / guard_failure | (0.514, 0.054, 0.021)→(0.514, 0.054, 0.021) | (0.520, 0.017, 0.025)→(0.520, 0.017, 0.025) | 0.169→0.169 | 1.00 / 3.333 | 1.601 | 12.936 |
| retract_1 | retract | 1.00 / step_budget | (0.514, 0.054, 0.021)→(0.511, 0.054, 0.149) | (0.520, 0.017, 0.025)→(0.520, 0.017, 0.025) | 0.169→0.168 | 1.00 / 4.000 | 0.245 | 3.011 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.041
- lateral_force_integral: None
- approach_alignment: 0.474
- goal_progress: 0.039
- terminal_score: 0.039
- phase_score: 0.416
- phase_breakdown.contact_score: 0.830
- phase_breakdown.push_score: 0.063
- phase_breakdown.approach_score: 0.676

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.265
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.039
- **Median Q (composite search score)**: -0.063
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.257


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.59542,"average_solve_count":131.0,"average_success_count":131.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.0587,"contact_1.speed":0.01556,"push_1.push_depth":0.11674,"push_1.speed":0.02103,"retract_1.retract_height":0.19216},"optimized_scores":{"best_composite_score":-0.06322,"best_fitness_score":0.24678,"best_task_score":0.02645},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.53627,0.05696,0.0389],"force_p95":15.07503,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.77918,"mean_force":8.76278,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53204,0.06882,0.0205]},{"body_a":"world","body_b":"push_box","contact_count":8.0,"contact_point_centroid":[0.55083,0.02615,-4e-05],"force_p95":7.95332,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.06583,"mean_force":3.53299,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53204,0.06882,0.0205]},{"body_a":"attachment","body_b":"push_box","contact_count":108.0,"contact_point_centroid":[0.53394,0.05961,0.0312],"force_p95":7.20288,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.80124,"mean_force":3.67746,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53166,0.07154,0.02158]},{"body_a":"world","body_b":"push_box","contact_count":3562.0,"contact_point_centroid":[0.53675,0.03624,-1e-05],"force_p95":1.30967,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.72925,"mean_force":0.35683,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52905,0.09121,0.02935]},{"body_a":"world","body_b":"push_box","contact_count":2104.0,"contact_point_centroid":[0.53754,0.03088,-1e-05],"force_p95":0.34482,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.56023,"mean_force":0.25281,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.52876,0.06833,0.1085]},{"body_a":"attachment","body_b":"push_box","contact_count":25.0,"contact_point_centroid":[0.53443,0.05658,0.04992],"force_p95":2.93887,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.1971,"mean_force":0.98414,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.52959,0.06846,0.03067]},{"body_a":"world","body_b":"push_box","contact_count":2276.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51312,0.07069,0.1802]}],"total_contact_groups":7},"final_pose_error":0.01971,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53747,0.03164,0.02499],"final_tcp_position":[0.52929,0.06839,0.19303],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":16.0,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":569.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2276.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.52999,0.11458,0.04329],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08003,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":934.0,"n_steps_budget":1000.0,"object_pos_end":[0.53824,0.0321,0.02492],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.18607,"object_to_goal_dist_start":0.1905,"object_z_max":0.02506,"peak_contact_force":16.0,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3670.0,"raw_peak_contact_force":7.80124,"subtask_id":"contact","tcp_end":[0.53205,0.06883,0.02053],"tcp_start":[0.52999,0.11458,0.04329],"tcp_to_object_dist_end":0.03751,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.53824,0.03207,0.02494],"object_pos_start":[0.53824,0.0321,0.02492],"object_to_goal_dist_end":0.18604,"object_to_goal_dist_start":0.18607,"object_z_max":0.02498,"peak_contact_force":1.77149,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":11.0,"raw_peak_contact_force":15.77918,"subtask_id":"push","tcp_end":[0.53197,0.06879,0.0204],"tcp_start":[0.53201,0.0688,0.02046],"tcp_to_object_dist_end":0.03753,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":546.0,"n_steps_budget":1000.0,"object_pos_end":[0.53747,0.03164,0.02499],"object_pos_start":[0.53822,0.03202,0.02499],"object_to_goal_dist_end":0.18546,"object_to_goal_dist_start":0.18599,"object_z_max":0.02523,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2129.0,"raw_peak_contact_force":4.56023,"tcp_end":[0.52929,0.06839,0.19303],"tcp_start":[0.53197,0.06879,0.0204],"tcp_to_object_dist_end":0.17221,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.30275,"average_solve_count":109.0,"average_success_count":109.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.06189,"contact_1.speed":0.01572,"push_1.push_depth":0.06519,"push_1.speed":0.02269,"retract_1.retract_height":0.05034},"optimized_scores":{"best_composite_score":-0.04489,"best_fitness_score":0.26511,"best_task_score":0.03927},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":97.0,"contact_point_centroid":[0.50311,0.004,0.03492],"force_p95":8.44206,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.78421,"mean_force":3.89304,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50021,0.01594,0.02208]},{"body_a":"world","body_b":"push_box","contact_count":3747.0,"contact_point_centroid":[0.50475,-0.01947,-1e-05],"force_p95":0.68424,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.5502,"mean_force":0.34702,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49879,0.03774,0.03029]},{"body_a":"world","body_b":"push_box","contact_count":6.0,"contact_point_centroid":[0.50636,-0.03994,-2e-05],"force_p95":2.59916,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.63111,"mean_force":1.68439,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50034,0.01351,0.0211]},{"body_a":"attachment","body_b":"push_box","contact_count":5.0,"contact_point_centroid":[0.50556,0.00161,0.04429],"force_p95":2.17725,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.21495,"mean_force":1.663,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50036,0.01352,0.02112]},{"body_a":"world","body_b":"push_box","contact_count":419.0,"contact_point_centroid":[0.50564,-0.02395,-2e-05],"force_p95":0.26519,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.1797,"mean_force":0.25275,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49779,0.01329,0.0351]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.50667,0.00149,0.04997],"force_p95":1.55705,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.55705,"mean_force":1.55705,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5002,0.01343,0.02092]},{"body_a":"world","body_b":"push_box","contact_count":2068.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49985,0.04551,0.17719]}],"total_contact_groups":7},"final_pose_error":0.02,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50593,-0.02402,0.02499],"final_tcp_position":[0.49699,0.01328,0.05152],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":9.78421,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":517.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2068.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.5009,0.06331,0.04412],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.0844,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":978.0,"n_steps_budget":1000.0,"object_pos_end":[0.50603,-0.0232,0.02508],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.12694,"object_to_goal_dist_start":0.13127,"object_z_max":0.02509,"peak_contact_force":1.56041,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3844.0,"raw_peak_contact_force":9.78421,"subtask_id":"contact","tcp_end":[0.50043,0.01359,0.02122],"tcp_start":[0.5009,0.06331,0.04412],"tcp_to_object_dist_end":0.03741,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":5.0,"n_steps_budget":900.0,"object_pos_end":[0.50598,-0.02335,0.02502],"object_pos_start":[0.50603,-0.0232,0.02508],"object_to_goal_dist_end":0.12679,"object_to_goal_dist_start":0.12694,"object_z_max":0.02508,"peak_contact_force":2.63111,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":11.0,"raw_peak_contact_force":2.63111,"subtask_id":"push","tcp_end":[0.5002,0.01343,0.02092],"tcp_start":[0.50026,0.01346,0.021],"tcp_to_object_dist_end":0.03746,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":106.0,"n_steps_budget":600.0,"object_pos_end":[0.50593,-0.02402,0.02499],"object_pos_start":[0.50596,-0.02352,0.02497],"object_to_goal_dist_end":0.12612,"object_to_goal_dist_start":0.12662,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":420.0,"raw_peak_contact_force":2.1797,"tcp_end":[0.49699,0.01328,0.05152],"tcp_start":[0.5002,0.01343,0.02092],"tcp_to_object_dist_end":0.04664,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.59091,"average_solve_count":132.0,"average_success_count":132.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.05965,"contact_1.speed":0.01598,"push_1.push_depth":0.10676,"push_1.speed":0.02598,"retract_1.retract_height":0.19992},"optimized_scores":{"best_composite_score":-0.06263,"best_fitness_score":0.24737,"best_task_score":0.02849},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":5.0,"contact_point_centroid":[0.51584,0.06764,0.04415],"force_p95":19.34246,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.3975,"mean_force":7.69884,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51064,0.07953,0.02093]},{"body_a":"world","body_b":"push_box","contact_count":18.0,"contact_point_centroid":[0.51901,0.04261,-3e-05],"force_p95":9.94374,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.3114,"mean_force":2.37011,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51059,0.07949,0.02087]},{"body_a":"attachment","body_b":"push_box","contact_count":109.0,"contact_point_centroid":[0.5112,0.07026,0.02507],"force_p95":7.59634,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.15875,"mean_force":3.85456,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.51043,0.08222,0.02209]},{"body_a":"world","body_b":"push_box","contact_count":3323.0,"contact_point_centroid":[0.51522,0.0472,-1e-05],"force_p95":1.58084,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.20431,"mean_force":0.36895,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50871,0.10105,0.02989]},{"body_a":"attachment","body_b":"push_box","contact_count":7.0,"contact_point_centroid":[0.50955,0.067,0.02743],"force_p95":2.08705,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.29165,"mean_force":1.36608,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5085,0.07897,0.02413]},{"body_a":"world","body_b":"push_box","contact_count":2155.0,"contact_point_centroid":[0.51571,0.04137,-1e-05],"force_p95":0.2462,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.56913,"mean_force":0.25087,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50736,0.07884,0.1121]},{"body_a":"world","body_b":"push_box","contact_count":2280.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50404,0.07546,0.1809]}],"total_contact_groups":7},"final_pose_error":0.01971,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51581,0.04194,0.02499],"final_tcp_position":[0.50788,0.07892,0.20103],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":20.3975,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":570.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2280.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.51044,0.1244,0.04392],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07917,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":864.0,"n_steps_budget":990.0,"object_pos_end":[0.51626,0.04271,0.02499],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.1934,"object_to_goal_dist_start":0.19823,"object_z_max":0.02502,"peak_contact_force":9e-05,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3432.0,"raw_peak_contact_force":8.15875,"subtask_id":"contact","tcp_end":[0.51071,0.07961,0.02103],"tcp_start":[0.51044,0.1244,0.04392],"tcp_to_object_dist_end":0.03752,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":6.0,"n_steps_budget":1000.0,"object_pos_end":[0.51622,0.04252,0.02494],"object_pos_start":[0.51626,0.04271,0.02499],"object_to_goal_dist_end":0.1932,"object_to_goal_dist_start":0.1934,"object_z_max":0.025,"peak_contact_force":0.39938,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":23.0,"raw_peak_contact_force":20.3975,"subtask_id":"push","tcp_end":[0.51041,0.07936,0.02066],"tcp_start":[0.51047,0.07939,0.02074],"tcp_to_object_dist_end":0.03753,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":554.0,"n_steps_budget":1000.0,"object_pos_end":[0.51581,0.04194,0.02499],"object_pos_start":[0.5162,0.0424,0.02493],"object_to_goal_dist_end":0.19259,"object_to_goal_dist_start":0.19308,"object_z_max":0.02507,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2162.0,"raw_peak_contact_force":2.29165,"tcp_end":[0.50788,0.07892,0.20103],"tcp_start":[0.51041,0.07936,0.02066],"tcp_to_object_dist_end":0.18006,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```