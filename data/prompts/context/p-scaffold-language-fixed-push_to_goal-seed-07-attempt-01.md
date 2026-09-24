## Search State

- **Seed**: 7
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | 0.2838 | 0.69 | ❌ rejected |
| 0 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | 0.2751 | 0.69 | ✅ accepted |

**Proposal policy**: task_score is 0.69 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.284) — your mutation base

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

- **Composite score**: 0.284
- **task_score** (E): 0.689
- **fitness_score**: 0.644  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2872 |
| contact_1 | 1.00 | 1.00 | 0.0534 |
| push_1 | 1.00 | 1.00 | 0.1268 |
| retract_1 | 0.00 | 1.00 | 0.1242 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.508, 0.106, 0.037) | (0.513, 0.027, 0.025)→(0.513, 0.027, 0.025) | 0.180→0.180 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / step_budget | (0.508, 0.106, 0.037)→(0.508, 0.055, 0.021) | (0.513, 0.027, 0.025)→(0.515, 0.018, 0.025) | 0.180→0.172 | 1.00 / 3.667 | 5.590 | 11.392 |
| push_1 | push | 1.00 / step_budget | (0.508, 0.055, 0.021)→(0.501, -0.070, 0.024) | (0.515, 0.018, 0.025)→(0.512, -0.104, 0.028) | 0.172→0.058 | 1.00 / 4.000 | 53.136 | 87.120 |
| retract_1 | retract | 0.00 / step_budget | (0.501, -0.070, 0.024)→(0.497, 0.039, 0.083) | (0.512, -0.104, 0.028)→(0.509, -0.100, 0.025) | 0.058→0.057 | 1.00 / 4.000 | 0.245 | 43.615 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.855
- lateral_force_integral: None
- approach_alignment: 0.489
- goal_progress: 0.747
- terminal_score: 0.747
- phase_score: 0.816
- phase_breakdown.push_score: 0.789
- phase_breakdown.approach_score: 0.819
- phase_breakdown.contact_score: 0.858

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.788
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.747
- **Median Q (composite search score)**: 0.215
- **K-run variance**: 0.0104
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.505


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.59884,"average_solve_count":172.0,"average_success_count":172.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.0955,"contact_1.speed":0.0456,"push_1.push_depth":0.09799,"push_1.push_distance":0.10113,"push_1.push_speed":0.07486,"retract_1.speed":0.06078},"optimized_scores":{"best_composite_score":0.21465,"best_fitness_score":0.57465,"best_task_score":0.65745},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1850.0,"contact_point_centroid":[0.52212,-0.04664,-0.00019],"force_p95":51.07677,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":72.76429,"mean_force":33.3281,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5046,0.00873,0.02212]},{"body_a":"push_box","body_b":"link7","contact_count":982.0,"contact_point_centroid":[0.53101,-0.00543,0.05474],"force_p95":54.06288,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":59.23992,"mean_force":46.76428,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50468,0.01125,0.02195]},{"body_a":"attachment","body_b":"push_box","contact_count":989.0,"contact_point_centroid":[0.52378,0.00146,0.05233],"force_p95":51.36601,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":53.76149,"mean_force":39.25762,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50472,0.01171,0.02194]},{"body_a":"push_box","body_b":"link7","contact_count":22.0,"contact_point_centroid":[0.52881,-0.07169,0.05482],"force_p95":41.7509,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":42.51986,"mean_force":19.38122,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49977,-0.04777,0.0237]},{"body_a":"attachment","body_b":"push_box","contact_count":40.0,"contact_point_centroid":[0.52028,-0.05574,0.05573],"force_p95":32.09974,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":34.42125,"mean_force":9.06607,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49902,-0.04557,0.02417]},{"body_a":"world","body_b":"push_box","contact_count":3870.0,"contact_point_centroid":[0.50734,-0.0831,-1e-05],"force_p95":0.24532,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":24.92443,"mean_force":0.29225,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49643,0.00814,0.0551]},{"body_a":"attachment","body_b":"push_box","contact_count":118.0,"contact_point_centroid":[0.51481,0.06846,0.0325],"force_p95":8.91488,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.92205,"mean_force":4.11025,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50994,0.08032,0.02194]},{"body_a":"world","body_b":"push_box","contact_count":2399.0,"contact_point_centroid":[0.51516,0.04634,-1e-05],"force_p95":2.03779,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.4336,"mean_force":0.4493,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50824,0.10113,0.02757]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50355,0.07659,0.17864]}],"total_contact_groups":9},"final_pose_error":0.1123,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50714,-0.08247,0.02499],"final_tcp_position":[0.49645,0.05746,0.08648],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":72.76429,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.50998,0.12526,0.03839],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07891,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":656.0,"n_steps_budget":750.0,"object_pos_end":[0.5172,0.03908,0.0249],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.18986,"object_to_goal_dist_start":0.19823,"object_z_max":0.02512,"peak_contact_force":8.46913,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2517.0,"raw_peak_contact_force":12.92205,"tcp_end":[0.51045,0.07578,0.02083],"tcp_start":[0.50998,0.12526,0.03839],"tcp_to_object_dist_end":0.03754,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":997.0,"n_steps_budget":1000.0,"object_pos_end":[0.50892,-0.08648,0.02914],"object_pos_start":[0.5172,0.03908,0.0249],"object_to_goal_dist_end":0.06428,"object_to_goal_dist_start":0.18986,"object_z_max":0.02919,"peak_contact_force":44.20666,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3821.0,"raw_peak_contact_force":72.76429,"tcp_end":[0.50043,-0.04867,0.02358],"tcp_start":[0.51045,0.07578,0.02083],"tcp_to_object_dist_end":0.03915,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50714,-0.08247,0.02499],"object_pos_start":[0.50892,-0.08648,0.02914],"object_to_goal_dist_end":0.0679,"object_to_goal_dist_start":0.06428,"object_z_max":0.02914,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3932.0,"raw_peak_contact_force":42.51986,"tcp_end":[0.49645,0.05746,0.08648],"tcp_start":[0.50043,-0.04867,0.02358],"tcp_to_object_dist_end":0.15322,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.43316,"average_solve_count":187.0,"average_success_count":187.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.09715,"contact_1.speed":0.04449,"push_1.push_depth":0.09934,"push_1.push_distance":0.12588,"push_1.push_speed":0.06962,"retract_1.speed":0.04581},"optimized_scores":{"best_composite_score":0.20838,"best_fitness_score":0.56838,"best_task_score":0.66246},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1235.0,"contact_point_centroid":[0.49112,-0.03119,-9e-05],"force_p95":49.21557,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":58.90892,"mean_force":12.63488,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48469,0.01647,0.01963]},{"body_a":"attachment","body_b":"push_box","contact_count":788.0,"contact_point_centroid":[0.49216,0.01278,0.0344],"force_p95":34.63474,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":41.62975,"mean_force":13.22712,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48354,0.02417,0.0197]},{"body_a":"push_box","body_b":"link7","contact_count":348.0,"contact_point_centroid":[0.50681,0.03687,0.05116],"force_p95":34.51346,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":36.16015,"mean_force":24.29756,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47822,0.06006,0.0201]},{"body_a":"attachment","body_b":"push_box","contact_count":134.0,"contact_point_centroid":[0.47769,0.07916,0.02796],"force_p95":10.92654,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.22557,"mean_force":4.37839,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47461,0.09099,0.02287]},{"body_a":"world","body_b":"push_box","contact_count":2500.0,"contact_point_centroid":[0.47962,0.05735,-1e-05],"force_p95":2.56984,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.83712,"mean_force":0.48069,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47354,0.11098,0.02914]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.49299,-0.05478,0.02095],"force_p95":6.74339,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.74339,"mean_force":6.74339,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49464,-0.04293,0.02005]},{"body_a":"world","body_b":"push_box","contact_count":3991.0,"contact_point_centroid":[0.48952,-0.0801,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.97008,"mean_force":0.24764,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49222,0.00789,0.04981]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48502,0.08112,0.18019]}],"total_contact_groups":8},"final_pose_error":0.11722,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.4895,-0.08007,0.02499],"final_tcp_position":[0.4936,0.05509,0.0815],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":58.90892,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.47582,0.13516,0.04053],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07832,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":679.0,"n_steps_budget":780.0,"object_pos_end":[0.48141,0.0496,0.02493],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.20047,"object_to_goal_dist_start":0.2095,"object_z_max":0.0251,"peak_contact_force":6.61524,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2634.0,"raw_peak_contact_force":12.22557,"tcp_end":[0.47496,0.0863,0.02148],"tcp_start":[0.47582,0.13516,0.04053],"tcp_to_object_dist_end":0.03742,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":861.0,"n_steps_budget":1000.0,"object_pos_end":[0.48958,-0.07956,0.02498],"object_pos_start":[0.48141,0.0496,0.02493],"object_to_goal_dist_end":0.07121,"object_to_goal_dist_start":0.20047,"object_z_max":0.02869,"peak_contact_force":6.87396,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2371.0,"raw_peak_contact_force":58.90892,"tcp_end":[0.49464,-0.04293,0.02005],"tcp_start":[0.47496,0.0863,0.02148],"tcp_to_object_dist_end":0.0373,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4895,-0.08007,0.02499],"object_pos_start":[0.48958,-0.07956,0.02498],"object_to_goal_dist_end":0.07072,"object_to_goal_dist_start":0.07121,"object_z_max":0.02501,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3992.0,"raw_peak_contact_force":6.74339,"tcp_end":[0.4936,0.05509,0.0815],"tcp_start":[0.49464,-0.04293,0.02005],"tcp_to_object_dist_end":0.14655,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.45789,"average_solve_count":190.0,"average_success_count":190.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.09634,"contact_1.speed":0.03783,"push_1.push_depth":0.09992,"push_1.push_distance":0.1369,"push_1.push_speed":0.07837,"retract_1.speed":0.04055},"optimized_scores":{"best_composite_score":0.42825,"best_fitness_score":0.78825,"best_task_score":0.74711},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":992.0,"contact_point_centroid":[0.55637,-0.0751,0.05396],"force_p95":110.09432,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":129.68716,"mean_force":76.07484,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52268,-0.05855,0.0234]},{"body_a":"attachment","body_b":"push_box","contact_count":991.0,"contact_point_centroid":[0.54177,-0.06724,0.05348],"force_p95":86.41102,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":90.94642,"mean_force":50.85352,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52269,-0.05857,0.02341]},{"body_a":"world","body_b":"push_box","contact_count":1923.0,"contact_point_centroid":[0.55038,-0.10959,-0.00035],"force_p95":73.27737,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":85.79934,"mean_force":49.71651,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52235,-0.06004,0.02356]},{"body_a":"push_box","body_b":"link7","contact_count":62.0,"contact_point_centroid":[0.54845,-0.12597,0.05661],"force_p95":74.42492,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":81.58112,"mean_force":30.92309,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5079,-0.11375,0.02969]},{"body_a":"world","body_b":"push_box","contact_count":3635.0,"contact_point_centroid":[0.53177,-0.13781,-3e-05],"force_p95":0.26558,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":78.27192,"mean_force":0.59833,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50279,-0.04877,0.0552]},{"body_a":"attachment","body_b":"push_box","contact_count":74.0,"contact_point_centroid":[0.53188,-0.11668,0.06074],"force_p95":55.11136,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":66.56197,"mean_force":19.92838,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50741,-0.1117,0.03004]},{"body_a":"attachment","body_b":"push_box","contact_count":150.0,"contact_point_centroid":[0.54484,-0.00488,0.03535],"force_p95":7.09317,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.02708,"mean_force":2.86416,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53912,0.00701,0.02043]},{"body_a":"world","body_b":"push_box","contact_count":3073.0,"contact_point_centroid":[0.54475,-0.02726,-1e-05],"force_p95":1.31676,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.53912,"mean_force":0.39019,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.5367,0.03031,0.02385]},{"body_a":"world","body_b":"push_box","contact_count":3740.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51728,0.04388,0.17037]}],"total_contact_groups":9},"final_pose_error":0.1613,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53111,-0.13781,0.02499],"final_tcp_position":[0.50106,0.00491,0.07955],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":129.68716,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":935.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3740.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.53808,0.0561,0.03253],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08227,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":852.0,"n_steps_budget":960.0,"object_pos_end":[0.54731,-0.0344,0.02503],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.1249,"object_to_goal_dist_start":0.13211,"object_z_max":0.02508,"peak_contact_force":1.68603,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3223.0,"raw_peak_contact_force":9.02708,"tcp_end":[0.53967,0.0024,0.01983],"tcp_start":[0.53808,0.0561,0.03253],"tcp_to_object_dist_end":0.03795,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53686,-0.14633,0.03105],"object_pos_start":[0.54731,-0.0344,0.02503],"object_to_goal_dist_end":0.03754,"object_to_goal_dist_start":0.1249,"object_z_max":0.03108,"peak_contact_force":108.32658,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3906.0,"raw_peak_contact_force":129.68716,"tcp_end":[0.50905,-0.11834,0.02879],"tcp_start":[0.53967,0.0024,0.01983],"tcp_to_object_dist_end":0.03952,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53111,-0.13781,0.02499],"object_pos_start":[0.53686,-0.14633,0.03105],"object_to_goal_dist_end":0.03341,"object_to_goal_dist_start":0.03754,"object_z_max":0.03477,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3771.0,"raw_peak_contact_force":81.58112,"tcp_end":[0.50106,0.00491,0.07955],"tcp_start":[0.50905,-0.11834,0.02879],"tcp_to_object_dist_end":0.15572,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```