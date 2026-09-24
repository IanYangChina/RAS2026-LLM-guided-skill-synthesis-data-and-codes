## Search State

- **Seed**: 7
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | 0.2629 | 0.68 | ❌ rejected |
| 9 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | 0.2670 | 0.68 | ❌ rejected |
| 8 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | 0.2775 | 0.69 | ❌ rejected |
| 7 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | 0.2748 | 0.69 | ❌ rejected |
| 6 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | 0.2819 | 0.69 | ❌ rejected |

**Proposal policy**: task_score is 0.68 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `c8d09cd43835becf8e5eb4413394fad8627e4bf404e9e7726e9f380b60e09752`
- Frozen object start: [0.51501145599256, 0.047665656116349056, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.51501145599256, 0.047665656116349056, 0.025)
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
  frozen_object_start: [0.515, 0.0477, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.51501145599256, 0.047665656116349056, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [-0.015, -0.1977, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: c8d09cd43835becf8e5eb4413394fad8627e4bf404e9e7726e9f380b60e09752

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

## Current Skill (Q=0.263) — your mutation base

```yaml
skill: push_to_goal
phases:
- id: approach_1
  type: approach
  generator: arc_cartesian
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
  control: admittance_control
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
  control: position_control
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

- **Composite score**: 0.263
- **task_score** (E): 0.683
- **fitness_score**: 0.623  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2751 |
| contact_1 | 1.00 | 1.00 | 0.0585 |
| push_1 | 1.00 | 0.67 | 0.1263 |
| retract_1 | 0.00 | 1.00 | 0.1242 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.507, 0.105, 0.050) | (0.513, 0.027, 0.025)→(0.513, 0.027, 0.025) | 0.180→0.180 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / step_budget | (0.507, 0.105, 0.050)→(0.508, 0.054, 0.021) | (0.513, 0.027, 0.025)→(0.515, 0.018, 0.025) | 0.180→0.171 | 1.00 / 3.667 | 5.188 | 11.797 |
| push_1 | push | 1.00 / step_budget | (0.508, 0.054, 0.021)→(0.502, -0.070, 0.024) | (0.515, 0.018, 0.025)→(0.511, -0.103, 0.029) | 0.171→0.058 | 0.67 / 2.667 | 54.915 | 83.834 |
| retract_1 | retract | 0.00 / step_budget | (0.502, -0.070, 0.024)→(0.497, 0.039, 0.083) | (0.511, -0.103, 0.029)→(0.508, -0.099, 0.025) | 0.058→0.058 | 1.00 / 4.000 | 0.245 | 47.486 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.836
- lateral_force_integral: None
- approach_alignment: 0.485
- goal_progress: 0.740
- terminal_score: 0.740
- phase_score: 0.790
- phase_breakdown.push_score: 0.773
- phase_breakdown.approach_score: 0.733
- phase_breakdown.contact_score: 0.857

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.770
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.740
- **Median Q (composite search score)**: 0.197
- **K-run variance**: 0.0109
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.369


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `75e2389a1a667086aa2b9c0de482ff37adf5571150b90a83772692baadf8b52e`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `154c216c563de6b8ee153943e5b668ca6d0c7dfd9253696b060f91a67dca06ec`; realized-scene SHA-256: `c8d09cd43835becf8e5eb4413394fad8627e4bf404e9e7726e9f380b60e09752`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51501,0.04767,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.01501,-0.19767,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.51501,0.04767,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.17757,"average_solve_count":214.0,"average_success_count":214.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.05828,"contact_1.speed":0.03791,"push_1.push_depth":0.09841,"push_1.push_distance":0.05433,"push_1.push_speed":0.07519,"retract_1.speed":0.06069},"optimized_scores":{"best_composite_score":0.18116,"best_fitness_score":0.54116,"best_task_score":0.65209},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1786.0,"contact_point_centroid":[0.5235,-0.04857,-0.00021],"force_p95":50.79377,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":69.52587,"mean_force":35.1727,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50465,0.00621,0.0227]},{"body_a":"push_box","body_b":"link7","contact_count":961.0,"contact_point_centroid":[0.53148,-0.00724,0.0551],"force_p95":58.11259,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":63.27405,"mean_force":48.86215,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50473,0.00907,0.02249]},{"body_a":"attachment","body_b":"push_box","contact_count":981.0,"contact_point_centroid":[0.52365,0.00025,0.05203],"force_p95":55.93259,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":60.29066,"mean_force":40.04837,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50483,0.01039,0.02247]},{"body_a":"push_box","body_b":"link7","contact_count":26.0,"contact_point_centroid":[0.53165,-0.07171,0.05485],"force_p95":50.97705,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":55.50257,"mean_force":25.15284,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50056,-0.04793,0.02461]},{"body_a":"attachment","body_b":"push_box","contact_count":48.0,"contact_point_centroid":[0.52138,-0.05503,0.05618],"force_p95":39.35602,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":44.33542,"mean_force":11.11159,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49974,-0.04534,0.02523]},{"body_a":"world","body_b":"push_box","contact_count":3854.0,"contact_point_centroid":[0.50977,-0.08238,-2e-05],"force_p95":0.24613,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":41.69974,"mean_force":0.31717,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49704,0.00818,0.0559]},{"body_a":"attachment","body_b":"push_box","contact_count":182.0,"contact_point_centroid":[0.51551,0.068,0.03801],"force_p95":9.79729,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.39999,"mean_force":5.82481,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50989,0.07984,0.02573]},{"body_a":"world","body_b":"push_box","contact_count":3295.0,"contact_point_centroid":[0.51483,0.04588,-1e-05],"force_p95":3.40659,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.79592,"mean_force":0.56883,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50785,0.09777,0.04006]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50296,0.07219,0.19036]}],"total_contact_groups":9},"final_pose_error":0.11191,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50946,-0.08168,0.02499],"final_tcp_position":[0.49686,0.05754,0.08703],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":69.52587,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.50882,0.12235,0.06352],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08427,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":895.0,"n_steps_budget":1000.0,"object_pos_end":[0.51677,0.03814,0.02495],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.18888,"object_to_goal_dist_start":0.19823,"object_z_max":0.02512,"peak_contact_force":7.97478,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3477.0,"raw_peak_contact_force":12.39999,"tcp_end":[0.51055,0.07485,0.0218],"tcp_start":[0.50882,0.12235,0.06352],"tcp_to_object_dist_end":0.03737,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":984.0,"n_steps_budget":1000.0,"object_pos_end":[0.51185,-0.08645,0.02949],"object_pos_start":[0.51677,0.03814,0.02495],"object_to_goal_dist_end":0.0648,"object_to_goal_dist_start":0.18888,"object_z_max":0.02951,"peak_contact_force":54.71685,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3728.0,"raw_peak_contact_force":69.52587,"tcp_end":[0.50128,-0.04915,0.02438],"tcp_start":[0.51055,0.07485,0.0218],"tcp_to_object_dist_end":0.03911,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50946,-0.08168,0.02499],"object_pos_start":[0.51185,-0.08645,0.02949],"object_to_goal_dist_end":0.06897,"object_to_goal_dist_start":0.0648,"object_z_max":0.02949,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3928.0,"raw_peak_contact_force":55.50257,"tcp_end":[0.49686,0.05754,0.08703],"tcp_start":[0.50128,-0.04915,0.02438],"tcp_to_object_dist_end":0.15294,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `4d55d9375783bea830660bf0a13dfc76a97a0d4f5645e7ebcc1ef7143776d0b7`; realized-scene SHA-256: `f3b8ea82cefd9504be10e2d47c49094a836a703404c06bdee3b01a27a59bf7be`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47924,0.05847,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.02076,-0.20847,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.47924,0.05847,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.07473,"average_solve_count":281.0,"average_success_count":281.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.07751,"contact_1.speed":0.02968,"push_1.push_depth":0.09968,"push_1.push_distance":0.03396,"push_1.push_speed":0.02857,"retract_1.speed":0.01786},"optimized_scores":{"best_composite_score":0.19733,"best_fitness_score":0.55733,"best_task_score":0.65689},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1484.0,"contact_point_centroid":[0.4889,-0.03152,-9e-05],"force_p95":46.41229,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":51.35561,"mean_force":11.7815,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48459,0.01587,0.01962]},{"body_a":"attachment","body_b":"push_box","contact_count":903.0,"contact_point_centroid":[0.49201,0.01232,0.03473],"force_p95":32.60836,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":36.57374,"mean_force":12.85012,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48342,0.02368,0.01967]},{"body_a":"push_box","body_b":"link7","contact_count":413.0,"contact_point_centroid":[0.50631,0.03563,0.05137],"force_p95":33.46287,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":35.18439,"mean_force":23.53658,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47824,0.0587,0.02004]},{"body_a":"attachment","body_b":"push_box","contact_count":221.0,"contact_point_centroid":[0.47787,0.07872,0.02905],"force_p95":8.86369,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.73519,"mean_force":4.36591,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47468,0.09055,0.02385]},{"body_a":"world","body_b":"push_box","contact_count":3704.0,"contact_point_centroid":[0.47959,0.057,-1e-05],"force_p95":2.30874,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.78673,"mean_force":0.50294,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47369,0.10875,0.03222]},{"body_a":"world","body_b":"push_box","contact_count":3994.0,"contact_point_centroid":[0.48363,-0.08002,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.75825,"mean_force":0.24599,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49223,0.00675,0.04962]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48523,0.07982,0.18344]}],"total_contact_groups":7},"final_pose_error":0.11845,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.48363,-0.08001,0.02499],"final_tcp_position":[0.49361,0.05388,0.08107],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":51.35561,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.47602,0.13421,0.04774],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07915,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":998.0,"n_steps_budget":1000.0,"object_pos_end":[0.48158,0.04882,0.02497],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.19967,"object_to_goal_dist_start":0.2095,"object_z_max":0.02505,"peak_contact_force":5.96743,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3925.0,"raw_peak_contact_force":10.73519,"tcp_end":[0.47501,0.0854,0.02153],"tcp_start":[0.47602,0.13421,0.04774],"tcp_to_object_dist_end":0.03733,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":988.0,"n_steps_budget":1000.0,"object_pos_end":[0.48398,-0.07941,0.02507],"object_pos_start":[0.48158,0.04882,0.02497],"object_to_goal_dist_end":0.07238,"object_to_goal_dist_start":0.19967,"object_z_max":0.02884,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2800.0,"raw_peak_contact_force":51.35561,"tcp_end":[0.49468,-0.04407,0.02006],"tcp_start":[0.47501,0.0854,0.02153],"tcp_to_object_dist_end":0.03726,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48363,-0.08001,0.02499],"object_pos_start":[0.48398,-0.07941,0.02507],"object_to_goal_dist_end":0.07188,"object_to_goal_dist_start":0.07238,"object_z_max":0.02507,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3994.0,"raw_peak_contact_force":0.75825,"tcp_end":[0.49361,0.05388,0.08107],"tcp_start":[0.49468,-0.04407,0.02006],"tcp_to_object_dist_end":0.1455,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `0a9238470f4497c7aa88b149b7cee960f9853513db10bf496723f5ea1d3a6043`; realized-scene SHA-256: `2cf7387f3e8baf02f18930263090d6f78777bdbc147b7fa30c178332e76b547b`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.54443,-0.02558,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.04443,-0.12442,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.54443,-0.02558,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.11017,"average_solve_count":236.0,"average_success_count":236.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.03936,"contact_1.speed":0.04933,"push_1.push_depth":0.0967,"push_1.push_distance":0.04327,"push_1.push_speed":0.08337,"retract_1.speed":0.05116},"optimized_scores":{"best_composite_score":0.41018,"best_fitness_score":0.77018,"best_task_score":0.73981},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":924.0,"contact_point_centroid":[0.55565,-0.07329,0.05422],"force_p95":111.27277,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":130.62037,"mean_force":75.58928,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52219,-0.05743,0.02362]},{"body_a":"attachment","body_b":"push_box","contact_count":932.0,"contact_point_centroid":[0.54099,-0.06562,0.05305],"force_p95":87.80808,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":94.06744,"mean_force":51.69709,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52234,-0.05691,0.02359]},{"body_a":"push_box","body_b":"link7","contact_count":62.0,"contact_point_centroid":[0.54808,-0.12361,0.05666],"force_p95":77.6796,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":86.19574,"mean_force":31.63331,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50743,-0.1116,0.02984]},{"body_a":"world","body_b":"push_box","contact_count":1830.0,"contact_point_centroid":[0.54914,-0.10669,-0.00033],"force_p95":75.53245,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":85.91105,"mean_force":48.85422,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52214,-0.05775,0.02368]},{"body_a":"world","body_b":"push_box","contact_count":3657.0,"contact_point_centroid":[0.53164,-0.1354,-3e-05],"force_p95":0.27285,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":77.90952,"mean_force":0.60487,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50242,-0.04699,0.05541]},{"body_a":"attachment","body_b":"push_box","contact_count":74.0,"contact_point_centroid":[0.53133,-0.11445,0.06055],"force_p95":54.99937,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":69.85001,"mean_force":20.23783,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50693,-0.10949,0.03022]},{"body_a":"attachment","body_b":"push_box","contact_count":108.0,"contact_point_centroid":[0.54441,-0.0045,0.03538],"force_p95":9.13174,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.25725,"mean_force":3.86476,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53902,0.00738,0.02129]},{"body_a":"world","body_b":"push_box","contact_count":2554.0,"contact_point_centroid":[0.54457,-0.0267,-1e-05],"force_p95":1.66958,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.78214,"mean_force":0.41131,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53626,0.03127,0.02727]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51674,0.04354,0.17358]}],"total_contact_groups":9},"final_pose_error":0.15955,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53102,-0.13519,0.02499],"final_tcp_position":[0.50077,0.00667,0.07991],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":130.62037,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.5372,0.05709,0.03845],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08407,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":693.0,"n_steps_budget":780.0,"object_pos_end":[0.54687,-0.0337,0.02505],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.12539,"object_to_goal_dist_start":0.13211,"object_z_max":0.02508,"peak_contact_force":1.62241,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2662.0,"raw_peak_contact_force":12.25725,"tcp_end":[0.53958,0.00319,0.02032],"tcp_start":[0.5372,0.05709,0.03845],"tcp_to_object_dist_end":0.03791,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":936.0,"n_steps_budget":1000.0,"object_pos_end":[0.53659,-0.14404,0.03104],"object_pos_start":[0.54687,-0.0337,0.02505],"object_to_goal_dist_end":0.03756,"object_to_goal_dist_start":0.12539,"object_z_max":0.03114,"peak_contact_force":110.02898,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3686.0,"raw_peak_contact_force":130.62037,"tcp_end":[0.50856,-0.11624,0.0289],"tcp_start":[0.53958,0.00319,0.02032],"tcp_to_object_dist_end":0.03953,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53102,-0.13519,0.02499],"object_pos_start":[0.53659,-0.14404,0.03104],"object_to_goal_dist_end":0.03437,"object_to_goal_dist_start":0.03756,"object_z_max":0.03484,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3793.0,"raw_peak_contact_force":86.19574,"tcp_end":[0.50077,0.00667,0.07991],"tcp_start":[0.50856,-0.11624,0.0289],"tcp_to_object_dist_end":0.15509,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```