## Search State

- **Seed**: 6
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | time_limit | 9 | 0.2676 | 0.73 | ❌ rejected |
| 13 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | pose_tolerance | 7 | 0.4795 | 0.56 | ❌ rejected |
| 12 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | pose_tolerance | force_exceeded | pose_tolerance | 10 | -0.1745 | 0.29 | ❌ rejected |
| 11 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | admittance_control | pose_tolerance | contact_detected | pose_tolerance | 8 | 0.0499 | 0.58 | ❌ rejected |
| 10 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | pose_tolerance | 9 | 0.3009 | 0.89 | ✅ accepted |

**Proposal policy**: task_score is 0.73 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.268) — your mutation base

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
  weight: 0.2
- id: side_contact
  anchor: object
  offset:
  - 0.0
  - 0.07
  - 0.0
  weight: 0.2
- id: goal_reach
  weight: 0.6
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
- id: contact_side
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.07
    - 0.0
  parameters:
    contact_offset_y:
      type: scalar
      range:
      - 0.04
      - 0.12
      default: 0.07
      binds_to:
      - path: target.offset.y
        mode: replace
    contact_speed:
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
      - 5.0
      - 15.0
      default: 10.0
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
  subtask_id: side_contact
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
    push_force_guard:
      type: scalar
      range:
      - 25.0
      - 40.0
      default: 35.0
      binds_to:
      - path: guards.force_guard.threshold
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.025
      - 0.08
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    push_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.02
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  guards:
  - id: force_guard
    when: during_phase
    predicate: force_below
    threshold: 35.0
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
- **contact_side** (`contact`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.07, 0.0]
  - parameter_bindings:
    - contact_offset_y: status=consumed; consumers=target.offset.y (replace)
    - contact_speed: status=consumed; consumers=generator.speed (replace)
    - force_threshold: status=consumed; consumers=termination.force_threshold (replace)
  - guards:
    - id=contact_check, when=after_phase, predicate=contact_detected, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.02, -0.01]
- **push_to_goal** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - push_force_guard: status=consumed; consumers=guards.force_guard.threshold (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
    - push_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
  - guards:
    - id=force_guard, when=during_phase, predicate=force_below, on_failure=continue, threshold=35.0

## Design Metrics

- **Composite score**: 0.268
- **task_score** (E): 0.731
- **fitness_score**: 0.636  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.111
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.480

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach | 1.00 | 1.00 | 0.2149 |
| contact_side | 0.33 | 1.00 | 0.1155 |
| push_to_goal | 0.67 | 1.00 | 0.1636 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, 0.126, 0.129) | (0.500, 0.029, 0.025)→(0.500, 0.029, 0.025) | 0.180→0.180 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_side | contact | 0.33 / step_budget | (0.496, 0.126, 0.129)→(0.495, 0.068, 0.030) | (0.500, 0.029, 0.025)→(0.500, 0.029, 0.025) | 0.180→0.180 | 1.00 / 4.333 | 3.753 | 0.245 |
| push_to_goal | push | 0.67 / time_limit | (0.495, 0.068, 0.030)→(0.498, -0.095, 0.023) | (0.500, 0.029, 0.025)→(0.508, -0.130, 0.027) | 0.180→0.049 | 1.00 / 3.333 | 17.010 | 35.278 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.724
- goal_progress: 0.792
- terminal_score: 0.792
- phase_score: 0.758
- phase_breakdown.side_contact_score: 0.516
- phase_breakdown.goal_reach_score: 0.795
- phase_breakdown.approach_box_score: 0.889

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.772
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.930
- **Median Q (composite search score)**: 0.281
- **K-run variance**: 0.0007
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.282


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.03371,"average_solve_count":89.0,"average_success_count":89.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_offset_y":0.10305,"approach.approach_speed":0.16531,"approach.approach_tolerance":0.00547,"contact_side.contact_offset_y":0.03499,"contact_side.contact_speed":0.07014,"contact_side.force_threshold":10.36888,"push_to_goal.push_force_guard":36.23758,"push_to_goal.push_speed":0.12908,"push_to_goal.push_time_limit":9.74658},"optimized_scores":{"best_composite_score":0.29157,"best_fitness_score":0.77157,"best_task_score":0.79184},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":706.0,"contact_point_centroid":[0.50306,-0.06925,0.03378],"force_p95":19.39094,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":33.00633,"mean_force":4.74004,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.49625,-0.05741,0.02004]},{"body_a":"world","body_b":"push_box","contact_count":1131.0,"contact_point_centroid":[0.50033,-0.0989,-6e-05],"force_p95":11.63828,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.33051,"mean_force":3.53296,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.49635,-0.0515,0.02014]},{"body_a":"push_box","body_b":"link7","contact_count":120.0,"contact_point_centroid":[0.52602,-0.06243,0.05033],"force_p95":14.15288,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.35811,"mean_force":3.01682,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.49626,-0.0442,0.02001]},{"body_a":"world","body_b":"push_box","contact_count":2824.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49957,0.0385,0.21532]},{"body_a":"world","body_b":"push_box","contact_count":3328.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_side","phase_type":"contact","tcp_position_centroid":[0.49912,0.04713,0.07201]}],"total_contact_groups":5},"final_pose_error":0.01147,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50077,-0.17731,0.02484],"final_tcp_position":[0.49588,-0.1406,0.01987],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":33.00633,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":706.0,"n_steps_budget":750.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2824.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach_box","tcp_end":[0.50099,0.0793,0.12923],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.14319,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":832.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"contact_side","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3328.0,"raw_peak_contact_force":0.24525,"subtask_id":"side_contact","tcp_end":[0.50009,0.01843,0.02418],"tcp_start":[0.50099,0.0793,0.12923],"tcp_to_object_dist_end":0.03751,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":807.0,"n_steps_budget":840.0,"object_pos_end":[0.50077,-0.17731,0.02484],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.02733,"object_to_goal_dist_start":0.13127,"object_z_max":0.02552,"peak_contact_force":13.39181,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1957.0,"raw_peak_contact_force":33.00633,"subtask_id":"goal_reach","tcp_end":[0.49588,-0.1406,0.01987],"tcp_start":[0.50009,0.01843,0.02418],"tcp_to_object_dist_end":0.03737,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `589e611c6c27578474525e3fd29be4fb5907d8bbd5d1ca44922bfd811e342c78`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.77451,"average_solve_count":102.0,"average_success_count":102.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_offset_y":0.11222,"approach.approach_speed":0.16207,"approach.approach_tolerance":0.01121,"contact_side.contact_offset_y":0.02201,"contact_side.contact_speed":0.05234,"contact_side.force_threshold":8.8338,"push_to_goal.push_force_guard":32.94255,"push_to_goal.push_speed":0.08844,"push_to_goal.push_time_limit":13.07487},"optimized_scores":{"best_composite_score":0.23061,"best_fitness_score":0.37727,"best_task_score":0.47169},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":127.0,"contact_point_centroid":[0.54204,-0.02076,0.05598],"force_p95":26.06836,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.63801,"mean_force":16.25121,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50264,-0.00836,0.0299]},{"body_a":"attachment","body_b":"push_box","contact_count":585.0,"contact_point_centroid":[0.51491,0.01975,0.04876],"force_p95":21.38043,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":31.46747,"mean_force":7.8027,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50403,0.03095,0.03213]},{"body_a":"world","body_b":"push_box","contact_count":1054.0,"contact_point_centroid":[0.52354,-0.01725,-9e-05],"force_p95":20.09349,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":28.38149,"mean_force":6.40135,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50438,0.03503,0.03259]},{"body_a":"world","body_b":"push_box","contact_count":2752.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.50465,0.07493,0.21318]},{"body_a":"world","body_b":"push_box","contact_count":3408.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_side","phase_type":"contact","tcp_position_centroid":[0.50909,0.11462,0.07888]}],"total_contact_groups":5},"final_pose_error":0.13307,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52437,-0.04828,0.03019],"final_tcp_position":[0.5033,-0.01707,0.03028],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":37.63801,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":688.0,"n_steps_budget":930.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2752.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach_box","tcp_end":[0.51098,0.15043,0.12902],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.14628,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":852.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.02499,"peak_contact_force":10.76707,"phase_name":"contact_side","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3408.0,"raw_peak_contact_force":0.24525,"subtask_id":"side_contact","tcp_end":[0.51003,0.08465,0.03998],"tcp_start":[0.51098,0.15043,0.12902],"tcp_to_object_dist_end":0.04022,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":729.0,"n_steps_budget":1000.0,"object_pos_end":[0.52437,-0.04828,0.03019],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.10473,"object_to_goal_dist_start":0.19823,"object_z_max":0.03017,"peak_contact_force":37.63801,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1766.0,"raw_peak_contact_force":37.63801,"subtask_id":"goal_reach","tcp_end":[0.5033,-0.01707,0.03028],"tcp_start":[0.51003,0.08465,0.03998],"tcp_to_object_dist_end":0.03765,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `f2c9c63f0d9eca1b3ff8bf951759f6a3adee73f9f65e1cd3613c5e9d1203ebcc`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.95413,"average_solve_count":109.0,"average_success_count":109.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_offset_y":0.10037,"approach.approach_speed":0.16114,"approach.approach_tolerance":0.01143,"contact_side.contact_offset_y":0.0401,"contact_side.contact_speed":0.05655,"contact_side.force_threshold":8.85111,"push_to_goal.push_force_guard":35.35063,"push_to_goal.push_speed":0.14637,"push_to_goal.push_time_limit":11.57404},"optimized_scores":{"best_composite_score":0.28055,"best_fitness_score":0.76055,"best_task_score":0.93002},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":813.0,"contact_point_centroid":[0.48948,-0.02553,0.03381],"force_p95":22.95533,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":35.18992,"mean_force":4.88172,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.48258,-0.0138,0.02136]},{"body_a":"world","body_b":"push_box","contact_count":1511.0,"contact_point_centroid":[0.48797,-0.04601,-6e-05],"force_p95":11.25265,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":26.59777,"mean_force":3.07408,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.48164,-0.00176,0.02175]},{"body_a":"push_box","body_b":"link7","contact_count":120.0,"contact_point_centroid":[0.51194,-0.00708,0.05044],"force_p95":11.31158,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.92303,"mean_force":1.91354,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.48027,0.00912,0.02154]},{"body_a":"world","body_b":"push_box","contact_count":2636.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.4879,0.07396,0.214]},{"body_a":"world","body_b":"push_box","contact_count":2812.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_side","phase_type":"contact","tcp_position_centroid":[0.47476,0.12434,0.07615]}],"total_contact_groups":5},"final_pose_error":0.02371,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49847,-0.16458,0.02507],"final_tcp_position":[0.49394,-0.1276,0.02015],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":35.18992,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":659.0,"n_steps_budget":930.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2636.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach_box","tcp_end":[0.47733,0.14887,0.13021],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.13873,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":703.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"contact_side","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2812.0,"raw_peak_contact_force":0.24525,"subtask_id":"side_contact","tcp_end":[0.47499,0.10068,0.02653],"tcp_start":[0.47733,0.14887,0.13021],"tcp_to_object_dist_end":0.04245,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49847,-0.16458,0.02507],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.01466,"object_to_goal_dist_start":0.2095,"object_z_max":0.02568,"peak_contact_force":0.0,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2444.0,"raw_peak_contact_force":35.18992,"subtask_id":"goal_reach","tcp_end":[0.49394,-0.1276,0.02015],"tcp_start":[0.47499,0.10068,0.02653],"tcp_to_object_dist_end":0.03758,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```