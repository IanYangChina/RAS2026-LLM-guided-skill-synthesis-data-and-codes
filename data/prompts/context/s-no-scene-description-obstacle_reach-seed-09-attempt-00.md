## Search State

- **Seed**: 9
- **Iteration**: 1 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 0 | rotate → pull → push → descend → descend | arc_cartesian | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | impedance_control | impedance_control | position_control | admittance_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | contact_detected | 4 | -0.2900 | 0.00 | ✅ accepted |

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

## Current Skill (Q=-0.290) — your mutation base

```yaml
skill: obstacle_reach
phases:
- id: rotate_1
  type: rotate
  generator: arc_cartesian
  control: impedance_control
  termination: time_limit
- id: pull_1
  type: pull
  generator: arc_cartesian
  control: impedance_control
  termination: time_limit
  parameters:
    pull_distance:
      type: scalar
      range:
      - 0.02
      - 0.2
- id: push_1
  type: push
  generator: impedance_motion
  control: position_control
  termination: time_limit
  parameters:
    push_depth:
      type: scalar
      range:
      - 0.01
      - 0.1
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
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
- id: descend_2
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: contact_detected

```

## Design Metrics

- **Composite score**: -0.290
- **task_score** (E): 0.000
- **fitness_score**: 0.000  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
  → CMA-ES cannot optimise this structure (shaped reward also near zero)
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.290

**⚠ Warning**: CMA-ES stagnated + low fitness_score → structure may be fundamentally incompatible with task

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| rotate_1 | 1.00 | 0.00 | 0.1700 |
| pull_1 | 1.00 | 0.00 | 0.1640 |
| push_1 | 1.00 | 1.00 | 0.2191 |
| descend_1 | 1.00 | 1.00 | 0.0060 |
| descend_2 | 1.00 | 1.00 | 0.0023 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force | Obstacle/contact |
|---|---|---|---|---|---|---|---|---|---|
| rotate_1 | rotate | 1.00 / time_limit | (0.350, -0.000, 0.321)→(0.500, 0.000, 0.401) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.731→0.731 | 0.00 / 0.000 | 0.000 | 0.000 | — |
| pull_1 | pull | 1.00 / time_limit | (0.500, 0.000, 0.401)→(0.663, -0.000, 0.383) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.731→0.731 | 0.00 / 0.000 | 0.000 | 0.000 | — |
| push_1 | push | 1.00 / time_limit | (0.663, -0.000, 0.383)→(0.699, 0.001, 0.167) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.731→0.731 | 1.00 / 1.000 | 151.494 | 172.351 | link5 ↔ obstacle_block/obstacle_block_geom |
| descend_1 | descend | 1.00 / step_budget | (0.699, 0.001, 0.167)→(0.704, 0.002, 0.163) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.731→0.731 | 1.00 / 1.000 | 179.532 | 193.030 | link5 ↔ obstacle_block/obstacle_block_geom |
| descend_2 | descend | 1.00 / step_budget | (0.704, 0.002, 0.163)→(0.704, 0.002, 0.161) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.731→0.731 | 1.00 / 1.000 | 160.278 | 162.529 | link5 ↔ obstacle_block/obstacle_block_geom |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- obstacle_clearance: 0.637
- path_efficiency: 0.668
- arc_smoothness: 0.992
- collision_factor: 0.000  (exp(−peak_force / force_scale))
- peak_obstacle_force: 192.949 N
- collision_location: obstacle_block  (or None if no contact)
- final_tcp_distance: 0.041
- min_tcp_distance: 0.041
- tcp_proximity_score: 0.759
- goal_reached_rate: 0.000
- peak_obstacle_counterbody: link5
- peak_obstacle_countergeom: None
- peak_obstacle_obstacle_body: obstacle_block
- peak_obstacle_obstacle_geom: obstacle_block_geom

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.000
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.000
- **Median Q (composite search score)**: -0.290
- **K-run variance**: 0.0000
- **Stagnated**: yes
  → Parameter optimiser converged to local optimum; structural change likely needed
- **Stop reason**: tolfun
- **Mean generations**: 2.0
- **Final σ (mean)**: 0.249


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `4a44882555f0d0b14e6aa599db443a998da24652eb9b9e2830cc337dec76aa35`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"object_xy_delta":[0.0,0.0]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `47104ba1d83b6713840746a9744b8461d7698be90a7b9bbdb4a5ee2c9b597658`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.08911,"average_solve_count":202.0,"average_success_count":202.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"pull_1.pull_distance":0.10578,"push_1.push_depth":0.04678,"push_1.push_distance":0.0707,"push_1.push_speed":0.05062},"optimized_scores":{"best_composite_score":-0.29,"best_fitness_score":0.0,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"obstacle_block","body_b":"link5","contact_count":222.0,"contact_point_centroid":[0.53996,0.10292,0.29995],"force_p95":188.63402,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":192.94903,"mean_force":169.65433,"phase_index":3.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.70266,0.00215,0.16444]},{"body_a":"obstacle_block","body_b":"link5","contact_count":93.0,"contact_point_centroid":[0.53996,0.10499,0.29996],"force_p95":163.82412,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":167.8056,"mean_force":130.47308,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.69635,0.00078,0.1679]},{"body_a":"obstacle_block","body_b":"link5","contact_count":367.0,"contact_point_centroid":[0.53998,0.10153,0.29997],"force_p95":160.68862,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":162.08824,"mean_force":136.67242,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.7045,0.00207,0.16179]}],"total_contact_groups":3},"final_pose_error":0.01183,"key_states":{"actual_goal_position":[0.73702,-0.02132,0.15],"actual_obstacle_position":[0.5,0.0,0.15],"final_tcp_position":[0.70444,0.00191,0.1608],"realised_goal_position":[0.73702,-0.02132,0.15],"realised_object_initial_position":[0.0,0.0,0.0],"realised_obstacle_position":[0.5,0.0,0.15]},"peak_contact_force":192.94903,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.75244,"object_to_goal_dist_start":0.75244,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.5003,0.0,0.40078],"tcp_start":[0.3503,-0.0,0.32087],"tcp_to_object_dist_end":0.64104,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.75244,"object_to_goal_dist_start":0.75244,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"pull_1","phase_peak_obstacle_force":0.0,"phase_type":"pull","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.66329,-5e-05,0.3827],"tcp_start":[0.5003,0.0,0.40078],"tcp_to_object_dist_end":0.76577,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.75244,"object_to_goal_dist_start":0.75244,"object_z_max":0.0,"peak_contact_force":158.28891,"phase_name":"push_1","phase_peak_obstacle_force":167.8056,"phase_type":"push","raw_contact_event_count":93.0,"raw_peak_contact_force":167.8056,"tcp_end":[0.69944,0.00148,0.16659],"tcp_start":[0.66329,-5e-05,0.3827],"tcp_to_object_dist_end":0.71901,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":230.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.75244,"object_to_goal_dist_start":0.75244,"object_z_max":0.0,"peak_contact_force":166.58234,"phase_name":"descend_1","phase_peak_obstacle_force":192.94903,"phase_type":"descend","raw_contact_event_count":222.0,"raw_peak_contact_force":192.94903,"tcp_end":[0.70426,0.00219,0.16287],"tcp_start":[0.69944,0.00148,0.16659],"tcp_to_object_dist_end":0.72285,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":368.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.75244,"object_to_goal_dist_start":0.75244,"object_z_max":0.0,"peak_contact_force":159.87393,"phase_name":"descend_2","phase_peak_obstacle_force":162.08824,"phase_type":"descend","raw_contact_event_count":367.0,"raw_peak_contact_force":162.08824,"tcp_end":[0.70444,0.00191,0.1608],"tcp_start":[0.70426,0.00219,0.16287],"tcp_to_object_dist_end":0.72256,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `dd76534a039a46a09f9e3c15723c51c6f1027acc2aa2ab4b06e8dae86dbdcd96`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.09524,"average_solve_count":189.0,"average_success_count":189.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"pull_1.pull_distance":0.10149,"push_1.push_depth":0.05366,"push_1.push_distance":0.1098,"push_1.push_speed":0.05893},"optimized_scores":{"best_composite_score":-0.29,"best_fitness_score":0.0,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"obstacle_block","body_b":"link5","contact_count":221.0,"contact_point_centroid":[0.53995,0.10282,0.29995],"force_p95":188.33219,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":192.59778,"mean_force":170.04557,"phase_index":3.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.70287,0.00216,0.16435]},{"body_a":"obstacle_block","body_b":"link5","contact_count":98.0,"contact_point_centroid":[0.53997,0.10494,0.29997],"force_p95":171.40118,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":187.06719,"mean_force":134.32561,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.69655,0.00083,0.16785]},{"body_a":"obstacle_block","body_b":"link5","contact_count":374.0,"contact_point_centroid":[0.53999,0.10158,0.29999],"force_p95":161.14855,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":162.55291,"mean_force":135.81928,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.70455,0.00213,0.16195]}],"total_contact_groups":3},"final_pose_error":0.01192,"key_states":{"actual_goal_position":[0.7456,-0.02923,0.15],"actual_obstacle_position":[0.5,0.0,0.15],"final_tcp_position":[0.70447,0.00198,0.16088],"realised_goal_position":[0.7456,-0.02923,0.15],"realised_object_initial_position":[0.0,0.0,0.0],"realised_obstacle_position":[0.5,0.0,0.15]},"peak_contact_force":192.59778,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.7611,"object_to_goal_dist_start":0.7611,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.5003,0.0,0.40078],"tcp_start":[0.3503,-0.0,0.32087],"tcp_to_object_dist_end":0.64104,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.7611,"object_to_goal_dist_start":0.7611,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"pull_1","phase_peak_obstacle_force":0.0,"phase_type":"pull","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.66329,-5e-05,0.3827],"tcp_start":[0.5003,0.0,0.40078],"tcp_to_object_dist_end":0.76577,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.7611,"object_to_goal_dist_start":0.7611,"object_z_max":0.0,"peak_contact_force":171.11954,"phase_name":"push_1","phase_peak_obstacle_force":187.06719,"phase_type":"push","raw_contact_event_count":98.0,"raw_peak_contact_force":187.06719,"tcp_end":[0.69998,0.0016,0.16647],"tcp_start":[0.66329,-5e-05,0.3827],"tcp_to_object_dist_end":0.7195,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":227.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.7611,"object_to_goal_dist_start":0.7611,"object_z_max":0.0,"peak_contact_force":185.75019,"phase_name":"descend_1","phase_peak_obstacle_force":192.59778,"phase_type":"descend","raw_contact_event_count":221.0,"raw_peak_contact_force":192.59778,"tcp_end":[0.70447,0.00217,0.16326],"tcp_start":[0.69998,0.0016,0.16647],"tcp_to_object_dist_end":0.72315,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":375.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.7611,"object_to_goal_dist_start":0.7611,"object_z_max":0.0,"peak_contact_force":160.34285,"phase_name":"descend_2","phase_peak_obstacle_force":162.55291,"phase_type":"descend","raw_contact_event_count":374.0,"raw_peak_contact_force":162.55291,"tcp_end":[0.70447,0.00198,0.16088],"tcp_start":[0.70447,0.00217,0.16326],"tcp_to_object_dist_end":0.72261,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `b9c2919c979234936a5d994fa5db826639b75dec9196808e9cc353d4e638017c`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.08451,"average_solve_count":213.0,"average_success_count":213.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"pull_1.pull_distance":0.11535,"push_1.push_depth":0.04061,"push_1.push_distance":0.08772,"push_1.push_speed":0.04476},"optimized_scores":{"best_composite_score":-0.29,"best_fitness_score":0.0,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"obstacle_block","body_b":"link5","contact_count":230.0,"contact_point_centroid":[0.53995,0.10299,0.29995],"force_p95":188.76139,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":193.54356,"mean_force":169.99505,"phase_index":3.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.7025,0.00214,0.16454]},{"body_a":"obstacle_block","body_b":"link5","contact_count":372.0,"contact_point_centroid":[0.53999,0.10168,0.29999],"force_p95":161.44484,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":162.9448,"mean_force":136.11831,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.70448,0.0022,0.16194]},{"body_a":"obstacle_block","body_b":"link5","contact_count":91.0,"contact_point_centroid":[0.53997,0.10506,0.29997],"force_p95":149.55116,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":162.17973,"mean_force":124.96298,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.69619,0.00075,0.16803]}],"total_contact_groups":3},"final_pose_error":0.01195,"key_states":{"actual_goal_position":[0.66286,-7e-05,0.15],"actual_obstacle_position":[0.5,0.0,0.15],"final_tcp_position":[0.70446,0.00206,0.1609],"realised_goal_position":[0.66286,-7e-05,0.15],"realised_object_initial_position":[0.0,0.0,0.0],"realised_obstacle_position":[0.5,0.0,0.15]},"peak_contact_force":193.54356,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.67962,"object_to_goal_dist_start":0.67962,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.5003,0.0,0.40078],"tcp_start":[0.3503,-0.0,0.32087],"tcp_to_object_dist_end":0.64104,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.67962,"object_to_goal_dist_start":0.67962,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"pull_1","phase_peak_obstacle_force":0.0,"phase_type":"pull","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.66329,-5e-05,0.3827],"tcp_start":[0.5003,0.0,0.40078],"tcp_to_object_dist_end":0.76577,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.67962,"object_to_goal_dist_start":0.67962,"object_z_max":0.0,"peak_contact_force":125.0747,"phase_name":"push_1","phase_peak_obstacle_force":162.17973,"phase_type":"push","raw_contact_event_count":91.0,"raw_peak_contact_force":162.17973,"tcp_end":[0.69907,0.0014,0.16676],"tcp_start":[0.66329,-5e-05,0.3827],"tcp_to_object_dist_end":0.71869,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":237.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.67962,"object_to_goal_dist_start":0.67962,"object_z_max":0.0,"peak_contact_force":186.26255,"phase_name":"descend_1","phase_peak_obstacle_force":193.54356,"phase_type":"descend","raw_contact_event_count":230.0,"raw_peak_contact_force":193.54356,"tcp_end":[0.70435,0.00224,0.16325],"tcp_start":[0.69907,0.0014,0.16676],"tcp_to_object_dist_end":0.72302,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":373.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.67962,"object_to_goal_dist_start":0.67962,"object_z_max":0.0,"peak_contact_force":160.61787,"phase_name":"descend_2","phase_peak_obstacle_force":162.9448,"phase_type":"descend","raw_contact_event_count":372.0,"raw_peak_contact_force":162.9448,"tcp_end":[0.70446,0.00206,0.1609],"tcp_start":[0.70435,0.00224,0.16325],"tcp_to_object_dist_end":0.7226,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```