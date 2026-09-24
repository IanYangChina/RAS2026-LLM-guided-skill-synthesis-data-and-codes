## Search State

- **Seed**: 5
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → contact → push → retract | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4746 | 0.75 | ❌ rejected |
| 3 | approach → contact → push → retract | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4751 | 0.76 | ✅ accepted |
| 2 | approach → contact → push → retract | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4735 | 0.75 | ✅ accepted |
| 1 | approach → contact → push → retract | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 4 | 0.3766 | 0.71 | ❌ rejected |
| 0 | approach → contact → push → retract | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4708 | 0.75 | ✅ accepted |

**Proposal policy**: task_score is 0.75 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.475) — your mutation base

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

- **Composite score**: 0.475
- **task_score** (E): 0.751
- **fitness_score**: 0.685  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.210

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2855 |
| contact_1 | 1.00 | 1.00 | 0.0539 |
| push_1 | 1.00 | 1.00 | 0.1269 |
| retract_1 | 0.00 | 1.00 | 0.1645 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.514, 0.101, 0.036) | (0.519, 0.022, 0.025)→(0.519, 0.022, 0.025) | 0.173→0.173 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / step_budget | (0.514, 0.101, 0.036)→(0.514, 0.049, 0.020) | (0.519, 0.022, 0.025)→(0.521, 0.013, 0.025) | 0.173→0.164 | 1.00 / 3.000 | 3.201 | 9.037 |
| push_1 | push | 1.00 / step_budget | (0.514, 0.049, 0.020)→(0.501, -0.076, 0.023) | (0.521, 0.013, 0.025)→(0.511, -0.111, 0.028) | 0.164→0.047 | 1.00 / 3.000 | 38.706 | 94.024 |
| retract_1 | retract | 0.00 / step_budget | (0.501, -0.076, 0.023)→(0.496, 0.069, 0.101) | (0.511, -0.111, 0.028)→(0.507, -0.110, 0.025) | 0.047→0.047 | 1.00 / 4.000 | 0.245 | 27.194 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.431
- goal_progress: 0.936
- terminal_score: 0.936
- phase_score: 0.850
- phase_breakdown.contact_score: 0.871
- phase_breakdown.push_score: 0.849
- phase_breakdown.approach_score: 0.820

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.884
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.936
- **Median Q (composite search score)**: 0.389
- **K-run variance**: 0.0201
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.399


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.71341,"average_solve_count":164.0,"average_success_count":164.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.speed":0.03324,"push_1.push_depth":0.09972,"retract_1.retract_height":0.09688},"optimized_scores":{"best_composite_score":0.36099,"best_fitness_score":0.57099,"best_task_score":0.61995},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":799.0,"contact_point_centroid":[0.55064,-0.0117,0.05452],"force_p95":115.39993,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":129.44357,"mean_force":77.36084,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51826,0.00402,0.0237]},{"body_a":"attachment","body_b":"push_box","contact_count":798.0,"contact_point_centroid":[0.53737,-0.00469,0.05282],"force_p95":99.9339,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":108.66977,"mean_force":55.59623,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51827,0.00399,0.02371]},{"body_a":"world","body_b":"push_box","contact_count":1508.0,"contact_point_centroid":[0.54588,-0.04773,-0.00032],"force_p95":80.64578,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":92.97818,"mean_force":52.91775,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51785,0.00145,0.02401]},{"body_a":"push_box","body_b":"link7","contact_count":44.0,"contact_point_centroid":[0.54968,-0.06127,0.05595],"force_p95":74.77081,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":79.50303,"mean_force":36.75874,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50711,-0.05282,0.03044]},{"body_a":"attachment","body_b":"push_box","contact_count":66.0,"contact_point_centroid":[0.52776,-0.05524,0.0586],"force_p95":56.36409,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":61.29722,"mean_force":19.19146,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50625,-0.04918,0.0316]},{"body_a":"world","body_b":"push_box","contact_count":3664.0,"contact_point_centroid":[0.52646,-0.08231,-3e-05],"force_p95":0.47235,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":57.08097,"mean_force":0.48513,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50119,0.02374,0.07132]},{"body_a":"attachment","body_b":"push_box","contact_count":193.0,"contact_point_centroid":[0.53875,0.05723,0.04009],"force_p95":6.70078,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.95889,"mean_force":3.16073,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53133,0.06916,0.02115]},{"body_a":"world","body_b":"push_box","contact_count":3306.0,"contact_point_centroid":[0.53672,0.03474,-1e-05],"force_p95":2.03758,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.4479,"mean_force":0.43721,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52895,0.09079,0.02598]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51292,0.07216,0.17685]}],"total_contact_groups":9},"final_pose_error":0.07283,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52576,-0.08234,0.02499],"final_tcp_position":[0.49884,0.08929,0.10978],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":129.44357,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.53035,0.11538,0.03637],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07949,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":934.0,"n_steps_budget":1000.0,"object_pos_end":[0.53953,0.02721,0.02503],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.18157,"object_to_goal_dist_start":0.1905,"object_z_max":0.02516,"peak_contact_force":1.54792,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3499.0,"raw_peak_contact_force":8.95889,"tcp_end":[0.5319,0.06407,0.02005],"tcp_start":[0.53035,0.11538,0.03637],"tcp_to_object_dist_end":0.03797,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":808.0,"n_steps_budget":900.0,"object_pos_end":[0.53466,-0.08436,0.03136],"object_pos_start":[0.53953,0.02721,0.02503],"object_to_goal_dist_end":0.07451,"object_to_goal_dist_start":0.18157,"object_z_max":0.03144,"peak_contact_force":113.3438,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3105.0,"raw_peak_contact_force":129.44357,"tcp_end":[0.50808,-0.05602,0.02933],"tcp_start":[0.5319,0.06407,0.02005],"tcp_to_object_dist_end":0.0389,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52576,-0.08234,0.02499],"object_pos_start":[0.53466,-0.08436,0.03136],"object_to_goal_dist_end":0.0724,"object_to_goal_dist_start":0.07451,"object_z_max":0.03491,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3774.0,"raw_peak_contact_force":79.50303,"tcp_end":[0.49884,0.08929,0.10978],"tcp_start":[0.50808,-0.05602,0.02933],"tcp_to_object_dist_end":0.19332,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.69136,"average_solve_count":162.0,"average_success_count":162.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.speed":0.03143,"push_1.push_depth":0.09996,"retract_1.retract_height":0.16364},"optimized_scores":{"best_composite_score":0.67421,"best_fitness_score":0.88421,"best_task_score":0.9356},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1078.0,"contact_point_centroid":[0.51313,-0.10666,-0.00015],"force_p95":64.70638,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":79.43665,"mean_force":29.40865,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4989,-0.04989,0.02049]},{"body_a":"push_box","body_b":"link7","contact_count":611.0,"contact_point_centroid":[0.52534,-0.06058,0.05304],"force_p95":50.95969,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":64.90592,"mean_force":34.46235,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49925,-0.03969,0.02052]},{"body_a":"attachment","body_b":"push_box","contact_count":745.0,"contact_point_centroid":[0.51445,-0.06246,0.04677],"force_p95":54.35457,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":64.7094,"mean_force":27.8614,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49872,-0.05145,0.02037]},{"body_a":"attachment","body_b":"push_box","contact_count":178.0,"contact_point_centroid":[0.50641,0.00198,0.03477],"force_p95":6.10144,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.0203,"mean_force":2.50123,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.4997,0.01386,0.02131]},{"body_a":"world","body_b":"push_box","contact_count":3596.0,"contact_point_centroid":[0.50464,-0.02061,-1e-05],"force_p95":1.36033,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.23582,"mean_force":0.37463,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49815,0.03654,0.02511]},{"body_a":"push_box","body_b":"link7","contact_count":8.0,"contact_point_centroid":[0.53175,-0.00185,0.05009],"force_p95":3.87179,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.9601,"mean_force":1.76843,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50004,0.00975,0.02067]},{"body_a":"world","body_b":"push_box","contact_count":3996.0,"contact_point_centroid":[0.4975,-0.15808,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.80851,"mean_force":0.24628,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49323,-0.04374,0.05194]},{"body_a":"world","body_b":"push_box","contact_count":3580.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4992,0.04658,0.17199]}],"total_contact_groups":8},"final_pose_error":0.13568,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49752,-0.15808,0.02499],"final_tcp_position":[0.49444,0.02977,0.08735],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":79.43665,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":895.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3580.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.50029,0.06252,0.03384],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08192,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50708,-0.02781,0.0248],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.1224,"object_to_goal_dist_start":0.13127,"object_z_max":0.0251,"peak_contact_force":6.46624,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3782.0,"raw_peak_contact_force":8.0203,"tcp_end":[0.50009,0.00901,0.02055],"tcp_start":[0.50029,0.06252,0.03384],"tcp_to_object_dist_end":0.03771,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":783.0,"n_steps_budget":870.0,"object_pos_end":[0.49752,-0.15735,0.02506],"object_pos_start":[0.50708,-0.02781,0.0248],"object_to_goal_dist_end":0.00776,"object_to_goal_dist_start":0.1224,"object_z_max":0.02851,"peak_contact_force":0.75673,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2434.0,"raw_peak_contact_force":79.43665,"tcp_end":[0.49586,-0.12027,0.01979],"tcp_start":[0.50009,0.00901,0.02055],"tcp_to_object_dist_end":0.03749,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49752,-0.15808,0.02499],"object_pos_start":[0.49752,-0.15735,0.02506],"object_to_goal_dist_end":0.00845,"object_to_goal_dist_start":0.00776,"object_z_max":0.02506,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3996.0,"raw_peak_contact_force":0.80851,"tcp_end":[0.49444,0.02977,0.08735],"tcp_start":[0.49586,-0.12027,0.01979],"tcp_to_object_dist_end":0.19796,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.73885,"average_solve_count":157.0,"average_success_count":157.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.speed":0.03995,"push_1.push_depth":0.09977,"retract_1.retract_height":0.14503},"optimized_scores":{"best_composite_score":0.38852,"best_fitness_score":0.59852,"best_task_score":0.69626},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1255.0,"contact_point_centroid":[0.52155,-0.03919,-0.00014],"force_p95":59.57355,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":73.19144,"mean_force":31.53527,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50467,0.01491,0.0212]},{"body_a":"push_box","body_b":"link7","contact_count":749.0,"contact_point_centroid":[0.53126,-0.00565,0.05367],"force_p95":53.26803,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":63.01937,"mean_force":36.7414,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5045,0.01363,0.02117]},{"body_a":"attachment","body_b":"push_box","contact_count":772.0,"contact_point_centroid":[0.52109,0.00205,0.04837],"force_p95":56.6106,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":60.57237,"mean_force":33.93027,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50439,0.01254,0.02117]},{"body_a":"attachment","body_b":"push_box","contact_count":155.0,"contact_point_centroid":[0.51511,0.06822,0.0327],"force_p95":8.92404,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.13218,"mean_force":3.46709,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.51,0.08009,0.02163]},{"body_a":"world","body_b":"push_box","contact_count":2756.0,"contact_point_centroid":[0.51531,0.04593,-1e-05],"force_p95":2.10612,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.66123,"mean_force":0.44327,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50829,0.1011,0.02653]},{"body_a":"attachment","body_b":"push_box","contact_count":11.0,"contact_point_centroid":[0.5128,-0.06132,0.04799],"force_p95":1.18471,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.26963,"mean_force":0.31806,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49626,-0.04998,0.02148]},{"body_a":"world","body_b":"push_box","contact_count":3914.0,"contact_point_centroid":[0.49883,-0.0899,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.19344,"mean_force":0.25169,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49467,0.01946,0.06232]},{"body_a":"push_box","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.52128,-0.0762,0.05396],"force_p95":0.39384,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.39384,"mean_force":0.39384,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49717,-0.05272,0.02089]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50358,0.07681,0.17794]}],"total_contact_groups":9},"final_pose_error":0.07785,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.499,-0.0898,0.02499],"final_tcp_position":[0.49571,0.08659,0.10504],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":73.19144,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.51015,0.12542,0.03668],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07878,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":765.0,"n_steps_budget":870.0,"object_pos_end":[0.51716,0.0384,0.02502],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.18918,"object_to_goal_dist_start":0.19823,"object_z_max":0.02509,"peak_contact_force":1.58848,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2911.0,"raw_peak_contact_force":10.13218,"tcp_end":[0.51046,0.07523,0.02056],"tcp_start":[0.51015,0.12542,0.03668],"tcp_to_object_dist_end":0.03771,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":776.0,"n_steps_budget":870.0,"object_pos_end":[0.49959,-0.09139,0.02768],"object_pos_start":[0.51716,0.0384,0.02502],"object_to_goal_dist_end":0.05867,"object_to_goal_dist_start":0.18918,"object_z_max":0.02886,"peak_contact_force":2.01853,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2776.0,"raw_peak_contact_force":73.19144,"tcp_end":[0.49759,-0.05258,0.02101],"tcp_start":[0.51046,0.07523,0.02056],"tcp_to_object_dist_end":0.03943,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.499,-0.0898,0.02499],"object_pos_start":[0.49959,-0.09139,0.02768],"object_to_goal_dist_end":0.06021,"object_to_goal_dist_start":0.05867,"object_z_max":0.02769,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3926.0,"raw_peak_contact_force":1.26963,"tcp_end":[0.49571,0.08659,0.10504],"tcp_start":[0.49759,-0.05258,0.02101],"tcp_to_object_dist_end":0.19373,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```