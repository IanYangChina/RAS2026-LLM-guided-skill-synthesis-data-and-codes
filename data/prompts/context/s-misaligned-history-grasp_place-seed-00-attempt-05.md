## Search State

- **Seed**: 0
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | insert → approach → push → retract → lift → insert → push | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | force_threshold_switch | position_control | position_control | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 8  | -0.1730 | 0.17 | ❌ rejected |
| 4 | insert → approach → push → retract → lift → insert → push | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | force_threshold_switch | position_control | position_control | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 8  | -0.1694 | 0.19 | ✅ accepted |
| 3 | insert → approach → push → retract → lift → insert → push | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | force_threshold_switch | position_control | position_control | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 8  | -0.1713 | 0.18 | ❌ rejected |
| 2 | insert → approach → push → retract → lift → insert → push | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | force_threshold_switch | position_control | position_control | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 8  | -0.1716 | 0.18 | ❌ rejected |
| 1 | insert → approach → push → retract → lift → insert → push | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | force_threshold_switch | position_control | position_control | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 8  | -0.1713 | 0.18 | ❌ rejected |

**Proposal policy**: task_score is 0.18 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

- Task name: grasp_place
- Frozen realised-scene SHA-256: `f07a678caf5b8ea43212ad5a337315ad102b1ae725b01cf669f7af9bd0eea2ea`
- Frozen object start: [0.5136961687321454, -0.02302132862361297, 0.03]
- Frozen task target: [0.5540973523936195, 0.15165276355285293, 0.22199053588004086]
- Goal object position: (0.5540973523936195, 0.15165276355285293, 0.22199053588004086)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5540973523936195, 0.15165276355285293, 0.22199053588004086)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5136961687321454, -0.02302132862361297, 0.03)
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 20.0 N
- Robot initial TCP position: (0.5, 0.0, 0.3)
- Robot initial gripper state: **open** (gripper starts fully open; ensure a `grasp`/`force_grasp` phase closes it before lifting)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **final object-to-realised-airborne-3D-target proximity. Grasp/lift signals are optimiser fitness diagnostics only; they do not gate the canonical task_score.**

## Scene Entities

robot:
  model: panda_full
  tcp_site: attachment_site
  gripper: franka_hand
  tcp_initial_world: [0.5, 0, 0.3]
objects:
  - name: grasp_target
    role: manipulated_object
    dynamics: free
    geometry: box
    dimensions_m: [0.04, 0.04, 0.06]
    mass_kg: 0.05
  - name: placement_surface
    role: goal_area
    dynamics: static
    geometry: point
task_landmarks:
  frozen_object_start: [0.5137, -0.023, 0.03]
  frozen_task_target: [0.5541, 0.1517, 0.222]
  frozen_object_starts: {'grasp_target': [0.5136961687321454, -0.02302132862361297, 0.03]}
  frozen_targets: {'place_target': [0.5540973523936195, 0.15165276355285293, 0.22199053588004086]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: f07a678caf5b8ea43212ad5a337315ad102b1ae725b01cf669f7af9bd0eea2ea

## Subtask Layer

**Mode**: free (you define subtask targets; use `subtasks:` block in your YAML)

Define subtasks in a `subtasks:` block **before** `phases:`. Each subtask specifies an intermediate optimisation target.

**Required fields** — always include both, never omit:
- `anchor` (**required**): fixture | goal | object | world
- `target_entity` (**required**): hinge | object | tcp

Subtask anchors are separate from phase `target.anchor` vocabulary: subtasks use `world | object | goal | fixture`, while phase targets use `world | task_goal | task_object | fixture | body | site | current_tcp`.

Optional fields:
- `metric`: contact | distance | goal_progress | hinge_angle (default: distance)
- `offset`: [x, y, z] in metres relative to anchor (default: [0, 0, 0])
- `param_offset_key`: CMA-ES parameter added to offset at runtime (optional)
- `weight`: scoring weight [0.1, 1.0] (default: 1.0)

**Anchor resolution for this task** — choose anchor so the resolved position is meaningful:
| Anchor | Resolves to | Best used for |
|--------|-------------|---------------|
| `world` | absolute world-frame coordinate | fixed reference points not tied to objects |
| `object` | offset from object initial position (0.5136961687321454, -0.02302132862361297, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5540973523936195, 0.15165276355285293, 0.22199053588004086) | final destination targets |
| `fixture` | offset from fixture pose (if defined, else world) | targets near fixture |

Annotate each phase with `subtask_id: <id>` to bind it to a subtask.
Only the **last phase** bound to a given subtask contributes to subtask scoring.

Example (two subtasks — one near object start, one at goal):
```yaml
subtasks:
  - id: reach_pre_contact
    anchor: object         # resolved to object initial position (see table above)
    target_entity: tcp     # score TCP distance to this target
    metric: distance
    offset: [0.0, 0.0, 0.10]  # 10 cm above object start position
    weight: 0.3
  - id: reach_goal
    anchor: goal           # resolved to task goal position (see table above)
    target_entity: tcp
    metric: distance
    offset: [0.0, 0.0, 0.0]
    weight: 0.7
phases:
  - id: approach_1
    type: approach
    subtask_id: reach_pre_contact
    ...
  - id: push_1
    type: push
    subtask_id: reach_goal
    ...
```

## Current Skill (Q=-0.171) — your mutation base

```yaml
skill: grasp_place
phases:
- id: insert_1
  type: insert
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  parameters:
    insertion_force:
      type: scalar
      range:
      - 1.0
      - 20.0
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
- id: push_1
  type: push
  generator: impedance_motion
  control: position_control
  termination: time_limit
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
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: lift_1
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
- id: insert_2
  type: insert
  generator: impedance_motion
  control: impedance_control
  termination: force_exceeded
  parameters:
    insertion_depth:
      type: scalar
      range:
      - 0.01
      - 0.15
    insertion_force:
      type: scalar
      range:
      - 1.0
      - 20.0
- id: push_2
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: time_limit
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.02
      - 0.2

```

## Design Metrics

- **Composite score**: -0.171
- **task_score** (E): 0.179
- **fitness_score**: 0.179  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.550

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| insert_1 | 0.00 | 1.00 | 0.2373 |
| approach_1 | 1.00 | 1.00 | 0.1834 |
| push_1 | 1.00 | 1.00 | 0.0693 |
| retract_1 | 0.00 | 1.00 | 0.0551 |
| lift_1 | 1.00 | 1.00 | 0.1603 |
| insert_2 | 1.00 | 1.00 | 0.0001 |
| push_2 | 1.00 | 1.00 | 0.1633 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| insert_1 | insert | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.574, 0.155, 0.137) | (0.497, 0.001, 0.030)→(0.497, 0.001, 0.026) | 0.263→0.265 | 1.00 / 4.000 | 0.123 | 0.138 |
| approach_1 | approach | 1.00 / step_budget | (0.574, 0.155, 0.137)→(0.497, 0.010, 0.058) | (0.497, 0.001, 0.026)→(0.494, -0.006, 0.022) | 0.265→0.273 | 1.00 / 6.667 | 0.423 | 0.425 |
| push_1 | push | 1.00 / time_limit | (0.497, 0.010, 0.058)→(0.526, 0.073, 0.066) | (0.494, -0.006, 0.022)→(0.497, 0.009, 0.026) | 0.273→0.259 | 1.00 / 4.000 | 27.197 | 0.453 |
| retract_1 | retract | 0.00 / step_budget | (0.526, 0.073, 0.066)→(0.540, 0.109, 0.099) | (0.497, 0.009, 0.026)→(0.498, 0.007, 0.026) | 0.259→0.260 | 1.00 / 4.000 | 0.123 | 0.208 |
| lift_1 | lift | 1.00 / step_budget | (0.540, 0.109, 0.099)→(0.496, 0.011, 0.215) | (0.498, 0.007, 0.026)→(0.498, 0.007, 0.026) | 0.260→0.260 | 1.00 / 4.000 | 0.123 | 0.123 |
| insert_2 | insert | 1.00 / force_exceeded | (0.496, 0.011, 0.215)→(0.496, 0.011, 0.215) | (0.498, 0.007, 0.026)→(0.498, 0.007, 0.026) | 0.260→0.260 | 1.00 / 4.000 | 282.681 | 0.123 |
| push_2 | push | 1.00 / time_limit | (0.496, 0.011, 0.215)→(0.561, 0.133, 0.131) | (0.498, 0.007, 0.026)→(0.498, 0.007, 0.026) | 0.260→0.260 | 1.00 / 4.000 | 54.136 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: None
- grasp_place_fitness: 0.182

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.182
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.218
- **Median Q (composite search score)**: -0.171
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.398


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `096c354712624ed6bd8f9b9cbbbc2b7d35a94d9c1517cfb8353e2e383be5aaf0`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `3798aa6551d21849355469c7d63897f628ac7de9267c18bb4301fe6cfaae0164`; realized-scene SHA-256: `f07a678caf5b8ea43212ad5a337315ad102b1ae725b01cf669f7af9bd0eea2ea`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5137,-0.02302,0.03]},{"name":"goal","value":[0.5541,0.15165,0.22199]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5137,-0.02302,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5541,0.15165,0.22199]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.56379,"average_solve_count":243.0,"average_success_count":243.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.0514,"insert_1.insertion_force":10.22605,"insert_2.insertion_depth":0.07641,"insert_2.insertion_force":5.78879,"push_1.push_distance":0.13575,"push_1.push_speed":0.05864,"push_2.push_distance":0.07323,"retract_1.speed":0.02659},"optimized_scores":{"best_composite_score":-0.16815,"best_fitness_score":0.18185,"best_task_score":0.1728},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3472.0,"contact_point_centroid":[0.50923,-0.01756,-0.00448],"force_p95":0.57127,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.67654,"mean_force":0.27839,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52476,0.02853,0.05434]},{"body_a":"world","body_b":"grasp_target","contact_count":2794.0,"contact_point_centroid":[0.51329,-0.0234,-0.00227],"force_p95":0.38256,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60712,"mean_force":0.1452,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.54177,0.07205,0.09138]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6482.0,"contact_point_centroid":[0.51909,-0.02733,0.046],"force_p95":0.17208,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20997,"mean_force":0.0744,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51932,0.0153,0.05142]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":682.0,"contact_point_centroid":[0.52156,-0.04129,0.05001],"force_p95":0.14604,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16057,"mean_force":0.08144,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51693,0.00062,0.05695]},{"body_a":"world","body_b":"grasp_target","contact_count":3996.0,"contact_point_centroid":[0.5137,-0.02302,-0.00196],"force_p95":0.12459,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12275,"phase_index":0.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.53682,0.07971,0.21414]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.5075,-0.01797,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12323,"mean_force":0.12262,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.54028,0.08578,0.08597]},{"body_a":"world","body_b":"grasp_target","contact_count":3852.0,"contact_point_centroid":[0.5075,-0.01797,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52139,0.04058,0.16]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.5075,-0.01797,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"insert_2","phase_type":"insert","tcp_position_centroid":[0.50552,-0.01348,0.21561]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.5075,-0.01797,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"push_2","phase_type":"push","tcp_position_centroid":[0.53095,0.0517,0.17413]}],"total_contact_groups":9},"final_pose_error":0.09799,"key_states":{"actual_goal_position":[0.5541,0.15165,0.22199],"final_object_position":[0.5075,-0.01797,0.02602],"final_tcp_position":[0.56013,0.1184,0.1368],"realised_goal_position":[0.5541,0.15165,0.22199],"realised_object_initial_position":[0.5137,-0.02302,0.03]},"peak_contact_force":255.95803,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.03],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26269,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":3996.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.57391,0.15482,0.13706],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.21814,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":715.0,"n_steps_budget":1000.0,"object_pos_end":[0.50785,-0.03718,0.01979],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.2805,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.60124,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3476.0,"raw_peak_contact_force":0.60712,"tcp_end":[0.51211,-0.01337,0.05028],"tcp_start":[0.57391,0.15482,0.13706],"tcp_to_object_dist_end":0.03892,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50753,-0.01794,0.02602],"object_pos_start":[0.50785,-0.03718,0.01979],"object_to_goal_dist_end":0.26332,"object_to_goal_dist_start":0.2805,"object_z_max":0.02614,"peak_contact_force":0.12281,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":9954.0,"raw_peak_contact_force":0.67654,"tcp_end":[0.54274,0.07231,0.06393],"tcp_start":[0.51211,-0.01337,0.05028],"tcp_to_object_dist_end":0.10403,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5075,-0.01797,0.02602],"object_pos_start":[0.50753,-0.01794,0.02602],"object_to_goal_dist_end":0.26334,"object_to_goal_dist_start":0.26332,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12323,"tcp_end":[0.5419,0.09707,0.10826],"tcp_start":[0.54274,0.07231,0.06393],"tcp_to_object_dist_end":0.14554,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":963.0,"n_steps_budget":1000.0,"object_pos_end":[0.5075,-0.01797,0.02602],"object_pos_start":[0.5075,-0.01797,0.02602],"object_to_goal_dist_end":0.26334,"object_to_goal_dist_start":0.26334,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":3852.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.50552,-0.01348,0.21561],"tcp_start":[0.5419,0.09707,0.10826],"tcp_to_object_dist_end":0.18966,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.5075,-0.01797,0.02602],"object_pos_start":[0.5075,-0.01797,0.02602],"object_to_goal_dist_end":0.26334,"object_to_goal_dist_start":0.26334,"object_z_max":0.02602,"peak_contact_force":255.95803,"phase_name":"insert_2","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":4.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.50551,-0.01355,0.21565],"tcp_start":[0.50552,-0.01348,0.21561],"tcp_to_object_dist_end":0.1897,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5075,-0.01797,0.02602],"object_pos_start":[0.5075,-0.01797,0.02602],"object_to_goal_dist_end":0.26334,"object_to_goal_dist_start":0.26334,"object_z_max":0.02602,"peak_contact_force":81.14225,"phase_name":"push_2","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.56013,0.1184,0.1368],"tcp_start":[0.50551,-0.01355,0.21565],"tcp_to_object_dist_end":0.18341,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `ed2df336ade3d991e9495251c8398520a59dd014a70bd2d7bb71dc7aefccaa8a`; realized-scene SHA-256: `a2ed2c4162d37489f2d2d0fa0373774d72c951d58f2469e0ba2d602ff46b6cfb`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50118,0.04505,0.03]},{"name":"goal","value":[0.56442,0.24486,0.14677]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.50118,0.04505,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.56442,0.24486,0.14677]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.5084,"average_solve_count":238.0,"average_success_count":238.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.05129,"insert_1.insertion_force":9.24117,"insert_2.insertion_depth":0.02666,"insert_2.insertion_force":13.37591,"push_1.push_distance":0.08399,"push_1.push_speed":0.03214,"push_2.push_distance":0.14607,"retract_1.speed":0.02825},"optimized_scores":{"best_composite_score":-0.17143,"best_fitness_score":0.17857,"best_task_score":0.21776},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3098.0,"contact_point_centroid":[0.50042,0.0544,-0.00298],"force_p95":0.38175,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55965,"mean_force":0.19057,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51103,0.07264,0.05392]},{"body_a":"world","body_b":"grasp_target","contact_count":1775.0,"contact_point_centroid":[0.50111,0.04504,-0.00213],"force_p95":0.2862,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54568,"mean_force":0.13828,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.53796,0.10595,0.0936]},{"body_a":"world","body_b":"grasp_target","contact_count":3220.0,"contact_point_centroid":[0.50685,0.06245,-0.00248],"force_p95":0.3547,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.37717,"mean_force":0.15383,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.53087,0.12903,0.07399]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":753.0,"contact_point_centroid":[0.52489,0.06588,0.05563],"force_p95":0.05939,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26556,"mean_force":0.02879,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.52603,0.10601,0.06211]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3434.0,"contact_point_centroid":[0.51674,0.03298,0.04713],"force_p95":0.13361,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18492,"mean_force":0.05968,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51132,0.07256,0.05426]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":320.0,"contact_point_centroid":[0.51537,0.02141,0.05151],"force_p95":0.14628,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15475,"mean_force":0.08986,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5082,0.06208,0.05922]},{"body_a":"world","body_b":"grasp_target","contact_count":3996.0,"contact_point_centroid":[0.50118,0.04505,-0.00196],"force_p95":0.12459,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12275,"phase_index":0.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.53682,0.07971,0.21414]},{"body_a":"world","body_b":"grasp_target","contact_count":3852.0,"contact_point_centroid":[0.50904,0.05877,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51894,0.10386,0.14798]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.50904,0.05877,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"insert_2","phase_type":"insert","tcp_position_centroid":[0.50679,0.06183,0.21464]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.50904,0.05877,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"push_2","phase_type":"push","tcp_position_centroid":[0.54025,0.11594,0.16287]}],"total_contact_groups":10},"final_pose_error":0.03915,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.50904,0.05877,0.02602],"final_tcp_position":[0.57751,0.1717,0.11505],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":306.28802,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":3996.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.57391,0.15482,0.13706],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17225,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":445.0,"n_steps_budget":1000.0,"object_pos_end":[0.49653,0.03818,0.02144],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.25107,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.54568,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2095.0,"raw_peak_contact_force":0.54568,"tcp_end":[0.50317,0.05456,0.05344],"tcp_start":[0.57391,0.15482,0.13706],"tcp_to_object_dist_end":0.03656,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50823,0.06391,0.02688],"object_pos_start":[0.49653,0.03818,0.02144],"object_to_goal_dist_end":0.22423,"object_to_goal_dist_start":0.25107,"object_z_max":0.02695,"peak_contact_force":0.32595,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":6532.0,"raw_peak_contact_force":0.55965,"tcp_end":[0.52717,0.09712,0.06111],"tcp_start":[0.50317,0.05456,0.05344],"tcp_to_object_dist_end":0.05132,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50904,0.05877,0.02602],"object_pos_start":[0.50823,0.06391,0.02688],"object_to_goal_dist_end":0.22865,"object_to_goal_dist_start":0.22423,"object_z_max":0.02755,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3973.0,"raw_peak_contact_force":0.37717,"tcp_end":[0.53572,0.1483,0.08488],"tcp_start":[0.52717,0.09712,0.06111],"tcp_to_object_dist_end":0.11042,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":963.0,"n_steps_budget":1000.0,"object_pos_end":[0.50904,0.05877,0.02602],"object_pos_start":[0.50904,0.05877,0.02602],"object_to_goal_dist_end":0.22865,"object_to_goal_dist_start":0.22865,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":3852.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.50679,0.06183,0.21464],"tcp_start":[0.53572,0.1483,0.08488],"tcp_to_object_dist_end":0.18865,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50904,0.05877,0.02602],"object_pos_start":[0.50904,0.05877,0.02602],"object_to_goal_dist_end":0.22865,"object_to_goal_dist_start":0.22865,"object_z_max":0.02602,"peak_contact_force":306.28802,"phase_name":"insert_2","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":4.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.50684,0.06179,0.2147],"tcp_start":[0.50679,0.06183,0.21464],"tcp_to_object_dist_end":0.18871,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50904,0.05877,0.02602],"object_pos_start":[0.50904,0.05877,0.02602],"object_to_goal_dist_end":0.22865,"object_to_goal_dist_start":0.22865,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"push_2","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57751,0.1717,0.11505],"tcp_start":[0.50684,0.06179,0.2147],"tcp_to_object_dist_end":0.15927,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `291bc6f2bd023fc25503740a7343328e565e43fc71fa3c9c5d2fdbe2d4351fd2`; realized-scene SHA-256: `67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47616,-0.02015,0.03]},{"name":"goal","value":[0.63142,0.15919,0.19002]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.47616,-0.02015,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63142,0.15919,0.19002]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.60163,"average_solve_count":246.0,"average_success_count":246.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.07255,"insert_1.insertion_force":18.95619,"insert_2.insertion_depth":0.037,"insert_2.insertion_force":19.91501,"push_1.push_distance":0.09231,"push_1.push_speed":0.03087,"push_2.push_distance":0.07893,"retract_1.speed":0.03353},"optimized_scores":{"best_composite_score":-0.17443,"best_fitness_score":0.17557,"best_task_score":0.14623},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3996.0,"contact_point_centroid":[0.47616,-0.02015,-0.00196],"force_p95":0.12459,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12275,"phase_index":0.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.53682,0.07971,0.21414]},{"body_a":"world","body_b":"grasp_target","contact_count":2872.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52391,0.07219,0.10102]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49018,0.0194,0.06993]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.52442,0.06744,0.08792]},{"body_a":"world","body_b":"grasp_target","contact_count":3972.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5061,0.03235,0.15807]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"insert_2","phase_type":"insert","tcp_position_centroid":[0.4754,-0.01622,0.21609]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"push_2","phase_type":"push","tcp_position_centroid":[0.50815,0.04628,0.17678]}],"total_contact_groups":7},"final_pose_error":0.11316,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.47616,-0.02015,0.02602],"final_tcp_position":[0.54479,0.11023,0.14121],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":285.79559,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":3996.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.57391,0.15482,0.13706],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.22913,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":718.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2872.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.47708,-0.01045,0.07092],"tcp_start":[0.57391,0.15482,0.13706],"tcp_to_object_dist_end":0.04595,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":81.14225,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.50719,0.04875,0.07343],"tcp_start":[0.47708,-0.01045,0.07092],"tcp_to_object_dist_end":0.0892,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.54199,0.08306,0.10386],"tcp_start":[0.50719,0.04875,0.07343],"tcp_to_object_dist_end":0.14507,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":993.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":3972.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.4754,-0.01622,0.21609],"tcp_start":[0.54199,0.08306,0.10386],"tcp_to_object_dist_end":0.19012,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":285.79559,"phase_name":"insert_2","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":4.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.47543,-0.01628,0.21614],"tcp_start":[0.4754,-0.01622,0.21609],"tcp_to_object_dist_end":0.19016,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":81.14225,"phase_name":"push_2","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.54479,0.11023,0.14121],"tcp_start":[0.47543,-0.01628,0.21614],"tcp_to_object_dist_end":0.18703,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```