## Search State

- **Seed**: 4
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | force_threshold_switch | impedance_control | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | 0.3486 | 0.76 | ❌ rejected |
| 8 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | force_threshold_switch | impedance_control | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | 0.3482 | 0.75 | ❌ rejected |
| 7 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | force_threshold_switch | impedance_control | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | 0.3227 | 0.73 | ❌ rejected |
| 6 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | force_threshold_switch | impedance_control | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | 0.3482 | 0.75 | ❌ rejected |
| 5 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | -0.3477 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.76 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.349) — your mutation base

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

- **Composite score**: 0.349
- **task_score** (E): 0.761
- **fitness_score**: 0.709  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2829 |
| contact_1 | 1.00 | 1.00 | 0.0479 |
| push_1 | 1.00 | 1.00 | 0.1260 |
| retract_1 | 0.00 | 1.00 | 0.1432 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.526, 0.082, 0.033) | (0.531, 0.007, 0.025)→(0.531, 0.007, 0.025) | 0.161→0.161 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / step_budget | (0.526, 0.082, 0.033)→(0.527, 0.035, 0.020) | (0.531, 0.007, 0.025)→(0.533, -0.001, 0.025) | 0.161→0.153 | 1.00 / 3.000 | 4.432 | 11.684 |
| push_1 | push | 1.00 / step_budget | (0.527, 0.035, 0.020)→(0.504, -0.087, 0.026) | (0.533, -0.001, 0.025)→(0.523, -0.119, 0.029) | 0.153→0.041 | 1.00 / 4.333 | 78.783 | 107.462 |
| retract_1 | retract | 0.00 / step_budget | (0.504, -0.087, 0.026)→(0.498, 0.041, 0.089) | (0.523, -0.119, 0.029)→(0.519, -0.114, 0.025) | 0.041→0.042 | 1.00 / 4.000 | 0.245 | 61.840 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.494
- goal_progress: 0.987
- terminal_score: 0.987
- phase_score: 0.821
- phase_breakdown.approach_score: 0.822
- phase_breakdown.push_score: 0.796
- phase_breakdown.contact_score: 0.860

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.887
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.987
- **Median Q (composite search score)**: 0.305
- **K-run variance**: 0.0174
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.398


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.8,"average_solve_count":155.0,"average_success_count":155.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.09624,"contact_1.contact_force":14.34943,"push_1.push_depth":0.09867,"push_1.push_distance":0.1035,"push_1.push_speed":0.08316,"retract_1.speed":0.09983},"optimized_scores":{"best_composite_score":0.30511,"best_fitness_score":0.66511,"best_task_score":0.67206},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":949.0,"contact_point_centroid":[0.56077,-0.04716,0.05405],"force_p95":117.24323,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":137.54359,"mean_force":77.28392,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52646,-0.03127,0.02371]},{"body_a":"world","body_b":"push_box","contact_count":1857.0,"contact_point_centroid":[0.55444,-0.08074,-0.00036],"force_p95":81.67797,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":96.13231,"mean_force":49.91584,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52622,-0.0322,0.02385]},{"body_a":"world","body_b":"push_box","contact_count":3679.0,"contact_point_centroid":[0.53317,-0.10879,-3e-05],"force_p95":0.26103,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":84.41056,"mean_force":0.51495,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50226,-0.00704,0.06646]},{"body_a":"attachment","body_b":"push_box","contact_count":950.0,"contact_point_centroid":[0.54573,-0.03984,0.05434],"force_p95":81.02319,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":84.34534,"mean_force":49.14854,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5265,-0.03118,0.02371]},{"body_a":"push_box","body_b":"link7","contact_count":53.0,"contact_point_centroid":[0.54902,-0.09692,0.05726],"force_p95":69.65662,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":79.77892,"mean_force":28.15591,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50811,-0.08586,0.03075]},{"body_a":"attachment","body_b":"push_box","contact_count":61.0,"contact_point_centroid":[0.53258,-0.08832,0.0615],"force_p95":49.6561,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":69.66291,"mean_force":18.52196,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50763,-0.08383,0.03124]},{"body_a":"attachment","body_b":"push_box","contact_count":88.0,"contact_point_centroid":[0.55379,0.02265,0.03797],"force_p95":9.95959,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.9651,"mean_force":3.27352,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54758,0.03461,0.02029]},{"body_a":"world","body_b":"push_box","contact_count":1900.0,"contact_point_centroid":[0.55321,-0.00022,-1e-05],"force_p95":1.02405,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.36493,"mean_force":0.40231,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54521,0.05574,0.0234]},{"body_a":"world","body_b":"push_box","contact_count":3820.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5223,0.03842,0.16453]}],"total_contact_groups":9},"final_pose_error":0.10153,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53258,-0.10869,0.02499],"final_tcp_position":[0.4998,0.06121,0.10076],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":137.54359,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":955.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3820.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.54657,0.07718,0.03124],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07637,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":529.0,"n_steps_budget":600.0,"object_pos_end":[0.5545,-0.00648,0.025],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.15352,"object_to_goal_dist_start":0.16043,"object_z_max":0.02513,"peak_contact_force":6.24574,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1988.0,"raw_peak_contact_force":11.9651,"tcp_end":[0.54816,0.03038,0.01979],"tcp_start":[0.54657,0.07718,0.03124],"tcp_to_object_dist_end":0.03777,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":960.0,"n_steps_budget":1000.0,"object_pos_end":[0.53887,-0.11634,0.03113],"object_pos_start":[0.5545,-0.00648,0.025],"object_to_goal_dist_end":0.05178,"object_to_goal_dist_start":0.15352,"object_z_max":0.03113,"peak_contact_force":117.4638,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3756.0,"raw_peak_contact_force":137.54359,"tcp_end":[0.50928,-0.09032,0.0296],"tcp_start":[0.54816,0.03038,0.01979],"tcp_to_object_dist_end":0.03944,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53258,-0.10869,0.02499],"object_pos_start":[0.53887,-0.11634,0.03113],"object_to_goal_dist_end":0.05261,"object_to_goal_dist_start":0.05178,"object_z_max":0.03501,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3793.0,"raw_peak_contact_force":84.41056,"tcp_end":[0.4998,0.06121,0.10076],"tcp_start":[0.50928,-0.09032,0.0296],"tcp_to_object_dist_end":0.1889,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.6954,"average_solve_count":174.0,"average_success_count":174.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.08228,"contact_1.contact_force":9.19152,"push_1.push_depth":0.09994,"push_1.push_distance":0.16152,"push_1.push_speed":0.08445,"retract_1.speed":0.06565},"optimized_scores":{"best_composite_score":0.2133,"best_fitness_score":0.5733,"best_task_score":0.62486},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":919.0,"contact_point_centroid":[0.54783,-0.01324,0.0548],"force_p95":106.75643,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":116.86365,"mean_force":70.48874,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51722,0.00295,0.02335]},{"body_a":"attachment","body_b":"push_box","contact_count":927.0,"contact_point_centroid":[0.53633,-0.00566,0.05302],"force_p95":95.11379,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":102.33807,"mean_force":51.71093,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51734,0.0035,0.02332]},{"body_a":"push_box","body_b":"link7","contact_count":51.0,"contact_point_centroid":[0.54645,-0.0653,0.05575],"force_p95":81.0701,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":88.4949,"mean_force":38.73731,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5056,-0.05275,0.02956]},{"body_a":"world","body_b":"push_box","contact_count":3662.0,"contact_point_centroid":[0.52537,-0.08313,-3e-05],"force_p95":0.27371,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":87.46691,"mean_force":0.5197,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50064,0.00855,0.06183]},{"body_a":"attachment","body_b":"push_box","contact_count":68.0,"contact_point_centroid":[0.5285,-0.05691,0.0598],"force_p95":61.0803,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":84.11095,"mean_force":23.32381,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50499,-0.05038,0.03025]},{"body_a":"world","body_b":"push_box","contact_count":1762.0,"contact_point_centroid":[0.54176,-0.04989,-0.00031],"force_p95":70.10004,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":80.91998,"mean_force":47.65847,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51692,0.00108,0.02357]},{"body_a":"attachment","body_b":"push_box","contact_count":98.0,"contact_point_centroid":[0.53848,0.05794,0.03987],"force_p95":10.67168,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.07166,"mean_force":3.42344,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53117,0.06987,0.02096]},{"body_a":"world","body_b":"push_box","contact_count":1842.0,"contact_point_centroid":[0.53688,0.03517,-1e-05],"force_p95":1.38538,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.95463,"mean_force":0.43488,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.5291,0.08959,0.02487]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51434,0.05497,0.16529]}],"total_contact_groups":9},"final_pose_error":0.10804,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52477,-0.08296,0.02499],"final_tcp_position":[0.49919,0.05906,0.09167],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":116.86365,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.53062,0.11018,0.0334],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07395,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":521.0,"n_steps_budget":600.0,"object_pos_end":[0.53803,0.02865,0.02497],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.18266,"object_to_goal_dist_start":0.1905,"object_z_max":0.02509,"peak_contact_force":6.3311,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1940.0,"raw_peak_contact_force":11.07166,"tcp_end":[0.53173,0.06555,0.02023],"tcp_start":[0.53062,0.11018,0.0334],"tcp_to_object_dist_end":0.03773,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":931.0,"n_steps_budget":1000.0,"object_pos_end":[0.5301,-0.08731,0.03109],"object_pos_start":[0.53803,0.02865,0.02497],"object_to_goal_dist_end":0.06981,"object_to_goal_dist_start":0.18266,"object_z_max":0.03108,"peak_contact_force":108.06805,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3608.0,"raw_peak_contact_force":116.86365,"tcp_end":[0.50657,-0.05629,0.02834],"tcp_start":[0.53173,0.06555,0.02023],"tcp_to_object_dist_end":0.03903,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52477,-0.08296,0.02499],"object_pos_start":[0.5301,-0.08731,0.03109],"object_to_goal_dist_end":0.07146,"object_to_goal_dist_start":0.06981,"object_z_max":0.03392,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3781.0,"raw_peak_contact_force":88.4949,"tcp_end":[0.49919,0.05906,0.09167],"tcp_start":[0.50657,-0.05629,0.02834],"tcp_to_object_dist_end":0.15897,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.11765,"average_solve_count":221.0,"average_success_count":221.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.05222,"contact_1.contact_force":15.20894,"push_1.push_depth":0.09673,"push_1.push_distance":0.0821,"push_1.push_speed":0.07675,"retract_1.speed":0.05223},"optimized_scores":{"best_composite_score":0.52733,"best_fitness_score":0.88733,"best_task_score":0.98746},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1246.0,"contact_point_centroid":[0.51155,-0.10478,-0.00013],"force_p95":57.29866,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":67.97882,"mean_force":24.46597,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49826,-0.04934,0.0202]},{"body_a":"push_box","body_b":"link7","contact_count":625.0,"contact_point_centroid":[0.52512,-0.05275,0.05268],"force_p95":45.25201,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":55.88152,"mean_force":33.71274,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49884,-0.03282,0.02029]},{"body_a":"attachment","body_b":"push_box","contact_count":823.0,"contact_point_centroid":[0.51332,-0.05959,0.04604],"force_p95":42.558,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":49.23278,"mean_force":22.72245,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4982,-0.04829,0.02011]},{"body_a":"push_box","body_b":"link7","contact_count":34.0,"contact_point_centroid":[0.52406,-0.13578,0.05026],"force_p95":8.74275,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.61347,"mean_force":4.20031,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49368,-0.10994,0.02013]},{"body_a":"attachment","body_b":"push_box","contact_count":84.0,"contact_point_centroid":[0.50372,0.00247,0.02967],"force_p95":10.07829,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.01523,"mean_force":3.47433,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49961,0.01437,0.0214]},{"body_a":"world","body_b":"push_box","contact_count":3879.0,"contact_point_centroid":[0.49983,-0.15122,-2e-05],"force_p95":0.24971,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.69076,"mean_force":0.29227,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49292,-0.05258,0.04595]},{"body_a":"attachment","body_b":"push_box","contact_count":6.0,"contact_point_centroid":[0.50531,-0.12772,0.03992],"force_p95":5.91016,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.55768,"mean_force":1.67852,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49572,-0.11583,0.01975]},{"body_a":"world","body_b":"push_box","contact_count":1936.0,"contact_point_centroid":[0.50484,-0.0197,-1e-05],"force_p95":1.17468,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.90177,"mean_force":0.3968,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49821,0.03547,0.02515]},{"body_a":"world","body_b":"push_box","contact_count":3808.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4992,0.02862,0.16612]}],"total_contact_groups":9},"final_pose_error":0.16603,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49989,-0.15164,0.02499],"final_tcp_position":[0.49384,0.00294,0.07317],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":67.97882,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":952.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3808.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.50028,0.0578,0.03311],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07716,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":525.0,"n_steps_budget":600.0,"object_pos_end":[0.50621,-0.02635,0.02505],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.1238,"object_to_goal_dist_start":0.13127,"object_z_max":0.02506,"peak_contact_force":0.71995,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2020.0,"raw_peak_contact_force":12.01523,"tcp_end":[0.5,0.01047,0.02082],"tcp_start":[0.50028,0.0578,0.03311],"tcp_to_object_dist_end":0.03759,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":872.0,"n_steps_budget":1000.0,"object_pos_end":[0.49982,-0.15252,0.0249],"object_pos_start":[0.50621,-0.02635,0.02505],"object_to_goal_dist_end":0.00252,"object_to_goal_dist_start":0.1238,"object_z_max":0.02802,"peak_contact_force":10.81771,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2694.0,"raw_peak_contact_force":67.97882,"tcp_end":[0.49585,-0.11574,0.01982],"tcp_start":[0.5,0.01047,0.02082],"tcp_to_object_dist_end":0.03734,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49989,-0.15164,0.02499],"object_pos_start":[0.49982,-0.15252,0.0249],"object_to_goal_dist_end":0.00165,"object_to_goal_dist_start":0.00252,"object_z_max":0.02683,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3919.0,"raw_peak_contact_force":12.61347,"tcp_end":[0.49384,0.00294,0.07317],"tcp_start":[0.49585,-0.11574,0.01982],"tcp_to_object_dist_end":0.16203,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```