## Search State

- **Seed**: 3
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | -0.2082 | 0.02 | ❌ rejected |
| 8 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | force_exceeded | pose_tolerance | 4 | 0.2665 | 0.04 | ❌ rejected |
| 7 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4540 | 0.64 | ❌ rejected |
| 6 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4710 | 0.73 | ❌ rejected |
| 5 | approach → contact → push → lift | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | -0.4194 | 0.05 | ❌ rejected |

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
- Frozen realised-scene SHA-256: `35b7946dd60174c5d3e72b05c58367a0800836a817579e6ae5b810157d0560be`
- Frozen object start: [0.45027790005723495, -0.03158273920846803, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.45027790005723495, -0.03158273920846803, 0.025)
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
  frozen_object_start: [0.4503, -0.0316, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.45027790005723495, -0.03158273920846803, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [0.0497, -0.1184, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: 35b7946dd60174c5d3e72b05c58367a0800836a817579e6ae5b810157d0560be

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

## Current Skill (Q=-0.208) — your mutation base

```yaml
skill: push_to_goal
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
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
  generator: linear_cartesian
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

```

## Design Metrics

- **Composite score**: -0.208
- **task_score** (E): 0.018
- **fitness_score**: 0.152  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2338 |
| contact_1 | 1.00 | 1.00 | 0.0593 |
| push_1 | 0.00 | 1.00 | 0.0000 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.513, 0.074, 0.091) | (0.513, 0.002, 0.025)→(0.513, 0.002, 0.025) | 0.160→0.160 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / step_budget | (0.513, 0.074, 0.091)→(0.514, 0.032, 0.051) | (0.513, 0.002, 0.025)→(0.514, -0.000, 0.024) | 0.160→0.157 | 1.00 / 4.667 | 83.001 | 92.285 |
| push_1 | push | 0.00 / guard_failure | (0.514, 0.032, 0.051)→(0.514, 0.032, 0.051) | (0.514, -0.000, 0.024)→(0.514, -0.000, 0.024) | 0.157→0.157 | 1.00 / 4.667 | 59.444 | 59.444 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.031
- lateral_force_integral: None
- approach_alignment: 0.458
- goal_progress: 0.031
- terminal_score: 0.031
- phase_score: 0.242
- phase_breakdown.contact_score: 0.557
- phase_breakdown.approach_score: 0.220
- phase_breakdown.push_score: 0.061

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.157
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.031
- **Median Q (composite search score)**: -0.210
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.258


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `01fea9f27a58d64b0f9b0ff0cae1096a52b0da1ad311c77058a75ddb9aab77d2`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `c53c9bf1992485fcf877d50f4ee23d3483b4b9e63e5a19adda2461c26d89c46e`; realized-scene SHA-256: `35b7946dd60174c5d3e72b05c58367a0800836a817579e6ae5b810157d0560be`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45028,-0.03158,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.04972,-0.11842,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.45028,-0.03158,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.94969,"average_solve_count":159.0,"average_success_count":159.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.03908,"contact_1.speed":0.03748,"push_1.force_limit":20.94642,"push_1.push_depth":0.12379,"push_1.speed":0.0333,"retract_1.speed":0.05994},"optimized_scores":{"best_composite_score":-0.20252,"best_fitness_score":0.15748,"best_task_score":0.03095},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":178.0,"contact_point_centroid":[0.44354,-0.00827,0.04894],"force_p95":109.50058,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":127.87913,"mean_force":73.07015,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.43598,-0.0007,0.05332]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.44617,-0.01065,0.04841],"force_p95":57.31126,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":57.31126,"mean_force":57.31126,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.43946,-0.00223,0.05182]},{"body_a":"world","body_b":"push_box","contact_count":3964.0,"contact_point_centroid":[0.45042,-0.03186,-4e-05],"force_p95":24.39011,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":47.54672,"mean_force":3.52534,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.42769,0.01526,0.0685]},{"body_a":"world","body_b":"push_box","contact_count":4.0,"contact_point_centroid":[0.45192,-0.03522,-0.00032],"force_p95":35.09284,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":38.3728,"mean_force":14.80045,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.43946,-0.00223,0.05182]},{"body_a":"world","body_b":"push_box","contact_count":3004.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.46013,0.01935,0.19703]}],"total_contact_groups":5},"final_pose_error":0.15901,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.45192,-0.03521,0.02437],"final_tcp_position":[0.43948,-0.00223,0.05181],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":127.87913,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":751.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3004.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.42088,0.03935,0.09423],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.10339,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":991.0,"n_steps_budget":1000.0,"object_pos_end":[0.45193,-0.03518,0.02436],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12448,"object_to_goal_dist_start":0.12843,"object_z_max":0.02499,"peak_contact_force":106.30343,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":4142.0,"raw_peak_contact_force":127.87913,"subtask_id":"contact","tcp_end":[0.43946,-0.00223,0.05182],"tcp_start":[0.42088,0.03935,0.09423],"tcp_to_object_dist_end":0.04467,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.45192,-0.03521,0.02437],"object_pos_start":[0.45193,-0.03518,0.02436],"object_to_goal_dist_end":0.12446,"object_to_goal_dist_start":0.12448,"object_z_max":0.02436,"peak_contact_force":57.31126,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":5.0,"raw_peak_contact_force":57.31126,"subtask_id":"push","tcp_end":[0.43948,-0.00223,0.05181],"tcp_start":[0.43946,-0.00223,0.05182],"tcp_to_object_dist_end":0.04467,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `234a0edc218dcf63b67654ddcfd8b0f12da84040687f62c4c4845001a50f549a`; realized-scene SHA-256: `721a00290a47301d7751e432f1a041db545f1b55cfdb74b1d642c32f5b25f702`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.55317,0.00136,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.05317,-0.15136,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.55317,0.00136,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.95,"average_solve_count":140.0,"average_success_count":140.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.05032,"contact_1.speed":0.03195,"push_1.force_limit":18.34874,"push_1.push_depth":0.12972,"push_1.speed":0.03747,"retract_1.speed":0.0192},"optimized_scores":{"best_composite_score":-0.21008,"best_fitness_score":0.14992,"best_task_score":0.01151},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":172.0,"contact_point_centroid":[0.56919,0.02531,0.04918],"force_p95":69.8241,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":72.36996,"mean_force":42.54748,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.56026,0.03271,0.05151]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.57137,0.02391,0.04856],"force_p95":60.39391,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":60.39391,"mean_force":60.39391,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.56156,0.03005,0.05085]},{"body_a":"world","body_b":"push_box","contact_count":3703.0,"contact_point_centroid":[0.55352,0.00153,-3e-05],"force_p95":16.93838,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":46.78244,"mean_force":2.23553,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.56275,0.04767,0.06342]},{"body_a":"world","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.56193,0.00724,-0.00028],"force_p95":41.8357,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":45.29528,"mean_force":20.53001,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.56156,0.03005,0.05085]},{"body_a":"world","body_b":"push_box","contact_count":3636.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.53492,0.03613,0.19336]}],"total_contact_groups":5},"final_pose_error":0.16141,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.55373,-0.0008,0.02458],"final_tcp_position":[0.56157,0.03003,0.05085],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":72.36996,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":909.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3636.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.57194,0.07256,0.08931],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.09777,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":938.0,"n_steps_budget":1000.0,"object_pos_end":[0.55373,-0.00079,0.02457],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.15859,"object_to_goal_dist_start":0.16043,"object_z_max":0.02499,"peak_contact_force":69.83503,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3875.0,"raw_peak_contact_force":72.36996,"subtask_id":"contact","tcp_end":[0.56156,0.03005,0.05085],"tcp_start":[0.57194,0.07256,0.08931],"tcp_to_object_dist_end":0.04127,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.55373,-0.0008,0.02458],"object_pos_start":[0.55373,-0.00079,0.02457],"object_to_goal_dist_end":0.15858,"object_to_goal_dist_start":0.15859,"object_z_max":0.02457,"peak_contact_force":60.39391,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4.0,"raw_peak_contact_force":60.39391,"subtask_id":"push","tcp_end":[0.56157,0.03003,0.05085],"tcp_start":[0.56156,0.03005,0.05085],"tcp_to_object_dist_end":0.04126,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `107d1233d3b0a09f0fa34aa18231b315c9a1d92237bb254399d486ed8004836a`; realized-scene SHA-256: `b2a76c5d1121259d09d3db2c62740fd8fe93dd873d8f379ba1928ff319a7d266`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5366,0.03695,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.0366,-0.18695,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5366,0.03695,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.89571,"average_solve_count":163.0,"average_success_count":163.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.04248,"contact_1.speed":0.03024,"push_1.force_limit":15.46336,"push_1.push_depth":0.1232,"push_1.speed":0.0287,"retract_1.speed":0.05223},"optimized_scores":{"best_composite_score":-0.21196,"best_fitness_score":0.14804,"best_task_score":0.01146},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":184.0,"contact_point_centroid":[0.54743,0.06082,0.0492],"force_p95":72.82825,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":76.60725,"mean_force":44.23307,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53934,0.06907,0.05166]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.54973,0.05929,0.04862],"force_p95":60.627,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":60.627,"mean_force":60.627,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.54105,0.06682,0.05096]},{"body_a":"world","body_b":"push_box","contact_count":3956.0,"contact_point_centroid":[0.53664,0.03676,-3e-05],"force_p95":16.11986,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":44.44835,"mean_force":2.31177,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53981,0.08368,0.06345]},{"body_a":"world","body_b":"push_box","contact_count":4.0,"contact_point_centroid":[0.53712,0.03447,-0.00023],"force_p95":34.38769,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":37.36836,"mean_force":15.48845,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.54105,0.06682,0.05096]},{"body_a":"world","body_b":"push_box","contact_count":3752.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52189,0.05448,0.19324]}],"total_contact_groups":5},"final_pose_error":0.15555,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53734,0.03458,0.02454],"final_tcp_position":[0.54107,0.06681,0.05096],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":76.60725,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":938.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3752.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.54576,0.10923,0.0894],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.09724,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":989.0,"n_steps_budget":1000.0,"object_pos_end":[0.53734,0.03459,0.02454],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.18833,"object_to_goal_dist_start":0.1905,"object_z_max":0.02499,"peak_contact_force":72.86584,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":4140.0,"raw_peak_contact_force":76.60725,"subtask_id":"contact","tcp_end":[0.54105,0.06682,0.05096],"tcp_start":[0.54576,0.10923,0.0894],"tcp_to_object_dist_end":0.04185,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.53734,0.03458,0.02454],"object_pos_start":[0.53734,0.03459,0.02454],"object_to_goal_dist_end":0.18832,"object_to_goal_dist_start":0.18833,"object_z_max":0.02454,"peak_contact_force":60.627,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":5.0,"raw_peak_contact_force":60.627,"subtask_id":"push","tcp_end":[0.54107,0.06681,0.05096],"tcp_start":[0.54105,0.06682,0.05096],"tcp_to_object_dist_end":0.04184,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```