## Search State

- **Seed**: 3
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4710 | 0.73 | ❌ rejected |
| 5 | approach → contact → push → lift | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | -0.4194 | 0.05 | ❌ rejected |
| 4 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4751 | 0.73 | ❌ rejected |
| 3 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4582 | 0.64 | ❌ rejected |
| 2 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4714 | 0.74 | ✅ accepted |

**Proposal policy**: task_score is 0.73 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.471) — your mutation base

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

- **Composite score**: 0.471
- **task_score** (E): 0.731
- **fitness_score**: 0.681  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.210

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2843 |
| contact_1 | 1.00 | 1.00 | 0.0441 |
| push_1 | 1.00 | 1.00 | 0.1258 |
| retract_1 | 0.00 | 1.00 | 0.1665 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.509, 0.078, 0.032) | (0.513, 0.002, 0.025)→(0.513, 0.002, 0.025) | 0.160→0.160 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / step_budget | (0.509, 0.078, 0.032)→(0.509, 0.035, 0.021) | (0.513, 0.002, 0.025)→(0.515, -0.004, 0.025) | 0.160→0.154 | 1.00 / 3.000 | 1.067 | 5.807 |
| push_1 | push | 1.00 / step_budget | (0.509, 0.035, 0.021)→(0.504, -0.084, 0.026) | (0.515, -0.004, 0.025)→(0.524, -0.115, 0.029) | 0.154→0.046 | 1.00 / 4.333 | 78.880 | 101.168 |
| retract_1 | retract | 0.00 / step_budget | (0.504, -0.084, 0.026)→(0.497, 0.064, 0.101) | (0.524, -0.115, 0.029)→(0.519, -0.110, 0.025) | 0.046→0.047 | 1.00 / 4.000 | 0.245 | 57.043 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.415
- goal_progress: 0.969
- terminal_score: 0.969
- phase_score: 0.751
- phase_breakdown.contact_score: 0.678
- phase_breakdown.approach_score: 0.820
- phase_breakdown.push_score: 0.767

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.838
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.969
- **Median Q (composite search score)**: 0.440
- **K-run variance**: 0.0139
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Parameters at upper bound**: push_1.push_depth
- **Final σ (mean)**: 0.497


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.07018,"average_solve_count":228.0,"average_success_count":228.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.02683,"contact_1.speed":0.01826,"push_1.push_depth":0.09024},"optimized_scores":{"best_composite_score":0.6282,"best_fitness_score":0.8382,"best_task_score":0.96925},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":698.0,"contact_point_centroid":[0.47466,-0.06725,0.02969],"force_p95":18.46518,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":34.26264,"mean_force":4.7656,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46954,-0.0553,0.02045]},{"body_a":"world","body_b":"push_box","contact_count":1494.0,"contact_point_centroid":[0.46918,-0.09037,-5e-05],"force_p95":8.23808,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.76316,"mean_force":2.571,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46702,-0.04847,0.02073]},{"body_a":"push_box","body_b":"link7","contact_count":61.0,"contact_point_centroid":[0.49198,-0.06112,0.05023],"force_p95":9.43119,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.87068,"mean_force":1.71815,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46326,-0.03972,0.0205]},{"body_a":"attachment","body_b":"push_box","contact_count":2.0,"contact_point_centroid":[0.49346,-0.12666,0.02001],"force_p95":2.14343,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.16349,"mean_force":1.96287,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49337,-0.11467,0.02003]},{"body_a":"world","body_b":"push_box","contact_count":3990.0,"contact_point_centroid":[0.4966,-0.15208,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.86095,"mean_force":0.24679,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49152,-0.03737,0.05331]},{"body_a":"world","body_b":"push_box","contact_count":3712.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47374,0.02259,0.16679]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.44552,0.02721,0.02727]}],"total_contact_groups":7},"final_pose_error":0.12833,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49661,-0.15202,0.02499],"final_tcp_position":[0.49349,0.03688,0.08976],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":34.26264,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":928.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3712.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.4489,0.04564,0.03445],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07781,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.44572,0.01228,0.02438],"tcp_start":[0.4489,0.04564,0.03445],"tcp_to_object_dist_end":0.04411,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":809.0,"n_steps_budget":900.0,"object_pos_end":[0.49677,-0.1516,0.02486],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.00361,"object_to_goal_dist_start":0.12843,"object_z_max":0.02542,"peak_contact_force":3.20071,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2253.0,"raw_peak_contact_force":34.26264,"tcp_end":[0.49337,-0.11463,0.02005],"tcp_start":[0.44572,0.01228,0.02438],"tcp_to_object_dist_end":0.03744,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49661,-0.15202,0.02499],"object_pos_start":[0.49677,-0.1516,0.02486],"object_to_goal_dist_end":0.00395,"object_to_goal_dist_start":0.00361,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3992.0,"raw_peak_contact_force":2.16349,"tcp_end":[0.49349,0.03688,0.08976],"tcp_start":[0.49337,-0.11463,0.02005],"tcp_to_object_dist_end":0.19972,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.7907,"average_solve_count":172.0,"average_success_count":172.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.07488,"contact_1.speed":0.04492,"push_1.push_depth":0.1},"optimized_scores":{"best_composite_score":0.44036,"best_fitness_score":0.65036,"best_task_score":0.63187},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":825.0,"contact_point_centroid":[0.56297,-0.04495,0.05401],"force_p95":125.58331,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":141.2377,"mean_force":83.2741,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5275,-0.03058,0.02403]},{"body_a":"world","body_b":"push_box","contact_count":1640.0,"contact_point_centroid":[0.55755,-0.07695,-0.00036],"force_p95":92.79057,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":105.7732,"mean_force":53.07857,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52753,-0.03063,0.02408]},{"body_a":"attachment","body_b":"push_box","contact_count":824.0,"contact_point_centroid":[0.54667,-0.03901,0.05449],"force_p95":83.72965,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":89.45319,"mean_force":51.47555,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5275,-0.03061,0.02404]},{"body_a":"world","body_b":"push_box","contact_count":3650.0,"contact_point_centroid":[0.53653,-0.10318,-3e-05],"force_p95":0.34052,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":81.71844,"mean_force":0.52435,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50282,-0.00712,0.06682]},{"body_a":"push_box","body_b":"link7","contact_count":52.0,"contact_point_centroid":[0.55137,-0.0936,0.05701],"force_p95":64.02283,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":75.17553,"mean_force":27.47102,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50896,-0.08652,0.03107]},{"body_a":"attachment","body_b":"push_box","contact_count":68.0,"contact_point_centroid":[0.53331,-0.08793,0.06181],"force_p95":42.30784,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":63.60507,"mean_force":15.38816,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50831,-0.08372,0.03172]},{"body_a":"attachment","body_b":"push_box","contact_count":120.0,"contact_point_centroid":[0.5539,0.02224,0.03803],"force_p95":7.98342,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.73364,"mean_force":2.78792,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54764,0.03418,0.02023]},{"body_a":"world","body_b":"push_box","contact_count":2230.0,"contact_point_centroid":[0.55328,-0.00072,-1e-05],"force_p95":1.06637,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.99029,"mean_force":0.40286,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54522,0.05522,0.02322]},{"body_a":"world","body_b":"push_box","contact_count":3916.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52229,0.03843,0.16448]}],"total_contact_groups":9},"final_pose_error":0.10196,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53594,-0.10314,0.02499],"final_tcp_position":[0.50014,0.06073,0.10074],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":141.2377,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":979.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3916.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.54658,0.0772,0.03118],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07637,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":633.0,"n_steps_budget":720.0,"object_pos_end":[0.55555,-0.00716,0.02505],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.15326,"object_to_goal_dist_start":0.16043,"object_z_max":0.02514,"peak_contact_force":1.70848,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2350.0,"raw_peak_contact_force":9.73364,"tcp_end":[0.54823,0.02967,0.01968],"tcp_start":[0.54658,0.0772,0.03118],"tcp_to_object_dist_end":0.03794,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":837.0,"n_steps_budget":930.0,"object_pos_end":[0.54228,-0.1146,0.03119],"object_pos_start":[0.55555,-0.00716,0.02505],"object_to_goal_dist_end":0.05549,"object_to_goal_dist_start":0.15326,"object_z_max":0.0312,"peak_contact_force":124.43804,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3289.0,"raw_peak_contact_force":141.2377,"tcp_end":[0.51016,-0.09075,0.03001],"tcp_start":[0.54823,0.02967,0.01968],"tcp_to_object_dist_end":0.04002,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53594,-0.10314,0.02499],"object_pos_start":[0.54228,-0.1146,0.03119],"object_to_goal_dist_end":0.05906,"object_to_goal_dist_start":0.05549,"object_z_max":0.03441,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3770.0,"raw_peak_contact_force":81.71844,"tcp_end":[0.50014,0.06073,0.10074],"tcp_start":[0.51016,-0.09075,0.03001],"tcp_to_object_dist_end":0.18404,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.60947,"average_solve_count":169.0,"average_success_count":169.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.09253,"contact_1.speed":0.02781,"push_1.push_depth":0.0922},"optimized_scores":{"best_composite_score":0.34447,"best_fitness_score":0.55447,"best_task_score":0.59153},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":738.0,"contact_point_centroid":[0.54903,-0.00806,0.05483],"force_p95":112.28222,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":128.0036,"mean_force":75.30864,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51807,0.00766,0.02346]},{"body_a":"attachment","body_b":"push_box","contact_count":744.0,"contact_point_centroid":[0.5367,-0.00087,0.05212],"force_p95":99.96781,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":110.42972,"mean_force":55.35063,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51818,0.00812,0.02342]},{"body_a":"world","body_b":"push_box","contact_count":1460.0,"contact_point_centroid":[0.54278,-0.04239,-0.0003],"force_p95":76.53348,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":93.29026,"mean_force":49.54855,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5181,0.00757,0.02351]},{"body_a":"push_box","body_b":"link7","contact_count":44.0,"contact_point_centroid":[0.54781,-0.05594,0.05587],"force_p95":79.67299,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":87.24604,"mean_force":39.82626,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50635,-0.04472,0.02992]},{"body_a":"world","body_b":"push_box","contact_count":3695.0,"contact_point_centroid":[0.52389,-0.07584,-3e-05],"force_p95":0.24862,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":73.93262,"mean_force":0.47833,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50067,0.02994,0.07172]},{"body_a":"attachment","body_b":"push_box","contact_count":64.0,"contact_point_centroid":[0.52747,-0.04804,0.05883],"force_p95":57.5752,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":69.15928,"mean_force":21.77066,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50555,-0.04145,0.03102]},{"body_a":"attachment","body_b":"push_box","contact_count":224.0,"contact_point_centroid":[0.53873,0.05723,0.03936],"force_p95":6.37965,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.44106,"mean_force":2.68209,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53131,0.06918,0.02039]},{"body_a":"world","body_b":"push_box","contact_count":3409.0,"contact_point_centroid":[0.53681,0.03413,-1e-05],"force_p95":2.08539,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.63895,"mean_force":0.42987,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52921,0.08882,0.02288]},{"body_a":"world","body_b":"push_box","contact_count":3996.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51453,0.05559,0.1638]}],"total_contact_groups":9},"final_pose_error":0.06734,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52337,-0.07578,0.02499],"final_tcp_position":[0.49852,0.09476,0.11151],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":128.0036,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":999.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3996.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.53088,0.11131,0.03067],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07479,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":980.0,"n_steps_budget":1000.0,"object_pos_end":[0.53952,0.02729,0.02521],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.18164,"object_to_goal_dist_start":0.1905,"object_z_max":0.02523,"peak_contact_force":1.24804,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3633.0,"raw_peak_contact_force":7.44106,"tcp_end":[0.53192,0.06407,0.01982],"tcp_start":[0.53088,0.11131,0.03067],"tcp_to_object_dist_end":0.03794,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":750.0,"n_steps_budget":840.0,"object_pos_end":[0.53176,-0.07798,0.03118],"object_pos_start":[0.53952,0.02729,0.02521],"object_to_goal_dist_end":0.07895,"object_to_goal_dist_start":0.18164,"object_z_max":0.03119,"peak_contact_force":109.00001,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2942.0,"raw_peak_contact_force":128.0036,"tcp_end":[0.50729,-0.04795,0.02866],"tcp_start":[0.53192,0.06407,0.01982],"tcp_to_object_dist_end":0.03882,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52337,-0.07578,0.02499],"object_pos_start":[0.53176,-0.07798,0.03118],"object_to_goal_dist_end":0.07781,"object_to_goal_dist_start":0.07895,"object_z_max":0.03437,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3803.0,"raw_peak_contact_force":87.24604,"tcp_end":[0.49852,0.09476,0.11151],"tcp_start":[0.50729,-0.04795,0.02866],"tcp_to_object_dist_end":0.19284,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```