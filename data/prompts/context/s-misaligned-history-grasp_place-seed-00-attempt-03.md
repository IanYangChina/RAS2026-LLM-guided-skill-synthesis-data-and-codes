## Search State

- **Seed**: 0
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | insert → approach → push → retract → lift → insert → push | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | force_threshold_switch | position_control | position_control | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 8  | -0.1713 | 0.18 | ❌ rejected |
| 2 | insert → approach → push → retract → lift → insert → push | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | force_threshold_switch | position_control | position_control | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 8  | -0.1716 | 0.18 | ❌ rejected |
| 1 | insert → approach → push → retract → lift → insert → push | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | force_threshold_switch | position_control | position_control | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 8  | -0.1715 | 0.18 | ✅ accepted |
| 0 | insert → approach → push → retract → lift → insert → push | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | force_threshold_switch | position_control | position_control | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 8  | -0.1694 | 0.19 | ✅ accepted |

**Proposal policy**: task_score is 0.19 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.169) — your mutation base

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

- **Composite score**: -0.169
- **task_score** (E): 0.189
- **fitness_score**: 0.181  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.550

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| insert_1 | 0.00 | 1.00 | 0.2373 |
| approach_1 | 1.00 | 1.00 | 0.1834 |
| push_1 | 1.00 | 1.00 | 0.0936 |
| retract_1 | 0.33 | 1.00 | 0.0561 |
| lift_1 | 1.00 | 1.00 | 0.1588 |
| insert_2 | 1.00 | 1.00 | 0.0001 |
| push_2 | 1.00 | 1.00 | 0.1644 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| insert_1 | insert | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.574, 0.155, 0.137) | (0.497, 0.001, 0.030)→(0.497, 0.001, 0.026) | 0.263→0.265 | 1.00 / 4.000 | 0.123 | 0.138 |
| approach_1 | approach | 1.00 / step_budget | (0.574, 0.155, 0.137)→(0.497, 0.010, 0.058) | (0.497, 0.001, 0.026)→(0.494, -0.006, 0.022) | 0.265→0.273 | 1.00 / 7.667 | 0.425 | 0.434 |
| push_1 | push | 1.00 / time_limit | (0.497, 0.010, 0.058)→(0.540, 0.091, 0.072) | (0.494, -0.006, 0.022)→(0.497, 0.023, 0.022) | 0.273→0.251 | 1.00 / 4.333 | 27.249 | 0.470 |
| retract_1 | retract | 0.33 / step_budget | (0.540, 0.091, 0.072)→(0.548, 0.127, 0.108) | (0.497, 0.023, 0.022)→(0.493, 0.020, 0.023) | 0.251→0.253 | 1.00 / 4.000 | 0.123 | 0.244 |
| lift_1 | lift | 1.00 / step_budget | (0.548, 0.127, 0.108)→(0.492, 0.024, 0.213) | (0.493, 0.020, 0.023)→(0.493, 0.020, 0.023) | 0.253→0.253 | 1.00 / 4.000 | 0.123 | 0.123 |
| insert_2 | insert | 1.00 / force_exceeded | (0.492, 0.024, 0.213)→(0.492, 0.024, 0.213) | (0.493, 0.020, 0.023)→(0.493, 0.020, 0.023) | 0.253→0.253 | 1.00 / 4.000 | 285.544 | 0.123 |
| push_2 | push | 1.00 / time_limit | (0.492, 0.024, 0.213)→(0.564, 0.141, 0.126) | (0.493, 0.020, 0.023)→(0.493, 0.020, 0.023) | 0.253→0.253 | 1.00 / 4.000 | 54.136 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: None
- grasp_place_fitness: 0.185

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.185
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.246
- **Median Q (composite search score)**: -0.169
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.399


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.58848,"average_solve_count":243.0,"average_success_count":243.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.0502,"insert_1.insertion_force":7.88687,"insert_2.insertion_depth":0.07011,"insert_2.insertion_force":15.1756,"push_1.push_distance":0.12486,"push_1.push_speed":0.03581,"push_2.push_distance":0.18748,"retract_1.speed":0.03017},"optimized_scores":{"best_composite_score":-0.16862,"best_fitness_score":0.18138,"best_task_score":0.17493},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3526.0,"contact_point_centroid":[0.50845,-0.01607,-0.00539],"force_p95":0.64785,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.71513,"mean_force":0.33558,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51983,0.01674,0.05071]},{"body_a":"world","body_b":"grasp_target","contact_count":2788.0,"contact_point_centroid":[0.51326,-0.02339,-0.00233],"force_p95":0.4151,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64849,"mean_force":0.14959,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.54178,0.07208,0.09084]},{"body_a":"world","body_b":"grasp_target","contact_count":3901.0,"contact_point_centroid":[0.50579,-0.01404,-0.00206],"force_p95":0.13869,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.48545,"mean_force":0.12701,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.53153,0.06534,0.08154]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9526.0,"contact_point_centroid":[0.51919,-0.0262,0.04524],"force_p95":0.17349,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2536,"mean_force":0.07397,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51965,0.01636,0.0506]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":817.0,"contact_point_centroid":[0.52116,-0.04057,0.04955],"force_p95":0.15775,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1862,"mean_force":0.08228,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51719,0.00138,0.05629]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":60.0,"contact_point_centroid":[0.52452,0.0014,0.05259],"force_p95":0.13401,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15127,"mean_force":0.06799,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.53103,0.04769,0.05763]},{"body_a":"world","body_b":"grasp_target","contact_count":3996.0,"contact_point_centroid":[0.5137,-0.02302,-0.00196],"force_p95":0.12459,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12275,"phase_index":0.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.53682,0.07971,0.21414]},{"body_a":"world","body_b":"grasp_target","contact_count":3612.0,"contact_point_centroid":[0.50532,-0.01448,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51668,0.03383,0.15825]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.50532,-0.01448,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"insert_2","phase_type":"insert","tcp_position_centroid":[0.50322,-0.01056,0.21522]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.50532,-0.01448,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"push_2","phase_type":"push","tcp_position_centroid":[0.5299,0.05482,0.17327]}],"total_contact_groups":10},"final_pose_error":0.09446,"key_states":{"actual_goal_position":[0.5541,0.15165,0.22199],"final_object_position":[0.50532,-0.01448,0.02602],"final_tcp_position":[0.56043,0.12186,0.13537],"realised_goal_position":[0.5541,0.15165,0.22199],"realised_object_initial_position":[0.5137,-0.02302,0.03]},"peak_contact_force":273.36539,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.03],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26269,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":3996.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.57391,0.15482,0.13706],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.21814,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":6.0,"n_steps":714.0,"n_steps_budget":1000.0,"object_pos_end":[0.50743,-0.03794,0.01875],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.28183,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.62096,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3605.0,"raw_peak_contact_force":0.64849,"tcp_end":[0.51211,-0.01337,0.04916],"tcp_start":[0.57391,0.15482,0.13706],"tcp_to_object_dist_end":0.03937,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51599,-0.00455,0.02443],"object_pos_start":[0.50743,-0.03794,0.01875],"object_to_goal_dist_end":0.25472,"object_to_goal_dist_start":0.28183,"object_z_max":0.02442,"peak_contact_force":0.48301,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":13052.0,"raw_peak_contact_force":0.71513,"tcp_end":[0.53204,0.04665,0.05737],"tcp_start":[0.51211,-0.01337,0.04916],"tcp_to_object_dist_end":0.06296,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50532,-0.01448,0.02602],"object_pos_start":[0.51599,-0.00455,0.02443],"object_to_goal_dist_end":0.2615,"object_to_goal_dist_start":0.25472,"object_z_max":0.0262,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3961.0,"raw_peak_contact_force":0.48545,"tcp_end":[0.53471,0.0803,0.1048],"tcp_start":[0.53204,0.04665,0.05737],"tcp_to_object_dist_end":0.1267,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":903.0,"n_steps_budget":990.0,"object_pos_end":[0.50532,-0.01448,0.02602],"object_pos_start":[0.50532,-0.01448,0.02602],"object_to_goal_dist_end":0.2615,"object_to_goal_dist_start":0.2615,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":3612.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.50322,-0.01056,0.21522],"tcp_start":[0.53471,0.0803,0.1048],"tcp_to_object_dist_end":0.18926,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50532,-0.01448,0.02602],"object_pos_start":[0.50532,-0.01448,0.02602],"object_to_goal_dist_end":0.2615,"object_to_goal_dist_start":0.2615,"object_z_max":0.02602,"peak_contact_force":273.36539,"phase_name":"insert_2","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":4.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.50327,-0.01062,0.21528],"tcp_start":[0.50322,-0.01056,0.21522],"tcp_to_object_dist_end":0.18931,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50532,-0.01448,0.02602],"object_pos_start":[0.50532,-0.01448,0.02602],"object_to_goal_dist_end":0.2615,"object_to_goal_dist_start":0.2615,"object_z_max":0.02602,"peak_contact_force":81.14225,"phase_name":"push_2","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.56043,0.12186,0.13537],"tcp_start":[0.50327,-0.01062,0.21528],"tcp_to_object_dist_end":0.18326,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.69658,"average_solve_count":234.0,"average_success_count":234.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.05358,"insert_1.insertion_force":18.20443,"insert_2.insertion_depth":0.09034,"insert_2.insertion_force":11.11669,"push_1.push_distance":0.13465,"push_1.push_speed":0.09953,"push_2.push_distance":0.10137,"retract_1.speed":0.0299},"optimized_scores":{"best_composite_score":-0.16514,"best_fitness_score":0.18486,"best_task_score":0.24641},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3164.0,"contact_point_centroid":[0.49927,0.0738,-0.00299],"force_p95":0.39887,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57143,"mean_force":0.18649,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.54066,0.11662,0.06855]},{"body_a":"world","body_b":"grasp_target","contact_count":1776.0,"contact_point_centroid":[0.50117,0.04508,-0.00209],"force_p95":0.24696,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.53123,"mean_force":0.13583,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.53779,0.10569,0.0944]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1678.0,"contact_point_centroid":[0.51751,0.0274,0.0482],"force_p95":0.13261,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2843,"mean_force":0.07172,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50784,0.06646,0.05486]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":353.0,"contact_point_centroid":[0.51535,0.02023,0.05169],"force_p95":0.13451,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15854,"mean_force":0.07925,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50717,0.06052,0.05997]},{"body_a":"world","body_b":"grasp_target","contact_count":3996.0,"contact_point_centroid":[0.50118,0.04505,-0.00196],"force_p95":0.12459,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12275,"phase_index":0.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.53682,0.07971,0.21414]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.49821,0.09431,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5717,0.20078,0.1004]},{"body_a":"world","body_b":"grasp_target","contact_count":3972.0,"contact_point_centroid":[0.49821,0.09431,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52954,0.15695,0.15902]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.49821,0.09431,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"insert_2","phase_type":"insert","tcp_position_centroid":[0.49743,0.09835,0.20645]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.49821,0.09431,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"push_2","phase_type":"push","tcp_position_centroid":[0.54008,0.14329,0.15206]}],"total_contact_groups":9},"final_pose_error":0.01657,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.49821,0.09431,0.01602],"final_tcp_position":[0.58688,0.18997,0.10139],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":296.22586,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":3996.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.57391,0.15482,0.13706],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17225,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":13.0,"n_steps":444.0,"n_steps_budget":1000.0,"object_pos_end":[0.49706,0.03942,0.02166],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24979,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.53123,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2129.0,"raw_peak_contact_force":0.53123,"tcp_end":[0.50318,0.05456,0.05551],"tcp_start":[0.57391,0.15482,0.13706],"tcp_to_object_dist_end":0.03758,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49821,0.09431,0.01602],"object_pos_start":[0.49706,0.03942,0.02166],"object_to_goal_dist_end":0.21011,"object_to_goal_dist_start":0.24979,"object_z_max":0.02803,"peak_contact_force":0.12263,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4842.0,"raw_peak_contact_force":0.57143,"tcp_end":[0.58228,0.17898,0.08632],"tcp_start":[0.50318,0.05456,0.05551],"tcp_to_object_dist_end":0.13849,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49821,0.09431,0.01602],"object_pos_start":[0.49821,0.09431,0.01602],"object_to_goal_dist_end":0.21011,"object_to_goal_dist_start":0.21011,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.56675,0.21886,0.11673],"tcp_start":[0.58228,0.17898,0.08632],"tcp_to_object_dist_end":0.17422,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":993.0,"n_steps_budget":1000.0,"object_pos_end":[0.49821,0.09431,0.01602],"object_pos_start":[0.49821,0.09431,0.01602],"object_to_goal_dist_end":0.21011,"object_to_goal_dist_start":0.21011,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":3972.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.49743,0.09835,0.20645],"tcp_start":[0.56675,0.21886,0.11673],"tcp_to_object_dist_end":0.19048,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.49821,0.09431,0.01602],"object_pos_start":[0.49821,0.09431,0.01602],"object_to_goal_dist_end":0.21011,"object_to_goal_dist_start":0.21011,"object_z_max":0.01602,"peak_contact_force":296.22586,"phase_name":"insert_2","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":4.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.49745,0.0983,0.20649],"tcp_start":[0.49743,0.09835,0.20645],"tcp_to_object_dist_end":0.19051,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49821,0.09431,0.01602],"object_pos_start":[0.49821,0.09431,0.01602],"object_to_goal_dist_end":0.21011,"object_to_goal_dist_start":0.21011,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"push_2","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58688,0.18997,0.10139],"tcp_start":[0.49745,0.0983,0.20649],"tcp_to_object_dist_end":0.15589,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.60163,"average_solve_count":246.0,"average_success_count":246.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.07059,"insert_1.insertion_force":12.87986,"insert_2.insertion_depth":0.06157,"insert_2.insertion_force":7.19499,"push_1.push_distance":0.08391,"push_1.push_speed":0.03304,"push_2.push_distance":0.10213,"retract_1.speed":0.01045},"optimized_scores":{"best_composite_score":-0.17442,"best_fitness_score":0.17558,"best_task_score":0.14623},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3996.0,"contact_point_centroid":[0.47616,-0.02015,-0.00196],"force_p95":0.12459,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12275,"phase_index":0.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.53682,0.07971,0.21414]},{"body_a":"world","body_b":"grasp_target","contact_count":2864.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5239,0.0722,0.1001]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49016,0.01941,0.06835]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.52431,0.06737,0.08675]},{"body_a":"world","body_b":"grasp_target","contact_count":3972.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50601,0.0323,0.15755]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"insert_2","phase_type":"insert","tcp_position_centroid":[0.4754,-0.01622,0.21605]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"push_2","phase_type":"push","tcp_position_centroid":[0.50814,0.04628,0.17676]}],"total_contact_groups":7},"final_pose_error":0.11315,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.47616,-0.02015,0.02602],"final_tcp_position":[0.54479,0.11023,0.1412],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":287.04178,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":3996.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.57391,0.15482,0.13706],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.22913,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":716.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2864.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.47707,-0.01044,0.06908],"tcp_start":[0.57391,0.15482,0.13706],"tcp_to_object_dist_end":0.04415,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":81.14225,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.50717,0.04875,0.0721],"tcp_start":[0.47707,-0.01044,0.06908],"tcp_to_object_dist_end":0.0885,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.54185,0.08295,0.10285],"tcp_start":[0.50717,0.04875,0.0721],"tcp_to_object_dist_end":0.14439,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":993.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":3972.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.4754,-0.01622,0.21605],"tcp_start":[0.54185,0.08295,0.10285],"tcp_to_object_dist_end":0.19008,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":287.04178,"phase_name":"insert_2","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":4.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.47543,-0.01628,0.2161],"tcp_start":[0.4754,-0.01622,0.21605],"tcp_to_object_dist_end":0.19012,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":81.14225,"phase_name":"push_2","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.54479,0.11023,0.1412],"tcp_start":[0.47543,-0.01628,0.2161],"tcp_to_object_dist_end":0.18702,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```