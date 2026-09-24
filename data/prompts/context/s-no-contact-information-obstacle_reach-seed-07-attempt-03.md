## Search State

- **Seed**: 7
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → descend → align | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 10 | -0.5300 | 0.00 | ❌ rejected |
| 2 | approach → descend → align | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.3300 | 0.00 | ❌ rejected |
| 1 | approach → descend | linear_cartesian | linear_cartesian | position_control | position_control | pose_tolerance | pose_tolerance | 4 | 0.0928 | 0.29 | ✅ accepted |
| 0 | descend → insert → grasp → approach | linear_cartesian | impedance_motion | — | linear_cartesian | position_control | admittance_control | position_control | position_control | contact_detected | pose_tolerance | time_limit | pose_tolerance | 3 | 0.0400 | 0.00 | ✅ accepted |

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
- Frozen realised-scene SHA-256: `f5f2ee542fad8ea5b5618e39465af4fd2d024325ca55c46b8aecfe9ce333bfb2`
- Frozen task target: [0.7125095466604666, 0.039721380096957554, 0.15]
- Goal object position: (0.7125095466604666, 0.039721380096957554, 0.15)
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
  frozen_task_target: [0.7125, 0.0397, 0.15]
  frozen_obstacle_position: [0.5, 0, 0.15]
  frozen_targets: {'task_goal': [0.7125095466604666, 0.039721380096957554, 0.15]}
  frozen_obstacles: {'obstacle_block': [0.5, 0.0, 0.15]}
  goal_tolerance_m: 0.02
  force_limit_n: 5
  obstacle_height_m: 0.3
  force_scale_n: 5
  realized_scene_sha256: f5f2ee542fad8ea5b5618e39465af4fd2d024325ca55c46b8aecfe9ce333bfb2

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
| `goal` | offset from task goal position (0.7125095466604666, 0.039721380096957554, 0.15) | final destination targets |
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

## Current Skill (Q=-0.530) — your mutation base

```yaml
skill: obstacle_reach
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_waypoint
  offset:
  - 0.0
  - 0.0
  - 0.17
  weight: 0.3
- id: reach_goal
  weight: 0.7
phases:
- id: approach_above_goal
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
    - 0.17
    tolerance: 0.02
    orientation:
      mode: none
  parameters:
    speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
    tolerance:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: reach_waypoint
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
      mode: none
  parameters:
    speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    tolerance:
      type: scalar
      range:
      - 0.005
      - 0.02
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: reach_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_above_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.17], tolerance=0.02
  - orientation: mode=none
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
    - tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
  - retries: max_attempts=0, strategy=repeat
- **descend_to_goal** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=none
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
    - tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
  - retries: max_attempts=0, strategy=repeat

## Design Metrics

- **Composite score**: -0.530
- **task_score** (E): 0.000
- **fitness_score**: 0.000  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
  → CMA-ES cannot optimise this structure (shaped reward also near zero)
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.530

**⚠ Warning**: CMA-ES stagnated + low fitness_score → structure may be fundamentally incompatible with task

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| arc_approach_side | 0.00 | 0.0000 |
| descend_behind_obstacle | 0.00 | 0.1375 |
| lateral_to_goal | 0.00 | 0.0744 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| arc_approach_side | approach | 0.00 / guard_failure | (0.350, -0.000, 0.321)→(0.350, -0.000, 0.321) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.727→0.727 |
| descend_behind_obstacle | descend | 0.00 / step_budget | (0.350, -0.000, 0.321)→(0.393, -0.130, 0.311) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.727→0.727 |
| lateral_to_goal | align | 0.00 / step_budget | (0.393, -0.130, 0.311)→(0.427, -0.140, 0.376) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.727→0.727 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- obstacle_clearance: 0.584
- path_efficiency: 0.600
- arc_smoothness: 0.977
- final_tcp_distance: 0.402
- min_tcp_distance: 0.358
- tcp_proximity_score: 0.068
- goal_reached_rate: 0.000
- peak_obstacle_counterbody: link7
- peak_obstacle_countergeom: None
- peak_obstacle_obstacle_body: obstacle_block
- peak_obstacle_obstacle_geom: obstacle_block_geom

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.000
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.000
- **Median Q (composite search score)**: -0.530
- **K-run variance**: 0.0000
- **Stagnated**: yes
  → Parameter optimiser converged to local optimum; structural change likely needed
- **Stop reason**: tolfun
- **Mean generations**: 2.0
- **Final σ (mean)**: 0.282


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `ee3df1cfa385834280b1b81fd9f0e349b6eb2ac9615126fa1df028e39d9bc447`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"object_xy_delta":[0.0,0.0]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `c0103a17499c8e8b9aa43b2853a2df398616901e8934c1ef10fa47d87723b50d`; realized-scene SHA-256: `f5f2ee542fad8ea5b5618e39465af4fd2d024325ca55c46b8aecfe9ce333bfb2`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.0,0.15]},{"name":"goal","value":[0.71251,0.03972,0.15]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":5.0},{"name":"obstacle_height_m","value":0.3},{"name":"force_scale_n","value":5.0}],"object_starts":[],"obstacles":[{"name":"obstacle_block","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,0.0,0.15]}],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.71251,0.03972,0.15]}],"task_name":"obstacle_reach"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.82955,"average_solve_count":88.0,"average_success_count":88.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"arc_approach_side.approach_height":0.26112,"arc_approach_side.arc_height":0.13715,"arc_approach_side.lateral_offset":-0.62135,"arc_approach_side.speed":0.16679,"arc_approach_side.tolerance":0.03175,"descend_behind_obstacle.lateral_offset_descend":-0.58447,"descend_behind_obstacle.speed":0.12023,"descend_behind_obstacle.tolerance":0.01321,"lateral_to_goal.speed":0.10891,"lateral_to_goal.tolerance":0.01272},"optimized_scores":{"best_composite_score":-0.53,"best_fitness_score":0.0,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"obstacle_block","body_b":"link7","contact_count":447.0,"contact_point_centroid":[0.46009,-0.11725,0.29994],"force_p95":421.93366,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":465.50419,"mean_force":371.2981,"phase_index":1.0,"phase_name":"descend_behind_obstacle","phase_type":"descend","tcp_position_centroid":[0.39944,-0.10828,0.2945]},{"body_a":"obstacle_block","body_b":"link6","contact_count":275.0,"contact_point_centroid":[0.46002,-0.14428,0.29995],"force_p95":344.72743,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":382.85004,"mean_force":307.97976,"phase_index":1.0,"phase_name":"descend_behind_obstacle","phase_type":"descend","tcp_position_centroid":[0.39118,-0.12754,0.30675]},{"body_a":"obstacle_block","body_b":"link6","contact_count":991.0,"contact_point_centroid":[0.49372,-0.14344,0.29992],"force_p95":296.44562,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":323.64294,"mean_force":267.29588,"phase_index":2.0,"phase_name":"lateral_to_goal","phase_type":"align","tcp_position_centroid":[0.40584,-0.13536,0.34459]}],"total_contact_groups":3},"final_pose_error":0.40215,"key_states":{"actual_goal_position":[0.71251,0.03972,0.15],"actual_obstacle_position":[0.5,0.0,0.15],"final_tcp_position":[0.43333,-0.13122,0.38357],"realised_goal_position":[0.71251,0.03972,0.15],"realised_object_initial_position":[0.0,0.0,0.0],"realised_obstacle_position":[0.5,0.0,0.15]},"phases":[{"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.72921,"object_to_goal_dist_start":0.72921,"object_z_max":0.0,"phase_name":"arc_approach_side","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_waypoint","tcp_end":[0.35024,-0.0,0.32078],"tcp_start":[0.35027,-0.0,0.32082],"tcp_to_object_dist_end":0.47494,"terminated_normally":false,"termination_reason":"guard_failure"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.72921,"object_to_goal_dist_start":0.72921,"object_z_max":0.0,"phase_name":"descend_behind_obstacle","phase_peak_obstacle_force":465.50419,"phase_type":"descend","subtask_id":"reach_waypoint","tcp_end":[0.39434,-0.12228,0.31647],"tcp_start":[0.35024,-0.0,0.32078],"tcp_to_object_dist_end":0.5202,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.72921,"object_to_goal_dist_start":0.72921,"object_z_max":0.0,"phase_name":"lateral_to_goal","phase_peak_obstacle_force":323.64294,"phase_type":"align","subtask_id":"reach_goal","tcp_end":[0.43333,-0.13122,0.38357],"tcp_start":[0.39434,-0.12228,0.31647],"tcp_to_object_dist_end":0.5934,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `5aed51a381cd066930e6976e6d6ccfd73886636bec948604cbfe8eb976a9a4c5`; realized-scene SHA-256: `4d99f589f09839c4f3a4e389174672e239f050e8ccee110af89dc738cbe9e683`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.0,0.15]},{"name":"goal","value":[0.6827,0.04873,0.15]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":5.0},{"name":"obstacle_height_m","value":0.3},{"name":"force_scale_n","value":5.0}],"object_starts":[],"obstacles":[{"name":"obstacle_block","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,0.0,0.15]}],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.6827,0.04873,0.15]}],"task_name":"obstacle_reach"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.83516,"average_solve_count":91.0,"average_success_count":91.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"arc_approach_side.approach_height":0.20232,"arc_approach_side.arc_height":0.0871,"arc_approach_side.lateral_offset":-0.6072,"arc_approach_side.speed":0.18379,"arc_approach_side.tolerance":0.02189,"descend_behind_obstacle.lateral_offset_descend":-0.58875,"descend_behind_obstacle.speed":0.10846,"descend_behind_obstacle.tolerance":0.01705,"lateral_to_goal.speed":0.10071,"lateral_to_goal.tolerance":0.01212},"optimized_scores":{"best_composite_score":-0.53,"best_fitness_score":0.0,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"obstacle_block","body_b":"link7","contact_count":529.0,"contact_point_centroid":[0.46007,-0.12623,0.29995],"force_p95":418.71505,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":470.1645,"mean_force":341.97088,"phase_index":1.0,"phase_name":"descend_behind_obstacle","phase_type":"descend","tcp_position_centroid":[0.39721,-0.11671,0.29377]},{"body_a":"obstacle_block","body_b":"link6","contact_count":242.0,"contact_point_centroid":[0.46011,-0.14803,0.29995],"force_p95":359.77045,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":430.81001,"mean_force":304.68193,"phase_index":1.0,"phase_name":"descend_behind_obstacle","phase_type":"descend","tcp_position_centroid":[0.39038,-0.13573,0.3014]},{"body_a":"obstacle_block","body_b":"link6","contact_count":993.0,"contact_point_centroid":[0.49138,-0.14816,0.29993],"force_p95":307.27681,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":334.45513,"mean_force":270.86087,"phase_index":2.0,"phase_name":"lateral_to_goal","phase_type":"align","tcp_position_centroid":[0.40348,-0.17001,0.33133]}],"total_contact_groups":3},"final_pose_error":0.40073,"key_states":{"actual_goal_position":[0.6827,0.04873,0.15],"actual_obstacle_position":[0.5,0.0,0.15],"final_tcp_position":[0.42952,-0.16197,0.37824],"realised_goal_position":[0.6827,0.04873,0.15],"realised_object_initial_position":[0.0,0.0,0.0],"realised_obstacle_position":[0.5,0.0,0.15]},"phases":[{"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.70068,"object_to_goal_dist_start":0.70068,"object_z_max":0.0,"phase_name":"arc_approach_side","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_waypoint","tcp_end":[0.35024,-0.0,0.32078],"tcp_start":[0.35027,-0.0,0.32082],"tcp_to_object_dist_end":0.47494,"terminated_normally":false,"termination_reason":"guard_failure"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.70068,"object_to_goal_dist_start":0.70068,"object_z_max":0.0,"phase_name":"descend_behind_obstacle","phase_peak_obstacle_force":470.1645,"phase_type":"descend","subtask_id":"reach_waypoint","tcp_end":[0.38953,-0.15014,0.29981],"tcp_start":[0.35024,-0.0,0.32078],"tcp_to_object_dist_end":0.51397,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.70068,"object_to_goal_dist_start":0.70068,"object_z_max":0.0,"phase_name":"lateral_to_goal","phase_peak_obstacle_force":334.45513,"phase_type":"align","subtask_id":"reach_goal","tcp_end":[0.42952,-0.16197,0.37824],"tcp_start":[0.38953,-0.15014,0.29981],"tcp_to_object_dist_end":0.5948,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `f024bcb71fae796c72f6d149639f1bf75bdc180037c5c08610261d31ea463257`; realized-scene SHA-256: `fda113aaf8e8c099f2c28b9d9dc98e35a2e52600fa9b3eec61a8dea75fa26f9a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.0,0.15]},{"name":"goal","value":[0.73702,-0.02132,0.15]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":5.0},{"name":"obstacle_height_m","value":0.3},{"name":"force_scale_n","value":5.0}],"object_starts":[],"obstacles":[{"name":"obstacle_block","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,0.0,0.15]}],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.73702,-0.02132,0.15]}],"task_name":"obstacle_reach"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.83333,"average_solve_count":90.0,"average_success_count":90.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"arc_approach_side.approach_height":0.24287,"arc_approach_side.arc_height":0.13908,"arc_approach_side.lateral_offset":-0.52429,"arc_approach_side.speed":0.1932,"arc_approach_side.tolerance":0.03065,"descend_behind_obstacle.lateral_offset_descend":-0.49451,"descend_behind_obstacle.speed":0.07148,"descend_behind_obstacle.tolerance":0.0143,"lateral_to_goal.speed":0.08493,"lateral_to_goal.tolerance":0.01071},"optimized_scores":{"best_composite_score":-0.53,"best_fitness_score":0.0,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"obstacle_block","body_b":"link7","contact_count":578.0,"contact_point_centroid":[0.46007,-0.11045,0.29995],"force_p95":397.40819,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":449.7301,"mean_force":344.69115,"phase_index":1.0,"phase_name":"descend_behind_obstacle","phase_type":"descend","tcp_position_centroid":[0.39957,-0.10194,0.29829]},{"body_a":"obstacle_block","body_b":"link6","contact_count":201.0,"contact_point_centroid":[0.46002,-0.14019,0.29996],"force_p95":317.97201,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":325.09743,"mean_force":280.02274,"phase_index":1.0,"phase_name":"descend_behind_obstacle","phase_type":"descend","tcp_position_centroid":[0.39157,-0.12133,0.30895]},{"body_a":"obstacle_block","body_b":"link6","contact_count":995.0,"contact_point_centroid":[0.4868,-0.14383,0.29994],"force_p95":285.34859,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":318.30195,"mean_force":267.8577,"phase_index":2.0,"phase_name":"lateral_to_goal","phase_type":"align","tcp_position_centroid":[0.40201,-0.12624,0.33904]}],"total_contact_groups":3},"final_pose_error":0.39804,"key_states":{"actual_goal_position":[0.73702,-0.02132,0.15],"actual_obstacle_position":[0.5,0.0,0.15],"final_tcp_position":[0.41891,-0.12571,0.36527],"realised_goal_position":[0.73702,-0.02132,0.15],"realised_object_initial_position":[0.0,0.0,0.0],"realised_obstacle_position":[0.5,0.0,0.15]},"phases":[{"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.75244,"object_to_goal_dist_start":0.75244,"object_z_max":0.0,"phase_name":"arc_approach_side","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_waypoint","tcp_end":[0.35024,-0.0,0.32078],"tcp_start":[0.35027,-0.0,0.32082],"tcp_to_object_dist_end":0.47494,"terminated_normally":false,"termination_reason":"guard_failure"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.75244,"object_to_goal_dist_start":0.75244,"object_z_max":0.0,"phase_name":"descend_behind_obstacle","phase_peak_obstacle_force":449.7301,"phase_type":"descend","subtask_id":"reach_waypoint","tcp_end":[0.39374,-0.1179,0.31545],"tcp_start":[0.35024,-0.0,0.32078],"tcp_to_object_dist_end":0.51811,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.75244,"object_to_goal_dist_start":0.75244,"object_z_max":0.0,"phase_name":"lateral_to_goal","phase_peak_obstacle_force":318.30195,"phase_type":"align","subtask_id":"reach_goal","tcp_end":[0.41891,-0.12571,0.36527],"tcp_start":[0.39374,-0.1179,0.31545],"tcp_to_object_dist_end":0.56983,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```