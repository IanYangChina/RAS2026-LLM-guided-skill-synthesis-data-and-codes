## Search State

- **Seed**: 2
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → descend | arc_cartesian | linear_cartesian | position_control | position_control | pose_tolerance | pose_tolerance | 5 | 0.0428 | 0.29 | ❌ rejected |
| 7 | approach → approach | arc_cartesian | arc_cartesian | position_control | position_control | pose_tolerance | pose_tolerance | 6 | 0.0580 | 0.36 | ✅ accepted |
| 6 | approach → approach | arc_cartesian | linear_cartesian | position_control | position_control | pose_tolerance | pose_tolerance | 5 | 0.0428 | 0.29 | ❌ rejected |
| 5 | approach → approach | arc_cartesian | linear_cartesian | position_control | position_control | pose_tolerance | pose_tolerance | 5 | -0.2113 | 0.04 | ❌ rejected |
| 4 | approach → approach | arc_cartesian | linear_cartesian | position_control | position_control | pose_tolerance | pose_tolerance | 5 | 0.0428 | 0.29 | ❌ rejected |

**Proposal policy**: task_score is 0.29 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.5
- Force limit: 5.0 N
- Obstacle body: obstacle_block (contact = collision penalty)
- Primary evaluation target: **TCP distance to goal position (Gaussian proximity kernel)**

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
| `goal` | offset from task goal position | final destination targets |
| `fixture` | offset from fixture pose | approach/contact targets near fixture |

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

## Current Skill (Q=0.043) — your mutation base

```yaml
skill: obstacle_reach
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: approach_above_goal
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.3
- id: reach_goal
  weight: 0.7
phases:
- id: approach_1
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
    - 0.15
    tolerance: 0.02
  parameters:
    arc_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.12
      binds_to:
      - path: generator.arc_height
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.15
      default: 0.08
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
  subtask_id: approach_above_goal
- id: descend_to_goal
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
    - 0.0
    tolerance: 0.02
  parameters:
    arc_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.arc_height
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.15
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    tolerance:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.03
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  guards:
  - id: obstacle_contact_guard
    when: during_phase
    predicate: contact_detected
    threshold: 0.5
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
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
    - tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **descend_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
    - tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
  - guards:
    - id=obstacle_contact_guard, when=during_phase, predicate=contact_detected, on_failure=retry, threshold=0.5
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.05, 0.0]

## Design Metrics

- **Composite score**: 0.043
- **task_score** (E): 0.293
- **fitness_score**: 0.293  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.250

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 0.33 | 0.00 | 0.3240 |
| descend_1 | 0.67 | 0.67 | 0.1611 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force | Obstacle/contact |
|---|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 0.33 / step_budget | (0.350, -0.000, 0.321)→(0.673, -0.015, 0.338) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.709→0.709 | 0.00 / 0.000 | 0.000 | 0.000 | — |
| descend_1 | descend | 0.67 / step_budget | (0.673, -0.015, 0.338)→(0.697, -0.015, 0.179) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.709→0.709 | 0.67 / 0.667 | 142.694 | 182.218 | link5 ↔ obstacle_block/obstacle_block_geom |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- obstacle_clearance: 0.809
- path_efficiency: 0.714
- arc_smoothness: 0.995
- collision_factor: 1.000  (exp(−peak_force / force_scale))
- peak_obstacle_force: 0.000 N
- collision_location: obstacle_block  (or None if no contact)
- final_tcp_distance: 0.019
- min_tcp_distance: 0.019
- tcp_proximity_score: 0.878
- goal_reached_rate: 1.000
- peak_obstacle_counterbody: None
- peak_obstacle_countergeom: None
- peak_obstacle_obstacle_body: None
- peak_obstacle_obstacle_geom: None

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.878
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.878
- **Median Q (composite search score)**: -0.250
- **K-run variance**: 0.1715
- **Stagnated**: yes
  → Parameter optimiser converged to local optimum; structural change likely needed
- **Stop reason**: tolfun
- **Mean generations**: 4.3
- **Final σ (mean)**: 0.251


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `f800b324b333bf92ab38395ea2012437ea47aa487cfa00211f655ffc1e1f3195`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"object_xy_delta":[0.0,0.0]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `3279d67c4edbf0c030d9541a1fc5a04a28b1fb39645a052c44a102acb501fa91`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.208,"average_solve_count":125.0,"average_success_count":125.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.arc_height":0.16112,"approach_1.speed":0.09134,"approach_1.tolerance":0.0184,"descend_1.speed":0.0754,"descend_1.tolerance":0.03175},"optimized_scores":{"best_composite_score":-0.25,"best_fitness_score":0.0,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"obstacle_block","body_b":"link5","contact_count":142.0,"contact_point_centroid":[0.53996,0.05954,0.29998],"force_p95":232.15328,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":238.66717,"mean_force":200.09175,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.6774,-0.01992,0.18635]},{"body_a":"obstacle_block","body_b":"link6","contact_count":5.0,"contact_point_centroid":[0.53994,-0.03907,0.29998],"force_p95":148.99994,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":150.85854,"mean_force":134.58831,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.67012,-0.01994,0.20524]}],"total_contact_groups":2},"final_pose_error":0.01987,"key_states":{"actual_goal_position":[0.67616,-0.02015,0.15],"actual_obstacle_position":[0.5,0.0,0.15],"final_tcp_position":[0.68057,-0.01972,0.16937],"realised_goal_position":[0.67616,-0.02015,0.15],"realised_object_initial_position":[0.0,0.0,0.0],"realised_obstacle_position":[0.5,0.0,0.15]},"peak_contact_force":238.66717,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.69289,"object_to_goal_dist_start":0.69289,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_above_goal","tcp_end":[0.66288,-0.0194,0.35843],"tcp_start":[0.3503,-0.0,0.32087],"tcp_to_object_dist_end":0.75383,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":440.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.69289,"object_to_goal_dist_start":0.69289,"object_z_max":0.0,"peak_contact_force":175.75244,"phase_name":"descend_1","phase_peak_obstacle_force":238.66717,"phase_type":"descend","raw_contact_event_count":147.0,"raw_peak_contact_force":238.66717,"subtask_id":"reach_goal","tcp_end":[0.68057,-0.01972,0.16937],"tcp_start":[0.66288,-0.0194,0.35843],"tcp_to_object_dist_end":0.70161,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `66d26d1c2bdf955217f340b9b03f23361c9eeea750a84bd79880abed4fe043dd`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.95522,"average_solve_count":134.0,"average_success_count":134.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.arc_height":0.11279,"approach_1.speed":0.06872,"approach_1.tolerance":0.03004,"descend_1.speed":0.0829,"descend_1.tolerance":0.01888},"optimized_scores":{"best_composite_score":-0.25,"best_fitness_score":0.0,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"obstacle_block","body_b":"link6","contact_count":352.0,"contact_point_centroid":[0.53993,-0.0244,0.29995],"force_p95":279.50401,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":307.98574,"mean_force":241.24575,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.66419,-0.02626,0.21386]},{"body_a":"obstacle_block","body_b":"link5","contact_count":84.0,"contact_point_centroid":[0.53994,0.01057,0.29997],"force_p95":284.90515,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":291.00797,"mean_force":197.9664,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.67003,-0.02629,0.20466]}],"total_contact_groups":2},"final_pose_error":0.05137,"key_states":{"actual_goal_position":[0.65856,-0.02632,0.15],"actual_obstacle_position":[0.5,0.0,0.15],"final_tcp_position":[0.6731,-0.02631,0.19927],"realised_goal_position":[0.65856,-0.02632,0.15],"realised_object_initial_position":[0.0,0.0,0.0],"realised_obstacle_position":[0.5,0.0,0.15]},"peak_contact_force":307.98574,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":920.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.67594,"object_to_goal_dist_start":0.67594,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_above_goal","tcp_end":[0.64756,-0.02548,0.31653],"tcp_start":[0.3503,-0.0,0.32087],"tcp_to_object_dist_end":0.72123,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":579.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.67594,"object_to_goal_dist_start":0.67594,"object_z_max":0.0,"peak_contact_force":252.3296,"phase_name":"descend_1","phase_peak_obstacle_force":307.98574,"phase_type":"descend","raw_contact_event_count":436.0,"raw_peak_contact_force":307.98574,"subtask_id":"reach_goal","tcp_end":[0.6731,-0.02631,0.19927],"tcp_start":[0.64756,-0.02548,0.31653],"tcp_to_object_dist_end":0.70247,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `b7b048f5d0b9db8e06f7a4e7cd38174b92fd1a59140bfe1012f881edd44f4223`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.7619,"average_solve_count":147.0,"average_success_count":147.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.arc_height":0.10975,"approach_1.speed":0.08481,"approach_1.tolerance":0.02769,"descend_1.speed":0.06789,"descend_1.tolerance":0.02518},"optimized_scores":{"best_composite_score":0.62838,"best_fitness_score":0.87838,"best_task_score":0.87838},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[],"total_contact_groups":0},"final_pose_error":0.01945,"key_states":{"actual_goal_position":[0.74431,0.00113,0.15],"actual_obstacle_position":[0.5,0.0,0.15],"final_tcp_position":[0.7367,0.00099,0.1679],"realised_goal_position":[0.74431,0.00113,0.15],"realised_object_initial_position":[0.0,0.0,0.0],"realised_obstacle_position":[0.5,0.0,0.15]},"peak_contact_force":0.0,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.75927,"object_to_goal_dist_start":0.75927,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_above_goal","tcp_end":[0.70815,0.00096,0.33886],"tcp_start":[0.3503,-0.0,0.32087],"tcp_to_object_dist_end":0.78505,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":299.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.75927,"object_to_goal_dist_start":0.75927,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_goal","tcp_end":[0.7367,0.00099,0.1679],"tcp_start":[0.70815,0.00096,0.33886],"tcp_to_object_dist_end":0.75559,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```