## Search State

- **Seed**: 6
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | pose_tolerance | 8 | 0.1124 | 0.64 | ❌ rejected |
| 8 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | admittance_control | pose_tolerance | force_exceeded | pose_tolerance | 8 | 0.2751 | 0.83 | ✅ accepted |
| 7 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | admittance_control | pose_tolerance | pose_tolerance | pose_tolerance | 10 | -0.2136 | 0.09 | ❌ rejected |
| 6 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | force_exceeded | 8 | 0.0512 | 0.24 | ❌ rejected |
| 5 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | admittance_control | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.0582 | 0.26 | ❌ rejected |

**Proposal policy**: task_score is 0.64 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.112) — your mutation base

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

- **Composite score**: 0.112
- **task_score** (E): 0.636
- **fitness_score**: 0.542  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.430

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach | 1.00 | 1.00 | 0.2150 |
| contact_side | 0.00 | 1.00 | 0.0931 |
| push_to_goal | 0.00 | 1.00 | 0.1523 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.497, 0.132, 0.133) | (0.500, 0.029, 0.025)→(0.500, 0.029, 0.025) | 0.180→0.180 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_side | contact | 0.00 / step_budget | (0.497, 0.132, 0.133)→(0.495, 0.092, 0.050) | (0.500, 0.029, 0.025)→(0.500, 0.029, 0.025) | 0.180→0.180 | 1.00 / 4.000 | 0.245 | 0.245 |
| push_to_goal | push | 0.00 / step_budget | (0.495, 0.092, 0.050)→(0.495, -0.059, 0.030) | (0.500, 0.029, 0.025)→(0.520, -0.089, 0.028) | 0.180→0.067 | 1.00 / 2.333 | 10.150 | 28.907 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.828
- lateral_force_integral: None
- approach_alignment: 0.663
- goal_progress: 0.704
- terminal_score: 0.704
- phase_score: 0.519
- phase_breakdown.goal_reach_score: 0.329
- phase_breakdown.approach_box_score: 0.796
- phase_breakdown.contact_pose_score: 0.578

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.593
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.704
- **Median Q (composite search score)**: 0.150
- **K-run variance**: 0.0039
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.317


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.1988,"average_solve_count":166.0,"average_success_count":166.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_offset_y":0.11467,"approach.approach_speed":0.14958,"approach.approach_tolerance":0.01228,"contact_side.contact_offset_y":0.08583,"contact_side.contact_speed":0.04134,"contact_side.force_threshold":13.9191,"push_to_goal.push_speed":0.03115,"push_to_goal.push_tolerance":0.00997},"optimized_scores":{"best_composite_score":0.16264,"best_fitness_score":0.59264,"best_task_score":0.70352},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":547.0,"contact_point_centroid":[0.50676,-0.05059,0.04945],"force_p95":21.43942,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":27.19512,"mean_force":9.84418,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.49626,-0.03914,0.034]},{"body_a":"world","body_b":"push_box","contact_count":2262.0,"contact_point_centroid":[0.51266,-0.05733,-4e-05],"force_p95":12.23487,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.14525,"mean_force":2.71771,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.49653,-0.00251,0.03886]},{"body_a":"world","body_b":"push_box","contact_count":2048.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49978,0.04309,0.21684]},{"body_a":"world","body_b":"push_box","contact_count":1996.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_side","phase_type":"contact","tcp_position_centroid":[0.49929,0.078,0.09112]}],"total_contact_groups":4},"final_pose_error":0.05563,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52946,-0.12457,0.02519],"final_tcp_position":[0.49626,-0.09453,0.02702],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":27.19512,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":512.0,"n_steps_budget":840.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2048.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach_box","tcp_end":[0.50108,0.08796,0.13347],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.15225,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":499.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"contact_side","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1996.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact_pose","tcp_end":[0.50024,0.06822,0.05204],"tcp_start":[0.50108,0.08796,0.13347],"tcp_to_object_dist_end":0.09123,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52946,-0.12457,0.02519],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.03892,"object_to_goal_dist_start":0.13127,"object_z_max":0.02701,"peak_contact_force":0.36596,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2809.0,"raw_peak_contact_force":27.19512,"subtask_id":"goal_reach","tcp_end":[0.49626,-0.09453,0.02702],"tcp_start":[0.50024,0.06822,0.05204],"tcp_to_object_dist_end":0.04482,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `589e611c6c27578474525e3fd29be4fb5907d8bbd5d1ca44922bfd811e342c78`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.34868,"average_solve_count":152.0,"average_success_count":152.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_offset_y":0.11519,"approach.approach_speed":0.16376,"approach.approach_tolerance":0.01591,"contact_side.contact_offset_y":0.03671,"contact_side.contact_speed":0.03023,"contact_side.force_threshold":14.12101,"push_to_goal.push_speed":0.05054,"push_to_goal.push_tolerance":0.00805},"optimized_scores":{"best_composite_score":0.02455,"best_fitness_score":0.45455,"best_task_score":0.50694},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":811.0,"contact_point_centroid":[0.5139,0.01111,0.04768],"force_p95":19.16571,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":30.08468,"mean_force":7.02021,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50404,0.02192,0.0362]},{"body_a":"push_box","body_b":"link7","contact_count":125.0,"contact_point_centroid":[0.54121,-0.02977,0.0587],"force_p95":24.35111,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":25.72957,"mean_force":15.75327,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50229,-0.02242,0.03239]},{"body_a":"world","body_b":"push_box","contact_count":1436.0,"contact_point_centroid":[0.52616,-0.0237,-6e-05],"force_p95":15.66465,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.98517,"mean_force":5.43494,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50442,0.02642,0.03681]},{"body_a":"world","body_b":"push_box","contact_count":2084.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.5047,0.07419,0.21564]},{"body_a":"world","body_b":"push_box","contact_count":3768.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_side","phase_type":"contact","tcp_position_centroid":[0.50954,0.11255,0.08147]}],"total_contact_groups":5},"final_pose_error":0.12212,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52733,-0.05635,0.03109],"final_tcp_position":[0.50264,-0.02814,0.03243],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":30.08468,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":521.0,"n_steps_budget":930.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2084.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach_box","tcp_end":[0.51091,0.14988,0.13273],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.14857,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":942.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"contact_side","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3768.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact_pose","tcp_end":[0.51075,0.08509,0.04656],"tcp_start":[0.51091,0.14988,0.13273],"tcp_to_object_dist_end":0.0434,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":970.0,"n_steps_budget":1000.0,"object_pos_end":[0.52733,-0.05635,0.03109],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.09774,"object_to_goal_dist_start":0.19823,"object_z_max":0.03109,"peak_contact_force":30.08468,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2372.0,"raw_peak_contact_force":30.08468,"subtask_id":"goal_reach","tcp_end":[0.50264,-0.02814,0.03243],"tcp_start":[0.51075,0.08509,0.04656],"tcp_to_object_dist_end":0.03751,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `f2c9c63f0d9eca1b3ff8bf951759f6a3adee73f9f65e1cd3613c5e9d1203ebcc`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.2795,"average_solve_count":161.0,"average_success_count":161.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_offset_y":0.11145,"approach.approach_speed":0.14846,"approach.approach_tolerance":0.01576,"contact_side.contact_offset_y":0.06237,"contact_side.contact_speed":0.04204,"contact_side.force_threshold":19.18993,"push_to_goal.push_speed":0.03344,"push_to_goal.push_tolerance":0.01044},"optimized_scores":{"best_composite_score":0.15012,"best_fitness_score":0.58012,"best_task_score":0.69772},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":650.0,"contact_point_centroid":[0.48881,0.00678,0.04817],"force_p95":22.63131,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.44245,"mean_force":8.84957,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.48096,0.01836,0.03734]},{"body_a":"world","body_b":"push_box","contact_count":1709.0,"contact_point_centroid":[0.48901,-0.00019,-6e-05],"force_p95":11.88994,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.76422,"mean_force":3.77746,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.47822,0.05227,0.04113]},{"body_a":"world","body_b":"push_box","contact_count":2188.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.48828,0.07744,0.21582]},{"body_a":"world","body_b":"push_box","contact_count":2072.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_side","phase_type":"contact","tcp_position_centroid":[0.47519,0.13975,0.09115]}],"total_contact_groups":4},"final_pose_error":0.09786,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.5035,-0.08684,0.02811],"final_tcp_position":[0.48732,-0.05309,0.02998],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":29.44245,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":547.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2188.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach_box","tcp_end":[0.47783,0.15673,0.13285],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.14591,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":518.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"contact_side","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2072.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact_pose","tcp_end":[0.47523,0.12287,0.05213],"tcp_start":[0.47783,0.15673,0.13285],"tcp_to_object_dist_end":0.07,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5035,-0.08684,0.02811],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.06333,"object_to_goal_dist_start":0.2095,"object_z_max":0.02823,"peak_contact_force":0.0,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2359.0,"raw_peak_contact_force":29.44245,"subtask_id":"goal_reach","tcp_end":[0.48732,-0.05309,0.02998],"tcp_start":[0.47523,0.12287,0.05213],"tcp_to_object_dist_end":0.03748,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```