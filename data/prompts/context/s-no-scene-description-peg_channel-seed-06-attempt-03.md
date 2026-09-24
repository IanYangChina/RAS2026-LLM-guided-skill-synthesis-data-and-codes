## Search State

- **Seed**: 6
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | -0.0108 | 0.00 | ✅ accepted |
| 2 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | -0.0107 | 0.00 | ✅ accepted |
| 1 | align → lift → push → approach → approach → descend → grasp | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | force_threshold_switch | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | -0.0828 | 0.00 | ❌ rejected |
| 0 | align → lift → push → approach → approach → descend → grasp | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | force_threshold_switch | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | -0.0805 | 0.00 | ✅ accepted |

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

- Task name: peg_channel
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.5
- Force limit: 40.0 N
- Peg body: `peg`
- Primary evaluation target: **insertion depth × lateral alignment (axial progress penalised by wall deviation)**

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

## Current Skill (Q=-0.011) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: pre_push
  anchor: object
  offset:
  - 0.0
  - -0.02
  - 0.04
  weight: 0.3
- id: push_goal
  target_entity: object
  weight: 0.7
phases:
- id: approach_peg
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - -0.02
    - 0.04
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    lateral_offset_x:
      type: scalar
      range:
      - -0.01
      - 0.01
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: add
  guards:
  - id: check_approach
    when: after_phase
    predicate: pose_within_tolerance
    threshold: 0.01
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.005
    - 0.0
    - 0.0
  subtask_id: pre_push
- id: contact_peg
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.0
    - 0.04
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 5.0
      - 30.0
      default: 15.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    contact_speed:
      type: scalar
      range:
      - 0.005
      - 0.03
      default: 0.01
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: ensure_contact
    when: during_phase
    predicate: contact_detected
    threshold: 0.5
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.005
    - 0.0
- id: push_channel
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.04
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.06
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: force_limit
    when: during_phase
    predicate: force_below
    threshold: 40.0
    on_failure: abort
  subtask_id: push_goal
- id: retract
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    retract_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_peg** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, -0.02, 0.04], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - lateral_offset_x: status=consumed; consumers=target.offset.x (add)
  - guards:
    - id=check_approach, when=after_phase, predicate=pose_within_tolerance, on_failure=retry, threshold=0.01
  - retries: max_attempts=2, strategy=offset_target, offset=[0.005, 0.0, 0.0]
- **contact_peg** (`contact`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.0, 0.04], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - contact_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=ensure_contact, when=during_phase, predicate=contact_detected, on_failure=retry, threshold=0.5
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.005, 0.0]
- **push_channel** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.04], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_limit, when=during_phase, predicate=force_below, on_failure=abort, threshold=40.0
- **retract** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: -0.011
- **task_score** (E): 0.000
- **fitness_score**: 0.349  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 0.33 | 1.00 | 0.0737 |
| contact_peg | 0.00 | 1.00 | 0.0162 |
| push_channel | 1.00 | 1.00 | 0.1578 |
| retract | 1.00 | 1.00 | 0.0906 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 0.33 / step_budget | (0.494, 0.115, 0.139)→(0.499, 0.081, 0.074) | (0.500, 0.099, 0.040)→(0.501, 0.099, 0.034) | 0.180→0.180 | 1.00 / 1.000 | 0.554 | 2.127 |
| contact_peg | contact | 0.00 / step_budget | (0.499, 0.081, 0.074)→(0.497, 0.096, 0.069) | (0.501, 0.099, 0.034)→(0.501, 0.100, 0.034) | 0.180→0.180 | 1.00 / 1.000 | 0.563 | 0.619 |
| push_channel | push | 1.00 / step_budget | (0.497, 0.096, 0.069)→(0.496, -0.062, 0.074) | (0.501, 0.100, 0.034)→(0.507, 0.113, 0.027) | 0.180→0.194 | 1.00 / 1.000 | 0.565 | 1.371 |
| retract | retract | 1.00 / step_budget | (0.496, -0.062, 0.074)→(0.493, -0.062, 0.165) | (0.507, 0.113, 0.027)→(0.525, 0.114, 0.027) | 0.194→0.197 | 1.00 / 1.000 | 0.621 | 0.641 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.000
- alignment_error: None
- force_efficiency: 0.959
- terminal_score: 0.000
- phase_score: 0.604
- phase_breakdown.pre_push_score: 0.871
- phase_breakdown.push_goal_score: 0.489

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.362
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.001
- **Median Q (composite search score)**: -0.005
- **K-run variance**: 0.0002
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.313


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `080f370e6b427cbdf66706e7036a0e474f3967ccfc94f129756881a980a10a27`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `1f3f20d8b9dd2cb87de5d9f0723b4addbc88cdcf096cd2177633d23c0fa32881`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.94118,"average_solve_count":255.0,"average_success_count":255.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.0236,"approach_peg.lateral_offset_x":-0.00075,"contact_peg.contact_force_threshold":18.72129,"contact_peg.contact_speed":0.01587,"push_channel.push_speed":0.0313,"retract.retract_speed":0.0555},"optimized_scores":{"best_composite_score":0.00229,"best_fitness_score":0.36229,"best_task_score":0.00019},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":1586.0,"contact_point_centroid":[0.50305,0.06747,0.00937],"force_p95":0.55081,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.55207,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49874,0.12216,0.18241]},{"body_a":"peg","body_b":"channel_base_body","contact_count":476.0,"contact_point_centroid":[0.50302,0.06743,0.00938],"force_p95":0.55055,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5506,"mean_force":0.54665,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49977,0.05868,0.06948]},{"body_a":"peg","body_b":"channel_base_body","contact_count":860.0,"contact_point_centroid":[0.50309,0.06741,0.00938],"force_p95":0.55055,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55057,"mean_force":0.54664,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49625,-0.00551,0.07003]},{"body_a":"peg","body_b":"channel_base_body","contact_count":881.0,"contact_point_centroid":[0.50306,0.06747,0.00938],"force_p95":0.55055,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55055,"mean_force":0.54665,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.49323,-0.07204,0.11979]}],"total_contact_groups":4},"final_pose_error":0.00998,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50301,0.06743,0.0338],"final_tcp_position":[0.49337,-0.07202,0.16524],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":2.06903,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1602.0,"n_steps_budget":1000.0,"object_pos_end":[0.50308,0.06743,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54355,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1586.0,"raw_peak_contact_force":2.06903,"subtask_id":"pre_push","tcp_end":[0.50312,0.05011,0.07363],"tcp_start":[0.49835,0.10374,0.15753],"tcp_to_object_dist_end":0.04343,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":476.0,"n_steps_budget":690.0,"object_pos_end":[0.50308,0.06748,0.0338],"object_pos_start":[0.50309,0.06745,0.0338],"object_to_goal_dist_end":0.14765,"object_to_goal_dist_start":0.14762,"object_z_max":0.0338,"peak_contact_force":0.54735,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":476.0,"raw_peak_contact_force":0.5506,"tcp_end":[0.49938,0.06525,0.06906],"tcp_start":[0.50312,0.05011,0.07363],"tcp_to_object_dist_end":0.03553,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":860.0,"n_steps_budget":1000.0,"object_pos_end":[0.503,0.06745,0.0338],"object_pos_start":[0.50308,0.06748,0.0338],"object_to_goal_dist_end":0.14761,"object_to_goal_dist_start":0.14765,"object_z_max":0.0338,"peak_contact_force":0.54672,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":860.0,"raw_peak_contact_force":0.55057,"subtask_id":"push_goal","tcp_end":[0.49635,-0.07241,0.07476],"tcp_start":[0.49938,0.06525,0.06906],"tcp_to_object_dist_end":0.14589,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":881.0,"n_steps_budget":1000.0,"object_pos_end":[0.50301,0.06743,0.0338],"object_pos_start":[0.503,0.06745,0.0338],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14761,"object_z_max":0.0338,"peak_contact_force":0.54736,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":881.0,"raw_peak_contact_force":0.55055,"tcp_end":[0.49337,-0.07202,0.16524],"tcp_start":[0.49635,-0.07241,0.07476],"tcp_to_object_dist_end":0.19188,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `625c03a21403c0f6267b643060335ee3d751a26340ace08db5429afcee4c5ccf`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.78491,"average_solve_count":265.0,"average_success_count":265.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.04475,"approach_peg.lateral_offset_x":0.00384,"contact_peg.contact_force_threshold":15.9763,"contact_peg.contact_speed":0.00511,"push_channel.push_speed":0.04826,"retract.retract_speed":0.0708},"optimized_scores":{"best_composite_score":-0.00517,"best_fitness_score":0.35483,"best_task_score":0.00092},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":1363.0,"contact_point_centroid":[0.50363,0.11167,0.00939],"force_p95":0.61076,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.54994,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50355,0.14487,0.18376]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50369,0.11166,0.0094],"force_p95":0.60021,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.66599,"mean_force":0.54461,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50272,0.1012,0.06985]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50373,0.11162,0.0094],"force_p95":0.59807,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63936,"mean_force":0.54449,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.4973,0.01899,0.06986]},{"body_a":"peg","body_b":"channel_base_body","contact_count":787.0,"contact_point_centroid":[0.50362,0.11155,0.0094],"force_p95":0.59475,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63069,"mean_force":0.54427,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.49338,-0.0622,0.11943]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49967,0.19937,0.29936]}],"total_contact_groups":5},"final_pose_error":0.00999,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50375,0.11162,0.03382],"final_tcp_position":[0.49351,-0.06218,0.16481],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":2.06328,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1385.0,"n_steps_budget":1000.0,"object_pos_end":[0.50371,0.11172,0.0338],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19186,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.54559,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1379.0,"raw_peak_contact_force":2.06328,"subtask_id":"pre_push","tcp_end":[0.50831,0.09395,0.07506],"tcp_start":[0.50666,0.12189,0.13801],"tcp_to_object_dist_end":0.04516,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50373,0.11168,0.03379],"object_pos_start":[0.50373,0.11174,0.03381],"object_to_goal_dist_end":0.19182,"object_to_goal_dist_start":0.19187,"object_z_max":0.03396,"peak_contact_force":0.54491,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.66599,"tcp_end":[0.50143,0.10551,0.06932],"tcp_start":[0.50831,0.09395,0.07506],"tcp_to_object_dist_end":0.03614,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50369,0.11168,0.03379],"object_pos_start":[0.50373,0.11168,0.03379],"object_to_goal_dist_end":0.19181,"object_to_goal_dist_start":0.19182,"object_z_max":0.034,"peak_contact_force":0.51626,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.63936,"subtask_id":"push_goal","tcp_end":[0.49651,-0.06251,0.07433],"tcp_start":[0.50143,0.10551,0.06932],"tcp_to_object_dist_end":0.17899,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":787.0,"n_steps_budget":900.0,"object_pos_end":[0.50375,0.11162,0.03382],"object_pos_start":[0.50369,0.11168,0.03379],"object_to_goal_dist_end":0.19176,"object_to_goal_dist_start":0.19181,"object_z_max":0.03392,"peak_contact_force":0.5763,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":787.0,"raw_peak_contact_force":0.63069,"tcp_end":[0.49351,-0.06218,0.16481],"tcp_start":[0.49651,-0.06251,0.07433],"tcp_to_object_dist_end":0.21787,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `abe38b4b57ac37a91047e57d04e408cb1fd05583a47670bcb186dc9505a3f021`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.85217,"average_solve_count":230.0,"average_success_count":230.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.05936,"approach_peg.lateral_offset_x":-0.00969,"contact_peg.contact_force_threshold":10.96955,"contact_peg.contact_speed":0.01858,"push_channel.push_speed":0.04848,"retract.retract_speed":0.04991},"optimized_scores":{"best_composite_score":-0.0295,"best_fitness_score":0.3305,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"world","contact_count":883.0,"contact_point_centroid":[0.50148,0.15925,-0.00189],"force_p95":0.74028,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.92426,"mean_force":0.61205,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49206,0.02014,0.06993]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1376.0,"contact_point_centroid":[0.49617,0.11909,0.00944],"force_p95":0.60141,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.54616,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.48601,0.1441,0.17455]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49944,0.19914,0.29858]},{"body_a":"peg","body_b":"world","contact_count":873.0,"contact_point_centroid":[0.53817,0.1612,-0.00197],"force_p95":0.74033,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.74049,"mean_force":0.60602,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.49203,-0.05068,0.11893]},{"body_a":"peg","body_b":"channel_base_body","contact_count":546.0,"contact_point_centroid":[0.49603,0.11918,0.00943],"force_p95":0.61441,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63898,"mean_force":0.54198,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.48797,0.10885,0.06971]},{"body_a":"peg","body_b":"channel_base_body","contact_count":113.0,"contact_point_centroid":[0.49521,0.1199,0.00948],"force_p95":0.57555,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.58645,"mean_force":0.49239,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48973,0.10597,0.06696]}],"total_contact_groups":6},"final_pose_error":0.00992,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.56707,0.162,0.01411],"final_tcp_position":[0.49216,-0.05066,0.16433],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":2.92426,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1401.0,"n_steps_budget":1000.0,"object_pos_end":[0.49605,0.11898,0.03397],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19911,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.57214,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1400.0,"raw_peak_contact_force":2.24822,"subtask_id":"pre_push","tcp_end":[0.48654,0.10022,0.07399],"tcp_start":[0.47826,0.11957,0.12217],"tcp_to_object_dist_end":0.04521,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":546.0,"n_steps_budget":720.0,"object_pos_end":[0.49603,0.12018,0.03389],"object_pos_start":[0.49601,0.11902,0.03388],"object_to_goal_dist_end":0.20031,"object_to_goal_dist_start":0.19915,"object_z_max":0.03401,"peak_contact_force":0.59618,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":546.0,"raw_peak_contact_force":0.63898,"tcp_end":[0.49147,0.11639,0.06917],"tcp_start":[0.48654,0.10022,0.07399],"tcp_to_object_dist_end":0.03577,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51432,0.16062,0.01412],"object_pos_start":[0.49603,0.12018,0.03389],"object_to_goal_dist_end":0.24243,"object_to_goal_dist_start":0.20031,"object_z_max":0.03391,"peak_contact_force":0.63091,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":996.0,"raw_peak_contact_force":2.92426,"subtask_id":"push_goal","tcp_end":[0.49514,-0.05093,0.07379],"tcp_start":[0.49147,0.11639,0.06917],"tcp_to_object_dist_end":0.22064,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":873.0,"n_steps_budget":1000.0,"object_pos_end":[0.56707,0.162,0.01411],"object_pos_start":[0.51432,0.16062,0.01412],"object_to_goal_dist_end":0.25245,"object_to_goal_dist_start":0.24243,"object_z_max":0.01412,"peak_contact_force":0.74033,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":873.0,"raw_peak_contact_force":0.74049,"tcp_end":[0.49216,-0.05066,0.16433],"tcp_start":[0.49514,-0.05093,0.07379],"tcp_to_object_dist_end":0.27093,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```