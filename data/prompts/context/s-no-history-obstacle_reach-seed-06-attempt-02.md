## Search State

- **Seed**: 6
- **Iteration**: 3 / 15

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

- Task name: obstacle_reach
- Frozen realised-scene SHA-256: `bd4f35ed59709260e094776b661704e90745f7a52d08ebc05c5947cbc49435ce`
- Frozen task target: [0.7038164351471943, -0.015672913018666156, 0.15]
- Goal object position: (0.7038164351471943, -0.015672913018666156, 0.15)
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.5
- Force limit: 5.0 N
- Obstacle body: obstacle_block (contact = collision penalty)
- Robot initial TCP position: (0.35, 0.0, 0.32)
- Primary evaluation target: **TCP distance to goal position (Gaussian proximity kernel)**

## Scene Entities

robot:
  model: panda_full
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.35, 0, 0.32]
objects:
  - name: obstacle_block
    role: obstacle
    dynamics: static
    geometry: box
    dimensions_m: [0.08, 0.3, 0.3]
  - name: goal_marker
    role: target_marker
    dynamics: static
    geometry: point
task_landmarks:
  frozen_task_target: [0.7038, -0.0157, 0.15]
  frozen_obstacle_position: [0.5, 0, 0.15]
  frozen_targets: {'task_goal': [0.7038164351471943, -0.015672913018666156, 0.15]}
  frozen_obstacles: {'obstacle_block': [0.5, 0.0, 0.15]}
  goal_tolerance_m: 0.02
  force_limit_n: 5
  obstacle_height_m: 0.3
  force_scale_n: 5
  realized_scene_sha256: bd4f35ed59709260e094776b661704e90745f7a52d08ebc05c5947cbc49435ce

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
| `object` | offset from object initial position | approach/contact targets near object |
| `goal` | offset from task goal position (0.7038164351471943, -0.015672913018666156, 0.15) | final destination targets |
| `fixture` | offset from fixture pose (0.5, 0.0, 0.15) | approach/contact targets near fixture |

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

## Current Skill (Q=-0.380) — your mutation base

```yaml
skill: obstacle_reach
skill_type: arm_gripper
phases:
- id: rotate_1
  type: rotate
  generator: impedance_motion
  control: impedance_control
  termination: time_limit
- id: align_1
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    lateral_offset_y:
      type: scalar
      range:
      - -0.01
      - 0.01
- id: lift_1
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
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
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: approach_1
  type: approach
  generator: arc_cartesian
  control: force_threshold_switch
  termination: pose_tolerance
- id: approach_2
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
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
- id: grasp_1
  type: grasp
  control: position_control
  termination: time_limit
  end_effector_action: force_grasp

```

## Design Metrics

- **Composite score**: -0.380
- **task_score** (E): 0.000
- **fitness_score**: 0.000  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
  → CMA-ES cannot optimise this structure (shaped reward also near zero)
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.380

**⚠ Warning**: CMA-ES stagnated + low fitness_score → structure may be fundamentally incompatible with task

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| rotate_1 | 1.00 | 1.00 | 0.0557 |
| align_1 | 0.00 | 1.00 | 0.0450 |
| lift_1 | 1.00 | 0.00 | 0.0137 |
| push_1 | 0.00 | 0.67 | 0.0661 |
| approach_1 | 1.00 | 0.00 | 0.1895 |
| approach_2 | 1.00 | 0.00 | 0.0056 |
| descend_1 | 1.00 | 0.00 | 0.1901 |
| grasp_1 | 1.00 | 1.00 | 0.0106 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force | Obstacle/contact |
|---|---|---|---|---|---|---|---|---|---|
| rotate_1 | rotate | 1.00 / time_limit | (0.350, -0.000, 0.321)→(0.406, 0.000, 0.315) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.717→0.717 | 1.00 / 1.000 | 277.519 | 402.924 | link7 ↔ obstacle_block/obstacle_block_geom |
| align_1 | align | 0.00 / step_budget | (0.406, 0.000, 0.315)→(0.427, 0.000, 0.354) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.717→0.717 | 1.00 / 1.000 | 248.915 | 274.244 | link6 ↔ obstacle_block/obstacle_block_geom |
| lift_1 | lift | 1.00 / step_budget | (0.427, 0.000, 0.354)→(0.440, -0.000, 0.350) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.717→0.717 | 0.00 / 0.000 | 0.000 | 169.078 | link6 ↔ obstacle_block/obstacle_block_geom |
| push_1 | push | 0.00 / step_budget | (0.440, -0.000, 0.350)→(0.500, -0.000, 0.377) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.717→0.717 | 0.67 / 0.667 | 177.074 | 300.489 | link6 ↔ obstacle_block/obstacle_block_geom |
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.377)→(0.688, -0.000, 0.354) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.717→0.717 | 0.00 / 0.000 | 0.000 | 226.483 | link6 ↔ obstacle_block/obstacle_block_geom |
| approach_2 | approach | 1.00 / step_budget | (0.688, -0.000, 0.354)→(0.691, -0.000, 0.349) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.717→0.717 | 0.00 / 0.000 | 0.000 | 0.000 | — |
| descend_1 | descend | 1.00 / step_budget | (0.691, -0.000, 0.349)→(0.697, -0.000, 0.159) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.717→0.717 | 0.00 / 0.000 | 0.000 | 0.000 | — |
| grasp_1 | grasp | 1.00 / step_budget | (0.697, -0.000, 0.159)→(0.694, -0.000, 0.149) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.717→0.717 | 1.00 / 1.000 | 57.918 | 68.520 | link5 ↔ obstacle_block/obstacle_block_geom |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- obstacle_clearance: 0.753
- path_efficiency: 0.602
- arc_smoothness: 0.985
- collision_factor: 0.000  (exp(−peak_force / force_scale))
- peak_obstacle_force: 402.924 N
- collision_location: obstacle_block  (or None if no contact)
- final_tcp_distance: 0.019
- min_tcp_distance: 0.019
- tcp_proximity_score: 0.879
- goal_reached_rate: 1.000
- peak_obstacle_counterbody: link7
- peak_obstacle_countergeom: None
- peak_obstacle_obstacle_body: obstacle_block
- peak_obstacle_obstacle_geom: obstacle_block_geom

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.000
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.000
- **Median Q (composite search score)**: -0.380
- **K-run variance**: 0.0000
- **Stagnated**: yes
  → Parameter optimiser converged to local optimum; structural change likely needed
- **Stop reason**: tolfun
- **Mean generations**: 2.0
- **Final σ (mean)**: 0.386


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `89af5e6373a217810de823e85ed206d27eafc89c151e748b39ede2d750fe7c5e`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"object_xy_delta":[0.0,0.0]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `6b4e4a3a850359b999c84710456096c65c7b37ffa6a27fd54ebaec8821f1dcd2`; realized-scene SHA-256: `bd4f35ed59709260e094776b661704e90745f7a52d08ebc05c5947cbc49435ce`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.0,0.15]},{"name":"goal","value":[0.70382,-0.01567,0.15]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":5.0},{"name":"obstacle_height_m","value":0.3},{"name":"force_scale_n","value":5.0}],"object_starts":[],"obstacles":[{"name":"obstacle_block","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,0.0,0.15]}],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.70382,-0.01567,0.15]}],"task_name":"obstacle_reach"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.61472,"average_solve_count":231.0,"average_success_count":231.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_y":-0.00525,"approach_2.speed":0.05282,"push_1.push_depth":0.04999,"push_1.push_speed":0.09602},"optimized_scores":{"best_composite_score":-0.38,"best_fitness_score":0.0,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"obstacle_block","body_b":"link7","contact_count":603.0,"contact_point_centroid":[0.46008,0.00101,0.29994],"force_p95":353.04166,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":402.92406,"mean_force":309.44787,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.40497,2e-05,0.30212]},{"body_a":"obstacle_block","body_b":"link6","contact_count":970.0,"contact_point_centroid":[0.53996,-0.00385,0.29991],"force_p95":275.14151,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":304.5705,"mean_force":224.61304,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46955,1e-05,0.37237]},{"body_a":"obstacle_block","body_b":"link6","contact_count":190.0,"contact_point_centroid":[0.52527,-0.00446,0.29994],"force_p95":258.8246,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":274.24353,"mean_force":250.04585,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.42396,2e-05,0.34776]},{"body_a":"obstacle_block","body_b":"link7","contact_count":824.0,"contact_point_centroid":[0.46002,0.00154,0.29993],"force_p95":267.15948,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":272.0597,"mean_force":246.7527,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.41156,3e-05,0.32939]},{"body_a":"obstacle_block","body_b":"link6","contact_count":33.0,"contact_point_centroid":[0.54,-0.00507,0.29999],"force_p95":163.03959,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":169.07836,"mean_force":95.60661,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4326,-4e-05,0.35241]},{"body_a":"obstacle_block","body_b":"link5","contact_count":378.0,"contact_point_centroid":[0.54,0.03195,0.29997],"force_p95":66.25583,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":70.91331,"mean_force":60.58467,"phase_index":7.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.69361,-0.00018,0.14922]},{"body_a":"obstacle_block","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.54,-0.00268,0.3],"force_p95":56.99569,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":56.99569,"mean_force":56.99569,"phase_index":4.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50245,-0.00018,0.3753]}],"total_contact_groups":7},"final_pose_error":0.00974,"key_states":{"actual_goal_position":[0.70382,-0.01567,0.15],"actual_obstacle_position":[0.5,0.0,0.15],"final_tcp_position":[0.69665,-0.00014,0.15914],"realised_goal_position":[0.70382,-0.01567,0.15],"realised_object_initial_position":[0.0,0.0,0.0],"realised_obstacle_position":[0.5,0.0,0.15]},"peak_contact_force":402.92406,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.71979,"object_to_goal_dist_start":0.71979,"object_z_max":0.0,"peak_contact_force":277.51859,"phase_name":"rotate_1","phase_peak_obstacle_force":402.92406,"phase_type":"rotate","raw_contact_event_count":603.0,"raw_peak_contact_force":402.92406,"tcp_end":[0.40568,3e-05,0.31495],"tcp_start":[0.3503,-0.0,0.32087],"tcp_to_object_dist_end":0.51359,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.71979,"object_to_goal_dist_start":0.71979,"object_z_max":0.0,"peak_contact_force":248.91504,"phase_name":"align_1","phase_peak_obstacle_force":274.24353,"phase_type":"align","raw_contact_event_count":1014.0,"raw_peak_contact_force":274.24353,"tcp_end":[0.4273,1e-05,0.35439],"tcp_start":[0.40568,3e-05,0.31495],"tcp_to_object_dist_end":0.55513,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":77.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.71979,"object_to_goal_dist_start":0.71979,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"lift_1","phase_peak_obstacle_force":169.07836,"phase_type":"lift","raw_contact_event_count":33.0,"raw_peak_contact_force":169.07836,"tcp_end":[0.44014,-8e-05,0.34962],"tcp_start":[0.4273,1e-05,0.35439],"tcp_to_object_dist_end":0.5621,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.71979,"object_to_goal_dist_start":0.71979,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":304.5705,"phase_type":"push","raw_contact_event_count":970.0,"raw_peak_contact_force":304.5705,"tcp_end":[0.50242,-0.00017,0.37534],"tcp_start":[0.44014,-8e-05,0.34962],"tcp_to_object_dist_end":0.62715,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":988.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.71979,"object_to_goal_dist_start":0.71979,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":56.99569,"phase_type":"approach","raw_contact_event_count":1.0,"raw_peak_contact_force":56.99569,"tcp_end":[0.6902,-0.00012,0.35088],"tcp_start":[0.50242,-0.00017,0.37534],"tcp_to_object_dist_end":0.77427,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.71979,"object_to_goal_dist_start":0.71979,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.69182,-0.00015,0.34787],"tcp_start":[0.6902,-0.00012,0.35088],"tcp_to_object_dist_end":0.77436,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":456.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.71979,"object_to_goal_dist_start":0.71979,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.69665,-0.00014,0.15914],"tcp_start":[0.69182,-0.00015,0.34787],"tcp_to_object_dist_end":0.7146,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.71979,"object_to_goal_dist_start":0.71979,"object_z_max":0.0,"peak_contact_force":59.90189,"phase_name":"grasp_1","phase_peak_obstacle_force":70.91331,"phase_type":"grasp","raw_contact_event_count":378.0,"raw_peak_contact_force":70.91331,"tcp_end":[0.69363,-0.00016,0.14926],"tcp_start":[0.69665,-0.00014,0.15914],"tcp_to_object_dist_end":0.7095,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `3dbedbccfafbb480e6b8853d24674113c48a7d6ac70107463f0222214d243e47`; realized-scene SHA-256: `f5f2ee542fad8ea5b5618e39465af4fd2d024325ca55c46b8aecfe9ce333bfb2`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.0,0.15]},{"name":"goal","value":[0.71251,0.03972,0.15]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":5.0},{"name":"obstacle_height_m","value":0.3},{"name":"force_scale_n","value":5.0}],"object_starts":[],"obstacles":[{"name":"obstacle_block","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,0.0,0.15]}],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.71251,0.03972,0.15]}],"task_name":"obstacle_reach"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.61472,"average_solve_count":231.0,"average_success_count":231.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_y":0.00441,"approach_2.speed":0.05687,"push_1.push_depth":0.06159,"push_1.push_speed":0.09997},"optimized_scores":{"best_composite_score":-0.38,"best_fitness_score":0.0,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"obstacle_block","body_b":"link7","contact_count":603.0,"contact_point_centroid":[0.46008,0.00101,0.29994],"force_p95":353.04166,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":402.92406,"mean_force":309.44787,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.40497,2e-05,0.30212]},{"body_a":"obstacle_block","body_b":"link6","contact_count":2.0,"contact_point_centroid":[0.53999,-0.00238,0.29999],"force_p95":354.99942,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":371.04734,"mean_force":210.56818,"phase_index":4.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50572,-0.00017,0.37285]},{"body_a":"obstacle_block","body_b":"link6","contact_count":965.0,"contact_point_centroid":[0.53996,-0.00379,0.29991],"force_p95":281.0404,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":305.93006,"mean_force":227.36555,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47104,0.0,0.37238]},{"body_a":"obstacle_block","body_b":"link6","contact_count":190.0,"contact_point_centroid":[0.52527,-0.00446,0.29994],"force_p95":258.8246,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":274.24353,"mean_force":250.04585,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.42396,2e-05,0.34776]},{"body_a":"obstacle_block","body_b":"link7","contact_count":824.0,"contact_point_centroid":[0.46002,0.00154,0.29993],"force_p95":267.15948,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":272.0597,"mean_force":246.7527,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.41156,3e-05,0.32939]},{"body_a":"obstacle_block","body_b":"link6","contact_count":33.0,"contact_point_centroid":[0.54,-0.00507,0.29999],"force_p95":163.03959,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":169.07836,"mean_force":95.60661,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4326,-4e-05,0.35241]},{"body_a":"obstacle_block","body_b":"link5","contact_count":380.0,"contact_point_centroid":[0.54,0.0319,0.29997],"force_p95":70.32736,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":76.77714,"mean_force":63.96159,"phase_index":7.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.69372,-0.00017,0.14954]}],"total_contact_groups":7},"final_pose_error":0.00973,"key_states":{"actual_goal_position":[0.71251,0.03972,0.15],"actual_obstacle_position":[0.5,0.0,0.15],"final_tcp_position":[0.69665,-0.00014,0.15913],"realised_goal_position":[0.71251,0.03972,0.15],"realised_object_initial_position":[0.0,0.0,0.0],"realised_obstacle_position":[0.5,0.0,0.15]},"peak_contact_force":402.92406,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.72921,"object_to_goal_dist_start":0.72921,"object_z_max":0.0,"peak_contact_force":277.51859,"phase_name":"rotate_1","phase_peak_obstacle_force":402.92406,"phase_type":"rotate","raw_contact_event_count":603.0,"raw_peak_contact_force":402.92406,"tcp_end":[0.40568,3e-05,0.31495],"tcp_start":[0.3503,-0.0,0.32087],"tcp_to_object_dist_end":0.51359,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.72921,"object_to_goal_dist_start":0.72921,"object_z_max":0.0,"peak_contact_force":248.91504,"phase_name":"align_1","phase_peak_obstacle_force":274.24353,"phase_type":"align","raw_contact_event_count":1014.0,"raw_peak_contact_force":274.24353,"tcp_end":[0.4273,1e-05,0.35439],"tcp_start":[0.40568,3e-05,0.31495],"tcp_to_object_dist_end":0.55513,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":77.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.72921,"object_to_goal_dist_start":0.72921,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"lift_1","phase_peak_obstacle_force":169.07836,"phase_type":"lift","raw_contact_event_count":33.0,"raw_peak_contact_force":169.07836,"tcp_end":[0.44014,-8e-05,0.34962],"tcp_start":[0.4273,1e-05,0.35439],"tcp_to_object_dist_end":0.5621,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.72921,"object_to_goal_dist_start":0.72921,"object_z_max":0.0,"peak_contact_force":273.70989,"phase_name":"push_1","phase_peak_obstacle_force":305.93006,"phase_type":"push","raw_contact_event_count":965.0,"raw_peak_contact_force":305.93006,"tcp_end":[0.5057,-0.00017,0.37286],"tcp_start":[0.44014,-8e-05,0.34962],"tcp_to_object_dist_end":0.6283,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":982.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.72921,"object_to_goal_dist_start":0.72921,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":371.04734,"phase_type":"approach","raw_contact_event_count":2.0,"raw_peak_contact_force":371.04734,"tcp_end":[0.69012,-0.00012,0.35073],"tcp_start":[0.5057,-0.00017,0.37286],"tcp_to_object_dist_end":0.77413,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.72921,"object_to_goal_dist_start":0.72921,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.69175,-0.00015,0.34776],"tcp_start":[0.69012,-0.00012,0.35073],"tcp_to_object_dist_end":0.77425,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":456.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.72921,"object_to_goal_dist_start":0.72921,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.69665,-0.00014,0.15913],"tcp_start":[0.69175,-0.00015,0.34776],"tcp_to_object_dist_end":0.71459,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.72921,"object_to_goal_dist_start":0.72921,"object_z_max":0.0,"peak_contact_force":63.14094,"phase_name":"grasp_1","phase_peak_obstacle_force":76.77714,"phase_type":"grasp","raw_contact_event_count":380.0,"raw_peak_contact_force":76.77714,"tcp_end":[0.69373,-0.00015,0.14959],"tcp_start":[0.69665,-0.00014,0.15913],"tcp_to_object_dist_end":0.70967,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `71285845baf1b8f9da7d5ce873550759a4c17d69a356cdc4cf82cc31badfb976`; realized-scene SHA-256: `4d99f589f09839c4f3a4e389174672e239f050e8ccee110af89dc738cbe9e683`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.0,0.15]},{"name":"goal","value":[0.6827,0.04873,0.15]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":5.0},{"name":"obstacle_height_m","value":0.3},{"name":"force_scale_n","value":5.0}],"object_starts":[],"obstacles":[{"name":"obstacle_block","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,0.0,0.15]}],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.6827,0.04873,0.15]}],"task_name":"obstacle_reach"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.64807,"average_solve_count":233.0,"average_success_count":233.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_y":-0.00086,"approach_2.speed":0.05577,"push_1.push_depth":0.0149,"push_1.push_speed":0.08105},"optimized_scores":{"best_composite_score":-0.38,"best_fitness_score":0.0,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"obstacle_block","body_b":"link7","contact_count":603.0,"contact_point_centroid":[0.46008,0.00101,0.29994],"force_p95":353.04166,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":402.92406,"mean_force":309.44787,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.40497,2e-05,0.30212]},{"body_a":"obstacle_block","body_b":"link6","contact_count":984.0,"contact_point_centroid":[0.53997,-0.00408,0.29993],"force_p95":251.84612,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":290.96709,"mean_force":215.28364,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46467,-0.0,0.37193]},{"body_a":"obstacle_block","body_b":"link6","contact_count":190.0,"contact_point_centroid":[0.52527,-0.00446,0.29994],"force_p95":258.8246,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":274.24353,"mean_force":250.04585,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.42396,2e-05,0.34776]},{"body_a":"obstacle_block","body_b":"link7","contact_count":824.0,"contact_point_centroid":[0.46002,0.00154,0.29993],"force_p95":267.15948,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":272.0597,"mean_force":246.7527,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.41156,3e-05,0.32939]},{"body_a":"obstacle_block","body_b":"link6","contact_count":2.0,"contact_point_centroid":[0.53999,-0.00357,0.29998],"force_p95":241.10354,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":251.40601,"mean_force":148.38129,"phase_index":4.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49154,-0.00012,0.38341]},{"body_a":"obstacle_block","body_b":"link6","contact_count":33.0,"contact_point_centroid":[0.54,-0.00507,0.29999],"force_p95":163.03959,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":169.07836,"mean_force":95.60661,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4326,-4e-05,0.35241]},{"body_a":"obstacle_block","body_b":"link5","contact_count":371.0,"contact_point_centroid":[0.54,0.03213,0.29998],"force_p95":55.21636,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":57.87072,"mean_force":51.17929,"phase_index":7.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.69316,-0.00021,0.14819]}],"total_contact_groups":7},"final_pose_error":0.00972,"key_states":{"actual_goal_position":[0.6827,0.04873,0.15],"actual_obstacle_position":[0.5,0.0,0.15],"final_tcp_position":[0.6965,-0.00014,0.15907],"realised_goal_position":[0.6827,0.04873,0.15],"realised_object_initial_position":[0.0,0.0,0.0],"realised_obstacle_position":[0.5,0.0,0.15]},"peak_contact_force":402.92406,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.70068,"object_to_goal_dist_start":0.70068,"object_z_max":0.0,"peak_contact_force":277.51859,"phase_name":"rotate_1","phase_peak_obstacle_force":402.92406,"phase_type":"rotate","raw_contact_event_count":603.0,"raw_peak_contact_force":402.92406,"tcp_end":[0.40568,3e-05,0.31495],"tcp_start":[0.3503,-0.0,0.32087],"tcp_to_object_dist_end":0.51359,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.70068,"object_to_goal_dist_start":0.70068,"object_z_max":0.0,"peak_contact_force":248.91504,"phase_name":"align_1","phase_peak_obstacle_force":274.24353,"phase_type":"align","raw_contact_event_count":1014.0,"raw_peak_contact_force":274.24353,"tcp_end":[0.4273,1e-05,0.35439],"tcp_start":[0.40568,3e-05,0.31495],"tcp_to_object_dist_end":0.55513,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":77.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.70068,"object_to_goal_dist_start":0.70068,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"lift_1","phase_peak_obstacle_force":169.07836,"phase_type":"lift","raw_contact_event_count":33.0,"raw_peak_contact_force":169.07836,"tcp_end":[0.44014,-8e-05,0.34962],"tcp_start":[0.4273,1e-05,0.35439],"tcp_to_object_dist_end":0.5621,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.70068,"object_to_goal_dist_start":0.70068,"object_z_max":0.0,"peak_contact_force":257.51152,"phase_name":"push_1","phase_peak_obstacle_force":290.96709,"phase_type":"push","raw_contact_event_count":984.0,"raw_peak_contact_force":290.96709,"tcp_end":[0.49151,-0.00012,0.38341],"tcp_start":[0.44014,-8e-05,0.34962],"tcp_to_object_dist_end":0.62337,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.70068,"object_to_goal_dist_start":0.70068,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":251.40601,"phase_type":"approach","raw_contact_event_count":2.0,"raw_peak_contact_force":251.40601,"tcp_end":[0.68329,-0.00012,0.35923],"tcp_start":[0.49151,-0.00012,0.38341],"tcp_to_object_dist_end":0.77197,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":41.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.70068,"object_to_goal_dist_start":0.70068,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.69025,-0.00014,0.35186],"tcp_start":[0.68329,-0.00012,0.35923],"tcp_to_object_dist_end":0.77476,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":466.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.70068,"object_to_goal_dist_start":0.70068,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.6965,-0.00014,0.15907],"tcp_start":[0.69025,-0.00014,0.35186],"tcp_to_object_dist_end":0.71444,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.70068,"object_to_goal_dist_start":0.70068,"object_z_max":0.0,"peak_contact_force":50.7126,"phase_name":"grasp_1","phase_peak_obstacle_force":57.87072,"phase_type":"grasp","raw_contact_event_count":371.0,"raw_peak_contact_force":57.87072,"tcp_end":[0.69317,-0.00019,0.14822],"tcp_start":[0.6965,-0.00014,0.15907],"tcp_to_object_dist_end":0.70884,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```