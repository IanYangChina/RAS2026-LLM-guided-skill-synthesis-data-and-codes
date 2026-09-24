## Search State

- **Seed**: 4
- **Iteration**: 2 / 15

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
- Frozen realised-scene SHA-256: `f04b195e402ac39779662418f5ff4bea89ac7f3f52518881a8eb9756a965f187`
- Frozen task target: [0.7443056105572368, 0.0011327552814361583, 0.15]
- Goal object position: (0.7443056105572368, 0.0011327552814361583, 0.15)
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
  frozen_task_target: [0.7443, 0.0011, 0.15]
  frozen_obstacle_position: [0.5, 0, 0.15]
  frozen_targets: {'task_goal': [0.7443056105572368, 0.0011327552814361583, 0.15]}
  frozen_obstacles: {'obstacle_block': [0.5, 0.0, 0.15]}
  goal_tolerance_m: 0.02
  force_limit_n: 5
  obstacle_height_m: 0.3
  force_scale_n: 5
  realized_scene_sha256: f04b195e402ac39779662418f5ff4bea89ac7f3f52518881a8eb9756a965f187

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
| `goal` | offset from task goal position (0.7443056105572368, 0.0011327552814361583, 0.15) | final destination targets |
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

## Current Skill (Q=-0.180) — your mutation base

```yaml
skill: obstacle_reach
skill_type: arm_gripper
phases:
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
- id: release_1
  type: release
  generator: linear_cartesian
  control: position_control
  termination: time_limit
  end_effector_action: open

```

## Design Metrics

- **Composite score**: -0.180
- **task_score** (E): 0.000
- **fitness_score**: 0.000  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
  → CMA-ES cannot optimise this structure (shaped reward also near zero)
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.180

**⚠ Warning**: CMA-ES stagnated + low fitness_score → structure may be fundamentally incompatible with task

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| push_1 | 1.00 | 1.00 | 0.0574 |
| align_1 | 0.00 | 1.00 | 0.0416 |
| release_1 | 1.00 | 1.00 | 0.0746 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force | Obstacle/contact |
|---|---|---|---|---|---|---|---|---|---|
| push_1 | push | 1.00 / time_limit | (0.350, -0.000, 0.321)→(0.404, 0.000, 0.300) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.742→0.742 | 1.00 / 1.000 | 310.142 | 395.279 | link7 ↔ obstacle_block/obstacle_block_geom |
| align_1 | align | 0.00 / step_budget | (0.404, 0.000, 0.300)→(0.418, 0.000, 0.340) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.742→0.742 | 1.00 / 1.000 | 258.491 | 353.476 | link7 ↔ obstacle_block/obstacle_block_geom |
| release_1 | release | 1.00 / time_limit | (0.418, 0.000, 0.340)→(0.469, 0.000, 0.393) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.742→0.742 | 1.00 / 1.000 | 67.714 | 290.503 | link6 ↔ obstacle_block/obstacle_block_geom |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- obstacle_clearance: 0.648
- path_efficiency: 0.690
- arc_smoothness: 0.984
- collision_factor: 0.000  (exp(−peak_force / force_scale))
- peak_obstacle_force: 395.279 N
- collision_location: obstacle_block  (or None if no contact)
- final_tcp_distance: 0.367
- min_tcp_distance: 0.365
- tcp_proximity_score: 0.087
- goal_reached_rate: 0.000
- peak_obstacle_counterbody: link7
- peak_obstacle_countergeom: None
- peak_obstacle_obstacle_body: obstacle_block
- peak_obstacle_obstacle_geom: obstacle_block_geom

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.000
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.000
- **Median Q (composite search score)**: -0.180
- **K-run variance**: 0.0000
- **Stagnated**: yes
  → Parameter optimiser converged to local optimum; structural change likely needed
- **Stop reason**: tolfun
- **Mean generations**: 2.0
- **Final σ (mean)**: 0.308


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `d910c77cb638a69341ed671296c717a208cd48823489ef9211f18ea0e1b939e7`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"object_xy_delta":[0.0,0.0]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `f90839fb981b04e986bac696c468b50f4838fff85cbd7f5c1f7b2ee178b7b0de`; realized-scene SHA-256: `f04b195e402ac39779662418f5ff4bea89ac7f3f52518881a8eb9756a965f187`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.0,0.15]},{"name":"goal","value":[0.74431,0.00113,0.15]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":5.0},{"name":"obstacle_height_m","value":0.3},{"name":"force_scale_n","value":5.0}],"object_starts":[],"obstacles":[{"name":"obstacle_block","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,0.0,0.15]}],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.74431,0.00113,0.15]}],"task_name":"obstacle_reach"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.75,"average_solve_count":108.0,"average_success_count":108.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_y":0.00732,"push_1.push_distance":0.12685,"push_1.push_speed":0.05303},"optimized_scores":{"best_composite_score":-0.18,"best_fitness_score":0.0,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"obstacle_block","body_b":"link7","contact_count":410.0,"contact_point_centroid":[0.46009,0.00097,0.29995],"force_p95":351.91093,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":395.27948,"mean_force":326.71405,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.40486,1e-05,0.29482]},{"body_a":"obstacle_block","body_b":"link7","contact_count":1000.0,"contact_point_centroid":[0.46003,0.00145,0.29994],"force_p95":301.09672,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":353.476,"mean_force":270.37359,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.40794,-0.0,0.32052]},{"body_a":"obstacle_block","body_b":"link6","contact_count":996.0,"contact_point_centroid":[0.5371,-0.00483,0.29989],"force_p95":255.6377,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":290.50282,"mean_force":205.84449,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.44689,0.0001,0.37321]},{"body_a":"obstacle_block","body_b":"link7","contact_count":154.0,"contact_point_centroid":[0.46,0.00169,0.29995],"force_p95":136.49016,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":229.90567,"mean_force":104.67881,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.41909,-1e-05,0.34132]}],"total_contact_groups":4},"final_pose_error":0.33505,"key_states":{"actual_goal_position":[0.74431,0.00113,0.15],"actual_obstacle_position":[0.5,0.0,0.15],"final_tcp_position":[0.46919,0.0002,0.39286],"realised_goal_position":[0.74431,0.00113,0.15],"realised_object_initial_position":[0.0,0.0,0.0],"realised_obstacle_position":[0.5,0.0,0.15]},"peak_contact_force":395.27948,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.75927,"object_to_goal_dist_start":0.75927,"object_z_max":0.0,"peak_contact_force":310.14242,"phase_name":"push_1","phase_peak_obstacle_force":395.27948,"phase_type":"push","raw_contact_event_count":410.0,"raw_peak_contact_force":395.27948,"tcp_end":[0.40393,1e-05,0.30046],"tcp_start":[0.3503,-0.0,0.32087],"tcp_to_object_dist_end":0.50343,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.75927,"object_to_goal_dist_start":0.75927,"object_z_max":0.0,"peak_contact_force":258.49113,"phase_name":"align_1","phase_peak_obstacle_force":353.476,"phase_type":"align","raw_contact_event_count":1000.0,"raw_peak_contact_force":353.476,"tcp_end":[0.41773,0.0,0.33966],"tcp_start":[0.40393,1e-05,0.30046],"tcp_to_object_dist_end":0.5384,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.75927,"object_to_goal_dist_start":0.75927,"object_z_max":0.0,"peak_contact_force":67.71417,"phase_name":"release_1","phase_peak_obstacle_force":290.50282,"phase_type":"release","raw_contact_event_count":1150.0,"raw_peak_contact_force":290.50282,"tcp_end":[0.46944,0.00019,0.3934],"tcp_start":[0.41773,0.0,0.33966],"tcp_to_object_dist_end":0.61248,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `94e78c883a04c29d3c37cc716fa077d5c59698d148b7b4f0e399907a3c99cbc8`; realized-scene SHA-256: `35b656cc89b57a5f115ac5b9cfa690565debfcfd5af880d0b6438b747265b590`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.0,0.15]},{"name":"goal","value":[0.7305,0.03079,0.15]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":5.0},{"name":"obstacle_height_m","value":0.3},{"name":"force_scale_n","value":5.0}],"object_starts":[],"obstacles":[{"name":"obstacle_block","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,0.0,0.15]}],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.7305,0.03079,0.15]}],"task_name":"obstacle_reach"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.75,"average_solve_count":108.0,"average_success_count":108.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_y":0.00042,"push_1.push_distance":0.1022,"push_1.push_speed":0.06357},"optimized_scores":{"best_composite_score":-0.18,"best_fitness_score":0.0,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"obstacle_block","body_b":"link7","contact_count":410.0,"contact_point_centroid":[0.46009,0.00097,0.29995],"force_p95":351.91093,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":395.27948,"mean_force":326.71405,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.40486,1e-05,0.29482]},{"body_a":"obstacle_block","body_b":"link7","contact_count":1000.0,"contact_point_centroid":[0.46003,0.00145,0.29994],"force_p95":301.09672,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":353.476,"mean_force":270.37359,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.40794,-0.0,0.32052]},{"body_a":"obstacle_block","body_b":"link6","contact_count":996.0,"contact_point_centroid":[0.5371,-0.00483,0.29989],"force_p95":255.6377,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":290.50282,"mean_force":205.84449,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.44689,0.0001,0.37321]},{"body_a":"obstacle_block","body_b":"link7","contact_count":154.0,"contact_point_centroid":[0.46,0.00169,0.29995],"force_p95":136.49016,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":229.90567,"mean_force":104.67881,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.41909,-1e-05,0.34132]}],"total_contact_groups":4},"final_pose_error":0.33505,"key_states":{"actual_goal_position":[0.7305,0.03079,0.15],"actual_obstacle_position":[0.5,0.0,0.15],"final_tcp_position":[0.46919,0.0002,0.39286],"realised_goal_position":[0.7305,0.03079,0.15],"realised_object_initial_position":[0.0,0.0,0.0],"realised_obstacle_position":[0.5,0.0,0.15]},"peak_contact_force":395.27948,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.74638,"object_to_goal_dist_start":0.74638,"object_z_max":0.0,"peak_contact_force":310.14242,"phase_name":"push_1","phase_peak_obstacle_force":395.27948,"phase_type":"push","raw_contact_event_count":410.0,"raw_peak_contact_force":395.27948,"tcp_end":[0.40393,1e-05,0.30046],"tcp_start":[0.3503,-0.0,0.32087],"tcp_to_object_dist_end":0.50343,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.74638,"object_to_goal_dist_start":0.74638,"object_z_max":0.0,"peak_contact_force":258.49113,"phase_name":"align_1","phase_peak_obstacle_force":353.476,"phase_type":"align","raw_contact_event_count":1000.0,"raw_peak_contact_force":353.476,"tcp_end":[0.41773,0.0,0.33966],"tcp_start":[0.40393,1e-05,0.30046],"tcp_to_object_dist_end":0.5384,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.74638,"object_to_goal_dist_start":0.74638,"object_z_max":0.0,"peak_contact_force":67.71417,"phase_name":"release_1","phase_peak_obstacle_force":290.50282,"phase_type":"release","raw_contact_event_count":1150.0,"raw_peak_contact_force":290.50282,"tcp_end":[0.46944,0.00019,0.3934],"tcp_start":[0.41773,0.0,0.33966],"tcp_to_object_dist_end":0.61248,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `4545dd6ce27d481eea1784f20773d493eb22fff73af3521a1f048df5cf49bcf3`; realized-scene SHA-256: `bd4f35ed59709260e094776b661704e90745f7a52d08ebc05c5947cbc49435ce`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.0,0.15]},{"name":"goal","value":[0.70382,-0.01567,0.15]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":5.0},{"name":"obstacle_height_m","value":0.3},{"name":"force_scale_n","value":5.0}],"object_starts":[],"obstacles":[{"name":"obstacle_block","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,0.0,0.15]}],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.70382,-0.01567,0.15]}],"task_name":"obstacle_reach"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.75,"average_solve_count":108.0,"average_success_count":108.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_y":0.00059,"push_1.push_distance":0.15767,"push_1.push_speed":0.05193},"optimized_scores":{"best_composite_score":-0.18,"best_fitness_score":0.0,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"obstacle_block","body_b":"link7","contact_count":410.0,"contact_point_centroid":[0.46009,0.00097,0.29995],"force_p95":351.91093,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":395.27948,"mean_force":326.71405,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.40486,1e-05,0.29482]},{"body_a":"obstacle_block","body_b":"link7","contact_count":1000.0,"contact_point_centroid":[0.46003,0.00145,0.29994],"force_p95":301.09672,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":353.476,"mean_force":270.37359,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.40794,-0.0,0.32052]},{"body_a":"obstacle_block","body_b":"link6","contact_count":996.0,"contact_point_centroid":[0.5371,-0.00483,0.29989],"force_p95":255.6377,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":290.50282,"mean_force":205.84449,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.44689,0.0001,0.37321]},{"body_a":"obstacle_block","body_b":"link7","contact_count":154.0,"contact_point_centroid":[0.46,0.00169,0.29995],"force_p95":136.49016,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":229.90567,"mean_force":104.67881,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.41909,-1e-05,0.34132]}],"total_contact_groups":4},"final_pose_error":0.33505,"key_states":{"actual_goal_position":[0.70382,-0.01567,0.15],"actual_obstacle_position":[0.5,0.0,0.15],"final_tcp_position":[0.46919,0.0002,0.39286],"realised_goal_position":[0.70382,-0.01567,0.15],"realised_object_initial_position":[0.0,0.0,0.0],"realised_obstacle_position":[0.5,0.0,0.15]},"peak_contact_force":395.27948,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.71979,"object_to_goal_dist_start":0.71979,"object_z_max":0.0,"peak_contact_force":310.14242,"phase_name":"push_1","phase_peak_obstacle_force":395.27948,"phase_type":"push","raw_contact_event_count":410.0,"raw_peak_contact_force":395.27948,"tcp_end":[0.40393,1e-05,0.30046],"tcp_start":[0.3503,-0.0,0.32087],"tcp_to_object_dist_end":0.50343,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.71979,"object_to_goal_dist_start":0.71979,"object_z_max":0.0,"peak_contact_force":258.49113,"phase_name":"align_1","phase_peak_obstacle_force":353.476,"phase_type":"align","raw_contact_event_count":1000.0,"raw_peak_contact_force":353.476,"tcp_end":[0.41773,0.0,0.33966],"tcp_start":[0.40393,1e-05,0.30046],"tcp_to_object_dist_end":0.5384,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.71979,"object_to_goal_dist_start":0.71979,"object_z_max":0.0,"peak_contact_force":67.71417,"phase_name":"release_1","phase_peak_obstacle_force":290.50282,"phase_type":"release","raw_contact_event_count":1150.0,"raw_peak_contact_force":290.50282,"tcp_end":[0.46944,0.00019,0.3934],"tcp_start":[0.41773,0.0,0.33966],"tcp_to_object_dist_end":0.61248,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```