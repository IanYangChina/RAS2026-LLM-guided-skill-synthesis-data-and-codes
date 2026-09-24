## Search State

- **Seed**: 0
- **Iteration**: 11 / 15

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
- Frozen realised-scene SHA-256: `47501b1aab9bfa0e6b563b161626f42def695cce7ac7b19bb24da49f0ff9be1e`
- Frozen task target: [0.7136961687321454, -0.02302132862361297, 0.15]
- Goal object position: (0.7136961687321454, -0.02302132862361297, 0.15)
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
  frozen_task_target: [0.7137, -0.023, 0.15]
  frozen_obstacle_position: [0.5, 0, 0.15]
  frozen_targets: {'task_goal': [0.7136961687321454, -0.02302132862361297, 0.15]}
  frozen_obstacles: {'obstacle_block': [0.5, 0.0, 0.15]}
  goal_tolerance_m: 0.02
  force_limit_n: 5
  obstacle_height_m: 0.3
  force_scale_n: 5
  realized_scene_sha256: 47501b1aab9bfa0e6b563b161626f42def695cce7ac7b19bb24da49f0ff9be1e

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
| `goal` | offset from task goal position (0.7136961687321454, -0.02302132862361297, 0.15) | final destination targets |
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

## Current Skill (Q=-0.230) — your mutation base

```yaml
skill: obstacle_reach
dsl_version: 2
subtasks:
- id: approach_high
  offset:
  - 0.0
  - 0.3
  - 0.3
  weight: 0.3
- id: reach_goal
  weight: 0.7
phases:
- id: arc_to_side
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.3
    - 0.3
    tolerance: 0.03
  parameters:
    approach_arc_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.15
      binds_to:
      - path: generator.arc_height
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: approach_high
- id: descend_side
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.3
    - 0.0
    tolerance: 0.015
  parameters:
    descend_side_speed:
      type: scalar
      range:
      - 0.03
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: reach_goal
- id: shift_to_goal
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.01
  parameters:
    shift_speed:
      type: scalar
      range:
      - 0.03
      - 0.15
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: reach_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **arc_to_side** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.3, 0.3], tolerance=0.03
  - parameter_bindings:
    - approach_arc_height: status=consumed; consumers=generator.arc_height (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat
- **descend_side** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.3, 0.0], tolerance=0.015
  - parameter_bindings:
    - descend_side_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat
- **shift_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - parameter_bindings:
    - shift_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat

## Design Metrics

- **Composite score**: -0.230
- **task_score** (E): 0.000
- **fitness_score**: 0.000  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
  → CMA-ES cannot optimise this structure (shaped reward also near zero)
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.230

**⚠ Warning**: CMA-ES stagnated + low fitness_score → structure may be fundamentally incompatible with task

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| arc_to_left_high | 1.00 | 0.00 | 0.4236 |
| descend_to_left_z | 1.00 | 0.33 | 0.2802 |
| shift_to_goal | 0.00 | 1.00 | 0.1308 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force | Obstacle/contact |
|---|---|---|---|---|---|---|---|---|---|
| arc_to_left_high | approach | 1.00 / step_budget | (0.350, -0.000, 0.321)→(0.675, -0.233, 0.459) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.714→0.714 | 0.00 / 0.000 | 0.000 | 0.000 | — |
| descend_to_left_z | descend | 1.00 / step_budget | (0.675, -0.233, 0.459)→(0.702, -0.250, 0.180) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.714→0.714 | 0.33 / 0.333 | 80.189 | 304.471 | link5 ↔ obstacle_block/obstacle_block_geom |
| shift_to_goal | approach | 0.00 / step_budget | (0.702, -0.250, 0.180)→(0.699, -0.120, 0.165) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.714→0.714 | 1.00 / 1.000 | 175.265 | 275.574 | link5 ↔ obstacle_block/obstacle_block_geom |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- obstacle_clearance: 0.460
- path_efficiency: 0.420
- arc_smoothness: 0.984
- collision_factor: 0.000  (exp(−peak_force / force_scale))
- peak_obstacle_force: 298.414 N
- collision_location: obstacle_block  (or None if no contact)
- final_tcp_distance: 0.103
- min_tcp_distance: 0.103
- tcp_proximity_score: 0.504
- goal_reached_rate: 0.000
- peak_obstacle_counterbody: link5
- peak_obstacle_countergeom: None
- peak_obstacle_obstacle_body: obstacle_block
- peak_obstacle_obstacle_geom: obstacle_block_geom

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.000
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.000
- **Median Q (composite search score)**: -0.230
- **K-run variance**: 0.0000
- **Stagnated**: yes
  → Parameter optimiser converged to local optimum; structural change likely needed
- **Stop reason**: tolfun
- **Mean generations**: 2.0
- **Final σ (mean)**: 0.319


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `30565d16bb12c763ef96950bff0806542e706772a2f5d6530b71a1e799295889`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"object_xy_delta":[0.0,0.0]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `93ed75540af82fc2f732261ad21f1d84d6fc60a0bcf806dd0394bfdc69d4362f`; realized-scene SHA-256: `47501b1aab9bfa0e6b563b161626f42def695cce7ac7b19bb24da49f0ff9be1e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.0,0.15]},{"name":"goal","value":[0.7137,-0.02302,0.15]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":5.0},{"name":"obstacle_height_m","value":0.3},{"name":"force_scale_n","value":5.0}],"object_starts":[],"obstacles":[{"name":"obstacle_block","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,0.0,0.15]}],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.7137,-0.02302,0.15]}],"task_name":"obstacle_reach"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.95288,"average_solve_count":191.0,"average_success_count":191.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"arc_to_left_high.approach_speed":0.10944,"arc_to_left_high.arc_height":0.14419,"descend_to_left_z.descend_speed":0.09766,"shift_to_goal.shift_speed":0.09423},"optimized_scores":{"best_composite_score":-0.23,"best_fitness_score":0.0,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"obstacle_block","body_b":"link5","contact_count":115.0,"contact_point_centroid":[0.53994,-0.10667,0.29991],"force_p95":297.36918,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":298.41351,"mean_force":264.91874,"phase_index":1.0,"phase_name":"descend_to_left_z","phase_type":"descend","tcp_position_centroid":[0.71567,-0.27233,0.18485]},{"body_a":"obstacle_block","body_b":"link5","contact_count":671.0,"contact_point_centroid":[0.54,-0.05357,0.29999],"force_p95":137.47888,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":297.6622,"mean_force":103.13166,"phase_index":2.0,"phase_name":"shift_to_goal","phase_type":"approach","tcp_position_centroid":[0.71598,-0.19872,0.17081]}],"total_contact_groups":2},"final_pose_error":0.10275,"key_states":{"actual_goal_position":[0.7137,-0.02302,0.15],"actual_obstacle_position":[0.5,0.0,0.15],"final_tcp_position":[0.71437,-0.12515,0.16127],"realised_goal_position":[0.7137,-0.02302,0.15],"realised_object_initial_position":[0.0,0.0,0.0],"realised_obstacle_position":[0.5,0.0,0.15]},"peak_contact_force":298.41351,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":868.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.72965,"object_to_goal_dist_start":0.72965,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"arc_to_left_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_left_high","tcp_end":[0.69336,-0.25698,0.46506],"tcp_start":[0.3503,-0.0,0.32087],"tcp_to_object_dist_end":0.87354,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":655.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.72965,"object_to_goal_dist_start":0.72965,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"descend_to_left_z","phase_peak_obstacle_force":298.41351,"phase_type":"descend","raw_contact_event_count":115.0,"raw_peak_contact_force":298.41351,"subtask_id":"reach_goal","tcp_end":[0.72073,-0.27385,0.18648],"tcp_start":[0.69336,-0.25698,0.46506],"tcp_to_object_dist_end":0.79323,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.72965,"object_to_goal_dist_start":0.72965,"object_z_max":0.0,"peak_contact_force":137.5758,"phase_name":"shift_to_goal","phase_peak_obstacle_force":297.6622,"phase_type":"approach","raw_contact_event_count":671.0,"raw_peak_contact_force":297.6622,"subtask_id":"reach_goal","tcp_end":[0.71437,-0.12515,0.16127],"tcp_start":[0.72073,-0.27385,0.18648],"tcp_to_object_dist_end":0.74296,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `e2f42f3fbbcca284b57f515aa7c9c12d3405e5434d2b225f750641c72d8a7bd9`; realized-scene SHA-256: `46c72c16be0fa319940ad2424e6763e117e5dc5f0c6b9e34d827f50eec225036`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.0,0.15]},{"name":"goal","value":[0.70118,0.04505,0.15]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":5.0},{"name":"obstacle_height_m","value":0.3},{"name":"force_scale_n","value":5.0}],"object_starts":[],"obstacles":[{"name":"obstacle_block","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,0.0,0.15]}],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.70118,0.04505,0.15]}],"task_name":"obstacle_reach"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.31646,"average_solve_count":158.0,"average_success_count":158.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"arc_to_left_high.approach_speed":0.14464,"arc_to_left_high.arc_height":0.11802,"descend_to_left_z.descend_speed":0.10416,"shift_to_goal.shift_speed":0.11279},"optimized_scores":{"best_composite_score":-0.23,"best_fitness_score":0.0,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"obstacle_block","body_b":"link5","contact_count":34.0,"contact_point_centroid":[0.53988,-0.0708,0.29985],"force_p95":310.17631,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":334.21971,"mean_force":258.56439,"phase_index":1.0,"phase_name":"descend_to_left_z","phase_type":"descend","tcp_position_centroid":[0.69922,-0.20355,0.17011]},{"body_a":"obstacle_block","body_b":"link5","contact_count":813.0,"contact_point_centroid":[0.53999,0.00177,0.29999],"force_p95":232.62884,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":245.96658,"mean_force":168.72033,"phase_index":2.0,"phase_name":"shift_to_goal","phase_type":"approach","tcp_position_centroid":[0.70101,-0.1247,0.16399]}],"total_contact_groups":2},"final_pose_error":0.09102,"key_states":{"actual_goal_position":[0.70118,0.04505,0.15],"actual_obstacle_position":[0.5,0.0,0.15],"final_tcp_position":[0.70366,-0.0452,0.16163],"realised_goal_position":[0.70118,0.04505,0.15],"realised_object_initial_position":[0.0,0.0,0.0],"realised_obstacle_position":[0.5,0.0,0.15]},"peak_contact_force":334.21971,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":729.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.71846,"object_to_goal_dist_start":0.71846,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"arc_to_left_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_left_high","tcp_end":[0.67839,-0.19095,0.46245],"tcp_start":[0.3503,-0.0,0.32087],"tcp_to_object_dist_end":0.84294,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":605.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.71846,"object_to_goal_dist_start":0.71846,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"descend_to_left_z","phase_peak_obstacle_force":334.21971,"phase_type":"descend","raw_contact_event_count":34.0,"raw_peak_contact_force":334.21971,"subtask_id":"reach_goal","tcp_end":[0.70215,-0.20416,0.17044],"tcp_start":[0.67839,-0.19095,0.46245],"tcp_to_object_dist_end":0.75084,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.71846,"object_to_goal_dist_start":0.71846,"object_z_max":0.0,"peak_contact_force":227.34176,"phase_name":"shift_to_goal","phase_peak_obstacle_force":245.96658,"phase_type":"approach","raw_contact_event_count":813.0,"raw_peak_contact_force":245.96658,"subtask_id":"reach_goal","tcp_end":[0.70366,-0.0452,0.16163],"tcp_start":[0.70215,-0.20416,0.17044],"tcp_to_object_dist_end":0.72339,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `6daafe4988ca0b57abfa37034ad4d1d5846eda9319b3f27d8d423c2e135ec43b`; realized-scene SHA-256: `91e4de206df15f80750cdb645e4a7fbeecac222f6e7e3c9e7aabeca93992a5f5`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.0,0.15]},{"name":"goal","value":[0.67616,-0.02015,0.15]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":5.0},{"name":"obstacle_height_m","value":0.3},{"name":"force_scale_n","value":5.0}],"object_starts":[],"obstacles":[{"name":"obstacle_block","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,0.0,0.15]}],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.67616,-0.02015,0.15]}],"task_name":"obstacle_reach"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.628,"average_solve_count":250.0,"average_success_count":250.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"arc_to_left_high.approach_speed":0.06246,"arc_to_left_high.arc_height":0.06093,"descend_to_left_z.descend_speed":0.06698,"shift_to_goal.shift_speed":0.05244},"optimized_scores":{"best_composite_score":-0.23,"best_fitness_score":0.0,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"obstacle_block","body_b":"link5","contact_count":875.0,"contact_point_centroid":[0.53999,-0.09209,0.29999],"force_p95":156.94053,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":283.09203,"mean_force":128.57497,"phase_index":2.0,"phase_name":"shift_to_goal","phase_type":"approach","tcp_position_centroid":[0.68048,-0.2315,0.17742]},{"body_a":"obstacle_block","body_b":"link5","contact_count":176.0,"contact_point_centroid":[0.53993,-0.12034,0.29992],"force_p95":276.45966,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":280.77871,"mean_force":251.35195,"phase_index":1.0,"phase_name":"descend_to_left_z","phase_type":"descend","tcp_position_centroid":[0.67928,-0.26969,0.18422]}],"total_contact_groups":2},"final_pose_error":0.17161,"key_states":{"actual_goal_position":[0.67616,-0.02015,0.15],"actual_obstacle_position":[0.5,0.0,0.15],"final_tcp_position":[0.67928,-0.19029,0.17216],"realised_goal_position":[0.67616,-0.02015,0.15],"realised_object_initial_position":[0.0,0.0,0.0],"realised_obstacle_position":[0.5,0.0,0.15]},"peak_contact_force":283.09203,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":739.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.69289,"object_to_goal_dist_start":0.69289,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"arc_to_left_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_left_high","tcp_end":[0.65344,-0.25073,0.44823],"tcp_start":[0.3503,-0.0,0.32087],"tcp_to_object_dist_end":0.83112,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":728.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.69289,"object_to_goal_dist_start":0.69289,"object_z_max":0.0,"peak_contact_force":240.56643,"phase_name":"descend_to_left_z","phase_peak_obstacle_force":280.77871,"phase_type":"descend","raw_contact_event_count":176.0,"raw_peak_contact_force":280.77871,"subtask_id":"reach_goal","tcp_end":[0.68443,-0.27135,0.18401],"tcp_start":[0.65344,-0.25073,0.44823],"tcp_to_object_dist_end":0.75891,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.69289,"object_to_goal_dist_start":0.69289,"object_z_max":0.0,"peak_contact_force":160.87796,"phase_name":"shift_to_goal","phase_peak_obstacle_force":283.09203,"phase_type":"approach","raw_contact_event_count":875.0,"raw_peak_contact_force":283.09203,"subtask_id":"reach_goal","tcp_end":[0.67928,-0.19029,0.17216],"tcp_start":[0.68443,-0.27135,0.18401],"tcp_to_object_dist_end":0.72614,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```