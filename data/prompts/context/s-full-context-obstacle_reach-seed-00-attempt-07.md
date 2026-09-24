## Search State

- **Seed**: 0
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → approach | arc_cartesian | linear_cartesian | position_control | position_control | pose_tolerance | pose_tolerance | 6 | -0.3000 | 0.00 | ❌ rejected |
| 6 | approach → approach | arc_cartesian | linear_cartesian | position_control | position_control | pose_tolerance | pose_tolerance | 6 | 0.0580 | 0.36 | ❌ rejected |
| 5 | approach → align → approach | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 10 | -0.4213 | 0.11 | ❌ rejected |
| 4 | approach → approach | arc_cartesian | linear_cartesian | position_control | position_control | pose_tolerance | pose_tolerance | 7 | -0.0572 | 0.29 | ❌ rejected |
| 3 | approach → approach | arc_cartesian | linear_cartesian | position_control | position_control | pose_tolerance | pose_tolerance | 6 | 0.2857 | 0.59 | ✅ accepted |

**Proposal policy**: task_score is 0.00 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.300) — your mutation base

```yaml
skill: obstacle_reach
dsl_version: 2
subtasks:
- id: reach_over
  offset:
  - 0.0
  - 0.0
  - 0.2
  weight: 0.3
- id: reach_goal
  weight: 0.7
phases:
- id: approach_over_obstacle
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.2
    tolerance: 0.01
    orientation:
      mode: none
  parameters:
    approach_offset_z:
      type: scalar
      range:
      - 0.1
      - 0.3
      default: 0.2
      binds_to:
      - path: target.offset.z
        mode: replace
    arc_height:
      type: scalar
      range:
      - 0.05
      - 0.25
      default: 0.15
      binds_to:
      - path: generator.arc_height
        mode: replace
    pose_tol:
      type: scalar
      range:
      - 0.005
      - 0.02
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
    speed:
      type: scalar
      range:
      - 0.05
      - 0.5
      default: 0.3
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.02
  subtask_id: reach_over
- id: descend_to_goal
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
    tolerance: 0.02
    orientation:
      mode: none
  parameters:
    pose_tol:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
    speed:
      type: scalar
      range:
      - 0.05
      - 0.5
      default: 0.2
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_over_obstacle** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.2], tolerance=0.01
  - orientation: mode=none
  - parameter_bindings:
    - approach_offset_z: status=consumed; consumers=target.offset.z (replace)
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - pose_tol: status=consumed; consumers=termination.pose_tolerance (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.02]
- **descend_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=none
  - parameter_bindings:
    - pose_tol: status=consumed; consumers=termination.pose_tolerance (replace)
    - speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: -0.300
- **task_score** (E): 0.000
- **fitness_score**: 0.000  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
  → CMA-ES cannot optimise this structure (shaped reward also near zero)
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.300

**⚠ Warning**: CMA-ES stagnated + low fitness_score → structure may be fundamentally incompatible with task

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_over_obstacle | 0.00 | 0.00 | 0.2145 |
| descend_to_goal | 0.00 | 1.00 | 0.1181 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force | Obstacle/contact |
|---|---|---|---|---|---|---|---|---|---|
| approach_over_obstacle | approach | 0.00 / step_budget | (0.350, -0.000, 0.321)→(0.563, 0.001, 0.334) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.714→0.714 | 0.00 / 0.000 | 0.000 | 1636.569 | link6 ↔ obstacle_block/obstacle_block_geom |
| descend_to_goal | approach | 0.00 / step_budget | (0.563, 0.001, 0.334)→(0.576, -0.013, 0.219) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.714→0.714 | 1.00 / 1.000 | 319.017 | 1110.677 | link5 ↔ obstacle_block/obstacle_block_geom |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- obstacle_clearance: 0.751
- path_efficiency: 0.478
- arc_smoothness: 0.984
- collision_factor: 0.000  (exp(−peak_force / force_scale))
- peak_obstacle_force: 1638.172 N
- collision_location: obstacle_block  (or None if no contact)
- final_tcp_distance: 0.156
- min_tcp_distance: 0.156
- tcp_proximity_score: 0.354
- goal_reached_rate: 0.000
- peak_obstacle_counterbody: link6
- peak_obstacle_countergeom: None
- peak_obstacle_obstacle_body: obstacle_block
- peak_obstacle_obstacle_geom: obstacle_block_geom

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.000
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.000
- **Median Q (composite search score)**: -0.300
- **K-run variance**: 0.0000
- **Stagnated**: yes
  → Parameter optimiser converged to local optimum; structural change likely needed
- **Stop reason**: tolfun
- **Mean generations**: 2.0
- **Final σ (mean)**: 0.307


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":20.0,"average_failure_rate":0.5,"average_mean_iterations":104.225,"average_solve_count":40.0,"average_success_count":20.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_over_obstacle.approach_offset_z":0.16514,"approach_over_obstacle.arc_height":0.14713,"approach_over_obstacle.pose_tol_arc":0.01777,"approach_over_obstacle.speed_arc":0.39041,"descend_to_goal.pose_tol_descend":0.03696,"descend_to_goal.speed_descend":0.3717},"optimized_scores":{"best_composite_score":-0.3,"best_fitness_score":0.0,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"obstacle_block","body_b":"link6","contact_count":240.0,"contact_point_centroid":[0.50279,-0.00367,0.29952],"force_p95":615.72697,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":1638.17163,"mean_force":321.42857,"phase_index":0.0,"phase_name":"approach_over_obstacle","phase_type":"approach","tcp_position_centroid":[0.3939,-0.0021,0.35577]},{"body_a":"obstacle_block","body_b":"link5","contact_count":50.0,"contact_point_centroid":[0.53966,0.03049,0.29824],"force_p95":1126.24682,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":1380.51009,"mean_force":309.67382,"phase_index":1.0,"phase_name":"descend_to_goal","phase_type":"approach","tcp_position_centroid":[0.57722,-0.01416,0.2285]},{"body_a":"obstacle_block","body_b":"link7","contact_count":6.0,"contact_point_centroid":[0.53994,-0.01021,0.29989],"force_p95":559.15264,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":564.87736,"mean_force":512.35329,"phase_index":0.0,"phase_name":"approach_over_obstacle","phase_type":"approach","tcp_position_centroid":[0.52204,-0.01243,0.36071]}],"total_contact_groups":3},"final_pose_error":0.15587,"key_states":{"actual_goal_position":[0.7137,-0.02302,0.15],"actual_obstacle_position":[0.5,0.0,0.15],"final_tcp_position":[0.58174,-0.01419,0.23249],"realised_goal_position":[0.7137,-0.02302,0.15],"realised_object_initial_position":[0.0,0.0,0.0],"realised_obstacle_position":[0.5,0.0,0.15]},"peak_contact_force":1638.17163,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":391.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.72965,"object_to_goal_dist_start":0.72965,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_over_obstacle","phase_peak_obstacle_force":1638.17163,"phase_type":"approach","raw_contact_event_count":246.0,"raw_peak_contact_force":1638.17163,"subtask_id":"reach_over","tcp_end":[0.57713,-0.01377,0.32472],"tcp_start":[0.3503,-0.0,0.32087],"tcp_to_object_dist_end":0.66235,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":70.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.72965,"object_to_goal_dist_start":0.72965,"object_z_max":0.0,"peak_contact_force":303.69779,"phase_name":"descend_to_goal","phase_peak_obstacle_force":1380.51009,"phase_type":"approach","raw_contact_event_count":50.0,"raw_peak_contact_force":1380.51009,"subtask_id":"reach_goal","tcp_end":[0.58174,-0.01419,0.23249],"tcp_start":[0.57713,-0.01377,0.32472],"tcp_to_object_dist_end":0.62663,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":18.0,"average_failure_rate":0.45,"average_mean_iterations":94.6,"average_solve_count":40.0,"average_success_count":22.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_over_obstacle.approach_offset_z":0.18453,"approach_over_obstacle.arc_height":0.23032,"approach_over_obstacle.pose_tol_arc":0.01577,"approach_over_obstacle.speed_arc":0.43268,"descend_to_goal.pose_tol_descend":0.02755,"descend_to_goal.speed_descend":0.36175},"optimized_scores":{"best_composite_score":-0.3,"best_fitness_score":0.0,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"obstacle_block","body_b":"link6","contact_count":258.0,"contact_point_centroid":[0.50342,0.00317,0.29953],"force_p95":617.27514,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":1658.38935,"mean_force":327.93432,"phase_index":0.0,"phase_name":"approach_over_obstacle","phase_type":"approach","tcp_position_centroid":[0.39468,0.00495,0.35698]},{"body_a":"obstacle_block","body_b":"link5","contact_count":70.0,"contact_point_centroid":[0.53968,0.08344,0.29909],"force_p95":690.44724,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":872.26034,"mean_force":262.80313,"phase_index":1.0,"phase_name":"descend_to_goal","phase_type":"approach","tcp_position_centroid":[0.56175,0.03282,0.23017]},{"body_a":"obstacle_block","body_b":"link7","contact_count":25.0,"contact_point_centroid":[0.53989,0.02667,0.22204],"force_p95":768.23973,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":800.06449,"mean_force":488.9991,"phase_index":1.0,"phase_name":"descend_to_goal","phase_type":"approach","tcp_position_centroid":[0.55558,0.03105,0.24802]},{"body_a":"obstacle_block","body_b":"link7","contact_count":11.0,"contact_point_centroid":[0.53989,0.02321,0.29979],"force_p95":638.82448,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":640.99051,"mean_force":567.09576,"phase_index":0.0,"phase_name":"approach_over_obstacle","phase_type":"approach","tcp_position_centroid":[0.52899,0.0259,0.3558]}],"total_contact_groups":4},"final_pose_error":0.15344,"key_states":{"actual_goal_position":[0.70118,0.04505,0.15],"actual_obstacle_position":[0.5,0.0,0.15],"final_tcp_position":[0.57216,0.03476,0.23241],"realised_goal_position":[0.70118,0.04505,0.15],"realised_object_initial_position":[0.0,0.0,0.0],"realised_obstacle_position":[0.5,0.0,0.15]},"peak_contact_force":1658.38935,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":421.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.71846,"object_to_goal_dist_start":0.71846,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_over_obstacle","phase_peak_obstacle_force":1658.38935,"phase_type":"approach","raw_contact_event_count":269.0,"raw_peak_contact_force":1658.38935,"subtask_id":"reach_over","tcp_end":[0.56397,0.02898,0.32341],"tcp_start":[0.3503,-0.0,0.32087],"tcp_to_object_dist_end":0.65077,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":124.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.71846,"object_to_goal_dist_start":0.71846,"object_z_max":0.0,"peak_contact_force":342.75881,"phase_name":"descend_to_goal","phase_peak_obstacle_force":872.26034,"phase_type":"approach","raw_contact_event_count":95.0,"raw_peak_contact_force":872.26034,"subtask_id":"reach_goal","tcp_end":[0.57216,0.03476,0.23241],"tcp_start":[0.56397,0.02898,0.32341],"tcp_to_object_dist_end":0.61854,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":11.0,"average_failure_rate":0.275,"average_mean_iterations":61.1,"average_solve_count":40.0,"average_success_count":29.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_over_obstacle.approach_offset_z":0.24993,"approach_over_obstacle.arc_height":0.16117,"approach_over_obstacle.pose_tol_arc":0.01993,"approach_over_obstacle.speed_arc":0.3861,"descend_to_goal.pose_tol_descend":0.03421,"descend_to_goal.speed_descend":0.32116},"optimized_scores":{"best_composite_score":-0.3,"best_fitness_score":0.0,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"obstacle_block","body_b":"link6","contact_count":271.0,"contact_point_centroid":[0.48829,-0.00276,0.29955],"force_p95":372.27514,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":1613.1448,"mean_force":278.91764,"phase_index":0.0,"phase_name":"approach_over_obstacle","phase_type":"approach","tcp_position_centroid":[0.3712,-0.00053,0.34539]},{"body_a":"obstacle_block","body_b":"link5","contact_count":145.0,"contact_point_centroid":[0.53973,0.0506,0.29925],"force_p95":749.21148,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":1079.26007,"mean_force":379.03859,"phase_index":1.0,"phase_name":"descend_to_goal","phase_type":"approach","tcp_position_centroid":[0.56945,-0.02775,0.22055]},{"body_a":"obstacle_block","body_b":"link7","contact_count":105.0,"contact_point_centroid":[0.5394,-0.01795,0.29214],"force_p95":804.11329,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":934.47194,"mean_force":437.78551,"phase_index":1.0,"phase_name":"descend_to_goal","phase_type":"approach","tcp_position_centroid":[0.55019,-0.01403,0.32995]}],"total_contact_groups":3},"final_pose_error":0.11784,"key_states":{"actual_goal_position":[0.67616,-0.02015,0.15],"actual_obstacle_position":[0.5,0.0,0.15],"final_tcp_position":[0.57329,-0.05919,0.19218],"realised_goal_position":[0.67616,-0.02015,0.15],"realised_object_initial_position":[0.0,0.0,0.0],"realised_obstacle_position":[0.5,0.0,0.15]},"peak_contact_force":1613.1448,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":451.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.69289,"object_to_goal_dist_start":0.69289,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_over_obstacle","phase_peak_obstacle_force":1613.1448,"phase_type":"approach","raw_contact_event_count":271.0,"raw_peak_contact_force":1613.1448,"subtask_id":"reach_over","tcp_end":[0.54765,-0.01357,0.35439],"tcp_start":[0.3503,-0.0,0.32087],"tcp_to_object_dist_end":0.65245,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":307.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.69289,"object_to_goal_dist_start":0.69289,"object_z_max":0.0,"peak_contact_force":310.59432,"phase_name":"descend_to_goal","phase_peak_obstacle_force":1079.26007,"phase_type":"approach","raw_contact_event_count":250.0,"raw_peak_contact_force":1079.26007,"subtask_id":"reach_goal","tcp_end":[0.57329,-0.05919,0.19218],"tcp_start":[0.54765,-0.01357,0.35439],"tcp_to_object_dist_end":0.60753,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```