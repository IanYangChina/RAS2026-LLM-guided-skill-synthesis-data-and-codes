## Search State

- **Seed**: 8
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | force_threshold_switch | impedance_control | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 5 | 0.4445 | 0.75 | ❌ rejected |
| 2 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | force_threshold_switch | impedance_control | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 5 | 0.4361 | 0.73 | ❌ rejected |
| 1 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 12 | -0.0999 | 0.20 | ❌ rejected |
| 0 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | force_threshold_switch | impedance_control | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 5 | 0.4443 | 0.76 | ✅ accepted |

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
- Frozen realised-scene SHA-256: `f3b8ea82cefd9504be10e2d47c49094a836a703404c06bdee3b01a27a59bf7be`
- Frozen object start: [0.4792366731926673, 0.05847322120055107, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.4792366731926673, 0.05847322120055107, 0.025)
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
  frozen_object_start: [0.4792, 0.0585, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.4792366731926673, 0.05847322120055107, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [0.0208, -0.2085, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: f3b8ea82cefd9504be10e2d47c49094a836a703404c06bdee3b01a27a59bf7be

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

## Current Skill (Q=0.444) — your mutation base

```yaml
skill: push_to_goal
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: force_threshold_switch
  termination: pose_tolerance
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.3
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: impedance_control
  termination: contact_detected
- id: push_1
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: pose_tolerance
  parameters:
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
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.2
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1

```

## Design Metrics

- **Composite score**: 0.444
- **task_score** (E): 0.749
- **fitness_score**: 0.754  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.310

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2844 |
| contact_1 | 1.00 | 1.00 | 0.0483 |
| push_1 | 1.00 | 1.00 | 0.1408 |
| retract_1 | 0.00 | 1.00 | 0.1298 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.521, 0.075, 0.032) | (0.526, -0.001, 0.025)→(0.526, -0.001, 0.025) | 0.156→0.156 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / step_budget | (0.521, 0.075, 0.032)→(0.521, 0.028, 0.020) | (0.526, -0.001, 0.025)→(0.528, -0.008, 0.025) | 0.156→0.150 | 1.00 / 3.000 | 3.389 | 12.541 |
| push_1 | push | 1.00 / step_budget | (0.521, 0.028, 0.020)→(0.505, -0.108, 0.026) | (0.528, -0.008, 0.025)→(0.518, -0.136, 0.029) | 0.150→0.042 | 1.00 / 3.667 | 76.478 | 112.489 |
| retract_1 | retract | 0.00 / step_budget | (0.505, -0.108, 0.026)→(0.499, -0.004, 0.102) | (0.518, -0.136, 0.029)→(0.515, -0.136, 0.025) | 0.042→0.038 | 1.00 / 4.000 | 0.245 | 53.019 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.928
- lateral_force_integral: None
- approach_alignment: 0.520
- goal_progress: 0.736
- terminal_score: 0.736
- phase_score: 0.831
- phase_breakdown.contact_score: 0.848
- phase_breakdown.approach_score: 0.822
- phase_breakdown.push_score: 0.824

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.793
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.786
- **Median Q (composite search score)**: 0.465
- **K-run variance**: 0.0018
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Parameters at upper bound**: push_1.push_speed
- **Final σ (mean)**: 0.327


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `8267fcc1127ab3c529e380fe6aea430def9956719b146bd9818eb52355cb895d`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `33d626702a3717cebb1eda35e1cb80c1c9d108c246efccd193577b9105813420`; realized-scene SHA-256: `f3b8ea82cefd9504be10e2d47c49094a836a703404c06bdee3b01a27a59bf7be`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47924,0.05847,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.02076,-0.20847,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.47924,0.05847,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.51429,"average_solve_count":175.0,"average_success_count":175.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.19737,"push_1.push_distance":0.13982,"push_1.push_speed":0.09931,"retract_1.retract_height":0.092,"retract_1.speed":0.03585},"optimized_scores":{"best_composite_score":0.38512,"best_fitness_score":0.69512,"best_task_score":0.78621},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1504.0,"contact_point_centroid":[0.48237,-0.0506,-8e-05],"force_p95":56.21649,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":73.61928,"mean_force":10.88195,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48479,-0.00575,0.01928]},{"body_a":"attachment","body_b":"push_box","contact_count":862.0,"contact_point_centroid":[0.4895,-0.00447,0.03158],"force_p95":43.91162,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":55.06035,"mean_force":13.13909,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48332,0.00688,0.01935]},{"body_a":"push_box","body_b":"link7","contact_count":295.0,"contact_point_centroid":[0.50537,0.03914,0.05133],"force_p95":42.35318,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":44.30201,"mean_force":28.64051,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47728,0.06207,0.02002]},{"body_a":"attachment","body_b":"push_box","contact_count":105.0,"contact_point_centroid":[0.47907,0.0795,0.02918],"force_p95":8.07072,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.5515,"mean_force":3.47063,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47458,0.09126,0.02156]},{"body_a":"world","body_b":"push_box","contact_count":1861.0,"contact_point_centroid":[0.47956,0.05705,-1e-05],"force_p95":1.75689,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.83506,"mean_force":0.44468,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47369,0.11068,0.02457]},{"body_a":"attachment","body_b":"push_box","contact_count":2.0,"contact_point_centroid":[0.49046,-0.09292,0.02206],"force_p95":1.40562,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.40966,"mean_force":1.36918,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49477,-0.08194,0.01992]},{"body_a":"world","body_b":"push_box","contact_count":3986.0,"contact_point_centroid":[0.47385,-0.11369,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.2029,"mean_force":0.24684,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49192,-0.04031,0.05733]},{"body_a":"world","body_b":"push_box","contact_count":3972.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48715,0.06586,0.16416]}],"total_contact_groups":8},"final_pose_error":0.15669,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.4738,-0.11367,0.02499],"final_tcp_position":[0.49303,0.00418,0.09308],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":73.61928,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":993.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3972.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.47614,0.13178,0.03157],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07366,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":519.0,"n_steps_budget":600.0,"object_pos_end":[0.4812,0.05027,0.02512],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.20115,"object_to_goal_dist_start":0.2095,"object_z_max":0.0252,"peak_contact_force":1.50959,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1966.0,"raw_peak_contact_force":11.5515,"tcp_end":[0.4749,0.08694,0.02102],"tcp_start":[0.47614,0.13178,0.03157],"tcp_to_object_dist_end":0.03743,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47452,-0.11288,0.02502],"object_pos_start":[0.4812,0.05027,0.02512],"object_to_goal_dist_end":0.04502,"object_to_goal_dist_start":0.20115,"object_z_max":0.0289,"peak_contact_force":0.73382,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2661.0,"raw_peak_contact_force":73.61928,"tcp_end":[0.49478,-0.08189,0.01993],"tcp_start":[0.4749,0.08694,0.02102],"tcp_to_object_dist_end":0.03737,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4738,-0.11367,0.02499],"object_pos_start":[0.47452,-0.11288,0.02502],"object_to_goal_dist_end":0.04479,"object_to_goal_dist_start":0.04502,"object_z_max":0.02502,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3988.0,"raw_peak_contact_force":1.40966,"tcp_end":[0.49303,0.00418,0.09308],"tcp_start":[0.49478,-0.08189,0.01993],"tcp_to_object_dist_end":0.13746,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `021f3e69028f16fb65e79b302b37775f7324e143e034cbac30fdb04ffcd99d24`; realized-scene SHA-256: `2cf7387f3e8baf02f18930263090d6f78777bdbc147b7fa30c178332e76b547b`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.54443,-0.02558,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.04443,-0.12442,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.54443,-0.02558,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.79355,"average_solve_count":155.0,"average_success_count":155.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.17487,"push_1.push_distance":0.10384,"push_1.push_speed":0.08195,"retract_1.retract_height":0.08028,"retract_1.speed":0.07577},"optimized_scores":{"best_composite_score":0.48313,"best_fitness_score":0.79313,"best_task_score":0.73639},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":985.0,"contact_point_centroid":[0.55573,-0.07604,0.05422],"force_p95":111.93536,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":130.14192,"mean_force":77.03216,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5223,-0.06021,0.02356]},{"body_a":"attachment","body_b":"push_box","contact_count":992.0,"contact_point_centroid":[0.54127,-0.06836,0.0532],"force_p95":88.98572,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":95.78935,"mean_force":52.7423,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52242,-0.05976,0.02354]},{"body_a":"world","body_b":"push_box","contact_count":1914.0,"contact_point_centroid":[0.54974,-0.11067,-0.00034],"force_p95":76.16853,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":87.3196,"mean_force":50.49014,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.522,-0.06164,0.02373]},{"body_a":"push_box","body_b":"link7","contact_count":37.0,"contact_point_centroid":[0.55081,-0.12689,0.05603],"force_p95":74.7335,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":80.8178,"mean_force":27.39902,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50756,-0.12105,0.03017]},{"body_a":"world","body_b":"push_box","contact_count":3657.0,"contact_point_centroid":[0.53518,-0.14801,-3e-05],"force_p95":0.2856,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":73.35196,"mean_force":0.40405,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50292,-0.06338,0.07276]},{"body_a":"attachment","body_b":"push_box","contact_count":59.0,"contact_point_centroid":[0.52912,-0.12364,0.06053],"force_p95":39.89798,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":65.63153,"mean_force":14.05704,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5066,-0.11776,0.03205]},{"body_a":"attachment","body_b":"push_box","contact_count":85.0,"contact_point_centroid":[0.54513,-0.00428,0.03662],"force_p95":9.6618,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.54545,"mean_force":3.39524,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.539,0.00761,0.02053]},{"body_a":"world","body_b":"push_box","contact_count":1922.0,"contact_point_centroid":[0.54452,-0.02698,-1e-05],"force_p95":0.97284,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.79059,"mean_force":0.40074,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53668,0.02975,0.024]},{"body_a":"world","body_b":"push_box","contact_count":3616.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51809,0.02558,0.16513]}],"total_contact_groups":9},"final_pose_error":0.16467,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53476,-0.14778,0.02499],"final_tcp_position":[0.50139,-0.00891,0.10683],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":130.14192,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":904.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3616.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.53817,0.05149,0.03197],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07764,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":532.0,"n_steps_budget":600.0,"object_pos_end":[0.54653,-0.03298,0.02506],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.12593,"object_to_goal_dist_start":0.13211,"object_z_max":0.02511,"peak_contact_force":1.15254,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2007.0,"raw_peak_contact_force":10.54545,"tcp_end":[0.53949,0.00376,0.02003],"tcp_start":[0.53817,0.05149,0.03197],"tcp_to_object_dist_end":0.03775,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":995.0,"n_steps_budget":1000.0,"object_pos_end":[0.53771,-0.14999,0.03113],"object_pos_start":[0.54653,-0.03298,0.02506],"object_to_goal_dist_end":0.0382,"object_to_goal_dist_start":0.12593,"object_z_max":0.03115,"peak_contact_force":110.48596,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3891.0,"raw_peak_contact_force":130.14192,"tcp_end":[0.50856,-0.12298,0.02897],"tcp_start":[0.53949,0.00376,0.02003],"tcp_to_object_dist_end":0.03979,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53476,-0.14778,0.02499],"object_pos_start":[0.53771,-0.14999,0.03113],"object_to_goal_dist_end":0.03483,"object_to_goal_dist_start":0.0382,"object_z_max":0.03393,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3753.0,"raw_peak_contact_force":80.8178,"tcp_end":[0.50139,-0.00891,0.10683],"tcp_start":[0.50856,-0.12298,0.02897],"tcp_to_object_dist_end":0.16462,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `886824c4c8b8334954c1de9b3100fb0acfdd4a04855e7e82a07b72c52723cc86`; realized-scene SHA-256: `d6f67641a3df0efca2ae6de2763dea57e4736e336d1ca3e6fe373ea0745d2d85`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.55472,-0.03508,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.05472,-0.11492,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.55472,-0.03508,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.78082,"average_solve_count":146.0,"average_success_count":146.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.21173,"push_1.push_distance":0.09402,"push_1.push_speed":0.1,"retract_1.retract_height":0.14105,"retract_1.speed":0.07631},"optimized_scores":{"best_composite_score":0.46513,"best_fitness_score":0.77513,"best_task_score":0.72297},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":763.0,"contact_point_centroid":[0.56293,-0.07863,0.05399],"force_p95":118.30665,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":133.70598,"mean_force":78.86713,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52813,-0.06337,0.0236]},{"body_a":"world","body_b":"push_box","contact_count":1499.0,"contact_point_centroid":[0.55654,-0.1119,-0.00033],"force_p95":89.3902,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":101.74888,"mean_force":50.90748,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52796,-0.06403,0.02371]},{"body_a":"attachment","body_b":"push_box","contact_count":754.0,"contact_point_centroid":[0.54699,-0.07248,0.05454],"force_p95":77.95043,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":83.25259,"mean_force":49.26842,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52794,-0.06396,0.02367]},{"body_a":"world","body_b":"push_box","contact_count":3695.0,"contact_point_centroid":[0.5357,-0.1474,-3e-05],"force_p95":0.25192,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":76.83045,"mean_force":0.39397,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50426,-0.06142,0.07272]},{"body_a":"push_box","body_b":"link7","contact_count":35.0,"contact_point_centroid":[0.55251,-0.12323,0.05636],"force_p95":68.6002,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":72.69698,"mean_force":24.76688,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50929,-0.11857,0.0304]},{"body_a":"attachment","body_b":"push_box","contact_count":56.0,"contact_point_centroid":[0.52935,-0.12126,0.05961],"force_p95":46.24903,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":60.07846,"mean_force":12.64353,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50826,-0.11513,0.03238]},{"body_a":"attachment","body_b":"push_box","contact_count":78.0,"contact_point_centroid":[0.5553,-0.01348,0.03762],"force_p95":10.16049,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.52698,"mean_force":3.73071,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54914,-0.00161,0.02033]},{"body_a":"world","body_b":"push_box","contact_count":1978.0,"contact_point_centroid":[0.55472,-0.03622,-1e-05],"force_p95":1.02306,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.75611,"mean_force":0.39846,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54659,0.02074,0.02373]},{"body_a":"world","body_b":"push_box","contact_count":3644.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52296,0.02111,0.16506]}],"total_contact_groups":9},"final_pose_error":0.1623,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53515,-0.14716,0.02499],"final_tcp_position":[0.50238,-0.00653,0.10718],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55472,-0.03508,0.025]},"peak_contact_force":133.70598,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":911.0,"n_steps_budget":1000.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.025],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3644.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.54794,0.04249,0.03178],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07816,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.55769,-0.04237,0.02486],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.12211,"object_to_goal_dist_start":0.12728,"object_z_max":0.02513,"peak_contact_force":7.50497,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2056.0,"raw_peak_contact_force":15.52698,"tcp_end":[0.5497,-0.00564,0.01983],"tcp_start":[0.54794,0.04249,0.03178],"tcp_to_object_dist_end":0.03793,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":776.0,"n_steps_budget":870.0,"object_pos_end":[0.54079,-0.14613,0.03105],"object_pos_start":[0.55769,-0.04237,0.02486],"object_to_goal_dist_end":0.04141,"object_to_goal_dist_start":0.12211,"object_z_max":0.03105,"peak_contact_force":118.21416,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3016.0,"raw_peak_contact_force":133.70598,"tcp_end":[0.51027,-0.1203,0.02933],"tcp_start":[0.5497,-0.00564,0.01983],"tcp_to_object_dist_end":0.04001,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53515,-0.14716,0.02499],"object_pos_start":[0.54079,-0.14613,0.03105],"object_to_goal_dist_end":0.03526,"object_to_goal_dist_start":0.04141,"object_z_max":0.03402,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3786.0,"raw_peak_contact_force":76.83045,"tcp_end":[0.50238,-0.00653,0.10718],"tcp_start":[0.51027,-0.1203,0.02933],"tcp_to_object_dist_end":0.16614,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```