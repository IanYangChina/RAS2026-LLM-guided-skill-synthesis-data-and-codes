## Search State

- **Seed**: 9
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 7 | 0.4551 | 0.63 | ❌ rejected |
| 4 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | force_threshold_switch | admittance_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 5 | 0.6774 | 0.82 | ✅ accepted |
| 3 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | force_threshold_switch | admittance_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 5 | 0.6651 | 0.80 | ❌ rejected |
| 2 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.3249 | 0.44 | ❌ rejected |
| 1 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | force_threshold_switch | admittance_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 5 | 0.7669 | 0.72 | ❌ rejected |

**Proposal policy**: task_score is 0.63 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.455) — your mutation base

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

- **Composite score**: 0.455
- **task_score** (E): 0.631
- **fitness_score**: 0.643  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.222
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.410

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2028 |
| contact_1 | 0.67 | 1.00 | 0.0900 |
| push_1 | 1.00 | 1.00 | 0.1428 |
| retract_1 | 0.67 | 1.00 | 0.1033 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.514, 0.056, 0.111) | (0.518, -0.020, 0.025)→(0.518, -0.020, 0.025) | 0.139→0.139 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 0.67 / force_exceeded | (0.514, 0.056, 0.111)→(0.514, 0.016, 0.031) | (0.518, -0.020, 0.025)→(0.518, -0.021, 0.025) | 0.139→0.138 | 1.00 / 4.333 | 11.396 | 3.274 |
| push_1 | push | 1.00 / time_limit | (0.514, 0.016, 0.031)→(0.491, -0.117, 0.026) | (0.518, -0.021, 0.025)→(0.527, -0.112, 0.025) | 0.138→0.048 | 1.00 / 3.333 | 0.588 | 25.884 |
| retract_1 | retract | 0.67 / step_budget | (0.491, -0.117, 0.026)→(0.487, -0.116, 0.129) | (0.527, -0.112, 0.025)→(0.528, -0.113, 0.025) | 0.048→0.048 | 1.00 / 4.000 | 0.245 | 0.595 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.776
- goal_progress: 0.949
- terminal_score: 0.949
- phase_score: 0.682
- phase_breakdown.approach_score: 0.275
- phase_breakdown.push_score: 0.802
- phase_breakdown.contact_score: 0.753

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.789
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.949
- **Median Q (composite search score)**: 0.526
- **K-run variance**: 0.0595
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.345


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.49697,"average_solve_count":165.0,"average_success_count":165.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.06951,"contact_1.contact_force_threshold":11.41086,"contact_1.speed":0.03645,"push_1.push_depth":0.28716,"push_1.push_speed":0.08804,"retract_1.retract_height":0.13872,"retract_1.speed":0.06264},"optimized_scores":{"best_composite_score":0.52559,"best_fitness_score":0.60226,"best_task_score":0.5303},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":819.0,"contact_point_centroid":[0.52452,-0.06028,0.04941],"force_p95":12.77284,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.56603,"mean_force":3.20596,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51239,-0.05211,0.02661]},{"body_a":"world","body_b":"push_box","contact_count":1613.0,"contact_point_centroid":[0.55607,-0.08137,-4e-05],"force_p95":7.43874,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.07924,"mean_force":2.10308,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51049,-0.05759,0.02669]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.52882,-0.09504,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24719,"mean_force":0.2452,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48348,-0.12213,0.07895]},{"body_a":"world","body_b":"push_box","contact_count":2784.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5181,0.02515,0.19994]},{"body_a":"world","body_b":"push_box","contact_count":3884.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.5374,0.02767,0.05838]}],"total_contact_groups":5},"final_pose_error":0.03368,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52882,-0.09504,0.02499],"final_tcp_position":[0.48364,-0.12212,0.13173],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":23.56603,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":696.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2784.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.53823,0.05082,0.10122],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.10811,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":971.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.02499,"peak_contact_force":13.98131,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3884.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.53915,0.01142,0.0313],"tcp_start":[0.53823,0.05082,0.10122],"tcp_to_object_dist_end":0.0379,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52869,-0.09505,0.02484],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.06198,"object_to_goal_dist_start":0.13211,"object_z_max":0.02964,"peak_contact_force":0.24878,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2432.0,"raw_peak_contact_force":23.56603,"subtask_id":"push","tcp_end":[0.4869,-0.12282,0.02652],"tcp_start":[0.53915,0.01142,0.0313],"tcp_to_object_dist_end":0.0502,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52882,-0.09504,0.02499],"object_pos_start":[0.52869,-0.09505,0.02484],"object_to_goal_dist_end":0.06205,"object_to_goal_dist_start":0.06198,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24719,"tcp_end":[0.48364,-0.12212,0.13173],"tcp_start":[0.4869,-0.12282,0.02652],"tcp_to_object_dist_end":0.11903,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.90833,"average_solve_count":240.0,"average_success_count":240.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.11146,"contact_1.contact_force_threshold":17.48816,"contact_1.speed":0.02805,"push_1.push_depth":0.20366,"push_1.push_speed":0.07647,"retract_1.retract_height":0.14605,"retract_1.speed":0.0127},"optimized_scores":{"best_composite_score":0.12755,"best_fitness_score":0.53755,"best_task_score":0.41334},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":712.0,"contact_point_centroid":[0.53478,-0.05531,0.04773],"force_p95":11.39032,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.41636,"mean_force":3.30386,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5237,-0.04556,0.02477]},{"body_a":"world","body_b":"push_box","contact_count":1943.0,"contact_point_centroid":[0.55972,-0.08633,-3e-05],"force_p95":6.41058,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.50147,"mean_force":1.60808,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5146,-0.06416,0.02487]},{"body_a":"attachment","body_b":"push_box","contact_count":130.0,"contact_point_centroid":[0.55154,-0.01129,0.04186],"force_p95":7.42871,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.33016,"mean_force":5.18543,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54963,0.0007,0.03344]},{"body_a":"world","body_b":"push_box","contact_count":3880.0,"contact_point_centroid":[0.55497,-0.03575,-1e-05],"force_p95":1.93019,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.52302,"mean_force":0.4171,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.5475,0.0172,0.07616]},{"body_a":"world","body_b":"push_box","contact_count":2328.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52264,0.0204,0.2208]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.54605,-0.09122,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48763,-0.11103,0.06866]}],"total_contact_groups":6},"final_pose_error":0.05766,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.54605,-0.09122,0.02499],"final_tcp_position":[0.48777,-0.11102,0.11335],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55472,-0.03508,0.025]},"peak_contact_force":19.41636,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":582.0,"n_steps_budget":1000.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.025],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2328.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.54757,0.04145,0.14243],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.14036,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55498,-0.03767,0.02495],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.12507,"object_to_goal_dist_start":0.12728,"object_z_max":0.025,"peak_contact_force":0.00038,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":4010.0,"raw_peak_contact_force":9.33016,"subtask_id":"contact","tcp_end":[0.54986,-0.00074,0.02962],"tcp_start":[0.54757,0.04145,0.14243],"tcp_to_object_dist_end":0.03758,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54605,-0.09122,0.02499],"object_pos_start":[0.55498,-0.03767,0.02495],"object_to_goal_dist_end":0.07467,"object_to_goal_dist_start":0.12507,"object_z_max":0.02885,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2655.0,"raw_peak_contact_force":19.41636,"subtask_id":"push","tcp_end":[0.49114,-0.11166,0.02486],"tcp_start":[0.54986,-0.00074,0.02962],"tcp_to_object_dist_end":0.05859,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54605,-0.09122,0.02499],"object_pos_start":[0.54605,-0.09122,0.02499],"object_to_goal_dist_end":0.07467,"object_to_goal_dist_start":0.07467,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.48777,-0.11102,0.11335],"tcp_start":[0.49114,-0.11166,0.02486],"tcp_to_object_dist_end":0.10769,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.36022,"average_solve_count":186.0,"average_success_count":186.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.05596,"contact_1.contact_force_threshold":8.08614,"contact_1.speed":0.02295,"push_1.push_depth":0.26872,"push_1.push_speed":0.09828,"retract_1.retract_height":0.13623,"retract_1.speed":0.07056},"optimized_scores":{"best_composite_score":0.71222,"best_fitness_score":0.78889,"best_task_score":0.94935},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":799.0,"contact_point_centroid":[0.475,-0.05067,0.0421],"force_p95":18.54267,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":34.67103,"mean_force":5.25746,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47087,-0.03882,0.02767]},{"body_a":"world","body_b":"push_box","contact_count":1300.0,"contact_point_centroid":[0.48071,-0.08881,-6e-05],"force_p95":9.8294,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.96663,"mean_force":3.67606,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46938,-0.03348,0.02781]},{"body_a":"world","body_b":"push_box","contact_count":3961.0,"contact_point_centroid":[0.50767,-0.15225,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.29248,"mean_force":0.24723,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4905,-0.11536,0.08557]},{"body_a":"attachment","body_b":"push_box","contact_count":15.0,"contact_point_centroid":[0.49888,-0.12783,0.04632],"force_p95":1.02349,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.1328,"mean_force":0.5847,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49257,-0.11614,0.0288]},{"body_a":"world","body_b":"push_box","contact_count":2888.0,"contact_point_centroid":[0.45543,-9e-05,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47669,0.03708,0.19396]},{"body_a":"world","body_b":"push_box","contact_count":2168.0,"contact_point_centroid":[0.45543,-9e-05,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.45181,0.05574,0.05883]}],"total_contact_groups":6},"final_pose_error":0.02035,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50764,-0.1521,0.02499],"final_tcp_position":[0.49075,-0.11538,0.14317],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45543,-9e-05,0.025]},"peak_contact_force":34.67103,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":722.0,"n_steps_budget":1000.0,"object_pos_end":[0.45543,-9e-05,0.02499],"object_pos_start":[0.45543,-9e-05,0.025],"object_to_goal_dist_end":0.1564,"object_to_goal_dist_start":0.1564,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2888.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.45475,0.07491,0.0893],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.0988,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":542.0,"n_steps_budget":1000.0,"object_pos_end":[0.45543,-9e-05,0.02499],"object_pos_start":[0.45543,-9e-05,0.02499],"object_to_goal_dist_end":0.1564,"object_to_goal_dist_start":0.1564,"object_z_max":0.02499,"peak_contact_force":20.20646,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2168.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.45164,0.03691,0.03161],"tcp_start":[0.45475,0.07491,0.0893],"tcp_to_object_dist_end":0.03777,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50728,-0.15105,0.02605],"object_pos_start":[0.45543,-9e-05,0.02499],"object_to_goal_dist_end":0.00743,"object_to_goal_dist_start":0.1564,"object_z_max":0.0262,"peak_contact_force":1.27042,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2099.0,"raw_peak_contact_force":34.67103,"subtask_id":"push","tcp_end":[0.49394,-0.11601,0.02702],"tcp_start":[0.45164,0.03691,0.03161],"tcp_to_object_dist_end":0.0375,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50764,-0.1521,0.02499],"object_pos_start":[0.50728,-0.15105,0.02605],"object_to_goal_dist_end":0.00792,"object_to_goal_dist_start":0.00743,"object_z_max":0.02605,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3976.0,"raw_peak_contact_force":1.29248,"tcp_end":[0.49075,-0.11538,0.14317],"tcp_start":[0.49394,-0.11601,0.02702],"tcp_to_object_dist_end":0.1249,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```