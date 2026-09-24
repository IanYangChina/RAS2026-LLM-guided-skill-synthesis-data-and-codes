## Search State

- **Seed**: 5
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | approach → contact → push → retract | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 4 | 0.3766 | 0.71 | ❌ rejected |
| 0 | approach → contact → push → retract | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4708 | 0.75 | ✅ accepted |

**Proposal policy**: task_score is 0.71 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.377) — your mutation base

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

- **Composite score**: 0.377
- **task_score** (E): 0.706
- **fitness_score**: 0.637  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.260

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2020 |
| contact_1 | 1.00 | 1.00 | 0.1174 |
| push_1 | 0.00 | 1.00 | 0.1809 |
| retract_1 | 1.00 | 1.00 | 0.1251 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.516, 0.105, 0.131) | (0.519, 0.022, 0.025)→(0.519, 0.022, 0.025) | 0.173→0.173 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / step_budget | (0.516, 0.105, 0.131)→(0.515, 0.055, 0.025) | (0.519, 0.022, 0.025)→(0.519, 0.018, 0.025) | 0.173→0.169 | 1.00 / 4.000 | 10.937 | 18.396 |
| push_1 | push | 0.00 / step_budget | (0.515, 0.055, 0.025)→(0.495, -0.125, 0.021) | (0.519, 0.018, 0.025)→(0.539, -0.129, 0.028) | 0.169→0.053 | 1.00 / 3.333 | 15.499 | 43.295 |
| retract_1 | retract | 1.00 / step_budget | (0.495, -0.125, 0.021)→(0.492, -0.124, 0.146) | (0.539, -0.129, 0.028)→(0.536, -0.130, 0.025) | 0.053→0.051 | 1.00 / 4.000 | 0.245 | 16.355 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.849
- lateral_force_integral: None
- approach_alignment: 0.752
- goal_progress: 0.778
- terminal_score: 0.778
- phase_score: 0.592
- phase_breakdown.contact_score: 0.839
- phase_breakdown.push_score: 0.635
- phase_breakdown.approach_score: 0.113

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.666
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.778
- **Median Q (composite search score)**: 0.383
- **K-run variance**: 0.0007
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.277


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.05809,"average_solve_count":241.0,"average_success_count":241.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.arc_height":0.06407,"contact_1.speed":0.01789,"push_1.push_depth":0.14493,"retract_1.retract_height":0.17325},"optimized_scores":{"best_composite_score":0.38328,"best_fitness_score":0.64328,"best_task_score":0.63546},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":487.0,"contact_point_centroid":[0.54744,-0.03388,0.05486],"force_p95":34.48468,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":38.60346,"mean_force":22.68184,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51085,-0.03137,0.02159]},{"body_a":"world","body_b":"push_box","contact_count":1867.0,"contact_point_centroid":[0.55153,-0.06832,-5e-05],"force_p95":26.2902,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":31.43785,"mean_force":8.78522,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50854,-0.04191,0.02106]},{"body_a":"attachment","body_b":"push_box","contact_count":741.0,"contact_point_centroid":[0.52806,-0.02043,0.04883],"force_p95":18.9492,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":25.5914,"mean_force":8.95386,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51404,-0.01323,0.02132]},{"body_a":"attachment","body_b":"push_box","contact_count":77.0,"contact_point_centroid":[0.53294,0.05997,0.0317],"force_p95":17.49276,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.77307,"mean_force":11.72283,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53243,0.07193,0.02982]},{"body_a":"world","body_b":"push_box","contact_count":3194.0,"contact_point_centroid":[0.53646,0.03668,-1e-05],"force_p95":3.36798,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.83892,"mean_force":0.52539,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53208,0.09428,0.0761]},{"body_a":"world","body_b":"push_box","contact_count":3608.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52313,0.08058,0.24742]},{"body_a":"world","body_b":"push_box","contact_count":3972.0,"contact_point_centroid":[0.54393,-0.09621,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4916,-0.11178,0.10028]}],"total_contact_groups":7},"final_pose_error":0.01185,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.54393,-0.09621,0.02499],"final_tcp_position":[0.49206,-0.11182,0.18195],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":38.60346,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":902.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3608.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.53487,0.12092,0.13369],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.13736,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":816.0,"n_steps_budget":1000.0,"object_pos_end":[0.53663,0.03297,0.02499],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.1866,"object_to_goal_dist_start":0.1905,"object_z_max":0.02503,"peak_contact_force":0.3529,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3271.0,"raw_peak_contact_force":17.77307,"subtask_id":"contact","tcp_end":[0.53256,0.06986,0.02512],"tcp_start":[0.53487,0.12092,0.13369],"tcp_to_object_dist_end":0.03711,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54393,-0.09621,0.02499],"object_pos_start":[0.53663,0.03297,0.02499],"object_to_goal_dist_end":0.06945,"object_to_goal_dist_start":0.1866,"object_z_max":0.02941,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3095.0,"raw_peak_contact_force":38.60346,"subtask_id":"push","tcp_end":[0.49489,-0.11238,0.0202],"tcp_start":[0.53256,0.06986,0.02512],"tcp_to_object_dist_end":0.05186,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":993.0,"n_steps_budget":1000.0,"object_pos_end":[0.54393,-0.09621,0.02499],"object_pos_start":[0.54393,-0.09621,0.02499],"object_to_goal_dist_end":0.06945,"object_to_goal_dist_start":0.06945,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3972.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.49206,-0.11182,0.18195],"tcp_start":[0.49489,-0.11238,0.0202],"tcp_to_object_dist_end":0.16605,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.30846,"average_solve_count":201.0,"average_success_count":201.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.arc_height":0.09883,"contact_1.speed":0.02436,"push_1.push_depth":0.11725,"retract_1.retract_height":0.12181},"optimized_scores":{"best_composite_score":0.34033,"best_fitness_score":0.60033,"best_task_score":0.70487},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":613.0,"contact_point_centroid":[0.53242,-0.10921,0.05489],"force_p95":39.66934,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":53.50998,"mean_force":27.79766,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49575,-0.10719,0.02156]},{"body_a":"world","body_b":"push_box","contact_count":1571.0,"contact_point_centroid":[0.53641,-0.1221,-7e-05],"force_p95":31.95308,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":46.94138,"mean_force":15.41743,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49603,-0.08276,0.02147]},{"body_a":"attachment","body_b":"push_box","contact_count":899.0,"contact_point_centroid":[0.50964,-0.08638,0.04854],"force_p95":22.83472,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":36.75094,"mean_force":11.67229,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49601,-0.07924,0.02139]},{"body_a":"push_box","body_b":"link7","contact_count":6.0,"contact_point_centroid":[0.53287,-0.16252,0.05416],"force_p95":23.7349,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":25.24336,"mean_force":13.77114,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49438,-0.15848,0.02134]},{"body_a":"attachment","body_b":"push_box","contact_count":81.0,"contact_point_centroid":[0.50922,-0.15705,0.05387],"force_p95":6.35128,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.46091,"mean_force":1.38191,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49188,-0.15776,0.03158]},{"body_a":"attachment","body_b":"push_box","contact_count":64.0,"contact_point_centroid":[0.50099,0.00435,0.0313],"force_p95":16.22058,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.72028,"mean_force":10.17236,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50041,0.01631,0.02883]},{"body_a":"world","body_b":"push_box","contact_count":2477.0,"contact_point_centroid":[0.53384,-0.17315,-1e-05],"force_p95":0.44182,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.10999,"mean_force":0.2794,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49114,-0.15739,0.0808]},{"body_a":"world","body_b":"push_box","contact_count":3477.0,"contact_point_centroid":[0.50447,-0.01916,-1e-05],"force_p95":0.69319,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.71961,"mean_force":0.43222,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49931,0.04122,0.0724]},{"body_a":"world","body_b":"push_box","contact_count":3624.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49922,0.07825,0.23684]}],"total_contact_groups":9},"final_pose_error":0.01201,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53094,-0.17332,0.02499],"final_tcp_position":[0.49142,-0.15744,0.13159],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":53.50998,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":906.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3624.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.50115,0.07032,0.12609],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.13482,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":890.0,"n_steps_budget":1000.0,"object_pos_end":[0.50496,-0.02263,0.02495],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.12746,"object_to_goal_dist_start":0.13127,"object_z_max":0.02502,"peak_contact_force":16.0,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3541.0,"raw_peak_contact_force":16.72028,"subtask_id":"contact","tcp_end":[0.50061,0.0142,0.0249],"tcp_start":[0.50115,0.07032,0.12609],"tcp_to_object_dist_end":0.03709,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5357,-0.17271,0.02878],"object_pos_start":[0.50496,-0.02263,0.02495],"object_to_goal_dist_end":0.04248,"object_to_goal_dist_start":0.12746,"object_z_max":0.0295,"peak_contact_force":26.35166,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3083.0,"raw_peak_contact_force":53.50998,"subtask_id":"push","tcp_end":[0.49461,-0.15833,0.02132],"tcp_start":[0.50061,0.0142,0.0249],"tcp_to_object_dist_end":0.04417,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":693.0,"n_steps_budget":780.0,"object_pos_end":[0.53094,-0.17332,0.02499],"object_pos_start":[0.5357,-0.17271,0.02878],"object_to_goal_dist_end":0.03874,"object_to_goal_dist_start":0.04248,"object_z_max":0.02878,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2564.0,"raw_peak_contact_force":25.24336,"tcp_end":[0.49142,-0.15744,0.13159],"tcp_start":[0.49461,-0.15833,0.02132],"tcp_to_object_dist_end":0.11479,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.62025,"average_solve_count":158.0,"average_success_count":158.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.arc_height":0.0312,"contact_1.speed":0.04998,"push_1.push_depth":0.11785,"retract_1.retract_height":0.1146},"optimized_scores":{"best_composite_score":0.40631,"best_fitness_score":0.66631,"best_task_score":0.77778},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":428.0,"contact_point_centroid":[0.53571,-0.06626,0.05519],"force_p95":31.24609,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.77163,"mean_force":20.30278,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49866,-0.06628,0.02204]},{"body_a":"world","body_b":"push_box","contact_count":1417.0,"contact_point_centroid":[0.53635,-0.06531,-6e-05],"force_p95":26.06448,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":32.03016,"mean_force":10.44943,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50116,-0.02349,0.02198]},{"body_a":"attachment","body_b":"push_box","contact_count":872.0,"contact_point_centroid":[0.5131,-0.02768,0.04612],"force_p95":21.6462,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":30.22829,"mean_force":7.96513,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50133,-0.01943,0.0219]},{"body_a":"push_box","body_b":"link7","contact_count":6.0,"contact_point_centroid":[0.53445,-0.10705,0.05448],"force_p95":22.64253,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.57513,"mean_force":11.42404,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49595,-0.10309,0.02173]},{"body_a":"attachment","body_b":"push_box","contact_count":52.0,"contact_point_centroid":[0.51113,0.07054,0.0328],"force_p95":20.56712,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.6933,"mean_force":14.8191,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.51076,0.08249,0.03177]},{"body_a":"world","body_b":"push_box","contact_count":2269.0,"contact_point_centroid":[0.53485,-0.11972,-1e-05],"force_p95":0.44698,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.87114,"mean_force":0.28152,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49271,-0.10231,0.07735]},{"body_a":"attachment","body_b":"push_box","contact_count":72.0,"contact_point_centroid":[0.51108,-0.10245,0.05386],"force_p95":4.03855,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.39222,"mean_force":1.24148,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49357,-0.10264,0.03109]},{"body_a":"world","body_b":"push_box","contact_count":2797.0,"contact_point_centroid":[0.51497,0.04738,-1e-05],"force_p95":2.90521,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.78337,"mean_force":0.5196,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50978,0.10203,0.07787]},{"body_a":"world","body_b":"push_box","contact_count":3068.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50629,0.07292,0.2307]}],"total_contact_groups":9},"final_pose_error":0.01192,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53202,-0.11975,0.02499],"final_tcp_position":[0.49294,-0.10231,0.12485],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":37.77163,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":767.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3068.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.51166,0.12486,0.13381],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.13346,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":715.0,"n_steps_budget":1000.0,"object_pos_end":[0.5154,0.04363,0.02483],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.19425,"object_to_goal_dist_start":0.19823,"object_z_max":0.02505,"peak_contact_force":16.4588,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2849.0,"raw_peak_contact_force":20.6933,"subtask_id":"contact","tcp_end":[0.511,0.08038,0.0262],"tcp_start":[0.51166,0.12486,0.13381],"tcp_to_object_dist_end":0.03703,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53672,-0.11919,0.02897],"object_pos_start":[0.5154,0.04363,0.02483],"object_to_goal_dist_end":0.0481,"object_to_goal_dist_start":0.19425,"object_z_max":0.02963,"peak_contact_force":19.89895,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2717.0,"raw_peak_contact_force":37.77163,"subtask_id":"push","tcp_end":[0.49619,-0.10288,0.02171],"tcp_start":[0.511,0.08038,0.0262],"tcp_to_object_dist_end":0.04429,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":633.0,"n_steps_budget":720.0,"object_pos_end":[0.53202,-0.11975,0.02499],"object_pos_start":[0.53672,-0.11919,0.02897],"object_to_goal_dist_end":0.04405,"object_to_goal_dist_start":0.0481,"object_z_max":0.02897,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2347.0,"raw_peak_contact_force":23.57513,"tcp_end":[0.49294,-0.10231,0.12485],"tcp_start":[0.49619,-0.10288,0.02171],"tcp_to_object_dist_end":0.10865,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```