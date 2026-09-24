## Search State

- **Seed**: 7
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → descend | arc_cartesian | linear_cartesian | position_control | position_control | pose_tolerance | pose_tolerance | 3 | -0.1500 | 0.00 | ❌ rejected |
| 1 | approach → descend | arc_cartesian | linear_cartesian | position_control | position_control | pose_tolerance | pose_tolerance | 3 | -0.1500 | 0.00 | ✅ accepted |
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
- Frozen task target: [0.35, 0.0, 0.32]
- Goal object position: (0.35, 0.0, 0.32)
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.5
- Force limit: 5.0 N
- Obstacle body: obstacle_block (contact = collision penalty)
- Robot initial TCP position: (0.7125095466604666, 0.039721380096957554, 0.15)
- Primary evaluation target: **TCP distance to goal position (Gaussian proximity kernel)**

## Scene Entities

robot:
  model: panda_full
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.7125095466604666, 0.039721380096957554, 0.15]
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
  frozen_targets: {'task_goal': [0.35, 0.0, 0.32]}
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
| `goal` | offset from task goal position (0.35, 0.0, 0.32) | final destination targets |
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

## Current Skill (Q=-0.150) — your mutation base

```yaml
skill: obstacle_reach
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_high
  offset:
  - 0.0
  - 0.0
  - 0.03
  weight: 0.3
- id: reach_goal
  weight: 0.7
phases:
- id: approach_arc
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
    - 0.03
  parameters:
    arc_height:
      type: scalar
      range:
      - 0.1
      - 0.35
      default: 0.2
      binds_to:
      - path: generator.arc_height
        mode: replace
    speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: obstacle_check
    when: during_phase
    predicate: contact_detected
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.05
  subtask_id: reach_high
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
  parameters:
    speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: goal_check
    when: after_phase
    predicate: pose_within_tolerance
    threshold: 0.02
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: reach_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_arc** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.03]
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=obstacle_check, when=during_phase, predicate=contact_detected, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.05]
- **descend_to_goal** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=goal_check, when=after_phase, predicate=pose_within_tolerance, on_failure=retry, threshold=0.02
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, 0.0]

## Design Metrics

- **Composite score**: -0.150
- **task_score** (E): 0.000
- **fitness_score**: 0.000  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
  → CMA-ES cannot optimise this structure (shaped reward also near zero)
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.150

**⚠ Warning**: CMA-ES stagnated + low fitness_score → structure may be fundamentally incompatible with task

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_arc | 0.00 | 0.00 | 0.0000 |
| descend_to_goal | 0.00 | 0.67 | 0.1169 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force | Obstacle/contact |
|---|---|---|---|---|---|---|---|---|---|
| approach_arc | approach | 0.00 / guard_failure | (0.350, -0.000, 0.321)→(0.350, -0.000, 0.321) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.727→0.727 | 0.00 / 0.000 | 0.000 | 0.000 | — |
| descend_to_goal | descend | 0.00 / step_budget | (0.405, 0.004, 0.310)→(0.502, 0.013, 0.372) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.727→0.727 | 0.67 / 0.667 | 424.175 | 412.665 | link7 ↔ obstacle_block/obstacle_block_geom |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- obstacle_clearance: 0.562
- path_efficiency: 0.727
- arc_smoothness: 0.979
- collision_factor: 0.000  (exp(−peak_force / force_scale))
- peak_obstacle_force: 389.635 N
- collision_location: obstacle_block  (or None if no contact)
- final_tcp_distance: 0.306
- min_tcp_distance: 0.306
- tcp_proximity_score: 0.130
- goal_reached_rate: 0.000
- peak_obstacle_counterbody: link7
- peak_obstacle_countergeom: None
- peak_obstacle_obstacle_body: obstacle_block
- peak_obstacle_obstacle_geom: obstacle_block_geom

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.000
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.000
- **Median Q (composite search score)**: -0.150
- **K-run variance**: 0.0000
- **Stagnated**: yes
  → Parameter optimiser converged to local optimum; structural change likely needed
- **Stop reason**: tolfun
- **Mean generations**: 2.0
- **Final σ (mean)**: 0.310


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
{"anchors":[{"name":"fixture","value":[0.71251,0.03972,0.15]},{"name":"goal","value":[0.5,0.0,0.15]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":5.0},{"name":"obstacle_height_m","value":0.3},{"name":"force_scale_n","value":5.0}],"object_starts":[],"obstacles":[{"name":"obstacle_block","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,0.0,0.15]}],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,0.0,0.15]}],"task_name":"obstacle_reach"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.32353,"average_solve_count":68.0,"average_success_count":68.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_arc.arc_height":0.22573,"approach_arc.speed":0.16007,"descend_to_goal.speed":0.07217},"optimized_scores":{"best_composite_score":-0.15,"best_fitness_score":0.0,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"obstacle_block","body_b":"link7","contact_count":1177.0,"contact_point_centroid":[0.46029,0.00762,0.29993],"force_p95":346.29958,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":389.63456,"mean_force":288.52965,"phase_index":1.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.40976,0.00776,0.31258]},{"body_a":"obstacle_block","body_b":"link6","contact_count":442.0,"contact_point_centroid":[0.53681,0.01712,0.29987],"force_p95":320.91018,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":388.39323,"mean_force":262.03107,"phase_index":1.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.46233,0.01747,0.36447]}],"total_contact_groups":2},"final_pose_error":0.30637,"key_states":{"actual_goal_position":[0.71251,0.03972,0.15],"actual_obstacle_position":[0.5,0.0,0.15],"final_tcp_position":[0.5038,0.02488,0.37379],"realised_goal_position":[0.71251,0.03972,0.15],"realised_object_initial_position":[0.0,0.0,0.0],"realised_obstacle_position":[0.5,0.0,0.15]},"peak_contact_force":1020.18377,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.72921,"object_to_goal_dist_start":0.72921,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_high","tcp_end":[0.35024,-0.0,0.32078],"tcp_start":[0.35027,-0.0,0.32082],"tcp_to_object_dist_end":0.47494,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1951.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.72921,"object_to_goal_dist_start":0.72921,"object_z_max":0.0,"peak_contact_force":1020.18377,"phase_name":"descend_to_goal","phase_peak_obstacle_force":389.63456,"phase_type":"descend","raw_contact_event_count":1619.0,"raw_peak_contact_force":389.63456,"subtask_id":"reach_goal","tcp_end":[0.5038,0.02488,0.37379],"tcp_start":[0.4053,0.00756,0.31148],"tcp_to_object_dist_end":0.62781,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `5aed51a381cd066930e6976e6d6ccfd73886636bec948604cbfe8eb976a9a4c5`; realized-scene SHA-256: `4d99f589f09839c4f3a4e389174672e239f050e8ccee110af89dc738cbe9e683`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.6827,0.04873,0.15]},{"name":"goal","value":[0.5,0.0,0.15]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":5.0},{"name":"obstacle_height_m","value":0.3},{"name":"force_scale_n","value":5.0}],"object_starts":[],"obstacles":[{"name":"obstacle_block","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,0.0,0.15]}],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,0.0,0.15]}],"task_name":"obstacle_reach"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.98571,"average_solve_count":70.0,"average_success_count":70.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_arc.arc_height":0.28519,"approach_arc.speed":0.13715,"descend_to_goal.speed":0.04382},"optimized_scores":{"best_composite_score":-0.15,"best_fitness_score":0.0,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"obstacle_block","body_b":"link7","contact_count":1202.0,"contact_point_centroid":[0.46023,0.00869,0.29993],"force_p95":350.36712,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":388.84073,"mean_force":295.5469,"phase_index":1.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.40697,0.00997,0.3103]},{"body_a":"obstacle_block","body_b":"link6","contact_count":412.0,"contact_point_centroid":[0.53623,0.02186,0.29985],"force_p95":307.75573,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":373.74049,"mean_force":261.76072,"phase_index":1.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.45021,0.02141,0.36283]}],"total_contact_groups":2},"final_pose_error":0.30442,"key_states":{"actual_goal_position":[0.6827,0.04873,0.15],"actual_obstacle_position":[0.5,0.0,0.15],"final_tcp_position":[0.48363,0.02775,0.37935],"realised_goal_position":[0.6827,0.04873,0.15],"realised_object_initial_position":[0.0,0.0,0.0],"realised_obstacle_position":[0.5,0.0,0.15]},"peak_contact_force":388.84073,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.70068,"object_to_goal_dist_start":0.70068,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_high","tcp_end":[0.35024,-0.0,0.32078],"tcp_start":[0.35027,-0.0,0.32082],"tcp_to_object_dist_end":0.47494,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1951.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.70068,"object_to_goal_dist_start":0.70068,"object_z_max":0.0,"peak_contact_force":252.34248,"phase_name":"descend_to_goal","phase_peak_obstacle_force":388.84073,"phase_type":"descend","raw_contact_event_count":1614.0,"raw_peak_contact_force":388.84073,"subtask_id":"reach_goal","tcp_end":[0.48363,0.02775,0.37935],"tcp_start":[0.40312,0.00975,0.3075],"tcp_to_object_dist_end":0.61528,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `f024bcb71fae796c72f6d149639f1bf75bdc180037c5c08610261d31ea463257`; realized-scene SHA-256: `fda113aaf8e8c099f2c28b9d9dc98e35a2e52600fa9b3eec61a8dea75fa26f9a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.73702,-0.02132,0.15]},{"name":"goal","value":[0.5,0.0,0.15]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":5.0},{"name":"obstacle_height_m","value":0.3},{"name":"force_scale_n","value":5.0}],"object_starts":[],"obstacles":[{"name":"obstacle_block","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,0.0,0.15]}],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,0.0,0.15]}],"task_name":"obstacle_reach"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.32353,"average_solve_count":68.0,"average_success_count":68.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_arc.arc_height":0.28225,"approach_arc.speed":0.11855,"descend_to_goal.speed":0.05492},"optimized_scores":{"best_composite_score":-0.15,"best_fitness_score":0.0,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"obstacle_block","body_b":"link6","contact_count":432.0,"contact_point_centroid":[0.53789,-0.01395,0.29987],"force_p95":342.02147,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":459.51975,"mean_force":264.21298,"phase_index":1.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.46722,-0.00887,0.36434]},{"body_a":"obstacle_block","body_b":"link7","contact_count":1166.0,"contact_point_centroid":[0.46136,-0.00401,0.29993],"force_p95":344.40626,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":397.74586,"mean_force":288.63152,"phase_index":1.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.41221,-0.00406,0.31368]}],"total_contact_groups":2},"final_pose_error":0.30641,"key_states":{"actual_goal_position":[0.73702,-0.02132,0.15],"actual_obstacle_position":[0.5,0.0,0.15],"final_tcp_position":[0.51791,-0.01403,0.36406],"realised_goal_position":[0.73702,-0.02132,0.15],"realised_object_initial_position":[0.0,0.0,0.0],"realised_obstacle_position":[0.5,0.0,0.15]},"peak_contact_force":459.51975,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.75244,"object_to_goal_dist_start":0.75244,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_high","tcp_end":[0.35024,-0.0,0.32078],"tcp_start":[0.35027,-0.0,0.32082],"tcp_to_object_dist_end":0.47494,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1951.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.75244,"object_to_goal_dist_start":0.75244,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"descend_to_goal","phase_peak_obstacle_force":459.51975,"phase_type":"descend","raw_contact_event_count":1598.0,"raw_peak_contact_force":459.51975,"subtask_id":"reach_goal","tcp_end":[0.51791,-0.01403,0.36406],"tcp_start":[0.40647,-0.00383,0.31212],"tcp_to_object_dist_end":0.63322,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```