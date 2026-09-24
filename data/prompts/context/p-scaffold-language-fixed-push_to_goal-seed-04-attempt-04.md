## Search State

- **Seed**: 4
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | force_threshold_switch | impedance_control | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | 0.3481 | 0.78 | ✅ accepted |
| 3 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.3267 | 0.19 | ❌ rejected |
| 2 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | force_threshold_switch | impedance_control | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | 0.3474 | 0.75 | ✅ accepted |
| 1 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.4720 | 0.58 | ❌ rejected |
| 0 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | force_threshold_switch | impedance_control | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | 0.3434 | 0.75 | ✅ accepted |

**Proposal policy**: task_score is 0.78 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `721a00290a47301d7751e432f1a041db545f1b55cfdb74b1d642c32f5b25f702`
- Frozen object start: [0.5531667326686841, 0.0013593063377233885, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.5531667326686841, 0.0013593063377233885, 0.025)
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
  frozen_object_start: [0.5532, 0.0014, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.5531667326686841, 0.0013593063377233885, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [-0.0532, -0.1514, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: 721a00290a47301d7751e432f1a041db545f1b55cfdb74b1d642c32f5b25f702

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

## Current Skill (Q=0.348) — your mutation base

```yaml
skill: push_to_goal
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: force_threshold_switch
  termination: pose_tolerance
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: impedance_control
  termination: contact_detected
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
    push_depth:
      type: scalar
      range:
      - 0.01
      - 0.1
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
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1

```

## Design Metrics

- **Composite score**: 0.348
- **task_score** (E): 0.778
- **fitness_score**: 0.708  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2765 |
| contact_1 | 1.00 | 1.00 | 0.0482 |
| push_1 | 1.00 | 1.00 | 0.1261 |
| retract_1 | 0.00 | 1.00 | 0.1448 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.525, 0.079, 0.038) | (0.531, 0.007, 0.025)→(0.531, 0.007, 0.025) | 0.161→0.161 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / step_budget | (0.525, 0.079, 0.038)→(0.527, 0.035, 0.021) | (0.531, 0.007, 0.025)→(0.533, -0.001, 0.025) | 0.161→0.153 | 1.00 / 2.333 | 3.309 | 13.951 |
| push_1 | push | 1.00 / step_budget | (0.527, 0.035, 0.021)→(0.502, -0.087, 0.024) | (0.533, -0.001, 0.025)→(0.515, -0.122, 0.028) | 0.153→0.037 | 1.00 / 4.333 | 57.497 | 78.722 |
| retract_1 | retract | 0.00 / step_budget | (0.502, -0.087, 0.024)→(0.497, 0.042, 0.089) | (0.515, -0.122, 0.028)→(0.512, -0.119, 0.025) | 0.037→0.038 | 1.00 / 4.000 | 0.245 | 47.626 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.468
- goal_progress: 0.953
- terminal_score: 0.953
- phase_score: 0.840
- phase_breakdown.approach_score: 0.821
- phase_breakdown.push_score: 0.834
- phase_breakdown.contact_score: 0.860

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.885
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.953
- **Median Q (composite search score)**: 0.316
- **K-run variance**: 0.0177
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.324


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `8d5a7e825d9524a0954b44a69bda19e1d764760f64bb1262d03aec3c389fadbb`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `c4094dd933e0897d422d7ea261a82b80810f7dec183b19c1da5b940157e7d0c4`; realized-scene SHA-256: `721a00290a47301d7751e432f1a041db545f1b55cfdb74b1d642c32f5b25f702`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.55317,0.00136,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.05317,-0.15136,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.55317,0.00136,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.8,"average_solve_count":155.0,"average_success_count":155.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.09114,"contact_1.contact_force":12.7468,"push_1.push_depth":0.09721,"push_1.push_distance":0.05349,"push_1.push_speed":0.09319,"retract_1.speed":0.08794},"optimized_scores":{"best_composite_score":0.31568,"best_fitness_score":0.67568,"best_task_score":0.71231},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":820.0,"contact_point_centroid":[0.55601,-0.04771,0.05476],"force_p95":108.65731,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":122.6774,"mean_force":70.35491,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52543,-0.03162,0.02301]},{"body_a":"world","body_b":"push_box","contact_count":1641.0,"contact_point_centroid":[0.54848,-0.08179,-0.00029],"force_p95":77.15636,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":93.13573,"mean_force":45.07115,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52567,-0.03105,0.02299]},{"body_a":"attachment","body_b":"push_box","contact_count":823.0,"contact_point_centroid":[0.54431,-0.04047,0.05384],"force_p95":83.17973,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":90.96953,"mean_force":48.74824,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52555,-0.03134,0.02301]},{"body_a":"world","body_b":"push_box","contact_count":3688.0,"contact_point_centroid":[0.52778,-0.11287,-3e-05],"force_p95":0.26844,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":86.04208,"mean_force":0.48722,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50205,-0.01316,0.0619]},{"body_a":"push_box","body_b":"link7","contact_count":49.0,"contact_point_centroid":[0.54945,-0.09515,0.05559],"force_p95":75.07767,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":81.71839,"mean_force":33.40868,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50756,-0.08418,0.0296]},{"body_a":"attachment","body_b":"push_box","contact_count":63.0,"contact_point_centroid":[0.53071,-0.08786,0.06018],"force_p95":58.76484,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":74.4145,"mean_force":20.99995,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50697,-0.08171,0.03018]},{"body_a":"attachment","body_b":"push_box","contact_count":89.0,"contact_point_centroid":[0.55366,0.02257,0.03749],"force_p95":10.11854,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.12765,"mean_force":3.25608,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54759,0.03452,0.02024]},{"body_a":"world","body_b":"push_box","contact_count":1878.0,"contact_point_centroid":[0.55317,-0.00049,-1e-05],"force_p95":0.94557,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.54148,"mean_force":0.40644,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54519,0.05605,0.0233]},{"body_a":"world","body_b":"push_box","contact_count":3848.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52232,0.03847,0.16436]}],"total_contact_groups":9},"final_pose_error":0.11815,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52713,-0.11266,0.02499],"final_tcp_position":[0.50005,0.04676,0.09255],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":122.6774,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":962.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3848.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.5466,0.07725,0.031],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07641,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":529.0,"n_steps_budget":600.0,"object_pos_end":[0.55389,-0.00634,0.02508],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.15344,"object_to_goal_dist_start":0.16043,"object_z_max":0.02516,"peak_contact_force":0.72856,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1967.0,"raw_peak_contact_force":12.12765,"tcp_end":[0.54817,0.03042,0.01979],"tcp_start":[0.5466,0.07725,0.031],"tcp_to_object_dist_end":0.03757,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":846.0,"n_steps_budget":960.0,"object_pos_end":[0.53377,-0.11785,0.03096],"object_pos_start":[0.55389,-0.00634,0.02508],"object_to_goal_dist_end":0.047,"object_to_goal_dist_start":0.15344,"object_z_max":0.03097,"peak_contact_force":120.68278,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3284.0,"raw_peak_contact_force":122.6774,"tcp_end":[0.50861,-0.08791,0.02864],"tcp_start":[0.54817,0.03042,0.01979],"tcp_to_object_dist_end":0.03918,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52713,-0.11266,0.02499],"object_pos_start":[0.53377,-0.11785,0.03096],"object_to_goal_dist_end":0.04615,"object_to_goal_dist_start":0.047,"object_z_max":0.03412,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3800.0,"raw_peak_contact_force":86.04208,"tcp_end":[0.50005,0.04676,0.09255],"tcp_start":[0.50861,-0.08791,0.02864],"tcp_to_object_dist_end":0.17525,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `452b4d03bf1b69f7d6475210c4cc0fbd85197208ecbf5594cd2cfcf54c82bcbb`; realized-scene SHA-256: `b2a76c5d1121259d09d3db2c62740fd8fe93dd873d8f379ba1928ff319a7d266`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5366,0.03695,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.0366,-0.18695,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5366,0.03695,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.3125,"average_solve_count":208.0,"average_success_count":208.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.03968,"contact_1.contact_force":14.34581,"push_1.push_depth":0.09364,"push_1.push_distance":0.15499,"push_1.push_speed":0.07428,"retract_1.speed":0.08108},"optimized_scores":{"best_composite_score":0.20374,"best_fitness_score":0.56374,"best_task_score":0.67004},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":752.0,"contact_point_centroid":[0.53754,-0.02471,0.05461],"force_p95":51.63056,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":57.70972,"mean_force":36.21729,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51175,-0.00814,0.02157]},{"body_a":"push_box","body_b":"link7","contact_count":24.0,"contact_point_centroid":[0.53167,-0.07764,0.05474],"force_p95":44.01687,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":50.46934,"mean_force":20.50808,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50114,-0.0536,0.02429]},{"body_a":"attachment","body_b":"push_box","contact_count":774.0,"contact_point_centroid":[0.5305,-0.01723,0.05279],"force_p95":44.84573,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":49.89112,"mean_force":30.15341,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51212,-0.00659,0.02151]},{"body_a":"world","body_b":"push_box","contact_count":1592.0,"contact_point_centroid":[0.52721,-0.05777,-0.00015],"force_p95":35.62323,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":46.65956,"mean_force":23.58026,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5128,-0.00351,0.02132]},{"body_a":"world","body_b":"push_box","contact_count":3869.0,"contact_point_centroid":[0.51019,-0.08855,-1e-05],"force_p95":0.24542,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":46.00473,"mean_force":0.2992,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49744,0.00929,0.05882]},{"body_a":"attachment","body_b":"push_box","contact_count":39.0,"contact_point_centroid":[0.52195,-0.06161,0.05621],"force_p95":33.3579,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.89251,"mean_force":10.35691,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50049,-0.05156,0.02475]},{"body_a":"attachment","body_b":"push_box","contact_count":114.0,"contact_point_centroid":[0.53841,0.05787,0.04461],"force_p95":13.75498,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.64899,"mean_force":7.0499,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53072,0.06982,0.02477]},{"body_a":"world","body_b":"push_box","contact_count":1815.0,"contact_point_centroid":[0.53693,0.0348,-1e-05],"force_p95":4.75793,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.54761,"mean_force":0.69544,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52804,0.08472,0.03489]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5132,0.05123,0.17421]}],"total_contact_groups":9},"final_pose_error":0.10164,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50999,-0.08794,0.02499],"final_tcp_position":[0.4971,0.06559,0.09346],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":57.70972,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.52839,0.10278,0.05105],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07128,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":509.0,"n_steps_budget":600.0,"object_pos_end":[0.5383,0.02843,0.02502],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.18249,"object_to_goal_dist_start":0.1905,"object_z_max":0.02514,"peak_contact_force":8.35338,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1929.0,"raw_peak_contact_force":15.64899,"tcp_end":[0.53168,0.0653,0.02184],"tcp_start":[0.52839,0.10278,0.05105],"tcp_to_object_dist_end":0.0376,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":859.0,"n_steps_budget":1000.0,"object_pos_end":[0.51177,-0.0923,0.02922],"object_pos_start":[0.5383,0.02843,0.02502],"object_to_goal_dist_end":0.05904,"object_to_goal_dist_start":0.18249,"object_z_max":0.02925,"peak_contact_force":50.69108,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3118.0,"raw_peak_contact_force":57.70972,"tcp_end":[0.50186,-0.05475,0.02411],"tcp_start":[0.53168,0.0653,0.02184],"tcp_to_object_dist_end":0.03917,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50999,-0.08794,0.02499],"object_pos_start":[0.51177,-0.0923,0.02922],"object_to_goal_dist_end":0.06286,"object_to_goal_dist_start":0.05904,"object_z_max":0.02922,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3932.0,"raw_peak_contact_force":50.46934,"tcp_end":[0.4971,0.06559,0.09346],"tcp_start":[0.50186,-0.05475,0.02411],"tcp_to_object_dist_end":0.1686,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `e3aaa9b30183e782395a479a1824f41a69a2557638e862a63e7a5368dd2a464a`; realized-scene SHA-256: `5f9daa62d5a7a2b8a7116f2dfbb5f9857bb0d5d4b297d304a4e76a9a270e7ec7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50458,-0.01881,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.00458,-0.13119,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.50458,-0.01881,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.55556,"average_solve_count":198.0,"average_success_count":198.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.07451,"contact_1.contact_force":7.52734,"push_1.push_depth":0.09989,"push_1.push_distance":0.14706,"push_1.push_speed":0.05011,"retract_1.speed":0.07085},"optimized_scores":{"best_composite_score":0.5248,"best_fitness_score":0.8848,"best_task_score":0.95268},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1474.0,"contact_point_centroid":[0.50916,-0.10642,-0.00013],"force_p95":48.1798,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":55.77999,"mean_force":21.03486,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49801,-0.05097,0.01997]},{"body_a":"push_box","body_b":"link7","contact_count":680.0,"contact_point_centroid":[0.52526,-0.05289,0.05231],"force_p95":42.00999,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":49.85183,"mean_force":30.97211,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49869,-0.03142,0.02008]},{"body_a":"attachment","body_b":"push_box","contact_count":945.0,"contact_point_centroid":[0.51244,-0.06099,0.04497],"force_p95":38.76646,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":43.43615,"mean_force":20.39023,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49796,-0.04964,0.01989]},{"body_a":"attachment","body_b":"push_box","contact_count":87.0,"contact_point_centroid":[0.506,0.00248,0.03428],"force_p95":10.86806,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.07665,"mean_force":3.54615,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49964,0.01434,0.02141]},{"body_a":"world","body_b":"push_box","contact_count":1912.0,"contact_point_centroid":[0.50464,-0.01994,-1e-05],"force_p95":1.00409,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.39735,"mean_force":0.41033,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49819,0.03577,0.02524]},{"body_a":"attachment","body_b":"push_box","contact_count":4.0,"contact_point_centroid":[0.50927,-0.13086,0.04847],"force_p95":5.56165,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.36629,"mean_force":2.22999,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49577,-0.11896,0.01976]},{"body_a":"world","body_b":"push_box","contact_count":3991.0,"contact_point_centroid":[0.49879,-0.15613,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.46878,"mean_force":0.24777,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49305,-0.05005,0.04837]},{"body_a":"world","body_b":"push_box","contact_count":3588.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49924,0.02862,0.16615]}],"total_contact_groups":8},"final_pose_error":0.15294,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49877,-0.15609,0.02499],"final_tcp_position":[0.49412,0.01437,0.07956],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":55.77999,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":897.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3588.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.5003,0.05779,0.03317],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07715,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":525.0,"n_steps_budget":600.0,"object_pos_end":[0.50662,-0.02639,0.02512],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.12379,"object_to_goal_dist_start":0.13127,"object_z_max":0.02514,"peak_contact_force":0.84449,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1999.0,"raw_peak_contact_force":14.07665,"tcp_end":[0.5,0.01046,0.02082],"tcp_start":[0.5003,0.05779,0.03317],"tcp_to_object_dist_end":0.03769,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":997.0,"n_steps_budget":1000.0,"object_pos_end":[0.49894,-0.15576,0.02493],"object_pos_start":[0.50662,-0.02639,0.02512],"object_to_goal_dist_end":0.00586,"object_to_goal_dist_start":0.12379,"object_z_max":0.02794,"peak_contact_force":1.11845,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3099.0,"raw_peak_contact_force":55.77999,"tcp_end":[0.49583,-0.11887,0.0198],"tcp_start":[0.5,0.01046,0.02082],"tcp_to_object_dist_end":0.03738,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49877,-0.15609,0.02499],"object_pos_start":[0.49894,-0.15576,0.02493],"object_to_goal_dist_end":0.00621,"object_to_goal_dist_start":0.00586,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3995.0,"raw_peak_contact_force":6.36629,"tcp_end":[0.49412,0.01437,0.07956],"tcp_start":[0.49583,-0.11887,0.0198],"tcp_to_object_dist_end":0.17905,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```