## Search State

- **Seed**: 6
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | admittance_control | pose_tolerance | force_exceeded | pose_tolerance | 8 | 0.2751 | 0.83 | ✅ accepted |
| 7 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | admittance_control | pose_tolerance | pose_tolerance | pose_tolerance | 10 | -0.2136 | 0.09 | ❌ rejected |
| 6 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | force_exceeded | 8 | 0.0512 | 0.24 | ❌ rejected |
| 5 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | admittance_control | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.0582 | 0.26 | ❌ rejected |
| 4 | approach → align → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.3328 | 0.29 | ❌ rejected |

**Proposal policy**: task_score is 0.83 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

- Task name: push_to_goal
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.8
- Force limit: 25.0 N
- Primary evaluation target: **object displacement ratio toward goal_object_position**

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
| `object` | offset from object initial position | approach/contact targets near object start |
| `goal` | offset from task goal position | final destination targets |
| `fixture` | offset from fixture pose | targets near fixture |

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

## Current Skill (Q=0.275) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: approach_box
  anchor: object
  offset:
  - 0.0
  - 0.1
  - 0.1
  weight: 0.3
- id: contact_pose
  anchor: object
  offset:
  - 0.0
  - 0.06
  - 0.0
  weight: 0.2
- id: goal_reach
  weight: 0.5
phases:
- id: approach
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.1
    - 0.1
  parameters:
    approach_offset_y:
      type: scalar
      range:
      - 0.06
      - 0.16
      default: 0.1
      binds_to:
      - path: target.offset.y
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.08
      - 0.2
      default: 0.12
      binds_to:
      - path: generator.speed
        mode: replace
    approach_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.02
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: approach_box
- id: descend_to_side
  type: descend
  generator: linear_cartesian
  control: impedance_control
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.06
    - 0.0
  parameters:
    descend_offset_y:
      type: scalar
      range:
      - 0.03
      - 0.1
      default: 0.06
      binds_to:
      - path: target.offset.y
        mode: replace
    descend_speed:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    force_threshold:
      type: scalar
      range:
      - 8.0
      - 20.0
      default: 12.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
  guards:
  - id: contact_check
    when: after_phase
    predicate: contact_detected
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.02
    - -0.01
  subtask_id: contact_pose
- id: push_to_goal
  type: push
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
  parameters:
    push_speed:
      type: scalar
      range:
      - 0.015
      - 0.06
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
    push_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.025
      default: 0.015
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  guards:
  - id: force_guard
    when: during_phase
    predicate: force_below
    threshold: 30.0
    on_failure: continue
  subtask_id: goal_reach

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.1, 0.1]
  - parameter_bindings:
    - approach_offset_y: status=consumed; consumers=target.offset.y (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - approach_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **descend_to_side** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.06, 0.0]
  - parameter_bindings:
    - descend_offset_y: status=consumed; consumers=target.offset.y (replace)
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - force_threshold: status=consumed; consumers=termination.force_threshold (replace)
  - guards:
    - id=contact_check, when=after_phase, predicate=contact_detected, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.02, -0.01]
- **push_to_goal** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - push_speed: status=consumed; consumers=generator.speed (replace)
    - push_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
  - guards:
    - id=force_guard, when=during_phase, predicate=force_below, on_failure=continue, threshold=30.0

## Design Metrics

- **Composite score**: 0.275
- **task_score** (E): 0.834
- **fitness_score**: 0.705  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.430

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach | 1.00 | 1.00 | 0.2183 |
| descend_to_side | 0.00 | 1.00 | 0.1117 |
| push_to_goal | 0.67 | 1.00 | 0.1962 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, 0.133, 0.131) | (0.500, 0.029, 0.025)→(0.500, 0.029, 0.025) | 0.180→0.180 | 1.00 / 4.000 | 0.245 | 0.245 |
| descend_to_side | descend | 0.00 / step_budget | (0.496, 0.133, 0.131)→(0.495, 0.096, 0.026) | (0.500, 0.029, 0.025)→(0.500, 0.029, 0.025) | 0.180→0.180 | 1.00 / 4.000 | 0.245 | 0.245 |
| push_to_goal | push | 0.67 / step_budget | (0.495, 0.096, 0.026)→(0.496, -0.100, 0.020) | (0.500, 0.029, 0.025)→(0.502, -0.137, 0.025) | 0.180→0.029 | 1.00 / 2.333 | 1.024 | 24.417 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.719
- goal_progress: 0.822
- terminal_score: 0.822
- phase_score: 0.784
- phase_breakdown.goal_reach_score: 0.742
- phase_breakdown.approach_box_score: 0.785
- phase_breakdown.contact_pose_score: 0.885

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.799
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.993
- **Median Q (composite search score)**: 0.352
- **K-run variance**: 0.0147
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.303


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `acf3715aaa310bcc73047d49f01e71bc863ef036ae437b7dc851a0f6d3fe40ae`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `ec1d0331416d42e6883eeb3b72499fac99c0735b785eb70ece69dc94e8044fc3`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.17277,"average_solve_count":191.0,"average_success_count":191.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_offset_y":0.10332,"approach.approach_speed":0.14782,"approach.approach_tolerance":0.01396,"descend_to_side.descend_offset_y":0.06234,"descend_to_side.descend_speed":0.04181,"descend_to_side.force_threshold":8.12871,"push_to_goal.push_speed":0.03673,"push_to_goal.push_tolerance":0.01129},"optimized_scores":{"best_composite_score":0.36877,"best_fitness_score":0.79877,"best_task_score":0.82163},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":719.0,"contact_point_centroid":[0.50532,-0.07162,0.03914],"force_p95":17.75668,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.48385,"mean_force":4.82217,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.49601,-0.05979,0.02091]},{"body_a":"world","body_b":"push_box","contact_count":1614.0,"contact_point_centroid":[0.50306,-0.08253,-4e-05],"force_p95":10.82888,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.50703,"mean_force":2.73796,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.49641,-0.02976,0.02163]},{"body_a":"push_box","body_b":"link7","contact_count":152.0,"contact_point_centroid":[0.52723,-0.06462,0.05066],"force_p95":11.79282,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.71515,"mean_force":2.96669,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.49605,-0.04812,0.02105]},{"body_a":"world","body_b":"push_box","contact_count":1792.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49986,0.03743,0.21807]},{"body_a":"world","body_b":"push_box","contact_count":2808.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_to_side","phase_type":"descend","tcp_position_centroid":[0.49917,0.06046,0.0785]}],"total_contact_groups":5},"final_pose_error":0.01491,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50096,-0.17339,0.02531],"final_tcp_position":[0.49595,-0.13653,0.02006],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":22.48385,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":448.0,"n_steps_budget":840.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1792.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach_box","tcp_end":[0.50112,0.07653,0.13565],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.1461,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":702.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_to_side","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2808.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact_pose","tcp_end":[0.50009,0.04502,0.0265],"tcp_start":[0.50112,0.07653,0.13565],"tcp_to_object_dist_end":0.06401,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50096,-0.17339,0.02531],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.02342,"object_to_goal_dist_start":0.13127,"object_z_max":0.02638,"peak_contact_force":2.07879,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2485.0,"raw_peak_contact_force":22.48385,"subtask_id":"goal_reach","tcp_end":[0.49595,-0.13653,0.02006],"tcp_start":[0.50009,0.04502,0.0265],"tcp_to_object_dist_end":0.03757,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `589e611c6c27578474525e3fd29be4fb5907d8bbd5d1ca44922bfd811e342c78`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.22162,"average_solve_count":185.0,"average_success_count":185.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_offset_y":0.13334,"approach.approach_speed":0.14366,"approach.approach_tolerance":0.01214,"descend_to_side.descend_offset_y":0.06324,"descend_to_side.descend_speed":0.03611,"descend_to_side.force_threshold":10.03252,"push_to_goal.push_speed":0.03914,"push_to_goal.push_tolerance":0.01006},"optimized_scores":{"best_composite_score":0.10406,"best_fitness_score":0.53406,"best_task_score":0.68796},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":200.0,"contact_point_centroid":[0.53472,0.01794,0.05027],"force_p95":18.36663,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.93883,"mean_force":5.97849,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50334,0.03353,0.02034]},{"body_a":"attachment","body_b":"push_box","contact_count":710.0,"contact_point_centroid":[0.51113,0.00127,0.03762],"force_p95":16.45422,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.69801,"mean_force":4.57746,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.5024,0.01295,0.02025]},{"body_a":"world","body_b":"push_box","contact_count":1779.0,"contact_point_centroid":[0.51032,-0.00924,-4e-05],"force_p95":10.17516,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.07172,"mean_force":2.7643,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50395,0.04141,0.02069]},{"body_a":"world","body_b":"push_box","contact_count":2912.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.50465,0.085,0.21297]},{"body_a":"world","body_b":"push_box","contact_count":3044.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_to_side","phase_type":"descend","tcp_position_centroid":[0.50932,0.14077,0.07366]}],"total_contact_groups":5},"final_pose_error":0.09846,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50546,-0.08838,0.02501],"final_tcp_position":[0.49974,-0.05166,0.02016],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":20.93883,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":728.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2912.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach_box","tcp_end":[0.51102,0.17039,0.12885],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.16082,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":761.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_to_side","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3044.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact_pose","tcp_end":[0.5105,0.11305,0.02507],"tcp_start":[0.51102,0.17039,0.12885],"tcp_to_object_dist_end":0.06554,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50546,-0.08838,0.02501],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.06186,"object_to_goal_dist_start":0.19823,"object_z_max":0.02581,"peak_contact_force":4e-05,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2689.0,"raw_peak_contact_force":20.93883,"subtask_id":"goal_reach","tcp_end":[0.49974,-0.05166,0.02016],"tcp_start":[0.5105,0.11305,0.02507],"tcp_to_object_dist_end":0.03749,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `f2c9c63f0d9eca1b3ff8bf951759f6a3adee73f9f65e1cd3613c5e9d1203ebcc`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.18033,"average_solve_count":183.0,"average_success_count":183.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_offset_y":0.10102,"approach.approach_speed":0.12409,"approach.approach_tolerance":0.00894,"descend_to_side.descend_offset_y":0.07013,"descend_to_side.descend_speed":0.05548,"descend_to_side.force_threshold":16.26094,"push_to_goal.push_speed":0.05032,"push_to_goal.push_tolerance":0.01372},"optimized_scores":{"best_composite_score":0.35238,"best_fitness_score":0.78238,"best_task_score":0.99282},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":732.0,"contact_point_centroid":[0.49104,-0.02086,0.03532],"force_p95":25.60363,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.82942,"mean_force":5.15871,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.48348,-0.00915,0.02166]},{"body_a":"world","body_b":"push_box","contact_count":1583.0,"contact_point_centroid":[0.48699,-0.02116,-5e-05],"force_p95":12.42228,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.80844,"mean_force":2.78763,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.48033,0.03001,0.02247]},{"body_a":"push_box","body_b":"link7","contact_count":93.0,"contact_point_centroid":[0.51642,-0.03875,0.05062],"force_p95":7.49871,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.62513,"mean_force":1.42806,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.48481,-0.0231,0.02162]},{"body_a":"world","body_b":"push_box","contact_count":3460.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.48751,0.07588,0.21209]},{"body_a":"world","body_b":"push_box","contact_count":2400.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_to_side","phase_type":"descend","tcp_position_centroid":[0.4746,0.14002,0.07614]}],"total_contact_groups":5},"final_pose_error":0.03919,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49912,-0.14878,0.02502],"final_tcp_position":[0.49265,-0.11178,0.02042],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":29.82942,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":865.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3460.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach_box","tcp_end":[0.47694,0.15143,0.12801],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.13877,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":600.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_to_side","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2400.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact_pose","tcp_end":[0.47498,0.12915,0.02742],"tcp_start":[0.47694,0.15143,0.12801],"tcp_to_object_dist_end":0.07085,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49912,-0.14878,0.02502],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.0015,"object_to_goal_dist_start":0.2095,"object_z_max":0.02587,"peak_contact_force":0.99265,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2408.0,"raw_peak_contact_force":29.82942,"subtask_id":"goal_reach","tcp_end":[0.49265,-0.11178,0.02042],"tcp_start":[0.47498,0.12915,0.02742],"tcp_to_object_dist_end":0.03785,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```