## Search State

- **Seed**: 9
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.3249 | 0.44 | ❌ rejected |
| 1 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | force_threshold_switch | admittance_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 5 | 0.7669 | 0.72 | ❌ rejected |
| 0 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | force_threshold_switch | admittance_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 5 | 0.6768 | 0.81 | ✅ accepted |

**Proposal policy**: task_score is 0.44 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.325) — your mutation base

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

- **Composite score**: 0.325
- **task_score** (E): 0.437
- **fitness_score**: 0.485  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.410

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2284 |
| contact_1 | 1.00 | 1.00 | 0.0238 |
| push_1 | 1.00 | 1.00 | 0.1196 |
| retract_1 | 1.00 | 1.00 | 0.1048 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.514, -0.001, 0.077) | (0.518, -0.020, 0.025)→(0.518, -0.020, 0.025) | 0.139→0.139 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / force_exceeded | (0.514, -0.001, 0.077)→(0.513, 0.006, 0.055) | (0.518, -0.020, 0.025)→(0.518, -0.020, 0.025) | 0.139→0.139 | 1.00 / 5.000 | 50609.120 | 0.245 |
| push_1 | push | 1.00 / step_budget | (0.513, 0.006, 0.055)→(0.506, -0.106, 0.033) | (0.518, -0.020, 0.025)→(0.527, -0.067, 0.033) | 0.139→0.091 | 1.00 / 2.667 | 62.174 | 209.193 |
| retract_1 | retract | 1.00 / step_budget | (0.506, -0.106, 0.033)→(0.497, -0.144, 0.130) | (0.527, -0.067, 0.033)→(0.521, -0.078, 0.025) | 0.091→0.079 | 1.00 / 4.000 | 0.245 | 27.944 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.508
- lateral_force_integral: None
- approach_alignment: 0.801
- goal_progress: 0.488
- terminal_score: 0.488
- phase_score: 0.526
- phase_breakdown.approach_score: 0.210
- phase_breakdown.push_score: 0.635
- phase_breakdown.contact_score: 0.555

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.511
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.488
- **Median Q (composite search score)**: 0.340
- **K-run variance**: 0.0008
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.326


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.73973,"average_solve_count":146.0,"average_success_count":146.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.05427,"approach_1.arc_height":0.1294,"contact_1.contact_force_threshold":11.15062,"contact_1.contact_speed":0.02492,"push_1.push_speed":0.06889,"retract_1.retract_height":0.14826,"retract_1.retract_speed":0.07564},"optimized_scores":{"best_composite_score":0.3397,"best_fitness_score":0.4997,"best_task_score":0.46859},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":591.0,"contact_point_centroid":[0.54008,-0.04597,0.04658],"force_p95":210.39364,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":215.57024,"mean_force":161.86556,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52979,-0.04847,0.04904]},{"body_a":"world","body_b":"push_box","contact_count":1841.0,"contact_point_centroid":[0.54145,-0.04166,-0.00051],"force_p95":127.20829,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":140.15658,"mean_force":52.8371,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53118,-0.04081,0.04978]},{"body_a":"push_box","body_b":"link7","contact_count":11.0,"contact_point_centroid":[0.55411,-0.07656,0.06917],"force_p95":87.41514,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":88.20426,"mean_force":71.94497,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5125,-0.10546,0.03604]},{"body_a":"world","body_b":"push_box","contact_count":1392.0,"contact_point_centroid":[0.53234,-0.08529,-5e-05],"force_p95":0.5641,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":42.48501,"mean_force":0.41855,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50249,-0.12831,0.09973]},{"body_a":"push_box","body_b":"link7","contact_count":16.0,"contact_point_centroid":[0.55411,-0.08037,0.0686],"force_p95":40.88841,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":41.67274,"mean_force":11.75713,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51032,-0.10848,0.03565]},{"body_a":"attachment","body_b":"push_box","contact_count":5.0,"contact_point_centroid":[0.51186,-0.10472,0.05254],"force_p95":2.73262,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.79924,"mean_force":1.99954,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50639,-0.11444,0.05437]},{"body_a":"world","body_b":"push_box","contact_count":2428.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51953,0.05119,0.18658]},{"body_a":"world","body_b":"push_box","contact_count":948.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53826,-0.00262,0.06283]}],"total_contact_groups":8},"final_pose_error":0.01999,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53206,-0.08754,0.02499],"final_tcp_position":[0.49827,-0.14497,0.15399],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":75893.53664,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":607.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2428.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.53984,-0.00625,0.07776],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.05639,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":237.0,"n_steps_budget":780.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.02499,"peak_contact_force":75893.53664,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":948.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.53863,0.00061,0.05401],"tcp_start":[0.53984,-0.00625,0.07776],"tcp_to_object_dist_end":0.03952,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":592.0,"n_steps_budget":1000.0,"object_pos_end":[0.53716,-0.06899,0.03424],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.0896,"object_to_goal_dist_start":0.13211,"object_z_max":0.03484,"peak_contact_force":88.20426,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2443.0,"raw_peak_contact_force":215.57024,"subtask_id":"push","tcp_end":[0.51133,-0.10739,0.03491],"tcp_start":[0.53863,0.00061,0.05401],"tcp_to_object_dist_end":0.04628,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":394.0,"n_steps_budget":1000.0,"object_pos_end":[0.53206,-0.08754,0.02499],"object_pos_start":[0.53716,-0.06899,0.03424],"object_to_goal_dist_end":0.07021,"object_to_goal_dist_start":0.0896,"object_z_max":0.03463,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1413.0,"raw_peak_contact_force":42.48501,"tcp_end":[0.49827,-0.14497,0.15399],"tcp_start":[0.51133,-0.10739,0.03491],"tcp_to_object_dist_end":0.14519,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.24375,"average_solve_count":160.0,"average_success_count":160.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.05005,"approach_1.arc_height":0.14294,"contact_1.contact_force_threshold":19.71237,"contact_1.contact_speed":0.02313,"push_1.push_speed":0.0513,"retract_1.retract_height":0.132,"retract_1.retract_speed":0.05821},"optimized_scores":{"best_composite_score":0.3507,"best_fitness_score":0.5107,"best_task_score":0.48756},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":657.0,"contact_point_centroid":[0.54522,-0.05507,0.04651],"force_p95":212.24961,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":214.75338,"mean_force":166.11477,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53469,-0.05734,0.04885]},{"body_a":"world","body_b":"push_box","contact_count":2016.0,"contact_point_centroid":[0.54991,-0.05118,-0.00053],"force_p95":158.37299,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":169.9009,"mean_force":54.84223,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53671,-0.05001,0.0496]},{"body_a":"push_box","body_b":"link7","contact_count":6.0,"contact_point_centroid":[0.56294,-0.08321,0.06978],"force_p95":96.91984,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":97.50564,"mean_force":73.44573,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51417,-0.10945,0.03676]},{"body_a":"world","body_b":"push_box","contact_count":1212.0,"contact_point_centroid":[0.53998,-0.09519,-8e-05],"force_p95":0.69313,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":38.77919,"mean_force":0.47049,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50334,-0.13008,0.09301]},{"body_a":"push_box","body_b":"link7","contact_count":19.0,"contact_point_centroid":[0.56263,-0.08666,0.06968],"force_p95":35.10943,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.70201,"mean_force":10.1609,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5122,-0.11151,0.03693]},{"body_a":"attachment","body_b":"push_box","contact_count":11.0,"contact_point_centroid":[0.51769,-0.10249,0.03757],"force_p95":7.72639,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.59137,"mean_force":1.83743,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51185,-0.11237,0.03987]},{"body_a":"world","body_b":"push_box","contact_count":2456.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52514,0.04463,0.182]},{"body_a":"world","body_b":"push_box","contact_count":860.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54822,-0.01262,0.06097]}],"total_contact_groups":8},"final_pose_error":0.01973,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53908,-0.09778,0.02499],"final_tcp_position":[0.49848,-0.14478,0.13803],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55472,-0.03508,0.025]},"peak_contact_force":75893.53664,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":614.0,"n_steps_budget":1000.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.025],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2456.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.54981,-0.01601,0.07356],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.05241,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":215.0,"n_steps_budget":720.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.02499,"peak_contact_force":75893.53664,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":860.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.54847,-0.00955,0.05377],"tcp_start":[0.54981,-0.01601,0.07356],"tcp_to_object_dist_end":0.03898,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":657.0,"n_steps_budget":1000.0,"object_pos_end":[0.54726,-0.07643,0.0346],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.08797,"object_to_goal_dist_start":0.12728,"object_z_max":0.03477,"peak_contact_force":97.50564,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2679.0,"raw_peak_contact_force":214.75338,"subtask_id":"push","tcp_end":[0.51339,-0.11042,0.03606],"tcp_start":[0.54847,-0.00955,0.05377],"tcp_to_object_dist_end":0.04801,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":360.0,"n_steps_budget":1000.0,"object_pos_end":[0.53908,-0.09778,0.02499],"object_pos_start":[0.54726,-0.07643,0.0346],"object_to_goal_dist_end":0.06523,"object_to_goal_dist_start":0.08797,"object_z_max":0.03523,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1242.0,"raw_peak_contact_force":38.77919,"tcp_end":[0.49848,-0.14478,0.13803],"tcp_start":[0.51339,-0.11042,0.03606],"tcp_to_object_dist_end":0.12898,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.89778,"average_solve_count":225.0,"average_success_count":225.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.05184,"approach_1.arc_height":0.13878,"contact_1.contact_force_threshold":12.49617,"contact_1.contact_speed":0.04355,"push_1.push_speed":0.02636,"retract_1.retract_height":0.0894,"retract_1.retract_speed":0.05238},"optimized_scores":{"best_composite_score":0.28429,"best_fitness_score":0.44429,"best_task_score":0.35341},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":492.0,"contact_point_centroid":[0.48305,-0.01934,0.04625],"force_p95":189.93194,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":197.25467,"mean_force":151.66367,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47529,-0.0235,0.04909]},{"body_a":"world","body_b":"push_box","contact_count":986.0,"contact_point_centroid":[0.4776,-0.02017,-0.0007],"force_p95":164.86129,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":172.46862,"mean_force":76.50258,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47173,-0.01668,0.04959]},{"body_a":"world","body_b":"push_box","contact_count":952.0,"contact_point_centroid":[0.49298,-0.04954,-0.0001],"force_p95":0.56545,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.56711,"mean_force":0.29186,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49348,-0.1244,0.06493]},{"body_a":"world","body_b":"push_box","contact_count":2300.0,"contact_point_centroid":[0.45543,-9e-05,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4776,0.05973,0.19519]},{"body_a":"world","body_b":"push_box","contact_count":696.0,"contact_point_centroid":[0.45543,-9e-05,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.45162,0.02215,0.06786]}],"total_contact_groups":5},"final_pose_error":0.01999,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.4933,-0.0491,0.02499],"final_tcp_position":[0.49569,-0.14214,0.09654],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45543,-9e-05,0.025]},"peak_contact_force":197.25467,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":575.0,"n_steps_budget":1000.0,"object_pos_end":[0.45543,-9e-05,0.02499],"object_pos_start":[0.45543,-9e-05,0.025],"object_to_goal_dist_end":0.1564,"object_to_goal_dist_start":0.1564,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2300.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.45379,0.01929,0.08072],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.05903,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":174.0,"n_steps_budget":600.0,"object_pos_end":[0.45543,-9e-05,0.02499],"object_pos_start":[0.45543,-9e-05,0.02499],"object_to_goal_dist_end":0.1564,"object_to_goal_dist_start":0.1564,"object_z_max":0.02499,"peak_contact_force":40.28811,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":696.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.45119,0.02612,0.05609],"tcp_start":[0.45379,0.01929,0.08072],"tcp_to_object_dist_end":0.04089,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":533.0,"n_steps_budget":1000.0,"object_pos_end":[0.49612,-0.05465,0.02998],"object_pos_start":[0.45543,-9e-05,0.02499],"object_to_goal_dist_end":0.09556,"object_to_goal_dist_start":0.1564,"object_z_max":0.03584,"peak_contact_force":0.81309,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1478.0,"raw_peak_contact_force":197.25467,"subtask_id":"push","tcp_end":[0.49379,-0.1014,0.02732],"tcp_start":[0.45119,0.02612,0.05609],"tcp_to_object_dist_end":0.04689,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":273.0,"n_steps_budget":1000.0,"object_pos_end":[0.4933,-0.0491,0.02499],"object_pos_start":[0.49612,-0.05465,0.02998],"object_to_goal_dist_end":0.10113,"object_to_goal_dist_start":0.09556,"object_z_max":0.02999,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":952.0,"raw_peak_contact_force":2.56711,"tcp_end":[0.49569,-0.14214,0.09654],"tcp_start":[0.49379,-0.1014,0.02732],"tcp_to_object_dist_end":0.1174,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```