## Search State

- **Seed**: 5
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | push → release → pull → release → release → grasp | linear_cartesian | — | arc_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | admittance_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | time_limit | time_limit | 2 | -0.2200 | 0.00 | ❌ rejected |
| 1 | push → release → pull → release → release → grasp | linear_cartesian | — | arc_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | admittance_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | time_limit | time_limit | 2 | -0.2200 | 0.00 | ❌ rejected |
| 0 | push → release → pull → release → release → grasp | linear_cartesian | — | arc_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | admittance_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | time_limit | time_limit | 2 | -0.2200 | 0.00 | ✅ accepted |

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
- Frozen realised-scene SHA-256: `35b656cc89b57a5f115ac5b9cfa690565debfcfd5af880d0b6438b747265b590`
- Frozen task target: [0.730500292374538, 0.030794078973649372, 0.15]
- Goal object position: (0.730500292374538, 0.030794078973649372, 0.15)
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
  frozen_task_target: [0.7305, 0.0308, 0.15]
  frozen_obstacle_position: [0.5, 0, 0.15]
  frozen_targets: {'task_goal': [0.730500292374538, 0.030794078973649372, 0.15]}
  frozen_obstacles: {'obstacle_block': [0.5, 0.0, 0.15]}
  goal_tolerance_m: 0.02
  force_limit_n: 5
  obstacle_height_m: 0.3
  force_scale_n: 5
  realized_scene_sha256: 35b656cc89b57a5f115ac5b9cfa690565debfcfd5af880d0b6438b747265b590

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
| `goal` | offset from task goal position (0.730500292374538, 0.030794078973649372, 0.15) | final destination targets |
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

## Current Skill (Q=-0.220) — your mutation base

```yaml
skill: obstacle_reach
skill_type: arm_gripper
phases:
- id: push_1
  type: push
  generator: linear_cartesian
  control: position_control
  termination: time_limit
  parameters:
    push_depth:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: release_1
  type: release
  control: position_control
  termination: time_limit
  end_effector_action: open
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
- id: release_2
  type: release
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
  end_effector_action: open
- id: release_3
  type: release
  generator: linear_cartesian
  control: position_control
  termination: time_limit
  end_effector_action: open
- id: grasp_1
  type: grasp
  control: position_control
  termination: time_limit
  end_effector_action: force_grasp

```

## Design Metrics

- **Composite score**: -0.220
- **task_score** (E): 0.000
- **fitness_score**: 0.000  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
  → CMA-ES cannot optimise this structure (shaped reward also near zero)
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.220

**⚠ Warning**: CMA-ES stagnated + low fitness_score → structure may be fundamentally incompatible with task

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| push_1 | 1.00 | 0.0557 |
| release_1 | 1.00 | 0.0005 |
| pull_1 | 1.00 | 0.1674 |
| release_2 | 1.00 | 0.2778 |
| release_3 | 1.00 | 0.0128 |
| grasp_1 | 1.00 | 0.0090 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| push_1 | push | 1.00 / time_limit | (0.350, -0.000, 0.321)→(0.406, 0.000, 0.315) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.732→0.732 |
| release_1 | release | 1.00 / step_budget | (0.406, 0.000, 0.315)→(0.405, 0.000, 0.315) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.732→0.732 |
| pull_1 | pull | 1.00 / time_limit | (0.405, 0.000, 0.315)→(0.556, -0.000, 0.388) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.732→0.732 |
| release_2 | release | 1.00 / step_budget | (0.556, -0.000, 0.388)→(0.687, -0.000, 0.144) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.732→0.732 |
| release_3 | release | 1.00 / time_limit | (0.687, -0.000, 0.144)→(0.691, -0.000, 0.132) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.732→0.732 |
| grasp_1 | grasp | 1.00 / step_budget | (0.691, -0.000, 0.132)→(0.688, -0.000, 0.123) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.732→0.732 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- obstacle_clearance: 0.459
- path_efficiency: 0.693
- arc_smoothness: 0.991
- final_tcp_distance: 0.048
- min_tcp_distance: 0.048
- tcp_proximity_score: 0.725
- goal_reached_rate: 0.000
- peak_obstacle_counterbody: link7
- peak_obstacle_countergeom: None
- peak_obstacle_obstacle_body: obstacle_block
- peak_obstacle_obstacle_geom: obstacle_block_geom

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.000
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.000
- **Median Q (composite search score)**: -0.220
- **K-run variance**: 0.0000
- **Stagnated**: yes
  → Parameter optimiser converged to local optimum; structural change likely needed
- **Stop reason**: tolfun
- **Mean generations**: 2.0
- **Final σ (mean)**: 0.284


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `f3b9025bd026eb63e7a6b7b9dcbae30ae5fd727c3f404b5eea2986d705494aa6`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"object_xy_delta":[0.0,0.0]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `016b297ed5457e75e60006ae43546f9e20e6368637b147588ecc5457d8da87e0`; realized-scene SHA-256: `35b656cc89b57a5f115ac5b9cfa690565debfcfd5af880d0b6438b747265b590`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.0,0.15]},{"name":"goal","value":[0.7305,0.03079,0.15]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":5.0},{"name":"obstacle_height_m","value":0.3},{"name":"force_scale_n","value":5.0}],"object_starts":[],"obstacles":[{"name":"obstacle_block","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,0.0,0.15]}],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.7305,0.03079,0.15]}],"task_name":"obstacle_reach"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.65541,"average_solve_count":148.0,"average_success_count":148.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"pull_1.pull_distance":0.10385,"push_1.push_depth":0.07884},"optimized_scores":{"best_composite_score":-0.22,"best_fitness_score":0.0,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"obstacle_block","body_b":"link7","contact_count":603.0,"contact_point_centroid":[0.46008,0.00101,0.29994],"force_p95":353.04166,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":402.92406,"mean_force":309.44787,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.40497,2e-05,0.30212]},{"body_a":"obstacle_block","body_b":"link7","contact_count":200.0,"contact_point_centroid":[0.46001,0.00129,0.29998],"force_p95":68.00606,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":139.31834,"mean_force":58.48534,"phase_index":1.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.40527,1e-05,0.31487]},{"body_a":"obstacle_block","body_b":"link7","contact_count":33.0,"contact_point_centroid":[0.46001,0.00131,0.29999],"force_p95":69.37503,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":103.56829,"mean_force":55.45116,"phase_index":2.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.40518,-0.0,0.31486]},{"body_a":"obstacle_block","body_b":"link5","contact_count":384.0,"contact_point_centroid":[0.53999,0.08605,0.29998],"force_p95":68.03438,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":70.78803,"mean_force":59.97174,"phase_index":5.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.68805,-0.00033,0.12329]}],"total_contact_groups":4},"final_pose_error":0.01103,"key_states":{"actual_goal_position":[0.7305,0.03079,0.15],"actual_obstacle_position":[0.5,0.0,0.15],"final_tcp_position":[0.6949,-0.00016,0.14022],"realised_goal_position":[0.7305,0.03079,0.15],"realised_object_initial_position":[0.0,0.0,0.0],"realised_obstacle_position":[0.5,0.0,0.15]},"phases":[{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.74638,"object_to_goal_dist_start":0.74638,"object_z_max":0.0,"phase_name":"push_1","phase_peak_obstacle_force":402.92406,"phase_type":"push","tcp_end":[0.40568,3e-05,0.31495],"tcp_start":[0.3503,-0.0,0.32087],"tcp_to_object_dist_end":0.51359,"terminated_normally":true,"termination_reason":"time_limit"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.74638,"object_to_goal_dist_start":0.74638,"object_z_max":0.0,"phase_name":"release_1","phase_peak_obstacle_force":139.31834,"phase_type":"release","tcp_end":[0.40516,0.0,0.31483],"tcp_start":[0.40568,3e-05,0.31495],"tcp_to_object_dist_end":0.5131,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.74638,"object_to_goal_dist_start":0.74638,"object_z_max":0.0,"phase_name":"pull_1","phase_peak_obstacle_force":103.56829,"phase_type":"pull","tcp_end":[0.5555,-5e-05,0.38836],"tcp_start":[0.40516,0.0,0.31483],"tcp_to_object_dist_end":0.6778,"terminated_normally":true,"termination_reason":"time_limit"},{"n_steps":892.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.74638,"object_to_goal_dist_start":0.74638,"object_z_max":0.0,"phase_name":"release_2","phase_peak_obstacle_force":0.0,"phase_type":"release","tcp_end":[0.6868,-0.00026,0.14353],"tcp_start":[0.5555,-5e-05,0.38836],"tcp_to_object_dist_end":0.70164,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":426.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.74638,"object_to_goal_dist_start":0.74638,"object_z_max":0.0,"phase_name":"release_3","phase_peak_obstacle_force":0.0,"phase_type":"release","tcp_end":[0.69137,-0.00029,0.13161],"tcp_start":[0.6868,-0.00026,0.14353],"tcp_to_object_dist_end":0.70379,"terminated_normally":true,"termination_reason":"time_limit"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.74638,"object_to_goal_dist_start":0.74638,"object_z_max":0.0,"phase_name":"grasp_1","phase_peak_obstacle_force":70.78803,"phase_type":"grasp","tcp_end":[0.68809,-0.00032,0.12326],"tcp_start":[0.69137,-0.00029,0.13161],"tcp_to_object_dist_end":0.69904,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `91da6d91b20aa8f1968f3c6d7ec8aa818a9ddb55695f45bcb9bfaacd3acccdac`; realized-scene SHA-256: `bd4f35ed59709260e094776b661704e90745f7a52d08ebc05c5947cbc49435ce`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.0,0.15]},{"name":"goal","value":[0.70382,-0.01567,0.15]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":5.0},{"name":"obstacle_height_m","value":0.3},{"name":"force_scale_n","value":5.0}],"object_starts":[],"obstacles":[{"name":"obstacle_block","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,0.0,0.15]}],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.70382,-0.01567,0.15]}],"task_name":"obstacle_reach"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.65541,"average_solve_count":148.0,"average_success_count":148.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"pull_1.pull_distance":0.14736,"push_1.push_depth":0.05483},"optimized_scores":{"best_composite_score":-0.22,"best_fitness_score":0.0,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"obstacle_block","body_b":"link7","contact_count":603.0,"contact_point_centroid":[0.46008,0.00101,0.29994],"force_p95":353.04166,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":402.92406,"mean_force":309.44787,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.40497,2e-05,0.30212]},{"body_a":"obstacle_block","body_b":"link7","contact_count":200.0,"contact_point_centroid":[0.46001,0.00129,0.29998],"force_p95":68.00606,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":139.31834,"mean_force":58.48534,"phase_index":1.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.40527,1e-05,0.31487]},{"body_a":"obstacle_block","body_b":"link7","contact_count":33.0,"contact_point_centroid":[0.46001,0.00131,0.29999],"force_p95":69.37503,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":103.56829,"mean_force":55.45116,"phase_index":2.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.40518,-0.0,0.31486]},{"body_a":"obstacle_block","body_b":"link5","contact_count":384.0,"contact_point_centroid":[0.53999,0.08605,0.29998],"force_p95":68.03438,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":70.78803,"mean_force":59.97174,"phase_index":5.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.68805,-0.00033,0.12329]}],"total_contact_groups":4},"final_pose_error":0.01103,"key_states":{"actual_goal_position":[0.70382,-0.01567,0.15],"actual_obstacle_position":[0.5,0.0,0.15],"final_tcp_position":[0.6949,-0.00016,0.14022],"realised_goal_position":[0.70382,-0.01567,0.15],"realised_object_initial_position":[0.0,0.0,0.0],"realised_obstacle_position":[0.5,0.0,0.15]},"phases":[{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.71979,"object_to_goal_dist_start":0.71979,"object_z_max":0.0,"phase_name":"push_1","phase_peak_obstacle_force":402.92406,"phase_type":"push","tcp_end":[0.40568,3e-05,0.31495],"tcp_start":[0.3503,-0.0,0.32087],"tcp_to_object_dist_end":0.51359,"terminated_normally":true,"termination_reason":"time_limit"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.71979,"object_to_goal_dist_start":0.71979,"object_z_max":0.0,"phase_name":"release_1","phase_peak_obstacle_force":139.31834,"phase_type":"release","tcp_end":[0.40516,0.0,0.31483],"tcp_start":[0.40568,3e-05,0.31495],"tcp_to_object_dist_end":0.5131,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.71979,"object_to_goal_dist_start":0.71979,"object_z_max":0.0,"phase_name":"pull_1","phase_peak_obstacle_force":103.56829,"phase_type":"pull","tcp_end":[0.5555,-5e-05,0.38836],"tcp_start":[0.40516,0.0,0.31483],"tcp_to_object_dist_end":0.6778,"terminated_normally":true,"termination_reason":"time_limit"},{"n_steps":892.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.71979,"object_to_goal_dist_start":0.71979,"object_z_max":0.0,"phase_name":"release_2","phase_peak_obstacle_force":0.0,"phase_type":"release","tcp_end":[0.6868,-0.00026,0.14353],"tcp_start":[0.5555,-5e-05,0.38836],"tcp_to_object_dist_end":0.70164,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":426.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.71979,"object_to_goal_dist_start":0.71979,"object_z_max":0.0,"phase_name":"release_3","phase_peak_obstacle_force":0.0,"phase_type":"release","tcp_end":[0.69137,-0.00029,0.13161],"tcp_start":[0.6868,-0.00026,0.14353],"tcp_to_object_dist_end":0.70379,"terminated_normally":true,"termination_reason":"time_limit"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.71979,"object_to_goal_dist_start":0.71979,"object_z_max":0.0,"phase_name":"grasp_1","phase_peak_obstacle_force":70.78803,"phase_type":"grasp","tcp_end":[0.68809,-0.00032,0.12326],"tcp_start":[0.69137,-0.00029,0.13161],"tcp_to_object_dist_end":0.69904,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `fc3e8abaaf02ca668222d0cd4e885164ebd20230be343b2ee428dfce1066794d`; realized-scene SHA-256: `f5f2ee542fad8ea5b5618e39465af4fd2d024325ca55c46b8aecfe9ce333bfb2`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.0,0.15]},{"name":"goal","value":[0.71251,0.03972,0.15]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":5.0},{"name":"obstacle_height_m","value":0.3},{"name":"force_scale_n","value":5.0}],"object_starts":[],"obstacles":[{"name":"obstacle_block","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,0.0,0.15]}],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.71251,0.03972,0.15]}],"task_name":"obstacle_reach"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.65541,"average_solve_count":148.0,"average_success_count":148.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"pull_1.pull_distance":0.09873,"push_1.push_depth":0.05801},"optimized_scores":{"best_composite_score":-0.22,"best_fitness_score":0.0,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"obstacle_block","body_b":"link7","contact_count":603.0,"contact_point_centroid":[0.46008,0.00101,0.29994],"force_p95":353.04166,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":402.92406,"mean_force":309.44787,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.40497,2e-05,0.30212]},{"body_a":"obstacle_block","body_b":"link7","contact_count":200.0,"contact_point_centroid":[0.46001,0.00129,0.29998],"force_p95":68.00606,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":139.31834,"mean_force":58.48534,"phase_index":1.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.40527,1e-05,0.31487]},{"body_a":"obstacle_block","body_b":"link7","contact_count":33.0,"contact_point_centroid":[0.46001,0.00131,0.29999],"force_p95":69.37503,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":103.56829,"mean_force":55.45116,"phase_index":2.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.40518,-0.0,0.31486]},{"body_a":"obstacle_block","body_b":"link5","contact_count":384.0,"contact_point_centroid":[0.53999,0.08605,0.29998],"force_p95":68.03438,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":70.78803,"mean_force":59.97174,"phase_index":5.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.68805,-0.00033,0.12329]}],"total_contact_groups":4},"final_pose_error":0.01103,"key_states":{"actual_goal_position":[0.71251,0.03972,0.15],"actual_obstacle_position":[0.5,0.0,0.15],"final_tcp_position":[0.6949,-0.00016,0.14022],"realised_goal_position":[0.71251,0.03972,0.15],"realised_object_initial_position":[0.0,0.0,0.0],"realised_obstacle_position":[0.5,0.0,0.15]},"phases":[{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.72921,"object_to_goal_dist_start":0.72921,"object_z_max":0.0,"phase_name":"push_1","phase_peak_obstacle_force":402.92406,"phase_type":"push","tcp_end":[0.40568,3e-05,0.31495],"tcp_start":[0.3503,-0.0,0.32087],"tcp_to_object_dist_end":0.51359,"terminated_normally":true,"termination_reason":"time_limit"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.72921,"object_to_goal_dist_start":0.72921,"object_z_max":0.0,"phase_name":"release_1","phase_peak_obstacle_force":139.31834,"phase_type":"release","tcp_end":[0.40516,0.0,0.31483],"tcp_start":[0.40568,3e-05,0.31495],"tcp_to_object_dist_end":0.5131,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.72921,"object_to_goal_dist_start":0.72921,"object_z_max":0.0,"phase_name":"pull_1","phase_peak_obstacle_force":103.56829,"phase_type":"pull","tcp_end":[0.5555,-5e-05,0.38836],"tcp_start":[0.40516,0.0,0.31483],"tcp_to_object_dist_end":0.6778,"terminated_normally":true,"termination_reason":"time_limit"},{"n_steps":892.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.72921,"object_to_goal_dist_start":0.72921,"object_z_max":0.0,"phase_name":"release_2","phase_peak_obstacle_force":0.0,"phase_type":"release","tcp_end":[0.6868,-0.00026,0.14353],"tcp_start":[0.5555,-5e-05,0.38836],"tcp_to_object_dist_end":0.70164,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":426.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.72921,"object_to_goal_dist_start":0.72921,"object_z_max":0.0,"phase_name":"release_3","phase_peak_obstacle_force":0.0,"phase_type":"release","tcp_end":[0.69137,-0.00029,0.13161],"tcp_start":[0.6868,-0.00026,0.14353],"tcp_to_object_dist_end":0.70379,"terminated_normally":true,"termination_reason":"time_limit"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.72921,"object_to_goal_dist_start":0.72921,"object_z_max":0.0,"phase_name":"grasp_1","phase_peak_obstacle_force":70.78803,"phase_type":"grasp","tcp_end":[0.68809,-0.00032,0.12326],"tcp_start":[0.69137,-0.00029,0.13161],"tcp_to_object_dist_end":0.69904,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```