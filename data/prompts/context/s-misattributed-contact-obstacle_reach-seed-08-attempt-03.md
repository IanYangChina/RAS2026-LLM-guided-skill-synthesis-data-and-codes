## Search State

- **Seed**: 8
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → descend | arc_cartesian | linear_cartesian | position_control | position_control | pose_tolerance | pose_tolerance | 5 | -0.2500 | 0.00 | ❌ rejected |
| 2 | approach → descend | arc_cartesian | linear_cartesian | position_control | position_control | pose_tolerance | pose_tolerance | 5 | -0.1835 | 0.07 | ❌ rejected |
| 1 | approach → descend | arc_cartesian | linear_cartesian | position_control | position_control | pose_tolerance | pose_tolerance | 5 | -0.1835 | 0.07 | ✅ accepted |
| 0 | pull → insert → descend | arc_cartesian | impedance_motion | linear_cartesian | impedance_control | impedance_control | position_control | time_limit | pose_tolerance | contact_detected | 4 | -0.2300 | 0.00 | ✅ accepted |

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
- Frozen realised-scene SHA-256: `4d99f589f09839c4f3a4e389174672e239f050e8ccee110af89dc738cbe9e683`
- Frozen task target: [0.6826972276605561, 0.048727684333792556, 0.15]
- Goal object position: (0.6826972276605561, 0.048727684333792556, 0.15)
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
  frozen_task_target: [0.6827, 0.0487, 0.15]
  frozen_obstacle_position: [0.5, 0, 0.15]
  frozen_targets: {'task_goal': [0.6826972276605561, 0.048727684333792556, 0.15]}
  frozen_obstacles: {'obstacle_block': [0.5, 0.0, 0.15]}
  goal_tolerance_m: 0.02
  force_limit_n: 5
  obstacle_height_m: 0.3
  force_scale_n: 5
  realized_scene_sha256: 4d99f589f09839c4f3a4e389174672e239f050e8ccee110af89dc738cbe9e683

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
| `goal` | offset from task goal position (0.6826972276605561, 0.048727684333792556, 0.15) | final destination targets |
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

## Current Skill (Q=-0.250) — your mutation base

```yaml
skill: obstacle_reach
dsl_version: 2
subtasks:
- id: approach_goal
  offset:
  - 0.0
  - 0.0
  - 0.25
  weight: 0.3
- id: reach_goal
  weight: 0.7
phases:
- id: arc_over_obstacle
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
    - 0.25
    tolerance: 0.02
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
      tolerance: 0.2
  parameters:
    arc_height:
      type: scalar
      range:
      - 0.05
      - 0.25
      default: 0.12
      binds_to:
      - path: generator.arc_height
        mode: replace
    arc_speed:
      type: scalar
      range:
      - 0.2
      - 0.8
      default: 0.4
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: contact_guard
    when: during_phase
    predicate: contact_detected
    threshold: 0.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.05
    - 0.0
  subtask_id: approach_goal
- id: descend_to_goal
  type: descend
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
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
      tolerance: 0.2
  parameters:
    descend_tolerance:
      type: scalar
      range:
      - 0.01
      - 0.03
      default: 0.02
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
    descend_x_offset:
      type: scalar
      range:
      - -0.05
      - 0.05
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: add
    descend_y_offset:
      type: scalar
      range:
      - -0.05
      - 0.05
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: add
  guards:
  - id: descend_contact_guard
    when: during_phase
    predicate: contact_detected
    threshold: 0.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.05
    - 0.0
  subtask_id: reach_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **arc_over_obstacle** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.25], tolerance=0.02
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.2
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - arc_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=contact_guard, when=during_phase, predicate=contact_detected, on_failure=retry, threshold=0.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.05, 0.0]
- **descend_to_goal** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.2
  - parameter_bindings:
    - descend_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
    - descend_x_offset: status=consumed; consumers=target.offset.x (add)
    - descend_y_offset: status=consumed; consumers=target.offset.y (add)
  - guards:
    - id=descend_contact_guard, when=during_phase, predicate=contact_detected, on_failure=retry, threshold=0.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.05, 0.0]

## Design Metrics

- **Composite score**: -0.250
- **task_score** (E): 0.000
- **fitness_score**: 0.000  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
  → CMA-ES cannot optimise this structure (shaped reward also near zero)
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.250

**⚠ Warning**: CMA-ES stagnated + low fitness_score → structure may be fundamentally incompatible with task

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| arc_over_obstacle | 0.00 | 1.00 | 0.2223 |
| descend_to_goal | 0.00 | 0.00 | 0.1442 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force | Obstacle/contact |
|---|---|---|---|---|---|---|---|---|---|
| arc_over_obstacle | approach | 0.00 / step_budget | (0.350, -0.000, 0.321)→(0.567, 0.002, 0.366) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.738→0.738 | 1.00 / 1.000 | 349.758 | 1405.570 | link5 ↔ obstacle_block/obstacle_block_geom |
| descend_to_goal | descend | 0.00 / step_budget | (0.567, 0.002, 0.366)→(0.703, -0.017, 0.337) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.738→0.738 | 0.00 / 0.000 | 0.000 | 1566.385 | link6 ↔ obstacle_block/obstacle_block_geom |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- obstacle_clearance: 0.344
- path_efficiency: 0.411
- arc_smoothness: 0.980
- collision_factor: 0.000  (exp(−peak_force / force_scale))
- peak_obstacle_force: 1599.611 N
- collision_location: obstacle_block  (or None if no contact)
- final_tcp_distance: 0.171
- min_tcp_distance: 0.123
- tcp_proximity_score: 0.320
- goal_reached_rate: 0.000
- peak_obstacle_counterbody: link6
- peak_obstacle_countergeom: None
- peak_obstacle_obstacle_body: obstacle_block
- peak_obstacle_obstacle_geom: obstacle_block_geom

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.000
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.000
- **Median Q (composite search score)**: -0.250
- **K-run variance**: 0.0000
- **Stagnated**: yes
  → Parameter optimiser converged to local optimum; structural change likely needed
- **Stop reason**: tolfun
- **Mean generations**: 2.0
- **Final σ (mean)**: 0.268


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `153111e21f17c0d331b561f1147684993204f9f696925b5b61ee34d65508a2ad`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"object_xy_delta":[0.0,0.0]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `09a48f578e6b1d8164588605561432222dd1ada27be56833f7098561f0a0705c`; realized-scene SHA-256: `4d99f589f09839c4f3a4e389174672e239f050e8ccee110af89dc738cbe9e683`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.0,0.15]},{"name":"goal","value":[0.6827,0.04873,0.15]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":5.0},{"name":"obstacle_height_m","value":0.3},{"name":"force_scale_n","value":5.0}],"object_starts":[],"obstacles":[{"name":"obstacle_block","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,0.0,0.15]}],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.6827,0.04873,0.15]}],"task_name":"obstacle_reach"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":12.0,"average_failure_rate":0.1791,"average_mean_iterations":41.86567,"average_solve_count":67.0,"average_success_count":55.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"arc_over_obstacle.arc_height":0.17976,"arc_over_obstacle.arc_speed":0.57661,"descend_to_goal.descend_tolerance":0.02322,"descend_to_goal.descend_x_offset":-0.01975,"descend_to_goal.descend_y_offset":0.01188},"optimized_scores":{"best_composite_score":-0.25,"best_fitness_score":0.0,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"obstacle_block","body_b":"link6","contact_count":256.0,"contact_point_centroid":[0.48637,-0.00129,0.29958],"force_p95":362.46254,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":1599.61147,"mean_force":282.43619,"phase_index":0.0,"phase_name":"arc_over_obstacle","phase_type":"approach","tcp_position_centroid":[0.36923,0.0013,0.34137]},{"body_a":"obstacle_block","body_b":"link5","contact_count":589.0,"contact_point_centroid":[0.53334,-0.04019,0.2998],"force_p95":639.77969,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":1402.84944,"mean_force":322.08964,"phase_index":1.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.61932,0.07023,0.27404]},{"body_a":"obstacle_block","body_b":"link7","contact_count":245.0,"contact_point_centroid":[0.53989,0.03331,0.26988],"force_p95":630.916,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":1065.37468,"mean_force":435.61984,"phase_index":1.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.55404,0.03801,0.29666]}],"total_contact_groups":3},"final_pose_error":0.17108,"key_states":{"actual_goal_position":[0.6827,0.04873,0.15],"actual_obstacle_position":[0.5,0.0,0.15],"final_tcp_position":[0.67766,0.06172,0.32044],"realised_goal_position":[0.6827,0.04873,0.15],"realised_object_initial_position":[0.0,0.0,0.0],"realised_obstacle_position":[0.5,0.0,0.15]},"peak_contact_force":1599.61147,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":451.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.70068,"object_to_goal_dist_start":0.70068,"object_z_max":0.0,"peak_contact_force":240.40038,"phase_name":"arc_over_obstacle","phase_peak_obstacle_force":1599.61147,"phase_type":"approach","raw_contact_event_count":834.0,"raw_peak_contact_force":1402.84944,"subtask_id":"approach_goal","tcp_end":[0.55684,0.03248,0.35129],"tcp_start":[0.3503,-0.0,0.32087],"tcp_to_object_dist_end":0.65919,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":972.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.70068,"object_to_goal_dist_start":0.70068,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"descend_to_goal","phase_peak_obstacle_force":1402.84944,"phase_type":"descend","raw_contact_event_count":256.0,"raw_peak_contact_force":1599.61147,"subtask_id":"reach_goal","tcp_end":[0.67766,0.06172,0.32044],"tcp_start":[0.55684,0.03248,0.35129],"tcp_to_object_dist_end":0.75214,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `e48c638882a658e374f83b9ad4d96930956de0db1e88d759e02d159e310d1b19`; realized-scene SHA-256: `fda113aaf8e8c099f2c28b9d9dc98e35a2e52600fa9b3eec61a8dea75fa26f9a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.0,0.15]},{"name":"goal","value":[0.73702,-0.02132,0.15]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":5.0},{"name":"obstacle_height_m","value":0.3},{"name":"force_scale_n","value":5.0}],"object_starts":[],"obstacles":[{"name":"obstacle_block","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,0.0,0.15]}],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.73702,-0.02132,0.15]}],"task_name":"obstacle_reach"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":20.0,"average_failure_rate":0.26667,"average_mean_iterations":58.56,"average_solve_count":75.0,"average_success_count":55.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"arc_over_obstacle.arc_height":0.18642,"arc_over_obstacle.arc_speed":0.48215,"descend_to_goal.descend_tolerance":0.02157,"descend_to_goal.descend_x_offset":-0.03089,"descend_to_goal.descend_y_offset":-0.01391},"optimized_scores":{"best_composite_score":-0.25,"best_fitness_score":0.0,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"obstacle_block","body_b":"link6","contact_count":220.0,"contact_point_centroid":[0.48477,-0.0029,0.29953],"force_p95":392.26558,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":1535.05045,"mean_force":272.03059,"phase_index":0.0,"phase_name":"arc_over_obstacle","phase_type":"approach","tcp_position_centroid":[0.3682,-0.00045,0.33912]},{"body_a":"obstacle_block","body_b":"link5","contact_count":758.0,"contact_point_centroid":[0.50176,-0.0875,0.29981],"force_p95":627.00861,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":1277.21801,"mean_force":379.42194,"phase_index":1.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.65329,-0.02804,0.2974]},{"body_a":"obstacle_block","body_b":"link7","contact_count":55.0,"contact_point_centroid":[0.53991,-0.01916,0.21744],"force_p95":528.78697,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":531.36359,"mean_force":357.67985,"phase_index":1.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.55591,-0.01545,0.24336]}],"total_contact_groups":3},"final_pose_error":0.2099,"key_states":{"actual_goal_position":[0.73702,-0.02132,0.15],"actual_obstacle_position":[0.5,0.0,0.15],"final_tcp_position":[0.72398,-0.0533,0.35836],"realised_goal_position":[0.73702,-0.02132,0.15],"realised_object_initial_position":[0.0,0.0,0.0],"realised_obstacle_position":[0.5,0.0,0.15]},"peak_contact_force":1535.05045,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":391.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.75244,"object_to_goal_dist_start":0.75244,"object_z_max":0.0,"peak_contact_force":424.66315,"phase_name":"arc_over_obstacle","phase_peak_obstacle_force":1535.05045,"phase_type":"approach","raw_contact_event_count":813.0,"raw_peak_contact_force":1277.21801,"subtask_id":"approach_goal","tcp_end":[0.57136,-0.01147,0.37765],"tcp_start":[0.3503,-0.0,0.32087],"tcp_to_object_dist_end":0.68498,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":976.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.75244,"object_to_goal_dist_start":0.75244,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"descend_to_goal","phase_peak_obstacle_force":1277.21801,"phase_type":"descend","raw_contact_event_count":220.0,"raw_peak_contact_force":1535.05045,"subtask_id":"reach_goal","tcp_end":[0.72398,-0.0533,0.35836],"tcp_start":[0.57136,-0.01147,0.37765],"tcp_to_object_dist_end":0.80957,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `7c770227bfbc61ad3e08c75d3630762494b918d2814b704b39c653a43064979c`; realized-scene SHA-256: `61ec300895503e484321052c14122005b6d825b54245a4a918a581ea2f04a59f`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.0,0.15]},{"name":"goal","value":[0.7456,-0.02923,0.15]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":5.0},{"name":"obstacle_height_m","value":0.3},{"name":"force_scale_n","value":5.0}],"object_starts":[],"obstacles":[{"name":"obstacle_block","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,0.0,0.15]}],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.7456,-0.02923,0.15]}],"task_name":"obstacle_reach"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":11.0,"average_failure_rate":0.16667,"average_mean_iterations":39.18182,"average_solve_count":66.0,"average_success_count":55.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"arc_over_obstacle.arc_height":0.17398,"arc_over_obstacle.arc_speed":0.5877,"descend_to_goal.descend_tolerance":0.02099,"descend_to_goal.descend_x_offset":-0.02787,"descend_to_goal.descend_y_offset":-0.01704},"optimized_scores":{"best_composite_score":-0.25,"best_fitness_score":0.0,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"obstacle_block","body_b":"link6","contact_count":220.0,"contact_point_centroid":[0.48895,-0.00288,0.29951],"force_p95":367.94467,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":1564.49209,"mean_force":280.58255,"phase_index":0.0,"phase_name":"arc_over_obstacle","phase_type":"approach","tcp_position_centroid":[0.3719,-0.00075,0.34333]},{"body_a":"obstacle_block","body_b":"link5","contact_count":782.0,"contact_point_centroid":[0.5005,-0.1005,0.29986],"force_p95":708.31512,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":1536.64353,"mean_force":396.11916,"phase_index":1.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.64309,-0.03773,0.28866]},{"body_a":"obstacle_block","body_b":"link6","contact_count":129.0,"contact_point_centroid":[0.53986,-0.0818,0.18647],"force_p95":841.36242,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":906.55768,"mean_force":370.06357,"phase_index":1.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.65427,-0.03078,0.3016]},{"body_a":"obstacle_block","body_b":"link7","contact_count":50.0,"contact_point_centroid":[0.53976,-0.02495,0.1976],"force_p95":500.44115,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":598.3494,"mean_force":367.45064,"phase_index":1.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.56497,-0.01129,0.23287]}],"total_contact_groups":4},"final_pose_error":0.18436,"key_states":{"actual_goal_position":[0.7456,-0.02923,0.15],"actual_obstacle_position":[0.5,0.0,0.15],"final_tcp_position":[0.706,-0.06002,0.33347],"realised_goal_position":[0.7456,-0.02923,0.15],"realised_object_initial_position":[0.0,0.0,0.0],"realised_obstacle_position":[0.5,0.0,0.15]},"peak_contact_force":1564.49209,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":391.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.7611,"object_to_goal_dist_start":0.7611,"object_z_max":0.0,"peak_contact_force":384.21127,"phase_name":"arc_over_obstacle","phase_peak_obstacle_force":1564.49209,"phase_type":"approach","raw_contact_event_count":961.0,"raw_peak_contact_force":1536.64353,"subtask_id":"approach_goal","tcp_end":[0.5721,-0.0154,0.36766],"tcp_start":[0.3503,-0.0,0.32087],"tcp_to_object_dist_end":0.68023,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.7611,"object_to_goal_dist_start":0.7611,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"descend_to_goal","phase_peak_obstacle_force":1536.64353,"phase_type":"descend","raw_contact_event_count":220.0,"raw_peak_contact_force":1564.49209,"subtask_id":"reach_goal","tcp_end":[0.706,-0.06002,0.33347],"tcp_start":[0.5721,-0.0154,0.36766],"tcp_to_object_dist_end":0.7831,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```