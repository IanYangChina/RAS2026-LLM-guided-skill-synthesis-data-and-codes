## Search State

- **Seed**: 9
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | force_threshold_switch | admittance_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 5 | 0.6651 | 0.80 | ❌ rejected |
| 2 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.3249 | 0.44 | ❌ rejected |
| 1 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | force_threshold_switch | admittance_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 5 | 0.7669 | 0.72 | ❌ rejected |
| 0 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | force_threshold_switch | admittance_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 5 | 0.6768 | 0.81 | ✅ accepted |

**Proposal policy**: task_score is 0.80 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `2cf7387f3e8baf02f18930263090d6f78777bdbc147b7fa30c178332e76b547b`
- Frozen object start: [0.5444299044764102, -0.025581934909493356, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.5444299044764102, -0.025581934909493356, 0.025)
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
  frozen_object_start: [0.5444, -0.0256, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.5444299044764102, -0.025581934909493356, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [-0.0444, -0.1244, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: 2cf7387f3e8baf02f18930263090d6f78777bdbc147b7fa30c178332e76b547b

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

## Current Skill (Q=0.665) — your mutation base

```yaml
skill: push_to_goal
phases:
- id: approach_1
  type: approach
  generator: arc_cartesian
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
  control: admittance_control
  termination: force_exceeded
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
  termination: time_limit
  parameters:
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

- **Composite score**: 0.665
- **task_score** (E): 0.803
- **fitness_score**: 0.753  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.222
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.310

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2785 |
| contact_1 | 0.67 | 1.00 | 0.0419 |
| push_1 | 1.00 | 1.00 | 0.1349 |
| retract_1 | 0.00 | 1.00 | 0.1338 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.513, 0.061, 0.033) | (0.518, -0.020, 0.025)→(0.518, -0.020, 0.025) | 0.139→0.139 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 0.67 / force_exceeded | (0.513, 0.061, 0.033)→(0.513, 0.021, 0.022) | (0.518, -0.020, 0.025)→(0.518, -0.020, 0.025) | 0.139→0.139 | 1.00 / 4.667 | 14.191 | 0.245 |
| push_1 | push | 1.00 / time_limit | (0.513, 0.021, 0.022)→(0.503, -0.109, 0.026) | (0.518, -0.020, 0.025)→(0.522, -0.140, 0.029) | 0.139→0.028 | 1.00 / 3.333 | 72.347 | 98.740 |
| retract_1 | retract | 0.00 / step_budget | (0.503, -0.109, 0.026)→(0.497, 0.014, 0.080) | (0.522, -0.140, 0.029)→(0.518, -0.135, 0.025) | 0.028→0.026 | 1.00 / 4.000 | 0.245 | 58.474 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.818
- lateral_force_integral: None
- approach_alignment: 0.477
- goal_progress: 0.746
- terminal_score: 0.746
- phase_score: 0.747
- phase_breakdown.approach_score: 0.821
- phase_breakdown.push_score: 0.712
- phase_breakdown.contact_score: 0.757

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.776
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.939
- **Median Q (composite search score)**: 0.760
- **K-run variance**: 0.0199
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Parameters at upper bound**: push_1.push_speed
- **Final σ (mean)**: 0.486


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `327b95871eb659cd41b4cf66bc0b4dfb3b240662e8501854b46ee2b8b86a04c5`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `5ffd2bb280d1d50ec9ffd23c1ed75abf73d645c1d10372a9b5bb6e9fac6e0bf8`; realized-scene SHA-256: `2cf7387f3e8baf02f18930263090d6f78777bdbc147b7fa30c178332e76b547b`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.54443,-0.02558,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.04443,-0.12442,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.54443,-0.02558,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.47429,"average_solve_count":175.0,"average_success_count":175.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.27392,"contact_1.speed":0.04709,"push_1.push_speed":0.08405,"retract_1.retract_height":0.14026,"retract_1.speed":0.03078},"optimized_scores":{"best_composite_score":0.76987,"best_fitness_score":0.74654,"best_task_score":0.74583},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":967.0,"contact_point_centroid":[0.55375,-0.06481,0.05434],"force_p95":108.28873,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":129.27219,"mean_force":69.74195,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52166,-0.04863,0.02327]},{"body_a":"attachment","body_b":"push_box","contact_count":982.0,"contact_point_centroid":[0.54021,-0.05671,0.05257],"force_p95":87.99383,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":94.37951,"mean_force":48.51119,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52191,-0.04772,0.02323]},{"body_a":"world","body_b":"push_box","contact_count":1914.0,"contact_point_centroid":[0.54701,-0.09858,-0.0003],"force_p95":73.60345,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":87.50177,"mean_force":45.13037,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52173,-0.04871,0.02336]},{"body_a":"push_box","body_b":"link7","contact_count":62.0,"contact_point_centroid":[0.5488,-0.1175,0.05591],"force_p95":80.07503,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":86.5381,"mean_force":32.93136,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5071,-0.106,0.02967]},{"body_a":"world","body_b":"push_box","contact_count":3637.0,"contact_point_centroid":[0.52941,-0.13264,-3e-05],"force_p95":0.28933,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":73.81085,"mean_force":0.59187,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50211,-0.04213,0.05555]},{"body_a":"attachment","body_b":"push_box","contact_count":78.0,"contact_point_centroid":[0.5308,-0.10881,0.06039],"force_p95":59.28535,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":70.36901,"mean_force":20.59229,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5065,-0.10352,0.03013]},{"body_a":"world","body_b":"push_box","contact_count":3720.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51729,0.04386,0.17039]},{"body_a":"world","body_b":"push_box","contact_count":2308.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53649,0.03315,0.02425]}],"total_contact_groups":8},"final_pose_error":0.15601,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52868,-0.13254,0.02499],"final_tcp_position":[0.50055,0.0105,0.08015],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":129.27219,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":930.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3720.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.53811,0.05607,0.03239],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08223,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":577.0,"n_steps_budget":780.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.02499,"peak_contact_force":24.56147,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2308.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.53855,0.0114,0.02095],"tcp_start":[0.53811,0.05607,0.03239],"tcp_to_object_dist_end":0.03766,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":992.0,"n_steps_budget":1000.0,"object_pos_end":[0.53475,-0.13941,0.0311],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.03684,"object_to_goal_dist_start":0.13211,"object_z_max":0.03109,"peak_contact_force":108.71904,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3863.0,"raw_peak_contact_force":129.27219,"tcp_end":[0.50817,-0.11054,0.02866],"tcp_start":[0.53855,0.0114,0.02095],"tcp_to_object_dist_end":0.03932,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52868,-0.13254,0.02499],"object_pos_start":[0.53475,-0.13941,0.0311],"object_to_goal_dist_end":0.03358,"object_to_goal_dist_start":0.03684,"object_z_max":0.03491,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3777.0,"raw_peak_contact_force":86.5381,"tcp_end":[0.50055,0.0105,0.08015],"tcp_start":[0.50817,-0.11054,0.02866],"tcp_to_object_dist_end":0.15587,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `e094d2c5a71c8b89ef1fa30d7ce553b9c4ed64cd3fbca90620c3ede94e719cec`; realized-scene SHA-256: `d6f67641a3df0efca2ae6de2763dea57e4736e336d1ca3e6fe373ea0745d2d85`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.55472,-0.03508,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.05472,-0.11492,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.55472,-0.03508,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.61176,"average_solve_count":170.0,"average_success_count":170.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.27491,"contact_1.speed":0.0314,"push_1.push_speed":0.08227,"retract_1.retract_height":0.13806,"retract_1.speed":0.06888},"optimized_scores":{"best_composite_score":0.75957,"best_fitness_score":0.73624,"best_task_score":0.72324},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":969.0,"contact_point_centroid":[0.5609,-0.07006,0.05382],"force_p95":109.80836,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":129.66307,"mean_force":69.0763,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52715,-0.05347,0.02319]},{"body_a":"world","body_b":"push_box","contact_count":1985.0,"contact_point_centroid":[0.55322,-0.10116,-0.00031],"force_p95":75.679,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":89.39237,"mean_force":42.65744,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52775,-0.05195,0.02312]},{"body_a":"world","body_b":"push_box","contact_count":3638.0,"contact_point_centroid":[0.53094,-0.13185,-3e-05],"force_p95":0.45807,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":80.79365,"mean_force":0.53545,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5026,-0.03752,0.05804]},{"body_a":"push_box","body_b":"link7","contact_count":56.0,"contact_point_centroid":[0.5497,-0.11709,0.0561],"force_p95":70.39065,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":80.11605,"mean_force":28.99943,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5079,-0.10658,0.02985]},{"body_a":"attachment","body_b":"push_box","contact_count":985.0,"contact_point_centroid":[0.546,-0.06172,0.05427],"force_p95":74.64729,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":76.77093,"mean_force":42.80128,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52749,-0.05259,0.02313]},{"body_a":"attachment","body_b":"push_box","contact_count":72.0,"contact_point_centroid":[0.53169,-0.10917,0.06048],"force_p95":50.1227,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":64.91849,"mean_force":17.55348,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50729,-0.10401,0.03033]},{"body_a":"world","body_b":"push_box","contact_count":3752.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52219,0.03965,0.16907]},{"body_a":"world","body_b":"push_box","contact_count":3328.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54641,0.02338,0.0235]}],"total_contact_groups":8},"final_pose_error":0.146,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53025,-0.13194,0.02499],"final_tcp_position":[0.50074,0.01948,0.08459],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55472,-0.03508,0.025]},"peak_contact_force":129.66307,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":938.0,"n_steps_budget":1000.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.025],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3752.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.54794,0.04702,0.03174],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08265,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":832.0,"n_steps_budget":1000.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.02499,"peak_contact_force":17.7669,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3328.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.5487,0.00192,0.02061],"tcp_start":[0.54794,0.04702,0.03174],"tcp_to_object_dist_end":0.03774,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":992.0,"n_steps_budget":1000.0,"object_pos_end":[0.53673,-0.13887,0.03095],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.03883,"object_to_goal_dist_start":0.12728,"object_z_max":0.03096,"peak_contact_force":107.45466,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3939.0,"raw_peak_contact_force":129.66307,"tcp_end":[0.50904,-0.11089,0.02899],"tcp_start":[0.5487,0.00192,0.02061],"tcp_to_object_dist_end":0.03942,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53025,-0.13194,0.02499],"object_pos_start":[0.53673,-0.13887,0.03095],"object_to_goal_dist_end":0.03523,"object_to_goal_dist_start":0.03883,"object_z_max":0.03475,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3766.0,"raw_peak_contact_force":80.79365,"tcp_end":[0.50074,0.01948,0.08459],"tcp_start":[0.50904,-0.11089,0.02899],"tcp_to_object_dist_end":0.16538,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `0fd7d18e656259f06515eb57b82afa0c0febd9395a43c1a5f926ddaec3767c64`; realized-scene SHA-256: `5de0d8cc5a3c16249bcf1097af6edba15dfacc79d06e3eed726605dcb01257b0`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45543,-9e-05,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.04457,-0.14991,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.45543,-9e-05,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.22449,"average_solve_count":196.0,"average_success_count":196.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.15097,"contact_1.speed":0.01648,"push_1.push_speed":0.1,"retract_1.retract_height":0.19158,"retract_1.speed":0.02263},"optimized_scores":{"best_composite_score":0.46579,"best_fitness_score":0.77579,"best_task_score":0.93928},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1741.0,"contact_point_centroid":[0.47259,-0.06681,-5e-05],"force_p95":21.1935,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":37.28609,"mean_force":3.93378,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46741,-0.0221,0.02118]},{"body_a":"attachment","body_b":"push_box","contact_count":844.0,"contact_point_centroid":[0.47826,-0.04445,0.03433],"force_p95":20.87692,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":33.26013,"mean_force":6.52034,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47018,-0.03268,0.02083]},{"body_a":"push_box","body_b":"link7","contact_count":185.0,"contact_point_centroid":[0.48755,-0.01325,0.05139],"force_p95":12.10048,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.64959,"mean_force":6.9705,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.45882,0.00885,0.0214]},{"body_a":"world","body_b":"push_box","contact_count":3929.0,"contact_point_centroid":[0.49507,-0.14173,-1e-05],"force_p95":0.24549,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.08951,"mean_force":0.25829,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48896,-0.04424,0.04643]},{"body_a":"push_box","body_b":"link7","contact_count":16.0,"contact_point_centroid":[0.51944,-0.12338,0.05005],"force_p95":4.66236,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.95153,"mean_force":1.94224,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48839,-0.09918,0.0205]},{"body_a":"world","body_b":"push_box","contact_count":3640.0,"contact_point_centroid":[0.45543,-9e-05,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47735,0.05545,0.17352]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.45543,-9e-05,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.45047,0.06237,0.02758]}],"total_contact_groups":7},"final_pose_error":0.15872,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49509,-0.14187,0.02499],"final_tcp_position":[0.49104,0.01074,0.07439],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45543,-9e-05,0.025]},"peak_contact_force":37.28609,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":910.0,"n_steps_budget":1000.0,"object_pos_end":[0.45543,-9e-05,0.02499],"object_pos_start":[0.45543,-9e-05,0.025],"object_to_goal_dist_end":0.1564,"object_to_goal_dist_start":0.1564,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3640.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.45384,0.08031,0.03462],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08098,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45543,-9e-05,0.02499],"object_pos_start":[0.45543,-9e-05,0.02499],"object_to_goal_dist_end":0.1564,"object_to_goal_dist_start":0.1564,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.45067,0.04878,0.02505],"tcp_start":[0.45384,0.08031,0.03462],"tcp_to_object_dist_end":0.0491,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49451,-0.142,0.02509],"object_pos_start":[0.45543,-9e-05,0.02499],"object_to_goal_dist_end":0.00971,"object_to_goal_dist_start":0.1564,"object_z_max":0.02755,"peak_contact_force":0.86785,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2770.0,"raw_peak_contact_force":37.28609,"tcp_end":[0.49061,-0.10497,0.02019],"tcp_start":[0.45067,0.04878,0.02505],"tcp_to_object_dist_end":0.03756,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49509,-0.14187,0.02499],"object_pos_start":[0.49451,-0.142,0.02509],"object_to_goal_dist_end":0.0095,"object_to_goal_dist_start":0.00971,"object_z_max":0.0256,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3945.0,"raw_peak_contact_force":8.08951,"tcp_end":[0.49104,0.01074,0.07439],"tcp_start":[0.49061,-0.10497,0.02019],"tcp_to_object_dist_end":0.16046,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```